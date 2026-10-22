"""Round trip: a fake old machine is mirrored by sync.build, then restored onto a fake new one."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import restore  # noqa: E402
import sync  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n\x00\x01binary"
PLUGINS = [{
    "plugin_id": "herdr-file-viewer", "enabled": True,
    "plugin_root": "C:\\Users\\alice\\AppData\\Roaming\\herdr\\plugins\\github\\x",
    "source": {"kind": "github", "owner": "smarzban", "repo": "herdr-file-viewer",
               "resolved_commit": "c237626", "managed_path": "C:\\Users\\alice\\x"},
}, {"plugin_id": "local-thing", "enabled": True, "source": {"kind": "local", "path": "D:\\x"}}]


def put(base, rel, data):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        p.write_bytes(data)
    else:
        p.write_text(data, encoding="utf-8")
    return p


def old_machine(home):
    put(home, ".claude/CLAUDE.md", "rules for C:\\Users\\alice\\proj and Jane\n[projects.'c:\\users\\alice\\x']\n"
                                   "docs say C:\\Users\\<user>\\AppData\n")
    put(home, ".claude/settings.json", json.dumps({"model": "opus", "env": {"API_KEY": "s3cret"}}))
    put(home, ".claude.json", json.dumps({"numStartups": 9, "mcpServers": {
        "fc": {"command": "firecrawl-mcp", "env": {"FIRECRAWL_API_KEY": "fc-x"}}}}))
    put(home, ".claude/agents/a.md", "mail me at real@corp.com\n")
    put(home, ".claude/agents/b.md", "key k1\n")
    put(home, ".codex/config.toml", 'model = "gpt"\napi_key = "sk-1"\n')
    put(home, "AppData/Local/noctty/config.ghostty",
        "background = #0D0208\nbackground-image = C:/Users/alice/.config/noctty/backgrounds/pcb.png\n")
    put(home, "AppData/Local/noctty/config.ghostty.bak-old", "stale")
    put(home, "AppData/Local/noctty/session-state.json", "{}")
    put(home, ".config/noctty/shaders/tail.glsl", "void main(){}\n")
    put(home, ".config/noctty/backgrounds/pcb.png", PNG)
    put(home, "AppData/Roaming/herdr/config.toml", 'onboarding = false\n[theme]\nname = "terminal"\n')
    put(home, "AppData/Roaming/herdr/plugins.json", json.dumps(PLUGINS))
    put(home, "AppData/Roaming/herdr/herdr-server.log", "noise")
    put(home, ".hermes/skills/herdr/SKILL.md", "hermes herdr skill\n")
    put(home, "AppData/Local/hermes/skills/software-development/plan/SKILL.md", "plan\n")
    put(home, "AppData/Roaming/npm/node_modules/@openai/codex/package.json", json.dumps({"name": "@openai/codex"}))
    put(home, "AppData/Roaming/npm/node_modules/gh-axi/package.json", json.dumps({"name": "gh-axi"}))
    put(home, ".bun/install/global/package.json", json.dumps({"dependencies": {"@oh-my-pi/pi-coding-agent": "^18"}}))
    put(home, "AppData/Roaming/uv/tools/ppt-mcp/uv-receipt.toml",
        '[tool]\nrequirements = [{ name = "ppt-mcp" }]\n')


class RoundTripTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.old, self.new, self.repo = tmp / "Users" / "alice", tmp / "Users" / "bob", tmp / "repo"
        old_machine(self.old)
        self.new.mkdir(parents=True)
        mapping = {"Jane": "<APPROVER>", "k1": "<SHARED>", "k2": "<SHARED>"}
        put(self.repo, ".private/redactions.json", json.dumps(mapping))
        with mock.patch.object(sync, "HOME", self.old), mock.patch.object(sync, "ROOT", self.repo):
            sync.build(mapping)

    def tearDown(self):
        self._tmp.cleanup()

    def run_restore(self, **kw):
        return restore.restore(self.repo, self.new, **kw)

    # --- mirror side ---
    def test_mirror_carries_noctty_and_herdr_without_noise(self):
        r = self.repo
        self.assertIn("<USER>", (r / "noctty/config.ghostty").read_text(encoding="utf-8"))
        self.assertNotIn("alice", (r / "noctty/config.ghostty").read_text(encoding="utf-8"))
        self.assertEqual((r / "noctty/dotconfig/backgrounds/pcb.png").read_bytes(), PNG)
        self.assertTrue((r / "noctty/dotconfig/shaders/tail.glsl").exists())
        self.assertTrue((r / "herdr/config.toml").exists())
        self.assertEqual(json.loads((r / "herdr/plugins.json").read_text(encoding="utf-8")),
                         [{"repo": "smarzban/herdr-file-viewer", "ref": "c237626", "enabled": True}])
        for noise in ["herdr/herdr-server.log", "noctty/session-state.json", "noctty/config.ghostty.bak-old"]:
            self.assertFalse((r / noise).exists(), noise)

    def test_mirror_lists_global_packages(self):
        pk = json.loads((self.repo / "machine/packages.json").read_text(encoding="utf-8"))
        self.assertEqual(pk, {"npm": ["@openai/codex", "gh-axi"],
                              "bun": ["@oh-my-pi/pi-coding-agent"], "uv": ["ppt-mcp"]})

    # --- restore side ---
    def test_restores_noctty_with_new_username_and_binary_intact(self):
        self.run_restore()
        cfg = (self.new / "AppData/Local/noctty/config.ghostty").read_text(encoding="utf-8")
        self.assertIn("background-image = C:/Users/bob/.config/noctty/backgrounds/pcb.png", cfg)
        self.assertEqual((self.new / ".config/noctty/backgrounds/pcb.png").read_bytes(), PNG)
        self.assertTrue((self.new / "AppData/Roaming/herdr/config.toml").exists())

    def test_reverses_private_redaction_map(self):
        self.run_restore()
        text = (self.new / ".claude/CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(text, "rules for C:\\Users\\bob\\proj and Jane\n[projects.'c:\\users\\bob\\x']\n"
                               "docs say C:\\Users\\<user>\\AppData\n")

    def test_splits_hermes_skills_back_to_both_homes(self):
        self.run_restore()
        self.assertTrue((self.new / ".hermes/skills/herdr/SKILL.md").exists())
        self.assertTrue((self.new / "AppData/Local/hermes/skills/software-development/plan/SKILL.md").exists())

    def test_sanitized_configs_fill_gaps_but_never_overwrite(self):
        put(self.new, ".codex/config.toml", 'api_key = "real-key"\n')
        rep = self.run_restore()
        self.assertEqual((self.new / ".codex/config.toml").read_text(encoding="utf-8"), 'api_key = "real-key"\n')
        self.assertIn(str(self.new / ".codex/config.toml"), rep["kept"])
        self.assertTrue((self.new / ".claude/settings.json").exists())
        self.assertIn(str(self.new / ".claude/settings.json"), rep["needs_values"])

    def test_mcp_servers_merge_into_existing_claude_json(self):
        put(self.new, ".claude.json", json.dumps({"numStartups": 1, "mcpServers": {"mine": {"command": "x"}}}))
        self.run_restore()
        data = json.loads((self.new / ".claude.json").read_text(encoding="utf-8"))
        self.assertEqual(data["numStartups"], 1)
        self.assertEqual(set(data["mcpServers"]), {"mine", "fc"})

    def test_lossy_files_fill_gaps_but_never_overwrite(self):
        # emails and placeholders shared by several map entries can't be reversed
        put(self.new, ".claude/agents/a.md", "mail me at real@corp.com\n")
        rep = self.run_restore()
        self.assertEqual((self.new / ".claude/agents/a.md").read_text(encoding="utf-8"), "mail me at real@corp.com\n")
        self.assertIn(str(self.new / ".claude/agents/a.md"), rep["kept"])
        self.assertEqual((self.new / ".claude/agents/b.md").read_text(encoding="utf-8"), "key <SHARED>\n")
        self.assertIn(str(self.new / ".claude/agents/b.md"), rep["needs_values"])

    def test_claude_json_untouched_when_no_server_is_new(self):
        put(self.new, ".claude.json", json.dumps({"mcpServers": {"fc": {"command": "mine"}}}))
        self.assertNotIn(str(self.new / ".claude.json"), self.run_restore()["written"])

    def test_overwritten_files_are_backed_up(self):
        put(self.new, ".claude/CLAUDE.md", "old local rules\n")
        rep = self.run_restore()
        [bak] = rep["backed_up"]
        self.assertEqual(Path(bak).read_text(encoding="utf-8"), "old local rules\n")
        self.assertIn(".bak-tstack-", Path(bak).name)

    def test_unchanged_files_are_not_backed_up_on_rerun(self):
        self.run_restore()
        self.assertEqual(self.run_restore()["backed_up"], [])

    def test_dry_run_writes_nothing(self):
        rep = self.run_restore(dry_run=True)
        self.assertTrue(rep["written"])
        self.assertEqual(list(self.new.rglob("*")), [])


if __name__ == "__main__":
    unittest.main()
