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

# ===== قاموس ترجمة بسيط للكلمات الشائعة =====
TRANSLATIONS = {
    # الملابس
    "dress": "فستان", "skirt": "تنورة", "blouse": "بلوزة", "shirt": "قميص",
    "pants": "بنطلون", "jeans": "جينز", "jacket": "جاكيت", "coat": "معطف",
    "sweater": "كنزة", "hoodie": "هودي", "t-shirt": "تيشيرت", "shorts": "شورت",
    "leggings": "ليقنز", "abaya": "عباية", "kaftan": "قفطان", "robe": "روب",
    "suit": "بدلة", "uniform": "زي", "sportswear": "ملابس رياضية",
    
    # الأحذية
    "shoes": "حذاء", "sneakers": "حذاء رياضي", "heels": "كعب عالي", "pumps": "حذاء كعب",
    "sandals": "صندل", "boots": "بوت", "slippers": "شبشب", "loafers": "لوفر",
    
    # الإكسسوارات
    "watch": "ساعة", "sunglasses": "نظارة شمسية", "bag": "شنطة", "handbag": "حقيبة يد",
    "backpack": "حقيبة ظهر", "wallet": "محفظة", "belt": "حزام", "scarf": "وشاح",
    "hat": "قبعة", "cap": "كاب", "gloves": "قفازات", "jewelry": "مجوهرات",
    "necklace": "عقد", "earrings": "حلق", "bracelet": "سوار", "ring": "خاتم",
    
    # الإلكترونيات
    "phone": "موبايل", "smartphone": "سنارت فون", "laptop": "لابتوب", "tablet": "تابلت",
    "headphones": "سماعات", "earbuds": "سماعات أذن", "charger": "شاحن", "cable": "كابل",
    "case": "جراب", "screen": "شاشة", "camera": "كاميرا", "speaker": "سماعة",
    "keyboard": "كيبورد", "mouse": "ماوس", "watch": "ساعة ذكية",
    
    # الميك أب والعناية
    "makeup": "ميك أب", "lipstick": "أحمر شفاه", "mascara": "ماسكارا", "eyeliner": "آيلاينر",
    "foundation": "فاونديشن", "concealer": "كونسيلر", "powder": "بودرة", "blush": "بلاشر",
    "perfume": "عطر", "cream": "كريم", "lotion": "لوشن", "shampoo": "شامبو",
    "conditioner": "بلسم", "serum": "سيروم", "mask": "ماسك",
    
    # المنزل
    "furniture": "أثاث", "chair": "كرسي", "table": "طاولة", "bed": "سرير",
    "sofa": "كنبة", "lamp": "لمبة", "carpet": "سجادة", "curtain": "ستارة",
    "kitchen": "مطبخ", "bathroom": "حمام", "bedroom": "غرفة نوم",
    
    # الأطفال
    "toys": "ألعاب", "stroller": "عربية أطفال", "diaper": "حفاض", "baby": "بيبي",
    "kids": "أطفال", "children": "أطفال",
    
    # صفات عامة
    "new": "جديد", "original": "أصلي", "genuine": "أصلي", "official": "رسمي",
    "premium": "بريميوم", "professional": "احترافي", "waterproof": "مقاوم للماء",
    "wireless": "لاسلكي", "bluetooth": "بلوتوث", "smart": "ذكي", "portable": "محمول",
    "adjustable": "قابل للتعديل", "foldable": "قابل للطي", "rechargeable": "قابل لإعادة الشحن",
    "automatic": "أوتوماتيك", "manual": "يدوي", "digital": "ديجيتال", "electric": "كهربائي",
    
    # ألوان
    "black": "أسود", "white": "أبيض", "red": "أحمر", "blue": "أزرق", "green": "أخضر",
    "yellow": "أصفر", "pink": "وردي", "purple": "بنفسجي", "gold": "ذهبي", "silver": "فضي",
}

class SmartGenerator:
    def __init__(self):
        self.brands = {
            "Apple": ["iphone", "ipad", "macbook", "airpods", "apple"],
            "Samsung": ["samsung", "galaxy"],
            "Sony": ["sony", "playstation", "wh-", "xm", "xb"],
            "Nike": ["nike", "air max", "jordan", "dunk"],
            "Adidas": ["adidas", "ultraboost", "yeezy", "nmd"],
            "Chanel": ["chanel", "no.5", "coco"],
            "Dior": ["dior", "sauvage", "jadore"],
            "Gucci": ["gucci", "bloom", "flora"],
            "Zara": ["zara"],
            "H&M": ["h&m"],
            "Shein": ["shein"],
            "MAC": ["mac ", "lipstick", "mac cosmetics"],
            "L'Oreal": ["l'oreal", "loreal", "l'oréal"],
            "Maybelline": ["maybelline"],
            "Estee Lauder": ["estee lauder"],
            "Lancome": ["lancome", "lancome"],
            "Timon": ["timon", "تمون"],
            "X Zone": ["x zone", "اكس زون"],
            "Saudi": ["السعودي", "saudi"],
            "Rolex": ["rolex"],
            "Casio": ["casio"],
            "Ray-Ban": ["ray-ban", "rayban"],
            "Victoria's Secret": ["victoria's secret", "victoria secret"],
            "Calvin Klein": ["calvin klein", "ck "],
            "Tommy Hilfiger": ["tommy hilfiger"],
            "Lacoste": ["lacoste"],
            "Puma": ["puma"],
            "Reebok": ["reebok"],
            "Under Armour": ["under armour"],
            "The North Face": ["the north face", "north face"],
            "Levi's": ["levi's", "levis"],
            "Hugo Boss": ["hugo boss", "boss "],
            "Dolce & Gabbana": ["dolce", "gabbana", "d&g"],
            "Prada": ["prada"],
            "Versace": ["versace"],
            "Armani": ["armani", "giorgio armani"],
            "Guess": ["guess"],
            "Michael Kors": ["michael kors", "mk "],
            "Coach": ["coach"],
            "Fossil": ["fossil"],
            "Daniel Wellington": ["daniel wellington", "dw "],
            "Anker": ["anker"],
            "Logitech": ["logitech"],
            "JBL": ["jbl"],
            "Bose": ["bose"],
            "Beats": ["beats", "beats by dre"],
            "Sennheiser": ["sennheiser"],
            "Philips": ["philips"],
            "Braun": ["braun"],
            "Dyson": ["dyson"],
            "Nespresso": ["nespresso"],
            "KitchenAid": ["kitchenaid"],
            "Tefal": ["tefal", "t-fal"],
            "Kenwood": ["kenwood"],
            "Bosch": ["bosch"],
            "Siemens": ["siemens"],
            "LG": ["lg ", "life's good"],
            "Panasonic": ["panasonic"],
            "Sharp": ["sharp"],
            "Toshiba": ["toshiba"],
            "Hitachi": ["hitachi"],
            "Whirlpool": ["whirlpool"],
            "Samsung": ["samsung"],
            "Huawei": ["huawei"],
            "Xiaomi": ["xiaomi", "mi "],
            "Oppo": ["oppo"],
            "Vivo": ["vivo"],
            "Realme": ["realme"],
            "OnePlus": ["oneplus"],
            "Nokia": ["nokia"],
            "Motorola": ["motorola"],
            "Lenovo": ["lenovo"],
            "HP": ["hp ", "hewlett packard"],
            "Dell": ["dell"],
            "Asus": ["asus"],
            "Acer": ["acer"],
            "MSI": ["msi"],
            "Razer": ["razer"],
            "Alienware": ["alienware"],
            "Corsair": ["corsair"],
            "SteelSeries": ["steelseries"],
            "HyperX": ["hyperx"],
            "BenQ": ["benq"],
            "ViewSonic": ["viewsonic"],
            "Epson": ["epson"],
            "Canon": ["canon"],
            "Nikon": ["nikon"],
            "Fujifilm": ["fujifilm", "fuji"],
            "GoPro": ["gopro"],
            "DJI": ["dji"],
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
        
        # قوالب قصيرة ومختلفة للستات
        self.templates_female = [
            "{emoji} {product} {brand}",
            "{emoji} {product} من {brand}",
            "{emoji} وصل: {product} {brand}",
            "{emoji} {product} الأنيق {brand}",
            "{emoji} {product} الفاخر {brand}",
            "{emoji} {product} المميز {brand}",
            "{emoji} {product} الأصلي {brand}",
        ]
        
        # قوالب للرجالة
        self.templates_male = [
            "{emoji} {product} {brand}",
            "{emoji} {product} من {brand}",
            "{emoji} وصل: {product} {brand}",
            "{emoji} {product} الأصلي {brand}",
            "{emoji} {product} المميز {brand}",
            "{emoji} {product} الاحترافي {brand}",
        ]
        
        self.emojis_female = ["✨", "💎", "👑", "🌸", "💖", "👜", "💄", "👗", "🛍️", "🎀", "🌟", "💫"]
        self.emojis_male = ["🔥", "⚡", "💪", "🎯", "🏆", "🚀", "⭐", "👊", "🎮", "📱", "💻", "⌚"]
    
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
    
    def translate_product_name(self, title, brand):
        """يترجم اسم المنتج للعربي بشكل ذكي"""
        t = title.lower()
        
        # نشيل البراند من العنوان
        if brand:
            t = re.sub(brand, "", t, flags=re.IGNORECASE)
        
        # نشيل الكلمات المشتركة الزايدة
        junk = ["with", "and", "the", "for", "new", "original", "genuine", "official", 
                "men", "women", "man", "woman", "male", "female", "unisex", "edition",
                "version", "model", "series", "pack", "set", "kit", "bundle"]
        for j in junk:
            t = re.sub(r"\b" + j + r"\b", "", t, flags=re.IGNORECASE)
        
        # نترجم الكلمات المتاحة
        words = t.split()
        translated_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in TRANSLATIONS:
                translated_words.append(TRANSLATIONS[clean_word])
            elif len(clean_word) > 2:  # نحتفظ بالكلمات الإنجليزية المهمة
                # نحاول نبسط
                if any(char.isdigit() for char in clean_word):  # موديلات زي iPhone 15
                    translated_words.append(word)
        
        # لو مفيش ترجمة، نرجع أول 3 كلمات من العنوان الأصلي
        if not translated_words:
            original_words = title.split()
            # نشيل البراند
            if brand:
                original_words = [w for w in original_words if brand.lower() not in w.lower()]
            return " ".join(original_words[:3]) if len(original_words) > 3 else title
        
        # نرجع 2-3 كلمات بس
        return " ".join(translated_words[:3])
    
    def clean_brand(self, brand):
        """تنظيف اسم البراند للعرض"""
        if not brand:
            return ""
        return f"({brand})"
    
    def format_price(self, price, old_price):
        """تنسيق السعر: السعر القديم في سطر والجديد في سطر تاني"""
        if old_price and price:
            try:
                # نستخرج الأرقام
                old_nums = re.findall(r"[\d,.]+", old_price)
                new_nums = re.findall(r"[\d,.]+", price)
                
                if old_nums and new_nums:
                    old_val = float(old_nums[0].replace(",", ""))
                    new_val = float(new_nums[0].replace(",", ""))
                    
                    if old_val > new_val:
                        disc = int(((old_val - new_val) / old_val) * 100)
                        # السطر الأول: السعر القديم مع ❌
                        # السطر الثاني: السعر الجديد مع نسبة الخصم
                        return f"❌ ~~{int(old_val):,}~~ ريال\n🔥 *{int(new_val):,}* ريال (-{disc}%)"
            except:
                pass
        
        # لو مفيش خصم أو فشل التحليل
        try:
            nums = re.findall(r"[\d,.]+", price)
            if nums:
                val = float(nums[0].replace(",", ""))
                return f"🔥 *{int(val):,}* ريال"
        except:
            pass
        
        return f"🔥 {price}"
    
    def generate(self, title, price, old_price, original_url):
        is_female = self.is_female(title)
        brand = self.get_brand(title)
        
        # نترجم اسم المنتج
        product_ar = self.translate_product_name(title, brand)
        
        # نجهز البراند
        brand_str = self.clean_brand(brand) if brand else ""
        
        # نختار الإيموجي والقالب
        if is_female:
            emoji = random.choice(self.emojis_female)
            template = random.choice(self.templates_female)
        else:
            emoji = random.choice(self.emojis_male)
            template = random.choice(self.templates_male)
        
        # نبني السطر الأول
        line1 = template.format(emoji=emoji, product=product_ar, brand=brand_str)
        
        # نبني السطر الثاني (السعر)
        line2 = self.format_price(price, old_price)
        
        # البوست النهائي: سطرين فقط + اللينك
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
                "❌ فشل في جلب المنتج من كل المصادر.\n\n"
                "جرب:\n"
                "• تأكد أن الرابط شغال في المتصفح\n"
                "• جرب تبعت الرابط من أمازون مباشرة مش مختصر", 
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
