#!/usr/bin/env python3
# Adapted from warpdotdev/common-skills skill-doctor (MIT, Copyright (c) 2026 Denver Technologies, Inc.)
"""Tests for reflect report rendering."""

import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from render_report import (
    format_generated_at,
    grade_for,
    main,
    open_report,
    parse_args,
    render_page,
)

ALL_SCORES = {
    "efficiency": 1.0,
    "code_quality": 0.9,
    "procedure_compliance": 0.8,
    "verbosity": 0.7,
    "skill_coverage": 0.6,
    "overall": 0.83,
}

ALLOWED_TAGS = {
    "html", "head", "meta", "title", "style", "body", "header", "main", "section", "div",
    "span", "h1", "h2", "p", "ul", "ol", "li", "b", "code", "pre", "details", "summary",
}


class TagCollector(HTMLParser):
    """Collects real tags and attributes (escaped text never shows up here)."""

    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.extend(name for name, _ in attrs)


def assert_inert(test, page):
    """No scripts, no resource-loading tags, no event handlers or links."""
    parsed = TagCollector()
    parsed.feed(page)
    test.assertTrue(set(parsed.tags) <= ALLOWED_TAGS, set(parsed.tags) - ALLOWED_TAGS)
    test.assertFalse([a for a in parsed.attrs if a in ("src", "href", "action", "poster") or a.startswith("on")])
    test.assertNotRegex(page, r"url\(|@import|@font-face")


def long_diff(lines):
    body = "\n".join(f"+added line {i}" for i in range(lines))
    return f"--- a/SKILL.md\n+++ b/SKILL.md\n@@ -1,1 +1,{lines} @@\n{body}"


class ReportRendererTests(unittest.TestCase):
    def test_report_renders_letter_grade_and_numeric_value(self):
        page = render_page({"scores": {"overall": 0.7}})

        self.assertIn('<div class="grade">C</div>', page)
        self.assertIn('<div class="grade-label">overall 0.70</div>', page)

    def test_grade_thresholds(self):
        for score, letter in [
            (1.0, "A"), (0.9, "A"), (0.89, "B"), (0.8, "B"),
            (0.79, "C"), (0.7, "C"), (0.69, "D"), (0.6, "D"), (0.59, "F"), (0.0, "F"),
        ]:
            self.assertEqual(grade_for(score), letter, score)

    def test_scorecard_lists_every_metric_with_value(self):
        page = render_page({"scores": ALL_SCORES})

        for name in ["Efficiency", "Code Quality", "Procedure Compliance", "Verbosity", "Skill Coverage"]:
            self.assertIn(name, page)
        self.assertIn("0.80", page)
        self.assertIn("width:60%", page)

    def test_report_follows_os_theme(self):
        page = render_page({"scores": ALL_SCORES})

        self.assertIn('<meta name="color-scheme" content="light dark">', page)
        self.assertIn("@media (prefers-color-scheme: dark)", page)
        self.assertIn(":root {", page)
        self.assertRegex(page, r"body \{[^}]*background: var\(--bg\)")
        self.assertIn('<meta name="viewport"', page)

    def test_header_shows_generated_time_harness_and_mode_note(self):
        page = render_page({
            "title": "Reflect Report",
            "generated_at": "2026-08-25T00:00:00Z",
            "harness": "claude",
            "mode_note": "Scored from the current session only.",
            "scores": ALL_SCORES,
        })

        self.assertIn("Generated August 25, 2026 at 12:00 AM UTC", page)
        self.assertIn("harness: claude", page)
        self.assertIn("Scored from the current session only.", page)

    def test_empty_mode_note_renders_nothing(self):
        body = render_page({"mode_note": "", "scores": ALL_SCORES}).split("</style>")[1]

        self.assertNotIn("mode-note", body)

    def test_stats_strip_and_findings_render(self):
        page = render_page({
            "stats": {"sessions_analyzed": 7, "sessions_scanned": 12,
                      "skills_found": 5, "skills_used": 3, "window_days": 30},
            "scores": ALL_SCORES,
            "top_findings": ["First finding.", "Second finding."],
        })

        for expected in ["First finding.", "Second finding.", ">7<", ">12<", ">5<", ">3<", ">30<"]:
            self.assertIn(expected, page)

    def test_generated_timestamp_formatting(self):
        self.assertEqual(
            format_generated_at("2026-08-27T22:06:10.421941+00"),
            "August 27, 2026 at 10:06 PM UTC",
        )
        self.assertEqual(format_generated_at("not-a-date"), "not-a-date")

    def test_open_report_uses_default_browser_with_file_uri(self):
        report_path = Path("/tmp/reflect report/report.html")
        args = parse_args([str(report_path), "--open"])

        self.assertEqual(args.report_path, str(report_path))
        self.assertTrue(args.open_browser)

        with patch("render_report.webbrowser.open", return_value=True) as browser_open:
            self.assertTrue(open_report(report_path))

        browser_open.assert_called_once_with(report_path.absolute().as_uri(), new=2)

        with patch("render_report.webbrowser.open", side_effect=OSError):
            self.assertFalse(open_report(report_path))

    def test_untrusted_text_is_html_escaped(self):
        evil = "<script>alert(1)</script>"
        page = render_page({
            "title": evil,
            "handle": evil,
            "harness": evil,
            "mode_note": evil,
            "scores": ALL_SCORES,
            "top_findings": [evil, "<img src=x onerror=alert(1)>"],
            "suggestions": [{
                "skill": evil,
                "change": '"><img src=x onerror=alert(2)>',
                "evidence": "<b onmouseover=alert(3)>x</b>",
                "proposed_path": "javascript:alert(4)",
                "diff": "@@ -1 +1 @@\n-ok\n+<img src=x onerror=alert(5)>\n+<script>steal()</script>",
            }],
        })

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        self.assertIn("&lt;script&gt;steal()&lt;/script&gt;", page)
        assert_inert(self, page)
        self.assertNotIn("<script", page)

    def test_missing_optional_fields_do_not_crash(self):
        for report in [
            {},
            {"scores": {}},
            {"scores": {"overall": "n/a"}, "stats": None, "top_findings": "one string",
             "suggestions": [None, "x", {}], "cta_url": "https://example.invalid/x",
             "unknown_field": {"a": 1}},
            {"scores": {"overall": 0.5}, "suggestions": [{"skill": "s", "diff": None}]},
        ]:
            self.assertIn("</html>", render_page(report))
        self.assertNotIn("example.invalid", render_page({"cta_url": "https://example.invalid/x"}))

    def test_long_diff_is_collapsed_in_details(self):
        page = render_page({"scores": ALL_SCORES, "suggestions": [
            {"skill": "s", "change": "c", "diff": long_diff(40)}]})

        self.assertRegex(page, r"<details[^>]*>\s*<summary>[^<]*</summary>\s*<pre")
        self.assertNotRegex(page, r"<details[^>]*\sopen")
        self.assertIn("+added line 39", page)

    def test_short_diff_is_not_collapsed(self):
        page = render_page({"scores": ALL_SCORES, "suggestions": [
            {"skill": "s", "change": "c", "diff": long_diff(5)}]})

        self.assertNotIn("<details", page)
        self.assertIn('<pre class="diff">', page)

    def test_diff_lines_are_colored_by_kind(self):
        page = render_page({"scores": ALL_SCORES, "suggestions": [
            {"skill": "s", "diff": "--- a/x\n+++ b/x\n@@ -1,2 +1,2 @@\n context\n-gone\n+new"}]})

        self.assertIn('<span class="hunk">@@ -1,2 +1,2 @@</span>', page)
        self.assertIn('<span class="del">-gone</span>', page)
        self.assertIn('<span class="add">+new</span>', page)
        self.assertIn('<span class="meta">--- a/x</span>', page)

    def test_removed_line_starting_with_dashes_after_hunk_is_a_deletion(self):
        page = render_page({"scores": ALL_SCORES, "suggestions": [
            {"skill": "s", "diff": "@@ -1 +1 @@\n--- old yaml separator\n+++ new\n"}]})

        self.assertIn('<span class="del">--- old yaml separator</span>', page)
        self.assertIn('<span class="add">+++ new</span>', page)

    def test_output_has_no_external_resources(self):
        page = render_page({
            "title": "t", "scores": ALL_SCORES,
            "top_findings": ["see https://example.com/page for details"],
            "suggestions": [{"skill": "s", "change": "c",
                             "evidence": "http://example.com/a",
                             "diff": "+link https://example.com/b"}],
        })

        # URLs survive only as text content.
        self.assertIn("https://example.com/page", page)
        assert_inert(self, page)
        # With no URLs in the input, none appear anywhere (no CDN, fonts, namespaces).
        self.assertNotRegex(render_page({"scores": ALL_SCORES}), r"https?://")

    def test_main_writes_html_next_to_json_and_survives_non_ascii(self):
        title = "Réflexion — 日本語"
        with tempfile.TemporaryDirectory() as tmp:
            report_json = Path(tmp) / "report.json"
            report_json.write_text(
                json.dumps({"title": title, "scores": ALL_SCORES}), encoding="utf-8")

            main([str(report_json)])

            out = (Path(tmp) / "report.html").read_text(encoding="utf-8")
            self.assertIn(title, out)


if __name__ == "__main__":
    unittest.main()
