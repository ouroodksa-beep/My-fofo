import telebot
import requests
from bs4 import BeautifulSoup
import random  # مكتبة الاختيار العشوائي

# التوكن حقك
API_TOKEN = '8534031232:AAHwBJ0HZvOlbDmeevlbd2zM9FvSIfeskjk'
bot = telebot.TeleBot(API_TOKEN)

# قائمة الجمل الافتتاحية العشوائية
openings = [
    "🔥 يا هلا والله.. جبت لكم لقطة ما تتفوت!",
    "✨ شوفوا وش لقيت لكم اليوم.. شي فاخر!",
    "🎯 قنصة اليوم وصلت.. الزين ما يكمل إلا به!",
    "🚀 الحقوا على هاللقطة قبل تخلص!",
    "🌟 يا حي الله هالطلة.. شوفوا هالزين وش يقول:",
    "💎 لقطة ملكية وتستاهل قلوبكم!"
]

# قائمة أوصاف عشوائية (الجملة الواحدة)
descriptions = [
    "شي من الآخر، جودة وسعر ويبيض الوجه.",
    "منتج بطل ويستاهل يكون عندك في البيت.",
    "رهيب وفنان وتصميمه يفتح النفس بصراحة.",
    "الكل يمدحه وتقييمه يطمن، لا يفوتكم!",
    "قطعة فنية وسعرها لقطة، وش تنتظرون؟",
    "فخامة وجودة، وهالزين ما يتفوت أبداً."
]

# قائمة قفلات عشوائية (دعوة للطلب)
closings = [
    "لحقوا عليه قبل يطير وتندمون! 😍👇",
    "اطلبه الحين ووسع صدرك، الرابط هنا 👇",
    "الزين عندكم والشوق عندنا، تفضلوا 👇",
    "لا تقولون ما قلت لكم، العرض بطل! 👇",
    "هذا الرابط للي يبي الزين 👇"
]

def get_product_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(response.content, 'html.parser')

        # استخراج العنوان
        title_tag = soup.find('meta', property='og:title') or soup.find('title')
        title = title_tag['content'] if title_tag and title_tag.has_attr('content') else title_tag.text
        title = title.split('|')[0].split(':')[0].strip()

        # استخراج الصورة
        img_tag = soup.find('meta', property='og:image')
        img_url = img_tag['content'] if img_tag else None

        # اختيار جمل عشوائية
        intro = random.choice(openings)
        desc = random.choice(descriptions)
        outro = random.choice(closings)

        # صياغة النص النهائية
        caption = (
            f"{intro}\n\n"
            f"📦 **المنتج:** {title}\n"
            f"✨ **وش وضع المنتج؟** {desc}\n\n"
            f"🔗 **رابط الطلب:** {url}\n\n"
            f"{outro}"
        )
        
        return caption, img_url
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if "http" in message.text:
        # استخراج الرابط
        url = [word for word in message.text.split() if word.startswith('http')][0]
        
        bot.reply_to(message, "لحظة خليني أشيك لك على هالزين... 🧐")
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
            bot.send_message(message.chat.id, "يا غالي الرابط عيا يفتح معي، تأكد منه لاهنت! 💔")
    else:
        bot.reply_to(message, "أرسلي لي رابط المنتج وابشري بالخير 🫡")

print("البوت شغال.. وجاهز للفزعة!")
bot.polling()

