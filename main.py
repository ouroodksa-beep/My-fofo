import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import re
import time


# ===== الإعدادات =====

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"

SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"

OPENAI_API_KEY = "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"



bot = telebot.TeleBot(TOKEN)

app = Flask('')


@app.route('/')
def home():
    return "Bot Active"



def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)



# ===== توسيع روابط أمازون المختصرة =====

def expand_short_url(short_url):

    try:
        response = requests.head(short_url, allow_redirects=True, timeout=10)
        return response.url
    except:
        return short_url



# ===== استخراج ASIN =====

def extract_asin(url):

    if 'amzn.to' in url or 'amzn.eu' in url:
        url = expand_short_url(url)

    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'product/([A-Z0-9]{10})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).upper()

    return None



# ===== تنظيف السعر =====

def format_price(price_str):

    try:
        price_clean = price_str.replace(',', '').strip()
        return str(int(float(price_clean)))
    except:
        return price_str



# ===== تحديد الصنف =====

def get_category(title):

    t = title.lower()

    if any(x in t for x in ['shoe', 'sneaker', 'boot']):
        return "أحذية"

    elif any(x in t for x in ['phone', 'laptop', 'tablet']):
        return "إلكترونيات"

    elif any(x in t for x in ['perfume', 'beauty']):
        return "جمال"

    elif any(x in t for x in ['sport', 'fitness']):
        return "رياضة"

    elif any(x in t for x in ['baby', 'kids']):
        return "أطفال"

    return "ملابس"



# ===== AI كتابة البوست =====

def generate_post_with_ai(product):

    try:

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        system_msg = """
أنت مسوق سعودي محترف.
تكتب بوستات قصيرة جداً وجذابة باللهجة السعودية.
بدون إطالة.
"""

        user_msg = f"""
حوّل اسم المنتج للعربي.

اكتب بوست:

- جملة افتتاحية جذابة.

- سطر فاضي.

- اسم المنتج بالعربي + وصف بسيط (اللون – المقاس – الاستخدام).

- سطر فاضي.

- جملة حماسية للشراء.

لا تكتب السعر أو الرابط.

اسم المنتج:
{product['original_title']}
"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.8,
            "max_tokens": 120
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        result = response.json()

        if 'choices' in result:
            return result['choices'][0]['message']['content'].strip()

        return None

    except Exception as e:
        print(e)
        return None



# ===== جلب المنتج =====

def get_product_scraperapi(asin):

    try:

        amazon_url = f"https://www.amazon.sa/dp/{asin}"

        scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={amazon_url}&country_code=sa"

        response = requests.get(scraper_url, timeout=20)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        title_elem = soup.select_one('#productTitle')

        if not title_elem:
            return None

        title = title_elem.get_text().strip()

        price_elem = soup.select_one('.a-price .a-offscreen')

        if not price_elem:
            return None

        price = format_price(price_elem.get_text())

        img = soup.select_one('#landingImage')

        image = None

        if img:
            image = img.get('src')

        category = get_category(title)

        return {
            'original_title': title,
            'price': price,
            'image': image,
            'category': category,
            'url': amazon_url
        }

    except Exception as e:
        print(e)
        return None



# ===== إنشاء البوست النهائي =====

def generate_post(product):

    ai_text = generate_post_with_ai(product)

    if not ai_text:
        ai_text = "عرض قوي لا يفوت!"

    final_post = f"""{ai_text}

🔥 السعر: {product['price']} ريال فقط

📦 الصنف: {product['category']}

🔗 الرابط:
{product['url']}"""

    return final_post



# ===== استقبال الرسائل =====

@bot.message_handler(func=lambda m: True)
def handle_message(message):

    chat_id = message.chat.id

    urls = re.findall(r'https?://\S+', message.text)

    if not urls:
        bot.reply_to(message, "أرسل رابط أمازون")
        return

    for url in urls:

        if "amazon" not in url and "amzn" not in url:
            continue

        wait = bot.reply_to(message, "جاري قراءة المنتج...")

        expanded = expand_short_url(url)

        asin = extract_asin(expanded)

        if not asin:
            bot.edit_message_text("رابط غير صحيح", chat_id, wait.message_id)
            continue

        product = get_product_scraperapi(asin)

        if not product:
            bot.edit_message_text("ما قدرت أقرأ المنتج", chat_id, wait.message_id)
            continue

        post = generate_post(product)

        try:

            if product['image']:
                bot.send_photo(chat_id, product['image'], caption=post)
            else:
                bot.send_message(chat_id, post)

            bot.delete_message(chat_id, wait.message_id)

        except:
            bot.edit_message_text("خطأ أثناء الإرسال", chat_id, wait.message_id)



# ===== تشغيل =====

def keep_alive():
    while True:
        time.sleep(60)



if __name__ == "__main__":

    print("Bot starting...")

    try:
        bot.remove_webhook()
    except:
        pass

    Thread(target=run_flask, daemon=True).start()

    Thread(target=keep_alive, daemon=True).start()

    bot.infinity_polling()
