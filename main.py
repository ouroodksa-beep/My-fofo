import telebot
import requests
from bs4 import BeautifulSoup
import random
import re

# التوكن حقك
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

# --- بنك الجمل السعودية ---
intros = [
    "يا هلا والله.. شوفوا هاللقطة! 😍", "جبت لكم زين القنصات 🔥", "لقطة اليوم لا تفوتكم ✨", "ابشروا بالزين.. شوفوا وش لقيت 💎",
    "يا حي الله هالطلة.. جبنا لكم شي فنان 🌟", "قنصة اليوم وصلت يالربع 🎯", "لقيت لكم شي يفتح النفس بصراحة 😍",
    "تبون الصدق؟ هالقطعة ما تتفوت 🚀", "شوفوا وش طحت عليه.. لقطة ملكية 👑", "الزين وصل.. الحقوا عليه! 🔥",
    "يا مسا الزين.. شوفوا هالجمال 🌸", "لقطة اليوم للي يدور الفخامة ✨", "هذا اللي يقال عنه لقطة العمر 🎯",
    "يا بلاش على هالزين.. شوفوا وش لقيت! 💰", "تبون قطعة تبيض الوجه؟ هذي هي 💎", "قنصتها لكم من قلب أمازون 🔥",
    "لا تدورون غيره.. هذا هو المطلوب 🎯", "شوفوا هالزين وش يقول يا جماعة 😍", "لقطة خرافية وسعرها لقطة أكثر ✨",
    "يا هلا باللي يدورون الجودة.. شوفوا هذا 🌟"
] # تقدرين تزيدينهم لـ 100 بنفس النمط

descs = [
    "شيء فاخر ومن الآخر ويستاهلكم.", "الزين ما يكمل إلا به، جودة وسعر.", "رهيب وفنان وتصميمه يفتح النفس.", "تقييمه يطمن وبصراحة ما يتفوت.",
    "قطعة فنية وتبيض الوجه عند الضيوف.", "خامة ممتازة وسعرها يا بلاش والله.", "والله لو ماهو بطل ما جبته لكم.", "جودة عالية وسعره صدمة بصراحة.",
    "من أكثر القطع طلباً وتقييمه عالي.", "يستاهل كل ريال يدفع فيه يالربع.", "فخامة وجودة وتصميم عصري فنان.", "تراه يخلص بسرعة، اللي يبيه يلحق.",
    "شي بطل بطل.. لا تقولون ما قلت لكم.", "مناسب جداً للاستخدام اليومي وقوي.", "الكل يمدحه وتجربته تبيض الوجه.", "خيار ذكي للي يدور الزين وبس.",
    "تصميم يفتح النفس وسعر ولا في الأحلام.", "والله قطعة متعوب عليها يا جماعة.", "هذا اللي يخليك متميز في اختياراتك.", "جودة وسعر ومظهر.. وش تبي أكثر؟"
]

def get_product_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "ar-SA,en-US;q=0.9,ar;q=0.8",
        }
        res = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 1. الاسم (سطرين)
        title_tag = soup.find("span", {"id": "productTitle"}) or soup.find("meta", property="og:title")
        raw_title = title_tag.get_text().strip() if title_tag else "منتج فخم"
        raw_title = raw_title.replace("Amazon.sa :", "").replace("Amazon.sa:", "").strip()
        words = raw_title.split()
        product_info = " ".join(words[:14]) + ".." if len(words) > 14 else raw_title

        # 2. السعر (البحث المتقدم)
        price = "شيك بالرابط 🏷️"
        # محاولة البحث عن أي نص يحتوي على ريال أو SR أو أرقام السعر
        price_patterns = [
            soup.find("span", class_="a-price-whole"),
            soup.find("span", class_="a-offscreen"),
            soup.find("span", id="priceblock_ourprice"),
            soup.find("span", id="priceblock_dealprice")
        ]
        
        for p in price_patterns:
            if p and p.get_text().strip():
                price_val = p.get_text().strip().replace("\u200f", "").replace("\u200e", "")
                if any(char.isdigit() for char in price_val):
                    price = price_val if "ريال" in price_val else f"{price_val} ريال"
                    break

        # 3. الصورة
        img_url = None
        img_tag = soup.find("img", {"id": "landingImage"})
        if img_tag and img_tag.has_attr('data-a-dynamic-image'):
            img_url = list(eval(img_tag.get('data-a-dynamic-image')).keys())[-1]
        elif img_tag:
            img_url = img_tag.get('src')

        # 4. التنسيق النهائي (اللمسة السعودية)
        caption = (
            f"{random.choice(intros)}\n\n"
            f"📦 **المنتج:** {product_info}\n\n"
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
        url = re.search(r'(https?://\S+)', message.text).group(0)
        bot.send_chat_action(message.chat.id, 'upload_photo')
        caption, img_url = get_product_data(url)
        if caption:
            if img_url:
                try: bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode='Markdown')
                except: bot.send_message(message.chat.id, caption, parse_mode='Markdown')
            else: bot.send_message(message.chat.id, caption, parse_mode='Markdown')
        else:
            bot.reply_to(message, "الرابط عيّا يفتح، جربي غيره يا بعدي 💔")

print("البوت شغال..")
bot.polling()
