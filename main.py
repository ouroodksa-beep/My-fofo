import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import random

TOKEN = "7956075348:AAEYTL28GKeMN7TXyVeGM69iUcfg5ZwOSIk"
bot = telebot.TeleBot(TOKEN)

GROQ_API_KEY = "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"

BRAND_NAMES = {
    "nespresso": "Nespresso", "nescafe": "Nescafé", "nescafé": "Nescafé",
    "dolce gusto": "Dolce Gusto", "delonghi": "DeLonghi", "philips": "Philips",
    "bosch": "Bosch", "samsung": "Samsung", "apple": "Apple", "iphone": "iPhone",
    "ipad": "iPad", "macbook": "MacBook", "airpods": "AirPods", "sony": "Sony",
    "lg": "LG", "dyson": "Dyson", "braun": "Braun", "panasonic": "Panasonic",
    "canon": "Canon", "nikon": "Nikon", "xiaomi": "Xiaomi", "huawei": "Huawei",
    "oppo": "OPPO", "realme": "Realme", "oneplus": "OnePlus", "nokia": "Nokia",
    "lenovo": "Lenovo", "dell": "Dell", "hp": "HP", "asus": "ASUS", "acer": "Acer",
    "msi": "MSI", "logitech": "Logitech", "razer": "Razer", "hyperx": "HyperX",
    "jbl": "JBL", "bose": "Bose", "beats": "Beats", "sennheiser": "Sennheiser",
    "anker": "Anker", "baseus": "Baseus", "ugreen": "UGREEN", "amazon": "Amazon",
    "google": "Google", "microsoft": "Microsoft", "adidas": "Adidas", "nike": "Nike",
    "puma": "Puma", "reebok": "Reebok", "under armour": "Under Armour",
    "new balance": "New Balance", "asics": "ASICS", "timberland": "Timberland",
    "skechers": "Skechers", "crocs": "Crocs", "levis": "Levi's", "wrangler": "Wrangler",
    "tommy hilfiger": "Tommy Hilfiger", "calvin klein": "Calvin Klein", "lacoste": "Lacoste",
    "polo": "Polo", "gucci": "Gucci", "prada": "Prada", "versace": "Versace",
    "dior": "Dior", "chanel": "Chanel", "louis vuitton": "Louis Vuitton",
    "hermes": "Hermès", "burberry": "Burberry", "coach": "Coach",
    "michael kors": "Michael Kors", "fossil": "Fossil", "casio": "Casio",
    "swatch": "Swatch", "rolex": "Rolex", "omega": "Omega", "tissot": "Tissot",
    "seiko": "Seiko", "citizen": "Citizen", "orient": "Orient", "dove": "Dove",
    "nivea": "Nivea", "loreal": "L'Oréal", "pantene": "Pantene",
    "head & shoulders": "Head & Shoulders", "gillette": "Gillette",
    "oral-b": "Oral-B", "colgate": "Colgate", "signal": "Signal",
    "ariel": "Ariel", "tide": "Tide", "persil": "Persil", "downy": "Downy",
    "comfort": "Comfort", "finish": "Finish", "fa": "FA", "rexona": "Rexona",
    "axe": "AXE", "old spice": "Old Spice", "dettol": "Dettol",
    "lifebuoy": "Lifebuoy", "purell": "Purell", "kleenex": "Kleenex",
    "tork": "Tork", "tempo": "Tempo", "whisper": "Whisper", "always": "Always",
    "tampax": "Tampax", "johnson": "Johnson's", "johnsons": "Johnson's",
    "pampers": "Pampers", "huggies": "Huggies", "molfix": "Molfix",
    "fine": "Fine", "marlboro": "Marlboro", "lm": "L&M", "kent": "Kent",
    "davidoff": "Davidoff", "nesquik": "Nesquik", "kitkat": "KitKat",
    "snickers": "Snickers", "mars": "Mars", "twix": "Twix", "bounty": "Bounty",
    "milky way": "Milky Way", "galaxy": "Galaxy", "cadbury": "Cadbury",
    "lindt": "Lindt", "ferrero": "Ferrero", "nutella": "Nutella",
    "kinder": "Kinder", "oreo": "Oreo", "belvita": "Belvita", "lu": "LU",
    "tuc": "TUC", "pringles": "Pringles", "lays": "Lay's", "doritos": "Doritos",
    "cheetos": "Cheetos", "pepsi": "Pepsi", "coca cola": "Coca-Cola",
    "cocacola": "Coca-Cola", "sprite": "Sprite", "fanta": "Fanta",
    "7up": "7UP", "mirinda": "Mirinda", "mountain dew": "Mountain Dew",
    "red bull": "Red Bull", "monster": "Monster", "power horse": "Power Horse",
    "nescafe dolce gusto": "Nescafé Dolce Gusto", "dolcegusto": "Dolce Gusto",
    "vichy": "Vichy", "dercos": "Dercos", "l'oreal": "L'Oréal",
    "l'oréal": "L'Oréal", "loreal paris": "L'Oréal Paris",
    "tresemme": "TRESemmé", "guess": "Guess", "night guess": "Night Guess",
    "swiss arabian": "Swiss Arabian", "kashkha": "Kashkha",
    "ultra doux": "Ultra Doux", "honey treasures": "Honey Treasures",
    "magic retouch": "Magic Retouch", "keratin smooth": "Keratin Smooth",
    "energy": "Energy",
}


def protect_brands(text):
    for brand_key, brand_original in sorted(BRAND_NAMES.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(brand_key), re.IGNORECASE)
        text = pattern.sub(brand_original, text)
    return text


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
    women_indicators = ['women', 'woman', 'ladies', 'lady', 'female', 'feminine', 'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي', 'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick', 'شامبو', 'بلسم', 'كريم', 'عطر نسائي', 'عطر للنساء']
    men_indicators = ['men', 'man', 'male', 'masculine', 'gents', 'gentlemen', 'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة', 'عطر رجالي', 'عطر للرجال']
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    return 'neutral'


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
    "anti": "مضاد", "anti-hair loss": "مضاد تساقط", "hair loss": "تساقط الشعر",
    "stimulating": "منشط", "stimulator": "منشط", "fortifying": "يقوي",
    "serum": "سيروم", "repair": "ترميم", "damaged": "تالف", "split ends": "نهايات متقصفة",
    "protection": "حماية", "heat": "حرارة", "spray": "بخاخ", "fixative": "مثبت",
    "keratin": "كيراتين", "smooth": "سموث", "touch": "ريتاتش", "retouch": "ريتاتش",
    "night": "نايت", "eau de toilette": "أو دي تواليت", "edt": "أو دي تواليت",
    "eau de parfum": "أو دي بارفان", "edp": "أو دي بارفان", "perfume": "عطر",
    "for men": "للرجال", "for women": "للنساء", "unisex": "للجنسين",
    "swiss": "سويسرية", "arabian": "عربية", "oriental": "شرقية",
    "honey": "هوني", "treasures": "تريجرز",
}


def translate_to_arabic(text):
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
    full_title = protect_brands(full_title)
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
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
    emojis = {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}
    return emojis.get(category, "📦")


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
        r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})', r'([A-Z0-9]{10})/?$',
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


def extract_number(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            return float(nums[0].replace(",", ""))
    except:
        pass
    return 0


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


def get_seller_info(soup):
    seller_name = None
    seller_rating = None
    seller_selectors = [
        "#merchant-info a",
        "[data-feature-name='merchant'] a",
        ".tabular-buybox-text[tabular-attribute-name='Merchant']",
        "#merchant-info",
    ]
    for selector in seller_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and "Amazon" not in text and len(text) > 2:
                seller_name = text
                break
    rating_elem = soup.select_one("[data-feature-name='merchant'] .a-icon-alt")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        match = re.search(r'(\d+)%', text)
        if match:
            seller_rating = int(match.group(1))
    return seller_name, seller_rating


def is_valid_coupon_code(text):
    """Filter out product features and invalid codes"""
    if not text:
        return False
    
    # Skip product features/tech specs
    invalid_keywords = [
        'turbo', 'wash', 'dry', 'spin', 'rpm', 'kg', 'kilo', 'inverter',
        'wifi', 'bluetooth', 'smart', 'sensor', 'motor', 'digital', 'display',
        'touch', 'control', 'mode', 'speed', 'power', 'energy', 'class',
        'dimension', 'size', 'weight', 'capacity', 'volume', 'noise',
        'program', 'function', 'technology', 'system', 'filter', 'brush',
        'battery', 'wireless', 'cable', 'charger', 'adapter', 'remote',
        ' guarantee', 'warranty', 'year', 'month', 'day', 'model', 'series',
        'version', 'generation', 'type', 'color', 'black', 'white', 'silver',
        'gold', 'red', 'blue', 'green', 'new', 'original', 'official',
    ]
    
    text_lower = text.lower()
    for kw in invalid_keywords:
        if kw in text_lower:
            return False
    
    # Must contain at least one letter and one digit, or be all uppercase letters
    has_letter = bool(re.search(r'[a-zA-Z]', text))
    has_digit = bool(re.search(r'\d', text))
    
    # Pure numbers are not coupon codes
    if not has_letter and has_digit:
        return False
    
    # Too short or too long
    if len(text) < 4 or len(text) > 20:
        return False
    
    # Must look like a code (contains uppercase or digits)
    if not re.match(r'^[A-Z0-9]+$', text):
        # Allow some mixed case but mostly uppercase
        if sum(1 for c in text if c.isupper()) < 2 and not has_digit:
            return False
    
    return True


def extract_coupon_details(coupon_text):
    if not coupon_text:
        return None, 0
    
    # Extract code - look for explicit code patterns first
    code = None
    
    # Pattern: "Apply XXXXX" or "Clip XXXXX" or "Code: XXXXX"
    explicit_patterns = [
        r'(?:apply|clip|use|enter)\s+([A-Z0-9]{4,15})',
        r'(?:code|كود|قسيمة)[\s:]+([A-Z0-9]{4,15})',
        r'([A-Z0-9]{5,12})(?:\s*[-–]\s*\d+%)',
    ]
    
    for pattern in explicit_patterns:
        match = re.search(pattern, coupon_text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if is_valid_coupon_code(candidate):
                code = candidate
                break
    
    # If no explicit code, look for standalone codes
    if not code:
        standalone = re.findall(r'\b([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z0-9]{6,12})\b', coupon_text)
        for candidate in standalone:
            if is_valid_coupon_code(candidate):
                code = candidate
                break
    
    # Extract discount percentage
    discount_percent = 0
    percent_match = re.search(r'(\d+)%', coupon_text)
    if percent_match:
        discount_percent = int(percent_match.group(1))
    
    # Extract fixed amount discount
    fixed_discount = 0
    amount_match = re.search(r'(\d+)\s*(?:SAR|ريال)', coupon_text, re.IGNORECASE)
    if amount_match:
        fixed_discount = int(amount_match.group(1))
    
    return code, discount_percent, fixed_discount


def get_all_promos_and_coupons(soup, current_price_num):
    """Extract ALL valid promo codes and coupons"""
    all_coupons = []
    
    # Look in coupon-specific areas
    coupon_selectors = [
        "#couponTextInput",
        "[data-feature-name='coupon']",
        ".couponText",
        "#couponContainer",
        "[id*='coupon']",
        ".promoPriceBlockMessage",
        "[data-a-expander-name='couponSecondaryView']",
        ".couponCheckbox",
        ".savingsPercentage",
        ".a-color-price",
    ]
    
    for selector in coupon_selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and any(word in text.lower() for word in ['coupon', 'خصم', 'discount', 'save', 'وفّر', 'قسيمة', 'كوبون', 'clip', 'apply', 'promo', 'كود', 'offer', 'عرض', 'extra']):
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 3:
                    all_coupons.append(text)
    
    # Search page text for promo patterns with actual codes
    page_text = soup.get_text()
    promo_patterns = [
        r'(?:apply|clip|use|enter)\s+([A-Z]{3,}\d{2,})\s*(?:to save|to get|for|للحصول)',
        r'(?:promo\s*code|كود\s*الخصم|كوبون)[\s:]+([A-Z0-9]{4,12})',
        r'([A-Z]{4,}\d{2,4})\s*[-–]\s*save\s*\d+%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*\d+%\s*off',
    ]
    for pattern in promo_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str) and is_valid_coupon_code(match):
                all_coupons.append(f"Code {match}")
            elif isinstance(match, tuple) and match[0] and is_valid_coupon_code(match[0]):
                all_coupons.append(f"Code {match[0]}")
    
    all_coupons = list(set(all_coupons))
    
    coupons_data = []
    for coupon_text in all_coupons:
        code, percent, fixed = extract_coupon_details(coupon_text)
        if code and (percent > 0 or fixed > 0):
            final_price = int(current_price_num)
            if percent > 0 and current_price_num > 0:
                discount_amount = (current_price_num * percent) / 100
                final_price = int(current_price_num - discount_amount)
            elif fixed > 0 and current_price_num > 0:
                final_price = int(current_price_num - fixed)
                if final_price < 0:
                    final_price = 0
                percent = int((fixed / current_price_num) * 100)
            
            coupons_data.append({
                "text": coupon_text,
                "code": code,
                "percent": percent,
                "fixed": fixed,
                "final_price": final_price
            })
    
    # Remove duplicates by code
    seen_codes = set()
    unique_coupons = []
    for c in coupons_data:
        key = c["code"].upper()
        if key not in seen_codes:
            seen_codes.add(key)
            unique_coupons.append(c)
    
    # Sort by discount percentage (highest first)
    unique_coupons.sort(key=lambda x: x["percent"], reverse=True)
    
    return unique_coupons


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
            seller_name, seller_rating = get_seller_info(soup)
            
            current_price_num = extract_number(price) if price else 0
            all_coupons = get_all_promos_and_coupons(soup, current_price_num)
            
            if price:
                arabic_title = smart_arabic_title(full_title)
                return {
                    "name": arabic_title,
                    "price": price,
                    "old_price": old_price,
                    "image": image,
                    "seller_name": seller_name,
                    "seller_rating": seller_rating,
                    "all_coupons": all_coupons,
                    "current_price_num": current_price_num,
                }
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    return None


def generate_post(product_data, original_url):
    name = product_data["name"]
    price = product_data["price"]
    old_price = product_data["old_price"]
    all_coupons = product_data["all_coupons"]
    current_price_num = product_data["current_price_num"]
    
    category = detect_product_category(name)
    gender = detect_product_gender(name)
    
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    old_num = extract_number(old_price) if old_price else 0
    
    # Build context for AI
    context_parts = []
    
    if clean_old and old_num > current_price_num:
        context_parts.append(f"السعر السابق {clean_old} والسعر الحالي {clean_current}")
    
    if all_coupons:
        for c in all_coupons[:2]:
            context_parts.append(f"كود {c['code']} خصم {c['percent']}% يصير بـ {c['final_price']} ريال")
    
    context = " | ".join(context_parts)
    
    # AI generates dramatic opening sentence
    opening = generate_ai_sentence(name, category, gender, context)
    
    emoji = get_category_emoji(category)
    
    parts = []
    parts.append(opening)
    parts.append(f"{emoji} {name}")
    
    # Prices
    price_lines = []
    if clean_old and old_num > current_price_num:
        price_lines.append(f"❌ السعر السابق: {clean_old}")
    price_lines.append(f"✅ السعر الحالي: {clean_current}")
    parts.append("\n".join(price_lines))
    
    # Valid coupons only
    if all_coupons:
        for coupon in all_coupons[:2]:
            if coupon["final_price"] > 0 and coupon["final_price"] != int(current_price_num):
                parts.append(f"🎟️ مع كود {coupon['code']} (خصم {coupon['percent']}%) يطلع بـ {coupon['final_price']} ريال 🔥")
            elif coupon["percent"] > 0:
                parts.append(f"🎟️ كود {coupon['code']} (خصم {coupon['percent']}%)")
    
    parts.append(f"رابط الشراء 👇🏻\n{original_url}")
    
    return "\n\n".join(parts)


def generate_ai_sentence(product_name, category, gender, context):
    """AI generates dramatic/exaggerated opening sentence"""
    
    gender_hint = ""
    if gender == "women":
        gender_hint = "المنتج نسائي، وجه الجملة للبنات بأسلوب تهويلي"
    elif gender == "men":
        gender_hint = "المنتج رجالي، وجه الجملة للرجال بأسلوب تهويلي"
    else:
        gender_hint = "المنتج للجنسين، اكتب بأسلوب تهويلي عام"
    
    # Random dramatic style
    styles = [
        "افتتح بأسلوب تهويلي صاروخي (مثل: 'انفجار سعر!'، 'صدمة!'، 'مستحيل!'، 'تخيلوا!')",
        "افتتح بأسلوب صياد لقى كنز (مثل: 'غنيمة العمر!'، 'صفقة تاريخية!'، 'هجمة!'، 'صطولة!')",
        "افتتح بأسلوب مفاجأة صادمة (مثل: 'صدمووو!'، 'تبي تصدق!'، 'عقلك راح ينفجر!'، 'لا يفوتك!')",
        "افتتح بأسلوب تحدي (مثل: 'جربوا تصدقوا!'، 'أقوى صفقة!'، 'ما راح تلقى مثلها!'، 'فرصة وحيدة!')",
        "افتتح بأسلوب فزعة (مثل: 'عاجل!'، 'هيّا!'، 'بسرعة!'، 'الحين الحين!'، 'قبل ما ينتهي!')",
    ]
    chosen_style = random.choice(styles)
    
    prompt = f"""أنت كاتب محتوى سعودي خليجي محترف في قناة تليجرام "صيدات وصفقات" للتسويق بالعمولة.
اكتب جملة افتتاحية قصيرة جداً (سطر واحد فقط، 4-10 كلمات كحد أقصى) باللهجة السعودية الخليجية.

🔹 قواعد مهمة:
- الجملة لازم تكون مختصرة جداً (تنفع تغريدة تويتر)
- استخدم إيموجي (2-3 إيموجي) في الجملة نفسها
- الجملة لازم تكون بأسلوب تهويلي حماسي صادم يشد العين فوراً
- أسلوب التهويل: صدمة، انفجار، غنيمة، صفقة خرافية، فرصة مجنونة، توفير جنوني
- بلهجة سعودية خليجية كريمة
- ❌ ممنوع: "ياجدعان", "ياجماعة", "يالله يا شباب", "حياكم", "يالا"
- ❌ ممنوع أي أمثلة جاهزة أو نمط ثابت
- ❌ ممنوع تكرار نفس الجملة أو نفس الأسلوب
- ❌ ممنوع استخدام كلمة "صيدة" أو "لازم تشوفها"
- كل مرة اكتب جملة مختلفة تماماً بناءً على المنتج والسياق
- الأسلوب المطلوب: {chosen_style}

🔹 {gender_hint}

🔹 المنتج: {product_name}
🔹 الفئة: {category}
🔹 المعلومات المتاحة: {context}

اكتب جملة واحدة فقط بدون أي مقدمة:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت كاتب محتوى سعودي خليجي في قناة 'صيدات وصفقات'. تكتب جمل افتتاحية قصيرة بأسلوب تهويلي صادم. أسلوبك: صدمة، انفجار، غنيمة، صفقة خرافية. كل مرة تكتب جملة مختلفة تماماً. ممنوع الأمثلة الجاهزة. ممنوع التكرار. ممنوع استخدام كلمة 'صيدة' أو 'لازم تشوفها'."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.99,
            "max_tokens": 40
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
            
            vulgar_calls = ["ياجدعان", "ياجماعه", "ياجماعة", "يالله يا", "حياكم", "يالا", "يالله"]
            for vulgar in vulgar_calls:
                if vulgar in sentence.lower().replace(" ", ""):
                    return generate_fallback_sentence(category)
            
            return sentence
                
    except Exception as e:
        print(f"Groq error: {e}")
    
    return generate_fallback_sentence(category)


def generate_fallback_sentence(category):
    """Dramatic fallback sentences"""
    fallbacks = [
        "💥 انفجار سعر مجنون! 🔥",
        "🎯 غنيمة العمر وصلت! ⚡️",
        "💰 صفقة تاريخية بانتظارك! 🚀",
        "🔥 صدمة سعر لا تُصدق! 💎",
        "⚡️ فرصة مجنونة قبل تفوت! 💸",
        "💎 كنز ببلاش تقريباً! 🏆",
        "🚀 هجمة أسعار لا تُفوت! 🔥",
        "💸 توفير جنوني شفتوه! ⚡️",
        "🔥 مستحيل تلقى مثلها! 💰",
        "⚡️ عاجل! صفقة صطورة! 🎯",
    ]
    return random.choice(fallbacks)


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

        post = generate_post(product, original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post)
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
