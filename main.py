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

TOKEN = "7956075348:AAEbIrxXc0xOh1jeMcWlYfRF1Qw5jENjv3U"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

# ============================================================
# جمل افتتاحية بلهجة سعودية عامية ومباشرة
# ============================================================
def generate_dynamic_hook(brand=""):
    emojis = ["🚨", "🔥", "⚡", "💥", "🎯", "🛍️", "💣", "✨", "📣", "🏷️", "🚀", "🎉", "💎", "💸", "😱"]
    openers = [
        "يا بلاش! طاح سعره اليوم بشكل مو طبيعي",
        "من أطلق العروض اللي مرت علي اليوم",
        "صيدة رهيبة للي يبي يطلب الحين",
        "لحقوا عليه السعر نازل لقطة",
        "هذا من الشغلات اللي تتسحب للسلة على طول",
        "السعر طايح والفرصة ما تتفوت أبداً",
        "خصم حقيقي ويستاهل نطلبه فوراً",
        "من زمان ما نزل لهالسعر الجبار",
        "لقطة اليوم وبفرق سعر واضح جداً",
        "لا تترددون السعر نزوله يجنن اليوم",
        "عروض اليوم مولعة وهذا أقواها",
        "فرصة توفير رهيبة للي يحتاجه"
    ]
    if brand:
        openers += [
            f"خصم {brand} اليوم يفتح النفس صراحة",
            f"نزول خرافي بمنتجات {brand} الحقوا عليه",
            f"عروض {brand} المباشرة نازلة بسعر قوي"
        ]

    return f"{random.choice(emojis)} <b>{random.choice(openers)}!</b>"

# ============================================================
# دعوة واستخدام الكوبون بأساليب متنوّعة وبلهجة سعودية
# ============================================================
def generate_dynamic_coupon_call(code):
    icons = ["🎟️", "🏷️", "🔑", "💥", "🎁", "✨", "📌"]
    phrases = [
        "لا تنسون تطبقون كود الخصم عند الدفع",
        "وفّروا أكثر واستخدموا الكود هذا",
        "ادخلوا هالكود وفعلوا التخفيض الإضافي",
        "انسخوا كود الخصم وطبقوه بالسلة",
        "طبّقوا هالرمز الإضافي قبل تطلبون",
        "حطوا هذا الكود عشان يخصم لكم زيادة"
    ]
    return f"{random.choice(icons)} <b>{random.choice(phrases)}:</b> <code>{html.escape(code)}</code>"

def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"

PHRASE_TRANSLATIONS = {
    "roll on": "مزيل عرق رول", "roll-on": "مزيل عرق رول",
    "body wash": "غسول جسم", "hand wash": "غسول يدين",
    "face wash": "غسول وجه", "hair wash": "شامبو",
    "shower gel": "جل استحمام", "body lotion": "لوشن جسم",
    "face cream": "كريم وجه", "eye cream": "كريم عيون",
    "hair oil": "زيت شعر", "hair serum": "سيرم شعر",
    "air fryer": "قلاية هوائية", "washing machine": "غسالة ملابس",
    "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف",
    "coffee maker": "صانعة قهوة", "electric kettle": "غلاية كهربائية",
    "power bank": "باور بانك", "smart watch": "ساعة ذكية",
    "wireless earbuds": "سماعات لاسلكية", "wireless headphones": "سماعات رأس لاسلكية",
    "bluetooth speaker": "مكبر صوت بلوتوث", "phone case": "كفر جوال",
    "screen protector": "حماية شاشة", "charging cable": "كيبل شحن",
    "wall charger": "شاحن جداري", "car charger": "شاحن سيارة",
    "baby diapers": "حفاضات أطفال", "baby wipes": "مناديل أطفال",
    "tooth paste": "معجون أسنان", "tooth brush": "فرشاة أسنان",
    "mouth wash": "غسول فم", "extra virgin olive oil": "زيت زيتون بكر"
}

WORD_TRANSLATIONS = {
    "deodorant": "مزيل عرق", "cream": "كريم", "lotion": "لوشن",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "perfume": "عطر", "fragrance": "عطر", "oud": "عود", "musk": "مسك",
    "makeup": "مكياج", "lipstick": "أحمر شفاه", "mascara": "ماسكارا",
    "blush": "بلاشر", "serum": "سيرم", "scrub": "مقشر", "toner": "تونر",
    "cleanser": "غسول", "moisturizer": "مرطب", "sunscreen": "واقي شمس",
    "shirt": "قميص", "tshirt": "تيشيرت", "pants": "بنطلون", "jeans": "جينز",
    "jacket": "جاكيت", "hoodie": "هودي", "dress": "فستان", "shoes": "حذاء",
    "sneakers": "سنيكرز", "bag": "شنطة", "backpack": "شنطة ظهر", "watch": "ساعة",
    "phone": "جوال", "iphone": "آيفون", "laptop": "لابتوب", "tablet": "تابلت",
    "headphones": "سماعات", "speaker": "مكبر صوت", "camera": "كاميرا",
    "tv": "تلفزيون", "screen": "شاشة", "charger": "شاحن", "cable": "كيبل",
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "blender": "خلاط",
    "oven": "فرن", "microwave": "مايكرويف", "kettle": "غلاية", "iron": "مكواة",
    "rice": "أرز", "milk": "حليب", "biscuits": "بسكويت", "chocolate": "شوكولاتة",
    "coffee": "قهوة", "tea": "شاي", "juice": "عصير", "water": "مياه", "oil": "زيت"
}

UNITS_MAP = {
    "ml": "مل", "l": "لتر", "kg": "كيلو", "g": "جرام",
    "pcs": "قطعة", "pc": "قطعة", "pack": "عبوة", "packs": "عبوات"
}

ARABIC_ADJECTIVES = {
    "مبيض", "مغذي", "مرطب", "منعش", "أصلي", "رجالي", "نسائي",
    "أطفال", "رياضي", "كهربائي", "رقمي", "محمول", "لاسلكي"
}

def translate_to_arabic(text):
    if not text or not re.search(r'[A-Za-z]', text):
        return text
    original = text.lower()
    clean = re.sub(r'[^\w\s]', ' ', original)
    clean = re.sub(r'\s+', ' ', clean).strip()

    for phrase in sorted(PHRASE_TRANSLATIONS.keys(), key=len, reverse=True):
        if f" {phrase} " in f" {clean} ":
            clean = re.sub(r'\b' + re.escape(phrase) + r'\b', PHRASE_TRANSLATIONS[phrase], clean)

    words = clean.split()
    translated = []
    for w in words:
        if not w:
            continue
        num_unit = re.match(r'^(\d+(?:\.\d+)?)(ml|l|kg|g|pcs|pc|pack|packs)?$', w)
        if num_unit:
            num = num_unit.group(1)
            unit = num_unit.group(2)
            translated.append(num + (UNITS_MAP.get(unit, unit) if unit else ""))
            continue
        if re.match(r'^\d+$', w):
            translated.append(w)
            continue
        translated.append(WORD_TRANSLATIONS.get(w, w))

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
    return re.sub(r'\s+', ' ', result)

def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"
    if found_brand:
        full_title = re.sub(re.escape(found_brand), '', full_title, flags=re.IGNORECASE)
    clean = translate_to_arabic(full_title) if re.search(r'[A-Za-z]', full_title) else full_title
    clean = re.sub(r'\b(الأصلي|جديد|عرض خاص|فقط)\b', '', clean)
    parts = re.split(r'[-–,|/]', clean)
    words = parts[0].strip().split()[:6]
    return " ".join(words).strip() if words else "منتج مميز"

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
    elem = soup.select_one("#bylineInfo, #bylineInfo_feature_div a, .po-brand .po-break-word")
    if elem:
        text = elem.get_text(strip=True)
        text = re.sub(r'^(Brand:|الماركة:|العلامة التجارية:|زيارة متجر|Visit the)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*(Store|متجر)$', '', text, flags=re.IGNORECASE).strip()
        if text and len(text) < 40:
            return text
    return ""

def extract_coupons_and_vouchers(soup, current_price=0.0):
    coupon_info = {"code": None, "voucher_text": None, "discount_percent": None, "discount_amount": None}
    all_text = soup.get_text(" ", strip=True)
    IGNORED = ["AMAZON", "PRIME", "SHIPPING", "DETAILS", "TERMS", "CHECKOUT", "SELECT", "FREE", "OFFER", "SAR"]

    code_pattern = re.search(r'(?:كود|رمز|Coupon|Promo|Code|Voucher|كوبون)[:\s\-]*([A-Za-z0-9]{3,15})', all_text, re.IGNORECASE)
    if code_pattern:
        cand = code_pattern.group(1).upper()
        if cand not in IGNORED and len(cand) >= 3:
            coupon_info["code"] = cand

    voucher_candidates = []
    for sel in ["label[for*='checkbox'] span", "#vpcButton", ".vouchers-discount-text", "#coupon_feature_div", ".couponText"]:
        for elem in soup.select(sel):
            if elem.get_text(strip=True):
                voucher_candidates.append(elem.get_text(" ", strip=True))
    voucher_candidates.append(all_text)

    found_percents, found_amounts = set(), set()
    KEYWORDS = r'(?:كوبون|قسيمة|خصم\s*إضافي|خصم|وفّر|وفر|Coupon|Voucher|Save|Extra|off)'

    for text in voucher_candidates:
        for m in re.finditer(rf'{KEYWORDS}\D{{0,40}}?(\d{{1,2}})\s*%', text, re.IGNORECASE):
            found_percents.add(float(m.group(1)))
        for m in re.finditer(rf'(\d{{1,2}})\s*%\D{{0,40}}?{KEYWORDS}', text, re.IGNORECASE):
            found_percents.add(float(m.group(1)))
        for m in re.finditer(rf'{KEYWORDS}\D{{0,40}}?(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)', text, re.IGNORECASE):
            found_amounts.add(float(m.group(1)))

    if found_percents:
        coupon_info["discount_percent"] = max(found_percents)
        coupon_info["voucher_text"] = f"خصم إضافي {int(coupon_info['discount_percent'])}%"
    elif found_amounts:
        coupon_info["discount_amount"] = max(found_amounts)
        coupon_info["voucher_text"] = f"خصم إضافي {coupon_info['discount_amount']:.0f} ريال"

    return coupon_info

def extract_best_image(soup, asin):
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront") or soup.select_one("#main-image")
    if img_elem:
        dynamic_img = img_elem.get("data-a-dynamic-image")
        if dynamic_img:
            try:
                img_data = json.loads(dynamic_img)
                return max(img_data.keys(), key=lambda k: img_data[k][0] * img_data[k][1])
            except:
                pass
        src = img_elem.get("src", "")
        if src and "blank" not in src.lower():
            return re.sub(r'\._AC_.*_\.', '._AC_SL1500_.', src)
    if asin:
        return f"https://images-na.ssl-images-amazon.com/images/I/{asin}._AC_SL1500_.jpg"
    return None

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
    cleaned = str(price_text).replace('\xa0', ' ').replace(',', '').strip()
    nums = re.findall(r'\d+(?:\.\d+)?', cleaned)
    return float(nums[0]) if nums else 0.0

def extract_prices_advanced(soup, html_content):
    current_price = 0.0
    old_price = 0.0

    try:
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and 'offers' in item:
                        offers = item['offers']
                        if isinstance(offers, list) and len(offers) > 0:
                            current_price = float(offers[0].get('price', 0))
                        elif isinstance(offers, dict):
                            current_price = float(offers.get('price', 0))
                    if current_price > 0:
                        break
    except Exception:
        pass

    if current_price == 0.0:
        patterns = [
            r'"priceAmount"\s*:\s*([\d\.]+)',
            r'"buyingPrice"\s*:\s*([\d\.]+)',
            r'"displayPrice"\s*:\s*"([\d\.,]+)"',
            r'"price"\s*:\s*([\d\.]+)',
            r'priceToPay.*?([\d\.,]+)'
        ]
        for pat in patterns:
            match = re.search(pat, html_content, re.IGNORECASE)
            if match:
                val = extract_number(match.group(1))
                if val > 0:
                    current_price = val
                    break

    if current_price == 0.0:
        selectors = [
            ".apexPriceToPay .a-offscreen",
            "#corePrice_feature_div .a-price .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-price-whole",
            ".a-price .a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice"
        ]
        for sel in selectors:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                val = extract_number(elem.text.strip())
                if val > 0:
                    current_price = val
                    break

    old_selectors = [
        "#corePriceDisplay_desktop_feature_div .a-text-price .a-offscreen",
        ".a-basisPrice .a-offscreen",
        "#corePrice_desktop .a-text-price .a-offscreen",
        "#listPrice"
    ]
    for sel in old_selectors:
        elem = soup.select_one(sel)
        if elem and elem.text.strip():
            val = extract_number(elem.text.strip())
            if val > current_price:
                old_price = val
                break

    return current_price, old_price

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
        current_p, old_p = extract_prices_advanced(soup, html_text)

        found_brand = extract_brand_from_soup(soup, title)
        title_res = clean_arabic_title(title, found_brand)

        package_detail = ""
        size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|حبة))', title, re.IGNORECASE)
        if size_match:
            package_detail = size_match.group(1)

        coupon_details = extract_coupons_and_vouchers(soup, current_p)
        image_url = extract_best_image(soup, asin)

        final_price = current_p

        # ========================================================
        # حساب السعر النهائي المباشر بالخصم (بدون إظهار السعر قبل الخصم)
        # ========================================================
        if current_p > 0:
            if coupon_details.get("discount_percent"):
                percent = coupon_details["discount_percent"]
                final_price = round(current_p * (1 - percent / 100), 2)
            elif coupon_details.get("discount_amount"):
                amount = coupon_details["discount_amount"]
                final_price = max(round(current_p - amount, 2), 0)

        return {
            "title_clean": title_res,
            "brand": found_brand,
            "package": package_detail,
            "old_price_num": old_p,
            "final_price_num": final_price,
            "category": detect_product_category(title),
            "coupon_code": coupon_details["code"],
            "voucher_text": coupon_details["voucher_text"],
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

# ============================================================
# توليد المنشور بتنوع ديناميكي ولهجة سعودية جذابة
# ============================================================
def generate_post(product_data, original_url):
    title = html.escape(product_data["title_clean"])
    brand = html.escape(product_data["brand"])
    package = html.escape(product_data["package"])
    category = product_data["category"]
    old_price_num = product_data["old_price_num"]
    final_price = product_data["final_price_num"]
    coupon_code = product_data.get("coupon_code")
    voucher_text = product_data.get("voucher_text")

    emoji = {"electronics": "📱", "fashion": "🧥", "beauty": "💄", "home": "🧼", "sports": "⚡"}.get(category, "🔥")

    brand_str = f"<b>{brand}</b> " if brand else ""
    package_str = f" <b>({package})</b>" if package else ""
    product_item = f"{brand_str}<b>{title}</b>{package_str}"

    dynamic_hook = generate_dynamic_hook(brand)
    lines = [f"{dynamic_hook}\n", f"{emoji} {product_item}\n"]

    if final_price > 0:
        clean_final = f"<b>{int(final_price)} ريال</b>"

        # تنوع عشوائي في طريقة عرض الأسعار (مرة يظهر السعر السابق المشطوب ومرة يظهر السعر النهائي مباشرة)
        show_old_price = random.choice([True, False])

        if old_price_num > final_price and show_old_price:
            price_phrases = [
                f"❌ كان بـ <s>{int(old_price_num)} ريال</s> ← الحين بـ {clean_final} بس 😱",
                f"السعر السابق: <s>{int(old_price_num)} ريال</s> | طاح لـ {clean_final} 🔥",
                f"فرق السعر جبار! نزل من <s>{int(old_price_num)} ريال</s> إلى {clean_final} ⚡"
            ]
            lines.append(random.choice(price_phrases))
        else:
            final_phrases = [
                f"🔥 السعر الحين نازل لـ {clean_final} بس! 😱",
                f"💥 مطلوب فيه الحين {clean_final} بلاش والله 💸",
                f"✨ واصل لأفضل سعر بـ {clean_final} لحقوا عليه 🚀"
            ]
            lines.append(random.choice(final_phrases))

        # حساب نسبة التوفير الكلية لو كانت مشجعة
        if old_price_num > final_price:
            calc_percent = int(((old_price_num - final_price) / old_price_num) * 100)
            if calc_percent >= 20 and random.choice([True, False]):
                lines.append(f"🎯 (التوفير طالع معك فوق {calc_percent}% مع الخصم)")

    # كود الخصم أو القسيمة
    if coupon_code:
        lines.append("\n" + generate_dynamic_coupon_call(coupon_code))
    elif voucher_text:
        lines.append(f"\n🎟️ <b>{voucher_text} — فعلوها من صفحة المنتج قبل تطلبون ✅</b>")

    # Call To Action جذاب ومباشر باسم المنتج وبدون عبارات رسمية
    cta_phrases = [
        f"👇 اطلبوا {title} من هنا قبل يخلص العرض:",
        f"👇 للطلب المباشر لـ {title} اضغطوا الرابط:",
        f"👇 الحقوا على {title} اطلبوه من هنا:"
    ]
    lines.append(f"\n{random.choice(cta_phrases)}\n{original_url}")

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
