"""Build system tests (stdlib unittest). Run: python3 -m unittest discover -s _build/test -v"""
import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
sys.path.insert(0, BUILD)
import build  # noqa: E402
import build_page_checks as checks  # noqa: E402
import build_picture_helper as pics  # noqa: E402
from build_template_engine import Renderer, TemplateError  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures", "pages")


class BuildRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pages = os.path.join(self.tmp, "pages")
        self.out = os.path.join(self.tmp, "out")
        os.makedirs(self.pages)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_build(self, pages=None):
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            rc = build.build(pages or self.pages, self.out, quiet=True)
        return rc, err.getvalue()

    def page(self, body, path="t.html"):
        with open(os.path.join(self.pages, path.replace("/", "_")), "w") as f:
            f.write(f"<!-- path: {path} -->\n<main id=\"main\"><h1>T</h1>{body}</main>\n")

    def test_stub_pages_build_clean(self):
        rc, err = self.run_build(FIXTURES)
        self.assertEqual(rc, 0, err)
        home = build.read(os.path.join(self.out, "stub-home.html"))
        sub = build.read(os.path.join(self.out, "services/stub-sub.html"))
        self.assertIn('<source media="(min-width:900px)"', home)
        self.assertEqual(home.count("<template data-dial-stop"), 9)
        self.assertIn('src="../images/jobs/wall-1/before-m-800.webp"', sub)       # rebased for the subfolder
        self.assertIn('href="../stub-home.html#jobs"', sub)
        self.assertTrue(os.path.exists(os.path.join(self.out, "js/dial.js")))
        self.assertNotIn("<\\/", home.split('id="film-data">')[0])

    def test_banned_claim_fails_and_writes_nothing(self):
        self.page("<p>Fully licensed and insured.</p>")
        rc, err = self.run_build()
        self.assertEqual(rc, 1)
        self.assertIn("banned claim", err)
        self.assertFalse(os.path.exists(os.path.join(self.out, "t.html")))

    def test_free_consultation_is_allowed_but_free_estimate_is_not(self):
        self.page("<p>Free consultation.</p>")
        self.assertEqual(self.run_build()[0], 0)
        self.page("<p>Get a free estimate.</p>")
        self.assertIn("free estimate", self.run_build()[1])

    def test_banned_claim_in_alt_text_fails(self):
        self.page('<img data-nopic src="images/logo.png" alt="5-star contractor">')
        self.assertIn("banned claim", self.run_build()[1])

    def test_duplicate_ids_fail(self):
        self.page('<p id="x"></p><p id="x"></p>')
        self.assertIn("duplicate ids", self.run_build()[1])

    def test_img_without_picture_fails(self):
        self.page('<img src="images/logo.png" alt="">')
        self.assertIn("not in a <picture>", self.run_build()[1])

    def test_missing_image_file_fails(self):
        self.page('<img data-nopic src="images/nope.webp" alt="">')
        self.assertIn("missing file", self.run_build()[1])

    def test_held_frame_and_unpublished_job_fail(self):
        self.page("{{pic fireplace-1/process-2}}")
        self.assertIn("on hold", self.run_build()[1])
        self.page("{{pic bathroom-3/after}}")
        self.assertIn("not published", self.run_build()[1])

    def test_root_absolute_url_and_bad_anchor_fail(self):
        self.page('<a href="/about.html">About</a><a href="#nowhere">x</a>')
        _, err = self.run_build()
        self.assertIn("root-absolute", err)
        self.assertIn("#nowhere", err)

    def test_crlf_target_keeps_crlf(self):
        os.makedirs(self.out)
        with open(os.path.join(self.out, "t.html"), "wb") as f:
            f.write(b"old\r\nfile\r\n")
        self.page("<p>ok</p>")
        self.assertEqual(self.run_build()[0], 0)
        with open(os.path.join(self.out, "t.html"), "rb") as f:
            data = f.read()
        self.assertIn(b"\r\n", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))


class Units(unittest.TestCase):
    def test_template_engine(self):
        r = Renderer(lambda n: "<b>{{x}}</b>", {})
        out = r.render("{{#each xs}}{{@n}}:{{.}}{{#unless @last}},{{/unless}}{{/each}}|{{#if no}}A{{else}}B{{/if}}|{{> p}}|{{y}}",
                       [{"xs": ["a", "b"], "no": False, "x": "<i>", "y": "&"}])
        self.assertEqual(out, "1:a,2:b|B|<b>&lt;i&gt;</b>|&amp;")
        with self.assertRaises(TemplateError):
            r.render("{{missing}}", [{}])
        with self.assertRaises(TemplateError):
            r.render("{{#if x}}open", [{"x": 1}])

    def test_webp_size_reader(self):
        site = os.path.dirname(BUILD)
        self.assertEqual(pics.image_size(os.path.join(site, "images/jobs/bathroom-1/after-m-1200.webp")), (1200, 1600))

    def test_claims_raw_grep(self):
        c = checks.load_claims()
        kinds = [h[0] for h in c.hits("Free consultation. Free parking. Since 2009.", ("ban", "check"))]
        self.assertEqual(kinds, ["check", "ban"])


if __name__ == "__main__":
    unittest.main()
