# Chrome Internal URLs via cua-driver

Chrome treats navigation commands for `chrome://` URLs (such as `chrome://extensions`) as **search queries** when typed via cua-driver's accessibility-level `type_text` + `Enter` actions. The simulated keystrokes don't trigger Chrome's URL-detection heuristic.

## Symptom

You `computer_use(action="click", element=N)` on the address bar,
`computer_use(action="type", text="chrome://extensions")`, then
`computer_use(action="key", keys="Enter")`. The tab title reads
`chrome://extensions - Google Search` — Chrome searched for it instead of
navigating to the internal page.

This happens consistently on both Chrome and Chrome Beta on Windows.

## Do not persist

Repeated retries (click address bar again, select-all, re-type, different
formats like `chrome://extensions/` with trailing slash) do NOT help.
The underlying issue is that cua-driver's keyboard simulation doesn't
trigger the same `Navigation` event as a real user's keystrokes.

## Alternative approaches (pick one)

1. **Manual guidance** — Describe the steps to the user and let them do it:
   - Open `chrome://extensions`
   - Enable Developer mode
   - Load unpacked extension from `C:\Users\tukum\AppData\...`

2. **Launch Chrome with URL as CLI argument** — If Chrome isn't already
   running, launch it with the URL baked in:
   ```
   chrome.exe "chrome://extensions"
   ```
   Via terminal:
   ```
   "/c/Program Files/Google/Chrome/Application/chrome.exe" "chrome://extensions"
   ```

3. **Open a new tab first, then type** — Ctrl+T via cua-driver, then type
   the URL. Sometimes works on non-`chrome://` URLs but still fails on
   internal URLs.
