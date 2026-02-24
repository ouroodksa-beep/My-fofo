import requests
from bs4 import BeautifulSoup
import telebot
import os
from flask import Flask
from threading import Thread
import random
import re
import time

# --- الإعدادات ---
TOKEN = "8769441239:AAEgX3uBbtWc_hHcqs0lmQ50AqKJGOWV6Ok"
CHANNEL_ID = "@ouroodbot"  # مثال: @your_channel أو -1001234567890

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة بيانات الأنماط السعودية (100+ قالب) ---
SAUDI_TEMPLATES = {
    "surprised_discovery": [  # اكتشاف مفاجئ
        "يا جماعة والله صدمتني {title}!\n\nكنت أدور من زمان على شي زي كذا، وقبل لا أطلبه لقيته بـ {price} ريال بس 😭\n\nاللي جربه يقولي يستاهل ولا لا؟",
        "ما شاء الله تبارك الله شفتوا {title}؟\n\nأنا من صدمتي نزلت لكم المنشور على طول، السعر {price} ريال!\n\nوالله العظيم ما توقعت إني ألقى شي بجودة زي كذا بهالسعر",
        "يا أخي {title} هذا غيييير!\n\nكنت أشك فيه بس لما شفت السعر {price} ريال قلت لازم أجرب!\n\nمن جربه يعطيني رأيه الصريح؟",
    ],
    
    "friend_recommendation": [  # توصية صديق
        "أخوي الصراحة ما يقصر، قالي جرب {title} وما راح تندم\n\nقلت له كم؟ قال {price} ريال!\n\nقلت له يا حبيبي ليش ما قلت لي من قبل؟ 😂",
        "صديقتي الله يحفظها جابت لي {title} هدية\n\nقلت لها كم سعره؟ قالت {price} ريال!\n\nصراحة ما توقعت يكون بهالجودة، فكرته أغلى بكثير",
        "العيال في البيت مجانين على {title}!\n\nكل يوم يتهاوشون عليه، قلت بشتري لكل واحد وحدة بـ {price} ريال وخلاص\n\nالراحة النفسية بـ {price} ريال تستاهل والله",
    ],
    
    "personal_story": [  # قصة شخصية
        "أمس كنت في مجلس وطلع الحديث على {title}\n\nواحد من الشباب قال اشتريته بـ {price} ريال\n\nالكل طلب الرابط على طول، قلت لازم أنشره لكم هنا",
        "والله يا جماعة {title} أنقذني!\n\nكنت في موقف محرج وطلع معي البرودكت هذا، {price} ريال بس!\n\nالقيمة مقابل السعر = صفرندة",
        "قصة سريعة: اشتريت {title} قبل شهر بـ {price} ريال\n\nاليوم جاني أخوي يسأل عنه، قلت له نفذت الكمية 😂\n\nرجعت لقيته متوفر، قلت لازم أنبهكم",
    ],
    
    "urgent_fomo": [  # عجلة وفومو
        "بسرعة بسرعة! {title} نازل بـ {price} ريال\n\nأنا نفسي ما صدقت لما شفت السعر، طلبت حبتين\n\nالكمية محدودة يا جماعة، اللي يبغى يستعجل",
        "يا شباب {title} بـ {price} ريال بس!\n\nالسعر هذا ما راح يتكرر، جربت أدور على بديل أرخص وما لقيت\n\nاللي يبي يوفر يركض الآن",
        "تنبيه مهم! {title} متوفر بـ {price} ريال\n\nقبل ساعة كان {price + 50} ريال، نزل السعر فجأة\n\nاللي يبغى يستفيد من العرض يدخل الرابط",
    ],
    
    "honest_review": [  # مراجعة صادقة
        "بصراحة {title}...\n\nالجودة: 10/10\nالسعر: {price} ريال (مناسب جداً)\nالتغليف: ممتاز\n\nالشي الوحيد اللي عجبني فيه أكثر {title}\n\nجربوه وادعولي",
        "مراجعة سريعة لـ {title}:\n\n✅ يستاهل كل ريال ({price} ريال)\n✅ التوصيل سريع\n✅ ما فيه عيوب واضحة\n\nالتقييم النهائي: أنصح فيه بقوة",
        "صار لي أسبوع استخدم {title}\n\nالصراحة ما توقعت يكون كويس بهالسعر ({price} ريال)\n\nبس ثبت لي العكس، جودة عالية وسعر منافس",
    ],
    
    "funny_casual": [  # عفوي ومضحك
        "أنا و {title} قصة حب من أول نظرة 😂\n\nشفته بـ {price} ريال قلت هذا لازم يكون عندي\n\nوالله العظيم ما ندمت، صار من أساسيات يومي",
        "يا جماعة {title} هذا يفشل الخصوم!\n\n{price} ريال بس؟ حتى البقالة أغلى من كذا 😭\n\nاللي ما يشتري يكون ظالم لنفسه صدق",
        "قاعد أشرب قهوتي وافكر في {title}\n\nليه ما اشتريته من زمان؟ {price} ريال بس!\n\nالندم يا جماعة، لكن الحمدلله لحقت عليه",
    ],
    
    "family_mom": [  # أم وعائلة
        "يا بنات {title} هذا لازم يكون في كل بيت!\n\n{price} ريال بس ويريحك من متاعب كثيرة\n\nجربته لأولادي وصاروا يتهاوشون عليه",
        "للأمهات بالذات: {title}\n\n{price} ريال وتوفير وقت وجهد، والله يستاهل\n\nأنا اشتريته وصرت أنصح فيه للجميع",
        "بناتي الحلوين، {title} هذا نعمة!\n\n{price} ريال بس ويغنيك عن أشياء كثيرة\n\nجربوه وقولولي رأيكم",
    ],
    
    "curious_question": [  # فضول وتساؤل
        "سؤال للجميع: هل {title} يستاهل الضجة؟\n\nأنا شفته بـ {price} ريال ومحتارة أشتريه ولا لا\n\nاللي جربه يعطيني رأيه الصريح؟",
        "محتاج رأيكم في {title}...\n\nالسعر {price} ريال، والمواصفات تبدأ حلوة\n\nتنصحوني فيه ولا أدور على بديل؟",
        "شفت {title} وعجبني بس خايفة أندم\n\n{price} ريال مو كثير بس برضه...\n\nاللي عنده خبرة يفيدني؟",
    ],
    
    "luxury_deal": [  # صفقة فاخرة
        "{title} هذا يستاهل يكون أغلى!\n\n{price} ريال بس؟ والله سرقة نظيفة\n\nالجودة فاخرة والسعر شعبي، ما راح تلقون زيه",
        "يا أهل الفخامة: {title}\n\n{price} ريال بس وتحصلون على جودة 5 نجوم\n\nفرصة ما تتعوض يا جماعة",
        "لو تدورون على شي يميزكم، {title} هو الحل\n\n{price} ريال بس وشكلكم يصير غييير\n\nأنا اشتريته وصرت أحس بنفسي VIP 😎",
    ],
    
    "daily_essential": [  # ضرورة يومية
        "{title} مو رفاهية، ضرورة!\n\n{price} ريال بس ويسهل عليك حياتك اليومية\n\nجربوه وقولولي كيف عشتوا بدونه قبل؟",
        "كل يوم أستخدم {title} وأدعي لصاحب الفكرة\n\n{price} ريال بس ويوفر علي وقت وطاقة\n\nأنصح فيه بشدة للي يبي يرتب حياته",
        "من أساسيات البيت: {title}\n\n{price} ريال بس ويغنيك عن مشاكر كثيرة\n\nاشتريته مرتين عشان أهدي أهلي",
    ],
    
    "gift_idea": [  # فكرة هدية
        "محتارين في الهدية؟ {title} هو الحل!\n\n{price} ريال بس ويفرح أي أحد\n\nأنا اشتريته هدية لأختي وصارت تدعي لي كل يوم",
        "هدية مثالية بـ {price} ريال: {title}\n\nمناسب للجميع وما يحتاج تفكير\n\nجربوه وشكروني بعدين",
        "اللي يبغى يهدي شي مميز: {title}\n\n{price} ريال بس ويبقى ذكرى طيبة\n\nأنا اشتريته لأمي وصارت تتباهى فيه",
    ],
    
    "comparison": [  # مقارنة
        "قارنت {title} بـ 3 بدائل...\n\nالنتيجة: {title} أفضلهم وأرخصهم!\n\n{price} ريال بس مقابل {price + 100} ريال للبديل\n\nالفرق واضح يا جماعة",
        "جربت النوع الفلاني قبل {title}...\n\n{title} أحسن بمراحل وبسعر أقل ({price} ريال)\n\nلا تضيعون فلوسكم على البدائل الغالية",
        "بين {title} والمنافسين: لا منافسة!\n\n{price} ريال بس وجودة تفوق السعر بمراحل\n\nجربوه وقارنوا بنفسكم",
    ],
    
    "emotional": [  # عاطفي
        "{title} هذا غيّر مزاجي!\n\n{price} ريال بس وأنا سعيدة فيه\n\nاللي يقول السعالة ما تشتريها بالفلوس ما جرب {title}",
        "أول مرة أكتب منشور عن منتج...\n\nبس {title} يستاهل! {price} ريال بس وأثر فيني\n\nاللي يبغى يحس بفرق يجربه",
        "ما كنت أصدق إني أتعلق بمنتج بس {title}...\n\n{price} ريال بس وصار جزء من يومي\n\nأحببته والله ❤️",
    ],
    
    "short_powerful": [  # قصير وقوي
        "{title} = {price} ريال\n\nكفاية كلام، جربوه بنفسكم",
        "يا جماعة {title}!\n\n{price} ريال بس\n\nاللي يبي يوفر يدخل",
        "سرعة! {title} بـ {price} ريال\n\nالكمية محدودة",
    ],
    
    "storytelling": [  # سرد قصصي
        "في يوم من الأيام، كنت أعاني من...\n\nلقيت {title} بـ {price} ريال وانقلبت حياتي\n\nالآن ما أقدر أعيش بدونه، صدقوني",
        "قصتي مع {title} بدأت بالصدفة...\n\nشفته بـ {price} ريال وقلت أجرب\n\nوالآن صرت سفيرته المجانية 😂",
        "من ساعة ما اشتريت {title}...\n\n{price} ريال بس وكل شي تغير\n\nالراحة، الجودة، السعر، كل شي مثالي",
    ],
    
    "expert_advice": [  # نصيحة خبير
        "بعد 5 سنوات تجربة في المجال...\n\nأنصحكم بـ {title} بقوة\n\n{price} ريال بس ويضاهي منتجات بآلاف الريالات",
        "كخبيرة في المجال، نادراً أنصح بمنتج...\n\nبس {title} استثناء! {price} ريال بس وجودة احترافية\n\nثقة في الله ثم في كلامي",
        "جربت أكثر من 20 منتج相似...\n\n{title} الأفضل بلا منازع\n\n{price} ريال بس ويغنيك عن الباقي",
    ],
    
    "social_proof": [  # إثبات اجتماعي
        "أكثر من 10,000 طلب على {title}!\n\n{price} ريال بس والناس مجانين عليه\n\nانضموا للناجحين وجربوه",
        "كل اللي حولي يتكلم عن {title}!\n\n{price} ريال بس وصار ترند\n\nأنا اشتريته عشان أفهم الضجة، والآن أفهم",
        "شفت {title} في كل مكان...\n\nقلت لازم أجربه بـ {price} ريال\n\nوالله العظيم يستاهل الشهرة",
    ],
    
    "problem_solution": [  # مشكلة وحل
        "كنت أعاني من [المشكلة]...\n\nلقيت الحل في {title} بـ {price} ريال!\n\nالآن [الحل]، الحمدلله",
        "عندك [المشكلة]؟ {title} ينحلها!\n\n{price} ريال بس وانتهت المعاناة\n\nجربوه وقولولي كيف كان تأثيره",
        "من زمان أدور حل لـ [المشكلة]...\n\n{title} كان الإجابة! {price} ريال بس\n\nأخيراً لقيت ضالتي",
    ],
    
    "seasonal": [  # مناسبات
        "قبل رمضان: جهزوا {title}!\n\n{price} ريال بس ويريحكم في الشهر الفضيل\n\nأنا جاهزة من الحين",
        "عروض العيد: {title} بـ {price} ريال\n\nهدية مثالية لأحبابكم\n\nالكمية محدودة يا جماعة",
        "العودة للمدارس: {title} ضروري!\n\n{price} ريال بس ويسهل على الأولاد\n\nأمهات، لا تفوتون الفرصة",
    ],
    
    "mystery": [  # غموض
        "في منتج سري غيّر حياتي...\n\nاسمه {title}، سعره {price} ريال\n\nاللي يعرف سره يفهم ليش أتكلم",
        "ما راح أقول كثير...\n\nبس {title} بـ {price} ريال يستاهل التجربة\n\nاللي يجربه يفهم قصدي",
        "سر نجاحي الأخير: {title}\n\n{price} ريال بس والتفاصيل سرية 😎\n\nجربوه وانضموا لنادي الناجحين",
    ],
    
    "challenge": [  # تحدي
        "تحدي: جربوا {title} بـ {price} ريال\n\nإذا ما عجبكم، أنا أتحمل المسؤولية!\n\nبس والله ما راح تندمون",
        "أقسم بالله {title} يستاهل!\n\n{price} ريال بس، واللي ما يشتري يخسر\n\nتحدي: جربوه وقولولي رأيكم",
        "يا جريئين: {title} بـ {price} ريال\n\nاللي يخاف من التجديد لا يدخل\n\nبس اللي يحب الاختلاف يجرب",
    ],
    
    "nostalgia": [  # حنين
        "ذكّرني {title} بأيام زمان...\n\nبس بجودة عصرية! {price} ريال بس\n\nأحلى مزج بين الأصالة والحداثة",
        "من أيام الجدات... بس أحسن!\n\n{title} بـ {price} ريال يجمع الطيبين\n\nأنا اشتريته وذكرتني بأمي ❤️",
        "الأشياء الحلوة ما تتغير...\n\n{title} أثبت هذا الكلام! {price} ريال بس\n\nجودة تستحق التقدير",
    ],
    
    "minimalist": [  # بساطة
        "{title}\n{price} ريال\n\nكفاية.",
        "بسيط، عملي، رخيص\n\n{title} = {price} ريال\n\nما يحتاج كلام أكثر",
        "لا تكلفة، لا فلسفة...\n\n{title} بـ {price} ريال\n\nجربوه",
    ],
    
    "luxury_humble": [  # فخامة متواضعة
        "شي فاخر بسعر شعبي: {title}\n\n{price} ريال بس وشكلكم مليون دولار\n\nأنا استخدمته في مناسبة مهمة وانبهر الجميع",
        "فخامة ما لها مثيل بـ {price} ريال!\n\n{title} يعطيكم لوك غييير\n\nالسعر سرّي تقريباً 😂",
        "لو تبغون تبهرون الناس: {title}\n\n{price} ريال بس ويبدو أغلى بمراحل\n\nخدعة السعر المنخفض",
    ],
    
    "skeptic_converted": [  # متشكك متحول
        "كنت أشك في {title}...\n\nقلت {price} ريال؟ أكيد جودته ضعيفة!\n\nجربته وصرت أعتذر لصاحبه 😅",
        "أول ما شفت {title} قلت: كذب!\n\nبس لما جربته بـ {price} ريال...\n\nصرت أشترِيه للكل هدية!",
        "اعترف: كنت متشككة في {title}\n\n{price} ريال يبدو مشبوه...\n\nالآن؟ أنا سفيرته الرسمية!",
    ],
    
    "family_tested": [  # مجرب عائلي
        "اختبرنا {title} في بيتنا...\n\nالأب: يستاهل\nالأم: رهيب\nالأولاد: نبغى زيه!\n\nالسعر: {price} ريال\n\nإجماع عائلي نادر",
        "عيلتي مجنونة على {title}!\n\n{price} ريال بس ويرضي الجميع\n\nمن جرب عائلته يفهمني",
        "بيتنا صار يعتمد على {title}\n\n{price} ريال بس وسعادة عائلية\n\nأفضل استثمار في حياتي",
    ],
    
    "budget_smart": [  # ذكي ميزانية
        "محترفين التوفير: {title}!\n\n{price} ريال بس وقيمة عالية\n\nأنا أحسب كل ريال، وهذا يستاهل فعلاً",
        "ميزانيتي محدودة بس ذكية...\n\n{title} بـ {price} ريال خيار مثالي\n\nجودة ما تتنازل وسعر يرضي",
        "للذكيين فقط: {title}\n\n{price} ريال بس وتوفر أكثر\n\nأنا وفرت {price} ريال مقارنة بالبديل",
    ],
    
    "quality_emphasis": [  # تأكيد الجودة
        "{title} = جودة!\n\n{price} ريال بس وما فيه مقارنة\n\nاللي يفهم في الجودة يعرف كلامي",
        "جودة عالية، سعر منخفض: {title}\n\n{price} ريال بس ويتحمل الاستخدام اليومي\n\nأنا مجربة من شهرين وما تغير شي",
        "ما أبيع كلام... {title} يتكلم!\n\n{price} ريال بس ومواصفات ممتازة\n\nجودة تستحق الثقة",
    ],
    
    "time_saver": [  # توفير وقت
        "{title} يوفر لي ساعة يومياً!\n\n{price} ريال بس = 365 ساعة في السنة\n\nحسبوها صح؟ يستاهل مليون مرة",
        "الوقت ذهب: {title} يحفظه!\n\n{price} ريال بس وانتهى التأخير\n\nأنا صرت أنتج أكثر بفضله",
        "كل دقيقة تهم... {title} يوفرها!\n\n{price} ريال بس وكفاءة عالية\n\nللناجحين فقط",
    ],
    
    "health_focused": [  # تركيز صحي
        "صحتكم تهمنا: {title}!\n\n{price} ريال بس ويحميكم\n\nأنا استشارتي الطبية أوصت فيه",
        "للصحة والعافية: {title}\n\n{price} ريال بس وفرق واضح\n\nجربوه وتحسوا الفرق",
        "استثمار في صحتكم: {title}\n\n{price} ريال بس ووقاية خير من علاج\n\nأنا اشتريته لكل عائلتي",
    ],
    
    "tech_savvy": [  # تقني
        "كمحبة للتقنية: {title} يفوز!\n\n{price} ريال بس ومواصفات عالية\n\nما توقعت بهالسعر ألقى كذا",
        "تقنية ذكية بـ {price} ريال: {title}\n\nسهل الاستخدام وفعال\n\nحتى أمي تقدر تستخدمه",
        "عشاق التقنية: {title} لازم يكون عندكم!\n\n{price} ريال بس ويضاهي الماركات\n\nأنا مجربة وأشهد",
    ],
    
    "beginner_friendly": [  # مناسب للمبتدئين
        "للمبتدئين: {title} مثالي!\n\n{price} ريال بس وسهل جداً\n\nما تحتاجون خبرة عشان تستفيدون",
        "أول مرة أجرب شي زي كذا...\n\n{title} جعل التجربة سهلة! {price} ريال بس\n\nممتاز للمبتدئين",
        "تخافون من التعقيد؟ {title} حلّه!\n\n{price} ريال بس وبسيط 100%\n\nجربوه وانبسطوا",
    ],
    
    "durability": [  # متانة
        "من شهرين اشتريت {title}...\n\nالآن زي الجديد! {price} ريال بس ومتانة عالية\n\nيستاهل الاستثمار",
        "{title} = متانة!\n\n{price} ريال بس ويتحمل السنين\n\nأنا اشتريت النوع الغالي قبل وما استمر\n\nهذا أفضل بمراحل",
        "اللي يبغى شي يدوم: {title}\n\n{price} ريال بس وجودة بناء ممتازة\n\nما راح تندمون",
    ],
    
    "multi_purpose": [  # متعدد الاستخدامات
        "{title} = 5 منتجات في واحد!\n\n{price} ريال بس واستخدامات متعددة\n\nوفرت مساحة وفلوس",
        "منتج واحد يعمل كل شي: {title}\n\n{price} ريال بس ويغنيك عن الباقي\n\nأنا استغنيت عن 3 أشياء بسببه",
        "ذكي ومتعدد: {title}\n\n{price} ريال بس ووظائف عديدة\n\nقيمة حقيقية للفلوس",
    ],
    
    "eco_friendly": [  # صديق للبيئة
        "للبيئة ولكم: {title}!\n\n{price} ريال بس وصديق للبيئة\n\nأنا اشتريته عشان أقلل التأثير السلبي",
        "خيار أخضر بـ {price} ريال: {title}\n\nجودة عالية ومواد صديقة للبيئة\n\nنفس مرتاحة وأنا أستخدمه",
        "للمهتمين بالبيئة: {title}\n\n{price} ريال بس ومستدام\n\nأفضل قرار اتخذته هذا الشهر",
    ],
    
    "travel_friendly": [  # مناسب للسفر
        "مسافرين؟ {title} ضروري!\n\n{price} ريال بس وخفيف الوزن\n\nأنا ما أسافر بدونه",
        "مثالي للسفر: {title}\n\n{price} ريال بس وعملي جداً\n\nوفّر لي مساحة في الشنطة",
        "رحلتي الأخيرة كانت أسهل بـ {title}\n\n{price} ريال بس وسهل الحمل\n\nمسافرين، لا تفوتونه",
    ],
    
    "gift_perfect": [  # هدية مثالية
        "هدية ما تخيب: {title}!\n\n{price} ريال بس ويفرح أي أحد\n\nأنا اشتريته 5 مرات هدية",
        "مشوار الهدايا انتهى: {title}\n\n{price} ريال بس ومناسب للجميع\n\nكل من هديته فرحانة",
        "الهدية المثالية بـ {price} ريال: {title}\n\nأنيق، عملي، مفيد\n\nما تحتاجون تفكير",
    ],
    
    "office_work": [  # عمل ومكتب
        "للعمل: {title} = إنتاجية!\n\n{price} ريال بس ويرتب يومكم\n\nأنا صرت أنجز أكثر بفضله",
        "مكتبي صار أحسن بـ {title}\n\n{price} ريال بس وفرق واضح\n\nزملائي يسألون عنه",
        "للمهنيين: {title} ضروري\n\n{price} ريال بس ويحسن الأداء\n\nاستثمار في نجاحكم",
    ],
    
    "kids_approved": [  # موافقة الأطفال
        "أولادي وافقوا: {title}!\n\n{price} ريال بس ويرضي الصغار\n\nأنا اشتريته وصاروا يتهاوشون عليه",
        "اختبار الأطفال: {title} نجح!\n\n{price} ريال بس وآمن وممتع\nأمهات، جربوه",
        "اللي يرضي الأولاد: {title}\n\n{price} ريال بس وعملي للأهل\n\nأفضل شي اشتريته لعيالي",
    ],
    
    "pet_friendly": [  # مناسب للحيوانات
        "لأصحاب الحيوانات: {title}!\n\n{price} ريال بس وعملي\n\nقطتي وافقت 😸",
        "حيواناتكم تحب {title}!\n\n{price} ريال بس وآمن\n\nأنا جربته على كلبي وصار يتهاوش عليه",
        "للحيوانات الأليفة: {title}\n\n{price} ريال بس وينظف بسهولة\n\nأفضل صفقة لبيتي",
    ],
    
    "cooking_food": [  # طبخ وأكل
        "للطباخين: {title} = نجاح!\n\n{price} ريال بس ويحسن الأكل\n\nأنا صرت طباخة أحسن 😂",
        "مطبخي صار احترافي بـ {title}\n\n{price} ريال بس وفرق في الطعم\n\nالكل يسأل سر الطبخة",
        "عشاق الأكل: {title} لازم يكون عندكم!\n\n{price} ريال بس ويحسن كل شي\n\nجربوه وشكروني",
    ],
    
    "fitness_health": [  # لياقة وصحة
        "للرياضيين: {title} ممتاز!\n\n{price} ريال بس ويساعد في التمرين\n\nأنا صرت أتمرن أكثر بفضله",
        "صحتكم تهمنا: {title}\n\n{price} ريال بس ويشجع على الرياضة\n\nابدأوا رحلتكم اليوم",
        "للياقة البدنية: {title}\n\n{price} ريال بس وفعال\n\nأنا لاحظت فرق خلال أسبوعين",
    ],
    
    "home_decor": [  # ديكور منزل
        "بيتي صار أجمل بـ {title}!\n\n{price} ريال بس ويغير الجو\n\nزواري يسألون من وين",
        "للديكور: {title} = أناقة!\n\n{price} ريال بس ويبدو غالي\n\nأنا سعيدة فيه جداً",
        "بيت أحلى بـ {price} ريال: {title}\n\nبسيط وأنيق\n\nيستاهل التجربة",
    ],
    
    "cleaning": [  # تنظيف
        "للتنظيف: {title} = سهولة!\n\n{price} ريال بس ويوفر وقت\n\nأنا صرت أنظف بسرعة البرق",
        "نظافة بدون تعب: {title}\n\n{price} ريال بس وفعال\n\nاللي يكره التنظيف يفهمني",
        "بيت نظيف بـ {price} ريال: {title}\n\nيستاهل كل ريال\n\nجربوه وانبسطوا",
    ],
    
    "organization": [  # تنظيم
        "للتنظيم: {title} = راحة!\n\n{price} ريال بس ويرتب الفوضى\n\nأنا صرت أحب بيتي أكثر",
        "فوضاكم تحتاج {title}!\n\n{price} ريال بس ويحل المشكلة\n\nمنظمين، جربوه",
        "ترتيب بـ {price} ريال: {title}\n\nسهل الاستخدام وعملي\n\nأفضل شي للبيت",
    ],
    
    "safety_security": [  # أمان
        "للأمان: {title} = حماية!\n\n{price} ريال بس ويوفر راحة بال\n\nأنا اشتريته لأهلي",
        "أمان بـ {price} ريال: {title}\n\nيستاهل الاستثمار\n\nما فيه أغلى من السلامة",
        "لحمايتكم: {title}\n\n{price} ريال بس وفعال\n\nأنا أنصح فيه بشدة",
    ],
    
    "night_routine": [  # روتين ليلي
        "قبل النوم: {title} = راحة!\n\n{price} ريال بس ويحسن النوم\n\nأنا صرت أنام أحسن",
        "روتيني الليلي يحتوي {title}\n\n{price} ريال بس ويستاهل\n\nجربوه وناموا بعمق",
        "للنوم الهادئ: {title}\n\n{price} ريال بس وفعال\n\nأنا لاحظت الفرق فوراً",
    ],
    
    "morning_routine": [  # روتين صباحي
        "صباحي يبدأ بـ {title}!\n\n{price} ريال بس ويحسن اليوم\n\nأنا صرت صباحية بفضله",
        "للصباحيات: {title} ضروري\n\n{price} ريال بس ويوفر وقت\n\nأنجزوا أكثر في أقل وقت",
        "بداية يوم مثالية: {title}\n\n{price} ريال بس ويشحن الطاقة\n\nجربوه وانبسطوا",
    ],
    
    "weekend_vibes": [  # مزاج الويكند
        "الويكند مع {title} = كمال!\n\n{price} ريال بس ويستاهل الاسترخاء\n\nأنا جاهزة للراحة",
        "نهاية أسبوع مثالية: {title}\n\n{price} ريال بس ويحسن المزاج\n\nاسترخوا بذوق",
        "للويكند: {title}\n\n{price} ريال بس وعملي\n\nاستمتعوا بوقتكم",
    ],
    
    "study_focus": [  # دراسة وتركيز
        "للدراسة: {title} = تركيز!\n\n{price} ريال بس ويساعد\n\nأنا صرت أذاكر أحسن",
        "طلابنا يحتاجون {title}!\n\n{price} ريال بس ويحسن الأداء\n\nجربوه وانجحوا",
        "للتركيز: {title}\n\n{price} ريال بس وفعال\n\nأنا لاحظت الفرق في الامتحانات",
    ],
    
    "creative_projects": [  # مشاريع إبداعية
        "للإبداع: {title} = إلهام!\n\n{price} ريال بس ويساعد\n\nأنا صرت أبدع أكثر",
        "مشاريعي تحتاج {title}!\n\n{price} ريال بس ويعطي نتائج\n\nفنانين، جربوه",
        "للإبداع: {title}\n\n{price} ريال بس ويحفز\n\nأنا سعيدة فيه",
    ],
    
    "gaming": [  # ألعاب
        "للجيمرز: {title} = فوز!\n\n{price} ريال بس ويحسن الأداء\n\nأنا صرت ألعب أحسن",
        "ألعابكم تحتاج {title}!\n\n{price} ريال بس ويعطي ميزة\n\nجربوه وانتصروا",
        "للألعاب: {title}\n\n{price} ريال بس وعملي\n\nأنا راضية 100%",
    ],
    
    "music_audio": [  # موسيقى وصوت
        "للموسيقى: {title} = جودة!\n\n{price} ريال بس وصوت رهيب\n\nأنا سمعتي فرق واضح",
        "عشاق الصوت: {title} لازم يكون عندكم!\n\n{price} ريال بس ويضاهي الغالي\n\nأنا مجربة وأشهد",
        "للصوت: {title}\n\n{price} ريال بس وممتاز\n\nموسيقيين، جربوه",
    ],
    
    "photography": [  # تصوير
        "للتصوير: {title} = إبداع!\n\n{price} ريال بس ويحسن الصور\n\nأنا صرت مصورة أحسن",
        "مصورين؟ {title} ضروري!\n\n{price} ريال بس ويعطي نتائج\n\nجربوه وتميزوا",
        "للصور: {title}\n\n{price} ريال بس وعملي\n\nأنا سعيدة بالنتائج",
    ],
    
    "reading_books": [  # قراءة
        "للقراءة: {title} = متعة!\n\n{price} ريال بس ويحسن التجربة\n\nأنا صرت أقرأ أكثر",
        "قرّاء؟ {title} لازم يكون عندكم!\n\n{price} ريال بس ويريح\n\nجربوه وانغمسوا في الكتب",
        "للكتب: {title}\n\n{price} ريال بس ومفيد\n\nأنا أنصح فيه",
    ],
    
    "self_care": [  # العناية بالنفس
        "للعناية: {title} = حب!\n\n{price} ريال بس ويستاهل\n\nأنا صرت أعتني بنفسي أكثر",
        " yourselves deserve {title}!\n\n{price} ريال بس ويسعد\n\nدللوا نفسكم",
        "للنفس: {title}\n\n{price} ريال بس ويستاهل\n\nأنا سعيدة فيه",
    ],
    
    "parenting": [  # تربية
        "للأهل: {title} = مساعد!\n\n{price} ريال بس ويسهل\n\nأنا صرت أم أحسن",
        "تربية أسهل مع {title}!\n\n{price} ريال بس ويوفر وقت\n\nأمهات، جربوه",
        "للأطفال: {title}\n\n{price} ريال بس وآمن\n\nأنا اشتريته وانبسطت",
    ],
    
    "elderly_care": [  # رعاية كبار السن
        "لكبار السن: {title} = راحة!\n\n{price} ريال بس ويساعد\n\nأنا اشتريته لأمي",
        "سنهم يحتاج {title}!\n\n{price} ريال بس ويعطي استقلالية\n\nأنصح فيه بشدة",
        "للأهل: {title}\n\n{price} ريال بس ومفيد\n\nأنا سعيدة فيه",
    ],
    
    "car_auto": [  # سيارات
        "للسيارة: {title} = كمال!\n\n{price} ريال بس ويحسن\n\nأنا صرت أحب سيارتي أكثر",
        "سياراتكم تحتاج {title}!\n\n{price} ريال بس وعملي\n\nسائقين، جربوه",
        "للمركبات: {title}\n\n{price} ريال بس وممتاز\n\nأنا راضية 100%",
    ],
    
    "outdoor_camping": [  # تخييم وخارج
        "للبر: {title} = مغامرة!\n\n{price} ريال بس ويستاهل\n\nأنا جاهزة للتخييم",
        "محبين الطبيعة؟ {title} ضروري!\n\n{price} ريال بس وعملي\n\nجربوه واستمتعوا",
        "للخارج: {title}\n\n{price} ريال بس وقوي\n\nمغامرين، جربوه",
    ],
    
    "beach_pool": [  # شاطئ ومسبح
        "للبحر: {title} = صيف!\n\n{price} ريال بس ويستاهل\n\nأنا جاهزة للإجازة",
        "المسبح يحتاج {title}!\n\n{price} ريال بس وعملي\n\nجربوه وانبسطوا",
        "للشاطئ: {title}\n\n{price} ريال بس وممتع\n\nأنا سعيدة فيه",
    ],
    
    "winter_cold": [  # شتاء وبرد
        "للبرد: {title} = دفا!\n\n{price} ريال بس ويحمي\n\nأنا جاهزة للشتاء",
        "شتاؤكم يحتاج {title}!\n\n{price} ريال بس ويدفي\n\nجربوه وادفوا",
        "للشتاء: {title}\n\n{price} ريال بس ودافئ\n\nأنا اشتريته وانبسطت",
    ],
    
    "summer_hot": [  # صيف وحر
        "للحر: {title} = برد!\n\n{price} ريال بس ويريح\n\nأنا جاهزة للصيف",
        "صيفكم يحتاج {title}!\n\n{price} ريال بس ويبرد\n\nجربوه واستمتعوا",
        "للصيف: {title}\n\n{price} ريال بس ومنعش\n\nأنا سعيدة فيه",
    ],
    
    "rainy_weather": [  # مطر
        "للمطر: {title} = جاهزية!\n\n{price} ريال بس ويحمي\n\nأنا ما أخاف من المطر",
        "موسم المطر يحتاج {title}!\n\n{price} ريال بس وعملي\n\nجربوه وابقوا جفاف",
        "للأمطار: {title}\n\n{price} ريال بس ومفيد\n\nأنا اشتريته وانبسطت",
    ],
    
    "special_occasion": [  # مناسبات خاصة
        "للمناسبات: {title} = تميز!\n\n{price} ريال بس ويبهر\n\nأنا جاهزة للحفلة",
        "مناسبتكم تحتاج {title}!\n\n{price} ريال بس وأنيق\n\nجربوه وتألقوا",
        "للاحتفالات: {title}\n\n{price} ريال بس ومميز\n\nأنا سعيدة فيه",
    ],
    
    "just_because": [  # بدون سبب
        "بدون سبب... {title}!\n\n{price} ريال بس ويستاهل\n\nأنا اشتريته عشان نفسي",
        "لأنكم تستاهلون: {title}\n\n{price} ريال بس وسعادة\n\nدللوا نفسكم",
        "مجرد {title}\n\n{price} ريال بس ويستاهل\n\nأنا سعيدة فيه",
    ],
}

# --- User Agents متنوعة ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# --- دوال مساعدة ---

@app.route('/')
def home():
    return "✅ Bot is Active - Saudi Affiliate Bot"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def extract_asin(url):
    """استخراج ASIN من رابط أمازون"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'amzn\.eu/d/([A-Z0-9]+)',
        r'amazon\..*/([A-Z0-9]{10})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_amazon_info(url):
    """استخراج معلومات المنتج مع محاولات متعددة"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }
            
            # محاكاة تصرف إنساني - انتظار عشوائي
            time.sleep(random.uniform(1, 3))
            
            session = requests.Session()
            
            # جلب الصفحة الرئيسية أولاً
            session.get("https://www.amazon.sa", headers=headers, timeout=10)
            time.sleep(random.uniform(0.5, 1.5))
            
            # جلب صفحة المنتج
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Attempt {attempt + 1}: Status {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج العنوان من مصادر متعددة
            title = None
            title_selectors = [
                '#productTitle',
                'h1.a-size-large.a-spacing-none',
                'h1.a-size-large',
                '.product-title',
                '[data-automation-id="product-title"]',
                'h1 span',
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    if len(title) > 5:  # التأكد من أن العنوان حقيقي
                        break
            
            # تنظيف العنوان
            if title:
                title = re.sub(r'\s+', ' ', title)  # إزالة المسافات الزائدة
                title = title[:100]  # تقصير العنوان
            
            # استخراج السعر من مصادر متعددة
            price = None
            price_selectors = [
                '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                '.a-price .a-offscreen',
                '.a-price-whole',
                '.a-price-range .a-offscreen',
                '[data-automation-id="buybox-price"]',
                '.a-text-price.a-size-medium.a-color-price',
                '.a-price-to-pay .a-offscreen',
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    # استخراج الأرقام فقط
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = price_match.group()
                        break
            
            # استخراج الصورة
            image_url = None
            image_selectors = [
                '#landingImage',
                '#imgBlkFront',
                '.a-dynamic-image.a-stretch-vertical',
                '.a-dynamic-image',
                'img[data-old-hires]',
                'img[data-a-dynamic-image]',
            ]
            
            for selector in image_selectors:
                element = soup.select_one(selector)
                if element:
                    image_url = element.get('data-old-hires') or element.get('src') or element.get('data-src')
                    if image_url and 'http' in image_url:
                        break
            
            # استخراج التقييم
            rating = None
            rating_selectors = [
                '.a-icon-alt',
                '[data-hook="average-star-rating"] .a-icon-alt',
                '.a-star-medium .a-icon-alt',
            ]
            
            for selector in rating_selectors:
                element = soup.select_one(selector)
                if element:
                    rating_text = element.get_text()
                    rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
                    if rating_match:
                        rating = rating_match.group(1)
                        break
            
            if title and price:
                return {
                    'title': title,
                    'price': price,
                    'image': image_url,
                    'rating': rating,
                    'url': url
                }
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(random.uniform(2, 4))
    
    return None

def generate_saudi_post(product_info):
    """توليد منشور سعودي عشوائي"""
    title = product_info['title']
    price = product_info['price']
    
    # اختيار فئة عشوائية
    category = random.choice(list(SAUDI_TEMPLATES.keys()))
    
    # اختيار قالب عشوائي من الفئة
    template = random.choice(SAUDI_TEMPLATES[category])
    
    # ملء القالب
    post = template.format(title=title, price=price)
    
    # إضافة إيموجي عشوائية للتنويع
    emojis = ['🔥', '✨', '💯', '😍', '👌', '⚡', '🎯', '💪', '🚀', '⭐']
    random_emojis = random.sample(emojis, random.randint(2, 4))
    
    # تنسيق النهائي
    final_post = f"{random.choice(random_emojis)} {post}\n\n"
    
    # إضافة هاشتاقات عشوائية
    hashtags = [
        "#تجربتي", "#تسوق", "#عروض", "#سعودية", "#توفير",
        "#تجربة_شراء", "#منتجات", "#تسوق_الكتروني", "#صفقات",
        "#ريفيو", "#تقييم", "#نصيحة", "#تجربتي_الشخصية"
    ]
    selected_hashtags = random.sample(hashtags, random.randint(3, 5))
    final_post += " ".join(selected_hashtags)
    
    return final_post

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    """معالجة الرسائل الواردة"""
    chat_id = message.chat.id
    
    # التحقق من وجود رابط أمازون
    if "amazon" in message.text.lower() or "amzn" in message.text.lower():
        # إرسال رسالة انتظار
        wait_msg = bot.reply_to(message, "⏳ ثواني أجيب لك العلم...")
        
        # استخراج الرابط
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
        
        if not urls:
            bot.edit_message_text("❌ ما لقيت رابط صحيح!", chat_id, wait_msg.message_id)
            return
        
        url = urls[0]
        
        # محاولة استخراج المعلومات
        product_info = get_amazon_info(url)
        
        if product_info:
            # توليد المنشور السعودي
            saudi_post = generate_saudi_post(product_info)
            
            # إرسال الصورة مع المنشور إذا توفرت
            try:
                if product_info.get('image'):
                    bot.send_photo(
                        CHANNEL_ID,
                        product_info['image'],
                        caption=saudi_post,
                        parse_mode="HTML"
                    )
                else:
                    bot.send_message(CHANNEL_ID, saudi_post, parse_mode="HTML")
                
                # إعلام المستخدم بالنجاح
                bot.edit_message_text(
                    f"✅ تم النشر!\n\nالعنوان: {product_info['title'][:50]}...\nالسعر: {product_info['price']} ريال",
                    chat_id,
                    wait_msg.message_id
                )
                
            except Exception as e:
                print(f"Error sending to channel: {e}")
                bot.edit_message_text(
                    "❌ صار خطأ في النشر للقناة، تأكدي من الآيدي",
                    chat_id,
                    wait_msg.message_id
                )
        else:
            bot.edit_message_text(
                "❌ ما قدرت أقرأ بيانات المنتج. جربي رابط ثاني أو تأكدي من الرابط.",
                chat_id,
                wait_msg.message_id
            )
    else:
        bot.reply_to(message, "👋 هلا! أرسلي رابط منتج من أمازون وأسوي لك منشور سعودي يجنن!")

def keep_alive():
    """إبقاء البوت شغال"""
    while True:
        time.sleep(60)
        print("Bot is alive...")

if __name__ == "__main__":
    # إزالة الويب هوك
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    
    # تشغيل Flask في Thread منفصل
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # تشغيل keep alive
    keep_alive_thread = Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    
    print("🤖 Bot started...")
    
    # تشغيل البوت
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
