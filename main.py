import requests
import time
from telebot import TeleBot # تأكدي من إضافة pyTelegramBotAPI في ملف requirements.txt

# --- بياناتك (يفضل وضعها في Environment Variables على Render) ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "ضع_توقن_البوت_هنا"
CHAT_ID = "ftwu_bot"

bot = TeleBot(TELEGRAM_TOKEN)

def get_amazon_details(short_url):
    try:
        # 1. فك الرابط القصير
        session = requests.Session()
        resp = session.head(short_url, allow_redirects=True, timeout=10)
        long_url = resp.url
        
        # 2. جلب البيانات من Rainforest
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE'
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            product = res.get("product", {})
            title = product.get("title", "بدون عنوان")
            price = product.get("buybox_winner", {}).get("price", {}).get("value", "غير متوفر")
            
            # أعلى جودة صورة
            images = product.get("images", [])
            img = images[0].get("link") if images else product.get("main_image", {}).get("link")
            
            caption = f"👌 **خيار ذكي**\n\n{title}\n\n💸 **السعر:** {price} ريال\n\n🌐 **الرابط:** {short_url}"
            return caption, img
    except Exception as e:
        print(f"Error: {e}")
    return None, None

# لجعل الكود يعمل كبوت ينتظر الرسائل (هذا يمنع Render من إغلاق التطبيق)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "amzn.to" in url or "amazon" in url:
        bot.reply_to(message, "⏳ جاري استخراج العرض...")
        text, image = get_amazon_details(url)
        if text and image:
            bot.send_photo(CHAT_ID, image, caption=text, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ فشل سحب بيانات المنتج. تأكد من الرابط.")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling() # تجعل البرنامج لا يتوقف
