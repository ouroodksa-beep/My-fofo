import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
# تأكدي من وضع القيم الصحيحة هنا
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHANNEL_ID = "ouroodbot"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        # فك الرابط المختصر والوصول للمنتج
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # سحب الاسم والسعر
        title_tag = soup.find(id="productTitle")
        price_tag = soup.find("span", {"class": "a-price-whole"})
        
        if title_tag:
            title = title_tag.get_text().strip()
            price = price_tag.get_text().strip() if price_tag else "شيك بالرابط"
            return f"📦 **{title[:55]}..**\n💸 **السعر:** {price} ريال\n🔗 {url}"
    except Exception as e:
        print(f"Error scraping: {e}")
    return None

@bot.message_handler(func=lambda m: True)
def handle_message(m):
    if "amazon" in m.text or "amzn" in m.text:
        # حل مشكلة التعارض 409
        try:
            bot.delete_webhook(drop_pending_updates=True)
        except:
            pass
            
        wait_msg = bot.reply_to(m, "⏳ ثواني أجيب لك العلم من أمازون...")
        result = get_amazon_info(m.text)
        
        if result:
            bot.send_message(CHANNEL_ID, result, parse_mode="Markdown")
            bot.delete_message(m.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ لم أتمكن من قراءة البيانات، جربي رابطاً طويلاً.", m.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    # تنظيف الجلسات القديمة لمنع توقف البوت
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    
    # تشغيل سيرفر ويب بسيط لإبقاء البوت حياً في Render
    Thread(target=run_flask).start()
    print("🚀 البوت يعمل الآن بدون أخطاء مسافات...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
