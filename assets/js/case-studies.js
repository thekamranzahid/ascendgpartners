// Case Studies page: shares the homepage's nav/footer behaviors, adds filters.

// CUSTOM CURSOR
const cursor = document.getElementById('cursor');
let cursorX = 0, cursorY = 0, clientX = 0, clientY = 0;
document.addEventListener('mousemove', e => { clientX = e.clientX; clientY = e.clientY; });
(function updateCursor() {
  cursorX += (clientX - cursorX) * 0.15;
  cursorY += (clientY - cursorY) * 0.15;
  cursor.style.left = cursorX + 'px';
  cursor.style.top = cursorY + 'px';
  requestAnimationFrame(updateCursor);
})();
document.querySelectorAll('a, button').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
  el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
});

// NAV SCROLL
window.addEventListener('scroll', () => {
  document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 20);
});

// MOBILE HAMBURGER + DRAWER
const navEl = document.getElementById('nav');
const hamburger = document.getElementById('navHamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => navEl.classList.toggle('menu-open'));
}
document.querySelectorAll('.nav-mb-section-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const section = btn.getAttribute('data-section');
    const list = document.querySelector(`[data-section-list="${section}"]`);
    const isOpen = btn.classList.contains('open');
    document.querySelectorAll('.nav-mb-section-btn').forEach(b => b.classList.remove('open'));
    document.querySelectorAll('.nav-mb-sublist').forEach(l => l.classList.remove('open'));
    if (!isOpen) { btn.classList.add('open'); if (list) list.classList.add('open'); }
  });
});
document.querySelectorAll('.nav-mobile-drawer a').forEach(a => {
  a.addEventListener('click', () => navEl.classList.remove('menu-open'));
});

// SCROLL REVEAL
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => observer.observe(el));

// WORD-MASK REVEALS — section headings use the homepage entrance
var rvReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
(function () {
  var els = document.querySelectorAll('.rv-words');
  if (!els.length || rvReduce) return;
  els.forEach(function (el) {
    var idx = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var parts = child.textContent.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
            var w = document.createElement('span'); w.className = 'rv-w';
            var wi = document.createElement('span'); wi.className = 'rv-wi';
            wi.textContent = p;
            wi.style.transitionDelay = (idx++ * 0.055) + 's';
            w.appendChild(wi); frag.appendChild(w);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && child.tagName !== 'BR') walk(child);
      });
    })(el);
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        en.target.classList.add('rv-on');
        setTimeout(function () { en.target.classList.add('rv-done'); }, 2100);
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0.25, rootMargin: '0px 0px -8% 0px' });
  els.forEach(function (el) { io.observe(el); });
})();

// CHAPTERS — image reveals, parallax, contents scroll-spy, chapter rail, filters
(function () {
  var chapters = Array.prototype.slice.call(document.querySelectorAll('.ed-ch'));
  if (!chapters.length) return;
  var hasGsap = typeof window.gsap !== 'undefined';
  var figs = Array.prototype.slice.call(document.querySelectorAll('.ed-fig'));
  var indexLinks = Array.prototype.slice.call(document.querySelectorAll('.ed-index a, .ed-rail a'));
  var rail = document.getElementById('edRail');
  var deck = document.getElementById('edDeck');

  // image reveal: a slow clip wipe + settle, once, as each figure arrives
  var revealIo = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var fig = en.target;
      revealIo.unobserve(fig);
      if (hasGsap && !rvReduce) {
        gsap.fromTo(fig, { clipPath: 'inset(7% 0 0 0)', opacity: 0 },
          { clipPath: 'inset(0% 0 0 0)', opacity: 1, duration: 1.15, ease: 'expo.out', clearProps: 'clip-path' });
        gsap.fromTo(fig.querySelector('img'), { scale: 1.08 }, { scale: 1, duration: 1.4, ease: 'expo.out' });
      } else {
        fig.style.opacity = '1';
      }
    });
  }, { threshold: 0.18 });
  figs.forEach(function (f) { revealIo.observe(f); });

  // parallax: figures drift a few percent against scroll while on screen
  if (!rvReduce) {
    var visible = new Set();
    var pxIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.isIntersecting ? visible.add(en.target) : visible.delete(en.target); });
    });
    figs.forEach(function (f) { pxIo.observe(f); });
    var ticking = false;
    function drift() {
      ticking = false;
      var vh = window.innerHeight;
      visible.forEach(function (fig) {
        var r = fig.getBoundingClientRect();
        var p = (r.top + r.height / 2 - vh / 2) / vh; // -1 .. 1
        fig.querySelector('img').style.translate = '0 ' + (p * 6).toFixed(2) + '%';
      });
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(drift); }
    }, { passive: true });
    drift();
  }

  // scroll-spy: highlight the current chapter in the contents and the rail
  function setActive(id) {
    indexLinks.forEach(function (a) { a.classList.toggle('active', a.getAttribute('data-ch') === id); });
  }
  var spyIo = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) setActive(en.target.id.replace('ch-', ''));
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  chapters.forEach(function (c) { spyIo.observe(c); });

  // rail only lives while the pages deck is on screen
  if (rail && deck) {
    var railIo = new IntersectionObserver(function (entries) {
      rail.classList.toggle('show', entries[0].isIntersecting);
    }, { rootMargin: '-15% 0px -15% 0px' });
    railIo.observe(deck);
  }

  // filters: chapters outside the category fold away, contents rows dim
  var pills = document.querySelectorAll('.cs-filter');
  var empty = document.getElementById('edEmpty');
  var filtering = false;
  pills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      if (filtering) return;
      pills.forEach(function (p) { p.classList.remove('active'); });
      pill.classList.add('active');
      var f = pill.getAttribute('data-filter');
      var shown = 0;
      filtering = true;
      chapters.forEach(function (ch) {
        var match = f === 'all' || ch.getAttribute('data-tags').split(' ').indexOf(f) !== -1;
        var id = ch.id.replace('ch-', '');
        document.querySelectorAll('.ed-index a[data-ch="' + id + '"], .ed-rail a[data-ch="' + id + '"]')
          .forEach(function (a) { a.classList.toggle('dim', !match); });
        if (match) shown++;
        if (hasGsap && !rvReduce) {
          if (match && ch.classList.contains('is-hidden')) {
            ch.classList.remove('is-hidden');
            gsap.fromTo(ch, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'expo.out', clearProps: 'all' });
          } else if (!match && !ch.classList.contains('is-hidden')) {
            gsap.to(ch, { autoAlpha: 0, duration: 0.22, ease: 'power2.in', onComplete: function () {
              ch.classList.add('is-hidden'); gsap.set(ch, { clearProps: 'all' });
            } });
          }
        } else {
          ch.classList.toggle('is-hidden', !match);
        }
      });
      if (empty) empty.hidden = shown > 0;
      setTimeout(function () { filtering = false; }, 320);
    });
  });
})();

// FOOTER TYPEWRITER — same one-shot reveal as the homepage
(function () {
  var giant = document.querySelector('.footer-giant');
  if (!giant) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var span = giant.querySelector('span');
  var text = span.textContent;
  span.textContent = '';
  var letters = [];
  for (var i = 0; i < text.length; i++) {
    var l = document.createElement('i');
    l.className = 'ft-letter';
    l.textContent = text[i] === ' ' ? ' ' : text[i];
    span.appendChild(l);
    letters.push(l);
  }
  giant.classList.add('type-ready');
  var played = false;
  var io = new IntersectionObserver(function (entries) {
    if (played || !entries[0].isIntersecting) return;
    played = true;
    io.disconnect();
    letters.forEach(function (el, idx) {
      setTimeout(function () { el.classList.add('on'); }, 100 + idx * 26);
    });
  }, { threshold: 0.35 });
  io.observe(giant);
})();

// SMOOTH WHEEL SCROLL (desktop pointers; touch keeps native momentum)
if (window.matchMedia('(pointer: fine)').matches) {
  let smoothTarget = 0;
  let smoothCurrent = 0;
  let smoothActive = false;
  const maxScroll = () => document.documentElement.scrollHeight - window.innerHeight;
  window.addEventListener('wheel', (e) => {
    if (e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    const delta = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
    if (!smoothActive) { smoothTarget = window.scrollY; smoothCurrent = window.scrollY; }
    smoothTarget = Math.max(0, Math.min(smoothTarget + delta, maxScroll()));
    if (!smoothActive) { smoothActive = true; requestAnimationFrame(smoothStep); }
  }, { passive: false });
  function smoothStep() {
    smoothCurrent += (smoothTarget - smoothCurrent) * 0.11;
    if (Math.abs(smoothTarget - smoothCurrent) < 0.6) {
      window.scrollTo({ top: smoothTarget, behavior: 'instant' });
      smoothActive = false;
      return;
    }
    window.scrollTo({ top: smoothCurrent, behavior: 'instant' });
    requestAnimationFrame(smoothStep);
  }
}
