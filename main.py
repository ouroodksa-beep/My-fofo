import telebot
import cloudscraper
from bs4 import BeautifulSoup
import re
import random
import json

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

scraper = cloudscraper.create_scraper()

# ===================================
# 🧠 تحديد نوع المنتج
# ===================================
def detect_product_type(title):
    t = title.lower()
    if any(x in t for x in ["iphone","samsung","headphone","earbuds","laptop"]):
        return "electronics"
    if any(x in t for x in ["shirt","pants","dress","shoes"]):
        return "fashion"
    if any(x in t for x in ["cream","makeup","lipstick"]):
        return "beauty"
    return "general"

# ===================================
# 🎯 CTA
# ===================================
CTA = [
    "👉 الحق العرض",
    "👉 خذها قبل تخلص",
    "👉 اطلبه الحين",
]

# ===================================
# 🔗 استخراج ASIN
# ===================================
def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    return None

# ===================================
# 📦 جلب المنتج (قوي)
# ===================================
def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    try:
        r = scraper.get(url, timeout=7)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")

        if not title or not price:
            print("❌ Amazon Blocked")
            return None

        image = soup.select_one("#landingImage")
        image_url = image.get("src") if image else None

        return (
            title.text.strip(),
            price.text.strip(),
            image_url
        )

    except Exception as e:
        print("ERROR:", e)
        return None

# ===================================
# ✍️ بوست
# ===================================
def generate_post(title, price, url):
    product_name = title[:60]

    text = f"""🔥 عرض على {product_name}

{product_name}

💰 {price}

{random.choice(CTA)}

🔗 {url}
"""
    return text

# ===================================
# 🤖 البوت
# ===================================
@bot.message_handler(func=lambda m: True)
def handler(msg):

    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط امازون")
        return

    for url in urls:

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        if "amazon.sa" not in url:
            bot.edit_message_text("❌ الرابط لازم يكون amazon.sa", msg.chat.id, wait.message_id)
            continue

        asin = extract_asin(url)

        if not asin:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue

        product = get_product(asin)

        # 💥 fallback مهم
        if not product:
            bot.send_message(msg.chat.id, f"""🔥 المنتج موجود هنا 👇

🔗 {url}

(تعذر تحليل التفاصيل 😅)
""")
            bot.delete_message(msg.chat.id, wait.message_id)
            continue

        title, price, image = product

        post = generate_post(title, price, url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
        except:
            bot.send_message(msg.chat.id, post)

        bot.delete_message(msg.chat.id, wait.message_id)

print("🔥 BOT READY (FAST + BYPASS AMAZON)")
bot.infinity_polling()
