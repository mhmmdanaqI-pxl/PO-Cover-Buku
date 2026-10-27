"""Book mockups for the pitch, rendered as a real object rather than a flat card.

An A5 perfect-bound softcover (148 x 210 mm, 9 mm thick, 6 mm rounded corners, as the 2025 book)
lies on a matte desk, seen from the front-left at ~50 degrees with a ~50 mm-lens perspective:
  - the front cover is the final artwork (trimmed), mapped with an exact perspective transform,
    with a faint hinge score line and a soft matte-laminate sheen
  - the page block sits between the front and back cover (flush, as trimmed): the visible edges
    show the cover's own edge colour on top, stacked paper, and the back cover underneath
  - the spine is the cover wrapping the left edge
  - one key light from the back-left: Lambert shading on every face, a contact shadow and a
    soft cast shadow on the desk
Outputs 05_Presentation/mockup_C*.jpg and mockup_trio.jpg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np

import comp as C

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "05_Presentation")
os.makedirs(OUT, exist_ok=True)
PX = 300 / 25.4
B = int(round(3 * PX))
BW, BH, BT, BR = 148.0, 210.0, 9.0, 6.0          # book width, height, thickness, corner radius (mm)
SS = 2                                             # supersampling
LIGHT = np.array([-0.55, 0.65, 1.0]) / np.linalg.norm([-0.55, 0.65, 1.0])   # towards the key light
PAPER = C.hexf("#EEE9DF")


def unit(v):
    return v / np.linalg.norm(v)


def cover_art(key):
    """Final artwork trimmed to A5, with a faint hinge score 8 mm from the spine."""
    im = C.load_rgb(os.path.join(ROOT, f"04_Final/{key}/CGSO2026_{key}_preview.jpg"))[B:B + 2480, B:B + 1748].copy()
    x = int(8 * PX)
    im[:, x:x + 3] *= 0.93
    im[:, x + 3:x + 6] = np.clip(im[:, x + 3:x + 6] * 1.04, 0, 1)
    return im


def outline(n=560):
    """Rounded-rectangle perimeter in cover mm (x right, y down), clockwise on the page,
    with outward normals and a flag for the straight spine edge (x = 0)."""
    per = 2 * (BW + BH - 4 * BR) + 2 * np.pi * BR
    pts, nrm, spine = [], [], []
    for t in np.linspace(0, per, n, endpoint=False):
        segs = [(BW - 2 * BR, "top"), (np.pi * BR / 2, "tr"), (BH - 2 * BR, "right"), (np.pi * BR / 2, "br"),
                (BW - 2 * BR, "bottom"), (np.pi * BR / 2, "bl"), (BH - 2 * BR, "left"), (np.pi * BR / 2, "tl")]
        for L, name in segs:
            if t <= L:
                break
            t -= L
        if name == "top":
            p, q = (BR + t, 0), (0, -1)
        elif name == "right":
            p, q = (BW, BR + t), (1, 0)
        elif name == "bottom":
            p, q = (BW - BR - t, BH), (0, 1)
        elif name == "left":
            p, q = (0, BH - BR - t), (-1, 0)
        else:
            c, a0 = {"tr": ((BW - BR, BR), -90), "br": ((BW - BR, BH - BR), 0),
                     "bl": ((BR, BH - BR), 90), "tl": ((BR, BR), 180)}[name]
            a = np.radians(a0 + np.degrees(t / BR))
            q = (np.cos(a), np.sin(a))
            p = (c[0] + BR * q[0], c[1] + BR * q[1])
        pts.append(p)
        nrm.append(q)
        spine.append(name == "left")
    return np.array(pts), np.array(nrm), np.array(spine)


class Book:
    def __init__(self, key, x=0.0, y=0.0, angle=0.0):
        self.art = cover_art(key)
        self.x, self.y, self.a = x, y, np.radians(angle)
        h, w = self.art.shape[:2]
        # spine / back cover: the artwork's own dark base (darkest decile of the left strip)
        strip = self.art[:, :int(4 * PX)].reshape(-1, 3)
        self.spine_col = np.percentile(strip, 20, axis=0) * 0.9

    def world(self, xy, z):
        """cover mm (x right, y down) at height z -> world mm (head of the book away from camera)."""
        lx, ly = xy[..., 0] - BW / 2, BH / 2 - xy[..., 1]
        c, s = np.cos(self.a), np.sin(self.a)
        return np.stack([self.x + c * lx - s * ly, self.y + s * lx + c * ly, np.full(lx.shape, float(z))], -1)

    def dir(self, v2):
        c, s = np.cos(self.a), np.sin(self.a)
        return np.stack([c * v2[..., 0] + s * v2[..., 1], s * v2[..., 0] - c * v2[..., 1], np.zeros(len(v2))], -1)


class Camera:
    def __init__(self, pos, target):
        self.pos = np.array(pos, float)
        f = unit(np.array(target, float) - self.pos)
        r = unit(np.cross(f, [0, 0, 1]))
        self.R = np.stack([r, np.cross(r, f), f])
        self.f, self.cx, self.cy = 1.0, 0.0, 0.0

    def norm(self, P):
        q = (P - self.pos) @ self.R.T
        return q[..., 0] / q[..., 2], q[..., 1] / q[..., 2], q[..., 2]

    def fit(self, P, size, margin):
        a, b, _ = self.norm(P)
        W, H = size
        self.f = min(W * (1 - 2 * margin[0]) / np.ptp(a), H * (1 - 2 * margin[1]) / np.ptp(b))
        self.cx = W / 2 - self.f * (a.min() + a.max()) / 2
        self.cy = H / 2 + self.f * (b.min() + b.max()) / 2

    def px(self, P):
        a, b, z = self.norm(P)
        return np.stack([self.cx + self.f * a, self.cy - self.f * b], -1), z


def shadow_hull(book, per):
    base = book.world(per, 0)
    top = book.world(per, BT)
    top = top - LIGHT[None, :] * (top[:, 2:3] / LIGHT[2])
    pts = np.concatenate([base, top])[:, :2].astype(np.float32)
    hull = cv2.convexHull(pts)[:, 0]
    return np.concatenate([hull, np.zeros((len(hull), 1), np.float32)], 1)


def desk(W, H, seed=5):
    """Matte warm-grey desk: soft light falloff from the key side, large tonal drift, fine tooth."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = 1 - 0.16 * np.clip(np.hypot((xx / W - 0.15) * 1.2, (yy / H - 0.05)), 0, 1.4)
    low = C.blur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), 10)
    low = cv2.resize(low / (low.std() + 1e-6), (W, H), interpolation=cv2.INTER_CUBIC)
    fine = C.blur(rng.normal(0, 1, (H, W)).astype(np.float32), 0.8)
    fine /= fine.std() + 1e-6
    base = C.hexf("#D8D2C8")
    return np.clip(base[None, None] * (g * (1 + 0.012 * low) + 0.010 * fine)[..., None], 0, 1)


def poly(img, pts, col, aa=True):
    cv2.fillPoly(img, [np.round(pts * 4).astype(np.int32)], col, lineType=cv2.LINE_AA if aa else cv2.LINE_8, shift=2)


def render(books, size, cam_pos, target, margin):
    W, H = size[0] * SS, size[1] * SS
    cam = Camera(cam_pos, target)
    per, nrm, spine = outline()
    pts = [np.concatenate([b.world(per, 0), b.world(per, BT), shadow_hull(b, per)]) for b in books]
    cam.fit(np.concatenate(pts), (W, H), margin)
    img = desk(W, H)

    # --- shadows on the desk (all books first): soft cast shadow + tight contact shadow
    cast = np.zeros((H, W), np.float32)
    contact = np.zeros((H, W), np.float32)
    for b in books:
        poly(cast, cam.px(shadow_hull(b, per))[0], 1.0)
        poly(contact, cam.px(b.world(per, 0))[0], 1.0)
    cast = C.blur(cast, 9 * SS) * 0.34
    contact = C.blur(cv2.dilate(contact, np.ones((3, 3), np.uint8)), 2.2 * SS) * 0.5
    img *= (1 - np.maximum(cast, contact))[..., None]

    rng = np.random.default_rng(11)
    leaves = np.sort(rng.uniform(0.6, BT - 0.6, 7))                    # a few visible sheet lines
    for b in sorted(books, key=lambda b: -cam.norm(b.world(np.array([[BW / 2, BH / 2]]), 0))[2][0]):
        nw = b.dir(nrm)
        mid = b.world(per, BT / 2)
        vis = np.einsum("ij,ij->i", nw, cam.pos[None] - mid) > 0
        lam = 0.74 + 0.26 * np.clip(nw @ LIGHT, 0, 1)                  # room fill keeps shaded paper off-white
        h, w = b.art.shape[:2]
        # --- side faces, one quad per band, no per-quad anti-aliasing (supersampling smooths the
        # silhouette; abutting AA quads would leak the desk shadow through as seam lines)
        def band(p0, p1, z0, z1, col):
            quad = np.concatenate([b.world(np.array([p0, p1]), z0), b.world(np.array([p1, p0]), z1)])
            poly(img, cam.px(quad)[0], tuple(float(c) for c in col), aa=False)

        for i in np.where(vis)[0]:
            p0, p1 = per[i], per[(i + 1) % len(per)]
            if spine[i]:                                                # the cover wraps the spine
                band(p0, p1, 0, BT, b.spine_col * lam[i])
                continue
            edge_col = b.art[int(np.clip(p0[1] * PX, 0, h - 1)), int(np.clip(p0[0] * PX, 0, w - 1))]
            band(p0, p1, 0, 0.3, b.spine_col * lam[i])                  # back cover edge
            band(p0, p1, 0.3, BT - 0.3, PAPER * lam[i])                 # page block
            for z in leaves:
                band(p0, p1, z, z + 0.05, PAPER * lam[i] * 0.93)
            band(p0, p1, BT - 0.3, BT, edge_col * lam[i])               # front cover edge
        # --- front cover: exact perspective map of the artwork, clipped to the rounded outline
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        dst = cam.px(b.world(np.array([[0, 0], [BW, 0], [BW, BH], [0, BH]], float), BT))[0].astype(np.float32)
        M = cv2.getPerspectiveTransform(src, dst)
        art = cv2.warpPerspective(b.art, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        m = np.zeros((H, W), np.float32)
        poly(m, cam.px(b.world(per, BT))[0], 1.0)
        # light: Lambert on the top face + a broad, low matte-laminate sheen (Blinn, low gloss)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        u = (xx - dst[:, 0].min()) / np.ptp(dst[:, 0])
        v = (yy - dst[:, 1].min()) / np.ptp(dst[:, 1])
        shade = 1.0 - 0.05 * (u * 0.6 + v * 0.4)
        sheen = np.exp(-(((u - 0.18) / 0.55) ** 2 + ((v - 0.1) / 0.6) ** 2)) * 0.06
        art = 1 - (1 - art * shade[..., None]) * (1 - sheen[..., None])
        img = img * (1 - m[..., None]) + art * m[..., None]

    img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    g = C.grain((size[1], size[0]), amount=0.007, size=1.2)[..., None]
    return np.clip(img + g, 0, 1)


for k in ("C1", "C2", "C3"):
    im = render([Book(k, angle=-7)], (2400, 1800), cam_pos=(-260, -560, 1050), target=(0, 4, 0), margin=(0.22, 0.07))
    C.save_rgb(im, os.path.join(OUT, f"mockup_{k}.jpg"))

# a row square to the camera's view (camera 10.4 deg left of centre), so the three sit level, not stepping
trio = [Book("C1", x=-179, y=33, angle=-6), Book("C2", x=0, y=0, angle=-10), Book("C3", x=179, y=-33, angle=-8)]
im = render(trio, (3800, 1700), cam_pos=(-150, -820, 1150), target=(0, 0, 0), margin=(0.06, 0.10))
C.save_rgb(im, os.path.join(OUT, "mockup_trio.jpg"))
print("mockups done")
