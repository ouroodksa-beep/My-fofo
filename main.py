import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
import time

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

TRANSLATIONS = {
    "cabinet": "خزانة", "shelf": "رف", "organizer": "منظم", "metal": "معدني", "kitchen": "مطبخ",
    "white": "أبيض", "black": "أسود", "chair": "كرسي", "table": "طاولة", "set": "طقم",
    "bag": "شنطة", "shoes": "حذاء", "dress": "فستان", "skirt": "تنورة", "cream": "كريم",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون", "oil": "زيت", "spray": "بخاخ",
}

BRANDS = {
    "SONGMICS": ["songmics"], "Nike": ["nike"], "Adidas": ["adidas"], "Apple": ["iphone", "ipad", "macbook", "airpods"],
}

OPENING_LINES = [
    "🔥 عرض مميز لا يفوت!", "✨ منتج مميز للجميع!", "💎 أفضل اختيار اليوم!", "🏆 منتج عالي الجودة بسعر ممتاز!",
]

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
            url = img.get("data-old-hires")
            if url:
                return url
            dyn = img.get("data-a-dynamic-image")
            if dyn:
                data = json.loads(dyn)
                max_url = max(data.keys(), key=lambda x: data[x][0]*data[x][1])
                return max_url
            src = img.get("src")
            if src:
                src = re.sub(r"\._.*_\.", ".", src)
                src = re.sub(r"_SL\d+_", "_SL1500_", src)
                return src
        alt_images = soup.select("#altImages img")
        for alt_img in alt_images:
            src = alt_img.get("src")
            if src and "images-na" in src:
                src = src.replace("_SS40_", "_SL1500_")
                return src
    except:
        pass
    return None

def get_product_from_amazon(asin, domain):
    url = f"https://{domain}/dp/{asin}"
    headers = get_random_headers()
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.select_one("#productTitle")
            price_tag = soup.select_one(".a-price .a-offscreen")
            if title_tag:
                title = title_tag.text.strip()
                price = price_tag.text.strip() if price_tag else "غير متوفر"
                image = get_high_quality_image(soup)
                return {"title": title, "price": price, "image": image}
    except Exception as e:
        print(f"Error fetching product: {e}")
    return None

def translate_product(title):
    words = title.split()
    translated = []
    for w in words:
        translated.append(TRANSLATIONS.get(w.lower(), w))
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
        if "amazon." not in expanded_url:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue
        
        asin = extract_asin(expanded_url)
        if not asin:
            bot.edit_message_text("❌ لم يتم العثور على ASIN", msg.chat.id, wait.message_id)
            continue
        
        domain = "amazon.com" if "amazon.com" in expanded_url else "amazon.sa"
        prod = get_product_from_amazon(asin, domain)
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
        except Exception as e:
            print(f"Error sending: {e}")
            bot.send_message(msg.chat.id, post)

print("🔥 البوت شغال!")
bot.infinity_polling()
