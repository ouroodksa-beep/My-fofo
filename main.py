import requests
import telebot
import random
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
# ضعي الـ Key الجديد من موقع RapidAPI (خدمة Axesso)
AXESSO_API_KEY = "291c5dc917msh1d653eaeac8aa90p18c689jsn69d6b6d5aed7"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data(short_url):
    try:
        # 1. فك الرابط المختصر
        res_head = requests.head(short_url, allow_redirects=True, timeout=10)
        long_url = res_head.url
        
        # 2. استخراج ASIN
        asin = None
        if "/dp/" in long_url: asin = long_url.split("/dp/")[1].split("/")[0].split("?")[0]
        elif "/gp/product/" in long_url: asin = long_url.split("/gp/product/")[1].split("/")[0].split("?")[0]
        
        if not asin: return None, None

        # 3. الطلب من Axesso
        url = "https://axesso-amazon-data-service.p.rapidapi.com/amz/amazon-lookup-product"
        headers = {
            "X-RapidAPI-Key": AXESSO_API_KEY,
            "X-RapidAPI-Host": "axesso-amazon-data-service.p.rapidapi.com"
        }
        params = {"asin": asin, "domainCode": "sa"}
        
        res = requests.get(url, headers=headers, params=params).json()
        
        if res.get("responseStatus") == "PRODUCT_FOUND_OK":
            title = res.get("productTitle", "منتج مميز")
            # اختصار الاسم لسطر واحد
            short_title = (title[:45] + '..') if len(title) > 45 else title
            price = res.get("price", "شيك بالرابط")
            img = res.get("imageUrlList", [None])[0]
            
            phrase = random.choice(["لقطة اليوم 🔥", "يا هلا بالزين ✨", "شي فاخر 👌"])
            caption = f"🔥 **{phrase}**\n\n📦 **المنتج:** {short_title}\n💸 **السعر:** {price} ريال\n\n🔗 **رابط الطلب:** {short_url}"
            return caption, img
    except: pass
    return None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        bot.delete_webhook(drop_pending_updates=True) # حل مشكلة Conflict 409
        caption, img = get_amazon_data(m.text)
        if caption and img:
            bot.send_photo(CHAT_ID, img, caption=caption, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ المعذرة، الرابط ما سحب البيانات، تأكدي من الـ API Key الجديد.")

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_flask).start() # حل مشكلة Port في Render
    bot.infinity_polling()
