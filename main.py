import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ---------------- HEADERS ----------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    }

# ---------------- GENERATOR ----------------
class SmartGenerator:
    def __init__(self):
        self.female_keywords = ["dress", "heels", "makeup", "bag", "perfume"]

        self.templates_female = [
            "{emoji} {product} 💕\n\n{price} {cta}",
            "{emoji} يا هلا بالأناقة! {product}\n\n{price} {cta}",
        ]

        self.templates_male = [
            "{emoji} {product} 🔥\n\n{price} {cta}",
            "{emoji} عرض مميز: {product}\n\n{price} {cta}",
        ]

        self.cta_female = ["👉 سارعي بالشراء", "👉 اشتري الآن"]
        self.cta_male = ["👉 سارع بالشراء", "👉 اشتري الآن"]

        self.emojis_female = ["💕", "✨", "🌸"]
        self.emojis_male = ["🔥", "⚡", "💪"]

    def is_female(self, title):
        t = title.lower()
        return any(k in t for k in self.female_keywords)

    def format_price(self, price):
        try:
            num = float(re.findall(r"[\d,.]+", price)[0].replace(",", ""))
            return f"*{int(num):,}* ريال 🏷️"
        except:
            return price

    def generate(self, title, price, url):
        is_female = self.is_female(title)
        product = " ".join(title.split()[:5])

        if is_female:
            emoji = random.choice(self.emojis_female)
            template = random.choice(self.templates_female)
            cta = random.choice(self.cta_female)
        else:
            emoji = random.choice(self.emojis_male)
            template = random.choice(self.templates_male)
            cta = random.choice(self.cta_male)

        price_str = self.format_price(price)

        post = template.format(
            emoji=emoji,
            product=product,
            price=price_str,
            cta=cta
        )

        return post + f"\n\n🔗 {url}"

# ---------------- FUNCTIONS ----------------
def is_amazon_url(url):
    return re.search(r"(amazon\.[a-z.]+|amzn\.to)", url.lower())

def expand_url(url):
    try:
        r = requests.get(url, headers=get_headers(), allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

def extract_asin(url):
    patterns = [r"/dp/([A-Z0-9]{10})", r"/gp/product/([A-Z0-9]{10})"]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_product(asin):
    domains = ["amazon.sa", "amazon.com"]

    for domain in domains:
        url = f"https://{domain}/dp/{asin}"

        for attempt in range(3):
            try:
                r = requests.get(url, headers=get_headers(), timeout=10)

                if r.status_code != 200:
                    time.sleep(2)
                    continue

                soup = BeautifulSoup(r.text, "html.parser")

                title = soup.select_one("#productTitle")
                price = soup.select_one(".a-price .a-offscreen")

                if title and price:
                    return {
                        "title": title.text.strip(),
                        "price": price.text.strip()
                    }

            except:
                pass

            time.sleep(2)

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

        expanded = expand_url(url)
        asin = extract_asin(expanded)

        if not asin:
            bot.edit_message_text("❌ لم يتم العثور على ASIN", msg.chat.id, wait.message_id)
            continue

        prod = get_product(asin)

        if not prod:
            bot.edit_message_text("❌ فشل في جلب المنتج", msg.chat.id, wait.message_id)
            continue

        post = gen.generate(prod["title"], prod["price"], url)

        bot.send_message(msg.chat.id, post, parse_mode="Markdown")
        bot.delete_message(msg.chat.id, wait.message_id)

# ---------------- RUN ----------------
print("🔥 البوت شغال!")
bot.infinity_polling()
