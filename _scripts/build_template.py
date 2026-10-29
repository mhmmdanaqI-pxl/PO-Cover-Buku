"""Builds the CGSO 2026 A5 master template: vector overlay PDFs, transparent PNGs,
layered PSDs (with real Photoshop guides) and previews for concepts C1-C3.

Run: venv python -I _scripts/build_template.py <workspace>
"""
import os
import sys
import struct
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageCms
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, Group
from psd_tools.constants import Resource
from psd_tools.psd.image_resources import ImageResource, GridGuidesInfo

from typeset import line_paths, draw_contours, shape_line, outline_bounds, FONT_DIR

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "01_Template")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- geometry
MM = 72 / 25.4                      # pt per mm
PXMM = 300 / 25.4                   # px per mm at 300 ppi
TRIM_W, TRIM_H, BLEED = 148.0, 210.0, 3.0
W_MM, H_MM = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
W_PT, H_PT = W_MM * MM, H_MM * MM
W_PX, H_PX = 1819, 2551
SAFE = 10.0                         # mm inside trim (book has rounded corners)
MARGIN = 14.0                       # text/logo margin from trim
CORNER_R = 6.0                      # assumed corner radius, confirm with printer


def pt(x_mm, y_mm):
    """trim-based mm -> canvas pt"""
    return ((x_mm + BLEED) * MM, (y_mm + BLEED) * MM)


def px(v_mm):
    """trim-based mm -> canvas px"""
    return (v_mm + BLEED) * PXMM


JATA_SRC = os.path.join(ROOT, "JATA NEGARA AI (1).ai")
ROUNDEL_SRC = os.path.join(ROOT, "Rahsiakan Rahsia Kerajaan.ai")


def art_bbox(path):
    p = pymupdf.open(path)[0]
    r = pymupdf.Rect()
    for d in p.get_drawings():
        r |= d["rect"]
    return r


JATA_ART = art_bbox(JATA_SRC)
ROUNDEL_ART = art_bbox(ROUNDEL_SRC)

WHITE = (1, 1, 1)
CONCEPTS = {
    "C1": dict(title="Alam Sekitar", accent="#8FD6FF", dark="#062A20",
               bg=[(0.00, "#B7A47E"), (0.38, "#5E9BD0"), (0.62, "#2C7FC4"), (1.00, "#0B3D2E")], bg_angle=-35),
    "C2": dict(title="Keselamatan Dokumen", accent="#E2BC4F", dark="#050D24",
               bg=[(0.00, "#0B1F4B"), (0.45, "#1D3F8F"), (1.00, "#050D24")], bg_angle=0),
    # thumbnail test 28 Oct: amber + navy base read as a variant of C2's gold + navy at phone size;
    # C3 is now the warm cover: sunrise orange accent over a dusk-plum base
    "C3": dict(title="Ekonomi", accent="#FF8A3D", dark="#1E1218",
               bg=[(0.00, "#0E1E44"), (0.50, "#2B3F73"), (0.66, "#E89A3A"), (0.74, "#6A4A4E"), (1.00, "#1E1218")], bg_angle=0),
}


def hex2rgb(h, scale=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 * scale for i in (0, 2, 4))


def hex2rgb255(h):
    return tuple(int(c * 255 + 0.5) for c in hex2rgb(h))


# ---------------------------------------------------------------- layout
# Jata: top-right, right edge on the margin line. Client revision 29 Oct (via Zharief): the Jata Negara
# must be the most prominent mark on the cover and the "Rahsiakan Rahsia Kerajaan" roundel a little
# smaller than it (hierarchy: Jata Negara > Jabatan Perdana Menteri > CGSO > its campaign mark), so the
# Jata goes 28 -> 33 mm and the roundel 38 -> 27 mm. Text sizes follow the 2024 printed sample.
JATA_W = 33.0
JATA_H = JATA_W * JATA_ART.height / JATA_ART.width
RIGHT = TRIM_W - MARGIN
JATA_RECT_MM = (RIGHT - JATA_W, MARGIN, RIGHT, MARGIN + JATA_H)

# Office block (right-aligned on the ink edge), following the 2024/2025 hierarchy
OFFICE_SIZE, WWW_SIZE, OFFICE_LEAD = 8.5, 7.5, 4.1
cap = 0.711 * OFFICE_SIZE / MM
b1 = JATA_RECT_MM[3] + 2.8 + cap
OFFICE_LINES = [
    ("Pejabat Ketua Pegawai", "Bold", OFFICE_SIZE, b1),
    ("Keselamatan Kerajaan Malaysia", "Regular", OFFICE_SIZE, b1 + OFFICE_LEAD),
    ("Jabatan Perdana Menteri", "Regular", OFFICE_SIZE, b1 + 2 * OFFICE_LEAD),
    ("www.cgso.gov.my", "Regular", WWW_SIZE, b1 + 3 * OFFICE_LEAD + 1.4),
]

# Headline: Roboto Black, tracking -10, cap height 6.9 mm as on the 2024 printed sample
# (TANGGUNGJAWAB then measures 83 mm of ink, as on the sample)
HEAD_TRACK = -0.01
HEAD_CAP = 6.9
g, s, _ = shape_line("TANGGUNGJAWAB", "Black", 10, HEAD_TRACK)
_, _, yt, _ = outline_bounds(g, s)
HEAD_SIZE = 10 * (HEAD_CAP * MM) / (-yt)
HEAD_PITCH = 0.93 * HEAD_SIZE / MM          # mm between baselines
LAST_BASE = 188.0
HEAD_LINES = [
    ("LINDUNGI", "accent", LAST_BASE - 3 * HEAD_PITCH),
    ("ASET NEGARA", "accent", LAST_BASE - 2 * HEAD_PITCH),
    ("TANGGUNGJAWAB", "white", LAST_BASE - HEAD_PITCH),
    ("BERSAMA", "white", LAST_BASE),
]


def head_contours():
    out = []
    for text, role, base in HEAD_LINES:
        x, y = pt(MARGIN, base)
        c, b = line_paths(text, "Black", HEAD_SIZE, HEAD_TRACK, "left", x, y)
        out.append((role, c, b))
    return out


HEAD = head_contours()
head_cap_top = {t: b[2] / MM - BLEED for (t, _, _), (_, _, b) in zip(HEAD_LINES, HEAD)}
head_right = {t: b[1] / MM - BLEED for (t, _, _), (_, _, b) in zip(HEAD_LINES, HEAD)}

# Roundel: white brushed disc 27 mm wide (smaller than the Jata, client revision 29 Oct), right edge on
# the margin line, sitting beside LINDUNGI / ASET NEGARA and clear of TANGGUNGJAWAB.
# 29 Oct review: at 27 mm, floating above the headline, it read as a sticker. 29 mm (still smaller than the
# 33 mm Jata) with its top on LINDUNGI's cap line: the headline and the roundel read as one lockup.
ROUND_W = 29.0
ROUND_H = ROUND_W * ROUNDEL_ART.height / ROUNDEL_ART.width
round_left = RIGHT - ROUND_W
gap = 3.0
round_top = head_cap_top["LINDUNGI"]
ROUND_RECT_MM = (round_left, round_top, RIGHT, round_top + ROUND_H)
assert head_right["TANGGUNGJAWAB"] < round_left - gap, "TANGGUNGJAWAB collides with roundel"
assert ROUND_RECT_MM[3] < TRIM_H - SAFE, "roundel outside the safe area"


def rect_pt(r):
    a = pt(r[0], r[1])
    b = pt(r[2], r[3])
    return pymupdf.Rect(a[0], a[1], b[0], b[1])


# ---------------------------------------------------------------- drawing
def draw_jata(page, oc=0):
    page.show_pdf_page(rect_pt(JATA_RECT_MM), pymupdf.open(JATA_SRC), 0, clip=JATA_ART, oc=oc)


def draw_roundel(page, oc=0):
    page.show_pdf_page(rect_pt(ROUND_RECT_MM), pymupdf.open(ROUNDEL_SRC), 0, clip=ROUNDEL_ART, oc=oc)


def draw_office(page, oc=0):
    for text, weight, size, base in OFFICE_LINES:
        x, y = pt(RIGHT, base)
        c, _ = line_paths(text, weight, size, 0.0, "right", x, y)
        draw_contours(page, c, WHITE, oc)


def draw_headline(page, accent, oc=0):
    for role, c, _ in HEAD:
        draw_contours(page, c, hex2rgb(accent) if role == "accent" else WHITE, oc)


def draw_guides_vector(page, oc=0):
    trim = pymupdf.Rect(*pt(0, 0), *pt(TRIM_W, TRIM_H))
    safe = pymupdf.Rect(*pt(SAFE, SAFE), *pt(TRIM_W - SAFE, TRIM_H - SAFE))
    sh = page.new_shape()
    sh.draw_rect(trim)
    sh.finish(color=(0, 0.72, 1), width=0.5, fill=None, oc=oc)
    sh.draw_rect(safe)
    sh.finish(color=(1, 0.18, 0.58), width=0.5, dashes="[3 2] 0", fill=None, oc=oc)
    sh.commit()


def new_doc():
    doc = pymupdf.open()
    page = doc.new_page(width=W_PT, height=H_PT)
    return doc, page


def render(build):
    """Render a single element to a transparent 1819x2551 RGBA image."""
    doc, page = new_doc()
    build(page)
    pix = page.get_pixmap(dpi=300, alpha=True)
    im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    canvas = Image.new("RGBA", (W_PX, H_PX), (0, 0, 0, 0))
    canvas.paste(im.crop((0, 0, min(W_PX, im.width), min(H_PX, im.height))), (0, 0))
    return canvas


# ---------------------------------------------------------------- raster layers
yy, xx = np.mgrid[0:H_PX, 0:W_PX].astype(np.float32)


def gradient_bg(stops, angle_deg):
    """Linear gradient; angle 0 = top->bottom, negative tilts so the top-left starts first."""
    a = np.radians(angle_deg)
    d = (yy / H_PX) * np.cos(a) - (xx / W_PX) * np.sin(a)
    d = (d - d.min()) / (d.max() - d.min())
    pos = np.array([p for p, _ in stops], np.float32)
    cols = np.array([hex2rgb255(c) for _, c in stops], np.float32)
    out = np.stack([np.interp(d, pos, cols[:, i]) for i in range(3)], -1)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")


def shade_bottom(dark):
    t = np.clip((yy / H_PX - 0.58) / 0.42, 0, 1)
    alpha = (t ** 1.6) * 0.88
    return solid_alpha(dark, alpha)


def shade_top_right(dark):
    dx = (xx - W_PX) / W_PX
    dy = yy / W_PX
    r = np.sqrt(dx * dx + dy * dy)
    alpha = np.clip(1 - r / 0.62, 0, 1) ** 1.8 * 0.5
    return solid_alpha(dark, alpha)


def solid_alpha(hexcol, alpha):
    rgb = np.zeros((H_PX, W_PX, 4), np.uint8)
    rgb[..., :3] = hex2rgb255(hexcol)
    rgb[..., 3] = (alpha * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgb, "RGBA")


def roundel_shadow(roundel_rgba):
    a = roundel_rgba.split()[3]
    a = a.point(lambda v: 255 if v > 8 else 0)
    shadow = Image.new("RGBA", a.size, (0, 0, 0, 0))
    blk = Image.new("RGBA", a.size, (0, 0, 0, 255))
    shadow.paste(blk, (0, 0), a)
    shadow = shadow.transform(shadow.size, Image.AFFINE, (1, 0, 0, 0, 1, -int(1.2 * PXMM)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(2.2 * PXMM))
    r, g_, b, al = shadow.split()
    al = al.point(lambda v: int(v * 0.45))
    return Image.merge("RGBA", (r, g_, b, al))


def guides_raster():
    im = Image.new("RGBA", (W_PX, H_PX), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    t0, t1x, t1y = px(0), px(TRIM_W), px(TRIM_H)
    # bleed zone tint
    tint = (255, 40, 40, 46)
    d.rectangle([0, 0, W_PX, t0], fill=tint)
    d.rectangle([0, t1y, W_PX, H_PX], fill=tint)
    d.rectangle([0, t0, t0, t1y], fill=tint)
    d.rectangle([t1x, t0, W_PX, t1y], fill=tint)
    # trim
    d.rectangle([t0, t0, t1x, t1y], outline=(0, 184, 255, 255), width=3)
    # safe (dashed)
    s0, s1x, s1y = px(SAFE), px(TRIM_W - SAFE), px(TRIM_H - SAFE)
    dash, gapl = 22, 14

    def dashed(p0, p1):
        (xa, ya), (xb, yb) = p0, p1
        L = max(abs(xb - xa), abs(yb - ya))
        n = 0
        while n < L:
            e = min(n + dash, L)
            f0, f1 = n / L, e / L
            d.line([(xa + (xb - xa) * f0, ya + (yb - ya) * f0), (xa + (xb - xa) * f1, ya + (yb - ya) * f1)],
                   fill=(255, 46, 148, 255), width=3)
            n += dash + gapl

    dashed((s0, s0), (s1x, s0)); dashed((s1x, s0), (s1x, s1y))
    dashed((s1x, s1y), (s0, s1y)); dashed((s0, s1y), (s0, s0))
    # assumed rounded corners
    r = CORNER_R * PXMM
    for cx, cy, start in [(t0 + r, t0 + r, 180), (t1x - r, t0 + r, 270), (t1x - r, t1y - r, 0), (t0 + r, t1y - r, 90)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start, start + 90, fill=(0, 184, 255, 255), width=3)
    # margin lines for type (thin)
    for xm in (px(MARGIN), px(RIGHT)):
        d.line([(xm, px(SAFE)), (xm, px(TRIM_H - SAFE))], fill=(0, 184, 255, 90), width=1)
    f = ImageFont.truetype(os.path.join(FONT_DIR, "Roboto-Medium.ttf"), 26)
    d.text((t0 + 10, t0 - 32), "BLEED 3 mm  |  TRIM 148 x 210 mm (A5)  |  SAFE 10 mm  |  corner radius ~6 mm (confirm)",
           font=f, fill=(255, 255, 255, 230))
    return im


def guide_resource():
    v = [px(0), px(TRIM_W), px(SAFE), px(TRIM_W - SAFE), px(MARGIN), px(RIGHT)]
    h = [px(0), px(TRIM_H), px(SAFE), px(TRIM_H - SAFE), px(LAST_BASE)]
    data = [(int(round(x * 32)), 0) for x in v] + [(int(round(y * 32)), 1) for y in h]
    return GridGuidesInfo(version=1, horizontal=576, vertical=576, data=data)


def save_psd(path, layers_spec):
    psd = PSDImage.new("RGBA", (W_PX, H_PX))
    for item in layers_spec:
        if item[0] == "group":
            grp = Group.new(psd, item[1])
            for name, img in item[2]:
                PixelLayer.frompil(img, grp, name, 0, 0)
        else:
            PixelLayer.frompil(item[2], psd, item[1], 0, 0)
    psd.image_resources[Resource.RESOLUTION_INFO] = ImageResource(
        key=Resource.RESOLUTION_INFO.value, data=struct.pack(">IHHIHH", 300 << 16, 1, 2, 300 << 16, 1, 2))
    psd.image_resources[Resource.GRID_AND_GUIDES_INFO] = ImageResource(
        key=Resource.GRID_AND_GUIDES_INFO.value, data=guide_resource())
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    psd.image_resources[Resource.ICC_PROFILE] = ImageResource(key=Resource.ICC_PROFILE.value, data=srgb)
    psd.save(path)


# ---------------------------------------------------------------- build
jata_img = render(draw_jata)
office_img = render(draw_office)
roundel_img = render(draw_roundel)
shadow_img = roundel_shadow(roundel_img)
ja = jata_img.split()[3].filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(9))
jata_glow = Image.new("RGBA", jata_img.size, (255, 255, 255, 0))
jata_glow.putalpha(ja.point(lambda v: int(v * 0.5)))
guides_img = guides_raster()
guides_img.save(os.path.join(OUT, "CGSO2026_guides.png"))

for key, c in CONCEPTS.items():
    accent = c["accent"]
    head_img = render(lambda p: draw_headline(p, accent))

    # vector overlay PDF with toggleable layers
    doc, page = new_doc()
    oc_logo = doc.add_ocg("Jata Negara", on=True)
    oc_text = doc.add_ocg("Text", on=True)
    oc_round = doc.add_ocg("Roundel", on=True)
    oc_guides = doc.add_ocg("Guides (do not print)", on=False)
    draw_jata(page, oc_logo)
    draw_office(page, oc_text)
    draw_headline(page, accent, oc_text)
    draw_roundel(page, oc_round)
    draw_guides_vector(page, oc_guides)
    page.set_bleedbox(page.rect)
    page.set_trimbox(pymupdf.Rect(*pt(0, 0), *pt(TRIM_W, TRIM_H)))
    doc.set_metadata({"title": f"CGSO 2026 cover overlay {key} ({c['title']})", "creator": "CGSO 2026 template"})
    doc.save(os.path.join(OUT, f"CGSO2026_overlay_{key}.pdf"), garbage=3, deflate=True)

    # print overlay: same vectors, no guides and no optional-content layers
    pdoc, ppage = new_doc()
    draw_jata(ppage)
    draw_office(ppage)
    draw_headline(ppage, accent)
    draw_roundel(ppage)
    ppage.set_bleedbox(ppage.rect)
    ppage.set_trimbox(pymupdf.Rect(*pt(0, 0), *pt(TRIM_W, TRIM_H)))
    pdoc.save(os.path.join(OUT, f"CGSO2026_overlay_{key}_print.pdf"), garbage=3, deflate=True)

    # transparent overlay PNG (fixed elements only)
    overlay = Image.new("RGBA", (W_PX, H_PX), (0, 0, 0, 0))
    for im in (jata_glow, jata_img, office_img, head_img, shadow_img, roundel_img):
        overlay = Image.alpha_composite(overlay, im)
    overlay.save(os.path.join(OUT, f"CGSO2026_overlay_{key}.png"))

    bg = gradient_bg(c["bg"], c["bg_angle"])
    sb = shade_bottom(c["dark"])
    st = shade_top_right(c["dark"])

    save_psd(os.path.join(OUT, f"CGSO2026_{key}_master.psd"), [
        ("group", "ARTWORK - composite here", [("Background placeholder (replace)", bg)]),
        ("group", "LEGIBILITY SHADES - adjust opacity", [("Shade bottom (headline base)", sb),
                                                         ("Shade top-right (office text)", st)]),
        ("group", "FIXED ELEMENTS - do not edit", [("Jata glow", jata_glow), ("Jata Negara", jata_img), ("Office block", office_img),
                                                   ("Headline", head_img), ("Roundel shadow", shadow_img),
                                                   ("Roundel - Rahsiakan Rahsia Kerajaan", roundel_img)]),
        ("layer", "GUIDES - hide before export", guides_img),
    ])

    prev = bg
    for im in (st, sb, overlay):
        prev = Image.alpha_composite(prev, im)
    prev.convert("RGB").save(os.path.join(OUT, f"preview_{key}.jpg"), quality=92)
    Image.alpha_composite(prev, guides_img).convert("RGB").save(os.path.join(OUT, f"preview_{key}_guides.jpg"), quality=90)

# fonts for editing
fd = os.path.join(OUT, "fonts")
os.makedirs(fd, exist_ok=True)
for f in ("Roboto-Regular.ttf", "Roboto-Medium.ttf", "Roboto-Bold.ttf", "Roboto-Black.ttf", "LICENSE"):
    shutil.copy(os.path.join(FONT_DIR, f), fd)

print(f"headline {HEAD_SIZE:.2f} pt, pitch {HEAD_PITCH:.2f} mm")
print("cap tops:", {k: round(v, 1) for k, v in head_cap_top.items()})
print("right ink:", {k: round(v, 1) for k, v in head_right.items()})
print("jata mm:", [round(v, 2) for v in JATA_RECT_MM], "roundel mm:", [round(v, 2) for v in ROUND_RECT_MM])
print("office baselines:", [round(l[3], 2) for l in OFFICE_LINES])
# geometry for the cover builds (canvas mm, i.e. trim + 3 mm bleed): no hard-coded logo positions there
import json
rr, jr = ROUND_RECT_MM, JATA_RECT_MM
with open(os.path.join(OUT, "CGSO2026_layout.json"), "w") as fh:
    json.dump(dict(roundel_c=[(rr[0] + rr[2]) / 2 + BLEED, (rr[1] + rr[3]) / 2 + BLEED], roundel_r=(rr[2] - rr[0]) / 2,
                   jata=[jr[0] + BLEED, jr[1] + BLEED, jr[2] + BLEED, jr[3] + BLEED],
                   head_cap_top={k: v + BLEED for k, v in head_cap_top.items()},
                   head_right={k: v + BLEED for k, v in head_right.items()}), fh, indent=1)
