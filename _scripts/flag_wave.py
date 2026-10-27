"""Waving Jalur Gemilang: the exact 6000 px vector flag mapped onto the
photographed fabric (S-1_v2) enlarged 2x. Output: 03_Cutouts/FLAG_waving.png
Run: venv python -I _scripts/flag_wave.py <workspace>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

import comp as C

ROOT = sys.argv[1]
fabric = C.load_rgb(os.path.join(ROOT, "assets/shared/S-1_v2.png"))
flag = C.load_rgb(os.path.join(ROOT, "02_Vectors/Flag/Jalur_Gemilang_6000x3000.png"))
out = C.flag_on_fabric(fabric, flag, scale=2)
Image.fromarray(C.to_u8(out), "RGBA").save(os.path.join(ROOT, "03_Cutouts/FLAG_waving.png"))
print("flag", out.shape[1], "x", out.shape[0])
