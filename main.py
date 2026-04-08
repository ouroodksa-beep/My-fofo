import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
]

OPENING_LINES = [
    "🔥 عرض مميز لا يفوت!",
    "💎 أفضل اختيار اليوم!",
    "✨ فرصة قوية!",
    "🏆 منتج بسعر رهيب!",
]

TRANSLATIONS = {
    "cabinet": "خزانة", "shelf": "رف", "organizer": "منظم",
    "kitchen": "مطبخ", "metal": "معدني", "set": "طقم",
    "white": "أبيض", "black": "أسود"
}

# ===== أدوات =====
def headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def expand(url):
    try:
        if "amzn.to" in url:
            return requests.get(url, headers=headers(), allow_redirects=True).url
    except:
        pass
    return url

def asin(url):
    m = re.search(r"/([A-Z0-9]{10})", url)
    return m.group(1) if m else None

# ===== استخراج نظيف =====
def clean_title(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    for l in lines:
        # تجاهل الروابط والهبل
        if "http" in l.lower():
            continue
        if "amazon" in l.lower():
            continue
        if len(l) < 5:
            continue
        if len(l) > 200:
            continue
        
        return l
    
    return "منتج مميز"

def get_product(asin_code):
    try:
        url = f"https://r.jina.ai/http://amazon.sa/dp/{asin_code}"
        r = requests.get(url, headers=headers(), timeout=15)
        
        if r.status_code == 200:
            title = clean_title(r.text)
            
            prices = re.findall(r'(\d+)\s*ريال', r.text)
            price = prices[0] if prices else "غير متوفر"
            
            return {
                "title": title,
                "price": price
            }
    except:
        pass
    
    return None

# ===== ترجمة بسيطة =====
def translate(title):
    words = title.split()
    result = []
    for w in words:
        result.append(TRANSLATIONS.get(w.lower(), w))
    return " ".join(result)

def format_price(p):
    if p == "غير متوفر":
        return "💰 السعر: غير متوفر"
    return f"💰 السعر: {p} ريال"

# ===== إنشاء البوست =====
def make_post(prod, url):
    title = translate(prod["title"])
    opening = random.choice(OPENING_LINES)
    
    return f"{opening}\n\n🛒 {title}\n\n{format_price(prod['price'])}\n\n🔗 {url}"

# ===== البوت =====
@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r"https?://\S+", msg.text)
    
    if not urls:
        bot.reply_to(msg, "❌ ابعت رابط أمازون")
        return
    
    for u in urls:
        wait = bot.reply_to(msg, "⏳ جاري التحميل...")
        
        full = expand(u)
        code = asin(full)
        
        if not code:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            continue
        
        prod = get_product(code)
        
        if not prod:
            bot.edit_message_text("❌ فشل في جلب المنتج", msg.chat.id, wait.message_id)
            continue
        
        post = make_post(prod, u)
        
        bot.send_message(msg.chat.id, post)
        bot.delete_message(msg.chat.id, wait.message_id)

print("🔥 شغال")
bot.infinity_polling()
