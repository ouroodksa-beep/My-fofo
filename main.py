import telebot
import cloudscraper
from bs4 import BeautifulSoup
import random
import re
import os
from flask import Flask
from threading import Thread

# --- خادم الويب لإبقاء البوت حياً ---
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

# إعداد السكرابر مع إجبار اللغة العربية في الـ Headers
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
HEADERS = {
    "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.amazon.sa/-/ar/",
}

# بنك الجمل السعودي
price_labels = ["بكم؟", "السعر الحين:", "بكم هالزين؟", "سعره اللقطة:", "قيمة القطعة:"]
intros = [
    "يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", 
    "ابشروا بالزين.. شوفوا وش لقيت 💎", "قنصة اليوم وصلت يالربع 🎯", "لقيت لكم شي يفتح النفس 😍"
]
descs = [
    "شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", 
    "تقييمه يطمن وبصراحة ما يتفوت.", "خامة ممتازة وسعرها يا بلاش والله."
]

def clean_product_title(title):
    # تنظيف العبارات المتكررة
    title = title.replace("Amazon.sa :", "").replace("Amazon.sa:", "").strip()
    
    # محاولة ترتيب الاسم بحيث لو فيه عربي يظهر بوضوح
    words = title.split()
    if len(words) > 12:
        return " ".join(words[:12]) + ".."
    return title

def get_product_data(url):
    try:
        # إرسال الطلب مع الهيدرز العربية
        res = scraper.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. سحب الاسم
        title_tag = soup.select_one('#productTitle') or soup.find("meta", property="og:title")
        product_info = "منتج مميز"
        if title_tag:
            product_info = clean_product_title(title_tag.get_text().strip())

        # 2. سحب السعر (بدون هللات وبدون نقاط)
        price = "شيك بالرابط 🏷️"
        selectors = [
            'span.a-price-whole', '.a-price .a-offscreen', 
            '#corePrice_feature_div .a-offscreen', '#corePriceDisplay_desktop_feature_div .a-offscreen',
            '.a-color-price'
        ]
        for sel in selectors:
            p_tag = soup.select_one(sel)
            if p_tag and p_tag.get_text().strip():
                p_text = p_tag.get_text().strip().split('.')[0]
                clean_p = re.sub(r'[^\d]', '', p_text)
                if clean_p:
                    price = f"{clean_p} ريال"
                    break

        # 3. سحب الصورة
        img_url = None
        img_tag = soup.select_one('#landingImage') or soup.select_one('#main-image')
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            links = re.findall(r'(https?://[^\s"]+)', img_tag['data-a-dynamic-image'])
            img_url = links[-1] if links else img_tag.get('src')
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
    keep_alive()
    bot.polling(none_stop=True)
