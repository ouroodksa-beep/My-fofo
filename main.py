import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import os
import html
import json
from flask import Flask, request

TOKEN = "7956075348:AAFetNzy6ECdP8iHgMWbwQIfjSInomOuhBU"
bot = telebot.TeleBot(TOKEN)

POPULAR_BRANDS = [
    "Apple", "Samsung", "Sony", "Philips", "Dyson", "Braun", "Tefal", "Moulinex",
    "Pampers", "Nivea", "Dove", "L'Oreal", "Maybelline", "Macvities", "Nadec",
    "Almarai", "Savola", "Tide", "Persil", "Downy", "Nike", "Adidas", "Puma",
    "Gillette", "Clorox", "Fine", "Vaseline", "MOTHERCARE", "U.S. POLO"
]

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "هاتف", "آيفون", "لابتوب", "سماعات", "شاحن", "كيبل", "شاشة", "تلفزيون", "ساعة"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "bag", "backpack", "wallet", "belt", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "حذاء", "شنطة", "مكياج", "ملابس", "بوكسر"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "deodorant", "roll-on", "عطر", "عود", "مسك", "كريم", "لوشن", "شامبو", "بلسم", "صابون", "مزيل عرق", "مغذي", "رول", "حلاقة", "موس"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "blender", "mixer", "oven", "microwave", "kettle", "coffee maker", "iron", "ارز", "رز", "حليب", "بسكويت", "منعم", "ثلاجة", "غسالة", "مكنسة", "مكيف", "خلاط", "فرن", "غلاية", "مطبخ", "غسول", "مطهر", "مناديل"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "sport", "رياضة", "جيم", "تمارين", "دراجة"]
}

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache"
    }

# ============================================================
# الجملة الافتتاحية — كلمات جديدة، جملة واحدة فقط
# ============================================================
def generate_dynamic_hook(brand=""):
    emojis = ["🚨", "🔥", "⚡", "💥", "🎯", "🛍️", "💣", "✨", "📣", "🏷️", "🚀", "🎉", "💎", "👁️", "💸", "😱", "📢"]
    openers = [
        "نزل السعر بشكل رهيب وما تتكرر كثير",
        "يوميات العروض الحلوة ما تنتهي",
        "كل ما تشوفه أرخص من أي وقت ثاني",
        "من الحاجات اللي تدخلها السلة على طول",
        "عرض هادي وساري ومحتاج سرعة قرار",
        "صيدة رائعة نزلت حالاً",
        "قررنا نشارككم خصم اليوم الجميل",
        "هذي من العروض اللي ما تخليها تفوت",
        "اخترناها لكم لأن فرق السعر واضح",
        "لو تنتظر تنزل أكثر بتخسر اللي عندك",
        "عرض مباشر من الصفحة الرسمية",
        "كذا سعر يستاهل الطلب فوراً",
        "لقطة اليوم تستاهل المتابعة",
        "خصم حقيقي مش مجرد تخفيض شكلي",
        "وصل لأفضل سعر وصله من فترة",
        "سعر ممتاز جداً وفرصة طيبة للشراء",
        "اخفض ميزانيتك واطلب بدون تردد",
        "عروض الساعة هذه تستاهل اللقطة"
    ]
    if brand:
        openers += [
            f"عروض {brand} اليوم وصلت لأحلى مرحلة",
            f"تخفيضات {brand} المباشرة من الصفحة الرسمية",
            f"{brand} نزلت اليوم بسعر يخلينا نطلب فوراً",
            f"خصومات {brand} وصلت لسعر ما تتوقعه"
        ]

    emoji = random.choice(emojis)
    opener = random.choice(openers)
    return f"{emoji} <b>{opener}!</b>"

def generate_dynamic_coupon_call(code):
    icons = ["🎟️", "🏷️", "🔑", "💥", "🎁", "✨", "📌", "💳"]
    verbs = ["استخدموا", "لا تنسوا استخدام", "تأكدوا من تطبيق", "ادخلوا", "انسخوا", "ضعوا", "فعّلوا"]
    nouns = ["كود الخصم", "رمز الخصم", "الكود الإضافي", "كود التوفير", "الكود المباشر", "الرمز الترويجي"]
    adjectives = ["الفعّال", "المتاح", "الحالي", "المميز", "الخاص بالموقع"]

    icon = random.choice(icons)
    verb = random.choice(verbs)
    noun = random.choice(nouns)
    adj = random.choice(adjectives)

    style = random.choice([1, 2, 3])
    if style == 1:
        phrase = f"{verb} {noun} {adj}:"
    elif style == 2:
        phrase = f"{noun} {adj} للتوفير:"
    else:
        phrase = f"{verb} هذا الكود عند الدفع:"

    return f"{icon} <b>{phrase}</b> <code>{html.escape(code)}</code>"

def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"

# ============================================================
# ترجمة الأصناف — عبارات أولاً ثم كلمات، مع إعادة ترتيب الصفات
# ============================================================
PHRASE_TRANSLATIONS = {
    "roll on": "مزيل عرق رول", "roll-on": "مزيل عرق رول",
    "body wash": "غسول جسم", "hand wash": "غسول يدين",
    "face wash": "غسول وجه", "hair wash": "شامبو",
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
    "liquid detergent": "مسحوق غسيل سائل", "dish soap": "سائل جلي",
    "floor cleaner": "منظف أرضيات", "glass cleaner": "منظف زجاج",
    "fabric softener": "منعم أقمشة", "stain remover": "مزيل بقع",
    "sports shoes": "حذاء رياضي", "running shoes": "حذاء جري",
    "t shirt": "تيشيرت", "polo shirt": "قميص بولو",
    "winter jacket": "جاكيت شتوي", "summer dress": "فستان صيفي",
    "school bag": "شنطة مدرسة", "travel bag": "شنطة سفر",
    "sunscreen": "واقي شمس", "sun block": "واقي شمس",
    "makeup remover": "مزيل مكياج", "foundation": "كريم أساس",
    "lip stick": "أحمر شفاه", "eye liner": "آيلاينر",
    "face mask": "ماسك وجه", "sheet mask": "ماسك ورقي",
    "anti aging": "مضاد للشيخوخة", "anti dandruff": "ضد القشرة",
    "extra virgin olive oil": "زيت زيتون بكر", "olive oil": "زيت زيتون"
}

WORD_TRANSLATIONS = {
    # عناية شخصية
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
    # ملابس وإكسسوارات
    "shirt": "قميص", "tshirt": "تيشيرت", "pants": "بنطلون",
    "jeans": "جينز", "jacket": "جاكيت", "hoodie": "هودي",
    "dress": "فستان", "skirt": "تنورة", "socks": "شرابات",
    "shoes": "حذاء", "sneakers": "سنيكرز", "boots": "بوت",
    "sandals": "صنادل", "slippers": "شباشب", "cap": "كاب",
    "hat": "قبعة", "bag": "شنطة", "backpack": "شنطة ظهر",
    "wallet": "محفظة", "belt": "حزام", "scarf": "شال",
    "sunglasses": "نظارة شمس", "watch": "ساعة", "gloves": "قفازات",
    # إلكترونيات
    "phone": "جوال", "iphone": "آيفون", "laptop": "لابتوب",
    "computer": "كمبيوتر", "tablet": "تابلت", "ipad": "آيباد",
    "headphones": "سماعات", "earbuds": "سماعات", "speaker": "مكبر صوت",
    "camera": "كاميرا", "tv": "تلفزيون", "screen": "شاشة",
    "monitor": "شاشة", "keyboard": "كيبورد", "mouse": "ماوس",
    "charger": "شاحن", "cable": "كيبل", "battery": "بطارية",
    "router": "راوتر", "modem": "مودم", "console": "جهاز ألعاب",
    "controller": "يد تحكم", "stand": "ستاند", "holder": "حامل",
    # منزل ومطبخ
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "blender": "خلاط",
    "mixer": "عجانة", "oven": "فرن", "microwave": "مايكرويف",
    "kettle": "غلاية", "iron": "مكواة", "fan": "مروحة",
    "heater": "دفاية", "lamp": "لمبة", "light": "إضاءة",
    "mattress": "مرتبة", "pillow": "مخدة", "blanket": "بطانية",
    "towel": "منشفة", "curtain": "ستارة", "carpet": "سجادة",
    "laundry": "غسيل", "detergent": "مسحوق غسيل", "softener": "منعم",
    "cleaner": "منظف", "disinfectant": "مطهر", "bleach": "مبيض",
    # أطعمة ومشروبات
    "rice": "أرز", "milk": "حليب", "biscuits": "بسكويت", "cookies": "كوكيز",
    "chocolate": "شوكولاتة", "candy": "حلاوة", "honey": "عسل",
    "coffee": "قهوة", "tea": "شاي", "juice": "عصير", "water": "مياه",
    "oil": "زيت", "sugar": "سكر", "salt": "ملح", "flour": "دقيق",
    "pasta": "مكرونة", "noodles": "نودلز", "sauce": "صلصة",
    "cereal": "كورن فليكس", "oats": "شوفان", "nuts": "مكسرات",
    # رياضة
    "treadmill": "سير كهربائي", "dumbbell": "دمبل", "yoga": "يوجا",
    "bicycle": "دراجة", "ball": "كرة", "gym": "جيم",
    "supplement": "مكمل", "protein": "بروتين",
    # صفات شائعة
    "whitening": "مبيض", "nourishing": "مغذي", "moisturizing": "مرطب",
    "hydrating": "مرطب", "revitalizing": "منعش", "refreshing": "منعش",
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

def translate_to_arabic(text):
    if not text or not re.search(r'[A-Za-z]', text):
        return text

    original = text.lower()
    clean = re.sub(r'[^\w\s]', ' ', original)
    clean = re.sub(r'\s+', ' ', clean).strip()

    # 1) ترجمة العبارات (الأطول أولاً)
    for phrase in sorted(PHRASE_TRANSLATIONS.keys(), key=len, reverse=True):
        if f" {phrase} " in f" {clean} ":
            clean = re.sub(r'\b' + re.escape(phrase) + r'\b', PHRASE_TRANSLATIONS[phrase], clean)

    words = clean.split()
    translated = []
    for w in words:
        if not w:
            continue
        # أرقام ووحدات تفضل كما هي أو تترجم وحداتها فقط
        num_unit = re.match(r'^(\d+(?:\.\d+)?)(ml|l|kg|g|pcs|pc|pack|packs|pair|pairs|set|sets)?$', w)
        if num_unit:
            num = num_unit.group(1)
            unit = num_unit.group(2)
            translated.append(num + (UNITS_MAP.get(unit, unit) if unit else ""))
            continue
        if re.match(r'^\d+$', w):
            translated.append(w)
            continue
        translated.append(WORD_TRANSLATIONS.get(w, w))

    # 2) إعادة الترتيب: [صفة + اسم] <- [اسم + صفة] حسب القواعد العربية
    reordered = []
    i = 0
    while i < len(translated):
        if (i + 1 < len(translated)
                and translated[i] in ARABIC_ADJECTIVES
                and translated[i + 1] not in ARABIC_ADJECTIVES
                and not re.match(r'^\d', translated[i + 1])):
            reordered.append(translated[i + 1])
            reordered.append(translated[i])
            i += 2
        else:
            reordered.append(translated[i])
            i += 1

    result = " ".join(reordered).strip()
    result = re.sub(r'\s+', ' ', result)
    return result

def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"

    # إزالة البراند أولاً عشان ما يدخل في الترجمة
    if found_brand:
        full_title = re.sub(re.escape(found_brand), '', full_title, flags=re.IGNORECASE)

    clean = translate_to_arabic(full_title) if re.search(r'[A-Za-z]', full_title) else full_title
    clean = re.sub(r'\b(الأصلي|جديد|عرض خاص|فقط|للرجال|للنساء)\b', '', clean)

    parts = re.split(r'[-–,|/]', clean)
    words = parts[0].strip().split()[:6]

    bad_endings = ['من', 'عن', 'في', 'على', 'إلى', 'مع', 'أو', 'و', 'الخالي', 'ذو', 'ذات', 'يغذي', 'للبشرة']
    while words and words[-1] in bad_endings:
        words.pop()

    res = " ".join(words).strip()
    return res if res else "منتج مميز"

# ============================================================
# استخراج البراند
# ============================================================
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

    brand_selectors = [
        "#bylineInfo",
        "#bylineInfo_feature_div a",
        "a#bylineInfo",
        ".po-brand .po-break-word",
        "tr.po-brand td.a-span9",
    ]
    for sel in brand_selectors:
        elem = soup.select_one(sel)
        if elem:
            text = elem.get_text(strip=True)
            text = re.sub(r'^(Brand:|الماركة:|العلامة التجارية:|زيارة متجر|Visit the)\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*(Store|متجر)$', '', text, flags=re.IGNORECASE).strip()
            if text and not re.search(r'[\u0600-\u06FF]', text) and len(text) < 40:
                return text

    detail_rows = soup.select(
        "#productOverview_feature_div tr, "
        "#detailBullets_feature_div li, "
        "#productDetails_techSpec_section_1 tr, "
        "#productDetails_detailBullets_sections1 tr"
    )
    for row in detail_rows:
        row_text = row.get_text(" ", strip=True)
        m = re.search(r'(?:Brand|العلامة التجارية|الماركة)\s*[:\-]?\s*(.+)', row_text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            candidate = re.split(r'\s{2,}', candidate)[0].strip()
            if candidate and len(candidate) < 40:
                return candidate

    return ""

def extract_coupons_and_vouchers(soup, current_price=0.0):
    coupon_info = {
        "code": None,
        "voucher_text": None,
        "discount_percent": None,
        "discount_amount": None,
    }
    all_text = soup.get_text(" ", strip=True)
    IGNORED = ["AMAZON", "PRIME", "SHIPPING", "DETAILS", "TERMS", "CHECKOUT", "SELECT", "FREE", "OFFER"]

    code_pattern = re.search(r'(?:كود|رمز|Coupon|Promo|Code|Voucher|كوبون)[:\s\-]*([A-Za-z0-9]{3,15})', all_text, re.IGNORECASE)
    if code_pattern:
        cand = code_pattern.group(1).upper()
        if cand not in IGNORED and len(cand) >= 3:
            coupon_info["code"] = cand

    voucher_selectors = [
        "label[for*='checkbox'] span",
        "#vpcButton",
        ".vouchers-discount-text",
        "#promoPriceBlockMessage_feature_div",
        "#coupon_feature_div",
        ".couponBadge",
        ".couponText",
        ".a-color-success",
        "#promotion_feature_div",
        "[id*='coupon']",
        "[class*='coupon']",
    ]
    voucher_candidates = []
    for sel in voucher_selectors:
        for elem in soup.select(sel):
            v_text = elem.get_text(" ", strip=True)
            if v_text:
                voucher_candidates.append(v_text)

    voucher_candidates.append(all_text)

    KEYWORDS = r'(?:كوبون|قسيمة|خصم\s*إضافي|خصم|وفّر|وفر|Coupon|Voucher|Save|Extra|off)'

    percent_patterns = [
        rf'{KEYWORDS}\D{{0,40}}?(\d{{1,2}})\s*%',
        rf'(\d{{1,2}})\s*%\D{{0,40}}?{KEYWORDS}',
    ]
    amount_patterns = [
        rf'{KEYWORDS}\D{{0,40}}?(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)',
        rf'(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)\D{{0,40}}?{KEYWORDS}',
    ]

    found_percents = set()
    found_amounts = set()

    for text in voucher_candidates:
        for pat in percent_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                try:
                    val = float(m.group(1))
                    if 0 < val <= 90:
                        found_percents.add(val)
                except (ValueError, IndexError):
                    pass
        for pat in amount_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                try:
                    val = float(m.group(1))
                    if val > 0:
                        found_amounts.add(val)
                except (ValueError, IndexError):
                    pass

    best_percent = max(found_percents) if found_percents else None
    best_amount = max(found_amounts) if found_amounts else None

    if best_percent is not None and best_amount is not None and current_price > 0:
        percent_saving = current_price * (best_percent / 100)
        if percent_saving >= best_amount:
            coupon_info["discount_percent"] = best_percent
        else:
            coupon_info["discount_amount"] = best_amount
    elif best_percent is not None:
        coupon_info["discount_percent"] = best_percent
    elif best_amount is not None:
        coupon_info["discount_amount"] = best_amount

    if coupon_info["discount_percent"] is not None:
        coupon_info["voucher_text"] = f"خصم إضافي {int(coupon_info['discount_percent'])}%"
    elif coupon_info["discount_amount"] is not None:
        coupon_info["voucher_text"] = f"خصم إضافي {coupon_info['discount_amount']:.0f} ريال"

    return coupon_info

def extract_best_image(soup, asin):
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront") or soup.select_one("#main-image")
    if img_elem:
        dynamic_img = img_elem.get("data-a-dynamic-image")
        if dynamic_img:
            try:
                img_data = json.loads(dynamic_img)
                best_url = max(img_data.keys(), key=lambda k: img_data[k][0] * img_data[k][1])
                return best_url
            except:
                pass

        src = img_elem.get("src", "")
        if src and "blank" not in src.lower():
            return re.sub(r'\._AC_.*_\.', '._AC_SL1500_.', src)

    if asin:
        return f"https://images-na.ssl-images-amazon.com/images/I/{asin}._AC_SL1500_.jpg"

    return None

def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "🧥", "beauty": "💄", "home": "🧼", "sports": "⚡"}
    return emojis.get(category, "🔥")

def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=12, headers=get_headers())
        return r.url
    except:
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
    nums = re.findall(r'[\d,]+(?:.\d+)?', str(price_text))
    return float(nums[0].replace(",", "")) if nums else 0.0

def extract_prices_advanced(soup, html_content):
    current_price = 0.0
    old_price = 0.0
    page_discount_percent = 0.0

    try:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, list) and len(offers) > 0:
                        current_price = float(offers[0].get('price', 0))
                    elif isinstance(offers, dict):
                        current_price = float(offers.get('price', 0))
    except Exception:
        pass

    if current_price == 0.0:
        price_patterns = [
            r'"priceAmount"\s*:\s*([\d\.]+)',
            r'"buyingPrice"\s*:\s*([\d\.]+)',
            r'"amount"\s*:\s*([\d\.]+)',
            r'priceToPay.*?[\$SRSAR\s]+([\d\.,]+)'
        ]
        for pat in price_patterns:
            match = re.search(pat, html_content, re.IGNORECASE)
            if match:
                val = extract_number(match.group(1))
                if val > 0:
                    current_price = val
                    break

    if current_price == 0.0:
        curr_selectors = [
            ".apexPriceToPay .a-offscreen",
            "#corePrice_feature_div .a-price .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-price-whole",
            ".a-price .a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice"
        ]
        for sel in curr_selectors:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                val = extract_number(elem.text.strip())
                if val > 0:
                    current_price = val
                    break

    old_selectors = [
        ".a-basisPrice .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-text-price .a-offscreen",
        ".a-text-price .a-offscreen",
        "#listPrice"
    ]
    for sel in old_selectors:
        elem = soup.select_one(sel)
        if elem and elem.text.strip():
            val = extract_number(elem.text.strip())
            if val > current_price:
                old_price = val
                break

    # === استخراج نسبة الخصم المعروضة في الصفحة نفسها ===
    percent_selectors = [
        "#corePriceDisplay_desktop_feature_div .savingsPercentage",
        ".a-price-savings .a-offscreen",
        "#savingsPercentage",
        ".savingsPercentage"
    ]
    for sel in percent_selectors:
        elem = soup.select_one(sel)
        if elem:
            m = re.search(r'(\d{1,3})', elem.get_text())
            if m:
                page_discount_percent = float(m.group(1))
                break

    if page_discount_percent == 0.0:
        m = re.search(r'(?:خصم|وفّر|وفر|Save)\s*(\d{1,2})\s*%', soup.get_text(" ", strip=True), re.IGNORECASE)
        if m:
            page_discount_percent = float(m.group(1))

    return current_price, old_price, page_discount_percent

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
        current_p, old_p, page_discount = extract_prices_advanced(soup, html_text)

        found_brand = extract_brand_from_soup(soup, title)
        title_res = clean_arabic_title(title, found_brand)

        package_detail = ""
        size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|حبة|موس|\bL\b|\bml\b|\bkg\b))', title, re.IGNORECASE)
        if size_match:
            package_detail = size_match.group(1)

        coupon_details = extract_coupons_and_vouchers(soup, current_p)
        image_url = extract_best_image(soup, asin)

        price_before_coupon = current_p
        final_price = current_p

        if current_p > 0:
            if coupon_details.get("discount_percent"):
                final_price = round(current_p * (1 - coupon_details["discount_percent"] / 100), 2)
            elif coupon_details.get("discount_amount"):
                final_price = max(round(current_p - coupon_details["discount_amount"], 2), 0)

        return {
            "title_clean": title_res,
            "brand": found_brand,
            "package": package_detail,
            "old_price_num": old_p,
            "current_price_num": final_price,
            "price_before_coupon_num": price_before_coupon if final_price != price_before_coupon else 0.0,
            "page_discount_percent": page_discount,
            "category": detect_product_category(title),
            "coupon_code": coupon_details["code"],
            "voucher_text": coupon_details["voucher_text"],
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_post(product_data, original_url):
    title = html.escape(product_data["title_clean"])
    brand = html.escape(product_data["brand"])
    package = html.escape(product_data["package"])
    category = product_data["category"]
    old_price_num = product_data["old_price_num"]
    current_num = product_data["current_price_num"]
    coupon_code = product_data.get("coupon_code")
    voucher_text = product_data.get("voucher_text")
    page_discount = product_data.get("page_discount_percent", 0.0)

    emoji = get_category_emoji(category)

    brand_str = f"<b>{brand}</b> " if brand else ""
    package_str = f" <b>({package})</b>" if package else ""
    product_item = f"{brand_str}<b>{title}</b>{package_str}"

    dynamic_hook = generate_dynamic_hook(brand)
    lines = [f"{dynamic_hook}\n", f"{emoji} {product_item}\n"]

    if current_num > 0:
        clean_current = f"{int(current_num)} ريال"
        # السعر السابق الموجود في الصفحة كما هو
        effective_old_price = old_price_num
        has_discount = effective_old_price > current_num and effective_old_price > 0

        price_styles = ["old_and_new", "discount_percentage", "simple_price_with_words"]
        selected_style = random.choice(price_styles) if has_discount else "simple_price_with_words"

        if selected_style == "old_and_new":
            phrases = ["السعر قبل الخصم", "السعر المشطوب في الصفحة", "السعر الأصلي", "كان معروض بـ"]
            phrase = random.choice(phrases)
            lines.append(f"❌ {phrase}: <s>{int(effective_old_price)} ريال</s> ← 🔥 الآن: <b>{clean_current}</b> بس 😱")

        elif selected_style == "discount_percentage":
            if page_discount > 0:
                lines.append(f"🔥 السعر الآن: <b>{clean_current}</b> (خصم {int(page_discount)}% مباشر من الصفحة) 😱")
            else:
                calc_percent = int(((effective_old_price - current_num) / effective_old_price) * 100)
                lines.append(f"🔥 السعر الآن: <b>{clean_current}</b> (خصم {calc_percent}%) 😱")

        else:
            word_decorations = ["السعر حالياً بـ", "نازل لـ", "مطلوب فيه الآن", "وصل لسعر"]
            decoration = random.choice(word_decorations)
            lines.append(f"🔥 {decoration}: <b>{clean_current}</b> 😱")

    if coupon_code:
        lines.append(generate_dynamic_coupon_call(coupon_code))
    elif voucher_text:
        lines.append("🎟️ <b>السعر أعلاه شامل خصم القسيمة — فعّلها من نفس صفحة المنتج قبل الطلب ✅</b>")

    lines.append(f"\n{original_url}")
    return "\n".join(lines)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط المنتج من أمازون السعودية لتحويله لبوست احترافي ✨")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        asin = extract_asin(expanded)

        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رمز المنتج (ASIN)، تأكد من صحة الرابط.")
            continue

        target_url = f"https://www.amazon.sa/dp/{asin}"
        wait = bot.reply_to(msg, "⏳ جاري قراءة بيانات المنتج وصنع المنشور...")

        product = fetch_product_details(target_url, asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، حاول مجدداً بعد قليل.", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, original_url)

        try:
            if product.get("image_url"):
                bot.send_photo(msg.chat.id, product["image_url"], caption=post, parse_mode="HTML")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="HTML")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception:
            bot.send_message(msg.chat.id, post, parse_mode="HTML")
            bot.delete_message(msg.chat.id, wait.message_id)

app = Flask(__name__)

@app.route('/')
def index():
    return "🤖 البوت يعمل بأعلى كفاءة 🔥", 200

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
        webhook_url = f"https://{WEBHOOK_HOST}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
    except Exception as e:
        print(f"Webhook setup failed: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
