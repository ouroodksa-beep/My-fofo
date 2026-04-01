import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🧠 قاعدة بيانات الجمل السعودية الأصيلة
# ===================================

# أنماط الجمل السعودية الخالصة
SENTENCE_PATTERNS = [
    # نمط الاستعجال والندرة
    "شف هالعرض، ما يتفوت 👀",
    "يا هلا بالسعر الزين 💰",
    "من الآخر، {product} يستاهل التجربة 👌",
    "بلا كلام فاضي، هالسعر مناسب 🔥",
    "باختصار، {product} من {brand} يستحق الشراء 💯",
    "ما راح تلقى مثل هالسعر 👍",
    "فرصة تجي مرة، لا تطوفها ⏰",
    "هالعرض يبي له سرعة 🏃‍♂️",
    "اللي يدور {benefit}، هنا موجود 👌",
    "ما في زيه بهالسعر 🔥",
    
    # نمط الثقة والجودة
    "{product} من {brand}، شغل نظيف 👌",
    "جودة {brand} معروفة، و{product} يثبتها 💯",
    "منتج {brand} على الطبيعة زي ما تشوف 👍",
    "{product} فخم ويستاهل كل ريال 💎",
    "اختار {product} من {brand} وارتاح بال 👌",
    "هالمنتج رايق ويخدمك زين 🎯",
    "{product} من {brand}، موضوع ثابت ومضمون ✅",
    "اللي يبغى الاحترافية، {product} حلالها 🏆",
    
    # نمط التوصية الشخصية
    "أقول لك شي؟ {product} من {brand} يستاهل 👍",
    "جربته وعجبني، ودك تجربه؟ {product} من {brand} 👌",
    "من وجهة نظري، {product} خيار طيب 💡",
    "أنصح فيه بقوة: {product} من {brand} 💪",
    "لو تسألني، أقول لك {product} من {brand} 🔥",
    "من تجربة، {product} يستاهل كل ريال 💰",
    
    # نمط الشرهة (الحاجة الملحة)
    "{product} شرهة ما تتأخر عليها 🚨",
    "هالسعر ما يتكرر، خذه ولا تفكر كثير 💸",
    "{product} من {brand}، خذه وارتاح 🎯",
    "ما يحتاج تفكير، {product} من {brand} واضح 👌",
    "القرار سهل: {product} بسعر مناسب ✅",
    
    # نمط المقارنة والقيمة
    "سعره طيب مقابل اللي يعطيك إياه 💰",
    "قيمة {product} فوق السعر 👆",
    "ما راح تندم على هالشراء 👍",
    "استثمارك في {product} مضمون 📈",
    "{product} من {brand}، سعره مناسب وجودته زينة 👌",
]

# افتتاحيات سعودية
OPENING_HOOKS = [
    "صدقني،",
    "والله،",
    "من الآخر،",
    "باختصار،",
    "بلا كلام كثير،",
    "أقول لك شي؟",
    "شف،",
    "يا هلا،",
    "طال عمرك،",
    "بكل بساطة،",
    "ما في أحسن من",
    "لو تدور",
]

# مفردات سعودية حسب الفئة
PRODUCT_BENEFITS = {
    "phone": ["الأداء", "التصوير", "السرعة", "الجودة", "الموثوقية"],
    "laptop": ["الشغل", "الدراسة", "الإنتاج", "الأداء", "الكفاءة"],
    "audio": ["الصوت النقي", "الوضوح", "العزل", "الجودة", "التجربة"],
    "home": ["البيت", "الراحة", "النظافة", "الطهي", "الاسترخاء"],
    "fashion": ["الأناقة", "الطلة", "المناسبات", "الجودة", "الراحة"],
    "beauty": ["العناية", "النضارة", "الثقة", "الجودة", "التميز"],
    "default": ["الجودة", "الأداء", "الراحة", "القيمة", "التميز"]
}

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
        "Garmin", "Apple Watch", "iPhone", "iPad", "MacBook", "AirPods", "Galaxy"
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

def detect_product_category(title):
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['phone', 'iphone', 'samsung', 'xiaomi', 'mobile', 'هاتف', 'جوال']):
        return "phone"
    elif any(word in title_lower for word in ['laptop', 'macbook', 'notebook', 'computer', 'لابتوب', 'كمبيوتر']):
        return "laptop"
    elif any(word in title_lower for word in ['headphone', 'earbuds', 'airpods', 'speaker', 'سماعة', 'مكبر']):
        return "audio"
    elif any(word in title_lower for word in ['shoes', 'shirt', 'dress', 'bag', 'watch', 'حذاء', 'قميص', 'فستان', 'شنطة', 'ساعة']):
        return "fashion"
    elif any(word in title_lower for word in ['cream', 'perfume', 'lotion', 'shampoo', 'عطر', 'كريم', 'شامبو']):
        return "beauty"
    elif any(word in title_lower for word in ['fridge', 'washer', 'oven', 'vacuum', 'tv', 'ثلاجة', 'غسالة', 'فرن', 'تلفزيون']):
        return "home"
    else:
        return "default"

def generate_smart_sentence(product_name, brand, category):
    pattern = random.choice(SENTENCE_PATTERNS)
    benefits = PRODUCT_BENEFITS.get(category, PRODUCT_BENEFITS["default"])
    benefit = random.choice(benefits)
    
    opening = ""
    if random.random() < 0.4:  # 40% احتمالية إضافة افتتاحية
        opening = random.choice(OPENING_HOOKS) + " "
    
    try:
        sentence = pattern.format(
            product=product_name,
            brand=brand,
            benefit=benefit
        )
    except:
        # لو النمط ما يحتوي على متغيرات
        sentence = pattern
    
    return opening + sentence

# ===================================
# 🔄 قاموس الترجمة السعودي
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
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "pro": "برو",
    "max": "ماكس",
    "plus": "بلس",
    "ultra": "ألترا",
    "original": "أصلي",
    "new": "جديد",
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
# ✨ التوليد النهائي السعودي
# ===================================

def generate_post(full_title, price, old_price, discount_percent, original_url):
    brand, product_name = extract_brand_and_product(full_title)
    brand_ar = translate_to_arabic(brand)
    product_name_ar = translate_to_arabic(product_name)
    category = detect_product_category(full_title)
    
    smart_sentence = generate_smart_sentence(product_name_ar, brand_ar, category)
    
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    
    lines = [smart_sentence]
    lines.append("")
    
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"قبل: {clean_old} ❌")
        lines.append(f"الآن: {clean_current} (وفر {discount_percent}%) 🔥")
    else:
        lines.append(f"السعر: {clean_current} 💰")
    
    lines.append("")
    lines.append(f"🔗 {original_url}")
    
    return "\n".join(lines), product_name_ar, brand_ar

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ يرسل رابط المنتج من أمازون السعودية")
        return

    for original_url in urls:
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
            post, product_ar, brand_ar = generate_post(full_title, price, old_price, discount_percent, original_url)
            
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
            
        except Exception as e:
            print(f"Error: {e}")
            bot.edit_message_text("❌ صار خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت شغال باللهجة السعودية...")
bot.infinity_polling()
