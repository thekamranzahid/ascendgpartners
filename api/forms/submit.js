// Relay for the site's forms.
//
// The pages post JSON here; this forwards it, as the multipart form the
// production site's own pages send, to the same intake that handles submissions
// on ascendgpartners.com. Nothing is stored here and nothing is invented: the
// upstream's answer is returned as-is, so the page only reports success when
// the intake actually accepted the submission.
const UPSTREAM = 'https://ascendgpartners.com/api/forms/submit';

// Only the fields the intake knows about are relayed, so this cannot be used as
// an open relay for anything else.
const FIELDS = ['formId', 'pageUrl', 'website', 'firstName', 'lastName', 'email', 'phone', 'city',
                'company', 'jobTitle', 'websiteUrl', 'interest', 'services', 'message'];
const FORMS = ['contact', 'newsletter'];
const MAX_BYTES = 32 * 1024;

function readBody(req) {
  if (req.body !== undefined) return Promise.resolve(req.body);
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on('data', c => { size += c.length; if (size > MAX_BYTES) { reject(new Error('too large')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ error: 'Method not allowed' }); }

  let data;
  try {
    const raw = await readBody(req);
    data = typeof raw === 'string' ? JSON.parse(raw || '{}') : (raw || {});
  } catch (e) {
    return res.status(400).json({ error: 'Could not read the submission.' });
  }
  if (!data || typeof data !== 'object' || !FORMS.includes(data.formId)) {
    return res.status(400).json({ error: 'Unknown form.' });
  }
  const email = String(data.email || '').trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return res.status(400).json({ error: 'Please enter a valid email address.' });

  const form = new FormData();
  for (const key of FIELDS) {
    const v = data[key];
    if (v === undefined || v === null) continue;
    if (Array.isArray(v)) v.forEach(x => form.append(key, String(x).slice(0, 2000)));
    else form.append(key, String(v).slice(0, 5000));
  }

  let upstream;
  try {
    upstream = await fetch(UPSTREAM, { method: 'POST', body: form, headers: { 'user-agent': 'ascendgpartners.vercel.app forms relay' } });
  } catch (e) {
    return res.status(502).json({ error: 'The intake could not be reached. Please email hello@ascendgpartners.com.' });
  }
  const text = await upstream.text();
  let json; try { json = JSON.parse(text); } catch (e) { json = null; }
  if (!upstream.ok) return res.status(upstream.status).json({ error: (json && json.error) || 'The submission was not accepted.' });
  return res.status(200).json({ ok: true, message: json && json.message ? json.message : undefined });
};
