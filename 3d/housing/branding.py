"""Lastdrop branding as 2D shapes (shapely), sized for printing.
Glyph outlines come straight from the font files (fontTools), curves flattened, then every shape is grown by a
fixed amount so that no engraved stroke is thinner than the nozzle can make. Units: mm. y up, text reads along +x."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity

class _Flatten(BasePen):
    def __init__(self, gs, step=24):
        super().__init__(gs); self.rings, self.cur, self.step = [], [], step
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.step + 1):
            t = i / self.step; s = 1 - t
            self.cur.append((s**3*p0[0] + 3*s*s*t*p1[0] + 3*s*t*t*p2[0] + t**3*p3[0],
                             s**3*p0[1] + 3*s*s*t*p1[1] + 3*s*t*t*p2[1] + t**3*p3[1]))
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.step + 1):
            t = i / self.step; s = 1 - t
            self.cur.append((s*s*p0[0] + 2*s*t*p1[0] + t*t*p2[0], s*s*p0[1] + 2*s*t*p1[1] + t*t*p2[1]))
    def _closePath(self):
        if len(self.cur) > 2: self.rings.append(self.cur)
        self.cur = []
    _endPath = _closePath

def _signed_area(r):
    return 0.5 * sum(r[i][0]*r[i-1][1] - r[i-1][0]*r[i][1] for i in range(len(r)))

class Font:
    def __init__(self, path):
        self.f = TTFont(path); self.gs = self.f.getGlyphSet(); self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
    def glyph(self, ch):
        name = self.cmap[ord(ch)]
        pen = _Flatten(self.gs); self.gs[name].draw(pen)
        polys = [Polygon(r).buffer(0) for r in pen.rings]
        areas = [_signed_area(r) for r in pen.rings]
        if not polys:
            return Polygon(), self.gs[name].width
        main = max(range(len(polys)), key=lambda i: abs(areas[i]))
        sgn = math.copysign(1, areas[main])                      # same winding as the biggest contour = ink
        ink = unary_union([p for p, a in zip(polys, areas) if math.copysign(1, a) == sgn])
        holes = unary_union([p for p, a in zip(polys, areas) if math.copysign(1, a) != sgn])
        return ink.difference(holes), self.gs[name].width
    def text(self, s, tracking_units=0.0):
        shapes, x = [], 0.0
        for ch in s:
            g, adv = self.glyph(ch)
            if not g.is_empty:
                shapes.append(affinity.translate(g, x, 0))
            x += adv + tracking_units
        return unary_union(shapes)

def _fit(shape, *, width=None, height_of=None, height=None, font=None):
    if width is not None:
        b = shape.bounds; k = width / (b[2] - b[0])
    else:
        ref = font.glyph(height_of)[0].bounds; k = height / (ref[3] - ref[1])
    return affinity.scale(shape, k, k, origin=(0, 0)), k

def drop(R, tip, line):
    """Water-drop outline with a little water left at the bottom: the 'last drop'."""
    def shape(r, d):
        a = math.asin(r / d)
        circle = Polygon([(r*math.cos(t), r*math.sin(t)) for t in [i*2*math.pi/180 for i in range(180)]])
        tri = Polygon([(-r*math.cos(a), r*math.sin(a)), (0, d), (r*math.cos(a), r*math.sin(a))])
        return unary_union([circle, tri])
    d = tip * R; a = math.asin(R / d)
    ring = shape(R, d).difference(shape(R - line, d - line / math.sin(a)))
    inner = shape(R - 2*line, d)                                  # a full line of wall between ring and water
    water = inner.intersection(box(-R, -R, R, -0.05*R))           # a little water left: about the bottom third
    return ring, water

_fonts = {}
def _font(path):
    if path not in _fonts: _fonts[path] = Font(path)
    return _fonts[path]

def rich_line(item, default_font, default_grow):
    """item: (text, height, tracking_mm, grow) in default_font, or
    {"h": height, "ref": "x" or "H", "segments": [(text, font_path, tracking_mm, grow), ...]}: all segments share one
    em size, set so the FIRST segment's ref letter is `h` mm tall, and sit on one baseline (like 'taflev' + '.com')."""
    if not isinstance(item, dict):
        s, h, tr, *g = item
        item = {"h": h, "ref": "H" if s.isupper() else "x", "segments": [(s, default_font, tr, g[0] if g else default_grow)]}
    f0 = _font(item["segments"][0][1])
    ref = f0.glyph(item["ref"])[0].bounds
    em_mm = item["h"] / (ref[3] - ref[1]) * f0.upm                # mm per em
    out, x = [], 0.0
    for s, path, tr, grow in item["segments"]:
        f = _font(path); k = em_mm / f.upm
        t = affinity.scale(f.text(s, tr / k), k, k, origin=(0, 0))
        if not t.is_empty:
            b = t.bounds
            out.append(affinity.translate(t, x - b[0], 0).buffer(grow, quad_segs=8))
            x += (b[2] - b[0]) + tr + 0.04*em_mm
    return unary_union(out)

def layout(name_font, byline_font, name, name_w, name_grow, byline, byline_grow, drop_args, gaps):
    """Returns (all, pieces): one shapely shape with everything, centred on (0, 0), and the same placement split into
    named pieces: drop_ring, water, name, byline0, byline1, ..."""
    nf, bf = Font(name_font), Font(byline_font)
    ring, water = drop(*drop_args)
    lines = [unary_union([ring, water])]
    n = nf.text(name)
    n, _ = _fit(n, width=name_w - 2*name_grow)
    lines.append(n.buffer(name_grow, quad_segs=8))
    for item in byline:
        lines.append(rich_line(item, byline_font, byline_grow))
    out, moves, y = [], [], 0.0
    for i, sh in enumerate(lines):
        b = sh.bounds
        moves.append((-(b[0] + b[2]) / 2, y - b[3]))
        out.append(affinity.translate(sh, *moves[-1]))
        y -= (b[3] - b[1]) + (gaps[i] if i < len(gaps) else 0)
    allu = unary_union(out); b = allu.bounds
    c = (-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)
    mv = lambda sh, i: affinity.translate(sh, moves[i][0] + c[0], moves[i][1] + c[1]).simplify(0.01)
    pieces = {"drop_ring": mv(ring, 0), "water": mv(water, 0), "name": mv(lines[1], 1)}
    for j in range(len(byline)):
        pieces[f"byline{j}"] = mv(lines[2 + j], 2 + j)
    return affinity.translate(allu, *c).simplify(0.01), pieces

def polygons(shape):
    return list(shape.geoms) if isinstance(shape, MultiPolygon) else [shape]
