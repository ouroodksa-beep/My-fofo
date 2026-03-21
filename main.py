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
# 🎯 جمل تسويقية حسب الجمهور
# ===================================

# 🔥 للرجال (أجهزة، أدوات، ملابس رجالية)
MEN_SENTENCES = [
    "والله صيدة صيدة يا رجال 🎣🔥",
    "صيدة العمر هذي يا أخوان 💯",
    "صيدة ما تتعوض يا شباب 🎯",
    "الحقو يا رجال قبل يروح 🏃‍♂️💨",
    "الحقو يا جماعة الخير ⚡️",
    "صيدة ذهبية يا أبطال 🏆",
    "فرصة صيد نادرة يا محترفين 💎",
    "الحقو الفرصة ذي يا رجال 👊",
    "صيدة السنة هذي يا شباب 🌟",
    "ما راح تلقى زيها أبداً يا رجال 🚨",
    "صيدة تاريخية يا أخوان 📉🔥",
    "الحقو قبل الكل يا شباب 🏃‍♂️",
    "صيدة مجنونة يا رجال 🤯",
    "الحقو الحقو يا أبطال 💪",
    "صيدة العروض يا محترفين 💰",
    "فرصة صيد ما تتكرر يا شباب ⏰",
    "الحقو يا ولد ⚠️",
    "صيدة فخمة يا رجال 👑",
    "الحقو الكمية محدودة جداً يا أخوان 🔥",
    "صيدة صيدة صيدة يا شباب 🎣🎣🎣",
    "ينتهي بأي لحظة يا رجال ⏰⚡️",
    "الوقت ينفد بسرعة يا أبطال ⏳🔥",
    "لا تنام عليه يا شباب 🚨🚨",
    "ينتهي اليوم يا رجال 🌙",
    "العرض ينتهي بسرعة يا أخوان 💨",
    "فرصة لحظية يا شباب ⚡️",
    "الحقو قبل ينتهي العرض يا رجال ⏰",
    "ينتهي خلال ساعات يا أبطال ⏳",
    "الوقت ضيق جداً يا شباب 🚨",
    "العرض محدود الوقت يا رجال ⏰💥",
    "ينتهي بدون سابق إنذار يا أخوان ⚠️",
    "الحقو الحين يا شباب 🏃‍♂️",
    "ما في وقت للتفكير يا رجال 🤔❌",
    "قرر الحين أو ندم بكرة يا أبطال 😢",
    "العرض على وشك الانتهاء يا شباب 🔥",
    "الكمية قليلة والوقت ينفد يا رجال ⚡️",
    "الحقو الفرصة الأخيرة يا أخوان 🎯",
    "ينتهي قبل ما تلحق يا شباب 🚨",
    "الوقت ما ينتظر أحد يا رجال ⏳",
    "العرض يروح بسرعة البرق يا أبطال ⚡️",
    "سعر خرافي صراحة يا شباب 🔥🔥",
    "ما شاء الله تبارك الله السعر حلو يا رجال 💥",
    "والله صفقة ما تتفوت يا أخوان 🎯",
    "عرض ناري وما يتكرر يا شباب 🔥🔥🔥",
    "الحين أو لا يا أبطال 💪💪",
    "ببلاش تقريباً يا رجال 😍🎉",
    "تخفيض مجنون يا شباب 👌👌",
    "صفقة العمر هذي يا أخوان 💯🏆",
    "الكمية قليلة جداً يا رجال ⚠️⚠️",
    "خذه فوراً يا شباب 💨💨",
    "هاته الحين قبل يروح يا أبطال 🏃‍♂️💨",
    "ما راح تلقى مثله يا رجال 👀👀",
    "سعر تاريخي يا شباب 📉🔥",
    "فرصة لا تعوض أبداً يا أخوان 💎💎",
    "احجز قبل الكل يا رجال 🏆🥇",
    "المنتج مطلوب جداً يا شباب 🔥🔥",
    "سعر جنوني يا أبطال 🤯",
    "صفقة مجنونة يا رجال 💥💥",
    "السعر كأنه غلطة يا شباب 😂",
    "هذا سعر ولا حلم يا رجال؟ 💭",
    "يا أخي الحقو يا رجال 🙏",
    "والله العظيم صفقة يا شباب 👌",
    "ما راح تندم أبداً يا أخوان 💯",
    "ثقة في الله واشتري يا رجال 🤲",
    "السعر يتكلم يا شباب 🔊",
    "جودة وسعر منافس يا أبطال 💪",
    "تبي تنتظر زيادة السعر يا رجال؟ 📈❌",
    "الحقو يا أهل الرياض يا شباب 🏙️",
    "يا أهل جدة الحقو يا رجال 🌊",
    "يا أهل مكة الحقو يا شباب 🕋",
    "يا أهل الشرقية الحقو يا رجال 🌅",
    "الحقو يا أهل السعودية يا أبطال 🇸🇦",
    "عرض للرجال الأوفياء 💚",
    "بسعر الجملة تقريباً يا شباب 💰",
    "أرخص من السوق بكثير يا رجال 📉",
    "توفير خرافي يا أبطال 💸",
    "وفر فلوسك يا شباب 💵",
    "استغل الفرصة يا بطل 🦸‍♂️",
    "الحقو يا صياد يا محترف 🎣",
    "صيدة الصيادين المحترفين يا رجال 🏆",
    "الكل يتكلم عنه يا شباب 📢",
    "المنتج رقم 1 مبيعاً يا رجال 🥇",
    "نفذ من المخزن مرتين يا أبطال 🔥",
    "الطلبات جاية من كل مكان يا شباب 📦",
    "المنتج الأشهر الحين يا رجال 🔝",
    "ترند السعودية يا شباب 🇸🇦🔥",
    "الكل يبغاه يا أخوان 😍",
    "الكمية نفذت مرة وردت بصعوبة يا رجال ⚠️",
    "المنتج اللي كله يدور عليه يا شباب 👀",
    "الحقو قبل ينفذ نهائياً يا رجال 🚫",
    "آخر فرصة للحصول عليه يا أبطال 🎯",
    "المنتج نادر في المخزون يا شباب 📉",
    "نفذ سريع في المرات السابقة يا رجال ⚡️",
    "الطلب مرتفع جداً يا شباب 📈",
    "الحقو قبل ما ينتهي المخزون يا رجال 🚨",
    "قرر الآن ولا تتردد يا أبطال ✅",
    "التردد خسارة يا شباب 💸",
    "الفرصة ما تنتظر يا رجال 🏃‍♂️",
    "الحقو ولا تفكر كثير يا أخوان 🤔❌",
    "اشتري الحين وارتح بالباقي يا شباب 😌",
    "السعر ما راح ينزل أكثر يا رجال 📉❌",
    "هذا أقل سعر ممكن يا أبطال 💯",
    "السعر الأخير يا شباب 🔚",
    "ما في أرخص من كذا يا رجال 👌",
    "العرض الأقوى يا أبطال 💪🔥",
    "صفقة القرن يا شباب 🌍",
    "الحقو يا صاحبي يا رجال 👊",
    "يا ولد الحقو 🏃‍♂️💨",
    "السعر يصرخ يا شباب 📢🔥",
    "فرصة العمر لا تفوتها يا رجال 🎯",
    "الحقو واستغل يا أبطال 🎣",
    "السعر يناديك يا شباب 📞💰",
    "المنتج ينتظرك يا رجال 🎁",
    "الحقو قبل الغيرك يا أبطال 🏃‍♂️🏃‍♂️",
    "السعر حقيقي ومو مزح يا شباب 💯",
]

# 💄 للنساء (ميكب، ملابس نسائية، عطور)
WOMEN_SENTENCES = [
    "والله صيدة صيدة يا بنات 🎣🔥",
    "صيدة العمر هذي يا حلوات 💯",
    "صيدة ما تتعوض يا بنات 🎯",
    "الحقو يا بنات قبل يروح 🏃‍♀️💨",
    "الحقو يا جماعة الخير ⚡️",
    "صيدة ذهبية يا حلوات 🏆",
    "فرصة صيد نادرة يا بنات 💎",
    "الحقو الفرصة ذي يا حلوات 👊",
    "صيدة السنة هذي يا بنات 🌟",
    "ما راح تلقى زيها أبداً يا حلوات 🚨",
    "صيدة تاريخية يا بنات 📉🔥",
    "الحقو قبل الكل يا حلوات 🏃‍♀️",
    "صيدة مجنونة يا بنات 🤯",
    "الحقو الحقو يا حلوات 💪",
    "صيدة العروض يا بنات 💰",
    "فرصة صيد ما تتكرر يا حلوات ⏰",
    "الحقو يا حبيبتي ⚠️",
    "صيدة فخمة يا بنات 👑",
    "الحقو الكمية محدودة جداً يا حلوات 🔥",
    "صيدة صيدة صيدة يا بنات 🎣🎣🎣",
    "ينتهي بأي لحظة يا بنات ⏰⚡️",
    "الوقت ينفد بسرعة يا حلوات ⏳🔥",
    "لا تنامي عليه يا بنات 🚨🚨",
    "ينتهي اليوم يا حلوات 🌙",
    "العرض ينتهي بسرعة يا بنات 💨",
    "فرصة لحظية يا حلوات ⚡️",
    "الحقو قبل ينتهي العرض يا بنات ⏰",
    "ينتهي خلال ساعات يا حلوات ⏳",
    "الوقت ضيق جداً يا بنات 🚨",
    "العرض محدود الوقت يا حلوات ⏰💥",
    "ينتهي بدون سابق إنذار يا بنات ⚠️",
    "الحقو الحين يا حلوات 🏃‍♀️",
    "ما في وقت للتفكير يا بنات 🤔❌",
    "قرري الحين أو ندمي بكرة يا حلوات 😢",
    "العرض على وشك الانتهاء يا بنات 🔥",
    "الكمية قليلة والوقت ينفد يا حلوات ⚡️",
    "الحقو الفرصة الأخيرة يا بنات 🎯",
    "ينتهي قبل ما تلحقين يا حلوات 🚨",
    "الوقت ما ينتظر أحد يا بنات ⏳",
    "العرض يروح بسرعة البرق يا حلوات ⚡️",
    "سعر خرافي صراحة يا بنات 🔥🔥",
    "ما شاء الله تبارك الله السعر حلو يا حلوات 💥",
    "والله صفقة ما تتفوت يا بنات 🎯",
    "عرض ناري وما يتكرر يا حلوات 🔥🔥🔥",
    "الحين أو لا يا بنات 💪💪",
    "ببلاش تقريباً يا حلوات 😍🎉",
    "تخفيض مجنون يا بنات 👌👌",
    "صفقة العمر هذي يا حلوات 💯🏆",
    "الكمية قليلة جداً يا بنات ⚠️⚠️",
    "خذيه فوراً يا حلوات 💨💨",
    "هايتيه الحين قبل يروح يا بنات 🏃‍♀️💨",
    "ما راح تلقين مثله يا حلوات 👀👀",
    "سعر تاريخي يا بنات 📉🔥",
    "فرصة لا تعوض أبداً يا حلوات 💎💎",
    "احجزي قبل الكل يا بنات 🏆🥇",
    "المنتج مطلوب جداً يا حلوات 🔥🔥",
    "سعر جنوني يا بنات 🤯",
    "صفقة مجنونة يا حلوات 💥💥",
    "السعر كأنه غلطة يا بنات 😂",
    "هذا سعر ولا حلم يا حلوات؟ 💭",
    "يا أختي الحقو يا بنات 🙏",
    "والله العظيم صفقة يا حلوات 👌",
    "ما راح تندمي أبداً يا بنات 💯",
    "ثقة في الله واشتري يا حلوات 🤲",
    "السعر يتكلم يا بنات 🔊",
    "جودة وسعر منافس يا حلوات 💪",
    "تبين تنتظرين زيادة السعر يا بنات؟ 📈❌",
    "الحقو يا أهل الرياض يا بنات 🏙️",
    "يا أهل جدة الحقو يا حلوات 🌊",
    "يا أهل مكة الحقو يا بنات 🕋",
    "يا أهل الشرقية الحقو يا حلوات 🌅",
    "الحقو يا أهل السعودية يا بنات 🇸🇦",
    "عرض للبنات الأوفياء 💚",
    "بسعر الجملة تقريباً يا حلوات 💰",
    "أرخص من السوق بكثير يا بنات 📉",
    "توفير خرافي يا حلوات 💸",
    "وفري فلوسك يا بنات 💵",
    "استغلي الفرصة يا حلوة 🦸‍♀️",
    "الحقو يا صيادة يا محترفة 🎣",
    "صيدة الصيادات المحترفات يا بنات 🏆",
    "الكل يتكلم عنه يا حلوات 📢",
    "المنتج رقم 1 مبيعاً يا بنات 🥇",
    "نفذ من المخزن مرتين يا حلوات 🔥",
    "الطلبات جاية من كل مكان يا بنات 📦",
    "المنتج الأشهر الحين يا حلوات 🔝",
    "ترند السعودية يا بنات 🇸🇦🔥",
    "الكل يبغاه يا حلوات 😍",
    "الكمية نفذت مرة وردت بصعوبة يا بنات ⚠️",
    "المنتج اللي كله يدور عليه يا حلوات 👀",
    "الحقو قبل ينفذ نهائياً يا بنات 🚫",
    "آخر فرصة للحصول عليه يا حلوات 🎯",
    "المنتج نادر في المخزون يا بنات 📉",
    "نفذ سريع في المرات السابقة يا حلوات ⚡️",
    "الطلب مرتفع جداً يا بنات 📈",
    "الحقو قبل ما ينتهي المخزون يا حلوات 🚨",
    "قرري الآن ولا تترددي يا حلوات ✅",
    "التردد خسارة يا بنات 💸",
    "الفرصة ما تنتظر يا حلوات 🏃‍♀️",
    "الحقو ولا تفكري كثير يا بنات 🤔❌",
    "اشتري الحين وارتحي بالباقي يا حلوات 😌",
    "السعر ما راح ينزل أكثر يا بنات 📉❌",
    "هذا أقل سعر ممكن يا حلوات 💯",
    "السعر الأخير يا بنات 🔚",
    "ما في أرخص من كذا يا حلوات 👌",
    "العرض الأقوى يا بنات 💪🔥",
    "صفقة القرن يا حلوات 🌍",
    "الحقو يا صاحبتي يا بنات 👊",
    "يا بنت الحقو 🏃‍♀️💨",
    "السعر يصرخ يا حلوات 📢🔥",
    "فرصة العمر لا تفوتيها يا بنات 🎯",
    "الحقو واستغلي يا حلوات 🎣",
    "السعر يناديك يا بنات 📞💰",
    "المنتج ينتظرك يا حلوات 🎁",
    "الحقو قبل الغيرك يا بنات 🏃‍♀️🏃‍♀️",
    "السعر حقيقي ومو مزح يا حلوات 💯",
]

# 🌟 للكل (محايد)
GENERAL_SENTENCES = [
    "والله صيدة صيدة 🎣🔥",
    "صيدة العمر هذي 💯",
    "صيدة ما تتعوض 🎯",
    "الحقو الحقو قبل يروح 🏃‍♂️💨",
    "الحقو يا جماعة الخير ⚡️",
    "صيدة ذهبية 🏆",
    "فرصة صيد نادرة 💎",
    "الحقو الفرصة ذي 👊",
    "صيدة السنة هذي 🌟",
    "ما راح تلقى زيها أبداً 🚨",
    "صيدة تاريخية 📉🔥",
    "الحقو قبل الكل 🏃‍♂️🏃‍♀️",
    "صيدة مجنونة 🤯",
    "الحقو الحقو يا شباب 💪",
    "صيدة العروض 💰",
    "فرصة صيد ما تتكرر ⏰",
    "الحقو يا ولد ⚠️",
    "صيدة فخمة 👑",
    "الحقو الكمية محدودة جداً 🔥",
    "صيدة صيدة صيدة 🎣🎣🎣",
    "ينتهي بأي لحظة ⏰⚡️",
    "الوقت ينفد بسرعة ⏳🔥",
    "لا تنام عليه 🚨🚨",
    "ينتهي اليوم 🌙",
    "العرض ينتهي بسرعة 💨",
    "فرصة لحظية ⚡️",
    "الحقو قبل ينتهي العرض ⏰",
    "ينتهي خلال ساعات ⏳",
    "الوقت ضيق جداً 🚨",
    "العرض محدود الوقت ⏰💥",
    "ينتهي بدون سابق إنذار ⚠️",
    "الحقو الحين 🏃‍♂️",
    "ما في وقت للتفكير 🤔❌",
    "قرر الحين أو ندم بكرة 😢",
    "العرض على وشك الانتهاء 🔥",
    "الكمية قليلة والوقت ينفد ⚡️",
    "الحقو الفرصة الأخيرة 🎯",
    "ينتهي قبل ما تلحق 🚨",
    "الوقت ما ينتظر أحد ⏳",
    "العرض يروح بسرعة البرق ⚡️",
    "سعر خرافي صراحة 🔥🔥",
    "ما شاء الله تبارك الله السعر حلو 💥",
    "والله صفقة ما تتفوت 🎯",
    "عرض ناري وما يتكرر 🔥🔥🔥",
    "الحين أو لا 💪💪",
    "ببلاش تقريباً 😍🎉",
    "تخفيض مجنون 👌👌",
    "صفقة العمر هذي 💯🏆",
    "الكمية قليلة جداً ⚠️⚠️",
    "خذه فوراً 💨💨",
    "هاته الحين قبل يروح 🏃‍♂️💨",
    "ما راح تلقى مثله 👀👀",
    "سعر تاريخي 📉🔥",
    "فرصة لا تعوض أبداً 💎💎",
    "احجز قبل الكل 🏆🥇",
    "المنتج مطلوب جداً 🔥🔥",
    "سعر جنوني 🤯",
    "صفقة مجنونة 💥💥",
    "السعر كأنه غلطة 😂",
    "هذا سعر ولا حلم؟ 💭",
    "يا أخي الحقو 🙏",
    "والله العظيم صفقة 👌",
    "ما راح تندم أبداً 💯",
    "ثقة في الله واشتري 🤲",
    "السعر يتكلم 🔊",
    "جودة وسعر منافس 💪",
    "تبي تنتظر زيادة السعر؟ 📈❌",
    "الحقو يا أهل الرياض 🏙️",
    "يا أهل جدة الحقو 🌊",
    "يا أهل مكة الحقو 🕋",
    "يا أهل الشرقية الحقو 🌅",
    "الحقو يا أهل السعودية 🇸🇦",
    "عرض للسعوديين الأوفياء 💚",
    "بسعر الجملة تقريباً 💰",
    "أرخص من السوق بكثير 📉",
    "توفير خرافي 💸",
    "وفر فلوسك 💵",
    "استغل الفرصة يا بطل 🦸‍♂️",
    "الحقو يا صياد 🎣",
    "صيدة الصيادين المحترفين 🏆",
    "الكل يتكلم عنه 📢",
    "المنتج رقم 1 مبيعاً 🥇",
    "نفذ من المخزن مرتين 🔥",
    "الطلبات جاية من كل مكان 📦",
    "المنتج الأشهر الحين 🔝",
    "ترند السعودية 🇸🇦🔥",
    "الكل يبغاه 😍",
    "الكمية نفذت مرة وردت بصعوبة ⚠️",
    "المنتج اللي كله يدور عليه 👀",
    "الحقو قبل ينفذ نهائياً 🚫",
    "آخر فرصة للحصول عليه 🎯",
    "المنتج نادر في المخزون 📉",
    "نفذ سريع في المرات السابقة ⚡️",
    "الطلب مرتفع جداً 📈",
    "الحقو قبل ما ينتهي المخزون 🚨",
    "قرر الآن ولا تتردد ✅",
    "التردد خسارة 💸",
    "الفرصة ما تنتظر 🏃‍♂️",
    "الحقو ولا تفكر كثير 🤔❌",
    "اشتري الحين وارتح بالباقي 😌",
    "السعر ما راح ينزل أكثر 📉❌",
    "هذا أقل سعر ممكن 💯",
    "السعر الأخير 🔚",
    "ما في أرخص من كذا 👌",
    "العرض الأقوى 💪🔥",
    "صفقة القرن 🌍",
    "الحقو يا صاحبي 👊",
    "يا ولد الحقو 🏃‍♂️💨",
    "السعر يصرخ 📢🔥",
    "فرصة العمر لا تفوتها 🎯",
    "الحقو واستغل 🎣",
    "السعر يناديك 📞💰",
    "المنتج ينتظرك 🎁",
    "الحقو قبل الغيرك 🏃‍♂️🏃‍♂️",
    "السعر حقيقي ومو مزح 💯",
]

# كلمات تحدد نوع المنتج
WOMEN_KEYWORDS = [
    # ميكب وعناية
    "makeup", "lipstick", "mascara", "eyeliner", "foundation", "concealer", "blush", 
    "eyeshadow", "makeup", "ميكب", "ميك أب", "أحمر شفاه", "روج", "ماسكرا", "ايلاينر", 
    "فاونديشن", "كونسيلر", "بلشر", "ظلال عيون", "مناكير", "nail polish", "lip gloss",
    "primer", "setting spray", "highlighter", "bronzer", "contour", "makeup brush",
    "beauty blender", "face mask", "skincare", "moisturizer", "serum", "toner",
    "makeup remover", "facial", "eye cream", "anti-aging", "lip balm", "body lotion",
    "shower gel", "body wash", "perfume", "عطر", "parfum", "eau de", "fragrance",
    "hair dryer", "straightener", "curler", "hair tool", "blow dryer", "styling",
    
    # ملابس نسائية
    "dress", "فستان", "skirt", "تنورة", "blouse", "بلوزة", "bra", "حمالة صدر", 
    "lingerie", "لانجري", "nightgown", "قميص نوم", "panties", "سروال", "tights", 
    "stockings", "جوارب", "leggings", "ليقنز", "yoga pants", "scarf", "وشاح", 
    "hijab", "حجاب", "abaya", "عباية", "kimono", "cardigan", "كارديجان", "tunic", 
    "تونيك", "maxi dress", "midi dress", "party dress", "evening dress", "wedding dress",
    "gown", "prom dress", "cocktail dress", "summer dress", "floral dress",
    "handbag", "purse", "clutch", "tote bag", "shoulder bag", "crossbody", "شنطة",
    "jewelry", "مجوهرات", "necklace", "عقد", "earrings", "اقراط", "bracelet", "سوار",
    "ring", "خاتم", "watch", "ساعة", "sunglasses", "نظارة شمسية", "accessories",
    "hair accessory", "اكسسوار شعر", "belt", "حزام", "wallet", "محفظة",
    
    # أحذية نسائية
    "heels", "كعب", "high heels", "كعب عالي", "pumps", "sandals", "صندل", "flats",
    "ballet flats", "ballerina", "wedge", "platform", "ankle boots", "knee high",
    "over the knee", "booties", "stiletto", "block heel", "wedding shoes",
    
    # عناية بالشعر والبشرة
    "shampoo", "conditioner", "hair mask", "hair oil", "hair serum", "dry shampoo",
    "hairspray", "mousse", "hair gel", "wax", "cream", "lotion", "body butter",
    "scrub", "exfoliator", "cleanser", "face wash", "sunscreen", "spf",
    "lip care", "hand cream", "foot cream", "eye serum", "face oil", "essence",
    
    # أدوات تجميل
    "curling iron", "flat iron", "hair straightener", "crimper", "hot brush",
    "epilator", "razor", "shaver", "trimmer", "tweezers", "mirror", "vanity",
    "makeup organizer", "jewelry box", "cosmetic bag", "toiletry bag",
]

MEN_KEYWORDS = [
    # ملابس رجالية
    "men", "رجالي", "male", "for men", "mens", "man's", "للرجال", "للرجل",
    "shirt", "قميص", "polo", "polo shirt", "t-shirt", "تيشيرت", "henley",
    "jeans", "جينز", "trousers", "بنطلون", "pants", "slacks", "chinos",
    "shorts", "شورت", "cargo shorts", "bermuda", "boxer", "بوكسر", "briefs",
    "undershirt", "فانلة", "singlet", "tank top", "vest", "سترة", "waistcoat",
    "suit", "بدلة", "blazer", "جاكيت رسمي", "tuxedo", "smoking", "formal wear",
    "tie", "ربطة عنق", "bow tie", "فيونكة", "cufflinks", "كبك", "belt", "حزام رجالي",
    "suspenders", "حمالات", "socks", "شرابات", "gloves", "قفازات", "scarf", "وشاح رجالي",
    "cap", "كاب", "hat", "قبعة", "baseball cap", "snapback", "fedora", "beanie",
    "jacket", "جاكيت", "bomber jacket", "leather jacket", "denim jacket", "parka",
    "coat", "معطف", "overcoat", "trench coat", "raincoat", "windbreaker", "fleece",
    "hoodie", "هودي", "sweatshirt", "سويت شيرت", "sweater", "سترة صوف", "pullover",
    "cardigan", "كارديجان رجالي", "turtleneck", "polo neck", "crew neck", "v-neck",
    
    # أحذية رجالية
    "shoes", "حذاء", "shoe", "formal shoes", "dress shoes", "oxford", "loafer",
    "derby", "brogue", "monk strap", "boots", "بوت", "chelsea boots", "combat boots",
    "work boots", "hiking boots", "timberland", "sneakers", "حذاء رياضي", "running shoes",
    "athletic shoes", "trainers", "tennis shoes", "basketball shoes", "football boots",
    "sandals", "صندل رجالي", "flip flops", "شبشب", "slippers", "نعال", "espadrilles",
    "boat shoes", "moccasin", "suede shoes", "leather shoes", "canvas shoes",
    
    # إكسسوارات رجالية
    "watch", "ساعة رجالية", "wristwatch", "chronograph", "automatic watch", "diver watch",
    "sunglasses", "نظارة شمسية رجالية", "aviator", "wayfarer", "clubmaster",
    "wallet", "محفظة رجالية", "card holder", "حامل بطاقات", "money clip", "keychain",
    "ring", "خاتم رجالي", "tie clip", "دبوس ربطة", "lapel pin", "badge",
    "backpack", "حقيبة ظهر", "messenger bag", "briefcase", "حقيبة عمل", "duffle bag",
    "gym bag", "travel bag", "toiletry bag", "شنطة رجالية",
    
    # عطور رجالية
    "cologne", "كولونيا", "aftershave", "افتر شيف", "oud", "عود رجالي", "musk", "مسك",
    "eau de toilette", "eau de parfum", "fragrance men", "perfume men", "عطر رجالي",
    "amber", "woody", "spicy", "fresh", "citrus", "oriental", "leather scent",
    
    # أدوات رجالية
    "trimmer", "مقص شعر", "hair clipper", " shaver", "ماكينة حلاقة", "razor", "شفرة",
    "beard trimmer", "مقص ذقن", "grooming kit", "shaving kit", "straight razor",
    "beard oil", "balm", "wax", "mustache", "شوارب", "beard", "ذقن", "goatee",
    
    # رياضة رجالية
    "gym", "جيم", "fitness", "لياقة", "workout", "تمرين", "training", "تدريب",
    "sportswear", "ملابس رياضية", "activewear", "compression", "ضغط", "base layer",
    "jersey", "فانلة رياضية", "kit", "uniform", "رياضة", "sports", "football", "كرة قدم",
    "basketball", "كرة سلة", "tennis", "تنس", "running", "جري", "cycling", "دراجات",
    "swimming", "سباحة", "boxing", "ملاكمة", "mma", "martial arts", "فنون قتالية",
    "golf", "تنس أرضي", "cricket", "كريكت", "rugby", "هوكي", "hockey",
    
    # معدات رجالية
    "tool", "أداة", "tools", "أدوات", "drill", "مثقاب", "saw", "منشار", "hammer",
    "مطرقة", "screwdriver", "مفك", "wrench", "مفتاح", "pliers", "كماشة", "toolbox",
    "camping", "تخييم", "hiking", "تسلق", "fishing", "صيد", "hunting", "قنص",
    "outdoor", "خارجي", "adventure", "مغامرة", "survival", "بقاء", "tactical", "تكتيكي",
]

def detect_audience(title):
    """
    يحدد الجمهور المستهدف من عنوان المنتج
    """
    title_lower = title.lower()
    
    # نحسب عدد الكلمات النسائية vs الرجالية
    women_count = sum(1 for word in WOMEN_KEYWORDS if word.lower() in title_lower)
    men_count = sum(1 for word in MEN_KEYWORDS if word.lower() in title_lower)
    
    if women_count > men_count:
        return "women"
    elif men_count > women_count:
        return "men"
    else:
        return "general"

def get_opening_sentence(audience):
    """
    يختار جملة افتتاحية حسب الجمهور
    """
    if audience == "women":
        return random.choice(WOMEN_SENTENCES)
    elif audience == "men":
        return random.choice(MEN_SENTENCES)
    else:
        return random.choice(GENERAL_SENTENCES)

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
    # نترك العنوان كامل ما نقطعه
    arabic_title = translate_to_arabic(full_title)
    
    # نحذف التكرار في الكلمات المتتالية فقط
    words = arabic_title.split()
    unique_words = []
    for word in words:
        if not unique_words or word.lower() != unique_words[-1].lower():
            unique_words.append(word)
    
    result = " ".join(unique_words)
    
    # لو طويل جداً نختصره بذكاء
    if len(result) > 100:
        # نبحث عن فاصلة أو شرطة نختصر عندها
        for sep in ['،', ',', '-', '|', '/']:
            if sep in result[:100]:
                idx = result.rfind(sep, 50, 100)
                if idx > 0:
                    result = result[:idx]
                    break
        else:
            # لو ما لقينا فاصل، نختصر عند آخر مسافة
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
# 💰 تنظيف السعر - بدون نقاط ولا هللات
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
                # نحدد الجمهور من العنوان الأصلي
                audience = detect_audience(full_title)
                return arabic_title, price, old_price, image, discount_percent, audience
                  
        except Exception as e:  
            print(f"Attempt {attempt + 1} failed: {e}")  
            continue  
  
    return None

# ===================================
# ✨ التوليد النهائي - عشوائي حسب الجمهور
# ===================================

def generate_post(product_name, price, old_price, discount_percent, original_url, audience):
    # ✅ اختيار جملة عشوائية حسب الجمهور
    opening = get_opening_sentence(audience)

    clean_current = clean_price(price)  
    clean_old = clean_price(old_price) if old_price else None  
  
    lines = [opening]  
    lines.append("")  
    lines.append(f"🛒 {product_name}")  
    lines.append("")  
  
    if clean_old and discount_percent and discount_percent > 5:  
        lines.append(f"❌ قبل: {clean_old}")  
        lines.append(f"✅ الحين: {clean_current} (وفر {discount_percent}%)")  
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
        bot.reply_to(msg, "❌ أرسل رابط منتج")  
        return  

    for original_url in urls:  
        expanded = expand_url(original_url)  

        if not is_saudi_amazon(expanded):  
            bot.reply_to(msg, "❌ الرابط لازم يكون من amazon.sa")  
            continue  

        asin = extract_asin(expanded)  
        if not asin:  
            bot.reply_to(msg, "❌ ما قدرت أستخرج رقم المنتج")  
            continue  

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")  

        product = get_product(asin)  

        if not product:  
            bot.edit_message_text("❌ ما قدرت أقرأ المنتج", msg.chat.id, wait.message_id)  
            continue  

        product_name, price, old_price, image, discount_percent, audience = product  
        post = generate_post(product_name, price, old_price, discount_percent, original_url, audience)  

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
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت يعمل...")
bot.infinity_polling()
