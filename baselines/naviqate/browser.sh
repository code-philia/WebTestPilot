#!/bin/bash

PORT=9222
WINDOW_SIZE="1280,720"
PROFILE_DIR="/tmp/chrome-profile"

# Kill any existing Chrome instance using that port
pkill -f "google-chrome.*--remote-debugging-port=${PORT}" || true

# Make sure profile dir exists
mkdir -p "$PROFILE_DIR"

# Start Chrome
echo "Starting local Chrome..."
google-chrome \
    --remote-debugging-port=${PORT} \
    --remote-debugging-address=127.0.0.1 \
    --user-data-dir=${PROFILE_DIR} \
    --no-first-run \
    --no-default-browser-check \
    --disable-extensions \
    --headless=new \
    --window-size=${WINDOW_SIZE} \
    > /tmp/chrome.log 2>&1 &

CHROME_PID=$!
echo "Chrome PID: $CHROME_PID"

# Wait for "DevTools listening on" in logs
echo "Waiting for Chrome DevTools endpoint..."
while true; do
    endpoint=$(grep -oE "ws://[^ ]+" /tmp/chrome.log)
    if [ -n "$endpoint" ]; then
        echo "DevTools endpoint: $endpoint"
        break
    fi
    sleep 0.5
done
