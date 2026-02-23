import requests
import telebot
import time

# --- 1. إعدادات الوصول (تأكدي من صحة التوقن ووجود النقطتين :) ---
# نصيحة: تأكدي من نسخ التوقن كاملاً من BotFather
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
CHAT_ID = "ftwu_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_amazon_details_ar(short_url):
    """دالة استخراج بيانات المنتج باللغة العربية وأعلى جودة صورة"""
    try:
        # أ- فك الرابط المختصر amzn.to
        session = requests.Session()
        resp = session.head(short_url, allow_redirects=True, timeout=10)
        long_url = resp.url
        print(f"DEBUG: Long URL found: {long_url}")

        # ب- طلب البيانات من Rainforest مع تفعيل اللغة العربية
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',  # لضمان الاسم بالعربي
            'amazon_domain': 'amazon.sa' # لضمان نتائج متجر السعودية
        }
        
        response = requests.get('https://api.rainforestapi.com/request', params=params)
        res = response.json()
        
        if res.get("success"):
            product = res.get("product", {})
            
            # ج- استخراج التفاصيل بالعربي
            title = product.get("title", "اسم المنتج غير متوفر")
            
            # د- استخراج السعر (نفس المسار الموثوق لديكِ)
            price_info = product.get("buybox_winner", {}).get("price", {})
            price_value = price_info.get("value", "غير متوفر")
            
            # هـ- استخراج الصورة بأعلى جودة متوفرة
            images = product.get("images", [])
            if images:
                image_url = images[0].get("link") # الصورة الأساسية عالية الدقة
            else:
                image_url = product.get("main_image", {}).get("link")
            
            # و- تنسيق نص البوست
            caption = (
                f"👌 **خيار ذكي ومميز**\n\n"
                f"📦 **المنتج:**\n{title}\n\n"
                f"💸 **السعر الحالي:** {price_value} ريال\n\n"
                f"🌐 **رابط الطلب:**\n{short_url}\n\n"
                f"✨ لقطة لا تفوتكم!"
            )
            return caption, image_url
            
    except Exception as e:
        print(f"Error in fetching: {e}")
    return None, None

# --- 2. معالج الرسائل (يستقبل الروابط ويرد عليها) ---
@bot.message_handler(func=lambda message: True)
def handle_amazon_links(message):
    text_received = message.text
    if "amazon" in text_received or "amzn.to" in text_received:
        bot.reply_to(message, "⏳ جاري استخراج العرض باللغة العربية...")
        
        caption, photo_url = get_amazon_details_ar(text_received)
        
        if caption and photo_url:
            bot.send_photo(CHAT_ID, photo_url, caption=caption, parse_mode="Markdown")
            print("✅ تم الإرسال بنجاح!")
        else:
            bot.reply_to(message, "❌ نعتذر، لم نتمكن من سحب بيانات المنتج بالعربي. تأكد أن الرابط لمنتج حقيقي.")

# --- 3. تشغيل البوت (لضمان عدم الإغلاق في Render) ---
if __name__ == "__main__":
    print("🚀 البوت يعمل الآن وبانتظار روابط أمازون...")
    # infinity_polling تضمن استمرار البرنامج 24/7
    bot.infinity_polling()
