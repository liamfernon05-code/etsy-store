"""The ten pet-collection designs. Each draw_* function builds one design into a Doc.

Illustrations are hand-constructed vector shapes (see lib.py), not generated images.
T = text ink hex, A = accent ink hex (per colorway).
"""

import math

from .lib import (Doc, blob, catmull, cap_height, f, fit_size, heart, paw, snowflake,
                  star5, text_path, text_width, wobble_poly)

ROUND = 'stroke-linejoin="round" stroke-linecap="round"'


def place(doc: Doc, body: str, height: float, dx: float = 0.0, s: float = 1.0, top: float = 0.0):
    """Drop an illustration drawn around x=0. `top` = local y of its highest point, `height` = local extent."""
    doc.add(f'<g transform="translate({f(doc.w / 2 + dx)} {f(doc.y - top * s)}) scale({s})">{body}</g>')
    doc.y += height * s


def masked(doc: Doc, shapes: str, holes: str, box):
    mid = doc.uid("m")
    x, y, w, h = box
    doc.defs.append(
        f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}">'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/>{holes}</mask>')
    return f'<g mask="url(#{mid})">{shapes}</g>'


def arrowhead(ex, ey, tx, ty, size):
    n = math.hypot(tx, ty)
    ux, uy = tx / n, ty / n
    px, py = -uy, ux
    tip = (ex + ux * size * 0.55, ey + uy * size * 0.55)
    b1 = (ex - ux * size * 0.45 + px * size * 0.55, ey - uy * size * 0.45 + py * size * 0.55)
    b2 = (ex - ux * size * 0.45 - px * size * 0.55, ey - uy * size * 0.45 - py * size * 0.55)
    return f"M{f(tip[0])} {f(tip[1])} L{f(b1[0])} {f(b1[1])} L{f(b2[0])} {f(b2[1])} Z"


# ---------------------------------------------------------------- 1
def draw_01(T, A):
    d = Doc(3150)
    lines = ["RETRIEVER", "IN NAME", "ONLY."]
    size = fit_size(lines, "bowlby", 2900)
    d.headline(lines, "bowlby", size, T, gap=size * 0.13)
    d.gap(170)
    cid = d.uid("c")
    ball = blob(-420, 380, 320, 320, amp=0.012, seed=11)
    d.defs.append(f'<clipPath id="{cid}"><path d="{ball}"/></clipPath>')
    body = (f'<path d="{ball}" fill="{A}" stroke="{T}" stroke-width="24"/>'
            f'<g clip-path="url(#{cid})"><path d="M-716 130 C-500 260 -500 500 -716 630" fill="none" stroke="{T}" stroke-width="22" {ROUND}/>'
            f'<path d="M-124 130 C-340 260 -340 500 -124 630" fill="none" stroke="{T}" stroke-width="22" {ROUND}/></g>'
            f'<path d="M-30 260 C230 40 470 470 880 210" fill="none" stroke="{T}" stroke-width="24" stroke-dasharray="72 58" stroke-linecap="round"/>'
            f'<path d="{arrowhead(880, 210, 410, -260, 150)}" fill="{T}" stroke="{T}" stroke-width="20" {ROUND}/>')
    place(d, body, 690, dx=110, s=1.35, top=40)
    d.gap(160)
    d.pill("the ball is hers now", T)
    return d


# ---------------------------------------------------------------- 2
def draw_02(T, A):
    d = Doc(3000)
    lines = ["SHEDDING", "IS A LOVE", "LANGUAGE."]
    size = fit_size(lines, "fraunces", 2700)
    d.headline(lines, "fraunces", size, T, gap=size * 0.14)
    d.gap(170)
    pins = "".join(f'<line x1="{x}" y1="330" x2="{x}" y2="475" stroke="{T}" stroke-width="42" stroke-linecap="round"/>'
                   for x in range(-300, 301, 100))
    body = (f'<g transform="rotate(-6 0 300)">'
            f'<rect x="330" y="150" width="480" height="130" rx="65" fill="{A}" stroke="{T}" stroke-width="22"/>'
            f'<rect x="-370" y="100" width="740" height="230" rx="72" fill="{A}" stroke="{T}" stroke-width="22"/>'
            f'{pins}'
            f'<path d="{heart(0, 585, 270)}" fill="{A}" stroke="{T}" stroke-width="18" {ROUND}/></g>')
    place(d, body, 680, s=1.3, top=40)
    d.gap(160)
    d.pill("doodle household", T)
    return d


# ---------------------------------------------------------------- 3
def draw_03(T, A):
    d = Doc(3150)
    lines = ["MY HUSKY", "HAS OPINIONS.", "LOUD ONES."]
    size = fit_size(lines, "bowlby", 2900)
    d.headline(lines, "bowlby", size, T, gap=size * 0.13)
    d.gap(200)
    ear_l = "M-360 -120 L-330 -470 L-80 -330 Z"
    ear_r = "M360 -120 L330 -470 L80 -330 Z"
    ear_in_l = "M-300 -200 L-290 -350 L-190 -290 Z"
    ear_in_r = "M300 -200 L290 -350 L190 -290 Z"
    head = blob(0, 20, 400, 350, amp=0.012, seed=21)
    blaze = "M-58 -330 C-50 -200 -120 -100 -78 60 L78 60 C120 -100 50 -200 58 -330 Z"
    shapes = (f'<path d="{ear_l}" fill="{A}" stroke="{A}" stroke-width="40" {ROUND}/>'
              f'<path d="{ear_r}" fill="{A}" stroke="{A}" stroke-width="40" {ROUND}/>'
              f'<path d="{head}" fill="{A}"/>'
              f'<path d="{blaze}" fill="{T}"/>'
              f'<path d="{blob(-215, 150, 190, 160, seed=23)}" fill="{T}"/>'
              f'<path d="{blob(215, 150, 190, 160, seed=24)}" fill="{T}"/>'
              f'<path d="{blob(0, 175, 175, 195, seed=25)}" fill="{T}"/>')
    holes = (f'<path d="{ear_in_l}" fill="#000" stroke="#000" stroke-width="30" {ROUND}/>'
             f'<path d="{ear_in_r}" fill="#000" stroke="#000" stroke-width="30" {ROUND}/>'
             f'<path d="M-250 -20 Q-170 -110 -90 -20" fill="none" stroke="#000" stroke-width="36" {ROUND}/>'
             f'<path d="M250 -20 Q170 -110 90 -20" fill="none" stroke="#000" stroke-width="36" {ROUND}/>'
             f'<path d="{blob(0, 90, 92, 62, seed=27)}" fill="#000"/>'
             f'<path d="{blob(0, 300, 78, 120, seed=28)}" fill="#000"/>')
    head_svg = masked(d, shapes, holes, (-800, -600, 1600, 1200))
    tongue = f'<path d="{blob(0, 360, 52, 62, seed=29)}" fill="{A}"/>'
    waves = ""
    for side in (-1, 1):
        for i, (x, half) in enumerate([(590, 250), (700, 200), (810, 150)]):
            x *= side
            pts = [(x, -half), (x - side * 62, -half / 2), (x, 0), (x - side * 62, half / 2), (x, half)]
            waves += (f'<polyline points="{" ".join(f"{f(px)},{f(py)}" for px, py in pts)}" fill="none" '
                      f'stroke="{T}" stroke-width="32" {ROUND}/>')
    place(d, head_svg + tongue + waves, 940, s=1.3, top=-510)
    d.gap(150)
    d.pill("and she’ll share them at 6 a.m.", T)
    return d


# ---------------------------------------------------------------- 4
def draw_04(T, A):
    d = Doc(3600)
    lines = ["MAXIMUM DOG.", "MINIMUM LEGS."]
    size = fit_size(lines, "bowlby", 3350)
    d.headline(lines, "bowlby", size, T, gap=size * 0.14)
    d.gap(200)
    cid = d.uid("c")
    body_rect = '<rect x="-880" y="100" width="2380" height="380" rx="190"/>'
    d.defs.append(f'<clipPath id="{cid}">{body_rect}</clipPath>')
    shapes = (
        f'<g fill="{T}">{body_rect}'
        f'<path d="{blob(-1130, 320, 310, 235, seed=41, rot=-0.08)}"/>'
        f'<path d="{blob(-1440, 400, 215, 120, seed=42)}"/>'
        f'<rect x="-640" y="440" width="190" height="125" rx="62"/><rect x="-250" y="440" width="190" height="125" rx="62"/>'
        f'<rect x="900" y="440" width="190" height="125" rx="62"/><rect x="1280" y="440" width="190" height="125" rx="62"/></g>'
        f'<path d="M1440 240 C1600 250 1700 150 1730 20" fill="none" stroke="{T}" stroke-width="84" stroke-linecap="round"/>'
        f'<g clip-path="url(#{cid})" fill="{A}"><path d="M60 60 L470 60 L560 520 L150 520 Z"/><path d="M620 60 L780 60 L870 520 L710 520 Z"/></g>'
        f'<path d="{blob(-1010, 430, 125, 235, seed=43, rot=0.25)}" fill="{A}"/>')
    holes = (f'<path d="M-1200 300 Q-1140 350 -1080 300" fill="none" stroke="#000" stroke-width="30" {ROUND}/>'
             f'<path d="{blob(-1600, 385, 46, 38, seed=44)}" fill="#000"/>')
    dog = masked(d, shapes, holes, (-1800, -100, 3800, 800))
    place(d, dog, 620, dx=0)
    d.gap(170)
    d.pill("est. every afternoon", T)
    return d


# ---------------------------------------------------------------- 5
def draw_05(T, A):
    d = Doc(3000)
    circle = (f'<circle cx="0" cy="400" r="385" fill="none" stroke="{T}" stroke-width="28" stroke-dasharray="122 64.8"/>'
              f'<path d="{paw(0, 380, 420)}" fill="{A}"/>')
    place(d, circle, 820)
    d.gap(170)
    l1 = ["YES, SHE’S", "REACTIVE."]
    l2 = ["NO, YOU CAN’T", "SAY HI."]
    size = fit_size(l1 + l2, "dmsans800", 2700)
    d.headline(l1, "dmsans800", size, T, gap=size * 0.16)
    d.gap(size * 0.42)
    d.headline(l2, "dmsans800", size, T, gap=size * 0.16)
    d.gap(170)
    d.pill("thank you for the space.", T)
    return d


# ---------------------------------------------------------------- 6
def draw_06(T, A):
    d = Doc(3000)
    lines = ["I ONLY MEANT", "TO FOSTER."]
    size = fit_size(lines, "fraunces", 2750)
    d.headline(lines, "fraunces", size, T, gap=size * 0.15)
    d.gap(190)
    hs = f'<path d="{heart(0, 560, 1180)}" fill="{A}"/>'
    house = ('M-190 450 L0 260 L190 450 L150 450 L150 650 L-150 650 L-150 450 Z')
    holes = f'<path d="{house}" fill="#000" stroke="#000" stroke-width="24" {ROUND}/>'
    body = masked(d, hs, holes, (-800, -100, 1600, 1300))
    place(d, body, 1120, dx=0)
    d.gap(150)
    d.pill("foster fail, officially.", T)
    return d


# ---------------------------------------------------------------- 7
def draw_07(T, A):
    d = Doc(3000)
    lines = ["SLOW WALKS.", "SOFT BEDS.", "GOOD DOG."]
    size = fit_size(lines, "fraunces", 2750)
    d.headline(lines, "fraunces", size, T, gap=size * 0.15)
    d.gap(170)
    body = (f'<ellipse cx="-520" cy="150" rx="195" ry="130" transform="rotate(-18 -520 150)" fill="none" stroke="{T}" stroke-width="46"/>'
            f'<path d="M-345 215 C-120 430 110 30 390 200 C560 300 600 410 620 470" fill="none" stroke="{T}" stroke-width="46" {ROUND}/>'
            f'<path d="{heart(660, 640, 360)}" fill="{A}" stroke="{T}" stroke-width="26" {ROUND}/>')
    place(d, body, 780, dx=-60, s=1.25, top=10)
    d.gap(150)
    d.pill("senior dog parent.", T)
    return d


# ---------------------------------------------------------------- 8
def draw_08(T, A):
    d = Doc(3000)
    lines = ["CAT REVIEW:", "FIVE STARS.", "NO NOTES."]
    size = fit_size(lines, "alfa", 2750)
    d.headline(lines, "alfa", size, T, gap=size * 0.14)
    d.gap(150)
    stars = "".join(f'<path d="{star5(x, 175, 175, seed=50 + i)}" fill="{A}" stroke="{T}" stroke-width="22" {ROUND}/>'
                    for i, x in enumerate(range(-800, 801, 400)))
    place(d, stars, 350, s=1.1)
    d.gap(110)
    shapes = (f'<g fill="{T}">'
              f'<path d="M-190 110 L-175 -60 L-30 40 Z" stroke="{T}" stroke-width="40" {ROUND}/>'
              f'<path d="M190 110 L175 -60 L30 40 Z" stroke="{T}" stroke-width="40" {ROUND}/>'
              f'<path d="{blob(0, 230, 200, 175, seed=61)}"/>'
              f'<path d="{blob(0, 620, 235, 320, seed=62)}"/></g>'
              f'<path d="M205 820 C430 850 500 570 390 420" fill="none" stroke="{T}" stroke-width="80" stroke-linecap="round"/>')
    holes = (f'<path d="{blob(-78, 220, 21, 34, seed=63)}" fill="#000"/><path d="{blob(78, 220, 21, 34, seed=64)}" fill="#000"/>'
             f'<path d="M-24 285 L24 285 L0 315 Z" fill="#000" stroke="#000" stroke-width="12" {ROUND}/>'
             f'<line x1="-72" y1="800" x2="-72" y2="930" stroke="#000" stroke-width="18" stroke-linecap="round"/>'
             f'<line x1="72" y1="800" x2="72" y2="930" stroke="#000" stroke-width="18" stroke-linecap="round"/>')
    cat = masked(d, shapes, holes, (-700, -150, 1400, 1300))
    place(d, cat, 1010, s=1.2, top=-70)
    d.gap(150)
    d.pill("the house passed inspection.", T)
    return d


# ---------------------------------------------------------------- 9
def draw_09(T, A):
    d = Doc(3000)
    l1 = ["MEETING", "CANCELLED."]
    l2 = ["CAT HAS", "DECIDED."]
    size = fit_size(l1 + l2, "dmsans800", 2500)
    d.headline(l1, "dmsans800", size, T, gap=size * 0.16)
    d.gap(size * 0.42)
    d.headline(l2, "dmsans800", size, T, gap=size * 0.16)
    d.gap(190)
    cid = d.uid("c")
    d.defs.append(f'<clipPath id="{cid}"><rect x="-675" y="110" width="1350" height="1090" rx="90"/></clipPath>')
    cal = (f'<rect x="-675" y="110" width="1350" height="1090" rx="90" fill="none" stroke="{T}" stroke-width="28"/>'
           f'<g clip-path="url(#{cid})"><rect x="-690" y="100" width="1380" height="240" fill="{T}"/></g>'
           f'<line x1="-360" y1="40" x2="-360" y2="190" stroke="{T}" stroke-width="56" stroke-linecap="round"/>'
           f'<line x1="360" y1="40" x2="360" y2="190" stroke="{T}" stroke-width="56" stroke-linecap="round"/>'
           f'<line x1="-225" y1="340" x2="-225" y2="1190" stroke="{T}" stroke-width="24"/>'
           f'<line x1="225" y1="340" x2="225" y2="1190" stroke="{T}" stroke-width="24"/>'
           f'<line x1="-670" y1="622" x2="670" y2="622" stroke="{T}" stroke-width="24"/>'
           f'<line x1="-670" y1="905" x2="670" y2="905" stroke="{T}" stroke-width="24"/>'
           f'<path d="M930 30 C700 230 330 330 130 690 C50 840 170 960 110 1090 C70 1170 -20 1150 10 1070" fill="none" stroke="{T}" stroke-width="150" stroke-linecap="round"/>'
           f'<path d="M930 30 C700 230 330 330 130 690 C50 840 170 960 110 1090 C70 1170 -20 1150 10 1070" fill="none" stroke="{A}" stroke-width="102" stroke-linecap="round"/>')
    place(d, cal, 1260)
    d.gap(150)
    d.pill("sorry, I’m pinned.", T)
    return d


# ---------------------------------------------------------------- 10
def sock(T, A, clip_id, seed):
    outline = ("M0 0 L300 0 L300 420 C300 470 360 480 440 500 C560 530 590 640 500 690 "
               "C420 735 300 740 120 740 C20 740 -30 700 -20 620 C-10 560 0 520 0 470 Z")
    return outline, (
        f'<g clip-path="url(#{clip_id})">'
        f'<rect x="-60" y="0" width="720" height="780" fill="{T}"/>'
        f'<rect x="-60" y="150" width="420" height="70" fill="{A}"/>'
        f'<rect x="-60" y="290" width="420" height="70" fill="{A}"/>'
        f'<path d="M-40 560 C60 520 120 560 140 640 C160 720 60 760 -40 760 Z" fill="{A}"/>'
        f'<path d="M400 480 C480 490 580 560 590 640 C600 720 470 740 400 720 Z" fill="{A}"/>'
        f'<path d="{paw(250, 555, 150, seed=seed)}" fill="{A}"/></g>')


def draw_10(T, A):
    d = Doc(3150)
    lines = ["HEATED", "BY DOG."]
    size = fit_size(lines, "bowlby", 2900)
    d.headline(lines, "bowlby", size, T, gap=size * 0.10)
    d.gap(200)
    c1, c2 = d.uid("s"), d.uid("s")
    outline, s1 = sock(T, A, c1, 71)
    _, s2 = sock(T, A, c2, 73)
    d.defs.append(f'<clipPath id="{c1}"><path d="{outline}"/></clipPath><clipPath id="{c2}"><path d="{outline}"/></clipPath>')
    sock1 = f'<g transform="translate(-620 60) rotate(-7 150 370)">{s1}</g>'
    sock2 = f'<g transform="translate(120 60) rotate(6 150 370)">{s2}</g>'
    flakes = "".join(f'<path d="{snowflake(x, y, R, 0)}" fill="none" stroke="{A}" stroke-width="26" {ROUND}/>'
                     for x, y, R in [(-1160, 260, 190), (1180, 200, 170), (1060, 700, 120)])
    body = masked(d, sock1 + sock2 + flakes, "", (-1500, -50, 3000, 900))
    place(d, body, 860, s=1.1, top=0)
    d.gap(160)
    d.pill("warm feet. zero regrets.", T)
    return d


DESIGNS = [
    # n, slug, draw fn, [(blank_name, blank_hex, text_ink, accent_ink), ...] primary first
    (1, "retriever-in-name-only", draw_01, [("sand", "#D6C7A8", "#3A230D", "#7E4A0C"), ("sport-grey", "#A4A7AB", "#3A230D", "#7E4A0C")]),
    (2, "shedding-love-language", draw_02, [("sport-grey", "#A4A7AB", "#14284A", "#7A2A14"), ("ash", "#C4C5C8", "#14284A", "#7A2A14")]),
    (3, "husky-opinions", draw_03, [("black", "#191919", "#F4E9D0", "#A9CCE6")]),
    (4, "maximum-dog", draw_04, [("forest", "#1C3A2B", "#F1E3C8", "#EE8A47"), ("black", "#191919", "#F1E3C8", "#EE8A47")]),
    (5, "reactive-dog", draw_05, [("black", "#191919", "#FFFFFF", "#F5C518"), ("navy", "#1C2842", "#FFFFFF", "#F5C518")]),
    (6, "only-meant-to-foster", draw_06, [("maroon", "#58202B", "#F6E7D8", "#F2B8B0"), ("black", "#191919", "#F6E7D8", "#F2B8B0")]),
    (7, "slow-walks", draw_07, [("ash", "#C4C5C8", "#2B2B2B", "#3F6244"), ("sport-grey", "#A4A7AB", "#1F1F1F", "#3F6244")]),
    (8, "cat-review", draw_08, [("sand", "#D6C7A8", "#3E2A1E", "#8F3D06"), ("sport-grey", "#A4A7AB", "#3E2A1E", "#8F3D06")]),
    (9, "meeting-cancelled", draw_09, [("navy", "#1C2842", "#FFFFFF", "#E9B949"), ("black", "#191919", "#FFFFFF", "#E9B949")]),
    (10, "heated-by-dog", draw_10, [("black", "#191919", "#F4E9D0", "#EF5F52"), ("forest", "#1C3A2B", "#F4E9D0", "#EF5F52")]),
]
