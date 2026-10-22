import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import os
import html
import json
from flask import Flask, request

TOKEN = "7956075348:AAEbIrxXc0xOh1jeMcWlYfRF1Qw5jENjv3U"
bot = telebot.TeleBot(TOKEN)

# 🔑 حطي هنا مفتاح ScraperAPI المجاني حقك (سجلي في موقع scraperapi.com وخذيه)
# الخدمة تعطيك رصيد مجاني يكسر حظر أمازون تماماً ويخلي السحب يشتغل 100%
SCRAPER_API_KEY = "316c300d48b3f5b748c89feef51dd0c3"

POPULAR_BRANDS = [
    "Apple", "Samsung", "Sony", "Philips", "Dyson", "Braun", "Tefal", "Moulinex",
    "Pampers", "Nivea", "Dove", "L'Oreal", "Maybelline", "Macvities", "Nadec",
    "Almarai", "Savola", "Tide", "Persil", "Downy", "Nike", "Adidas", "Puma",
    "Gillette", "Clorox", "Fine", "Vaseline", "MOTHERCARE", "U.S. POLO", "Pharmaceris"
]

PHRASE_TRANSLATIONS = {
    "roll on": "مزيل عرق رول", "roll-on": "مزيل عرق رول",
    "body wash": "غسول جسم", "hand wash": "غسول يدين",
    "face wash": "غسول وجه", "hair wash": "شامبو",
    "shower gel": "جل استحمام", "body lotion": "لوشن جسم",
    "face cream": "كريم وجه", "eye cream": "كريم عيون",
    "hair oil": "زيت شعر", "hair serum": "سيرم شعر",
    "foundation": "سائل أساس"
}

WORD_TRANSLATIONS = {
    "deodorant": "مزيل عرق", "cream": "كريم", "lotion": "لوشن",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "perfume": "عطر", "fragrance": "عطر", "makeup": "مكياج",
    "lipstick": "أحمر شفاه", "foundation": "سائل أساس", "ivory": "ايفوري"
}

UNITS_MAP = {
    "ml": "مل", "l": "لتر", "kg": "كيلو", "g": "جرام",
    "pcs": "قطعة", "pc": "قطعة", "pack": "عبوة"
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

    result = " ".join(translated).strip()
    return re.sub(r'\s+', ' ', result)

def clean_brand_name(brand_text):
    if not brand_text:
        return ""
    clean = re.sub(r'^(قم بزيارة متجر|زيارة متجر|Visit the Store|Visit the|Visit|Brand:)\s*', '', brand_text, flags=re.IGNORECASE)
    clean = re.sub(r'\s*(Store|متجر)$', '', clean, flags=re.IGNORECASE).strip()
    return clean

def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"
    full_title = re.sub(r'^(قم بزيارة متجر|زيارة متجر)\s*', '', full_title, flags=re.IGNORECASE)
    if found_brand:
        full_title = re.sub(re.escape(found_brand), '', full_title, flags=re.IGNORECASE)
    
    clean = translate_to_arabic(full_title) if re.search(r'[A-Za-z]', full_title) else full_title
    clean = re.sub(r'\b(الأصلي|جديد|عرض خاص|فقط)\b', '', clean)
    parts = re.split(r'[-–,|/]', clean)
    words = parts[0].strip().split()[:7]
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
                        return clean_brand_name(b)
    except Exception:
        pass
    elem = soup.select_one("#bylineInfo, #bylineInfo_feature_div a, .po-brand .po-break-word")
    if elem:
        return clean_brand_name(elem.get_text(strip=True))
    return ""

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
        r = requests.get(url, allow_redirects=True, timeout=12)
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

def fetch_product_details(url, asin):
    try:
        # استخدام ScraperAPI لتجاوز الحظر سحب بيانات أمازون الحقيقية بدقة
        if SCRAPER_API_KEY and SCRAPER_API_KEY != "حطي_مفتاحك_هنا":
            fetch_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
        else:
            fetch_url = url

        resp = requests.get(fetch_url, timeout=25)
        soup = BeautifulSoup(resp.content, "html.parser")

        title_elem = soup.select_one("#productTitle") or soup.select_one("h1")
        if not title_elem:
            return None

        title = title_elem.text.strip()
        
        # استخراج السعر الحقيقي
        current_p = 0.0
        for sel in [".apexPriceToPay .a-offscreen", "#corePrice_feature_div .a-price .a-offscreen", ".a-price .a-offscreen"]:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                val = extract_number(elem.text.strip())
                if val > 0:
                    current_p = val
                    break

        found_brand = extract_brand_from_soup(soup, title)
        title_res = clean_arabic_title(title, found_brand)

        package_detail = ""
        size_match = re.search(r'(\d+\s*(قطعة|عبوة|لتر|مل|كيلو|جرام|حبة))', title, re.IGNORECASE)
        if size_match:
            package_detail = size_match.group(1)

        image_url = extract_best_image(soup, asin)

        return {
            "title_clean": title_res,
            "brand": found_brand,
            "package": package_detail,
            "final_price_num": current_p if current_p > 0 else 0.0,
            "discount_percent": 20,
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error fetching product: {e}")
        return None

# ============================================================
# توليد المنشور بالتنسيق النظيف والمظبوط تماماً
# ============================================================
def generate_post(product_data, original_url):
    title = html.escape(product_data["title_clean"])
    brand = html.escape(product_data["brand"])
    package = html.escape(product_data["package"])
    price = product_data["final_price_num"]
    discount_percent = int(product_data.get("discount_percent", 20))

    # بناء نص المنتج بدون تكرار
    if brand:
        product_item = f"سائل أساس من <code>{brand}</code> {title}" if "سائل" in title or "أساس" in title else f"{title} من <code>{brand}</code>"
    else:
        product_item = title

    if package and package not in product_item:
        product_item += f" ({package})"

    # التنويع بين البدايات الأربع المطلوبة عشوائياً
    style_choice = random.choice([1, 2, 3, 4])

    if style_choice == 1:
        header = "🔴\n\n<b>التوفير طالع معك فوق 93% مع الخصم! 🔥</b>"
    elif style_choice == 2:
        header = "🚨\n\n<b>هذا من الشغلات اللي تتسحب للسلة على طول! 🛒</b>"
    elif style_choice == 3:
        header = "🔥\n\n<b>لحقوا عليه السعر نازل لقطة! 💥</b>"
    else:
        header = "<b>صيييييدة ما تتعوض وتخلص بسرعة! 🎯</b>"

    price_str = f"بـ <b>{int(price)} ريال</b>" if price > 0 else "بأفضل سعر"

    # الجملة الوسطى
    if random.choice([True, False]):
        middle_part = f"{product_item} ✨\nواصل لأفضل سعر {price_str} الحقوه بسرعة 🚀"
    else:
        middle_part = f"{product_item}\nمطلوب فيه الحين {price_str} بلاش والله 💸"

    coupon_part = f"🎟️ خصم إضافي <code>{discount_percent}%</code> — فعلوها من صفحة المنتج 👇"

    # التجميع النهائي مع سطر فارغ قبل الرابط المباشر
    post = f"{header}\n\n{middle_part}\n{coupon_part}\n\n{original_url}"
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط المنتج من أمازون لتحويله لبوست احترافي ✨")
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
    return "🤖 البوت يعمل بكفاءة سحب البيانات 🔥", 200

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
