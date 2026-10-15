#!/usr/bin/env bash
# Banned-claims grep over the published files (every .html + llms*.txt), raw lines: comments, meta, schema and URLs
# count too. Patterns: _build/data/banned-words.txt ("allow:" phrases such as "Free consultation" are OK).
# Usage: _build/qa/qa_claims.sh [files...]     Exit 1 on any banned hit (target: 0).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; SITE="$(cd "$HERE/../.." && pwd)"
if [ $# -eq 0 ]; then
  files=()
  while IFS= read -r f; do files+=("$f"); done < <(cd "$SITE" && python3 -I -c 'import sys; sys.path.insert(0, "_build"); from tools.make_scrub_inventory import published_files; print("\n".join(published_files()))')
  set -- "${files[@]}"
fi
python3 -I "$HERE/../build_page_checks.py" claims "$@"
