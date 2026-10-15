/* The Dial: one full-screen frame + a thumb dial, small job to big job.
   Logic ported from the approved comp (round-3 wildcard-2-the-dial.js); comp-only still/URL modes removed.
   Data-driven: the build renders one <template data-dial-stop> per stop from services.json + jobs.json:
     <template data-dial-stop data-kind="photo|word|urgent" data-label="Bathroom"
               data-job="Tiled walk-in shower" data-href="jobs/....html"> ...frame content... </template>
   Page hooks: #frame (data-default-stop, data-keep-turned, data-sweep-on-view), #stage, #jobLink, #jobName,
   #dial, #dialSvg (viewBox 0 0 390 100), #dialLabel (role=slider), #prev, #next. */
(function () {
  const $ = (id) => document.getElementById(id);
  const frame = $("frame"), stage = $("stage"), svg = $("dialSvg");
  if (!frame || !stage || !svg) return;
  const TPL = [...document.querySelectorAll("template[data-dial-stop]")];
  const STOPS = TPL.map((t) => ({ kind: t.dataset.kind, label: t.dataset.label, job: t.dataset.job || "", href: t.dataset.href || "" }));
  const N = STOPS.length;
  if (!N) return;
  const STEP = 8, R = 560, CX = 195, TOP = 30, CY = TOP + R; // dial geometry (deg, svg px)
  const DEF = Math.min(N, Math.max(1, +frame.dataset.defaultStop || 1));
  const KEEP_TURNED = "keepTurned" in frame.dataset, SWEEP_ON_VIEW = "sweepOnView" in frame.dataset;
  const reduce = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  let cur = DEF - 1;

  /* The iris opens from the dial pointer and must cover the whole frame, phone or desktop. */
  function iris() {
    const d = $("dial"), x = d.offsetLeft + d.offsetWidth / 2, y = d.offsetTop + 30;
    return { x, y, r: Math.hypot(Math.max(x, frame.clientWidth - x), Math.max(y, frame.clientHeight - y)) + 24 };
  }

  /* One frame: a clone of the stop's template (a real job photo, or a big-word frame). */
  function layer(i) {
    const el = document.createElement("div"), k = STOPS[i].kind;
    el.className = "layer" + (k === "photo" ? "" : " layer--word") + (k === "urgent" ? " layer--urgent" : "");
    el.appendChild(TPL[i].content.cloneNode(true));
    return el;
  }

  /* Dial: ticks on a big arc, numbers on the stops, fixed pointer at the top. */
  function drawDial(rot) {
    let out = `<circle cx="${CX}" cy="${CY}" r="${R}" class="disc"/><circle cx="${CX}" cy="${CY}" r="${R}" class="arc"/>`;
    for (let k = -2; k <= (N - 1) * 5 + 2; k++) {
      const a = ((k / 5) - rot) * STEP * Math.PI / 180;
      if (Math.abs(a) > 0.42) continue;
      const major = k % 5 === 0 && k >= 0 && k <= (N - 1) * 5;
      const len = major ? 24 : 11, sx = Math.sin(a), cy = Math.cos(a);
      const x1 = CX + R * sx, y1 = CY - R * cy, x2 = CX + (R - len) * sx, y2 = CY - (R - len) * cy;
      const on = major && Math.round(rot) === k / 5;
      out += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" class="${major ? "tk tk--major" : "tk"}${on ? " tk--on" : ""}"/>`;
      if (major) {
        const tx = CX + (R - 40) * sx, ty = CY - (R - 40) * cy, deg = a * 180 / Math.PI;
        out += `<text x="${tx.toFixed(1)}" y="${ty.toFixed(1)}" transform="rotate(${deg.toFixed(2)} ${tx.toFixed(1)} ${ty.toFixed(1)})" class="num${on ? " num--on" : ""}">${String(k / 5 + 1).padStart(2, "0")}</text>`;
      }
    }
    out += `<path d="M${CX - 8} ${TOP - 18} L${CX + 8} ${TOP - 18} L${CX} ${TOP - 5} Z" class="ptr"/>`;
    svg.innerHTML = out;
  }

  /* The dial's own label updates at once; the caption over the photo waits for the iris. */
  function label(i) {
    const s = STOPS[i], lb = $("dialLabel");
    lb.textContent = s.label;
    lb.setAttribute("aria-valuemax", N);
    lb.setAttribute("aria-valuenow", i + 1);
    lb.setAttribute("aria-valuetext", s.label + (s.job ? ": " + s.job : ""));
    $("prev").disabled = i === 0; $("next").disabled = i === N - 1;
  }
  function caption(i) {
    const s = STOPS[i], link = $("jobLink"), photo = s.kind === "photo";
    link.hidden = !photo;
    if (photo) { $("jobName").textContent = s.job; link.href = s.href || "#jobs"; }
    frame.classList.toggle("is-word", !photo);
  }
  let capT;
  function swapCaption(i, wait) {
    clearTimeout(capT); $("jobLink").classList.add("is-out");
    capT = setTimeout(() => { caption(i); $("jobLink").classList.remove("is-out"); }, wait);
  }

  /* Go to a stop: the new frame opens as an iris from the pointer (a cut, not a slide). */
  function go(i, animate = true) {
    i = Math.max(0, Math.min(N - 1, i));
    if (i === cur && stage.children.length) return;
    const from = cur; cur = i;
    const top = layer(i);
    if (animate && !reduce()) {
      const c = iris();
      top.style.clipPath = `circle(0px at ${c.x}px ${c.y}px)`;
      stage.appendChild(top);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        top.style.transition = "clip-path .62s cubic-bezier(.7,0,.2,1)";
        top.style.clipPath = `circle(${c.r}px at ${c.x}px ${c.y}px)`;
      }));
      setTimeout(() => { while (stage.children.length > 1 && stage.firstChild !== top) stage.firstChild.remove(); top.style.clipPath = ""; }, 700);
      swapCaption(i, 300);
    } else { stage.replaceChildren(top); caption(i); }
    tween(from, i); label(i);
    if (i !== from) frame.classList.add("is-turned");
  }

  let rotNow = cur, tw = 0;
  function tween(a, b) { // the dial rotates to the new stop
    const t0 = performance.now(), d = reduce() ? 0 : 520, id = ++tw;
    (function f(t) {
      if (id !== tw) return;
      const p = d ? Math.min(1, (t - t0) / d) : 1, e = 1 - Math.pow(1 - p, 3);
      rotNow = a + (b - a) * e; drawDial(rotNow); if (p < 1) requestAnimationFrame(f);
    })(t0);
  }

  /* Input: drag the dial, tap the arrows, arrow keys on the slider. */
  $("prev").addEventListener("click", () => go(cur - 1));
  $("next").addEventListener("click", () => go(cur + 1));
  $("dialLabel").addEventListener("keydown", (e) => {
    const step = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1, Home: -N, End: N }[e.key];
    if (step) { go(cur + step); e.preventDefault(); }
  });
  let drag = null;
  svg.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, r: rotNow, k: svg.getBoundingClientRect().width / 390 }; svg.setPointerCapture(e.pointerId); });
  svg.addEventListener("pointermove", (e) => {
    if (!drag) return;
    tw++; // stop any running tween
    rotNow = Math.max(-0.4, Math.min(N - 0.6, drag.r - (e.clientX - drag.x) / drag.k / (R * STEP * Math.PI / 180)));
    drawDial(rotNow);
  });
  const release = () => { if (!drag) return; drag = null; const t = Math.round(rotNow); if (t !== cur) go(t); else tween(rotNow, cur); };
  svg.addEventListener("pointerup", release);
  svg.addEventListener("pointercancel", release);

  /* First paint on the default stop; once the dial is on screen, one sweep 01 -> default teaches it. */
  stage.replaceChildren(layer(cur)); label(cur); caption(cur); drawDial(cur);
  function sweep() {
    if (reduce() || DEF < 2) return;
    cur = 0; stage.replaceChildren(layer(0)); label(0); caption(0); rotNow = 0; drawDial(0);
    let k = 1;
    const iv = setInterval(() => {
      go(k++);
      if (k >= DEF) { clearInterval(iv); if (!KEEP_TURNED) frame.classList.remove("is-turned"); }
    }, 520);
  }
  if (SWEEP_ON_VIEW && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((e) => { if (e[0].isIntersecting) { io.disconnect(); sweep(); } }, { threshold: 0.6 });
    io.observe(frame);
  } else sweep();
})();
