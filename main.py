import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json

# ================================
# 🎯 إعدادات البوت
# ================================
TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"  # ضع توكن البوت هنا
bot = telebot.TeleBot(TOKEN)

# ================================
# 🔥 جمل افتتاحية
# ================================
OPENING_SENTENCES = [
    "هذا من الأشياء اللي تستاهل تجربها 👍",
    "بصراحة صفقة حلوة بهالسعر 🔥",
    "شيء بسيط لكنه يفرق معك 👌",
    "منتج عملي ويخدمك كثير 🙌",
    "خيار حلو للي يحب الجودة 💰",
]

# ================================
# 💣 تيك توك هوكس
# ================================
TIKTOK_HOOKS = [
    "😳 محد كان يتوقع السعر كذا!",
    "🚨 لا تشتري قبل ما تشوف هذا!",
    "💣 هذا المنتج عامل ضجة!",
    "🔥 الناس تشتريه بشكل مجنون!",
    "👀 شوف ليه الكل يتكلم عنه!",
]

# ================================
# 📦 هوكس حسب الفئة
# ================================
CATEGORY_HOOKS = {
    "electronics": ["📱 عرض قوي على الأجهزة!", "🔥 خيار تقني ممتاز!"],
    "fashion": ["👕 ستايل حلو!", "🔥 إضافة لإطلالتك!"],
    "perfume": ["🌸 عطر يلفت!", "🔥 ريحة فخمة!"],
    "home": ["🏠 شيء مفيد للبيت!", "✨ يسهل حياتك!"],
    "default": ["🔥 شوف هذا العرض!", "👀 لا يفوتك!"]
}

# ================================
# 🧠 تحليل الفئة
# ================================
def detect_category(product_name):
    name = product_name.lower()

    if any(x in name for x in ["iphone","سامسونج","سماعات","bluetooth","لابتوب"]):
        return "electronics"
    if any(x in name for x in ["حذاء","تيشيرت","شنطة"]):
        return "fashion"
    if any(x in name for x in ["عطر","perfume","عود"]):
        return "perfume"
    if any(x in name for x in ["مطبخ","خلاط","كرسي"]):
        return "home"

    return "default"

# ================================
# 💰 تحليل السعر
# ================================
def detect_style(price):
    try:
        num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
        if num < 50:
            return "cheap"
        elif num > 1000:
            return "premium"
    except:
        pass
    return "normal"

# ================================
# ✂️ اختصار الاسم
# ================================
def smart_title(title):
    words = title.split()
    important = ["آيفون","سامسونج","سماعات","لابتوب","عطر"]
    keep = [w for w in words if any(k in w for k in important)]

    if len(keep) < 2:
        keep = words[:4]

    return " ".join(dict.fromkeys(keep))[:50]

# ================================
# 🔥 هوك ذكي
# ================================
def get_hook(name, price):
    cat = detect_category(name)
    style = detect_style(price)

    hooks = CATEGORY_HOOKS.get(cat, []) + TIKTOK_HOOKS

    if style == "cheap":
        hooks += ["💸 سعر خرافي!", "😳 رخيص مرة!"]
    elif style == "premium":
        hooks += ["💎 منتج فاخر!", "👑 مستوى عالي!"]

    return random.choice(hooks)

# ================================
# 💵 تنظيف السعر
# ================================
def clean_price(price):
    try:
        num = int(float(re.findall(r'[\d,.]+', price)[0].replace(",", "")))
        return f"{num} ريال سعودي"
    except:
        return price

# ================================
# 🖼️ تنظيف رابط الصورة
# ================================
def clean_image_url(url):
    url = re.sub(r'_SX\d+_', '_', url)
    url = re.sub(r'_SY\d+_', '_', url)
    if "_SL" not in url:
        url = url.replace(".jpg", "_SL1500_.jpg")
    return url

def get_image(soup):
    img = soup.select_one("#landingImage")
    if img:
        image = img.get("data-old-hires")
        if not image:
            data = img.get("data-a-dynamic-image")
            if data:
                try:
                    img_dict = json.loads(data)
                    image = list(img_dict.keys())[0]
                except:
                    pass
        if not image:
            image = img.get("src")
        return clean_image_url(image)
    return None

# ================================
# 📦 جلب بيانات المنتج
# ================================
def get_product(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("#productTitle")
    price = soup.select_one(".a-price .a-offscreen")

    if not title or not price:
        return None

    image = get_image(soup)
    return title.text.strip(), price.text.strip(), image

# ================================
# ✨ إنشاء البوست النهائي
# ================================
def generate_post(name, price, url):
    hook = get_hook(name, price)
    opening = random.choice(OPENING_SENTENCES)
    short = smart_title(name)

    return f"""{hook}
{opening}

🛒 {short}

💰 السعر: {clean_price(price)}

🔗 {url}
"""

# ================================
# 🤖 تشغيل البوت
# ================================
@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط امازون")
        return

    for url in urls:
        wait = bot.reply_to(msg, "⏳ جاري التحليل...")
        product = get_product(url)
        if not product:
            bot.send_message(msg.chat.id, "❌ فشل التحليل")
            continue

        name, price, image = product
        post = generate_post(name, price, url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except:
            bot.send_message(msg.chat.id, post)

print("🤖 البوت يعمل...")
bot.infinity_polling()
