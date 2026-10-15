#!/usr/bin/env python3
"""List every file GitHub Pages will publish (Jekyll rules + _config.yml exclude) and prove each asset is used.

  python3 -I _build/qa/qa_published.py [--all]      exit 1 if a published image/css/js/font file has no page using it
Prints each published file under images/ (or every published file with --all) with how many pages reference it.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
SITE = os.path.dirname(BUILD)
sys.path.insert(0, BUILD)
import build_publish_list as publish  # noqa: E402
import json  # noqa: E402


def main(argv):
    with open(os.path.join(SITE, "_config.yml"), encoding="utf-8") as f:
        exclude = re.findall(r"^\s+-\s+(.+?)\s*$", f.read(), re.M)
    files = publish.published(publish.repo_files(SITE), exclude)
    pages = {p: open(os.path.join(SITE, p), encoding="utf-8", errors="replace").read() for p in files if p.endswith(".html")}
    site_url = json.load(open(os.path.join(BUILD, "data", "site.json")))["site_url"]
    refs = publish.referenced(pages, site_url, SITE)
    bad = publish.unreferenced_assets(files, refs)
    show = files if "--all" in argv else [p for p in files if p.startswith("images/")]
    for p in show:
        n = len(refs.get(p, ()))
        print(f"{'OK ' if n or not p.startswith(publish.ASSET_DIRS) else 'BAD'}  {n:3d} page(s)  {p}")
    print(f"qa_published: {len(files)} files published ({len(pages)} pages, "
          f"{sum(p.startswith('images/') for p in files)} images); {len(bad)} unreferenced asset(s)")
    for b in bad:
        print("  UNREFERENCED:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
