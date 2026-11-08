"""Build the small project thumbnails used in the README.

Pipeline (deterministic for a given Pillow/libwebp build):
  media/covers/<file>  --16:10 crop + Lanczos-->  media/thumbs/<slug>.webp (288x180)
                       --base64 inline-->         assets/thumb-<slug>.svg (144x90 viewBox)

Usage:
  python scripts/thumbs.py                         # rebuild from media/covers/
  python scripts/thumbs.py --import-from DIR       # first copy missing covers from DIR
  python scripts/thumbs.py --sheet DIR             # also write contact sheets for review

Crop boxes are fractions of the source width/height. Only the width (x0..x1) and the
vertical centre of the box are used: the height is derived so the crop is exactly 16:10.
"""
from __future__ import annotations

import argparse
import base64
import io
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
COVERS = ROOT / "media" / "covers"
THUMBS = ROOT / "media" / "thumbs"
ASSETS = ROOT / "assets"

THUMB_W, THUMB_H = 368, 230          # 2x of the 184x104 card slot (16:10 crop, sliced to 16:9 in the card)
SVG_W, SVG_H, RADIUS = 144, 90, 8
WEBP_QUALITY, WEBP_METHOD = 82, 6

# slug: (title, cover file, (x0, y0, x1, y1) as fractions of the source)
PROJECTS: dict[str, tuple[str, str, tuple[float, float, float, float]]] = {
    "nedirbeo":        ("NedirBeo",        "nedirbeo.webp",        (0.270, 0.324, 0.620, 0.736)),
    "wipeout":         ("Wipeout",         "wipeout.webp",         (0.050, 0.198, 0.570, 0.671)),
    "hesappcim":       ("HesAppc\u0131m",  "hesappcim.jpg",        (0.300, 0.170, 0.630, 0.410)),
    "yayla-yemek-evi": ("Yayla Yemek Evi", "yayla-yemek-evi.webp", (0.160, 0.122, 0.750, 0.778)),
}


def crop_box(size: tuple[int, int], frac: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """Return a float pixel box of exactly THUMB_W:THUMB_H, centred on the given box, clamped inside."""
    W, H = size
    x0, y0, x1, y1 = frac
    w = (x1 - x0) * W
    h = w * THUMB_H / THUMB_W
    if h > H:                          # too tall for the source: shrink around the centre
        h = float(H)
        w = h * THUMB_W / THUMB_H
    cx = (x0 + x1) / 2 * W
    cy = (y0 + y1) / 2 * H
    left = min(max(cx - w / 2, 0.0), W - w)
    top = min(max(cy - h / 2, 0.0), H - h)
    return (left, top, left + w, top + h)


def make_thumb(src: Path, frac) -> tuple[Image.Image, tuple[float, float, float, float]]:
    with Image.open(src) as im:
        im = im.convert("RGB")
        box = crop_box(im.size, frac)
        return im.resize((THUMB_W, THUMB_H), Image.Resampling.LANCZOS, box=box), box


def encode_webp(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    # exact=False and no metadata keep the output byte-stable across runs
    im.save(buf, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
    return buf.getvalue()


def svg_for(title: str, webp: bytes, slug: str) -> str:
    b64 = base64.b64encode(webp).decode("ascii")
    cid = f"c-{slug}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}" role="img">'
        f"<title>{title}</title>"
        f'<defs><clipPath id="{cid}"><rect width="{SVG_W}" height="{SVG_H}" rx="{RADIUS}"/></clipPath></defs>'
        f'<image clip-path="url(#{cid})" width="{SVG_W}" height="{SVG_H}" preserveAspectRatio="xMidYMid slice" '
        f'href="data:image/webp;base64,{b64}"/>'
        f'<rect x="0.5" y="0.5" width="{SVG_W - 1}" height="{SVG_H - 1}" rx="{RADIUS - 0.5}" fill="none" '
        f'stroke="#808080" stroke-opacity="0.35" stroke-width="1"/>'
        "</svg>\n"
    )


def contact_sheets(thumbs: list[tuple[str, Image.Image]], out_dir: Path) -> list[Path]:
    """Thumbs at 144x90 (72x45 CSS @2x) and 72x45 (@1x), on light and dark rows."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for tag, (w, h), pad in (("2x", (144, 90), 16), ("1x", (72, 45), 8)):
        r = max(1, round(RADIUS * w / SVG_W))
        cols = len(thumbs)
        sheet = Image.new("RGB", (pad + cols * (w + pad), 2 * (h + pad) + pad), "#ffffff")
        ImageDraw.Draw(sheet).rectangle([0, h + pad + pad // 2, sheet.width, sheet.height], fill="#0d1117")
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
        for row in range(2):
            for i, (_, im) in enumerate(thumbs):
                small = im.resize((w, h), Image.Resampling.LANCZOS)
                sheet.paste(small, (pad + i * (w + pad), pad + row * (h + pad)), mask)
        p = out_dir / f"thumbs-sheet-{tag}.png"
        sheet.save(p)
        paths.append(p)
    return paths


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--import-from", type=Path, help="copy covers missing from media/covers/ out of this dir")
    ap.add_argument("--sheet", type=Path, help="write review contact sheets into this dir")
    args = ap.parse_args(argv)

    COVERS.mkdir(parents=True, exist_ok=True)
    THUMBS.mkdir(parents=True, exist_ok=True)
    built = []
    for slug, (title, fname, frac) in PROJECTS.items():
        cover = COVERS / fname
        if not cover.exists():
            if args.import_from and (args.import_from / fname).exists():
                shutil.copy2(args.import_from / fname, cover)
                print(f"imported {fname}")
            else:
                print(f"missing cover: {cover}", file=sys.stderr)
                return 1
        im, box = make_thumb(cover, frac)
        webp = encode_webp(im)
        (THUMBS / f"{slug}.webp").write_bytes(webp)
        svg = svg_for(title, webp, slug)  # kept for reference; the cards in build.py embed the WebP directly
        with Image.open(cover) as c:
            W, H = c.size
        fx = (box[0] / W, box[1] / H, box[2] / W, box[3] / H)
        print(f"{slug:16} crop x {fx[0]:.3f}-{fx[2]:.3f} y {fx[1]:.3f}-{fx[3]:.3f}  "
              f"webp {len(webp):6,d} B  svg {len(svg.encode()):6,d} B")
        built.append((slug, im))
    if args.sheet:
        for p in contact_sheets(built, args.sheet):
            print("sheet", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
