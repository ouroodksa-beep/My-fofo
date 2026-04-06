import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
import time
import subprocess

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# ===== قاموس ترجمة =====
TRANSLATIONS = {
    "serum": "سيروم", "eye": "عين", "collagen": "كولاجين", "vegan": "نباتي",
    "cream": "كريم", "lotion": "لوشن", "shampoo": "شامبو", "conditioner": "بلسم",
    "mask": "ماسك", "oil": "زيت", "gel": "جل", "spray": "بخاخ",
    "perfume": "عطر", "makeup": "ميك أب", "lipstick": "أحمر شفاه",
    "phone": "موبايل", "laptop": "لابتوب", "headphones": "سماعات",
    "watch": "ساعة", "shoes": "حذاء", "bag": "شنطة", "dress": "فستان",
    "skirt": "تنورة", "shirt": "قميص", "pants": "بنطلون", "jacket": "جاكيت",
    "sneakers": "حذاء رياضي", "heels": "كعب", "sandals": "صندل",
    "jewelry": "مجوهرات", "necklace": "عقد", "earrings": "حلق",
    "furniture": "أثاث", "kitchen": "مطبخ", "toys": "ألعاب",
    "new": "جديد", "original": "أصلي", "professional": "احترافي",
    "smart": "ذكي", "wireless": "لاسلكي", "waterproof": "مقاوم للماء",
    "black": "أسود", "white": "أبيض", "gold": "ذهبي", "silver": "فضي",
}

# ===== جمل افتتاحية سعودية =====
OPENING_LINES_FEMALE = [
    "مناسب للاستخدام اليومي بدون تعقيد 🏡",
    "لأنك تستحقين الأفضل دائماً 💎",
    "حل سحري لمظهر أكثر إشراقاً ✨",
    "سر جمالكِ في منتج واحد 🌸",
    "تجربة فاخرة بسعر ممتاز 👑",
    "منتج يستحق التجربة فعلاً 💕",
    "للمحافظة على جمالكِ الطبيعي 🦋",
    "اختياركِ الأمثل للعناية اليومية 🌺",
    "جودة عالية بتكلفة معقولة 💫",
    "بشرتكِ تستحق الأفضل دائماً ✨",
]

OPENING_LINES_MALE = [
    "مناسب للاستخدام اليومي بدون تعقيد 🏡",
    "اختيارك الذكي للعناية الشخصية 🎯",
    "جودة عالية بسعر ممتاز 💪",
    "منتج يستحق التجربة فعلاً 🔥",
    "للرجال اللي يقدرون الجودة ⚡",
    "أداء احترافي بتكلفة معقولة 🏆",
    "حل عملي لمظهر أكثر تميزاً 👔",
    "تصميم عملي وأنيق في نفس الوقت 🎩",
    "اختيارك الأمثل للاستخدام اليومي 🚀",
    "قيمة ممتازة مقابل السعر 👌",
]

OPENING_LINES_GENERAL = [
    "مناسب للاستخدام اليومي بدون تعقيد 🏡",
    "جودة ممتازة بسعر unbeatable ✨",
    "اختيارك الأمثل للعناية الشخصية 🎯",
    "منتج يستحق التجربة فعلاً 💎",
    "قيمة رائعة مقابل السعر 🔥",
    "تصميم عملي وأنيق في نفس الوقت 🌟",
    "لجميع أفراد العائلة 👨‍👩‍👧‍👦",
    "حل مثالي للاستخدام اليومي 💫",
    "جودة عالية بتكلفة معقولة 💪",
    "اختيار ذكي لميزانية محدودة 🏆",
]

class SmartGenerator:
    def __init__(self):
        self.brands = {
            "Apple": ["iphone", "ipad", "macbook", "airpods", "apple"],
            "Samsung": ["samsung", "galaxy"],
            "Sony": ["sony", "playstation", "wh-", "xm"],
            "Nike": ["nike", "air max", "jordan"],
            "Adidas": ["adidas", "ultraboost", "yeezy"],
            "Chanel": ["chanel", "no.5", "coco"],
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
            "The Ordinary": ["the ordinary"],
            "CeraVe": ["cerave"],
            "Neutrogena": ["neutrogena"],
            "Olay": ["olay"],
            "Nivea": ["nivea"],
            "L'Oreal Paris": ["l'oreal paris"],
            "Garnier": ["garnier"],
            "Pond's": ["pond's", "ponds"],
            "Vaseline": ["vaseline"],
            "Dove": ["dove"],
            "Lux": ["lux"],
            "Pampers": ["pampers"],
            "Huggies": ["huggies"],
            "Johnsons": ["johnson's", "johnsons"],
            "Philips": ["philips"],
            "Braun": ["braun"],
            "Oral-B": ["oral-b", "oralb"],
            "Colgate": ["colgate"],
            "Sensodyne": ["sensodyne"],
            "Signal": ["signal"],
            "Close Up": ["close up"],
            "Axe": ["axe"],
            "Old Spice": ["old spice"],
            "Adidas": ["adidas"],
            "Rexona": ["rexona"],
            "Nivea Men": ["nivea men"],
            "Gillette": ["gillette"],
            "Schick": ["schick"],
            "Veet": ["veet"],
            "X Zone": ["x zone", "اكس زون"],
            "Timon": ["timon", "تمون"],
            "Saudi": ["السعودي", "saudi"],
        }
        
        self.female_keywords = [
            "dress", "skirt", "blouse", "abaya", "kaftan", "robe", "lingerie",
            "heels", "pumps", "handbag", "purse", "clutch", "jewelry", "earrings",
            "necklace", "bracelet", "makeup", "lipstick", "mascara", "eyeliner",
            "foundation", "concealer", "blush", "perfume", "fragrance", "skincare",
            "cream", "serum", "moisturizer", "face mask", "hair care", "shampoo",
            "conditioner", "nail polish", "maternity", "women", "woman", "lady",
            "female", "girl", "for her", "hers", "she", "madam", "miss", "mrs",
        ]
    
    def is_female(self, title):
        t = title.lower()
        score = sum(2 if w in t else 0 for w in self.female_keywords)
        strong_female = ["dress", "skirt", "heels", "makeup", "lipstick", "perfume", "jewelry", "handbag", "lingerie"]
        if any(w in t for w in strong_female):
            return True
        return score >= 2
    
    def get_brand(self, title):
        t = title.lower()
        for brand, keys in self.brands.items():
            if any(k in t for k in keys):
                return brand
        return None
    
    def translate_product(self, title, brand):
        """يترجم اسم المنتج للعربي"""
        t = title.lower()
        
        # نشيل البراند
        if brand:
            t = re.sub(brand, "", t, flags=re.IGNORECASE)
        
        # نشيل الكلمات الزايدة
        junk = ["with", "and", "the", "for", "new", "original", "genuine", "official",
                "men", "women", "man", "woman", "male", "female", "unisex", "edition",
                "version", "model", "series", "pack", "set", "kit", "bundle", "ml", "g",
                "all", "types", "skin", "hair", "types", "suitable", "for"]
        for j in junk:
            t = re.sub(r"\b" + j + r"\b", "", t, flags=re.IGNORECASE)
        
        # نترجم الكلمات
        words = t.split()
        translated = []
        
        for word in words:
            clean = re.sub(r'[^\w]', '', word.lower())
            if clean in TRANSLATIONS:
                translated.append(TRANSLATIONS[clean])
            elif any(char.isdigit() for char in clean):
                translated.append(word)
        
        if not translated:
            # نرجع أول 4 كلمات مفيدة من العنوان
            clean_words = [w for w in title.split() if len(w) > 2]
            if brand:
                clean_words = [w for w in clean_words if brand.lower() not in w.lower()]
            return " ".join(clean_words[:4]) if clean_words else title
        
        return " ".join(translated[:5])
    
    def format_price(self, price, old_price):
        """تنسيق السعر بالطريقة السعودية"""
        # نستخرج الأرقام والعملة
        def extract_price(text):
            nums = re.findall(r"[\d,.]+", text)
            currency = "ريال" if "sar" in text.lower() or "ريال" in text else "$"
            if nums:
                try:
                    val = float(nums[0].replace(",", ""))
                    return int(val), currency
                except:
                    pass
            return None, "ريال"
        
        current_val, curr = extract_price(price)
        old_val, _ = extract_price(old_price) if old_price else (None, curr)
        
        if old_val and current_val and old_val > current_val:
            discount = int(((old_val - current_val) / old_val) * 100)
            return f"❌ قبل: {old_val:,} {curr} سعودي\n✅ الآن: {current_val:,} {curr} سعودي (وفر {discount}%)"
        
        return f"✅ السعر: {current_val:,} {curr} سعودي" if current_val else f"✅ {price}"
    
    def generate(self, title, price, old_price, original_url):
        is_female = self.is_female(title)
        brand = self.get_brand(title)
        
        # نختار الجملة الافتتاحية
        if is_female:
            opening = random.choice(OPENING_LINES_FEMALE)
        else:
            opening = random.choice(OPENING_LINES_MALE)
        
        # نترجم اسم المنتج
        product_ar = self.translate_product(title, brand)
        
        # نبني السطر الأول (الجملة + المنتج)
        if brand:
            line1 = f"{opening}\n\n🛒 {product_ar} {brand}"
        else:
            line1 = f"{opening}\n\n🛒 {product_ar}"
        
        # السطر الثاني (السعر)
        line2 = self.format_price(price, old_price)
        
        # البوست النهائي
        post = f"{line1}\n\n{line2}\n\n🔗 {original_url}"
        
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

def get_from_google_cache(asin, domain):
    try:
        url = f"https://webcache.googleusercontent.com/search?q=cache:https://{domain}/dp/{asin}"
        headers = get_random_headers()
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200 and "amazon" in r.text.lower():
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
        print(f"Google cache error: {e}")
    return None

def get_from_textise(asin, domain):
    try:
        url = f"https://r.jina.ai/http://{domain}/dp/{asin}"
        headers = get_random_headers()
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            text = r.text
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if len(lines) >= 2:
                title = lines[0][:200]
                # البحث عن سعرين (قديم وجديد)
                prices = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:SAR|USD|\$|ريال)', text)
                current_price = prices[0] + " ريال" if prices else "غير متوفر"
                old_price = prices[1] + " ريال" if len(prices) > 1 else None
                
                return {
                    "title": title,
                    "price": current_price,
                    "old_price": old_price,
                    "image": None
                }
    except Exception as e:
        print(f"Textise error: {e}")
    return None

def get_with_curl(asin, domain):
    try:
        url = f"https://{domain}/dp/{asin}"
        cmd = [
            "curl", "--silent", "--location",
            "--header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "--header", "Accept-Language: en-US,en;q=0.5",
            "--header", "Accept-Encoding: gzip, deflate, br",
            "--header", "DNT: 1",
            "--header", "Connection: keep-alive",
            "--header", "Upgrade-Insecure-Requests: 1",
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
                "❌ فشل في جلب المنتج.\n\n"
                "جرب تبعت الرابط من أمازون مباشرة", 
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
