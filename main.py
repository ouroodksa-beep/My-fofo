import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import re
import time

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot Active"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def expand_short_url(short_url):
    """تحويل الرابط المختصر للرابط الكامل"""
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=10)
        return response.url
    except:
        return short_url

def extract_asin(url):
    """استخراج ASIN"""
    if 'amzn.to' in url or 'amzn.eu' in url or 'tinyurl' in url or 'bit.ly' in url:
        url = expand_short_url(url)
        if not url:
            return None
    
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'product/([A-Z0-9]{10})',
        r'amazon\..*/([A-Z0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    return None

def format_price(price_str):
    """إزالة النقطة العشرية من السعر"""
    try:
        price_clean = price_str.replace(',', '').replace(' ', '').strip()
        price_num = float(price_clean)
        return str(int(price_num))
    except:
        return price_str

def get_category(title):
    """تحديد تصنيف المنتج بالعربي"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['shoe', 'shoes', 'sneaker', 'boot', 'sandal', 'footwear']):
        return "أحذية"
    elif any(word in title_lower for word in ['phone', 'smartphone', 'laptop', 'computer', 'tablet', 'headphone', 'speaker', 'charger', 'camera', 'electronic']):
        return "إلكترونيات"
    elif any(word in title_lower for word in ['furniture', 'sofa', 'bed', 'mattress', 'pillow', 'blanket', 'carpet', 'lamp', 'pot', 'pan', 'blender', 'oven', 'fridge', 'washer', 'vacuum', 'fan', 'heater', 'kitchen']):
        return "منزل ومطبخ"
    elif any(word in title_lower for word in ['perfume', 'cream', 'shampoo', 'soap', 'makeup', 'lipstick', 'beauty', 'skin', 'hair']):
        return "جمال وعناية"
    elif any(word in title_lower for word in ['sport', 'fitness', 'gym', 'running', 'yoga', 'exercise', 'workout']):
        return "رياضة"
    elif any(word in title_lower for word in ['baby', 'kids', 'children', 'toy', 'doll', 'stroller', 'diaper']):
        return "أطفال"
    elif any(word in title_lower for word in ['watch', 'jewelry', 'ring', 'necklace', 'bracelet']):
        return "ساعات ومجوهرات"
    else:
        return "ملابس وأزياء"

def generate_post_with_ai(price, original_title, product_url, category):
    """استخدام OpenAI GPT لكتابة بوست"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""اكتب منشور تسويقي باللهجة السعودية الأصيلة:

بيانات المنتج:
- الاسم: {original_title}
- السعر: {price} ريال
- الصنف: {category}
- الرابط: {product_url}

هيكل المنشور (كل سطر منفصل بسطر فاضي):

سطر 1: جملة تعبيرية قصيرة تشد وتحمس (هلا بالزين، تخيل، يا عزيزي)

سطر فاضي

سطر 2: اسم المنتج مترجم للعربي

سطر فاضي

سطر 3-5: وصف كامل للمنتج بالذكاء الاصطناعي (3-4 جمل عن فوائد المنتج واستخداماته وجودته)

سطر فاضي

سطر 6: السعر القديم (أعلى من {price} بـ 30-40%) ثم السعر الجديد {price} ريال

سطر فاضي

سطر 7: جملة تعبيرية ثانية + دعوة للشراء الآن

سطر فاضي

سطر 8: الرابط كما هو

مثال على التنسيق:
هلا بالزين كله! 🤩

حذاء نايك الرياضي 👟

هذا الحذاء يجنن والله، راحة لا توصف في المشي، مناسب للتمرين والخروج، جودة عالمية تدوم سنين! 💎✨

كان بـ 280 ريال والحين بـ 199 ريال بس! 🔥💰

فرصة ذهبية ما تتعوض يا بطل! ⚡🏃‍♂️

{product_url}

اكتب المنشور بنفس التنسيق:"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "أنت مسوق سعودي أصيل، تكتب منشورات باللهجة السعودية. لازم تضع سطر فاضي بين كل جملة والثانية. تكتب وصف كامل للمنتج بالذكاء الاصطناعي. تستخدم إيموجي كثيرة."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.95,
            "max_tokens": 400
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
            ai_text = ai_text.strip('"').strip("'")
            return ai_text
        else:
            return None
            
    except Exception as e:
        print(f"AI Error: {e}")
        return None

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
        
        category = get_category(title)
        
        return {
            'original_title': title,
            'price': price,
            'image': image,
            'category': category,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None

def generate_post(product):
    """توليد المنشور باستخدام AI"""
    original_title = product['original_title']
    price = product['price']
    url = product['url']
    category = product['category']
    
    ai_text = generate_post_with_ai(price, original_title, url, category)
    
    if not ai_text:
        fake_old = int(int(price) * 1.4)
        arabic_name = original_title.split()[0] if len(original_title.split()) > 0 else "منتج رائع"
        ai_text = f"""هلا بالزين كله! 🤩✨

{arabic_name} وصل بقوة! 🔥

هذا المنتج يجنن والله، جودة عالية وأداء ممتاز، مناسب للاستخدام اليومي ويستاهل كل ريال! 💎👌

كان بـ {fake_old} ريال والحين بـ {price} بس! 💰😱

فرصة ذهبية ما تتعوض، لا تفوتك يا بطل! ⚡🏃‍♂️

{url}"""
    
    if url not in ai_text:
        ai_text = ai_text + f"\n\n{url}"
    
    return ai_text

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
        
        wait_msg = bot.reply_to(message, "⏳ جاري قراءة الرابط...")
        
        expanded_url = expand_short_url(url) if ('amzn.to' in url or 'amzn.eu' in url) else url
        
        asin = extract_asin(expanded_url)
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
    print("🚀 Bot starting...")
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot running!")
    bot.infinity_polling()
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

def format_price(price_str):
    """إزالة النقطة العشرية من السعر"""
    try:
        price_clean = price_str.replace(',', '').replace(' ', '').strip()
        price_num = float(price_clean)
        return str(int(price_num))
    except:
        return price_str

def get_category(title):
    """تحديد تصنيف المنتج بالعربي"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['shoe', 'shoes', 'sneaker', 'boot', 'sandal', 'footwear']):
        return "أحذية"
    elif any(word in title_lower for word in ['phone', 'smartphone', 'laptop', 'computer', 'tablet', 'headphone', 'speaker', 'charger', 'camera', 'electronic']):
        return "إلكترونيات"
    elif any(word in title_lower for word in ['furniture', 'sofa', 'bed', 'mattress', 'pillow', 'blanket', 'carpet', 'lamp', 'pot', 'pan', 'blender', 'oven', 'fridge', 'washer', 'vacuum', 'fan', 'heater', 'kitchen']):
        return "منزل ومطبخ"
    elif any(word in title_lower for word in ['perfume', 'cream', 'shampoo', 'soap', 'makeup', 'lipstick', 'beauty', 'skin', 'hair']):
        return "جمال وعناية"
    elif any(word in title_lower for word in ['sport', 'fitness', 'gym', 'running', 'yoga', 'exercise', 'workout']):
        return "رياضة"
    elif any(word in title_lower for word in ['baby', 'kids', 'children', 'toy', 'doll', 'stroller', 'diaper']):
        return "أطفال"
    elif any(word in title_lower for word in ['watch', 'jewelry', 'ring', 'necklace', 'bracelet']):
        return "ساعات ومجوهرات"
    else:
        return "ملابس وأزياء"

def generate_post_with_ai(price, original_title, product_url, category):
    """استخدام OpenAI GPT لكتابة بوست"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""اكتب منشور تسويقي قصير جداً باللهجة السعودية الأصيلة:

بيانات المنتج:
- الاسم: {original_title}
- السعر: {price} ريال
- الصنف: {category}
- الرابط: {product_url}

هيكل المنشور (4-6 أسطر بالكثير):
1. سطر: جملة تعبيرية قصيرة تشد وتحمس (باللهجة السعودية)
2. سطر: جملة تعبيرية ثانية أو اسم المنتج المترجم
3. سطر: اسم المنتج + السعر القديم vs الجديد
4. سطر: الرابط كما هو

أمثلة للجمل التعبيرية:
- "هلا بالزين كله! 🤩"
- "تخيل يا عزيزي! 😱"
- "والله العظيم يجنن! 🔥"
- "فرصة ذهبية ما تتعوض! ⚡"
- "يا هلا والله بأصحاب الذوق! 💎"
- "صدقني ما راح تندم! 👌"
- "الله يبارك، منتج فاخر وصل! ✨"
- "يا بطل، هالصيدة لك! 🏃‍♂️"

اكتب 2 جمل تعبيرية مختلفة + المنتج + السعر + الرابط

المنشور:"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "أنت مسوق سعودي أصيل، تكتب منشورات قصيرة جداً 4-6 أسطر. جملتين فقط تعبيرية تشد وتحمس باللهجة السعودية، الباقي معلومات. تستخدم إيموجي كثيرة."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.95,
            "max_tokens": 200
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
            ai_text = ai_text.strip('"').strip("'")
            return ai_text
        else:
            return None
            
    except Exception as e:
        print(f"AI Error: {e}")
        return None

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
        
        category = get_category(title)
        
        return {
            'original_title': title,
            'price': price,
            'image': image,
            'category': category,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None

def generate_post(product):
    """توليد المنشور باستخدام AI"""
    original_title = product['original_title']
    price = product['price']
    url = product['url']
    category = product['category']
    
    ai_text = generate_post_with_ai(price, original_title, url, category)
    
    if not ai_text:
        fake_old = int(int(price) * 1.4)
        # ترجمة يدوية بسيطة لو AI فشل
        arabic_name = original_title.split()[0] if len(original_title.split()) > 0 else "منتج رائع"
        ai_text = f"""هلا بالزين كله! 🤩✨
يا عزيزي، {arabic_name} وصل بقوة! 🔥
كان بـ {fake_old} ريال والحين بـ {price} بس! 💰😱
{url}"""
    
    if url not in ai_text:
        ai_text = ai_text + f"\n{url}"
    
    return ai_text

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
        
        wait_msg = bot.reply_to(message, "⏳ جاري كتابة المنشور...")
        
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
    print("🚀 Bot starting...")
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot running! 2 expressive lines only.")
    bot.infinity_polling()
