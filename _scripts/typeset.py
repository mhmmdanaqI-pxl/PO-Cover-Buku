"""Shared typesetting helpers: HarfBuzz shaping (kerning on) + fontTools outlines.

Text is converted to outline paths so every output (PDF, SVG, PNG) is identical
and needs no installed fonts.
"""
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

import font_roboto

FONT_DIR = os.path.join(os.path.dirname(font_roboto.__file__), "files")
_cache = {}


def font(weight):
    """weight: 'Regular', 'Medium', 'Bold', 'Black' ..."""
    if weight not in _cache:
        path = os.path.join(FONT_DIR, f"Roboto-{weight}.ttf")
        face = hb.Face(hb.Blob.from_file_path(path))
        _cache[weight] = (hb.Font(face), TTFont(path), face.upem)
    return _cache[weight]


class _OpsPen(BasePen):
    """Collects contours as ('M'|'L'|'C', points...) in font units; quadratics become cubics."""

    def __init__(self, glyphset):
        super().__init__(glyphset)
        self.ops = []

    def _moveTo(self, p):
        self.ops.append(("M", p))

    def _lineTo(self, p):
        self.ops.append(("L", p))

    def _curveToOne(self, p1, p2, p3):
        self.ops.append(("C", p1, p2, p3))

    def _closePath(self):
        self.ops.append(("Z",))


def shape_line(text, weight, size, tracking=0.0):
    """Returns list of (ops_in_font_units, x_offset_pt, y_offset_pt), scale, advance_pt.

    tracking is in em (e.g. -0.01 = Photoshop tracking -10).
    """
    hbfont, tt, upem = font(weight)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    gs = tt.getGlyphSet()
    scale = size / upem
    x = 0.0
    glyphs = []
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = tt.getGlyphName(info.codepoint)
        pen = _OpsPen(gs)
        gs[name].draw(pen)
        glyphs.append((pen.ops, x + pos.x_offset * scale, -pos.y_offset * scale))
        x += pos.x_advance * scale
        if i < n - 1:
            x += tracking * size
    return glyphs, scale, x


def outline_bounds(glyphs, scale):
    """Ink bounds (x0, x1, y_top, y_bottom) in pt relative to origin/baseline, y down."""
    xs, ys = [], []
    for ops, gx, gy in glyphs:
        for op in ops:
            for p in op[1:]:
                xs.append(gx + p[0] * scale)
                ys.append(gy - p[1] * scale)
    return min(xs), max(xs), min(ys), max(ys)


def line_paths(text, weight, size, tracking=0.0, anchor="left", x=0.0, baseline=0.0):
    """Absolute contours (pt, y down) for one line, aligned optically by ink edge.

    anchor 'left'  -> ink left edge sits exactly on x
    anchor 'right' -> ink right edge sits exactly on x
    Returns (contours, ink_bounds) where contours is a list of op lists.
    """
    glyphs, scale, _ = shape_line(text, weight, size, tracking)
    x0, x1, yt, yb = outline_bounds(glyphs, scale)
    dx = x - x0 if anchor == "left" else x - x1
    contours = []
    for ops, gx, gy in glyphs:
        cur = []
        for op in ops:
            if op[0] == "Z":
                if cur:
                    contours.append(cur)
                cur = []
                continue
            pts = [(dx + gx + p[0] * scale, baseline + gy - p[1] * scale) for p in op[1:]]
            cur.append((op[0], *pts))
        if cur:
            contours.append(cur)
    return contours, (x0 + dx, x1 + dx, baseline + yt, baseline + yb)


def draw_contours(page_or_shape, contours, color, oc=0):
    """Fill contours on a pymupdf page (nonzero winding)."""
    shape = page_or_shape.new_shape()
    for c in contours:
        start = c[0][1]
        last = start
        for op in c[1:]:
            if op[0] == "L":
                shape.draw_line(last, op[1])
                last = op[1]
            elif op[0] == "C":
                shape.draw_bezier(last, op[1], op[2], op[3])
                last = op[3]
        if last != start:
            shape.draw_line(last, start)
    shape.finish(fill=color, color=None, width=0, even_odd=False, closePath=True, oc=oc)
    shape.commit()


def contours_to_svg(contours, ndigits=2):
    f = lambda v: f"{v:.{ndigits}f}".rstrip("0").rstrip(".")
    out = []
    for c in contours:
        out.append(f"M{f(c[0][1][0])} {f(c[0][1][1])}")
        for op in c[1:]:
            if op[0] == "L":
                out.append(f"L{f(op[1][0])} {f(op[1][1])}")
            else:
                out.append("C" + " ".join(f"{f(p[0])} {f(p[1])}" for p in op[1:]))
        out.append("Z")
    return "".join(out)
