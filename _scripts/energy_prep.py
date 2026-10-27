"""C3 Tenaga: cut-outs from the REAL photos (Zharief 27 Oct: "jgn versi AI"), sources in
assets/_reference/SOURCES.md (C3_energy/).

  E_TANKER  Eagle San Diego (CC0): name + "NO SMOKING / SAFETY FIRST" retouched out, BiRefNet matte
  E_TANKS   Pengerang storage tanks (CC BY-SA 4.0): terminal lettering + logo retouched out, sky key
  E_COAL    TNB Kapar coal power station + its pylons (CC BY-SA 4.0): sky key
  E_PYLON   the red-and-white TNB 275 kV tower from the same Kapar photo (blue sky behind it): sky key
  E_SIGN    the real roadside signboard from the Kapar photo, its face replaced by a white panel
            carrying the official TNB logo (Tenaga_Nasional.svg), warped to the board and given the
            board's own light and grain
Sky key: the sky is estimated per pixel from the clearly-blue pixels (normalised blur), each pixel's
distance to it in Lab becomes alpha, and the sky is unmixed out of the edges (thin lattice members
keep their own colour instead of a blue fringe).
Run: venv python -I _scripts/energy_prep.py <workspace>
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, "assets/_reference/C3_energy")
OUT = os.path.join(ROOT, "03_Cutouts")


def load(name, box=None):
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    if box:
        im = im.crop(box)
    return np.asarray(im, np.float32) / 255


def save(rgba, name):
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, name))
    print(name, rgba.shape[1], "x", rgba.shape[0])


def retouch(rgb, boxes, grow=3, thr=14):
    """Inpaint painted lettering: the ink inside each box (darker, or more saturated, than the wall)."""
    u8 = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    m = np.zeros(rgb.shape[:2], np.uint8)
    L = cv2.cvtColor(u8, cv2.COLOR_RGB2LAB).astype(np.float32)
    for x0, y0, x1, y1 in boxes:
        reg = L[y0:y1, x0:x1]
        wall = np.median(reg.reshape(-1, 3), axis=0)
        d = np.linalg.norm(reg - wall, axis=2)
        m[y0:y1, x0:x1] = (d > thr).astype(np.uint8)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    out = cv2.inpaint(u8, m * 255, 9, cv2.INPAINT_TELEA)
    # the inpaint is smooth: give it back the wall's grain
    rng = np.random.default_rng(5)
    hp = (u8.astype(np.float32) - cv2.GaussianBlur(u8.astype(np.float32), (0, 0), 1.5))
    sd = float(hp[m == 0].std()) * 0.8
    nz = cv2.GaussianBlur(rng.normal(0, sd, rgb.shape[:2]).astype(np.float32), (0, 0), 0.7)[..., None]
    out = np.clip(out.astype(np.float32) + nz * (m[..., None] > 0), 0, 255)
    return out / 255


def clone(rgb, box, dy, feather=12):
    """Cover a box with the same-size patch dy rows away (plain painted plate), soft-edged."""
    x0, y0, x1, y1 = box
    out = rgb.copy()
    m = np.zeros(rgb.shape[:2], np.float32)
    m[y0:y1, x0:x1] = 1
    m = cv2.GaussianBlur(m, (0, 0), feather / 2)[..., None]
    src = np.roll(rgb, -dy, axis=0)
    return out * (1 - m) + src * m


def sky_key(rgb, blue_b=-9.0, lo=5.0, hi=13.0, sigma=35):
    """alpha from the distance to a smooth per-pixel sky estimate; sky unmixed from the edges."""
    lab = cv2.cvtColor(rgb.astype(np.float32), cv2.COLOR_RGB2LAB)
    sky = (lab[..., 2] < blue_b) & (lab[..., 0] > 35)
    sky = cv2.erode(sky.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    w = cv2.GaussianBlur(sky, (0, 0), sigma)
    est = np.dstack([cv2.GaussianBlur(rgb[..., c] * sky, (0, 0), sigma) for c in range(3)]) / np.maximum(w, 1e-4)[..., None]
    # fill where no sky was nearby: nearest known sky by a wider blur
    w2 = cv2.GaussianBlur(sky, (0, 0), sigma * 4)
    est2 = np.dstack([cv2.GaussianBlur(rgb[..., c] * sky, (0, 0), sigma * 4) for c in range(3)]) / np.maximum(w2, 1e-4)[..., None]
    est = np.where((w > 0.02)[..., None], est, est2)
    elab = cv2.cvtColor(np.clip(est, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)
    d = np.linalg.norm((lab - elab) * [0.6, 1, 1], axis=2)
    a = np.clip((d - lo) / (hi - lo), 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 0.5)
    fg = (rgb - (1 - a[..., None]) * est) / np.maximum(a[..., None], 0.08)
    fg = np.where(a[..., None] > 0.08, np.clip(fg, 0, 1), rgb)
    return np.dstack([fg, a])


def keep_rows(rgba, y_cut, feather=3):
    """Hard bottom edge (the base sits on the horizon / behind the bank)."""
    h = rgba.shape[0]
    r = np.clip((y_cut - np.arange(h, dtype=np.float32)) / feather, 0, 1)
    rgba[..., 3] *= r[:, None]
    return rgba


def fade_sides(rgba, frac=0.08):
    w = rgba.shape[1]
    x = np.arange(w, dtype=np.float32) / w
    rgba[..., 3] *= np.clip(np.minimum(x, 1 - x) / frac, 0, 1)[None, :]
    return rgba


# ------------------------------------------------------------------ tanker (BiRefNet)
from rembg import new_session, remove

T_BOX = (497, 351, 7385, 2838)
t = load("Tanker_EagleSanDiego.jpg")
t = clone(t, (2560, 2165, 3430, 2330), dy=175)                             # EAGLE SAN DIEGO: clean hull below it
t = retouch(t, [(5535, 1468, 6035, 1592)], grow=3)                         # NO SMOKING / SAFETY FIRST
t = t[T_BOX[1]:T_BOX[3], T_BOX[0]:T_BOX[2]]
s = 2600 / t.shape[1]
t = cv2.resize(t, (2600, int(t.shape[0] * s)), interpolation=cv2.INTER_AREA)
mask = remove(Image.fromarray((t * 255).astype(np.uint8)), session=new_session("birefnet-general"), only_mask=True)
a = np.asarray(mask, np.float32) / 255
n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])                                # the ship only (no tug, no mast)
keep = cv2.dilate((labs == big).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
a *= keep
save(np.dstack([t, a]), "E_TANKER.png")

# ------------------------------------------------------------------ storage tanks (sky key, retouched)
k = load("Tanks_Pengerang.jpg")
k = retouch(k, [(440, 2150, 625, 2345), (640, 2205, 1135, 2335)], grow=4)
k0 = k[1644:2500, 113:3968]
k = keep_rows(sky_key(k0, blue_b=-6), 2486 - 1644)                         # cut at the hoarding top
# the domes' shaded side is nearly sky-coloured: tanks are solid, so every column is filled below
# its first clearly-opaque row (the soft top edge is kept)
solid = np.maximum.accumulate((k[..., 3] > 0.6).astype(np.float32), axis=0)
solid = cv2.morphologyEx(solid, cv2.MORPH_OPEN, np.ones((1, 9), np.uint8))           # no lone rail posts
solid = cv2.GaussianBlur(solid, (0, 0), 0.8)
k[..., 3] = np.maximum(k[..., 3], solid)
k[..., :3] = k[..., :3] * (1 - solid[..., None]) + k0 * solid[..., None]          # the photo's own wall, not unmixed
k = keep_rows(k, 2486 - 1644)
save(k, "E_TANKS.png")

# ------------------------------------------------------------------ coal power station + pylons (Kapar)
c = load("Coal_Kapar_SSAA.jpg", (1590, 1147, 3648, 2184))
c = keep_rows(sky_key(c), 2172 - 1147)
save(fade_sides(c, 0.04), "E_COAL.png")

# ------------------------------------------------------------------ foreground TNB tower (Kapar, upper 2/3 against blue sky)
p = load("Coal_Kapar_SSAA.jpg", (600, 40, 1700, 1500))
p = sky_key(p, lo=4.0, hi=11.0, sigma=25)
save(fade_sides(p, 0.14), "E_PYLON.png")

# ------------------------------------------------------------------ signboard with the TNB logo
import pymupdf as fitz

SB = (470, 1940, 800, 2350)                                                  # crop holding the board and posts
sb = load("Coal_Kapar_SSAA.jpg", SB)
H, W = sb.shape[:2]
BOARD = np.float32([(509.6, 1959.6), (761.7, 1972.0), (757.5, 2086.7), (503.3, 2084.6)]) - SB[:2]
POSTS = [np.float32([(539, 2091), (550, 2091), (521, 2340), (509, 2340)]) - SB[:2],
         np.float32([(689, 2094), (698, 2094), (679, 2340), (667, 2340)]) - SB[:2]]
S4 = 4
m = np.zeros((H * S4, W * S4), np.uint8)
cv2.fillConvexPoly(m, (BOARD * S4).astype(np.int32), 255)
for q in POSTS:
    cv2.fillConvexPoly(m, (q * S4).astype(np.int32), 255)
alpha = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
# the board's light: its own lightness, smoothed (folds of the photo's light, not its lettering)
L = cv2.cvtColor(sb, cv2.COLOR_RGB2LAB)[..., 0] / 100
bm = np.zeros((H, W), np.uint8)
cv2.fillConvexPoly(bm, BOARD.astype(np.int32), 1)
shade = cv2.GaussianBlur(np.where(bm > 0, L, 0).astype(np.float32), (0, 0), 18) / np.maximum(
    cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 18), 1e-3)
shade = shade / np.median(shade[bm > 0])
# the face: white panel, logo centred with margins (rendered from the official SVG)
doc = fitz.open(os.path.join(SRC, "TNB_logo.svg"))
pix = doc[0].get_pixmap(alpha=True, matrix=fitz.Matrix(2, 2))
logo = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n).astype(np.float32) / 255
FW, FH = 1200, 560
face = np.ones((FH, FW, 3), np.float32) * np.float32([0.93, 0.93, 0.91])
lw = int(FW * 0.80)
lh = int(logo.shape[0] * lw / logo.shape[1])
lg = cv2.resize(logo, (lw, lh), interpolation=cv2.INTER_AREA)
x0, y0 = (FW - lw) // 2, (FH - lh) // 2
la = lg[..., 3:4]
face[y0:y0 + lh, x0:x0 + lw] = face[y0:y0 + lh, x0:x0 + lw] * (1 - la) + lg[..., :3] * la
cv2.rectangle(face, (6, 6), (FW - 7, FH - 7), (0.62, 0.63, 0.64), 10)                 # the board's metal edge
M = cv2.getPerspectiveTransform(np.float32([[0, 0], [FW, 0], [FW, FH], [0, FH]]), np.float32(BOARD * S4))
fw = cv2.warpPerspective(face, M, (W * S4, H * S4), flags=cv2.INTER_LINEAR)
fw = cv2.resize(fw, (W, H), interpolation=cv2.INTER_AREA)
fm = cv2.resize(cv2.warpPerspective(np.ones((FH, FW), np.float32), M, (W * S4, H * S4)), (W, H), interpolation=cv2.INTER_AREA)
fw = fw * np.clip(shade, 0.6, 1.3)[..., None] * 0.92
rng = np.random.default_rng(11)
hp = sb - cv2.GaussianBlur(sb, (0, 0), 1.2)
nz = cv2.GaussianBlur(rng.normal(0, float(hp[bm > 0].std()) * 0.7, (H, W)).astype(np.float32), (0, 0), 0.6)[..., None]
fw = np.clip(fw + nz, 0, 1)
rgb = sb * (1 - fm[..., None]) + fw * fm[..., None]
# posts: the photo's own posts, darkened slightly so they read as steel, not fence
save(np.dstack([rgb, alpha]), "E_SIGN.png")
print("energy prep done")
