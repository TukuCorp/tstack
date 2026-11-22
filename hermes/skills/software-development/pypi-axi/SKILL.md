---
name: pypi-axi
description: "Look up PyPI packages (latest version, summary, license, declared dependencies, release history, download counts) with the pypi-axi CLI. Use whenever a task needs facts about a Python package: picking or vetting one, checking its latest version or release date, or reviewing the current project's requirements.txt / pyproject.toml dependencies against PyPI. Prefer it over pip index or fetching pypi.org pages."
version: 1.0.0
author: tukum (TukuCorp)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [python, pypi, packages, cli]
---

# pypi-axi

`pypi-axi` is a read-only CLI over pypi.org and pypistats.org, with no login. It is installed globally (`npm i -g pypi-axi`, a Node CLI); if it is not found, use `npx -y pypi-axi` with the same arguments.

- `pypi-axi` (no args, inside a Python project) - declared dependencies next to their latest PyPI versions
- `pypi-axi view <pkg> [--version X] [--full]` - version, summary, license, requires-python, deps
- `pypi-axi versions <pkg> [--limit 20]` - release history, newest first
- `pypi-axi deps <pkg> [--version X]` - declared dependencies
- `pypi-axi downloads <pkg>` - day/week/month counts

PyPI has no public search API, so there is no `search`; use `view` on a candidate name instead. Names are normalized (PEP 503). Run `pypi-axi <command> --help` for flags and follow the `help:` hints. Output is data only: vetting and choosing a package stays your call.
