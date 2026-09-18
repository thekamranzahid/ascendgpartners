// Case study pages: reading progress, hero parallax, stat count-ups.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGsap = typeof window.gsap !== 'undefined';

  // reading progress line + parallax for every figure on screen
  var bar = document.getElementById('bkProgress');
  var figs = Array.prototype.slice.call(document.querySelectorAll('.bk-fig'));
  var ticking = false;
  function onScroll() {
    ticking = false;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, window.scrollY / max) : 0) + ')';
    if (reduce) return;
    figs.forEach(function (fig) {
      var r = fig.getBoundingClientRect();
      if (r.bottom <= 0 || r.top >= window.innerHeight) return;
      var p = (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight;
      var img = fig.querySelector('img');
      if (img) img.style.translate = '0 ' + (p * 6).toFixed(2) + '%';
    });
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  // figure reveals: clip-wipe + settle; the first on load, the rest as they arrive
  function revealFig(fig, delay) {
    var img = fig.querySelector('img');
    if (hasGsap && !reduce) {
      gsap.fromTo(fig, { clipPath: 'inset(6% 0 0 0)', opacity: 0 },
        { clipPath: 'inset(0% 0 0 0)', opacity: 1, duration: 1.3, ease: 'expo.out', delay: delay, clearProps: 'clip-path' });
      if (img) gsap.fromTo(img, { scale: 1.08 }, { scale: 1, duration: 1.6, ease: 'expo.out', delay: delay });
    } else {
      fig.style.opacity = '1';
    }
  }
  if (figs.length) {
    revealFig(figs[0], 0.35);
    var figIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        figIo.unobserve(en.target);
        revealFig(en.target, 0);
      });
    }, { threshold: 0.15 });
    figs.slice(1).forEach(function (f) { figIo.observe(f); });
  }

  // count-ups: numbers roll to their value the first time the strip is seen
  var counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;
  function run(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var prefix = el.getAttribute('data-prefix') || '';
    var suffix = el.getAttribute('data-suffix') || '';
    var out = el.querySelector('b');
    if (reduce || !hasGsap) { out.textContent = prefix + (el.hasAttribute('data-comma') ? target.toLocaleString('en-US') : target) + suffix; return; }
    var obj = { v: 0 };
    gsap.to(obj, {
      v: target, duration: 1.6, ease: 'expo.out',
      onUpdate: function () { var n = Math.round(obj.v); out.textContent = prefix + (el.hasAttribute('data-comma') ? n.toLocaleString('en-US') : n) + suffix; }
    });
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      io.unobserve(en.target);
      run(en.target);
    });
  }, { threshold: 0.4 });
  counters.forEach(function (c) { io.observe(c); });
})();
