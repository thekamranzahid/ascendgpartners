"""AI Solutions — the four drawings the page needs.

House style: flat vector, hairlines, one accent that marks the outcome.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from dsl import *

OUT = 'outai'
CARD = '#FBFBF9'
DARKLINE = '#4A4A47'

def save(s, name):
    n = s.save(f'{OUT}/{name}.svg'); print(f'{n/1024:6.1f}KB  {name}.svg')

def doc(cx, cy, w, h, stroke=INK, sw=3, fill=CARD, r=14, lines=3, tick=False):
    """A unit of work: a card with a few lines of content in it."""
    o = [rect(cx-w/2, cy-h/2, w, h, fill=fill, r=r, stroke=stroke, sw=sw)]
    ix, iw = cx-w/2 + w*0.12, w*0.76
    for i in range(lines):
        o.append(rect(ix, cy-h/2 + h*0.24 + i*h*0.20, iw*[1.0, 0.72, 0.86][i % 3],
                      max(7, h*0.070), fill=HAIR2 if i else stroke, r=h*0.035))
    if tick:
        o.append(check(cx + w*0.28, cy + h*0.30, w*0.10, stroke, sw*0.9))
    return ''.join(o)

# ── hero · one brief in, the work of a team out ──────────────────────────────
def hero():
    W, H = 1200, 800
    s = SVG(W, H, bg=None)
    # the request, once
    s.add(doc(210, 400, 230, 300, INK, 3.6, lines=3))
    # the spine that carries it, and the bracket that splits it
    bx, top, bot = 430, 200, 600
    s.add(line(325, 400, bx, 400, INK, 3))
    s.add(line(bx, top, bx, bot, INK, 3))
    # the work that comes back, nine times
    cols, rows = 3, 3
    for r_ in range(rows):
        y = top + r_ * ((bot - top) / (rows - 1))
        s.add(line(bx, y, 560, y, INK, 2.6))
        for c in range(cols):
            x = 640 + c * 190
            last = (r_ == rows - 1 and c == cols - 1)
            col = ACCENT if last else INK
            s.add(doc(x, y, 160, 118, col, 3.2 if last else 2.4, lines=2, tick=True))
    return s

# ── step 01 · the work that drains the most time ─────────────────────────────
def drain():
    """Five workflows, ranked by the hours they take. The worst one first."""
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    lens = [430, 330, 250, 180, 120]
    steps = [5, 4, 5, 3, 4]
    for i, (ln, n) in enumerate(zip(lens, steps)):
        y = 190 + i * 118
        # the workflow itself: a run of steps on a line
        x0 = 110
        s.add(line(x0, y, x0 + (n - 1) * 62, y, HAIR2, 2.6))
        for k in range(n):
            s.add(circle(x0 + k * 62, y, 13, fill=CARD, stroke=INK, sw=3))
        # and what it costs
        s.add(rect(600, y - 17, ln, 34, fill=ACCENT if i == 0 else HAIR2, r=17))
    s.add(line(600, 118, 600, 690, HAIR2, 2.6))
    return s

# ── step 02 · the AI laid into the workflow already running ──────────────────
def build():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    lane = 340
    xs = [290, 545, 800, 1055, 1310]
    s.add(line(170, lane, 1430, lane, INK, 3))
    # the layer that joins underneath, and the points where it touches
    s.add(rect(230, 690, 1140, 86, fill=ACCENT, r=43))
    for x in [418, 673, 928, 1183]:
        s.add(line(x, 690, x, lane, ACCENT, 4))
        s.add(circle(x, lane, 12, fill=ACCENT))
    # the tools the team already uses
    for x in xs:
        s.add(doc(x, lane, 196, 200, INK, 3.4, lines=3))
    return s

# ── step 03 · output climbing, and the team climbing with it (on graphite) ───
def adopt():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    n = 8
    x0, dx = 210, 168
    used = [1, 2, 2, 3, 3, 4, 4, 5]
    base, step = 700, 48
    for c in range(n):
        x = x0 + c * dx
        last = c == n - 1
        for k in range(5):
            y = base - k * step
            on = k < used[c]
            if on:
                s.add(circle(x, y, 13, fill=ACCENT if last else ONDARK))
            else:
                s.add(circle(x, y, 13, fill='none', stroke=DARKLINE, sw=2.6))
    # the output the adoption bought
    top, low = 180, 400
    pts = [(x0 + c * dx, low - (used[c] - 1) * (low - top) / 4) for c in range(n)]
    d = 'M%.0f %.0f' % pts[0]
    for i in range(1, n):
        px, py = pts[i-1]; cx, cy = pts[i]
        d += ' C%.0f %.0f %.0f %.0f %.0f %.0f' % (px + dx*0.45, py, cx - dx*0.45, cy, cx, cy)
    s.add(path(d, stroke=ONDARK, sw=5))
    s.add(circle(*pts[-1], 19, fill=ACCENT))
    s.add(line(x0 - 60, base + 62, x0 + (n-1)*dx + 60, base + 62, DARKLINE, 3))
    return s

if __name__ == '__main__':
    save(hero(), 'ai-hero')
    save(drain(), 'ai-drain')
    save(build(), 'ai-build')
    save(adopt(), 'ai-adopt')
