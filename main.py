import telebot
import re
import random
from playwright.sync_api import sync_playwright

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🔥 تحليل نوع المنتج
# ===================================

TECH_KEYWORDS = ["iphone", "samsung", "laptop", "tablet", "headphone", "airpods", "monitor", "camera"]
FASHION_KEYWORDS = ["shirt", "dress", "shoes", "nike", "adidas", "bag", "watch"]
PERFUME_KEYWORDS = ["perfume", "fragrance", "parfum", "oud", "attar"]

def detect_product_style(title):
    t = title.lower()

    if any(k in t for k in TECH_KEYWORDS):
        return "tech"
    elif any(k in t for k in FASHION_KEYWORDS):
        return "youth"
    elif any(k in t for k in PERFUME_KEYWORDS):
        return "luxury"
    else:
        return "general"


# ===================================
# 🎯 التسويق
# ===================================

OPENINGS = {
    "tech": ["⚡️ عرض تقني قوي", "🔥 سعر ممتاز على جهاز مطلوب", "🚀 فرصة لمحبي التقنية"],
    "youth": ["🔥 ستايل وسعر بنفس الوقت", "⚡️ خيار شبابي ملفت", "💥 عرض مناسب للموضة"],
    "luxury": ["💎 عرض فاخر بسعر ذكي", "✨ خيار راقي حالياً", "🔥 فخامة بسعر أقل"],
    "general": ["🔥 تخفيض يستحق الانتباه", "⚡️ سعر خارج التوقع", "💥 فرصة مناسبة"]
}

ENDINGS = {
    "tech": ["قرار ممتاز لعشاق التقنية", "ممكن ما يتكرر"],
    "youth": ["اختيار مناسب حالياً", "ستايل بسعر أقل"],
    "luxury": ["الفخامة ما تنتظر", "فرصة للتميز"],
    "general": ["خيار ذكي حالياً", "وقته مناسب"]
}


# ===================================
# 💰 السعر
# ===================================

def format_price(price):
    try:
        num = re.findall(r'[\d,]+', price)
        if num:
            main = int(float(num[0].replace(",", "")))
            return f"{main} ريال 🔥"
    except:
        pass
    return price


# ===================================
# 🏷 العنوان
# ===================================

def smart_title(title):
    words = title.split()
    brand = words[0] if words else ""
    short = " ".join(words[:10])
    return f"{brand} | {short}"


# ===================================
# 🔗 ASIN
# ===================================

def extract_asin(url):
    m = re.search(r'([A-Z0-9]{10})', url)
    return m.group(1) if m else None


# ===================================
# 🧠 Scraping قوي عبر المتصفح
# ===================================

def get_product_browser(url):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="ar-SA",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)

            # العنوان
            title = page.locator("#productTitle").inner_text().strip()

            # السعر
            price = None
            price_selectors = [
                ".a-price-to-pay",
                ".a-price .a-offscreen"
            ]

            for s in price_selectors:
                if page.locator(s).count() > 0:
                    price = page.locator(s).first.inner_text()
                    break

            # السعر القديم
            old_price = None
            if page.locator(".a-text-price").count() > 0:
                old_price = page.locator(".a-text-price").first.inner_text()

            # الصورة
            image = None
            if page.locator("#landingImage").count() > 0:
                image = page.locator("#landingImage").get_attribute("src")

            browser.close()

            if not title or not price:
                return None

            # الخصم
            discount = None
            try:
                if old_price:
                    old = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
                    new = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
                    if old > new:
                        discount = int(((old - new) / old) * 100)
            except:
                pass

            return title, price, old_price, image, discount

        except:
            browser.close()
            return None


# ===================================
# ✨ التوليد
# ===================================

def generate_post(title, price, old_price, discount, url):
    style = detect_product_style(title)

    opening = random.choice(OPENINGS[style])
    ending = random.choice(ENDINGS[style])

    title = smart_title(title)
    price = format_price(price)

    if discount and discount > 5:
        price += f" (وفر {discount}%)"

    return f"""{opening}

🛒 {title}

💰 {price}

👉 {ending}

🔗 {url}"""


# ===================================
# 🤖 البوت
# ===================================

@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج")
        return

    for url in urls:
        wait = bot.reply_to(msg, "جاري التحليل...")

        product = get_product_browser(url)

        if not product:
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)
            continue

        title, price, old_price, image, discount = product
        post = generate_post(title, price, old_price, discount, url)

        if image:
            bot.send_photo(msg.chat.id, image, caption=post)
        else:
            bot.send_message(msg.chat.id, post)

        bot.delete_message(msg.chat.id, wait.message_id)


print("Bot running...")
bot.infinity_polling()


