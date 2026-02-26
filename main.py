import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})'
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
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
    except:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title_elem = soup.select_one("#productTitle")
    if not title_elem:
        return None
    
    title = title_elem.text.strip()

    # استخراج السعر
    price = None
    old_price = None
    
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
        if elem:
            price_text = elem.text.strip()
            if price_text and any(c.isdigit() for c in price_text):
                price = price_text
                break
    
    if not price:
        price_pattern = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*ر\.?س', r.text)
        if price_pattern:
            price = f"{price_pattern.group(1)} ر.س"

    # السعر القديم
    old_selectors = [
        ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
        ".a-price.a-text-price .a-offscreen",
        ".priceBlockStrikePriceString"
    ]
    
    for selector in old_selectors:
        elem = soup.select_one(selector)
        if elem:
            old_text = elem.text.strip()
            if old_text != price and any(c.isdigit() for c in old_text):
                old_price = old_text
                break

    # الصورة
    img_elem = soup.select_one("#landingImage")
    image = img_elem.get("src") if img_elem else None

    # حساب الخصم
    discount_percent = None
    try:
        if old_price and price:
            def clean_num(text):
                return float(re.sub(r'[^\d.]', '', text.replace(",", "")))
            
            old_num = clean_num(old_price)
            new_num = clean_num(price)
            
            if old_num > new_num > 0:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        pass

    if not price:
        return None

    return title, price, old_price, image, discount_percent

# ===== جمل حماسية حرشة =====

OPENINGS = [
    "🔥 سعر مجنون",
    "⚡️ فرصة ذهبية",
    "💥 عرض ناري",
    "🎯 صفقة العمر",
    "🔥 ما يتكرر",
    "⚡️ الحين أو لا",
    "💥 خصم خرافي"
]

REACTIONS = [
    "هاته الحين",
    "ما تفكر",
    "خذه فوراً",
    "بسرعة قبل ينتهي",
    "لا تنام عليه",
    "احجز فوري",
    "ما راح تلقى مثله"
]

URGENCY = [
    "ينتهي اليوم",
    "الكمية قليلة",
    "سعر مؤقت",
    "بأي لحظة يرجع",
    "الوقت ينفد",
    "لا تتردد",
    "فرصة لا تعوض"
]

def generate_post(title, price, old_price, discount_percent, original_url):
    opening = random.choice(OPENINGS)
    reaction = random.choice(REACTIONS)
    urgency = random.choice(URGENCY)
    
    # عنوان مختصر
    display_title = title[:60] + "..." if len(title) > 60 else title
    
    # نص السعر
    if discount_percent and discount_percent > 5:
        price_line = f"💰 {price} (وفر {discount_percent}%) | ❌ {old_price}"
    else:
        price_line = f"💰 {price}"
    
    # منشور حرش ومركز - الجملتين في نفس السطر
    post = f"""{opening}

🛒 {display_title}

{price_line}

👉 {reaction} | ⏰ {urgency}

🔗 {original_url}"""
    
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل رابط المنتج")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳")

        asin = extract_asin(original_url)

        if not asin:
            bot.edit_message_text("❌ رابط غير صالح", msg.chat.id, wait.message_id)
            return

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة المنتج", msg.chat.id, wait.message_id)
            return

        title, price, old_price, image, discount_percent = product

        post = generate_post(title, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            bot.edit_message_text("❌ حدث خطأ", msg.chat.id, wait.message_id)

print("🤖 البوت يعمل...")
bot.infinity_polling()
