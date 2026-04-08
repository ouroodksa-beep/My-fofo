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

# ===== قاموس ترجمة موسع =====
TRANSLATIONS = {
    # أجهزة منزلية
    "vacuum": "مكنسة", "cleaner": "نظافة", "robot": "روبوت", "automatic": "أوتوماتيك",
    "fan": "مروحة", "air": "هواء", "conditioner": "مكيف", "purifier": "منقي",
    "heater": "دفاية", "cooler": "مبرد", "humidifier": "مرطب", "dehumidifier": "مزيل رطوبة",
    "washer": "غسالة", "dryer": "نشافة", "dishwasher": "جلاية", "refrigerator": "ثلاجة",
    "fridge": "ثلاجة", "freezer": "فريزر", "oven": "فرن", "microwave": "ميكروويف",
    "blender": "خلاط", "mixer": "عجان", "toaster": "محمصة", "kettle": "غلاية",
    "coffee": "قهوة", "maker": "صانع", "machine": "ماكينة", "espresso": "إسبريسو",
    
    # إلكترونيات
    "phone": "موبايل", "smartphone": "جوال", "mobile": "موبايل", "cell": "جوال",
    "laptop": "لابتوب", "computer": "كمبيوتر", "tablet": "تابلت", "ipad": "آيباد",
    "headphones": "سماعات", "earbuds": "سماعات أذن", "speaker": "سماعة", "soundbar": "ساوند بار",
    "charger": "شاحن", "cable": "كابل", "adapter": "محول", "battery": "بطارية",
    "power": "طاقة", "bank": "بنك", "wireless": "لاسلكي", "bluetooth": "بلوتوث",
    "watch": "ساعة", "smart": "ذكية", "band": "سوار", "tracker": "متعقب",
    "camera": "كاميرا", "lens": "عدسة", "tripod": "ترايبود", "light": "إضاءة",
    "tv": "تلفزيون", "television": "تلفزيون", "screen": "شاشة", "monitor": "شاشة",
    "projector": "بروجكتور", "remote": "ريموت", "control": "تحكم",
    
    # أثاث وديكور
    "furniture": "أثاث", "chair": "كرسي", "table": "طاولة", "desk": "مكتب",
    "bed": "سرير", "sofa": "كنبة", "couch": "صوفا", "wardrobe": "دولاب",
    "cabinet": "خزانة", "shelf": "رف", "mirror": "مراية", "lamp": "لمبة",
    "lighting": "إضاءة", "carpet": "سجادة", "rug": "سجادة", "curtain": "ستارة",
    "pillow": "مخدة", "mattress": "مرتبة", "blanket": "بطانية", "towel": "فوطة",
    
    # مطبخ وأدوات
    "kitchen": "مطبخ", "cookware": "أدوات طبخ", "pot": "حلة", "pan": "مقلاة",
    "knife": "سكينة", "cutlery": "أدوات مائدة", "plate": "طبق", "bowl": "بولة",
    "cup": "كوب", "mug": "مج", "glass": "كاسة", "bottle": "زجاجة",
    "container": "حافظة", "storage": "تخزين", "box": "صندوق", "organizer": "منظم",
    
    # عناية شخصية
    "cream": "كريم", "lotion": "لوشن", "serum": "سيروم", "oil": "زيت",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون", "wash": "غسول",
    "scrub": "مقشر", "mask": "ماسك", "sunscreen": "واقي شمس", "deodorant": "مزيل عرق",
    "perfume": "عطر", "fragrance": " fragrance", "makeup": "ميك أب", "cosmetic": "مستحضر",
    "lipstick": "أحمر شفاه", "mascara": "ماسكارا", "eyeliner": "آيلاينر",
    "foundation": "فاونديشن", "concealer": "كونسيلر", "powder": "بودرة",
    "brush": "فرشاة", "comb": "مشط", "razor": "موس حلاقة", "trimmer": "ماكينة حلاقة",
    
    # ملابس وأحذية
    "shoes": "حذاء", "sneakers": "حذاء رياضي", "boots": "بوت", "sandals": "صندل",
    "slippers": "شبشب", "heels": "كعب عالي", "dress": "فستان", "skirt": "تنورة",
    "shirt": "قميص", "t-shirt": "تيشيرت", "pants": "بنطلون", "jeans": "جينز",
    "jacket": "جاكيت", "coat": "معطف", "sweater": "كنزة", "hoodie": "هودي",
    "shorts": "شورت", "socks": "جورب", "underwear": "ملابس داخلية", "pajamas": "بيجاما",
    "suit": "بدلة", "uniform": "زي", "sportswear": "ملابس رياضية", "swimwear": "ملابس سباحة",
    
    # إكسسوارات
    "bag": "شنطة", "handbag": "حقيبة يد", "backpack": "حقيبة ظهر", "wallet": "محفظة",
    "belt": "حزام", "scarf": "وشاح", "hat": "قبعة", "cap": "كاب", "gloves": "قفازات",
    "sunglasses": "نظارة شمسية", "glasses": "نظارة", "jewelry": "مجوهرات",
    "necklace": "عقد", "earrings": "حلق", "bracelet": "سوار", "ring": "خاتم",
    "watch": "ساعة", "clock": "ساعة حائط",
    
    # رياضة ولياقة
    "fitness": "لياقة", "gym": "جيم", "yoga": "يوجا", "mat": "حصيرة", "ball": "كرة",
    "dumbbell": "دامبل", "weight": "وزن", "rope": "حبل", "band": "شريط مقاومة",
    "bicycle": "دراجة", "treadmill": "سير كهربائي", "equipment": "معدات",
    
    # ألعاب وهدايا
    "toys": "ألعاب", "game": "لعبة", "puzzle": "لغز", "doll": "دمية", "car": "سيارة",
    "gift": "هدية", "set": "طقم", "kit": "مجموعة", "box": "صندوق",
    
    # مستلزمات أطفال
    "baby": "بيبي", "diaper": "حفاض", "stroller": "عربية أطفال", "crib": "سرير أطفال",
    "bottle": "رضاعة", "pacifier": "مصاصة", "toys": "ألعاب",
    
    # صفات عامة
    "new": "جديد", "original": "أصلي", "genuine": "أصلي", "official": "رسمي",
    "premium": "بريميوم", "professional": "احترافي", "advanced": "متقدم",
    "portable": "محمول", "compact": "مضغوط", "mini": "ميني", "small": "صغير",
    "large": "كبير", "big": "كبير", "light": "خفيف", "heavy": "ثقيل",
    "fast": "سريع", "quick": "سريع", "slow": "بطيء", "quiet": "هادئ", "silent": "صامت",
    "powerful": "قوي", "strong": "قوي", "durable": "متين", "sturdy": "متين",
    "waterproof": "مقاوم للماء", "resistant": "مقاوم", "protection": "حماية",
    "adjustable": "قابل للتعديل", "foldable": "قابل للطي", "rechargeable": "قابل لإعادة الشحن",
    "cordless": "لا سلكي", "wireless": "لاسلكي", "digital": "ديجيتال", "electric": "كهربائي",
    "manual": "يدوي", "automatic": "أوتوماتيك", "smart": "ذكي", "intelligent": "ذكي",
    
    # ألوان
    "black": "أسود", "white": "أبيض", "red": "أحمر", "blue": "أزرق", "green": "أخضر",
    "yellow": "أصفر", "orange": "برتقالي", "pink": "وردي", "purple": "بنفسجي",
    "brown": "بني", "gray": "رمادي", "grey": "رمادي", "gold": "ذهبي", "silver": "فضي",
    "beige": "بيج", "navy": "كحلي", "turquoise": "فيروزي",
}

# ===== جمل افتتاحية سعودية =====
OPENING_LINES_FEMALE = [
    "الوقت ضيق جداً 🚨",
    "لأنك تستحقين الأفضل دائماً 💎",
    "سر جمالكِ في منتج واحد ✨",
    "تجربة فاخرة بسعر ممتاز 🌸",
    "منتج يستحق التجربة فعلاً 💕",
    "للمحافظة على جمالكِ الطبيعي 🦋",
    "اختياركِ الأمثل للعناية اليومية 🌺",
    "جودة عالية بتكلفة معقولة 💫",
    "بشرتكِ تستحق الأفضل دائماً ✨",
    "لا يفوتكِ هذا العرض المميز 👑",
]

OPENING_LINES_MALE = [
    "الوقت ضيق جداً 🚨",
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
    "الوقت ضيق جداً 🚨",
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
            "Rexona": ["rexona"],
            "Nivea Men": ["nivea men"],
            "Gillette": ["gillette"],
            "Schick": ["schick"],
            "Veet": ["veet"],
            "Xiaomi": ["xiaomi", "mi "],
            "Huawei": ["huawei"],
            "Anker": ["anker"],
            "Logitech": ["logitech"],
            "JBL": ["jbl"],
            "Bose": ["bose"],
            "Beats": ["beats"],
            "X Zone": ["x zone", "اكس زون"],
            "Timon": ["timon", "تمون"],
            "Saudi": ["السعودي", "saudi"],
            "iRobot": ["irobot", "roomba"],
            "Dyson": ["dyson"],
            "De'Longhi": ["delonghi", "de longhi"],
            "Nespresso": ["nespresso"],
            "Breville": ["breville"],
            "KitchenAid": ["kitchenaid"],
            "Tefal": ["tefal", "t-fal"],
            "Kenwood": ["kenwood"],
            "Bosch": ["bosch"],
            "Siemens": ["siemens"],
            "LG": ["lg "],
            "Panasonic": ["panasonic"],
            "Sharp": ["sharp"],
            "Toshiba": ["toshiba"],
            "Whirlpool": ["whirlpool"],
            "Samsung": ["samsung"],
            "Xiaomi": ["xiaomi"],
            "Dreame": ["dreame"],
            "Roborock": ["roborock"],
            "Ecovacs": ["ecovacs"],
            "Eufy": ["eufy"],
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
        """يترجم اسم المنتج للعربي بشكل ذكي"""
        t = title.lower()
        
        # نشيل البراند
        if brand:
            t = re.sub(brand, "", t, flags=re.IGNORECASE)
        
        # نشيل الكلمات الزايدة والأرقام والوحدات
        junk = ["with", "and", "the", "for", "new", "original", "genuine", "official",
                "men", "women", "man", "woman", "male", "female", "unisex", "edition",
                "version", "model", "series", "pack", "set", "kit", "bundle", 
                "ml", "mm", "cm", "kg", "g", "l", "w", "v", "hz",
                "all", "types", "skin", "hair", "suitable", "for", "universal",
                "high", "low", "quality", "best", "top", "super", "ultra", "mega",
                "in", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                " rechargeable", " cordless", " wireless", " portable"]
        
        for j in junk:
            t = re.sub(r"\b" + j + r"\b", "", t, flags=re.IGNORECASE)
        
        # نحذف الأرقام والرموز
        t = re.sub(r'\d+', '', t)
        t = re.sub(r'[^\w\s]', '', t)
        
        # نترجم الكلمات
        words = t.split()
        translated = []
        
        for word in words:
            clean = word.lower().strip()
            if not clean or len(clean) < 2:
                continue
            
            if clean in TRANSLATIONS:
                translated.append(TRANSLATIONS[clean])
            elif clean.replace('s', '') in TRANSLATIONS:  # جمع مفرد
                translated.append(TRANSLATIONS[clean.replace('s', '')])
        
        # لو مفيش ترجمة، نرجع كلمات مفيدة من العنوان الأصلي
        if not translated:
            original_words = title.split()
            # ننظف الكلمات
            clean_words = []
            for w in original_words:
                w_clean = re.sub(r'[^\w]', '', w)
                if len(w_clean) > 3 and w_clean.lower() not in ['with', 'and', 'the', 'for', 'new']:
                    if not brand or brand.lower() not in w.lower():
                        clean_words.append(w_clean)
            
            # نترجم اللي نقدر عليه
            for w in clean_words[:5]:
                w_lower = w.lower()
                if w_lower in TRANSLATIONS:
                    clean_words[clean_words.index(w)] = TRANSLATIONS[w_lower]
            
            return " ".join(clean_words[:4]) if clean_words else "منتج مميز"
        
        return " ".join(translated[:5])
    
    def format_price(self, price, old_price):
        """تنسيق السعر بالطريقة السعودية"""
        # نستخرج الأرقام والعملة
        def extract_price(text):
            if not text:
                return None, "ريال"
            nums = re.findall(r"[\d,.]+", str(text))
            currency = "ريال"
            if "sar" in text.lower() or "ريال" in text or "saudi" in text.lower():
                currency = "ريال سعودي"
            elif "$" in text or "usd" in text.lower():
                currency = "دولار"
            
            if nums:
                try:
                    # ننظف الرقم
                    num_str = nums[0].replace(",", "")
                    val = float(num_str)
                    return int(val), currency
                except:
                    pass
            return None, currency
        
        current_val, curr = extract_price(price)
        old_val, _ = extract_price(old_price)
        
        print(f"Price parsing: current={current_val}, old={old_val}, curr={curr}")
        
        if old_val and current_val and old_val > current_val:
            discount = int(((old_val - current_val) / old_val) * 100)
            return f"❌ قبل: {old_val:,} {curr}\n✅ الآن: {current_val:,} {curr} (وفر {discount}%)"
        
        if current_val:
            return f"💰 السعر: {current_val:,} {curr}"
        
        return f"💰 السعر: {price}"
    
    def generate(self, title, price, old_price, original_url):
        print(f"Generating post for: {title}")
        print(f"Price: {price}, Old: {old_price}")
        
        is_female = self.is_female(title)
        brand = self.get_brand(title)
        
        # نختار الجملة الافتتاحية
        if is_female:
            opening = random.choice(OPENING_LINES_FEMALE)
        else:
            opening = random.choice(OPENING_LINES_MALE)
        
        # نترجم اسم المنتج
        product_ar = self.translate_product(title, brand)
        print(f"Translated product: {product_ar}")
        
        # نبني السطر الأول (الجملة + المنتج)
        brand_str = f" {brand}" if brand else ""
        line1 = f"{opening}\n\n🛒 {product_ar}{brand_str}"
        
        # السطر الثاني (السعر)
        line2 = self.format_price(price, old_price)
        
        # البوست النهائي
        post = f"{line1}\n\n{line2}\n\n🔗 {original_url}"
        
        print(f"Final post:\n{post}")
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
                print(f"Title: {result['title'][:50]}...")
                print(f"Price: {result.get('price')}")
                print(f"Old Price: {result.get('old_price')}")
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
