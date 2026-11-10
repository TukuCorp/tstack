---
name: windows-shell
description: Shell habits on this Windows machine. Use when running a multi-line script, a heredoc, inline Python or PowerShell, or passing file paths to python, gws or other native Windows programs.
version: 1.0.0
author: Tung Ho
---

# Shell on Windows

- Write any script longer than a few lines to a scratch file and run the file. Long programs inlined in `bash -c`, heredocs or PowerShell strings break on quotes.
- Give native Windows programs (python, gws, PIL) `C:/...` paths, not Git Bash `/c/...` paths.
- Run Python as `python -X utf8`, or Unicode output crashes on cp1252. Add `-I` only for scripts that read untrusted downloads: it ignores `PYTHONUTF8` and drops the script's own folder from imports (`No module named ...`).
