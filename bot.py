import random, string, requests, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# --- الإعدادات الأساسية (تأكد من صحتها) ---
TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"
OWNER_USERNAME = "r9a0n"  # يوزرك أنت المالك
CHANNEL_ID = "@W9edding"  # قناتك للقرآن الكريم

# قائمة المسموح لهم (تبدأ بك أنت كمالك)
AUTHORIZED_USERS = {OWNER_USERNAME.lower()}
is_running = {}

# 1️⃣ دالة فحص الاشتراك الإجباري في القناة
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception: return False

# 2️⃣ دالة توليد يوزرات منوعة (ثلاثي، رباعي، شبه ثلاثي، شبه رباعي)
def generate_user():
    chars = string.ascii_lowercase + string.digits
    types = [
        "".join(random.choices(chars, k=3)), # ثلاثي
        "".join(random.choices(chars, k=4)), # رباعي
        random.choice(chars) + "_" + "".join(random.choices(chars, k=2)), # شبه ثلاثي
        "".join(random.choices(chars, k=2)) + "_" + random.choice(chars)  # شبه رباعي
    ]
    return random.choice(types)

# 3️⃣ فحص المنصات (ديسكورد وتيك توك)
def check_discord(user):
    try:
        r = requests.post("https://discord.com/api/v9/auth/register", json={"username": user}, timeout=3)
        return "already_taken" not in r.text
    except: return False

def check_tiktok(user):
    try:
        r = requests.get(f"https://www.tiktok.com/@{user}", timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
        return r.status_code == 404
    except: return False

# 4️⃣ أمر البدء والقائمة الرئيسية
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.message.from_user
    uname = user.username.lower() if user.username else str(user.id)

    # فحص التفعيل
    if uname not in AUTHORIZED_USERS:
        await u.message.reply_text(f"⚠️ عذراً @{uname}، البوت مدفوع وغير مفعل لحسابك.\nللتفعيل تواصل مع المالك: @{OWNER_USERNAME}")
        return

    # فحص الاشتراك في القناة
    if not await check_subscription(user.id, c):
        kb = [[InlineKeyboardButton("اضغط للاشتراك في القناة ✅", url=f"https://t.me/W9edding")]]
        await u.message.reply_text("🛑 لكي يعمل البوت، يجب أن تشترك في قناة القرآن الكريم أولاً.\nبعد الاشتراك، أرسل /start مجدداً.", reply_markup=InlineKeyboardMarkup(kb))
        return

    # عرض الأزرار
    buttons = [
        [InlineKeyboardButton("🎮 صيد ديسكورد", callback_data="discord"), InlineKeyboardButton("🎵 صيد تيك توك", callback_data="tiktok")],
        [InlineKeyboardButton("📖 شرح الأوامر", callback_data="help")],
        [InlineKeyboardButton("👨‍💻 مراسلة المالك", callback_data="contact")]
    ]
    await u.message.reply_text(f"✨ أهلاً بك @{uname} في لوحة التحكم.\nاختر المنصة لبدء الصيد التلقائي:", reply_markup=InlineKeyboardMarkup(buttons))

# 5️⃣ معالجة ضغط الأزرار
async def handle_choice(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    uid = q.from_user.id
    uname = q.from_user.username.lower() if q.from_user.username else str(uid)
    choice = q.data
    await q.answer()

    if choice == "help":
        help_txt = (
            "📖 **شرح أوامر البوت:**\n\n"
            "1️⃣ اختر المنصة (تيك توك أو ديسكورد).\n"
            "2️⃣ سيبدأ البوت بالبحث تلقائياً عن اليوزرات المتاحة.\n"
            "3️⃣ للإيقاف، أرسل أمر `/stop` في أي وقت.\n"
            "4️⃣ للعودة للقائمة الرئيسية، أرسل `/start`."
        )
        await q.message.reply_text(help_txt, parse_mode=ParseMode.MARKDOWN)
        return

    if choice == "contact":
        await q.message.reply_text(f"👨‍💻 المالك الرسمي للبوت هو: @{OWNER_USERNAME}\nيمكنك مراسلته للاشتراك أو الاستفسار.")
        return

    # بدء عملية الصيد
    is_running[uname] = True
    await q.message.reply_text(f"🚀 انطلق الصيد التلقائي لـ {choice}...\nسأرسل لك النتائج هنا فور إيجادها.")
    
    while is_running.get(uname):
        # التحقق من القناة (إذا غادر يتوقف فوراً)
        if not await check_subscription(uid, c):
            is_running[uname] = False
            await q.message.reply_text("🛑 تم إيقاف الصيد تلقائياً لأنك غادرت القناة!")
            break

        target = generate_user()
        available = check_discord(target) if choice == "discord" else check_tiktok(target)
        
        if available:
            await q.message.reply_text(f"🎯 صيد جديد ({choice})!\n👤 اليوزر: `@{target}`\n✅ متاح للاستخدام", parse_mode=ParseMode.MARKDOWN)
        
        await asyncio.sleep(2.5) # سرعة الفحص لمنع الحظر

# 6️⃣ أمر الإضافة بالمنشن (للمالك فقط)
async def add_user(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # التأكد أن المرسل هو أنت @r9a0n
    if not u.message.from_user.username or u.message.from_user.username.lower() != OWNER_USERNAME.lower():
        return
    
    if c.args:
        target = c.args[0].replace("@", "").lower()
        AUTHORIZED_USERS.add(target)
        await u.message.reply_text(f"✅ تم تفعيل المستخدم: @{target}\nبإمكانه الآن استخدام البوت بالكامل.")
    else:
        await u.message.reply_text("⚠️ يرجى منشنة الشخص أو كتابة يوزره، مثال:\n`/add @username`", parse_mode=ParseMode.MARKDOWN)

# 7️⃣ أمر إيقاف الصيد
async def stop_hunt(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.message.from_user
    uname = user.username.lower() if user.username else str(user.id)
    is_running[uname] = False
    await u.message.reply_text("🛑 تم إيقاف عملية الصيد بنجاح.")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("stop", stop_hunt))
    app.add_handler(CallbackQueryHandler(handle_choice))
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()
    
