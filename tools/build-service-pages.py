"""Build the five Ascend service pages on the quiet system.

One image per chapter, one reveal, one turn from paper to graphite.
Copy is passed in verbatim; this file only lays it out.
Run:  python3 tools/build-service-pages.py
"""
import json, os, re, html, posixpath, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seo_head import head as seo_head

def rootify(h, from_dir):
    """Every href/src becomes root-relative, and page addresses lose their
       trailing slash, which is the form the production site links with."""
    def fix(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if url == '' or re.match(r'^(https?:|mailto:|tel:|#|data:|javascript:|//)', url): return m.group(0)
        p = posixpath.normpath(posixpath.join(from_dir, url))
        if url.endswith('/') and not p.endswith('/'): p += '/'
        if p != '/' and p.endswith('/'): p = p[:-1]
        return '%s=%s%s%s' % (attr, q, p, q)
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix, h)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = json.load(open(os.environ.get('COPY_JSON', os.path.join(ROOT, 'tools/service-copy.json')), encoding='utf-8'))

# slug -> (image folder, hero image, [chapter images], index of the dark chapter)
ART = {
 'seo':              ('index',   'hero-active',  ['tech-aligned', 'content-organized', 'authority-connected'], 2),
 'link-building':    ('link',    'lb-hero-3',    ['lb-gap-2', 'lb-field-3', 'lb-earned-2'], 2),
 'geo':              ('geo',     'geo-hero-3',   ['geo-vis-2', 'geo-field-3', 'geo-attrib-2'], 2),
 'content-creation': ('content', 'cc-hero-3',    ['cc-demand-2', 'cc-field-3', 'cc-pipe-2'], 2),
 'email-marketing':  ('email',   'em-hero-3',    ['em-rev-2', 'em-field-3', 'em-sms', 'em-creators'], 2),
 'paid-social':      ('social',  'ps-hero',      ['ps-creative', 'ps-funnel', 'ps-scale'], 2),
 'google-ads':       ('ads',     None,           ['ga-intent', 'ga-tracking', 'ga-scale', 'ga-buyers'], 2),
 'creative':         ('creative','cr-hero',      ['cr-angle', 'cr-system', 'cr-refresh'], 2),
 'ai-solutions':     ('ai',      'ai-hero',      ['ai-drain', 'ai-build', 'ai-adopt'], 2),
 'press-pr':         ('pr',      'pr-hero',      ['pr-audit', 'pr-readiness', 'pr-story', 'pr-moment', 'pr-speed'], 2),
 'affiliate-marketing': ('affiliate', 'af-hero',  ['af-model', 'af-recruit', 'af-quality'], 2),
 'web-design':       ('webdesign', 'wd-hero',    ['wd-journey', 'wd-build', 'wd-measure'], 2),
}
ALT = {
 'hero-active': 'The index complete: every layer aligned and the strongest at the top',
 'tech-aligned': 'A site’s infrastructure layers in alignment, every route open',
 'content-organized': 'Four clusters of supporting pages feeding one pillar page',
 'authority-connected': 'Links earned from outside publications arriving at one site',
 'lb-hero-3': 'A site connected to the publications that have linked to it',
 'lb-gap-2': 'A backlink profile measured against the authority the same rankings demand',
 'lb-field-3': 'Research resolved into one asset a publication would want to cite',
 'lb-earned-2': 'Pitches going out, and the links that came back',
 'geo-hero-3': 'A generated answer citing the brand as its first source',
 'geo-vis-2': 'A page a model reads as one resolved entity',
 'geo-field-3': 'The finite set of sources a model trusts, with the brand inside it',
 'geo-attrib-2': 'Answer engine sessions stitched through to revenue',
 'cc-hero-3': 'Published pieces whose value keeps compounding',
 'cc-demand-2': 'Demand measured and ranked before a word is written',
 'cc-field-3': 'Pieces organised into lanes across the buyer journey around one pillar',
 'cc-pipe-2': 'Five pieces, each with a job, feeding one pipeline',
 'em-hero-3': 'A message composed, sent, and landing at the top of the inbox',
 'em-rev-2': 'Sends measured by the revenue each one produced',
 'em-field-3': 'One list resolved into segments, each receiving its own message',
 'em-sms': 'A month of email, and the two moments that earned a text',
 'em-creators': 'An issue landing on the same day, and the list it builds',
 'ps-hero': 'One ad unit, and the return it produced',
 'ps-creative': 'Five variants of the same ad, and the one that carried',
 'ps-funnel': 'Prospecting, retargeting and retention, each speaking to a smaller audience',
 'ps-scale': 'Spend climbing while efficiency is held level, with creative refreshed along the way',
 'ga-intent': 'The purchase-intent terms funded, and the broad ones cut',
 'ga-tracking': 'A page, a server, a conversion store, and the value taught back to bidding',
 'ga-scale': 'The spend that converts separated from the spend that does not, then scaled',
 'ga-buyers': 'Five kinds of brand, each needing its own campaign shape',
 'cr-hero': 'One asset cutting through a feed the eye would otherwise slide past',
 'cr-angle': 'The same subject shot four ways, and the attention each angle held',
 'cr-system': 'One concept resolved into five formats, each cut for its own channel',
 'cr-refresh': 'Performance decaying between refreshes, and lifted each time new work lands',
 'ai-hero': 'One brief going in, and the work of a team coming back',
 'ai-drain': 'Five workflows ranked by the hours each one takes',
 'ai-build': 'An AI layer joining the tools the team already works in',
 'ai-adopt': 'Output climbing as more of the team picks the system up',
 'pr-hero': 'One placement standing in front of the coverage behind it',
 'pr-audit': 'Four lanes of the conversation already taken, and the one still open',
 'pr-readiness': 'One message, carried the same way across every channel',
 'pr-story': 'A press release beside a story, and the difference between them',
 'pr-moment': 'A news cycle forecast, and the moment built into it',
 'pr-speed': 'The same ground covered, arriving a third of the way in',
 'af-hero': 'Revenue from the existing channels, and the slice partners add on top',
 'af-model': 'Three partner tiers, and the margin none of their commissions cross',
 'af-recruit': 'Eight candidate partners measured for fit, and the three chosen',
 'af-quality': 'Partner revenue tracked over time, with the traffic that never counted filtered out',
 'wd-hero': 'A page laid out on its grid: headline, copy, one action, one image',
 'wd-journey': 'Four sections in the order a visitor reads them, ending at the action',
 'wd-build': 'Design, copy, structure and performance landing as one finished page',
 'wd-measure': 'A page with the attention it received mapped across it',
}
NAV_SELF = {
 'seo': 'SEO', 'link-building': 'Link Building', 'geo': 'GEO',
 'content-creation': 'Content Creation', 'email-marketing': 'Email & SMS',
 'paid-social': 'Paid Social',
 'google-ads': 'Google Ads',
 'creative': 'Creative',
 'ai-solutions': 'AI Solutions',
 'press-pr': 'Press & PR',
 'affiliate-marketing': 'Affiliate Marketing',
 'web-design': 'Web Design',
}
SIBLING_HREF = {
 'SEO': '../seo/', 'GEO': '../geo/', 'Link Building': '../link-building/',
 'Content Creation': '../content-creation/', 'Email & SMS': '../email-marketing/',
 'Paid Social': '../paid-social/',
 'Google Ads': '../google-ads/',
 'Creative': '../creative/',
 'AI Solutions': '../ai-solutions/',
 'Press & PR': '../press-pr/',
 'Affiliate Marketing': '../affiliate-marketing/',
 'Web Design': '../web-design/',
}
E = lambda s: html.escape(s, quote=False).replace('&amp;#', '&#')

_CHROME = None
def shared_chrome():
    """Nav, cursor and footer are lifted once from a built page and never edited."""
    global _CHROME
    if _CHROME is None:
        src = open(os.path.join(ROOT, 'services/seo/index.html'), encoding='utf-8').read()
        a = src.index('<!-- CUSTOM CURSOR -->')
        b = src.index('<main')
        nav = src[a:b]
        foot = src[src.index('</main>') + len('</main>'):src.index('<script src="https://cdnjs')]
        # the source lost the opening angle bracket of the footer comment, which
        # leaves its text rendering as a stray line above the footer
        foot = foot.replace('\n!-- FOOTER', '\n<!-- FOOTER')
        nav, foot = rootify(nav, '/services/seo/'), rootify(foot, '/services/seo/')
        nav = nav.replace('<a href="/services/seo" class="nav-link">Services', '<a href="/services" class="nav-link">Services')
        # the menu's thumbnails are ~100px wide; the 2400px case-study photos behind
        # them cost 600KB a page, so interior pages use 600px copies of the same images
        nav = re.sub(r'src="/uploads/(bkfc-david-feldman|dr-harrison-lee-1|dr-harrison-lee-2)\.webp"', r'src="/uploads/nav/\1.webp"', nav)
        # footer destinations follow the production site's footer for the same labels
        foot = re.sub(r'<a href="/contact">(\s*SEO &(?:amp;)? GEO\s*)</a>', r'<a href="/services/seo">\1</a>', foot)
        foot = re.sub(r'<a href="/contact">(\s*Web Design &(?:amp;)? Dev\s*)</a>', r'<a href="/services/web-design">\1</a>', foot)
        _CHROME = (nav, foot)
    return _CHROME

def nav_for(slug, nav):
    """The header is the same on every page: every link is the page's one address,
       as on the production site, including the link to the page itself."""
    return nav

def art_size(folder, name):
    """Intrinsic size from the artwork itself, so the layout never shifts."""
    src = open(os.path.join(ROOT, 'uploads', folder, name + '.svg'), encoding='utf-8').read()
    m = re.search(r'viewBox="[\d.-]+ [\d.-]+ ([\d.]+) ([\d.]+)"', src)
    return (round(float(m.group(1))), round(float(m.group(2)))) if m else (1600, 1000)

INLINE_HERO = {'google-ads': 'tools/google-ads-hero.svg'}

def inline_hero(slug):
    return '<div class="sv-stage">%s</div>' % open(os.path.join(ROOT, INLINE_HERO[slug]), encoding='utf-8').read()

def drawn_hero(folder, name):
    """The hero drawing inline, so it can draw itself on arrival. Its alt text
       becomes the accessible name; the drawing is otherwise the same file."""
    svg = open(os.path.join(ROOT, 'uploads', folder, name + '.svg'), encoding='utf-8').read().strip()
    svg = re.sub(r'^<\?xml[^>]*>\s*', '', svg)
    svg = re.sub(r'<svg\b', '<svg class="sv-draw" aria-label="%s"' % E(ALT.get(name, '')), svg, count=1)
    return '<div class="sv-stage rv" data-rv="120">%s</div>' % svg

def stage(folder, name, eager=False):
    w, h = art_size(folder, name)
    return ('<div class="sv-stage rv" data-rv="120">'
            '<img src="/uploads/%s/%s.svg" alt="%s" width="%d" height="%d" '
            '%s decoding="async">'
            '</div>') % (folder, name, E(ALT.get(name, '')), w, h,
                         'fetchpriority="high"' if eager else 'loading="lazy"')

def chapter(c, folder, img, dark=False):
    link = ('\n      <a class="sv-link" href="%s">%s</a>' % (E(c['link']['href']), E(c['link']['text']))) if c.get('link') else ''
    return ('<section class="sv-chapter">\n'
            '  <div class="sv-in">\n'
            '    <div class="sv-mid rv">\n'
            '      <span class="sv-label">%s</span>\n'
            '      <h2 class="sv-h">%s</h2>\n'
            '      <p class="sv-body">%s</p>%s\n'
            '    </div>\n'
            '    %s\n'
            '  </div>\n'
            '</section>') % (E(c['label']), c.get('h2_html') or E(c['h2']), E(c['body']), link, stage(folder, img))

def build(slug, d):
    folder, hero_img, chap_imgs, dark_at = ART[slug]
    cta_href = d.get('cta_href', '/#contact')     # where production's service CTAs go
    nav, foot = shared_chrome()
    faq = d.get('faq') or []

    path = '/services/%s' % slug
    extra = ('<link rel="stylesheet" href="/assets/css/motion.css">\n'
             '<script>document.documentElement.classList.add("mo")</script>')
    head = seo_head(path, ['/assets/css/styles.css', '/assets/css/case-studies.css', '/assets/css/service-page.css'], extra)
    head += '<body class="cs-page paper-page%s">\n<div class="mo-curtain" aria-hidden="true"></div>\n' % (' ga' if slug in INLINE_HERO else '')

    hero = ('\n<main class="sv">\n\n'
      '<section class="sv-hero" id="top">\n  <div class="sv-in">\n'
      '    <div class="rv">\n'
      '      <span class="sv-label is-accent">%s</span>\n'
      '      <h1 class="sv-h">%s</h1>\n'
      '      <p class="sv-lede">%s</p>\n'
      '      <a class="sv-btn" href="%s">%s <span aria-hidden="true">&#8594;</span></a>\n'
      '    </div>\n'
      '  </div>\n  %s\n</section>\n') % (
        E(d['label']), d.get('h1_html') or E(d['h1']), E(d['lede']), cta_href, E(d['cta']),
        inline_hero(slug) if slug in INLINE_HERO else drawn_hero(folder, hero_img))

    def figsize(v):
        n = len(v)
        return '' if n <= 7 else ' is-mid' if n <= 11 else ' is-long' if n <= 16 else ' is-text'
    figs = ''.join('<div class="sv-fig%s"><strong>%s</strong><span>%s</span></div>'
                   % (figsize(f['value']), E(f['value']), E(f['cap']))
                   for f in d['figures'])
    figures = ('\n<section class="sv-figures">\n  <div class="sv-in">\n'
               '    <div class="sv-figrow rv">%s</div>\n  </div>\n</section>\n') % figs

    chaps = d['chapters']
    before = ''.join('\n' + chapter(c, folder, chap_imgs[i]) + '\n' for i, c in enumerate(chaps[:dark_at]))
    dark_block = chapter(chaps[dark_at], folder, chap_imgs[dark_at], dark=True)
    turn = '\n<div class="sv-turn">\n%s\n</div>\n' % dark_block
    after = ''.join('\n' + chapter(c, folder, chap_imgs[dark_at + 1 + i]) + '\n'
                    for i, c in enumerate(chaps[dark_at + 1:]))

    rows = ''.join(
      '<div class="sv-row rv" data-rv="%d"><b>%02d</b><h3>%s</h3><p>%s</p></div>' % (i * 60, i + 1, E(x['title']), E(x['desc']))
      for i, x in enumerate(d['list']))
    lst = ('\n<section class="sv-list" id="deliverables" aria-labelledby="svList">\n  <div class="sv-in">\n'
           '    <div class="sv-list-head rv">\n'
           '      <span class="sv-label is-accent">%s</span>\n'
           '      <h2 class="sv-h" id="svList">%s</h2>\n'
           '    </div>\n    %s\n  </div>\n</section>\n') % (
             E(d.get('list_label') or 'What You Get'),
             d.get('list_h2_html') or E(d.get('list_h2', 'The pieces needed to scale cleanly.')), rows)

    faq_html = ''
    if faq:
        qs = ''.join(
          '<div class="sv-q"><button type="button" aria-expanded="false" aria-controls="q%d">'
          '<span class="t">%s</span><span class="pm" aria-hidden="true"></span></button>'
          '<div class="sv-a" id="q%d"><div><p>%s</p></div></div></div>' % (i + 1, E(x['q']), i + 1, E(x['a']))
          for i, x in enumerate(faq))
        faq_html = ('\n<section class="sv-faq" id="faq" aria-labelledby="svFaq">\n  <div class="sv-in">\n'
                    '    <div class="sv-faq-head rv">\n'
                    '      <span class="sv-label is-accent">FAQ</span>\n'
                    '      <h2 class="sv-h" id="svFaq">%s</h2>\n'
                    '      <a class="sv-link" href="/#contact">Talk to Us</a>\n'
                    '    </div>\n    <div class="rv">%s</div>\n  </div>\n</section>\n') % (d.get('faq_h2_html') or 'Common questions.', qs)

    final = ('\n<section class="sv-final" id="ready" aria-labelledby="svReady">\n  <div class="sv-in">\n'
             '    <div class="sv-mid rv">\n'
             '      <span class="sv-label is-accent">Ready?</span>\n'
             '      <h2 class="sv-h" id="svReady">%s</h2>\n'
             '      <a class="sv-btn" href="%s">%s <span aria-hidden="true">&#8594;</span></a>\n'
             '    </div>\n  </div>\n</section>\n\n</main>\n') % (d.get('final_h2_html') or 'Let\'s build the system that grows with you.', cta_href, E(d['final_cta']))

    scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>\n'
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>\n'
               '<script src="/assets/js/case-studies.js"></script>\n'
               '<script src="/assets/js/motion.js"></script>\n'
               '<script src="/assets/js/service-page.js"></script>\n'
               '<script src="/assets/js/forms.js" data-root="/"></script>\n</body>\n</html>\n')

    doc = head + nav_for(slug, nav) + hero + figures + before + turn + after + lst + faq_html + final + foot + scripts
    out = os.path.join(ROOT, 'services', slug, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(doc)
    return len(doc)

if __name__ == '__main__':
    shared_chrome()          # cache before the first page overwrites its source
    for slug, d in COPY.items():
        n = build(slug, d)
        print('%-18s %6d chars  %d chapters  %d list  %d questions' % (slug, n, len(d['chapters']), len(d['list']), len(d.get('faq') or [])))
