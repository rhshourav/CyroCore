# handlers.py

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import get_command, save_command, list_commands, log_execution
from config import logger


# ===== ASYNC HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram messages and run pre-programmed or custom commands."""

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    # chat_id = update.effective_chat.id # chat_id is available here if needed for whitelisting
    logger.info(f"📩 Received: {text}")

    # ---- Run command (cmd) ----
    if text.lower().startswith("cmd "):
        await handle_cmd_execution(update, text[4:].strip())

    # ---- Add new command (addcmd) ----
    elif text.lower().startswith("addcmd "):
        await handle_add_command(update, text[7:].strip())

    # ---- List all commands (listcmd) ----
    elif text.lower() == "listcmd":
        await handle_list_commands(update)

    # ---- Reply normally ----
    else:
        await update.message.reply_text(f"You said: {text}")


async def handle_cmd_execution(update: Update, cmd_input: str):
    """Executes a pre-programmed or custom shell command."""

    cmd_name = cmd_input
    row = get_command(cmd_name)

    if row:
        command = row[0]
        is_preprogrammed = True
        logger.info(f"⚡ Running pre-programmed command: {command}")
    else:
        command = cmd_input
        is_preprogrammed = False
        logger.info(f"⚡ Running custom command: {command}")

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

    # Save log
    log_execution(cmd_name if is_preprogrammed else None, command, output)

    # Send response (using HTML for code formatting)
    formatted_output = f"<pre>{output[:4000]}</pre>"
    await update.message.reply_html(formatted_output)


async def handle_add_command(update: Update, command_text: str):
    """Handles adding a new pre-programmed command."""
    try:
        parts = command_text.split("|", 1)
        if len(parts) != 2:
            await update.message.reply_text("❌ Format: addcmd command_name | shell_command")
            return

        name = parts[0].strip()
        command = parts[1].strip()

        save_command(name, command)
        await update.message.reply_text(f"✅ Command '{name}' added successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to add command: {e}")


async def handle_list_commands(update: Update):
    """Handles listing all saved commands."""
    rows = list_commands()

    if rows:
        msg = "Saved Commands:\n" + "\n".join([f"`{name}` → `{cmd}`" for name, cmd in rows])
    else:
        msg = "No commands saved yet."

    # Send response with Markdown formatting
    await update.message.reply_text(msg, parse_mode='Markdown')