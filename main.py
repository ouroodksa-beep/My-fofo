import os

import random

import requests

from bs4 import BeautifulSoup

import telebot



# =================================
# TOKEN
# =================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN missing")



bot = telebot.TeleBot(TOKEN)



# =================================
# أنماط التسويق
# =================================

STYLES = [

    "عرض لفترة محدودة",

    "جودة عالية بسعر رائع",

    "الأكثر مبيعاً حالياً",

    "اختيار مثالي",

    "فرصة لا تعوض",

    "راحة وأناقة",

    "تصميم عصري",

    "مميز وفريد"

]



# =================================
# قراءة الرابط (سريعة)
# =================================

def get_product_info(url):

    try:

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=8)



        soup = BeautifulSoup(response.text, "html.parser")



        title = soup.title.string.strip() if soup.title else "منتج مميز"



        meta = soup.find("meta", {"name": "description"})

        desc = meta["content"] if meta else "أفضل منتج بجودة عالية"



        return title, desc



    except Exception as e:
        print("ERROR:", e)
        return "منتج رائع", "جودة عالية وسعر ممتاز"



# =================================
# توليد جمل بدون تعليق
# =================================

def generate_sentences(title, desc, count=50):

    results = []

    used = set()



    for _ in range(count * 3):

        style = random.choice(STYLES)

        emoji = random.choice(["🔥", "✨", "🚀", "⭐", "💎"])



        text = f"{emoji} {title}\n{desc}\n✔ {style}"



        if text not in used:

            used.add(text)

            results.append(text)



        if len(results) >= count:
            break



    return results



# =================================
# START
# =================================

@bot.message_handler(commands=["start"])

def start(message):

    bot.reply_to(message, "👋 أرسل رابط المنتج وسأجهز لك منشورات جاهزة.")



# =================================
# الروابط
# =================================

@bot.message_handler(func=lambda m: m.text and "http" in m.text)

def handle_link(message):

    url = message.text.strip()



    bot.reply_to(message, "⏳ جاري تجهيز المنشورات...")



    title, desc = get_product_info(url)



    texts = generate_sentences(title, desc, 50)



    final = "\n\n-----------------\n\n".join(texts)



    bot.send_message(message.chat.id, final)



# =================================
# fallback
# =================================

@bot.message_handler(func=lambda m: True)

def fallback(message):

    bot.reply_to(message, "❌ أرسل رابط صحيح")



# =================================
# تشغيل
# =================================

print("BOT RUNNING")

bot.infinity_polling()
