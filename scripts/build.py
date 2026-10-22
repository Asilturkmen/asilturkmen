"""Builds the profile README and the single scene it shows.

The README is one continuous picture, night at the top and dawn at the bottom:
  the lighthouse beam lights up the name, a short about, four project screens
  (the beam passes over each), the tools (a band of light sweeps across them),
  and sunrise with asilturkmen.com. The whole picture links to the site; the
  project case studies and contact links sit under it as text.

Projects, skills and covers come from the portfolio site's content files
(../AsilPortfolio/content, or set SITE_DIR), so a change there is one rerun
away. Everything is plain SVG + SMIL: it animates inside GitHub's <img>,
with no script and no external fonts. Text is converted to paths from
Satoshi, the font used on asilturkmen.com.

    python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
    .venv/bin/python scripts/build.py
"""
import base64
import html
import io
import json
import math
import os
import random
import re
import urllib.request

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
CACHE = os.path.join(ROOT, "scripts", ".cache")
SITE_DIR = os.environ.get("SITE_DIR", os.path.join(os.path.dirname(ROOT), "AsilPortfolio"))
SITE = "https://asilturkmen.com"

FONTS = {
    500: "https://cdn.fontshare.com/wf/P2LQKHE6KA6ZP4AAGN72KDWMHH6ZH3TA/ZC32TK2P7FPS5GFTL46EU6KQJA24ZYDB/7AHDUZ4A7LFLVFUIFSARGIWCRQJHISQP.woff2",
    700: "https://cdn.fontshare.com/wf/LAFFD4SDUCDVQEXFPDC7C53EQ4ZELWQI/PXCT3G6LO6ICM5I3NTYENYPWJAECAWDD/GHM6WVH6MILNYOOCXHXB5GTSGNTMGXZR.woff2",
    900: "https://cdn.fontshare.com/wf/NHPGVFYUXYXE33DZ75OIT4JFGHITX5PE/PSUTMASCDJTVPERDYJZPN23BVUFUCQIF/J64QX5IPOHK56I2KYUNBQ5M2XWZEYKYX.woff2",
}
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{}.svg"
TABLER = "https://cdn.jsdelivr.net/npm/@tabler/icons@3.19.0/icons/outline/{}.svg"
ICONS = {  # site skill slug -> icon source
    "typescript": ("si", "typescript"), "react": ("si", "react"), "next-js": ("si", "nextdotjs"),
    "vue-3": ("si", "vuedotjs"), "vite": ("si", "vite"), "tailwind-css": ("si", "tailwindcss"),
    "node-js": ("si", "nodedotjs"), "laravel": ("si", "laravel"), "python": ("si", "python"),
    "flask": ("si", "flask"), "postgresql": ("si", "postgresql"),
    "sqlite": ("si", "sqlite"), "unity": ("si", "unity"), "c-sharp": ("tabler", "brand-c-sharp"),
    "docker": ("si", "docker"), "git": ("si", "git"), "vercel": ("si", "vercel"),
}

ABOUT = (
    "I'm Asil Türkmen, a Software Engineering student at Eastern Mediterranean University in North Cyprus. "
    "I work on web apps, APIs, automation and games."
)
ABOUT_MORE = f"You can find more about my projects and my CV at **[asilturkmen.com]({SITE})**."
# One line per project, written for this page; the long story is on the site.
PROJECTS = [
    ("nedirbeo", "A community dictionary for Cypriot Turkish."),
    ("wipeout", "A multiplayer parkour game played over LAN by 50+ people at an event."),
    ("hesappcim", "An app for tracking shared expenses and calculating who owes whom."),
    ("yayla-yemek-evi", "The website of a village restaurant in Pamuklu, North Cyprus."),
]
# Where to keep the cover when cropping it to a 16:9 screen (0 = top, 0.5 = centre).
COVER_FOCUS = {"wipeout": 0.0}
# Tools whose icon already reads as its name; the chip shows the icon alone.
NAME_IN_ICON = {"c-sharp"}
TOOLS = [
    ("FRONTEND", ["typescript", "react", "next-js", "vue-3", "vite", "tailwind-css"]),
    ("BACKEND & DATA", ["node-js", "laravel", "python", "flask", "postgresql", "sqlite"]),
    ("GAMES & DEVELOPMENT TOOLS", ["unity", "c-sharp", "docker", "git", "vercel"]),
]
WORK_LABEL, TOOLS_LABEL = "Selected work", "Tools I use"
DAWN_KICKER, DAWN_SUB = "MORE ABOUT MY WORK", "PROJECTS · CASE STUDIES · CV"
LINKS = [
    ("LinkedIn", "https://www.linkedin.com/in/asil-t%C3%BCrkmen-224ab0241/"),
    ("Email", "mailto:contact.asilturkmen@gmail.com"),
    ("Instagram", "https://instagram.com/asil_turkmen28"),
    ("CV", f"{SITE}/cv/cveng.pdf"),
    ("Buy me a coffee", "https://buymeacoffee.com/turkmenasil"),
]

PERIOD = 10.0  # seconds per lighthouse revolution
STEPS = 48
WARM = "#fbf1dc"
SAND = "#e2cfa6"
AMBER = "#d9a861"


# ------------------------------------------------------------------ helpers
def f(x, d=1):
    s = f"{x:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fetch(url, name):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "readme-build"})
        with urllib.request.urlopen(req) as r, open(path, "wb") as fh:
            fh.write(r.read())
    return path


class Face:
    def __init__(self, weight):
        self.tt = TTFont(fetch(FONTS[weight], f"Satoshi-{weight}.woff2"))
        self.tt.flavor = None
        buf = io.BytesIO()
        self.tt.save(buf)
        self.hb = hb.Font(hb.Face(hb.Blob(buf.getvalue())))
        self.upem = self.tt["head"].unitsPerEm
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def _shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return buf

    def width(self, text, size, tracking=0.0):
        buf = self._shape(text)
        adv = sum(p.x_advance for p in buf.glyph_positions) * size / self.upem
        return adv + tracking * (len(buf.glyph_positions) - 1)

    def path(self, text, x, y, size, tracking=0.0, anchor="start"):
        if anchor == "middle":
            x -= self.width(text, size, tracking) / 2
        elif anchor == "end":
            x -= self.width(text, size, tracking)
        buf = self._shape(text)
        scale = size / self.upem
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f(v, 1 if size < 30 else 2))  # 0.1px is invisible on small text
        adv = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            tx = x + adv + pos.x_offset * scale
            ty = y - pos.y_offset * scale
            self.glyphs[self.order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, tx, ty)))
            adv += pos.x_advance * scale + tracking
        return pen.getCommands()

    def wrap(self, text, size, width, tracking=0.0):
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if cur and self.width(trial, size, tracking) > width:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        return lines + [cur]


def save(name, svg):
    with open(os.path.join(ASSETS, name), "w") as fh:
        fh.write(svg)
    print(f"  assets/{name:<26} {len(svg.encode()) / 1024:6.0f} KB")


def stars(rng, n, W, top, bottom, still, avoid=(), fade=lambda y: 1.0):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(top, bottom)
        r = rng.choice([0.5, 0.7, 0.9, 1.1])
        base = rng.uniform(0.25, 0.85) * fade(y)
        dur, begin = rng.uniform(2.5, 7.0), rng.uniform(0, 6)
        if base < 0.04 or any(ax0 < x < ax1 and ay0 < y < ay1 for ax0, ay0, ax1, ay1 in avoid):
            continue
        tw = "" if still else (
            f'<animate attributeName="opacity" values="{f(base, 2)};{f(base * 0.2, 2)};{f(base, 2)}" '
            f'dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        )
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#d6deea" opacity="{f(base, 2)}">{tw}</circle>')
    return "".join(out)


def sea_lines(W, hz, depth, still, color="#1d3449", strength=1.0):
    out = []
    for i, (dy, amp, wl, dur, op, sw) in enumerate([
        (5, 0.5, 26, 16, 0.30, 0.7), (12, 0.8, 32, 14, 0.34, 0.8), (22, 1.1, 40, 12, 0.38, 0.9),
        (36, 1.6, 52, 10, 0.42, 1.0), (54, 2.2, 66, 8.5, 0.46, 1.1), (77, 3.0, 84, 7, 0.50, 1.3),
    ]):
        y0 = hz + dy * depth
        pts, x = [], -wl
        while x <= W + wl:
            pts.append(f"{f(x)},{f(y0 + amp * math.sin(2 * math.pi * x / wl + i))}")
            x += 3
        drift = "" if still else (
            f'<animateTransform attributeName="transform" type="translate" from="0 0" '
            f'to="{-wl if i % 2 == 0 else wl} 0" dur="{dur}s" repeatCount="indefinite"/>'
        )
        out.append(
            f'<g>{drift}<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
            f'stroke-opacity="{f(op * strength, 2)}" stroke-width="{sw}"/></g>'
        )
    return "".join(out)


def tower(lx, ly, hz):
    body, lit, glass, rock = "#0b1422", "#0e1a2b", "#1a2433", "#050a12"
    return (
        f'<path d="M{lx - 46},{hz + 4} C{lx - 32},{hz - 6} {lx - 22},{hz - 9} {lx - 10},{hz - 8} L{lx + 12},{hz - 8} '
        f'C{lx + 26},{hz - 7} {lx + 38},{hz - 2} {lx + 52},{hz + 4} Z" fill="{rock}"/>'
        f'<polygon points="{lx - 16},{hz - 8} {lx + 16},{hz - 8} {lx + 9},{ly + 16} {lx - 9},{ly + 16}" fill="{body}"/>'
        f'<polygon points="{lx},{hz - 8} {lx + 16},{hz - 8} {lx + 9},{ly + 16} {lx},{ly + 16}" fill="{lit}"/>'
        f'<rect x="{lx - 10}" y="{ly + 52}" width="20" height="2" fill="{lit}"/>'
        f'<rect x="{lx - 12}" y="{ly + 11}" width="24" height="5" rx="1" fill="{body}"/>'
        f'<rect x="{lx - 8}" y="{ly - 8}" width="16" height="19" fill="{glass}"/>'
        f'<polygon points="{lx - 12},{ly - 8} {lx + 12},{ly - 8} {lx},{ly - 20}" fill="{body}"/>'
        f'<rect x="{lx - 0.6}" y="{ly - 25}" width="1.2" height="6" fill="{body}"/>'
    )


def lighten(rgb, amount):
    r, g, b = (int(c) for c in rgb.split(","))
    mix = [round(c + (255 - c) * amount) for c in (r, g, b)]
    return "#" + "".join(f"{c:02x}" for c in mix)


def gradient(gid, y0, y1, stops):
    """Vertical gradient in canvas units: stops are (y, colour) pairs."""
    inner = "".join(f'<stop offset="{f((y - y0) / (y1 - y0), 4)}" stop-color="{c}"/>' for y, c in stops)
    return f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{f(y0)}" x2="0" y2="{f(y1)}">{inner}</linearGradient>'


def cover_data(project, w, h):
    src = os.path.join(SITE_DIR, "public", project["cover"]["src"].lstrip("/"))
    im = Image.open(src).convert("RGB")
    target = w / h
    if im.width / im.height > target:
        nw = round(im.height * target)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = round(im.width / target)
        top = max(0, round((im.height - nh) * COVER_FOCUS.get(project["slug"], 0.5)))
        im = im.crop((0, top, im.width, top + nh))
    im = im.resize((round(w * 1.75), round(h * 1.75)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=74, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def icon_symbol(slug, size):
    """Icon drawn once in <defs>; each <use> sets its colour through currentColor."""
    kind, name = ICONS[slug]
    scale = f"scale({f(size / 24, 4)})"
    if kind == "si":
        raw = open(fetch(SIMPLE_ICONS.format(name), f"si-{name}.svg")).read()
        d = re.search(r'<path d="([^"]+)"', raw).group(1)
        return f'<path id="i-{slug}" d="{d}" fill="currentColor" transform="{scale}"/>'
    raw = open(fetch(TABLER.format(name), f"tabler-{name}.svg")).read()
    paths = "".join(f'<path d="{p}"/>' for p in re.findall(r'<path d="([^"]+)"', raw) if p != "M0 0h24v24H0z")
    return (
        f'<g id="i-{slug}" transform="{scale}" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{paths}</g>'
    )


# ------------------------------------------------------------------ the scene
HERO = {
    False: dict(
        W=846, H=300, horizon=214, lx=722, ly=108, stars=80, refl=(380, 360), margin=64,
        name=[("Asil Türkmen", 64, 148, 60, -1.0)],
        sub=[("SOFTWARE ENGINEERING · NORTH CYPRUS", 67, 182, 13, 3.6)],
        beam_l=(900, -36, 100), beam_r=(320, -28, 76),
    ),
    True: dict(
        W=420, H=380, horizon=272, lx=346, ly=166, stars=50, refl=(180, 170), margin=24,
        name=[("Asil", 24, 126, 60, -1.0), ("Türkmen", 24, 186, 60, -1.0)],
        sub=[("SOFTWARE ENGINEERING", 26, 224, 12, 3.0), ("NORTH CYPRUS", 26, 244, 12, 3.0)],
        beam_l=(460, -118, 150), beam_r=(140, -20, 50),
    ),
}


def hero(L, faces, still, rng):
    """The night: sky, the lighthouse and its beam over the name. Returns (defs, body)."""
    W, hz, lx, ly = L["W"], L["horizon"], L["lx"], L["ly"]
    left, right, flash = [], [], []
    for k in range(STEPS + 1):
        a = 2 * math.pi * k / STEPS
        left.append(max(0.001, math.sin(a)))
        right.append(max(0.001, -math.sin(a)))
        flash.append(max(0.0, math.cos(a)) ** 6)

    def anim(attr, seq, lo, hi):
        if still:
            return ""
        vals = ";".join(f(lo + (hi - lo) * v, 3) for v in seq)
        return f'<animate attributeName="{attr}" values="{vals}" dur="{PERIOD}s" repeatCount="indefinite"/>'

    def sweep(seq):
        if still:
            return ""
        vals = ";".join(f"{f(v, 3)} 1" for v in seq)
        return f'<animateTransform attributeName="transform" type="scale" values="{vals}" dur="{PERIOD}s" repeatCount="indefinite"/>'

    def rest(value_still, seq, lo, hi):
        return f(value_still, 3) if still else f(lo + (hi - lo) * seq[0], 3)

    bl_len, bl_top, bl_bot = L["beam_l"]
    br_len, br_top, br_bot = L["beam_r"]
    beam_l = f"0,0 {-bl_len},{bl_top} {-bl_len},{bl_bot}"
    beam_r = f"0,0 {br_len},{br_top} {br_len},{br_bot}"
    mid_l = (bl_top + bl_bot) / 2
    right_beam = "" if still else f'<g>{sweep(right)}<polygon points="{beam_r}" fill="url(#beamR)"/></g>'
    name_d = "".join(faces[700].path(t, x, y, s, tr) for t, x, y, s, tr in L["name"])
    sub_d = "".join(faces[500].path(t, x, y, s, tr) for t, x, y, s, tr in L["sub"])
    rx, rrx = L["refl"]

    defs = f'''
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#03060c"/><stop offset="0.75" stop-color="#091424"/><stop offset="1" stop-color="#10213a"/>
  </linearGradient>
  <linearGradient id="beamL" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{-bl_len}" y2="{f(mid_l)}">
    <stop offset="0" stop-color="#fff2d2" stop-opacity="0.62"/><stop offset="0.3" stop-color="#ffe6b0" stop-opacity="0.2"/>
    <stop offset="1" stop-color="#ffe6b0" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="beamR" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{br_len}" y2="{f((br_top + br_bot) / 2)}">
    <stop offset="0" stop-color="#fff2d2" stop-opacity="0.55"/><stop offset="1" stop-color="#ffe6b0" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="beamMaskG" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{-bl_len}" y2="{f(mid_l)}">
    <stop offset="0" stop-color="#fff"/><stop offset="0.82" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
  </linearGradient>
  <radialGradient id="lamp"><stop offset="0" stop-color="#fff1cc" stop-opacity="0.95"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient>
  <linearGradient id="column" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe2a6" stop-opacity="0.55"/><stop offset="1" stop-color="#ffe2a6" stop-opacity="0"/>
  </linearGradient>
  <filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
  <filter id="softer" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
  <mask id="beamMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{hz + 120}">
    <g transform="translate({lx} {ly})" filter="url(#softer)"><g>{sweep(left)}<polygon points="{beam_l}" fill="url(#beamMaskG)"/></g></g>
  </mask>'''
    body = f'''<rect width="{W}" height="{hz}" fill="url(#sky)"/>
{stars(rng, L["stars"], W, 6, hz - 24, still, avoid=[(lx - 42, ly - 28, lx + 48, hz)])}
<rect y="{hz - 1}" width="{W}" height="2" fill="#1a2f48" opacity="0.6"/>
{sea_lines(W, hz, 1.0, still)}
<ellipse cx="{rx}" cy="{hz + 7}" rx="{rrx}" ry="3.5" fill="#ffe6b0" opacity="{rest(0.16, left, 0, 0.16)}" filter="url(#soft)">{anim("opacity", left, 0, 0.16)}</ellipse>
<rect x="{lx - 6}" y="{hz + 2}" width="12" height="80" fill="url(#column)" filter="url(#soft)" opacity="{rest(0.04, flash, 0.04, 0.5)}">{anim("opacity", flash, 0.04, 0.5)}</rect>
<path d="{name_d}" fill="#16243a"/>
<path d="{sub_d}" fill="#2e3f55"/>
<g mask="url(#beamMask)">
  <path d="{name_d}" fill="#ffe7b8" filter="url(#soft)" opacity="0.7"/>
  <path d="{name_d}" fill="{WARM}"/>
  <path d="{sub_d}" fill="{SAND}"/>
</g>
<g transform="translate({lx} {ly})" filter="url(#soft)">
  <g>{sweep(left)}<polygon points="{beam_l}" fill="url(#beamL)"/></g>
  {right_beam}
</g>
{tower(lx, ly, hz)}
<circle cx="{lx}" cy="{ly}" r="64" fill="url(#lamp)" opacity="{rest(0, flash, 0, 0.42)}">{anim("opacity", flash, 0, 0.42)}</circle>
<circle cx="{lx}" cy="{ly}" r="22" fill="url(#lamp)" opacity="{rest(0.28, flash, 0.28, 1)}">{anim("opacity", flash, 0.28, 1)}</circle>
<circle cx="{lx}" cy="{ly}" r="3" fill="#fff6e0"/>'''
    return defs, body


def section_label(faces, text, x, y, right):
    """Lamp dot, label and a hairline running to the right margin; y is the text baseline."""
    tw = faces[700].width(text, 13, 0.5)
    return (
        f'<circle cx="{x + 3}" cy="{f(y - 4.5)}" r="8" fill="url(#dot)"/><circle cx="{x + 3}" cy="{f(y - 4.5)}" r="2.6" fill="{AMBER}"/>'
        f'<path d="{faces[700].path(text, x + 18, y, 13, 0.5)}" fill="{AMBER}"/>'
        f'<rect x="{f(x + 18 + tw + 14)}" y="{f(y - 5)}" width="{f(right - (x + 18 + tw + 14))}" height="1" fill="#8b97a6" opacity="0.28"/>'
    )


def scene(faces, skills, projects, mobile, still):
    rng = random.Random(11)
    L = HERO[mobile]
    W, hz, m = L["W"], L["horizon"], L["margin"]
    right = W - m
    cw = right - m
    defs, body = [], []

    # night ----------------------------------------------------------------
    hero_defs, hero_body = hero(L, faces, still, rng)
    defs.append(hero_defs)

    # about ----------------------------------------------------------------
    about_size, about_lh = (15, 22) if mobile else (16, 24)
    about = faces[500].wrap(ABOUT, about_size, cw)
    y = L["H"] + (38 if mobile else 44)
    about_paths = []
    for line in about:
        about_paths.append(f'<path d="{faces[500].path(line, m, y, about_size)}" fill="#a9b6c6"/>')
        y += about_lh
    about_bottom = y - about_lh

    # selected work --------------------------------------------------------
    work_label_y = about_bottom + (50 if mobile else 54)
    cols = 2 if mobile else 4
    gap = 14 if mobile else 18
    tw = (cw - gap * (cols - 1)) / cols
    th = tw * 9 / 16
    name_size, desc_size, desc_lh = 15, 11.5, 16
    work = []
    tile_top = work_label_y + 20
    rows = [projects[i:i + cols] for i in range(0, len(projects), cols)]
    index = 0
    for row in rows:
        wrapped = [faces[500].wrap(line, desc_size, tw) for _, line in row]
        row_h = th + 24 + max(len(w) for w in wrapped) * desc_lh + 4
        for c, ((project, line), desc) in enumerate(zip(row, wrapped)):
            x = m + c * (tw + gap)
            ty = tile_top
            accent = project.get("accent") or "201, 162, 110"
            sid = f"s{index}"
            defs.append(f'<clipPath id="{sid}"><rect x="{f(x)}" y="{f(ty)}" width="{f(tw)}" height="{f(th)}" rx="6"/></clipPath>')
            period, sweep_part, begin = 9.0, 1.4, 1.5 + index * 1.9
            g0, g1 = x - th * 0.6 - 120, x + tw + 60
            glint = "" if still else (
                f'<g clip-path="url(#{sid})"><g transform="skewX(-22)">'
                f'<rect x="{f(g0)}" y="{f(ty - 10)}" width="90" height="{f(th + 20)}" fill="url(#glint)">'
                f'<animate attributeName="x" values="{f(g0 + th * 0.4)};{f(g1 + th * 0.4)};{f(g1 + th * 0.4)}" '
                f'keyTimes="0;{f(sweep_part / period, 3)};1" dur="{period}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
                f"</rect></g></g>"
            )
            work.append(
                f'<rect x="{f(x + 6)}" y="{f(ty + 8)}" width="{f(tw - 12)}" height="{f(th - 6)}" rx="8" '
                f'fill="{lighten(accent, 0.1)}" opacity="0.28" filter="url(#spill)"/>'
                f'<image href="data:image/jpeg;base64,{cover_data(project, tw, th)}" x="{f(x)}" y="{f(ty)}" '
                f'width="{f(tw)}" height="{f(th)}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{sid})"/>'
                f'<rect x="{f(x)}" y="{f(ty)}" width="{f(tw)}" height="{f(th)}" rx="6" fill="url(#shade)"/>'
                f"{glint}"
                f'<rect x="{f(x + 0.5)}" y="{f(ty + 0.5)}" width="{f(tw - 1)}" height="{f(th - 1)}" rx="6" fill="none" stroke="#fff" stroke-opacity="0.1"/>'
                f'<path d="{faces[700].path(project["title"], x, ty + th + 24, name_size, -0.2)}" fill="{WARM}"/>'
            )
            for i, text in enumerate(desc):
                work.append(f'<path d="{faces[500].path(text, x, ty + th + 43 + i * desc_lh, desc_size)}" fill="#8e9db1"/>')
            index += 1
        tile_top += row_h + (18 if mobile else 0)
    work_bottom = tile_top - (18 if mobile else 0)

    # tools ----------------------------------------------------------------
    tools_label_y = work_bottom + (40 if mobile else 44)
    icon, chip_size, chip_gap = 16, 12, 16
    group_size, group_track = 9.5, 1.4
    row_h = 30 if mobile else 34
    chips, group_paths = [], []
    y = tools_label_y + (36 if mobile else 42)
    label_col = 0 if mobile else max(faces[700].width(g, group_size, group_track) for g, _ in TOOLS) + 34
    for group, slugs in TOOLS:
        group_paths.append(f'<path d="{faces[700].path(group, m, y, group_size, group_track)}" fill="#7489a3"/>')
        if mobile:
            y += 26
        x = m + label_col
        for slug in slugs:
            name = "" if slug in NAME_IN_ICON else skills[slug]["name"]
            w = icon + (7 + faces[500].width(name, chip_size) if name else 0)
            if x + w > right:
                x = m + label_col
                y += row_h
            chips.append((slug, x, y))
            x += w + chip_gap
        y += row_h + (10 if mobile else 0)
    tools_top, tools_bottom = tools_label_y + 12, y - row_h + 12

    symbols = "".join(icon_symbol(s, icon) for s, _, _ in chips)
    symbols += "".join(
        f'<path id="n-{s}" d="{faces[500].path(skills[s]["name"], x + icon + 7, y, chip_size)}"/>'
        for s, x, y in chips if s not in NAME_IN_ICON
    )
    defs.append(symbols)

    def tool_layer(dim):
        out = []
        for s, x, y in chips:
            color = "#3a4c68" if dim else (skills[s].get("heroColor") or "#e9dcc0")
            out.append(f'<use href="#i-{s}" x="{f(x)}" y="{f(y - icon / 2 - 4.3)}" color="{color}"/>')
            if s not in NAME_IN_ICON:
                out.append(f'<use href="#n-{s}" fill="{"#6b7c93" if dim else "#f3e7cd"}"/>')
        return "".join(out)

    band, t_period, travel = 220, 6.5, 3.0
    bx0, bx1 = W + 40, -band - 40
    move = "" if still else (
        f'<animate attributeName="x" values="{bx0};{bx1};{bx1}" keyTimes="0;{f(travel / t_period, 3)};1" '
        f'dur="{t_period}s" begin="0.6s" repeatCount="indefinite"/>'
    )
    defs.append(
        f'<mask id="sweep" maskUnits="userSpaceOnUse" x="0" y="{f(tools_top)}" width="{W}" height="{f(tools_bottom - tools_top)}">'
        f'<rect x="{bx0}" y="{f(tools_top)}" width="{band}" height="{f(tools_bottom - tools_top)}" fill="url(#band)">{move}</rect></mask>'
    )
    tools_lit = tool_layer(False) if still else f'<g mask="url(#sweep)">{tool_layer(False)}</g>'
    glow_move = "" if still else (
        f'<animate attributeName="cx" values="{bx0 + band / 2};{bx1 + band / 2};{bx1 + band / 2}" keyTimes="0;{f(travel / t_period, 3)};1" '
        f'dur="{t_period}s" begin="0.6s" repeatCount="indefinite"/>'
    )
    tools_beam = "" if still else (
        f'<ellipse cx="{bx0 + band / 2}" cy="{f((tools_top + tools_bottom) / 2)}" rx="{band * 0.6}" '
        f'ry="{f((tools_bottom - tools_top) / 2 + 24)}" fill="url(#bandWarm)">{glow_move}</ellipse>'
    )

    # dawn -----------------------------------------------------------------
    cx = W / 2
    kicker_y = tools_bottom + (70 if mobile else 78)
    ds = 40 if mobile else 54
    domain_y = kicker_y + (50 if mobile else 60)
    sub_y = domain_y + (32 if mobile else 36)
    hz2 = sub_y + (46 if mobile else 52)
    H = round(hz2 + (40 if mobile else 44))
    domain = "asilturkmen.com"
    dw = faces[900].width(domain, ds, -0.8)
    arrow_w = ds * 0.42
    dx = cx - (dw + 14 + arrow_w) / 2
    domain_d = faces[900].path(domain, dx, domain_y, ds, -0.8)
    ax, ay = dx + dw + 14, domain_y - ds * 0.34
    a4 = arrow_w * 0.4
    sun_r = 24 if mobile else 30

    shimmer = []
    for i in range(7):
        yy = hz2 + 5 + i * (5 + i * 0.8)
        if yy > H - 3:
            break
        rxs = 12 + i * 8 + rng.uniform(-3, 3)
        base = rng.uniform(0.35, 0.7) * (1 - i * 0.08)
        anim = "" if still else (
            f'<animate attributeName="opacity" values="{f(base, 2)};{f(base * 0.3, 2)};{f(base, 2)}" '
            f'dur="{f(rng.uniform(1.6, 3.4))}s" begin="{f(rng.uniform(0, 2))}s" repeatCount="indefinite"/>'
        )
        shimmer.append(f'<ellipse cx="{f(cx + rng.uniform(-5, 5))}" cy="{f(yy)}" rx="{f(rxs)}" ry="1.2" fill="#ffd29a" opacity="{f(base, 2)}">{anim}</ellipse>')

    birds = []
    for i, (bx, by) in enumerate([(0.18, kicker_y - 24), (0.22, kicker_y - 36), (0.74, sub_y + 6)][: 2 if mobile else 3]):
        up, down = "M-6,0 Q-3,-4 0,0 Q3,-4 6,0", "M-6,-1.4 Q-3,2.2 0,0 Q3,2.2 6,-1.4"
        flap = "" if still else f'<animate attributeName="d" values="{up};{down};{up}" dur="{f(0.8 + i * 0.13, 2)}s" repeatCount="indefinite"/>'
        drift = "" if still else (
            f'<animateTransform attributeName="transform" type="translate" values="{f(W * bx)} {f(by)};{f(W * bx + 60)} {f(by - 8)};{f(W * bx)} {f(by)}" '
            f'dur="{18 + i * 4}s" repeatCount="indefinite"/>'
        )
        birds.append(
            f'<g transform="translate({f(W * bx)} {f(by)})">{drift}<path d="{up}" fill="none" stroke="#2c2238" '
            f'stroke-width="1.3" stroke-linecap="round">{flap}</path></g>'
        )
    glow_anim = "" if still else f'<animate attributeName="r" values="{sun_r * 4.2};{sun_r * 4.8};{sun_r * 4.2}" dur="7s" repeatCount="indefinite"/>'

    # one sky from the night sea down to sunrise ----------------------------
    sea_end = hz + 96
    defs.append(gradient("deep", hz, hz2, [
        (hz, "#07111e"), (sea_end, "#03070d"), (about_bottom + 40, "#050a15"),
        (tools_label_y, "#08112a"), (kicker_y - 40, "#171a3c"), (kicker_y + 20, "#2b2650"),
        (sub_y, "#5a4069"), (hz2 - 26, "#b06d69"), (hz2 - 8, "#e29769"), (hz2, "#f5c38c"),
    ]))
    defs.append(gradient("sea2", hz2, H, [(hz2, "#3a2f4e"), (hz2 + 16, "#1c1b31"), (H, "#0b0c19")]))
    defs.append(f'''
  <radialGradient id="dot"><stop offset="0" stop-color="#e8b464" stop-opacity="0.5"/><stop offset="1" stop-color="#e8b464" stop-opacity="0"/></radialGradient>
  <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff3d6" stop-opacity="0"/><stop offset="0.5" stop-color="#fff3d6" stop-opacity="0.32"/><stop offset="1" stop-color="#fff3d6" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0.5" stop-color="#02050a" stop-opacity="0"/><stop offset="1" stop-color="#02050a" stop-opacity="0.3"/></linearGradient>
  <linearGradient id="band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset="0.5" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
  <radialGradient id="bandWarm"><stop offset="0" stop-color="#ffe6b0" stop-opacity="0.08"/><stop offset="1" stop-color="#ffe6b0" stop-opacity="0"/></radialGradient>
  <radialGradient id="sunglow"><stop offset="0" stop-color="#ffcf8f" stop-opacity="0.75"/><stop offset="0.4" stop-color="#ff9f6a" stop-opacity="0.25"/><stop offset="1" stop-color="#ff9f6a" stop-opacity="0"/></radialGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#fff3d8"/><stop offset="1" stop-color="#ffd59c"/></radialGradient>
  <clipPath id="above"><rect y="{f(kicker_y - 60)}" width="{W}" height="{f(hz2 - kicker_y + 60)}"/></clipPath>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  <filter id="spill" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>
  <filter id="dglow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>''')

    def fade(y):  # stars thin out as the sky warms
        return max(0.0, 1 - (y - hz) / (kicker_y - hz)) * 0.55

    body = [
        f'<rect y="{hz}" width="{W}" height="{f(hz2 - hz)}" fill="url(#deep)"/>',
        stars(rng, 70 if mobile else 90, W, sea_end + 20, kicker_y + 10, still, fade=fade),
        hero_body,
        "".join(about_paths),
        section_label(faces, WORK_LABEL, m, work_label_y, right),
        "".join(work),
        section_label(faces, TOOLS_LABEL, m, tools_label_y, right),
        tools_beam,
        "".join(group_paths),
        tool_layer(True),
        tools_lit,
        f'<g clip-path="url(#above)"><circle cx="{f(cx)}" cy="{f(hz2 + 4)}" r="{sun_r * 4.2}" fill="url(#sunglow)">{glow_anim}</circle>'
        f'<circle cx="{f(cx)}" cy="{f(hz2 + 8)}" r="{sun_r}" fill="url(#sun)"/></g>',
        f'<rect y="{f(hz2)}" width="{W}" height="{f(H - hz2)}" fill="url(#sea2)"/>',
        f'<rect y="{f(hz2 - 0.5)}" width="{W}" height="1.5" fill="#ffd9a6" opacity="0.45"/>',
        "".join(shimmer),
        "".join(birds),
        f'<path d="{faces[700].path(DAWN_KICKER, cx, kicker_y, 11.5, 3.8, "middle")}" fill="#f2d7b6" opacity="0.85"/>',
        f'<path d="{domain_d}" fill="#ffcf9a" opacity="0.32" filter="url(#dglow)"/><path d="{domain_d}" fill="#fff4e6"/>',
        f'<path d="M{f(ax)},{f(ay)} h{f(arrow_w)} m-{f(a4)},-{f(a4)} l{f(a4)},{f(a4)} l-{f(a4)},{f(a4)}" fill="none" '
        f'stroke="#fff4e6" stroke-width="{f(ds * 0.075)}" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path d="{faces[500].path(DAWN_SUB, cx, sub_y, 10.5, 3.4, "middle")}" fill="#ecc9a8" opacity="0.8"/>',
    ]

    title = (
        "Asil Türkmen, software engineering, North Cyprus. A lighthouse beam sweeps over the night sea and lights up the name. "
        f"{ABOUT} Selected work: " + "; ".join(f'{p["title"]}: {line.rstrip(".")}' for p, line in projects)
        + ". Tools I use: " + ", ".join(skills[s]["name"] for _, slugs in TOOLS for s in slugs)
        + ". Dawn breaks over the sea: more about my work at asilturkmen.com."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">\n'
        f'<title id="t">{html.escape(title)}</title>\n<defs>{"".join(defs)}</defs>\n'
        f'<g clip-path="url(#frame)">\n{chr(10).join(body)}\n</g>\n</svg>\n'
    ), title


# ------------------------------------------------------------------ README
def readme(projects, alt):
    picture = f'''<p><a href="{SITE}"><picture>
  <source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="assets/readme-mobile-still.svg">
  <source media="(max-width: 600px)" srcset="assets/readme-mobile.svg">
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/readme-still.svg">
  <img src="assets/readme.svg" width="100%" alt="{html.escape(alt)}">
</picture></a></p>'''
    work = " · ".join(f'<a href="{SITE}/projects/{p["slug"]}">{html.escape(p["title"])}</a>' for p, _ in projects)
    contact = " · ".join(f'<a href="{u}">{n}</a>' for n, u in LINKS)
    parts = [
        picture,
        "",
        f'<p align="center">{ABOUT_MORE.replace("**[asilturkmen.com](" + SITE + ")**", f"<b><a href=\"{SITE}\">asilturkmen.com</a></b>")}<br>',
        f"Case studies: {work}</p>",
        "",
        f'<p align="center">{contact}</p>',
        "",
    ]
    with open(os.path.join(ROOT, "README.md"), "w") as fh:
        fh.write("\n".join(parts))
    print("  README.md")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(SITE_DIR, "content", "site.json")) as fh:
        skills = {s["slug"]: s for s in json.load(fh)["skills"]}
    projects = []
    for slug, line in PROJECTS:
        with open(os.path.join(SITE_DIR, "content", "projects", f"{slug}.json")) as fh:
            projects.append((json.load(fh), line))

    faces = {w: Face(w) for w in FONTS}
    alt = ""
    for mobile in (False, True):
        for still in (False, True):
            svg, title = scene(faces, skills, projects, mobile, still)
            save(f"readme{'-mobile' if mobile else ''}{'-still' if still else ''}.svg", svg)
            alt = alt or title
    readme(projects, alt)


if __name__ == "__main__":
    main()
