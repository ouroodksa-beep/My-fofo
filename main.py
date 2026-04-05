import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import json

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ---------------- GENERATOR ----------------
class SmartGenerator:
    def __init__(self):
        self.brands = {
            "Apple": ["iphone", "ipad", "macbook", "airpods"],
            "Samsung": ["samsung", "galaxy"],
            "Nike": ["nike", "air max"],
            "Adidas": ["adidas"]
        }

        self.female_keywords = [
            "dress", "skirt", "heels", "makeup", "lipstick",
            "perfume", "bag", "handbag", "women", "girl"
        ]

        self.templates_female = [
            "{emoji} {product} من {brand}\n\n{price} {cta}",
            "{emoji} يا هلا بالأناقة! {product}\n\n{price} {cta}"
        ]

        self.templates_male = [
            "{emoji} {product} من {brand}\n\n{price} {cta}",
            "{emoji} عرض مميز: {product}\n\n{price} {cta}"
        ]

        self.cta_female = ["👉 اشتري الآن", "👉 سارعي بالشراء"]
        self.cta_male = ["👉 اشتري الآن", "👉 سارع بالشراء"]

        self.emojis_female = ["💕", "✨", "🌸"]
        self.emojis_male = ["🔥", "⚡", "💪"]

    def is_female(self, title):
        t = title.lower()
        return any(k in t for k in self.female_keywords)

    def get_brand(self, title):
        t = title.lower()
        for brand, keys in self.brands.items():
            if any(k in t for k in keys):
                return brand
        return "ماركة مميزة"

    def clean_name(self, title, brand):
        name = title
        if brand:
            name = re.sub(rf"\b{re.escape(brand)}\b", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\b(for|with|and|the|new|original)\b", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\s+", " ", name).strip()
        return " ".join(name.split()[:5])

    def format_price(self, price, old_price):
        try:
            nums = re.findall(r"[\d,.]+", price)
            if not nums:
                return price
            new = float(nums[0].replace(",", ""))
        except:
            return price

        try:
            if old_price:
                old_nums = re.findall(r"[\d,.]+", old_price)
                if old_nums:
                    old = float(old_nums[0].replace(",", ""))
                    if old > new:
                        disc = int(((old - new) / old) * 100)
                        return f"~~{int(old):,}~~ → *{int(new):,}* ريال (-{disc}%) 🏷️"
        except:
            pass

        return f"*{int(new):,}* ريال 🏷️"

    def generate(self, title, price, old_price, url):
        is_female = self.is_female(title)
        brand = self.get_brand(title)
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
            emoji=emoji,
            product=product,
            brand=brand,
            price=price_str,
            cta=cta
        )

        return post + f"\n\n🔗 {url}"

# ---------------- FUNCTIONS ----------------
def is_amazon_url(url):
    return re.search(r"(amazon\.[a-z.]+|amzn\.to)", url.lower())

def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

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

def get_image(soup):
    img = soup.select_one("#landingImage")
    if img:
        return img.get("src")
    return None

def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")
        old = soup.select_one(".a-text-price .a-offscreen")

        if not title or not price:
            return None

        return {
            "title": title.text.strip(),
            "price": price.text.strip(),
            "old_price": old.text.strip() if old else None,
            "image": get_image(soup)
        }

    except Exception as e:
        print("Error:", e)
        return None

# ---------------- BOT ----------------
gen = SmartGenerator()

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r"https?://\S+", msg.text)
    if not urls:
        bot.reply_to(msg, "❌ ارسل رابط أمازون")
        return

    for url in urls:
        if not is_amazon_url(url):
            continue

        wait = bot.reply_to(msg, "⏳ جاري جلب المنتج...")
        original_url = url
        expanded = expand_url(url)
        asin = extract_asin(expanded)

        if not asin:
            bot.edit_message_text("❌ لم يتم العثور على ASIN", msg.chat.id, wait.message_id)
            continue

        prod = get_product(asin)
        if not prod:
            bot.edit_message_text("❌ فشل في جلب المنتج", msg.chat.id, wait.message_id)
            continue

        post = gen.generate(prod["title"], prod["price"], prod["old_price"], original_url)

        try:
            if prod["image"]:
                bot.send_photo(msg.chat.id, prod["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print("Send Error:", e)
            bot.send_message(msg.chat.id, post, parse_mode="Markdown")

# ---------------- RUN ----------------
print("🔥 البوت شغال!")
bot.infinity_polling()
