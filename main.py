import telebot
import cloudscraper
from bs4 import BeautifulSoup
import random
import re
import os
from flask import Flask
from threading import Thread

# --- إعداد خادم الويب لإبقاء البوت حياً على Render ---
app = Flask('')
@app.route('/')
def home(): return "البوت شغال بنجاح!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)
# استخدام scraper متطور لتجاوز حجب الأسعار
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

# بنك الكلمات السعودي (أكثر من 100 خلطة)
price_labels = ["بكم؟", "السعر:", "بكم هالزين؟", "قيمة اللقطة:", "سعره اللقطة:", "بكم نخلص؟"]
intros = [
    "يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", 
    "ابشروا بالزين.. شوفوا وش لقيت 💎", "قنصة اليوم وصلت يالربع 🎯", "لقيت لكم شي يفتح النفس 😍",
    "يا مسا الزين.. شوفوا هالجمال 🌸", "لقطة اليوم للي يدور الفخامة ✨"
]
descs = [
    "شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", 
    "تقييمه يطمن وبصراحة ما يتفوت.", "خامة ممتازة وسعرها يا بلاش والله."
]

def get_product_data(url):
    try:
        # جلب الصفحة باستخدام المتصفح الوهمي
        res = scraper.get(url, timeout=30)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. سحب الاسم (سطرين)
        title_tag = soup.select_one('#productTitle') or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip().replace("Amazon.sa :", "").strip() if title_tag else "منتج فخم"
        words = raw_title.split()
        product_info = " ".join(words[:13]) + ".." if len(words) > 13 else raw_title

        # 2. سحب السعر (محاولات متعددة ومكثفة)
        price = "شيك بالرابط 🏷️"
        # نبحث عن السعر في كل مكان ممكن أمازون يخفيه فيه
        p_tag = (soup.select_one('.a-price .a-offscreen') or 
                 soup.select_one('span.a-price-whole') or 
                 soup.select_one('.a-color-price') or
                 soup.select_one('#corePrice_feature_div .a-offscreen'))
        
        if p_tag:
            price_text = p_tag.get_text().strip()
            # حذف الهللات: نأخذ فقط ما قبل النقطة
            price_text = price_text.split('.')[0]
            # حذف أي رموز غير الأرقام (الفواصل، النقاط، العملات)
            clean_p = re.sub(r'[^\d]', '', price_text)
            if clean_p:
                price = f"{clean_p} ريال"

        # 3. سحب الصورة (أعلى جودة)
        img_url = None
        img_tag = soup.find("img", {"id": "landingImage"})
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            img_url = re.findall(r'(https?://[^\s"]+)', img_tag['data-a-dynamic-image'])[-1]
        elif img_tag:
            img_url = img_tag.get('src')

        # 4. التنسيق النهائي
        caption = (
            f"{random.choice(intros)}\n\n"
            f"📦 **المنتج:** {product_info}\n\n"
            f"💰 **{random.choice(price_labels)}** {price}\n"
            f"👌 {random.choice(descs)}\n\n"
            f"🔗 **رابط الطلب:** {url}"
        )
        return caption, img_url
    except:
        return None, None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if "http" in message.text:
        url_match = re.search(r'(https?://\S+)', message.text)
        if url_match:
            url = url_match.group(0)
            bot.send_chat_action(message.chat.id, 'upload_photo')
            caption, img_url = get_product_data(url)
            if caption:
                try:
                    if img_url: bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown')
                    else: bot.send_message(message.chat.id, caption, parse_mode='Markdown')
                except:
                    bot.send_message(message.chat.id, caption, parse_mode='Markdown')

if __name__ == "__main__":
    keep_alive() # لتشغيل الموقع الوهمي على Render
    bot.polling(none_stop=True)
