import random, string, requests, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# توكن بوتك
TOKEN = "8343948878:AAEY42fD6uH5dWRRghQtZsgWaU69mtSs6bE"

def generate_user():
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(5))

def check_discord(user):
    try:
        r = requests.post("https://discord.com/api/v9/auth/register", json={"username": user}, timeout=5)
        return "already_taken" not in r.text
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 تخمين يدوي (مرة واحدة)", callback_data="once")],
        [InlineKeyboardButton("♻️ تخمين تلقائي (10 محاولات)", callback_data="auto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحباً بك في بوت تخمين ديسكورد!\nاختر نوع التخمين:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "once":
        user = generate_user()
        status = "✅ متاح" if check_discord(user) else "❌ محجوز"
        msg = f"اليوزر المحاول: @{user}\nالحالة: {status}"
        kb = [[InlineKeyboardButton("🔄 محاولة أخرى", callback_data="once")], [InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "auto":
        await query.edit_message_text("جاري التخمين التلقائي لـ 10 يوزرات... انتظر ثواني.")
        results = ""
        for _ in range(10):
            user = generate_user()
            if check_discord(user):
                results += f"✅ @{user} (متاح!)\n"
            else:
                results += f"❌ @{user} (محجوز)\n"
            time.sleep(1) # لتجنب الحظر
        
        kb = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.message.reply_text(f"نتائج التخمين:\n\n{results}", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "back":
        await start(query, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()

if __name__ == "__main__":
    main()
  
