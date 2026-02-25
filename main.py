import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import random
import re
import time

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاموس ترجمة المنتجات ---
PRODUCT_TRANSLATIONS = {
    # ملابس
    "shoe": "حذاء", "shoes": "حذاء", "sneaker": "حذاء رياضي", "sneakers": "حذاء رياضي",
    "boot": "جزمة", "boots": "جزمة", "sandal": "صندل", "sandals": "صندل",
    "slipper": "شبشب", "slippers": "شبشب",
    "pant": "بنطلون", "pants": "بنطلون", "trouser": "بنطلون", "trousers": "بنطلون",
    "jean": "جينز", "jeans": "جينز",
    "shirt": "قميص", "shirts": "قميص", "t-shirt": "تيشيرت", "tshirt": "تيشيرت",
    "dress": "فستان", "dresses": "فستان",
    "jacket": "جاكيت", "jackets": "جاكيت", "coat": "معطف", "coats": "معطف",
    "sweater": "سترة", "sweaters": "سترة", "hoodie": "هودي", "hoodies": "هودي",
    "sweatpant": "بنطلون رياضي", "sweatpants": "بنطلون رياضي",
    "short": "شورت", "shorts": "شورت",
    "sock": "جورب", "socks": "جورب", "stocking": "شراب", "stockings": "شراب",
    "underwear": "ملابس داخلية", "lingerie": "لانجري",
    "pajama": "بيجاما", "pajamas": "بيجاما", "robe": "روب", "robes": "روب",
    "scarf": "وشاح", "scarves": "وشاح", "shawl": "شال", "shawls": "شال",
    "glove": "قفاز", "gloves": "قفاز", "hat": "قبعة", "hats": "قبعة", "cap": "طاقية", "caps": "طاقية",
    "belt": "حزام", "belts": "حزام", "tie": "ربطة عنق", "ties": "ربطة عنق",
    "suit": "بدلة", "suits": "بدلة", "uniform": "زي موحد", "uniforms": "زي موحد",
    "abaya": "عباية", "thobe": "ثوب", "shmagh": "شماغ", "ghutra": "غترة",
    
    # إكسسوارات
    "watch": "ساعة", "watches": "ساعة",
    "jewelry": "مجوهرات", "ring": "خاتم", "rings": "خاتم",
    "necklace": "عقد", "necklaces": "عقد", "bracelet": "سوار", "bracelets": "سوار",
    "earring": "حلق", "earrings": "حلق",
    "sunglass": "نظارة شمسية", "sunglasses": "نظارة شمسية",
    "glass": "نظارة", "glasses": "نظارة", "eyeglass": "نظارة طبية", "eyeglasses": "نظارة طبية",
    "wallet": "محفظة", "wallets": "محفظة", "purse": "شنطة يد", "purses": "شنطة يد",
    "bag": "حقيبة", "bags": "حقيبة", "backpack": "شنطة ظهر", "backpacks": "شنطة ظهر",
    "suitcase": "حقيبة سفر", "suitcases": "حقيبة سفر", "luggage": "أمتعة",
    
    # إلكترونيات
    "phone": "هاتف", "phones": "هاتف", "smartphone": "هاتف ذكي", "smartphones": "هاتف ذكي",
    "iphone": "آيفون", "samsung": "سامسونج", "xiaomi": "شاومي", "huawei": "هواوي",
    "laptop": "لابتوب", "laptops": "لابتوب", "computer": "كمبيوتر", "computers": "كمبيوتر",
    "tablet": "تابلت", "tablets": "تابلت", "ipad": "آيباد",
    "headphone": "سماعة رأس", "headphones": "سماعة رأس", "earphone": "سماعة أذن", "earphones": "سماعة أذن",
    "earbud": "سماعة لاسلكية", "earbuds": "سماعة لاسلكية", "airpod": "آيربودز", "airpods": "آيربودز",
    "speaker": "مكبر صوت", "speakers": "مكبر صوت", "bluetooth speaker": "سماعة بلوتوث",
    "charger": "شاحن", "chargers": "شاحن", "cable": "كيبل", "cables": "كيبل",
    "power bank": "باور بانك", "battery": "بطارية", "batteries": "بطارية",
    "mouse": "ماوس", "keyboard": "كيبورد", "monitor": "شاشة", "monitors": "شاشة",
    "camera": "كاميرا", "cameras": "كاميرا", "webcam": "كاميرا ويب",
    "printer": "طابعة", "printers": "طابعة", "scanner": "ماسح", "scanners": "ماسح",
    "router": "راوتر", "routers": "راوتر", "modem": "مودم", "modems": "مودم",
    "hard drive": "هارد ديسك", "harddisk": "هارد ديسك", "ssd": "SSD",
    "usb": "يو اس بي", "flash drive": "فلاش ميموري", "memory card": "كرت ميموري",
    "game": "لعبة", "games": "لعبة", "console": "جهاز ألعاب", "consoles": "جهاز ألعاب",
    "controller": "يد تحكم", "controllers": "يد تحكم", "playstation": "بلايستيشن", "xbox": "إكس بوكس",
    
    # منزل ومطبخ
    "furniture": "أثاث", "sofa": "كنبة", "sofas": "كنبة", "couch": "كنبة", "couches": "كنبة",
    "bed": "سرير", "beds": "سرير", "mattress": "مرتبة", "mattresses": "مرتبة",
    "pillow": "مخدة", "pillows": "مخدة", "blanket": "بطانية", "blankets": "بطانية",
    "sheet": "شرشف", "sheets": "شرشف", "towel": "منشفة", "towels": "منشفة",
    "curtain": "ستارة", "curtains": "ستارة", "carpet": "سجادة", "carpets": "سجادة", "rug": "سجادة", "rugs": "سجادة",
    "lamp": "مصباح", "lamps": "مصباح", "light": "إضاءة", "lights": "إضاءة",
    "mirror": "مرآة", "mirrors": "مرآة", "clock": "ساعة حائط", "clocks": "ساعة حائط",
    "vase": "مزهرية", "vases": "مزهرية", "frame": "براويز", "frames": "براويز",
    "pot": "قدر", "pots": "قدر", "pan": "مقلاة", "pans": "مقلاة",
    "plate": "صحن", "plates": "صحن", "bowl": "وعاء", "bowls": "وعاء",
    "cup": "كوب", "cups": "كوب", "mug": "مج", "mugs": "مج",
    "glass": "كاس", "glasses": "كاس", "fork": "شوكة", "forks": "شوكة",
    "spoon": "ملعقة", "spoons": "ملعقة", "knife": "سكين", "knives": "سكين",
    "blender": "خلاط", "blenders": "خلاط", "mixer": "عجانة", "mixers": "عجانة",
    "oven": "فرن", "ovens": "فرن", "microwave": "مايكرويف", "microwaves": "مايكرويف",
    "fridge": "ثلاجة", "fridges": "ثلاجة", "refrigerator": "ثلاجة", "refrigerators": "ثلاجة",
    "washer": "غسالة", "washers": "غسالة", "dryer": "نشافة", "dryers": "نشافة",
    "vacuum": "مكنسة", "vacuums": "مكنسة", "iron": "مكواة", "irons": "مكواة",
    "fan": "مروحة", "fans": "مروحة", "ac": "مكيف", "air conditioner": "مكيف",
    "heater": "دفاية", "heaters": "دفاية",
    
    # جمال وعناية
    "perfume": "عطر", "perfumes": "عطر", "fragrance": "عطر", "fragrances": "عطر",
    "cream": "كريم", "creams": "كريم", "lotion": "لوشن", "lotions": "لوشن",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون", "soaps": "صابون",
    "toothpaste": "معجون أسنان", "toothbrush": "فرشاة أسنان",
    "makeup": "مكياج", "lipstick": "أحمر شفاه", "mascara": "ماسكارا",
    "hair dryer": "سشوار", "straightener": "مملس شعر", "curler": "مكواة تجعيد",
    
    # رياضة
    "gym": "جيم", "fitness": "لياقة", "yoga": "يوغا", "mat": "حصيرة",
    "dumbbell": "دمبل", "dumbbells": "دمبل", "treadmill": "سير كهربائي",
    "ball": "كرة", "balls": "كرة", "racket": "مضرب", "rackets": "مضرب",
    "bicycle": "دراجة", "bicycles": "دراجة", "bike": "دراجة", "bikes": "دراجة",
    
    # أطفال
    "toy": "لعبة", "toys": "لعبة", "doll": "دمية", "dolls": "دمية",
    "stroller": "عربة أطفال", "strollers": "عربة أطفال",
    "car seat": "كرسي سيارة", "diaper": "حفاض", "diapers": "حفاض",
    "baby": "بيبي", "kids": "أطفال", "children": "أطفال",
    
    # أخرى
    "book": "كتاب", "books": "كتاب", "notebook": "دفتر", "notebooks": "دفتر",
    "pen": "قلم", "pens": "قلم", "pencil": "قلم رصاص", "pencils": "قلم رصاص",
    "bag": "شنطة", "backpack": "شنطة ظهر", "suitcase": "حقيبة سفر",
    "umbrella": "مظلة", "umbrellas": "مظلة",
    "tool": "أداة", "tools": "أدوات", "screwdriver": "مفك", "hammer": "مطرقة",
    "paint": "دهان", "brush": "فرشاة", "brushes": "فرشاة",
}

# --- الجمل السعودية ---
SAUDI_TEMPLATES = [
    "تخيل يا عزيزي أن {title} يكون بسعر كذا! 🤯",
    "أبطالنا أصحاب الذوق {title} وصل! 🦸‍♂️",
    "هلا بالزين كله {title} وصل! 🤍",
    "🔴 آخر حبة بالمخزون {title}!",
    "🏃‍♂️ سارع قبل ما ينتهي {title}!",
    "💎 جودة تفوق التوقع {title}!",
    "❤️ من القلب {title} يستاهل!",
    "🎉 مفاجأة سارة {title} وصل!",
]

PRICE_FORMATS = [
    "🔥 بـ {price} ريال فقط!",
    "💰 {price} ريال",
    "⚡ {price} ريال بس!",
]

@app.route('/')
def home():
    return "✅ Bot Active"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def extract_asin(url):
    """استخراج ASIN"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'product/([A-Z0-9]{10})',
        r'amazon\..*/([A-Z0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    if 'amzn.to' in url or 'amzn.eu' in url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            final_url = response.url
            for pattern in patterns:
                match = re.search(pattern, final_url, re.IGNORECASE)
                if match:
                    return match.group(1).upper()
        except:
            pass
    
    return None

def translate_product(title):
    """ترجمة اسم المنتج للعربي"""
    # استخراج البراند (أول كلمة)
    words = title.split()
    brand = words[0] if words else ""
    
    # البحث عن كلمات للترجمة
    translated_words = [brand]  # البراند يبقى إنجليزي
    translated = False
    
    title_lower = title.lower()
    
    for eng, ar in PRODUCT_TRANSLATIONS.items():
        if eng in title_lower:
            translated_words.append(ar)
            translated = True
            break
    
    # إذا ما لقينا ترجمة محددة، نضيف وصف عام
    if not translated:
        # كلمات عامة
        if any(word in title_lower for word in ['men', 'men\'s', 'man']):
            translated_words.append("رجالي")
        elif any(word in title_lower for word in ['women', 'women\'s', 'woman', 'lady', 'ladies']):
            translated_words.append("نسائي")
        elif any(word in title_lower for word in ['kid', 'kids', 'child', 'children', 'baby']):
            translated_words.append("أطفال")
        elif any(word in title_lower for word in ['adult']):
            translated_words.append("بالغين")
        
        if any(word in title_lower for word in ['sport', 'sports', 'athletic', 'running']):
            translated_words.append("رياضي")
        elif any(word in title_lower for word in ['casual', 'daily']):
            translated_words.append("كاجوال")
        elif any(word in title_lower for word in ['formal', 'classic']):
            translated_words.append("كلاسيك")
    
    # دمج الكلمات
    result = " ".join(translated_words)
    
    # تنظيف
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'[,\.]', '', result)
    
    return result.strip()

def get_product_scraperapi(asin):
    """ScraperAPI"""
    amazon_url = f"https://www.amazon.sa/dp/{asin}"
    scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={amazon_url}&country_code=sa"
    
    try:
        response = requests.get(scraper_url, timeout=20)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_elem = soup.select_one('#productTitle')
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        title = re.sub(r'\s+', ' ', title)
        
        price = None
        price_selectors = [
            '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '.a-price .a-offscreen',
            '.a-price-whole',
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    price = price_match.group()
                    break
        
        if not price:
            return None
        
        image = None
        img_elem = soup.select_one('#landingImage')
        if img_elem:
            image = img_elem.get('data-old-hires') or img_elem.get('src')
            if image:
                image = image.replace('._SL500_', '._SL1500_')
        
        # ترجمة العنوان
        arabic_title = translate_product(title)
        
        return {
            'original_title': title,
            'title': arabic_title,
            'price': price,
            'image': image,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None

def generate_post(product):
    """توليد المنشور"""
    title = product['title']  # الآن بالعربي
    price = product['price']
    url = product['url']
    
    template = random.choice(SAUDI_TEMPLATES)
    main_text = template.format(title=title)
    price_text = random.choice(PRICE_FORMATS).format(price=price)
    
    return f"{main_text}\n\n{price_text}\n\nالرابط: {url}"

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    
    urls = re.findall(r'https?://\S+', text)
    
    if not urls:
        bot.reply_to(message, "👋 أرسلي رابط أمازون")
        return
    
    for url in urls:
        if "amazon" not in url.lower() and "amzn" not in url.lower():
            continue
        
        wait_msg = bot.reply_to(message, "⏳ جاري القراءة...")
        
        asin = extract_asin(url)
        if not asin:
            bot.edit_message_text("❌ رابط غير صحيح", chat_id, wait_msg.message_id)
            continue
        
        product = get_product_scraperapi(asin)
        
        if not product:
            bot.edit_message_text(
                "❌ ما قدرت أقرأ المنتج\n\nجربي رابط مباشر من amazon.sa",
                chat_id,
                wait_msg.message_id
            )
            continue
        
        # الرد في نفس الشات
        try:
            post = generate_post(product)
            
            if product.get('image'):
                bot.send_photo(chat_id, product['image'], caption=post)
            else:
                bot.send_message(chat_id, post)
            
            bot.delete_message(chat_id, wait_msg.message_id)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            bot.edit_message_text(f"❌ خطأ: {error_msg[:100]}", chat_id, wait_msg.message_id)

def keep_alive():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    print("🚀 Bot starting...")
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot running! Arabic products enabled")
    bot.infinity_polling()
