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
# 🔄 قاموس ترجمة المنتجات
# ===================================
TRANSLATION_DICT = {
    "iphone": "آيفون",
    "samsung": "سامسونج",
    "xiaomi": "شاومي",
    "huawei": "هواوي",
    "airpods": "سماعات آيربودز",
    "earbuds": "سماعات أذن",
    "headphones": "سماعات رأس",
    "laptop": "لابتوب",
    "macbook": "ماك بوك",
    "tablet": "تابلت",
    "ipad": "آيباد",
    "watch": "ساعة ذكية",
    "smartwatch": "ساعة ذكية",
    "charger": "شاحن",
    "cable": "كيبل",
    "power bank": "باور بانك",
    "battery": "بطارية",
    "screen": "شاشة",
    "monitor": "شاشة عرض",
    "keyboard": "كيبورد",
    "mouse": "ماوس",
    "camera": "كاميرا",
    "speaker": "سماعة",
    "tv": "تلفزيون",
    "television": "تلفزيون",
    "shoes": "حذاء",
    "sneakers": "حذاء رياضي",
    "boots": "بوت",
    "sandals": "صندل",
    "t-shirt": "تيشيرت",
    "shirt": "قميص",
    "pants": "بنطلون",
    "jeans": "جينز",
    "jacket": "جاكيت",
    "hoodie": "هودي",
    "dress": "فستان",
    "skirt": "تنورة",
    "socks": "شرابات",
    "bag": "شنطة",
    "backpack": "حقيبة ظهر",
    "perfume": "عطر",
    "fragrance": "عطر",
    "cream": "كريم",
    "lotion": "لوشن",
    "shampoo": "شامبو",
    "conditioner": "بلسم",
    "soap": "صابون",
    "refrigerator": "ثلاجة",
    "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة كهربائية",
    "air conditioner": "مكيف",
    "ac": "مكيف",
    "heater": "دفاية",
    "fan": "مروحة",
    "blender": "خلاط",
    "mixer": "عجانة",
    "oven": "فرن",
    "microwave": "مايكرويف",
    "toaster": "محمصة",
    "kettle": "غلاية",
    "coffee maker": "ماكينة قهوة",
    "iron": "مكواة",
    "hair dryer": "سشوار",
    "chair": "كرسي",
    "table": "طاولة",
    "desk": "مكتب",
    "bed": "سرير",
    "sofa": "كنبة",
    "couch": "كنبة",
    "lamp": "لمبة",
    "light": "إضاءة",
    "mirror": "مرآة",
    "carpet": "سجادة",
    "curtain": "ستارة",
    "treadmill": "سير كهربائي",
    "dumbbell": "دامبل",
    "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة",
    "ball": "كرة",
    "toys": "ألعاب",
    "toy": "لعبة",
    "baby": "أطفال",
    "kids": "أطفال",
    "stroller": "عربة أطفال",
    "car seat": "كرسي سيارة للأطفال",
    "car": "سيارة",
    "tire": "إطار",
    "oil": "زيت",
    "cleaner": "منظف",
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "digital": "رقمي",
    "electric": "كهربائي",
    "automatic": "أوتوماتيك",
    "portable": "محمول",
    "professional": "احترافي",
    "original": "أصلي",
    "new": "جديد",
    "pro": "برو",
    "max": "ماكس",
    "plus": "بلس",
    "ultra": "ألترا",
    "mini": "ميني",
    "premium": "بريميوم",
    "deluxe": "ديلوكس",
    "unisex": "للجنسين",
    "adult": "للبالغين",
    "men": "رجالي",
    "women": "نسائي",
    "black": "أسود",
    "white": "أبيض",
    "blue": "أزرق",
    "red": "أحمر",
    "green": "أخضر",
}

# ===================================
# 🎯 الجمل التسويقية مع hook حسب نوع المنتج
# ===================================
HOOKS = {
    "phone": ["🔥 ما يفوتك!", "📱 وصل الجديد!", "⚡ أفضل صفقة على الهاتف!"],
    "headphones": ["🎧 جرب أفضل تجربة صوت!", "🔊 صوت واضح وجودة عالية!", "🔥 عرض سماعات اليوم!"],
    "laptop": ["💻 استثمر في جهاز قوي!", "⚡ أفضل لابتوبات بسعر ممتاز!", "🔥 صفقة لا تعوض!"],
    "watch": ["⌚ خلي حياتك أسهل!", "🔥 ساعة ذكية بسعر رهيب!", "🎯 لا تفوت هذه الفرصة!"],
    "clothes": ["👗 تألقي بأحدث صيحات الموضة!", "🧥 اختياراتك تعكس ذوقك!", "🔥 عروض الملابس المميزة اليوم!"],
    "shoes": ["🥿 حذاء مريح وأنيق!", "🔥 احصل على أفضل حذاء اليوم!", "👟 عروض مميزة على الأحذية!"],
    "kids": ["🧸 خلي صغيرك سعيد!", "🚼 كل احتياجات طفلك هنا!", "🎁 ألعاب وهدايا ممتعة!"],
    "home": ["🏡 خلي بيتك أرقى!", "✨ أفضل الأجهزة المنزلية!", "🔥 وفر وقتك وجهدك اليوم!"],
    "default": ["🎯 فرصة مميزة لا تفوت!", "💰 أفضل صفقة اليوم!", "✨ منتج بجودة وسعر ممتاز!"]
}

# ===================================
# 🔧 دوال المساعدة
# ===================================
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

def smart_arabic_title(full_title):
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()  
    unique_words = []  
    for word in words:  
        if not unique_words or word.lower() != unique_words[-1].lower():  
            unique_words.append(word)  
    result = " ".join(unique_words)  
    if len(result) > 100:  
        for sep in ['،', ',', '-', '|', '/']:  
            if sep in result[:100]:  
                idx = result.rfind(sep, 50, 100)  
                if idx > 0:  
                    result = result[:idx]  
                    break  
        else:  
            idx = result.rfind(' ', 80, 100)  
            if idx > 0:  
                result = result[:idx]  
            else:  
                result = result[:100]  
    return result.strip()

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
            return f"{num_int} ريال سعودي"
    except:
        pass
    return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================
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
                        sorted_urls = sorted(img_dict.keys(), key=lambda x: img_dict[x][0]*img_dict[x][1], reverse=True)    
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

# ===================================
# 🔍 استخراج بيانات المنتج
# ===================================
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

            # تجربة عدة selectors للعنوان
            title_elem = soup.select_one("#productTitle") or soup.select_one(".product-title-word-break")
            if not title_elem:    
                continue    
            full_title = title_elem.text.strip()    

            # تجربة عدة selectors للسعر
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
                arabic_title = smart_arabic_title(full_title)    
                return arabic_title, price, old_price, image, discount_percent    
        except Exception as e:    
            print(f"Attempt {attempt + 1} failed: {e}")    
            continue    
    return None

# ===================================
# ✨ التوليد النهائي مع hook مخصص
# ===================================
def generate_post(product_name, price, old_price, discount_percent, original_url):
    product_lower = product_name.lower()
    if any(k in product_lower for k in ["iphone", "samsung", "xiaomi", "huawei", "phone", "tablet", "ipad"]):
        opening = random.choice(HOOKS["phone"])
    elif any(k in product_lower for k in ["airpods", "headphones", "earbuds", "speaker"]):
        opening = random.choice(HOOKS["headphones"])
    elif any(k in product_lower for k in ["laptop", "macbook", "monitor", "keyboard", "mouse"]):
        opening = random.choice(HOOKS["laptop"])
    elif any(k in product_lower for k in ["watch", "smartwatch"]):
        opening = random.choice(HOOKS["watch"])
    elif any(k in product_lower for k in ["shirt", "t-shirt", "jeans", "jacket", "hoodie", "dress", "skirt"]):
        opening = random.choice(HOOKS["clothes"])
    elif any(k in product_lower for k in ["shoes", "sneakers", "boots", "sandals"]):
        opening = random.choice(HOOKS["shoes"])
    elif any(k in product_lower for k in ["baby", "kids", "toy", "stroller"]):
        opening = random.choice(HOOKS["kids"])
    elif any(k in product_lower for k in ["fridge", "refrigerator", "washing machine", "oven", "microwave", "blender", "fan", "ac", "heater"]):
        opening = random.choice(HOOKS["home"])
    else:
        opening = random.choice(HOOKS["default"])

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None

    lines = [opening, "", f"🛒 {product_name}", ""]
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الآن: {clean_current} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean    "camera": "كاميرا",
    "speaker": "سماعة",
    "tv": "تلفزيون",
    "television": "تلفزيون",
    "shoes": "حذاء",
    "sneakers": "حذاء رياضي",
    "boots": "بوت",
    "sandals": "صندل",
    "t-shirt": "تيشيرت",
    "shirt": "قميص",
    "pants": "بنطلون",
    "jeans": "جينز",
    "jacket": "جاكيت",
    "hoodie": "هودي",
    "dress": "فستان",
    "skirt": "تنورة",
    "socks": "شرابات",
    "bag": "شنطة",
    "backpack": "حقيبة ظهر",
    "perfume": "عطر",
    "fragrance": "عطر",
    "cream": "كريم",
    "lotion": "لوشن",
    "shampoo": "شامبو",
    "conditioner": "بلسم",
    "soap": "صابون",
    "refrigerator": "ثلاجة",
    "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة كهربائية",
    "air conditioner": "مكيف",
    "ac": "مكيف",
    "heater": "دفاية",
    "fan": "مروحة",
    "blender": "خلاط",
    "mixer": "عجانة",
    "oven": "فرن",
    "microwave": "مايكرويف",
    "toaster": "محمصة",
    "kettle": "غلاية",
    "coffee maker": "ماكينة قهوة",
    "iron": "مكواة",
    "hair dryer": "سشوار",
    "chair": "كرسي",
    "table": "طاولة",
    "desk": "مكتب",
    "bed": "سرير",
    "sofa": "كنبة",
    "couch": "كنبة",
    "lamp": "لمبة",
    "light": "إضاءة",
    "mirror": "مرآة",
    "carpet": "سجادة",
    "curtain": "ستارة",
    "treadmill": "سير كهربائي",
    "dumbbell": "دامبل",
    "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة",
    "ball": "كرة",
    "toys": "ألعاب",
    "toy": "لعبة",
    "baby": "أطفال",
    "kids": "أطفال",
    "stroller": "عربة أطفال",
    "car seat": "كرسي سيارة للأطفال",
    "car": "سيارة",
    "tire": "إطار",
    "oil": "زيت",
    "cleaner": "منظف",
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "digital": "رقمي",
    "electric": "كهربائي",
    "automatic": "أوتوماتيك",
    "portable": "محمول",
    "professional": "احترافي",
    "original": "أصلي",
    "new": "جديد",
    "pro": "برو",
    "max": "ماكس",
    "plus": "بلس",
    "ultra": "ألترا",
    "mini": "ميني",
    "premium": "بريميوم",
    "deluxe": "ديلوكس",
    "unisex": "للجنسين",
    "adult": "للبالغين",
    "men": "رجالي",
    "women": "نسائي",
    "black": "أسود",
    "white": "أبيض",
    "blue": "أزرق",
    "red": "أحمر",
    "green": "أخضر",
}

# ===================================
# 🎯 الجمل التسويقية مع hook حسب نوع المنتج
# ===================================
HOOKS = {
    "phone": ["🔥 ما يفوتك!", "📱 وصل الجديد!", "⚡ أفضل صفقة على الهاتف!"],
    "headphones": ["🎧 جرب أفضل تجربة صوت!", "🔊 صوت واضح وجودة عالية!", "🔥 عرض سماعات اليوم!"],
    "laptop": ["💻 استثمر في جهاز قوي!", "⚡ أفضل لابتوبات بسعر ممتاز!", "🔥 صفقة لا تعوض!"],
    "watch": ["⌚ خلي حياتك أسهل!", "🔥 ساعة ذكية بسعر رهيب!", "🎯 لا تفوت هذه الفرصة!"],
    "clothes": ["👗 تألقي بأحدث صيحات الموضة!", "🧥 اختياراتك تعكس ذوقك!", "🔥 عروض الملابس المميزة اليوم!"],
    "shoes": ["🥿 حذاء مريح وأنيق!", "🔥 احصل على أفضل حذاء اليوم!", "👟 عروض مميزة على الأحذية!"],
    "kids": ["🧸 خلي صغيرك سعيد!", "🚼 كل احتياجات طفلك هنا!", "🎁 ألعاب وهدايا ممتعة!"],
    "home": ["🏡 خلي بيتك أرقى!", "✨ أفضل الأجهزة المنزلية!", "🔥 وفر وقتك وجهدك اليوم!"],
    "default": ["🎯 فرصة مميزة لا تفوت!", "💰 أفضل صفقة اليوم!", "✨ منتج بجودة وسعر ممتاز!"]
}

# ===================================
# 🔧 دوال المساعدة
# ===================================
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

def smart_arabic_title(full_title):
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()  
    unique_words = []  
    for word in words:  
        if not unique_words or word.lower() != unique_words[-1].lower():  
            unique_words.append(word)  
    result = " ".join(unique_words)  
    if len(result) > 100:  
        for sep in ['،', ',', '-', '|', '/']:  
            if sep in result[:100]:  
                idx = result.rfind(sep, 50, 100)  
                if idx > 0:  
                    result = result[:idx]  
                    break  
        else:  
            idx = result.rfind(' ', 80, 100)  
            if idx > 0:  
                result = result[:idx]  
            else:  
                result = result[:100]  
    return result.strip()

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
            return f"{num_int} ريال سعودي"
    except:
        pass
    return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================
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
                        sorted_urls = sorted(img_dict.keys(), key=lambda x: img_dict[x][0]*img_dict[x][1], reverse=True)    
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

# ===================================
# 🔍 استخراج بيانات المنتج
# ===================================
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

            # تجربة عدة selectors للعنوان
            title_elem = soup.select_one("#productTitle") or soup.select_one(".product-title-word-break")
            if not title_elem:    
                continue    
            full_title = title_elem.text.strip()    

            # تجربة عدة selectors للسعر
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
                arabic_title = smart_arabic_title(full_title)    
                return arabic_title, price, old_price, image, discount_percent    
        except Exception as e:    
            print(f"Attempt {attempt + 1} failed: {e}")    
            continue    
    return None

# ===================================
# ✨ التوليد النهائي مع hook مخصص
# ===================================
def generate_post(product_name, price, old_price, discount_percent, original_url):
    product_lower = product_name.lower()
    if any(k in product_lower for k in ["iphone", "samsung", "xiaomi", "huawei", "phone", "tablet", "ipad"]):
        opening = random.choice(HOOKS["phone"])
    elif any(k in product_lower for k in ["airpods", "headphones", "earbuds", "speaker"]):
        opening = random.choice(HOOKS["headphones"])
    elif any(k in product_lower for k in ["laptop", "macbook", "monitor", "keyboard", "mouse"]):
        opening = random.choice(HOOKS["laptop"])
    elif any(k in product_lower for k in ["watch", "smartwatch"]):
        opening = random.choice(HOOKS["watch"])
    elif any(k in product_lower for k in ["shirt", "t-shirt", "jeans", "jacket", "hoodie", "dress", "skirt"]):
        opening = random.choice(HOOKS["clothes"])
    elif any(k in product_lower for k in ["shoes", "sneakers", "boots", "sandals"]):
        opening = random.choice(HOOKS["shoes"])
    elif any(k in product_lower for k in ["baby", "kids", "toy", "stroller"]):
        opening = random.choice(HOOKS["kids"])
    elif any(k in product_lower for k in ["fridge", "refrigerator", "washing machine", "oven", "microwave", "blender", "fan", "ac", "heater"]):
        opening = random.choice(HOOKS["home"])
    else:
        opening = random.choice(HOOKS["default"])

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None

    lines = [opening, "", f"🛒 {product_name}", ""]
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الآن: {clean_current} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean
