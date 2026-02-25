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

def format_price(price_str):
    """إزالة النقطة العشرية من السعر"""
    try:
        price_clean = price_str.replace(',', '').replace(' ', '').strip()
        price_num = float(price_clean)
        return str(int(price_num))
    except:
        return price_str

def count_words(text):
    """عد الكلمات"""
    return len(text.split())

def generate_post_with_ai(price, original_title, product_url):
    """استخدام OpenAI GPT لكتابة بوست"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""اكتب منشور تسويقي باللهجة السعودية الأصيلة (ابن بلد):

بيانات المنتج:
- الاسم: {original_title}
- السعر: {price} ريال
- الرابط: {product_url}

الشروط الصارمة:
1. عدد الكلمات: بين 100 إلى 160 كلمة بالضبط (لا أقل ولا أكثر)
2. اكتب اسم المنتج مترجم للعربي بشكل واضح في أول المنشور
3. استخدم الرابط كما هو: {product_url} (لا تختصره)
4. اللهجة السعودية الأصيلة فقط (هلا، يا هلا، يا عزيزي، والله، صدقني، يا جماعة)
5. أسلوب يشد ويحمس للصيدات (عروض، خصومات، فرص، بأسعار خيالية)
6. استخدم إيموجي بكثرة ومناسبة
7. اذكر السعر القديم (أعلى من {price} بـ 30-50%) ثم السعر الجديد {price} ريال
8. اكتب بأسلوب صديق محترف يعرف يسوق ويبيع

الهيكل المطلوب:
- افتتاحية جذابة (هلا بالزين!)
- اسم المنتج مترجم
- وصف شيق يحمس
- مقارنة السعر (القديم vs الجديد)
- دعوة للشراء الآن
- الرابط كما هو

اكتب المنشور مباشرة:"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "أنت مسوق سعودي أصيل، خبير في الكتابة التسويقية باللهجة السعودية. تكتب منشورات طويلة نسبياً (100-160 كلمة) تجذب العملاء وتحمسهم للشراء. تستخدم إيموجي كثيرة وتكتب بأسلوب ابن البلد."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
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
            
            word_count = count_words(ai_text)
            if word_count < 100:
                return expand_post(ai_text, headers, price, product_url)
            elif word_count > 160:
                return shorten_post(ai_text, headers, price, product_url)
            
            return ai_text
        else:
            return None
            
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def expand_post(short_text, headers, price, product_url):
    """توسيع المنشور القصير"""
    try:
        prompt = f"""وسّع هذا المنشور ليصبح بين 100-160 كلمة:

{short_text}

أضف:
- وصف أكثر تفصيل للمنتج
- فوائد إضافية
- دعوة للشراء أقوى
- حافظ على الرابط: {product_url}
- حافظ على السعر: {price} ريال

النتيجة:"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
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
            return result['choices'][0]['message']['content'].strip()
        return short_text
    except:
        return short_text

def shorten_post(long_text, headers, price, product_url):
    """تختصير المنشور الطويل"""
    try:
        prompt = f"""اختصر هذا المنشور ليصبح بين 100-160 كلمة:

{long_text}

احتفظ بالأهم:
- اسم المنتج
- السعر القديم والجديد ({price} ريال)
- الرابط: {product_url}
- دعوة للشراء

النتيجة:"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
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
            return result['choices'][0]['message']['content'].strip()
        return long_text
    except:
        return long_text

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
        
        return {
            'original_title': title,
            'price': price,
            'image': image,
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
    
    ai_text = generate_post_with_ai(price, original_title, url)
    
    if not ai_text:
        fake_old = int(int(price) * 1.4)
        ai_text = f"""هلا بالزين كله! 🤩👋

يا عزيزي وصلنا لك {original_title} بقوة! 🔥💪

هذا المنتج يجنن والله، جودة عالية وأداء ممتاز، كل اللي جربه مدح فيه وقال إنه يستاهل كل ريال! ⭐👌

تخيل يا طويل العمر كان بـ {fake_old} ريال والحين بنقدملك بـ {price} ريال فقط! 😱💰

فرصة ذهبية ما تتعوض، الكمية محدودة والعرض لفترة قصيرة! ⚡🔥

لا تفوتك الصيدة يا بطل! 🏃‍♂️💨

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
    
    print("🤖 Bot running! 100-160 words posts.")
    bot.infinity_polling()
