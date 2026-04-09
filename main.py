import telebot
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json

TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
bot = telebot.TeleBot(TOKEN)

# ===================================
# 🎯 جمل سعودية خفيفة وقريبة من الناس
# ===================================

OPENING_SENTENCES_BY_CATEGORY = {
    "electronics": {
        "men": [
            "شغل نظيف ولا أرووع 👌",
            "هالجهاز يغنيك عن الباقي 💪",
            "تقنية مره حلوة بسعر طيب 💰",
            "مواصفات خرافية وما يخيب ظنك 🚀",
            "جهاز يليق فيك وفي شغلك 👔",
            "استثمارك الصح هالمرة 📈",
            "اداء قوي وثابت مايتهز ⚡️",
            "من الأخير: جهاز يستاهل التجربة ✅",
            "شيء يفوق التوقع بمراحل 🔥",
            "تكنولوجيا تليق بطموحك 💎",
            "ما راح تندم على هالاختيار 👍",
            "جهاز يسوى كل ريال تنفقه 💵",
            "ترقية ذكية لأدواتك الحين 🆙",
            "شغل احترافي بمعنى الكلمة 🏆",
            "تبي الجودة؟ هذي لك 🎯"
        ],
        "women": [
            "شغل نظيف ولا أرووع 👌",
            "هالجهاز يغنيكِ عن الباقي 💪",
            "تقنية مره حلوة بسعر طيب 💰",
            "مواصفات خرافية وما تخيب ظنكِ 🚀",
            "جهاز يليق فيكِ وفي أناقتكِ 👑",
            "استثماركِ الصح هالمرة 📈",
            "أداء قوي وثابت مايتهز ⚡️",
            "من الأخير: جهاز يستاهل التجربة ✅",
            "شيء يفوق التوقع بمراحل 🔥",
            "تكنولوجيا تليق بطموحكِ 💎",
            "ما راح تندمين على هالاختيار 👍",
            "جهاز يسوى كل ريال تنفقينه 💵",
            "ترقية ذكية لأدواتكِ الحين 🆙",
            "شغل احترافي بمعنى الكلمة 🏆",
            "تبيْن الجودة؟ هذي لكِ 🎯"
        ]
    },
    
    "fashion": {
        "men": [
            "إطلالة تلفت الأنظار من أول نظرة 👀",
            "لبس مره يليق فيك وفي ذوقك 🎩",
            "قطعة أساسية لازم تكون بخزانتك 👕",
            "أناقة بسيطة وشيء فيك الخالق ✨",
            "من الأخير: لبس يستاهل المبلغ 💵",
            "إضافة مره حلوة لإطلالاتك 🌟",
            "خامة ممتازة وتفصيل محترم 👌",
            "هالقطعة تغير مودك للأفضل 🔥",
            "شياكة وراحة بوقت واحد 😎",
            "لا يفوتك هالعرض على هالقطعة ⏰",
            "تلبسه وانت مغتنع 100% ✅",
            "تحدث بصمت.. أناقة وذوق 🎭",
            "قطعة تدل على رجولتك 💪",
            "شيء يفرق عن الباقيين 🥇",
            "إطلالة كاملة بقطعة واحدة 🎯"
        ],
        "women": [
            "إطلالة تلفت الأنظار من أول نظرة 👀",
            "لبس مره يليق فيكِ وفي أناقتكِ 💃",
            "قطعة أساسية لازم تكون بخزانتكِ 👗",
            "أناقة بسيطة وشيء فيكِ الخالق ✨",
            "من الأخير: لبس يستاهل المبلغ 💵",
            "إضافة مره حلوة لإطلالاتكِ 🌟",
            "خامة ممتازة وتفصيل محترم 👌",
            "هالقطعة تغير مودكِ للأفضل 🔥",
            "شياكة وراحة بوقت واحد 💅",
            "لا يفوتكِ هالعرض على هالقطعة ⏰",
            "تلبسينه وانتِ مغتنعة 100% ✅",
            "تحدثي بصمت.. أناقة وذوق 🎭",
            "قطعة تدل على أناقتكِ 👑",
            "شيء يفرقكِ عن الباقين 🥇",
            "إطلالة كاملة بقطعة واحدة 🎯"
        ]
    },
    
    "beauty": {
        "men": [
            "عطر يخلي حضورك له وزن 🌹",
            "ريحة تثبت أنك تفهم بالجودة 👃",
            "منتج مره يعطي نتيجة واضحة ✨",
            "من الأخير: نظافة وأناقة كاملة 🧼",
            "عطر يسألونك عن اسمه لما تمر 🚶‍♂️",
            "اعتناء بسيط يفرق كثير 🧴",
            "شيء يزيد ثقتك بنفسك أضعاف 💪",
            "جودة تبان من أول استخدام 🌟",
            "ريحة تليق في الرجال الأصليين 🎩",
            "منتج يستاهل التجربة بصراحة 💯",
            "عطرك عنوانك.. اختر الأفضل 🏆",
            "نظافة وانتعاش ما له مثيل 🌊",
            "اهتمام بسيط بمظهرك الخارجي 👔",
            "شيء يفرق عن ريحة السوق 🥇",
            "تستاهل هالرفاهية البسيطة 💎"
        ],
        "women": [
            "عطر يخلي حضوركِ له وزن 🌹",
            "ريحة تثبت أنكِ تفهمين بالجودة 👃",
            "منتج مره يعطي نتيجة واضحة ✨",
            "من الأخير: نظافة وأناقة كاملة 🧼",
            "عطر يسألونكِ عن اسمه لما تمري 🚶‍♀️",
            "اعتناء بسيط يفرق كثير 💆‍♀️",
            "شيء يزيد ثقتكِ بنفسكِ أضعاف 💪",
            "جودة تبان من أول استخدام 🌟",
            "ريحة تليق في الأناقة والجمال 👑",
            "منتج يستاهل التجربة بصراحة 💯",
            "عطركِ عنوانكِ.. اختاري الأفضل 🏆",
            "نظافة وانتعاش ما له مثيل 🌊",
            "اهتمام بسيط بمظهركِ الخارجي 💄",
            "شيء يفرق عن ريحة السوق 🥇",
            "تستاهلين هالرفاهية البسيطة 💎"
        ]
    },
    
    "home": {
        "men": [
            "راحة البيت تبدأ من هالمنتج 🏠",
            "شيء يسهل عليك حياتك اليومية 🛋️",
            "جودة تدوم وما تخذلك مع الوقت 🛡️",
            "إضافة مره عملية لبيتك 🔧",
            "بيتك يستاهل هالاهتمام 👌",
            "منتج يريح بالك وبال عائلتك 👨‍👩‍👧‍👦",
            "حل ممتاز لمشاكل البيت اليومية ✅",
            "من الأخير: شيء يستاهل الفلوس 💵",
            "راحة نفسية بمنتج بسيط 😌",
            "أداة موثوقة ومره مفيدة 🏗️",
            "تنظيم وترتيب بأقل جهد 🗄️",
            "بيتك أجمل وأرتب مع هالقطعة ✨",
            "استثمار في راحتك اليومية 📈",
            "شيء تحتاجه كل بيت الآن 🔥",
            "جودة عالية بسعر مره مناسب 💰"
        ],
        "women": [
            "راحة البيت تبدأ من هالمنتج 🏠",
            "شيء يسهل عليكِ حياتكِ اليومية 🛋️",
            "جودة تدوم وما تخذلكِ مع الوقت 🛡️",
            "إضافة مره عملية لبيتكِ 🔧",
            "بيتكِ يستاهل هالاهتمام 👌",
            "منتج يريح بالكِ وبال عائلتكِ 👨‍👩‍👧‍👦",
            "حل ممتاز لمشاكل البيت اليومية ✅",
            "من الأخير: شيء يستاهل الفلوس 💵",
            "راحة نفسية بمنتج بسيط 😌",
            "أداة موثوقة ومره مفيدة 🏗️",
            "تنظيم وترتيب بأقل جهد 🗄️",
            "بيتكِ أجمل وأرتب مع هالقطعة ✨",
            "استثمار في راحتكِ اليومية 📈",
            "شيء تحتاجينه كل بيت الآن 🔥",
            "جودة عالية بسعر مره مناسب 💰"
        ]
    },
    
    "sports": {
        "men": [
            "هالأداة ترفع مستواك الرياضي 📈",
            "جهاز يساعدك توصل لهدفك أسرع 🏃‍♂️",
            "معدات احترافية للي جاد بالرياضة 💪",
            "شيء يحمسك تبدأ اليوم مش بكرا 🔥",
            "جودة تتحمل أقوى التمارين 🏋️‍♂️",
            "استثمار في صحتك ولياقتك ❤️",
            "معدات تليق في المحترفين 🏆",
            "تمرن بذكاء مو بس بقوة 🧠",
            "شيء يفرق معك بالتمرين كثير ✅",
            "لا يفوتك هالعرض على الرياضة ⏰",
            "أداء ممتاز يساعدك تتطور 🚀",
            "معدات موثوقة لكل تحدي 🛡️",
            "تبي نتيجة؟ ابدأ بمعدات صح 🎯",
            "شيء يخلي التمرين أمتع وأفضل 🎽",
            "لياقتك تستاهل هالاهتمام 💎"
        ],
        "women": [
            "هالأداة ترفع مستواكِ الرياضي 📈",
            "جهاز يساعدكِ توصلين لهدفكِ أسرع 🏃‍♀️",
            "معدات احترافية للي جادة بالرياضة 💪",
            "شيء يحمسكِ تبدأين اليوم مش بكرا 🔥",
            "جودة تتحمل أقوى التمارين 🏋️‍♀️",
            "استثمار في صحتكِ ولياقتكِ ❤️",
            "معدات تليق في المحترفات 🏆",
            "تمرني بذكاء مو بس بقوة 🧠",
            "شيء يفرق معكِ بالتمرين كثير ✅",
            "لا يفوتكِ هالعرض على الرياضة ⏰",
            "أداء ممتاز يساعدكِ تتطورين 🚀",
            "معدات موثوقة لكل تحدي 🛡️",
            "تبيْن نتيجة؟ ابدأي بمعدات صح 🎯",
            "شيء يخلي التمرين أمتع وأفضل 🎽",
            "لياقتكِ تستاهل هالاهتمام 💎"
        ]
    },
    
    "general": {
        "men": [
            "عرض ما يتفوت بصراحة 🔥",
            "سعر مره حلو على منتج أحلى 👌",
            "جودة تتكلم عن نفسها 💎",
            "من الأخير: شيء يستاهل الشراء ✅",
            "فرصة لا تعوض استغلها الحين ⏰",
            "منتج مره يسوى الفلوس 💵",
            "توفير حقيقي على شيء أصلي 🏆",
            "لا تفكر كثير.. هذي لك 🎯",
            "شيء يفوق السعر بمراحل 📈",
            "اختار الصح.. اختار هالمنتج 👍",
            "قيمة عالية بسعر ينافس 💰",
            "ما راح تلقى مثله بسعر أحسن 🥇",
            "منتج يستخدمه المحترفين 🏅",
            "تستاهل هالجودة العالية ✨",
            "فرصة ذهبية لمنتج ممتاز ⚡️"
        ],
        "women": [
            "عرض ما يتفوت بصراحة 🔥",
            "سعر مره حلو على منتج أحلى 👌",
            "جودة تتكلم عن نفسها 💎",
            "من الأخير: شيء يستاهل الشراء ✅",
            "فرصة لا تعوضينها استغليها الحين ⏰",
            "منتج مره يسوى الفلوس 💵",
            "توفير حقيقي على شيء أصلي 🏆",
            "لا تفكرين كثير.. هذي لكِ 🎯",
            "شيء يفوق السعر بمراحل 📈",
            "اختاري الصح.. اختاري هالمنتج 👍",
            "قيمة عالية بسعر ينافس 💰",
            "ما راح تلقين مثله بسعر أحسن 🥇",
            "منتج يستخدمه المحترفات 🏅",
            "تستاهلين هالجودة العالية ✨",
            "فرصة ذهبية لمنتج ممتاز ⚡️"
        ]
    }
}

# كلمات مفتاحية لتحديد الفئة
CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "هاتف", "آيفون", "لابتوب", "كمبيوتر", "تابلت", "سماعات", "شاحن", "كيبل", "بطارية", "شاشة", "كاميرا", "تلفزيون", "راوتر", "ساعة ذكية", "إلكتروني"],
    
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "قميص", "تيشيرت", "بنطلون", "جاكيت", "فستان", "تنورة", "حذاء", "شنطة", "حقيبة", "محفظة", "حزام", "كاب", "ملابس", "أزياء"],
    
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "عطر", "عود", "مسك", "كريم", "شامبو", "بلسم", "صابون", "مكياج", "أحمر شفاه", "عناية", "جمال", "تجميل"],
    
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "ثلاجة", "غسالة", "مكنسة", "مكيف", "دفاية", "مروحة", "خلاط", "فرن", "مايكرويف", "غلاية", "كرسي", "طاولة", "سرير", "كنبة", "لمبة", "سجادة", "أثاث", "مطبخ", "منزل"],
    
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "رياضة", "جيم", "لياقة", "تمارين", "سير", "دامبل", "يوغا", "دراجة", "كرة", "جري", "مشي", "تدريب"]
}

def detect_product_category(product_name):
    """تحديد فئة المنتج بناءً على الكلمات المفتاحية"""
    name_lower = product_name.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    
    return "general"

def detect_product_gender(product_name):
    """
    تحدد إذا كان المنتج رجالي أم نسائي أم محايد
    ترجع: 'men' أو 'women' أو 'neutral'
    """
    name_lower = product_name.lower()
    
    # كلمات مؤشرة على المنتجات النسائية
    women_indicators = [
        'women', 'woman', 'ladies', 'lady', 'female', 'feminine',
        'نسائي', 'نساء', 'نسا', 'سيدات', 'سيدة', 'انثى', 'انثوي',
        'dress', 'skirt', 'فستان', 'تنورة', 'بلايز', 'فساتين', 'makeup', 'lipstick'
    ]
    
    # كلمات مؤشرة على المنتجات الرجالية
    men_indicators = [
        'men', 'man', 'male', 'masculine', 'gents', 'gentlemen',
        'رجالي', 'رجال', 'رجل', 'ذكر', 'ذكوري', 'رجولة'
    ]
    
    # كلمات محايدة (للجنسين)
    unisex_indicators = [
        'unisex', 'adult', 'للجنسين', 'للبالغين', 'محايد'
    ]
    
    # التحقق من وجود مؤشرات نسائية
    for indicator in women_indicators:
        if indicator in name_lower:
            return 'women'
    
    # التحقق من وجود مؤشرات رجالية
    for indicator in men_indicators:
        if indicator in name_lower:
            return 'men'
    
    # التحقق من وجود مؤشرات محايدة
    for indicator in unisex_indicators:
        if indicator in name_lower:
            return 'neutral'
    
    # افتراضياً: محايد (سيتم استخدام المذكر للمحايد)
    return 'neutral'

# ===================================
# 🔄 قاموس ترجمة المنتجات
# ===================================

TRANSLATION_DICT = {
    "iphone": "آيفون",
    "samsung": "سامسونج",
    "xiaomi": "شاومي",
    "huawei": "هواوي",
    "airpods": "سماعات آيربودز",
    "earbuds": "سماعات أذن",
    "headphones": "سماعات رأس",
    "laptop": "لابتوب",
    "macbook": "ماك بوك",
    "tablet": "تابلت",
    "ipad": "آيباد",
    "watch": "ساعة ذكية",
    "smartwatch": "ساعة ذكية",
    "charger": "شاحن",
    "cable": "كيبل",
    "power bank": "باور بانك",
    "battery": "بطارية",
    "screen": "شاشة",
    "monitor": "شاشة عرض",
    "keyboard": "كيبورد",
    "mouse": "ماوس",
    "camera": "كاميرا",
    "speaker": "سماعة",
    "tv": "تلفزيون",
    "television": "تلفزيون",
    "router": "راوتر",
    "modem": "مودم",
    "shoes": "حذاء",
    "shoe": "حذاء",
    "sneakers": "حذاء رياضي",
    "boots": "بوت",
    "sandals": "صندل",
    "slippers": "شبشب",
    "t-shirt": "تيشيرت",
    "shirt": "قميص",
    "pants": "بنطلون",
    "jeans": "جينز",
    "jacket": "جاكيت",
    "hoodie": "هودي",
    "dress": "فستان",
    "skirt": "تنورة",
    "socks": "شرابات",
    "cap": "كاب",
    "hat": "قبعة",
    "bag": "شنطة",
    "backpack": "حقيبة ظهر",
    "wallet": "محفظة",
    "perfume": "عطر",
    "fragrance": "عطر",
    "oud": "عود",
    "musk": "مسك",
    "cream": "كريم",
    "lotion": "لوشن",
    "shampoo": "شامبو",
    "conditioner": "بلسم",
    "soap": "صابون",
    "refrigerator": "ثلاجة",
    "fridge": "ثلاجة",
    "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة كهربائية",
    "air conditioner": "مكيف",
    "ac": "مكيف",
    "heater": "دفاية",
    "fan": "مروحة",
    "blender": "خلاط",
    "mixer": "عجانة",
    "oven": "فرن",
    "microwave": "مايكرويف",
    "toaster": "محمصة",
    "kettle": "غلاية",
    "coffee maker": "ماكينة قهوة",
    "iron": "مكواة",
    "hair dryer": "سشوار",
    "chair": "كرسي",
    "table": "طاولة",
    "desk": "مكتب",
    "bed": "سرير",
    "sofa": "كنبة",
    "couch": "كنبة",
    "lamp": "لمبة",
    "light": "إضاءة",
    "mirror": "مرآة",
    "carpet": "سجادة",
    "curtain": "ستارة",
    "treadmill": "سير كهربائي",
    "dumbbell": "دامبل",
    "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة",
    "ball": "كرة",
    "toys": "ألعاب",
    "toy": "لعبة",
    "baby": "أطفال",
    "kids": "أطفال",
    "stroller": "عربة أطفال",
    "car seat": "كرسي سيارة للأطفال",
    "car": "سيارة",
    "tire": "إطار",
    "oil": "زيت",
    "cleaner": "منظف",
    "wireless": "لاسلكي",
    "bluetooth": "بلوتوث",
    "smart": "ذكي",
    "digital": "رقمي",
    "electric": "كهربائي",
    "automatic": "أوتوماتيك",
    "portable": "محمول",
    "professional": "احترافي",
    "original": "أصلي",
    "new": "جديد",
    "pro": "برو",
    "max": "ماكس",
    "plus": "بلس",
    "ultra": "ألترا",
    "mini": "ميني",
    "premium": "بريميوم",
    "deluxe": "ديلوكس",
    "unisex": "للجنسين",
    "adult": "للبالغين",
    "men": "رجالي",
    "women": "نسائي",
    "black": "أسود",
    "white": "أبيض",
    "blue": "أزرق",
    "red": "أحمر",
    "green": "أخضر",
}

def translate_to_arabic(text):
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
    arabic_title = translate_to_arabic(full_title)
    
    words = arabic_title.split()
    seen = set()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    
    result = " ".join(unique_words)
    
    if len(result) > 100:
        for sep in ['،', ',', '-', '|', '/']:
            if sep in result[:100]:
                idx = result.rfind(sep, 50, 100)
                if idx > 0:
                    result = result[:idx]
                    break
        else:
            idx = result.rfind(' ', 80, 100)
            if idx > 0:
                result = result[:idx]
            else:
                result = result[:100]
    
    return result.strip()

# ===================================
# 🔧 دوال المساعدة
# ===================================

def expand_url(url):
    try:
        if any(short in url.lower() for short in ['amzn.to', 'bit.ly', 'tinyurl', 't.co']):
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

# ===================================
# 💰 تنظيف السعر
# ===================================

def clean_price(price_text):
    try:
        nums = re.findall(r'[\d,]+(?:.\d+)?', price_text)
        if nums:
            num_str = nums[0].replace(",", "")
            num_float = float(num_str)
            num_int = int(num_float)
            return f"{num_int} ريال سعودي"
    except:
        pass
    return price_text

# ===================================
# 🖼️ استخراج صورة عالية الجودة
# ===================================

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
        r'_SX\d+_SY\d+_',  
        r'_SX\d+_',        
        r'_SY\d+_',        
        r'_CR\d+,\d+,\d+,\d+_',  
        r'_AC_SL\d+_',      
        r'_SCLZZZZZZZ_',    
        r'_FMwebp_',         
        r'_QL\d+_',          
    ]  
  
    cleaned = url  
    for pattern in patterns_to_remove:  
        cleaned = re.sub(pattern, '_', cleaned)  
  
    if '_SL' not in cleaned and 'amazon' in cleaned:  
        cleaned = re.sub(r'(\.[a-zA-Z]+)(\?.*)?$', r'_SL1500\1', cleaned)  
  
    cleaned = cleaned.split('?')[0]  
  
    return cleaned

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

            discount_percent = None  
            try:  
                if old_price and price:  
                    old_num = float(re.findall(r'[\d,.]+', old_price)[0].replace(",", ""))  
                    new_num = float(re.findall(r'[\d,.]+', price)[0].replace(",", ""))  
                    if old_num > new_num:  
                        discount_percent = int(((old_num - new_num) / old_num) * 100)  
            except:  
                pass  

            if price:  
                arabic_title = smart_arabic_title(full_title)  
                return arabic_title, price, old_price, image, discount_percent  
                  
        except Exception as e:  
            print(f"Attempt {attempt + 1} failed: {e}")  
            continue  
  
    return None

# ===================================
# ✨ التوليد النهائي
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url):
    # تحديد فئة المنتج
    category = detect_product_category(product_name)
    
    # تحديد نوع المنتج (الجنس)
    gender = detect_product_gender(product_name)
    
    # اختيار الجملة المناسبة حسب الفئة والجنس
    if gender == 'neutral':
        gender = 'men'  # افتراضياً للمحايد نستخدم المذكر
    
    category_sentences = OPENING_SENTENCES_BY_CATEGORY.get(category, OPENING_SENTENCES_BY_CATEGORY['general'])
    opening = random.choice(category_sentences[gender])

    clean_current = clean_price(price)  
    clean_old = clean_price(old_price) if old_price else None  
  
    lines = [opening]  
    lines.append("")  
    lines.append(f"🛒 {product_name}")  
    lines.append("")  
  
    if clean_old and discount_percent and discount_percent > 5:  
        lines.append(f"❌ قبل: {clean_old}")  
        lines.append(f"✅ الآن: {clean_current} (وفر {discount_percent}%)")  
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

        product_name, price, old_price, image, discount_percent = product  
        post = generate_post(product_name, price, old_price, discount_percent, original_url)  

        try:  
            if image:  
                bot.send_photo(msg.chat.id, image, caption=post)  
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
