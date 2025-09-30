# CryoCoreBot Improvement Roadmap

Your existing bot is a powerful foundation for a remote executor, but it's currently highly vulnerable. The immediate focus must be **security**, followed by **usability** and **advanced features**.

---

## 1. Top-Priority Security & Robustness

These changes are essential before running the bot in any shared or production environment.

### 1.1 Mandatory User Whitelisting

The most critical flaw is that *any user* can potentially send commands if they find your bot.

* **Action:** Implement a `whitelist` database table or simply hardcode a list of allowed Telegram **`user_id`s** and check against `update.effective_user.id` at the very beginning of the `handle_message` function.
* **Feature:** Add new administrative commands, accessible only by the primary admin ID, to manage this list:
    * `/auth <user_id>`: Add a new user to the whitelist.
    * `/unauth <user_id>`: Remove a user.
    * `/listusers`: View all authorized users.

### 1.2 Output Management (File Uploads)

Truncating command output at 4000 characters is limiting and can hide important error messages.

* **Action:** Modify the command execution block:
    1.  If `output` is less than 4000 characters, send it as a standard message, using **Markdown or HTML formatting** for a code block (e.g., `<pre>output</pre>`).
    2.  If `output` is greater than 4000 characters, save the full output to a temporary `.txt` file, upload the file to Telegram, and send a message like, "✅ Command complete. Output attached."

### 1.3 Shell Command Sanitization

While whitelisting helps, it's safer to prevent common shell injection attacks, even from trusted users.

* **Action:** For the **custom command execution path** (`cmd` without a saved name), proactively block dangerous characters that facilitate command chaining:
    * Disallow or warn against inputs containing symbols like: **`;`**, **`|`**, **`&&`**, **`||`**, **`$`** (for variable expansion), **`\``** (backticks for command substitution).

---

## 2. Advanced Features and Usability

Once secured, you can focus on making the bot more powerful and user-friendly.

### 2.1 Full Command Management Suite

Currently, you can add commands but not easily delete or officially register them.

| Feature | New Command | Functionality |
| :--- | :--- | :--- |
| **Official Commands** | Use Telegram's native **`/` commands** (`/cmd`, `/addcmd`, `/listcmd`) for better UX and auto-complete. |
| **Delete Command** | `/delcmd <name>` | Removes a pre-programmed command from `commands.db`. |
| **Help/Info** | `/help` | Sends a summary of all available commands (including pre-programmed ones from `commands.db`). |
| **Command Aliases** | `/alias <new_name> <existing_name>` | Allows multiple shortcut names for the same shell command. E.g., `alias ls | ls -la` and `alias files | ls -la`. |

### 2.2 Shell Argument Handling

Allowing dynamic input into saved commands transforms them into powerful parameterized scripts.

* **Implementation:** Adopt a simple variable placeholder system (e.g., `$1`, `$2`).
    * *Stored Command:* `addcmd killapp | kill -9 $(pgrep $1)`
    * *User Execution:* `cmd killapp nginx`
    * *Bot executes:* `kill -9 $(pgrep nginx)`

### 2.3 File Transfer Capability

This is extremely useful for remote management, diagnostics, and moving configuration files.

* **Upload (Bot Side)**: Use a `MessageHandler` to capture incoming files/documents. When a user uploads a file, the bot saves it to a designated directory on the server (e.g., `~/cryocorebot_uploads/`).
* **Download (User Side)**: Introduce a new command:
    * `/getfile <path>`: Bot reads the specified file (with strict path checks to prevent accessing sensitive areas) and sends it back to the user via `send_document`.
    * **Security Note:** Absolutely enforce a safe root directory (`/home/botuser/safe_files/`) for downloads and only allow paths *within* that directory.

### 2.4 Persistent Task Tracking

For long-running processes (e.g., backups, updates), the bot should handle them in the background and report back later.

* **Action:** When a command is run:
    1.  Store the **Process ID (PID)** and the **`chat_id`** in your `logs.db`.
    2.  Send an immediate "Task started: PID **[1234]**" message.
    3.  Introduce a `/tasks` command to list all active PIDs started by the bot.
    4.  Introduce a `/kill <pid>` command to stop a running task (requires sending a `SIGTERM` signal to the process).

---

## 3. Deployment and Maintenance

### 3.1 Better Configuration

Instead of manually editing the `tokens.db` on first run, use standard configuration methods.

* **Action:** Load the Telegram token from a **`.env` file** (using the `python-dotenv` library) or an environment variable. This is cleaner and more secure for deployment.

### 3.2 Enhanced Logging

The current logging is functional but basic.

* **Action:** Improve the internal `logging.basicConfig` to include a file handler, writing all internal events (startup, user messages, errors) to a separate log file (`cryocorebot.log`) in addition to the console output. This separates runtime events from command execution history (`logs.db`).