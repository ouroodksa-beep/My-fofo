import telebot
import cloudscraper
from bs4 import BeautifulSoup
import random
import re
import os
from flask import Flask
from threading import Thread

# --- إعداد خادم الويب (Render) ---
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
# سكرابر بمحاكاة متصفح حقيقي جداً
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

# بنك الكلمات السعودي (أكثر من 100 خيار)
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
        res = scraper.get(url, timeout=30)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. سحب الاسم
        title_tag = soup.select_one('#productTitle') or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip().replace("Amazon.sa :", "").strip() if title_tag else "منتج فخم"
        words = raw_title.split()
        product_info = " ".join(words[:13]) + ".." if len(words) > 13 else raw_title

        # 2. سحب السعر (مود الصياد الشامل)
        price = "شيك بالرابط 🏷️"
        
        # قائمة بكل المعرفات الممكنة للسعر في أمازون
        selectors = [
            'span.a-price-whole',             # السعر الأساسي
            '.a-price .a-offscreen',          # السعر المخفي (دقيق جداً)
            '#corePrice_feature_div .a-offscreen', 
            '#corePriceDisplay_desktop_feature_div .a-offscreen',
            '#corePrice_desktop .a-offscreen',
            '.a-color-price',                 # سعر العروض
            '#priceblock_ourprice',
            '#priceblock_dealprice'
        ]
        
        for sel in selectors:
            p_tag = soup.select_one(sel)
            if p_tag and p_tag.get_text().strip():
                p_text = p_tag.get_text().strip()
                # إزالة الهللات: القص عند أول نقطة تظهر
                p_text = p_text.split('.')[0]
                # تنظيف الرقم من أي رمز غير الأرقام
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
