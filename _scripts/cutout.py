"""Cut out the picked assets: BiRefNet alpha + colour decontamination of edges.

Output: 03_Cutouts/<id>.png (RGBA, original resolution) and <id>_mask.png
Run: venv python -I _scripts/cutout.py <workspace> [ids...]
"""
import os
import sys
import time

import numpy as np
from PIL import Image
from rembg import new_session, remove
from pymatting import estimate_foreground_ml

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "03_Cutouts")
os.makedirs(OUT, exist_ok=True)

PICKS = {
    "C2-B": "assets/C2/C2-B_v2.png", "C2-C": "assets/C2/C2-C_v3.png", "C2-D": "assets/C2/C2-D_v2.png",
    "C2-C1": "assets/C2/C2-C_v1.png",            # soldier only: a different face from C1's soldier
    # uniform-accurate regenerations (PROMPTS_ChatGPT_Uniformed.md), blank badges for the real insignia
    "UNI-C2-PDRM": "assets/uniformed/UNI-C2-PDRM_v2.png", "UNI-C2-ARMY": "assets/uniformed/UNI-C2-ARMY_v2.png",
    "UNI-C3-PDRM": "assets/uniformed/UNI-C3-PDRM_v1.png", "UNI-C1-ARMY": "assets/uniformed/UNI-C1-ARMY_v1.png",
    # v3.1: current PDRM working uniforms (short sleeves, no cross strap)
    "UNI-C2-PDRM3": "assets/uniformed/UNI-C2-PDRM_v3.png", "UNI-C3-PDRM2": "assets/uniformed/UNI-C3-PDRM_v2.png",

    "C2-E": "assets/C2/C2-E_v4.png", "C2-F": "assets/C2/C2-F_v1.png",
    "C1-C": "assets/C1/C1-C_v2.png", "C1-D": "assets/C1/C1-D_v2.png", "C1-E": "assets/C1/C1-E_v4.png",
    "C1-F": "assets/C1/C1-F_v2.png", "C1-G": "assets/C1/C1-G_v1.png",
    "C3-D": "assets/C3/C3-D_v2.png", "C3-E": "assets/C3/C3-E_v2.png", "C3-F": "assets/C3/C3-F_v2.png",
    "C3-H": "assets/C3/C3-H_v1.png",
    "ISTANA": "assets/_reference/Istana_Negara_Jalan_Duta.jpg",
}

ids = sys.argv[2:] or list(PICKS)
sess = new_session("birefnet-general")
for key in ids:
    t = time.time()
    src = Image.open(os.path.join(ROOT, PICKS[key])).convert("RGB")
    mask = remove(src, session=sess, only_mask=True)
    mask.save(os.path.join(OUT, f"{key}_mask.png"))
    img = np.asarray(src, np.float64) / 255
    a = np.asarray(mask, np.float64) / 255
    if max(src.size) <= 2048:
        fg = estimate_foreground_ml(img, a)          # removes background colour from edge pixels
    else:
        fg = img
    rgba = np.dstack([np.clip(fg, 0, 1), a])
    Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, f"{key}.png"))
    print(key, src.size, f"{time.time() - t:.0f}s", flush=True)
print("ALL DONE")
