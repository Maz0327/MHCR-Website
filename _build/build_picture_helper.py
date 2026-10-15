"""Responsive job photos for the MHCR build (stdlib only).

Every job frame ships as 4 files in images/jobs/<job>/ (made by tools/import_job_images.py):
  <frame>-m-800.webp  <frame>-m-1200.webp   3:4 portrait  (phones; the <img>)
  <frame>-d-1600.webp <frame>-d-2400.webp   3:2 landscape (>= 1024px; the <source>)
The -800/-1200/-1600/-2400 names are size SLOTS: a slot is never upscaled past its master, so the real
width can be smaller. The helper reads each file's real pixel size, so srcset `w` values and width/height are true.
"""
import html
import os
import struct

BREAKPOINT = "(min-width:1024px)"   # matches the comps: desktop layout and 3:2 photos from 1024px
SLOTS = {"m": ("m-800", "m-1200"), "d": ("d-1600", "d-2400")}


def image_size(path):
    """(width, height) of a .webp or .png file, read from its header. Raises FileNotFoundError / ValueError."""
    with open(path, "rb") as f:
        head = f.read(40)
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", head[16:24])
    if head[:4] != b"RIFF" or head[8:12] != b"WEBP":
        raise ValueError(f"not a webp/png: {path}")
    chunk = head[12:16]
    if chunk == b"VP8 ":                                   # lossy: start code 9d 01 2a, then 14-bit sizes
        if head[23:26] != b"\x9d\x01\x2a":
            raise ValueError(f"bad VP8 header: {path}")
        w, h = struct.unpack("<HH", head[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if chunk == b"VP8L":                                   # lossless: 0x2f, then 14+14 bits (minus one)
        b = struct.unpack("<I", head[21:25])[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X":                                   # extended: 24-bit canvas sizes (minus one)
        return int.from_bytes(head[24:27], "little") + 1, int.from_bytes(head[27:30], "little") + 1
    raise ValueError(f"unknown webp chunk {chunk!r}: {path}")


def frame_files(site_root, job, frame):
    """{'m': [(url, w, h), ...], 'd': [...]} for one frame, deduped by width. Raises if a file is missing."""
    out = {}
    for kind, slots in SLOTS.items():
        seen, rows = set(), []
        for slot in slots:
            url = f"images/jobs/{job}/{frame}-{slot}.webp"
            path = os.path.join(site_root, url)
            if not os.path.isfile(path):
                raise FileNotFoundError(f"missing image {url} (run _build/tools/import_job_images.py)")
            w, h = image_size(path)
            if w not in seen:
                seen.add(w)
                rows.append((url, w, h))
        out[kind] = sorted(rows, key=lambda r: r[1])
    return out


def _attrs(d):
    return "".join(f' {k}="{html.escape(str(v), quote=True)}"' for k, v in d.items() if v is not None)


def picture(files, alt, eager=False, sizes="100vw", dsizes=None, pclass=None, pos=None, **img_attrs):
    """<picture>: 3:2 <source> from 900px up, 3:4 <img> below. pos = object-position for the crop.
    Extra keyword attrs go on the <img> (class, style...)."""
    if pos:
        img_attrs["style"] = f"object-position:{pos};" + img_attrs.get("style", "")
    m, d = files["m"], files["d"]
    srcset = lambda rows: ", ".join(f"{u} {w}w" for u, w, _ in rows)
    big_d, big_m = d[-1], m[-1]
    source = {"media": BREAKPOINT, "srcset": srcset(d), "sizes": dsizes or sizes, "width": big_d[1], "height": big_d[2]}
    img = {"src": m[0][0], "srcset": srcset(m), "sizes": sizes, "width": big_m[1], "height": big_m[2], "alt": alt,
           "loading": None if eager else "lazy", "decoding": "async", "fetchpriority": "high" if eager else None}
    img.update(img_attrs)
    return f"<picture{_attrs({'class': pclass})}><source{_attrs(source)}><img{_attrs(img)}></picture>"
