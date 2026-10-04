#!/usr/bin/env python3
"""
CC Nightly Orchestrator (herdr transport)
=========================================
Cooldown-aware shuffle-pick of a project from ~/.hermes/cc-nightly-projects.json,
launch Claude Code in a herdr workspace with Remote Control enabled. If the repo
has any unfinished plan, do NOT start anything new: enter backlog mode and triage
the existing plans/ instead. Otherwise: brainstorm, then plan, then STOP — the
execution prompt is staged in the session, unsubmitted, for the operator to run
themselves from the Claude mobile app. This job never writes code and never
pushes to a branch on its own.

TRANSPORT: this variant drives Claude through herdr (the agent runtime) instead
of tmux. Each run creates a dedicated herdr workspace whose root pane hosts the
`claude` TUI via `agent start`. Prompts are delivered with `agent prompt` (which
delivers multi-line text intact — the paste-collapse bug that affected tmux
send-keys is avoided). Marker detection reads the pane with `agent read` (recent
when idle, visible mid-run). Prior sessions stay alive (unique names per run) so
they remain resumable from the Claude mobile app via Remote Control; sessions
older than SESSION_MAX_AGE_H are pruned by closing their herdr workspace.

State tracked in ~/.hermes/cc-nightly-state.json (shuffle-playlist, no repeats
within COOLDOWN_DAYS). Outcomes appended to ~/.hermes/cc-nightly-ledger.jsonl;
projects with 2+ consecutive failed runs are skipped until a run succeeds or the
streak is cleared manually. Runs defer (without consuming the project's shuffle
slot) when less than USAGE_MIN_PCT of the Claude usage window remains at spawn.
Every exit path sends exactly one Discord notification via `hermes send` — see
notify(). Verbose logs live in ~/.hermes/cc-nightly-logs/, not stdout.
"""

import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 stdout regardless of the parent process's console codepage —
# Windows can default to cp1252, which crashes on the emoji markers log()
# uses throughout (🔄 ⏭ ⚠ ✓). Mirrors the encoding="utf-8" forcing already
# applied to every subprocess call below.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# ── Config ───────────────────────────────────────────────────────────────
STATE_FILE = Path.home() / ".hermes" / "cc-nightly-state.json"
LEDGER_FILE = Path.home() / ".hermes" / "cc-nightly-ledger.jsonl"
PROJECTS_CONFIG_FILE = Path.home() / ".hermes" / "cc-nightly-projects.json"
# Time-boxed escape hatch: while the timestamp inside is in the future,
# pick_project() ignores COOLDOWN_DAYS so a run can be observed on demand
# instead of waiting for the rotation. See cooldown_override_active().
COOLDOWN_OVERRIDE_FILE = Path.home() / ".hermes" / "cc-nightly-cooldown-override.json"
USAGE_MIN_PCT = 20   # defer the run if less than this % of the usage window remains
FAILURE_SKIP_STREAK = 2
COOLDOWN_DAYS = 5    # minimum days between visits to the same project
PROJECTS_DIR = Path.home() / "Downloads"
# Fallback used only if PROJECTS_CONFIG_FILE is missing or unparseable —
# keep in sync with the seed written to that file.
FALLBACK_PROJECTS = ["dss-grid", "reopt-pysam", "pacta-trisk", "dppa-case",
            "carbonsim-online", "pdd-auto", "freecad-blender", "workflow-bench", "city-ghg"]
FALLBACK_GIT_BRANCH = {"dppa-case": "master", "carbonsim-online": "master"}
# Unique session per run — prior sessions stay alive so they remain viewable
# and resumable from the Claude mobile app via Remote Control. Old ones are
# pruned after SESSION_MAX_AGE_H.
SESSION_PREFIX = "cc-nightly"
SESSION_MAX_AGE_H = 24

# herdr binary — resolved at runtime; the cron runner may not carry
# HERDR_BIN_PATH, so default to the installed preview binary.
HERDR_BIN = Path(os.environ.get(
    "HERDR_BIN",
    r"C:\Users\tukum\AppData\Local\Programs\Herdr\bin\herdr.exe"))

# Shared timestamp for this process, used both as the log filename (known
# immediately, before a project is even picked) and as part of the session /
# workspace name (finalized once a project is selected).
RUN_TS = datetime.now().strftime("%Y%m%d-%H%M%S")

# SESSION starts at this timestamp-only fallback and is reassigned to
# f"{SESSION_PREFIX}-{project}-{RUN_TS}" by main() as soon as a project is
# picked. It is the claude `--remote-control` / `-n` name (shown in the mobile
# app) AND the herdr workspace label. AGENT_NAME is the herdr registry name
# (unique, <=32 chars) — distinct from SESSION because herdr caps agent names.
SESSION = f"{SESSION_PREFIX}-{RUN_TS}"
WORKSPACE_LABEL = SESSION
AGENT_NAME = f"ccn-{RUN_TS[-6:]}"   # finalized in main() (project-scoped)
WORKSPACE_ID = None                 # set by launch_session()
PANE_ID = None                      # set by launch_session()

# Notification / logging — each overridable by an env var of the same name
# so the job can be pointed at a different Discord target or hermes binary
# without editing the script.
HERMES_BIN = Path(os.environ.get(
    "HERMES_BIN",
    r"C:\Users\tukum\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"))
DISCORD_TARGET = os.environ.get(
    "CC_NIGHTLY_DISCORD_TARGET",
    "discord:<DISCORD_GUILD_ID>:<DISCORD_CHANNEL_ID>")
LOG_DIR = Path(os.environ.get(
    "CC_NIGHTLY_LOG_DIR", str(Path.home() / ".hermes" / "cc-nightly-logs")))
LOG_FILE = LOG_DIR / f"cc-nightly-{RUN_TS}.log"

# Time budgets
CHECK_INTERVAL = 15          # seconds between pane polls
BRAINSTORM_MAX_CHECKS = 120  # ~30 min
PLAN_MAX_CHECKS = 60         # ~15 min
BACKLOG_MAX_CHECKS = 60      # ~15 min

# ── Helpers ──────────────────────────────────────────────────────────────

def log(msg: str):
    """Print AND append to this run's log file. Verbose output is meant to
    live in the file, not on stdout — see the Notification section below
    for why: leaving stdout empty is what keeps the Hermes cron runner from
    also relaying a second, uncontrolled message to Discord."""
    line = f"[{datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass  # stdout above is the fallback of record if the log file can't be written


def herdr(*args: str, timeout: int = 60) -> tuple[str, str, int]:
    """Run herdr CLI with list args (no shell). Returns (stdout, stderr, rc).
    Json envelopes come back on stdout; error text on stderr."""
    try:
        # encoding forced: Windows defaults to cp1252, which crashes the
        # reader thread on UTF-8 output (CC TUI spinners, git messages)
        r = subprocess.run([str(HERDR_BIN), *args], capture_output=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", f"TIMEOUT after {timeout}s", -1
    except Exception as e:
        return "", str(e), -1


def _jr(out: str) -> dict:
    """Parse a herdr CLI JSON envelope into its `result` dict (tolerant to
    both {"result": {...}} and bare {...} shapes). {} on parse failure."""
    try:
        return json.loads(out).get("result", {})
    except Exception:
        return {}


RUN_START = time.time()


def pane() -> str:
    """Read the agent pane's recent output. Prefer `--source recent` (full
    history, only available while the agent is idle); fall back to
    `--source visible` (works mid-run) because herdr refuses `recent` while
    the agent is working (agent_not_idle)."""
    out, err, rc = herdr("agent", "read", PANE_ID, "--source", "recent",
                         "--lines", "300", "--format", "text")
    if rc == 0 and out:
        return out
    out, err, rc = herdr("agent", "read", PANE_ID, "--source", "visible",
                         "--lines", "300", "--format", "text")
    return out or err


def send(text: str, submit: bool = True):
    """Deliver a prompt. With submit=True it is entered into the agent's
    prompt box via `agent prompt` (multi-line safe). With submit=False the
    text is typed as literal keystrokes WITHOUT Enter — used to *stage* an
    unsubmitted takeover prompt. An empty text with submit=True just sends an
    Enter (the platform quirk the tmux path needed too)."""
    if not text:
        if submit:
            herdr("pane", "send-keys", PANE_ID, "Enter")
        return
    if not submit:
        herdr("pane", "send-text", PANE_ID, text)   # literal text, no Enter
        return
    herdr("agent", "prompt", PANE_ID, text)


def send_prompt(text: str, label: str, submit: bool = True) -> Path:
    """Deliver a multi-line prompt to the agent.

    With submit=True the FULL body is entered via `agent prompt` — herdr
    delivers multi-line text intact (verified live: 597 bytes / 13 lines with
    no paste-collapse), which is the fix for the tmux send-keys defect that
    used to drop multi-line prompts. A first-delivery guard re-sends once if
    the prompt's tail isn't echoed in the pane (herdr can report a fresh
    pane's first prompt as landed while the text never reached the model).

    With submit=False the prompt is written to a file under LOG_DIR and a
    ONE-LINE pointer to it is typed unsubmitted — used by stage_execution_prompt
    so a manual takeover from the Claude mobile app is one keypress: open the
    session, hit send. The staged line names the prompt file, which keep the
    takeover on a single line (the body can't be typed into a TUI without
    paste-collapse).

    The file is kept (under LOG_DIR, beside the run log) so a failed run can
    be diagnosed from exactly what CC was asked to do."""
    path = LOG_DIR / f"prompt-{RUN_TS}-{label}.md"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if submit:
        herdr("agent", "prompt", PANE_ID, text)
        # First-delivery guard: re-send once if the tail isn't reflected.
        time.sleep(4)
        p = pane()
        tail = text.strip().splitlines()[-1] if text.strip() else ""
        if tail and tail not in p:
            log(f"⚠ First prompt echo not confirmed — re-sending '{label}' prompt once")
            herdr("agent", "prompt", PANE_ID, text)
            time.sleep(4)
    else:
        herdr("pane", "send-text", PANE_ID,
              f"Read the file {path} and follow its instructions exactly, "
              f"as if I had typed them here.")
    return path


# Matches both the legacy "cc-nightly-<timestamp>" name and the current
# "cc-nightly-<project>-<timestamp>" name. Anchored on the trailing
# timestamp rather than a fixed segment count because the project name can
# itself contain hyphens (e.g. "carbonsim-online"). Applied against herdr
# workspace labels (which equal SESSION). Deliberately does NOT match
# unrelated workspaces that merely happen to be named after a project.
_SESSION_AGE_RE = re.compile(rf"^{re.escape(SESSION_PREFIX)}-(?:.+-)?(\d{{8}}-\d{{6}})$")


def cleanup_old_sessions():
    """Close cc-nightly-* herdr workspaces older than SESSION_MAX_AGE_H so
    yesterday's session stays alive all day but they don't accumulate."""
    out, _, _ = herdr("workspace", "list")
    for w in _jr(out).get("workspaces", []):
        label = (w.get("label") or "").strip()
        m = _SESSION_AGE_RE.match(label)
        if not m:
            continue
        started = datetime.strptime(m.group(1), "%Y%m%d-%H%M%S")
        age_h = (datetime.now() - started).total_seconds() / 3600
        if age_h > SESSION_MAX_AGE_H:
            log(f"Pruning old session {label} ({age_h:.1f}h old)")
            herdr("workspace", "close", w.get("workspace_id"))


def find_marker(p: str, name: str) -> str | None:
    """Find 'NAME: <value>' printed by CC in the pane, ignoring the echo of
    our own instructions: the prompt's example value contains <angle brackets>
    (e.g. research/<date>-<slug>-brainstorm.md), a real path never does."""
    for m in re.finditer(rf"{name}:\s*(\S+)", p):
        val = m.group(1)
        if "<" not in val and ">" not in val:
            return val
    return None


_API_FAILURE_RE = re.compile(
    r"API Error:\s*(?:429|5\d\d)"          # CC's own hard-failure line
    r"|\b(?:429|5\d\d)\s+Overloaded"       # "529 Overloaded"
    # Mid-retry spinner. Both forms occur on the same session: one carries the
    # status code ("529 Overloaded · Retrying"), the other does not
    # ("API error · Retrying in 0s · attempt 1/10"), so matching only the
    # coded form silently misses half the cases.
    r"|(?:Overloaded|API error)\s*·\s*Retrying"
    r"|rate limit(?:ed)?\s+exceeded",
    re.IGNORECASE)


def pane_shows_api_failure(p: str, tail_lines: int = 25) -> bool:
    """True when the tail of the pane shows CC having given up on an upstream
    API error (overload / rate limit) rather than on anything to do with the
    repo.

    Only ever consulted when a phase's completion marker is absent: a run
    that retried through a transient 529 and then finished does reach its
    marker, so an old 'Retrying' line further up the scrollback can never
    reach this check. Restricted to the tail for the same reason in reverse —
    a genuine stall that happens to have a long-resolved API error somewhere
    in scrollback must still be reported as a real failure."""
    lines = [ln for ln in p.strip().splitlines() if ln.strip()]
    return bool(_API_FAILURE_RE.search("\n".join(lines[-tail_lines:])))


def stall_outcome(stage: str, fallback_detail: str) -> tuple[str, str]:
    """Classify a phase that never produced its completion marker, returning
    (ledger_status, notification_detail).

    An upstream API failure is recorded as 'deferred' rather than 'failed'.
    Both consecutive_failures() and last_visit_days() ignore deferred
    entries, which is exactly the right semantic here: a 529 says nothing
    about the project, so it must neither count toward the failure streak
    that self-blocks a repo nor consume that repo's rotation slot."""
    if pane_shows_api_failure(pane()):
        return "deferred", (
            f"Upstream API error during {stage} — CC gave up before finishing. "
            "Recorded as deferred: not counted as a project failure, and it "
            "does not consume the cooldown slot.")
    return "failed", fallback_detail


def parse_usage_remaining(text: str) -> int | None:
    """Extract the remaining session percentage from a /usage pane capture.
    Accepts 'N% used' / 'N% left' / 'N% remaining'; first match wins
    (the session line renders above the weekly line). None if not found."""
    m = re.search(r"(\d{1,3})\s*%\s*(used|left|remaining)", text, re.IGNORECASE)
    if not m:
        return None
    val = int(m.group(1))
    return 100 - val if m.group(2).lower() == "used" else val


def check_usage_remaining() -> int | None:
    """Send /usage into the CC pane (via keystrokes so the TUI sees it as a
    slash command, not a chat message) and parse the remaining session %.
    Returns None if the output can't be parsed (caller should proceed)."""
    herdr("pane", "send-text", PANE_ID, "/usage")
    herdr("pane", "send-keys", PANE_ID, "Enter")
    time.sleep(5)
    remaining = parse_usage_remaining(pane())
    herdr("pane", "send-keys", PANE_ID, "Escape")  # close the usage panel
    time.sleep(1)
    return remaining


# ── Notification ─────────────────────────────────────────────────────────

def format_notification(project: str, status: str, session: str, open_count: int,
                         detail: str = "", paths: list[str] | None = None) -> str:
    """Build the Discord message body for one run's outcome. Hard-truncated
    to 1900 characters (Discord's cap is 2000) so a repo with a long backlog
    can never blow the limit."""
    lines = [
        f"CC Nightly — {project} — {status.upper()}",
        f"Session: {session}",
        f"Open plans: {open_count}",
    ]
    if detail:
        lines.append(detail)
    if paths:
        lines.append(f"Files: {', '.join(paths)}")
    lines.append(f"Log: {LOG_FILE}")
    body = "\n".join(lines)
    if len(body) > 1900:
        body = body[:1899] + "…"
    return body


def notify(project: str, status: str, session: str, open_count: int,
           detail: str = "", paths: list[str] | None = None) -> bool:
    """Send this run's outcome to Discord via `hermes send`. Must never raise
    — a broken notification path must never take down the run it's trying to
    report on. Returns True only on a confirmed exit code 0."""
    body = format_notification(project, status, session, open_count, detail, paths)
    try:
        r = subprocess.run(
            [str(HERMES_BIN), "send", "--to", DISCORD_TARGET, "--quiet", body],
            capture_output=True, encoding="utf-8", errors="replace", timeout=60)
        if r.returncode != 0:
            log(f"⚠ notify() failed (exit {r.returncode}): {(r.stderr or '').strip()[:300]}")
            return False
        return True
    except Exception as e:
        log(f"⚠ notify() raised: {e}")
        return False


# ── State management ────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def ledger_append(entry: dict):
    """Append one outcome record to the JSONL ledger."""
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = dict(entry, ts=datetime.now(timezone.utc).astimezone().isoformat(),
                 session=SESSION)
    with LEDGER_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def consecutive_failures(project: str) -> int:
    """Count this project's trailing consecutive 'failed' runs in the ledger.
    'deferred' entries say nothing about the project and are ignored."""
    if not LEDGER_FILE.exists():
        return 0
    count = 0
    for line in reversed(LEDGER_FILE.read_text(encoding="utf-8").splitlines()):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("project") != project or e.get("status") == "deferred":
            continue
        if e.get("status") == "failed":
            count += 1
        else:
            break
    return count


def load_projects() -> tuple[list[str], dict[str, str]]:
    """Read the enabled project names and their branch overrides from
    PROJECTS_CONFIG_FILE. Falls back to FALLBACK_PROJECTS/FALLBACK_GIT_BRANCH
    if the file is missing or unparseable, so a corrupted config never takes
    the whole job down."""
    try:
        data = json.loads(PROJECTS_CONFIG_FILE.read_text(encoding="utf-8"))
        entries = data["projects"]
        names = [e["name"] for e in entries if e.get("enabled")]
        branches = {e["name"]: e.get("branch", "main") for e in entries}
        return names, branches
    except (FileNotFoundError, ValueError, KeyError, TypeError) as e:
        log(f"⚠ Could not load {PROJECTS_CONFIG_FILE} ({e}) — using fallback project list")
        branches = {p: "main" for p in FALLBACK_PROJECTS}
        branches.update(FALLBACK_GIT_BRANCH)
        return FALLBACK_PROJECTS.copy(), branches


def last_visit_days(project: str, now: datetime | None = None) -> float | None:
    """Days since this project's most recent non-'deferred' ledger entry, or
    None if it has never had one. 'deferred' entries are ignored — they say
    nothing about whether real work happened, so they must not reset the
    cooldown."""
    if not LEDGER_FILE.exists():
        return None
    now = now or datetime.now(timezone.utc).astimezone()
    for line in reversed(LEDGER_FILE.read_text(encoding="utf-8").splitlines()):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("project") != project or e.get("status") == "deferred":
            continue
        ts = e.get("ts")
        if not ts:
            continue
        try:
            visited = datetime.fromisoformat(ts)
        except ValueError:
            continue
        return (now - visited).total_seconds() / 86400
    return None


def cooldown_override_active(now: datetime | None = None) -> bool:
    """True while COOLDOWN_OVERRIDE_FILE names a future instant.

    Deliberately time-boxed rather than a boolean flag: an override that has
    to be remembered and removed would eventually be forgotten, and a
    forgotten one silently defeats the whole point of the rotation (the
    cooldown is what stops the same repo being picked night after night).
    This one expires on its own. An unreadable or malformed file is treated
    as 'no override' — failing closed keeps the normal rotation intact."""
    if not COOLDOWN_OVERRIDE_FILE.exists():
        return False
    try:
        data = json.loads(COOLDOWN_OVERRIDE_FILE.read_text(encoding="utf-8"))
        until = datetime.fromisoformat(data["ignore_cooldown_until"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        log(f"⚠ Ignoring unreadable cooldown override {COOLDOWN_OVERRIDE_FILE} ({e})")
        return False
    now = now or datetime.now(timezone.utc).astimezone()
    return now < until


def pick_project() -> str | None:
    """Pick the next project from the shuffle playlist that is both off
    cooldown (COOLDOWN_DAYS since its last non-deferred run) and not on a
    failure streak. Returns None — never an ineligible project — when
    nothing qualifies; the caller must treat that as a valid 'skip tonight'
    outcome.

    The cooldown check (but never the failure-streak check) is suspended
    while cooldown_override_active()."""
    projects, _branches = load_projects()
    state = load_state()
    order = state.get("order")
    idx = state.get("current_index", 0)
    skipped: set[str] = set()
    project = None
    override = cooldown_override_active()
    if override:
        log(f"⚡ Cooldown override active — ignoring the {COOLDOWN_DAYS}d cooldown "
            f"for this run (expires per {COOLDOWN_OVERRIDE_FILE.name})")

    for _ in range(2 * len(projects) + 1):
        # First run, corrupted state, project list changed, or list
        # exhausted → reshuffle
        if not order or idx >= len(order) or set(order) != set(projects):
            order = projects.copy()
            random.shuffle(order)
            idx = 0
            state["completed_rounds"] = state.get("completed_rounds", 0) + 1
            log(f"🔄 New shuffle round #{state['completed_rounds']}: {order}")

        candidate = order[idx]
        idx += 1

        if consecutive_failures(candidate) >= FAILURE_SKIP_STREAK:
            log(f"⏭ Skipping {candidate}: {FAILURE_SKIP_STREAK}+ consecutive failed "
                f"runs (needs a manual look; a non-failed ledger entry clears the streak)")
            skipped.add(candidate)
            if len(skipped) >= len(projects):
                break
            continue

        days = last_visit_days(candidate)
        if days is not None and days < COOLDOWN_DAYS and not override:
            log(f"⏭ Skipping {candidate}: visited {days:.1f}d ago, "
                f"cooldown is {COOLDOWN_DAYS}d")
            skipped.add(candidate)
            if len(skipped) >= len(projects):
                break
            continue

        project = candidate
        break

    state["order"] = order
    state["current_index"] = idx
    state["project"] = project
    state["last_run"] = datetime.now(timezone.utc).astimezone().isoformat()
    save_state(state)

    if project is None:
        log("⚠ Every project is on cooldown or has a failure streak — nothing to pick")
        return None

    log(f"→ Picked #{idx}/{len(order)}: {project}")
    return project


# ── Plan scanning ────────────────────────────────────────────────────────
# Canonical status vocabulary a plan's frontmatter status normalizes to.
# "open" is the default for anything unrecognized or missing — every
# failure mode here must bias toward "still needs attention", never toward
# silently dropping a plan out of the backlog.
_STATUS_MAP = {
    "complete": "complete", "completed": "complete", "done": "complete",
    "shipped": "complete",
    "superseded": "superseded", "obsolete": "superseded", "replaced": "superseded",
    "abandoned": "abandoned", "cancelled": "abandoned", "canceled": "abandoned",
    "dropped": "abandoned", "wontfix": "abandoned",
}

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)
_FRONTMATTER_SCALAR_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$')
_TASK_CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s*TASK-\d+-\d+")


def parse_plan_frontmatter(text: str) -> dict[str, str]:
    """Extract the top-level scalar keys of a leading '---'-delimited YAML
    block as a string→string map, quotes stripped. Nested keys and list
    values (e.g. 'research_inputs:\n  - "a.md"') are ignored, not parsed —
    this is a plan file, not a general YAML document."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t", "-")):
            continue  # list item or nested value — not a top-level scalar
        sm = _FRONTMATTER_SCALAR_RE.match(line)
        if not sm:
            continue
        key, value = sm.group(1), sm.group(2).strip()
        if value == "":
            continue  # this key introduces a nested block/list, not a scalar
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        result[key] = value
    return result


def normalize_status(raw: str | None) -> str:
    """Map a plan's raw frontmatter status to one of the four canonical
    values: open, complete, superseded, abandoned. Comparison is
    case-insensitive on the raw value truncated at the first '—', ' - ',
    or ',' — several plans append a prose justification after the status
    word (e.g. 'superseded — replaced by <other plan>'). Defaults to
    'open' for anything missing or unrecognized."""
    if not raw:
        return "open"
    truncated = re.split(r"—| - |,", raw, maxsplit=1)[0].strip().strip("\"'").lower()
    return _STATUS_MAP.get(truncated, "open")


def plan_progress(text: str) -> tuple[int, int]:
    """Count '- [ ] TASK-NN-MM' / '- [x] TASK-NN-MM' checkboxes in a plan
    body. Returns (tasks_done, tasks_total). Anchored on the literal
    'TASK-' prefix — plan templates also use bare '- [ ]' for exit-criteria
    bullets, which must NOT be counted as tasks."""
    total = 0
    done = 0
    for line in text.splitlines():
        m = _TASK_CHECKBOX_RE.match(line)
        if not m:
            continue
        total += 1
        if m.group(1) in "xX":
            done += 1
    return done, total


def scan_plans(project_dir: Path) -> list[dict]:
    """Return one record per plans/*.md file in project_dir (PROGRESS.md
    excluded — it is a human-maintained rollup, not a plan), sorted by
    filename. Each record: path, name, status (canonical), raw_status,
    done, total, age_days (from file mtime). Returns [] if plans/ does not
    exist."""
    plans_dir = project_dir / "plans"
    if not plans_dir.exists():
        return []
    now = time.time()
    records = []
    for path in sorted(plans_dir.glob("*.md")):
        if path.name == "PROGRESS.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter = parse_plan_frontmatter(text)
        raw_status = frontmatter.get("status")
        done, total = plan_progress(text)
        records.append({
            "path": str(path),
            "name": path.name,
            "status": normalize_status(raw_status),
            "raw_status": raw_status,
            "done": done,
            "total": total,
            "age_days": (now - path.stat().st_mtime) / 86400,
        })
    return records


def open_plans(records: list[dict]) -> list[dict]:
    """Filter scan_plans() records down to canonical status 'open'."""
    return [r for r in records if r["status"] == "open"]


# ── Session launch ───────────────────────────────────────────────────────

def launch_session(project: str, project_dir: Path) -> str | None:
    """Create the herdr workspace, launch Claude Code in its root pane with
    Remote Control enabled (so the session is reachable from the Claude
    mobile app), clear the workspace-trust dialog, and apply the usage gate.
    Returns "deferred" when remaining usage is below USAGE_MIN_PCT, None on
    a launch failure, and "ok" otherwise. Assumes SESSION / WORKSPACE_LABEL /
    AGENT_NAME have already been set to this run's final per-project values.

    herdr launches CC with args after `--` appended to the canonical claude
    executable, so the model + effort + remote-control flags pass through
    exactly as the tmux path sent them."""
    global WORKSPACE_ID, PANE_ID

    # Prior sessions are left alive (unique names per run) so the user can
    # keep viewing/interacting with them via the Claude mobile app. Only
    # sessions older than SESSION_MAX_AGE_H are pruned.
    cleanup_old_sessions()

    log(f"Creating fresh herdr workspace: {WORKSPACE_LABEL}")
    out, err, rc = herdr("workspace", "create", "--cwd", str(project_dir),
                         "--label", WORKSPACE_LABEL)
    if rc != 0:
        log(f"ERROR: herdr workspace create failed (exit {rc}): {err}")
        return None
    r = _jr(out)
    PANE_ID = (r.get("root_pane") or {}).get("pane_id")
    WORKSPACE_ID = (r.get("workspace") or {}).get("workspace_id") or r.get("workspace_id")
    if not PANE_ID:
        log(f"ERROR: workspace created but no pane_id in response: {out[:300]}")
        return None
    log(f"Workspace {WORKSPACE_ID} → pane {PANE_ID} (cwd {project_dir})")

    # Launch CC with high effort + Remote Control under this run's SESSION
    # name, so it shows up in the Claude mobile app under that name. The
    # model in this line is patched by the scheduled revert job.
    #
    # The root pane is a fresh shell; right after workspace create herdr may
    # still be registering it and report agent start as blocked / "not ready
    # for prompts" (transient boot noise). Retry over a short window before
    # treating it as a real launch failure.
    start_args = ["agent", "start", AGENT_NAME, "--kind", "claude",
                  "--pane", PANE_ID, "--",
                  "--model", "opus", "--effort", "high",
                  "--remote-control", SESSION, "-n", SESSION]
    rc = -1
    for attempt in range(8):
        out, err, rc = herdr(*start_args)
        if rc == 0:
            break
        if "not ready" in err.lower() or "startup" in err.lower() or "blocked" in err.lower():
            log(f"⚠ agent start not ready (attempt {attempt + 1}/8) — retrying")
            time.sleep(3)
            continue
        log(f"ERROR: herdr agent start failed (exit {rc}): {err}")
        return None
    if rc != 0:
        log(f"ERROR: herdr agent start failed after 8 attempts (exit {rc}): {err}")
        return None
    time.sleep(6)

    # Handle workspace trust if it appears (retry: slow TUI startups miss a
    # single 6s check)
    for _ in range(4):
        p = pane()
        if "trust" in p.lower() or "yes, i trust" in p.lower():
            log("Workspace trust dialog — accepting")
            herdr("pane", "send-keys", PANE_ID, "Enter")
            time.sleep(3)
            break
        time.sleep(4)
    # Additional Enter for the platform quirk
    herdr("pane", "send-keys", PANE_ID, "Enter")
    time.sleep(2)

    # Usage gate: this schedule shares the subscription window with the CC
    # Pipeline and Tung's interactive use — don't start work that can't finish.
    remaining = check_usage_remaining()
    if remaining is not None and remaining < USAGE_MIN_PCT:
        log(f"Deferring run: only {remaining}% of the usage window remains "
            f"(threshold {USAGE_MIN_PCT}%)")
        return "deferred"
    log(f"Usage check: {remaining if remaining is not None else 'unparsable'}% "
        f"remaining — proceeding")
    return "ok"


# ── Phase 1: Brainstorm ──────────────────────────────────────────────────

def phase_brainstorm(project: str, project_dir: Path) -> bool:
    """Send the brainstorm prompt and monitor for BRAINSTORM_DONE. Assumes
    launch_session() has already created the session, launched CC, and
    cleared the usage gate — this function only drives the conversation."""
    log("=" * 50)
    log("PHASE 1: BRAINSTORM")
    log("=" * 50)

    # Send the orchestrated brainstorm prompt
    prompt = f"""I am your orchestrator, but I am NOT watching — you are unattended. Today we are working on: {project}

Please thoroughly analyze this project's current state, codebase, documentation, and architecture. Brainstorm what improvements, features, refactors, architectural changes, or optimizations would take it to the next level.

Workflow rules:
1. Explore the codebase fully before concluding
2. NEVER ask me questions, render pickers, or wait for input of any kind. When uncertain, adopt the option you would have recommended, note the assumption in the brainstorm file, and continue
3. When your analysis is complete, print EXACTLY this on its own line:
   BRAINSTORM_DONE: research/<date>-<slug>-brainstorm.md
   (Replace <date> with YYYY-MM-DD and <slug> with a kebab-case label)
4. Save your brainstorm output to that file

Begin your thorough analysis now."""
    path = send_prompt(prompt, "brainstorm")
    time.sleep(2)
    send("")  # Extra Enter for Windows quirk
    log(f"Brainstorm prompt sent ({path.name}), monitoring...")

    # Monitor loop
    brain_done = False
    for i in range(BRAINSTORM_MAX_CHECKS):
        p = pane()

        # Check for completion marker
        val = find_marker(p, "BRAINSTORM_DONE")
        if val:
            log(f"BRAINSTORM_DONE found! File: {val}")
            brain_done = True
            break

        # Disk fallback: CC may print the sentinel and scroll it off the
        # visible pane while busy (herdr only exposes full history when idle).
        # A research/*-brainstorm.md written this run is strong evidence the
        # phase completed even if the marker isn't in the pane capture.
        if not brain_done:
            rdir = project_dir / "research"
            if rdir.exists():
                fresh = [p2 for p2 in rdir.glob("*-brainstorm.md")
                         if p2.stat().st_mtime >= RUN_START]
                if fresh:
                    log(f"Brainstorm file detected on disk: {fresh[0]}")
                    brain_done = True
                    break

        # Progress log
        if i > 0 and i % 6 == 0:
            lines = p.strip().split("\n")
            last = lines[-1][:150] if lines else "(empty)"
            log(f"check [{i * CHECK_INTERVAL}s] … {last}")

        time.sleep(CHECK_INTERVAL)

    if not brain_done:
        log("ERROR: BRAINSTORM_DONE marker not detected — aborting run "
            "(planning on top of an unknown state produces junk)")
        p = pane()
        log(f"Last pane content (tail):\n{p[-1000:]}")

    return brain_done


# ── Phase 2: Plan ───────────────────────────────────────────────────────

def phase_plan(project: str, project_dir: Path):
    """Check if CC suggests a plan, invoke plan skill, wait for PLAN_SAVED."""
    log("=" * 50)
    log("PHASE 2: PLAN")
    log("=" * 50)

    p = pane()

    # Check if CC is already suggesting a plan or if we need to prompt
    plan_suggested = re.search(r"(?i)(plan\s+next|suggested\s+next|/plan|\*\*Suggested\s+Next\s+Step\*\*)", p)

    if plan_suggested:
        log("CC suggested a plan — responding yes")
        send("Yes! Please invoke the plan skill and create a multi-phase implementation plan. Save it to the project's plans/ folder at the root (NOT .hermes/plans/).")
        time.sleep(3)
        send("")
    else:
        log("Proactively asking CC to create a plan")
        send("Now please create a multi-phase plan. Use the plan skill. Break the work into phases with clear deliverables. IMPORTANT: save the plan to plans/ at the project root (create the folder if needed). Then print EXACTLY: PLAN_SAVED: plans/<filename>.md")
        time.sleep(2)
        send("")

    # Monitor for PLAN_SAVED marker or plan file on disk
    saved_on_disk = None
    for i in range(PLAN_MAX_CHECKS):
        p = pane()

        # Check for PLAN_SAVED marker
        val = find_marker(p, "PLAN_SAVED")
        if val:
            log(f"PLAN_SAVED found! File: {val}")
            return True, val

        # Check for plan file appearing on disk (in order: project plans/ first,
        # then fallbacks). Only accept files created during THIS run — an
        # hour-wide window can pick up a leftover from an earlier same-day run.
        for plans_subdir in [Path("plans"), Path(".hermes/plans"), Path(".claude/plans")]:
            plans_dir = project_dir / plans_subdir
            if plans_dir.exists():
                plan_files = sorted(plans_dir.glob("*.md"), key=os.path.getmtime, reverse=True)
                if plan_files and os.path.getmtime(plan_files[0]) >= RUN_START:
                    log(f"Plan file detected on disk: {plan_files[0]}")
                    saved_on_disk = plan_files[0]
                    break
        if saved_on_disk:
            break

        if i > 0 and i % 4 == 0:
            lines = p.strip().split("\n")
            last = lines[-1][:150] if lines else "(empty)"
            log(f"plan check [{i * CHECK_INTERVAL}s] … {last}")

        time.sleep(CHECK_INTERVAL)

    if saved_on_disk:
        log(f"Plan file: {saved_on_disk}")
        return True, str(saved_on_disk)

    log("WARNING: Plan not detected within time limit")
    return False, None


# ── Phase: Backlog triage ────────────────────────────────────────────────

_BACKLOG_PROMPT_TEMPLATE = """I am your orchestrator, but I am NOT watching — you are unattended. Today's project is {project}. This repository has unfinished plans, so we are NOT starting anything new.

Open plans:
{plan_list}

Your job is triage only. For EACH open plan above:
1. Read the plan.
2. Check it against the actual repository state: git log, the files it claims to change, and any report in reports/ that references it.
3. Decide one of:
   - complete    — every phase is genuinely implemented in the codebase
   - superseded  — a later plan replaced this work; name the plan that replaced it
   - abandoned   — the work is no longer wanted; say why in one line
   - open        — still real, still wanted, not done
4. If the decision is complete, superseded, or abandoned, set that plan file's YAML frontmatter `status:` field to that value, appending " — <one-line justification>". Also tick the `- [ ] TASK-NN-MM` checkboxes that are genuinely done.
5. If a plan shows `status: none` above, it has NO YAML frontmatter block or no `status:` field in it. ADD one: a `---` delimited block at the very top of the file containing at least `status: <your decision>`. This is required even when your decision is `open`. A plan with no status is counted as open forever, so a single one of them keeps this repository stuck in triage mode permanently and it will never get to plan new work again. If the plan records its state in prose instead (e.g. a `**Status:** complete` line in the body), use that as evidence, but still add real frontmatter.

HARD RULES:
- Edit ONLY files under plans/. Do not touch source code, tests, configuration, or documentation outside plans/.
- Do not create any new plan, brainstorm, or report file.
- Base every decision on evidence you actually read. If you cannot verify, leave it open.
- NEVER ask me questions, render pickers, or wait for input of any kind.

When finished, run: git add plans/ && git commit -m "plans: triage open plans"
(if there is nothing to commit, that is fine).

Then print EXACTLY this on its own line:
BACKLOG_TRIAGED: <number of plans you closed>

Begin now."""


def phase_backlog(project: str, project_dir: Path, records: list[dict]) -> tuple[bool, int]:
    """Send the backlog-triage prompt for the given open plan records and
    monitor for BACKLOG_TRIAGED. After the marker (or a timeout), re-scans
    plans/ so the returned open count reflects whatever the session actually
    closed. Returns (marker_seen, open_count_after)."""
    log("=" * 50)
    log("PHASE: BACKLOG TRIAGE")
    log("=" * 50)

    plan_list = "\n".join(
        f"- {r['name']} — status: {r['raw_status'] or 'none'} — "
        f"tasks {r['done']}/{r['total']} — {r['age_days']:.0f} days old"
        for r in records
    )
    prompt = _BACKLOG_PROMPT_TEMPLATE.format(project=project, plan_list=plan_list)
    path = send_prompt(prompt, "backlog")
    time.sleep(2)
    send("")
    log(f"Backlog triage prompt sent ({path.name}), monitoring...")

    marker_seen = False
    for i in range(BACKLOG_MAX_CHECKS):
        p = pane()

        val = find_marker(p, "BACKLOG_TRIAGED")
        if val:
            log(f"BACKLOG_TRIAGED found! Closed: {val}")
            marker_seen = True
            break

        if i > 0 and i % 4 == 0:
            lines = p.strip().split("\n")
            last = lines[-1][:150] if lines else "(empty)"
            log(f"backlog check [{i * CHECK_INTERVAL}s] … {last}")

        time.sleep(CHECK_INTERVAL)

    if not marker_seen:
        log("WARNING: BACKLOG_TRIAGED marker not detected within time limit")

    open_after = len(open_plans(scan_plans(project_dir)))
    return marker_seen, open_after


# ── Manual takeover staging ──────────────────────────────────────────────

def stage_execution_prompt(plan_path: str, branch: str) -> None:
    """Stage the execution prompt in the pane WITHOUT submitting it, so a
    manual takeover from the Claude mobile app is one keypress: open the
    session, hit send. Never sent automatically — execution is deliberately
    the operator's call, not this job's.

    What is staged is a one-line pointer at the prompt file rather than the
    prompt itself (see send_prompt): typed directly, the body would be
    paste-collapsed and silently dropped, so the keypress would submit a
    fragment. The tradeoff is that the staged line is not self-describing on
    mobile — the prompt file it names has to be opened to read it."""
    prompt = f"""Implement the FIRST TWO phases of the plan at {plan_path}.

Make sure you are on `{branch}` and up to date first: git checkout {branch} && git pull.

For EACH of the first two phases:
1. Implement all the code and changes described in that phase
2. Run the project's test suite (or the closest available check: lint, build, a smoke run). If it fails, fix the failures before committing — never commit red
3. Run git add -A
4. Commit with a descriptive message like "phase-N: <summary>"
5. Then proceed to the next phase

After both phases are complete, generate a final report using the report skill and save it to reports/, then push to {branch} yourself once you're satisfied with the result."""
    send_prompt(prompt, "execute", submit=False)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("CC NIGHTLY ORCHESTRATOR (herdr transport)")
    log(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    global SESSION, WORKSPACE_LABEL, AGENT_NAME, WORKSPACE_ID, PANE_ID

    # ---- Pick project (cooldown-aware shuffle playlist) ----
    project = pick_project()
    if project is None:
        log("Nothing eligible to pick tonight — every project is on cooldown "
            "or has a failure streak")
        ledger_append({"project": None, "status": "skipped", "stage": "all-on-cooldown"})
        notify("(none)", "skipped", SESSION, 0,
               detail="Every project is on cooldown or has a failure streak.")
        return

    _projects, branches = load_projects()
    branch = branches.get(project, "main")
    project_dir = PROJECTS_DIR / project
    # SESSION is the claude --remote-control / -n name (shown in mobile) and
    # the herdr workspace label. The herdr AGENT_NAME is kept short (herdr
    # caps agent names at 32 chars) but unique per run.
    SESSION = f"{SESSION_PREFIX}-{project}-{RUN_TS}"
    WORKSPACE_LABEL = SESSION
    AGENT_NAME = f"ccn-{project[:20]}-{RUN_TS[-6:]}"[:32]
    log(f"Project: {project}  |  Dir: {project_dir}")
    log(f"Git branch: {branch}")
    log(f"Session (remote-control / workspace): {SESSION}")
    log(f"Herdr agent: {AGENT_NAME}")

    if not project_dir.exists():
        log(f"ERROR: Project directory not found: {project_dir}")
        ledger_append({"project": project, "status": "failed", "stage": "missing-dir"})
        notify(project, "failed", SESSION, 0,
               detail=f"Project directory not found: {project_dir}")
        return

    os.chdir(str(project_dir))

    # ---- Backlog gate: decide clean-mode vs backlog-mode before launch ----
    open_records = open_plans(scan_plans(project_dir))

    # ---- Launch the session (usage gate applies regardless of mode) ----
    launch_result = launch_session(project, project_dir)
    if launch_result == "deferred":
        # Slot is NOT rewound: a deferred project simply loses its turn and
        # is reached again on its next natural pass through the playlist.
        ledger_append({"project": project, "status": "deferred", "stage": "usage-gate"})
        if WORKSPACE_ID:
            herdr("workspace", "close", WORKSPACE_ID)
        notify(project, "deferred", SESSION, len(open_records),
               detail="Usage window nearly exhausted — session killed, "
                      "project slot returned to the shuffle.")
        log("Run deferred (usage window nearly exhausted) — session killed, "
            "project slot returned to the shuffle")
        return
    if launch_result != "ok":
        ledger_append({"project": project, "status": "failed", "stage": "launch"})
        notify(project, "failed", SESSION, len(open_records),
               detail="Session launch failed — see the log for the herdr error.")
        log(f"Run aborted — session launch failed. Session left alive in herdr "
            f"workspace {WORKSPACE_ID} ({SESSION}) for inspection")
        return

    # ---- Backlog mode: unfinished plans exist, do not start anything new ----
    if open_records:
        log(f"{len(open_records)} open plan(s) found — entering backlog mode "
            "(no brainstorm, no new plan)")
        triaged, open_after = phase_backlog(project, project_dir, open_records)
        if triaged:
            status, notify_status = "triaged", "backlog"
            detail = f"Backlog triage completed ({len(open_records)} → {open_after} open)."
        else:
            status, detail = stall_outcome(
                "backlog triage",
                "Backlog triage did not confirm completion within the time limit.")
            notify_status = status
        ledger_append({"project": project, "status": status, "stage": "backlog",
                       "open_before": len(open_records), "open_after": open_after})
        notify(project, notify_status, SESSION, open_after, detail=detail)
        if triaged and open_after == 0:
            # Triage cleared the backlog — continue straight into clean mode
            # so the run makes progress instead of ending here.
            log(f"Backlog triage cleared all plans ({len(open_records)} → 0) — "
                "continuing into brainstorm + plan in the same run")
        else:
            log("=" * 60)
            log("CC NIGHTLY COMPLETE (backlog mode)")
            log(f"Project: {project}  |  Status: {status}  |  "
                f"Open plans: {len(open_records)} → {open_after}")
            log("=" * 60)
            return

    # ---- Clean mode: brainstorm, then plan (no unattended execution) ----
    brain_ok = phase_brainstorm(project, project_dir)
    if not brain_ok:
        status, detail = stall_outcome("brainstorm", "Brainstorm did not complete.")
        ledger_append({"project": project, "status": status, "stage": "brainstorm"})
        notify(project, status, SESSION, 0, detail=detail)
        log(f"Run aborted at brainstorm. Session left alive in herdr "
            f"workspace {WORKSPACE_ID} ({SESSION}) for inspection")
        return

    plan_ok, plan_path = phase_plan(project, project_dir)
    if not plan_ok:
        status, detail = stall_outcome("plan", "Plan was not saved.")
        ledger_append({"project": project, "status": status, "stage": "plan"})
        notify(project, status, SESSION, 0, detail=detail)
        log(f"Run aborted at plan. Session left alive in herdr "
            f"workspace {WORKSPACE_ID} ({SESSION}) for inspection")
        return

    # Pre-stage the execution prompt, unsubmitted, for one-keypress takeover.
    stage_execution_prompt(plan_path, branch)

    ledger_append({"project": project, "status": "planned", "stage": "complete",
                   "plan": str(plan_path)})
    notify(project, "planned", SESSION, 0,
           detail="Plan saved. Execution prompt is staged in the session, "
                  "unsubmitted — ready for manual takeover.",
           paths=[str(plan_path)])

    log(f"Session left alive in herdr workspace {WORKSPACE_ID} ({SESSION}) for takeover")
    log("=" * 60)
    log("CC NIGHTLY COMPLETE")
    log(f"Project: {project}  |  Status: planned")
    log("Brainstorm: ✓")
    log(f"Plan: ✓ {plan_path}")
    log("Execution: staged, unsubmitted — awaiting manual takeover from the Claude app")
    log("=" * 60)


def emit_wake_gate():
    """Print the Hermes wake gate as the very last stdout line.

    A no_agent cron job's stdout is delivered to its `deliver:` target
    verbatim unless the last non-empty line is {"wakeAgent": false}. log()
    prints every line, so without this gate every run posts its whole log to
    Discord *in addition to* the notify() message this script sends itself —
    two messages per run, the noisy one being 40-odd 'backlog check [...]'
    lines. This job owns its own notifications (see the Notification
    section), so the runner is told to stay quiet.

    Deliberately print() and not log(): this is a control signal for the
    runner, not part of the run record, and it must be the final line.
    Deliberately NOT emitted on the crash path below — if the script dies,
    the traceback on stdout being delivered is the failsafe that surfaces it."""
    print(json.dumps({"wakeAgent": False}), flush=True)


if __name__ == "__main__":
    try:
        main()
        emit_wake_gate()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        try:
            ledger_append({"project": None, "status": "failed", "stage": "crash",
                           "error": str(e)})
            notify("(unknown)", "crashed", SESSION, 0,
                   detail=f"Unhandled exception: {e}")
        except Exception:
            pass  # notification must never mask the original crash
        sys.exit(1)
