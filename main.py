import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Perfectly!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data(url):
    # استخدام الوسيط لتجنب الحظر والبطء
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    try:
        res = requests.get(proxy_url, timeout=30)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # سحب البيانات
        title_tag = soup.find(id="productTitle")
        if not title_tag:
            return None, None
        
        title = title_tag.get_text().strip()
        price_tag = soup.find("span", {"class": "a-price-whole"})
        price = price_tag.get_text().strip() if price_tag else "شيك بالرابط"
        
        img_tag = soup.find("img", {"id": "landingImage"})
        img = img_tag.get("src") if img_tag else None
        
        caption = f"📦 **{title[:50]}..**\n💸 **السعر:** {price} ريال\n🔗 {url}"
        return caption, img
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn" in m.text:
        # حل مشكلة التعارض 409
        try:
            bot.delete_webhook(drop_pending_updates=True)
        except:
            pass
            
        msg = bot.reply_to(m, "⏳ ثواني أجيب لك العلم من أمازون...")
        caption, img = get_amazon_data(m.text)
        
        if caption:
            if img:
                bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
            else:
                bot.send_message(CHAT_ID, caption, parse_mode="Markdown")
            bot.delete_message(m.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ عذراً، لم أتمكن من قراءة البيانات. تأكدي من الرابط.", m.chat.id, msg.message_id)

if __name__ == "__main__":
    # مسح التعارض عند التشغيل
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    Thread(target=run_flask).start()
    bot.infinity_polling()
