import telebot
import requests
from bs4 import BeautifulSoup
import random
import re

# التوكن حقك
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

def clean_title(full_title):
    # اختصار الاسم بأخذ أول 6 كلمات فقط لضمان عدم قطع الكلمات
    words = full_title.split()
    if len(words) > 6:
        return " ".join(words[:6]) + ".."
    return full_title

def get_product_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "ar-SA,en-US;q=0.9,ar;q=0.8",
        }
        
        res = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. استخراج الاسم واختصاره بذكاء (كلمات كاملة)
        title_tag = soup.find("span", {"id": "productTitle"}) or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip() if title_tag else "منتج مميز"
        # تنظيف الاسم من كلمة Amazon وغيرها
        raw_title = raw_title.replace("Amazon.sa :", "").replace("Amazon.sa:", "").strip()
        product_name = clean_title(raw_title)

        # 2. استخراج السعر
        price = "سعر لقطة!"
        # محاولة سحب السعر من الـ Offscreen أولاً (الأكثر دقة في أمازون)
        price_tag = soup.select_one(".a-price .a-offscreen")
        if price_tag:
            price = price_tag.get_text().strip()
        else:
            # محاولة بديلة لو كان السعر بنظام الخانات المنفصلة
            p_whole = soup.find("span", {"class": "a-price-whole"})
            if p_whole:
                price = p_whole.get_text().strip().replace(".", "") + " ريال"

        # 3. سحب الصورة (أعلى جودة)
        img_url = None
        img_tag = soup.find("img", {"id": "landingImage"})
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            img_data = img_tag.get('data-a-dynamic-image')
            img_url = list(eval(img_data).keys())[-1]
        elif img_tag:
            img_url = img_tag.get('src')

        # 4. تنسيق المنشور (5 سطور مرتبة)
        intros = ["يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨"]
        descs = ["جودة وفخامة وتستاهلكم.", "شيء من الآخر ويبيض الوجه.", "رهيب وتقييمه عالي جداً."]
        
        caption = (
            f"{random.choice(intros)}\n"
            f"📦 **المنتج:** {product_name}\n"
            f"💰 **السعر:** {price}\n"
            f"👌 {random.choice(descs)}\n"
            f"🔗 **الرابط:** {url}"
        )
        
        return caption, img_url
    except Exception as e:
        print(f"Error: {e}")
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
                if img_url:
                    try:
                        bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown')
                    except:
                        bot.send_message(message.chat.id, caption, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, caption, parse_mode='Markdown')
            else:
                bot.reply_to(message, "الرابط ما سحب بيانات، جربي رابط ثاني 💔")

print("البوت شغال.. وجاهز للفزعة!")
bot.polling()
