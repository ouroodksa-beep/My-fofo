import requests
import telebot
import random

# --- 1. الإعدادات (تأكدي من صحة التوقن ووجود النقطتين :) ---
RAINFOREST_KEY = "702EB0E493B342139C8727EF35A626C0"
TELEGRAM_TOKEN = "7956075348:AAEwHrxqtlHzew69Mu2UlxVd_1hEBq9mDeA" 
CHAT_ID = "ftwu_bot"

bot = telebot.TeleBot()

# --- 2. قاموس العبارات السعودية (أكثر من 100 كلمة وجملة) ---
SAUDI_PHRASES = [
    "يا هلا ومسهلا بالزين", "لقطة العمر يا بعدي", "خذه وأنت مغمض", "جايب لكم شي يبيض الوجه", 
    "هذا اللي عليه الكلام", "تكفى لا يفوتك", "السعر لقطة وقسماً بالله", "فالك الطيب", 
    "شي فاخر من الآخر", "على ضمانتي جربه بس", "أطلق عرض شفته اليوم", "يا بلاش والله", 
    "عز الله إنه كفو", "الحق ما تلحق", "للناس الذوق وبس", "تراه لقطة يا جماعة", 
    "وش ترجي بعد هالسعر؟", "الزين فرض نفسه", "ما يبي لها تفكير", "عرض يبرد القلب",
    "يا حظ من شراه", "كشخة ولقطة بنفس الوقت", "تدلل يا بعد حيي", "هذا المطنوخ صح",
    "يسوى ريال ريال", "هدية تبيض الوجه", "عليك بالعافية مقدماً", "قرم وراعي ذوق",
    "شي يسعد الخاطر", "خلك ذيب واشتريه", "والله إنه شي يجمل", "سعر خيالي يا بطل",
    "بشرى سارة لراعين الذوق", "وش تنتظر؟ العرض نار", "بصراحة شي ما يتفوت", "يا لبييه على هالزين",
    "ذوقك رفيع يا شيخ", "هذا اللي يدور عليه الكل", "جودة وسعر توب", "خذه وما تندم",
    "يا هلا باللي يدور التوفير", "جبناه لك لين عندك", "وفر قريشاتك واشتريه", "قوة القوة",
    "شي يرفع الراس", "على متمه يا غالي", "يا حي هالعين", "للي يعرفون للزين",
    "سعر يكسر الصخر", "ما شا الله تبارك الله", "منوة الخاطر", "تدلل عسى عمرك طويل",
    "لا تضيع الفرصة من يدك", "الزين عندنا والشين حولنا", "بالهنا والشفا", "يستاهل كل ريال",
    "يا بعد راسي والله", "انشهيد إنه زين", "خلك سبّاق", "العرض لؤلؤ", "يا حي هالطاري",
    "فداك كلي خذه", "شي يونس", "رخص التراب", "بلاش بلاش يا ولد", "ما يغلى عليك",
    "يا حبني لك ولذوقك", "هذا الطلب الصح", "أبشر بالخير", "سمّ وابشر باللي يسرك",
    "عرض يشرح الصدر", "من الأخير.. خذه", "الزبون دايماً على حق", "لبيه يا هالمنتج",
    "سعر ولا في الأحلام", "كفو والله كفو", "ابك إنه زين", "يا وجد حالي عليه",
    "الزين يفرض هيبته", "صيدة اليوم", "ارحبوا يا أهل الزين", "جبت لك العلم الوكاد",
    "فالك الفوز بهالعرض", "وش بقيت لغيرك؟", "جمال ودلال وسعر خيال", "أنت تستاهل أكثر",
    "هذا اللي يفتح النفس", "ما عليه حكي", "زين القوم", "يا لبى قلبك", "خذه ودع لي",
    "الفرصة تجيك مرة", "طابت ليلتك بهالزين", "يا مال العز", "سعر ماله مثيل",
    "يا ويلي على السعر", "يجنن يجنن", "ذوقك دايم يغلبني", "أبشر بعزك", "خذ العلم"
]

def get_amazon_details_ar(short_url):
    try:
        # أ- فك الرابط المختصر
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = session.head(short_url, allow_redirects=True, timeout=15, headers=headers)
        long_url = resp.url
        
        # ب- طلب البيانات بالعربي
        params = {
            'api_key': RAINFOREST_KEY,
            'type': 'product',
            'url': long_url,
            'language': 'ar_AE',
            'amazon_domain': 'amazon.sa'
        }
        
        response = requests.get('https://api.rainforestapi.com/request', params=params)
        res = response.json()
        
        if res.get("success"):
            product = res.get("product", {})
            title = product.get("title", "منتج رهيب")
            
            # ج- السعر
            price_info = product.get("buybox_winner", {}).get("price", {})
            if not price_info: price_info = product.get("price", {})
            price_value = price_info.get("value", "غير متوفر")
            
            # د- الصورة بأعلى جودة
            images = product.get("images", [])
            image_url = images[0].get("link") if images else product.get("main_image", {}).get("link")
            
            # هـ- اختيار عبارة سعودية عشوائية
            shorthand = random.choice(SAUDI_PHRASES)
            
            caption = (
                f"🔥 **{shorthand}** 🔥\n\n"
                f"📦 **اسم القطعة:**\n{title}\n\n"
                f"💸 **سعره الحين:** {price_value} ريال بس!\n\n"
                f"🔗 **رابط الشراء (الحق عليه):**\n{short_url}\n\n"
                f"🇸🇦 شحن سريع لين باب بيتك"
            )
            return caption, image_url
    except Exception as e:
        print(f"Error: {e}")
    return None, None

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text
    if "amazon" in url or "amzn.to" in url:
        wait_msg = bot.reply_to(message, "⏳ أبشر.. جاري تجهيز العرض السنع...")
        caption, photo = get_amazon_details_ar(url)
        
        if caption and photo:
            bot.send_photo(CHAT_ID, photo, caption=caption, parse_mode="Markdown")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ المعذرة منك، الرابط فيه مشكلة أو المنتج مخلص.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    print("🚀 البوت السعودي شغال.. عطنا الروابط يا ذيب!")
    bot.infinity_polling()
