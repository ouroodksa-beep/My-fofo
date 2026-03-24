import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🌟 جمل تسويقية احترافية (محايدة)
# ===================================

MARKETING_SENTENCES = [
    "صيدة قوية اليوم 🔥",
    "عرض يستاهل الوقفة 👀",
    "فرصة ممتازة ما تتفوت 💯",
    "سعر فعلياً نادر 🔥",
    "من أقوى العروض حالياً ⚡️",
    "لقطة مميزة بهالسعر 👌",
    "عرض قوي لفترة محدودة ⏳",
    "السعر حالياً مغري جداً 💸",
    "فرصة تستحق الاستغلال 🔥",
    "واحدة من أفضل الصفقات حالياً 💯",
    "عرض يستاهل الاهتمام 👀",
    "السعر حالياً تحت السوق 📉",
    "فرصة ممتازة للتوفير 💰",
    "عرض محدود لا يفوت ⏰",
    "صفقة قوية بهالسعر 🔥",
    "سعر منافس جداً حالياً ⚡️",
    "فرصة جميلة للتوفير 💸",
    "عرض يستحق التجربة 👌",
    "من أفضل الأسعار المتوفرة الآن 📉",
    "لقطة حلوة بهالسعر 🔥",
    "عرض قوي لفترة قصيرة ⏳",
    "فرصة ممتازة قبل ينتهي العرض ⚡️",
    "السعر حالياً مغري جداً 👌",
    "عرض نادر بالسوق حالياً 💯",
    "فرصة تستاهل الانتباه 👀",
    "صفقة حلوة بهالسعر 💰",
    "عرض قوي والتوفير واضح 🔥",
    "فرصة ممتازة حالياً 📉",
    "سعر يعتبر فرصة حقيقية 💯",
    "من العروض اللي تستحق 🔥",
    "عرض جميل بهالسعر 👌",
    "فرصة مو دايم تتكرر ⏳",
    "السعر حالياً جداً مناسب 💸"
]

def get_opening_sentence():
    return random.choice(MARKETING_SENTENCES)

# ===================================
# 🔧 أدوات مساعدة
# ===================================

def expand_url(url):
    try:
        if any(short in url for short in ['amzn.to', 'bit.ly', 't.co']):
            return requests.get(url, allow_redirects=True).url
        return url
    except:
        return url

def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None

def clean_price(price_text):
    try:
        num = float(re.findall(r'[\d,.]+', price_text)[0].replace(",", ""))
        return f"{int(num)} ريال"
    except:
        return price_text

# ===================================
# 📦 جلب المنتج
# ===================================

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("#productTitle")
    price = soup.select_one(".a-price .a-offscreen")

    if not title or not price:
        return None

    title = title.text.strip()
    price = price.text.strip()

    return title, price

# ===================================
# ✨ إنشاء البوست
# ===================================

def generate_post(name, price, url):
    opening = get_opening_sentence()

    return f"""{opening}

🛒 {name}

💰 السعر: {clean_price(price)}

🔗 {url}
"""

# ===================================
# 🤖 البوت
# ===================================

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج")
        return

    for url in urls:
        expanded = expand_url(url)
        asin = extract_asin(expanded)

        if not asin:
            bot.reply_to(msg, "رابط غير صحيح")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)
            continue

        name, price = product
        post = generate_post(name, price, url)

        bot.send_message(msg.chat.id, post)
        bot.delete_message(msg.chat.id, wait.message_id)

print("🤖 البوت يعمل...")
bot.infinity_polling()
