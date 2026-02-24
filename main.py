import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- الإعدادات (تأكدي من التوقن والآيدي) ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok" 
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- حل مشكلة Render (فتح منفذ وهمي) ---
app = Flask('')
@app.route('/')
def home(): return "البوت يعمل بكفاءة!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- دالة سحب البيانات المختصرة ---
def get_amazon_ar(short_url):
    try:
        # فك الرابط المختصر أولاً
        r = requests.head(short_url, allow_redirects=True, timeout=10)
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
            p = res['product']
            # اختصار الاسم لسطر واحد (بحدود 45 حرف) ليكون مرتباً
            title = p.get('title', 'منتج مميز')
            short_title = (title[:45] + '..') if len(title) > 45 else title
            
            price = p.get('buybox_winner', {}).get('price', {}).get('value', 'شيك بالرابط')
            img = p.get('images', [{}])[0].get('link') or p.get('main_image', {}).get('link')
            
            phrase = random.choice(["يا هلا بالزين ✨", "لقطة العمر 🔥", "شي فاخر 👌", "خذه وأنت مغمض 😎"])
            
            caption = (
                f"🔥 **{phrase}**\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💸 **السعر:** {price} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, img
    except: return None, None

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض Conflict 409 بمسح التحديثات القديمة
        bot.delete_webhook(drop_pending_updates=True)
        cap, img = get_amazon_ar(m.text)
        if cap and img:
            bot.send_photo(CHAT_ID, img, caption=cap, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ المعذرة، ما قدرت أسحب البيانات بالعربي، جربي رابط ثاني.")

if __name__ == "__main__":
    # تنظيف التعارض عند التشغيل
    bot.delete_webhook(drop_pending_updates=True)
    # تشغيل المنفذ الوهمي لإرضاء Render
    Thread(target=run_flask).start()
    print("🚀 انطلق البوت السعودي!")
    bot.infinity_polling()
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            p = res['product']
            # اختصار الاسم لسطر واحد (بحدود 45 حرف)
            title = p.get('title', 'منتج مميز')
            short_title = (title[:45] + '..') if len(title) > 45 else title
            
            price = p.get('buybox_winner', {}).get('price', {}).get('value', 'شيك بالرابط')
            img = p.get('images', [{}])[0].get('link') or p.get('main_image', {}).get('link')
            
            phrase = random.choice(["يا هلا بالزين ✨", "لقطة العمر 🔥", "شي فاخر 👌", "خذه وأنت مغمض 😎"])
            return f"🔥 **{phrase}**\n\n📦 **المنتج:** {short_title}\n💸 **السعر:** {price} ريال\n\n🔗 {short_url}", img
    except: return None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض Conflict 409
        bot.delete_webhook(drop_pending_updates=True)
        cap, img = get_data(m.text)
        if cap and img:
            bot.send_photo(CHAT_ID, img, caption=cap, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ ما قدرت أسحب البيانات، جرب رابط ثاني.")

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_flask).start() # تشغيل المنفذ الوهمي
    print("🚀 انطلقنا!")
    bot.infinity_polling()
