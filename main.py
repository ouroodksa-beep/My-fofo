import telebot
import requests
from bs4 import BeautifulSoup
import random
import re

# التوكن حقك
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

def get_product_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Accept-Language": "ar-SA,en-US;q=0.9,en;q=0.8"
        }
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. استخراج الاسم واختصاره جداً
        raw_title = soup.find("span", {"id": "productTitle"})
        title = raw_title.get_text().strip()[:45] + ".." if raw_title else "منتج فخم"

        # 2. استخراج السعر بالريال
        p_whole = soup.find("span", {"class": "a-price-whole"})
        p_frac = soup.find("span", {"class": "a-price-fraction"})
        price = f"{p_whole.get_text().strip()}{p_frac.get_text().strip() if p_frac else ''} ريال" if p_whole else "سعر بطل!"

        # 3. سحب الصورة بأعلى جودة (تنظيف رابط الصورة)
        img_tag = soup.find("img", {"id": "landingImage"}) or soup.find("img", {"id": "imgBlkFront"})
        img_url = None
        if img_tag:
            # أمازون يضع روابط الصور بجودات مختلفة، هنا ناخذ الرابط الأصلي
            img_data = img_tag.get('data-a-dynamic-image')
            if img_data:
                img_url = list(eval(img_data).keys())[-1] # ياخذ أكبر مقاس
            else:
                img_url = img_tag.get('src')

        # 4. قوالب المنشور (5 سطور قصيرة)
        intros = ["يا هلا.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨"]
        descs = ["جودة وفخامة وتستاهلكم.", "شيء من الآخر ويبيض الوجه.", "رهيب وتقييمه عالي جداً."]
        
        caption = (
            f"{random.choice(intros)}\n"
            f"📦 **المنتج:** {title}\n"
            f"💰 **السعر:** {price}\n"
            f"👌 {random.choice(descs)}\n"
            f"🔗 **الرابط:** {url}"
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
                if img_url:
                    try:
                        bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown')
                    except:
                        bot.send_message(message.chat.id, caption, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, caption, parse_mode='Markdown')
            else:
                bot.reply_to(message, "الرابط ما سحب بيانات، جربي واحد ثاني 💔")

print("البوت شغال على ريندر..")
bot.polling()
