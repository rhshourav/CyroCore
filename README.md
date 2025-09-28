# 🤖 Telegram Command Bot

A Python-based Telegram bot that:
- Stores credentials, tokens, logs, and pre-stored commands in SQLite databases.  
- Executes shell commands remotely via Telegram (`cmd <command>`).  
- Sends back the command output to your Telegram chat.  

---

## ⚡ Features
- **Database storage**:
  - `credentials.db` → Stores the Telegram bot token (secure storage).  
  - `logs.db` → Stores logs of all executed commands and results.  
  - `commands.db` → Can store pre-defined reusable commands.  
- **Command Execution**:  
  - Prefix messages with `cmd` to run commands.  
  - Example:  
    ```
    cmd dir
    cmd echo Hello World
    ```
- **Logging**:  
  - All inputs, outputs, and errors are stored in `logs.db`.  
- **Auto Setup**:  
  - If databases are missing, they are created automatically on first run.  
  - If no token is stored, you’ll be prompted for it.

---

## 🛠 Requirements
- Python **3.10+**
- Install dependencies:
  ```bash
  pip install python-telegram-bot==20.7
