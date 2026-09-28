"""Vector art toolkit: outlined type from real OFL fonts + hand-cut style shape primitives.

Everything is emitted as plain SVG paths (no font dependency, no raster, no AI imagery).
Coordinates are pixels at 300 DPI, origin top-left.
"""

import math
import random
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).parent / "fonts"
FONT_FILES = {
    "bowlby": "bowlby-one-latin-400-normal.woff2",
    "alfa": "alfa-slab-one-latin-400-normal.woff2",
    "fraunces": "fraunces-latin-900-normal.woff2",
    "dmsans800": "dm-sans-latin-800-normal.woff2",
    "dmsans700": "dm-sans-latin-700-normal.woff2",
}


def f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- type

class Face:
    def __init__(self, name: str):
        tt = TTFont(FONT_DIR / FONT_FILES[name])
        tt.flavor = None
        buf = BytesIO()
        tt.save(buf)
        self.tt = TTFont(BytesIO(buf.getvalue()))
        self.upem = self.tt["head"].unitsPerEm
        self.order = self.tt.getGlyphOrder()
        self.gs = self.tt.getGlyphSet()
        self.hbfont = hb.Font(hb.Face(hb.Blob(buf.getvalue())))
        os2 = self.tt["OS/2"]
        self.cap = getattr(os2, "sCapHeight", 0) or self.upem * 0.7


@lru_cache(maxsize=None)
def face(name: str) -> Face:
    return Face(name)


def shape(text: str, fname: str):
    fc = face(fname)
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(fc.hbfont, b, {"kern": True, "liga": False})
    return fc, b.glyph_infos, b.glyph_positions


def text_width(text: str, fname: str, size: float, tracking: float = 0.0) -> float:
    fc, infos, pos = shape(text, fname)
    adv = sum(p.x_advance for p in pos) * size / fc.upem
    return adv + tracking * size * (len(infos) - 1)


def text_path(text: str, fname: str, size: float, x: float, baseline: float, tracking: float = 0.0) -> str:
    """Outlined text; x is the left edge, baseline in canvas coords."""
    fc, infos, pos = shape(text, fname)
    s = size / fc.upem
    pen_x = x
    parts = []
    for info, p in zip(infos, pos):
        name = fc.order[info.codepoint]
        sp = SVGPathPen(fc.gs)
        tp = TransformPen(sp, (s, 0, 0, -s, pen_x + p.x_offset * s, baseline - p.y_offset * s))
        fc.gs[name].draw(tp)
        parts.append(sp.getCommands())
        pen_x += p.x_advance * s + tracking * size
    return " ".join(x for x in parts if x)


def cap_height(fname: str, size: float) -> float:
    return face(fname).cap * size / face(fname).upem


def fit_size(lines, fname, target_w, tracking=0.0):
    return target_w / max(text_width(l, fname, 1.0, tracking) for l in lines)


# ---------------------------------------------------------------- shapes

def catmull(points, closed=True):
    """Smooth path through points (Catmull-Rom -> cubic beziers)."""
    n = len(points)
    d = [f"M{f(points[0][0])} {f(points[0][1])}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = points[(i - 1) % n] if closed or i > 0 else points[i]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n] if closed or i + 2 < n else points[(i + 1) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return " ".join(d) + (" Z" if closed else "")


def blob(cx, cy, rx, ry, amp=0.025, n=16, seed=1, rot=0.0):
    """Ellipse with slight hand-cut irregularity."""
    r = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + r.uniform(-amp, amp)
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        ca, sa = math.cos(rot), math.sin(rot)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return catmull(pts)


def wobble_poly(points, amp=6, seed=1, smooth=True):
    r = random.Random(seed)
    pts = [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in points]
    return catmull(pts) if smooth else "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + " Z"


def heart(cx, cy, w, seed=3):
    """Heart, top-center notch at (cx, cy - 0.18w)."""
    h = w * 0.92
    pts = []
    for i in range(36):
        t = 2 * math.pi * i / 36
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x, y))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    sx = w / (max(xs) - min(xs))
    sy = h / (max(ys) - min(ys))
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    r = random.Random(seed)
    out = [(cx + (x - mx) * sx + r.uniform(-1, 1) * w * 0.006, cy + (y - my) * sy + r.uniform(-1, 1) * w * 0.006) for x, y in pts]
    return catmull(out)


def star5(cx, cy, R, r=None, rot=-90, seed=5):
    r = r or R * 0.48
    rnd = random.Random(seed)
    pts = []
    for i in range(10):
        rad = R if i % 2 == 0 else r
        rad *= 1 + rnd.uniform(-0.02, 0.02)
        a = math.radians(rot + i * 36)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + " Z"


def paw(cx, cy, s, seed=7):
    """Paw print: pad + four toes. s = overall width."""
    d = [blob(cx, cy + 0.18 * s, 0.30 * s, 0.24 * s, seed=seed)]
    toes = [(-0.34, -0.12, -0.4), (-0.13, -0.34, -0.12), (0.13, -0.34, 0.12), (0.34, -0.12, 0.4)]
    for i, (dx, dy, rot) in enumerate(toes):
        d.append(blob(cx + dx * s, cy + dy * s, 0.105 * s, 0.14 * s, seed=seed + i + 1, rot=rot))
    return " ".join(d)


def snowflake(cx, cy, R, sw):
    """Six-arm snowflake as stroked paths (returns svg fragment body of path d)."""
    d = []
    for i in range(6):
        a = math.radians(60 * i - 90)
        ex, ey = cx + R * math.cos(a), cy + R * math.sin(a)
        d.append(f"M{f(cx)} {f(cy)} L{f(ex)} {f(ey)}")
        bx, by = cx + 0.58 * R * math.cos(a), cy + 0.58 * R * math.sin(a)
        for s in (-1, 1):
            b = a + s * math.radians(50)
            d.append(f"M{f(bx)} {f(by)} L{f(bx + 0.32 * R * math.cos(b))} {f(by + 0.32 * R * math.sin(b))}")
    return " ".join(d)


# ---------------------------------------------------------------- composition

class Doc:
    def __init__(self, width):
        self.w = width
        self.parts = []
        self.defs = []
        self.y = 0.0
        self._id = 0

    def uid(self, p="i"):
        self._id += 1
        return f"{p}{self._id}"

    def add(self, s):
        self.parts.append(s)

    def path(self, d, fill, extra=""):
        self.add(f'<path d="{d}" fill="{fill}" {extra}/>')

    def headline(self, lines, fname, size, fill, gap, tracking=0.0, x_center=None):
        cx = self.w / 2 if x_center is None else x_center
        cap = cap_height(fname, size)
        for l in lines:
            tw = text_width(l, fname, size, tracking)
            base = self.y + cap
            self.path(text_path(l, fname, size, cx - tw / 2, base, tracking), fill)
            self.y = base + gap
        self.y -= gap
        return cap

    def pill(self, text, fill, size=126, pad_x=70, pad_y=48, sw=18, fname="dmsans700"):
        tw = text_width(text, fname, size)
        cap = cap_height(fname, size)
        h = cap + 2 * pad_y
        w = tw + 2 * pad_x
        x = self.w / 2 - w / 2
        self.add(f'<rect x="{f(x)}" y="{f(self.y + sw / 2)}" width="{f(w)}" height="{f(h)}" rx="{f(h / 2)}" fill="none" stroke="{fill}" stroke-width="{sw}"/>')
        self.path(text_path(text, fname, size, self.w / 2 - tw / 2, self.y + sw / 2 + pad_y + cap), fill)
        self.y += h + sw

    def gap(self, g):
        self.y += g

    def block(self, body, height, dy=0):
        """Place an illustration group whose local origin is its top-left; consumes height."""
        self.add(f'<g transform="translate(0 {f(self.y + dy)})">{body}</g>')
        self.y += height

    def svg(self):
        h = math.ceil(self.y)
        defs = "".join(self.defs)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(self.w)}" height="{h}" '
                f'viewBox="0 0 {int(self.w)} {h}"><defs>{defs}</defs>{"".join(self.parts)}</svg>')
