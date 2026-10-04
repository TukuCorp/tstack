# Hermes TUI Scroll Diagnostics — Windows (2026-08-29)

Session: user reported "can't scroll up in hermes tui" on Windows 11, Windows Terminal (WT_SESSION present, TERM=xterm-256color), display.interface=cli.

## What was found

- `hermes config get display.interface` returned `cli` — default is CLI, not TUI. `hermes` launches prompt_toolkit REPL; `hermes --tui` launches Ink TUI. The 80-line scroll test sent via agent is CLI output (terminal scrollback), not TUI ScrollBox.
- TUI uses alt-screen (`ui-tui/packages/hermes-ink/src/ink/ink.tsx: ENTER_ALT_SCREEN / EXIT_ALT_SCREEN`) — native scrollback disabled by design; scroll is internal.
- Ink mouse tracking enabled only when `options.stdout.isTTY && altScreenActive` (ink.tsx:592,714). Code path: `enableMouseTrackingFor(altScreenMouseTracking)` after `DISABLE_MOUSE_TRACKING`. If launched via git-bash wrapper where stdin is not a TTY, wheel events never fire.
- Scroll path: `useInputHandlers.ts:502 handleInputSelectionClipboard` → `wheelUp/wheelDown` → `computePrecisionWheelStep` / `computeWheelStep` → `scrollWithSelectionBy` (`ui-tui/src/app/scroll.ts`) → `ScrollBox.scrollTo()`. Bounds: `scrollBoundsForDelta()` with `viewport=getViewportHeight()`, `cachedHeight=getScrollHeight()`, `max=cachedHeight-viewport`. `max==0` → no-op.
- `WHEEL_SCROLL_STEP=1` (`ui-tui/src/config/limits.ts:26`), accel in `src/lib/wheelAccel.ts` (WHEEL_ACCEL_WINDOW_MS=40, MAX=6), precision sticky 80ms (`precisionWheel.ts`).
- Sticky behavior: `ScrollBox.scrollTo()` sets `stickyScroll=false` and `pendingScrollDelta=undefined` — correctly breaks bottom pin. `isSticky()` reads `el.stickyScroll ?? attributes['stickyScroll']`.

## Code map

- `ui-tui/src/app/useInputHandlers.ts` — wheel, Shift+Up/Down, PageUp/Down handlers, `shouldFallThroughForScroll`, `wheelStep` wiring
- `ui-tui/src/app/scroll.ts` — `scrollWithSelectionBy`, `scrollBoundsForDelta` (fresh height fallback via `getFreshScrollHeight`)
- `ui-tui/packages/hermes-ink/src/ink/components/ScrollBox.tsx` — imperative `ScrollBoxHandle` (scrollTo, scrollBy, adjustScrollTop, getViewportHeight, getScrollHeight, getFreshScrollHeight)
- `ui-tui/packages/hermes-ink/src/ink/ink.tsx` — alt-screen + mouse tracking enable, `handleResize`, `handleResume`
- `ui-tui/src/config/limits.ts` — `WHEEL_SCROLL_STEP`
- `ui-tui/src/lib/wheelAccel.ts` / `precisionWheel.ts` — accel and precision logic

## How to test correctly

```bash
hermes config get display.interface   # cli or tui?
hermes --tui                          # force TUI
# inside TUI: /help then PageUp, Shift+Up, wheel in order
# wheel dead + PageUp works => TTY/mouse-tracking issue
# try Shift+wheel (bypass app mouse) or launch from cmd.exe instead of mintty
hermes config set display.interface tui  # make TUI default
```

## Windows-specific notes

- WT_SESSION present doesn't guarantee mouse CSI passthrough through MSYS/mintty layer. Prefer Windows Terminal → cmd.exe for TUI testing.
- `TERM=xterm-256color` expected; `winpty` wrapping needed for Node ink if "Found xterm-256color, while expecting a Windows console" appears.
- `cli_rebuild_scrollback_on_redraw: true` (display config) can clear CLI scrollback via CSI repaint — if CLI scroll dead, check this flag.
