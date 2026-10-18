# Troubleshooting

Start with `browser-control doctor`. Its Extension line reports the running shim
version; the package's `extension/dist/manifest.json` reports the installed
one. If they differ (for example after `npm install --global` upgraded the
package), reload the unpacked extension once in Chrome. Behavior described below
assumes the shim and CLI match.

- `connected:false`: run a relay-backed command to auto-start the relay, then
  reload the unpacked extension if its reconnect loop does not recover.
- `Target not found`: check `http://127.0.0.1:19989/extension/status`, then
  attach a tab with the toolbar button.
- Extension changes not taking effect after an upgrade: reload the unpacked
  extension once from `chrome://extensions`.
- Repeated `hello` messages or in-flight RPC timeouts: check for duplicate shim
  websocket reconnects, and compare the shim version in `doctor` with
  `extension/dist/manifest.json`.
- Relay restarted while tabs were attached: the shim re-announces attached tabs
  after reconnecting, so the relay rebuilds its target registry without
  re-clicking the toolbar. If `activeTargets` stays 0, reload the unpacked
  extension and re-attach.
- Stale relay build: operational CLI and MCP calls reject a relay that does not
  match the CLI build and print a restart message; `status` and `doctor` remain
  observational. Follow the restart message.
- All tabs suddenly detached (`activeTargets: 0`) while the browser looks fine:
  the user probably dismissed the "is being debugged" banner, which detaches
  chrome.debugger from every tab at once. Re-attach via the toolbar (or
  `session adopt` after re-attaching).
- Control group: session-owned tabs, including adopted user tabs, sit in a
  purple `control` group within each browser window. Merely attached tabs remain
  where the user put them. Reset, delete, or re-adoption releases an adopted tab
  from the group without closing it. Legacy `browser-control`, `bc:*`, and
  `bc · *` groups remain recognized for cleanup.
- Toolbar badge: `ON` when attached, `RUN` while a mutable session executes, and
  `WAIT` while a handoff is pending. Read-only execution stays quietly `ON`. Full
  session ids remain in CLI status, journals, and in-page accessibility text.
- Active targets after an execute run are expected: relay-created tabs persist
  across short-lived CLI calls. Close the visible tab, call `await page.close()`,
  or detach it with the toolbar if you want `/extension/status` to return to zero.
- Clipboard failures on HTTP pages: prefer a secure origin and explicit browser
  permissions. DOM clicking alone may not update or expose clipboard contents.
- Download waits fail with a direct capability error: Chromium does not expose
  download artifact control through an extension's `chrome.debugger` tab
  attachment. Prefer fetching the payload and writing it with `fs`; do not wait
  for a Playwright download event or retry the click.
- Login or password field fill timeouts: suspect installed browser extensions
  interfering with Playwright's native fill path. Try selector-based
  `fillInput(selector, value)` first, or `fillInput(locator, value)` after
  confirming the locator resolves.
- Ghost cursor overlay: allowed Playwright mouse actions show it automatically,
  and it fades when idle. Use `showGhostCursor()`, `hideGhostCursor()`, or
  `ghostCursor.show/hide` for persistent/customized or disabled behavior.
  Read-only input is rejected before rendering; recording does not change mode.
- Closed page during input on real-world React apps: suspect CDP session detach
  around `Target.detachFromTarget` / `Input.dispatchKeyEvent`, and browser
  extension interference. Reset or re-adopt the session before changing locator
  code.
- Missing iframe after reconnect: Browser Control replays stored child target
  attaches and current child frame navigation. If the frame is still missing,
  reset the session or re-adopt the tab.
- Repeated `Execution context was destroyed` failures: run one short follow-up
  execute so Browser Control can wait through transient context replacement and
  health-check the default page. Same-tab root replacements preserve ownership,
  handoffs, and the exact target id. A genuinely unhealthy relay-owned page is
  recreated automatically; reset or re-adopt an unhealthy user-owned tab
  because Browser Control will not replace it. If failures continue,
  restart the relay with `BROWSER_CONTROL_DEBUG=1` before reproducing. `[bc:ctx]`
  lines contain bounded metadata only: target/context IDs, ownership, loader changes, URL origin/shape
  plus fingerprint, reset outcomes, and evaluate shape/failure class. They never
  include expressions, arguments, results, headers, cookies, or form values.
- Bursty navigation to the same heavyweight origin: if several fresh sessions
  all stall before commit while other origins work, serialize those navigations
  or give `page.goto` a deliberate longer timeout. Browser Control preserves raw
  Playwright navigation semantics rather than adding hidden retries.
