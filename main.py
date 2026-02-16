import telebot
import requests
from bs4 import BeautifulSoup
import random
import re
import os
from flask import Flask
from threading import Thread

# --- إعداد خادم ويب وهمي لمنصة Render ---
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

def run():
    # Render يطلب العمل على منفذ معين (غالباً 10000 أو 8080)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت الأساسية ---
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

# بنك الجمل السعودي الضخم
price_labels = ["بكم؟", "السعر:", "بكم هالزين؟", "قيمة اللقطة:", "سعره اللقطة:", "بكم نخلص؟", "قيمة القطعة:"]
intros = [
    "يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", 
    "ابشروا بالزين.. شوفوا وش لقيت 💎", "قنصة اليوم وصلت يالربع 🎯", "لقيت لكم شي يفتح النفس 😍",
    "يا مسا الزين.. شوفوا هالجمال 🌸", "لقطة اليوم للي يدور الفخامة ✨", "يا حي الله هالطلة.. شي فنان 🌟"
]
descs = [
    "شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", 
    "تقييمه يطمن وبصراحة ما يتفوت.", "خامة ممتازة وسعرها يا بلاش والله.", "والله لو ماهو بطل ما جبته لكم."
]

def get_product_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(res.content, 'html.parser')

        # سحب الاسم (سطرين)
        title_tag = soup.select_one('#productTitle') or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip().replace("Amazon.sa :", "").strip() if title_tag else "منتج فخم"
        words = raw_title.split()
        product_info = " ".join(words[:13]) + ".." if len(words) > 13 else raw_title

        # سحب السعر (تنظيف الهللات والنقاط)
        price = "شيك بالرابط 🏷️"
        price_selectors = ['.a-price .a-offscreen', 'span.a-price-whole', '#corePrice_feature_div .a-price-whole']
        for sel in price_selectors:
            p_tag = soup.select_one(sel)
            if p_tag and p_tag.text.strip():
                # إزالة الهللات والرموز
                raw_p = p_tag.text.strip().split('.')[0]
                clean_p = re.sub(r'[^\d]', '', raw_p)
                if clean_p:
                    price = f"{clean_p} ريال"
                    break

        # سحب الصورة (أعلى جودة)
        img_url = None
        img_tag = soup.select_one('#landingImage')
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            links = re.findall(r'(https?://[^\s"]+)', img_tag['data-a-dynamic-image'])
            img_url = links[-1] if links else img_tag.get('src')
        elif img_tag:
            img_url = img_tag.get('src')

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

# --- التشغيل الرئيسي ---
if __name__ == "__main__":
    keep_alive()  # البدء بتشغيل خادم الويب الوهمي
    print("البوت والموقع الوهمي في حالة تشغيل..")
    bot.polling(none_stop=True)
