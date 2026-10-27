"""Cut-outs from the real photos Anaqi supplied for the 9.5 push (pitch comps; licences to confirm,
see SOURCES.md 'Supplied by Anaqi').

  U-C2-SOLDIER   10 Para soldier, maroon beret, current digital camouflage (photo 36). He carries a
                 rifle: the cut stops at mid-chest, above the weapon, and the build sinks him into the
                 navy base below that line
  U-C2-SOLDIER2  Col. Mohd Azral Manan, 10 Para, at the Tiger Strike 24 opening ceremony aboard USS Somerset
                 (DVIDS 8439351, Cpl. Aidan Hekker USMC, PUBLIC DOMAIN): standing at ease, hands clasped, no
                 weapon; the officers either side of him excluded
  R-RMN-KELANTAN Royal Malaysian Navy OPV KD Kelantan (175) underway in the Strait of Malacca (US Navy
                 110126-N-6320L-821, MC Oscar Sosa, PUBLIC DOMAIN; Commons 960 px): C3 escort on the empty sea,
                 cut at its waterline
  U-C2-STUDENT   student in a grey hijab, phone and folder, smiling at the camera (photo 37)
  U-C2-ANALYST   cyber analyst with tablet and phone, lanyard (photo 39): the chair and screens excluded
  U-C1-RESEARCH  researcher in a lab coat with an orange handheld meter (photo 40): the right-hand woman
                 only (the two beside her, the readable name tag, out)
  U-C1-PLANTING  two young people planting a sapling, with the soil they kneel on (photo 43)
Output: 03_Cutouts/<id>.png. Run: venv python -I _scripts/user_prep2.py <workspace> [--masks]
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
MASKS = "--masks" in sys.argv


def largest(a, dil=9):
    n, labs, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return a * cv2.dilate((labs == big).astype(np.uint8), np.ones((dil, dil), np.uint8))


def cut(name, keep_fn, out):
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    a = np.asarray(remove(im, session=SESS, only_mask=True), np.float64) / 255
    a = keep_fn(a)
    rgb = np.asarray(im, np.float64) / 255
    if out.startswith("U-C1-PLANTING"):
        a = planting(a, rgb)
    if out.startswith("U-C1-RESEARCH"):
        rgb = research_retouch(rgb)
    if MASKS:
        Image.fromarray((a * 255).astype(np.uint8)).save(os.path.join(OUT, out.replace(".png", "_rawmask.png")))
    fg = estimate_foreground_ml(rgb, a)
    Image.fromarray((np.dstack([np.clip(fg, 0, 1), a]) * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, out))
    print(out, im.size)


def box(x0, y0, x1, y1, feather=6):
    def f(a):
        H, W = a.shape
        xs, ys = np.arange(W)[None, :], np.arange(H)[:, None]
        m = (np.clip((xs - x0) / feather, 0, 1) * np.clip((x1 - xs) / feather, 0, 1)
             * np.clip((ys - y0) / feather, 0, 1) * np.clip((y1 - ys) / feather, 0, 1))
        return largest(a * m)
    return f


def research(a):
    """The right-hand researcher only: traced along her face profile, collar and coat front (the woman
    beside her overlaps), keeping her own hands and the orange meter; her sleeve logo retouched out."""
    H, W = a.shape
    poly = np.array([(380, 38), (560, 40), (700, 980), (305, 980), (300, 800), (205, 784), (98, 780), (85, 700),
                     (95, 630), (200, 622), (242, 640), (312, 620), (318, 446), (350, 425), (360, 375), (335, 370), (320, 365),
                     (310, 350), (305, 340), (295, 330), (287, 315), (262, 300), (250, 282), (240, 262), (214, 230), (186, 200), (230, 140), (290, 80)],
                    np.float64) + (800, 100)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(poly).astype(np.int32)], 1)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
    return largest(a * m)


def research_retouch(rgb):
    """Sleeve logo (university crest) out: inpaint it with the coat's own cloth."""
    u8 = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    m = np.zeros(u8.shape[:2], np.uint8)
    cv2.ellipse(m, (1195, 760), (44, 40), 0, 0, 360, 255, -1)
    return cv2.inpaint(u8, m, 9, cv2.INPAINT_TELEA).astype(np.float64) / 255


def planting(a, rgb):
    """The pair plus the sapling (thin, so the matting drops it) keyed back by colour and sharpness,
    plus a feathered patch of the real soil where their hands meet the ground."""
    H, W = a.shape
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    L = 0.3 * r + 0.59 * g + 0.11 * b
    detail = np.abs(L - cv2.GaussianBlur(L.astype(np.float32), (0, 0), 5))
    # the background behind the sapling is far out of focus: a large median is a clean plate of it, and
    # the leaves (pale green, sharp) and the stem stand apart from it
    u8 = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    plate = cv2.medianBlur(u8, 151).astype(np.float64) / 255
    dist = np.linalg.norm(rgb - plate, axis=-1)
    greenish = (g - r) > -0.01
    ys, xs = np.mgrid[0:H, 0:W]
    inbox = (xs > 815) & (xs < 1145) & (ys > 622) & (ys < 1050)
    sap = ((dist > 0.09) & greenish & inbox).astype(np.uint8)
    sap = cv2.morphologyEx(sap, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    ff = sap.copy()                                             # fill holes inside the leaves
    cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 1)
    sap = sap | (1 - ff)
    n, labs, st, _ = cv2.connectedComponentsWithStats(sap)
    keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 1500]   # leaf fragments off
    sap = np.isin(labs, keep).astype(np.float32)
    sap = cv2.GaussianBlur(sap, (0, 0), 0.8) * np.clip(detail * 60 + 0.6, 0, 1)
    soil = np.clip(1 - (((xs - 975) / 330.0) ** 2 + ((ys - 1060) / 95.0) ** 2), 0, 1) ** 0.7
    # the ground they crouch on: the photo's own soil, a band from just under their feet to the frame
    # edge, its top a soft ragged line (the ferns cover its foot on the cover)
    rag = 1010 + 18 * np.sin(xs / 37.0) + 10 * np.sin(xs / 11.0 + 1.3)
    band = np.clip((ys - rag) / 30.0, 0, 1) * np.clip((xs - 60) / 80.0, 0, 1)
    soil = np.maximum(cv2.GaussianBlur(soil.astype(np.float32), (0, 0), 10), band.astype(np.float32))
    return np.maximum(np.maximum(a, sap), soil)


def soldier(a):
    """The soldier; the top of his rifle stock juts past the front of his chest (x > ~1163 between
    y 590 and 720): cut out, so only his own outline remains."""
    a = box(800, 300, 1330, 1333)(a)
    H, W = a.shape
    xs, ys = np.arange(W)[None, :], np.arange(H)[:, None]
    edge = 1163 + (ys - 590) * 0.05                                  # his chest front, leaning slightly
    rifle = (xs > edge) & (ys > 588) & (ys < 760)
    return a * (1 - cv2.GaussianBlur(rifle.astype(np.float32), (0, 0), 1.5))


def azral(a):
    """Col. Azral only: the matting also takes the flag behind him and slivers of the officers either
    side, so it is limited to a trace of his own silhouette (beret, shoulders, arms, legs)."""
    H, W = a.shape
    poly = np.array([(776, 433), (858, 429), (869, 458), (864, 498), (869, 538), (894, 571), (945, 595), (966, 633),
                     (972, 763), (959, 883), (934, 938), (939, 1068), (933, 1340), (677, 1340), (693, 1100),
                     (693, 1000), (695, 945), (735, 912), (700, 880), (673, 833), (660, 800), (658, 773),
                     (661, 660), (670, 640), (680, 626), (700, 614), (727, 603), (764, 590), (771, 556), (764, 507), (757, 470)], np.float64)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(poly).astype(np.int32)], 1)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)
    return largest(a * m)


def kelantan(a):
    """The ship only, cut along its waterline (the wake below stays in the sea of the cover)."""
    H, W = a.shape
    ys = np.arange(H, dtype=np.float64)[:, None]
    a = a * np.clip((WATERLINE - ys) / 2.0, 0, 1)
    return largest(a)


WATERLINE = 276          # source px (960 x 402), checked on the mask


JOBS = {
    "U-C2-SOLDIER": ("36_ATM_10Para_patrol_RIFLE.png", soldier),
    "U-C2-SOLDIER2": ("44_DVIDS_8439351_TigerStrike24_PD.jpg", azral),
    "R-RMN-KELANTAN": ("../C3_energy/RMN_KD_Kelantan_175_USNavy_PD.jpg", kelantan),
    "U-C2-STUDENT": ("37_Student_hijab_phone.png", box(40, 120, 1010, 1333)),
    "U-C2-ANALYST": ("39_Cyber_analyst_SOC.png", box(60, 30, 1460, 1333)),
    "U-C1-RESEARCH": ("40_Researchers_labcoat_meter_NAMETAG.png", research),
    "U-C1-PLANTING": ("43_Planting_pair_sapling.png", box(80, 230, 2000, 1250)),
}
only = [a for a in sys.argv[2:] if not a.startswith("--")]
for out, (src, fn) in JOBS.items():
    if not only or out in only:
        cut(src, fn, out + ".png")
