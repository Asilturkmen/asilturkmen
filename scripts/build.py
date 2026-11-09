"""Draw the profile README images.

Everything on github.com/Asilturkmen that is not plain text comes out of this
file: the hero (name, role, and a watch that counts the time you spend on the
page), the project cards with their Code / Live buttons, the orbit, where
the tools I use circle the pointer to asilturkmen.com (scripts/orbit.py), and
the contact links (LinkedIn, email, Buy me a coffee) on the plate's last row.

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
import json
import math
import re
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
from tools import icon as brand_icon   # brand icons (Simple Icons), scripts/tools.py
from orbit import orbit, ORBIT, MARGIN_X as ORBIT_MARGIN_X   # the tools orbiting the asilturkmen.com lockup, scripts/orbit.py

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
ROLE_1_TAIL = "Cyprus"
ROLE_2 = "Software Engineering student at EMU"
BUILDS = ("web apps", "APIs", "automation", "games")   # "I build ___", the word keeps turning
BUILD_LEAD = "I build"
BUILD_HOLD = 2.4      # seconds each word stays
BUILD_RISE = 0.5      # seconds a word takes to turn in / out
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
    ("hesappcim", "HesAppcım", "https://hes-appcim.vercel.app", "https://github.com/Asilturkmen/HesAppcim"),
    ("yayla-yemek-evi", "Yayla Yemek Evi", "https://www.yaylayemekevi.com", "https://github.com/Asilturkmen/Yaylayemekevi"),
]
# The Live button's label and the verb in its title, where "Live" / "live site" is not the word.
LIVE = {"wipeout": ("Play", "play on itch.io")}
MEDIA = ROOT / "media" / "thumbs"

# Contact links: the plate's last row, three frameless windows (gold glyph + label), each
# its own image wrapped in <a>: (slug, label, title = README alt text).
LINKS = [
    ("linkedin", "LinkedIn", "LinkedIn — Asil Türkmen"),
    ("email", "Email", "Email — contact.asilturkmen@gmail.com"),
    ("coffee", "Buy me a coffee", "Buy me a coffee — buymeacoffee.com/turkmenasil"),
]
PLATE_LINKS = (40, 20, 40)       # link images (the click areas), % of the README width; the groups' places are LINK_ROW's
# Per breakpoint: h the row height; cy the groups' centre line below the row's top (the rest is the
# gap to the plate's bottom edge, a little more than above since the rounded corners eat into the
# slab); glyph, label (Satoshi Medium) and gap sizes; spread the distance from the plate's centre to
# the outer groups' centres (desktop 148 / 423 / 698, phones 72 / 180 / 288: the phone windows'
# own centres would push the long coffee label to within ~9 units of the edge).
LINK_ROW = {"desktop": dict(h=76, cy=34, glyph=16, label=13, gap=8, spread=275),
            "mobile": dict(h=64, cy=30, glyph=14, label=12, gap=6, spread=108)}

# ----------------------------------------------------------------- palettes
THEMES = {
    "dark": dict(
        bg0="#101216", bg1="#161920", border="#272b34", sheen="#ffffff",
        ink="#f4f5f7", ink2="#c9ccd3", muted="#9a9ea8", accent="#d4b483",
        accent_dim="#8c7a5c", dial="#0c0e12", tick="#6b6f78", tick_major="#d4b483",
        hand="#e9eaee", hand_sec="#d4b483", cap="#101216",
    ),
}
# Light mode shows the same obsidian artwork, fused into one plate (see Plate).
# Only the plate's outer 1px edge differs, so it has a defined rim on white.
THEMES["dark"]["edge"] = "#363b45"   # plate outline: visible on white, quiet on #0d1117
THEME = "dark"                      # one asset set for both GitHub themes

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



# ----------------------------------------------------------------- plate (light mode)
# On GitHub's white page the light set is ONE obsidian plate. Hero, project row,
# button row, orbit and the contact links are laid out in one coordinate system
# (846 units wide on desktop, 360 on phones) and every image is a window (its
# viewBox) onto that plate. Each window draws the whole plate's surface, outline
# and dividers, so neighbouring images continue each other exactly. The README
# glues the images with no whitespace and align="top" (vertical-align: top), which
# removes the gap GitHub would otherwise leave under every line of inline images.
PLATE_COLS = (26, 24, 24, 26)                    # card images, % of the README width
PLATE_BTNS = (14, 12, 12, 12, 12, 12, 12, 14)    # button images: the two halves under each card
PLATE_INSET = 24                                 # the dividers' and the sheen's inset from the plate's sides
assert ORBIT_MARGIN_X == PLATE_INSET, "orbit.MARGIN_X keeps the icons off the plate's sides by PLATE_INSET; keep them equal"


class Plate:
    def __init__(self, mobile: bool, faces: dict):
        self.mobile = mobile
        W = self.W = 360 if mobile else 846
        G = self.gutter = 8 if mobile else 16                    # gutter between covers
        self.xs, self.bxs, self.lxs = [0.0], [0.0], [0.0]
        for p in PLATE_COLS:
            self.xs.append(self.xs[-1] + p * W / 100)
        for p in PLATE_BTNS:
            self.bxs.append(self.bxs[-1] + p * W / 100)
        for p in PLATE_LINKS:
            self.lxs.append(self.lxs[-1] + p * W / 100)
        self.cw = PLATE_COLS[1] * W / 100 - G                    # cover width
        self.cx = [self.xs[1] - G / 2 - self.cw] + [self.xs[i] + G / 2 for i in (1, 2, 3)]
        self.ch = self.cw * 104 / 184                            # cover height (card ratio)
        self.name_size = 9.6 if mobile else 20
        self.pad_top, self.name_gap, pad_bot = (22, 6, 10) if mobile else (40, 13, 18)
        # vertical breathing room inside each row (content is pushed down by pad[row]);
        # the orbit row takes its content height and padding from orbit.ORBIT
        orbit_h, orbit_pad = ORBIT["mobile" if mobile else "desktop"]
        self.pad = dict(hero=8 if mobile else 12, cards=0, buttons=0, orbit=orbit_pad, links=0)
        cap = faces[700].cap_height(self.name_size)
        self.h = dict(
            hero=(416 + 16) if mobile else (300 + 24),
            cards=math.ceil(self.pad_top + self.ch + self.name_gap + cap + pad_bot),
            buttons=BTN_H + (30 if mobile else 44),
            orbit=orbit_h + 2 * orbit_pad,
            links=LINK_ROW["mobile" if mobile else "desktop"]["h"],
        )
        self.y, y = {}, 0
        for k, h in self.h.items():
            self.y[k] = y
            y += h
        self.H = y


def plate_svg(pl: "Plate", t: dict, x0: float, x1: float, row: str, content: str, title: str,
              defs: str = "", shift: bool = True) -> str:
    """One window of the plate: x0..x1 across, the given row down. content is in
    the row's own coordinates (shift) or already in plate coordinates."""
    W, H, y0, h = pl.W, pl.H, pl.y[row], pl.h[row]
    edge = t.get("edge", t["border"])
    dy = y0 + pl.pad[row]
    if shift and dy:
        content = f'<g transform="translate(0 {dy})">{content}</g>'
    rules = "".join(f'<rect x="{PLATE_INSET}" y="{pl.y[k]}" width="{W - 2 * PLATE_INSET}" height="1" fill="url(#pl-rule)"/>'
                    for k in ("cards", "orbit", "links"))
    w = num(x1 - x0, 2)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x0, 2)} {y0} {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">\n'
            f'<title id="t">{title}</title>\n<defs>\n'
            f'<clipPath id="pl-frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>\n'
            f'<linearGradient id="pl-surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>\n'
            f'<linearGradient id="pl-sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["sheen"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{t["accent"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{t["sheen"]}" stop-opacity="0"/></linearGradient>\n'
            f'<linearGradient id="pl-rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["border"]}" stop-opacity="0"/><stop offset="0.06" stop-color="{t["border"]}"/><stop offset="0.94" stop-color="{t["border"]}"/><stop offset="1" stop-color="{t["border"]}" stop-opacity="0"/></linearGradient>\n'
            f'{defs}\n</defs>\n<g clip-path="url(#pl-frame)">\n'
            f'<rect width="{W}" height="{H}" fill="url(#pl-surface)"/>\n{content}\n{rules}\n'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{edge}"/>'
            f'<rect x="{PLATE_INSET}" y="0.5" width="{W - 2 * PLATE_INSET}" height="1" fill="url(#pl-sheen)"/>\n</g>\n</svg>\n')


def _inner(svg: str) -> str:
    """The drawing inside a standalone button SVG, without its <svg> and <title>."""
    body = svg.split("\n", 1)[1]
    body = body.split("</title>\n", 1)[1]
    return body.rsplit("</svg>", 1)[0]


def plate_card(pl: "Plate", i: int, slug: str, name: str, live: str, t: dict, faces: dict) -> str:
    """Cover and name straight on the plate (no card frame): the plate is the card."""
    x, y, w, h = pl.cx[i], pl.y["cards"] + pl.pad_top, pl.cw, pl.ch
    r = 4 if pl.mobile else 7
    data = base64.b64encode((MEDIA / f"{slug}.webp").read_bytes()).decode("ascii")
    nm = faces[700].layout(name, pl.name_size, tracking=-0.01)
    X, Y, Wd, Hd = num(x, 2), num(y, 2), num(w, 2), num(h, 2)
    defs = f'<clipPath id="shot"><rect x="{X}" y="{Y}" width="{Wd}" height="{Hd}" rx="{r}"/></clipPath>'
    parts = (f'<rect x="{X}" y="{Y}" width="{Wd}" height="{Hd}" rx="{r}" fill="{t["dial"]}"/>'
             f'<image href="data:image/webp;base64,{data}" x="{X}" y="{Y}" width="{Wd}" height="{Hd}" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#shot)"/>'
             f'<rect x="{num(x + .5, 2)}" y="{num(y + .5, 2)}" width="{num(w - 1, 2)}" height="{num(h - 1, 2)}" rx="{r - .5}" '
             f'fill="none" stroke="{t["sheen"]}" stroke-opacity="0.08"/>'
             + nm.path(x, y + h + pl.name_gap + faces[700].cap_height(pl.name_size), t["ink"],
                       nd=2 if pl.mobile else 1))
    return plate_svg(pl, t, pl.xs[i], pl.xs[i + 1], "cards", parts, f"{name} — {pretty_url(live)}", defs, shift=False)


def plate_button(pl: "Plate", i: int, right: bool, kind: str, slug: str, name: str, theme: str, faces: dict) -> str:
    """Left (Code, or the Private pill) or right (Live) half under card i, on the plate."""
    g = BTN_GAP[pl.mobile]
    if right:
        x0, x1 = pl.cx[i] + pl.cw / 2 + g / 2, pl.cx[i] + pl.cw
    else:
        x0, x1 = pl.cx[i], pl.cx[i] + pl.cw / 2 - g / 2
    w = round(x1 - x0, 2)
    if kind == "private":
        svg = private_button(pl.mobile, faces, name, width=w)
    else:
        label, verb = LIVE.get(slug, (None, None)) if kind == "live" else (None, None)
        svg = button(kind, name, theme, pl.mobile, False, faces, width=w, label=label, verb=verb)
    title = svg.split('<title id="t">', 1)[1].split("</title>", 1)[0]
    pill = (f'<svg x="{num(x0, 2)}" y="{pl.y["buttons"]}" width="{num(w, 2)}" height="{BTN_H}" '
            f'viewBox="0 0 {num(w, 2)} {BTN_H}">{_inner(svg)}</svg>')
    j = 2 * i + int(right)
    return plate_svg(pl, THEMES[theme], pl.bxs[j], pl.bxs[j + 1], "buttons", pill, title, shift=False)


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


# ----------------------------------------------------------------- hero lockup
# The text block left of the watch, in three registers: the name; the
# statement "I build ___" whose last word keeps turning like a slot drum (web
# apps, APIs, automation, games); and a meta strip (role, place, school) under
# a gold rule. The moving hero plays the block in once (name, statement, rule,
# strip items, staggered over ~2 s) and then only the turning word and the
# watch keep moving. Every animation starts at t=0,
# holds its first value until its cue and ends on the drawing's own attributes,
# so a renderer without SMIL shows the finished lockup, which is exactly what
# the still (reduced-motion) variant draws.
EASE = "0.2 0.8 0.2 1"     # keySplines: quick start, long soft landing
SWEEP = "0.45 0 0.2 1"     # the light across the name: eases in, so it is seen travelling


def intro(tag: str, attr: str, a: str, b: str, at: float, dur: float, extra: str = "", ease: str = EASE) -> str:
    """One-shot SMIL entrance: hold a until `at` s, ease to b over `dur` s, freeze."""
    total = at + dur
    if at <= 0:
        vals, keys, splines = f"{a};{b}", "0;1", ease
    else:
        vals, keys, splines = f"{a};{a};{b}", f"0;{num(at / total, 4)};1", f"0 0 1 1;{ease}"
    return (f'<{tag} attributeName="{attr}"{extra} values="{vals}" keyTimes="{keys}" dur="{num(total, 3)}s" '
            f'calcMode="spline" keySplines="{splines}" fill="freeze"/>')


def glyph(kind: str, cx: float, cy: float, s: float, colour: str, sw: float) -> str:
    """Small stroke icons drawn in a 24-unit box centred on (cx, cy), s units wide:
    "code" (</>), "pin" (map pin), "spark" (four-point star) and "cap" (mortarboard)."""
    k = s / 24

    def p(x: float, y: float) -> str:
        return f"{num(cx + (x - 12) * k, 2)} {num(cy + (y - 12) * k, 2)}"

    def arc(rad: float) -> str:
        return f"{num(rad * k, 2)} {num(rad * k, 2)}"

    if kind == "code":
        d = (f"M{p(7.5, 6.5)}L{p(2, 12)}L{p(7.5, 17.5)}M{p(16.5, 6.5)}L{p(22, 12)}L{p(16.5, 17.5)}"
             f"M{p(13.8, 4)}L{p(10.2, 20)}")
    elif kind == "pin":
        d = (f"M{p(12, 22)}C{p(12, 22)} {p(5, 15.2)} {p(5, 9.8)}A{arc(7)} 0 0 1 {p(19, 9.8)}"
             f"C{p(19, 15.2)} {p(12, 22)} {p(12, 22)}Z"
             f"M{p(9.6, 9.8)}A{arc(2.4)} 0 1 0 {p(14.4, 9.8)}A{arc(2.4)} 0 1 0 {p(9.6, 9.8)}Z")
    elif kind == "spark":
        d = (f"M{p(12, 2.5)}C{p(12.6, 8.4)} {p(15.6, 11.4)} {p(21.5, 12)}C{p(15.6, 12.6)} {p(12.6, 15.6)} {p(12, 21.5)}"
             f"C{p(11.4, 15.6)} {p(8.4, 12.6)} {p(2.5, 12)}C{p(8.4, 11.4)} {p(11.4, 8.4)} {p(12, 2.5)}Z")
    elif kind == "cap":
        d = (f"M{p(1, 9.5)}L{p(12, 4.5)}L{p(23, 9.5)}L{p(12, 14.5)}Z"
             f"M{p(5.5, 12)}L{p(5.5, 16.5)}C{p(7.5, 18.6)} {p(9.6, 19.5)} {p(12, 19.5)}"
             f"C{p(14.4, 19.5)} {p(16.5, 18.6)} {p(18.5, 16.5)}L{p(18.5, 12)}"
             f"M{p(23, 9.5)}L{p(23, 15)}")
    else:
        raise ValueError(kind)
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{num(sw, 2)}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


META_SCHOOL = "EMU Software Engineering"   # ROLE_2 in the one-line desktop strip (the phone strip has room for ROLE_2)

# The view counter at the top centre of the hero: "(eye) 1,248 views" as plain text on
# the hero surface (gold eye, the count in Satoshi Bold, "views" in Satoshi Medium), no
# box. The number is live, so the hero on GitHub is served by counter/api/hero.js from
# the templates this file writes to counter/hero/: the counter's place and size are left
# in a <!--VIEWS {"cx","y","num","label","eye"}--> comment (cx the centre of the whole
# eye+number+label group, y the text baseline, num/label the font sizes, eye the eye's
# height) that the function fills from counter/glyphs.json (render.js renderCounter);
# in the moving hero the eye blinks. assets/hero*.svg get the comment and the title's
# sentence about it stripped.
VIEWS_RE = re.compile(r"<!--VIEWS .*?-->")
VIEWS_TITLE = " The number at the top is the profile view count."
COUNTER = ROOT / "counter"


def lockup(t: dict, faces: dict, mobile: bool, still: bool, x0: float) -> tuple[str, str]:
    """The hero's text block in hero coordinates; returns (defs, drawing).

    Three registers instead of three equal lines: the name (Black, large); the
    statement "I build ___" at half its size, a quiet Medium lead and a gold
    Black word that keeps turning like a slot drum; and the facts collapsed
    into one small meta strip under a gold hairline, split by gold hairlines
    (two short rows on phones). x0 is the block's left edge: the covers' left
    edge in the card row (Plate.cx[0]), so the hero text and the covers line up."""
    if mobile:
        yn, ns, band, floor = 88, 44, 72, 5   # the name's baseline leaves room for the counter above it (hero() H and cy move with it)
        sy, ss = 37, 22                    # statement: baseline below the name's, size
        ry, my, ms, mlh = 19, 21, 12, 20   # rule below the statement, strip below the rule, strip size, row pitch
        ics, isw, igap, sgap = 12, 1.35, 6, 10
        right, fit = 360 - x0, 352 - x0    # the text column ends here (the left margin mirrored); the still statement a little sooner
        rows = [[("code", ROLE_1), ("pin", ROLE_1_TAIL)], [("cap", ROLE_2)]]
        ccx, cyb, cn, cl, ce = 180, 34, 15, 12, 17   # counter: group centre x, baseline, number, label, eye sizes
    else:
        # the block (name, statement, rule, strip) sits a little below the hero's middle, so with
        # the counter above it the whole column balances against the watch (cy 150)
        yn, ns, band, floor = 136, 60, 96, 7
        sy, ss = 50, 30
        ry, my, ms, mlh = 24, 24, 13, 0
        ics, isw, igap, sgap = 13.5, 1.4, 7, 13
        right, fit = 528, x0 + 432         # clear of the watch's dotted track; still statement <= strip
        rows = [[("code", ROLE_1), ("pin", ROLE_1_TAIL), ("cap", META_SCHOOL)]]
        ccx, cyb, cn, cl, ce = 423, 46, 20, 15, 22
    ink, ink2, gold = t["ink"], t["ink2"], t["accent"]
    translate = ' type="translate"'
    defs, out = [], []

    # counter: the live view count at the top centre of the hero (eye + number + "views",
    # centred as one group on the hero's midline); its place is a comment that
    # counter/api/hero.js fills (see VIEWS_RE). It fades in and settles first.
    slot_json = json.dumps(dict(cx=ccx, y=cyb, num=cn, label=cl, eye=ce), separators=(",", ":"))
    counter = f"<!--VIEWS {slot_json}-->"
    if still:
        out.append(counter)
    else:
        settle = intro("animateTransform", "transform", "0 6", "0 0", 0.2, 0.8, translate)
        fade = intro("animate", "opacity", "0", "1", 0.2, 0.6)
        out.append(f"<g>{settle}<g>{fade}{counter}</g></g>")

    # name: revealed left to right behind a warm edge while it rises a few units
    name = faces[900].layout(NAME, ns, tracking=-0.012)
    if still:
        out.append(name.path(x0, yn, ink))
    else:
        xe = x0 + name.width + 4                     # at rest the band sits right of the name
        travel = name.width + band + 8
        sweep = intro("animateTransform", "gradientTransform", f"-{num(travel)} 0", "0 0", 0.0, 1.1, translate, SWEEP)
        defs.append(f'<linearGradient id="hx-name" gradientUnits="userSpaceOnUse" x1="{num(xe)}" y1="0" x2="{num(xe + band)}" y2="0">'
                    f'<stop offset="0" stop-color="{ink}"/><stop offset="0.3" stop-color="{mix(ink, gold, 0.5)}"/>'
                    f'<stop offset="0.62" stop-color="{mix(gold, ink, 0.3)}" stop-opacity="0.5"/>'
                    f'<stop offset="1" stop-color="{gold}" stop-opacity="0"/>{sweep}</linearGradient>')
        rise = intro("animateTransform", "transform", "0 10", "0 0", 0.0, 0.9, translate)
        out.append(f'<g>{rise}{name.path(x0, yn, "url(#hx-name)")}</g>')

    def slot(body: str, box, at: float, dur: float, key: str) -> str:
        """Rise into place out of an invisible slot (a clipPath). Its floor sits `floor`
        units below the box, so descenders are already clear of it during the slow
        landing: only the quick first part of the rise is cut by the floor."""
        if still:
            return body
        bx0, by0, bx1, by1 = box
        by1 += floor
        defs.append(f'<clipPath id="hx-{key}"><rect x="{num(bx0)}" y="{num(by0)}" '
                    f'width="{num(bx1 - bx0)}" height="{num(by1 - by0)}"/></clipPath>')
        a = intro("animateTransform", "transform", f"0 {num(by1 - by0 + 1)}", "0 0", at, dur, translate)
        return f'<g clip-path="url(#hx-{key})"><g>{a}{body}</g></g>'

    # statement: I build ___ ; the lead stays, the last word keeps turning
    ys = yn + sy

    def still_line(size: float):
        """lead, then the words in gold Black split by quiet Medium middots: [(run, x, colour)]."""
        lead = faces[500].layout(BUILD_LEAD, size)
        dot = faces[500].layout("·", size)
        parts, x = [(lead, x0, ink2)], x0 + lead.width + size * 0.26
        for i, w in enumerate(BUILDS):
            if i:
                x += size * 0.2
                parts.append((dot, x, t["muted"]))
                x += dot.width + size * 0.2
            run = faces[900].layout(w, size)
            parts.append((run, x, gold))
            x += run.width
        return parts, x

    if still:                       # every word on one line, no wider than the strip under it
        parts, x_end = still_line(ss)
        if x_end > fit:
            parts, x_end = still_line(round(ss * (fit - x0) / (x_end - x0), 1))
        out.append("".join(run.path(x, ys, c) for run, x, c in parts))
    else:
        lead = faces[500].layout(BUILD_LEAD, ss)
        capS = faces[900].cap_height(ss)
        xw = x0 + lead.width + ss * 0.26
        out.append(slot(lead.path(x0, ys, ink2), (x0 - 4, ys - capS - 8, xw, ys + ss * 0.3), 0.45, 0.75, "lead"))
        # the drum: one slot, four words; word i turns in while word i-1 turns out
        words = [faces[900].layout(w, ss) for w in BUILDS]
        # its window is the word's own height plus a soft edge above and below, where
        # a turning word fades like the curve of a cylinder; one turn moves a word by
        # the whole window, so two words never share it
        F = ss * 0.3
        top, bottom = ys - capS - 4 - F, ys + ss * 0.27 + F
        h = bottom - top + 1
        wmax = max(w.width for w in words)
        e = F / (bottom - top)
        box = f'x="{num(xw - 2)}" y="{num(top)}" width="{num(wmax + 6)}" height="{num(bottom - top)}"'
        defs.append(f'<linearGradient id="hx-drum-edge" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="{num(e, 3)}" stop-color="#fff"/>'
                    f'<stop offset="{num(1 - e, 3)}" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                    f'<mask id="hx-drum" maskUnits="userSpaceOnUse" {box}><rect {box} fill="url(#hx-drum-edge)"/></mask>')
        P = BUILD_HOLD * len(BUILDS)
        r = BUILD_RISE / P
        k_out = BUILD_HOLD / P
        vals = f"0 {num(h)};0 0;0 0;0 -{num(h)};0 -{num(h)}"
        keys = f"0;{num(r, 4)};{num(k_out, 4)};{num(k_out + r, 4)};1"
        splines = f"{EASE};0 0 1 1;{EASE};0 0 1 1"      # same curve in and out: one drum
        drum = []
        for i, run in enumerate(words):
            begin = 0.85 + i * BUILD_HOLD
            turn = (f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{keys}" '
                    f'calcMode="spline" keySplines="{splines}" begin="{num(begin, 2)}s" dur="{num(P, 2)}s" repeatCount="indefinite"/>')
            drum.append(f'<g transform="translate(0 {num(h)})">{turn}{run.path(xw, ys, gold)}</g>')
        out.append(f'<g mask="url(#hx-drum)">{"".join(drum)}</g>')

    # meta strip: </> role | (pin) place | (cap) school, gold glyphs, gold hairlines between
    yr = ys + ry
    capM = faces[500].cap_height(ms)
    items, seps, widths = [], [], []
    for ri, row in enumerate(rows):
        yb = yr + my + ri * mlh
        x = x0
        for j, (kind, text) in enumerate(row):
            run = faces[500].layout(text, ms)
            body = glyph(kind, x + ics / 2, yb - capM / 2, ics, gold, isw) + run.path(x + ics + igap, yb, ink2)
            x1 = x + ics + igap + run.width
            items.append((body, (x - 3, yb - capM - 7, x1 + 3, yb + ms * 0.3)))
            if j < len(row) - 1:
                seps.append((x1 + sgap, yb - capM - 2.5, yb + 2.5))
                x = x1 + 2 * sgap
        widths.append(x1 - x0)
    assert x0 + max(widths) <= right, "meta strip runs into the watch"

    # gold hairline between statement and strip, as long as the strip, fading out
    L = round(max(max(widths), name.width * 0.9), 1)
    X0 = num(x0, 2)
    defs.append(f'<linearGradient id="hx-rule" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{num(x0 + L, 2)}" y2="0">'
                f'<stop offset="0" stop-color="{gold}" stop-opacity="0.9"/><stop offset="0.5" stop-color="{gold}" stop-opacity="0.4"/>'
                f'<stop offset="1" stop-color="{gold}" stop-opacity="0"/></linearGradient>')
    if still:
        out.append(f'<path d="M{X0} {num(yr)}H{num(x0 + L, 2)}" stroke="url(#hx-rule)"/>')
    else:
        draw = intro("animate", "stroke-dashoffset", num(L), "0", 0.8, 0.9)
        out.append(f'<path d="M{X0} {num(yr)}H{num(x0 + L, 2)}" stroke="url(#hx-rule)" '
                   f'stroke-dasharray="{num(L)} {num(L)}">{draw}</path>')

    # a short solid gold lead-in on the rule: the block's one strong accent
    A = 26 if not mobile else 20
    if still:
        out.append(f'<rect x="{X0}" y="{num(yr - 1)}" width="{A}" height="2" fill="{gold}"/>')
    else:
        grow = intro("animate", "width", "0", str(A), 0.7, 0.5)
        out.append(f'<rect x="{X0}" y="{num(yr - 1)}" width="{A}" height="2" fill="{gold}">{grow}</rect>')

    # the strip plays in item by item once the rule is drawing
    for k, (body, box) in enumerate(items):
        out.append(slot(body, box, 1.0 + k * 0.13, 0.7, f"m{k}"))
    for k, (xs, sy0, sy1) in enumerate(seps):
        fade = "" if still else intro("animate", "opacity", "0", "1", 1.12 + k * 0.13, 0.5)
        out.append(f'<path d="M{num(xs)} {num(sy0)}V{num(sy1)}" stroke="{gold}" stroke-opacity="0.45">{fade}</path>')
    return "".join(defs), "\n".join(out)


# ----------------------------------------------------------------- hero
def hero(theme: str, mobile: bool, still: bool, faces: dict, plate: "Plate | None" = None) -> str:
    t = THEMES[theme]
    if mobile:
        W, H = 360, 416
        cx, cy, r, label = 180, 294, 92, 10
    else:
        W, H = 846, 300
        cx, cy, r, label = 690, 150, 118, 9

    defs, body, border = frame(W, H, t)
    x0 = (plate if plate is not None else Plate(mobile, faces)).cx[0]   # the text block starts where the covers do
    ldefs, lockup_svg = lockup(t, faces, mobile, still, x0)
    defs += ldefs
    text = [lockup_svg]
    title = (f"{NAME} — {ROLE_1}, {ROLE_2}, {ROLE_1_TAIL}. I build {', '.join(BUILDS[:-1])} and {BUILDS[-1]}. "
             f"The watch shows how long you have been on this page.{VIEWS_TITLE}")
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
    if plate is not None:
        extra = ldefs + gdefs + (movement_defs(t) if movement is not None else "")
        return plate_svg(plate, t, 0, W, "hero", chr(10).join(text) + chr(10) + grid + chr(10) + dial, title, extra)
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


def button(kind: str, name: str, theme: str, mobile: bool, half: bool, faces: dict, width: float | None = None,
           label: str | None = None, verb: str | None = None, badge=None) -> str:
    """kind is "code" (GitHub mark, links to the repo) or "live" (arrow, links to the site).
    label and verb replace the button's word and the verb in its title (see LIVE, private_button);
    badge(icx, cy, icon_size) -> svg draws something over the icon (the private padlock)."""
    t = THEMES[theme]
    W, H = (width or BTN_W[(mobile, half)]), BTN_H
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
    label = None if mobile else faces[700].layout(label or kind.title(), BTN_LABEL, tracking=0.01)
    gap = 8
    group = icon_size + (gap + label.width if label else 0)
    gx = x0 + (w - group) / 2
    icx = gx + icon_size / 2
    if kind == "code":
        shapes.append(brand_icon("github", icx, cy, icon_size, fg))
    else:
        shapes.append(arrow_ne(icx, cy, icon_size * 0.82, fg, 2.0 if mobile else 1.8))
    if badge:
        shapes.append(badge(icx, cy, icon_size))
    if label:
        shapes.append(label.path(gx + icon_size + gap, cy + faces[700].cap_height(BTN_LABEL) / 2, lab, nd=2))
    title = f"{name} — {verb or ('source code on GitHub' if kind == 'code' else 'live site')}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<defs>
{chr(10).join(defs)}
</defs>
{chr(10).join(shapes)}
</svg>
'''


def lock_badge(cx: float, cy: float, s: float, colour: str, key: str, sw: float) -> str:
    """A small filled padlock (body s*15/24 wide, shackle above) centred on (cx, cy), with a
    1-unit keyline in `key` (the pill's own colour) behind it, so it stays crisp where it
    overlaps the GitHub mark."""
    k = s / 24
    bx, by, bw, bh, br = cx - 7.5 * k, cy - 1.5 * k, 15 * k, 11 * k, 2.6 * k
    shackle = (f'M{num(cx - 3.8 * k, 2)} {num(cy - 1.5 * k, 2)}V{num(cy - 4.6 * k, 2)}'
               f'A{num(3.8 * k, 2)} {num(3.8 * k, 2)} 0 0 1 {num(cx + 3.8 * k, 2)} {num(cy - 4.6 * k, 2)}V{num(cy - 1.5 * k, 2)}')
    return (f'<path d="{shackle}" fill="none" stroke="{key}" stroke-width="{num(sw + 2, 2)}" stroke-linecap="round"/>'
            f'<rect x="{num(bx - 1, 2)}" y="{num(by - 1, 2)}" width="{num(bw + 2, 2)}" height="{num(bh + 2, 2)}" rx="{num(br + 1, 2)}" fill="{key}"/>'
            f'<path d="{shackle}" fill="none" stroke="{colour}" stroke-width="{num(sw, 2)}" stroke-linecap="round"/>'
            f'<rect x="{num(bx, 2)}" y="{num(by, 2)}" width="{num(bw, 2)}" height="{num(bh, 2)}" rx="{num(br, 2)}" fill="{colour}"/>'
            f'<circle cx="{num(cx, 2)}" cy="{num(cy + 4 * k, 2)}" r="{num(1.3 * k, 2)}" fill="{key}"/>')


PRIVATE_LABEL = "Private"


def private_button(mobile: bool, faces: dict, name: str, width: float | None = None) -> str:
    """Left half for a project whose code is private: the Code pill itself (same frame, GitHub
    mark and type) reading "Private", with a small gold padlock badged on the mark's lower
    right; not a link. Phones get the mark and the badge alone, like the other icon-only pills."""
    t = THEMES[THEME]
    key = mix(t["bg0"], t["bg1"], 0.5)          # the pill's surface, for the badge's keyline

    def badge(icx: float, cy: float, size: float) -> str:
        s, sw = (10, 1.2) if mobile else (9, 1.1)
        return lock_badge(icx + size * 0.4, cy + size * 0.4, s, t["accent"], key, sw)

    return button("code", name, THEME, mobile, width is None, faces, width=width,
                  label=PRIVATE_LABEL, verb=PRIVATE_LABEL, badge=badge)


# ----------------------------------------------------------------- contact links
def link_glyph(kind: str, cx: float, cy: float, s: float, colour: str, sw: float) -> str:
    """The contact glyphs, drawn in a 24-unit box centred on (cx, cy), s units wide, in one
    colour: "linkedin" (the in mark, filled), "email" (envelope) and "coffee" (cup on a
    saucer, two curls of steam), the last two stroked sw units wide."""
    k = s / 24
    if kind == "linkedin":
        body = (f'<circle cx="5.6" cy="5.6" r="1.85" fill="{colour}"/>'
                f'<rect x="4.1" y="9.2" width="3" height="10.6" rx="0.7" fill="{colour}"/>'
                f'<path d="M9.8 9.9c0-.4.3-.7.7-.7h1.7c.4 0 .65.25.7.6l.1.85c.75-.95 1.9-1.65 3.45-1.65 2.55 0 4.05 1.65 4.05 4.55'
                f'v5.55c0 .4-.3.7-.7.7h-1.8c-.4 0-.7-.3-.7-.7v-5c0-1.55-.7-2.45-2-2.45-1.35 0-2.2.95-2.2 2.5v4.95'
                f'c0 .4-.3.7-.7.7h-1.9c-.4 0-.7-.3-.7-.7Z" fill="{colour}"/>')
    elif kind == "email":
        body = (f'<g fill="none" stroke="{colour}" stroke-width="{num(sw / k, 2)}" stroke-linecap="round" stroke-linejoin="round">'
                f'<rect x="2.5" y="4.8" width="19" height="14.4" rx="2.4"/><path d="M3.5 6.2L12 12.6 20.5 6.2"/></g>')
    elif kind == "coffee":
        body = (f'<g fill="none" stroke="{colour}" stroke-width="{num(sw / k, 2)}" stroke-linecap="round" stroke-linejoin="round">'
                f'<path d="M8.2 3.2c0 1.4-1.2 1.8-1.2 3.2M12.8 3.2c0 1.4-1.2 1.8-1.2 3.2"/>'
                f'<path d="M4.2 9.2h11.8v5.2a4.8 4.8 0 0 1-4.8 4.8h-2.2a4.8 4.8 0 0 1-4.8-4.8Z"/>'
                f'<path d="M16 10.4h1.8a2.4 2.4 0 0 1 0 4.8h-1.8"/>'
                f'<path d="M3.2 21.2H17" stroke-opacity="0.75"/></g>')
    else:
        raise ValueError(kind)
    return f'<g transform="translate({num(cx - 12 * k, 2)} {num(cy - 12 * k, 2)}) scale({num(k, 4)})">{body}</g>'


def plate_link(pl: "Plate", i: int, t: dict, faces: dict) -> str:
    """Window i of the links row: a gold glyph and its label in ink, one group centred on
    the plate's middle or LINK_ROW's spread either side of it, inside its own window (the
    image is the click area); the outer windows carry the plate's bottom corners."""
    slug, text, title = LINKS[i]
    g = LINK_ROW["mobile" if pl.mobile else "desktop"]
    gs, ls, gap = g["glyph"], g["label"], g["gap"]
    x0, x1 = pl.lxs[i], pl.lxs[i + 1]
    run = faces[500].layout(text, ls)
    cap = faces[500].cap_height(ls)
    group = gs + gap + run.width
    gx = pl.W / 2 + (i - 1) * g["spread"] - group / 2
    margin = pl.gutter if pl.mobile else PLATE_INSET          # the group keeps the plate's inset (the cover gutter on phones) from its window's sides
    assert x0 + margin <= gx and gx + group <= x1 - margin, (
        f"links: {text!r} ({num(gx, 1)}..{num(gx + group, 1)}) leaves its window {num(x0, 1)}..{num(x1, 1)} less {margin}")
    yb = pl.y["links"] + g["cy"] + cap / 2                    # label baseline: cap centred on the group's centre line
    body = (link_glyph(slug, gx + gs / 2, yb - cap / 2, gs, t["accent"], 1.3 if pl.mobile else 1.4)
            + run.path(gx + gs + gap, yb, t["ink"], nd=2))
    return plate_svg(pl, t, x0, x1, "links", body, title, shift=False)



# ----------------------------------------------------------------- main
def main() -> None:
    fonts_ready()
    faces = {w: Face(FONT_DIR / Path(p).name) for w, p in FONT_FILES.items()}
    # the counter's renderer puts the title's counter sentence back into the live hero: it
    # must carry this file's VIEWS_TITLE word for word, or the served hero and the still
    # assets would describe the page differently
    render_js = (COUNTER / "render.js").read_text(encoding="utf-8")
    assert any(f"{q}{VIEWS_TITLE}{q}" in render_js for q in ('"', "'")), (
        f"counter/render.js must contain the string literal {VIEWS_TITLE!r} (build.VIEWS_TITLE) verbatim; "
        "the two copies have drifted apart")
    ASSETS.mkdir(exist_ok=True)
    written, theme = [], THEME
    for mobile in (False, True):
        m = "-mobile" if mobile else ""
        pl = Plate(mobile, faces)          # every image is a window onto one plate
        for still in (False, True):
            s = "-still" if still else ""
            svg = hero(theme, mobile, still, faces, pl)
            p = COUNTER / "hero" / f"hero{m}{s}.svg"      # template with the counter slot, served by the function
            p.parent.mkdir(exist_ok=True)
            p.write_text(svg, encoding="utf-8", newline="\n")
            written.append(p)
            p = ASSETS / f"hero{m}{s}.svg"                 # the same hero without the live counter
            p.write_text(VIEWS_RE.sub("", svg).replace(VIEWS_TITLE, ""), encoding="utf-8", newline="\n")
            written.append(p)
            p = ASSETS / f"orbit{m}{s}.svg"
            p.write_text(orbit(theme, mobile, still, faces, pl), encoding="utf-8", newline="\n")
            written.append(p)
        for i, (slug, name, live, repo) in enumerate(PROJECTS):
            p = ASSETS / f"card-{slug}{m}.svg"
            p.write_text(plate_card(pl, i, slug, name, live, THEMES[theme], faces), encoding="utf-8", newline="\n")
            written.append(p)
            for right, kind in enumerate(("code" if repo else "private", "live")):
                p = ASSETS / f"btn-{slug}-{kind}{m}.svg"
                p.write_text(plate_button(pl, i, bool(right), kind, slug, name, theme, faces), encoding="utf-8", newline="\n")
                written.append(p)
        for i, (slug, _, _) in enumerate(LINKS):
            p = ASSETS / f"link-{slug}{m}.svg"
            p.write_text(plate_link(pl, i, THEMES[theme], faces), encoding="utf-8", newline="\n")
            written.append(p)
    for p in written:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:>7,} bytes")
    for old in ASSETS.glob("*.svg"):       # assets/ holds this build's files only (removed last, so a failed build leaves the old set)
        if old not in written:
            old.unlink()
            print(f"{old.relative_to(ROOT)}  removed")


if __name__ == "__main__":
    sys.exit(main())
