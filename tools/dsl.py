"""A small SVG drawing kit for the site's artwork.

Flat vector only: rectangles, lines, circles, paths. Every drawing in
uploads/ is produced from one of the build-*-art.py scripts beside this file.
"""
PAPER  = '#F3F3EF'
PAPER2 = '#EAEAE4'
INK    = '#101010'
INK2   = '#6B6B66'
INK3   = '#9A9A94'
HAIR   = '#DCDCD5'
HAIR2  = '#C9CAC2'
ACCENT = '#E8613C'
GRAPH  = '#0C0C0C'
ONDARK = '#F3F3EF'

def _f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.') if isinstance(v, float) else str(v)

def _attrs(**kw):
    out = []
    for k, v in kw.items():
        if v is None: continue
        out.append('%s="%s"' % (k.replace('_', '-'), _f(v) if isinstance(v, (int, float)) else v))
    return ' '.join(out)

def rect(x, y, w, h, fill='none', r=0, stroke=None, sw=1, opacity=None, dash=None):
    return '<rect %s/>' % _attrs(x=x, y=y, width=w, height=h, rx=r or None, fill=fill, stroke=stroke,
                                 stroke_width=sw if stroke else None, opacity=opacity, stroke_dasharray=dash)

def line(x1, y1, x2, y2, stroke=HAIR, sw=1, dash=None, opacity=None, cap='round'):
    return '<line %s/>' % _attrs(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=sw,
                                 stroke_linecap=cap, stroke_dasharray=dash, opacity=opacity)

def circle(cx, cy, r, fill='none', stroke=None, sw=1, opacity=None):
    return '<circle %s/>' % _attrs(cx=cx, cy=cy, r=r, fill=fill, stroke=stroke,
                                   stroke_width=sw if stroke else None, opacity=opacity)

def path(d, fill='none', stroke=None, sw=1, opacity=None, dash=None, cap='round', join='round'):
    return '<path %s/>' % _attrs(d=d, fill=fill, stroke=stroke, stroke_width=sw if stroke else None,
                                 stroke_linecap=cap, stroke_linejoin=join, stroke_dasharray=dash, opacity=opacity)

def curve(x1, y1, x2, y2, bow=0.28, **kw):
    """A gentle S-curve between two points, bowing horizontally."""
    dx = (x2 - x1) * bow
    return path('M%s %s C%s %s %s %s %s %s' % (_f(x1), _f(y1), _f(x1 + dx), _f(y1), _f(x2 - dx), _f(y2), _f(x2), _f(y2)), **kw)

def check(cx, cy, s, stroke, sw=2.2):
    return path('M%s %s L%s %s L%s %s' % (_f(cx - s), _f(cy), _f(cx - s * 0.25), _f(cy + s * 0.75), _f(cx + s), _f(cy - s * 0.85)), stroke=stroke, sw=sw)

def cross(cx, cy, s, stroke, sw=2.2):
    return (line(cx - s, cy - s, cx + s, cy + s, stroke, sw) + line(cx + s, cy - s, cx - s, cy + s, stroke, sw))

def mark(cx, cy, s, fill=ACCENT):
    return circle(cx, cy, s, fill=fill)

def bar(x, y, w, h, pct, fill, track=HAIR, r=None):
    r = h / 2 if r is None else r
    return rect(x, y, w, h, fill=track, r=r) + rect(x, y, w * pct, h, fill=fill, r=r)

class SVG:
    def __init__(self, w, h, bg=None):
        self.w, self.h, self.parts = w, h, []
        if bg: self.parts.append(rect(0, 0, w, h, fill=bg))
    def add(self, s): self.parts.append(s)
    def text(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img">\n%s\n</svg>\n'
                % (self.w, self.h, self.w, self.h, '\n'.join(self.parts)))
    def save(self, p):
        t = self.text(); open(p, 'w', encoding='utf-8').write(t); return len(t)
