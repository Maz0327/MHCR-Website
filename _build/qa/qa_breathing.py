#!/usr/bin/env python3
"""MHCR breathing-room QA: the owner-approved spec (2026-10-14) as automatic checks.

Run:  python3 -I qa_breathing.py <index.html> [more pages...] [--shots] [--skip-footer]
Spec: ~/plans/reports/researcher-261014-1832-mhcr-owner-references-and-award-sites.md  section 7.
Reuses the throwaway local server, request guard and page-settle helpers from qa_v1.py. Read-only on the site.

How it works: one JS pass at 390x844 (DPR 3, mobile emulation) records every text block, photo, list, rail and
section in DOCUMENT coordinates. Python cuts the page into 844px screens starting right after the film (or at the
top when the page has no film) and scores each screen. Fixed/sticky bars are the one thing sampled live, by
scrolling to each screen and reading what is actually painted there.

Opt-out for a deliberate exception: put data-br-exempt on the element (its text/photos are ignored).
"""
import argparse, math, os, sys, time
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # -I drops the script dir from sys.path; qa_v1.py is our sibling
import qa_v1                           # noqa: E402  (serve, route_handler, settle)
from playwright.sync_api import sync_playwright  # noqa: E402

# ------------------------------------------------------------------ SPEC + TOLERANCES (edit here)
W, H, DPR = 390, 844, 3
GUTTER_MIN = 24          # text side gutter, px (>=)
PHOTO_INSET = 24         # photo inset both sides, px; or 0 = full-bleed
INSET_TOL = 2            # +- px on photo insets / full-bleed (spec: exactly 24, +-2)
TOL = 1                  # px slack on every >= / <= px rule (sub-pixel rounding)
TEXT_MAX_W = 300         # multi-line body text, widest line, px
STATEMENT_MAX_W = 330    # multi-line text at font-size >= STATEMENT_FS
STATEMENT_FS = 24
MAX_LINES = 4            # per text block
SECTION_GAP_MIN = 112    # between consecutive sections' content, px
HEAD_GAP_MIN = 28        # heading bottom -> next content top, px
MAX_ELEMS, MAX_TEXTS, MAX_BTNS = 6, 4, 1   # per screen; mono labels exempt
PHOTO_MIN, EMPTY_MIN = 0.40, 0.60          # screen must be picture-led OR air-led
BARS_MAX = 64            # fixed + sticky chrome total, px (top + bottom)
ANCHOR = 24              # a fixed bar within this many px of an edge counts as anchored to it
LIST_MAX_ITEMS = 6       # vertical list on the homepage; items one line each; one list per screen
GRID_MIN_TILE = 150      # owner exception: a 2-column photo grid is allowed on phones if every tile is >= this wide,
GRID_MIN_GAP = 16        #   the column gap is >= this, the outer gutters are PHOTO_INSET (+-INSET_TOL),
GRID_MAX_TILES = 4       #   and the screen holds at most this many tiles (one 2x2). Tile width + column gap use the <img> box.
#   Gutters (and single-photo insets) are measured on the OUTER edge of the mat/frame around the photo, if there is one.
GRID_CAPTION_MAX_LINES = 2  # a legal grid counts as ONE element; captions (non-mono text in a tile's cell) are absorbed
                            #   into it only if each tile's caption is <= this many lines, else they count as text blocks
RAIL_W = (0.80, 0.84)    # photo-card rail: card width share of viewport
RAIL_W_TOL = 0.02
PEEK_MIN = 24            # next rail card must show >= this many px
MONO_LABEL_MAX_FS = 15   # mono text at or below this size is a "label", not a text block
LIST_AS_ONE_BLOCK = True # a text-only list counts as ONE text block (else a 6-item list can never fit the <=4 rule)
SLIVER = 0.25           # a last screen with less than this share of a viewport left is just padding: not scored
MIN_PHOTO_PX = 60        # smaller images (logos, icons) are not photos
BAR_WAIT_MS = 700        # let bars finish their slide-in after each scroll
EXEMPT = "[data-br-exempt]"

OUT = qa_v1.OUT
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
RULES = [("G", "text gutters"), ("P", "photos"), ("T", "text block size"), ("S", "section gap"), ("H", "heading gap"),
         ("E", "elements/screen"), ("D", "photo-led or air-led"), ("B", "fixed bars"), ("L", "homepage lists")]

# ------------------------------------------------------------------ in-page: whole-document layout model
MODEL_JS = r"""(A) => {
 const W = innerWidth, H = innerHeight, SY = scrollY;
 const ids = new WeakMap(); let n = 0; const id = e => { if (!ids.has(e)) ids.set(e, ++n); return ids.get(e); };
 const cs = e => getComputedStyle(e);
 const ok = e => e.checkVisibility ? e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true, opacityProperty: true, visibilityProperty: true}) : !!(e.offsetWidth || e.offsetHeight);
 const sel = e => { let s = e.tagName.toLowerCase(); if (e.id) return s + '#' + e.id; const c = (e.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0, 2); return c.length ? s + '.' + c.join('.') : s; };
 const fixedAnc = e => { for (let a = e; a && a !== document.body; a = a.parentElement) if (cs(a).position === 'fixed' && a.getBoundingClientRect().height < H * 0.6) return true; return false; };
 const exempt = e => A.exempt && !!e.closest(A.exempt);
 const xScroller = e => { for (let a = e.parentElement; a && a !== document.body && a !== document.documentElement; a = a.parentElement) { const o = cs(a).overflowX; if ((o === 'auto' || o === 'scroll') && a.scrollWidth > a.clientWidth + 4) return a; } return null; };
 const rows = (rr, fs) => { const ts = rr.map(r => r.top).sort((x, y) => x - y); let k = 0, last = -1e9; for (const t of ts) if (t - last > fs * 0.5) { k++; last = t; } return Math.max(1, k); };
 const uni = rr => rr.reduce((m, r) => ({l: Math.min(m.l, r.left), t: Math.min(m.t, r.top), r: Math.max(m.r, r.right), b: Math.max(m.b, r.bottom)}), {l: 1e9, t: 1e9, r: -1e9, b: -1e9});
 const onX = r => r.width > 1 && r.height > 1 && r.left < W && r.right > 0;
 const isBtn = ctl => { if (ctl.classList.contains('btn-text') || ctl.querySelector('img,picture,video')) return false; if (ctl.classList.contains('btn')) return true;
   if (ctl.closest('li')) return false; const s = cs(ctl), r = ctl.getBoundingClientRect(); if (r.height > 72 || r.width < 80) return false;
   const m = (s.backgroundColor.match(/[\d.]+/g) || []); const al = s.backgroundColor === 'transparent' ? 0 : (m.length > 3 ? +m[3] : 1);
   return al > 0.05 || parseFloat(s.borderTopWidth) > 0; };
 // ---- text blocks: nearest block-level ancestor of each text node (same grouping logic as breathing-room-measure-390.py)
 const BLOCK = /^(block|flex|grid|list-item|table-cell|flow-root)$/, blocks = new Map();
 const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
 while (tw.nextNode()) { const nd = tw.currentNode; if (nd.textContent.trim().length < 2) continue; let a = nd.parentElement;
   if (!a || /^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|OPTION|TEXTAREA)$/.test(a.tagName)) continue;
   while (a && a !== document.body && !BLOCK.test(cs(a).display)) a = a.parentElement;
   for (let k = 0; k < 3 && a && /^(SPAN|DIV)$/.test(a.tagName); k++) { const pa = a.parentElement; if (!pa || pa === document.body) break;
     if (cs(pa).fontSize !== cs(a).fontSize || pa.children.length < 2 || (pa.innerText || '').length > 700 || pa.querySelector('img,picture,video,canvas,ul,ol,section,article,h1,h2,h3,h4,h5,h6')) break; a = pa; }
   if (!a || a === document.body) continue; const rg = document.createRange(); rg.selectNodeContents(nd);
   const rr = [...rg.getClientRects()].filter(onX); if (!rr.length) continue; if (!blocks.has(a)) blocks.set(a, []); blocks.get(a).push(...rr); }
 const texts = [];
 for (const [b, rr] of blocks) { if (!ok(b) || fixedAnc(b) || exempt(b)) continue; const c = cs(b), fs = parseFloat(c.fontSize), u = uni(rr);
   const ctl = b.closest('button,a,[role=button]'), li = b.closest('li'), rail = xScroller(b);
   const mono = /mono|courier|consol/i.test(c.fontFamily) && fs <= A.monoFs;
   let kind = 'text', grp = id(b);
   if (ctl && isBtn(ctl)) { kind = 'btn'; grp = id(ctl); }
   else if (mono) kind = 'mono';
   else if (li && li.parentElement && /^(UL|OL)$/.test(li.parentElement.tagName)) { const list = li.parentElement; grp = list.querySelector('img,picture,video,canvas') ? id(li) : id(list); }
   texts.push({kind, grp, rail: !!rail, l: u.l, r: u.r, t: u.t + SY, b: u.b + SY, fs, lines: rows(rr, fs), head: /^H[1-6]$/.test(b.tagName) || fs >= 24,
     sel: sel(b), s: (b.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 38), e: b, rects: rr.map(r => [r.left, r.top + SY, r.right, r.bottom + SY]) }); }
 // ---- photos: img / video / canvas / background-image on text-free boxes
 const media = [], add = (m, r) => { const c = cs(m); if (!ok(m) || fixedAnc(m) || exempt(m) || r.width < MIN || r.height < MIN || r.right <= 0 || r.left >= W) return;
   media.push({e: m, sel: sel(m), l: r.left, r: r.right, t: r.top + SY, b: r.bottom + SY, w: r.width, h: r.height, rail: !!xScroller(m)}); };
 const MIN = A.minPhoto;
 for (const m of document.querySelectorAll('img,video,canvas')) add(m, m.getBoundingClientRect());
 for (const m of document.querySelectorAll('body *')) { if (/^(IMG|VIDEO|CANVAS|SCRIPT|STYLE)$/.test(m.tagName)) continue; const bi = cs(m).backgroundImage;
   if (bi && bi.includes('url(') && !(m.innerText || '').trim()) add(m, m.getBoundingClientRect()); }
 // ---- mat = outermost styled single-child wrapper around a photo (padding/background/border frame), narrower than the screen
 const matOf = img => { let best = null, a = img;
   // <picture> = <source>s + <img> (2+ children by design): step through it without the one-child test. Only the <img>
   // is ever measured as the photo (<source> has no box); the mat is the first styled single-child wrapper above the picture.
   for (let k = 0; k < 5; k++) { const p = a.parentElement; if (!p || /^(LI|UL|OL|SECTION|MAIN|ARTICLE|BODY|NAV|HEADER|FOOTER)$/.test(p.tagName)) break;
     if (p.tagName === 'PICTURE') { a = p; continue; }
     if (p.children.length !== 1) break;
     if ([...p.childNodes].some(c => c.nodeType === 3 && c.textContent.trim())) break; a = p; const s = cs(p), r = p.getBoundingClientRect();
     const m = (s.backgroundColor.match(/[\d.]+/g) || []), al = s.backgroundColor === 'transparent' ? 0 : (m.length > 3 ? +m[3] : 1);
     const styled = al > 0.05 || (s.backgroundImage && s.backgroundImage !== 'none') || parseFloat(s.borderTopWidth) > 0 || (s.boxShadow && s.boxShadow !== 'none');
     if (styled && r.width < W - 2) best = {l: r.left, r: r.right, t: r.top + SY, b: r.bottom + SY}; }
   return best; };
 for (const m of media) m.mat = matOf(m.e);
 // ---- cell = largest ancestor holding only this one photo (its tile: photo + caption). Text blocks inside a cell get that cell id.
 const cells = new Map();
 for (const m of media) { let a = m.e; while (a.parentElement && a.parentElement !== document.body && media.filter(o => a.parentElement.contains(o.e)).length === 1) a = a.parentElement; m.cell = id(a); cells.set(a, m.cell); }
 for (const t of texts) { t.cell = 0; for (const [el, cid] of cells) if (el.contains(t.e)) { t.cell = cid; break; } }
 // ---- lists (vertical lists only matter; rails and one-row lists are skipped later)
 const lists = [];
 for (const ul of document.querySelectorAll('ul,ol,[role=list]')) { if (!ok(ul) || fixedAnc(ul) || exempt(ul)) continue;
   const lis = [...ul.children].filter(li => li.tagName === 'LI' && ok(li) && li.getBoundingClientRect().height > 0); if (!lis.length) continue;
   const r = ul.getBoundingClientRect(), media = !!ul.querySelector('img,picture,video,canvas');
   const items = lis.map(li => { const q = document.createTreeWalker(li, NodeFilter.SHOW_TEXT), rr = []; while (q.nextNode()) { const nd = q.currentNode;
       if (nd.textContent.trim().length < 2 || !nd.parentElement || !ok(nd.parentElement)) continue; const g = document.createRange(); g.selectNodeContents(nd); rr.push(...[...g.getClientRects()].filter(onX)); }
     const lr = li.getBoundingClientRect(); return {t: lr.top + SY, b: lr.bottom + SY, lines: rr.length ? rows(rr, parseFloat(cs(li).fontSize)) : 0, s: (li.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 30)}; });
   const tops = items.map(i => Math.round(i.t)); lists.push({sel: sel(ul), n: lis.length, t: r.top + SY, b: r.bottom + SY, media, rail: !!xScroller(ul) || cs(ul).overflowX === 'auto' || cs(ul).overflowX === 'scroll',
     oneRow: lis.length > 1 && Math.max(...tops) - Math.min(...tops) < 6, inNav: !!ul.closest('nav[aria-label*=readcrumb]'), items}); }
 // ---- photo-card rails (horizontal scrollers that hold photos)
 const rails = [];
 for (const s of document.querySelectorAll('body *')) { if (s === document.documentElement || s === document.body) continue; const o = cs(s).overflowX;
   if (!(o === 'auto' || o === 'scroll') || s.scrollWidth <= s.clientWidth + 4 || !ok(s) || fixedAnc(s) || exempt(s) || !s.querySelector('img,picture,video')) continue;
   const kids = [...s.children].filter(k => ok(k)).slice(0, 3).map(k => { const r = k.getBoundingClientRect(); return {l: r.left, r: r.right, w: r.width}; }); const r = s.getBoundingClientRect();
   rails.push({sel: sel(s), t: r.top + SY, b: r.bottom + SY, scrollLeft: s.scrollLeft, kids}); }
 // ---- sections = children of <main> + footer; content extent = union of the text/photos inside
 const secs = [...document.querySelectorAll('main > *, footer')].filter(s => ok(s) && s.getBoundingClientRect().height > 8).map(s => { const r = s.getBoundingClientRect();
   let ct = 1e9, cb = -1e9; for (const t of texts) if (s.contains(t.e)) { ct = Math.min(ct, t.t); cb = Math.max(cb, t.b); }
   for (const m of media) if (s.contains(m.e)) { ct = Math.min(ct, m.t); cb = Math.max(cb, m.b); }
   const hd = s.querySelector('h1,h2,h3'); return {sel: sel(s), id: s.id || (hd ? hd.innerText.trim().slice(0, 16) : ''), foot: s.tagName === 'FOOTER', t: r.top + SY, b: r.bottom + SY, ct, cb}; });
 const film = document.querySelector('#film, .film, [data-film]'); const fr = film && film.getBoundingClientRect();
 const fonts = document.fonts ? [...document.fonts].filter(f => f.status === 'loaded').length : -1;
 return {innerW: W, innerH: H, docH: document.documentElement.scrollHeight, start: film ? fr.bottom + SY : 0, hasFilm: !!film, fonts,
   extFonts: [...document.querySelectorAll('link[href*="fonts.googleapis"]')].length,
   texts: texts.map(({e, ...t}) => t), media: media.map(({e, ...m}) => m), lists, rails, secs}; }"""

# ------------------------------------------------------------------ in-page: fixed / sticky chrome painted at the current scroll
BARS_JS = r"""() => { const H = innerHeight, out = [];
 for (const e of document.querySelectorAll('body *')) { const s = getComputedStyle(e); if (s.position !== 'fixed' && s.position !== 'sticky') continue;
   const ok = e.checkVisibility ? e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true, opacityProperty: true, visibilityProperty: true}) : true;
   const r = e.getBoundingClientRect(); if (!ok || r.height < 8 || r.width < 8 || r.height >= H * 0.6 || s.pointerEvents === 'none' || e.getAttribute('aria-hidden') === 'true') continue;
   if (r.bottom <= 0 || r.top >= H) continue;
   const nm = e.tagName.toLowerCase() + (e.id ? '#' + e.id : (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : ''));
   out.push({sel: nm, pos: s.position, t: r.top, b: r.bottom, l: r.left, r: r.right}); }
 return out; }"""


# ------------------------------------------------------------------ analysis helpers
def raster(rects, y0, hh, nx):
    """Cells (6px grid) of the screen window covered by any rect (document coords)."""
    cells = set()
    for l, t, r, b in rects:
        t -= y0; b -= y0
        if b <= 0 or t >= hh: continue
        for iy in range(max(0, math.ceil((t - 3) / 6)), min(math.ceil(hh / 6) - 1, math.floor((b - 3) / 6)) + 1):
            for ix in range(max(0, math.ceil((l - 3) / 6)), min(nx - 1, math.floor((r - 3) / 6)) + 1):
                cells.add(iy * nx + ix)
    return cells


def chrome_total(bars):
    """Top chrome = lowest bottom edge of top-anchored bars; bottom chrome = highest top edge of bottom-anchored bars."""
    top = bot = 0.0; floating = 0.0; bottom_bars = []
    for b in bars:
        if b["t"] <= ANCHOR: top = max(top, b["b"])
        elif b["b"] >= H - ANCHOR:
            bot = max(bot, H - b["t"])
            if b["r"] - b["l"] >= W * 0.5: bottom_bars.append(b)
        else: floating += b["b"] - b["t"]
    return round(top + bot + floating), round(top), round(bot), bottom_bars


def groups_of(texts):
    """Text blocks -> counted elements. Buttons = one per control; text-only lists = one per list (see LIST_AS_ONE_BLOCK)."""
    seen = {}
    for t in texts:
        key = (t["kind"] == "btn", t["grp"]) if (LIST_AS_ONE_BLOCK or t["kind"] == "btn") else (False, id(t))
        g = seen.setdefault(key, {"kind": t["kind"], "t": t["t"], "b": t["b"], "n": 0})
        g["t"] = min(g["t"], t["t"]); g["b"] = max(g["b"], t["b"]); g["n"] += 1
        if t["kind"] == "text": g["kind"] = "text"
    return list(seen.values())


def score_page(model, bars_at, is_home, skip_footer):
    tx, md = model["texts"], model["media"]
    start, docH = model["start"], model["docH"]
    foot_top = next((s["t"] for s in model["secs"] if s["foot"]), docH)
    ys, y = [], start
    while y < docH - SLIVER * H:
        if skip_footer and y >= foot_top - 1: break
        ys.append(y); y += H
    nx = math.ceil(W / 6)
    screens = []
    for si, y0 in enumerate(ys):
        y1 = y0 + H; hh = min(H, docH - y0); R = {k: ("PASS", []) for k, _ in RULES}; M = {}
        fail = lambda k, msg: R.__setitem__(k, ("FAIL", R[k][1] + [msg]))
        mid = lambda o: (o["t"] + o["b"]) / 2
        inwin = lambda o: y0 <= mid(o) < y1
        t_in = [t for t in tx if inwin(t) and not (t["rail"] and t["l"] >= W)]
        names = []
        for s in model["secs"]:
            if s["t"] < y1 and s["b"] > y0 and (s["id"] or s["sel"]) not in names: names.append(s["id"] or s["sel"])
        # G: text side gutters
        tight = []
        for t in t_in:
            if t["rail"]: continue   # rail cards run off the right edge by design; rule P checks where the first card starts
            lg, rg = t["l"], W - t["r"]
            if lg < GUTTER_MIN - TOL or rg < GUTTER_MIN - TOL: tight.append((min(lg, rg), t))
        if tight:
            m, t = min(tight, key=lambda q: q[0])
            fail("G", f'{len(tight)} of {len(t_in)} text blocks have a side gutter under {GUTTER_MIN}px; tightest {m:.0f}px on "{t["s"]}"')
        M["gut"] = min([round(t["l"]) for t in t_in] + [round(W - t["r"]) for t in t_in if not t["rail"]] or [0])
        # T: text block width and lines (paragraphs: multi-line; statements get a wider limit)
        for t in t_in:
            if t["kind"] == "mono": continue
            w = t["r"] - t["l"]; lim = STATEMENT_MAX_W if t["fs"] >= STATEMENT_FS else TEXT_MAX_W
            if t["lines"] >= 2 and w > lim + TOL: fail("T", f'{w:.0f}px wide (max {lim}) "{t["s"]}"')
            if t["lines"] > MAX_LINES: fail("T", f'{t["lines"]} lines (max {MAX_LINES}) "{t["s"]}"')
        # P: photos (full-bleed or 24px inset, one per row, rails sized 80-84% with a peek)
        ph = sorted([m for m in md if inwin(m) and not m["rail"]], key=lambda m: (m["t"], m["l"]))
        prow = []   # photos that share a row (vertical overlap >= half the shorter one)
        for m in ph:
            for r in prow:
                if any(min(m["b"], o["b"]) - max(m["t"], o["t"]) >= 0.5 * min(m["h"], o["h"]) for o in r): r.append(m); break
            else: prow.append([m])
        grid_tiles = 0; grid_ok = []   # grid_ok = tiles of legal 2-column rows
        edge = lambda m: (m["mat"]["l"], W - m["mat"]["r"]) if m.get("mat") else (m["l"], W - m["r"])
        for r in prow:
            r.sort(key=lambda m: m["l"])
            if len(r) == 1:
                m = r[0]; li, ri = edge(m)
                bleed = li <= INSET_TOL and ri <= INSET_TOL
                inset = abs(li - PHOTO_INSET) <= INSET_TOL and abs(ri - PHOTO_INSET) <= INSET_TOL
                if not (bleed or inset): fail("P", f'photo inset {li:.0f}/{ri:.0f}px{" (mat outer edge)" if m.get("mat") else ""}, {m["w"]:.0f}px wide (need 0 or {PHOTO_INSET})')
            elif len(r) == 2:   # 2-column grid row: allowed only as a proper grid
                a_, b_ = r; grid_tiles += 2; gap = b_["l"] - a_["r"]
                if min(a_["w"], b_["w"]) < GRID_MIN_TILE - TOL: fail("P", f'2-up row of small tiles {a_["w"]:.0f}+{b_["w"]:.0f}px (grid tiles need >= {GRID_MIN_TILE}px)')
                elif gap < GRID_MIN_GAP - TOL: fail("P", f'2-up grid column gap {gap:.0f}px (min {GRID_MIN_GAP})')
                elif abs(edge(a_)[0] - PHOTO_INSET) > INSET_TOL or abs(edge(b_)[1] - PHOTO_INSET) > INSET_TOL:
                    fail("P", f'2-up grid gutters {edge(a_)[0]:.0f}/{edge(b_)[1]:.0f}px{" (mat outer edge)" if a_.get("mat") else ""} (need {PHOTO_INSET})')
                else: grid_ok += [a_, b_]
            else: fail("P", f'{len(r)}-up photo row (max 2 columns)')
        if grid_tiles > GRID_MAX_TILES: fail("P", f"{grid_tiles} grid tiles on one screen (max {GRID_MAX_TILES}, one 2x2)")
        for rl in model["rails"]:
            if not inwin(rl) or not rl["kids"]: continue
            k0 = rl["kids"][0]; lo, hi = RAIL_W[0] - RAIL_W_TOL, RAIL_W[1] + RAIL_W_TOL
            if rl["scrollLeft"] >= 2: fail("P", f'rail loads scrolled {rl["scrollLeft"]:.0f}px, first card flush at {k0["l"]:.0f}px (scroll-snap without scroll-padding-inline:{PHOTO_INSET}px?)')
            elif abs(k0["l"] - PHOTO_INSET) > INSET_TOL: fail("P", f'rail first card at {k0["l"]:.0f}px (need {PHOTO_INSET})')
            if not lo <= k0["w"] / W <= hi: fail("P", f'rail card {k0["w"] / W:.0%} wide (need {RAIL_W[0]:.0%}-{RAIL_W[1]:.0%})')
            if len(rl["kids"]) > 1 and W - rl["kids"][1]["l"] < PEEK_MIN - TOL: fail("P", f'next rail card peeks only {max(0, W - rl["kids"][1]["l"]):.0f}px (need {PEEK_MIN})')
        vis_photos = [m for m in md if inwin(m) and m["l"] < W]
        # E: elements per screen
        # a legal grid = ONE element; its captions (non-mono text per tile cell, <= GRID_CAPTION_MAX_LINES lines) are part of it
        absorbed = set()
        for m in grid_ok:
            cap = [t for t in tx if t.get("cell") == m["cell"] and t["kind"] != "mono"]
            if sum(t["lines"] for t in cap) <= GRID_CAPTION_MAX_LINES: absorbed.add(m["cell"])
        gok = {id(m) for m in grid_ok}
        g_in = [g for g in groups_of([t for t in tx if t.get("cell") not in absorbed]) if inwin(g)]
        nT = sum(g["kind"] == "text" for g in g_in); nB = sum(g["kind"] == "btn" for g in g_in)
        nP = sum(id(m) not in gok for m in vis_photos) + (1 if grid_ok else 0); nE = nT + nB + nP
        if nT > MAX_TEXTS: fail("E", f"{nT} text blocks (max {MAX_TEXTS})")
        if nB > MAX_BTNS: fail("E", f"{nB} buttons (max {MAX_BTNS})")
        if nE > MAX_ELEMS: fail("E", f"{nE} elements (max {MAX_ELEMS})")
        M.update(nT=nT, nB=nB, nP=nP, raw=sum(1 for t in t_in if t["kind"] == "text"))
        # D: picture-led or air-led
        ph_cells = raster([[m["l"], m["t"], m["r"], m["b"]] for m in md if m["t"] < y1 and m["b"] > y0], y0, hh, nx)
        all_cells = ph_cells | raster([r for t in tx for r in t["rects"] if r[1] < y1 and r[3] > y0], y0, hh, nx)
        total = nx * math.ceil(hh / 6); photo = len(ph_cells) / total; empty = 1 - len(all_cells) / total
        if photo < PHOTO_MIN and empty < EMPTY_MIN: fail("D", f"photo {photo:.0%} (<{PHOTO_MIN:.0%}) and empty {empty:.0%} (<{EMPTY_MIN:.0%})")
        M.update(photo=photo, empty=empty)
        # S: section gap (boundary assigned to the screen holding its midpoint)
        secs = [s for s in model["secs"] if s["cb"] > s["ct"] and s["b"] > start + 2]
        sg = []
        for a, b in zip(secs, secs[1:]):
            gap = b["ct"] - a["cb"]
            if y0 <= (a["cb"] + b["ct"]) / 2 < y1:
                sg.append(round(gap))
                if gap < SECTION_GAP_MIN - TOL: fail("S", f'{gap:.0f}px between {a["id"] or a["sel"]} and {b["id"] or b["sel"]} (min {SECTION_GAP_MIN})')
        M["sgap"] = min(sg) if sg else None
        # H: heading -> next content below it
        hg = []
        for h in (t for t in tx if t["head"] and inwin(t)):
            nxt = [o for o in [*tx, *md] if o is not h and o["t"] >= h["b"] - 1 and o["l"] < h["r"] and o["r"] > h["l"]]
            if not nxt: continue
            o = min(nxt, key=lambda q: q["t"]); gap = o["t"] - h["b"]
            if gap > 400: continue
            hg.append(round(gap))
            if gap < HEAD_GAP_MIN - TOL: fail("H", f'{gap:.0f}px under heading "{h["s"]}" (min {HEAD_GAP_MIN})')
        M["hgap"] = min(hg) if hg else None
        # B: fixed/sticky chrome painted at this scroll position
        bars = bars_at[si]; tot, top, bot, bottom_bars = chrome_total(bars)
        if tot > BARS_MAX + TOL: fail("B", f"bars {tot}px = {top} top + {bot} bottom (max {BARS_MAX}): " + ", ".join(b["sel"] for b in bars))
        for b in bottom_bars: fail("B", f'bottom fixed bar over content: {b["sel"]} ({b["b"] - b["t"]:.0f}px)')
        M["bars"] = tot
        # L: lists (homepage only; other pages are measured but not scored)
        starts = []
        for L in model["lists"]:
            if not (y0 <= L["t"] < y1) or L["rail"] or L["oneRow"] or L["inNav"] or L["n"] < 2: continue
            starts.append(L)
            if not is_home: continue
            if L["n"] > LIST_MAX_ITEMS: fail("L", f'{L["sel"]}: {L["n"]} items (max {LIST_MAX_ITEMS})')
            if not L["media"]:
                multi = [i for i in L["items"] if i["lines"] > 1]
                if multi: fail("L", f'{L["sel"]}: {len(multi)} item(s) wrap past one line, e.g. "{multi[0]["s"]}"')
        if is_home and len(starts) > 1: fail("L", f"{len(starts)} lists on one screen (max 1): " + ", ".join(L["sel"] for L in starts))
        M["lists"] = [f'{L["sel"]}x{L["n"]}' for L in starts]
        if not t_in and not vis_photos: R["G"] = R["P"] = R["T"] = ("PASS", [])
        screens.append({"i": si, "y0": round(y0), "names": names, "R": R, "M": M})
    return screens


# ------------------------------------------------------------------ report
def mark(status, reasons, applicable=True):
    return "FAIL" if status == "FAIL" else ("PASS" if applicable else " -  ")


def render_page(path, model, screens, is_home, note):
    L = [f"PAGE {path}", f"  home page (lists scored): {'yes' if is_home else 'no (lists measured only)'}   start y={round(model['start'])} "
         f"({'after #film' if model['hasFilm'] else 'no film: top of page'})   doc {round(model['docH'])}px   fonts loaded: {model['fonts']}"]
    if note: L.append("  NOTE " + note)
    head = "   #   y0  " + " ".join(k.center(4) for k, _ in RULES) + "  txt raw btn img  photo empty  gut sgap hgap bars  sections"
    L += [head, "  " + "-" * (len(head) - 2)]
    for s in screens:
        M, R = s["M"], s["R"]
        cells = " ".join(R[k][0].center(4) for k, _ in RULES)
        f = lambda v: "  - " if v is None else f"{v:>4}"
        L.append(f"  {s['i'] + 1:>2} {s['y0']:>5}  {cells}  {M['nT']:>3} {M['raw']:>3} {M['nB']:>3} {M['nP']:>3}  {M['photo']:>5.0%} {M['empty']:>5.0%}  {M['gut']:>3} {f(M['sgap'])} {f(M['hgap'])} {M['bars']:>4}  {','.join(s['names'])[:34]}")
    bad = [s for s in screens if any(v[0] == "FAIL" for v in s["R"].values())]
    failing = sorted({k for s in bad for k, v in s["R"].items() if v[0] == "FAIL"})
    L += ["", f"  RESULT {'FAIL' if bad else 'PASS'}: {len(screens) - len(bad)}/{len(screens)} screens pass; failing rules: {', '.join(failing) or 'none'}", ""]
    for s in bad:
        L.append(f"  screen {s['i'] + 1} (y={s['y0']}, {','.join(s['names'])[:50]})")
        for k, (st, why) in s["R"].items():
            uniq = {}
            for w in why: uniq[w] = uniq.get(w, 0) + 1
            for w, c in list(uniq.items())[:5]: L.append(f"    [{k}] {w}" + (f"  (x{c})" if c > 1 else ""))
            if len(uniq) > 5: L.append(f"    [{k}] ... +{len(uniq) - 5} more")
    return "\n".join(L), failing, len(bad)


def main():
    ap = argparse.ArgumentParser(description="MHCR breathing-room QA at 390x844 DPR3")
    ap.add_argument("pages", nargs="+"); ap.add_argument("--shots", action="store_true", help="save a screenshot of every screen to out/breathing/")
    ap.add_argument("--skip-footer", action="store_true", help="do not score the footer screens")
    a = ap.parse_args()
    files = [Path(p).resolve() for p in a.pages]
    for f in files:
        if not f.is_file(): sys.exit(f"not a file: {f}")
    root = Path(os.path.commonpath([str(f.parent) for f in files]))
    root = next((d for d in [root, *root.parents] if (d / "css" / "site.css").exists()), root)   # serve the site root
    if str(root) == "/": sys.exit("pages share no common folder below /; pass pages from one site folder")
    OUT.mkdir(exist_ok=True)
    if a.shots: (OUT / "breathing").mkdir(exist_ok=True)
    srv = qa_v1.serve(root); base = f"http://127.0.0.1:{srv.server_address[1]}/"
    sections, summary, any_fail = [], [], False
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        for f in files:
            rel = f.relative_to(root).as_posix(); is_home = f.name == "index.html"
            ctx = br.new_context(viewport={"width": W, "height": H}, device_scale_factor=DPR, is_mobile=True, has_touch=True, user_agent=UA)
            ctx.route("**/*", qa_v1.route_handler); pg = ctx.new_page()
            try:
                pg.goto(base + quote(rel), wait_until="load"); qa_v1.settle(pg)
                model = pg.evaluate(MODEL_JS, {"exempt": EXEMPT, "monoFs": MONO_LABEL_MAX_FS, "minPhoto": MIN_PHOTO_PX})
                note = ""
                if model["innerW"] != W: note = f"layout viewport is {model['innerW']}px, not {W}: page probably lacks <meta name=viewport>. All numbers invalid."
                elif model["extFonts"] and model["fonts"] == 0: note = "page links Google Fonts but no web font loaded (offline?): line counts may be off."
                ys, y = [], model["start"]
                foot_top = next((s["t"] for s in model["secs"] if s["foot"]), model["docH"])
                while y < model["docH"] - SLIVER * H:
                    if a.skip_footer and y >= foot_top - 1: break
                    ys.append(y); y += H
                bars_at = []
                for i, y0 in enumerate(ys):
                    pg.evaluate("y=>scrollTo({top:y,behavior:'instant'})", y0); pg.wait_for_timeout(BAR_WAIT_MS)
                    bars_at.append(pg.evaluate(BARS_JS))
                    if a.shots: pg.screenshot(path=str(OUT / "breathing" / f"{f.stem}-{f.parent.name}-s{i + 1}.jpg"), type="jpeg", quality=60)
                screens = score_page(model, bars_at, is_home, a.skip_footer)
                text, failing, nbad = render_page(rel, model, screens, is_home, note)
                if note.startswith("layout viewport"): failing, nbad = ["VIEWPORT"], len(screens)
                summary.append((rel, "FAIL" if nbad else "PASS", len(screens), nbad, ",".join(failing) or "-"))
            except Exception as e:
                text = f"PAGE {rel}\n  SCRIPT ERROR: {e!r}"; summary.append((rel, "ERROR", 0, 0, "script error"))
            any_fail |= summary[-1][1] != "PASS"; sections.append(text); ctx.close()
        br.close()
    srv.shutdown()
    w = max(len(s[0]) for s in summary)
    out = [f"MHCR BREATHING-ROOM QA  {time.strftime('%Y-%m-%d %H:%M:%S')}  {W}x{H} @{DPR}x mobile emulation",
           "Rules: G text gutter>=24 | P photo full-bleed or 24px inset, 1/row (2x2 grid ok = 1 element: tiles>=150, gap>=16, 24px gutters to mat edge, <=4/screen), rails 80-84% |",
           "       T text <=300px wide (stmt 330), <=4 lines |",
           "       S section gap>=112 | H heading gap>=28 | E <=6 elems, <=4 text, <=1 button | D photo>=40% OR empty>=60% | B bars<=64, no bottom bar |",
           "       L homepage lists <=6 items, 1 line, 1 list/screen.   '-' = not measurable on that screen.", "",
           f"{'PAGE'.ljust(w)}  RESULT  SCREENS  FAILING  FAILING RULES", "-" * (w + 40)]
    out += [f"{s[0].ljust(w)}  {s[1]:<6}  {s[2]:>7}  {s[3]:>7}  {s[4]}" for s in summary]
    out += ["", *[t + "\n" for t in sections]]
    text = "\n".join(out); (OUT / "breathing-report.txt").write_text(text); print(text)
    print(f"report saved: {OUT / 'breathing-report.txt'}")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
