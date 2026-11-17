"""Tests for swarm-gateway-guard. Run: python -X utf8 -m pytest -q -p no:cacheprovider <this file>."""
import importlib.util
import os
import pathlib

import pytest

HERE = pathlib.Path(__file__).parent


@pytest.fixture
def guard(monkeypatch):
    spec = importlib.util.spec_from_file_location("swarm_gateway_guard", HERE / "__init__.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.delenv("HERMES_PLATFORM", raising=False)
    monkeypatch.delenv("HERMES_SESSION_PLATFORM", raising=False)
    monkeypatch.delenv("HERMES_SESSION_SOURCE", raising=False)
    return mod


def gateway(monkeypatch):
    monkeypatch.setenv("HERMES_PLATFORM", "discord")


BRIEF_OLD = "## Last action (mandatory)\n1. Create `_hc/cybex.reported`.\n2. Run: herdr agent prompt w2P:p2 \"cybex finished\"\n"
BRIEF_NEW = "## Last action (mandatory)\n1. Create the empty file `_hc/cybex.reported`.\n"
WATCH_TAB = ("herdr pane run w2M:p1A '& \"$env:ProgramFiles\\Git\\bin\\bash.exe\" "
             "\"C:/x/swarm/scripts/watchdog.sh\" w2M:p16 _eb 45 earbuds shopee'")
WAITER = 'bash "C:/x/swarm/scripts/watchdog.sh" - _eb 45 earbuds'


def test_blocks_brief_with_herdr_report_back_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    r = guard.check("write_file", {"path": "C:/p/hc-brief-cybex.md", "content": BRIEF_OLD}, "t")
    assert r["action"] == "block" and "skill_view" in r["message"]


def test_blocks_patch_adding_report_back_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    r = guard.check("patch", {"path": "hc-brief-cybex.md", "old_string": "x",
                              "new_string": "herdr agent prompt w2P:p2 \"done\""}, "t")
    assert r["action"] == "block"


def test_allows_marker_only_brief_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    assert guard.check("write_file", {"path": "C:/p/hc-brief-cybex.md", "content": BRIEF_NEW}, "t") is None


def test_blocks_watchdog_with_pane_caller_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    assert guard.check("terminal", {"command": WATCH_TAB}, "t")["action"] == "block"


def test_blocks_stdout_waiter_without_notify(guard, monkeypatch):
    gateway(monkeypatch)
    for args in ({"command": WAITER}, {"command": WAITER, "background": True}):
        r = guard.check("terminal", args, "t")
        assert r["action"] == "block" and "notify_on_complete" in r["message"]


def test_allows_background_notify_waiter(guard, monkeypatch):
    gateway(monkeypatch)
    assert guard.check("terminal", {"command": WAITER, "background": True, "notify_on_complete": True}, "t") is None


def test_allows_steering_a_lane_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    cmd = 'MSYS_NO_PATHCONV=1 herdr agent prompt cybex "/goal Read the brief hc-brief-cybex.md and execute it"'
    assert guard.check("terminal", {"command": cmd}, "t") is None


def test_inactive_outside_gateway(guard, monkeypatch):
    monkeypatch.setenv("HERMES_SESSION_SOURCE", "cli")
    assert guard.check("write_file", {"path": "hc-brief-cybex.md", "content": BRIEF_OLD}, "t") is None
    assert guard.check("terminal", {"command": WATCH_TAB}, "t") is None


def test_register_hooks_pre_tool_call(guard):
    seen = {}

    class Ctx:
        def register_hook(self, name, fn):
            seen[name] = fn

    guard.register(Ctx())
    assert seen["pre_tool_call"] is guard.check
