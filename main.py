import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json
from urllib.parse import parse_qs, urlparse

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🇸🇦 افتتاحيات سعودية (كثيرة ومتغيرة)
# ===================================

SAUDI_HOOKS_1 = [
    "🔥 عرض نار على", "💥 لقطة اليوم على", "✨ جاكم عرض على",
    "🚨 انتبهوا على", "🔥 لا يفوتكم", "💣 كسر السعر على",
    "⚡ عرض قوي على", "🔥 الحق العرض على", "💯 من أقوى العروض على",
    "👀 شوفوا هذا العرض على", "🔥 سعر خرافي على", "💥 عرض مجنون على",
    "📢 إعلان مهم على", "🔥 فرصة ذهبية على", "💸 سعر ما يتعوض على",
]

SAUDI_HOOKS_2 = [
    "سعر ما يتكرر 🔥", "فرصة لا تفوت 👌", "اللي يعرف يعرف 😏",
    "سعر كسر السوق 💥", "محد بيقول لا 🔥", "يستاهل وبقوة 💯",
    "خذها قبل تخلص 🚨", "العرض عليه كلام 🔥", "صفقة رابحة 👌",
    "لا تفكر كثير وخذها 🔥", "بتندم لو فاتك 😅",
    "سعر بلاش حرفياً 💸", "شيء فخم الصراحة ✨",
    "مطلوب وبقوة 🔥", "الناس طايحين عليه 👀",
]

SMART_ENDINGS = [
    "👌 خيار ممتاز",
    "🔥 يستاهل التجربة",
    "💯 من الآخر",
    "✨ جودة توب",
    "😎 اختيار ذكي",
    "📦 عملي ومفيد",
]

# ===================================
# 🔤 ترجمة بدون تقطيع
# ===================================

TRANSLATION_DICT = {
    "pillow": "مخدة",
    "memory": "ميموري",
    "foam": "فوم",
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "black": "أسود",
    "white": "أبيض",
    "blue": "أزرق",
    "red": "أحمر",
    "green": "أخضر",
}

def translate_to_arabic(text):
    if not text:
        return text

    for eng, ar in TRANSLATION_DICT.items():
        text = re.sub(r'\b' + re.escape(eng) + r'\b', ar, text, flags=re.IGNORECASE)

    return text

# ===================================
# 🔧 أدوات مساعدة
# ===================================

def extract_asin(url):
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    return m.group(1) if m else None

def clean_price(price_text):
    nums = re.findall(r'[\d,.]+', price_text)
    if nums:
        return f"{int(float(nums[0].replace(',', '')))} ريال"
    return price_text

def extract_size_color(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    size = params.get("size", [None])[0]
    color = params.get("color", [None])[0]

    return size, color

# ===================================
# 📦 جلب المنتج
# ===================================

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ar-SA,ar;q=0.9"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("#productTitle")
    price = soup.select_one(".a-price .a-offscreen")

    old_price = soup.select_one(".a-text-price .a-offscreen")

    image = soup.select_one("#landingImage")

    if not title or not price:
        return None

    return (
        title.text.strip(),
        price.text.strip(),
        old_price.text.strip() if old_price else None,
        image.get("src") if image else None
    )

# ===================================
# 🧠 توليد البوست (ستايل X)
# ===================================

def generate_post(title, price, old_price, size, color, url):
    product_name = translate_to_arabic(title[:60])

    hook1 = random.choice(SAUDI_HOOKS_1)
    hook2 = random.choice(SAUDI_HOOKS_2)

    lines = []

    lines.append(f"{hook1} {product_name}")
    lines.append(hook2)
    lines.append("")

    lines.append(product_name)

    extras = []
    if size:
        extras.append(f"📏 {size}")
    if color:
        extras.append(f"🎨 {color}")

    if extras:
        lines.append(" | ".join(extras))

    current = clean_price(price)
    old = clean_price(old_price) if old_price else None

    if old:
        lines.append(f"❌ {old}")
        lines.append(f"✅ {current} 🔥")
    else:
        lines.append(f"💰 {current}")

    lines.append(random.choice(SMART_ENDINGS))
    lines.append(f"🔗 {url}")

    return "\n".join(lines)

# ===================================
# 🤖 البوت
# ===================================

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط امازون")
        return

    for url in urls:
        asin = extract_asin(url)

        if not asin:
            bot.reply_to(msg, "❌ رابط غير صحيح")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ فشل استخراج المنتج", msg.chat.id, wait.message_id)
            continue

        title, price, old_price, image = product
        size, color = extract_size_color(url)

        post = generate_post(title, price, old_price, size, color, url)

        if image:
            bot.send_photo(msg.chat.id, image, caption=post)
        else:
            bot.send_message(msg.chat.id, post)

        bot.delete_message(msg.chat.id, wait.message_id)

print("🤖 شغال بأسلوب سعودي احترافي")
bot.infinity_polling()# وصف سريع
QUICK_DESC = [
    "جودة عالية 👌",
    "يستاهل التجربة 🔥",
    "منتج ممتاز 👍",
    "خيار ذكي 💡",
    "جودة مضمونة ✅",
]

# ===================================
# 🔧 استخراج المقاس واللون من الرابط
# ===================================

def extract_selected_size_color(url):
    """
    استخراج المقاس واللون المختارين من رابط أمازون
    """
    selected_size = None
    selected_color = None
    
    try:
        # تحليل الرابط
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # البحث عن المقاس في المعاملات المختلفة
        size_params = ['size', 'th', 'psc']
        for param in size_params:
            if param in params:
                value = params[param][0]
                selected_size = value.replace('_', ' ').replace('-', ' ')
                # لو الرقم 1 أو 2 إلخ، ممكن يكون index فنتركه
                if value.isdigit() and int(value) < 10:
                    selected_size = None
                break
        
        # البحث عن اللون
        color_params = ['color', 'colour', 'col']
        for param in color_params:
            if param in params:
                value = params[param][0]
                selected_color = value.replace('_', ' ').replace('-', ' ')
                break
        
        # البحث في المسار (path) عن مقاسات مثل 40x60
        path = parsed.path + '?' + parsed.query
        
        # استخراج المقاسات بالصيغة الرقمية (40x60, 50x70, إلخ)
        size_match = re.search(r'(\d+)\s*[xX]\s*(\d+)', path)
        if size_match and not selected_size:
            selected_size = f"{size_match.group(1)}x{size_match.group(2)}"
        
        # استخراج أسماء المقاسات الشائعة
        size_names = re.search(r'(small|medium|large|xl|xxl|xxxl|king|queen|single|twin|full|double)', path, re.IGNORECASE)
        if size_names and not selected_size:
            selected_size = size_names.group(1).upper()
        
        # استخراج الألوان الشائعة
        color_names = re.search(r'(black|white|red|blue|green|yellow|gray|grey|brown|pink|purple|orange|beige|navy|gold|silver)', path, re.IGNORECASE)
        if color_names and not selected_color:
            selected_color = color_names.group(1).capitalize()
            
    except Exception as e:
        print(f"Error extracting size/color: {e}")
    
    return selected_size, selected_color

# ===================================
# 🔧 دوال استخراج المعلومات
# ===================================

def extract_brand_and_product(title):
    known_brands = [
        "Apple", "Samsung", "Xiaomi", "Huawei", "Sony", "LG", "Nike", "Adidas",
        "Puma", "Gucci", "Chanel", "Dior", "HP", "Dell", "Lenovo", "Asus",
        "Microsoft", "Canon", "Nikon", "Bose", "JBL", "Anker", "Philips",
        "Panasonic", "Toshiba", "Hisense", "TCL", "Dyson", "Nespresso",
        "Ray-Ban", "Oakley", "Zara", "H&M", "Uniqlo", "Levi's", "Calvin Klein",
        "Lacoste", "Tommy Hilfiger", "Ralph Lauren", "Under Armour", "Reebok",
        "New Balance", "Asics", "Converse", "Vans", "The North Face", "Columbia",
        "Patagonia", "IKEA", "Home Center", "Extra", "Jarir", "Amazon Basics",
        "Sandisk", "Seagate", "Western Digital", "Logitech", "Razer", "Corsair",
        "HyperX", "SteelSeries", "BenQ", "AOC", "MSI", "Gigabyte", "AMD", "Intel",
        "NVIDIA", "PlayStation", "Xbox", "Nintendo", "GoPro", "DJI", "Fitbit",
        "Garmin", "Apple Watch", "iPhone", "iPad", "MacBook", "AirPods", "Galaxy",
        "Sleep", "Factory", "Luna", "Maybelline", "Loreal", "LC Waikiki"
    ]
    
    title_clean = title.strip()
    brand = None
    product_name = title_clean
    
    for known_brand in known_brands:
        if known_brand.lower() in title_clean.lower():
            brand = known_brand
            product_name = re.sub(r'\b' + re.escape(known_brand) + r'\b', '', title_clean, flags=re.IGNORECASE).strip()
            product_name = re.sub(r'^(Original|New|Official|Authentic|Genuine)\s+', '', product_name, flags=re.IGNORECASE)
            break
    
    if not brand:
        words = title_clean.split()
        if len(words) > 0:
            potential_brand = words[0]
            if len(potential_brand) > 2 and potential_brand.lower() not in ['the', 'new', 'original', 'for', 'with']:
                brand = potential_brand
                product_name = ' '.join(words[1:])
    
    product_name = re.sub(r'\s+', ' ', product_name).strip()
    if len(product_name) > 60:
        product_name = product_name[:60].rsplit(' ', 1)[0] + "..."
    
    return brand or "ماركة معروفة", product_name or title_clean[:50]

# ===================================
# 🔄 قاموس الترجمة
# ===================================

TRANSLATION_DICT = {
    "iphone": "آيفون",
    "samsung": "سامسونج",
    "galaxy": "جالاكسي",
    "xiaomi": "شاومي",
    "huawei": "هواوي",
    "apple": "آبل",
    "sony": "سوني",
    "lg": "إل جي",
    "nike": "نايك",
    "adidas": "أديداس",
    "puma": "بوما",
    "gucci": "غوتشي",
    "chanel": "شانيل",
    "dior": "ديور",
    "hp": "إتش بي",
    "dell": "ديل",
    "lenovo": "لينوفو",
    "asus": "أسوس",
    "microsoft": "مايكروسوفت",
    "canon": "كانون",
    "nikon": "نيكون",
    "bose": "بوز",
    "jbl": "جي بي إل",
    "anker": "أنكر",
    "philips": "فيليبس",
    "panasonic": "باناسونيك",
    "toshiba": "توشيبا",
    "hisense": "هايسنس",
    "tcl": "تي سي إل",
    "dyson": "دايسون",
    "nespresso": "نسبريسو",
    "ray-ban": "راي بان",
    "oakley": "أوكلي",
    "zara": "زارا",
    "h&m": "إتش آند إم",
    "uniqlo": "يونيكلو",
    "levi's": "ليفايز",
    "calvin klein": "كالفن كلاين",
    "lacoste": "لاكوست",
    "tommy hilfiger": "تومي هيلفيغر",
    "ralph lauren": "رالف لورين",
    "under armour": "أندر أرمور",
    "reebok": "ريبوك",
    "new balance": "نيو بالانس",
    "asics": "أسيكس",
    "converse": "كونفرس",
    "vans": "فانس",
    "the north face": "ذا نورث فيس",
    "columbia": "كولومبيا",
    "patagonia": "باتاغونيا",
    "ikea": "إيكيا",
    "sandisk": "سانديسك",
    "seagate": "سيغيت",
    "western digital": "ويسترن ديجيتال",
    "logitech": "لوجيتك",
    "razer": "ريزر",
    "corsair": "كورسير",
    "hyperx": "هايبر إكس",
    "steelseries": "ستيل سيريز",
    "benq": "بينكيو",
    "aoc": "إي أو سي",
    "msi": "إم إس آي",
    "gigabyte": "جيجابايت",
    "amd": "إيه إم دي",
    "intel": "إنتل",
    "nvidia": "إنفيديا",
    "playstation": "بلاي ستيشن",
    "xbox": "إكس بوكس",
    "nintendo": "نينتندو",
    "gopro": "غو برو",
    "dji": "دي جي آي",
    "fitbit": "فيتبيت",
    "garmin": "جارمين",
    "airpods": "سماعات آيربودز",
    "macbook": "ماك بوك",
    "ipad": "آيباد",
    "apple watch": "ساعة آبل",
    "airpods pro": "آيربودز برو",
    "airpods max": "آيربودز ماكس",
    "sleep": "سليب",
    "factory": "فاكتوري",
    "luna": "لونا",
    "maybelline": "ميبيلين",
    "loreal": "لوريال",
    "lc waikiki": "ال سي وايكيكي",
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "pro": "برو",
    "max": "ماكس",
    "plus": "بلس",
    "ultra": "ألترا",
    "original": "أصلي",
    "new": "جديد",
    "pillow": "مخدة",
    "milk powder": "حليب مجفف",
    "black": "أسود",
    "white": "أبيض",
    "red": "أحمر",
    "blue": "أزرق",
    "green": "أخضر",
    "yellow": "أصفر",
    "gray": "رمادي",
    "grey": "رمادي",
    "brown": "بني",
    "pink": "وردي",
    "purple": "بنفسجي",
    "orange": "برتقالي",
    "beige": "بيج",
    "navy": "كحلي",
    "gold": "ذهبي",
    "silver": "فضي",
    "small": "صغير",
    "medium": "وسط",
    "large": "كبير",
    "xl": "XL",
    "xxl": "XXL",
    "xxxl": "XXXL",
    "king": "كينج",
    "queen": "كوين",
    "single": "فردي",
    "twin": "توين",
    "full": "فول",
    "double": "مزدوج",
}

def translate_to_arabic(text):
    if not text:
        return text
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

# ===================================
# 🔧 دوال المساعدة
# ===================================

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co']):
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
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'([A-Z0-9]{10})/?$',
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
        r'_SX\d+_SY\d+_',
        r'_SX\d+_',
        r'_SY\d+_',
        r'_CR\d+,\d+,\d+,\d+_',
        r'_AC_SL\d+_',
        r'_SCLZZZZZZZ_',
        r'_FMwebp_',
        r'_QL\d+_',
    ]
  
    cleaned = url
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '_', cleaned)

    if '_SL' not in cleaned and 'amazon' in cleaned:
        cleaned = re.sub(r'(\.[a-zA-Z]+)(\?.*)?$', r'_SL1500\1', cleaned)

    cleaned = cleaned.split('?')[0]

    return cleaned

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

            discount_percent = None
            try:
                if old_price and price:
                    old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
                    new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
                    if old_num > new_num:
                        discount_percent = int(((old_num - new_num) / old_num) * 100)
            except:
                pass

            if price:
                return full_title, price, old_price, image, discount_percent
                  
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
  
    return None

# ===================================
# ✨ توليد منشور اكس زون
# ===================================

def generate_xzone_post(full_title, price, old_price, discount_percent, selected_size, selected_color, original_url):
    brand, product_name = extract_brand_and_product(full_title)
    brand_ar = translate_to_arabic(brand)
    product_name_ar = translate_to_arabic(product_name)
    
    # افتتاحية قوية
    opening = random.choice(OPENING_HOOKS)
    
    # اسم المنتج
    pattern = random.choice(PRODUCT_PATTERNS)
    product_line = pattern.format(product=product_name_ar, brand=brand_ar)
    
    # بناء المنشور
    lines = [f"{opening} {product_line}"]
    lines.append("")  # سطر فارغ
    
    # إضافة المقاس المختار فقط
    if selected_size:
        size_ar = translate_to_arabic(selected_size)
        lines.append(f"المقاس: {size_ar} 📏")
        lines.append("")
    
    # إضافة اللون المختار فقط
    if selected_color:
        color_ar = translate_to_arabic(selected_color)
        lines.append(f"اللون: {color_ar} 🎨")
        lines.append("")
    
    # السعر بشكل مباشر
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ في السوق: {clean_old}")
        lines.append(f"✅ الآن: {clean_current} (وفر {discount_percent}%) 💥")
    else:
        lines.append(f"💰 السعر: {clean_current}")
    
    lines.append("")
    
    # وصف سريع
    desc = random.choice(QUICK_DESC)
    lines.append(desc)
    
    lines.append("")
    lines.append(f"🔗 الرابط: {original_url}")
    
    return "\n".join(lines)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط المنتج من أمازون السعودية")
        return

    for original_url in urls:
        # استخراج المقاس واللون المختارين من الرابط الأصلي
        selected_size, selected_color = extract_selected_size_color(original_url)
        
        expanded = expand_url(original_url)

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط يجب يكون من amazon.sa")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج رقم المنتج")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        full_title, price, old_price, image, discount_percent = product
        
        try:
            post = generate_xzone_post(full_title, price, old_price, discount_percent, selected_size, selected_color, original_url)
            
            # إرسال الصورة مع المنشور
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
            
        except Exception as e:
            print(f"Error: {e}")
            bot.edit_message_text("❌ صار خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت شغال بأسلوب اكس زون...")
bot.infinity_polling()
