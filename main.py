import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import os
import html

TOKEN = "7956075348:AAFetNzy6ECdP8iHgMWbwQIfjSInomOuhBU"
bot = telebot.TeleBot(TOKEN)

POPULAR_BRANDS = [
    "Apple", "Samsung", "Sony", "Philips", "Dyson", "Braun", "Tefal", "Moulinex", 
    "Pampers", "Nivea", "Dove", "L'Oreal", "Maybelline", "Macvities", "Nadec", 
    "Almarai", "Savola", "Tide", "Persil", "Downy", "Nike", "Adidas", "Puma",
    "الشعلان", "MOTHERCARE", "Gillette", "U.S. POLO", "لافيسيرا", "دوف", "نيفيا",
    "أبل", "سامسونج", "سوني", "فيليبس", "دايسون", "براون", "تيفال", "مولينكس", "شي إن", "نوون"
]

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "هاتف", "آيفون", "لابتوب", "سماعات", "شاحن", "كيبل", "شاشة", "تلفزيون", "ساعة"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "bag", "backpack", "wallet", "belt", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "حذاء", "شنطة", "مكياج", "ملابس", "بوكسر"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "deodorant", "roll-on", "عطر", "عود", "مسك", "كريم", "لوشن", "شامبو", "بلسم", "صابون", "مزيل عرق", "مغذي", "رول", "حلاقة", "موس"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "blender", "mixer", "oven", "microwave", "kettle", "coffee maker", "iron", "ارز", "رز", "حليب", "بسكويت", "منعم", "ثلاجة", "غسالة", "مكنسة", "مكيف", "خلاط", "فرن", "غلاية", "مطبخ", "غسول"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "sport", "رياضة", "جيم", "تمارين", "دراجة"]
}

# ==================== DYNAMIC HOOK GENERATOR ====================
def generate_dynamic_hook(brand=""):
    emojis = ["🚨", "🔥", "⚡", "💥", "🎯", "🛍️", "💣", "✨", "📣", "🏷️", "🚀", "🎉", "💎", "👁️", "💸"]
    openers = [
        "تنبيه عاجل", "صيدة اليوم", "نزول مفاجئ بالسعر", "عرض لا يتكرر", "فرصة توفير جبارة",
        "لقطة ممتازة", "سعر حارق الآن", "صفقة استثنائية", "تخفيض قوي جداً", "انخفاض ممتاز",
        "عروض اللحظة الأخيرة", "عينكم على الخصم", "صيدة رايقة", "توفير قوي", "خصم خيالي"
    ]
    actions = [
        "الحقوا العرض قبل النفاد", "لا تفوتوا هذه الفرصة", "بسعر يابلاش الآن", "وفر فلوسك واطلب فوراً",
        "طايح السعر بشكل ممتاز", "السعر صار بلاش", "من أقوى صيدات الساعة", "فرصة ممتازة للطلب",
        "تم تحديث الخصم ليكون الأفضل", "سعر ممتاز جداً لليوم"
    ]
    
    emoji = random.choice(emojis)
    opener = random.choice(openers)
    action = random.choice(actions)
    
    if brand and random.choice([True, False]):
        return f"{emoji} <b>الحقوا على عروض {brand}.. {action}!</b>"
    else:
        return f"{emoji} <b>{opener}.. {action}!</b>"

# ==================== DYNAMIC COUPON CALL GENERATOR ====================
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

TRANSLATION_DICT = {
    "deodorant": "مزيل عرق", "roll-on": "مزيل عرق رول", "cream": "كريم", "lotion": "لوشن",
    "shampoo": "شامبو", "soap": "صابون", "hand wash": "غسول يدين", "body wash": "غسول جسم",
    "perfume": "عطر", "shoes": "حذاء", "t-shirt": "تيشيرت", "bag": "حقيبة", "watch": "ساعة",
    "headphones": "سماعات", "charger": "شاحن", "laptop": "لابتوب", "whitening": "مبيض",
    "nourishing": "مغذي", "original": "أصلي", "men": "رجالي", "women": "نسائي"
}

def translate_to_arabic(text):
    words = text.lower().split()
    translated_words = []
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            translated_words.append(word)
    return " ".join(translated_words)

def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"
    
    if re.search(r'[A-Za-z]', full_title):
        clean = translate_to_arabic(full_title)
    else:
        clean = full_title

    clean = re.sub(r'\b(الأصلي|جديد|عرض خاص|فقط|للرجال|للنساء)\b', '', clean)
    
    if found_brand:
        clean = re.sub(re.escape(found_brand), '', clean, flags=re.IGNORECASE)

    parts = re.split(r'[-–,|/]', clean)
    main_part = parts[0].strip()
    
    words = main_part.split()[:5]
    
    bad_endings = ['من', 'عن', 'في', 'على', 'إلى', 'مع', 'أو', 'و', 'الخالي', 'ذو', 'ذات', 'يغذي', 'الدوار']
    while words and words[-1] in bad_endings:
        words.pop()
        
    res = " ".join(words).strip()
    return res if res else "منتج مميز"

def extract_product_details(full_title):
    found_brand = ""
    for brand in POPULAR_BRANDS:
        if brand.lower() in full_title.lower():
            found_brand = brand
            break

    package_detail = ""
    size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|سم|حبة|موس|\bL\b|\bml\b|\bkg\b))', full_title, re.IGNORECASE)
    if size_match:
        package_detail = size_match.group(1)

    title_res = clean_arabic_title(full_title, found_brand)
    return title_res, found_brand, package_detail

def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "🧥", "beauty": "💄", "home": "🧼", "sports": "⚡"}
    return emojis.get(category, "🔥")

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl', 'link.amazon']):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            }
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
            if 'link.amazon' in url.lower():
                soup = BeautifulSoup(r.text, "html.parser")
                canonical = soup.select_one('link[rel="canonical"]')
                if canonical:
                    href = canonical.get('href', '')
                    asin_match = re.search(r'/dp/([A-Z0-9]{9,10})', href)
                    if asin_match:
                        return f"https://www.amazon.sa/dp/{asin_match.group(1)}"
            return r.url
        return url
    except:
        return url

def is_saudi_amazon(url):
    return "amazon.sa" in url.lower() or "link.amazon" in url.lower()

def extract_asin(url):
    patterns = [r'/dp/([A-Z0-9]{9,10})', r'/gp/product/([A-Z0-9]{9,10})', r'link\.amazon/([A-Za-z0-9]{9,10})', r'([A-Z0-9]{9,10})/?$']
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1).upper()
    return None

def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            return f"{int(float(num_str))} ريال"
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

def extract_coupons_and_vouchers(soup):
    coupon_info = {"code": None, "voucher_text": None}
    all_text = soup.get_text()
    
    code_pattern = re.search(r'(?:كود|رمز|Coupon|Promo|Code)[:\s\-]*([A-Z0-9]{4,12})', all_text, re.IGNORECASE)
    if code_pattern:
        cand = code_pattern.group(1).upper()
        if cand not in ["AMAZON", "PRIME", "SHIPPING", "DETAILS"]:
            coupon_info["code"] = cand

    if not coupon_info["code"]:
        selectors = [
            "#couponText", ".promoPriceBlockMessage", ".vouchers-one-time-code", 
            "#couponBadge", "span.a-declarative[data-action='a-modal']", ".sns-coupon-details",
            "span.a-color-success", "div[id*='coupon']"
        ]
        for sel in selectors:
            for elem in soup.select(sel):
                text = elem.text.strip()
                match = re.search(r'\b([A-Z0-9]{5,10})\b', text)
                if match:
                    val = match.group(1)
                    if val not in ["OFF", "SAR", "AED", "GET", "SAVE", "AMAZON", "DETAILS"]:
                        coupon_info["code"] = val
                        break
            if coupon_info["code"]:
                break

    voucher_selectors = [
        "label[for*='checkbox'] span", "#vpcButton", ".a-section .a-color-success", 
        ".vouchers-discount-text", "#item_coupon_vt", ".badge-link", "span[id*='couponText']"
    ]
    for sel in voucher_selectors:
        for elem in soup.select(sel):
            v_text = elem.text.strip()
            if any(k in v_text for k in ["كوبون", "خصم", "voucher", "coupon", "توفير", "%", "ريال"]):
                discount_match = re.search(r'(\d+%\s*خصم|خصم\s*\d+%|\d+\s*ريال\s*خصم|خصم\s*\d+\s*ريال)', v_text)
                if discount_match:
                    coupon_info["voucher_text"] = discount_match.group(1)
                    break
        if coupon_info["voucher_text"]:
            break

    return coupon_info

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
        "Referer": "https://www.amazon.sa/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        
        title_elem = soup.select_one("#productTitle")
        if not title_elem:
            return None
        title = title_elem.text.strip()

        price = ""
        price_elem = soup.select_one(".a-price .a-offscreen") or soup.select_one("#priceblock_ourprice") or soup.select_one(".priceToPay")
        if price_elem:
            price = price_elem.text.strip()

        old_price_elem = soup.select_one(".a-text-price .a-offscreen")
        old_price = old_price_elem.text.strip() if old_price_elem else None

        img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
        image = img_elem.get("src") if img_elem else None

        title_res, brand_res, package_res = extract_product_details(title)
        category = detect_product_category(title)
        coupon_details = extract_coupons_and_vouchers(soup)

        return {
            "title_clean": title_res,
            "brand": brand_res,
            "package": package_res,
            "price": price,
            "old_price_num": extract_number(old_price) if old_price else 0,
            "current_price_num": extract_number(price),
            "image": image,
            "category": category,
            "coupon_code": coupon_details["code"],
            "voucher_text": coupon_details["voucher_text"]
        }
    except:
        return None

def generate_post(product_data, original_url):
    title = html.escape(product_data["title_clean"])
    brand = html.escape(product_data["brand"])
    package = html.escape(product_data["package"])
    price = product_data["price"]
    category = product_data["category"]
    old_price_num = product_data["old_price_num"]
    current_num = product_data["current_price_num"]
    coupon_code = product_data.get("coupon_code")
    voucher_text = product_data.get("voucher_text")
    
    clean_current = clean_price(price) if price and price != "0" else None
    emoji = get_category_emoji(category)

    brand_str = f"<b>{brand}</b> " if brand else ""
    package_str = f" <b>({package})</b>" if package else ""
    product_item = f"{brand_str}<b>{title}</b>{package_str}"

    discount_line = ""
    if old_price_num > current_num and old_price_num > 0:
        discount_percent = int(((old_price_num - current_num) / old_price_num) * 100)
        if discount_percent > 0:
            discount_line = f"🔥 <b>خصم قوي بنسبة {discount_percent}%!</b>"

    coupon_line = ""
    if coupon_code:
        coupon_line = generate_dynamic_coupon_call(coupon_code)
    elif voucher_text:
        coupon_line = f"🎟️ <b>تأكدوا من تفعيل القسيمة ({html.escape(voucher_text)}) في الصفحة!</b>"

    dynamic_hook = generate_dynamic_hook(brand)
    style_choice = random.choice([1, 2, 3, 4])
    lines = []

    if style_choice == 1:
        lines.append(f"{dynamic_hook}\n")
        lines.append(f"{emoji} {product_item}\n")
        if clean_current:
            if old_price_num > current_num and old_price_num > 0:
                lines.append(f"❌ قبل: <s>{int(old_price_num)} ريال</s> ← 🔥 الآن: <b>{clean_current}</b> بس 😱")
            else:
                lines.append(f"🔥 السعر الحالي: <b>{clean_current}</b> 😱🔥")
        if discount_line:
            lines.append(discount_line)
        if coupon_line:
            lines.append(coupon_line)

    elif style_choice == 2:
        lines.append(f"{dynamic_hook}\n")
        if clean_current:
            if old_price_num > current_num and old_price_num > 0:
                lines.append(f"🔥 نازل من <s>{int(old_price_num)} ريال</s> لـ <b>{clean_current}</b> بس! 😱")
            else:
                lines.append(f"🔥 السعر الحالي المميز: <b>{clean_current}</b> 😱")
        if discount_line:
            lines.append(discount_line)
        lines.append(f"\n{emoji} المنتج: {product_item}")
        if coupon_line:
            lines.append(coupon_line)

    elif style_choice == 3:
        lines.append(f"{dynamic_hook}\n")
        lines.append(f"{emoji} {product_item}\n")
        if coupon_line:
            lines.append(coupon_line)
        if discount_line:
            lines.append(discount_line)
        if clean_current:
            lines.append(f"🔥 السعر الحالي: <b>{clean_current}</b> 😱")

    else:
        lines.append(f"{dynamic_hook}\n")
        lines.append(f"{emoji} {product_item}\n")
        if clean_current:
            lines.append(f"💰 السعر المطلوب: <b>{clean_current}</b>")
        if discount_line:
            lines.append(discount_line)
        if coupon_line:
            lines.append(coupon_line)

    # إرجاع الرابط كنص عادي في آخر البوست تماماً كما أرسلتيه
    lines.append(f"\n{original_url}")

    return "\n".join(lines)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أهلاً بك! أرسل رابط المنتج من أمازون السعودية لتحويله لبوست صيدات احترافي ✨")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ عذراً، البوت مخصص لأمازون السعودية فقط.")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج من الرابط.")
            continue

        wait = bot.reply_to(msg, "⏳ جاري جلب التفاصيل وقراءة الأكواد وتنسيق المنشور...")

        product = get_product(asin)
        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، تأكد من صحة الرابط.", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post, parse_mode="HTML")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="HTML")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception:
            bot.send_message(msg.chat.id, post, parse_mode="HTML")
            bot.delete_message(msg.chat.id, wait.message_id)

# ============ WEBHOOK SERVER ============
from flask import Flask, request

app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route('/')
def index():
    return "🤖 البوت يعمل بأعلى كفاءة 🔥"

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Unsupported Media Type', 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

if __name__ == '__main__':
    start_webhook()
