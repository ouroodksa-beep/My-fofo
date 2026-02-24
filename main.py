import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- الإعدادات النهائية ---
# تم استخدام المفتاح من حافظة جوالك
AXESSO_API_KEY = "fa4beb785ae545dd8e42395f875f4b17"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Axesso API is Active & Fast!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data_api(short_url):
    try:
        # فك الرابط المختصر بسرعة عالية
        with requests.Session() as s:
            r = s.head(short_url, allow_redirects=True, timeout=7)
            long_url = r.url
            
            # استخراج ASIN بدقة
            asin = None
            if "/dp/" in long_url: asin = long_url.split("/dp/")[1].split("/")[0].split("?")[0]
            elif "/gp/product/" in long_url: asin = long_url.split("/gp/product/")[1].split("/")[0].split("?")[0]
            
            if not asin: return None, None

            # طلب البيانات من Axesso API
            url = "https://axesso-amazon-data-service.p.rapidapi.com/amz/amazon-lookup-product"
            headers = {
                "X-RapidAPI-Key": AXESSO_API_KEY,
                "X-RapidAPI-Host": "axesso-amazon-data-service.p.rapidapi.com"
            }
            params = {"asin": asin, "domainCode": "sa"}
            
            res = s.get(url, headers=headers, params=params, timeout=12).json()
            
            if res.get("responseStatus") == "PRODUCT_FOUND_OK":
                title = res.get("productTitle", "منتج مميز")
                price = res.get("price", "شيك بالرابط")
                img = res.get("imageUrlList", [None])[0]
                
                # تنسيق الاسم المختصر
                short_title = (title[:55] + '..') if len(title) > 55 else title
                caption = f"🔥 **لقطة اليوم**\n\n📦 **{short_title}**\n💸 **السعر:** {price} ريال\n\n🔗 **للطلب:** {short_url}"
                return caption, img
    except Exception as e:
        print(f"API Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn" in m.text:
        # حل مشكلة التعارض 409 فوراً
        try:
            bot.delete_webhook(drop_pending_updates=True)
        except:
            pass
            
        status = bot.reply_to(m, "⏳ ثواني أجيب لك السعر والبيانات...")
        
        caption, img = get_amazon_data_api(m.text)
        if caption:
            if img:
                bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
            else:
                bot.send_message(CHAT_ID, caption, parse_mode="Markdown")
            bot.delete_message(m.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ الرابط لم يرد، تأكدي من تفعيل الاشتراك (Subscribe) في RapidAPI.", m.chat.id, status.message_id)

if __name__ == "__main__":
    # تنظيف شامل للجلسات عند التشغيل
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    Thread(target=run_flask).start()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
