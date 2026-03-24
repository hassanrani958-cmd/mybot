import random, string, requests, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# التوكن الخاص بك
TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"

# دالة توليد يوزرات (رباعي، شبه ثلاثي، شبه رباعي)
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
        # فحص اليوزر عبر ديسكورد
        r = requests.post("https://discord.com/api/v9/auth/register", json={"username": user}, timeout=5)
        return "already_taken" not in r.text
    except:
        return False

# متغير للتحكم في حالة التشغيل
is_running = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 بوت الصيد التلقائي جاهز!\n\n"
        "🚀 أرسل /run لبدء الصيد.\n"
        "🛑 أرسل /stop لإيقاف الصيد."
    )

async def run_hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    if is_running:
        await update.message.reply_text("⚠️ الصيد يعمل بالفعل!")
        return
    
    is_running = True
    await update.message.reply_text("✅ بدأ الصيد التلقائي... سأخبرك عند إيجاد يوزر متاح.")
    
    while is_running:
        user = generate_user()
        if check_discord(user):
            await update.message.reply_text(f"🎯 صيد جديد!\nاليوزر: @{user}\nالحالة: متاح ✅")
        
        # انتظر 3 ثوانٍ قبل التخمين التالي
        await asyncio.sleep(3)

async def stop_hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    is_running = False
    await update.message.reply_text("🛑 تم إيقاف الصيد التلقائي بنجاح.")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_hunt))
    app.add_handler(CommandHandler("stop", stop_hunt))
    print("البوت يعمل الآن...")
    app.run_polling()
    
