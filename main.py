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
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- جمل تسويقية بنفس أسلوب الصور ---
MARKETING_PHRASES = [
    "📉 أقل سعر خلال 30 يوم",
    "⏰ العرض لفترة محدودة",
    "🔥 الكمية محدودة جداً",
    "💰 وفّر {discount} ريال",
    "🎁 هدية مجانية مع الطلب",
    "🚚 توصيل سريع لجميع المناطق",
    "⭐ تقييم 5 نجوم من العملاء",
    "✅ ضمان استرجاع خلال 30 يوم",
    "🔒 دفع آمن وموثوق",
    "📞 خدمة عملاء 24/7",
    "💯 جودة مضمونة 100%",
    "⚡ سارع قبل النفاذ",
    "🏆 الأكثر مبيعاً",
    "🎯 أفضل سعر في السوق",
    "🔥 عرض حصري",
    "📦 توصيل مجاني للطلبات +99 ريال",
    "💎 منتج أصلي 100%",
    "⏳ ينتهي العرض قريباً",
    "🛡️ ضمان مصنع 2 سنة",
    "🎉 خصم إضافي مع الكوبون",
]

# --- صيغ السعر ---
PRICE_FORMATS = [
    "🔥 بـ {price} ريال فقط!",
    "💰 {price} ريال",
    "⚡ {price} ريال بس!",
    "💸 فقط {price} ريال!",
    "🎯 {price} ريال ويوصلك!",
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

def translate_title(title):
    """ترجمة العنوان للعربي باستخدام Google Translate API"""
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': title,
            'langpair': 'en|ar',
            'de': 'your_email@example.com'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['responseStatus'] == 200:
            translated = data['responseData']['translatedText']
            translated = translated.replace('&#39;', "'").replace('&quot;', '"')
            return translated
        else:
            return title
            
    except Exception as e:
        print(f"Translation error: {e}")
        return title

def format_price(price_str):
    """إزالة النقطة العشرية من السعر"""
    try:
        price_clean = price_str.replace(',', '').replace(' ', '').strip()
        price_num = float(price_clean)
        return str(int(price_num))
    except:
        return price_str

def generate_post_with_ai(title, price, category):
    """استخدام OpenAI GPT لكتابة البوست"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # اختيار جملة تسويقية عشوائية
        marketing = random.choice(MARKETING_PHRASES)
        if "{discount}" in marketing:
            try:
                current_price = int(price)
                fake_old_price = int(current_price * 1.3)
                discount_amount = fake_old_price - current_price
                marketing = marketing.format(discount=discount_amount)
            except:
                marketing = marketing.replace(" {discount} ريال", "")
        
        # بناء الـ Prompt
        prompt = f"""اكتب منشور تسويقي قصير ومشوق باللهجة السعودية لمنتج:
        
المنتج: {title}
السعر: {price} ريال
التصنيف: {category}

المتطلبات:
- ابدأ بجملة افتتاحية جذابة (هلا بالزين، تخيل، يا عزيزي، وش رايك)
- استخدم إيموجي مناسبة (🔥💎✨🤩🏃‍♂️)
- اذكر اسم المنتج بشكل طبيعي
- لا تكرر نفس الأسلوب دائماً (تنوع في الأسلوب)
- اكتب بأسلوب محادثة ودي (زي الواتساب)
- لا تستخدم نقاط في النهاية
- اجعلها جملة أو جملتين فقط

أمثلة للأسلوب المطلوب:
"هلا بالزين كله {title} وصل! 🤍👟"
"تخيل يا عزيزي {title} يكون بسعر كذا! 🤯"
"أبطالنا أصحاب الذوق {title} بين يديك! 🦸‍♂️"
"🔴 آخر حبة بالمخزون {title}!"

اكتب منشور واحد فقط:"""

        data = {
            "model": "gpt-4o-mini",  # أو "gpt-3.5-turbo" للتوفير
            "messages": [
                {"role": "system", "content": "أنت مسوق محترف في السعودية، تكتب منشورات قصيرة وجذابة للمنتجات باللهجة السعودية. تستخدم إيموجي بكثرة وتكتب بأسلوب محادثة ودي."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,  # عشوائية عالية للتنوع
            "max_tokens": 150
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            ai_text = result['choices'][0]['message']['content'].strip()
            # إزالة علامات الاقتباس إذا وجدت
            ai_text = ai_text.strip('"').strip("'")
            return ai_text, marketing
        else:
            return None, marketing
            
    except Exception as e:
        print(f"AI Error: {e}")
        return None, marketing

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
        
        price = format_price(price)
        
        image = None
        img_elem = soup.select_one('#landingImage')
        if img_elem:
            image = img_elem.get('data-old-hires') or img_elem.get('src')
            if image:
                image = image.replace('._SL500_', '._SL1500_')
        
        # تحديد التصنيف
        category = "عام"
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['shoe', 'shoes', 'sneaker', 'boot']):
            category = "أحذية"
        elif any(word in title_lower for word in ['phone', 'laptop', 'electronic']):
            category = "إلكترونيات"
        elif any(word in title_lower for word in ['furniture', 'kitchen', 'home']):
            category = "منزل"
        elif any(word in title_lower for word in ['beauty', 'cream', 'perfume']):
            category = "جمال"
        elif any(word in title_lower for word in ['sport', 'gym', 'fitness']):
            category = "رياضة"
        elif any(word in title_lower for word in ['baby', 'kids', 'toy']):
            category = "أطفال"
        elif any(word in title_lower for word in ['shirt', 'pant', 'dress', 'cloth']):
            category = "ملابس"
        
        # ترجمة العنوان
        arabic_title = translate_title(title)
        
        return {
            'original_title': title,
            'title': arabic_title,
            'category': category,
            'price': price,
            'image': image,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None

def generate_post(product):
    """توليد المنشور باستخدام AI"""
    title = product['title']
    price = product['price']
    category = product['category']
    url = product['url']
    
    # الحصول على نص من AI
    ai_text, marketing = generate_post_with_ai(title, price, category)
    
    # إذا فشل AI، نستخدم نص احتياطي بسيط
    if not ai_text:
        ai_text = f"✨ {title} وصل! 🔥"
    
    # صيغة السعر
    price_text = random.choice(PRICE_FORMATS).format(price=price)
    
    # تجميع المنشور
    return f"{ai_text}\n\n{price_text}\n\n{marketing}\n\nالرابط: {url}"

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
        
        wait_msg = bot.reply_to(message, "⏳ جاري قراءة المنتج وكتابة المنشور بالذكاء الاصطناعي...")
        
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
        
        try:
            post = generate_post(product)
            
            if product.get('image'):
                bot.send_photo(chat_id, product['image'], caption=post)
            else:
                bot.send_message(chat_id, post)
            
            bot.delete_message(chat_id, wait_msg.message_id)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            bot.edit_message_text(f"❌ خطأ: {str(e)[:100]}", chat_id, wait_msg.message_id)

def keep_alive():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    print("🚀 Bot starting with AI...")
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot running with GPT-4! AI will write all posts.")
    bot.infinity_polling()
