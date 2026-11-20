#!/usr/bin/env python3
"""Weekly disk cleanup (Hermes cron, no_agent). Sundays 10:00 ICT.

1. Deterministic SAFE clean (rules below; the model never chooses what to delete).
2. Report-only scan: stale rebuildable dev folders, files >1 GB, week-over-week growth.
3. Writes %LOCALAPPDATA%/hermes/disk-cleanup/<date>.md, opens a visible herdr tab with a
   Hermes agent (deepseek-v4.1-flash via opencode-go, file toolset only = cannot delete)
   that ranks the report-only items and appends a "Review" section.
4. Prints a short summary; cron delivers stdout to origin.

Flags: --dry-run (delete nothing, no herdr tab), --no-herdr.
"""
import json, os, shutil, stat, subprocess, sys, time
from datetime import datetime
from pathlib import Path

DRY = "--dry-run" in sys.argv
NO_HERDR = DRY or "--no-herdr" in sys.argv
HOME = Path.home()
LOCAL = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData/Local"))
TEMP = LOCAL / "Temp"
OUT_DIR = LOCAL / "hermes/disk-cleanup"
SIZES_PATH = OUT_DIR / "sizes.json"
DAY = 86400
NOW = time.time()
MODEL, PROVIDER = "deepseek-v4.1-flash", "opencode-go"

def find_exe(name, *cands):
    for c in (shutil.which(name), *cands):
        if c and Path(c).exists():
            return str(c)
    return name

GIT = find_exe("git", LOCAL / "hermes/tools/git-2.53.0+3-win32-x64/cmd/git.exe")
UV = find_exe("uv", LOCAL / "hermes/bin/uv.exe")
NPM = find_exe("npm.cmd", r"C:\Program Files\nodejs\npm.cmd")
HERDR = find_exe("herdr", LOCAL / "Programs/Herdr/bin/herdr.exe",
                 HOME / ".herdr/packages/standalone/current/herdr.exe")

actions, errors = [], []

def run(cmd, cwd=None, timeout=600):
    try:
        p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:  # missing binary, timeout
        return 1, "", str(e)

def free_gb():
    return shutil.disk_usage("C:\\").free / 1e9

def dir_size(p):
    total = 0
    for dp, _, fn in os.walk(p):
        for f in fn:
            try:
                total += os.lstat(os.path.join(dp, f)).st_size
            except OSError:
                pass
    return total

def remove(p, why):
    p = Path(p)
    if not p.exists():
        return
    size = dir_size(p) if p.is_dir() else p.stat().st_size
    if not DRY:
        shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
        if p.exists():
            errors.append(f"could not fully remove (in use?): {p}")
    actions.append((size, why, str(p)))

def age_days(p):
    try:
        return (NOW - Path(p).stat().st_mtime) / DAY
    except OSError:
        return 0

# ---------- 1. SAFE CLEAN ----------
def clean_temp():
    claude = TEMP / "claude"
    keep = {"bundled-skills", "bash-edit-diff"}
    if claude.exists():
        for d in claude.iterdir():
            # >3 days untouched = not a live session's temp dir
            if d.is_dir() and d.name not in keep and age_days(d) > 3:
                remove(d, "Claude session temp >3 days")
    remove(TEMP / f"pytest-of-{os.environ.get('USERNAME', '')}", "pytest temp")
    for d in TEMP.glob("verify-base-*"):
        if age_days(d) < 1:
            continue
        gitfile = d / "wt/.git"
        if gitfile.is_file() and not DRY:
            gitdir = gitfile.read_text(encoding="utf-8", errors="replace").split("gitdir:")[-1].strip()
            repo = Path(gitdir).parent.parent.parent  # <repo>/.git/worktrees/<n>
            run([GIT, "-C", repo, "worktree", "remove", "--force", d / "wt"])
            run([GIT, "-C", repo, "worktree", "prune"])
        remove(d, "verify skill base worktree")

def clean_caches():
    before = free_gb()
    if not DRY:
        rc, _, err = run([UV, "cache", "prune"])
        if rc: errors.append(f"uv cache prune: {err[:200]}")
        rc, _, err = run([NPM, "cache", "clean", "--force"])
        if rc: errors.append(f"npm cache clean: {err[:200]}")
        actions.append((max(0, (free_gb() - before) * 1e9), "uv prune + npm cache", "caches"))
    else:
        actions.append((0, "would run uv cache prune + npm cache clean", "caches"))

def clean_codex():
    rel = HOME / ".codex/packages/standalone/releases"
    cur = HOME / ".codex/packages/standalone/current"
    if not rel.exists():
        return
    try:
        keep = Path(os.readlink(cur)).name if cur.is_symlink() else None
    except OSError:
        keep = None
    pinned = (HOME / ".codex/packages/standalone/auto-update-version")
    pin = pinned.read_text().strip() if pinned.exists() else None
    if not keep and not pin:
        errors.append("codex: cannot resolve current release, skipped")
        return
    for d in rel.iterdir():
        if d.is_dir() and d.name not in (keep, pin):
            remove(d, "old Codex standalone release")

def worktree_admin_age(common_git, wt_path):
    """Days since git last touched this worktree's admin dir (index/HEAD)."""
    for d in (Path(common_git) / "worktrees").glob("*"):
        g = d / "gitdir"
        if g.exists() and Path(g.read_text().strip()).parent.resolve() == Path(wt_path).resolve():
            return min(age_days(d / "index"), age_days(d / "HEAD"), age_days(d / "logs/HEAD"))
    return 0

def clean_worktrees():
    """Remove linked worktrees under Downloads that are merged into main, clean (incl.
    untracked), and untouched for 7+ days. Branch deleted with -d (merged only)."""
    roots = [p for p in (HOME / "Downloads").glob("*/.git") if p.is_dir()]
    roots += [p for p in (HOME / "Downloads").glob("*/*/.git") if p.is_dir()]
    for gitdir in roots:
        repo = gitdir.parent
        rc, out, _ = run([GIT, "-C", repo, "worktree", "list", "--porcelain"])
        if rc:
            continue
        main = "main" if run([GIT, "-C", repo, "rev-parse", "--verify", "-q", "main"])[0] == 0 else "master"
        blocks = [b for b in out.split("\n\n") if b.strip()][1:]  # skip the main worktree
        for b in blocks:
            f = dict((l.split(" ", 1) + [""])[:2] for l in b.splitlines())
            wt = f.get("worktree", "")
            if not wt or "locked" in f or "prunable" in f:
                continue
            if "/Temp/" in wt.replace("\\", "/") or "/.claude/worktrees/" in wt.replace("\\", "/"):
                continue  # temp ones handled above; Claude agent worktrees may be live
            head = f.get("HEAD", "")
            merged = run([GIT, "-C", repo, "merge-base", "--is-ancestor", head, main])[0] == 0
            dirty = run([GIT, "-C", wt, "status", "--porcelain"])[1]
            old = worktree_admin_age(gitdir, wt) > 7 and age_days(wt) > 7
            if not (merged and not dirty and old):
                continue
            size = dir_size(wt)
            if not DRY:
                rc, _, err = run([GIT, "-C", repo, "worktree", "remove", wt])
                if rc:
                    errors.append(f"worktree remove {wt}: {err[:200]}")
                    continue
                br = f.get("branch", "").replace("refs/heads/", "")
                if br:
                    run([GIT, "-C", repo, "branch", "-d", br])
            actions.append((size, f"merged+clean worktree (repo {repo.name})", wt))

# ---------- 2. REPORT ONLY ----------
REGEN = {"node_modules", ".venv", "venv", "target", ".next", ".mypy_cache"}

def scan_report():
    """One scandir pass over the home folder: sizes of every dir at depth 1-2 (growth),
    stale rebuildable dirs and files >1 GB outside AppData."""
    stale, big_files, sizes = [], [], {}
    home_depth = len(HOME.parts)
    appdata = str(HOME / "AppData") + os.sep

    def walk(path):
        in_appdata = (path + os.sep).startswith(appdata)
        total = 0
        try:
            entries = list(os.scandir(path))
        except OSError:
            return 0
        for e in entries:
            try:
                if e.is_symlink():
                    continue
                st = e.stat(follow_symlinks=False)
                if e.is_dir(follow_symlinks=False):
                    if getattr(st, "st_file_attributes", 0) & 0x400:  # junction
                        continue
                    sub = walk(e.path)
                    total += sub
                    if e.name in REGEN and not in_appdata:
                        a = (NOW - Path(path).stat().st_mtime) / DAY
                        if a > 60 and sub > 100e6:
                            stale.append((sub, int(a), e.path))
                else:
                    total += st.st_size
                    if st.st_size > 1e9 and not in_appdata:
                        big_files.append((st.st_size, e.path))
            except OSError:
                pass
        if 1 <= len(Path(path).parts) - home_depth <= 2:
            sizes[path] = total
        return total

    walk(str(HOME))
    # nested regen dirs (node_modules inside .venv etc.): keep only outermost
    stale = [s for s in stale if not any(o[2] != s[2] and s[2].startswith(o[2] + os.sep) for o in stale)]
    prev = json.loads(SIZES_PATH.read_text()) if SIZES_PATH.exists() else {}
    growth = sorted(((sizes[k] - prev[k], k) for k in sizes if k in prev and sizes[k] - prev[k] > 2e9), reverse=True)
    return sorted(stale, reverse=True), sorted(big_files, reverse=True), growth, sizes

# ---------- 3. HERDR REVIEW TAB ----------
def open_herdr(report_path):
    tag = datetime.now().strftime("%m%d-%H%M")  # unique per run (agent names are global)
    rc, out, err = run([HERDR, "workspace", "create", "--label", f"disk-cleanup-{tag}",
                        "--cwd", str(OUT_DIR), "--no-focus"], timeout=30)
    if rc:
        return f"herdr workspace create failed: {err[:200]}"
    try:
        pane = json.loads(out)["result"]["root_pane"]["pane_id"]
    except Exception:
        return f"herdr: unexpected output {out[:200]}"
    name = f"disk-review-{tag}"
    rc, out, err = run([HERDR, "agent", "start", name, "--kind", "hermes", "--pane", pane,
                        "--timeout", "120000", "--", "chat", "-m", MODEL, "--provider", PROVIDER,
                        "-t", "file"], timeout=150)
    if rc:
        return f"herdr agent start failed: {(err or out)[:200]}"
    prompt = (f"Read {report_path}. The safe cleanup already ran; do NOT delete anything "
              "(you only have file tools). Rank the REPORT-ONLY items by GB freed x safety, "
              "say for each what rebuilds it or what to check first, flag anything surprising "
              "in the growth list. If a section is empty, say so in one line; do not rank other "
              "folders. In active use, never suggest removing: agent-browser, puppeteer, "
              "ms-playwright, WinGet\\Packages, hermes, .codex, .claude, ~/wiki. Edit ONLY "
              "that report file: append a '## Review' section (max 15 lines), then reply 'done'.")
    # Hermes ignores input until its startup output (curator) finishes, and herdr's
    # working-state detection is unreliable for hermes: wait, send, then confirm by the
    # Review section appearing in the report; re-send once if it never shows.
    for wait in (45, 20):
        time.sleep(wait)
        run([HERDR, "agent", "prompt", name, prompt], timeout=60)
        for _ in range(30):  # up to 5 min per attempt
            time.sleep(10)
            if "## Review" in report_path.read_text(encoding="utf-8"):
                return f"herdr tab disk-cleanup-{tag}, agent {name} (review written)"
    return f"herdr tab disk-cleanup-{tag}, agent {name} (NO review after 2 prompts; check the tab)"

# ---------- main ----------
def gb(b):
    return f"{b/1e9:.2f} GB"

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    start = free_gb()
    for step in (clean_temp, clean_caches, clean_codex, clean_worktrees):
        try:
            step()
        except Exception as e:
            errors.append(f"{step.__name__}: {e}")
    end = free_gb()
    had_baseline = SIZES_PATH.exists()
    stale, big, growth, sizes = scan_report()
    if not DRY:
        # read-only so the review agent (file tools) can't alter next week's baseline
        if SIZES_PATH.exists():
            os.chmod(SIZES_PATH, stat.S_IWRITE | stat.S_IREAD)
        SIZES_PATH.write_text(json.dumps(sizes))
        os.chmod(SIZES_PATH, stat.S_IREAD)
    day = datetime.now().strftime("%Y-%m-%d")
    report = OUT_DIR / f"{day}{'-dryrun' if DRY else ''}.md"
    L = [f"# Disk cleanup {day}{' (DRY RUN)' if DRY else ''}",
         f"Free on C: {start:.1f} GB -> {end:.1f} GB", "",
         "## Would clean (dry run: nothing deleted)" if DRY else "## Cleaned (safe rules)"]
    L += [f"- {gb(s)}  {why}: {p}" for s, why, p in sorted(actions, reverse=True)] or ["- nothing"]
    L += ["", "## REPORT ONLY: stale rebuildable folders (>60 days, >100 MB)"]
    L += [f"- {gb(s)}  {a}d  {p}" for s, a, p in stale[:25]] or ["- none"]
    L += ["", "## REPORT ONLY: files >1 GB (home folder, excluding AppData)"]
    L += [f"- {gb(s)}  {p}" for s, p in big[:15]] or ["- none"]
    L += ["", "## REPORT ONLY: grew >2 GB since last run"]
    first = not had_baseline
    L += [f"- +{gb(d)}  {p}" for d, p in growth[:15]] or (
        ["- first run: baseline saved, growth compared from next week"] if first else ["- none"])
    if errors:
        L += ["", "## Errors"] + [f"- {e}" for e in errors]
    report.write_text("\n".join(L) + "\n", encoding="utf-8")
    herdr = "skipped" if NO_HERDR else open_herdr(report)
    freed = sum(s for s, _, _ in actions)
    print(f"Weekly disk cleanup{' (dry run)' if DRY else ''}: cleaned {gb(freed)}, "
          f"C: free {end:.1f} GB. Review candidates: {len(stale)} stale dev folders "
          f"({gb(sum(s for s,_,_ in stale))}), {len(big)} files >1 GB, {len(growth)} growth alerts. "
          f"Report: {report}. Review: {herdr}." + (f" ERRORS: {len(errors)}" if errors else ""))

if __name__ == "__main__":
    main()
