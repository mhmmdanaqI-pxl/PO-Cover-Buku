"""Press-ready CMYK print files + soft proofs for the three covers (FOGRA39, 300% TAC).

For each cover:
  - lossless RGB artwork (04_Final/<key>/_art_<key>_300ppi.png) -> FOGRA39 CMYK,
    relative colorimetric + black point compensation, stored lossless (Flate)
  - vector overlay (Jata, office block, headline, roundel) colour operators rewritten
    to DeviceCMYK: near-white -> paper, near-black -> 100% K, roundel keeps its
    designer CMYK values, everything else through the same FOGRA39 transform
  - checks: total ink (TAC), colour shift (CIEDE2000) vs the RGB master, no RGB left
  - soft proof (paper white simulated) + gamut-warning map
Outputs in 06_Print/.
Run: venv python -I _scripts/print_proof.py <workspace>
"""
import os
import re
import sys

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageCms

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "06_Print")
PROFILE = os.path.join(OUT, "_profile", "Coated_Fogra39L_VIGC_300.icc")
os.makedirs(OUT, exist_ok=True)

srgb = ImageCms.createProfile("sRGB")
fogra = ImageCms.getOpenProfile(PROFILE)
BPC = ImageCms.Flags.BLACKPOINTCOMPENSATION
REL, ABS = ImageCms.Intent.RELATIVE_COLORIMETRIC, ImageCms.Intent.ABSOLUTE_COLORIMETRIC
to_cmyk = ImageCms.buildTransform(srgb, fogra, "RGB", "CMYK", REL, BPC)
proof_rel = ImageCms.buildTransform(fogra, srgb, "CMYK", "RGB", REL, BPC)
proof_abs = ImageCms.buildTransform(fogra, srgb, "CMYK", "RGB", ABS)


# ------------------------------------------------------------------ colour maths
def lab(rgb_u8):
    return cv2.cvtColor(rgb_u8.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def de2000(lab1, lab2):
    L1, a1, b1 = [lab1[..., i] for i in range(3)]
    L2, a2, b2 = [lab2[..., i] for i in range(3)]
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh))
    dh = np.where(C1p * C2p == 0, 0, dh)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hs = h1p + h2p
    hbp = np.where(C1p * C2p == 0, hs, np.where(np.abs(h1p - h2p) <= 180, hs / 2,
                                               np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)))
    T = (1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp))
         + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dth = 30 * np.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dth)) * Rc
    return np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def vec_cmyk(r, g, b):
    """One vector colour -> CMYK (0..1) with prepress rules."""
    mx, mn = max(r, g, b), min(r, g, b)
    if mn > 0.95 and mx - mn < 0.03:
        return (0.0, 0.0, 0.0, 0.0)                     # paper white, no stray dots
    if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.16 and mx - mn < 0.07:
        return (0.0, 0.0, 0.0, 1.0)                     # fine black linework: 100% K, no registration fringe
    px = Image.new("RGB", (1, 1), tuple(int(round(v * 255)) for v in (r, g, b)))
    c = [v / 255 for v in ImageCms.applyTransform(px, to_cmyk).getpixel((0, 0))]
    if max(c) > 0.5:                                    # clean solid: drop contaminant inks under 5%
        c = [0.0 if v < 0.05 else v for v in c]
    return tuple(round(v, 4) for v in c)


NUM = r"(\d*\.?\d+)"
RGB_OP = re.compile(rf"{NUM}\s+{NUM}\s+{NUM}\s+(rg|RG)\b")
SCN_OP = re.compile(rf"/CS0\s+(cs|CS)\s+")
CMYK_SCN = re.compile(rf"{NUM}\s+{NUM}\s+{NUM}\s+{NUM}\s+(scn|SCN)\b")


def cmyk_overlay(src_path):
    """Rewrite every RGB colour operator in the overlay to DeviceCMYK."""
    d = pymupdf.open(src_path)
    log = {}
    for x in range(1, d.xref_length()):
        if not d.xref_is_stream(x):
            continue
        try:
            s = d.xref_stream(x).decode("latin-1")
        except Exception:
            continue

        def rep(m):
            r, g, b = (float(m.group(i)) for i in (1, 2, 3))
            c = vec_cmyk(r, g, b)
            log[(round(r, 3), round(g, 3), round(b, 3))] = c
            op = "k" if m.group(4) == "rg" else "K"
            return " ".join(f"{v:.4f}".rstrip("0").rstrip(".") or "0" for v in c) + f" {op}"

        s2 = RGB_OP.sub(rep, s)
        # the Jata / roundel .ai sources mark their art as Illustrator "Layer 1" optional content that
        # the PDF never declares (a PDF/X preflight error): keep the art, drop the layer marker
        s2 = re.sub(r"/OC\s+/MC\d+\s+BDC", "/Layer BMC", s2)
        # roundel: designer CMYK in an ICC-based space -> same numbers as DeviceCMYK
        s2 = SCN_OP.sub("", s2)
        s2 = CMYK_SCN.sub(lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)} {m.group(4)} "
                                    f"{'k' if m.group(5) == 'scn' else 'K'}", s2)
        if s2 != s:
            d.update_stream(x, s2.encode("latin-1"))
    for x in range(1, d.xref_length()):                 # transparency groups blend in CMYK
        o = d.xref_object(x, compressed=False)
        if "/DeviceRGB" in o:
            d.update_object(x, o.replace("/DeviceRGB", "/DeviceCMYK"))
        if "/Properties" in o and "/MC" in o:           # the now-unused layer references
            d.xref_set_key(x, "Resources/Properties", "null")
    return d, log


def check_no_rgb(doc):
    bad = []
    for x in range(1, doc.xref_length()):
        o = doc.xref_object(x, compressed=False)
        if "/DeviceRGB" in o or "/CalRGB" in o:
            bad.append(f"xref {x}: RGB colour space")
        if "/ICCBased" in o or "/CS0" in o:
            bad.append(f"xref {x}: ICC tag other than the output intent")
        if "/OCG" in o:
            bad.append(f"xref {x}: undeclared optional-content layer")
        if doc.xref_is_stream(x):
            try:
                s = doc.xref_stream(x).decode("latin-1")
            except Exception:
                continue
            if RGB_OP.search(s):
                bad.append(f"xref {x}: rg/RG operator")
    return bad


def add_output_intent(doc):
    icc = open(PROFILE, "rb").read()
    xi = doc.get_new_xref()
    doc.update_object(xi, "<< /N 4 /Alternate /DeviceCMYK >>")
    doc.update_stream(xi, icc)
    doc.xref_set_key(doc.pdf_catalog(), "OutputIntents",
                     f"[<< /Type /OutputIntent /S /GTS_PDFX /OutputConditionIdentifier (FOGRA39) "
                     f"/OutputCondition (Offset printing, coated paper, FOGRA39L, 300% TAC) "
                     f"/RegistryName (http://www.color.org) /Info (Coated_Fogra39L_VIGC_300) "
                     f"/DestOutputProfile {xi} 0 R >>]")


report = []
for key, title in (("C1", "Alam Sekitar"), ("C2", "Keselamatan Dokumen"), ("C3", "Ekonomi")):
    art = Image.open(os.path.join(ROOT, f"04_Final/{key}/_art_{key}_300ppi.png")).convert("RGB")
    cmyk = ImageCms.applyTransform(art, to_cmyk)
    c = np.asarray(cmyk, np.float32) / 255 * 100
    tac = c.sum(axis=2)

    # soft proofs (relative for measurement, absolute = paper white simulated for viewing)
    rel = np.asarray(ImageCms.applyTransform(cmyk, proof_rel))
    absv = ImageCms.applyTransform(cmyk, proof_abs)
    de = de2000(lab(np.asarray(art)), lab(rel))

    # overlay -> CMYK, then assemble the press PDF
    ov, log = cmyk_overlay(os.path.join(ROOT, f"01_Template/CGSO2026_overlay_{key}_print.pdf"))
    doc = pymupdf.open()
    page = doc.new_page(width=ov[0].rect.width, height=ov[0].rect.height)
    pix = pymupdf.Pixmap(pymupdf.csCMYK, cmyk.width, cmyk.height, cmyk.tobytes(), False)
    page.insert_image(page.rect, pixmap=pix)
    page.show_pdf_page(page.rect, ov, 0)
    page.set_bleedbox(page.rect)
    page.set_trimbox(ov[0].trimbox)
    # untag the CMYK: the numbers are already FOGRA39, so the output intent must govern them.
    # MuPDF tags an inserted CMYK pixmap with its default SWOP ICC, and the roundel form still
    # lists the designer's U.S. Coated SWOP v2 space (unused once its scn ops became k)
    doc.xref_set_key(page.get_images()[0][0], "ColorSpace", "/DeviceCMYK")
    for x in range(1, doc.xref_length()):
        if "/CS0" in doc.xref_object(x, compressed=False):
            doc.xref_set_key(x, "Resources/ColorSpace", "null")
    add_output_intent(doc)
    doc.set_metadata({"title": f"CGSO 2026 kulit buku - Konsep {key[1]} {title} (CMYK FOGRA39)",
                      "creator": "CGSO 2026 cover pipeline", "subject": "A5 148x210 mm + 3 mm bleed, 300 ppi"})
    pdf_path = os.path.join(OUT, f"CGSO2026_{key}_PRINT_CMYK_FOGRA39.pdf")
    doc.save(pdf_path, garbage=3, deflate=True)

    # verify what was written
    chk = pymupdf.open(pdf_path)
    imgs = chk[0].get_images(full=True)
    img_cs = {chk.extract_image(i[0])["colorspace"] for i in imgs}
    bad = check_no_rgb(chk)
    render = np.asarray(Image.frombytes("RGB", (lambda p: (p.width, p.height))(chk[0].get_pixmap(dpi=100)),
                                        chk[0].get_pixmap(dpi=100).samples))

    # full-cover soft proof: CMYK artwork + CMYK vector overlay rasterised in CMYK, then FOGRA39 -> screen
    ovp = ov[0].get_pixmap(dpi=300, colorspace=pymupdf.csCMYK, alpha=True)
    o = np.frombuffer(ovp.samples, np.uint8).reshape(ovp.height, ovp.width, 5).astype(np.float32)
    o = o[:cmyk.height, :cmyk.width]
    oa = o[..., 4:5] / 255
    oc = np.where(oa > 0, o[..., :4] / np.maximum(oa, 1e-6), 0)          # un-premultiply
    full_cmyk = np.asarray(cmyk, np.float32) * (1 - oa) + oc * oa
    full_cmyk = Image.fromarray(np.clip(full_cmyk + 0.5, 0, 255).astype(np.uint8), "CMYK")
    absv = ImageCms.applyTransform(full_cmyk, proof_abs)
    screen = Image.open(os.path.join(ROOT, f"04_Final/{key}/CGSO2026_{key}_preview.jpg")).convert("RGB")

    # proof images
    absv.save(os.path.join(OUT, f"{key}_softproof_FOGRA39.jpg"), quality=92, dpi=(300, 300))
    warn = np.asarray(art).copy()
    m = de > 6
    warn[m] = (warn[m] * 0.3 + np.array([255, 0, 200]) * 0.7).astype(np.uint8)
    Image.fromarray(warn).resize((art.width // 2, art.height // 2), Image.LANCZOS).save(
        os.path.join(OUT, f"{key}_gamut_warning.jpg"), quality=88)
    side = Image.new("RGB", (art.width * 2 // 3 + 30, art.height // 3 + 20), (40, 40, 40))
    side.paste(screen.resize((art.width // 3, art.height // 3), Image.LANCZOS), (10, 10))
    side.paste(absv.resize((art.width // 3, art.height // 3), Image.LANCZOS), (art.width // 3 + 20, 10))
    side.save(os.path.join(OUT, f"{key}_screen_vs_print.jpg"), quality=90)

    report.append(dict(key=key, title=title, tac_max=float(tac.max()), tac_p999=float(np.percentile(tac, 99.9)),
                       de_mean=float(de.mean()), de_p95=float(np.percentile(de, 95)),
                       de_gt3=float((de > 3).mean() * 100), de_gt6=float((de > 6).mean() * 100),
                       img_cs=sorted(img_cs), rgb_left=len(bad), vec=log, pdf=os.path.basename(pdf_path),
                       mb=os.path.getsize(pdf_path) / 1e6))
    print(f"{key}: TAC max {tac.max():.0f}% | dE2000 mean {de.mean():.2f}, p95 {np.percentile(de, 95):.2f}, "
          f">6: {(de > 6).mean() * 100:.2f}% | image cs {sorted(img_cs)} | RGB left {len(bad)} | "
          f"{os.path.getsize(pdf_path) / 1e6:.1f} MB")

np.save(os.path.join(OUT, "_report.npy"), np.array(report, dtype=object), allow_pickle=True)
