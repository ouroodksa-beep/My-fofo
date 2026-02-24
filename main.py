import requests
from bs4 import BeautifulSoup
import telebot
import random
import os
from flask import Flask
from threading import Thread
import time

# --- الإعدادات ---
# ضعي توقن بوتك وآيدي قناتك هنا
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home(): 
    return "Amazon Scraper is Running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data_improved(url):
    session = requests.Session()
    # هوية متصفح تبدو كأنها من جوال أندرويد حقيقي لتخطي الحجب
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # فك الرابط المختصر والوصول للصفحة
        res = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        # إذا ظهرت كلمة captcha يعني أمازون كشف البوت
        if "captcha" in res.text.lower():
            return "حجب", None
            
        soup = BeautifulSoup(res.content, "html.parser")
        
        # محاولة سحب العنوان بأكثر من طريقة (لأن أمازون يغير الكود)
        title_tag = soup.select_one('#productTitle') or soup.select_one('.a-size-large.product-title-word-break')
        if not title_tag: 
            return None, None
        
        title = title_tag.get_text().strip()
        short_title = (title[:45] + '..') if len(title) > 45 else title
        
        # سحب السعر
        price = "شيك بالرابط"
        price_tag = soup.select_one('.a-price-whole')
        if price_tag:
            price = price_tag.get_text().strip().replace(".", "")
            
        # سحب الصورة
        img_tag = soup.select_one('#landingImage') or soup.select_one('#main-image')
        img_url = img_tag.get('src') if img_tag else None
        
        phrase = random.choice(["لقطة اليوم 🔥", "يا هلا بالزين ✨", "شي فاخر 👌"])
        caption = f"🔥 **{phrase}**\n\n📦 **المنتج:** {short_title}\n💸 **السعر:** {price} ريال\n\n🔗 **رابط الطلب:** {url}"
        return caption, img_url
            
    except Exception as e:
        print(f"Scraping Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "amazon" in m.text or "amzn" in m.text:
        # تنظيف الجلسات القديمة لمنع خطأ 409
        try:
            bot.delete_webhook(drop_pending_updates=True)
        except:
            pass
            
        status_msg = bot.reply_to(m, "⏳ ثواني أجيب لك العلم من أمازون...")
        
        caption, img = get_amazon_data_improved(m.text)
        
        if caption == "حجب":
            bot.edit_message_text("❌ أمازون حجب الطلب حالياً (نظام الحماية)، جربي مرة ثانية بعد قليل.", m.chat.id, status_msg.message_id)
        elif caption:
            if img:
                bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
            else:
                bot.send_message(CHAT_ID, caption, parse_mode="Markdown")
            bot.delete_message(m.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ لم أتمكن من قراءة بيانات هذا الرابط، تأكدي أنه رابط منتج صحيح.", m.chat.id, status_msg.message_id)

if __name__ == "__main__":
    # حل مشكلة التعارض عند التشغيل في Render
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
        
    Thread(target=run_flask).start()
    print("🚀 البوت انطلق بنظام الكشط الذكي...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
