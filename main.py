import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import os

TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
bot = telebot.TeleBot(TOKEN)

DB_FILE = "posted.txt"

if not os.path.exists(DB_FILE):
    open(DB_FILE, "w").close()

def expand_url(url):
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        return r.url
    except:
        return url

def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def is_posted(asin):
    with open(DB_FILE, "r") as f:
        return asin in f.read()

def mark_posted(asin):
    with open(DB_FILE, "a") as f:
        f.write(asin + "\n")

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    r = requests.get(url, headers=headers, timeout=20)

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title_elem = soup.select_one("#productTitle")
    price_elem = soup.select_one(".a-price .a-offscreen")
    old_price_elem = soup.select_one(".a-price.a-text-price .a-offscreen")
    img_elem = soup.select_one("#landingImage")
    
    # محاولة استخراج الصنف من breadcrumb أو العنوان
    category = None
    breadcrumb = soup.select_one("#wayfinding-breadcrumbs_feature_div")
    if breadcrumb:
        cats = breadcrumb.find_all("a")
        if len(cats) >= 2:
            category = cats[-2].text.strip()
    
    if not category and title_elem:
        # استخراج أول كلمة أو كلمتين من العنوان كصنف تقريبي
        title_words = title_elem.text.strip().split()[:3]
        category = " ".join(title_words)

    if not title_elem or not price_elem:
        return None

    title = title_elem.text.strip()
    price = price_elem.text.strip()
    old_price = old_price_elem.text.strip() if old_price_elem else None
    image = img_elem.get("src") if img_elem else None

    discount_percent = None

    try:
        if old_price:
            # تنظيف السعر من الرموز والفواصل
            old_clean = re.sub(r'[^\d.]', '', old_price.replace(",", ""))
            new_clean = re.sub(r'[^\d.]', '', price.replace(",", ""))
            old_num = float(old_clean)
            new_num = float(new_clean)
            if old_num > new_num:
                discount_percent = int(((old_num - new_num) / old_num) * 100)
    except:
        discount_percent = None

    return title, price, old_price, image, discount_percent, category

# ===== نبرة سعودية طبيعية =====

OPENINGS = [
    "والله صفقة حلوة اليوم",
    "ما شاء الله تبارك الله السعر حلو",
    "الحين فرصتك ذهبية",
    "صراحة منتج يستاهل",
    "شفت السعر الحين؟",
    "عرض يفوتك ولا يفوت غيرك",
    "ببلاش تقريباً",
    "تخفيض مجنون صراحة"
]

REACTIONS = [
    "أنا جربت أشياء من نفس النوع ومرتبة",
    "جودته ممتازة والله",
    "يستاهل التجربة بصراحة",
    "ما راح تلقى مثله بهالسعر",
    "الناس مدحته كثير",
    "استخدمته قبل وفادني كثير",
    "من أفضل المنتجات اللي جربتها"
]

URGENCY = [
    "بسرعة قبل ينتهي العرض",
    "الكمية محدودة يا جماعة",
    "ما أدري كم باقي من الكمية",
    "احجز الحين ولا تنتظر",
    "السعر يرجع طبيعي بأي لحظة"
]

def generate_post(title, price, old_price, discount_percent, affiliate_url, category):
    opening = random.choice(OPENINGS)
    reaction = random.choice(REACTIONS)
    urgency = random.choice(URGENCY)
    
    # استخراج اسم المنتج المختصر للعنوان
    short_title = title[:60] + "..." if len(title) > 60 else title
    
    # بناء نص السعر بشكل طبيعي
    if discount_percent and discount_percent > 5:
        price_text = f"🔥 خصم {discount_percent}% | كان {old_price} الحين {price}"
    else:
        price_text = f"💰 بـ {price} فقط"
    
    # تنسيق المنشور كأنه إنسان
    post = f"""{opening}

🛒 {short_title}

📦 الصنف: {category if category else 'متنوع'}
{price_text}

💭 {reaction}
⚡ {urgency}

🔗 للطلب: {affiliate_url}

#عروض #تسوق #السعودية"""
    
    return post

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)

    if not urls:
        bot.reply_to(msg, "أرسل لي رابط منتج من أمازون السعودية وأنشره لك بشكل مرتب 👍")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        expanded_url = expand_url(original_url)
        asin = extract_asin(expanded_url)

        if not asin:
            bot.edit_message_text("❌ الرابط مو من أمازون أو فيه مشكلة", msg.chat.id, wait.message_id)
            return

        if is_posted(asin):
            bot.edit_message_text("⚠️ هذا المنتج نشرته قبل كذا", msg.chat.id, wait.message_id)
            return

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ ما قدرت أجيب تفاصيل المنتج، جرب رابط ثاني", msg.chat.id, wait.message_id)
            return

        title, price, old_price, image, discount_percent, category = product

        post = generate_post(title, price, old_price, discount_percent, original_url, category)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            
            mark_posted(asin)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ صار خطأ: {str(e)}", msg.chat.id, wait.message_id)

print("🤖 البوت شغال...")
bot.infinity_polling()
