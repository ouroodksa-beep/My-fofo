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
    return "Bot Active"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def expand_short_url(short_url):
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=10)
        return response.url
    except:
        return short_url

def extract_asin(url):
    if 'amzn.to' in url or 'amzn.eu' in url:
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
    try:
        price_clean = price_str.replace(',', '').replace(' ', '').strip()
        price_num = float(price_clean)
        return str(int(price_num))
    except:
        return price_str

def get_category(title):
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['shoe', 'shoes', 'sneaker', 'boot', 'sandal']):
        return "أحذية"
    elif any(word in title_lower for word in ['phone', 'laptop', 'computer', 'tablet', 'electronic']):
        return "إلكترونيات"
    elif any(word in title_lower for word in ['furniture', 'sofa', 'bed', 'kitchen']):
        return "منزل"
    elif any(word in title_lower for word in ['perfume', 'beauty', 'cream']):
        return "جمال"
    elif any(word in title_lower for word in ['sport', 'gym', 'fitness']):
        return "رياضة"
    elif any(word in title_lower for word in ['baby', 'kids', 'toy']):
        return "أطفال"
    else:
        return "ملابس"

def generate_post_with_ai(price, original_title, product_url, category):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_msg = "أنت مسوق سعودي. اكتب منشورات قصيرة. جملتين تسويقيتين فقط. وصف تفصيلي يذكر المقاس واللون. سطر فاضي بين كل جزء."
        
        user_msg = f"""اكتب منشور تسويقي باللهجة السعودية:

المنتج: {original_title}
السعر: {price} ريال
الصنف: {category}
الرابط: {product_url}

الهيكل:
1. جملة تعبيرية قصيرة
2. (سطر فاضي)
3. اسم المنتج مترجم + وصف تفصيلي (المقاس/اللون/الموديل)
4. (سطر فاضي)
5. السعر القديم vs الجديد
6. (سطر فاضي)
7. جملة تسويقية + دعوة للشراء
8. (سطر فاضي)
9. الرابط

اكتب المنشور:"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.9,
            "max_tokens": 300
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
            return ai_text
        else:
            return None
            
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def get_product_scraperapi(asin):
    try:
        amazon_url = f"https://www.amazon.sa/dp/{asin}"
        scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={amazon_url}&country_code=sa"
        
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
        
        category = get_category(title)
        
        return {
            'original_title': title,
            'price': price,
            'image': image,
            'category': category,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"Scraper error: {e}")
        return None

def generate_post(product):
    original_title = product['original_title']
    price = product['price']
    url = product['url']
    category = product['category']
    
    ai_text = generate_post_with_ai(price, original_title, url, category)
    
    if not ai_text:
        fake_old = int(int(price) * 1.4)
        words = original_title.split()[:5]
        details = " ".join(words)
        ai_text = f"""هلا بالزين!

{details} - منتج رائع بجودة عالية!

كان بـ {fake_old} ريال والحين بـ {price} بس!

فرصة ذهبية!

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
        bot.reply_to(message, "أرسلي رابط أمازون")
        return
    
    for url in urls:
        if "amazon" not in url.lower() and "amzn" not in url.lower():
            continue
        
        wait_msg = bot.reply_to(message, "جاري قراءة الرابط...")
        
        expanded_url = expand_short_url(url) if 'amzn.to' in url else url
        
        asin = extract_asin(expanded_url)
        if not asin:
            bot.edit_message_text("رابط غير صحيح", chat_id, wait_msg.message_id)
            continue
        
        product = get_product_scraperapi(asin)
        
        if not product:
            bot.edit_message_text("ما قدرت أقرأ المنتج. جربي رابط مباشر من amazon.sa", chat_id, wait_msg.message_id)
            continue
        
        try:
            post = generate_post(product)
            
            if product.get('image'):
                bot.send_photo(chat_id, product['image'], caption=post)
            else:
                bot.send_message(chat_id, post)
            
            bot.delete_message(chat_id, wait_msg.message_id)
            
        except Exception as e:
            print(f"Error: {e}")
            bot.edit_message_text(f"خطأ: {str(e)[:100]}", chat_id, wait_msg.message_id)

def keep_alive():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    print("Bot starting...")
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("Bot running!")
    bot.infinity_polling()
