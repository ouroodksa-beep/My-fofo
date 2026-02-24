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
CHANNEL_ID = "@Ouroodbot"  # مثال: @your_channel أو -1001234567890

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة بيانات الأنماط السعودية المختصرة (جمل قصيرة) ---
SAUDI_TEMPLATES = {
    "discovery": [
        "صدمني {title}!\n{price} ريال بس 🤯",
        "لقيت الكنز {title}\nبـ {price} ريال ✨",
        "ما توقعت {title} يكون بـ {price} ريال!",
    ],
    "friend_tip": [
        "أخوي قالي جرب {title}\n{price} ريال ويستاهل 👌",
        "صديقتي نصحتني بـ {title}\n{price} ريال بس 💯",
    ],
    "personal": [
        "مجرب {title} من شهر\n{price} ريال وما ندمت ❤️",
        "اشتريت {title} بـ {price} ريال\nصار من أساسياتي 🔥",
    ],
    "urgent": [
        "بسرعة! {title}\n{price} ريال بس ⚡",
        "عرض ينتهي {title}\n{price} ريال 🏃‍♀️",
    ],
    "honest": [
        "بصراحة {title} يستاهل\n{price} ريال 💪",
        "جودة عالية بـ {price} ريال\n{title} يفوز 🏆",
    ],
    "casual": [
        "يا جماعة {title}!\n{price} ريال بس 😍",
        "فشلت الخصوم {title}\n{price} ريال 💸",
    ],
    "mom": [
        "للأمهات {title}\n{price} ريال ويريح 🤱",
        "أولادي يحبون {title}\n{price} ريال بس 👶",
    ],
    "luxury": [
        "فخامة بـ {price} ريال\n{title} يستاهل 👑",
        "غالي المظهر رخيص السعر\n{title} = {price} ريال 💎",
    ],
    "daily": [
        "ضرورة يومية {title}\n{price} ريال بس 📌",
        "ما أقدر أستغني عن {title}\n{price} ريال 🎯",
    ],
    "gift": [
        "هدية مثالية {title}\n{price} ريال 🎁",
        "تبي تهدي؟ {title}\n{price} ريال ويفرح 🎀",
    ],
}

# --- User Agents ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

@app.route('/')
def home():
    return "✅ Bot Active - Saudi Pro Affiliate"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def extract_asin(url):
    """استخراج ASIN من رابط أمازون"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'amzn\.eu/d/([A-Z0-9]+)',
        r'amzn\.to/[a-zA-Z0-9]+',
        r'amazon\..*/([A-Z0-9]{10})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1) if len(match.group(1)) == 10 else match.group(0)
    return None

def get_high_quality_image(soup):
    """استخراج صورة عالية الجودة من أمازون"""
    image_url = None
    
    # محاولة 1: البيانات المخزنة في JavaScript
    try:
        scripts = soup.find_all('script', type='text/javascript')
        for script in scripts:
            if script.string and 'hiRes' in script.string:
                # البحث عن روابط الصور في الـ JSON
                matches = re.findall(r'"hiRes":"(https://[^"]+)"', script.string)
                if matches:
                    image_url = matches[0].replace('\\', '')
                    return image_url
    except:
        pass
    
    # محاولة 2: data-a-dynamic-image (أحجام متعددة)
    try:
        img = soup.select_one('#landingImage')
        if img:
            dynamic_data = img.get('data-a-dynamic-image')
            if dynamic_data:
                # تحويل الـ JSON واختيار أكبر حجم
                images_dict = json.loads(dynamic_data)
                # اختيار الصورة الأكبر (آخر مفتاح عادة)
                largest_url = max(images_dict.keys(), key=lambda x: images_dict[x][0] * images_dict[x][1])
                image_url = largest_url
                return image_url
    except:
        pass
    
    # محاولة 3: data-old-hires (الجودة العالية القديمة)
    try:
        img = soup.select_one('#landingImage')
        if img:
            image_url = img.get('data-old-hires')
            if image_url:
                return image_url
    except:
        pass
    
    # محاولة 4: src العادي مع تعديل للجودة العالية
    try:
        img = soup.select_one('#landingImage')
        if img:
            src = img.get('src')
            if src:
                # تعديل الرابط لجودة أعلى
                image_url = re.sub(r'._[^_]+_\.', '._SL1500_.', src)
                return image_url
    except:
        pass
    
    # محاولة 5: صور البدائل
    try:
        alt_images = soup.select('#altImages img')
        for alt_img in alt_images:
            src = alt_img.get('src')
            if src and 'images-na' in src:
                # تحويل لجودة عالية
                high_res = re.sub(r'._[^_]+_\.', '._SL1500_.', src)
                return high_res
    except:
        pass
    
    return image_url

def get_amazon_info(url):
    """استخراج معلومات المنتج مع صورة عالية الجودة"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            time.sleep(random.uniform(1, 2))
            
            session = requests.Session()
            session.get("https://www.amazon.sa", headers=headers, timeout=10)
            time.sleep(random.uniform(0.5, 1))
            
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Attempt {attempt + 1}: Status {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # العنوان
            title = None
            title_selectors = [
                '#productTitle',
                'h1.a-size-large',
                '[data-automation-id="product-title"]',
            ]
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    title = re.sub(r'\s+', ' ', title)
                    title = title[:80]  # أقصر للبروفشنال
                    break
            
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
            
            # الصورة عالية الجودة
            image_url = get_high_quality_image(soup)
            
            # التقييم
            rating = None
            rating_element = soup.select_one('[data-hook="average-star-rating"] .a-icon-alt')
            if rating_element:
                rating_text = rating_element.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
            
            if title and price:
                return {
                    'title': title,
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
    """توليد منشور بروفشنال قصير"""
    title = product_info['title']
    price = product_info['price']
    rating = product_info.get('rating')
    url = product_info['url']
    
    # اختيار قالب عشوائي
    category = random.choice(list(SAUDI_TEMPLATES.keys()))
    template = random.choice(SAUDI_TEMPLATES[category])
    
    # ملء القالب
    main_text = template.format(title=title, price=price)
    
    # إضافة تقييم إذا موجود
    rating_line = f"⭐ {rating}/5" if rating else ""
    
    # تجميع المنشور البروفشنال
    lines = [
        main_text,
        "",  # سطر فارغ
        rating_line if rating_line else "",
        "",  # سطر فارغ
        f"الرابط: {url}"  # ثابت في آخر سطر
    ]
    
    # إزالة الأسطر الفارغة
    post = "\n".join([line for line in lines if line])
    
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
                # إرسال الصورة مع المنشور
                if product_info.get('image'):
                    bot.send_photo(
                        CHANNEL_ID,
                        product_info['image'],
                        caption=pro_post,
                        parse_mode=None  # نص عادي للتنسيق الأفضل
                    )
                else:
                    bot.send_message(CHANNEL_ID, pro_post)
                
                bot.edit_message_text(
                    f"✅ تم النشر!\n\n{product_info['title'][:40]}...\n{product_info['price']} ريال",
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
                    # جرب نص فقط
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
