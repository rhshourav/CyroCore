"""
CyroCoreBot - Telegram bot for executing commands remotely
Author: rhshourav
"""
import sqlite3
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ===== ENABLE LOGGING =====
logging.basicConfig(level=logging.INFO)

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


# ===== ASYNC HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram messages and run commands asynchronously."""
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    logging.info(f"📩 Received: {text}")

    if text.lower().startswith("cmd "):
        command = text[4:]  # remove 'cmd '

        logging.info(f"⚡ Running command: {command}")

        try:
            # Run command asynchronously
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode().strip() if stdout else stderr.decode().strip()

            if not output:
                output = "✅ Command executed (no output)"
        except Exception as e:
            output = f"❌ Error: {e}"

        # Telegram message limit is 4096 chars
        await update.message.reply_text(output[:4000])

    else:
        # Reply to normal messages
        await update.message.reply_text(f"You said: {text}")


# ===== REGISTER HANDLER =====
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ===== RUN =====
def main():
    print("✅ Bot is starting...")
    telegram_app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
