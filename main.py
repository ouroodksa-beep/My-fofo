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
CHANNEL_ID = "@ouroodksa"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- Proxy مجاني (يتغير تلقائياً) ---
def get_free_proxy():
    """جلب proxy مجاني"""
    try:
        # قائمة proxies مجانية
        proxies = [
            "http://20.206.106.192:80",
            "http://20.111.54.16:80",
            "http://20.24.43.214:80",
        ]
        return random.choice(proxies)
    except:
        return None

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
    
    # فك الروابط المختصرة
    if 'amzn.to' in url or 'amzn.eu' in url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            final_url = response.url
            for pattern in patterns:
                match = re.search(pattern, final_url, re.IGNORECASE)
                if match:
                    return match.group(1).upper()
        except:
            pass
    return None

def get_product_fast(asin):
    """Scraping سريع بدون انتظار طويل"""
    urls = [
        f"https://www.amazon.sa/dp/{asin}",
        f"https://www.amazon.com/dp/{asin}",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    for url in urls:
        try:
            # ⏱️ timeout قصير 10 ثواني
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # العنوان
                title_elem = soup.select_one('#productTitle, h1.a-size-large')
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                title = re.sub(r'\s+', ' ', title)
                
                # السعر
                price = None
                price_elem = soup.select_one('.a-price .a-offscreen, .a-price-whole')
                if price_elem:
                    price_text = price_elem.get_text()
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = price_match.group()
                
                # الصورة
                image = None
                img_elem = soup.select_one('#landingImage')
                if img_elem:
                    image = img_elem.get('data-old-hires') or img_elem.get('src')
                
                if title and price:
                    return {
                        'title': title[:80],
                        'price': price,
                        'image': image,
                        'url': f"https://www.amazon.sa/dp/{asin}"
                    }
                    
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    return None

def generate_post(product):
    """توليد المنشور"""
    title = product['title']
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
        
        # ⏱️ رسالة سريعة
        wait_msg = bot.reply_to(message, "⏳ جاري القراءة...")
        
        asin = extract_asin(url)
        if not asin:
            bot.edit_message_text("❌ رابط غير صحيح", chat_id, wait_msg.message_id)
            continue
        
        # ⏱️ مهلة 15 ثانية
        product = get_product_fast(asin)
        
        if product:
            try:
                post = generate_post(product)
                
                if product.get('image'):
                    bot.send_photo(CHANNEL_ID, product['image'], caption=post)
                else:
                    bot.send_message(CHANNEL_ID, post)
                
                bot.edit_message_text(
                    f"✅ تم النشر!\n\n{product['title'][:40]}...\n{product['price']} ريال",
                    chat_id,
                    wait_msg.message_id
                )
                
            except Exception as e:
                print(f"Error: {e}")
                bot.edit_message_text("❌ خطأ في النشر", chat_id, wait_msg.message_id)
        else:
            bot.edit_message_text(
                "❌ ما قدرت أقرأ المنتج\n\n"
                "💡 جربي:\n"
                "1. رابط amazon.sa مباشرة\n"
                "2. تأكدي المنتج متوفر\n"
                "3. جربي رابط ثاني",
                chat_id,
                wait_msg.message_id
            )

def keep_alive():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot started!")
    bot.infinity_polling()
