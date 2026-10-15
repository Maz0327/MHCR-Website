"""Load and validate _build/data/*.json, then derive what templates need (stdlib only).

Template context (all keys available in every page):
  site      site.json as-is (phone, cities, nav, form, flags, dial, home_jobs)
  services  services.json list, A-Z, each + .jobs (its PUBLISHED jobs, derived from jobs.json `category`)
  jobs      published jobs only (jobs.json order: they get a page), each with .frames (held frames removed) and .after
  job       {slug: job} for every job whose photos may be shown (photos != false), published or not
  home_jobs the homepage 2x2 (site.home_jobs as job dicts; use {{pic after}})
  dial      the dial stops, 1..N: n, nn, total, label, line, kind (photo|word|urgent), urgent, links [{name, path}],
            photo (job/frame or None), pos, job (title), href (job page), alt
  film      film.json (frame files + geometry for js/film.js)
Every rule below fails the build loudly; data mistakes must never ship as blanks.
"""
import json
import os
import re


class DataError(Exception):
    pass


def _load(data_dir, name):
    path = os.path.join(data_dir, name)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise DataError(f"{name}: {e}") from e


def _check(cond, msg):
    if not cond:
        raise DataError(msg)


def _az(items, key, what):
    names = [i[key].lower() for i in items]
    _check(names == sorted(names), f"{what} must be A-Z: {[i[key] for i in items]}")


def load(data_dir):
    site, svc_doc, job_doc = (_load(data_dir, n) for n in ("site.json", "services.json", "jobs.json"))
    film = _load(data_dir, "film.json")
    services, all_jobs = svc_doc["services"], job_doc["jobs"]

    # ---- site
    _check(re.fullmatch(r"\+1\d{10}", site["phone"]["tel"] or ""), "site.phone.tel must look like +17204924326")
    _az(site["cities"], "name", "site.cities")
    _az(site["nav"], "label", "site.nav")

    # ---- jobs
    slugs = [j["slug"] for j in all_jobs]
    _check(len(slugs) == len(set(slugs)), f"jobs.json: duplicate slugs {slugs}")
    by_slug = {}
    for j in all_jobs:
        _check(re.fullmatch(r"[a-z0-9-]+", j["slug"]), f"jobs.json: bad slug {j['slug']!r}")
        names = [f["name"] for f in j["frames"]]
        _check(len(names) == len(set(names)), f"jobs.json {j['slug']}: duplicate frame names")
        for f in j["frames"]:
            _check(f.get("alt", "").strip(), f"jobs.json {j['slug']}/{f['name']}: alt text is required")
            _check(f.get("provenance", "").strip(), f"jobs.json {j['slug']}/{f['name']}: provenance is required")
        if j.get("photos", True):
            live = [dict(f) for f in j["frames"] if not f.get("hold")]
            _check(live and live[-1]["name"] == "after", f"jobs.json {j['slug']}: last shown frame must be 'after'")
            by_slug[j["slug"]] = dict(j, frames=live, after=f"{j['slug']}/after", href=j.get("page") if j.get("publish") else "")
        else:
            _check(not j.get("publish"), f"jobs.json {j['slug']}: publish:true needs photos")
    jobs = [by_slug[s] for s in slugs if s in by_slug and by_slug[s].get("publish")]

    # ---- services (A-Z, dial order 1..N, photos must be published frames)
    _az(services, "name", "services.json")
    names = {s["name"] for s in services}
    for j in all_jobs:
        _check(j["category"] in names, f"jobs.json {j['slug']}: category {j['category']!r} is not a service name")
    out_services = []
    for i, s in enumerate(services):
        _check(s["az_order"] == i + 1, f"services.json {s['name']}: az_order {s['az_order']} != position {i + 1}")
        _check(re.fullmatch(r"[a-z0-9/-]+\.html", s["path"]), f"services.json {s['name']}: bad path {s['path']!r}")
        if s.get("photo"):
            _frame(by_slug, s["photo"], f"services.json {s['name']}.photo")
        out_services.append(dict(s, jobs=[j for j in jobs if j["category"] == s["name"]]))
    stops = sorted((s for s in out_services if s.get("dial_order")), key=lambda s: s["dial_order"])
    orders = [s["dial_order"] for s in stops]
    _check(orders == list(range(1, len(stops) + 1)), f"services.json: dial_order must run 1..N once each, got {orders}")
    dial = []
    for s in stops:
        n, photo = s["dial_order"], s.get("photo")
        job, frame = (_frame(by_slug, photo, "dial") if photo else (None, None))
        by_name = {x["name"]: x for x in out_services}
        links = []
        for name in s.get("dial_links", []):
            _check(name in by_name, f"services.json {s['name']}.dial_links: unknown service {name!r}")
            links.append({"name": name, "path": by_name[name]["path"]})
        dial.append({"n": n, "nn": f"{n:02d}", "total": f"{len(stops):02d}", "label": s.get("dial_label") or s["name"],
                     "line": s.get("dial_line") or s["line"], "urgent": bool(s.get("urgent")), "path": s["path"],
                     "kind": "photo" if photo else ("urgent" if s.get("urgent") else "word"), "links": links,
                     "photo": photo, "pos": s.get("photo_pos", "50% 50%"),
                     "job": job["title"] if job else "", "job_slug": job["slug"] if job else "",
                     "href": job["href"] if job else "", "alt": frame["alt"] if frame else ""})

    # ---- homepage 2x2: finished afters of published jobs
    for slug in site.get("home_jobs", []):
        _check(slug in by_slug and by_slug[slug].get("publish"), f"site.home_jobs: {slug!r} must be a published job (tiles link to its page)")
    _check(1 <= site["dial"]["default_stop"] <= len(dial), "site.dial.default_stop is outside the dial")

    home_jobs = [by_slug[s] for s in site.get("home_jobs", [])]
    return {"site": site, "services": out_services, "jobs": jobs, "job": by_slug, "dial": dial, "film": film,
            "home_jobs": home_jobs}


def _frame(by_slug, ref, where):
    """'job/frame' -> (job, frame) for a published job and a frame that isn't on hold."""
    _check(isinstance(ref, str) and ref.count("/") == 1, f"{where}: frame ref must be 'job/frame', got {ref!r}")
    slug, name = ref.split("/")
    _check(slug in by_slug, f"{where}: job {slug!r} has photos:false (never shown) or does not exist")
    for f in by_slug[slug]["frames"]:
        if f["name"] == name:
            return by_slug[slug], f
    raise DataError(f"{where}: {ref!r} is not a shown frame of {slug} (missing or on hold)")


def frame(ctx, ref):
    """Public lookup for helpers: same rules as the data checks."""
    return _frame(ctx["job"], ref, "pic")
