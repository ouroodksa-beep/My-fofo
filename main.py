import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

def expand_url(url):
    """يفك الروابط المختصرة باستخدام GET بدل HEAD"""
    try:
        # لو الرابط مختصر، نستخدم GET عشان نتبع التوجيه
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'short.link', 'ow.ly', 'is.gd']):
            r = requests.get(url, allow_redirects=True, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            print(f"Expanded {url} -> {r.url}")
            return r.url
        return url
    except Exception as e:
        print(f"Expand error: {e}")
        return url

def extract_asin(url):
    """يستخرج ASIN من أي رابط أمازون"""
    # ندور على ASIN (10 حروف كبيرة وأرقام)
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'([A-Z0-9]{10})/?$',  # في نهاية الرابط
        r'([A-Z0-9]{10})(?:[/?]|\b)'  # في أي مكان
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            asin = m.group(1)
            print(f"Found ASIN: {asin}")
            return asin
    return None

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 404:
            print("Product not found")
            return None
            
        if r.status_code != 200:
            print(f"Bad status: {r.status_code}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # العنوان
    title_elem = soup.select_one("#productTitle")
    if not title_elem:
        # نجرب ندور على عنوان بديل
        title_elem = soup.select_one("h1.a-size-large")
        if not title_elem:
            print("No title found in page")
            return None
    
    title = title_elem.text.strip()
    print(f"Title: {title[:50]}")

    # استخراج السعر - طرق متعددة
    price = None
    old_price = None
    
    # الطريقة 1: السعر الرئيسي
    price_elem = soup.select_one(".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen")
    if not price_elem:
        price_elem = soup.select_one(".a-price.a-text-price.apexPriceToPay .a-offscreen")
    if not price_elem:
        price_elem = soup.select_one(".a-price.aok-align-center .a-offscreen")
    if not price_elem:
        price_elem = soup.select_one(".a-price .a-offscreen")
    
    if price_elem:
        price = price_elem.text.strip()
        print(f"Price from element: {price}")

    # لو ملقناش، ندور في النص
    if not price:
        # ندور على نمط السعر بالريال
        price_matches = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:ر\.?س|SAR|ريال|رس)', r.text)
        if price_matches:
            # نختار أصغر سعر (السعر الحالي عادة)
            price = f"{min(price_matches, key=lambda x: float(x.replace(',', '')))} ر.س"
            print(f"Price from text: {price}")

    # السعر القديم
    old_elem = soup.select_one(".a-price.a-text-price[data-a-color='secondary'] .a-offscreen")
    if old_elem:
        old_price = old_elem.text.strip()
        if old_price == price:
            old_price = None
        else:
            print(f"Old price: {old_price}")

    # الصورة
    image = None
    img_elem = soup.select_one("#landingImage")
    if img_elem:
        image = img_elem.get("src") or img_elem.get("data-old-hires")
        if not image:
            data = img_elem.get("data-a-dynamic-image")
            if data:
                try:
                    import json
                    img_dict = json.loads(data)
                    image = list(img_dict.keys())[0] if img_dict else None
                except:
                    pass

    # حساب الخصم
    discount_percent = None
    try:
        if old_price and price:
            def get_num(text):
                nums = re.findall(r'[\d,]+\.?\d*', text)
                return float(nums[0].replace(",", "")) if nums else 0
            
            old_num = get_num(old_price)
            new_num = get_num(price)
            
            if old_num > new_num > 0:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
                print(f"Discount: {discount_percent}%")
    except Exception as e:
        print(f"Discount calc error: {e}")

    if not price:
        print("No price found at all")
        return None

    return title, price, old_price, image, discount_percent

OPENINGS = [
    "🔥 سعر مجنون",
    "⚡️ فرصة ذهبية",
    "💥 عرض ناري",
    "🎯 صفقة العمر",
    "🔥 ما يتكرر",
    "⚡️ الحين أو لا",
    "💥 خصم خرافي"
]

REACTIONS = [
    "هاته الحين",
    "ما تفكر",
    "خذه فوراً",
    "بسرعة قبل ينتهي",
    "لا تنام عليه",
    "احجز فوري",
    "ما راح تلقى مثله"
]

URGENCY = [
    "ينتهي اليوم",
    "الكمية قليلة",
    "سعر مؤقت",
    "بأي لحظة يرجع",
    "الوقت ينفد",
    "لا تتردد",
    "فرصة لا تعوض"
]

def generate_post(title, price, old_price, discount_percent, original_url):
    opening = random.choice(OPENINGS)
    reaction = random.choice(REACTIONS)
    urgency = random.choice(URGENCY)
    
    display_title = title[:60] + "..." if len(title) > 60 else title
    
    if discount_percent and discount_percent > 5:
        price_line = f"💰 {price} (وفر {discount_percent}%) | ❌ {old_price}"
    else:
        price_line = f"💰 {price}"
    
    post = f"""{opening}

🛒 {display_title}

{price_line}

👉 {reaction} | ⏰ {urgency}

🔗 {original_url}"""
    
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)
    
    print(f"Message: {text}")
    print(f"URLs found: {urls}")

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج من أمازون")
        return

    for original_url in urls:
        # نفك الرابط
        expanded = expand_url(original_url)
        print(f"Processing: {expanded}")
        
        asin = extract_asin(expanded)
        
        if not asin:
            bot.reply_to(msg, f"❌ ما قدرت أفهم الرابط\n`{original_url[:40]}...`\nجرب رابط طويل من أمازون السعودية", parse_mode="Markdown")
            continue

        wait = bot.reply_to(msg, f"⏳ جاري تحليل المنتج...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text(
                f"❌ ما قدرت أقرأ المنتج\nASIN: `{asin}`\n\nتأكد إن:\n• المنتج متاح في amazon.sa\n• الرابط صحيح\n• المنتج مش محذوف", 
                msg.chat.id, wait.message_id,
                parse_mode="Markdown"
            )
            continue

        title, price, old_price, image, discount_percent = product
        post = generate_post(title, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Send error: {e}")
            bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت يعمل...")
bot.infinity_polling()
