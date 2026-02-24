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
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data(short_url):
    try:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = session.head(short_url, allow_redirects=True, timeout=10)
        long_url = r.url
        
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',
            'amazon_domain': 'amazon.sa'
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            product = res.get("product", {})
            title = product.get("title", "منتج مميز")
            # جعل الاسم في سطر واحد مختصر (45 حرف)
            short_title = (title[:45] + '..') if len(title) > 45 else title
            
            price = product.get("buybox_winner", {}).get("price", {}).get("value", "شيك بالرابط")
            img = product.get("images", [{}])[0].get("link") or product.get("main_image", {}).get("link")
            
            phrases = ["يا هلا بالزين ✨", "لقطة اليوم 🔥", "شي فاخر 👌", "خذه وأنت مغمض 😎"]
            shorthand = random.choice(phrases)
            
            caption = (
                f"🔥 **{shorthand}**\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💸 **السعر:** {price} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, img
    except Exception as e:
        print(f"Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle_links(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض (Conflict 409)
        try:
            bot.delete_webhook(drop_pending_updates=True)
        except:
            pass
            
        caption, img = get_amazon_data(m.text)
        if caption and img:
            bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ المعذرة، الرابط ما سحب البيانات بالعربي، جربي رابط ثاني.")

if __name__ == "__main__":
    # تنظيف التعارض عند التشغيل
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
        
    # تشغيل المنفذ الوهمي لإرضاء Render
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 البوت يعمل الآن...")
    bot.infinity_polling()
