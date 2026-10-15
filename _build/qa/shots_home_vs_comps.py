#!/usr/bin/env python3
"""Homepage vs approved comps, side by side (for Maz: he judges screenshots, not scripts).

  python3 -I _build/qa/shots_home_vs_comps.py [OUT_DIR]     (default: ~/Documents/Projects/MHCR-Redesign/build-qa)

Needs playwright + system Chrome (already on this Mac). Serves the repo root on a throwaway local port, shoots the
built index.html at the same states as the comps (phone 390x844 @3x = tpl2-home-phone-1..8, desktop 1440x900 =
tpl2-home-desktop-1..6), then lays comp (top/left) and build (bottom/right) out in one page and screenshots that:
  home-vs-comp-390.png, home-vs-comp-1440.png (+ the single shots in shots/).
"""
import functools, http.server, os, sys, threading
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parents[2]
COMPS = Path.home() / "Documents/Projects/MHCR-Redesign/round-3-fresh-direction/wildcard-2"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents/Projects/MHCR-Redesign/build-qa"


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k): pass
        def handle(self):
            try: super().handle()
            except (BrokenPipeError, ConnectionResetError): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


TOP = "([sel, y]) => { const r = document.querySelector(sel).getBoundingClientRect(); window.scrollTo({top: scrollY + r.top - y, behavior: 'instant'}); }"
FILM = """p => { const f = document.getElementById('film'); const top = f.getBoundingClientRect().top + scrollY;
  window.scrollTo({top: top + p * (f.offsetHeight - 2 * innerHeight), behavior: 'instant'}); }"""


def settle(page):
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    page.evaluate("Promise.all([...document.images].filter(i => !i.loading || i.loading === 'eager').map(i => i.decode().catch(() => 0)))")


def shoot(page, name, wait=700):
    page.wait_for_timeout(wait)
    path = OUT / "shots" / f"{name}.png"
    page.screenshot(path=str(path))
    return path


def phone(browser):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
    page = ctx.new_page(); page.goto(URL); settle(page)
    shots = [shoot(page, "home-390-1-film-opener", 900)]
    page.evaluate(FILM, 0.42); shots.append(shoot(page, "home-390-2-film-plays", 1400))
    page.evaluate(TOP, ["#frame", 844]); page.wait_for_timeout(1500)     # film settles on its last frame first
    page.evaluate(TOP, ["#frame", 0]); shots.append(shoot(page, "home-390-3-hand-off", 60))
    shots.append(shoot(page, "home-390-4-dial-05", 3600))
    page.evaluate(TOP, ["#jobsTitle", 84]); shots.append(shoot(page, "home-390-5-our-jobs", 900))
    page.evaluate(TOP, ["#procTitle", 84]); shots.append(shoot(page, "home-390-6-our-process", 900))
    page.evaluate(TOP, [".ask__photo", 0]); shots.append(shoot(page, "home-390-7-the-ask", 900))
    page.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})")
    shots.append(shoot(page, "home-390-8-footer", 900))
    ctx.close()
    return shots


def desktop(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page = ctx.new_page(); page.goto(URL); settle(page)
    shots = [shoot(page, "home-1440-1-film-opener", 900)]
    page.evaluate(TOP, ["#frame", 0]); shots.append(shoot(page, "home-1440-2-dial-05", 3600))
    for _ in range(4):
        page.click("#prev"); page.wait_for_timeout(650)
    page.mouse.move(5, 450)
    shots.append(shoot(page, "home-1440-3-word-stop-01", 900))
    page.evaluate(TOP, ["#jobsTitle", 100]); shots.append(shoot(page, "home-1440-4-our-jobs", 900))
    page.evaluate(TOP, [".rail figure", 130]); shots.append(shoot(page, "home-1440-5-our-process", 900))
    page.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})")
    shots.append(shoot(page, "home-1440-6-ask-footer", 900))
    ctx.close()
    return shots


def sheet(browser, comps, builds, cols, w, h, label, out):
    """One page: comp row over build row (phone) or comp | build pairs (desktop)."""
    cell = lambda p, cap: f'<figure><img src="file://{p}" style="width:{w}px;height:{h}px"><figcaption>{cap}</figcaption></figure>'
    rows = []
    if cols:   # phone: two rows of 8
        rows.append('<div class="row">' + "".join(cell(c, f"COMP {i + 1}") for i, c in enumerate(comps)) + "</div>")
        rows.append('<div class="row">' + "".join(cell(b, f"BUILD {i + 1}") for i, b in enumerate(builds)) + "</div>")
    else:      # desktop: comp | build per state
        comps = list(comps) + [None] * (len(builds) - len(comps))
        rows += [f'<div class="row">{cell(c, f"COMP {i + 1}") if c else f"<figure style=\'width:{w}px\'></figure>"}{cell(b, f"BUILD {i + 1}")}</div>'
                 for i, (c, b) in enumerate(zip(comps, builds))]
    doc = OUT / "shots" / f"_{out}.html"
    doc.write_text(f"""<!doctype html><meta charset="utf-8"><style>body{{margin:0;padding:24px;background:#d9d6d1;font:600 14px system-ui}}
      h1{{font-size:18px;margin:0 0 16px}} .row{{display:flex;gap:16px;margin-bottom:16px}} figure{{margin:0}}
      img{{display:block;box-shadow:0 1px 4px rgba(0,0,0,.25)}} figcaption{{margin-top:6px}}</style>
      <h1>{label}</h1>{''.join(rows)}""")
    ctx = browser.new_context(viewport={"width": 800, "height": 600}, device_scale_factor=1)
    pg = ctx.new_page(); pg.goto(f"file://{doc}"); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / f"{out}.png"), full_page=True)
    ctx.close()
    return OUT / f"{out}.png"


if __name__ == "__main__":
    (OUT / "shots").mkdir(parents=True, exist_ok=True)
    srv = serve(SITE)
    URL = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        ph, dk = phone(browser), desktop(browser)
        a = sheet(browser, [COMPS / f"tpl2-home-phone-{i}.png" for i in range(1, 9)], ph, True, 390, 844,
                  "Homepage 390: approved comp (top) vs build (bottom)", "home-vs-comp-390")
        b = sheet(browser, [COMPS / f"tpl2-home-desktop-{i}.png" for i in range(1, 7)], dk, False, 720, 450,
                  "Homepage 1440: approved comp (left) vs build (right)", "home-vs-comp-1440")
        browser.close()
    srv.shutdown()
    print(a, b, sep="\n")
