---
description: Work with Google Workspace or NotebookLM using the correct personal or work Google account
---

# Drive Command

<command_purpose>Handle Google Drive, Gmail, Docs, Sheets, Calendar, and NotebookLM tasks using the `drive` skill, choosing the correct Google account for both browser and CLI actions.</command_purpose>

## Required Behavior

1. Load the `drive` skill immediately.
2. Infer the account when the request is explicit:
   - `personal`, `tukumalu91`, or `<EMAIL>` => personal
   - `work`, `allotrope`, or `<EMAIL>` => work
3. If the request is ambiguous, ask one short account-selection question before acting.

## Browser Routing

Playwright MCP is configured in Chrome extension mode and reuses the live Chrome profile.

Current Google account routing in that profile:

- personal `<EMAIL>` => index `0`
- work `<EMAIL>` => index `1`
- `<EMAIL>` => index `2`

When browser control is needed, route explicitly:

- Gmail personal: `https://mail.google.com/mail/u/0/#inbox`
- Gmail work: `https://mail.google.com/mail/u/1/#inbox`
- Drive personal: `https://drive.google.com/drive/u/0/home`
- Drive work: `https://drive.google.com/drive/u/1/home`
- NotebookLM personal: `https://notebooklm.google.com/?authuser=0`
- NotebookLM work: `https://notebooklm.google.com/?authuser=1`
- For other Google apps, add `authuser=0` for personal or `authuser=1` for work

After navigating, verify the resulting page matches the requested account by title, visible email, or account chooser state.

Do not infer Google `authuser` routing from Chrome `Preferences.account_info` ordering.

## CLI Routing

For Google Workspace CLI commands:

- personal => `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-personal`
- work => `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-work`

Verify auth before running the real command:

```powershell
$env:GOOGLE_WORKSPACE_CLI_CONFIG_DIR = "$HOME/.config/gws-work"
gws auth status
```

For NotebookLM CLI commands:

- personal => `--profile personal`
- work => `--profile work`

Verify auth before running the real command:

```bash
nlm login --check --profile work
```

If `gws` or `nlm` auth is missing or expired, stop and tell the user exactly which account needs re-authentication. If the user wants, run the appropriate login flow.

## Tool Choice

- Prefer CLI for Drive, Gmail, Docs, Sheets, Calendar, and NotebookLM data operations
- Use Playwright when the user explicitly wants browser interaction or when the workflow requires a live signed-in Google web UI
- Report which account was used in the final response
