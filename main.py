import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🎯 جمل SEO قوية جداً
# ===================================

OPENING_SENTENCES = [
    "🔥 عرض قوي اليوم – لا يفوتك السعر!",
    "💥 تخفيضات رهيبة الآن على أفضل المنتجات",
    "🚨 فرصة محدودة – السعر ممكن يتغير بأي لحظة",
    "🛍️ أفضل عرض اليوم في السعودية",
    "📉 خصم كبير لفترة محدودة",
    "🔥 السعر نازل بشكل مجنون اليوم",
    "💸 وفر فلوسك الآن مع هذا العرض",
    "⚡ عرض سريع – الكمية محدودة",
    "🎯 أفضل سعر حالياً على المنتج",
    "🏆 منتج مطلوب جداً وبسعر خرافي",
    "📦 المنتج الأكثر طلباً الآن",
    "🔥 عرض حصري – لا يتكرر كثير",
    "💥 صفقة قوية لعشاق العروض",
    "🛒 اشتري الآن قبل نفاد الكمية",
    "🚀 عرض اليوم فقط – الحق قبل ما يخلص",
    "📊 ترند السعودية حالياً",
    "💯 أفضل قيمة مقابل السعر",
    "🔥 عرض خاص لفترة محدودة جداً",
    "⚠️ المنتج بينفذ بسرعة",
    "🎁 فرصة ممتازة للشراء الآن",
    "🔥 خصم جامد لفترة محدودة",
    "💥 عرض ناري على المنتج اليوم",
    "🚨 لا تفوت أقوى تخفيض اليوم",
    "🛍️ صفقة اليوم في السعودية",
    "📉 أقل سعر حالياً في السوق",
    "🔥 السعر دا مش هتلاقيه تاني",
    "💸 وفر أكثر مع العرض ده",
    "⚡ أسرع عرض بيخلص بسرعة",
    "🎯 اختيار ممتاز بسعر مناسب",
    "🏆 منتج عليه إقبال عالي",
    "📦 الأكثر مبيعاً حالياً",
    "🔥 عرض لفترة قصيرة جداً",
    "💥 سعر خرافي مقارنة بالسوق",
    "🛒 فرصة شراء ممتازة الآن",
    "🚀 اطلب قبل ما السعر يعلى",
    "📊 من أفضل العروض حالياً",
    "💯 صفقة تستاهل الشراء",
    "🔥 عرض محدود جداً",
    "⚠️ الكمية قربت تخلص",
    "🎁 عرض خاص اليوم فقط",
]

# ===================================
# 🔄 ترجمة
# ===================================

TRANSLATION_DICT = {
    "iphone": "آيفون",
    "samsung": "سامسونج",
    "xiaomi": "شاومي",
    "huawei": "هواوي",
    "airpods": "سماعات آيربودز",
    "earbuds": "سماعات",
    "laptop": "لابتوب",
    "watch": "ساعة ذكية",
    "shoes": "حذاء",
    "perfume": "عطر",
    "bag": "شنطة",
    "camera": "كاميرا",
    "speaker": "سماعة",
    "tv": "تلفزيون",
    "men": "رجالي",
    "women": "نسائي",
    "black": "أسود",
    "white": "أبيض",
}

def translate_to_arabic(text):
    words = text.lower().split()
    return " ".join([TRANSLATION_DICT.get(w, w) for w in words])

# ===================================
# 🧠 اسم منتج بدون تقطيع
# ===================================

def smart_arabic_title(full_title):
    arabic_title = translate_to_arabic(full_title)
    
    if len(arabic_title) > 120:
        cut_point = arabic_title.rfind(' ', 80, 120)
        if cut_point == -1:
            cut_point = 120
        arabic_title = arabic_title[:cut_point] + "..."
    
    return arabic_title

# ===================================
# 🔧 أدوات
# ===================================

def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=15)
        return r.url
    except:
        return url

def is_saudi_amazon(url):
    return "amazon.sa" in url.lower()

def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'([A-Z0-9]{10})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def clean_price(price):
    try:
        num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
        return f"{int(num)} ريال سعودي"
    except:
        return price

# ===================================
# 📦 جلب المنتج
# ===================================

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ar-SA,ar;q=0.9"
    }

    r = requests.get(url, headers=headers, timeout=25)
    soup = BeautifulSoup(r.text, "html.parser")

    title_elem = soup.select_one("#productTitle")
    price_elem = soup.select_one(".a-price .a-offscreen")

    if not title_elem or not price_elem:
        return None

    title = smart_arabic_title(title_elem.text.strip())
    price = price_elem.text.strip()

    image = None
    img = soup.select_one("#landingImage")
    if img:
        image = img.get("src")

    return title, price, None, image, None

# ===================================
# ✨ بوست SEO احترافي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    opening = random.choice(OPENING_SENTENCES)
    clean_current = clean_price(price)

    lines = []
    lines.append(opening)
    lines.append("")
    
    lines.append("🛒 المنتج:")
    lines.append(product_name)
    lines.append("")
    
    lines.append(f"💰 السعر: {clean_current}")
    lines.append("")
    
    lines.append("📌 اطلب الآن بأفضل سعر في السعودية")
    lines.append("📦 شحن سريع | دفع آمن | منتج أصلي")
    lines.append("")
    
    lines.append("🔗 رابط الشراء:")
    lines.append(original_url)
    lines.append("")
    
    lines.append("#عروض #تخفيضات #amazon_السعودية #خصومات #تسوق #عروض_اليوم")

    return "\n".join(lines)

# ===================================
# 🤖 البوت
# ===================================

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج")
        return

    for original_url in urls:
        expanded = expand_url(original_url)

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط لازم يكون من amazon.sa")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج المنتج")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ فشل قراءة المنتج", msg.chat.id, wait.message_id)
            continue

        name, price, old, image, discount = product
        post = generate_post(name, price, old, discount, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)
        except:
            bot.send_message(msg.chat.id, post)

print("🤖 Bot Running...")
bot.infinity_polling()
