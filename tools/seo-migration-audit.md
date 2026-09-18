# SEO migration audit: ascendgpartners.com → the new site

Prepared 2026-09-18 against production commit `dpl_EhP1rbpm8P9s24hPgx3v9RQnUTYi` (the deployment id in production's asset URLs) and the new site at commit `42606ff` and after.

## Method

1. Every URL in production's `sitemap.xml` (33), plus `/services`, `/storefront` and a deliberate 404, was fetched twice: once raw (status, headers, redirects) and once rendered in headless Chrome after hydration (React hoists `<title>`, canonical and Open Graph into `<head>` at runtime; the raw HTML of the blog posts has them in `<body>`). The rendered DOM is what Google indexes, so it is the reference.
2. The rendered values were frozen into `tools/seo-meta.json`. Both page generators emit `<head>` from that file and refuse to build a page that has no production record.
3. Redirect and status behaviour was captured with a request matrix (http, www, trailing slash, `/index.html`, case, query strings, 404).
4. The new site was inventoried the same way, on the Vercel deployment, and compared field by field (`seo/diff.py`): 608 head-level fields across 31 URLs.
5. The deployed site was crawled from `/` (29 routes, 29 internal destinations, 0 broken, 0 broken anchors, 0 page errors; `tools/link-audit.md`).

## What is identical to production

| Element | State |
|---|---|
| URL paths and slugs | Identical for every production URL that has a page. Slash-free addresses; `/services/seo/` → 308 → `/services/seo`, as production. |
| http → https | 308 (Vercel default), as production. |
| www → apex | 301 via `vercel.json`, as production. Takes effect once `www.ascendgpartners.com` is attached to the Vercel project. |
| Titles | Identical on all 30 pages, including the truncated ones ("...") production emits. |
| Meta descriptions | Identical where production has one; absent where production has none (7 service pages). |
| Robots meta | `index,follow` on `/`; `noindex, follow` on privacy and terms; `noindex, nofollow` on 404; none elsewhere. Identical. |
| Canonicals | Identical, as written in production's source: self-referencing on blog posts, case studies, about, press, reviews, contact, privacy, terms; `https://ascendgpartners.com` (no slash) on every service page, `/blog`, `/case-studies` and `/services/coming-soon`; `https://ascendgpartners.com/` on the homepage. |
| Open Graph and Twitter | Identical sets and values per page (`og:title/description/url/site_name/image/image:width/image:height/image:alt/type`, `twitter:card/title/description/image`), including production's homepage defaults on the service pages and its `favicon.png` image. |
| `application-name`, `viewport`, `lang`, icons | Identical (`initial-scale=1` on interior pages, `1.0` on the homepage, as production). |
| Structured data | None, as production. The JSON-LD the earlier build had (Service, FAQPage, BreadcrumbList, BlogPosting, Organization) was removed to match. |
| H1s | Identical text on every page, including production's `<br>` line breaks and `<em>` emphasis inside them, and straight apostrophes. |
| Heading outlines (h1–h4) | Identical on every page except the homepage (see below). Case studies were rebuilt from production's own articles so every heading level and order matches. |
| Body copy | Service pages re-derived from production's rendered DOM character for character (`tools/extract-service-copy.py`); case studies rebuilt from production's article HTML (`tools/case-studies-src/`); blog posts, about, reviews, press, contact, legal, coming-soon: production's text. |
| Internal links and anchor text | Header, footer and in-content links resolve to production's destinations with production's anchor text, including the SEO page's in-chapter "See our PR services", the case studies' outlet links, "← Back to Case Studies", "← Back to Blog", the posts' closing "Work With Us", the FAQ "Talk to Us", and every service CTA to `/#contact`. |
| External links | Same URLs and anchor text as production. Forbes, Inc., FCC and Vents Magazine answer 403 to automated requests and McKinsey times out; they could not be confirmed by a script, but they are production's own links, carried unchanged. |
| Images and alt text | Every image production shows is present with production's `src` (original filenames, original `?v=` query) and production's alt text. Production's image files are hosted at their original paths, byte-identical (verified by checksum), so indexed image URLs keep resolving after the domain moves. The optimised copies from the earlier build are attached as `srcset` candidates only. |
| sitemap.xml | Production's file, byte for byte (33 URLs with its lastmod/changefreq/priority). |
| robots.txt | Production's file, byte for byte. |
| 404 | Status 404, title "Page Not Found", `noindex, nofollow`, as production's rendered 404. |
| Headers | No `X-Robots-Tag` on either. HSTS `max-age=63072000` on both. |

## Differences (every one of them)

### A. Decisions for you: production behaviour reproduced that I recommend changing

These are copied faithfully because the brief is parity. Each is a production defect worth a decision before or after launch. Changing any of them is a one-line edit to `tools/seo-meta.json` and a rebuild.

1. **Canonical to the homepage on 15 pages.** Every service page, `/blog`, `/case-studies` and `/services/coming-soon` carry `<link rel="canonical" href="https://ascendgpartners.com">`. That tells Google each of those pages is a duplicate of the homepage. Google usually ignores a canonical this implausible, which is probably why the pages still rank, but it is a standing risk. Recommendation: self-referencing canonicals.
2. **No meta description on seven service pages** (affiliate-marketing, ai-solutions, content-creation, creative, link-building, paid-social, web-design).
3. **Homepage Open Graph on interior pages.** Service pages, `/blog`, `/case-studies` and `/services/coming-soon` share the homepage's `og:title`, `og:description`, `og:url` and `favicon.png` as `og:image`, so a shared service link previews as the homepage.
4. **The sitemap lists five URLs that return 404** on production and here: `/blog/ai-changing-seo-2026`, `/case-studies/ember-ai-visibility-q4`, `/case-studies/finance-paid-media-lead-surge`, `/case-studies/hedley-bennett-backlinking`, `/case-studies/homage-email-lifecycle`. It also lists `/storefront` (noindex) and `/services/coming-soon` (an orphan). Kept verbatim.
5. **Three blog posts link to `/blog/ai-changing-seo-2026`**, which does not exist on production (404). On the new site that sentence keeps its words but is not a link. This is the one internal link deliberately not reproduced; restore it if you prefer a link to a 404.

### B. Content that differs because the approved Vercel homepage is not production's homepage

You locked the homepage as it appears on ascendgpartners.vercel.app. Production's homepage is a different page. Its head is identical (title, description, robots, canonical, OG, Twitter), but the body differs: production's h1 is "Ascend Growth Partners" (yours: "We Get You Featured in Top Media and Build Your Brand Into an Industry Authority"), production has an "Over $50M in revenue generated for our clients" section with the three case studies as h3s, and different h2/h3 text throughout. Production's footer also differs from the locked footer: it links SEO and GEO separately, plus "Content & Creative", "Email & SMS" and "Press & PR", and labels "Performance Mktg"; the locked footer has "SEO & GEO" (now → `/services/seo`), "Performance Marketing", "Web Design & Dev", "Careers" → `/contact`, social icons → `/contact`, and "Cookies" → `/privacy-policy`. The header's mega-menu on production has an "All Case Studies" link; the locked header has "Case Studies". None of this was changed because the homepage, header and footer are locked; it is listed so it is a conscious choice.

### C. Additions (present on the new site, absent on production)

6. `/services`: production returns 404 for the "Services" link in its own header. The new site has an index page there, with the site-wide default metadata production emits for pages without their own (default title, canonical to the homepage). Remove `services/index.html` and the record in `seo-meta.json` if you would rather keep the 404.
7. The hand-drawn SVG illustrations on the twelve service pages: the hero drawing is inline SVG (labelled with `aria-label`, so it is not an `<img>`), the chapter drawings are `<img>` elements with alt text. Production's service pages have no content images.
8. A closing "Ready? / Let's build the system that grows with you. / Work With Us" block on about, reviews, press, blog index and contact (a paragraph, not a heading, so outlines match). Production has no closing block on those pages; it adds one link to `/contact` per page.
9. On `/company/press`: links to `/services/press-pr`, `/case-studies` and `mailto:hello@ascendgpartners.com`; on `/contact` and `/privacy-policy`: a `mailto:` link. Production has none of these.
10. `/404.html` exists as a page (production renders its 404 in-app).
11. The `/blog` and `/case-studies` card links wrap category, date and title in the anchor (production's wrap image, title, author, category). Same destinations.

### C2. Reproduced but unloadable in browsers

12a. `/company/press` shows the Vents Magazine article picture with production's exact `src` (a hotlink to `ventsmagazine.com`). Their server sends `Cross-Origin-Resource-Policy: same-origin`, so browsers refuse to render it on any other site, production included (crawlers are not subject to that header, which is why the reference is kept). The frame hides itself if the picture fails, and the page logs one blocked request.

### D. Pages not migrated

12. `/storefront`: a `noindex, nofollow` demo of a Whop checkout with placeholder products and non-functional "Buy" buttons. Not rebuilt; it returns 404 here. It carries no index value (noindex on production) and rebuilding it would mean shipping fake purchase flows.

### E. Host-level items to verify at cutover

13. `www.ascendgpartners.com` must be added to the Vercel project for the 301 in `vercel.json` to apply.
14. `/index.html` and `/services/seo/index.html` answer 308 to the clean URL on Vercel (`cleanUrls`); production answers 404. Harmless, noted for completeness.
15. `/SERVICES/SEO` answers 200 on production (Next.js) and 404 on Vercel static hosting. No internal or known external link uses uppercase paths.
16. GitHub Pages (`ausystems.github.io/ascendgpartners`) can no longer mirror the site: it serves from a sub-path and cannot do slash-free URLs or the relay function. Vercel is the deployment target.

## Reproducing the audit

```
python3 tools/extract-service-copy.py     # service copy from production's rendered pages
python3 tools/build-service-pages.py
python3 tools/build-site-pages.py
python3 tools/build-case-studies.py       # from tools/case-studies-src/*.html
```

The rendered inventories and the diff script live in the session workspace (`seo/rendered.js`, `seo/diff.py`); `tools/seo-meta.json` is the frozen production record every head is built from.
