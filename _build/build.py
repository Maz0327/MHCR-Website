"""Build the MHCR site from _build/ (Python 3 stdlib only). Edit _build/, never the generated HTML.

  python3 _build/build.py                     build every page in _build/pages/ into the repo root
  python3 _build/build.py --out /tmp/preview  build somewhere else (preview / tests); images resolve from the repo
  python3 _build/build.py --pages DIR         use another fragment folder (e.g. _build/test/fixtures/pages)

Page fragments (_build/pages/**/*.html) start with header comments, then the body:
  <!-- path: services/kitchen-remodeling.html -->     required: where the page is written (existing slugs)
  <!-- title: ... -->  <!-- description: ... -->       optional (title defaults to the <h1> + site name)
  <!-- layout: none -->                               optional: the fragment is a whole document (no shell)
Bodies use the template syntax in build_template_engine.py. Write every URL from the site root without a
leading slash ("services.html", "images/jobs/..."); the build adds ../ for pages in subfolders.
Nothing is written unless EVERY page passes: banned claims, duplicate ids, <img> without a mobile + desktop
<picture>, missing files, root-absolute URLs and same-page anchors with no target all stop the build.
Each target keeps its existing line endings (faq.html is CRLF). js-src/*.js is copied to js/.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                  # python3 -I drops the script dir; these are our own modules
import build_page_checks as checks        # noqa: E402
import build_picture_helper as pics       # noqa: E402
import build_site_data as site_data       # noqa: E402
from build_template_engine import Renderer, TemplateError  # noqa: E402

SITE = os.path.dirname(HERE)
HEADER = re.compile(r"\s*<!--\s*(path|title|description|layout):\s*(.*?)\s*-->", re.S)
SKIP_URL = re.compile(r"^(?:#|[a-z][a-z0-9+.-]*:|//|/|\.\./)", re.I)
REBASE_ATTRS = r"href|src|poster|action|data-href"


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def parse_fragment(text, name):
    meta, pos = {}, 0
    while True:
        m = HEADER.match(text, pos)
        if not m:
            break
        meta[m.group(1)], pos = m.group(2), m.end()
    if not re.fullmatch(r"[a-z0-9][a-z0-9/_-]*\.html", meta.get("path", "")) or ".." in meta["path"]:
        raise SystemExit(f"{name}: first line must be <!-- path: folder/name.html --> (got {meta.get('path')!r})")
    return meta, text[pos:].strip("\r\n")


def rebase(h, prefix):
    """Prefix site-root URLs with ../ for pages in subfolders (href, src, srcset/imagesrcset entries...)."""
    if not prefix:
        return h
    one = lambda u: u if SKIP_URL.match(u) else prefix + u
    h = re.sub(rf'(\s(?:{REBASE_ATTRS})=")([^"]*)(")', lambda m: m.group(1) + one(m.group(2)) + m.group(3), h)
    return re.sub(r'(\s(?:srcset|imagesrcset)=")([^"]*)(")', lambda m: m.group(1) + ", ".join(
        " ".join([one(p.strip().split()[0])] + p.strip().split()[1:]) for p in m.group(2).split(",") if p.strip()) + m.group(3), h)


def make_helpers(ctx):
    def pic(ref, *flags, scopes=None, **kw):
        job, frame = site_data.frame(ctx, ref)
        files = pics.frame_files(SITE, job["slug"], frame["name"])
        alt = kw.pop("alt", frame["alt"])
        return pics.picture(files, alt, eager="eager" in flags, **kw)

    def as_json(value, scopes=None):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return {"pic": pic, "json": as_json}


def build(pages_dir, out_dir, quiet=False):
    t0 = time.time()
    ctx = site_data.load(os.path.join(HERE, "data"))
    claims = checks.load_claims()
    partial_dir = os.path.join(HERE, "partials")
    renderer = Renderer(lambda n: read(os.path.join(partial_dir, f"{n}.html")), make_helpers(ctx))
    frags = sorted(glob.glob(os.path.join(pages_dir, "**", "*.html"), recursive=True))
    if not frags:
        print(f"build: no page fragments in {os.path.relpath(pages_dir, SITE)}; nothing to do")
        return 0
    js_out = {f"js/{os.path.basename(p)}": p for p in glob.glob(os.path.join(HERE, "js-src", "*.js"))}
    pages, problems, warnings = {}, {}, []
    metas = [(f, *parse_fragment(read(f), os.path.relpath(f, SITE))) for f in frags]
    paths = [m["path"] for _, m, _ in metas]
    dup = sorted({p for p in paths if paths.count(p) > 1})
    if dup:
        raise SystemExit(f"build: two fragments write the same page: {dup}")
    exists = lambda t: t in pages or t in paths or t in js_out or os.path.exists(os.path.join(out_dir, t)) or os.path.exists(os.path.join(SITE, t))
    for src, meta, body in metas:
        path, name = meta["path"], os.path.relpath(src, SITE)
        prefix = "../" * path.count("/")
        page = {"path": path, "root": prefix, "is_home": path == "index.html", "description": meta.get("description", "")}
        scopes = [ctx, {"page": page}]
        try:
            content = renderer.render(body, scopes, name)
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S)
            page["title"] = meta.get("title") or (
                (html.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip() + " | " if h1 else "") + ctx["site"]["name"])
            out = content if meta.get("layout") == "none" else renderer.render(
                read(os.path.join(partial_dir, "shell.html")), scopes + [{"content": content}], "partials/shell.html")
        except (TemplateError, site_data.DataError, FileNotFoundError) as e:
            problems[path] = [str(e)]
            continue
        out = rebase(out, prefix)
        bad = checks.page_problems(path, out, claims, exists)
        if bad:
            problems[path] = bad
        warnings += [f"{path}: dead link {d}" for d in checks.dead_links(path, out, exists)]
        pages[path] = out
    if problems:
        for path, bad in sorted(problems.items()):
            print(f"FAIL {path}", file=sys.stderr)
            for b in bad[:20]:
                print(f"  - {b}", file=sys.stderr)
        print(f"build: {len(problems)} page(s) failed; nothing written", file=sys.stderr)
        return 1
    for path, text in pages.items():
        write(os.path.join(out_dir, path), text)
    for rel, src in js_out.items():
        os.makedirs(os.path.join(out_dir, "js"), exist_ok=True)
        shutil.copyfile(src, os.path.join(out_dir, rel))
    for w in warnings:
        print(f"WARN {w}")
    if not quiet:
        print(f"build: {len(pages)} page(s) + {len(js_out)} script(s) -> {out_dir} in {time.time() - t0:.2f}s")
    return 0


def write(path, text):
    """Write LF text, or CRLF when the file already there uses CRLF (keeps diffs clean)."""
    crlf = False
    if os.path.exists(path):
        with open(path, "rb") as f:
            crlf = b"\r\n" in f.read()
    text = text.replace("\r\n", "\n")
    if not text.endswith("\n"):
        text += "\n"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n") if crlf else text)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the MHCR site from _build/.")
    ap.add_argument("--out", default=SITE, help="output folder (default: the repo root)")
    ap.add_argument("--pages", default=os.path.join(HERE, "pages"), help="page fragment folder")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    return build(os.path.abspath(a.pages), os.path.abspath(a.out), a.quiet)


if __name__ == "__main__":
    sys.exit(main())
