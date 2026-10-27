"""Real insignia on the uniformed figures (client feedback 27 Oct: "logo mcm bukan PDRM").

The image generator invented the badges. This replaces each one with the real insignia:
  - PDRM crest (Royal_Malaysian_Police.svg, Commons) on the police cap badges and collar
  - 10 Parachute Brigade beret badge (with black backing, en.wikipedia) on the maroon berets
Per badge: the generated badge is inpainted out, the real artwork is rendered as metal with
relief, warped to the cap / beret surface, tone-matched to the old badge (so it carries the
photo's own light), given a 1 px contact shadow and the photo's grain.
Input 03_Cutouts/<id>.png -> output 03_Cutouts/<id>_ins.png (originals untouched).
Run: venv python -I _scripts/insignia.py <workspace> [preview_dir]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import camo

ROOT = sys.argv[1]
PREVIEW = sys.argv[2] if len(sys.argv) > 2 else None
REF = os.path.join(ROOT, "assets/_reference")
LIGHT = np.array([-0.6, -0.8])          # light from upper left in image space (x right, y down)


def lum(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


# ------------------------------------------------------------------ badge textures (RGBA, float)
def pdrm_texture():
    a = np.asarray(Image.open(os.path.join(REF, "PDRM_crest_1600.png")).convert("RGBA"), np.float32) / 255
    rgb = a[..., :3] * a[..., 3:4] + (1 - a[..., 3:4])                 # on white, as drawn
    L = lum(rgb)
    ink = (L < 0.55).astype(np.uint8)
    # silhouette: everything not reachable from the border through un-inked pixels
    outside = np.zeros((ink.shape[0] + 2, ink.shape[1] + 2), np.uint8)
    fill = (1 - ink).copy()
    cv2.floodFill(fill, outside, (0, 0), 2)
    sil = (fill != 2).astype(np.float32)
    sil = cv2.dilate(sil, np.ones((3, 3), np.uint8))
    # the metal cap badge is pierced: the four open fields between the wreath, the blades and the
    # tiger show the cap through them (points inside each field, in the 1600 px rendering)
    _, lab = cv2.connectedComponents((1 - ink).astype(np.uint8), connectivity=4)
    for px, py in ((700, 560), (470, 880), (950, 880), (720, 1080)):
        sil[lab == lab[py, px]] = 0
    raised = (1 - ink) * sil                                            # white artwork = raised metal
    h = cv2.GaussianBlur(raised.astype(np.float32), (0, 0), 3.0)
    gy, gx = np.gradient(h)
    shade = np.clip(0.62 + 9.0 * (gx * LIGHT[0] + gy * LIGHT[1]), 0.15, 1.2)
    metal = 0.36 + 0.52 * h                                             # recessed lines darker
    v = np.clip(metal * shade, 0, 1)
    spec = np.clip((shade - 0.95) * 2.5, 0, 1) * raised * 0.35
    v = np.clip(v + spec, 0, 1)
    return np.dstack([v, v, v, sil]), sil                              # metal mask = whole crest


def para_texture():
    a = np.asarray(Image.open(os.path.join(REF, "Para10_badge_1600.png")).convert("RGBA"), np.float32) / 255
    rgb, al = a[..., :3], a[..., 3]
    L = lum(rgb)
    metal = ((L > 0.35) & (al > 0.5)).astype(np.float32)               # silver wings + parachute
    h = cv2.GaussianBlur(metal, (0, 0), 2.5)
    gy, gx = np.gradient(h)
    shade = np.clip(0.75 + 8.0 * (gx * LIGHT[0] + gy * LIGHT[1]), 0.3, 1.25)
    v = np.where(metal > 0, np.clip(L * shade, 0, 1), L * 0.9)         # black felt backing stays matte
    return np.dstack([v, v, v, al]), metal


def pip_texture(rot):
    """PDRM rank pip, drawn from its geometry (no source file): a 5-point star with one point toward
    the collar, a fan of five rays between each pair of points, a centre disc with a recessed ring
    and a domed boss. Built as a height map so the points are faceted metal; shaded for the photo's
    light turned into the pip's own frame (the pip is placed rotated rot degrees)."""
    N = 1024                                                           # 2x, area-downsampled to 512
    c = np.linspace(-1.07, 1.07, N, dtype=np.float32)
    X, Y = np.meshgrid(c, c)
    r = np.hypot(X, Y)
    h = np.full((N, N), -1.0, np.float32)
    alb = np.ones((N, N), np.float32)
    for k in range(5):
        phi = np.pi + 2 * np.pi * k / 5
        xa, ya = X * np.cos(phi) + Y * np.sin(phi), -X * np.sin(phi) + Y * np.cos(phi)
        hw = 0.4545 * (1 - xa)                                          # tip at 1, half-width 0.2 at the disc
        h = np.where((xa > 0) & (np.abs(ya) < hw), np.maximum(h, 0.5 * (hw - np.abs(ya))), h)
        psi = phi + np.pi / 5                                          # ray fan between two points
        xf, yf = X * np.cos(psi) + Y * np.sin(psi), -X * np.sin(psi) + Y * np.cos(psi)
        for off in (-0.14, -0.07, 0.0, 0.07, 0.14):
            end, t = 0.88 - 0.7 * abs(off), 0.026
            d = np.hypot(np.clip(xf, 0.5, end) - xf, yf - off)            # capsule from 0.5 to end
            ray = d < t
            h = np.where(ray, np.maximum(h, 0.035 * np.sqrt(np.clip(1 - (d / t) ** 2, 0, 1))), h)
    disc = r < 0.56
    h = np.where(disc, 0.13 + 0.04 * (1 - (r / 0.56) ** 2), h)
    groove = (r > 0.2) & (r < 0.33)
    h = np.where(groove, 0.10, h)
    alb = np.where(groove, 0.3, alb)
    h = np.where(r <= 0.2, 0.15 + 0.06 * (1 - (r / 0.2) ** 2), h)
    al = (h > -1).astype(np.float32)
    hs = np.where(al > 0, h, 0)
    gy, gx = np.gradient(hs, c[1] - c[0])
    gx, gy = np.clip(gx, -3, 3), np.clip(gy, -3, 3)                    # silhouette steps are not facets
    t = np.radians(rot)
    lx = LIGHT[0] * np.cos(t) + LIGHT[1] * np.sin(t)                   # image light in the pip's frame
    ly = -LIGHT[0] * np.sin(t) + LIGHT[1] * np.cos(t)
    lv = np.array([lx, ly, 0.9]) / np.linalg.norm([lx, ly, 0.9])
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    diff = np.clip(n @ lv, 0, 1)
    hv = (lv + [0, 0, 1]) / np.linalg.norm(lv + [0, 0, 1])
    spec = np.clip(n @ hv, 0, 1) ** 40
    v = np.clip(alb * (0.1 + 0.9 * diff ** 1.6) + 0.7 * spec * alb, 0, 1) * al  # struck silver: deep facets
    small = cv2.resize(np.dstack([v, al, al]), (N // 2, N // 2), interpolation=cv2.INTER_AREA)
    a = small[..., 1]
    v = np.where(a > 1e-3, small[..., 0] / np.maximum(a, 1e-3), 0)
    return np.dstack([v, v, v, a]), a


def strap_pips(mid, thick, n, button):
    """Jobs for n rank pips on one epaulette. mid: the strap's centre line from the collar end to
    the shoulder seam, as (x, y) points; thick: its vertical face thickness at those points. Layout
    as on the PDRM shoulder board: centres at 0.385 / 0.607 / 0.83 of the length from the collar
    end, filled from the shoulder end; pip 0.19 of the length along, 0.47 of the face across.
    button: (cx, cy, rx, ry, rot) of the strap's own button, the pips' metal tone reference."""
    mid, thick = np.float32(mid), np.float32(thick)
    seg = np.hypot(*np.diff(mid, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    along = 0.19 * s[-1]
    jobs = []
    for u in (0.83, 0.607, 0.385)[:n]:
        p = u * s[-1]
        x, y, th = (np.interp(p, s, v) for v in (mid[:, 0], mid[:, 1], thick))
        i = min(np.searchsorted(s, p) - 1, len(seg) - 1)
        d = mid[i + 1] - mid[i]
        rot = float(np.degrees(np.arctan2(d[1], d[0])))
        across = max(0.47 * th * abs(np.cos(np.radians(rot))), 4.0)    # the pip's relief: never a hairline
        jobs.append((("pip", round(rot)), quad(x, y, across, 1.0, along / across, rot), button, None))
    return jobs


TEX = {"pdrm": pdrm_texture(), "para": para_texture()}


# ------------------------------------------------------------------ placement
def quad(cx, cy, h, aspect, sx, rot):
    """Corners (TL, TR, BR, BL) of the badge: height h px, width h*aspect*sx (sx < 1 = turned
    away), rotated rot degrees clockwise about its centre."""
    w = h * aspect * sx
    pts = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]])
    t = np.radians(rot)
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    return (pts @ R.T + [cx, cy]).astype(np.float32)


def place_badge(img, key, q, remove, tint=None, clone=None):
    """img: HxWx4 float cutout. q: quad. remove: (cx, cy, rx, ry, rot) ellipse of the old badge.
    clone: (dx, dy) offset to clean fabric whose weave is copied into the filled area."""
    H, W = img.shape[:2]
    rgb, al = img[..., :3].copy(), img[..., 3]
    # tone target: the old badge's metal (pixels well off the surrounding fabric's level)
    cx, cy, rx, ry, rot = remove
    em = np.zeros((H, W), np.uint8)
    cv2.ellipse(em, (int(cx), int(cy)), (int(rx), int(ry)), rot, 0, 360, 1, -1)
    ring = cv2.dilate(em, np.ones((15, 15), np.uint8)) - em
    L = lum(rgb)
    fab = np.median(L[(ring > 0) & (al > 0.5)])
    old = (em > 0) & (al > 0.5) & (L > fab + 0.12)
    lo, mid, hi = np.percentile(L[old], [8, 50, 97]) if old.sum() > 20 else (fab + 0.1, fab + 0.3, fab + 0.55)
    col = rgb[old].mean(0) / max(L[old].mean(), 1e-3) if (tint is None and old.sum() > 20) else np.array(tint or (1, 1, 1))
    col = col / max(lum(col[None, None])[0, 0], 1e-3)
    # remove the generated badge; transparent pixels near it are filled too, so the inpaint only
    # draws on the real fabric around the badge, never on the cutout's undefined background colour
    near = cv2.dilate(em, np.ones((41, 41), np.uint8))
    # never touch the beret's headband / cap band: dark, low-saturation and much wider than the badge
    hsv = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    dark = ((L < 0.14) & (hsv[..., 1] < 0.45) & (al > 0.5)).astype(np.uint8)
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    band = np.isin(lab, [i for i in range(1, nlab) if st[i, cv2.CC_STAT_WIDTH] > 5 * rx])
    m8 = np.maximum(cv2.dilate(em, np.ones((5, 5), np.uint8)), near * (al < 0.5)) * (~band)
    u8 = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    src_rgb = rgb.copy()
    if clone == "keep":
        # badge struck onto an existing plate (belt buckle): keep the plate, only add the crest
        clone = None
    elif clone in ("felt", "fabric"):
        # felt: disc inside a narrow black felt patch, filled with that patch's own felt (dark pixels
        # only, so no beret colour is pulled in). fabric: small disc on plain uniform cloth, filled
        # from the cloth just outside its dark rim (an inpaint drags that rim in as a dark ring)
        if clone == "felt":
            felt = (cv2.dilate(em, np.ones((9, 9), np.uint8)) > 0) & (em == 0) & (L < 0.2) & (al > 0.5)
        else:
            felt = (cv2.dilate(em, np.ones((17, 17), np.uint8)) > 0) & ~(cv2.dilate(em, np.ones((7, 7), np.uint8)) > 0) & (al > 0.5)
            em = cv2.dilate(em, np.ones((5, 5), np.uint8))
        base = np.median(rgb[felt], axis=0) if felt.sum() > 10 else np.array([0.08, 0.08, 0.09])
        sd = float(L[felt].std()) if felt.sum() > 10 else 0.02
        n = np.random.default_rng(3).normal(0, sd, (H, W)).astype(np.float32)
        fill = np.clip(base[None, None] + cv2.GaussianBlur(n, (0, 0), 0.7)[..., None], 0, 1)
        fm = cv2.GaussianBlur(cv2.dilate(em, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.8)
        rgb = rgb * (1 - fm[..., None]) + fill * fm[..., None]
        clone = None
    else:
        rgb = cv2.inpaint(u8, m8.astype(np.uint8), 6, cv2.INPAINT_TELEA).astype(np.float32) / 255
    if clone:
        # the inpaint carries the right shading but no weave: add the felt texture of clean fabric
        # nearby (high-pass only), so the filled patch has the same nap and grain as the beret
        dx, dy = clone[:2]
        shifted = cv2.warpAffine(src_rgb, np.float32([[1, 0, -dx], [0, 1, -dy]]), (W, H),
                                 borderMode=cv2.BORDER_REFLECT)
        fm = cv2.GaussianBlur(cv2.dilate(em, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 2.0)
        fm *= ~band
        if len(clone) > 2 and clone[2] == "copy":
            # badge on the silhouette edge, where an inpaint has too little fabric to draw from:
            # copy the felt itself, exposure-matched to the fabric ring around the old badge
            ok = (ring > 0) & (al > 0.5) & ~band
            gain = rgb[ok].mean(0) / np.maximum(shifted[ok].mean(0), 1e-3) if ok.sum() > 20 else 1.0
            rgb = np.clip(rgb * (1 - fm[..., None]) + shifted * gain * fm[..., None], 0, 1)
        else:
            detail = shifted - cv2.GaussianBlur(shifted, (0, 0), 3.0)
            rgb = np.clip(rgb + detail * fm[..., None] * 0.85, 0, 1)
    # warp the real badge onto the surface (4x supersampled)
    tex, metal = pip_texture(key[1]) if isinstance(key, tuple) else TEX[key]
    th, tw = tex.shape[:2]
    S = 4
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]), q * S)
    # premultiplied value, alpha and metal mask, warped as one 3-channel image
    stack = np.dstack([tex[..., 0] * tex[..., 3], tex[..., 3], metal * tex[..., 3]]).astype(np.float32)
    big = cv2.warpPerspective(stack, M, (W * S, H * S), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    small = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    bv, ba = small[..., 0], small[..., 1]
    bm = small[..., 2] / np.maximum(ba, 1e-4)
    bv = np.where(ba > 1e-3, bv / np.maximum(ba, 1e-4), 0)
    # tone-map the metal to the old badge's lo/mid/hi (keeps the photo's exposure and contrast)
    sel = (ba > 0.5) & (bm > 0.5)
    if sel.sum() > 10:
        s_lo, s_mid, s_hi = np.percentile(bv[sel], [8, 50, 97])
        mv = np.interp(bv, [s_lo, s_mid, s_hi], [lo, mid, hi])
        bv = np.where(bm > 0.5, mv, np.clip(bv * 0.8 + fab * 0.2, 0, 1) * 0.6)   # felt: darker than the beret
    badge = np.clip(bv[..., None] * col, 0, 1)
    # contact shadow (away from the light) and grain matched to the fabric around it
    sh = cv2.GaussianBlur(cv2.warpAffine(ba, np.float32([[1, 0, 1.2], [0, 1, 1.4]]), (W, H)), (0, 0), 1.0)
    rgb = rgb * (1 - (sh * (1 - ba) * 0.35)[..., None])
    hp = L - cv2.GaussianBlur(L, (0, 0), 1.5)
    noise_sd = float(hp[(ring > 0) & (al > 0.5)].std())
    rng = np.random.default_rng(int(cx * 7 + cy))
    n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6)
    grain_w = np.where(bm > 0.5, 0.6, 0.25)                             # metal takes grain, felt barely
    badge = np.clip(badge + (n / (n.std() + 1e-6) * noise_sd * grain_w)[..., None], 0, 1)
    a = (cv2.GaussianBlur(ba, (0, 0), 0.45) * (al > 0.5))[..., None]
    rgb = rgb * (1 - a) + badge * a
    return np.dstack([rgb, al])


ASPECT = {k: v[0].shape[1] / v[0].shape[0] for k, v in TEX.items()}


def _triangle(mask):
    """Minimum enclosing triangle of a mask, vertices ordered top-left, top-right, bottom."""
    pts = np.argwhere(mask)[:, ::-1].astype(np.float32).reshape(-1, 1, 2)
    _, tri = cv2.minEnclosingTriangle(pts)
    tri = tri.reshape(3, 2)
    tri = tri[np.argsort(tri[:, 1])]
    top = tri[:2][np.argsort(tri[:2, 0])]
    return np.vstack([top, tri[2:]]).astype(np.float32)


def para_fit(o_tri):
    """Quad for the 10 Para badge whose black backing lands exactly on the generated placeholder
    triangle: the texture's own backing triangle is mapped vertex-to-vertex (affine) onto it.
    o_tri: the placeholder's top-left, top-right and bottom vertices, measured at 4-5x (the felt is
    too close in tone to the beret headband for a reliable automatic outline)."""
    tex, metal = TEX["para"]
    L = lum(tex[..., :3])
    t_tri = _triangle((tex[..., 3] > 0.5) & (L < 0.3) & (metal < 0.5))
    A = cv2.getAffineTransform(t_tri, np.float32(o_tri))
    th, tw = tex.shape[:2]
    corners = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]])
    return (np.hstack([corners, np.ones((4, 1), np.float32)]) @ A.T).astype(np.float32)
# measured on the cutouts at 2-3x (px in each cutout's own 1024 x 1536 frame)
JOBS = {
    "C2-C": [  # police (left figure of C2-C_v3)
        ("pdrm", quad(271, 196, 56, ASPECT["pdrm"], 0.80, 1), (271, 196, 23, 30, 0), None),
        ("pdrm", quad(345, 414, 22, ASPECT["pdrm"], 0.85, -8), (345, 414, 17, 12, -10), None),
    ],
    "C3-D": [  # police
        ("pdrm", quad(401, 163, 86, ASPECT["pdrm"], 0.82, 1), (401, 162, 36, 45, 0), None),
        ("pdrm", quad(400, 523, 34, ASPECT["pdrm"], 0.92, -10), (400, 523, 23, 19, -10), None),
    ],
    "C1-C": [  # soldier, badge on the far side of the beret, nearly edge-on (old badge y 98-168)
        ("para", quad(603, 132, 60, ASPECT["para"], 0.40, -10), (607, 133, 16, 37, -8), (1.0, 0.985, 0.95)),
    ],
    "C2-C1": [  # soldier (right figure of C2-C_v1), old badge x 790-853, y 238-281, tilted ~18 deg
        ("para", quad(821, 258, 50, ASPECT["para"], 0.95, 18), (821, 259, 37, 17, 18), (1.0, 0.97, 0.92)),
    ],
    # uniform-accurate regenerations: blank placeholders generated at the right size, angle and light
    "UNI-C2-PDRM": [
        ("pdrm", quad(494, 133, 72, ASPECT["pdrm"], 0.66, -2), (494, 133, 21, 36, 0), None),
        ("pdrm", quad(605, 453, 36, ASPECT["pdrm"], 0.85, -8), (605, 453, 14, 16, 0), None),
    ],
    "UNI-C3-PDRM": [
        ("pdrm", quad(425, 166, 86, ASPECT["pdrm"], 0.68, -3), (425, 166, 26, 42, -3), None),
        ("pdrm", quad(435, 537, 34, ASPECT["pdrm"], 0.90, -20), (435, 537, 15, 15, 0), None),
    ],
    # v3.1 police: current working uniforms; cap, near collar, round chest badge (+ C3 belt buckle)
    "UNI-C2-PDRM3": [
        ("pdrm", quad(512, 131, 68, ASPECT["pdrm"], 0.62, -2), (512, 131, 19, 33, 0), None),
        ("pdrm", quad(655, 454, 30, ASPECT["pdrm"], 0.88, -6), (655, 454, 14, 14, 0), None),
        ("pdrm", quad(613, 702, 38, ASPECT["pdrm"], 0.95, 0), (613, 702, 20, 20, 0), None),
        # rank: ASP, three pips on each epaulette (near one bends over the shoulder; far one edge-on)
        *strap_pips([(700, 426), (730, 427), (750, 433), (770, 440), (790, 447), (805, 451)],
                    [21, 22, 25, 25, 26, 26], 3, (718, 420, 10, 5, 0)),
        *strap_pips([(508, 440), (490, 448), (475, 456), (460, 464), (445, 472), (430, 479), (415, 491),
                     (400, 500), (392, 505)], [8, 8, 7, 8, 8, 9, 14, 14, 14], 3, (500, 444, 10, 6, -30)),
    ],
    "UNI-C3-PDRM2": [
        ("pdrm", quad(403, 163, 76, ASPECT["pdrm"], 0.66, -3), (403, 163, 23, 37, -3), None),
        ("pdrm", quad(404, 527, 28, ASPECT["pdrm"], 0.92, -15), (404, 527, 13, 13, 0), None),
        ("pdrm", quad(628, 658, 30, ASPECT["pdrm"], 0.92, -4), (628, 658, 16, 16, 0), None),
        ("pdrm", quad(548, 1064, 54, ASPECT["pdrm"], 0.80, 0), (548, 1064, 32, 36, 0), None),
        # rank: Inspector, two pips on each epaulette
        *strap_pips([(362, 489), (340, 493), (320, 499), (300, 505.5), (280, 512), (260, 520), (240, 528),
                     (220, 535), (212, 538)], [28, 28, 32, 33, 32, 34, 36, 34, 34], 2, (337, 491, 11, 7, -18)),
        *strap_pips([(578, 517), (595, 526), (610, 534.5), (625, 542.5), (640, 550.5), (655, 559.5),
                     (670, 569.5), (685, 580.5), (694, 588)], [14, 14, 14, 14, 14, 14, 12, 12, 12], 2,
                    (585, 529, 8, 6, 40)),
    ],
    "UNI-C2-ARMY": [  # placeholder: black inverted triangle with a silver disc; badge fitted to it
        ("para", para_fit([(557, 84), (619, 108), (575, 151)]), (582, 117, 17, 12, -12), (1.0, 0.97, 0.92)),
    ],
    "UNI-C1-ARMY": [  # placeholder nearly edge-on at the beret's far front; badge fitted to it
        ("para", para_fit([(590, 97), (615, 98), (614, 158)]), (605, 123, 8, 16, 0), (1.0, 0.985, 0.95)),
    ],
}
# clean beret felt beside each removed badge (offset to the source patch), keyed by badge centre
CLONE = {("C1-C", (607, 133)): (-34, -4, "copy"), ("C2-C1", (821, 259)): (-100, -6), ("UNI-C1-ARMY", (605, 123)): "felt", ("UNI-C3-PDRM2", (548, 1064)): "keep",
         ("UNI-C2-PDRM3", (655, 454)): "fabric", ("UNI-C2-PDRM3", (613, 702)): "fabric",
         ("UNI-C3-PDRM2", (404, 527)): "fabric", ("UNI-C3-PDRM2", (628, 658)): "fabric",
         # rank pips go onto plain epaulette cloth: nothing to remove (the button is the tone reference)
         ("UNI-C2-PDRM3", (718, 420)): "keep", ("UNI-C2-PDRM3", (500, 444)): "keep",
         ("UNI-C3-PDRM2", (337, 491)): "keep", ("UNI-C3-PDRM2", (585, 529)): "keep"}

def name_tape(img, face, text, text_face=None):
    """Malaysian Army chest tape (No. 5 uniform, checked on US Army photos of Keris Strike 26): light
    khaki tape with black block capitals; the soldier's name over the right pocket, MALAYSIA over the
    left. The generated tapes are blank olive panels. face: the tape's inner face (TL, TR, BR, BL).
    The whole tape is recoloured to khaki under the photo's own light (khaki = the camo's tan patches
    beside it, the tape's own shading and nap kept), then the lettering is warped on as embroidery."""
    H, W = img.shape[:2]
    rgb, al = img[..., :3].copy(), img[..., 3]
    face = np.float32(face)
    L = lum(rgb)
    fm = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(fm, face.astype(np.int32), 1)
    lab = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)
    ref = np.median(lab[fm > 0], axis=0)
    dist = np.linalg.norm((lab - ref) * [0.5, 1, 1], axis=2)          # tape = olive, flat; lightness may vary
    near = cv2.dilate(fm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))) > 0
    tape = ((dist < 9) & near & (al > 0.5)).astype(np.uint8) | fm
    tape = cv2.morphologyEx(tape, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, labs = cv2.connectedComponents(tape)
    tape = (labs == labs[int(face[:, 1].mean()), int(face[:, 0].mean())]).astype(np.float32)
    tape = cv2.GaussianBlur(tape, (0, 0), 0.6) * (al > 0.5)
    # khaki under this light: the camo's tan patches around the tape (warm, light, low green)
    ring = (cv2.dilate(fm, np.ones((45, 45), np.uint8)) > 0) & (tape < 0.05) & (al > 0.5)
    hsv = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    tan = ring & (hsv[..., 0] > 20) & (hsv[..., 0] < 45) & (hsv[..., 1] > 0.12) & (L > np.percentile(L[ring], 70))
    khaki = np.median(rgb[tan], axis=0) if tan.sum() > 30 else np.array([0.62, 0.58, 0.47])
    khaki = khaki * 0.85 + lum(khaki[None, None])[0, 0] * 0.15           # tape dye: a touch greyer than the camo
    m = fm > 0
    S = np.clip(L / max(float(np.median(L[m])), 1e-3), 0.3, 1.6)        # the tape's own shading and nap
    Ss = np.clip(cv2.GaussianBlur(S, (0, 0), 2.5), 0.72, 1.3)            # shading, minus the olive's blotches
    S = Ss * (1 + 0.45 * (cv2.GaussianBlur(S, (0, 0), 0.5) / np.maximum(cv2.GaussianBlur(S, (0, 0), 2.5), 1e-3) - 1))
    new = np.clip(khaki[None, None] * S[..., None], 0, 1)
    rgb = rgb * (1 - tape[..., None]) + new * tape[..., None]
    # lettering, laid out on a flat tape (4.4:1) and warped onto the face
    TW, TH = 880, 200
    from PIL import ImageDraw, ImageFont
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 300)
    big = Image.new("L", (300 * len(text) + 200, 420), 0)
    ImageDraw.Draw(big).text((60, 40), text, font=font, fill=255)
    big = big.crop(big.getbbox())
    cap = int(TH * 0.52)
    w = int(big.width * cap / big.height)
    w = min(w, int(TW * 0.8))                                         # long words are condensed to fit
    lay = np.zeros((TH, TW), np.float32)
    x0, y0 = (TW - w) // 2, (TH - cap) // 2
    lay[y0:y0 + cap, x0:x0 + w] = np.asarray(big.resize((w, cap), Image.LANCZOS), np.float32) / 255
    S4 = 4
    tf = np.float32(text_face) if text_face is not None else face
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [TW, 0], [TW, TH], [0, TH]]), tf * S4)
    A = cv2.resize(cv2.warpPerspective(lay, M, (W * S4, H * S4), flags=cv2.INTER_LINEAR), (W, H),
                   interpolation=cv2.INTER_AREA)
    A = cv2.GaussianBlur(A, (0, 0), 0.35)
    # black thread: dark, with a faint satin sheen on the lit side and a soft shadow off the stitches
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 0.6))
    sheen = np.clip(-(gx * LIGHT[0] + gy * LIGHT[1]) * 2.2, 0, 1) * 0.10
    thread = khaki[None, None] * S[..., None] * 0.13 + sheen[..., None]
    sh = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, 0.6], [0, 1, 0.7]]), (W, H)), (0, 0), 0.6)
    rgb = rgb * (1 - (sh * (1 - A) * 0.25)[..., None])
    rgb = rgb * (1 - A[..., None]) + thread * A[..., None]
    # grain matched to the cloth around the tape
    hp = L - cv2.GaussianBlur(L, (0, 0), 1.5)
    sd = float(hp[ring].std()) * 0.6
    nz = cv2.GaussianBlur(np.random.default_rng(int(face[0, 0])).normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6)
    rgb = np.clip(rgb + (nz / (nz.std() + 1e-6) * sd * tape)[..., None], 0, 1)
    return np.dstack([rgb, al])


def velcro(img, face, outer):
    """Bare black hook-and-loop strip, as on the issue shirt Zharief sent (27 Oct ~20:40). The generated
    olive tab (outer: its full outline incl. the bound border) is re-dyed near-black under the photo's
    own light: its folds and stitched edge are kept, and the loop pile is added as fine grain with a
    faint lift where the light grazes it."""
    H, W = img.shape[:2]
    rgb, al = img[..., :3].copy(), img[..., 3]
    L = lum(rgb)
    fm = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(fm, np.int32(face), 1)
    tape = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(tape, np.int32(outer), 1)
    tape = cv2.GaussianBlur(tape.astype(np.float32), (0, 0), 0.6) * np.clip(al * 2, 0, 1)
    m = fm > 0
    S = np.clip(L / max(float(np.median(L[m])), 1e-3), 0.3, 1.6)
    Ss = np.clip(cv2.GaussianBlur(S, (0, 0), 2.5), 0.7, 1.35)            # folds and curvature
    S = Ss * (1 + 0.35 * (cv2.GaussianBlur(S, (0, 0), 0.5) / np.maximum(Ss, 1e-3) - 1))   # stitching, edge
    # black under this light: the cloth's light colour (tint of the tape's own olive, mostly neutral)
    tint = np.median(rgb[m], axis=0)
    tint = 0.75 + 0.25 * tint / max(float(lum(tint[None, None])[0, 0]), 1e-3)
    base = 0.30 * float(np.median(L[m])) * tint      # on the issue shirt the velcro sits at ~0.2 of the sand's value
    rng = np.random.default_rng(int(face[0][0]))
    pile = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)
    pile = pile / (pile.std() + 1e-6)
    gy, gx = np.gradient(cv2.GaussianBlur(Ss, (0, 0), 1.5))
    graze = np.clip(-(gx * LIGHT[0] + gy * LIGHT[1]) * 6, 0, 0.25)
    new = base[None, None] * (S * (1 + 0.16 * pile + graze))[..., None]
    rgb = rgb * (1 - tape[..., None]) + np.clip(new, 0, 1) * tape[..., None]
    return np.dstack([rgb, al])


TAPE_STYLE = "velcro"   # Zharief's issue-shirt photo: bare black velcro; "name" = khaki name tapes (name_tape)

# blank tapes measured on the cutouts at 5x (inner face TL, TR, BR, BL); wearer's right = image left
TAPES = {
    "UNI-C1-ARMY": [([(387, 604), (532, 610), (534, 637), (389, 635)], "HAFIZ"),
                    ([(643, 623), (728, 646), (728, 672), (652, 648)], "MALAYSIA")],
    # this tape is drawn sheared; its lettering is squared up halfway toward the tape's long axis
    "UNI-C2-ARMY": [([(282, 652), (374, 633), (366, 666), (281, 683)], "AIZAT",
                     [(282, 652), (374, 633), (373, 666), (285, 684)]),
                    ([(512, 610), (661, 603), (661, 634), (512, 638)], "MALAYSIA")],
}

for cid, jobs in JOBS.items():
    img = np.asarray(Image.open(os.path.join(ROOT, f"03_Cutouts/{cid}.png")).convert("RGBA"), np.float32) / 255
    if cid in camo.FIGS:
        img = camo.recolour(img, cid)
    for key, q, rem, tint in jobs:
        img = place_badge(img, key, q, rem, tint, CLONE.get((cid, rem[:2])))
    for i, tape in enumerate(TAPES.get(cid, [])):
        img = velcro(img, tape[0], camo.FIGS[cid]["tapes"][i]) if TAPE_STYLE == "velcro" else name_tape(img, *tape)
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(
        os.path.join(ROOT, f"03_Cutouts/{cid}_ins.png"))
    if PREVIEW:
        for i, (key, q, rem, tint) in enumerate(jobs):
            x0, y0 = q.min(0) - 40
            x1, y1 = q.max(0) + 40
            box = tuple(int(v) for v in (max(0, x0), max(0, y0), x1, y1))
            src = Image.open(os.path.join(ROOT, f"03_Cutouts/{cid}.png")).convert("RGBA").crop(box)
            new = Image.open(os.path.join(ROOT, f"03_Cutouts/{cid}_ins.png")).convert("RGBA").crop(box)
            out = Image.new("RGBA", (src.width * 2 + 6, src.height), (255, 0, 255, 255))
            out.alpha_composite(src, (0, 0)); out.alpha_composite(new, (src.width + 6, 0))
            s = 4 if src.height < 120 else 3
            out.convert("RGB").resize((out.width * s, out.height * s), Image.LANCZOS).save(
                os.path.join(PREVIEW, f"ins_{cid}_{i}.jpg"), quality=92)
    print(cid, "done")
