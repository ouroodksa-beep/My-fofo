import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
import time
from concurrent.futures import ThreadPoolExecutor

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🧠 تحديد نوع المنتج والبراند (بالإنجلش)
# ===================================
def detect_product_type(title):
    t = title.lower()
    brands = {
        "APPLE": ["iphone", "ipad", "macbook", "airpods", "apple"],
        "SAMSUNG": ["samsung", "galaxy"],
        "SONY": ["sony", "playstation"],
        "NIKE": ["nike"],
        "ADIDAS": ["adidas"],
        "HUAWEI": ["huawei"],
        "XIAOMI": ["xiaomi", "mi "],
        "LENOVO": ["lenovo"],
        "DELL": ["dell"],
        "HP": ["hp "],
        "LG": ["lg "],
        "PHILIPS": ["philips"],
        "BOSE": ["bose"],
        "BEATS": ["beats"],
        "RAY-BAN": ["ray-ban", "rayban"],
        "CHANEL": ["chanel"],
        "DIOR": ["dior"],
        "GUCCI": ["gucci"],
        "PRADA": ["prada"],
        "UNDER ARMOUR": ["under armour"],
        "PUMA": ["puma"],
        "REEBOK": ["reebok"],
        "ZARA": ["zara"],
        "H&M": ["h&m"],
        "SHEIN": ["shein"],
        "MAC": ["mac ", "m.a.c"],
        "MAYBELLINE": ["maybelline"],
        "LOREAL": ["l'oreal", "loreal"],
        "NESTLE": ["nestle"],
        "COCA COLA": ["coca cola", "cocacola"],
        "PEPSI": ["pepsi"],
        "STARBUCKS": ["starbucks"],
        "NESCAFE": ["nescafe"],
    }
    
    detected_brand = None
    for brand, keywords in brands.items():
        if any(k in t for k in keywords):
            detected_brand = brand
            break
    
    if any(x in t for x in ["iphone","samsung","headphone","earbuds","laptop","keyboard","mouse","usb","ipad","macbook","airpods","playstation","tv","tablet","charger","cable","monitor","camera","speaker"]):
        return "electronics", detected_brand
    if any(x in t for x in ["shirt","pants","dress","jacket","hoodie","shoes","t-shirt","jeans","sneakers","boots","sandals","watch","sunglasses","bag","wallet","belt","hat","cap"]):
        return "fashion", detected_brand
    if any(x in t for x in ["cream","serum","makeup","lipstick","lotion","perfume","fragrance","shampoo","conditioner","mask","foundation","mascara","eyeliner"]):
        return "beauty", detected_brand
    if any(x in t for x in ["pillow","blanket","kitchen","pan","mattress","sofa","vacuum","lamp","curtain","carpet","table","chair","organizer","storage"]):
        return "home", detected_brand
    if any(x in t for x in ["milk","coffee","tea","chocolate","snack","protein","vitamin","juice","water","honey","dates","nuts","rice","oil"]):
        return "food", detected_brand
    return "general", detected_brand

# ===================================
# 🇸🇦 Hooks سعودية خليجية أصيلة
# ===================================
STYLE_HOOKS = {
    "electronics": [
        "⚡ {brand} {product} | سعر يكسر الدنيا 💥",
        "🔥 {product} من {brand} | صفقة العمر يا جماعة",
        "💻 {brand} {product} | تقنية عالمية بسعر محلي 👌",
        "📱 وصل حديثاً {brand} {product} | ما راح تندم",
        "⚡ جهاز {brand} {product} | فخامة وأداء",
    ],
    "fashion": [
        "👟 {brand} {product} | ستايلك بيصير مختلف 🔥",
        "✨ {product} من {brand} | أناقة ما تتفوت",
        "🔥 {brand} {product} | لبسة تفرق والله",
        "👌 وصل حديثاً {brand} {product} | طلّة فخمة",
        "💯 {product} من {brand} | كلاسيك وعصري",
    ],
    "beauty": [
        "💄 {brand} {product} | جمال بسعر خيالي",
        "✨ {product} من {brand} | بشرة flawless يا بنت",
        "🔥 {brand} {product} | العناية تستاهل والله",
        "🌟 وصل حديثاً {brand} {product} | إشراقة طبيعية",
        "💅 {product} من {brand} | فخامة في كل تفصيلة",
    ],
    "home": [
        "🏠 {product} من {brand} | بيتك يستاهل الأفضل",
        "✨ {brand} {product} | راحة بسعر معقول",
        "🔥 {product} | فرق واضح في بيتك",
        "🛋️ وصل حديثاً {brand} {product} | بيت أحلى",
        "👌 {product} من {brand} | جودة تثبت مع الوقت",
    ],
    "food": [
        "🍫 {brand} {product} | طعم يدمن والله",
        "🥤 {product} من {brand} | خزّن قبل يخلص",
        "🔥 {brand} {product} | جودة تستاهل يا جماعة",
        "🍯 وصل حديثاً {brand} {product} | أصلي وطبيعي",
        "☕ {product} من {brand} | يومك يبدا أحلى",
    ],
    "general": [
        "🔥 {brand} {product} | لقطة اليوم ما تتفوت",
        "💥 {product} من {brand} | سعر ما يتكرر والله",
        "⚡ {brand} {product} | فرصة لا تفوت",
        "👌 {product} | جودة عالية بسعر مناسب",
        "🌟 {brand} {product} | اختيارك الأفضل",
    ]
}

# ===================================
# 🎯 CTA سعودي خليجي
# ===================================
CTA_SMART = [
    "👉 اضغط واشتري الحين قبل ينتهي",
    "👉 السعر ما يطول - اضغط",
    "👉 الحق العرض قبل يخلص",
    "👉 خذها الآن ولا تنتظر",
    "👉 ما راح تندم - اضغط واشتري",
    "👉 فرصة ذهبية - لا تفوتها",
    "👉 اطلبها الحين واستمتع",
]

# ===================================
# 🔗 فك الروابط المختصرة (بدون تحويل الدومين)
# ===================================
def expand_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
        # ما نحولش الروابط الطويلة اللي هي أصلاً أمازون
        if "amazon.sa" in url or "amazon.com" in url:
            return url
            
        r = requests.get(url, allow_redirects=True, timeout=15, headers=headers)
        final_url = r.url
        
        # لو الرابط المفكوك فيه أمازون، رجعه زي ما هو
        if "amazon." in final_url:
            return final_url
        return None
    except Exception as e:
        print(f"Expand error: {e}")
        # لو فشل الفك، جرب الرابط الأصلي
        return url if "amazon." in url else None

# ===================================
# 🔧 أدوات
# ===================================
def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def clean_price(text):
    if not text:
        return None
    nums = re.findall(r'[\d,.]+', text)
    if nums:
        try:
            num = float(nums[0].replace(',', ''))
            return int(num)
        except:
            return None
    return None

def format_price(num):
    if num:
        return f"{num:,} ريال"
    return ""

# ===================================
# 🖼️ صورة HD فائقة الجودة (2000px)
# ===================================
def get_high_quality_image(soup):
    try:
        image = None
        
        # الطريقة 1: data-old-hires (أعلى جودة)
        img = soup.select_one("#landingImage")
        if img:
            image = img.get("data-old-hires")
        
        # الطريقة 2: data-a-dynamic-image (JSON مع أحجام متعددة)
        if not image and img:
            dynamic = img.get("data-a-dynamic-image")
            if dynamic:
                try:
                    data = json.loads(dynamic)
                    max_size = 0
                    for url, size in data.items():
                        area = size[0] * size[1]
                        if area > max_size:
                            max_size = area
                            image = url
                except:
                    pass
        
        # الطريقة 3: src attribute
        if not image and img:
            image = img.get("src")
        
        # الطريقة 4: صور البدائل
        if not image:
            for selector in ["#imgBlkFront", "#main-image", ".a-dynamic-image", "#ebooksImgBlkFront"]:
                img_alt = soup.select_one(selector)
                if img_alt:
                    image = img_alt.get("src") or img_alt.get("data-old-hires")
                    if image:
                        break
        
        # تحسين جودة الصورة إلى 2000px
        if image:
            image = re.sub(r'\._.*_\.', '.', image)
            if "_SL" in image:
                image = re.sub(r'_SL\d+_', '_SL2000_', image)
            else:
                image = image.replace(".jpg", "_SL2000_.jpg")
            return image
            
    except Exception as e:
        print(f"Image error: {e}")
    
    return None

# ===================================
# 📦 جلب المنتج - محسن للمنتجات المحمية
# ===================================
def fetch_product_page(asin, domain="amazon.sa"):
    url = f"https://{domain}/dp/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }
    
    try:
        # جرب أمازون سعودي أولاً
        r = requests.get(url, headers=headers, timeout=20)
        
        # لو محظور، جرب أمازون أمريكي
        if r.status_code in [503, 403, 429] or "To discuss automated access" in r.text:
            print("Blocked on SA, trying US...")
            url_us = f"https://amazon.com/dp/{asin}"
            r = requests.get(url_us, headers=headers, timeout=20)
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser"), "amazon.com"
        
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser"), domain
        
        return None, None
    except Exception as e:
        print(f"Fetch error: {e}")
        return None, None

def get_product(asin, original_url):
    # حدد الدومين من الرابط الأصلي
    domain = "amazon.sa"
    if "amazon.com" in original_url:
        domain = "amazon.com"
    
    soup, used_domain = fetch_product_page(asin, domain)
    if not soup:
        return None
    
    try:
        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")
        old_price = soup.select_one(".a-text-price .a-offscreen")
        image = get_high_quality_image(soup)
        
        # لو مفيش سعر، جرب selectors ثانية
        if not price:
            price = soup.select_one(".a-price-range .a-offscreen")
        if not price:
            price = soup.select_one("[data-a-color='price'] .a-offscreen")
        
        if not title:
            return None
            
        return {
            "title": title.text.strip(),
            "price": price.text.strip() if price else "غير متوفر",
            "old_price": old_price.text.strip() if old_price else None,
            "image": image,
            "domain": used_domain
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

# ===================================
# ✍️ توليد البوست السعودي الخليجي
# ===================================
def generate_post(product_data, url):
    title = product_data["title"]
    price_raw = product_data["price"]
    old_price_raw = product_data["old_price"]
    
    product_type, brand = detect_product_type(title)
    
    # نظف العنوان من اسم البراند لو موجود
    clean_title = title
    if brand:
        brand_lower = brand.lower()
        clean_title = re.sub(brand_lower, '', title, flags=re.IGNORECASE).strip()
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    
    # اختصر اسم المنتج
    product_name = clean_title[:45] if len(clean_title) > 45 else clean_title
    
    # البراند بالإنجلش
    brand_display = brand if brand else "ماركة مميزة"
    
    # اختر hook عشوائي
    hook_template = random.choice(STYLE_HOOKS.get(product_type, STYLE_HOOKS["general"]))
    hook = hook_template.format(brand=brand_display, product=product_name)
    
    # الأسعار
    current_num = clean_price(price_raw)
    old_num = clean_price(old_price_raw) if old_price_raw else None
    
    lines = []
    lines.append(hook)
    lines.append("")
    
    # عرض الأسعار مع الخصم
    if old_num and current_num and old_num > current_num:
        discount = int(((old_num - current_num) / old_num) * 100)
        if discount >= 10:
            lines.append(f"❌ ~~{format_price(old_num)}~~")
            lines.append(f"✅ {format_price(current_num)} 🔥 وفر {discount}%")
        else:
            lines.append(f"💰 السعر: {format_price(current_num)}")
    else:
        if current_num:
            lines.append(f"💰 السعر: {format_price(current_num)}")
        else:
            lines.append(f"💰 السعر: {price_raw}")
    
    lines.append("")
    lines.append(random.choice(CTA_SMART))
    lines.append(f"🔗 {url}")
    
    return "\n".join(lines)

# ===================================
# 🤖 البوت
# ===================================
@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)
    
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return

    for url in urls:
        # قبول كل روابط أمازون والأفلييت
        if not any(x in url for x in ["amzn.to", "amzn.", "amazon.", "amazon-"]):  # amazon- للأفلييت
            bot.reply_to(msg, "❌ الرابط لازم يكون من أمازون")
            continue
            
        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        expanded = expand_url(url)
        if not expanded:
            bot.edit_message_text("❌ ما قدرت أفك الرابط", msg.chat.id, wait.message_id)
            continue

        print(f"Working with: {expanded}")

        asin = extract_asin(expanded)
        if not asin:
            bot.edit_message_text("❌ ما لقيت كود المنتج", msg.chat.id, wait.message_id)
            continue

        print(f"ASIN: {asin}")

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_product, asin, expanded)
                product = future.result(timeout=25)
        except Exception as e:
            print(f"Error: {e}")
            product = None

        if not product:
            bot.edit_message_text("❌ فشل التحليل - جرب رابط ثاني", msg.chat.id, wait.message_id)
            continue

        print(f"Got product: {product['title'][:30]}")

        # استخدم الرابط الأصلي مش الرابط المفكوك عشان الأفلييت
        post = generate_post(product, expanded)

        # إرسال الصورة مع الكابشن
        try:
            if product["image"]:
                bot.send_photo(
                    chat_id=msg.chat.id,
                    photo=product["image"],
                    caption=post,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
            
        except Exception as e:
            print(f"Send error: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🔥 البوت شغال!")
bot.infinity_polling()
'''

# Verify no syntax errors
import ast
try:
    ast.parse(final_code)
    print("✅ No syntax errors!")
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")

# Save
with open('/mnt/kimi/output/amazon_bot_final_v3.py', 'w', encoding='utf-8') as f:
    f.write(final_code)

print("✅ تم حفظ الكود النهائي!")
print("📁 الملف: amazon_bot_final_v3.py")        "UNDER ARMOUR": ["under armour"],
        "PUMA": ["puma"],
        "REEBOK": ["reebok"],
        "ZARA": ["zara"],
        "H&M": ["h&m"],
        "SHEIN": ["shein"],
        "MAC": ["mac ", "m.a.c"],
        "MAYBELLINE": ["maybelline"],
        "LOREAL": ["l'oreal", "loreal"],
        "NESTLE": ["nestle"],
        "COCA COLA": ["coca cola", "cocacola"],
        "PEPSI": ["pepsi"],
        "STARBUCKS": ["starbucks"],
        "NESCAFE": ["nescafe"],
    }
    
    detected_brand = None
    for brand, keywords in brands.items():
        if any(k in t for k in keywords):
            detected_brand = brand
            break
    
    if any(x in t for x in ["iphone","samsung","headphone","earbuds","laptop","keyboard","mouse","usb","ipad","macbook","airpods","playstation","tv","tablet","charger","cable","monitor","camera","speaker"]):
        return "electronics", detected_brand
    if any(x in t for x in ["shirt","pants","dress","jacket","hoodie","shoes","t-shirt","jeans","sneakers","boots","sandals","watch","sunglasses","bag","wallet","belt","hat","cap"]):
        return "fashion", detected_brand
    if any(x in t for x in ["cream","serum","makeup","lipstick","lotion","perfume","fragrance","shampoo","conditioner","mask","foundation","mascara","eyeliner"]):
        return "beauty", detected_brand
    if any(x in t for x in ["pillow","blanket","kitchen","pan","mattress","sofa","vacuum","lamp","curtain","carpet","table","chair","organizer","storage"]):
        return "home", detected_brand
    if any(x in t for x in ["milk","coffee","tea","chocolate","snack","protein","vitamin","juice","water","honey","dates","nuts","rice","oil"]):
        return "food", detected_brand
    return "general", detected_brand

# ===================================
# 🇸🇦 Hooks سعودية خليجية أصيلة
# ===================================
STYLE_HOOKS = {
    "electronics": [
        "⚡ {brand} {product} | سعر يكسر الدنيا 💥",
        "🔥 {product} من {brand} | صفقة العمر يا جماعة",
        "💻 {brand} {product} | تقنية عالمية بسعر محلي 👌",
        "📱 يا هلا والله بـ {brand} {product} | ما راح تندم",
        "⚡ جهاز {brand} {product} | فخامة وأداء",
    ],
    "fashion": [
        "👟 {brand} {product} | ستايلك بيصير مختلف 🔥",
        "✨ {product} من {brand} | أناقة ما تتفوت",
        "🔥 {brand} {product} | لبسة تفرق والله",
        "👌 يا هلا بـ {brand} {product} | طلّة فخمة",
        "💯 {product} من {brand} | كلاسيك وعصري",
    ],
    "beauty": [
        "💄 {brand} {product} | جمال بسعر خيالي",
        "✨ {product} من {brand} | بشرة flawless يا بنت",
        "🔥 {brand} {product} | العناية تستاهل والله",
        "🌟 يا هلا بـ {brand} {product} | إشراقة طبيعية",
        "💅 {product} من {brand} | فخامة في كل تفصيلة",
    ],
    "home": [
        "🏠 {product} من {brand} | بيتك يستاهل الأفضل",
        "✨ {brand} {product} | راحة بسعر معقول",
        "🔥 {product} | فرق واضح في بيتك يا هلا",
        "🛋️ يا هلا بـ {brand} {product} | بيت أحلى",
        "👌 {product} من {brand} | جودة تثبت مع الوقت",
    ],
    "food": [
        "🍫 {brand} {product} | طعم يدمن والله",
        "🥤 {product} من {brand} | خزّن قبل يخلص",
        "🔥 {brand} {product} | جودة تستاهل يا جماعة",
        "🍯 يا هلا بـ {brand} {product} | أصلي وطبيعي",
        "☕ {product} من {brand} | يومك يبدا أحلى",
    ],
    "general": [
        "🔥 {brand} {product} | لقطة اليوم ما تتفوت",
        "💥 {product} من {brand} | سعر ما يتكرر والله",
        "⚡ {brand} {product} | فرصة لا تفوت يا هلا",
        "👌 {product} | جودة عالية بسعر مناسب",
        "🌟 {brand} {product} | اختيارك الأفضل",
    ]
}

# ===================================
# 🎯 CTA سعودي خليجي
# ===================================
CTA_SMART = [
    "👉 اضغط واشتري الحين قبل ينتهي",
    "👉 السعر ما يطول - اضغط يا هلا",
    "👉 الحق العرض قبل يخلص",
    "👉 خذها الآن ولا تنتظر",
    "👉 ما راح تندم - اضغط واشتري",
    "👉 فرصة ذهبية - لا تفوتها",
    "👉 اطلبها الحين واستمتع",
]

# ===================================
# 🔗 فك الروابط المختصرة
# ===================================
def expand_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, allow_redirects=True, timeout=10, headers=headers)
        final_url = r.url
        
        if "amazon." in final_url:
            final_url = re.sub(r'amazon\.[a-z.]+', 'amazon.sa', final_url)
            return final_url
        return None
    except Exception as e:
        print(f"Expand error: {e}")
        return None

# ===================================
# 🔧 أدوات
# ===================================
def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def clean_price(text):
    if not text:
        return None
    nums = re.findall(r'[\d,.]+', text)
    if nums:
        try:
            num = float(nums[0].replace(',', ''))
            return int(num)
        except:
            return None
    return None

def format_price(num):
    if num:
        return f"{num:,} ريال"
    return ""

# ===================================
# 🖼️ صورة HD فائقة الجودة (2000px)
# ===================================
def get_high_quality_image(soup):
    try:
        image = None
        
        # الطريقة 1: data-old-hires (أعلى جودة)
        img = soup.select_one("#landingImage")
        if img:
            image = img.get("data-old-hires")
        
        # الطريقة 2: data-a-dynamic-image (JSON مع أحجام متعددة)
        if not image and img:
            dynamic = img.get("data-a-dynamic-image")
            if dynamic:
                try:
                    data = json.loads(dynamic)
                    max_size = 0
                    for url, size in data.items():
                        area = size[0] * size[1]
                        if area > max_size:
                            max_size = area
                            image = url
                except:
                    pass
        
        # الطريقة 3: src attribute
        if not image and img:
            image = img.get("src")
        
        # الطريقة 4: صور البدائل
        if not image:
            for selector in ["#imgBlkFront", "#main-image", ".a-dynamic-image"]:
                img_alt = soup.select_one(selector)
                if img_alt:
                    image = img_alt.get("src") or img_alt.get("data-old-hires")
                    if image:
                        break
        
        # تحسين جودة الصورة إلى 2000px
        if image:
            image = re.sub(r'\._.*_\.', '.', image)
            if "_SL" in image:
                image = re.sub(r'_SL\d+_', '_SL2000_', image)
            else:
                image = image.replace(".jpg", "_SL2000_.jpg")
            return image
            
    except Exception as e:
        print(f"Image error: {e}")
    
    return None

# ===================================
# 📦 جلب المنتج
# ===================================
def fetch_product_page(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
        return None
    except Exception as e:
        print(f"Fetch error: {e}")
        return None

def get_product(asin):
    soup = fetch_product_page(asin)
    if not soup:
        return None
    
    try:
        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")
        old_price = soup.select_one(".a-text-price .a-offscreen")
        image = get_high_quality_image(soup)
        
        if not title or not price:
            return None
            
        return {
            "title": title.text.strip(),
            "price": price.text.strip(),
            "old_price": old_price.text.strip() if old_price else None,
            "image": image
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

# ===================================
# ✍️ توليد البوست السعودي الخليجي
# ===================================
def generate_post(product_data, url):
    title = product_data["title"]
    price_raw = product_data["price"]
    old_price_raw = product_data["old_price"]
    
    product_type, brand = detect_product_type(title)
    
    # نظف العنوان من اسم البراند لو موجود
    clean_title = title
    if brand:
        brand_lower = brand.lower()
        clean_title = re.sub(brand_lower, '', title, flags=re.IGNORECASE).strip()
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    
    # اختصر اسم المنتج
    product_name = clean_title[:45] if len(clean_title) > 45 else clean_title
    
    # البراند بالإنجلش
    brand_display = brand if brand else "ماركة مميزة"
    
    # اختر hook عشوائي
    hook_template = random.choice(STYLE_HOOKS.get(product_type, STYLE_HOOKS["general"]))
    hook = hook_template.format(brand=brand_display, product=product_name)
    
    # الأسعار
    current_num = clean_price(price_raw)
    old_num = clean_price(old_price_raw) if old_price_raw else None
    
    lines = []
    lines.append(hook)
    lines.append("")
    
    # عرض الأسعار مع الخصم
    if old_num and current_num and old_num > current_num:
        discount = int(((old_num - current_num) / old_num) * 100)
        if discount >= 10:
            lines.append(f"❌ ~~{format_price(old_num)}~~")
            lines.append(f"✅ {format_price(current_num)} 🔥 وفر {discount}% يا هلا")
        else:
            lines.append(f"💰 السعر: {format_price(current_num)}")
    else:
        lines.append(f"💰 السعر: {format_price(current_num)}")
    
    lines.append("")
    lines.append(random.choice(CTA_SMART))
    lines.append(f"🔗 الرابط: {url}")
    
    return "\n".join(lines)

# ===================================
# 🤖 البوت
# ===================================
@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)
    
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون (amzn.to أو amazon.sa)")
        return

    for url in urls:
        if not any(x in url for x in ["amzn.to", "amzn.", "amazon."]):
            bot.reply_to(msg, "❌ الرابط لازم يكون من أمازون يا هلا")
            continue
            
        wait = bot.reply_to(msg, "⏳ جاري فك الرابط والتحليل... يا هلا والله")

        expanded = expand_url(url)
        if not expanded:
            bot.edit_message_text("❌ ما قدرت أفك الرابط، جرب رابط طويل", msg.chat.id, wait.message_id)
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.edit_message_text("❌ ما لقيت كود المنتج في الرابط", msg.chat.id, wait.message_id)
            continue

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_product, asin)
                product = future.result(timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            product = None

        if not product:
            bot.edit_message_text("❌ فشل التحليل - المنتج محمي أو الرابط غلط", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, expanded)

        # إرسال الصورة مع الكابشن
        try:
            if product["image"]:
                bot.send_photo(
                    chat_id=msg.chat.id,
                    photo=product["image"],
                    caption=post,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
            
        except Exception as e:
            print(f"Send error: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🔥 البوت شغال - يا هلا والله!")
bot.infinity_polling()
