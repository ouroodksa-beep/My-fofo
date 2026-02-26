import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

def expand_url(url):
    """يفك الروابط المختصرة ويرجع الرابط النهائي"""
    try:
        # لو الرابط مختصر
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ow.ly', 'short.link']):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            # نستخدم allow_redirects=True عشان نتبع التوجيه
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            final_url = r.url
            print(f"Expanded: {url} -> {final_url}")
            return final_url
            
        return url
    except Exception as e:
        print(f"Expand error: {e}")
        return url

def is_saudi_amazon(url):
    """يتأكد إن الرابط لأمازون السعودية"""
    saudi_domains = ['amazon.sa', 'www.amazon.sa', 'amazon.sa/']
    url_lower = url.lower()
    return any(domain in url_lower for domain in saudi_domains)

def extract_asin(url):
    """يستخرج ASIN من أي رابط أمازون"""
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

def get_product(asin):
    """Scraping قوي لأمازون السعودية فقط"""
    url = f"https://www.amazon.sa/dp/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.google.com/",
        "Origin": "https://www.amazon.sa"
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        if r.status_code != 200:
            print(f"Status: {r.status_code}")
            return None
            
        if len(r.text) < 3000 or "captcha" in r.text.lower():
            print("Captcha or blocked")
            return None
            
    except Exception as e:
        print(f"Request error: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # العنوان
    title = None
    title_selectors = [
        "#productTitle",
        "h1.a-size-large.a-spacing-none",
        "h1.a-size-large",
        "#title"
    ]
    
    for selector in title_selectors:
        elem = soup.select_one(selector)
        if elem:
            title = elem.text.strip()
            if len(title) > 5:
                break
    
    if not title:
        return None

    # السعر الحالي
    price = None
    price_selectors = [
        ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
        ".a-price.a-text-price.apexPriceToPay .a-offscreen",
        ".a-price.aok-align-center .a-offscreen",
        ".a-price .a-offscreen",
        "[data-a-color='price'] .a-offscreen",
        ".a-price-to-pay .a-offscreen",
        ".a-price-buy-box .a-offscreen",
        ".a-price-whole"
    ]
    
    for selector in price_selectors:
        try:
            elem = soup.select_one(selector)
            if elem and elem.text:
                text = elem.text.strip()
                if any(c.isdigit() for c in text):
                    price = text
                    break
        except:
            continue
    
    # Regex لو فشلت كلهم
    if not price:
        price_matches = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:ر\.?س|SAR|ريال|رس)', r.text)
        if price_matches:
            clean_nums = [float(p.replace(',', '')) for p in price_matches]
            min_price = min(clean_nums)
            price = f"{min_price:,.2f} ر.س"

    # السعر القديم
    old_price = None
    old_selectors = [
        ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
        ".a-price.a-text-price .a-offscreen",
        ".basisPrice .a-offscreen",
        ".priceBlockStrikePriceString"
    ]
    
    for selector in old_selectors:
        try:
            elem = soup.select_one(selector)
            if elem and elem.text:
                text = elem.text.strip()
                if text != price and any(c.isdigit() for c in text):
                    old_price = text
                    break
        except:
            continue

    # الصورة
    image = None
    img_elem = soup.select_one("#landingImage")
    if img_elem:
        image = img_elem.get("src") or img_elem.get("data-old-hires")
        if not image:
            data = img_elem.get("data-a-dynamic-image")
            if data and data.startswith("{"):
                try:
                    import json
                    img_dict = json.loads(data)
                    image = list(img_dict.keys())[0] if img_dict else None
                except:
                    pass

    # الخصم
    discount_percent = None
    try:
        if old_price and price:
            def extract_num(text):
                nums = re.findall(r'[\d,]+\.?\d*', str(text))
                return float(nums[0].replace(",", "")) if nums else 0
            
            old_num = extract_num(old_price)
            new_num = extract_num(price)
            
            if old_num > new_num > 0:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        pass

    if not price:
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
    
    print(f"Message: {text[:100]}")

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج")
        return

    for original_url in urls:
        # نفك الرابط الأول
        expanded = expand_url(original_url)
        print(f"Expanded: {expanded[:100]}")
        
        # نتأكد إنه أمازون سعودية
        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, 
                f"❌ الرابط مش لأمازون السعودية\n\n"
                f"الرابط المفكوك: `{expanded[:60]}...`\n\n"
                f"لازم يكون الرابط من `amazon.sa`\n"
                f"جرب تحوله لأفيلييت سعودي من OneLink أو Amazon Associates SA",
                parse_mode="Markdown"
            )
            continue
        
        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج رقم المنتج (ASIN)")
            continue

        print(f"ASIN: {asin}")

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text(
                f"❌ ما قدرت أقرأ المنتج\nASIN: `{asin}`\n\n"
                f"ممكن يكون:\n"
                f"• المنتج محذوف من أمازون السعودية\n"
                f"• أمازون حاطة حماية مؤقتة\n"
                f"• جرب منتج تاني", 
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
