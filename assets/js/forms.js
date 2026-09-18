/* Forms: the footer newsletter on every page, and the contact form.
   Submissions go to the site's own relay (/api/forms/submit), which hands them
   to the same intake the production site uses. A page only says "sent" when
   the intake accepted it; anything else is reported as what it is. */
(function () {
  'use strict';
  var here = document.currentScript;
  var ROOT = (here && here.getAttribute('data-root')) || './';
  var ENDPOINT = ROOT.replace(/\/?$/, '/') + 'api/forms/submit';
  var FALLBACK = 'hello@ascendgpartners.com';
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function send(payload) {
    payload.pageUrl = location.href;
    return fetch(ENDPOINT, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { return r.text().then(function (t) { var j; try { j = JSON.parse(t); } catch (e) { j = {}; } return { ok: r.ok && j.ok !== false, status: r.status, json: j }; }); })
      .catch(function () { return { ok: false, status: 0, json: {} }; });
  }
  function failText(res) {
    if (res.json && res.json.error) return res.json.error;
    return 'This could not be sent right now. Email ' + FALLBACK + ' and we will reply directly.';
  }

  /* ---- footer newsletter (shared chrome; the markup stays as it is) ---- */
  document.querySelectorAll('.footer-email').forEach(function (box) {
    var input = box.querySelector('input[type="email"]');
    var button = box.querySelector('button');
    if (!input || !button) return;
    var label = button.textContent;
    var msg = document.createElement('p');
    msg.setAttribute('role', 'status'); msg.setAttribute('aria-live', 'polite');
    msg.style.cssText = 'margin:0.55rem 0 0;font-size:0.8rem;line-height:1.45;opacity:0.85;display:none';
    box.insertAdjacentElement('afterend', msg);
    var busy = false;
    function note(text, bad) { msg.textContent = text; msg.style.display = text ? 'block' : 'none'; msg.style.color = bad ? '#ff8a6c' : 'inherit'; }
    function go() {
      if (busy) return;
      var email = input.value.trim();
      if (!EMAIL.test(email)) { note('Please enter a valid email address.', true); input.focus(); return; }
      busy = true; button.disabled = true; button.textContent = 'Sending…'; note('');
      send({ formId: 'newsletter', email: email, website: '' }).then(function (res) {
        busy = false; button.disabled = false;
        if (res.ok) { button.textContent = 'Done'; input.value = ''; note(res.json.message || 'Subscribed. Thank you.'); }
        else { button.textContent = label; note(failText(res), true); }
      });
    }
    button.addEventListener('click', function (e) { e.preventDefault(); go(); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); go(); } });
  });

  /* ---- contact form ---- */
  var form = document.querySelector('form[data-form-id]');
  if (!form) return;
  var status = form.querySelector('[data-form-status]');
  var submit = form.querySelector('button[type="submit"]');
  var submitLabel = submit ? submit.textContent : '';

  function fieldError(field, text) {
    var wrap = field.closest('.pg-field') || field.parentNode;
    var err = wrap.querySelector('.pg-field-error');
    if (!err) { err = document.createElement('p'); err.className = 'pg-field-error'; err.id = field.id + '-error'; wrap.appendChild(err); }
    err.textContent = text || '';
    err.hidden = !text;
    field.setAttribute('aria-invalid', text ? 'true' : 'false');
    if (text) field.setAttribute('aria-describedby', err.id); else field.removeAttribute('aria-describedby');
  }
  function validate() {
    var first = null;
    form.querySelectorAll('input, textarea, select').forEach(function (f) {
      if (f.type === 'hidden' || f.type === 'checkbox' || f.type === 'radio' || f.name === 'website') return;
      var v = f.value.trim(), text = '';
      if (f.required && !v) text = 'This one is needed.';
      else if (f.type === 'email' && v && !EMAIL.test(v)) text = 'That email address does not look right.';
      else if (f.name === 'websiteUrl' && v && !/^(https?:\/\/)?[^\s.]+\.[^\s]+$/.test(v)) text = 'Enter a web address, like example.com.';
      fieldError(f, text);
      if (text && !first) first = f;
    });
    return first;
  }
  form.querySelectorAll('input, textarea, select').forEach(function (f) {
    f.addEventListener('input', function () { if (f.getAttribute('aria-invalid') === 'true') fieldError(f, ''); });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = validate();
    if (bad) { bad.focus(); if (status) { status.textContent = 'Please check the highlighted fields.'; status.className = 'pg-form-status is-error'; } return; }
    var data = { formId: form.getAttribute('data-form-id'), website: '' };
    var fd = new FormData(form);
    fd.forEach(function (v, k) {
      if (k === 'services') { (data.services = data.services || []).push(v); }
      else data[k] = v;
    });
    if (submit) { submit.disabled = true; submit.textContent = 'Sending…'; }
    if (status) { status.textContent = ''; status.className = 'pg-form-status'; }
    send(data).then(function (res) {
      if (res.ok) {
        var done = form.querySelector('[data-form-done]');
        var text = res.json.message || form.getAttribute('data-success') || 'Thanks. We received it and will get back to you soon.';
        form.reset();
        if (done) { done.querySelector('p').textContent = text; form.classList.add('is-sent'); done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus(); }
        if (submit) { submit.disabled = false; submit.textContent = submitLabel; }
      } else {
        if (submit) { submit.disabled = false; submit.textContent = submitLabel; }
        if (status) { status.textContent = failText(res); status.className = 'pg-form-status is-error'; }
      }
    });
  });
})();
