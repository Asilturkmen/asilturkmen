"""Draw the profile README images.

Everything on github.com/Asilturkmen that is not plain text comes out of this
file: the hero (name, role, and a watch that counts the time you spend on the
page), the project cards with their Code / Live buttons, and the footer that
points to asilturkmen.com.

Each image is written in four variants: dark/light (chosen on GitHub with the
#gh-dark-mode-only / #gh-light-mode-only link fragments), desktop/mobile
(chosen with <picture> + max-width) and moving/still (chosen with
prefers-reduced-motion).

Text is drawn as paths from Satoshi (Fontshare). The licence allows outlines
but not embedding or committing the font files, so the fonts are downloaded
into scripts/.fonts/ (git-ignored) on first run.

    python scripts/build.py
"""
from __future__ import annotations

import base64
import io
import math
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from movement import movement, movement_defs  # skeleton watch, scripts/movement.py
except ImportError:  # pragma: no cover
    movement = movement_defs = None
from tools import tools_strip, _icon as brand_icon  # "Tools I use" strip, scripts/tools.py

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT_DIR = ROOT / "scripts" / ".fonts"
FONT_ZIP = "https://api.fontshare.com/v2/fonts/download/satoshi"
FONT_FILES = {
    900: "Satoshi_Complete/Fonts/OTF/Satoshi-Black.otf",
    700: "Satoshi_Complete/Fonts/OTF/Satoshi-Bold.otf",
    500: "Satoshi_Complete/Fonts/OTF/Satoshi-Medium.otf",
}

# ----------------------------------------------------------------- content
NAME = "Asil Türkmen"
ROLE_1 = "Full-stack developer"
ROLE_1_TAIL = "North Cyprus"
ROLE_2 = "Software Engineering student at EMU"
DIAL_LABEL = ("TIME ON", "THIS PAGE")
FOOT_KICKER = "MORE ABOUT MY WORK"
FOOT_DOMAIN = "asilturkmen.com"
FOOT_SUB = "projects · case studies · CV"

# (slug, name, live site, public repo or None when the code is private).
# The card links to the live site; under it sit a "Code" and a "Live" button
# side by side, or a single full-width "Live" button when there is no repo.
# Asil's one-line descriptions of the projects are in the README alt text.
PROJECTS = [
    ("nedirbeo", "NedirBeo", "https://nedirbeo.com", None),
    ("wipeout", "Wipeout", "https://eyll.itch.io/wipeout", None),
    ("hesappcim", "HesAppcım", "https://hes-appcim.vercel.app/login", "https://github.com/Asilturkmen/HesAppcim"),
    ("yayla-yemek-evi", "Yayla Yemek Evi", "https://www.yaylayemekevi.com", "https://github.com/Asilturkmen/Yaylayemekevi"),
]
MEDIA = ROOT / "media" / "thumbs"

# ----------------------------------------------------------------- palettes
THEMES = {
    "dark": dict(
        bg0="#101216", bg1="#161920", border="#272b34", sheen="#ffffff",
        ink="#f4f5f7", ink2="#c9ccd3", muted="#9a9ea8", accent="#d4b483",
        accent_dim="#8c7a5c", dial="#0c0e12", tick="#6b6f78", tick_major="#d4b483",
        hand="#e9eaee", hand_sec="#d4b483", cap="#101216",
    ),
    "light": dict(
        bg0="#f8f5ef", bg1="#efe9df", border="#d6cebf", sheen="#ffffff",
        ink="#17181c", ink2="#3a3d45", muted="#5f626a", accent="#7d6234",
        accent_dim="#bcae95", dial="#fdfbf7", tick="#a89f8f", tick_major="#7d6234",
        hand="#1f2127", hand_sec="#7d6234", cap="#f8f5ef",
    ),
}

# Still images (reduced motion) park the hands in the classic 10:10 pose.
STILL_POSE = dict(minute=60.0, second=300.0)


# ----------------------------------------------------------------- helpers
def num(v: float, nd: int = 1) -> str:
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fonts_ready() -> None:
    if all((FONT_DIR / Path(p).name).exists() for p in FONT_FILES.values()):
        return
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    print("downloading Satoshi from Fontshare ...")
    req = urllib.request.Request(FONT_ZIP, headers={"User-Agent": "readme-build"})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in FONT_FILES.values():
            (FONT_DIR / Path(member).name).write_bytes(z.read(member))
        (FONT_DIR / "FFL.txt").write_bytes(z.read("Satoshi_Complete/License/FFL.txt"))


class Face:
    """Shape a string with HarfBuzz and draw it as one SVG path."""

    def __init__(self, path: Path):
        blob = hb.Blob.from_file_path(str(path))
        self.face = hb.Face(blob)
        self.font = hb.Font(self.face)
        self.upem = self.face.upem
        tt = TTFont(str(path), lazy=True)
        self.cap = tt["OS/2"].sCapHeight or int(self.upem * 0.7)
        self.xh = tt["OS/2"].sxHeight or int(self.upem * 0.5)
        tt.close()

    def layout(self, text: str, size: float, tracking: float = 0.0):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        k = size / self.upem
        track = tracking * self.upem
        glyphs, x = [], 0.0
        infos, positions = buf.glyph_infos, buf.glyph_positions
        for i, (info, pos) in enumerate(zip(infos, positions)):
            glyphs.append((info.codepoint, (x + pos.x_offset) * k, pos.y_offset * k))
            x += pos.x_advance + (track if i < len(infos) - 1 else 0)
        return Run(self, glyphs, x * k, size)

    def cap_height(self, size: float) -> float:
        return self.cap * size / self.upem


class Run:
    def __init__(self, face: Face, glyphs, width: float, size: float):
        self.face, self.glyphs, self.width, self.size = face, glyphs, width, size

    def _draw(self, pen, x, y):
        k = self.size / self.face.upem
        for gid, dx, dy in self.glyphs:
            self.face.font.draw_glyph_with_pen(gid, TransformPen(pen, (k, 0, 0, -k, x + dx, y - dy)))

    def d(self, x: float, y: float, nd: int = 1) -> str:
        pen = SVGPathPen(None, ntos=lambda v: num(v, nd))
        self._draw(pen, x, y)
        return pen.getCommands()

    def path(self, x: float, y: float, fill: str, nd: int | None = None, extra: str = "") -> str:
        nd = nd if nd is not None else (2 if self.size < 12 else 1)
        return f'<path d="{self.d(x, y, nd)}" fill="{fill}"{extra}/>'

    def bbox(self, x=0.0, y=0.0):
        bp = BoundsPen(None)
        self._draw(bp, x, y)
        return bp.bounds


def frame(W: int, H: int, t: dict) -> tuple[str, str]:
    """Rounded surface with a 1px border and a faint top highlight."""
    defs = f'''<clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['sheen']}" stop-opacity="0"/><stop offset="0.5" stop-color="{t['accent']}" stop-opacity="0.35"/><stop offset="1" stop-color="{t['sheen']}" stop-opacity="0"/></linearGradient>'''
    body = f'<rect width="{W}" height="{H}" fill="url(#surface)"/>'
    border = (f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["border"]}"/>'
              f'<rect x="24" y="0.5" width="{W - 48}" height="1" fill="url(#sheen)"/>')
    return defs, body, border


# ----------------------------------------------------------------- the watch
def watch(cx: float, cy: float, r: float, t: dict, faces: dict, still: bool, label_size: float) -> str:
    """A dial whose hands start at 12:00 when the image loads and then run at
    real speed: it shows how long the visitor has been on the page."""
    out = []
    out.append(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}" fill="{t["dial"]}" stroke="{t["border"]}"/>')
    out.append(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r - 4)}" fill="none" stroke="{t["accent"]}" stroke-opacity="0.18" stroke-width="0.6"/>')
    # minute track: 60 ticks, hours stronger, quarters longest
    minor, major, quarter = [], [], []
    for i in range(60):
        a = math.radians(i * 6 - 90)
        if i % 15 == 0:
            r0, r1 = r - 18, r - 8
            quarter.append((a, r0, r1))
        elif i % 5 == 0:
            r0, r1 = r - 15, r - 8
            major.append((a, r0, r1))
        else:
            r0, r1 = r - 11, r - 8
            minor.append((a, r0, r1))

    def line(a, r0, r1):
        return (f'M{num(cx + r0 * math.cos(a))} {num(cy + r0 * math.sin(a))}'
                f'L{num(cx + r1 * math.cos(a))} {num(cy + r1 * math.sin(a))}')

    out.append(f'<path d="{"".join(line(*m) for m in minor)}" stroke="{t["tick"]}" stroke-width="0.8" stroke-opacity="0.55"/>')
    out.append(f'<path d="{"".join(line(*m) for m in major)}" stroke="{t["tick_major"]}" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(f'<path d="{"".join(line(*m) for m in quarter)}" stroke="{t["tick_major"]}" stroke-width="2.2" stroke-linecap="round"/>')
    # 12 o'clock marker
    out.append(f'<circle cx="{num(cx)}" cy="{num(cy - r + 24)}" r="1.6" fill="{t["accent"]}"/>')
    # label under the centre
    for i, line_text in enumerate(DIAL_LABEL):
        lab = faces[700].layout(line_text, label_size, tracking=0.14)
        out.append(lab.path(cx - lab.width / 2, cy + r * 0.40 + i * label_size * 1.3, t["accent"], nd=2))

    def rot(period: float, start: float) -> str:
        if still:
            return f' transform="rotate({num(start)} {num(cx)} {num(cy)})"'
        return ""

    def anim(period: float) -> str:
        if still:
            return ""
        return (f'<animateTransform attributeName="transform" type="rotate" '
                f'from="0 {num(cx)} {num(cy)}" to="360 {num(cx)} {num(cy)}" '
                f'dur="{num(period)}s" repeatCount="indefinite"/>')

    min_len, sec_len, sec_tail = r * 0.72, r * 0.80, r * 0.22
    # minute hand (60 min per turn)
    out.append(f'<g{rot(3600, STILL_POSE["minute"])}>{anim(3600)}'
               f'<path d="M{num(cx)} {num(cy + 8)}L{num(cx)} {num(cy - min_len)}" stroke="{t["hand"]}" stroke-width="2.6" stroke-linecap="round"/></g>')
    # seconds hand (60 s per turn) with counterweight
    out.append(f'<g{rot(60, STILL_POSE["second"])}>{anim(60)}'
               f'<path d="M{num(cx)} {num(cy + sec_tail)}L{num(cx)} {num(cy - sec_len)}" stroke="{t["hand_sec"]}" stroke-width="1.1" stroke-linecap="round"/>'
               f'<circle cx="{num(cx)}" cy="{num(cy + sec_tail * 0.55)}" r="2.6" fill="{t["hand_sec"]}"/></g>')
    out.append(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="4.2" fill="{t["hand"]}"/>'
               f'<circle cx="{num(cx)}" cy="{num(cy)}" r="1.6" fill="{t["cap"]}"/>')
    return "\n".join(out)


# ----------------------------------------------------------------- hero
def hero(theme: str, mobile: bool, still: bool, faces: dict) -> str:
    t = THEMES[theme]
    if mobile:
        W, H = 360, 380
        name = faces[900].layout(NAME, 44, tracking=-0.012)
        r1 = faces[500].layout(ROLE_1, 16)
        sep = faces[500].layout(" · ", 16)
        r1t = faces[500].layout(ROLE_1_TAIL, 16)
        r2 = faces[500].layout(ROLE_2, 15)
        x0, y_name, y1, y2 = 28, 74, 104, 128
        cx, cy, r, label = 180, 258, 92, 10
    else:
        W, H = 846, 300
        name = faces[900].layout(NAME, 60, tracking=-0.012)
        r1 = faces[500].layout(ROLE_1, 16)
        sep = faces[500].layout(" · ", 16)
        r1t = faces[500].layout(ROLE_1_TAIL, 16)
        r2 = faces[500].layout(ROLE_2, 15)
        x0, y_name, y1, y2 = 56, 140, 178, 203
        cx, cy, r, label = 690, 150, 118, 9

    defs, body, border = frame(W, H, t)
    text = [
        name.path(x0, y_name, t["ink"]),
        r1.path(x0, y1, t["ink2"]),
        sep.path(x0 + r1.width, y1, t["accent"]),
        r1t.path(x0 + r1.width + sep.width, y1, t["muted"]),
        r2.path(x0, y2, t["muted"]),
    ]
    title = f"{NAME} — {ROLE_1}, {ROLE_2}, {ROLE_1_TAIL}. The watch shows how long you have been on this page."
    # faint engineering grid behind the watch, fading out towards the text
    gx0 = cx - r - 60
    gdefs = (f'<radialGradient id="grid-fade" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r + 70}">'
             f'<stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="0.75" stop-color="#fff" stop-opacity="0.5"/>'
             f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
             f'<mask id="grid-mask"><rect x="{gx0}" y="0" width="{W - gx0}" height="{H}" fill="url(#grid-fade)"/></mask>')
    lines = []
    for x in range(int(gx0) + 4, W, 28):
        lines.append(f'M{x} 0V{H}')
    for y in range(4, H, 28):
        lines.append(f'M{gx0} {y}H{W}')
    grid = (f'<g mask="url(#grid-mask)"><path d="{"".join(lines)}" stroke="{t["ink"]}" stroke-opacity="0.05" stroke-width="1"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="none" stroke="{t["accent"]}" stroke-opacity="0.14" stroke-width="0.8" stroke-dasharray="2 5"/></g>')
    defs += gdefs
    if movement is not None:
        defs += movement_defs(t)
        lab, lsz = [], round(0.078 * r, 2)
        for i, line_text in enumerate(DIAL_LABEL):
            run = faces[700].layout(line_text, lsz, tracking=0.14)
            lab.append(run.path(cx - run.width / 2, cy + r * 0.385 + i * lsz * 1.3, t["accent"], nd=2))
        dial = movement(cx, cy, r, t, still, label_svg="".join(lab))
    else:
        dial = watch(cx, cy, r, t, faces, still, label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<defs>
{defs}
</defs>
<g clip-path="url(#frame)">
{body}
{chr(10).join(text)}
{grid}
{dial}
{border}
</g>
</svg>
'''



# ----------------------------------------------------------------- cards
def pretty_url(url: str) -> str:
    return url.split("://", 1)[-1].removeprefix("www.").rstrip("/")


def card(slug: str, name: str, live: str, theme: str, mobile: bool, faces: dict) -> str:
    """Cover shot and the project's name, nothing else: the whole card links to
    the live site and the buttons under it carry the calls to action."""
    t = THEMES[theme]
    W = 204
    # desktop renders at ~203 px, mobile at ~74 px (24% of a 308 px column)
    size, x, gap, H = (24, 12, 14, 160) if mobile else (22, 13, 16, 164)
    data = base64.b64encode((MEDIA / f"{slug}.webp").read_bytes()).decode("ascii")
    defs, body, border = frame(W, H, t)
    defs += f'<clipPath id="shot"><rect x="10" y="10" width="184" height="104" rx="7"/></clipPath>'
    nm = faces[700].layout(name, size, tracking=-0.01)
    parts = [
        f'<rect x="10" y="10" width="184" height="104" rx="7" fill="{t["dial"]}"/>',
        f'<image href="data:image/webp;base64,{data}" x="10" y="10" width="184" height="104" '
        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#shot)"/>',
        f'<rect x="10.5" y="10.5" width="183" height="103" rx="6.5" fill="none" stroke="{t["sheen"]}" stroke-opacity="0.08"/>',
        nm.path(x, 114 + gap + faces[700].cap_height(size), t["ink"]),
    ]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{name} — {pretty_url(live)}</title>
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


# ----------------------------------------------------------------- buttons
# Two links need two images on GitHub, so the buttons are images of their own,
# drawn to sit in the card's column: a "Code" + "Live" pair at 12% + 12% of the
# README width (glued together in the markup, no whitespace between them) or
# one "Live" button at 24%. A pair is drawn edge to edge with BTN_GAP of
# transparent space between the two pills, so pair and card share both edges.
# Live is the primary action and is filled with the accent gold; Code is
# outlined on the card surface. Mobile buttons (~37 px wide) are icon only.
BTN_H = 40
BTN_W = {(False, False): 204, (False, True): 102, (True, False): 84, (True, True): 42}  # (mobile, half)
BTN_GAP = {False: 4.0, True: 4.4}   # ~3.9 px on screen, the width of the space between the cards
BTN_LABEL = 14
BTN_STYLE = "ink"   # one of: metal, ink, goldline, ghost


def mix(a: str, b: str, k: float) -> str:
    """a moved towards b by k (0..1), sRGB hex."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(pa, pb))


def arrow_ne(cx: float, cy: float, s: float, colour: str, sw: float) -> str:
    """A north-east arrow drawn with strokes in an s x s box centred on (cx, cy)."""
    a = s / 2 - sw / 2
    head = a * 1.3
    return (f'<path d="M{num(cx - a, 2)} {num(cy + a, 2)}L{num(cx + a, 2)} {num(cy - a, 2)}'
            f'M{num(cx + a - head, 2)} {num(cy - a, 2)}H{num(cx + a, 2)}V{num(cy - a + head, 2)}" '
            f'fill="none" stroke="{colour}" stroke-width="{num(sw, 2)}" stroke-linecap="round" stroke-linejoin="round"/>')


def button(kind: str, name: str, theme: str, mobile: bool, half: bool, faces: dict) -> str:
    """kind is "code" (GitHub mark, links to the repo) or "live" (arrow, links to the site)."""
    t = THEMES[theme]
    W, H = BTN_W[(mobile, half)], BTN_H
    x0, x1 = 0.0, float(W)
    if half:
        if kind == "code":
            x1 -= BTN_GAP[mobile] / 2
        else:
            x0 += BTN_GAP[mobile] / 2
    w, cy, r = x1 - x0, H / 2, 10
    style = BTN_STYLE
    # colours per style: (fill kind, icon colour, label colour, border colour)
    if style == "metal" and kind == "live":
        fill, fg, lab, border = "metal", t["bg0"], t["bg0"], None
    elif style == "ink" and kind == "live":
        fill, fg, lab, border = "ink", t["bg0"], t["bg0"], None
    elif style == "goldline" and kind == "live":
        fill, fg, lab, border = "surface", t["accent"], t["accent"], t["accent"]
    elif style == "ghost":
        fill, fg, lab, border = "surface", (t["accent"] if kind == "live" else t["muted"]), t["ink"], t["border"]
    else:  # secondary button in every style
        fill, fg, lab, border = "surface", (t["accent"] if style == "goldline" else t["ink2"]), t["ink2"], t["border"]

    defs, shapes = [], []
    if fill == "metal":
        top, mid, bottom = mix(t["accent"], "#ffffff", 0.38), t["accent"], mix(t["accent"], "#000000", 0.16)
        defs.append(f'<linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
                    f'<stop offset="0.55" stop-color="{mid}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')
        shapes.append(f'<rect x="{num(x0)}" y="0" width="{num(w)}" height="{H}" rx="{r}" fill="url(#fill)"/>')
        shapes.append(f'<rect x="{num(x0 + 0.5)}" y="0.5" width="{num(w - 1)}" height="{H - 1}" rx="{r - 0.5}" fill="none" stroke="#ffffff" stroke-opacity="0.35"/>')
    elif fill == "ink":
        shapes.append(f'<rect x="{num(x0)}" y="0" width="{num(w)}" height="{H}" rx="{r}" fill="{t["ink"]}"/>')
    else:
        defs.append(f'<linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/>'
                    f'<stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>')
        defs.append(f'<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["sheen"]}" stop-opacity="0"/>'
                    f'<stop offset="0.5" stop-color="{t["accent"]}" stop-opacity="0.35"/>'
                    f'<stop offset="1" stop-color="{t["sheen"]}" stop-opacity="0"/></linearGradient>')
        shapes.append(f'<rect x="{num(x0 + 0.5)}" y="0.5" width="{num(w - 1)}" height="{H - 1}" rx="{r - 0.5}" '
                      f'fill="url(#surface)" stroke="{border}"{" stroke-opacity=\"0.7\"" if border == t["accent"] else ""}/>')
        if border != t["accent"]:
            shapes.append(f'<rect x="{num(x0 + 14)}" y="0.5" width="{num(w - 28)}" height="1" fill="url(#sheen)"/>')

    icon_size = 18 if mobile else 15
    label = None if mobile else faces[700].layout(kind.title(), BTN_LABEL, tracking=0.01)
    gap = 8
    group = icon_size + (gap + label.width if label else 0)
    gx = x0 + (w - group) / 2
    icx = gx + icon_size / 2
    if kind == "code":
        shapes.append(brand_icon("github", icx, cy, icon_size, fg))
    else:
        shapes.append(arrow_ne(icx, cy, icon_size * 0.82, fg, 2.0 if mobile else 1.8))
    if label:
        shapes.append(label.path(gx + icon_size + gap, cy + faces[700].cap_height(BTN_LABEL) / 2, lab, nd=2))
    title = f"{name} — source code on GitHub" if kind == "code" else f"{name} — live site"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<defs>
{chr(10).join(defs)}
</defs>
{chr(10).join(shapes)}
</svg>
'''


# One grey that reads as "dimmed" on both GitHub page colours (#0d1117 and #fff),
# so the non-link half needs no dark/light pair (#gh-*-mode-only keys off a link).
NEUTRAL = "#8b929c"


def lock(cx: float, cy: float, s: float, colour: str, sw: float) -> str:
    """A padlock drawn with strokes in an s x s box centred on (cx, cy)."""
    k = s / 24

    def p(x: float, y: float) -> str:
        return f"{num(cx + (x - 12) * k, 2)} {num(cy + (y - 12) * k, 2)}"

    body = (f'<rect x="{num(cx - 7.5 * k, 2)}" y="{num(cy - 1.5 * k, 2)}" width="{num(15 * k, 2)}" height="{num(11 * k, 2)}" '
            f'rx="{num(2.6 * k, 2)}" fill="none" stroke="{colour}" stroke-width="{num(sw, 2)}"/>')
    shackle = (f'<path d="M{p(8.2, 10.5)}L{p(8.2, 7.4)}A{num(3.8 * k, 2)} {num(3.8 * k, 2)} 0 0 1 {p(15.8, 7.4)}L{p(15.8, 10.5)}" '
               f'fill="none" stroke="{colour}" stroke-width="{num(sw, 2)}" stroke-linecap="round"/>')
    hole = f'<circle cx="{num(cx, 2)}" cy="{num(cy + 4 * k, 2)}" r="{num(1.4 * k, 2)}" fill="{colour}"/>'
    return body + shackle + hole


def private_button(mobile: bool, faces: dict) -> str:
    """Left half for a project whose code is private: not a link, no theme pair."""
    W, H = BTN_W[(mobile, True)], BTN_H
    x0, x1 = 0.0, W - BTN_GAP[mobile] / 2
    w, cy, r = x1 - x0, H / 2, 10
    shapes = [f'<rect x="{num(x0 + 0.5)}" y="0.5" width="{num(w - 1)}" height="{H - 1}" rx="{r - 0.5}" '
              f'fill="{NEUTRAL}" fill-opacity="0.06" stroke="{NEUTRAL}" stroke-opacity="0.32"/>']
    icon_size = 18 if mobile else 15
    label = None if mobile else faces[700].layout("Private", BTN_LABEL, tracking=0.01)
    group = icon_size + (8 + label.width if label else 0)
    gx = x0 + (w - group) / 2
    shapes.append(lock(gx + icon_size / 2, cy, icon_size, NEUTRAL, 1.8 if mobile else 1.6))
    if label:
        shapes.append(label.path(gx + icon_size + 8, cy + faces[700].cap_height(BTN_LABEL) / 2, NEUTRAL, nd=2))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">\n'
            f'<title id="t">The source code is private</title>\n' + "\n".join(shapes) + "\n</svg>\n")



# ----------------------------------------------------------------- footer
def footer(theme: str, mobile: bool, faces: dict) -> str:
    t = THEMES[theme]
    if mobile:
        W, H = 360, 104
        kick = faces[700].layout(FOOT_KICKER, 10, tracking=0.22)
        dom = faces[700].layout(FOOT_DOMAIN, 26, tracking=-0.01)
        arrow = faces[500].layout("→", 22)
        sub = faces[500].layout(FOOT_SUB, 13)
        yk, yd, ys, gap = 27, 58, 81, 8
    else:
        W, H = 846, 124
        kick = faces[700].layout(FOOT_KICKER, 10, tracking=0.24)
        dom = faces[700].layout(FOOT_DOMAIN, 38, tracking=-0.01)
        arrow = faces[500].layout("→", 30)
        sub = faces[500].layout(FOOT_SUB, 13)
        yk, yd, ys, gap = 32, 70, 96, 12
    defs, body, border = frame(W, H, t)
    total = dom.width + gap + arrow.width
    xd = (W - total) / 2
    parts = [
        kick.path((W - kick.width) / 2, yk, t["accent"], nd=2),
        dom.path(xd, yd, t["ink"]),
        arrow.path(xd + dom.width + gap, yd - (dom.size - arrow.size) * 0.18, t["accent"]),
        sub.path((W - sub.width) / 2, ys, t["muted"]),
    ]
    if not mobile:
        # hairlines left and right of the domain
        hx, ly = 64, yd - dom.size * 0.33
        parts.append(f'<rect x="{hx}" y="{num(ly)}" width="{num(xd - hx - 24)}" height="1" fill="{t["border"]}"/>')
        parts.append(f'<rect x="{num(xd + total + 24)}" y="{num(ly)}" width="{num(W - hx - (xd + total + 24))}" height="1" fill="{t["border"]}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">More about my work at asilturkmen.com: projects, case studies and CV.</title>
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


# ----------------------------------------------------------------- main
def main() -> None:
    fonts_ready()
    faces = {w: Face(FONT_DIR / Path(p).name) for w, p in FONT_FILES.items()}
    ASSETS.mkdir(exist_ok=True)
    written = []
    for theme in THEMES:
        for mobile in (False, True):
            m = "-mobile" if mobile else ""
            for still in (False, True):
                s = "-still" if still else ""
                p = ASSETS / f"hero-{theme}{m}{s}.svg"
                p.write_text(hero(theme, mobile, still, faces), encoding="utf-8", newline="\n")
                written.append(p)
            p = ASSETS / f"footer-{theme}{m}.svg"
            p.write_text(footer(theme, mobile, faces), encoding="utf-8", newline="\n")
            written.append(p)
            p = ASSETS / f"tools-{theme}{m}.svg"
            p.write_text(tools_strip(theme, mobile, faces), encoding="utf-8", newline="\n")
            written.append(p)
            for slug, name, live, repo in PROJECTS:
                p = ASSETS / f"card-{slug}-{theme}{m}.svg"
                p.write_text(card(slug, name, live, theme, mobile, faces), encoding="utf-8", newline="\n")
                written.append(p)
                for kind in (("code", "live") if repo else ("live",)):
                    p = ASSETS / f"btn-{slug}-{kind}-{theme}{m}.svg"
                    p.write_text(button(kind, name, theme, mobile, True, faces), encoding="utf-8", newline="\n")
                    written.append(p)
    for mobile in (False, True):   # theme-neutral, one image for both themes
        p = ASSETS / f"btn-private{'-mobile' if mobile else ''}.svg"
        p.write_text(private_button(mobile, faces), encoding="utf-8", newline="\n")
        written.append(p)
    for p in written:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:>7,} bytes")


if __name__ == "__main__":
    sys.exit(main())
