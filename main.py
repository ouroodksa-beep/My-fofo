import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
# سجلي في ScraperAPI وخذي المفتاح
SCRAPER_API_KEY = "fb7742b2e62f3699d5059eea890268dd"
TELEGRAM_TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHAT_ID = "ouroodbot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "ScraperAPI System is Live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_amazon_data_free(url):
    # إرسال الطلب عبر الوسيط لتجنب الحجب
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    
    try:
        res = requests.get(proxy_url, timeout=30)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # سحب البيانات من صفحة أمازون السعودية
        title_tag = soup.find(id="productTitle")
        if not title_tag: return None, None
        
        title = title_tag.get_text().strip()
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
        # تنظيف الجلسات لمنع خطأ 409
        bot.delete_webhook(drop_pending_updates=True)
        
        msg = bot.reply_to(m, "⌛ لحظات، أحاول تخطي حماية أمازون...")
        caption, img = get_amazon_data_free(m.text)
        
        if caption:
            if img: bot.send_photo(CHAT_ID, img, caption=caption)
            else: bot.send_message(CHAT_ID, caption)
            bot.delete_message(m.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ فشل تخطي الحماية، جربي مرة أخرى.", m.chat.id, msg.message_id)

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True) # حل مشكلة التعارض
    Thread(target=run_flask).start()
    bot.infinity_polling()

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
