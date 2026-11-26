"""Golden tests: real fixture files (tests/fixtures, rebuilt by make_fixtures.py) with
hand-written expected findings. Run: python -X utf8 -m pytest -q -p no:cacheprovider tests"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))
FX = HERE / "fixtures"

import extract_numbers  # noqa: E402
import post_comments  # noqa: E402
import scan_workbook  # noqa: E402


def keys(res):
    return {(i["sheet"], i["cell"], i["kind"]) for i in res["issues"]}


def test_scan_finds_every_planted_defect():
    res = scan_workbook.scan(FX / "model.xlsx")
    k = keys(res)
    assert ("Calc", "E4", "inconsistent_formula") in k
    assert ("Calc", "E4", "hardcoded_literal") in k
    assert ("Calc", "D5", "constant_in_formula_run") in k
    assert ("Calc", "B7", "error_value") in k
    assert ("Calc", "B8", "volatile_function") in k
    assert ("Old", "-", "hidden_sheet") in k
    assert res["stats"]["uncalculated"] == 0


def test_scan_has_no_false_positives_on_clean_rows():
    res = scan_workbook.scan(FX / "model.xlsx")
    flagged = {(s, c) for s, c, kind in keys(res) if kind in {"inconsistent_formula", "hardcoded_literal"}}
    for c in ["B4", "C4", "D4", "F4", "C3", "D3", "E3", "F3", "C5", "E5", "F5"]:
        assert ("Calc", c) not in flagged, c


def test_literals_ignore_refs_sheet_names_and_strings():
    assert scan_workbook.literals_in("=Sheet2!B3*1.05") == ["1.05"]
    assert scan_workbook.literals_in("='FY 2026'!C4+A1") == []
    assert scan_workbook.literals_in('=IF(A1="Q3 2026",B2,0)') == []
    assert scan_workbook.literals_in("=SUM(A1:A10)*12") == []


def test_deck_tie_out():
    res = extract_numbers.extract(FX / "deck.pptx", FX / "model.xlsx")
    by_text = {}
    for r in res["numbers"]:
        by_text.setdefault(r["text"], r)
    assert by_text["1,823"]["status"] == "TIED"      # Calc!F3 = 1823.25...
    assert by_text["12%"]["status"] == "TIED"        # Inputs!B4 = 0.12
    assert by_text["$1,500"]["status"] == "TIED"
    assert by_text["7.3"]["status"] == "UNTIED"      # planted: ties to nothing
    assert by_text["189.0"]["status"] == "TIED"      # Calc!C4 = 189.0
    assert by_text["2026"]["likely_year"]
    assert any("chart 'Revenue'" in r["location"] for r in res["numbers"])
    assert "-1" not in by_text                       # "Year-1" is a label, not minus one


def test_hyphenated_labels_are_not_negative_numbers():
    texts = [n["text"] for n in extract_numbers.numbers_in("Year-1 revenue, Phase-2, COVID-19, net -4.5%")]
    assert texts == ["-4.5%"]


def test_report_units_and_scaling():
    res = extract_numbers.extract(FX / "report.docx", FX / "model.xlsx")
    by_text = {r["text"]: r for r in res["numbers"]}
    assert by_text["$1.5 k"]["status"] == "TIED"     # 1.5 k = 1500
    assert by_text["8%"]["status"] == "TIED"
    assert by_text["3.2 MtCO2e"]["unit"] == "MtCO2e"
    assert by_text["3.2 MtCO2e"]["status"] == "UNTIED"


def test_comment_validation_rejects_vague_and_unanchored():
    good = {"fileId": "x", "kind": "sheets", "comments": [
        {"location": "Calc!E4", "body": "Calc!E4 types 0.12 instead of Inputs!$B$4; link it."}]}
    assert post_comments.validate(good) == []
    vague = {"fileId": "x", "kind": "sheets", "comments": [
        {"location": "Calc!E4", "body": "This cell looks wrong."}]}
    errs = post_comments.validate(vague)
    assert any("must name its location" in e for e in errs)
    docs = {"fileId": "x", "kind": "docs", "comments": [{"body": "Source?"}]}
    assert any("exact quoted text" in e for e in post_comments.validate(docs))
    slides = {"fileId": "x", "kind": "slides", "comments": [
        {"location": "slide 1", "body": "Slide 1: 7.3-year payback does not tie to the model."}]}
    assert post_comments.validate(slides) == []
    anchored_doc = {"fileId": "x", "kind": "docs", "comments": [
        {"quote": "5.568.100", "body": "@owner Sums to 8,992,506 instead of 8,992,306."}]}
    assert post_comments.validate(anchored_doc) == []
    unanchored_doc = {"fileId": "x", "kind": "docs", "comments": [
        {"quote": "5.568.100", "anchored": False, "body": "Wrong sum."}]}
    assert any("must quote its target text" in e for e in post_comments.validate(unanchored_doc))
    docx_good = {"fileId": "x", "kind": "docx", "comments": [
        {"quote": "4.084.960,53", "body": "@owner Table 114 lacks tonnes for all 8 measures."}]}
    assert post_comments.validate(docx_good) == []
    docx_no_quote = {"fileId": "x", "kind": "docx", "comments": [{"body": "Fix this."}]}
    assert any("exact quoted text" in e for e in post_comments.validate(docx_no_quote))


def test_docx_inspection_and_guarded_browse_script(tmp_path):
    import zipfile

    p = tmp_path / "sample.docx"
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p><w:r><w:t>Live 4.084.960,53 value</w:t></w:r>'
        '<w:del><w:r><w:delText>Deleted 4.084.960,53</w:delText></w:r></w:del></w:p>'
        '<w:p><w:r><w:drawing><w:txbxContent><w:p><w:r><w:t>COVER BOX ONLY</w:t></w:r></w:p></w:txbxContent></w:drawing></w:r></w:p>'
        '<w:p><w:commentRangeStart w:id="1"/><w:r><w:t>4.084.960,53</w:t></w:r><w:commentRangeEnd w:id="1"/></w:p>'
        '</w:body></w:document>'
    )
    com_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:comment w:id="1" w:author="Tung Ho" w:date="2026-11-25T11:08:02Z">'
        '<w:p><w:r><w:t>Existing comment on 4.084.960,53</w:t></w:r></w:p></w:comment>'
        '</w:comments>'
    )
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("word/document.xml", doc_xml)
        z.writestr("word/comments.xml", com_xml)

    info = post_comments.inspect_docx(
        p,
        [
            {"quote": "Live 4.084.960,53", "body": "Body check"},
            {"quote": "COVER BOX ONLY", "body": "Box check"},
            {"quote": "Deleted 4.084.960,53", "body": "Deleted check"},
        ],
    )
    assert len(info["existing_comments"]) == 1
    assert info["existing_comments"][0]["anchor"] == "4.084.960,53"
    assert info["checks"][0]["matches"] == 1 and not info["checks"][0]["in_textbox"]
    assert info["checks"][1]["matches"] == 0 and info["checks"][1]["in_textbox"]
    assert info["checks"][2]["matches"] == 0

    js = post_comments.build_docx_browse_script(
        {"fileId": "FID123", "kind": "docx", "authuser": "<EMAIL>"},
        [{"quote": "Live 4.084.960,53", "occurrence": 1, "body": "@owner Check value"}],
    )
    assert "docs.google.com/document/d/FID123/edit?authuser=<EMAIL>" in js
    assert "docos-input-textarea" in js
    assert "composer_not_focused" in js


def test_find_quote_ranges_body_table_utf16_and_disambiguation():
    doc = {
        "revisionId": "rev-1",
        "tabs": [{
            "tabProperties": {"tabId": "t.0"},
            "documentTab": {"body": {"content": [
                {"paragraph": {"elements": [
                    {"startIndex": 1, "textRun": {"content": "Hi \U0001F642 "}},  # emoji = 2 UTF-16 units
                    {"startIndex": 7, "textRun": {"content": "5.568.100", "suggestedDeletionIds": ["s1"]}},
                    {"startIndex": 16, "textRun": {"content": "PA1 5.568.100 end\n"}},
                ]}},
                {"table": {"tableRows": [{"tableCells": [{"content": [
                    {"paragraph": {"elements": [
                        {"startIndex": 40, "textRun": {"content": "PA2 5.568.100 ok\n"}},
                    ]}}
                ]}]}]}},
            ]}},
        }],
    }
    matches = post_comments.find_quote_ranges(doc, "5.568.100")
    assert len(matches) == 2  # suggestedDeletionIds run skipped
    assert matches[0]["range"] == {"startIndex": 20, "endIndex": 29, "tabId": "t.0"}
    assert matches[1]["range"] == {"startIndex": 44, "endIndex": 53, "tabId": "t.0"}
    assert post_comments.resolve_doc_range(doc, {"quote": "5.568.100", "context": "PA2"}) == {
        "startIndex": 44, "endIndex": 53, "tabId": "t.0"
    }
    assert post_comments.resolve_doc_range(doc, {"quote": "5.568.100", "occurrence": 1}) == {
        "startIndex": 20, "endIndex": 29, "tabId": "t.0"
    }
    req = post_comments.build_insert_comment_request(
        {"body": "@a Fix", "assignee": "a@example.com"}, matches[1]["range"]
    )
    assert req == {"insertComment": {
        "content": "@a Fix",
        "range": {"startIndex": 44, "endIndex": 53, "tabId": "t.0"},
        "assigneeEmailAddress": "a@example.com",
    }}


def test_cli_writes_outputs(tmp_path):
    assert scan_workbook.main([str(FX / "model.xlsx"), "--out", str(tmp_path)]) == 0
    data = json.loads((tmp_path / "scan.json").read_text(encoding="utf-8"))
    assert data["counts"]["inconsistent_formula"] >= 1
    assert "## inconsistent_formula" in (tmp_path / "scan.md").read_text(encoding="utf-8")
