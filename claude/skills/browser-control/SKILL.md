---
name: browser-control
description: Drive the user's own logged-in Chrome tabs with scripted Playwright through the Browser Control extension and local relay. Use when the user names Browser Control, or a task needs deterministic Playwright against their existing authenticated tabs (session adopt, human handoff for 2FA/CAPTCHA, session journal, tab recording). Not for general browsing, page screenshots or DevTools inspection; use the chrome-devtools-axi CLI for those.
---

# Browser Control

Use Browser Control as a **driver**: run deterministic Playwright code against
the user's visible Chromium-family browser. Do not treat it as an autonomous
agent.

## Local Install

- Browser: Chrome Stable at `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- CLI: `npm install --global @opencode-ai/browser-control`; npm global root is
  `%APPDATA%\npm\node_modules`.
- Extension: loaded unpacked from
  `%APPDATA%\npm\node_modules\@opencode-ai\browser-control\extension\dist`.
- Relay: `http://127.0.0.1:19989` (`/extension/status` shows connection and
  shim version).

## Workflow

1. Run the first task directly.

```bash
browser-control --help
browser-control execute 'return { url: page.url(), title: await page.title() }'
```

Relay-backed commands start a detached relay when needed and wait briefly for
the extension to reconnect. Do not start `browser-control serve` first; it is
the foreground debugging path and intentionally does not return.
CLI and MCP share this detached relay; restarting the MCP process does not stop
the relay or interrupt a CLI execute or pending handoff.

`browser-control skill` prints the upstream skill text for the installed
version. After an upgrade, diff it against this file and port relevant changes
by hand; do not overwrite this file with it (it lacks the local notes here).

Completion criterion: execute returns a page result and a readable session id
with the exact `--session` continuation command.

2. Inspect health only when setup or runtime behavior is unclear.

```bash
browser-control doctor
browser-control doctor --json
browser-control status
browser-control status --json
browser-control session list
```

`status` and `doctor` are read-only and never start the relay. A stopped `status`
prints one concise next step instead of a stack trace. When running, `status`
reports relay build compatibility, extension connectivity, sessions, targets,
child target counts, and `crashed=true` for known crashed targets.

Use `browser-control doctor` before deeper debugging. It checks the package,
relay endpoint, extension connection and shim version, sessions, crashed
targets, and whether the running relay matches the CLI build. Relay-backed
commands reject a stale relay build with a concise restart message. On this npm
install the `extension/manifest.json` warning is expected; only
`extension/dist/manifest.json` ships.

3. Create once, then continue the named session.

Bare execute always creates a fresh isolated session and prints `Continue with
--session <id>`. Every later shell call must pass that id (or set
`BROWSER_CONTROL_SESSION`). No toolbar attachment is required.

To control a tab already open in the user's browser, ask the user to click the
Browser Control toolbar button on that tab, then select it while creating a new
session or adopt it for sticky reuse:

```bash
browser-control execute --target-url example.com 'return page.url()'
browser-control session adopt --target-url example.com
```

4. Execute Playwright code.

```bash
# Creates a fresh session and prints its id.
browser-control execute 'return { url: page.url(), title: await page.title() }'
# Continue only with that returned id.
browser-control execute --session cosmic-otter-866 'page.url()'
browser-control execute --session cosmic-otter-866 --file ./script.js
browser-control session new amazon
browser-control execute --session amazon 'await page.goto("https://www.amazon.com")'
browser-control execute --target-url example.com 'return page.url()'
browser-control execute --target-index 0 'return page.url()'
```

**Shell quoting.** From PowerShell, always pass code with `--file <path>`;
PowerShell strips or mangles quotes inside arguments to native executables, so
inline JavaScript breaks unpredictably. The inline single-quote form above is
for Git Bash only: single-quoted shell arguments with double-quoted JavaScript
strings keep `$`, backticks, and `!` from being expanded. If the script itself
needs shell single quotes, use `--file` there too. Do not pass both positional
code and `--file`.

Use `page`, `context`, `browser`, relay-backed persistent `state`, and `fillInput`
inside execute code. Without a session, CLI execute atomically creates a fresh
one and returns its id without reading or writing shared current-session state.
Explicit ids from `--session`, `BROWSER_CONTROL_SESSION`, or MCP `execute({
session: "id" })` must already exist. Each session gets one owned default page
that persists across named execute calls. MCP keeps its own process-local current
session because the MCP process itself is the agent boundary.

Create an explicit id with `session_new` first. With MCP, omit the id to let the
server establish its process-local current session. `targetUrl` and
`targetIndex` only select pages that already exist in
the attached page pool; they never navigate or create a page. Use `page.goto()`
to open a URL in a session-owned page, or attach an existing user tab with the
toolbar before selecting or adopting it.

The sandbox also exposes Node modules both through `modules` and convenient
aliases such as `fs` and `path`. Execute code runs in its own lexical scope, so
scripts may safely declare local names such as `const path = ...` without
colliding with those aliases.

**File paths inside execute code must be absolute.** Code runs in the detached
relay, whose working directory is wherever the relay was first started, not
your shell's current directory. Build the full path in your shell (for example
`C:/Users/tukum/project/tmp/shot.png`) and write it literally into the script.

MCP `execute` extracts returned screenshot buffers, including buffers nested in
objects and arrays, into ordered native image attachments without temporary
files. This lets one call return images plus metadata. A screenshot saved to a
path but not returned remains file-only. `snapshot()` remains the preferred
compact textual read; request images only when visual layout matters.

Bare execute drives its new session-owned page, never the user's attached tabs. To
drive a tab the user attached with the toolbar, adopt it as the session's
default page:

```bash
browser-control session adopt --target-url opencode-agent
browser-control session adopt --target-index 0 -s my-session
```

Adoption is sticky: later executes reuse the adopted tab. Adopting closes the
session's previous relay-created page; session reset/delete releases an adopted
tab but never closes it. MCP exposes the same operation as `session_adopt`.
When a bare execute has to create a fresh page while a user-attached tab is
open, the result includes a warning tip suggesting the adopt command —
that is the "why did a new tab appear?" moment. `--target-url`/`--target-index`
on execute itself remain one-command selections, not sticky adoption. For multi-field forms that wedge on repeated
locator-level DOM evaluation, use `fillInputs(page, fields)` to fill several
selectors in one page execution.

For authentication already established in a user-attached tab, prefer
`execute --target-url <unique-url-part>` for one command or `session adopt
--target-url <unique-url-part>` for sticky reuse rather than reproducing login in
a fresh relay-owned tab. After navigation or `handoff`, verify the expected URL
or a stable element before entering data or continuing.

Single-expression snippets such as `page.url()` and `await page.title()` return
their value automatically; multi-statement scripts still require `return` for a
value. Use `browser-control execute --file <path>` for longer scripts instead of
embedding code in the shell.
Execute responses include structured per-call script/page console logs and page
errors; human CLI output prints the returned value first, then logs, then any
warnings and a one-line aftermath summary when the page URL changed or the call
navigated, hit page errors, or paused for handoffs.

Use `browser-control execute --json` when you want to branch on the result: it
prints `{ ok, isError, text, value, valueUnavailable, error?: { _tag, message },
logs, warnings, diagnostic?, aftermath, session }`. `value` is the structured JSON result of
the script (jq-able: `execute --json '({a: 1})' | jq .value.a` prints `1`);
`text` is the human-formatted rendering. `value` carries plain data only: objects,
arrays, and primitives round-trip; `Map` becomes a plain object, `Set` an
array, bigints strings. Class instances (Playwright `Page`, `Locator`, ...)
and results whose JSON exceeds 32KB are withheld: `value` is `null` and
`valueUnavailable` is `true` — fall back to `text`.
`aftermath` reports `startUrl`, `endUrl`, main-frame `navigations`,
`consoleErrorCount`, `pageErrorCount`, and `handoffs` for that one call.
Recurring permissions-policy warnings and blocked analytics resources are folded
into representative log entries, while application errors stay distinct and
aftermath error counts continue to include every event. Warnings are delivered
with the call that caused them, for example when the session default page was
closed, crashed, or recreated. After an execution-context failure or crash,
the next normal execute gives the default page a one-second health check. An
unhealthy relay-owned page is recreated after it closes; a close failure gives
reset guidance instead of leaking the old tab. An unhealthy adopted tab is
preserved and the call fails quickly with reset/adopt guidance. Failed
execution-context calls also carry a short fixed diagnostic classification with page/navigation
counts; cross-extension navigation failures use
`target/cross-extension-page`. Diagnostics never include evaluation arguments
or results.

Playwright downloads are not available through extension-backed tabs. Chromium
blocks both `Browser.setDownloadBehavior` and the legacy
`Page.setDownloadBehavior` through `chrome.debugger`, so
`page.waitForEvent("download")` rejects immediately with a capability error
instead of timing out and `download.saveAs()` cannot receive an artifact. When
the page exposes the payload through fetch or an API response, read those bytes
in the page and write them with the sandbox's `fs` module instead.

## Guardrails And Read-Only Sessions

The relay always blocks CDP commands that would destroy the user's real browser
state: `Network.clearBrowserCookies`, `Network.clearBrowserCache`,
`Storage.clearCookies` (which backs `context.clearCookies()`), and
`Browser.close`. Scripts that call them fail with a clear error; never try to
work around this.

For inspect-only tasks, create a read-only session. The relay rejects
input-dispatching CDP (`Input.*`) for it, so scripts can navigate, read, and
screenshot but not click or type:

```bash
browser-control session new inspect-prod --read-only
browser-control execute -s inspect-prod 'await page.goto("https://example.com"); return await page.title()'
```

In a read-only session, Playwright actions like `locator.click()` keep retrying
the rejected input dispatch until their own timeout; pass a short `{ timeout }`
if you expect a click to be blocked. Note that `page.evaluate` can still mutate
the page via JavaScript; read-only guards trusted mistakes, not malicious code.

For destructive UI work (deleting records, bulk actions) when no CLI/API exists,
read `references/destructive-ui.md` first and follow its two-phase
read-confirm-verify recipe.

## Human Handoff

When a flow hits 2FA, CAPTCHAs, payment confirmation, or anything the user must
do personally, call `handoff(message, { timeoutMs })` inside execute code. It
shows the message and an accessible **I'm done, continue** control in the page,
blocks the script, and resumes only when the user activates that control. The
WAIT UI survives top-level navigation and ambiguous extension child-target
closures. Actual tab removal cancels the handoff explicitly. Default timeout is
10 minutes; a timeout throws so the failure is explicit.

```js
await page.goto("https://accounts.example.com/login")
await fillInput("#email", "me@example.com")
await page.getByRole("button", { name: "Continue" }).click()
await handoff("Complete the 2FA prompt, then use the in-page continue control")
if (!page.url().startsWith("https://app.example.com/")) {
  throw new Error(`2FA did not reach the app: ${page.url()}`)
}
await page.getByRole("heading", { name: "Dashboard" }).waitFor()
return await page.title()
```

Tell the user what you need before or while the handoff is pending. Handoffs are
counted in the result aftermath and recorded in the session journal. Human
acknowledgment is not proof that the task succeeded: always assert the expected
URL or element after `handoff` before continuing. A toolbar click never resumes
a handoff and does not detach its tab while the execute call is active.

## Session Journal

Every execute call is journaled to
`~/.browser-control/sessions/<id>/journal.jsonl` with a timestamp, the code, the
result status, duration, URL movement, warnings, handoffs, and any bounded
execution-context failure diagnostic. Use it to audit
what an agent did to the browser or to debug a session after the fact:

```bash
browser-control journal -s amazon --limit 50
browser-control journal -s amazon --json
```

For concurrent agents, let each agent's first bare execute create a fresh session,
then require that agent to retain and pass its returned id. Use `browser-control
session list` to see session-owned pages. `--target-url` and `--target-index` are manual
recovery selectors for adopting a specific attached page for one command. The same
selection can be supplied to scripts with `BROWSER_CONTROL_TARGET_URL` or
`BROWSER_CONTROL_TARGET_INDEX`. `--target-url` must match exactly one attached
page; use a more specific URL substring or `--target-index` if it matches multiple
pages. Do not set URL and index selectors together.

## Session Lifecycle

Session-owned pages stay attached and visible so repeated shell commands reuse the
same browser state. Use `browser-control session reset` or
`browser-control session delete` to close a session-owned page and clear its
state. Close manually attached tabs normally, call `await page.close()`, or detach
with the toolbar when you want to release them.

For multi-step UI tasks, prefer one `execute` block when the steps depend on
transient page state such as selected rows, open menus, dialogs, hover state, or
in-progress form edits. Persistent tabs preserve navigation and DOM state between
commands, but a single script is safer when one action creates the exact UI state
that the next action must consume.

## Reading And Acting On Pages

Prefer normal Playwright actions first:

```js
await page.getByRole("textbox", { name: "Email" }).fill("me@example.com")
```

Inspect before acting. Start with `snapshot()` and use `ariaSnapshot()` when the
compact view omits the structure you need; do not spend a default 30-second
locator timeout testing a guessed role or selector. Use a short exploratory
timeout, inspect the current page after a miss, and only then choose the stable
locator. After a click that navigates, verify the destination URL or a stable
element before filling the next document. If execution-context diagnostics
repeat, stop changing selectors and investigate page/session health instead.

```js
return await snapshot()          // compact read; assigns refs e1, e2, ...
await ref("e12").click()         // next call: act on a ref from the latest snapshot
return await snapshot({ diff: true })
```

Read `references/snapshots.md` when you need snapshot options, diff semantics,
`ariaSnapshot()`, or `screenshotWithLabels()` for a labeled visual read.

For visual verification, return screenshot buffers through MCP so the image is
actually attached and inspectable. Saving a screenshot to a path and returning
only `"ok"` proves that capture completed, not that the layout looks correct.
Report exactly the viewport, state, and interaction path tested; do not describe
a synthetic browser fixture as broad end-to-end or physical-device coverage.

If normal `locator.fill()` hangs on login/password-style fields in the user's
existing browser, use the explicit DOM-input fallback:

```js
await fillInput("#user-name", "standard_user")
await fillInput(page.getByPlaceholder("Username"), "standard_user")
await fillInputs(page, [
  { selector: "#first-name", value: "Kit" },
  { selector: "#last-name", value: "BrowserControl" },
])
```

This is useful when installed browser extensions, such as password managers,
interfere with Playwright's focus/fill machinery. It sets the value and dispatches
`input` and `change` events; it is only for `input` and `textarea` locators.

Allowed Playwright mouse actions automatically show a spring-animated arrow cursor that
fades after idle time. The relay mirrors successful `Input.dispatchMouseEvent`
move/press/release commands; blocked read-only input never renders the cursor.
Use the helpers to keep it visible, customize it, or disable it for the current
document:

```js
await page.goto("https://example.com")
await page.mouse.move(100, 120)
await page.getByRole("button", { name: "Submit" }).click()
await showGhostCursor({ size: 20 })
await ghostCursor.hide()
```

`showGhostCursor()` / `ghostCursor.show()` enters persistent mode.
`hideGhostCursor()` / `ghostCursor.hide()` disables the cursor until the page's
next document.

## More References

- `references/recording.md`: read before recording a tab to WebM/MP4
  (`browser-control recording start|status|stop|cancel`).
- `references/snapshots.md`: read when `snapshot()` alone is not enough
  (options, diff mode, `ariaSnapshot`, labeled screenshots).
- `references/destructive-ui.md`: read before deleting or bulk-changing anything
  through the UI.
- `references/troubleshooting.md`: read when `doctor`/`status` show a problem,
  tabs detach, fills hang, or execution-context errors repeat.
