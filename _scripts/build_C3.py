"""Cover C3 - Ekonomi: 'Berhemah Hari Ini, Teguh Esok' (Tenaga, revised 27-28 Oct).

Zharief, 27 Oct 21:27: an oil-and-gas ship, coal, natural gas and a little TNB; police and Istana
removed. Then "jgn versi AI": every new energy element is a REAL photograph (sources and licences in
assets/_reference/SOURCES.md, cut-outs by _scripts/energy_prep.py). Layout = the approved blockout.

Sunrise low behind the tanker's bridge. The big Jalur Gemilang fades out above a clean dawn band;
on the far shore storage tanks (left) and TNB's Kapar coal power station with its pylons (right);
the oil tanker crosses in front, backlit, with its reflection; a red-and-white TNB tower stands on
the near bank with a TNB signboard; the gold chart dips and recovers over the ship; Su-30MKMs over
the flag; an oil-and-gas crew stand in the lalang on the near shore (review 28 Oct: the four civilians
removed), solar farm as the base.
Positive: no conflict imagery, white steam only.
Run: venv python -I _scripts/build_C3.py <workspace> [fast]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np

import comp as C
from comp import W, H, mm

ROOT = sys.argv[1]
FAST = len(sys.argv) > 2
OUT = os.path.join(ROOT, "04_Final", "C3")
os.makedirs(OUT, exist_ok=True)
cut = lambda n: C.load_rgba(os.path.join(ROOT, "03_Cutouts", n))
REF = lambda n: os.path.join(ROOT, "assets/_reference/C3_energy", n)
AMBER = "#FFB35A"
HAZE = C.hexf("#C99682")
DUSK = "#1E1218"                          # warm dusk-plum base (C2 owns navy)
SUN = (101.0, 95.0)                       # canvas mm, just above the horizon, behind the tanker's bridge
HZ = 104.0                                 # horizon (lifted 5 mm in the review: a taller energy band)
yy = np.arange(H, dtype=np.float32)[:, None] / mm(1)
xx = np.arange(W, dtype=np.float32)[None, :] / mm(1)


def full(rgb, a=None):
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = 1.0 if a is None else a
    return out


def as_rgba(rgb):
    return np.dstack([rgb, np.ones(rgb.shape[:2], np.float32)])


def backlit(rgba, ev, sat, shadow, haze=0.0, haze_col=HAZE):
    """A real daylight photo relit as backlit at sunrise: darker, cooler, less saturated, hazed."""
    rgb = C.exposure(rgba[..., :3], ev)
    rgb = C.saturation(rgb, sat)
    rgb = C.tint_shadows_highlights(rgb, shadow=shadow, highlight=(0.02, 0.008, -0.012))
    rgb = rgb * (1 - haze) + haze_col * haze
    out = rgba.copy()
    out[..., :3] = np.clip(rgb, 0, 1)
    return out


# ------------------------------------------------------------------ sky
sky = C.place(as_rgba(C.load_rgb(os.path.join(ROOT, "assets/C3/C3-A_v1.png"))), left_mm=0, top_mm=-24,
              width_mm=154)[..., :3]
sky = C.curves(sky, [(0, 0), (0.5, 0.47), (1, 0.97)])
sky = C.blend(sky, np.broadcast_to(C.hexf("#FFC27A"), sky.shape), C.radial(*SUN, 70, 2.4), "screen", 0.55)
sky = C.blend(sky, np.broadcast_to(C.hexf("#FFF1D2"), sky.shape), C.radial(*SUN, 10, 2.0), "screen", 0.9)
st = C.Stack("Sky - sunrise", sky)
# 9.5 review: the sunrise had no source. A visible sun just above the horizon, behind the tanker's
# bridge, is the cover's focal point: a near-white core, a warm corona and a wide low glow
# (in the clear gap between the bridge mast and the chimneys, a little above the light source used
# for the sea's glitter path, which stays under the bridge)
SD = (111.0, 82.5)
# review 28 Oct: the sun read as soft haze; a crisper, brighter disc and a tighter, hotter corona
sun_core = np.clip((1 - np.hypot(xx - SD[0], (yy - SD[1]) * 1.05) / 3.0) * 6, 0, 1)
# the halo warms the sky (amber, not white) so the near-white disc stands out against it
st.add("Sun - warm halo", full(np.broadcast_to(C.hexf("#E9963C"), (H, W, 3)), C.radial(SD[0], SD[1], 30, 1.6) * 0.42))
st.add("Sun - corona", full(np.broadcast_to(C.hexf("#FFC870"), (H, W, 3)), C.radial(SD[0], SD[1], 9, 1.6) * 0.75),
       mode="screen")
st.add("Sun - corona core", full(np.broadcast_to(C.hexf("#FFF4D6"), (H, W, 3)), C.radial(SD[0], SD[1], 4.2, 1.8)),
       mode="screen")
st.add("Sun - disc", full(np.broadcast_to(C.hexf("#FFF8E8"), (H, W, 3)), sun_core))

# ------------------------------------------------------------------ big flag (as 2025), fading out above the dawn band
flag = cut("FLAG_waving.png")
flag[..., :3] = C.exposure(flag[..., :3], -0.3)
flag[..., :3] = C.saturation(flag[..., :3], 0.85)                      # review 28 Oct: the scene, not the flag, leads
flag[..., :3] = C.tint_shadows_highlights(flag[..., :3], shadow=(0.0, -0.01, 0.03), highlight=(0.06, 0.03, -0.02))
# 9.5 review: the flag owned the top third and out-read the energy scene; smaller, and it clears
# the sky ~12 mm higher so the dawn band and sun carry the middle of the cover
fl = C.place(flag, left_mm=-24, top_mm=-7, width_mm=168, rotate=3)
fl[..., 3] *= np.clip(1 - (xx - 90) / 60, 0.2, 1) * np.clip((78 - yy) / 22, 0, 1) * 0.94
fl = C.rim_light(fl, AMBER, direction=(1, -0.5), width_px=6, strength=0.4)
st.add("Jalur Gemilang (exact vector on fabric)", fl)

# ------------------------------------------------------------------ jets (over the stripes, clear of the star)
jets = cut("R-SU30.png")                     # REAL RMAF Su-30MKMs (USAF photo, public domain; real_prep.py)
jets[..., :3] = C.exposure(jets[..., :3], -0.1) * C.hexf("#FFE2C2")
jkw = dict(cx_mm=86, cy_mm=23, width_mm=45, rotate=0)
jt = C.rim_light(C.place(jets, **jkw), AMBER, direction=(1, -0.3), width_px=4, strength=0.5)
st.add("Su-30MKM formation (real photo)", jt)

# ------------------------------------------------------------------ sea (real open water, Tinos)
seaimg = C.load_rgb(REF("Sea_Tinos.jpg"))
water = seaimg[1832:2752]
sea = C.place(as_rgba(water), left_mm=-33, top_mm=HZ - 0.2, width_mm=220)        # down past the solar row
srgb = C.saturation(sea[..., :3], 0.75)
t = np.clip((yy - HZ) / 44, 0, 1)[..., None]
srgb = srgb * (0.95 - 0.35 * t) + (HAZE * 0.6 + C.hexf("#5B4A66") * 0.4) * 0.18 * (1 - t)
# the sun's glitter path: the ripples' own highlights, warmed, in a column under the sun
L = C.lum(srgb)
crest = np.clip((L - cv2.GaussianBlur(L, (0, 0), 6)) * 6, 0, 1)
col = np.exp(-((xx - SUN[0]) / (2.5 + (yy - HZ) * 0.42)) ** 2) * np.clip((yy - HZ) / 1.5, 0, 1) * np.clip((142 - yy) / 22, 0, 1)
srgb = C.blend(srgb, np.broadcast_to(C.hexf("#FFD49A"), srgb.shape), np.clip(col * (0.35 + crest), 0, 1), "screen", 0.85)
sea[..., :3] = srgb
st.add("Sea (real photo)", sea)


# ------------------------------------------------------------------ far shore: storage tanks (left), TNB Kapar coal plant (right)
tanks = cut("E_TANKS.png")
tk = C.place(tanks, left_mm=50, top_mm=HZ + 0.3 - 13.3, width_mm=48, crop=(0, 0, 0.80, 1))
tk = backlit(tk, -0.5, 0.65, (0.0, 0.0, 0.03), haze=0.14)
tk = C.rim_light(tk, AMBER, direction=(1, -0.6), width_px=2, strength=0.35)
st.add("Storage tanks - gas (real photo, Pengerang)", tk)

coal = cut("E_COAL.png")
ch = 46 * coal.shape[0] / coal.shape[1]
co = C.place(coal, left_mm=106, top_mm=HZ + 0.4 - ch * 1023 / 1037, width_mm=46)
co = backlit(co, -1.1, 0.45, (0.0, 0.0, 0.03), haze=0.48)
st.add("Coal power station + TNB pylons (real photo, Kapar)", co)
st.add("Shoreline haze", full(np.broadcast_to(HAZE, (H, W, 3)), np.clip(1 - np.abs(yy - HZ + 1) / 7, 0, 1) * 0.38))

# ------------------------------------------------------------------ offshore: PETRONAS Dulang B platform (REAL, supplied; user_prep.py)
dul = cut("U-DULANG.png")
dk = C.place(dul, left_mm=-1, top_mm=HZ + 0.6 - 0.64 * 35, width_mm=35)
# asset review: the supplied photo is front-lit noon daylight; at sunrise it stands against the dawn,
# so its sea-facing side falls into a cool, hazed shadow and only the edges toward the sun catch light
dk = backlit(dk, -0.8, 0.68, (0.0, 0.0, 0.04), haze=0.18)
dk[..., :3] = C.curves(dk[..., :3], [(0, 0), (0.25, 0.19), (0.6, 0.64), (1, 1)])     # review 28 Oct: more contrast
dk = C.rim_light(dk, AMBER, direction=(1, -0.5), width_px=2, strength=0.65)
dref = np.zeros_like(dk)
dwl = int(round(mm(HZ + 0.6)))
span_d = min(dwl, H - dwl)
dref[dwl:dwl + span_d] = dk[dwl - span_d:dwl][::-1]
dref[..., :3] *= 0.6
dref[..., 3] = C.blur(dref[..., 3], 2) * np.clip(1 - (yy - HZ) / 4, 0, 1) * 0.4
st.add("Platform reflection", dref)
st.add("PETRONAS Dulang B offshore platform (real photo)", dk)

# ------------------------------------------------------------------ oil tanker (hero), backlit, with its reflection
TW = 75.0
tan = cut("E_TANKER.png")
th = TW * tan.shape[0] / tan.shape[1]
ttop = HZ + 3.2 - th * 928 / 938
tkw = dict(left_mm=34, top_mm=ttop, width_mm=TW)
sh = C.place(tan, **tkw)
sh = backlit(sh, -0.95, 0.95, (-0.005, -0.005, 0.03), haze=0.04)
sh[..., :3] = C.curves(sh[..., :3], [(0, 0), (0.25, 0.2), (0.6, 0.63), (1, 1)])          # backlit contrast, hull stays red-orange
sh = C.rim_light(sh, "#FFC27A", direction=(0.2, -1.0), width_px=3, strength=0.75)
sh = C.light_wrap(sh, full(st.comp), width_px=5, strength=0.45)
# reflection: mirrored about the waterline, broken by the sea's own ripples, fading down
wl = int(round(mm(HZ + 3.2)))
ref = np.zeros_like(sh)
span = min(wl, H - wl)
ref[wl:wl + span] = sh[wl - span:wl][::-1]
ripple = (L - cv2.GaussianBlur(L, (0, 0), 3)) * 40
mx, my = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
ref = cv2.remap(ref, mx + ripple * 2.2, my + ripple * 0.6, cv2.INTER_LINEAR)
ref = np.dstack([cv2.GaussianBlur(ref[..., :3], (0, 0), 1.2), cv2.GaussianBlur(ref[..., 3], (0, 0), 1.2)])
ref[..., 3] *= np.clip(1 - (yy - HZ - 3.2) / 7, 0, 1) * 0.55
ref[..., :3] = ref[..., :3] * 0.8
st.add("Tanker reflection", ref)
st.add("Oil tanker (real photo, Eagle San Diego)", sh)
# bow wave + wake from the sea's own crests: white water folding off the bow, a thin wash along the
# hull, and a dark wet contact line where the hull meets the water
wly = HZ + 3.2
crest_n = np.clip(crest * 1.6, 0, 1)
bow = np.exp(-(((xx - 35.5) / 3.2) ** 2 + ((yy - wly - 0.2) / 0.9) ** 2))
wash = np.exp(-((yy - wly - 0.25) / 0.45) ** 2) * np.clip((xx - 34) / 3, 0, 1) * np.clip((74 - xx) / 30, 0, 1)
foam = np.clip((bow * 0.9 + wash * 0.55) * (0.45 + crest_n), 0, 1)
st.add("Bow wave + wake (sea's own crests)", full(np.broadcast_to(C.hexf("#FFE9CC"), (H, W, 3)), foam), mode="screen", opacity=0.8)
hull_x = ((xx > 34.5) & (xx < 108.5)).astype(np.float32)
contact = np.exp(-((yy - wly + 0.05) / 0.22) ** 2) * hull_x
st.add("Waterline contact", full(np.broadcast_to(C.hexf("#120A0E"), (H, W, 3)), contact * 0.7))
st.add("Sun flare behind the bridge", full(np.broadcast_to(C.hexf("#FFE2B0"), (H, W, 3)), C.radial(SUN[0], SUN[1] + 1, 7, 2.2) * 0.55),
       mode="screen")

# ------------------------------------------------------------------ near bank (real grass from the Kapar photo), TNB tower + sign
field = C.load_rgb(REF("Pylons_KelanaJaya.jpg"))[1600:2448]                     # real lalang field under TNB lines (CC0)
bank = C.place(as_rgba(field), left_mm=98, top_mm=106.5, width_mm=60)
# a low grassy spit rising to the right: a ragged top edge cut from the grass's own blade texture,
# a darker wet foot at the waterline
top = np.maximum(111.6 - (xx - 108) * 0.07 + 1.1 * np.sin(xx * 0.31 + 1.3) + 0.5 * np.sin(xx * 0.83),
                 120.5 - (xx - 98) * 0.55)                                           # rolling top, long taper into the water
Lg = C.lum(bank[..., :3])
tuft = (cv2.GaussianBlur(Lg, (0, 0), 1.2) - cv2.GaussianBlur(Lg, (0, 0), 6.0)) * 22
edge = top - np.clip(tuft, -1.0, 1.0)
bank[..., 3] = np.clip((yy - edge) * mm(1) / 1.8, 0, 1) * np.clip((xx - 98) / 7, 0, 1) * (bank[..., 3] > 0)
bank = backlit(bank, -1.35, 0.55, (0.0, 0.0, 0.035))
bank[..., :3] *= (1 - np.clip((yy - edge) / 9, 0, 1) * 0.45)[..., None]           # darker toward the water
bank = C.rim_light(bank, AMBER, direction=(-0.5, -1), width_px=3, strength=0.55)
foot = np.exp(-((yy - 119.6) / 0.7) ** 2) * np.clip((xx - 104) / 8, 0, 1)
wl_b = 120.6 + np.clip(tuft, -1, 1) * 0.35 + np.sin(xx * 1.7) * 0.15               # an uneven waterline
bank[..., 3] *= np.clip((wl_b - yy) / 0.6, 0, 1)
wet = full(np.broadcast_to(C.hexf("#1C1620"), (H, W, 3)), foot * 0.6)

pyl = cut("E_PYLON.png")
pkw = dict(left_mm=118.5, top_mm=74.4, width_mm=33.0)
py = C.place(pyl, **pkw)
py = backlit(py, -1.7, 0.6, (0.0, 0.0, 0.03), haze=0.06)
py = C.rim_light(py, "#FFC27A", direction=(-1, -0.4), width_px=2, strength=0.7)
st.add("TNB 275 kV tower (real photo, Kapar)", py)
# the bank's reflection: mirrored about the waterline, dark, broken by the ripples
bref = np.zeros_like(bank)
wl_px = int(round(mm(120.6)))
span = min(wl_px, H - wl_px)
bref[wl_px:wl_px + span] = bank[wl_px - span:wl_px][::-1]
bref = cv2.remap(bref, mx + ripple * 2.0, my + ripple * 0.5, cv2.INTER_LINEAR)
bref[..., :3] *= 0.45
bref[..., 3] *= np.clip(1 - (yy - 120.6) / 5, 0, 1) * 0.6
st.add("Bank reflection", bref)
st.add("Near bank (real grass, Kelana Jaya)", bank)
st.add("Bank waterline", wet)

sign = cut("E_SIGN.png")
skw = dict(left_mm=124.0, top_mm=99.6, width_mm=14.4)
sg = C.place(sign, **skw)
# the board faces the camera with the sun behind it: its face is in shade (logo still legible), lit edges only
sg = backlit(sg, -1.45, 0.75, (0.0, 0.0, 0.035), haze=0.04)
sg = C.rim_light(sg, AMBER, direction=(-1, -0.5), width_px=2, strength=0.7)
st.add("TNB signboard shadow", C.shadow_layer(sg, offset_mm=(0.6, 0.4), blur_mm=0.8, opacity=0.35, color="#140D12"))
st.add("TNB signboard (real board, official TNB logo)", sg)

# ------------------------------------------------------------------ RMN escort on the open sea (review 28 Oct)
# The open water left of the crew read as empty; a Royal Malaysian Navy offshore patrol vessel, KD Kelantan
# (175), escorts the tanker: security on the energy route. REAL (US Navy 110126-N-6320L-821, PUBLIC
# DOMAIN; user_prep2.py), nearer than the tanker, so a little larger than its true scale beside it.
KEL = cut("R-RMN-KELANTAN.png")
KS = 34.0 / 850                                  # mm per source px (hull 30 -> 880 px = 34 mm)
WLK = 117.0                                      # waterline (canvas mm)
kkw = dict(left_mm=5.0 - 30 * KS, top_mm=WLK - 276 * KS, width_mm=960 * KS)
kk = C.place(KEL, **kkw)
kk = backlit(kk, -1.05, 0.7, (0.0, 0.0, 0.035), haze=0.1)
kk = C.rim_light(kk, AMBER, direction=(1, -0.6), width_px=2, strength=0.6)
kk = C.light_wrap(kk, full(st.comp), width_px=3, strength=0.35)
kref = np.zeros_like(kk)
kwl = int(round(mm(WLK)))
kspan = min(kwl, H - kwl)
kref[kwl:kwl + kspan] = kk[kwl - kspan:kwl][::-1]
kref = cv2.remap(kref, mx + ripple * 1.6, my + ripple * 0.5, cv2.INTER_LINEAR)
kref[..., :3] *= 0.7
kref[..., 3] *= np.clip(1 - (yy - WLK) / 3.5, 0, 1) * 0.5
st.add("Patrol vessel reflection", kref)
st.add("RMN patrol vessel KD Kelantan (real photo, US Navy, public domain)", kk)
kbow = np.exp(-(((xx - 38.6) / 1.8) ** 2 + ((yy - WLK - 0.1) / 0.6) ** 2))
kwash = np.exp(-((yy - WLK - 0.15) / 0.35) ** 2) * np.clip((xx - 5) / 2, 0, 1) * np.clip((39 - xx) / 3, 0, 1)
kwake = np.exp(-((yy - WLK - 0.3) / 0.5) ** 2) * np.clip((5 - xx) / 1.0 + 1, 0, 1) * np.clip((xx + 6) / 6, 0, 1)
kfoam = np.clip((kbow * 0.9 + kwash * 0.5 + kwake * 0.6) * (0.45 + crest_n), 0, 1)
st.add("Patrol vessel bow wave + wake", full(np.broadcast_to(C.hexf("#FFE9CC"), (H, W, 3)), kfoam), mode="screen", opacity=0.75)


# ------------------------------------------------------------------ rising line (in front of the scene, behind the people)
rl = C.load_rgba(os.path.join(ROOT, "02_Vectors/C3_Growth/C3_rising_line_300ppi.png"))
rlg = C.load_rgba(os.path.join(ROOT, "02_Vectors/C3_Growth/C3_rising_line_glow_300ppi.png"))
office = C.text_burn(ROOT, "C3", feather_mm=1.0)                  # no linework behind the small type
rl[..., 3] *= 1 - office
rlg[..., 3] *= 1 - office
# the line weaves behind the Dulang platform and the patrol vessel instead of scribbling across them
plat = C.blur(cv2.dilate((np.maximum(dk[..., 3], kk[..., 3]) > 0.3).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), 1.0)
rl[..., 3] *= 1 - plat
rlg[..., 3] *= 1 - plat * 0.85
st.add("Rising line glow", rlg, mode="screen", opacity=0.7)
st.add("Rising line", rl)


# ------------------------------------------------------------------ solar farm base
sol = C.load_rgb(os.path.join(ROOT, "assets/C3/C3-C_v2.png"))
edge = np.interp(np.arange(sol.shape[1]), [0, 192, 384, 576, 864, 960, 1248, 1340, 1536],
                 [390, 406, 423, 437, 461, 463, 469, 472, 476]).astype(np.float32)
sm = np.clip(np.arange(sol.shape[0], dtype=np.float32)[:, None] - edge[None, :] + 0.5, 0, 1)
skw2 = dict(left_mm=-12, top_mm=133, width_mm=178, crop=(0, 0.30, 1, 1))
so = C.place(np.dstack([sol, sm]), **skw2)
so[..., :3] = C.exposure(so[..., :3], -0.35)

# ------------------------------------------------------------------ foreground shore + oil-and-gas crew
# Review 28 Oct: the four civilians removed; the crew are the people of this cover. They stand
# waist-deep in real lalang on a shore that runs off the right edge, watching over the tanker; the
# roundel covers only grass. Field: Kelana Jaya under the TNB lines (CC0), its near part.
near = C.load_rgb(REF("Pylons_KelanaJaya.jpg"))[1450:2448]
shore = C.place(as_rgba(near), left_mm=60, top_mm=120, width_mm=100)
Lr = C.lum(shore[..., :3])
tuft2 = np.clip((cv2.GaussianBlur(Lr, (0, 0), 1.4) - cv2.GaussianBlur(Lr, (0, 0), 7.0)) * 26, -1.4, 1.4)
s_top = np.maximum(131.0 + 0.9 * np.sin(xx * 0.27 + 0.4) + 0.4 * np.sin(xx * 0.9), 150.0 - (xx - 68) * 0.8) - tuft2
shore[..., 3] = np.clip((yy - s_top) * mm(1) / 1.6, 0, 1) * (shore[..., 3] > 0)
shore = backlit(shore, -1.25, 0.6, (0.0, 0.0, 0.035))
shore[..., :3] *= (1 - np.clip((yy - 131) / 40, 0, 1) * 0.35)[..., None]
shore = C.rim_light(shore, "#FFC27A", direction=(-0.6, -1), width_px=3, strength=0.6)

# the land they stand on: a receding grass flat behind them that joins the TNB bank (so they read as
# on a promontory, not in the water); the taller near lalang (shore) hides their waists
back = C.place(as_rgba(near), left_mm=64, top_mm=116, width_mm=94)
Lb = C.lum(back[..., :3])
tb = np.clip((cv2.GaussianBlur(Lb, (0, 0), 1.2) - cv2.GaussianBlur(Lb, (0, 0), 6.0)) * 20, -0.8, 0.8)
b_top = np.maximum(121.2 + 0.4 * np.sin(xx * 0.5 + 1.0), 142.0 - (xx - 70) * 0.75) - tb
back[..., 3] = np.clip((yy - b_top) * mm(1) / 1.4, 0, 1) * (back[..., 3] > 0)
back = backlit(back, -1.45, 0.55, (0.0, 0.0, 0.035), haze=0.08)
back = C.rim_light(back, "#FFC27A", direction=(-0.6, -1), width_px=2, strength=0.5)
st.add("Promontory under the crew (real lalang)", back)

crew = cut("R-OG-CREW.png")                   # REAL (Pexels 28247164; real_prep2.py)
# they face the sunrise, so the backs we see are in shade; the coveralls stay orange, the sun rims hats and shoulders
crew = backlit(crew, -0.72, 0.88, (-0.005, 0.0, 0.035))                      # review 28 Oct: a step brighter
CW = 46.0                                     # 9.5 review: larger and closer, a clear human anchor
ckw = dict(left_mm=76, top_mm=110.0 - 0.063 * CW * crew.shape[0] / crew.shape[1], width_mm=CW)
cw = C.place(crew, **ckw)
cw = C.rim_light(cw, "#FFC27A", direction=(-0.3, -1), width_px=5, strength=0.95)
cw = C.light_wrap(cw, full(st.comp), width_px=6, strength=0.3)
st.add("O&G crew shadow", C.shadow_layer(cw, offset_mm=(1.5, 1.0), blur_mm=4, opacity=0.25, color="#1A0F14"))
st.add("Oil & gas crew (real photo)", cw)
st.add("Foreground shore (real lalang, Kelana Jaya)", shore)
st.add("Solar farm base", so)

shade = np.clip((yy - 140) / 56, 0, 1) ** 1.15 * 0.88
shade = shade * np.clip((120 - xx) / 32, 0.5, 1)
st.add("Shade - headline base", full(np.broadcast_to(C.hexf(DUSK), (H, W, 3)), shade))
st.add("Shade - roundel backing", full(np.broadcast_to(C.hexf(DUSK), (H, W, 3)), C.radial(118, 151.8, 30, 1.6) * 0.5))
tr = np.clip(C.radial(120, 30, 46, 1.4) * 0.72 + C.radial(154, 0, 82, 1.7) * 0.4, 0, 0.82)
st.add("Shade - Jata + office text", full(np.broadcast_to(C.hexf("#0B1638"), (H, W, 3)), tr))
st.add("Shade - office text (soft burn)", full(np.broadcast_to(C.hexf("#0B1638"), (H, W, 3)),
                                               C.text_burn(ROOT, "C3") * 0.3))
st.add("Shade - headline accent lines (soft burn)", full(np.broadcast_to(C.hexf(DUSK), (H, W, 3)),
       C.text_burn(ROOT, "C3", "Headline", feather_mm=2.5, spread_mm=(2.0, 1.2), rows_mm=(140, 168)) * 0.75))


def grade(c):
    g = C.curves(c, [(0, 0.012), (0.25, 0.23), (0.6, 0.62), (1, 0.985)])
    # thumbnail test: the energy scene (platform, tanker, plant) must out-read the flag at phone size
    band = (np.clip((yy - 82) / 8, 0, 1) * np.clip((128 - yy) / 10, 0, 1))[..., None]
    g = g * (1 + band * 0.1) + (g - 0.5) * band * 0.08
    g = C.tint_shadows_highlights(g, shadow=(-0.004, -0.002, 0.012), highlight=(0.014, 0.006, -0.01))
    vign = 1 - C.radial(96, 112, 150, 1.0)
    return g * (1 - vign[..., None] * 0.18)


C.finalize_live(ROOT, "C3", OUT, "CGSO2026_C3_Ekonomi.psd", st, grade, fast=FAST)
print("C3 done")
