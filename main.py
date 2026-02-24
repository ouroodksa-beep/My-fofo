import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- الإعدادات (تأكدي من صحة التوقن والآيدي) ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok" # تأكدي من وجود النقطتين :
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- حل مشكلة Render (فتح منفذ وهمي لإرضاء النظام في الخطة المجانية) ---
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال بأفضل حال!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- دالة سحب البيانات الاحترافية ---
def get_amazon_data(short_url):
    try:
        # فك الرابط المختصر ضروري جداً لسحب البيانات صح
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = session.head(short_url, allow_redirects=True, timeout=15, headers=headers)
        long_url = r.url
        
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',    # جلب الاسم بالعربي
            'amazon_domain': 'amazon.sa' # التركيز على متجر السعودية
        }
        
        response = requests.get('https://api.rainforestapi.com/request', params=params)
        res = response.json()
        
        if res.get("success"):
            product = res.get("product", {})
            
            # --- اختصار الاسم لسطر واحد (بحدود 45 حرف) ---
            full_title = product.get("title", "منتج مميز")
            short_title = (full_title[:45] + '..') if len(full_title) > 45 else full_title
            
            # السعر والصورة بأعلى جودة
            price = product.get("buybox_winner", {}).get("price", {}).get("value", "شيك بالرابط")
            img = product.get("images", [{}])[0].get("link") or product.get("main_image", {}).get("link")
            
            # جمل سعودية عشوائية
            phrases = ["يا هلا بالزين ✨", "لقطة اليوم 🔥", "شي فاخر من الآخر 👌", "خذه وأنت مغمض 😎"]
            shorthand = random.choice(phrases)
            
            caption = (
                f"🔥 **{shorthand}**\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💸 **السعر:** {price} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, img
    except Exception as e:
        print(f"Error fetching data: {e}")
    return None, None

# --- معالج الرسائل ---
@bot.message_handler(func=lambda m: True)
def handle_amazon_links(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # مسح التعارض القديم عند كل طلب (Conflict 409)
        bot.delete_webhook(drop_pending_updates=True)
        
        cap, img = get_amazon_data(m.text)
        if cap and img:
            bot.send_photo(CHAT_ID, img, caption=cap, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ المعذرة، الرابط ما سحب البيانات بالعربي، جرب رابط ثاني يا ذيبة.")

# --- التشغيل المزدوج لضمان عدم توقف Render ---
if __name__ == "__main__":
    # تنظيف التعارض عند البداية
    bot.delete_webhook(drop_pending_updates=True)
    
    # تشغيل Flask في خيط منفصل لإرضاء فحص المنفذ في Render
    t = Thread(target=run_flask)
    t.start()
    
    print("🚀 البوت يعمل الآن على الخطة المجانية...")
    bot.infinity_polling()
