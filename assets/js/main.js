// PRELOADER
window.addEventListener('load', () => {
  setTimeout(() => {
    document.getElementById('preloader').classList.add('done');
    animateHero();
  }, 3000);
});

// HERO ANIMATION
function animateHero() {
  const wordmark = document.querySelector('.hero-wordmark');
  const sub = document.querySelector('.hero-sub');
  const ctaRow = document.querySelector('.hero-cta-row');

  // the headline letter sweep starts the moment the lifting preloader turns
  // transparent (expo fade is mostly clear by ~320ms), so the full sweep is
  // seen with no perceived delay; the block itself appears immediately
  wordmark.style.transition = 'opacity 0.5s ease-out, transform 0.9s var(--ease-out-expo)';
  wordmark.style.opacity = '1';
  wordmark.style.transform = 'translateY(0)';
  const h1 = document.querySelector('.hero-h1-text');
  if (h1) setTimeout(() => h1.classList.add('hl-on'), 320);

  if (sub) setTimeout(() => {
    sub.style.transition = 'opacity 1s var(--ease-out-expo), transform 1s var(--ease-out-expo)';
    sub.style.opacity = '1';
    sub.style.transform = 'translateY(0)';
  }, 550);

  if (ctaRow) setTimeout(() => {
    ctaRow.style.transition = 'opacity 1s var(--ease-out-expo), transform 1s var(--ease-out-expo)';
    ctaRow.style.opacity = '1';
    ctaRow.style.transform = 'translateY(0)';
  }, 800);
}

// HERO LETTER SWEEP — split the headline into word-bound letters up front
// (runs once at parse time, so the load-time animation costs nothing)
(function () {
  const h1 = document.querySelector('.hero-h1-text');
  if (!h1) return;
  const heading = h1.closest('h1');
  if (heading) heading.setAttribute('aria-label', h1.textContent);
  h1.setAttribute('aria-hidden', 'true');
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  let idx = 0;
  (function walk(node) {
    Array.prototype.slice.call(node.childNodes).forEach(function (child) {
      if (child.nodeType === 3) {
        const parts = child.textContent.split(/(\s+)/);
        const frag = document.createDocumentFragment();
        parts.forEach(function (p) {
          if (!p) return;
          if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
          const w = document.createElement('span'); w.className = 'hl-w';
          for (let i = 0; i < p.length; i++) {
            const l = document.createElement('span'); l.className = 'hl-l';
            l.textContent = p[i];
            l.style.transitionDelay = (idx++ * 0.012) + 's';
            w.appendChild(l);
          }
          frag.appendChild(w);
        });
        node.replaceChild(frag, child);
      } else if (child.nodeType === 1) walk(child);
    });
  })(h1);
})();

// CUSTOM CURSOR
const cursor = document.getElementById('cursor');
let cursorX = 0, cursorY = 0, clientX = 0, clientY = 0;
document.addEventListener('mousemove', e => { clientX = e.clientX; clientY = e.clientY; });
function updateCursor() {
  cursorX += (clientX - cursorX) * 0.15;
  cursorY += (clientY - cursorY) * 0.15;
  cursor.style.left = cursorX + 'px';
  cursor.style.top = cursorY + 'px';
  requestAnimationFrame(updateCursor);
}
updateCursor();
document.querySelectorAll('a, button, .service-card, .testimonial-dot, .case-card, .client-cell, .btn-accent').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
  el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
});

// NAV SCROLL
window.addEventListener('scroll', () => {
  document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 20);
});

// MOBILE HAMBURGER
const navEl = document.getElementById('nav');
const hamburger = document.getElementById('navHamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    navEl.classList.toggle('menu-open');
  });
}
// Accordion sections
document.querySelectorAll('.nav-mb-section-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const section = btn.getAttribute('data-section');
    const list = document.querySelector(`[data-section-list="${section}"]`);
    const isOpen = btn.classList.contains('open');
    // close all
    document.querySelectorAll('.nav-mb-section-btn').forEach(b => b.classList.remove('open'));
    document.querySelectorAll('.nav-mb-sublist').forEach(l => l.classList.remove('open'));
    // open clicked
    if (!isOpen) { btn.classList.add('open'); if (list) list.classList.add('open'); }
  });
});
// Close menu on link click
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

// PARALLAX ON HERO
window.addEventListener('scroll', () => {
  const s = window.scrollY;
  const hero = document.querySelector('.hero-content');
  if (s < window.innerHeight) {
    hero.style.transform = `translateY(${s * 0.25}px)`;
    hero.style.opacity = 1 - (s / window.innerHeight) * 0.7;
  }
});

// SCROLL INDICATOR
// The hero scroll control is a hash anchor. /smooth-scroll.js intercepts it for animated scrolling.

// STATS COUNTER
const statsObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('.stat-val').forEach(el => {
        const target = parseInt(el.dataset.target);
        animateNum(el, target);
      });
      statsObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stats-bar').forEach(el => statsObs.observe(el));

function animateNum(el, end) {
  let start = null;
  function step(ts) {
    if (!start) start = ts;
    const p = Math.min((ts - start) / 1800, 1);
    const eased = 1 - Math.pow(1 - p, 4);
    el.textContent = Math.floor(eased * end) + '%';
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// WORD-MASK REVEALS — display headings rise word by word behind clip masks,
// once, when scrolled into view. The hero headline cascades after the
// preloader instead, in step with its block animation.
(function () {
  var els = document.querySelectorAll('.rv-words');
  if (!els.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

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
        } else if (child.nodeType === 1 && child.tagName !== 'BR') {
          walk(child);
        }
      });
    })(el);
  });

  function arm(el) {
    el.classList.add('rv-on');
    setTimeout(function () { el.classList.add('rv-done'); }, 2100);
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { arm(en.target); io.unobserve(en.target); }
    });
  }, { threshold: 0.25, rootMargin: '0px 0px -8% 0px' });

  var hero = null;
  els.forEach(function (el) {
    if (el.closest('.hero')) { hero = el; } else { io.observe(el); }
  });
  // hero cascade fires as the preloader lifts (load + 3000ms + wordmark's 200ms)
  if (hero) {
    window.addEventListener('load', function () {
      setTimeout(function () { arm(hero); }, 3250);
    });
  }
})();

// FOOTER TYPEWRITER — the giant lockup types in letter by letter, once,
// the first time it scrolls into view; static forever after.
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
    if (e.ctrlKey || e.metaKey) return; // keep zoom gestures native
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
