---
name: windows-shell
description: Shell habits on this Windows machine. Use when running a multi-line script, a heredoc, inline Python or PowerShell, or passing file paths to python, gws or other native Windows programs.
version: 1.0.0
author: Tung Ho
---

# Shell on Windows

- Write any script longer than a few lines to a scratch file and run the file. Long programs inlined in `bash -c`, heredocs or PowerShell strings break on quotes.
- Give native Windows programs (python, gws, PIL) `C:/...` paths, not Git Bash `/c/...` paths.
