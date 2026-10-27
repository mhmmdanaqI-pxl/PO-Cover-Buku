"""Matte for the rainforest border (C1-F): the salient-object model misses foliage
against a dark forest, so build it from the leaves' own brightness + silhouette."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np
from PIL import Image

import comp as C

ROOT = sys.argv[1]
img = C.load_rgb(os.path.join(ROOT, "assets/C1/C1-F_v2.png"))
h, w = img.shape[:2]
L = C.lum(C.blur(img, 1.5))
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
yy = np.arange(h, dtype=np.float32)[:, None]
edge = np.clip((L - 0.085) / 0.12, 0, 1)
edge = edge * edge * (3 - 2 * edge)
solid = np.clip((yy - 0.58 * h) / (0.10 * h), 0, 1)
a = np.maximum(edge, solid)
a = np.minimum(a, np.clip((yy - 0.12 * h) / (0.06 * h), 0, 1))          # drop the far canopy
a = C.guided_filter(C.lum(img).astype(np.float32), a.astype(np.float32), 2, 3e-3)
a = np.clip(a, 0, 1)
# keep only foliage connected to the main mass at the bottom (drops bokeh specks)
n, lab = cv2.connectedComponents((a > 0.25).astype(np.uint8), connectivity=8)
keep = np.unique(lab[-5:, :])
keep = keep[keep > 0]
conn = np.isin(lab, keep).astype(np.float32)
conn = cv2.dilate(conn, np.ones((5, 5), np.uint8))
a = a * C.blur(conn, 1.0)
rgba = np.dstack([img, a])
Image.fromarray(C.to_u8(rgba), "RGBA").save(os.path.join(ROOT, "03_Cutouts/C1-F.png"))
print("foliage coverage", round(float((a > 0.5).mean()), 3))
