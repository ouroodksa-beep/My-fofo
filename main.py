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


def extract_smart_title(full_title):
    """
    يستخرج عنوان ذكي وقصير:
    - البراند (أول كلمة)
    - النوع/الفئة (كلمات مفتاحية)
    - يتجاهل الأرقام والمقاسات والألوان الطويلة
    """
    words = full_title.split()
    
    if not words:
        return "منتج"
    
    # البراند دائماً أول كلمة
    brand = words[0]
    
    # كلمات مفتاحية ندور عليها
    key_types = {
        "سماعة": ["سماعة", "سماعات", "headphone", "earbuds", "airpods", "سماعه"],
        "حذاء": ["حذاء", "حذاء", "shoe", "shoes", "boot", "sneaker", "رياضي"],
        "ساعة": ["ساعة", "ساعات", "watch", "smartwatch", "ساعه"],
        "هاتف": ["هاتف", "جوال", "موبايل", "iphone", "samsung", "xiaomi", "هاتف"],
        "لابتوب": ["لابتوب", "لابتوب", "laptop", "macbook", "notebook", "كمبيوتر"],
        "شنطة": ["شنطة", "شنط", "bag", "backpack", "حقيبة", "شنطه"],
        "نظارة": ["نظارة", "نظارات", "glass", "sunglasses", "نظاره"],
        "كاميرا": ["كاميرا", "كاميرات", "camera", "كاميره"],
        "تلفزيون": ["تلفزيون", "تلفزيون", "tv", "television", "شاشة"],
        "عطر": ["عطر", "عطور", "perfume", "fragrance", "oud", "عطر"],
        "مكيف": ["مكيف", "مكيفات", "ac", "air conditioner", "تكييف"],
        "مروحة": ["مروحة", "مراوح", "fan", "مروحه"],
        "ماكينة": ["ماكينة", "ماكينات", "machine", "ماكينه"],
    }
    
    # ندور على النوع في العنوان
    product_type = ""
    for ptype, keywords in key_types.items():
        for keyword in keywords:
            if keyword.lower() in full_title.lower():
                product_type = ptype
                break
        if product_type:
            break
    
    # لو لقينا نوع، نرجع "براند + نوع"
    if product_type:
        return f"{brand} {product_type}"
    
    # لو مالقيناش، نرجع أول 3 كلمات مفيدة (نتجاهل الأرقام والمقاسات)
    useful_words = []
    for word in words[1:]:  # نبدأ من بعد البراند
        # نتجاهل الأرقام والمقاسات والألوان الطويلة
        if re.match(r'^\d', word):  # يبدأ برقم
            continue
        if any(x in word.lower() for x in ['eu', 'us', 'cm', 'mm', 'gb', 'tb', 'inch', '"']):  # مقاسات
            continue
        if len(word) > 15:  # كلمة طويلة جداً (وصف مفصل)
            continue
        useful_words.append(word)
        if len(useful_words) >= 2:  # كلمتين كفاية بعد البراند
            break
    
    if useful_words:
        return f"{brand} {' '.join(useful_words)}"
    
    # آخر حل: نرجع البراند بس
    return brand


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
            
            # العنوان الكامل
            title_elem = soup.select_one("#productTitle")
            if not title_elem:
                continue
            
            full_title = title_elem.text.strip()
            
            # نستخرج عنوان ذكي
            smart_title = extract_smart_title(full_title)
            print(f"Full: {full_title[:80]}")
            print(f"Smart: {smart_title}")

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
                return smart_title, price, old_price, image, discount_percent
                
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
    lines.append(f"🛒 {product_name}")  # اسم المنتج المحسن
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
