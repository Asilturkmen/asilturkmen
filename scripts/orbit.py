"""The orbit: the tools I use circling the asilturkmen.com lockup, in fake 3D.

    ORBIT                                        content height and padding of the plate row
    orbit(theme, mobile, still, faces, plate) -> str
        one window of the plate (build.Plate) for THEMES[theme]. The footer's
        text lockup (kicker, domain with a gold arrow, sub line) sits centred;
        the TOOLS icons ride an elliptical ring around it. The ring's back arc
        passes above the kicker, where the icons are small, pale and silver,
        its front arc passes below the sub line, where they are large, bright
        and in their brand colours, so the ring frames the text and never
        crosses it. The icon at the front shows its name under it; the front
        moves right to left and each icon holds the front for HOLD seconds.

SMIL only, like the watch. The ring is one <path id="orbit-path"> in the defs;
every icon is one <g> that rides it with an animateMotion (an <mpath> to the
shared path, keyPoints so the icon moves at a constant angle, not at a constant
speed along the path), carrying an animateTransform scale for depth, an opacity
animation and a fill animation (silver at the back to the brand colour at the
front). The depth lists are the same for every icon; only the begin offset
differs from icon to icon. The <mpath> carries both href (SVG 2: Chromium,
Firefox 51+, Safari 12.1+) and xlink:href (older WebKit), so the moving variants
declare the xlink namespace on their root. still=True draws the ring stopped,
TypeScript at the front with its name.

check() runs at build time: at every half degree of the orbit no icon's outline
(nor its name while it is visible) may come near the text lockup, touch its
neighbour on the ring, or leave the plate's margins. The build fails if it does.
"""
from __future__ import annotations

import bisect
import math

from tools import TOOLS, icon, icon_bounds, icon_fill, tint

__all__ = ["orbit", "ORBIT"]

# (content height, padding above and below it) of the plate row; build.Plate
# makes the row H + 2 * pad tall and draws the content pad units down
ORBIT = {"desktop": (260, 14), "mobile": (220, 10)}

HOLD = 2.5                        # seconds each icon owns the front
PERIOD = HOLD * len(TOOLS)        # one orbit: 42.5 s
STEP = 360 / len(TOOLS)           # angular spacing of the icons, 21.2 deg
# the depth lists (scale, opacity, fill) hold SAMPLES + 1 values per orbit, 15 deg apart:
# they are cosine-shaped, so linear steps this short are invisible
SAMPLES = 24
# the motion path's keyPoints: MOTION_SAMPLES + 1 per orbit, 6.4 deg apart. Between two
# key points the icon moves at a constant speed along the path rather than at a
# constant angle; _motion() measures how far that lets it stray (about 0.4 px on
# desktop, a quarter of that on mobile), which the geometry check's slack must absorb
MOTION_SAMPLES = 56
# the name under the front icon: solid within LABEL_FULL deg of the front (about
# 1.5 s), gone by LABEL_OFF (0.35 s fades), so there is a short dark beat
# between names: a crisp tick. LABEL_OFF stays under half the icon spacing, so
# two names are never lit at once however many tools there are.
LABEL_FULL, LABEL_OFF = 6.5, 9.5
assert LABEL_OFF < STEP / 2, f"orbit: LABEL_OFF {LABEL_OFF} deg would light two names at once (icons are {STEP:.1f} deg apart)"
DIM = 0.65                        # opacity at the back of the ring (1 at the front)
TINT_POWER = 1.0                  # colour fades to silver towards the back: k = ((1 + cos) / 2) ** TINT_POWER
PAD_TEXT = 6                      # clearance the icons keep from the lockup
MARGIN_X, MARGIN_Y = 24, 14       # ... and from the plate's sides / the row's bounds
CHECK_STEP = 0.5                  # degrees between the geometry check's samples


def _geom(mobile: bool) -> dict:
    """Layout for one breakpoint, in the row's content coordinates.

    cx, cy: ring centre; rx, ry: ellipse radii; base: icon size at the front;
    s_min: icon scale at the back; yk, yd, ys: baselines of kicker, domain and
    sub line relative to cy; gap: domain to arrow; lead: the name's baseline
    below the icon's lower edge (in the icon's own, unscaled units)."""
    if mobile:
        return dict(W=360, H=ORBIT["mobile"][0], cx=180, cy=102, rx=146, ry=65, base=18, s_min=0.72,
                    kick=(10, 0.22), dom=26, arrow=22, sub=13, label=12,
                    yk=-30, yd=4, ys=27, gap=8, lead=13)
    return dict(W=846, H=ORBIT["desktop"][0], cx=423, cy=122, rx=345, ry=76, base=28, s_min=0.72,
                kick=(10, 0.24), dom=38, arrow=30, sub=13, label=12,
                yk=-40, yd=8, ys=34, gap=12, lead=17)


# ----------------------------------------------------------------- the ring
# theta is the position on the ring: 0 at the front (bottom, nearest the viewer),
# 180 at the back (top). Motion: theta falls with time, so the front moves right to left.
def _pos(g: dict, deg: float) -> tuple[float, float]:
    th = math.radians(deg)
    return g["rx"] * math.sin(th), g["ry"] * math.cos(th)


def _near(deg: float) -> float:
    """How near the front theta is: 1 at the front, 0 at the back."""
    return (1 + math.cos(math.radians(deg))) / 2


def _depth(g: dict, deg: float) -> tuple[float, float]:
    """(scale, opacity) at theta: 1, 1 at the front; s_min, DIM at the back."""
    k = _near(deg)
    return g["s_min"] + (1 - g["s_min"]) * k, DIM + (1 - DIM) * k


def _colour(silver: str, brand: str, deg: float) -> str:
    """The icon's fill at theta: its brand colour at the front, silver at the
    back, half way to colour at the sides."""
    return tint(silver, brand, _near(deg) ** TINT_POWER)


def _label_opacity(deg: float) -> float:
    a = abs((deg + 180) % 360 - 180)            # angular distance from the front, 0..180
    if a <= LABEL_FULL:
        return 1.0
    if a >= LABEL_OFF:
        return 0.0
    return (LABEL_OFF - a) / (LABEL_OFF - LABEL_FULL)


def _theta_at_rest(i: int) -> float:
    """Where icon i sits at t = 0 (and in the still image): TypeScript at the
    front, the list continuing to the right, so the next name comes in from the right."""
    return i * STEP


def _begin(i: int) -> float:
    """Negative begin offset that puts icon i at _theta_at_rest(i) when the page loads."""
    n = len(TOOLS)
    return -((n - i) % n) * HOLD


def _ring_table(g: dict, steps: int = 7200) -> list[float]:
    """The fraction of the ring path's length covered after every 1 / steps of an orbit
    at a constant angle, from the front. (Equal angles cover less of the path near the
    sides, where the ellipse is tight, than across the front and back.) Simpson's rule."""
    rx, ry = g["rx"], g["ry"]
    h = 2 * math.pi / steps

    def speed(th: float) -> float:
        return math.hypot(rx * math.cos(th), ry * math.sin(th))

    out = [0.0]
    for k in range(steps):
        a = k * h
        out.append(out[-1] + h / 6 * (speed(a) + 4 * speed(a + h / 2) + speed(a + h)))
    return [v / out[-1] for v in out]


def _ring_fraction(table: list[float], turn: float) -> float:
    """Path fraction after `turn` (0..1) of an orbit, read off the table."""
    x = turn * (len(table) - 1)
    i = min(int(x), len(table) - 2)
    return table[i] + (table[i + 1] - table[i]) * (x - i)


def _ring_turn(table: list[float], frac: float) -> float:
    """The inverse: how much of an orbit (0..1) puts an icon at path fraction `frac`."""
    i = min(max(bisect.bisect_right(table, frac) - 1, 0), len(table) - 2)
    return (i + (frac - table[i]) / (table[i + 1] - table[i])) / (len(table) - 1)


def _motion(g: dict) -> tuple[str, str, float]:
    """keyTimes and keyPoints for the ring's animateMotion, as written (4 decimals), and
    the slip: the most (px) that motion strays from the constant-angle position the
    geometry check assumes, since between two key points animateMotion moves at a
    constant speed along the path. Measured on the rounded values that are emitted."""
    from build import num

    n, table = MOTION_SAMPLES, _ring_table(g)
    times = [num(k / n, 4) for k in range(n + 1)]
    points = [num(_ring_fraction(table, float(t)), 4) for t in times]
    kt, kp = [float(v) for v in times], [float(v) for v in points]
    fine, worst = 20, 0.0
    for k in range(n):
        for j in range(1, fine):
            u = j / fine
            meant = _pos(g, 360 * (kt[k] + (kt[k + 1] - kt[k]) * u))                   # where it should be
            there = _pos(g, 360 * _ring_turn(table, kp[k] + (kp[k + 1] - kp[k]) * u))  # where it is
            worst = max(worst, math.dist(there, meant))
    return ";".join(times), ";".join(points), worst


# ----------------------------------------------------------------- geometry check
def _gap(a, b) -> float:
    """Clearance between two boxes along the axis that separates them (0 when they touch
    or overlap): the same measure as testing a against b grown by that amount."""
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return max(dx, dy)


def _place(g: dict, deg: float, box) -> tuple[float, float, float, float]:
    """A box given in an icon's own coordinates (centre 0,0, front size), placed and
    scaled where the icon is at theta, in content coordinates."""
    dx, dy = _pos(g, deg)
    s, _ = _depth(g, deg)
    x, y = g["cx"] + dx, g["cy"] + dy
    return x + box[0] * s, y + box[1] * s, x + box[2] * s, y + box[3] * s


def _boxes_at(g: dict, deg: float, glyph, label) -> list[tuple[float, float, float, float]]:
    """What one icon covers at theta: its outline's box and, while its name is lit,
    the name's box."""
    out = [_place(g, deg, glyph)]
    if _label_opacity(deg) > 0:
        out.append(_place(g, deg, label))
    return out


def check(g: dict, pad: float, text_boxes: dict, glyphs, labels) -> dict:
    """Fail loudly if, at any CHECK_STEP of the orbit, any icon's outline (or its lit
    name) comes within PAD_TEXT of the text lockup, touches the next icon on the ring,
    or leaves the margins: MARGIN_X from the plate's sides, MARGIN_Y from the row's
    bounds (the content sits `pad` units below the row's top). glyphs[i] and labels[i]
    are icon i's outline and name boxes in its own coordinates. Returns the smallest
    clearances found: margin, one per text box, neighbour."""
    W, H, n = g["W"], g["H"], len(glyphs)
    x0, x1 = MARGIN_X, W - MARGIN_X
    y0, y1 = MARGIN_Y - pad, H + pad - MARGIN_Y
    slack = {"margin": math.inf, **{k: math.inf for k in text_boxes}, "neighbour": math.inf}
    for k in range(int(round(360 / CHECK_STEP))):
        deg = k * CHECK_STEP
        for i in range(n):
            boxes = _boxes_at(g, deg, glyphs[i], labels[i])
            j = (i + 1) % n                       # icon j rides STEP degrees ahead of icon i
            nboxes = _boxes_at(g, deg + STEP, glyphs[j], labels[j])
            for b in boxes:
                bx = tuple(round(v, 1) for v in b)
                m = min(b[0] - x0, x1 - b[2], b[1] - y0, y1 - b[3])
                assert m >= 0, (f"orbit: {TOOLS[i][1]} leaves the row at {deg} deg: box {bx}, "
                                f"allowed x {x0}..{x1}, y {y0}..{y1}")
                slack["margin"] = min(slack["margin"], m)
                for name, tb in text_boxes.items():
                    d = _gap(b, tb)
                    assert d >= PAD_TEXT, (f"orbit: {TOOLS[i][1]} runs into the {name} at {deg} deg: box {bx}, "
                                           f"{name} {tuple(round(v, 1) for v in tb)}, clearance {d:.2f} < {PAD_TEXT}")
                    slack[name] = min(slack[name], d)
                for nb in nboxes:
                    d = _gap(b, nb)
                    assert d > 0, (f"orbit: {TOOLS[i][1]} and {TOOLS[j][1]} touch at {deg} deg: "
                                   f"{bx} and {tuple(round(v, 1) for v in nb)}")
                    slack["neighbour"] = min(slack["neighbour"], d)
    return slack


# ----------------------------------------------------------------- drawing
def orbit(theme: str, mobile: bool, still: bool, faces: dict, plate) -> str:
    # build.py imports this module, so its helpers are imported at call time
    from build import THEMES, FOOT_KICKER, FOOT_DOMAIN, FOOT_SUB, intro, num, plate_svg

    t = THEMES[theme]
    g = _geom(mobile)
    W, H, cx, cy = g["W"], g["H"], g["cx"], g["cy"]
    pad = ORBIT["mobile" if mobile else "desktop"][1]
    assert plate.h["orbit"] == H + 2 * pad and plate.pad["orbit"] == pad, "orbit: the plate's orbit row does not match ORBIT"
    ink, ink2, gold, muted = t["ink"], t["ink2"], t["accent"], t["muted"]
    title = ("Tools I use — " + ", ".join(name for _, name, _, _ in TOOLS[:-1]) + f" and {TOOLS[-1][1]} — "
             "orbiting asilturkmen.com: projects, case studies and CV.")
    parts = []

    # the lockup, centred (the footer's, without its hairlines)
    ks, kt = g["kick"]
    kick = faces[700].layout(FOOT_KICKER, ks, tracking=kt)
    dom = faces[700].layout(FOOT_DOMAIN, g["dom"], tracking=-0.01)
    arrow = faces[500].layout("→", g["arrow"])
    sub = faces[500].layout(FOOT_SUB, g["sub"])
    yk, yd, ys = cy + g["yk"], cy + g["yd"], cy + g["ys"]
    xk, xs = cx - kick.width / 2, cx - sub.width / 2
    xd = cx - (dom.width + g["gap"] + arrow.width) / 2
    xa, ya = xd + dom.width + g["gap"], yd - (dom.size - arrow.size) * 0.18
    text = [kick.path(xk, yk, gold, nd=2), dom.path(xd, yd, ink), arrow.path(xa, ya, gold), sub.path(xs, ys, muted)]
    db, ab = dom.bbox(xd, yd), arrow.bbox(xa, ya)
    text_boxes = dict(kicker=kick.bbox(xk, yk), domain=(min(db[0], ab[0]), min(db[1], ab[1]), max(db[2], ab[2]), max(db[3], ab[3])),
                      sub=sub.bbox(xs, ys))

    # the names, each centred under its icon in the icon's own units (scaled with it)
    lead = g["base"] / 2 + g["lead"]
    runs = [faces[500].layout(name, g["label"]) for _, name, _, _ in TOOLS]
    labels = [run.bbox(-run.width / 2, lead) for run in runs]
    glyphs = [icon_bounds(si, g["base"]) for _, _, si, _ in TOOLS]
    slack = check(g, pad, text_boxes, glyphs, labels)
    # the check follows the ideal constant-angle motion; the real motion may stray by
    # the slip, which the margins, the text clearance and the gaps between neighbours
    # (where both icons stray) must absorb
    key_times, key_points, slip = _motion(g)
    text_slack = min(slack[k] for k in text_boxes)
    assert slack["margin"] > slip and slack["neighbour"] > 2 * slip and text_slack - slip >= PAD_TEXT, (
        f"orbit: the motion path lets an icon stray {slip:.2f} px: smallest margin {slack['margin']:.2f}, "
        f"neighbour gap {slack['neighbour']:.2f} (needs > {2 * slip:.2f}), text clearance {text_slack:.2f} "
        f"(needs >= {PAD_TEXT + slip:.2f}); raise MOTION_SAMPLES or give the ring more room")

    # the track: a faint dotted gold ellipse like the watch's, its front half a little
    # stronger than the back half (a sweep flag of 0 runs the arc through the bottom)
    rx, ry = g["rx"], g["ry"]
    dots = f'fill="none" stroke="{gold}" stroke-width="0.8" stroke-dasharray="2 5"'
    track = [f'<path d="M{cx - rx} {cy}A{rx} {ry} 0 0 1 {cx + rx} {cy}" {dots} stroke-opacity="0.1"/>',
             f'<path d="M{cx - rx} {cy}A{rx} {ry} 0 0 0 {cx + rx} {cy}" {dots} stroke-opacity="0.26"/>']
    # the ring the icons ride, centred on the origin (the icons sit in a group moved to
    # cx, cy): from the front round through the left, the way theta falls (sweep 1 is
    # clockwise on screen), in four quarter arcs
    path = (f'<path id="orbit-path" d="M0 {ry}A{rx} {ry} 0 0 1 {-rx} 0A{rx} {ry} 0 0 1 0 {-ry}'
            f'A{rx} {ry} 0 0 1 {rx} 0A{rx} {ry} 0 0 1 0 {ry}"/>')

    # the icons, painted back to front
    brands = {slug: icon_fill(hex_, theme, t) for slug, _, _, hex_ in TOOLS}
    # one orbit as SAMPLES linear steps, theta falling from 0 (the last value repeats the first)
    degs = [-k * 360 / SAMPLES for k in range(SAMPLES + 1)]
    scale = ";".join(num(_depth(g, d)[0], 2) for d in degs)
    fade = ";".join(num(_depth(g, d)[1], 2) for d in degs)
    # the name: lit only around the front, so a short piecewise-linear list with keyTimes
    f, o = LABEL_FULL / 360, LABEL_OFF / 360
    lit_vals = "1;1;0;0;1;1"
    lit_keys = f' keyTimes="0;{num(f, 4)};{num(o, 4)};{num(1 - o, 4)};{num(1 - f, 4)};1"'
    dur = f'dur="{num(PERIOD, 2)}s"'

    def at(begin: float) -> str:
        return f' begin="{num(begin, 2)}s"' if begin else ""

    def anim(tag: str, attr: str, values: str, begin: float, extra: str = "") -> str:
        # calcMode is linear by default for animate and animateTransform
        return f'<{tag} attributeName="{attr}"{extra} values="{values}" {dur}{at(begin)} repeatCount="indefinite"/>'

    def ride(begin: float) -> str:
        # animateMotion defaults to paced (constant speed along the path): keyPoints make it constant-angle
        return (f'<animateMotion {dur}{at(begin)} repeatCount="indefinite" calcMode="linear" '
                f'keyPoints="{key_points}" keyTimes="{key_times}"><mpath href="#orbit-path" xlink:href="#orbit-path"/>'
                '</animateMotion>')

    icons = []
    order = sorted(range(len(TOOLS)), key=lambda i: math.cos(math.radians(_theta_at_rest(i))))
    for i in order:
        slug, name, si, _ = TOOLS[i]
        th = _theta_at_rest(i)
        rest_fill = _colour(ink2, brands[slug], th)
        label = runs[i].path(-runs[i].width / 2, lead, muted, nd=2)
        if still:
            dx, dy = _pos(g, th)
            s, op = _depth(g, th)
            lo = _label_opacity(th)
            body = icon(si, 0, 0, g["base"], rest_fill)
            if op < 1:
                body = f'<g opacity="{num(op, 2)}">{body}</g>'
            if lo > 0:
                body += f'<g opacity="{num(lo, 2)}">{label}</g>' if lo < 1 else label
            icons.append(f'<g transform="translate({num(cx + dx)} {num(cy + dy)}) scale({num(s, 2)})">{body}</g>')
        else:
            b = _begin(i)
            colours = ";".join(_colour(ink2, brands[slug], d) for d in degs)
            glyph = icon(si, 0, 0, g["base"], rest_fill, anim("animate", "fill", colours, b))
            # the name's static opacity is its resting one, so a renderer without SMIL
            # shows the one name at the front, not seventeen
            lit = "" if _label_opacity(th) > 0 else ' opacity="0"'
            # the motion rides on the outer group and the scale on the inner one: a scale
            # on the moving element would scale its motion too
            icons.append(f'<g>{ride(b)}<g>{anim("animateTransform", "transform", scale, b, ' type="scale"')}'
                         f'<g>{anim("animate", "opacity", fade, b)}{glyph}</g>'
                         f'<g{lit}>{anim("animate", "opacity", lit_vals, b, lit_keys)}{label}</g></g></g>')
    if still:
        parts += track + icons
        defs = ""
    else:   # the ring fades in once; the lockup is there from the start, like the footer was
        parts.append(f'<g>{intro("animate", "opacity", "0", "1", 0.0, 0.8)}{chr(10).join(track)}\n'
                     f'<g transform="translate({cx} {cy})">\n{chr(10).join(icons)}\n</g></g>')
        defs = path
    parts += text
    svg = plate_svg(plate, t, 0, W, "orbit", chr(10).join(parts), title, defs=defs)
    if not still:   # the mpath's xlink:href fallback needs the namespace declared on the root
        root = '<svg xmlns="http://www.w3.org/2000/svg" '
        assert svg.startswith(root) and svg.count(root) == 1 and "xlink" not in svg.split(">", 1)[0], "orbit: unexpected root element"
        svg = svg.replace(root, root + 'xmlns:xlink="http://www.w3.org/1999/xlink" ', 1)
    return svg
