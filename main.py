import telebot
import requests
from bs4 import BeautifulSoup
import random
import re
from flask import Flask
from threading import Thread

# --- إعداد موقع ويب "وهمي" لإرضاء Render ---
app = Flask('')
@app.route('/')
def home():
    return "البوت شغال بنجاح!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- كود البوت الأساسي ---
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

# بنك الجمل السعودي (نسخة الـ 100+ جملة)
price_labels = ["بكم؟", "السعر:", "بكم هالزين؟", "قيمة اللقطة:", "سعره اللقطة:"]
intros = [
    "يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", 
    "ابشروا بالزين.. شوفوا وش لقيت 💎", "قنصة اليوم وصلت يالربع 🎯", "لقيت لكم شي يفتح النفس 😍",
    "يا مسا الزين.. شوفوا هالجمال 🌸", "لقطة اليوم للي يدور الفخامة ✨", "يا حي الله هالطلة.. شي فنان 🌟"
]
descs = [
    "شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", 
    "تقييمه يطمن وبصراحة ما يتفوت.", "فخامة وجودة وتصميم عصري فنان.", "الكل يمدحه وتجربته تبيض الوجه."
]

def get_product_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.content, 'html.parser')

        # سحب الاسم
        title_tag = soup.select_one('#productTitle') or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip().replace("Amazon.sa :", "").strip() if title_tag else "منتج مميز"
        product_info = " ".join(raw_title.split()[:13]) + ".."

        # سحب السعر (بدون هللات)
        price = "شيك بالرابط 🏷️"
        p_tag = soup.select_one('.a-price .a-offscreen') or soup.select_one('span.a-price-whole')
        if p_tag:
            clean_p = re.sub(r'[^\d]', '', p_tag.text.split('.')[0])
            if clean_p: price = f"{clean_p} ريال"

        # سحب الصورة
        img_url = None
        img_tag = soup.select_one('#landingImage')
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            img_url = re.findall(r'(https?://[^\s"]+)', img_tag['data-a-dynamic-image'])[-1]

        caption = f"{random.choice(intros)}\n\n📦 **المنتج:** {product_info}\n\n💰 **{random.choice(price_labels)}** {price}\n👌 {random.choice(descs)}\n\n🔗 **رابط الطلب:** {url}"
        return caption, img_url
    except: return None, None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if "http" in message.text:
        url = re.search(r'(https?://\S+)', message.text).group(0)
        caption, img_url = get_product_data(url)
        if caption:
            try:
                if img_url: bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown')
                else: bot.send_message(message.chat.id, caption, parse_mode='Markdown')
            except: bot.send_message(message.chat.id, caption, parse_mode='Markdown')

# --- تشغيل الموقع ثم البوت ---
if __name__ == "__main__":
    keep_alive() # تشغيل الموقع الوهمي في الخلفية
    print("البوت والموقع الوهمي شغالين..")
    bot.polling(none_stop=True)
