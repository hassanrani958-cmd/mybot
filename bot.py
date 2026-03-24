import random, string, requests, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"

# دالة توليد يوزرات (ثلاثي ورباعي وشبه رباعي)
def generate_user():
    chars = string.ascii_lowercase + string.digits
    types = [
        "".join(random.choice(chars) for _ in range(4)), # رباعي صافي
        random.choice(chars) + "_" + "".join(random.choice(chars) for _ in range(2)), # شبه ثلاثي
        "".join(random.choice(chars) for _ in range(2)) + "_" + random.choice(chars) # شبه رباعي
    ]
    return random.choice(types)

def check_discord(user):
    try:
        r = requests.post("https://discord.com/api/v9/auth/register", json={"username": user}, timeout=5)
        return "already_taken" not in r.text
    except: return False

# حالة الصيد (تشغيل أو إيقاف)
hunting = False

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("أهلاً بك!\nأرسل /run لبدء التخمين التلقائي المستمر.\nأرسل /stop لإيقاف البوت.")

async def run_hunt(u: Update, c: ContextTypes.DEFAULT_TYPE):
    global hunting
    if hunting:
        await u.message.reply_text("البوت يعمل بالفعل!")
        return
    
    hunting = True
    await u.message.reply_text("🚀 تم بدء الصيد التلقائي (تخمين كل 3 ثوانٍ)...\nسأرسل لك رسالة فقط عند إيجاد يوزر متاح ✅")
    
    while hunting:
        user = generate_user()
        if check_discord(user):
            await u.message.reply_text(f"🎯 صيد جديد!\nاليوزر: @{user}\nالحالة: ✅ متاح")
        
        # الانتظار لمدة 3 ثوانٍ لتجنب حظر IP السيرفر من ديسكورد
        await asyncio.sleep(3)

async def stop_hunt(u: Update, c: ContextTypes.DEFAULT_TYPE):
    global hunting
    hunting = False
    await u.message.reply_text("🛑 تم إيقاف الصيد التلقائي.")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_hunt))
    app.add_handler(CommandHandler("stop", stop_hunt))
    app.run_polling()
    
