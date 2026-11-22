---
name: npm-axi
description: "Look up npm registry packages (search, latest version, dependencies, README preview, versions with publish dates, download counts) with the npm-axi CLI. Use whenever a task needs facts about an npm package: picking or vetting a package, checking its latest version or release date, or reviewing the current project's package.json dependencies. Prefer it over npm view or fetching npmjs.com pages."
version: 1.0.0
author: tukum (TukuCorp)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [npm, packages, registry, cli]
---

# npm-axi

`npm-axi` is a read-only CLI over registry.npmjs.org and api.npmjs.org, with no login. It is installed globally (`npm i -g npm-axi`); if it is not found, use `npx -y npm-axi` with the same arguments.

- `npm-axi` (no args) - command hints, plus the current project's dependencies
- `npm-axi search "<query>" [--limit 20]` - find packages
- `npm-axi view <pkg> [--full]` - version, license, deps, weekly downloads, README preview
- `npm-axi versions <pkg> [--limit 15]` - recent versions with publish dates
- `npm-axi downloads <pkg>` - weekly and monthly counts

Run `npm-axi <command> --help` for per-command flags and follow the `help:` hints in each response. Output is data only: vetting and choosing a package stays your call.
