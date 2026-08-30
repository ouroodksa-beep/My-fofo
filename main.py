import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import os

TOKEN = "7956075348:AAFetNzy6ECdP8iHgMWbwQIfjSInomOuhBU"
bot = telebot.TeleBot(TOKEN)

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني", "مكنسة"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "معطف", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل", "جل"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ارز", "حليب", "بسكويت", "منعم", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}

def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"

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
}

def translate_to_arabic(text):
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

def extract_smart_highlight(full_title):
    if not full_title:
        return "منتج مميز وعالي الطلب"
    
    # البحث عن تفاصيل جذابة داخل العنوان مثل (الحجم، العدد، المقاس، القوة) لاختيارها كمعلومة مفيدة
    extra_info = ""
    size_match = re.search(r'(\d+\s*(لتر|مل|قطعة|عبوة|كيلو|جرام|واط|ساعة|سم|إنش|مقاس|\bL\b|\bml\b|\bkg\b))', full_title, re.IGNORECASE)
    if size_match:
        extra_info = f" ({size_match.group(1)})"

    # تنظيف العنوان واستخراج الكốt الأساسي بذكاء بدون قطع الكلمات المفيدة
    clean_title = re.sub(r'\b(الأصلي|جديد|عرض خاص|فقط)\b', '', full_title)
    parts = re.split(r'[-–,|/]', clean_title)
    main_part = parts[0].strip()
    
    if len(main_part) < 12 and len(parts) > 1:
        main_part = f"{parts[0].strip()} {parts[1].strip()}"

    if re.search(r'[A-Za-z]', main_part):
        translated = translate_to_arabic(main_part)
        words = translated.split()
        title_res = " ".join(words[:8])
    else:
        words = main_part.split()
        title_res = " ".join(words[:8])

    return f"{title_res}{extra_info}"

def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "🧥", "beauty": "💄", "home": "🏡", "sports": "⚡"}
    return emojis.get(category, "🔥")

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl', 'link.amazon']):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            if 'link.amazon' in url.lower():
                soup = BeautifulSoup(r.text, "html.parser")
                asin = None
                canonical = soup.select_one('link[rel="canonical"]')
                if canonical:
                    href = canonical.get('href', '')
                    asin_match = re.search(r'/dp/([A-Z0-9]{9,10})', href)
                    if asin_match:
                        asin = asin_match.group(1)
                if asin:
                    return f"https://www.amazon.sa/dp/{asin}"
            return r.url
        return url
    except:
        return url

def is_saudi_amazon(url):
    if "link.amazon" in url.lower():
        return True
    return "amazon.sa" in url.lower()

def extract_asin(url):
    if 'link.amazon' in url.lower():
        match = re.search(r'link\.amazon/([A-Za-z0-9]{9,10})', url, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    patterns = [r'/dp/([A-Z0-9]{9,10})', r'/gp/product/([A-Z0-9]{9,10})', r'/product/([A-Z0-9]{9,10})', r'([A-Z0-9]{9,10})/?$']
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

def get_high_quality_image(soup):
    image = None
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
    if img_elem:
        image = img_elem.get("data-old-hires") or img_elem.get("src")
    if not image:
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img:
            image = og_img.get("content")
    if image:
        image = re.sub(r'_SX\d+_SY\d+_', '_', image).split('?')[0]
    return image

def extract_promos_and_discounts(soup):
    promos = []
    coupon_elems = soup.select(".promoPriceBlockMessage, #couponText, span.av-coupon-text, div[id*='coupon']")
    for elem in coupon_elems:
        text = elem.text.strip()
        if text and "تسجيل الدخول" not in text and "الشروط" not in text:
            if len(text) < 50 and text not in promos:
                promos.append(f"🎟️ **قسيمة خصم إضافية:** `{text}`")

    bank_codes = ["SAB20", "ANB", "ALJ", "STCPAY", "VISA", "MASTERCARD"]
    page_text = soup.get_text()
    
    for code in bank_codes:
        if code in page_text and f"كود `{code}`" not in promos:
            promos.append(f"💳 **كود خصم بنكي:** استخدم الرمز `{code}` عند الدفع")

    return promos[:1]

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    for ua in user_agents:
        try:
            headers = {
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "https://www.amazon.sa/",
                "DNT": "1"
            }
            r = requests.get(url, headers=headers, timeout=25)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            if "To discuss automated automated access to Amazon data" in r.text or soup.select_one("input#captchacharacters"):
                continue

            title_elem = soup.select_one("#productTitle")
            title = title_elem.text.strip() if title_elem else ""
            if not title:
                continue

            price = ""
            price_elem = soup.select_one(".a-price .a-offscreen")
            if price_elem:
                price = price_elem.text.strip()
            
            if not price or price == "0":
                price_alt = soup.select_one("#priceblock_ourprice") or soup.select_one("#priceblock_dealprice") or soup.select_one(".priceToPay")
                if price_alt:
                    price = price_alt.text.strip()

            old_price_elem = soup.select_one(".a-text-price .a-offscreen")
            old_price = old_price_elem.text.strip() if old_price_elem else None

            image = get_high_quality_image(soup)
            smart_name = extract_smart_highlight(title)
            category = detect_product_category(title)
            current_price_num = extract_number(price)
            promos = extract_promos_and_discounts(soup)

            return {
                "full_title": title,
                "name": smart_name,
                "price": price if price else "0",
                "old_price": old_price,
                "image": image,
                "category": category,
                "current_price_num": current_price_num,
                "promos": promos
            }
        except:
            continue
    return None

def generate_post(product_data, original_url):
    name = product_data["name"]
    price = product_data["price"]
    old_price = product_data["old_price"]
    category = product_data["category"]
    promos = product_data.get("promos", [])
    
    clean_current = clean_price(price) if price and price != "0" else None
    clean_old = clean_price(old_price) if old_price else ""
    emoji = get_category_emoji(category)

    old_num = extract_number(old_price) if old_price else 0
    current_num = product_data["current_price_num"]
    
    discount_pct = 0
    if old_num > current_num and old_num > 0 and current_num > 0:
        calc_pct = int(((old_num - current_num) / old_num) * 100)
        if calc_pct < 100:
            discount_pct = calc_pct

    # تشكيلة واسعة وعشوائية تماماً لجعل أسلوب كل بوست مختلف عن الآخر
    hooks = [
        f"🔥 **صفقة مميزة ولا تفوتك!**\n{emoji} **{name}**",
        f"🚨 **تخفيض قوي وعليها إقبال عالي:**\n{emoji} **{name}**",
        f"⚡ **لقطة اليوم السريعة.. استغل الفرصة:**\n{emoji} **{name}**",
        f"🎯 **منتج يستهل الطلب بسعر مميز:**\n{emoji} **{name}**",
        f"💥 **خصم طازج وفرصة ذهبية للتوفير:**\n{emoji} **{name}**",
        f"✨ **طلب مسبق وعليها خصم واو:**\n{emoji} **{name}**"
    ]
    selected_hook = random.choice(hooks)
    
    if clean_current:
        if clean_old and discount_pct > 0:
            price_phrases = [
                f"💰 السعر الآن: **{clean_current}** (بدلاً من ~~{clean_old}~~) 🔥 وفر **{discount_pct}%**",
                f"🏷️ خذها بـ **{clean_current}** فقط! (كانت ~~{clean_old}~~ بخصم **{discount_pct}%**)",
                f"✨ السعر الحالي: **{clean_current}** | السعر السابق ~~{clean_old}~~ 📉 بنسبة خصم **{discount_pct}%**"
            ]
            price_section = random.choice(price_phrases)
        else:
            price_section = f"💰 السعر الحالي المميز: **{clean_current}**"
    else:
        price_section = f"💰 **شاهد السعر الحالي والخصم المباشر هنا 👇**"

    post_lines = [
        selected_hook,
        "",
        price_section,
    ]

    if promos:
        post_lines.append(promos[0])

    cta_phrases = [
        f"🛒 **اطلبها الآن قبل نفاد الكمية:**\n{original_url}",
        f"🏃‍♂️ **رابط الشراء السريع:**\n{original_url}",
        f"🔗 **لطلب المنتج مباشرة:**\n{original_url}",
        f"👇 **الحق العرض من هنا:**\n{original_url}"
    ]
    
    post_lines.extend([
        "",
        random.choice(cta_phrases)
    ])

    return "\n".join([line for line in post_lines if line is not None])

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أهلاً بك! يرجى إرسال روابط أمازون السعودية لتحويلها فوراً إلى صيدات احترافية ✨")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ عذراً، الرابط مخصص لأمازون السعودية (amazon.sa) فقط.")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج من الرابط.")
            continue

        wait = bot.reply_to(msg, "⏳ جاري استخلاص أهم تفاصيل المنتج وصياغة بوست حصري...")

        product = get_product(asin)
        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، تأكد من صحة الرابط أو جرب رابطاً آخر.", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ حدث خطأ أثناء إرسال المنشور.", msg.chat.id, wait.message_id)

# ============ WEBHOOK SERVER ============
from flask import Flask, request

app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route('/')
def index():
    return "🤖 بوت الصيدات والخصومات يعمل بأعلى كفاءة 🔥"

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
        print(f"✅ Webhook set to: {WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}")
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

if __name__ == '__main__':
    start_webhook()
