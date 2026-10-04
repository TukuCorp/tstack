# Windows Computer Use: Chrome Window Invisible in Capture

**Symptom:** `computer_use(action="capture", ...)` returns a valid desktop screenshot (wallpaper, Recycle Bin, Spotlight button), but a Chrome window that is confirmed running (via `list_apps`) never appears in the capture — even when navigated to a page with content. The window is simply invisible to the capture.

**Diagnostic state:**
- `list_apps` shows `"Google Chrome"` with a valid PID
- `focus_app(app="Google Chrome")` returns `"No on-screen window found"` — even though `list_apps` lists it
- `capture(mode="vision")` returns the desktop wallpaper only — no application windows
- `cua-driver doctor` reports: D3D11 device reachable, UI Automation reachable, session active
- Chrome is running but not captured

**Likely cause:** The Chrome window is minimized, was opened behind the Hermes Desktop GUI (which captures the foreground), or is on a different Windows virtual desktop. cua-driver's background-mode capture only sees the **active/foreground** desktop — it does not composite all windows. If Chrome is minimized or covered, the capture shows the desktop instead.

**Also possible:** Chrome was launched via `terminal(background=true, command="chrome.exe ...")` where the Launcher may have created the window as a **background process** (invisible window frame) rather than a normal window.

## Debug sequence

1. **Confirm Chrome is truly running:**
   ```
   list_apps   # Should show "Google Chrome" with PID
   ```

2. **Try navigating Chrome to a URL first** (uses Hermes' CDP browser, not cua-driver):
   ```
   browser_navigate(url="https://google.com")
   browser_snapshot()
   ```
   If this works, the Chrome Stable config is correct and the browser IS launching — just not where cua-driver can see it.

3. **Try `focus_app` with different app names:**
   Windows `list_apps` returns process names, NOT user-friendly app names. The `app` parameter in `focus_app` and `capture` expects a **process name substring**:
   - `"Chrome"` — usually works (matches "Google Chrome")
   - `"chrome.exe"` — sometimes needed
   - `"Google Chrome"` — as shown in `list_apps`
   
   If none work, the window may be on a different virtual desktop.

4. **Try `capture(app="Chrome")` without specifying Chrome** — capture the **screen** (the whole desktop) rather than a specific app window:
   ```
   computer_use(action="capture", mode="vision")
   ```
   If only the desktop is visible, Chrome is genuinely not in the visible frame.

5. **Workaround — use `browser_*` tools instead.** If the goal is to browse with the user's accounts logged in:
   - `computer_use` drives the user's existing GUI Chrome (better for logged-in accounts)
   - `browser_navigate` / `browser_vision` uses Hermes' headless/cloud browser (no accounts unless configured)
   
   If the user wants their accounts available in `browser_*`, configure Chrome Stable's user data directory (Chrome Beta was uninstalled Aug 2026):
   ```
   hermes config set browser.chrome_beta_path "C:\Program Files\Google\Chrome\Application\chrome.exe"
   hermes config set browser.chrome_user_data_dir "C:\Users\tukum\AppData\Local\Google\Chrome\User Data"
   ```

6. **Last resort — ask the user to open Chrome Stable manually and make it the foreground window.** Once it's visible, `capture` should find it.

## Workaround for automated use

When you need to interact with a Chrome window that cua-driver can't capture, fall back to the Hermes `browser_*` tools. Configure them to use Chrome Stable with the user's existing profile (Step 5 above). This makes the user's accounts, cookies, and extensions available even though the automation is via CDP rather than desktop capture.

To switch from cloud browser to local Chrome Stable CDP:
```bash
hermes config set browser.engine auto
hermes config set browser.chrome_beta_path "C:\Program Files\Google\Chrome\Application\chrome.exe"
hermes config set browser.chrome_user_data_dir "C:\Users\tukum\AppData\Local\Google\Chrome\User Data"
```
Then `browser_navigate` will launch Chrome Stable with the user's profile directory and their accounts will be signed in.
