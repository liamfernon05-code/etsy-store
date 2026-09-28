"""Build all artwork: python -m artwork.build  (run from the repo root)

Outputs:  artwork/svg/*.svg (vector masters)  artwork/png/*.png (transparent, 300 DPI print files)
          artwork/previews/*.png (flat sweatshirt mockups)  artwork/contact_sheet.png  artwork/REPORT.md
Rendering uses headless Chromium via artwork/render.js (npm i playwright-core; needs a chromium binary).
"""

import json
import os
import re
import subprocess
from pathlib import Path

from PIL import Image

from .designs import DESIGNS

ROOT = Path(__file__).parent
DPI = 300


def lum(hex_):
    r, g, b = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mockup_svg(art_svg, blank_hex, w_px, h_px):
    """Flat sweatshirt with the art at ~3in below collar; 1in = 60px, garment 22in wide."""
    u = 60
    gw = 22 * u
    m = re.search(r'width="(\d+)" height="(\d+)"', art_svg)
    aw, ah = int(m.group(1)), int(m.group(2))
    scale = (aw / DPI) * u / aw  # art px -> mock px
    inner = re.search(r"<svg[^>]*>(.*)</svg>", art_svg, re.S).group(1)
    ox = 360 + (gw - aw * scale) / 2
    oy = 150 + 3 * u
    shade = "#000"
    body = (f'<g fill="{blank_hex}" stroke="{shade}" stroke-opacity=".18" stroke-width="3" stroke-linejoin="round">'
            f'<path d="M{360 + 300} 110 L{360 + gw - 300} 110 L{360 + gw} 140 L{360 + gw + 380} 700 L{360 + gw + 250} 760 L{360 + gw - 10} 470 L{360 + gw - 10} 1250 L{360 + 10} 1250 L{360 + 10} 470 L-{0} 0 Z" fill="none" stroke="none"/>'
            f'<rect x="{360}" y="130" width="{gw}" height="1120" rx="30"/>'
            f'<path d="M360 150 L{360 - 330} 760 L{360 - 210} 830 L{360 + 120} 420 Z"/>'
            f'<path d="M{360 + gw} 150 L{360 + gw + 330} 760 L{360 + gw + 210} 830 L{360 + gw - 120} 420 Z"/>'
            f'<rect x="{360}" y="1180" width="{gw}" height="80" rx="20"/></g>'
            f'<ellipse cx="{360 + gw / 2}" cy="140" rx="200" ry="70" fill="{blank_hex}" stroke="#000" stroke-opacity=".28" stroke-width="4"/>'
            f'<ellipse cx="{360 + gw / 2}" cy="128" rx="150" ry="42" fill="#000" fill-opacity=".16"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_px}" height="{h_px}" viewBox="0 0 {gw + 720} 1400">'
            f'<rect width="100%" height="100%" fill="#ECE9E4"/>{body}'
            f'<g transform="translate({ox:.1f} {oy:.1f}) scale({scale:.5f})">{inner}</g></svg>')


def main():
    for sub in ("svg", "png", "previews"):
        (ROOT / sub).mkdir(exist_ok=True)
    jobs, report, sheet = [], [], []
    for n, slug, draw, colorways in DESIGNS:
        for i, (blank, bhex, T, A) in enumerate(colorways):
            doc = draw(T, A)
            svg = doc.svg()
            stem = f"{n:02d}-{slug}_{blank}"
            (ROOT / "svg" / f"{stem}.svg").write_text(svg)
            m = re.search(r'width="(\d+)" height="(\d+)"', svg)
            w, h = int(m.group(1)), int(m.group(2))
            jobs.append({"svg": str(ROOT / "svg" / f"{stem}.svg"), "png": str(ROOT / "png" / f"{stem}.png"), "w": w, "h": h, "transparent": True})
            mk = mockup_svg(svg, bhex, 1200, int(1200 * 1400 / (22 * 60 + 720)))
            (ROOT / "previews" / f"{stem}.svg").write_text(mk)
            jobs.append({"svg": str(ROOT / "previews" / f"{stem}.svg"), "png": str(ROOT / "previews" / f"{stem}.png"), "w": 1200, "h": int(1200 * 1400 / (22 * 60 + 720)), "transparent": False})
            report.append((n, slug, blank, "primary" if i == 0 else "fallback", w, h, T, A, bhex))
            if i == 0:
                sheet.append(str(ROOT / "previews" / f"{stem}.png"))
    (ROOT / "jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(ROOT / "render.js"), str(ROOT / "jobs.json")], check=True)
    for j in jobs:
        if "/png/" in j["png"]:
            im = Image.open(j["png"])
            im.save(j["png"], dpi=(DPI, DPI))
    # contact sheet (5x2) of primary previews
    thumbs = [Image.open(p).convert("RGB").resize((480, int(480 * 1400 / (22 * 60 + 720)))) for p in sheet]
    tw, th = thumbs[0].size
    cs = Image.new("RGB", (tw * 5, th * 2), "#ECE9E4")
    for k, t in enumerate(thumbs):
        cs.paste(t, ((k % 5) * tw, (k // 5) * th))
    cs.save(ROOT / "contact_sheet.png")
    (ROOT / "jobs.json").unlink()

    lines = ["# Artwork build report", "",
             "Print files are transparent PNG, sRGB, 300 DPI. Contrast uses ESTIMATED blank hexes (re-measure on real samples).", "",
             "| # | Design | Blank | Role | Size (px) | Size (in) | Text ink vs blank | Accent vs blank |", "|---|---|---|---|---|---|---|---|"]
    for n, slug, blank, role, w, h, T, A, bhex in report:
        lines.append(f"| {n} | {slug} | {blank} | {role} | {w}x{h} | {w / DPI:.1f} x {h / DPI:.1f} | {contrast(T, bhex):.2f}:1 | {contrast(A, bhex):.2f}:1 |")
    (ROOT / "REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
