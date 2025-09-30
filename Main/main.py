# main.py

import asyncio
from telegram.ext import Application, MessageHandler, filters
from config import load_telegram_token, logger
from database import setup_databases
from handlers import handle_message


def main():
    """The main function to set up and run the bot."""

    # 1. Setup
    try:
        TELEGRAM_TOKEN = load_telegram_token()
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        return

    setup_databases()

    # 2. Build App
    telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
    logger.info("✅ Telegram Application built successfully.")

    # 3. Register Handler
    # Process all text messages that are NOT official Telegram /commands
    telegram_app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # 4. Run Polling
    logger.info("🚀 Bot is starting... Press Ctrl+C to stop.")
    telegram_app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()