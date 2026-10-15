#!/usr/bin/env python3
"""MHCR V3 page QA (adapted 2026-10-15 from the V1 homepage QA). Run: python3 -I qa_v1.py <path-to-page.html>

Needs: python3 playwright + system Google Chrome (already on this Mac; nothing new to install). Read-only on the
site: the page's folder is served by a throwaway local HTTP server on an OS-chosen free port.
Writes screenshots + report.txt into ./out next to this script (git-ignored).
V3 changes: the film is OPTIONAL (only the homepage has it); banned words come from _build/data/banned-words.txt
(allow-list honoured); "consultation links" became quote links: every quote/consultation control must open the
#quote sheet on the same page, every tel: link must be the site phone, and with an empty form endpoint the sheet
must offer call + text instead of a form (never a 405).
"""
import functools, http.server, json, os, re, sys, threading, time, urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE.parent))   # -I drops script dirs; build_page_checks is our own module in _build/
import build_page_checks  # noqa: E402
CLAIMS = build_page_checks.load_claims()
SITE = json.loads((HERE.parent / "data" / "site.json").read_text())
TEL = "tel:" + SITE["phone"]["tel"]
FILM_POS = (0, 33, 66, 100)
SUCCESS_RE = r"thanks?\b|thank you|received|success|got your|we.ll be in touch|all set|on its way|request is in|we.ve got"

# ---------------------------------------------------------------- in-page helpers
JS_HELPERS = r"""
window.__qa = (() => {
  const SKIP = new Set(['SCRIPT','STYLE','NOSCRIPT','TEMPLATE','OPTION','OPTGROUP','HEAD','TITLE','META','LINK','CANVAS']);
  const cs = e => getComputedStyle(e);
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) return s + '#' + el.id;
    const c = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0, 2);
    return c.length ? s + '.' + c.join('.') : s;
  };
  const rendered = el => el.checkVisibility
    ? el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true, opacityProperty: true, visibilityProperty: true})
    : !!(el.offsetWidth || el.offsetHeight);
  // sr-only / clipped / offscreen-hack detection on the element itself
  const tinyOrClipped = (el, strict) => {
    const r = el.getBoundingClientRect(), s = cs(el);
    if ((r.width <= 1 || r.height <= 1) && (strict || s.overflow !== 'visible')) return true;
    if (s.clip && /rect\(\s*(0|1)(px)?[ ,]+(0|1)(px)?[ ,]+(0|1)(px)?[ ,]+(0|1)(px)?\s*\)/.test(s.clip)) return true;
    if (s.clipPath && /inset\(\s*(50|100)%/.test(s.clipPath)) return true;
    if (r.right + scrollX <= 0 || r.bottom + scrollY <= 0) return true;
    return false;
  };
  const hiddenChain = el => {   // aria-hidden or visually hidden at el or any ancestor
    if (tinyOrClipped(el, true)) return true;
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      if (e.getAttribute('aria-hidden') === 'true') return true;
      if (e !== el && tinyOrClipped(e, false)) return true;
    }
    return false;
  };
  let ctx;
  const parse = str => {
    str = (str || '').trim();
    if (str === 'transparent') return {r: 0, g: 0, b: 0, a: 0};
    const m = str.match(/^rgba?\(([^)]+)\)$/);
    if (m) {
      const p = m[1].split(/[,\s/]+/).filter(Boolean).map(t => t.endsWith('%') ? parseFloat(t) / 100 : parseFloat(t));
      return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
    }
    // modern syntaxes (oklch, color(), lab...): resolve through canvas, alpha via black/white backdrops
    ctx = ctx || document.createElement('canvas').getContext('2d', {willReadFrequently: true});
    const px = base => { ctx.fillStyle = base; ctx.fillRect(0, 0, 1, 1); ctx.fillStyle = str; ctx.fillRect(0, 0, 1, 1); return ctx.getImageData(0, 0, 1, 1).data; };
    const a1 = px('#000'), a2 = px('#fff');
    const a = 1 - ((a2[0] - a1[0]) + (a2[1] - a1[1]) + (a2[2] - a1[2])) / 765;
    return a <= 0.001 ? {r: 0, g: 0, b: 0, a: 0} : {r: a1[0] / a, g: a1[1] / a, b: a1[2] / a, a};
  };
  const lin = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = c => 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const over = (f, b) => ({r: f.r * f.a + b.r * (1 - f.a), g: f.g * f.a + b.g * (1 - f.a), b: f.b * f.a + b.b * (1 - f.a), a: 1});
  const bgOf = el => {   // nearest opaque ancestor bg, compositing translucent layers; bg images => unknown
    const layers = []; let unknown = false;
    for (let e = el; e; e = e.parentElement) {
      const s = cs(e);
      if (s.backgroundImage && s.backgroundImage !== 'none') { unknown = true; break; }
      const c = parse(s.backgroundColor);
      if (c.a > 0) layers.push(c);
      if (c.a >= 0.999) break;
    }
    let base = {r: 255, g: 255, b: 255, a: 1};
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return {bg: base, unknown};
  };
  const overMedia = el => {   // is text sitting on top of a canvas/video/img/bg-image sibling layer?
    const sx = scrollX, sy = scrollY;
    el.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'});
    const r = el.getBoundingClientRect();
    const stack = document.elementsFromPoint(Math.min(Math.max(r.left + r.width / 2, 0), innerWidth - 1), Math.min(Math.max(r.top + r.height / 2, 0), innerHeight - 1));
    const i = stack.indexOf(el);
    const rest = (i >= 0 ? stack.slice(i + 1) : stack).filter(e => !e.contains(el));
    window.scrollTo({left: sx, top: sy, behavior: 'instant'});
    return rest.some(e => ['CANVAS', 'VIDEO', 'IMG', 'PICTURE', 'svg'].includes(e.tagName) || (cs(e).backgroundImage || 'none') !== 'none');
  };
  // Scan every visible text-bearing element: font size + contrast
  const scanText = () => {
    const out = [];
    for (const el of document.body.querySelectorAll('*')) {
      if (SKIP.has(el.tagName) || el.closest('svg,canvas,select')) continue;
      const own = [...el.childNodes].filter(n => n.nodeType === 3 && n.nodeValue.trim()).map(n => n.nodeValue.trim()).join(' ');
      if (!own || !rendered(el) || hiddenChain(el)) continue;
      const s = cs(el), size = parseFloat(s.fontSize), weight = parseInt(s.fontWeight) || 400;
      const fg = parse(s.webkitTextFillColor || s.color);
      if (fg.a === 0) continue;
      let op = 1; for (let e = el; e; e = e.parentElement) op *= parseFloat(cs(e).opacity);
      fg.a *= op;
      const {bg, unknown} = bgOf(el);
      const rec = {sel: sel(el), text: own.slice(0, 40), size, large: size >= 24 || (size >= 18.66 && weight >= 700)};
      if (unknown) rec.ratio = null; else rec.ratio = ratio(over(fg, bg), bg);
      rec.unmeasured = unknown;
      out.push(rec);
    }
    return out;
  };
  const overMediaBySel = (selector, text) => {
    for (const el of document.querySelectorAll(selector)) if ((el.textContent || '').includes(text)) return overMedia(el);
    return false;
  };
  return {sel, rendered, hiddenChain, tinyOrClipped, scanText, overMedia, overMediaBySel};
})();
"""


# ---------------------------------------------------------------- tiny static server
def serve(root: Path):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k): pass
    h = functools.partial(Quiet, directory=str(root))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)   # port 0 = OS picks a free port
    assert srv.server_address[1] not in (8765, 8799)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ---------------------------------------------------------------- browser helpers
def route_handler(route):
    """Never let a test submission leave the machine: all writes and cross-origin XHR get a fake 200."""
    req = route.request
    host = urlparse(req.url).hostname
    local = host in ("127.0.0.1", "localhost")
    if req.method != "GET" or (not local and req.resource_type in ("fetch", "xhr", "ping", "other")):
        route.fulfill(status=200, content_type="application/json", body='{"ok":true}')
    else:
        route.continue_()


def new_page(browser, w, h, log=None):
    ctx = browser.new_context(viewport={"width": w, "height": h}, has_touch=w < 800, device_scale_factor=1)
    ctx.add_init_script(JS_HELPERS)
    ctx.route("**/*", route_handler)
    page = ctx.new_page()
    if log is not None:
        page.on("response", lambda r: log.append(f"HTTP {r.status} {r.url[-90:]}") if r.status >= 400 else None)
        page.on("requestfailed", lambda r: log.append(f"FAILED {r.url[-90:]} {r.failure}"))
        page.on("pageerror", lambda e: log.append(f"JS error: {str(e)[:120]}"))
    return page


def settle(page):
    """Load, walk the page once so lazy images / reveal animations fire, return to top."""
    try: page.wait_for_load_state("networkidle", timeout=6000)
    except Exception: pass
    page.evaluate("document.fonts && document.fonts.ready")
    y = 0
    while True:
        h, vh = page.evaluate("[document.documentElement.scrollHeight, innerHeight]")
        if y >= h: break
        page.evaluate("y=>window.scrollTo({top:y,behavior:'instant'})", y)
        page.wait_for_timeout(110)
        y += int(vh * 0.8)
    page.wait_for_timeout(300)
    try: page.wait_for_function("[...document.images].every(i=>i.complete)", timeout=4000)
    except Exception: pass
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.wait_for_timeout(600)


def open_page(browser, url, w, h, log=None):
    page = new_page(browser, w, h, log)
    page.goto(url, wait_until="load")
    settle(page)
    return page


FILM_JS = """() => {
  const f = document.querySelector('#film, .film, [data-film], section[id*="film" i]');
  const doc = document.documentElement.scrollHeight;
  if (!f) return {found: false, top: 0, range: Math.max(1, doc - innerHeight)};
  const r = f.getBoundingClientRect();
  return {found: true, top: r.top + scrollY, range: Math.max(1, f.offsetHeight - innerHeight), h: f.offsetHeight, vh: innerHeight};
}"""


def screenshots(page, tag):
    """Film positions first (scroll-driven), then full page. Returns (files, note)."""
    files = []
    fm = page.evaluate(FILM_JS)
    for p in (FILM_POS if fm["found"] else ()):   # the film is optional: no film = top + full page only
        y = fm["top"] + fm["range"] * p / 100
        page.evaluate("y=>window.scrollTo({top:y,behavior:'instant'})", y)
        page.wait_for_timeout(700)
        f = OUT / f"{tag}-film-{p:03d}.png"
        page.screenshot(path=str(f)); files.append(f)
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.wait_for_timeout(400)
    f = OUT / f"{tag}-full.png"
    page.screenshot(path=str(f), full_page=True); files.append(f)
    if not fm["found"]:
        f = OUT / f"{tag}-top.png"; page.screenshot(path=str(f)); files.append(f)
    note = "no #film on this page (optional)"
    if fm["found"]: note = f"film {fm['h']}px tall vs viewport {fm['vh']}px"
    return files, note


def scan_text_everywhere(page):
    """scanText at top + each film position (beats only exist mid-scroll). Dedupes."""
    fm = page.evaluate(FILM_JS)
    seen, rows = set(), []
    for p in (None,) + (FILM_POS if fm["found"] else ()):
        y = 0 if p is None else fm["top"] + fm["range"] * p / 100
        page.evaluate("y=>window.scrollTo({top:y,behavior:'instant'})", y)
        page.wait_for_timeout(500 if p is not None else 100)
        for r in page.evaluate("window.__qa.scanText()"):
            k = (r["sel"], r["text"])
            if k not in seen:
                seen.add(k); rows.append(r)
    # media check only for low-ratio hits: text over canvas/img is unmeasurable, not a fail
    for r in rows:
        if r["ratio"] is not None and r["ratio"] < 4.5:
            r["over_media"] = page.evaluate("([s,t])=>window.__qa.overMediaBySel(s,t)", [r["sel"], r["text"]])
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    return rows


# ---------------------------------------------------------------- individual checks
def check_overflow(browser, url, widths=(360, 390, 430)):
    bad, notes = [], []
    for w in widths:
        pg = open_page(browser, url, w, 844)
        r = pg.evaluate("""() => {
          const vw = innerWidth, q = window.__qa;
          const doc = document.scrollingElement.scrollWidth, body = document.body.scrollWidth;
          const meta = document.querySelector('meta[name=viewport]');
          const off = [];
          for (const el of document.body.querySelectorAll('*')) {
            const rc = el.getBoundingClientRect();
            if (!rc.width && !rc.height) continue;
            if (rc.right <= vw + 1 || !q.rendered(el)) continue;
            // ignore if an ancestor clips it AND that ancestor itself fits (carousels, marquees)
            let clipped = false;
            for (let a = el.parentElement; a && a !== document.body && a !== document.documentElement; a = a.parentElement) {
              if (getComputedStyle(a).overflowX !== 'visible' && a.getBoundingClientRect().right <= vw + 1) { clipped = true; break; }
            }
            if (!clipped) off.push({el, sel: q.sel(el), right: Math.round(rc.right)});
          }
          const set = new Set(off.map(o => o.el));
          const top = off.filter(o => { for (let a = o.el.parentElement; a; a = a.parentElement) if (set.has(a)) return false; return true; });
          return {vw, doc, body, meta: meta ? meta.content : null,
                  bodyOverflowX: getComputedStyle(document.body).overflowX, htmlOverflowX: getComputedStyle(document.documentElement).overflowX,
                  total: off.length, top: top.slice(0, 8).map(o => `${o.sel} right=${o.right}`)};
        }""")
        pg.context.close()
        if r["doc"] > r["vw"] or r["body"] > r["vw"]: bad.append(f"@{w}: scrollWidth doc={r['doc']} body={r['body']} > {r['vw']}")
        if r["total"]: bad.append(f"@{w}: {r['total']} elements past right edge (body overflow-x={r['bodyOverflowX']}): " + "; ".join(r["top"]))
        if not r["meta"] or "width=device-width" not in r["meta"].replace(" ", ""):
            bad.append(f"@{w}: viewport meta missing/not width=device-width ({r['meta']})")
    return bad


def check_taps(page):
    rows = page.evaluate("""() => {
      const q = window.__qa, out = [];
      for (const el of document.querySelectorAll('a, button, input, select, summary')) {
        if (el.tagName === 'INPUT' && el.type === 'hidden') continue;
        if (!q.rendered(el) || q.tinyOrClipped(el, true) || el.closest('[aria-hidden="true"]')) continue;
        const r = el.getBoundingClientRect();
        if (r.width >= 43.5 && r.height >= 43.5) continue;
        const inline = getComputedStyle(el).display === 'inline' && el.tagName === 'A';
        out.push(`${q.sel(el)} "${(el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim().slice(0, 24)}" ${Math.round(r.width)}x${Math.round(r.height)}${inline ? ' [inline link]' : ''}`);
      }
      return out;
    }""")
    return rows


def check_small_text(rows):
    groups = {}
    for r in rows:
        if r["size"] < 16:
            g = groups.setdefault((r["sel"], r["size"]), [0, r["text"]]); g[0] += 1
    return [f"{s} {sz:g}px x{n} e.g. \"{t}\"" for (s, sz), (n, t) in sorted(groups.items(), key=lambda kv: kv[0][1])]


def check_contrast(rows_by_vp):
    bad, unmeasured = [], {}
    for vp, rows in rows_by_vp.items():
        for r in rows:
            if r.get("unmeasured") or r.get("over_media"):
                unmeasured[r["sel"]] = unmeasured.get(r["sel"], 0) + 1
            elif r["ratio"] is not None and r["ratio"] < 4.5:
                bad.append(f"@{vp} {r['sel']} {r['ratio']:.2f}:1 {r['size']:g}px{' [large]' if r['large'] else ''} \"{r['text']}\"")
    return bad, unmeasured


def check_banned(browser_pages):
    """Visible text and alt/aria/title/meta text, checked with _build/data/banned-words.txt (allow-list honoured)."""
    hits, attr_hits = [], []
    for vp, page in browser_pages.items():
        res = page.evaluate("""() => ({text: document.body.innerText, attrs: [document.title,
            ...[...document.querySelectorAll('meta[name=description],meta[property^="og:"]')].map(m => m.content),
            ...[...document.querySelectorAll('[alt],[aria-label],[title]')].map(e => [e.getAttribute('alt'), e.getAttribute('aria-label'), e.getAttribute('title')].filter(Boolean).join(' '))].join('\\n')})""")
        for key, sink in (("text", hits), ("attrs", attr_hits)):
            t = res[key]
            for _, label, word, at in CLAIMS.hits(t):
                sink.append(f"@{vp} {label}: \"...{' '.join(t[max(0, at - 22):at + len(word) + 22].split())}...\"")
    uniq = lambda xs: list(dict.fromkeys(xs))
    return uniq(hits), uniq(attr_hits)


def check_images(page, base_url, log):
    bad = page.evaluate("""() => [...document.images].filter(i => (i.complete && i.naturalWidth === 0) || !i.complete)
        .map(i => (i.complete ? 'broken ' : 'never finished ') + (i.currentSrc || i.src || '(no src)').slice(-90))""")
    srcs = page.evaluate("[...document.scripts].map(s => s.src ? {src: s.src} : {inline: s.textContent})")
    for s in srcs:
        if "inline" in s: text, label = s["inline"], "inline script"
        else:
            if urlparse(s["src"]).hostname not in ("127.0.0.1", "localhost"): continue
            try: text = urllib.request.urlopen(s["src"], timeout=5).read().decode("utf8", "replace")
            except Exception: continue
            label = "script " + s["src"].rsplit("/", 1)[-1]
        for m in re.finditer(r"new\s+Image\s*\(", text):
            bad.append(f"`new Image(` in {label}: ...{text[max(0, m.start() - 30):m.end() + 40].strip()[:90]!r}")
    return bad


def check_scroll_padding(pages):
    bad = []
    for vp, page in pages.items():
        r = page.evaluate("""() => {
          const out = [], s = getComputedStyle(document.documentElement);
          if (s.scrollPaddingTop !== 'auto') out.push('computed scroll-padding-top=' + s.scrollPaddingTop);
          if (document.documentElement.style.scrollPaddingTop || document.documentElement.style.scrollPadding) out.push('inline style on <html>');
          const walk = rules => { for (const r of rules) {
            if (r.cssRules && !r.selectorText) walk(r.cssRules);
            else if (r.selectorText && /(^|,)\\s*(html|:root)\\s*(,|$)/.test(r.selectorText) && (r.style.scrollPaddingTop || r.style.scrollPadding))
              out.push('rule "' + r.selectorText + '" sets ' + (r.style.scrollPaddingTop || r.style.scrollPadding)); } };
          for (const ss of document.styleSheets) { try { walk(ss.cssRules); } catch (e) {} }
          return out;
        }""")
        bad += [f"@{vp} {x}" for x in r]
    return list(dict.fromkeys(bad))


def check_quote_links(page):
    """Every a/button about a quote or consultation must open the #quote sheet ON THIS PAGE (href="#quote" or
    aria-controls="quote"); clicking the first visible one must show it. Every tel: link must be the site phone,
    and one must be on screen at the top of the page (the header Call button)."""
    items = page.evaluate("""() => {
      const q = window.__qa, out = [];
      document.querySelectorAll('a, button, [role=button], [role=link]').forEach(el => {
        const txt = ((el.textContent || '') + ' ' + (el.getAttribute('aria-label') || '')).replace(/\\s+/g, ' ').trim();
        if (!/\\b(quote|consultation)\\b/i.test(txt) || el.closest('#quote')) return;
        el.setAttribute('data-qa-idx', String(out.length));
        const href = el.getAttribute('href'), rec = {i: out.length, tag: el.tagName, txt: txt.slice(0, 40), href,
          visible: q.rendered(el) && !q.tinyOrClipped(el, true), problem: null};
        if (el.tagName === 'A') {
          const u = href ? new URL(href, location.href) : null;
          if (!u || u.origin !== location.origin || u.pathname !== location.pathname || u.hash !== '#quote') rec.problem = 'href is not #quote on this page: ' + href;
        } else if (el.getAttribute('aria-controls') !== 'quote' && !el.closest('form')) rec.problem = 'button without aria-controls="quote"';
        out.push(rec);
      });
      return {items: out, sheet: !!document.getElementById('quote'),
              tels: [...document.querySelectorAll('a[href^="tel:"]')].map(a => ({href: a.getAttribute('href'),
                top: a.getBoundingClientRect().top < innerHeight && q.rendered(a) && !q.tinyOrClipped(a, true)}))};
    }""")
    bad = []
    if not items["sheet"]: bad.append("no #quote sheet on this page")
    for it in items["items"]:
        if it["problem"]: bad.append(f"{it['tag']} \"{it['txt']}\": {it['problem']}")
    first = next((it for it in items["items"] if it["visible"] and not it["problem"]), None)
    if first and items["sheet"]:
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        try:
            page.locator(f'[data-qa-idx="{first["i"]}"]').click(timeout=3000)
            page.wait_for_timeout(700)
            shown = page.evaluate("""() => { const s = document.getElementById('quote'); const r = s.getBoundingClientRect();
              return (s.tagName !== 'DIALOG' || s.open) && r.bottom > 0 && r.top < innerHeight && window.__qa.rendered(s); }""")
            if not shown: bad.append(f"\"{first['txt']}\": click did not show the #quote sheet")
            page.keyboard.press("Escape"); page.wait_for_timeout(300)
        except Exception as e:
            bad.append(f"\"{first['txt']}\": click failed ({str(e).splitlines()[0][:60]})")
    wrong = sorted({t["href"] for t in items["tels"] if t["href"] != TEL})
    if wrong: bad.append(f"tel: links not {TEL}: {wrong}")
    if not any(t["top"] for t in items["tels"]): bad.append("no tel: link visible at the top of the page")
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    return bad, len(items["items"]), len(items["tels"])


FIND_FORM_JS = """() => {
  const f = document.querySelector('#quote form, #consult-form, form[id*=consult i], form[id*=estimate i], form[id*=contact i]') || document.querySelector('form');
  if (!f) return null;
  f.setAttribute('data-qa-form', '1'); return true;
}"""


def fill_valid(form):
    fields = form.evaluate("""f => [...f.elements].filter(e => !['hidden','submit','button','reset','image','file'].includes(e.type) && e.tagName !== 'FIELDSET' && e.tagName !== 'BUTTON' && !e.disabled && e.checkVisibility())
      .map((e, i) => { e.setAttribute('data-qa-f', i); return {i, tag: e.tagName, type: e.type, key: (e.name + ' ' + e.id + ' ' + (e.autocomplete || '')).toLowerCase(), group: e.name}; })""")
    seen_radio = set()
    for fd in fields:
        loc = form.locator(f'[data-qa-f="{fd["i"]}"]')
        k, t = fd["key"], fd["type"]
        if fd["tag"] == "SELECT":
            val = loc.evaluate("s => (([...s.options].find(o => o.value !== '' && !o.disabled)) || {}).value")
            loc.select_option(value=val)
        elif t == "checkbox": loc.check()
        elif t == "radio":
            if fd["group"] not in seen_radio: seen_radio.add(fd["group"]); loc.check()
        elif t == "tel" or "phone" in k: loc.fill("3035550142")
        elif t == "email" or "email" in k: loc.fill("qa.test@example.com")
        elif re.search(r"zip|postal|location", k): loc.fill("80202")
        elif t == "number": loc.fill("3")
        elif t == "date": loc.fill("2030-01-15")
        elif fd["tag"] == "TEXTAREA": loc.fill("QA test: replace the tub with a walk-in shower.")
        elif "name" in k: loc.fill("QA Tester")
        else: loc.fill("QA test")
    return len(fields)


def form_state(page, form):
    return page.evaluate("""([f, re]) => {
      const q = window.__qa, scope = f.closest('section') || document.body;
      const errs = [...scope.querySelectorAll('[class~=err],[class~=error],[class*=error],[role=alert],[id^="e-"],[id$="-error"],[aria-live=polite],[aria-live=assertive]')]
        .filter(e => e.textContent.trim() && q.rendered(e) && !e.closest('[role=status]')).map(e => e.textContent.trim().slice(0, 40));
      const txt = document.body.innerText, ok = (txt.match(new RegExp(re, 'gi')) || []).length;
      return {url: location.href, marker: window.__qaMarker === 1, errs, invalid: f.querySelectorAll('[aria-invalid=true]').length,
              formVisible: q.rendered(f), okCount: ok, required: f.querySelectorAll('[required]').length};
    }""", [form.element_handle(), SUCCESS_RE])


def open_consult_dialog(pg, form):
    """Form inside a CLOSED <dialog>: open it with the first usable [aria-controls=<dialog id>] / [data-open-consult] control.
    Returns (opened, error): opened=True if it had to open the dialog; error is a string when it could not."""
    info = form.evaluate("f => { const d = f.closest('dialog'); if (!d) return null; d.setAttribute('data-qa-dialog', '1'); return {id: d.id, open: d.open}; }")
    if not info or info["open"]: return False, None
    sel = ", ".join([f'[aria-controls="{info["id"]}"]', f'a[href="#{info["id"]}"]'] * bool(info["id"]) + ["[data-open-consult]"])
    cands = pg.locator(sel)
    for i in range(cands.count()):
        c = cands.nth(i)
        if not c.evaluate("e => e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true})"): continue   # skip hidden / opacity-0 openers
        try:
            c.scroll_into_view_if_needed(timeout=1500); c.click(timeout=2500)
            pg.wait_for_function("document.querySelector('dialog[data-qa-dialog]').open", timeout=2500)
            pg.wait_for_timeout(400)   # open animation
            return True, None
        except Exception: continue
    return False, f'form is in a closed <dialog id="{info["id"]}"> but no visible opener ({sel}) opened it'


def pick_first_project(form):
    """Choose the first project radio. Chip-style radios are often visually hidden, so fall back to clicking the label."""
    r = form.locator("input[type=radio][name=project]")
    first = (r if r.count() else form.locator("input[type=radio]")).first
    try: first.check(timeout=1500)
    except Exception:
        try: first.locator("xpath=ancestor::label[1]").click(timeout=1500)
        except Exception: first.check(force=True, timeout=1500)


def text_fields_visible(form):
    """True once a name/phone/ZIP-style field is on screen (i.e. a multi-step form has reached its details step)."""
    return form.evaluate("f => [...f.elements].some(e => /^(text|tel|email)$/.test(e.type) && e.checkVisibility() && !e.closest('[hidden]'))")


def check_fallback(page):
    """form.endpoint is empty: the #quote sheet must offer call + text (tel:/sms:) and hold no form that could 405."""
    r = page.evaluate("""() => { const s = document.getElementById('quote'); if (!s) return null;
      return {forms: document.querySelectorAll('form').length, tel: !!s.querySelector('a[href^="tel:"]'), sms: !!s.querySelector('a[href^="sms:"]')}; }""")
    if r is None: return ["no #quote sheet on this page"], []
    bad = [m for ok, m in ((r["tel"], "#quote has no tel: link"), (r["sms"], "#quote has no sms: link"),
                           (not r["forms"], f"{r['forms']} <form> on the page while form.endpoint is empty (would 405)")) if not ok]
    return bad, ["form.endpoint is empty: checked the call/text fallback instead of a submit"]


def check_forms(browser, url):
    """Returns (problems, notes). Handles: form in a closed <dialog>, 2-step forms ([data-next]), and the plain single-step form."""
    if not SITE["form"]["endpoint"]:
        pg = open_page(browser, url, 390, 844)
        try: return check_fallback(pg)
        finally: pg.context.close()
    bad, notes, multi, opened = [], [], False, False
    for mode in ("empty", "valid"):
        pg = open_page(browser, url, 390, 844)
        if not pg.evaluate(FIND_FORM_JS): pg.context.close(); return ["no <form> found on page"], notes
        pg.evaluate("window.__qaMarker = 1")
        form = pg.locator('[data-qa-form="1"]')
        opened, err = open_consult_dialog(pg, form)
        if err: bad.append(f"{mode}: {err}"); pg.context.close(); continue
        nxt = form.locator("[data-next][type=button]")
        multi = nxt.count() > 0
        if mode == "empty" and multi:   # step 1 with no project chosen must show an inline error and stay on step 1
            nxt.first.click(); pg.wait_for_timeout(400)
            st = form_state(pg, form)
            if not st["errs"]: bad.append("empty: [data-next] with no project chosen showed no inline error")
            else: notes.append(f"[data-next] with no project -> inline error: {st['errs'][0]!r}")
            if text_fields_visible(form): bad.append("empty: [data-next] advanced to step 2 with no project chosen")
        if multi and not text_fields_visible(form):
            pick_first_project(form); nxt.first.click()
            t0 = time.time()
            while not text_fields_visible(form) and time.time() - t0 < 3: pg.wait_for_timeout(150)
            if not text_fields_visible(form): bad.append(f"{mode}: [data-next] with a project chosen never reached step 2"); pg.context.close(); continue
        before = form_state(pg, form)   # baseline: dialog open, on the step that holds the submit button
        if mode == "valid": fill_valid(form)
        btn = form.locator('[type=submit], button:not([type])').first
        if btn.count(): btn.click()
        else: form.locator("input").first.press("Enter")
        t0 = time.time(); after = None
        while time.time() - t0 < (5 if mode == "valid" else 1.2):
            pg.wait_for_timeout(250)
            after = form_state(pg, form)
            if mode == "valid" and after["okCount"] > before["okCount"]: break
        nav = after["url"].split("#")[0] != before["url"].split("#")[0] or not after["marker"]
        if nav: bad.append(f"{mode}: page navigated away on submit ({after['url'][-60:]})")
        if mode == "empty":
            if after["okCount"] > before["okCount"]: bad.append("empty: success state shown for EMPTY form")
            if not after["errs"]: bad.append(f"empty: no inline error text shown (aria-invalid={after['invalid']}, required={after['required']}; native bubbles aren't inline)")
            else: notes.append(f"empty submit{' at step 2' if multi else ''} -> {len(after['errs'])} inline errors, {after['required']} required fields")
        else:
            if after["okCount"] <= before["okCount"]: bad.append(f"valid: no success state appeared within 5s (errors: {after['errs'][:3]})")
            if after["errs"]: bad.append(f"valid: inline errors still visible: {after['errs'][:3]}")
        pg.context.close()
    if not any('closed <dialog' in b for b in bad): notes.insert(0, f"form flow tested: {'2-step' if multi else 'single-step'}{', opened from a closed <dialog>' if opened else ''}")
    return bad, notes


# ---------------------------------------------------------------- reporting
def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 -I qa_v1.py <path-to-index.html>")
    index = Path(sys.argv[1]).resolve()
    if not index.is_file(): sys.exit(f"not a file: {index}")
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"): old.unlink()
    srv = serve(index.parent)
    url = f"http://127.0.0.1:{srv.server_address[1]}/{index.name}"
    results = []   # (name, status, summary, details)

    def record(name, bad, ok_msg, extra=None):
        results.append((name, "FAIL" if bad else "PASS", f"{len(bad)} issue(s)" if bad else ok_msg, bad + (extra or [])))

    def guarded(name, fn):
        try: fn()
        except Exception as e:
            results.append((name, "FAIL", f"script error: {str(e).splitlines()[0][:80]}", [repr(e)]))
            print(f"   [!] {name}: {e!r}", flush=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        netlog = []
        mob = open_page(browser, url, 390, 844, netlog)
        desk = open_page(browser, url, 1440, 900)
        print(f"serving {index} at {url}", flush=True)

        def shots():
            files = []; notes = []
            for pg, tag in ((mob, "m390"), (desk, "d1440")):
                f, n = screenshots(pg, tag); files += f; notes.append(n)
            small = [f.name for f in files if f.stat().st_size < 3000]
            record("1 Screenshots", [f"suspiciously small: {s}" for s in small], f"{len(files)} files in out/", [notes[0]])
        guarded("1 Screenshots", shots)

        guarded("2 Horizontal overflow 360/390/430", lambda: record("2 Horizontal overflow 360/390/430", check_overflow(browser, url), "none; element rects all within width"))
        guarded("3 Tap targets <44px @390", lambda: (lambda b: record("3 Tap targets <44px @390", b, "all >=44x44"))(check_taps(mob)))

        text_rows = {}
        def texts():
            text_rows["390"] = scan_text_everywhere(mob)
            text_rows["1440"] = scan_text_everywhere(desk)
            record("4 Text <16px @390", check_small_text(text_rows["390"]), f"{len(text_rows['390'])} text nodes all >=16px")
            bad, unm = check_contrast(text_rows)
            ex = [f"unmeasured (bg image/canvas/video behind text, eyeball in screenshots): {', '.join(f'{k} x{v}' for k, v in list(unm.items())[:10])}"] if unm else []
            record("5 Contrast <4.5:1", bad, f"{sum(len(v) for v in text_rows.values())} text nodes ok", ex)
        guarded("4 Text <16px @390", texts)
        if "390" not in text_rows:
            results.append(("5 Contrast <4.5:1", "FAIL", "not run (see 4)", []))

        def banned():
            vis, attrs = check_banned({"390": mob, "1440": desk})
            record("6 Banned words (visible)", vis, "none")
            if attrs: results.append(("6b Banned words (alt/aria/meta)", "FAIL", f"{len(attrs)} hit(s)", attrs))
        guarded("6 Banned words", banned)
        guarded("7 Broken images / new Image(", lambda: record("7 Broken images / new Image(", check_images(mob, url, netlog), f"all images loaded"))
        guarded("8 html scroll-padding-top", lambda: record("8 html scroll-padding-top", check_scroll_padding({"390": mob, "1440": desk}), "not set (computed auto)"))

        def quote():
            bad, n, t = check_quote_links(mob)
            if n == 0: bad = bad + ["no link/button mentioning 'quote' or 'consultation' found (expected CTAs)"]
            record("9a Quote sheet + tel links", bad, f"{n} quote controls open #quote; {t} tel: links all {TEL}")
        guarded("9a Quote sheet + tel links", quote)
        def forms():
            bad, notes = check_forms(browser, url)
            record("9b Form empty + valid submit", bad, "call/text fallback in #quote" if not SITE["form"]["endpoint"] else "inline errors on empty; success state on valid; no navigation", notes)
        guarded("9b Form empty/valid submit", forms)

        net = list(dict.fromkeys(netlog))
        results.append(("10 Network/JS errors (info)", "FAIL" if net else "PASS", f"{len(net)} failed request/JS error(s)" if net else "none", net))
        browser.close()
    srv.shutdown()

    # ---- render
    w = max(len(r[0]) for r in results)
    lines = [f"MHCR V3 QA  {time.strftime('%Y-%m-%d %H:%M:%S')}  {index}", "",
             f"{'CHECK'.ljust(w)}  RESULT  SUMMARY", "-" * (w + 40)]
    for name, status, summ, _ in results: lines.append(f"{name.ljust(w)}  {status:<6}  {summ}")
    nfail = sum(1 for r in results if r[1] == "FAIL")
    lines += ["", f"TOTAL: {len(results) - nfail} pass / {nfail} fail", ""]
    for name, status, _, det in results:
        if not det: continue
        lines.append(f"== {name} [{status}]")
        lines += [f"  - {d}" for d in det[:14]]
        if len(det) > 14: lines.append(f"  ... +{len(det) - 14} more")
        lines.append("")
    lines.append(f"Screenshots: {OUT}")
    text = "\n".join(lines)
    (OUT / "report.txt").write_text(text)
    print(text)
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
