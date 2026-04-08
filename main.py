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

# ================= فك الرابط المختصر =================
def expand_url(url):
    try:
        r = requests.get(url, headers=get_headers(), allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

# ================= استخراج ASIN =================
def extract_asin(url):
    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})"
    ]

    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    return None

# ================= تنظيف العنوان =================
def clean_title(text):
    if not text:
        return ""

    text = re.sub(r'[^\w\s\u0600-\u06FF\-]', ' ', text)
    return " ".join(text.split())

# ================= استخراج البراند =================
def get_brand(title):
    brands = [
        "Apple", "Samsung", "Sony", "Nike", "Adidas",
        "Huawei", "Xiaomi", "Lenovo", "HP", "Dell",
        "Chanel", "Dior", "Gucci", "Zara", "H&M",
        "L'Oreal", "Nivea", "Dove", "Pampers", "Gillette"
    ]

    for brand in brands:
        if brand.lower() in title.lower():
            return brand

    return None

# ================= جلب المنتج =================
def get_product(url):
    headers = get_headers()

    # إجبار اللغة العربية
    if "?" in url:
        url += "&language=ar_AE"
    else:
        url += "?language=ar_AE"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # ===== العنوان =====
        title_tag = soup.select_one("#productTitle")
        title = None

        if title_tag:
            title = title_tag.text.strip()

        # fallback
        if not title:
            meta = soup.select_one("meta[property='og:title']")
            if meta:
                title = meta.get("content")

        title = clean_title(title)

        if not title or len(title) < 5:
            return None

        # ===== السعر =====
        price_tag = soup.select_one(".a-price .a-offscreen")
        price = price_tag.text.strip() if price_tag else "غير متوفر"

        # ===== الصورة =====
        img = soup.select_one("#landingImage")
        image = img.get("src") if img else None

        return {
            "title": title,
            "price": price,
            "image": image
        }

    except Exception as e:
        print(e)
        return None

# ================= توليد البوست =================
def generate_post(title, price, original_url):
    brand = get_brand(title)
    brand_text = f" ({brand})" if brand else ""

    post = f"""🔥 منتج يستحق التجربة

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
        wait = bot.reply_to(msg, "⏳ جاري التحميل...")

        original_url = url

        # فك الرابط المختصر
        expanded_url = expand_url(url)

        if "amazon." not in expanded_url:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue

        product = get_product(expanded_url)

        if not product:
            bot.edit_message_text(
                "❌ فشل في جلب المنتج",
                msg.chat.id,
                wait.message_id
            )
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
