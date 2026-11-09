"""The tools I use: brand icons, their names and colours.

    TOOLS                                  (slug, display name, simple-icons slug, brand hex)
    icon_fill(brand, theme, t) -> str      the brand colour, corrected for contrast on the surface
    tint(grey, colour, k) -> str           grey moved k of the way to colour, in Oklab
    icon(slug, cx, cy, size, fill) -> str  one Simple Icons glyph centred on (cx, cy)
    icon_bounds(slug, size) -> box         what that glyph really covers, centred on the origin

scripts/orbit.py draws them circling the asilturkmen.com lockup; build.py
borrows the GitHub mark for the Code buttons.

Icon outlines and brand colours come from Simple Icons and are vendored in
scripts/icons.json, so the build needs no network and is deterministic.
A brand colour is used as is unless it would vanish into the surface: black or
white marks (Next.js, Vercel and Flask on dark, Unity on light) take the
theme's ink, and coloured marks that are too dark or too pale (SQLite and C# on
dark, React on light) keep their hue and move in OKLCH lightness just far
enough to reach MIN_CONTRAST against the surface.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path

__all__ = ["TOOLS", "OPTICAL", "icon_fill", "tint", "icon", "icon_bounds"]

ICONS = json.loads((Path(__file__).resolve().parent / "icons.json").read_text(encoding="utf-8"))

# (slug, display name, simple-icons slug, brand hex)
TOOLS = [
    ("typescript", "TypeScript", "typescript", "#3178c6"),
    ("react", "React", "react", "#61dafb"),
    ("nextjs", "Next.js", "nextdotjs", "#000000"),
    ("vue", "Vue", "vuedotjs", "#4fc08d"),
    ("vite", "Vite", "vite", "#646cff"),
    ("tailwind", "Tailwind CSS", "tailwindcss", "#06b6d4"),
    ("nodejs", "Node.js", "nodedotjs", "#5fa04e"),
    ("laravel", "Laravel", "laravel", "#ff2d20"),
    ("python", "Python", "python", "#3776ab"),
    ("flask", "Flask", "flask", "#000000"),
    ("postgresql", "PostgreSQL", "postgresql", "#4169e1"),
    ("sqlite", "SQLite", "sqlite", "#003b57"),
    ("unity", "Unity", "unity", "#ffffff"),
    ("csharp", "C#", "csharp", "#512bd4"),
    ("docker", "Docker", "docker", "#2496ed"),
    ("git", "Git", "git", "#f05032"),
    ("vercel", "Vercel", "vercel", "#000000"),
]
assert all(ICONS[si]["hex"] == hex_ for _, _, si, hex_ in TOOLS), "TOOLS and icons.json disagree"

# Simple Icons fill a 24-unit box edge to edge whatever the shape, so solid
# squares, discs and triangles look bigger than open or wide marks. These scale
# factors (about the icon's centre) even out the optical size.
OPTICAL = {
    "typescript": 0.88, "nextdotjs": 0.92, "vercel": 0.88, "csharp": 0.94,
    "python": 0.96, "sqlite": 0.96, "tailwindcss": 1.06, "docker": 1.04,
}

# Minimum contrast of an icon against the surface (WCAG ratio). The light floor
# is low on purpose: Vue, Tailwind and Node.js keep their own colours and only
# React's pale cyan is deepened a little.
MIN_CONTRAST = {"dark": 3.5, "light": 1.8}
NEUTRAL_CHROMA = 0.03  # OKLCH chroma below which a mark counts as black/white/grey


# ----------------------------------------------------------------- colour
def _hex(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _to_hex(rgb) -> str:
    return "#" + "".join(f"{round(min(1.0, max(0.0, c)) * 255):02x}" for c in rgb)


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _lum(rgb) -> float:
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _oklch(rgb):
    r, g, b = (_lin(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.atan2(B, A)


def _rgb(L, C, H):
    """OKLCH -> linear sRGB (may fall outside 0..1)."""
    A, B = C * math.cos(H), C * math.sin(H)
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def _in_gamut(L, C, H) -> tuple[float, float, float]:
    """sRGB colour at (L, H) with the largest chroma <= C that fits the gamut."""
    lo, hi = 0.0, C
    for _ in range(24):
        mid = (lo + hi) / 2
        if all(-1e-6 <= v <= 1 + 1e-6 for v in _rgb(L, mid, H)):
            lo = mid
        else:
            hi = mid
    return tuple(_gam(min(1.0, max(0.0, v))) for v in _rgb(L, lo, H))


def surface_of(t: dict):
    """The frame's diagonal gradient, averaged."""
    a, b = _hex(t["bg0"]), _hex(t["bg1"])
    return tuple((x + y) / 2 for x, y in zip(a, b))


def icon_fill(brand: str, theme: str, t: dict) -> str:
    surf = surface_of(t)
    rgb = _hex(brand)
    target = MIN_CONTRAST["dark" if _lum(surf) < 0.18 else "light"]
    if contrast(rgb, surf) >= target:
        return brand
    L, C, H = _oklch(rgb)
    if C < NEUTRAL_CHROMA:
        return t["ink"]
    # keep hue, walk lightness away from the surface until the contrast is reached
    # (aim a hair above the target so rounding to 8-bit hex cannot undershoot it)
    up = _lum(surf) < 0.18
    lo, hi = (L, 1.0) if up else (0.0, L)
    for _ in range(30):
        mid = (lo + hi) / 2
        ok = contrast(_in_gamut(mid, C, H), surf) >= target + 0.02
        if up:
            hi, lo = (mid, lo) if ok else (hi, mid)
        else:
            lo, hi = (mid, hi) if ok else (lo, mid)
    return _to_hex(_in_gamut(hi if up else lo, C, H))


def tint(grey: str, colour: str, k: float) -> str:
    """grey moved k (0..1) of the way to colour, interpolated in Oklab: lightness
    and chroma move together along a straight line towards the colour, so the
    midpoints are quiet versions of it, never a muddy grey-brown."""
    if k <= 0:
        return grey
    if k >= 1:
        return colour
    (L0, C0, H0), (L1, C1, H1) = _oklch(_hex(grey)), _oklch(_hex(colour))
    a0, b0, a1, b1 = C0 * math.cos(H0), C0 * math.sin(H0), C1 * math.cos(H1), C1 * math.sin(H1)
    L, A, B = L0 + (L1 - L0) * k, a0 + (a1 - a0) * k, b0 + (b1 - b0) * k
    return _to_hex(_in_gamut(L, math.hypot(A, B), math.atan2(B, A)))


# ----------------------------------------------------------------- drawing
def _num(v: float, nd: int = 2) -> str:
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def icon(slug: str, cx: float, cy: float, size: float, fill: str, inner: str = "") -> str:
    """A 24-unit Simple Icons glyph centred on (cx, cy) in a size x size slot: one
    <path> with one fill. `inner` (e.g. an <animate> of the fill) goes inside it."""
    k = size * OPTICAL.get(slug, 1.0) / 24
    head = (f'<path transform="translate({_num(cx - 12 * k)} {_num(cy - 12 * k)}) scale({_num(k, 4)})" '
            f'fill="{fill}" d="{ICONS[slug]["d"]}"')
    return f"{head}>{inner}</path>" if inner else f"{head}/>"


_BOUNDS: dict[str, tuple] = {}


def icon_bounds(slug: str, size: float) -> tuple[float, float, float, float]:
    """Bounding box (x0, y0, x1, y1) of the outline icon(slug, 0, 0, size, ...) draws:
    what the glyph really covers, with its OPTICAL factor applied. Wide or short marks
    (Tailwind, Docker) cover much less than their square slot."""
    if slug not in _BOUNDS:
        pen = BoundsPen(None)
        parse_path(ICONS[slug]["d"], pen)
        _BOUNDS[slug] = pen.bounds
    k = size * OPTICAL.get(slug, 1.0) / 24
    x0, y0, x1, y1 = _BOUNDS[slug]
    return (x0 - 12) * k, (y0 - 12) * k, (x1 - 12) * k, (y1 - 12) * k
