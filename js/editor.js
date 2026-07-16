/**
 * MHCR Inline Content Editor  v4.0
 * ─────────────────────────────────────────────────────────────────────────────
 * Only activates on localhost / 127.0.0.1 — safe to deploy to production.
 *
 * Modes:
 *  ✏  Text   — click any text element to edit it in place
 *  🎨 Style  — click any element to open a live style panel
 *              Colors, Spacing, Typography, Alignment, Size, Margin, Layout, Position
 *
 * Auto-save:
 *  • Folder handle is stored in IndexedDB — pick it once, never again
 *  • 1.5 s debounce after any change → silently writes the correct .html file
 *  • Status indicator: ● unsaved → ● saving… → ✓ saved → ✕ save failed
 *  • Folder validation on connect — checks file exists before enabling
 *
 * Saving:
 *  Chrome/Edge  → File System Access API (auto-save + manual save)
 *  Safari/FF    → "Download HTML" fallback (no auto-save)
 */

(function () {
  'use strict';

  /* ── Guard: localhost only ─────────────────────────────────────────────── */
  const host = window.location.hostname;
  if (host !== 'localhost' && host !== '127.0.0.1' && !host.match(/^192\.168\./)) return;

  /* ── State ─────────────────────────────────────────────────────────────── */
  let editMode     = false;
  let activeMode   = 'text';
  let dirHandle    = null;
  let undoStack    = [];
  let changeCount  = 0;
  let activeTextEl = null;
  let styleTarget  = null;
  let toastTimer   = null;
  let autoSaveTimer = null;

  const HAS_FSA = 'showDirectoryPicker' in window;
  const AUTO_SAVE_DELAY = 1500; // ms after last change before writing to disk

  /* ── IndexedDB — persist folder handle across sessions ─────────────────── */
  const IDB_NAME  = 'mhcr-editor-v1';
  const IDB_STORE = 'handles';
  const IDB_KEY   = 'dirHandle';

  function openIDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(IDB_NAME, 1);
      req.onupgradeneeded = () => req.result.createObjectStore(IDB_STORE);
      req.onsuccess  = () => resolve(req.result);
      req.onerror    = () => reject(req.error);
    });
  }

  async function persistHandle(handle) {
    try {
      const db = await openIDB();
      const tx = db.transaction(IDB_STORE, 'readwrite');
      tx.objectStore(IDB_STORE).put(handle, IDB_KEY);
      return new Promise((res, rej) => { tx.oncomplete = res; tx.onerror = () => rej(tx.error); });
    } catch (_) {}
  }

  async function restoreHandle() {
    try {
      const db = await openIDB();
      return new Promise((resolve) => {
        const tx  = db.transaction(IDB_STORE, 'readonly');
        const req = tx.objectStore(IDB_STORE).get(IDB_KEY);
        req.onsuccess = () => resolve(req.result || null);
        req.onerror   = () => resolve(null);
      });
    } catch (_) { return null; }
  }

  async function clearStoredHandle() {
    try {
      const db = await openIDB();
      const tx = db.transaction(IDB_STORE, 'readwrite');
      tx.objectStore(IDB_STORE).delete(IDB_KEY);
    } catch (_) {}
  }

  /** Verify / re-request readwrite permission on a handle. Requires user gesture. */
  async function verifyPermission(handle) {
    if (!handle) return false;
    try {
      const opts = { mode: 'readwrite' };
      if (await handle.queryPermission(opts) === 'granted') return true;
      if (await handle.requestPermission(opts) === 'granted') return true;
    } catch (_) {}
    return false;
  }

  /* ── Selectors ─────────────────────────────────────────────────────────── */
  const TEXT_SEL = [
    'h1','h2','h3','h4','h5','h6','p','li','blockquote','td','th',
    '.section-label','.section-title','.section-subtitle',
    '.hero-title','.hero-subtitle','.hero-description',
    '.testimonial-text','.author-name','.author-location',
    '.service-card h3','.service-card p',
    '.btn-primary','.btn-secondary','.btn-accent',
    '.cta-title','.cta-subtitle','.step-card p','.benefit-item p',
  ].join(',');

  const SKIP_CLOSEST = [
    'nav','footer','.top-bar','.nav-menu',
    '#editor-toggle','#editor-toolbar','#editor-toast','#ed-style-panel',
    'script','style',
  ];

  /* ── Style panel sections ─────────────────────────────────────────────── */
  const STYLE_SECTIONS = [
    {
      title: 'Colors',
      rows: [
        { label: 'Background', prop: 'backgroundColor', type: 'color' },
        { label: 'Text',       prop: 'color',           type: 'color' },
        { label: 'Border',     prop: 'borderColor',     type: 'color' },
      ],
    },
    {
      title: 'Spacing',
      rows: [
        { label: 'Pad Top',    prop: 'paddingTop',    type: 'px', min:0, max:80 },
        { label: 'Pad Right',  prop: 'paddingRight',  type: 'px', min:0, max:80 },
        { label: 'Pad Bottom', prop: 'paddingBottom', type: 'px', min:0, max:80 },
        { label: 'Pad Left',   prop: 'paddingLeft',   type: 'px', min:0, max:80 },
        { label: 'Radius',     prop: 'borderRadius',  type: 'px', min:0, max:48 },
        { label: 'Gap',        prop: 'gap',           type: 'px', min:0, max:64 },
      ],
    },
    {
      title: 'Typography',
      rows: [
        { label: 'Font Size',   prop: 'fontSize',      type: 'px',    min:8,  max:72 },
        { label: 'Weight',      prop: 'fontWeight',    type: 'select', options:['300','400','500','600','700','800','900'] },
        { label: 'Line Height', prop: 'lineHeight',    type: 'float', min:1,  max:3,  step:0.05 },
        { label: 'Tracking',   prop: 'letterSpacing',  type: 'px',    min:-2, max:12, step:0.5 },
      ],
    },
    {
      title: 'Alignment',
      rows: [
        { label: 'Text Align', prop: 'textAlign', type: 'buttons', options: [
          { value: 'left',    label: '⫷' },
          { value: 'center',  label: '☰' },
          { value: 'right',   label: '⫸' },
          { value: 'justify', label: '⊞' },
        ]},
      ],
    },
    {
      title: 'Size',
      rows: [
        { label: 'Width',     prop: 'width',    type: 'px', min:0, max:1200 },
        { label: 'Height',    prop: 'height',   type: 'px', min:0, max:1200 },
        { label: 'Min Width', prop: 'minWidth', type: 'px', min:0, max:1200 },
        { label: 'Max Width', prop: 'maxWidth', type: 'px', min:0, max:1200 },
      ],
    },
    {
      title: 'Margin',
      rows: [
        { label: 'Top',    prop: 'marginTop',    type: 'px', min:-100, max:200 },
        { label: 'Right',  prop: 'marginRight',  type: 'px', min:-100, max:200 },
        { label: 'Bottom', prop: 'marginBottom', type: 'px', min:-100, max:200 },
        { label: 'Left',   prop: 'marginLeft',   type: 'px', min:-100, max:200 },
      ],
    },
    {
      title: 'Layout',
      rows: [
        { label: 'Display', prop: 'display', type: 'select',
          options: ['block','flex','grid','inline-block','inline','none'] },
        { label: 'Direction', prop: 'flexDirection', type: 'buttons', options: [
          { value: 'row',            label: '→' },
          { value: 'column',         label: '↓' },
          { value: 'row-reverse',    label: '←' },
          { value: 'column-reverse', label: '↑' },
        ]},
        { label: 'Wrap', prop: 'flexWrap', type: 'buttons', options: [
          { value: 'nowrap', label: 'No' },
          { value: 'wrap',   label: 'Wrap' },
        ]},
        { label: 'Justify', prop: 'justifyContent', type: 'buttons', options: [
          { value: 'flex-start',    label: '⫷' },
          { value: 'center',        label: '☰' },
          { value: 'flex-end',      label: '⫸' },
          { value: 'space-between', label: '⇔' },
        ]},
        { label: 'Align', prop: 'alignItems', type: 'buttons', options: [
          { value: 'flex-start', label: '⬆' },
          { value: 'center',    label: '⬌' },
          { value: 'flex-end',  label: '⬇' },
          { value: 'stretch',   label: '⇕' },
        ]},
      ],
    },
    {
      title: 'Position',
      rows: [
        { label: 'Position', prop: 'position', type: 'select',
          options: ['static','relative','absolute','fixed'] },
        { label: 'Top',  prop: 'top',  type: 'px', min:-200, max:200 },
        { label: 'Left', prop: 'left', type: 'px', min:-200, max:200 },
      ],
    },
  ];

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  CSS                                                                    */
  /* ═══════════════════════════════════════════════════════════════════════ */
  const CSS = `
    /* ── Toggle button ── */
    #editor-toggle {
      position:fixed; bottom:24px; right:24px; z-index:2147483647;
      display:flex; align-items:center; gap:8px; padding:10px 18px;
      border-radius:100px; background:#12151e; border:1px solid #2a2f42;
      color:#c8cdd8; font:500 13px/1 Inter,system-ui,sans-serif;
      cursor:pointer; box-shadow:0 4px 24px rgba(0,0,0,.5);
      transition:background .2s,border-color .2s,color .2s; user-select:none;
    }
    #editor-toggle:hover { background:#1a1f30; border-color:#E85A1B; color:#fff; }
    #editor-toggle.active { background:#E85A1B; border-color:#E85A1B; color:#fff; }
    #editor-toggle .ed-dot {
      width:8px; height:8px; border-radius:50%; background:#3d4460;
      transition:background .2s; flex-shrink:0;
    }
    #editor-toggle.active .ed-dot { background:rgba(255,255,255,.7); }

    /* ── Toolbar ── */
    #editor-toolbar {
      position:fixed; top:12px; left:50%; transform:translateX(-50%);
      z-index:2147483647; display:none; align-items:center; gap:6px;
      padding:8px 10px; border-radius:14px; background:#12151e;
      border:1px solid #2a2f42; box-shadow:0 8px 40px rgba(0,0,0,.6);
      font:500 12px/1 Inter,system-ui,sans-serif; white-space:nowrap;
    }
    #editor-toolbar.visible { display:flex; }
    .ed-label { color:#E85A1B; font-weight:700; font-size:11px; letter-spacing:.06em;
      text-transform:uppercase; padding-right:10px; border-right:1px solid #252a3a;
      margin-right:2px; user-select:none; }
    .ed-divider { width:1px; height:20px; background:#252a3a; margin:0 2px; }

    /* Mode buttons */
    .ed-mode-btn {
      display:flex; align-items:center; gap:5px; padding:5px 10px;
      border-radius:7px; border:1px solid #2a2f42; background:transparent;
      color:#6b7280; font:inherit; cursor:pointer;
      transition:background .15s,color .15s,border-color .15s;
    }
    .ed-mode-btn:hover { background:#1c2135; color:#d1d5db; border-color:#3a4060; }
    .ed-mode-btn.active { background:#1c2135; border-color:#E85A1B; color:#E85A1B; }

    /* Action buttons */
    .ed-btn {
      display:flex; align-items:center; gap:5px; padding:6px 11px;
      border-radius:8px; border:1px solid #2a2f42; background:transparent;
      color:#8892a4; font:inherit; cursor:pointer;
      transition:background .15s,color .15s,border-color .15s;
    }
    .ed-btn:hover:not(:disabled) { background:#1c2135; color:#fff; border-color:#3a4060; }
    .ed-btn.primary { background:#E85A1B; border-color:#E85A1B; color:#fff; }
    .ed-btn.primary:hover:not(:disabled) { background:#cf5019; }
    .ed-btn.danger  { color:#f87171; }
    .ed-btn.danger:hover:not(:disabled) { background:rgba(248,113,113,.1); border-color:#f87171; }
    .ed-btn:disabled { opacity:.35; cursor:not-allowed; }

    #ed-badge { background:#E85A1B; color:#fff; font-size:10px; font-weight:700;
      padding:2px 6px; border-radius:100px; min-width:18px; text-align:center;
      display:none; user-select:none; }

    /* ── Auto-save status ── */
    #ed-save-status {
      display:none; align-items:center; gap:5px;
      font-size:11px; padding:4px 9px; border-radius:6px;
      border:1px solid transparent; transition:all .3s;
    }
    #ed-save-status.pending { display:flex; color:#fbbf24; border-color:#2a2f42;
      background:rgba(251,191,36,.08); }
    #ed-save-status.saving  { display:flex; color:#60a5fa; border-color:#2a2f42;
      background:rgba(96,165,250,.08); }
    #ed-save-status.saved   { display:flex; color:#4ade80; border-color:#2a2f42;
      background:rgba(74,222,128,.08); }
    #ed-save-status.error   { display:flex; color:#f87171; border-color:rgba(248,113,113,.3);
      background:rgba(248,113,113,.08); }
    #ed-save-status .ed-status-dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; }
    #ed-save-status.pending .ed-status-dot { background:#fbbf24;
      animation:ed-pulse 1s ease-in-out infinite; }
    #ed-save-status.saving  .ed-status-dot { background:#60a5fa;
      animation:ed-pulse .6s ease-in-out infinite; }
    #ed-save-status.saved   .ed-status-dot { background:#4ade80; }
    #ed-save-status.error   .ed-status-dot { background:#f87171; }
    @keyframes ed-pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

    /* Folder chip */
    #ed-folder-chip {
      display:none; align-items:center; gap:5px; padding:4px 9px;
      border-radius:6px; background:rgba(74,222,128,.08);
      border:1px solid rgba(74,222,128,.2); color:#4ade80; font-size:11px;
    }
    #ed-folder-chip.visible { display:flex; }
    #ed-folder-chip button {
      background:none; border:none; color:#6b7280; cursor:pointer;
      font-size:10px; padding:0 0 0 4px; line-height:1;
    }
    #ed-folder-chip button:hover { color:#f87171; }

    /* ── Text editing highlights ── */
    .ed-text-target { outline:2px dashed rgba(232,90,27,.35)!important;
      outline-offset:3px!important; cursor:text!important; transition:outline-color .15s!important; }
    .ed-text-target:hover { outline-color:rgba(232,90,27,.8)!important; }
    [contenteditable="true"] { outline:2px solid #E85A1B!important;
      outline-offset:3px!important; cursor:text!important; min-height:1em; }

    /* ── Style mode highlights ── */
    .ed-style-hover { outline:2px dashed rgba(96,165,250,.4)!important;
      outline-offset:3px!important; cursor:crosshair!important; transition:outline-color .15s!important; }
    .ed-style-hover:hover { outline-color:rgba(96,165,250,.85)!important; }
    .ed-style-selected { outline:2px solid #60a5fa!important; outline-offset:3px!important; }

    /* ── Image overlay ── */
    .ed-img-wrap { position:relative; display:inline-block; }
    .ed-img-wrap.block { display:block; }
    .ed-img-overlay {
      position:absolute; inset:0; background:rgba(0,0,0,.55);
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      gap:6px; color:#fff; font:500 12px/1 Inter,system-ui,sans-serif;
      opacity:0; transition:opacity .2s; cursor:pointer; border-radius:inherit;
    }
    .ed-img-overlay:hover { opacity:1; }
    .ed-img-overlay svg { width:28px; height:28px; opacity:.9; }

    /* ── Style panel ── */
    #ed-style-panel {
      position:fixed; z-index:2147483646; width:272px;
      max-height:calc(100vh - 80px); overflow-y:auto;
      background:#12151e; border:1px solid #2a2f42; border-radius:14px;
      box-shadow:0 12px 48px rgba(0,0,0,.7);
      font:500 12px/1 Inter,system-ui,sans-serif; color:#c8cdd8; display:none;
    }
    #ed-style-panel.visible { display:block; }
    #ed-style-panel::-webkit-scrollbar { width:4px; }
    #ed-style-panel::-webkit-scrollbar-thumb { background:#2a2f42; border-radius:2px; }

    .ed-panel-header {
      display:flex; align-items:center; justify-content:space-between;
      padding:12px 14px; border-bottom:1px solid #1e2336;
      position:sticky; top:0; background:#12151e; border-radius:14px 14px 0 0; z-index:1;
    }
    .ed-panel-tag { font-size:11px; color:#60a5fa; font-weight:600; letter-spacing:.04em;
      text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:160px; }
    .ed-panel-actions { display:flex; gap:4px; flex-shrink:0; }
    .ed-panel-btn { padding:4px 8px; border-radius:6px; border:1px solid #2a2f42;
      background:transparent; color:#8892a4; font:inherit; cursor:pointer; font-size:11px;
      transition:background .15s,color .15s; }
    .ed-panel-btn:hover { background:#1c2135; color:#fff; }

    .ed-section { padding:10px 14px; border-bottom:1px solid #1a1f2e; }
    .ed-section:last-child { border-bottom:none; padding-bottom:14px; }
    .ed-section-title { font-size:10px; font-weight:700; letter-spacing:.08em;
      text-transform:uppercase; color:#4b5563; margin-bottom:10px; }
    .ed-row { display:flex; align-items:center; gap:8px; margin-bottom:8px; }
    .ed-row:last-child { margin-bottom:0; }
    .ed-row-label { font-size:11px; color:#6b7280; min-width:76px; flex-shrink:0; }

    .ed-color-wrap { display:flex; align-items:center; gap:7px; flex:1; }
    .ed-color-swatch { width:20px; height:20px; border-radius:5px; border:1px solid #2a2f42;
      cursor:pointer; flex-shrink:0; overflow:hidden; position:relative; }
    .ed-color-swatch input[type=color] { position:absolute; inset:-4px;
      width:calc(100%+8px); height:calc(100%+8px); opacity:0; cursor:pointer; border:none; padding:0; }
    .ed-color-hex { flex:1; background:#1c2135; border:1px solid #2a2f42; border-radius:6px;
      color:#c8cdd8; font:500 11px/1 Inter,monospace; padding:4px 8px; width:0; min-width:0; }
    .ed-color-hex:focus { outline:none; border-color:#60a5fa; }

    .ed-slider-wrap { display:flex; align-items:center; gap:6px; flex:1; }
    .ed-slider { flex:1; -webkit-appearance:none; appearance:none; height:4px;
      border-radius:2px; background:#1e2336; outline:none; cursor:pointer; }
    .ed-slider::-webkit-slider-thumb { -webkit-appearance:none; width:14px; height:14px;
      border-radius:50%; background:#60a5fa; border:2px solid #12151e; cursor:pointer; }
    .ed-num { width:46px; background:#1c2135; border:1px solid #2a2f42; border-radius:6px;
      color:#c8cdd8; font:500 11px/1 Inter,system-ui,sans-serif; padding:4px 6px;
      text-align:right; flex-shrink:0; }
    .ed-num:focus { outline:none; border-color:#60a5fa; }

    .ed-select { flex:1; background:#1c2135; border:1px solid #2a2f42; border-radius:6px;
      color:#c8cdd8; font:500 11px/1 Inter,system-ui,sans-serif; padding:5px 8px;
      cursor:pointer; appearance:none; -webkit-appearance:none;
      background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%236b7280' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat:no-repeat; background-position:right 8px center; }
    .ed-select:focus { outline:none; border-color:#60a5fa; }

    /* ── Button-group control ── */
    .ed-btn-group { display:flex; gap:2px; flex:1; }
    .ed-btn-group .ed-btn-opt {
      flex:1; padding:5px 0; border:1px solid #2a2f42; border-radius:5px;
      background:transparent; color:#6b7280; font:500 11px/1 Inter,system-ui,sans-serif;
      cursor:pointer; text-align:center; transition:background .15s,color .15s,border-color .15s;
      min-width:0; overflow:hidden; white-space:nowrap;
    }
    .ed-btn-group .ed-btn-opt:hover { background:#1c2135; color:#d1d5db; border-color:#3a4060; }
    .ed-btn-group .ed-btn-opt.active { background:#1c2135; border-color:#60a5fa; color:#60a5fa; }

    /* ── Toast ── */
    #editor-toast {
      position:fixed; bottom:80px; right:24px; z-index:2147483647;
      padding:10px 16px; border-radius:10px;
      font:500 13px/1.4 Inter,system-ui,sans-serif; color:#fff;
      pointer-events:none; opacity:0; transform:translateY(6px);
      transition:opacity .22s,transform .22s; max-width:320px;
    }
    #editor-toast.show { opacity:1; transform:translateY(0); }
    #editor-toast.success { background:#14532d; border:1px solid #22c55e; }
    #editor-toast.error   { background:#450a0a; border:1px solid #f87171; }
    #editor-toast.info    { background:#0c1a3a; border:1px solid #60a5fa; }
  `;

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  Auto-save                                                              */
  /* ═══════════════════════════════════════════════════════════════════════ */

  /** Called after every change — sets a debounce timer then writes to disk */
  function scheduleAutoSave() {
    if (!HAS_FSA || !dirHandle) return;
    clearTimeout(autoSaveTimer);
    setAutoSaveStatus('pending');
    autoSaveTimer = setTimeout(async () => {
      // Re-check — dirHandle may have been nulled since the timer was set
      if (!dirHandle) {
        console.warn('[editor] autoSave: dirHandle is null when timer fired — skipping');
        setAutoSaveStatus('idle');
        return;
      }
      setAutoSaveStatus('saving');
      try {
        // Check permission before attempting save (queryPermission is non-blocking)
        const opts = { mode: 'readwrite' };
        const perm = await dirHandle.queryPermission(opts);
        if (perm !== 'granted') {
          // Permission was lost since edit mode was activated — can't re-request without user gesture
          toast('Folder access lost — click "Edit Mode" to reconnect', 'error', 6000);
          setAutoSaveStatus('error');
          setTimeout(() => setAutoSaveStatus('pending'), 8000);
          return;
        }
        const ok = await doSave(/* silent */ true);
        if (ok) {
          setAutoSaveStatus('saved');
          setTimeout(() => setAutoSaveStatus('idle'), 3000);
        } else {
          // doSave returned false — error toast already shown inside doSave
          setAutoSaveStatus('error');
          setTimeout(() => setAutoSaveStatus('pending'), 8000);
        }
      } catch (err) {
        // Catch any unexpected rejection from doSave itself
        console.error('[editor] scheduleAutoSave unhandled error:', err);
        toast(`Auto-save error: ${err.message}`, 'error', 6000);
        setAutoSaveStatus('error');
        setTimeout(() => setAutoSaveStatus('pending'), 8000);
      }
    }, AUTO_SAVE_DELAY);
  }

  function setAutoSaveStatus(status) {
    const el = document.getElementById('ed-save-status');
    if (!el) return;
    if (status === 'idle') {
      el.className = '';
      el.style.display = 'none';
      return;
    }
    const labels = { pending: '● Unsaved', saving: '● Saving…', saved: '✓ Saved', error: '✕ Save failed' };
    el.className = status;
    el.style.display = 'flex'; // explicitly override any inline display:none
    el.innerHTML = `<span class="ed-status-dot"></span>${labels[status] || status}`;
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  Boot                                                                   */
  /* ═══════════════════════════════════════════════════════════════════════ */
  async function boot() {
    injectCSS();
    buildToggle();
    buildToolbar();
    buildStylePanel();
    buildToast();

    // Try to restore folder handle from a previous session (no user gesture needed yet)
    if (HAS_FSA) {
      const stored = await restoreHandle();
      if (stored) {
        // Don't request permission yet — do it when user activates Edit Mode
        dirHandle = stored;
        showFolderChip(stored.name, /* connected= */ false);
      }
    }
  }

  /* ── Toggle button ── */
  function buildToggle() {
    const btn = el('button', { id: 'editor-toggle' }, `<span class="ed-dot"></span> Edit Mode`);
    btn.addEventListener('click', () => setEditMode(!editMode));
    document.body.appendChild(btn);
  }

  /* ── Toolbar ── */
  function buildToolbar() {
    const bar = el('div', { id: 'editor-toolbar' });
    bar.innerHTML = `
      <span class="ed-label">✏ Editing</span>
      <button class="ed-mode-btn active" id="ed-mode-text">✏ Text</button>
      <button class="ed-mode-btn"        id="ed-mode-style">🎨 Style</button>
      <span class="ed-divider"></span>
      <button class="ed-btn" id="ed-undo" disabled>↩ Undo</button>
      <span id="ed-badge"></span>
      <span class="ed-divider"></span>
      <div id="ed-folder-chip">
        <span id="ed-folder-label">📁 —</span>
        <button id="ed-folder-clear" title="Disconnect folder">✕</button>
      </div>
      ${HAS_FSA
        ? `<button class="ed-btn" id="ed-folder-pick">📁 Select Folder</button>`
        : ''
      }
      <span id="ed-save-status"></span>
      ${HAS_FSA
        ? `<button class="ed-btn primary" id="ed-save-manual" disabled>💾 Save</button>`
        : `<button class="ed-btn primary" id="ed-save-manual">⬇ Download</button>`
      }
      <span class="ed-divider"></span>
      <button class="ed-btn danger" id="ed-exit">✕</button>
    `;
    document.body.appendChild(bar);

    document.getElementById('ed-mode-text').addEventListener('click',  () => switchMode('text'));
    document.getElementById('ed-mode-style').addEventListener('click', () => switchMode('style'));
    document.getElementById('ed-undo').addEventListener('click', undo);
    document.getElementById('ed-save-manual').addEventListener('click', () => doSave(false));
    document.getElementById('ed-exit').addEventListener('click', () => setEditMode(false));
    document.getElementById('ed-folder-clear').addEventListener('click', disconnectFolder);
    if (HAS_FSA) {
      document.getElementById('ed-folder-pick').addEventListener('click', pickFolder);
    }
  }

  function buildStylePanel() {
    document.body.appendChild(el('div', { id: 'ed-style-panel' }));
  }

  function buildToast() {
    document.body.appendChild(el('div', { id: 'editor-toast' }));
  }

  /* ── Folder chip (shows connected folder name) ── */
  function showFolderChip(name, connected = true) {
    const chip      = document.getElementById('ed-folder-chip');
    const label     = document.getElementById('ed-folder-label');
    const pickBtn   = document.getElementById('ed-folder-pick');
    const saveBtn   = document.getElementById('ed-save-manual');

    if (!chip) return;
    chip.classList.add('visible');
    label.textContent = `📁 ${name}`;
    chip.title = connected ? `Auto-saving to: ${name}` : `${name} (click Edit Mode to reconnect)`;
    if (pickBtn) pickBtn.style.display = 'none';
    if (saveBtn && HAS_FSA) saveBtn.disabled = !connected;
  }

  function hideFolderChip() {
    const chip    = document.getElementById('ed-folder-chip');
    const pickBtn = document.getElementById('ed-folder-pick');
    const saveBtn = document.getElementById('ed-save-manual');
    if (chip) chip.classList.remove('visible');
    if (pickBtn) pickBtn.style.display = '';
    if (saveBtn && HAS_FSA) saveBtn.disabled = true;
  }

  async function disconnectFolder() {
    dirHandle = null;
    await clearStoredHandle();
    hideFolderChip();
    setAutoSaveStatus('idle');
    clearTimeout(autoSaveTimer);
    toast('Folder disconnected', 'info');
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  Edit mode                                                              */
  /* ═══════════════════════════════════════════════════════════════════════ */
  async function setEditMode(on) {
    editMode = on;
    const toggle  = document.getElementById('editor-toggle');
    const toolbar = document.getElementById('editor-toolbar');

    toggle.classList.toggle('active', on);
    toggle.innerHTML = `<span class="ed-dot"></span> ${on ? 'Editing…' : 'Edit Mode'}`;
    toolbar.classList.toggle('visible', on);

    if (on) {
      // Activate mode (this IS a user gesture — safe to request FSA permission)
      console.log('[editor] setEditMode ON — dirHandle:', dirHandle ? dirHandle.name : 'null');
      if (HAS_FSA && dirHandle) {
        const ok = await verifyPermission(dirHandle);
        console.log('[editor] verifyPermission result:', ok);
        if (ok) {
          const valid = await validateFolder(dirHandle);
          console.log('[editor] validateFolder result:', valid, '— dirHandle now:', dirHandle ? dirHandle.name : 'null');
          if (valid) {
            showFolderChip(dirHandle.name, true);
            toast(`Auto-save connected to "${dirHandle.name}" → ${currentFilePath()}`, 'success', 4000);
          }
        } else {
          dirHandle = null;
          hideFolderChip();
          toast('Folder permission denied — pick the folder again', 'info', 4000);
        }
      }
      switchMode(activeMode);
      console.log('[editor] edit mode ready — dirHandle:', dirHandle ? dirHandle.name : 'null');
      if (!dirHandle) {
        toast('Click text or images to edit — pick a folder to enable auto-save', 'info', 5000);
      }
    } else {
      teardownAll();
    }
  }

  function switchMode(mode) {
    activeMode = mode;
    document.getElementById('ed-mode-text').classList.toggle('active',  mode === 'text');
    document.getElementById('ed-mode-style').classList.toggle('active', mode === 'style');
    teardownAll();
    if (mode === 'text')  { attachTextTargets(); wrapImages(); }
    else                  { attachStyleTargets(); }
  }

  function teardownAll() {
    detachTextTargets(); unwrapImages(); detachStyleTargets(); closeStylePanel(); blurActive();
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  TEXT MODE                                                              */
  /* ═══════════════════════════════════════════════════════════════════════ */
  function attachTextTargets() {
    getTextEls().forEach(t => { t.classList.add('ed-text-target'); t.addEventListener('click', onTextClick); });
  }
  function detachTextTargets() {
    document.querySelectorAll('.ed-text-target').forEach(t => {
      t.classList.remove('ed-text-target'); t.removeAttribute('contenteditable');
      t.removeEventListener('click', onTextClick);
    });
  }
  function getTextEls() {
    return Array.from(document.querySelectorAll(TEXT_SEL)).filter(t => {
      if (SKIP_CLOSEST.some(s => t.closest(s))) return false;
      return (t.innerText || '').trim().length > 0;
    });
  }
  function onTextClick(e) {
    if (!editMode || activeMode !== 'text') return;
    const t = e.currentTarget;
    if (t === activeTextEl) return;
    blurActive();
    t.dataset.edOrig = t.dataset.edOrig ?? t.innerHTML;
    t.setAttribute('contenteditable', 'true');
    t.addEventListener('blur',    onTextBlur,    { once: true });
    t.addEventListener('keydown', onTextKeydown);
    t.focus(); activeTextEl = t; e.stopPropagation();
  }
  function onTextBlur(e) {
    const t = e.currentTarget;
    const oldVal = t.dataset.edOrig, newVal = t.innerHTML;
    if (oldVal !== newVal) { pushUndo(t, 'innerHTML', oldVal, newVal); t.dataset.edOrig = newVal; }
    t.removeAttribute('contenteditable'); t.removeEventListener('keydown', onTextKeydown);
    if (activeTextEl === t) activeTextEl = null;
  }
  function onTextKeydown(e) {
    if (e.key === 'Escape') { const t = e.currentTarget; t.innerHTML = t.dataset.edOrig ?? t.innerHTML; t.blur(); }
    if (e.key === 'Enter' && !e.shiftKey) {
      const tag = e.currentTarget.tagName.toLowerCase();
      if (!['p','li','blockquote','td','th'].includes(tag)) { e.preventDefault(); e.currentTarget.blur(); }
    }
  }
  function blurActive() {
    if (!activeTextEl) return;
    const t = activeTextEl;
    activeTextEl = null; // clear BEFORE .blur() — blur fires onTextBlur which also nulls this
    t.blur();
    t.removeAttribute('contenteditable');
    t.removeEventListener('keydown', onTextKeydown);
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  IMAGE REPLACEMENT                                                      */
  /* ═══════════════════════════════════════════════════════════════════════ */
  function wrapImages() {
    getImgEls().forEach(img => {
      if (img.closest('.ed-img-wrap')) return;
      const display = window.getComputedStyle(img).display;
      const wrap = el('div', { class: `ed-img-wrap${display === 'block' ? ' block' : ''}` });
      img.parentNode.insertBefore(wrap, img); wrap.appendChild(img);
      const overlay = el('div', { class: 'ed-img-overlay' }, `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg><span>Replace Image</span>
      `);
      overlay.addEventListener('click', () => pickImage(img));
      wrap.appendChild(overlay);
    });
  }
  function unwrapImages() {
    document.querySelectorAll('.ed-img-wrap').forEach(wrap => {
      const img = wrap.querySelector('img');
      if (img) wrap.replaceWith(img); else wrap.remove();
    });
  }
  function getImgEls() {
    return Array.from(document.querySelectorAll('img')).filter(img => {
      if (SKIP_CLOSEST.some(s => img.closest(s))) return false;
      if (img.closest('#editor-toolbar') || img.closest('#editor-toggle')) return false;
      const r = img.getBoundingClientRect(); return r.width >= 48 && r.height >= 48;
    });
  }
  function pickImage(img) {
    const input = el('input', { type: 'file', accept: 'image/*' });
    input.addEventListener('change', async () => {
      const file = input.files[0]; if (!file) return;
      const oldSrc = img.getAttribute('src');
      if (dirHandle) {
        try {
          const newSrc = await saveImgToDisk(file);
          pushUndo(img, 'src', oldSrc, newSrc);
          img.src = newSrc; if (img.dataset.src) img.dataset.src = newSrc;
          scheduleAutoSave();
          toast(`Image saved → images/uploads/${file.name}`, 'success');
        } catch (err) { previewImgBlob(img, file, oldSrc); }
      } else {
        previewImgBlob(img, file, oldSrc);
        toast('Image previewed — pick a 📁 folder to auto-save', 'info', 5000);
      }
    });
    input.click();
  }
  function previewImgBlob(img, file, oldSrc) {
    pushUndo(img, 'src', oldSrc, URL.createObjectURL(file)); img.src = URL.createObjectURL(file);
  }
  async function saveImgToDisk(file) {
    let dir = dirHandle;
    try { dir = await dirHandle.getDirectoryHandle('images', { create: true });
          dir = await dir.getDirectoryHandle('uploads', { create: true }); } catch (_) {}
    const safe = file.name.replace(/[^a-zA-Z0-9._-]/g, '-');
    const fh = await dir.getFileHandle(safe, { create: true });
    const wr = await fh.createWritable(); await wr.write(file); await wr.close();
    return `${'../'.repeat(pageDepth())}images/uploads/${safe}`;
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  STYLE MODE                                                             */
  /* ═══════════════════════════════════════════════════════════════════════ */
  function attachStyleTargets() {
    document.addEventListener('mouseover', onStyleHover);
    document.addEventListener('mouseout',  onStyleOut);
    document.addEventListener('click',     onStyleClick, true);
  }
  function detachStyleTargets() {
    document.removeEventListener('mouseover', onStyleHover);
    document.removeEventListener('mouseout',  onStyleOut);
    document.removeEventListener('click',     onStyleClick, true);
    document.querySelectorAll('.ed-style-hover,.ed-style-selected').forEach(t =>
      t.classList.remove('ed-style-hover','ed-style-selected'));
  }
  function onStyleHover(e) {
    if (!editMode || activeMode !== 'style' || shouldSkip(e.target)) return;
    e.target.classList.add('ed-style-hover');
  }
  function onStyleOut(e) { if (e.target !== styleTarget) e.target.classList.remove('ed-style-hover'); }
  function onStyleClick(e) {
    if (!editMode || activeMode !== 'style' || shouldSkip(e.target)) return;
    e.stopPropagation(); e.preventDefault(); openStylePanel(e.target);
  }
  function shouldSkip(t) { return SKIP_CLOSEST.some(s => t.closest && t.closest(s)); }

  function openStylePanel(target) {
    if (styleTarget && styleTarget !== target) styleTarget.classList.remove('ed-style-selected','ed-style-hover');
    styleTarget = target;
    styleTarget.classList.add('ed-style-selected'); styleTarget.classList.remove('ed-style-hover');
    const panel = document.getElementById('ed-style-panel');
    renderPanel(panel, target); panel.classList.add('visible'); positionPanel(panel, target);
  }
  function closeStylePanel() {
    const panel = document.getElementById('ed-style-panel');
    if (panel) panel.classList.remove('visible');
    if (styleTarget) { styleTarget.classList.remove('ed-style-selected','ed-style-hover'); styleTarget = null; }
  }
  function positionPanel(panel, target) {
    const pr = target.getBoundingClientRect(), vw = window.innerWidth, vh = window.innerHeight, pw = 272, gap = 12;
    let left = pr.right + gap + pw < vw ? pr.right + gap :
               pr.left - gap - pw > 0  ? pr.left - gap - pw : Math.max(8, vw - pw - 8);
    let top  = Math.max(60, Math.min(pr.top, vh - 300));
    panel.style.left = left + 'px'; panel.style.top = top + 'px';
    requestAnimationFrame(() => {
      top = Math.max(60, Math.min(pr.top, vh - panel.offsetHeight - 16));
      panel.style.top = top + 'px';
    });
  }

  function renderPanel(panel, target) {
    const computed = window.getComputedStyle(target);
    let html = `
      <div class="ed-panel-header">
        <span class="ed-panel-tag">${elementLabel(target)}</span>
        <div class="ed-panel-actions">
          <button class="ed-panel-btn" id="ed-panel-up">↑ Up</button>
          <button class="ed-panel-btn" id="ed-panel-close">✕</button>
        </div>
      </div>`;
    STYLE_SECTIONS.forEach(section => {
      html += `<div class="ed-section"><div class="ed-section-title">${section.title}</div>`;
      section.rows.forEach(row => { html += buildControl(row, computed, target); });
      html += `</div>`;
    });
    panel.innerHTML = html;

    panel.querySelector('#ed-panel-up').addEventListener('click', e => {
      e.stopPropagation();
      const p = styleTarget?.parentElement;
      if (p && p !== document.body && !shouldSkip(p)) openStylePanel(p);
    });
    panel.querySelector('#ed-panel-close').addEventListener('click', e => { e.stopPropagation(); closeStylePanel(); });

    // Wire all controls
    panel.querySelectorAll('[data-prop]').forEach(input => {
      const prop = input.dataset.prop, type = input.dataset.type;
      if (type === 'color') {
        const swatch   = panel.querySelector(`input[type=color][data-prop="${prop}"]`);
        const hexInput = panel.querySelector(`input.ed-color-hex[data-prop="${prop}"]`);
        if (!swatch || !hexInput) return;
        swatch.addEventListener('input', () => { hexInput.value = swatch.value; applyStyle(styleTarget, prop, swatch.value); });
        hexInput.addEventListener('input', () => {
          if (/^#[0-9a-fA-F]{6}$/.test(hexInput.value)) { swatch.value = hexInput.value; applyStyle(styleTarget, prop, hexInput.value); }
        });
        hexInput.addEventListener('change', () => {
          const v = hexInput.value.trim().replace(/^(?!#)/, '#');
          if (/^#[0-9a-fA-F]{6}$/.test(v)) { hexInput.value = v; swatch.value = v; applyStyle(styleTarget, prop, v); }
        });
      } else if (type === 'range') {
        const slider = panel.querySelector(`input[type=range][data-prop="${prop}"]`);
        const numIn  = panel.querySelector(`input.ed-num[data-prop="${prop}"]`);
        const unit   = input.dataset.unit || '';
        const sync = v => { slider.value = v; numIn.value = v; applyStyle(styleTarget, prop, v + unit); };
        slider.addEventListener('input', () => sync(slider.value));
        numIn.addEventListener('change', () => sync(numIn.value));
        numIn.addEventListener('input',  () => sync(numIn.value));
      } else if (type === 'select') {
        input.addEventListener('change', () => applyStyle(styleTarget, prop, input.value));
      }
    });

    // Wire button-group controls (alignment, flex direction, etc.)
    panel.querySelectorAll('.ed-btn-group').forEach(group => {
      const buttons = group.querySelectorAll('.ed-btn-opt');
      buttons.forEach(btn => {
        btn.addEventListener('click', e => {
          e.stopPropagation();
          const prop = btn.dataset.prop;
          const value = btn.dataset.value;
          buttons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          applyStyle(styleTarget, prop, value);
        });
      });
    });
  }

  function buildControl(row, computed, target) {
    const { label, prop, type } = row;
    if (type === 'color') {
      const raw = computed[prop] || '', hex = raw ? rgbToHex(raw) : '#000000';
      const cur = target.style[prop] ? rgbToHex(target.style[prop]) : hex;
      return `<div class="ed-row">
        <span class="ed-row-label">${label}</span>
        <div class="ed-color-wrap">
          <div class="ed-color-swatch" style="background:${cur}">
            <input type="color" data-prop="${prop}" data-type="color" value="${cur}">
          </div>
          <input class="ed-color-hex" data-prop="${prop}" data-type="color" value="${cur}" maxlength="7" spellcheck="false">
        </div></div>`;
    }
    if (type === 'px' || type === 'float') {
      const raw = parseFloat(computed[prop]) || 0;
      const cur = target.style[prop] ? parseFloat(target.style[prop]) : raw;
      const { min=0, max=100, step=type==='float'?.05:1 } = row;
      const unit = type === 'px' ? 'px' : '';
      return `<div class="ed-row">
        <span class="ed-row-label">${label}</span>
        <div class="ed-slider-wrap">
          <input class="ed-slider" type="range" data-prop="${prop}" data-type="range" data-unit="${unit}"
            min="${min}" max="${max}" step="${step}" value="${cur}">
          <input class="ed-num" type="number" data-prop="${prop}" data-type="range" data-unit="${unit}"
            min="${min}" max="${max}" step="${step}" value="${cur}">
        </div></div>`;
    }
    if (type === 'select') {
      const cur = computed[prop];
      const opts = (row.options||[]).map(o =>
        `<option value="${o}"${Math.round(parseFloat(cur))===parseInt(o)||cur===o?' selected':''}>${o}</option>`).join('');
      return `<div class="ed-row">
        <span class="ed-row-label">${label}</span>
        <select class="ed-select" data-prop="${prop}" data-type="select">${opts}</select></div>`;
    }
    if (type === 'buttons') {
      const cur = target.style[prop] || computed[prop] || '';
      const btns = (row.options || []).map(o =>
        `<button class="ed-btn-opt${cur === o.value ? ' active' : ''}"
           data-prop="${prop}" data-type="buttons" data-value="${o.value}"
           title="${o.value}">${o.label}</button>`
      ).join('');
      return `<div class="ed-row">
        <span class="ed-row-label">${label}</span>
        <div class="ed-btn-group">${btns}</div></div>`;
    }
    return '';
  }

  function applyStyle(target, prop, value) {
    if (!target) return;
    const old = target.style[prop];
    target.style[prop] = value;
    if (old !== target.style[prop]) pushUndo(target, `style:${prop}`, old, target.style[prop]);
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  UNDO                                                                   */
  /* ═══════════════════════════════════════════════════════════════════════ */
  function pushUndo(target, field, oldVal, newVal) {
    undoStack.push({ target, field, oldVal, newVal });
    changeCount++;
    syncUI();
    scheduleAutoSave(); // trigger auto-save on every change
  }

  function undo() {
    if (!undoStack.length) return;
    const { target, field, oldVal } = undoStack.pop();
    if (field === 'innerHTML')           target.innerHTML = oldVal;
    else if (field === 'src')            target.src = oldVal;
    else if (field.startsWith('style:')) target.style[field.slice(6)] = oldVal;
    changeCount = Math.max(0, changeCount - 1);
    syncUI();
    if (styleTarget === target) { const p = document.getElementById('ed-style-panel'); renderPanel(p, target); }
    scheduleAutoSave();
    toast('Change undone', 'info');
  }

  function syncUI() {
    const badge = document.getElementById('ed-badge'), undoBtn = document.getElementById('ed-undo');
    if (!badge || !undoBtn) return;
    undoBtn.disabled = undoStack.length === 0;
    badge.textContent = changeCount; badge.style.display = changeCount > 0 ? 'inline-block' : 'none';
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  FOLDER PICKER + SAVE                                                   */
  /* ═══════════════════════════════════════════════════════════════════════ */
  async function pickFolder() {
    try {
      console.log('[editor] pickFolder: opening directory picker…');
      const handle = await window.showDirectoryPicker({ mode: 'readwrite' });
      console.log('[editor] pickFolder: user selected folder:', handle.name);
      dirHandle = handle;
      await persistHandle(handle);
      console.log('[editor] pickFolder: handle persisted, validating…');
      const valid = await validateFolder(handle);
      console.log('[editor] pickFolder: validation result:', valid);
      if (!valid) return; // validateFolder shows its own error toast
      showFolderChip(handle.name, true);
      toast(`"${handle.name}" connected — auto-save enabled`, 'success');
      console.log('[editor] pickFolder: ✓ folder connected, auto-save ready');
      if (changeCount > 0) scheduleAutoSave();
    } catch (e) {
      console.error('[editor] pickFolder error:', e);
      if (e.name !== 'AbortError') toast('Could not access folder', 'error');
    }
  }

  /** Check that the connected folder actually contains the current HTML file.
   *  Returns true if valid, false + shows toast if not. */
  async function validateFolder(handle) {
    try {
      const filePath = currentFilePath();
      const parts = filePath.split('/').filter(Boolean);
      const filename = parts.pop() || 'index.html';
      const subdirs = parts.slice(); // copy for logging
      console.log('[editor] validateFolder: looking for', filePath, '→ subdirs:', subdirs, '→ file:', filename);
      let dir = handle;
      for (const p of parts) {
        console.log('[editor] validateFolder: traversing into subdir:', p);
        dir = await dir.getDirectoryHandle(p, { create: false });
      }
      await dir.getFileHandle(filename, { create: false });
      console.log('[editor] validateFolder: ✓ found', filename);
      return true;
    } catch (err) {
      console.error('[editor] validateFolder error:', err.name, err.message);
      if (err.name === 'NotFoundError') {
        const expected = currentFilePath();
        toast(`Wrong folder — "${handle.name}" doesn't contain "${expected}". Select the folder that has index.html at its root.`, 'error', 10000);
        dirHandle = null;
        await clearStoredHandle();
        hideFolderChip();
      } else {
        toast(`Folder validation failed: ${err.message}`, 'error', 6000);
      }
      return false;
    }
  }

  /** Core save function. silent=true → no toast on success */
  async function doSave(silent = false) {
    if (!HAS_FSA) {
      // Download fallback
      const a = el('a', { href: URL.createObjectURL(new Blob([cleanHTML()],{type:'text/html'})), download: currentFilename() });
      a.click(); if (!silent) toast(`Downloaded: ${currentFilename()}`, 'success');
      return true;
    }
    if (!dirHandle) { if (!silent) toast('Pick a folder first (📁)', 'error'); return false; }
    try {
      blurActive();
      const filePath = currentFilePath();
      const parts = filePath.split('/').filter(Boolean);
      const filename = parts.pop() || 'index.html';
      console.log('[editor] doSave: saving', filePath, '→ file:', filename, 'silent:', silent);
      let dir = dirHandle;
      for (const p of parts) dir = await dir.getDirectoryHandle(p, { create: false });
      const fh = await dir.getFileHandle(filename, { create: false });
      const wr = await fh.createWritable(); await wr.write(cleanHTML()); await wr.close();
      console.log('[editor] doSave: ✓ wrote', filename);
      if (!silent) { undoStack = []; changeCount = 0; syncUI(); toast(`✓ Saved: ${filename}`, 'success'); }
      return true;
    } catch (err) {
      console.error('[editor] doSave error:', err.name, err.message, err);
      const msg = err.name === 'NotFoundError'
        ? `File not found — make sure you selected the correct root folder (the one containing index.html)`
        : err.name === 'NotAllowedError'
        ? `Permission denied — click "Edit Mode" again to re-grant folder access`
        : `Save failed: ${err.message}`;
      toast(msg, 'error', 8000);
      return false;
    }
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  HTML SERIALISATION                                                     */
  /* ═══════════════════════════════════════════════════════════════════════ */
  function cleanHTML() {
    const clone = document.documentElement.cloneNode(true);
    ['editor-toggle','editor-toolbar','editor-toast','editor-styles','ed-style-panel']
      .forEach(id => clone.querySelector(`#${id}`)?.remove());
    clone.querySelectorAll('.ed-text-target,.ed-style-hover,.ed-style-selected')
      .forEach(t => t.classList.remove('ed-text-target','ed-style-hover','ed-style-selected'));
    clone.querySelectorAll('[contenteditable]').forEach(t => t.removeAttribute('contenteditable'));
    clone.querySelectorAll('[data-ed-orig]').forEach(t => delete t.dataset.edOrig);
    clone.querySelectorAll('.ed-img-wrap').forEach(wrap => {
      const img = wrap.querySelector('img');
      if (img) { delete img.dataset.pendingFile; wrap.replaceWith(img); } else wrap.remove();
    });
    return '<!DOCTYPE html>\n' + clone.outerHTML;
  }

  /* ═══════════════════════════════════════════════════════════════════════ */
  /*  UTILITIES                                                              */
  /* ═══════════════════════════════════════════════════════════════════════ */
  function rgbToHex(str) {
    const m = (str||'').match(/\d+/g);
    if (!m||m.length<3) return '#000000';
    return '#'+[m[0],m[1],m[2]].map(n=>parseInt(n).toString(16).padStart(2,'0')).join('');
  }
  function elementLabel(t) {
    const tag = t.tagName.toLowerCase(), id = t.id ? `#${t.id}` : '';
    const cls = Array.from(t.classList)
      .filter(c=>!['ed-style-hover','ed-style-selected','ed-text-target'].includes(c))
      .slice(0,2).map(c=>`.${c}`).join('');
    return `${tag}${id}${cls}`;
  }
  function currentFilePath() {
    let p = window.location.pathname.replace(/^\//,'');
    if (!p||p.endsWith('/')) p += 'index.html';
    if (!p.includes('.'))    p += '.html';
    return p;
  }
  function currentFilename() { return currentFilePath().split('/').pop(); }
  function pageDepth()       { return currentFilePath().split('/').length - 1; }

  function el(tag, attrs={}, html='') {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v]) => node.setAttribute(k,v));
    node.innerHTML = html; return node;
  }
  function injectCSS() {
    const style = el('style', { id: 'editor-styles' }); style.textContent = CSS;
    document.head.appendChild(style);
  }
  function toast(msg, type='info', ms=3200) {
    const t = document.getElementById('editor-toast'); if (!t) return;
    t.textContent = msg; t.className = `show ${type}`;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { t.className = ''; }, ms);
  }

  /* ── Init ── */
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

})();
