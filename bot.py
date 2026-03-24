import random, string, requests, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# --- الإعدادات الأساسية ---
TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"
OWNER_USERNAME = "r9a0n" 
CHANNEL_ID = "@W9edding" 

AUTHORIZED_USERS = {OWNER_USERNAME.lower()}
is_running = {}

# 1️⃣ فحص الاشتراك في القناة
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except: return False

# 2️⃣ توليد يوزرات ديسكورد (ثلاثي، رباعي، شبه ثلاثي، شبه رباعي)
def generate_user():
    chars = string.ascii_lowercase + string.digits
    types = [
        "".join(random.choices(chars, k=3)), # ثلاثي (abc)
        "".join(random.choices(chars, k=4)), # رباعي (abcd)
        random.choice(chars) + "_" + "".join(random.choices(chars, k=2)), # شبه ثلاثي (a_bc)
        "".join(random.choices(chars, k=2)) + "_" + "".join(random.choices(chars, k=2)), # شبه رباعي (ab_cd)
        "".join(random.choices(chars, k=3)) + "_" + random.choice(chars)  # شبه رباعي (abc_d)
    ]
    return random.choice(types)

# 3️⃣ فحص ديسكورد بدقة
def check_discord(user):
    try:
        # إرسال طلب فحص لـ API التسجيل
        r = requests.post("https://discord.com/api/v9/auth/register", 
                          json={"username": user}, 
                          timeout=3)
        # إذا لم يظهر "already_taken" في الرد يعني اليوزر متاح
        return "already_taken" not in r.text
    except: return False

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.message.from_user
    uname = user.username.lower() if user.username else str(user.id)

    if uname not in AUTHORIZED_USERS:
        await u.message.reply_text(f"⚠️ البوت مخصص للمشتركين.\nللتفعيل تواصل مع المالك: @{OWNER_USERNAME}")
        return

    if not await check_subscription(user.id, c):
        kb = [[InlineKeyboardButton("اشترك في القناة لتفعيل البوت ✅", url=f"https://t.me/W9edding")]]
        await u.message.reply_text("🛑 يجب أن تكون مشتركاً في قناة القرآن الكريم أولاً.", reply_markup=InlineKeyboardMarkup(kb))
        return

    buttons = [
        [InlineKeyboardButton("🎮 ابدأ صيد ديسكورد 🚀", callback_data="start_hunt")],
        [InlineKeyboardButton("📖 الشرح", callback_data="help"), InlineKeyboardButton("👨‍💻 المالك", callback_data="contact")]
    ]
    await u.message.reply_text(f"✨ أهلاً بك @{uname}\nجاهز لصيد يوزرات ديسكورد النادرة؟", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_choice(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    uid = q.from_user.id
    uname = q.from_user.username.lower() if q.from_user.username else str(uid)
    await q.answer()

    if q.data == "help":
        await q.message.reply_text("📖 **طريقة العمل:**\n- اضغط زر البدء.\n- سيقوم البوت بفحص (ثلاثي، رباعي، وشبهها).\n- عند إيجاد يوزر سيصلك تنبيه فوراً.\n- للإيقاف أرسل `/stop`.")
        return
    if q.data == "contact":
        await q.message.reply_text(f"👨‍💻 مبرمج البوت: @{OWNER_USERNAME}")
        return

    # بدء الصيد
    is_running[uname] = True
    await q.message.reply_text("🚀 بدأ الصيد التلقائي لـ Discord...\n(ثلاثي، رباعي، شبه رباعي، شبه ثلاثي)")
    
    while is_running.get(uname):
        # فحص القناة لضمان عدم مغادرة المستخدم
        if not await check_subscription(uid, c):
            is_running[uname] = False
            await q.message.reply_text("🛑 توقف الصيد لأنك غادرت القناة!")
            break

        target = generate_user()
        if check_discord(target):
            await q.message.reply_text(f"🎯 **صيد ديسكورد جديد!**\n👤 اليوزر: `@{target}`\n✅ متاح للاستخدام", parse_mode=ParseMode.MARKDOWN)
        
        await asyncio.sleep(2.2) # سرعة الفحص (أسرع استجابة)

async def add_user(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.message.from_user.username.lower() != OWNER_USERNAME.lower(): return
    if c.args:
        target = c.args[0].replace("@", "").lower()
        AUTHORIZED_USERS.add(target)
        await u.message.reply_text(f"✅ تم تفعيل العضو: @{target}")

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
    
