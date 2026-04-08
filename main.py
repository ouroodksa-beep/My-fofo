import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ================= User Agents =================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9"
    }

# ================= تنظيف العنوان =================
def clean_title(text):
    if not text:
        return ""

    text = re.sub(r'[^\w\s\-]', ' ', text)

    words = text.split()
    clean_words = []

    for w in words:
        if len(w) > 2 and not re.match(r'^[A-Z]{3,}$', w):
            clean_words.append(w)

    result = " ".join(clean_words)

    if len(result) < 5:
        return text[:80]

    return result


# ================= ترجمة بسيطة =================
TRANSLATIONS = {
    "shampoo": "شامبو",
    "cream": "كريم",
    "phone": "جوال",
    "watch": "ساعة",
    "headphones": "سماعات",
    "shoes": "حذاء",
    "bag": "شنطة",
    "dress": "فستان",
    "laptop": "لابتوب",
    "hair": "شعر",
    "face": "وجه",
    "skin": "بشرة"
}

def translate(text):
    words = text.split()
    result = []

    for w in words:
        lw = w.lower()
        if lw in TRANSLATIONS:
            result.append(TRANSLATIONS[lw])
        else:
            result.append(w)

    return " ".join(result)


# ================= استخراج ASIN =================
def extract_asin(url):
    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})"
    ]

    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    return None


# ================= جلب المنتج =================
def get_product(url):
    headers = get_headers()

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # ===== العنوان =====
        title_tag = soup.select_one("#productTitle")

        if not title_tag:
            meta = soup.select_one("meta[property='og:title']")
            if meta:
                title = meta.get("content")
            else:
                title = None
        else:
            title = title_tag.text.strip()

        title = clean_title(title)

        if not title or len(title) < 10:
            return None

        # ===== السعر =====
        price_tag = soup.select_one(".a-price .a-offscreen")
        price = price_tag.text.strip() if price_tag else "غير متوفر"

        # ===== الصورة =====
        img = soup.select_one("#landingImage")
        image = img.get("src") if img else None

        return {
            "title": title,
            "price": price,
            "image": image
        }

    except Exception as e:
        print(e)
        return None


# ================= توليد البوست =================
def generate_post(title, price, url):
    title_ar = translate(title)

    post = f"""🔥 منتج يستحق التجربة

🛒 {title_ar}

💰 السعر: {price}

🔗 {url}
"""

    return post


# ================= البوت =================
@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r"https?://\S+", msg.text)

    if not urls:
        bot.reply_to(msg, "❌ ابعت رابط أمازون")
        return

    for url in urls:
        wait = bot.reply_to(msg, "⏳ جاري التحميل...")

        product = get_product(url)

        if not product:
            bot.edit_message_text(
                "❌ فشل في جلب المنتج\nجرب رابط تاني",
                msg.chat.id,
                wait.message_id
            )
            continue

        post = generate_post(product["title"], product["price"], url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)

        except Exception as e:
            print(e)
            bot.send_message(msg.chat.id, post)


print("🔥 البوت شغال")
bot.infinity_polling()
