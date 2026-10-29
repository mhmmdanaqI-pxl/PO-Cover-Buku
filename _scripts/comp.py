"""Compositing engine for the CGSO 2026 covers (float32 linear-ish sRGB, 0..1).

Canvas = template: 1819 x 2551 px @300ppi = 154 x 216 mm incl. 3 mm bleed.
Layers are full-canvas RGBA float arrays so they can be written to a PSD 1:1.
"""
import os
import struct

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageCms
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, Group
from psd_tools.constants import Resource
from psd_tools.psd.image_resources import ImageResource, GridGuidesInfo

W, H = 1819, 2551
PXMM = 300 / 25.4
ROOT = None  # set by caller


def mm(v):
    return v * PXMM


# ------------------------------------------------------------------ io
def load_rgba(path):
    im = Image.open(path).convert("RGBA")
    return np.asarray(im, np.float32) / 255


def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), np.float32) / 255


def to_u8(a):
    return (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)


def save_rgb(a, path, q=93):
    im = Image.fromarray(to_u8(a[..., :3]))
    if path.lower().endswith(".jpg"):
        im.save(path, quality=q, subsampling=0, dpi=(300, 300))
    else:
        im.save(path, dpi=(300, 300))


# ------------------------------------------------------------------ colour
def lum(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def hexf(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def curves(rgb, pts, channel=None):
    """pts: list of (in, out) 0..1."""
    xs, ys = zip(*sorted(pts))
    out = rgb.copy()
    chans = range(3) if channel is None else [channel]
    for c in chans:
        out[..., c] = np.interp(rgb[..., c], xs, ys)
    return out


def exposure(rgb, ev):
    return rgb * (2.0 ** ev)


def saturation(rgb, s):
    l = lum(rgb)[..., None]
    return l + (rgb - l) * s


def lift_gamma_gain(rgb, lift=(0, 0, 0), gamma=(1, 1, 1), gain=(1, 1, 1)):
    lift, gamma, gain = map(lambda v: np.array(v, np.float32), (lift, gamma, gain))
    x = np.clip(rgb * gain + lift * (1 - rgb), 0, None)
    return np.power(x, 1 / gamma)


def tint_shadows_highlights(rgb, shadow=(0, 0, 0), highlight=(0, 0, 0), balance=0.5):
    l = lum(rgb)[..., None]
    ws = np.clip(1 - l / balance, 0, 1) ** 1.5
    wh = np.clip((l - balance) / (1 - balance), 0, 1) ** 1.5
    return rgb + ws * np.array(shadow, np.float32) + wh * np.array(highlight, np.float32)


def match_stats(src_rgb, alpha, ref_rgb, ref_mask=None, strength=0.6):
    """Move the masked element's Lab mean/std toward a reference region."""
    def lab(x):
        return cv2.cvtColor(np.clip(x, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)
    s, r = lab(src_rgb), lab(ref_rgb)
    m = alpha > 0.5
    rm = np.ones(r.shape[:2], bool) if ref_mask is None else ref_mask > 0.5
    out = s.copy()
    for c in range(3):
        sm, ss = s[..., c][m].mean(), s[..., c][m].std() + 1e-5
        rmn, rs = r[..., c][rm].mean(), r[..., c][rm].std() + 1e-5
        tgt = (s[..., c] - sm) * (1 + (rs / ss - 1) * strength * 0.5) + sm + (rmn - sm) * strength
        out[..., c] = tgt
    return np.clip(cv2.cvtColor(out, cv2.COLOR_LAB2RGB), 0, 1)


# ------------------------------------------------------------------ blending
def blend(base, top, alpha, mode="normal", opacity=1.0):
    a = (alpha * opacity)[..., None]
    if mode == "normal":
        res = top
    elif mode == "screen":
        res = 1 - (1 - base) * (1 - top)
    elif mode == "multiply":
        res = base * top
    elif mode == "add":
        res = base + top
    elif mode == "overlay":
        res = np.where(base < 0.5, 2 * base * top, 1 - 2 * (1 - base) * (1 - top))
    elif mode == "softlight":
        res = (1 - 2 * top) * base * base + 2 * top * base
    else:
        raise ValueError(mode)
    return base * (1 - a) + res * a


def blur(a, sigma):
    if sigma <= 0:
        return a
    return cv2.GaussianBlur(a, (0, 0), sigma)


def guided_filter(guide, src, r, eps):
    """He et al. guided filter (grey guide) for matte edge refinement."""
    mean = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp = mean(guide), mean(src)
    cov = mean(guide * src) - mI * mp
    var = mean(guide * guide) - mI * mI
    a = cov / (var + eps)
    b = mp - a * mI
    return mean(a) * guide + mean(b)


# ------------------------------------------------------------------ geometry
def place(rgba, cx_mm=None, cy_mm=None, width_mm=None, height_mm=None, left_mm=None, top_mm=None,
          rotate=0.0, flip=False, crop=None):
    """Scale/rotate an RGBA element and drop it on a transparent full canvas.
    crop: (x0, y0, x1, y1) fraction box applied first."""
    src = rgba
    if crop:
        h, w = src.shape[:2]
        x0, y0, x1, y1 = crop
        src = src[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    if flip:
        src = src[:, ::-1]
    h, w = src.shape[:2]
    if width_mm:
        s = mm(width_mm) / w
    else:
        s = mm(height_mm) / h
    # premultiply for clean resampling
    pm = src.copy()
    pm[..., :3] *= pm[..., 3:4]
    nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
    interp = cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4
    pm = cv2.resize(pm, (nw, nh), interpolation=interp)
    if rotate:
        M = cv2.getRotationMatrix2D((nw / 2, nh / 2), rotate, 1.0)
        cos, sin = abs(M[0, 0]), abs(M[0, 1])
        bw, bh = int(nh * sin + nw * cos), int(nh * cos + nw * sin)
        M[0, 2] += bw / 2 - nw / 2
        M[1, 2] += bh / 2 - nh / 2
        pm = cv2.warpAffine(pm, M, (bw, bh), flags=cv2.INTER_LANCZOS4, borderValue=(0, 0, 0, 0))
        nw, nh = bw, bh
    if left_mm is not None:
        x = int(round(mm(left_mm)))
    else:
        x = int(round(mm(cx_mm) - nw / 2))
    if top_mm is not None:
        y = int(round(mm(top_mm)))
    else:
        y = int(round(mm(cy_mm) - nh / 2))
    canvas = np.zeros((H, W, 4), np.float32)
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    dx1, dy1 = min(W, x + nw), min(H, y + nh)
    if dx1 > dx0 and dy1 > dy0:
        canvas[dy0:dy1, dx0:dx1] = pm[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    a = canvas[..., 3:4]
    canvas[..., :3] = np.where(a > 1e-4, canvas[..., :3] / np.maximum(a, 1e-4), 0)
    canvas[..., :3] = np.clip(canvas[..., :3], 0, 1)
    return canvas


def lin_grad(y0_mm, y1_mm, axis=0, power=1.0):
    """0 at y0 -> 1 at y1 (axis 0 = vertical)."""
    if axis == 0:
        v = (np.arange(H, dtype=np.float32) - mm(y0_mm)) / (mm(y1_mm) - mm(y0_mm))
        g = np.clip(v, 0, 1) ** power
        return np.repeat(g[:, None], W, 1)
    v = (np.arange(W, dtype=np.float32) - mm(y0_mm)) / (mm(y1_mm) - mm(y0_mm))
    g = np.clip(v, 0, 1) ** power
    return np.repeat(g[None, :], H, 0)


def radial(cx_mm, cy_mm, r_mm, power=2.0, aspect=1.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - mm(cx_mm)) / aspect) ** 2 + (yy - mm(cy_mm)) ** 2) / mm(r_mm)
    return np.clip(1 - d, 0, 1) ** power


# ------------------------------------------------------------------ integration
def light_wrap(layer, background, width_px=6, strength=0.35):
    """Bleed background light onto the element's edges (screen)."""
    a = layer[..., 3]
    inner = blur(a, width_px)
    edge = np.clip(a - inner, 0, 1) * 2.2 + np.clip(a * (1 - blur(a, width_px * 0.5)), 0, 1)
    edge = np.clip(edge, 0, 1) * a
    bg = blur(background[..., :3], width_px * 2)
    out = layer.copy()
    out[..., :3] = blend(layer[..., :3], bg, edge, "screen", strength)
    return out


def rim_light(layer, color, direction=(-1, 0), width_px=5, strength=0.6):
    """Warm/cool edge light from a direction (dx, dy) in screen space."""
    a = layer[..., 3]
    dx, dy = direction
    shift = np.float32([[1, 0, -dx * width_px], [0, 1, -dy * width_px]])
    shifted = cv2.warpAffine(a, shift, (a.shape[1], a.shape[0]), borderValue=0)
    rim = np.clip(a - shifted, 0, 1)
    rim = blur(rim, width_px * 0.6) * a
    out = layer.copy()
    out[..., :3] = blend(layer[..., :3], np.broadcast_to(hexf(color), layer[..., :3].shape), rim, "screen", strength)
    return out


def shadow_layer(layer, offset_mm=(0, 1.5), blur_mm=3.0, opacity=0.5, color="#000000"):
    a = layer[..., 3]
    M = np.float32([[1, 0, mm(offset_mm[0])], [0, 1, mm(offset_mm[1])]])
    s = cv2.warpAffine(a, M, (W, H), borderValue=0)
    s = blur(s, mm(blur_mm)) * opacity
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = hexf(color)
    out[..., 3] = s
    return out


def grain(shape, amount=0.025, size=1.0, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, shape[:2]).astype(np.float32)
    if size > 1:
        n = blur(n, size * 0.5)
        n /= n.std() + 1e-6
    return n * amount


def unsharp(rgb, sigma=1.0, amount=0.35):
    return np.clip(rgb + (rgb - blur(rgb, sigma)) * amount, 0, 1)


def over(base, layer, opacity=1.0, mode="normal"):
    return blend(base, layer[..., :3], layer[..., 3], mode, opacity)


# ------------------------------------------------------------------ flag on fabric
def flag_on_fabric(fabric_rgb, flag_rgb, scale=1):
    """Map an exact flat flag onto a photographed white fabric.
    Displacement from the fabric's shading + multiply shading + specular screen.
    scale > 1 enlarges the (smooth) fabric shading first, so the vector flag's
    stripe/star edges are mapped at full sharpness on a larger grid."""
    s = float(scale)
    if s != 1:
        fabric_rgb = cv2.resize(fabric_rgb, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
        fabric_rgb = np.clip(fabric_rgb, 0, 1)
    h, w = fabric_rgb.shape[:2]
    L = lum(fabric_rgb)
    alpha = np.clip((L - 0.06) / 0.10, 0, 1)
    alpha = blur(alpha, 0.8 * s)
    ys, xs = np.where(alpha > 0.5)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    # per-column vertical extent so the stripes follow the fabric's silhouette
    top = np.full(w, np.nan, np.float32)
    bot = np.full(w, np.nan, np.float32)
    for x in range(x0, x1 + 1):
        col = np.where(alpha[:, x] > 0.5)[0]
        if len(col):
            top[x], bot[x] = col.min(), col.max()
    idx = np.arange(w)
    good = ~np.isnan(top)
    top = np.interp(idx, idx[good], top[good])
    bot = np.interp(idx, idx[good], bot[good])
    top = cv2.GaussianBlur(top[None, :], (0, 0), 25 * s)[0]
    bot = cv2.GaussianBlur(bot[None, :], (0, 0), 25 * s)[0]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = (yy - top[None, :]) / np.maximum(bot - top, 1)[None, :]
    u = (xx - x0) / max(1, x1 - x0)
    # displacement from shading gradient (folds); constants scale with s^2
    # because the gradient per px shrinks by s and the span grows by s
    Ls = blur(L, 10 * s)
    gy, gx = np.gradient(Ls)
    span = np.maximum(bot - top, 1)[None, :]
    v = v + gy * 260 * s * s / span          # folds bend the stripes by a few px
    u = u + gx * 120 * s * s / max(1, x1 - x0)
    # keep the vector flag at ~2x the target density: remap stays crisp, and the
    # later downscale onto the cover anti-aliases the edges (supersampling)
    tw, th = int(x1 - x0 + 1), int(np.median(bot - top) + 1)
    if flag_rgb.shape[1] > tw * 2.4:
        flag_rgb = cv2.resize(flag_rgb, (2 * tw, 2 * th), interpolation=cv2.INTER_AREA)
    fh, fw = flag_rgb.shape[:2]
    mapx = np.clip(u, 0, 1) * (fw - 1)
    mapy = np.clip(v, 0, 1) * (fh - 1)
    flat = cv2.remap(flag_rgb, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT)
    shade = np.clip(L / np.percentile(L[alpha > 0.5], 97), 0, 1.15)[..., None]
    out = flat * np.clip(shade, 0, 1) ** 1.1
    spec = np.clip((shade - 0.92) / 0.25, 0, 1) * 0.35
    out = 1 - (1 - out) * (1 - spec)
    return np.dstack([np.clip(out, 0, 1), alpha])


# ------------------------------------------------------------------ export
def write_psd(path, layers):
    """layers: list of (name, rgba_float) bottom -> top, or ('group', name, [...])."""
    psd = PSDImage.new("RGBA", (W, H))

    def add(parent, name, arr):
        im = Image.fromarray(to_u8(arr), "RGBA")
        PixelLayer.frompil(im, parent, name, 0, 0)

    for item in layers:
        if item[0] == "group":
            g = Group.new(psd, item[1])
            for n, arr in item[2]:
                add(g, n, arr)
        else:
            add(psd, item[0], item[1])
    psd.image_resources[Resource.RESOLUTION_INFO] = ImageResource(
        key=Resource.RESOLUTION_INFO.value, data=struct.pack(">IHHIHH", 300 << 16, 1, 2, 300 << 16, 1, 2))
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    psd.image_resources[Resource.ICC_PROFILE] = ImageResource(key=Resource.ICC_PROFILE.value, data=srgb)
    psd.save(path)


def write_print_pdf(art_rgb, overlay_pdf, path, jpg_path):
    """Artwork (300ppi, with bleed) + vector overlay on top; Trim/Bleed boxes set."""
    Image.fromarray(to_u8(art_rgb)).save(jpg_path, quality=95, subsampling=0, dpi=(300, 300))
    ov = pymupdf.open(overlay_pdf)
    doc = pymupdf.open()
    page = doc.new_page(width=ov[0].rect.width, height=ov[0].rect.height)
    page.insert_image(page.rect, filename=jpg_path)
    page.show_pdf_page(page.rect, ov, 0)
    page.set_bleedbox(page.rect)
    page.set_trimbox(ov[0].trimbox)
    doc.save(path, garbage=3, deflate=True)


# ------------------------------------------------------------------ shared finish + export
FIXED_ORDER = ("Roundel shadow", "Jata glow", "Jata Negara", "Office block", "Headline", "Roundel - Rahsiakan Rahsia Kerajaan")


def text_burn(root, key, layer="Office block", feather_mm=1.6, spread_mm=(1.2, 0.6), rows_mm=None):
    """Soft alpha shaped to a block of type (no visible box): the template's own text layer merged
    into line bands, then feathered. Used to burn the artwork behind small type and to knock
    decorative linework back from it. rows_mm=(top, bottom) limits it to some lines (canvas mm)."""
    a = fixed_layers(root, key)[layer][..., 3] > 0.3
    if rows_mm:
        yy = np.arange(H)[:, None] / PXMM
        a &= (yy >= rows_mm[0]) & (yy <= rows_mm[1])
    k = np.ones((int(mm(spread_mm[1])) * 2 + 1, int(mm(spread_mm[0])) * 2 + 1), np.uint8)
    band = cv2.dilate(a.astype(np.uint8), k).astype(np.float32)
    return np.clip(blur(band, mm(feather_mm)) * 1.3, 0, 1)


_fixed_cache = {}


def layout(root):
    """Template geometry (canvas mm) written by build_template.py: roundel centre/radius, Jata box, headline."""
    import json
    with open(os.path.join(root, "01_Template", "CGSO2026_layout.json")) as fh:
        return json.load(fh)


def add_security(root, key, st, color, base_top_mm, field_opacity=0.55, frame_opacity=0.5):
    """Client revision 29 Oct: every concept carries document-security features, in C2's language.
    (1) a guilloche underprint (the C2 interference line field, lines one pixel heavier so they hold in
    print) over the dark base, fading in from base_top_mm, knocked back behind the headline and roundel;
    (2) the "RAHSIAKAN RAHSIA KERAJAAN" microtext frame 8 mm inside the trim."""
    sec = os.path.join(root, "02_Vectors", "C2_Security")
    yy = np.arange(H, dtype=np.float32)[:, None] / PXMM
    lay = layout(root)
    wf = place(load_rgba(os.path.join(sec, "C2_guilloche_wavefield_300ppi.png")), left_mm=0, top_mm=0, width_mm=154)
    wf[..., 3] = cv2.dilate(wf[..., 3], np.ones((2, 2), np.uint8))
    wf[..., :3] = hexf(color)
    wf[..., 3] *= np.clip((yy - base_top_mm) / 14, 0, 1)
    wf[..., 3] *= 1 - text_burn(root, key, "Headline", feather_mm=1.2, spread_mm=(1.2, 0.8)) * 0.9
    wf[..., 3] *= 1 - radial(*lay["roundel_c"], lay["roundel_r"] + 2.5, 3.0)
    st.add("Security - guilloche underprint", wf, opacity=field_opacity)
    mf = place(load_rgba(os.path.join(sec, "C2_microtext_frame_300ppi.png")), left_mm=0, top_mm=0, width_mm=154)
    mf[..., :3] = hexf(color)
    st.add("Security - microtext frame", mf, opacity=frame_opacity)


def fixed_layers(root, key):
    if (root, key) not in _fixed_cache:
        _fixed_cache[(root, key)] = _fixed_layers(root, key)
    return _fixed_cache[(root, key)]


def _fixed_layers(root, key):
    tpl = PSDImage.open(os.path.join(root, f"01_Template/CGSO2026_{key}_master.psd"))
    out = {}
    for l in tpl.descendants():
        if l.kind == "pixel" and l.name in FIXED_ORDER:
            im = np.zeros((H, W, 4), np.float32)
            arr = np.asarray(l.topil().convert("RGBA"), np.float32) / 255
            im[l.top:l.top + arr.shape[0], l.left:l.left + arr.shape[1]] = arr
            out[l.name] = im
    return out


def finalize(root, key, out_dir, psd_name, layers, comp_rgb, grade, fast=False, grain_amt=0.022):
    """grade(rgb)->rgb is the cover's single colour grade. Then vignette-free grain + sharpen,
    fixed elements on top, and all exports."""
    graded = grade(comp_rgb)
    graded = unsharp(graded, 1.0, 0.25)
    g = grain((H, W), amount=grain_amt, size=1.3)[..., None]
    graded = np.clip(graded + g * (0.35 + 0.65 * (1 - np.abs(graded - 0.5) * 2)), 0, 1)
    fx = fixed_layers(root, key)
    final = graded.copy()
    for n in FIXED_ORDER:
        final = over(final, fx[n])
    save_rgb(final, os.path.join(out_dir, f"CGSO2026_{key}_preview.jpg"))
    Image.fromarray(to_u8(final)).resize((W // 3, H // 3), Image.LANCZOS).save(
        os.path.join(out_dir, f"{key}_thumb.jpg"), quality=90)
    if fast:
        return final
    art_print = over(over(graded, fx["Roundel shadow"]), fx["Jata glow"])
    write_print_pdf(art_print, os.path.join(root, f"01_Template/CGSO2026_overlay_{key}_print.pdf"),
                    os.path.join(out_dir, f"CGSO2026_{key}_SCREEN_RGB.pdf"), os.path.join(out_dir, f"_art_{key}_300ppi.jpg"))
    full = np.ones((H, W, 4), np.float32)
    full[..., :3] = graded
    write_psd(os.path.join(out_dir, psd_name), [
        ("group", "ARTWORK (layers before grade)", layers),
        ("Final grade + grain (flattened artwork)", full),
        ("group", "FIXED ELEMENTS", [(n, fx[n]) for n in FIXED_ORDER]),
    ])
    return final


def melt_background(ist_rgba_src, bgmask, place_kw, layer, sky_rgb, top=0.9, bottom=0.5):
    """Dissolve the (already hazed) background buildings into the cover's own sky,
    stronger toward their tops - atmospheric perspective, no architecture changed."""
    m = np.dstack([bgmask, bgmask, bgmask, ist_rgba_src[..., 3]])
    w = place(m, **place_kw)[..., 0] * (layer[..., 3] > 0.01)
    rows = np.where(w.max(axis=1) > 0.5)[0]
    if len(rows) == 0:
        return layer
    y0, y1 = rows.min(), rows.max()
    v = np.clip((y1 - np.arange(H, dtype=np.float32)) / max(1, y1 - y0), 0, 1)[:, None]
    f = (w * (bottom + (top - bottom) * v))[..., None]
    out = layer.copy()
    out[..., :3] = layer[..., :3] * (1 - f) + sky_rgb * f
    return out


# ------------------------------------------------------------------ live, editable PSD
from psd_tools.constants import BlendMode

SRC = {
    "C2-B.png": "assets/C2/C2-B_v2.png", "C2-C.png": "assets/C2/C2-C_v3.png", "C2-D.png": "assets/C2/C2-D_v2.png",
    "C2-C1.png": "assets/C2/C2-C_v1.png",
    # real PDRM / 10 Para insignia retouched in (insignia.py); same photos behind the PSD masks
    "C2-C_ins.png": "assets/C2/C2-C_v3.png", "C2-C1_ins.png": "assets/C2/C2-C_v1.png",
    "C1-C_ins.png": "assets/C1/C1-C_v2.png", "C3-D_ins.png": "assets/C3/C3-D_v2.png",
    "UNI-C2-PDRM_ins.png": "assets/uniformed/UNI-C2-PDRM_v2.png", "UNI-C2-ARMY_ins.png": "assets/uniformed/UNI-C2-ARMY_v2.png",
    "UNI-C3-PDRM_ins.png": "assets/uniformed/UNI-C3-PDRM_v1.png", "UNI-C1-ARMY_ins.png": "assets/uniformed/UNI-C1-ARMY_v1.png",
    "UNI-C2-PDRM3_ins.png": "assets/uniformed/UNI-C2-PDRM_v3.png", "UNI-C3-PDRM2_ins.png": "assets/uniformed/UNI-C3-PDRM_v2.png",
    "C2-E.png": "assets/C2/C2-E_v4.png", "C2-F.png": "assets/C2/C2-F_v1.png",
    "C1-C.png": "assets/C1/C1-C_v2.png", "C1-D.png": "assets/C1/C1-D_v2.png", "C1-E.png": "assets/C1/C1-E_v4.png",
    "C1-F.png": "assets/C1/C1-F_v2.png", "C1-G.png": "assets/C1/C1-G_v1.png",
    "C3-D.png": "assets/C3/C3-D_v2.png", "C3-E.png": "assets/C3/C3-E_v2.png", "C3-F.png": "assets/C3/C3-F_v2.png",
}
MODES = {"normal": BlendMode.NORMAL, "screen": BlendMode.SCREEN, "multiply": BlendMode.MULTIPLY,
         "overlay": BlendMode.OVERLAY, "softlight": BlendMode.SOFT_LIGHT, "add": BlendMode.LINEAR_DODGE}


def src_layer(root, cut_name, **place_kw):
    """The untouched original photo, placed exactly like its cutout (for the PSD mask)."""
    path = SRC.get(cut_name)
    if not path:
        return None
    rgb = load_rgb(os.path.join(root, path))
    return place(np.dstack([rgb, np.ones(rgb.shape[:2], np.float32)]), **place_kw)


class Stack:
    """Composite + a record of every layer (pixels, mask, blend mode, opacity, original photo)."""

    def __init__(self, name, rgb):
        self.comp = rgb.copy()
        self.items = [dict(name=name, rgb=rgb.astype(np.float16), mask=None, mode="normal", opacity=1.0, src=None)]

    def add(self, name, rgba, mode="normal", opacity=1.0, src=None):
        self.comp = blend(self.comp, rgba[..., :3], rgba[..., 3], mode, opacity)
        self.items.append(dict(name=name, rgb=rgba[..., :3].astype(np.float16), mask=rgba[..., 3].astype(np.float16),
                               mode=mode, opacity=opacity, src=None if src is None else src.astype(np.float16)))


def _bbox(m):
    ys, xs = np.where(m)
    if len(ys) == 0:
        return 0, 0, 1, 1
    return ys.min(), xs.min(), ys.max() + 1, xs.max() + 1


def finalize_live(root, key, out_dir, psd_name, stack, grade, fast=False, grain_amt=0.022):
    graded = grade(stack.comp)
    graded = unsharp(graded, 1.0, 0.25)
    g = grain((H, W), amount=grain_amt, size=1.3)
    graded = np.clip(graded + g[..., None] * (0.35 + 0.65 * (1 - np.abs(graded - 0.5) * 2)), 0, 1)
    fx = fixed_layers(root, key)
    final = graded.copy()
    for n in FIXED_ORDER:
        final = over(final, fx[n])
    save_rgb(final, os.path.join(out_dir, f"CGSO2026_{key}_preview.jpg"))
    Image.fromarray(to_u8(final)).resize((W // 3, H // 3), Image.LANCZOS).save(
        os.path.join(out_dir, f"{key}_thumb.jpg"), quality=90)
    if fast:
        return final
    art_print = over(over(graded, fx["Roundel shadow"]), fx["Jata glow"])
    # RGB review copy only; the press files are 06_Print/*_PRINT_CMYK_FOGRA39.pdf (print_proof.py)
    write_print_pdf(art_print, os.path.join(root, f"01_Template/CGSO2026_overlay_{key}_print.pdf"),
                    os.path.join(out_dir, f"CGSO2026_{key}_SCREEN_RGB.pdf"), os.path.join(out_dir, f"_art_{key}_300ppi.jpg"))
    Image.fromarray(to_u8(art_print)).save(os.path.join(out_dir, f"_art_{key}_300ppi.png"), dpi=(300, 300))  # lossless, for CMYK

    # ---- live PSD: RGB document, so every layer = pixels + editable layer mask
    psd = PSDImage.new("RGB", (W, H))
    art = Group.new(psd, "ARTWORK - live layers (grade applied per layer)")
    for it in stack.items:
        rgb = grade(it["rgb"].astype(np.float32))
        if it["mask"] is None:
            m = np.ones((H, W), np.float32)
        else:
            m = it["mask"].astype(np.float32)
        cover = m > 0.002
        if it["src"] is not None:
            s = it["src"].astype(np.float32)
            sa = s[..., 3:4]
            orig = grade(s[..., :3])
            rgb = rgb * m[..., None] + (orig * sa + rgb * (1 - sa)) * (1 - m[..., None])
            cover |= sa[..., 0] > 0.5
        y0, x0, y1, x1 = _bbox(cover)
        rgba = np.dstack([rgb[y0:y1, x0:x1], m[y0:y1, x0:x1]])
        L = PixelLayer.frompil(Image.fromarray(to_u8(rgba), "RGBA"), art, it["name"], int(y0), int(x0))
        L.blend_mode = MODES[it["mode"]]
        L.opacity = int(round(it["opacity"] * 255))
    gl = np.dstack([np.full((H, W, 3), 0.5, np.float32) + g[..., None], np.ones((H, W), np.float32)])
    L = PixelLayer.frompil(Image.fromarray(to_u8(gl), "RGBA"), psd, "Film grain (Overlay)", 0, 0)
    L.blend_mode = BlendMode.OVERLAY
    fxg = Group.new(psd, "FIXED ELEMENTS - Jata, text, roundel")
    for n in FIXED_ORDER:
        a = fx[n]
        y0, x0, y1, x1 = _bbox(a[..., 3] > 0.002)
        PixelLayer.frompil(Image.fromarray(to_u8(a[y0:y1, x0:x1]), "RGBA"), fxg, n, int(y0), int(x0))
    gd = load_rgba(os.path.join(root, "01_Template/CGSO2026_guides.png"))
    Lg = PixelLayer.frompil(Image.fromarray(to_u8(gd), "RGBA"), psd, "GUIDES - bleed / trim / safe (hidden)", 0, 0)
    Lg.visible = False
    psd.image_resources[Resource.RESOLUTION_INFO] = ImageResource(
        key=Resource.RESOLUTION_INFO.value, data=struct.pack(">IHHIHH", 300 << 16, 1, 2, 300 << 16, 1, 2))
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    psd.image_resources[Resource.ICC_PROFILE] = ImageResource(key=Resource.ICC_PROFILE.value, data=srgb)
    psd.save(os.path.join(out_dir, psd_name))
    return final


# ------------------------------------------------------------------ istana domes
def dome_region(rgb, alpha):
    """Full gold-dome silhouettes. The overcast photo leaves the upper tiles and ribs
    desaturated, so a hue mask misses them; fill each dome-like gold component with its
    convex hull (thin gold trims around windows have low solidity and are left alone)."""
    hsv = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    gold = ((hsv[..., 0] > 32) & (hsv[..., 0] < 65) & (hsv[..., 1] > 0.28) & (hsv[..., 2] > 0.35)).astype(np.uint8)
    # opening removes thin trims so they can't join a dome into one low-solidity blob
    core = cv2.morphologyEx(gold, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
    out = gold.copy()
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 1500:
            continue
        x, y, w, h = stats[i, :4]
        sub = (lab[y:y + h, x:x + w] == i).astype(np.uint8)
        cnts, _ = cv2.findContours(sub, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hull = cv2.convexHull(np.vstack(cnts))
        if stats[i, cv2.CC_STAT_AREA] / max(cv2.contourArea(hull), 1) < 0.55:
            continue
        cv2.fillPoly(out[y:y + h, x:x + w], [hull], 1)
    # main dome (largest component, the only one against open sky): its crown facets, outer rim,
    # finial and needle are pale or grey in the overcast photo and fall outside the hue mask, so
    # they went grey under the relights. Take everything opaque from the needle tip down to the
    # dome's base within the dome's own width (sky around it is transparent, so nothing else joins).
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = stats[big, :4]
    top = int(np.argmax((alpha[:, x + w // 2 - 3:x + w // 2 + 4] > 0.3).any(axis=1)))
    span = np.zeros_like(out)
    span[top:y + h, x - 30:x + w + 30] = 1
    out = np.maximum(out, span * (alpha > 0.3))
    # secondary domes stand against the cream walls, whose colour their pale crowns and upper ribs
    # share (median saturation 0.22 vs 0.19), so neither hue nor alpha separates them: use the shape,
    # the hull of the dome's gold body plus its crown apex, minus the poles and flags in front
    assert rgb.shape[1] == 3600, "SECONDARY_DOMES are in ISTANA_base working px"
    sec = np.zeros_like(out)
    for d in SECONDARY_DOMES:
        x0, y0, x1, y1 = d["box"]
        ax, ay = d["apex"]
        ids = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 1500
               and x0 <= stats[i, 0] + stats[i, 2] / 2 <= x1 and y0 <= stats[i, 1] + stats[i, 3] / 2 <= y1]
        ys, xs = np.nonzero(np.isin(lab[y0:y1, x0:x1], ids))
        pts = np.stack([xs + x0, ys + y0], 1)
        if d.get("mirror"):                                   # only one clean half: mirror it about the axis
            pts = np.concatenate([pts, np.stack([2 * ax - pts[:, 0], pts[:, 1]], 1)])
        hull = cv2.convexHull(np.concatenate([pts, [[ax, ay]]]).astype(np.int32))[:, 0].astype(np.float64)
        # the onion outline bulges outward between shoulder and apex (measured 4-11 px outside the
        # straight hull chord on the far-left dome): replace both apex chords with a sine-bulged arc
        k = int(np.argmin(np.hypot(hull[:, 0] - ax, hull[:, 1] - ay)))
        c = hull.mean(axis=0)
        poly_pts = []
        for i in range(len(hull)):
            p, q = hull[i], hull[(i + 1) % len(hull)]
            poly_pts.append(p)
            if k in (i, (i + 1) % len(hull)):
                v = q - p
                nrm = np.array([v[1], -v[0]]) / max(np.hypot(*v), 1e-6)
                if np.dot(nrm, (p + q) / 2 - c) < 0:
                    nrm = -nrm
                bulge = d["bulge"][0 if (p[0] + q[0]) / 2 < ax else 1]          # per side, fitted at 3x zoom
                t = np.linspace(0, 1, 40)[1:-1, None]
                poly_pts.extend(p + t * v + nrm * bulge * np.hypot(*v) * np.sin(np.pi * t))
        cv2.fillPoly(sec, [np.round(np.vstack(poly_pts)).astype(np.int32)], 1)
    S, Hh = hsv[..., 1], hsv[..., 0]
    pole = cv2.morphologyEx((S < 0.07).astype(np.uint8), cv2.MORPH_OPEN, np.ones((41, 1), np.uint8))
    redblue = ((Hh < 12) | (Hh > 330) | ((Hh > 190) & (Hh < 260))) & (S > 0.3)   # flag reds and blues only,
    flag = cv2.morphologyEx(redblue.astype(np.uint8), cv2.MORPH_CLOSE,          # not the crowns' brown grooves
                            np.ones((15, 15), np.uint8))
    occ = cv2.dilate(np.maximum(pole, flag), np.ones((5, 5), np.uint8))
    out = np.where(sec > 0, sec * (1 - occ), out)
    out = out.astype(np.float32) * (alpha > 0.3)
    return blur(out, 1.5)


# secondary domes in ISTANA_base working px (3600 x 2400): a box that gathers the dome's gold-body
# components, the crown apex where the facets meet the finial collar (measured at 4x zoom), and the
# outward bulge of the shoulder-to-apex outline as a fraction of the chord (left, right side)
SECONDARY_DOMES = [
    dict(box=(1580, 1300, 2330, 1690), apex=(1946, 1250), bulge=(0.02, 0.02)),   # lower central (flagpole)
    dict(box=(950, 1340, 1200, 1470), apex=(1078, 1327), bulge=(0.06, 0.08)),    # upper left
    dict(box=(2520, 1350, 2770, 1475), apex=(2643, 1341), bulge=(0.08, 0.04)),   # upper right (behind a flag)
    dict(box=(585, 1540, 830, 1675), apex=(713, 1530), bulge=(0.08, 0.08)),      # far left
    dict(box=(2960, 1540, 3180, 1675), apex=(3057, 1527), bulge=(0.06, 0.08)),   # far right
    dict(box=(1970, 1860, 2120, 2000), apex=(2112, 1834), bulge=(0.08, 0.08),    # entrance (right half behind
         mirror=True),                                                           # a pole and the door frame)
]


def goldify(rgb, region, gold="#E6BF58", strength=0.7):
    """Retouch desaturated dome tiles back to the dome's own gold (luminance kept)."""
    hsv = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    g = hexf(gold)
    target = lum(rgb)[..., None] / max(float(lum(g[None, None])[0, 0]), 1e-3) * g
    w = (region * np.clip((0.34 - hsv[..., 1]) / 0.2, 0, 1) * strength)[..., None]
    return np.clip(rgb * (1 - w) + target * w, 0, 1)
