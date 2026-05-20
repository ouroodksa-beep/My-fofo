import telebot, requests, re, time, json, random
from bs4 import BeautifulSoup

TOKEN = "7956075348:AAEYTL28GKeMN7TXyVeGM69iUcfg5ZwOSIk"
bot = telebot.TeleBot(TOKEN)
GROQ_API_KEY = "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"

BRAND_NAMES = {
    "nespresso": "Nespresso", "nescafe": "Nescafé", "nescafé": "Nescafé",
    "iphone": "iPhone", "ipad": "iPad", "macbook": "MacBook", "airpods": "AirPods",
    "samsung": "Samsung", "sony": "Sony", "lg": "LG", "dyson": "Dyson",
    "philips": "Philips", "bosch": "Bosch", "adidas": "Adidas", "nike": "Nike",
    "puma": "Puma", "gucci": "Gucci", "prada": "Prada", "dior": "Dior",
    "chanel": "Chanel", "loreal": "L'Oréal", "loreal": "L'Oréal", "loreal": "L'Oréal"
}

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "laptop", "ipad", "airpods", "headphones", "camera", "tv", "screen", "watch", "speaker", "router"],
    "fashion": ["shirt", "pants", "jeans", "jacket", "dress", "shoes", "sneakers", "boots", "bag", "wallet", "belt"],
    "beauty": ["perfume", "cream", "shampoo", "makeup", "lipstick", "serum", "oud"],
    "home": ["fridge", "washing", "vacuum", "ac", "heater", "blender", "oven", "sofa", "bed", "lamp"],
    "sports": ["treadmill", "dumbbell", "yoga", "bicycle", "gym", "fitness"]
}

def protect_brands(t):
    for k, v in sorted(BRAND_NAMES.items(), key=lambda x: -len(x[0])):
        t = re.compile(re.escape(k), re.I).sub(v, t)
    return t

def detect_category(n):
    n = n.lower()
    for c, kws in CATEGORY_KEYWORDS.items():
        if any(k in n for k in kws):
            return c
    return "general"

def detect_gender(n):
    n = n.lower()
    if any(w in n for w in ['women', 'lady', 'female', 'نسائي', 'فستان', 'dress', 'skirt', 'makeup', 'lipstick']):
        return 'women'
    if any(w in n for w in ['men', 'male', 'رجالي', 'عطر رجالي']):
        return 'men'
    return 'neutral'

def get_emoji(c):
    return {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}.get(c, "📦")

# ========== NEW: Support all Amazon domains + affiliate links ==========

def is_amazon_link(url):
    """Check if URL is any Amazon or affiliate link"""
    amazon_domains = [
        'amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.it', 'amazon.es',
        'amazon.ca', 'amazon.com.au', 'amazon.in', 'amazon.jp', 'amazon.cn',
        'amazon.sa', 'amazon.ae', 'amazon.com.tr', 'amazon.com.br', 'amazon.com.mx',
        'amzn.to', 'amzn.com', 'a.co', 'z.cn'
    ]
    url_lower = url.lower()
    return any(domain in url_lower for domain in amazon_domains)

def resolve_amazon_url(url):
    """Follow redirects to get real Amazon URL from affiliate/short links"""
    # Handle amzn.to and other short links
    short_domains = ['amzn.to', 'a.co']
    if any(domain in url.lower() for domain in short_domains):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            resp = requests.head(url, headers=headers, allow_redirects=True, timeout=15)
            if resp.status_code in [200, 301, 302] and resp.url != url:
                return resp.url
        except Exception as e:
            print(f"Redirect error: {e}")
    return url

def get_asin(url):
    """Extract ASIN from any Amazon URL format"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/([A-Z0-9]{10})/?$',
        r'[?&]asin=([A-Z0-9]{10})',
        r'[?&]dp=([A-Z0-9]{10})',
        r'[?&]productId=([A-Z0-9]{10})',
        r'%2Fdp%2F([A-Z0-9]{10})',
        r'[?&]url=.*%2Fdp%2F([A-Z0-9]{10})',
    ]
    for p in patterns:
        m = re.search(p, url, re.I)
        if m:
            return m.group(1)
    return None

def get_amazon_domain(url):
    """Extract Amazon domain from URL"""
    m = re.search(r'(amazon\.[a-z.]+)', url.lower())
    if m:
        return m.group(1)
    # Default to amazon.com if can't detect
    return "amazon.com"

# ========== END NEW ==========

def clean_price(t):
    try:
        n = re.findall(r'[\d,]+(?:\.\d+)?', t)[0].replace(",", "")
        return f"{int(float(n))} ريال"
    except:
        return t

def extract_num(t):
    try:
        return float(re.findall(r'[\d,]+(?:\.\d+)?', t)[0].replace(",", ""))
    except:
        return 0

def get_image(soup):
    img = soup.select_one("#landingImage")
    if img:
        url = img.get("data-old-hires") or img.get("src")
        if not url:
            try:
                d = json.loads(img.get("data-a-dynamic-image", "{}"))
                url = sorted(d.keys(), key=lambda x: d[x][0]*d[x][1], reverse=True)[0] if d else None
            except:
                pass
        if url:
            return re.sub(r'_SX\d+_SY\d+_|_SX\d+_|_SY\d+_|_CR\d+,\d+,\d+,\d+_|_AC_SL\d+_|_SCLZZZZZZZ_|_FMwebp_|_QL\d+_', '_', url).split('?')[0]
    og = soup.select_one('meta[property="og:image"]')
    return og.get("content") if og else None

def get_seller(soup):
    for sel in ["#merchant-info a", "[data-feature-name='merchant'] a", "#merchant-info"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if len(t) > 2:
                return t
    return None

def get_rating(soup):
    r = soup.select_one("#acrPopover .a-icon-alt") or soup.select_one("[data-hook='rating-out-of-text']")
    rating = re.search(r'([\d.]+)', r.get_text(strip=True)).group(1) if r else None
    rc = soup.select_one("#acrCustomerReviewText") or soup.select_one("[data-hook='total-review-count']")
    reviews = re.search(r'([\d,]+)', rc.get_text(strip=True)).group(1).replace(",", "") if rc else None
    return rating, reviews

def get_stock(soup):
    for sel in ["#availability span", ".a-color-price.a-text-bold", "#outOfStock"]:
        el = soup.select_one(sel)
        if el and any(w in el.get_text(strip=True).lower() for w in ['left', 'متبقي', 'stock', 'soon', 'limited', 'only']):
            return el.get_text(strip=True)
    return None

def get_coupons(soup, price):
    found = []
    for sel in ["#couponTextInput", "[data-feature-name='coupon']", ".couponText", "#couponContainer", ".savingsPercentage"]:
        for el in soup.select(sel):
            txt = el.get_text(strip=True)
            if len(txt) > 3:
                p = re.search(r'(\d+)%', txt)
                if p:
                    pct = int(p.group(1))
                    code = re.search(r'\b([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z]{4,})\b', txt)
                    code = code.group(1) if code else f"خصم {pct}%"
                    found.append({"code": code, "percent": pct, "final_price": int(price - price * pct / 100), "text": txt})
    seen = {}
    uniq = []
    for c in found:
        k = c["code"].upper()
        if k not in seen:
            seen[k] = True
            uniq.append(c)
    uniq.sort(key=lambda x: x["percent"], reverse=True)
    return uniq

def get_product(asin, domain="amazon.sa"):
    """Fetch product from any Amazon domain"""
    url = f"https://www.{domain}/dp/{asin}"

    # Try multiple user agents and domains
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
    ]

    for ua in user_agents:
        try:
            r = requests.get(url, headers={
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Referer": "https://www.google.com/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }, timeout=30)

            if r.status_code != 200 or len(r.text) < 5000:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            if not title:
                continue

            full = title.text.strip()
            price = None
            for sel in [".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen", ".a-price .a-offscreen", ".a-price-whole"]:
                el = soup.select_one(sel)
                if el and el.text and any(c.isdigit() for c in el.text):
                    price = el.text.strip()
                    break
            if not price:
                continue

            old = None
            for sel in [".a-price.a-text-price[data-a-color='secondary'] .a-offscreen", ".basisPrice .a-offscreen"]:
                el = soup.select_one(sel)
                if el and el.text != price and any(c.isdigit() for c in el.text):
                    old = el.text.strip()
                    break

            img = get_image(soup)
            seller = get_seller(soup)
            rating, reviews = get_rating(soup)
            stock = get_stock(soup)
            cur = extract_num(price)
            coupons = get_coupons(soup, cur)

            return {
                "name": protect_brands(full[:80]),
                "full_title": full,
                "price": price,
                "old_price": old,
                "image": img,
                "seller": seller,
                "rating": rating,
                "reviews": reviews,
                "stock": stock,
                "coupons": coupons,
                "current_num": cur,
                "domain": domain
            }
        except Exception as e:
            print(f"Error: {e}")
    return None

HEADLINES = {
    "electronics": [
        "✨ من بين آلاف الخيارات،\nهالصفقة تبرق وتلمع\n— سعر **{price}** يخليك تتوقف\nوتفكر: وش يمنعك الحين؟ 🔥",
        "🌟 يا هلا بالصفقة اللي تستاهل\nكل ثانية تفكير\n**{discount}%** خصم حقيقي 💎",
        "⚡️ تقنية بمواصفات عالية\nوسعر **{price}** معقول\nنادر تلقى مثله 🎯",
        "🔥 فرصة ما تتكرر\nجهاز بـ **{price}** يستاهل\nكل قرش فيه 🚀",
        "💡 ذكاء الاختيار في التوقيت\n— والحين يصرخ: اشتري!\n**{discount}%** خصم ⚡️"
    ],
    "fashion_men": [
        "👔 أناقة رجالية بثقة\n— هالطقم بـ **{price}**\nيمنحك الاثنين 🔥",
        "🕶️ طلّة تفرض احترامك\nبسعر **{price}** يفرض تقديرك 💎",
        "⌚ وقتك ثمين\nوساعتك بـ **{price}** تستاهله ⚡️",
        "👟 حذاء يركض بك للأهداف\nوسعر **{price}** يركض بالتوفير 🌟",
        "🧥 جاكيت شتوي بخفة سعر\n**{price}** مع **{discount}%** يدفي القلب 🔥"
    ],
    "fashion_women": [
        "👗 فستان يحكي قصة\nبـ **{price}** يحكي ذكاء اختيارك 🔥",
        "👜 شنطة تكمل إطلالتك\nوسعر **{price}** يكمل فرحتك 💎",
        "💄 مكياج يزين وجهك\nوسعر **{price}** يزين يومك ⚡️",
        "👠 كعب يرفعك فوق\nوسعر **{price}** يرفعك أعلى 🌟",
        "🧕 عباية تسترك وتزينك\nبـ **{price}** تستر ميزانيتك 🔥"
    ],
    "beauty_men": [
        "🧔 رجل مهتم بنظافته\n— هالمنتج بـ **{price}** يهتم بميزانيتك 🔥",
        "💈 حلاقة نظيفة بمنتج نظيف\nوسعر **{price}** ينظف الغلاء 💎",
        "👔 عطر يثبت حضورك\nبسعر **{price}** يثبت ذكاءك ⚡️",
        "🧴 لوشن يترطب بشرتك\nوسعر **{price}** يترطب قلبك 🌟",
        "🪒 ماكينة تفصلك عن الباهت\nوسعر **{price}** يفصلك عن الباهظ 🔥"
    ],
    "beauty_women": [
        "💅 طلاء يلمع زي عينك\nلما تشوفين **{price}** ⚡️",
        "🧖‍♀️ كريم يخليك تتأملين\nبمرآتك ومحفظتك بـ **{price}** 🌟",
        "💋 أحمر شفاه بـ **{price}**؟\nيا ليت كل القرارات الحلوة تجي كذا 🔥",
        "🌸 عطر يفوح بأريج الأناقة\nوسعر **{price}** يفوح بالذكاء 💎",
        "✨ سيروم يبرق وجهك\nوسعر **{price}** يبرق يومك ⚡️"
    ],
    "home": [
        "🏠 بيت يعكس ذوقك\nيبدأ بـ **{price}** يعكس ذكاءك 🔥",
        "🛋️ أثاث يستقبل ضيوفك\nبكرامة وسعر **{price}** بترحيب 💎",
        "🍳 جهاز يختصر وقتك\nوخصم **{discount}%** يختصر قلقك ⚡️",
        "❄️ مكيف يبرد حر الصيف\nوسعر **{price}** يبرد قلقك 🌟",
        "🧹 مكنسة تنظف بيتك\nوسعر **{price}** ينظف ميزانيتك 🔥"
    ],
    "sports": [
        "💪 قوة تبدأ بقرار\n— قرار بـ **{price}** يبدأ بذكاء 🔥",
        "🏋️ جهاز يرفعك فوق\nوسعر **{price}** يرفع ميزانيتك 💎",
        "🏃 حذاء يجري بك للأهداف\nوخصم **{discount}%** يجري بالتوفير ⚡️",
        "🧘 يوغا تريح جسمك\nوسعر **{price}** تريح محفظتك 🌟",
        "🚴 دراجة تقوي قلبك\nوسعر **{price}** يقوي قرارك 🔥"
    ],
    "general": [
        "✨ من بين كل الخيارات\nوقف عند هالصفقة\n— **{price}** تستاهل التفكير 🔥",
        "🌟 ذهب يلمع دائماً\nبس هالصفقة بـ **{price}** تلمع أكثر 💎",
        "⚡️ في زحمة العروض\nنادر تلقى صفقة حقيقية\nهذي واحدة منهم ⚡️",
        "🔥 فرصة ما تجي مرتين\nهذي المرة الأولى بـ **{price}** 🌟",
        "💎 جودة وسعر معقول\nيجتمعون في صفقة بـ **{price}** 🔥"
    ]
}

def get_headline(name, cat, gender, price, discount):
    sub = cat
    if cat == "fashion":
        sub = f"fashion_{gender}" if gender in ["men", "women"] else "general"
    elif cat == "beauty":
        sub = f"beauty_{gender}" if gender in ["men", "women"] else "general"
    templates = HEADLINES.get(sub, HEADLINES["general"])
    h = random.choice(templates).format(price=price, discount=discount)
    price_digits = re.sub(r'[^\d]', '', price)
    has_price = price_digits and price_digits in re.sub(r'[^\d]', '', h)
    return h, has_price

def generate_post(data, url):
    name = data["name"]
    price = clean_price(data["price"])
    old = clean_price(data["old_price"]) if data["old_price"] else None
    old_num = extract_num(data["old_price"]) if data["old_price"] else 0
    cur_num = data["current_num"]
    discount = int(((old_num - cur_num) / old_num) * 100) if old_num > cur_num > 0 else 0
    cat = detect_category(name)
    gender = detect_gender(name)
    headline, has_price = get_headline(name, cat, gender, price, discount)
    parts = [headline]
    name_words = set(name.lower().split()[:3])
    if not bool(name_words & set(headline.lower().split())):
        parts.append(f"{get_emoji(cat)} {name}")
    if not has_price:
        if old and old_num > cur_num:
            parts.append(f"❌ السعر السابق: ~~{old}~~\n💥 السعر الآن: **{price}** (خصم {discount}%)")
        else:
            parts.append(f"💰 السعر: **{price}**")
    if data["coupons"]:
        b = data["coupons"][0]
        parts.append(f"🎟️ كوبون **{b['percent']}%** ← يصير بـ **{b['final_price']} ريال**! 🔥")
        if len(data["coupons"]) > 1:
            parts.append("💡 كوبونات إضافية:\n" + "\n".join(f"   • `{c['code']}` — **{c['percent']}%**" for c in data["coupons"][1:3]))
    
    # ========== تعديل: الرابط ظاهر تحت كلمة رابط الشراء ==========
    parts.append(f"🛒 رابط الشراء:\n{url}")
    
    return "\n\n".join(parts)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text.strip())
    if not urls:
        return bot.reply_to(msg, "❌ أرسل رابط أمازون")

    for u in urls:
        # ========== NEW: Check any Amazon link ==========
        if not is_amazon_link(u):
            bot.reply_to(msg, "❌ يرجى إرسال رابط أمازون فقط (أي دولة)")
            continue

        # Resolve affiliate/short links
        resolved_url = resolve_amazon_url(u)

        asin = get_asin(resolved_url)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج (ASIN) من الرابط\nجرب رابط مباشر من صفحة المنتج")
            continue

        domain = get_amazon_domain(resolved_url)

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")
        p = get_product(asin, domain)

        if not p:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج\nقد يكون المنتج غير متوفر أو محمي", msg.chat.id, wait.message_id)
            continue

        # Use original URL (affiliate link) in the post to preserve commissions
        post = generate_post(p, u)

        try:
            if p["image"]:
                bot.send_photo(msg.chat.id, p["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error: {e}")
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت يعمل — يقبل أي رابط أمازون + أفيلييت 🔥")
bot.infinity_polling()
