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
            if text and len(text) > 2:
                seller_name = text
                break
    rating_elem = soup.select_one("[data-feature-name='merchant'] .a-icon-alt")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        match = re.search(r'(\d+)%', text)
        if match:
            seller_rating = int(match.group(1))
    return seller_name, seller_rating


def get_product_rating(soup):
    rating = None
    review_count = None
    rating_elem = soup.select_one("#acrPopover .a-icon-alt")
    if not rating_elem:
        rating_elem = soup.select_one("[data-hook='rating-out-of-text']")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        m = re.search(r'([\d.]+)', text)
        if m:
            rating = m.group(1)
    review_elem = soup.select_one("#acrCustomerReviewText")
    if not review_elem:
        review_elem = soup.select_one("[data-hook='total-review-count']")
    if review_elem:
        text = review_elem.get_text(strip=True)
        m = re.search(r'([\d,]+)', text)
        if m:
            review_count = m.group(1).replace(",", "")
    return rating, review_count


def get_stock_info(soup):
    stock_text = None
    selectors = [
        "#availability span",
        ".a-color-price.a-text-bold",
        "#outOfStock",
        "[data-feature-name='availability']",
    ]
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and any(w in text.lower() for w in ['left', 'متبقي', 'stock', 'soon', 'قريباً', 'limited', 'only']):
                stock_text = text
                break
    return stock_text


def extract_coupon_info(text):
    if not text:
        return None, 0
    percent = 0
    percent_match = re.search(r'(\d+)%', text)
    if percent_match:
        percent = int(percent_match.group(1))
    code = None
    code_match = re.search(r'\b([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z]{4,})\b', text)
    if code_match:
        candidate = code_match.group(1)
        if len(candidate) >= 4 and len(candidate) <= 15 and re.search(r'[A-Z]', candidate):
            code = candidate
    if not code and percent > 0:
        code = f"خصم {percent}%"
    return code, percent


def get_all_coupons(soup, current_price_num):
    found_coupons = []
    selectors = [
        "#couponTextInput", "[data-feature-name='coupon']", ".couponText",
        "#couponContainer", "[id*='coupon']", ".promoPriceBlockMessage",
        "[data-a-expander-name='couponSecondaryView']", ".couponCheckbox",
        ".savingsPercentage", ".a-color-price",
    ]
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:
                code, percent = extract_coupon_info(text)
                if code and percent > 0:
                    final_price = int(current_price_num - (current_price_num * percent / 100))
                    found_coupons.append({"code": code, "percent": percent, "final_price": final_price, "text": text})

    page_text = soup.get_text()
    explicit_patterns = [
        r'(?:apply|clip|use|enter|استخدم|طبّق)\s+([A-Z0-9]{4,12})\s*(?:to save|للحصول|for)\s*(\d+)%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*save\s*(\d+)%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*(\d+)%\s*off',
        r'(?:promo\s*code|كود\s*الخصم|كوبون)[\s:]+([A-Z0-9]{4,12})',
    ]
    for pattern in explicit_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                code, percent = match[0], int(match[1]) if str(match[1]).isdigit() else 0
            else:
                code, percent = match, 0
            if code and len(code) >= 4 and percent > 0:
                final_price = int(current_price_num - (current_price_num * percent / 100))
                found_coupons.append({"code": code.upper(), "percent": percent, "final_price": final_price, "text": f"{code} خصم {percent}%"})

    seen = {}
    unique = []
    for c in found_coupons:
        key = c["code"].upper()
        if key not in seen:
            seen[key] = True
            unique.append(c)
    unique.sort(key=lambda x: x["percent"], reverse=True)
    return unique


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
            rating, review_count = get_product_rating(soup)
            stock_info = get_stock_info(soup)
            current_price_num = extract_number(price) if price else 0
            all_coupons = get_all_coupons(soup, current_price_num)

            if price:
                arabic_title = smart_arabic_title(full_title)
                return {
                    "name": arabic_title,
                    "full_title": full_title,
                    "price": price,
                    "old_price": old_price,
                    "image": image,
                    "seller_name": seller_name,
                    "seller_rating": seller_rating,
                    "rating": rating,
                    "review_count": review_count,
                    "stock_info": stock_info,
                    "all_coupons": all_coupons,
                    "current_price_num": current_price_num,
                }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    return None


# ========== قوالب الجمل الافتتاحية الأنيقة والراقية ==========
HEADLINE_TEMPLATES = {
    "electronics": [
        "✨ من بين آلاف الخيارات، هذي الصفقة تبرق وتلمع بفرادة — سعر {price} يجعلك تتوقف وتفكر: وش اللي يمنعني الحين؟ 🔥",
        "🌟 يا هلا بـ الصفقة اللي تستاهل كل ثانية تفكير — {discount}% خصم حقيقي، مو مجرد رقم على ورقة 💎",
        "⚡️ في عالم التقنية السريع، نادر تلقى توازن بين الجودة العالية والسعر المعقول — هالمنتج يقدم لك الاثنين بـ {price} 🎯",
        "🔥 يقولون الفرصة ما تدق الباب مرتين، بس هالمرة دقت بقوة — جهاز إلكتروني بمواصفات تنافسية بسعر {price} يستاهل التجربة 🚀",
        "💡 ذكاء الاختيار مو بس في المنتج، ذكاء الاختيار في التوقيت — والتوقيت الحين يصرخ: اشتري! {discount}% خصم ⚡️",
        "📱 بين كل الإعلانات اللي تمر قدامك، وقف عند هالصفقة — جهاز يستاهل ثقتك بسعر {price} ما يخيب ظنك 🌟",
        "🎯 التميز مو دائماً يجي بسعر باهظ — أحياناً يجي بـ {price} مع خصم {discount}% يثبتلك كلامي 💎",
        "⚡️ سرعة التقنية تتطلب قرار سريع — وهالقرار يبدأ بـ {price} وينتهي بابتسامة رضا 🔥",
        "💻 للمحترفين والهواة على حد سواء — هالجهاز يفتح لك أبواب الإبداع بسعر {price} يناسب كل الميزانيات 🌟",
        "🔋 قوة تدوم، أداء يبهر، وسعر {price} يخليك تتساءل: ليش تأخرت؟ ⚡️",
        "🎧 جودة صوت تغمرك، سعر {price} يبهرك — هالسماعة مو بس تسمع، تخليك تحس بكل نغمة 💎",
        "📡 اتصال سريع، أداء ثابت، وسعر {price} يثبت إن التميز مو حكر على الأغلى 🎯",
        "💾 مساحة تكفي، سرعة تبهر، وسعر {price} يخليك تفكر في مشتريات ثانية ⚡️",
        "🖥️ وضوح يخطف العين، أداء يخطف القلب، وسعر {price} يخطف محفظتك بذكاء 🔥",
        "⌚ أناقة تتجسد على معصمك، ذكاء يتجسد في كل إشعار — والسعر؟ {price} يستاهل الاحتفال 🌟",
        "📺 شاشة تغمرك في عالمها، صوت يحيطك من كل زاوية — والسعر {price} يحيط محفظتك بالراحة 💎",
        "🔌 شاحن سريع يعيد الحياة لأجهزتك، وسعر {price} يعيد الأمل لميزانيتك ⚡️",
        "💡 لمبة ذكية تنوّر بيتك، وسعر {price} ينوّر يومك بقرار ذكي 🎯",
    ],
    
    "fashion_men": [
        "👔 الأناقة الرجالية مو بس في الملبس، في الثقة اللي يمنحك إياها — وهالطقم بـ {price} يمنحك الاثنين معاً 🔥",
        "🕶️ بين كل الخيارات اللي تمر قدامك، وقف عند هالقطعة — طلّة تفرض احترامك بسعر {price} يفرض تقديرك 💎",
        "👞 الحذاء الرجالي الصح يمشي بك كل الطرقات بثقة — وهذا بـ {price} يمشي بك نحو التوفير أيضاً ⚡️",
        "⌚ الوقت ثمين، والساعة اللي ترتديها تثبتلك كلامي — ساعة بـ {price} تستاهل كل دقيقة فيها 🌟",
        "👖 الجينز الصح يدوم معك سنين، والسعر {price} يدوم في ذاكرتك كصفقة ناجحة 🔥",
        "🧥 الشتوي يجي بثقله، بس هالجاكيت يجي بخفة في السعر — {price} مع خصم {discount}% يدفي القلب 💎",
        "👟 حذاء رياضي يركض بك نحو أهدافك، وسعر {price} يركض بك نحو التوفير ⚡️",
        "🎒 شنطة ظهر تحمل أحلامك وأدواتك، وسعر {price} يحمل محفظتك من العبء الزايد 🌟",
        "👔 القميص الأنيق يفتح لك أبواباً كانت مسكرة — بـ {price} يفتح لك باب التوفير أيضاً 🔥",
        "🧢 كاب يغطي راسك من حرارة الشمس، وسعر {price} يغطي جيبك من حرارة الغلاء 💎",
        "👜 محفظة جلدية ت aging معك بكرامة، وسعر {price} ي aging في ذاكرتك كأحسن صفقة ⚡️",
        "🧣 وشاح يدفي عنقك في البرد، وخصم {discount}% يدفي قلبك من فرحة التوفير 🌟",
        "👖 بنطلون رياضي يريحك في الجيم، وسعر {price} يريحك في المحفظة 🔥",
        "🥾 بوت يدوس على كل الطرقات الوعرة، وسعر {price} يدوس على كل الأسعار المنافسة 💎",
        "🕴️ طقم كامل يخليك جاهز لأي مناسبة، وسعر {price} يخليك جاهز لأي صفقة قادمة ⚡️",
    ],
    
    "fashion_women": [
        "👗 الفستان الأنيق يحكي قصة قبل ما تتكلمي — وهذا بـ {price} يحكي قصة ذكاء اختيارك 🔥",
        "👜 الشنطة النسائية الصح تكمل إطلالتك وتكمل ثقتك — وهذه بـ {price} تكمل ميزانيتك بسعادة 💎",
        "💄 المكياج الجيد يزين الوجه، بس المكياج بسعر {price} يزين اليوم كله ⚡️",
        "👠 الكعب العالي يرفعك فوق، والسعر المنخفض {price} يرفعك أعلى — هالتوازن نادر 🌟",
        "🧕 العباية/الشيلة تسترك وتزينك، وسعر {price} يستر ميزانيتك ويزينها 🔥",
        "👡 صندل صيفي يريح قدمك، وسعر {price} يريح بالك من القلق 💎",
        "💍 إكسسوار يلمع زي نجمة في سمائك، وسعر {price} يلمع زي فرصة ما تتكرر ⚡️",
        "🎀 تسريحة شعر تكمل جمالك، وسعر {price} يكمل فرحتك بالشراء 🌟",
        "👛 محفظة صغيرة في الحجم، كبيرة في التوفير — بـ {price} تثبت إن الأشياء الحلوة تجي بأحجام مدروسة 🔥",
        "🧥 كوت شتوي يدفي جسمك، وخصم {discount}% يدفي قلبك من الفرحة 💎",
        "👖 بنطلون يبرر خطوط جسمك، وسعر {price} يبرر قرارك الشرائي بذكاء ⚡️",
        "💃 تنورة ترقص معك في كل خطوة، وسعر {price} يرقص في ذاكرتك كصفقة عمر 🌟",
        "🧴 عطر نسائي يفوح في كل مكان تروحينه، وسعر {price} يفوح في محفظتك كتوفير حقيقي 🔥",
        "👙 لانجري أنيق يمنحك ثقة خفية، وسعر {price} يمنحك فرحة ظاهرة 💎",
        "🎒 حقيبة يد للمرأة العصرية — بـ {price} تثبت إن الأناقة مو حكر على الغالي ⚡️",
    ],
    
    "beauty_men": [
        "🧔 الرجل المهتم بنظافته مهتم بتفاصيل حياته — وهالمنتج بـ {price} يهتم بميزانيتك أيضاً 🔥",
        "💈 حلاقة نظيفة تبدأ بمنتج نظيف، وسعر {price} ينظف ميزانيتك من الغلاء 💎",
        "🧴 لوشن رجالي يترطب بشرتك، وسعر {price} يترطب قلبك من فرحة التوفير ⚡️",
        "🪒 ماكينة حلاقة تفصلك عن المظهر الباهت، وسعر {price} يفصلك عن الأسعار الباهظة 🌟",
        "👔 عطر رجالي يثبت حضورك في أي مكان، وسعر {price} يثبت ذكاءك في كل مكان 🔥",
        "🧼 صابون/شامبو رجالي ينظف وينعش، وسعر {price} ينظف ميزانيتك وينعشها 💎",
        "💪 عناية بالبشرة للرجل الطموح — بـ {price} تثبت إن العناية مو حكر على النساء ⚡️",
        "🌿 زيت طبيعي للرجال اللي يقدرون الأصالة — وسعر {price} يقدر ميزانيتك بأصالة 🌟",
        "🎩 كريم ترتيب يرتب بشرتك، وسعر {price} يرتب أولوياتك المالية 🔥",
        "🧊 مزيل عرق يبردك في الحر، وخصم {discount}% يبرد جيبك من القلق 💎",
    ],
    
    "beauty_women": [
        "💅 طلاء أظافر يلمع زي لمعان عينك لما تشوفين السعر — {price} يستاهل كل نظرة ⚡️",
        "🧖‍♀️ كريم بشرة يخليك تتأملين في مرآتك بسعادة، وسعر {price} يخليك تتأملين في محفظتك براحة 🌟",
        "💋 أحمر شفاه بـ {price}؟! يا ليت كل القرارات الحلوة تجي بهالسهولة والجمال 🔥",
        "🌸 عطر نسائي يفوح بأريج الأناقة، وسعر {price} يفوح بأريج الذكاء في الاختيار 💎",
        "🧴 شامبو/بلسم يقوي شعرك من الجذور، وسعر {price} يقوي ميزانيتك من الأساس ⚡️",
        "✨ سيروم يبرق وجهك بنضارة، وسعر {price} يبرق يومك بفرحة 🌟",
        "🎀 ماسك وجه بـ {price}؟! يستاهل كل دقيقة استرخاء تمنحك إياها 🔥",
        "🌺 زيت عطري يهدي أعصابك بعد يوم طويل، وسعر {price} يهدي قلبك من توتر الميزانية 💎",
        "💄 مجموعة مكياج كاملة بسعر قطعة واحدة — {price} يثبت إن الجمال مو بس للأغنياء ⚡️",
        "🛁 منتج استحمام يدللك كأنك في سبا، وسعر {price} يدللك كأنك محظوظة 🌟",
        "👁️ ماسكرا/آيلاينر يكحل عينك بجاذبية، وسعر {price} يكحل محفظتك بالتوفير 🔥",
        "🧼 غسول وجه نسائي ينظف بعمق، وسعر {price} ينظف ميزانيتك بذكاء 💎",
        "💆‍♀️ كريم ليلي يشتغل وأنت نايمة، وخصم {discount}% يشتغل لمصلحتك وأنت مرتاحة ⚡️",
        "🌙 عطر ليلي يضفي سحراً على لياليك، وسعر {price} يضفي سحراً على ميزانيتك 🌟",
        "✨ بودرة تثبت المكياج طوال اليوم، وسعر {price} يثبت إن قرارك كان صح 🔥",
    ],
    
    "home": [
        "🏠 البيت اللي يعكس ذوقك يبدأ باختيارات ذكية — وهالمنتج بـ {price} يعكس ذكاءك بالكامل 💎",
        "🛋️ كنبة/أثاث يستقبل ضيوفك بكرامة، وسعر {price} يستقبل ميزانيتك بترحيب ⚡️",
        "🍳 جهاز مطبخ يختصر عليك الوقت والجهد، وخصم {discount}% يختصر عليك القلق 🌟",
        "❄️ مكيف/ثلاجة يبرد حرارة الصيف، وسعر {price} يبرد حرارة القلق على الميزانية 🔥",
        "🧹 مكنسة/غسالة تنظف بيتك بعمق، وسعر {price} ينظف ميزانيتك بذكاء 💎",
        "🛏️ سرير/مرتبة ينومك على أحلام هنيئة، وسعر {price} ينومك مرتاح من القلق ⚡️",
        "💡 إضاءة تنوّر زوايا بيتك، وسعر {price} ينوّر زوايا يومك بفرحة 🌟",
        "🚿 سخان/دش يدفيك في البرد، وسعر {price} يدفي محفظتك من الصدمة 🔥",
        "🍽️ طقم مطبخ يجمع العائلة على مائدة واحدة، وسعر {price} يجمع الجودة والتوفير 💎",
        "🪴 ديكور/نبتة تضفي حياة على بيتك، وسعر {price} يضفي حياة على ميزانيتك ⚡️",
        "🧺 منظم/خزانة يرتب فوضى بيتك، وسعر {price} يرتب فوضى ميزانيتك 🌟",
        "🔥 مدفأة/فرن يدفيك في الشتاء، وخصم {discount}% يدفي قلبك في كل فصل 🔥",
        "🚪 باب/ستارة يفصل بينك وبين العالم، وسعر {price} يفصل بينك وبين الغلاء 💎",
        "🪑 كرسي/طاولة تجلسك مرتاح، وسعر {price} يجلس ميزانيتك مرتاحة ⚡️",
        "🌡️ مكيف/دفاية يوازن حرارة بيتك، وسعر {price} يوازن حرارة ميزانيتك 🌟",
    ],
    
    "sports": [
        "💪 القوة الحقيقية تبدأ بقرار — قرار الاعتناء بجسمك، وقرار الشراء بذكاء بـ {price} 🔥",
        "🏋️ دامبل/جهاز رياضي يرفعك فوق، وسعر {price} يرفع ميزانيتك فوق أيضاً 💎",
        "🏃 حذاء رياضي يجري بك نحو أهدافك، وخصم {discount}% يجري بك نحو التوفير ⚡️",
        "🧘 حصيرة يوغا تريح جسمك وعقلك، وسعر {price} يريح محفظتك من الضغط 🌟",
        "🚴 دراجة/جهاز كارديو يقوي قلبك، وسعر {price} يقوي قرارك الشرائي 🔥",
        "⚽ كرة/معدات رياضية تسجل هدف في اللعب، وسعر {price} يسجل هدف في التوفير 💎",
        "🥊 قفازات ملاكمة تضرب الغلاء ضربة قاضية، وسعر {price} يضرب المنافسين ⚡️",
        "🏊 معدات سباحة تغوص بك في عالم الماء، وسعر {price} يغوص بك في عالم التوفير 🌟",
        "🎽 ملابس رياضية تتعبك في التمرين، وسعر {price} يريحك في المحفظة 🔥",
        "🥤 شيكر/زجاجة رياضية ترافقك في كل جلسة، وسعر {price} يرافقك في كل صفقة 💎",
        "🏸 مضرب رياضي يرد كرة الخصم، وسعر {price} يرد كرة الغلاء ⚡️",
        "🧗 معدات تسلق تصعد بك للقمة، وسعر {price} يصعد بك لمستوى جديد من الذكاء 🌟",
        "🏆 جهاز تمرين منزلي يمنحك بطولة يومية، وسعر {price} يمنحك بطولة التوفير 🔥",
        "⛹️ كرة سلة/قدم تجمع الأصدقاء، وسعر {price} يجمع الجودة والسعر المناسب 💎",
        "🤸 إكسسوار رياضي يطوّيك جسدياً، وخصم {discount}% يطوّيك مالياً ⚡️",
    ],
    
    "general": [
        "✨ من بين كل ما يمر أمام عينك اليوم، وقف عند هالصفقة — فرصة نادرة بـ {price} تستاهل كل ثانية تفكير 🔥",
        "🌟 يقولون الذهب يلمع دائماً، بس هالصفقة بـ {price} تلمع أكثر — خصم {discount}% يثبت كلامي 💎",
        "⚡️ في زحمة العروض والإعلانات، نادر تلقى صفقة حقيقية — هذي واحدة منهم، وسعر {price} يكفي كدليل ⚡️",
        "🔥 الفرصة الحقيقية ما تجي مرتين، وإذا جت المرة الثانية فهي مو فرصة — هذي المرة الأولى بـ {price}، لا تفوتها 🌟",
        "💎 الجودة العالية والسعر المعقول نادراً ما يجتمعان — بس هالمرة اجتمعوا في صفقة واحدة بـ {price} 🔥",
        "🎯 الذكاء مو بس في اختيار المنتج، الذكاء في اختيار التوقيت — والتوقيت الحين يصرخ: {price} مع خصم {discount}% 💎",
        "🌊 موجة من التوفير جاية بقوة، وسعر {price} يثبت إن الموجة ما راح تمر بدون ما تستفيد منها ⚡️",
        "🏆 البطولة الحقيقية مو في الملعب، في المحفظة — وهالصفقة بـ {price} تمنحك لقب بطل التوفير 🌟",
        "😤 مستحيل؟! مو معقول؟! بهالحق؟! — كل هالكلمات تطلع من فمك لما تشوف السعر {price} 🔥",
        "🚀 طار السعر لتحت بشكل جنوني، ومحفظتك تستعد للإقلاع — {discount}% خصم يمنحك تذكرة الرحلة 💎",
        "👀 شوفوا بأعينكم، اسمعوا بآذانكم، احسوا بقلوبكم — هالصفقة بـ {price} تستاهل كل حاسة ⚡️",
        "🍀 حظك اليوم مفتوح على مصراعيه، وسعر {price} يثبت إن بختك في التسوق قوي 🌟",
        "🎉 يا هلا بالفرحة! يا هلا بالصفقة! يا هلا بـ {price} اللي يسعد القلب ويريح المحفظة 🔥",
        "🦁 أسد الصفقات هنا، يمشي بثقة ويختار بذكاء — بـ {price} يثبت إن الملكية مو حكر على الأغلى 💎",
        "🎵 لحن التوفير يعزف بأجمل إيقاع، وسعر {price} يكمل السيمفونية بأريج الفرحة ⚡️",
        "🏠 للبيت، للمكتب، لنفسك، لعائلتك — هالمنتج بـ {price} يستاهل كل زاوية في حياتك 🌟",
        "💪 قوية، ثابتة، موثوقة — صفقة بـ {price} ترفع هامتك في أي مجلس 🔥",
        "🎮 جيم أوفر للغلاء، ليفل أب للتوفير — {price} مع خصم {discount}% يفتحلك مراحل جديدة 💎",
        "🌙 ليلة هادئة، قرار ذكي، وسعر {price} ينور طريقك نحو الرضا ⚡️",
        "🧠 عقلية الملياردير بميزانية الموظف — هالصفقة بـ {price} تثبت إن الذكاء مو بس للأغنياء 🌟",
    ],
}


def generate_contextual_headline(product_name, category, gender, context, discount_pct):
    """
    تبني جملة افتتاحية راقية وأنيقة مربوطة بالمنتج، باللهجة السعودية الخليجية
    """
    # تحديد الفئة الفرعية
    if category == "fashion":
        subcategory = f"fashion_{gender}" if gender in ["men", "women"] else "general"
    elif category == "beauty":
        subcategory = f"beauty_{gender}" if gender in ["men", "women"] else "general"
    else:
        subcategory = category if category in HEADLINE_TEMPLATES else "general"
    
    # اختيار قائمة القوالب
    templates = HEADLINE_TEMPLATES.get(subcategory, HEADLINE_TEMPLATES["general"])
    
    # اختيار قالب عشوائي
    template = random.choice(templates)
    
    # استخراج السعر من السياق
    price_match = re.search(r'(\d+)\s*ريال', context)
    price = price_match.group(1) + " ريال" if price_match else "رخيص"
    
    # ملء القالب
    headline = template.format(
        discount=discount_pct,
        price=price
    )
    
    # التأكد من الطول المناسب
    if len(headline) > 120:
        # نختصر الجملة لو طويلة جداً
        shorter_templates = [
            "✨ صفقة نادرة بـ {price} تستاهل كل ثانية تفكير 🔥",
            "🌟 فرصة حقيقية بـ {price} مع خصم {discount}% 💎",
            "⚡️ سعر {price} يثبت إن التميز مو حكر على الأغلى ⚡️",
        ]
        headline = random.choice(shorter_templates).format(price=price, discount=discount_pct)
    
    return headline


def generate_ai_headline(product_name, category, gender, context, discount_pct):
    """
    AI generates a creative multi-line opening block in pure Saudi dialect.
    Highly varied — never repeats the same pattern twice.
    """
    gender_hint = ""
    if gender == "women":
        gender_hint = "المنتج نسائي — اكتب بأسلوب يخاطب البنات والنساء السعوديات."
    elif gender == "men":
        gender_hint = "المنتج رجالي — اكتب بأسلوب يخاطب الشباب والرجال السعوديين."
    else:
        gender_hint = "المنتج للجنسين — اكتب بأسلوب عام."

    discount_hint = f"الخصم {discount_pct}% — ركّز عليه في الجملة." if discount_pct > 0 else ""

    # Rich pool of styles — one picked randomly each call
    styles = [
        'افتح بـ "✨" + جملة وصف أنيقة للمنتج + صدمة عن السعر',
        'افتح بأسلوب القصة: "🌟 من بين آلاف الخيارات..." + وصف المنتج + السعر',
        'افتح بـ "💎" + جملة عن ندرة الصفقة + وصف المنتج المختصر',
        'افتح بأسلوب التأمل: "⚡️ في زحمة العروض..." + المنتج + السعر المجنون',
        'افتح بـ "🔥" + جملة تهويل راقية + "ما يتكرر" + المنتج',
        'افتح بأسلوب الحكمة: "🏆 الذكاء مو بس..." + المنتج + السعر',
        'افتح بـ "🌊" + جملة عن موجة التوفير + المنتج + السعر',
        'افتح بأسلوب التحدي: "😤 مستحيل؟!" + المنتج + "بهالسعر؟!"',
        'افتح بـ "👀" + جملة عن الحواس + المنتج + السعر',
        'افتح بأسلوب الفرحة: "🎉 يا هلا..." + المنتج + السعر + "اللي يسعد"',
        'افتح بـ "🦁" + جملة عن القوة والثقة + المنتج + السعر',
        'افتح بأسلوب الليل: "🌙 ليلة هادئة..." + قرار ذكي + المنتج + السعر',
        'افتح بـ "🧠" + جملة عن الذكاء + المنتج + السعر + "يثبت"',
        'افتح بأسلوب الموسيقى: "🎵 لحن التوفير..." + المنتج + السعر + "يكمل"',
        'افتح بـ "🏠" + جملة عن الزوايا + المنتج + السعر + "يستاهل"',
    ]
    chosen_style = random.choice(styles)

    # Extra spice words to encourage variety
    saudi_words = random.sample([
        "صطولة", "صيدة", "غنيمة", "هجمة", "لحقوا", "شفتوا", "ما يصدق",
        "والله العظيم", "بالحق", "زبالة السعر", "تهبيلة", "مستحيل", "ما يطيح",
        "طار السعر", "دفعة واحدة", "قبل ما يخلص", "اللي فاته فاته",
        "فرصة نادرة", "صفقة العمر", "ذكاء اختيار", "قرار حكيم", "تميز بلا حدود",
    ], k=3)

    prompt = f"""أنت كاتب محتوى سعودي خليجي راقي لقناة تلغرام "صيدات وصفقات".

مهمتك: اكتب جملة افتتاحية واحدة فقط، متوسطة الطول (15-25 كلمة)، باللهجة السعودية الخالصة، أنيقة وراقية وتهويلية تشد العين فوراً.

🎯 الأسلوب المطلوب لهذه المرة:
{chosen_style}

🌶️ كلمات سعودية تقدر تستخدمها (اختر منها أو اخترع غيرها):
{' — '.join(saudi_words)}

📌 قواعد صارمة:
- اللهجة سعودية خليجية 100% (مو مصرية، مو شامية)
- استخدم 2-3 إيموجي داخل الجملة
- جملة واحدة فقط، بدون نقطة في النهاية
- ❌ ممنوع: "ياجدعان"، "ياجماعة"، "يالا"، "حياكم"، "يسلموا"
- ❌ ممنوع تكرار نفس البداية مرتين
- ✅ كل مرة أسلوب مختلف تماماً بناءً على المنتج
- ✅ الأسلوب راقي وأنيق — مو صارخ ولا مبتذل

{gender_hint}
{discount_hint}

المنتج: {product_name}
الفئة: {category}
السياق: {context}

اكتب الجملة مباشرة الآن بدون أي مقدمة أو تفسير:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "أنت كاتب محتوى سعودي خليجي محترف متخصص في التسويق بالعمولة على تلغرام. "
                        "أسلوبك: راقي، أنيق، تهويلي بذوق، لهجة سعودية خالصة. "
                        "كل جملة تكتبها مختلفة تماماً عن السابقة. "
                        "ممنوع التكرار، ممنوع اللهجات الأخرى، ممنوع الكلمات المبتذلة."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 1.0,
            "max_tokens": 80,
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

            forbidden = ["ياجدعان", "ياجماعه", "ياجماعة", "يالله يا", "حياكم", "يالا"]
            for f in forbidden:
                if f in sentence.replace(" ", ""):
                    return generate_contextual_headline(product_name, category, gender, context, discount_pct)

            return sentence

    except Exception as e:
        print(f"Groq error: {e}")

    # لو فشل Groq، نرجع للجملة المربوطة بالمنتج
    return generate_contextual_headline(product_name, category, gender, context, discount_pct)


def _fallback_headline(category):
    """احتياطي فقط — نادراً ما يستخدم"""
    general = HEADLINE_TEMPLATES.get("general", [])
    if general:
        template = random.choice(general)
        return template.format(discount="🔥", price="رخيص")
    return "✨ من بين كل ما يمر أمام عينك، وقف عند هالصفقة — فرصة نادرة تستاهل كل ثانية تفكير 🔥"


def generate_post(product_data, original_url):
    """Generate full Telegram post in the X-Zone channel style"""
    name = product_data["name"]
    full_title = product_data.get("full_title", name)
    price = product_data["price"]
    old_price = product_data["old_price"]
    all_coupons = product_data["all_coupons"]
    current_price_num = product_data["current_price_num"]
    seller_name = product_data.get("seller_name")
    seller_rating = product_data.get("seller_rating")
    rating = product_data.get("rating")
    review_count = product_data.get("review_count")
    stock_info = product_data.get("stock_info")

    category = detect_product_category(name)
    gender = detect_product_gender(name)
    category_emoji = get_category_emoji(category)

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    old_num = extract_number(old_price) if old_price else 0

    # Calculate discount percentage
    discount_pct = 0
    if old_num > current_price_num and old_num > 0:
        discount_pct = int(((old_num - current_price_num) / old_num) * 100)

    # Build context for AI headline
    context_parts = []
    if clean_old and old_num > current_price_num:
        context_parts.append(f"السعر كان {clean_old} والآن {clean_current}")
    if discount_pct > 0:
        context_parts.append(f"خصم {discount_pct}%")
    if all_coupons:
        best = all_coupons[0]
        context_parts.append(f"كوبون إضافي {best['percent']}%")
    context = " | ".join(context_parts)

    # --- AI generates the headline (line 1) ---
    headline = generate_ai_headline(name, category, gender, context, discount_pct)

    parts = []

    # 1. Headline
    parts.append(headline)

    # 2. Product name with category emoji — نكتبه بس لو الجملة الافتتاحية ما فيها اسم المنتج
    # ناخذ أول 3 كلمات من اسم المنتج للمقارنة
    name_words = set(name.lower().split()[:4])
    headline_words = set(headline.lower().split())
    
    # لو فيه تداخل بين كلمات اسم المنتج والجملة = ما نكتبش اسم المنتج تاني
    has_product_name_in_headline = bool(name_words & headline_words)
    
    if not has_product_name_in_headline:
        parts.append(f"{category_emoji} {name}")

    # 3. Prices block
    price_block = []
    if clean_old and old_num > current_price_num:
        price_block.append(f"❌ السعر السابق: {clean_old}")
        if discount_pct > 0:
            price_block.append(f"💥 السعر الآن: {clean_current} (خصم {discount_pct}%)")
        else:
            price_block.append(f"💥 السعر الآن: {clean_current}")
    else:
        price_block.append(f"💰 السعر: {clean_current}")
    parts.append("\n".join(price_block))

    # 4. Coupons block
    if all_coupons:
        best = all_coupons[0]
        final_after_coupon = best["final_price"]
        coupon_block = []
        coupon_block.append(
            f"🎟️ كوبون إضافي {best['percent']}% ← يصير بـ {final_after_coupon} ريال فقط! 🔥"
        )
        # Extra coupons
        if len(all_coupons) > 1:
            coupon_block.append("💡 كوبونات إضافية:")
            for c in all_coupons[1:3]:
                coupon_block.append(f"   • {c['code']} — خصم {c['percent']}%")
        parts.append("\n".join(coupon_block))

    # 5. Buy link
    parts.append(f"🛒 ر هنا الكود كامل مع الجمل الافتتاحية **الأطول والأرقى** — أسلوب أدبي-تسويقي سعودي خالص، بدون تكرار اسم المنتج:

```python
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
            if text and len(text) > 2:
                seller_name = text
                break
    rating_elem = soup.select_one("[data-feature-name='merchant'] .a-icon-alt")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        match = re.search(r'(\d+)%', text)
        if match:
            seller_rating = int(match.group(1))
    return seller_name, seller_rating


def get_product_rating(soup):
    rating = None
    review_count = None
    rating_elem = soup.select_one("#acrPopover .a-icon-alt")
    if not rating_elem:
        rating_elem = soup.select_one("[data-hook='rating-out-of-text']")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        m = re.search(r'([\d.]+)', text)
        if m:
            rating = m.group(1)
    review_elem = soup.select_one("#acrCustomerReviewText")
    if not review_elem:
        review_elem = soup.select_one("[data-hook='total-review-count']")
    if review_elem:
        text = review_elem.get_text(strip=True)
        m = re.search(r'([\d,]+)', text)
        if m:
            review_count = m.group(1).replace(",", "")
    return rating, review_count


def get_stock_info(soup):
    stock_text = None
    selectors = [
        "#availability span",
        ".a-color-price.a-text-bold",
        "#outOfStock",
        "[data-feature-name='availability']",
    ]
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and any(w in text.lower() for w in ['left', 'متبقي', 'stock', 'soon', 'قريباً', 'limited', 'only']):
                stock_text = text
                break
    return stock_text


def extract_coupon_info(text):
    if not text:
        return None, 0
    percent = 0
    percent_match = re.search(r'(\d+)%', text)
    if percent_match:
        percent = int(percent_match.group(1))
    code = None
    code_match = re.search(r'\b([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z]{4,})\b', text)
    if code_match:
        candidate = code_match.group(1)
        if len(candidate) >= 4 and len(candidate) <= 15 and re.search(r'[A-Z]', candidate):
            code = candidate
    if not code and percent > 0:
        code = f"خصم {percent}%"
    return code, percent


def get_all_coupons(soup, current_price_num):
    found_coupons = []
    selectors = [
        "#couponTextInput", "[data-feature-name='coupon']", ".couponText",
        "#couponContainer", "[id*='coupon']", ".promoPriceBlockMessage",
        "[data-a-expander-name='couponSecondaryView']", ".couponCheckbox",
        ".savingsPercentage", ".a-color-price",
    ]
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:
                code, percent = extract_coupon_info(text)
                if code and percent > 0:
                    final_price = int(current_price_num - (current_price_num * percent / 100))
                    found_coupons.append({"code": code, "percent": percent, "final_price": final_price, "text": text})

    page_text = soup.get_text()
    explicit_patterns = [
        r'(?:apply|clip|use|enter|استخدم|طبّق)\s+([A-Z0-9]{4,12})\s*(?:to save|للحصول|for)\s*(\d+)%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*save\s*(\d+)%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*(\d+)%\s*off',
        r'(?:promo\s*code|كود\s*الخصم|كوبون)[\s:]+([A-Z0-9]{4,12})',
    ]
    for pattern in explicit_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                code, percent = match[0], int(match[1]) if str(match[1]).isdigit() else 0
            else:
                code, percent = match, 0
            if code and len(code) >= 4 and percent > 0:
                final_price = int(current_price_num - (current_price_num * percent / 100))
                found_coupons.append({"code": code.upper(), "percent": percent, "final_price": final_price, "text": f"{code} خصم {percent}%"})

    seen = {}
    unique = []
    for c in found_coupons:
        key = c["code"].upper()
        if key not in seen:
            seen[key] = True
            unique.append(c)
    unique.sort(key=lambda x: x["percent"], reverse=True)
    return unique


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
            rating, review_count = get_product_rating(soup)
            stock_info = get_stock_info(soup)
            current_price_num = extract_number(price) if price else 0
            all_coupons = get_all_coupons(soup, current_price_num)

            if price:
                arabic_title = smart_arabic_title(full_title)
                return {
                    "name": arabic_title,
                    "full_title": full_title,
                    "price": price,
                    "old_price": old_price,
                    "image": image,
                    "seller_name": seller_name,
                    "seller_rating": seller_rating,
                    "rating": rating,
                    "review_count": review_count,
                    "stock_info": stock_info,
                    "all_coupons": all_coupons,
                    "current_price_num": current_price_num,
                }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    return None


# ========== قوالب الجمل الافتتاحية الأنيقة والراقية ==========
HEADLINE_TEMPLATES = {
    "electronics": [
        "✨ من بين آلاف الخيارات، هذي الصفقة تبرق وتلمع بفرادة — سعر {price} يجعلك تتوقف وتفكر: وش اللي يمنعني الحين؟ 🔥",
        "🌟 يا هلا بـ الصفقة اللي تستاهل كل ثانية تفكير — {discount}% خصم حقيقي، مو مجرد رقم على ورقة 💎",
        "⚡️ في عالم التقنية السريع، نادر تلقى توازن بين الجودة العالية والسعر المعقول — هالمنتج يقدم لك الاثنين بـ {price} 🎯",
        "🔥 يقولون الفرصة ما تدق الباب مرتين، بس هالمرة دقت بقوة — جهاز إلكتروني بمواصفات تنافسية بسعر {price} يستاهل التجربة 🚀",
        "💡 ذكاء الاختيار مو بس في المنتج، ذكاء الاختيار في التوقيت — والتوقيت الحين يصرخ: اشتري! {discount}% خصم ⚡️",
        "📱 بين كل الإعلانات اللي تمر قدامك، وقف عند هالصفقة — جهاز يستاهل ثقتك بسعر {price} ما يخيب ظنك 🌟",
        "🎯 التميز مو دائماً يجي بسعر باهظ — أحياناً يجي بـ {price} مع خصم {discount}% يثبتلك كلامي 💎",
        "⚡️ سرعة التقنية تتطلب قرار سريع — وهالقرار يبدأ بـ {price} وينتهي بابتسامة رضا 🔥",
        "💻 للمحترفين والهواة على حد سواء — هالجهاز يفتح لك أبواب الإبداع بسعر {price} يناسب كل الميزانيات 🌟",
        "🔋 قوة تدوم، أداء يبهر، وسعر {price} يخليك تتساءل: ليش تأخرت؟ ⚡️",
        "🎧 جودة صوت تغمرك، سعر {price} يبهرك — هالسماعة مو بس تسمع، تخليك تحس بكل نغمة 💎",
        "📡 اتصال سريع، أداء ثابت، وسعر {price} يثبت إن التميز مو حكر على الأغلى 🎯",
        "💾 مساحة تكفي، سرعة تبهر، وسعر {price} يخليك تفكر في مشتريات ثانية ⚡️",
        "🖥️ وضوح يخطف العين، أداء يخطف القلب، وسعر {price} يخطف محفظتك بذكاء 🔥",
        "⌚ أناقة تتجسد على معصمك، ذكاء يتجسد في كل إشعار — والسعر؟ {price} يستاهل الاحتفال 🌟",
        "📺 شاشة تغمرك في عالمها، صوت يحيطك من كل زاوية — والسعر {price} يحيط محفظتك بالراحة 💎",
        "🔌 شاحن سريع يعيد الحياة لأجهزتك، وسعر {price} يعيد الأمل لميزانيتك ⚡️",
        "💡 لمبة ذكية تنوّر بيتك، وسعر {price} ينوّر يومك بقرار ذكي 🎯",
    ],
    
    "fashion_men": [
        "👔 الأناقة الرجالية مو بس في الملبس، في الثقة اللي يمنحك إياها — وهالطقم بـ {price} يمنحك الاثنين معاً 🔥",
        "🕶️ بين كل الخيارات اللي تمر قدامك، وقف عند هالقطعة — طلّة تفرض احترامك بسعر {price} يفرض تقديرك 💎",
        "👞 الحذاء الرجالي الصح يمشي بك كل الطرقات بثقة — وهذا بـ {price} يمشي بك نحو التوفير أيضاً ⚡️",
        "⌚ الوقت ثمين، والساعة اللي ترتديها تثبتلك كلامي — ساعة بـ {price} تستاهل كل دقيقة فيها 🌟",
        "👖 الجينز الصح يدوم معك سنين، والسعر {price} يدوم في ذاكرتك كصفقة ناجحة 🔥",
        "🧥 الشتوي يجي بثقله، بس هالجاكيت يجي بخفة في السعر — {price} مع خصم {discount}% يدفي القلب 💎",
        "👟 حذاء رياضي يركض بك نحو أهدافك، وسعر {price} يركض بك نحو التوفير ⚡️",
        "🎒 شنطة ظهر تحمل أحلامك وأدواتك، وسعر {price} يحمل محفظتك من العبء الزايد 🌟",
        "👔 القميص الأنيق يفتح لك أبواباً كانت مسكرة — بـ {price} يفتح لك باب التوفير أيضاً 🔥",
        "🧢 كاب يغطي راسك من حرارة الشمس، وسعر {price} يغطي جيبك من حرارة الغلاء 💎",
        "👜 محفظة جلدية ت aging معك بكرامة، وسعر {price} ي aging في ذاكرتك كأحسن صفقة ⚡️",
        "🧣 وشاح يدفي عنقك في البرد، وخصم {discount}% يدفي قلبك من فرحة التوفير 🌟",
        "👖 بنطلون رياضي يريحك في الجيم، وسعر {price} يريحك في المحفظة 🔥",
        "🥾 بوت يدوس على كل الطرقات الوعرة، وسعر {price} يدوس على كل الأسعار المنافسة 💎",
        "🕴️ طقم كامل يخليك جاهز لأي مناسبة، وسعر {price} يخليك جاهز لأي صفقة قادمة ⚡️",
    ],
    
    "fashion_women": [
        "👗 الفستان الأنيق يحكي قصة قبل ما تتكلمي — وهذا بـ {price} يحكي قصة ذكاء اختيارك 🔥",
        "👜 الشنطة النسائية الصح تكمل إطلالتك وتكمل ثقتك — وهذه بـ {price} تكمل ميزانيتك بسعادة 💎",
        "💄 المكياج الجيد يزين الوجه، بس المكياج بسعر {price} يزين اليوم كله ⚡️",
        "👠 الكعب العالي يرفعك فوق، والسعر المنخفض {price} يرفعك أعلى — هالتوازن نادر 🌟",
        "🧕 العباية/الشيلة تسترك وتزينك، وسعر {price} يستر ميزانيتك ويزينها 🔥",
        "👡 صندل صيفي يريح قدمك، وسعر {price} يريح بالك من القلق 💎",
        "💍 إكسسوار يلمع زي نجمة في سمائك، وسعر {price} يلمع زي فرصة ما تتكرر ⚡️",
        "🎀 تسريحة شعر تكمل جمالك، وسعر {price} تكمل فرحتك بالشراء 🌟",
        "👛 محفظة صغيرة في الحجم، كبيرة في التوفير — بـ {price} تثبت إن الأشياء الحلوة تجي بأحجام مدروسة 🔥",
        "🧥 كوت شتوي يدفي جسمك، وخصم {discount}% يدفي قلبك من الفرحة 💎",
        "👖 بنطلون يبرر خطوط جسمك، وسعر {price} يبرر قرارك الشرائي بذكاء ⚡️",
        "💃 تنورة ترقص معك في كل خطوة، وسعر {price} يرقص في ذاكرتك كصفقة عمر 🌟",
        "🧴 عطر نسائي يفوح في كل مكان تروحينه، وسعر {price} يفوح في محفظتك كتوفير حقيقي 🔥",
        "👙 لانجري أنيق يمنحك ثقة خفية، وسعر {price} يمنحك فرحة ظاهرة 💎",
        "🎒 حقيبة يد للمرأة العصرية — بـ {price} تثبت إن الأناقة مو حكر على الغالي ⚡️",
    ],
    
    "beauty_men": [
        "🧔 الرجل المهتم بنظافته مهتم بتفاصيل حياته — وهالمنتج بـ {price} يهتم بميزانيتك أيضاً 🔥",
        "💈 حلاقة نظيفة تبدأ بمنتج نظيف، وسعر {price} ينظف ميزانيتك من الغلاء 💎",
        "🧴 لوشن رجالي يترطب بشرتك، وسعر {price} يترطب قلبك من فرحة التوفير ⚡️",
        "🪒 ماكينة حلاقة تفصلك عن المظهر الباهت، وسعر {price} يفصلك عن الأسعار الباهظة 🌟",
        "👔 عطر رجالي يثبت حضورك في أي مكان، وسعر {price} يثبت ذكاءك في كل مكان 🔥",
        "🧼 صابون/شامبو رجالي ينظف وينعش، وسعر {price} ينظف ميزانيتك وينعشها 💎",
        "💪 عناية بالبشرة للرجل الطموح — بـ {price} تثبت إن العناية مو حكر على النساء ⚡️",
        "🌿 زيت طبيعي للرجال اللي يقدرون الأصالة — وسعر {price} يقدر ميزانيتك بأصالة 🌟",
        "🎩 كريم ترتيب يرتب بشرتك، وسعر {price} يرتب أولوياتك المالية 🔥",
        "🧊 مزيل عرق يبردك في الحر، وخصم {discount}% يبرد جيبك من القلق 💎",
    ],
    
    "beauty_women": [
        "💅 طلاء أظافر يلمع زي لمعان عينك لما تشوفين السعر — {price} يستاهل كل نظرة ⚡️",
        "🧖‍♀️ كريم بشرة يخليك تتأملين في مرآتك بسعادة، وسعر {price} يخليك تتأملين في محفظتك براحة 🌟",
        "💋 أحمر شفاه بـ {price}؟! يا ليت كل القرارات الحلوة تجي بهالسهولة والجمال 🔥",
        "🌸 عطر نسائي يفوح بأريج الأناقة، وسعر {price} يفوح بأريج الذكاء في الاختيار 💎",
        "🧴 شامبو/بلسم يقوي شعرك من الجذور، وسعر {price} يقوي ميزانيتك من الأساس ⚡️",
        "✨ سيروم يبرق وجهك بنضارة، وسعر {price} يبرق يومك بفرحة 🌟",
        "🎀 ماسك وجه بـ {price}؟! يستاهل كل دقيقة استرخاء تمنحك إياها 🔥",
        "🌺 زيت عطري يهدي أعصابك بعد يوم طويل، وسعر {price} يهدي قلبك من توتر الميزانية 💎",
        "💄 مجموعة مكياج كاملة بسعر قطعة واحدة — {price} يثبت إن الجمال مو بس للأغنياء ⚡️",
        "🛁 منتج استحمام يدللك كأنك في سبا، وسعر {price} يدللك كأنك محظوظة 🌟",
        "👁️ ماسكرا/آيلاينر يكحل عينك بجاذبية، وسعر {price} يكحل محفظتك بالتوفير 🔥",
        "🧼 غسول وجه نسائي ينظف بعمق، وسعر {price} ينظف ميزانيتك بذكاء 💎",
        "💆‍♀️ كريم ليلي يشتغل وأنت نايمة، وخصم {discount}% يشتغل لمصلحتك وأنت مرتاحة ⚡️",
        "🌙 عطر ليلي يضفي سحراً على لياليك، وسعر {price} يضفي سحراً على ميزانيتك 🌟",
        "✨ بودرة تثبت المكياج طوال اليوم، وسعر {price} يثبت إن قرارك كان صح 🔥",
    ],
    
    "home": [
        "🏠 البيت اللي يعكس ذوقك يبدأ باختيارات ذكية — وهالمنتج بـ {price} يعكس ذكاءك بالكامل 💎",
        "🛋️ كنبة/أثاث يستقبل ضيوفك بكرامة، وسعر {price} يستقبل ميزانيتك بترحيب ⚡️",
        "🍳 جهاز مطبخ يختصر عليك الوقت والجهد، وخصم {discount}% يختصر عليك القلق 🌟",
        "❄️ مكيف/ثلاجة يبرد حرارة الصيف، وسعر {price} يبرد حرارة القلق على الميزانية 🔥",
        "🧹 مكنسة/غسالة تنظف بيتك بعمق، وسعر {price} ينظف ميزانيتك بذكاء 💎",
        "🛏️ سرير/مرتبة ينومك على أحلام هنيئة، وسعر {price} ينومك مرتاح من القلق ⚡️",
        "💡 إضاءة تنوّر زوايا بيتك، وسعر {price} ينوّر زوايا يومك بفرحة 🌟",
        "🚿 سخان/دش يدفيك في البرد، وسعر {price} يدفي محفظتك من الصدمة 🔥",
        "🍽️ طقم مطبخ يجمع العائلة على مائدة واحدة، وسعر {price} يجمع الجودة والتوفير 💎",
        "🪴 ديكور/نبتة تضفي حياة على بيتك، وسعر {price} يضفي حياة على ميزانيتك ⚡️",
        "🧺 منظم/خزانة يرتب فوضى بيتك، وسعر {price} يرتب فوضى ميزانيتك 🌟",
        "🔥 مدفأة/فرن يدفيك في الشتاء، وخصم {discount}% يدفي قلبك في كل فصل 🔥",
        "🚪 باب/ستارة يفصل بينك وبين العالم، وسعر {price} يفصل بينك وبين الغلاء 💎",
        "🪑 كرسي/طاولة تجلسك مرتاح، وسعر {price} يجلس ميزانيتك مرتاحة ⚡️",
        "🌡️ مكيف/دفاية يوازن حرارة بيتك، وسعر {price} يوازن حرارة ميزانيتك 🌟",
    ],
    
    "sports": [
        "💪 القوة الحقيقية تبدأ بقرار — قرار الاعتناء بجسمك، وقرار الشراء بذكاء بـ {price} 🔥",
        "🏋️ دامبل/جهاز رياضي يرفعك فوق، وسعر {price} يرفع ميزانيتك فوق أيضاً 💎",
        "🏃 حذاء رياضي يجري بك نحو أهدافك، وخصم {discount}% يجري بك نحو التوفير ⚡️",
        "🧘 حصيرة يوغا تريح جسمك وعقلك، وسعر {price} يريح محفظتك من الضغط 🌟",
        "🚴 دراجة/جهاز كارديو يقوي قلبك، وسعر {price} يقوي قرارك الشرائي 🔥",
        "⚽ كرة/معدات رياضية تسجل هدف في اللعب، وسعر {price} يسجل هدف في التوفير 💎",
        "🥊 قفازات ملاكمة تضرب الغلاء ضربة قاضية، وسعر {price} يضرب المنافسين ⚡️",
        "🏊 معدات سباحة تغوص بك في عالم الماء، وسعر {price} يغوص بك في عالم التوفير 🌟",
        "🎽 ملابس رياضية تتعبك في التمرين، وسعر {price} يريحك في المحفظة 🔥",
        "🥤 شيكر/زجاجة رياضية ترافقك في كل جلسة، وسعر {price} يرافقك في كل صفقة 💎",
        "🏸 مضرب رياضي يرد كرة الخصم، وسعر {price} يرد كرة الغلاء ⚡️",
        "🧗 معدات تسلق تصعد بك للقمة، وسعر {price} يصعد بك لمستوى جديد من الذكاء 🌟",
        "🏆 جهاز تمرين منزلي يمنحك بطولة يومية، وسعر {price} يمنحك بطولة التوفير 🔥",
        "⛹️ كرة سلة/قدم تجمع الأصدقاء، وسعر {price} يجمع الجودة والسعر المناسب 💎",
        "🤸 إكسسوار رياضي يطوّيك جسدياً، وخصم {discount}% يطوّيك مالياً ⚡️",
    ],
    
    "general": [
        "✨ من بين كل ما يمر أمام عينك اليوم، وقف عند هالصفقة — فرصة نادرة بـ {price} تستاهل كل ثانية تفكير 🔥",
        "🌟 يقولون الذهب يلمع دائماً، بس هالصفقة بـ {price} تلمع أكثر — خصم {discount}% يثبت كلامي 💎",
        "⚡️ في زحمة العروض والإعلانات، نادر تلقى صفقة حقيقية — هذي واحدة منهم، وسعر {price} يكفي كدليل ⚡️",
        "🔥 الفرصة الحقيقية ما تجي مرتين، وإذا جت المرة الثانية فهي مو فرصة — هذي المرة الأولى بـ {price}، لا تفوتها 🌟",
        "💎 الجودة العالية والسعر المعقول نادراً ما يجتمعان — بس هالمرة اجتمعوا في صفقة واحدة بـ {price} 🔥",
        "🎯 الذكاء مو بس في اختيار المنتج، الذكاء في اختيار التوقيت — والتوقيت الحين يصرخ: {price} مع خصم {discount}% 💎",
        "🌊 موجة من التوفير جاية بقوة، وسعر {price} يثبت إن الموجة ما راح تمر بدون ما تستفيد منها ⚡️",
        "🏆 البطولة الحقيقية مو في الملعب، في المحفظة — وهالصفقة بـ {price} تمنحك لقب بطل التوفير 🌟",
        "😤 مستحيل؟! مو معقول؟! بهالحق؟! — كل هالكلمات تطلع من فمك لما تشوف السعر {price} 🔥",
        "🚀 طار السعر لتحت بشكل جنوني، ومحفظتك تستعد للإقلاع — {discount}% خصم يمنحك تذكرة الرحلة 💎",
        "👀 شوفوا بأعينكم، اسمعوا بآذانكم، احسوا بقلوبكم — هالصفقة بـ {price} تستاهل كل حاسة ⚡️",
        "🍀 حظك اليوم مفتوح على مصراعيه، وسعر {price} يثبت إن بختك في التسوق قوي 🌟",
        "🎉 يا هلا بالفرحة! يا هلا بالصفقة! يا هلا بـ {price} اللي يسعد القلب ويريح المحفظة 🔥",
        "🦁 أسد الصفقات هنا، يمشي بثقة ويختار بذكاء — بـ {price} يثبت إن الملكية مو حكر على الأغلى 💎",
        "🎵 لحن التوفير يعزف بأجمل إيقاع، وسعر {price} يكمل السيمفونية بأريج الفرحة ⚡️",
        "🏠 للبيت، للمكتب، لنفسك، لعائلتك — هالمنتج بـ {price} يستاهل كل زاوية في حياتك 🌟",
        "💪 قوية، ثابتة، موثوقة — صفقة بـ {price} ترفع هامتك في أي مجلس 🔥",
        "🎮 جيم أوفر للغلاء، ليفل أب للتوفير — {price} مع خصم {discount}% يفتحلك مراحل جديدة 💎",
        "🌙 ليلة هادئة، قرار ذكي، وسعر {price} ينور طريقك نحو الرضا ⚡️",
        "🧠 عقلية الملياردير بميزانية الموظف — هالصفقة بـ {price} تثبت إن الذكاء مو بس للأغنياء 🌟",
    ],
}


def generate_contextual_headline(product_name, category, gender, context, discount_pct):
    """
    تبني جملة افتتاحية راقية وأنيقة مربوطة بالمنتج، باللهجة السعودية الخليجية
    """
    # تحديد الفئة الفرعية
    if category == "fashion":
        subcategory = f"fashion_{gender}" if gender in ["men", "women"] else "general"
    elif category == "beauty":
        subcategory = f"beauty_{gender}" if gender in ["men", "women"] else "general"
    else:
        subcategory = category if category in HEADLINE_TEMPLATES else "general"
    
    # اختيار قائمة القوالب
    templates = HEADLINE_TEMPLATES.get(subcategory, HEADLINE_TEMPLATES["general"])
    
    # اختيار قالب عشوائي
    template = random.choice(templates)
    
    # استخراج السعر من السياق
    price_match = re.search(r'(\d+)\s*ريال', context)
    price = price_match.group(1) + " ريال" if price_match else "رخيص"
    
    # ملء القالب
    headline = template.format(
        discount=discount_pct,
        price=price
    )
    
    # التأكد من الطول المناسب
    if len(headline) > 120:
        # نختصر الجملة لو طويلة جداً
        shorter_templates = [
            "✨ صفقة نادرة بـ {price} تستاهل كل ثانية تفكير 🔥",
            "🌟 فرصة حقيقية بـ {price} مع خصم {discount}% 💎",
            "⚡️ سعر {price} يثبت إن التميز مو حكر على الأغلى ⚡️",
        ]
        headline = random.choice(shorter_templates).format(price=price, discount=discount_pct)
    
    return headline


def generate_ai_headline(product_name, category, gender, context, discount_pct):
    """
    AI generates a creative multi-line opening block in pure Saudi dialect.
    Highly varied — never repeats the same pattern twice.
    """
    gender_hint = ""
    if gender == "women":
        gender_hint = "المنتج نسائي — اكتب بأسلوب يخاطب البنات والنساء السعوديات."
    elif gender == "men":
        gender_hint = "المنتج رجالي — اكتب بأسلوب يخاطب الشباب والرجال السعوديين."
    else:
        gender_hint = "المنتج للجنسين — اكتب بأسلوب عام."

    discount_hint = f"الخصم {discount_pct}% — ركّز عليه في الجملة." if discount_pct > 0 else ""

    # Rich pool of styles — one picked randomly each call
    styles = [
        'افتح بـ "✨" + جملة وصف أنيقة للمنتج + صدمة عن السعر',
        'افتح بأسلوب القصة: "🌟 من بين آلاف الخيارات..." + وصف المنتج + السعر',
        'افتح بـ "💎" + جملة عن ندرة الصفقة + وصف المنتج المختصر',
        'افتح بأسلوب التأمل: "⚡️ في زحمة العروض..." + المنتج + السعر المجنون',
        'افتح بـ "🔥" + جملة تهويل راقية + "ما يتكرر" + المنتج',
        'افتح بأسلوب الحكمة: "🏆 الذكاء مو بس..." + المنتج + السعر',
        'افتح بـ "🌊" + جملة عن موجة التوفير + المنتج + السعر',
        'افتح بأسلوب التحدي: "😤 مستحيل؟!" + المنتج + "بهالسعر؟!"',
        'افتح بـ "👀" + جملة عن الحواس + المنتج + السعر',
        'افتح بأسلوب الفرحة: "🎉 يا هلا..." + المنتج + السعر + "اللي يسعد"',
        'افتح بـ "🦁" + جملة عن القوة والثقة + المنتج + السعر',
        'افتح بأسلوب الليل: "🌙 ليلة هادئة..." + قرار ذكي + المنتج + السعر',
        'افتح بـ "🧠" + جملة عن الذكاء + المنتج + السعر + "يثبت"',
        'افتح بأسلوب الموسيقى: "🎵 لحن التوفير..." + المنتج + السعر + "يكمل"',
        'افتح بـ "🏠" + جملة عن الزوايا + المنتج + السعر + "يستاهل"',
    ]
    chosen_style = random.choice(styles)

    # Extra spice words to encourage variety
    saudi_words = random.sample([
        "صطولة", "صيدة", "غنيمة", "هجمة", "لحقوا", "شفتوا", "ما يصدق",
        "والله العظيم", "بالحق", "زبالة السعر", "تهبيلة", "مستحيل", "ما يطيح",
        "طار السعر", "دفعة واحدة", "قبل ما يخلص", "اللي فاته فاته",
        "فرصة نادرة", "صفقة العمر", "ذكاء اختيار", "قرار حكيم", "تميز بلا حدود",
    ], k=3)

    prompt = f"""أنت كاتب محتوى سعودي خليجي راقي لقناة تلغرام "صيدات وصفقات".

مهمتك: اكتب جملة افتتاحية واحدة فقط، متوسطة الطول (15-25 كلمة)، باللهجة السعودية الخالصة، أنيقة وراقية وتهويلية تشد العين فوراً.

🎯 الأسلوب المطلوب لهذه المرة:
{chosen_style}

🌶️ كلمات سعودية تقدر تستخدمها (اختر منها أو اخترع غيرها):
{' — '.join(saudi_words)}

📌 قواعد صارمة:
- اللهجة سعودية خليجية 100% (مو مصرية، مو شامية)
- استخدم 2-3 إيموجي داخل الجملة
- جملة واحدة فقط، بدون نقطة في النهاية
- ❌ ممنوع: "ياجدعان"، "ياجماعة"، "يالا"، "حياكم"، "يسلموا"
- ❌ ممنوع تكرار نفس البداية مرتين
- ✅ كل مرة أسلوب مختلف تماماً بناءً على المنتج
- ✅ الأسلوب راقي وأنيق — مو صارخ ولا مبتذل

{gender_hint}
{discount_hint}

المنتج: {product_name}
الفئة: {category}
السياق: {context}

اكتب الجملة مباشرة الآن بدون أي مقدمة أو تفسير:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "أنت كاتب محتوى سعودي خليجي محترف متخصص في التسويق بالعمولة على تلغرام. "
                        "أسلوبك: راقي، أنيق، تهويلي بذوق، لهجة سعودية خالصة. "
                        "كل جملة تكتبها مختلفة تماماً عن السابقة. "
                        "ممنوع التكرار، ممنوع اللهجات الأخرى، ممنوع الكلمات المبتذلة."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 1.0,
            "max_tokens": 80,
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

            forbidden = ["ياجدعان", "ياجماعه", "ياجماعة", "يالله يا", "حياكم", "يالا"]
            for f in forbidden:
                if f in sentence.replace(" ", ""):
                    return generate_contextual_headline(product_name, category, gender, context, discount_pct)

            return sentence

    except Exception as e:
        print(f"Groq error: {e}")

    # لو فشل Groq، نرجع للجملة المربوطة بالمنتج
    return generate_contextual_headline(product_name, category, gender, context, discount_pct)


def _fallback_headline(category):
    """احتياطي فقط — نادراً ما يستخدم"""
    general = HEADLINE_TEMPLATES.get("general", [])
    if general:
        template = random.choice(general)
        return template.format(discount="🔥", price="رخيص")
    return "✨ من بين كل ما يمر أمام عينك، وقف عند هالصفقة — فرصة نادرة تستاهل كل ثانية تفكير 🔥"


def generate_post(product_data, original_url):
    """Generate full Telegram post in the X-Zone channel style"""
    name = product_data["name"]
    full_title = product_data.get("full_title", name)
    price = product_data["price"]
    old_price = product_data["old_price"]
    all_coupons = product_data["all_coupons"]
    current_price_num = product_data["current_price_num"]
    seller_name = product_data.get("seller_name")
    seller_rating = product_data.get("seller_rating")
    rating = product_data.get("rating")
    review_count = product_data.get("review_count")
    stock_info = product_data.get("stock_info")

    category = detect_product_category(name)
    gender = detect_product_gender(name)
    category_emoji = get_category_emoji(category)

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    old_num = extract_number(old_price) if old_price else 0

    # Calculate discount percentage
    discount_pct = 0
    if old_num > current_price_num and old_num > 0:
        discount_pct = int(((old_num - current_price_num) / old_num) * 100)

    # Build context for AI headline
    context_parts = []
    if clean_old and old_num > current_price_num:
        context_parts.append(f"السعر كان {clean_old} والآن {clean_current}")
    if discount_pct > 0:
        context_parts.append(f"خصم {discount_pct}%")
    if all_coupons:
        best = all_coupons[0]
        context_parts.append(f"كوبون إضافي {best['percent']}%")
    context = " | ".join(context_parts)

    # --- AI generates the headline (line 1) ---
    headline = generate_ai_headline(name, category, gender, context, discount_pct)

    parts = []

    # 1. Headline
    parts.append(headline)

    # 2. Product name with category emoji — نكتبه بس لو الجملة الافتتاحية ما فيها اسم المنتج
    # ناخذ أول 3 كلمات من اسم المنتج للمقارنة
    name_words = set(name.lower().split()[:4])
    headline_words = set(headline.lower().split())
    
    # لو فيه تداخل بين كلمات اسم المنتج والجملة = ما نكتبش اسم المنتج تاني
    has_product_name_in_headline = bool(name_words & headline_words)
    
    if not has_product_name_in_headline:
        parts.append(f"{category_emoji} {name}")

    # 3. Prices block
    price_block = []
    if clean_old and old_num > current_price_num:
        price_block.append(f"❌ السعر السابق: {clean_old}")
        if discount_pct > 0:
            price_block.append(f"💥 السعر الآن: {clean_current} (خصم {discount_pct}%)")
        else:
            price_block.append(f"💥 السعر الآن: {clean_current}")
    else:
        price_block.append(f"💰 السعر: {clean_current}")
    parts.append("\n".join(price_block))

    # 4. Coupons block
    if all_coupons:
        best = all_coupons[0]
        final_after_coupon = best["final_price"]
        coupon_block = []
        coupon_block.append(
            f"🎟️ كوبون إضافي {best['percent']}% ← يصير بـ {final_after_coupon} ريال فقط! 🔥"
        )
        # Extra coupons
        if len(all_coupons) > 1:
            coupon_block.append("💡 كوبونات إضافية:")
            for c in all_coupons[1:3]:
                coupon_block.append(f"   • {c['code']} — خصم {c['percent']}%")
        parts.append("\n".join(coupon_block))

    # 5. Buy link
    parts.append(f"🛒 ر يبدو إن الرد اتقطع. هنا الجزء الباقي من الكود:

```python
    # 5. Buy link
    parts.append(f"🛒 رابط الشراء:\n{original_url}")

    return "\n\n".join(parts)


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج من أمازون السعودية")
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

        wait = bot.reply_to(msg, "⏳ جاري تحليل المنتج وتجهيز المنشور...")

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
            print(f"Error sending with image: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل — صيدات وصفقات 🔥")
bot.infinity_polling()
