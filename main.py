import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import random
import os

TOKEN = "7956075348:AAGhje5ywzVq1ktdWIQ-7KOeisWbje9amf0"
bot = telebot.TeleBot(TOKEN)

GROQ_API_KEY = "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"

# Optional: Set proxy in environment variable
PROXY_URL = os.environ.get("PROXY_URL")


def protect_brands(text):
    return text


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


# ============ expand_url ============
def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl', 'link.amazon']):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)

            if 'link.amazon' in url.lower():
                soup = BeautifulSoup(r.text, "html.parser")
                asin = None
                # 4 طرق لاستخراج ASIN
                detail_rows = soup.find_all('tr')
                for row in detail_rows:
                    cells = row.find_all(['td', 'th'])
                    for i, cell in enumerate(cells):
                        if 'ASIN' in cell.get_text(strip=True) and i + 1 < len(cells):
                            asin = cells[i + 1].get_text(strip=True)
                            if asin and len(asin) >= 9:
                                break
                    if asin:
                        break
                if not asin:
                    page_text = soup.get_text()
                    asin_match = re.search(r'ASIN\s*[:\-]?\s*([A-Z0-9]{9,10})', page_text, re.IGNORECASE)
                    if asin_match:
                        asin = asin_match.group(1)
                if not asin:
                    canonical = soup.select_one('link[rel="canonical"]')
                    if canonical:
                        href = canonical.get('href', '')
                        asin_match = re.search(r'/dp/([A-Z0-9]{9,10})', href)
                        if asin_match:
                            asin = asin_match.group(1)
                if not asin:
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link.get('href', '')
                        asin_match = re.search(r'/dp/([A-Z0-9]{9,10})', href)
                        if asin_match:
                            asin = asin_match.group(1)
                            break
                if asin:
                    return f"https://www.amazon.sa/dp/{asin}"
                return r.url
            return r.url
        return url
    except Exception as e:
        print(f"expand_url error: {e}")
        return url


# ============ get_product ============
def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47",
    ]
    
    for attempt, ua in enumerate(user_agents):
        try:
            delay = (2 ** attempt) + random.uniform(0.5, 2.0)
            if attempt > 0:
                print(f"  Waiting {delay:.1f}s before retry...")
                time.sleep(delay)
            
            session = requests.Session()
            headers = {
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
            }
            
            proxies = {}
            if PROXY_URL:
                proxies = {"http": PROXY_URL, "https": PROXY_URL}
            
            try:
                session.get("https://www.amazon.sa/", headers=headers, timeout=10, proxies=proxies)
                time.sleep(random.uniform(0.5, 1.5))
            except:
                pass
            
            r = session.get(url, headers=headers, timeout=30, proxies=proxies)
            print(f"Attempt {attempt + 1}: Status {r.status_code}, Length {len(r.text)}")
            
            if r.status_code != 200:
                continue
            if len(r.text) < 3000:
                print(f"  Content too short ({len(r.text)} chars)")
                if "captcha" in r.text.lower():
                    print("  CAPTCHA detected!")
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            
            # TITLE
            title = None
            title_elem = soup.select_one("#productTitle")
            if title_elem:
                title = title_elem.text.strip()
            if not title:
                json_ld = soup.select_one('script[type="application/ld+json"]')
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        if isinstance(data, dict):
                            title = data.get('name', '')
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and item.get('@type') == 'Product':
                                    title = item.get('name', '')
                                    break
                    except:
                        pass
            if not title:
                print("  Title not found")
                continue
            
            # PRICE (4 methods)
            price = None
            price_selectors = [
                ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
                ".a-price.a-text-price.apexPriceToPay .a-offscreen",
                ".a-price.aok-align-center .a-offscreen",
                ".a-price .a-offscreen",
                "span.a-price span.a-offscreen",
                ".a-price-buy-box .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
                ".a-price-whole",
                ".a-price-current .a-offscreen",
                ".a-price-to-pay .a-offscreen",
            ]
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    text = elem.text.strip()
                    if any(c.isdigit() for c in text):
                        price = text
                        break
            
            if not price:
                json_ld = soup.select_one('script[type="application/ld+json"]')
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        if isinstance(data, dict):
                            offers = data.get('offers', {})
                            if isinstance(offers, dict):
                                price = offers.get('price', '')
                                if price:
                                    price = f"SAR {price}"
                    except:
                        pass
            
            if not price:
                price_match = re.search(r'"displayPrice"\s*:\s*"([^"]+)"', r.text)
                if price_match:
                    price = price_match.group(1)
            
            if not price:
                price_match = re.search(r'"priceAmount"\s*:\s*([\d.]+)', r.text)
                if price_match:
                    price = f"SAR {price_match.group(1)}"
            
            if not price:
                price_match = re.search(r'SAR\s*([\d,]+(?:\.\d+)?)', r.text)
                if price_match:
                    price = f"SAR {price_match.group(1)}"
            
            if not price:
                print("  Price not found")
                continue
            
            # OLD PRICE
            old_price = None
            old_selectors = [
                ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
                ".a-price.a-text-price .a-offscreen",
                ".basisPrice .a-offscreen",
                ".a-price.a-text-price[data-a-strike='true'] .a-offscreen",
                ".a-price[data-a-color='secondary'] .a-offscreen",
            ]
            for selector in old_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    text = elem.text.strip()
                    if text != price and any(c.isdigit() for c in text):
                        old_price = text
                        break
            
            # OTHER DATA
            image = get_high_quality_image(soup)
            seller_name, seller_rating = get_seller_info(soup)
            rating, review_count = get_product_rating(soup)
            stock_info = get_stock_info(soup)
            current_price_num = extract_number(price) if price else 0
            all_coupons = get_all_coupons(soup, current_price_num)
            
            arabic_title = smart_arabic_title(title)
            print(f"  SUCCESS: '{arabic_title[:50]}...' at {price}")
            
            return {
                "name": arabic_title,
                "full_title": title,
                "price": price,
                "old_price": old_price,
                "image": image,
                "seller_name": seller_name,
                "seller_rating": seller_rating,
                "rating": rating,
                "review_count": review_count,
                "stock_info": stock_info,
                "all_coupons": all_coupons,
                "current_price_num": current_price_num,
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    print("  All attempts failed")
    return None


def is_saudi_amazon(url):
    if "link.amazon" in url.lower():
        return True
    return "amazon.sa" in url.lower()


def extract_asin(url):
    if 'link.amazon' in url.lower():
        match = re.search(r'link\.amazon/([A-Za-z0-9]{9,10})', url, re.IGNORECASE)
        if match:
            return match.group(1).upper()

    patterns = [
        r'/dp/([A-Z0-9]{9,10})', r'/gp/product/([A-Z0-9]{9,10})',
        r'/product/([A-Z0-9]{9,10})', r'([A-Z0-9]{9,10})/?$',
        r'([A-Z0-9]{9,10})(?:[/?]|\b)'
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
            if text and len(text) > 2:
                seller_name = text
                break
    rating_elem = soup.select_one("[data-feature-name='merchant'] .a-icon-alt")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        match = re.search(r'(\d+)%', text)
        if match:
            seller_rating = int(match.group(1))
    return seller_name, seller_rating


def get_product_rating(soup):
    rating = None
    review_count = None
    rating_elem = soup.select_one("#acrPopover .a-icon-alt")
    if not rating_elem:
        rating_elem = soup.select_one("[data-hook='rating-out-of-text']")
    if rating_elem:
        text = rating_elem.get_text(strip=True)
        m = re.search(r'([\d.]+)', text)
        if m:
            rating = m.group(1)
    review_elem = soup.select_one("#acrCustomerReviewText")
    if not review_elem:
        review_elem = soup.select_one("[data-hook='total-review-count']")
    if review_elem:
        text = review_elem.get_text(strip=True)
        m = re.search(r'([\d,]+)', text)
        if m:
            review_count = m.group(1).replace(",", "")
    return rating, review_count


def get_stock_info(soup):
    stock_text = None
    selectors = [
        "#availability span",
        ".a-color-price.a-text-bold",
        "#outOfStock",
        "[data-feature-name='availability']",
    ]
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and any(w in text.lower() for w in ['left', 'متبقي', 'stock', 'soon', 'قريباً', 'limited', 'only']):
                stock_text = text
                break
    return stock_text


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
        "#couponTextInput", "[data-feature-name='coupon']", ".couponText",
        "#couponContainer", "[id*='coupon']", ".promoPriceBlockMessage",
        "[data-a-expander-name='couponSecondaryView']", ".couponCheckbox",
        ".savingsPercentage", ".a-color-price",
    ]
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:
                code, percent = extract_coupon_info(text)
                if code and percent > 0:
                    final_price = int(current_price_num - (current_price_num * percent / 100))
                    found_coupons.append({"code": code, "percent": percent, "final_price": final_price, "text": text})
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
                found_coupons.append({"code": code.upper(), "percent": percent, "final_price": final_price, "text": f"{code} خصم {percent}%"})
    seen = {}
    unique = []
    for c in found_coupons:
        key = c["code"].upper()
        if key not in seen:
            seen[key] = True
            unique.append(c)
    unique.sort(key=lambda x: x["percent"], reverse=True)
    return unique


# ============ MAJOR FIX: get_product with JSON-LD, better retries, delays ============
def get_product(asin):
    url = f"https://www.amazon.sa/dp/{asin}"

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47",
    ]

    for attempt, ua in enumerate(user_agents):
        try:
            # Exponential backoff + random delay
            delay = (2 ** attempt) + random.uniform(0.5, 2.0)
            if attempt > 0:
                print(f"  Waiting {delay:.1f}s before retry...")
                time.sleep(delay)

            session = requests.Session()

            headers = {
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
            }

            proxies = {}
            if PROXY_URL:
                proxies = {"http": PROXY_URL, "https": PROXY_URL}

            # Visit homepage first to get cookies
            try:
                session.get("https://www.amazon.sa/", headers=headers, timeout=10, proxies=proxies)
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                print(f"  Homepage visit failed: {e}")

            r = session.get(url, headers=headers, timeout=30, proxies=proxies)

            print(f"Attempt {attempt + 1}: Status {r.status_code}, Length {len(r.text)}")

            if r.status_code != 200:
                print(f"  Non-200 status, skipping...")
                continue

            if len(r.text) < 3000:
                print(f"  Content too short ({len(r.text)} chars), possible block")
                if "captcha" in r.text.lower():
                    print("  CAPTCHA detected!")
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            # ========== TITLE EXTRACTION ==========
            title = None
            title_elem = soup.select_one("#productTitle")
            if title_elem:
                title = title_elem.text.strip()

            # Fallback: JSON-LD
            if not title:
                json_ld = soup.select_one('script[type="application/ld+json"]')
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        if isinstance(data, dict):
                            title = data.get('name', '')
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and item.get('@type') == 'Product':
                                    title = item.get('name', '')
                                    break
                    except:
                        pass

            if not title:
                print("  Title not found")
                continue

            # ========== PRICE EXTRACTION (Multiple methods) ==========
            price = None
            old_price = None

            # Method 1: Standard selectors
            price_selectors = [
                ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
                ".a-price.a-text-price.apexPriceToPay .a-offscreen",
                ".a-price.aok-align-center .a-offscreen",
                ".a-price .a-offscreen",
                "span.a-price span.a-offscreen",
                ".a-price-buy-box .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
                ".a-price-whole",
                ".a-price-current .a-offscreen",
                ".a-price-to-pay .a-offscreen",
            ]
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    text = elem.text.strip()
                    if any(c.isdigit() for c in text):
                        price = text
                        break

            # Method 2: JSON-LD price
            if not price:
                json_ld = soup.select_one('script[type="application/ld+json"]')
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        if isinstance(data, dict):
                            offers = data.get('offers', {})
                            if isinstance(offers, dict):
                                price = offers.get('price', '')
                                if price:
                                    price = f"SAR {price}"
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and item.get('@type') == 'Product':
                                    offers = item.get('offers', {})
                                    if isinstance(offers, dict):
                                        price = offers.get('price', '')
                                        if price:
                                            price = f"SAR {price}"
                                    break
                    except:
                        pass

            # Method 3: Regex from page text
            if not price:
                price_match = re.search(r'"displayPrice"\s*:\s*"([^"]+)"', r.text)
                if price_match:
                    price = price_match.group(1)

            if not price:
                price_match = re.search(r'"priceAmount"\s*:\s*([\d.]+)', r.text)
                if price_match:
                    price = f"SAR {price_match.group(1)}"

            # Method 4: Look for SAR/ريال in page text
            if not price:
                price_match = re.search(r'SAR\s*([\d,]+(?:\.\d+)?)', r.text)
                if price_match:
                    price = f"SAR {price_match.group(1)}"

            if not price:
                print("  Price not found")
                continue

            # Old price extraction
            old_selectors = [
                ".a-price.a-text-price[data-a-color='secondary'] .a-offscreen",
                ".a-price.a-text-price .a-offscreen",
                ".basisPrice .a-offscreen",
                ".a-price.a-text-price[data-a-strike='true'] .a-offscreen",
                ".a-price[data-a-color='secondary'] .a-offscreen",
            ]
            for selector in old_selectors:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    text = elem.text.strip()
                    if text != price and any(c.isdigit() for c in text):
                        old_price = text
                        break

            # ========== OTHER DATA ==========
            image = get_high_quality_image(soup)
            seller_name, seller_rating = get_seller_info(soup)
            rating, review_count = get_product_rating(soup)
            stock_info = get_stock_info(soup)
            current_price_num = extract_number(price) if price else 0
            all_coupons = get_all_coupons(soup, current_price_num)

            arabic_title = smart_arabic_title(title)

            print(f"  SUCCESS: '{arabic_title[:50]}...' at {price}")

            return {
                "name": arabic_title,
                "full_title": title,
                "price": price,
                "old_price": old_price,
                "image": image,
                "seller_name": seller_name,
                "seller_rating": seller_rating,
                "rating": rating,
                "review_count": review_count,
                "stock_info": stock_info,
                "all_coupons": all_coupons,
                "current_price_num": current_price_num,
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    print("  All attempts failed")
    return None


def generate_post(product_data, original_url):
    """Generate full Telegram post WITHOUT headline - using full Amazon link"""
    name = product_data["name"]
    full_title = product_data.get("full_title", name)
    price = product_data["price"]
    old_price = product_data["old_price"]
    all_coupons = product_data["all_coupons"]
    current_price_num = product_data["current_price_num"]
    seller_name = product_data.get("seller_name")
    seller_rating = product_data.get("seller_rating")
    rating = product_data.get("rating")
    review_count = product_data.get("review_count")
    stock_info = product_data.get("stock_info")

    category = detect_product_category(name)
    gender = detect_product_gender(name)
    category_emoji = get_category_emoji(category)

    clean_current = clean_price(price)
    clean_old = clean_price(old_price) if old_price else None
    old_num = extract_number(old_price) if old_price else 0

    discount_pct = 0
    if old_num > current_price_num and old_num > 0:
        discount_pct = int(((old_num - current_price_num) / old_num) * 100)

    asin = extract_asin(original_url)
    if not asin:
        asin_match = re.search(r'/dp/([A-Z0-9]{9,10})', original_url)
        if asin_match:
            asin = asin_match.group(1)
    full_link = f"https://www.amazon.sa/dp/{asin}" if asin else original_url

    parts = []
    parts.append(f"{category_emoji} {name}")

    price_block = []
    if clean_old and old_num > current_price_num:
        price_block.append(f"❌ السعر السابق: {clean_old}")
        if discount_pct > 0:
            price_block.append(f"💥 السعر الآن: {clean_current} (خصم {discount_pct}%)")
        else:
            price_block.append(f"💥 السعر الآن: {clean_current}")
    else:
        price_block.append(f"💰 السعر: {clean_current}")
    parts.append("\n".join(price_block))

    if all_coupons:
        best = all_coupons[0]
        final_after_coupon = best["final_price"]
        coupon_block = []
        coupon_block.append(f"🎟️ كوبون إضافي {best['percent']}% ← يصير بـ {final_after_coupon} ريال فقط! 🔥")
        if len(all_coupons) > 1:
            coupon_block.append("💡 كوبونات إضافية:")
            for c in all_coupons[1:3]:
                coupon_block.append(f"   • {c['code']} — خصم {c['percent']}%")
        parts.append("\n".join(coupon_block))

    parts.append(f"🛒 رابط الشراء:\n{full_link}")

    return "\n\n".join(parts)


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج من أمازون السعودية")
        return

    for original_url in urls:
        print(f"\n{'='*50}")
        print(f"Processing: {original_url}")

        expanded = expand_url(original_url)
        print(f"Expanded: {expanded}")

        if not is_saudi_amazon(expanded):
            bot.reply_to(msg, "❌ الرابط يجب أن يكون من amazon.sa")
            continue

        asin = extract_asin(expanded)
        print(f"ASIN: {asin}")
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج")
            continue

        wait = bot.reply_to(msg, "⏳ جاري تحليل المنتج وتجهيز المنشور...")

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
            print(f"Error sending with image: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


print("🤖 البوت يعمل — صيدات وصفقات 🔥")
bot.infinity_polling()
