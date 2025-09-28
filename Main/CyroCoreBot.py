"""
CyroCoreBot - Telegram bot for executing commands remotely
Author: rhshourav
"""
import sqlite3
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ===== ENABLE LOGGING =====
logging.basicConfig(level=logging.DEBUG)

# ===== LOAD TOKEN =====
DB_FILE = "credentials.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY, token TEXT)")
conn.commit()
c.execute("SELECT token FROM tokens WHERE id=1")
row = c.fetchone()
if row:
    TELEGRAM_TOKEN = row[0]
else:
    TELEGRAM_TOKEN = input("Enter your Telegram bot token: ").strip()
    c.execute("INSERT INTO tokens (id, token) VALUES (1, ?)", (TELEGRAM_TOKEN,))
    conn.commit()
conn.close()

# ===== BOT APP =====
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


# ===== HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle a specific Telegram command."""
    text = update.message.text.strip()
    _chat_id = update.effective_chat.id

    logging.info("📩 Received: {text}")

    if text.lower().startswith("cmd "):
        command = text[4:]  # remove 'cmd '
        logging.info("⚡ Running command: {command}")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            output = result.stdout if result.stdout else result.stderr
            if not output.strip():
                output = "✅ Command executed (no output)"
        except Exception as e:
            output = f"❌ Error: {e}"
        await update.message.reply_text(output[:4000])  # Telegram limit
    else:
        await update.message.reply_text(f"You said: {text}")


# ===== REGISTER HANDLER =====
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ===== RUN =====
def main():
    print("✅ Bot is starting...")
    telegram_app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
