import requests
import telebot
import random
import time

# --- البيانات ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA" # تأكدي من النقطتين :
CHAT_ID = "ftwu_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# جمل سعودية مختارة بعناية
SAUDI_PHRASES = [
    "يا هلا ومسهلا بالزين ✨", "لقطة العمر يا بعدي 🔥", 
    "شي فاخر من الآخر 👌", "خذه وأنت مغمض 😎",
    "عز الله إنه كفو 🦾", "الحق ما تلحق يا ذيب 🏃‍♂️"
]

def get_real_data(short_url):
    try:
        # فك الرابط المختصر ضروري لسحب البيانات صح
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = session.head(short_url, allow_redirects=True, timeout=15, headers=headers)
        long_url = r.url
        
        # طلب البيانات بالعربي
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',
            'amazon_domain': 'amazon.sa'
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            p = res.get("product", {})
            
            # اختصار الاسم لسطر واحد فقط (بحدود 50 حرف)
            full_title = p.get("title", "منتج مميز")
            short_title = (full_title[:50] + '..') if len(full_title) > 50 else full_title
            
            # السعر والصورة
            price = p.get("buybox_winner", {}).get("price", {}).get("value", "شيك بالرابط")
            img = p.get("images", [{}])[0].get("link") or p.get("main_image", {}).get("link")
            
            phrase = random.choice(SAUDI_PHRASES)
            caption = (
                f"🔥 **{phrase}**\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💸 **السعر:** {price} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, img
    except Exception as e:
        print(f"خطأ تقني: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amzn.to" in m.text or "amazon" in m.text:
        # تنظيف التحديثات المعلقة لحل مشكلة الـ Conflict 409
        bot.delete_webhook(drop_pending_updates=True)
        
        cap, img = get_real_data(m.text)
        if cap and img:
            bot.send_photo(CHAT_ID, img, caption=cap, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ الرابط ما سحب البيانات، جربي رابط ثاني يا ذيبة.")

if __name__ == "__main__":
    # مسح الـ Webhook عند التشغيل لضمان عمل البوت في Render بدون تعارض
    bot.delete_webhook(drop_pending_updates=True)
    print("🚀 البوت السعودي شغال...")
    bot.infinity_polling()
