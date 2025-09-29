# CryoCoreBot

A small, simple Telegram bot for running (and storing) pre-programmed shell commands, logging their outputs, and letting you run ad-hoc shell commands via chat. This README explains every part of the provided `main.py` (the bot script) in depth and gives installation, configuration, security, deployment, and troubleshooting guidance.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Repository layout / file structure](#repository-layout--file-structure)
5. [Installation (quick)](#installation-quick)
6. [Configuration & environment variables](#configuration--environment-variables)
7. [Database schema explained](#database-schema-explained)
8. [Detailed code walkthrough](#detailed-code-walkthrough)
   - [Imports and logging](#imports-and-logging)
   - [Database setup](#database-setup)
   - [Loading the Telegram token](#loading-the-telegram-token)
   - [Building the telegram Application](#building-the-telegram-application)
   - [The ](#the-handle_message-handler-full-flow)[`handle_message`](#the-handle_message-handler-full-flow)[ handler (full flow)](#the-handle_message-handler-full-flow)
   - [Registering the handler and run loop](#registering-the-handler-and-run-loop)
9. [How to use the bot (examples)](#how-to-use-the-bot-examples)
10. [Security considerations & hardening](#security-considerations--hardening)
11. [Suggested improvements & TODOs](#suggested-improvements--todos)
12. [Troubleshooting](#troubleshooting)
13. [Deployment examples (systemd + Docker)](#deployment-examples-systemd--docker)
14. [Contributing](#contributing)
15. [License](#license)

---

## Overview

The bot monitors plain text messages (not slash commands) and supports three main features:

- `addcmd <name>|<command>` — save a pre-programmed command under a short name
- `cmd <name-or-shell>` — run a stored command (if `<name>` exists) or run the rest as a shell command
- `listcmd` — list saved commands

Every executed command (pre-programmed or ad-hoc) is logged into a SQLite database with output and timestamp.

> **Important:** The bot executes shell commands directly using `asyncio.create_subprocess_shell` — this is powerful but *dangerous* when the bot accepts commands from untrusted users. See Security considerations.

---

## Features

- Simple persistent storage using SQLite (`db/credentials.db`)
- Add, list, and execute named commands via Telegram chat
- Execution logs stored with timestamps
- Asynchronous subprocess execution so the bot remains responsive
- Minimal dependencies (primarily `python-telegram-bot`)

---

## Requirements

- Python **3.10+** (3.11 recommended)
- `python-telegram-bot` v20+ (the script uses the modern `Application` API)

Suggested `requirements.txt`:

```
python-telegram-bot>=20
python-dotenv>=1.0  # optional, if you want .env support
```

---

## Repository layout / file structure

```
CryoreBot/
├─ db/                      # SQLite DB directory (created at runtime)
│  └─ credentials.db        # main database (contains tokens, commands, logs)
├─ main.py                  # the bot script (the code you provided)
├─ requirements.txt         # dependencies (see Requirements)
├─ README.md                # this file
├─ Dockerfile               # optional (example in README)
└─ systemd/                 # optional systemd unit example
```

---

## Installation (quick)

1. Clone the repo

```bash
git clone <your-repo-url>
cd CryoCoreBot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Provide your Telegram bot token (see Configuration section). The script will prompt for a token the first time and store it in the database.

3. Run the bot:

```bash
python main.py
```

The script creates `db/` automatically, and will write the token to `db/credentials.db` the first time you run it.

---

## Configuration & environment variables

The script currently tries to read the token from the `tokens` table in the SQLite database. If `tokens.id=1` is not present, it prompts interactively for a token and inserts it into the database.

**Recommended change (production):** don't rely on interactive input — set `TELEGRAM_TOKEN` via environment variable and/or `.env` file. Example modification at the top of the script:

```python
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    # fallback to DB or interactive prompt (as present in your code)
```

**Paths:** use an absolute DB path in production to avoid `unable to open database file` errors, e.g.:

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'db')
os.makedirs(DB_DIR, exist_ok=True)
DB_FILE = os.path.join(DB_DIR, 'credentials.db')
```

---

## Database schema explained

The SQLite database (`db/credentials.db`) contains 3 tables:

1. `tokens`

```sql
CREATE TABLE IF NOT EXISTS tokens (
  id INTEGER PRIMARY KEY,
  token TEXT
);
```

- Stores the Telegram bot token. The script expects a single row with `id=1`.

2. `commands`

```sql
CREATE TABLE IF NOT EXISTS commands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  command TEXT NOT NULL
);
```

- `name` is a short alias used with `cmd <name>`; `command` is the full shell command that will be executed.
- `INSERT OR REPLACE` is used so adding a command with an existing name will overwrite it.

3. `logs`

```sql
CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  command_name TEXT,
  command TEXT,
  output TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

- Each time the bot executes a command (named or ad-hoc) it inserts a log row. `command_name` is nullable (ad-hoc commands are stored with `NULL` for `command_name`).

---

## Detailed code walkthrough

This section walks through the important parts of the script and explains why they are there and how they work.

### Imports and logging

```python
import sqlite3
import asyncio
import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
```

- `sqlite3` for the local database.
- `asyncio` to run shell commands asynchronously so the bot event loop is not blocked.
- `python-telegram-bot` provides the `Application` interface used by v20+ of the library.
- `logging` is configured to `INFO` level; you can change to `DEBUG` for more verbose logs.

### Database setup

```python
os.makedirs("db", exist_ok=True)
DB_FILE = "db/credentials.db"
conn = sqlite3.connect(DB_FILE)
...
conn.commit()
```

- Creates the `db/` directory if it does not exist (this is the fix for the `unable to open database file` issue).
- Creates the three tables described in the schema section.
- Commits and closes the connection later.

**Note:** the script opens and closes new connections inside handlers. For higher concurrency or production use, prefer a small connection pool or execute DB code in a separate thread via `asyncio.to_thread` to avoid blocking the event loop.

### Loading the Telegram token

```python
c.execute("SELECT token FROM tokens WHERE id=1")
row = c.fetchone()
if row:
    TELEGRAM_TOKEN = row[0]
else:
    TELEGRAM_TOKEN = input("Enter your Telegram bot token: ").strip()
    c.execute("INSERT INTO tokens (id, token) VALUES (1, ?)", (TELEGRAM_TOKEN,))
    conn.commit()
```

- If a token row exists in the DB it uses that. Otherwise it asks interactively and stores it.
- **Production tip:** prefer `os.getenv('TELEGRAM_TOKEN')` to avoid interactive prompts and to allow containerized runtime.

### Building the telegram Application

```python
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
```

- Creates the bot application object used to register handlers and to start polling.

### The `handle_message` handler (full flow)

This is the heart of the bot. Summary of logic:

1. Trim incoming text and get `chat_id`.

2. If the message starts with `cmd `:

   - Extract `cmd_name` (text after `cmd `)
   - Look up `cmd_name` in `commands` table.
   - If found, treat `command` as the stored command; otherwise treat `cmd_name` as a raw shell command.
   - Run `asyncio.create_subprocess_shell(...)` to execute the command asynchronously.
   - Read `stdout`/`stderr`, decode, and produce `output` (fallback `✅ Command executed (no output)` if both empty).
   - Insert a row into `logs` with the command and output.
   - Reply to the user with `output[:4000]` (truncates to avoid Telegram limits).

3. If message starts with `addcmd `:

   - Expect the string form `addcmd name|command`.
   - `name` and `command` are split on the first `|` and saved to `commands` table via `INSERT OR REPLACE`.

4. If message equals `listcmd`:

   - Fetch and list all saved commands.

5. Otherwise reply with a simple echo `You said: {text}`.

**Important details & gotchas inside the handler:**

- The code opens a fresh SQLite connection for every command execution / listing / insert. That works for light use, but for more load it’s better to push DB operations to a thread or reuse a connection safely.

- When logging, the script uses `cmd_name if row else None` — this stores the alias only when the command was found. For ad-hoc commands it records `NULL`.

- The script trims output to 4000 characters. Telegram’s message limit is 4096 characters; trimming is sensible but you may prefer to send as a file if the output is long.

- `parts = text[7:].split("|", 1)` will raise if the user sends `addcmd ` without `|` or a name. The `except` branch will catch and report an error, but you may want to validate input and send a helpful usage message.

### Registering the handler and run loop

```python
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def main():
    print("✅ Bot is starting...")
    telegram_app.run_polling(allowed_updates=["message"])
```

- The handler listens for *plain text messages* and explicitly excludes library-style `COMMAND` filters.
- `run_polling` starts the long-polling loop. For production you may use webhooks; polling is easiest for small deployments.

---

## How to use the bot (examples)

### Add a pre-programmed command

```
User: addcmd uptime|uptime -p
Bot: ✅ Command 'uptime' added successfully!
```

### Execute a named command

```
User: cmd uptime
Bot: up 2 hours, 3 minutes
```

### Execute ad-hoc shell command

```
User: cmd ls -la /tmp
Bot: total 8\ndrwxrwxrwt ...
```

### List commands

```
User: listcmd
Bot: uptime → uptime -p\nbackup → /usr/local/bin/backup.sh
```

---

