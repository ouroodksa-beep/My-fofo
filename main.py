import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time

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
        nums = re.findall(r'[\d,]+', price_text)
        if nums:
            num = nums[0].replace(",", "")
            return f"{num} ريال سعودي"
    except:
        pass
    return price_text


def get_product(asin):
    """Scraping قوي مع محاولات متعددة"""
    url = f"https://www.amazon.sa/dp/{asin}"
    
    # قائمة User-Agents مختلفة
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]
    
    for attempt, ua in enumerate(user_agents):
        try:
            print(f"Attempt {attempt + 1} with {ua[:50]}...")
            
            headers = {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/search?q=amazon.sa",
                "Origin": "https://www.amazon.sa"
            }

            # نعمل delay بين المحاولات
            if attempt > 0:
                time.sleep(2)
            
            r = requests.get(url, headers=headers, timeout=30)
            print(f"Status: {r.status_code}, Size: {len(r.text)}")
            
            if r.status_code != 200:
                continue
                
            # نتأكد إن الصفحة مش فارغة أو كابتشا
            if len(r.text) < 5000:
                print("Page too small, might be blocked")
                continue
            
            # ندور على علامات المنتج
            if "productTitle" not in r.text and "a-price" not in r.text:
                print("No product data found")
                continue
                
            soup = BeautifulSoup(r.text, "html.parser")
            
            # ===== العنوان =====
            title = None
            title_selectors = [
                "#productTitle",
                "h1.a-size-large.a-spacing-none",
                "h1.a-size-large",
                "#title",
                "h1[data-testid='product-title']",
                ".product-title"
            ]
            
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.text.strip()
                    if len(title) > 3:
                        print(f"Title found: {title[:60]}")
                        break
            
            if not title:
                continue

            # ===== السعر الحالي =====
            price = None
            price_selectors = [
                ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
                ".a-price.a-text-price.apexPriceToPay .a-offscreen",
                ".a-price.aok-align-center .a-offscreen",
                ".a-price .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
                ".a-price-to-pay .a-offscreen",
                ".a-price-buy-box .a-offscreen",
                ".a-price-whole",
                ".a-price .a-price-whole",
                ".a-offscreen",
                ".a-price"
            ]
            
            for selector in price_selectors:
                try:
                    elem = soup.select_one(selector)
                    if elem and elem.text:
                        text = elem.text.strip()
                        if any(c.isdigit() for c in text):
                            price = text
                            print(f"Price found: {price}")
                            break
                except:
                    continue
            
            # Regex كبديل أخير
            if not price:
                price_patterns = [
                    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:ر\.?س|SAR|ريال|رس)',
                    r'(\d{1,3}(?:,\d{3})*)\s*(?:ر\.?س|SAR)',
                    r'SAR\s*(\d{1,3}(?:,\d{3})*)',
                    r'(\d+)\s*ريال'
                ]
                for pattern in price_patterns:
                    matches = re.findall(pattern, r.text)
                    if matches:
                        price = f"{matches[0]} ر.س"
                        print(f"Price from regex: {price}")
                        break

            # ===== السعر القديم =====
            old_price = None
            old_selectors = [
                ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
                ".a-price.a-text-price .a-offscreen",
                ".basisPrice .a-offscreen",
                ".priceBlockStrikePriceString",
                "[data-a-color='secondary'] .a-offscreen",
                ".a-price[data-a-strike='true'] .a-offscreen"
            ]
            
            for selector in old_selectors:
                try:
                    elem = soup.select_one(selector)
                    if elem and elem.text:
                        text = elem.text.strip()
                        if text != price and any(c.isdigit() for c in text):
                            old_price = text
                            print(f"Old price: {old_price}")
                            break
                except:
                    continue

            # ===== الصورة =====
            image = None
            img_selectors = [
                "#landingImage",
                "#imgBlkFront",
                ".a-dynamic-image",
                "#main-image",
                "img[data-a-image-name='landingImage']"
            ]
            
            for selector in img_selectors:
                try:
                    elem = soup.select_one(selector)
                    if elem:
                        for attr in ["src", "data-old-hires", "data-a-dynamic-image", "data-src"]:
                            val = elem.get(attr)
                            if val:
                                if attr == "data-a-dynamic-image" and val.startswith("{"):
                                    try:
                                        import json
                                        img_dict = json.loads(val)
                                        image = list(img_dict.keys())[0] if img_dict else None
                                    except:
                                        continue
                                else:
                                    image = val
                                if image and image.startswith("http"):
                                    break
                        if image:
                            break
                except:
                    continue

            # ===== الخصم =====
            discount_percent = None
            try:
                if old_price and price:
                    def extract_num(text):
                        nums = re.findall(r'[\d,]+\.?\d*', str(text))
                        return float(nums[0].replace(",", "")) if nums else 0
                    
                    old_num = extract_num(old_price)
                    new_num = extract_num(price)
                    
                    if old_num > new_num > 0:
                        discount_percent = int(((old_num - new_num) / old_num) * 100)
                        print(f"Discount: {discount_percent}%")
            except:
                pass

            if price:
                # نختصر اسم المنتج
                words = title.split()
                if len(words) > 5:
                    product_name = " ".join(words[:5])
                else:
                    product_name = title
                
                if len(product_name) > 60:
                    product_name = product_name[:60] + "..."
                
                return product_name, price, old_price, image, discount_percent
            else:
                print("No price found in this attempt")
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    return None


# ===================================
# ✨ التوليد النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    opening = random.choice(OPENING_SENTENCES)
    
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    
    lines = [opening]
    lines.append("")
    lines.append(f"🛒 {product_name}")
    lines.append("")
    
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
        print(f"\n{'='*50}")
        print(f"Processing: {expanded[:100]}")

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, 
                f"❌ الرابط مش لأمازون السعودية\n\n"
                f"الرابط المفكوك: `{expanded[:60]}...`\n\n"
                f"لازم يكون من `amazon.sa`",
                parse_mode="Markdown"
            )
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ ما قدرت أستخرج رقم المنتج (ASIN)")
            continue

        print(f"ASIN: {asin}")

        wait = bot.reply_to(msg, "⏳ جاري تحليل المنتج...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text(
                f"❌ ما قدرت أقرأ المنتج بعد عدة محاولات\n\n"
                f"ASIN: `{asin}`\n\n"
                f"ممكن يكون:\n"
                f"• أمازون حاط حماية قوية (Captcha)\n"
                f"• المنتج محذوف\n"
                f"• جرب منتج تاني\n\n"
                f"💡 تلميح: جرب تبعت الرابط مباشرة من أمازون بدون اختصار",
                msg.chat.id, wait.message_id,
                parse_mode="Markdown"
            )
            continue

        product_name, price, old_price, image, discount_percent = product
        post = generate_post(product_name, price, old_price, discount_percent, original_url)

        try:
            if image:
                bot.send_photo(msg.chat.id, image, caption=post)
            else:
                bot.send_message(msg.chat.id, post)

            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Send error: {e}")
            bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()
