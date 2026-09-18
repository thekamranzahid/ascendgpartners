"""Rebuild the copy fields of tools/service-copy.json from the production site's
rendered pages, character for character.

tools/services-src/<slug>.html is the rendered <main> of each service page on
ascendgpartners.com (saved by the inventory). Headings keep their <br> and <em>
as HTML in *_html fields; everything else is plain text exactly as rendered.
Layout fields (cta_href, image maps) are left alone.
Run:  python3 tools/extract-service-copy.py
"""
import os, re, json, html, collections
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools/services-src')
COPY = os.path.join(ROOT, 'tools/service-copy.json')

class Node:
    def __init__(self, tag, attrs=None): self.tag, self.attrs, self.kids = tag, dict(attrs or []), []
    def text(self): return ''.join(k if isinstance(k, str) else k.text() for k in self.kids)
    def all(self, tag):
        out = []
        for k in self.kids:
            if isinstance(k, Node):
                if k.tag == tag: out.append(k)
                out += k.all(tag)
        return out
class Tree(HTMLParser):
    VOID = {'img', 'hr', 'br', 'meta', 'link', 'input'}
    def __init__(self): super().__init__(convert_charrefs=True); self.root = Node('root'); self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs); self.stack[-1].kids.append(n)
        if tag not in self.VOID: self.stack.append(n)
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag: del self.stack[i:]; break
    def handle_data(self, d): self.stack[-1].kids.append(d)

def clean(t): return re.sub(r'\s+', ' ', t).strip()
def inner_html(n):
    """Text plus <br> and <em>/<strong> only, as the production heading has them."""
    out = []
    for k in n.kids:
        if isinstance(k, str): out.append(html.escape(k, quote=False))
        elif k.tag == 'br': out.append('<br>')
        elif k.tag in ('em', 'i'): out.append('<em>%s</em>' % inner_html(k))
        elif k.tag in ('strong', 'b'): out.append('<strong>%s</strong>' % inner_html(k))
        else: out.append(inner_html(k))
    return re.sub(r'\s+', ' ', ''.join(out)).strip()

def extract(slug):
    t = Tree(); t.feed(open(os.path.join(SRC, slug + '.html'), encoding='utf-8').read()); root = t.root
    sections = root.all('section')
    hero = sections[0]
    h1 = hero.all('h1')[0]
    ps = hero.all('p')
    label = clean(ps[0].text()); lede = clean(ps[1].text()) if len(ps) > 1 else ''
    cta = [a for a in hero.all('a')][0]
    # the three figures are the last three (value, caption) pairs of the hero
    figs = []
    for d in hero.all('div'):
        spans = [k for k in d.kids if isinstance(k, Node) and k.tag == 'div']
        if len(spans) == 2 and all(len(x.all('span')) == 1 for x in spans) and not d.all('h1'):
            figs.append({'value': clean(spans[0].text()), 'cap': clean(spans[1].text())})
    figs = figs[-3:]
    chapters, lst, faq, list_label, list_h2_html, faq_h2_html, final_h2_html, final_cta = [], [], [], None, None, None, None, None
    for sec in sections[1:]:
        h2s = [h for h in sec.all('h2')]
        arts = sec.all('article')
        p0 = [p for p in sec.all('p')]
        if arts and h2s:                                   # what you get
            list_label = clean(p0[0].text()); list_h2_html = inner_html(h2s[0])
            for a in arts: lst.append({'title': clean(a.all('h3')[0].text()), 'desc': clean(a.all('p')[0].text())})
        elif h2s and p0 and clean(p0[0].text()) == 'FAQ':
            faq_h2_html = inner_html(h2s[0])
            for item in [d for d in sec.all('div') if len(d.all('p')) == 1 and not d.all('h2') and any(clean(x.text()) == '+' for x in d.all('span'))]:
                q = [x for x in item.all('span') if clean(x.text()) not in ('', '+') and not x.all('span')]
                a = item.all('p')
                if q and a: faq.append({'q': clean(q[0].text()), 'a': clean(a[0].text())})
        elif h2s and p0 and clean(p0[0].text()) == 'Ready?':
            final_h2_html = inner_html(h2s[0]); final_cta = clean(sec.all('a')[0].text())
        elif h2s and p0 and sec.all('span') and clean(sec.all('span')[-1].text()).replace('*', '') == clean(p0[0].text()):
            # a chapter: its label opens it and is repeated, decoratively, at its end
            ch = {'label': clean(p0[0].text()), 'h2': clean(h2s[0].text()), 'h2_html': inner_html(h2s[0]),
                  'body': ' '.join(clean(p.text()) for p in sec.all('p')[1:] if clean(p.text()) and clean(p.text()) != clean(p0[0].text()))}
            links = [a for a in sec.all('a') if clean(a.text())]
            if links: ch['link'] = {'text': clean(links[0].text()), 'href': links[0].attrs.get('href', '')}
            chapters.append(ch)
    # de-duplicate faq items that the nested-div walk found twice
    seen, faq2 = set(), []
    for f in faq:
        if f['q'] not in seen: seen.add(f['q']); faq2.append(f)
    h1_text = clean(re.sub(r'<br>', ' ', re.sub(r'</?(em|strong)>', '', inner_html(h1))))   # readable form, for lists elsewhere
    return collections.OrderedDict([('label', label), ('h1', html.unescape(h1_text)), ('h1_html', inner_html(h1)), ('lede', lede), ('cta', clean(cta.text())),
        ('figures', figs), ('chapters', chapters), ('list_label', list_label), ('list_h2_html', list_h2_html), ('list', lst),
        ('faq_h2_html', faq_h2_html), ('faq', faq2), ('final_h2_html', final_h2_html), ('final_cta', final_cta)])

if __name__ == '__main__':
    copy = json.load(open(COPY, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    for slug in copy:
        if not os.path.exists(os.path.join(SRC, slug + '.html')): print('no source for', slug); continue
        ex = extract(slug); old = copy[slug]
        changed = []
        for k, v in ex.items():
            if v in (None, '', []) and k in ('list_label', 'list_h2_html', 'faq_h2_html', 'final_h2_html', 'final_cta'): continue
            if old.get(k) != v: changed.append(k)
            old[k] = v
        print('%-20s h1=%r | chapters %d | list %d | faq %d | changed: %s' % (slug, ex['h1'][:40], len(ex['chapters']), len(ex['list']), len(ex['faq']), changed))
    json.dump(copy, open(COPY, 'w', encoding='utf-8'), indent=1, ensure_ascii=False); open(COPY, 'a').write('\n')
