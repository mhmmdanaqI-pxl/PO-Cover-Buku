"""Cover C1 - Alam Sekitar: 'Langit Biru, Negara Terpelihara'.

The haze lifting diagonally: smoky amber veil top-left, clean blue sky over the
Istana. Big Jalur Gemilang across the top (as 2025) emerging from the haze,
TUDM C-130 (cloud seeding) flying out of it; soldier and environmental
researcher on the left, youths planting a sapling on the right; rainforest at
the base. Sun from the upper right.
Run: venv python -I _scripts/build_C1.py <workspace> [fast]
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
OUT = os.path.join(ROOT, "04_Final", "C1")
os.makedirs(OUT, exist_ok=True)
cut = lambda n: C.load_rgba(os.path.join(ROOT, "03_Cutouts", n))
SUN = "#FFF1D6"
yy = np.arange(H, dtype=np.float32)[:, None] / mm(1)
xx = np.arange(W, dtype=np.float32)[None, :] / mm(1)


def full(rgb, a=None):
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = 1.0 if a is None else a
    return out


def plate(path):
    p = C.load_rgb(path)
    rgba = np.dstack([p, np.ones(p.shape[:2], np.float32)])
    return C.place(rgba, left_mm=0, top_mm=-8, width_mm=154)[..., :3]


# ------------------------------------------------------------------ sky: haze lifting
clear = plate(os.path.join(ROOT, "assets/C1/C1-A1_v2.png"))
haze = plate(os.path.join(ROOT, "assets/C1/C1-A2_v2.png"))
# keep the plate's own smoky brown-grey (desaturating it to beige read as plain background at thumbnail)
haze = C.saturation(C.exposure(haze, 0.06), 0.95)
clear = C.curves(clear, [(0, 0), (0.5, 0.48), (1, 0.98)])
rng = np.random.default_rng(11)
n1 = C.blur(rng.normal(0, 1, (H, W)).astype(np.float32), 55)
n1 /= n1.std() + 1e-6
n2 = C.blur(rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32), 30)
n2 = cv2.resize(n2 / (n2.std() + 1e-6), (W, H), interpolation=cv2.INTER_CUBIC)
haze = haze * (1 + 0.11 * np.clip(n2, -2, 2))[..., None]               # large, soft smoke volumes
d = (xx / 154) * 0.85 + (yy / 216) * 0.75                              # diagonal coordinate
hz = np.clip((0.90 - d + n1 * 0.04) / 0.44, 0, 1)
hz = hz * hz * (3 - 2 * hz)
sky = clear * (1 - hz[..., None]) + haze * hz[..., None]
beam = np.clip(1 - np.abs(d - 0.74 + n1 * 0.02) / 0.10, 0, 1) * np.clip((150 - yy) / 60, 0, 1)
sky = C.blend(sky, np.broadcast_to(C.hexf("#FFF4DC"), sky.shape), beam, "screen", 0.22)
st = C.Stack("Sky - haze lifting (real plates blended)", sky)

# ------------------------------------------------------------------ big flag (as 2025), emerging from the haze
flag = cut("FLAG_waving.png")
flag[..., :3] = C.curves(flag[..., :3], [(0, 0.02), (0.5, 0.52), (1, 1)])
# the smog is distant atmosphere: it sits behind the flag, which stays clean and vivid
drift = np.clip(hz * 1.15 - 0.15, 0, 1) ** 1.3 * (0.75 + 0.25 * np.clip(n1, -1, 1)) * 0.6
st.add("Haze drift (behind the flag)", full(haze, np.clip(drift, 0, 1)))
fl = C.place(flag, left_mm=-26, top_mm=-8, width_mm=190, rotate=3)
fl[..., 3] *= np.clip(1 - (xx - 98) / 62, 0.22, 1) * np.clip((100 - yy) / 30, 0, 1)
fl[..., 3] *= np.clip((58 + 0.30 * xx - yy) / 16 + 0.5, 0, 1)        # lower-left edge dissolves into the haze (clear sky for the C-130)
fl = C.rim_light(fl, SUN, direction=(1, -1), width_px=5, strength=0.3)
st.add("Jalur Gemilang (exact vector on fabric)", fl)

# ------------------------------------------------------------------ C-130 flying out of the haze
c130 = cut("C1-G.png")
blue = np.clip((c130[..., 2] - c130[..., 0] - 0.06) / 0.12, 0, 1)[..., None]   # sky caught in the prop discs
c130[..., :3] = c130[..., :3] * (1 - blue) + C.lum(c130[..., :3])[..., None] * C.hexf("#D8CDB8") * blue
c130[..., 3] *= 1 - blue[..., 0] * 0.35
# seen from below with the sun above: deeper mid-tones and a shaded underside, so it reads against bright haze
c130[..., :3] = C.curves(c130[..., :3], [(0, 0), (0.3, 0.19), (0.7, 0.58), (1, 0.94)])
rows = np.where(c130[..., 3].max(axis=1) > 0.5)[0]
under = np.clip((np.arange(c130.shape[0], dtype=np.float32) - rows.min()) / max(1, rows.max() - rows.min()), 0, 1)
c130[..., :3] *= (1 - 0.32 * under)[:, None, None]
ckw = dict(cx_mm=28, cy_mm=75, width_mm=46, rotate=5)
cl = C.place(c130, **ckw)
v = (hz * np.clip(0.22 - xx / 300, 0.08, 0.22))[..., None]   # flying out of the haze: tail more veiled than nose
cl[..., :3] = cl[..., :3] * (1 - v) + haze * v
cl = C.rim_light(cl, SUN, direction=(1, -1), width_px=3, strength=0.45)
st.add("TUDM C-130H (cloud seeding)", cl, src=C.src_layer(ROOT, "C1-G.png", **ckw))

# ------------------------------------------------------------------ istana in clear morning sun
IST_W_MM = 188.0
ist = cut("ISTANA_base.png")
sc = mm(IST_W_MM) / ist.shape[1]
IST_LEFT = 77 - 1813.6 * sc / mm(1)
IST_TOP = 40 - 171 * sc / mm(1)
rgb = ist[..., :3]
dreg = C.dome_region(rgb, ist[..., 3])                 # full dome silhouettes (overcast tiles included)
rgb = C.goldify(rgb, dreg)                             # retouch desaturated tiles back to the dome's gold
hsv = cv2.cvtColor(np.clip(rgb, 0, 1), cv2.COLOR_RGB2HSV)
gold = dreg[..., None]
ih, iw = rgb.shape[:2]
gy = np.arange(ih, dtype=np.float32)[:, None] / ih
gx = np.arange(iw, dtype=np.float32)[None, :] / iw
sunw = np.clip(0.55 + 0.45 * (gx * 0.7 + (1 - gy) * 0.5), 0, 1.2)[..., None]   # brighter toward upper right
lit = C.curves(rgb, [(0, 0), (0.25, 0.2), (0.6, 0.64), (0.9, 0.97), (1, 1)])
lit = lit * (0.82 + 0.3 * sunw)
lit = C.tint_shadows_highlights(lit, shadow=(-0.01, 0.0, 0.025), highlight=(0.035, 0.02, -0.01))
dome = C.curves(rgb * C.hexf("#FFF0C4"), [(0, 0), (0.3, 0.26), (0.7, 0.8), (1, 1)]) * (0.9 + 0.25 * sunw)
lit = lit * (1 - gold * 0.8) + dome * gold * 0.8
ist[..., :3] = np.clip(C.saturation(lit, 1.06), 0, 1)
bgm = np.asarray(Image.open(os.path.join(ROOT, "03_Cutouts/ISTANA_bgmask.png")), np.float32) / 255
ist[..., :3] = ist[..., :3] * (1 - bgm[..., None] * 0.85) + (ist[..., :3] * 0.22 + C.hexf("#6E9FD6") * 0.78) * bgm[..., None] * 0.85
ikw = dict(left_mm=IST_LEFT, top_mm=IST_TOP, width_mm=IST_W_MM)
it = C.place(ist, **ikw)
v = (hz * 0.5)[..., None]                                    # the palace's left wing stands in the haze
it[..., :3] = it[..., :3] * (1 - v) + haze * v
it = C.light_wrap(it, full(st.comp), width_px=5, strength=0.3)
it = C.melt_background(ist, bgm, ikw, it, st.comp, top=1.0, bottom=0.92)
st.add("Istana Negara (real photo, relit to clear sun)", it)

# ------------------------------------------------------------------ distant forest band (grounds the palace)
fplate = C.load_rgb(os.path.join(ROOT, "assets/C1/C1-F_v2.png"))
fb = C.place(np.dstack([fplate, np.ones(fplate.shape[:2], np.float32)]), left_mm=-10, top_mm=118, width_mm=176)
fb[..., :3] = C.blur(C.exposure(fb[..., :3], -0.9), 4) * 0.8 + C.hexf("#0E2E20") * 0.2
fb[..., 3] = np.clip((yy - 134) / 10, 0, 1) * (fb[..., 3] > 0)
st.add("Distant forest band", fb)


# ------------------------------------------------------------------ people
def person(name, layer_name, ground=None, **kw):
    p = cut(name)
    if ground:                                   # restore the real soil/grass under kneeling subjects
        src = C.load_rgb(os.path.join(ROOT, ground))
        ph, pw = src.shape[:2]
        gy_, gx_ = np.mgrid[0:ph, 0:pw].astype(np.float32)
        ell = np.clip(1 - (((gx_ / pw - 0.52) / 0.52) ** 2 + ((gy_ / ph - 0.86) / 0.21) ** 2), 0, 1) ** 0.6
        ell = C.blur(ell * (gy_ / ph > 0.6), 8)
        p = np.dstack([src * (1 - p[..., 3:4]) + p[..., :3] * p[..., 3:4], np.maximum(p[..., 3], ell)])
    pl = C.place(p, **kw)
    pl = C.rim_light(pl, SUN, direction=(1, -0.6), width_px=5, strength=0.28)
    pl = C.light_wrap(pl, full(st.comp), width_px=6, strength=0.28)
    pl[..., 3] *= np.clip((176 - yy) / 26, 0, 1)
    st.add(layer_name + " shadow", C.shadow_layer(pl, offset_mm=(-1.5, 1.2), blur_mm=4, opacity=0.28, color="#0C1A14"))
    st.add(layer_name, pl, src=C.src_layer(ROOT, name, **kw))


# researcher left and soldier right, so her air-quality meter (the research cue) is clear of his sleeve
person("C1-D.png", "Environmental researcher - penyelidikan", left_mm=-6, top_mm=92, height_mm=74)
person("UNI-C1-ARMY_ins.png", "Soldier - ATM", left_mm=28.46, top_mm=86.41, height_mm=94.35)
person("C1-E.png", "Youths planting - rakyat / anak muda", ground="assets/C1/C1-E_v4.png", left_mm=74, top_mm=94,
       width_mm=84)

# ------------------------------------------------------------------ rainforest base
fol = cut("C1-F.png")
fol[..., :3] = C.curves(fol[..., :3], [(0, 0), (0.5, 0.46), (1, 0.95)])
fkw = dict(left_mm=-14, top_mm=100, width_mm=182)
fo = C.place(fol, **fkw)
fo[..., :3] = C.exposure(fo[..., :3], -0.25)
st.add("Rainforest base shadow", C.shadow_layer(fo, offset_mm=(0, -2), blur_mm=6, opacity=0.35, color="#06140E"))
st.add("Rainforest base", fo, src=C.src_layer(ROOT, "C1-F.png", **fkw))

shade = np.clip((yy - 136) / 52, 0, 1) ** 1.1 * 0.9
shade = shade * np.clip((118 - xx) / 30, 0.45, 1)
st.add("Shade - headline base", full(np.broadcast_to(C.hexf("#04190F"), (H, W, 3)), shade))

# Jata + office block: a soft deep-blue pad so the emblem pops over sky and flag
tr = np.clip(C.radial(120, 30, 46, 1.4) * 0.62 + C.radial(154, 0, 82, 1.7) * 0.35, 0, 0.75)
st.add("Shade - Jata + office text", full(np.broadcast_to(C.hexf("#0B2B56"), (H, W, 3)), tr))
# the 7.5-8.5 pt white office lines cross the flag's white stripes and bright cloud: a soft burn
# shaped to the lines (no box) keeps every line above 4.5:1
st.add("Shade - office text (soft burn)", full(np.broadcast_to(C.hexf("#0B2B56"), (H, W, 3)),
                                               C.text_burn(ROOT, "C1") * 0.55))


def grade(c):
    g = C.curves(c, [(0, 0.01), (0.25, 0.235), (0.6, 0.625), (1, 0.985)])
    g = C.tint_shadows_highlights(g, shadow=(-0.006, 0.004, 0.006), highlight=(0.012, 0.008, -0.006))
    vign = 1 - C.radial(84, 100, 150, 1.0)
    return g * (1 - vign[..., None] * 0.16)


C.finalize_live(ROOT, "C1", OUT, "CGSO2026_C1_Alam_Sekitar.psd", st, grade, fast=FAST)
print("C1 done")
