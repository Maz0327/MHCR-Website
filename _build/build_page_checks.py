"""Page checks shared by build.py, qa/qa_pictures.py, qa/qa_claims.sh and tools/make_scrub_inventory.py (stdlib only).

  load_claims()        data/banned-words.txt -> Claims (banned + check patterns, allow phrases)
  Claims.hits(text)    banned/check hits in a string (allowed phrases removed first)
  scan(html)           one parse: ids, <img>s with their <picture> context, local URLs, claim-relevant text
  page_problems(...)   everything build.py fails on, for one rendered page
CLI (raw-line grep, the strictest form: comments, URLs and schema count too):
  python3 -I _build/build_page_checks.py claims FILE...    exit 1 if any BANNED hit
"""
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_ATTRS = {"alt", "title", "aria-label", "aria-description", "placeholder", "content", "value", "label"}
URL_ATTRS = {"href", "src", "srcset", "imagesrcset", "poster", "action", "data-href"}
LOCAL = re.compile(r"^(?![a-z][a-z0-9+.-]*:|//|#)", re.I)       # not a scheme, protocol-relative or bare anchor


class Claims:
    def __init__(self, rows, allow):
        self.rows, self.allow = rows, allow                      # rows: (kind, label, compiled regex)
        self.allow_re = re.compile("|".join(re.escape(a) for a in allow), re.I) if allow else None

    def hits(self, text, kinds=("ban",)):
        """[(kind, label, matched, start)] in text; allowed phrases are blanked first (offsets kept)."""
        if self.allow_re:
            text = self.allow_re.sub(lambda m: " " * len(m.group(0)), text)
        out = []
        for kind, label, rx in self.rows:
            if kind in kinds:
                out += [(kind, label, m.group(0), m.start()) for m in rx.finditer(text)]
        return sorted(out, key=lambda h: h[3])

    def allowed(self, text):
        return [(m.group(0), m.start()) for m in self.allow_re.finditer(text)] if self.allow_re else []


def load_claims(path=None):
    rows, allow = [], []
    with open(path or os.path.join(HERE, "data", "banned-words.txt"), encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            body, _, label = line.partition("## ")
            body = body.strip()
            if body.startswith("allow:"):
                allow.append(body[6:].strip())
                continue
            kind = "check" if body.startswith("check:") else "ban"
            rx = body[6:].strip() if kind == "check" else body
            rows.append((kind, label.strip() or rx, re.compile(rx, re.I)))
    return Claims(rows, allow)


class _Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.imgs, self.urls, self.text = [], [], [], []
        self.stack, self.pictures, self.in_style = [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        for k, v in attrs:
            if k in TEXT_ATTRS and v and not (tag == "meta" and a.get("name") in ("viewport", "theme-color", "robots")):
                self.text.append(v)
            if k in URL_ATTRS and v:
                parts = [p.strip().split()[0] for p in v.split(",") if p.strip()] if k.endswith("srcset") else [v.strip()]
                self.urls += [(tag, k, u) for u in parts if u]
        if tag == "picture":
            self.pictures.append({"media_sources": 0})
        elif tag == "source" and self.pictures and a.get("media") and a.get("srcset"):
            self.pictures[-1]["media_sources"] += 1
        elif tag == "img":
            pic = self.pictures[-1] if self.pictures else None
            self.imgs.append({"src": a.get("src") or a.get("srcset", ""), "nopic": "data-nopic" in a, "picture": pic,
                              "has_srcset": bool(a.get("srcset")), "line": self.getpos()[0]})
        if tag == "style":
            self.in_style += 1
        if tag not in ("img", "source", "br", "hr", "meta", "link", "input", "wbr"):
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "picture" and self.pictures:
            self.pictures.pop()
        if tag == "style" and self.in_style:
            self.in_style -= 1
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if not self.in_style and data.strip():
            self.text.append(data)


def scan(html_text):
    s = _Scan()
    s.feed(html_text)
    s.close()
    return s


def picture_problems(s):
    """Every content <img> needs a <picture> with a 3:2 <source media srcset> and its own 3:4 src/srcset.
    Opt out (logo, film frames drawn on canvas, icons) with data-nopic."""
    out = []
    for im in s.imgs:
        if im["nopic"]:
            continue
        if im["picture"] is None:
            out.append(f"line {im['line']}: <img {im['src'][:60]}> is not in a <picture> (add one, or data-nopic)")
        elif not im["picture"]["media_sources"]:
            out.append(f"line {im['line']}: <picture> for {im['src'][:60]} has no desktop <source media srcset>")
        elif not im["has_srcset"]:
            out.append(f"line {im['line']}: <img {im['src'][:60]}> has no mobile srcset")
    return out


def page_problems(page_path, html_text, claims, exists):
    """All build-stopping problems for one rendered page. exists(site_relative_path) -> bool."""
    s, bad = scan(html_text), []
    dupes = sorted({i for i in s.ids if s.ids.count(i) > 1})
    if dupes:
        bad.append(f"duplicate ids: {dupes}")
    for kind, label, word, _ in claims.hits("\n".join(s.text)):
        bad.append(f"banned claim [{label}]: {word!r}")
    bad += picture_problems(s)
    here = os.path.dirname(page_path)
    ids = set(s.ids)
    for tag, attr, url in s.urls:
        if url.startswith("/") and not url.startswith("//"):
            bad.append(f"root-absolute URL breaks on the github.io subpath: {attr}={url!r}")
        elif url.startswith("#") and attr == "href" and len(url) > 1 and url[1:] not in ids:
            bad.append(f"anchor {url} has no matching id on this page")
        elif LOCAL.match(url) and (attr != "href" or tag == "link"):
            target = os.path.normpath(os.path.join(here, url.split("#")[0].split("?")[0])).replace(os.sep, "/")
            if not exists(target):
                bad.append(f"missing file: {attr}={url!r} -> {target}")
    return bad


def dead_links(page_path, html_text, exists):
    """Local <a href> targets that don't exist (a warning: later phases build some of them)."""
    here, out = os.path.dirname(page_path), []
    for tag, attr, url in scan(html_text).urls:
        if tag == "a" and attr == "href" and LOCAL.match(url) and not url.startswith("/"):
            target = os.path.normpath(os.path.join(here, url.split("#")[0].split("?")[0])).replace(os.sep, "/")
            if target and not exists(target):
                out.append(f"{url} -> {target}")
    return out


def grep_claims(path, claims, kinds=("ban",)):
    """Raw line grep of one file: [(line_no, kind, label, matched, line_text)]."""
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            for kind, label, word, _ in claims.hits(line, kinds):
                out.append((n, kind, label, word, line.rstrip("\r\n")))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "claims":
        sys.exit("usage: python3 -I build_page_checks.py claims FILE...")
    c, total = load_claims(), 0
    for p in sys.argv[2:]:
        for n, _, label, word, _line in grep_claims(p, c):
            print(f"{p}:{n}: [{label}] {word}")
            total += 1
    print(f"qa_claims: {total} banned hit(s) in {len(sys.argv) - 2} file(s)")
    sys.exit(1 if total else 0)
