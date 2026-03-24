import random, string, requests, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# --- الإعدادات ---
TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"
OWNER_USERNAME = "r9a0n"
CHANNEL_ID = "@W9edding"

AUTHORIZED_USERS = {OWNER_USERNAME.lower()}
is_running = {}

async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except: return False

def generate_user():
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=random.choice([3, 4])))

def check_discord(user):
    try:
        r = requests.post("https://discord.com/api/v9/auth/register", json={"username": user}, timeout=3)
        return "already_taken" not in r.text
    except: return False

# ⚡ تحديث فحص التيك توك ليكون أقوى وأسرع
def check_tiktok(user):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    try:
        # فحص مباشر للصفحة
        r = requests.get(f"https://www.tiktok.com/@{user}", headers=headers, timeout=5)
        # إذا كانت النتيجة 404 يعني اليوزر متاح 100%
        return r.status_code == 404
    except: return False

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.message.from_user
    uname = user.username.lower() if user.username else str(user.id)
    if uname not in AUTHORIZED_USERS:
        await u.message.reply_text(f"⚠️ البوت مدفوع.\nللتفعيل تواصل مع المالك: @{OWNER_USERNAME}")
        return
    if not await check_subscription(user.id, c):
        kb = [[InlineKeyboardButton("اضغط للاشتراك في القناة ✅", url=f"https://t.me/W9edding")]]
        await u.message.reply_text("🛑 اشترك في قناة القرآن أولاً.", reply_markup=InlineKeyboardMarkup(kb))
        return
    buttons = [[InlineKeyboardButton("🎮 صيد ديسكورد", callback_data="discord"), InlineKeyboardButton("🎵 صيد تيك توك", callback_data="tiktok")],
               [InlineKeyboardButton("📖 شرح الأوامر", callback_data="help")], [InlineKeyboardButton("👨‍💻 مراسلة المالك", callback_data="contact")]]
    await u.message.reply_text(f"✨ أهلاً @{uname}\nاختر المنصة:", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_choice(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    uid = q.from_user.id
    uname = q.from_user.username.lower() if q.from_user.username else str(uid)
    choice = q.data
    await q.answer()
    
    if choice in ["help", "contact"]:
        txt = "شرح الأوامر: /run للبدء و /stop للإيقاف." if choice=="help" else f"المالك: @{OWNER_USERNAME}"
        await q.message.reply_text(txt)
        return

    is_running[uname] = True
    await q.message.reply_text(f"🚀 بدأ الصيد لـ {choice}...")
    
    while is_running.get(uname):
        if not await check_subscription(uid, c):
            is_running[uname] = False
            break
        target = generate_user()
        available = check_discord(target) if choice == "discord" else check_tiktok(target)
        if available:
            await q.message.reply_text(f"🎯 صيد جديد ({choice})!\n👤 اليوزر: `@{target}`\n✅ متاح", parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(3) # زيادة الوقت قليلاً لثبات الفحص

async def add_user(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.message.from_user.username.lower() != OWNER_USERNAME.lower(): return
    if c.args:
        target = c.args[0].replace("@", "").lower()
        AUTHORIZED_USERS.add(target)
        await u.message.reply_text(f"✅ تم تفعيل {target}")

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
    
