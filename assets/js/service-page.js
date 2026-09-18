// Ascend service pages: three animations, and nothing else.
//   1 · a single reveal as each block arrives
//   2 · the turn, where the page moves from paper to graphite and back
//   3 · a slow settle on the image inside the dark stretch
// All of it stops under prefers-reduced-motion, which leaves the finished state.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── 1 · reveal ────────────────────────────────────────────────────────────
  // When motion.js is present it owns the reveal (masked lines, image wipes);
  // this is the plain fallback for when it is not.
  var targets = window.MOTION ? [] : [].slice.call(document.querySelectorAll('.rv'));
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var show = function (el) {
      var d = parseFloat(el.getAttribute('data-rv')) || 0;
      setTimeout(function () { el.classList.add('is-in'); }, d);
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        show(en.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    // A block taller than the screen can never show 8% of itself at once, so
    // it is watched for any intersection at all; otherwise a long article on a
    // small phone would never reveal.
    var ioTall = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        ioTall.unobserve(en.target);
        show(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });
    targets.forEach(function (el) {
      // Anything already on the first screen plays on arrival rather than
      // waiting for a scroll it may never get — a tall hero can sit below the
      // observer's threshold while being the first thing anybody looks at.
      if (el.getBoundingClientRect().top < window.innerHeight * 0.92) { show(el); return; }
      (el.offsetHeight > window.innerHeight * 0.6 ? ioTall : io).observe(el);
    });
  }

  // ── 2 · the turn ──────────────────────────────────────────────────────────
  // Graphite arrives as an inset, rounded panel and opens to full bleed. The
  // type on it is light throughout, so contrast is never in question; what the
  // eye reads as "the page going dark" is the panel opening.
  var turn = document.querySelector('.sv-turn');
  if (turn) {
    // the panel arrives inset; on a phone the inset is a share of the screen, not a fixed 46px
    var INSET = Math.min(46, Math.round(window.innerWidth * 0.05)), RADIUS = Math.min(30, Math.round(window.innerWidth * 0.045));
    var setPanel = function (open) {
      var k = 1 - open;
      turn.style.setProperty('--turn-x', (INSET * k).toFixed(1) + 'px');
      turn.style.setProperty('--turn-r', (RADIUS * k).toFixed(1) + 'px');
    };

    if (reduce || typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
      setPanel(1);
    } else {
      gsap.registerPlugin(ScrollTrigger);
      setPanel(0);
      ScrollTrigger.create({
        trigger: turn, start: 'top 94%', end: 'top 52%', scrub: 0.7,
        onUpdate: function (st) { setPanel(st.progress); }
      });
      ScrollTrigger.create({
        trigger: turn, start: 'bottom 56%', end: 'bottom 10%', scrub: 0.7,
        onUpdate: function (st) { setPanel(1 - st.progress); }
      });

      // ── 3 · the settle ──────────────────────────────────────────────────
      var art = turn.querySelector('.sv-stage img');
      if (art) {
        gsap.fromTo(art, { scale: 1.04 }, {
          scale: 1, ease: 'none',
          scrollTrigger: { trigger: art, start: 'top 92%', end: 'bottom 45%', scrub: 0.8 }
        });
      }
    }
  }

  // ── questions ─────────────────────────────────────────────────────────────
  [].slice.call(document.querySelectorAll('.sv-q button')).forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.parentElement, open = item.classList.contains('is-open');
      [].slice.call(document.querySelectorAll('.sv-q.is-open')).forEach(function (o) {
        o.classList.remove('is-open');
        o.querySelector('button').setAttribute('aria-expanded', 'false');
      });
      if (!open) { item.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); }
    });
  });
})();
