/* Job pages: the before/after slider (.ba) and the build-up (#build). No deps.
   .ba      drag anywhere on the photo (or the knob), tap to jump, or use the arrow keys on the knob (role=slider).
            Sets --split (0-100%) on .ba; the after photo is clipped to the right of the line.
   #build   a pinned 100svh stage; scrolling wipes each frame up over the last (before -> in progress -> after) and
            fills the progress line. --steps on #build sets the scroll length (the CSS uses it).
   Reduced motion: the build-up becomes a plain stack of frames (.is-static). */
(() => {
  "use strict";
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- before / after ---- */
  document.querySelectorAll(".ba").forEach((ba) => {
    const knob = ba.querySelector(".ba__knob");
    let split = 50, drag = false;
    const set = (v) => {
      split = clamp(v, 0, 100);
      ba.style.setProperty("--split", split.toFixed(2) + "%");
      if (knob) { knob.setAttribute("aria-valuenow", Math.round(split)); knob.setAttribute("aria-valuetext", `${Math.round(split)}% after`); }
    };
    const fromX = (x) => { const r = ba.getBoundingClientRect(); set(((x - r.left) / r.width) * 100); };
    ba.addEventListener("dragstart", (e) => e.preventDefault());   // desktop: no native image drag (it cancels the pointer)
    ba.addEventListener("pointerdown", (e) => { drag = true; ba.setPointerCapture(e.pointerId); fromX(e.clientX); e.preventDefault(); });
    ba.addEventListener("pointermove", (e) => { if (drag) fromX(e.clientX); });
    ["pointerup", "pointercancel"].forEach((t) => ba.addEventListener(t, () => { drag = false; }));
    if (knob) knob.addEventListener("keydown", (e) => {
      const d = { ArrowLeft: -5, ArrowDown: -5, ArrowRight: 5, ArrowUp: 5, Home: -100, End: 100 }[e.key];
      if (d) { set(split + d); e.preventDefault(); }
    });
    set(50);
  });

  /* ---- build-up ---- */
  const build = document.getElementById("build");
  if (!build) return;
  const frames = [...build.querySelectorAll(".build__frame")], bar = build.querySelector(".build__bar i");
  if (reduce || frames.length < 2) { build.classList.add("is-static"); return; }
  const n = frames.length - 1;
  frames.forEach((f, k) => { if (k) { f.style.opacity = 1; f.style.clipPath = "inset(100% 0 0 0)"; } });
  let shown = -1, ticking = false;
  function paint() {
    ticking = false;
    const r = build.getBoundingClientRect(), p = clamp(-r.top / Math.max(1, r.height - innerHeight));
    if (Math.abs(p - shown) < 0.0005) return;
    shown = p;
    frames.forEach((f, k) => {
      if (!k) return;
      const w = clamp(p * n * 1.15 - (k - 1));                     // each frame wipes up over the one before it
      f.style.clipPath = `inset(${((1 - w) * 100).toFixed(2)}% 0 0 0)`;
    });
    if (bar) bar.style.transform = `scaleX(${p.toFixed(4)})`;
  }
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(paint); } };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  paint();
})();
