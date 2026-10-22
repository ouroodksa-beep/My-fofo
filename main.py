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
    "Gillette", "Clorox", "Fine", "Vaseline", "MOTHERCARE", "U.S. POLO", "Pharmaceris"
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
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en-E;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

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
    "mouth wash": "غسول فم"
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
    "tv": "تلفزيون", "screen": "شاشة", "charger": "شاحن", "cable": "كيبل"
}

UNITS_MAP = {
    "ml": "مل", "l": "لتر", "kg": "كيلو", "g": "جرام",
    "pcs": "قطعة", "pc": "قطعة", "pack": "عبوة", "packs": "عبوات"
}

ARABIC_ADJECTIVES = {"مبيض", "مغذي", "مرطب", "منعش", "أصلي", "رجالي", "نسائي", "أطفال", "رياضي", "كهربائي"}

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

def extract_coupons_and_vouchers(soup):
    coupon_info = {"code": None, "discount_percent": None, "discount_amount": None}
    all_text = soup.get_text(" ", strip=True)
    IGNORED = ["AMAZON", "PRIME", "SHIPPING", "DETAILS", "TERMS", "CHECKOUT", "SELECT", "FREE", "OFFER", "SAR"]

    code_pattern = re.search(r'(?:كود|رمز|Coupon|Promo|Code|Voucher|كوبون)[:\s\-]*([A-Za-z0-9]{3,15})', all_text, re.IGNORECASE)
    if code_pattern:
        cand = code_pattern.group(1).upper()
        if cand not in IGNORED and len(cand) >= 3:
            coupon_info["code"] = cand

    found_percents = set()
    KEYWORDS = r'(?:كوبون|قسيمة|خصم\s*إضافي|خصم|وفّر|وفر|Coupon|Voucher|Save|Extra|off)'

    for m in re.finditer(rf'{KEYWORDS}\D{{0,40}}?(\d{{1,2}})\s*%', all_text, re.IGNORECASE):
        found_percents.add(float(m.group(1)))

    if found_percents:
        coupon_info["discount_percent"] = max(found_percents)
    else:
        coupon_info["discount_percent"] = 20.0  # افتراضي للتجربة

    return coupon_info

def extract_best_image(soup, asin):
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
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
    selectors = [
        ".apexPriceToPay .a-offscreen",
        "#corePrice_feature_div .a-price .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-price-whole",
        ".a-price .a-offscreen"
    ]
    for sel in selectors:
        elem = soup.select_one(sel)
        if elem and elem.text.strip():
            val = extract_number(elem.text.strip())
            if val > 0:
                current_price = val
                break
    return current_price, 0.0

def fetch_product_details(url, asin):
    try:
        resp = requests.get(url, headers=get_headers(), timeout=12)
        html_text = resp.text
        soup = BeautifulSoup(resp.content, "html.parser")

        title_elem = soup.select_one("#productTitle") or soup.select_one("h1")
        if not title_elem:
            return None

        title = title_elem.text.strip()
        current_p, _ = extract_prices_advanced(soup, html_text)
        found_brand = extract_brand_from_soup(soup, title)
        title_res = clean_arabic_title(title, found_brand)

        package_detail = ""
        size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|حبة))', title, re.IGNORECASE)
        if size_match:
            package_detail = size_match.group(1)

        coupon_details = extract_coupons_and_vouchers(soup)
        image_url = extract_best_image(soup, asin)

        return {
            "title_clean": title_res,
            "brand": found_brand,
            "package": package_detail,
            "final_price_num": current_p if current_p > 0 else 8.0, # قيمة افتراضية للتجربة لو ما انقرأت
            "coupon_code": coupon_details["code"],
            "discount_percent": coupon_details["discount_percent"],
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

# ============================================================
# توليد المنشور بالتنسيق المتفق عليه بدقة تامة
# ============================================================
def generate_post(product_data, original_url):
    title = html.escape(product_data["title_clean"])
    brand = html.escape(product_data["brand"])
    package = html.escape(product_data["package"])
    price = int(product_data["final_price_num"])
    discount_percent = int(product_data.get("discount_percent", 20))

    # تنسيق اسم المنتج مع الماركة بخط مونو (`brand`)
    if brand:
        product_item = f"سائل أساس من `{brand}` {title}"
    else:
        product_item = title

    if package:
        product_item += f" ({package})"

    # تنويع البدايات الأربع المطلوبة بدون تكرار
    style_choice = random.choice([1, 2, 3, 4])

    if style_choice == 1:
        header = "🔴\n\nالتوفير طالع معك فوق **93%** مع الخصم! 🔥"
    elif style_choice == 2:
        header = "🚨\n\nهذا من الشغلات اللي تتسحب للسلة على طول! 🛒"
    elif style_choice == 3:
        header = "🔥\n\nلحقوا عليه السعر نازل لقطة! 💥"
    else:
        header = "صيييييدة ما تتعوض وتخلص بسرعة! 🎯"

    # صياغة نص السعر بشكل منوع
    price_style = random.choice([1, 2])
    if price_style == 1:
        middle_part = f"{product_item} ✨\nواصل لأفضل سعر بـ **{price} ريال** الحقوه بسرعة 🚀"
    else:
        middle_part = f"{product_item}\nمطلوب فيه الحين **{price} ريال** بلاش والله 💸"

    coupon_part = f"🎟️ خصم إضافي `{discount_percent}%` — فعلوها من صفحة المنتج 👇"

    # التجميع النهائي بدون أي كلمة "اطلبوا" قبل الرابط
    post_lines = [
        header,
        "",
        middle_part,
        coupon_part,
        "",
        original_url
    ]

    return "\n".join(post_lines)

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
