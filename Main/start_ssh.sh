#!/bin/bash

# --- Configuration ---
SSH_PORT=22
DURATION=1800  # 30 minutes in seconds
LOG_FILE="/tmp/ngrok_ssh_log.txt"
# Ngrok is often in the user's PATH, if not, use the full path: /usr/local/bin/ngrok

# --- Start Tunnel in Background ---
# The command starts ngrok, tunnels port 22, and saves the connection details to a log file.
# Note: The output format relies on ngrok's 'start' command output, adjust if using 'http' or other commands.
ngrok tcp $SSH_PORT --log "stdout" > "$LOG_FILE" &
NGROK_PID=$!  # Store the Process ID of ngrok
echo "NGROK_PID:$NGROK_PID" >> "$LOG_FILE"

# --- Wait for ngrok to initialize and get the URL ---
sleep 5

# --- Extract Connection Info ---
# Grep the log file for the public connection URL (often on line 2-4)
TUNNEL_URL=$(grep "url" "$LOG_FILE" | head -n 1 | awk '{print $NF}' | sed 's/tcp:\/\///')

# --- Check if URL was captured ---
if [ -z "$TUNNEL_URL" ]; then
    echo "ERROR: Failed to start ngrok or capture URL."
    # Kill the background process if it failed to start properly
    kill "$NGROK_PID" 2>/dev/null
    exit 1
fi

# --- Schedule Termination (30 minutes) ---
(
    sleep $DURATION
    kill "$NGROK_PID" 2>/dev/null  # Kill the ngrok process
    rm "$LOG_FILE" 2>/dev/null      # Clean up the log file
    echo "--- SSH Session Terminated After 30 Minutes ---"
) &

# --- Output to Telegram ---
echo "✅ SSH Session Live (30 Minutes)"
echo "----------------------------------------------------"
echo "Connection details:"
echo "User: <Your_SSH_Username>"
echo "Host: $TUNNEL_URL"
echo "----------------------------------------------------"
echo "Session will automatically close in 30 minutes."

exit 0