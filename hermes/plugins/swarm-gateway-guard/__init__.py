"""Keep /necro report-backs reachable in chat-gateway sessions (Discord, Telegram, ...).

A gateway chat is not an hc terminal. If the gateway was started from one, its HC_TERMINAL_ID
names that console, so a lane's `hc send <caller>` report-back lands there and never reaches
the chat. A gateway chat is one continuous session, so the agent can keep a copy of the necro
skill from before its gateway steps existed (13-15 Nov 2026, Herdr TUI era: lanes reported to
the console, the user had to ask for progress). This pre_tool_call hook blocks the two calls
that cause it and tells the agent to reload the skill.
"""
from __future__ import annotations

import os
import re

_RELOAD = ("Reload the necro skill now with skill_view(name=\"necro\"): the copy earlier in this chat may "
           "be stale. Follow its Gateway steps.")
_WHY = ("This is a chat-gateway session, so a lane's `hc send` report-back goes to the gateway's console "
        "terminal and never reaches this chat.")
_NON_MESSAGING = {"", "api_server", "cli", "codex", "desktop", "gateway", "kanban", "local",
                  "msgraph_webhook", "tool", "tui", "webhook"}
_HC_SEND = re.compile(r"\bhc(?:\.exe)?\s+send\b")
_LANE_WAIT = re.compile(r"\bhc(?:\.exe)?\s+wait\s+(?!--children)\S+")


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
        if "-brief-" in path and _HC_SEND.search(text):
            return _block(f"{_WHY} The brief's last action must only finish the output file. {_RELOAD}")
    elif tool_name == "terminal":
        if _LANE_WAIT.search(str(args.get("command", ""))) and not (
                args.get("background") and args.get("notify_on_complete")):
            return _block("an `hc wait <lane>` waiter must run with background=true and notify_on_complete=true; "
                          "otherwise its exit never reaches this chat.")
    return None


def register(ctx):
    ctx.register_hook("pre_tool_call", check)
