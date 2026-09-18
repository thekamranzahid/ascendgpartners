// Services: scroll-driven stacked cards.
// Pure scroll mapping: every card position is computed directly from the
// scroll offset each frame (no springs, no tilt, no overshoot), so the stack
// is perfectly stable. Each pinned card holds for 62% of its step, then the
// next card rises over it through the remaining 38%; waiting cards sit in a
// slim fan of peeks below the active card.
(function () {
  var stack = document.getElementById('shipStack');
  if (!stack) return;
  var cards = Array.prototype.slice.call(stack.querySelectorAll('.ship-card'));
  var N = cards.length;
  if (!N) return;

  var STEP = 0.88;   // scroll distance per card, in viewport heights
  var PIN_T = 0.115; // pinned card top
  var CARD_H = 0.76; // card height (matches CSS)
  var PEEK = 0.047;  // fan spacing below the active card
  var TAIL = 0.45;   // hold after the last card arrives

  function sizeStack() {
    stack.style.height = (100 + (N - 1) * STEP * 100 + TAIL * 100) + 'vh';
  }
  sizeStack();
  window.addEventListener('resize', sizeStack);

  var running = false;
  var rafId = 0;
  function frame() {
    var vh = window.innerHeight;
    var local = (-stack.getBoundingClientRect().top) / (STEP * vh);
    if (local < 0) local = 0;
    var f = local - Math.floor(local);
    var eased = f < 0.62 ? 0 : (f - 0.62) / 0.38;
    local = Math.floor(local) + eased;
    var fan0 = (PIN_T + CARD_H) * vh;
    for (var i = 0; i < N; i++) {
      var d = i - local; // distance from this card's pin moment, in steps
      var y, scale;
      if (d <= 0) {
        y = PIN_T * vh;
        scale = 1 - 0.015 * Math.min(-d, 2); // recede slightly once covered
      } else if (d <= 1) {
        y = PIN_T * vh + (fan0 - PIN_T * vh) * d; // scrub up from the fan
        scale = 1 - 0.018 * d;
      } else {
        y = fan0 + (d - 1) * PEEK * vh; // waiting in the fan
        scale = 0.982 - 0.014 * Math.min(d - 1, 2.5);
      }
      cards[i].style.transform =
        'translate3d(-50%,' + y.toFixed(2) + 'px,0) scale(' + scale.toFixed(4) + ')';
    }
    if (running) rafId = requestAnimationFrame(frame);
  }
  // drive the stack only while it is on screen
  var io = new IntersectionObserver(function (entries) {
    var vis = entries[0].isIntersecting;
    if (vis && !running) { running = true; rafId = requestAnimationFrame(frame); }
    else if (!vis && running) { running = false; cancelAnimationFrame(rafId); }
  }, { rootMargin: '120px 0px' });
  io.observe(stack);
})();
