#!/usr/bin/env python3
"""Inner pages vs approved comps, side by side (service, services index, job, text pages).

  python3 -I _build/qa/shots_pages_vs_comps.py service index job text [OUT_DIR]

Reuses the server/settle/sheet helpers from shots_home_vs_comps.py. Each set shoots the built page at the comp's
states (phone 390x844 @3x, desktop 1440x900) and writes <set>-vs-comp-390.png / -1440.png (text pages: text-pages-*.png).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shots_home_vs_comps as H  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

C = H.COMPS
TOP, BOTTOM = ("top",), ("bottom",)
# set: (page, out name, phone comps, phone states, desktop comps, desktop states)
SETS = {
    "service": ("services/bathroom-remodeling.html", "service-vs-comp",
                [C / f"tpl2-service-phone-{i}.png" for i in (1, 2, 3)], [TOP, ("el", ".svc-end", 96), BOTTOM],
                [C / f"tpl2-service-desktop-{i}.png" for i in (1, 2, 3)], [TOP, ("el", ".svc-jobs .card", 0), BOTTOM]),
    "index": ("services.html", "index-vs-comp",
              [C / f"tpl2-index-phone-{i}.png" for i in (1, 2)], [TOP, BOTTOM],
              [C / "tpl2-index-desktop-1.png"], [TOP]),
    "job": ("jobs/bathroom-remodel.html", "job-vs-comp",
            [C / f"tpl2-job-phone-{i}.png" for i in (1, 2, 3, 4)], [TOP, ("el", ".ba", 64), ("build", 0.45), BOTTOM],
            [C / f"tpl2-job-desktop-{i}.png" for i in (1, 2, 3, 4)], [TOP, ("el", ".ba", 78), ("build", 0.45), BOTTOM]),
    "text": ("terms.html", "text-pages",
             [C / f"tpl2-terms-phone-{i}.png" for i in (1, 2)], [TOP, BOTTOM], [], [TOP, BOTTOM]),
}
BUILD = """p => { const b = document.getElementById('build'); const top = b.getBoundingClientRect().top + scrollY;
  window.scrollTo({top: top + p * (b.offsetHeight - innerHeight), behavior: 'instant'}); }"""


def go(page, state):
    if state[0] == "top": page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    elif state[0] == "bottom": page.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})")
    elif state[0] == "el": page.evaluate(H.TOP, [state[1], state[2]])
    elif state[0] == "build": page.evaluate(BUILD, state[1])


def shoot_set(browser, base, key):
    path, out, pc, ps, dc, ds = SETS[key]
    shots = {}
    for tag, vp, states in (("390", dict(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True), ps),
                            ("1440", dict(viewport={"width": 1440, "height": 900}, device_scale_factor=1), ds)):
        ctx = browser.new_context(**vp); page = ctx.new_page(); page.goto(f"{base}/{path}"); H.settle(page)
        shots[tag] = []
        for i, st in enumerate(states, 1):
            go(page, st); shots[tag].append(H.shoot(page, f"{out}-{tag}-{i}", 900))
        ctx.close()
    name = path.rsplit("/", 1)[-1]
    if pc: H.sheet(browser, pc, shots["390"], True, 390, 844, f"{name} 390: approved comp (top) vs build (bottom)", f"{out}-390")
    else: H.sheet(browser, shots["390"], shots["390"], True, 390, 844, f"{name} 390 (build)", f"{out}-390")
    if dc: H.sheet(browser, dc, shots["1440"], False, 720, 450, f"{name} 1440: approved comp (left) vs build (right)", f"{out}-1440")
    else: H.sheet(browser, shots["1440"], shots["1440"], False, 720, 450, f"{name} 1440 (build; no desktop comp: text-page system)", f"{out}-1440")


if __name__ == "__main__":
    keys = [a for a in sys.argv[1:] if a in SETS]
    rest = [a for a in sys.argv[1:] if a not in SETS]
    H.OUT = Path(rest[0]) if rest else Path.home() / "Documents/Projects/MHCR-Redesign/build-qa"
    (H.OUT / "shots").mkdir(parents=True, exist_ok=True)
    srv = H.serve(H.SITE)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        for k in keys or SETS:
            shoot_set(browser, f"http://127.0.0.1:{srv.server_address[1]}", k)
        browser.close()
    srv.shutdown()
    print("\n".join(str(p) for p in sorted(H.OUT.glob("*-vs-comp-*.png")) + sorted(H.OUT.glob("text-pages-*.png"))))
