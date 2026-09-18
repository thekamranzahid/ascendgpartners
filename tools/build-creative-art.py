"""Creative — the four drawings the page needs.

House style: flat vector, hairlines, one accent that marks the outcome.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from dsl import *

OUT = 'outcr'
CARD = '#FBFBF9'

def save(s, name):
    n = s.save(f'{OUT}/{name}.svg'); print(f'{n/1024:6.1f}KB  {name}.svg')

def frame(cx, cy, w, h, stroke=INK, sw=3, fill=CARD, r=14, mark=True, lines=2):
    """A creative asset: a picture area and a line or two under it."""
    o = [rect(cx-w/2, cy-h/2, w, h, fill=fill, r=r, stroke=stroke, sw=sw)]
    ix, iw = cx-w/2 + w*0.09, w*0.82
    ph = h*0.50
    o.append(rect(ix, cy-h/2 + h*0.08, iw, ph, fill='none', r=r*0.6, stroke=stroke, sw=sw*0.8))
    if mark:
        o.append(circle(ix + iw*0.28, cy-h/2 + h*0.08 + ph*0.40, min(iw, ph)*0.15, fill='none', stroke=stroke, sw=sw*0.8))
        o.append(path('M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (
            ix + iw*0.12, cy-h/2 + h*0.08 + ph*0.86,
            ix + iw*0.46, cy-h/2 + h*0.08 + ph*0.48,
            ix + iw*0.88, cy-h/2 + h*0.08 + ph*0.86), stroke=stroke, sw=sw*0.8))
    for i in range(lines):
        o.append(rect(ix, cy-h/2 + h*0.66 + i*h*0.13, iw*[0.78, 0.5][i % 2], max(9, h*0.045),
                      fill=stroke if i == 0 else HAIR2, r=h*0.024))
    return ''.join(o)

# ── hero · one asset that stops the scroll ───────────────────────────────────
def hero():
    W, H = 1200, 800
    s = SVG(W, H, bg=None)
    # the noise: a column of everything else, muted and uniform
    for i in range(4):
        y = 120 + i * 176
        s.add(rect(96, y, 420, 140, fill=CARD, r=16, stroke=HAIR2, sw=2.6))
        s.add(rect(128, y + 34, 250, 18, fill=HAIR2, r=9))
        s.add(rect(128, y + 68, 180, 14, fill=HAIR, r=7))
    for i in range(4):
        y = 120 + i * 176
        s.add(rect(1000, y, 108, 140, fill=CARD, r=16, stroke=HAIR2, sw=2.6))
        s.add(rect(1022, y + 34, 64, 16, fill=HAIR2, r=8))
    # the one that cuts through
    s.add(frame(760, 400, 380, 560, ACCENT, 4.6, lines=2))
    return s

# ── step 01 · the angle that lands ───────────────────────────────────────────
def angle():
    """Four angles tried on the same subject, and the attention each one pulled."""
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    xs = [230, 470, 710, 950]
    hs = [58, 92, 210, 74]
    win = 2
    base = 700
    for c, cx in enumerate(xs):
        on = c == win
        s.add(frame(cx, 300, 200, 262, ACCENT if on else INK, 3.8 if on else 2.8, lines=1))
    for c, (cx, hgt) in enumerate(zip(xs, hs)):
        on = c == win
        s.add(rect(cx - 50, base - hgt, 100, hgt, fill=ACCENT if on else HAIR2, r=13))
    s.add(line(96, base + 24, 1104, base + 24, INK, 3))
    return s

# ── step 02 · one concept, every format ──────────────────────────────────────
def system():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    s.add(frame(300, 450, 300, 380, INK, 4, lines=2))
    outs = [(820, 220, 200, 200), (820, 640, 300, 180), (1180, 190, 180, 300),
            (1180, 560, 260, 240), (1450, 400, 150, 380)]
    for i, (x, y, w, h) in enumerate(outs):
        last = i == 4
        col = ACCENT if last else INK
        s.add(path(f'M460 450 C580 450 {x - w/2 - 120:.0f} {y:.0f} {x - w/2 - 26:.0f} {y:.0f}',
                   stroke=HAIR2, sw=2.8))
        s.add(frame(x, y, w, h, col, 3.6 if last else 2.8, mark=False, lines=2))
    return s

# ── step 03 · decay, and the refresh that beats it (on graphite) ─────────────
def refresh():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    x0, x1 = 170, 1440
    top, floor = 250, 640
    # three runs: each climbs, decays, and is refreshed before it bottoms out
    seg = (x1 - x0) / 3
    pts = []
    for k in range(3):
        sx = x0 + k * seg
        pts.append((sx, floor - (360 + k * 26)))
        pts.append((sx + seg * 0.80, floor - (110 + k * 62)))
    d = 'M%.0f %.0f' % pts[0]
    for i in range(1, len(pts)):
        px, py = pts[i - 1]
        cx, cy = pts[i]
        if i % 2:                       # the decay inside a run
            d += ' C%.0f %.0f %.0f %.0f %.0f %.0f' % (px + seg*0.30, py + 40, cx - seg*0.24, cy - 60, cx, cy)
        else:                           # the refresh that lifts it again
            d += ' L%.0f %.0f' % (cx, cy)
    s.add(path(d, stroke=ONDARK, sw=5))
    for k in range(1, 3):
        x = x0 + k * seg
        s.add(line(x, top - 40, x, floor + 40, '#3A3A38', 3, dash='13 11'))
        s.add(circle(x, floor - (360 + k * 26), 19, fill=ACCENT))
    s.add(line(x0 - 20, floor + 66, x1 + 20, floor + 66, '#3A3A38', 3))
    return s

if __name__ == '__main__':
    save(hero(), 'cr-hero')
    save(angle(), 'cr-angle')
    save(system(), 'cr-system')
    save(refresh(), 'cr-refresh')
