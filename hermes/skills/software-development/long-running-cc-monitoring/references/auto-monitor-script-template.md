# Automated Monitor Script Template

Reusable bash template for background monitoring of Claude Code in tmux during fully autonomous runs. Copy this into a cron job's working directory as `.monitor.sh`, adjust the parameters, then run via `terminal(background=true, notify_on_complete=true)`.

## Template

```bash
#!/bin/bash
# Auto-monitor for Claude Code in tmux — polls, auto-answers, detects completion

SESSION="cc-<project>"          # tmux session name
COMPLETE_FILE="<workdir>/<output-artifact.md>"  # CC creates this when done
POLL_INTERVAL=10                # seconds between polls
SILENT_THRESHOLD=6              # consecutive idle polls before assuming completion

# Model-switch dialog uses "Switch model" / "Yes, switch to" — NOT AskUserQuestion / Recommended
QUESTION_PATTERNS="Continue|Proceed|Allow|Approve|Enter to confirm|Enter to continue|open the URL|type yes to confirm|Switch model|Yes, switch to"

SILENT_COUNT=0
LAST_ACTIVE=""

echo "[monitor] Starting at $(date)"
echo "[monitor] Session: $SESSION | Poll: ${POLL_INTERVAL}s | Complete file: $COMPLETE_FILE"

while true; do
  # Capture the last few lines of the tmux pane
  OUTPUT=$(tmux capture-pane -t $SESSION -p -S -3 2>/dev/null)
  if [ $? -ne 0 ]; then
    echo "[monitor] tmux session '$SESSION' no longer exists at $(date)"
    break
  fi

  LAST_LINE=$(echo "$OUTPUT" | tail -1)

  # Check if completion artifact exists
  if [ -f "$COMPLETE_FILE" ]; then
    echo "[monitor] Complete file found at $(date)"
    break
  fi

  CURRENT_OUTPUT=$(tmux capture-pane -t $SESSION -p | tail -5)

  # If CC is at the prompt (❯), check for questions
  if echo "$LAST_LINE" | grep -q "❯"; then
    FULL_OUTPUT=$(tmux capture-pane -t $SESSION -p -S -10)

    # Look for question keywords
    if echo "$FULL_OUTPUT" | grep -qiE "$QUESTION_PATTERNS"; then
      echo "[monitor] Question detected at $(date): $(echo "$FULL_OUTPUT" | tail -3)"
      tmux send-keys -t $SESSION Enter
      echo "[monitor] Sent Enter (accepted default)"
      SILENT_COUNT=0
    fi

    # Track idle time (no new output)
    if [ "$CURRENT_OUTPUT" = "$LAST_ACTIVE" ]; then
      SILENT_COUNT=$((SILENT_COUNT + 1))
    else
      SILENT_COUNT=0
      LAST_ACTIVE="$CURRENT_OUTPUT"
    fi

    # If idle for threshold, double-check and bail
    if [ $SILENT_COUNT -ge $SILENT_THRESHOLD ]; then
      echo "[monitor] Idle $((SILENT_COUNT * POLL_INTERVAL))s at $(date) — may be done"
      if [ -f "$COMPLETE_FILE" ]; then
        echo "[monitor] Complete file confirmed"
        break
      fi
    fi
  else
    SILENT_COUNT=0  # CC is actively working
  fi

  sleep $POLL_INTERVAL
done

echo "[monitor] Ended at $(date)"

# Report
if [ -f "$COMPLETE_FILE" ]; then
  echo "[monitor] === Session Complete ==="
  cat "$COMPLETE_FILE"
else
  echo "[monitor] No complete file. Current tmux state:"
  tmux capture-pane -t $SESSION -p -S -30 2>/dev/null || echo "[monitor] Session gone"
fi
```

## Key Dialog Detection Notes

The template's `QUESTION_PATTERNS` must include dialog-specific phrases because CC uses different vocabulary for different prompts:

| Dialog type | Detection phrase(s) | Notes |
|------------|-------------------|-------|
| Model-switch (`/model name`) | "Switch model" or "Yes, switch to" | NOT caught by AskUserQuestion / Recommended patterns |
| Workspace trust | "trust this folder" | First visit only; cached after that |
| Permissions bypass | "Yes, I accept" or "No, exit" | Default is WRONG (No, exit); must send Down+Enter |
| Context pickers | "Recommended" / "choose" / "option" | Multi-select; needs number keys, not just Enter |
| Session limit error | "hit your session limit" | Non-recoverable; log the reset time and stop |

## Integration in a Cron Job Prompt

When writing a cron job that uses this pattern:

```markdown
## Step 1: Launch CC in tmux

tmux new-session -d -s cc-<project> -x 140 -y 40
tmux send-keys -t cc-<project> 'cd <workdir> && claude --model <model>' Enter
Sleep 10s for startup.

## Step 2: Send the task prompt

Write a prompt file, then send it via tmux send-keys:
tmux send-keys -t cc-<project> -l "$(cat <workdir>/.cc_prompt.txt)"
tmux send-keys -t cc-<project> Enter

## Step 3: Deploy monitor in background

Write the monitor script using the template above, adjusting:
- SESSION = "cc-<project>"
- COMPLETE_FILE = "<workdir>/<output-artifact.md>"

Then run:
terminal(background=true, notify_on_complete=true, command="bash <workdir>/.monitor.sh")

## Step 4: When notified, read results, clean up

- Read the complete file
- Kill tmux: tmux kill-session -t cc-<project>
- Clean up temp files
- Report to user
```

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `POLL_INTERVAL` | 10 | Increase to 15-30 if the tmux session is on a remote machine with high-latency SSH |
| `SILENT_THRESHOLD` | 6 | Increase for very long-running CC tasks that may have pauses between phases (e.g., waiting for MCP server responses) |
| `QUESTION_PATTERNS` | Continue, Proceed, Allow, ... | Add task-specific patterns if CC asks questions with different phrasing |
| `COMPLETE_FILE` | (none) | Point to whatever file CC creates when done — could be a summary report, a commit hash file, etc. |

## Pitfalls

1. **Capture-pane on a dead session** silently returns empty output. Always check `$?` from `tmux capture-pane` to detect if the session was killed externally.
2. **Question patterns are case-insensitive** (uses `grep -i`). The template's default list covers permission prompts, "Continue?" questions, URL-opening confirmations, and model-switch dialogs.
3. **`send-keys` on Windows (git-bash)** may write text to the input line without submitting it. The template only uses Enter (not text submission), which is safe — bare Enter at the ❯ prompt either submits the current input or is a harmless no-op.
4. **The script only sends Enter** — it cannot choose between alternatives. For tasks where CC presents genuine branching decisions (which branch to merge, which approach to take), use manual monitoring instead.
