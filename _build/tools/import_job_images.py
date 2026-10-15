"""Import the approved job photos into images/jobs/<job>/ with the site's 4-file names. 0 credits, local only.

NOT part of build.py (that one is stdlib only). This one-off needs Pillow for the unstretch step:
    /usr/local/bin/python3 _build/tools/import_job_images.py            # writes images/jobs/** + tools/image-import-log.tsv

What it does, per shown frame of every job whose photos may be shown (photos != false) in data/jobs.json:
  <frame>-m-800 / -m-1200 (3:4)  byte copies of the approved mobile finals (<frame>-800.webp / <frame>.webp)
  <frame>-d-1600 / -d-2400 (3:2) byte copies of the approved desktop wides (-wide-1600 / -wide), EXCEPT the
                                 older wides in UNSTRETCH: re-made from their 2048px masters, squeezed sideways by
                                 1/aspect (aspect measured by NCC against the mobile), trimmed back to 3:2.
Slots are never upscaled past the master, so a slot's real width can be under its name (build reads real sizes).
Film frames (images/jobs/fireplace-1/film-<frame>-<set>.webp, prep + final): m = the phone film frames cut to the
stone wall's width (x 198-1230 of 1440: the bar shelf with bottles sits right of it and must never show at any width);
d = the cleaned 3:2 card crop of the 4K keys (x 1338-2706, y 1184-2096: no bar shelves or bottles), 2400x1600 +
light unsharp, the same recipe as the approved film card (fireplace-1/after-d-2400).
Never touches: Kitchen 1 IMG_9626-9630 / IMG_0029, Bathroom 3 IMG_9638-9640 (MLS); none are in the sources below.
"""
import json
import os
import shutil

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
ARCHIVE = "/Users/maz/Documents/Projects/MHCR-Redesign/2026-10-14-session/scratchpad"
FINAL = f"{ARCHIVE}/photo-batch/final"
MASTER2 = f"{ARCHIVE}/photo-batch/master2"
FILM = f"{ARCHIVE}/mhcr-stone-film/f"
KEYS = f"{ARCHIVE}/fp1/keys"
CARD_BOX = (1338, 1184, 2706, 2096)
FP1_M_BOX = (198, 300, 1230, 1676)
# Prep frame v2 (10-15): cement-board seams redrawn as staggered T joints, pixel-identical outside the board.
PREP_FIX = "/Users/maz/Documents/Projects/MHCR-Redesign/photo-fixes-261015/fp1-prep"
PREP_4K, PREP_M = f"{PREP_FIX}/prep_4k_v2.png", f"{PREP_FIX}/m_prep_v2.png"   # replace keys/prep_4k.png, keys/m_prep.png   # where fireplace-1/after (the 3:4 film card) sits in the film's final-m frame

# Older wides that were still stretched: (master file, measured aspect vs the mobile, NCC confidence).
# Measured 2026-10-15 with a two-stage NCC fit (coarse grid as wide2/tools/measure_stretch.py, then 0.005 steps).
UNSTRETCH = {
    "kitchen-1/before": ("wide_k1_before_s.png", 1.095, 0.951),
    "kitchen-1/after": ("wide_k1_after_s.png", 1.105, 0.940),
    "kitchen-1/process-2": ("wide_k1_p2_s.png", 1.045, 0.876),
    "bathroom-2/process-1": ("wide_b2_p1_s.png", 1.110, 0.945),
    "bathroom-2/process-2": ("wide_b2_p2_s.png", 1.175, 0.760),
    "wall-1/before": ("wide_w1_before_s.png", 1.155, 0.948),
    "fireplace-2/before": ("wide_fp2_before_s.png", 1.090, 0.974),
    "fireplace-2/after": ("wide_fp2_after_s.png", 1.050, 0.779),
}
# Frames whose finals live outside final/<job>/ (Fireplace 1's after is the cleaned film final card).
SPECIAL = {"fireplace-1/after": f"{FINAL}/service-cards/fp1-film-final-crop"}


def save_webp(im, path, q):
    im.save(path, "WEBP", quality=q, method=6)


def unstretch(master, aspect, out_dir, frame):
    im = Image.open(os.path.join(MASTER2, master)).convert("RGB")
    w, h = im.size
    im = im.resize((round(w / aspect), h), Image.LANCZOS)              # undo the sideways stretch
    w, h = im.size
    nh = round(w / 1.5)                                                 # trim top + bottom back to 3:2
    y = (h - nh) // 2
    im = im.crop((0, y, w, y + nh))
    big = im if im.width <= 2400 else im.resize((2400, 1600), Image.LANCZOS)
    save_webp(big, f"{out_dir}/{frame}-d-2400.webp", 82)
    save_webp(im.resize((1600, 1067), Image.LANCZOS), f"{out_dir}/{frame}-d-1600.webp", 82)
    return f"unstretched 1/{aspect} from master2/{master}"


def fp1_before(out_dir):
    """Fireplace 1's before, cut from the film's aligned frames so the before/after slider lines up exactly with the
    after (same camera, same crop): 3:4 = film before-m at FP1_M_BOX; 3:2 = before_4k at CARD_BOX (same as the after)."""
    m = Image.open(f"{FILM}/before-m.webp").convert("RGB").crop(FP1_M_BOX)
    save_webp(m, f"{out_dir}/before-m-1200.webp", 80)
    save_webp(m.resize((800, round(800 * m.height / m.width)), Image.LANCZOS), f"{out_dir}/before-m-800.webp", 80)
    d = Image.open(f"{KEYS}/before_4k.png").convert("RGB").crop(CARD_BOX).resize((2400, 1600), Image.LANCZOS)
    d = d.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=2))
    save_webp(d, f"{out_dir}/before-d-2400.webp", 82)
    save_webp(d.resize((1600, 1067), Image.LANCZOS), f"{out_dir}/before-d-1600.webp", 82)
    return "aligned to the after: film before-m crop + before_4k card crop"


def make_og_images(jobs):
    """Share images, 1200x630 JPEG, in images/og/: home.jpg = the stacked stone wall + fireplace from the film's FINAL
    4K key, cut inside the stone wall (x 1350-2700: the bar shelf with bottles is right of 2706, so it can't show);
    <job>.jpg = the centre of each job's 3:2 after."""
    out_dir, rows = os.path.join(SITE, "images/og"), []
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(f"{KEYS}/final_4k.png").convert("RGB")
    w = 2700 - 1350; h = round(w * 630 / 1200); cy = 1660                    # centred on the gas insert
    im.crop((1350, cy - h // 2, 2700, cy - h // 2 + h)).resize((1200, 630), Image.LANCZOS).save(f"{out_dir}/home.jpg", "JPEG", quality=85, optimize=True, progressive=True)
    rows.append(("images/og/home.jpg", "1200", "630", "fp1/keys/final_4k.png", "og: crop x1350-2700 inside the stone wall"))
    for job in (j for j in jobs if j.get("photos", True)):
        src = os.path.join(SITE, f"images/jobs/{job['slug']}/after-d-2400.webp")
        im = Image.open(src).convert("RGB")
        ch = round(im.width * 630 / 1200); y = (im.height - ch) // 2
        im.crop((0, y, im.width, y + ch)).resize((1200, 630), Image.LANCZOS).save(f"{out_dir}/{job['slug']}.jpg", "JPEG", quality=85, optimize=True, progressive=True)
        rows.append((f"images/og/{job['slug']}.jpg", "1200", "630", f"images/jobs/{job['slug']}/after-d-2400.webp", "og: centre crop"))
    return rows


def main():
    with open(os.path.join(SITE, "_build/data/jobs.json"), encoding="utf-8") as f:
        jobs = json.load(f)["jobs"]
    log = [("file", "width", "height", "source", "note")]
    for job in (j for j in jobs if j.get("photos", True)):
        out_dir = os.path.join(SITE, "images/jobs", job["slug"])
        os.makedirs(out_dir, exist_ok=True)
        for fr in (f for f in job["frames"] if not f.get("hold")):
            key = f"{job['slug']}/{fr['name']}"
            base = SPECIAL.get(key, f"{FINAL}/{key}")
            note = "byte copy"
            shutil.copyfile(f"{base}.webp", f"{out_dir}/{fr['name']}-m-1200.webp")
            if os.path.exists(f"{base}-800.webp"):
                shutil.copyfile(f"{base}-800.webp", f"{out_dir}/{fr['name']}-m-800.webp")
            else:                                                       # only the film final card has no -800
                im = Image.open(f"{base}.webp").convert("RGB")
                save_webp(im.resize((800, round(800 * im.height / im.width)), Image.LANCZOS), f"{out_dir}/{fr['name']}-m-800.webp", 80)
                note = "m-800 resized from the 3:4 final"
            if key == "fireplace-1/before":
                note = fp1_before(out_dir); base = f"{FILM}/before-m"
            elif key in UNSTRETCH:
                master, aspect, _ = UNSTRETCH[key]
                note = unstretch(master, aspect, out_dir, fr["name"])
            else:
                shutil.copyfile(f"{base}-wide.webp", f"{out_dir}/{fr['name']}-d-2400.webp")
                shutil.copyfile(f"{base}-wide-1600.webp", f"{out_dir}/{fr['name']}-d-1600.webp")
            for slot in ("m-800", "m-1200", "d-1600", "d-2400"):
                p = f"{out_dir}/{fr['name']}-{slot}.webp"
                w, h = Image.open(p).size
                log.append((os.path.relpath(p, SITE), str(w), str(h), os.path.relpath(base, ARCHIVE), note))
    film_dir = os.path.join(SITE, "images/jobs/fireplace-1")
    for name in ("prep", "final"):
        dst = f"{film_dir}/film-{name}-m.webp"                    # phone set: cut to the stone wall's width (x 198-1230)
        if name == "prep":                                        # so the bar shelf + bottles at the right can never show
            m = Image.open(PREP_M).convert("RGB").resize((1440, 2217), Image.LANCZOS)   # same 0.75 scale as the film's -m
        else:
            m = Image.open(f"{FILM}/{name}-m.webp").convert("RGB")
        save_webp(m.crop((FP1_M_BOX[0], 0, FP1_M_BOX[2], m.height)), dst, 82)
        log.append((os.path.relpath(dst, SITE), *map(str, Image.open(dst).size), "photo-fixes-261015/fp1-prep/m_prep_v2.png" if name == "prep" else f"mhcr-stone-film/f/{name}-m.webp", "film frame, cut to x198-1230 (no shelf)"))
        dst = f"{film_dir}/film-{name}-d.webp"
        im = Image.open(PREP_4K if name == "prep" else f"{KEYS}/{name}_4k.png").convert("RGB").crop(CARD_BOX).resize((2400, 1600), Image.LANCZOS)
        save_webp(im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=2)), dst, 82)
        log.append((os.path.relpath(dst, SITE), "2400", "1600", "photo-fixes-261015/fp1-prep/prep_4k_v2.png" if name == "prep" else f"fp1/keys/{name}_4k.png", "film card crop x1338-2706 y1184-2096"))
    log += make_og_images(jobs)
    with open(os.path.join(HERE, "image-import-log.tsv"), "w", encoding="utf-8") as f:
        f.write("\n".join("\t".join(r) for r in log) + "\n")
    print(f"{len(log) - 1} files written; log: _build/tools/image-import-log.tsv")


if __name__ == "__main__":
    main()
