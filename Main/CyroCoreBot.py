from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import subprocess
import platform

# ===== TELEGRAM BOT TOKEN =====
TELEGRAM_TOKEN = "8351620039:AAE_eTYMKid9Kl4a4ObVruagPxe3c69TU9I"

# ===== TELEGRAM BOT SETUP =====
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def tg_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    text = f"You said: {update.message.text}"
    await update.message.reply_text(text)

    if update.message.text.lower() == "hi":
        # Use 'dir' on Windows, 'ls -l' on Linux/Mac
        if platform.system() == "Windows":
            cmd = ["cmd", "/c", "dir"]
        else:
            cmd = ["ls", "-l"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip() or "No output"
        await update.message.reply_text(f"Command output:\n{output}")

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tg_echo))

# ===== RUN TELEGRAM BOT =====
if __name__ == "__main__":
    try:
        telegram_app.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
