"""
CryoCoreBot - Telegram bot with pre-programmed commands and logging
Author: rhshourav
"""
import sqlite3
import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ===== ENABLE LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== DATABASE SETUP =====
os.makedirs("db", exist_ok=True)

# ----- TOKENS DB -----
with sqlite3.connect("db/tokens.db") as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY, token TEXT)")
    conn.commit()

# ----- COMMANDS DB -----
with sqlite3.connect("db/commands.db") as conn:
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        command TEXT NOT NULL
    )
    """)
    conn.commit()

# ----- LOGS DB -----
with sqlite3.connect("db/logs.db") as conn:
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command_name TEXT,
        command TEXT,
        output TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

# ===== LOAD TELEGRAM TOKEN =====
with sqlite3.connect("db/tokens.db") as conn:
    c = conn.cursor()
    c.execute("SELECT token FROM tokens WHERE id=1")
    row = c.fetchone()
    if row:
        TELEGRAM_TOKEN = row[0]
    else:
        TELEGRAM_TOKEN = input("Enter your Telegram bot token: ").strip()
        c.execute("INSERT INTO tokens (id, token) VALUES (1, ?)", (TELEGRAM_TOKEN,))
        conn.commit()

# ===== BOT APP =====
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


# ===== ASYNC HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram messages and run pre-programmed or custom commands."""
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    logging.info(f"📩 Received: {text}")

    # ---- Run command ----
    if text.lower().startswith("cmd "):
        cmd_name = text[4:].strip()

        # Fetch command from commands.db
        with sqlite3.connect("db/commands.db") as conn:
            c = conn.cursor()
            c.execute("SELECT command FROM commands WHERE name=?", (cmd_name,))
            row = c.fetchone()

        if row:
            command = row[0]
            logging.info(f"⚡ Running pre-programmed command: {command}")
        else:
            command = cmd_name
            logging.info(f"⚡ Running custom command: {command}")

        try:
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

        # Save log in logs.db
        with sqlite3.connect("db/logs.db") as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO logs (command_name, command, output) VALUES (?, ?, ?)",
                (cmd_name if row else None, command, output)
            )
            conn.commit()

        # Send response
        await update.message.reply_text(output[:4000])

    # ---- Add new command ----
    elif text.lower().startswith("addcmd "):
        try:
            parts = text[7:].split("|", 1)
            if len(parts) != 2:
                await update.message.reply_text("❌ Format: addcmd command_name | shell_command")
                return

            name = parts[0].strip()
            command = parts[1].strip()

            with sqlite3.connect("db/commands.db") as conn:
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO commands (name, command) VALUES (?, ?)", (name, command))
                conn.commit()

            await update.message.reply_text(f"✅ Command '{name}' added successfully!")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to add command: {e}")

    # ---- List all commands ----
    elif text.lower() == "listcmd":
        with sqlite3.connect("db/commands.db") as conn:
            c = conn.cursor()
            c.execute("SELECT name, command FROM commands")
            rows = c.fetchall()

        if rows:
            msg = "\n".join([f"{name} → {cmd}" for name, cmd in rows])
        else:
            msg = "No commands saved yet."
        await update.message.reply_text(msg)

    # ---- Reply normally ----
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
