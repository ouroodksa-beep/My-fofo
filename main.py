import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- الإعدادات الجديدة ---
# احصلي على مفتاحك من RapidAPI (بديل راين فورست الموقوف)
AXESSO_API_KEY = "65e7b2c367c24afd842bb1597071ae21"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Axesso Bot is Live!"

def run_flask():
    # حل مشكلة Port scan في Render لضمان استمرار الخدمة
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data(short_url):
    try:
        # فك الرابط المختصر (amzn.to) لضمان سحب البيانات
        r_head = requests.head(short_url, allow_redirects=True, timeout=10)
        long_url = r_head.url
        
        # استخراج الـ ASIN من الرابط (Axesso يحتاج الـ ASIN غالباً)
        asin = long_url.split("/dp/")[1].split("/")[0] if "/dp/" in long_url else None
        if not asin: asin = long_url.split("/gp/product/")[1].split("/")[0] if "/gp/product/" in long_url else None

        url = "https://axesso-amazon-data-service.p.rapidapi.com/amz/amazon-lookup-product"
        querystring = {"asin": asin, "domainCode": "sa"} # نطاق السعودية

        headers = {
            "X-RapidAPI-Key": AXESSO_API_KEY,
            "X-RapidAPI-Host": "axesso-amazon-data-service.p.rapidapi.com"
        }

        res = requests.get(url, headers=headers, params=querystring).json()
        
        if res.get("responseStatus") == "PRODUCT_FOUND_OK":
            title = res.get("productTitle", "منتج مميز")
            # --- اختصار الاسم لسطر واحد (بحدود 45 حرف) ---
            short_title = (title[:45] + '..') if len(title) > 45 else title
            
            price = res.get("price", "شيك بالرابط")
            img = res.get("imageUrlList", [None])[0]
            
            phrase = random.choice(["يا هلا بالزين ✨", "لقطة اليوم 🔥", "شي فاخر 👌", "خذه وأنت مغمض 😎"])
            
            caption = (
                f"🔥 **{phrase}**\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💸 **السعر:** {price} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, img
    except Exception as e:
        print(f"Error fetching from Axesso: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        # حل مشكلة التعارض 409 بمسح التحديثات القديمة
        bot.delete_webhook(drop_pending_updates=True)
        
        caption, img = get_amazon_data(m.text)
        if caption and img:
            bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ المعذرة، ما قدرت أسحب البيانات من المصدر الجديد، تأكدي من الـ API Key.")

if __name__ == "__main__":
    # تنظيف التعارض عند بداية التشغيل
    bot.delete_webhook(drop_pending_updates=True)
    
    # تشغيل Flask في خيط منفصل لإبقاء Render شغال
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 البوت انطلق باستخدام Axesso API...")
    bot.infinity_polling()
