import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import random
import os
from groq import Groq

TOKEN = "7956075348:AAFetNzy6ECdP8iHgMWbwQIfjSInomOuhBU"
bot = telebot.TeleBot(TOKEN)

GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)

PROXY_URL = os.environ.get("PROXY_URL")


def protect_brands(text):
    return text


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


def clean_product_title(full_title):
    """استخراج الزبدة والمهم فقط من اسم المنتج وحذف الحشو الطويل"""
    if not full_title:
        return "منتج مميز"
    
    # إزالة الكلمات الزائدة والخصائص الطويلة المعتادة في أمازون
    cleaned = re.sub(r'\b(Aspirin|By|with|for|and|من|لـ|مع)\b.*', '', full_title, flags=re.IGNORECASE)
    cleaned = re.split(r'[-–,|/]', full_title)[0] # اخذ أول جزء فقط قبل الرموز الفاصلة الطويلة
    
    # ترجمة وتحسين الاسم ليصبح قصيراً ومفهوماً
    arabic_name = translate_to_arabic(cleaned)
    words = arabic_name.split()
    
    # تقليص الاسم ليكون في حدود 3 إلى 5 كلمات قوية ومختصرة
    short_name = " ".join(words[:5])
    return short_name.strip() if len(short_name) > 3 else translate_to_arabic(full_title[:40])


def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}
    return emojis.get(category, "🔥")


def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl', 'link.amazon']):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            if 'link.amazon' in url.lower():
                soup = BeautifulSoup(r.text, "html.parser")
                asin = None
                canonical = soup.select_one('link[rel="canonical"]')
                if canonical:
                    href = canonical.get('href', '')
                    asin_match = re.search(r'/dp/([A-Z0-9]{9,10})', href)
                    if asin_match:
                        asin = asin_match.group(1)
                if asin:
                    return f"https://www.amazon.sa/dp/{asin}"
            return r.url
        return url
    except:
        return url


def is_saudi_amazon(url):
    if "link.amazon" in url.lower():
        return True
    return "amazon.sa" in url.lower()


def extract_asin(url):
    if 'link.amazon' in url.lower():
        match = re.search(r'link\.amazon/([A-Za-z0-9]{9,10})', url, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    patterns = [r'/dp/([A-Z0-9]{9,10})', r'/gp/product/([A-Z0-9]{9,10})', r'/product/([A-Z0-9]{9,10})', r'([A-Z0-9]{9,10})/?$']
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
            return f"{int(float(num_str))} ر.س"
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
        image = img_elem.get("data-old-hires") or img_elem.get("src")
    if not image:
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img:
            image = og_img.get("content")
    if image:
        image = re.sub(r'_SX\d+_SY\d+_', '_', image).split('?')[0]
    return image


def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    for ua in user_agents:
        try:
            headers = {"User-Agent": ua, "Accept-Language": "ar-SA,ar;q=0.9"}
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            
            title_elem = soup.select_one("#productTitle")
            title = title_elem.text.strip() if title_elem else ""
            if not title:
                continue

            price_elem = soup.select_one(".a-price .a-offscreen")
            price = price_elem.text.strip() if price_elem else "0"

            old_price_elem = soup.select_one(".a-text-price .a-offscreen")
            old_price = old_price_elem.text.strip() if old_price_elem else None

            image = get_high_quality_image(soup)
            clean_name = clean_product_title(title)
            category = detect_product_category(title)
            current_price_num = extract_number(price)

            return {
                "name": clean_name,
                "price": price,
                "old_price": old_price,
                "image": image,
                "category": category,
                "current_price_num": current_price_num,
            }
        except:
            continue
    return None


def generate_post(product_data, original_url):
    """توليد آلاف الصيغ الإبداعية المنمقة جداً بأساليب تسويقية ساحرة"""
    name = product_data["name"]
    price = product_data["price"]
    old_price = product_data["old_price"]
    category = product_data["category"]
    
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else ""
    emoji = get_category_emoji(category)

    # حساب نسبة الخصم إن وجد
    discount_text = ""
    old_num = extract_number(old_price) if old_price else 0
    if old_num > product_data["current_price_num"] and old_num > 0:
        pct = int(((old_num - product_data["current_price_num"]) / old_num) * 100)
        discount_text = f"⚡ خصم {pct}% لفترة محدودة!"

    # آلاف الاحتمالات العشوائية لكسر التكرار تماماً وصياغة جذابة
    marketing_styles = [
        "أسلوب الفخامة والروعة المباشرة",
        "أسلوب النصيحة الخفيفة والصدمة الإيجابية بالسعر",
        "أسلوب التشويق والإثارة لعرض لا يُعوض",
        "أسلوب الهدوء الأنيق والمميز"
    ]
    
    chosen_style = random.choice(marketing_styles)
    random_ref_id = random.randint(100000, 999999)

    prompt = f"""
[Ref_Code: {random_ref_id}]
أنت خبير تسويق إلكتروني وصانع محتوى محترف جداً على السوشيال ميديا.
اكتب رسالة ترويجية قصيرة ومنمقة للغاية لمنتج: ({name}).
الأسلوب المطلوب: ({chosen_style}).

شروط التنسيق والصياغة بدقة شديدة:
1. ابدأ فوراً بعبارة تشويقية أو إيموجي جذاب يناسب المنتج بدون أي مقدمات تقليدية.
2. لا تذكر سوى اسم المنتج المختصر والنظيف ({name}) بدون أي حشو أو تفاصيل تقنية معقدة.
3. اجعل الأسلوب راقياً، بسيطاً، مشجعاً، وغير مكرر نهائياً بفضل الـ Ref_Code.
4. الطول أقصاه سطران إلى 3 أسطر فقط.
5. لا تضع أي روابط نهائياً داخل النص.
6. أعطني النص الخالص فقط بدون أي علامات تنصيص.
"""

    ai_text = ""
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت كاتب محتوى تسويقي إبداعي بأسلوب راقي ومبتكر."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.5,
            max_tokens=200
        )
        ai_text = completion.choices[0].message.content.strip()
    except:
        ai_text = f"لقت لكم اليوم قطعة مميزة لا تستغنى عنها: **{name}** بجودة عالية وسعر استثنائي!"

    # تنسيق الفورمات النهائي بشكل مرتب وأنيق جداً (كما طلبت)
    post_lines = [
        f"{emoji} **{name}**",
        "",
        ai_text,
        "",
        f"🏷️ السعر بسعر لقطة: `{clean_current}`" + (f" ~~{clean_old}~~" if clean_old else ""),
        (f"🔥 {discount_text}" if discount_text else ""),
        "",
        f"🛒 **اضغط هنا للطلب والشراء:**",
        f"{original_url}"
    ]

    # إزالة الأسطر الفارغة الزائدة إن وجدت
    final_post = "\nnot_empty".join([line for line in post_lines if line != ""])
    # تصحيح تداخل الـ join المؤقت
    final_post = "\n".join([line for line in post_lines if line is not None])
    
    return final_post


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أهلاً بك! يرجى إرسال رابط المنتج من أمازون السعودية لنشر السحر ✨")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ عذراً، الرابط مخصص لأمازون السعودية (amazon.sa) فقط.")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج من الرابط.")
            continue

        wait = bot.reply_to(msg, "⏳ جاري إعداد التنسيق الأنيق والصياغة المبتكرة...")

        product = get_product(asin)
        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، تأكد من صحة الرابط.", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ حدث خطأ أثناء إرسال المنشور.", msg.chat.id, wait.message_id)


# ============ WEBHOOK SERVER ============
from flask import Flask, request

app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route('/')
def index():
    return "🤖 البوت يعمل بكفاءة عالية وتنسيق مميز 🔥"

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Unsupported Media Type', 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
        print(f"✅ Webhook set to: {WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}")
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

if __name__ == '__main__':
    start_webhook()
