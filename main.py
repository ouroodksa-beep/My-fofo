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
def home(): return "Scraper Bot is Live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data_scraping(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        # فك الرابط المختصر أولاً لضمان الوصول للصفحة الأصلية
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.content, "lxml")
        
        # 1. سحب العنوان
        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text().strip() if title_tag else "منتج مميز"
        short_title = (title[:45] + '..') if len(title) > 45 else title
        
        # 2. سحب السعر (نبحث في أكثر من مكان لأن أمازون يغير مكانه)
        price = "شيك بالرابط"
        price_tag = soup.find("span", {"class": "a-price-whole"})
        if price_tag:
            price = price_tag.get_text().replace(".", "").strip()
        
        # 3. سحب الصورة
        img_tag = soup.find("img", {"id": "landingImage"}) or soup.find("img", {"id": "imgBlkFront"})
        img_url = img_tag.get("src") if img_tag else None
        
        if title != "منتج مميز":
            phrase = random.choice(["لقطة اليوم 🔥", "يا هلا بالزين ✨", "شي فاخر 👌"])
            caption = f"🔥 **{phrase}**\n\n📦 **المنتج:** {short_title}\n💸 **السعر:** {price} ريال\n\n🔗 **رابط الطلب:** {url}"
            return caption, img_url
            
    except Exception as e:
        print(f"Scraping Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض 409
        bot.delete_webhook(drop_pending_updates=True)
        
        msg = bot.reply_to(m, "⏳ ثواني أجيب لك العلم...")
        
        caption, img = get_amazon_data_scraping(m.text)
        
        if caption:
            if img:
                bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
            else:
                bot.send_message(CHAT_ID, caption, parse_mode="Markdown")
            bot.delete_message(m.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ أمازون حجب الطلب حالياً، جربي مرة ثانية بعد شوي.", m.chat.id, msg.message_id)

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_flask).start()
    print("🚀 البوت يعمل الآن بنظام الكشط (بدون API)...")
    bot.infinity_polling()
