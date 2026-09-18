"""Build the three case-study pages from the production site's own articles.

tools/case-studies-src/<slug>.html is the rendered <main> of each case study on
ascendgpartners.com, saved verbatim. This script re-typesets that content in the
site's editorial system without changing it: every heading keeps its level,
text and order; every link keeps its destination and anchor text; every image
keeps its address and alt text. The head comes from tools/seo-meta.json.
Run:  python3 tools/build-case-studies.py
"""
import os, re, sys, html, json
from html.parser import HTMLParser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seo_head import head as seo_head

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = 'https://ascendgpartners.com'
A = lambda s: html.escape(s, quote=True)

# the short name on the cover, the chapter number, the date line the index uses,
# and the optimised copies of the production images (as srcset candidates)
COVER = {
  'bare-knuckle-fc':  {'name': 'David Feldman &amp; <em>BKFC</em>', 'num': '01', 'date': 'Jun 7, 2026', 'read': '5 min read'},
  'dr-harrison-lee':  {'name': 'Dr. Harrison <em>Lee</em>', 'num': '02', 'date': 'May 5, 2026', 'read': '5 min read'},
  'jason-wojo':       {'name': 'Jason <em>Wojo</em>', 'num': '03', 'date': 'Feb 27, 2026', 'read': '5 min read'},
}
SRCSET = {
  '/uploads/1780807010051-e0533e87-0227-4f90-909d-e542cbc58ed9-david-feldman.webp': '/uploads/bkfc-david-feldman-800.webp 800w, /uploads/bkfc-david-feldman-1200.webp 1200w, /uploads/bkfc-david-feldman.webp 2400w, /uploads/bkfc-david-feldman-4k.webp 3840w, /uploads/bkfc-david-feldman-8k.webp 7680w',
  '/uploads/1777958907409-dr-harrison-lee-1.png': '/uploads/dr-harrison-lee-1-800.webp 800w, /uploads/dr-harrison-lee-1-1200.webp 1200w, /uploads/dr-harrison-lee-1.webp 2400w, /uploads/dr-harrison-lee-1-4k.webp 3840w, /uploads/dr-harrison-lee-1-8k.webp 7680w',
  '/uploads/1780775065036-dr-harrison-lee-2.png': '/uploads/dr-harrison-lee-2-800.webp 800w, /uploads/dr-harrison-lee-2-1200.webp 1200w, /uploads/dr-harrison-lee-2.webp 2400w, /uploads/dr-harrison-lee-2-4k.webp 3840w, /uploads/dr-harrison-lee-2-8k.webp 7680w',
  '/uploads/1777957397635-wojo-media-cover.jpg': '/uploads/jason-wojo-800.webp 800w, /uploads/jason-wojo-1200.webp 1200w, /uploads/jason-wojo.webp 2400w, /uploads/jason-wojo-4k.webp 3840w, /uploads/jason-wojo-8k.webp 7680w',
}

# ---------- chrome, from a built service page ----------
_src = open(os.path.join(ROOT, 'services/seo/index.html'), encoding='utf-8').read()
NAV = _src[_src.index('<!-- CUSTOM CURSOR -->'):_src.index('<main')]
FOOT = _src[_src.index('</main>') + len('</main>'):_src.index('<script src="https://cdnjs')]

# ---------- a small tree of the production article ----------
class Node:
    def __init__(self, tag, attrs=None):
        self.tag, self.attrs, self.kids = tag, dict(attrs or []), []
    def text(self):
        return ''.join(k if isinstance(k, str) else k.text() for k in self.kids)
    def find_all(self, tag):
        out = []
        for k in self.kids:
            if isinstance(k, Node):
                if k.tag == tag: out.append(k)
                out += k.find_all(tag)
        return out

class Tree(HTMLParser):
    VOID = {'img', 'hr', 'br', 'meta', 'link', 'input'}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.root = Node('root'); self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs); self.stack[-1].kids.append(n)
        if tag not in self.VOID: self.stack.append(n)
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag: del self.stack[i:]; break
    def handle_data(self, data):
        if data: self.stack[-1].kids.append(data)

def href_out(h):
    """Internal destinations root-relative and slash-free, as the site links; everything else untouched."""
    if h.startswith(CANON):
        h = h[len(CANON):] or '/'
    if h.startswith('/') and h != '/' and h.endswith('/'): h = h[:-1]
    return h

def inline(node):
    """Serialise inline content, keeping a, strong, em, br and text exactly."""
    out = []
    for k in node.kids:
        if isinstance(k, str): out.append(html.escape(k, quote=False)); continue
        if k.tag == 'a':
            h = k.attrs.get('href', '#'); ext = h.startswith('http') and not h.startswith(CANON)
            out.append('<a href="%s"%s>%s</a>' % (A(href_out(h)), ' rel="noopener" target="_blank"' if ext else '', inline(k)))
        elif k.tag in ('strong', 'b'): out.append('<strong>%s</strong>' % inline(k))
        elif k.tag in ('em', 'i'): out.append('<em>%s</em>' % inline(k))
        elif k.tag == 'br': out.append('<br>')
        elif k.tag == 'span': out.append(inline(k))
        else: out.append(inline(k))
    return ''.join(out)

def img_tag(node, cls='', eager=False):
    src = node.attrs.get('src', ''); alt = node.attrs.get('alt', '')
    base = src.split('?')[0]
    ss = SRCSET.get(base)
    return '<img%s src="%s"%s alt="%s"%s decoding="async">' % (
        (' class="%s"' % cls) if cls else '', A(src), (' srcset="%s" sizes="(max-width: 1024px) 100vw, 760px"' % ss) if ss else '', A(alt),
        '' if eager else ' loading="lazy"')

# ---------- read one article ----------
def parse(slug):
    t = Tree(); t.feed(open(os.path.join(ROOT, 'tools/case-studies-src', slug + '.html'), encoding='utf-8').read())
    root = t.root
    sections = root.find_all('section')
    hero = sections[0]
    h1 = hero.find_all('h1')[0]
    tags = [s.text().strip() for s in hero.find_all('span') if s.text().strip() and s.text().strip() not in ('',)]
    back = [a for a in hero.find_all('a') if a.attrs.get('href') == '/case-studies'][0]
    # the tag chips are the spans inside the div right after the h1; the client name is the last span
    chips, client = [], None
    for d in hero.find_all('div'):
        spans = [k for k in d.kids if isinstance(k, Node) and k.tag == 'span']
        if spans and all(isinstance(k, Node) and k.tag == 'span' for k in d.kids if isinstance(k, Node)):
            texts = [s.text().strip() for s in spans]
            if not chips: chips = texts
            else: client = texts[0]
    descs = [p for p in hero.find_all('p')]
    desc = inline(descs[0]) if descs else ''
    hero_imgs = hero.find_all('img')
    article = root.find_all('article')[0]
    stats = []
    for d in root.find_all('div'):
        st = [k for k in d.kids if isinstance(k, Node) and k.tag == 'strong']
        sp = [k for k in d.kids if isinstance(k, Node) and k.tag == 'span']
        if len(st) == 1 and len(sp) == 1 and len(d.kids) <= 3: stats.append((st[0].text().strip(), sp[0].text().strip()))
    stats = stats[:3]
    tail = [s for s in sections[1:] if s.find_all('h2')]
    takeaways, more = None, None
    for s in sections:
        h2s = [h for h in s.find_all('h2')]
        if h2s and h2s[0].text().strip() == 'Key Takeaways': takeaways = s
        if h2s and h2s[0].text().strip() == 'More Case Studies': more = s
    return {'h1': inline(h1), 'h1_text': h1.text().strip(), 'chips': chips, 'client': client, 'desc': desc, 'back': back.text().strip(),
            'hero_imgs': hero_imgs, 'article': article, 'stats': stats, 'takeaways': takeaways, 'more': more}

# ---------- write one page ----------
def render(slug):
    d = parse(slug); c = COVER[slug]
    body = []
    body.append('<header class="bk-cover">\n  <div class="bk-wrap">\n    <div class="bk-run">\n      <a href="/case-studies">%s</a>\n      <span>%s</span>\n      %s\n      <span class="spacer"></span>\n      <span>%s &middot; %s</span>\n    </div>' % (
        A(d['back']), c['num'], ''.join('<span class="cs-chip">%s</span>' % A(x) for x in d['chips']), c['date'], c['read']))
    body.append('    <div class="hl-cover-grid">\n      <div>\n        <p class="bk-display">%s</p>\n        <h1 class="bk-deck bk-title rv-words">%s</h1>%s%s\n      </div>\n      <figure class="hl-portrait">%s</figure>\n    </div>' % (
        c['name'], d['h1'], ('\n        <p class="hl-dossier"><span class="hl-cred">%s</span></p>' % A(d['client'])) if d['client'] else '',
        ('\n        <p class="bk-intro">%s</p>' % d['desc']) if d['desc'] else '', img_tag(d['hero_imgs'][0], eager=True) if d['hero_imgs'] else ''))
    if d['stats']:
        body.append('    <div class="bk-tape">' + ''.join('<div><strong><b>%s</b></strong><span>%s</span></div>' % (A(v), A(l)) for v, l in d['stats']) + '</div>')
    body.append('  </div>\n</header>')
    # the article: h2 opens a section, h3 a sub-head, p/ul/em flow inside, hr is a boundary
    secs, cur, n = [], None, 0
    for k in d['article'].kids:
        if isinstance(k, str): continue
        if k.tag == 'h2':
            n += 1; cur = {'n': n, 'h2': inline(k), 'blocks': []}; secs.append(cur)
        elif k.tag == 'hr': continue
        elif cur is not None:
            cur['blocks'].append(k)
        else:
            secs.append({'n': 0, 'h2': None, 'blocks': [k]}); cur = secs[-1]
    out_secs = []
    for s in secs:
        if s['h2'] and s['h2'].strip() == 'Work With Ascend Growth Partners':
            ps = [b for b in s['blocks'] if b.tag == 'p']
            out_secs.append('<section class="bk-cta"><div class="bk-wrap"><div class="cta-card bk-cta-card reveal"><div><h2 class="rv-words">%s</h2>%s</div></div></div></section>' % (
                s['h2'], ''.join('<p class="bk-cta-p">%s</p>' % inline(p) for p in ps)))
            continue
        inner, first = [], True
        for b in s['blocks']:
            if b.tag == 'h3': inner.append('<h3 class="bk-h3 rv-words">%s</h3>' % inline(b)); first = True
            elif b.tag == 'p':
                em_only = len(b.kids) == 1 and isinstance(b.kids[0], Node) and b.kids[0].tag == 'em'
                lead = b.kids and isinstance(b.kids[0], Node) and b.kids[0].tag == 'strong'
                short = len(b.text().strip()) <= 190          # a pull line, not a pull paragraph
                cls = ' class="bk-pull"' if (first and short and not lead and not em_only) else (' class="bk-lead"' if lead else (' class="bk-note"' if em_only else ''))
                inner.append('<p%s>%s</p>' % (cls, inline(b))); first = False
            elif b.tag in ('ul', 'ol'):
                inner.append('<%s class="bk-list">%s</%s>' % (b.tag, ''.join('<li>%s</li>' % inline(li) for li in b.find_all('li')), b.tag))
            elif b.tag == 'img': inner.append('<figure class="bk-fig">%s</figure>' % img_tag(b))
        head = ('<div class="bk-sec-head"><span class="num">%02d</span><h2 class="rv-words">%s</h2></div>' % (s['n'], s['h2'])) if s['h2'] else ''
        out_secs.append('<div class="bk-sec">%s<div class="bk-prose">%s</div></div>' % (head, ''.join(inner)))
    body.append('<section class="bk-deck-cream">\n  <div class="bk-wrap">\n' + '\n'.join(out_secs) + '\n  </div>\n</section>')
    # key takeaways (h2 + h3s), exactly as on production
    if d['takeaways']:
        h3s = d['takeaways'].find_all('h3')
        body.append('<section class="bk-deck-cream bk-takeaways">\n  <div class="bk-wrap"><div class="bk-sec"><div class="bk-sec-head"><span class="num">&#10003;</span><h2 class="rv-words">Key Takeaways</h2></div><div class="hl-rows">%s</div></div></div>\n</section>' % (
            ''.join('<div class="reveal"><span class="num">%02d</span><h3>%s</h3></div>' % (i + 1, inline(h)) for i, h in enumerate(h3s))))
    # more case studies (h2 + cards with h3), exactly as on production
    if d['more']:
        cards = []
        for a in d['more'].find_all('a'):
            img = a.find_all('img'); h3 = a.find_all('h3')
            cards.append('<a class="bk-more-card" href="%s"><figure class="bk-fig bk-more-fig">%s</figure><h3>%s</h3></a>' % (A(href_out(a.attrs.get('href', '/case-studies'))), img_tag(img[0]) if img else '', inline(h3[0]) if h3 else ''))
        body.append('<section class="bk-more">\n  <div class="bk-wrap"><h2 class="bk-more-head">More Case Studies</h2><div class="bk-more-grid">%s</div></div>\n</section>' % ''.join(cards))
    extra = ('<link rel="stylesheet" href="/assets/css/motion.css">\n<script>document.documentElement.classList.add("mo")</script>')
    head = seo_head('/case-studies/' + slug, ['/assets/css/styles.css', '/assets/css/case-studies.css', '/assets/css/study.css'], extra)
    doc = (head + '<body class="cs-page bk-page">\n<div class="mo-curtain" aria-hidden="true"></div>\n' + NAV + '\n<main>\n' + '\n'.join(body) + '\n</main>\n' + FOOT +
           '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>\n'
           '<script src="/assets/js/case-studies.js"></script>\n<script src="/assets/js/motion.js"></script>\n<script src="/assets/js/study.js"></script>\n<script src="/assets/js/forms.js" data-root="/"></script>\n</body>\n</html>\n')
    out = os.path.join(ROOT, 'case-studies', slug, 'index.html')
    open(out, 'w', encoding='utf-8').write(doc)
    heads = re.findall(r'<(h[1-6])\b[^>]*>(.*?)</\1>', doc[doc.index('<main'):doc.index('</main>')], re.S)
    print('%-18s %6d chars | %s' % (slug, len(doc), ' '.join(k for k, _ in heads)))

if __name__ == '__main__':
    for slug in COVER: render(slug)
