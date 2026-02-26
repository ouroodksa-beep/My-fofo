import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

def expand_url(url):
    """يفك الروابط المختصرة"""
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co']):
            r = requests.get(url, allow_redirects=True, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            return r.url
        return url
    except:
        return url

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

def extract_domain(url):
    """يستخرج دومين أمازون من الرابط"""
    match = re.search(r'amazon\.([a-z\.]+)', url.lower())
    if match:
        return match.group(1)
    # افتراضياً نجرب السعودية
    return "sa"

def get_product(asin, domain="sa"):
    """يجيب المنتج من أي دومين أمازون"""
    
    # نجرب الدومين اللي جاي من الرابط أولاً
    domains_to_try = [domain, "sa", "com", "ae"]
    domains_to_try = list(dict.fromkeys(domains_to_try))  # نشيل التكرار
    
    for current_domain in domains_to_try:
        url = f"https://www.amazon.{current_domain}/dp/{asin}"
        print(f"Trying: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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
            print(f"Status for .{current_domain}: {r.status_code}")
            
            if r.status_code != 200:
                continue
                
            soup = BeautifulSoup(r.text, "html.parser")
            
            # نتأكد إن الصفحة مش خطأ
            if "captcha" in r.text.lower() or "robot" in r.text.lower():
                print(f"Captcha detected on .{current_domain}")
                continue
            
            # العنوان
            title_elem = soup.select_one("#productTitle")
            if not title_elem:
                title_elem = soup.select_one("h1.a-size-large")
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            if not title or len(title) < 3:
                continue
                
            print(f"Found title on .{current_domain}: {title[:50]}")

            # استخراج السعر
            price = None
            old_price = None
            
            # السعر الحالي
            price_selectors = [
                ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
                ".a-price.a-text-price.apexPriceToPay .a-offscreen",
                ".a-price.aok-align-center .a-offscreen",
                ".a-price .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
                ".a-price-whole",
                ".a-price-to-pay .a-offscreen",
                ".a-price-buy-box .a-offscreen"
            ]
            
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem:
                    price_text = elem.text.strip()
                    if price_text and any(c.isdigit() for c in price_text):
                        price = price_text
                        break

            # لو ملقناش، ندور في النص
            if not price:
                # ندور على أي سعر بالعملات المختلفة
                price_patterns = [
                    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:ر\.?س|SAR|ريال|رس)',  # ريال
                    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # دولار
                    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*AED',  # درهم
                    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:SR|sar|S\.?A\.?R)',  # ريال صريح
                ]
                for pattern in price_patterns:
                    matches = re.findall(pattern, r.text)
                    if matches:
                        # نختار أصغر سعر (السعر الحالي)
                        price = min(matches, key=lambda x: float(x.replace(',', '')))
                        if '$' in r.text[:1000]:
                            price = f"${price}"
                        else:
                            price = f"{price} ر.س"
                        break

            # السعر القديم
            old_selectors = [
                ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
                ".a-price.a-text-price .a-offscreen",
                ".basisPrice .a-offscreen",
                ".priceBlockStrikePriceString"
            ]
            
            for selector in old_selectors:
                elem = soup.select_one(selector)
                if elem:
                    old_text = elem.text.strip()
                    if old_text != price and any(c.isdigit() for c in old_text):
                        old_price = old_text
                        break

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
            except:
                pass

            if price:
                print(f"Success on .{current_domain}!")
                return title, price, old_price, image, discount_percent, current_domain
                
        except Exception as e:
            print(f"Error on .{current_domain}: {e}")
            continue
    
    return None

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

def generate_post(title, price, old_price, discount_percent, original_url, domain):
    opening = random.choice(OPENINGS)
    reaction = random.choice(REACTIONS)
    urgency = random.choice(URGENCY)
    
    display_title = title[:60] + "..." if len(title) > 60 else title
    
    if discount_percent and discount_percent > 5:
        price_line = f"💰 {price} (وفر {discount_percent}%) | ❌ {old_price}"
    else:
        price_line = f"💰 {price}"
    
    # نذكر الدومين لو مش سعودي
    domain_flag = ""
    if domain != "sa":
        domain_names = {"com": "🇺🇸 أمازون أمريكا", "ae": "🇦🇪 أمازون الإمارات", "uk": "🇬🇧 أمازون بريطانيا", "de": "🇩🇪 أمازون ألمانيا"}
        domain_flag = f"\n🌐 {domain_names.get(domain, 'أمازون عالمي')}"
    
    post = f"""{opening}

🛒 {display_title}{domain_flag}

{price_line}

👉 {reaction} | ⏰ {urgency}

🔗 {original_url}"""
    
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)
    
    print(f"URLs: {urls}")

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج من أمازون")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        print(f"Expanded: {expanded}")
        
        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أفهم الرابط\nجرب رابط أمازون طويل (amazon.sa/dp/... أو amazon.com/dp/...)")
            continue

        domain = extract_domain(expanded)
        print(f"ASIN: {asin}, Domain: {domain}")

        wait = bot.reply_to(msg, "⏳ جاري البحث عن المنتج...")

        product = get_product(asin, domain)

        if not product:
            bot.edit_message_text(
                f"❌ المنتج مش متاح في أمازون السعودية\nASIN: `{asin}`\n\nجرب رابط منتج ثاني متاح في amazon.sa", 
                msg.chat.id, wait.message_id,
                parse_mode="Markdown"
            )
            continue

        title, price, old_price, image, discount_percent, found_domain = product
        post = generate_post(title, price, old_price, discount_percent, original_url, found_domain)

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
