"""Exact Jalur Gemilang (Flag of Malaysia), 1:2.

Geometry: 28 x 14 units (1 unit = one stripe height, 480 px in the viewBox).
14 stripes (7 red from the top, 7 white), blue canton = half the length and
the top 8 stripes, 14-point Bintang Persekutuan and crescent. Star/crescent
path from the public-domain Wikimedia Commons construction.

Run: venv python -I _scripts/build_flag.py <workspace>
"""
import os
import sys

import numpy as np
import pymupdf
from PIL import Image

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "02_Vectors", "Flag")
os.makedirs(OUT, exist_ok=True)

U = 480
W, H = 28 * U, 14 * U
RED, WHITE, BLUE, YELLOW = "#CC0000", "#FFFFFF", "#000066", "#FFCC00"

STAR_CRESCENT = (
    "m4200 720 107 732 414-613-222 706 639-373-506 540 738-59-690 267 690 267-738-59 506 540"
    "-639-373 222 706-414-613-107 732-107-732-414 613 222-706-639 373 506-540-738 59 690-267"
    "-690-267 738 59-506-540 639 373-222-706 414 613z"
    "m-600 30a1280 1280 0 1 0 0 2340 1440 1440 0 1 1 0-2340z"
)


def flag_svg(mirror=False):
    # Stripes under the canton are extended and the canton runs under the 9th
    # stripe so no hairline seams appear when rasterised or printed.
    upper = "".join(f'<rect x="{13 * U}" y="{r * U}" width="{15 * U}" height="{U}"/>' for r in (0, 2, 4, 6))
    lower = "".join(f'<rect x="0" y="{r * U}" width="{W}" height="{U}"/>' for r in (8, 10, 12))
    body = (
        f'<rect width="{W}" height="{H}" fill="{WHITE}"/>'
        f'<g fill="{RED}">{upper}</g>'
        f'<rect width="{14 * U}" height="{8.5 * U:g}" fill="{BLUE}"/>'
        f'<g fill="{RED}">{lower}</g>'
        f'<path fill="{YELLOW}" d="{STAR_CRESCENT}"/>'
    )
    if mirror:
        body = f'<g transform="matrix(-1 0 0 1 {W} 0)">{body}</g>'
    title = "Jalur Gemilang (reverse side)" if mirror else "Jalur Gemilang"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="280mm" height="140mm" '
            f'viewBox="0 0 {W} {H}"><title>{title}</title>{body}</svg>')


def to_pdf_and_png(svg, stem, png_w):
    with open(os.path.join(OUT, stem + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    src = pymupdf.open(stream=svg.encode(), filetype="svg")
    pdf = pymupdf.open("pdf", src.convert_to_pdf())
    pdf.save(os.path.join(OUT, stem + ".pdf"), garbage=3, deflate=True)
    zoom = png_w / pdf[0].rect.width
    pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    pix.save(os.path.join(OUT, f"{stem}_{pix.width}x{pix.height}.png"))
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


front = to_pdf_and_png(flag_svg(False), "Jalur_Gemilang", 6000)
to_pdf_and_png(flag_svg(True), "Jalur_Gemilang_REVERSE", 6000)

# ---- verification -------------------------------------------------------------
a = np.asarray(front).astype(int)
h, w, _ = a.shape
u = h / 14


def is_col(px, hexc, tol=40):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return all(abs(int(px[i]) - c[i]) < tol for i in range(3))


stripes = ["R" if is_col(a[int((r + 0.5) * u), int(w * 0.9)], RED) else
           "W" if is_col(a[int((r + 0.5) * u), int(w * 0.9)], WHITE) else "?" for r in range(14)]
canton_rows = sum(is_col(a[int((r + 0.5) * u), int(w * 0.02)], BLUE) for r in range(14))
canton_w = np.argmax([not is_col(a[int(0.5 * u), x], BLUE) for x in range(w)]) / w
# star: sample a circle around its centre (8.75, 4) units at 0.8 of the outer radius
cx, cy, R = 8.75 * u, 4 * u, 2.5 * u * 0.80
ring = [is_col(a[int(cy + R * np.sin(t)), int(cx + R * np.cos(t))], YELLOW)
        for t in np.linspace(0, 2 * np.pi, 3600, endpoint=False)]
points = sum(1 for i in range(len(ring)) if ring[i] and not ring[i - 1])
print("stripes top->bottom:", "".join(stripes))
print("canton covers stripes:", canton_rows, " canton width / flag length:", round(canton_w, 3))
print("star points:", points, " size:", w, "x", h, " ratio:", round(w / h, 3))
