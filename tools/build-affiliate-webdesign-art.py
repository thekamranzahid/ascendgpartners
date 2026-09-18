"""Affiliate Marketing and Web Design — the eight drawings the two pages need.

House style: flat vector, hairlines, one accent that marks the outcome.
Run from the repo root:  python3 tools/build-affiliate-webdesign-art.py
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = '#FBFBF9'
DARKLINE = '#4A4A47'

def save(s, folder, name):
    d = os.path.join(ROOT, 'uploads', folder); os.makedirs(d, exist_ok=True)
    n = s.save(os.path.join(d, name + '.svg')); print('%6.1fKB  %s/%s.svg' % (n / 1024, folder, name))

# ═══ AFFILIATE ═══════════════════════════════════════════════════════════════
# hero · what the existing channels already make, and the slice partners add
def af_hero():
    W, H = 1200, 800
    s = SVG(W, H, bg=None)
    base = 690
    xs = [220, 420, 620, 820]
    hs = [300, 380, 340, 420]
    for x, h in zip(xs, hs):
        s.add(rect(x - 70, base - h, 140, h, fill='none', r=16, stroke=INK, sw=3.2))
    s.add(rect(820 - 70, base - hs[3] - 96, 140, 82, fill=ACCENT, r=16))
    for px, py in [(1030, 160), (1080, 290), (1040, 420)]:
        s.add(curve(px - 18, py, 892, base - hs[3] - 55, bow=0.2, stroke=ACCENT, sw=2.6))
        s.add(circle(px, py, 15, fill=CARD, stroke=ACCENT, sw=3.4))
    s.add(line(120, base + 30, 1080, base + 30, INK, 3))
    return s

# step 01 · three partner tiers, and the margin none of their commissions cross
def af_model():
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    x0 = 150
    tiers = [(1000, 210), (760, 160), (520, 110)]
    for i, (ln, cm) in enumerate(tiers):
        y = 210 + i * 170
        s.add(rect(x0, y - 32, ln, 64, fill='none', r=32, stroke=INK, sw=3))
        s.add(rect(x0 + ln - cm - 10, y - 22, cm, 44, fill=ACCENT if i == 0 else HAIR2, r=22))
    s.add(line(x0 + 1036, 130, x0 + 1036, 640, INK, 3, dash='14 12'))
    return s

# step 02 · partners chosen for fit, and the volume that did not earn a place
def af_recruit():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    xs = [220, 380, 540, 700, 860, 1020, 1180, 1340]
    fit = [0.30, 0.92, 0.42, 0.20, 0.86, 0.35, 0.78, 0.26]
    base = 690
    for x, f in zip(xs, fit):
        on = f > 0.7
        s.add(circle(x, 210, 30, fill=CARD, stroke=ACCENT if on else INK, sw=3.6 if on else 2.8))
        s.add(rect(x - 34, base - 380 * f, 68, 380 * f, fill=ACCENT if on else HAIR2, r=14))
    s.add(line(150, base + 30, 1450, base + 30, INK, 3))
    return s

# step 03 · partner revenue tracked, and the traffic that never counted (graphite)
def af_quality():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    x0, x1, floor = 200, 1400, 620
    lift = [40, 95, 130, 200, 235, 320, 360, 430]
    pts = [(x0 + k * (x1 - x0) / 7, floor - lift[k]) for k in range(8)]
    d = 'M%.0f %.0f' % pts[0]
    for (px, py), (cx, cy) in zip(pts, pts[1:]):
        d += ' C%.0f %.0f %.0f %.0f %.0f %.0f' % (px + 70, py, cx - 70, cy, cx, cy)
    s.add(path(d, stroke=ONDARK, sw=5))
    for x, y in pts[:-1]:
        s.add(circle(x, y, 11, fill=GRAPH, stroke=ONDARK, sw=3))
    s.add(circle(pts[-1][0], pts[-1][1], 19, fill=ACCENT))
    s.add(line(x0 - 40, floor + 60, x1 + 40, floor + 60, DARKLINE, 3))
    for x in [420, 760, 1100]:
        s.add(circle(x, floor + 150, 17, fill='none', stroke=DARKLINE, sw=3))
        s.add(cross(x, floor + 150, 8, DARKLINE, 3))
    return s

# ═══ WEB DESIGN ══════════════════════════════════════════════════════════════
def page_frame(x, y, w, h, stroke=INK, sw=3, fill=CARD, r=18):
    o = [rect(x, y, w, h, fill=fill, r=r, stroke=stroke, sw=sw), line(x, y + 58, x + w, y + 58, stroke, sw * 0.7)]
    for k in range(3): o.append(circle(x + 30 + k * 26, y + 29, 6, fill=stroke))
    return ''.join(o)

# hero · a page whose layout is the argument
def wd_hero():
    W, H = 1200, 800
    s = SVG(W, H, bg=None)
    x, y, w, h = 130, 90, 940, 620
    s.add(page_frame(x, y, w, h))
    gx, gy = x + 70, y + 130
    for c in range(7):
        s.add(line(gx + c * 134, gy - 20, gx + c * 134, y + h - 50, HAIR, 1.6))
    s.add(rect(gx, gy, 470, 46, fill=INK, r=10))
    s.add(rect(gx, gy + 66, 380, 46, fill=INK, r=10))
    s.add(rect(gx, gy + 150, 330, 14, fill=HAIR2, r=7))
    s.add(rect(gx, gy + 180, 280, 14, fill=HAIR2, r=7))
    s.add(rect(gx, gy + 240, 190, 58, fill=ACCENT, r=29))
    s.add(rect(gx + 536, gy - 10, 268, 380, fill='none', r=14, stroke=INK, sw=2.8))
    return s

# step 01 · what a visitor needs to understand, believe, and do, in that order
def wd_journey():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    xs = [180, 520, 860, 1200]
    w, top = 260, 250
    s.add(line(200, 660, 1400, 660, HAIR2, 2.6))
    for i, x in enumerate(xs):
        last = i == 3
        s.add(rect(x, top, w, 300, fill=CARD, r=14, stroke=ACCENT if last else INK, sw=3.4 if last else 2.8))
        if last:
            s.add(rect(x + 50, top + 128, 160, 44, fill=ACCENT, r=22))
        else:
            s.add(rect(x + 34, top + 46, w * [0.62, 0.5, 0.7][i], 20, fill=INK, r=10))
            s.add(rect(x + 34, top + 90, w * 0.42, 12, fill=HAIR2, r=6))
            s.add(rect(x + 34, top + 116, w * 0.55, 12, fill=HAIR2, r=6))
        s.add(circle(x + w / 2, 660, 13, fill=ACCENT if last else CARD, stroke=ACCENT if last else INK, sw=3))
    return s

# step 02 · design, copy, structure and performance landing as one page
def wd_build():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    layers = [(300, 300), (420, 240), (540, 180), (660, 120)]
    for i, (x, y) in enumerate(layers):
        last = i == 3
        col = ACCENT if last else INK
        s.add(page_frame(x, y, 620, 520, stroke=col, sw=3.6 if last else 2.6, fill=CARD if last else PAPER))
        if last:
            s.add(rect(x + 60, y + 110, 330, 40, fill=INK, r=9))
            s.add(rect(x + 60, y + 170, 250, 14, fill=HAIR2, r=7))
            s.add(rect(x + 60, y + 196, 290, 14, fill=HAIR2, r=7))
            s.add(rect(x + 60, y + 250, 170, 52, fill=ACCENT, r=26))
            s.add(rect(x + 380, y + 110, 180, 240, fill='none', r=12, stroke=INK, sw=2.6))
    return s

# step 03 · where attention actually lands, measured after launch (graphite)
def wd_measure():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    x, y, w, h = 400, 90, 800, 700
    s.add(page_frame(x, y, w, h, stroke=ONDARK, sw=3, fill=GRAPH))
    hx, hy = x + 250, y + 470
    cols, rows = 12, 9
    for r_ in range(rows):
        for c in range(cols):
            px = x + 60 + c * ((w - 120) / (cols - 1)); py = y + 110 + r_ * ((h - 170) / (rows - 1))
            dist = math.hypot(px - hx, py - hy)
            if dist < 110: s.add(circle(px, py, 9, fill=ACCENT))
            elif dist < 210: s.add(circle(px, py, 7, fill=ACCENT, opacity=0.45))
            else: s.add(circle(px, py, 5, fill=DARKLINE))
    return s

if __name__ == '__main__':
    save(af_hero(), 'affiliate', 'af-hero'); save(af_model(), 'affiliate', 'af-model')
    save(af_recruit(), 'affiliate', 'af-recruit'); save(af_quality(), 'affiliate', 'af-quality')
    save(wd_hero(), 'webdesign', 'wd-hero'); save(wd_journey(), 'webdesign', 'wd-journey')
    save(wd_build(), 'webdesign', 'wd-build'); save(wd_measure(), 'webdesign', 'wd-measure')
