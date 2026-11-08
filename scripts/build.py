"""Draw the profile README images.

Everything on github.com/Asilturkmen that is not plain text comes out of this
file: the hero (name, role, and a watch that counts the time you spend on the
page) and the footer that points to asilturkmen.com.

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
from tools import tools_strip  # "Tools I use" strip, scripts/tools.py

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT_DIR = ROOT / "scripts" / ".fonts"
FONT_ZIP = "https://api.fontshare.com/v2/fonts/download/satoshi"
FONT_FILES = {
    900: "Satoshi_Complete/Fonts/OTF/Satoshi-Black.otf",
    700: "Satoshi_Complete/Fonts/OTF/Satoshi-Bold.otf",
    500: "Satoshi_Complete/Fonts/OTF/Satoshi-Medium.otf",
}

SITE = "https://asilturkmen.com"

# ----------------------------------------------------------------- content
NAME = "Asil Türkmen"
ROLE_1 = "Full-stack developer"
ROLE_1_TAIL = "North Cyprus"
ROLE_2 = "Software Engineering student at EMU"
DIAL_LABEL = ("TIME ON", "THIS PAGE")
FOOT_KICKER = "MORE ABOUT MY WORK"
FOOT_DOMAIN = "asilturkmen.com"
FOOT_SUB = "projects · case studies · CV"

# (slug, kicker, name, sentence, link, call to action) — sentences are Asil's own (used in alt text).
PROJECTS = [
    ("nedirbeo", "COMMUNITY · DICTIONARY", "NedirBeo", "A community dictionary for Cypriot Turkish.",
     "https://nedirbeo.com", "VISIT SITE"),
    ("wipeout", "GAME · LAN MULTIPLAYER", "Wipeout", "A multiplayer parkour game played over LAN by 50+ people at an event.",
     f"{SITE}/projects/wipeout", "CASE STUDY"),
    ("hesappcim", "FINANCE · WEB APP", "HesAppcım", "An app for tracking shared expenses and calculating who owes whom.",
     f"{SITE}/projects/hesappcim", "CASE STUDY"),
    ("yayla-yemek-evi", "RESTAURANT · SHOWCASE", "Yayla Yemek Evi", "The website of a village restaurant in Pamuklu, North Cyprus.",
     "https://www.yaylayemekevi.com", "VISIT SITE"),
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
def wrap(face: Face, text: str, size: float, width: float) -> list:
    """Greedy word wrap using real advance widths."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and face.layout(trial, size).width > width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def card(slug: str, kicker: str, name: str, sentence: str, cta_text: str, theme: str, mobile: bool, faces: dict) -> str:
    t = THEMES[theme]
    W = 204
    H = 150 if mobile else 200
    data = base64.b64encode((MEDIA / f"{slug}.webp").read_bytes()).decode("ascii")
    defs, body, border = frame(W, H, t)
    defs += f'<clipPath id="shot"><rect x="10" y="10" width="184" height="104" rx="7"/></clipPath>'
    parts = [
        f'<rect x="10" y="10" width="184" height="104" rx="7" fill="{t["dial"]}"/>',
        f'<image href="data:image/webp;base64,{data}" x="10" y="10" width="184" height="104" '
        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#shot)"/>',
        f'<rect x="10.5" y="10.5" width="183" height="103" rx="6.5" fill="none" stroke="{t["sheen"]}" stroke-opacity="0.08"/>',
    ]
    if mobile:
        nm = faces[700].layout(name, 19, tracking=-0.01)
        parts.append(nm.path(14, 140, t["ink"]))
    else:
        kk = faces[700].layout(kicker, 8.8, tracking=0.2)
        parts.append(kk.path(14, 137, t["accent"], nd=2))
        nm = faces[700].layout(name, 18, tracking=-0.01)
        parts.append(nm.path(14, 160, t["ink"]))
        cta = faces[700].layout(cta_text, 8.5, tracking=0.18)
        arrow = faces[500].layout("→", 11)
        parts.append(f'<rect x="14" y="{H - 25.5}" width="176" height="1" fill="{t["border"]}"/>')
        parts.append(cta.path(14, H - 10, t["accent"], nd=2))
        parts.append(arrow.path(W - 14 - arrow.width, H - 9.5, t["accent"], nd=2))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{name} — {sentence}</title>
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
            for slug, kicker, name, sentence, _link, cta_text in PROJECTS:
                p = ASSETS / f"card-{slug}-{theme}{m}.svg"
                p.write_text(card(slug, kicker, name, sentence, cta_text, theme, mobile, faces), encoding="utf-8", newline="\n")
                written.append(p)
    for p in written:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:>7,} bytes")


if __name__ == "__main__":
    sys.exit(main())
