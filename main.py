import requests

# --- إعداداتك الخاصة ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA"
CHAT_ID = "ftwu_bot"

def get_amazon_data(amazon_url):
    # 1. طلب البيانات من Rainforest بنفس الطريقة السابقة
    api_url = f"https://api.rainforestapi.com/request?api_key={RAINFOREST_KEY}&type=product&url={amazon_url}"
    response = requests.get(api_url)
    res = response.json()
    
    if res.get("success"):
        product = res.get("product", {})
        
        # استخراج الاسم
        title = product.get("title", "منتج بدون عنوان")
        
        # --- الجزء اللي طلبتي رجوعه (استخراج السعر) ---
        # بيسحب السعر من الـ buybox_winner -> price -> value
        price_data = product.get("buybox_winner", {}).get("price", {})
        price_value = price_data.get("value", "غير متوفر")
        
        # استخراج الصورة
        image_url = product.get("main_image", {}).get("link")
        
        # 2. تنسيق البوست
        caption = (
            f"👌 خيار ذكي\n"
            f"{title}\n\n"
            f"💸 السعر الحالي: {price_value} ريال\n\n"
            f"🌐 الرابط: {amazon_url}"
        )
        return caption, image_url
    else:
        print("خطأ في سحب البيانات من Rainforest")
        return None, None

def send_to_telegram(text, image_url):
    # 3. إرسال الصورة مع النص (Caption)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": text
    }
    requests.post(url, data=payload)

# --- تجربة التشغيل ---
# (تأكدي من استخدام رابط طويل يبدأ بـ amazon.sa)
test_link = "حطي_رابط_أمازون_هنا"
caption_text, product_image = get_amazon_data(test_link)

if caption_text and product_image:
    send_to_telegram(caption_text, product_image)
    print("✅ تم الإرسال بنجاح!")
