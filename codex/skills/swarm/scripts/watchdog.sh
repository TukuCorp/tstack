#!/usr/bin/env bash
# Swarm stall watchdog. Runs in its own Herdr tab, not in the caller, so it
# outlives the caller's turn and costs no caller tokens while lanes work.
#
# Usage: watchdog.sh <caller-pane-id> <marker-dir> <stall-minutes> <lane> [lane ...]
#
# For each lane it blocks on `herdr agent wait` (server-side, no polling) and
# prompts the caller pane only when something is wrong:
#   - the lane is `blocked` on an approval or question prompt;
#   - the lane stopped (idle/done) and no report marker appeared within the grace period;
#   - the lane is still `working` after <stall-minutes> with no report.
# A lane is finished once <marker-dir>/<lane>.reported exists (the brief's last
# action creates it) or the agent is gone (its tab was closed).
#
# Env: WATCHDOG_GRACE_S (default 120) seconds to wait after a stop for the report;
#      WATCHDOG_DRY=1 prints notices instead of sending them (for testing).
set -u
caller=$1 markers=$2 stall_min=$3
shift 3
grace=${WATCHDOG_GRACE_S:-120}
stall_ms=$((stall_min * 60000))

notify() {
  if [ "${WATCHDOG_DRY:-}" = 1 ]; then
    echo "NOTICE: $1"
  else
    herdr agent prompt "$caller" "$1" --timeout 30000 >/dev/null
  fi
}

status() {
  # Prints the lane's agent_status, or nothing if the agent no longer exists.
  herdr agent get "$1" 2>/dev/null | grep -o '"agent_status":"[a-z]*"' | head -1 | cut -d'"' -f4
}

reported() { [ -f "$markers/$1.reported" ]; }

watch_lane() {
  lane=$1
  while :; do
    reported "$lane" && return
    herdr agent wait "$lane" --timeout "$stall_ms" >/dev/null 2>&1
    reported "$lane" && return
    st=$(status "$lane")
    case "$st" in
      "") return ;;
      working)
        notify "watchdog: $lane still working after $stall_min min with no report-back; read its pane" ;;
      blocked)
        notify "watchdog: $lane is blocked on a prompt; read its pane and answer it"
        herdr agent wait "$lane" --until working >/dev/null 2>&1 || return ;;
      *)
        sleep "$grace"
        reported "$lane" && return
        st=$(status "$lane")
        [ -z "$st" ] && return
        if [ "$st" != working ]; then
          notify "watchdog: $lane stopped ($st) without a report-back; read its pane and output file"
          return
        fi ;;
    esac
  done
}

for lane in "$@"; do
  watch_lane "$lane" &
done
wait
echo "watchdog: all lanes finished"
