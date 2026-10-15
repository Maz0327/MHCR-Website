#!/usr/bin/env python3
"""Every content <img> must sit in a <picture> with a 3:2 desktop <source media srcset> and its own 3:4 srcset,
and every file those reference must exist. Opt-out: data-nopic (logo, canvas film frames, icons). Stdlib only.

  python3 -I _build/qa/qa_pictures.py                # every published .html in the repo
  python3 -I _build/qa/qa_pictures.py page.html ...  # just these
Exit 1 on any problem. Legacy pages fail until Phases 03-06 rebuild them; that is expected.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
SITE = os.path.dirname(BUILD)
sys.path.insert(0, BUILD)
import build_page_checks as checks  # noqa: E402
from tools.make_scrub_inventory import published_files  # noqa: E402


def main(argv):
    files = [os.path.abspath(a) for a in argv] or [f for f in published_files() if f.endswith(".html")]
    total = 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            s = checks.scan(f.read())
        bad = checks.picture_problems(s)
        root = SITE if path.startswith(SITE + os.sep) else os.path.dirname(path)
        here = os.path.dirname(path)
        for tag, attr, url in s.urls:
            if attr in ("src", "srcset", "imagesrcset") and checks.LOCAL.match(url) and not url.startswith("/"):
                if not os.path.exists(os.path.normpath(os.path.join(here, url.split("?")[0]))):
                    bad.append(f"missing file {attr}={url}")
        rel = os.path.relpath(path, root)
        print(f"{'PASS' if not bad else 'FAIL'}  {rel}  ({len(s.imgs)} img)")
        for b in bad[:12]:
            print(f"      - {b}")
        if len(bad) > 12:
            print(f"      ... +{len(bad) - 12} more")
        total += len(bad)
    print(f"qa_pictures: {total} problem(s) in {len(files)} page(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
