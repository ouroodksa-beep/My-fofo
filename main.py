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
# 🎯 جمل تسويقية سعودية SEO - بدون هاشتاجات
# ===================================

OPENING_SENTENCES = [
    # 🔥 صيدات قوية
    "صيدة اليوم والله صيدة 🎣",
    "صيدة ما تتعوض أبداً",
    "الحقو قبل لا يروح",
    "فرصة صيد نادرة جداً",
    "صيدة السنة هذي صدق",
    "الحقو الحقو يا جماعة",
    "صيدة فخمة وما تتكرر",
    "فرصة ذهبية للي يبغى يوفر",
    "الحقو الكمية محدودة",
    "صيدة محترفين الصيد 🏆",
    
    # ⏰ عروض محدودة
    "ينتهي بأي لحظة",
    "الوقت ينفد بسرعة",
    "لا تنام على الصفقة",
    "العرض ينتهي اليوم",
    "فرصة لحظية فقط",
    "الحقو قبل ينتهي",
    "ينتهي خلال ساعات",
    "الوقت ضيق جداً",
    "الحقو الحين فوراً",
    "قرر الآن أو ندم",
    
    # 💥 إثارة وحماس
    "سعر خرافي صدق",
    "صفقة ما تتفوت",
    "عرض ناري وقوي",
    "الحين أو لا أبداً",
    "ببلاش تقريباً",
    "تخفيض مجنون",
    "صفقة العمر هذي",
    "الكمية قليلة جداً",
    "خذه فوراً",
    "ما راح تلقى مثله",
    
    # 🎯 حماس سعودي
    "يا أخي الحقو",
    "والله العظيم صفقة",
    "ما راح تندم أبداً",
    "ثقة في الله واشتري",
    "السعر يتكلم لوحده",
    "جودة وسعر منافس",
    "الحقو يا أهل الرياض",
    "يا أهل جدة الحقو",
    "يا أهل مكة الحقو",
    "عرض للسعوديين",
    
    # 😱 FOMO قوي
    "الكل يتكلم عنه",
    "المنتج رقم واحد مبيعاً",
    "نفذ من المخزن مرتين",
    "الطلبات جاية من كل مكان",
    "المنتج الأشهر الحين",
    "ترند السعودية",
    "الكل يبغاه",
    "الكمية نفذت قبل",
    "المنتج اللي كله يدور عليه",
    "آخر فرصة للحصول عليه",
    
    # 💪 تحفيز شراء
    "قرر الآن ولا تتردد",
    "التردد خسارة",
    "الفرصة ما تنتظر أحد",
    "الحقو ولا تفكر كثير",
    "اشتري الحين وارتح",
    "السعر ما راح ينزل أكثر",
    "هذا أقل سعر ممكن",
    "العرض الأقوى",
    "الحقو يا صاحبي",
    "استغل الفرصة يا بطل",
]

# ===================================
# 🔄 قاموس ترجمة مختصر SEO
# ===================================

TRANSLATION_DICT = {
    # أجهزة
    "iphone": "آيفون",
    "samsung": "سامسونج",
    "xiaomi": "شاومي",
    "huawei": "هواوي",
    "airpods": "سماعات آبل",
    "earbuds": "سماعات",
    "headphones": "سماعات رأس",
    "laptop": "لابتوب",
    "macbook": "ماك",
    "tablet": "تابلت",
    "ipad": "آيباد",
    "watch": "ساعة",
    "smartwatch": "ساعة ذكية",
    "charger": "شاحن",
    "cable": "سلك",
    "power bank": "باور بانك",
    "battery": "بطارية",
    "screen": "شاشة",
    "keyboard": "كيبورد",
    "mouse": "ماوس",
    "camera": "كاميرا",
    "speaker": "سماعة",
    "tv": "تلفزيون",
    "router": "راوتر",
    
    # ملابس وأزياء
    "shoes": "حذاء",
    "sneakers": "حذاء رياضي",
    "boots": "بوت",
    "sandals": "صندل",
    "slippers": "شبشب",
    "t-shirt": "تيشيرت",
    "shirt": "قميص",
    "pants": "بنطلون",
    "jeans": "جينز",
    "jacket": "جاكيت",
    "hoodie": "هودي",
    "dress": "فستان",
    "skirt": "تنورة",
    "socks": "شرابات",
    "cap": "كاب",
    "hat": "قبعة",
    "bag": "شنطة",
    "backpack": "حقيبة ظهر",
    "wallet": "محفظة",
    
    # عطور وبشرة
    "perfume": "عطر",
    "fragrance": "عطر",
    "oud": "عود",
    "musk": "مسك",
    "cream": "كريم",
    "lotion": "لوشن",
    "shampoo": "شامبو",
    "soap": "صابون",
    
    # أجهزة منزلية
    "refrigerator": "ثلاجة",
    "fridge": "ثلاجة",
    "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة",
    "air conditioner": "مكيف",
    "ac": "مكيف",
    "heater": "دفاية",
    "fan": "مروحة",
    "blender": "خلاط",
    "mixer": "عجانة",
    "oven": "فرن",
    "microwave": "مايكرويف",
    "coffee maker": "ماكينة قهوة",
    "iron": "مكواة",
    "hair dryer": "سشوار",
    
    # أثاث
    "chair": "كرسي",
    "table": "طاولة",
    "desk": "مكتب",
    "bed": "سرير",
    "sofa": "كنبة",
    "lamp": "لمبة",
    "mirror": "مرآة",
    "carpet": "سجادة",
    "curtain": "ستارة",
    
    # رياضة
    "treadmill": "سير",
    "dumbbell": "دامبل",
    "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة",
    "ball": "كرة",
    
    # أطفال
    "toys": "ألعاب",
    "toy": "لعبة",
    "baby": "أطفال",
    "kids": "أطفال",
    "stroller": "عربة أطفال",
    
    # سيارات
    "car": "سيارة",
    "tire": "إطار",
    "oil": "زيت",
    
    # صفات
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "digital": "رقمي",
    "electric": "كهربائي",
    "automatic": "أوتوماتيك",
    "portable": "محمول",
    "original": "أصلي",
    "new": "جديد",
    "pro": "برو",
    "max": "ماكس",
    "plus": "بلس",
    "ultra": "ألترا",
    "mini": "ميني",
    "black": "أسود",
    "white": "أبيض",
}

# كلمات نحذفها من العنوان
REMOVE_WORDS = [
    "amazon", "amazon sa", "saudi", "السعودية", "ksa", "prime",
    "official", "مستورد", "original", "أصلي", "ضمان", "warranty",
    "seller", "بائع", "store", "متجر", "brand", "علامة تجارية",
    "high quality", "جودة عالية", "best", "أفضل", "top", "أعلى",
    "new", "جديد", "2024", "2025", "2026", "model", "موديل"
]

def translate_to_arabic(text):
    text_lower = text.lower()
    words = text_lower.split()
    translated_words = []
    
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            # نحذف الكلمات غير الضرورية
            if clean_word not in [w.lower() for w in REMOVE_WORDS]:
                translated_words.append(word)
    
    result = " ".join(translated_words)
    # نحذف التكرار
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)
    return result

def smart_arabic_title(full_title):
    # نحذف الكلمات غير الضرورية أولاً
    words = full_title.split()
    filtered_words = []
    
    for word in words:
        clean = word.lower().strip(",.()[]{}")
        if clean not in [w.lower() for w in REMOVE_WORDS] and len(word) > 1:
            filtered_words.append(word)
    
    # نختصر العنوان لـ 6 كلمات كحد أقصى
    if len(filtered_words) > 6:
        short_words = filtered_words[:6]
    else:
        short_words = filtered_words
    
    short_title = " ".join(short_words)
    arabic_title = translate_to_arabic(short_title)
    
    # نختصر لو طويل
    if len(arabic_title) > 50:
        cut_point = arabic_title.rfind(' ', 30, 50)
        if cut_point == -1:
            cut_point = 45
        arabic_title = arabic_title[:cut_point]
    
    return arabic_title.strip()

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

# ===================================
# 💰 تنظيف السعر
# ===================================

def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:\.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            num_float = float(num_str)
            num_int = int(num_float)
            return f"{num_int} ريال"
    except:
        pass
    return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================

def get_high_quality_image(soup):
    image = None
    
    # 1. landingImage
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
    
    # 2. gallery
    if not image:
        gallery_img = soup.select_one("#imgTagWrapperId img")
        if gallery_img:
            image = gallery_img.get("data-old-hires") or gallery_img.get("src")
    
    # 3. meta
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
            
            # السعر
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
            
            # السعر القديم
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
            
            # الصورة
            image = get_high_quality_image(soup)
            
            # الخصم
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
# ✨ التوليد النهائي - SEO قوي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    # جملة عشوائية
    opening = random.choice(OPENING_SENTENCES)
    
    # تنظيف الأسعار
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    
    lines = [opening]
    lines.append("")
    lines.append(f"🛒 {product_name}")
    lines.append("")
    
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الحين: {clean_current} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean_current}")
    
    lines.append("")
    lines.append(f"🔗 الرابط: {original_url}")
    
    return "\n".join(lines)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)
    
    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج")
        return
    
    for original_url in urls:
        expanded = expand_url(original_url)
        
        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط لازم يكون من amazon.sa")
            continue
        
        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج رقم المنتج")
            continue
        
        wait = bot.reply_to(msg, "⏳ جاري التحليل...")
        
        product = get_product(asin)
        
        if not product:
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)
            continue
        
        product_name, price, old_price, image, discount_percent = product
        post = generate_post(product_name, price, old_price, discount_percent, original_url)
        
        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت يعمل...")
bot.infinity_polling()
