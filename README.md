

<p align="center">
  <img src="https://raw.githubusercontent.com/rhshourav/CyroCore/CyroBranch/img/cryoCroeLogo_git.png" alt="CryoCore Logo" width="150"/>
</p>


# <p align="center">🤖 **Cryo**Core™️</p>

 <p align="center">
  <!-- Build / Status -->
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status">
  <!-- Python Version -->
  <img src="https://img.shields.io/badge/python-3.10-blue" alt="Python">
  <!-- License -->
  <img src="https://img.shields.io/badge/license-GPL 2.0-orange" alt="License">
  <!-- Telegram Bot -->
  <img src="https://img.shields.io/badge/Telegram-Bot-blue" alt="Telegram Bot">
</p>

A Python-based Telegram bot that:
- Stores credentials, tokens, logs, and pre-stored commands in SQLite databases.
- Executes shell commands remotely via Telegram (`cmd <command>`).
- Sends back the command output to your Telegram chat.

---

## ⚡ Features

- **Database storage**:
  - `credentials.db` → Stores the Telegram bot token securely.
  - `commands.db` → Stores pre-defined reusable commands.
  - `logs.db` → Stores logs of all executed commands, including outputs and timestamps.

- **Command Execution**:
  - Prefix messages with `cmd` to run commands.
  - Example:
    ```
    cmd dir
    cmd echo Hello World
    ```
  - Supports both custom shell commands and pre-stored commands.

- **Pre-defined Commands**:
  - Add new commands:
    ```
    addcmd <name> | <shell command>
    ```
  - List all stored commands:
    ```
    listcmd
    ```

- **Logging**:
  - Every command execution is logged with:
    - Command name (if pre-stored)
    - Actual shell command
    - Output
    - Timestamp

- **Auto Setup**:
  - Databases are created automatically on first run if missing.
  - Prompts for Telegram bot token if none is stored.

---

## 🛠 Requirements

- Python **3.10+**
- Install dependencies:
  ```bash
  pip install python-telegram-bot==20.7
  ```

---

## 🚀 Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/rhshourav/CryoCore.git
   cd CryoCore
   ```

2. Run the bot:
   ```bash
   python CryoCoreBot.py
   ```

3. Use Telegram commands:
   - Run a shell command: `cmd <command>`
   - Add a pre-defined command: `addcmd <name> | <command>`
   - List pre-defined commands: `listcmd`


