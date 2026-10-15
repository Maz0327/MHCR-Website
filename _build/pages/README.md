# Page fragments

One `.html` file per published page; `python3 _build/build.py` renders them into the repo root.
Header comments come first (`<!-- path: ... -->` required; `title`, `description`, `layout: none` optional).
See the docstrings in `../build.py` and `../build_template_engine.py` for the syntax.
Phases 03-06 add: `home.html`, `services/*.html`, `jobs/*.html`, `legacy/*.html`.
