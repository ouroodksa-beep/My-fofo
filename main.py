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

def generate_ai_sentence(product_name, category, price, old_price, discount_percent, gender="men"):
    """
    توليد جملة تسويقية ذكية باستخدام Groq AI
    """
    
    # بناء برومبت ذكي حسب البيانات
    discount_info = ""
    if discount_percent and discount_percent > 5:
        discount_info = f"\n- خصم: {discount_percent}%"
    
    prompt = f"""أنت كاتب محتوى سعودي محترف في التسويق بالعمولة لمنتجات أمازون السعودية.
اكتب جملة تسويقية قصيرة (سطر واحد فقط) باللهجة السعودية الخفيفة والعامية.

🔹 قواعد مهمة:
- الجملة لازم تكون قصيرة (12-20 كلمة كحد أقصى)
- استخدم إيموجي واحد فقط في النهاية
- لا تذكر السعر في الجملة (السعر مكتوب تحت)
- اكتب بلهجة سعودية خفيفة (مثل: "مره", "شيء", "من الأخير", "يستاهل")
- خلي الجملة حماسية وتخلي المتابع يحب يشتري
- لا تستخدم نقاط أو قائمة، جملة واحدة متصلة فقط
- لا تكرر كلمة "منتج" أو "هذا"

🔹 بيانات المنتج:
- اسم المنتج: {product_name}
- الفئة: {category}
- الجنس المستهدف: {"نسائي" if gender == "women" else "رجالي" if gender == "men" else "عام"}{discount_info}

اكتب الجملة فقط بدون أي مقدمة أو شرح:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت كاتب محتوى سعودي محترف في التسويق بالعمولة. تكتب بلهجة سعودية خفيفة وجذابة."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 60
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
            
            # تنظيف الجملة
            sentence = sentence.replace('"', '').replace("'", "").strip()
            # إزالة ترقيم في النهاية لو فيه
            sentence = re.sub(r'[.!?]+$', '', sentence).strip()
            
            # التأكد من وجود إيموجي
            emojis = ["🔥", "👌", "💎", "✨", "🚀", "💪", "👍", "🎯", "⚡️", "🏆", "🌟", "😎", "💯", "✅", "👀", "🎩", "👑", "🎽", "🌹", "🏠", "🛋️", "🧴", "👗", "👕", "⌚️", "📱", "💻", "🎁", "⭐"]
            has_emoji = any(emoji in sentence for emoji in emojis)
            if not has_emoji:
                sentence += " 🔥"
            
            return sentence
                
    except Exception as e:
        print(f"Groq error: {e}")
    
    # fallback لو فشل الـ API
    return generate_smart_fallback_sentence(product_name, category, discount_percent, gender)


def generate_smart_fallback_sentence(product_name, category, discount_percent, gender):
    """
    توليد جملة ذكية محلياً بدون API
    """
    
    # قوالب حسب الفئة
    templates = {
        "electronics": [
            "جهاز {product} يغير طريقة استخدامك للتقنية 🔥",
            "{product} مواصفاته خرافية وما يخيب ظنك 👌",
            "تقنية مره حلوة بسعر ينافس، {product} يستاهل التجربة 💎",
            "من الأخير: {product} أداء قوي وثابت ما يتهز ⚡️",
            "ترقية ذكية لأدواتك مع {product} 🚀",
            "{product} شيء يفوق التوقع بمراحل ✨"
        ],
        "fashion": [
            "إطلالة تلفت الأنظار مع {product} 👀",
            "{product} لبس مره يليق فيك وفي ذوقك 🎩",
            "قطعة أساسية لازم تكون بخزانتك: {product} 👕",
            "أناقة بسيطة وشيء فيك الخالق مع {product} ✨",
            "{product} شياكة وراحة بوقت واحد 😎",
            "تحدث بصمت.. {product} أناقة وذوق 🎭"
        ],
        "beauty": [
            "عطر {product} يخلي حضورك له وزن 🌹",
            "{product} ريحة تثبت أنك تفهم بالجودة 👃",
            "منتج {product} يعطي نتيجة واضحة من أول استخدام ✨",
            "{product} شيء يزيد ثقتك بنفسك أضعاف 💪",
            "عطرك عنوانك.. {product} اختر الأفضل 🏆",
            "{product} نظافة وانتعاش ما له مثيل 🌊"
        ],
        "home": [
            "راحة البيت تبدأ من {product} 🏠",
            "{product} شيء يسهل عليك حياتك اليومية 🛋️",
            "جودة تدوم مع {product} وما تخذلك مع الوقت 🛡️",
            "بيتك يستاهل {product} 👌",
            "{product} حل ممتاز لمشاكل البيت اليومية ✅",
            "استثمار في راحتك اليومية مع {product} 📈"
        ],
        "sports": [
            "{product} ترفع مستواك الرياضي 📈",
            "جهاز {product} يساعدك توصل لهدفك أسرع 🏃‍♂️",
            "معدات احترافية للي جاد بالرياضة: {product} 💪",
            "{product} شيء يحمسك تبدأ اليوم مش بكرا 🔥",
            "جودة تتحمل أقوى التمارين مع {product} 🏋️‍♂️",
            "تمرن بذكاء مع {product} 🧠"
        ],
        "general": [
            "عرض ما يتفوت على {product} 🔥",
            "{product} جودة تتكلم عن نفسها 💎",
            "من الأخير: {product} شيء يستاهل الشراء ✅",
            "فرصة لا تعوض على {product} استغلها الحين ⏰",
            "{product} قيمة عالية بسعر ينافس 💰",
            "ما راح تلقى مثل {product} بسعر أحسن 🥇"
        ]
    }
    
    category_templates = templates.get(category, templates["general"])
    
    # تعديل حسب الجنس
    if gender == "women":
        category_templates = [
            t.replace("يليق فيك", "يليق فيكِ")
             .replace("تفهم", "تفهمين")
             .replace("ثقتك", "ثقتكِ")
             .replace("حياتك", "حياتكِ")
             .replace("بنفسك", "بنفسكِ")
             .replace("يساعدك", "يساعدكِ")
             .replace("توصل", "توصلين")
             .replace("تبدأ", "تبدأين")
             .replace("تمرن", "تمرنين")
             .replace("تحدث", "تحدثين")
            for t in category_templates
        ]
    
    template = random.choice(category_templates)
    
    # إضافة الخصم
    if discount_percent and discount_percent > 10:
        discount_phrases = [" وخصم {discount}% يجنن!", " ووفر {discount}% الحين!", " بخصم {discount}% لا يفوت!"]
        template = template.replace(" 🔥", random.choice(discount_phrases) + " 🔥")
        template = template.replace(" 👌", random.choice(discount_phrases) + " 👌")
        template = template.replace(" 💎", random.choice(discount_phrases) + " 💎")
    
    sentence = template.format(product=product_name, discount=discount_percent if discount_percent else 0)
    return sentence


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
    unisex_indicators = ['unisex', 'adult', 'للجنسين', 'للبالغين', 'محايد']
    
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    for indicator in unisex_indicators:
        if indicator in name_lower:
            return 'neutral'
    
    return 'neutral'

# ===================================
# 🔄 قاموس الترجمة
# ===================================

TRANSLATION_DICT = {
    "adidas": "Adidas", "nike": "Nike", "puma": "Puma", "reebok": "Reebok",
    "under armour": "Under Armour", "new balance": "New Balance", "asics": "ASICS",
    "vans": "Vans", "converse": "Converse", "fila": "Fila", "skechers": "Skechers",
    "crocs": "Crocs", "timberland": "Timberland",
    
    "zara": "Zara", "h&m": "H&M", "gap": "Gap", "mango": "Mango",
    "bershka": "Bershka", "pull&bear": "Pull&Bear", "shein": "SHEIN",
    
    "gucci": "Gucci", "prada": "Prada", "versace": "Versace",
    "burberry": "Burberry", "chanel": "Chanel", "dior": "Dior",
    "lv": "Louis Vuitton", "louis vuitton": "Louis Vuitton",
    "ysl": "YSL", "balenciaga": "Balenciaga", "fendi": "Fendi",
    
    "levi's": "Levi's", "wrangler": "Wrangler", "diesel": "Diesel",
    "guess": "GUESS", "tommy hilfiger": "Tommy Hilfiger",
    "calvin klein": "Calvin Klein", "ck": "CK",
    "ralph lauren": "Ralph Lauren", "lacoste": "Lacoste",
    
    "michael kors": "Michael Kors", "coach": "Coach", "fossil": "Fossil",
    "armani": "Armani", "emporio armani": "Emporio Armani",
    "hugo boss": "HUGO BOSS", "boss": "BOSS",
    
    "ray-ban": "Ray-Ban", "rayban": "Ray-Ban", "oakley": "Oakley",
    
    "casio": "Casio", "g-shock": "G-Shock", "gshock": "G-Shock",
    "seiko": "Seiko", "citizen": "Citizen", "tissot": "Tissot",
    
    "carolina herrera": "Carolina Herrera", "paco rabanne": "Paco Rabanne",
    "jean paul gaultier": "Jean Paul Gaultier", "montblanc": "Montblanc",
    "davidoff": "Davidoff",
    
    "l'oreal": "L'Oreal", "loreal": "L'Oreal", "maybelline": "Maybelline",
    "mac": "MAC", "clinique": "Clinique", "nivea": "Nivea",
    "the ordinary": "The Ordinary", "huda beauty": "Huda Beauty",
    "philips": "Philips", "braun": "Braun", "dyson": "Dyson",
    
    "apple": "Apple", "samsung": "Samsung", "huawei": "Huawei",
    "xiaomi": "Xiaomi", "oppo": "OPPO", "vivo": "vivo",
    "realme": "realme", "oneplus": "OnePlus", "nokia": "Nokia",
    "sony": "Sony", "lg": "LG", "lenovo": "Lenovo", "hp": "HP",
    "dell": "Dell", "asus": "ASUS", "acer": "Acer", "msi": "MSI",
    "razer": "Razer", "microsoft": "Microsoft", "surface": "Surface",
    "beats": "Beats", "jbl": "JBL", "bose": "Bose",
    "anker": "Anker", "logitech": "Logitech", "corsair": "Corsair",
    "tp-link": "TP-Link", "tplink": "TP-Link",
    "canon": "Canon", "nikon": "Nikon", "gopro": "GoPro",
    "playstation": "PlayStation", "ps5": "PS5", "ps4": "PS4",
    "xbox": "Xbox", "nintendo": "Nintendo", "switch": "Switch",
    
    "tefal": "Tefal", "moulinex": "Moulinex", "kenwood": "Kenwood",
    "bosch": "Bosch", "siemens": "Siemens", "panasonic": "Panasonic",
    "sharp": "Sharp", "toshiba": "Toshiba", "delonghi": "DeLonghi",
    "nespresso": "Nespresso", "kitchenaid": "KitchenAid",
    
    "ikea": "IKEA", "muji": "MUJI",
    
    "the north face": "The North Face", "north face": "The North Face",
    "columbia": "Columbia", "patagonia": "Patagonia",
    "salomon": "Salomon", "wilson": "Wilson",
    
    "lego": "LEGO", "barbie": "Barbie", "hasbro": "Hasbro",
    "mattel": "Mattel", "disney": "Disney", "marvel": "Marvel",
    
    "laptop": "لابتوب", "tablet": "تابلت", "keyboard": "كيبورد", "mouse": "ماوس",
    "charger": "شاحن", "cable": "كيبل", "power bank": "باور بانك", "battery": "بطارية",
    "screen": "شاشة", "monitor": "شاشة عرض", "camera": "كاميرا", "speaker": "سماعة",
    "watch": "ساعة", "smartwatch": "ساعة ذكية", "headphones": "سماعات رأس",
    "earbuds": "سماعات أذن", "router": "راوتر", "modem": "مودم",
    "tv": "تلفزيون", "television": "تلفزيون",
    
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
    result = " ".join(translated_words)
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)
    return result

def smart_arabic_title(full_title):
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    seen = set()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
    if len(result) > 100:
        for sep in ['،', ',', '-', '|', '/']:
            if sep in result[:100]:
                idx = result.rfind(sep, 50, 100)
                if idx > 0:
                    result = result[:idx]
                    break
        else:
            idx = result.rfind(' ', 80, 100)
            if idx > 0:
                result = result[:idx]
            else:
                result = result[:100]
    return result.strip()

# ===================================
# 🔧 دوال المساعدة
# ===================================

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co']):
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
            return f"{num_int} ريال سعودي"
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
# ✨ التوليد النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    category = detect_product_category(product_name)
    gender = detect_product_gender(product_name)
    if gender == 'neutral':
        gender = 'men'
    
    # 🧠 توليد الجملة الذكية باستخدام AI
    opening = generate_ai_sentence(product_name, category, price, old_price, discount_percent, gender)

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None

    lines = [opening]
    lines.append("")
    lines.append(f"🛒 {product_name}")
    lines.append("")

    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الآن: {clean_current} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean_current}")

    lines.append("")
    lines.append(f"🔗 {original_url}")

    return "\n".join(lines)

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

        wait = bot.reply_to(msg, "⏳ جاري التحليل والتوليد الذكي...")

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

print("🤖 البوت يعمل بالذكاء الاصطناعي...")
bot.infinity_polling()
