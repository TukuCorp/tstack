"""Tests for the pure logic added to cc-nightly.py (usage parsing, failure streaks).

Run: python test_cc_nightly.py
"""
import importlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

nightly = importlib.import_module("cc-nightly")


class ParseUsageTests(unittest.TestCase):
    def test_percent_used(self):
        self.assertEqual(nightly.parse_usage_remaining("Current session: 35% used"), 65)

    def test_percent_left(self):
        self.assertEqual(nightly.parse_usage_remaining("Session · 80% left · resets 14:00"), 80)

    def test_percent_remaining(self):
        self.assertEqual(nightly.parse_usage_remaining("12% remaining"), 12)

    def test_no_match_returns_none(self):
        self.assertIsNone(nightly.parse_usage_remaining("no usage info in this pane"))

    def test_first_match_wins(self):
        text = "Current session: 40% used\nWeekly: 90% used"
        self.assertEqual(nightly.parse_usage_remaining(text), 60)


class ConsecutiveFailuresTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl",
                                               delete=False, encoding="utf-8")
        self.path = Path(self.tmp.name)
        self.orig = nightly.LEDGER_FILE
        nightly.LEDGER_FILE = self.path

    def tearDown(self):
        nightly.LEDGER_FILE = self.orig
        self.tmp.close()
        self.path.unlink(missing_ok=True)

    def write(self, entries):
        self.tmp.write("\n".join(json.dumps(e) for e in entries) + "\n")
        self.tmp.flush()

    def test_empty_ledger(self):
        self.tmp.flush()
        self.assertEqual(nightly.consecutive_failures("dss-grid"), 0)

    def test_streak_counted(self):
        self.write([
            {"project": "dss-grid", "status": "done"},
            {"project": "dss-grid", "status": "failed"},
            {"project": "dss-grid", "status": "failed"},
        ])
        self.assertEqual(nightly.consecutive_failures("dss-grid"), 2)

    def test_success_breaks_streak(self):
        self.write([
            {"project": "dss-grid", "status": "failed"},
            {"project": "dss-grid", "status": "done"},
            {"project": "dss-grid", "status": "failed"},
        ])
        self.assertEqual(nightly.consecutive_failures("dss-grid"), 1)

    def test_other_projects_ignored(self):
        self.write([
            {"project": "dss-grid", "status": "failed"},
            {"project": "pdd-auto", "status": "done"},
            {"project": "dss-grid", "status": "failed"},
        ])
        self.assertEqual(nightly.consecutive_failures("dss-grid"), 2)

    def test_deferred_does_not_affect_streak(self):
        self.write([
            {"project": "dss-grid", "status": "failed"},
            {"project": "dss-grid", "status": "deferred"},
            {"project": "dss-grid", "status": "failed"},
        ])
        self.assertEqual(nightly.consecutive_failures("dss-grid"), 2)


class LoadProjectsTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp_dir.name) / "cc-nightly-projects.json"
        self.orig = nightly.PROJECTS_CONFIG_FILE
        nightly.PROJECTS_CONFIG_FILE = self.path

    def tearDown(self):
        nightly.PROJECTS_CONFIG_FILE = self.orig
        self.tmp_dir.cleanup()

    def write(self, obj):
        self.path.write_text(json.dumps(obj), encoding="utf-8")

    def test_enabled_only_returned_in_file_order(self):
        self.write({"projects": [
            {"name": "a", "branch": "main", "enabled": True},
            {"name": "b", "branch": "main", "enabled": False},
            {"name": "c", "branch": "master", "enabled": True},
        ]})
        names, branches = nightly.load_projects()
        self.assertEqual(names, ["a", "c"])
        self.assertEqual(branches, {"a": "main", "b": "main", "c": "master"})

    def test_missing_file_returns_seed_fallback(self):
        # Compared against the constant, not a hardcoded roster: seeding a new
        # project should not break this test (it did, when freecad-blender was
        # added and these assertions still expected the original six).
        names, branches = nightly.load_projects()
        self.assertEqual(set(names), set(nightly.FALLBACK_PROJECTS))
        self.assertEqual(branches["dppa-case"], "master")
        self.assertEqual(branches["dss-grid"], "main")

    def test_malformed_json_returns_seed_fallback(self):
        self.path.write_text("not json", encoding="utf-8")
        names, branches = nightly.load_projects()
        self.assertEqual(len(names), len(nightly.FALLBACK_PROJECTS))
        self.assertEqual(branches["carbonsim-online"], "master")


class CooldownPickTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        base = Path(self.tmp_dir.name)
        self.state_path = base / "state.json"
        self.ledger_path = base / "ledger.jsonl"
        self.projects_path = base / "projects.json"
        self.orig_state = nightly.STATE_FILE
        self.orig_ledger = nightly.LEDGER_FILE
        self.orig_projects = nightly.PROJECTS_CONFIG_FILE
        # Redirected to a path that does not exist: without this, a real
        # cooldown override sitting in ~/.hermes leaks into these tests and
        # silently turns every cooldown assertion green.
        self.orig_override = nightly.COOLDOWN_OVERRIDE_FILE
        nightly.COOLDOWN_OVERRIDE_FILE = base / "no-override.json"
        nightly.STATE_FILE = self.state_path
        nightly.LEDGER_FILE = self.ledger_path
        nightly.PROJECTS_CONFIG_FILE = self.projects_path

    def tearDown(self):
        nightly.STATE_FILE = self.orig_state
        nightly.LEDGER_FILE = self.orig_ledger
        nightly.PROJECTS_CONFIG_FILE = self.orig_projects
        nightly.COOLDOWN_OVERRIDE_FILE = self.orig_override
        self.tmp_dir.cleanup()

    def write_projects(self, names):
        self.projects_path.write_text(json.dumps({
            "projects": [{"name": n, "branch": "main", "enabled": True} for n in names]
        }), encoding="utf-8")

    def write_state(self, order, current_index):
        self.state_path.write_text(json.dumps({
            "order": order, "current_index": current_index
        }), encoding="utf-8")

    def write_ledger(self, entries):
        with self.ledger_path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

    def days_ago(self, n):
        return (datetime.now(timezone.utc).astimezone() - timedelta(days=n)).isoformat()

    def test_last_visit_days_basic(self):
        self.write_ledger([
            {"project": "dss-grid", "status": "done", "ts": self.days_ago(8)},
        ])
        days = nightly.last_visit_days("dss-grid")
        self.assertAlmostEqual(days, 8.0, delta=0.01)

    def test_last_visit_days_ignores_deferred(self):
        self.write_ledger([
            {"project": "dss-grid", "status": "deferred", "ts": self.days_ago(1)},
        ])
        self.assertIsNone(nightly.last_visit_days("dss-grid"))

    def test_last_visit_days_never_seen(self):
        self.write_ledger([
            {"project": "other", "status": "done", "ts": self.days_ago(1)},
        ])
        self.assertIsNone(nightly.last_visit_days("never-seen"))

    def test_picks_eligible_project_off_cooldown(self):
        self.write_projects(["a", "b"])
        self.write_state(["a", "b"], 0)
        self.write_ledger([
            {"project": "a", "status": "done", "ts": self.days_ago(2)},
            {"project": "b", "status": "done", "ts": self.days_ago(9)},
        ])
        picked = nightly.pick_project()
        self.assertEqual(picked, "b")
        state = json.loads(self.state_path.read_text())
        self.assertEqual(state["current_index"], 2)

    def test_all_on_cooldown_returns_none(self):
        self.write_projects(["a", "b"])
        self.write_state(["a", "b"], 0)
        self.write_ledger([
            {"project": "a", "status": "done", "ts": self.days_ago(1)},
            {"project": "b", "status": "done", "ts": self.days_ago(1)},
        ])
        self.assertIsNone(nightly.pick_project())

    def test_failure_streak_still_blocks_even_off_cooldown(self):
        self.write_projects(["x"])
        self.write_state(["x"], 0)
        self.write_ledger([
            {"project": "x", "status": "done", "ts": self.days_ago(20)},
            {"project": "x", "status": "failed", "ts": self.days_ago(10)},
            {"project": "x", "status": "failed", "ts": self.days_ago(9)},
        ])
        self.assertIsNone(nightly.pick_project())

    def test_deferred_run_does_not_rewind_slot(self):
        # A project that was 'deferred' keeps last_visit_days == None (ignored),
        # so it stays immediately eligible next run rather than being force-picked.
        self.write_projects(["a", "b"])
        self.write_state(["a", "b"], 1)  # index already advanced past 'a' by the deferred run
        self.write_ledger([
            {"project": "a", "status": "deferred", "ts": self.days_ago(0)},
        ])
        picked = nightly.pick_project()
        self.assertEqual(picked, "b")
        state = json.loads(self.state_path.read_text())
        self.assertEqual(state["current_index"], 2)


class PlanScanTests(unittest.TestCase):
    def test_parse_frontmatter_basic(self):
        text = '---\ntitle: "X"\nstatus: "draft"\n---\n# Body'
        self.assertEqual(nightly.parse_plan_frontmatter(text),
                          {"title": "X", "status": "draft"})

    def test_parse_frontmatter_missing(self):
        self.assertEqual(nightly.parse_plan_frontmatter("# No frontmatter here"), {})

    def test_parse_frontmatter_ignores_list_values(self):
        text = '---\nstatus: draft\nresearch_inputs:\n  - "a.md"\n---'
        self.assertEqual(nightly.parse_plan_frontmatter(text), {"status": "draft"})

    def test_normalize_draft_is_open(self):
        self.assertEqual(nightly.normalize_status("draft"), "open")

    def test_normalize_completed_is_complete(self):
        self.assertEqual(nightly.normalize_status("completed"), "complete")

    def test_normalize_complete_is_complete(self):
        self.assertEqual(nightly.normalize_status("complete"), "complete")

    def test_normalize_partially_implemented_is_open(self):
        self.assertEqual(nightly.normalize_status("partially_implemented"), "open")

    def test_normalize_scope_locked_is_open(self):
        self.assertEqual(nightly.normalize_status("scope-locked"), "open")

    def test_normalize_superseded_with_prose_truncates(self):
        raw = "superseded — PHASE-03 obsoleted by 2026-07-04-other-plan.md"
        self.assertEqual(nightly.normalize_status(raw), "superseded")

    def test_normalize_in_progress_with_prose_is_open(self):
        raw = "in-progress — PHASE-01–04 implemented, PHASE-05/06 pending"
        self.assertEqual(nightly.normalize_status(raw), "open")

    def test_normalize_none_is_open(self):
        self.assertEqual(nightly.normalize_status(None), "open")

    def test_normalize_unrecognized_is_open(self):
        self.assertEqual(nightly.normalize_status("something nobody has ever written"), "open")

    def test_plan_progress_counts_task_checkboxes_only(self):
        text = "- [x] TASK-01-01: a\n- [ ] TASK-01-02: b\n- [ ] Exit criterion"
        self.assertEqual(nightly.plan_progress(text), (1, 2))

    def test_plan_progress_no_tasks(self):
        self.assertEqual(nightly.plan_progress("# A plan with prose only"), (0, 0))

    def test_scan_plans_excludes_progress_md(self):
        with tempfile.TemporaryDirectory() as d:
            project_dir = Path(d)
            plans_dir = project_dir / "plans"
            plans_dir.mkdir()
            (plans_dir / "a.md").write_text('---\nstatus: "draft"\n---\n', encoding="utf-8")
            (plans_dir / "b.md").write_text('---\nstatus: "completed"\n---\n', encoding="utf-8")
            (plans_dir / "PROGRESS.md").write_text("# rollup\n", encoding="utf-8")

            records = nightly.scan_plans(project_dir)
            names = {r["name"] for r in records}
            self.assertEqual(len(records), 2)
            self.assertNotIn("PROGRESS.md", names)

    def test_scan_plans_no_plans_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(nightly.scan_plans(Path(d)), [])

    def test_open_plans_filters_to_open_only(self):
        with tempfile.TemporaryDirectory() as d:
            project_dir = Path(d)
            plans_dir = project_dir / "plans"
            plans_dir.mkdir()
            (plans_dir / "a.md").write_text('---\nstatus: "draft"\n---\n', encoding="utf-8")
            (plans_dir / "b.md").write_text('---\nstatus: "completed"\n---\n', encoding="utf-8")

            records = nightly.scan_plans(project_dir)
            open_records = nightly.open_plans(records)
            self.assertEqual(len(open_records), 1)
            self.assertEqual(open_records[0]["name"], "a.md")


class NotificationTests(unittest.TestCase):
    def test_format_first_line_and_fields(self):
        body = nightly.format_notification(
            "dss-grid", "planned", "cc-nightly-dss-grid-20260728", 0,
            detail="Plan saved, 6 phases",
            paths=["plans/2026-07-28-x-plan.md"])
        first_line = body.splitlines()[0]
        self.assertEqual(first_line, "CC Nightly — dss-grid — PLANNED")
        self.assertIn("Session: cc-nightly-dss-grid-20260728", body)
        self.assertIn("Open plans: 0", body)
        self.assertIn("plans/2026-07-28-x-plan.md", body)

    def test_format_truncates_to_discord_limit(self):
        body = nightly.format_notification(
            "pacta-trisk", "backlog", "s", 21, detail="x" * 5000)
        self.assertLessEqual(len(body), 1900)
        self.assertTrue(body.endswith("…"))

    def test_format_omits_files_line_when_no_paths(self):
        body = nightly.format_notification("dss-grid", "deferred", "s", 3)
        self.assertIn("DEFERRED", body)
        self.assertIn("Open plans: 3", body)
        self.assertNotIn("Files:", body)

    def test_notify_nonexistent_binary_returns_false(self):
        orig = nightly.HERMES_BIN
        nightly.HERMES_BIN = Path(self.__class__.__name__) / "definitely-does-not-exist.exe"
        try:
            result = nightly.notify("dss-grid", "planned", "s", 0)
        finally:
            nightly.HERMES_BIN = orig
        self.assertFalse(result)

    def test_notify_nonzero_exit_returns_false(self):
        # sys.executable is a real, always-present binary, but "send" is not
        # a script it can open — guarantees a clean nonzero exit rather than
        # a launch failure, without needing a purpose-built stub binary.
        import sys as _sys
        orig = nightly.HERMES_BIN
        nightly.HERMES_BIN = Path(_sys.executable)
        try:
            result = nightly.notify("dss-grid", "planned", "s", 0)
        finally:
            nightly.HERMES_BIN = orig
        self.assertFalse(result)


class LogFileTests(unittest.TestCase):
    def test_log_appends_to_log_file(self):
        with tempfile.TemporaryDirectory() as d:
            orig_dir = nightly.LOG_DIR
            orig_file = nightly.LOG_FILE
            nightly.LOG_DIR = Path(d)
            nightly.LOG_FILE = Path(d) / "test-run.log"
            try:
                nightly.log("hello from a test")
                content = nightly.LOG_FILE.read_text(encoding="utf-8")
            finally:
                nightly.LOG_DIR = orig_dir
                nightly.LOG_FILE = orig_file
            self.assertIn("hello from a test", content)


class SessionNamingTests(unittest.TestCase):
    """The pruning regex must match both the legacy timestamp-only session
    name and the current cc-nightly-<project>-<timestamp> name, including
    projects whose own name contains hyphens (e.g. carbonsim-online) — and
    must not match unrelated tmux sessions that happen to be named after a
    project (e.g. a session called just 'pdd-auto')."""

    def test_matches_old_timestamp_only_format(self):
        self.assertIsNotNone(nightly._SESSION_AGE_RE.match("cc-nightly-20260727-233001"))

    def test_matches_new_per_project_format(self):
        self.assertIsNotNone(
            nightly._SESSION_AGE_RE.match("cc-nightly-dss-grid-20260728-233001"))

    def test_matches_hyphenated_project_name(self):
        self.assertIsNotNone(
            nightly._SESSION_AGE_RE.match("cc-nightly-carbonsim-online-20260728-233001"))

    def test_does_not_match_unrelated_sessions(self):
        self.assertIsNone(nightly._SESSION_AGE_RE.match("pdd-auto"))
        self.assertIsNone(nightly._SESSION_AGE_RE.match("reopt-pysam"))


class StageExecutionPromptTests(unittest.TestCase):
    def setUp(self):
        self.orig_send = nightly.send
        self.orig_log_dir = nightly.LOG_DIR
        self.tmp = tempfile.TemporaryDirectory()
        nightly.LOG_DIR = Path(self.tmp.name)

    def tearDown(self):
        nightly.send = self.orig_send
        nightly.LOG_DIR = self.orig_log_dir
        self.tmp.cleanup()

    def test_staged_but_not_submitted(self):
        sent = []
        nightly.send = lambda *a, **kw: sent.append((a, kw))
        nightly.stage_execution_prompt("plans/x-plan.md", "main")
        self.assertEqual(len(sent), 1)
        _args, kwargs = sent[0]
        self.assertEqual(kwargs.get("submit"), False)

    def test_plan_path_and_branch_reach_the_prompt_file(self):
        # The plan path and branch used to be asserted on the typed text.
        # They now live in the prompt file — the typed line is only a pointer,
        # because a typed multi-line prompt gets paste-collapsed and dropped.
        nightly.send = lambda *a, **kw: None
        written = list(Path(self.tmp.name).glob("*.md"))
        self.assertEqual(written, [])
        nightly.stage_execution_prompt("plans/x-plan.md", "main")
        written = list(Path(self.tmp.name).glob("*execute.md"))
        self.assertEqual(len(written), 1)
        body = written[0].read_text(encoding="utf-8")
        self.assertIn("plans/x-plan.md", body)
        self.assertIn("git checkout main", body)


class PhaseBacklogTests(unittest.TestCase):
    def setUp(self):
        self.orig_pane = nightly.pane
        self.orig_send = nightly.send
        self.orig_scan = nightly.scan_plans
        self.orig_max_checks = nightly.BACKLOG_MAX_CHECKS
        self.orig_interval = nightly.CHECK_INTERVAL
        # LOG_DIR is redirected because phase_backlog now writes its prompt to
        # a file — without this the suite litters the real cc-nightly-logs dir.
        self.orig_log_dir = nightly.LOG_DIR
        self.tmp = tempfile.TemporaryDirectory()
        nightly.LOG_DIR = Path(self.tmp.name)
        nightly.send = lambda *a, **kw: None
        nightly.BACKLOG_MAX_CHECKS = 2
        nightly.CHECK_INTERVAL = 0.01

    def tearDown(self):
        nightly.pane = self.orig_pane
        nightly.send = self.orig_send
        nightly.scan_plans = self.orig_scan
        nightly.BACKLOG_MAX_CHECKS = self.orig_max_checks
        nightly.CHECK_INTERVAL = self.orig_interval
        nightly.LOG_DIR = self.orig_log_dir
        self.tmp.cleanup()

    def test_marker_seen_returns_true_and_rescanned_open_count(self):
        nightly.pane = lambda: "triaging...\nBACKLOG_TRIAGED: 3\ndone"
        nightly.scan_plans = lambda project_dir: [
            {"status": "open"}, {"status": "open"}, {"status": "complete"},
        ]
        records = [{"name": "a.md", "raw_status": "draft", "done": 0,
                    "total": 3, "age_days": 5.0}]
        marker_seen, open_after = nightly.phase_backlog("dss-grid", Path("."), records)
        self.assertTrue(marker_seen)
        self.assertEqual(open_after, 2)

    def test_angle_bracket_echo_is_not_treated_as_marker(self):
        # The prompt itself contains the literal text
        # 'BACKLOG_TRIAGED: <number of plans you closed>' — if CC's pane
        # echoes the instructions back before acting, find_marker() must
        # reject the angle-bracketed placeholder rather than treat it as
        # a real completion marker.
        nightly.pane = lambda: "BACKLOG_TRIAGED: <number of plans you closed>"
        nightly.scan_plans = lambda project_dir: []
        records = [{"name": "a.md", "raw_status": "draft", "done": 0,
                    "total": 3, "age_days": 5.0}]
        marker_seen, _open_after = nightly.phase_backlog("dss-grid", Path("."), records)
        self.assertFalse(marker_seen)


class SendPromptTests(unittest.TestCase):
    """send_prompt() must hand CC a file to read rather than typing the prompt.

    CC's TUI classifies a multi-line send-keys burst as a paste, collapses it,
    and DISCARDS the body — the model receives only the trailing fragment.
    """

    def setUp(self):
        self.orig_send = nightly.send
        self.orig_log_dir = nightly.LOG_DIR
        self.tmp = tempfile.TemporaryDirectory()
        nightly.LOG_DIR = Path(self.tmp.name)
        self.sent = []
        nightly.send = lambda text, submit=True: self.sent.append((text, submit))

    def tearDown(self):
        nightly.send = self.orig_send
        nightly.LOG_DIR = self.orig_log_dir
        self.tmp.cleanup()

    def test_writes_full_prompt_to_file(self):
        body = "line one — with an em-dash\nline two\nline three"
        path = nightly.send_prompt(body, "unit")
        self.assertEqual(path.read_text(encoding="utf-8"), body)

    def test_typed_text_is_a_single_line_pointing_at_the_file(self):
        path = nightly.send_prompt("a\nb\nc\nd\ne\nf\ng\nh\ni\nj\nk\nl\nm", "unit")
        self.assertEqual(len(self.sent), 1)
        text, _submit = self.sent[0]
        self.assertNotIn("\n", text)
        self.assertIn(str(path), text)

    def test_submit_flag_is_forwarded(self):
        nightly.send_prompt("x\ny", "unit", submit=False)
        self.assertEqual(self.sent[0][1], False)


class NoMultilineSendTests(unittest.TestCase):
    """Regression guard: no phase may ever type a multi-line prompt into the
    TUI. Anything with a newline gets paste-collapsed and silently dropped —
    this is what made the 2026-07-29 freecad-blender run fail with the model
    replying 'I'm ready. What would you like to work on?'."""

    def setUp(self):
        self.orig = {n: getattr(nightly, n) for n in
                     ("send", "pane", "scan_plans", "LOG_DIR",
                      "BACKLOG_MAX_CHECKS", "BRAINSTORM_MAX_CHECKS",
                      "CHECK_INTERVAL")}
        self.tmp = tempfile.TemporaryDirectory()
        nightly.LOG_DIR = Path(self.tmp.name)
        self.sent = []
        nightly.send = lambda text, submit=True: self.sent.append(text)
        nightly.BACKLOG_MAX_CHECKS = 1
        nightly.BRAINSTORM_MAX_CHECKS = 1
        nightly.CHECK_INTERVAL = 0.01
        nightly.scan_plans = lambda project_dir: []

    def tearDown(self):
        for n, v in self.orig.items():
            setattr(nightly, n, v)
        self.tmp.cleanup()

    def assert_all_single_line(self):
        for text in self.sent:
            self.assertNotIn("\n", text,
                             f"multi-line text typed into the TUI: {text[:80]!r}")

    def test_phase_backlog_types_only_single_lines(self):
        nightly.pane = lambda: "BACKLOG_TRIAGED: 2"
        records = [{"name": "a.md", "raw_status": "draft", "done": 0,
                    "total": 3, "age_days": 5.0}]
        nightly.phase_backlog("dss-grid", Path("."), records)
        self.assert_all_single_line()

    def test_phase_brainstorm_types_only_single_lines(self):
        nightly.pane = lambda: "BRAINSTORM_DONE: research/x-brainstorm.md"
        nightly.phase_brainstorm("dss-grid", Path("."))
        self.assert_all_single_line()

    def test_stage_execution_prompt_types_only_single_lines(self):
        nightly.stage_execution_prompt("plans/x-plan.md", "main")
        self.assert_all_single_line()


class CooldownOverrideTests(unittest.TestCase):
    """A time-boxed escape hatch for observing runs on demand: while it is in
    force, pick_project() ignores COOLDOWN_DAYS. Time-boxed rather than a
    boolean so that forgetting to remove it cannot silently disable the
    rotation forever — it expires on its own."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        base = Path(self.tmp_dir.name)
        self.override_path = base / "override.json"
        self.state_path = base / "state.json"
        self.ledger_path = base / "ledger.jsonl"
        self.projects_path = base / "projects.json"
        self.orig = (nightly.COOLDOWN_OVERRIDE_FILE, nightly.STATE_FILE,
                     nightly.LEDGER_FILE, nightly.PROJECTS_CONFIG_FILE)
        nightly.COOLDOWN_OVERRIDE_FILE = self.override_path
        nightly.STATE_FILE = self.state_path
        nightly.LEDGER_FILE = self.ledger_path
        nightly.PROJECTS_CONFIG_FILE = self.projects_path

    def tearDown(self):
        (nightly.COOLDOWN_OVERRIDE_FILE, nightly.STATE_FILE,
         nightly.LEDGER_FILE, nightly.PROJECTS_CONFIG_FILE) = self.orig
        self.tmp_dir.cleanup()

    def write_override(self, hours_from_now):
        until = datetime.now(timezone.utc).astimezone() + timedelta(hours=hours_from_now)
        self.override_path.write_text(
            json.dumps({"ignore_cooldown_until": until.isoformat()}), encoding="utf-8")

    def setup_all_on_cooldown(self, names=("alpha", "beta")):
        self.projects_path.write_text(json.dumps({
            "projects": [{"name": n, "branch": "main", "enabled": True} for n in names]
        }), encoding="utf-8")
        self.state_path.write_text(json.dumps({
            "order": list(names), "current_index": 0}), encoding="utf-8")
        recent = (datetime.now(timezone.utc).astimezone() - timedelta(hours=2)).isoformat()
        with self.ledger_path.open("w", encoding="utf-8") as f:
            for n in names:
                f.write(json.dumps({"project": n, "status": "done", "ts": recent}) + "\n")

    def test_inactive_when_file_missing(self):
        self.assertFalse(nightly.cooldown_override_active())

    def test_active_within_window(self):
        self.write_override(6)
        self.assertTrue(nightly.cooldown_override_active())

    def test_expired_window_is_inactive(self):
        self.write_override(-1)
        self.assertFalse(nightly.cooldown_override_active())

    def test_malformed_file_is_inactive(self):
        self.override_path.write_text("not json", encoding="utf-8")
        self.assertFalse(nightly.cooldown_override_active())

    def test_pick_project_skips_everything_without_override(self):
        self.setup_all_on_cooldown()
        self.assertIsNone(nightly.pick_project())

    def test_pick_project_ignores_cooldown_while_override_active(self):
        self.setup_all_on_cooldown()
        self.write_override(6)
        self.assertEqual(nightly.pick_project(), "alpha")

    def test_override_does_not_bypass_failure_streak(self):
        # The streak guard is a separate safety: a repo failing repeatedly
        # needs a human, and burning a forced run on it helps nobody.
        self.setup_all_on_cooldown()
        self.write_override(6)
        fails = [{"project": "alpha", "status": "failed",
                  "ts": (datetime.now(timezone.utc).astimezone()
                         - timedelta(hours=3)).isoformat()}
                 for _ in range(nightly.FAILURE_SKIP_STREAK)]
        with self.ledger_path.open("a", encoding="utf-8") as f:
            for e in fails:
                f.write(json.dumps(e) + "\n")
        self.assertEqual(nightly.pick_project(), "beta")


class BacklogPromptTests(unittest.TestCase):
    """A plan with no `status:` frontmatter normalizes to 'open' forever, so a
    repo containing one can never leave backlog mode and never reaches
    brainstorm/plan again. The triage prompt must therefore authorize ADDING
    frontmatter, not just editing an existing field. Observed on dss-grid and
    pdd-auto, 2026-07-30."""

    def test_missing_frontmatter_normalizes_to_open(self):
        # The reason the prompt instruction below has to exist.
        self.assertEqual(nightly.normalize_status(None), "open")

    def test_prompt_authorizes_adding_absent_frontmatter(self):
        t = nightly._BACKLOG_PROMPT_TEMPLATE.lower()
        self.assertIn("no yaml frontmatter", t)
        self.assertIn("add", t)

    def test_prompt_still_confines_edits_to_plans_dir(self):
        # The new instruction must not widen the blast radius.
        self.assertIn("Edit ONLY files under plans/",
                      nightly._BACKLOG_PROMPT_TEMPLATE)


class ApiStallTests(unittest.TestCase):
    """An upstream 529/rate-limit is not a project failure. Recorded as
    'failed' it would count toward FAILURE_SKIP_STREAK and consume the
    cooldown slot, so two unlucky runs could self-block a healthy repo.
    Observed live on pdd-auto, 2026-07-30."""

    # Verbatim from the failing pdd-auto session.
    HARD_ERROR = ("● API Error: 529 Overloaded. This is a server-side issue, "
                  "usually temporary — try again in a moment. If it persists, "
                  "check https://status.claude.com.\n✻ Cogitated for 3m 21s")
    RETRYING = "✻ 529 Overloaded · Retrying in 30s · attempt 8/10"
    # The generic form, with no status code and a lowercase 'error'. Seen on
    # the same session moments later — an earlier regex missed it entirely.
    RETRYING_GENERIC = "✻ API error · Retrying in 0s · attempt 1/10"
    HEALTHY = ("● Reading 4 files, listing 2 directories\n"
               "  ⎿  $ git show --stat 8a8e206\n✻ Topsy-turvying… (1m 7s)")

    def setUp(self):
        self.orig_pane = nightly.pane

    def tearDown(self):
        nightly.pane = self.orig_pane

    def test_detects_hard_api_error(self):
        self.assertTrue(nightly.pane_shows_api_failure(self.HARD_ERROR))

    def test_detects_retry_exhaustion_line(self):
        self.assertTrue(nightly.pane_shows_api_failure(self.RETRYING))

    def test_detects_generic_retry_line_without_a_status_code(self):
        self.assertTrue(nightly.pane_shows_api_failure(self.RETRYING_GENERIC))

    def test_healthy_pane_is_not_an_api_failure(self):
        self.assertFalse(nightly.pane_shows_api_failure(self.HEALTHY))

    def test_ancient_api_error_outside_tail_window_is_ignored(self):
        # A stall with a long-resolved 529 far up the scrollback is still a
        # real failure — only the tail reflects the current state.
        p = self.HARD_ERROR + "\n" + ("\n".join(f"line {i}" for i in range(60)))
        self.assertFalse(nightly.pane_shows_api_failure(p))

    def test_stall_outcome_defers_on_api_failure(self):
        nightly.pane = lambda: self.HARD_ERROR
        status, detail = nightly.stall_outcome("backlog triage", "fallback")
        self.assertEqual(status, "deferred")
        self.assertIn("API", detail)

    def test_stall_outcome_fails_on_a_genuine_stall(self):
        nightly.pane = lambda: self.HEALTHY
        status, detail = nightly.stall_outcome("backlog triage", "fallback")
        self.assertEqual(status, "failed")
        self.assertEqual(detail, "fallback")

    def test_deferred_entries_do_not_build_a_failure_streak(self):
        with tempfile.TemporaryDirectory() as td:
            orig = nightly.LEDGER_FILE
            nightly.LEDGER_FILE = Path(td) / "ledger.jsonl"
            try:
                ts = datetime.now(timezone.utc).astimezone().isoformat()
                with nightly.LEDGER_FILE.open("w", encoding="utf-8") as f:
                    for _ in range(3):
                        f.write(json.dumps({"project": "p", "status": "deferred",
                                            "ts": ts}) + "\n")
                self.assertEqual(nightly.consecutive_failures("p"), 0)
            finally:
                nightly.LEDGER_FILE = orig


class WakeGateTests(unittest.TestCase):
    """The Hermes no_agent runner delivers a job's entire stdout to Discord
    unless the LAST non-empty stdout line is {"wakeAgent": false}. Because
    log() prints every line, without that gate the whole run log gets posted
    on top of the script's own hermes-send notification — two messages per
    run, one of them a wall of 'backlog check [...]' spam."""

    def test_gate_is_valid_json_disabling_wake(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            nightly.emit_wake_gate()
        last = [ln for ln in buf.getvalue().splitlines() if ln.strip()][-1]
        self.assertEqual(json.loads(last), {"wakeAgent": False})

    def test_gate_is_not_written_to_the_log_file(self):
        # It is a control signal for the runner, not part of the run record.
        import io
        import contextlib
        orig_log_dir = nightly.LOG_DIR
        orig_log_file = nightly.LOG_FILE
        with tempfile.TemporaryDirectory() as td:
            nightly.LOG_DIR = Path(td)
            nightly.LOG_FILE = Path(td) / "run.log"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    nightly.emit_wake_gate()
                self.assertFalse(nightly.LOG_FILE.exists() and
                                 "wakeAgent" in nightly.LOG_FILE.read_text(encoding="utf-8"))
            finally:
                nightly.LOG_DIR = orig_log_dir
                nightly.LOG_FILE = orig_log_file


if __name__ == "__main__":
    unittest.main()
