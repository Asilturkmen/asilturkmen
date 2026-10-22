"""Builds the profile README and every image it uses.

The page reads as one night at sea, top to bottom:
  hero      a lighthouse beam lights up the name (night)
  work      four project cards, the beam passes over each screen
  tools     the beam sweeps across the tools one by one
  dawn      sunrise, with asilturkmen.com written in the sky

Projects, skills and the bio come from the portfolio site's content files
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

# One line per card, written for this page; the long story is on the site.
PROJECTS = [
    ("nedirbeo", "A community dictionary for Cypriot Turkish."),
    ("wipeout", "A multiplayer parkour game played over LAN by 50+ people at an event."),
    ("hesappcim", "An app for tracking shared expenses and calculating who owes whom."),
    ("yayla-yemek-evi", "The website of a village restaurant in Pamuklu, North Cyprus."),
]
# Where to keep the cover when cropping it to the card's 16:9 screen (0 = top, 0.5 = centre).
COVER_FOCUS = {"wipeout": 0.0}
TOOLS = [
    ("FRONTEND", ["typescript", "react", "next-js", "vue-3", "vite", "tailwind-css"]),
    ("BACKEND & DATA", ["node-js", "laravel", "python", "flask", "postgresql", "sqlite"]),
    ("GAMES & DEVELOPMENT TOOLS", ["unity", "c-sharp", "docker", "git", "vercel"]),
]
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
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f(v, 2))
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


def svg_doc(W, H, title, defs, body, rounded=True):
    clip = f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>' if rounded else ""
    open_g, close_g = ('<g clip-path="url(#frame)">', "</g>") if rounded else ("", "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="t">\n<title id="t">{html.escape(title)}</title>\n'
        f"<defs>{clip}{defs}</defs>\n{open_g}\n{body}\n{close_g}\n</svg>\n"
    )


def save(name, svg):
    with open(os.path.join(ASSETS, name), "w") as fh:
        fh.write(svg)
    print(f"  assets/{name:<34} {len(svg.encode()) / 1024:6.0f} KB")


def stars(rng, n, W, top, bottom, still, avoid=(), color="#d6deea", fade=1.0):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(top, bottom)
        r = rng.choice([0.5, 0.7, 0.9, 1.1])
        base = rng.uniform(0.25, 0.85) * fade
        dur, begin = rng.uniform(2.5, 7.0), rng.uniform(0, 6)
        if any(ax0 < x < ax1 and ay0 < y < ay1 for ax0, ay0, ax1, ay1 in avoid):
            continue
        tw = "" if still else (
            f'<animate attributeName="opacity" values="{f(base, 2)};{f(base * 0.2, 2)};{f(base, 2)}" '
            f'dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        )
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{color}" opacity="{f(base, 2)}">{tw}</circle>')
    return "".join(out)


def sea_lines(W, H, hz, still, color="#1d3449", strength=1.0):
    depth = (H - hz) / 86
    out = []
    for i, (dy, amp, wl, dur, op, sw) in enumerate([
        (5, 0.5, 26, 16, 0.30, 0.7), (12, 0.8, 32, 14, 0.34, 0.8), (22, 1.1, 40, 12, 0.38, 0.9),
        (36, 1.6, 52, 10, 0.42, 1.0), (54, 2.2, 66, 8.5, 0.46, 1.1), (77, 3.0, 84, 7, 0.50, 1.3),
    ]):
        y0 = hz + dy * depth
        if y0 > H + 4:
            break
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


def tower(lx, ly, hz, body="#0b1422", lit="#0e1a2b", glass="#1a2433", rock="#050a12"):
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


# ------------------------------------------------------------------ hero
HERO = {
    "hero": dict(
        W=846, H=300, horizon=214, lx=722, ly=108, stars=80, refl=(380, 360),
        name=[("Asil Türkmen", 64, 148, 60, -1.0)],
        sub=[("SOFTWARE ENGINEERING · NORTH CYPRUS", 67, 182, 13, 3.6)],
        beam_l=(900, -36, 100), beam_r=(320, -28, 76),
    ),
    "hero-mobile": dict(
        W=420, H=380, horizon=272, lx=346, ly=166, stars=50, refl=(180, 170),
        name=[("Asil", 24, 126, 60, -1.0), ("Türkmen", 24, 186, 60, -1.0)],
        sub=[("SOFTWARE ENGINEERING", 26, 224, 12, 3.0), ("NORTH CYPRUS", 26, 244, 12, 3.0)],
        beam_l=(460, -118, 150), beam_r=(140, -20, 50),
    ),
}


def hero(L, faces, still):
    rng = random.Random(11)
    W, H, hz, lx, ly = L["W"], L["H"], L["horizon"], L["lx"], L["ly"]
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
  <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07111e"/><stop offset="1" stop-color="#02050a"/></linearGradient>
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
  <mask id="beamMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
    <g transform="translate({lx} {ly})" filter="url(#softer)"><g>{sweep(left)}<polygon points="{beam_l}" fill="url(#beamMaskG)"/></g></g>
  </mask>'''
    body = f'''<rect width="{W}" height="{hz}" fill="url(#sky)"/>
<rect y="{hz}" width="{W}" height="{H - hz}" fill="url(#sea)"/>
{stars(rng, L["stars"], W, 6, hz - 24, still, avoid=[(lx - 42, ly - 28, lx + 48, hz)])}
<rect y="{hz - 1}" width="{W}" height="2" fill="#1a2f48" opacity="0.6"/>
{sea_lines(W, H, hz, still)}
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
    title = "Asil Türkmen. Software engineering, North Cyprus. A lighthouse beam sweeps over the night sea and lights up the name."
    return svg_doc(W, H, title, defs, body)


# ------------------------------------------------------------------ section labels
def label(faces, text):
    """Transparent section label in lamp amber, readable on GitHub's light and dark pages alike
    (a themed <picture> follows the OS scheme, which can disagree with the GitHub theme)."""
    W, H = 420, 40
    tracking = 0.5
    tw = faces[700].width(text, 12.5, tracking)
    defs = '<radialGradient id="g"><stop offset="0" stop-color="#e8b464" stop-opacity="0.55"/><stop offset="1" stop-color="#e8b464" stop-opacity="0"/></radialGradient>'
    body = (
        f'<circle cx="7" cy="20" r="9" fill="url(#g)"/><circle cx="7" cy="20" r="3" fill="#d9a050"/>'
        f'<path d="{faces[700].path(text, 24, 24.5, 12.5, tracking)}" fill="#b98a4c"/>'
        f'<rect x="{f(24 + tw + 16)}" y="19.5" width="{f(W - (24 + tw + 16))}" height="1" fill="#8b97a6" opacity="0.45"/>'
    )
    return svg_doc(W, H, text.title(), defs, body, rounded=False)


# ------------------------------------------------------------------ project cards
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
    im = im.resize((w * 2, h * 2), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def card(project, line, skills, faces, index, mobile, still):
    rng = random.Random(100 + index)
    slug = project["slug"]
    accent = project.get("accent") or "201, 162, 110"
    tint, glow = lighten(accent, 0.45), lighten(accent, 0.1)
    kicker = project["category"].replace(" / ", " · ")
    tech = " · ".join(skills[t]["name"] for t in project["tech"] if t in skills)
    cta = f"asilturkmen.com/projects/{slug}"

    if mobile:
        W = 420
        sx, sy, sw, sh = 16, 16, 388, 218
        tx, tw = 26, 368
        title_size, desc_size = 32, 16
    else:
        W = 846
        sw, sh = 456, 256
        sx = 22 if index % 2 == 0 else W - 22 - sw
        sy = 22
        tx = sx + sw + 38 if index % 2 == 0 else 38
        tw = (W - 30 - tx) if index % 2 == 0 else (sx - 38 - tx)
        title_size, desc_size = 38, 15.5

    desc = faces[500].wrap(line, desc_size, tw)
    tech_lines = faces[500].wrap(tech, 10.5, tw, 0.3)
    # Baselines relative to the kicker's baseline; cap heights are ~0.72em in Satoshi.
    title_y = 16 + 0.74 * title_size
    desc_ys = [title_y + 14 + desc_size * 1.15 + i * desc_size * 1.5 for i in range(len(desc))]
    tech_ys = [desc_ys[-1] + 28 + i * 17 for i in range(len(tech_lines))]
    cta_y = tech_ys[-1] + 32
    top, bottom = -9, cta_y + 5
    if mobile:
        k = sy + sh + 38
        H = round(k + bottom + 22)
    else:
        H = 300
        k = (H - (bottom - top)) / 2 - top

    texts = [
        f'<path d="{faces[700].path(kicker, tx, k, 11, 2.4)}" fill="{tint}"/>',
        f'<path d="{faces[700].path(project["title"], tx - 1, k + title_y, title_size, -0.6)}" fill="{WARM}"/>',
    ]
    texts += [f'<path d="{faces[500].path(t, tx, k + y, desc_size)}" fill="#a6b3c3"/>' for t, y in zip(desc, desc_ys)]
    texts += [f'<path d="{faces[500].path(t, tx, k + y, 10.5, 0.3)}" fill="#6f8199"/>' for t, y in zip(tech_lines, tech_ys)]
    cy = k + cta_y
    ax = tx + faces[500].width(cta, 12.5) + 10
    texts.append(
        f'<path d="{faces[500].path(cta, tx, cy, 12.5)}" fill="{SAND}"/>'
        f'<path d="M{f(ax)},{f(cy - 4.5)} h12 m-4.5,-4.5 l4.5,4.5 l-4.5,4.5" fill="none" stroke="{SAND}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    )

    img = cover_data(project, sw, sh)
    period, sweep_part = 9.0, 1.7
    begin = 1.2 + index * 2.1
    gx0, gx1 = sx - 260, sx + sw + 120
    glint = "" if still else (
        f'<g clip-path="url(#shot)"><g transform="skewX(-22)">'
        f'<rect x="{gx0}" y="{sy - 20}" width="150" height="{sh + 40}" fill="url(#glint)">'
        f'<animate attributeName="x" values="{gx0 + sh * 0.4:.0f};{gx1 + sh * 0.4:.0f};{gx1 + sh * 0.4:.0f}" '
        f'keyTimes="0;{f(sweep_part / period, 3)};1" dur="{period}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        f"</rect></g></g>"
    )
    defs = f'''
  <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060c17"/><stop offset="1" stop-color="#0b1627"/></linearGradient>
  <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff3d6" stop-opacity="0"/><stop offset="0.5" stop-color="#fff3d6" stop-opacity="0.32"/>
    <stop offset="1" stop-color="#fff3d6" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0.55" stop-color="#02050a" stop-opacity="0"/><stop offset="1" stop-color="#02050a" stop-opacity="0.35"/></linearGradient>
  <clipPath id="shot"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8"/></clipPath>
  <filter id="spill" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="16"/></filter>'''
    avoid = [(sx - 10, sy - 10, sx + sw + 10, sy + sh + 10), (tx - 10, 0, tx + tw + 10, H)]
    body = f'''<rect width="{W}" height="{H}" fill="url(#panel)"/>
{stars(rng, 26 if not mobile else 14, W, 6, H - 6, still, avoid=avoid, fade=0.7)}
<rect x="{sx + 10}" y="{sy + 12}" width="{sw - 20}" height="{sh - 8}" rx="10" fill="{glow}" opacity="0.32" filter="url(#spill)"/>
<image href="data:image/jpeg;base64,{img}" x="{sx}" y="{sy}" width="{sw}" height="{sh}" preserveAspectRatio="xMidYMid slice" clip-path="url(#shot)"/>
<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8" fill="url(#shade)"/>
{glint}
<rect x="{sx + 0.5}" y="{sy + 0.5}" width="{sw - 1}" height="{sh - 1}" rx="8" fill="none" stroke="#ffffff" stroke-opacity="0.09"/>
{"".join(texts)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#1a2740"/>'''
    title = f'{project["title"]}. {line} Read the case study on asilturkmen.com.'
    return svg_doc(W, H, title, defs, body)


# ------------------------------------------------------------------ tools
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


def tools(faces, skills, mobile, still):
    rng = random.Random(7)
    icon = 26
    items, groups = [], []
    if mobile:
        W, cols, x0 = 420, 6, 14
        colw = (W - 2 * x0) / cols
        name_size, name_dy, y = 10, 36, 42
        for label_text, slugs in TOOLS:
            groups.append((label_text, 22, y))
            for i, slug in enumerate(slugs):
                items.append((slug, x0 + colw * (i % cols) + colw / 2, y + 34 + 70 * (i // cols)))
            y += 34 + 70 * math.ceil(len(slugs) / cols) + 22
        H = round(y - 18)
    else:
        W, colw, x0 = 846, 92, 196
        name_size, name_dy, y = 10.5, 40, 34
        for label_text, slugs in TOOLS:
            groups.append((label_text, 34, y + 26))
            for i, slug in enumerate(slugs):
                items.append((slug, x0 + colw * i + colw / 2, y + 20))
            y += 92
        H = y + 14

    symbols = "".join(icon_symbol(slug, icon) for slug, _, _ in items)
    symbols += "".join(
        f'<path id="n-{slug}" d="{faces[500].path(skills[slug]["name"], cx, cy + name_dy, name_size, 0.3, "middle")}"/>'
        for slug, cx, cy in items
    )

    def layer(dim):
        out = []
        for slug, cx, cy in items:
            color = "#3a4c68" if dim else (skills[slug].get("heroColor") or "#e9dcc0")
            out.append(f'<use href="#i-{slug}" x="{f(cx - icon / 2)}" y="{f(cy - icon / 2)}" color="{color}"/>')
            out.append(f'<use href="#n-{slug}" fill="{"#6b7c93" if dim else "#f3e7cd"}"/>')
        return "".join(out)

    labels = []
    for text, gx, gy in groups:
        lines = faces[700].wrap(text, 10.5, W - 44 if mobile else x0 - gx - 16, 2.6)
        for i, line in enumerate(lines):
            baseline = gy + (i - (len(lines) - 1) / 2) * 17
            labels.append(f'<path d="{faces[700].path(line, gx, baseline, 10.5, 2.6)}" fill="#7489a3"/>')
    labels = "".join(labels)
    band, period, travel = 260, 6.5, 3.4
    x_from, x_to = W + 40, -band - 40
    move = "" if still else (
        f'<animate attributeName="x" values="{x_from};{x_to};{x_to}" keyTimes="0;{f(travel / period, 3)};1" '
        f'dur="{period}s" begin="0.8s" repeatCount="indefinite"/>'
    )
    lit = layer(False) if still else f'<g mask="url(#sweep)">{layer(False)}</g>'
    beam = "" if still else (
        f'<rect x="{x_from}" y="0" width="{band}" height="{H}" fill="url(#bandWarm)">{move}</rect>'
    )
    defs = f'''{symbols}
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070d19"/><stop offset="0.7" stop-color="#0f1630"/><stop offset="1" stop-color="#1a1b37"/></linearGradient>
  <linearGradient id="band" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#000"/><stop offset="0.5" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
  </linearGradient>
  <linearGradient id="bandWarm" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ffe6b0" stop-opacity="0"/><stop offset="0.5" stop-color="#ffe6b0" stop-opacity="0.07"/>
    <stop offset="1" stop-color="#ffe6b0" stop-opacity="0"/>
  </linearGradient>
  <mask id="sweep" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
    <rect x="{x_from}" y="0" width="{band}" height="{H}" fill="url(#band)">{move}</rect>
  </mask>'''
    body = f'''<rect width="{W}" height="{H}" fill="url(#bg)"/>
{stars(rng, 22, W, 4, H - 4, still, fade=0.45)}
{beam}
{labels}
{layer(True)}
{lit}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#1a2740"/>'''
    names = ", ".join(skills[s]["name"] for _, slugs in TOOLS for s in slugs)
    return svg_doc(W, H, f"Tools I use: {names}.", defs, body)


# ------------------------------------------------------------------ dawn
DAWN = {
    "dawn": dict(W=846, H=340, horizon=262, lx=724, sun=423,
                 kicker=94, domain=152, domain_size=54, sub=188, birds=[(150, 0), (130, -14), (176, -27)]),
    "dawn-mobile": dict(W=420, H=420, horizon=322, lx=356, sun=190,
                        kicker=104, domain=154, domain_size=40, sub=188, birds=[(214, 0), (196, -16)]),
}


def dawn(L, faces, still):
    rng = random.Random(23)
    W, H, hz, lx = L["W"], L["H"], L["horizon"], L["lx"]
    ly = hz - 106
    cx = W / 2
    sun_r = 30 if W > 500 else 24

    kicker, sub = "MORE ABOUT MY WORK", "PROJECTS · CASE STUDIES · CV"
    domain = "asilturkmen.com"
    ds = L["domain_size"]
    dw = faces[700].width(domain, ds, -0.8)
    arrow_w = ds * 0.42
    dx = cx - (dw + 14 + arrow_w) / 2
    ay = L["domain"] - ds * 0.34
    domain_d = faces[700].path(domain, dx, L["domain"], ds, -0.8)
    ax = dx + dw + 14
    arrow = (
        f'<path d="M{f(ax)},{f(ay)} h{f(arrow_w)} m-{f(arrow_w * 0.4)},-{f(arrow_w * 0.4)} '
        f'l{f(arrow_w * 0.4)},{f(arrow_w * 0.4)} l-{f(arrow_w * 0.4)},{f(arrow_w * 0.4)}" fill="none" '
        f'stroke="#fff4e6" stroke-width="{f(ds * 0.075)}" stroke-linecap="round" stroke-linejoin="round"/>'
    )

    shimmer = []
    for i in range(9):
        yy = hz + 5 + i * (7 + i * 0.9)
        if yy > H - 4:
            break
        rxs = 14 + i * 9 + rng.uniform(-4, 4)
        base = rng.uniform(0.35, 0.7) * (1 - i * 0.07)
        anim = "" if still else (
            f'<animate attributeName="opacity" values="{f(base, 2)};{f(base * 0.3, 2)};{f(base, 2)}" '
            f'dur="{f(rng.uniform(1.6, 3.4))}s" begin="{f(rng.uniform(0, 2))}s" repeatCount="indefinite"/>'
            f'<animate attributeName="rx" values="{f(rxs)};{f(rxs * 1.18)};{f(rxs)}" '
            f'dur="{f(rng.uniform(2.5, 4.5))}s" repeatCount="indefinite"/>'
        )
        shimmer.append(
            f'<ellipse cx="{f(L["sun"] + rng.uniform(-6, 6))}" cy="{f(yy)}" rx="{f(rxs)}" ry="1.3" '
            f'fill="#ffd29a" opacity="{f(base, 2)}">{anim}</ellipse>'
        )

    birds = []
    for i, (by, off) in enumerate(L["birds"]):
        up = "M-7,0 Q-3.5,-4.5 0,0 Q3.5,-4.5 7,0"
        down = "M-7,-1.5 Q-3.5,2.5 0,0 Q3.5,2.5 7,-1.5"
        flap = "" if still else f'<animate attributeName="d" values="{up};{down};{up}" dur="{f(0.8 + i * 0.13, 2)}s" repeatCount="indefinite"/>'
        fly = "" if still else (
            f'<animateTransform attributeName="transform" type="translate" values="-30 {by};{W + 30} {by - 18}" '
            f'dur="46s" begin="{off}s" repeatCount="indefinite"/>'
        )
        start_x = W * (0.22 + 0.08 * i)
        birds.append(
            f'<g transform="translate({f(start_x)} {by})">{fly}<path d="{up}" fill="none" stroke="#2a2036" '
            f'stroke-width="1.4" stroke-linecap="round">{flap}</path></g>'
        )

    sun_anim = "" if still else (
        f'<animate attributeName="r" values="{sun_r * 4.2};{sun_r * 4.8};{sun_r * 4.2}" dur="7s" repeatCount="indefinite"/>'
    )
    defs = f'''
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a1430"/><stop offset="0.36" stop-color="#22284d"/><stop offset="0.62" stop-color="#553f68"/>
    <stop offset="0.82" stop-color="#b06d69"/><stop offset="0.93" stop-color="#e29769"/><stop offset="1" stop-color="#f5c38c"/>
  </linearGradient>
  <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2f4e"/><stop offset="0.35" stop-color="#1c1b31"/><stop offset="1" stop-color="#0b0c19"/></linearGradient>
  <radialGradient id="sunglow"><stop offset="0" stop-color="#ffcf8f" stop-opacity="0.75"/><stop offset="0.4" stop-color="#ff9f6a" stop-opacity="0.25"/><stop offset="1" stop-color="#ff9f6a" stop-opacity="0"/></radialGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#fff3d8"/><stop offset="1" stop-color="#ffd59c"/></radialGradient>
  <clipPath id="above"><rect width="{W}" height="{hz}"/></clipPath>
  <filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur1" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="0.6"/></filter>'''
    body = f'''<rect width="{W}" height="{hz}" fill="url(#sky)"/>
{stars(rng, 26, W, 4, hz * 0.36, still, fade=0.6)}
<g clip-path="url(#above)">
  <circle cx="{L["sun"]}" cy="{hz + 4}" r="{sun_r * 4.2}" fill="url(#sunglow)">{sun_anim}</circle>
  <circle cx="{L["sun"]}" cy="{hz + 8}" r="{sun_r}" fill="url(#sun)"/>
</g>
<rect y="{hz}" width="{W}" height="{H - hz}" fill="url(#sea)"/>
<rect y="{hz - 0.5}" width="{W}" height="1.5" fill="#ffd9a6" opacity="0.45"/>
{sea_lines(W, H, hz, still, color="#8a6a86", strength=0.6)}
<g filter="url(#blur1)">{"".join(shimmer)}</g>
{"".join(birds)}
{tower(lx, ly, hz, body="#120f1f", lit="#1b1629", glass="#211b30", rock="#0c0a16")}
<path d="{faces[700].path(kicker, cx, L["kicker"], 11.5, 3.8, "middle")}" fill="#f2d7b6" opacity="0.85"/>
<path d="{domain_d}" fill="#ffcf9a" opacity="0.35" filter="url(#soft)"/>
<path d="{domain_d}" fill="#fff4e6"/>
{arrow}
<path d="{faces[500].path(sub, cx, L["sub"], 10.5, 3.4, "middle")}" fill="#ecc9a8" opacity="0.8"/>'''
    return svg_doc(W, H, "Dawn over the sea. More about my work at asilturkmen.com: projects, case studies and CV.", defs, body)


# ------------------------------------------------------------------ README
def picture(base, alt, href):
    return f'''<p><a href="{href}"><picture>
  <source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="assets/{base}-mobile-still.svg">
  <source media="(max-width: 600px)" srcset="assets/{base}-mobile.svg">
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/{base}-still.svg">
  <img src="assets/{base}.svg" width="100%" alt="{html.escape(alt)}">
</picture></a></p>'''


def section_label(base, alt):
    return f'<p><img src="assets/{base}.svg" width="420" alt="{html.escape(alt)}"></p>'


def readme(projects):
    parts = [
        picture("hero", "Asil Türkmen. Software engineering, North Cyprus. A lighthouse beam sweeps over the night sea and lights up the name.", SITE),
        "",
        "I'm **Asil Türkmen**, a Software Engineering student at Eastern Mediterranean University in North Cyprus. "
        "I work on web apps, APIs, automation and games. "
        "You can find more about my projects and my CV at "
        f"**[asilturkmen.com]({SITE})**.",
        "",
        section_label("label-work", "Selected work"),
        "",
    ]
    for project, line in projects:
        slug = project["slug"]
        extra = []
        if project.get("liveUrl"):
            host = re.sub(r"^https?://(www\.)?", "", project["liveUrl"]).rstrip("/")
            extra.append(f'<a href="{project["liveUrl"]}">{html.escape(host)}</a>')
        if project.get("repoUrl"):
            extra.append(f'<a href="{project["repoUrl"]}">Source</a>')
        meta = " · ".join([f'<a href="{SITE}/projects/{slug}"><b>Case study</b></a>'] + extra)
        parts += [
            picture(f"work-{slug}", f'{project["title"]}. {line} Read the case study on asilturkmen.com.', f"{SITE}/projects/{slug}")[:-4]
            + f"<br>\n<sub>{meta}</sub></p>",
            "",
        ]
    parts += [
        section_label("label-tools", "Tools I use"),
        "",
        picture("tools", "Tools I use: " + ", ".join(n for n in TOOL_NAMES), SITE),
        "",
        picture("dawn", "Dawn over the sea. More about my work at asilturkmen.com: projects, case studies and CV.", SITE),
        "",
        '<p align="center">' + " · ".join(f'<a href="{u}">{n}</a>' for n, u in LINKS) + "</p>",
        "",
    ]
    with open(os.path.join(ROOT, "README.md"), "w") as fh:
        fh.write("\n".join(parts))
    print("  README.md")


TOOL_NAMES = []


def main():
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(SITE_DIR, "content", "site.json")) as fh:
        site = json.load(fh)
    skills = {s["slug"]: s for s in site["skills"]}
    TOOL_NAMES.extend(skills[s]["name"] for _, slugs in TOOLS for s in slugs)
    projects = []
    for slug, line in PROJECTS:
        with open(os.path.join(SITE_DIR, "content", "projects", f"{slug}.json")) as fh:
            projects.append((json.load(fh), line))

    faces = {w: Face(w) for w in FONTS}
    for still in (False, True):
        tag = "-still" if still else ""
        for name, layout in HERO.items():
            save(f"{name}{tag}.svg", hero(layout, faces, still))
        for i, (project, line) in enumerate(projects):
            for mobile in (False, True):
                save(f"work-{project['slug']}{'-mobile' if mobile else ''}{tag}.svg",
                     card(project, line, skills, faces, i, mobile, still))
        for mobile in (False, True):
            save(f"tools{'-mobile' if mobile else ''}{tag}.svg", tools(faces, skills, mobile, still))
        for name, layout in DAWN.items():
            save(f"{name}{tag}.svg", dawn(layout, faces, still))
    for base, text in (("label-work", "Selected work"), ("label-tools", "Tools I use")):
        save(f"{base}.svg", label(faces, text))
    readme(projects)


if __name__ == "__main__":
    main()
