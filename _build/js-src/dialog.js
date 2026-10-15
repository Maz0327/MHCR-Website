/* Site dialogs (the quote sheet #quote and the phone menu #menu), on every page. No deps.
   Open: any [aria-controls="<dialog id>"] button, or any link to "#<dialog id>" on this page (e.g. "Get a free quote").
   showModal() gives the focus trap and Esc. Also: tap on the backdrop closes, [data-close] closes, and the phone's
   back button closes (one history entry is pushed on open and popped on close). Focus returns to the opener.
   Links inside the menu close it without the history pop, so they navigate (other pages) or jump (#jobs).
   A page loaded with #quote in the URL opens the sheet. */
(() => {
  "use strict";
  const state = new WeakMap(); // dialog -> { opener, pushed }
  const isDialog = (el) => el && el.tagName === "DIALOG" && typeof el.showModal === "function";
  function open(dlg, opener) {
    if (!isDialog(dlg) || dlg.open) return;
    dlg.showModal();
    let pushed = false;
    try { history.pushState({ mhcrDialog: dlg.id }, ""); pushed = true; } catch (_) { /* sandboxed: Esc/Close still work */ }
    state.set(dlg, { opener, pushed });
    if (opener && opener.hasAttribute("aria-expanded")) opener.setAttribute("aria-expanded", "true");
    dlg.dispatchEvent(new CustomEvent("mhcr:open", { detail: { opener } }));
  }
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[aria-controls], a[href^='#']");
    if (!t) return;
    const id = t.getAttribute("aria-controls") || t.getAttribute("href").slice(1);
    const dlg = id && document.getElementById(id);
    if (!isDialog(dlg)) return;
    e.preventDefault();
    open(dlg, t);
  });
  document.querySelectorAll("dialog").forEach((dlg) => {
    dlg.addEventListener("click", (e) => {
      if (e.target === dlg) dlg.close();                                  // backdrop
      else if (e.target.closest("[data-close]")) dlg.close();
      else if (dlg.id === "menu" && e.target.closest("a")) {            // menu link: close, then follow it
        // No history.back() on close here: it would cancel the link (another page) or undo the jump (#jobs).
        const st = state.get(dlg); if (st) st.pushed = false;
        dlg.close();
      }
    });
    dlg.addEventListener("close", () => {
      const s = state.get(dlg); if (!s) return;
      state.delete(dlg);
      if (s.pushed) history.back();
      if (s.opener) { if (s.opener.hasAttribute("aria-expanded")) s.opener.setAttribute("aria-expanded", "false"); s.opener.focus(); }
    });
  });
  addEventListener("popstate", () => {
    document.querySelectorAll("dialog[open]").forEach((dlg) => { const s = state.get(dlg); if (s) s.pushed = false; dlg.close(); });
  });
  if (location.hash === "#quote") open(document.getElementById("quote"), null);
  window.MHCRDialog = { open };
})();
