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


# =========================
# أدوات مساعدة
# =========================

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


# =========================
# قراءة المنتج من amazon.sa
# =========================

def get_product(asin):

    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
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


# =========================
# جمل سعودي احترافي
# =========================

OPENINGS = [
"بصراحة عرض خرافي.",
"فرصة قوية اليوم.",
"السعر حالياً مغري جداً.",
"أفضل صفقة تشوفها اليوم.",
"عرض ما يتكرر.",
"منتج يستاهل كل ريال.",
"أفضل وقت للشراء."
]

HUMAN = [
"أنصح فيه بقوة.",
"ما راح تندم عليه.",
"صفقة ناجحة فعلاً.",
"يعجبك أكيد.",
"يفرق معك فعلياً.",
"جربه وبتشوف."
]

CTA = [
"لا تنتظر لين يخلص.",
"استغل السعر قبل يتغير.",
"الكمية محدودة.",
"اطلبه اليوم.",
"عرض لفترة قصيرة.",
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

    post = f"""
{s1} {discount_text} {s2} {s3}

🛍️ {title}

💰 السعر: {price}

🔗 {affiliate_url}
"""

    return post


# =========================
# البوت
# =========================

@bot.message_handler(func=lambda m: True)
def handler(msg):

    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج من أمازون السعودية.")
        return

    for original_url in urls:

        wait = bot.reply_to(msg, "⏳ جاري تحليل المنتج...")

        expanded_url = expand_url(original_url)

        asin = extract_asin(expanded_url)

        if not asin:
            bot.edit_message_text("الرابط غير صحيح.", msg.chat.id, wait.message_id)
            return

        if is_posted(asin):
            bot.edit_message_text("⚠️ تم نشر هذا المنتج مسبقاً.", msg.chat.id, wait.message_id)
            return

        product = get_product(asin)

        if not product:
            bot.edit_message_text("ما قدرت أقرأ المنتج من أمازون.", msg.chat.id, wait.message_id)
            return

        title, price, old_price, image, discount_percent = product

        if discount_percent and discount_percent < 5:
            bot.edit_message_text("المنتج ما عليه خصم حقيقي حالياً.", msg.chat.id, wait.message_id)
            return

        post = generate_post(title, price, old_price, discount_percent, original_url)

        if image:
            bot.send_photo(msg.chat.id, image, caption=post)
        else:
            bot.send_message(msg.chat.id, post)

        mark_posted(asin)

        bot.delete_message(msg.chat.id, wait.message_id)


print("Bot Running...")
bot.infinity_polling()"فرصة قوية اليوم.",
"السعر حالياً مغري جداً.",
"أفضل صفقة تشوفها اليوم.",
"عرض ما يتكرر.",
"منتج يستاهل كل ريال.",
"اللي يفهم بالعروض يعرف قيمته.",
"أفضل وقت للشراء."
]

HUMAN = [
"أنصح فيه بقوة.",
"ما راح تندم عليه.",
"صفقة ناجحة فعلاً.",
"يعجبك أكيد.",
"خيار موفق جداً.",
"يفرق معك فعلياً.",
"جربه وبتشوف.",
"يستاهل التجربة."
]

CTA = [
"لا تنتظر لين يخلص.",
"استغل السعر قبل يتغير.",
"الكمية محدودة.",
"اطلبه اليوم.",
"عرض لفترة قصيرة.",
"سارع قبل يرتفع السعر.",
"لا تضيع الفرصة."
]


# =========================
# استخراج ASIN
# =========================

def extract_asin(url):
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    return m.group(1) if m else None


# =========================
# قراءة المنتج من amazon.sa
# =========================

def get_product(asin):

    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "ar-SA,ar;q=0.9"
    }

    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # اسم المنتج
    title = soup.select_one("#productTitle")
    title = title.text.strip() if title else None

    # السعر الحالي
    price_elem = soup.select_one(".a-price .a-offscreen")
    price = price_elem.text.strip() if price_elem else None

    # السعر القديم
    old_price_elem = soup.select_one(".priceBlockStrikePriceString")
    old_price = old_price_elem.text.strip() if old_price_elem else None

    # الصورة
    img = soup.select_one("#landingImage")
    image = img.get("src") if img else None

    if not title or not price:
        return None

    # حساب نسبة الخصم
    discount_percent = None

    try:
        if old_price:
            old_num = float(re.findall(r'\d+', old_price.replace(",", ""))[0])
            new_num = float(re.findall(r'\d+', price.replace(",", ""))[0])
            discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        discount_percent = None

    return title, price, old_price, image, discount_percent


# =========================
# توليد البوست
# =========================

def generate_post(title, price, old_price, discount_percent, affiliate_url):

    s1 = random.choice(OPENINGS)
    s2 = random.choice(HUMAN)
    s3 = random.choice(CTA)

    discount_text = ""

    if discount_percent and discount_percent > 5:
        discount_text = f"خصم {discount_percent}% 🔥 بدل {old_price} صار {price}."
    else:
        discount_text = f"بسعر {price}."

    post = f"""
{s1} {discount_text} {s2} {s3}

🛍️ {title}

💰 السعر: {price}

🔗 {affiliate_url}
"""

    return post


# =========================
# البوت
# =========================

@bot.message_handler(func=lambda m: True)
def handler(msg):

    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج من أمازون السعودية.")
        return

    for original_url in urls:

        wait = bot.reply_to(msg, "⏳ جاري تحليل المنتج...")

        asin = extract_asin(original_url)

        if not asin:
            bot.edit_message_text("الرابط غير صحيح.", msg.chat.id, wait.message_id)
            return

        if is_posted(asin):
            bot.edit_message_text("⚠️ تم نشر هذا المنتج مسبقاً.", msg.chat.id, wait.message_id)
            return

        try:
            product = get_product(asin)

            if not product:
                bot.edit_message_text("ما قدرت أقرأ المنتج من أمازون.", msg.chat.id, wait.message_id)
                return

            title, price, old_price, image, discount_percent = product

            # فلترة: لو ما فيه خصم واضح ما ننزل
            if discount_percent and discount_percent < 5:
                bot.edit_message_text("المنتج ما عليه خصم حقيقي حالياً.", msg.chat.id, wait.message_id)
                return

            post = generate_post(title, price, old_price, discount_percent, original_url)

            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            mark_posted(asin)

            bot.delete_message(msg.chat.id, wait.message_id)

        except Exception:
            bot.edit_message_text("صار خطأ أثناء قراءة المنتج.", msg.chat.id, wait.message_id)


print("Bot Running...")
bot.infinity_polling()# =========================
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
