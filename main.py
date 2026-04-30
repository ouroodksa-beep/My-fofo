import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "7956075348:AAFVmKy956NrjQrYR5-zBMz5l4jV85Q5K8s"
bot = telebot.TeleBot(TOKEN)

GROQ_API_KEY = "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"

def safe_float(value):
   if value is None:
       return 0.0
   if isinstance(value, (int, float)):
       return float(value)
   cleaned = re.sub(r'[^\d.]', '', str(value))
   try:
       return float(cleaned) if cleaned else 0.0
   except:
       return 0.0

def calculate_savings(old_price, new_price):
   old_val = safe_float(old_price)
   new_val = safe_float(new_price)
   if old_val > new_val:
       return int(old_val - new_val)
   return 0


def generate_ai_post(product_info):
   """
   أسلوب قنوات التسويق السعودية (زي أكسب زون)
   مختصر ومباشر وحماسي
   """
   
   # نختار معلومة واحدة بس اللي تخدم التسويق
   hook = ""
   if product_info.get('discount_percent') and product_info['discount_percent'] >= 30:
       hook = f"خصم {product_info['discount_percent']}%"
   elif product_info.get('is_best_seller'):
       hook = "الأكثر مبيعاً"
   elif product_info.get('brand') and product_info['brand'] != 'غير معروف':
       hook = f"براند {product_info['brand']}"
   elif product_info.get('prime'):
       hook = "توصيل Prime"
   
   savings = calculate_savings(product_info.get('old_price'), product_info['price'])
   
   original_url = product_info.get('url', '')
   
   prompt = f"""أنت كاتب محتوى سعودي في قناة تسويق بالعمولة (زي قناة "أكسب زون" و"نص السعر").
اكتب بوست تسويقي للمنتج التالي.

🔹 الأسلوب المطلوب:
- مختصر جداً ومباشر (6-8 أسطر كحد أقصى)
- حماسي وسعودي وقريب من الناس
- ما تحشي بيانات كثيرة! معلومة واحدة بس في أول سطر
- التنسيق:
 السطر 1: صيحة أو جملة حماسية مختصرة (ممكن تذكر الخصم أو البراند)
 السطر 2: اسم المنتج مختصر
 سطر فارغ
 السطر 3: السعر القديم
 السطر 4: السعر الجديد
 سطر فارغ
 السطر 5: الرابط
- فاصل سطر واحد بين كل جزء
- استخدم إيموجي بسيط

🔹 بيانات المنتج:
- الاسم: {product_info['name']}
- السعر الحالي: {product_info['price']} ريال
- السعر القديم: {product_info.get('old_price', 'غير متوفر')} ريال
- المعلومة المختارة: {hook if hook else 'لا يوجد'}
- التوفير: {savings} ريال
- الرابط: {original_url}

🔹 أمثلة للأسلوب المطلوب:

مثال 1:
🔥 لا يفوتكم يا جماعة!
Puma حذاء رياضي 👟

❌ كان بـ 388 ريال
✅ الحين بـ 190 ريال بس!

🔗 https://ty.gl/xxx

مثال 2:
💥 ووووووو 🔥 خصم 51%!
مقاس 38.5 لا يفوتك 👟

❌ كان 388 ريال
✅ وصار 190 ريال بس!

🔗 https://ty.gl/xxx

مثال 3:
🎉 صيدة من يوما 🔥
زيت زيتون السوسن 2 لتر 🫒

😱 قبل: 80 ريال
✅ الحين: 40 ريال فقط!

🔗 https://amzn.to/xxx

مثال 4:
😎👌💎 براند Pierre Cardin!
حقيبة نسائية 🇫🇷

❌ 261 ريال
✅ 112 ريال فقط!

🔗 https://ty.gl/xxx

اكتب البوست مباشرة:"""

   try:
       headers = {
           "Authorization": f"Bearer {GROQ_API_KEY}",
           "Content-Type": "application/json"
       }
       data = {
           "model": "llama-3.3-70b-versatile",
           "messages": [
               {"role": "system", "content": "أنت كاتب محتوى سعودي في قنوات تسويق بالعمولة. تكتب بوستات مختصرة، مباشرة، حماسية، قريبة من الناس. ما تحشي بيانات كثيرة."},
               {"role": "user", "content": prompt}
           ],
           "temperature": 0.9,
           "max_tokens": 200
       }
       
       r = requests.post(
           "https://api.groq.com/openai/v1/chat/completions",
           headers=headers,
           json=data,
           timeout=20
       )
       
       if r.status_code == 200:
           result = r.json()
           post = result["choices"][0]["message"]["content"].strip()
           post = post.replace('"', '').replace("'", "").strip()
           
           if original_url and original_url not in post:
               post += f"\n\n🔗 {original_url}"
           
           return post
               
   except Exception as e:
       print(f"Groq error: {e}")
   
   return generate_smart_fallback_post(product_info)


def generate_smart_fallback_post(product_info):
   """Fallback بأسلوب قنوات التسويق السعودية"""
   
   name = product_info['name']
   price = product_info['price']
   old_price = product_info.get('old_price')
   discount = product_info.get('discount_percent', 0)
   brand = product_info.get('brand', '')
   savings = calculate_savings(old_price, price)
   url = product_info.get('url', '')
   
   # نختار hook واحد بس
   hooks = []
   if discount >= 30:
       hooks.append(f"خصم {discount}% 🔥")
   if brand and brand != 'غير معروف':
       hooks.append(f"براند {brand} 💎")
   if product_info.get('is_best_seller'):
       hooks.append("الأكثر مبيعاً ⭐")
   if savings > 100:
       hooks.append(f"وفر {savings} ريال 💰")
   
   hook = random.choice(hooks) if hooks else "عرض ممتاز ✨"
   
   styles = [
       f"""🔥 لا يفوتكم يا جماعة! {hook}
{name}

❌ كان بـ {old_price or '---'} ريال
✅ الحين بـ {price} ريال بس!

🔗 {url}""",
       
       f"""💥 ووووووو! {hook}
{name}

😱 {old_price or '---'} ريال
✅ {price} ريال فقط!

🔗 {url}""",
       
       f"""🎉 صيدة من يوما! {hook}
{name}

❌ قبل: {old_price or '---'} ريال
✅ الحين: {price} ريال بس!

🔗 {url}""",
       
       f"""😎👌 {hook}
{name}

🤩 من {old_price or '---'} لـ {price} ريال!

🔗 {url}""",
       
       f"""🚨 {hook}
{name}

❌ {old_price or '---'} ريال
✅ {price} ريال فقط!

🔗 {url}""",
       
       f"""👀 شفت هذا العرض! {hook}
{name}

😱 {old_price or '---'} ريال
✅ {price} ريال بس!

🔗 {url}""",
   ]
   
   return random.choice(styles)


# ===================================
# 🔧 الكلمات المفتاحية للفئات
# ===================================

CATEGORY_KEYWORDS = {
   "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
   "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
   "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
   "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
   "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}

BRAND_KEYWORDS = {
   "nike": "Nike", "adidas": "Adidas", "puma": "Puma", "reebok": "Reebok",
   "skechers": "Skechers", "new balance": "New Balance", "asics": "ASICS",
   "under armour": "Under Armour",
   "apple": "Apple", "samsung": "Samsung", "huawei": "Huawei", "xiaomi": "Xiaomi",
   "sony": "Sony", "lg": "LG", "philips": "Philips", "bosch": "Bosch",
   "pierre cardin": "Pierre Cardin", "gucci": "Gucci", "prada": "Prada",
   "zara": "Zara", "h&m": "H&M", "shein": "SHEIN", "mango": "Mango",
   "lacoste": "Lacoste", "tommy hilfiger": "Tommy Hilfiger",
   "calvin klein": "Calvin Klein", "armani": "Armani",
   "levi's": "Levi's", "wrangler": "Wrangler", "diesel": "Diesel",
   "ray-ban": "Ray-Ban", "oakley": "Oakley",
   "casio": "Casio", "g-shock": "G-Shock", "seiko": "Seiko",
   "dior": "Dior", "chanel": "Chanel", "versace": "Versace",
   "l'oreal": "L'Oreal", "nivea": "Nivea", "dove": "Dove",
   "oral-b": "Oral-B", "gillette": "Gillette", "braun": "Braun",
   "tefal": "Tefal", "moulinex": "Moulinex", "kenwood": "Kenwood",
   "delonghi": "DeLonghi", "nespresso": "Nespresso",
   "ikea": "IKEA", "home centre": "Home Centre",
   "the north face": "The North Face", "columbia": "Columbia",
   "lego": "LEGO", "barbie": "Barbie", "hasbro": "Hasbro",
   "comfort": "Comfort", "persil": "Persil", "ariel": "Ariel",
   "tide": "Tide", "downy": "Downy",
}

def detect_product_category(product_name):
   name_lower = product_name.lower()
   for category, keywords in CATEGORY_KEYWORDS.items():
       for keyword in keywords:
           if keyword in name_lower:
               return category
   return "general"

def detect_brand(product_name):
   name_lower = product_name.lower()
   for keyword, brand in BRAND_KEYWORDS.items():
       if keyword in name_lower:
           return brand
   return "غير معروف"

def detect_product_gender(product_name):
   name_lower = product_name.lower()
   women_indicators = ['women', 'woman', 'ladies', 'lady', 'female', 'feminine', 'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي', 'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick']
   men_indicators = ['men', 'man', 'male', 'masculine', 'gents', 'gentlemen', 'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة']
   for indicator in women_indicators:
       if indicator in name_lower:
           return 'women'
   for indicator in men_indicators:
       if indicator in name_lower:
           return 'men'
   return 'neutral'

# ===================================
# 🔄 قاموس الترجمة
# ===================================

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
}

def translate_to_arabic(text):
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
   arabic_title = translate_to_arabic(full_title)
   words = arabic_title.split()
   unique_words = []
   for word in words:
       if not unique_words or word.lower() != unique_words[-1].lower():
           unique_words.append(word)
   result = " ".join(unique_words)
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

# ===================================
# 🔧 دوال المساعدة
# ===================================

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

def clean_price(price_text):
   try:
       nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
       if nums:
           num_str = nums[0].replace(",", "")
           num_float = float(num_str)
           num_int = int(num_float)
           return num_int
   except:
       pass
   return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================

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
           
           brand = detect_brand(full_title)
           brand_elem = soup.select_one("#bylineInfo") or soup.select_one(".po-brand .po-break-word")
           if brand_elem:
               brand_text = brand_elem.text.strip()
               if brand_text and brand == 'غير معروف':
                   brand = brand_text
           
           rating = None
           rating_elem = soup.select_one("[data-hook='average-star-rating'] .a-icon-alt") or soup.select_one(".a-icon-alt")
           if rating_elem:
               rating_text = rating_elem.text.strip()
               rating_match = re.search(r'([\d.]+)\s*out of\s*5', rating_text) or re.search(r'([\d.]+)', rating_text)
               if rating_match:
                   rating = rating_match.group(1)
           
           reviews_count = None
           reviews_elem = soup.select_one("[data-hook='total-review-count']") or soup.select_one("a[href*='reviews'] span")
           if reviews_elem:
               reviews_text = reviews_elem.text.strip()
               reviews_match = re.search(r'([\d,]+)', reviews_text)
               if reviews_match:
                   reviews_count = reviews_match.group(1)
           
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
           
           discount_percent = None
           try:
               if old_price and price:
                   old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
                   new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
                   if old_num > new_num:
                       discount_percent = int(((old_num - new_num) / old_num) * 100)
           except:
               pass
           
           is_best_seller = bool(soup.select_one("[data-hook='best-seller-badge']") or soup.select_one(".badge-best-seller"))
           is_amazon_choice = bool(soup.select_one(".ac-badge") or soup.select_one("[data-hook='amazon-choice-badge']"))
           prime = bool(soup.select_one("[aria-label='Prime']") or soup.select_one(".a-icon-prime"))
           
           if price:
               arabic_title = smart_arabic_title(full_title)
               clean_price_val = clean_price(price)
               clean_old_price = clean_price(old_price) if old_price else None
               
               return {
                   'name': arabic_title,
                   'full_name': full_title,
                   'price': clean_price_val,
                   'old_price': clean_old_price,
                   'discount_percent': discount_percent,
                   'image': image,
                   'brand': brand,
                   'rating': rating or 'غير معروف',
                   'reviews_count': reviews_count or 'غير معروف',
                   'is_best_seller': is_best_seller,
                   'is_amazon_choice': is_amazon_choice,
                   'prime': prime,
                   'category': detect_product_category(full_title),
                   'gender': detect_product_gender(full_title),
                   'url': f"https://www.amazon.sa/dp/{asin}"
               }
               
       except Exception as e:
           print(f"Attempt {attempt + 1} failed: {e}")
           continue
   return None

# ===================================
# ✨ معالجة الرسائل
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

       wait = bot.reply_to(msg, "⏳ جاري التحليل الذكي...")

       product = get_product(asin)

       if not product:
           bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
           continue

       product['url'] = original_url
       
       post = generate_ai_post(product)

       try:
           if product.get('image'):
               bot.send_photo(msg.chat.id, product['image'], caption=post)
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

print("🤖 البوت يعمل بالذكاء الاصطناعي...")
bot.infinity_polling()
    """
    
    # نختار معلومة واحدة بس اللي تخدم التسويق
    hook = ""
    if product_info.get('discount_percent') and product_info['discount_percent'] >= 30:
        hook = f"خصم {product_info['discount_percent']}%"
    elif product_info.get('is_best_seller'):
        hook = "الأكثر مبيعاً"
    elif product_info.get('brand') and product_info['brand'] != 'غير معروف':
        hook = f"براند {product_info['brand']}"
    elif product_info.get('prime'):
        hook = "توصيل Prime"
    
    savings = calculate_savings(product_info.get('old_price'), product_info['price'])
    
    original_url = product_info.get('url', '')
    
    prompt = f"""أنت كاتب محتوى سعودي في قناة تسويق بالعمولة (زي قناة "أكسب زون" و"نص السعر").
اكتب بوست تسويقي للمنتج التالي.

🔹 الأسلوب المطلوب:
- مختصر جداً ومباشر (4-6 أسطر كحد أقصى)
- حماسي وسعودي وقريب من الناس
- ما تحشي بيانات كثيرة! معلومة واحدة بس في أول سطر
- التنسيق:
  السطر 1: صيحة أو جملة حماسية مختصرة (ممكن تذكر الخصم أو البراند)
  السطر 2: اسم المنتج مختصر
  السطر 3: السعر القديم
  السطر 4: السعر الجديد
  السطر 5: الرابط
- لا فواصل كثيرة، سطر واحد بين كل جزء
- استخدم إيموجي بسيط

🔹 بيانات المنتج:
- الاسم: {product_info['name']}
- السعر الحالي: {product_info['price']} ريال
- السعر القديم: {product_info.get('old_price', 'غير متوفر')} ريال
- المعلومة المختارة: {hook if hook else 'لا يوجد'}
- التوفير: {savings} ريال
- الرابط: {original_url}

🔹 أمثلة للأسلوب المطلوب:

مثال 1:
🔥 لا يفوتكم يا جماعة!
Puma حذاء رياضي 👟
❌ كان بـ 388 ريال
✅ الحين بـ 190 ريال بس!
🔗 https://ty.gl/xxx

مثال 2:
💥 ووووووو 🔥 خصم 51%!
مقاس 38.5 لا يفوتك 👟
❌ كان 388 ريال
✅ وصار 190 ريال بس!
🔗 https://ty.gl/xxx

مثال 3:
🎉 صيدة من يوما 🔥
زيت زيتون السوسن 2 لتر 🫒
😱 قبل: 80 ريال
✅ الحين: 40 ريال فقط!
🔗 https://amzn.to/xxx

مثال 4:
😎👌💎 براند Pierre Cardin!
حقيبة نسائية 🇫🇷
❌ 261 ريال
✅ 112 ريال فقط!
🔗 https://ty.gl/xxx

اكتب البوست مباشرة:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت كاتب محتوى سعودي في قنوات تسويق بالعمولة. تكتب بوستات مختصرة، مباشرة، حماسية، قريبة من الناس. ما تحشي بيانات كثيرة."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 200
        }
        
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )
        
        if r.status_code == 200:
            result = r.json()
            post = result["choices"][0]["message"]["content"].strip()
            post = post.replace('"', '').replace("'", "").strip()
            
            if original_url and original_url not in post:
                post += f"\n🔗 {original_url}"
            
            return post
                
    except Exception as e:
        print(f"Groq error: {e}")
    
    return generate_smart_fallback_post(product_info)


def generate_smart_fallback_post(product_info):
    """Fallback بأسلوب قنوات التسويق السعودية"""
    
    name = product_info['name']
    price = product_info['price']
    old_price = product_info.get('old_price')
    discount = product_info.get('discount_percent', 0)
    brand = product_info.get('brand', '')
    savings = calculate_savings(old_price, price)
    url = product_info.get('url', '')
    
    # نختار hook واحد بس
    hooks = []
    if discount >= 30:
        hooks.append(f"خصم {discount}% 🔥")
    if brand and brand != 'غير معروف':
        hooks.append(f"براند {brand} 💎")
    if product_info.get('is_best_seller'):
        hooks.append("الأكثر مبيعاً ⭐")
    if savings > 100:
        hooks.append(f"وفر {savings} ريال 💰")
    
    hook = random.choice(hooks) if hooks else "عرض ممتاز ✨"
    
    styles = [
        f"""🔥 لا يفوتكم يا جماعة! {hook}
{name}
❌ كان بـ {old_price or '---'} ريال
✅ الحين بـ {price} ريال بس!
🔗 {url}""",
        
        f"""💥 ووووووو! {hook}
{name}
😱 {old_price or '---'} ريال
✅ {price} ريال فقط!
🔗 {url}""",
        
        f"""🎉 صيدة من يوما! {hook}
{name}
❌ قبل: {old_price or '---'} ريال
✅ الحين: {price} ريال بس!
🔗 {url}""",
        
        f"""😎👌 {hook}
{name}
🤩 من {old_price or '---'} لـ {price} ريال!
🔗 {url}""",
        
        f"""🚨 {hook}
{name}
❌ {old_price or '---'} ريال
✅ {price} ريال فقط!
🔗 {url}""",
        
        f"""👀 شفت هذا العرض! {hook}
{name}
😱 {old_price or '---'} ريال
✅ {price} ريال بس!
🔗 {url}""",
    ]
    
    return random.choice(styles)


# ===================================
# 🔧 الكلمات المفتاحية للفئات
# ===================================

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}

BRAND_KEYWORDS = {
    "nike": "Nike", "adidas": "Adidas", "puma": "Puma", "reebok": "Reebok",
    "skechers": "Skechers", "new balance": "New Balance", "asics": "ASICS",
    "under armour": "Under Armour",
    "apple": "Apple", "samsung": "Samsung", "huawei": "Huawei", "xiaomi": "Xiaomi",
    "sony": "Sony", "lg": "LG", "philips": "Philips", "bosch": "Bosch",
    "pierre cardin": "Pierre Cardin", "gucci": "Gucci", "prada": "Prada",
    "zara": "Zara", "h&m": "H&M", "shein": "SHEIN", "mango": "Mango",
    "lacoste": "Lacoste", "tommy hilfiger": "Tommy Hilfiger",
    "calvin klein": "Calvin Klein", "armani": "Armani",
    "levi's": "Levi's", "wrangler": "Wrangler", "diesel": "Diesel",
    "ray-ban": "Ray-Ban", "oakley": "Oakley",
    "casio": "Casio", "g-shock": "G-Shock", "seiko": "Seiko",
    "dior": "Dior", "chanel": "Chanel", "versace": "Versace",
    "l'oreal": "L'Oreal", "nivea": "Nivea", "dove": "Dove",
    "oral-b": "Oral-B", "gillette": "Gillette", "braun": "Braun",
    "tefal": "Tefal", "moulinex": "Moulinex", "kenwood": "Kenwood",
    "delonghi": "DeLonghi", "nespresso": "Nespresso",
    "ikea": "IKEA", "home centre": "Home Centre",
    "the north face": "The North Face", "columbia": "Columbia",
    "lego": "LEGO", "barbie": "Barbie", "hasbro": "Hasbro",
    "comfort": "Comfort", "persil": "Persil", "ariel": "Ariel",
    "tide": "Tide", "downy": "Downy",
}

def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"

def detect_brand(product_name):
    name_lower = product_name.lower()
    for keyword, brand in BRAND_KEYWORDS.items():
        if keyword in name_lower:
            return brand
    return "غير معروف"

def detect_product_gender(product_name):
    name_lower = product_name.lower()
    women_indicators = ['women', 'woman', 'ladies', 'lady', 'female', 'feminine', 'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي', 'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick']
    men_indicators = ['men', 'man', 'male', 'masculine', 'gents', 'gentlemen', 'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة']
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    return 'neutral'

# ===================================
# 🔄 قاموس الترجمة
# ===================================

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
}

def translate_to_arabic(text):
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
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
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

# ===================================
# 🔧 دوال المساعدة
# ===================================

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

def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            num_float = float(num_str)
            num_int = int(num_float)
            return num_int
    except:
        pass
    return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================

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
            
            brand = detect_brand(full_title)
            brand_elem = soup.select_one("#bylineInfo") or soup.select_one(".po-brand .po-break-word")
            if brand_elem:
                brand_text = brand_elem.text.strip()
                if brand_text and brand == 'غير معروف':
                    brand = brand_text
            
            rating = None
            rating_elem = soup.select_one("[data-hook='average-star-rating'] .a-icon-alt") or soup.select_one(".a-icon-alt")
            if rating_elem:
                rating_text = rating_elem.text.strip()
                rating_match = re.search(r'([\d.]+)\s*out of\s*5', rating_text) or re.search(r'([\d.]+)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
            
            reviews_count = None
            reviews_elem = soup.select_one("[data-hook='total-review-count']") or soup.select_one("a[href*='reviews'] span")
            if reviews_elem:
                reviews_text = reviews_elem.text.strip()
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    reviews_count = reviews_match.group(1)
            
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
            
            discount_percent = None
            try:
                if old_price and price:
                    old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
                    new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
                    if old_num > new_num:
                        discount_percent = int(((old_num - new_num) / old_num) * 100)
            except:
                pass
            
            is_best_seller = bool(soup.select_one("[data-hook='best-seller-badge']") or soup.select_one(".badge-best-seller"))
            is_amazon_choice = bool(soup.select_one(".ac-badge") or soup.select_one("[data-hook='amazon-choice-badge']"))
            prime = bool(soup.select_one("[aria-label='Prime']") or soup.select_one(".a-icon-prime"))
            
            if price:
                arabic_title = smart_arabic_title(full_title)
                clean_price_val = clean_price(price)
                clean_old_price = clean_price(old_price) if old_price else None
                
                return {
                    'name': arabic_title,
                    'full_name': full_title,
                    'price': clean_price_val,
                    'old_price': clean_old_price,
                    'discount_percent': discount_percent,
                    'image': image,
                    'brand': brand,
                    'rating': rating or 'غير معروف',
                    'reviews_count': reviews_count or 'غير معروف',
                    'is_best_seller': is_best_seller,
                    'is_amazon_choice': is_amazon_choice,
                    'prime': prime,
                    'category': detect_product_category(full_title),
                    'gender': detect_product_gender(full_title),
                    'url': f"https://www.amazon.sa/dp/{asin}"
                }
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    return None

# ===================================
# ✨ معالجة الرسائل
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

        wait = bot.reply_to(msg, "⏳ جاري التحليل الذكي...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        product['url'] = original_url
        
        post = generate_ai_post(product)

        try:
            if product.get('image'):
                bot.send_photo(msg.chat.id, product['image'], caption=post)
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

print("🤖 البوت يعمل بالذكاء الاصطناعي...")
bot.infinity_polling()
def generate_ai_post(product_info):
    """
    توليد بوست بأسلوب فانسي وسعودي
    يختار بذكاء بيانات قليلة تخدم التسويق فقط
    """
    
    # نجمع البيانات ونختار 1-2 بس اللي تخدم التسويق
    data_points = []
    
    if product_info.get('brand') and product_info['brand'] != 'غير معروف':
        data_points.append(f"براند: {product_info['brand']}")
    if product_info.get('rating') and product_info['rating'] != 'غير معروف':
        data_points.append(f"تقييم {product_info['rating']}/5 ⭐")
    if product_info.get('discount_percent') and product_info['discount_percent'] > 0:
        data_points.append(f"خصم {product_info['discount_percent']}%")
    if product_info.get('is_best_seller'):
        data_points.append("الأكثر مبيعاً 🔥")
    if product_info.get('is_amazon_choice'):
        data_points.append("Amazon's Choice ✅")
    if product_info.get('prime'):
        data_points.append("Prime 🚚")
    
    savings = calculate_savings(product_info.get('old_price'), product_info['price'])
    if savings > 0:
        data_points.append(f"وفر {savings} ريال")
    
    # نختار بذكاء 1-2 بيانات بس
    selected = random.sample(data_points, min(2, len(data_points))) if data_points else []
    highlight_text = " | ".join(selected)
    
    original_url = product_info.get('url', '')
    
    prompt = f"""أنت كاتب محتوى سعودي محترف في قنوات تليجرام للتسويق بالعمولة.
اكتب بوست تسويقي للمنتج التالي.

🔹 قواعد مهمة:
- أسلوب فانسي، سعودي، مرتاح، قريب من الناس
- ما تحشي البوست ببيانات كثيرة! اختار بذكاء معلومة واحدة أو اثنتين بس اللي تخدم التسويق (زي خصم كبير، براند معروف، أو الأكثر مبيعاً)
- التنسيط:
  السطر 1-2: جملة تسويقية حماسية مختصرة (ممكن تذكر فيها المعلومة المختارة بشكل طبيعي)
  سطر فارغ
  السطر 3: اسم المنتج مختصر مع إيموجي
  سطر فارغ
  السطر 4: السعر القديم لوحده
  السطر 5: السعر الجديد لوحده
  سطر فارغ
  السطر 6: الرابط فقط
- فاصل سطر واحد فقط بين كل جزء
- لا قوائم، لا نقاط، جمل متصلة وعفوية

🔹 بيانات المنتج:
- الاسم: {product_info['name']}
- السعر الحالي: {product_info['price']} ريال
- السعر القديم: {product_info.get('old_price', 'غير متوفر')} ريال
- المعلومات المتاحة (اختار منها بس اللي تخدم): {highlight_text if highlight_text else 'لا يوجد'}
- الرابط: {original_url}

🔹 أمثلة:

مثال 1:
🔥 لا يفوتكم يا جماعة!

Puma حذاء رياضي 👟

❌ كان بـ 388 ريال
✅ الحين بـ 190 ريال بس!

🔗 https://ty.gl/xxx

مثال 2:
💥 ووووووو 🔥 خصم 51% مجنون!

مقاس 38.5 لا يفوتك 👟

❌ كان 388 ريال
✅ وصار 190 ريال بس!

🔗 https://ty.gl/xxx

مثال 3:
🎉 صيدة من يوما 🔥

زيت زيتون السوسن 2 لتر 🫒

😱 قبل: 80 ريال
✅ الحين: 40 ريال فقط!

🔗 https://amzn.to/xxx

مثال 4:
😎👌💎 براند Pierre Cardin يا جماعة!

حقيبة نسائية 🇫🇷

❌ 261 ريال
✅ 112 ريال فقط!

🔗 https://ty.gl/xxx

اكتب البوست مباشرة:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت كاتب محتوى سعودي محترف في قنوات تسويق بالعمولة. تكتب بوستات مختصرة، فانسيّة، سعودية، مرتاحة. ما تحشي البيانات، تختار بذكاء اللي يخدم التسويق فقط."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.95,
            "max_tokens": 250
        }
        
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )
        
        if r.status_code == 200:
            result = r.json()
            post = result["choices"][0]["message"]["content"].strip()
            post = post.replace('"', '').replace("'", "").strip()
            
            if original_url and original_url not in post:
                post += f"\n\n🔗 {original_url}"
            
            return post
                
    except Exception as e:
        print(f"Groq error: {e}")
    
    return generate_smart_fallback_post(product_info)


def generate_smart_fallback_post(product_info):
    """توليد بوست عشوائي - فانسي وبسيط يختار بيانات قليلة"""
    
    name = product_info['name']
    price = product_info['price']
    old_price = product_info.get('old_price')
    discount = product_info.get('discount_percent', 0)
    brand = product_info.get('brand', '')
    savings = calculate_savings(old_price, price)
    url = product_info.get('url', '')
    
    # نختار بذكاء 0-2 معلومة بس تخدم التسويق
    extras = []
    if brand and brand != 'غير معروف' and random.random() > 0.5:
        extras.append(f"براند {brand}")
    if discount > 30 and random.random() > 0.3:
        extras.append(f"خصم {discount}%")
    if product_info.get('is_best_seller') and random.random() > 0.5:
        extras.append("الأكثر مبيعاً 🔥")
    if product_info.get('prime') and random.random() > 0.6:
        extras.append("Prime 🚚")
    if savings > 100 and random.random() > 0.4:
        extras.append(f"وفر {savings} ريال")
    
    # نختار واحدة بس عشوائية
    extra_line = random.choice(extras) if extras else ""
    
    styles = [
        lambda: f"""🔥😱 لا يفوتكم يا جماعة!{f" {extra_line}" if extra_line else ""}

{name}

❌ كان بـ {old_price or '---'} ريال
✅ الحين بـ {price} ريال بس!

🔗 {url}""",
        
        lambda: f"""💥🔥 ووووووو!{f" {extra_line}" if extra_line else ""}

{name}

😱 {old_price or '---'} ريال
✅ {price} ريال فقط!

🔗 {url}""",
        
        lambda: f"""🎉✨ صيدة من يوما 🔥{f" {extra_line}" if extra_line else ""}

{name}

❌ قبل: {old_price or '---'} ريال
✅ الحين: {price} ريال بس!

🔗 {url}""",
        
        lambda: f"""😎👌💎{f" {extra_line}" if extra_line else ""}

{name}

🤩 من {old_price or '---'} لـ {price} ريال!

🔗 {url}""",
        
        lambda: f"""🚨⏰🔥
لا يفوتك يا جماعة!{f" {extra_line}" if extra_line else ""}

{name}

❌ {old_price or '---'} ريال
✅ {price} ريال فقط!

🔗 {url}""",
        
        lambda: f"""👀🔥 شفت هذا العرض!{f" {extra_line}" if extra_line else ""}

{name}

😱 {old_price or '---'} ريال
✅ {price} ريال بس!

🔗 {url}""",
        
        lambda: f"""🔥💎✨{f" {extra_line}" if extra_line else ""}

{name}

❌ كان {old_price or '---'} ريال
✅ وصار {price} ريال! 🤩

🔗 {url}""",
        
        lambda: f"""⭐✨ يستاهل التجربة!{f" {extra_line}" if extra_line else ""}

{name}

❌ {old_price or '---'} ريال
✅ {price} ريال فقط!

🔗 {url}""",
    ]
    
    return random.choice(styles)()


# ===================================
# 🔧 الكلمات المفتاحية للفئات
# ===================================

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}

BRAND_KEYWORDS = {
    "nike": "Nike", "adidas": "Adidas", "puma": "Puma", "reebok": "Reebok",
    "skechers": "Skechers", "new balance": "New Balance", "asics": "ASICS",
    "under armour": "Under Armour",
    "apple": "Apple", "samsung": "Samsung", "huawei": "Huawei", "xiaomi": "Xiaomi",
    "sony": "Sony", "lg": "LG", "philips": "Philips", "bosch": "Bosch",
    "pierre cardin": "Pierre Cardin", "gucci": "Gucci", "prada": "Prada",
    "zara": "Zara", "h&m": "H&M", "shein": "SHEIN", "mango": "Mango",
    "lacoste": "Lacoste", "tommy hilfiger": "Tommy Hilfiger",
    "calvin klein": "Calvin Klein", "armani": "Armani",
    "levi's": "Levi's", "wrangler": "Wrangler", "diesel": "Diesel",
    "ray-ban": "Ray-Ban", "oakley": "Oakley",
    "casio": "Casio", "g-shock": "G-Shock", "seiko": "Seiko",
    "dior": "Dior", "chanel": "Chanel", "versace": "Versace",
    "l'oreal": "L'Oreal", "nivea": "Nivea", "dove": "Dove",
    "oral-b": "Oral-B", "gillette": "Gillette", "braun": "Braun",
    "tefal": "Tefal", "moulinex": "Moulinex", "kenwood": "Kenwood",
    "delonghi": "DeLonghi", "nespresso": "Nespresso",
    "ikea": "IKEA", "home centre": "Home Centre",
    "the north face": "The North Face", "columbia": "Columbia",
    "lego": "LEGO", "barbie": "Barbie", "hasbro": "Hasbro",
    "comfort": "Comfort", "persil": "Persil", "ariel": "Ariel",
    "tide": "Tide", "downy": "Downy",
}

def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"

def detect_brand(product_name):
    name_lower = product_name.lower()
    for keyword, brand in BRAND_KEYWORDS.items():
        if keyword in name_lower:
            return brand
    return "غير معروف"

def detect_product_gender(product_name):
    name_lower = product_name.lower()
    women_indicators = ['women', 'woman', 'ladies', 'lady', 'female', 'feminine', 'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي', 'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick']
    men_indicators = ['men', 'man', 'male', 'masculine', 'gents', 'gentlemen', 'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة']
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    return 'neutral'

# ===================================
# 🔄 قاموس الترجمة
# ===================================

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
}

def translate_to_arabic(text):
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
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
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

# ===================================
# 🔧 دوال المساعدة
# ===================================

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

def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            num_float = float(num_str)
            num_int = int(num_float)
            return num_int
    except:
        pass
    return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================

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
            
            brand = detect_brand(full_title)
            brand_elem = soup.select_one("#bylineInfo") or soup.select_one(".po-brand .po-break-word")
            if brand_elem:
                brand_text = brand_elem.text.strip()
                if brand_text and brand == 'غير معروف':
                    brand = brand_text
            
            rating = None
            rating_elem = soup.select_one("[data-hook='average-star-rating'] .a-icon-alt") or soup.select_one(".a-icon-alt")
            if rating_elem:
                rating_text = rating_elem.text.strip()
                rating_match = re.search(r'([\d.]+)\s*out of\s*5', rating_text) or re.search(r'([\d.]+)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
            
            reviews_count = None
            reviews_elem = soup.select_one("[data-hook='total-review-count']") or soup.select_one("a[href*='reviews'] span")
            if reviews_elem:
                reviews_text = reviews_elem.text.strip()
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    reviews_count = reviews_match.group(1)
            
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
            
            discount_percent = None
            try:
                if old_price and price:
                    old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
                    new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
                    if old_num > new_num:
                        discount_percent = int(((old_num - new_num) / old_num) * 100)
            except:
                pass
            
            is_best_seller = bool(soup.select_one("[data-hook='best-seller-badge']") or soup.select_one(".badge-best-seller"))
            is_amazon_choice = bool(soup.select_one(".ac-badge") or soup.select_one("[data-hook='amazon-choice-badge']"))
            prime = bool(soup.select_one("[aria-label='Prime']") or soup.select_one(".a-icon-prime"))
            
            if price:
                arabic_title = smart_arabic_title(full_title)
                clean_price_val = clean_price(price)
                clean_old_price = clean_price(old_price) if old_price else None
                
                return {
                    'name': arabic_title,
                    'full_name': full_title,
                    'price': clean_price_val,
                    'old_price': clean_old_price,
                    'discount_percent': discount_percent,
                    'image': image,
                    'brand': brand,
                    'rating': rating or 'غير معروف',
                    'reviews_count': reviews_count or 'غير معروف',
                    'is_best_seller': is_best_seller,
                    'is_amazon_choice': is_amazon_choice,
                    'prime': prime,
                    'category': detect_product_category(full_title),
                    'gender': detect_product_gender(full_title),
                    'url': f"https://www.amazon.sa/dp/{asin}"
                }
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    return None

# ===================================
# ✨ معالجة الرسائل
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

        wait = bot.reply_to(msg, "⏳ جاري التحليل الذكي...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        product['url'] = original_url
        
        post = generate_ai_post(product)

        try:
            if product.get('image'):
                bot.send_photo(msg.chat.id, product['image'], caption=post)
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

print("🤖 البوت يعمل بالذكاء الاصطناعي...")
bot.infinity_polling()
