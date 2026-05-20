import telebot, requests, re, time, json, random
from bs4 import BeautifulSoup

TOKEN = "7956075348:AAEYTL28GKeMN7TXyVeGM69iUcfg5ZwOSIk"
bot = telebot.TeleBot(TOKEN)
GROQ_API_KEY = "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"

BRAND_NAMES = {
    "nespresso": "Nespresso", "nescafe": "Nescafe", "nescafe": "Nescafe",
    "iphone": "iPhone", "ipad": "iPad", "macbook": "MacBook", "airpods": "AirPods",
    "samsung": "Samsung", "sony": "Sony", "lg": "LG", "dyson": "Dyson",
    "philips": "Philips", "bosch": "Bosch", "adidas": "Adidas", "nike": "Nike",
    "puma": "Puma", "gucci": "Gucci", "prada": "Prada", "dior": "Dior",
    "chanel": "Chanel", "loreal": "L'Oreal", "loreal": "L'Oreal", "loreal": "L'Oreal"
}

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "laptop", "ipad", "airpods", "headphones", "camera", "tv", "screen", "watch", "speaker", "router"],
    "fashion": ["shirt", "pants", "jeans", "jacket", "dress", "shoes", "sneakers", "boots", "bag", "wallet", "belt"],
    "beauty": ["perfume", "cream", "shampoo", "makeup", "lipstick", "serum", "oud"],
    "home": ["fridge", "washing", "vacuum", "ac", "heater", "blender", "oven", "sofa", "bed", "lamp"],
    "sports": ["treadmill", "dumbbell", "yoga", "bicycle", "gym", "fitness"]
}

def protect_brands(t):
    for k, v in sorted(BRAND_NAMES.items(), key=lambda x: -len(x[0])):
        t = re.compile(re.escape(k), re.I).sub(v, t)
    return t

def detect_category(n):
    n = n.lower()
    for c, kws in CATEGORY_KEYWORDS.items():
        if any(k in n for k in kws):
            return c
    return "general"

def detect_gender(n):
    n = n.lower()
    if any(w in n for w in ['women', 'lady', 'female', 'nsay', 'fstan', 'dress', 'skirt', 'makeup', 'lipstick']):
        return 'women'
    if any(w in n for w in ['men', 'male', 'rjaly', 'atr rjaly']):
        return 'men'
    return 'neutral'

def get_emoji(c):
    return {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}.get(c, "📦")

# ========== Support all Amazon domains + affiliate links ==========

def is_amazon_link(url):
    amazon_domains = [
        'amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.it', 'amazon.es',
        'amazon.ca', 'amazon.com.au', 'amazon.in', 'amazon.jp', 'amazon.cn',
        'amazon.sa', 'amazon.ae', 'amazon.com.tr', 'amazon.com.br', 'amazon.com.mx',
        'amzn.to', 'amzn.com', 'a.co', 'z.cn'
    ]
    url_lower = url.lower()
    return any(domain in url_lower for domain in amazon_domains)

def resolve_amazon_url(url):
    short_domains = ['amzn.to', 'a.co']
    if any(domain in url.lower() for domain in short_domains):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            resp = requests.head(url, headers=headers, allow_redirects=True, timeout=15)
            if resp.status_code in [200, 301, 302] and resp.url != url:
                return resp.url
        except Exception as e:
            print(f"Redirect error: {e}")
    return url

def get_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/([A-Z0-9]{10})/?$',
        r'[?&]asin=([A-Z0-9]{10})',
        r'[?&]dp=([A-Z0-9]{10})',
        r'[?&]productId=([A-Z0-9]{10})',
        r'%2Fdp%2F([A-Z0-9]{10})',
        r'[?&]url=.*%2Fdp%2F([A-Z0-9]{10})',
    ]
    for p in patterns:
        m = re.search(p, url, re.I)
        if m:
            return m.group(1)
    return None

def get_amazon_domain(url):
    m = re.search(r'(amazon\.[a-z.]+)', url.lower())
    if m:
        return m.group(1)
    return "amazon.com"

# ========== END ==========

def clean_price(t):
    try:
        n = re.findall(r'[\d,]+(?:\.\d+)?', t)[0].replace(",", "")
        return f"{int(float(n))} ryl"
    except:
        return t

def extract_num(t):
    try:
        return float(re.findall(r'[\d,]+(?:\.\d+)?', t)[0].replace(",", ""))
    except:
        return 0

def get_image(soup):
    img = soup.select_one("#landingImage")
    if img:
        url = img.get("data-old-hires") or img.get("src")
        if not url:
            try:
                d = json.loads(img.get("data-a-dynamic-image", "{}"))
                url = sorted(d.keys(), key=lambda x: d[x][0]*d[x][1], reverse=True)[0] if d else None
            except:
                pass
        if url:
            return re.sub(r'_SX\d+_SY\d+_|_SX\d+_|_SY\d+_|_CR\d+,\d+,\d+,\d+_|_AC_SL\d+_|_SCLZZZZZZZ_|_FMwebp_|_QL\d+_', '_', url).split('?')[0]
    og = soup.select_one('meta[property="og:image"]')
    return og.get("content") if og else None

def get_seller(soup):
    for sel in ["#merchant-info a", "[data-feature-name='merchant'] a", "#merchant-info"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if len(t) > 2:
                return t
    return None

def get_rating(soup):
    r = soup.select_one("#acrPopover .a-icon-alt") or soup.select_one("[data-hook='rating-out-of-text']")
    rating = re.search(r'([\d.]+)', r.get_text(strip=True)).group(1) if r else None
    rc = soup.select_one("#acrCustomerReviewText") or soup.select_one("[data-hook='total-review-count']")
    reviews = re.search(r'([\d,]+)', rc.get_text(strip=True)).group(1).replace(",", "") if rc else None
    return rating, reviews

def get_stock(soup):
    for sel in ["#availability span", ".a-color-price.a-text-bold", "#outOfStock"]:
        el = soup.select_one(sel)
        if el and any(w in el.get_text(strip=True).lower() for w in ['left', 'mtbq', 'stock', 'soon', 'limited', 'only']):
            return el.get_text(strip=True)
    return None

def get_coupons(soup, price):
    found = []
    for sel in ["#couponTextInput", "[data-feature-name='coupon']", ".couponText", "#couponContainer", ".savingsPercentage"]:
        for el in soup.select(sel):
            txt = el.get_text(strip=True)
            if len(txt) > 3:
                p = re.search(r'(\d+)%', txt)
                if p:
                    pct = int(p.group(1))
                    code = re.search(r'\b([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z]{4,})\b', txt)
                    code = code.group(1) if code else f"khsom {pct}%"
                    found.append({"code": code, "percent": pct, "final_price": int(price - price * pct / 100), "text": txt})
    seen = {}
    uniq = []
    for c in found:
        k = c["code"].upper()
        if k not in seen:
            seen[k] = True
            uniq.append(c)
    uniq.sort(key=lambda x: x["percent"], reverse=True)
    return uniq

def get_product(asin, domain="amazon.sa"):
    url = f"https://www.{domain}/dp/{asin}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
    ]
    for ua in user_agents:
        try:
            r = requests.get(url, headers={
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Referer": "https://www.google.com/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }, timeout=30)
            if r.status_code != 200 or len(r.text) < 5000:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            if not title:
                continue
            full = title.text.strip()
            price = None
            for sel in [".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen", ".a-price .a-offscreen", ".a-price-whole"]:
                el = soup.select_one(sel)
                if el and el.text and any(c.isdigit() for c in el.text):
                    price = el.text.strip()
                    break
            if not price:
                continue
            old = None
            for sel in [".a-price.a-text-price[data-a-color='secondary'] .a-offscreen", ".basisPrice .a-offscreen"]:
                el = soup.select_one(sel)
                if el and el.text != price and any(c.isdigit() for c in el.text):
                    old = el.text.strip()
                    break
            img = get_image(soup)
            seller = get_seller(soup)
            rating, reviews = get_rating(soup)
            stock = get_stock(soup)
            cur = extract_num(price)
            coupons = get_coupons(soup, cur)
            return {
                "name": protect_brands(full[:80]),
                "full_title": full,
                "price": price,
                "old_price": old,
                "image": img,
                "seller": seller,
                "rating": rating,
                "reviews": reviews,
                "stock": stock,
                "coupons": coupons,
                "current_num": cur,
                "domain": domain
            }
        except Exception as e:
            print(f"Error: {e}")
    return None

# ========== 100 UNIQUE HEADLINES WITH ANTI-REPETITION ==========

_used_headlines = {}

HEADLINES = {
    "electronics": [
        "✨ mn byn alaf alkhyarat, halSfqh tbrq wtlmA — sAr **{price}** yKlyk ttWqf wtfkr: wsh ymnAk alHyn? 🔥",
        "🌟 yA hlA bAlSfqh alty tstAhl kl thanyH tfkyr — **{discount}%** khsom Hqyqy 💎",
        "⚡️ tqnyH bmwSfAt Alyh w sAr **{price}** mAqwl — nAdr tlqA mthlh 🎯",
        "🔥 frSH mA ttkrr — jhAz bA **{price}** ystAhl kl qrsh fyh 🚀",
        "💡 dkA' alakhtyAr fy altwqyt — w alHyn ySrK: ashtry! **{discount}%** khsom ⚡️",
        "📱 jhAz yGyr TryqH HyAtk b sAr **{price}** — wsh tntZr? 🌟",
        "🎯 SfqH alywm: tknwlwjyA mtqdmH b sAr yfAjAk — **{price}** bs! 🔥",
        "💎 jwdH TSnyA AlmAlyH w sAr mHly — **{price}** ystAhl alahthAm ⚡️",
        "🚀 tknwlwjyA almstqbl byn ydyk alywm bA **{price}** — lA tfwthA! 💫",
        "⚡️ sArAH, adA', w mwthwqyH — klhA fy SfqH bA **{price}** 🎯",
        "🔋 bTaryH tdwm mAk w khsom **{discount}%** ydwm fy dhAkrtk 💪",
        "🎮 adA' aHtrafy b sAr Ady — **{price}** yGyr almAadlH 🏆",
        "📸 lHmAt ystAhl tWthq b jwdH Alyh w sAr **{price}** ystAhl yshtry 🌟",
        "🎧 Swt nqy kAnk fy alAstwdyw — w al sAr? **{price}** bs! 🎵",
        "💻 shAshH wAdHA w adA' sls — kl hthA bA **{price}** ySdmk 🔥",
        "📡 sArAH atSAl tKlyk mtqdm — w khsom **{discount}%** tKlyk fAyZ ⚡️",
        "🔌 jhAz yshrjn HyAtk b alAntAjyH — b sAr **{price}** yshrjn mHfZtk b altwfyryr 💡",
        "🖥️ shAshH Ard bAlwAn HyH — w sAr **{price}** yAtk HyH thanyH 🌈",
        "⌚ sAH dhkyH tTAbA SHtk — w khsom **{discount}%** tTAbA myzAnytk 💚",
        "🎤 Swtk ystAhl ynsmA b wDwH — w hAlmAyik bA **{price}** ywSlh 🎙️",
        "📶 wAy fAy sryA yGhY kl albyt — b sAr **{price}** yGhY kl twqyAtk 🏠",
        "🖱️ dqH tHkm tfrq fy allAb w alshGl — **{price}** tfrq fy myzAnytk 🎮",
        "🔊 mkbr Swt ymlA alGurfH — w sAr **{price}** ymlA qlbk frH 😊",
        "📞 mkAlmAt wAdHA kAnkm wjh l wjh — bA **{price}** tstAhl altjrbH 📱",
        "🌐 Almkm alrQmy ybdA b jhAz qwY — w **{price}** ybdA rHlH altwfyryr 🌍"
    ],
    "fashion_men": [
        "👔 AnqH rjAlyH b thqH — hAlTqm bA **{price}** ymnHk alAthnyn 🔥",
        "🕶️ Tl~t tfrD aHtrAmk — b sAr **{price}** yfrD tqdyrk 💎",
        "⌚ wqtk thmyn — w sAHtk bA **{price}** tstAhlh ⚡️",
        "👟 hthA' yrkD bk l alahdAf — w sAr **{price}** yrkD b altwfyryr 🌟",
        "🧥 jAkyt shtwy b KfH sAr — **{price}** mA **{discount}%** ydfy alqlb 🔥",
        "👕 tyshrt yAks shKsytk — bA **{price}** yAks dkA' akhtyArk 😎",
        "🎩 qbhH tkml ATlAltk — w sAr **{price}** tkml frHtH 🎩",
        "👖 bnTlwn yjls mthAly — w khsom **{discount}%** yjls mthAly fy almyzAnyH 💰",
        "🧣 wshAH ydfy w yzyn — bA **{price}** ydfy qlbk mn albrd w alGlA' ❄️",
        "👔 qmYsh klAsyky ynAsb kl mnAsbH — **{price}** ynAsb kl myzAnyH 🎯",
        "🥾 bwt shtwy ythml kl shy — w sAr **{price}** ythml kl myzAnyH 🏔️",
        "🧤 qfAzAt AnyqH w dAfytH — bA **{price}** tdfy ydyk w mHfZtk 🧤",
        "👞 hthA' rsmY ythbt dhwqk — w khsom **{discount}%** ythbt dkA'k 👔",
        "🎒 Hqybt Zhr AmlyH w AnyqH — **{price}** yjmA alAthnyn b dkA' 🎒",
        "🕶️ nZArH shmsyH tHmy Aynk — w tsAr **{price}** tHmy myzAnytk ☀️",
        "🧦 jwArb mryHtH w TwylH alAumr — bA **{price}** tstAhl al stwk kAmel 🧦",
        "🎽 strH ryAdyH KfyfH — w sAr **{price}** ythql mHfZtk b altwfyryr 🏃",
        "👔 krftH tfrq fy Tltk — **{price}** tfrq fy ywmk 🎀",
        "🧥 mATf Anyq l almnAsbAt — w khsom **{discount}%** Anyq l almyzAnyH 🎩",
        "👟 snykrs Asry ynAsb kl shy — bA **{price}** ynAsb kl myzAnyH 👟",
        "🎩 Tqm kAmel b sAr jzA' — **{price}** yKlyk tTA bAql tkflH wAAlA AnqH 💼",
        "🧢 kAb ryAdyH bAlwAn mtAddH — w sAr **{price}** yKlyk tAkhZ Akthr mn wAHd 🧢",
        "👖 jynz ythml alGsylyl w alAstkhdAm — **{price}** ythml alAstkhdAm alywmy 💪",
        "🎽 mlAbis dAkhlyH mryHtH — bA **{price}** tryH jsmk w mHfZtk 🩲",
        "👔 bdltH kAmH tlbsH l alArs — w khsom **{discount}%** yKlyk tfrH qbl alArs 🤵"
    ],
    "fashion_women": [
        "👗 fstAn yHky qSSH — bA **{price}** yHky dkA' akhtyArk 🔥",
        "👜 shnTtH tkml ATlAltk — w sAr **{price}** tkml frHtH 💎",
        "💄 mkAyG yzyn wjhHk — w sAr **{price}** yzyn ywmk ⚡️",
        "👠 kAb yrfAk fwq — w sAr **{price}** yrfAk AAlA 🌟",
        "🧕 AbAyH tstirk w tzyink — bA **{price}** tstir myzAnytk 🔥",
        "💍 aksywAr ylmA zy Aynk — lmA tshwfyyn **{price}** ✨",
        "🌸 Atr nAm yfHw bAryjk — w sAr **{price}** yfHw b al dkA' 🌺",
        "👡 Sndl Sfyfy mryH — w khsom **{discount}%** ybrd qlbk ☀️",
        "🎀 wshAH Hryry ylf jmAl — bA **{price}** ylf myzAnytk b altwfyryr 🧣",
        "💅 TlA' AZAfir blwnk almfDl — **{price}** yKlyk tAkhdyyn kl alAlwAn 💅",
        "👘 blwzyH AnyqH l aldwm — w sAr **{price}** AnyqH l almyzAnyH 👚",
        "🧥 kArdyGn dAfy w nAm — bA **{price}** ydfy qlbk mn albrd 🧶",
        "👖 bnTlwn jynz ybrz rshAqtik — w khsom **{discount}%** ybrz dkA'k 👖",
        "👛 mHfZH SgyrH w AnyqH — **{price}** tHfZ flwsk w bAnqH 💰",
        "🎀 rbtH shAr tzyin ywmk — bA **{price}** tzyin myzAnytk 🎀",
        "👗 fstAn sHrH yKHtf alAnZAr — w sAr **{price}** yKHtf qlbk mn alfrH 💃",
        "🥿 hthA' msTtH mryH l almshy — **{price}** yryH rjlk w mHfZtk 🥿",
        "🧣 shAl kshmyry fAKhr — w khsom **{discount}%** yKlyk tHsyyn b al fKHAmH 🧣",
        "👙 lAnjry Anyq w mryH — bA **{price}** tstAhlHyn alrAHtH w alAnqH 💕",
        "🎩 qbhH shmsyH tHmy bshrHk — w sAr **{price}** tHmy myzAnytk 🌞",
        "👗 tnwrH tnAsb kl almnAsbAt — **{price}** tnAsb kl myzAnyH 👗",
        "💎 mjwhrAt bSyTpH w AnyqH — bA **{price}** tlmyHyn bdwA mA tkthrHyn 💎",
        "🧥 jAkyt jld yDyd l Tltk — w khsom **{discount}%** yDyd l frHtHk 🖤",
        "👠 kAb Aaly yKlyk tsyTrHyn — **{price}** yKlyk tsyTrHyn AlA almyzAnyH 👑",
        "🎀 Tqm kAmel l alKrwj — bA **{price}** tTAyn bAql tkflH wAAlA AnqH 💃"
    ],
    "beauty_men": [
        "🧔 rjl mhtm b nZAfH — hAlmntj bA **{price}** yhtm b myzAnytk 🔥",
        "💈 HlAqH nZyftH b mntj nZyf — w sAr **{price}** ynZf alGlA' 💎",
        "👔 Atr ythbt HDwrk — b sAr **{price}** ythbt dkA'k ⚡️",
        "🧴 lwjn ytrTb bshrHk — w sAr **{price}** ytrTb qlbk 🌟",
        "🪒 mAkyH tfsilk An albAht — w sAr **{price}** yfsilk An albAhZ 🔥",
        "🧼 Gsl wjh yAtk nZArH — **{price}** yAtk twfyr Hqyqy ✨",
        "💇‍♂️ shAmpw ywqf altshAqT — w khsom **{discount}%** ywqf alqlq 🚿",
        "🧴 krym HlAqH nAm — bA **{price}** yHmy bshrHk w mHfZtk 🪒",
        "🌿 zyt lHyH yGzyhA — w sAr **{price}** yGzy myzAnytk b altwfyryr 🌿",
        "🧽 AsfjnH AstHmAm TbyAH — **{price}** tstAhl alAstbdAl aldA'ym 🧽",
        "💪 mzyl Arq ydwm 48 sAH — w khsom **{discount}%** ydwm fy dhAkrtk 💪",
        "🧴 wAqy shms yHmyk — bA **{price}** yHmy bshrHk mn alHrwq w alGlA' ☀️",
        "🎩 jl shAr ythbt tsryHtHk — **{price}** ythbt qrr alshryA' 💇‍♂️",
        "🧼 SAbwnH TbyAH l alwjh — w sAr **{price}** TbyAy w mAqwl 🧼",
        "💈 frshH HlAqH aHtrafyH — bA **{price}** tfrq fy alntyjH 🪒",
        "🧴 syrym yAlyj altjAyd — w khsom **{discount}%** yAlyj alqlq mn al sAr 🧬",
        "🌊 bKHAK mlH bHrY l alshAr — **{price}** yAtk lwK alshATy bdwA sfr 🏖️",
        "🧴 mqshsh l alwjh yjdyd KHlAtk — bA **{price}** yjdyd thqtik bnfsik 🧴",
        "💈 zyt HlAqH klAsyky — w sAr **{price}** klAsyky w mwthwq 🎩",
        "🧼 Gsl l aljsm brAyHtH mnAsh — **{price}** ybdl ywmk 180 drjH 🚿",
        "🧴 mrTb shfAH ydwm — w khsom **{discount}%** ydwm fy jybk 💋",
        "🪒 shfrAt HlAqH dqyqH — bA **{price}** tHllq al sAr mA al shAr 🪒",
        "🧴 twnr l alwjh ywAzn — w sAr **{price}** ywAzn myzAnytk ⚖️",
        "💈 krym TSyf yAty lmA' — **{price}** yAty lmA' l alSfqH 💫",
        "🧴 mjmwAAt AnAyH kAmH — bA **{price}** tbdA rHlH alAnAyH al dhkyH 🧴"
    ],
    "beauty_women": [
        "💅 TlA' ylmA zy Aynk — lmA tshwfyyn **{price}** ⚡️",
        "🧖‍♀️ krym yKlyk ttAmlHyn — bmra'tk w mHfZtk bA **{price}** 🌟",
        "💋 AHmr shfAH bA **{price}**? — yA lyt kl alqrrAt alHwlyH tjy kthA 🔥",
        "🌸 Atr yfHw bAryj alAnqH — w sAr **{price}** yfHw b al dkA' 💎",
        "✨ syrym ybrq wjhk — w sAr **{price}** ybrq ywmk ⚡️",
        "🧴 Gsl yAtyk bshrH SAfytH — **{price}** yAtyk twfyr SAfy 🧼",
        "💄 mAskArA tTwyl rmwshk — w khsom **{discount}%** tTwyl frHtHk 👁️",
        "🌺 bwdrtH thbt almkAyG — bA **{price}** thbt qrr alshryA' 💨",
        "🧴 mrTb lylY yjdyd bshrHk — w sAr **{price}** yjdyd thqtik 🌙",
        "💅 mnAkryr jl ydwm asAbYH — **{price}** ydwm fy dhAkrtk kSfqH HwlyH 💅",
        "🧴 zyt ArGAn l alshAr — bA **{price}** yGzy shArk w ywfr flwsk 🌿",
        "💄 kntwr yHdd mlAmHk — w khsom **{discount}%** yHdd dkA' akhtyArk 🎨",
        "🧴 Gsl fwmy nAm — **{price}** ynZf wjhk mn alshaw'yb w alGlA' 🫧",
        "🌹 mA' wrd TbyAy — bA **{price}** ynAsh bshrHk w ywmk 🌹",
        "💋 lyb lyynr yAty Hgm — w sAr **{price}** yAty qymH HqyqyH 💋",
        "🧴 krym Aywn yKfy alhAlAt — **{price}** yKfy alqlq mn al sAr 👁️",
        "✨ hAylAytwr yAty twhj — bA **{price}** yAty twhj l alSfqH ✨",
        "🧴 shAmpw bdwA slfAt — w khsom **{discount}%** bdwA qlq 🚿",
        "💄 bAlm shfAH wrdy — **{price}** yrtb shfAyfk w ywmk 🌸",
        "🧴 skrAb l aljsm yjdydh — bA **{price}** yjdyd rwtyn alAnAyH 🧴",
        "🌺 Atr zhry nAm — w sAr **{price}** nAm AlA almyzAnyH 🌸",
        "💅 TlA' AZAfir jl — **{price}** yKlyk tswyn SAlwn fy albyt 💅",
        "🧴 krym AsAs yGhY Aywb — bA **{price}** yGhY kl twqyAtk 🎭",
        "✨ rmwsh SnAyAH TbyAyH — w khsom **{discount}%** ybdw TbyAy w mnTqy 👁️",
        "🧴 mjmwAAt mkAyG kAmH — **{price}** tbdAyn rHlH aljmAl al dhkiH 💄"
    ],
    "home": [
        "🏠 byt yAks dhwqk — ybdA bA **{price}** yAks dkA'k 🔥",
        "🛋️ Athy ystqbl Dywfk — bkrAmH w sAr **{price}** btrHyb 💎",
        "🍳 jhAz ykhtSr wqtk — w khsom **{discount}%** ykhtSr qlqk ⚡️",
        "❄️ mkYf ybrd Hr alSyf — w sAr **{price}** ybrd qlqk 🌟",
        "🧹 mknsH tnZf bytk — w sAr **{price}** ynZf myzAnytk 🔥",
        "🛏️ mrtbH nAmH tryH Zhrk — **{price}** tryH myzAnytk mn alGlA' 🛏️",
        "🪑 krsy mryH l alAmal — w khsom **{discount}%** mryH l almyzAnyH 💺",
        "🍽️ Tqm AwAny THy — bA **{price}** tTbKHyn bAdwAt aHtrafyH 🍳",
        "🌡️ mdfA'H khrbAyH dAfytH — w sAr **{price}** ydfy qlbk mn albrd 🔥",
        "🚿 dsh AstHmAm bDGH Aaly — **{price}** yGyr tjrbH alAstHmAm 🚿",
        "🪟 stAyr tAm alGurfH — w khsom **{discount}%** tAm alqlq mn al sAr 🌑",
        "🛁 HwD AstHmAm fAKhr — bA **{price}** tstHmyn b fKHAmH 🛁",
        "📺 HAmyl tlfzywn mthrk — **{price}** ythrk mA aHtAyAtk 📺",
        "🍞 mHmsH Khbz sryA' — w sAr **{price}** sryA' fy altwfyryr 🍞",
        "🧺 slH Gsyl AnyqH — bA **{price}** tKlyn alGsyl Aql kAbH 🧺",
        "🪴 nbAt SnAyAH tzyin — w khsom **{discount}%** tzyin almyzAnyH 🌿",
        "🛋️ Tqm knb mryH — **{price}** yjmA alAryHyH w alAnqH 🛋️",
        "🔦 AdA'tH LED mwfrH — bA **{price}** twfr flwsk w khrbA'k 💡",
        "🍵 GlAyH mA' sryA' — w sAr **{price}** sryA' fy alAstHqAq ☕",
        "🧽 mnZf bKHAr l alArDyAt — **{price}** ynZf bytk bdwA mAd kyMyAyH 🧽",
        "🛏️ mKHdt TbbyH l alrqbH — w khsom **{discount}%** tryH rqbtk w jybk 🛏️",
        "🪞 mrA' mDA'tH l altzyyn — bA **{price}** tzyinHyn nfsk bAdA'tH mthylyH 🪞",
        "🍳 mqlyH Gyr lASqH — **{price}** tKly alTbKH mtA'H bdwA tAb 🍳",
        "🧹 mmsH bKHAr — w sAr **{price}** tbKr alqlq mn altnZyf 🧹",
        "🏠 mnZm KhzAnH dhky — bA **{price}** ynZm mlAbisk w myzAnytk 📦"
    ],
    "sports": [
        "💪 qwH tbdA b qrr — qrr bA **{price}** ybdA b dkA' 🔥",
        "🏋️ jhAz yrfAk fwq — w sAr **{price}** yrfA myzAnytk 💎",
        "🏃 hthA' yjry bk l alahdAf — w khsom **{discount}%** yjry b altwfyryr ⚡️",
        "🧘 ywGH tryH jsmk — w sAr **{price}** tryH mHfZtk 🌟",
        "🚴 drAjH tqwY qlbk — w sAr **{price}** yqwY qrrk 🔥",
        "🏊 zAAnf sbAHh aHtrafyH — **{price}** tKlyk tsbbH b thqH 🏊",
        "🥊 qfAzAt mlAkHmH mtynH — w khsom **{discount}%** tthml kl DrbH 🥊",
        "🧘‍♀️ bsAT ywGH mAnA l alAnzlAq — bA **{price}** tswyn kl alwDAyAt bAmAn 🧘",
        "🏸 mDrb tns Kfyf — w sAr **{price}** Kfyf AlA almyzAnyH 🏸",
        "⚽ krH qdm AslyH — **{price}** tstAhl tlAb fyhA kl ywm ⚽",
        "🎿 nZArAt tzlj wAqyH — w khsom **{discount}%** tHmy Aynk w jybk 🎿",
        "🏋️‍♀️ dmblz mtAddH alAwzAn — bA **{price}** tbnyn ADmAltk b dkA' 🏋️",
        "🧗 Hbl qfz aHtrafy — **{price}** yHrQ sArAtk w yHrQ alGlA' 🪢",
        "🚣 AlH tjdyf mnzlyH — w sAr **{price}** yjdyf bAd An alGlA' 🚣",
        "🎯 lwH sHAm dqyqH — bA **{price}** tSyb alhdaf fy altwfyryr 🎯",
        "🧴 zyt tdfyH l alADmAl — w khsom **{discount}%** ydfy ADmAltk w jybk 🔥",
        "🎽 strH ryAdyH tArq — **{price}** tArqk w tnhAf myzAnytk 💦",
        "🏃 sAH ryAdyH tTAbA nbDk — bA **{price}** tTAbA SHtk b dkA' ⌚",
        "🧘 krH tmAryn albTn — w sAr **{price}** tswy lk bTn msTtH 🏐",
        "🏸 Tqm rysh tns — **{price}** yKlyk tlAbyn bdwA twqf 🏸",
        "🚴 KwDH drAjH AmnH — w khsom **{discount}%** AmnH l myzAnytk 🪖",
        "🏋️ HzAm rfy' aTqAl — bA **{price}** tHmy Zhrk w mHfZtk 🏋️",
        "🧘 zjAjH mA' ryAdyH — **{price}** trwyk aTnyA' altmryn 💧",
        "🏃 shrAbAt DGH l alryAdH — w sAr **{price}** tDGH AlA altwfyryr 🧦",
        "💪 brwtyn bnA' ADmAl — bA **{price}** tbnY jsmk b dkA' 💪"
    ],
    "general": [
        "✨ mn byn kl alKHyArAt — wqf And hAlSfqH — **{price}** tstAhl altfkyr 🔥",
        "🌟 dhhb ylmA dA'ymA' — bs hAlSfqH bA **{price}** tlmA Akthr 💎",
        "⚡️ fy zHmH alArwD — nAdr tlqA SfqH HqyqyH — hthy wAHdH mnhm ⚡️",
        "🔥 frSH mA tjy mrtHyn — hthy almrH alAwlA bA **{price}** 🌟",
        "💎 jwdH w sAr mAqwl — yjtmnwn fy SfqH bA **{price}** 🔥",
        "🎯 SfqH alywm: mntj ystAhl — w sAr **{price}** ystAhl Akthr 🎯",
        "💰 twfyr Hqyqy msh mjrd kAlAm — **{discount}%** ythbt alkAlAm 💰",
        "🚀 lA tfwthA — **{price}** yjy mrtH wAHdH fy alAumr 🚀",
        "⭐ mntj bAlf njmH — w sAr **{price}** ystAhl mlywn njmH ⭐",
        "🔥 al sAr ytklm — w **{price}** ySrK: KhDny! 🔥",
        "💎 SfqH mn dhhb — b sAr **{price}** yKlyk tshtry dhhb 💎",
        "⚡️ qrr dhky ybdA bA **{price}** — w yntHy bAbtsAmH ⚡️",
        "🌟 alnjwm tStf — w **{price}** yqwl: alHyn wqt alshryA' 🌟",
        "💪 qwH alSfqH fy **{price}** — w qwH qrrk fy akhtyArhA 💪",
        "🎯 hdafk wADH: twfyr — w **{discount}%** ywSlk l hdafk 🎯",
        "🔥 mA yHtAj tfkyr — **{price}** ytklm An nfsH 🔥",
        "💰 flwsk tstAhl ttSrf b dkA' — **{price}** ythbt dkA'k 💰",
        "⭐ SfqH KHms njmAt b sAr njmH wAHdH — **{price}** ystAhl ⭐",
        "🚀 AnTlq bA **{price}** — w lA ttrdd lHZH 🚀",
        "💎 alAlmAs nAdr — w hAlSfqH bA **{price}** nAdrH mthlh 💎",
        "⚡️ sArAH fy alAstfAdH — **{discount}%** yKlyk tstfyd qbl aljmAyA' ⚡️",
        "🌟 ywmk yHtAj SfqH HwlyH — w **{price}** AHlA SfqH 🌟",
        "🔥 kl qrsh fy **{price}** ystAhl — w kl thanyH tfkyr tDyA frSH 🔥",
        "💪 qrr qwY ybdA bA **{price}** — w yntHy b mntj qwY 💪",
        "🎯 alSfqH almthylyH mwjwdt — w **{price}** ythbt wjwdhA 🎯"
    ]
}

def get_headline(name, cat, gender, price, discount, chat_id=None):
    sub = cat
    if cat == "fashion":
        sub = f"fashion_{gender}" if gender in ["men", "women"] else "general"
    elif cat == "beauty":
        sub = f"beauty_{gender}" if gender in ["men", "women"] else "general"
    templates = HEADLINES.get(sub, HEADLINES["general"])
    if chat_id is not None:
        chat_key = f"{chat_id}_{sub}"
        if chat_key not in _used_headlines:
            _used_headlines[chat_key] = set()
        available = [i for i in range(len(templates)) if i not in _used_headlines[chat_key]]
        if not available:
            _used_headlines[chat_key] = set()
            available = list(range(len(templates)))
        chosen_idx = random.choice(available)
        _used_headlines[chat_key].add(chosen_idx)
        h = templates[chosen_idx].format(price=price, discount=discount)
    else:
        h = random.choice(templates).format(price=price, discount=discount)
    price_digits = re.sub(r'[^\d]', '', price)
    has_price = price_digits and price_digits in re.sub(r'[^\d]', '', h)
    return h, has_price

def generate_post(data, url, chat_id=None):
    name = data["name"]
    price = clean_price(data["price"])
    old = clean_price(data["old_price"]) if data["old_price"] else None
    old_num = extract_num(data["old_price"]) if data["old_price"] else 0
    cur_num = data["current_num"]
    discount = int(((old_num - cur_num) / old_num) * 100) if old_num > cur_num > 0 else 0
    cat = detect_category(name)
    gender = detect_gender(name)
    headline, has_price = get_headline(name, cat, gender, price, discount, chat_id)
    parts = [headline]
    name_words = set(name.lower().split()[:3])
    if not bool(name_words & set(headline.lower().split())):
        parts.append(f"{get_emoji(cat)} {name}")
    if not has_price:
        if old and old_num > cur_num:
            parts.append(f"❌ al sAr alsAbq: ~~{old}~~\n💥 al sAr alAn: **{price}** (khsom {discount}%)")
        else:
            parts.append(f"💰 al sAr: **{price}**")
    if data["coupons"]:
        b = data["coupons"][0]
        parts.append(f"🎟️ kwbwn **{b['percent']}%** ← ySHr bA **{b['final_price']} ryl**! 🔥")
        if len(data["coupons"]) > 1:
            parts.append("💡 kwbwnAt AdAfytH:\n" + "\n".join(f"   • `{c['code']}` — **{c['percent']}%**" for c in data["coupons"][1:3]))
    parts.append(f"🛒 rAbT alshryA':\n{url}")
    return "\n\n".join(parts)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text.strip())
    if not urls:
        return bot.reply_to(msg, "❌ arsl rAbT AmAzwn")
    for u in urls:
        if not is_amazon_link(u):
            bot.reply_to(msg, "❌ yrjy arsl rAbT AmAzwn fqT (Ay dwlH)")
            continue
        resolved_url = resolve_amazon_url(u)
        asin = get_asin(resolved_url)
        if not asin:
            bot.reply_to(msg, "❌ tAdr AstKhrAj rqm almntj (ASIN) mn alrAbT\njrb rAbT mbAshr mn SfHh almntj")
            continue
        domain = get_amazon_domain(resolved_url)
        wait = bot.reply_to(msg, "⏳ jAry altHlyl...")
        p = get_product(asin, domain)
        if not p:
            bot.edit_message_text("❌ tAdr qrA't byAnAt almntj\nqd ykwn almntj Gyr mtwfr aw mHmY", msg.chat.id, wait.message_id)
            continue
        post = generate_post(p, u, msg.chat.id)
        try:
            if p["image"]:
                bot.send_photo(msg.chat.id, p["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error: {e}")
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ KTA' fy alArsAl", msg.chat.id, wait.message_id)

print("🤖 albwt yAml — yqbl Ay rAbT AmAzwn + Afylyt 🔥")
bot.infinity_polling()
def detect_gender(n):
    n = n.lower()
    if any(w in n for w in ['women', 'lady', 'female', 'نسائي', 'فستان', 'dress', 'skirt', 'makeup', 'lipstick']):
        return 'women'
    if any(w in n for w in ['men', 'male', 'رجالي', 'عطر رجالي']):
        return 'men'
    return 'neutral'

def get_emoji(c):
    return {"electronics": "📱", "fashion": "👕", "beauty": "💄", "home": "🏠", "sports": "💪"}.get(c, "📦")

# ========== NEW: Support all Amazon domains + affiliate links ==========

def is_amazon_link(url):
    """Check if URL is any Amazon or affiliate link"""
    amazon_domains = [
        'amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.it', 'amazon.es',
        'amazon.ca', 'amazon.com.au', 'amazon.in', 'amazon.jp', 'amazon.cn',
        'amazon.sa', 'amazon.ae', 'amazon.com.tr', 'amazon.com.br', 'amazon.com.mx',
        'amzn.to', 'amzn.com', 'a.co', 'z.cn'
    ]
    url_lower = url.lower()
    return any(domain in url_lower for domain in amazon_domains)

def resolve_amazon_url(url):
    """Follow redirects to get real Amazon URL from affiliate/short links"""
    # Handle amzn.to and other short links
    short_domains = ['amzn.to', 'a.co']
    if any(domain in url.lower() for domain in short_domains):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            resp = requests.head(url, headers=headers, allow_redirects=True, timeout=15)
            if resp.status_code in [200, 301, 302] and resp.url != url:
                return resp.url
        except Exception as e:
            print(f"Redirect error: {e}")
    return url

def get_asin(url):
    """Extract ASIN from any Amazon URL format"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/([A-Z0-9]{10})/?$',
        r'[?&]asin=([A-Z0-9]{10})',
        r'[?&]dp=([A-Z0-9]{10})',
        r'[?&]productId=([A-Z0-9]{10})',
        r'%2Fdp%2F([A-Z0-9]{10})',
        r'[?&]url=.*%2Fdp%2F([A-Z0-9]{10})',
    ]
    for p in patterns:
        m = re.search(p, url, re.I)
        if m:
            return m.group(1)
    return None

def get_amazon_domain(url):
    """Extract Amazon domain from URL"""
    m = re.search(r'(amazon\.[a-z.]+)', url.lower())
    if m:
        return m.group(1)
    # Default to amazon.com if can't detect
    return "amazon.com"

# ========== END NEW ==========

def clean_price(t):
    try:
        n = re.findall(r'[\d,]+(?:\.\d+)?', t)[0].replace(",", "")
        return f"{int(float(n))} ريال"
    except:
        return t

def extract_num(t):
    try:
        return float(re.findall(r'[\d,]+(?:\.\d+)?', t)[0].replace(",", ""))
    except:
        return 0

def get_image(soup):
    img = soup.select_one("#landingImage")
    if img:
        url = img.get("data-old-hires") or img.get("src")
        if not url:
            try:
                d = json.loads(img.get("data-a-dynamic-image", "{}"))
                url = sorted(d.keys(), key=lambda x: d[x][0]*d[x][1], reverse=True)[0] if d else None
            except:
                pass
        if url:
            return re.sub(r'_SX\d+_SY\d+_|_SX\d+_|_SY\d+_|_CR\d+,\d+,\d+,\d+_|_AC_SL\d+_|_SCLZZZZZZZ_|_FMwebp_|_QL\d+_', '_', url).split('?')[0]
    og = soup.select_one('meta[property="og:image"]')
    return og.get("content") if og else None

def get_seller(soup):
    for sel in ["#merchant-info a", "[data-feature-name='merchant'] a", "#merchant-info"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if len(t) > 2:
                return t
    return None

def get_rating(soup):
    r = soup.select_one("#acrPopover .a-icon-alt") or soup.select_one("[data-hook='rating-out-of-text']")
    rating = re.search(r'([\d.]+)', r.get_text(strip=True)).group(1) if r else None
    rc = soup.select_one("#acrCustomerReviewText") or soup.select_one("[data-hook='total-review-count']")
    reviews = re.search(r'([\d,]+)', rc.get_text(strip=True)).group(1).replace(",", "") if rc else None
    return rating, reviews

def get_stock(soup):
    for sel in ["#availability span", ".a-color-price.a-text-bold", "#outOfStock"]:
        el = soup.select_one(sel)
        if el and any(w in el.get_text(strip=True).lower() for w in ['left', 'متبقي', 'stock', 'soon', 'limited', 'only']):
            return el.get_text(strip=True)
    return None

def get_coupons(soup, price):
    found = []
    for sel in ["#couponTextInput", "[data-feature-name='coupon']", ".couponText", "#couponContainer", ".savingsPercentage"]:
        for el in soup.select(sel):
            txt = el.get_text(strip=True)
            if len(txt) > 3:
                p = re.search(r'(\d+)%', txt)
                if p:
                    pct = int(p.group(1))
                    code = re.search(r'([A-Z]{3,}\d{2,}|\d{2,}[A-Z]{3,}|[A-Z]{4,})', txt)
                    code = code.group(1) if code else f"خصم {pct}%"
                    found.append({"code": code, "percent": pct, "final_price": int(price - price * pct / 100), "text": txt})
    seen = {}
    uniq = []
    for c in found:
        k = c["code"].upper()
        if k not in seen:
            seen[k] = True
            uniq.append(c)
    uniq.sort(key=lambda x: x["percent"], reverse=True)
    return uniq

def get_product(asin, domain="amazon.sa"):
    """Fetch product from any Amazon domain"""
    url = f"https://www.{domain}/dp/{asin}"

    # Try multiple user agents and domains
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
    ]

    for ua in user_agents:
        try:
            r = requests.get(url, headers={
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
                "Referer": "https://www.google.com/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }, timeout=30)

            if r.status_code != 200 or len(r.text) < 5000:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.select_one("#productTitle")
            if not title:
                continue

            full = title.text.strip()
            price = None
            for sel in [".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen", ".a-price .a-offscreen", ".a-price-whole"]:
                el = soup.select_one(sel)
                if el and el.text and any(c.isdigit() for c in el.text):
                    price = el.text.strip()
                    break
            if not price:
                continue

            old = None
            for sel in [".a-price.a-text-price[data-a-color='secondary'] .a-offscreen", ".basisPrice .a-offscreen"]:
                el = soup.select_one(sel)
                if el and el.text != price and any(c.isdigit() for c in el.text):
                    old = el.text.strip()
                    break

            img = get_image(soup)
            seller = get_seller(soup)
            rating, reviews = get_rating(soup)
            stock = get_stock(soup)
            cur = extract_num(price)
            coupons = get_coupons(soup, cur)

            return {
                "name": protect_brands(full[:80]),
                "full_title": full,
                "price": price,
                "old_price": old,
                "image": img,
                "seller": seller,
                "rating": rating,
                "reviews": reviews,
                "stock": stock,
                "coupons": coupons,
                "current_num": cur,
                "domain": domain
            }
        except Exception as e:
            print(f"Error: {e}")
    return None

HEADLINES = {
    "electronics": [
        "✨ من بين آلاف الخيارات،\nهالصفقة تبرق وتلمع\n— سعر **{price}** يخليك تتوقف\nوتفكر: وش يمنعك الحين؟ 🔥",
        "🌟 يا هلا بالصفقة اللي تستاهل\nكل ثانية تفكير\n**{discount}%** خصم حقيقي 💎",
        "⚡️ تقنية بمواصفات عالية\nوسعر **{price}** معقول\nنادر تلقى مثله 🎯",
        "🔥 فرصة ما تتكرر\nجهاز بـ **{price}** يستاهل\nكل قرش فيه 🚀",
        "💡 ذكاء الاختيار في التوقيت\n— والحين يصرخ: اشتري!\n**{discount}%** خصم ⚡️"
    ],
    "fashion_men": [
        "👔 أناقة رجالية بثقة\n— هالطقم بـ **{price}**\nيمنحك الاثنين 🔥",
        "🕶️ طلّة تفرض احترامك\nبسعر **{price}** يفرض تقديرك 💎",
        "⌚ وقتك ثمين\nوساعتك بـ **{price}** تستاهله ⚡️",
        "👟 حذاء يركض بك للأهداف\nوسعر **{price}** يركض بالتوفير 🌟",
        "🧥 جاكيت شتوي بخفة سعر\n**{price}** مع **{discount}%** يدفي القلب 🔥"
    ],
    "fashion_women": [
        "👗 فستان يحكي قصة\nبـ **{price}** يحكي ذكاء اختيارك 🔥",
        "👜 شنطة تكمل إطلالتك\nوسعر **{price}** يكمل فرحتك 💎",
        "💄 مكياج يزين وجهك\nوسعر **{price}** يزين يومك ⚡️",
        "👠 كعب يرفعك فوق\nوسعر **{price}** يرفعك أعلى 🌟",
        "🧕 عباية تسترك وتزينك\nبـ **{price}** تستر ميزانيتك 🔥"
    ],
    "beauty_men": [
        "🧔 رجل مهتم بنظافته\n— هالمنتج بـ **{price}** يهتم بميزانيتك 🔥",
        "💈 حلاقة نظيفة بمنتج نظيف\nوسعر **{price}** ينظف الغلاء 💎",
        "👔 عطر يثبت حضورك\nبسعر **{price}** يثبت ذكاءك ⚡️",
        "🧴 لوشن يترطب بشرتك\nوسعر **{price}** يترطب قلبك 🌟",
        "🪒 ماكينة تفصلك عن الباهت\nوسعر **{price}** يفصلك عن الباهظ 🔥"
    ],
    "beauty_women": [
        "💅 طلاء يلمع زي عينك\nلما تشوفين **{price}** ⚡️",
        "🧖‍♀️ كريم يخليك تتأملين\nبمرآتك ومحفظتك بـ **{price}** 🌟",
        "💋 أحمر شفاه بـ **{price}**؟\nيا ليت كل القرارات الحلوة تجي كذا 🔥",
        "🌸 عطر يفوح بأريج الأناقة\nوسعر **{price}** يفوح بالذكاء 💎",
        "✨ سيروم يبرق وجهك\nوسعر **{price}** يبرق يومك ⚡️"
    ],
    "home": [
        "🏠 بيت يعكس ذوقك\nيبدأ بـ **{price}** يعكس ذكاءك 🔥",
        "🛋️ أثاث يستقبل ضيوفك\nبكرامة وسعر **{price}** بترحيب 💎",
        "🍳 جهاز يختصر وقتك\nوخصم **{discount}%** يختصر قلقك ⚡️",
        "❄️ مكيف يبرد حر الصيف\nوسعر **{price}** يبرد قلقك 🌟",
        "🧹 مكنسة تنظف بيتك\nوسعر **{price}** ينظف ميزانيتك 🔥"
    ],
    "sports": [
        "💪 قوة تبدأ بقرار\n— قرار بـ **{price}** يبدأ بذكاء 🔥",
        "🏋️ جهاز يرفعك فوق\nوسعر **{price}** يرفع ميزانيتك 💎",
        "🏃 حذاء يجري بك للأهداف\nوخصم **{discount}%** يجري بالتوفير ⚡️",
        "🧘 يوغا تريح جسمك\nوسعر **{price}** تريح محفظتك 🌟",
        "🚴 دراجة تقوي قلبك\nوسعر **{price}** يقوي قرارك 🔥"
    ],
    "general": [
        "✨ من بين كل الخيارات\nوقف عند هالصفقة\n— **{price}** تستاهل التفكير 🔥",
        "🌟 ذهب يلمع دائماً\nبس هالصفقة بـ **{price}** تلمع أكثر 💎",
        "⚡️ في زحمة العروض\nنادر تلقى صفقة حقيقية\nهذي واحدة منهم ⚡️",
        "🔥 فرصة ما تجي مرتين\nهذي المرة الأولى بـ **{price}** 🌟",
        "💎 جودة وسعر معقول\nيجتمعون في صفقة بـ **{price}** 🔥"
    ]
}

def get_headline(name, cat, gender, price, discount):
    sub = cat
    if cat == "fashion":
        sub = f"fashion_{gender}" if gender in ["men", "women"] else "general"
    elif cat == "beauty":
        sub = f"beauty_{gender}" if gender in ["men", "women"] else "general"
    templates = HEADLINES.get(sub, HEADLINES["general"])
    h = random.choice(templates).format(price=price, discount=discount)
    price_digits = re.sub(r'[^\d]', '', price)
    has_price = price_digits and price_digits in re.sub(r'[^\d]', '', h)
    return h, has_price

def generate_post(data, url):
    name = data["name"]
    price = clean_price(data["price"])
    old = clean_price(data["old_price"]) if data["old_price"] else None
    old_num = extract_num(data["old_price"]) if data["old_price"] else 0
    cur_num = data["current_num"]
    discount = int(((old_num - cur_num) / old_num) * 100) if old_num > cur_num > 0 else 0
    cat = detect_category(name)
    gender = detect_gender(name)
    headline, has_price = get_headline(name, cat, gender, price, discount)
    parts = [headline]
    name_words = set(name.lower().split()[:3])
    if not bool(name_words & set(headline.lower().split())):
        parts.append(f"{get_emoji(cat)} {name}")
    if not has_price:
        if old and old_num > cur_num:
            parts.append(f"❌ السعر السابق: ~~{old}~~\n💥 السعر الآن: **{price}** (خصم {discount}%)")
        else:
            parts.append(f"💰 السعر: **{price}**")
    if data["coupons"]:
        b = data["coupons"][0]
        parts.append(f"🎟️ كوبون **{b['percent']}%** ← يصير بـ **{b['final_price']} ريال**! 🔥")
        if len(data["coupons"]) > 1:
            parts.append("💡 كوبونات إضافية:\n" + "\n".join(f"   • `{c['code']}` — **{c['percent']}%**" for c in data["coupons"][1:3]))
    parts.append(f"🛒 [رابط الشراء]({url})")
    return "\n\n".join(parts)

@bot.message_handler(func=lambda m: True)
def handler(msg):
    urls = re.findall(r'https?://\S+', msg.text.strip())
    if not urls:
        return bot.reply_to(msg, "❌ أرسل رابط أمازون")

    for u in urls:
        # ========== NEW: Check any Amazon link ==========
        if not is_amazon_link(u):
            bot.reply_to(msg, "❌ يرجى إرسال رابط أمازون فقط (أي دولة)")
            continue

        # Resolve affiliate/short links
        resolved_url = resolve_amazon_url(u)

        asin = get_asin(resolved_url)
        if not asin:
            bot.reply_to(msg, "❌ تعذر استخراج رقم المنتج (ASIN) من الرابط\nجرب رابط مباشر من صفحة المنتج")
            continue

        domain = get_amazon_domain(resolved_url)

        wait = bot.reply_to(msg, "⏳ جاري التحليل...")
        p = get_product(asin, domain)

        if not p:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج\nقد يكون المنتج غير متوفر أو محمي", msg.chat.id, wait.message_id)
            continue

        # Use original URL (affiliate link) in the post to preserve commissions
        post = generate_post(p, u)

        try:
            if p["image"]:
                bot.send_photo(msg.chat.id, p["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error: {e}")
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown", disable_web_page_preview=True)
                bot.delete_message(msg.chat.id, wait.message_id)
            except:
                bot.edit_message_text("❌ خطأ في الإرسال", msg.chat.id, wait.message_id)

print("🤖 البوت يعمل — يقبل أي رابط أمازون + أفيلييت 🔥")
bot.infinity_polling()
