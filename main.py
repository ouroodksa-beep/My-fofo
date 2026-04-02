import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
from concurrent.futures import ThreadPoolExecutor

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🧠 تحديد نوع المنتج والبراند
# ===================================
def detect_product_type(title):
    t = title.lower()
    brands = {
        "apple": ["iphone", "ipad", "macbook", "airpods", "apple"],
        "samsung": ["samsung", "galaxy"],
        "sony": ["sony", "playstation"],
        "nike": ["nike"],
        "adidas": ["adidas"]
    }
    
    detected_brand = None
    for brand, keywords in brands.items():
        if any(k in t for k in keywords):
            detected_brand = brand.upper()
            break
    
    if any(x in t for x in ["iphone","samsung","headphone","earbuds","laptop","keyboard","mouse","usb","ipad","macbook","airpods","playstation"]):
        return "electronics", detected_brand
    if any(x in t for x in ["shirt","pants","dress","jacket","hoodie","shoes","nike","adidas","watch","sunglasses"]):
        return "fashion", detected_brand
    if any(x in t for x in ["cream","serum","makeup","lipstick","lotion","perfume","fragrance"]):
        return "beauty", detected_brand
    if any(x in t for x in ["pillow","blanket","kitchen","pan","mattress","sofa","vacuum","lamp"]):
        return "home", detected_brand
    if any(x in t for x in ["milk","coffee","tea","chocolate","snack","protein","vitamin"]):
        return "food", detected_brand
    return "general", detected_brand

# ===================================
# 🇸🇦 Hooks ذكية ومختصرة
# ===================================
STYLE_HOOKS = {
    "electronics": [
        "⚡ {brand} {product} | سعر يكسر الدنيا",
        "🔥 {product} من {brand} | صفقة العمر",
        "💻 {brand} {product} | تكنولوجيا بسعر جنوني",
    ],
    "fashion": [
        "👟 {brand} {product} | ستايلك بيصير مختلف",
        "✨ {product} من {brand} | أناقة ما تتفوت",
        "🔥 {brand} {product} | لبسة تفرق",
    ],
    "beauty": [
        "💄 {brand} {product} | جمال بسعر خيالي",
        "✨ {product} من {brand} | بشرة flawless",
        "🔥 {brand} {product} | العناية تستاهل",
    ],
    "home": [
        "🏠 {product} من {brand} | بيتك يستاهل الأفضل",
        "✨ {brand} {product} | راحة بسعر معقول",
        "🔥 {product} | فرق واضح في بيتك",
    ],
    "food": [
        "🍫 {brand} {product} | طعم يدمن",
        "🥤 {product} من {brand} | خزن قبل يخلص",
        "🔥 {brand} {product} | جودة تستاهل",
    ],
    "general": [
        "🔥 {brand} {product} | لقطة اليوم",
        "💥 {product} من {brand} | سعر ما يتكرر",
        "⚡ {brand} {product} | فرصة لا تفوت",
    ]
}

# ===================================
# 🎯 CTA ذكي
# ===================================
CTA_SMART = [
    "👉 اضغط واشتري الحين",
    "👉 السعر ما يطول - اضغط",
    "👉 الحق العرض قبل ينتهي",
    "👉 خذها الآن - لا تنتظر",
]

# ===================================
# 🔗 فك الروابط المختصرة (amzn.to + amzn)
# ===================================
def expand_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, allow_redirects=True, timeout=10, headers=headers)
        final_url = r.url
        
        if "amazon." in final_url:
            final_url = re.sub(r'amazon\.[a-z\.]+', 'amazon.sa', final_url)
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
# 🖼️ صورة HD - محسنة
# ===================================
def get_high_quality_image(soup):
    try:
        # جرب كل الطرق الممكنة للصورة
        selectors = [
            "#landingImage",
            "#imgBlkFront",
            ".a-dynamic-image",
            ".a-stretch-horizontal img",
            "#main-image"
        ]
        
        image = None
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img:
                # جرب data-old-hires
                image = img.get("data-old-hires")
                if image:
                    break
                    
                # جرب data-a-dynamic-image
                dynamic = img.get("data-a-dynamic-image")
                if dynamic:
                    try:
                        data = json.loads(dynamic)
                        image = max(data.keys(), key=lambda x: data[x][0] * data[x][1])
                        break
                    except:
                        pass
                
                # جرب src
                image = img.get("src")
                if image and "images-amazon" in image:
                    break
        
        if image:
            # نظف وكبر الصورة
            image = re.sub(r'\._.*_\.', '.', image)
            if "_SL" not in image:
                image = image.replace(".jpg", "_SL1500_.jpg")
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
# ✍️ توليد البوست الذكي
# ===================================
def generate_post(product_data, url):
    title = product_data["title"]
    price_raw = product_data["price"]
    old_price_raw = product_data["old_price"]
    
    product_type, brand = detect_product_type(title)
    
    clean_title = title
    if brand and brand.lower() in title.lower():
        clean_title = re.sub(brand, '', title, flags=re.IGNORECASE).strip()
    
    product_name = clean_title[:50] if len(clean_title) > 50 else clean_title
    brand_display = brand if brand else "ماركة مميزة"
    
    hook_template = random.choice(STYLE_HOOKS.get(product_type, STYLE_HOOKS["general"]))
    hook = hook_template.format(brand=brand_display, product=product_name)
    
    current_num = clean_price(price_raw)
    old_num = clean_price(old_price_raw) if old_price_raw else None
    
    lines = []
    lines.append(hook)
    lines.append("")
    
    if old_num and current_num and old_num > current_num:
        discount = int(((old_num - current_num) / old_num) * 100)
        if discount >= 10:
            lines.append(f"❌ ~~{format_price(old_num)}~~")
            lines.append(f"✅ {format_price(current_num)} 🔥 وفر {discount}%")
        else:
            lines.append(f"💰 {format_price(current_num)}")
    else:
        lines.append(f"💰 {format_price(current_num)}")
    
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
        bot.reply_to(msg, "❌ ارسل رابط أمازون (amzn.to أو amazon.sa)")
        return

    for url in urls:
        if not any(x in url for x in ["amzn.to", "amzn.", "amazon."]):
            bot.reply_to(msg, "❌ الرابط لازم يكون من أمازون")
            continue
            
        wait = bot.reply_to(msg, "⏳ جاري فك الرابط والتحليل...")

        expanded = expand_url(url)
        if not expanded:
            bot.edit_message_text("❌ ما قدرت أفك الرابط، جرب رابط طويل", msg.chat.id, wait.message_id)
            continue

        print(f"Expanded: {expanded}")

        asin = extract_asin(expanded)
        if not asin:
            bot.edit_message_text("❌ ما لقيت كود المنتج في الرابط", msg.chat.id, wait.message_id)
            continue

        print(f"ASIN: {asin}")

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

        print(f"Product: {product['title'][:30]}")
        print(f"Image found: {product['image'] is not None}")

        post = generate_post(product, expanded)

        # ✅ إرسال الصورة مع الكابشن (النص)
        try:
            if product["image"]:
                bot.send_photo(
                    chat_id=msg.chat.id,
                    photo=product["image"],
                    caption=post,
                    parse_mode="Markdown"  # عشان يشتغل ~~الخط المشطوب~~
                )
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
            
        except Exception as e:
            print(f"Send error: {e}")
            # لو فشلت الصورة، ارسل نص بس
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🔥 البوت شغال - يقبل amzn.to و amazon.sa")
bot.infinity_polling()
    "fashion": [
        ("✨ ستايل جديد على", "أناقة بسعر رهيب 😎"),
        ("🔥 عرض أزياء على", "لبسك بيصير مختلف 👌"),
    ],
    "beauty": [
        ("💄 عرض جمال على", "اهتمي بنفسك ✨"),
        ("✨ منتج عناية على", "نتيجته واضحة 🔥"),
    ],
    "home": [
        ("🏠 عرض للبيت على", "راحة وجودة 👌"),
        ("✨ منتج منزلي", "فرق واضح 💯"),
    ],
    "food": [
        ("🥤 عرض غذائي على", "طعم رهيب 😋"),
        ("🍫 لقطة على", "خزن قبل يخلص 🔥"),
    ],
    "general": [
        ("🔥 عرض قوي على", "سعر ما يتكرر 🔥"),
        ("💥 لقطة اليوم على", "فرصة لا تفوت 👌"),
    ]
}

# ===================================
# 🎯 CTA ذكي
# ===================================
CTA_SMART = [
    "👉 الحق العرض",
    "👉 خذها قبل تخلص",
    "👉 اطلبه الحين",
    "👉 لا يفوتك",
    "👉 إذا ناوي هذا وقتك",
    "👉 السعر ما يطول",
]

# ===================================
# 🔗 فك الروابط المختصرة
# ===================================
def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=5)
        return r.url
    except:
        return url

# ===================================
# 🔧 أدوات
# ===================================
def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})'
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
            return f"{int(num)} ريال"
        except:
            return text
    return text

# ===================================
# 🖼️ صورة HD
# ===================================
def get_high_quality_image(soup):
    img = soup.select_one("#landingImage")
    if not img:
        return None
    image = img.get("data-old-hires")
    if not image:
        dynamic = img.get("data-a-dynamic-image")
        if dynamic:
            try:
                data = json.loads(dynamic)
                image = max(data.keys(), key=lambda x: data[x][0] * data[x][1])
            except:
                pass
    if not image:
        image = img.get("src")
    if image:
        image = re.sub(r'\._.*_\.', '.', image)
        if "_SL" not in image:
            image = image.replace(".jpg", "_SL1500_.jpg")
    return image

# ===================================
# 📦 جلب المنتج
# ===================================
def fetch_product_page(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
        return None
    except Exception as e:
        print(f"Error fetching: {e}")
        return None

def get_product(asin):
    soup = fetch_product_page(asin)
    if not soup:
        return None
    
    title = soup.select_one("#productTitle")
    price = soup.select_one(".a-price .a-offscreen")
    old_price = soup.select_one(".a-text-price .a-offscreen")
    image = get_high_quality_image(soup)
    
    if not title or not price:
        return None
        
    return (
        title.text.strip(),
        price.text.strip(),
        old_price.text.strip() if old_price else None,
        image
    )

# ===================================
# ✍️ توليد البوست - التنسيق الجديد
# ===================================
def generate_post(title, price, old_price, url):
    product_type = detect_product_type(title)
    hook1, hook2 = random.choice(STYLE_HOOKS.get(product_type, STYLE_HOOKS["general"]))
    
    # اسم المنتج مختصر
    product_name = title[:55] if len(title) > 55 else title
    
    lines = []
    # السطر الأول: الهوك + اسم المنتج
    lines.append(f"{hook1} {product_name}")
    lines.append("")  # سطر فاضي
    
    # السطر الثاني: الهوك الثاني
    lines.append(hook2)
    lines.append("")  # سطر فاضي

    # السعر
    current = clean_price(price)
    old = clean_price(old_price) if old_price else None

    if old:
        try:
            old_n = float(re.findall(r'[\d.]+', old)[0])
            new_n = float(re.findall(r'[\d.]+', current)[0])
            if old_n > new_n:
                discount = int(((old_n - new_n) / old_n) * 100)
                if discount >= 10:
                    lines.append(f"❌ {old}")
                    lines.append(f"✅ {current} 🔥")
                else:
                    lines.append(f"💰 {current}")
            else:
                lines.append(f"💰 {current}")
        except:
            lines.append(f"💰 {current}")
    else:
        lines.append(f"💰 {current}")
    
    lines.append("")  # سطر فاضي

    # CTA + الرابط
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
        bot.reply_to(msg, "❌ ارسل رابط امازون")
        return

    for short_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        expanded = expand_url(short_url)
        if "amazon.sa" not in expanded:
            bot.edit_message_text("❌ الرابط لازم يكون من amazon.sa", msg.chat.id, wait.message_id)
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.edit_message_text("❌ ما قدرت أقرأ كود المنتج (ASIN)", msg.chat.id, wait.message_id)
            continue

        print(f"Processing ASIN: {asin}")
        
        # ⚡ تحسين الأداء
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(get_product, asin)
            try:
                product = future.result(timeout=15)
            except Exception as e:
                print(f"Timeout error: {e}")
                product = None

        if not product:
            bot.edit_message_text("❌ فشل التحليل - جرب رابط ثاني", msg.chat.id, wait.message_id)
            continue

        title, price, old_price, image = product
        print(f"Got product: {title[:30]}...")
        
        post = generate_post(title, price, old_price, expanded)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            bot.edit_message_text(f"❌ خطأ في الإرسال: {str(e)}", msg.chat.id, wait.message_id)

print("🔥 البوت شغال - جرب ارسل رابط امازون")
bot.infinity_polling()
# ===================================
def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    return None

# ===================================
# 📦 جلب المنتج (قوي)
# ===================================
def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    try:
        r = scraper.get(url, timeout=7)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")

        if not title or not price:
            print("❌ Amazon Blocked")
            return None

        image = soup.select_one("#landingImage")
        image_url = image.get("src") if image else None

        return (
            title.text.strip(),
            price.text.strip(),
            image_url
        )

    except Exception as e:
        print("ERROR:", e)
        return None

# ===================================
# ✍️ بوست
# ===================================
def generate_post(title, price, url):
    product_name = title[:60]

    text = f"""🔥 عرض على {product_name}

{product_name}

💰 {price}

{random.choice(CTA)}

🔗 {url}
"""
    return text

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

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        if "amazon.sa" not in url:
            bot.edit_message_text("❌ الرابط لازم يكون amazon.sa", msg.chat.id, wait.message_id)
            continue

        asin = extract_asin(url)

        if not asin:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue

        product = get_product(asin)

        # 💥 fallback مهم
        if not product:
            bot.send_message(msg.chat.id, f"""🔥 المنتج موجود هنا 👇

🔗 {url}

(تعذر تحليل التفاصيل 😅)
""")
            bot.delete_message(msg.chat.id, wait.message_id)
            continue

        title, price, image = product

        post = generate_post(title, price, url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
        except:
            bot.send_message(msg.chat.id, post)

        bot.delete_message(msg.chat.id, wait.message_id)

print("🔥 BOT READY (FAST + BYPASS AMAZON)")
bot.infinity_polling()
