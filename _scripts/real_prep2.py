"""Real photographs, round 2 (28 Oct): Zharief "orang yang pakai baju kapten, oil and gas"; Anaqi:
real photos wherever they fit.

  R-OG-CREW  two oil-and-gas crew in coveralls and hard hats on a ship's deck, from behind
             (Pexels 28247164). Company logo and safety patch on the right man's back retouched
             out; the deck sign between them excluded; BiRefNet matte; mirrored so they watch left.
  R-FERNS    real rainforest ferns (Pexels 38145936) as C1's front foliage border: the bright
             yellow-green fronds are keyed against the darker bush behind, so the fronds form a
             natural ragged top edge; solid below.
Output: 03_Cutouts/<id>.png. Run: venv python -I _scripts/real_prep2.py <workspace>
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from pymatting import estimate_foreground_ml
from rembg import new_session, remove

ROOT = sys.argv[1]
REF = os.path.join(ROOT, "assets/_reference")
OUT = os.path.join(ROOT, "03_Cutouts")


def save(rgba, name):
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, name))
    print(name, rgba.shape[1], "x", rgba.shape[0])


# ------------------------------------------------------------------ O&G crew
src = Image.open(os.path.join(REF, "C3_energy/OG_crew_pexels_28247164.jpg")).convert("RGB")
s = src.width / 1000                                            # boxes measured on the 1000 px preview
P = lambda pts: np.int32(np.float32(pts) * s)
img = np.asarray(src, np.uint8).copy()
# retouch: the "MM" logo and the safety patch on the right man's back, filled from the coverall
m = np.zeros(img.shape[:2], np.uint8)
cv2.fillPoly(m, [P([(350, 428), (425, 428), (425, 478), (350, 478)])], 255)
cv2.fillPoly(m, [P([(342, 478), (452, 478), (452, 580), (342, 580)])], 255)
lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
fill = cv2.inpaint(img, m, 25, cv2.INPAINT_TELEA).astype(np.float32)
# the inpaint is flat: give it back the coverall's own light falloff (heavy blur of the original,
# the print excluded) and its cloth grain
area = cv2.dilate(m, np.ones((61, 61), np.uint8))
cloth = (area > 0) & (m == 0)
L = lab[..., 0]
Lw = cv2.GaussianBlur(np.where(cloth, L, 0), (0, 0), 40) / np.maximum(cv2.GaussianBlur(cloth.astype(np.float32), (0, 0), 40), 1e-3)
Lf = cv2.cvtColor(np.clip(fill, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
hp = img.astype(np.float32) - cv2.GaussianBlur(img.astype(np.float32), (0, 0), 1.5)
sd = float(hp[cloth].std())
fill += cv2.GaussianBlur(np.random.default_rng(3).normal(0, sd, img.shape[:2]).astype(np.float32), (0, 0), 0.8)[..., None]
w = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 6)[..., None]
img = np.clip(img * (1 - w) + fill * w, 0, 255).astype(np.uint8)
# crop: both men from the hard hats to the waist (the rail and lower deck below are not needed)
x0, y0, x1, y1 = P([(105, 215)])[0].tolist() + P([(600, 495)])[0].tolist()
crop = Image.fromarray(img[y0:y1, x0:x1])
crop = crop.resize((crop.width // 2, crop.height // 2), Image.LANCZOS)        # 1130 x 647: ample for ~46 mm
a = np.asarray(remove(crop, session=new_session("birefnet-general"), only_mask=True), np.float64) / 255
# the deck sign the left man holds stands between them: not part of the crew
k = 0.5
sign = np.zeros(a.shape, np.uint8)
cv2.fillPoly(sign, [np.int32((np.float32([(280, 440), (335, 440), (335, 495), (280, 495)]) * s - [x0, y0]) * k)], 1)
cv2.fillPoly(sign, [np.int32((np.float32([(264, 420), (292, 420), (292, 495), (264, 495)]) * s - [x0, y0]) * k)], 1)   # deck rail post
a *= 1 - cv2.GaussianBlur(sign.astype(np.float64), (0, 0), 1.5)
n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
keep = np.zeros_like(a)
for i in np.argsort(-st[1:, cv2.CC_STAT_AREA])[:2] + 1:
    keep = np.maximum(keep, cv2.dilate((labs == i).astype(np.uint8), np.ones((7, 7), np.uint8)))
a *= keep
rgb = np.asarray(crop, np.float64) / 255
fg = estimate_foreground_ml(rgb, a)
save(np.dstack([fg, a])[:, ::-1], "R-OG-CREW.png")                            # mirrored: they watch left

# ------------------------------------------------------------------ ferns (colour key: fronds vs. dark bush)
f = Image.open(os.path.join(REF, "C1_real/Ferns_pexels_38145936.jpg")).convert("RGB")
f = f.resize((3000, round(f.height * 3000 / f.width)), Image.LANCZOS)
fs = 3000 / 1000
fr = np.asarray(f, np.float32)[int(190 * fs):, :] / 255                       # below the hazy palm line
lab = cv2.cvtColor(fr, cv2.COLOR_RGB2LAB)
Lc, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
frond = np.clip((Lc - 42) / 10, 0, 1) * np.clip((B - 22) / 10, 0, 1) * np.clip((-A - 6) / 8, 0, 1)
frond = cv2.morphologyEx(frond, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
h = fr.shape[0]
yy = np.arange(h, dtype=np.float32)[:, None] / h
# only sharp fronds count (the blurred background leaves are soft): local detail energy
g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
sharp = cv2.GaussianBlur(np.abs(g - cv2.GaussianBlur(g, (0, 0), 2)), (0, 0), 6)
frond *= np.clip((sharp - 0.012) / 0.01, 0, 1)
# a ragged bush top (from the bush's own texture), solid below it
rag = cv2.GaussianBlur(g, (0, 0), 9) - cv2.GaussianBlur(g, (0, 0), 30)
solid = np.clip((yy - 0.47 + rag * 0.9) / 0.015, 0, 1)
alpha = np.maximum(frond, solid)
# keep only fronds connected to the bush mass
n, labs = cv2.connectedComponents((alpha > 0.35).astype(np.uint8))
base = set(np.unique(labs[-5:, :])) - {0}
alpha *= np.isin(labs, list(base))
alpha = cv2.GaussianBlur(alpha, (0, 0), 0.8)
save(np.dstack([fr, alpha]), "R-FERNS.png")
print("round 2 done")
