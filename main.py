import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import random
import re
import time

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاموس التصنيفات ---
CATEGORIES = {
    "shoe": "حذاء", "shoes": "حذاء", "sneaker": "حذاء رياضي", "sneakers": "حذاء رياضي",
    "boot": "جزمة", "boots": "جزمة", "sandal": "صندل", "sandals": "صندل",
    "slipper": "شبشب", "slippers": "شبشب", "footwear": "أحذية",
    "pant": "بنطلون", "pants": "بنطلون", "trouser": "بنطلون", "trousers": "بنطلون",
    "jean": "جينز", "jeans": "جينز", "short": "شورت", "shorts": "شورت",
    "shirt": "قميص", "shirts": "قميص", "t-shirt": "تيشيرت", "tshirt": "تيشيرت",
    "dress": "فستان", "dresses": "فستان", "skirt": "تنورة", "skirts": "تنورة",
    "jacket": "جاكيت", "jackets": "جاكيت", "coat": "معطف", "coats": "معطف",
    "sweater": "سترة", "sweaters": "سترة", "hoodie": "هودي", "hoodies": "هودي",
    "sweatpant": "بنطلون رياضي", "sweatpants": "بنطلون رياضي", "fleece": "فليس",
    "sock": "جورب", "socks": "جورب", "underwear": "ملابس داخلية",
    "pajama": "بيجاما", "pajamas": "بيجاما", "robe": "روب", "robes": "روب",
    "scarf": "وشاح", "shaw": "شال", "glove": "قفاز", "gloves": "قفاز",
    "hat": "قبعة", "hats": "قبعة", "cap": "طاقية", "caps": "طاقية",
    "belt": "حزام", "belts": "حزام", "tie": "ربطة عنق", "ties": "ربطة عنق",
    "suit": "بدلة", "suits": "بدلة", "abaya": "عباية", "thobe": "ثوب",
    
    "watch": "ساعة", "watches": "ساعة", "jewelry": "مجوهرات",
    "ring": "خاتم", "necklace": "عقد", "bracelet": "سوار", "earring": "حلق",
    "sunglass": "نظارة شمسية", "sunglasses": "نظارة شمسية",
    "wallet": "محفظة", "purse": "شنطة يد", "bag": "حقيبة", "backpack": "شنطة ظهر",
    
    "phone": "هاتف", "smartphone": "هاتف ذكي", "iphone": "آيفون",
    "laptop": "لابتوب", "computer": "كمبيوتر", "tablet": "تابلت", "ipad": "آيباد",
    "headphone": "سماعة", "earphone": "سماعة أذن", "earbud": "سماعة لاسلكية",
    "speaker": "مكبر صوت", "charger": "شاحن", "cable": "كيبل",
    "power bank": "باور بانك", "battery": "بطارية", "mouse": "ماوس",
    "keyboard": "كيبورد", "monitor": "شاشة", "camera": "كاميرا",
    
    "furniture": "أثاث", "sofa": "كنبة", "bed": "سرير", "mattress": "مرتبة",
    "pillow": "مخدة", "blanket": "بطانية", "carpet": "سجادة", "lamp": "مصباح",
    "pot": "قدر", "pan": "مقلاة", "blender": "خلاط", "oven": "فرن",
    "fridge": "ثلاجة", "washer": "غسالة", "vacuum": "مكنسة", "fan": "مروحة",
    "ac": "مكيف", "heater": "دفاية",
    
    "perfume": "عطر", "cream": "كريم", "shampoo": "شامبو", "soap": "صابون",
    "makeup": "مكياج", "lipstick": "أحمر شفاه",
    
    "toy": "لعبة", "doll": "دمية", "stroller": "عربة أطفال", "diaper": "حفاض",
    "book": "كتاب", "pen": "قلم", "notebook": "دفتر",
}

# --- 200+ جملة سعودية مرتبطة بالمنتج ---
TEMPLATES = {
    # أحذية (30 جملة)
    "shoe": [
        "هلا بالزين كله {title} وصل! 🤍👟",
        "تخيل يا عزيزي {title} يكون بسعر كذا! 🤯👞",
        "أبطالنا أصحاب الذوق {title} بين يديك! 🦸‍♂️👟",
        "🔴 آخر حبة بالمخزون {title}! 👠",
        "🏃‍♂️ سارع قبل ما ينتهي {title}! 👟⚡",
        "💎 جودة تفوق التوقع {title}! 👞✨",
        "❤️ من القلب {title} يستاهل كل ريال! 💰👟",
        "🎉 مفاجأة سارة {title} وصل! 🎁👞",
        "وش رايكم في {title}؟ يستاهل ولا لا؟ 🤔👟",
        "صدقوني {title} يفرق في مشيتك! 💪👞",
        "والله العظيم {title} رهيب! 😍👟",
        "من تجربتي {title} يستاهل! ⭐👞",
        "بسرعة! {title} بنفذ بسرعة البرق! ⚡👟",
        "جودة عالمية {title} بسعر محلي! 🌍👞",
        "اللي يبي يتميز يلبس {title}! 😎👟",
        "راحة لا توصف مع {title}! ☁️👞",
        "أناقة وراحة في {title}! 💎👟",
        "ما شاء الله {title} فخم! 👌👞",
        "يستاهل الضجة {title}! 🔥👟",
        "من أحسن الأحذية اللي جربتها {title}! 👏👞",
        "السعر خرافي على {title}! 🤩👟",
        "لا يفوتك {title} بهالسعر! 🏃‍♂️👞",
        "نعمة من الله {title}! 🙏👟",
        "يستاهل التجربة {title}! 💯👞",
        "أنصح فيه بقوة {title}! 💪👟",
        "ما راح تندم على {title}! ✅👞",
        "فرصة ذهبية {title}! 🌟👟",
        "الأناقة تبدأ من {title}! ✨👞",
        "تميز مع {title}! 🏆👟",
        "الجودة تتكلم عن {title}! 💎👞",
    ],
    
    # ملابس (30 جملة)
    "clothes": [
        "هلا بالزين كله {title} وصل! 🤍👕",
        "أبطالنا أصحاب الذوق {title} بين يديك! 🦸‍♂️👔",
        "تخيل {title} بجودة عالية وبسعر ينافس! 🤯👖",
        "🔴 آخر حبة بالمخزون {title}! 👗",
        "🏃‍♂️ سارع قبل ما ينتهي {title}! 👔⚡",
        "💎 جودة تفوق التوقع {title}! 👕✨",
        "❤️ من القلب {title} يستاهل! 💰👖",
        "🎉 مفاجأة سارة {title} وصل! 🎁👔",
        "أناقة لا توصف مع {title}! 💎👗",
        "والله {title} يجنن! 😍👕",
        "من تجربتي {title} يستاهل! ⭐👖",
        "بسرعة! {title} بنفذ! ⚡👔",
        "جودة عالمية {title}! 🌍👗",
        "اللي يبي يتميز يلبس {title}! 😎👕",
        "راحة وأناقة مع {title}! ☁️👖",
        "ما شاء الله {title} فخم! 👌👔",
        "يستاهل الضجة {title}! 🔥👗",
        "السعر خرافي على {title}! 🤩👕",
        "لا يفوتك {title}! 🏃‍♂️👖",
        "نعمة من الله {title}! 🙏👔",
        "يستاهل التجربة {title}! 💯👗",
        "أنصح فيه بقوة {title}! 💪👕",
        "ما راح تندم على {title}! ✅👖",
        "فرصة ذهبية {title}! 🌟👔",
        "الأناقة تبدأ من {title}! ✨👗",
        "تميز مع {title}! 🏆👕",
        "راحة يومية مع {title}! 😌👖",
        "جودة تدوم مع {title}! ⏳👔",
        "أفضل اختيار {title}! 🥇👗",
        "الكل يسأل عن {title}! 💬👕",
    ],
    
    # إلكترونيات (30 جملة)
    "electronics": [
        "🚀 تكنولوجيا المستقبل {title} وصلت! 📱",
        "💡 ذكاء اصطناعي في {title}! 🤖",
        "⚡ سرعة خرافية مع {title}! 🚀",
        "🔋 بطارية تدوم مع {title}! ⏳",
        "📱 الجيل الجديد {title} بين يديك! ✨",
        "🎧 صوت نقي مع {title}! 🎵",
        "💻 إنتاجية أعلى مع {title}! 📈",
        "📸 لحظات لا تُنسى مع {title}! 🌟",
        "🎮 أداء احترافي مع {title}! 🏆",
        "🔌 شحن سريع مع {title}! ⚡",
        "📡 اتصال مستقر مع {title}! 📶",
        "🛡️ حماية كاملة مع {title}! 🔒",
        "🌐 عالم رقمي مع {title}! 🌍",
        "🎯 دقة عالية مع {title}! 🎯",
        "🎬 تجربة سينمائية مع {title}! 🍿",
        "🎤 صوت احترافي مع {title}! 🎙️",
        "💾 مساحة كبيرة مع {title}! 💽",
        "🔄 سرعة استجابة مع {title}! ⚡",
        "📞 تواصل سهل مع {title}! 📲",
        "🎨 ألوان حية مع {title}! 🌈",
        "🔊 صوت محيطي مع {title}! 🔊",
        "📡 تغطية شاملة مع {title}! 📶",
        "⚙️ أداء ممتاز مع {title}! 🔧",
        "🔋 طاقة تدوم مع {title}! 🔋",
        "🚀 سرعة فائقة مع {title}! 🚀",
        "💡 إضاءة ذكية مع {title}! 💡",
        "🎧 عزل مثالي مع {title}! 🔇",
        "📱 تصميم أنيق مع {title}! ✨",
        "🎮 تحكم سلس مع {title}! 🎮",
        "🔌 توصيل سهل مع {title}! 🔌",
    ],
    
    # منزل ومطبخ (30 جملة)
    "home": [
        "🏠 بيت أحلى مع {title}! 🏡",
        "🍳 مطبخ مثالي مع {title}! 👨‍🍳",
        "🛋️ راحة تامة مع {title}! ☁️",
        "🛏️ نوم هادئ مع {title}! 😴",
        "🍽️ سفرة فاخرة مع {title}! 🥘",
        "🧹 نظافة سهلة مع {title}! ✨",
        "🌡️ جو مثالي مع {title}! 🌤️",
        "🪴 ديكور راقي مع {title}! 🎨",
        "🛁 استرخاء تام مع {title}! 🧖‍♀️",
        "🍰 حلويات لذيذة مع {title}! 🧁",
        "☕ صباح أجمل مع {title}! 🌅",
        "🍳 إفطار شهي مع {title}! 🥞",
        "🧺 غسيل سهل مع {title}! 👕",
        "🍽️ عشاء عائلي مع {title}! 🍛",
        "🛋️ جلسة مريحة مع {title}! 🛋️",
        "🌙 ليلة هادئة مع {title}! 🌃",
        "🍵 شاي ساخن مع {title}! 🫖",
        "🧹 تنظيف سريع مع {title}! 🧽",
        "🍲 طبخ سهل مع {title}! 🥘",
        "🏡 بيت نظيف مع {title}! 🧼",
        "🛏️ راحة نفسية مع {title}! 🧘‍♀️",
        "🍽️ تقديم أنيق مع {title}! 🍴",
        "🌸 رائحة جميلة مع {title}! 🌺",
        "🧊 تبريد مثالي مع {title}! ❄️",
        "🔥 دفء ممتع مع {title}! 🔥",
        "💡 إضاءة مثالية مع {title}! 💡",
        "🪟 ستارة أنيقة مع {title}! 🪟",
        "🛁 حمام فاخر مع {title}! 🚿",
        "🍳 أدوات احترافية مع {title}! 🔪",
        "🏠 سعادة عائلية مع {title}! 👨‍👩‍👧‍👦",
    ],
    
    # جمال وعناية (30 جملة)
    "beauty": [
        "💄 جمال طبيعي مع {title}! 💋",
        "✨ بشرة نضرة مع {title}! 🌟",
        "🌸 عطر فاخر مع {title}! 🌺",
        "💇‍♀️ شعر صحي مع {title}! 💆‍♀️",
        "🧴 نعومة فائقة مع {title}! 🦢",
        "💅 أظافر جميلة مع {title}! 💅",
        "👁️ نظرة جذابة مع {title}! 👁️",
        "🌹 رائحة ساحرة مع {title}! 🌹",
        "🧖‍♀️ سبا منزلي مع {title}! 🛁",
        "💆‍♂️ استرخاء تام مع {title}! 🧘‍♂️",
        "✨ تألق ساحر مع {title}! ✨",
        "🌙 روتين ليلي مع {title}! 🌃",
        "☀️ حماية نهارية مع {title}! 🌞",
        "💧 ترطيب عميق مع {title}! 💧",
        "🌿 طبيعي وآمن مع {title}! 🌱",
        "🎯 نتائج مضمونة مع {title}! 🎯",
        "⏳ شباب دائم مع {title}! ⏳",
        "🎀 أنوثة طاغية مع {title}! 🎀",
        "💪 ثقة بالنفس مع {title}! 💪",
        "🌟 لمعان خاص مع {title}! 🌟",
        "🧼 نظافة عميقة مع {title}! 🧼",
        "🌸 رائحة منعشة مع {title}! 🌸",
        "💄 لون جذاب مع {title}! 💋",
        "✨ تألق يومي مع {title}! ✨",
        "🌹 فخامة تامة مع {title}! 🌹",
        "💆‍♀️ راحة تامة مع {title}! 💆‍♀️",
        "🧴 عناية فائقة مع {title}! 🧴",
        "👑 ملكة الجمال مع {title}! 👑",
        "🌟 بريق ساحر مع {title}! 🌟",
        "💋 جاذبية لا تُقاوم مع {title}! 💋",
    ],
    
    # رياضة ولياقة (25 جملة)
    "sports": [
        "💪 قوة ونشاط مع {title}! 🏋️‍♂️",
        "🏃‍♂️ أداء ممتاز مع {title}! ⚡",
        "🎯 لياقة عالية مع {title}! 🎯",
        "🏆 بطل مع {title}! 🥇",
        "💦 عرق وجهد مع {title}! 💪",
        "🧘‍♀️ توازن روحي مع {title}! 🧘‍♀️",
        "⚡ طاقة لا نهائية مع {title}! 🔋",
        "🎽 راحة حركية مع {title}! 🏃‍♀️",
        "🏅 إنجازات جديدة مع {title}! 🏅",
        "🤸‍♂️ مرونة عالية مع {title}! 🤸‍♂️",
        "💪 عضلات قوية مع {title}! 💪",
        "🏃‍♀️ سرعة فائقة مع {title}! 🏃‍♀️",
        "🎯 تركيز تام مع {title}! 🎯",
        "🏋️‍♀️ تحدي يومي مع {title}! 🏋️‍♀️",
        "🧘‍♂️ هدوء داخلي مع {title}! 🧘‍♂️",
        "⚡ حيوية يومية مع {title}! ⚡",
        "🎾 أداء احترافي مع {title}! 🎾",
        "🏊‍♂️ سباحة ممتعة مع {title}! 🏊‍♂️",
        "🚴‍♂️ مغامرة رائعة مع {title}! 🚴‍♂️",
        "🏃‍♂️ تحدي نفسك مع {title}! 🏃‍♂️",
        "💪 صحة ولياقة مع {title}! 💪",
        "🎯 أهداف جديدة مع {title}! 🎯",
        "🏆 فوز مضمون مع {title}! 🏆",
        "⚡ نشاط دائم مع {title}! ⚡",
        "🧘‍♀️ صفاء ذهني مع {title}! 🧘‍♀️",
    ],
    
    # أطفال (25 جملة)
    "kids": [
        "👶 سعادة طفلك مع {title}! 🎈",
        "🧸 لحظات جميلة مع {title}! 🎀",
        "🎨 إبداع لا حدود مع {title}! 🖍️",
        "👼 راحة أمك مع {title}! 🤱",
        "🎉 فرح لا ينتهي مع {title}! 🎊",
        "🧩 تعلم ممتع مع {title}! 📚",
        "🍼 رعاية كاملة مع {title}! 🍼",
        "🎈 طفولة سعيدة مع {title}! 🎠",
        "🧸 أحلام جميلة مع {title}! 🌙",
        "🎁 مفاجأة سارة مع {title}! 🎀",
        "👶 نوم هادئ مع {title}! 😴",
        "🎨 ألوان زاهية مع {title}! 🌈",
        "🧩 ذكاء متنامي مع {title}! 🧠",
        "🎉 احتفال مميز مع {title}! 🎂",
        "🍼 راحة تامة مع {title}! ☁️",
        "🧸 حنان لا ينتهي مع {title}! ❤️",
        "🎈 يوم مشرق مع {title}! ☀️",
        "🎠 مغامرة آمنة مع {title}! 🎢",
        "👼 براءة الطفولة مع {title}! 👼",
        "🎀 لمسة أمومة مع {title}! 🤱",
        "🧸 ذكريات جميلة مع {title}! 📸",
        "🎨 موهبة صغيرة مع {title}! 🌟",
        "🎉 ضحكة عالية مع {title}! 😄",
        "👶 نعمة من الله مع {title}! 🙏",
        "🎈 سعادة عائلية مع {title}! 👨‍👩‍👧‍👦",
    ],
}

# --- صيغ السعر ---
PRICE_FORMATS = [
    "🔥 بـ {price} ريال فقط!",
    "💰 {price} ريال",
    "⚡ {price} ريال بس!",
    "💸 فقط {price} ريال!",
    "🎯 {price} ريال ويوصلك!",
]

@app.route('/')
def home():
    return "✅ Bot Active"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def extract_asin(url):
    """استخراج ASIN"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'product/([A-Z0-9]{10})',
        r'amazon\..*/([A-Z0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    if 'amzn.to' in url or 'amzn.eu' in url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            final_url = response.url
            for pattern in patterns:
                match = re.search(pattern, final_url, re.IGNORECASE)
                if match:
                    return match.group(1).upper()
        except:
            pass
    
    return None

def get_category(title):
    """تحديد تصنيف المنتج"""
    title_lower = title.lower()
    
    # تصنيف المنتج"""
    title_lower = title.lower()
    
    # أحذية
    if any(word in title_lower for word in ['shoe', 'shoes', 'sneaker', 'sneakers', 'boot', 'boots', 'sandal', 'sandals', 'footwear']):
        return "shoe"
    
    # إلكترونيات
    if any(word in title_lower for word in ['phone', 'smartphone', 'laptop', 'computer', 'tablet', 'headphone', 'speaker', 'charger', 'camera', 'electronic']):
        return "electronics"
    
    # منزل
    if any(word in title_lower for word in ['furniture', 'sofa', 'bed', 'mattress', 'pillow', 'blanket', 'carpet', 'lamp', 'pot', 'pan', 'blender', 'oven', 'fridge', 'washer', 'vacuum', 'fan', 'heater', 'home', 'kitchen']):
        return "home"
    
    # جمال
    if any(word in title_lower for word in ['perfume', 'cream', 'shampoo', 'soap', 'makeup', 'lipstick', 'beauty', 'skin', 'hair']):
        return "beauty"
    
    # رياضة
    if any(word in title_lower for word in ['sport', 'fitness', 'gym', 'running', 'yoga', 'exercise', 'workout', 'ball', 'racket', 'bicycle']):
        return "sports"
    
    # أطفال
    if any(word in title_lower for word in ['baby', 'kids', 'children', 'toy', 'doll', 'stroller', 'diaper']):
        return "kids"
    
    # ملابس (افتراضي)
    return "clothes"

def translate_title(title):
    """ترجمة العنوان للعربي"""
    words = title.split()
    brand = words[0] if words else ""
    
    title_lower = title.lower()
    category_words = []
    
    # البحث عن كلمات التصنيف
    for eng, ar in CATEGORIES.items():
        if eng in title_lower and ar not in category_words:
            category_words.append(ar)
    
    # إضافة وصف عام
    if any(word in title_lower for word in ['men', 'men\'s', 'man']):
        category_words.append("رجالي")
    elif any(word in title_lower for word in ['women', 'women\'s', 'woman', 'lady', 'ladies']):
        category_words.append("نسائي")
    elif any(word in title_lower for word in ['kid', 'kids', 'child', 'children', 'baby']):
        category_words.append("أطفال")
    
    if any(word in title_lower for word in ['sport', 'running', 'athletic']):
        category_words.append("رياضي")
    
    # دمج الكلمات
    result = brand + " " + " ".join(category_words[:2])
    return result.strip()

def get_product_scraperapi(asin):
    """ScraperAPI"""
    amazon_url = f"https://www.amazon.sa/dp/{asin}"
    scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={amazon_url}&country_code=sa"
    
    try:
        response = requests.get(scraper_url, timeout=20)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_elem = soup.select_one('#productTitle')
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        title = re.sub(r'\s+', ' ', title)
        
        price = None
        price_selectors = [
            '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '.a-price .a-offscreen',
            '.a-price-whole',
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    price = price_match.group()
                    break
        
        if not price:
            return None
        
        image = None
        img_elem = soup.select_one('#landingImage')
        if img_elem:
            image = img_elem.get('data-old-hires') or img_elem.get('src')
            if image:
                image = image.replace('._SL500_', '._SL1500_')
        
        # تحديد التصنيف والترجمة
        category = get_category(title)
        arabic_title = translate_title(title)
        
        return {
            'original_title': title,
            'title': arabic_title,
            'category': category,
            'price': price,
            'image': image,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None

def generate_post(product):
    """توليد المنشور"""
    title = product['title']
    category = product['category']
    price = product['price']
    url = product['url']
    
    # اختيار قالب حسب التصنيف
    templates = TEMPLATES.get(category, TEMPLATES['clothes'])
    template = random.choice(templates)
    
    main_text = template.format(title=title)
    price_text = random.choice(PRICE_FORMATS).format(price=price)
    
    return f"{main_text}\n\n{price_text}\n\nالرابط: {url}"

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    
    urls = re.findall(r'https?://\S+', text)
    
    if not urls:
        bot.reply_to(message, "👋 أرسلي رابط أمازون")
        return
    
    for url in urls:
        if "amazon" not in url.lower() and "amzn" not in url.lower():
            continue
        
        wait_msg = bot.reply_to(message, "⏳ جاري القراءة...")
        
        asin = extract_asin(url)
        if not asin:
            bot.edit_message_text("❌ رابط غير صحيح", chat_id, wait_msg.message_id)
            continue
        
        product = get_product_scraperapi(asin)
        
        if not product:
            bot.edit_message_text(
                "❌ ما قدرت أقرأ المنتج\n\nجربي رابط مباشر من amazon.sa",
                chat_id,
                wait_msg.message_id
            )
            continue
        
        try:
            post = generate_post(product)
            
            if product.get('image'):
                bot.send_photo(chat_id, product['image'], caption=post)
            else:
                bot.send_message(chat_id, post)
            
            bot.delete_message(chat_id, wait_msg.message_id)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            bot.edit_message_text(f"❌ خطأ: {str(e)[:100]}", chat_id, wait_msg.message_id)

def keep_alive():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    print("🚀 Bot starting...")
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot running! 200+ templates loaded")
    bot.infinity_polling()
