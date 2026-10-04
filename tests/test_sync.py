import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sync  # noqa: E402


class FilterTests(unittest.TestCase):
    def test_excludes_secret_and_noise_paths(self):
        for p in [
            "auth.json", "sub/.env", "x.sqlite", "agent.db", "agent.db-wal",
            "history.jsonl", "sessions/a.json", "logs/x.log", "node_modules/a/b.js",
            "__pycache__/m.pyc", "plan.md.bak-interview", "config.toml.bak.20260927",
            "ask.md.disabled", "SOUL.md.draft", "report/render-check-fixed.png",
            "a/nul", "agents/.bak-20260831-170927/x.md", ".system/skill/SKILL.md",
        ]:
            self.assertTrue(sync.is_excluded(p), p)

    def test_keeps_setup_files(self):
        for p in ["SKILL.md", "agents/ask.md", "hooks/herdr-agent-state.ps1",
                  "plugins/axi-gh-axi.js", "scripts/cc-nightly.py", "references/x.md"]:
            self.assertFalse(sync.is_excluded(p), p)


class CopyTreeTests(unittest.TestCase):
    def test_skips_vendored_skills_that_ship_a_license(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp, "src"), Path(tmp, "dest")
            (src / "mine").mkdir(parents=True)
            (src / "mine" / "SKILL.md").write_text("mine", encoding="utf-8")
            (src / "vendored" / "scripts").mkdir(parents=True)
            (src / "vendored" / "SKILL.md").write_text("x", encoding="utf-8")
            (src / "vendored" / "LICENSE.txt").write_text("x", encoding="utf-8")
            (src / "vendored" / "scripts" / "a.py").write_text("x", encoding="utf-8")
            sync._copy_tree(src, dest, {})
            self.assertTrue((dest / "mine" / "SKILL.md").exists())
            self.assertFalse((dest / "vendored").exists())


class HermesSkillsTests(unittest.TestCase):
    def test_copies_own_skills_in_allowed_categories_only(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp, "skills"), Path(tmp, "dest")
            for rel in ["software-development/plan", "software-development/systematic-debugging",
                        "baby/feeding-log", ".archive/software-development/old"]:
                (src / rel).mkdir(parents=True)
                (src / rel / "SKILL.md").write_text(rel, encoding="utf-8")
            (src / ".bundled_manifest").write_text("systematic-debugging:abc123\n", encoding="utf-8")
            (src / "software-development" / "vendored-thing").mkdir(parents=True)
            (src / "software-development" / "vendored-thing" / "SKILL.md").write_text("x", encoding="utf-8")
            sync._copy_hermes_skills(src, dest, {}, ["software-development"], exclude={"vendored-thing"})
            self.assertFalse((dest / "software-development" / "vendored-thing").exists())
            self.assertTrue((dest / "software-development" / "plan" / "SKILL.md").exists())
            self.assertFalse((dest / "software-development" / "systematic-debugging").exists())
            self.assertFalse((dest / "baby").exists())
            self.assertFalse((dest / ".archive").exists())


class SanitizeJsonTests(unittest.TestCase):
    def test_redacts_sensitive_keys_and_whole_env_headers_blocks(self):
        src = {
            "model": "opus",
            "env": {"HARMLESS_NAME": "value", "N": "1"},
            "mcpServers": {"fc": {"command": "firecrawl-mcp",
                                  "env": {"FIRECRAWL_API_KEY": "fc-abc"},
                                  "headers": {"Authorization": "Bearer x"}}},
            "provider": {"apiKey": "sk-123", "baseURL": "https://x"},
            "permissions": {"allow": ["Bash(ls)"]},
        }
        out = sync.sanitize_json(src)
        self.assertEqual(out["model"], "opus")
        self.assertEqual(out["env"], {"HARMLESS_NAME": "<REDACTED>", "N": "<REDACTED>"})
        self.assertEqual(out["mcpServers"]["fc"]["env"]["FIRECRAWL_API_KEY"], "<REDACTED>")
        self.assertEqual(out["mcpServers"]["fc"]["headers"]["Authorization"], "<REDACTED>")
        self.assertEqual(out["mcpServers"]["fc"]["command"], "firecrawl-mcp")
        self.assertEqual(out["provider"]["apiKey"], "<REDACTED>")
        self.assertEqual(out["provider"]["baseURL"], "https://x")
        self.assertEqual(out["permissions"]["allow"], ["Bash(ls)"])

    def test_does_not_mutate_input(self):
        src = {"token": "abc"}
        sync.sanitize_json(src)
        self.assertEqual(src, {"token": "abc"})


class SanitizeTextConfigTests(unittest.TestCase):
    def test_toml(self):
        src = ('model = "gpt"\napi_key = "sk-1"\n[mcp_servers.fc.env]\nFOO = "bar"\n'
               '[mcp_servers.fc]\ncommand = "fc"\nbearer_token_env_var = "X"\n'
               '[shell_environment_policy.set]\nSHA = "abc"\n')
        out = sync.sanitize_text_config(src)
        self.assertIn('model = "gpt"', out)
        self.assertIn('api_key = "<REDACTED>"', out)
        self.assertIn('FOO = "<REDACTED>"', out)
        self.assertIn('command = "fc"', out)
        self.assertIn('bearer_token_env_var = "<REDACTED>"', out)
        self.assertIn('SHA = "<REDACTED>"', out)

    def test_yaml(self):
        src = "model: x\nopenrouter_api_key: abc123\nenv:\n  SLACK: xyz\n  OTHER: 2\nname: me\n"
        out = sync.sanitize_text_config(src)
        self.assertIn("model: x", out)
        self.assertIn("openrouter_api_key: <REDACTED>", out)
        self.assertIn("  SLACK: <REDACTED>", out)
        self.assertIn("  OTHER: <REDACTED>", out)
        self.assertIn("name: me", out)


class RedactTests(unittest.TestCase):
    def test_applies_map_and_masks_emails(self):
        out = sync.redact("Send to boss@acme.com, sheet 1AbC_xyz, ask Jane",
                          {"1AbC_xyz": "<SHEET_ID>", "Jane": "<APPROVER>"})
        self.assertEqual(out, "Send to <EMAIL>, sheet <SHEET_ID>, ask <APPROVER>")

    def test_matches_whole_words_only(self):
        self.assertEqual(sync.redact("Ann approved in Annual", {"Ann": "<SUPERVISOR>"}),
                         "<SUPERVISOR> approved in Annual")

    def test_ids_match_inside_escaped_text(self):
        self.assertEqual(sync.redact(r"'\x271-AbC9_x\x27'", {"1-AbC9_x": "<ID>"}), r"'\x27<ID>\x27'")

    def test_keeps_noreply_and_example_emails(self):
        s = "noreply@anthropic.com you@example.com ssh -T git@github.com"
        self.assertEqual(sync.redact(s, {}), s)


class ScanTests(unittest.TestCase):
    def test_flags_known_secret_shapes(self):
        for s in ["sk-ant-api03-" + "a" * 40, "ghp_" + "A" * 36, "github_pat_" + "a" * 50,
                  "fc-" + "0123456789abcdef" * 2, "AIza" + "B" * 35, "xoxb-1234-5678-abcd",
                  "AKIA" + "ABCDEFGHIJKLMNOP", "-----BEGIN RSA PRIVATE KEY-----",
                  "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.abcdefghijklmnop"]:
            self.assertTrue(sync.scan_secrets(s), s)

    def test_ignores_placeholders(self):
        self.assertEqual(sync.scan_secrets('api_key = "<REDACTED>" sk-... fc-YOUR_KEY'), [])


if __name__ == "__main__":
    unittest.main()
