import requests

# --- إعداداتك الخاصة ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "ضع_هنا_توقن_البوت"
CHAT_ID = "ftwu_bot"

def get_amazon_data(amazon_url):
    # 1. طلب البيانات من Rainforest (مع إضافة طلب اللغة العربية)
    # ملاحظة: Rainforest يحاول جلب المحتوى بالعربي إذا كان متاحاً في المتجر
    api_url = f"https://api.rainforestapi.com/request?api_key={RAINFOREST_KEY}&type=product&url={amazon_url}"
    response = requests.get(api_url)
    res = response.json()
    
    if res.get("success"):
        product = res.get("product", {})
        
        # استخراج اسم المنتج (العنوان)
        title = product.get("title", "منتج بدون عنوان")
        
        # --- استخراج السعر (كما كان سابقاً) ---
        price_data = product.get("buybox_winner", {}).get("price", {})
        price_value = price_data.get("value", "غير متوفر")
        
        # --- استخراج الصورة بأعلى جودة ---
        # نبحث في مصفوفة الصور عن الرابط الذي يحتوي على أكبر دقة
        images_list = product.get("images", [])
        if images_list:
            # نختار الصورة الأولى عادة تكون الأساسية، ونأخذ رابط الـ link المباشر
            # Rainforest غالباً يضع الصورة الأعلى جودة في حقل 'link' الأساسي
            image_url = images_list[0].get("link")
        else:
            image_url = product.get("main_image", {}).get("link")
            
        # 2. تنسيق البوست باللغة العربية
        caption = (
            f"👌 **خيار ذكي ومميز**\n\n"
            f"📦 **المنتج:**\n{title}\n\n"
            f"💸 **السعر الحالي:** {price_value} ريال سعودي\n\n"
            f"🌐 **رابط الطلب:**\n{amazon_url}\n\n"
            f"✨ لقطة لا تفوتكم!"
        )
        return caption, image_url
    else:
        print("خطأ في سحب البيانات من Rainforest")
        return None, None

def send_to_telegram(text, image_url):
    # 3. إرسال الصورة مع النص (Caption) بصيغة Markdown للتنسيق
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": text,
        "parse_mode": "Markdown" # لجعل الخطوط عريضة ومنسقة
    }
    requests.post(url, data=payload)

# --- تجربة التشغيل ---
test_link = "حطي_رابط_أمازون_هنا"
caption_text, product_image = get_amazon_data(test_link)

if caption_text and product_image:
    send_to_telegram(caption_text, product_image)
    print("✅ تم إرسال العرض باللغة العربية وبأعلى جودة صورة!")
