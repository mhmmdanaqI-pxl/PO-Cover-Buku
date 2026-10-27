"""Cover C2 - Keselamatan Dokumen: 'Daulat Terpelihara, Rahsia Terjaga'.

Blue hour. Big Jalur Gemilang across the top (as 2025), Istana under a gold
guilloche halo, Su-30MKM formation, people row (student, police, soldier,
researcher), the classified dossier as the headline base.
Run: venv python -I _scripts/build_C2.py <workspace> [fast]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np
from PIL import Image

import comp as C
from comp import W, H, mm

ROOT = sys.argv[1]
FAST = len(sys.argv) > 2
OUT = os.path.join(ROOT, "04_Final", "C2")
os.makedirs(OUT, exist_ok=True)
cut = lambda n: C.load_rgba(os.path.join(ROOT, "03_Cutouts", n))
WARM = "#FFB65C"
yy = np.arange(H, dtype=np.float32)[:, None] / mm(1)
xx = np.arange(W, dtype=np.float32)[None, :] / mm(1)


def full(rgb, a=None):
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = 1.0 if a is None else a
    return out


# ------------------------------------------------------------------ sky
stops = [(0, "#08132F"), (45, "#11285A"), (95, "#1E3B78"), (128, "#33508C"), (150, "#2A3F74"), (216, "#0A1430")]
ys = np.array([s for s, _ in stops], np.float32)
cols = np.array([C.hexf(c) for _, c in stops])
sky = np.stack([np.interp(yy[:, 0], ys, cols[:, i]) for i in range(3)], -1)[:, None, :].repeat(W, 1)
glow = C.radial(77, 132, 95, 1.6, aspect=1.6)
sky = C.blend(sky, np.broadcast_to(C.hexf("#6C6A8E"), sky.shape), glow, "screen", 0.35)
rng = np.random.default_rng(3)
cloud = C.blur(rng.normal(0, 1, (H, W)).astype(np.float32), 70)
sky = sky * (1 + cloud[..., None] / (cloud.std() + 1e-6) * 0.018)
st = C.Stack("Sky - blue hour", sky)

# ------------------------------------------------------------------ big flag (as 2025)
flag = cut("FLAG_waving.png")
flag[..., :3] = C.exposure(flag[..., :3], -0.5)
flag[..., :3] = C.tint_shadows_highlights(flag[..., :3], shadow=(-0.02, -0.01, 0.05), highlight=(0.05, 0.03, -0.01))
# backdrop, not hero: blue-hour contrast so the dome + halo lead, but the reds stay red
# (a washed-out national flag reads as faded on a government cover)
flag[..., :3] = C.saturation(flag[..., :3], 1.1)
flag[..., :3] = C.curves(flag[..., :3], [(0, 0.03), (0.5, 0.43), (1, 0.8)])
flag[..., :3] = flag[..., :3] * 0.94 + C.hexf("#16285A") * 0.06
# canton edge ~3.5 mm left of the spire (as C1/C3); at -26 it ran 1 mm from the needle and read as a slab
fl = C.place(flag, left_mm=-29, top_mm=-10, width_mm=192, rotate=4)
fl[..., :3] = C.blur(fl[..., :3], 0.9)                              # slight depth softness behind the palace
fl[..., 3] *= np.clip(1 - (xx - 96) / 70, 0.3, 1) * np.clip((132 - yy) / 30, 0, 1) * 0.92
fl = C.rim_light(fl, WARM, direction=(-1, -0.3), width_px=6, strength=0.2)
st.add("Jalur Gemilang (exact vector on fabric)", fl)

# ------------------------------------------------------------------ istana geometry
IST_W_MM = 200.0
ist_src = cut("ISTANA_base.png")
sc = mm(IST_W_MM) / ist_src.shape[1]
IST_LEFT = 77 - 1813.6 * sc / mm(1)
IST_TOP = 47 - 171 * sc / mm(1)
DOME_CX, DOME_CY = 77.0, IST_TOP + 727.7 * sc / mm(1)

# ------------------------------------------------------------------ guilloche halo (lower, clears the jets)
ros = C.load_rgba(os.path.join(ROOT, "02_Vectors/C2_Security/C2_guilloche_rosette_bold_600ppi.png"))
HALO_CY = DOME_CY + 14
# rotated so the inner ring's '•' separator sits exactly behind the spire (measured: 1.04 deg)
rs = C.place(ros, cx_mm=DOME_CX, cy_mm=HALO_CY, width_mm=122, rotate=-1.04)
# reads as a seal at thumbnail: engraving lines one pixel heavier, plus a crisp double rim
# (0.45 + 0.18 mm, the way passport and banknote seals are framed) just outside the pattern
rs[..., 3] = cv2.dilate(rs[..., 3], np.ones((2, 2), np.uint8))
rim = np.zeros((H, W), np.uint8)
for r_mm, w_mm in ((62.3, 0.45), (63.6, 0.18)):
    cv2.circle(rim, (int(round(mm(DOME_CX) * 4)), int(round(mm(HALO_CY) * 4))), int(round(mm(r_mm) * 4)), 255,
               max(1, int(round(mm(w_mm)))), lineType=cv2.LINE_AA, shift=2)
rs[..., 3] = np.maximum(rs[..., 3], rim.astype(np.float32) / 255)
rs[..., 3] *= (1 - C.radial(124, 36, 36, 1.2)) * np.clip((156 - yy) / 40, 0, 1)
# hairline knockout: the lines stop ~2 px short of the needle and finial (engraving style) so the thin
# gold rod reads against the gold pattern; follows the rod's own matte, not a band through the halo
ist_a = C.place(ist_src, left_mm=IST_LEFT, top_mm=IST_TOP, width_mm=IST_W_MM)[..., 3]
rod = ((ist_a > 0.3) & (yy < IST_TOP + 430 * sc / mm(1))).astype(np.uint8)
rs[..., 3] *= 1 - C.blur(cv2.dilate(rod, np.ones((5, 5), np.uint8)).astype(np.float32), 0.7)
rs[..., 3] *= 1 - C.text_burn(ROOT, "C2", feather_mm=1.0) * 0.85    # guilloche knocked back behind small type
rs[..., :3] = C.hexf("#E2BC4F")
# a soft navy keyline under the engraving: the gold separates from the white stripes (where a screen
# blend vanished), and the seal reads as one darker, finely textured disc at thumbnail
key = np.zeros((H, W, 4), np.float32)
key[..., :3] = C.hexf("#081634")
key[..., 3] = np.clip(C.blur(rs[..., 3], 2.2) * 1.4, 0, 1) * 0.42
stripe = np.clip(fl[..., 3] * 1.2, 0, 1) * np.clip((DOME_CX - 18 - xx) / 14 + 1, 0, 1) * np.clip((DOME_CY + 2 - yy) / 6, 0, 1)
rs[..., 3] *= 1 - stripe * 0.4
key[..., 3] *= 1 - stripe * 0.4
# 9.5 review: the engraving competed with the dome. Ease it back close around the dome (the outer
# rings and rim stay at full strength), so the gold dome reads first and the seal second
near = C.radial(DOME_CX, DOME_CY + 4, 34, 2.0)
rs[..., 3] *= 1 - near * 0.4
key[..., 3] *= 1 - near * 0.4
# review 28 Oct: the top-left (engraving + crescent + stripes) was the busiest corner; ease it there
tl = C.radial(18, 40, 48, 1.6)
rs[..., 3] *= 1 - tl * 0.45
key[..., 3] *= 1 - tl * 0.45
st.add("Guilloche halo keyline", key)
st.add("Guilloche halo", rs, opacity=0.85)
halo = C.radial(DOME_CX, HALO_CY, 70, 2.2)
st.add("Halo glow", full(np.broadcast_to(C.hexf("#C99A3E"), (H, W, 3)), halo), mode="screen", opacity=0.18)

# ------------------------------------------------------------------ jets (clear of halo and Jata)
jets = cut("R-SU30.png")                     # REAL RMAF Su-30MKMs (USAF photo, public domain; real_prep.py)
jets[..., :3] = C.exposure(jets[..., :3], -0.25)
jets[..., :3] = C.tint_shadows_highlights(jets[..., :3], shadow=(0.0, 0.0, 0.03), highlight=(0.05, 0.02, -0.02))
jkw = dict(cx_mm=72, cy_mm=25, width_mm=58.9, rotate=0, flip=True)          # review 28 Oct: +15%
jt = C.place(jets, **jkw)
# last light of dusk catches the upper surfaces: a stronger warm edge so the formation reads on navy
jt = C.rim_light(jt, WARM, direction=(-1, -0.6), width_px=5, strength=0.6)
st.add("Su-30MKM formation (real photo)", jt)

# ------------------------------------------------------------------ istana relit to blue hour
ist = ist_src.copy()
rgb = ist[..., :3]
dreg = C.dome_region(rgb, ist[..., 3])                 # full dome silhouettes (overcast tiles included)
rgb = C.goldify(rgb, dreg)                             # retouch desaturated tiles back to the dome's gold
hsv = cv2.cvtColor(np.clip(rgb, 0, 1), cv2.COLOR_RGB2HSV)
gold = dreg
up = np.arange(rgb.shape[0], dtype=np.float32)[:, None] / rgb.shape[0]
base = C.exposure(rgb, -1.15)
base = C.tint_shadows_highlights(base, shadow=(-0.015, -0.005, 0.045), highlight=(0.0, 0.0, 0.02), balance=0.45)
flood = C.exposure(rgb, 0.12) * C.hexf("#FFD49A")
facade_w = np.clip(up * 1.45 - 0.1, 0, 1)[..., None] ** 0.75 * 0.85
lit = base * (1 - facade_w) + flood * facade_w
dome = C.curves(C.exposure(rgb, 0.3) * C.hexf("#FFE4AC"), [(0, 0), (0.35, 0.28), (0.75, 0.82), (1, 1)])
lit = lit * (1 - gold[..., None] * 0.85) + dome * gold[..., None] * 0.85
dark = (C.lum(rgb) < 0.32) & (hsv[..., 1] < 0.25)
win = C.blur(dark.astype(np.float32), 1.2)[..., None] * np.clip(up * 2 - 0.6, 0, 1)[..., None]
lit = lit * (1 - win * 0.35) + (lit * 0.5 + C.hexf("#FFC27A") * 0.22) * win * 0.35
ist[..., :3] = np.clip(C.saturation(lit, 0.92), 0, 1)
ikw = dict(left_mm=IST_LEFT, top_mm=IST_TOP, width_mm=IST_W_MM)
it = C.place(ist, **ikw)
it[..., :3] = it[..., :3] * 0.92 + C.hexf("#2C447E") * 0.08
it = C.light_wrap(it, full(st.comp), width_px=5, strength=0.25)
bgm = np.asarray(Image.open(os.path.join(ROOT, "03_Cutouts/ISTANA_bgmask.png")), np.float32) / 255
it = C.melt_background(ist, bgm, ikw, it, st.comp, top=0.97, bottom=0.82)
st.add("Istana Negara (real photo, relit)", it)

mist = np.clip((yy - 118) / 30, 0, 1) * np.clip((175 - yy) / 25, 0, 1) * 0.55
st.add("Evening mist", full(np.broadcast_to(C.hexf("#3B4F86"), (H, W, 3)), mist))


# ------------------------------------------------------------------ people row
def soldier_only(p):
    """C2-C_v1 shows the police officer and the soldier side by side; keep the soldier. Every row
    has a background gap between them (>= 3 px), so cut each row in the middle of its widest gap."""
    a = p[..., 3] > 0.5
    split = np.empty(a.shape[0], np.float32)
    for y in range(a.shape[0]):
        bg = np.concatenate([[False], ~a[y, 440:660], [False]]).astype(np.int8)
        st, en = np.where(np.diff(bg) == 1)[0], np.where(np.diff(bg) == -1)[0]
        i = int(np.argmax(en - st)) if len(st) else 0
        split[y] = 440 + (st[i] + en[i]) / 2 if len(st) else 550
    p = p.copy()
    p[..., 3] *= np.arange(p.shape[1])[None, :] >= split[:, None]
    return p


SOLDIER = dict(left_mm=72.4, top_mm=87.0, height_mm=84.3)


def extend_sleeve(pl):
    """The soldier's left sleeve meets the photo's right edge (rows 582-1079), which reads as a
    ruler-straight line on the cover. Retouch: continue the sleeve ~1.2 mm with its own mirrored
    fabric along a rounded upper-arm contour (joining the shoulder curve above and the forearm below),
    shaded toward the outer, shadow side. Only the sleeve is extended."""
    s = mm(SOLDIER["height_mm"]) / 1536
    xc = int(round(mm(SOLDIER["left_mm"]) + (1023 - 512) * s))          # last source column on the canvas
    y0, y1 = int(mm(SOLDIER["top_mm"]) + 575 * s), int(mm(SOLDIER["top_mm"]) + 1085 * s)
    xc = max(range(xc - 3, xc + 4), key=lambda x: pl[y0:y1, x, 3].mean())   # exact cut column
    out = pl.copy()
    for y in range(y0, y1):
        e = 14.0 * np.sin(np.pi * (y - y0) / (y1 - y0)) ** 0.7
        for d in range(1, int(np.ceil(e)) + 1):
            out[y, xc + d, :3] = pl[y, xc - d + 1, :3] * (1 - 0.35 * (d / e) ** 1.5)
            out[y, xc + d, 3] = np.clip(e - d + 1, 0, 1) * pl[y, xc, 3]
    return out


def person(cut_name, layer_name, fade=(146, 172), rim_dir=(-1, -0.2), prep=None, post=None, rim=0.22,
           lift=0.0, **kw):
    p = cut(cut_name)
    if prep:
        p = prep(p)
    pl = C.place(p, **kw)
    if post:
        pl = post(pl)
    if lift:                                  # open up near-black fabric so the uniform's shape reads
        pl[..., :3] = C.curves(pl[..., :3], [(0, 0), (0.12, 0.12 + lift), (0.45, 0.45 + lift * 0.5), (1, 1)])
    pl[..., :3] = C.tint_shadows_highlights(pl[..., :3], shadow=(-0.01, -0.005, 0.03))
    pl = C.rim_light(pl, WARM, direction=rim_dir, width_px=5, strength=rim)
    pl = C.light_wrap(pl, full(st.comp), width_px=6, strength=0.3)
    # the lower body sinks into the night shade: darken, don't thin out (no palace showing through the legs)
    k = np.clip((yy - fade[0]) / (fade[1] - fade[0]), 0, 1)[..., None] ** 1.3
    pl[..., :3] = pl[..., :3] * (1 - k) + C.hexf("#070F28") * k
    pl[..., 3] *= np.clip((fade[1] + 24 - yy) / 24, 0, 1)
    rows = np.where(pl[..., 3].max(axis=1) > 0.02)[0]        # photo's own bottom edge: never a hard line
    if len(rows):
        pl[..., 3] *= np.clip((rows.max() / mm(1) - yy) / 8, 0, 1)
    # (review 28 Oct: a strong offset shadow on the far palace and flag read as a dark fringe; a faint one)
    sh = C.shadow_layer(pl, offset_mm=(1.2, 0.8), blur_mm=4, opacity=0.12, color="#050A1C")
    st.add(layer_name + " shadow", sh)
    st.add(layer_name, pl, src=C.src_layer(ROOT, cut_name, **kw))


OFF_H = 103.0


def pdrm_light(p):
    """The real officer was shot at noon in hard sun: bring him into C2's warm dusk floodlight."""
    p = p.copy()
    p[..., :3] = C.exposure(p[..., :3], -0.85)
    p[..., :3] = C.curves(p[..., :3], [(0, 0), (0.25, 0.17), (0.7, 0.66), (1, 0.95)])     # deeper blacks, soldier's contrast
    # the uniform reads grey in the noon photo: pull its blue-grey toward PDRM navy (skin, badges, ribbons untouched)
    hsv = cv2.cvtColor(np.clip(p[..., :3], 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    navy = ((hsv[..., 0] > 190) & (hsv[..., 0] < 250) & (hsv[..., 1] < 0.6) & (hsv[..., 2] < 0.6)).astype(np.float32)
    navy = C.blur(navy, 2)[..., None]
    p[..., :3] = p[..., :3] * (1 - navy * 0.55) + (C.lum(p[..., :3])[..., None] * C.hexf("#2B3D78") * 1.6) * navy * 0.55
    p[..., :3] = C.tint_shadows_highlights(p[..., :3], shadow=(-0.01, -0.005, 0.03), highlight=(0.05, 0.02, -0.03))
    p[..., :3] = p[..., :3] * 0.92 + C.hexf("#1E2A4A") * 0.08                          # a step back in the dusk air
    return p
# back to front: police, soldier, researcher (far right), student (front-left).
# Police and soldier: uniform-accurate regenerations (PROMPTS_ChatGPT_Uniformed.md) with the real
# PDRM crest / 10 Para badge (insignia.py). Each is placed so the head top, head centre and head size
# (crown to chin) match the figure it replaces; the lower body sinks into the navy base.
# REAL PDRM officer taking the oath (ikrar), right hand raised (photo supplied by Anaqi 28 Oct, pitch
# comp; user_prep.py): the pledge is the cover's message, Rahsiakan Rahsia Kerajaan. He stands in the
# gap between the student and the soldier, so the raised hand rises clear of her; his right side is
# behind the soldier's shoulder. Overcast photo: already PDRM navy, so only brought into the dusk light.
def oath_light(p):
    p = p.copy()
    p[..., :3] = C.exposure(p[..., :3], -0.55)
    p[..., :3] = C.curves(p[..., :3], [(0, 0), (0.25, 0.19), (0.7, 0.67), (1, 0.96)])
    p[..., :3] = C.tint_shadows_highlights(p[..., :3], shadow=(-0.01, -0.005, 0.03), highlight=(0.05, 0.02, -0.03))
    return p


def brighter(p, ev):
    p = p.copy()
    p[..., :3] = C.exposure(p[..., :3], ev)
    return p


# review 28 Oct: a calmer, formal pose. Studio portrait (photo 31, supplied, pitch comp): hands clasped,
# working uniform, real crest and rank. Head matched (cap top 96.4 mm, 13 mm crown to chin), face at x 71;
# brightened slightly against the navy base (less darkening than the outdoor photos)
def formal_light(p):
    p = p.copy()
    p[..., :3] = C.exposure(p[..., :3], -0.2)
    p[..., :3] = C.curves(p[..., :3], [(0, 0), (0.25, 0.22), (0.7, 0.71), (1, 0.98)])
    p[..., :3] = C.tint_shadows_highlights(p[..., :3], shadow=(-0.008, -0.004, 0.025), highlight=(0.045, 0.02, -0.025))
    return p


# review 28 Oct: police and soldier stood shoulder to shoulder; 3 mm apart each way now, and both a
# step brighter (the dusk grade had taken them too far down)
person("U-PDRM-FORMAL.png", "Police - PDRM, formal (real photo)", fade=(142, 160), rim=0.3,
       prep=lambda p: brighter(formal_light(p), 0.18),
       left_mm=45.5, top_mm=89.4, width_mm=46.7)
# 9.5 push: the three AI figures replaced by REAL photos Anaqi supplied (user_prep2.py; licences to
# confirm, SOURCES.md). Head sizes and positions matched to the figures they replace.


def dusk_light(ev, sat=0.95):
    """Daylight photo into C2's blue hour: down in exposure, cooler shadows, warm floodlit highlights."""
    def f(p):
        p = p.copy()
        p[..., :3] = C.exposure(p[..., :3], ev)
        p[..., :3] = C.saturation(p[..., :3], sat)
        p[..., :3] = C.curves(p[..., :3], [(0, 0), (0.25, 0.2), (0.7, 0.68), (1, 0.96)])
        p[..., :3] = C.tint_shadows_highlights(p[..., :3], shadow=(-0.012, -0.004, 0.035), highlight=(0.04, 0.018, -0.02))
        return p
    return f


# 10 Para officer, Col. Mohd Azral Manan, at the Tiger Strike 24 opening ceremony aboard USS Somerset
# (DVIDS 8439351, Cpl. Aidan Hekker USMC, PUBLIC DOMAIN; user_prep2.py). Review 28 Oct: a full-height
# soldier standing at ease, hands clasped, no weapon, replaces the patrol photo (rifle, agency licence).
# His pose answers the police officer's. Beret top 98 mm, 13.5 mm crown to chin (source 432 -> 610).
# review 28 Oct: he read ~12% smaller than the officer beside him and in warmer daylight; now the same
# head size (15.1 mm crown to chin), the same dusk light, and the same fade into the night base
AZ = 15.1 / 178


def soldier_light(p):
    p = dusk_light(-0.32, 0.86)(p)
    p[..., :3] = C.tint_shadows_highlights(p[..., :3], shadow=(-0.006, -0.002, 0.02), highlight=(-0.01, -0.004, 0.01))
    return p


person("U-C2-SOLDIER2.png", "Soldier - ATM, 10 Para (real photo, DVIDS public domain)", fade=(142, 160),
       prep=soldier_light, rim=0.3, left_mm=91 - 812 * AZ, top_mm=97.4 - 432 * AZ, width_mm=2000 * AZ)
# cyber analyst (real; security-operations desk, tablet + phone, lanyard), flipped to face the centre;
# already lit by her screens' blue, so only a small step into the dusk
# review 28 Oct: her hands and tablet crowded the roundel; she stands a step further back (8% smaller)
# and 4 mm higher, so the tablet clears the roundel's top
AN = 17 * 0.92 / 505
person("U-C2-ANALYST.png", "Researcher - penyelidikan (siber, real photo)", rim_dir=(1, -0.2), fade=(114, 128),
       prep=dusk_light(-0.05, 1.0), left_mm=123.5 - 1310 * AN, top_mm=95.0 - 55 * AN, width_mm=2000 * AN,
       flip=True)
# her photo ends at the waist (seated at a desk): the night pools under the right of the row, so she and
# the soldier sink into the dark like the student and the officer on the left (she floated over the
# lit palace)
st.add("Shade - night pools under the row", full(np.broadcast_to(C.hexf("#070F28"), (H, W, 3)),
       np.clip((yy - 120) / 18, 0, 1) * (0.7 + 0.2 * np.clip((xx - 84) / 20, 0, 1))))
# student, front-left: review 28 Oct, a Malaysian Indian student (AI-generated placeholder, made for this
# cover's blue hour; to be replaced by a licensed or official photo for print) so the set shows all
# three main communities; her phone's padlock screen is the cover's message. She replaces the stock
# photo of a student in a grey hijab, whose licence was unknown.
person("C2-F.png", "Student - rakyat / anak muda (AI placeholder)", left_mm=8, top_mm=97, height_mm=82)

# ------------------------------------------------------------------ base + dossier
shade = np.clip((yy - 128) / 70, 0, 1) ** 1.3 * 0.9
st.add("Shade - headline base", full(np.broadcast_to(C.hexf("#060E26"), (H, W, 3)), shade))

dos = cut("C2-B.png")
dos[..., :3] = C.exposure(dos[..., :3], 0.05)
dh, dw = dos.shape[:2]
# the blank cream label read as a hole at thumbnail: re-cover it in the file's own navy leather
# (its paper grain kept as texture), so only the gold frame of the label remains
lab = np.zeros((dh, dw), np.float32)
lab[int(.40 * dh):int(.62 * dh), int(.22 * dw):int(.55 * dw)] = 1
lab *= (C.lum(dos[..., :3]) > 0.35)
lab = C.blur(lab, 3)[..., None]
grain_l = C.lum(dos[..., :3])
leather = C.hexf("#1E2D58") * (0.9 + (grain_l - C.blur(grain_l, 4))[..., None] * 1.5)
dos[..., :3] = dos[..., :3] * (1 - lab) + leather * lab


def foil_jata(img):
    """Gold-foil Jata Negara stamped into the file's blind-embossed circle (official government dossier).
    Rendered from the supplied vector, single-colour foil, mapped onto the tilted cover plane."""
    import pymupdf
    src = os.path.join(ROOT, "JATA NEGARA AI (1).ai")
    page = pymupdf.open(src)[0]
    r = pymupdf.Rect()
    for d in page.get_drawings():
        r |= d["rect"]
    pm = page.get_pixmap(clip=r, alpha=True, dpi=int(900 * 72 / r.width))
    px_ = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, pm.n).astype(np.float32) / 255
    # one-colour foil keeps the emblem's drawing: dark line work stamps solid, light fills stamp
    # thinner, so the tigers, shield and crest stay legible instead of a flat silhouette
    lum_j = px_[..., :3] @ np.array([0.3, 0.59, 0.11], np.float32)
    edge_j = np.clip(np.abs(lum_j - cv2.GaussianBlur(lum_j, (0, 0), 2.0)) * 4, 0, 1)
    ja = px_[..., 3] * np.clip(0.18 + 0.82 * (1 - lum_j) ** 1.4 + edge_j * 0.6, 0, 1)
    jh, jw = ja.shape
    # cover plane from the gold frame's corners (source px): top-left, top-right, bottom-left
    TL, U, V = np.array([612.0, 92.0]), np.array([428.0, 98.0]), np.array([-362.0, 513.0])
    ctr = np.array([722.0, 316.0])                                   # centre of the embossed circle
    ws = 0.33                                                        # Jata width as a fraction of the frame
    ht = ws * (jh / jw) * np.linalg.norm(U) / np.linalg.norm(V)
    Ux, Vy = U * ws / jw, V * ht / jh
    off = ctr - Ux * jw / 2 - Vy * jh / 2
    M = np.array([[Ux[0], Vy[0], off[0]], [Ux[1], Vy[1], off[1]]], np.float32)
    a = cv2.warpAffine(ja, M, (dw, dh), flags=cv2.INTER_AREA if False else cv2.INTER_LINEAR)
    a = np.clip(a, 0, 1)
    # foil: warm gold with a diagonal sheen; debossed, so a fine shadow on the upper-left inner edge
    gy_, gx_ = np.mgrid[0:dh, 0:dw].astype(np.float32)
    sheen = 0.5 + 0.5 * np.sin((gx_ * 0.6 + gy_) / 38.0)
    gold = C.hexf("#B8893A") * (1 - sheen[..., None]) + C.hexf("#F3D88C") * sheen[..., None]
    sh = np.clip(np.roll(np.roll(a, -2, 0), -2, 1) - a, 0, 1)
    out = img.copy()
    out[..., :3] = out[..., :3] * (1 - sh[..., None] * 0.5)
    out[..., :3] = out[..., :3] * (1 - a[..., None]) + gold * a[..., None]
    return out


dos = foil_jata(dos)
# lower right, clear of the headline: the roundel overlaps the file like an official chop
dkw = dict(left_mm=50, top_mm=139, width_mm=128, rotate=8)
dl = C.place(dos, **dkw)
dl = C.rim_light(dl, WARM, direction=(-1, -1), width_px=4, strength=0.45)
# a warm desk-lamp pool across the cover so the foil and gold frame catch light
pool = C.radial(104, 168, 34, 1.6)[..., None]
dl[..., :3] = np.clip(dl[..., :3] * (1 + pool * 0.35) + C.hexf("#FFB65C") * pool * 0.04, 0, 1)
st.add("Dossier shadow", C.shadow_layer(dl, offset_mm=(2, 3), blur_mm=5, opacity=0.6, color="#02050F"))
st.add("Classified dossier", dl, src=C.src_layer(ROOT, "C2-B.png", **dkw))

hl = np.clip((yy - 150) / 10, 0, 1) * np.clip((112 - xx) / 20, 0, 1) * 0.35
st.add("Shade - headline text", full(np.broadcast_to(C.hexf("#050B1E"), (H, W, 3)), hl))

mf = C.load_rgba(os.path.join(ROOT, "02_Vectors/C2_Security/C2_microtext_frame_300ppi.png"))
mf = C.place(mf, left_mm=0, top_mm=0, width_mm=154)
mf[..., :3] = C.hexf("#D8B556")
st.add("Microtext frame", mf, opacity=0.45)

# Jata + office block: a soft dark pad so the emblem pops over the flag
tr = np.clip(C.radial(120, 30, 46, 1.4) * 0.78 + C.radial(154, 0, 84, 1.8) * 0.4, 0, 0.85)
st.add("Shade - Jata + office text", full(np.broadcast_to(C.hexf("#050D24"), (H, W, 3)), tr))


def grade(c):
    g = C.curves(c, [(0, 0.012), (0.25, 0.235), (0.6, 0.62), (1, 0.98)])
    g = C.tint_shadows_highlights(g, shadow=(-0.004, 0.0, 0.012), highlight=(0.012, 0.006, -0.008))
    vign = 1 - C.radial(77, 108, 150, 1.0)
    return g * (1 - vign[..., None] * 0.22)


C.finalize_live(ROOT, "C2", OUT, "CGSO2026_C2_Keselamatan_Dokumen.psd", st, grade, fast=FAST)
print("C2 done")
