import telebot
import requests
from bs4 import BeautifulSoup
import re
import random

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🎯 جمل تسويقية سعودية عشوائية
# ===================================

OPENING_SENTENCES = [
    "والله صفقة ما تتفوت 🔥",
    "ما شاء الله تبارك الله السعر حلو 💥",
    "سعر خرافي صراحة ⚡️",
    "فرصة ذهبية الحين 🎯",
    "عرض ناري وما يتكرر 🔥",
    "الحين أو لا 💪",
    "ببلاش تقريباً 😍",
    "تخفيض مجنون 👌",
    "صفقة العمر هذي 💯",
    "الكمية قليلة جداً ⚠️",
    "ينتهي بأي لحظة ⏰",
    "لا تنام عليه 🚨",
    "خذه فوراً 💨",
    "هاته الحين قبل يروح 🏃‍♂️",
    "ما راح تلقى مثله 👀",
    "سعر تاريخي 📉",
    "فرصة لا تعوض أبداً 💎",
    "الوقت ينفد بسرعة ⏳",
    "احجز قبل الكل 🏆",
    "المنتج مطلوب جداً 🔥",
    "يستاهل التجربة 👍",
    "أنصح فيه بقوة 💪",
    "ما راح تندم عليه 😎",
    "فادني كثير شخصياً 🙌",
    "منتج موثوق 100% ✅",
    "سعره كان ضعف الحين 😱",
    "العرض محدود جداً ⚡️",
    "بسرعة قبل ينتهي 🚀",
    "لا تفكر كثير 🤔",
    "قرارك الذكي اليوم 🧠",
    "فرصتك الذهبية 💰",
    "سعر مغري جداً 🤩",
    "ما يصير كل يوم 📅",
    "الحين وقته ⏰",
    "لا تضيع الفرصة 🎯",
    "خذه وارتاح 😌",
    "سعر ينافس الجميع 🏆",
    "صفقة ناجحة مضمونة 💯",
    "الكل يدور عليه 👥",
    "ينتهي اليوم 📆",
    "الكمية بتخلص ⚠️",
    "سعر مؤقت فقط ⏳",
    "بأي لحظة يرجع غالي 📈",
    "استغل العرض الحين 💪",
    "ما راح تلقى أحسن من كذا 🥇",
    "عرض قوي ومميز 💥",
    "سعر منافس جداً 🏷️",
    "فرصة للتوفير 💰",
    "منتج ممتاز بسعر أقل ⭐",
    "يستحق الشراء 🛒",
    "خيار ذكي للجميع 🧠",
    "سعر معقول جداً 👌",
    "عرض يفوتك ولا يفوت غيرك 🏃‍♂️",
    "المنتج يستاهل 💎",
    "جودته عالية 👍",
    "تجربة مستخدم ممتازة ⭐",
    "الناس مدحته 🗣️",
    "منتج شهير ومطلوب 🔥",
    "سعره كان أغلى 📉",
    "الحين وقته المناسب ⏰",
    "لا تتردد كثير 🤔",
    "فرصة للي يبي يوفر 💰",
    "سعر يناسب الجيب 👛",
    "منتج عملي ومفيد 🔧",
    "يستاهل الفلوس 💵",
    "قرار شراء صحيح ✅",
    "سعر ممتاز للجودة ⭐",
    "عرض مناسب جداً 👌",
    "المنتج يعطي قيمة 💎",
    "يستحق التجربة 🎯",
    "سعره منافس 🏷️",
    "الكل يشكر فيه 🙏",
    "منتج موثوق من أمازون ✅",
    "سعر اليوم فقط 📅",
    "عرض حصري 🔥",
    "ما راح تلقى زيه 🥇",
    "الجودة تتكلم 📢",
    "سعر يرضيك 😊",
    "منتج يفرق معك 💪",
    "يستاهل الاهتمام 👀",
    "فرصة للتميز 🌟",
    "سعر مناسب للجميع 👥",
    "المنتج يعجبك ❤️",
    "جودة ممتازة ⭐⭐⭐⭐⭐",
    "سعر ينافس السوق 🏪",
    "بسرعة العرض ينتهي 🚨",
    "لا تنتظر كثير ⏳",
    "احجز الحين 🛒",
    "الكمية محدودة ⚠️",
    "الوقت ضيق ⏰",
    "العرض ما يدوم 📉",
    "بأي لحظة ينتهي 🛑",
    "لا تفوت الفرصة 🎯",
    "سارع بالحجز 🏃‍♂️",
    "المنتج ينفذ بسرعة 💨",
    "الكل يطلبه الحين 🔥",
    "العرض مش حيكون طويل ⏳",
    "خذه قبل الكل 🥇",
    "السعر يرجع غالي 📈",
    "الحين فرصتك 💎",
    "لا تتأخر 🚨",
    "بسرعة قبل ينفذ ⚡️",
    "العرض مؤقت ⏰",
    "الكمية قليلة ⚠️",
    "استغل اللحظة 🎯",
    "الوقت ذهب 💰",
    "لا تضيع الوقت ⏳",
    "سارع بالطلب 🚀",
    "المنتج يروح بسرعة 💨",
    "العرض ينتهي قريب 📆",
    "احجز مكانك 🏆",
    "لا تفوتك الصفقة 🎯",
    "الحين أو ابتعد 🚪",
    "سعر مؤقت جداً ⏳",
    "الكمية بتخلص ⚠️",
    "بسرعة البرق ⚡",
    "العرض ما يتكرر 🔄",
    "خذه ولا تندم ✅",
    "الوقت ينفد ⏰",
    "المنتج مطلوب 🔥",
    "الكل حاب ياخذه 👥",
    "العرض محدود الوقت ⏳",
    "لا تفكر طويل 🤔",
    "سارع قبل فوات الأوان 🚨",
    "منتج أصلي مضمون ✅",
    "جودة عالية صراحة ⭐",
    "تقييماته ممتازة 🌟",
    "الناس تشكر فيه 🙏",
    "منتج موثوق من الجميع 👥",
    "جودته تفرق 🎯",
    "منتج يستاهل الثقة 💯",
    "أصلي 100% ✅",
    "جودة ممتازة للسعر ⭐",
    "الناس راضية عنه 😊",
    "منتج معروف بجودته 🏆",
    "تقييمات إيجابية 👍",
    "الكل يمدحه 🗣️",
    "منتج يستاهل 💎",
    "جودة تنافسية 🏅",
    "منتج ممتاز فعلاً ⭐",
    "الناس تشتريه كثير 🛒",
    "منتج موثوق للجميع ✅",
    "جودة عالية وممتازة ⭐⭐⭐",
    "الكل يشهد له 🙌",
    "منتج أصلي ومضمون 💯",
    "جودة تستاهل 👌",
    "تقييمات المستخدمين عالية 📊",
    "منتج يعطي قيمة 💎",
    "الناس توصي فيه 👥",
    "جودة ممتازة حقيقية ⭐",
    "منتج يستاهل الشراء 🛒",
    "أصلي ومضمون ✅",
    "الكل يثق فيه 🤝",
    "جودة لا تتغير 💎",
    "منتج ممتاز للاستخدام 🔧",
    "الناس تشتريه مرة ثانية 🔄",
    "جودة تفرق معك 💪",
    "منتج يستاهل الفلوس 💵",
    "الكل راضي عنه 😊",
    "منتج موثوق 100% ✅",
    "جودة عالية جداً ⭐⭐⭐⭐⭐",
    "تقييماته ممتازة فعلاً 🌟",
    "الناس تحبه ❤️",
    "منتج يستاهل التجربة 🎯",
    "وفرت كثير معاه 💰",
    "سعر أقل من السوق 🏪",
    "توفير حقيقي ✅",
    "سعر ينافس الجميع 🏆",
    "أرخص من المحلات 🏪",
    "سعر ممتاز للجودة ⭐",
    "توفير مضمون 💯",
    "سعر يرضيك 😊",
    "أقل سعر شفته 👀",
    "صفقة توفر فلوسك 💰",
    "سعر منافس جداً 🏷️",
    "توفير يستاهل 👌",
    "سعر معقول للجميع 👥",
    "أرخص من المتوقع 😱",
    "صفقة ذكية 🧠",
    "سعر يناسب ميزانيتك 💳",
    "توفير حقيقي ومضمون ✅",
    "سعر ممتاز جداً ⭐",
    "أقل من السوق المحلي 🏪",
    "صفقة تستاهل 💎",
    "سعر يريح الجيب 👛",
    "توفير كبير معاه 💰",
    "سعر مناسب للكل 👥",
    "أرخص من غيره 🏷️",
    "صفقة ناجحة 💯",
    "سعر يعطيك قيمة 💎",
    "توفير ممتاز ⭐",
    "سعر ينافس المحلات 🏪",
    "أقل سعر متاح 🔥",
    "صفقة ذكية للتوفير 🧠",
    "سعر يرضي الجميع 😊",
    "توفير يفرق 💰",
    "سعر ممتاز للاستخدام 🔧",
    "أرخص مما تتخيل 😱",
    "صفقة تستاهل الاهتمام 👀",
    "منتج مميز جداً 🌟",
    "سعر مناسب للجودة ⭐",
    "يستاهل الاقتناء 💎",
    "المنتج يعجب الجميع 👥",
    "خيار ممتاز ✅",
    "سعر يستاهل 💰",
    "المنتج مفيد جداً 🔧",
    "يستحق الانتباه 👀",
    "سعر منافس 🏷️",
    "المنتج يفرق 💪",
    "يستاهل التجربة 🎯",
    "سعر معقول 👌",
    "المنتج عملي 🔧",
    "يستحق الشراء 🛒",
    "سعر يناسب 💰",
    "المنتج ممتاز ⭐",
    "يستاهل الفلوس 💵",
    "سعر جيد 👍",
    "المنتج يعطي فائدة ✅",
    "خيار مناسب 👌",
    "يستحق الاهتمام 👀",
    "سعر منطقي 🧠",
    "المنتج فعال 💪",
    "يستاهل الاقتناء 💎",
    "سعر مقبول 👌",
    "المنتج مفيد ✅",
    "يستحق التجربة 🎯",
    "سعر يرضي 😊",
    "المنتج جيد 👍",
    "خيار جيد ✅",
    "يستاهل الشراء 🛒",
    "سعر لطيف 😊",
    "المنتج مناسب 👌",
    "يستحق النظر 👀",
    "سعر يعجب 😍",
    "المنتج يستاهل 💎",
    "يستحق الاقتناء ✅",
    "سعر مناسب جداً 👌",
    "المنتج فعلاً ممتاز ⭐",
    "يستاهل الاهتمام 👀",
    "سعر يستحق 💰",
    "المنتج يعطي قيمة حقيقية 💎",
    "يستحق التجربة فعلاً 🎯",
    "سعر ممتاز للجميع 👥",
    "المنتج يفرق معك 💪",
    "يستاهل الاقتناء فعلاً 💎",
    "سعر ينافس بقوة 💪",
    "المنتج مميز فعلاً 🌟",
    "يستحق الشراء الآن 🚨",
    "سعر يستاهل الاهتمام 👀"
]

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


def clean_price(price_text):
    """ينظف السعر ويحوله لصيغة ريال سعودي بدون نقطة"""
    try:
        # نستخرج الرقم
        nums = re.findall(r'[\d,]+', price_text)
        if nums:
            # ننظف ونحط ريال سعودي
            num = nums[0].replace(",", "")
            return f"{num} ريال سعودي"
    except:
        pass
    return price_text


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

    # العنوان - اسم المنتج بس (أول 3-4 كلمات)
    title_elem = soup.select_one("#productTitle")
    if not title_elem:
        return None
    
    full_title = title_elem.text.strip()
    # ناخذ أول 3-4 كلمات كاسم للمنتج
    words = full_title.split()
    if len(words) > 4:
        product_name = " ".join(words[:4])
    else:
        product_name = full_title
    
    # ننظف الاسم
    product_name = product_name.replace("|", "").replace("-", "").strip()
    if len(product_name) > 50:
        product_name = product_name[:50] + "..."

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

    return product_name, price, old_price, image, discount_percent


# ===================================
# ✨ التوليد النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    # جملة عشوائية في البداية
    opening = random.choice(OPENING_SENTENCES)
    
    # تنظيف الأسعار
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    
    # بناء المنشور
    lines = [opening]
    lines.append("")
    lines.append(f"🛒 {product_name}")
    lines.append("")
    
    # الأسعار
    if clean_old and discount_percent and discount_percent > 5:
        lines.append(f"❌ قبل: {clean_old}")
        lines.append(f"✅ الحين: {clean_current} (وفر {discount_percent}%)")
    else:
        lines.append(f"💰 السعر: {clean_current}")
    
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

        product_name, price, old_price, image, discount_percent = product
        post = generate_post(product_name, price, old_price, discount_percent, original_url)

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
