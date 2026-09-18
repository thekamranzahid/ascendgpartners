"""Press & PR — the six drawings the page needs.

House style: flat vector, hairlines, one accent that marks the outcome.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from dsl import *

OUT = 'outpr'
CARD = '#FBFBF9'
DARKLINE = '#4A4A47'

def save(s, name):
    n = s.save(f'{OUT}/{name}.svg'); print(f'{n/1024:6.1f}KB  {name}.svg')

def page(cx, cy, w, h, stroke=INK, sw=3, fill=CARD, r=10, rich=True, body=HAIR2):
    """A published page. Rich means it has editorial anatomy; flat means it is
       a press release pretending to be one."""
    o = [rect(cx-w/2, cy-h/2, w, h, fill=fill, r=r, stroke=stroke, sw=sw)]
    ix, iw = cx-w/2 + w*0.10, w*0.80
    y = cy-h/2 + h*0.08
    o.append(line(ix, y, ix+iw, y, body, sw*0.8))
    if rich:
        o.append(rect(ix, y+h*0.05, iw*0.94, h*0.052, fill=stroke, r=h*0.014))
        o.append(rect(ix, y+h*0.125, iw*0.58, h*0.052, fill=stroke, r=h*0.014))
        o.append(rect(ix, y+h*0.235, iw, h*0.235, fill='none', r=h*0.022, stroke=stroke, sw=sw*0.7))
        for c in range(2):
            x0 = ix + c*(iw*0.545)
            for k in range(5):
                o.append(rect(x0, y+h*0.52+k*h*0.048, iw*0.455*[1,.88,.95,.82,.6][k],
                              h*0.017, fill=body, r=h*0.009))
    else:
        for k in range(13):
            o.append(rect(ix, y+h*0.055+k*h*0.058, iw*[1,.94,.97,.9,.98,.92,.96,.88,.99,.93,.95,.9,.62][k],
                          h*0.019, fill=body, r=h*0.01))
    return ''.join(o)

# ── hero · the placement, and the coverage standing behind it ────────────────
def hero():
    W, H = 1200, 800
    s = SVG(W, H, bg=None)
    s.add(page(400, 410, 330, 440, INK, 2.6))
    s.add(page(800, 410, 330, 440, INK, 2.6))
    s.add(page(600, 400, 380, 520, ACCENT, 4.2))
    return s

# ── step 01 · the lanes already taken, and the one left open ─────────────────
def audit():
    """Narrative share across the conversation, and where the space still is."""
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    rows = [[(120, 330), (466, 250), (732, 258)],
            [(120, 214), (350, 396), (762, 228)],
            [(120, 456), (592, 194), (802, 188)],
            [],                                    # the open lane
            [(120, 268), (404, 232), (652, 338)]]
    x0, span = 120, 870
    for i, segs in enumerate(rows):
        y = 180 + i * 118
        s.add(line(x0, y, x0 + span, y, HAIR, 2.4))
        for sx, sw_ in segs:
            s.add(rect(sx, y - 21, sw_, 42, fill=HAIR2, r=21))
        if not segs:
            s.add(rect(x0, y - 25, span, 50, fill='none', r=25, stroke=ACCENT, sw=4, dash='16 13'))
    return s

# ── step 02 · one message, said the same way everywhere ──────────────────────
def readiness():
    W, H = 1200, 800
    s = SVG(W, H, bg=PAPER)
    s.add(rect(390, 130, 420, 74, fill=ACCENT, r=37))
    bx, top, bot = 600, 236, 300
    s.add(line(bx, 204, bx, top, INK, 3))
    xs = [235, 465, 695, 925]
    s.add(line(xs[0], top, xs[-1], top, INK, 3))
    for x in xs:
        s.add(line(x, top, x, bot, INK, 3))
        s.add(rect(x - 100, bot, 200, 300, fill=CARD, r=16, stroke=INK, sw=3))
        s.add(rect(x - 74, bot + 52, 148, 30, fill=ACCENT, r=15))
        for k in range(3):
            s.add(rect(x - 74, bot + 118 + k*40, 148*[1, .82, .55][k], 20, fill=HAIR2, r=10))
    return s

# ── step 03 · a release, and a story (on graphite) ───────────────────────────
def story():
    W, H = 1600, 900
    s = SVG(W, H, bg=GRAPH)
    s.add(page(500, 450, 420, 620, '#6A6A65', 3, fill=GRAPH, rich=False, body='#5E5E59'))
    s.add(page(1080, 450, 460, 660, ACCENT, 4.4, fill=GRAPH, rich=True, body=ONDARK))
    return s

# ── step 04 · the cycle forecast, and the moment built into it ───────────────
def moment():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    base = 690
    hs = [120, 210, 165, 300, 190, 250, 135, 225, 170]
    x0, dx, bw = 190, 152, 84
    for i, h in enumerate(hs):
        x = x0 + i * dx
        s.add(rect(x - bw/2, base - h, bw, h, fill=HAIR2, r=14))
    # the one we build, placed ahead of the peak we saw coming
    xi = x0 + 5 * dx
    s.add(rect(xi - bw/2, base - 430, bw, 430, fill=ACCENT, r=14))
    s.add(line(xi, 150, xi, base + 34, ACCENT, 3, dash='14 12'))
    s.add(circle(xi, 150, 17, fill=ACCENT))
    s.add(line(130, base + 34, x0 + 8 * dx + 70, base + 34, INK, 3))
    return s

# ── why · the same ground, covered sooner ────────────────────────────────────
def speed():
    W, H = 1600, 900
    s = SVG(W, H, bg=PAPER)
    x0, full = 200, 1180
    for y, n, span, col, sw_, node in [(330, 9, full, INK3, 3, INK3),
                                       (620, 4, 470, ACCENT, 4.4, ACCENT)]:
        s.add(line(x0, y, x0 + full, y, HAIR, 2.6))
        s.add(line(x0, y, x0 + span, y, col, sw_))
        for k in range(n):
            s.add(circle(x0 + k * (span / (n - 1)), y, 15, fill=CARD, stroke=node, sw=sw_))
        s.add(circle(x0 + span, y, 26, fill=col))
    # how much of the run the second lane never needed
    s.add(line(x0 + 470, 214, x0 + 470, 620, ACCENT, 3, dash='14 12'))
    s.add(line(x0, 256, x0, 694, INK, 3))
    return s

if __name__ == '__main__':
    save(hero(), 'pr-hero')
    save(audit(), 'pr-audit')
    save(readiness(), 'pr-readiness')
    save(story(), 'pr-story')
    save(moment(), 'pr-moment')
    save(speed(), 'pr-speed')
