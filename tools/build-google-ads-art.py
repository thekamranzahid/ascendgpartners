"""Google Ads — the four chapter drawings.

House style throughout: flat vector, hairlines, one accent that marks the
outcome. No third-party marks, wordmarks or brand colours anywhere.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from dsl import *

OUT = 'outga'
CARD = '#FBFBF9'

def save(s, name):
    n = s.save(f'{OUT}/{name}.svg'); print(f'{n/1024:6.1f}KB  {name}.svg')

def arrow(x1, y1, x2, y2, stroke, sw, gap=0):
    d = math.hypot(x2-x1, y2-y1) or 1
    ux, uy = (x2-x1)/d, (y2-y1)/d
    ex, ey = x2-ux*gap, y2-uy*gap
    o = [line(x1, y1, ex, ey, stroke, sw)]
    a = sw*3.2; px, py = -uy, ux
    o.append(path(f'M{ex:.1f} {ey:.1f} L{ex-ux*a+px*a*0.6:.1f} {ey-uy*a+py*a*0.6:.1f} '
                  f'L{ex-ux*a-px*a*0.6:.1f} {ey-uy*a-py*a*0.6:.1f} Z', fill=stroke))
    return ''.join(o)

# ── step 01 · the terms worth paying for ─────────────────────────────────────
def intent():
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    # the query the buyer actually types
    s.add(rect(96, 84, 1008, 96, fill=CARD, r=48, stroke=INK, sw=3.6))
    s.add(circle(160, 132, 22, fill='none', stroke=INK, sw=3.4))
    s.add(line(176, 148, 194, 166, INK, 3.4))
    s.add(rect(228, 120, 430, 24, fill=INK, r=12))
    rows = [(0.86, True), (0.72, True), (0.62, True), (0.16, False), (0.11, False), (0.08, False)]
    y = 262
    for v, keep in rows:
        col = ACCENT if keep else HAIR2
        s.add(rect(96, y - 20, 300, 40, fill=CARD, r=20, stroke=INK if keep else HAIR2, sw=3.2 if keep else 2.6))
        s.add(rect(128, y - 8, 200 if keep else 150, 16, fill=INK if keep else HAIR2, r=8))
        s.add(rect(440, y - 20, 664, 40, fill=HAIR, r=20))
        s.add(rect(440, y - 20, 664 * v, 40, fill=col, r=20))
        if not keep:
            s.add(rect(436, y - 24, 672, 48, fill='none', r=24, stroke=HAIR2, sw=2.6, dash='12 10'))
        y += 88
    return s

# ── step 02 · the measurement stack, rebuilt ─────────────────────────────────
def tracking():
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    nodes = [(220, 'page'), (500, 'server'), (780, 'store'), (1030, 'bid')]
    y = 300
    for i, (x, kind) in enumerate(nodes):
        last = i == 3
        col = ACCENT if last else INK
        if kind == 'page':
            s.add(rect(x-84, y-104, 168, 208, fill=CARD, r=16, stroke=col, sw=3.4))
            for k in range(3):
                s.add(rect(x-52, y-60+k*44, 104 - k*22, 16, fill=HAIR2, r=8))
        elif kind == 'server':
            s.add(rect(x-84, y-104, 168, 208, fill=CARD, r=16, stroke=col, sw=3.4))
            for k in range(3):
                s.add(rect(x-56, y-64+k*46, 112, 30, fill='none', r=8, stroke=INK, sw=2.6))
                s.add(circle(x-38, y-49+k*46, 6, fill=INK))
        elif kind == 'store':
            s.add(rect(x-84, y-104, 168, 208, fill=CARD, r=16, stroke=col, sw=3.4))
            for k in range(4):
                s.add(rect(x-56, y-70+k*40, 112, 22, fill=INK if k < 3 else HAIR2, r=11))
        else:
            s.add(circle(x, y, 92, fill=CARD, stroke=col, sw=4.2))
            s.add(rect(x-40, y-10, 80, 20, fill=col, r=10))
        if i < 3:
            s.add(arrow(x+92, y, nodes[i+1][0]-92, y, INK, 3.4, gap=6))
    # the value that comes back and teaches the bidding
    s.add(path(f'M1030 400 C1030 560 700 620 500 620 C340 620 220 560 220 420',
               stroke=ACCENT, sw=4.5))
    s.add(arrow(240, 460, 220, 412, ACCENT, 4.5, gap=2))
    return s

# ── step 03 · two budgets, separated (on graphite) ───────────────────────────
def scale():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    x0, x1 = 170, 1430
    # before: revenue and waste running together
    y = 300
    s.add(rect(x0, y-46, (x1-x0)*0.42, 92, fill=ACCENT, r=46))
    s.add(rect(x0+(x1-x0)*0.42+10, y-46, (x1-x0)*0.58-10, 92, fill='none', r=46, stroke='#4A4A48', sw=3.4, dash='16 13'))
    # the cut
    cx = x0 + (x1-x0)*0.42 + 6
    s.add(line(cx, y-96, cx, y+96, ONDARK, 3.4, dash='12 10'))
    # after: the same money, all of it working
    y2 = 600
    s.add(rect(x0, y2-46, (x1-x0)*0.72, 92, fill=ACCENT, r=46))
    s.add(rect(x0+(x1-x0)*0.72+10, y2-46, (x1-x0)*0.28-10, 92, fill='none', r=46, stroke='#2E2E2C', sw=3))
    s.add(arrow(cx, 396, x0+(x1-x0)*0.72, 548, ONDARK, 3.4, gap=8))
    return s

# ── the buyers this is built for ─────────────────────────────────────────────
def buyers():
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    specs = [(190, 150, 300, 0), (400, 210, 250, 1), (630, 170, 340, 2), (860, 240, 220, 3), (1060, 130, 280, 4)]
    cy = 400
    for i, (cx, w, h, kind) in enumerate(specs):
        best = i == 2
        col = ACCENT if best else INK
        s.add(rect(cx-w/2, cy-h/2, w, h, fill=CARD, r=18, stroke=col, sw=4 if best else 3))
        ix, iw = cx-w*0.36, w*0.72
        if kind == 0:
            for k in range(3): s.add(rect(ix, cy-h*0.28+k*h*0.16, iw*[1,0.7,0.85][k], 14, fill=col, r=7))
        elif kind == 1:
            s.add(rect(ix, cy-h*0.26, iw, h*0.30, fill='none', r=10, stroke=col, sw=2.8))
            s.add(rect(ix, cy+h*0.14, iw*0.6, 14, fill=col, r=7))
        elif kind == 2:
            s.add(circle(cx, cy-h*0.12, w*0.16, fill='none', stroke=col, sw=3.2))
            s.add(rect(ix, cy+h*0.16, iw, 16, fill=col, r=8))
        elif kind == 3:
            for k in range(4): s.add(rect(ix, cy-h*0.30+k*h*0.17, iw*(1-k*0.18), 12, fill=col if k == 0 else HAIR2, r=6))
        else:
            s.add(rect(ix, cy-h*0.18, iw, h*0.20, fill=col, r=8))
            s.add(rect(ix, cy+h*0.12, iw*0.55, 12, fill=HAIR2, r=6))
    return s

if __name__ == '__main__':
    save(intent(), 'ga-intent')
    save(tracking(), 'ga-tracking')
    save(scale(), 'ga-scale')
    save(buyers(), 'ga-buyers')
