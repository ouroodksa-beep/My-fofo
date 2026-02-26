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
# 🎯 أساليب التسويق حسب الفئة
# ===================================

OPENINGS = {
    "tech": [
        "⚡️ عرض تقني قوي",
        "🔥 سعر ممتاز على جهاز مطلوب",
        "🚀 فرصة لمحبي التقنية",
        "🎯 خيار ذكي حالياً",
    ],
    "youth": [
        "🔥 ستايل وسعر بنفس الوقت",
        "⚡️ خيار شبابي ملفت",
        "💥 عرض مناسب للموضة",
        "🎯 لقطة للشباب",
    ],
    "luxury": [
        "💎 عرض فاخر بسعر ذكي",
        "✨ خيار راقي حالياً",
        "🔥 فخامة بسعر أقل",
        "🎯 صفقة لمحبي الفخامة",
    ],
    "general": [
        "🔥 تخفيض يستحق الانتباه",
        "⚡️ سعر خارج التوقع",
        "💥 فرصة مناسبة",
        "🎯 عرض واضح إنه قوي",
    ]
}

ENDINGS = {
    "tech": [
        "قرار ممتاز لعشاق التقنية",
        "ممكن ما يتكرر",
        "فرصة للتطوير",
        "وقته مناسب للشراء",
    ],
    "youth": [
        "اختيار مناسب حالياً",
        "ستايل بسعر أقل",
        "خيار شبابي ذكي",
        "واضح إنه يستاهل",
    ],
    "luxury": [
        "الفخامة ما تنتظر",
        "فرصة للتميز",
        "خيار راقي فعلاً",
        "يستحق التجربة",
    ],
    "general": [
        "خيار ذكي حالياً",
        "وقته مناسب",
        "اللي يحتاجه لا يفوت",
        "السعر يتغير بأي وقت",
    ]
}


# ===================================
# 💰 السعر التشويقي
# ===================================

def format_price_saudia(price):
    try:
        num = re.findall(r'[\d,]+', price)
        if num:
            main = num[0].replace(",", "")
            main_int = int(float(main))

            hooks = [
                f"تخيل بس {main_int} ريال 😍",
                f"بهالسعر فقط {main_int} ريال 🔥",
                f"سعر رهيب {main_int} ريال ⚡️",
                f"لقطة بـ {main_int} ريال 💥",
                f"أقل من المتوقع {main_int} ريال 🎯",
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
# باقي الكود كما هو
# ===================================

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co']):
            r = requests.get(url, allow_redirects=True, timeout=20)
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
        r'([A-Z0-9]{10})(?:[/?]|\b)'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            return None
    except:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("#productTitle")
    if not title:
        return None
    title = title.text.strip()

    price = None
    price_elem = soup.select_one(".a-price .a-offscreen")
    if price_elem:
        price = price_elem.text.strip()

    old_price = None
    old_elem = soup.select_one(".a-price.a-text-price .a-offscreen")
    if old_elem:
        old_price = old_elem.text.strip()

    image = None
    img_elem = soup.select_one("#landingImage")
    if img_elem:
        image = img_elem.get("src")

    discount_percent = None
    try:
        if old_price and price:
            old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
            new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
            if old_num > new_num:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        pass

    if not price:
        return None

    return title, price, old_price, image, discount_percent


# ===================================
# ✨ التوليد النهائي الذكي
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


