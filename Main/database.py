# database.py

import sqlite3
import os
from config import logger # Import logger from config

# Define database paths
COMMANDS_DB = "db/commands.db"
LOGS_DB = "db/logs.db"


def setup_databases():
    """Initializes all necessary SQLite tables."""
    os.makedirs("db", exist_ok=True)

    # ----- COMMANDS DB -----
    with sqlite3.connect(COMMANDS_DB) as conn:
        c = conn.cursor()
        c.execute("""
                  CREATE TABLE IF NOT EXISTS commands
                  (
                      id
                      INTEGER
                      PRIMARY
                      KEY
                      AUTOINCREMENT,
                      name
                      TEXT
                      UNIQUE
                      NOT
                      NULL,
                      command
                      TEXT
                      NOT
                      NULL
                  )
                  """)
        conn.commit()
        logger.info(f"Database {COMMANDS_DB} ready.")

    # ----- LOGS DB -----
    with sqlite3.connect(LOGS_DB) as conn:
        c = conn.cursor()
        c.execute("""
                  CREATE TABLE IF NOT EXISTS logs
                  (
                      id
                      INTEGER
                      PRIMARY
                      KEY
                      AUTOINCREMENT,
                      command_name
                      TEXT,
                      command
                      TEXT,
                      output
                      TEXT,
                      timestamp
                      DATETIME
                      DEFAULT
                      CURRENT_TIMESTAMP
                  )
                  """)
        conn.commit()
        logger.info(f"Database {LOGS_DB} ready.")


# ----- Database Functions for Handlers -----

def get_command(name: str) -> tuple | None:
    """Fetches a shell command by its name."""
    with sqlite3.connect(COMMANDS_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT command FROM commands WHERE name=?", (name,))
        return c.fetchone()


def save_command(name: str, command: str):
    """Inserts or replaces a pre-programmed command."""
    with sqlite3.connect(COMMANDS_DB) as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO commands (name, command) VALUES (?, ?)", (name, command))
        conn.commit()


def list_commands() -> list:
    """Fetches all saved command names and their shells."""
    with sqlite3.connect(COMMANDS_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT name, command FROM commands")
        return c.fetchall()


def log_execution(cmd_name: str | None, command: str, output: str):
    """Saves a command execution log to the logs database."""
    with sqlite3.connect(LOGS_DB) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO logs (command_name, command, output) VALUES (?, ?, ?)",
            (cmd_name, command, output)
        )
        conn.commit()