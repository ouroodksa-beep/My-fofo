import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import os

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

DB_FILE = "posted.txt"

if not os.path.exists(DB_FILE):
    open(DB_FILE, "w").close()

def expand_url(url):
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        return r.url
    except:
        return url

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

def is_posted(asin):
    with open(DB_FILE, "r") as f:
        return asin in f.read()

def mark_posted(asin):
    with open(DB_FILE, "a") as f:
        f.write(asin + "\n")

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ar-SA,ar;q=0.9"
    }

    r = requests.get(url, headers=headers, timeout=20)

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title_elem = soup.select_one("#productTitle")
    price_elem = soup.select_one(".a-price .a-offscreen")
    old_price_elem = soup.select_one(".priceBlockStrikePriceString")
    img_elem = soup.select_one("#landingImage")

    if not title_elem or not price_elem:
        return None

    title = title_elem.text.strip()
    price = price_elem.text.strip()
    old_price = old_price_elem.text.strip() if old_price_elem else None
    image = img_elem.get("src") if img_elem else None

    discount_percent = None

    try:
        if old_price:
            old_num = float(re.findall(r'\d+', old_price.replace(",", ""))[0])
            new_num = float(re.findall(r'\d+', price.replace(",", ""))[0])
            discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        discount_percent = None

    return title, price, old_price, image, discount_percent

OPENINGS = [
"بصراحة عرض خرافي.",
"فرصة قوية اليوم.",
"السعر حالياً مغري جداً.",
"أفضل صفقة تشوفها اليوم.",
"عرض ما يتكرر."
]

HUMAN = [
"أنصح فيه بقوة.",
"ما راح تندم عليه.",
"صفقة ناجحة فعلاً.",
"يفرق معك فعلياً."
]

CTA = [
"لا تنتظر لين يخلص.",
"استغل السعر قبل يتغير.",
"الكمية محدودة.",
"لا تضيع الفرصة."
]

def generate_post(title, price, old_price, discount_percent, affiliate_url):
    s1 = random.choice(OPENINGS)
    s2 = random.choice(HUMAN)
    s3 = random.choice(CTA)

    if discount_percent and discount_percent > 5:
        discount_text = f"خصم {discount_percent}% 🔥 بدل {old_price} صار {price}."
    else:
        discount_text = f"بسعر {price}."

    post = f"""{s1} {discount_text} {s2} {s3}

🛍️ {title}

💰 السعر: {price}

🔗 {affiliate_url}
"""
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):

    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج.")
        return

    for original_url in urls:

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        expanded_url = expand_url(original_url)
        asin = extract_asin(expanded_url)

        if not asin:
            bot.edit_message_text("الرابط غير صحيح.", msg.chat.id, wait.message_id)
            return

        if is_posted(asin):
            bot.edit_message_text("تم نشر المنتج مسبقاً.", msg.chat.id, wait.message_id)
            return

        product = get_product(asin)

        if not product:
            bot.edit_message_text("ما قدرت أقرأ المنتج.", msg.chat.id, wait.message_id)
            return

        title, price, old_price, image, discount_percent = product

        post = generate_post(title, price, old_price, discount_percent, original_url)

        if image:
            bot.send_photo(msg.chat.id, image, caption=post)
        else:
            bot.send_message(msg.chat.id, post)

        mark_posted(asin)
        bot.delete_message(msg.chat.id, wait.message_id)

print("Bot Running...")
bot.infinity_polling()
