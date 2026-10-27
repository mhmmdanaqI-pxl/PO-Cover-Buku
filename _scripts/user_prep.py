"""Cut-outs from photos Anaqi supplied (28 Oct), pitch comps only (SOURCES.md, 'Supplied by Anaqi').

  U-ARMY   the saluting 10 Para officer (real camouflage, beret badge, name tapes): BiRefNet, the
           officer beside him and the chair at the right edge excluded
  U-DULANG PETRONAS Dulang B platform: BiRefNet (its white modules are sky-coloured, so no sky key);
           cut at the waterline where the jacket legs enter the sea
Output: 03_Cutouts/<id>.png. Run: venv python -I _scripts/user_prep.py <workspace>
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from pymatting import estimate_foreground_ml
from rembg import new_session, remove

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, "assets/_reference/user_supplied")
OUT = os.path.join(ROOT, "03_Cutouts")
SESS = new_session("birefnet-general")


def cut(name, keep_fn, out):
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    a = np.asarray(remove(im, session=SESS, only_mask=True), np.float64) / 255
    a = keep_fn(a)
    rgb = np.asarray(im, np.float64) / 255
    fg = estimate_foreground_ml(rgb, a)
    Image.fromarray((np.dstack([np.clip(fg, 0, 1), a]) * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, out))
    print(out, im.size)


def army(a):
    H, W = a.shape
    xs = np.arange(W)[None, :]
    a = a * (xs > 425) * (xs < 1560)                     # not the officer on the left, not the chair
    n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return a * cv2.dilate((labs == big).astype(np.uint8), np.ones((9, 9), np.uint8))


def dulang(a):
    H, W = a.shape
    ys = np.arange(H, dtype=np.float64)[:, None]
    a = a * np.clip((768 - ys) / 3, 0, 1)                 # the legs enter the sea at ~y 770
    n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return a * cv2.dilate((labs == big).astype(np.uint8), np.ones((9, 9), np.uint8))


if not any(f in sys.argv for f in ("--oath-only", "--formal-only")):
    cut("08_ATM_10Para_salute.png", army, "U-ARMY.png")
    cut("12_PETRONAS_Dulang_B.png", dulang, "U-DULANG.png")


def oath(a):
    H, W = a.shape
    xs = np.arange(W)[None, :]
    a = a * (xs > 305) * (xs < 772)                      # the choir behind him stays out
    n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return a * cv2.dilate((labs == big).astype(np.uint8), np.ones((9, 9), np.uint8))


# U-PDRM-OATH: PDRM officer reciting the oath, right hand raised (supplied 28 Oct, photo 24)
if "--oath-only" in sys.argv:
    cut("24_PDRM_oath_officer.png", oath, "U-PDRM-OATH.png")


def formal(a):
    n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return a * cv2.dilate((labs == big).astype(np.uint8), np.ones((9, 9), np.uint8))


# U-PDRM-FORMAL: formal studio portrait, hands clasped, calm (supplied 28 Oct, photo 31)
if "--formal-only" in sys.argv:
    cut("31_PDRM_formal_NAAZRON.png", formal, "U-PDRM-FORMAL.png")
