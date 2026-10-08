import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import os
import html
import json
from flask import Flask, request

TOKEN = "7956075348:AAFetNzy6ECdP8iHgMWbwQIfjSInomOuhBU"
bot = telebot.TeleBot(TOKEN)

# مفتاح Gemini مدمج — لو حابة تخفيه بعدين حطيه في Environment Variables على Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or "AIzaSyAD68JzBWieLXb9kE-7qOg-8p10_EkY518"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
AED_TO_SAR = 3.75 / 3.6725

POPULAR_BRANDS = [
    "Apple", "Samsung", "Sony", "Philips", "Dyson", "Braun", "Tefal", "Moulinex",
    "Pampers", "Nivea", "Dove", "L'Oreal", "Maybelline", "Macvities", "Nadec",
    "Almarai", "Savola", "Tide", "Persil", "Downy", "Nike", "Adidas", "Puma",
    "Gillette", "Clorox", "Fine", "Vaseline", "MOTHERCARE", "U.S. POLO",
    "Real Techniques", "Anker", "Skechers", "Mustela", "Acer", "Lenovo"
]

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "هاتف", "آيفون", "لابتوب", "سماعات", "شاحن", "كيبل", "شاشة", "تلفزيون", "ساعة"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "bag", "backpack", "wallet", "belt", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "حذاء", "شنطة", "ملابس"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "brush", "lipstick", "deodorant", "roll-on", "عطر", "عود", "مسك", "كريم", "لوشن", "شامبو", "بلسم", "صابون", "مزيل عرق", "حلاقة"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "blender", "mixer", "oven", "microwave", "kettle", "coffee maker", "iron", "rice", "milk", "biscuits", "detergent", "ثلاجة", "غسالة", "مكنسة", "مكيف", "خلاط", "فرن", "غلاية", "مطبخ"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "sport", "رياضة", "جيم", "دراجة"]
}


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache"
    }


# ============================================================
# 110+ جملة افتتاحية — جمل كاملة تشد، لهجة سعودية، كل واحدة أسلوب مختلف
# ============================================================
HOOKS = [
    "عرض اليوم وصل والسعر ما يتصور إطلاقاً",
    "لقطة ما تتفوّت أبداً لهذا المنتج المميز",
    "اللي يدور الجودة والسعر مع بعض، مكانه هنا",
    "منتج تستخدمه كل يوم وسعره اليوم خيال",
    "وفرنا لكم شيء يسوى كل ريال تدفعونه",
    "لا تخلون أحد يشتري قبل ما تشوفون السعر",
    "السعر اليوم يتكلم عن نفسه وبقوة عالية",
    "هذي الفرصة اللي كنت تنتظرها من زمان",
    "اليوم سعره أرخص من أي وقت مضى لمنتج كذا",
    "لا تفوتكم هاللقطة قبل لا تخلص الكمية نهائياً",
    "جايينكم اليوم بعرض يستاهل كل ثانية انتظار",
    "شيء تحتاجه بيتك بسعر ما راح تلقاه في مكان ثاني",
    "إذا كنت تدور الجودة بسعر عادل، توقف عند هنا",
    "هذي مو لقطة عادية، هذي صيدة حقيقية للي يفهم",
    "المنتج اللي الكل يسأل عنه وصل أخيراً بسعر ممتاز",
    "اليوم نزل سعره ونزل بقوة تستاهل المتابعة",
    "خليك أول واحد يشوف هالعرض قبل الكل",
    "ما شفت سعر زي كذا من زمان طويل",
    "فرصة تجنن لمنتج تستخدمه في يومك كله",
    "اللقطة اللي تخلي كثيرين يضربون كف بكف ندماً",
    "منتج 5 نجوم وصل بسعر نجمة واحدة بس",
    "المراجعات تتكلم عن جودته والسعر يصرخ بفرقه",
    "لا تكمل يومك قبل لا تشوف فرق السعر بنفسك",
    "اللي سألت عنه من زمان صار بسعر يدعى له",
    "هنا تدفع أقل وتحصل أكثر، جرّب بنفسك وشوف",
    "المنتج الأصلي بسعر التقليد اليوم بس",
    "هالقطعة منتظرة من زمان وسعرها جاك وقتها أخيراً",
    "اكتشفنا لكم شيء يستاهل كل نجمة بالتقييم",
    "لا تقارن أسعار قبل لا تشوف السعر الموجود هنا",
    "فرصتك توفر الفرق كامل وتشتري بعد شي ثاني بيه",
    "من خمس نجوم لسعر نجمة، هالفرق كله لك",
    "هذي اللقطة اللي تجي مرة بالموسم وتمشي",
    "خذها بسعر العرض وارجع لنا بالشكر بعدين",
    "منتج يومي بسعر لا يومي أبداً ولا طبيعي",
    "راح تدور على هالسعر في أماكن ثانية وما تلقاه",
    "تفاصيل المنتج تجنن والسعر يجنن أكثر منها",
    "هاللقطة لمن يعرف يستغل الفرص الصح",
    "وفر الفرق الحين وخذه لبيتك بلا تردد",
    "هالعرض يثبت إن الجودة ما لازم تكون غالية أبداً",
    "الكمية محدودة والسعر أقل من كذا مستحيل ينزل",
    "عرض مؤقت ويختفي بدون أي سابق إنذار",
    "اللي جرّب السعر هذي ما يرجع يدفع كامل ثاني",
    "هالسعر يستاهل إنك توقف كل شي وتشوفه الحين",
    "لا تؤجلها، العروض مثل هذي تروح بسرعة البرق",
    "فرق السعر بين هنا وباقي الأماكن واضح جداً",
    "السعر اليوم غيره بكرا تماماً، لا تنتظر",
    "اللي يعرف قيمة المنتج يعرف قيمة هالسعر",
    "صدقني، هالسعر ما راح تشوفه ثاني قريب",
    "فاجأنا السعر اليوم وقررنا نشاركه وياكم فوراً",
    "عرض وصلنا اليوم خصيصاً لعشاق التوفير الحقيقي",
    "قطعة واحدة تكفي عشان تقتنع إن السعر صح",
    "سعر المنتج اليوم يستاهل إنك ترسله لأهلك",
    "ليش تدفع زيادة والسعر الصح موجود هنا؟",
    "الكثير اشتروه بكامل السعر، والحين دورك توفر",
    "هذي الفرصة اللي تنفع تهديها أو تقتنيها لنفسك",
    "الجودة والسعر في منتج واحد، وهنا مكانه الوحيد",
    "تخفيض اليوم يستاهل إنك تتابعنا من زمان",
    "هالمنتج قيمته أعلى بكثير من سعره الحالي",
    "لي كل بيت سعودي، هالمنتج صار أساسي",
    "شي تشتريه مرة وتستخدمه سنين بسعر هالعرض",
    "لا تجلس تتردد، هالأسعار ما تنتظر أحد",
    "وصلنا خبر يسرّ الخاطر لكل متابعينا اليوم",
    "تجربتك مع هالمنتج راح تخلي تعيد الطلب أكيد",
    "سعر اليوم يليق بمنتج يستاهل كل ريال",
    "عرض حطيناه لكم بعد بحث طويل عن الأفضل",
    "هاللقطة تجي كل فترة، والحين وقتها بالضبط",
    "منتج تلقاه غالي في كل مكان إلا هنا",
    "خصم اليوم يخليك تشتري اثنين بدل وحدة",
    "الفرق اللي بتوفره اليوم يكفي مصروف أسبوع",
    "لقطة اليوم لمن يتابعنا أول بأول، مبروك عليكم",
    "أسعار هالمنتج برا مو طبيعية، شوف الفرق هنا",
    "ما تلقى جودة هذي بسعر هذي بسهولة أبداً",
    "هالعرض هدية لكل واحد يتابعنا من زمان",
    "اليوم منتجك المفضل بسعر أقرب للمناسب",
    "توقعاتنا السعر يرجع يرتفع، فرصتك الحين",
    "كل يوم نزلنا عرض، بس هذي أقوى واحد",
    "منتج يحتاجه أغلب البيوت بسعر يستاهل المشاركة",
    "اقتنصها الحين قبل لا يندم أحد على التأخير",
    "سعر المنتج اليوم أرحم على جيبك بفرق واضح",
    "زمن التوفير الحقيقي وصل، وهالعرض بدايته",
    "هالقطعة تستاهل كل نجمة بتقييمات المشترين",
    "شوف بنفسك وقارن، والقرار الأخير لك طبعاً",
    "لا تحسبها تكلفة، حسبها استثمار بسعر رمزي",
    "هالعرض لمن يبي الجودة بدون ما يدفع زيادة",
    "ليش تنتظر المواسم والتخفيضات موجودة اليوم؟",
    "سعر مناسب لمنتج ما يناسب إلا الجودة العالية",
    "اليوم يومك توفر وتاخذ اللي نفسك فيه",
    "منتج يستاهل إنك توقف تمرير وتقرأ عنه",
    "هذي الصفقة اللي تتكلم عنها مع أصحابك",
    "السعر الحالي ما يعكس جودة المنتج الحقيقية",
    "أحسن وقت تشتري فيه هو اليوم، لا تتردد",
    "فرصة توفر حقيقية مش مجرد كلام إعلاني",
    "اللي فاته عروض قبل، هذي فرصته يعوض",
    "هالمنتج يبي له واحد يعرف قيمته وسعره",
    "اليوم خصم يفرق معك فعلاً مش ريالات بسيطة",
    "لا تقول ما قلنا لك، هالسعر ما يتكرر",
    "جاهزين؟ هالعرض يبي لها قلب قوي وقرار أسرع",
    "من يوم ما نزل ما شفنا له سعر أحلى من كذا",
    "البيت والجيب الاثنين راح يرتاحون بهاللقطة",
    "سعر اليوم يستاهل التجربة حتى لو متردد",
    "هالمنتج غيّر رأي كثيرين بعد ما جربوه",
    "فيه منتجات تشتريها رخيصة وتدفع غالي بعدين",
    "هذي مو، هذي جودة تدوم وسعر واحد يفرح",
    "توفير اليوم بيحسبونه لك بالمئة مو بالريالات",
    "خلك الذكي اللي يشتري بالوقت الصح",
    "سعره قبل ما يوصلنا كان أعلى بفرق واضح",
    "هالعرض وصلنا وقلنا لازم الكل يستفيد منه",
    "اللي دفع كامل السعر يتمنى لو شاف هالبوست قبل",
    "هاللقطة بتخليك تقول: الحمدلله إني متابعهم",
    "جايبين لكم اليوم منتج يستاهل أكثر من بوست",
    "سعر هالمنتج اليوم أجمل شي فيه بصراحة",
]

HOOKS_WITH_BRAND = [
    "عرض اليوم من {brand} يستاهل كل ريال تدفعه",
    "{brand} نزلت سعر منتجها المميز اليوم بقوة",
    "منتج {brand} اللي تدور عليه وصل بسعر أخير",
    "صيدة حقيقية من {brand} ما تتكرر كل يوم",
    "{brand} وصلت بسعر يليق بجودتها المعروفة",
    "فرصة تجنن من {brand} لكل محبي البراند",
    "{brand} اليوم بسعر ما شفته من قبل أبداً",
    "لقطة {brand} اليوم راح تفاجئك بسعرها",
    "عشاق {brand}، هالعرض وصل وما راح يطول",
    "منتج {brand} الأصلي بسعر ما يتخيله أحد",
    "حصرياً لكم، عرض {brand} اللي كثير يدورونه",
    "سعر {brand} اليوم يستاهل إنك تاخذه لنفسك",
]

EMOJIS = ["🔥", "⚡", "🎯", "🛍️", "📣", "✨", "🏷️", "🚨", "💸", "😱", "👀", "🤯"]


def generate_hook(brand=""):
    pool = list(HOOKS)
    if brand:
        pool += [h.format(brand=brand) for h in HOOKS_WITH_BRAND]
    return f"{random.choice(EMOJIS)} <b>{random.choice(pool)}</b>"


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


# ============================================================
# الترجمة — عبارات ثم كلمات، والكلمة غير المعروفة تبقى كما هي
# ============================================================
PHRASE_TRANSLATIONS = {
    "roll on": "مزيل عرق رول", "roll-on": "مزيل عرق رول",
    "body wash": "غسول جسم", "hand wash": "غسول يدين", "face wash": "غسول وجه",
    "shower gel": "جل استحمام", "body lotion": "لوشن جسم",
    "face cream": "كريم وجه", "eye cream": "كريم عيون",
    "hair oil": "زيت شعر", "hair serum": "سيرم شعر",
    "hair dryer": "مجفف شعر", "hair straightener": "مملس شعر",
    "air fryer": "قلاية هوائية", "washing machine": "غسالة ملابس",
    "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف",
    "coffee maker": "صانعة قهوة", "electric kettle": "غلاية كهربائية",
    "power bank": "باور بانك", "smart watch": "ساعة ذكية",
    "wireless earbuds": "سماعات لاسلكية", "wireless headphones": "سماعات رأس لاسلكية",
    "bluetooth speaker": "مكبر صوت بلوتوث", "phone case": "كفر جوال",
    "screen protector": "حماية شاشة", "charging cable": "كيبل شحن",
    "wall charger": "شاحن جداري", "car charger": "شاحن سيارة",
    "gaming mouse": "ماوس قيمنق", "gaming keyboard": "كيبورد قيمنق",
    "baby diapers": "حفاضات أطفال", "baby wipes": "مناديل أطفال",
    "baby lotion": "لوشن أطفال", "baby shampoo": "شامبو أطفال",
    "tooth paste": "معجون أسنان", "tooth brush": "فرشاة أسنان",
    "mouth wash": "غسول فم", "beard oil": "زيت لحية",
    "shaving foam": "رغوة حلاقة", "shaving gel": "جل حلاقة",
    "after shave": "بعد الحلاقة", "body spray": "بخاخ جسم",
    "eau de parfum": "عطر", "eau de toilette": "عطر",
    "liquid detergent": "منظف غسيل سائل", "dish soap": "سائل جلي",
    "floor cleaner": "منظف أرضيات", "glass cleaner": "منظف زجاج",
    "fabric softener": "منعم أقمشة", "stain remover": "مزيل بقع",
    "sports shoes": "حذاء رياضي", "running shoes": "حذاء جري",
    "t shirt": "تيشيرت", "polo shirt": "قميص بولو",
    "winter jacket": "جاكيت شتوي", "summer dress": "فستان صيفي",
    "school bag": "شنطة مدرسة", "travel bag": "شنطة سفر",
    "sun block": "واقي شمس", "makeup remover": "مزيل مكياج",
    "makeup brush": "فرشاة مكياج", "makeup brushes": "فرش مكياج",
    "brush set": "طقم فرش", "lip stick": "أحمر شفاه", "eye liner": "آيلاينر",
    "face mask": "ماسك وجه", "sheet mask": "ماسك ورقي",
    "anti aging": "مضاد للشيخوخة", "anti dandruff": "ضد القشرة",
    "extra virgin olive oil": "زيت زيتون بكر", "olive oil": "زيت زيتون"
}

WORD_TRANSLATIONS = {
    "deodorant": "مزيل عرق", "cream": "كريم", "lotion": "لوشن",
    "shampoo": "شامبو", "conditioner": "بلسم", "soap": "صابون",
    "perfume": "عطر", "fragrance": "عطر", "oud": "عود", "musk": "مسك",
    "makeup": "مكياج", "lipstick": "أحمر شفاه", "gloss": "ملمع شفاه",
    "mascara": "ماسكارا", "blush": "بلاشر", "serum": "سيرم",
    "scrub": "مقشر", "toner": "تونر", "cleanser": "غسول",
    "moisturizer": "مرطب", "sunscreen": "واقي شمس", "gel": "جل",
    "foam": "رغوة", "spray": "بخاخ", "powder": "بودرة",
    "mask": "ماسك", "wipes": "مناديل", "tissues": "مناديل",
    "toothpaste": "معجون أسنان", "toothbrush": "فرشاة أسنان",
    "razor": "ماكينة حلاقة", "trimmer": "ماكينة تشذيب",
    "brush": "فرشاة", "brushes": "فرش", "sponge": "إسفنجة",
    "shirt": "قميص", "tshirt": "تيشيرت", "pants": "بنطلون",
    "jeans": "جينز", "jacket": "جاكيت", "hoodie": "هودي",
    "dress": "فستان", "skirt": "تنورة", "socks": "شرابات",
    "shoes": "حذاء", "sneakers": "سنيكرز", "boots": "بوت",
    "sandals": "صنادل", "slippers": "شباشب", "cap": "كاب",
    "hat": "قبعة", "bag": "شنطة", "backpack": "شنطة ظهر",
    "wallet": "محفظة", "belt": "حزام", "scarf": "شال",
    "sunglasses": "نظارة شمس", "watch": "ساعة", "gloves": "قفازات",
    "phone": "جوال", "iphone": "آيفون", "laptop": "لابتوب",
    "computer": "كمبيوتر", "tablet": "تابلت", "ipad": "آيباد",
    "headphones": "سماعات", "earbuds": "سماعات", "speaker": "مكبر صوت",
    "camera": "كاميرا", "tv": "تلفزيون", "screen": "شاشة",
    "monitor": "شاشة", "keyboard": "كيبورد", "mouse": "ماوس",
    "charger": "شاحن", "cable": "كيبل", "battery": "بطارية",
    "router": "راوتر", "modem": "مودم", "console": "جهاز ألعاب",
    "controller": "يد تحكم", "stand": "ستاند", "holder": "حامل",
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "blender": "خلاط",
    "mixer": "عجانة", "oven": "فرن", "microwave": "مايكرويف",
    "kettle": "غلاية", "iron": "مكواة", "fan": "مروحة",
    "heater": "دفاية", "lamp": "لمبة", "light": "إضاءة",
    "mattress": "مرتبة", "pillow": "مخدة", "blanket": "بطانية",
    "towel": "منشفة", "curtain": "ستارة", "carpet": "سجادة",
    "laundry": "غسيل", "detergent": "منظف غسيل", "softener": "منعم",
    "cleaner": "منظف", "disinfectant": "مطهر", "bleach": "مبيض",
    "rice": "أرز", "milk": "حليب", "biscuits": "بسكويت", "cookies": "كوكيز",
    "chocolate": "شوكولاتة", "candy": "حلويات", "honey": "عسل",
    "coffee": "قهوة", "tea": "شاي", "juice": "عصير", "water": "مياه",
    "oil": "زيت", "sugar": "سكر", "salt": "ملح", "flour": "دقيق",
    "pasta": "مكرونة", "noodles": "نودلز", "sauce": "صلصة",
    "cereal": "كورن فليكس", "oats": "شوفان", "nuts": "مكسرات",
    "treadmill": "سير كهربائي", "dumbbell": "دمبل", "yoga": "يوجا",
    "bicycle": "دراجة", "ball": "كرة", "gym": "جيم",
    "supplement": "مكمل", "protein": "بروتين",
    "set": "طقم", "kit": "طقم",
    "whitening": "مبيض", "nourishing": "مغذي", "moisturizing": "مرطب",
    "hydrating": "مرطب", "refreshing": "منعش",
    "sensitive": "للبشرة الحساسة", "original": "أصلي", "genuine": "أصلي",
    "men": "رجالي", "women": "نسائي", "kids": "أطفال", "baby": "أطفال",
    "sport": "رياضي", "sports": "رياضي",
    "electric": "كهربائي", "digital": "رقمي", "portable": "محمول",
    "wireless": "لاسلكي", "waterproof": "مقاوم للماء", "rechargeable": "قابل للشحن"
}

UNITS_MAP = {
    "ml": "مل", "l": "لتر", "kg": "كيلو", "g": "جرام",
    "pcs": "قطعة", "pc": "قطعة", "pack": "عبوة", "packs": "عبوات",
    "pair": "زوج", "pairs": "أزواج", "set": "طقم", "sets": "أطكم"
}

ARABIC_ADJECTIVES = {
    "مبيض", "مغذي", "مرطب", "منعش", "أصلي", "رجالي", "نسائي",
    "أطفال", "رياضي", "كهربائي", "رقمي", "محمول", "لاسلكي",
    "مقاوم للماء", "قابل للشحن", "للبشرة الحساسة", "ضد القشرة", "مضاد للشيخوخة"
}

KNOWN_WORDS = set(WORD_TRANSLATIONS.keys()) | {
    p.split()[0] for p in PHRASE_TRANSLATIONS.keys()
}

# تحويل الأرقام العربية للإنجليزية — مهم جداً عشان فحص أرقام الـ AI ما يرفضش البوستات
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm_digits(s):
    return s.translate(AR_DIGITS)


def translate_to_arabic(text):
    if not text or not re.search(r'[A-Za-z]', text):
        return text

    clean = re.sub(r"[^\w\s]", " ", text.lower())
    clean = re.sub(r'\s+', ' ', clean).strip()

    for phrase in sorted(PHRASE_TRANSLATIONS.keys(), key=len, reverse=True):
        p = re.sub(r'[^\w\s]', ' ', phrase)
        clean = re.sub(r'\b' + re.escape(p) + r'\b', PHRASE_TRANSLATIONS[phrase], clean)

    translated = []
    for w in clean.split():
        m = re.match(r'^(\d+(?:\.\d+)?)(ml|l|kg|g|pcs|pc|pack|packs|pair|pairs|set|sets)?$', w)
        if m:
            translated.append(m.group(1) + (" " + UNITS_MAP[m.group(2)] if m.group(2) else ""))
            continue
        translated.append(WORD_TRANSLATIONS.get(w, w))

    reordered = []
    i = 0
    while i < len(translated):
        if (i + 1 < len(translated)
                and translated[i] in ARABIC_ADJECTIVES
                and translated[i + 1] not in ARABIC_ADJECTIVES
                and not re.match(r'^\d', translated[i + 1])):
            reordered += [translated[i + 1], translated[i]]
            i += 2
        else:
            reordered.append(translated[i])
            i += 1

    return re.sub(r'\s+', ' ', " ".join(reordered)).strip()


def guess_brand_from_title(title):
    tokens = re.sub(r"[,|()]", " ", title).split()
    brand_tokens = []
    for t in tokens[:3]:
        low = re.sub(r"[^\w']", "", t.lower())
        if not low or low in KNOWN_WORDS or low.isdigit() or not t[0].isalpha() or not t[0].isupper():
            break
        brand_tokens.append(t)
    return " ".join(brand_tokens)


def clean_arabic_title(full_title, found_brand):
    if not full_title:
        return "منتج مميز"

    if found_brand:
        full_title = re.sub(re.escape(found_brand), ' ', full_title, flags=re.IGNORECASE)

    first_part = re.split(r'\s[-–|]\s|,|\|', full_title)[0].strip()

    clean = translate_to_arabic(first_part)
    words = clean.split()[:6]

    bad_endings = ['من', 'عن', 'في', 'على', 'إلى', 'مع', 'أو', 'و', 'ذو', 'ذات', 'for', 'with', 'and', 'of', 'the']
    while words and words[-1].lower() in bad_endings:
        words.pop()

    res = " ".join(words).strip()
    return res if res else "منتج مميز"


# ============================================================
# استخراج البراند
# ============================================================
def extract_brand_from_soup(soup, full_title):
    for brand in POPULAR_BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', full_title, re.IGNORECASE):
            return brand

    try:
        for script in soup.find_all('script', type='application/ld+json'):
            if not script.string:
                continue
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and 'brand' in item:
                    b = item['brand']
                    if isinstance(b, dict):
                        b = b.get('name', '')
                    if isinstance(b, str) and b.strip() and not re.search(r'[\u0600-\u06FF]', b):
                        return b.strip()
    except Exception:
        pass

    for sel in ["#bylineInfo", "#bylineInfo_feature_div a", "a#bylineInfo",
                ".po-brand .po-break-word", "tr.po-brand td.a-span9"]:
        elem = soup.select_one(sel)
        if elem:
            text = elem.get_text(strip=True)
            text = re.sub(r'^(Brand:|الماركة:|العلامة التجارية:|زيارة متجر|Visit the)\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*(Store|متجر)$', '', text, flags=re.IGNORECASE).strip()
            if text and not re.search(r'[\u0600-\u06FF]', text) and len(text) < 40:
                return text

    detail_rows = soup.select(
        "#productOverview_feature_div tr, #detailBullets_feature_div li, "
        "#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr"
    )
    for row in detail_rows:
        row_text = row.get_text(" ", strip=True)
        m = re.search(r'(?:Brand|العلامة التجارية|الماركة)\s*[:\-]?\s*(.+)', row_text, re.IGNORECASE)
        if m:
            candidate = re.split(r'\s{2,}', m.group(1).strip())[0].strip()
            if candidate and len(candidate) < 40 and not re.search(r'[\u0600-\u06FF]', candidate):
                return candidate

    return guess_brand_from_title(full_title)


def extract_coupons_and_vouchers(soup, current_price=0.0):
    info = {"code": None, "voucher_text": None,
            "discount_percent": None, "discount_amount": None}

    all_text = soup.get_text(" ", strip=True)
    IGNORED = {"AMAZON", "PRIME", "SHIPPING", "DETAILS", "TERMS", "CHECKOUT",
               "SELECT", "FREE", "OFFER", "APPLY", "CLICK", "COUPON", "VOUCHER",
               "PROMO", "CODE", "SAVE", "EXTRA", "DISCOUNT"}

    m = re.search(r'(?i:كود|رمز|coupon code|promo code|voucher code|code|كوبون)\s*[:\-]\s*([A-Z0-9]{4,15})\b', all_text)
    if m:
        cand = m.group(1).upper()
        if cand not in IGNORED and re.search(r'[A-Z]', cand):
            info["code"] = cand

    voucher_selectors = [
        "label[for*='checkbox'] span", "#vpcButton", ".vouchers-discount-text",
        "#promoPriceBlockMessage_feature_div", "#coupon_feature_div",
        ".couponBadge", ".couponText", "#promotion_feature_div",
        "[id*='coupon']", "[class*='coupon']",
    ]
    candidates = []
    for sel in voucher_selectors:
        for elem in soup.select(sel):
            t = elem.get_text(" ", strip=True)
            if t:
                candidates.append(t)

    KW = r'(?:كوبون|قسيمة|خصم\s*إضافي|Coupon|Voucher|Extra)'
    percent_patterns = [rf'{KW}\D{{0,40}}?(\d{{1,2}})\s*%', rf'(\d{{1,2}})\s*%\D{{0,40}}?{KW}']
    amount_patterns = [rf'{KW}\D{{0,40}}?(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)',
                       rf'(\d+(?:\.\d+)?)\s*(?:ريال|ر\.س|SAR)\D{{0,40}}?{KW}']

    percents, amounts = set(), set()
    for text in candidates:
        for pat in percent_patterns:
            for mm in re.finditer(pat, text, re.IGNORECASE):
                v = float(mm.group(1))
                if 0 < v <= 90:
                    percents.add(v)
        for pat in amount_patterns:
            for mm in re.finditer(pat, text, re.IGNORECASE):
                v = float(mm.group(1))
                if v > 0:
                    amounts.add(v)

    best_percent = max(percents) if percents else None
    best_amount = max(amounts) if amounts else None

    if best_percent is not None and best_amount is not None and current_price > 0:
        if current_price * best_percent / 100 >= best_amount:
            info["discount_percent"] = best_percent
        else:
            info["discount_amount"] = best_amount
    elif best_percent is not None:
        info["discount_percent"] = best_percent
    elif best_amount is not None:
        info["discount_amount"] = best_amount

    if info["discount_percent"] is not None:
        info["voucher_text"] = f"خصم إضافي {int(info['discount_percent'])}%"
    elif info["discount_amount"] is not None:
        info["voucher_text"] = f"خصم إضافي {info['discount_amount']:.0f} ريال"

    return info


def extract_best_image(soup, asin):
    img_elem = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront") or soup.select_one("#main-image")
    if img_elem:
        dynamic_img = img_elem.get("data-a-dynamic-image")
        if dynamic_img:
            try:
                img_data = json.loads(dynamic_img)
                return max(img_data.keys(), key=lambda k: img_data[k][0] * img_data[k][1])
            except Exception:
                pass
        src = img_elem.get("src", "")
        if src and "blank" not in src.lower():
            return re.sub(r'\._AC_.*_\.', '._AC_SL1500_.', src)
    return None


def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "🧥", "beauty": "💄", "home": "🧼", "sports": "⚡"}
    return emojis.get(category, "🔥")


def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=12, headers=get_headers())
        return r.url
    except Exception:
        return url


def extract_asin(url):
    m = re.search(r'/(?:dp|gp/product|ASIN)/([A-Z0-9]{10})', url, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m_short = re.search(r'/([A-Za-z0-9]{10})(?:[/?]|$)', url)
    if m_short and m_short.group(1).upper() not in ["SAUDI", "AMAZON"]:
        return m_short.group(1).upper()
    return None


def extract_number(price_text):
    if not price_text:
        return 0.0
    nums = re.findall(r'\d[\d,]*(?:\.\d+)?', str(price_text))
    return float(nums[0].replace(",", "")) if nums else 0.0


def extract_current_price(soup, html_content):
    current_price = 0.0

    try:
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, list) and offers:
                        current_price = float(offers[0].get('price', 0))
                    elif isinstance(offers, dict):
                        current_price = float(offers.get('price', 0))
    except Exception:
        pass

    if current_price == 0.0:
        for sel in [".apexPriceToPay .a-offscreen",
                    "#corePrice_feature_div .a-price .a-offscreen",
                    "#corePriceDisplay_desktop_feature_div .a-price-whole",
                    ".a-price .a-offscreen",
                    "#priceblock_ourprice", "#priceblock_dealprice"]:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                val = extract_number(elem.text.strip())
                if val > 0:
                    current_price = val
                    break

    if current_price == 0.0:
        for pat in [r'"priceAmount"\s*:\s*([\d\.]+)', r'"buyingPrice"\s*:\s*([\d\.]+)']:
            match = re.search(pat, html_content, re.IGNORECASE)
            if match:
                val = extract_number(match.group(1))
                if val > 0:
                    current_price = val
                    break

    return current_price


def extract_variants(soup):
    def first_text(selectors):
        for sel in selectors:
            e = soup.select_one(sel)
            if e:
                t = e.get_text(" ", strip=True)
                if t and not re.search(r'select|اختر', t, re.IGNORECASE) and len(t) < 40:
                    return t
        return ""
    color = first_text(["#variation_color_name .selection",
                        "#inline-twister-expanded-dimension-text-color_name"])
    size = first_text(["#native_dropdown_selected_size_name",
                       "#variation_size_name .selection",
                       "#inline-twister-expanded-dimension-text-size_name"])
    return {"color": color, "size": size}


def fetch_product_details(url, asin):
    try:
        resp = requests.get(url, headers=get_headers(), timeout=12)
        html_text = resp.text
        soup = BeautifulSoup(resp.content, "html.parser")

        title_elem = soup.select_one("#productTitle") or soup.select_one("h1")

        if not title_elem or "captcha" in html_text.lower():
            proxy_url = f"https://corsproxy.io/?{url}"
            resp = requests.get(proxy_url, headers=get_headers(), timeout=12)
            html_text = resp.text
            soup = BeautifulSoup(resp.content, "html.parser")
            title_elem = soup.select_one("#productTitle") or soup.select_one("h1")

        if not title_elem:
            return None

        title = title_elem.text.strip()
        price = extract_current_price(soup, html_text)

        brand = extract_brand_from_soup(soup, title)
        title_res = clean_arabic_title(title, brand)

        package_detail = ""
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(ml|l|kg|g|pcs|pack|مل|لتر|كيلو|جرام|قطعة|عبوة)\b', title, re.IGNORECASE)
        if size_match:
            unit = size_match.group(2)
            package_detail = f"{size_match.group(1)} {UNITS_MAP.get(unit.lower(), unit)}"

        coupon = extract_coupons_and_vouchers(soup, price)
        final_price = price
        if price > 0:
            if coupon.get("discount_percent"):
                final_price = round(price * (1 - coupon["discount_percent"] / 100), 2)
            elif coupon.get("discount_amount"):
                final_price = max(round(price - coupon["discount_amount"], 2), 0)

        return {
            "title_clean": title_res,
            "title_raw": title,
            **extract_variants(soup),
            "brand": brand,
            "package": package_detail,
            "price": final_price,
            "price_before_coupon": price if final_price != price else 0.0,
            "category": detect_product_category(title),
            "coupon_code": coupon["code"],
            "voucher_text": coupon["voucher_text"],
            "image_url": extract_best_image(soup, asin),
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


def format_price(price):
    return str(int(price)) if float(price).is_integer() else f"{price:.2f}"


def fetch_uae_price(asin):
    try:
        resp = requests.get(f"https://www.amazon.ae/dp/{asin}", headers=get_headers(), timeout=12)
        if resp.status_code != 200 or "captcha" in resp.text.lower():
            return 0.0
        soup = BeautifulSoup(resp.content, "html.parser")
        if not soup.select_one("#productTitle"):
            return 0.0
        return extract_current_price(soup, resp.text)
    except Exception:
        return 0.0


REF_LABELS = r'(سوبرماركت|السوبرماركت|صيدلية|الصيدلية|محلات|المحلات|الموقع|نون|جرير|بنده|النهدي|الدواء)'


def parse_extras(text):
    t = re.sub(r'https?://\S+', ' ', text)
    t = re.sub(r'سوبر\s+ماركت', 'سوبرماركت', t)
    return [(label, float(p)) for label, p in
            re.findall(REF_LABELS + r'\s*[:=]?\s*(\d+(?:\.\d+)?)', t)]


def parse_note(text):
    t = re.sub(r'https?://\S+', ' ', text)
    t = re.sub(r'سوبر\s+ماركت', 'سوبرماركت', t)
    t = re.sub(REF_LABELS + r'\s*[:=]?\s*\d+(?:\.\d+)?', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


# ============================================================
# برومبت الـ AI — مسوّى احترافي، تنويع كامل، ممنوع التكرار
# ============================================================
AI_SYSTEM_PROMPT = """أنت كاتب محترف لبوستات قناة عروض على تيليجرام جمهورها سعودي. اكتب بلهجة سعودية خليجية طبيعية فقط، بدون أي كلمة مصرية أو شامية.

قواعد صارمة:
1. ممنوع تكتب كلمة "أمازون" أو "السعودية" أو "Amazon" نهائياً. الجمهور يعرف.
2. استخدم فقط الأرقام والمعلومات الموجودة في "المعطيات". ممنوع تخترع سعر أو خصم أو كود أو مقارنة أو مقاس أو لون.
3. اسم البراند يبقى بالإنجليزي كما هو بالضبط ولا يُترجم. اكتبه بخط عريض.
4. اسم المنتج بعربي طبيعي قصير (مثل: شامبو، حفاضات أطفال، طقم أواني). حط العدد أو الحجم بين أقواس مثل ( 400 مل ).
5. الجملة الافتتاحية: جملة كاملة تشد وتخلق فضول، 6 كلمات على الأقل، بخط عريض. ممنوع جمل قصيرة جداً مثل "شوفوا هالعرض". غيّر أسلوبها كل مرة: مرة حماس، مرة فضول، مرة استفهام، مرة نصيحة، مرة تحدي.
6. كل سطر بعد الافتتاحية يكون جملة كاملة فيها معلومة، 4 كلمات على الأقل، ما عدا سطر السعر. ممنوع السطور النصف فارغة.
7. فيه سعر مقارنة (سوبرماركت، صيدلية، موقع آخر)؟ اعرضه بسطر ❌ وسعرنا بسطر ✅ أو 😱. الإمارات: 🇦🇪 عندهم ... ❌ و 🇸🇦 عندنا ... ✅. لا تذكر مقارنة غير موجودة في المعطيات.
8. فيه كود خصم؟ اكتبه بين `` كما هو. فيه قسيمة؟ اكتب: فعّلوا القسيمة من صفحة المنتج قبل الطلب. ما فيه؟ لا تذكر أكواد ولا قسائم.
9. فيه لون أو مقاس في المعطيات؟ اذكره بسطر، ونبّه إن الفرق بين الألوان ممكن يكون في السعر فقط لو الملاحظة قالت كذا.
10. لو فيه "ملاحظة من صاحب القناة" التزم بها وضمّنها بأسلوبك.
11. اكتب الأرقام بالأرقام الإنجليزية (42 مو ٤٢). المدة: من 5 إلى 8 أسطر قصيرة، كل سطر فكرة، إيموجي بسيطة، بدون ختام وبدون شرح وبدون تكرار أي صيغة من الأمثلة حرفياً.
12. لا تكتب الرابط، يضاف تلقائياً.

أمثلة على الروح والأسلوب فقط (منتجات وأرقام من الخيال، لا تنسخ أي صيغة منها حرفياً):

🔥 **اللي دفع كامل السعر قبل أسبوع، لا يكمل قراءة!**
**Lancôme** عطر نسائي فاخر ( 50 مل )
✨ نفس العبوة في البوتيكات تتجاوز 520 ريال
💰 الحين بين يديك بـ 359 ريال بس
🎟️ كود الخصم: `LUXE20`

👶 **يا أمهات، جيبكم راح يرتاح من اليوم!**
**Huggies** حفاضات أطفال مقاس 5 ( 64 حبة )
❌ بالصيدلية قريبة منك بـ 105 ريال
😱 هنا توصلك لباب البيت بـ 72 ريال
👌 جلد طفلك الحساس في أمان تام معها

🎯 **فرق السعر بين الإمارات وعندنا يستاهل إنه يتقال!**
**Logitech** ماوس قيمنق احترافي
🇦🇪 عندهم بـ 219 درهم ( حوالي 224 ريال ) ❌
🇸🇦 عندنا بـ 149 ريال ✅
⚡ استجابة فورية وضمان وكيل معتمد

🛒 **سلة المطبخ الشهرية صارت أرخص بفرق واضح!**
**Tilda** أرز بسمتي ( 10 كيلو )
❌ بالسوبرماركت بـ 98 ريال
✅ الحين بـ 69 ريال وتوفيرك يرجع لجيبك
🍚 الحبة طويلة والريحة تبان من أول ما ينفتح

👟 **اللون الأسود نزل بسعر الثانيين لأول مرة!**
**New Balance** حذاء رياضي نسائي
👟 المقاس 38 | اللون الأسود
💰 بـ 279 ريال بس
⚠️ ثبتوا اللون الأسود بالضبط، باقي الألوان أغلى بـ 30 ريال
"""


def build_facts(product, extras, uae_aed, note=""):
    price = product["price"]
    facts = [f"اسم المنتج بالإنجليزي: {product.get('title_raw', '')}"]
    if product["brand"]:
        facts.append(f"البراند: {product['brand']}")
    if price > 0:
        facts.append(f"السعر الحالي: {format_price(price)} ريال")
    if product.get("price_before_coupon"):
        facts.append(f"السعر قبل القسيمة: {format_price(product['price_before_coupon'])} ريال")
    if product.get("size"):
        facts.append(f"المقاس: {product['size']}")
    if product.get("color"):
        facts.append(f"اللون: {product['color']}")
    if note:
        facts.append(f"ملاحظة من صاحب القناة: {note}")
    if product.get("coupon_code"):
        facts.append(f"كود الخصم: {product['coupon_code']}")
    elif product.get("voucher_text"):
        facts.append(f"فيه قسيمة تتفعّل من صفحة المنتج ({product['voucher_text']}) والسعر أعلاه بعدها")
    for label, p in extras:
        facts.append(f"سعره في {label}: {format_price(p)} ريال")
    if uae_aed > 0 and price > 0:
        uae_sar = round(uae_aed * AED_TO_SAR)
        if uae_sar > price:
            facts.append(f"سعره في أمازون الإمارات: {format_price(uae_aed)} درهم (حوالي {uae_sar} ريال)")
    return "\n".join(facts)


def ai_write_post(facts_text):
    """يكتب البوست عبر Gemini، مع محاولة ثانية لو فشلت الأولى."""
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("PUT_"):
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    for attempt in range(2):
        try:
            body = {
                "system_instruction": {"parts": [{"text": AI_SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": "المعطيات:\n" + facts_text + "\n\nاكتب البوست، ولا تنسَ: افتتاحية جملة كاملة تشد (6 كلمات فأكثر)، أرقام إنجليزية، كل سطر جملة كاملة."}]}],
                "generationConfig": {"temperature": 0.95},
            }
            r = requests.post(url, json=body, headers={"x-goog-api-key": GEMINI_API_KEY}, timeout=30)
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            text = re.sub(r'^```[a-z]*\n|\n```$', '', text)   # نشيل fences لو حطها
            text = norm_digits(text)                             # ٤٢ -> 42 عشان الفحص ما يرفض

            if re.search(r'أمازون|امازون|السعودية|amazon', text, re.IGNORECASE):
                print(f"AI mentioned forbidden word (attempt {attempt+1})")
                continue

            allowed = set(re.findall(r'\d+(?:\.\d+)?', facts_text))
            used = set(re.findall(r'\d+(?:\.\d+)?', text))
            if not used.issubset(allowed):
                print(f"AI used numbers not in facts (attempt {attempt+1}):", used - allowed)
                continue
            return text
        except Exception as e:
            print(f"Gemini error (attempt {attempt+1}): {e}")
    return None


def generate_post(product, original_url):
    """قالب بديل محترم — بيشتغل لو الـ AI فشل نهائياً."""
    title = html.escape(product["title_clean"])
    brand = html.escape(product["brand"])
    package = html.escape(product["package"])
    price = product["price"]

    brand_str = f"<b>{brand}</b> " if brand else ""
    package_str = f" <b>({package})</b>" if package else ""

    lines = [generate_hook(brand), ""]
    lines.append(f"{get_category_emoji(product['category'])} {brand_str}<b>{title}</b>{package_str}")

    if product.get("size") or product.get("color"):
        bits = []
        if product.get("size"):
            bits.append(f"المقاس {product['size']}")
        if product.get("color"):
            bits.append(f"اللون {product['color']}")
        lines.append("🔎 " + " | ".join(bits))

    lines.append("")
    if price > 0:
        if product.get("price_before_coupon"):
            lines.append(f"❌ السعر قبل القسيمة: <s>{format_price(product['price_before_coupon'])} ريال</s>")
        lines.append(f"💰 السعر الحين: <b>{format_price(price)} ريال</b>")

    if product.get("coupon_code"):
        lines.append(f"🎟️ كود الخصم: <code>{html.escape(product['coupon_code'])}</code>")
    elif product.get("voucher_text"):
        lines.append("🎟️ فعّل القسيمة من صفحة المنتج قبل الطلب ✅")

    lines.append("🔗 الرابط تحت 👇")
    lines.append(original_url)
    return "\n".join(lines)


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = (msg.text or "").strip()
    urls = re.findall(r'https?://\S+', text)

    if not urls:
        bot.reply_to(msg, "❌ أرسل رابط المنتج من أمازون السعودية لتحويله لبوست ✨")
        return

    for original_url in urls:
        expanded = expand_url(original_url)
        asin = extract_asin(expanded)

        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رمز المنتج (ASIN)، تأكد من صحة الرابط.")
            continue

        target_url = f"https://www.amazon.sa/dp/{asin}"
        wait = bot.reply_to(msg, "⏳ جاري قراءة بيانات المنتج...")

        product = fetch_product_details(target_url, asin)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، حاول مجدداً بعد قليل.", msg.chat.id, wait.message_id)
            continue

        extras = parse_extras(text)
        note = parse_note(text)
        uae_aed = fetch_uae_price(asin)
        facts_text = build_facts(product, extras, uae_aed, note)

        ai_text = ai_write_post(facts_text)
        if ai_text:
            safe = html.escape(ai_text)
            safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
            safe = re.sub(r'`(.+?)`', r'<code>\1</code>', safe)
            post = safe + "\n\n" + original_url
        else:
            post = generate_post(product, original_url)

        try:
            if product.get("image_url"):
                bot.send_photo(msg.chat.id, product["image_url"], caption=post, parse_mode="HTML")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="HTML")
        except Exception:
            bot.send_message(msg.chat.id, post, parse_mode="HTML")
        finally:
            try:
                bot.delete_message(msg.chat.id, wait.message_id)
            except Exception:
                pass


app = Flask(__name__)


@app.route('/')
def index():
    return "🤖 البوت يعمل", 200


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Unsupported Media Type', 415


WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if WEBHOOK_HOST:
    try:
        bot.remove_webhook()
        bot.set_webhook(url=f"https://{WEBHOOK_HOST}/webhook")
    except Exception as e:
        print(f"Webhook setup failed: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
