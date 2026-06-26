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
    """Translate title to Arabic without length limit"""
    full_title = protect_brands(full_title)
    arabic_title = translate_to_arabic(full_title)
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    result = " ".join(unique_words)
    result = protect_brands(result)
    return result.strip()


def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}
    return emojis.get(category, "📦")


def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co', 'ty.gl', 'link.amazon']):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)

            if 'link.amazon' in url.lower():
                soup = BeautifulSoup(r.text, "html.parser")

                asin = None
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
            if text and any(w in text.lower() for w in ['left', 'متبقي', 'stock', 'soon', 'قريبا\u00d9\u2021', 'limited', 'only']):
                stock_text = text
                break
    return stock_text


def extract_all_offers(soup, current_price_num):
    """Extract ALL offers from page - internal use only"""
    all_offers = []
    page_text = soup.get_text()

    # ===== 1. Promo codes =====
    promo_patterns = [
        r'promo\s*code[:\s]+([A-Z0-9]{3,15})',
        r'enter\s+code\s+([A-Z0-9]{3,15})\s+at\s+checkout',
        r'code[:\s]+([A-Z0-9]{3,15})',
        r'use\s+code\s+([A-Z0-9]{3,15})',
        r'(?:apply|clip|enter|استخدم|طبّق)\s+([A-Z0-9]{4,12})\s*(?:to save|للحصول|for)\s*(\d+)%',
    ]

    for pattern in promo_patterns:
        matches = re.finditer(pattern, page_text, re.IGNORECASE)
        for match in matches:
            code = match.group(1).upper() if match.group(1) else None
            percent = 0
            context = page_text[max(0, match.start()-100):min(len(page_text), match.end()+100)]
            pct_match = re.search(r'(\d+)%', context)
            if pct_match:
                percent = int(pct_match.group(1))

            if code and not any(o.get('code') == code for o in all_offers):
                discount = current_price_num * percent / 100 if percent > 0 else 0
                final = current_price_num - discount
                all_offers.append({
                    "type": "promo_code",
                    "code": code,
                    "percent": percent,
                    "discount_amount": int(discount),
                    "final_price": int(final),
                    "description": f"كود خصم: {code}"
                })

    # ===== 2. Prime Savings =====
    prime_patterns = [
        r'Prime\s*Savings\s*(\d+)%\s*off\s*up\s*to\s*SAR([\d,]+)',
        r'(\d+)%\s*OFF\s*SAR([\d,]+)',
        r'(\d+)%\s*off\s*up\s*to\s*SAR([\d,]+)',
    ]

    for pattern in prime_patterns:
        matches = re.finditer(pattern, page_text, re.IGNORECASE)
        for match in matches:
            percent = int(match.group(1))
            max_discount = extract_number(match.group(2))
            context = page_text[max(0, match.start()-150):min(len(page_text), match.end()+150)]
            card_match = re.search(r'(Rajhi|Alinma|SNB|Riyad|Emirates|Visa|Mastercard)', context, re.IGNORECASE)
            card_name = card_match.group(1) if card_match else "بطاقة ائتمان"

            discount = min(current_price_num * percent / 100, max_discount)
            final = current_price_num - discount

            offer_key = f"prime_{percent}_{card_name}"
            if not any(o.get('key') == offer_key for o in all_offers):
                all_offers.append({
                    "type": "prime_savings",
                    "code": None,
                    "percent": percent,
                    "discount_amount": int(discount),
                    "final_price": int(final),
                    "max_discount": int(max_discount),
                    "card": card_name,
                    "description": f"Prime Savings {percent}% | {card_name}",
                    "key": offer_key
                })

    # ===== 3. Subscribe & Save =====
    sub_save = soup.select_one("[data-feature-name='subscribeAndSave']")
    if sub_save:
        text = sub_save.get_text()
        pct_match = re.search(r'(\d+)%', text)
        if pct_match:
            percent = int(pct_match.group(1))
            discount = current_price_num * percent / 100
            final = current_price_num - discount
            all_offers.append({
                "type": "subscribe_save",
                "code": None,
                "percent": percent,
                "discount_amount": int(discount),
                "final_price": int(final),
                "description": f"اشتراك وتوفير {percent}%"
            })

    # ===== 4. Multi-buy =====
    multi_patterns = [
        r'Save\s*(\d+)%\s*on\s*any\s*(\d+)\s*or\s*more',
        r'(\d+)%\s*off\s*when\s*you\s*buy\s*(\d+)',
    ]
    for pattern in multi_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            percent = int(match.group(1))
            qty = int(match.group(2))
            discount = current_price_num * percent / 100
            final = current_price_num - discount
            all_offers.append({
                "type": "multi_buy",
                "code": None,
                "percent": percent,
                "discount_amount": int(discount),
                "final_price": int(final),
                "min_qty": qty,
                "description": f"اشتري {qty} واحصل على خصم {percent}%"
            })

    # ===== 5. Clip coupons =====
    coupon_selectors = [
        "#couponTextInput", "[data-feature-name='coupon']", ".couponText",
        "#couponContainer", "[id*='coupon']", ".promoPriceBlockMessage",
        "[data-a-expander-name='couponSecondaryView']", ".couponCheckbox",
        ".savingsPercentage", ".a-color-price",
    ]
    for selector in coupon_selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:
                code, percent = extract_coupon_info(text)
                if code and percent > 0:
                    discount = current_price_num * percent / 100
                    final = current_price_num - discount
                    if not any(o.get('code') == code and o.get('type') == 'clip_coupon' for o in all_offers):
                        all_offers.append({
                            "type": "clip_coupon",
                            "code": code,
                            "percent": percent,
                            "discount_amount": int(discount),
                            "final_price": int(final),
                            "description": f"خصم {percent}%"
                        })

    # ===== 6. Explicit patterns =====
    explicit_patterns = [
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
                if not any(o.get('code') == code for o in all_offers):
                    discount = current_price_num * percent / 100
                    final = current_price_num - discount
                    all_offers.append({
                        "type": "promo_code",
                        "code": code.upper(),
                        "percent": percent,
                        "discount_amount": int(discount),
                        "final_price": int(final),
                        "description": f"كود خصم: {code.upper()}"
                    })

    # Remove duplicates and sort by best discount
    seen = {}
    unique = []
    for o in all_offers:
        key = o.get("code") or o.get("key") or o.get("description", "")
        if key not in seen:
            seen[key] = True
            unique.append(o)

    unique.sort(key=lambda x: x["discount_amount"], reverse=True)
    return unique


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
    return extract_all_offers(soup, current_price_num)


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

            image = get_high_quality_image(soup)
            seller_name, seller_rating = get_seller_info(soup)
            rating, review_count = get_product_rating(soup)
            stock_info = get_stock_info(soup)
            current_price_num = extract_number(price) if price else 0

            all_offers = extract_all_offers(soup, current_price_num)
            all_coupons = all_offers

            arabic_title = smart_arabic_title(title)
            print(f"  SUCCESS: '{arabic_title[:50]}...' at {price}")
            print(f"  Found {len(all_offers)} offers")

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
                "all_offers": all_offers,
                "current_price_num": current_price_num,
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    print("  All attempts failed")
    return None


def generate_post(product_data, original_url):
    """Generate post - only shows best price + what offer gives it"""
    name = product_data["name"]
    full_title = product_data.get("full_title", name)
    price = product_data["price"]
    old_price = product_data["old_price"]
    all_offers = product_data.get("all_offers", [])
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

    parts = []
    parts.append(f"{category_emoji} {name}")

    # ===== PRICE BLOCK =====
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

    # ===== BEST OFFER ONLY =====
    if all_offers:
        best = all_offers[0]
        best_final = best.get("final_price", 0)
        best_type = best.get("type", "")
        best_code = best.get("code", "")
        best_percent = best.get("percent", 0)
        best_card = best.get("card", "")

        if best_type == "promo_code" and best_code:
            parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال (بكود `{best_code}` — خصم {best_percent}%)")
        elif best_type == "prime_savings":
            if best_card:
                parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال (Prime Savings {best_percent}% | {best_card})")
            else:
                parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال (Prime Savings {best_percent}%)")
        elif best_type == "subscribe_save":
            parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال (اشتراك وتوفير {best_percent}%)")
        elif best_type == "multi_buy":
            qty = best.get("min_qty", 0)
            parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال (اشتري {qty} ووفر {best_percent}%)")
        elif best_type == "clip_coupon":
            parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال (خصم {best_percent}%)")
        else:
            parts.append(f"🔥 أفضل سعر ممكن: {best_final} ريال")

    # ===== BUY LINK =====
    parts.append(f"🛒 رابط الشراء:\n{original_url}")

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
                bot.send_photo(msg.chat.id, product["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending with image: {e}")
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
                bot.delete_message(msg.chat.id, wait.message_id)
            except Exception as e2:
                print(f"Error sending text: {e2}")
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


# ============ WEBHOOK SERVER ============
from flask import Flask, request

app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route('/')
def index():
    return "🤖 البوت يعمل — صيدات وصفقات 🔥"

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Unsupported Media Type', 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
        print(f"✅ Webhook set to: {WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}")
    else:
        print("⚠️ RENDER_EXTERNAL_HOSTNAME not set, running in local mode...")

    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

if __name__ == '__main__':
    start_webhook()
