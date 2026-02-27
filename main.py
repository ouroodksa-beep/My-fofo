import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🔧 دوال المساعدة
# ===================================

def expand_url(url):
    """يفك الروابط المختصرة"""
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ow.ly', 'short.link']):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
            }
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            return r.url
        return url
    except:
        return url


def is_saudi_amazon(url):
    return "amazon.sa" in url.lower()


def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'([A-Z0-9]{10})/?$',
        r'([A-Z0-9]{10})(?:[/?]|\b)'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.google.com/"
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            return None
    except:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # العنوان
    title_elem = soup.select_one("#productTitle")
    if not title_elem:
        return None
    title = title_elem.text.strip()

    # السعر الحالي
    price = None
    price_selectors = [
        ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
        ".a-price.a-text-price.apexPriceToPay .a-offscreen",
        ".a-price.aok-align-center .a-offscreen",
        ".a-price .a-offscreen",
        "[data-a-color='price'] .a-offscreen",
        ".a-price-whole"
    ]
    
    for selector in price_selectors:
        elem = soup.select_one(selector)
        if elem and elem.text:
            price = elem.text.strip()
            if any(c.isdigit() for c in price):
                break

    # السعر القديم
    old_price = None
    old_selectors = [
        ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
        ".a-price.a-text-price .a-offscreen",
        ".basisPrice .a-offscreen",
        ".priceBlockStrikePriceString"
    ]
    
    for selector in old_selectors:
        elem = soup.select_one(selector)
        if elem and elem.text:
            old_text = elem.text.strip()
            if old_text != price and any(c.isdigit() for c in old_text):
                old_price = old_text
                break

    # الصورة
    image = None
    img_elem = soup.select_one("#landingImage")
    if img_elem:
        image = img_elem.get("src") or img_elem.get("data-old-hires")

    # الخصم
    discount_percent = None
    try:
        if old_price and price:
            old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))
            new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))
            if old_num > new_num:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        pass

    if not price:
        return None

    return title, price, old_price, image, discount_percent


# ===================================
# ✨ التوليد النهائي (بسيط ونظيف)
# ===================================

def generate_post(title, price, old_price, discount_percent, original_url):
    # اسم المنتج
    display_title = title[:100] + "..." if len(title) > 100 else title
    
    # بناء المنشور بدون جمل تسويقية بعد السعر
    lines = []
    lines.append(f"🛒 {display_title}")
    lines.append("")
    
    # السعر القديم في سطر لوحده
    if old_price and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {old_price}")
        lines.append(f"✅ الحين: {price} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {price}")
    
    lines.append("")
    lines.append(f"🔗 {original_url}")
    
    return "\n".join(lines)


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط منتج")
        return

    for original_url in urls:
        expanded = expand_url(original_url)

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط لازم يكون من amazon.sa")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج رقم المنتج")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)
            continue

        title, price, old_price, image, discount_percent = product
        post = generate_post(title, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)
        except:
            bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()
