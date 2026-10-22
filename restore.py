"""Put this mirror back onto the current machine: the reverse of sync.py.

Every file goes back to the live path sync.py read it from, with <USER> paths rewritten to this
machine's username and the private redaction map (if present) reversed. A live file that would
change is backed up first. Sanitized configs, and any file still holding a placeholder that can't be
reversed (<REDACTED>, <EMAIL>, a placeholder shared by several map entries), only fill gaps: an
existing live copy is kept, and new ones are listed so the values can be filled in.

    python restore.py --dry-run    # show what would change
    python restore.py              # restore
"""
import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import sync

SANITIZED = {"json", "config"}
SKIP = {"herdr/plugins.json"}  # bootstrap.ps1 reinstalls these with `herdr plugin install`


def _targets(root, home):
    """Yield (file in repo, live path, kind) for every mirrored file."""
    for src_rel, dest_rel, kind in sync.SOURCES:
        repo = root / dest_rel
        if dest_rel in SKIP:
            continue
        if kind != "tree":
            if repo.is_file():
                yield repo, home / src_rel, kind
            continue
        for f in sorted(repo.rglob("*")) if repo.is_dir() else []:
            rel = f.relative_to(repo)
            if not f.is_file():
                continue
            # hermes/skills merges ~/.hermes/skills with the workflow categories from %LOCALAPPDATA%
            if dest_rel == "hermes/skills" and rel.parts[0] in sync.HERMES_CATEGORIES:
                yield f, home / sync.HERMES_SKILLS / rel, "file"
            else:
                yield f, home / src_rel / rel, "file"


def _reverse_map(root):
    """Placeholder -> original, plus the placeholders that can't be reversed."""
    path = root / ".private" / "redactions.json"
    mapping = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    uses = Counter(mapping.values())
    reverse = {v: k for k, v in mapping.items() if uses[v] == 1}
    return reverse, {sync.R, "<EMAIL>"} | {v for v in uses if uses[v] > 1}


def _merge_mcp(live, text):
    """Add mirrored MCP servers missing from ~/.claude.json; None when there is nothing to add."""
    data = json.loads(live.read_text(encoding="utf-8")) if live.exists() else {}
    servers = data.setdefault("mcpServers", {})
    new = {k: v for k, v in json.loads(text)["mcpServers"].items() if k not in servers}
    if live.exists() and not new:
        return None
    servers.update(new)
    return json.dumps(data, indent=2) + "\n"


def restore(root, home, dry_run=False):
    reverse, unresolved = _reverse_map(root)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = {"written": [], "backed_up": [], "kept": [], "needs_values": []}
    for repo_file, live, kind in _targets(root, home):
        text = sync._read_text(repo_file)
        if text is not None:
            for placeholder in sorted(reverse, key=len, reverse=True):
                text = text.replace(placeholder, reverse[placeholder])
            text = sync.unmask_home(text, home.name)
        lossy = text is not None and any(p in text for p in unresolved)
        if kind == "mcp":
            text = _merge_mcp(live, text)
            if text is None:
                continue
        elif (kind in SANITIZED or lossy) and live.exists():
            data = repo_file.read_bytes() if text is None else text.encode("utf-8")
            if live.read_bytes() != data:
                report["kept"].append(str(live))
            continue
        data = repo_file.read_bytes() if text is None else text.encode("utf-8")
        if live.exists() and live.read_bytes() == data:
            continue
        report["written"].append(str(live))
        if lossy:
            report["needs_values"].append(str(live))
        if dry_run:
            continue
        if live.exists():
            bak = live.with_name(f"{live.name}.bak-tstack-{stamp}")
            shutil.copy2(live, bak)
            report["backed_up"].append(str(bak))
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(data)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report what would change; write nothing")
    args = ap.parse_args()
    report = restore(sync.ROOT, sync.HOME, dry_run=args.dry_run)
    verb = "would write" if args.dry_run else "wrote"
    print(f"{verb} {len(report['written'])} file(s); backed up {len(report['backed_up'])}; "
          f"kept {len(report['kept'])} live file(s) the mirror only has placeholders for")
    for path in report["kept"]:
        print(f"  kept (live copy wins): {path}")
    for path in report["needs_values"]:
        print(f"  fill in placeholder values: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
