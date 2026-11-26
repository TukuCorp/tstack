"""Tests for swarm-gateway-guard. Run: python -X utf8 -m pytest -q -p no:cacheprovider <this file>."""
import importlib.util
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


BRIEF_SEND = "## Last action (mandatory)\nWhen the file is finished, run:\nhc send t5 \"cybex finished: 3 rows\"\n"
BRIEF_FILE_ONLY = "## Last action (mandatory)\nFinish `hc-cybex.md`; that is the last action.\n"
WAITER = "hc wait cybex --timeout 2700"


def test_blocks_brief_with_hc_send_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    r = guard.check("write_file", {"path": "C:/p/hc-brief-cybex.md", "content": BRIEF_SEND}, "t")
    assert r["action"] == "block" and "skill_view" in r["message"]


def test_blocks_patch_adding_hc_send_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    r = guard.check("patch", {"path": "hc-brief-cybex.md", "old_string": "x",
                              "new_string": "hc send t5 \"done\""}, "t")
    assert r["action"] == "block"


def test_allows_file_only_brief_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    assert guard.check("write_file", {"path": "C:/p/hc-brief-cybex.md", "content": BRIEF_FILE_ONLY}, "t") is None


def test_blocks_lane_wait_without_notify(guard, monkeypatch):
    gateway(monkeypatch)
    for args in ({"command": WAITER}, {"command": WAITER, "background": True}):
        r = guard.check("terminal", args, "t")
        assert r["action"] == "block" and "notify_on_complete" in r["message"]


def test_allows_background_notify_lane_wait(guard, monkeypatch):
    gateway(monkeypatch)
    assert guard.check("terminal", {"command": WAITER, "background": True, "notify_on_complete": True}, "t") is None


def test_allows_steering_a_lane_in_gateway(guard, monkeypatch):
    gateway(monkeypatch)
    cmd = 'hc send cybex "also cover X; keep the same output file"'
    assert guard.check("terminal", {"command": cmd}, "t") is None


def test_inactive_outside_gateway(guard, monkeypatch):
    monkeypatch.setenv("HERMES_SESSION_SOURCE", "cli")
    assert guard.check("write_file", {"path": "hc-brief-cybex.md", "content": BRIEF_SEND}, "t") is None
    assert guard.check("terminal", {"command": WAITER}, "t") is None


def test_register_hooks_pre_tool_call(guard):
    seen = {}

    class Ctx:
        def register_hook(self, name, fn):
            seen[name] = fn

    guard.register(Ctx())
    assert seen["pre_tool_call"] is guard.check
