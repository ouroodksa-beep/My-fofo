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
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }

def generate_dynamic_hook(brand=""):
    emojis = ["🚨", "🔥", "⚡", "💥", "🎯", "🛍️", "💣", "✨", "📣", "🏷️", "🚀", "🎉", "💎", "👁️", "💸", "😱", "📢"]
    openers = [
        "تنبيه عاجل", "صيدة اليوم", "نزول مفاجئ بالسعر", "عرض لا يتكرر", "فرصة توفير جبارة",
        "لقطة ممتازة", "سعر حارق الآن", "صفقة استثنائية", "تخفيض قوي جداً", "انخفاض ممتاز",
        "عروض اللحظة الأخيرة", "عينكم على الخصم", "صيدة رايقة", "توفير قوي", "خصم خيالي",
        "يارب لحقتوا عليه", "شوفوا العرض الخيالي", "يا بلاش والله"
    ]
    actions = [
        "الحقوا العرض قبل النفاد", "لا تفوتوا هذه الفرصة", "بسعر يابلاش الآن", "وفر فلوسك واطلب فوراً",
        "طايح السعر بشكل ممتاز", "السعر صار بلاش", "من أقوى صيدات الساعة", "فرصة ممتازة للطلب",
        "تم تحديث الخصم ليكون الأفضل", "سعر ممتاز جداً لليوم", "قبل ما يرجع لسعره الاصلي"
    ]
    
    emoji = random.choice(emojis)
    opener = random.choice(openers)
    action = random.choice(actions)
    
    if brand and random.choice([True, False]):
        return f"{emoji} <b>الحقوا على عروض {brand}.. {action}!</b>"
    else:
        return f"{emoji} <b>{opener}.. {action}!</b>"

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
    translated_words = [TRANSLATION_DICT.get(re.sub(r'[^\w\s]', '', w), w) for w in words]
    return " ".join(translated_words)

def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"
    
    clean = translate_to_arabic(full_title) if re.search(r'[A-Za-z]', full_title) else full_title
    clean = re.sub(r'\b(الأصلي|جديد|عرض خاص|فقط|للرجال|للنساء)\b', '', clean)
    
    if found_brand:
        clean = re.sub(re.escape(found_brand), '', clean, flags=re.IGNORECASE)

    parts = re.split(r'[-–,|/]', clean)
    words = parts[0].strip().split()[:5]
    
    bad_endings = ['من', 'عن', 'في', 'على', 'إلى', 'مع', 'أو', 'و', 'الخالي', 'ذو', 'ذات', 'يغذي']
    while words and words[-1] in bad_endings:
        words.pop()
        
    res = " ".join(words).strip()
    return res if res else "منتج مميز"

def extract_brand_from_soup(soup, full_title):
    for brand in POPULAR_BRANDS:
        if brand.lower() in full_title.lower():
            return brand

    brand_elem = soup.select_one("#bylineInfo, .po-brand .a-span9, #bylineInfo_feature_div, a#bylineInfo")
    if brand_elem:
        text = re.sub(r'^(Brand:|الماركة:|زيارة متجر|Visit the|Store|\s+)+', '', brand_elem.text.strip(), flags=re.IGNORECASE)
        if text and not re.search(r'[\u0600-\u06FF]', text):
            return text
    return ""

def extract_coupons_and_vouchers(soup):
    coupon_info = {"code": None, "voucher_text": None}
    all_text = soup.get_text()
    IGNORED = ["AMAZON", "PRIME", "SHIPPING", "DETAILS", "TERMS", "CHECKOUT", "SELECT", "FREE", "OFFER"]

    code_pattern = re.search(r'(?:كود|رمز|Coupon|Promo|Code|Voucher|كوبون)[:\s\-]*([A-Za-z0-9]{3,15})', all_text, re.IGNORECASE)
    if code_pattern:
        cand = code_pattern.group(1).upper()
        if cand not in IGNORED and len(cand) >= 3:
            coupon_info["code"] = cand

    voucher_selectors = ["label[for*='checkbox'] span", "#vpcButton", ".vouchers-discount-text"]
    for sel in voucher_selectors:
        for elem in soup.select(sel):
            v_text = elem.text.strip()
            if any(k in v_text for k in ["كوبون", "خصم", "voucher", "coupon", "%", "ريال"]):
                discount_match = re.search(r'(\d+%\s*خصم|خصم\s*\d+%|\d+\s*ريال\s*خصم|خصم\s*\d+\s*ريال)', v_text, re.IGNORECASE)
                if discount_match:
                    coupon_info["voucher_text"] = discount_match.group(1)
                    break
    return coupon_info

# ==================== استخراج الصورة المضمونة بجودة عالية بدقة ====================
def extract_best_image(soup, asin):
    # الطريقة 1: البحث عن جودة الصورة العالية من الـ HTML مباشرة
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront") or soup.select_one("#main-image")
    if img_elem:
        dynamic_img = img_elem.get("data-a-dynamic-image")
        if dynamic_img:
            try:
                img_data = json.loads(dynamic_img)
                # جلب أعلى جودة ممكنة للصورة الحقيقية
                best_url = max(img_data.keys(), key=lambda k: img_data[k][0] * img_data[k][1])
                return best_url
            except:
                pass
        
        src = img_elem.get("src", "")
        if src and "blank" not in src.lower():
            # تحويل الرابط العادي إلى رابط عالي الجودة مقاس 1500px
            return re.sub(r'\._AC_.*_\.', '._AC_SL1500_.', src)

    # الطريقة 2: رابط صورة أمازون عالي الجودة المضمون (1500px) بدلاً من الرابط الأبيص
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

def clean_price(price_text):
    nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
    if nums:
        return f"{int(float(nums[0].replace(',', '')))} ريال"
    return price_text

def extract_number(price_text):
    nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
    return float(nums[0].replace(",", "")) if nums else 0

def fetch_product_details(url, asin):
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")

        title_elem = soup.select_one("#productTitle") or soup.select_one("h1")
        
        if not title_elem or "captcha" in resp.text.lower():
            resp = requests.get(f"https://corsproxy.io/?{url}", headers=get_headers(), timeout=12)
            soup = BeautifulSoup(resp.content, "html.parser")
            title_elem = soup.select_one("#productTitle") or soup.select_one("h1")

        if not title_elem:
            return None

        title = title_elem.text.strip()
        price_elem = soup.select_one(".a-price .a-offscreen") or soup.select_one("#priceblock_ourprice") or soup.select_one(".a-price-whole")
        price = price_elem.text.strip() if price_elem else ""

        old_price_elem = soup.select_one(".a-text-price .a-offscreen")
        old_price = old_price_elem.text.strip() if old_price_elem else None

        found_brand = extract_brand_from_soup(soup, title)
        title_res = clean_arabic_title(title, found_brand)
        
        package_detail = ""
        size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|حبة|موس|\bL\b|\bml\b|\bkg\b))', title, re.IGNORECASE)
        if size_match:
            package_detail = size_match.group(1)

        coupon_details = extract_coupons_and_vouchers(soup)
        image_url = extract_best_image(soup, asin)

        return {
            "title_clean": title_res,
            "brand": found_brand,
            "package": package_detail,
            "price": price,
            "old_price_num": extract_number(old_price) if old_price else 0,
            "current_price_num": extract_number(price),
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

    dynamic_hook = generate_dynamic_hook(brand)
    lines = [f"{dynamic_hook}\n", f"{emoji} {product_item}\n"]

    has_discount = old_price_num > current_num and old_price_num > 0
    
    price_styles = ["old_and_new", "discount_percentage", "simple_price_with_words"]
    selected_style = random.choice(price_styles) if has_discount else "simple_price_with_words"

    if selected_style == "old_and_new":
        phrases = ["السعر السابق", "قبل الخصم", "كان بـ", "سعره الأول"]
        phrase = random.choice(phrases)
        lines.append(f"❌ {phrase}: <s>{int(old_price_num)} ريال</s> ← 🔥 الآن: <b>{clean_current}</b> بس 😱")
        
    elif selected_style == "discount_percentage":
        discount_percent = int(((old_price_num - current_num) / old_price_num) * 100)
        lines.append(f"🔥 السعر الآن: <b>{clean_current}</b> (خصم ممتاز بنسبة {discount_percent}%) 😱")
        
    else:
        word_decorations = ["السعر حالياً بـ", "نازل لـ", "مطلوب فيه الآن", "وصل لسعر"]
        decoration = random.choice(word_decorations)
        if clean_current:
            lines.append(f"🔥 {decoration}: <b>{clean_current}</b> 😱")

    if coupon_code:
        lines.append(generate_dynamic_coupon_call(coupon_code))
    elif voucher_text:
        lines.append(f"🎟️ <b>لا تنسوا تفعيل قسيمة الخصم ({html.escape(voucher_text)}) بنفس الصفحة!</b>")

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
    return 'Unsupported Media Type', 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

if __name__ == '__main__':
    start_webhook()
