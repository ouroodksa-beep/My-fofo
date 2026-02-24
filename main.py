import requests
from bs4 import BeautifulSoup
import telebot
import random
import os
from flask import Flask
from threading import Thread
import time

# --- الإعدادات ---
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Scraper System is Online!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data_improved(url):
    # قائمة هويات مختلفة لخداع أمازون
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/"
    }
    
    try:
        # فك الرابط المختصر أولاً
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(res.content, "html.parser")
        
        # سحب العنوان
        title_tag = soup.find("span", {"id": "productTitle"})
        if not title_tag: return None, None # إذا لم يجد العنوان يعني تم الحجب
        
        title = title_tag.get_text().strip()
        short_title = (title[:45] + '..') if len(title) > 45 else title
        
        # سحب السعر
        price = "شيك بالرابط"
        price_whole = soup.find("span", {"class": "a-price-whole"})
        if price_whole:
            price = price_whole.get_text().strip().replace(".", "")
        
        # سحب الصورة
        img_tag = soup.find("img", {"id": "landingImage"}) or soup.find("img", {"id": "imgBlkFront"})
        img_url = img_tag.get("src") if img_tag else None
        
        phrase = random.choice(["لقطة اليوم 🔥", "يا هلا بالزين ✨", "شي فاخر 👌"])
        caption = f"🔥 **{phrase}**\n\n📦 **المنتج:** {short_title}\n💸 **السعر:** {price} ريال\n\n🔗 **رابط الطلب:** {url}"
        return caption, img_url
            
    except Exception as e:
        print(f"Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "amazon" in m.text or "amzn" in m.text:
        # حل مشكلة التعارض 409
        bot.delete_webhook(drop_pending_updates=True)
        
        status_msg = bot.reply_to(m, "⏳ ثواني أجيب لك العلم...")
        
        caption, img = get_amazon_data_improved(m.text)
        
        if caption:
            if img:
                bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
            else:
                bot.send_message(CHAT_ID, caption, parse_mode="Markdown")
            bot.delete_message(m.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ أمازون حجب الطلب حالياً، جربي مرة ثانية بعد شوي أو استخدمي رابطاً طويلًا.", m.chat.id, status_msg.message_id)

if __name__ == "__main__":
    # تنظيف التعارض نهائياً عند التشغيل
    bot.delete_webhook(drop_pending_updates=True)
    
    Thread(target=run_flask).start()
    print("🚀 انطلق البوت بنظام الكشط المطور...")
    bot.infinity_polling()
