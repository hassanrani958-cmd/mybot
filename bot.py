import random, string, requests, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# التوكن الخاص بك
TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"
OWNER_USERNAME = "r9a0n" 
CHANNEL_ID = "@W9edding" # قناتك للقرآن الكريم

AUTHORIZED_USERS = {OWNER_USERNAME.lower()}
is_running = {}

# دالة فحص الاشتراك الإجباري
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except: return False

def generate_user():
    chars = string.ascii_lowercase + string.digits
    types = [
        "".join(random.choice(chars) for _ in range(3)), # ثلاثي
        "".join(random.choice(chars) for _ in range(4)), # رباعي
        random.choice(chars) + "_" + "".join(random.choice(chars) for _ in range(2)), # شبه ثلاثي
        "".join(random.choice(chars) for _ in range(2)) + "_" + random.choice(chars)  # شبه رباعي
    ]
    return random.choice(types)

def check_discord(user):
    try:
        r = requests.post("https://discord.com/api/v9/auth/register", json={"username": user}, timeout=5)
        return "already_taken" not in r.text
    except: return False

def check_tiktok(user):
    try:
        r = requests.get(f"https://www.tiktok.com/@{user}", timeout=5)
        return r.status_code == 404
    except: return False

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.message.from_user
    uid = user.id
    uname = user.username.lower() if user.username else str(uid)

    if uname not in AUTHORIZED_USERS:
        await u.message.reply_text(f"⚠️ البوت مفعل للمشتركين فقط.\nتواصل مع المالك للاشتراك: @{OWNER_USERNAME}")
        return

    # فحص الاشتراك في القناة
    if not await check_subscription(uid, c):
        kb = [[InlineKeyboardButton("اضغط هنا للاشتراك في القناة", url=f"https://t.me/W9edding")]]
        await u.message.reply_text("🛑 لكي يعمل البوت، يجب أن تشترك في قناة القرآن الكريم أولاً.\nاشترك ثم أرسل /start", reply_markup=InlineKeyboardMarkup(kb))
        return

    kb = [
        [InlineKeyboardButton("🎮 تخمين ديسكورد", callback_data="discord")],
        [InlineKeyboardButton("🎵 تخمين تيك توك", callback_data="tiktok")]
    ]
    await u.message.reply_text(f"أهلاً بك @{uname}\nاختر المنصة لبدء الصيد التلقائي:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_choice(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    uid = q.from_user.id
    uname = q.from_user.username.lower() if q.from_user.username else str(uid)
    choice = q.data
    await q.answer()

    if not await check_subscription(uid, c):
        await q.message.reply_text("⚠️ توقف! لقد غادرت القناة.")
        return

    is_running[uname] = True
    await q.message.reply_text(f"🚀 بدأ الصيد التلقائي لـ {choice}...\nلإيقاف الصيد أرسل /stop")
    
    while is_running.get(uname):
        if not await check_subscription(uid, c):
            is_running[uname] = False
            await q.message.reply_text("🛑 تم إيقاف الصيد تلقائياً لأنك غادرت القناة!")
            break

        target = generate_user()
        available = check_discord(target) if choice == "discord" else check_tiktok(target)
        
        if available:
            await q.message.reply_text(f"🎯 صيد {choice} جديد!\n👤 اليوزر: @{target}\n✅ متاح")
        await asyncio.sleep(4)

async def add_user(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message.from_user.username or u.message.from_user.username.lower() != OWNER_USERNAME: return
    if not c.args:
        await u.message.reply_text("أرسل اليوزر هكذا: /add r9a0n")
        return
    target = c.args[0].replace("@", "").lower()
    AUTHORIZED_USERS.add(target)
    await u.message.reply_text(f"✅ تم تفعيل @{target} بنجاح!")

async def stop_hunt(u: Update, c: ContextTypes.DEFAULT_TYPE):
    uname = u.message.from_user.username.lower() if u.message.from_user.username else str(u.message.from_user.id)
    is_running[uname] = False
    await u.message.reply_text("🛑 تم إيقاف الصيد.")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("stop", stop_hunt))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.run_polling()
    
