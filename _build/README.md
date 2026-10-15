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
| `python3 -I _build/qa/shots_home_vs_comps.py` | Homepage vs approved comps, side by side (`~/Documents/Projects/MHCR-Redesign/build-qa/`). |
| `python3 -I _build/qa/shots_pages_vs_comps.py [service index job text]` | Inner pages vs comps + the text-page set. |
| `/usr/local/bin/python3 _build/tools/import_job_images.py` | Re-import job photos (needs Pillow; not part of the build). |

- `data/`: `site.json`, `services.json`, `jobs.json`, `film.json`, `banned-words.txt` (each JSON has a `_readme`).
- `partials/`: shared HTML (`shell`, `head`, `header`, `footer`, `ask`, `quote-sheet`).
- `pages/`: one fragment per page; header comments `path` / `title` / `description` / `layout` / `scripts` / `robots` / `sheet` / `each` (`<!-- each: services as svc -->` makes one page per item: services, jobs, cities).
- The build also writes `sitemap.xml` (indexable pages, real lastmod) and `robots.txt`; JSON-LD via `{{ld "business"}}`, `{{ld "service"}}`, `{{ld "faq"}}`. Every phone number in page text becomes a tel: link.
- CSS is hand-written in `css/site.css` (shared + homepage) and `css/site-pages.css` (inner pages), not generated. Desktop layout and 3:2 photos start at 1024px (the comps).
- `js-src/`: copied to `js/` on build: `dialog.js` + `quote-sheet.js` (every page), `film.js` + `dial.js` (pages that list them in `<!-- scripts: film dial -->`).
- Templates: `{{name}}`, `{{& raw}}`, `{{> partial}}`, `{{#each}}`, `{{#if}}/{{else}}`, `{{pic job/frame [eager] [pos=..] [sizes=".."]}}`, `{{json name}}`.
- Every content `<img>` comes from `{{pic}}` (3:4 phone + 3:2 desktop). Use `data-nopic` only for the logo, icons and film frames.
