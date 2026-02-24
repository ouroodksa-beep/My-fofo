import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import random
import re
import time
import json

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHANNEL_ID = "@Ouroodbot"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة بيانات ضخمة: 200+ جملة سعودية بروفشنال ---
SAUDI_TEMPLATES = {
    # اكتشاف مفاجئ (20 جملة)
    "discovery": [
        "اكتشفت {title} وما صدقت جودته!",
        "صادفة حلوة! لقيت {title} بسعر مغري",
        "من الصدف الجميلة: {title}",
        "ما كنت أدري إن {title} موجود بهالجودة!",
        "مفاجأة سارة: {title} يفوق التوقعات",
        "اكتشاف اليوم: {title} يستاهل التجربة",
        "خبر عاجل: {title} متوفر الآن!",
        "تصادف ولا أحلى: {title} بسعر منافس",
        "ما شاء الله! {title} فاق تصوري",
        "لحظة صادمة: {title} بهالسعر!",
        "فرصة لا تتكرر: اكتشفت {title}",
        "مفاجأة العام: {title} بجودة عالية",
        "صدفة غيرت رأيي: {title}",
        "اكتشاف ثمين: {title} يستاهل الاهتمام",
        "من غير ما أدور: لقيت {title}",
        "مفاجأة غير متوقعة: {title}",
        "اكتشاف رهيب: {title} بمواصفات ممتازة",
        "خبر حلو: {title} متاح الآن",
        "تصادف خير: {title} بسعر معقول",
        "ما توقعت ألقى {title} بهالسهولة!",
    ],
    
    # توصية شخصية (20 جملة)
    "personal": [
        "مجرب {title} وما ندمت أبداً",
        "من تجربتي: {title} يستاهل كل ريال",
        "صراحة {title} غيّر روتيني اليومي",
        "أعترف: {title} أفضل استثمار سويته",
        "بعد تجربة شهر: {title} يستاهل الثقة",
        "مجرب شخصياً: {title} لا يُضاهى",
        "من قلب التجربة: {title} رائع",
        "بكل صراحة: {title} فاق توقعاتي",
        "بعد استخدام مطوّل: {title} ممتاز",
        "تجربتي تقول: {title} يستاهل الشراء",
        "بشهادة شخصية: {title} لا يخيب",
        "من واقع التجربة: {title} مميز",
        "بعد فترة استخدام: {title} ثابت الجودة",
        "أشهد بصدق: {title} يستاهل التجربة",
        "تجربتي الخاصة: {title} ممتاز",
        "بكل أمانة: {title} يفوق الوصف",
        "من يوم جربت {title} وما تركته",
        "شهادة حق: {title} يستاهل الإشادة",
        "بعد تجربة حقيقية: {title} ممتاز",
        "مجرب ومتأكد: {title} يستاهل",
    ],
    
    # توصية صديق/عائلة (20 جملة)
    "friend": [
        "أخوي نصحني بـ {title} وصادق",
        "صديقتي جابت لي {title} هدية وانبهرت",
        "أمي اشتاقت لـ {title} وصارت تدعي لي",
        "أبوي وافق على {title} وهذا دليل نجاحه",
        "أختي مجنونة على {title}",
        "صاحبي يتباهى بـ {title}",
        "جارتي سألتني عن {title} بعد ما شافته",
        "زميلي في العمل يمدح {title}",
        "خالتي اشتريت {title} على توصيتي",
        "ابن عمي يتهاوش على {title}",
        "صديق العائلة وصى على {title}",
        "جيراننا يتساءلون عن {title}",
        "رفيجاتي يبغون {title} بعد ما شافوه",
        "أخواتي يتهاوشن على {title}",
        "عيال الخالة يحبون {title}",
        "صاحبتي سفيرة {title} في المجموعة",
        "أخوي الصغير يموت على {title}",
        "والدتي تقول {title} نعمة",
        "أبوي يستخدم {title} يومياً",
        "العائلة مجمعة على حب {title}",
    ],
    
    # عجلة وندرة (20 جملة)
    "urgent": [
        "بسرعة! الكمية محدودة على {title}",
        "الوقت ينفد: {title} بنفذ قريب",
        "فرصة أخيرة: {title} بسعر خاص",
        "لا تتأخر: {title} ينتهي العرض",
        "سارع: {title} متوفر لفترة محدودة",
        "الآن أو أبداً: {title} بسعر مغري",
        "باقي وقت قليل: {title} بخصم",
        "تنبيه عاجل: {title} على وشك النفاذ",
        "الحين أحسن: {title} ما راح يتكرر",
        "فرصة ذهبية: {title} متاح الآن",
        "لا تفوت: {title} بنفذ بسرعة",
        "عاجل: {title} بسعر مؤقت",
        "سارع بالحجز: {title} محدود",
        "العرض ينتهي: {title} لا يتأخر",
        "باقي كمية قليلة: {title}",
        "الوقت ضيق: {title} بسعر خاص",
        "فرصة ما تتعوض: {title} الآن",
        "تنبيه: {title} على وشك الانتهاء",
        "بسرعة قبل ما ينفذ: {title}",
        "الآن فرصتك: {title} محدود",
    ],
    
    # جودة وسعر (20 جملة)
    "value": [
        "جودة فاخرة بسعر شعبي: {title}",
        "القيمة الحقيقية: {title} يستاهل",
        "بين الجودة والسعر: {title} يوازن",
        "استثمار ذكي: {title} يدوم",
        "جودة تستحق الثناء: {title}",
        "سعر منافس وجودة عالية: {title}",
        "الأفضلية واضحة: {title}",
        "قيمة مقابل السعر = {title}",
        "جودة لا تتنازل: {title} بسعر معقول",
        "الاختيار الأذكى: {title}",
        "بين الغالي والرخيص: {title} الأفضل",
        "جودة احترافية بسعر مناسب: {title}",
        "التوازن المثالي: {title}",
        "يستاهل الاستثمار: {title}",
        "جودة تدوم بسعر يعقل: {title}",
        "الأداء يفوق السعر: {title}",
        "صفقة رابحة: {title} يستاهل",
        "الجودة تتكلم: {title}",
        "سعر ينافس وجودة تفوق: {title}",
        "الأفضل في فئته: {title}",
    ],
    
    # يومي وعملي (20 جملة)
    "daily": [
        "روتيني اليومي يحتاج {title}",
        "ما أقدر أستغني عن {title} صراحة",
        "يومي ما يكمل بدون {title}",
        "أساسيات يومي: {title} ضروري",
        "كل يوم أستخدم {title} وأدعي",
        "ما فيه يوم بدون {title}",
        "روتين الصباح يبدأ بـ {title}",
        "نهاية يومي تنتهي بـ {title}",
        "يومي أحلى مع {title}",
        "الحياة أسهل مع {title}",
        "يومي منظم بفضل {title}",
        "ما أتخيل يومي بدون {title}",
        "يومي كامل يحتوي {title}",
        "السعادة اليومية: {title}",
        "يومي يكتمل بـ {title}",
        "لا غنى عنه يومياً: {title}",
        "يومي أفضل مع {title}",
        "روتيني السعيد: {title}",
        "كل يوم مع {title} نعمة",
        "يومي يستاهل {title}",
    ],
    
    # هدية ومفاجأة (20 جملة)
    "gift": [
        "هدية تفرح القلب: {title}",
        "مفاجأة لا تُنسى: {title}",
        "الهدية المثالية: {title}",
        "تدليل لأحبابك: {title}",
        "هدية تعبر عن اهتمامك: {title}",
        "الإهداء الأنسب: {title}",
        "مفاجأة سعيدة: {title}",
        "هدية تستحق التقدير: {title}",
        "لمن تُحب: {title} هدية مميزة",
        "إسعاد الآخرين بـ {title}",
        "هدية تبقى ذكرى: {title}",
        "الإهداء الأفضل: {title}",
        "مفاجأة تسعد: {title}",
        "هدية عملية وجميلة: {title}",
        "للمناسبات الخاصة: {title}",
        "إهداء يليق بك: {title}",
        "هدية تُدهش: {title}",
        "التفكير في الآخرين: {title}",
        "مفاجأة تُفرح: {title}",
        "هدية تستاهل: {title}",
    ],
    
    # فخامة وأناقة (20 جملة)
    "luxury": [
        "لمسة فاخرة: {title} يميزك",
        "الأناقة تبدأ من {title}",
        "فخامة تليق بك: {title}",
        "التميز واضح في {title}",
        "أسلوب راقٍ: {title}",
        "الفخامة الحقيقية: {title}",
        "تألق بـ {title}",
        "التميز عنوانك مع {title}",
        "أناقة لا تُضاهى: {title}",
        "الفخامة تختصر بـ {title}",
        "بصمة أنيقة: {title}",
        "الأصالة تلتقي الفخامة: {title}",
        "تميزك يكمله {title}",
        "الأناقة في التفاصيل: {title}",
        "فخامة تستحق: {title}",
        "أسلوب حياة راقٍ: {title}",
        "التميز يبدأ بـ {title}",
        "أناقة تفرض احترامها: {title}",
        "الفخامة تختار {title}",
        "تألقك يستحق {title}",
    ],
    
    # أمومة وعائلة (20 جملة)
    "family": [
        "لراحة عائلتك: {title} مهم",
        "أمومة أسهل مع {title}",
        "العائلة تستاهل {title}",
        "لأحبابك الأفضل: {title}",
        "راحة البيت تبدأ بـ {title}",
        "للأم المثالية: {title}",
        "سعادة العائلة في {title}",
        "البيت أحلى مع {title}",
        "للأطفال الأعزاء: {title}",
        "راحة الأم: {title} يساعد",
        "العائلة تجتمع على {title}",
        "للأب المثالي: {title}",
        "سعادة الأطفال: {title}",
        "البيت المنظم: {title} يسهل",
        "للأم الحنونة: {title}",
        "راحة العائلة: {title}",
        "للأهل الأعزاء: {title}",
        "سعادة يومية: {title}",
        "البيت يستاهل {title}",
        "للعائلة السعيدة: {title}",
    ],
    
    # صحة ولياقة (20 جملة)
    "health": [
        "صحتك تستاهل {title}",
        "لياقتك تبدأ بـ {title}",
        "العافية تستحق {title}",
        "صحة أفضل مع {title}",
        "جسمك يشكرك على {title}",
        "النشاط اليومي: {title} يساعد",
        "لحياة صحية: {title} مهم",
        "صحتك أولوية: {title}",
        "اللياقة تستاهل {title}",
        "جسمك يستحق الأفضل: {title}",
        "العافية تبدأ من {title}",
        "صحة تدوم بـ {title}",
        "لطاقة يومية: {title}",
        "جسدك يحتاج {title}",
        "الصحة تختار {title}",
        "لياقة تستحق: {title}",
        "حياة صحية تبدأ بـ {title}",
        "صحتك في {title}",
        "النشاط يستاهل {title}",
        "لجسم رشيق: {title}",
    ],
    
    # تكنولوجيا وذكاء (20 جملة)
    "tech": [
        "تقنية تخدمك: {title}",
        "الذكاء يختار {title}",
        "تكنولوجيا تسهل حياتك: {title}",
        "العصرية تبدأ بـ {title}",
        "ابتكار يستاهل: {title}",
        "الذكاء في الاختيار: {title}",
        "تقنية تستحق: {title}",
        "الحداثة تلتقي الفائدة: {title}",
        "ابتكار يسهل: {title}",
        "تكنولوجيا تفرق: {title}",
        "الذكاء الاصطناعي ينصح بـ {title}",
        "تقنية تستاهل الاهتمام: {title}",
        "الابتكار يختصر {title}",
        "تكنولوجيا تخدمك: {title}",
        "العقلية الذكية تختار {title}",
        "ابتكار يوفر وقتك: {title}",
        "تقنية تستحق الثقة: {title}",
        "الحداثة تبدأ من {title}",
        "ذكاء في التصميم: {title}",
        "تكنولوجيا تليق بك: {title}",
    ],
    
    # تنظيم وتنظيف (20 جملة)
    "organization": [
        "تنظيم يسهل حياتك: {title}",
        "الترتيب يبدأ بـ {title}",
        "نظافة تستاهل: {title}",
        "تنظيم يريح بالك: {title}",
        "الترتيب يليق بك: {title}",
        "نظافة تدوم مع {title}",
        "تنظيم يوفر وقتك: {title}",
        "الترتيب السهل: {title}",
        "نظافة تستحق: {title}",
        "تنظيم يليق ببيتك: {title}",
        "الترتيب الذكي: {title}",
        "نظافة تفرق: {title}",
        "تنظيم يسهل يومك: {title}",
        "الترتيب المثالي: {title}",
        "نظافة تستاهل الاهتمام: {title}",
        "تنظيم يكمل بيتك: {title}",
        "الترتيب الاحترافي: {title}",
        "نظافة تليق بك: {title}",
        "تنظيم يريح عينك: {title}",
        "الترتيب السريع: {title}",
    ],
}

# --- User Agents ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

@app.route('/')
def home():
    return "✅ Bot Active - Saudi Pro Affiliate"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def translate_to_arabic(text):
    """محاكاة ترجمة الوصف للعربي (البراند يبقى إنجليزي)"""
    # في الواقع هنا تستخدمين Google Translate API
    # هذا نموذج مبسط للتوضيح
    
    # استخراج البراند (الكلمة الإنجليزية الأولى عادة)
    words = text.split()
    brand = words[0] if words and words[0].isascii() else ""
    
    # ترجمة بسيطة للكلمات الشائعة (محاكاة)
    translations = {
        "Shoes": "حذاء",
        "Watch": "ساعة",
        "Bag": "حقيبة",
        "Phone": "هاتف",
        "Laptop": "لابتوب",
        "Headphones": "سماعات",
        "Camera": "كاميرا",
        "Tablet": "تابلت",
        "Charger": "شاحن",
        "Cable": "كيبل",
        "Mouse": "ماوس",
        "Keyboard": "كيبورد",
        "Screen": "شاشة",
        "Battery": "بطارية",
        "Case": "غطاء",
        "Cover": "حماية",
        "Stand": "ستاند",
        "Holder": "حامل",
        "Light": "إضاءة",
        "Speaker": "سماعة",
        "Microphone": "مايك",
        "Tripod": "ترايبود",
        "Adapter": "محول",
        "Memory": "ذاكرة",
        "Storage": "تخزين",
        "Wireless": "لاسلكي",
        "Bluetooth": "بلوتوث",
        "Smart": "ذكي",
        "Digital": "رقمي",
        "Professional": "احترافي",
        "Original": "أصلي",
        "New": "جديد",
        "Premium": "مميز",
        "Pro": "برو",
        "Max": "ماكس",
        "Plus": "بلس",
        "Ultra": "ألترا",
        "Mini": "ميني",
        "Air": "آير",
    }
    
    # بناء النص المترجم (البراند يبقى إنجليزي)
    translated_words = [brand]  # البراند أول شي
    
    for word in words[1:]:
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word in translations:
            translated_words.append(translations[clean_word])
        elif word.isascii():
            # إذا ما لقينا ترجمة، نحط وصف عام
            continue
        else:
            translated_words.append(word)
    
    # إذا ما ترجم شي، نرجع وصف عام بالعربي
    if len(translated_words) < 2:
        return f"{brand} منتج أصلي مميز"
    
    return " ".join(translated_words[:6])  # نختصر للبروفشنال

def extract_brand(title):
    """استخراج البراند من العنوان"""
    words = title.split()
    if words:
        # البراند عادة أول كلمة أو أول كلمتين
        brand = words[0]
        # إذا الكلمة الثانية أيضاً إنجليزية وقصيرة، نضيفها
        if len(words) > 1 and words[1].isascii() and len(words[1]) < 10:
            brand = f"{words[0]} {words[1]}"
        return brand
    return title

def get_high_quality_image(soup):
    """استخراج صورة عالية الجودة"""
    try:
        img = soup.select_one('#landingImage')
        if img:
            dynamic_data = img.get('data-a-dynamic-image')
            if dynamic_data:
                images_dict = json.loads(dynamic_data)
                largest_url = max(images_dict.keys(), key=lambda x: images_dict[x][0] * images_dict[x][1])
                return largest_url
            
            image_url = img.get('data-old-hires') or img.get('src')
            if image_url:
                return re.sub(r'._[^_]+_\.', '._SL1500_.', image_url)
    except:
        pass
    return None

def get_amazon_info(url):
    """استخراج معلومات المنتج"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
            
            time.sleep(random.uniform(1, 2))
            session = requests.Session()
            session.get("https://www.amazon.sa", headers=headers, timeout=10)
            time.sleep(random.uniform(0.5, 1))
            
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # العنوان الأصلي
            original_title = None
            title_selectors = ['#productTitle', 'h1.a-size-large']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    original_title = element.get_text().strip()
                    original_title = re.sub(r'\s+', ' ', original_title)
                    break
            
            if not original_title:
                continue
            
            # استخراج البراند (إنجليزي)
            brand = extract_brand(original_title)
            
            # ترجمة الوصف للعربي
            arabic_description = translate_to_arabic(original_title)
            
            # السعر
            price = None
            price_selectors = [
                '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                '.a-price .a-offscreen',
                '.a-price-whole',
            ]
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = price_match.group()
                        break
            
            # الصورة
            image_url = get_high_quality_image(soup)
            
            # التقييم
            rating = None
            rating_element = soup.select_one('[data-hook="average-star-rating"] .a-icon-alt')
            if rating_element:
                rating_match = re.search(r'(\d+\.?\d*)', rating_element.get_text())
                if rating_match:
                    rating = rating_match.group(1)
            
            if brand and price:
                return {
                    'brand': brand,
                    'description': arabic_description,
                    'price': price,
                    'image': image_url,
                    'rating': rating,
                    'url': url
                }
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(random.uniform(2, 3))
    
    return None

def generate_pro_post(product_info):
    """توليد منشور بروفشنال"""
    brand = product_info['brand']
    description = product_info['description']
    price = product_info['price']
    rating = product_info.get('rating')
    url = product_info['url']
    
    # اختيار قالب عشوائي
    category = random.choice(list(SAUDI_TEMPLATES.keys()))
    template = random.choice(SAUDI_TEMPLATES[category])
    
    # بناء عنوان المنتج: براند إنجليزي + وصف عربي
    product_title = f"{brand} {description}"
    
    # ملء القالب
    main_text = template.format(title=product_title)
    
    # بناء المنشور البروفشنال
    lines = [
        main_text,
        "",  # سطر فارغ
        f"💰 {price} ريال",
    ]
    
    # إضافة التقييم إذا موجود
    if rating:
        lines.append(f"⭐ {rating}/5")
    
    # سطر فارغ قبل الرابط
    lines.append("")
    
    # الرابط ثابت في آخر سطر
    lines.append(f"الرابط: {url}")
    
    post = "\n".join(lines)
    
    return post

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if "amazon" in message.text.lower() or "amzn" in message.text.lower():
        wait_msg = bot.reply_to(message, "⏳ جاري التحضير...")
        
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
        
        if not urls:
            bot.edit_message_text("❌ ما لقيت رابط!", chat_id, wait_msg.message_id)
            return
        
        url = urls[0]
        product_info = get_amazon_info(url)
        
        if product_info:
            pro_post = generate_pro_post(product_info)
            
            try:
                if product_info.get('image'):
                    bot.send_photo(
                        CHANNEL_ID,
                        product_info['image'],
                        caption=pro_post,
                        parse_mode=None
                    )
                else:
                    bot.send_message(CHANNEL_ID, pro_post)
                
                bot.edit_message_text(
                    f"✅ تم النشر!\n\n{product_info['brand']} {product_info['description'][:30]}...\n{product_info['price']} ريال",
                    chat_id,
                    wait_msg.message_id
                )
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error: {error_msg}")
                
                if "chat not found" in error_msg:
                    bot.edit_message_text("❌ القناة ما لقيتها! تأكدي من الآيدي", chat_id, wait_msg.message_id)
                elif "not enough rights" in error_msg:
                    bot.edit_message_text("❌ البوت ما عنده صلاحيات! ضيفيه Admin", chat_id, wait_msg.message_id)
                elif "wrong file identifier" in error_msg:
                    try:
                        bot.send_message(CHANNEL_ID, pro_post)
                        bot.edit_message_text("✅ تم النشر (بدون صورة)", chat_id, wait_msg.message_id)
                    except:
                        bot.edit_message_text("❌ فشل النشر نهائياً", chat_id, wait_msg.message_id)
                else:
                    bot.edit_message_text(f"❌ خطأ: {error_msg[:100]}", chat_id, wait_msg.message_id)
        else:
            bot.edit_message_text(
                "❌ ما قدرت أقرأ المنتج\n\nجربي رابط amazon.sa مباشرة",
                chat_id,
                wait_msg.message_id
            )
    else:
        bot.reply_to(message, "👋 أرسلي رابط أمازون")

def keep_alive():
    while True:
        time.sleep(60)
        print("Bot alive...")

if __name__ == "__main__":
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot started...")
    bot.infinity_polling()
