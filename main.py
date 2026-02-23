import requests
import telebot
import random
import sys

# --- البيانات ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA" 
CHAT_ID = "ftwu_bot"

try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
except Exception as e:
    print(f"خطأ في التوقن: {e}")
    sys.exit(1)

# دالة سحب البيانات بالعربي
def get_data(url):
    try:
        # فك الرابط
        long_url = requests.head(url, allow_redirects=True).url
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',
            'amazon_domain': 'amazon.sa'
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        if res.get("success"):
            p = res['product']
            title = p.get('title', 'منتج رهيب')
            price = p.get('buybox_winner', {}).get('price', {}).get('value', 'غير متوفر')
            img = p.get('images', [{}])[0].get('link') or p.get('main_image', {}).get('link')
            return title, price, img
    except: return None, None, None

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "amazon" in m.text or "amzn.to" in m.text:
        t, p, i = get_data(m.text)
        if t:
            bot.send_photo(CHAT_ID, i, caption=f"✨ **لقطة سعودية**\n\n📦 {t}\n\n💸 السعر: {p} ريال\n\n🔗 {m.text}", parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 البوت شغال..")
    bot.infinity_polling()
