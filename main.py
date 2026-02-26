import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "PUT_YOUR_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)


# =========================
# جمل سعودي احترافي (AI مجاني)
# =========================

OPENINGS = [
"بصراحة عرض خرافي.",
"فرصة ما تتكرر.",
"السعر حالياً نار.",
"أفضل صفقة اليوم.",
"اللي يفهم بالعروض يعرف قيمته.",
"عرض قوي جداً.",
"سعر مغري حالياً.",
"من الآخر صفقة.",
"منتج يستاهل.",
"أفضل وقت للشراء."
]

HUMAN = [
"أنصح فيه بقوة.",
"يستاهل كل ريال.",
"تجربة ناجحة.",
"ما راح تندم.",
"يعجبك أكيد.",
"خيار موفق.",
"شي مضمون.",
"يفرق معك فعلياً.",
"صفقة ممتازة.",
"جربه وبتشوف."
]

CTA = [
"لا تنتظر لين يخلص.",
"استغل السعر الآن.",
"الكمية محدودة.",
"اطلبه اليوم.",
"عرض لفترة قصيرة.",
"سارع قبل يرتفع.",
"اللي يلحق يكسب.",
"لا تضيع الفرصة.",
"أفضل وقت الآن.",
"اطلبه قبل ينتهي."
]


# =========================
# ترجمة بسيطة
# =========================

WORDS = {
"pillow":"وسادة",
"shoes":"حذاء",
"phone":"جوال",
"bag":"شنطة",
"chair":"كرسي",
"table":"طاولة",
"sofa":"كنب",
"bed":"سرير",
"watch":"ساعة",
"headphone":"سماعة"
}


def translate_title(title):
    t = title.lower()
    for k,v in WORDS.items():
        if k in t:
            return v
    return title[:40]


# =========================
# قراءة المنتج
# =========================

def expand_url(url):
    try:
        return requests.get(url, timeout=10).url
    except:
        return url


def extract_asin(url):
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    return m.group(1) if m else None


def get_product(asin):

    url = f"https://www.amazon.sa/dp/{asin}"
    headers = {"User-Agent":"Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("#productTitle")
    title = title.text.strip() if title else "منتج مميز"

    price = soup.select_one(".a-price .a-offscreen")
    price = price.text.strip() if price else "غير متوفر"

    old_price = soup.select_one(".priceBlockStrikePriceString")
    if old_price:
        old_price = old_price.text.strip()

    else:
        # تقدير خصم وهمي
        try:
            num = float(re.findall(r'\d+', price)[0])
            old_price = str(int(num * 1.4)) + " ريال"
        except:
            old_price = ""

    img = soup.select_one("#landingImage")
    image = img["src"] if img else None

    return title, price, old_price, image, url


# =========================
# تحليل الخصم
# =========================

def discount_text(old_price, price):
    return f"بدل {old_price} صار {price}"


# =========================
# AI مجاني
# =========================

def generate_post(title, price, old_price, url):

    name = translate_title(title)

    s1 = random.choice(OPENINGS)

    s2 = f"{name} {discount_text(old_price, price)}."

    s3 = random.choice(HUMAN)
    s4 = random.choice(CTA)

    post = f"""
{s1} {s2} {s3} {s4}

🛍️ {title}

💰 السعر: {price}

🔗 {url}
"""
    return post


# =========================
# البوت
# =========================

@bot.message_handler(func=lambda m: True)
def handler(msg):

    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج.")
        return

    for u in urls:

        wait = bot.reply_to(msg, "⏳ جاري تجهيز العرض...")

        url = expand_url(u)
        asin = extract_asin(url)

        if not asin:
            bot.edit_message_text("الرابط غير صحيح.", msg.chat.id, wait.message_id)
            return

        try:
            title, price, old_price, image, product_url = get_product(asin)

            post = generate_post(title, price, old_price, product_url)

            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)

        except:
            bot.edit_message_text("ما قدرت أقرأ المنتج.", msg.chat.id, wait.message_id)


print("Bot Running...")
bot.infinity_polling()
