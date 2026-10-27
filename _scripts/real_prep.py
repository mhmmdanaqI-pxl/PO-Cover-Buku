"""Real photographs in place of the generated security assets (Zharief 27 Oct: "jgn versi AI").

  R-C2-PDRM  the PDRM officer (right) from Police-officer-at-Johore 014.jpg (Rizuan, CC BY-SA 3.0):
             current working uniform, peaked cap, real crests. BiRefNet, split from his colleague.
  R-SU30     two RMAF Su-30MKMs (USAF photo, public domain): BiRefNet; the tanker's refuelling
             hose and drogue are erased from the lead jet's probe.
  R-C130     RMAF C-130H in flight, seen from below (Pangalau, CC BY-SA 4.0): keyed against the grey
             sky by luminance, then enlarged 2.4x with Lanczos + a light unsharp. Classical
             resampling only (no AI upscaler, which would invent detail); a dark silhouette has no
             fine texture to lose.
Output: 03_Cutouts/<id>.png. Run: venv python -I _scripts/real_prep.py <workspace>
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
SESS = new_session("birefnet-general")


def load(path, width=None):
    im = Image.open(os.path.join(REF, path)).convert("RGB")
    if width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im


def matte(im):
    a = np.asarray(remove(im, session=SESS, only_mask=True), np.float64) / 255
    rgb = np.asarray(im, np.float64) / 255
    return rgb, a


def save(rgb, a, name):
    fg = estimate_foreground_ml(rgb, a)                      # no background colour left in the edges
    rgba = np.dstack([np.clip(fg, 0, 1), a])
    Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, name))
    print(name, rgba.shape[1], "x", rgba.shape[0])


def largest(a, thr=0.5):
    n, labs, st, _ = cv2.connectedComponentsWithStats((a > thr).astype(np.uint8))
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    keep = cv2.dilate((labs == big).astype(np.uint8), np.ones((7, 7), np.uint8))
    return a * keep


# ------------------------------------------------------------------ PDRM officer (1536 x 2048)
im = load("C2_real/PDRM_Johor_Rizuan.jpg", 1536)
rgb, a = matte(im)
s = 1536 / 2304
xs = np.arange(a.shape[1], dtype=np.float64)[None, :]
a *= np.clip((xs - 1212 * s) / 4, 0, 1)                    # his colleague (beret) stands to the left
save(rgb, largest(a), "R-C2-PDRM.png")

# ------------------------------------------------------------------ Su-30MKM formation (2400 wide)
im = load("Su30MKM_detail.jpg", 2400)
rgb, a = matte(im)
s = 2400 / 1200                                              # measured on the 1200 px preview
H, W = a.shape
hose = np.zeros((H, W), np.uint8)
cv2.fillPoly(hose, [np.int32(np.float32([(0, 392), (505, 388), (505, 418), (0, 420)]) * s)], 1)
cv2.fillPoly(hose, [np.int32(np.float32([(470, 376), (527, 376), (527, 423), (470, 423)]) * s)], 1)   # the drogue basket
a *= 1 - cv2.GaussianBlur(hose.astype(np.float64), (0, 0), 1.5)
n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
keep = np.zeros_like(a)
for i in np.argsort(-st[1:, cv2.CC_STAT_AREA])[:2] + 1:    # lead + wingman (the far third mattes badly)
    keep = np.maximum(keep, cv2.dilate((labs == i).astype(np.uint8), np.ones((7, 7), np.uint8)))
save(rgb, a * keep, "R-SU30.png")

# ------------------------------------------------------------------ C-130H in flight (luminance key, 2.4x)
im = load("C130H_flight.jpg")
c = np.asarray(im, np.float32)[860:1180, 360:760] / 255      # aircraft with a margin (full-res px)
L = cv2.cvtColor(c, cv2.COLOR_RGB2LAB)[..., 0]
sky = cv2.medianBlur(np.clip(L * 2.55, 0, 255).astype(np.uint8), 101).astype(np.float32) / 2.55   # local sky level
a = np.clip((sky - L - 7) / 14, 0, 1)
a = largest(a, 0.3)
# the lit belly sits close to the sky's value: fill every hole inside the silhouette
# (small holes only: the real sky gaps between nacelles and fuselage stay open)
solid = (a > 0.3).astype(np.uint8)
n, labs, st, _ = cv2.connectedComponentsWithStats(1 - solid, connectivity=4)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] < 40:
        solid[labs == i] = 1
a = np.maximum(a, cv2.GaussianBlur(cv2.erode(solid, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.7))
# partial-alpha speckle on the lit belly: close small semi-transparent pits only (gaps stay open)
closed = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
pits = ((closed - a) > 0.08).astype(np.uint8)
n, labs, st, _ = cv2.connectedComponentsWithStats(pits)
small = np.isin(labs, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < 60])
a = np.where(small, closed, a)
k = 2.4
c2 = cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
a2 = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
c2 = cv2.bilateralFilter(c2, 9, 0.08, 5)                   # the silhouette is one dark paint: no sensor speckle
core = cv2.erode((a2 > 0.95).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
med = cv2.medianBlur((c2 * 255).astype(np.uint8), 7).astype(np.float32) / 255
med = np.minimum(med, cv2.GaussianBlur(med, (0, 0), 6))      # the belly is uniform shade, never lighter than its surroundings
w = cv2.GaussianBlur(core, (0, 0), 2)[..., None]
c2 = c2 * (1 - w) + med * w
c2 = np.clip(c2 + (c2 - cv2.GaussianBlur(c2, (0, 0), 1.2)) * 0.25, 0, 1)
Image.fromarray((np.dstack([c2, np.clip(a2, 0, 1)]) * 255 + 0.5).astype(np.uint8), "RGBA").save(
    os.path.join(OUT, "R-C130.png"))
print("R-C130.png", c2.shape[1], "x", c2.shape[0])
