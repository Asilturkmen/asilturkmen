"""A skeleton (open-worked) watch movement drawn as animated SVG.

    movement_defs(theme) -> str
        gradients for the page's <defs>; every id starts with "mv-".
    movement(cx, cy, r, theme, still, label_svg="") -> str
        one <g> with the whole watch centred at (cx, cy), outer radius r.

SMIL only (no script, no CSS animation, no external references), so it keeps
moving inside an <img> on github.com. Output is deterministic.

The train is laid out like a real calibre: every wheel drives the *pinion* of
the next one, so pitch circles touch, neighbours turn in opposite directions
and the tooth ratios are the speed ratios (period in s, + = clockwise):

    barrel   36 T              -240   (its mesh with the centre pinion is under the hub)
    centre   75 T              +3600  minute hand; sits below the plate
    third    56 T, 10 leaves   -480   = 3600 * 10 / 75
    fourth   40 T,  7 leaves   +60    = 480 * 7 / 56   (the seconds wheel)
    escape   15 T,  8 leaves   -12    = 60 * 8 / 40, in 30 steps of 12 deg:
                                        half a tooth per beat, like the real thing
    balance  +-25 deg every 0.8 s (2 beats, 9000 vph); pallet fork and
             hairspring move in step with it.

Ten animated elements: barrel, centre, third, fourth, escape, pallet, balance,
hairspring, minute hand, seconds hand.
"""
from __future__ import annotations

import math

__all__ = ["movement", "movement_defs", "gear", "LABEL_ANCHOR"]

# Where the caller's two-line label fits, in r-units from the centre: centre x,
# first baseline y, font size, baseline-to-baseline distance in font sizes, and
# the widest half-line that stays on solid plate (clear of the cut-outs).
LABEL_ANCHOR = dict(x=0.0, y=0.385, size=0.078, leading=1.3, half_width=0.27)

BALANCE_AMP = 25.0      # deg
BALANCE_PERIOD = 0.8    # s, there and back (two beats)
ESC_TEETH = 15
ESC_STEPS = 2 * ESC_TEETH            # half a tooth per beat
ESC_PERIOD = ESC_STEPS * BALANCE_PERIOD / 2
STILL = dict(minute=60.0, second=300.0, balance=14.0)


# ----------------------------------------------------------------- numbers
def _f(v: float, nd: int = 1) -> str:
    s = f"{v:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        return "0"
    if s.startswith("0."):
        return s[1:]
    if s.startswith("-0."):
        return "-" + s[2:]
    return s


def _cat(nums: list[str]) -> str:
    """Join path numbers with the fewest separators the SVG grammar allows."""
    out = nums[0]
    for prev, s in zip(nums, nums[1:]):
        out += s if s[0] == "-" or (s[0] == "." and "." in prev) else " " + s
    return out


def _p(x: float, y: float, nd: int = 1) -> str:
    return _cat([_f(x, nd), _f(y, nd)])


def _rel(cmds, nd: int = 1) -> str:
    """Emit [(letter, [points...]), ...] given in absolute coordinates as
    relative commands. Points are rounded before differencing, so long outlines
    close without drift."""
    q = 10 ** nd
    cur = (0, 0)
    out = []
    for i, (cmd, pts) in enumerate(cmds):
        ip = [(round(x * q), round(y * q)) for x, y in pts]
        if cmd == "M" and i == 0:
            out.append("M" + _cat([_f(ip[0][0] / q, nd), _f(ip[0][1] / q, nd)]))
        else:
            nums = []
            for x, y in ip:
                nums += [_f((x - cur[0]) / q, nd), _f((y - cur[1]) / q, nd)]
            out.append(cmd.lower() + _cat(nums))
        cur = ip[-1]
    return "".join(out)


def _pol(rho: float, deg: float) -> tuple[float, float]:
    """Clock angle: 0 = 12 o'clock, growing clockwise (SVG y points down)."""
    a = math.radians(deg)
    return rho * math.sin(a), -rho * math.cos(a)


def _ang(x: float, y: float) -> float:
    return math.degrees(math.atan2(x, -y)) % 360


def _rgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _mix(a: str, b: str, t: float) -> str:
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ra, rb))


def _lum(c: str) -> float:
    r, g, b = (v / 255 for v in _rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# ----------------------------------------------------------------- palette
def _pal(t: dict) -> dict:
    dark = _lum(t["dial"]) < 0.5
    acc = t["accent"]
    if dark:
        gold_hi, gold_lo = _mix(acc, "#fff4dc", 0.42), _mix(acc, "#3a2a10", 0.22)
        bevel_hi, bevel_lo = _mix(acc, "#ffffff", 0.62), _mix(acc, "#000000", 0.62)
        void = _mix(t["dial"], "#000000", 0.62)
        plate_edge = _mix(t["dial"], t["ink"], 0.075)
        steel_hi, steel_lo = t["hand"], _mix(t["ink2"], t["dial"], 0.35)
        sunk = _mix(acc, t["dial"], 0.55)          # wheels one level down
    else:
        gold_hi, gold_lo = _mix(acc, "#e9cf98", 0.55), _mix(acc, "#2a1d08", 0.18)
        bevel_hi, bevel_lo = _mix(acc, "#fff8e8", 0.72), _mix(acc, "#000000", 0.45)
        void = _mix(t["dial"], t["accent_dim"], 0.62)
        plate_edge = _mix(t["dial"], t["accent_dim"], 0.16)
        steel_hi, steel_lo = _mix(t["ink2"], "#ffffff", 0.6), t["ink2"]
        sunk = _mix(acc, t["dial"], 0.42)
    return dict(dark=dark, acc=acc, gold_hi=gold_hi, gold_lo=gold_lo, bevel_hi=bevel_hi,
                bevel_lo=bevel_lo, void=void, plate=t["dial"], plate_edge=plate_edge,
                steel_hi=steel_hi, steel_lo=steel_lo, sunk=sunk, ruby="#a8323c", ruby_hi="#ff9aa2")


def movement_defs(theme: dict) -> str:
    c = _pal(theme)
    return (
        f'<linearGradient id="mv-gold" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["gold_hi"]}"/><stop offset="1" stop-color="{c["gold_lo"]}"/></linearGradient>'
        f'<radialGradient id="mv-wheel" cx=".5" cy=".5" r=".5">'
        f'<stop offset="0" stop-color="{c["gold_hi"]}"/><stop offset="1" stop-color="{_mix(c["acc"], c["gold_lo"], .5)}"/></radialGradient>'
        f'<radialGradient id="mv-plate" cx=".5" cy=".5" r=".5">'
        f'<stop offset=".25" stop-color="{c["plate"]}"/><stop offset="1" stop-color="{c["plate_edge"]}"/></radialGradient>'
        f'<linearGradient id="mv-case" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["gold_hi"]}"/><stop offset=".5" stop-color="{c["gold_lo"]}"/>'
        f'<stop offset="1" stop-color="{c["gold_hi"]}"/></linearGradient>'
        f'<linearGradient id="mv-steel" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["steel_hi"]}"/><stop offset="1" stop-color="{c["steel_lo"]}"/></linearGradient>'
        f'<linearGradient id="mv-edge" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["bevel_hi"]}"/><stop offset=".6" stop-color="{c["acc"]}"/>'
        f'<stop offset="1" stop-color="{c["bevel_lo"]}"/></linearGradient>'
        f'<linearGradient id="mv-sheen" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset=".3" stop-color="#fff" stop-opacity="0"/><stop offset=".48" stop-color="#fff" stop-opacity=".045"/>'
        f'<stop offset=".62" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )


# ----------------------------------------------------------------- shapes
def _circle(x: float, y: float, rad: float) -> str:
    return (f'M{_p(x - rad, y)}A{_f(rad)} {_f(rad)} 0 1 1 {_p(x + rad, y)}'
            f'A{_f(rad)} {_f(rad)} 0 1 1 {_p(x - rad, y)}Z')


def _sector(r_out: float, r_in: float, a1: float, a2: float, h: float, fil: float,
            cx: float = 0.0, cy: float = 0.0) -> str:
    """Annular sector a1..a2 (clock degrees) whose straight sides run parallel to
    the radii at a1 and a2, h px inside them; corners rounded by about fil px."""
    def at(rho, deg):
        x, y = _pol(rho, deg)
        return cx + x, cy + y

    oa = math.degrees(math.asin(min(.95, h / r_out)))
    ia = math.degrees(math.asin(min(.95, h / r_in)))
    A, B = at(r_out, a1 + oa), at(r_out, a2 - oa)
    C, D = at(r_in, a2 - ia), at(r_in, a1 + ia)

    def toward(p, q, d):
        L = math.hypot(q[0] - p[0], q[1] - p[1]) or 1
        return p[0] + (q[0] - p[0]) * d / L, p[1] + (q[1] - p[1]) * d / L

    fo, fi = math.degrees(fil / r_out), math.degrees(fil / r_in)
    a_s, a_e = at(r_out, a1 + oa + fo), at(r_out, a2 - oa - fo)
    i_s, i_e = at(r_in, a2 - ia - fi), at(r_in, a1 + ia + fi)
    big_o = 1 if (a2 - oa - fo) - (a1 + oa + fo) > 180 else 0
    big_i = 1 if (a2 - ia - fi) - (a1 + ia + fi) > 180 else 0
    return (f'M{_p(*toward(A, D, fil))}Q{_p(*A)} {_p(*a_s)}'
            f'A{_f(r_out)} {_f(r_out)} 0 {big_o} 1 {_p(*a_e)}'
            f'Q{_p(*B)} {_p(*toward(B, C, fil))}L{_p(*toward(C, B, fil))}'
            f'Q{_p(*C)} {_p(*i_s)}A{_f(r_in)} {_f(r_in)} 0 {big_i} 0 {_p(*i_e)}'
            f'Q{_p(*D)} {_p(*toward(D, A, fil))}Z')


def _teeth(r: float, n: int, add: float = 1.0, ded: float = 1.3,
           w_root: float = .29, w_tip: float = .15, cx: float = 0.0, cy: float = 0.0) -> str:
    """Closed outline of n rounded (ogival, watch-style) teeth on pitch radius r."""
    m = 2 * r / n
    ra, rd = r + add * m, r - ded * m
    step = 360 / n
    at = lambda rho, deg: (cx + _pol(rho, deg)[0], cy + _pol(rho, deg)[1])
    cmds = []
    for i in range(n):
        c = i * step
        cmds += [("M" if i == 0 else "L", [at(rd, c - w_root * step)]),
                 ("Q", [at(ra, c - w_tip * step), at(ra, c)]),
                 ("Q", [at(ra, c + w_tip * step), at(rd, c + w_root * step)])]
    return _rel(cmds) + "Z"


def gear(cx: float, cy: float, r: float, teeth: int, spokes: int, *, rim: float | None = None,
         hub: float | None = None, spoke_w: float | None = None) -> str:
    """Path data (fill-rule evenodd) for a toothed wheel centred at (cx, cy) with
    pitch radius r and `spokes` cut-out spokes; tooth 0 points to 12 o'clock.
    Rim, hub and spoke widths default to watch-like proportions of r."""
    m = 2 * r / teeth
    rd = r - 1.3 * m
    rim = rim if rim is not None else max(1.1, .11 * r)
    hub = hub if hub is not None else max(1.6, .2 * r)
    spoke_w = spoke_w if spoke_w is not None else max(.9, .09 * r)
    d = [_teeth(r, teeth, cx=cx, cy=cy)]
    r_out = rd - rim
    if spokes and r_out - hub > 2.5:
        step = 360 / spokes
        fil = min(1.2, (r_out - hub) * .22)
        for i in range(spokes):
            a = 90 / spokes + i * step
            d.append(_sector(r_out, hub, a, a + step, spoke_w / 2, fil, cx, cy))
    return "".join(d)


def _escape(r: float, n: int = ESC_TEETH, spokes: int = 5) -> str:
    """Club-tooth escape wheel turning counter-clockwise: teeth lean that way."""
    step = 360 / n
    rt, rr = r, r * .72
    out = []
    for i in range(n):
        c = i * step
        p0 = _pol(rr, c)
        back = _pol(rr + (rt - rr) * .55, c - step * .30)
        tip = _pol(rt, c - step * .52)
        club = _pol(rt * .965, c - step * .66)
        front = _pol(rr * 1.02, c - step * .58)
        nxt = _pol(rr, c - step)
        out.append(f'{"M" if i == 0 else "L"}{_p(*p0)}Q{_p(*back)} {_p(*tip)}L{_p(*club)}'
                   f'L{_p(*front)}A{_f(rr)} {_f(rr)} 0 0 0 {_p(*nxt)}')
    d = ["".join(out) + "Z"]
    s = 360 / spokes
    for i in range(spokes):
        d.append(_sector(rr - r * .14, r * .22, i * s + s * .5, i * s + s * 1.5, r * .045, .5))
    return "".join(d)


def _spiral(r0: float, r1: float, cx: float = 0.0, cy: float = 0.0, start: float = 0.0,
            pitch: float = 1.0) -> str:
    """Archimedean spiral from radius r0 out to r1, about `pitch` px between
    coils, built from half-circle arcs whose centre steps along a short axis
    (the classic two-centre construction). `start` is the clock angle of the
    inner end."""
    turns = max(1, round((r1 - r0) / pitch))
    pitch = (r1 - r0) / turns
    ux, uy = _pol(1, start)
    cur = (cx + ux * r0, cy + uy * r0)
    centre, rad = (cx, cy), r0
    d = [f"M{_p(*cur, 2)}"]
    for _ in range(turns * 2):
        end = (2 * centre[0] - cur[0], 2 * centre[1] - cur[1])
        d.append(f"A{_f(rad, 2)} {_f(rad, 2)} 0 0 1 {_p(*end, 2)}")
        rad2 = rad + pitch / 2
        dx, dy = (end[0] - centre[0]) / rad, (end[1] - centre[1]) / rad
        centre, cur, rad = (end[0] - dx * rad2, end[1] - dy * rad2), end, rad2
    return "".join(d)


# ----------------------------------------------------------------- outlines
def _cr_open(pts, move: bool = True) -> str:
    """Catmull-Rom spline through pts as cubic Beziers (open curve)."""
    d = [f"M{_p(*pts[0])}"] if move else []
    q = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(q) - 2):
        p0, p1, p2, p3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{_p(*c1)} {_p(*c2)} {_p(*p2)}")
    return "".join(d)


def _area(pts) -> float:
    return sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) / 2


def _arm(ctrl, samples: int = 5):
    """Outline of a flat bridge arm: a smooth centre line through ctrl points
    (x, y, width) whose width eases from point to point, with round ends.
    Returns (path data, centre-line samples). Wound clockwise, so several arms
    in one path union under the nonzero rule."""
    q = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    line = []
    for i in range(1, len(q) - 2):
        p0, p1, p2, p3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        for j in range(samples):
            s = j / samples
            s2, s3 = s * s, s * s * s
            xy = [0.5 * (2 * p1[a] + (-p0[a] + p2[a]) * s + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * s2
                         + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * s3) for a in (0, 1)]
            e = s * s * (3 - 2 * s)
            line.append((xy[0], xy[1], p1[2] + (p2[2] - p1[2]) * e))
    line.append(tuple(ctrl[-1]))
    n = len(line)
    left, right = [], []
    for i, (x, y, w) in enumerate(line):
        a, b = line[max(0, i - 1)], line[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    if _area(left + right[::-1]) < 0:
        left, right = right, left

    def cap(a, b, end: bool):
        i, j = (n - 1, n - 2) if end else (0, 1)
        x, y, w = line[i]
        tx, ty = x - line[j][0], y - line[j][1]
        L = math.hypot(tx, ty) or 1
        fx, fy = x + tx / L * w / 2, y + ty / L * w / 2
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        cross = (a[0] - mx) * (fy - my) - (a[1] - my) * (fx - mx)
        rr = math.hypot(a[0] - b[0], a[1] - b[1]) / 2
        return f"A{_f(rr)} {_f(rr)} 0 0 {1 if cross > 0 else 0} {_p(*b)}"

    d = (_cr_open(left) + cap(left[-1], right[-1], True)
         + _cr_open(right[::-1], move=False) + cap(right[0], left[0], False) + "Z")
    return d, line


def _union_outline(circles) -> str:
    """Closed outline(s) of the union of circles [(x, y, r), ...] as arcs,
    every loop wound clockwise. Arcs of one circle hidden inside another are
    dropped, so neighbouring cut-outs meet in sharp re-entrant cusps."""
    arcs = []                                        # (circle, start deg, end deg), clock angles
    for i, (xi, yi, ri) in enumerate(circles):
        cover = []
        inside = False
        for j, (xj, yj, rj) in enumerate(circles):
            if i == j:
                continue
            d = math.hypot(xj - xi, yj - yi)
            if d + ri <= rj:
                inside = True
                break
            if d >= ri + rj or d + rj <= ri:
                continue
            th = _ang(xj - xi, yj - yi)
            al = math.degrees(math.acos((ri * ri + d * d - rj * rj) / (2 * ri * d)))
            cover.append((th - al, th + al))
        if inside:
            continue
        if not cover:
            arcs.append((i, None, None))
            continue
        # merge covered intervals on the circle, then keep the gaps between them
        base = cover[0][0]
        iv = sorted(((a - base) % 360, (a - base) % 360 + (b - a)) for a, b in cover)
        merged = [list(iv[0])]
        for a, b in iv[1:]:
            if a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        for k, (a, b) in enumerate(merged):
            nxt = merged[(k + 1) % len(merged)][0] + (360 if k == len(merged) - 1 else 0)
            if nxt - b > 1e-6 and b < 360 + merged[0][0]:
                arcs.append((i, base + b, base + nxt))
    pt = lambda i, a: (circles[i][0] + _pol(circles[i][2], a)[0], circles[i][1] + _pol(circles[i][2], a)[1])
    d = []
    left = [a for a in arcs if a[1] is not None]
    for i, _, _ in (a for a in arcs if a[1] is None):
        x, y, rr = circles[i]
        d.append(_circle(x, y, rr))
    while left:
        loop = [left.pop(0)]
        while True:
            end = pt(loop[-1][0], loop[-1][2])
            nxt = min(left, key=lambda a: math.dist(pt(a[0], a[1]), end), default=None)
            if nxt is None or math.dist(pt(nxt[0], nxt[1]), end) > .5:
                break
            left.remove(nxt)
            loop.append(nxt)
        s = [f"M{_p(*pt(loop[0][0], loop[0][1]))}"]
        for i, a, b in loop:
            rr = circles[i][2]
            s.append(f"A{_f(rr)} {_f(rr)} 0 {1 if b - a > 180 else 0} 1 {_p(*pt(i, b))}")
        d.append("".join(s) + "Z")
    return "".join(d)


# ----------------------------------------------------------------- motion
def _spin(x: float, y: float, a0: float, period: float, sign: int, still: bool, body: str,
          steps: int = 0, begin: float = 0.0) -> str:
    """A body drawn around its own origin, placed at (x, y), turned to a0 and
    (unless still) rotating once per `period` s (sign +1 = clockwise)."""
    tr = f"translate({_p(x, y)}) " if (x or y) else ""
    head = f'<g transform="{tr}rotate({_f(a0 % 360)})">'
    if still:
        return head + body + "</g>"
    if steps:
        vals = ";".join(_f(sign * 360 * i / steps, 2) for i in range(steps))
        b = f' begin="{_f(begin, 2)}s"' if begin else ""
        anim = (f'<animateTransform attributeName="transform" type="rotate" additive="sum" '
                f'calcMode="discrete" values="{vals}" dur="{_f(period, 2)}s"{b} repeatCount="indefinite"/>')
    else:
        anim = (f'<animateTransform attributeName="transform" type="rotate" additive="sum" '
                f'values="0;{sign * 360}" dur="{_f(period)}s" repeatCount="indefinite"/>')
    return head + anim + body + "</g>"


def _swing(x: float, y: float, still_a: float, still: bool, body: str, values: str,
           key_times: str | None = None, spline: bool = False, dur: float = BALANCE_PERIOD) -> str:
    head = f'<g transform="translate({_p(x, y)}){f" rotate({_f(still_a)})" if still else ""}">'
    if still:
        return head + body + "</g>"
    kt = f' keyTimes="{key_times}"' if key_times else ""
    mode = ""
    if spline:   # sine-like ease in/out: a balance is a harmonic oscillator
        ks = ";".join([".37 0 .63 1"] * values.count(";"))
        mode = f' calcMode="spline" keySplines="{ks}"'
    anim = (f'<animateTransform attributeName="transform" type="rotate" additive="sum" '
            f'values="{values}"{kt}{mode} dur="{_f(dur, 2)}s" repeatCount="indefinite"/>')
    return head + anim + body + "</g>"


def _mesh_phase(a_drv: float, n_drv: int, x_drv: float, y_drv: float,
                n_drn: int, x_drn: float, y_drn: float) -> float:
    """Phase (clock deg of tooth 0) for the driven gear so that its teeth fall
    into the driver's gaps on the line of centres."""
    phi = _ang(x_drn - x_drv, y_drn - y_drv)
    u = ((phi - a_drv) / (360 / n_drv)) % 1.0
    return (phi + 180) - (0.5 - u) * (360 / n_drn)


# ----------------------------------------------------------------- the watch
def movement(cx: float, cy: float, r: float, theme: dict, still: bool, label_svg: str = "") -> str:
    """The watch as one <g>. label_svg (absolute coordinates) is drawn on the
    dial under the hands; LABEL_ANCHOR says where it fits."""
    t, c = theme, _pal(theme)
    k = r / 118.0                    # hairlines scale with the watch
    U = lambda v: v * r              # r-units -> px
    sw = lambda v: _f(max(.3, v * k), 2)
    rp = lambda R, N, p: R * p / N   # pinion pitch radius at the same module
    polish = f' stroke="{c["bevel_hi"]}" stroke-opacity=".35" stroke-width="{sw(.4)}"'
    out: list[str] = ["<g>"]
    add = out.append

    # ---------------- layout (r-units; x right, y down; centre = 0,0) ----------------
    P_R = .775                       # plate edge / inner edge of the chapter ring
    C_R, C_N, T_P = .36, 75, 10      # centre wheel, third pinion
    T_R, T_N, F_P = .21, 56, 7       # third wheel, fourth pinion
    F_R, F_N, E_P = .16, 40, 8       # fourth wheel, escape pinion
    E_R = .088                       # escape wheel tip radius
    B_R, B_N = .28, 36               # barrel
    BAL_R = .20
    BAL_P = _pol(.53, 242)
    P_P = (BAL_P[0], BAL_P[1] - .20)                 # pallet arbor, straight above the balance
    E_P_ = (P_P[0], P_P[1] - .105)                   # escape wheel above the pallet
    F_P_ = tuple(a + b for a, b in zip(E_P_, _pol(F_R + rp(F_R, F_N, E_P), 25)))
    d_ct, d_tf = C_R + rp(C_R, C_N, T_P), T_R + rp(T_R, T_N, F_P)
    fF = math.hypot(*F_P_)
    alpha = math.degrees(math.acos((d_ct ** 2 + fF ** 2 - d_tf ** 2) / (2 * d_ct * fF)))
    T_P_ = _pol(d_ct, _ang(*F_P_) + alpha)
    B_P = _pol(.455, 50)
    RAT_R, RAT_N, CR_N = .165, 40, 20
    CR_R = RAT_R * CR_N / RAT_N
    CR_P = tuple(a + b for a, b in zip(B_P, _pol(RAT_R + CR_R, 160)))

    px = lambda p: (U(p[0]), U(p[1]))
    B, T, F, E, P, BAL, CR = map(px, (B_P, T_P_, F_P_, E_P_, P_P, BAL_P, CR_P))
    rim = lambda deg, rho=.80: px(_pol(rho, deg))
    bx, by = B

    add(f'<g transform="translate({_p(cx, cy)})">')
    # ---------------- case back / void, and the centre wheel below the plate ----------------
    add(f'<circle r="{_f(r)}" fill="{c["void"]}"/>')
    add(_spin(0, 0, 2.0, 3600, 1, still,
              f'<path d="{gear(0, 0, U(C_R), C_N, 5, rim=U(.028), hub=U(.07), spoke_w=U(.03))}" '
              f'fill="{c["sunk"]}" fill-rule="evenodd"/>'))

    # ---------------- open-worked plate ----------------
    # Cut-outs are circles hugging the wheels; where two meet they leave a sharp
    # re-entrant cusp, the mark of a hand-skeletonised plate. The union outline
    # is computed here (no masks: the image is re-rasterised every frame), and
    # its edge gets a thin polished bevel (anglage).
    holes = [(*T, U(T_R + .03)), (*F, U(F_R + .028)), (*E, U(.105)), (*BAL, U(BAL_R + .018)),
             (*B, U(.292)), (*CR, U(.12)), (*px(_pol(.43, 118)), U(.15))]
    wd = _union_outline(holes)
    plate_r = U(P_R + .01)
    add(f'<path d="{_circle(0, 0, plate_r)}{wd}" fill="url(#mv-plate)" fill-rule="evenodd"/>')
    if c["dark"]:
        add(f'<path d="{_circle(0, 0, plate_r)}{wd}" fill="url(#mv-sheen)" fill-rule="evenodd"/>')
    add(f'<path d="{wd}" fill="none" stroke="{c["bevel_hi"] if c["dark"] else c["acc"]}" stroke-opacity=".55" '
        f'stroke-width="{sw(1)}"/>')

    # ---------------- barrel: the drum turns over the mainspring ----------------
    spring = _spiral(U(.07), U(.24), 0, 0, 0, pitch=1.15 * k)
    add(f'<path transform="translate({_p(bx, by)})" d="{spring}" fill="none" stroke="{c["steel_lo"]}" '
        f'stroke-opacity=".75" stroke-width="{sw(.5)}"/>')
    add(_spin(bx, by, 4.0, 240, -1, still,
              f'<path d="{gear(0, 0, U(B_R), B_N, 5, rim=U(.034), hub=U(.085), spoke_w=U(.028))}" '
              f'fill="url(#mv-wheel)" fill-rule="evenodd"{polish}/>'))

    # ---------------- going train ----------------
    a_t = 5.0
    a_f = _mesh_phase(a_t, T_N, *T, F_P, *F)        # fourth pinion into the third wheel
    a_e = _mesh_phase(a_f, F_N, *F, E_P, *E)        # escape pinion into the fourth wheel
    add(_spin(*E, a_e, ESC_PERIOD, -1, still,
              f'<path d="{_escape(U(E_R))}" fill="url(#mv-steel)" fill-rule="evenodd"/>',
              steps=ESC_STEPS, begin=-BALANCE_PERIOD / 4))
    add(_spin(*F, a_f, 60, 1, still,
              f'<path d="{gear(0, 0, U(F_R), F_N, 5)}" fill="url(#mv-wheel)" fill-rule="evenodd"{polish}/>'))
    add(_spin(*T, a_t, 480, -1, still,
              f'<path d="{gear(0, 0, U(T_R), T_N, 5)}" fill="url(#mv-wheel)" fill-rule="evenodd"{polish}/>'))

    # ---------------- pallet fork (lever and anchor) ----------------
    d_ep = U(.105)
    # the stones sit on the escape wheel's tip circle, 30 deg either side of the line of centres
    st = [(_pol(U(E_R), 180 + s * 30)[0], -d_ep + _pol(U(E_R), 180 + s * 30)[1]) for s in (-1, 1)]
    L = U(.205) - U(.04)
    w = U(.011)
    lever = (f'M{_p(-w, 0)}L{_p(-w * .55, L - U(.022))}L{_p(-U(.02), L)}L{_p(-U(.011), L + U(.013))}'
             f'L{_p(0, L - U(.006))}L{_p(U(.011), L + U(.013))}L{_p(U(.02), L)}'
             f'L{_p(w * .55, L - U(.022))}L{_p(w, 0)}Z')
    anchor = (f'M{_p(st[0][0] - U(.012), st[0][1] + U(.01))}Q{_p(0, U(.03))} {_p(st[1][0] + U(.012), st[1][1] + U(.01))}'
              f'L{_p(st[1][0] - U(.006), st[1][1] + U(.018))}Q{_p(0, U(.012))} {_p(st[0][0] + U(.006), st[0][1] + U(.018))}Z')
    stones = "".join(
        f'M{_p(x - U(.006), y - U(.004))}L{_p(x + U(.006), y - U(.004))}L{_p(x + U(.0072), y + U(.02))}'
        f'L{_p(x - U(.0072), y + U(.02))}Z' for x, y in st)
    fork = (f'<path d="{lever}{anchor}" fill="url(#mv-steel)"/>'
            f'<path d="{stones}" fill="{c["ruby"]}"/>'
            f'<circle r="{_f(U(.022), 2)}" fill="url(#mv-steel)"/>')
    p_amp = 7.0
    add(_swing(*P, p_amp, still, fork,
               f"{_f(p_amp)};{_f(p_amp)};{_f(-p_amp)};{_f(-p_amp)};{_f(p_amp)};{_f(p_amp)}",
               key_times="0;.19;.31;.69;.81;1"))

    # ---------------- balance wheel and hairspring ----------------
    bR = U(BAL_R)
    screws = "".join(_circle(*_pol(bR + U(.014), i * 30 + 15), U(.009)) for i in range(12))
    arms = "".join(f'M0 0L{_p(*_pol(bR, a))}' for a in (60, 180, 300))
    bal = (f'<path d="{arms}" stroke="{c["acc"]}" stroke-width="{_f(U(.017), 2)}" stroke-linecap="round"/>'
           f'<circle r="{_f(bR)}" fill="none" stroke="url(#mv-gold)" stroke-width="{_f(U(.026), 2)}"/>'
           f'<path d="{screws}" fill="{c["gold_hi"]}"/>'
           f'<circle r="{_f(U(.04))}" fill="url(#mv-gold)"/>'
           f'<circle cy="{_f(-U(.03))}" r="{_f(U(.009), 2)}" fill="{c["ruby"]}"/>')
    amp = BALANCE_AMP
    add(_swing(*BAL, STILL["balance"], still, bal, f"{_f(-amp)};{_f(amp)};{_f(-amp)}",
               key_times="0;.5;1", spline=True))
    hs = _spiral(U(.03), U(.125), 0, 0, 90, pitch=1.05 * k)
    add(_swing(*BAL, STILL["balance"] * .45, still,
               f'<path d="{hs}" fill="none" stroke="{c["steel_hi"]}" stroke-opacity=".85" stroke-width="{sw(.42)}"/>',
               f"{_f(-amp * .45)};{_f(amp * .45)};{_f(-amp * .45)}", key_times="0;.5;1", spline=True))

    # ---------------- bridges: one outline, so one gradient lights them all ----------------
    def mid(a, b, w_, bow=0.0):
        """Midpoint pushed sideways by bow * segment length (bridges are rarely straight)."""
        dx, dy = b[0] - a[0], b[1] - a[1]
        return ((a[0] + b[0]) / 2 - dy * bow, (a[1] + b[1]) / 2 + dx * bow, w_)

    tr_top, tr_end = rim(352), rim(286)
    arms_ctrl = [
        [(*tr_top, U(.05)), mid(tr_top, T, U(.036), -.1), (*T, U(.082)), mid(T, F, U(.03)), (*F, U(.07)),
         mid(F, E, U(.03)), (*E, U(.06)), mid(E, tr_end, U(.034)), (*tr_end, U(.05))],
        [(*rim(256), U(.045)), mid(rim(256), P, U(.03), .08), (*P, U(.05))],
        [(*rim(224), U(.06)), mid(rim(224), BAL, U(.04), -.12), (*BAL, U(.1))],
        [(*rim(14), U(.055)), mid(rim(14), B, U(.04), .12), (*B, U(.12)), mid(B, CR, U(.04)), (*CR, U(.075)),
         mid(CR, rim(132), U(.034), -.1), (*rim(132), U(.05))],
    ]
    arm_d, lines = zip(*(_arm(a) for a in arms_ctrl))
    add(f'<use href="#mv-br" transform="translate({_p(.5 * k, .8 * k, 2)})" fill="{c["bevel_lo"]}" fill-opacity=".55"/>')
    add(f'<use href="#mv-br" fill="none" stroke="url(#mv-edge)" stroke-width="{sw(1.5)}" stroke-linejoin="round"/>')
    add(f'<g fill="url(#mv-gold)"><path id="mv-br" d="{"".join(arm_d)}"/></g>')

    # keyless works on the barrel bridge: ratchet and crown wheel (they only turn when winding)
    a_cr = _mesh_phase(0, RAT_N, *B, CR_N, *CR)
    add(f'<path transform="translate({_p(bx, by)})" d="{gear(0, 0, U(RAT_R), RAT_N, 0)}" fill="url(#mv-gold)" '
        f'stroke="{c["bevel_lo"]}" stroke-width="{sw(.35)}"/>')
    add(f'<path transform="translate({_p(*CR)}) rotate({_f(a_cr)})" d="{gear(0, 0, U(CR_R), CR_N, 0)}" '
        f'fill="url(#mv-gold)" stroke="{c["bevel_lo"]}" stroke-width="{sw(.35)}"/>')
    sun = "".join(f'M{_p(*_pol(U(RAT_R) * .2, a))}L{_p(*_pol(U(RAT_R) * .84, a))}' for a in range(0, 360, 8))
    add(f'<path transform="translate({_p(bx, by)})" d="{sun}" stroke="{c["bevel_hi"]}" stroke-opacity=".3" '
        f'stroke-width="{sw(.4)}"/>')
    add(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="{_f(U(RAT_R) * .86)}" fill="none" stroke="{c["bevel_lo"]}" '
        f'stroke-opacity=".45" stroke-width="{sw(.5)}"/>')

    # ---------------- jewels and screws ----------------
    def jewel(x, y, s=1.0):
        return (f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(U(.022) * s, 2)}" fill="{c["bevel_hi"]}" '
                f'stroke="{c["bevel_lo"]}" stroke-width="{sw(.35)}"/>'
                f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(U(.0135) * s, 2)}" fill="{c["ruby"]}"/>'
                f'<circle cx="{_f(x - U(.004) * s, 2)}" cy="{_f(y - U(.0045) * s, 2)}" r="{_f(U(.0045) * s, 2)}" '
                f'fill="{c["ruby_hi"]}" fill-opacity=".85"/>')

    def screw(x, y, a=30.0, s=1.0):
        sx, sy = _pol(U(.016) * s, a)
        return (f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(U(.021) * s, 2)}" fill="url(#mv-steel)" '
                f'stroke="{c["bevel_lo"]}" stroke-width="{sw(.4)}"/>'
                f'<path d="M{_p(x - sx, y - sy)}L{_p(x + sx, y + sy)}" stroke="{c["bevel_lo"]}" stroke-width="{sw(.75)}"/>')

    for (x, y), s in ((T, 1), (F, .95), (E, .85), (P, .72)):
        add(jewel(x, y, s))
    add(jewel(*BAL, 1.2))      # balance jewel under a shock-protection lyre spring
    lyre = "".join(f'M{_p(BAL[0] + _pol(U(.036), a)[0], BAL[1] + _pol(U(.036), a)[1])}'
                   f'A{_f(U(.036))} {_f(U(.036))} 0 0 1 '
                   f'{_p(BAL[0] + _pol(U(.036), a + 70)[0], BAL[1] + _pol(U(.036), a + 70)[1])}'
                   for a in (15, 135, 255))
    add(f'<path d="{lyre}" fill="none" stroke="{c["steel_hi"]}" stroke-width="{sw(.8)}" stroke-linecap="round"/>')

    def foot(line, rho=.735):
        for x, y, _ in line:
            if math.hypot(x, y) < U(rho):
                return x, y
        return line[-1][:2]

    feet = [foot(lines[0]), foot(lines[0][::-1]), foot(lines[1]), foot(lines[2]), foot(lines[3]),
            foot(lines[3][::-1])]
    for (x, y), a in zip(feet, (20, 75, 130, 160, 40, 105)):
        add(screw(x, y, a))
    add(screw(bx, by, 65, 1.35))
    add(screw(*CR, 15, .85))

    # ---------------- chapter ring and case ----------------
    ring_in = U(P_R)
    ring_w = r - U(.025) - ring_in
    add(f'<circle r="{_f(ring_in - .8 * k)}" fill="none" stroke="#000" stroke-opacity="{".35" if c["dark"] else ".08"}" '
        f'stroke-width="{_f(2.4 * k, 2)}"/>')
    add(f'<circle r="{_f(ring_in + ring_w / 2)}" fill="none" stroke="{t["dial"]}" stroke-width="{_f(ring_w)}"/>')
    add(f'<circle r="{_f(ring_in)}" fill="none" stroke="{c["acc"]}" stroke-opacity=".7" stroke-width="{sw(.8)}"/>')
    add(f'<circle r="{_f(r - 1.4 * k)}" fill="none" stroke="url(#mv-case)" stroke-width="{_f(2.8 * k)}"/>')
    add(f'<circle r="{_f(r - 3 * k)}" fill="none" stroke="{c["bevel_lo"]}" stroke-opacity=".8" stroke-width="{sw(.6)}"/>')
    minor, major, quarter = [], [], []
    r0 = r - U(.045)
    for i in range(60):
        if i % 15 == 0:
            ln, bucket = U(.075), quarter
        elif i % 5 == 0:
            ln, bucket = U(.058), major
        else:
            ln, bucket = U(.032), minor
        bucket.append(f'M{_p(*_pol(r0, i * 6))}L{_p(*_pol(r0 - ln, i * 6))}')
    add(f'<path d="{"".join(minor)}" stroke="{t["tick"]}" stroke-width="{sw(.6)}"/>')
    add(f'<path d="{"".join(major)}" stroke="{t["tick_major"]}" stroke-width="{sw(1.1)}"/>')
    add(f'<path d="{"".join(quarter)}" stroke="{t["tick_major"]}" stroke-width="{sw(1.5)}"/>')
    idx = []
    i0, i1 = r - U(.145), r - U(.212)
    for h in range(12):
        for o in ((-U(.017), U(.017)) if h == 0 else (0.0,)):
            ox, oy = _pol(o, h * 30 + 90)
            (x0, y0), (x1, y1) = _pol(i0, h * 30), _pol(i1, h * 30)
            idx.append(f'M{_p(x0 + ox, y0 + oy)}L{_p(x1 + ox, y1 + oy)}')
    idx_d = "".join(idx)
    add(f'<path d="{idx_d}" transform="translate({_p(.45 * k, .6 * k, 2)})" stroke="{c["bevel_lo"]}" '
        f'stroke-width="{_f(U(.026), 2)}" stroke-linecap="round"/>')
    add(f'<path d="{idx_d}" stroke="url(#mv-gold)" stroke-width="{_f(U(.022), 2)}" stroke-linecap="round"/>')
    add("</g>")

    # ---------------- label (caller's text paths, absolute coordinates) ----------------
    if label_svg:
        add(label_svg)

    # ---------------- hands ----------------
    add(f'<g transform="translate({_p(cx, cy)})">')
    halo = c["plate"]
    Lm, wm, tail_m = U(.80), U(.036), U(.11)
    m_dark = _mix(t["hand"], t["dial"], .32)
    outline = f'M0 {_f(-Lm)}L{_p(-wm, -Lm * .24)}L0 {_f(tail_m)}L{_p(wm, -Lm * .24)}Z'
    mh = (f'<path d="{outline}" fill="{t["hand"]}" stroke="{halo}" stroke-width="{sw(1.6)}" '
          f'stroke-linejoin="round" paint-order="stroke"/>'
          f'<path d="M0 {_f(-Lm)}L{_p(wm, -Lm * .24)}L0 {_f(tail_m)}Z" fill="{m_dark}"/>')
    Ls, tail = U(.90), U(.22)
    sh = (f'<path d="M0 {_f(tail)}V{_f(-Ls)}" stroke="{halo}" stroke-width="{sw(2.4)}" stroke-linecap="round"/>'
          f'<circle cy="{_f(U(.155))}" r="{_f(U(.026))}" fill="{halo}" stroke="{halo}" stroke-width="{sw(2.6)}"/>'
          f'<path d="M0 {_f(tail)}V{_f(-Ls)}" stroke="{t["hand_sec"]}" stroke-width="{sw(1)}" stroke-linecap="round"/>'
          f'<circle cy="{_f(U(.155))}" r="{_f(U(.026))}" fill="none" stroke="{t["hand_sec"]}" stroke-width="{sw(1.2)}"/>'
          f'<circle r="{_f(U(.03))}" fill="{t["hand_sec"]}"/>')
    for body, period, pose in ((mh, 3600, STILL["minute"]), (sh, 60, STILL["second"])):
        if still:
            add(f'<g transform="rotate({_f(pose)})">{body}</g>')
        else:
            add(f'<g><animateTransform attributeName="transform" type="rotate" values="0;360" dur="{period}s" '
                f'repeatCount="indefinite"/>{body}</g>')
    add(f'<circle r="{_f(U(.042))}" fill="{t["hand"]}" stroke="{halo}" stroke-width="{sw(.8)}"/>')
    add(f'<circle r="{_f(U(.022))}" fill="{t["hand_sec"]}"/>')
    add(f'<circle r="{_f(U(.009), 2)}" fill="{t["cap"]}"/>')
    add("</g></g>")
    return "".join(out)
