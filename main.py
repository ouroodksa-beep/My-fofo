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
# 🎯 جمل تسويقية سعودية SEO + ريتش عالي
# ===================================

OPENING_SENTENCES = [
# 🔥 جذب قوي + كلمات بحث
"🔥 عرض قوي اليوم في السعودية | خصم رهيب لا يفوت 🚀",
"💥 أفضل سعر حالياً في السوق السعودي | فرصة محدودة ⏳",
"🚨 تخفيضات اليوم وصلت | لا يفوتك العرض 🔥",
"🎯 أقوى عروض أمازون السعودية الآن | السعر نازل 📉",
"💸 وفر فلوسك مع هذا العرض الخرافي اليوم 💥",
"🏆 من أكثر المنتجات طلباً في السعودية حالياً 🔥",
"📦 منتج ترند في السعودية | الكمية محدودة 🚨",
"⚡ عرض سريع ومحدود | الحق قبل ينتهي ⏳",
"🔥 خصم كبير اليوم فقط | فرصة تسوق ذكية 💡",
"💯 صفقة قوية تستحق الشراء الآن 🚀",

# ⏰ استعجال + رفع CTR
"⏳ العرض لفترة محدودة جداً | سارع قبل النفاذ 🚨",
"⚠️ الكمية محدودة والطلب عالي | لا تنتظر 🔥",
"🚀 ينتهي قريب | اغتنم الفرصة الآن 💥",
"📉 السعر الحالي نادر جداً | ممكن يرتفع بأي وقت ⚡",
"⏰ فرصة مؤقتة | القرار الآن يفرق 💯",
"🔥 العرض يختفي بسرعة | خلك سابق الكل 🚀",
"🚨 متوفر لفترة قصيرة فقط | لا تفوت 👀",
"💥 آخر فرصة تقريباً للحصول عليه بالسعر هذا ⏳",

# 💥 تحفيز شراء + SEO
"🛍️ اختيار ذكي لمحبي الجودة والسعر المناسب 💯",
"💡 منتج عملي وسعر منافس في السوق السعودي 🇸🇦",
"🔥 يجمع بين السعر القوي والجودة العالية 👌",
"💯 مناسب للاستخدام اليومي وبسعر ممتاز 💸",
"📊 من أفضل الخيارات حالياً حسب الطلب 🔝",
"🏅 تقييمات عالية وتجربة مستخدم ممتازة ⭐",
"💥 قيمة مقابل سعر رهيبة 🔥",
"📈 من المنتجات الأكثر بحثاً حالياً 👀",

# 🇸🇦 طابع سعودي + انتشار
"🇸🇦 عرض مميز داخل السعودية فقط 🔥",
"📦 شحن سريع داخل السعودية 🚚",
"💚 مناسب للسوق السعودي وبسعر قوي 💯",
"🔥 منتشر بقوة في السعودية حالياً 🚀",
"📢 الكل يتكلم عنه هالفترة 🔥",
"🏆 من ترندات التسوق في السعودية الآن 💥",
"📈 طلب عالي جداً داخل المملكة 🚨",

# 😱 FOMO + ترند
"🔥 المنتج هذا عليه طلب غير طبيعي 🚀",
"📦 ينفذ ويرجع بسرعة | الحق عليه ⏳",
"🚨 من المنتجات اللي تخلص بسرعة 🔥",
"👀 واضح إنه ترند بقوة هالأيام 💥",
"💯 الكل قاعد يطلبه حالياً 🔝",
"⚡ لا يفوتك قبل ما يختفي من السوق 🚨",
"🔥 فرصة شراء ممتازة قبل الزحمة 💸",
"📉 سعر حالي صعب يتكرر 💥",

# 💪 CTA قوي
"🚀 اطلبه الآن واستفد من الخصم 🔥",
"💥 قرار موفق لو أخذته اليوم 💯",
"📦 جاهز للطلب مباشرة وبسعر ممتاز 👌",
"🔥 لا تتردد | السعر يستاهل 👀",
"💸 استثمار ذكي مقابل السعر 🔥",
"⚡ خذ الخطوة الآن قبل ما يفوتك ⏳",
"💯 اختيار مناسب بسعر مغري 🔥",
"🎯 لا تضيع الفرصة الحالية 🚨",
]

# ===================================
# 🔄 قاموس ترجمة المنتجات للعربي
# ===================================

TRANSLATION_DICT = {
"iphone": "آيفون",
"samsung": "سامسونج",
"xiaomi": "شاومي",
"huawei": "هواوي",
"airpods": "سماعات آيربودز",
"earbuds": "سماعات أذن",
"headphones": "سماعات رأس",
"laptop": "لابتوب",
"macbook": "ماك بوك",
"tablet": "تابلت",
"ipad": "آيباد",
"watch": "ساعة ذكية",
"smartwatch": "ساعة ذكية",
"charger": "شاحن",
"cable": "كيبل",
"power bank": "باور بانك",
"battery": "بطارية",
"screen": "شاشة",
"monitor": "شاشة عرض",
"keyboard": "كيبورد",
"mouse": "ماوس",
"camera": "كاميرا",
"speaker": "سماعة",
"tv": "تلفزيون",
"television": "تلفزيون",
"router": "راوتر",
"modem": "مودم",
"shoes": "حذاء",
"sneakers": "حذاء رياضي",
"bag": "شنطة",
"perfume": "عطر",
"watch": "ساعة",
"smart": "ذكي",
"wireless": "لاسلكي",
"bluetooth": "بلوتوث",
"original": "أصلي",
"new": "جديد",
"pro": "برو",
"max": "ماكس",
"plus": "بلس",
"ultra": "ألترا",
"black": "أسود",
"white": "أبيض",
}

def translate_to_arabic(text):
    text_lower = text.lower()
    words = text_lower.split()
    translated_words = []

    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            translated_words.append(word)

    return " ".join(translated_words)

def smart_arabic_title(full_title):
    words = full_title.split()
    short_title = " ".join(words[:12])
    return translate_to_arabic(short_title)

# ===================================
# 💰 تنظيف السعر
# ===================================

def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num = int(float(nums[0].replace(",", "")))
            return f"{num} ريال سعودي"
    except:
        pass
    return price_text

# ===================================
# ✨ التوليد النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    opening = random.choice(OPENING_SENTENCES)

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None

    lines = [opening]
    lines.append("")
    lines.append(f"🛒 {product_name}")
    lines.append("")

    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الحين: {clean_current} 🔥 (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean_current}")

    lines.append("")
    lines.append(f"🔗 {original_url}")

    return "\n".join(lines)

print("🤖 البوت جاهز 🚀")
