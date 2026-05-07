import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "7956075348:AAEYTL28GKeMN7TXyVeGM69iUcfg5ZwOSIk"
bot = telebot.TeleBot(TOKEN)

GROQ_API_KEY = "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"

# ===================================
# 🏷️ البراندات
# ===================================

BRAND_NAMES = {
   "nespresso": "Nespresso", "nescafe": "Nescafé", "nescafé": "Nescafé",
   "dolce gusto": "Dolce Gusto", "delonghi": "DeLonghi", "philips": "Philips",
   "bosch": "Bosch", "samsung": "Samsung", "apple": "Apple", "iphone": "iPhone",
   "ipad": "iPad", "macbook": "MacBook", "airpods": "AirPods", "sony": "Sony",
   "lg": "LG", "dyson": "Dyson", "braun": "Braun", "panasonic": "Panasonic",
   "canon": "Canon", "nikon": "Nikon", "xiaomi": "Xiaomi", "huawei": "Huawei",
   "oppo": "OPPO", "realme": "Realme", "oneplus": "OnePlus", "nokia": "Nokia",
   "lenovo": "Lenovo", "dell": "Dell", "hp": "HP", "asus": "ASUS", "acer": "Acer",
   "msi": "MSI", "logitech": "Logitech", "razer": "Razer", "hyperx": "HyperX",
   "jbl": "JBL", "bose": "Bose", "beats": "Beats", "sennheiser": "Sennheiser",
   "anker": "Anker", "baseus": "Baseus", "ugreen": "UGREEN", "amazon": "Amazon",
   "google": "Google", "microsoft": "Microsoft", "adidas": "Adidas", "nike": "Nike",
   "puma": "Puma", "reebok": "Reebok", "under armour": "Under Armour",
   "new balance": "New Balance", "asics": "ASICS", "timberland": "Timberland",
   "skechers": "Skechers", "crocs": "Crocs", "levis": "Levi's", "wrangler": "Wrangler",
   "tommy hilfiger": "Tommy Hilfiger", "calvin klein": "Calvin Klein", "lacoste": "Lacoste",
   "polo": "Polo", "gucci": "Gucci", "prada": "Prada", "versace": "Versace",
   "dior": "Dior", "chanel": "Chanel", "louis vuitton": "Louis Vuitton",
   "hermes": "Hermès", "burberry": "Burberry", "coach": "Coach",
   "michael kors": "Michael Kors", "fossil": "Fossil", "casio": "Casio",
   "swatch": "Swatch", "rolex": "Rolex", "omega": "Omega", "tissot": "Tissot",
   "seiko": "Seiko", "citizen": "Citizen", "orient": "Orient", "dove": "Dove",
   "nivea": "Nivea", "loreal": "L'Oréal", "pantene": "Pantene",
   "head & shoulders": "Head & Shoulders", "gillette": "Gillette",
   "oral-b": "Oral-B", "colgate": "Colgate", "signal": "Signal",
   "ariel": "Ariel", "tide": "Tide", "persil": "Persil", "downy": "Downy",
   "comfort": "Comfort", "finish": "Finish", "fa": "FA", "rexona": "Rexona",
   "axe": "AXE", "old spice": "Old Spice", "dettol": "Dettol",
   "lifebuoy": "Lifebuoy", "purell": "Purell", "kleenex": "Kleenex",
   "tork": "Tork", "tempo": "Tempo", "whisper": "Whisper", "always": "Always",
   "tampax": "Tampax", "johnson": "Johnson's", "johnsons": "Johnson's",
   "pampers": "Pampers", "huggies": "Huggies", "molfix": "Molfix",
   "fine": "Fine", "marlboro": "Marlboro", "lm": "L&M", "kent": "Kent",
   "davidoff": "Davidoff", "nesquik": "Nesquik", "kitkat": "KitKat",
   "snickers": "Snickers", "mars": "Mars", "twix": "Twix", "bounty": "Bounty",
   "milky way": "Milky Way", "galaxy": "Galaxy", "cadbury": "Cadbury",
   "lindt": "Lindt", "ferrero": "Ferrero", "nutella": "Nutella",
   "kinder": "Kinder", "oreo": "Oreo", "belvita": "Belvita", "lu": "LU",
   "tuc": "TUC", "pringles": "Pringles", "lays": "Lay's", "doritos": "Doritos",
   "cheetos": "Cheetos", "pepsi": "Pepsi", "coca cola": "Coca-Cola",
   "cocacola": "Coca-Cola", "sprite": "Sprite", "fanta": "Fanta",
   "7up": "7UP", "mirinda": "Mirinda", "mountain dew": "Mountain Dew",
   "red bull": "Red Bull", "monster": "Monster", "power horse": "Power Horse",
   "nescafe dolce gusto": "Nescafé Dolce Gusto", "dolcegusto": "Dolce Gusto",
   "vichy": "Vichy", "dercos": "Dercos", "l'oreal": "L'Oréal",
   "l'oréal": "L'Oréal", "loreal paris": "L'Oréal Paris",
   "tresemme": "TRESemmé", "guess": "Guess", "night guess": "Night Guess",
   "swiss arabian": "Swiss Arabian", "kashkha": "Kashkha",
   "ultra doux": "Ultra Doux", "honey treasures": "Honey Treasures",
   "magic retouch": "Magic Retouch", "keratin smooth": "Keratin Smooth",
   "energy": "Energy",
}


def protect_brands(text):
   for brand_key, brand_original in sorted(BRAND_NAMES.items(), key=lambda x: -len(x[0])):
       pattern = re.compile(re.escape(brand_key), re.IGNORECASE)
       text = pattern.sub(brand_original, text)
   return text


# ===================================
# 🌍 أسعار دولية تقريبية
# ===================================

INTERNATIONAL_PRICES = {
   "iphone": {"us": 999, "ae": 4200},
   "ipad": {"us": 449, "ae": 1900},
   "macbook": {"us": 1299, "ae": 5200},
   "airpods": {"us": 179, "ae": 750},
   "samsung": {"us": 899, "ae": 3800},
   "sony": {"us": 350, "ae": 1400},
   "dyson": {"us": 500, "ae": 2100},
   "philips": {"us": 200, "ae": 850},
   "nespresso": {"us": 200, "ae": 850},
   "nescafe": {"us": 150, "ae": 650},
   "dolce gusto": {"us": 120, "ae": 550},
   "delonghi": {"us": 300, "ae": 1300},
   "l'oreal": {"us": 25, "ae": 100},
   "vichy": {"us": 35, "ae": 150},
   "dove": {"us": 15, "ae": 65},
   "nivea": {"us": 12, "ae": 50},
   "nike": {"us": 120, "ae": 500},
   "adidas": {"us": 100, "ae": 420},
   "puma": {"us": 80, "ae": 340},
}


def get_international_price(product_name):
   name_lower = product_name.lower()
   for brand, prices in INTERNATIONAL_PRICES.items():
       if brand in name_lower:
           avg_usd = (prices["us"] + prices["ae"] / 3.75) / 2
           return int(avg_usd * 3.75)
   return None


# ===================================
# 🔧 الفئات والترجمة
# ===================================

CATEGORY_KEYWORDS = {
   "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
   "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
   "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
   "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
   "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}


def detect_product_category(product_name):
   name_lower = product_name.lower()
   for category, keywords in CATEGORY_KEYWORDS.items():
       for keyword in keywords:
           if keyword in name_lower:
               return category
   return "general"


TRANSLATION_DICT = {
   "laptop": "لابتوب", "tablet": "تابلت", "keyboard": "كيبورد", "mouse": "ماوس",
   "charger": "شاحن", "cable": "كيبل", "power bank": "باور بانك", "battery": "بطارية",
   "screen": "شاشة", "monitor": "شاشة عرض", "camera": "كاميرا", "speaker": "سماعة",
   "watch": "ساعة", "smartwatch": "ساعة ذكية", "headphones": "سماعات رأس",
   "router": "راوتر", "modem": "مودم", "tv": "تلفزيون", "television": "تلفزيون",
   "shoes": "حذاء", "shoe": "حذاء", "sneakers": "حذاء رياضي", "boots": "بوت",
   "sandals": "صندل", "slippers": "شبشب", "t-shirt": "تيشيرت", "shirt": "قميص",
   "pants": "بنطلون", "jeans": "جينز", "jacket": "جاكيت", "hoodie": "هودي",
   "dress": "فستان", "skirt": "تنورة", "socks": "شرابات", "cap": "كاب",
   "hat": "قبعة", "bag": "شنطة", "backpack": "حقيبة ظهر", "wallet": "محفظة",
   "belt": "حزام", "scarf": "وشاح", "gloves": "قفازات",
   "perfume": "عطر", "fragrance": "عطر", "oud": "عود", "musk": "مسك",
   "cream": "كريم", "lotion": "لوشن", "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
   "refrigerator": "ثلاجة", "fridge": "ثلاجة", "washing machine": "غسالة",
   "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف", "ac": "مكيف",
   "heater": "دفاية", "fan": "مروحة", "blender": "خلاط", "mixer": "عجانة",
   "oven": "فرن", "microwave": "مايكرويف", "toaster": "محمصة", "kettle": "غلاية",
   "coffee maker": "ماكينة قهوة", "iron": "مكواة", "hair dryer": "سشوار",
   "chair": "كرسي", "table": "طاولة", "desk": "مكتب", "bed": "سرير",
   "sofa": "كنبة", "couch": "كنبة", "lamp": "لمبة", "light": "إضاءة",
   "mirror": "مرآة", "carpet": "سجادة", "curtain": "ستارة",
   "treadmill": "سير كهربائي", "dumbbell": "دامبل", "yoga mat": "حصيرة يوغا",
   "bicycle": "دراجة", "ball": "كرة", "toys": "ألعاب", "toy": "لعبة",
   "baby": "أطفال", "kids": "أطفال",
   "wireless": "لاسلكي", "bluetooth": "بلوتوث", "smart": "ذكي", "digital": "رقمي",
   "electric": "كهربائي", "automatic": "أوتوماتيك", "portable": "محمول",
   "professional": "احترافي", "original": "أصلي", "new": "جديد",
   "pro": "برو", "max": "ماكس", "plus": "بلس", "ultra": "ألترا", "mini": "ميني",
   "premium": "بريميوم", "deluxe": "ديلوكس", "unisex": "للجنسين", "adult": "للبالغين",
   "men": "رجالي", "women": "نسائي",
   "black": "أسود", "white": "أبيض", "blue": "أزرق", "red": "أحمر", "green": "أخضر",
   "capsule": "كبسولة", "capsules": "كبسولات", "machine": "ماكينة", "maker": "صانع",
   "espresso": "إسبريسو", "coffee": "قهوة", "cafe": "كافيه",
   "preparation": "تحضير", "prepare": "تحضير",
   "anti": "مضاد", "anti-hair loss": "مضاد تساقط", "hair loss": "تساقط الشعر",
   "stimulating": "منشط", "stimulator": "منشط", "fortifying": "يقوي",
   "serum": "سيروم", "repair": "ترميم", "damaged": "تالف", "split ends": "نهايات متقصفة",
   "protection": "حماية", "heat": "حرارة", "spray": "بخاخ", "fixative": "مثبت",
   "keratin": "كيراتين", "smooth": "سموث", "touch": "ريتاتش", "retouch": "ريتاتش",
   "night": "نايت", "eau de toilette": "أو دي تواليت", "edt": "أو دي تواليت",
   "eau de parfum": "أو دي بارفان", "edp": "أو دي بارفان", "perfume": "عطر",
   "for men": "للرجال", "for women": "للنساء", "unisex": "للجنسين",
   "swiss": "سويسرية", "arabian": "عربية", "oriental": "شرقية",
   "honey": "هوني", "treasures": "تريجرز",
}


def translate_to_arabic(text):
   text = protect_brands(text)
   text_lower = text.lower()
   words = text_lower.split()
   translated_words = []
   for word in words:
       clean_word = re.sub(r'[^\w\s]', '', word)
       if clean_word in TRANSLATION_DICT:
           translated_words.append(TRANSLATION_DICT[clean_word])
       else:
           translated_words.append(word)
   result = " ".join(translated_words)
   result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)
   return result


def smart_arabic_title(full_title):
   full_title = protect_brands(full_title)
   arabic_title = translate_to_arabic(full_title)
   words = arabic_title.split()
   unique_words = []
   for word in words:
       if not unique_words or word.lower() != unique_words[-1].lower():
           unique_words.append(word)
   result = " ".join(unique_words)
   result = protect_brands(result)
   if len(result) > 80:
       for sep in ['،', ',', '-', '|', '/']:
           if sep in result[:80]:
               idx = result.rfind(sep, 40, 80)
               if idx > 0:
                   result = result[:idx]
                   break
       else:
           idx = result.rfind(' ', 60, 80)
           if idx > 0:
               result = result[:idx]
           else:
               result = result[:80]
   return result.strip()


def get_category_emoji(category):
   emojis = {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}
   return emojis.get(category, "📦")


def expand_url(url):
   try:
       if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl']):
           headers = {"User-Agent": "Mozilla/5.0"}
           r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
           return r.url
       return url
   except:
       return url


def is_saudi_amazon(url):
   return "amazon.sa" in url.lower()


def extract_asin(url):
   patterns = [
       r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})',
       r'/product/([A-Z0-9]{10})', r'([A-Z0-9]{10})/?$',
       r'([A-Z0-9]{10})(?:[/?]|\b)'
   ]
   for p in patterns:
       m = re.search(p, url)
       if m:
           return m.group(1)
   return None


def clean_price(price_text):
   try:
       nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
       if nums:
           num_str = nums[0].replace(",", "")
           num_float = float(num_str)
           num_int = int(num_float)
           return f"{num_int} ريال"
   except:
       pass
   return price_text


def extract_number(price_text):
   try:
       nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
       if nums:
           return float(nums[0].replace(",", ""))
   except:
       pass
   return 0


def get_high_quality_image(soup):
   image = None
   img_elem = soup.select_one("#landingImage")
   if img_elem:
       image = img_elem.get("data-old-hires")
       if not image:
           dynamic_data = img_elem.get("data-a-dynamic-image")
           if dynamic_data:
               try:
                   img_dict = json.loads(dynamic_data)
                   if img_dict:
                       sorted_urls = sorted(img_dict.keys(), key=lambda x: img_dict[x][0] * img_dict[x][1], reverse=True)
                       image = sorted_urls[0] if sorted_urls else None
               except:
                   pass
       if not image:
           image = img_elem.get("src")
   if not image:
       gallery_img = soup.select_one("#imgTagWrapperId img")
       if gallery_img:
           image = gallery_img.get("data-old-hires") or gallery_img.get("src")
   if not image:
       og_img = soup.select_one('meta[property="og:image"]')
       if og_img:
           image = og_img.get("content")
   if image:
       image = clean_image_url(image)
   return image


def clean_image_url(url):
   if not url:
       return None
   patterns_to_remove = [
       r'_SX\d+_SY\d+_', r'_SX\d+_', r'_SY\d+_',
       r'_CR\d+,\d+,\d+,\d+_', r'_AC_SL\d+_',
       r'_SCLZZZZZZZ_', r'_FMwebp_', r'_QL\d+_',
   ]
   cleaned = url
   for pattern in patterns_to_remove:
       cleaned = re.sub(pattern, '_', cleaned)
   if '_SL' not in cleaned and 'amazon' in cleaned:
       cleaned = re.sub(r'(\.[a-zA-Z]+)(\?.*)?$', r'_SL1500\1', cleaned)
   cleaned = cleaned.split('?')[0]
   return cleaned


# ===================================
# ⭐ استخراج البيانات من الصفحة
# ===================================

def get_rating_and_reviews(soup):
   rating = None
   review_count = None
   review_text = None
   
   rating_selectors = [
       "[data-hook='average-star-rating'] .a-icon-alt",
       ".a-icon-alt",
       "#acrPopover .a-icon-alt",
       "[data-hook='rating-out-of-text']",
   ]
   for selector in rating_selectors:
       elem = soup.select_one(selector)
       if elem:
           text = elem.get_text(strip=True)
           match = re.search(r'(\d+\.?\d*)\s*out of\s*5', text)
           if match:
               rating = float(match.group(1))
               break
           match = re.search(r'(\d+\.?\d*)', text)
           if match:
               val = float(match.group(1))
               if 1 <= val <= 5:
                   rating = val
                   break
   
   review_selectors = [
       "[data-hook='total-review-count']",
       "#acrCustomerReviewText",
       "[data-hook='acr-count']",
       "a[href*='customerReviews']",
   ]
   for selector in review_selectors:
       elem = soup.select_one(selector)
       if elem:
           text = elem.get_text(strip=True)
           match = re.search(r'([\d,]+)', text)
           if match:
               review_count = int(match.group(1).replace(",", ""))
               break
   
   review_elem = soup.select_one("[data-hook='review-body'] span")
   if review_elem:
       review_text = review_elem.get_text(strip=True)
       if len(review_text) > 120:
           review_text = review_text[:120] + "..."
   
   return rating, review_count, review_text


def get_seller_info(soup):
   seller_name = None
   seller_rating = None
   
   seller_selectors = [
       "#merchant-info a",
       "[data-feature-name='merchant'] a",
       ".tabular-buybox-text[tabular-attribute-name='Merchant']",
       "#merchant-info",
   ]
   for selector in seller_selectors:
       elem = soup.select_one(selector)
       if elem:
           text = elem.get_text(strip=True)
           if text and "Amazon" not in text and len(text) > 2:
               seller_name = text
               break
   
   rating_elem = soup.select_one("[data-feature-name='merchant'] .a-icon-alt")
   if rating_elem:
       text = rating_elem.get_text(strip=True)
       match = re.search(r'(\d+)%', text)
       if match:
           seller_rating = int(match.group(1))
   
   return seller_name, seller_rating


def get_coupons_and_discounts(soup, current_price_num):
   coupons = []
   extra_discount_percent = 0
   
   coupon_selectors = [
       "#couponTextInput",
       "[data-feature-name='coupon']",
       ".couponText",
       "#couponContainer",
       "[id*='coupon']",
       ".promoPriceBlockMessage",
   ]
   
   for selector in coupon_selectors:
       elems = soup.select(selector)
       for elem in elems:
           text = elem.get_text(strip=True)
           if text and any(word in text.lower() for word in ['coupon', 'خصم', 'discount', 'save', 'وفّر', 'قسيمة', 'كوبون']):
               text = re.sub(r'\s+', ' ', text).strip()
               if len(text) > 5 and text not in coupons:
                   coupons.append(text)
   
   discount_patterns = [
       r'(\d+)%\s*(?:extra|additional|إضافي|إضافية)',
       r'(?:extra|additional|إضافي|إضافية)\s*(\d+)%',
       r'وفّر\s*(\d+)\s*ريال',
       r'save\s*SAR\s*(\d+)',
       r'save\s*([\d,]+)',
   ]
   
   for pattern in discount_patterns:
       matches = re.findall(pattern, soup.get_text(), re.IGNORECASE)
       for match in matches:
           try:
               val = float(match.replace(",", ""))
               if val > 0:
                   if current_price_num > 0 and val < current_price_num * 0.9:
                       extra_discount_percent = int((val / current_price_num) * 100)
                   else:
                       extra_discount_percent = int(val)
                   break
           except:
               continue
   
   coupons = list(set(coupons))[:2]
   return coupons, extra_discount_percent


def calculate_total_discount(old_price_num, current_price_num, extra_discount_percent):
   if old_price_num > 0 and current_price_num > 0:
       base_discount = int(((old_price_num - current_price_num) / old_price_num) * 100)
       if extra_discount_percent > 0:
           total = base_discount + extra_discount_percent
           return base_discount, extra_discount_percent, total
       return base_discount, 0, base_discount
   return 0, 0, 0


# ===================================
# 🔍 جلب بيانات المنتج
# ===================================

def get_product(asin):
   url = f"https://www.amazon.sa/dp/{asin}"
   user_agents = [
       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
       "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
   ]
   
   for attempt, ua in enumerate(user_agents):
       try:
           if attempt > 0:
               time.sleep(2)
           headers = {
               "User-Agent": ua,
               "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate, br",
               "DNT": "1",
               "Connection": "keep-alive",
               "Upgrade-Insecure-Requests": "1",
               "Cache-Control": "max-age=0",
               "Referer": "https://www.google.com/",
           }
           r = requests.get(url, headers=headers, timeout=30)
           if r.status_code != 200 or len(r.text) < 5000:
               continue
           
           soup = BeautifulSoup(r.text, "html.parser")
           
           title_elem = soup.select_one("#productTitle")
           if not title_elem:
               continue
           full_title = title_elem.text.strip()
           
           price = None
           price_selectors = [
               ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
               ".a-price.a-text-price.apexPriceToPay .a-offscreen",
               ".a-price.aok-align-center .a-offscreen",
               ".a-price .a-offscreen",
               "[data-a-color='price'] .a-offscreen",
               ".a-price-whole"
           ]
           for selector in price_selectors:
               elem = soup.select_one(selector)
               if elem and elem.text:
                   price = elem.text.strip()
                   if any(c.isdigit() for c in price):
                       break
           
           old_price = None
           old_selectors = [
               ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
               ".a-price.a-text-price .a-offscreen",
               ".basisPrice .a-offscreen",
           ]
           for selector in old_selectors:
               elem = soup.select_one(selector)
               if elem and elem.text:
                   text = elem.text.strip()
                   if text != price and any(c.isdigit() for c in text):
                       old_price = text
                       break
           
           image = get_high_quality_image(soup)
           rating, review_count, review_text = get_rating_and_reviews(soup)
           seller_name, seller_rating = get_seller_info(soup)
           
           current_price_num = extract_number(price) if price else 0
           coupons, extra_discount = get_coupons_and_discounts(soup, current_price_num)
           
           old_price_num = extract_number(old_price) if old_price else 0
           base_discount, extra_discount_pct, total_discount = calculate_total_discount(
               old_price_num, current_price_num, extra_discount
           )
           
           if price:
               arabic_title = smart_arabic_title(full_title)
               return {
                   "name": arabic_title,
                   "price": price,
                   "old_price": old_price,
                   "image": image,
                   "rating": rating,
                   "review_count": review_count,
                   "review_text": review_text,
                   "seller_name": seller_name,
                   "seller_rating": seller_rating,
                   "coupons": coupons,
                   "base_discount": base_discount,
                   "extra_discount": extra_discount_pct,
                   "total_discount": total_discount,
               }
               
       except Exception as e:
           print(f"Attempt {attempt + 1} failed: {e}")
           continue
   
   return None


# ===================================
# ✨ التوليد النهائي - بوست قصير يشد
# ===================================

def generate_post(product_data, original_url):
   name = product_data["name"]
   price = product_data["price"]
   old_price = product_data["old_price"]
   rating = product_data["rating"]
   review_count = product_data["review_count"]
   review_text = product_data["review_text"]
   seller_name = product_data["seller_name"]
   seller_rating = product_data["seller_rating"]
   coupons = product_data["coupons"]
   base_discount = product_data["base_discount"]
   extra_discount = product_data["extra_discount"]
   total_discount = product_data["total_discount"]
   
   category = detect_product_category(name)
   
   clean_current = clean_price(price)
   clean_old = clean_price(old_price) if old_price else None
   current_num = extract_number(price)
   old_num = extract_number(old_price) if old_price else 0
   
   intl_price = get_international_price(name)
   
   # 🧠 بناء سياق غني للـ AI
   context_parts = []
   
   if clean_old and old_num > current_num:
       context_parts.append(f"السعر قبل {clean_old} والحالي {clean_current}")
       if base_discount > 0:
           context_parts.append(f"خصم مباشر {base_discount}%")
   
   if intl_price and intl_price > old_num:
       context_parts.append(f"سعره بالخارج يوصل {intl_price} ريال")
   
   if rating and rating >= 4.0 and review_count:
       context_parts.append(f"تقييم {rating} نجوم من {review_count}+ مراجعة")
       if review_text:
           context_parts.append(f"مراجعة: {review_text}")
   
   if seller_name and seller_rating and seller_rating >= 90:
       context_parts.append(f"بائع موثوق {seller_name} تقييم {seller_rating}%")
   
   if coupons:
       context_parts.append(f"في كوبون: {coupons[0]}")
   
   if extra_discount > 0:
       context_parts.append(f"خصم إضافي {extra_discount}%")
   
   if total_discount > base_discount and total_discount > 0:
       context_parts.append(f"الخصم الكلي {total_discount}%")
   
   context = " | ".join(context_parts)
   
   # 🤖 توليد الجملة الافتتاحية بالـ AI
   opening = generate_ai_sentence(name, category, context)
   
   emoji = get_category_emoji(category)
   
   parts = []
   parts.append(opening)
   parts.append(f"{emoji} {name}")
   
   if clean_old and old_num > current_num:
       price_line = f"💰 ~~{clean_old}~~ → {clean_current}"
       if total_discount > 0:
           price_line += f" (-{total_discount}%)"
       parts.append(price_line)
   else:
       parts.append(f"💰 {clean_current}")
   
   if coupons:
       parts.append(f"🎟️ {coupons[0]}")
   
   parts.append(f"🔗 {original_url}")
   
   return "\n\n".join(parts)


def generate_ai_sentence(product_name, category, context):
   """توليد جملة افتتاحية قصيرة وقوية بناءً على السياق"""
   
   prompt = f"""أنت كاتب محتوى سعودي خليجي محترف في قناة تليجرام "صيدات وصفقات" للتسويق بالعمولة.
اكتب جملة افتتاحية قصيرة جداً (سطر واحد فقط، 5-10 كلمات كحد أقصى) باللهجة السعودية الخليجية.

🔹 قواعد مهمة:
- الجملة لازم تكون مختصرة جداً ومختصرة (تنفع تغريدة تويتر)
- استخدم إيموجي (2-3 إيموجي بس) في الجملة نفسها
- الجملة لازم تكون حماسية وتشد وتبيع المنتج
- بلهجة سعودية خليجية كريمة (مثل: "صيدة", "فرصة", "خطير", "يقطع", "يستاهل", "جودة")
- ❌ ممنوع: "ياجدعان", "ياجماعة", "يالله يا شباب", "حياكم", "يالا"
- ✅ استخدم أسلوب وصفي كريم: "صيدة من العيار الثقيل", "فرصة ما تتفوت", "جودة تاخذ العقل"
- كل مرة اكتب جملة مختلفة تماماً

🔹 المنتج: {product_name}
🔹 الفئة: {category}
🔹 المعلومات المتاحة: {context}

اكتب جملة واحدة فقط بدون أي مقدمة:"""

   try:
       headers = {
           "Authorization": f"Bearer {GROQ_API_KEY}",
           "Content-Type": "application/json"
       }
       data = {
           "model": "llama-3.3-70b-versatile",
           "messages": [
               {"role": "system", "content": "أنت كاتب محتوى سعودي خليجي في قناة 'صيدات وصفقات'. تكتب جمل افتتاحية قصيرة وقوية بإيموجي. أسلوبك حماسي وراقي ومختصر. كل مرة تكتب جملة مختلفة تماماً."},
               {"role": "user", "content": prompt}
           ],
           "temperature": 0.95,
           "max_tokens": 40
       }
       
       r = requests.post(
           "https://api.groq.com/openai/v1/chat/completions",
           headers=headers,
           json=data,
           timeout=20
       )
       
       if r.status_code == 200:
           result = r.json()
           sentence = result["choices"][0]["message"]["content"].strip()
           sentence = sentence.replace('"', '').replace("'", "").strip()
           sentence = re.sub(r'^[ـ\s]+', '', sentence)
           
           vulgar_calls = ["ياجدعان", "ياجماعه", "ياجماعة", "يالله يا", "حياكم", "يالا", "يالله"]
           for vulgar in vulgar_calls:
               if vulgar in sentence.lower().replace(" ", ""):
                   return generate_smart_fallback(category)
           
           return sentence
               
   except Exception as e:
       print(f"Groq error: {e}")
   
   return generate_smart_fallback(category)


def generate_smart_fallback(category):
   """جمل احتياطية قصيرة وقوية"""
   templates = {
       "electronics": ["⚡️ صيدة تقنية تاخذ العقل 🔥", "📱 جودة ما تتفوت 💎", "🚀 تحديث يستاهل ⚡️"],
       "home": ["🏠 بيتك يستاهل التحفة دي ✨", "☕️ لحظة هدوء تستاهلها 💫", "🔥 جهاز يسهللك حياتك 🏠"],
       "beauty": ["💄 جمالك يستاهل العناية ✨", "🌸 ريحة تفتح النفس 💫", "💎 فخامة تليق بيك 🌸"],
       "fashion": ["👟 طلة تكسر الدنيا ✨", "🔥 لبس ياخذ العقل 👌", "💫 أناقة بلا حدود 👟"],
       "sports": ["💪 طاقة تفجّر يا بطل 🔥", "🏋️ رياضتك تستاهل الأفضل ⚡️", "🔥 عرق اليوم يستاهل 💪"],
   }
   return random.choice(templates.get(category, ["🔥 صيدة من العيار الثقيل ✨", "💎 فرصة ما تتفوت 🔥", "⚡️ جودة تاخذ العقل 💫"]))


# ===================================
# 🤖 معالجة الرسائل
# ===================================

@bot.message_handler(func=lambda m: True)
def handler(msg):
   text = msg.text.strip()
   urls = re.findall(r'https?://\S+', text)

   if not urls:
       bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
       return

   for original_url in urls:
       expanded = expand_url(original_url)

       if not is_saudi_amazon(expanded):
           bot.reply_to(msg, "❌ الرابط يجب أن يكون من amazon.sa")
           continue

       asin = extract_asin(expanded)
       if not asin:
           bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج")
           continue

       wait = bot.reply_to(msg, "⏳ جاري التحليل...")

       product = get_product(asin)

       if not product:
           bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
           continue

       post = generate_post(product, original_url)

       try:
           if product["image"]:
               bot.send_photo(msg.chat.id, product["image"], caption=post)
           else:
               bot.send_message(msg.chat.id, post)
           bot.delete_message(msg.chat.id, wait.message_id)
       except Exception as e:
           print(f"Error sending: {e}")
           try:
               bot.send_message(msg.chat.id, post)
               bot.delete_message(msg.chat.id, wait.message_id)
           except:
               bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()
