import requests
from bs4 import BeautifulSoup
import telebot
import re
import random


# ===== الإعدادات =====
TOKEN = "PUT_TOKEN"
SCRAPER_API_KEY = "PUT_SCRAPER"
OPENAI_API_KEY = "PUT_OPENAI"


bot = telebot.TeleBot(TOKEN)


# ===== توسيع الرابط =====
def expand_short_url(url):
    try:
        return requests.head(url, allow_redirects=True).url
    except:
        return url


# ===== استخراج ASIN =====
def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


# ===== تنظيف السعر =====
def format_price(text):
    try:
        price = re.search(r'[\d,.]+', text).group()
        return int(float(price.replace(',', '')))
    except:
        return None


# ===== جلب المنتج =====
def get_product(asin):
    try:
        url = f"https://www.amazon.sa/dp/{asin}"
        scraper = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}&country_code=sa"

        r = requests.get(scraper)
        soup = BeautifulSoup(r.content, "html.parser")

        title = soup.select_one("#productTitle").text.strip()
        price = format_price(soup.select_one(".a-price .a-offscreen").text)
        img = soup.select_one("#landingImage")

        image = img.get("src") if img else None

        return title, price, image
    except:
        return None, None, None


# ===== ذكاء صناعي احترافي =====
def ai_marketing(title, price):

    fake_old = int(price * random.uniform(1.3, 1.6))

    hooks = [
        "🔥🔥 عرض اليوم القوي",
        "😍 المفاجأة وصلت",
        "💥 أقوى عروض اليوم",
        "🚨 لا يفوتكم العرض",
        "🔥 خصم كبير اليوم فقط"
    ]

    scarcity = [
        "الكمية محدودة ⏳",
        "العرض لفترة قصيرة",
        "سارع قبل نفاذ الكمية",
        "متوفر حالياً فقط"
    ]

    hook = random.choice(hooks)
    scarce = random.choice(scarcity)

    text = f"""{hook}

وفرنا عليكم بدل {fake_old} ريال 😍

السعر الآن {price} ريال فقط

جودة ممتازة ومناسبة للاستخدام اليومي

{scarce}
"""

    return text


# ===== استقبال الرسائل =====
@bot.message_handler(func=lambda m: True)
def handle(message):

    urls = re.findall(r'https?://\S+', message.text)

    if not urls:
        bot.reply_to(message, "أرسل رابط أمازون")
        return

    for original_url in urls:

        if "amazon" not in original_url and "amzn" not in original_url:
            continue

        wait = bot.reply_to(message, "جاري تجهيز العرض...")

        expanded = expand_short_url(original_url)
        asin = extract_asin(expanded)

        if not asin:
            bot.edit_message_text("الرابط غير صالح", message.chat.id, wait.message_id)
            continue

        title, price, image = get_product(asin)

        if not title:
            bot.edit_message_text("ما قدرت أقرأ المنتج", message.chat.id, wait.message_id)
            continue

        post = ai_marketing(title, price)

        final = f"""{post}

🔗 الرابط:
{original_url}
"""

        try:
            if image:
                bot.send_photo(message.chat.id, image, caption=final)
            else:
                bot.send_message(message.chat.id, final)

            bot.delete_message(message.chat.id, wait.message_id)

        except:
            bot.edit_message_text("خطأ", message.chat.id, wait.message_id)


print("Bot Running...")
bot.infinity_polling()
