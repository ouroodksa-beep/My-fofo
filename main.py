import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Server is Live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data(short_url):
    try:
        # خطوة أساسية: فك الرابط المختصر لجلب البيانات بنجاح
        res_head = requests.head(short_url, allow_redirects=True, timeout=10)
        long_url = res_head.url
        
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',
            'amazon_domain': 'amazon.sa'
        }
        response = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if response.get("success"):
            p = response.get("product", {})
            title = p.get("title", "منتج مميز")
            # قص الاسم لسطر واحد أنيق (45 حرف)
            short_title = (title[:45] + '..') if len(title) > 45 else title
            
            price = p.get("buybox_winner", {}).get("price", {}).get("value", "شيك بالرابط")
            img = p.get("images", [{}])[0].get("link") or p.get("main_image", {}).get("link")
            
            phrase = random.choice(["يا هلا بالزين ✨", "لقطة اليوم 🔥", "شي فاخر 👌", "خذه وأنت مغمض 😎"])
            
            caption = (
                f"🔥 **{phrase}**\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💸 **السعر:** {price} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, img
    except Exception as e:
        print(f"Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض Conflict 409 نهائياً
        bot.delete_webhook(drop_pending_updates=True)
        cap, img = get_amazon_data(m.text)
        if cap and img:
            bot.send_photo(CHAT_ID, img, caption=cap, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ المعذرة، ما قدرت أسحب البيانات بالعربي، جربي رابط ثاني.")

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling()
