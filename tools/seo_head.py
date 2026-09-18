"""The <head> of every page, reproduced from the production site.

tools/seo-meta.json holds, per URL path, exactly what ascendgpartners.com
serves once rendered: title, description (or none), robots (or none), the
canonical as written in its source, the Open Graph and Twitter sets, and the
application-name. Nothing here is composed; a page gets the values recorded
for its path, in production's order, or the build fails.
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, 'tools/seo-meta.json'), encoding='utf-8'))
A = lambda s: html.escape(s, quote=True)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">\n')

def head(path, stylesheets, extra=''):
    """path: the production URL path, e.g. '/services/seo'. stylesheets: root-relative hrefs."""
    if path not in SPEC:
        raise SystemExit('no production SEO record for %s; add it to tools/seo-meta.json from the inventory, do not invent one' % path)
    m = SPEC[path]
    out = ['<!DOCTYPE html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
           '<meta name="viewport" content="%s">' % A(m['viewport'] or 'width=device-width, initial-scale=1')]
    out.append(FONTS.rstrip('\n'))
    out += ['<link rel="stylesheet" href="%s">' % s for s in stylesheets]
    out.append('<title>%s</title>' % html.escape(m['title'], quote=False))
    if m.get('description'): out.append('<meta name="description" content="%s">' % A(m['description']))
    if m.get('application-name'): out.append('<meta name="application-name" content="%s">' % A(m['application-name']))
    if m.get('robots'): out.append('<meta name="robots" content="%s">' % A(m['robots']))
    if m.get('canonical'): out.append('<link rel="canonical" href="%s">' % A(m['canonical']))
    for k in ['og:title', 'og:description', 'og:url', 'og:site_name', 'og:image', 'og:image:width', 'og:image:height', 'og:image:alt', 'og:type']:
        if m.get(k): out.append('<meta property="%s" content="%s">' % (k, A(m[k])))
    for k in ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']:
        if m.get(k): out.append('<meta name="%s" content="%s">' % (k, A(m[k])))
    out += ['<link rel="icon" href="/favicon.png">', '<link rel="apple-touch-icon" href="/favicon.png">']
    if extra: out.append(extra.rstrip('\n'))
    out.append('</head>')
    return '\n'.join(out) + '\n'
