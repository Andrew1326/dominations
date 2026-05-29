#!/usr/bin/env python3
"""
Crop served building sprites to their content and re-center on a square canvas.

Blender renders frame each building loosely inside a large transparent canvas,
and the amount of empty margin varies per building. That makes catalog
thumbnails look small and inconsistently sized. This tool tight-crops each PNG
to its opaque bounding box, then centers it on a square transparent canvas with
a small uniform margin, so every building fills its thumbnail consistently.

Idempotent: re-running on an already-cropped image is a no-op (within rounding).

Usage:
  python3 blender/crop_building_assets.py
  python3 blender/crop_building_assets.py --dir client/public/assets/buildings
  python3 blender/crop_building_assets.py --margin 0.08
"""

import argparse
import glob
import os

from PIL import Image

DEFAULT_DIR = "client/public/assets/buildings"
ALPHA_THRESHOLD = 16  # alpha values <= this are treated as empty


def content_bbox(im: Image.Image):
    """Bounding box of pixels that are meaningfully opaque, or None if empty."""
    alpha = im.split()[-1]
    mask = alpha.point(lambda a: 255 if a > ALPHA_THRESHOLD else 0)
    return mask.getbbox()


def crop_square(im: Image.Image, margin: float) -> Image.Image:
    bbox = content_bbox(im)
    if not bbox:
        return im  # fully transparent, nothing to do

    cropped = im.crop(bbox)
    cw, ch = cropped.size

    # Square side large enough for the content plus a uniform margin
    side = max(cw, ch)
    pad = int(round(side * margin))
    canvas_side = side + pad * 2

    canvas = Image.new("RGBA", (canvas_side, canvas_side), (0, 0, 0, 0))
    offset = ((canvas_side - cw) // 2, (canvas_side - ch) // 2)
    canvas.paste(cropped, offset)
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description="Tight-crop building sprites.")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="Asset directory to process")
    parser.add_argument("--margin", type=float, default=0.08, help="Padding as fraction of content side")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "**", "*.png"), recursive=True))
    if not files:
        print(f"No PNGs found under {args.dir}")
        return

    changed = 0
    for f in files:
        im = Image.open(f).convert("RGBA")
        out = crop_square(im, args.margin)
        if out.size != im.size:
            out.save(f)
            changed += 1
            print(f"cropped {f}: {im.size[0]}x{im.size[1]} -> {out.size[0]}x{out.size[1]}")
        else:
            print(f"skipped {f}: already tight")

    print(f"\nDone. Cropped {changed}/{len(files)} images.")


if __name__ == "__main__":
    main()
