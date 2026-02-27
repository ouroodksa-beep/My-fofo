import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🎯 جمل تسويقية سعودية عشوائية
# ===================================

OPENING_SENTENCES = [
    "والله صفقة ما تتفوت 🔥",
    "ما شاء الله تبارك الله السعر حلو 💥",
    "سعر خرافي صراحة ⚡️",
    "فرصة ذهبية الحين 🎯",
    "عرض ناري وما يتكرر 🔥",
    "الحين أو لا 💪",
    "ببلاش تقريباً 😍",
    "تخفيض مجنون 👌",
    "صفقة العمر هذي 💯",
    "الكمية قليلة جداً ⚠️",
    "ينتهي بأي لحظة ⏰",
    "لا تنام عليه 🚨",
    "خذه فوراً 💨",
    "هاته الحين قبل يروح 🏃‍♂️",
    "ما راح تلقى مثله 👀",
    "سعر تاريخي 📉",
    "فرصة لا تعوض أبداً 💎",
    "الوقت ينفد بسرعة ⏳",
    "احجز قبل الكل 🏆",
    "المنتج مطلوب جداً 🔥",
]

# ===================================
# 🔄 قاموس ترجمة المنتجات للعربي
# ===================================

TRANSLATION_DICT = {
    # إلكترونيات
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
    "router": "راوتر",
    "modem": "مودم",
    
    # أحذية وملابس
    "shoes": "حذاء",
    "shoe": "حذاء",
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
    
    # عطور ومستحضرات
    "perfume": "عطر",
    "fragrance": "عطر",
    "oud": "عود",
    "musk": "مسك",
    "cream": "كريم",
    "lotion": "لوشن",
    "shampoo": "شامبو",
    "conditioner": "بلسم",
    "soap": "صابون",
    
    # أجهزة منزلية
    "refrigerator": "ثلاجة",
    "fridge": "ثلاجة",
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
    
    # أثاث وديكور
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
    
    # رياضة ولياقة
    "treadmill": "سير كهربائي",
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
    "car seat": "كرسي سيارة للأطفال",
    
    # سيارات
    "car": "سيارة",
    "tire": "إطار",
    "battery": "بطارية سيارة",
    "oil": "زيت",
    "cleaner": "منظف",
    
    # عام
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
}


def translate_to_arabic(text):
    """
    يترجم الكلمات الإنجليزية للعربي بشكل ذكي
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    # نبدأ بالبراند (أول كلمة)
    translated_words = []
    
    for word in words:
        # ننظف الكلمة من الرموز
        clean_word = re.sub(r'[^\w\s]', '', word)
        
        # ندور على الترجمة
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            # لو مالقناش ترجمة، نحتفظ بالكلمة الأصلية
            translated_words.append(word)
    
    # ندمج الكلمات
    result = " ".join(translated_words)
    
    # نحسن النتيجة (نشيل التكرارات)
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)  # تكرار كلمات
    
    return result


def smart_arabic_title(full_title):
    """
    يحول العنوان للعربي بشكل ذكي وقصير
    """
    # نختصر العنوان الأول
    words = full_title.split()
    
    if len(words) <= 10:
        short_title = full_title
    else:
        # ناخذ أول 10-12 كلمة
        short_words = words[:12]
        short_title = " ".join(short_words)
    
    # نترجم للعربي
    arabic_title = translate_to_arabic(short_title)
    
    # نتأكد إن العنوان مش طويل (سطر ونصف)
    if len(arabic_title) > 85:
        # نختصر لآخر مسافة مناسبة
        cut_point = arabic_title.rfind(' ', 50, 85)
        if cut_point == -1:
            cut_point = 80
        arabic_title = arabic_title[:cut_point] + "..."
    
    return arabic_title


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
        nums = re.findall(r'[\d,]+', price_text)
        if nums:
            num = nums[0].replace(",", "")
            return f"{num} ريال سعودي"
    except:
        pass
    return price_text


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
            print(f"Original: {full_title[:80]}...")
            
            # نحول للعربي
            arabic_title = smart_arabic_title(full_title)
            print(f"Arabic: {arabic_title}")

            # السعر
            price = None
            price_selectors = [
                ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
                ".a-price.a-text-price.apexPriceToPay .a-offscreen",
                ".a-price .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
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
            image = None
            img_elem = soup.select_one("#landingImage")
            if img_elem:
                image = img_elem.get("src") or img_elem.get("data-old-hires")

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
                return arabic_title, price, old_price, image, discount_percent
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    return None


# ===================================
# ✨ التوليد النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    opening = random.choice(OPENING_SENTENCES)
    
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    
    lines = [opening]
    lines.append("")
    lines.append(f"🛒 {product_name}")  # اسم المنتج بالعربي
    lines.append("")
    
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الحين: {clean_current} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean_current}")
    
    lines.append("")
    lines.append(f"🔗 {original_url}")
    
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
        except:
            bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()
