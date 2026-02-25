import requests
from bs4 import BeautifulSoup
import telebot
import os
import re
import random
from flask import Flask
from threading import Thread


# ================== Environment Variables ==================

TOKEN = os.getenv("TOKEN")
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or ":" not in TOKEN:
    raise ValueError("Telegram TOKEN is missing or invalid")

if not SCRAPER_API_KEY:
    raise ValueError("SCRAPER_API_KEY is missing")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing")


bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# ================== Flask Keep Alive ==================

@app.route("/")
def home():
    return "Bot is running"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ================== Helpers ==================

def expand_url(url):
    try:
        return requests.head(url, allow_redirects=True, timeout=10).url
    except:
        return url


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


def clean_price(text):
    try:
        price = re.search(r"[\d,.]+", text).group()
        return int(float(price.replace(",", "")))
    except:
        return None


# ================== Get Product ==================

def get_product(asin):
    try:
        amazon_url = f"https://www.amazon.sa/dp/{asin}"
        scraper = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={amazon_url}&country_code=sa"

        r = requests.get(scraper, timeout=20)
        soup = BeautifulSoup(r.content, "html.parser")

        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")
        image = soup.select_one("#landingImage")

        if not title or not price:
            return None

        return {
            "title": title.text.strip(),
            "price": clean_price(price.text),
            "image": image.get("src") if image else None
        }

    except:
        return None


# ================== AI Marketing ==================

def generate_marketing_text(title, price):

    fake_old = int(price * random.uniform(1.3, 1.6))

    hooks = [
        "🔥🔥 عرض اليوم القوي",
        "💥 لا يفوتكم العرض",
        "😍 المفاجأة وصلت",
        "🚨 خصم جامد اليوم فقط"
    ]

    scarcity = [
        "الكمية محدودة ⏳",
        "سارع قبل نفاذ الكمية",
        "العرض لفترة قصيرة",
        "متوفر حالياً فقط"
    ]

    hook = random.choice(hooks)
    scarce = random.choice(scarcity)

    text = f"""{hook}

نوفر عليكم بدل {fake_old} ريال 😍

السعر الآن {price} ريال فقط

جودة ممتازة ومناسبة للاستخدام اليومي

{scarce}
"""

    return text


# ================== Telegram Handler ==================

@bot.message_handler(func=lambda m: True)
def handle_message(message):

    urls = re.findall(r'https?://\S+', message.text)

    if not urls:
        bot.reply_to(message, "أرسل رابط أمازون")
        return

    for original_url in urls:

        if "amazon" not in original_url and "amzn" not in original_url:
            continue

        wait = bot.reply_to(message, "جاري تجهيز العرض...")

        expanded = expand_url(original_url)
        asin = extract_asin(expanded)

        if not asin:
            bot.edit_message_text("الرابط غير صالح", message.chat.id, wait.message_id)
            continue

        product = get_product(asin)

        if not product:
            bot.edit_message_text("ما قدرت أقرأ المنتج", message.chat.id, wait.message_id)
            continue

        marketing = generate_marketing_text(product["title"], product["price"])

        final_post = f"""{marketing}

🔗 الرابط:
{original_url}
"""

        try:
            if product["image"]:
                bot.send_photo(message.chat.id, product["image"], caption=final_post)
            else:
                bot.send_message(message.chat.id, final_post)

            bot.delete_message(message.chat.id, wait.message_id)

        except:
            bot.edit_message_text("حدث خطأ أثناء الإرسال", message.chat.id, wait.message_id)


# ================== Run ==================

if __name__ == "__main__":

    print("Bot Started Successfully")

    try:
        bot.remove_webhook()
    except:
        pass

    Thread(target=run_web).start()

    bot.infinity_polling()
