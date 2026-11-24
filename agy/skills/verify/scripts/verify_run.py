#!/usr/bin/env python3
"""Deterministic runner for /verify: execute a checks file and compute the verdict.

Usage:
  python -I verify_run.py <checks.json> [--base <ref>] [--independence subagent|inline]
                          [--report-dir reports] [--timeout <seconds>]

Run from anywhere inside the target git repo. Exit codes: 0 verified, 1 partial,
2 refuted, 3 invalid input. The verdict comes only from exit codes and regexes,
never from judgment, so the same commit and checks file give the same verdict.
"""
import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TEST_GLOBS = ["tests/*", "test/*", "spec/*", "*/tests/*", "*/test/*", "*/spec/*",
              "test_*", "*_test.*", "*.test.*", "*.spec.*", "conftest.py"]
# Untracked paths the runner and the skill write themselves; they don't make the tree dirty.
OWN_PATHS = (".verify/", "reports/")
TAIL_LINES = 15


class InputError(Exception):
    pass


def git(root, *args, check=True, stdin=None):
    p = subprocess.run(["git", *args], cwd=root, input=stdin, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise InputError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def find_bash():
    if os.name != "nt":
        return shutil.which("bash") or "/bin/sh"
    for cand in [shutil.which("bash"),
                 r"C:\Program Files\Git\bin\bash.exe",
                 r"C:\Program Files\Git\usr\bin\bash.exe"]:
        # System32\bash.exe is the WSL launcher, which would run checks in another OS.
        if cand and os.path.isfile(cand) and "system32" not in cand.lower():
            return cand
    raise InputError("no bash found; install Git for Windows")


def kill_tree(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, 9)


def run_cmd(cmd, cwd, timeout):
    start = time.monotonic()
    kwargs = {"start_new_session": True} if os.name != "nt" else {}
    proc = subprocess.Popen([find_bash(), "-c", cmd], cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                            errors="replace", **kwargs)
    try:
        out, _ = proc.communicate(timeout=timeout)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        out, _ = proc.communicate()
        code = None
    return {"cmd": cmd, "exit": code, "out": out or "", "secs": round(time.monotonic() - start, 1)}


def tail(text):
    return "\n".join(text.rstrip().splitlines()[-TAIL_LINES:])


def is_test_path(path):
    return any(fnmatch.fnmatch(path, g) for g in TEST_GLOBS)


def load_checks(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"cannot read checks file {path}: {e}")
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        raise InputError("checks file needs a non-empty 'claims' list")
    seen = set()
    for c in claims:
        for key in ("id", "claim"):
            if not isinstance(c.get(key), str) or not c[key]:
                raise InputError(f"every claim needs a string '{key}': {c}")
        if c["id"] in seen:
            raise InputError(f"duplicate claim id {c['id']}")
        seen.add(c["id"])
        if "run" not in c or not (c["run"] is None or isinstance(c["run"], str)):
            raise InputError(f"claim {c['id']}: 'run' must be a command string or null")
        if c.get("fails_on_base") and not c.get("base_fail_pattern"):
            raise InputError(f"claim {c['id']}: fails_on_base needs base_fail_pattern "
                             "(text the check prints when it fails for the right reason)")
        for key in ("expect_output", "base_fail_pattern"):
            if c.get(key):
                try:
                    re.compile(c[key])
                except re.error as e:
                    raise InputError(f"claim {c['id']}: bad {key} regex: {e}")
    return data


def repo_state(root, base_arg):
    head = git(root, "rev-parse", "HEAD").strip()
    tracked_dirty = bool(git(root, "status", "--porcelain", "--untracked-files=no").strip())
    untracked = [p for p in git(root, "ls-files", "--others", "--exclude-standard").splitlines()
                 if not p.startswith(OWN_PATHS)]
    # Untracked files don't count: checks leave artifacts (__pycache__, build output) that
    # would flip the base between runs. Uncommitted new files must be staged to count.
    dirty = tracked_dirty
    patch_id = None
    if tracked_dirty:
        diff = git(root, "diff", "HEAD", "--binary")
        out = git(root, "patch-id", "--stable", stdin=diff).split()
        patch_id = out[0] if out else None
    if base_arg:
        base = git(root, "rev-parse", base_arg).strip()
    elif dirty:
        base = head
    else:
        remote_head = git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD",
                          check=False).strip()
        mb = git(root, "merge-base", "HEAD", remote_head, check=False).strip() if remote_head else ""
        if mb and mb != head:
            base = mb
        else:
            base = git(root, "rev-parse", "--verify", "-q", "HEAD~1", check=False).strip() or head
    return {"head": head, "dirty": dirty, "patch_id": patch_id, "base": base,
            "untracked": untracked}


def changed_vs_base(root, base, untracked):
    """(path, status, deletions) for working tree vs base, including untracked files."""
    rows = []
    numstat = {}
    for line in git(root, "diff", "--numstat", base).splitlines():
        add, dele, path = line.split("\t", 2)
        numstat[path] = 0 if dele == "-" else int(dele)
    for line in git(root, "diff", "--name-status", "--no-renames", base).splitlines():
        status, path = line.split("\t", 1)
        rows.append((path, status, numstat.get(path, 0)))
    rows += [(p, "A", 0) for p in untracked]
    return rows


def weakened_tests(changes):
    return [f"{p} ({'deleted' if s == 'D' else f'{d} line(s) removed'})"
            for p, s, d in changes if is_test_path(p) and (s == "D" or d > 0)]


def run_on_base(root, base, claim, changes, timeout):
    tmp = Path(tempfile.mkdtemp(prefix="verify-base-"))
    wt = tmp / "wt"
    git(root, "worktree", "add", "--detach", str(wt), base)
    try:
        # Bring the new/changed test files to base, so the old code meets the new test.
        for path, status, _ in changes:
            if status != "D" and is_test_path(path):
                dest = wt / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / path, dest)
        if claim.get("base_setup"):
            setup = run_cmd(claim["base_setup"], wt, timeout)
            if setup["exit"] != 0:
                return setup, "base_setup failed"
        return run_cmd(claim["run"], wt, timeout), None
    finally:
        git(root, "worktree", "remove", "--force", str(wt), check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def judge(root, claim, state, changes, default_timeout):
    """Return (status, reason, evidence list). Status: reproduced|not reproduced|contradicted."""
    if claim["run"] is None:
        return "not reproduced", "no check can falsify this claim", []
    timeout = claim.get("timeout", default_timeout)
    res = run_cmd(claim["run"], root, timeout)
    ev = [("head", res)]
    if res["exit"] is None:
        return "not reproduced", f"timed out after {timeout}s", ev
    if res["exit"] == 127:
        return "not reproduced", "command not found (exit 127)", ev
    expect = claim.get("expect_exit", 0)
    if res["exit"] != expect:
        return "contradicted", f"exit {res['exit']}, expected {expect}", ev
    if claim.get("expect_output") and not re.search(claim["expect_output"], res["out"], re.M):
        return "contradicted", f"output did not match /{claim['expect_output']}/", ev
    if claim.get("fails_on_base"):
        if state["base"] == state["head"] and not state["dirty"]:
            return "not reproduced", "base equals head; nothing to compare", ev
        bres, err = run_on_base(root, state["base"], claim, changes, timeout)
        ev.append(("base", bres))
        if err:
            return "not reproduced", err, ev
        if bres["exit"] is None:
            return "not reproduced", f"timed out on base after {timeout}s", ev
        if bres["exit"] == expect:
            return "not reproduced", "check also passed on base, so it does not prove the change", ev
        if not re.search(claim["base_fail_pattern"], bres["out"], re.M):
            return "not reproduced", (f"failed on base but not for the stated reason "
                                      f"(/{claim['base_fail_pattern']}/ absent)"), ev
        return "reproduced", "passes on head, fails on base for the stated reason", ev
    return "reproduced", f"exit {res['exit']}" + (" and output matched" if claim.get("expect_output") else ""), ev


def verdict_of(statuses, flagged):
    if "contradicted" in statuses or "reproduced" not in statuses:
        return "refuted"
    if all(s == "reproduced" for s in statuses) and not flagged:
        return "verified"
    return "partial"


def ensure_ignored(root, report_dir):
    """Ignore reports via .git/info/exclude, so the runner never dirties the working tree."""
    rel = report_dir.relative_to(root).as_posix() + "/"
    if subprocess.run(["git", "check-ignore", "-q", rel], cwd=root).returncode == 0:
        return
    exclude = Path(git(root, "rev-parse", "--git-path", "info/exclude").strip())
    exclude = exclude if exclude.is_absolute() else root / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    text = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    exclude.write_text(text + ("" if text.endswith("\n") or not text else "\n") + rel + "\n",
                       encoding="utf-8")


def write_report(root, args, data, state, results, flagged, verdict):
    report_dir = (root / args.report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    ensure_ignored(root, report_dir)
    now = dt.datetime.now().astimezone()
    path = report_dir / f"verify-{now:%Y%m%d-%H%M}.md"
    n = 2
    while path.exists():
        path = report_dir / f"verify-{now:%Y%m%d-%H%M}-{n}.md"
        n += 1
    checks_rel = Path(args.checks).resolve().relative_to(root).as_posix()
    lines = ["---", f"verdict: {verdict}", f'date: "{now.isoformat(timespec="seconds")}"',
             f"claims_checked: {len(results)}", f"independence: {args.independence}",
             f"head_sha: {state['head']}", f"patch_id: {state['patch_id'] or 'null'}",
             f"base: {state['base']}", f"checks_file: {checks_rel}", "---", "",
             f"# Verify: {data.get('task', checks_rel)}", "", "## Claims"]
    for i, (c, status, reason, _) in enumerate(results, 1):
        lines.append(f"{i}. {c['claim']} — {status} ({reason})")
    lines += ["", "## Evidence"]
    for c, _, _, ev in results:
        for side, r in ev:
            code = "timeout" if r["exit"] is None else f"exit {r['exit']}"
            lines += [f"- [{c['id']}, {side}] `{r['cmd']}` -> {code} in {r['secs']}s",
                      "", "  ```", *("  " + ln for ln in (tail(r["out"]) or "(no output)").splitlines()), "  ```", ""]
    lines += ["## Test files with removed lines", ""]
    lines += [f"- {f}" for f in flagged] or ["- none"]
    lines += ["", "## Verdict",
              f"{verdict} — computed by verify_run.py from the claim statuses above"
              + ("; capped at partial because existing tests lost lines" if flagged and verdict == "partial"
                 and all(s == "reproduced" for _, s, _, _ in results) else "") + "."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path.relative_to(root).as_posix()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("checks")
    ap.add_argument("--base")
    ap.add_argument("--independence", choices=["subagent", "inline"], default="inline")
    ap.add_argument("--report-dir", default="reports")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()
    try:
        data = load_checks(args.checks)
        root = Path(git(Path(args.checks).resolve().parent, "rev-parse", "--show-toplevel").strip())
        state = repo_state(root, args.base)
        changes = changed_vs_base(root, state["base"], state["untracked"])
        flagged = weakened_tests(changes)
        results = [(c, *judge(root, c, state, changes, args.timeout)) for c in data["claims"]]
    except InputError as e:
        print(f"verify_run: {e}", file=sys.stderr)
        return 3
    verdict = verdict_of([s for _, s, _, _ in results], flagged)
    report = write_report(root, args, data, state, results, flagged, verdict)
    print(f"VERDICT: {verdict}")
    print(f"CLAIMS_CHECKED: {len(results)}")
    print("EVIDENCE:")
    for c, status, reason, ev in results:
        cmd = ev[0][1]["cmd"] if ev else "(no check)"
        print(f"- {cmd} -> {status}: {reason}")
    for f in flagged:
        print(f"- test file lost lines: {f}")
    print(f"REPORT: {report}")
    return {"verified": 0, "partial": 1, "refuted": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
