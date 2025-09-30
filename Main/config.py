# config.py

import sqlite3
import logging
import os

# ===== ENABLE LOGGING =====
# Configure logging to show timestamps and source
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ===== CONFIGURATION / TOKEN LOADING =====
def load_telegram_token() -> str:
    """Loads the Telegram bot token from the database, prompting if missing."""

    # Ensure the database directory exists
    os.makedirs("db", exist_ok=True)

    TELEGRAM_TOKEN = None
    DB_PATH = "db/tokens.db"

    # Connect to the tokens database
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY, token TEXT)")
        conn.commit()

        c.execute("SELECT token FROM tokens WHERE id=1")
        row = c.fetchone()

        if row:
            TELEGRAM_TOKEN = row[0]
            logger.info("Telegram token loaded from database.")
        else:
            TELEGRAM_TOKEN = input("Enter your Telegram bot token: ").strip()
            if not TELEGRAM_TOKEN:
                raise ValueError("Telegram token cannot be empty.")

            c.execute("INSERT INTO tokens (id, token) VALUES (1, ?)", (TELEGRAM_TOKEN,))
            conn.commit()
            logger.info("New Telegram token saved to database.")

    return TELEGRAM_TOKEN