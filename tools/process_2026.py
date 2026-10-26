#!/usr/bin/env python3
"""Ingest the 2026 competition: pupil entries + photographer's event pictures.

    python3 tools/process_2026.py --schools <dir> --events <dir> [--scorecard <csv>]

--schools   folder holding one sub-folder per school (Clydebank High School, St Peter the
            Apostle, Dumbarton, ...). Files may be loose or in S1-S2 / S3-S4 / S5-6 sub-folders.
--events    folder of the photographer's event pictures.
--scorecard optional CSV export of the scoring card. Only used to work out the year group of
            a few files whose names carry no stage. It is read locally and NEVER written out.

NO pupil names appear in any output: images are renamed to anonymous IDs and grouped only by
year -> school -> year group. The existing 2024/2025 entries are left untouched; this script
only (re)writes the 2026 entries and the 2026 event photos, merging into manifest.json.
"""

import argparse
import csv
import difflib
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile

from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()
Image.MAX_IMAGE_PIXELS = 600_000_000  # our own phone/camera files; some are huge

SITE = pathlib.Path(__file__).resolve().parent.parent
ENTRIES = SITE / "assets" / "entries"
EVENTS = SITE / "assets" / "events" / "2026"
YEAR = "2026"

SCHOOLS = {
    "clydebank high school": ("clydebank-high-school", "Clydebank High School"),
    "st peter the apostle": ("st-peter-the-apostle", "St Peter the Apostle High School"),
    "dumbarton": ("dumbarton-academy", "Dumbarton Academy"),
    "vale of leven": ("vale-of-leven-academy", "Vale of Leven Academy"),
}
BANDS = {"S1": "S1–S2", "S2": "S1–S2", "S3": "S3–S4", "S4": "S3–S4", "S5": "S5–S6", "S6": "S5–S6"}
LEVELS = {"JUNIOR": "S1–S2", "INTERMEDIATE": "S3–S4", "SENIOR": "S5–S6"}
RASTER = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}

ENTRY_FULL, ENTRY_THUMB = 1400, 520
EVENT_FULL, EVENT_THUMB = 1800, 640


def load_image(path):
    try:
        im = Image.open(path)
        im.load()
        return im
    except Exception:
        tmp = pathlib.Path(tempfile.mkstemp(suffix=".jpg")[1])
        subprocess.run(["sips", "-s", "format", "jpeg", str(path), "--out", str(tmp)],
                       check=True, capture_output=True)
        im = Image.open(tmp)
        im.load()
        return im


def save(im, path, longest, q):
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    w, h = im.size
    s = min(1.0, longest / max(w, h))
    if s < 1.0:
        im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=q, optimize=True, progressive=True)
    return im.size


def band_from_text(text):
    t = re.sub(r"(\d)([a-z])", r"\1 \2", text.lower())
    m = re.search(r"\bs\s?([1-6])\b", t)
    if m:
        return BANDS["S" + m.group(1)]
    for key, band in LEVELS.items():
        if key.lower() in t:
            return band
    return ""


def band_from_folder(parts):
    for seg in parts:
        m = re.match(r"s([1-6])\s*-\s*s?([1-6])", seg.strip().lower())
        if m:
            return BANDS["S" + m.group(1)]
    return ""


def load_scorecard(path):
    """name tokens -> band. Local lookup only; nothing here is ever written out."""
    out = []
    if not path:
        return out
    for r in csv.reader(open(path, encoding="utf-8", errors="replace")):
        if len(r) < 3 or not r[0].strip() or "example" in r[2].lower():
            continue
        cat = r[1].strip().upper().replace(" ", "")
        m = re.match(r"S([1-6])-S([1-6])", cat)
        if not m:
            continue
        toks = re.findall(r"[a-z]+", r[2].lower())
        if len(toks) >= 2:
            out.append((toks[0], toks[-1], BANDS["S" + m.group(1)]))
    return out


def band_from_scorecard(filename, table):
    toks = re.findall(r"[a-z]+", filename.lower())
    best, best_score = "", 0.0
    for first, last, band in table:
        f = max((difflib.SequenceMatcher(None, first, t).ratio() for t in toks), default=0)
        l = max((difflib.SequenceMatcher(None, last, t).ratio() for t in toks), default=0)
        if f >= 0.8 and l >= 0.8 and f + l > best_score:
            best, best_score = band, f + l
    return best


def ingest_entries(schools_dir, scorecard):
    # clear previous 2026 entry outputs only
    for slug, _ in SCHOOLS.values():
        shutil.rmtree(ENTRIES / YEAR / slug, ignore_errors=True)
    shutil.rmtree(ENTRIES / YEAR, ignore_errors=True)

    items, unresolved = [], []
    for sdir in sorted(p for p in schools_dir.iterdir() if p.is_dir()):
        key = sdir.name.strip().lower()
        if key not in SCHOOLS:
            print("  ?? unknown school folder:", sdir.name)
            continue
        for p in sorted(sdir.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in RASTER or p.name.startswith("."):
                continue
            rel = p.relative_to(sdir).parts[:-1]
            band = band_from_text(p.name) or band_from_folder(rel) or band_from_scorecard(p.name, scorecard)
            if not band:
                unresolved.append((sdir.name, p.name))
            items.append((key, band, p))

    groups = {}
    for key, band, p in items:
        groups.setdefault(key, {}).setdefault(band, []).append(p)

    manifest = {}
    total = 0
    for key, bands in groups.items():
        slug, label = SCHOOLS[key]
        s = {"label": label, "count": 0, "groups": {}}
        for band, paths in bands.items():
            paths = sorted(paths, key=lambda p: hashlib.md5(p.name.encode()).hexdigest())
            for i, src in enumerate(paths, 1):
                stem = f"{YEAR}-{slug}" + (f"-{band.lower().replace('–', '-')}" if band else "") + f"-{i:02d}"
                full = f"assets/entries/{YEAR}/{slug}/{stem}.jpg"
                thumb = f"assets/entries/{YEAR}/{slug}/thumb/{stem}.jpg"
                try:
                    im = load_image(src)
                    save(im, SITE / full, ENTRY_FULL, 78)
                    save(im, SITE / thumb, ENTRY_THUMB, 70)
                except Exception as e:
                    print("  !! failed:", e)
                    continue
                s["groups"].setdefault(band, []).append({"full": full, "thumb": thumb})
                s["count"] += 1
                total += 1
        manifest[slug] = s
    return manifest, total, unresolved


def ingest_events(events_dir):
    shutil.rmtree(EVENTS, ignore_errors=True)
    files = sorted(p for p in events_dir.iterdir()
                   if p.is_file() and p.suffix.lower() in RASTER and not p.name.startswith("."))
    out = []
    for i, src in enumerate(files, 1):
        stem = f"2026-event-{i:02d}"
        im = load_image(src)
        w, h = save(im, EVENTS / f"{stem}.jpg", EVENT_FULL, 78)
        save(im, EVENTS / "thumb" / f"{stem}.jpg", EVENT_THUMB, 70)
        out.append({"full": f"assets/events/2026/{stem}.jpg",
                    "thumb": f"assets/events/2026/thumb/{stem}.jpg", "w": w, "h": h})
    (EVENTS / "manifest.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schools", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--scorecard")
    a = ap.parse_args()

    table = load_scorecard(a.scorecard)
    m2026, n, unresolved = ingest_entries(pathlib.Path(a.schools), table)

    mpath = ENTRIES / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
    manifest[YEAR] = m2026
    mpath.write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    ev = ingest_events(pathlib.Path(a.events))

    print(f"\n2026 entries: {n}")
    for slug, d in m2026.items():
        print(f"  {d['label']:<34} {d['count']:>3}  " +
              ", ".join(f"{k or 'unstaged'}:{len(v)}" for k, v in d["groups"].items()))
    print(f"event photos: {len(ev)}")
    if unresolved:
        print("\nNo year group found for (check by hand):")
        for s, f in unresolved:
            print("  ", s, "|", f)


if __name__ == "__main__":
    main()
