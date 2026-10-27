"""Istana Negara base plate from the real photo (CEphoto, Uwe Aranas, CC BY-SA 3.0).

- refine the BiRefNet mask with a guided filter at working resolution
- fade out the lawn/fence at the bottom
- push the background apartment/pyramid buildings back with atmospheric haze
  (no architecture is invented, removed or mirrored)
Output: 03_Cutouts/ISTANA_base.png (RGBA, 3600 px wide)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np
from PIL import Image, ImageDraw

import comp as C

ROOT = sys.argv[1]
src = Image.open(os.path.join(ROOT, "assets/_reference/Istana_Negara_Jalan_Duta.jpg")).convert("RGB")
FW, FH = src.size
WW = 3600
S = WW / FW
WH = int(round(FH * S))
img = np.asarray(src.resize((WW, WH), Image.LANCZOS), np.float32) / 255
mask = np.asarray(Image.open(os.path.join(ROOT, "03_Cutouts/ISTANA_mask.png")).resize((WW, WH), Image.BILINEAR),
                  np.float32) / 255

# edge refinement: guided filter on luminance, then tighten
g = C.lum(img).astype(np.float32)
a = C.guided_filter(g, mask, 4, 2e-3)
a = np.clip((a - 0.3) / 0.4, 0, 1)
a = a * a * (3 - 2 * a)

# spire needle + finial: the rod above the main finial is ~2 px wide against the overcast sky, too
# thin for the segmentation mask, so it came out missing or half-transparent and dragged grey sky
# along (the finial's edges too). Matte it from its contrast with the local sky (median of the
# columns either side) and decontaminate every edge pixel; nothing is drawn that isn't in the photo.
NX0, NX1, NY0, NY1 = 1780, 1845, 40, 430           # working px around the main spire and finial
sky_cols = np.r_[NX0 - 80:NX0 - 30, NX1 + 30:NX1 + 80]
na = np.zeros((NY1 - NY0, NX1 - NX0), np.float32)
sky = np.zeros((NY1 - NY0, 3), np.float32)
for i, y in enumerate(range(NY0, NY1)):
    sky[i] = np.median(img[y, sky_cols], axis=0)
    na[i] = np.clip((C.lum(sky[i]) - g[y, NX0:NX1] - 0.03) / 0.18, 0, 1)
na = cv2.GaussianBlur(na, (0, 0), sigmaX=0.01, sigmaY=1.0)          # no row-to-row flicker along the rod
box = (slice(NY0, NY1), slice(NX0, NX1))
A = np.maximum(a[box], na)
dist = np.linalg.norm(img[box] - sky[:, None, :], axis=2)              # pure-sky pixels the mask kept solid
A *= np.clip((dist - 0.03) / 0.06, 0, 1)
part = ((A > 0.02) & (A < 0.98))[..., None]
dec = (img[box] - (1 - A[..., None]) * sky[:, None, :]) / np.maximum(A[..., None], 0.25)
img[box] = np.where(part, np.clip(dec, 0, 1), img[box])
a[box] = A

# bottom: keep the facade down to the fence line, soft fade below
full_to_w = lambda x, y: (x * S, y * S)
fence_y = 3440 * S
yy = np.arange(WH, dtype=np.float32)[:, None]
a *= np.clip((fence_y + 25 - yy) / 50, 0, 1)

# background buildings (behind the right wing): display-crop coords -> full res
def crop2full(dx, dy):
    return 3500 + dx / 0.5939, 1350 + dy / 0.5939

# The pyramid-roofed block and the apartment tower behind the right wing are not part of the palace:
# they are cut out along the palace's real outline (traced at 4-5x zoom in working px; straight roof
# edges snapped to the strongest luminance edge per column), keeping the royal standard, the Jalur
# Gemilang and its pole in front of them. The earlier hand-drawn block, softened 6 px and only faded
# on each cover, left a pale ghost, a flat cut through the drum and a stepped notch.
L = C.lum(img)


def snap(x0, x1, y_at, win=8):
    """Roof edge between x0 and x1: per column, the row of the strongest vertical luminance step
    within +-win of the traced guess, median-filtered so the line stays straight where it is."""
    xs = np.arange(x0, x1 + 1)
    ys = []
    for x in xs:
        g = int(round(y_at(x)))
        col = L[g - win - 1:g + win + 2, max(0, x - 2):x + 3].mean(axis=1)
        d = np.abs(col[2:] - col[:-2])
        ys.append(g - win + int(np.argmax(d)))
    ys = np.array(ys, np.float32)
    ys = np.array([np.median(ys[max(0, i - 6):i + 7]) for i in range(len(ys))])
    return [(float(x), float(y)) for x, y in zip(xs[::3], ys[::3])] + [(float(xs[-1]), float(ys[-1]))]


lin = lambda pts: (lambda x: np.interp(x, [p[0] for p in pts], [p[1] for p in pts]))
drum_l = snap(2381, 2550, lin([(2381, 1242), (2550, 1248)]))                  # drum cap, left of the flag
drum_r = snap(2603, 2712, lin([(2603, 1260), (2660, 1274), (2712, 1291)]))    # drum cap, right of the flag
ledge = snap(2752, 2950, lambda x: 1409)                                       # right-wing corbel top
ledge2 = snap(2906, 3268, lambda x: 1511)                                      # lower right-wing ledge
poly = ([(2396, 860), (3340, 860), (3340, 1593), (3268, 1593)] + ledge2[::-1] +
        [(2906, 1471), (2912, 1466), (2920, 1456), (2921, 1442), (2930, 1432), (2940, 1424), (2950, 1413)] +
        ledge[::-1] +
        [(2746, 1407), (2741, 1397), (2734, 1387), (2726, 1377), (2718, 1368), (2708, 1362), (2694, 1355),
         (2681, 1350), (2672, 1346),                                              # upper-right dome outline
         (2680, 1339), (2686, 1331), (2693, 1321), (2700, 1313), (2709, 1303), (2715, 1297)] +  # drum-end bowl
        drum_r[::-1] +
        [(2600, 1248), (2598, 1240), (2593, 1222), (2589, 1205), (2586, 1190), (2583, 1175), (2581, 1162),
         (2580, 1160), (2580, 1100), (2582, 1094), (2579, 1088), (2575, 1086), (2570, 1088), (2567, 1094),
         (2569, 1100), (2568, 1162), (2565, 1166), (2562, 1180), (2558, 1195), (2555, 1210), (2552, 1225),
         (2550.5, 1240)] +                                                        # flag + pole (kept, 6x trace)
        drum_l[::-1] + [(2381, 990), (2396, 990)])                                # royal standard (kept)
SS4 = 4
big = Image.new("L", (WW * SS4, WH * SS4), 0)
ImageDraw.Draw(big).polygon([(x * SS4, y * SS4) for x, y in poly], fill=255)
bgm = np.asarray(big.resize((WW, WH), Image.BOX), np.float32) / 255              # crisp, anti-aliased
Image.fromarray(C.to_u8(bgm), "L").save(os.path.join(ROOT, "03_Cutouts/ISTANA_bgmask.png"))

a *= 1 - bgm                                       # background buildings removed (the covers' own sky shows)
rgba = np.dstack([img, a])
Image.fromarray(C.to_u8(rgba), "RGBA").save(os.path.join(ROOT, "03_Cutouts/ISTANA_base.png"))
# geometry notes for placement (working px)
dome_c = (2866 * S, 1150 * S)
print("working size", WW, WH, "dome centre", [round(v) for v in dome_c], "spire top y", round(270 * S),
      "fence y", round(fence_y))
