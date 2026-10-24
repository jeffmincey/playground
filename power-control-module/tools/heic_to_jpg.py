"""Write metadata-free JPEG copies of phone photos, ready to commit.

iPhone photos arrive as HEIC, which GitHub does not display, and carry EXIF
metadata including the GPS position where they were taken. This writes
NAME.jpg for each photo: rotated upright, colour profile kept, every other
piece of metadata dropped. Commit the JPEG, never the original (.heic is in
.gitignore).

Usage:
    python3 tools/heic_to_jpg.py PHOTO.HEIC... --out reference/
    python3 tools/heic_to_jpg.py PHOTO.HEIC --max-px 1600   # smaller copy

Needs Pillow and pillow-heif (pip install pillow-heif).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()


def to_jpeg(src: Path, out_dir: Path, max_px: int | None = None) -> Path:
    with Image.open(src) as original:
        icc = original.info.get("icc_profile")
        img = ImageOps.exif_transpose(original).convert("RGB")
    if max_px:
        img.thumbnail((max_px, max_px))
    dst = out_dir / f"{src.stem}.jpg"
    # Only what is passed here is written: no EXIF, so no GPS, device or time.
    img.save(dst, "JPEG", quality=90, icc_profile=icc)
    return dst


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("photos", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, help="output folder (default: next to each photo)")
    parser.add_argument("--max-px", type=int, help="longest side in pixels (default: full size)")
    args = parser.parse_args()
    for src in args.photos:
        print(to_jpeg(src, args.out or src.parent, args.max_px))


if __name__ == "__main__":
    main()
