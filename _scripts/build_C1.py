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
# REAL haze: Kuala Lumpur, September 2026, AQI 200 (Renek78, CC0). The open smog and ghost towers of
# the left part of the frame, warmed toward the smoky amber of a burning-season haze
hreal = C.load_rgb(os.path.join(ROOT, "assets/_reference/C1_real/Haze_KL_2026.jpg"))[:, :1584]
haze = C.place(np.dstack([hreal, np.ones(hreal.shape[:2], np.float32)]), left_mm=0, top_mm=-8, width_mm=154)[..., :3]
haze = haze * 0.45 + C.lum(haze)[..., None] * C.hexf("#EAD2AE") * 0.62
# keep the plate's own smoky brown-grey (desaturating it to beige read as plain background at thumbnail)
haze = C.saturation(C.exposure(haze, 0.06), 0.95)
# 9.5 review: the before/after must be unmistakable: the smog a step denser and more amber-brown
haze = haze * 0.88 + C.hexf("#B58E62") * 0.12
clear = C.curves(clear, [(0, 0), (0.5, 0.48), (1, 0.98)])
rng = np.random.default_rng(11)
n1 = C.blur(rng.normal(0, 1, (H, W)).astype(np.float32), 55)
n1 /= n1.std() + 1e-6
n2 = C.blur(rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32), 30)
n2 = cv2.resize(n2 / (n2.std() + 1e-6), (W, H), interpolation=cv2.INTER_CUBIC)
n3 = C.blur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), 9)
n3 = cv2.resize(n3 / (n3.std() + 1e-6), (W, H), interpolation=cv2.INTER_CUBIC)
haze = haze + (haze - C.blur(haze, mm(14))) * 2.2                      # the smog's own tonal variation, amplified
haze = haze * (1 + 0.14 * np.clip(n2, -2, 2) + 0.03 * np.clip(n3, -2, 2))[..., None]   # rolling smoke volumes
haze = np.clip(haze, 0, 1)
d = (xx / 154) * 0.85 + (yy / 216) * 0.75                              # diagonal coordinate
hz = np.clip((0.90 - d + n1 * 0.04) / 0.44, 0, 1)
hz = hz * hz * (3 - 2 * hz)
# cloud-seeding run: the C-130 dispenses salt from its ramp; a widening plume streams back from the
# tail into the haze and the smog thins along its path (the story of the cover in one gesture)
P0, P1 = np.array([20.5, 79.6]), np.array([-8.0, 87.5])            # tail -> off the left edge (canvas mm)
seg = P1 - P0
tt = np.clip(((xx - P0[0]) * seg[0] + (yy - P0[1]) * seg[1]) / (seg @ seg), 0, 1)
dist = np.hypot(xx - (P0[0] + tt * seg[0]), yy - (P0[1] + tt * seg[1]))
pw = 0.7 + 4.2 * tt ** 0.8                                             # plume half-width grows behind the tail
wob = 1 + 0.35 * np.clip(n3, -2, 2)
plume = np.exp(-(dist / (pw * wob)) ** 2) * np.clip(tt * 12, 0, 1)
corridor = np.exp(-(dist / (pw * 3.6)) ** 2) * np.clip(tt * 4, 0, 1)
hz = hz * (1 - corridor * 0.7)
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
fl = C.place(flag, left_mm=-24, top_mm=-7, width_mm=176, rotate=3)          # 9.5 review: ~7% smaller, palace leads
fl[..., 3] *= np.clip(1 - (xx - 98) / 62, 0.22, 1) * np.clip((100 - yy) / 30, 0, 1)
fl[..., 3] *= np.clip((58 + 0.30 * xx - yy) / 16 + 0.5, 0, 1)        # lower-left edge dissolves into the haze (clear sky for the C-130)
fl = C.rim_light(fl, SUN, direction=(1, -1), width_px=5, strength=0.3)
st.add("Jalur Gemilang (exact vector on fabric)", fl)

# ------------------------------------------------------------------ C-130 flying out of the haze
c130 = cut("R-C130.png")                     # REAL RMAF C-130H seen from below (Pangalau, CC BY-SA 4.0; real_prep.py)
# a backlit underside against bright haze: keep it a deep, slightly warm silhouette, not pure black
c130[..., :3] = C.curves(c130[..., :3], [(0, 0.03), (0.3, 0.2), (0.7, 0.6), (1, 0.94)])
c130[..., :3] = C.tint_shadows_highlights(c130[..., :3], shadow=(0.01, 0.0, -0.01))
ckw = dict(cx_mm=29, cy_mm=75, width_mm=47, rotate=8, flip=True)
cl = C.place(c130, **ckw)
v = (hz * np.clip(0.42 - (xx - 8) / 90, 0.08, 0.42))[..., None]   # flying out of the haze: tail more veiled than nose
cl[..., :3] = cl[..., :3] * (1 - v) + haze * v
cl = C.rim_light(cl, SUN, direction=(1, -1), width_px=3, strength=0.45)
st.add("TUDM C-130H (real photo, cloud seeding)", cl)

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
# smog pools at ground level: the hazy wing's dark ground floor is veiled further (it read as a dark box
# beside the researcher)
v2 = (hz * np.clip((yy - 118) / 8, 0, 1) * 0.5)[..., None]
it[..., :3] = it[..., :3] * (1 - v2) + haze * v2
it = C.light_wrap(it, full(st.comp), width_px=5, strength=0.3)
it = C.melt_background(ist, bgm, ikw, it, st.comp, top=1.0, bottom=0.92)
st.add("Istana Negara (real photo, relit to clear sun)", it)
# the plume sits over the palace layer's melted sky edge (they never overlap the building itself)
pl_a = np.clip(plume * (0.8 + 0.3 * np.clip(n2, -1, 1)) * np.clip(1 - tt * 0.45, 0, 1), 0, 0.92)
# a cloud has a lit top and a cool, shaded underside: offset the shade down so the plume has volume
under = np.clip(np.roll(pl_a, int(mm(1.2)), axis=0) - pl_a * 0.6, 0, 1) * 0.55
st.add("Cloud-seeding plume underside", full(np.broadcast_to(C.hexf("#8F96A3"), (H, W, 3)), under), mode="multiply")
st.add("Cloud-seeding plume", full(np.broadcast_to(C.hexf("#FFFDF8"), (H, W, 3)), pl_a))

# ------------------------------------------------------------------ distant forest band (grounds the palace)
fplate = C.load_rgb(os.path.join(ROOT, "assets/_reference/C1_real/Rainforest_TamanNegara.jpg"))   # REAL (CC BY 4.0)
fb = C.place(np.dstack([fplate, np.ones(fplate.shape[:2], np.float32)]), left_mm=-10, top_mm=118, width_mm=176)
fb[..., :3] = C.blur(C.exposure(fb[..., :3], -0.9), 4) * 0.8 + C.hexf("#0E2E20") * 0.2
fb[..., 3] = np.clip((yy - 134) / 10, 0, 1) * (fb[..., 3] > 0)
st.add("Distant forest band", fb)


# ------------------------------------------------------------------ people
def person(name, layer_name, ground=None, bottom=None, prep=None, **kw):
    p = cut(name)
    if prep:
        p = prep(p)
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
    if bottom:                                   # the photo's own frame edge: never a hard line
        pl[..., 3] *= np.clip((bottom - yy) / 6, 0, 1)
    st.add(layer_name + " shadow", C.shadow_layer(pl, offset_mm=(-1.5, 1.2), blur_mm=4, opacity=0.28, color="#0C1A14"))
    st.add(layer_name, pl, src=C.src_layer(ROOT, name, **kw))


# researcher left and soldier right, so her air-quality meter (the research cue) is clear of his sleeve
# 9.5 push: both AI groups replaced by REAL photos Anaqi supplied (user_prep2.py; licences to confirm,
# SOURCES.md). The researcher (lab coat, orange handheld meter) is mirrored to face into the cover, so
# the noon sun in her photo falls from the upper right, as on this cover; review 28 Oct: moved 4.5 mm in
# so her shoulder is no longer cut by the trim.


def clear_morning(ev):
    def f(p):
        p = p.copy()
        p[..., :3] = C.exposure(p[..., :3], ev)
        p[..., :3] = C.curves(p[..., :3], [(0, 0), (0.25, 0.23), (0.7, 0.69), (1, 0.97)])
        p[..., :3] = C.tint_shadows_highlights(p[..., :3], shadow=(-0.008, 0.0, 0.012), highlight=(0.02, 0.012, -0.008))
        return p
    return f


# review 28 Oct: she was cut by the trim. Now in the middle ground with the planting pair (head 12 mm,
# hijab top 104 mm), fully inside the safe area, her meter clear of the officer's salute
RS = 12 / 320                                    # mm per source px (hijab top 145 -> chin 465)
RTOP = 104.0 - 145 * RS
person("U-C1-RESEARCH.png", "Environmental researcher - penyelidikan (real photo)", prep=clear_morning(-0.2),
       bottom=RTOP + 1080 * RS - 0.5, left_mm=10.5 - (1920 - 1500) * RS, top_mm=RTOP, width_mm=1920 * RS,
       flip=True)
# two young people planting a sapling (real), the sapling between them; they crouch on their own soil,
# with hands and sapling clear of the roundel (head 10 mm, a step behind the soldier; soil at 129 mm,
# just above the roundel; sapling at x 112)
# review 28 Oct: a step larger (head 11.5 mm) so they and the officer read as one group, and their hands
# and the sapling lifted (the photo's own shadowed soil had swallowed them)
PS = 11.5 / 210
PLANT = dict(left_mm=112 - 1000 * PS, top_mm=129 - 1060 * PS, width_mm=2000 * PS)


def planting_light(p):
    p = clear_morning(0.0)(p)
    hy, hx = np.mgrid[0:p.shape[0], 0:p.shape[1]].astype(np.float32)
    hands = np.exp(-(((hx - 990) / 230) ** 2 + ((hy - 930) / 120) ** 2))[..., None]
    p[..., :3] = np.clip(p[..., :3] * (1 + hands * 0.35), 0, 1)
    return p


person("U-C1-PLANTING.png", "Youths planting - rakyat / anak muda (real photo)", prep=planting_light,
       bottom=129 + (1333 - 1060) * PS - 1.0, **PLANT)                 # the photo's own bottom edge, feathered
# REAL 10 Para officer saluting (photo supplied by Anaqi 28 Oct, pitch comp; user_prep.py). Head matched
# to the soldier he replaces (beret top 94.5 mm, head 17 mm, face centre x 60.5); in front of the youths,
# the photo's bottom edge sinks into the ferns
arm = cut("U-ARMY.png")
# review 28 Oct: he out-shouted the planting (the theme); a step calmer in contrast and colour, and 5 mm
# to the right so he stands with the planting pair, saluting toward them
arm[..., :3] = C.saturation(C.curves(arm[..., :3], [(0, 0.015), (0.5, 0.47), (1, 0.94)]), 0.82)
akw = dict(left_mm=12.0, top_mm=92.3, width_mm=113.7)
ar = C.place(arm, **akw)
ar[..., 3] *= np.clip((156 - yy) / 8, 0, 1)
ar = C.rim_light(ar, SUN, direction=(1, -0.6), width_px=5, strength=0.28)
ar = C.light_wrap(ar, full(st.comp), width_px=6, strength=0.28)
st.add("Soldier - ATM shadow", C.shadow_layer(ar, offset_mm=(-1.5, 1.2), blur_mm=4, opacity=0.28, color="#0C1A14"))
st.add("Soldier - ATM, 10 Para (real photo)", ar)

# ------------------------------------------------------------------ rainforest base
fol = cut("R-FERNS.png")                     # REAL rainforest ferns (Pexels 38145936; real_prep2.py)
fol[..., 3] = np.clip((fol[..., 3] - 0.3) / 0.4, 0, 1)                 # solid fronds: no semi-transparent ghosting
fol[..., :3] = C.curves(fol[..., :3], [(0, 0), (0.25, 0.24), (0.5, 0.52), (1, 0.97)])
fol[..., :3] = C.tint_shadows_highlights(fol[..., :3], shadow=(-0.01, 0.0, 0.01), highlight=(0.03, 0.02, -0.02))
fkw = dict(left_mm=-48, top_mm=99, width_mm=250)
fo = C.place(fol, **fkw)
fo[..., :3] = C.exposure(fo[..., :3], -0.05)
st.add("Rainforest base shadow", C.shadow_layer(fo, offset_mm=(0, -2), blur_mm=6, opacity=0.35, color="#06140E"))
fo = C.rim_light(fo, SUN, direction=(1, -0.8), width_px=3, strength=0.55)
st.add("Rainforest base (real photo)", fo)
# the youths' planting patch ran out in mid-air: a second stand of the same real ferns rises in front
# of its edge on the right, so the ground runs continuously into the forest floor
# review 28 Oct: this second stand climbed over the soldier and the planting pair (six layers fighting
# for second place); it now starts lower, a foreground fringe that only hides the foot of their soil
f2 = C.place(fol, left_mm=48, top_mm=121.0, width_mm=160, flip=True)
f2[..., :3] = C.exposure(f2[..., :3], -0.12)
f2[..., 3] *= np.clip((xx - 62) / 8, 0, 1) * np.clip((174 - yy) / 12, 0, 1)   # melts into the first stand below
f2[..., 3] *= 1 - C.radial(112, 120, 20, 2.4) * 0.95                             # the sapling and hands stay clear
f2 = C.rim_light(f2, SUN, direction=(1, -0.8), width_px=3, strength=0.5)
st.add("Ferns in front of the planting patch shadow", C.shadow_layer(f2, offset_mm=(0, -1.5), blur_mm=4, opacity=0.3, color="#06140E"))
st.add("Ferns in front of the planting patch (real photo)", f2)

shade = np.clip((yy - 136) / 52, 0, 1) ** 1.1 * 0.9
shade = shade * np.clip((118 - xx) / 30, 0.45, 1)
st.add("Shade - headline base", full(np.broadcast_to(C.hexf("#04190F"), (H, W, 3)), shade))
# bright fronds and the lab coat sit behind the light-blue accent lines (3.5:1 measured): a soft burn
# shaped to the lines (no box), as on C3, lifts every letter above 4.5:1
st.add("Shade - headline accent lines (soft burn)", full(np.broadcast_to(C.hexf("#04190F"), (H, W, 3)),
       C.text_burn(ROOT, "C1", "Headline", feather_mm=2.5, spread_mm=(2.0, 1.2), rows_mm=(146, 176)) * 0.6))

# Jata + office block: a soft deep-blue pad so the emblem pops over sky and flag
st.add("Shade - roundel backing", full(np.broadcast_to(C.hexf("#04190F"), (H, W, 3)), C.radial(118, 151.8, 30, 1.6) * 0.5))
tr = np.clip(C.radial(120, 30, 46, 1.4) * 0.62 + C.radial(154, 0, 82, 1.7) * 0.35, 0, 0.75)
st.add("Shade - Jata + office text", full(np.broadcast_to(C.hexf("#0B2B56"), (H, W, 3)), tr))
# the 7.5-8.5 pt white office lines cross the flag's white stripes and bright cloud: a soft burn
# shaped to the lines (no box) keeps every line above 4.5:1
st.add("Shade - office text (soft burn)", full(np.broadcast_to(C.hexf("#0B2B56"), (H, W, 3)),
                                               C.text_burn(ROOT, "C1") * 0.75))


def grade(c):
    g = C.curves(c, [(0, 0.01), (0.25, 0.235), (0.6, 0.625), (1, 0.985)])
    g = C.tint_shadows_highlights(g, shadow=(-0.006, 0.004, 0.006), highlight=(0.012, 0.008, -0.006))
    vign = 1 - C.radial(84, 100, 150, 1.0)
    return g * (1 - vign[..., None] * 0.16)


C.finalize_live(ROOT, "C1", OUT, "CGSO2026_C1_Alam_Sekitar.psd", st, grade, fast=FAST)
print("C1 done")
