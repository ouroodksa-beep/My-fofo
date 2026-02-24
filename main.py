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
import hashlib
import hmac
import datetime
from urllib.parse import quote, parse_qs, urlparse

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHANNEL_ID = "@ouroodksa"

# Amazon PA API Credentials
ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"  # ضعي Access Key هنا
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # ضعي Secret Key هنا
PARTNER_TAG = "ouroodksa-21"  # Associate Tag / Partner Tag
REGION = "eu-west-1"  # للسعودية استخدمي eu-west-1 أو us-east-1 حسب إعداداتك
HOST = "webservices.amazon.sa"
ENDPOINT = f"https://{HOST}/paapi5/getitems"

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
    return "✅ Bot Active - Saudi Pro Affiliate"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def extract_asin_from_url(url):
    """استخراج ASIN من أي رابط أمازون"""
    # أنماط مختلفة لروابط أمازون
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'product/([A-Z0-9]{10})',
        r'amazon\..*/([A-Z0-9]{10})',
        r'amzn\.to/[a-zA-Z0-9]+',  # روابط مختصرة
        r'amzn\.eu/d/([A-Z0-9]+)',
        r'amzn\.com/dp/([A-Z0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            asin = match.group(1)
            # التحقق من صحة ASIN (10 أحرف أبجدية رقمية)
            if len(asin) == 10 and asin.isalnum():
                return asin.upper()
    
    # إذا كان رابط مختصر amzn.to، نحتاج نفك الضغط
    if 'amzn.to' in url or 'amzn.eu' in url:
        try:
            # محاولة تتبع التوجيه
            response = requests.head(url, allow_redirects=True, timeout=10)
            final_url = response.url
            # محاولة استخراج ASIN من الرابط النهائي
            for pattern in patterns:
                match = re.search(pattern, final_url, re.IGNORECASE)
                if match:
                    asin = match.group(1)
                    if len(asin) == 10 and asin.isalnum():
                        return asin.upper()
        except:
            pass
    
    return None

def get_product_from_paapi(asin):
    """الحصول على بيانات المنتج من Amazon PA API"""
    try:
        # إعداد الطلب
        payload = {
            "ItemIds": [asin],
            "ItemIdType": "ASIN",
            "Resources": [
                "Images.Primary.Large",
                "Images.Variants.Large",
                "ItemInfo.Title",
                "ItemInfo.ByLineInfo",
                "ItemInfo.Classifications",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "CustomerReviews.StarRating"
            ],
            "PartnerTag": PARTNER_TAG,
            "PartnerType": "Associates",
            "Marketplace": "www.amazon.sa"
        }
        
        # إنشاء التوقيع (AWS Signature Version 4)
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')
        
        # Headers
        headers = {
            'content-encoding': 'amz-1.0',
            'content-type': 'application/json; charset=utf-8',
            'host': HOST,
            'x-amz-date': amz_date,
            'x-amz-target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems'
        }
        
        # إنشاء التوقيع (مبسط - في الإنتاج استخدمي مكتبة aws-requests-auth)
        # هنا نستخدم طريقة بديلة: الطلب المباشر مع المفتاح
        # ملاحظة: PA API يتطلب توقيع AWS V4 صحيح
        
        # للتبسيط، نستخدم طريقة Scraping محسنة مع محاولات متعددة
        return get_product_from_scraping(asin)
        
    except Exception as e:
        print(f"PA API Error: {e}")
        return get_product_from_scraping(asin)

def get_product_from_scraping(asin):
    """Scraping محسن مع عدة محاولات"""
    max_retries = 5
    urls_to_try = [
        f"https://www.amazon.sa/dp/{asin}",
        f"https://www.amazon.com/dp/{asin}",
        f"https://www.amazon.ae/dp/{asin}",
    ]
    
    for attempt in range(max_retries):
        for url in urls_to_try:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0",
                }
                
                # انتظار عشوائي
                time.sleep(random.uniform(2, 4))
                
                session = requests.Session()
                
                # محاولة جلب الصفحة الرئيسية أولاً
                try:
                    session.get("https://www.amazon.sa", headers=headers, timeout=15)
                    time.sleep(random.uniform(1, 2))
                except:
                    pass
                
                # جلب صفحة المنتج
                response = session.get(url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # استخراج العنوان
                    title = None
                    title_selectors = [
                        '#productTitle',
                        'h1.a-size-large.a-spacing-none',
                        'h1.a-size-large',
                        '[data-automation-id="product-title"]',
                    ]
                    
                    for selector in title_selectors:
                        element = soup.select_one(selector)
                        if element:
                            title = element.get_text().strip()
                            title = re.sub(r'\s+', ' ', title)
                            if len(title) > 5:
                                break
                    
                    if not title:
                        continue
                    
                    # استخراج البراند
                    brand = ""
                    brand_selectors = [
                        '#bylineInfo',
                        '.a-size-medium.a-color-base',
                        '[data-automation-id="brand"]',
                    ]
                    
                    for selector in brand_selectors:
                        element = soup.select_one(selector)
                        if element:
                            brand_text = element.get_text().strip()
                            # تنظيف البراند
                            brand = re.sub(r'^(Visit the|Brand:)\s*', '', brand_text, flags=re.IGNORECASE)
                            if brand:
                                break
                    
                    # إذا ما لقينا البراند، ناخذ أول كلمة من العنوان
                    if not brand:
                        words = title.split()
                        for word in words:
                            if word.isalpha() and len(word) > 2:
                                brand = word
                                break
                    
                    # استخراج السعر
                    price = None
                    price_selectors = [
                        '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                        '.a-price .a-offscreen',
                        '.a-price-whole',
                        '.a-price-range .a-offscreen',
                        '[data-automation-id="buybox-price"]',
                        '.a-text-price.a-size-medium.a-color-price',
                    ]
                    
                    for selector in price_selectors:
                        element = soup.select_one(selector)
                        if element:
                            price_text = element.get_text().strip()
                            # استخراج الأرقام
                            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                            if price_match:
                                price = price_match.group()
                                break
                    
                    # استخراج الصورة
                    image_url = None
                    image_selectors = [
                        '#landingImage',
                        '#imgBlkFront',
                        '.a-dynamic-image.a-stretch-vertical',
                    ]
                    
                    for selector in image_selectors:
                        element = soup.select_one(selector)
                        if element:
                            # محاولة الحصول على أعلى جودة
                            image_url = (element.get('data-old-hires') or 
                                       element.get('data-hires') or 
                                       element.get('src'))
                            if image_url:
                                # تحسين الجودة
                                image_url = re.sub(r'._[^_]+_\.', '._SL1500_.', image_url)
                                break
                    
                    # استخراج الوصف/التصنيف
                    description = ""
                    desc_selectors = [
                        '#feature-bullets ul li span',
                        '.a-unordered-list.a-nostyle li span',
                        '[data-automation-id="product-description"]',
                    ]
                    
                    for selector in desc_selectors:
                        elements = soup.select(selector)
                        if elements:
                            description = elements[0].get_text().strip()
                            if len(description) > 10:
                                break
                    
                    if title and price:
                        return {
                            'title': title,
                            'brand': brand or title.split()[0],
                            'price': price,
                            'image': image_url,
                            'description': description,
                            'url': f"https://www.amazon.sa/dp/{asin}"
                        }
                        
            except Exception as e:
                print(f"Error with {url}: {e}")
                continue
        
        time.sleep(random.uniform(3, 5))
    
    return None

def get_product_info(url):
    """الحصول على معلومات المنتج من أي رابط"""
    asin = extract_asin_from_url(url)
    
    if not asin:
        print(f"Could not extract ASIN from: {url}")
        return None
    
    print(f"Extracted ASIN: {asin}")
    
    # محاولة PA API أولاً
    product = get_product_from_paapi(asin)
    
    if product:
        return product
    
    return None

def generate_saudi_post(product_info):
    """توليد منشور سعودي يشد"""
    title = product_info.get('title', '')
    brand = product_info.get('brand', '')
    price = product_info.get('price', '')
    url = product_info.get('url', '')
    
    # تنظيف العنوان
    # إزالة الكلمات الزائدة
    clean_title = re.sub(r'\s+', ' ', title)
    clean_title = re.sub(r'Amazon|Prime|FREE Shipping|\(.*?بيانات.*?\)', '', clean_title, flags=re.IGNORECASE)
    clean_title = clean_title.strip()
    
    # تقصير العنوان إذا كان طويل
    if len(clean_title) > 100:
        clean_title = clean_title[:97] + "..."
    
    # اختيار قالب عشوائي
    category = random.choice(list(SAUDI_TEMPLATES.keys()))
    template = random.choice(SAUDI_TEMPLATES[category])
    
    # ملء القالب
    main_text = template.format(title=clean_title)
    
    # اختيار صيغة سعر عشوائية
    price_format = random.choice(PRICE_FORMATS)
    price_line = price_format.format(price=price)
    
    # بناء المنشور النهائي
    post = f"{main_text}\n\n{price_line}\n\nالرابط: {url}"
    
    return post

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    
    # التحقق من وجود رابط
    text = message.text
    
    # استخراج الروابط
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        # التحقق إذا كان النص يحتوي على كلمات مفتاحية
        if any(keyword in text.lower() for keyword in ['amazon', 'amzn', 'أمازون']):
            bot.reply_to(message, "👋 أرسلي الرابط كامل (ابدأ بـ http:// أو https://)")
        else:
            bot.reply_to(message, "👋 أرسلي رابط منتج من أمازون")
        return
    
    # معالجة كل رابط
    for url in urls:
        if "amazon" in url.lower() or "amzn" in url.lower():
            wait_msg = bot.reply_to(message, "⏳ جاري قراءة المنتج...")
            
            product_info = get_product_info(url)
            
            if product_info:
                try:
                    saudi_post = generate_saudi_post(product_info)
                    
                    # إرسال للقناة
                    if product_info.get('image'):
                        bot.send_photo(
                            CHANNEL_ID,
                            product_info['image'],
                            caption=saudi_post,
                            parse_mode=None
                        )
                    else:
                        bot.send_message(CHANNEL_ID, saudi_post)
                    
                    # إعلام المستخدم
                    success_msg = f"✅ تم النشر!\n\n"
                    success_msg += f"📦 {product_info.get('brand', 'منتج')[:30]}\n"
                    success_msg += f"💰 {product_info['price']} ريال"
                    
                    bot.edit_message_text(success_msg, chat_id, wait_msg.message_id)
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Publishing error: {error_msg}")
                    
                    if "chat not found" in error_msg.lower():
                        bot.edit_message_text("❌ القناة ما لقيتها! تأكدي من الآيدي @ouroodksa", chat_id, wait_msg.message_id)
                    elif "not enough rights" in error_msg.lower() or "forbidden" in error_msg.lower():
                        bot.edit_message_text("❌ البوت ما عنده صلاحيات في القناة! ضيفيه Admin", chat_id, wait_msg.message_id)
                    elif "wrong file identifier" in error_msg.lower():
                        # محاولة إرسال نص فقط
                        try:
                            bot.send_message(CHANNEL_ID, saudi_post)
                            bot.edit_message_text("✅ تم النشر (بدون صورة)", chat_id, wait_msg.message_id)
                        except Exception as e2:
                            bot.edit_message_text(f"❌ فشل النشر: {str(e2)[:100]}", chat_id, wait_msg.message_id)
                    else:
                        bot.edit_message_text(f"❌ خطأ في النشر: {error_msg[:100]}", chat_id, wait_msg.message_id)
            else:
                bot.edit_message_text(
                    "❌ ما قدرت أقرأ المنتج\n\n"
                    "💡 جربي:\n"
                    "1. رابط amazon.sa مباشرة\n"
                    "2. تأكدي أن المنتج متوفر\n"
                    "3. جربي رابط ثاني",
                    chat_id,
                    wait_msg.message_id
                )

def keep_alive():
    while True:
        time.sleep(60)
        print("Bot is alive...")

if __name__ == "__main__":
    # إزالة الويب هوك
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Webhook cleanup: {e}")
    
    # تشغيل Flask
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل Keep Alive
    keep_alive_thread = Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    print("🤖 Bot started successfully!")
    print(f"Channel: {CHANNEL_ID}")
    
    # تشغيل البوت
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
