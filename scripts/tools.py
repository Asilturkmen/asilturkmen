"""The "Tools I use" strip: brand icons with names, drawn as one SVG.

    tools_strip(theme, mobile, faces) -> str
        complete SVG for THEMES[theme]; desktop 846 x 108 (two justified rows
        of icon + name), mobile 360 x 150 (icons only, six to a row).

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

__all__ = ["TOOLS", "tools_strip"]

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
ROW_SPLIT = 8          # desktop: first row TypeScript .. Laravel, second row Python .. Vercel
MOBILE_PER_ROW = 6

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
    target = MIN_CONTRAST[theme]
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


# ----------------------------------------------------------------- drawing
def _num(v: float, nd: int = 2) -> str:
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _icon(slug: str, cx: float, cy: float, size: float, fill: str) -> str:
    """A 24-unit Simple Icons glyph centred on (cx, cy) in a size x size slot."""
    k = size * OPTICAL.get(slug, 1.0) / 24
    return (f'<path transform="translate({_num(cx - 12 * k)} {_num(cy - 12 * k)}) scale({_num(k, 4)})" '
            f'fill="{fill}" d="{ICONS[slug]["d"]}"/>')


def tools_strip(theme: str, mobile: bool, faces: dict) -> str:
    # build.py imports this module, so its helpers are imported at call time
    from build import THEMES, frame

    t = THEMES[theme]
    fills = {slug: icon_fill(hex_, theme, t) for slug, _, _, hex_ in TOOLS}
    title = "Tools I use: " + ", ".join(name for _, name, _, _ in TOOLS) + "."
    parts = []

    if mobile:
        W, H = 360, 150
        size, margin = 22, 24
        pitch_x = (W - 2 * margin) / MOBILE_PER_ROW
        row_cy = (33, 75, 117)
        rows = [TOOLS[i:i + MOBILE_PER_ROW] for i in range(0, len(TOOLS), MOBILE_PER_ROW)]
        for r, row in enumerate(rows):
            # a short last row is centred on the same pitch
            x0 = margin + (MOBILE_PER_ROW - len(row)) * pitch_x / 2
            for i, (slug, _, si, _) in enumerate(row):
                cx = x0 + pitch_x * (i + 0.5)
                parts.append(_icon(si, cx, row_cy[r], size, fills[slug]))
    else:
        W, H = 846, 108
        size, gap, margin = 18, 8, 56
        face = faces[500]
        cap = face.cap_height(13)
        row_cy = (33, 75)
        rows = [TOOLS[:ROW_SPLIT], TOOLS[ROW_SPLIT:]]
        for r, row in enumerate(rows):
            runs = [face.layout(name, 13) for _, name, _, _ in row]
            widths = [size + gap + run.width for run in runs]
            space = (W - 2 * margin - sum(widths)) / (len(row) - 1)
            cy, x = row_cy[r], float(margin)
            for i, ((slug, _, si, _), run) in enumerate(zip(row, runs)):
                parts.append(_icon(si, x + size / 2, cy, size, fills[slug]))
                parts.append(run.path(x + size + gap, cy + cap / 2, t["ink2"]))
                x += widths[i]
                if i < len(row) - 1:
                    parts.append(f'<circle cx="{_num(x + space / 2)}" cy="{_num(cy)}" r="1.2" '
                                 f'fill="{t["muted"]}" fill-opacity="0.45"/>')
                    x += space
        # hairline between the rows, fading out at both ends
        parts.append(f'<rect x="{margin - 24}" y="54" width="{W - 2 * margin + 48}" height="1" fill="url(#rule)"/>')

    defs, body, border = frame(W, H, t)
    if not mobile:
        defs += ('\n<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
                 f'<stop offset="0" stop-color="{t["border"]}" stop-opacity="0"/>'
                 f'<stop offset="0.05" stop-color="{t["border"]}"/><stop offset="0.95" stop-color="{t["border"]}"/>'
                 f'<stop offset="1" stop-color="{t["border"]}" stop-opacity="0"/></linearGradient>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<defs>
{defs}
</defs>
<g clip-path="url(#frame)">
{body}
{chr(10).join(parts)}
{border}
</g>
</svg>
'''
