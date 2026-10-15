"""Cache-busting for the MHCR build (stdlib only).

Every local asset URL in generated HTML (img src/srcset, <source srcset>, CSS/JS/font/icon links, og:image) and every
url() inside the generated CSS gets ?v=<first 8 hex of sha1(file bytes)>. Any change to a file changes its URL, so a
returning visitor's cached copy can never be mixed with new code or new crops (the 10-15 film bug).
CSS and JS are generated from _build/css-src and _build/js-src, so their own hashes include the hashed font URLs.
"""
import hashlib
import os
import re

ASSET = re.compile(r"^(?:images|css|js|fonts)/|^favicon\.ico$")
ATTR = re.compile(r'(\s(?:src|href|srcset|imagesrcset|content)=")([^"]*)(")')
CSS_URL = re.compile(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""")
SKIP = re.compile(r"^(?:#|data:|[a-z][a-z0-9+.-]*:|//)", re.I)


def short_hash(data):
    return hashlib.sha1(data).hexdigest()[:8]


class Assets:
    """generated: {site path: bytes} for files the build writes (css/, js/); everything else is read from `site`."""

    def __init__(self, site, generated=None):
        self.site, self.generated, self.cache = site, dict(generated or {}), {}

    def version(self, rel):
        if rel not in self.cache:
            if rel in self.generated:
                data = self.generated[rel]
            else:
                with open(os.path.join(self.site, rel), "rb") as f:   # a missing file raises: the build reports it
                    data = f.read()
            self.cache[rel] = short_hash(data)
        return self.cache[rel]

    def _one(self, url, here, site_url):
        """Return url with ?v= added when it points at a local asset; anything else unchanged."""
        base, _, frag = url.partition("#")
        base = base.split("?")[0]
        if site_url and base.startswith(site_url + "/"):
            rel = base[len(site_url) + 1:]
        elif not base or SKIP.match(base):
            return url
        else:
            rel = os.path.normpath(os.path.join(here, base)).replace(os.sep, "/")
        if not ASSET.match(rel) or rel.startswith("..") or not (rel in self.generated or os.path.isfile(os.path.join(self.site, rel))):
            return url
        return f"{base}?v={self.version(rel)}" + (f"#{frag}" if frag else "")

    def version_html(self, h, page_path, site_url):
        here = os.path.dirname(page_path)

        def attr(m):
            name, val = m.group(1), m.group(2)
            if "srcset" in name:
                parts = [p.strip().split() for p in val.split(",") if p.strip()]
                val = ", ".join(" ".join([self._one(p[0], here, site_url)] + p[1:]) for p in parts)
            else:
                val = self._one(val, here, site_url)
            return name + val + m.group(3)
        return ATTR.sub(attr, h)

    def version_css(self, css, css_path):
        here = os.path.dirname(css_path)
        return CSS_URL.sub(lambda m: f'url("{self._one(m.group(2), here, "")}")', css)


def unversioned(h, page_path, site, site_url, generated_dir=None):
    """Test helper: local asset URLs in h that lack the right ?v= (checked against files in generated_dir or site)."""
    here, bad = os.path.dirname(page_path), []
    for m in ATTR.finditer(h):
        vals = [p.strip().split()[0] for p in m.group(2).split(",") if p.strip()] if "srcset" in m.group(1) else [m.group(2)]
        for u in vals:
            base, _, query = u.partition("#")[0].partition("?")
            if site_url and base.startswith(site_url + "/"):
                rel = base[len(site_url) + 1:]
            elif not base or SKIP.match(base):
                continue
            else:
                rel = os.path.normpath(os.path.join(here, base)).replace(os.sep, "/")
            if not ASSET.match(rel):
                continue
            path = next((os.path.join(d, rel) for d in (generated_dir, site) if d and os.path.isfile(os.path.join(d, rel))), None)
            want = short_hash(open(path, "rb").read()) if path else None
            if query != f"v={want}":
                bad.append(f"{u} (want v={want})")
    return bad
