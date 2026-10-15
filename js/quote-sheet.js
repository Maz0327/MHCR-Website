/* The quote sheet (#quote): step 1 = pick the kind of work, step 2 = details (or Call when no form service is set).
   Opened by js/dialog.js. With an endpoint the form POSTs via fetch (Accept: JSON) and shows Sent / Error in place.
   Without one there is no <form> at all, so nothing can ever 405: step 2 is the Call (and optional Text) fallback.
   "Emergency services" shows "call us instead" first. "Something else" opens a required text box. No deps. */
(() => {
  "use strict";
  const sheet = document.getElementById("quote");
  if (!sheet) return;
  const box = sheet.querySelector(".sheet__form"), steps = [...sheet.querySelectorAll(".sheet__step")];
  const q = (s) => sheet.querySelector(s), err = (id, msg) => { const e = document.getElementById(id); if (e) e.textContent = msg || ""; };
  const other = q("[data-other-box]"), urgent = q("[data-urgent-box]"), next = q("[data-next]"), done = q("[data-done]");
  const picked = () => q("input[name=project]:checked");
  const isForm = box.tagName === "FORM";

  function show(k) {
    steps.forEach((s, i) => { s.hidden = i !== k; });
    if (k === 1) {
      const p = picked(), o = q("#q-other");
      q("[data-pick]").textContent = p ? (p.hasAttribute("data-other") && o.value.trim() ? o.value.trim() : p.value) : "";
    }
    const f = steps[k].querySelector(k ? "input:not([tabindex='-1']), a.btn" : "input:checked, input");
    if (f) f.focus();
  }
  function reset() {
    if (isForm) box.reset(); else sheet.querySelectorAll("input[name=project]").forEach((r) => { r.checked = false; });
    other.hidden = true; urgent.hidden = true; next.hidden = false; done.hidden = true; box.hidden = false;
    err("e-project"); err("e-other"); show(0);
  }
  sheet.addEventListener("mhcr:open", () => { if (!done.hidden) reset(); else show(steps[1].hidden ? 0 : 1); });

  sheet.addEventListener("change", (e) => {
    if (e.target.name !== "project") return;
    err("e-project"); q(".chips").removeAttribute("aria-invalid");
    other.hidden = !e.target.hasAttribute("data-other");
    urgent.hidden = !e.target.hasAttribute("data-urgent");
    next.hidden = !urgent.hidden;                         // Emergency: "call us instead" first
    if (!other.hidden) q("#q-other").focus();
  });
  q("[data-continue]").addEventListener("click", () => { urgent.hidden = true; next.hidden = false; next.focus(); });

  function step1Ok() {
    const p = picked();
    if (!p) { err("e-project", "Please pick the kind of work."); q(".chips").setAttribute("aria-invalid", "true"); q("input[name=project]").focus(); return false; }
    if (p.hasAttribute("data-other") && q("#q-other").value.trim().length < 2) { err("e-other", "Please tell us what it is."); q("#q-other").focus(); return false; }
    err("e-other"); return true;
  }
  next.addEventListener("click", () => { if (step1Ok()) show(1); });
  q("[data-back]").addEventListener("click", () => show(0));
  if (!isForm) return;

  /* ---- with a form service: validate, send, show the result in place ---- */
  const digits = (v) => v.replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
  const RULES = { name: (v) => v.trim().length >= 2 || "Please add your name.",
                  phone: (v) => digits(v).length === 10 || "Please enter a 10-digit phone number." };
  const check = (n) => { const el = box.elements[n], r = RULES[n](el.value), bad = r !== true;
    el.setAttribute("aria-invalid", String(bad)); err(`e-${n}`, bad ? r : ""); return !bad; };
  ["name", "phone"].forEach((n) => box.elements[n].addEventListener("blur", () => { if (box.elements[n].value) check(n); }));
  box.addEventListener("submit", (e) => {
    e.preventDefault();
    if (steps[1].hidden) { if (step1Ok()) show(1); return; }           // Enter on step 1 = Next
    const bad = ["name", "phone"].filter((n) => !check(n));
    if (bad.length) { box.elements[bad[0]].focus(); return; }
    if (box.elements.website.value) return;                // honeypot: a bot filled it
    const btn = box.querySelector("[type=submit]"), label = btn.textContent, data = new FormData(box);
    const fail = q("[data-send-error]");
    btn.disabled = true; btn.textContent = "Sending…"; fail.textContent = "";
    fetch(box.action, { method: "POST", body: data, headers: { Accept: "application/json" } })
      .then((r) => { if (!r.ok) throw new Error(r.status); box.hidden = true; done.hidden = false; done.focus(); })
      .catch(() => { fail.textContent = fail.dataset.msg; })
      .finally(() => { btn.disabled = false; btn.textContent = label; });
  });
})();
