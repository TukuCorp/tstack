---
name: file-size-cap
description: Keep every code file at 1000 lines or fewer. Use when starting a new code repo, adding lint or CI config, or writing or editing a code file that is long or growing.
version: 1.0.0
author: Tung Ho
---

# File size cap

Keep each code file at 1000 lines or fewer. In a new repo, add a lint rule for it before much code exists (ESLint `max-lines`, pylint `max-module-lines`, or a test that counts lines); unwinding big files later is costly. Split a file that nears the cap by responsibility.
