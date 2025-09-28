

<p align="center">
  <img src="https://raw.githubusercontent.com/rhshourav/CyroCore/CyroBranch/img/cyroCroeLogo_git.png" alt="CyroCore Logo" width="150"/>
</p>

# <p align="center">🤖 **Cyro**Core™️</p>


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
   git clone https://github.com/rhshourav/CyroCore.git
   cd CyroCore
   ```

2. Run the bot:
   ```bash
   python CyroCoreBot.py
   ```

3. Use Telegram commands:
   - Run a shell command: `cmd <command>`
   - Add a pre-defined command: `addcmd <name> | <command>`
   - List pre-defined commands: `listcmd`


