"""Mirror my agent setup (Claude Code, Codex, Opencode, Hermes, omp) into this repo.

Every run rebuilds each tool folder from the live files, strips secrets from
configs, applies the private redaction map, and secret-scans the result.
`--push` commits and pushes only when the scan is clean.

    python sync.py            # rebuild + scan
    python sync.py --push     # rebuild + scan + commit + push
"""
import argparse
import copy
import fnmatch
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
REDACTIONS = ROOT / ".private" / "redactions.json"
R = "<REDACTED>"

# (source, destination in repo, kind) — kind: tree | file | json | config | mcp
SOURCES = [
    (".claude/CLAUDE.md", "claude/CLAUDE.md", "file"),
    (".claude/agents", "claude/agents", "tree"),
    (".claude/commands", "claude/commands", "tree"),
    (".claude/hooks", "claude/hooks", "tree"),
    (".claude/skills", "claude/skills", "tree"),
    (".claude/settings.json", "claude/settings.json", "json"),
    (".claude.json", "claude/mcp-servers.json", "mcp"),
    (".claude/projects/C--Users-tukum/memory", "claude/memory", "tree"),
    (".codex/AGENTS.md", "codex/AGENTS.md", "file"),
    (".codex/agents", "codex/agents", "tree"),
    (".codex/skills", "codex/skills", "tree"),
    (".codex/hooks.json", "codex/hooks.json", "json"),
    (".codex/config.toml", "codex/config.toml", "config"),
    (".codex/herdr-agent-state.ps1", "codex/herdr-agent-state.ps1", "file"),
    (".codex/memories/MEMORY.md", "codex/memories/MEMORY.md", "file"),
    (".config/opencode/AGENTS.md", "opencode/AGENTS.md", "file"),
    (".config/opencode/agents", "opencode/agents", "tree"),
    (".config/opencode/command", "opencode/command", "tree"),
    (".config/opencode/commands", "opencode/commands", "tree"),
    (".config/opencode/plugins", "opencode/plugins", "tree"),
    (".config/opencode/herdr-opencode", "opencode/herdr-opencode", "tree"),
    (".config/opencode/herdr-tui-session.js", "opencode/herdr-tui-session.js", "file"),
    (".config/opencode/skills", "opencode/skills", "tree"),
    (".config/opencode/opencode.json", "opencode/opencode.json", "json"),
    (".config/opencode/tui.jsonc", "opencode/tui.jsonc", "config"),
    (".config/opencode/package.json", "opencode/package.json", "file"),
    (".hermes/SOUL.md", "hermes/SOUL.md", "file"),
    (".hermes/config.yaml", "hermes/config.yaml", "config"),
    (".hermes/skills", "hermes/skills", "tree"),
    (".hermes/scripts", "hermes/scripts", "tree"),
    (".hermes/cron", "hermes/cron", "tree"),
    (".omp/agent/config.yml", "omp/config.yml", "config"),
    (".omp/agent/extensions", "omp/extensions", "tree"),
    (".omp/agent/skills", "omp/skills", "tree"),
    (".agents/skills", "shared/agents-skills", "tree"),
    ("AGENTS.md", "shared/AGENTS.md", "file"),
]
TOOL_DIRS = ["claude", "codex", "opencode", "hermes", "omp", "shared"]

# claude.ai-synced skills live under skills/synced/<org>/; only my own are mirrored.
SYNCED_DIR = ".claude/skills/synced"
SYNCED_EXTRA_MINE = {"plan"}  # manifest leaves creatorType null, but I wrote it

EXCLUDE_NAMES = {"auth.json", ".env", "history.jsonl", "nul", "synced", ".git", "node_modules",
                 "__pycache__", "sessions", "logs", "cache", ".DS_Store",
                 ".system"}  # Codex's bundled OpenAI skills
EXCLUDE_GLOBS = ["*.sqlite", "*.sqlite-*", "*.db", "*.db-shm", "*.db-wal", "*.bak", "*.bak*",
                 "*.bak-*", "*.disabled", "*.draft", "*.pyc", "render-check*.png", "tmp_*",
                 "debug_*", ".env.*", "*.pem", "*.key"]

SENSITIVE_WORDS = {"key", "apikey", "token", "secret", "password", "passwd", "auth",
                   "authorization", "cookie", "credential", "credentials", "bearer", "pat"}
SENSITIVE_BLOCKS = {"env", "headers", "http_headers", "environment", "env_http_headers", "set"}

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{20,}", r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}",
    r"fc-[0-9a-f]{24,}", r"AIza[0-9A-Za-z_\-]{35}", r"xox[abposr]-[A-Za-z0-9\-]{10,}",
    r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"eyJ[A-Za-z0-9_\-]{8,}\.eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}",
    r"ya29\.[0-9A-Za-z_\-]{20,}", r"1//[0-9A-Za-z_\-]{30,}", r"GOCSPX-[A-Za-z0-9_\-]{20,}",
    r"(?i:bearer)\s+[A-Za-z0-9._\-]{24,}",
]
SECRET_RE = re.compile("|".join(f"(?:{p})" for p in SECRET_PATTERNS))
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
EMAIL_KEEP = re.compile(r"(?i)(noreply@anthropic\.com|@example\.(com|org)|@users\.noreply\.github\.com)$")


def is_excluded(relpath):
    parts = Path(relpath).parts
    if any(p in EXCLUDE_NAMES for p in parts):
        return True
    return any(fnmatch.fnmatch(p, g) for p in parts for g in EXCLUDE_GLOBS)


def _words(key):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(key))
    return {w.lower() for w in re.split(r"[\s_\-.]+", spaced) if w}


def _is_sensitive_key(key):
    return bool(_words(key) & SENSITIVE_WORDS)


def _blank(value):
    if isinstance(value, dict):
        return {k: _blank(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_blank(v) for v in value]
    return R


def sanitize_json(obj):
    obj = copy.deepcopy(obj)

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k).lower() in SENSITIVE_BLOCKS or (_is_sensitive_key(k) and not isinstance(v, (dict, list))):
                    node[k] = _blank(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(obj)
    return obj


_TOML_HEADER = re.compile(r"^\s*\[+([^\]]+)\]+\s*$")
_ASSIGN = re.compile(r"^(\s*)([\"']?[\w.\-]+[\"']?)(\s*[=:]\s*)(.*?)(,?)\s*$")


def sanitize_text_config(text):
    """Line-based sanitizer for TOML / YAML / JSONC."""
    out, toml_block, yaml_block_indent = [], False, None
    for line in text.splitlines():
        header = _TOML_HEADER.match(line)
        if header:
            toml_block = header.group(1).split(".")[-1].strip().lower() in SENSITIVE_BLOCKS
            yaml_block_indent = None
            out.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if yaml_block_indent is not None and line.strip() and indent <= yaml_block_indent:
            yaml_block_indent = None
        m = _ASSIGN.match(line)
        if not m:
            out.append(line)
            continue
        lead, key, sep, value, comma = m.groups()
        bare = key.strip("\"'")
        v, block = value.strip(), bare.lower() in SENSITIVE_BLOCKS
        if block and v in ("", "{", "[", "|", ">"):
            yaml_block_indent = indent
            out.append(line)
            continue
        if v in ("", "{", "["):  # opens a nested structure; children are judged on their own lines
            out.append(line)
            continue
        if block:  # inline table / flow mapping, e.g. env = { FOO = "x" }
            out.append(f'{lead}{key}{sep}"{R}"{comma}')
            continue
        if toml_block or yaml_block_indent is not None or _is_sensitive_key(bare):
            quoted = value.strip()[:1] in ("'", '"')
            out.append(f'{lead}{key}{sep}{chr(34) + R + chr(34) if quoted else R}{comma}')
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def redact(text, mapping):
    for needle in sorted(mapping, key=len, reverse=True):
        if needle.isalpha():  # names: whole words only, so "Ann" never eats "Annual"
            text = re.sub(rf"(?<!\w){re.escape(needle)}(?!\w)", lambda _: mapping[needle], text)
        else:  # IDs and keys: anywhere, even glued to escapes like \x27
            text = text.replace(needle, mapping[needle])
    return EMAIL_RE.sub(lambda m: m.group(0) if EMAIL_KEEP.search(m.group(0)) else "<EMAIL>", text)


def scan_secrets(text):
    return [m.group(0)[:12] + "…" for m in SECRET_RE.finditer(text)]


def _read_text(path):
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None


def _write(dest, data, mapping):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        dest.write_bytes(data)
    else:
        dest.write_text(redact(data, mapping), encoding="utf-8", newline="")


def _copy_file(src, dest, mapping):
    text = _read_text(src)
    _write(dest, src.read_bytes() if text is None else text, mapping)


def _copy_tree(src, dest, mapping):
    # Assumption: a folder shipping its own LICENSE is a vendored third-party skill, not mine.
    vendored = {lic.parent for lic in src.rglob("LICENSE*") if lic.is_file()}
    for f in sorted(src.rglob("*")):
        rel = f.relative_to(src)
        if any(v == f.parent or v in f.parents for v in vendored):
            continue
        if f.is_file() and not is_excluded(rel.as_posix()):
            _copy_file(f, dest / rel, mapping)


def _synced_skills():
    base = HOME / SYNCED_DIR
    for org in base.glob("*"):
        manifest = org / "manifest.json"
        if not manifest.exists():
            continue
        for s in json.loads(manifest.read_text(encoding="utf-8")).get("skills", []):
            if s.get("creatorType") == "user" or s.get("name") in SYNCED_EXTRA_MINE:
                if (org / s["name"]).is_dir():
                    yield org / s["name"]


def build(mapping):
    for d in TOOL_DIRS:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    missing = []
    for src_rel, dest_rel, kind in SOURCES:
        src, dest = HOME / src_rel, ROOT / dest_rel
        if not src.exists():
            missing.append(src_rel)
            continue
        if kind == "tree":
            _copy_tree(src, dest, mapping)
        elif kind == "file":
            _copy_file(src, dest, mapping)
        elif kind == "json":
            raw = src.read_text(encoding="utf-8")
            try:
                _write(dest, json.dumps(sanitize_json(json.loads(raw)), indent=2) + "\n", mapping)
            except json.JSONDecodeError:
                _write(dest, sanitize_text_config(raw), mapping)
        elif kind == "config":
            _write(dest, sanitize_text_config(src.read_text(encoding="utf-8")), mapping)
        elif kind == "mcp":
            servers = json.loads(src.read_text(encoding="utf-8")).get("mcpServers", {})
            _write(dest, json.dumps({"mcpServers": sanitize_json(servers)}, indent=2) + "\n", mapping)
    for skill in _synced_skills():
        _copy_tree(skill, ROOT / "claude" / "skills-synced" / skill.name, mapping)
    return missing


def scan_repo():
    hits = []
    for d in TOOL_DIRS:
        for f in (ROOT / d).rglob("*"):
            text = f.is_file() and _read_text(f)
            if text:
                hits += [(f.relative_to(ROOT).as_posix(), h) for h in scan_secrets(text)]
    return hits


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="commit and push when the scan is clean")
    args = ap.parse_args()
    mapping = json.loads(REDACTIONS.read_text(encoding="utf-8")) if REDACTIONS.exists() else {}
    missing = build(mapping)
    for m in missing:
        print(f"skip (not found): ~/{m}")
    hits = scan_repo()
    for path, h in hits:
        print(f"SECRET? {path}: {h}")
    if hits:
        print(f"ABORT: {len(hits)} possible secret(s); nothing committed.")
        return 1
    print("scan clean")
    if args.push:
        git("add", "-A")
        if not git("status", "--porcelain").strip():
            print("no changes")
            return 0
        git("commit", "-m", f"sync {date.today().isoformat()}")
        git("push")
        print("pushed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
