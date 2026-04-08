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

# ===== قاموس ترجمة بسيط وعملي =====
TRANSLATIONS = {
    # عناية شخصية
    "shampoo": "شامبو", "conditioner": "بلسم", "serum": "سيروم", "cream": "كريم",
    "lotion": "لوشن", "oil": "زيت", "gel": "جل", "spray": "بخاخ", "wash": "غسول",
    "soap": "صابون", "scrub": "مقشر", "mask": "ماسك", "perfume": "عطر", "deo": "مزيل عرق",
    "toothpaste": "معجون أسنان", "brush": "فرشاة", "floss": "خيط أسنان",
    "razor": "موس حلاقة", "trimmer": "ماكينة حلاقة", "blade": "شفرة",
    
    # شعر
    "hair": "شعر", "shampoo": "شامبو", "conditioner": "بلسم", "dye": "صبغة",
    "color": "صبغة", "styling": "تصفيف", "gel": "جل", "wax": "شمع", "mousse": "موس",
    
    # بشرة
    "face": "وجه", "skin": "بشرة", "moisturizer": "مرطب", "cleanser": "منظف",
    "toner": "تونر", "sunscreen": "واقي شمس", "lip": "شفاه", "balm": "مرطب",
    "eye": "عين", "cream": "كريم", "anti-aging": "مكافح شيخوخة", "wrinkle": "تجاعيد",
    "acne": "حب شباب", "pimple": "بثرة", "spot": "بقعة", "dark": "داكن",
    "circle": "هالات", "under-eye": "تحت العين",
    
    # ميك أب
    "makeup": "ميك أب", "foundation": "فاونديشن", "concealer": "كونسيلر",
    "powder": "بودرة", "blush": "بلاشر", "bronzer": "برونزر", "highlighter": "هايلايتر",
    "lipstick": "أحمر شفاه", "gloss": "لمعة", "mascara": "ماسكارا", "liner": "آيلاينر",
    "shadow": "ظلال", "palette": "باليت", "makeup": "ميك أب", "remover": "مزيل",
    
    # أظافر
    "nail": "أظافر", "polish": "مناكير", "varnish": "مناكير", "remover": "مزيل",
    "file": "مبرد", "clipper": "قصاصة", "cutter": "قاطع",
    
    # إلكترونيات
    "phone": "موبايل", "mobile": "جوال", "smartphone": "سنارت فون", "charger": "شاحن",
    "cable": "كابل", "headphones": "سماعات", "earbuds": "سماعات أذن", "speaker": "سماعة",
    "power": "باور", "bank": "بنك", "adapter": "محول", "case": "جراب", "cover": "غطاء",
    "screen": "شاشة", "protector": "حماية", "lens": "عدسة", "camera": "كاميرا",
    "watch": "ساعة", "smart": "ذكية", "band": "سوار", "tracker": "متعقب",
    "keyboard": "كيبورد", "mouse": "ماوس", "laptop": "لابتوب", "tablet": "تابلت",
    
    # منزل
    "vacuum": "مكنسة", "cleaner": "نظافة", "robot": "روبوت", "fan": "مروحة",
    "purifier": "منقي", "humidifier": "مرطب", "heater": "دفاية", "light": "لمبة",
    "lamp": "إضاءة", "bulb": "لمبة", "battery": "بطارية",
    
    # مطبخ
    "blender": "خلاط", "mixer": "عجان", "toaster": "محمصة", "kettle": "غلاية",
    "coffee": "قهوة", "maker": "ماكينة", "pot": "حلة", "pan": "مقلاة", "knife": "سكينة",
    "plate": "طبق", "cup": "كوب", "mug": "مج", "glass": "كاسة", "bottle": "زجاجة",
    
    # ملابس
    "shirt": "قميص", "t-shirt": "تيشيرت", "pants": "بنطلون", "jeans": "جينز",
    "dress": "فستان", "skirt": "تنورة", "jacket": "جاكيت", "coat": "معطف",
    "shoes": "حذاء", "sneakers": "حذاء رياضي", "boots": "بوت", "sandals": "صندل",
    "slippers": "شبشب", "socks": "جورب", "underwear": "ملابس داخلية", "belt": "حزام",
    "hat": "قبعة", "cap": "كاب", "scarf": "وشاح", "gloves": "قفازات", "bag": "شنطة",
    
    # أطفال
    "baby": "بيبي", "diaper": "حفاض", "wipes": "مناديل", "stroller": "عربية",
    "bottle": "رضاعة", "pacifier": "مصاصة", "toys": "ألعاب",
    
    # رياضة
    "fitness": "لياقة", "gym": "جيم", "yoga": "يوجا", "mat": "حصيرة", "ball": "كرة",
    "dumbbell": "دامبل", "rope": "حبل", "bicycle": "دراجة",
    
    # صفات
    "digital": "رقمي", "electric": "كهربائي", "automatic": "أوتوماتيك", "manual": "يدوي",
    "wireless": "لاسلكي", "portable": "محمول", "rechargeable": "قابل للشحن",
    "waterproof": "مقاوم للماء", "professional": "احترافي", "original": "أصلي",
    "new": "جديد", "quick": "سريع", "fast": "سريع", "easy": "سهل", "simple": "بسيط",
    "soft": "ناعم", "smooth": "ملس", "fresh": "منعش", "clean": "نظيف", "clear": "واضح",
    
    # ألوان
    "black": "أسود", "white": "أبيض", "red": "أحمر", "blue": "أزرق", "green": "أخضر",
    "yellow": "أصفر", "pink": "وردي", "purple": "بنفسجي", "brown": "بني", "gray": "رمادي",
    "gold": "ذهبي", "silver": "فضي",
}

# ===== جمل افتتاحية =====
OPENING_LINES_FEMALE = [
    "اختيارك الذكي للعناية الشخصية 🎯",
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
    "اختيارك الذكي للعناية الشخصية 🎯",
    "جودة عالية بسعر ممتاز 💪",
    "منتج يستحق التجربة فعلاً 🔥",
    "للرجال اللي يقدرون الجودة ⚡",
    "أداء احترافي بتكلفة معقولة 🏆",
    "حل عملي لمظهر أكثر تميزاً 👔",
    "تصميم عملي وأنيق في نفس الوقت 🎩",
    "اختيارك الأمثل للاستخدام اليومي 🚀",
    "قيمة ممتازة مقابل السعر 👌",
    "منتج احترافي لرجل متميز 💼",
]

OPENING_LINES_GENERAL = [
    "اختيارك الذكي للعناية الشخصية 🎯",
    "مناسب للاستخدام اليومي بدون تعقيد 🏡",
    "جودة ممتازة بسعر unbeatable ✨",
    "اختيارك الأمثل للعناية الشخصية 💎",
    "منتج يستحق التجربة فعلاً 🔥",
    "قيمة رائعة مقابل السعر 🌟",
    "تصميم عملي وأنيق في نفس الوقت 💫",
    "لجميع أفراد العائلة 👨‍👩‍👧‍👦",
    "حل مثالي للاستخدام اليومي 💪",
    "جودة عالية بتكلفة معقولة 🏆",
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
            "L'Oreal": ["l'oreal", "loreal", "l'oréal"],
            "Maybelline": ["maybelline"],
            "Estee Lauder": ["estee lauder"],
            "Lancome": ["lancome"],
            "The Ordinary": ["the ordinary"],
            "CeraVe": ["cerave"],
            "Neutrogena": ["neutrogena"],
            "Olay": ["olay"],
            "Nivea": ["nivea", "nivea men"],
            "Garnier": ["garnier"],
            "Pond's": ["pond's", "ponds"],
            "Vaseline": ["vaseline"],
            "Dove": ["dove", "dove men"],
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
            "Gillette": ["gillette"],
            "Schick": ["schick"],
            "Veet": ["veet"],
            "Xiaomi": ["xiaomi", "mi ", "redmi", "poco"],
            "Huawei": ["huawei", "honor"],
            "Anker": ["anker", "soundcore", "eufy"],
            "Logitech": ["logitech"],
            "JBL": ["jbl"],
            "Bose": ["bose"],
            "Beats": ["beats"],
            "X Zone": ["x zone", "اكس زون"],
            "Timon": ["timon", "تمون"],
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
            "Dreame": ["dreame"],
            "Roborock": ["roborock"],
            "Ecovacs": ["ecovacs"],
            "Eufy": ["eufy"],
            "Amazon Basics": ["amazon basics", "amazonbasics"],
            "Sol de Janeiro": ["sol de janeiro"],
            "Cetaphil": ["cetaphil"],
            "La Roche-Posay": ["la roche-posay", "la roche posay"],
            "Vichy": ["vichy"],
            "Avene": ["avene"],
            "Bioderma": ["bioderma"],
            "Eucerin": ["eucerin"],
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
    
    def simplify_product_name(self, title, brand):
        """تبسيط اسم المنتج - نرجع أول 4-5 كلمات مفيدة"""
        # نشيل البراند
        if brand:
            title = re.sub(brand, "", title, flags=re.IGNORECASE)
        
        # نشيل الكلمات والرموز الزايدة
        junk_patterns = [
            r'\([^)]*\)',  # حذف ما بين قوسين
            r'\[[^\]]*\]',  # حذف ما بين أقواس مربعة
            r'\d+\s*(ml|g|kg|mm|cm|oz|lb|pcs|pieces|pack|set)',  # الأحجام والكميات
            r'\d+',  # الأرقام
            r'[^\w\s]',  # الرموز الخاصة
        ]
        
        clean_title = title
        for pattern in junk_patterns:
            clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
        
        # نشيل الكلمات المشتركة
        stop_words = ['with', 'and', 'the', 'for', 'new', 'original', 'genuine', 'official',
                      'men', 'women', 'man', 'woman', 'male', 'female', 'unisex',
                      'edition', 'version', 'model', 'series', 'type', 'style',
                      'high', 'quality', 'best', 'top', 'super', 'ultra', 'premium',
                      'suitable', 'all', 'skin', 'types', 'hair', 'body', 'face']
        
        words = clean_title.split()
        filtered_words = []
        
        for word in words:
            w_lower = word.lower()
            if len(word) > 2 and w_lower not in stop_words:
                filtered_words.append(word)
        
        # نرجع أول 4 كلمات
        result = ' '.join(filtered_words[:4]).strip()
        
        # لو فاضي، نرجع العنوان الأصلي المختصر
        if not result:
            original = title.split()[:5]
            result = ' '.join(original)
        
        return result
    
    def translate_product(self, title, brand):
        """ترجمة ذكية - لو مفيش ترجمة نرجع الإنجليزي المبسط"""
        simplified = self.simplify_product_name(title, brand)
        
        # نحاول نترجم كل كلمة
        words = simplified.split()
        translated_words = []
        
        for word in words:
            w_clean = word.lower().strip()
            # ندور على الترجمة
            if w_clean in TRANSLATIONS:
                translated_words.append(TRANSLATIONS[w_clean])
            else:
                # نشوف لو فيه جزء من الكلمة يتطابق
                found = False
                for key, value in TRANSLATIONS.items():
                    if key in w_clean or w_clean in key:
                        translated_words.append(value)
                        found = True
                        break
                if not found:
                    # نحتفظ بالكلمة الإنجليزية
                    translated_words.append(word)
        
        # نرجع النتيجة
        if translated_words:
            result = ' '.join(translated_words)
            # لو الترجمة ناقصة، نضيف الكلمات الإنجليزية الأصلية
            if len([w for w in translated_words if any('\u0600' <= c <= '\u06FF' for c in w)]) < 2:
                # أقل من كلمتين عربي، نرجع مكس
                return f"{simplified}"
            return result
        
        return simplified
    
    def format_price(self, price, old_price):
        """تنسيق السعر"""
        def extract_number(text):
            if not text:
                return None
            nums = re.findall(r"[\d,.]+", str(text))
            if nums:
                try:
                    return int(float(nums[0].replace(",", "")))
                except:
                    pass
            return None
        
        current = extract_number(price)
        old = extract_number(old_price)
        
        if old and current and old > current:
            discount = int(((old - current) / old) * 100)
            return f"❌ قبل: {old:,} ريال سعودي\n✅ الآن: {current:,} ريال سعودي (وفر {discount}%)"
        
        if current:
            return f"💰 السعر: {current:,} ريال سعودي"
        
        return f"💰 السعر: {price}"
    
    def generate(self, title, price, old_price, original_url):
        print(f"\n=== Generating Post ===")
        print(f"Original title: {title}")
        print(f"Price: {price}, Old: {old_price}")
        
        is_female = self.is_female(title)
        brand = self.get_brand(title)
        
        # نختار الجملة الافتتاحية
        if is_female:
            opening = random.choice(OPENING_LINES_FEMALE)
        else:
            opening = random.choice(OPENING_LINES_MALE)
        
        # نجهز اسم المنتج
        product_name = self.translate_product(title, brand)
        print(f"Product name: {product_name}")
        
        # نجهز البراند
        brand_str = f" ({brand})" if brand else ""
        
        # نبني البوست
        line1 = f"{opening}\n\n🛒 {product_name}{brand_str}"
        line2 = self.format_price(price, old_price)
        
        post = f"{line1}\n\n{line2}\n\n🔗 {original_url}"
        
        print(f"Final post:\n{post}\n")
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
