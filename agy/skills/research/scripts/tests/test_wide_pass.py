"""Unit tests for wide_pass.norm_url (pure string canonicalization; no network).

Run from anywhere:  python -m unittest discover -s <skill>/scripts/tests -v
"""
import importlib.util
import pathlib
import unittest

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "wide_pass.py"
_spec = importlib.util.spec_from_file_location("wide_pass", _SCRIPT)
wide_pass = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wide_pass)
norm_url = wide_pass.norm_url


class NormUrlGeneric(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(norm_url(""), "")
        self.assertEqual(norm_url(None), "")

    def test_scheme_www_query_fragment_trailing_slash(self):
        self.assertEqual(norm_url("https://www.Example.com/Path/?utm_source=x#top"),
                         "example.com/path")


class NormUrlDoi(unittest.TestCase):
    CANON = "doi.org/10.1234/abc.def"

    def test_doi_variants_collapse(self):
        for u in ["https://doi.org/10.1234/ABC.def",
                  "http://dx.doi.org/10.1234/abc.DEF",
                  "https://www.doi.org/10.1234/abc.def/",
                  "doi:10.1234/abc.def",
                  "DOI: 10.1234/ABC.DEF",
                  "10.1234/abc.def"]:
            with self.subTest(u=u):
                self.assertEqual(norm_url(u), self.CANON)

    def test_arxiv_doi_collapses_to_arxiv_id(self):
        self.assertEqual(norm_url("https://doi.org/10.48550/arXiv.2101.00001"),
                         "arxiv.org/abs/2101.00001")


class NormUrlArxiv(unittest.TestCase):
    CANON = "arxiv.org/abs/2101.00001"

    def test_abs_pdf_version_variants_collapse(self):
        for u in ["https://arxiv.org/abs/2101.00001",
                  "https://arxiv.org/abs/2101.00001v2",
                  "http://arxiv.org/pdf/2101.00001v3",
                  "https://arxiv.org/pdf/2101.00001.pdf",
                  "https://arxiv.org/pdf/2101.00001v1.pdf",
                  "https://export.arxiv.org/abs/2101.00001v4",
                  "https://www.arxiv.org/abs/2101.00001?context=cs"]:
            with self.subTest(u=u):
                self.assertEqual(norm_url(u), self.CANON)

    def test_old_style_id(self):
        self.assertEqual(norm_url("https://arxiv.org/pdf/hep-th/9901001v2"),
                         "arxiv.org/abs/hep-th/9901001")

    def test_non_paper_arxiv_page_untouched(self):
        self.assertEqual(norm_url("https://arxiv.org/list/cs.AI/recent"),
                         "arxiv.org/list/cs.ai/recent")


if __name__ == "__main__":
    unittest.main()
