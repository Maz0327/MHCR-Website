"""SEO outputs for the MHCR build (stdlib only): JSON-LD blocks, sitemap.xml and robots.txt.

All absolute URLs come from site.json `site_url` (one value; switch it when the domain is decided).
  json_ld(kind, ctx, scope)   <script type="application/ld+json"> for "business" | "service" | "faq"
  sitemap(pages, out_dir, url_of, today)  indexable pages only, <loc> + a real <lastmod> (kept unless the page changed)
  robots(ctx)                 allow all crawlers (AI crawlers included) + the sitemap line
Rules (Maz, 2026-10-15): HomeAndConstructionBusiness with areaServed; no ratings, reviews, hours or 24/7 claims.
"""
import html
import json
import os
import re
import xml.etree.ElementTree as ET

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def _plain(h):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", h)).split())


def business(ctx):
    s = ctx["site"]
    return {"@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "@id": f"{s['site_url']}/#business",
            "name": s["name"], "url": f"{s['site_url']}/", "telephone": s["phone"]["tel"],
            "logo": f"{s['site_url']}/images/brand/mhcr-logo-mark-orange.png",
            "areaServed": [{"@type": "City", "name": f"{c['name']}, CO"} for c in s["cities"]],
            "knowsAbout": [x["h1"] for x in ctx["services"]]}


def json_ld(kind, ctx, page, item=None):
    s = ctx["site"]
    if kind == "business":
        data = business(ctx)
    elif kind == "service":
        data = {"@context": "https://schema.org", "@type": "Service", "name": item["h1"], "serviceType": item["h1"],
                "description": item["intro"], "url": page["url"], "provider": {"@id": f"{s['site_url']}/#business"},
                "areaServed": business(ctx)["areaServed"]}
    elif kind == "faq":
        data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": _plain(q["a"])}}
            for g in ctx["faq"]["groups"] for q in g["items"]]}
    else:
        raise ValueError(f"unknown JSON-LD kind {kind!r}")
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{body}</script>'


def sitemap(pages, out_dir, url_of, today):
    """pages: {path: html}. Keeps a page's old <lastmod> when its HTML is unchanged on disk; else today."""
    old, path = {}, os.path.join(out_dir, "sitemap.xml")
    if os.path.exists(path):
        try:
            for u in ET.parse(path).getroot().iter(f"{NS}url"):
                old[u.findtext(f"{NS}loc")] = u.findtext(f"{NS}lastmod")
        except ET.ParseError:
            pass
    rows = []
    for p, text in sorted(pages.items()):
        if re.search(r'<meta name="robots" content="[^"]*noindex', text):
            continue
        loc, target = url_of(p), os.path.join(out_dir, p)
        same = False
        if os.path.exists(target):
            with open(target, encoding="utf-8", newline="") as f:
                same = f.read().replace("\r\n", "\n").rstrip("\n") == text.replace("\r\n", "\n").rstrip("\n")
        rows.append((loc, old.get(loc) if same and old.get(loc) else today))
    body = "".join(f"  <url><loc>{html.escape(l)}</loc><lastmod>{d}</lastmod></url>\n" for l, d in rows)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def robots(ctx):
    return ("# Every crawler, AI crawlers included, may read the whole site.\n"
            "# Note: robots.txt only takes effect at a domain root, not on a github.io project subpath.\n"
            f"User-agent: *\nAllow: /\n\nSitemap: {ctx['site']['site_url']}/sitemap.xml\n")
