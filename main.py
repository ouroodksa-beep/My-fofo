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
        "Referer": "https://www.google.com/"
    }

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

def generate_dynamic_coupon_call(code):
    icons = ["🎟️", "🏷️", "🔑", "💥", "🎁", "✨", "📌", "💳"]
    verbs = ["استخدموا", "لا تنسوا استخدام", "تأكدوا من تطبيق", "ادخلوا", "انسخوا", "ضعوا", "فعّلوا"]
    nouns = ["كود الخصم", "رمز الخصم", "الكود الإضافي", "كود التوفير", "الكود المباشر", "الرمز الترويجي"]
    adjectives = ["الفعّال", "المتاح", "الحالي", "المميز", "الخاص بالموقع"]
    
    icon = random.choice(icons)
    verb = random.choice(verbs)
    noun = random.choice(nouns)
    adj = random.choice(adjectives)
    
    return f"{icon} <b>{verb} {noun} {adj}:</b> <code>{html.escape(code)}</code>"

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
    words = parts[0].strip().split()[:6]
    
    bad_endings = ['من', 'عن', 'في', 'على', 'إلى', 'مع', 'أو', 'و', 'الخالي', 'ذو', 'ذات', 'يغذي']
    while words and words[-1] in bad_endings:
        words.pop()
        
    res = " ".join(words).strip()
    return res if res else "منتج مميز"

def extract_brand_from_soup(soup, full_title):
    for brand in POPULAR_BRANDS:
        if brand.lower() in full_title.lower():
            return brand

    brand_elem = soup.select_one("#bylineInfo, .po-brand .a-span9, #bylineInfo_feature_div")
    if brand_elem:
        text = re.sub(r'^(Brand:|الماركة:|زيارة متجر|Visit the|Store|\s+)+', '', brand_elem.text.strip(), flags=re.IGNORECASE)
        if text and not re.search(r'[\u0600-\u06FF]', text):
            return text
    return ""

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
    # محاولة تجريف البيانات بشكل ناعم
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")

        title_elem = soup.select_one("#productTitle") or soup.select_one("h1")
        
        # إذا تم كشف البوت من قبل أمازون، سنستخدم طريقة مجانية وسريعة للتخفي عبر ScraperAPI
        if not title_elem or "captcha" in resp.text.lower():
            proxy_url = f"https://api.scraperapi.com?api_key=free&url={url}" # يتم استبدال الكلمة بـ Scraping proxy عند الحاجة
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
        size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|حبة))', title, re.IGNORECASE)
        if size_match:
            package_detail = size_match.group(1)

        # رابط جودة عالية رئيسي بدقة فائقة عبر ASIN
        image_url = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_.jpg" if asin else None

        return {
            "title_clean": title_res,
            "brand": found_brand,
            "package": package_detail,
            "price": price,
            "old_price_num": extract_number(old_price) if old_price else 0,
            "current_price_num": extract_number(price),
            "category": detect_product_category(title),
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
    
    clean_current = clean_price(price) if price and price != "0" else None
    emoji = get_category_emoji(category)

    brand_str = f"<b>{brand}</b> " if brand else ""
    package_str = f" <b>({package})</b>" if package else ""
    product_item = f"{brand_str}<b>{title}</b>{package_str}"

    dynamic_hook = generate_dynamic_hook(brand)
    lines = [f"{dynamic_hook}\n", f"{emoji} {product_item}\n"]

    if old_price_num > current_num and old_price_num > 0 and clean_current:
        lines.append(f"❌ قبل: <s>{int(old_price_num)} ريال</s> ← 🔥 الآن: <b>{clean_current}</b> بس 😱")
    elif clean_current:
        lines.append(f"🔥 السعر الحالي: <b>{clean_current}</b> 😱")

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
        wait = bot.reply_to(msg, "⏳ جاري قراءة بيانات المنتج واستخراج الصورة بأعلى جودة...")

        product = fetch_product_details(target_url, asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج بسبب حظر أمازون الحالي، حاول مجدداً بعد قليل.", msg.chat.id, wait.message_id)
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
