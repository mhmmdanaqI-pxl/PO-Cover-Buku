"""C3 'Berhemah Hari Ini, Teguh Esok' graphics, positioned on the template canvas
(154 x 216 mm incl. bleed, 1819 x 2551 px):

  C3_rising_line     tapered metallic-gold growth line with data-point nodes
  C3_protective_arc  thin double arc over the Istana (the 'protective dome')

Each comes as an editable SVG plus separate crisp and glow PNG layers, so the
glow strength is set in Photoshop (Screen / Linear Dodge, low opacity).

Run: venv python -I _scripts/build_growth.py <workspace>
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "02_Vectors", "C3_Growth")
os.makedirs(OUT, exist_ok=True)

W_MM, H_MM = 154.0, 216.0
W_PX, H_PX = 1819, 2551
PXMM = 300 / 25.4
SS = 4                                   # supersampling for anti-aliasing

GOLD_STOPS = [(0.0, "#6E4510"), (0.35, "#B4852B"), (0.72, "#E6B44A"), (1.0, "#FFE4A3")]
NODE = "#FFE7B0"
ARC = "#D9B24C"

# roundel (canvas mm) from the template, used for a clearance check
ROUNDEL_C, ROUNDEL_R = (118.0, 151.8), 19.3


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def grad(s, stops):
    pos = [p for p, _ in stops]
    cols = np.array([hexrgb(c) for _, c in stops])
    return np.stack([np.interp(s, pos, cols[:, i]) for i in range(3)], -1)


def bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    pts = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
    return pts


def frame(pts):
    d = np.gradient(pts, axis=0)
    tan = d / np.linalg.norm(d, axis=1, keepdims=True)
    nrm = np.stack([-tan[:, 1], tan[:, 0]], 1)        # left normal (y down)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    return tan, nrm, s / s[-1]


def fmt(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def path_d(poly):
    return "M" + " ".join(f"{fmt(x)} {fmt(y)}" for x, y in poly) + "Z"


def canvas(scale=SS, mode="RGBA"):
    return Image.new(mode, (W_PX * scale, H_PX * scale), (0, 0, 0, 0) if mode == "RGBA" else 0)


def to_px(p, scale=SS):
    return [(x * PXMM * scale, y * PXMM * scale) for x, y in p]


def down(im):
    return im.resize((W_PX, H_PX), Image.LANCZOS)


def glow_from(alpha, color, radius_mm, strength):
    a = alpha.filter(ImageFilter.GaussianBlur(radius_mm * PXMM))
    a = a.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", alpha.size, tuple(int(c) for c in hexrgb(color)) + (0,))
    g.putalpha(a)
    return g


def save_preview(layers, stem):
    tpl = Image.open(os.path.join(ROOT, "01_Template", "preview_C3.jpg")).convert("RGBA")
    for im in layers:
        tpl = Image.alpha_composite(tpl, im)
    tpl.convert("RGB").save(os.path.join(OUT, f"preview_{stem}.jpg"), quality=90)


# ------------------------------------------------------------------ rising line (a real line chart)
# Data points in canvas mm: emerges from behind the engineer, climbs over the tanker's bow, a small
# dip (the energy shock), then a prudent recovery and steady growth to the upper right, above the
# tanker's bridge, the power station and the TNB tower. Straight segments, nodes, drop lines and a
# faint area fill are what make it read as a chart rather than a light streak.
# 9.5 review: the line used to run off the top-right edge behind the address block and never visibly
# ended, so it could read as "prices rising". It now ends below the address block in an arrowhead:
# a dip, a recovery, and growth that lands, unambiguously positive.
CHART = [(-2.0, 112.0), (20.0, 104.0), (36.0, 84.0), (50.0, 89.0), (68.0, 75.0), (100.0, 68.0),
         (124.0, 62.5)]
NODE_IDX = (2, 3, 4, 5)                          # visible points (0-1 sit behind the platform); the last is the arrow
ARROW_LEN, ARROW_W = 6.0, 5.4                    # mm
# C3 heads (canvas mm); nodes must stay clear of faces
HEADS = [(88, 111), (114, 110)]                         # the oil-and-gas crew (review 28 Oct)
KEEP_CLEAR = [(78, 80, 108, 100), (118, 74, 150, 95)]   # tanker bridge + mast, tower top + chimneys (x0, y0, x1, y1)


def rising_line():
    P = np.array(CHART)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    sv = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()           # 0..1 along the chart
    pts = np.concatenate([np.linspace(P[i], P[i + 1], max(2, int(seg[i] * 8)), endpoint=False)
                          for i in range(len(P) - 1)] + [P[-1:]])
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    s /= s[-1]
    width = 0.6 + 2.0 * s ** 1.3                                     # mm: a bold chart stroke that reads at thumbnail
    nodes = [(P[i][0], P[i][1], sv[i]) for i in NODE_IDX]
    # clearances: roundel (+3 mm), headline block (y >= 155), faces, tanker bridge, tower top
    dist = np.linalg.norm(pts - np.array(ROUNDEL_C), axis=1) - width / 2
    assert dist.min() > ROUNDEL_R + 3, f"line too close to roundel: {dist.min():.1f}"
    assert pts[:, 1].max() + width.max() / 2 < 155, "line touches headline"
    for x, y, _ in nodes:
        assert min(np.hypot(x - hx, y - hy) for hx, hy in HEADS) > 12, f"node ({x}, {y}) too close to a face"
        assert not any(x0 - 4 < x < x1 + 4 and y0 - 4 < y < y1 + 4 for x0, y0, x1, y1 in KEEP_CLEAR), (x, y)

    def stroke(draw, extra=0.0, fill=255):
        # a chain of overlapping discs (16 per mm): one smooth envelope with round joins. Thick
        # per-segment lines left a ladder of notches along the heavy end of the stroke.
        dense = np.concatenate([np.linspace(P[i], P[i + 1], max(2, int(seg[i] * 16)), endpoint=False)
                                for i in range(len(P) - 1)] + [P[-1:]])
        ds = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))])
        ds /= ds[-1]
        for (x, y), f in zip(dense, ds):
            j = min(len(pts) - 1, int(np.searchsorted(s, f)))
            r = max(0.5, (width[j] + extra) * PXMM * SS / 2)
            (cx, cy), = to_px([(x, y)])
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill if not callable(fill) else fill(j))

    # --- gold stroke (gradient along the chart) + a brighter core for a metallic edge
    base = grad(s, GOLD_STOPS)
    rgb = canvas(mode="RGB")
    dr = ImageDraw.Draw(rgb)
    stroke(dr, fill=lambda i: tuple(int(c) for c in base[i]))
    core = canvas(mode="L")
    stroke(ImageDraw.Draw(core), extra=-0.55 * 1.0, fill=255)
    rgb = Image.composite(Image.new("RGB", rgb.size, tuple(int(c) for c in hexrgb("#FFE9B8"))), rgb,
                          core.point(lambda v: int(v * 0.45)))
    mask = canvas(mode="L")
    stroke(ImageDraw.Draw(mask), fill=255)
    # arrowhead on the last segment: the chart lands, pointing up and on
    u = (P[-1] - P[-2]) / np.linalg.norm(P[-1] - P[-2])
    n = np.array([-u[1], u[0]])
    tip = P[-1] + u * ARROW_LEN * 0.75
    back = P[-1] - u * ARROW_LEN * 0.25
    tri = to_px([tuple(tip), tuple(back + n * ARROW_W / 2), tuple(back - n * ARROW_W / 2)])
    ImageDraw.Draw(rgb).polygon(tri, fill=tuple(int(c) for c in hexrgb(GOLD_STOPS[-1][1])))
    ImageDraw.Draw(mask).polygon(tri, fill=255)

    # --- nodes (dot + ring) and drop lines to the baseline (hairline, fading down)
    node_mask = canvas(mode="L")
    nd = ImageDraw.Draw(node_mask)
    drop_mask = canvas(mode="L")
    dd = ImageDraw.Draw(drop_mask)
    for x, y, f in nodes:
        r1, r2 = 0.85 + 0.3 * f, 1.8 + 0.5 * f
        (cx, cy), = to_px([(x, y)])
        nd.ellipse([cx - r1 * PXMM * SS, cy - r1 * PXMM * SS, cx + r1 * PXMM * SS, cy + r1 * PXMM * SS], fill=255)
        nd.ellipse([cx - r2 * PXMM * SS, cy - r2 * PXMM * SS, cx + r2 * PXMM * SS, cy + r2 * PXMM * SS],
                   outline=215, width=int(0.14 * PXMM * SS) + 1)
        for k in range(40):                                           # 16 mm drop, 55% -> 0
            ya, yb = y + r2 + 0.4 + k * 0.4, y + r2 + 0.4 + (k + 1) * 0.4
            dd.line(to_px([(x, ya), (x, yb)]), fill=int(255 * 0.55 * (1 - k / 40)), width=int(0.12 * PXMM * SS) + 1)

    # --- faint area fill under the chart (gold, fading 20 mm down, fading in from the left)
    yy = (np.arange(H_PX, dtype=np.float32)[:, None] + 0.5) / PXMM
    xx = (np.arange(W_PX, dtype=np.float32)[None, :] + 0.5) / PXMM
    yl = np.interp(xx, P[:, 0], P[:, 1])
    area = np.clip(1 - (yy - yl) / 26, 0, 1) * (yy > yl + 0.6) * np.clip((xx - 44) / 26, 0, 1) * 0.30
    area_l = Image.fromarray((area * 255).astype(np.uint8), "L")

    gold = tuple(int(c) for c in hexrgb("#E6B44A"))
    line = Image.new("RGBA", (W_PX, H_PX), gold + (0,))
    line.putalpha(area_l)
    # dark keyline under the stroke and nodes so the chart reads over the cream facade and bright sky
    key = Image.composite(Image.new("L", mask.size, 255), mask, node_mask)
    key = down(Image.merge("RGBA", (*Image.new("RGB", key.size, (0, 0, 0)).split(), key)))
    key_a = key.split()[3].filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    kl = Image.new("RGBA", (W_PX, H_PX), (26, 16, 24, 0))
    kl.putalpha(key_a.point(lambda v: int(v * 0.55)))
    line = Image.alpha_composite(line, kl)
    dl = Image.new("RGBA", drop_mask.size, gold + (0,))
    dl.putalpha(drop_mask)
    stroke_l = Image.merge("RGBA", (*rgb.split(), mask))
    nl = Image.new("RGBA", node_mask.size, tuple(int(c) for c in hexrgb(NODE)) + (0,))
    nl.putalpha(node_mask)
    line = Image.alpha_composite(line, down(Image.alpha_composite(Image.alpha_composite(dl, stroke_l), nl)))
    line.save(os.path.join(OUT, "C3_rising_line_300ppi.png"), dpi=(300, 300))

    glow_src = down(Image.composite(Image.new("L", mask.size, 255), mask, node_mask))
    glow = Image.alpha_composite(glow_from(glow_src, "#FFC24D", 1.6, 0.8),
                                 glow_from(glow_src, "#FFD98A", 0.45, 0.7))
    glow.save(os.path.join(OUT, "C3_rising_line_glow_300ppi.png"), dpi=(300, 300))

    # --- SVG (editable in Illustrator)
    _, nrm, _ = frame(pts)
    left = pts + nrm * (width / 2)[:, None]
    right = pts - nrm * (width / 2)[:, None]
    ribbon = np.concatenate([left, right[::-1]])
    p0, p3 = P[0], P[-1]
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GOLD_STOPS)
    area_pts = [(x, y) for x, y in P if x >= 44] + [(P[-1][0], P[-1][1] + 20), (44, np.interp(44, P[:, 0], P[:, 1]) + 20)]
    area_pts.insert(0, (44, float(np.interp(44, P[:, 0], P[:, 1]))))
    drops = "".join(f'<line x1="{fmt(x)}" y1="{fmt(y + 1.7 + 0.4 * f)}" x2="{fmt(x)}" y2="{fmt(y + 17.7)}" '
                    f'stroke="url(#drop)" stroke-width="0.12"/>' for x, y, f in nodes)
    node_svg = "".join(
        f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(0.85 + 0.3 * f)}" fill="{NODE}"/>'
        f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(1.8 + 0.5 * f)}" fill="none" stroke="{NODE}" '
        f'stroke-opacity="0.85" stroke-width="0.14"/>' for x, y, f in nodes)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_MM}mm" height="{H_MM}mm" viewBox="0 0 {W_MM} {H_MM}">'
           f'<defs><linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="{fmt(p0[0])}" y1="{fmt(p0[1])}" '
           f'x2="{fmt(p3[0])}" y2="{fmt(p3[1])}">{stops}</linearGradient>'
           f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E6B44A" '
           f'stop-opacity="0.30"/><stop offset="1" stop-color="#E6B44A" stop-opacity="0"/></linearGradient>'
           f'<linearGradient id="drop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E6B44A" '
           f'stop-opacity="0.55"/><stop offset="1" stop-color="#E6B44A" stop-opacity="0"/></linearGradient></defs>'
           f'<path fill="url(#area)" d="{path_d(area_pts)}"/>{drops}'
           f'<path fill="url(#gold)" d="{path_d(ribbon[::2])}"/>{node_svg}</svg>')
    with open(os.path.join(OUT, "C3_rising_line.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    return line, glow


# ------------------------------------------------------------------ protective arc
def protective_arc():
    cx, cy, R = 77.0, 175.0, 108.0
    th = np.linspace(np.radians(-48), np.radians(48), 3000)   # 0 = straight up
    def ring(r):
        return np.stack([cx + r * np.sin(th), cy - r * np.cos(th)], 1)
    fade = np.clip(np.minimum(th - th[0], th[-1] - th) / np.radians(14), 0, 1)
    strokes = [(R, 0.30, 1.0), (R - 1.1, 0.12, 0.7)]
    mask = canvas(mode="L")
    d = ImageDraw.Draw(mask)
    for r, w, op in strokes:
        p = ring(r)
        for i in range(len(p) - 1):
            v = int(255 * op * fade[i])
            if v:
                d.line(to_px([p[i], p[i + 1]]), fill=v, width=max(1, int(w * PXMM * SS)))
    mask = mask.resize((W_PX, H_PX), Image.LANCZOS)
    arc = Image.new("RGBA", (W_PX, H_PX), tuple(int(c) for c in hexrgb(ARC)) + (0,))
    arc.putalpha(mask)
    arc.save(os.path.join(OUT, "C3_protective_arc_300ppi.png"), dpi=(300, 300))
    glow = glow_from(mask, "#FFC24D", 1.5, 0.8)
    glow.save(os.path.join(OUT, "C3_protective_arc_glow_300ppi.png"), dpi=(300, 300))

    x0, y0 = ring(R)[0]
    x1, y1 = ring(R)[-1]
    def arc_path(r):
        a, b = ring(r)[0], ring(r)[-1]
        return f"M{fmt(a[0])} {fmt(a[1])}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(b[0])} {fmt(b[1])}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_MM}mm" height="{H_MM}mm" viewBox="0 0 {W_MM} {H_MM}">'
           f'<defs><linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="{fmt(x0)}" y1="0" x2="{fmt(x1)}" y2="0">'
           f'<stop offset="0" stop-color="{ARC}" stop-opacity="0"/><stop offset="0.16" stop-color="{ARC}"/>'
           f'<stop offset="0.84" stop-color="{ARC}"/><stop offset="1" stop-color="{ARC}" stop-opacity="0"/>'
           f'</linearGradient></defs>'
           f'<path fill="none" stroke="url(#fade)" stroke-width="0.30" d="{arc_path(R)}"/>'
           f'<path fill="none" stroke="url(#fade)" stroke-opacity="0.7" stroke-width="0.12" d="{arc_path(R - 1.1)}"/>'
           f'</svg>')
    with open(os.path.join(OUT, "C3_protective_arc.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    return arc, glow


line, line_glow = rising_line()
arc, arc_glow = protective_arc()
save_preview([arc_glow, arc, line_glow, line], "C3_growth")
print("done")
