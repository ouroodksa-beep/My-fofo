import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import os

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

DB_FILE = "posted.txt"

if not os.path.exists(DB_FILE):
    open(DB_FILE, "w").close()

def expand_url(url):
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        return r.url
    except:
        return url

def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def is_posted(asin):
    with open(DB_FILE, "r") as f:
        return asin in f.read()

def mark_posted(asin):
    with open(DB_FILE, "a") as f:
        f.write(asin + "\n")

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # العنوان
    title_elem = soup.select_one("#productTitle")
    if not title_elem:
        return None
    
    title = title_elem.text.strip()

    # ===== استخراج السعر بطرق متعددة =====
    price = None
    old_price = None
    
    # الطريقة 1: السعر الحالي في صندوق السعر الرئيسي
    price_selectors = [
        ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
        ".a-price.a-text-price.apexPriceToPay .a-offscreen",
        ".a-price.aok-align-center .a-offscreen",
        ".a-price .a-offscreen",
        "[data-a-color='price'] .a-offscreen",
        ".a-price-whole",
        ".a-price .a-price-whole"
    ]
    
    for selector in price_selectors:
        elem = soup.select_one(selector)
        if elem:
            price_text = elem.text.strip()
            if price_text and any(c.isdigit() for c in price_text):
                price = price_text
                break
    
    # الطريقة 2: لو لقينا السعر بالريال بس بدون رمز
    if not price:
        price_pattern = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*ر\.?س', r.text)
        if price_pattern:
            price = f"{price_pattern.group(1)} ر.س"

    # السعر القديم
    old_price_selectors = [
        ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
        ".a-price.a-text-price .a-offscreen",
        ".priceBlockStrikePriceString",
        "[data-a-color='secondary'] .a-offscreen"
    ]
    
    for selector in old_price_selectors:
        elem = soup.select_one(selector)
        if elem:
            old_text = elem.text.strip()
            if old_text != price and any(c.isdigit() for c in old_text):
                old_price = old_text
                break

    # الصورة
    img_elem = soup.select_one("#landingImage")
    image = None
    if img_elem:
        image = img_elem.get("src") or img_elem.get("data-old-hires") or img_elem.get("data-a-dynamic-image")
        if image and isinstance(image, str) and image.startswith("{"):
            # لو الصورة فيها JSON
            try:
                import json
                img_dict = json.loads(image)
                image = list(img_dict.keys())[0] if img_dict else None
            except:
                pass

    # حساب الخصم
    discount_percent = None
    try:
        if old_price and price:
            # تنظيف الأرقام
            def clean_num(text):
                return float(re.sub(r'[^\d.]', '', text.replace(",", "")))
            
            old_num = clean_num(old_price)
            new_num = clean_num(price)
            
            if old_num > new_num > 0:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except Exception as e:
        print(f"Discount calc error: {e}")
        discount_percent = None

    if not price:
        return None

    return title, price, old_price, image, discount_percent

# ===== جمل سعودية حماسية وقصيرة =====

OPENINGS = [
    "صفقة 🔥",
    "سعر مجنون",
    "فرصة",
    "شوف السعر",
    "ببلاش",
    "عرض قوي",
    "ما يتكرر"
]

REACTIONS = [
    "يستاهل",
    "جودة ممتازة",
    "أنصح فيه",
    "من تجربة",
    "فادني كثير"
]

URGENCY = [
    "بسرعة",
    "ينتهي قريب",
    "الكمية تخلص",
    "لا تنتظر",
    "احجز الحين"
]

def generate_post(title, price, old_price, discount_percent, affiliate_url):
    opening = random.choice(OPENINGS)
    reaction = random.choice(REACTIONS)
    urgency = random.choice(URGENCY)
    
    # عنوان مختصر
    short_title = title[:50] + ".." if len(title) > 50 else title
    
    # نص السعر
    if discount_percent and discount_percent > 5:
        price_line = f"🔥 {discount_percent}% خصم | {old_price} ⬅️ {price}"
    else:
        price_line = f"💰 {price}"
    
    # منشور قصير وحيوي
    post = f"""{opening}

{short_title}

{price_line}

{reaction} | {urgency}

🔗 {affiliate_url}"""
    
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط أمازون")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳..")

        expanded_url = expand_url(original_url)
        asin = extract_asin(expanded_url)

        if not asin:
            bot.edit_message_text("❌ رابط غلط", msg.chat.id, wait.message_id)
            return

        if is_posted(asin):
            bot.edit_message_text("⚠️ نشرته قبل", msg.chat.id, wait.message_id)
            return

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ ما لقيت السعر، جرب رابط ثاني", msg.chat.id, wait.message_id)
            return

        title, price, old_price, image, discount_percent = product

        post = generate_post(title, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            mark_posted(asin)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            bot.edit_message_text("❌ صار خطأ، جرب تاني", msg.chat.id, wait.message_id)

print("🤖 شغال...")
bot.infinity_polling()
