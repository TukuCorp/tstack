"""Keep /swarm report-backs reachable in chat-gateway sessions (Discord, Telegram, ...).

A gateway inherits HERDR_PANE_ID from the console pane it was started in, so a lane's
`herdr agent prompt <pane>` report-back lands in that console and never reaches the chat.
A gateway chat is one continuous session, so the agent can keep a copy of the swarm skill
from before its gateway steps existed (13-15 Nov 2026: lanes reported to the console, the
user had to ask for progress). This pre_tool_call hook blocks the two calls that cause it
and tells the agent to reload the skill.
"""
from __future__ import annotations

import os
import re

_RELOAD = ("Reload the swarm skill now with skill_view(name=\"swarm\"): the copy earlier in this chat may "
           "be stale. Follow its Gateway steps.")
_WHY = ("This is a chat-gateway session, so a herdr pane report-back goes to the gateway's console "
        "pane and never reaches this chat.")
_NON_MESSAGING = {"", "api_server", "cli", "codex", "desktop", "gateway", "kanban", "local",
                  "msgraph_webhook", "tool", "tui", "webhook"}
_WATCHDOG_CALLER = re.compile(r"watchdog\.sh[\"']?\s+(\S+)")


def _is_gateway() -> bool:
    try:
        from gateway.session_context import session_is_messaging_surface
        return session_is_messaging_surface()
    except Exception:
        # Outside the Hermes process (tests): same rule as session_is_messaging_surface.
        idents = (os.getenv("HERMES_PLATFORM") or os.getenv("HERMES_SESSION_PLATFORM", ""),
                  os.getenv("HERMES_SESSION_SOURCE", ""))
        return any(i.strip().lower() not in _NON_MESSAGING for i in idents if i)


def _block(msg: str) -> dict:
    return {"action": "block", "message": f"swarm-gateway-guard: {msg}"}


def check(tool_name, args, task_id="", **kwargs):
    if not isinstance(args, dict) or not _is_gateway():
        return None
    if tool_name in ("write_file", "patch"):
        path = str(args.get("path", ""))
        text = " ".join(str(v) for k, v in args.items() if k != "path")
        if "-brief-" in path and "herdr agent prompt" in text:
            return _block(f"{_WHY} The brief's last action must only create the `<lane>.reported` "
                          f"marker file. {_RELOAD}")
    elif tool_name == "terminal":
        m = _WATCHDOG_CALLER.search(str(args.get("command", "")))
        if m and m.group(1) != "-":
            return _block(f"{_WHY} Skip the watchdog tab; run one `watchdog.sh - _<prefix> <stall-minutes> "
                          f"<lane>` waiter per lane instead. {_RELOAD}")
        if m and not (args.get("background") and args.get("notify_on_complete")):
            return _block("a `watchdog.sh -` waiter must run with background=true and notify_on_complete=true; "
                          "otherwise its exit line never reaches this chat.")
    return None


def register(ctx):
    ctx.register_hook("pre_tool_call", check)
