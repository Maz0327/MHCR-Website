/* The stacked stone film: Fireplace 1 goes from drywall to stone, course by course, as you scroll.
   Logic ported from the approved stone film (mhcr-stone-film/home_part4.js). Removed for good: the .beat
   captions and the #rail stage strip. Framing now follows the comp: full-bleed cover on phone and desktop.
   Data-driven: <script type="application/json" id="film-data"> = _build/data/film.json (geo, timeline, cells, focus).
   Page hooks: #film (tall scroll section), #filmCanvas, optional #filmBar (> i scales with progress) and #filmCue,
   and hidden frames <img data-film-frame="before|prep|final" data-film-set="m|s|l" data-nopic>. */
(() => {
  const film = document.getElementById("film"), cv = document.getElementById("filmCanvas");
  const dataEl = document.getElementById("film-data");
  if (!film || !cv || !dataEl) return;
  const D = JSON.parse(dataEl.textContent), GEO = D.geo, T = D.timeline, FOCUS = D.focus || { m: 0.5, d: 0.56 };
  const ctx = cv.getContext("2d", { alpha: false });
  const bar = document.querySelector("#filmBar i"), cue = document.getElementById("filmCue");
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NAMES = ["before", "prep", "final"];
  const INK = getComputedStyle(film).backgroundColor || "#0b0b0c";

  // Seeded random so the stone order is the same on every visit.
  let seed = 7;
  const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

  // Stone-sized cells, course by course from the floor up. Row height scales with the frame's stone area.
  function buildCells(S, rowH, cellW) {
    seed = 7; const out = [], rows = [];
    let y = S.y1;
    while (y > S.y0 + 1e-4) { const h = Math.min(rowH * (0.85 + rnd() * 0.45), y - S.y0); rows.push({ y0: y - h, y1: y }); y -= h; }
    rows.forEach((r, i) => {
      let x = S.x0, first = true;
      while (x < S.x1 - 1e-4) {
        let w = (first ? cellW * (0.6 + (i % 2) * 0.9) : 0) + cellW * (1 + rnd() * 2);
        first = false; w = Math.min(w, S.x1 - x);
        out.push({ x0: x, x1: x + w, y0: r.y0, y1: r.y1, t: (i / rows.length) * 0.92 + rnd() * 0.05, d: 0.018 + rnd() * 0.02 });
        x += w;
      }
    });
    return out;
  }
  const CELLS = { d: buildCells(GEO.d.STONE, ...D.cells.d), m: buildCells(GEO.m.STONE, ...D.cells.m) };

  // Portrait frames on phones, wide frames elsewhere (l on big screens). Frames are real <img> tags in the page.
  let set = "", imgs = {}, ready = 0;
  function pickSet() {
    const want = innerWidth / innerHeight < 0.9 ? "m" : "d";
    if (want === set) return;
    set = want; ready = 0; imgs = {};
    const big = Math.max(innerWidth, innerHeight) * Math.min(devicePixelRatio || 1, 2) > 1700;
    const size = set === "m" ? "m" : (big ? "l" : "s");
    NAMES.forEach((n) => {
      const im = film.querySelector(`img[data-film-frame="${n}"][data-film-set="${size}"]`);
      if (!im) return;
      imgs[n] = im;
      if (im.loading === "lazy") im.loading = "eager";
      if (im.complete && im.naturalWidth) ready++;
      else im.addEventListener("load", () => { ready++; dirty = true; }, { once: true });
    });
  }

  let W = 0, H = 0, dirty = true, shown = 0, target = 0, lastKey = "";
  function resize() {
    const r = cv.getBoundingClientRect();
    if (Math.abs(r.width - W) < 1 && Math.abs(r.height - H) < 160 && W) return; // ignore the phone URL bar
    W = r.width; H = r.height;
    pickSet();
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const bw = Math.min(Math.round(W * dpr), 3200), s = bw / W;
    cv.width = bw; cv.height = Math.round(H * s); ctx.setTransform(s, 0, 0, s, 0, 0); ctx.imageSmoothingQuality = "high";
    dirty = true; draw(true);
  }

  // Cover the canvas; the wall's centre sits at FOCUS[set] of the width (clamped so no edge shows).
  function layout(im) {
    const S = GEO[set].STONE, s = Math.max(W / im.naturalWidth, H / im.naturalHeight);
    const dw = im.naturalWidth * s, dh = im.naturalHeight * s, fx = (S.x0 + S.x1) / 2;
    return { dx: Math.min(0, Math.max(W - dw, W * FOCUS[set] - fx * dw)), dy: (H - dh) / 2, dw, dh };
  }

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const span = (p, [a, b]) => clamp((p - a) / (b - a));
  const ease = (t) => t * t * (3 - 2 * t);

  function region(im, L, r, alpha, dy = 0) {
    const sw = im.naturalWidth, sh = im.naturalHeight;
    ctx.globalAlpha = alpha;
    ctx.drawImage(im, r.x0 * sw, r.y0 * sh, (r.x1 - r.x0) * sw, (r.y1 - r.y0) * sh,
      L.dx + r.x0 * L.dw, L.dy + r.y0 * L.dh + dy, (r.x1 - r.x0) * L.dw, (r.y1 - r.y0) * L.dh);
  }

  function draw(force) {
    const p = shown, key = p.toFixed(4) + W + "x" + H + ready + set;
    if (!force && key === lastKey) return;
    lastKey = key;
    const b = imgs.before, pr = imgs.prep, f = imgs.final, G = GEO[set];
    ctx.globalAlpha = 1; ctx.fillStyle = INK; ctx.fillRect(0, 0, W, H);
    if (!b || !b.complete || !b.naturalWidth) return;
    const L = layout(b), full = { x0: 0, x1: 1, y0: 0, y1: 1 };
    region(b, L, full, 1);
    const prepA = ease(span(p, T.prepIn));
    if (pr && pr.naturalWidth && prepA > 0) region(pr, L, full, prepA);
    const q = span(p, T.stone); // stone goes up over the prepped wall
    if (f && f.naturalWidth && q > 0 && prepA >= 1) {
      for (const c of CELLS[set]) {
        const a = clamp((q - c.t) / c.d);
        if (a > 0) region(f, L, c, ease(a), (1 - ease(a)) * -8);
      }
      // Keep the prepped insert and the props in front until the finish, so the fire only appears at the end.
      const keep = 1 - ease(span(p, T.finalIn));
      region(pr, L, G.INSERT, keep);
      G.PROPS.forEach((r) => region(pr, L, r, keep));
      // Hyperlapse feel: small exposure steps, like days passing on a fixed camera.
      if (!reduce && q < 1) {
        const day = Math.floor(q * 7), k = (day % 2 ? 1 : -1) * 0.035 * Math.sin(Math.PI * clamp(q * 7 - day));
        ctx.globalAlpha = Math.abs(k); ctx.fillStyle = k > 0 ? "#fff4e6" : "#000"; ctx.fillRect(0, 0, W, H);
      }
    }
    const finA = ease(span(p, T.finalIn));
    if (f && f.naturalWidth && finA > 0) region(f, L, full, finA);
    ctx.globalAlpha = 1;
  }

  function progress() {
    const r = film.getBoundingClientRect();
    return clamp(-r.top / Math.max(1, r.height - innerHeight));
  }

  function tick() {
    target = progress();
    shown = reduce ? target : shown + (target - shown) * 0.14;
    if (Math.abs(target - shown) < 0.0004) shown = target;
    film.style.setProperty("--film-p", shown.toFixed(4));
    if (bar) bar.style.transform = `scaleX(${shown.toFixed(4)})`;
    if (cue) cue.style.opacity = shown > 0.02 ? 0 : 1;
    draw(dirty); dirty = false; // draw() skips itself when nothing changed
    requestAnimationFrame(tick);
  }

  new ResizeObserver(resize).observe(cv);
  addEventListener("orientationchange", () => { W = 0; resize(); });
  resize();
  shown = target = progress();
  requestAnimationFrame(tick);
})();
