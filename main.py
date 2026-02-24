import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_data(url):
    # هوية متصفح بسيطة
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36"}
    try:
        # فك الرابط المختصر
        r = requests.get(url, headers=h, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # سحب العنوان والسعر
        t = soup.find(id="productTitle")
        p = soup.find("span", {"class": "a-price-whole"})
        
        if t:
            title = t.get_text().strip()[:50]
            price = p.get_text().strip() if p else "شيك بالرابط"
            return f"📦 **{title}**\n💸 **السعر:** {price} ريال\n🔗 {url}"
    except:
        pass
    return None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn" in m.text:
        # تنظيف التعارض فوراً
        bot.delete_webhook(drop_pending_updates=True)
        
        res = get_data(m.text)
        if res:
            bot.send_message(CHAT_ID, res, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ الرابط لم يرد، جربي رابطاً طويلاً.")

if __name__ == "__main__":
    # أهم خطوة لإنهاء خطأ 409
    bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_flask).start()
    bot.infinity_polling()
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
