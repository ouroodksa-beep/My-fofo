import requests
import telebot
import random
import sys

# --- بياناتك (تأكدي إنها صحيحة) ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA" 
CHAT_ID = "ftwu_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# عبارات سعودية تفتح النفس
SAUDI_PHRASES = ["يا هلا ومسهلا بالزين ✨", "لقطة العمر يا بعدي 🔥", "شي فاخر من الآخر 👌", "خذه وأنت مغمض 😎"]

def get_amazon_details_ar(short_url):
    try:
        # 1. أهم خطوة: فك الرابط المختصر لـ URL طويل حقيقي
        # هذا اللي بيحل مشكلة "منتج مميز" اللي تكررت عندك
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = session.head(short_url, allow_redirects=True, timeout=15, headers=headers)
        long_url = resp.url
        
        # 2. طلب البيانات من Rainforest (إجبار اللغة العربية)
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE', # لجلب الاسم بالعربي
            'amazon_domain': 'amazon.sa'
        }
        
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            product = res.get("product", {})
            
            # --- اختصار الاسم لسطر واحد (60 حرف كحد أقصى) ---
            full_title = product.get("title", "منتج رهيب")
            short_title = (full_title[:60] + '..') if len(full_title) > 60 else full_title
            
            # استخراج السعر الحقيقي
            price_info = product.get("buybox_winner", {}).get("price", {})
            if not price_info: price_info = product.get("price", {})
            price_value = price_info.get("value", "شيك بالرابط")
            
            # استخراج الصورة الأصلية
            images = product.get("images", [])
            image_url = images[0].get("link") if images else product.get("main_image", {}).get("link")
            
            phrase = random.choice(SAUDI_PHRASES)
            
            caption = (
                f"{phrase}\n\n"
                f"📦 **المنتج:** {short_title}\n"
                f"💰 **السعر:** {price_value} ريال\n\n"
                f"🔗 **رابط الطلب:** {short_url}"
            )
            return caption, image_url
    except Exception as e:
        print(f"Error: {e}")
    return None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amzn.to" in m.text or "amazon" in m.text:
        # حذف الرسالة اللي تطلع "منتج مميز" واستبدالها بالبيانات الصح
        caption, photo = get_amazon_details_ar(m.text)
        if caption and photo:
            bot.send_photo(CHAT_ID, photo, caption=caption, parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ الرابط ما سحب البيانات صح، جرب رابط ثاني يا ذيب.")

if __name__ == "__main__":
    bot.infinity_polling()
