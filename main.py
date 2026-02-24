import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- إعدادات البوت ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
CHAT_ID = "ftwu_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- خدعة الخطة المجانية (Flask لفتح منفذ وهمي) ---
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال زي الفل!"

def run_flask():
    # Render يعطي المنفذ تلقائياً في البيئة
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- دالة جلب البيانات ---
def get_amazon_data(short_url):
    try:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        # فك الرابط المختصر ضروري جداً
        r = session.head(short_url, allow_redirects=True, timeout=15, headers=headers)
        long_url = r.url
        
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE', # الاسم بالعربي
            'amazon_domain': 'amazon.sa'
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            p = res.get("product", {})
            # اختصار الاسم لسطر واحد (بحدود 45 حرف) ليكون مرتباً
            title = p.get("title", "منتج رهيب")
            short_title = (title[:45] + '..') if len(title) > 45 else title
            
            price = p.get("buybox_winner", {}).get("price", {}).get("value", "شيك بالرابط")
            img = p.get("images", [{}])[0].get("link") or p.get("main_image", {}).get("link")
            
            phrase = random.choice(["يا هلا بالزين ✨", "لقطة العمر 🔥", "شي فاخر 👌", "خذه وأنت مغمض 😎"])
            
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

# --- معالج الرسائل ---
@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض Conflict 409
        bot.delete_webhook(drop_pending_updates=True)
        cap, img = get_amazon_data(m.text)
        if cap and img:
            bot.send_photo(CHAT_ID, img, caption=cap, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ ما قدرت أسحب البيانات، جرب رابط ثاني.")

# --- التشغيل المزدوج ---
if __name__ == "__main__":
    # تنظيف التعارض عند التشغيل
    bot.delete_webhook(drop_pending_updates=True)
    
    # تشغيل Flask في سطر منفصل لإرضاء Render
    t = Thread(target=run_flask)
    t.start()
    
    print("🚀 البوت يعمل على الخطة المجانية...")
    bot.infinity_polling()
