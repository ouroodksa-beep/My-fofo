import os
import sys
import time
import json
import re
import hashlib
import threading
import logging
from datetime import datetime
from urllib.parse import urljoin, quote

import requests
import pandas as pd
from flask import Flask, jsonify
from bs4 import BeautifulSoup

# ============================================================
# SETTINGS & CONFIGURATION
# ============================================================
BOT_TOKEN = "8769441239:AAFUuBQcJ6xj-9q-xhYFGEW6yNWT2xWzvAA"
CHAT_ID = "432826122"

# 🔑 ScraperAPI Key
SCRAPER_API_KEY = "f56b509d66fa5a0f2b234473858004b7"

# 🎟️ البرومو كود
PROMO_CODE = "SAVE10"

# إعدادات الفحص
MAX_PRODUCTS = 300
REQUEST_DELAY = 2.0
SCAN_INTERVAL_MINUTES = 60
PRICE_FILE = "amazon_sa_prices.csv"
ALERT_FILE = "amazon_sa_alerts.csv"
SELF_PING_INTERVAL = 600

# ============================================================
# AMAZON SA BESTSELLERS URLS
# ============================================================
DISCOVERY_URLS = [
    "https://www.amazon.sa/gp/bestsellers/electronics",
    "https://www.amazon.sa/gp/bestsellers/mobile-phones",
    "https://www.amazon.sa/gp/bestsellers/computers",
    "https://www.amazon.sa/gp/bestsellers/kitchen",
    "https://www.amazon.sa/gp/bestsellers/beauty",
    "https://www.amazon.sa/gp/bestsellers/supermarket"
]

# ============================================================
# LOGGING & APP SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("amazon_sa_bot")

app = Flask(__name__)
session = requests.Session()

# ============================================================
# TELEGRAM HELPER
# ============================================================
def telegram_send(message):
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("BOT_TOKEN or CHAT_ID not set!")
        return False
    try:
        r = session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": False},
            timeout=20
        )
        return r.status_code == 200 and r.json().get("ok")
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

# ============================================================
# CLEAN URL BUILDER & PRICE PARSER
# ============================================================
def get_clean_url(url):
    asin_match = re.search(r"/(dp|gp/product)/([A-Z0-9]{10})", url)
    if asin_match:
        asin = asin_match.group(2)
        return f"https://www.amazon.sa/dp/{asin}"
    return url.split("?")[0]

def parse_price(value):
    if value is None:
        return None
    value = str(value)
    value = re.sub(r"(SAR|ر\.س|ريال|AED|USD|\$|€|£)", "", value, flags=re.I)
    value = re.sub(r"[^\d,\.]", "", value)
    if not value:
        return None
    try:
        if "," in value and "." in value:
            if value.rfind(",") > value.rfind("."):
                value = value.replace(".", "").replace(",", ".")
            else:
                value = value.replace(",", "")
        elif "," in value:
            parts = value.split(",")
            if len(parts[-1]) == 2:
                value = value.replace(",", ".")
            else:
                value = value.replace(",", "")
        return float(value)
    except Exception:
        return None

# ============================================================
# DATABASE MANAGEMENT
# ============================================================
PRICE_COLUMNS = ["product_id", "product", "url", "new_price", "timestamp"]

def load_database():
    global prices, sent_alerts
    if os.path.exists(PRICE_FILE):
        try:
            prices = pd.read_csv(PRICE_FILE)
            if not prices.empty:
                prices["timestamp"] = pd.to_datetime(prices["timestamp"], errors="coerce")
        except Exception:
            prices = pd.DataFrame(columns=PRICE_COLUMNS)
    else:
        prices = pd.DataFrame(columns=PRICE_COLUMNS)

    if os.path.exists(ALERT_FILE):
        try:
            alert_df = pd.read_csv(ALERT_FILE)
            sent_alerts = set(alert_df["alert_id"].astype(str).tolist())
        except Exception:
            sent_alerts = set()
    else:
        sent_alerts = set()

def save_database():
    try:
        prices.to_csv(PRICE_FILE, index=False)
        pd.DataFrame({"alert_id": list(sent_alerts)}).to_csv(ALERT_FILE, index=False)
    except Exception as e:
        logger.error(f"Save error: {e}")

load_database()

# ============================================================
# SCRAPERAPI FETCH & REAL PRICE CALCULATION
# ============================================================
def fetch_page_content(url):
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': url,
        'country_code': 'sa'
    }
    try:
        resp = session.get('http://api.scraperapi.com', params=payload, timeout=60)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        logger.error(f"Fetch error: {e}")
    return None

def calculate_real_promo_price(asin, base_price):
    """
    يحسب السعر الجديد الحقيقي بطلب السلة وتطبيق الكود
    """
    cart_url = f"https://www.amazon.sa/gp/item-dispatch/ref=dp_start-bgr?asin.1={asin}&action=addToCart&promoCode={PROMO_CODE}"
    
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': cart_url,
        'country_code': 'sa'
    }
    
    try:
        resp = session.get('http://api.scraperapi.com', params=payload, timeout=60)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            
            price_selectors = [
                "span#sc-subtotal-amount-buybox span",
                "span#sc-subtotal-amount-activecart span",
                "span.sc-price",
                "span.a-color-price"
            ]
            
            for selector in price_selectors:
                tag = soup.select_one(selector)
                if tag:
                    calc_price = parse_price(tag.get_text(strip=True))
                    if calc_price and calc_price > 0:
                        return calc_price
    except Exception as e:
        logger.warning(f"Failed to calculate promo price for {asin}: {e}")
    
    return base_price

def extract_bestsellers_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    products = []

    cards = soup.select(
        "div[id^='post-'], "
        "div[class*='zg-grid-general-faceout'], "
        "div[class*='p13n-sc-unselected-item'], "
        "div.zg-carousel-general-faceout, "
        "div[data-component-type='s-search-result']"
    )

    for card in cards:
        try:
            name = None
            for selector in ["span.zg-text-js-truncate", "a.a-link-normal span", "h2 span", ".a-size-base-plus"]:
                tag = card.select_one(selector)
                if tag and len(tag.get_text(strip=True)) > 3:
                    name = tag.get_text(strip=True)
                    break

            page_price = None
            for selector in ["span.a-price span.a-offscreen", "span.p13n-sc-price", "span.a-color-price"]:
                tag = card.select_one(selector)
                if tag:
                    page_price = parse_price(tag.get_text(strip=True))
                    if page_price and page_price > 0:
                        break

            link_tag = card.select_one("a.a-link-normal[href*='/dp/']")
            if link_tag and link_tag.get("href"):
                raw_url = "https://www.amazon.sa" + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
                clean_url = get_clean_url(raw_url)
                
                asin_match = re.search(r"/(dp|gp/product)/([A-Z0-9]{10})", raw_url)
                if asin_match and name and page_price:
                    asin = asin_match.group(2)
                    products.append({
                        "product_id": asin,
                        "product": str(name).strip()[:180],
                        "url": clean_url,
                        "page_price": page_price
                    })
        except Exception:
            continue

    return list({p["product_id"]: p for p in products}.values())

# ============================================================
# PROCESSING & NOTIFICATIONS
# ============================================================
def run_scan():
    global prices
    logger.info("STARTING SCAN WITH REAL PROMO PRICE CALCULATION...")

    all_discovered = []
    for url in DISCOVERY_URLS:
        html = fetch_page_content(url)
        if html:
            items = extract_bestsellers_from_html(html)
            all_discovered.extend(items)
        time.sleep(REQUEST_DELAY)

    unique_products = list({p["product_id"]: p for p in all_discovered}.values())
    logger.info(f"Discovered {len(unique_products)} unique products.")

    new_alerts_count = 0
    for item in unique_products:
        asin = item["product_id"]

        # 🧮 حساب السعر الجديد الحقيقي المخصوم
        real_new_price = calculate_real_promo_price(asin, item["page_price"])

        # حفظ البيانات
        new_row = pd.DataFrame([{
            "product_id": asin,
            "product": item["product"],
            "url": item["url"],
            "new_price": real_new_price,
            "timestamp": datetime.now()
        }])
        prices = pd.concat([prices, new_row], ignore_index=True)

        alert_id = f"{asin}_{real_new_price}"
        if alert_id not in sent_alerts:
            # ✉️ التنسيق الجديد: السعر الجديد الحقيقي فقط مع الكود تحته
            msg = (
                f"🛍 <b>المنتج:</b> {item['product']}\n"
                f"💵 <b>السعر الجديد:</b> <code>{real_new_price}</code> ر.س\n\n"
                f"📌 <b>كود الخصم:</b> <code>{PROMO_CODE}</code>\n"
                f"🔗 <b>الرابط:</b>\n{item['url']}"
            )
            if telegram_send(msg):
                sent_alerts.add(alert_id)
                new_alerts_count += 1
                time.sleep(1)

    save_database()
    logger.info(f"Scan complete. New alerts sent: {new_alerts_count}")
    return new_alerts_count

# ============================================================
# SCHEDULER & FLASK
# ============================================================
def background_scanner():
    while True:
        try:
            run_scan()
        except Exception as e:
            logger.error(f"Background scanner error: {e}")
        time.sleep(SCAN_INTERVAL_MINUTES * 60)

def self_ping():
    while True:
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
            session.get(url.rstrip("/") + "/ping", timeout=10)
        except Exception:
            pass
        time.sleep(SELF_PING_INTERVAL)

@app.route("/")
def home():
    return jsonify({"status": "online", "mode": "Real Promo Price Extraction Only"})

@app.route("/ping")
def ping():
    return jsonify({"status": "alive"})

@app.route("/scan")
def manual_scan():
    deals_count = run_scan()
    return jsonify({"status": "success", "deals_sent": deals_count})

if __name__ == "__main__":
    threading.Thread(target=background_scanner, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
