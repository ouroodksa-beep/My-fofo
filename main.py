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
SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

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

def check_channel():
    """فحص القناة والصلاحيات"""
    try:
        chat = bot.get_chat(CHANNEL_ID)
        print(f"✅ Channel found: {chat.title} (ID: {chat.id})")
        
        # فحص عضوية البوت
        member = bot.get_chat_member(CHANNEL_ID, bot.get_me().id)
        print(f"✅ Bot status: {member.status}")
        
        if member.status not in ['administrator', 'member']:
            print("❌ Bot is not a member/admin!")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Channel error: {e}")
        return False

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
        
        return {
            'title': title[:80],
            'price': price,
            'image': image,
            'url': f"https://www.amazon.sa/dp/{asin}"
        }
                
    except Exception as e:
        print(f"❌ Scraper error: {e}")
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
        
        wait_msg = bot.reply_to(message, "⏳ جاري القراءة...")
        
        # فحص القناة أولاً
        if not check_channel():
            bot.edit_message_text(
                "❌ البوت ما عنده صلاحيات في القناة!\n\n"
                "الحل:\n"
                "1. روحي @ouroodksa\n"
                "2. Administrators → Add Administrator\n"
                "3. ضيفي البوت واعطيه جميع الصلاحيات",
                chat_id,
                wait_msg.message_id
            )
            return
        
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
        
        # محاولة النشر
        try:
            post = generate_post(product)
            print(f"📝 Post: {post[:100]}...")
            
            # إرسال للقناة
            if product.get('image'):
                print(f"🖼️ Sending photo to {CHANNEL_ID}...")
                sent = bot.send_photo(CHANNEL_ID, product['image'], caption=post)
                print(f"✅ Photo sent! Message ID: {sent.message_id}")
            else:
                print(f"📤 Sending text to {CHANNEL_ID}...")
                sent = bot.send_message(CHANNEL_ID, post)
                print(f"✅ Text sent! Message ID: {sent.message_id}")
            
            # نجاح
            bot.edit_message_text(
                f"✅ تم النشر!\n\n{product['title'][:40]}...\n{product['price']} ريال",
                chat_id,
                wait_msg.message_id
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Publish error: {error_msg}")
            
            if "chat not found" in error_msg.lower():
                bot.edit_message_text(
                    "❌ القناة @ouroodksa ما لقيتها!\n\nتأكدي:\n1. الاسم مكتوب صح\n2. القناة عامة (Public)",
                    chat_id,
                    wait_msg.message_id
                )
            elif "not enough rights" in error_msg.lower() or "forbidden" in error_msg.lower():
                bot.edit_message_text(
                    "❌ البوت ما عنده صلاحيات!\n\nروحي @ouroodksa → Administrators → ضيفي البوت → فعلي 'Post Messages'",
                    chat_id,
                    wait_msg.message_id
                )
            elif "wrong file identifier" in error_msg.lower() or "failed to get http url" in error_msg.lower():
                # خطأ في الصورة، جرب نص فقط
                try:
                    bot.send_message(CHANNEL_ID, post)
                    bot.edit_message_text(
                        "✅ تم النشر (بدون صورة)\n\nالصورة ما رفعت بس المنشور نزل!",
                        chat_id,
                        wait_msg.message_id
                    )
                except Exception as e2:
                    bot.edit_message_text(
                        f"❌ فشل النشر نهائياً: {str(e2)[:100]}",
                        chat_id,
                        wait_msg.message_id
                    )
            else:
                bot.edit_message_text(
                    f"❌ خطأ غير متوقع: {error_msg[:200]}",
                    chat_id,
                    wait_msg.message_id
                )

def keep_alive():
    while True:
        time.sleep(60)

if __name__ == "__main__":
    print("🚀 Starting bot...")
    
    # فحص القناة عند التشغيل
    check_channel()
    
    try:
        bot.remove_webhook()
    except:
        pass
    
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    
    print("🤖 Bot running!")
    bot.infinity_polling()
