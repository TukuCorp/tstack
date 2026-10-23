"""Claim 5: ~/wiki/scripts/collect.py mirrors Claude/Codex/Hermes memory into ~/wiki/raw, redacted, idempotent."""
import re
import subprocess
import sys
from pathlib import Path

home = Path.home()
wiki = home / "wiki"
fail = []


def run(*args):
    p = subprocess.run([sys.executable, "-I", str(wiki / "scripts" / "collect.py"), *args],
                       cwd=wiki, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(p.stdout.rstrip())
    m = re.search(r"(\d+) file\(s\) (changed|restored)\s*$", p.stdout)
    if p.returncode != 0 or not m:
        sys.exit(f"collect.py {args} failed: exit {p.returncode}\n{p.stderr}")
    return int(m.group(1))


n = run()
if n:
    print(f"first run changed {n}; running again")
    n = run()
    if n:
        fail.append(f"second collect run reported {n} changed (not idempotent)")
print(f"collect final changed={n}")

r = run("--restore", "--dry-run")
if r:
    fail.append(f"--restore --dry-run reports {r} restored, expected 0")

# Independent expectation of what should be mirrored
claude_live = home / ".claude" / "projects" / "C--Users-tukum" / "memory"
codex_live = home / ".codex" / "memories"
hermes_live = home / "AppData" / "Local" / "hermes" / "memories"
expect = {
    "claude-memory": {p.name: p for p in claude_live.glob("*.md") if p.is_file()},
    "codex-memory": {**{n: codex_live / n for n in ["MEMORY.md", "memory_summary.md"] if (codex_live / n).is_file()},
                     **{"rollout_summaries/" + p.name: p for p in (codex_live / "rollout_summaries").glob("*.md")}},
    "hermes-memory": {p.name: p for p in hermes_live.glob("*.md") if p.is_file()},
}
secret = re.compile(r"sk-[A-Za-z0-9_\-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|fc-[0-9a-f]{24,}"
                    r"|AIza[0-9A-Za-z_\-]{35}|AKIA[0-9A-Z]{16}|GOCSPX-[A-Za-z0-9_\-]{20,}|ya29\.[0-9A-Za-z_\-]{20,}")
for sub, files in expect.items():
    if not files:
        fail.append(f"no live files for {sub}")
    raw = wiki / "raw" / sub
    have = {p.relative_to(raw).as_posix() for p in raw.rglob("*") if p.is_file()}
    if have != set(files):
        fail.append(f"{sub}: raw {sorted(have ^ set(files))} differ from live set")
    for rel, live in files.items():
        out = raw / rel
        if not out.is_file():
            continue
        lt, rt = live.read_text(encoding="utf-8", errors="replace"), out.read_text(encoding="utf-8")
        if secret.search(rt):
            fail.append(f"{sub}/{rel}: secret pattern present in raw")
        if secret.search(lt):
            if "<REDACTED>" not in rt:
                fail.append(f"{sub}/{rel}: live has secret but raw not redacted")
        elif lt != rt:
            fail.append(f"{sub}/{rel}: raw differs from live")
    print(f"{sub}: {len(files)} file(s) checked")

if (wiki / "raw" / "codex-memory" / "raw_memories.md").exists():
    fail.append("raw/codex-memory/raw_memories.md exists")
fc = re.compile(r"fc-[0-9a-f]{24,}")
for p in (wiki / "raw").rglob("*"):
    if p.is_file() and fc.search(p.read_text(encoding="utf-8", errors="replace")):
        fail.append(f"fc- key in {p}")

if fail:
    print("FAILURES:\n" + "\n".join(fail))
    sys.exit(1)
print("wiki collect verified: mirrored, redacted, idempotent, restore no-op")
