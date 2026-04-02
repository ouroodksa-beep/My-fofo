import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🧠 تحديد نوع المنتج (AI بسيط)
# ===================================

def detect_product_type(title):
    t = title.lower()

    if any(x in t for x in ["iphone","samsung","headphone","earbuds","laptop","keyboard","mouse","usb"]):
        return "electronics"

    if any(x in t for x in ["shirt","pants","dress","jacket","hoodie","shoes","nike","adidas"]):
        return "fashion"

    if any(x in t for x in ["cream","serum","makeup","lipstick","lotion"]):
        return "beauty"

    if any(x in t for x in ["pillow","blanket","kitchen","pan","mattress","sofa"]):
        return "home"

    if any(x in t for x in ["milk","coffee","tea","chocolate","snack"]):
        return "food"

    return "general"

# ===================================
# 🇸🇦 Hooks حسب النوع
# ===================================

STYLE_HOOKS = {
    "electronics": [
        ("🔥 عرض تقني على", "أداء قوي وسعر كسر 🔥"),
        ("⚡ صفقة إلكترونيات", "فرصة لعشاق التقنية 💯"),
    ],
    "fashion": [
        ("✨ ستايل جديد على", "أناقة بسعر رهيب 😎"),
        ("🔥 عرض أزياء على", "لبسك بيصير مختلف 👌"),
    ],
    "beauty": [
        ("💄 عرض جمال على", "اهتمي بنفسك ✨"),
        ("✨ منتج عناية على", "نتيجته واضحة 🔥"),
    ],
    "home": [
        ("🏠 عرض للبيت على", "راحة وجودة 👌"),
        ("✨ منتج منزلي", "فرق واضح 💯"),
    ],
    "food": [
        ("🥤 عرض غذائي على", "طعم رهيب 😋"),
        ("🍫 لقطة على", "خزن قبل يخلص 🔥"),
    ],
    "general": [
        ("🔥 عرض قوي على", "سعر ما يتكرر 🔥"),
        ("💥 لقطة اليوم على", "فرصة لا تفوت 👌"),
    ]
}

# ===================================
# 🎯 CTA ذكي
# ===================================

CTA_SMART = [
    "👉 الحق العرض",
    "👉 خذها قبل تخلص",
    "👉 اطلبه الحين",
    "👉 لا يفوتك",
    "👉 إذا ناوي هذا وقتك",
    "👉 السعر ما يطول",
]

# ===================================
# 🔗 فك الروابط المختصرة
# ===================================

def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

# ===================================
# 🔧 أدوات
# ===================================

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

def clean_price(text):
    nums = re.findall(r'[\d,.]+', text)
    if nums:
        return f"{int(float(nums[0].replace(',', '')))} ريال"
    return text

# ===================================
# 🖼️ صورة HD
# ===================================

def get_high_quality_image(soup):
    img = soup.select_one("#landingImage")

    if not img:
        return None

    image = img.get("data-old-hires")

    if not image:
        dynamic = img.get("data-a-dynamic-image")
        if dynamic:
            try:
                data = json.loads(dynamic)
                image = max(data.keys(), key=lambda x: data[x][0] * data[x][1])
            except:
                pass

    if not image:
        image = img.get("src")

    if image:
        image = re.sub(r'\._.*_\.', '.', image)
        if "_SL" not in image:
            image = image.replace(".jpg", "_SL1500_.jpg")

    return image

# ===================================
# 📦 جلب المنتج
# ===================================

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ar-SA,ar;q=0.9"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("#productTitle")
    price = soup.select_one(".a-price .a-offscreen")
    old_price = soup.select_one(".a-text-price .a-offscreen")

    if not title or not price:
        return None

    image = get_high_quality_image(soup)

    return (
        title.text.strip(),
        price.text.strip(),
        old_price.text.strip() if old_price else None,
        image
    )

# ===================================
# ✍️ توليد البوست
# ===================================

def generate_post(title, price, old_price, url):
    product_type = detect_product_type(title)

    hook1, hook2 = random.choice(STYLE_HOOKS.get(product_type, STYLE_HOOKS["general"]))

    product_name = title[:50]

    lines = []

    lines.append(f"{hook1} {product_name}")
    lines.append(hook2)
    lines.append("")

    lines.append(product_name)

    current = clean_price(price)
    old = clean_price(old_price) if old_price else None

    if old:
        try:
            old_n = float(re.findall(r'[\d.]+', old)[0])
            new_n = float(re.findall(r'[\d.]+', current)[0])

            if old_n > new_n:
                discount = int(((old_n - new_n) / old_n) * 100)
                if discount >= 15:
                    lines.append(f"❌ {old}")
                    lines.append(f"✅ {current} 🔥")
                else:
                    lines.append(f"💰 {current}")
            else:
                lines.append(f"💰 {current}")
        except:
            lines.append(f"💰 {current}")
    else:
        lines.append(f"💰 {current}")

    # CTA
    lines.append(random.choice(CTA_SMART))

    # رابط
    lines.append(f"🔗 {url}")

    return "\n".join(lines)

# ===================================
# 🤖 البوت
# ===================================

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط امازون")
        return

    for short_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        expanded = expand_url(short_url)

        if "amazon.sa" not in expanded:
            bot.edit_message_text("❌ الرابط لازم amazon.sa", msg.chat.id, wait.message_id)
            continue

        asin = extract_asin(expanded)

        if not asin:
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)
            continue

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ فشل التحليل", msg.chat.id, wait.message_id)
            continue

        title, price, old_price, image = product

        post = generate_post(title, price, old_price, short_url)

        if image:
            bot.send_photo(msg.chat.id, image, caption=post)
        else:
            bot.send_message(msg.chat.id, post)

        bot.delete_message(msg.chat.id, wait.message_id)

print("🔥 بوت احترافي شغال + CTA ذكي + AI")
bot.infinity_polling()
