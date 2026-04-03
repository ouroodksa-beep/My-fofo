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
# 🧠 AI: تحليل المنتج وتوليد هوك ذكي
# ===================================
class AIHookGenerator:
    def __init__(self):
        # قاعدة بيانات الميزات حسب الفئة
        self.features_db = {
            "electronics": {
                "keywords": ["iphone", "samsung", "laptop", "tablet", "airpods", "headphone", "charger", "cable", "camera", "smartwatch"],
                "benefits": ["سرعة", "أداء", "جودة", "تقنية", "تصميم", "بطارية", "شاشة", "كاميرا"],
                "emotions": ["💥", "⚡", "🔥", "📱", "💻", "🎧", "📸", "⌚"],
                "templates": [
                    "{emoji} {product} | {benefit} ياخذ العقل",
                    "{emoji} جهاز {brand} {product} | {benefit} خرافي",
                    "{emoji} {product} من {brand} | {benefit} بمعنى الكلمة",
                    "{emoji} وصل {product} | {benefit} يفرق",
                    "{emoji} {brand} {product} | كل {benefit} في جهاز واحد",
                ]
            },
            "fashion": {
                "keywords": ["shirt", "shoes", "watch", "bag", "jacket", "jeans", "sneakers", "dress", "sunglasses"],
                "benefits": ["أناقة", "راحة", "جودة", "خامة", "ستايل", "فخامة", "تصميم", "طلّة"],
                "emotions": ["👌", "✨", "🔥", "👟", "👔", "🕶️", "👜", "💎"],
                "templates": [
                    "{emoji} {product} من {brand} | {benefit} ما تتفوت",
                    "{emoji} {brand} {product} | {benefit} يتكلم عن نفسه",
                    "{emoji} وصل {product} | {benefit} فاخر",
                    "{emoji} {product} | {benefit} يفرق في كل مكان",
                    "{emoji} {brand} {product} | {benefit} عالي واضح",
                ]
            },
            "beauty": {
                "keywords": ["cream", "serum", "makeup", "lipstick", "perfume", "shampoo", "mask", "foundation"],
                "benefits": ["إشراقة", "نعومة", "نتيجة", "رائحة", "عناية", "جمال", "نضارة", "حماية"],
                "emotions": ["💄", "✨", "🌟", "💅", "🌸", "💎", "🧴", "🌺"],
                "templates": [
                    "{emoji} {product} من {brand} | {benefit} فورية",
                    "{emoji} {brand} {product} | {benefit} تلاحظينها من أول استخدام",
                    "{emoji} سر {benefit} | {product} الأصلي",
                    "{emoji} {product} | {benefit} طبيعية",
                    "{emoji} وصل {brand} {product} | {benefit} ما لها مثيل",
                ]
            },
            "home": {
                "keywords": ["pillow", "mattress", "lamp", "kitchen", "sofa", "vacuum", "organizer", "blanket"],
                "benefits": ["راحة", "جودة", "متانة", "تنظيم", "دفء", "إضاءة", "مساحة", "هدوء"],
                "emotions": ["🏠", "✨", "🛋️", "🛏️", "💡", "🔥", "👌", "🧹"],
                "templates": [
                    "{emoji} {product} من {brand} | بيتك يستاهل {benefit}",
                    "{emoji} {brand} {product} | {benefit} تستمر سنين",
                    "{emoji} فرق في {benefit} | {product} فاخر",
                    "{emoji} {product} | {benefit} بمعايير عالية",
                    "{emoji} وصل {product} | {benefit} يحسّن يومك",
                ]
            },
            "food": {
                "keywords": ["coffee", "chocolate", "honey", "dates", "nuts", "tea", "protein", "vitamin"],
                "benefits": ["طعم", "جودة", "صحة", "طاقة", "فائدة", "نكهة", "أصالة", "انتعاش"],
                "emotions": ["☕", "🍫", "🍯", "🌴", "🥜", "🍵", "💪", "✨"],
                "templates": [
                    "{emoji} {product} من {brand} | {benefit} يدمن",
                    "{emoji} {brand} {product} | {benefit} أصلية",
                    "{emoji} تجربة {benefit} | {product} مميز",
                    "{emoji} {product} | {benefit} تستاهل التجربة",
                    "{emoji} وصل {product} | {benefit} من أول لقمة",
                ]
            }
        }
        
        # براندات معروفة
        self.brands = {
            "APPLE": ["iphone", "ipad", "macbook", "airpods", "apple watch"],
            "SAMSUNG": ["samsung", "galaxy"],
            "SONY": ["sony", "playstation", "wh-1000"],
            "NIKE": ["nike", "air max", "jordan"],
            "ADIDAS": ["adidas", "ultraboost", "yeezy"],
            "HUAWEI": ["huawei", "mate", "p40", "p50"],
            "XIAOMI": ["xiaomi", "mi ", "redmi", "poco"],
            "LENOVO": ["lenovo", "thinkpad", "yoga"],
            "DELL": ["dell", "xps", "alienware"],
            "HP": ["hp ", "pavilion", "omen"],
            "LG": ["lg ", "oled", "gram"],
            "PHILIPS": ["philips", "hue"],
            "BOSE": ["bose", "quietcomfort", "soundlink"],
            "BEATS": ["beats", "studio", "solo"],
            "RAY-BAN": ["ray-ban", "rayban", "aviator"],
            "CHANEL": ["chanel", "no.5", "coco"],
            "DIOR": ["dior", "sauvage", "jadore"],
            "GUCCI": ["gucci", "bloom", "guilty"],
            "PRADA": ["prada", "luna rossa"],
            "UNDER ARMOUR": ["under armour", "ua ", "curry"],
            "PUMA": ["puma", "rs-x"],
            "REEBOK": ["reebok", "nano"],
            "ZARA": ["zara"],
            "H&M": ["h&m"],
            "SHEIN": ["shein"],
            "MAC": ["mac ", "m.a.c", "lipstick"],
            "MAYBELLINE": ["maybelline", "fit me"],
            "LOREAL": ["l'oreal", "loreal", "paris"],
            "NESTLE": ["nestle", "nespresso"],
            "STARBUCKS": ["starbucks", "via"],
            "NESCAFE": ["nescafe", "dolce gusto"],
            "COCA COLA": ["coca cola", "cocacola"],
            "PEPSI": ["pepsi"],
        }
    
    def detect_brand(self, title):
        t = title.lower()
        for brand, keywords in self.brands.items():
            if any(k in t for k in keywords):
                return brand
        return None
    
    def detect_category(self, title):
        t = title.lower()
        for cat, data in self.features_db.items():
            if any(k in t for k in data["keywords"]):
                return cat
        return "general"
    
    def extract_product_name(self, title, brand):
        # شيل البراند من العنوان
        clean = title
        if brand:
            brand_clean = brand.replace(" ", "")
            clean = re.sub(brand, '', clean, flags=re.IGNORECASE)
            clean = re.sub(brand_clean, '', clean, flags=re.IGNORECASE)
        
        # شيل الكلمات الزائدة
        noise = ["with", "and", "the", "for", "in", "of", "new", "original", "genuine", "official"]
        for n in noise:
            clean = re.sub(r'\b' + n + r'\b', '', clean, flags=re.IGNORECASE)
        
        # نظف
        clean = re.sub(r'\s+', ' ', clean).strip()
        clean = re.sub(r'[^\w\s\-]', '', clean)
        
        # اختصر
        words = clean.split()
        if len(words) > 6:
            clean = ' '.join(words[:6])
        
        return clean.strip()
    
    def generate_hook(self, title):
        brand = self.detect_brand(title)
        category = self.detect_category(title)
        product_name = self.extract_product_name(title, brand)
        
        if category in self.features_db:
            data = self.features_db[category]
        else:
            data = {
                "benefits": ["جودة", "قيمة", "تميز", "فخامة"],
                "emotions": ["🔥", "✨", "💎", "👌", "⚡"],
                "templates": [
                    "{emoji} {product} من {brand} | {benefit} واضح",
                    "{emoji} {brand} {product} | {benefit} يستاهل",
                    "{emoji} وصل {product} | {benefit} فاخر",
                    "{emoji} {product} | {benefit} ما يتفوت",
                    "{emoji} {brand} {product} | {benefit} عالي",
                ]
            }
        
        # اختر عشوائياً
        emoji = random.choice(data["emotions"])
        benefit = random.choice(data["benefits"])
        template = random.choice(data["templates"])
        
        brand_display = brand if brand else "ماركة مميزة"
        
        hook = template.format(
            emoji=emoji,
            brand=brand_display,
            product=product_name,
            benefit=benefit
        )
        
        return hook, brand

# ===================================
# 🎯 CTA ذكي
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
# ✍️ توليد البوست بالهوك الذكي AI
# ===================================
def generate_post(product_data, url, ai_generator):
    title = product_data["title"]
    price_raw = product_data["price"]
    old_price_raw = product_data["old_price"]

    # AI Generated Hook!
    hook, brand = ai_generator.generate_hook(title)

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
# إنشاء مولد الهوك الذكي
ai_hook_gen = AIHookGenerator()

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return

    for url in urls:
        # قبول كل روابط أمازون والأفلييت
        if not any(x in url for x in ["amzn.to", "amzn.", "amazon.", "amazon-"]):
            bot.reply_to(msg, "❌ الرابط لازم يكون من أمازون")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل الذكي...")

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

        # AI Generated Post!
        post = generate_post(product, expanded, ai_hook_gen)

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

print("🔥 البوت شغال - AI Hooks Enabled!")
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
with open('/mnt/kimi/output/amazon_bot_ai_hooks.py', 'w', encoding='utf-8') as f:
    f.write(final_code)

print("✅ تم حفظ الكود مع AI Hooks!")
print("📁 الملف: amazon_bot_ai_hooks.py")
