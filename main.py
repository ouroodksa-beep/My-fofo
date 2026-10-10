import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import os
import html
import json
from flask import Flask, request

TOKEN = "7956075348:AAFetNzy6ECdP8iHgMWbwQIfjSInomOuhBU"
bot = telebot.TeleBot(TOKEN)

# مفتاح Gemini المجاني: https://aistudio.google.com/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or "PUT_YOUR_GEMINI_KEY_HERE"
# موديل gemini-2.5-flash مجدول للإيقاف 16 أكتوبر 2026، فنجرب الأحدث أولاً وننزل تلقائياً للباقي
GEMINI_MODELS = [m for m in [
    os.environ.get("GEMINI_MODEL"),
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-2.5-flash",
] if m]
# Groq (مجاني): https://console.groq.com/keys — الأول في الترتيب، وGemini احتياطي
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or "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"
GROQ_MODELS = [m for m in [
    os.environ.get("GROQ_MODEL"),
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
] if m]
AED_TO_SAR = 3.75 / 3.6725  # الدرهم والريال مربوطين بالدولار

POPULAR_BRANDS = [
    "Apple", "Samsung", "Sony", "Philips", "Dyson", "Braun", "Tefal", "Moulinex",
    "Pampers", "Nivea", "Dove", "L'Oreal", "Maybelline", "Macvities", "Nadec",
    "Almarai", "Savola", "Tide", "Persil", "Downy", "Nike", "Adidas", "Puma",
    "Gillette", "Clorox", "Fine", "Vaseline", "MOTHERCARE", "U.S. POLO",
    "Real Techniques"
]

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "هاتف", "آيفون", "لابتوب", "سماعات", "شاحن", "كيبل", "شاشة", "تلفزيون", "ساعة"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "bag", "backpack", "wallet", "belt", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "حذاء", "شنطة", "ملابس"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "brush", "lipstick", "deodorant", "roll-on", "عطر", "عود", "مسك", "كريم", "لوشن", "شامبو", "بلسم", "صابون", "مزيل عرق", "حلاقة"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "blender", "mixer", "oven", "microwave", "kettle", "coffee maker", "iron", "rice", "milk", "biscuits", "detergent", "ثلاجة", "غسالة", "مكنسة", "مكيف", "خلاط", "فرن", "غلاية", "مطبخ"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "sport", "رياضة", "جيم", "دراجة"]
}


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache"
    }


# ============================================================
# الجملة الافتتاحية — لهجة سعودية، جمل قصيرة وواضحة، بدون ادعاءات
# ============================================================
HOOKS = [
    "صيييدة اليوم!",
    "قنص سريع!",
    "شوفوا هالعرض",
    "لقطة اليوم",
    "وصلنا عرض حلو لكم",
    "جبنا لكم عرض جديد",
    "عرض يستاهل نظرة",
    "سعر حلو لهالمنتج",
    "هذا المنتج سعره اليوم مناسب",
    "إذا كنتم تدورون عليه، شوفوا سعره الحين",
    "صيدة اليوم",
]

HOOKS_WITH_BRAND = [
    "عرض جديد من {brand}",
    "شوفوا هالعرض من {brand}",
    "جبنا لكم عرض من {brand}",
    "صيدة من {brand}",
]

EMOJIS = ["🔥", "⚡", "🎯", "🛍️", "📣", "✨", "🏷️", "🚨"]


def generate_hook(brand=""):
    pool = list(HOOKS)
    if brand:
        pool += [h.format(brand=brand) for h in HOOKS_WITH_BRAND]
    return f"{random.choice(EMOJIS)} <b>{random.choice(pool)}</b>"


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


# ============================================================
# الترجمة — عبارات ثم كلمات، والكلمة غير المعروفة تبقى كما هي
# ============================================================
PHRASE_TRANSLATIONS = {
    "roll on": "مزيل عرق رول", "roll-on": "مزيل عرق رول",
    "body wash": "غسول جسم", "hand wash": "غسول يدين", "face wash": "غسول وجه",
    "shower gel": "جل استحمام", "body lotion": "لوشن جسم",
    "face cream": "كريم وجه", "eye cream": "كريم عيون",
    "hair oil": "زيت شعر", "hair serum": "سيرم شعر",
    "hair dryer": "مجفف شعر", "hair straightener": "مملس شعر",
    "air fryer": "قلاية هوائية", "washing machine": "غسالة ملابس",
    "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف",
    "coffee maker": "صانعة قهوة", "electric kettle": "غلاية كهربائية",
    "power bank": "باور بانك", "smart watch": "ساعة ذكية",
    "wireless earbuds": "سماعات لاسلكية", "wireless headphones": "سماعات رأس لاسلكية",
    "bluetooth speaker": "مكبر صوت بلوتوث", "phone case": "كفر جوال",
    "screen protector": "حماية شاشة", "charging cable": "كيبل شحن",
    "wall charger": "شاحن جداري", "car charger": "شاحن سيارة",
    "gaming mouse": "ماوس قيمنق", "gaming keyboard": "كيبورد قيمنق",
    "baby diapers": "حفاضات أطفال", "baby wipes": "مناديل أطفال",
    "baby lotion": "لوشن أطفال", "baby shampoo": "شامبو أطفال",
    "tooth paste": "معجون أسنان", "tooth brush": "فرشاة أسنان",
    "mouth wash": "غسول فم", "beard oil": "زيت لحية",
    "shaving foam": "رغوة حلاقة", "shaving gel": "جل حلاقة",
    "after shave": "بعد الحلاقة", "body spray": "بخاخ جسم",
    "eau de parfum": "عطر", "eau de toilette": "عطر",
    "liquid detergent": "منظف غسيل سائل", "dish soap": "سائل جلي",
    "floor cleaner": "منظف أرضيات", "glass cleaner": "منظف زجاج",
    "fabric softener": "منعم أقمشة", "stain remover": "مزيل بقع",
    "sports shoes": "حذاء رياضي", "running shoes": "حذاء جري",
    "t shirt": "تيشيرت", "polo shirt": "قميص بولو",
    "winter jacket": "جاكيت شتوي", "summer dress": "فستان صيفي",
    "school bag": "شنطة مدرسة", "travel bag": "شنطة سفر",
    "sun block": "واقي شمس", "makeup remover": "مزيل مكياج",
    "makeup brush": "فرشاة مكياج", "makeup brushes": "فرش مكياج",
    "brush set": "طقم فرش", "lip stick": "أحمر شفاه", "eye liner": "آيلاينر",
    "face mask": "ماسك وجه", "sheet mask": "ماسك ورقي",
    "anti aging": "مضاد للشيخوخة", "anti dandruff": "ضد القشرة",
    "extra virgin olive oil": "زيت زيتون بكر", "olive oil": "زيت زيتون"
}

WORD_TRANSLATIONS = {
    "deodorant": "مزيل عرق", "cream": "كريم", "lotion": "لوشن",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "perfume": "عطر", "fragrance": "عطر", "oud": "عود", "musk": "مسك",
    "makeup": "مكياج", "lipstick": "أحمر شفاه", "gloss": "ملمع شفاه",
    "mascara": "ماسكارا", "blush": "بلاشر", "serum": "سيرم",
    "scrub": "مقشر", "toner": "تونر", "cleanser": "غسول",
    "moisturizer": "مرطب", "sunscreen": "واقي شمس", "gel": "جل",
    "foam": "رغوة", "spray": "بخاخ", "powder": "بودرة",
    "mask": "ماسك", "wipes": "مناديل", "tissues": "مناديل",
    "toothpaste": "معجون أسنان", "toothbrush": "فرشاة أسنان",
    "razor": "ماكينة حلاقة", "trimmer": "ماكينة تشذيب",
    "brush": "فرشاة", "brushes": "فرش", "sponge": "إسفنجة",
    "shirt": "قميص", "tshirt": "تيشيرت", "pants": "بنطلون",
    "jeans": "جينز", "jacket": "جاكيت", "hoodie": "هودي",
    "dress": "فستان", "skirt": "تنورة", "socks": "شرابات",
    "shoes": "حذاء", "sneakers": "سنيكرز", "boots": "بوت",
    "sandals": "صنادل", "slippers": "شباشب", "cap": "كاب",
    "hat": "قبعة", "bag": "شنطة", "backpack": "شنطة ظهر",
    "wallet": "محفظة", "belt": "حزام", "scarf": "شال",
    "sunglasses": "نظارة شمس", "watch": "ساعة", "gloves": "قفازات",
    "phone": "جوال", "iphone": "آيفون", "laptop": "لابتوب",
    "computer": "كمبيوتر", "tablet": "تابلت", "ipad": "آيباد",
    "headphones": "سماعات", "earbuds": "سماعات", "speaker": "مكبر صوت",
    "camera": "كاميرا", "tv": "تلفزيون", "screen": "شاشة",
    "monitor": "شاشة", "keyboard": "كيبورد", "mouse": "ماوس",
    "charger": "شاحن", "cable": "كيبل", "battery": "بطارية",
    "router": "راوتر", "modem": "مودم", "console": "جهاز ألعاب",
    "controller": "يد تحكم", "stand": "ستاند", "holder": "حامل",
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "blender": "خلاط",
    "mixer": "عجانة", "oven": "فرن", "microwave": "مايكرويف",
    "kettle": "غلاية", "iron": "مكواة", "fan": "مروحة",
    "heater": "دفاية", "lamp": "لمبة", "light": "إضاءة",
    "mattress": "مرتبة", "pillow": "مخدة", "blanket": "بطانية",
    "towel": "منشفة", "curtain": "ستارة", "carpet": "سجادة",
    "laundry": "غسيل", "detergent": "منظف غسيل", "softener": "منعم",
    "cleaner": "منظف", "disinfectant": "مطهر", "bleach": "مبيض",
    "rice": "أرز", "milk": "حليب", "biscuits": "بسكويت", "cookies": "كوكيز",
    "chocolate": "شوكولاتة", "candy": "حلويات", "honey": "عسل",
    "coffee": "قهوة", "tea": "شاي", "juice": "عصير", "water": "مياه",
    "oil": "زيت", "sugar": "سكر", "salt": "ملح", "flour": "دقيق",
    "pasta": "مكرونة", "noodles": "نودلز", "sauce": "صلصة",
    "cereal": "كورن فليكس", "oats": "شوفان", "nuts": "مكسرات",
    "treadmill": "سير كهربائي", "dumbbell": "دمبل", "yoga": "يوجا",
    "bicycle": "دراجة", "ball": "كرة", "gym": "جيم",
    "supplement": "مكمل", "protein": "بروتين",
    "set": "طقم", "kit": "طقم",
    "whitening": "مبيض", "nourishing": "مغذي", "moisturizing": "مرطب",
    "hydrating": "مرطب", "refreshing": "منعش",
    "sensitive": "للبشرة الحساسة", "original": "أصلي", "genuine": "أصلي",
    "men": "رجالي", "women": "نسائي", "kids": "أطفال", "baby": "أطفال",
    "sport": "رياضي", "sports": "رياضي",
    "electric": "كهربائي", "digital": "رقمي", "portable": "محمول",
    "wireless": "لاسلكي", "waterproof": "مقاوم للماء", "rechargeable": "قابل للشحن"
}

UNITS_MAP = {
    "ml": "مل", "l": "لتر", "kg": "كيلو", "g": "جرام",
    "pcs": "قطعة", "pc": "قطعة", "pack": "عبوة", "packs": "عبوات",
    "pair": "زوج", "pairs": "أزواج", "set": "طقم", "sets": "أطقم"
}

ARABIC_ADJECTIVES = {
    "مبيض", "مغذي", "مرطب", "منعش", "أصلي", "رجالي", "نسائي",
    "أطفال", "رياضي", "كهربائي", "رقمي", "محمول", "لاسلكي",
    "مقاوم للماء", "قابل للشحن", "للبشرة الحساسة", "ضد القشرة", "مضاد للشيخوخة"
}

KNOWN_WORDS = set(WORD_TRANSLATIONS.keys()) | {
    p.split()[0] for p in PHRASE_TRANSLATIONS.keys()
}


def translate_to_arabic(text):
    if not text or not re.search(r'[A-Za-z]', text):
        return text

    clean = re.sub(r"[^\w\s]", " ", text.lower())
    clean = re.sub(r'\s+', ' ', clean).strip()

    clean = re.sub(r'(\d)\s+(ml|l|kg|g|pcs|pc|pack|packs|pair|pairs)\b', r'\1\2', clean)

    for phrase in sorted(PHRASE_TRANSLATIONS.keys(), key=len, reverse=True):
        p = re.sub(r'[^\w\s]', ' ', phrase)
        clean = re.sub(r'\b' + re.escape(p) + r'\b', PHRASE_TRANSLATIONS[phrase], clean)

    translated = []
    for w in clean.split():
        m = re.match(r'^(\d+(?:\.\d+)?)(ml|l|kg|g|pcs|pc|pack|packs|pair|pairs|set|sets)?$', w)
        if m:
            translated.append(m.group(1) + (" " + UNITS_MAP[m.group(2)] if m.group(2) else ""))
            continue
        translated.append(WORD_TRANSLATIONS.get(w, w))

    # إعادة ترتيب: الاسم قبل الصفة
    reordered = []
    i = 0
    while i < len(translated):
        if (i + 1 < len(translated)
                and translated[i] in ARABIC_ADJECTIVES
                and translated[i + 1] not in ARABIC_ADJECTIVES
                and not re.match(r'^\d', translated[i + 1])):
            reordered += [translated[i + 1], translated[i]]
            i += 2
        else:
            reordered.append(translated[i])
            i += 1

    return re.sub(r'\s+', ' ', " ".join(reordered)).strip()


def guess_brand_from_title(title):
    """لو الصفحة ما فيها براند: الكلمات الأولى قبل أول كلمة صنف معروفة."""
    tokens = re.sub(r"[,|()]", " ", title).split()
    brand_tokens = []
    for t in tokens[:3]:
        low = re.sub(r"[^\w']", "", t.lower())
        if not low or low in KNOWN_WORDS or low.isdigit() or not t[0].isalpha() or not t[0].isupper():
            break
        brand_tokens.append(t)
    return " ".join(brand_tokens)


def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"

    # نشيل البراند قبل الترجمة عشان ما يتغير
    if found_brand:
        full_title = re.sub(re.escape(found_brand), ' ', full_title, flags=re.IGNORECASE)

    # ناخذ الجزء الأول من العنوان فقط
    first_part = re.split(r'\s[-–|]\s|,|\|', full_title)[0].strip()

    clean = translate_to_arabic(first_part)
    words = clean.split()[:6]

    bad_endings = ['من', 'عن', 'في', 'على', 'إلى', 'مع', 'أو', 'و', 'ذو', 'ذات', 'for', 'with', 'and', 'of', 'the']
    while words and words[-1].lower() in bad_endings:
        words.pop()

    res = " ".join(words).strip()
    return res if res else "منتج مميز"


# ============================================================
# استخراج البراند
# ============================================================
JUNK_BRANDS = {"other", "others", "generic", "unknown", "no brand", "unbranded", "n/a", "none",
               "أخرى", "اخرى", "غير معروف", "بدون علامة تجارية", "عام"}


def extract_brand_from_soup(soup, full_title):
    for brand in POPULAR_BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', full_title, re.IGNORECASE):
            return brand

    try:
        for script in soup.find_all('script', type='application/ld+json'):
            if not script.string:
                continue
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and 'brand' in item:
                    b = item['brand']
                    if isinstance(b, dict):
                        b = b.get('name', '')
                    if isinstance(b, str) and b.strip() and not re.search(r'[\u0600-\u06FF]', b):
                        return b.strip()
    except Exception:
        pass

    for sel in ["#bylineInfo", "#bylineInfo_feature_div a", "a#bylineInfo",
                ".po-brand .po-break-word", "tr.po-brand td.a-span9"]:
        elem = soup.select_one(sel)
        if elem:
            text = elem.get_text(strip=True)
            text = re.sub(r'^(Brand:|الماركة:|العلامة التجارية:|زيارة متجر|Visit the)\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*(Store|متجر)$', '', text, flags=re.IGNORECASE).strip()
            if text and not re.search(r'[\u0600-\u06FF]', text) and len(text) < 40:
                return text

    detail_rows = soup.select(
        "#productOverview_feature_div tr, #detailBullets_feature_div li, "
        "#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr"
    )
    for row in detail_rows:
        row_text = row.get_text(" ", strip=True)
        m = re.search(r'(?:Brand|العلامة التجارية|الماركة)\s*[:\-]?\s*(.+)', row_text, re.IGNORECASE)
        if m:
            candidate = re.split(r'\s{2,}', m.group(1).strip())[0].strip()
            if candidate and len(candidate) < 40 and not re.search(r'[\u0600-\u06FF]', candidate):
                return candidate

    return guess_brand_from_title(full_title)


def extract_coupons_and_vouchers(soup, current_price=0.0):
    """
    يرجع كود/قسيمة فقط لو موجودين فعلاً في الصفحة.
    - الكود: لازم يجي بعد كلمة (كود/Code/Coupon...) ثم نقطتين أو شرطة.
    - القسيمة: نقرأها من عناصر الكوبون فقط (مش من كل نص الصفحة)
      عشان ما نخلط بينها وبين نسبة الخصم العادية.
    """
    info = {"code": None, "voucher_text": None,
            "discount_percent": None, "discount_amount": None}

    all_text = soup.get_text(" ", strip=True)
    IGNORED = {"AMAZON", "PRIME", "SHIPPING", "DETAILS", "TERMS", "CHECKOUT",
               "SELECT", "FREE", "OFFER", "APPLY", "CLICK", "COUPON", "VOUCHER",
               "PROMO", "CODE", "SAVE", "EXTRA", "DISCOUNT"}

    m = re.search(r'(?i:كود|رمز|coupon code|promo code|voucher code|code|كوبون)\s*[:\-]\s*([A-Z0-9]{4,15})\b', all_text)
    if m:
        cand = m.group(1).upper()
        if cand not in IGNORED and re.search(r'[A-Z]', cand):
            info["code"] = cand

    voucher_selectors = [
        "label[for*='checkbox'] span", "#vpcButton", ".vouchers-discount-text",
        "#promoPriceBlockMessage_feature_div", "#coupon_feature_div",
        ".couponBadge", ".couponText", "#promotion_feature_div",
        "[id*='coupon']", "[class*='coupon']",
    ]
    candidates = []
    for sel in voucher_selectors:
        for elem in soup.select(sel):
            t = elem.get_text(" ", strip=True)
            if t:
                candidates.append(t)

    KW = r'(?:كوبون|قسيمة|خصم\s*إضافي|Coupon|Voucher|Extra)'
    percent_patterns = [rf'{KW}\D{{0,40}}?(\d{{1,2}})\s*%', rf'(\d{{1,2}})\s*%\D{{0,40}}?{KW}']
    amount_patterns = [rf'{KW}\D{{0,40}}?(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)',
                       rf'(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)\D{{0,40}}?{KW}']

    percents, amounts = set(), set()
    for text in candidates:
        for pat in percent_patterns:
            for mm in re.finditer(pat, text, re.IGNORECASE):
                v = float(mm.group(1))
                if 0 < v <= 90:
                    percents.add(v)
        for pat in amount_patterns:
            for mm in re.finditer(pat, text, re.IGNORECASE):
                v = float(mm.group(1))
                if v > 0:
                    amounts.add(v)

    best_percent = max(percents) if percents else None
    best_amount = max(amounts) if amounts else None

    # حماية: خصم القسيمة غير منطقي -> نتجاهله بدل ما ننشر خصم مش حقيقي
    if current_price > 0:
        if best_amount is not None and best_amount > current_price * 0.5:
            best_amount = None
        if best_percent is not None and best_percent > 60:
            best_percent = None

    if best_percent is not None and best_amount is not None and current_price > 0:
        if current_price * best_percent / 100 >= best_amount:
            info["discount_percent"] = best_percent
        else:
            info["discount_amount"] = best_amount
    elif best_percent is not None:
        info["discount_percent"] = best_percent
    elif best_amount is not None:
        info["discount_amount"] = best_amount

    if info["discount_percent"] is not None:
        info["voucher_text"] = f"خصم إضافي {int(info['discount_percent'])}%"
    elif info["discount_amount"] is not None:
        info["voucher_text"] = f"خصم إضافي {info['discount_amount']:.0f} ريال"

    return info


def extract_best_image(soup, asin):
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront") or soup.select_one("#main-image")
    if img_elem:
        dynamic_img = img_elem.get("data-a-dynamic-image")
        if dynamic_img:
            try:
                img_data = json.loads(dynamic_img)
                return max(img_data.keys(), key=lambda k: img_data[k][0] * img_data[k][1])
            except Exception:
                pass
        src = img_elem.get("src", "")
        if src and "blank" not in src.lower():
            return re.sub(r'\._AC_.*_\.', '._AC_SL1500_.', src)
    return None


def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "🧥", "beauty": "💄", "home": "🧼", "sports": "⚡"}
    return emojis.get(category, "🔥")


def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=12, headers=get_headers())
        return r.url
    except Exception:
        return url


def extract_asin(url):
    m = re.search(r'/(?:dp|gp/product|ASIN)/([A-Z0-9]{10})', url, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m_short = re.search(r'/([A-Za-z0-9]{10})(?:[/?]|$)', url)
    if m_short and m_short.group(1).upper() not in ["SAUDI", "AMAZON"]:
        return m_short.group(1).upper()
    return None


def extract_number(price_text):
    if not price_text:
        return 0.0
    nums = re.findall(r'\d[\d,]*(?:\.\d+)?', str(price_text))
    return float(nums[0].replace(",", "")) if nums else 0.0


def extract_current_price(soup, html_content):
    current_price = 0.0

    try:
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, list) and offers:
                        current_price = float(offers[0].get('price', 0))
                    elif isinstance(offers, dict):
                        current_price = float(offers.get('price', 0))
    except Exception:
        pass

    if current_price == 0.0:
        for sel in [".apexPriceToPay .a-offscreen",
                    "#corePrice_feature_div .a-price .a-offscreen",
                    "#corePriceDisplay_desktop_feature_div .a-price-whole",
                    ".a-price .a-offscreen",
                    "#priceblock_ourprice", "#priceblock_dealprice"]:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                val = extract_number(elem.text.strip())
                if val > 0:
                    current_price = val
                    break

    if current_price == 0.0:
        for pat in [r'"priceAmount"\s*:\s*([\d\.]+)', r'"buyingPrice"\s*:\s*([\d\.]+)']:
            match = re.search(pat, html_content, re.IGNORECASE)
            if match:
                val = extract_number(match.group(1))
                if val > 0:
                    current_price = val
                    break

    return current_price


def fetch_product_details(url, asin):
    try:
        resp = requests.get(url, headers=get_headers(), timeout=12)
        html_text = resp.text
        soup = BeautifulSoup(resp.content, "html.parser")

        title_elem = soup.select_one("#productTitle") or soup.select_one("h1")

        if not title_elem or "captcha" in html_text.lower():
            proxy_url = f"https://corsproxy.io/?{url}"
            resp = requests.get(proxy_url, headers=get_headers(), timeout=12)
            html_text = resp.text
            soup = BeautifulSoup(resp.content, "html.parser")
            title_elem = soup.select_one("#productTitle") or soup.select_one("h1")

        if not title_elem:
            return None

        title = title_elem.text.strip()
        price = extract_current_price(soup, html_text)

        brand = extract_brand_from_soup(soup, title)
        if brand.strip().lower() in JUNK_BRANDS:
            brand = guess_brand_from_title(title)
        title_res = clean_arabic_title(title, brand)

        package_detail = ""
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(ml|l|kg|g|pcs|pack|مل|لتر|كيلو|جرام|قطعة|عبوة)\b', title, re.IGNORECASE)
        if size_match:
            unit = size_match.group(2)
            package_detail = f"{size_match.group(1)} {UNITS_MAP.get(unit.lower(), unit)}"

        coupon = extract_coupons_and_vouchers(soup, price)
        final_price = price
        if price > 0:
            if coupon.get("discount_percent"):
                final_price = round(price * (1 - coupon["discount_percent"] / 100), 2)
            elif coupon.get("discount_amount"):
                final_price = max(round(price - coupon["discount_amount"], 2), 0)

        # أهم المزايا/تفاصيل العبوة الظاهرة فعلاً في صفحة المنتج
        feature_items = []
        for selector in ["#feature-bullets li span.a-list-item", "#feature-bullets li", "#productDescription p"]:
            for elem in soup.select(selector):
                value = re.sub(r"\s+", " ", elem.get_text(" ", strip=True)).strip()
                value = re.sub(r"^(?:[•·▪︎\-]+)\s*", "", value)
                if (len(value) >= 12 and len(value) <= 220
                        and not re.search(r"إعلان|تسوق الآن|قد يعجبك|sponsored|customers also", value, re.IGNORECASE)
                        and value not in feature_items):
                    feature_items.append(value)
                if len(feature_items) >= 8:
                    break
            if len(feature_items) >= 8:
                break

        return {
            "title_clean": title_res,
            "title_raw": title,
            "features": feature_items[:6],
            **extract_variants(soup),
            "brand": brand,
            "package": package_detail,
            "price": final_price,
            "price_before_coupon": price if final_price != price else 0.0,
            "category": detect_product_category(title),
            "coupon_code": coupon["code"],
            "voucher_text": coupon["voucher_text"],
            "image_url": extract_best_image(soup, asin),
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


def format_price(price):
    return str(int(price)) if float(price).is_integer() else f"{price:.2f}"


def extract_variants(soup):
    """اللون والمقاس المختارين في الصفحة (لو موجودين)."""
    def first_text(selectors):
        for sel in selectors:
            e = soup.select_one(sel)
            if e:
                t = e.get_text(" ", strip=True)
                if t and not re.search(r'select|اختر', t, re.IGNORECASE) and len(t) < 40:
                    return t
        return ""
    color = first_text(["#variation_color_name .selection",
                        "#inline-twister-expanded-dimension-text-color_name"])
    size = first_text(["#native_dropdown_selected_size_name",
                       "#variation_size_name .selection",
                       "#inline-twister-expanded-dimension-text-size_name"])
    return {"color": color, "size": size}


def fetch_uae_price(asin):
    """سعر نفس المنتج في أمازون الإمارات بالدرهم، أو 0 لو غير متوفر/محجوب."""
    try:
        resp = requests.get(f"https://www.amazon.ae/dp/{asin}", headers=get_headers(), timeout=12)
        if resp.status_code != 200 or "captcha" in resp.text.lower():
            return 0.0
        soup = BeautifulSoup(resp.content, "html.parser")
        if not soup.select_one("#productTitle"):
            return 0.0
        return extract_current_price(soup, resp.text)
    except Exception:
        return 0.0


REF_LABELS = r'(سوبرماركت|السوبرماركت|صيدلية|الصيدلية|محلات|المحلات|الموقع|نون|جرير|بنده|النهدي|الدواء)'


def parse_extras(text):
    """
    يقرأ أسعار المقارنة اليدوية من رسالتك، مثال:
    <الرابط> سوبرماركت 90
    <الرابط> صيدلية 23
    """
    t = re.sub(r'https?://\S+', ' ', text)
    t = re.sub(r'سوبر\s+ماركت', 'سوبرماركت', t)
    return [(label, float(p)) for label, p in
            re.findall(REF_LABELS + r'\s*[:=]?\s*(\d+(?:\.\d+)?)', t)]


def parse_note(text):
    """أي كلام حر تكتبينه مع الرابط (غير أسعار المقارنة) يوصل للكاتب كملاحظة."""
    t = re.sub(r'https?://\S+', ' ', text)
    t = re.sub(r'سوبر\s+ماركت', 'سوبرماركت', t)
    t = re.sub(REF_LABELS + r'\s*[:=]?\s*\d+(?:\.\d+)?', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


AI_SYSTEM_PROMPT = """أنت كاتب إعلانات عروض لقناة تيليجرام سعودية اسمها «اكس زون». اكتب بلهجة سعودية/خليجية طبيعية وعفوية، مثل شخص يشارك أصحابه عرضًا يستاهل. لا تكتب وصف متجر رسمي ولا كلامًا آليًا.

روح الأسلوب: «جبته لكم»، «والسعر يا بلااااش»، «شدني مدح التعليقات» إذا كانت الملاحظة موجودة فعلًا. نوّع الصياغة ولا تكرر افتتاحية واحدة.

تنسيق المنشور مهم جدًا:
- اكتب 2 إلى 3 أسطر محتوى قصيرة فقط، والرابط يضاف تلقائيًا بعدك.
- افصل بين كل سطر محتوى وسطر فارغ؛ لا تجمع الكلام في فقرة واحدة.
- استخدم **الخط العريض** لاسم المنتج أو السعر، واختر الأهم. يمكن استخدام *المائل* لملاحظة قصيرة، و`الخط الثابت` لكود قسيمة أو رمز منتج عند الحاجة فقط.
- لا تجعل السطر جملة طويلة؛ خله خفيفًا وسهل القراءة من نظرة واحدة.
- لا تضف كلام ربط أو مقدمات بلا فائدة. أحيانًا ابدأ باسم المنتج مباشرة.
- اذكر اسم المنتج باختصار، ثم السعر، ثم نقطة بيع واحدة فقط إذا كانت مفيدة وموثوقة.
- أبرز الكمية/عدد القطع أو ميزة عملية أو توفيرًا مؤكدًا؛ لا تسرد كل المواصفات. لا تجمع مبلغ التوفير والنسبة والسعر المقارن كلها معًا.
- استخدم لهجة طبيعية مثل «بالسوق يوصل...» أو «جبته لكم بـ...» إذا كانت البيانات تدعم ذلك.
- لا تخترع خصمًا أو سعرًا سابقًا أو جودة أو ضمانًا أو ميزة أو مراجعات. لا تقل «مضمون» دون دليل.
- لا تذكر أمازون أو السعودية أو Amazon في نص المنشور، ولا تكتب أي رابط أو شرح تقني.
- أخرج نص المنشور فقط، مع فواصل الأسطر الفارغة كما هو مطلوب.

أمثلة على التنسيق والنبرة:
🧴 **كريم كاب 500 مل**

جبته لكم بـ **23 ريال** ✅

بالسوق يوصل لـ 55 ريال 🔥

🧦 **جوارب شتوية مبطنة**

🥇 5 أزواج بـ **27 ريال** — و15 زوج بـ **55 ريال**

🤩 *شدني مدح التعليقات على المنتج!*

✨ **اسم المنتج المختصر** بـ **السعر المتوفر**
"""


def build_facts(product, extras, uae_aed, asin="", source_urls=None):
    """يرجع (المعطيات للكاتب, روابط مصدر المقارنة)."""
    source_urls = source_urls or []
    price = product["price"]
    sources = []
    facts = [f"اسم المنتج بالإنجليزي: {product.get('title_raw', '')}"]
    if product["brand"]:
        facts.append(f"البراند: {product['brand']}")
    if price > 0:
        facts.append(f"السعر الحالي: {format_price(price)} ريال")
    if product.get("price_before_coupon"):
        facts.append(f"السعر قبل القسيمة: {format_price(product['price_before_coupon'])} ريال")
    if product.get("size"):
        facts.append(f"المقاس: {product['size']}")
    if product.get("color"):
        facts.append(f"اللون: {product['color']}")
    if product.get("features"):
        facts.append("تفاصيل ومزايا مذكورة في صفحة المنتج (استخدم المفيد فقط، ولا تحولها لادعاءات أكبر):")
        facts.extend(f"- {feature}" for feature in product["features"][:6])
    if product.get("coupon_code"):
        facts.append(f"كود الخصم: {product['coupon_code']}")
    elif product.get("voucher_text"):
        facts.append(f"فيه قسيمة تتفعّل من صفحة المنتج ({product['voucher_text']}) والسعر أعلاه بعدها")

    # مقارنة يدوية: نذكرها فقط لو الرقم أعلى من سعرنا (يعني فعلاً توفير)
    added_manual = False
    for label, p in extras:
        if price > 0 and p >= price + 1:
            facts.append(f"سعره في {label}: {format_price(p)} ريال (الفرق: {format_price(round(p - price, 2))} ريال، توفير حوالي {round((p - price) / p * 100)}% مقارنة بهذا السعر)")
            added_manual = True
    if added_manual and source_urls:
        sources.append(source_urls[0])

    # مقارنة أمازون الإمارات: فقط لو أغلى بوضوح
    if uae_aed > 0 and price > 0:
        uae_sar = round(uae_aed * AED_TO_SAR)
        if uae_sar >= price * 1.05 and uae_sar - price >= 1:
            facts.append(f"سعره في الإمارات: حوالي {uae_sar} ريال (الفرق: {format_price(round(uae_sar - price))} ريال، توفير حوالي {round((uae_sar - price) / uae_sar * 100)}% مقارنة بهذا السعر)")
            if asin:
                sources.append(f"https://www.amazon.ae/dp/{asin}")

    return "\n".join(facts), sources


def _key_ok(key):
    return bool(key) and not key.startswith("PUT_")


def _user_prompt(facts_text):
    return ("المعطيات المتاحة للمنتج:\n" + facts_text +
            "\n\nاكتب بوستًا قصيرًا باللهجة السعودية/الخليجية، حيويًا وطبيعيًا مثل توصية لصديق، "
            "من 2 إلى 4 أسطر محتوى. نوّع البداية ولا تكرر قالبًا ثابتًا. "
            "اذكر اسمًا مختصرًا والسعر الحالي، ثم أقوى نقطة بيع واحدة أو مقارنة موثوقة إن وجدت. "
            "إذا وُجدت ملاحظة من صاحب القناة فاستفد منها فقط إذا كانت طبيعية وذات صلة. "
            "لا تخترع معلومات ولا تحذف السعر الحالي. أخرج نص المنشور فقط.")


def _groq_generate(facts_text):
    """يرجع (نص, None) أو (None, سبب) أو (None, None) لو المفتاح غير مضاف."""
    if not _key_ok(GROQ_API_KEY):
        return None, None
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    last_error = "Groq: لا يوجد موديل متاح"
    for model in GROQ_MODELS:
        try:
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": _user_prompt(facts_text)},
                ],
                "temperature": 0.8,
                "max_completion_tokens": 500,
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              json=body, headers=headers, timeout=30)
            if r.status_code in (404, 413, 429, 500, 503):
                last_error = f"Groq {model}: HTTP {r.status_code}"
                print("Groq skip:", last_error)
                continue
            if r.status_code in (400, 401, 403):
                msg = ""
                try:
                    msg = r.json().get("error", {}).get("message", "")[:100]
                except Exception:
                    pass
                return None, f"Groq: المفتاح أو الطلب مرفوض (HTTP {r.status_code}) {msg}"
            r.raise_for_status()
            text = (r.json()["choices"][0]["message"].get("content") or "").strip()
            if not text:
                last_error = f"Groq {model}: رد فارغ"
                continue
            return text, None
        except Exception as e:
            last_error = f"Groq {model}: {str(e)[:100]}"
            print("Groq error:", last_error)
            continue
    return None, last_error


def _gemini_generate(facts_text):
    if not _key_ok(GEMINI_API_KEY):
        return None, None
    body = {
        "system_instruction": {"parts": [{"text": AI_SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": _user_prompt(facts_text)}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 500},
    }
    headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
    last_error = "Gemini: لا يوجد موديل متاح"
    for model in GEMINI_MODELS:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            r = requests.post(url, json=body, headers=headers, timeout=30)
            if r.status_code in (404, 429, 500, 503):
                last_error = f"Gemini {model}: HTTP {r.status_code}"
                print("Gemini skip:", last_error)
                continue
            if r.status_code in (400, 401, 403):
                msg = ""
                try:
                    msg = r.json().get("error", {}).get("message", "")[:100]
                except Exception:
                    pass
                return None, f"Gemini: المفتاح أو الطلب مرفوض (HTTP {r.status_code}) {msg}"
            r.raise_for_status()
            parts = r.json()["candidates"][0]["content"]["parts"]
            text = "".join(pt.get("text", "") for pt in parts if not pt.get("thought")).strip()
            if not text:
                last_error = f"Gemini {model}: رد فارغ"
                continue
            return text, None
        except Exception as e:
            last_error = f"Gemini {model}: {str(e)[:100]}"
            print("Gemini error:", last_error)
            continue
    return None, last_error


def style_post_lines(text):
    """يحافظ على فواصل الأسطر الفارغة ويمنع تكديس المسافات."""
    lines = []
    blank_pending = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            blank_pending = bool(lines)
            continue
        if blank_pending and lines and lines[-1] != "":
            lines.append("")
        # لا نضيف رموزًا عشوائية؛ الكاتب مسؤول عن اختيار الإيموجي المناسب.
        lines.append(line)
        blank_pending = False
    return "\n".join(lines).strip()



def validate_ai_text(text, facts_text):
    """يرفض الردود الناقصة أو الطويلة أو التي تحتوي أرقامًا غير موثقة."""
    if not text or not text.strip():
        return "رد فارغ"
    text = text.strip()
    if re.search(r'أمازون|امازون|السعودية|amazon', text, re.IGNORECASE):
        return "النص ذكر كلمة ممنوعة"
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2 or len(lines) > 3:
        return "عدد الأسطر غير مناسب"
    # ارفض النص الذي يبدو مقطوعًا أو يحتوي على تنسيق غير مكتمل
    if text.count('**') % 2 or text.count('`') % 2:
        return "تنسيق غير مكتمل"
    if re.search(r'(?:توفير|ميزة|السعر|مقارنة|بـ|بس|من|على|مع|لل|ال)\s*$', lines[-1]):
        return "النص يبدو مقطوعًا"
    # إذا كان السعر الحالي موجودًا في المعطيات، لا نقبل منشورًا نسي ذكره.
    price_match = re.search(r'السعر الحالي:\s*(\d+(?:\.\d+)?)\s*ريال', facts_text)
    if price_match:
        expected_price = float(price_match.group(1))
        visible_numbers = {float(x) for x in re.findall(r'\d+(?:\.\d+)?', text)}
        if expected_price not in visible_numbers:
            return "المنشور لا يتضمن السعر الحالي"
    allowed = {float(x) for x in re.findall(r'\d+(?:\.\d+)?', facts_text)}
    used = {float(x) for x in re.findall(r'\d+(?:\.\d+)?', text)}
    if not used.issubset(allowed):
        print("AI used numbers not in facts:", used - allowed)
        return "النص ذكر أرقام غير موجودة في بيانات المنتج"
    return None


def ai_write_post(facts_text):
    """Groq أولاً ثم Gemini. يرجع النص بعد التحقق أو سبب الفشل للتسجيل فقط."""
    errors = []
    for generate in (_groq_generate, _gemini_generate):
        text, err = generate(facts_text)
        if text:
            bad = validate_ai_text(text, facts_text)
            if bad:
                errors.append(bad)
                print("AI response rejected:", bad)
                continue
            return text, None
        if err:
            errors.append(err)
    if not errors:
        return None, "لا يوجد مفتاح ذكاء اصطناعي مضاف"
    return None, " | ".join(errors)


def generate_post(product, original_url):
    """قالب احتياطي قصير ومكتمل؛ لا يرسل رسائل الخطأ التقنية للمشتركين."""
    title = html.escape((product.get("title_clean") or "المنتج").strip())
    brand = html.escape((product.get("brand") or "").strip())
    package = html.escape((product.get("package") or "").strip())
    price = product.get("price", 0)

    if package and package.lower() not in title.lower():
        title = f"{title} ({package})"
    if brand and brand.lower() not in title.lower():
        title = f"{brand} {title}"

    # لا نستخدم مقدمة عامة؛ الاسم والسعر أهم معلومتين.
    content_lines = [f"🛍️ <b>{title}</b>"]
    if price and price > 0:
        content_lines.append(f"💰 <b>بـ {format_price(price)} ريال بس!</b>")
    if product.get("coupon_code"):
        content_lines.append(f"🎟️ كود الخصم: <code>{html.escape(product['coupon_code'])}</code>")
    elif product.get("voucher_text"):
        content_lines.append("🎟️ فعّل القسيمة من صفحة المنتج قبل الطلب")
    return "\n\n".join(content_lines) + "\n\n🔗 " + html.escape(original_url, quote=True)



@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = (msg.text or "").strip()
    all_urls = [u.rstrip(".,،)") for u in re.findall(r'https?://\S+', text)]
    urls = [u for u in all_urls if re.search(r'amazon|amzn', u, re.IGNORECASE)]
    source_urls = [u for u in all_urls if u not in urls]

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط المنتج من أمازون السعودية لتحويله لبوست ✨")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        asin = extract_asin(expanded)

        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رمز المنتج (ASIN)، تأكد من صحة الرابط.")
            continue

        target_url = f"https://www.amazon.sa/dp/{asin}"
        wait = bot.reply_to(msg, "⏳ جاري قراءة بيانات المنتج...")

        product = fetch_product_details(target_url, asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، حاول مجدداً بعد قليل.", msg.chat.id, wait.message_id)
            continue

        extras = parse_extras(text)
        note = parse_note(text)
        uae_aed = fetch_uae_price(asin)
        facts_text, compare_sources = build_facts(product, extras, uae_aed, asin, source_urls)
        if note:
            facts_text += f"\nملاحظة من صاحب القناة: {note}"

        ai_text, ai_error = ai_write_post(facts_text)
        if ai_error:
            # الخطأ للتشخيص في سجلات التشغيل فقط، لا يظهر في قناة العروض.
            print("AI generation failed; using concise fallback:", ai_error)
        if ai_text:
            ai_text = style_post_lines(ai_text)
            # حوّل تنسيق Markdown إلى HTML بعد تهريب النص، مع دعم العريض والمائل والثابت.
            safe = html.escape(ai_text)
            safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
            safe = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', safe)
            safe = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', safe)
            # لا نضيف إيموجي تلقائيًا لكل سطر؛ نحافظ على تنسيق الكاتب وفواصل الأسطر.
            post = safe.strip() + "\n\n🔗 " + html.escape(original_url, quote=True)
        else:
            post = generate_post(product, original_url)

        try:
            if product.get("image_url"):
                bot.send_photo(msg.chat.id, product["image_url"], caption=post, parse_mode="HTML")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="HTML")
        except Exception:
            bot.send_message(msg.chat.id, post, parse_mode="HTML")
        finally:
            try:
                bot.delete_message(msg.chat.id, wait.message_id)
            except Exception:
                pass


app = Flask(__name__)


@app.route('/')
def index():
    return "🤖 البوت يعمل", 200


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Unsupported Media Type', 415


WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if WEBHOOK_HOST:
    try:
        bot.remove_webhook()
        bot.set_webhook(url=f"https://{WEBHOOK_HOST}/webhook")
    except Exception as e:
        print(f"Webhook setup failed: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
