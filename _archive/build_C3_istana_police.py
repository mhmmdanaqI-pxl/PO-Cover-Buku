"""Cover C3 - Ekonomi: 'Berhemah Hari Ini, Teguh Esok'.

Sunrise behind-right. Big Jalur Gemilang across the top (as 2025), a thin
protective arc above the dome, the rising gold growth line over the Istana,
port cranes on the horizon, Su-30MKM formation (C2 plate, flipped + warmed),
engineer / young professionals / police in front, solar farm as the base.
Positive: no conflict imagery.
Run: venv python -I _scripts/build_C3.py <workspace> [fast]
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
OUT = os.path.join(ROOT, "04_Final", "C3")
os.makedirs(OUT, exist_ok=True)
cut = lambda n: C.load_rgba(os.path.join(ROOT, "03_Cutouts", n))
AMBER = "#FFB35A"
yy = np.arange(H, dtype=np.float32)[:, None] / mm(1)
xx = np.arange(W, dtype=np.float32)[None, :] / mm(1)


def full(rgb, a=None):
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = 1.0 if a is None else a
    return out


def as_rgba(rgb):
    return np.dstack([rgb, np.ones(rgb.shape[:2], np.float32)])


# ------------------------------------------------------------------ sky
sky = C.place(as_rgba(C.load_rgb(os.path.join(ROOT, "assets/C3/C3-A_v1.png"))), left_mm=0, top_mm=-24,
              width_mm=154)[..., :3]
sky = C.curves(sky, [(0, 0), (0.5, 0.47), (1, 0.97)])
sun = C.radial(122, 120, 70, 2.4)
sky = C.blend(sky, np.broadcast_to(C.hexf("#FFC27A"), sky.shape), sun, "screen", 0.55)
core = C.radial(122, 120, 14, 2.0)
sky = C.blend(sky, np.broadcast_to(C.hexf("#FFF1D2"), sky.shape), core, "screen", 0.8)
st = C.Stack("Sky - sunrise", sky)

# ------------------------------------------------------------------ port cranes on the horizon (darken)
port = C.load_rgb(os.path.join(ROOT, "assets/C3/C3-H_v1.png"))
pt_ = C.place(as_rgba(port), left_mm=-34, top_mm=72, width_mm=210, crop=(0.08, 0.25, 1, 0.78))
pt_[..., :3] = C.blur(pt_[..., :3], 1.0) * 0.85 + C.hexf("#5B4A63") * 0.15
band = np.clip((yy - 78) / 12, 0, 1) * np.clip((140 - yy) / 8, 0, 1) * pt_[..., 3]
st.add("Port cranes on the horizon", full(np.minimum(st.comp, pt_[..., :3]), band * 0.6))

# ------------------------------------------------------------------ big flag (as 2025)
flag = cut("FLAG_waving.png")
flag[..., :3] = C.exposure(flag[..., :3], -0.3)
flag[..., :3] = C.tint_shadows_highlights(flag[..., :3], shadow=(0.0, -0.01, 0.03), highlight=(0.06, 0.03, -0.02))
fl = C.place(flag, left_mm=-26, top_mm=-8, width_mm=190, rotate=3)
fl[..., 3] *= np.clip(1 - (xx - 96) / 64, 0.22, 1) * np.clip((126 - yy) / 26, 0, 1) * 0.94
fl = C.rim_light(fl, AMBER, direction=(1, -0.5), width_px=6, strength=0.4)
st.add("Jalur Gemilang (exact vector on fabric)", fl)

# ------------------------------------------------------------------ protective arc over the dome
arc = C.load_rgba(os.path.join(ROOT, "02_Vectors/C3_Growth/C3_protective_arc_300ppi.png"))
arcg = C.load_rgba(os.path.join(ROOT, "02_Vectors/C3_Growth/C3_protective_arc_glow_300ppi.png"))
shift = np.float32([[1, 0, 0], [0, 1, -mm(24)]])
arc = cv2.warpAffine(arc, shift, (W, H))
arcg = cv2.warpAffine(arcg, shift, (W, H))
arc[..., 3] *= 1 - C.radial(124, 36, 34, 1.2)
arcg[..., 3] *= 1 - C.radial(124, 36, 34, 1.2)
office = C.text_burn(ROOT, "C3", feather_mm=1.0)                  # no linework behind the small type
arc[..., 3] *= 1 - office
arcg[..., 3] *= 1 - office
st.add("Protective arc glow", arcg, mode="screen", opacity=0.6)
st.add("Protective arc", arc, opacity=0.9)

# ------------------------------------------------------------------ jets (over the stripes, clear of the star)
jets = cut("C2-D.png")
jets[..., :3] = C.exposure(jets[..., :3], -0.25) * C.hexf("#FFE2C2")
jkw = dict(cx_mm=86, cy_mm=20, width_mm=44, rotate=7, flip=True)
jt = C.place(jets, **jkw)
jt = C.rim_light(jt, AMBER, direction=(1, -0.3), width_px=4, strength=0.5)
st.add("Su-30MKM formation", jt, src=C.src_layer(ROOT, "C2-D.png", **jkw))

# ------------------------------------------------------------------ istana, backlit at sunrise
IST_W_MM = 192.0
ist = cut("ISTANA_base.png")
sc = mm(IST_W_MM) / ist.shape[1]
IST_LEFT = 77 - 1813.6 * sc / mm(1)
IST_TOP = 47 - 171 * sc / mm(1)
rgb = ist[..., :3]
dreg = C.dome_region(rgb, ist[..., 3])                 # full dome silhouettes (overcast tiles included)
rgb = C.goldify(rgb, dreg)                             # retouch desaturated tiles back to the dome's gold
hsv = cv2.cvtColor(np.clip(rgb, 0, 1), cv2.COLOR_RGB2HSV)
gold = dreg[..., None]
iw = rgb.shape[1]
gx = (np.arange(iw, dtype=np.float32)[None, :] / iw)[..., None]
lit = C.exposure(rgb, -0.55)
lit = C.tint_shadows_highlights(lit, shadow=(-0.01, 0.0, 0.03), highlight=(0.03, 0.01, -0.01))
warm = C.exposure(rgb, 0.05) * C.hexf("#FFC98C")
lit = lit * (1 - gx * 0.45) + warm * gx * 0.45                               # sun side (right) warmer
dome = C.curves(rgb * C.hexf("#FFD9A0"), [(0, 0), (0.3, 0.22), (0.7, 0.74), (1, 1)]) * (0.8 + 0.35 * gx)
lit = lit * (1 - gold * 0.8) + dome * gold * 0.8
bgm = np.asarray(Image.open(os.path.join(ROOT, "03_Cutouts/ISTANA_bgmask.png")), np.float32) / 255
lit = lit * (1 - bgm[..., None] * 0.85) + (lit * 0.25 + C.hexf("#C9967E") * 0.75) * bgm[..., None] * 0.85
ist[..., :3] = np.clip(lit, 0, 1)
ikw = dict(left_mm=IST_LEFT, top_mm=IST_TOP, width_mm=IST_W_MM)
it = C.place(ist, **ikw)
it = C.rim_light(it, "#FFC070", direction=(1, -0.4), width_px=5, strength=0.65)
it = C.light_wrap(it, full(st.comp), width_px=6, strength=0.35)
it = C.melt_background(ist, bgm, ikw, it, st.comp, top=1.0, bottom=0.9)
st.add("Istana Negara (real photo, sunrise backlight)", it)

mist = np.clip((yy - 112) / 26, 0, 1) * np.clip((172 - yy) / 26, 0, 1) * 0.5
st.add("Morning haze", full(np.broadcast_to(C.hexf("#C98E6E"), (H, W, 3)), mist))

# ------------------------------------------------------------------ rising line (in front of the palace)
rl = C.load_rgba(os.path.join(ROOT, "02_Vectors/C3_Growth/C3_rising_line_300ppi.png"))
rlg = C.load_rgba(os.path.join(ROOT, "02_Vectors/C3_Growth/C3_rising_line_glow_300ppi.png"))
st.add("Rising line glow", rlg, mode="screen", opacity=0.7)
st.add("Rising line", rl)


# ------------------------------------------------------------------ people
# no opacity fades: everyone stands behind the front panel row, which hides legs and feet
def person(name, layer_name, **kw):
    p = cut(name)
    pl = C.place(p, **kw)
    pl = C.rim_light(pl, AMBER, direction=(1, -0.5), width_px=5, strength=0.4)
    pl = C.light_wrap(pl, full(st.comp), width_px=6, strength=0.3)
    st.add(layer_name + " shadow", C.shadow_layer(pl, offset_mm=(-1.5, 1.0), blur_mm=4, opacity=0.3, color="#1A0F14"))
    st.add(layer_name, pl, src=C.src_layer(ROOT, name, **kw))


person("C3-E.png", "Renewable-energy engineer - penyelidikan", left_mm=-2, top_mm=94, height_mm=80)
person("C3-F.png", "Young professionals - rakyat / anak muda", left_mm=27, top_mm=110, width_mm=86)
person("UNI-C3-PDRM2_ins.png", "Police officer - PDRM", left_mm=90.62, top_mm=85.05, height_mm=104.44)

# ------------------------------------------------------------------ solar farm base
sol = C.load_rgb(os.path.join(ROOT, "assets/C3/C3-C_v2.png"))
# matte = everything below the front panel row's top edge (measured per column in the photo);
# a crisp edge, so the row reads as a real foreground object in front of the people
edge = np.interp(np.arange(sol.shape[1]), [0, 192, 384, 576, 864, 960, 1248, 1340, 1536],
                 [390, 406, 423, 437, 461, 463, 469, 472, 476]).astype(np.float32)
sm = np.clip(np.arange(sol.shape[0], dtype=np.float32)[:, None] - edge[None, :] + 0.5, 0, 1)
skw = dict(left_mm=-4, top_mm=141, width_mm=162, crop=(0, 0.30, 1, 1))     # full width: ~1.2x, was 2.2x
so = C.place(np.dstack([sol, sm]), **skw)
so[..., :3] = C.exposure(so[..., :3], -0.35)
st.add("Solar farm base", so)

shade = np.clip((yy - 140) / 56, 0, 1) ** 1.15 * 0.88
shade = shade * np.clip((120 - xx) / 32, 0.5, 1)
st.add("Shade - headline base", full(np.broadcast_to(C.hexf("#0B1430"), (H, W, 3)), shade))

# Jata + office block: a soft dark pad so the emblem pops over the flag
tr = np.clip(C.radial(120, 30, 46, 1.4) * 0.72 + C.radial(154, 0, 82, 1.7) * 0.4, 0, 0.82)
st.add("Shade - Jata + office text", full(np.broadcast_to(C.hexf("#0B1638"), (H, W, 3)), tr))
st.add("Shade - office text (soft burn)", full(np.broadcast_to(C.hexf("#0B1638"), (H, W, 3)),
                                               C.text_burn(ROOT, "C3") * 0.3))
# amber LINDUNGI / ASET NEGARA cross the engineer's white coat and the lit panel row: burn behind them
st.add("Shade - headline accent lines (soft burn)", full(np.broadcast_to(C.hexf("#0B1430"), (H, W, 3)),
       C.text_burn(ROOT, "C3", "Headline", feather_mm=2.5, spread_mm=(2.0, 1.2), rows_mm=(140, 168)) * 0.5))


def grade(c):
    g = C.curves(c, [(0, 0.012), (0.25, 0.23), (0.6, 0.62), (1, 0.985)])
    g = C.tint_shadows_highlights(g, shadow=(-0.004, -0.002, 0.012), highlight=(0.014, 0.006, -0.01))
    vign = 1 - C.radial(96, 112, 150, 1.0)
    return g * (1 - vign[..., None] * 0.18)


C.finalize_live(ROOT, "C3", OUT, "CGSO2026_C3_Ekonomi.psd", st, grade, fast=FAST)
print("C3 done")
