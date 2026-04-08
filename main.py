import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
import time
import subprocess

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# ===== قاموس ترجمة بسيط =====
TRANSLATIONS = {
    "cabinet": "خزانة", "shelf": "رف", "organizer": "منظم", "metal": "معدني",
    "kitchen": "مطبخ", "white": "أبيض", "black": "أسود", "chair": "كرسي", "table": "طاولة",
    "set": "طقم", "bag": "شنطة", "shoes": "حذاء", "dress": "فستان", "skirt": "تنورة",
    "cream": "كريم", "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "oil": "زيت", "spray": "بخاخ",
}

# ===== Brands =====
BRANDS = {
    "SONGMICS": ["songmics"], "Nike": ["nike"], "Adidas": ["adidas"], "Apple": ["iphone", "ipad", "macbook", "airpods"],
}

OPENING_LINES = [
    "🔥 عرض مميز لا يفوت!", "✨ منتج مميز للجميع!", "💎 أفضل اختيار اليوم!", "🏆 منتج عالي الجودة بسعر ممتاز!",
]

# ===== وظائف مساعدة =====
def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def is_amazon_url(url):
    return any(p in url.lower() for p in ["amazon.", "amzn.to", "amzn.com"])

def expand_short_url(url):
    try:
        if "amzn.to" in url.lower():
            r = requests.get(url, headers=get_random_headers(), allow_redirects=True, timeout=20)
            return r.url
        return url
    except:
        return url

def extract_asin(url):
    for p in [r"/dp/([A-Z0-9]{10})", r"/gp/product/([A-Z0-9]{10})", r"/([A-Z0-9]{10})(?:[/?]|$)"]:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_high_quality_image(soup):
    try:
        img = soup.select_one("#landingImage")
        if img:
            url = img.get("data-old-hires") or img.get("src")
            if url:
                url = re.sub(r"\._.*_\.", ".", url)
                url = re.sub(r"_SL\d+_", "_SL1500_", url)
                return url
        alt_images = soup.select("#altImages img")
        for alt_img in alt_images:
            src = alt_img.get("src")
            if src:
                src = src.replace("_SS40_", "_SL1500_")
                return src
    except:
        pass
    return None

# ===== طرق استخراج المنتج =====
def get_from_google_cache(asin, domain):
    try:
        url = f"https://webcache.googleusercontent.com/search?q=cache:https://{domain}/dp/{asin}"
        r = requests.get(url, headers=get_random_headers(), timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.select_one("#productTitle")
            price_tag = soup.select_one(".a-price .a-offscreen")
            if title_tag:
                return {
                    "title": title_tag.text.strip(),
                    "price": price_tag.text.strip() if price_tag else "غير متوفر",
                    "image": get_high_quality_image(soup)
                }
    except:
        pass
    return None

def get_from_textise(asin, domain):
    try:
        url = f"https://r.jina.ai/http://{domain}/dp/{asin}"
        r = requests.get(url, headers=get_random_headers(), timeout=15)
        if r.status_code == 200:
            lines = [l.strip() for l in r.text.split('\n') if l.strip()]
            title = lines[0][:200] if lines else "منتج"
            prices = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:SAR|USD|\$|ريال)', r.text)
            current_price = prices[0] + " ريال" if prices else "غير متوفر"
            return {"title": title, "price": current_price, "image": None}
    except:
        pass
    return None

def get_with_curl(asin, domain):
    try:
        url = f"https://{domain}/dp/{asin}"
        cmd = ["curl", "--silent", "--location", "--header", "User-Agent: Mozilla/5.0", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and "productTitle" in result.stdout:
            soup = BeautifulSoup(result.stdout, "html.parser")
            title_tag = soup.select_one("#productTitle")
            price_tag = soup.select_one(".a-price .a-offscreen")
            if title_tag:
                return {
                    "title": title_tag.text.strip(),
                    "price": price_tag.text.strip() if price_tag else "غير متوفر",
                    "image": get_high_quality_image(soup)
                }
    except:
        pass
    return None

def get_product(asin, domain):
    methods = [get_from_google_cache, get_from_textise, get_with_curl]
    for method in methods:
        prod = method(asin, domain)
        if prod and prod.get("title"):
            return prod
        time.sleep(0.5)
    return None

# ===== الترجمة الذكية =====
def translate_word(word):
    w = word.lower()
    if w in TRANSLATIONS:
        return TRANSLATIONS[w]
    # لو مش موجود في القاموس نعمل transliteration بسيطة
    w_ar = ''
    mapping = {
        'a':'ا','b':'ب','c':'ك','d':'د','e':'ي','f':'ف','g':'ج','h':'ه','i':'ي','j':'ج',
        'k':'ك','l':'ل','m':'م','n':'ن','o':'و','p':'ب','q':'ك','r':'ر','s':'س','t':'ت',
        'u':'و','v':'ف','w':'و','x':'كس','y':'ي','z':'ز','0':'0','1':'1','2':'2','3':'3',
        '4':'4','5':'5','6':'6','7':'7','8':'8','9':'9'
    }
    for c in word:
        w_ar += mapping.get(c.lower(), c)
    return w_ar

def translate_product(title):
    words = title.split()
    translated = []
    for w in words:
        translated.append(translate_word(w))
    return " ".join(translated)

def get_brand(title):
    t = title.lower()
    for brand, keys in BRANDS.items():
        if any(k in t for k in keys):
            return brand
    return None

def format_price(price):
    try:
        num = int(float(re.sub(r"[^\d]", "", price)))
        return f"💰 السعر: {num} ريال"
    except:
        return f"💰 السعر: {price}"

def generate_post(product, url):
    brand = get_brand(product["title"])
    product_name = translate_product(product["title"])
    opening = random.choice(OPENING_LINES)
    brand_str = f" ({brand})" if brand else ""
    post = f"{opening}\n\n🛒 {product_name}{brand_str}\n\n{format_price(product['price'])}\n\n🔗 {url}"
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r"https?://\S+", msg.text)
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return
    for url in urls:
        if not is_amazon_url(url):
            continue
        wait = bot.reply_to(msg, "⏳ جاري جلب المنتج...")
        original_url = url
        expanded_url = expand_short_url(url)
        asin = extract_asin(expanded_url)
        if not asin:
            bot.edit_message_text("❌ لم يتم العثور على ASIN", msg.chat.id, wait.message_id)
            continue
        domain = "amazon.com" if "amazon.com" in expanded_url else "amazon.sa"
        prod = get_product(asin, domain)
        if not prod:
            bot.edit_message_text("❌ فشل في جلب المنتج", msg.chat.id, wait.message_id)
            continue
        post = generate_post(prod, original_url)
        try:
            if prod.get("image"):
                bot.send_photo(msg.chat.id, prod["image"], caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except:
            bot.send_message(msg.chat.id, post)

print("🔥 البوت شغال!")
bot.infinity_polling()
