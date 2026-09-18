/* Ascend — motion. Loaded before service-page.js on every interior page.
   One language: a graphite curtain hands the page over, type arrives line by
   line from behind a mask, images are wiped in, figures count up, and the
   cursor is answered by the things it nears. Everything here is enhancement.
   With the script absent the pages are complete and still; with reduced
   motion they stay still. */
(function () {
  'use strict';
  var html = document.documentElement;
  var curtain = document.querySelector('.mo-curtain');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var hasGsap = typeof window.gsap !== 'undefined';

  function still() {                      // nothing moves, nothing is hidden
    if (curtain) curtain.remove();
    html.classList.remove('mo');
  }
  if (reduce || !hasGsap) { still(); return; }
  if (typeof ScrollTrigger !== 'undefined') gsap.registerPlugin(ScrollTrigger);

  var EASE = 'expo.out';

  /* ---------- type: split a heading into masked lines ---------- */
  function wrapWords(node, out) {
    var i, c, t, words, w, span;
    for (i = 0; i < node.childNodes.length; i++) {
      c = node.childNodes[i];
      if (c.nodeType === 3) {
        t = c.nodeValue;
        if (!t.trim()) { out.push(document.createTextNode(' ')); continue; }
        words = t.split(/(\s+)/);
        for (w = 0; w < words.length; w++) {
          if (!words[w]) continue;
          if (/^\s+$/.test(words[w])) { out.push(document.createTextNode(' ')); continue; }
          span = document.createElement('span'); span.className = 'mo-w'; span.textContent = words[w]; out.push(span);
        }
      } else if (c.nodeType === 1) {
        if (c.tagName === 'BR') { out.push(c.cloneNode(false)); continue; }
        var el = c.cloneNode(true); el.classList.add('mo-w'); out.push(el);   // an inline element is one unit
      }
    }
  }
  function split(h) {
    if (h.__lines) return h.__lines;
    if (!h.__html) h.__html = h.innerHTML;
    var nodes = []; wrapWords(h, nodes);
    h.innerHTML = '';
    nodes.forEach(function (n) { h.appendChild(n); });
    var kids = [].slice.call(h.childNodes), lines = [], cur = null, top = null, k, n, isW, y;
    for (k = 0; k < kids.length; k++) {
      n = kids[k];
      if (n.nodeType === 1 && n.tagName === 'BR') { cur = null; continue; }
      isW = n.nodeType === 1;
      if (isW) {
        y = n.offsetTop;
        if (!cur || Math.abs(y - top) > 2) { cur = []; lines.push(cur); top = y; }
        cur.push(n);
      } else if (cur) cur.push(n);
    }
    h.innerHTML = '';
    var out = [];
    lines.forEach(function (line) {
      var outer = document.createElement('span'); outer.className = 'mo-line';
      var inner = document.createElement('span'); inner.className = 'mo-line-in';
      line.forEach(function (n) { inner.appendChild(n); });
      outer.appendChild(inner); h.appendChild(outer); out.push(inner);
    });
    h.__lines = out;
    return out;
  }
  var splitHeads = [];
  function lines(h) { var l = split(h); if (splitHeads.indexOf(h) < 0) splitHeads.push(h); return l; }
  var resizeT;
  window.addEventListener('resize', function () {
    clearTimeout(resizeT);
    resizeT = setTimeout(function () {                 // lines are measured, so they are re-measured
      splitHeads.forEach(function (h) { h.innerHTML = h.__html; h.__lines = null; });
      splitHeads.forEach(function (h) { gsap.set(split(h), { yPercent: 0 }); });
    }, 200);
  });

  /* ---------- figures count up ---------- */
  function counters(scope) {
    scope.querySelectorAll('.sv-fig strong').forEach(function (el) {
      if (el.__counted) return; el.__counted = true;
      var m = /^([^\d]*)(\d[\d,]*(?:\.\d+)?)([\s\S]*)$/.exec(el.textContent.trim());
      if (!m) return;
      var target = parseFloat(m[2].replace(/,/g, '')), decimals = (m[2].split('.')[1] || '').length, grouped = m[2].indexOf(',') > -1;
      var obj = { v: 0 };
      gsap.to(obj, { v: target, duration: 1.4, ease: EASE, onUpdate: function () {
        var v = obj.v.toFixed(decimals); if (grouped) v = Number(v).toLocaleString('en-US', { minimumFractionDigits: decimals });
        el.textContent = m[1] + v + m[3];
      } });
    });
  }

  /* ---------- the drawing draws itself ----------
     Strokes are dashed to their own length and offset out of sight, then let
     run; filled shapes follow; the accent arrives last, as the conclusion. */
  function draw(svg, delay) {
    if (svg.__drawn) return; svg.__drawn = true;
    var strokes = [], fills = [], accent = [];
    [].slice.call(svg.querySelectorAll('path, line, rect, circle, polyline, ellipse')).forEach(function (el) {
      var st = el.getAttribute('stroke'), fi = el.getAttribute('fill');
      var isAccent = /e8613c/i.test(st || '') || /e8613c/i.test(fi || '');
      if (st && st !== 'none') {
        var len = 0; try { len = el.getTotalLength(); } catch (e) { len = 0; }
        if (len > 0) { el.style.strokeDasharray = len; el.style.strokeDashoffset = len; strokes.push(el); }
      }
      if (fi && fi !== 'none' && !(st && st !== 'none')) { if (isAccent) accent.push(el); else fills.push(el); }
      else if (isAccent && st) accent.push(el);
    });
    // a filled shape that is also the ground of the drawing stays as it is
    fills = fills.filter(function (el) { var b = el.getBBox(); return !(b.width >= svg.viewBox.baseVal.width * 0.98 && b.height >= svg.viewBox.baseVal.height * 0.98); });
    gsap.set(fills, { opacity: 0, transformOrigin: '50% 50%', scale: 0.92 });
    gsap.set(accent.filter(function (e) { return strokes.indexOf(e) < 0; }), { opacity: 0, transformOrigin: '50% 50%', scale: 0.9 });
    var tl = gsap.timeline({ delay: delay });
    tl.to(strokes, { strokeDashoffset: 0, duration: 1.5, ease: 'power2.inOut', stagger: { each: 0.035, from: 'start' } }, 0)
      .to(fills, { opacity: 1, scale: 1, duration: 0.8, ease: EASE, stagger: 0.03 }, 0.55)
      .to(accent.filter(function (e) { return strokes.indexOf(e) < 0; }), { opacity: 1, scale: 1, duration: 0.9, ease: 'back.out(1.6)', stagger: 0.05 }, 1.05)
      .add(function () { strokes.forEach(function (el) { el.style.strokeDasharray = ''; el.style.strokeDashoffset = ''; }); });
    return tl;
  }

  /* ---------- reveal: what a block does as it arrives ---------- */
  function reveal(el, delay) {
    delay = delay || 0;
    el.classList.add('is-in');
    var drawn = el.matches('.sv-stage') ? el.querySelector('svg.sv-draw') : el.querySelector('.sv-stage > svg.sv-draw');
    if (drawn) draw(drawn, delay + 0.15);
    var heads = el.matches('h1, h2, h3, p') ? [el] : [].slice.call(el.querySelectorAll('.sv-h, .pg-h, .pg-review p, .pg-statement p'));
    heads.forEach(function (h) {
      gsap.fromTo(lines(h), { yPercent: 112 }, { yPercent: 0, duration: 1.15, ease: EASE, stagger: 0.075, delay: delay });
    });
    var imgs = el.querySelectorAll('.sv-stage > img, .pg-portrait');
    if (imgs.length) gsap.fromTo(imgs, { clipPath: 'inset(100% 0 0 0)', scale: 1.06 }, { clipPath: 'inset(0% 0 0 0)', scale: 1, duration: 1.35, ease: EASE, delay: delay + 0.1, clearProps: 'clipPath' });
    var items = el.querySelectorAll('.pg-entries > li, .sv-figrow > *, .pg-checks > *');
    if (items.length) gsap.fromTo(items, { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.95, ease: EASE, stagger: 0.06, delay: delay + 0.05, clearProps: 'opacity,transform' });
    counters(el);
  }

  var targets = [].slice.call(document.querySelectorAll('.rv'));
  var hero = document.querySelector('.sv-hero, .pg-hero, .pg-contact');
  var onFirstScreen = function (el) { return el.getBoundingClientRect().top < window.innerHeight * 0.92; };
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { io.unobserve(en.target); reveal(en.target); } });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
  var ioTall = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { ioTall.unobserve(en.target); reveal(en.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });

  /* ---------- arrival: fonts, then the curtain lifts and the hero plays ---------- */
  function arrive() {
    var first = [], later = [];
    targets.forEach(function (el) { (onFirstScreen(el) ? first : later).push(el); });
    later.forEach(function (el) { (el.offsetHeight > window.innerHeight * 0.6 ? ioTall : io).observe(el); });
    if (curtain) {
      html.classList.add('mo-lifted');
      gsap.set(curtain, { opacity: 1, visibility: 'visible', clipPath: 'inset(0% 0 0 0)' });
      gsap.to(curtain, { clipPath: 'inset(0 0 100% 0)', duration: 0.95, ease: 'expo.inOut', onComplete: function () { curtain.style.display = 'none'; } });
    }
    first.forEach(function (el, i) { reveal(el, (curtain ? 0.28 : 0) + i * 0.12); });
    // the first screen rises to meet the lifting curtain
    if (curtain && hero) gsap.from(hero, { y: 44, duration: 1.4, ease: EASE, delay: 0.1, clearProps: 'transform' });
    // the hero image drifts a little slower than the page
    var art = document.querySelector('.sv-hero .sv-stage > img, .sv-hero .sv-stage > svg');
    if (art && typeof ScrollTrigger !== 'undefined') gsap.to(art, { yPercent: -7, ease: 'none', scrollTrigger: { trigger: hero || art, start: 'top top', end: 'bottom top', scrub: true } });
    // portraits drift a little inside their frame on wide screens; the picture is
    // held slightly larger than the frame so the drift never shows an edge
    if (typeof ScrollTrigger !== 'undefined' && fine && !window.matchMedia('(max-width: 1024px)').matches) {
      document.querySelectorAll('.pg-portrait').forEach(function (img, i) {
        gsap.fromTo(img, { yPercent: i % 2 ? 2 : 3, scale: 1.08 }, { yPercent: i % 2 ? -2 : -3, scale: 1.08, ease: 'none', scrollTrigger: { trigger: img, start: 'top bottom', end: 'bottom top', scrub: true } });
      });
    }
  }
  var fontsReady = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
  var started = false, start = function () { if (started) return; started = true; arrive(); };
  fontsReady.then(start); setTimeout(start, 420);   // fonts, or a short wait at most

  /* ---------- the cursor is answered ---------- */
  if (fine) {
    document.querySelectorAll('.sv-btn, .pg-btn').forEach(function (btn) {
      var toX = gsap.quickTo(btn, 'x', { duration: 0.5, ease: 'power3.out' }), toY = gsap.quickTo(btn, 'y', { duration: 0.5, ease: 'power3.out' });
      btn.addEventListener('mousemove', function (e) {
        var r = btn.getBoundingClientRect();
        toX((e.clientX - (r.left + r.width / 2)) * 0.28); toY((e.clientY - (r.top + r.height / 2)) * 0.28);
      });
      btn.addEventListener('mouseleave', function () { gsap.to(btn, { x: 0, y: 0, duration: 0.9, ease: 'elastic.out(1, 0.45)' }); });
    });
    var entries = document.querySelectorAll('.pg-entry[data-preview]');
    if (entries.length) {
      var prev = document.createElement('div'); prev.className = 'mo-preview'; prev.setAttribute('aria-hidden', 'true');
      document.body.appendChild(prev);
      var pimg = null;                       // made on the first hover, so no empty image ever sits in the page
      var px = gsap.quickTo(prev, 'x', { duration: 0.55, ease: 'power3.out' }), py = gsap.quickTo(prev, 'y', { duration: 0.55, ease: 'power3.out' });
      entries.forEach(function (a) {
        a.addEventListener('mouseenter', function (e) {
          if (!pimg) { pimg = document.createElement('img'); pimg.alt = ''; prev.appendChild(pimg); }
          pimg.src = a.getAttribute('data-preview');
          gsap.set(prev, { x: e.clientX + 310, y: e.clientY - 30 });
          gsap.to(prev, { opacity: 1, scale: 1, duration: 0.5, ease: EASE });
        });
        a.addEventListener('mousemove', function (e) { px(e.clientX + 310); py(e.clientY - 30); });
        a.addEventListener('mouseleave', function () { gsap.to(prev, { opacity: 0, scale: 0.9, duration: 0.35, ease: 'power2.out' }); });
      });
    }
  }

  /* ---------- the page is handed over ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || !curtain || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var href = a.getAttribute('href');
    if (a.target === '_blank' || a.hasAttribute('download') || /^(#|mailto:|tel:)/.test(href)) return;
    var url; try { url = new URL(a.href, location.href); } catch (err) { return; }
    if (url.origin !== location.origin) return;
    if (url.pathname === location.pathname && url.hash) return;
    e.preventDefault();
    html.classList.add('mo-lifted');
    curtain.style.display = 'block';
    // the name of where we are going rides up with the curtain
    var name = a.getAttribute('data-title') || (a.querySelector('h1, h2, h3') || a).textContent.replace(/\s+/g, ' ').trim();
    var label = curtain.querySelector('.mo-curtain-name');
    if (name && name.length <= 48 && !/[→↗]/.test(name)) {
      if (!label) { label = document.createElement('span'); label.className = 'mo-curtain-name'; label.innerHTML = '<span class="mo-line"><span class="mo-line-in"></span></span>'; curtain.appendChild(label); }
      label.querySelector('.mo-line-in').textContent = name; label.style.display = 'block';
      gsap.fromTo(label.querySelector('.mo-line-in'), { yPercent: 110 }, { yPercent: 0, duration: 0.7, ease: EASE, delay: 0.18 });
    } else if (label) label.style.display = 'none';
    gsap.set(curtain, { opacity: 1, visibility: 'visible', clipPath: 'inset(100% 0 0 0)' });
    var main = document.querySelector('main');
    if (main) gsap.to(main, { y: -36, duration: 0.6, ease: 'expo.inOut' });
    gsap.to(curtain, { clipPath: 'inset(0% 0 0 0)', duration: 0.6, ease: 'expo.inOut', onComplete: function () { setTimeout(function () { location.href = url.href; }, 90); } });
  });
  window.addEventListener('pageshow', function (e) { if (e.persisted && curtain) curtain.style.display = 'none'; });

  /* inertial wheel scrolling is the shared chrome's (case-studies.js), the same on every page */

  if (typeof ScrollTrigger !== 'undefined') {
    /* chapter images drift a touch slower than the page */
    document.querySelectorAll('.sv-chapter:not(.sv-turn .sv-chapter) .sv-stage > img').forEach(function (img) {
      gsap.fromTo(img, { yPercent: 4 }, { yPercent: -4, ease: 'none', scrollTrigger: { trigger: img.parentNode, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
    /* a reading line on articles */
    var article = document.querySelector('.pg-article');
    if (article) {
      var line = document.createElement('div'); line.className = 'mo-progress'; line.setAttribute('aria-hidden', 'true'); document.body.appendChild(line);
      gsap.fromTo(line, { scaleX: 0 }, { scaleX: 1, ease: 'none', scrollTrigger: { trigger: article, start: 'top top', end: 'bottom bottom', scrub: 0.3 } });
    }
  }

  /* the blog's filters settle the list rather than snapping it */
  document.querySelectorAll('.pg-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var rows = [].slice.call(document.querySelectorAll('#pgPosts li')).filter(function (r) { return !r.hidden; });
      gsap.fromTo(rows, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: EASE, stagger: 0.05, clearProps: 'opacity,transform' });
    });
  });

  window.MOTION = true;                    // service-page.js leaves the reveal to us
})();
