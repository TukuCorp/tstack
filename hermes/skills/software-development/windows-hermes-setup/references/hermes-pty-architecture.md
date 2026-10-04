# Hermes PTY Architecture & the Tmux Gap

Why interactive CLI tools (Claude Code, Codex, OpenCode, Python REPL) need
tmux on Windows — and how to eventually remove that requirement.

## Current Architecture (v0.18.0)

Hermes has two independent PTY stacks that **do not talk to each other**:

### Stack 1: Dashboard PTY Bridges (production-ready, isolated)

Used exclusively by the `hermes dashboard` `/api/pty` WebSocket endpoint for the
in-browser TUI tab. Not wired into any tool path.

| File | Platform | Backend | Interface |
|------|----------|---------|-----------|
| `hermes_cli/pty_bridge.py` | POSIX | `ptyprocess.PtyProcess` | `spawn`, `read`, `write`, `resize`, `close` |
| `hermes_cli/win_pty_bridge.py` | Windows | `pywinpty.PtyProcess` (ConPTY) | `spawn`, `read`, `write`, `resize`, `close` |

Both expose an identical public API (`spawn(argv, cwd, env, cols, rows) → bridge`
with `read(timeout) → bytes|None`, `write(data)`, `close()`). WinPtyBridge
already handles the `\r` vs `\n` issue correctly (pywinpty.write wants str).

### Stack 2: Background Process PTY (partial, in `process_registry.py`)

The `ProcessRegistry.spawn_local()` method accepts `use_pty: bool = False`. When
True, it directly uses `winpty.PtyProcess` (Windows) or `ptyprocess.PtyProcess`
(POSIX) — **not** the bridge classes from Stack 1 — wrapping the command in
`[shell, "-lic", f"set +m; {command}"]`. This path is used only for
`terminal(background=true, pty=true)`.

The process registry also correctly implements `write_stdin()` and
`submit_stdin()` which write to the PTY handle (encoding correctly per
platform), so background PTY processes can receive input. This works.

**But:** `write_stdin()` just writes bytes — no prompt-awareness, no blocking
until ready, no expect-style wait. You must `sleep N` before writing, which is
brittle.

### The Gap: Foreground Terminal Always Uses Popen Pipes

The foreground `terminal()` tool (in `terminal_tool.py`) never touches PTY. It
always goes through `subprocess.Popen` with `stdin=PIPE`, `stdout=PIPE` on a
login shell:

```python
proc = subprocess.Popen(
    [shell, "-lic", f"set +m; {command}"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    ...
)
```

This is the root cause of the tmux workaround. prompt_toolkit, Claude Code
TUI, and Codex all detect that stdin is a pipe (not a real terminal) and either:

- Refuse to start ("not a TTY")
- Fall back to non-interactive mode
- Lose keyboard input handling (`\r` vs `\n`, arrow keys, etc.)

## What Needs to Change

### Step 1: Wire the existing bridge classes into foreground terminal

Add a `pty=True` parameter to `terminal()` that uses `WinPtyBridge`/`PtyBridge`
instead of `subprocess.Popen` for the foreground case:

```python
# In terminal_tool.py foreground exec path:
if pty and _PTY_AVAILABLE:
    bridge = WinPtyBridge.spawn(
        [shell, "-lic", command],
        cwd=cwd, env=env, cols=120, rows=40
    )
    # Read output until done (blocking read loop)
    # bridge.read(timeout) returns bytes, None on EOF
    bridge.close()
```

Both bridge classes already exist at `hermes_cli/pty_bridge.py` and
`hermes_cli/win_pty_bridge.py`. ~50 lines of integration.

### Step 2: Add prompt-aware wait (expect-style)

Replace `sleep N + read` with "wait until prompt shows up":

- `ptyprocess.PtyProcess` has built-in `expect(pattern, timeout)` — blocks
  until the PTY output matches a regex, returns matched text
- `pywinpty` does NOT have this — implement as a polling loop:
  ```
  while time.monotonic() < deadline:
      chunk = bridge.read(timeout=0.1)
      buffer += chunk
      if regex.search(buffer):
          return buffer
  ```

Expose as `wait_for(prompt_regex, timeout=30)` on the bridge classes or as a
new process tool action: `process(action="wait_for", session_id="...",
prompt=r"\$\s*$", timeout=30)`.

### Step 3: Integrate into the process tool

The `process` tool today has `write`, `submit`, `poll`, `log`, `wait`, `kill`.
Add:

- `action="write_and_wait"` — write text, then block until the next prompt
  appears (combining `write` + `wait_for` in a single call). Gives one
  round-trip per interaction instead of submit → poll → submit → poll.

This is the key feature that makes tmux fully redundant for interactive CLI
orchestration.

### Step 4: Auto-detect PTY need

Add a heuristic in `process_registry.py` or `terminal_tool.py`:

```python
_INTERACTIVE_TOOLS = ["claude", "codex", "opencode", "python", "ipython", "node"]
if any(tool in command for tool in _INTERACTIVE_TOOLS):
    use_pty = True  # auto-promote
```

Or expose an explicit `interactive=True` flag on `terminal()`.

### Step 5: Remove tmux sections from coding-agent skills

Once Steps 1-4 land, the claude-code, codex, and opencode skills can replace
their "tmux for interactive" sections with "use `terminal(interactive=True)`
or `process(action='write_and_wait')`".

## Current vs. Future State

| Scenario | Current (v0.18.0) | Future |
|----------|-------------------|--------|
| One-shot CLI task | `terminal("claude -p 'task'")` — works, clean | Same |
| Multi-turn interactive | tmux `send-keys`/`capture-pane` dance | `terminal("claude", interactive=True)` + `process("write_and_wait")` |
| Read output mid-session | `tmux capture-pane -t <name> -p -S -50` | `process(action="log")` with proper PTY stream |
| Send follow-up | `tmux send-keys -t <name> 'text' Enter` | `process(action="write_and_wait", data="text")` |
| Detect completion | Poll scrollback for `❯` prompt | `wait_for(r"❯")` blocks until prompt |
| Windows support | Broken without tmux (`-d` is no-op) | Native ConPTY via `pywinpty` |
| Cleanup | Must `tmux kill-session` | `process(action="kill")` or auto-cleanup |

## Key Files Reference

| File | Role |
|------|------|
| `hermes_cli/pty_bridge.py` | POSIX PTY bridge (dashboard use only) |
| `hermes_cli/win_pty_bridge.py` | Windows ConPTY bridge (dashboard use only) |
| `tools/process_registry.py` | Background process manager with `use_pty` support |
| `tools/terminal_tool.py` | Foreground terminal (always Popen pipes — the gap) |
| `tools/process_tool.py` | Process tool handler for `write/submit/poll/log` |

## Testing the PTY Path Manually

To verify the background PTY path works today (independent of tmux):

```python
# Start a Python REPL in background PTY
terminal(command="python", pty=true, background=true)
# Submit code (note: use write + \\r, NOT submit on Windows)
process(action="write", session_id="<id>", data="print('hello from pty')")
process(action="write", session_id="<id>", data="\\r")
process(action="log", session_id="<id>")  # Should show "hello from pty"
process(action="write", session_id="<id>", data="exit()")
process(action="write", session_id="<id>", data="\\r")
process(action="kill", session_id="<id>")
```

The tmux gap is a *foreground integration gap*, not a fundamental capability
gap — all the pieces exist, they just need connecting.
