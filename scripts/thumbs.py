"""Build the project covers the README's cards embed.

Pipeline (deterministic for a given Pillow/libwebp build):
  media/covers/<file>  --crop + Lanczos-->  media/thumbs/<slug>.webp          desktop, 712x298
                                            media/thumbs/<slug>-mobile.webp   phones,  384x234
scripts/build.py inlines them (base64) into the card images, inside each project's aperture.

Usage:
  python scripts/thumbs.py                         # rebuild from media/covers/
  python scripts/thumbs.py --import-from DIR       # first copy missing covers from DIR
  python scripts/thumbs.py --sheet DIR             # also write a contact sheet per size for review

Each crop is given as fractions of the source: its left and right edges (x0, x1) and its
vertical centre (cy); its height follows from the size's aspect ratio.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
COVERS = ROOT / "media" / "covers"
THUMBS = ROOT / "media" / "thumbs"

# Pixel size per breakpoint: the cover slot inside an aperture (build.GRID: the aperture less
# case + ring on each side) at 2x on desktop (356 x 149 units, 1 px each) and at ~3x on
# phones (146 x 89 units, ~0.86 px each). The aspect ratios must match the slots; build.py
# checks them.
SIZES = {"desktop": (712, 298), "mobile": (384, 234)}
SUFFIX = {"desktop": "", "mobile": "-mobile"}
WEBP_QUALITY, WEBP_METHOD = 82, 6

# slug: (cover file, {breakpoint: (x0, x1, cy)}), fractions of the source's width (x0, x1:
# the crop's left and right edges) and height (cy: the crop's vertical centre); the height
# follows from the size's aspect ratio. The wide desktop crops show the whole scene, the
# taller phone crops close in on its subject.
PROJECTS: dict[str, tuple[str, dict[str, tuple[float, float, float]]]] = {
    "nedirbeo":        ("nedirbeo.webp",        {"desktop": (0.272, 0.873, 0.555),     # the word-of-the-day card
                                                 "mobile":  (0.283, 0.620, 0.522)}),
    "wipeout":         ("wipeout.webp",         {"desktop": (0.015, 0.981, 0.481),     # character select
                                                 "mobile":  (0.019, 0.595, 0.440)}),
    "hesappcim":       ("hesappcim.jpg",        {"desktop": (0.229, 0.636, 0.325),     # "You're owed TRY 0.00", 1.25x, the device edge across the corner
                                                 "mobile":  (0.343, 0.643, 0.299)}),
    "yayla-yemek-evi": ("yayla-yemek-evi.webp", {"desktop": (0.179, 0.777, 0.477),     # the site on the laptop's screen
                                                 "mobile":  (0.200, 0.705, 0.475)}),
}


def crop_box(size: tuple[int, int], crop: tuple[float, float, float],
             out: tuple[int, int]) -> tuple[float, float, float, float]:
    """The pixel box x0..x1 across, centred on cy, with out's aspect ratio, clamped inside."""
    W, H = size
    x0, x1, cy = crop
    w = (x1 - x0) * W
    h = w * out[1] / out[0]
    if h > H:                          # too tall for the source: shrink around the centre
        h = float(H)
        w = h * out[0] / out[1]
    cx = (x0 + x1) / 2 * W
    left = min(max(cx - w / 2, 0.0), W - w)
    top = min(max(cy * H - h / 2, 0.0), H - h)
    return (left, top, left + w, top + h)


def make_thumb(src: Path, crop, out: tuple[int, int]) -> tuple[Image.Image, tuple[float, float, float, float]]:
    with Image.open(src) as im:
        im = im.convert("RGB")
        box = crop_box(im.size, crop, out)
        return im.resize(out, Image.Resampling.LANCZOS, box=box), box


def encode_webp(im: Image.Image, path: Path) -> int:
    # exact=False and no metadata keep the output byte-stable across runs
    im.save(path, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
    return path.stat().st_size


def contact_sheet(thumbs: list[Image.Image], size: tuple[int, int], path: Path) -> Path:
    """The thumbs side by side on the plate's colour, at their pixel size."""
    pad = 16
    sheet = Image.new("RGB", (pad + len(thumbs) * (size[0] + pad), size[1] + 2 * pad), "#101216")
    for i, im in enumerate(thumbs):
        sheet.paste(im, (pad + i * (size[0] + pad), pad))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--import-from", type=Path, help="copy covers missing from media/covers/ out of this dir")
    ap.add_argument("--sheet", type=Path, help="write review contact sheets into this dir")
    args = ap.parse_args(argv)

    COVERS.mkdir(parents=True, exist_ok=True)
    THUMBS.mkdir(parents=True, exist_ok=True)
    built: dict[str, list[Image.Image]] = {bp: [] for bp in SIZES}
    for slug, (fname, crops) in PROJECTS.items():
        cover = COVERS / fname
        if not cover.exists():
            if args.import_from and (args.import_from / fname).exists():
                shutil.copy2(args.import_from / fname, cover)
                print(f"imported {fname}")
            else:
                print(f"missing cover: {cover}", file=sys.stderr)
                return 1
        with Image.open(cover) as c:
            W, H = c.size
        for bp, size in SIZES.items():
            im, box = make_thumb(cover, crops[bp], size)
            n = encode_webp(im, THUMBS / f"{slug}{SUFFIX[bp]}.webp")
            fx = (box[0] / W, box[1] / H, box[2] / W, box[3] / H)
            print(f"{slug + SUFFIX[bp]:23} crop x {fx[0]:.3f}-{fx[2]:.3f} y {fx[1]:.3f}-{fx[3]:.3f}  webp {n:7,d} B")
            built[bp].append(im)
    if args.sheet:
        for bp, ims in built.items():
            print("sheet", contact_sheet(ims, SIZES[bp], args.sheet / f"thumbs-{bp}.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
