import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
import time
import subprocess
import tempfile
import os

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

class SmartGenerator:
    def __init__(self):
        self.brands = {
            "Apple": ["iphone", "ipad", "macbook", "airpods"],
            "Samsung": ["samsung", "galaxy"],
            "Sony": ["sony", "playstation"],
            "Nike": ["nike", "air max", "jordan"],
            "Adidas": ["adidas", "ultraboost"],
            "Chanel": ["chanel", "no.5"],
            "Dior": ["dior", "sauvage", "jadore"],
            "Gucci": ["gucci", "bloom"],
            "Zara": ["zara"],
            "H&M": ["h&m"],
            "Shein": ["shein"],
            "MAC": ["mac ", "lipstick"],
            "L'Oreal": ["l'oreal", "loreal"],
            "Maybelline": ["maybelline"],
            "Estee Lauder": ["estee lauder"],
            "Lancome": ["lancome"],
            "Timon": ["timon", "تمون"],
            "X Zone": ["x zone", "زي اكس زون", "اكس زون"],
            "Saudi": ["السعودي", "saudi", "السعودية"],
        }
        
        self.female_keywords = [
            "dress", "skirt", "blouse", "gown", "frock", "maxi", "midi", "mini",
            "abaya", "kaftan", "kimono", "robe", "nightgown", "lingerie", "bra", "panties",
            "tights", "leggings", "yoga pants", "palazzo", "saree", "lehenga",
            "heels", "high heels", "pumps", "stiletto", "wedges", "sandals women",
            "handbag", "purse", "clutch", "tote", "sling bag", "backpack women",
            "jewelry", "earrings", "necklace", "bracelet", "ring", "pendant",
            "gold", "diamond", "silver", "pear", "ruby", "emerald",
            "makeup", "lipstick", "lip gloss", "mascara", "eyeliner", "eyeshadow",
            "foundation", "concealer", "blush", "bronzer", "highlighter",
            "primer", "setting spray", "makeup remover",
            "skincare", "cream", "serum", "moisturizer", "toner", "cleanser",
            "face mask", "sheet mask", "eye cream", "anti-aging", "wrinkle",
            "perfume", "fragrance", "eau de parfum", "eau de toilette", "attar",
            "hair care", "shampoo", "conditioner", "hair mask", "hair oil",
            "nail polish", "manicure", "pedicure", "nail care",
            "hair dryer", "straightener", "curler", "curling iron", "hair brush",
            "makeup brushes", "beauty blender", "sponge", "tweezers", "razor women",
            "maternity", "pregnancy", "nursing", "breast pump", "diaper bag",
            "baby care", "stretch mark", "prenatal",
            "feminine wash", "intimate care", "sanitary", "menstrual", "period",
            "menopause", "fertility", "ovulation",
            "hijab", "scarf", "shawl", "headband", "hair clip", "hair band",
            "wig", "hair extension", "hair accessory",
            "sports bra", "yoga mat women", "fitness women", "gym wear women",
            "women", "woman", "lady", "ladies", "female", "girl", "girls",
            "for her", "hers", "she", "madam", "miss", "mrs", "ms",
        ]
        
        self.templates_female = [
            "{emoji} {product} من {brand}\n\n{price}\n{cta}",
            "{emoji} وصل حديثاً: {product} ✨\n\n{price}\n{cta}",
            "{emoji} يا هلا بالأناقة! {product}\n\n{price}\n{cta}",
            "{emoji} {product} 💕\n\n{price}\n{cta}",
            "{emoji} خصم حصري على {product}\n\n{price}\n{cta}",
            "{emoji} {product} بجودة عالية\n\n{price}\n{cta}",
            "{emoji} لا يفوتكِ: {product}\n\n{price}\n{cta}",
            "{emoji} {product} الأكثر مبيعاً 🔥\n\n{price}\n{cta}",
            "{emoji} عرض محدود ⏰ {product}\n\n{price}\n{cta}",
            "{emoji} الكمية محدودة! {product}\n\n{price}\n{cta}",
            "{emoji} ينتهي اليوم: {product}\n\n{price}\n{cta}",
            "{emoji} رشحنا لكِ: {product}\n\n{price}\n{cta}",
            "{emoji} الأفضل مبيعاً: {product}\n\n{price}\n{cta}",
            "{emoji} تجربة عملاء: {product}\n\n{price}\n{cta}",
            "{emoji} قبل ما ينتهي: {product}\n\n{price}\n{cta}",
            "{emoji} آخر فرصة! {product}\n\n{price}\n{cta}",
            "{emoji} نفذت الكمية قريباً: {product}\n\n{price}\n{cta}",
        ]
        
        self.templates_male = [
            "{emoji} {product} من {brand}\n\n{price}\n{cta}",
            "{emoji} وصل: {product} ⚡\n\n{price}\n{cta}",
            "{emoji} {product} بأفضل سعر\n\n{price}\n{cta}",
            "{emoji} {product} الأصلي\n\n{price}\n{cta}",
            "{emoji} عرض مميز: {product}\n\n{price}\n{cta}",
            "{emoji} {product} بجودة عالية\n\n{price}\n{cta}",
            "{emoji} لا يفوتك: {product}\n\n{price}\n{cta}",
            "{emoji} {product} الأكثر مبيعاً 🔥\n\n{price}\n{cta}",
            "{emoji} عرض محدود ⏰ {product}\n\n{price}\n{cta}",
            "{emoji} الكمية محدودة! {product}\n\n{price}\n{cta}",
            "{emoji} قبل ما ينتهي: {product}\n\n{price}\n{cta}",
        ]
        
        self.cta_female = [
            "👉 اشتري الآن",
            "👉 اضغطي للطلب",
            "👉 حصلي عليه",
            "👉 سارعي بالشراء",
            "👉 احجزي قبل ينتهي",
            "👉 اطلبي بسرعة",
            "👉 لا تفوتي الفرصة",
            "👉 تسوقي الآن",
        ]
        
        self.cta_male = [
            "👉 اشتري الآن",
            "👉 اضغط للطلب",
            "👉 احصل عليه",
            "👉 سارع بالشراء",
            "👉 احجز قبل ينتهي",
            "👉 اطلب بسرعة",
            "👉 لا تفوت الفرصة",
            "👉 تسوق الآن",
        ]
        
        self.emojis_female = ["💕", "✨", "🌸", "💎", "🦋", "🌺", "💖", "👜", "💄", "👗", "🛍️", "🎀"]
        self.emojis_male = ["💥", "⚡", "🔥", "📱", "💻", "🎧", "📸", "⌚", "🎯", "💪", "🛒", "🏆"]
    
    def is_female(self, title):
        t = title.lower()
        score = sum(2 if w in t else 0 for w in self.female_keywords)
        strong_female = ["dress", "skirt", "heels", "makeup", "lipstick", "perfume", "jewelry", "handbag", "lingerie", "maternity"]
        if any(w in t for w in strong_female):
            return True
        return score >= 2
    
    def get_brand(self, title):
        t = title.lower()
        for brand, keys in self.brands.items():
            if any(k in t for k in keys):
                return brand
        return None
    
    def clean_name(self, title, brand):
        name = title
        if brand:
            name = re.sub(brand, "", name, flags=re.IGNORECASE)
        
        junk = ["with", "and", "the", "for", "new", "original", "genuine", "official", 
                "men", "women", "man", "woman", "male", "female", "unisex"]
        for j in junk:
            name = re.sub(r"\b" + j + r"\b", "", name, flags=re.IGNORECASE)
        
        name = re.sub(r"\s+", " ", name).strip()
        words = name.split()
        return " ".join(words[:5]) if len(words) > 5 else name
    
    def format_price(self, price, old_price):
        if old_price and price:
            try:
                old = float(re.findall(r"[\d,.]+", old_price)[0].replace(",", ""))
                new = float(re.findall(r"[\d,.]+", price)[0].replace(",", ""))
                if old > new:
                    disc = int(((old - new) / old) * 100)
                    return f"~~{int(old):,}~~ ريال\n*{int(new):,}* ريال (-{disc}%) 🏷️"
            except:
                pass
        
        try:
            num = float(re.findall(r"[\d,.]+", price)[0].replace(",", ""))
            return f"*{int(num):,}* ريال 🏷️"
        except:
            return price
    
    def generate(self, title, price, old_price, original_url):
        is_female = self.is_female(title)
        brand = self.get_brand(title) or "ماركة مميزة"
        product = self.clean_name(title, brand)
        
        if is_female:
            emoji = random.choice(self.emojis_female)
            template = random.choice(self.templates_female)
            cta = random.choice(self.cta_female)
        else:
            emoji = random.choice(self.emojis_male)
            template = random.choice(self.templates_male)
            cta = random.choice(self.cta_male)
        
        price_str = self.format_price(price, old_price)
        
        post = template.format(
            emoji=emoji, brand=brand, product=product, 
            price=price_str, cta=cta
        )
        
        post += f"\n\n🔗 {original_url}"
        
        return post

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar-SA;q=0.8",
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
    }

def is_amazon_url(url):
    return any(p in url.lower() for p in ["amazon.", "amzn.to", "amzn.com"])

def expand_short_url(url):
    try:
        if "amzn.to" in url.lower():
            session = requests.Session()
            r = session.get(url, headers=get_random_headers(), allow_redirects=True, timeout=20)
            if "amazon." in r.url:
                return r.url
        return url
    except:
        return url

def extract_asin(url):
    for p in [r"/dp/([A-Z0-9]{10})", r"/gp/product/([A-Z0-9]{10})", r"/([A-Z0-9]{10})(?:[/?]|$)"]:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_high_quality_image(soup):
    try:
        img = soup.select_one("#landingImage")
        if img:
            url = img.get("data-old-hires")
            if url:
                return url
            
            dyn = img.get("data-a-dynamic-image")
            if dyn:
                try:
                    data = json.loads(dyn)
                    max_url = max(data.keys(), key=lambda x: data[x][0] * data[x][1] if isinstance(data[x], list) and len(data[x]) >= 2 else 0)
                    return max_url
                except:
                    pass
            
            url = img.get("src")
            if url:
                url = re.sub(r"\._.*_\.", ".", url)
                url = re.sub(r"_SL\d+_", "_SL1500_", url)
                return url
        
        alt_images = soup.select("#altImages img")
        for alt_img in alt_images:
            url = alt_img.get("src")
            if url and "images-na" in url:
                url = url.replace("_SS40_", "_SL1500_")
                return url
    except:
        pass
    return None

# ===== الطريقة 1: Google Cache =====
def get_from_google_cache(asin, domain):
    try:
        url = f"https://webcache.googleusercontent.com/search?q=cache:https://{domain}/dp/{asin}"
        headers = get_random_headers()
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200 and "amazon" in r.text.lower():
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            price = soup.select_one(".a-price .a-offscreen")
            
            if title:
                return {
                    "title": title.text.strip(),
                    "price": price.text.strip() if price else "غير متوفر",
                    "old_price": None,
                    "image": get_high_quality_image(soup)
                }
    except Exception as e:
        print(f"Google cache error: {e}")
    return None

# ===== الطريقة 2: textise dot iitty =====
def get_from_textise(asin, domain):
    try:
        url = f"https://r.jina.ai/http://{domain}/dp/{asin}"
        headers = get_random_headers()
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            text = r.text
            # jina.ai بيرجع نص مرتب، نحاول نستخرج منه
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if len(lines) >= 2:
                title = lines[0][:200]
                # البحث عن سعر في النص
                price_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:SAR|USD|\$|ريال)', text)
                price = price_match.group(1) + " ريال" if price_match else "غير متوفر"
                
                return {
                    "title": title,
                    "price": price,
                    "old_price": None,
                    "image": None
                }
    except Exception as e:
        print(f"Textise error: {e}")
    return None

# ===== الطريقة 3: curl impersonate (أقوى) =====
def get_with_curl(asin, domain):
    try:
        url = f"https://{domain}/dp/{asin}"
        
        # curl impersonate بيقلد Chrome بالضبط
        cmd = [
            "curl", "--silent", "--location",
            "--header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "--header", "Accept-Language: en-US,en;q=0.5",
            "--header", "Accept-Encoding: gzip, deflate, br",
            "--header", "DNT: 1",
            "--header", "Connection: keep-alive",
            "--header", "Upgrade-Insecure-Requests: 1",
            "--header", "Sec-Fetch-Dest: document",
            "--header", "Sec-Fetch-Mode: navigate",
            "--header", "Sec-Fetch-Site: none",
            "--header", "Sec-Fetch-User: ?1",
            "--compressed",
            "--max-time", "20",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and "productTitle" in result.stdout:
            soup = BeautifulSoup(result.stdout, "html.parser")
            title = soup.select_one("#productTitle")
            price = soup.select_one(".a-price .a-offscreen")
            old = soup.select_one(".a-text-price .a-offscreen")
            
            if title:
                return {
                    "title": title.text.strip(),
                    "price": price.text.strip() if price else "غير متوفر",
                    "old_price": old.text.strip() if old else None,
                    "image": get_high_quality_image(soup)
                }
    except Exception as e:
        print(f"Curl error: {e}")
    return None

# ===== الطريقة 4: Amazon Smile (أقل حماية) =====
def get_from_smile(asin, domain):
    try:
        smile_domain = "smile.amazon.com" if "amazon.com" in domain else "smile.amazon.sa"
        url = f"https://{smile_domain}/dp/{asin}"
        headers = get_random_headers()
        
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            price = soup.select_one(".a-price .a-offscreen")
            old = soup.select_one(".a-text-price .a-offscreen")
            
            if title:
                return {
                    "title": title.text.strip(),
                    "price": price.text.strip() if price else "غير متوفر",
                    "old_price": old.text.strip() if old else None,
                    "image": get_high_quality_image(soup)
                }
    except Exception as e:
        print(f"Smile error: {e}")
    return None

# ===== المحاولة المباشرة الأخيرة =====
def get_direct(asin, domain):
    try:
        url = f"https://{domain}/dp/{asin}"
        headers = get_random_headers()
        
        session = requests.Session()
        r = session.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            price = soup.select_one(".a-price .a-offscreen")
            old = soup.select_one(".a-text-price .a-offscreen")
            
            if title:
                return {
                    "title": title.text.strip(),
                    "price": price.text.strip() if price else "غير متوفر",
                    "old_price": old.text.strip() if old else None,
                    "image": get_high_quality_image(soup)
                }
    except Exception as e:
        print(f"Direct error: {e}")
    return None

# ===== الدالة الرئيسية =====
def get_product(asin, domain):
    methods = [
        ("Google Cache", get_from_google_cache),
        ("Textise", get_from_textise),
        ("Curl", get_with_curl),
        ("Amazon Smile", get_from_smile),
        ("Direct", get_direct),
    ]
    
    for name, method in methods:
        print(f"Trying {name}...")
        try:
            result = method(asin, domain)
            if result and result.get("title"):
                print(f"✅ {name} worked!")
                return result
        except Exception as e:
            print(f"❌ {name} failed: {e}")
        time.sleep(0.5)
    
    return None

gen = SmartGenerator()

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r"https?://\S+", msg.text)
    
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return
    
    for url in urls:
        if not is_amazon_url(url):
            continue
        
        wait = bot.reply_to(msg, "⏳ جاري جلب المنتج...")
        
        original_url = url
        expanded_url = expand_short_url(url)
        
        print(f"Original: {url}")
        print(f"Expanded: {expanded_url}")
        
        if expanded_url == url and "amzn.to" in url.lower():
            bot.edit_message_text("❌ فشل في توسيع الرابط المختصر.", msg.chat.id, wait.message_id)
            continue
        
        if "amazon." not in expanded_url:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue
        
        asin = extract_asin(expanded_url)
        if not asin:
            bot.edit_message_text("❌ لم يتم العثور على ASIN", msg.chat.id, wait.message_id)
            continue
        
        print(f"ASIN: {asin}")
        
        domain = "amazon.com" if "amazon.com" in expanded_url else "amazon.sa"
        
        prod = get_product(asin, domain)
        
        if not prod:
            bot.edit_message_text(
                "❌ فشل في جلب المنتج من كل المصادر.\n\n"
                "جرب:\n"
                "• تأكد أن الرابط شغال في المتصفح\n"
                "• جرب تبعت الرابط من أمازون مباشرة مش مختصر\n"
                "• لو المنتج محظور جغرافياً ممكن مينفعش", 
                msg.chat.id, wait.message_id
            )
            continue
        
        post = gen.generate(prod["title"], prod["price"], prod["old_price"], original_url)
        
        try:
            if prod["image"]:
                bot.send_photo(msg.chat.id, prod["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=False)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=False)
            try:
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                pass

print("🔥 البوت شغال!")
bot.infinity_polling()
