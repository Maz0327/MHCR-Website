# MHCR site build (`_build/`)

GitHub Pages runs Jekyll, so this `_`-prefixed folder is never published. Python 3 stdlib only.
**Edit `_build/`, never the generated HTML.**

| Command | What it does |
|---|---|
| `python3 _build/build.py` | Render `pages/**/*.html` into the repo root (existing slugs). Writes nothing if any page fails. |
| `python3 _build/build.py --pages _build/test/fixtures/pages --out /tmp/x` | Build the stub pages somewhere else (smoke test). |
| `python3 -m unittest discover -s _build/test` | Build-system tests. |
| `python3 _build/tools/make_scrub_inventory.py` | Rewrite `scrub-inventory.tsv` (every claims hit in the live pages + `llms*.txt`). |
| `_build/qa/qa_all.sh index.html [pages...]` | Claims grep, picture check, browser QA, breathing-room QA. |
| `/usr/local/bin/python3 _build/tools/import_job_images.py` | Re-import job photos (needs Pillow; not part of the build). |

- `data/`: `site.json`, `services.json`, `jobs.json`, `film.json`, `banned-words.txt` (each JSON has a `_readme`).
- `partials/`: shared HTML (`shell`, `head`, `header`, `footer`, `ask`, `quote-sheet`).
- `pages/`: one fragment per page; header comments `path` / `title` / `description` / `layout`.
- `js-src/`: copied to `js/` on build (`dial.js`, `film.js`).
- Templates: `{{name}}`, `{{& raw}}`, `{{> partial}}`, `{{#each}}`, `{{#if}}/{{else}}`, `{{pic job/frame [eager] [pos=..] [sizes=".."]}}`, `{{json name}}`.
- Every content `<img>` comes from `{{pic}}` (3:4 phone + 3:2 desktop). Use `data-nopic` only for the logo, icons and film frames.
