# MHCR Inline Content Editor — Changelog & Troubleshooting

**File:** `js/editor.js`
**Injected into:** All 32 HTML files via `<script src="js/editor.js">` (root) or `<script src="../js/editor.js">` (subdirectories)
**Activates on:** `localhost` / `127.0.0.1` / `192.168.*` only — invisible in production

---

## Version History

### v1.0 — Basic Text & Image Editing
- **Text Mode:** Click any heading, paragraph, list item, button, etc. to edit in-place via `contenteditable`
- **Image Replacement:** Hover any image → overlay appears → click to pick a new image file
- **Manual Save:** File System Access API (Chrome/Edge) writes directly to disk, or download fallback (Safari/Firefox)
- **Undo:** Tracks all text and image changes, reverts one at a time
- **Localhost guard:** Editor only loads on localhost — `<script>` tag can stay in production HTML

### v2.0 — Style Mode
- **Style panel:** Click any element in Style Mode to open a floating panel with live CSS controls
- **3 sections:** Colors (bg, text, border), Spacing (padding ×4, border-radius, gap), Typography (font-size, weight, line-height, letter-spacing)
- **Control types:** Color picker + hex input, range slider + number input, select dropdown
- **"↑ Up" button:** Navigate to parent element without leaving the panel
- **Positioning:** Panel auto-positions to the right of the target element, falls back left or screen-edge

### v3.0 — Auto-Save
- **IndexedDB persistence:** Folder handle stored in `mhcr-editor-v1` database — pick folder once, never again across page loads
- **1.5s debounced auto-save:** Every change triggers a debounce timer → silently writes the current page's HTML file to disk
- **Status indicator:** `● Unsaved` (yellow) → `● Saving…` (blue) → `✓ Saved` (green) in the toolbar
- **Folder chip:** Shows connected folder name with ✕ disconnect button
- **Permission re-verification:** On Edit Mode activation, calls `verifyPermission()` on restored handle (requires user gesture)

### v3.1 — Auto-Save Bug Fixes
- **`blurActive()` crash fix:** `.blur()` fires `onTextBlur` synchronously which sets `activeTextEl = null`, then `removeAttribute()` would crash on null. Fixed by saving reference before `.blur()` call.
- **Error visibility:** `doSave()` now always shows toast errors, even in silent/auto-save mode (previously suppressed)
- **`✕ Save failed` error state:** New red status indicator when auto-save fails, with descriptive error messages:
  - `NotFoundError` → "File not found — make sure you selected the correct root folder"
  - `NotAllowedError` → "Permission denied — click Edit Mode again to re-grant"
  - Generic → shows actual error message
- **Permission pre-check:** `scheduleAutoSave` calls `queryPermission()` before attempting save — if permission was lost, shows actionable error instead of cryptic failure
- **Null guard in timer:** Re-checks `dirHandle` when setTimeout fires (could have been nulled during the 1.5s delay)
- **Folder validation:** `validateFolder()` checks that the selected folder actually contains the expected HTML file. Shows clear error if wrong folder selected.

### v4.0 — Layout, Sizing & Alignment Controls
- **5 new style panel sections** (8 total):

| Section | Controls | Type |
|---------|----------|------|
| Alignment | textAlign (left/center/right/justify) | button group |
| Size | width, height, minWidth, maxWidth (0–1200px) | px sliders |
| Margin | marginTop/Right/Bottom/Left (-100 to 200px) | px sliders |
| Layout | display, flexDirection, flexWrap, justifyContent, alignItems | select + button groups |
| Position | position, top, left (-200 to 200px) | select + px sliders |

- **New `buttons` control type:** Row of visual toggle buttons (`.ed-btn-group` + `.ed-btn-opt`). Used for alignment, flex controls. Active state highlighted in blue.
- All new controls use the same `applyStyle()` → `pushUndo()` → `scheduleAutoSave()` pipeline — undo and auto-save work automatically

---

## Architecture

### Data Flow
```
STYLE_SECTIONS (config) → renderPanel() → buildControl() → HTML string
                                        → event listeners → applyStyle()
                                                          → pushUndo()
                                                          → scheduleAutoSave()
                                                          → doSave() → File System Access API
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `boot()` | Entry point — injects CSS, builds UI, restores folder handle from IndexedDB |
| `setEditMode(on)` | Toggles edit mode, verifies folder permission, validates folder |
| `switchMode(mode)` | Switches between 'text' and 'style' modes |
| `attachTextTargets()` | Adds click-to-edit to all matching text elements |
| `wrapImages()` | Wraps images in overlay containers for replacement |
| `openStylePanel(target)` | Renders style controls for clicked element |
| `renderPanel(panel, target)` | Builds all sections from `STYLE_SECTIONS`, wires event listeners |
| `buildControl(row, computed, target)` | Returns HTML for one control row (color/px/float/select/buttons) |
| `applyStyle(target, prop, value)` | Sets `target.style[prop]`, pushes undo if changed |
| `pushUndo(target, field, oldVal, newVal)` | Adds to undo stack, increments change count, triggers auto-save |
| `scheduleAutoSave()` | 1.5s debounced save — checks permission, calls `doSave(true)` |
| `doSave(silent)` | Writes `cleanHTML()` to disk via FSA, or download fallback |
| `cleanHTML()` | Clones DOM, strips editor elements/classes, returns clean HTML string |
| `validateFolder(handle)` | Checks that folder contains the current page's HTML file |
| `pickFolder()` | Opens directory picker, validates, persists handle to IndexedDB |
| `blurActive()` | Safely blurs active text element (nulls ref BEFORE calling .blur()) |

### Control Types in `buildControl()`

| Type | UI | Data Attributes |
|------|-----|-----------------|
| `color` | Color swatch + hex text input | `data-prop`, `data-type="color"` |
| `px` | Range slider + number input | `data-prop`, `data-type="range"`, `data-unit="px"` |
| `float` | Range slider + number input (no unit) | `data-prop`, `data-type="range"`, `data-unit=""` |
| `select` | Dropdown `<select>` | `data-prop`, `data-type="select"` |
| `buttons` | Row of toggle buttons | `data-prop`, `data-type="buttons"`, `data-value` |

### CSS Classes (injected via `<style id="editor-styles">`)

| Selector | Purpose |
|----------|---------|
| `#editor-toggle` | Fixed bottom-right Edit Mode button |
| `#editor-toolbar` | Fixed top-center toolbar (modes, undo, save, folder) |
| `#ed-style-panel` | Floating style panel (272px wide, max-height scrollable) |
| `#ed-save-status` | Auto-save status indicator (pending/saving/saved/error) |
| `#ed-folder-chip` | Connected folder name chip |
| `.ed-text-target` | Dashed orange outline on editable text elements |
| `.ed-style-hover` | Dashed blue outline on hovered elements (style mode) |
| `.ed-style-selected` | Solid blue outline on selected element |
| `.ed-img-wrap` / `.ed-img-overlay` | Image replacement overlay |
| `.ed-btn-group` / `.ed-btn-opt` | Button-group toggle controls |

### IndexedDB

- **Database:** `mhcr-editor-v1`
- **Object Store:** `handles`
- **Key:** `dirHandle`
- **Value:** `FileSystemDirectoryHandle` — persists across sessions
- Functions: `persistHandle()`, `restoreHandle()`, `clearStoredHandle()`

---

## Troubleshooting

### Editor doesn't appear
- Check you're on `localhost`, `127.0.0.1`, or `192.168.*`
- Check browser console for JS errors
- Verify `<script src="js/editor.js"></script>` (or `../js/editor.js`) exists before `</body>`

### Auto-save status stays at "● Unsaved"
- **Most likely:** `doSave()` is failing silently. Open DevTools Console → look for `[editor] doSave error:` messages
- **Wrong folder:** You selected a parent folder or wrong folder. Disconnect (✕ on folder chip) and re-select the exact folder containing `index.html`
- **Permission lost:** Toggle Edit Mode off then on again to re-grant filesystem permission

### "✕ Save failed" appears in red
- Check the toast message — it explains the specific error
- `NotFoundError`: Wrong folder selected, or file was renamed/deleted
- `NotAllowedError`: Browser revoked permission — toggle Edit Mode to re-grant
- Generic error: Check DevTools Console for full stack trace

### Style changes don't persist after reload
- Auto-save must be connected (folder chip shows green)
- Check that status goes through `Saving…` → `Saved` after changes
- If using Safari/Firefox: no auto-save, use manual 💾 Save (downloads HTML file)

### Panel doesn't show all sections
- Hard refresh (Cmd+Shift+R) to bypass browser cache
- Check console for JS errors during `renderPanel`

### Browser cache serving old editor.js
- Python `http.server` supports `If-Modified-Since` but browsers can be aggressive
- Hard refresh: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows)
- Or: DevTools → Network tab → check "Disable cache" while DevTools is open

### blurActive() crash (fixed in v3.1)
- **Symptom:** `TypeError: Cannot read properties of null (reading 'removeAttribute')`
- **Cause:** `.blur()` fires `onTextBlur` synchronously which nulls `activeTextEl`, then next line uses null ref
- **Fix:** Save reference before `.blur()`: `const t = activeTextEl; activeTextEl = null; t.blur(); t.removeAttribute(...)`

---

## Dev Server

**Python (recommended):**
```bash
python3 -m http.server 8080 --directory "/Users/maz/Documents/Github/MHCR Website"
```

**Or via Claude launch.json:**
- Config: `~/.claude/launch.json` → "MHCR Python Server" on port 8080

---

## Files Modified by Editor Sessions

When auto-save writes, it saves the FULL HTML of the current page (via `cleanHTML()`). The serializer:
1. Clones `document.documentElement`
2. Removes editor elements: `#editor-toggle`, `#editor-toolbar`, `#editor-toast`, `#editor-styles`, `#ed-style-panel`
3. Removes editor classes: `.ed-text-target`, `.ed-style-hover`, `.ed-style-selected`
4. Removes `contenteditable` attributes and `data-ed-orig` datasets
5. Unwraps `.ed-img-wrap` containers (restores plain `<img>` tags)
6. Outputs `<!DOCTYPE html>\n` + `clone.outerHTML`

Style changes are saved as **inline styles** on the elements (e.g., `style="text-align: center; width: 300px;"`).
