import os

import random

import requests

from bs4 import BeautifulSoup

import telebot



# =========================================
# إعدادات البوت
# =========================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN is missing. Add it in Render Environment Variables.")



bot = telebot.TeleBot(TOKEN)



# =========================================
# أنماط الكتابة المختلفة
# =========================================

STYLES = [

    "أسلوب تسويقي احترافي",

    "أسلوب عاطفي مؤثر",

    "أسلوب إقناعي مباشر",

    "أسلوب قصصي جذاب",

    "أسلوب فاخر راقي",

    "أسلوب شبابي عصري",

    "أسلوب نسائي أنيق",

    "أسلوب قوي وحماسي",

    "أسلوب مختصر وسريع"

]



generated_texts = set()



# =========================================
# دالة قراءة بيانات المنتج من الرابط
# =========================================

def get_product_info(url):

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(response.text, "html.parser")



        title = soup.title.string.strip() if soup.title else "منتج مميز"



        description = ""

        meta_desc = soup.find("meta", {"name": "description"})

        if meta_desc:
            description = meta_desc.get("content", "").strip()



        if not description:
            description = "أفضل منتج بجودة عالية وسعر منافس ومناسب للجميع"



        return title, description



    except Exception:
        return "منتج رائع", "منتج عالي الجودة مناسب لجميع الاستخدامات"



# =========================================
# توليد جمل تسويقية بدون تكرار
# =========================================

def generate_marketing_sentences(title, description, count=200):

    sentences = []



    while len(sentences) < count:

        style = random.choice(STYLES)

        power_word = random.choice(["🔥", "✨", "🚀", "💎", "🎯", "⭐"])



        sentence = f"{power_word} {title}\n{description}\n✔ {style}\n"



        if sentence not in generated_texts:

            generated_texts.add(sentence)

            sentences.append(sentence)



    return sentences



# =========================================
# أمر البدء
# =========================================

@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(

        message,

        "👋 أهلاً بك في بوت كتابة الإعلانات الذكي\n\n"

        "أرسل رابط المنتج وسأولد لك أكثر من 200 جملة تسويقية مختلفة 💰🔥"

    )



# =========================================
# استقبال الروابط
# =========================================

@bot.message_handler(func=lambda message: "http" in message.text)

def handle_link(message):

    url = message.text.strip()



    bot.reply_to(message, "⏳ جاري قراءة الرابط...")



    title, description = get_product_info(url)



    bot.reply_to(message, "✍ جاري توليد الجمل التسويقية...")



    texts = generate_marketing_sentences(title, description, 200)



    final_text = "\n\n------------------------\n\n".join(texts)



    if len(final_text) > 4000:

        parts = [final_text[i:i+3500] for i in range(0, len(final_text), 3500)]

        for part in parts:
            bot.send_message(message.chat.id, part)

    else:
        bot.send_message(message.chat.id, final_text)



# =========================================
# استقبال أي رسالة أخرى
# =========================================

@bot.message_handler(func=lambda message: True)

def fallback(message):

    bot.reply_to(message, "❌ أرسل رابط منتج صحيح يبدأ بـ http")



# =========================================
# تشغيل البوت
# =========================================

print("✅ Bot is running...")

bot.infinity_polling()
