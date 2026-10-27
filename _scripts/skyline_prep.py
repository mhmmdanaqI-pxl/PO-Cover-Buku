"""KL skyline silhouette from the real night photo (Azreey, CC BY-SA 4.0).
The sky is modelled per column (smooth), and each column's skyline top is where
the image departs from that model. Real building shapes, no generation.
Output: 03_Cutouts/SKYLINE_silhouette.png (L, 2400 px wide)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np
from PIL import Image

import comp as C

ROOT = sys.argv[1]
src = Image.open(os.path.join(ROOT, "assets/_reference/KL_skyline.jpg")).convert("RGB")
Wd = 2400
s = Wd / src.width
img = np.asarray(src.resize((Wd, int(src.height * s)), Image.LANCZOS), np.float32) / 255
h, w = img.shape[:2]
I = C.blur(img, 1.2)
# sky model: per-column median of the clean top band, plus a vertical trend
top_band = I[: int(0.18 * h)]
col = np.median(top_band, axis=0)                             # (w, 3)
rows = np.arange(h, dtype=np.float32)
k = int(0.42 * h)
trend = np.zeros((h, 3), np.float32)
trend[:k] = np.median(I[:k] - col[None], axis=1)            # average change with height
trend[k:] = trend[k - 1]
sky = col[None] + trend[:, None]
D = np.abs(I - sky).max(axis=2)
D = C.blur(D, 0.8)
bld = (D > 0.045).astype(np.uint8)
bld = cv2.morphologyEx(bld, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
# a building column starts where 'building' persists downward
run = cv2.boxFilter(bld.astype(np.float32), -1, (1, 25), anchor=(0, 0), normalize=True, borderType=cv2.BORDER_REPLICATE)
top = np.full(w, h, np.int32)
for x in range(w):
    r = np.where(run[:, x] > 0.85)[0]
    r = r[r > int(0.10 * h)]
    if len(r):
        top[x] = r.min()
top = cv2.medianBlur(top.astype(np.float32)[None, :], 3)[0]
sil = (rows[:, None] >= top[None, :]).astype(np.float32)
# KL Tower from BiRefNet (thin, caught well there)
kt = np.asarray(Image.open(os.path.join(ROOT, "03_Cutouts/SKYLINE_mask.png")).resize((w, h), Image.BILINEAR),
                np.float32) / 255
sil = np.maximum(sil, kt)
sil = C.guided_filter(C.lum(img), sil, 2, 2e-3)
Image.fromarray(C.to_u8(np.clip(sil, 0, 1)), "L").save(os.path.join(ROOT, "03_Cutouts/SKYLINE_silhouette.png"))
print("skyline", w, h, "top min/max", int(top.min()), int(np.median(top)))
