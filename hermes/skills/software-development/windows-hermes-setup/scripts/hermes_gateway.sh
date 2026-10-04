#!/bin/bash
# Hermes Gateway auto-restart script with PID-lock guard and OOM protection.
# Place at: ~/AppData/Local/hermes/gateway-service/hermes_gateway.sh
# This should be the ONLY auto-start source for the gateway.
# It checks the gateway.lock PID file before starting a new gateway
# to prevent multiple sources from racing each other.
#
# Companion to SKILL.md section "Gateway Restart Loop Conflicts".
# Also see scripts/install_single_scheduled_task.cmd for the matching
# Windows Task Scheduler entry that runs this script on logon.

LOCK_FILE="$HOME/AppData/Local/hermes/gateway.lock"

while true; do
    # Check if a gateway is already running by reading the JSON lock
    if [ -f "$LOCK_FILE" ]; then
        EXISTING_PID=$(python -c "import json; print(json.load(open(r'$LOCK_FILE'))['pid'])" 2>/dev/null)
        if [ -n "$EXISTING_PID" ] && ps -p $EXISTING_PID > /dev/null 2>&1; then
            echo "[$(date)] Gateway already running (PID $EXISTING_PID), skipping"
            sleep 30
            continue
        fi
    fi

    echo "[$(date)] Starting Hermes Gateway..."
    # Start in background so we can set High priority before the gateway needs memory
    /c/Users/tukum/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe gateway run &
    GW_PID=$!
    sleep 5
    wmic process where "processid=$GW_PID" CALL setpriority 128 > /dev/null 2>&1
    echo "[$(date)] Gateway PID $GW_PID set to High priority"
    wait $GW_PID
    EXIT_CODE=$?
    echo "[$(date)] Gateway exited with code $EXIT_CODE. Restarting in 10s..."
    sleep 10
done
