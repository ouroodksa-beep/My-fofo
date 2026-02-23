import requests

# --- إعداداتك ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "ضع_التوقن_هنا"
CHAT_ID = "ftwu_bot"

def get_amazon_data(short_url):
    try:
        # 1. فك الرابط المختصر (amzn.to) وتحويله لرابط طويل تلقائياً
        response_expand = requests.head(short_url, allow_redirects=True, timeout=10)
        long_url = response_expand.url
        print(f"تم فك الرابط إلى: {long_url}")
        
        # 2. طلب البيانات من Rainforest باستخدام الرابط الطويل المستخرج
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE'
        }
        res = requests.get('https://api.rainforestapi.com/request', params=params).json()
        
        if res.get("success"):
            product = res.get("product", {})
            title = product.get("title", "بدون عنوان")
            
            # استخراج السعر (كما في طلبك السابق)
            price_value = product.get("buybox_winner", {}).get("price", {}).get("value", "غير متوفر")
            
            # استخراج أعلى جودة صورة
            images = product.get("images", [])
            image_url = images[0].get("link") if images else product.get("main_image", {}).get("link")
            
            # 3. تنسيق البوست بالعربي
            caption = (
                f"👌 **خيار ذكي**\n\n"
                f"{title}\n\n"
                f"💸 **السعر الحالي:** {price_value} ريال\n\n"
                f"🌐 **الرابط:** {short_url}" # نرسل الرابط القصير للمستخدم لأنه أجمل
            )
            return caption, image_url
        else:
            print(f"فشل السحب من Rainforest: {res.get('message')}")
            return None, None
            
    except Exception as e:
        print(f"حدث خطأ تقني: {e}")
        return None, None

def send_to_telegram(text, image_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {"chat_id": CHAT_ID, "photo": image_url, "caption": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# تجربة التشغيل برابط قصير
test_link = "https://amzn.to/example" # ضعي رابطك هنا
caption, img = get_amazon_data(test_link)
if caption and img:
    send_to_telegram(caption, img)
