import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "7956075348:AAFVmKy956NrjQrYR5-zBMz5l4jV85Q5K8s"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🤖 إعدادات الذكاء الاصطناعي - Groq
# ===================================

GROQ_API_KEY = "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"

# ===================================
# 🏷️ البراندات الشهيرة (تفضل بالإنجليزي)
# ===================================

BRAND_NAMES = {
    "nespresso": "Nespresso",
    "nescafe": "Nescafé",
    "nescafé": "Nescafé",
    "dolce gusto": "Dolce Gusto",
    "delonghi": "DeLonghi",
    "philips": "Philips",
    "bosch": "Bosch",
    "samsung": "Samsung",
    "apple": "Apple",
    "iphone": "iPhone",
    "ipad": "iPad",
    "macbook": "MacBook",
    "airpods": "AirPods",
    "sony": "Sony",
    "lg": "LG",
    "dyson": "Dyson",
    "braun": "Braun",
    "panasonic": "Panasonic",
    "canon": "Canon",
    "nikon": "Nikon",
    "xiaomi": "Xiaomi",
    "huawei": "Huawei",
    "oppo": "OPPO",
    "realme": "Realme",
    "oneplus": "OnePlus",
    "nokia": "Nokia",
    "lenovo": "Lenovo",
    "dell": "Dell",
    "hp": "HP",
    "asus": "ASUS",
    "acer": "Acer",
    "msi": "MSI",
    "logitech": "Logitech",
    "razer": "Razer",
    "hyperx": "HyperX",
    "jbl": "JBL",
    "bose": "Bose",
    "beats": "Beats",
    "sennheiser": "Sennheiser",
    "anker": "Anker",
    "baseus": "Baseus",
    "ugreen": "UGREEN",
    "amazon": "Amazon",
    "google": "Google",
    "microsoft": "Microsoft",
    "adidas": "Adidas",
    "nike": "Nike",
    "puma": "Puma",
    "reebok": "Reebok",
    "under armour": "Under Armour",
    "new balance": "New Balance",
    "asics": "ASICS",
    "timberland": "Timberland",
    "skechers": "Skechers",
    "crocs": "Crocs",
    "levis": "Levi's",
    "wrangler": "Wrangler",
    "tommy hilfiger": "Tommy Hilfiger",
    "calvin klein": "Calvin Klein",
    "lacoste": "Lacoste",
    "polo": "Polo",
    "gucci": "Gucci",
    "prada": "Prada",
    "versace": "Versace",
    "dior": "Dior",
    "chanel": "Chanel",
    "louis vuitton": "Louis Vuitton",
    "hermes": "Hermès",
    "burberry": "Burberry",
    "coach": "Coach",
    "michael kors": "Michael Kors",
    "fossil": "Fossil",
    "casio": "Casio",
    "swatch": "Swatch",
    "rolex": "Rolex",
    "omega": "Omega",
    "tissot": "Tissot",
    "seiko": "Seiko",
    "citizen": "Citizen",
    "orient": "Orient",
    "dove": "Dove",
    "nivea": "Nivea",
    "loreal": "L'Oréal",
    "pantene": "Pantene",
    "head & shoulders": "Head & Shoulders",
    "gillette": "Gillette",
    "oral-b": "Oral-B",
    "colgate": "Colgate",
    "signal": "Signal",
    "ariel": "Ariel",
    "tide": "Tide",
    "persil": "Persil",
    "downy": "Downy",
    "comfort": "Comfort",
    "finish": "Finish",
    "fa": "FA",
    "rexona": "Rexona",
    "axe": "AXE",
    "old spice": "Old Spice",
    "dettol": "Dettol",
    "lifebuoy": "Lifebuoy",
    "purell": "Purell",
    "kleenex": "Kleenex",
    "tork": "Tork",
    "tempo": "Tempo",
    "whisper": "Whisper",
    "always": "Always",
    "tampax": "Tampax",
    "johnson": "Johnson's",
    "johnsons": "Johnson's",
    "pampers": "Pampers",
    "huggies": "Huggies",
    "molfix": "Molfix",
    "fine": "Fine",
    "marlboro": "Marlboro",
    "lm": "L&M",
    "kent": "Kent",
    "davidoff": "Davidoff",
    "nesquik": "Nesquik",
    "kitkat": "KitKat",
    "snickers": "Snickers",
    "mars": "Mars",
    "twix": "Twix",
    "bounty": "Bounty",
    "milky way": "Milky Way",
    "galaxy": "Galaxy",
    "cadbury": "Cadbury",
    "lindt": "Lindt",
    "ferrero": "Ferrero",
    "nutella": "Nutella",
    "kinder": "Kinder",
    "oreo": "Oreo",
    "belvita": "Belvita",
    "lu": "LU",
    "tuc": "TUC",
    "pringles": "Pringles",
    "lays": "Lay's",
    "doritos": "Doritos",
    "cheetos": "Cheetos",
    "pepsi": "Pepsi",
    "coca cola": "Coca-Cola",
    "cocacola": "Coca-Cola",
    "sprite": "Sprite",
    "fanta": "Fanta",
    "7up": "7UP",
    "mirinda": "Mirinda",
    "mountain dew": "Mountain Dew",
    "red bull": "Red Bull",
    "monster": "Monster",
    "power horse": "Power Horse",
    "nescafe dolce gusto": "Nescafé Dolce Gusto",
    "dolcegusto": "Dolce Gusto",
    "piccolo": "Piccolo",
    "genio": "Genio",
    "infinissima": "Infinissima",
    "esperta": "Esperta",
    "circolo": "Circolo",
    "creativa": "Creativa",
    "melody": "Melody",
    "oblo": "Oblo",
    "jovia": "Jovia",
    "minime": "Mini Me",
    "colors": "Colors",
    "drop": "Drop",
    "stelia": "Stelia",
    "movenza": "Movenza",
    "lumio": "Lumio",
    "eclipse": "Eclipse",
}


def protect_brands(text):
    """يحافظ على اسماء البراندات بالإنجليزي"""
    for brand_key, brand_original in sorted(BRAND_NAMES.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(brand_key), re.IGNORECASE)
        text = pattern.sub(brand_original, text)
    return text


def generate_ai_sentence(product_name, category, price, old_price, discount_percent, gender="men"):
    """
    توليد جملة تشويقية ذكية ومتغيرة كل مرة باستخدام Groq AI
    """
    
    # اختيار نمط عشوائي للجملة عشان يكون في تنوع أكبر
    styles = [
        "حماسي وصاروخي",
        "مفاجأة وصدمة سعر",
        "عاطفي وشخصي (تكلم وكأنك جربت المنتج)",
        "تحدي وسخرية خفيفة",
        "ترقب وندرة",
    ]
    chosen_style = random.choice(styles)
    
    discount_info = ""
    if discount_percent and discount_percent > 5:
        discount_info = f"\n- نسبة الخصم: {discount_percent}%"
    
    prompt = f"""أنت كاتب محتوى سعودي محترف في قنوات تليجرام للتسويق بالعمولة (زي قناة "نص السعر").
اكتب جملة تشويقية قصيرة جداً ومختصرة (سطر واحد فقط) باللهجة السعودية الخفيفة.

🔹 قواعد مهمة:
- الجملة لازم تكون مختصرة جداً (5-12 كلمة كحد أقصى)
- استخدم إيموجي كثير (2-4 إيموجي) في الجملة نفسها
- خلي الجملة تخص المنتج نفسه (مثلاً لو قهوة: تكلم عن القهوة والصباح والطاقة، لو إلكترونيات: تكلم عن التقنية والجودة)
- لا تذكر السعر أو اسم المنتج بالتفصيل في الجملة
- اكتب بلهجة سعودية خفيفة (مثل: "مره", "ياجمااعة", "يستاهل", "صيدة", "ووووو", "ياجدعان")
- كل مرة اكتب جملة مختلفة تماماً عن اللي قبلها (ما تكررش نفس الجملة أبداً)
- النمط المطلوب: {chosen_style}

🔹 بيانات المنتج:
- اسم المنتج: {product_name}
- الفئة: {category}{discount_info}

اكتب جملة واحدة فقط بدون أي مقدمة:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت كاتب محتوى سعودي في قنوات تسويق بالعمولة. تكتب جمل تشويقية مختصرة جداً بإيموجي كثير. كل مرة تكتب جملة مختلفة تماماً."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.95,
            "max_tokens": 50
        }
        
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )
        
        if r.status_code == 200:
            result = r.json()
            sentence = result["choices"][0]["message"]["content"].strip()
            sentence = sentence.replace('"', '').replace("'", "").strip()
            sentence = re.sub(r'^[ـ\s]+', '', sentence)
            return sentence
                
    except Exception as e:
        print(f"Groq error: {e}")
    
    # fallback - متنوع وعشوائي حسب الفئة
    return generate_smart_fallback_sentence(product_name, category, discount_percent)


def generate_smart_fallback_sentence(product_name, category, discount_percent):
    """توليد جملة تشويقية مختصرة بدون API - متغيرة حسب الفئة"""
    
    category_templates = {
        "electronics": [
            "⚡️ تقنية مره تفوز! 🔥",
            "📱 يا سلام على الجودة! 🤩",
            "🚀 جهاز يستاهل كل ريال! 💎",
            "🔥 تحديث لازم يصير! ⚡️",
            "💻 أداء مجنون يا جماعة! 🚀",
        ],
        "home": [
            "🏠 بيتك يستاهل الأفضل! ✨",
            "🔥 راحة البيت تبدأ من هنا! ☕️",
            "⚡️ جهاز يسهللك حياتك! 🏠",
            "💎 جودة تدوم معاك! 🔥",
            "🚀 تحديث للبيت ولا أروع! ✨",
        ],
        "beauty": [
            "💄 جمالك يستاهل الأفضل! ✨",
            "🌸 ريحة تفتح النفس! 💫",
            "✨ إشراقة مختلفة اليوم! 💄",
            "💎 فخامة بسعر يجنن! 🌸",
            "🔥 جمال ما يتفوت! 💫",
        ],
        "fashion": [
            "👟 طلة تكسر الدنيا! 🔥",
            "✨ ستايل مختلف اليوم! 💎",
            "🔥 لبس ياخذ العقل! 👌",
            "💫 أناقة بلا حدود! 👟",
            "🚀 طلة صاروخية يا جماعة! ✨",
        ],
        "sports": [
            "💪 طاقة تفجّر يا بطل! 🔥",
            "🏋️ رياضتك تستاهل الأفضل! ⚡️",
            "🔥 عرق اليوم يستاهل! 💪",
            "🚀 أداء يجنن يا جماعة! 💥",
            "⚡️ جاهز للتحدي؟! 🔥",
        ],
    }
    
    templates = category_templates.get(category, [
        "🔥 لا يفوتكم يا جماعة! 🚨",
        "💥 ووووووو 🔥",
        "🎉 صيدة ما تتفوت 🔥",
        "🤩 خصم مجنون عليه! ⚡️",
        "🔥 العرض رهيييب! 💰",
        "🚨 فرصة ذهبية! ⏰",
        "⚡️ لا يفوتك! 🔥",
        "💰 سعر مره حلو! 🤩",
        "🔥 يستاهل التجربة! 👌",
        "🎯 من الأخير: لا يتفوت! 🔥",
        "💎 جودة بسعر خيالي! 🔥",
        "🚀 عرض صاروخي! ⚡️",
        "🔥 يا سلااام على السعر! 🤩",
        "⏰ العرض محدود! 🔥",
        "💥 خصم يجنن! 🚨",
    ])
    
    if discount_percent and discount_percent > 30:
        discount_templates = [
            f"🔥 خصم {discount_percent}% يا جماعة! 🚨",
            f"🤩 وفر {discount_percent}% الحين! ⚡️",
            f"💥 خصم {discount_percent}% مجنون! 🔥",
            f"🎯 خصم {discount_percent}% لا يتفوت! ⏰",
        ]
        return random.choice(discount_templates)
    
    return random.choice(templates)


# ===================================
# 🔧 الكلمات المفتاحية للفئات
# ===================================

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


def detect_product_gender(product_name):
    name_lower = product_name.lower()
    women_indicators = ['women', 'woman', 'ladies', 'lady', 'female', 'feminine', 'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي', 'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick']
    men_indicators = ['men', 'man', 'male', 'masculine', 'gents', 'gentlemen', 'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة']
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    return 'neutral'


# ===================================
# 🔄 قاموس الترجمة (بدون براندات)
# ===================================

TRANSLATION_DICT = {
    "laptop": "لابتوب", "tablet": "تابلت", "keyboard": "كيبورد", "mouse": "ماوس",
    "charger": "شاحن", "cable": "كيبل", "power bank": "باور بانك", "battery": "بطارية",
    "screen": "شاشة", "monitor": "شاشة عرض", "camera": "كاميرا", "speaker": "سماعة",
    "watch": "ساعة", "smartwatch": "ساعة ذكية", "headphones": "سماعات رأس",
    "router": "راوتر", "modem": "مودم", "tv": "تلفزيون", "television": "تلفزيون",
    "shoes": "حذاء", "shoe": "حذاء", "sneakers": "حذاء رياضي", "boots": "بوت",
    "sandals": "صندل", "slippers": "شبشب", "t-shirt": "تيشيرت", "shirt": "قميص",
    "pants": "بنطلون", "jeans": "جينز", "jacket": "جاكيت", "hoodie": "هودي",
    "dress": "فستان", "skirt": "تنورة", "socks": "شرابات", "cap": "كاب",
    "hat": "قبعة", "bag": "شنطة", "backpack": "حقيبة ظهر", "wallet": "محفظة",
    "belt": "حزام", "scarf": "وشاح", "gloves": "قفازات",
    "perfume": "عطر", "fragrance": "عطر", "oud": "عود", "musk": "مسك",
    "cream": "كريم", "lotion": "لوشن", "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف", "ac": "مكيف",
    "heater": "دفاية", "fan": "مروحة", "blender": "خلاط", "mixer": "عجانة",
    "oven": "فرن", "microwave": "مايكرويف", "toaster": "محمصة", "kettle": "غلاية",
    "coffee maker": "ماكينة قهوة", "iron": "مكواة", "hair dryer": "سشوار",
    "chair": "كرسي", "table": "طاولة", "desk": "مكتب", "bed": "سرير",
    "sofa": "كنبة", "couch": "كنبة", "lamp": "لمبة", "light": "إضاءة",
    "mirror": "مرآة", "carpet": "سجادة", "curtain": "ستارة",
    "treadmill": "سير كهربائي", "dumbbell": "دامبل", "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة", "ball": "كرة", "toys": "ألعاب", "toy": "لعبة",
    "baby": "أطفال", "kids": "أطفال",
    "wireless": "لاسلكي", "bluetooth": "بلوتوث", "smart": "ذكي", "digital": "رقمي",
    "electric": "كهربائي", "automatic": "أوتوماتيك", "portable": "محمول",
    "professional": "احترافي", "original": "أصلي", "new": "جديد",
    "pro": "برو", "max": "ماكس", "plus": "بلس", "ultra": "ألترا", "mini": "ميني",
    "premium": "بريميوم", "deluxe": "ديلوكس", "unisex": "للجنسين", "adult": "للبالغين",
    "men": "رجالي", "women": "نسائي",
    "black": "أسود", "white": "أبيض", "blue": "أزرق", "red": "أحمر", "green": "أخضر",
    "capsule": "كبسولة", "capsules": "كبسولات", "machine": "ماكينة", "maker": "صانع",
    "espresso": "إسبريسو", "coffee": "قهوة", "cafe": "كافيه",
    "preparation": "تحضير", "prepare": "تحضير",
}


def translate_to_arabic(text):
    # حماية البراندات أولاً
    text = protect_brands(text)
    
    text_lower = text.lower()
    words = text_lower.split()
    translated_words = []
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            translated_words.append(word)
    result = " ".join(translated_words)
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)
    return result


def smart_arabic_title(full_title):
    # حماية البراندات في العنوان الأصلي
    full_title = protect_brands(full_title)
    
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
    
    # إعادة حماية البراندات بعد الترجمة
    result = protect_brands(result)
    
    if len(result) > 80:
        for sep in ['،', ',', '-', '|', '/']:
            if sep in result[:80]:
                idx = result.rfind(sep, 40, 80)
                if idx > 0:
                    result = result[:idx]
                    break
        else:
            idx = result.rfind(' ', 60, 80)
            if idx > 0:
                result = result[:idx]
            else:
                result = result[:80]
    return result.strip()


def get_category_emoji(category):
    """إيموجي حسب الفئة"""
    emojis = {
        "electronics": "📱",
        "fashion": "👕",
        "beauty": "💄",
        "home": "🏠",
        "sports": "💪",
    }
    return emojis.get(category, "📦")


# ===================================
# 🔧 دوال المساعدة
# ===================================

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl']):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            return r.url
        return url
    except:
        return url


def is_saudi_amazon(url):
    return "amazon.sa" in url.lower()


def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'([A-Z0-9]{10})/?$',
        r'([A-Z0-9]{10})(?:[/?]|\b)'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            num_float = float(num_str)
            num_int = int(num_float)
            return f"{num_int} ريال"
    except:
        pass
    return price_text


# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================

def get_high_quality_image(soup):
    image = None
    img_elem = soup.select_one("#landingImage")
    if img_elem:
        image = img_elem.get("data-old-hires")
        if not image:
            dynamic_data = img_elem.get("data-a-dynamic-image")
            if dynamic_data:
                try:
                    img_dict = json.loads(dynamic_data)
                    if img_dict:
                        sorted_urls = sorted(img_dict.keys(), key=lambda x: img_dict[x][0] * img_dict[x][1], reverse=True)
                        image = sorted_urls[0] if sorted_urls else None
                except:
                    pass
        if not image:
            image = img_elem.get("src")
    if not image:
        gallery_img = soup.select_one("#imgTagWrapperId img")
        if gallery_img:
            image = gallery_img.get("data-old-hires") or gallery_img.get("src")
    if not image:
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img:
            image = og_img.get("content")
    if image:
        image = clean_image_url(image)
    return image


def clean_image_url(url):
    if not url:
        return None
    patterns_to_remove = [
        r'_SX\d+_SY\d+_', r'_SX\d+_', r'_SY\d+_',
        r'_CR\d+,\d+,\d+,\d+_', r'_AC_SL\d+_',
        r'_SCLZZZZZZZ_', r'_FMwebp_', r'_QL\d+_',
    ]
    cleaned = url
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '_', cleaned)
    if '_SL' not in cleaned and 'amazon' in cleaned:
        cleaned = re.sub(r'(\.[a-zA-Z]+)(\?.*)?$', r'_SL1500\1', cleaned)
    cleaned = cleaned.split('?')[0]
    return cleaned


def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    for attempt, ua in enumerate(user_agents):
        try:
            if attempt > 0:
                time.sleep(2)
            headers = {
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
            }
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code != 200 or len(r.text) < 5000:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            title_elem = soup.select_one("#productTitle")
            if not title_elem:
                continue
            full_title = title_elem.text.strip()
            price = None
            price_selectors = [
                ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
                ".a-price.a-text-price.apexPriceToPay .a-offscreen",
                ".a-price.aok-align-center .a-offscreen",
                ".a-price .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
                ".a-price-whole"
            ]
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    price = elem.text.strip()
                    if any(c.isdigit() for c in price):
                        break
            old_price = None
            old_selectors = [
                ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
                ".a-price.a-text-price .a-offscreen",
                ".basisPrice .a-offscreen",
            ]
            for selector in old_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    text = elem.text.strip()
                    if text != price and any(c.isdigit() for c in text):
                        old_price = text
                        break
            image = get_high_quality_image(soup)
            discount_percent = None
            try:
                if old_price and price:
                    old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
                    new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
                    if old_num > new_num:
                        discount_percent = int(((old_num - new_num) / old_num) * 100)
            except:
                pass
            if price:
                arabic_title = smart_arabic_title(full_title)
                return arabic_title, price, old_price, image, discount_percent
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    return None


# ===================================
# ✨ التوليد النهائي - المنشور النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    category = detect_product_category(product_name)
    gender = detect_product_gender(product_name)
    
    # 🧠 توليد جملة تشويقية مختلفة كل مرة (ممكن تستخدم old_price وdiscount_percent كسياق للذكاء)
    opening = generate_ai_sentence(product_name, category, price, old_price, discount_percent, gender)

    clean_current = clean_price(price)
    
    # اختيار الإيموجي حسب الفئة
    emoji = get_category_emoji(category)

    # بناء الرسالة بأجزاء منفصلة
    parts = []
    
    # الجزء الأول: الجملة التشويقية
    parts.append(opening)
    
    # الجزء الثاني: اسم المنتج (البراند بالإنجليزي)
    parts.append(f"{emoji} {product_name}")
    
    # الجزء الثالث: السعر فقط (بدون سعر قديم)
    parts.append(f"💰 السعر: {clean_current}")
    
    # الجزء الرابع: الرابط
    parts.append(f"🔗 {original_url}")

    # ربط الأجزاء بسطرين فاضيين (\n\n) عشان Telegram يعرض سطر فاضي واضح بين كل جزء
    return "\n\n".join(parts)


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        expanded = expand_url(original_url)

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط يجب أن يكون من amazon.sa")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        product_name, price, old_price, image, discount_percent = product
        post = generate_post(product_name, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()
