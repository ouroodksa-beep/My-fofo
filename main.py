import telebot
import requests
from bs4 import BeautifulSoup
import random
import re

# التوكن حقك
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

def get_smart_text(full_text, max_words=12):
    # يختصر الاسم لسطرين تقريباً بدون ما يقطع الكلمة
    words = full_text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + ".."
    return full_text

def get_product_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "ar-SA,en-US;q=0.9,ar;q=0.8",
        }
        
        res = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. اسم المنتج (ذكاء سطرين)
        title_tag = soup.find("span", {"id": "productTitle"}) or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip() if title_tag else "منتج فخم"
        raw_title = raw_title.replace("Amazon.sa :", "").replace("Amazon.sa:", "").strip()
        product_info = get_smart_text(raw_title, max_words=13)

        # 2. السعر (محاولات مكثفة عشان ما يطلع فاضي)
        price = "سعره لقطة (شيك بالرابط) 🏷️"
        # نبحث في الأماكن اللي يتخبا فيها السعر في أمازون السعودية
        selectors = [
            "span.a-price-whole", 
            ".a-price .a-offscreen", 
            "#corePrice_feature_div .a-price-whole",
            ".a-color-price"
        ]
        
        for selector in selectors:
            tag = soup.select_one(selector)
            if tag and tag.get_text().strip():
                p_text = tag.get_text().strip().replace(".", "")
                # تنظيف الرقم وتجهيزه بكلمة ريال
                if any(char.isdigit() for char in p_text):
                    price = f"{p_text} ريال" if "ريال" not in p_text else p_text
                    break

        # 3. الصورة (أعلى جودة)
        img_url = None
        img_tag = soup.find("img", {"id": "landingImage"})
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            img_data = img_tag.get('data-a-dynamic-image')
            img_url = list(eval(img_data).keys())[-1]
        elif img_tag:
            img_url = img_tag.get('src')

        # 4. سوالف سعودية (افتتاحية ووصف)
        intros = ["يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", "ابشروا بالزين.. شوفوا وش لقيت 💎"]
        descs = ["شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", "تقييمه يطمن وبصراحة ما يتفوت."]
        
        caption = (
            f"{random.choice(intros)}\n\n"
            f"📦 **المنتج:** {product_info}\n"
            f"💰 **بكم؟** {price}\n"
            f"👌 {random.choice(descs)}\n\n"
            f"🔗 **اطلبه من هنا:** {url}"
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
                bot.reply_to(message, "الرابط عيّا يفتح معي، جربي غيره يا بعدي 💔")
    else:
        bot.reply_to(message, "أرسلي الرابط وابشري بالفزعة 🫡")

print("البوت شغال.. وبالهوية السعودية!")
bot.polling()
