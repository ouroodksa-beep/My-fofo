import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import random
import re
import time
import json

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHANNEL_ID = "@ouroodksa"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة بيانات ضخمة: 300+ جملة سعودية تشد ---
SAUDI_TEMPLATES = {
    # تخيل وعجب (30 جملة)
    "imagine": [
        "تخيل يا عزيزي أن {title} يكون بسعر كذا! 🤯",
        "تخيل {title} بجودة عالية وبسعر ينافس! 😍",
        "تخيل {title} يغير روتينك اليومي! ✨",
        "تخيل {title} بين يديك الحين! 🔥",
        "تخيل {title} يوفر لك وقت وجهد! 💪",
        "تخيل {title} بسعر ما يتكرر! 😱",
        "تخيل {title} يجعل حياتك أسهل! 🎯",
        "تخيل {title} يفرق في يومك! ⚡",
        "تخيل {title} بجودة تفوق السعر! 💯",
        "تخيل {title} يكون لك بسعر خاص! 🎁",
        "تخيل {title} يصير من أساسياتك! 🌟",
        "تخيل {title} يريحك من متاعب كثيرة! 😌",
        "تخيل {title} يجمع الجودة والسعر! 💎",
        "تخيل {title} يبهر كل من يشوفه! 🤩",
        "تخيل {title} يكون سر تميزك! 👑",
        "تخيل {title} يغير نظرتك للمنتجات! 🔄",
        "تخيل {title} يعطيك قيمة حقيقية! 💰",
        "تخيل {title} يكون استثمارك الأفضل! 📈",
        "تخيل {title} يسعدك كل يوم! 😊",
        "تخيل {title} يكون حلولك المثالية! ✅",
        "تخيل {title} يجعلك تتباهى! 😎",
        "تخيل {title} يصير حديث الجميع! 💬",
        "تخيل {title} يعطيك راحة بال! 🧘",
        "تخيل {title} يكون عندك الحين! 🚀",
        "تخيل {title} يسهل عليك حياتك! 🌈",
        "تخيل {title} يجمع الفخامة والعملية! 🏆",
        "تخيل {title} يكون خيارك الذكي! 🧠",
        "تخيل {title} يفرحك ويوفر لك! 🎉",
        "تخيل {title} يكون نعمة في بيتك! 🏠",
        "تخيل {title} يصير جزء من نجاحك! ⭐",
    ],
    
    # أبطالنا وأصحاب (30 جملة)
    "heroes": [
        "أبطالنا أصحاب الذوق {title} وصل! 🦸‍♂️",
        "أصحاب الجودة {title} بين أيديكم! 💪",
        "أبطال التوفير {title} ينتظركم! 🏆",
        "أصحاب الذوق الرفيع {title} لكم! 👌",
        "أبطالنا اللي يعرفون القيمة {title}! ⭐",
        "أصحاب الاختيار الذكي {title} وصل! 🧠",
        "أبطال الجودة {title} بين يديكم! 🔥",
        "أصحاب التميز {title} لكم بسعر خاص! 💎",
        "أبطالنا اللي ما يقبلون الغلط {title}! ✅",
        "أصحاب الفخامة {title} يناديكم! 👑",
        "أبطال التسوق {title} جاهز لكم! 🛍️",
        "أصحاب الذوق {title} ما راح يتفوتهم! 😍",
        "أبطالنا أصحاب القرار {title} وصل! 🎯",
        "أصحاب الجودة العالية {title} لكم! 🌟",
        "أبطال التوفير الذكي {title} ينتظر! 💰",
        "أصحاب الاختيار الصح {title} بين يديكم! 👍",
        "أبطالنا اللي يعرفون الصح {title}! 🏅",
        "أصحاب الذوق المميز {title} لكم بس! ✨",
        "أبطال الجودة والسعر {title} وصل أخيراً! 🚀",
        "أصحاب التميز {title} ما راح يندمون! 💯",
        "أبطالنا أصحاب النظرة {title} يناديكم! 👀",
        "أصحاب الفخامة بسعر معقول {title}! 💸",
        "أبطال التجربة {title} جاهز للطلب! 📦",
        "أصحاب الذوق الراقي {title} لكم! 🥂",
        "أبطالنا اللي ما يفوتهم شي {title}! 🔍",
        "أصحاب الجودة الفائقة {title} بين أيديكم! 🏆",
        "أبطال الاختيار {title} ينتظر قراركم! ⏰",
        "أصحاب التميز والأناقة {title} لكم! 🎩",
        "أبطالنا أصحاب القرار الصح {title}! 🎯",
        "أصحاب الذوق العالي {title} ما راح يتأخرون! ⚡",
    ],
    
    # هلا بالزين (30 جملة)
    "hala": [
        "هلا بالزين كله {title} وصل! 🤍",
        "هلا بالجودة {title} بين يديك! 👋",
        "هلا بالتميز {title} يناديك! ✨",
        "هلا بالفخامة {title} بسعر ينافس! 💎",
        "هلا بالأناقة {title} وصل أخيراً! 🌟",
        "هلا بالذوق {title} ينتظرك! 😍",
        "هلا بالجودة العالية {title}! 🔥",
        "هلا بالاختيار الصح {title} بين يديك! ✅",
        "هلا بالتميز والأصالة {title}! 🏆",
        "هلا بالزين {title} بجودة تفوق! 💯",
        "هلا بالفخامة السعرية {title}! 💰",
        "هلا بالذوق الرفيع {title} وصل! 👌",
        "هلا بالجودة اللي تدوم {title}! ⏳",
        "هلا بالتميز اللي يفرق {title}! 🎯",
        "هلا بالزين كله {title} بسعر خاص! 🎁",
        "هلا بالأناقة العملية {title}! 👑",
        "هلا بالجودة اللي تستاهل {title}! 💪",
        "هلا بالذوق المميز {title} يناديك! 🎨",
        "هلا بالتميز اللي يبهر {title}! 🤩",
        "هلا بالزين {title} بين يديك الحين! 🚀",
        "هلا بالفخامة بأقل سعر {title}! 🔥",
        "هلا بالجودة اللي تفرح {title}! 😊",
        "هلا بالذوق اللي يميزك {title}! 🌟",
        "هلا بالتميز اللي يستاهل {title}! ⭐",
        "هلا بالزين كله {title} ما يتفوت! ⚡",
        "هلا بالأناقة اليومية {title}! ✨",
        "هلا بالجودة اللي تثبت {title}! 📈",
        "هلا بالذوق الراقي {title} وصل! 🥂",
        "هلا بالتميز اللي يدوم {title}! 🏅",
        "هلا بالزين {title} ينتظر طلبك! 📦",
    ],
    
    # آخر حبة/كمية (30 جملة)
    "last_piece": [
        "🔴 آخر حبة بالمخزون {title}!",
        "🔴 الكمية نفذت تقريباً {title}!",
        "🔴 باقي قطعتين {title} بس!",
        "🔴 نفذ من المستودع {title}!",
        "🔴 آخر فرصة {title} ما تتكرر!",
        "🔴 الكمية محدودة جداً {title}!",
        "🔴 على وشك النفاذ {title}!",
        "🔴 باقي عدد قليل {title}!",
        "🔴 آخر 3 قطع {title}!",
        "🔴 نفذ من معظم الأماكن {title}!",
        "🔴 الكمية تنتهي اليوم {title}!",
        "🔴 آخر فرصة للحصول على {title}!",
        "🔴 باقي حبتين بس {title}!",
        "🔴 نفذ الكمية الأولى {title}!",
        "🔴 الطلب عالي على {title}!",
        "🔴 آخر 5 قطع {title}!",
        "🔴 الكمية محدودة {title} بشدة!",
        "🔴 على وشك الانتهاء {title}!",
        "🔴 باقي القليل {title}!",
        "🔴 آخر حبة {title} لا تفوت!",
        "🔴 نفذ من المخزن الرئيسي {title}!",
        "🔴 الكمية شارفت على الانتهاء {title}!",
        "🔴 باقي 4 قطع {title}!",
        "🔴 آخر فرصة حقيقية {title}!",
        "🔴 الطلبات فاقت التوقع {title}!",
        "🔴 باقي حبة واحدة {title}!",
        "🔴 نفذ بسرعة {title}!",
        "🔴 الكمية الأخيرة {title}!",
        "🔴 على وشك النفاذ التام {title}!",
        "🔴 باقي عدد محدود جداً {title}!",
    ],
    
    # سرعة وعجلة (30 جملة)
    "hurry": [
        "🏃‍♂️ سارع قبل ما ينتهي {title}!",
        "⏰ الوقت ينفد {title} ينتظر!",
        "⚡ بسرعة {title} بنفذ!",
        "🚨 عاجل {title} كمية محدودة!",
        "🔥 سارع {title} بسعر خاص!",
        "⏳ لا تتأخر {title} ينتهي!",
        "⚠️ تنبيه {title} على وشك النفاذ!",
        "🎯 الآن أو أبداً {title}!",
        "🚀 سارع بالحجز {title}!",
        "⏰ الفرصة لا تتكرر {title}!",
        "⚡ بسرعة البرق {title}!",
        "🔴 عاجل جداً {title}!",
        "🏃‍♀️ اركض قبل ما ينتهي {title}!",
        "⏳ الوقت ضيق {title}!",
        "🚨 تنبيه عاجل {title}!",
        "⚡ فرصة ثمينة {title}!",
        "🔥 سارع بالطلب {title}!",
        "⏰ لا تفوت {title}!",
        "⚠️ احذر النفاذ {title}!",
        "🎯 القرار الآن {title}!",
        "🚀 بسرعة قبل الغير {title}!",
        "⏳ العد التنازلي بدأ {title}!",
        "🔴 عاجل الكمية تنتهي {title}!",
        "⚡ لا تنتظر {title}!",
        "🏃‍♂️ سارع الفرصة تفلت {title}!",
        "⏰ الوقت لا ينتظر {title}!",
        "🚨 تنبيه أخير {title}!",
        "⚡ بسرعة الريح {title}!",
        "🔥 سارع قبل الندم {title}!",
        "⏳ الفرصة الأخيرة {title}!",
    ],
    
    # جودة وقيمة (30 جملة)
    "quality": [
        "💎 جودة تفوق التوقع {title}!",
        "⭐ قيمة حقيقية {title} يستاهل!",
        "🏆 الأفضل في فئته {title}!",
        "💯 جودة 100% {title} مضمون!",
        "🎯 الاختيار الصح {title}!",
        "💪 جودة تدوم {title}!",
        "🌟 تميز واضح {title}!",
        "✅ جودة مثبتة {title}!",
        "💎 فخامة بسعر معقول {title}!",
        "⭐ يستاهل كل ريال {title}!",
        "🏅 جودة عالمية {title}!",
        "💯 ثقة وجودة {title}!",
        "🎯 القيمة الحقيقية {title}!",
        "💪 متانة تدوم {title}!",
        "🌟 يتفوق على المنافسين {title}!",
        "✅ اختيار مضمون {title}!",
        "💎 جودة تبهر {title}!",
        "⭐ سعر ينافس وجودة تفوق {title}!",
        "🏆 الأفضل على الإطلاق {title}!",
        "💯 رضا تام {title}!",
        "🎯 جودة تستحق {title}!",
        "💪 يتحمل الاستخدام اليومي {title}!",
        "🌟 يفرق عن الباقي {title}!",
        "✅ جودة لا تتنازل {title}!",
        "💎 استثمار ذكي {title}!",
        "⭐ يستاهل التجربة {title}!",
        "🏅 جودة تليق بك {title}!",
        "💯 تميز في كل تفصيلة {title}!",
        "🎯 الأفضلية واضحة {title}!",
        "💪 جودة تثبت نفسها {title}!",
    ],
    
    # من القلب (30 جملة)
    "heart": [
        "❤️ من القلب {title} يستاهل!",
        "💕 صدقوني {title} يفرق!",
        "💖 جربته وانبهرت {title}!",
        "💗 والله العظيم {title} رهيب!",
        "💝 من تجربتي {title} يستاهل!",
        "💓 صدقني ما راح تندم {title}!",
        "💞 والله يا جماعة {title} يجنن!",
        "💕 من قلبي أنصح فيه {title}!",
        "❤️‍🔥 حبيته من أول نظرة {title}!",
        "💖 صراحة {title} يستاهل كل hype!",
        "💗 والله العظيم يفرح {title}!",
        "💝 مجرب ومتأكد {title}!",
        "💕 من القلب {title} يستاهل الدعم!",
        "❤️ يا جماعة {title} يستاهل التجربة!",
        "💖 والله نعمة {title}!",
        "💗 صدقوني القيمة {title}!",
        "💞 من القلب {title} يستاهل الشراء!",
        "💕 والله يا عزيزي {title} رهيب!",
        "❤️‍🔥 جربته بنفسي {title}!",
        "💖 صراحة ما توقعت {title} يكون كذا!",
        "💗 والله يستاهل {title}!",
        "💝 من القلب {title} يفرح!",
        "💕 يا جماعة الخير {title}!",
        "❤️ والله العظيم {title} يجنن!",
        "💖 صدقني {title} يستاهل!",
        "💗 من تجربة شخصية {title}!",
        "💞 والله نعمة من الله {title}!",
        "💕 يا أخوان {title} يستاهل!",
        "❤️‍🔥 صراحة {title} يبهر!",
        "💖 من القلب {title} يستاهل كل ريال!",
    ],
    
    # مفاجآت وعروض (30 جملة)
    "surprise": [
        "🎉 مفاجأة سارة {title} وصل!",
        "🎁 عرض خاص {title} ينتظرك!",
        "🎊 مفاجأة العام {title}!",
        "🎈 خبر حلو {title} متاح!",
        "✨ مفاجأة تفرح {title}!",
        "🎉 عرض محدود {title}!",
        "🎁 مفاجأة ما تتوقعها {title}!",
        "🎊 خبر يفرح {title} وصل!",
        "🎈 مفاجأة سعيدة {title}!",
        "✨ عرض ذهبي {title}!",
        "🎉 مفاجأة تستاهل {title}!",
        "🎁 خبر جميل {title} بين يديك!",
        "🎊 مفاجأة العمر {title}!",
        "🎈 عرض لا يُفوت {title}!",
        "✨ مفاجأة تبهر {title}!",
        "🎉 خبر سار {title} ينتظرك!",
        "🎁 مفاجأة تستحق {title}!",
        "🎊 عرض مميز {title}!",
        "🎈 مفاجأة تفرح القلب {title}!",
        "✨ خبر رائع {title} وصل!",
        "🎉 مفاجأة تستاهل الاهتمام {title}!",
        "🎁 عرض حصري {title}!",
        "🎊 مفاجأة تبهر الجميع {title}!",
        "🎈 خبر يستاهل {title}!",
        "✨ مفاجأة تستحق التجربة {title}!",
        "🎉 عرض خاص جداً {title}!",
        "🎁 مفاجأة تفرح {title}!",
        "🎊 خبر ممتاز {title} بين يديك!",
        "🎈 مفاجأة تليق بك {title}!",
        "✨ عرض رابح {title}!",
    ],
    
    # سؤال وتفاعل (30 جملة)
    "question": [
        "وش رايكم في {title}؟ 🤔",
        "من جرب {title} يعطينا رأيه؟ 👇",
        "تستاهل {title} التجربة؟ 🤷‍♀️",
        "وش تنتظر عشان {title}؟ ⏰",
        "من يبي {title} يدخل بسرعة! 🏃‍♂️",
        "وش السالفة مع {title}؟ 🔍",
        "تعرفون {title}؟ جربتوه؟ 🤔",
        "وش رأيكم يستاهل {title}؟ 💭",
        "من يبي يوفر يجرب {title}! 💰",
        "وش تنتظرون {title} ينتهي؟ 😱",
        "جربتوا {title} ولا لا؟ 🤷‍♂️",
        "وش السر في {title}؟ 🧐",
        "من يعرف {title} يتكلم! 🗣️",
        "وش رايكم بالسعر {title}؟ 💸",
        "تستاهل {title} الضجة؟ 🔥",
        "وش تنتظر عشان تطلب {title}؟ ⏳",
        "من جرب {title} يشاركنا! 👥",
        "وش الفرق مع {title}؟ 🎯",
        "تبي توفر {title} هو الحل! 💡",
        "وش رأيكم في جودة {title}؟ ⭐",
        "من يبي يتميز يختار {title}! 👑",
        "وش السالفة {title} ينفذ بسرعة؟ 🚨",
        "جربت {title} ولا تنتظر؟ 🤔",
        "وش تنتظر {title} يختفي؟ 😰",
        "من يعطي رأيه الصريح في {title}؟ 💬",
        "وش رايكم {title} يستاهل؟ 🤷‍♀️",
        "تبي الجودة {title} موجود! ✅",
        "وش السر {title} يريح الجميع؟ 😌",
        "من يبي يستفيد يجرب {title}! 📈",
        "وش تنتظر {title} ينتهي العرض؟ ⏰",
    ],
}

# --- صيغ السعر المتنوعة (10 صيغ) ---
PRICE_FORMATS = [
    "🔥 بـ {price} ريال فقط!",
    "💰 السعر: {price} ريال",
    "⚡ {price} ريال بس!",
    "💸 فقط بـ {price} ريال",
    "🎯 {price} ريال ويوصلك!",
    "🔥 {price} ريال شامل التوصيل!",
    "💰 بـ {price} ريال تستاهل!",
    "⚡ سعر خاص: {price} ريال",
    "💸 {price} ريال ولا أروع!",
    "🎯 بـ {price} ريال بس!",
]

# --- User Agents ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

@app.route('/')
def home():
    return "✅ Bot Active - Saudi Style Affiliate"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def extract_asin(url):
    """استخراج ASIN من رابط أمازون"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'amzn\.eu/d/([A-Z0-9]+)',
        r'amzn\.to/[a-zA-Z0-9]+',
        r'amazon\..*/([A-Z0-9]{10})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1) if len(match.group(1)) == 10 else match.group(0)
    return None

def get_high_quality_image(soup):
    """استخراج صورة عالية الجودة"""
    try:
        img = soup.select_one('#landingImage')
        if img:
            dynamic_data = img.get('data-a-dynamic-image')
            if dynamic_data:
                images_dict = json.loads(dynamic_data)
                largest_url = max(images_dict.keys(), key=lambda x: images_dict[x][0] * images_dict[x][1])
                return largest_url
            
            image_url = img.get('data-old-hires') or img.get('src')
            if image_url:
                return re.sub(r'._[^_]+_\.', '._SL1500_.', image_url)
    except:
        pass
    return None

def get_product_description(soup, brand):
    """استخراج وصف المنتج بالعربي"""
    # قائمة الكلمات العربية الشائعة للمنتجات
    arabic_keywords = {
        "حذاء": ["shoe", "حذاء", "boot", "sneaker", "running"],
        "ساعة": ["watch", "ساعة", "clock", "smartwatch"],
        "حقيبة": ["bag", "حقيبة", "backpack", "suitcase"],
        "هاتف": ["phone", "هاتف", "mobile", "smartphone", "iphone"],
        "لابتوب": ["laptop", "لابتوب", "notebook", "computer", "macbook"],
        "سماعات": ["headphone", "سماعات", "earphone", "airpods", "buds"],
        "كاميرا": ["camera", "كاميرا", "canon", "nikon", "gopro"],
        "تابلت": ["tablet", "تابلت", "ipad"],
        "شاحن": ["charger", "شاحن", "cable", "power bank"],
        "ماوس": ["mouse", "ماوس"],
        "كيبورد": ["keyboard", "كيبورد"],
        "شاشة": ["screen", "شاشة", "monitor", "display"],
        "طقم": ["set", "طقم", "kit", "collection"],
        "فستان": ["dress", "فستان", "gown"],
        "قميص": ["shirt", "قميص", "blouse"],
        "بنطلون": ["pants", "بنطلون", "trousers", "jeans"],
        "عطر": ["perfume", "عطر", "fragrance", "cologne"],
        "سجادة": ["carpet", "سجادة", "rug", "mat"],
        "مكواة": ["iron", "مكواة", "steamer"],
        "خلاط": ["blender", "خلاط", "mixer"],
        "مقلاة": ["pan", "مقلاة", "skillet"],
        "قدر": ["pot", "قدر", "cooker"],
        "مكيف": ["ac", "مكيف", "conditioner", "cooler"],
        "مروحة": ["fan", "مروحة"],
        "مكتبة": ["bookshelf", "مكتبة", "shelf"],
        "كنبة": ["sofa", "كنبة", "couch"],
        "سرير": ["bed", "سرير", "mattress"],
        "مخدة": ["pillow", "مخدة", "cushion"],
        "لحاف": ["blanket", "لحاف", "comforter"],
        "مناشف": ["towel", "مناشف", "bath"],
        "صابون": ["soap", "صابون", "shampoo", "body wash"],
        "كريم": ["cream", "كريم", "lotion", "moisturizer"],
        "مكياج": ["makeup", "مكياج", "cosmetic", "lipstick"],
        "فرشاة": ["brush", "فرشاة", "comb"],
        "نظارات": ["glasses", "نظارات", "sunglasses"],
        "ساعة يد": ["wristwatch", "ساعة يد"],
        "محفظة": ["wallet", "محفظة", "purse"],
        "حزام": ["belt", "حزام"],
        "ربطة عنق": ["tie", "ربطة عنق"],
        "جاكيت": ["jacket", "جاكيت", "coat"],
        "جزمة": ["boot", "جزمة", "boots"],
        "شبشب": ["slipper", "شبشب", "sandal"],
        "جورب": ["sock", "جورب", "socks"],
        "قبعة": ["hat", "قبعة", "cap"],
        "وشاح": ["scarf", "وشاح"],
        "قفازات": ["glove", "قفازات", "gloves"],
        "مظلة": ["umbrella", "مظلة"],
        "حقيبة سفر": ["luggage", "حقيبة سفر", "suitcase"],
        "صندوق": ["box", "صندوق", "storage"],
        "منظم": ["organizer", "منظم", "storage box"],
        "سلة": ["basket", "سلة", "hamper"],
        "ممسحة": ["mop", "ممسحة", "broom"],
        "مكنسة": ["vacuum", "مكنسة", "cleaner"],
        "غسالة": ["washer", "غسالة", "washing machine"],
        "نشافة": ["dryer", "نشافة"],
        "ثلاجة": ["fridge", "ثلاجة", "refrigerator"],
        "فرن": ["oven", "فرن", "microwave"],
        "غلاية": ["kettle", "غلاية", "boiler"],
        "توستر": ["toaster", "توستر"],
        "قهوة": ["coffee", "قهوة", "espresso", "machine"],
        "مطحنة": ["grinder", "مطحنة"],
        "طباخ": ["stove", "طباخ", "cooktop"],
        "شواية": ["grill", "شواية", "bbq"],
        "قلاية": ["fryer", "قلاية", "air fryer"],
        "محمصة": ["roaster", "محمصة"],
        "عصارة": ["juicer", "عصارة"],
        "قطاعة": ["slicer", "قطاعة", "cutter"],
        " weighing": ["scale", "ميزان", "weighing"],
        "ترمومتر": ["thermometer", "ترمومتر"],
        "ميزان حرارة": ["thermometer", "ميزان حرارة"],
        "مكبر صوت": ["speaker", "مكبر صوت", "bluetooth speaker"],
        "مايك": ["microphone", "مايك", "mic"],
        "كاميرا مراقبة": ["camera", "كاميرا مراقبة", "security"],
        "جرس": ["bell", "جرس", "doorbell"],
        "إضاءة": ["light", "إضاءة", "lamp", "led"],
        "ثريا": ["chandelier", "ثريا"],
        "ستاند": ["stand", "ستاند", "holder"],
        "مرآة": ["mirror", "مرآة"],
        "ساعة حائط": ["wall clock", "ساعة حائط"],
        "براويز": ["frame", "براويز", "frames"],
        "ستارة": ["curtain", "ستارة", "blinds"],
        "مفرش": ["sheet", "مفرش", "bedsheet"],
        "مخدة طبية": ["pillow", "مخدة طبية", "orthopedic"],
        "وسادة": ["cushion", "وسادة", "pillow"],
        "بطانية": ["blanket", "بطانية", "throw"],
        "سجادة صلاة": ["prayer mat", "سجادة صلاة"],
        "مصحف": ["quran", "مصحف"],
        "سبحة": ["prayer beads", "سبحة", "misbaha"],
        "ماء زمزم": ["zamzam", "ماء زمزم"],
        "عسل": ["honey", "عسل"],
        "تمور": ["dates", "تمور", "date"],
        "قهوة عربية": ["arabic coffee", "قهوة عربية"],
        "شاي": ["tea", "شاي"],
        "زيت": ["oil", "زيت", "olive oil"],
        "سمن": ["ghee", "سمن", "butter"],
        "أرز": ["rice", "أرز"],
        "معكرونة": ["pasta", "معكرونة", "noodles"],
        "بهارات": ["spices", "بهارات", "spice"],
        "ملح": ["salt", "ملح"],
        "سكر": ["sugar", "سكر"],
        "دقيق": ["flour", "دقيق"],
        "بيض": ["egg", "بيض"],
        "حليب": ["milk", "حليب"],
        "جبن": ["cheese", "جبن"],
        "زبادي": ["yogurt", "زبادي"],
        "لحوم": ["meat", "لحوم", "beef", "chicken"],
        "سمك": ["fish", "سمك", "seafood"],
        "خضروات": ["vegetables", "خضروات", "greens"],
        "فواكه": ["fruits", "فواكه", "fruit"],
        "مكسرات": ["nuts", "مكسرات", "almonds", "cashews"],
        "شوكولاتة": ["chocolate", "شوكولاتة", "candy"],
        "بسكويت": ["biscuit", "بسكويت", "cookies"],
        "كيك": ["cake", "كيك"],
        "مربى": ["jam", "مربى", "spread"],
        "عصير": ["juice", "عصير"],
        "مياه": ["water", "مياه", "mineral water"],
        "مشروبات غازية": ["soda", "مشروبات غازية", "soft drinks"],
        "طاقية": ["cap", "طاقية", "hat"],
        "عباية": ["abaya", "عباية"],
        "شماغ": ["shmagh", "شماغ", "ghutra"],
        "ثوب": ["thobe", "ثوب", "dishdasha"],
        "بيجاما": ["pajama", "بيجاما", "sleepwear"],
        "لانجري": ["lingerie", "لانجري", "underwear"],
        "مايوه": ["swimsuit", "مايوه", "swimwear"],
        "بدلة رياضية": ["tracksuit", "بدلة رياضية", "sportswear"],
        "فنيلة": ["undershirt", "فنيلة", "vest"],
        "كلوت": ["underwear", "كلوت", "briefs"],
        "جوارب": ["socks", "جوارب"],
        "شرابات": ["stockings", "شرابات", "tights"],
        "لاصق طبي": ["bandage", "لاصق طبي", "plaster"],
        "مطهر": ["sanitizer", "مطهر", "disinfectant"],
        "كمامات": ["mask", "كمامات", "face mask"],
        "قفازات طبية": ["gloves", "قفازات طبية", "medical gloves"],
        "مضاد حيوي": ["antibiotic", "مضاد حيوي"],
        "فيتامينات": ["vitamins", "فيتامينات", "supplements"],
        "مكملات غذائية": ["supplements", "مكملات غذائية"],
        "زيت زيتون": ["olive oil", "زيت زيتون"],
        "زيت نباتي": ["vegetable oil", "زيت نباتي"],
        "خل": ["vinegar", "خل"],
        "صلصة": ["sauce", "صلصة", "ketchup", "mayonnaise"],
        "خردل": ["mustard", "خردل"],
        "كاتشب": ["ketchup", "كاتشب"],
        "مايونيز": ["mayonnaise", "مايونيز"],
        "تونة": ["tuna", "تونة"],
        "معلبات": ["canned", "معلبات", "canned food"],
        "مجمدات": ["frozen", "مجمدات", "frozen food"],
        "مخبوزات": ["bakery", "مخبوزات", "bread"],
        "كرواسان": ["croissant", "كرواسان"],
        "دونات": ["donut", "دونات"],
        "كب كيك": ["cupcake", "كب كيك"],
        "براونيز": ["brownies", "براونيز"],
        "تشيز كيك": ["cheesecake", "تشيز كيك"],
        "آيس كريم": ["ice cream", "آيس كريم"],
        "حلويات": ["sweets", "حلويات", "desserts"],
        "تمريه": ["date paste", "تمريه"],
        "معمول": ["maamoul", "معمول"],
        "بقلاوة": ["baklava", "بقلاوة"],
        "كنافة": ["kunafa", "كنافة"],
        "قطايف": ["qatayef", "قطايف"],
        "رز بلبن": ["rice pudding", "رز بلبن"],
        "أشطة": ["cream", "أشطة", "eshta"],
        "جبن كريمي": ["cream cheese", "جبن كريمي"],
        "لبنة": ["labneh", "لبنة"],
        "زبدة": ["butter", "زبدة"],
        "قشطة": ["qishta", "قشطة"],
        "تمر هندي": ["tamarind", "تمر هندي"],
        "عرق سوس": ["licorice", "عرق سوس"],
        "قرفة": ["cinnamon", "قرفة"],
        "هيل": ["cardamom", "هيل"],
        "زعفران": ["saffron", "زعفران"],
        "قرنفل": ["cloves", "قرنفل"],
        "فلفل أسود": ["black pepper", "فلفل أسود"],
        "كمون": ["cumin", "كمون"],
        "كزبرة": ["coriander", "كزبرة"],
        "زنجبيل": ["ginger", "زنجبيل"],
        "ثوم": ["garlic", "ثوم"],
        "بصل": ["onion", "بصل"],
        "طماطم": ["tomato", "طماطم"],
        "خيار": ["cucumber", "خيار"],
        "جزر": ["carrot", "جزر"],
        "بطاطس": ["potato", "بطاطس"],
        "بصل أخضر": ["green onion", "بصل أخضر"],
        "فلفل": ["pepper", "فلفل"],
        "فلفل حار": ["chili", "فلفل حار"],
        "ليمون": ["lemon", "ليمون"],
        "برتقال": ["orange", "برتقال"],
        "تفاح": ["apple", "تفاح"],
        "موز": ["banana", "موز"],
        "عنب": ["grape", "عنب"],
        "بطيخ": ["watermelon", "بطيخ"],
        "شمام": ["melon", "شمام"],
        "خوخ": ["peach", "خوخ"],
        "مشمش": ["apricot", "مشمش"],
        "تين": ["fig", "تين"],
        "رمان": ["pomegranate", "رمان"],
        "فراولة": ["strawberry", "فراولة"],
        "توت": ["berry", "توت", "blueberry", "raspberry"],
        "أناناس": ["pineapple", "أناناس"],
        "مانجو": ["mango", "مانجو"],
        "كيوي": ["kiwi", "كيوي"],
        "أفوكادو": ["avocado", "أفوكادو"],
        "جوز": ["walnut", "جوز"],
        "لوز": ["almond", "لوز"],
        "فستق": ["pistachio", "فستق"],
        "كاجو": ["cashew", "كاجو"],
        "بندق": ["hazelnut", "بندق"],
        "صنوبر": ["pine nut", "صنوبر"],
        "لب": ["seed", "لب", "pumpkin seeds"],
        "زبيب": ["raisin", "زبيب"],
        "مشمش مجفف": ["dried apricot", "مشمش مجفف"],
        "تين مجفف": ["dried fig", "تين مجفف"],
        "برقوق مجفف": ["prune", "برقوق مجفف"],
        "مانجو مجفف": ["dried mango", "مانجو مجفف"],
        "لحم مجفف": ["jerky", "لحم مجفف", "biltong"],
        "سمك مجفف": ["dried fish", "سمك مجفف"],
        "روبيان": ["shrimp", "روبيان", "prawn"],
        "كاليماري": ["calamari", "كاليماري", "squid"],
        "محار": ["oyster", "محار", "mussels"],
        "كركند": ["lobster", "كركند"],
        "سرطان": ["crab", "سرطان"],
        "سلطعون": ["crab", "سلطعون"],
    }
    
    # البحث في العنوان عن الكلمات المفتاحية
    title_lower = soup.get_text().lower() if soup else ""
    
    for arabic_word, keywords in arabic_keywords.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return arabic_word
    
    # إذا ما لقينا، نرجع وصف عام
    return "منتج مميز"

def get_amazon_info(url):
    """استخراج معلومات المنتج"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
            
            time.sleep(random.uniform(1, 2))
            session = requests.Session()
            session.get("https://www.amazon.sa", headers=headers, timeout=10)
            time.sleep(random.uniform(0.5, 1))
            
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # العنوان الأصلي
            original_title = None
            title_selectors = ['#productTitle', 'h1.a-size-large']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    original_title = element.get_text().strip()
                    original_title = re.sub(r'\s+', ' ', original_title)
                    break
            
            if not original_title:
                continue
            
            # استخراج البراند (أول كلمة إنجليزية)
            words = original_title.split()
            brand = words[0] if words else original_title
            
            # استخراج الوصف بالعربي
            description = get_product_description(soup, brand)
            
            # السعر
            price = None
            price_selectors = [
                '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                '.a-price .a-offscreen',
                '.a-price-whole',
            ]
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = price_match.group()
                        break
            
            # الصورة
            image_url = get_high_quality_image(soup)
            
            if brand and price and description:
                return {
                    'brand': brand,
                    'description': description,
                    'price': price,
                    'image': image_url,
                    'url': url
                }
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(random.uniform(2, 3))
    
    return None

def generate_saudi_post(product_info):
    """توليد منشور سعودي يشد"""
    brand = product_info['brand']
    description = product_info['description']
    price = product_info['price']
    url = product_info['url']
    
    # بناء عنوان المنتج الكامل: براند + وصف عربي
    full_title = f"{brand} {description}"
    
    # اختيار قالب عشوائي
    category = random.choice(list(SAUDI_TEMPLATES.keys()))
    template = random.choice(SAUDI_TEMPLATES[category])
    
    # ملء القالب بالعنوان الكامل
    main_text = template.format(title=full_title)
    
    # اختيار صيغة سعر عشوائية
    price_format = random.choice(PRICE_FORMATS)
    price_line = price_format.format(price=price)
    
    # بناء المنشور النهائي
    post = f"{main_text}\n\n{price_line}\n\nالرابط: {url}"
    
    return post

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if "amazon" in message.text.lower() or "amzn" in message.text.lower():
        wait_msg = bot.reply_to(message, "⏳ جاري التحضير...")
        
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
        
        if not urls:
            bot.edit_message_text("❌ ما لقيت رابط!", chat_id, wait_msg.message_id)
            return
        
        url = urls[0]
        product_info = get_amazon_info(url)
        
        if product_info:
            saudi_post = generate_saudi_post(product_info)
            
            try:
                if product_info.get('image'):
                    bot.send_photo(
                        CHANNEL_ID,
                        product_info['image'],
                        caption=saudi_post,
                        parse_mode=None
                    )
                else:
                    bot.send_message(CHANNEL_ID, saudi_post)
                
                bot.edit_message_text(
                    f"✅ تم النشر!\n\n{product_info['brand']} {product_info['description']}\n{product_info['price']} ريال",
                    chat_id,
                    wait_msg.message_id
                )
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error: {error_msg}")
                
                if "chat not found" in error_msg:
                    bot.edit_message_text("❌ القناة ما لقيتها! تأكدي من الآيدي", chat_id, wait_msg.message_id)
                elif "not enough rights" in error_msg:
                    bot.edit_message_text("❌ البوت ما عنده صلاحيات! ضيفيه Admin", chat_id, wait_msg.message_id)
                elif "wrong file identifier" in error_msg:
                    try:
                        bot.send_message(CHANNEL_ID, saudi_post)
                        bot.edit_message_text("✅ تم النشر (بدون صورة)", chat_id, wait_msg.message_id)
                    except:
                        bot.edit_message_text("❌ فشل النشر نهائياً", chat_id, wait_msg.message_id)
                else:
                    bot.edit_message_text(f"❌ خطأ: {error_msg[:100]}", chat_id, wait_msg.message_id)
        else:
            bot.edit_message_text(
                "❌ ما قدرت أقرأ المنتج\n\nجربي رابط amazon.sa مباشرة",
                chat_id,
                wait_msg.message_id
            )
    else:
        bot.reply_to(message, "👋 أرسلي رابط أمازون")

def keep_alive():
    while True:
        time.sleep(60)
        print("Bot alive...")

if __name__ == "__main__":
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot started...")
    bot.infinity_polling()
