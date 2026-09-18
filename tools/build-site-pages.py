"""Build the company, blog, contact, legal and services-index pages.

Copy comes from tools/site-copy.json verbatim; this file only lays it out.
The header, footer and cursor are lifted from a built service page and
re-based for each page's depth, so every page carries the same chrome.
Run:  python3 tools/build-site-pages.py
"""
import json, os, re, html, posixpath, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seo_head import head as seo_head

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = json.load(open(os.path.join(ROOT, 'tools/site-copy.json'), encoding='utf-8'))
SVC = json.load(open(os.path.join(ROOT, 'tools/service-copy.json'), encoding='utf-8'))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('svcgen', os.path.join(ROOT, 'tools/build-service-pages.py'))
_svcgen = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_svcgen)
ART = _svcgen.ART                       # which drawing opens each service page
E = lambda s: html.escape(s, quote=False)
A = lambda s: html.escape(s, quote=True)
BRAND = 'Ascend Growth Partners'
CANON = 'https://ascendgpartners.com'

# ---------- chrome ----------
_src = open(os.path.join(ROOT, 'services/seo/index.html'), encoding='utf-8').read()
NAV = _src[_src.index('<!-- CUSTOM CURSOR -->'):_src.index('<main')]
FOOT = _src[_src.index('</main>') + len('</main>'):_src.index('<script src="https://cdnjs')]
CHROME_DIR = '/services/seo/'

def rebase(h, from_dir, to_dir):
    """Every address is root-relative and slash-free, as on the production site,
       so the chrome is the same string on every page."""
    def fix(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if url == '' or re.match(r'^(https?:|mailto:|tel:|#|data:|javascript:|//)', url): return m.group(0)
        p = posixpath.normpath(posixpath.join(from_dir, url))
        if url.endswith('/') and not p.endswith('/'): p += '/'
        if p != '/' and p.endswith('/'): p = p[:-1]
        return '%s=%s%s%s' % (attr, q, p, q)
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix, h)

# ---------- page shell ----------
def shell(path_dir, d, body, kind='WebPage', extra_ld=None, og_image=None):
    """path_dir is the directory the page is written to, e.g. '/company/about/'.
       Its address, and the record its head comes from, is the same without the slash."""
    path = path_dir if path_dir == '/' else path_dir.rstrip('/')
    extra = ('<link rel="stylesheet" href="/assets/css/motion.css">\n'
             '<script>document.documentElement.classList.add("mo")</script>')
    head = seo_head(path, ['/assets/css/styles.css', '/assets/css/case-studies.css', '/assets/css/pages.css'], extra)
    head += '<body class="cs-page paper-page">\n<div class="mo-curtain" aria-hidden="true"></div>\n'
    scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>\n'
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>\n'
               '<script src="/assets/js/case-studies.js"></script>\n'
               '<script src="/assets/js/motion.js"></script>\n'
               '<script src="/assets/js/service-page.js"></script>\n'
               '<script src="/assets/js/forms.js" data-root="/"></script>\n</body>\n</html>\n')
    nav = rebase(NAV, CHROME_DIR, path_dir); foot = rebase(FOOT, CHROME_DIR, path_dir)
    return head + nav + '\n<main class="pg">\n' + body + '\n</main>\n' + foot + scripts

def crumbs(path_dir, d):
    parts = [p for p in path_dir.split('/') if p]
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": CANON + '/'}]
    names = {'company': 'Company', 'services': 'Services', 'blog': 'Blog'}
    acc = ''
    for i, p in enumerate(parts):
        acc += '/' + p
        last = i == len(parts) - 1
        items.append({"@type": "ListItem", "position": i + 2, "name": d.get('crumb', d['title'].split(' | ')[0]) if last else names.get(p, p.title()), "item": CANON + acc})
    return items

def final(root):
    # the production pages this closes have no closing heading, so the line is a paragraph
    return ('\n<section class="pg-final" aria-label="Ready?">\n  <div class="pg-in">\n    <div class="rv">\n'
            '      <span class="pg-label is-accent">Ready?</span>\n'
            '      <p class="pg-h" id="pgReady">Let’s build the system that grows with you.</p>\n'
            '      <a class="pg-btn" href="/contact">Work With Us <span aria-hidden="true">&#8594;</span></a>\n'
            '    </div>\n  </div>\n</section>\n')

def rows(items, key_t='t', key_d='d'):
    return '<div class="pg-rows">' + ''.join(
        '<div class="pg-row rv" data-rv="%d"><b>%02d</b><h3>%s</h3><p>%s</p></div>' % (i * 60, i + 1, E(x[key_t]), E(x[key_d]))
        for i, x in enumerate(items)) + '</div>'

def write(path_dir, doc):
    out = os.path.join(ROOT, path_dir.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(doc)
    print('%-42s %6d chars' % (path_dir, len(doc)))

# ---------- inline text (from the post extraction) ----------
LOCAL_PATHS = set()

def inline(text, page_dir):
    """**bold**, *em* and [text](url) → HTML; site links become relative when the page exists here."""
    t = E(text)
    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(CANON): url = url[len(CANON):] or '/'
        if url.startswith('/'):
            path = url if url.endswith('/') else url + '/'
            if path in LOCAL_PATHS:
                return '<a href="%s">%s</a>' % (path if path == '/' else path.rstrip('/'), label)
            # a post the production site never published: the sentence keeps its
            # words, but there is nothing honest to point them at
            if path.startswith('/blog/'): return label
            url = CANON + url
        return '<a href="%s"%s>%s</a>' % (url, ' rel="noopener" target="_blank"' if url.startswith('http') else '', label)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)\*(?!\*)', r'<em>\1</em>', t)
    return t

# ============================================================
# services index
# ============================================================
def build_services():
    d = SITE['services']; root = '../'
    groups = ''
    n = 0
    for g in d['groups']:
        entries = ''
        for it in g['items']:
            n += 1
            folder, hero_img, chap_imgs = ART[it['slug']][0], ART[it['slug']][1], ART[it['slug']][2]
            preview = ' data-preview="/uploads/%s/%s.svg"' % (folder, hero_img or chap_imgs[0])
            entries += ('<li><a class="pg-entry" href="/services/%s"%s data-title="%s"><b>%02d</b><div><h3>%s</h3><p>%s</p></div>'
                        '<span class="pg-entry-arrow" aria-hidden="true">&#8594;</span></a></li>') % (it['slug'], preview, E(it['name']), n, E(it['name']), E(it['h1']))
        groups += ('<div class="pg-group rv"><div class="pg-group-name"><h2 class="pg-label">%s</h2></div>'
                   '<ol class="pg-entries">%s</ol></div>') % (E(g['name']), entries)
    body = ('<section class="pg-hero is-split">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">%s</span>\n'
            '    <h1 class="pg-h is-xl">Twelve practices.<br>One growth system.</h1>\n'
            '    <p class="pg-lede">%s</p>\n  </div>\n</section>\n'
            '<section class="pg-index" aria-label="All services">\n  <div class="pg-in">%s</div>\n</section>\n') % (E(d['eyebrow']), E(d['lede']), groups) + final(root)
    write('/services/', shell('/services/', dict(d, crumb='Services'), body, kind='CollectionPage'))

# ============================================================
# about
# ============================================================
def build_about():
    d = SITE['about']; root = '../../'
    people = ''.join(
        '<figure class="pg-person rv" data-rv="%d"><img class="pg-portrait" src="%s" srcset="/uploads/team/%s.webp 960w" sizes="(max-width: 720px) 92vw, 40vw" alt="%s" width="960" height="1200" loading="lazy" decoding="async">'
        '<figcaption><h3>%s</h3><span>%s</span></figcaption></figure>' % (i * 80, A(p['src']), p['img'], E(p['name']), E(p['name']), E(p['role']))
        for i, p in enumerate(d['people']))
    story = ''.join('<p>%s</p>' % E(p) for p in d['story'])
    body = ('<section class="pg-hero is-split">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">%s</span>\n    <h1 class="pg-h is-xl">%s</h1>\n'
            '    <p class="pg-lede">%s</p>\n  </div>\n</section>\n'
            '<section class="pg-team" aria-labelledby="pgTeam">\n  <div class="pg-in">\n'
            '    <div class="rv"><span class="pg-label">%s</span><h2 class="pg-h is-md" id="pgTeam">%s</h2></div>\n'
            '    <div class="pg-team-grid">%s</div>\n  </div>\n</section>\n'
            '<section class="pg-mv" aria-labelledby="pgMv">\n  <div class="pg-in pg-grid rv">\n'
            '    <h2 class="pg-label" id="pgMv">%s</h2>\n'
            '    <div class="pg-statement"><span class="pg-statement-k">Mission</span><p>%s</p></div>\n'
            '    <div class="pg-statement"><span class="pg-statement-k">Vision</span><p>%s</p></div>\n  </div>\n</section>\n'
            '<section class="pg-story" aria-labelledby="pgStory">\n  <div class="pg-in pg-grid">\n'
            '    <span class="pg-label rv">%s</span>\n    <h2 class="pg-h rv" id="pgStory">%s</h2>\n'
            '    <div class="pg-story-body rv" data-rv="80">%s</div>\n  </div>\n</section>\n'
            '<section class="pg-values" aria-labelledby="pgValues">\n  <div class="pg-in">\n'
            '    <h2 class="pg-h is-md rv" id="pgValues">%s</h2>\n    %s\n  </div>\n</section>\n'
            '<section class="pg-diff" aria-labelledby="pgDiff">\n  <div class="pg-in">\n'
            '    <div class="rv"><span class="pg-label is-accent">%s</span><h2 class="pg-h is-md" id="pgDiff">%s</h2></div>\n    %s\n  </div>\n</section>\n') % (
        E(d['eyebrow']), E(d['h1']), E(d['team_text']),
        E(d['team_label']), E(d['team_h2']), people,
        E(d['mv_h2']), E(d['mission']), E(d['vision']),
        E(d['story_label']), E(d['story_h2']), story,
        E(d['values_h2']), rows(d['values']),
        E(d['diff_label']), E(d['diff_h2']), rows(d['diff'])) + final(root)
    ld = [{"@type": "Organization", "name": BRAND, "url": CANON + '/',
           "member": [{"@type": "Person", "name": p['name'], "jobTitle": p['role']} for p in d['people']]}]
    write('/company/about/', shell('/company/about/', dict(d, crumb='About'), body, kind='AboutPage', extra_ld=ld))

# ============================================================
# reviews
# ============================================================
def build_reviews():
    d = SITE['reviews']; root = '../../'
    items = ''.join(
        '<li class="pg-review rv"><figure><blockquote><p>%s</p></blockquote>'
        '<figcaption><strong>%s</strong><span>%s, %s</span></figcaption></figure></li>'
        % (E(r['quote']), E(r['name']), E(r['role']), E(r['company'])) for r in d['reviews'])
    body = ('<section class="pg-hero is-split">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">%s</span>\n'
            '    <h1 class="pg-h is-xl">Real Clients.<br>Real People.<br><span class="pg-serif">Real Reviews.</span></h1>\n'
            '    <p class="pg-lede">%s</p>\n  </div>\n</section>\n'
            '<section class="pg-ledger" aria-label="Client reviews">\n  <div class="pg-in"><ol class="pg-reviews">%s</ol></div>\n</section>\n') % (
        E(d['eyebrow']), E(d['intro']), items) + final(root)
    write('/company/reviews/', shell('/company/reviews/', dict(d, crumb='Reviews'), body))

# ============================================================
# press
# ============================================================
def build_press():
    d = SITE['press']; root = '../../'
    items = ''.join(
        '<article class="pg-press-item rv"><div class="pg-press-meta"><strong>%s</strong><time datetime="%s">%s</time>'
        '<a class="pg-press-fig" href="%s" rel="noopener" target="_blank"><img src="%s" alt="%s" loading="lazy" decoding="async" onerror="this.parentNode.hidden=true"></a></div>'
        '<div><h3><a href="%s" rel="noopener" target="_blank">%s</a></h3><p>%s</p>'
        '<a class="pg-link is-ext" href="%s" rel="noopener" target="_blank">Read it at %s</a></div></article>'
        % (E(it['outlet']), iso(it['date']), E(it['date']), it['url'], A(it['image']), A(it['image_alt']), it['url'], E(it['headline']), E(it['excerpt']), it['url'], E(it['outlet'])) for it in d['items'])
    body = ('<section class="pg-hero">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">%s</span>\n    <h1 class="pg-h is-xl">%s</h1>\n  </div>\n</section>\n'
            '<section class="pg-press" aria-label="Coverage">\n  <div class="pg-in">\n    %s\n'
            '    <div class="pg-press-more rv"><span class="pg-label">Press inquiries</span><div>'
            '<p>Working on a story? Write to <a class="pg-link" href="mailto:%s">%s</a>.</p>'
            '<p>For the work behind the coverage, see <a class="pg-link" href="/services/press-pr">our Press &amp; PR practice</a> and the <a class="pg-link" href="/case-studies">case studies</a>.</p>'
            '</div></div>\n  </div>\n</section>\n') % (
        E(d['eyebrow']), E(d['h1']), items, d['inquiries_email'], d['inquiries_email']) + final(root)
    write('/company/press/', shell('/company/press/', dict(d, crumb='Press'), body))

MONTHS = {m: i + 1 for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])}
def iso(date_text):
    m = re.match(r'(\w+) (\d+), (\d{4})', date_text)
    return '%s-%02d-%02d' % (m.group(3), MONTHS[m.group(1)], int(m.group(2))) if m else ''

# ============================================================
# blog
# ============================================================
def post_meta(p, root):
    return ('<div class="pg-post-meta"><span class="pg-cat">%s</span><time datetime="%s">%s</time></div>'
            % (E(p['category']), iso(p['date']), E(p['date'])))

def build_blog():
    d = SITE['blog']; root = '../'
    cats = ['All'] + sorted({p['category'] for p in d['posts']}, key=lambda c: [p['category'] for p in d['posts']].index(c))
    chips = ''.join('<li><button type="button" class="pg-chip" data-filter="%s" aria-pressed="%s">%s</button></li>'
                    % (E(c), 'true' if c == 'All' else 'false', E(c)) for c in cats)
    feat = next(p for p in d['posts'] if p['slug'] == d['featured'])
    featured = ('<a class="pg-featured-link rv" href="/blog/%s" data-title="Blog">%s<div class="pg-featured-body">%s<h3>%s</h3><p>%s</p>'
                '<span class="pg-read">Read the post <span aria-hidden="true">&#8594;</span></span></div></a>'
                % (feat['slug'], post_meta(feat, root), post_img(feat, 'pg-featured-img'), E(feat['title']), E(d['featured_excerpt'])))
    posts = ''.join(
        '<li data-cat="%s"><a class="pg-post-link rv" href="/blog/%s" data-title="Blog">%s<div class="pg-post-body"><h3>%s</h3><p>%s</p></div>%s</a></li>'
        % (E(p['category']), p['slug'], post_meta(p, root), E(p['title']), E(p['desc']), post_img(p, 'pg-post-thumb')) for p in d['posts'])
    body = ('<section class="pg-hero">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">Blog</span>\n    <h1 class="pg-h is-xl">%s</h1>\n'
            '    <ul class="pg-filters" aria-label="Filter posts by category">%s</ul>\n  </div>\n</section>\n'
            '<section class="pg-featured" aria-labelledby="pgFeat">\n  <div class="pg-in"><h2 class="pg-label rv" id="pgFeat">Featured Post</h2>%s</div>\n</section>\n'
            '<section class="pg-all" aria-labelledby="pgAll">\n  <div class="pg-in"><h2 class="pg-label rv" id="pgAll">All Posts</h2>'
            '<ol class="pg-posts" id="pgPosts">%s</ol><p class="pg-empty" id="pgEmpty" hidden>No posts in this category yet.</p></div>\n</section>\n') % (
        E(d['h1']), chips, featured, posts) + final(root)
    script = ('<script>(function(){var chips=document.querySelectorAll(".pg-chip"),rows=document.querySelectorAll("#pgPosts li"),empty=document.getElementById("pgEmpty");'
              'chips.forEach(function(c){c.addEventListener("click",function(){var f=c.getAttribute("data-filter"),n=0;'
              'chips.forEach(function(x){x.setAttribute("aria-pressed",x===c?"true":"false")});'
              'rows.forEach(function(r){var on=f==="All"||r.getAttribute("data-cat")===f;r.hidden=!on;if(on)n++});empty.hidden=n>0;});});})();</script>\n')
    doc = shell('/blog/', dict(d, crumb='Blog'), body, kind='Blog')
    doc = doc.replace('</body>', script + '</body>')
    write('/blog/', doc)
    for p in d['posts']:
        build_post(p, d)

IMG_DIMS = {'ai-solutions-for-business': (2500, 1400), 'ascend-growth-partners-ai-pr-agency': (1024, 1024),
            'what-does-a-growth-marketing-agency-do': (1600, 800), 'what-is-an-ai-marketing-agency': (2200, 1238)}
IMG_SMALL = {'ai-solutions-for-business': (800, 1400), 'ascend-growth-partners-ai-pr-agency': (800, 1024),
             'what-does-a-growth-marketing-agency-do': (800, 1400), 'what-is-an-ai-marketing-agency': (800, 1400)}
def srcset_for(slug, src):
    """Production's picture stays the src; phones get width-faithful webp copies of the same picture."""
    a, b = IMG_SMALL[slug]; w, h = IMG_DIMS[slug]
    return ' srcset="/uploads/blog/%s-%d.webp %dw, /uploads/blog/%s-%d.webp %dw, %s %dw"' % (slug, a, a, slug, b, b, A(src), w)

def post_img(p, cls):
    if not p.get('images'): return ''
    i = p['images'][0]; w, h = IMG_DIMS[p['slug']]
    sizes = '(max-width: 720px) 92vw, 40vw' if cls == 'pg-featured-img' else '(max-width: 720px) 92vw, 22vw'
    return '<img class="%s" src="%s"%s sizes="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">' % (cls, A(i['src']), srcset_for(p['slug'], i['src']), sizes, A(i['alt']), w, h)

def render_blocks(blocks, page_dir, date_text, title, images=None, slug=None):
    out = []
    used = 0
    for b in blocks:
        t = b['t']
        if t == 'h1': continue
        if t == 'img':
            # the same pictures the production page shows, at the same addresses, with the same alt
            if images and used < len(images):
                i = images[used]; used += 1
                if used == 1 and slug in IMG_DIMS:
                    w, h = IMG_DIMS[slug]
                    out.append('<figure class="pg-figure"><img src="%s"%s sizes="(max-width: 720px) 92vw, 68ch" alt="%s" width="%d" height="%d" fetchpriority="high" decoding="async"></figure>' % (A(i['src']), srcset_for(slug, i['src']), A(i['alt']), w, h))
                elif 'images.unsplash.com' in i['src']:
                    base = i['src'].split('?')[0]
                    out.append('<figure class="pg-figure"><img src="%s" srcset="%s?q=80&amp;w=800&amp;auto=format&amp;fit=crop 800w, %s?q=80&amp;w=1400&amp;auto=format&amp;fit=crop 1400w, %s 2232w" sizes="(max-width: 720px) 92vw, 68ch" alt="%s" width="2232" height="1255" loading="lazy" decoding="async"></figure>' % (A(i['src']), base, base, A(i['src']), A(i['alt'])))
                else:
                    out.append('<figure class="pg-figure"><img src="%s" alt="%s" loading="lazy" decoding="async"></figure>' % (A(i['src']), A(i['alt'])))
            continue
        if t == 'p' and b['x'].strip() == date_text: continue
        if t == 'p' and b['x'].strip() == title: continue
        # production's closing box is rendered by the page itself, not as article text
        if t == 'h3' and b['x'].strip() == 'Ready to grow?': continue
        if t == 'p' and b['x'].strip() in ("Let's build a growth strategy tailored to your business.", 'Work With Us'): continue
        if t in ('p', 'h2', 'h3', 'h4'):
            out.append('<%s>%s</%s>' % (t, inline(b['x'], page_dir), t))
        elif t in ('ul', 'ol'):
            out.append('<%s>%s</%s>' % (t, ''.join('<li>%s</li>' % inline(i, page_dir) for i in b['items']), t))
        elif t == 'blockquote':
            out.append('<blockquote><p>%s</p></blockquote>' % inline(b['x'], page_dir))
        elif t == 'table' and b['rows']:
            head_r, body_r = b['rows'][0], b['rows'][1:]
            out.append('<div class="pg-table"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
                ''.join('<th>%s</th>' % inline(c, page_dir) for c in head_r),
                ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c, page_dir) for c in r) for r in body_r)))
    return '\n'.join(out)

def build_post(p, d):
    page_dir = '/blog/%s/' % p['slug']; root = '../../'
    others = [q for q in d['posts'] if q['slug'] != p['slug']]
    more = ''.join(
        '<li data-cat="%s"><a class="pg-post-link rv" href="/blog/%s" data-title="Blog">%s<div class="pg-post-body"><h3>%s</h3><p>%s</p></div>%s</a></li>'
        % (E(q['category']), q['slug'], post_meta(q, root), E(q['title']), E(q['desc']), post_img(q, 'pg-post-thumb')) for q in others)
    body = ('<article class="pg-article">\n<section class="pg-hero">\n  <div class="pg-in pg-grid rv">\n'
            '    <a class="pg-back" href="/blog">&#8592; Back to Blog</a>\n'
            '    <h1 class="pg-h">%s</h1>\n'
            '    <div class="pg-article-meta"><span class="pg-cat">%s</span><time datetime="%s">%s</time><span>By %s</span></div>\n  </div>\n</section>\n'
            '<section class="pg-prose-wrap">\n  <div class="pg-in pg-grid"><div class="pg-prose rv">%s'
            '<aside class="pg-post-cta rv"><h3>Ready to grow?</h3><p>Let\'s build a growth strategy tailored to your business.</p>'
            '<a class="pg-btn" href="/contact">Work With Us</a></aside></div></div>\n</section>\n</article>\n') % (
        E(p['title']), E(p['category']), iso(p['date']), E(p['date']), E(d['author']),
        render_blocks(p['blocks'], page_dir, p['date'], p['title'], p.get('images'), p['slug']))
    meta = {'title': '%s | %s' % (p['title'], BRAND), 'desc': p['desc'], 'canonical': CANON + '/blog/' + p['slug'], 'crumb': p['title']}
    ld = [{"@type": "BlogPosting", "headline": p['title'], "datePublished": iso(p['date']), "description": p['desc'],
           "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@type": "Organization", "name": BRAND},
           "mainEntityOfPage": CANON + '/blog/' + p['slug'], "image": CANON + '/uploads/blog/%s.webp' % p['slug']}]
    write(page_dir, shell(page_dir, meta, body, kind='BlogPosting', extra_ld=ld, og_image=root + 'uploads/blog/%s.webp' % p['slug']))

# ============================================================
# contact
# ============================================================
def build_contact():
    d = SITE['contact']; root = '../'; f = d['form']
    fields = ''
    for x in f['fields']:
        req = ' required' if x.get('required') else ''
        lab = '%s%s' % (E(x['label']), ' <em aria-hidden="true">*</em>' if x.get('required') else '')
        fid = 'f-' + x['key']
        full = x['type'] in ('textarea', 'checkboxes', 'select') or x['key'] in ('websiteUrl',)
        cls = 'pg-field' + (' is-full' if full else '')
        if x['type'] == 'textarea':
            fields += '<div class="%s"><label for="%s">%s</label><textarea id="%s" name="%s" rows="4"%s></textarea></div>' % (cls, fid, lab, fid, x['key'], req)
        elif x['type'] == 'select':
            opts = '<option value="" selected disabled>Choose one</option>' + ''.join('<option value="%s">%s</option>' % (E(o), E(o)) for o in x['options'])
            fields += '<div class="%s"><label for="%s">%s</label><select id="%s" name="%s"%s>%s</select></div>' % (cls, fid, lab, fid, x['key'], req, opts)
        elif x['type'] == 'checkboxes':
            boxes = ''.join('<label class="pg-check"><input type="checkbox" name="%s" value="%s"><span>%s</span></label>' % (x['key'], E(o), E(o)) for o in x['options'])
            fields += '<fieldset class="%s"><legend>%s</legend><div class="pg-checks">%s</div></fieldset>' % (cls, lab, boxes)
        else:
            fields += '<div class="%s"><label for="%s">%s</label><input id="%s" name="%s" type="%s" autocomplete="%s"%s%s></div>' % (
                cls, fid, lab, fid, x['key'], x['type'], x.get('auto', 'on'), req, ' inputmode="url"' if x['key'] == 'websiteUrl' else '')
    bullets = ''.join('<li>%s</li>' % E(b) for b in d['bullets'])
    q = d['quote']
    body = ('<section class="pg-contact">\n  <div class="pg-in pg-contact-grid">\n'
            '    <div class="pg-contact-copy rv">\n      <span class="pg-label is-accent">%s</span>\n'
            '      <h1 class="pg-h">Get your <span class="pg-serif">personalized</span> growth plan today.</h1>\n'
            '      <ul class="pg-bullets">%s</ul>\n'
            '      <figure class="pg-contact-quote"><blockquote><p>“%s”</p></blockquote><figcaption><strong>%s</strong><span>%s</span></figcaption></figure>\n'
            '    </div>\n'
            '    <form class="pg-form rv" data-rv="120" data-form-id="%s" data-success="%s" novalidate aria-label="Contact form">\n'
            '      <div class="pg-form-grid">\n        %s\n'
            '        <input class="pg-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">\n'
            '        <div class="pg-form-foot"><button class="pg-btn" type="submit">%s <span aria-hidden="true">&#8594;</span></button>'
            '<p class="pg-form-status" data-form-status role="status" aria-live="polite"></p></div>\n'
            '      </div>\n'
            '      <div class="pg-form-done" data-form-done hidden><p class="pg-h is-md">Sent.</p><p></p>'
            '<a class="pg-link" href="/services">While you wait, see what we do</a></div>\n'
            '    </form>\n'
            '    <p class="pg-contact-alt">Prefer email? <a class="pg-link" href="mailto:%s">%s</a></p>\n'
            '  </div>\n</section>\n') % (
        E(d['eyebrow']), bullets, E(q['text']), E(q['name']), E(q['role']),
        f['id'], E(f['success']), fields, E(f['submit']), d['email'], d['email'])
    write('/contact/', shell('/contact/', dict(d, crumb='Contact'), body, kind='ContactPage'))

# ============================================================
# legal
# ============================================================
def build_legal(key, path_dir, crumb):
    d = SITE[key]; root = '../'
    paras = ''
    for p in d['paras']:
        t = E(p)
        if '[email]' in t: t = t.replace('[email]', '<a class="pg-link" href="mailto:%s">%s</a>' % (d['email'], d['email']))
        paras += '<p>%s</p>' % t
    body = ('<section class="pg-hero">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">%s</span>\n    <h1 class="pg-h is-xl">%s</h1>\n  </div>\n</section>\n'
            '<section class="pg-legal">\n  <div class="pg-in pg-grid"><div class="pg-legal-body rv">%s</div></div>\n</section>\n') % (E(d['eyebrow']), E(d['h1']), paras)
    write(path_dir, shell(path_dir, dict(d, crumb=crumb), body))

# ============================================================
# /services/coming-soon and the 404 page: the production pages, word for word
# ============================================================
def build_coming_soon():
    body = ('<section class="pg-hero pg-soon is-dark">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">Coming Soon</span>\n'
            '    <h1 class="pg-h is-xl">Something great<br><span class="pg-serif">is ascending.</span></h1>\n'
            '    <p class="pg-lede">We’re hard at work crafting something worth the wait. In the meantime, let’s talk about how we can help your business grow.</p>\n'
            '    <div class="pg-soon-actions"><a class="pg-btn is-accent" href="/#contact">Work With Us</a>'
            '<a class="pg-link" href="/">&#8592; Back to Home</a></div>\n  </div>\n</section>\n')
    write('/services/coming-soon/', shell('/services/coming-soon/', {'title': 'Coming Soon', 'desc': '', 'canonical': ''}, body))

def build_404():
    body = ('<section class="pg-hero pg-soon">\n  <div class="pg-in pg-grid rv">\n'
            '    <span class="pg-label is-accent">404</span>\n'
            '    <h1 class="pg-h is-xl">This page could not be found.</h1>\n'
            '    <p class="pg-lede">The address may have changed, or it never existed. Everything we do is one step from here.</p>\n'
            '    <div class="pg-soon-actions"><a class="pg-btn" href="/">Back to Home</a><a class="pg-link" href="/services">See our services</a>'
            '<a class="pg-link" href="/contact">Work with us</a></div>\n  </div>\n</section>\n')
    doc = shell('/404/', {'title': 'Page Not Found', 'desc': '', 'canonical': ''}, body)
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(doc); print('%-42s %6d chars' % ('/404.html', len(doc)))

# ============================================================
# sitemap + robots
# ============================================================
def build_sitemap(paths):
    urls = ''.join('  <url><loc>%s%s</loc></url>\n' % (CANON, p.rstrip('/') or '/') for p in paths)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write('User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: %s/sitemap.xml\n' % CANON)
    print('sitemap.xml: %d urls' % len(paths))

if __name__ == '__main__':
    LOCAL_PATHS.update(['/', '/services/', '/case-studies/', '/blog/', '/contact/', '/company/about/', '/company/reviews/', '/company/press/',
                        '/privacy-policy/', '/terms-of-use/'] + ['/services/%s/' % s for s in SVC] +
                       ['/blog/%s/' % p['slug'] for p in SITE['blog']['posts']] +
                       ['/case-studies/%s/' % c for c in ('bare-knuckle-fc', 'dr-harrison-lee', 'jason-wojo')])
    build_services(); build_about(); build_reviews(); build_press(); build_blog(); build_contact()
    build_legal('privacy-policy', '/privacy-policy/', 'Privacy Policy'); build_legal('terms-of-use', '/terms-of-use/', 'Terms of Use')
    build_coming_soon(); build_404()
    # sitemap.xml and robots.txt are the production site's own files, copied verbatim; nothing generates them
