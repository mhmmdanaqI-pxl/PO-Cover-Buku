"""Real Malaysian Army digital camouflage on the generated soldiers (Zharief, 27 Oct ~20:40: a photo of
the actual issue shirt).

The image generator drew a five-colour approximation: dark olive, dark green, khaki, brown and a lot
of near-black. The real ATM pattern has four colours: a clear mid green, a pale pinkish sand, a
muted taupe-brown and sparse navy. This re-dyes the generated cloth to the real four colours
without touching its geometry. The print still follows every seam, pocket and fold as generated.
Per figure: the garment pixels are clustered by colour (lightness normalised to the local sand
level, so fold shadows don't change a pixel's class) and each cluster is assigned to one of the
four real dyes. The generator's dark-green blocks become the one real green, so only true
near-black stays navy. Each pixel's light is kept: new = dye * (Y / the mixed albedo of its classes),
all in linear light. The dyes are measured from Zharief's photo, then put under the figure's
own light by matching the sand.
Used by insignia.py before the badges go on. Run alone for previews:
venv python -I _scripts/camo.py <workspace> <preview_dir>
"""
import os
import sys

import cv2
import numpy as np

# measured on Zharief's photo of the issue shirt (CIE Lab, D65): sand, green, brown, navy
DYES = {"S": (82.0, 1.0, 10.0), "G": (53.0, -24.0, 17.0), "B": (49.0, 6.0, 9.0), "N": (21.0, 0.0, -5.0)}
ORDER = "SGBN"
NAVY = 0.07                     # share of the cloth left navy (real shirt: 5-9%)

# per figure, in the cutout's own 1024 x 1536 frame:
#   cut    - everything above this y is head/beret (no cloth)
#   keep   - polygons left untouched (olive T-shirt, black belt, buttons)
#   skin   - boxes where skin (neck, hands) is found by colour and left untouched
#   tapes  - chest tabs, outer edge incl. the bound border (left for insignia.py to make black velcro)
#   patch  - (rect x0, y0, x1, y1, source dy): a plain tab the issue shirt doesn't have, re-covered with
#            the same panel's own print from just above it before the re-dye
FIGS = {
    "UNI-C1-ARMY": dict(
        cut=383,
        keep=[[(486, 472), (577, 436), (579, 576), (549, 576)]],
        skin=[(380, 370, 660, 520), (220, 1230, 420, 1460), (740, 1250, 890, 1450)],
        tapes=[[(382, 600), (538, 605), (541, 640), (386, 640)], [(638, 618), (732, 644), (732, 676), (650, 650)]],
        patch=[(582, 681, 637, 722, -42)],          # rank-style tab on the placket
    ),
    "UNI-C2-ARMY": dict(
        cut=360,
        keep=[[(433, 474), (527, 468), (526, 572), (470, 580), (440, 520)],
              [(298, 998), (728, 990), (728, 1096), (298, 1100)]],
        skin=[(400, 360, 620, 480), (160, 1270, 290, 1470), (620, 1270, 780, 1480)],
        tapes=[[(276, 648), (377, 629), (369, 668), (277, 686)], [(506, 600), (664, 599), (664, 639), (506, 642)]],
    ),
}


def to_lin(s):
    return np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)


def to_srgb(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - 0.055)


def lab2rgb(lab):
    px = np.float32(lab).reshape(1, 1, 3)
    return cv2.cvtColor(px, cv2.COLOR_LAB2RGB).reshape(3).astype(np.float64)


def lum_lin(lin):
    return lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722


def garment_mask(img, fig):
    H, W = img.shape[:2]
    rgb, al = img[..., :3], img[..., 3]
    lab = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)
    m = (al > 0.01).astype(np.uint8)
    m[:fig["cut"]] = 0
    for poly in fig["keep"]:
        cv2.fillPoly(m, [np.int32(poly)], 0)
    for poly in fig["tapes"]:
        t = np.zeros_like(m)
        cv2.fillConvexPoly(t, np.int32(poly), 1)
        m[cv2.dilate(t, np.ones((3, 3), np.uint8)) > 0] = 0
    skin = np.zeros_like(m)
    warm = ((lab[..., 1] > 11) & (lab[..., 0] > 18)).astype(np.uint8)
    for x0, y0, x1, y1 in fig["skin"]:
        box = np.zeros_like(m)
        box[y0:y1, x0:x1] = 1
        n, labs, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(warm & box, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)))
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] > 900:
                skin[labs == i] = 1
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    skin = cv2.dilate(skin, np.ones((5, 5), np.uint8))
    m[skin > 0] = 0
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8) * (m > 0), lab, skin


def features(lab, m):
    """Lightness relative to the local sand level (the brightest cloth nearby), plus chromaticity
    (a*, b* over lightness), which a fold shadow barely changes: a shaded green stays green
    instead of turning into navy."""
    L = lab[..., 0]
    Lg = np.where(m > 0, L, 0).astype(np.float32)
    env = cv2.dilate(cv2.GaussianBlur(Lg, (0, 0), 1.5), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    w = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 14)
    env = cv2.GaussianBlur(env * (m > 0), (0, 0), 14) / np.maximum(w, 1e-3)
    Lr = L / np.maximum(env, 8)
    ca, cb = lab[..., 1] / (L + 8), lab[..., 2] / (L + 8)
    return np.dstack([Lr * 40, ca * 100, cb * 60]).astype(np.float32), Lr


def cluster(f, sel, k, seed=7):
    cv2.setRNGSeed(seed)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.05)
    _, lab, cen = cv2.kmeans(f[sel], k, None, crit, 8, cv2.KMEANS_PP_CENTERS)
    o = np.argsort(-cen[:, 0])                       # lightest first, stable naming
    return cen[o]


def patch(img, rect):
    """Cover a plain tab with the print just above it on the same panel, at the tab's own brightness."""
    x0, y0, x1, y1, dy = rect
    out = img.copy()
    src = img[y0 + dy:y1 + dy, x0:x1, :3]
    dst = img[y0:y1, x0:x1, :3]
    src = src * (dst.mean() / max(float(src.mean()), 1e-3))
    f = np.zeros(img.shape[:2], np.float32)
    f[y0:y1, x0:x1] = 1
    f = cv2.GaussianBlur(cv2.erode(f, np.ones((3, 3), np.uint8)), (0, 0), 1.2)[y0:y1, x0:x1, None]
    out[y0:y1, x0:x1, :3] = dst * (1 - f) + src * f
    return out


def recolour(img, cid, k=6, assign=None, report=None):
    fig = FIGS[cid]
    for rect in fig.get("patch", []):
        img = patch(img, rect)
    m, lab, skin = garment_mask(img, fig)
    f, Lr = features(lab, m)
    sel = m > 0.5
    cen = cluster(f, sel, k)
    if assign is None:
        assign = fig.get("assign")
    if assign is None:                                # default rule; overridden per figure after inspection
        assign = []
        sand_ca = cen[0][1] / 100                    # hue judged against the sand, so a warm light doesn't turn green to brown
        for c in cen:
            lr, ca, cb = c[0] / 40, c[1] / 100, c[2] / 60
            assign.append("S" if lr > 0.8 else "N" if lr < 0.4 and cb < 0.16 and abs(ca) < 0.08
                          else "G" if ca - sand_ca < -0.1 else "B")
    # soft membership to each cluster -> each dye
    d = np.stack([np.sum((f - c) ** 2, axis=2) for c in cen], -1)
    p = np.exp(-(d - d.min(-1, keepdims=True)) / (2 * 3.5 ** 2))
    p /= p.sum(-1, keepdims=True)
    W4 = np.stack([p[..., [i for i, a in enumerate(assign) if a == c]].sum(-1) for c in ORDER], -1)
    W4 = np.stack([cv2.GaussianBlur(W4[..., i], (0, 0), 0.5) for i in range(4)], -1)
    W4 /= np.maximum(W4.sum(-1, keepdims=True), 1e-6)
    hard = W4.argmax(-1)
    # navy is sparse on the real cloth (~7%): keep the darkest small near-black blobs, the rest are
    # the generator's extra dark-green blocks and become the one real green
    nv = (sel & (hard == 3)).astype(np.uint8)
    n, labs, st, _ = cv2.connectedComponentsWithStats(nv, connectivity=8)
    lrm = np.bincount(labs.ravel(), weights=Lr.ravel(), minlength=n) / np.maximum(st[:, cv2.CC_STAT_AREA], 1)
    budget, kept = NAVY * sel.sum(), 0
    keep = np.zeros(n, bool)
    for i in sorted(range(1, n), key=lambda i: lrm[i]):
        if st[i, cv2.CC_STAT_AREA] <= 2500 and kept < budget:
            keep[i], kept = True, kept + st[i, cv2.CC_STAT_AREA]
    drop = cv2.dilate(((labs > 0) & ~keep[labs]).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    W4[..., 1] += np.where(drop, W4[..., 3], 0)
    W4[..., 3] = np.where(drop, 0, W4[..., 3])
    hard = W4.argmax(-1)
    lin = to_lin(np.clip(img[..., :3], 0, 1).astype(np.float64))
    Y = lum_lin(lin)
    # the figure's light: the generated sand under it vs the real sand dye
    sand = sel & (hard == 0) & (W4[..., 0] > 0.9)
    dyes = np.array([to_lin(lab2rgb(DYES[c])) for c in ORDER])
    gain = np.median(lin[sand], axis=0) / dyes[0]
    gain = gain / lum_lin(gain[None])[0] * np.median(Y[sand]) / lum_lin(dyes[0][None])[0]
    tgt = dyes * gain[None]
    # each class's mean albedo in the generated image (its mean Y), mixed per pixel by membership
    Ybar = np.array([np.mean(Y[sel & (hard == i)]) if np.any(sel & (hard == i)) else 0.1 for i in range(4)])
    alb = (W4 * Ybar).sum(-1)
    light = np.clip(Y / np.maximum(alb, 1e-4), 0.15, 3.0)
    new = to_srgb((W4[..., :, None] * tgt[None, None]).sum(2) * light[..., None])
    out = img.copy()
    out[..., :3] = img[..., :3] * (1 - m[..., None]) + new * m[..., None]
    if report is not None:
        frac = [float((hard[sel] == i).mean()) for i in range(4)]
        report.update(cen=cen, assign=assign, frac=dict(zip(ORDER, frac)), hard=hard, sel=sel, skin=skin)
    return out


if __name__ == "__main__":
    from PIL import Image
    ROOT, PREV = sys.argv[1], sys.argv[2]
    pal = np.uint8([[230, 210, 160], [40, 160, 60], [140, 90, 60], [20, 30, 110]])
    for cid in FIGS:
        img = np.asarray(Image.open(os.path.join(ROOT, f"03_Cutouts/{cid}.png")).convert("RGBA"), np.float32) / 255
        rep = {}
        out = recolour(img, cid, report=rep)
        print(cid, "fractions", {k: round(v, 3) for k, v in rep["frac"].items()})
        for c, a in zip(rep["cen"], rep["assign"]):
            print("   centroid Lr=%.2f a/L=%.3f b/L=%.3f -> %s" % (c[0] / 40, c[1] / 100, c[2] / 60, a))
        cls = np.zeros(img.shape[:2] + (3,), np.uint8)
        cls[rep["sel"]] = pal[rep["hard"][rep["sel"]]]
        cls[rep["skin"] > 0] = (255, 0, 255)
        bg = np.full(img.shape[:2] + (3,), 128, np.float32) / 255
        a = img[..., 3:4]
        before = (img[..., :3] * a + bg * (1 - a)) * 255
        after = (out[..., :3] * a + bg * (1 - a)) * 255
        Image.fromarray(np.hstack([before, after, cls]).astype(np.uint8)).save(
            os.path.join(PREV, f"camo_{cid}.jpg"), quality=90)
