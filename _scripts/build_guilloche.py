"""C2 security graphics, built the way banknote/passport engraving is built:
mathematically exact guilloche bands + microtext set in Roboto.

Outputs (02_Vectors/C2_Security):
  C2_guilloche_rosette      140 mm rosette with two microtext rings
  C2_guilloche_wavefield    full-cover (154 x 216 mm) interference line field
  C2_microtext_frame        full-cover microtext border, 8 mm inside trim

Run: venv python -I _scripts/build_guilloche.py <workspace>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pymupdf
from PIL import Image

from typeset import shape_line

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "02_Vectors", "C2_Security")
os.makedirs(OUT, exist_ok=True)

GOLD = "#C9A227"
MM_PT = 72 / 25.4
TAU = 2 * np.pi


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def polyline(xs, ys, closed=True):
    pts = " ".join(f"{fmt(x)} {fmt(y)}" for x, y in zip(xs, ys))
    return f"M{pts}{'Z' if closed else ''}"


def write_outputs(stem, w_mm, h_mm, body, png_ppi, preview_bg="#0B1F4B"):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_mm}mm" height="{h_mm}mm" '
           f'viewBox="0 0 {w_mm} {h_mm}">{body}</svg>')
    with open(os.path.join(OUT, stem + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    pdf = pymupdf.open("pdf", pymupdf.open(stream=svg.encode(), filetype="svg").convert_to_pdf())
    pdf.save(os.path.join(OUT, stem + ".pdf"), garbage=3, deflate=True)
    pix = pdf[0].get_pixmap(dpi=png_ppi, alpha=True)
    im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    im.save(os.path.join(OUT, f"{stem}_{png_ppi}ppi.png"), dpi=(png_ppi, png_ppi))
    bg = Image.new("RGBA", im.size, preview_bg)
    Image.alpha_composite(bg, im).convert("RGB").save(os.path.join(OUT, f"preview_{stem}.jpg"), quality=90)
    return im


# ------------------------------------------------------------------ microtext
def text_glyphs(text, size_mm, tracking=0.0, weight="Medium"):
    """Glyph contours in mm (u right, v up), plus advance positions."""
    size_pt = size_mm * MM_PT
    glyphs, scale, adv = shape_line(text, weight, size_pt, tracking)
    s = scale / MM_PT  # font units -> mm
    out = []
    for ops, gx, gy in glyphs:
        out.append((ops, gx / MM_PT, s))
    return out, adv / MM_PT


def glyph_path(ops, s, place):
    """place(u, v) -> (x, y). Builds SVG path data for one glyph."""
    d = []
    for op in ops:
        if op[0] == "Z":
            d.append("Z")
            continue
        pts = [place(p[0] * s, p[1] * s) for p in op[1:]]
        if op[0] == "M":
            d.append(f"M{fmt(pts[0][0])} {fmt(pts[0][1])}")
        elif op[0] == "L":
            d.append(f"L{fmt(pts[0][0])} {fmt(pts[0][1])}")
        else:
            d.append("C" + " ".join(f"{fmt(x)} {fmt(y)}" for x, y in pts))
    return "".join(d)


def ring_text(phrase, cx, cy, r, cap_mm, weight="Medium"):
    """Phrase repeated around a circle, reading clockwise, glyphs bent to the arc.
    Tracking is solved so a whole number of repeats closes the ring exactly."""
    size = cap_mm / 0.711
    _, adv = text_glyphs(phrase, size, 0.0, weight)
    circ = TAU * r
    reps = max(1, int(circ // (adv * 1.08)))
    n_chars = len(phrase)
    extra = (circ / reps - adv) / n_chars          # mm added after each glyph
    tracking = extra / size
    glyphs, adv = text_glyphs(phrase, size, tracking, weight)
    period = circ / reps
    d = []
    for k in range(reps):
        for ops, gx, s in glyphs:
            base = k * period + gx

            def place(u, v, base=base):
                th = (base + u) / r
                rr = r + v
                return cx + rr * np.sin(th), cy - rr * np.cos(th)

            d.append(glyph_path(ops, s, place))
    return f'<path fill="{GOLD}" d="{"".join(d)}"/>'


def line_text(phrase, x0, y0, length, cap_mm, angle_deg, weight="Medium"):
    """Phrase repeated along a straight segment, fitted exactly to its length."""
    size = cap_mm / 0.711
    _, adv = text_glyphs(phrase, size, 0.0, weight)
    reps = max(1, int(length // (adv * 1.05)))
    tracking = ((length / reps - adv) / len(phrase)) / size
    glyphs, adv = text_glyphs(phrase, size, tracking, weight)
    period = length / reps
    a = np.radians(angle_deg)
    t = (np.cos(a), np.sin(a))          # along the line (y down)
    n = (np.sin(a), -np.cos(a))         # glyph "up"
    d = []
    for k in range(reps):
        for ops, gx, s in glyphs:
            base = k * period + gx

            def place(u, v, base=base):
                along = base + u
                return x0 + along * t[0] + v * n[0], y0 + along * t[1] + v * n[1]

            d.append(glyph_path(ops, s, place))
    return f'<path fill="{GOLD}" d="{"".join(d)}"/>'


# ------------------------------------------------------------------ rosette
def band(cx, cy, r_in, r_out, k, copies, samples, sw, twist=1.0):
    """Family of evenly phase-shifted curves oscillating between two (possibly
    wavy) envelopes. Neighbouring curves cross, producing the woven lattice.
    twist > 0 adds a second, slower harmonic so the lattice cells vary in size."""
    th = np.linspace(0, TAU, samples, endpoint=False)
    ri, ro = r_in(th), r_out(th)
    paths = []
    for i in range(copies):
        ph = i * TAU / copies
        m = np.sin(k * th + ph)
        if twist:
            m = 0.82 * m + 0.18 * np.sin(2 * k * th - ph) * twist
        r = ri + (ro - ri) * (0.5 + 0.5 * m)
        paths.append(polyline(cx + r * np.sin(th), cy - r * np.cos(th)))
    return f'<path fill="none" stroke="{GOLD}" stroke-width="{sw}" stroke-linejoin="round" d="{"".join(paths)}"/>'


def circle(cx, cy, r, sw):
    return f'<circle cx="{cx}" cy="{cy}" r="{fmt(r)}" fill="none" stroke="{GOLD}" stroke-width="{sw}"/>'


def rosette(fine=0.075, hair=0.12):
    S = 140.0
    c = S / 2
    parts = [
        # outer scalloped border: 72 lobes woven between two counter-phased scallops
        band(c, c, lambda t: 62.6 + 0.9 * np.sin(24 * t), lambda t: 68.4 + 0.9 * np.sin(24 * t + np.pi),
             k=72, copies=7, samples=9000, sw=fine, twist=0),
        circle(c, c, 69.6, hair),
        circle(c, c, 61.9, hair),
        # microtext ring between outer border and petals
        ring_text("RAHSIAKAN RAHSIA KERAJAAN • LINDUNGI ASET NEGARA TANGGUNGJAWAB BERSAMA • ",
                  c, c, 60.25, 0.95),
        circle(c, c, 59.2, hair),
        # 12 broad petals: lattice between a circle and a 12-scallop envelope
        band(c, c, lambda t: 46.2 + 0 * t, lambda t: 54.8 + 3.4 * np.cos(12 * t),
             k=60, copies=6, samples=9000, sw=fine, twist=0),
        # rope ring
        band(c, c, lambda t: 44.0 + 0 * t, lambda t: 45.6 + 0 * t, k=120, copies=4, samples=9000, sw=fine, twist=0),
        circle(c, c, 43.4, hair),
        ring_text("PEJABAT KETUA PEGAWAI KESELAMATAN KERAJAAN MALAYSIA • JABATAN PERDANA MENTERI • ",
                  c, c, 42.15, 0.8),
        circle(c, c, 41.2, hair),
        # inner 16-petal rosette, two interleaved families for depth
        band(c, c, lambda t: 22.0 + 2.5 * np.cos(16 * t), lambda t: 39.6 + 0 * t,
             k=40, copies=6, samples=8000, sw=fine, twist=0),
        band(c, c, lambda t: 24.0 + 0 * t, lambda t: 36.0 + 2.0 * np.cos(16 * t + np.pi),
             k=28, copies=3, samples=8000, sw=fine, twist=0),
        circle(c, c, 21.0, hair),
        # centre star-flower (14 lobes, after the Bintang Persekutuan)
        band(c, c, lambda t: 3.0 + 0 * t, lambda t: 19.6 + 0 * t, k=14, copies=8, samples=6000, sw=fine, twist=0),
        circle(c, c, 2.6, hair),
    ]
    return S, "".join(parts)


# ------------------------------------------------------------------ wave field
def wavefield():
    W, H = 154.0, 216.0
    x = np.linspace(-2, W + 2, 700)
    paths_a, paths_b = [], []
    spacing = 1.05
    n = int((H + 8) / spacing)
    for j in range(n):
        y0 = -4 + j * spacing
        ph = j * 0.115
        ya = y0 + 1.6 * np.sin(TAU * x / 38 + ph) + 0.55 * np.sin(TAU * x / 11.5 - 0.6 * ph)
        yb = y0 + 1.6 * np.sin(TAU * x / 38 - ph + 1.3) + 0.55 * np.sin(TAU * x / 13.2 + 0.5 * ph)
        paths_a.append(polyline(x, ya, closed=False))
        paths_b.append(polyline(x, yb, closed=False))
    body = (f'<path fill="none" stroke="{GOLD}" stroke-width="0.07" d="{"".join(paths_a)}"/>'
            f'<path fill="none" stroke="{GOLD}" stroke-width="0.07" d="{"".join(paths_b)}"/>')
    return W, H, body


# ------------------------------------------------------------------ microtext frame
def microtext_frame():
    W, H, B = 154.0, 216.0, 3.0
    inset = 8.0                       # from trim
    clear = 14.0                      # keep corners free (rounded corners)
    cap = 0.9
    phrase = "RAHSIAKAN RAHSIA KERAJAAN • "
    x0, x1 = B + clear, W - B - clear
    y0, y1 = B + clear, H - B - clear
    top_y, bot_y = B + inset, H - B - inset
    left_x, right_x = B + inset, W - B - inset
    parts = [
        line_text(phrase, x0, top_y, x1 - x0, cap, 0),           # top, left -> right
        line_text(phrase, right_x, y0, y1 - y0, cap, 90),        # right, top -> bottom
        line_text(phrase, x1, bot_y, x1 - x0, cap, 180),         # bottom, right -> left
        line_text(phrase, left_x, y1, y1 - y0, cap, 270),        # left, bottom -> top
    ]
    return W, H, "".join(parts)


S, body = rosette()
write_outputs("C2_guilloche_rosette", S, S, body, 600)
S, body = rosette(fine=0.15, hair=0.22)
write_outputs("C2_guilloche_rosette_bold", S, S, body, 600)
W, H, body = wavefield()
write_outputs("C2_guilloche_wavefield", W, H, body, 300)
W, H, body = microtext_frame()
write_outputs("C2_microtext_frame", W, H, body, 300)
print("done")
