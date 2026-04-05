import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
from concurrent.futures import ThreadPoolExecutor

TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)

class SmartGenerator:
    def __init__(self):
        self.brands = {
            "Apple": ["iphone", "ipad", "macbook", "airpods"],
            "Samsung": ["samsung", "galaxy"],
            "Sony": ["sony", "playstation"],
            "Nike": ["nike", "air max", "jordan"],
            "Adidas": ["adidas", "ultraboost"],
            "Chanel": ["chanel", "no.5"],
            "Dior": ["dior", "sauvage", "jadore"],
            "Gucci": ["gucci", "bloom"],
            "Zara": ["zara"],
            "H&M": ["h&m"],
            "Shein": ["shein"],
            "MAC": ["mac ", "lipstick"],
            "L'Oreal": ["l'oreal", "loreal"],
            "Maybelline": ["maybelline"],
            "Estee Lauder": ["estee lauder"],
            "Lancome": ["lancome"],
        }
        
        # كلمات نسائية قوية
        self.female_keywords = [
            "dress", "skirt", "blouse", "gown", "frock", "maxi", "midi", "mini",
            "abaya", "kaftan", "kimono", "robe", "nightgown", "lingerie", "bra", "panties",
            "tights", "leggings", "yoga pants", "palazzo", "saree", "lehenga",
            "heels", "high heels", "pumps", "stiletto", "wedges", "sandals women",
            "handbag", "purse", "clutch", "tote", "sling bag", "backpack women",
            "jewelry", "earrings", "necklace", "bracelet", "ring", "pendant",
            "gold", "diamond", "silver", "pearl", "ruby", "emerald",
            "makeup", "lipstick", "lip gloss", "mascara", "eyeliner", "eyeshadow",
            "foundation", "concealer", "blush", "bronzer", "highlighter",
            "primer", "setting spray", "makeup remover",
            "skincare", "cream", "serum", "moisturizer", "toner", "cleanser",
            "face mask", "sheet mask", "eye cream", "anti-aging", "wrinkle",
            "perfume", "fragrance", "eau de parfum", "eau de toilette", "attar",
            "hair care", "shampoo", "conditioner", "hair mask", "hair oil",
            "nail polish", "manicure", "pedicure", "nail care",
            "hair dryer", "straightener", "curler", "curling iron", "hair brush",
            "makeup brushes", "beauty blender", "sponge", "tweezers", "razor women",
            "maternity", "pregnancy", "nursing", "breast pump", "diaper bag",
            "baby care", "stretch mark", "prenatal",
            "feminine wash", "intimate care", "sanitary", "menstrual", "period",
            "menopause", "fertility", "ovulation",
            "hijab", "scarf", "shawl", "headband", "hair clip", "hair band",
            "wig", "hair extension", "hair accessory",
            "sports bra", "yoga mat women", "fitness women", "gym wear women",
            "women", "woman", "lady", "ladies", "female", "girl", "girls",
            "for her", "hers", "she", "madam", "miss", "mrs", "ms",
        ]
        
        # التمبليتس الجديدة - جملتين فقط وبينهم سطر فاضي
        self.templates_female = [
            "{emoji} {product} من {brand}\n\n{price} {cta}",
            "{emoji} وصل حديثاً: {product} ✨\n\n{price} {cta}",
            "{emoji} يا هلا بالأناقة! {product}\n\n{price} {cta}",
            "{emoji} {product} 💕\n\n{price} {cta}",
            "{emoji} خصم حصري على {product}\n\n{price} {cta}",
            "{emoji} {product} بجودة عالية\n\n{price} {cta}",
            "{emoji} لا يفوتكِ: {product}\n\n{price} {cta}",
            "{emoji} {product} الأكثر مبيعاً 🔥\n\n{price} {cta}",
        ]
        
        self.templates_male = [
            "{emoji} {product} من {brand}\n\n{price} {cta}",
            "{emoji} وصل: {product} ⚡\n\n{price} {cta}",
            "{emoji} {product} بأفضل سعر\n\n{price} {cta}",
            "{emoji} {product} الأصلي\n\n{price} {cta}",
            "{emoji} عرض مميز: {product}\n\n{price} {cta}",
            "{emoji} {product} بجودة عالية\n\n{price} {cta}",
            "{emoji} لا يفوتك: {product}\n\n{price} {cta}",
            "{emoji} {product} الأكثر مبيعاً 🔥\n\n{price} {cta}",
        ]
        
        self.cta_female = [
            "👉 اشتري الآن",
            "👉 اضغطي للطلب",
            "👉 حصلي عليه",
            "👉 سارعي بالشراء",
        ]
        
        self.cta_male = [
            "👉 اشتري الآن",
            "👉 اضغط للطلب",
            "👉 احصل عليه",
            "👉 سارع بالشراء",
        ]
        
        self.emojis_female = ["💕", "✨", "🌸", "💎", "🦋", "🌺", "💖", "👜", "💄", "👗"]
        self.emojis_male = ["💥", "⚡", "🔥", "📱", "💻", "🎧", "📸", "⌚", "🎯", "💪"]
    
    def is_female(self, title):
        t = title.lower()
        score = sum(2 if w in t else 0 for w in self.female_keywords)
        strong_female = ["dress", "skirt", "heels", "makeup", "lipstick", "perfume", "jewelry", "handbag", "lingerie", "maternity"]
        if any(w in t for w in strong_female):
            return True
        return score >= 2
    
    def get_brand(self, title):
        t = title.lower()
        for brand, keys in self.brands.items():
            if any(k in t for k in keys):
                return brand
        return None
    
    def clean_name(self, title, brand):
        name = title
        if brand:
            name = re.sub(brand, '', name, flags=re.IGNORECASE)
        
        junk = ["with", "and", "the", "for", "new", "original", "genuine", "official", 
                "men", "women", "man", "woman", "male", "female", "unisex"]
        for j in junk:
            name = re.sub(r'\b' + j + r'\b', '', name, flags=re.IGNORECASE)
        
        name = re.sub(r'\s+', ' ', name).strip()
        words = name.split()
        return ' '.join(words[:5]) if len(words) > 5 else name
    
    def format_price(self, price, old_price):
        if old_price and price:
            try:
                old = float(re.findall(r'[\d,.]+', old_price)[0].replace(',', ''))
                new = float(re.findall(r'[\d,.]+', price)[0].replace(',', ''))
                if old > new:
                    disc = int(((old - new) / old) * 100)
                    return f"~~{int(old):,}~~ → *{int(new):,}* ريال (-{disc}%) 🏷️"
            except:
                pass
        
        try:
            num = float(re.findall(r'[\d,.]+', price)[0].replace(',', ''))
            return f"*{int(num):,}* ريال 🏷️"
        except:
            return price
    
    def generate(self, title, price, old_price, url):
        is_female = self.is_female(title)
        brand = self.get_brand(title) or "ماركة مميزة"
        product = self.clean_name(title, brand)
        
        if is_female:
            emoji = random.choice(self.emojis_female)
            template = random.choice(self.templates_female)
            cta = random.choice(self.cta_female)
        else:
            emoji = random.choice(self.emojis_male)
            template = random.choice(self.templates_male)
            cta = random.choice(self.cta_male)
        
        price_str = self.format_price(price, old_price)
        
        post = template.format(
            emoji=emoji, brand=brand, product=product, 
            price=price_str, cta=cta
        )
        
        # إضافة الرابط في النهاية
        post += f"\n\n🔗 [اطلب من هنا]({url})"
        
        return post

def expand_url(url):
    try:
        if "amazon.sa" in url or "amazon.com" in url:
            return url
        r = requests.get(url, allow_redirects=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return r.url if "amazon." in r.url else url
    except:
        return url if "amazon." in url else None

def extract_asin(url):
    for p in [r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})']:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_image(soup):
    try:
        img = soup.select_one("#landingImage")
        if not img:
            return None
        url = img.get("data-old-hires") or img.get("src")
        if not url:
            dyn = img.get("data-a-dynamic-image")
            if dyn:
                data = json.loads(dyn)
                url = max(data.keys(), key=lambda x: data[x][0])
        if url:
            url = re.sub(r'\._.*_\.', '.', url)
            url = re.sub(r'_SL\d+_', '_SL1500_', url) if "_SL" in url else url.replace(".jpg", "_SL1500_.jpg")
            return url
    except:
        pass
    return None

def get_product(asin, domain):
    url = f"https://{domain}/dp/{asin}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ar-SA,ar;q=0.9"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code in [503, 403]:
            r = requests.get(f"https://amazon.com/dp/{asin}", headers=headers, timeout=15)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            price = soup.select_one(".a-price .a-offscreen")
            old = soup.select_one(".a-text-price .a-offscreen")
            
            if title and price:
                return {
                    "title": title.text.strip(),
                    "price": price.text.strip(),
                    "old_price": old.text.strip() if old else None,
                    "image": get_image(soup)
                }
    except:
        pass
    return None

gen = SmartGenerator()

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text)
    
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return
    
    for url in urls:
        if "amazon." not in url and "amzn." not in url:
            continue
        
        wait = bot.reply_to(msg, "⏳ جاري جلب المنتج...")
        
        expanded = expand_url(url)
        if not expanded:
            bot.delete_message(msg.chat.id, wait.message_id)
            continue
        
        asin = extract_asin(expanded)
        if not asin:
            bot.delete_message(msg.chat.id, wait.message_id)
            continue
        
        domain = "amazon.com" if "amazon.com" in expanded else "amazon.sa"
        
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                prod = ex.submit(get_product, asin, domain).result(timeout=20)
        except:
            prod = None
        
        if not prod:
            bot.edit_message_text("❌ فشل في جلب المنتج", msg.chat.id, wait.message_id)
            continue
        
        post = gen.generate(prod["title"], prod["price"], prod["old_price"], expanded)
        
        try:
            if prod["image"]:
                bot.send_photo(msg.chat.id, prod["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
            bot.delete_message(msg.chat.id, wait.message_id)

print("🔥 البوت شغال!")
bot.infinity_polling()
            "abaya", "kaftan", "kimono", "robe", "nightgown", "lingerie", "bra", "panties",
            "tights", "leggings", "yoga pants", "palazzo", "saree", "lehenga",
            # أحذية وإكسسوارات
            "heels", "high heels", "pumps", "stiletto", "wedges", "sandals women",
            "handbag", "purse", "clutch", "tote", "sling bag", "backpack women",
            # مجوهرات
            "jewelry", "earrings", "necklace", "bracelet", "ring", "pendant",
            "gold", "diamond", "silver", "pearl", "ruby", "emerald",
            # مكياج وعناية
            "makeup", "lipstick", "lip gloss", "mascara", "eyeliner", "eyeshadow",
            "foundation", "concealer", "blush", "bronzer", "highlighter",
            "primer", "setting spray", "makeup remover",
            "skincare", "cream", "serum", "moisturizer", "toner", "cleanser",
            "face mask", "sheet mask", "eye cream", "anti-aging", "wrinkle",
            "perfume", "fragrance", "eau de parfum", "eau de toilette", "attar",
            "hair care", "shampoo", "conditioner", "hair mask", "hair oil",
            "nail polish", "manicure", "pedicure", "nail care",
            # أدوات تجميل
            "hair dryer", "straightener", "curler", "curling iron", "hair brush",
            "makeup brushes", "beauty blender", "sponge", "tweezers", "razor women",
            # أمومة وطفل
            "maternity", "pregnancy", "nursing", "breast pump", "diaper bag",
            "baby care", "stretch mark", "prenatal",
            # صحة نسائية
            "feminine wash", "intimate care", "sanitary", "menstrual", "period",
            "menopause", "fertility", "ovulation",
            # إكسسوارات شعر
            "hijab", "scarf", "shawl", "headband", "hair clip", "hair band",
            "wig", "hair extension", "hair accessory",
            # رياضة نسائية
            "sports bra", "yoga mat women", "fitness women", "gym wear women",
            # كلمات توجيه
            "women", "woman", "lady", "ladies", "female", "girl", "girls",
            "for her", "hers", "she", "madam", "miss", "mrs", "ms",
        ]
        
        self.templates_female = [
            "{emoji} {brand} {product}\\n\\n{hook}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} وصل حديثاً: {brand} {product}\\n\\n✨ {benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} يا هلا بالأناقة! {brand} {product}\\n\\n{benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} {product} من {brand}\\n\\n{hook}\\n{benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} تدورين على {product}؟\\n\\n{brand} يجيب لكِ {benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} جربتِ {brand} {product}؟\\n\\n{benefit} من أول استخدام 💕\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} فخامة {brand} لكِ\\n\\n{product}\\n{hook}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} خصم حصري! {product}\\n\\n{brand} الأصلي\\n{benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
        ]
        
        self.templates_male = [
            "{emoji} {brand} {product}\\n\\n{hook}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} وصل: {brand} {product}\\n\\n✨ {benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} {product} من {brand}\\n\\n{hook}\\n{benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} {brand} {product}\\n\\nقبل: {old_price}\\nالحين: {price}\\n\\n{cta}\\n🔗 {url}",
        ]
        
        self.hooks_female = [
            "أناقة تليق بكِ يا بنت ✨",
            "طلّة تخطف الأنظار 💕",
            "جمال يتكلم عن نفسه 🌸",
            "فخامة بأسلوبكِ الخاص 💎",
            "تميزي باختياركِ 👌",
            "أصالة وجودة عالية 💅",
            "لأنكِ تستاهلين الأفضل 👑",
        ]
        
        self.hooks_male = [
            "أداء يتكلم 🎯",
            "جودة تدوم 💪",
            "فخامة ببساطة 👌",
            "تميز واضح ⚡",
        ]
        
        self.benefits_female = [
            "يعطيكِ إشراقة طبيعية",
            "يناسب ذوقكِ الرفيع",
            "يبرز جمالكِ الطبيعي",
            "راحة تكمل يومكِ بنشاط",
            "جودة تستاهل ثقتكِ",
            "تصميم يخطف الأنظار",
            "نتيجة واضحة من أول استخدام",
            "يعتني بكِ بعمق",
        ]
        
        self.benefits_male = [
            "أداء قوي يتحمل",
            "جودة تدوم معك",
            "تصميم عملي وأنيق",
            "راحة تكمل يومك",
        ]
        
        self.cta_female = [
            "👉 لا تفوتي - اشتري الحين",
            "👉 اضغطي واطلبي قبل ينتهي",
            "👉 حصلي عليه الحين يا هلا",
            "👉 جربيه بنفسكِ وشوفي الفرق",
            "👉 استمتعي بأناقتكِ",
            "👉 اطلبي الآن بسعر مميز",
        ]
        
        self.cta_male = [
            "👉 لا تفوت - اشتري الحين",
            "👉 اضغط واطلب قبل ينتهي",
            "👉 احصل عليه الحين",
            "👉 جرب بنفسك",
        ]
        
        self.emojis_female = ["💕", "✨", "🌸", "💎", "🦋", "🌺", "💖", "👜", "💄", "👗"]
        self.emojis_male = ["💥", "⚡", "🔥", "📱", "💻", "🎧", "📸", "⌚", "🎯", "💪"]
    
    def is_female(self, title):
        t = title.lower()
        score = sum(2 if w in t else 0 for w in self.female_keywords)
        # لو فيه كلمات نسائية واضحة
        strong_female = ["dress", "skirt", "heels", "makeup", "lipstick", "perfume", "jewelry", "handbag", "lingerie", "maternity"]
        if any(w in t for w in strong_female):
            return True
        return score >= 2
    
    def get_brand(self, title):
        t = title.lower()
        for brand, keys in self.brands.items():
            if any(k in t for k in keys):
                return brand
        return None
    
    def clean_name(self, title, brand):
        name = title
        if brand:
            name = re.sub(brand, '', name, flags=re.IGNORECASE)
        
        junk = ["with", "and", "the", "for", "new", "original", "genuine", "official", 
                "men", "women", "man", "woman", "male", "female", "unisex"]
        for j in junk:
            name = re.sub(r'\\b' + j + r'\\b', '', name, flags=re.IGNORECASE)
        
        name = re.sub(r'\\s+', ' ', name).strip()
        words = name.split()
        return ' '.join(words[:5]) if len(words) > 5 else name
    
    def format_price(self, price, old_price):
        if old_price and price:
            try:
                old = float(re.findall(r'[\\d,.]+', old_price)[0].replace(',', ''))
                new = float(re.findall(r'[\\d,.]+', price)[0].replace(',', ''))
                if old > new:
                    disc = int(((old - new) / old) * 100)
                    return f"~~{int(old):,}~~ → {int(new):,} ريال (-{disc}%)", str(int(old))
            except:
                pass
        
        try:
            num = float(re.findall(r'[\\d,.]+', price)[0].replace(',', ''))
            return f"{int(num):,} ريال", None
        except:
            return price, None
    
    def generate(self, title, price, old_price, url):
        is_female = self.is_female(title)
        brand = self.get_brand(title) or "ماركة مميزة"
        product = self.clean_name(title, brand)
        
        # اختيارات حسب الجنس
        if is_female:
            emoji = random.choice(self.emojis_female)
            template = random.choice(self.templates_female)
            hook = random.choice(self.hooks_female)
            benefit = random.choice(self.benefits_female)
            cta = random.choice(self.cta_female)
        else:
            emoji = random.choice(self.emojis_male)
            template = random.choice(self.templates_male)
            hook = random.choice(self.hooks_male)
            benefit = random.choice(self.benefits_male)
            cta = random.choice(self.cta_male)
        
        price_str, old_str = self.format_price(price, old_price)
        
        post = template.format(
            emoji=emoji, brand=brand, product=product, hook=hook,
            benefit=benefit, price=price_str, old_price=f"{old_str} ريال" if old_str else "",
            cta=cta, url=url
        )
        
        lines = [l for l in post.split('\\n') if l.strip()]
        return '\\n'.join(lines)

def expand_url(url):
    try:
        if "amazon.sa" in url or "amazon.com" in url:
            return url
        r = requests.get(url, allow_redirects=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return r.url if "amazon." in r.url else url
    except:
        return url if "amazon." in url else None

def extract_asin(url):
    for p in [r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})']:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_image(soup):
    try:
        img = soup.select_one("#landingImage")
        if not img:
            return None
        url = img.get("data-old-hires") or img.get("src")
        if not url:
            dyn = img.get("data-a-dynamic-image")
            if dyn:
                data = json.loads(dyn)
                url = max(data.keys(), key=lambda x: data[x][0])
        if url:
            url = re.sub(r'\\._.*_\\.', '.', url)
            url = re.sub(r'_SL\\d+_', '_SL1500_', url) if "_SL" in url else url.replace(".jpg", "_SL1500_.jpg")
            return url
    except:
        pass
    return None

def get_product(asin, domain):
    url = f"https://{domain}/dp/{asin}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ar-SA,ar;q=0.9"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code in [503, 403]:
            r = requests.get(f"https://amazon.com/dp/{asin}", headers=headers, timeout=15)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            price = soup.select_one(".a-price .a-offscreen")
            old = soup.select_one(".a-text-price .a-offscreen")
            
            if title and price:
                return {
                    "title": title.text.strip(),
                    "price": price.text.strip(),
                    "old_price": old.text.strip() if old else None,
                    "image": get_image(soup)
                }
    except:
        pass
    return None

gen = SmartGenerator()

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\\S+', msg.text)
    
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return
    
    for url in urls:
        if "amazon." not in url and "amzn." not in url:
            continue
        
        wait = bot.reply_to(msg, "⏳...")
        
        expanded = expand_url(url)
        if not expanded:
            bot.delete_message(msg.chat.id, wait.message_id)
            continue
        
        asin = extract_asin(expanded)
        if not asin:
            bot.delete_message(msg.chat.id, wait.message_id)
            continue
        
        domain = "amazon.com" if "amazon.com" in expanded else "amazon.sa"
        
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                prod = ex.submit(get_product, asin, domain).result(timeout=20)
        except:
            prod = None
        
        if not prod:
            bot.edit_message_text("❌ فشل", msg.chat.id, wait.message_id)
            continue
        
        post = gen.generate(prod["title"], prod["price"], prod["old_price"], expanded)
        
        try:
            if prod["image"]:
                bot.send_photo(msg.chat.id, prod["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except:
            bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)

print("🔥 شغال!")
bot.infinity_polling()
