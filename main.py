import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import random
import urllib.parse

TOKEN = "7956075348:AAEYTL28GKeMN7TXyVeGM69iUcfg5ZwOSIk"
bot = telebot.TeleBot(TOKEN)

GROQ_API_KEY = "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"

BRAND_NAMES = {
    "nespresso": "Nespresso", "nescafe": "Nescafé", "nescafé": "Nescafé",
    "dolce gusto": "Dolce Gusto", "delonghi": "DeLonghi", "philips": "Philips",
    "bosch": "Bosch", "samsung": "Samsung", "apple": "Apple", "iphone": "iPhone",
    "ipad": "iPad", "macbook": "MacBook", "airpods": "AirPods", "sony": "Sony",
    "lg": "LG", "dyson": "Dyson", "braun": "Braun", "panasonic": "Panasonic",
    "canon": "Canon", "nikon": "Nikon", "xiaomi": "Xiaomi", "huawei": "Huawei",
    "oppo": "OPPO", "realme": "Realme", "oneplus": "OnePlus", "nokia": "Nokia",
    "lenovo": "Lenovo", "dell": "Dell", "hp": "HP", "asus": "ASUS", "acer": "Acer",
    "msi": "MSI", "logitech": "Logitech", "razer": "Razer", "hyperx": "HyperX",
    "jbl": "JBL", "bose": "Bose", "beats": "Beats", "sennheiser": "Sennheiser",
    "anker": "Anker", "baseus": "Baseus", "ugreen": "UGREEN", "amazon": "Amazon",
    "google": "Google", "microsoft": "Microsoft", "adidas": "Adidas", "nike": "Nike",
    "puma": "Puma", "reebok": "Reebok", "under armour": "Under Armour",
    "new balance": "New Balance", "asics": "ASICS", "timberland": "Timberland",
    "skechers": "Skechers", "crocs": "Crocs", "levis": "Levi's", "wrangler": "Wrangler",
    "tommy hilfiger": "Tommy Hilfiger", "calvin klein": "Calvin Klein", "lacoste": "Lacoste",
    "polo": "Polo", "gucci": "Gucci", "prada": "Prada", "versace": "Versace",
    "dior": "Dior", "chanel": "Chanel", "louis vuitton": "Louis Vuitton",
    "hermes": "Hermès", "burberry": "Burberry", "coach": "Coach",
    "michael kors": "Michael Kors", "fossil": "Fossil", "casio": "Casio",
    "swatch": "Swatch", "rolex": "Rolex", "omega": "Omega", "tissot": "Tissot",
    "seiko": "Seiko", "citizen": "Citizen", "orient": "Orient", "dove": "Dove",
    "nivea": "Nivea", "loreal": "L'Oréal", "pantene": "Pantene",
    "head & shoulders": "Head & Shoulders", "gillette": "Gillette",
    "oral-b": "Oral-B", "colgate": "Colgate", "signal": "Signal",
    "ariel": "Ariel", "tide": "Tide", "persil": "Persil", "downy": "Downy",
    "comfort": "Comfort", "finish": "Finish", "fa": "FA", "rexona": "Rexona",
    "axe": "AXE", "old spice": "Old Spice", "dettol": "Dettol",
    "lifebuoy": "Lifebuoy", "purell": "Purell", "kleenex": "Kleenex",
    "tork": "Tork", "tempo": "Tempo", "whisper": "Whisper", "always": "Always",
    "tampax": "Tampax", "johnson": "Johnson's", "johnsons": "Johnson's",
    "pampers": "Pampers", "huggies": "Huggies", "molfix": "Molfix",
    "fine": "Fine", "marlboro": "Marlboro", "lm": "L&M", "kent": "Kent",
    "davidoff": "Davidoff", "nesquik": "Nesquik", "kitkat": "KitKat",
    "snickers": "Snickers", "mars": "Mars", "twix": "Twix", "bounty": "Bounty",
    "milky way": "Milky Way", "galaxy": "Galaxy", "cadbury": "Cadbury",
    "lindt": "Lindt", "ferrero": "Ferrero", "nutella": "Nutella",
    "kinder": "Kinder", "oreo": "Oreo", "belvita": "Belvita", "lu": "LU",
    "tuc": "TUC", "pringles": "Pringles", "lays": "Lay's", "doritos": "Doritos",
    "cheetos": "Cheetos", "pepsi": "Pepsi", "coca cola": "Coca-Cola",
    "cocacola": "Coca-Cola", "sprite": "Sprite", "fanta": "Fanta",
    "7up": "7UP", "mirinda": "Mirinda", "mountain dew": "Mountain Dew",
    "red bull": "Red Bull", "monster": "Monster", "power horse": "Power Horse",
    "nescafe dolce gusto": "Nescafé Dolce Gusto", "dolcegusto": "Dolce Gusto",
    "vichy": "Vichy", "dercos": "Dercos", "l'oreal": "L'Oréal",
    "l'oréal": "L'Oréal", "loreal paris": "L'Oréal Paris",
    "tresemme": "TRESemmé", "guess": "Guess", "night guess": "Night Guess",
    "swiss arabian": "Swiss Arabian", "kashkha": "Kashkha",
    "ultra doux": "Ultra Doux", "honey treasures": "Honey Treasures",
    "magic retouch": "Magic Retouch", "keratin smooth": "Keratin Smooth",
    "energy": "Energy",
}

# All real examples from the user's channel
EXAMPLES_POOL = [
    "🧼 مطهر زوفلورا\n\n❌ سعره كان 34 ريال\n💥 مع عرض أسبوع التوفير\n\n🔥 تاخذه بـ 12 ريال فقط 😱\n\n🔗 الرابط",
    
    '" 2 لتر "من زيت زيتون السوسن بـ 56 ريال بعد تفعيل عرض اسبوع التوفير .\n\nالرابط\n\nيصـل في السوبر ماركت الـى 75 ريـال ❌',
    
    "🚨 رز الوليمة 5 كيلو 🍚🔥\n\n💥 مع أسبوع التوفير\n🔥 بـ 26 ريال فقط 🤯\n\n❌ بالسوق (العثيم/بندة/كارفور) يوصل 48 ريال\n\n🔗 الرابط\n\n➖ الناس تشتري 5 كيلو بـ 45 ريال \n\n🔥 وإكس زون يجيب لك\n💥 30 كيلو بـ 147 ريال \n\n📉 يعني 5 كيلو بـ 24.5\n\n🎟️ فعـل أسبوع التوفير\n\n🔗 الرابط",
    
    "🚨 صـيدة سكيتشرز 👟🔥\n\n📏 مقاس 39.5 فقط\n\n🖤 الأسود بـ 188 ريال\n❌ كان فوق 466 ريال\n\n⚠️ متبقي حبتين فقط 👀 مين الأسرع؟\n\n🔗 الرابط",
    
    "🚨 شاحن تايب C من Belkin 🔌🔥\n\n🏷️ ماركة معروفة وجودة مضمونة\n\n❌ كان بـ 49 ريال\n💥 الحين بـ 19 ريال فقط 🤯\n\n🔗 الرابط\n\nلحقوووو عليه 😱🔥",
    
    "🫖 إبريق مغربي نحاسي 600 مل\n\n📉 خصم 69%\n💥 بـ 53 ريال فقط\n\n❌ بالسوق يوصل 180 ريال\n\n🔗 الرابط",
    
    "❌ 32 ريال بالسوق\n🔥 16 ريـال في أمازون\n\n🤯 فرق واضح\n\n🧼 دوف 4 حبات\n\n🎟️ فعـل أسبوع التوفير \n\n🔗 الرابط",
    
    "يا بـنااااااات  ✨\n\n👟 العرض على مقاس 40 و 41\n◾️ اللون: أسود\n\n💥 بـ 135 ريال فقط\n\n❌ باقي المقاسات بـ 400 ريال\n\n⚠️ متبقي حبتين فقط\n\n🔗 الرابط\n\n😱",
    
    "4 لتر بـ 15 ريال بس!!\n\n🔥 خصم 50%\nفعـل عـرض التوفير\n\n🛒:\nالرابط\n\n🥞🔥",
    
    "خليط بيتي من كويكر \n\nبالسـوق يصل الى 14 ريـال \nاليوم مع عرض التوفير يصل الى 8 ريـال \n\n\nالرابط\n\n🔥🔥الحقووووووو 🔥🔥",
    
    "من اندر ارمر 👟🔥\n\n❌كان سعره 629 ريال\n✅والحين 258 ريال ! \n\nالعـرض على جميع المقاسـات 🔵\n\nالرابط\n\n❌ارتفع السـعر الى 380 ريـال ❌\n\n😱 🔥😱",
    
    "هذه المجموعة بالسوق توصل تقريبًا لـ 60 ريال 💸  \n\nلكن مع عرض أسبوع التوفير 😳  \n💥 تاخذها كلها بـ 29 ريال فقط!  \n\n🛒 الروابط:  \n\nالرابط 1\nالرابط 2\nالرابط 3\nالرابط 4\n\n⚠️ينتهي عـرض اسبوع التوفير غدا\n\n🔴",
    
    "😱 لاحظ فرق الحجم وفرق السعر  \n\n🔥 الكبير مع عرض التوفير  \nيطلع بـ 16 ريال فقط  \n\nالرابط",
    
    "⚠️حريص جدا اني ابحث عن افضـل سعـر\n\n⌨️ كيبورد ألعاب ميكانيكي YZ98 RGB 🎮  \n\n💸 قيمته 368 ريال  \n🔥 عليه خصـم + كوبون إضافي 35% \n\n😱 وصار بـ 155 ريال \n\nالرابط",
    
    "🍚 الوليمة 5 كيلو 😱🔥  \n\n💸 بـ 26 ريال فقط  \nمع عرض التوفير من أمازون  \n\n📦 تقدر تاخذ حتى 25 كيلو  \n\nالرابط\n\nحاليا في الهايبرات وصل الى 52 ريال",
    
    "سكر محلي ستيفيا 100 كيس\nبخصـم 69% | يا بـلااااااااش . \n\nالرابط\n\n❌انتهى المخزون ❌",
    
    "كلوركس 🚨 5 لتر بـ 11 ريال 😱🔥  \n\n💥 فعّل الكود + عرض التوفير  \n\nالرابط\n\n🚨 مستحييييل تحصل أرخص من كذا 🔥",
    
    "4 لتر بـ 13 ريال فقط!  \n\n💸 بالسوق يوصل إلى 28 ريال  \n\n⚫️ فعّل كودي  \n⚫️ عرض أسبوع التوفير  \n  \nالرابط\n\nحررررررق اسعـار 🔥",
    
    "🚨 اكسترا 10 كيلو   \n\n💸 بـ 26 ريال فقط  \n💥 مع الكود + أسبوع التوفير  \n\nالرابط",
    
    "🚨 صيييييدة  🔥😱  \n\n🧴 فازلين بهذا الحجم بالصيدلية يوصل 30 ريال   \n\n😳 تخيل تاخذه بـ 10 ريال فقط!!  \n\n✔️فعـل كودي + فعل اسبوع التوفير \n\nالرابط",
    
    "🧺 برسيل بالسوق يوصل لـ 75 ريال 💸\n\n💥 جبته لكم بـ 40 ريال فقط!\n\n🔥 فعّل كودي + عرض أسبوع التوفير\n\n⏳ العرض ينتهي بعد ساعتين\n\nالرابط",
    
    "👟 صيييييدة 🔥\n\n💸 كل المقاسات 280 ريال\n😱 مقاس 43 بـ 151 ريال فقط\n\nالرابط",
    
    "🚨 صيييييدة أديداس 🔥😱\n\n👟 جراند كورت لمقاس 44 و 45\n\n💥 خصم 73٪\n\n💸 كانت بـ 493 ريال\n🔥 وصارت بـ 135 ريال\n\n🛒\nالرابط\n\n⏳ المقاسات محدودة",
    
    "🔥 خصم إضافي 30٪ على الشــفرات\n\nإذا أخذت (2) بتدفع 58 ريال فقط ✅\n\nفي صيدلية الدواء\nنفس الكمية بـ 140 ريال ❌💸\n\nالرابط",
    
    "أمازون يقولكم  هوفر منظف السجاد\nكانت بـ 999 ريال 💸❌\n\nونزل عليها خصم + كوبون\nوصارت بـ 340 ريال فقط 🤯🔥\n\nقبل الشــراء ابحث بالمواقع ممكن تحصل سعــر اقــل \n\n\nالرابط",
    
    "🔥🔥 صـيدة  🔥🔥\n\nالشحن من المانيا \nوبالصوره سعرها في فرعهم بالسعودية\n\nالرابط",
    
    "صيدة صيدة صيدة 🤯🔥\n\nلحاف فندقي مبطن 🛌\n\nخصم 62٪+ كوبون 15٪ \nبسعر 32 ريال فقط 😱🤑\n\n الرابط\n\nالتعليقات تضمن لك الجودة 🤩✨",
    
    "لحاف منزلي من قطيفة الصوف \nبخصم 64٪ وبسعر 46 ريال 🔥\n\n الرابط",
]

BRAND_OFFICIAL_SITES = {
    "nike": {
        "search_url": "https://www.nike.com/sa/search?q={query}",
        "price_selectors": [".product-price", ".css-1wmqe5w", ".css-11s11ax", "[data-testid='product-price']"],
        "domain": "nike.com/sa"
    },
    "adidas": {
        "search_url": "https://www.adidas.sa/search?q={query}",
        "price_selectors": [".gl-price-item", ".price-item", "[data-testid='price']", ".sales-price"],
        "domain": "adidas.sa"
    },
    "apple": {
        "search_url": "https://www.apple.com/sa/search/{query}",
        "price_selectors": [".rf-hcard-copy", ".as-price-currentprice", ".typography-caption"],
        "domain": "apple.com/sa"
    },
    "samsung": {
        "search_url": "https://www.samsung.com/sa/search/?searchvalue={query}",
        "price_selectors": [".price", ".prd-price", "[data-price]", ".cost"],
        "domain": "samsung.com/sa"
    },
    "xiaomi": {
        "search_url": "https://www.mi.com/sa/search?keyword={query}",
        "price_selectors": [".price", ".pro-price", ".goods-price"],
        "domain": "mi.com/sa"
    },
    "huawei": {
        "search_url": "https://consumer.huawei.com/sa/search/?q={query}",
        "price_selectors": [".price", ".p-price", ".product-price"],
        "domain": "consumer.huawei.com/sa"
    },
    "philips": {
        "search_url": "https://www.philips.com.sa/c-m/search?q={query}",
        "price_selectors": [".price", ".pdp-price", ".product-price"],
        "domain": "philips.com.sa"
    },
    "lg": {
        "search_url": "https://www.lg.com/sa/search?search={query}",
        "price_selectors": [".price", ".model-price", ".retail-price"],
        "domain": "lg.com/sa"
    },
    "sony": {
        "search_url": "https://www.sony.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".pdp-price"],
        "domain": "sony.com.sa"
    },
    "dyson": {
        "search_url": "https://www.dyson.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".value"],
        "domain": "dyson.sa"
    },
    "bosch": {
        "search_url": "https://www.bosch-home.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "bosch-home.com.sa"
    },
    "puma": {
        "search_url": "https://sa.puma.com/search?q={query}",
        "price_selectors": [".price", ".product-price", ".sales-price"],
        "domain": "sa.puma.com"
    },
    "under armour": {
        "search_url": "https://www.underarmour.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".ua-price"],
        "domain": "underarmour.sa"
    },
    "reebok": {
        "search_url": "https://www.reebok.sa/search?q={query}",
        "price_selectors": [".price", ".gl-price-item", ".sales-price"],
        "domain": "reebok.sa"
    },
    "new balance": {
        "search_url": "https://www.newbalance.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "newbalance.com.sa"
    },
    "asics": {
        "search_url": "https://www.asics.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".sales"],
        "domain": "asics.com/sa"
    },
    "skechers": {
        "search_url": "https://www.skechers.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "skechers.com.sa"
    },
    "crocs": {
        "search_url": "https://www.crocs.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "crocs.sa"
    },
    "levis": {
        "search_url": "https://www.levi.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "levi.com/sa"
    },
    "tommy hilfiger": {
        "search_url": "https://sa.tommy.com/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "sa.tommy.com"
    },
    "calvin klein": {
        "search_url": "https://www.calvinklein.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "calvinklein.sa"
    },
    "lacoste": {
        "search_url": "https://www.lacoste.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "lacoste.com.sa"
    },
    "fossil": {
        "search_url": "https://www.fossil.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "fossil.com/sa"
    },
    "casio": {
        "search_url": "https://www.casio.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "casio.com/sa"
    },
    "guess": {
        "search_url": "https://www.guess.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "guess.com/sa"
    },
    "swiss arabian": {
        "search_url": "https://www.swissarabian.com/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "swissarabian.com"
    },
    "l'oreal": {
        "search_url": "https://www.lorealparis.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "lorealparis.com.sa"
    },
    "gillette": {
        "search_url": "https://www.gillette.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "gillette.sa"
    },
    "oral-b": {
        "search_url": "https://www.oralb.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "oralb.com/sa"
    },
    "colgate": {
        "search_url": "https://www.colgate.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "colgate.com/sa"
    },
    "dettol": {
        "search_url": "https://www.dettol.com.sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "dettol.com.sa"
    },
    "pampers": {
        "search_url": "https://www.pampers.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "pampers.com/sa"
    },
    "huggies": {
        "search_url": "https://www.huggies.com/sa/search?q={query}",
        "price_selectors": [".price", ".product-price", ".amount"],
        "domain": "huggies.com/sa"
    },
}


def protect_brands(text):
    for brand_key, brand_original in sorted(BRAND_NAMES.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(brand_key), re.IGNORECASE)
        text = pattern.sub(brand_original, text)
    return text


def detect_brand_from_title(title):
    title_lower = title.lower()
    for brand_key in sorted(BRAND_NAMES.keys(), key=len, reverse=True):
        if brand_key in title_lower:
            return brand_key
    return None


def get_official_brand_price(brand, product_name):
    if not brand or brand not in BRAND_OFFICIAL_SITES:
        return None, None
    
    brand_info = BRAND_OFFICIAL_SITES[brand]
    search_query = re.sub(r'[^\w\s]', '', product_name)
    search_query = search_query.replace('  ', ' ').strip()
    words = search_query.split()
    if len(words) > 4:
        search_query = ' '.join(words[:4])
    
    encoded_query = urllib.parse.quote(search_query)
    search_url = brand_info["search_url"].format(query=encoded_query)
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]
    
    try:
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        r = requests.get(search_url, headers=headers, timeout=15, allow_redirects=True)
        
        if r.status_code == 200 and len(r.text) > 1000:
            soup = BeautifulSoup(r.text, "html.parser")
            
            for selector in brand_info["price_selectors"]:
                elems = soup.select(selector)
                for elem in elems:
                    text = elem.get_text(strip=True)
                    price_match = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:SAR|ريال|ر\.س|SR)?', text)
                    if price_match:
                        price_num = float(price_match.group(1).replace(',', ''))
                        if price_num > 10:
                            return f"{int(price_num)} ريال", brand_info["domain"]
                    
                    price_match = re.search(r'([\d,]+(?:\.\d+)?)', text)
                    if price_match:
                        price_num = float(price_match.group(1).replace(',', ''))
                        if 10 < price_num < 50000:
                            return f"{int(price_num)} ريال", brand_info["domain"]
            
            page_text = soup.get_text()
            price_patterns = [
                r'(\d[\d,]*)\s*SAR',
                r'(\d[\d,]*)\s*ريال',
                r'(\d[\d,]*)\s*ر\.س',
                r'\b(\d{2,4})\s*\$',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    price_num = float(match.group(1).replace(',', ''))
                    if 10 < price_num < 50000:
                        return f"{int(price_num)} ريال", brand_info["domain"]
    
    except Exception as e:
        print(f"Brand price fetch error for {brand}: {e}")
    
    return None, None


CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


def detect_product_gender(product_name):
    name_lower = product_name.lower()
    women_indicators = ['women', 'woman', 'ladies', 'lady', 'female', 'feminine', 'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي', 'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick', 'شامبو', 'بلسم', 'كريم', 'عطر نسائي', 'عطر للنساء']
    men_indicators = ['men', 'man', 'male', 'masculine', 'gents', 'gentlemen', 'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة', 'عطر رجالي', 'عطر للرجال']
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    return 'neutral'


TRANSLATION_DICT = {
    "laptop": "لابتوب", "tablet": "تابلت", "keyboard": "كيبورد", "mouse": "ماوس",
    "charger": "شاحن", "cable": "كيبل", "power bank": "باور بانك", "battery": "بطارية",
    "screen": "شاشة", "monitor": "شاشة عرض", "camera": "كاميرا", "speaker": "سماعة",
    "watch": "ساعة", "smartwatch": "ساعة ذكية", "headphones": "سماعات رأس",
    "router": "راوتر", "modem": "مودم", "tv": "تلفزيون", "television": "تلفزيون",
    "shoes": "حذاء", "shoe": "حذاء", "sneakers": "حذاء رياضي", "boots": "بوت",
    "sandals": "صندل", "slippers": "شبشب", "t-shirt": "تيشيرت", "shirt": "قميص",
    "pants": "بنطلون", "jeans": "جينز", "jacket": "جاكيت", "hoodie": "هودي",
    "dress": "فستان", "skirt": "تنورة", "socks": "شرابات", "cap": "كاب",
    "hat": "قبعة", "bag": "شنطة", "backpack": "حقيبة ظهر", "wallet": "محفظة",
    "belt": "حزام", "scarf": "وشاح", "gloves": "قفازات",
    "perfume": "عطر", "fragrance": "عطر", "oud": "عود", "musk": "مسك",
    "cream": "كريم", "lotion": "لوشن", "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف", "ac": "مكيف",
    "heater": "دفاية", "fan": "مروحة", "blender": "خلاط", "mixer": "عجانة",
    "oven": "فرن", "microwave": "مايكرويف", "toaster": "محمصة", "kettle": "غلاية",
    "coffee maker": "ماكينة قهوة", "iron": "مكواة", "hair dryer": "سشوار",
    "chair": "كرسي", "table": "طاولة", "desk": "مكتب", "bed": "سرير",
    "sofa": "كنبة", "couch": "كنبة", "lamp": "لمبة", "light": "إضاءة",
    "mirror": "مرآة", "carpet": "سجادة", "curtain": "ستارة",
    "treadmill": "سير كهربائي", "dumbbell": "دامبل", "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة", "ball": "كرة", "toys": "ألعاب", "toy": "لعبة",
    "baby": "أطفال", "kids": "أطفال",
    "wireless": "لاسلكي", "bluetooth": "بلوتوث", "smart": "ذكي", "digital": "رقمي",
    "electric": "كهربائي", "automatic": "أوتوماتيك", "portable": "محمول",
    "professional": "احترافي", "original": "أصلي", "new": "جديد",
    "pro": "برو", "max": "ماكس", "plus": "بلس", "ultra": "ألترا", "mini": "ميني",
    "premium": "بريميوم", "deluxe": "ديلوكس", "unisex": "للجنسين", "adult": "للبالغين",
    "men": "رجالي", "women": "نسائي",
    "black": "أسود", "white": "أبيض", "blue": "أزرق", "red": "أحمر", "green": "أخضر",
    "capsule": "كبسولة", "capsules": "كبسولات", "machine": "ماكينة", "maker": "صانع",
    "espresso": "إسبريسو", "coffee": "قهوة", "cafe": "كافيه",
    "preparation": "تحضير", "prepare": "تحضير",
    "anti": "مضاد", "anti-hair loss": "مضاد تساقط", "hair loss": "تساقط الشعر",
    "stimulating": "منشط", "stimulator": "منشط", "fortifying": "يقوي",
    "serum": "سيروم", "repair": "ترميم", "damaged": "تالف", "split ends": "نهايات متقصفة",
    "protection": "حماية", "heat": "حرارة", "spray": "بخاخ", "fixative": "مثبت",
    "keratin": "كيراتين", "smooth": "سموث", "touch": "ريتاتش", "retouch": "ريتاتش",
    "night": "نايت", "eau de toilette": "أو دي تواليت", "edt": "أو دي تواليت",
    "eau de parfum": "أو دي بارفان", "edp": "أو دي بارفان", "perfume": "عطر",
    "for men": "للرجال", "for women": "للنساء", "unisex": "للجنسين",
    "swiss": "سويسرية", "arabian": "عربية", "oriental": "شرقية",
    "honey": "هوني", "treasures": "تريجرز",
}


def translate_to_arabic(text):
    text = protect_brands(text)
    text_lower = text.lower()
    words = text_lower.split()
    translated_words = []
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            translated_words.append(word)
    result = " ".join(translated_words)
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)
    return result


def smart_arabic_title(full_title):
    full_title = protect_brands(full_title)
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
    result = protect_brands(result)
    if len(result) > 80:
        for sep in ['،', ',', '-', '|', '/']:
            if sep in result[:80]:
                idx = result.rfind(sep, 40, 80)
                if idx > 0:
                    result = result[:idx]
                    break
        else:
            idx = result.rfind(' ', 60, 80)
            if idx > 0:
                result = result[:idx]
            else:
                result = result[:80]
    return result.strip()


def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}
    return emojis.get(category, "📦")


def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl']):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
            return r.url
        return url
    except:
        return url


def is_saudi_amazon(url):
    return "amazon.sa" in url.lower()


def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})', r'([A-Z0-9]{10})/?$',
        r'([A-Z0-9]{10})(?:[/?]|\b)'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            num_float = float(num_str)
            num_int = int(num_float)
            return f"{num_int} ريال"
    except:
        pass
    return price_text


def extract_number(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            return float(nums[0].replace(",", ""))
    except:
        pass
    return 0


def get_high_quality_image(soup):
    image = None
    img_elem = soup.select_one("#landingImage")
    if img_elem:
        image = img_elem.get("data-old-hires")
        if not image:
            dynamic_data = img_elem.get("data-a-dynamic-image")
            if dynamic_data:
                try:
                    img_dict = json.loads(dynamic_data)
                    if img_dict:
                        sorted_urls = sorted(img_dict.keys(), key=lambda x: img_dict[x][0] * img_dict[x][1], reverse=True)
                        image = sorted_urls[0] if sorted_urls else None
                except:
                    pass
        if not image:
            image = img_elem.get("src")
    if not image:
        gallery_img = soup.select_one("#imgTagWrapperId img")
        if gallery_img:
            image = gallery_img.get("data-old-hires") or gallery_img.get("src")
    if not image:
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img:
            image = og_img.get("content")
    if image:
        image = clean_image_url(image)
    return image


def clean_image_url(url):
    if not url:
        return None
    patterns_to_remove = [
        r'_SX\d+_SY\d+_', r'_SX\d+_', r'_SY\d+_',
        r'_CR\d+,\d+,\d+,\d+_', r'_AC_SL\d+_',
        r'_SCLZZZZZZZ_', r'_FMwebp_', r'_QL\d+_',
    ]
    cleaned = url
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '_', cleaned)
    if '_SL' not in cleaned and 'amazon' in cleaned:
        cleaned = re.sub(r'(\.[a-zA-Z]+)(\?.*)?$', r'_SL1500\1', cleaned)
    cleaned = cleaned.split('?')[0]
    return cleaned


def get_seller_info(soup):
    seller_name = None
    seller_rating = None
    seller_selectors = [
        "#merchant-info a",
        "[data-feature-name='merchant'] a",
        ".tabular-buybox-text[tabular-attribute-name='Merchant']",
        "#merchant-info",
    ]
    for selector in seller_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and "Amazon" not in text and len(text) > 2:
                seller_name = text
                break
    rating_elem = soup.select_one("[data-feature-name='merchant'] .a-icon-alt")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        match = re.search(r'(\d+)%', text)
        if match:
            seller_rating = int(match.group(1))
    return seller_name, seller_rating


def extract_coupon_info(text):
    if not text:
        return None, 0
    
    percent = 0
    percent_match = re.search(r'(\d+)%', text)
    if percent_match:
        percent = int(percent_match.group(1))
    
    code = None
    code_match = re.search(r'\b([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z]{4,})\b', text)
    if code_match:
        candidate = code_match.group(1)
        if len(candidate) >= 4 and len(candidate) <= 15 and re.search(r'[A-Z]', candidate):
            code = candidate
    
    if not code and percent > 0:
        code = f"خصم {percent}%"
    
    return code, percent


def get_all_coupons(soup, current_price_num):
    found_coupons = []
    
    selectors = [
        "#couponTextInput",
        "[data-feature-name='coupon']",
        ".couponText",
        "#couponContainer",
        "[id*='coupon']",
        ".promoPriceBlockMessage",
        "[data-a-expander-name='couponSecondaryView']",
        ".couponCheckbox",
        ".savingsPercentage",
        ".a-color-price",
    ]
    
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:
                code, percent = extract_coupon_info(text)
                if code and percent > 0:
                    final_price = int(current_price_num - (current_price_num * percent / 100))
                    found_coupons.append({
                        "code": code,
                        "percent": percent,
                        "final_price": final_price,
                        "text": text
                    })
    
    page_text = soup.get_text()
    
    explicit_patterns = [
        r'(?:apply|clip|use|enter|استخدم|طبّق)\s+([A-Z0-9]{4,12})\s*(?:to save|للحصول|for)\s*(\d+)%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*save\s*(\d+)%',
        r'([A-Z]{3,}\d{2,})\s*[-–]\s*(\d+)%\s*off',
        r'(?:promo\s*code|كود\s*الخصم|كوبون)[\s:]+([A-Z0-9]{4,12})',
    ]
    
    for pattern in explicit_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                code, percent = match[0], int(match[1]) if str(match[1]).isdigit() else 0
            else:
                code, percent = match, 0
            
            if code and len(code) >= 4 and percent > 0:
                final_price = int(current_price_num - (current_price_num * percent / 100))
                found_coupons.append({
                    "code": code.upper(),
                    "percent": percent,
                    "final_price": final_price,
                    "text": f"{code} خصم {percent}%"
                })
    
    seen = {}
    unique = []
    for c in found_coupons:
        key = c["code"].upper()
        if key not in seen:
            seen[key] = True
            unique.append(c)
    
    unique.sort(key=lambda x: x["percent"], reverse=True)
    
    return unique


def get_reviews_info(soup):
    rating = None
    review_count = None
    
    rating_selectors = [
        "[data-hook='average-star-rating'] .a-icon-alt",
        ".a-icon-alt",
        "#acrPopover .a-icon-alt",
        "[data-hook='rating-out-of-text']"
    ]
    for selector in rating_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            match = re.search(r'(\d+\.?\d*)\s*out of\s*5', text)
            if match:
                rating = float(match.group(1))
                break
            match = re.search(r'(\d+\.?\d*)', text)
            if match and float(match.group(1)) <= 5:
                rating = float(match.group(1))
                break
    
    review_selectors = [
        "[data-hook='total-review-count']",
        "#acrCustomerReviewText",
        "a[href*='#customerReviews']",
        "[data-hook='see-all-reviews-link-foot']"
    ]
    for selector in review_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            match = re.search(r'(\d[\d,]*)', text)
            if match:
                review_count = match.group(1).replace(",", "")
                break
    
    return rating, review_count


def get_list_price(soup):
    list_price = None
    
    list_selectors = [
        ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
        ".a-price.a-text-price .a-offscreen",
        ".basisPrice .a-offscreen",
        "#listPrice",
        ".a-price[data-a-color='secondary'] .a-offscreen",
        "[data-a-color='secondary'] .a-offscreen"
    ]
    
    for selector in list_selectors:
        elem = soup.select_one(selector)
        if elem and elem.text:
            text = elem.text.strip()
            if any(c.isdigit() for c in text):
                list_price = text
                break
    
    if not list_price:
        typical_selectors = [
            "#typicalPrice",
            ".a-price[data-a-color='tertiary'] .a-offscreen",
            "[data-a-color='tertiary'] .a-offscreen"
        ]
        for selector in typical_selectors:
            elem = soup.select_one(selector)
            if elem and elem.text:
                text = elem.text.strip()
                if any(c.isdigit() for c in text):
                    list_price = text
                    break
    
    return list_price


def get_discount_percentage(soup, current_price, list_price):
    current_num = extract_number(current_price)
    list_num = extract_number(list_price) if list_price else 0
    
    if list_num > current_num and list_num > 0:
        discount = int(((list_num - current_num) / list_num) * 100)
        return discount
    return 0


def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    
    for attempt, ua in enumerate(user_agents):
        try:
            if attempt > 0:
                time.sleep(2)
            headers = {
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
            }
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code != 200 or len(r.text) < 5000:
                continue
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            title_elem = soup.select_one("#productTitle")
            if not title_elem:
                continue
            full_title = title_elem.text.strip()
            
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
            
            list_price = get_list_price(soup)
            discount_percent = get_discount_percentage(soup, price, list_price)
            
            old_price = None
            old_selectors = [
                ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
                ".a-price.a-text-price .a-offscreen",
                ".basisPrice .a-offscreen",
            ]
            for selector in old_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    text = elem.text.strip()
                    if text != price and any(c.isdigit() for c in text):
                        old_price = text
                        break
            
            image = get_high_quality_image(soup)
            seller_name, seller_rating = get_seller_info(soup)
            product_rating, review_count = get_reviews_info(soup)
            
            current_price_num = extract_number(price) if price else 0
            all_coupons = get_all_coupons(soup, current_price_num)
            
            detected_brand = detect_brand_from_title(full_title)
            official_price, official_domain = None, None
            if detected_brand:
                official_price, official_domain = get_official_brand_price(detected_brand, full_title)
            
            if price:
                arabic_title = smart_arabic_title(full_title)
                return {
                    "name": arabic_title,
                    "price": price,
                    "old_price": old_price,
                    "list_price": list_price,
                    "discount_percent": discount_percent,
                    "image": image,
                    "seller_name": seller_name,
                    "seller_rating": seller_rating,
                    "product_rating": product_rating,
                    "review_count": review_count,
                    "all_coupons": all_coupons,
                    "current_price_num": current_price_num,
                    "detected_brand": detected_brand,
                    "official_brand_price": official_price,
                    "official_brand_domain": official_domain,
                }
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    return None


def select_random_examples(count=5):
    """Select random examples from the pool"""
    if len(EXAMPLES_POOL) <= count:
        return EXAMPLES_POOL
    return random.sample(EXAMPLES_POOL, count)


def generate_post(product_data, original_url):
    name = product_data["name"]
    price = product_data["price"]
    old_price = product_data["old_price"]
    list_price = product_data["list_price"]
    discount_percent = product_data["discount_percent"]
    all_coupons = product_data["all_coupons"]
    current_price_num = product_data["current_price_num"]
    seller_name = product_data["seller_name"]
    seller_rating = product_data["seller_rating"]
    product_rating = product_data["product_rating"]
    review_count = product_data["review_count"]
    detected_brand = product_data.get("detected_brand")
    official_brand_price = product_data.get("official_brand_price")
    official_brand_domain = product_data.get("official_brand_domain")
    
    category = detect_product_category(name)
    gender = detect_product_gender(name)
    
    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    clean_list = clean_price(list_price) if list_price else None
    old_num = extract_number(old_price) if old_price else 0
    list_num = extract_number(list_price) if list_price else 0
    
    context_parts = []
    
    if clean_old and old_num > current_price_num:
        context_parts.append(f"السعر السابق على أمازون {clean_old} والحالي {clean_current}")
    
    if clean_list and list_num > current_price_num:
        context_parts.append(f"السعر القائم/الأساسي {clean_list}")
    
    if discount_percent > 0:
        context_parts.append(f"نسبة الخصم على أمازون {discount_percent}%")
    
    if official_brand_price and official_brand_domain:
        official_num = extract_number(official_brand_price)
        if official_num > current_price_num:
            context_parts.append(f"السعر على موقع البراند الرسمي ({official_brand_domain}) {official_brand_price}")
            context_parts.append(f"الفرق: توفير {int(official_num - current_price_num)} ريال")
    
    if all_coupons:
        best = all_coupons[0]
        context_parts.append(f"كود {best['code']} خصم {best['percent']}% يصير بـ {best['final_price']} ريال")
        if len(all_coupons) > 1:
            context_parts.append(f"وفيه كوبونات ثانية")
    
    if seller_name and seller_rating and seller_rating >= 90:
        context_parts.append(f"بائع {seller_name} تقييم {seller_rating}%")
    
    if product_rating and review_count:
        context_parts.append(f"تقييم المنتج {product_rating}/5 من {review_count} تقييم")
    elif product_rating:
        context_parts.append(f"تقييم المنتج {product_rating}/5")
    
    context = " | ".join(context_parts)
    
    post = generate_ai_post(
        name, category, gender, context, 
        clean_current, clean_old, clean_list, discount_percent, 
        all_coupons, seller_name, seller_rating, 
        product_rating, review_count, 
        detected_brand, official_brand_price, official_brand_domain,
        original_url
    )
    
    return post


def generate_ai_post(
    product_name, category, gender, context, 
    current_price, old_price, list_price, discount_percent, 
    all_coupons, seller_name, seller_rating, 
    product_rating, review_count,
    detected_brand, official_brand_price, official_brand_domain,
    url
):
    """AI generates post using REAL few-shot examples from user's channel"""
    
    gender_hint = ""
    if gender == "women":
        gender_hint = "المنتج نسائي، وجه الأسلوب للبنات"
    elif gender == "men":
        gender_hint = "المنتج رجالي، وجه الأسلوب للرجال"
    else:
        gender_hint = "المنتج للجنسين"
    
    # Select 5 random real examples
    selected_examples = select_random_examples(5)
    examples_text = "\n\n---\n\n".join([f"مثال {i+1}:\n{ex}" for i, ex in enumerate(selected_examples)])
    
    structured_data = {
        "product_name": product_name,
        "category": category,
        "current_price": current_price,
        "old_price": old_price,
        "list_price": list_price,
        "discount_percent": discount_percent,
        "coupons": all_coupons,
        "seller_name": seller_name,
        "seller_rating": seller_rating,
        "product_rating": product_rating,
        "review_count": review_count,
        "detected_brand": detected_brand,
        "official_brand_price": official_brand_price,
        "official_brand_domain": official_brand_domain,
        "url": url
    }
    
    prompt = f"""أنت كاتب محتوى سعودي خليجي في قناة تليجرام "صيدات وصفقات" للتسويق بالعمولة.

🔹 مهمتك: اكتب منشور تسويقي جديد يقلد **بالضبط** الأسلوب والهيكل والطاقة والإيموجي في الأمثلة التالية. لكن استخدم بيانات المنتج الجديد.

🔹 الأمثلة الحقيقية من القناة (اقرأها كوصف للأسلوب المطلوب):

{examples_text}

---

🔹 بيانات المنتج الجديد:
{json.dumps(structured_data, ensure_ascii=False, indent=2)}

🔹 سياق إضافي: {context}

🔹 {gender_hint}

---

🔹 قواعد صارمة:
1. اكتب المنشور **بنفس الأسلوب والهيكل والطاقة** تماماً مثل الأمثلة أعلاه
2. استخدم **نفس عدد الأسطر** و**نفس توزيع الإيموجي** و**نفس الأسلوب اللغوي**
3. استخدم لهجة سعودية خليجية أصيلة (وش، هاذي، بالله، بتدفع، صارت، يستاهل، فرصة، صفقة، غنيمة، هجمة، صطولة، لحقوووو)
4. مدح الأحرف للتأكيد: صيييييدة، الشــراء، السعــر، اقــل، بـلااااااااش
5. لا نقاط في نهاية الأسطر
6. أسلوب صادم يشد العين فوراً
7. قارن الأسعار داخل صفحة أمازون (السعر القديم vs الجديد)
8. إذا فيه سعر من موقع البراند الرسمي، قارنه بصراحة مع سعر أمازون واذكر الفرق بالريال
9. إذا فيه كوبون، اذكره بوضوح مع السعر بعد الخصم
10. إذا فيه تقييم منتج عالي (>4.5) وعدد تقييمات كبير، اذكره كدليل مصداقية
11. اختتم دائماً برابط + إيموجي سهم/عربة/سلسلة
12. ❌ ممنوع: "ياجدعان", "ياجماعة", "يالله يا شباب", "حياكم", "يالا"
13. ❌ ممنوع تكرار نفس الجملة أو نفس الأسلوب في منشورات مختلفة
14. اكتب منشور واحد فقط بدون أي مقدمة أو شرح
15. كل سطر لازم يكون قصير وقوي وفي إيموجي
16. لو المنتج نسائي، افتتح بـ "يا بـنااااااات" أو "يا بنات"
17. لو فيه مقاسات محدودة، اذكر "متبقي حبتين فقط" أو "المقاسات محدودة"
18. لو فيه كود خصم، اذكر "فعّل كودي" أو "فعّل أسبوع التوفير"
19. لو السعر في السوق أغلى، اذكر "بالسوق يوصل"
20. استخدم عبارات مثل: "الحقوووو", "صدمة", "مستحيل", "فرق واضح", "حرق أسعار"

اكتب المنشور الآن:"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "أنت كاتب محتوى سعودي خليجي في قناة 'صيدات وصفقات'. تكتب منشورات تسويقية قصيرة بأسلوب صادم وحماسي. تقلد الأمثلة المعطاة في الأسلوب والهيكل والطاقة والإيموجي بالضبط. بلهجة سعودية خليجية. كل مرة تكتب منشور مختلف تماماً. ممنوع الأمثلة الجاهزة. ممنوع التكرار."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.88,
            "max_tokens": 300
        }
        
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if r.status_code == 200:
            result = r.json()
            post = result["choices"][0]["message"]["content"].strip()
            
            post = post.replace('"', '').replace("'", "").strip()
            post = re.sub(r'^[ـ\s]+', '', post)
            
            if url not in post:
                post += f"\n\n{url}"
            
            vulgar_calls = ["ياجدعان", "ياجماعه", "ياجماعة", "يالله يا", "حياكم", "يالا", "يالله"]
            for vulgar in vulgar_calls:
                if vulgar in post.lower().replace(" ", ""):
                    return generate_fallback_post(
                        product_name, current_price, old_price, list_price, 
                        discount_percent, all_coupons, detected_brand, 
                        official_brand_price, official_brand_domain, url
                    )
            
            return post
                
    except Exception as e:
        print(f"Groq error: {e}")
    
    return generate_fallback_post(
        product_name, current_price, old_price, list_price, 
        discount_percent, all_coupons, detected_brand, 
        official_brand_price, official_brand_domain, url
    )


def generate_fallback_post(
    name, current_price, old_price, list_price, 
    discount_percent, all_coupons, detected_brand, 
    official_brand_price, official_brand_domain, url
):
    """Fallback post - randomized to match user examples"""
    parts = []
    
    # Random opening matching user examples
    openings = [
        f"🚨 {name} 🔥",
        f"💥 {name} 🤯🔥",
        f"🚨 صيييييدة {detected_brand.upper() if detected_brand else ''} 🔥😱",
        f"👟 صيييييدة 🔥",
        f"🔥🔥 صـيدة 🔥🔥",
        f"صيدة صيدة صيدة 🤯🔥",
        f"🚨 صـيدة {name} 👟🔥",
        f"🫖 {name} 🔥",
        f"🧼 {name}",
        f"🍚 {name} 😱🔥",
        f"⌨️ {name} 🎮",
        f"🧺 {name}",
        f"🚨 {name} 🔌🔥",
        f"🧴 {name}",
        f"🥞 {name} 🔥",
    ]
    parts.append(random.choice(openings))
    
    # Price info matching user style
    price_lines = []
    if official_brand_price and official_brand_domain:
        price_lines.append(f"السعر الاساسي على موقع {official_brand_domain} {official_brand_price}")
    
    if old_price:
        price_lines.append(f"❌ كان بـ {old_price}")
    if list_price and list_price != old_price:
        price_lines.append(f"📊 السعر الأساسي: {list_price}")
    
    price_lines.append(f"💥 الحين بـ {current_price}")
    
    if discount_percent > 0:
        price_lines.append(f"🔥 خصم {discount_percent}%")
    
    parts.append("\n".join(price_lines))
    
    # Coupons
    if all_coupons:
        best = all_coupons[0]
        if best["final_price"] > 0:
            parts.append(f"🎟️ مع كود {best['code']} (خصم {best['percent']}%) يصير بـ {best['final_price']} ريال 🔥")
    
    # Urgency
    urgency = ["⏳ المقاسات محدودة", "⏳ الكمية محدودة", "🔥 العرض ينتهي قريب", "⚠️ متبقي حبتين فقط", "⏳ العرض ينتهي بعد ساعتين"]
    parts.append(random.choice(urgency))
    
    # URL
    parts.append(f"🔗\n{url}")
    
    return "\n\n".join(parts)


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        expanded = expand_url(original_url)

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط يجب أن يكون من amazon.sa")
            continue

        asin = extract_asin(expanded)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج")
            continue

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")

        product = get_product(asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل...")
bot.infinity_polling()
