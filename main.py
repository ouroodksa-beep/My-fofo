import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🔥 تحليل نوع المنتج
# ===================================

TECH_KEYWORDS = ["iphone", "samsung", "laptop", "tablet", "headphone", "airpods", "monitor", "camera"]
FASHION_KEYWORDS = ["shirt", "dress", "shoes", "nike", "adidas", "bag", "watch"]
PERFUME_KEYWORDS = ["perfume", "fragrance", "parfum", "oud", "attar"]

def detect_product_style(title):
    t = title.lower()

    if any(k in t for k in TECH_KEYWORDS):
        return "tech"
    elif any(k in t for k in FASHION_KEYWORDS):
        return "youth"
    elif any(k in t for k in PERFUME_KEYWORDS):
        return "luxury"
    else:
        return "general"


# ===================================
# 🎯 أساليب التسويق
# ===================================

OPENINGS = {
    "tech": ["⚡️ عرض تقني قوي", "🔥 سعر ممتاز على جهاز مطلوب", "🚀 فرصة لمحبي التقنية"],
    "youth": ["🔥 ستايل وسعر بنفس الوقت", "⚡️ خيار شبابي ملفت", "💥 عرض مناسب للموضة"],
    "luxury": ["💎 عرض فاخر بسعر ذكي", "✨ خيار راقي حالياً", "🔥 فخامة بسعر أقل"],
    "general": ["🔥 تخفيض يستحق الانتباه", "⚡️ سعر خارج التوقع", "💥 فرصة مناسبة"]
}

ENDINGS = {
    "tech": ["قرار ممتاز لعشاق التقنية", "ممكن ما يتكرر", "فرصة للتطوير"],
    "youth": ["اختيار مناسب حالياً", "ستايل بسعر أقل", "واضح إنه يستاهل"],
    "luxury": ["الفخامة ما تنتظر", "فرصة للتميز", "خيار راقي فعلاً"],
    "general": ["خيار ذكي حالياً", "وقته مناسب", "اللي يحتاجه لا يفوت"]
}


# ===================================
# 💰 السعر التشويقي فقط
# ===================================

def format_price_saudia(price):
    try:
        num = re.findall(r'[\d,]+', price)
        if num:
            main = num[0].replace(",", "")
            main_int = int(float(main))

            hooks = [
                f"{main_int} ريال 😍",
                f"{main_int} ريال 🔥",
                f"{main_int} ريال ⚡️",
                f"{main_int} ريال 💥",
                f"{main_int} ريال 🎯",
            ]
            return random.choice(hooks)
    except:
        pass

    return price


# ===================================
# 🏷 اختصار العنوان + البراند
# ===================================

def smart_title(title):
    words = title.split()
    brand = words[0] if words else ""
    short = " ".join(words[:10])
    return f"{brand} | {short}"


# ===================================
# 🔗 فك الروابط
# ===================================

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ow.ly']):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            return r.url
        return url
    except:
        return url


def is_saudi_amazon(url):
    return "amazon.sa" in url.lower()


def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'([A-Z0-9]{10})(?:[/?]|\b)'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


# ===================================
# 🧠 Scraping القوي (كما كان)
# ===================================

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)

        if r.status_code != 200:
            return None

        if len(r.text) < 3000 or "captcha" in r.text.lower():
            return None

    except:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # العنوان
    title = None
    for s in ["#productTitle", "h1.a-size-large", "#title"]:
        elem = soup.select_one(s)
        if elem:
            title = elem.text.strip()
            if len(title) > 5:
                break

    if not title:
        return None

    # السعر
    price = None
    for s in [
        ".a-price-to-pay .a-offscreen",
        ".a-price .a-offscreen",
        ".a-price-whole"
    ]:
        elem = soup.select_one(s)
        if elem and any(c.isdigit() for c in elem.text):
            price = elem.text.strip()
            break

    if not price:
        m = re.findall(r'(\d{1,3}(?:,\d{3})*)\s*(?:ر\.?س|SAR)', r.text)
        if m:
            price = m[0]

    # السعر القديم
    old_price = None
    old_elem = soup.select_one(".a-text-price .a-offscreen")
    if old_elem and old_elem.text != price:
        old_price = old_elem.text.strip()

    # الصورة
    image = None
    img = soup.select_one("#landingImage")
    if img:
        image = img.get("src") or img.get("data-old-hires")

    # الخصم
    discount_percent = None
    try:
        if old_price and price:
            old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
            new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
            if old_num > new_num:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        pass

    return title, price, old_price, image, discount_percent


# ===================================
# ✨ التوليد النهائي
# ===================================

def generate_post(title, price, old_price, discount_percent, original_url):
    style = detect_product_style(title)

    opening = random.choice(OPENINGS[style])
    ending = random.choice(ENDINGS[style])

    display_title = smart_title(title)
    price_line = format_price_saudia(price)

    if discount_percent and discount_percent > 5:
        price_line += f" (وفر {discount_percent}%)"

    post = f"""{opening}

🛒 {display_title}

💰 {price_line}

👉 {ending}

🔗 {original_url}"""

    return post


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج")
        return

    for original_url in urls:
        expanded = expand_url(original_url)

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط لازم من أمازون السعودية")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج ASIN")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)
            continue

        title, price, old_price, image, discount_percent = product
        post = generate_post(title, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)
        except:
            bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()


