import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ================= Headers =================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8"
    }

# ================= فك الرابط =================
def expand_url(url):
    try:
        r = requests.get(url, headers=get_headers(), allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

# ================= تنظيف العنوان =================
def clean_title(text):
    if not text:
        return ""
    text = re.sub(r'[^\w\s\u0600-\u06FF\-]', ' ', text)
    return " ".join(text.split())

# ================= ترجمة ذكية =================
def smart_translate(text):
    TRANSLATIONS = {
        "cabinet": "خزانة",
        "shelf": "رف",
        "organizer": "منظم",
        "kitchen": "مطبخ",
        "metal": "معدني",
        "set": "طقم",
        "white": "أبيض",
        "black": "أسود",
        "table": "طاولة",
        "chair": "كرسي"
    }

    words = text.split()
    result = []

    for w in words:
        lw = w.lower()
        if lw in TRANSLATIONS:
            result.append(TRANSLATIONS[lw])
        else:
            result.append(w)

    return " ".join(result)

# ================= استخراج السعر =================
def extract_price(text):
    prices = re.findall(r'(\d{1,3}(?:,\d{3})*)\s*(?:ريال|SAR)', text)
    if not prices:
        return "غير متوفر"

    return prices[0] + " ريال"

# ================= استخراج البراند =================
def get_brand(title):
    brands = [
        "Apple", "Samsung", "Sony", "Nike", "Adidas",
        "Huawei", "Xiaomi", "Lenovo", "HP", "Dell",
        "Chanel", "Dior", "Gucci", "Zara", "H&M",
        "L'Oreal", "Nivea", "Dove", "Pampers", "Gillette",
        "SONGMICS"
    ]

    for b in brands:
        if b.lower() in title.lower():
            return b

    return None

# ================= طريقة jina =================
def get_with_jina(url):
    try:
        text_url = url.replace("https://", "https://r.jina.ai/https://")
        r = requests.get(text_url, timeout=15)
        text = r.text

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # اختيار عنوان مناسب
        title = None
        for line in lines:
            if len(line) > 20 and not line.lower().startswith("title"):
                title = line
                break

        title = clean_title(title)

        if not title or len(title) < 5:
            return None

        price = extract_price(text)

        # صورة نظيفة
        images = re.findall(r'https://[^ ]+\.jpg', text)
        image = None
        for img in images:
            if "images-na.ssl-images-amazon" in img:
                image = img
                break

        return {
            "title": title,
            "price": price,
            "image": image
        }

    except Exception as e:
        print("Jina error:", e)
        return None

# ================= fallback direct =================
def get_direct(url):
    try:
        if "?" in url:
            url += "&language=ar_AE"
        else:
            url += "?language=ar_AE"

        r = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        title_tag = soup.select_one("#productTitle")
        title = title_tag.text.strip() if title_tag else None

        if not title:
            meta = soup.select_one("meta[property='og:title']")
            if meta:
                title = meta.get("content")

        title = clean_title(title)

        if not title or len(title) < 5:
            return None

        price_tag = soup.select_one(".a-price .a-offscreen")
        price = price_tag.text.strip() if price_tag else "غير متوفر"

        img = soup.select_one("#landingImage")
        image = img.get("src") if img else None

        return {
            "title": title,
            "price": price,
            "image": image
        }

    except Exception as e:
        print("Direct error:", e)
        return None

# ================= اختيار أفضل طريقة =================
def get_product(url):
    data = get_with_jina(url)
    if data:
        return data

    return get_direct(url)

# ================= توليد البوست =================
def generate_post(title, price, original_url):
    brand = get_brand(title)

    # ترجمة لو مفيش عربي
    if not re.search(r'[\u0600-\u06FF]', title):
        title = smart_translate(title)

    brand_text = f" ({brand})" if brand else ""

    post = f"""🔥 عرض مميز لفترة محدودة!

🛒 {title}{brand_text}

💰 السعر: {price}

🔗 {original_url}
"""
    return post

# ================= البوت =================
@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r"https?://\S+", msg.text)

    if not urls:
        bot.reply_to(msg, "❌ ابعت رابط أمازون")
        return

    for url in urls:
        wait = bot.reply_to(msg, "⏳ جاري جلب المنتج...")

        original_url = url
        expanded = expand_url(url)

        if "amazon." not in expanded:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue

        product = get_product(expanded)

        if not product:
            bot.edit_message_text("❌ فشل في جلب المنتج", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product["title"], product["price"], original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)

        except Exception as e:
            print(e)
            bot.send_message(msg.chat.id, post)

print("🔥 البوت شغال")
bot.infinity_polling()
