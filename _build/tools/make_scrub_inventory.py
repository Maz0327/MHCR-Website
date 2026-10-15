"""Write _build/scrub-inventory.tsv: every claims hit in the published pages + llms*.txt (stdlib only).

  python3 _build/tools/make_scrub_inventory.py

Raw-line grep with data/banned-words.txt (banned AND check patterns), so comments, meta tags, schema JSON and
llms text all count. One row per hit: file, line, kind, label, phrase, context, proposed. The copywriter reviews
the `proposed` column; Phase 06 rebuilds each legacy page from a scrubbed fragment.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
SITE = os.path.dirname(BUILD)
sys.path.insert(0, BUILD)
import build_page_checks as checks  # noqa: E402

SKIP_DIRS = {".git", ".claude", "_build", "MHCR IMAGES", "screenshots", "__pycache__", "images", "css", "js"}
PHONE = "(720) 492-4326"
PROPOSE = {
    "licensed": "delete (no license claim)",
    "insured": "delete (no insurance claim)",
    "bonded": "delete",
    "contractor": 'replace: "we" / "our crew" / "remodeler" (never contractor/contracting); schema type -> HomeAndConstructionBusiness',
    "since 2009": "delete (no tenure claim)",
    "N years": "delete (no tenure or experience claim)",
    "years of experience": "delete (no experience claim)",
    "reviews": "delete (no reviews module Monday)",
    "ratings": "delete (no ratings)",
    "star rating": "delete (no ratings)",
    "testimonials": "delete (no testimonials Monday)",
    "financing": "delete (no financing offer)",
    "warranty": "delete (no warranty claim)",
    "guarantee": "delete (no guarantee claim)",
    "24/7": f'replace: "Call {PHONE}" (no hours claim)',
    "free estimate": 'replace: "Free consultation" (client OK) or "Get a quote"',
    "storm/hail (until the owner confirms storm work)": 'delete; emergency line = "Leaks, water damage and small fixes"',
    "fabricated address": "delete (no street address until Omar gives one)",
    "N+ count (500+ projects, 15+ years)": "delete (unverified count)",
    "free (other)": 'keep only as "Free consultation"; otherwise delete or confirm with owner',
}


def published_files():
    out = []
    for dp, dns, fns in os.walk(SITE):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS and not d.startswith("."))
        for fn in sorted(fns):
            if fn.endswith(".html") or (fn.startswith("llms") and fn.endswith(".txt")):
                out.append(os.path.join(dp, fn))
    return out


def main():
    claims = checks.load_claims()
    rows, allowed = [], 0
    for path in published_files():
        rel = os.path.relpath(path, SITE)
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        for n, line in enumerate(lines, 1):
            allowed += len(claims.allowed(line))
            for kind, label, word, start in claims.hits(line, ("ban", "check")):
                ctx = " ".join(line[max(0, start - 50):start + len(word) + 50].split())
                rows.append((rel, str(n), kind, label, word, ctx.replace("\t", " "), PROPOSE.get(label, "review")))
    out = os.path.join(BUILD, "scrub-inventory.tsv")
    with open(out, "w", encoding="utf-8") as f:
        f.write("file\tline\tkind\tlabel\tphrase\tcontext\tproposed\n")
        f.writelines("\t".join(r) + "\n" for r in rows)
    by = {}
    for r in rows:
        by[(r[2], r[3])] = by.get((r[2], r[3]), 0) + 1
    print(f"{len(rows)} hits in {len({r[0] for r in rows})} files (+{allowed} allowed 'Free consultation') -> {os.path.relpath(out, SITE)}")
    for (kind, label), n in sorted(by.items(), key=lambda kv: -kv[1]):
        print(f"  {n:4d}  {kind:5s}  {label}")


if __name__ == "__main__":
    main()
