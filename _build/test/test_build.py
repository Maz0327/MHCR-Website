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
import build_asset_versions as versions  # noqa: E402
import build_page_checks as checks  # noqa: E402
import build_seo_outputs as seo  # noqa: E402
import build_site_data as site_data  # noqa: E402
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
        self.assertIn(f'<source media="{pics.BREAKPOINT}"', home)
        self.assertNotIn('_readme', home)
        self.assertEqual(home.count("<template data-dial-stop"), 9)
        self.assertIn('src="../images/jobs/wall-1/before-m-800.webp?v=', sub)       # rebased + versioned
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
        self.assertIn("photos:false", self.run_build()[1])

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


    def test_dead_internal_link_fails(self):
        self.page('<a href="nope-not-a-page.html">x</a>')
        self.assertIn("dead internal link", self.run_build()[1])

    def test_wrong_phone_number_fails(self):
        self.page('<p>Call (303) 555-0100</p>')
        self.assertIn("is not site.json phone", self.run_build()[1])
        self.page('<a href="tel:+13035550100">call</a>')
        self.assertIn("tel link", self.run_build()[1])

    def test_every_asset_url_carries_its_content_hash(self):
        rc, err = self.run_build(FIXTURES)
        self.assertEqual(rc, 0, err)
        site_url = site_data.load(os.path.join(BUILD, "data"))["site"]["site_url"]
        n = 0
        for dp, _, fs in os.walk(self.out):
            for fn in fs:
                if fn.endswith(".html"):
                    rel = os.path.relpath(os.path.join(dp, fn), self.out)
                    text = build.read(os.path.join(dp, fn))
                    n += text.count("?v=")
                    self.assertEqual(versions.unversioned(text, rel, build.SITE, site_url, self.out), [], rel)
        self.assertGreater(n, 20)

    def test_sitemap_skips_noindex_and_keeps_unchanged_lastmod(self):
        os.makedirs(self.out)
        pages = {"a.html": "<html>A</html>", "b.html": '<meta name="robots" content="noindex, follow">B'}
        url = lambda p: "https://example.test/" + p
        xml = seo.sitemap(pages, self.out, url, "2026-10-15")
        self.assertIn("<loc>https://example.test/a.html</loc><lastmod>2026-10-15</lastmod>", xml)
        self.assertNotIn("b.html", xml)
        with open(os.path.join(self.out, "sitemap.xml"), "w") as f:
            f.write(xml)
        with open(os.path.join(self.out, "a.html"), "w") as f:
            f.write("<html>A</html>")
        self.assertIn("<lastmod>2026-10-15</lastmod>", seo.sitemap(pages, self.out, url, "2026-12-01"))   # unchanged page
        self.assertIn("<lastmod>2026-12-01</lastmod>", seo.sitemap({"a.html": "<html>A2</html>"}, self.out, url, "2026-12-01"))

    def test_domain_switch_moves_canonical_og_and_sitemap(self):
        data = os.path.join(self.tmp, "data")
        shutil.copytree(os.path.join(BUILD, "data"), data)
        p = os.path.join(data, "site.json")
        s = build.read(p).replace("https://maz0327.github.io/MHCR-Website", "https://www.example-remodels.test")
        with open(p, "w") as f:
            f.write(s)
        ctx = site_data.load(data)
        self.assertEqual(ctx["site"]["site_url"], "https://www.example-remodels.test")
        self.assertEqual(ctx["site_path"], "")
        self.assertIn("https://www.example-remodels.test/sitemap.xml", seo.robots(ctx))
        self.assertTrue(seo.json_ld("business", ctx, {"url": ""}).count("https://www.example-remodels.test/") >= 2)

    def test_form_endpoint_must_be_https(self):
        data = os.path.join(self.tmp, "data")
        shutil.copytree(os.path.join(BUILD, "data"), data)
        p = os.path.join(data, "site.json")
        s = build.read(p).replace('"endpoint": ""', '"endpoint": "http://forms.example.test/x"')
        with open(p, "w") as f:
            f.write(s)
        with self.assertRaises(site_data.DataError):
            site_data.load(data)


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
