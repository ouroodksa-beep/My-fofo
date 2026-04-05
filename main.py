import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json
from concurrent.futures import ThreadPoolExecutor

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
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
            "Dior": ["dior", "sauvage"],
            "Gucci": ["gucci", "bloom"],
            "Zara": ["zara"],
            "H&M": ["h&m"],
            "Shein": ["shein"],
            "MAC": ["mac ", "lipstick"],
            "L'Oreal": ["l'oreal", "loreal"],
        }
        
        self.female_words = ["woman", "women", "lady", "dress", "skirt", "heels", "makeup", "lipstick", "perfume", "cream", "handbag", "purse", "jewelry", "earrings", "necklace", "lingerie", "bra"]
        
        self.templates = [
            "{emoji} {brand} {product}\\n\\n{hook}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} وصل: {brand} {product}\\n\\n✨ {benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} تدورين على {product}؟\\n\\n{brand} يجيب لكِ {benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} {brand} {product}\\n\\nقبل: {old_price}\\nالحين: {price}\\n\\n{cta}\\n🔗 {url}",
            "{emoji} جربتِ {brand} {product}؟\\n\\n{benefit} من أول استخدام\\n\\n{price}\\n{cta}\\n🔗 {url}",
            "{emoji} متوفر الآن:\\n{brand} {product}\\n\\n{hook}\\n{price}\\n\\n{cta}\\n🔗 {url}",
            "{emoji} خصم على {product}\\n\\n{brand} الأصلي\\n{price}\\n\\n{cta}\\n🔗 {url}",
            "{emoji} فخامة {brand}\\n\\n{product}\\n{benefit}\\n\\n{price}\\n{cta}\\n🔗 {url}",
        ]
        
        self.hooks_female = ["أناقة تليق بكِ ✨", "طلّة ما تتفوت 💕", "جمال يخطف الأنظار 🌸", "فخامة بأسلوبكِ 💎"]
        self.hooks_male = ["أداء يتكلم 🎯", "جودة تدوم 💪", "فخامة ببساطة 👌", "تميز واضح ⚡"]
        
        self.benefits_female = ["يعطيكِ إشراقة طبيعية", "يناسب ذوقكِ الرفيع", "يبرز أناقتكِ", "راحة تكمل يومكِ"]
        self.benefits_male = ["أداء قوي يتحمل", "جودة تدوم معك", "تصميم عملي وأنيق", "راحة تكمل يومك"]
        
        self.cta_female = ["👉 لا تفوتي - اشتري الحين", "👉 اضغطي واطلبي قبل ينتهي", "👉 حصلي عليه الحين"]
        self.cta_male = ["👉 لا تفوت - اشتري الحين", "👉 اضغط واطلب قبل ينتهي", "👉 احصل عليه الحين"]
        
        self.emojis = ["✨", "🔥", "💎", "⚡", "🌟", "💥", "👌", "🎯"]
    
    def is_female(self, title):
        return any(w in title.lower() for w in self.female_words)
    
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
        
        for j in ["with", "and", "the", "for", "new", "original", "genuine", "official", "men", "women", "man", "woman", "male", "female"]:
            name = re.sub(r'\\b' + j + r'\\b', '', name, flags=re.IGNORECASE)
        
        name = re.sub(r'\\s+', ' ', name).strip()
        words = name.split()
        return ' '.join(words[:6]) if len(words) > 6 else name
    
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
        is_f = self.is_female(title)
        brand = self.get_brand(title) or "ماركة مميزة"
        product = self.clean_name(title, brand)
        
        emoji = random.choice(self.emojis)
        template = random.choice(self.templates)
        
        hook = random.choice(self.hooks_female if is_f else self.hooks_male)
        benefit = random.choice(self.benefits_female if is_f else self.benefits_male)
        cta = random.choice(self.cta_female if is_f else self.cta_male)
        
        price_str, old_str = self.format_price(price, old_price)
        
        post = template.format(
            emoji=emoji, brand=brand, product=product, hook=hook,
            benefit=benefit, price=price_str, old_price=f"{old_str} ريال" if old_str else "",
            cta=cta, url=url
        )
        
        return '\\n'.join([l for l in post.split('\\n') if l.strip()])

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
'''

# Verify and save
import ast
try:
    ast.parse(code)
    print("✅ Syntax OK!")
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")

with open('/mnt/kimi/output/bot_clean.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✅ Saved: bot_clean.py")
print(f"✅ Size: {len(code)} chars")
