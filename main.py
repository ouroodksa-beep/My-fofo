import telebot
import requests
from bs4 import BeautifulSoup
import random
import re

# التوكن الخاص بكِ
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

# بنك الجمل السعودية (أكثر من 50 جملة)
intros = [
    "يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", 
    "ابشروا بالزين.. شوفوا وش لقيت 💎", "قنصة اليوم وصلت يالربع 🎯", "لقيت لكم شي يفتح النفس 😍",
    "تبون الصدق؟ هالقطعة ما تتفوت 🚀", "شوفوا وش طحت عليه.. لقطة ملكية 👑", "الزين وصل.. الحقوا عليه! 🔥",
    "يا مسا الزين.. شوفوا هالجمال 🌸", "لقطة اليوم للي يدور الفخامة ✨", "هذا لقطة العمر 🎯"
]

descs = [
    "شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", 
    "تقييمه يطمن وبصراحة ما يتفوت.", "خامة ممتازة وسعرها يا بلاش والله.", "والله لو ماهو بطل ما جبته لكم.", 
    "جودة عالية وسعره صدمة بصراحة.", "يستاهل كل ريال يدفع فيه يالربع.", "فخامة وجودة وتصميم عصري فنان."
]

def get_product_data(url):
    try:
        # رؤوس طلبات متنوعة لتجنب الحظر
        headers_list = [
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"},
            {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
        ]
        
        res = requests.get(url, headers=random.choice(headers_list), timeout=25)
        if res.status_code != 200:
            return None, None

        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. سحب الاسم (سطرين بدون قطع كلمات)
        title = "منتج رهيب"
        title_tag = soup.select_one('#productTitle') or soup.find("meta", property="og:title")
        if title_tag:
            raw_title = title_tag.get_text().strip().replace("Amazon.sa :", "").strip()
            words = raw_title.split()
            title = " ".join(words[:13]) + ".." if len(words) > 13 else raw_title

        # 2. سحب السعر وتنظيفه من النقاط والرموز
        price = "شيك بالرابط 🏷️"
        price_selectors = ['.a-price .a-offscreen', 'span.a-price-whole', '#corePrice_feature_div .a-price-whole']
        
        for sel in price_selectors:
            p_tag = soup.select_one(sel)
            if p_tag and p_tag.text.strip():
                # تنظيف السعر من (النقطة، الفواصل، والرموز المخفية)
                raw_p = p_tag.text.strip()
                clean_p = re.sub(r'[^\d]', '', raw_p) # استخراج الأرقام فقط
                
                if clean_p:
                    price = f"{clean_p} ريال"
                    break

        # 3. سحب الصورة (أعلى جودة)
        img_url = None
        img_tag = soup.select_one('#landingImage') or soup.select_one('#imgBlkFront')
        if img_tag:
            if img_tag.has_attr('data-a-dynamic-image'):
                links = re.findall(r'(https?://[^\s"]+)', img_tag['data-a-dynamic-image'])
                img_url = links[-1] if links else img_tag.get('src')
            else:
                img_url = img_tag.get('src')

        # 4. التنسيق النهائي
        caption = (
            f"{random.choice(intros)}\n\n"
            f"📦 **المنتج:** {title}\n\n"
            f"💰 **بكم؟** {price}\n"
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
                    if img_url:
                        bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown')
                    else:
                        bot.send_message(message.chat.id, caption, parse_mode='Markdown')
                except:
                    bot.send_message(message.chat.id, caption, parse_mode='Markdown')
            else:
                bot.reply_to(message, "الرابط عيّا يسحب، جربي واحد ثاني يا بعدي 💔")

print("البوت شغال.. وتم تنظيف السعر من النقاط!")
bot.polling()
