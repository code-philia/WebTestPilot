#!/bin/bash

PANE="3"              # target tmux pane
INTERVAL=10           # check every 10 seconds
expected="... Indico not ready yet, retrying in 5s"
error_pattern="<urlopen error \[Errno 111\] Connection refused>"

while true; do
    # Get last 10 lines from tmux pane 3, trim spaces
    last_lines=$(tmux capture-pane -t ${PANE} -S -10 -E - -p \
        | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # ---- Condition 1: all 10 lines are the "not ready" message ----
    all_match=true
    while IFS= read -r line; do
        if [ "$line" != "$expected" ]; then
            all_match=false
            break
        fi
    done <<< "$last_lines"

    # ---- Condition 2: any line contains the error message ----
    has_error=false
    if echo "$last_lines" | grep -q "$error_pattern"; then
        has_error=true
    fi

    # ---- Trigger if either condition is true ----
    if [ "$all_match" = true ] || [ "$has_error" = true ]; then
        echo "🚨 Indico issue detected, restarting..."
        docker rm -f $(docker ps -aq)   # remove all containers
        docker volume rm $(docker volume ls -q)  # remove all volumes
        ./stop_app.sh indico
        ./start_app.sh indico
        sleep 180
    else
        echo "ℹ️ No issue, sleeping..."
        sleep "$INTERVAL"
    fi
done
