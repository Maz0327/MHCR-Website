#!/usr/bin/env bash
# Run every QA script. Usage: _build/qa/qa_all.sh <page.html> [more pages...]
#   qa_claims.sh     banned-claims grep over ALL published files (raw lines)        stdlib
#   qa_pictures.py   every content <img> has mobile + desktop sources, files exist    stdlib
#   qa_v1.py         browser QA of the FIRST page given (film optional, quote sheet)  playwright + Chrome
#   qa_breathing.py  breathing-room spec on every page given                          playwright + Chrome
# Reports: out/report.txt and out/breathing-report.txt. Exit 1 if any script fails.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
[ $# -ge 1 ] || { echo "usage: qa_all.sh <page.html> [more pages...]" >&2; exit 2; }
rc=0
"$HERE/qa_claims.sh" || rc=1
python3 -I "$HERE/qa_pictures.py" "$@" || rc=1
python3 -I "$HERE/qa_v1.py" "$1" || rc=1
python3 -I "$HERE/qa_breathing.py" "$@" || rc=1
echo; echo "qa_all: $([ $rc -eq 0 ] && echo ALL PASS || echo FAILURES, see the output above and out/*.txt)"
exit $rc
