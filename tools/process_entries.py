#!/usr/bin/env python3
"""Ingest pupil competition entries from the synced Google Drive folders,
strip all identifying info, resize for web, and write an anonymised manifest.

NO pupil names appear in output filenames, the manifest, or anywhere on the site.
Entries are grouped only by competition year -> school -> stage (S1..S6 / Primary).
"""

import hashlib
import json
import re
import pathlib
import subprocess
import tempfile

from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()


def load_image(path: pathlib.Path) -> Image.Image:
    """Open an image; fall back to macOS `sips` for HEICs Pillow can't parse."""
    try:
        im = Image.open(path)
        im.load()
        return im
    except Exception:
        tmp = pathlib.Path(tempfile.mkstemp(suffix=".jpg")[1])
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(path), "--out", str(tmp)],
            check=True, capture_output=True,
        )
        im = Image.open(tmp)
        im.load()
        return im

# Point these at the "JMM Art Prize" folders synced by Google Drive for Desktop.
# If Drive streaming is slow, copy the two "…submissions 20XX" folders to a local
# disk first (into <somewhere>/2024 and <somewhere>/2025) and set SRC_2024 / SRC_2025
# to those local copies instead.
DRIVE = pathlib.Path.home() / (
    "Library/CloudStorage/GoogleDrive-cjwstewart1@gmail.com/My Drive/JMM Art Prize"
)
SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = SITE / "assets" / "entries"

SRC_2024 = DRIVE / "JMM Art Prize 2024" / "Jackie Marno-McGoldrick Art Competition submissions 2024"
SRC_2025 = DRIVE / "JMM Art Prize 2025" / "Jackie Marno-McGoldrick Art Competition submissions 2025"

# The 2024 folder holds loose files (school code in the filename); the 2025 folder
# has one sub-folder per school. Both are handled below.

SCHOOLS = {
    "CHS":  ("clydebank-high-school",   "Clydebank High School"),
    "SPTA": ("st-peter-the-apostle",    "St Peter the Apostle High School"),
    "DA":   ("dumbarton-academy",       "Dumbarton Academy"),
    "VOLA": ("vale-of-leven-academy",   "Vale of Leven Academy"),
    "OLSP": ("our-lady-and-st-patricks","Our Lady and St Patrick's High School"),
    "GAVINBURN": ("gavinburn-primary",  "Gavinburn Primary School"),
}
FOLDER_TO_CODE = {
    "clydebank high school": "CHS",
    "st peter the apostle": "SPTA",
    "dumbarton academy": "DA",
    "vale of leven": "VOLA",
}

SKIP_SUBSTR = ("joe_bloggs", "thumbs.db")
SKIP_EXT = {".gsheet", ".gslides", ".pdf", ".db", ".ini"}
RASTER_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}

FULL_MAX = 1400
FULL_Q = 78
THUMB_MAX = 520
THUMB_Q = 70


def stage_from_name(name: str) -> str:
    n = re.sub(r"(\d)([a-z])", r"\1 \2", name.lower())  # split "s6spta" -> "s6 spta"
    if re.search(r"\bp\s?[67]\b", n) or "gavinburn" in n:
        return "Primary"
    m = re.search(r"\bs\s?([1-6])\b", n)
    if m:
        return "S" + m.group(1)
    return ""


def code_from_2024_name(name: str) -> str:
    up = " " + name.upper().replace(".", " ") + " "
    if "GAVINBURN" in up:
        return "GAVINBURN"
    # space-delimited first
    for code in ("SPTA", "OLSP", "VOLA", "CHS", "DA"):
        if f" {code} " in up:
            return code
    # 4-letter codes are unambiguous even when jammed against a stage ("S6SPTA")
    for code in ("SPTA", "OLSP", "VOLA"):
        if code in up:
            return code
    return ""


def save_variant(im: Image.Image, path: pathlib.Path, longest: int, q: int) -> None:
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    w, h = im.size
    scale = min(1.0, longest / max(w, h))
    if scale < 1.0:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=q, optimize=True, progressive=True)


def collect():
    """Return list of (year, code, stage, src_path)."""
    items = []

    # ---- 2024: loose files, school code in the filename
    for p in sorted(SRC_2024.iterdir()):
        if not p.is_file():
            continue
        low = p.name.lower()
        if any(s in low for s in SKIP_SUBSTR) or p.suffix.lower() in SKIP_EXT:
            continue
        if p.suffix.lower() not in RASTER_EXT:
            continue
        code = code_from_2024_name(p.name)
        if not code:
            print("  ?? 2024 no school:", p.name)
            continue
        items.append(("2024", code, stage_from_name(p.name), p))

    # ---- 2025: per-school folders (CHS has stage subfolders)
    for school_dir in sorted(SRC_2025.iterdir()):
        if not school_dir.is_dir():
            continue
        code = FOLDER_TO_CODE.get(school_dir.name.strip().lower())
        if not code:
            print("  ?? 2025 unknown folder:", school_dir.name)
            continue
        for p in sorted(school_dir.rglob("*")):
            if not p.is_file():
                continue
            low = p.name.lower()
            if any(s in low for s in SKIP_SUBSTR) or p.suffix.lower() in SKIP_EXT:
                continue
            if p.suffix.lower() not in RASTER_EXT:
                continue
            stage = stage_from_name(p.name)
            if not stage:
                # fall back to CHS subfolder name like "s5-6"
                rel = p.relative_to(school_dir).parts
                if rel and re.match(r"s[1-6]", rel[0].lower()):
                    seg = rel[0].lower().replace("s", "S").replace("-", "–")
                    stage = "S" + seg[1:]
            items.append(("2025", code, stage, p))
    return items


def main():
    if OUT.exists():
        for p in sorted(OUT.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
    items = collect()
    print(f"collected {len(items)} entry images")

    # group -> anonymised order (hash of original name, never alphabetical)
    groups: dict = {}
    for year, code, stage, path in items:
        groups.setdefault((year, code), {}).setdefault(stage, []).append(path)

    manifest: dict = {}
    total = 0
    for (year, code), stages in sorted(groups.items()):
        slug, label = SCHOOLS[code]
        ymani = manifest.setdefault(year, {})
        smani = ymani.setdefault(slug, {"label": label, "count": 0, "groups": {}})
        for stage, paths in stages.items():
            paths = sorted(paths, key=lambda p: hashlib.md5(p.name.encode()).hexdigest())
            arr = []
            for i, src in enumerate(paths, 1):
                stem = f"{year}-{slug}"
                if stage:
                    stem += "-" + stage.lower().replace("–", "-")
                stem += f"-{i:02d}"
                full_rel = f"assets/entries/{year}/{slug}/{stem}.jpg"
                thumb_rel = f"assets/entries/{year}/{slug}/thumb/{stem}.jpg"
                try:
                    im = load_image(src)
                    save_variant(im, SITE / full_rel, FULL_MAX, FULL_Q)
                    save_variant(im, SITE / thumb_rel, THUMB_MAX, THUMB_Q)
                except Exception as e:
                    print("  !! failed", src.name, "->", e)
                    continue
                arr.append({"full": full_rel, "thumb": thumb_rel})
                total += 1
            if arr:
                smani["groups"].setdefault(stage or "", []).extend(arr)
                smani["count"] += len(arr)

    (OUT).mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    print(f"\nwrote {total} images")
    for year in sorted(manifest, reverse=True):
        print(f"  {year}:")
        for slug, d in manifest[year].items():
            stages = ", ".join(f"{k or 'unstaged'}:{len(v)}" for k, v in d["groups"].items())
            print(f"    {d['label']:<34} {d['count']:>3}   ({stages})")


if __name__ == "__main__":
    main()
