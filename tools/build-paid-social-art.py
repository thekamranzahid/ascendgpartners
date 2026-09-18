"""Paid Social — the four drawings the page needs.

Same house style as the rest of the family: flat vector, hairlines, one accent
that marks the outcome, and nothing that is not carrying meaning.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from dsl import *

OUT = 'outps'
CARD = '#FBFBF9'

def save(s, name):
    n = s.save(f'{OUT}/{name}.svg'); print(f'{n/1024:6.1f}KB  {name}.svg')

def ad(cx, cy, w, h, stroke=INK, sw=3.4, fill=CARD, r=18, accent=False, lines=2):
    """An ad unit: a creative frame, a line of copy, and the button under it."""
    o = [rect(cx-w/2, cy-h/2, w, h, fill=fill, r=r, stroke=stroke, sw=sw)]
    ix, iw = cx - w/2 + w*0.08, w*0.84
    ch = h * 0.52
    o.append(rect(ix, cy-h/2 + h*0.07, iw, ch, fill='none', r=r*0.6, stroke=stroke, sw=sw*0.8))
    # a simple mark inside the creative frame so it does not read as an empty box
    o.append(circle(ix + iw*0.30, cy-h/2 + h*0.07 + ch*0.42, min(iw, ch)*0.13, fill='none', stroke=stroke, sw=sw*0.8))
    o.append(path('M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (
        ix + iw*0.14, cy-h/2 + h*0.07 + ch*0.86,
        ix + iw*0.46, cy-h/2 + h*0.07 + ch*0.50,
        ix + iw*0.86, cy-h/2 + h*0.07 + ch*0.86), stroke=stroke, sw=sw*0.8))
    y = cy-h/2 + h*0.66
    o.append(rect(ix, y, iw*0.72, max(12, h*0.045), fill=stroke, r=h*0.024))
    for i in range(lines-1):
        o.append(rect(ix, y + h*0.075 + i*h*0.06, iw*0.5, max(9, h*0.032), fill=HAIR2, r=h*0.018))
    bw, bh = iw*0.62, h*0.10
    o.append(rect(ix, cy + h/2 - h*0.055 - bh, bw, bh,
                  fill=ACCENT if accent else 'none', r=bh/2,
                  stroke=None if accent else stroke, sw=sw*0.8))
    o.append(rect(ix + bw*0.24, cy + h/2 - h*0.055 - bh/2 - h*0.014, bw*0.5, h*0.028,
                  fill='#FFFFFF' if accent else stroke, r=h*0.014))
    return ''.join(o)

# ── hero · one ad, and what it returned ──────────────────────────────────────
def hero():
    W, H = 1200, 800
    s = SVG(W, H, bg=None)
    s.add(ad(330, 400, 400, 640, INK, 4, accent=True, lines=3))
    x0, x1 = 620, 1110
    labels = [(0.42, INK), (0.68, INK), (0.92, ACCENT)]
    y = 300
    for v, col in labels:
        s.add(rect(x0, y - 24, x1 - x0, 48, fill=HAIR, r=24))
        s.add(rect(x0, y - 24, (x1 - x0) * v, 48, fill=col, r=24))
        y += 106
    s.add(line(x0, 226, x1, 226, HAIR2, 2.4))
    s.add(line(x0, 560, x1, 560, HAIR2, 2.4))
    return s

# ── step 01 · the message that moves buyers ──────────────────────────────────
def creative():
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    xs = [200, 400, 600, 800, 1000]
    hs = [102, 152, 84, 230, 128]
    win = 3
    base = 762
    for i, x in enumerate(xs):
        on = i == win
        s.add(ad(x, 278, 168, 356, ACCENT if on else INK, 3.6 if on else 2.8, accent=on, lines=2))
    for i, (x, hgt) in enumerate(zip(xs, hs)):
        on = i == win
        s.add(rect(x - 46, base - hgt, 92, hgt, fill=ACCENT if on else INK, r=14))
    s.add(line(96, base + 22, 1104, base + 22, INK, 3.2))
    return s

# ── step 02 · a full-funnel media system ─────────────────────────────────────
def funnel():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    groups = [(300, 12, 0.95), (800, 7, 0.62), (1300, 4, 0.40)]
    for gi, (gx, n, _) in enumerate(groups):
        last = gi == 2
        col = ACCENT if last else INK
        s.add(ad(gx, 260, 250, 330, col, 3.6 if last else 3, accent=last, lines=2))
        # the audience that stage speaks to
        cols = 4
        for k in range(n):
            cx = gx - 108 + (k % cols) * 72
            cy = 560 + (k // cols) * 72
            s.add(circle(cx, cy, 22, fill='none', stroke=col if last else INK, sw=3))
        if gi < 2:
            nx = groups[gi + 1][0]
            s.add(path(f'M{gx + 140:.0f} 260 C{gx + 250:.0f} 260 {nx - 250:.0f} 260 {nx - 140:.0f} 260',
                       stroke=HAIR2, sw=3))
            s.add(path(f'M{gx + 130:.0f} 596 C{gx + 250:.0f} 596 {nx - 250:.0f} 596 {nx - 130:.0f} 596',
                       stroke=HAIR2, sw=3))
    return s

# ── step 03 · scale without breaking efficiency (on graphite) ────────────────
def scale():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    n = 9
    x0, cw, gap = 180, 96, 44
    base = 700
    hs = [96, 138, 178, 232, 286, 348, 410, 486, 560]
    tops = []
    for i, hgt in enumerate(hs):
        x = x0 + i * (cw + gap)
        s.add(rect(x, base - hgt, cw, hgt, fill=ONDARK, r=14))
        tops.append((x + cw / 2, base - hgt))
    # efficiency, held level while the spend climbs
    ey = 250
    s.add(path('M%.0f %.0f L%.0f %.0f' % (x0 - 30, ey, x0 + (n - 1) * (cw + gap) + cw + 30, ey),
               stroke=ACCENT, sw=6))
    for i in (2, 5, 8):
        x = x0 + i * (cw + gap) + cw / 2
        s.add(circle(x, ey, 17, fill=ACCENT))
        s.add(line(x, ey + 24, x, base - hs[i] - 20, '#3A3A38', 3, dash='12 10'))
    s.add(line(150, base + 26, 1450, base + 26, '#3A3A38', 3))
    return s

if __name__ == '__main__':
    save(hero(), 'ps-hero')
    save(creative(), 'ps-creative')
    save(funnel(), 'ps-funnel')
    save(scale(), 'ps-scale')
