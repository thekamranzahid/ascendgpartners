// Hero background: 3D particle-wave field (recreated from reference video).
// A single dotted sheet displaced by layered simplex noise, viewed from inside
// the wave band at a grazing angle. Luminance follows surface steepness (screen
// compression), so folds glow as cyan strings while face-on regions fall to
// near-black — matching the reference's measured palette (dim ~rgb(8,25,40) ->
// mid ~rgb(40,87,100) -> ridge ~rgb(79,173,177) -> peak ~rgb(86,220,219)),
// dot scale (~0.5% of width), string pitch (~1.15%), slow in-place morph with
// ~1.5%/s lateral drift, static camera.
(function () {
  var canvas = document.getElementById('heroWave');
  if (!canvas) return;
  var gl = canvas.getContext('webgl', { antialias: false, alpha: true, powerPreference: 'high-performance' })
        || canvas.getContext('experimental-webgl');
  if (!gl) { canvas.style.display = 'none'; return; }

  var VERT = [
    'precision highp float;',
    'attribute vec2 aGrid;',            // grid coords: x in [-1,1], y in [0,1] (near->far)
    'uniform float uTime;',
    'uniform vec2  uRes;',
    'uniform vec2  uPointer;',          // eased pointer, [-1,1]
    'varying float vLum;',
    'varying float vHeight;',

    // --- simplex noise (Ashima Arts / Stefan Gustavson, MIT) ---
    'vec3 mod289(vec3 x){return x - floor(x * (1.0/289.0)) * 289.0;}',
    'vec4 mod289(vec4 x){return x - floor(x * (1.0/289.0)) * 289.0;}',
    'vec4 permute(vec4 x){return mod289(((x*34.0)+1.0)*x);}',
    'vec4 taylorInvSqrt(vec4 r){return 1.79284291400159 - 0.85373472095314 * r;}',
    'float snoise(vec3 v){',
    '  const vec2 C = vec2(1.0/6.0, 1.0/3.0);',
    '  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);',
    '  vec3 i  = floor(v + dot(v, C.yyy));',
    '  vec3 x0 = v - i + dot(i, C.xxx);',
    '  vec3 g = step(x0.yzx, x0.xyz);',
    '  vec3 l = 1.0 - g;',
    '  vec3 i1 = min(g.xyz, l.zxy);',
    '  vec3 i2 = max(g.xyz, l.zxy);',
    '  vec3 x1 = x0 - i1 + C.xxx;',
    '  vec3 x2 = x0 - i2 + C.yyy;',
    '  vec3 x3 = x0 - D.yyy;',
    '  i = mod289(i);',
    '  vec4 p = permute(permute(permute(i.z + vec4(0.0, i1.z, i2.z, 1.0)) + i.y + vec4(0.0, i1.y, i2.y, 1.0)) + i.x + vec4(0.0, i1.x, i2.x, 1.0));',
    '  float n_ = 0.142857142857;',
    '  vec3 ns = n_ * D.wyz - D.xzx;',
    '  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);',
    '  vec4 x_ = floor(j * ns.z);',
    '  vec4 y_ = floor(j - 7.0 * x_);',
    '  vec4 x = x_ * ns.x + ns.yyyy;',
    '  vec4 y = y_ * ns.x + ns.yyyy;',
    '  vec4 h = 1.0 - abs(x) - abs(y);',
    '  vec4 b0 = vec4(x.xy, y.xy);',
    '  vec4 b1 = vec4(x.zw, y.zw);',
    '  vec4 s0 = floor(b0) * 2.0 + 1.0;',
    '  vec4 s1 = floor(b1) * 2.0 + 1.0;',
    '  vec4 sh = -step(h, vec4(0.0));',
    '  vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;',
    '  vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;',
    '  vec3 p0 = vec3(a0.xy, h.x);',
    '  vec3 p1 = vec3(a0.zw, h.y);',
    '  vec3 p2 = vec3(a1.xy, h.z);',
    '  vec3 p3 = vec3(a1.zw, h.w);',
    '  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));',
    '  p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;',
    '  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);',
    '  m = m * m;',
    '  return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));',
    '}',

    'float surface(vec2 p, float t){',
    // large silk folds
    '  float h = 0.70 * snoise(vec3(p * 0.52, t * 0.12));',
    '  h += 0.46 * snoise(vec3(p * 1.35 + vec2(11.7, 3.1), t * 0.17));',
    // patchy fine ripples, gated by a slow mask
    '  float gate = smoothstep(0.05, 0.75, snoise(vec3(p * 0.70 + vec2(4.2, 9.3), t * 0.08)));',
    '  h += gate * 0.050 * snoise(vec3(p * 7.5, t * 0.16));',
    '  return h;',
    '}',

    'void main(){',
    '  float t = uTime;',
    // sheet coords: u along strings (screen-x), v across strings
    '  float u = aGrid.x * 1.15;',
    '  float vN = aGrid.y * 2.0 - 1.0;',
    // resolution anchoring: the reference video is 1338px wide; base row
    // pitch (6.7px; the mapping stretches it to the ~15px face-on spacing),
    // fold amplitude (374px) and dot size all scale with width so the effect
    // renders as a cover-fit of the reference at any viewport
    '  float refS = uRes.x / 1338.0;',
    '  float halfH = uRes.y * 0.5;',
    '  float v = vN * 1.75;',
    // slight diagonal so strings sweep like the reference
    '  vec2 sp = vec2(u * 0.940 - v * 0.342, u * 0.342 + v * 0.940);',
    '  vec2 wp = sp * 1.15 + vec2(t * 0.020, 0.0);',
    '  float h = surface(wp, t);',
    '  vHeight = h;',
    // near-edge-on sheet: screen-y = sheet position + fold height.
    // where successive rows land on the same y the mapping folds over
    // itself and additive stacking draws the bright caustic strings.
    '  float sx = u * 1.02 + h * 0.115 + uPointer.x * 0.006;',
    '  float syPx = vN * 120.0 * 6.7 * refS + h * 374.0 * refS;',
    '  float sy = (syPx + uPointer.y * -4.0 * refS) / halfH;',
    '  gl_Position = vec4(sx, -sy, 0.0, 1.0);',
    '  float edgeFade = 1.0 - smoothstep(0.60, 0.97, abs(sy));',
    // mild depth cue: high folds sit closer -> slightly larger dots
    '  float hN = smoothstep(-1.1, 1.1, h);',
    '  float px = uRes.x / 1338.0;',
    '  gl_PointSize = clamp((5.2 + 3.0 * hN - 1.8 * vN) * px, 2.0, 9.5 * px);',
    // per-dot luminance dim; caustic stacking creates the ridge glow
    '  vLum = (0.125 + 0.235 * pow(hN, 1.9) - 0.065 * vN) * edgeFade;',
    '}'
  ].join('\n');

  var FRAG = [
    'precision mediump float;',
    'varying float vLum;',
    'varying float vHeight;',
    'void main(){',
    '  vec2 uv = gl_PointCoord.xy - 0.5;',
    '  float r = length(uv) * 2.0;',
    '  float core = smoothstep(1.0, 0.62, r);',
    '  if (core <= 0.004) discard;',
    // palette: dim blue -> teal -> cyan (measured ramp); additive stacking
    // pushes compressed folds toward rgb(86,220,219)
    '  float hn = smoothstep(-0.55, 0.85, vHeight);',
    '  vec3 deep = vec3(0.059, 0.082, 0.208);',
    '  vec3 teal = vec3(0.106, 0.204, 0.671);',
    '  vec3 cyan = vec3(0.152, 0.278, 0.900);',
    '  vec3 col = mix(deep, teal, smoothstep(0.10, 0.62, hn));',
    '  col = mix(col, cyan, smoothstep(0.55, 0.97, hn));',
    '  gl_FragColor = vec4(col * vLum * core, 1.0);',
    '}'
  ].join('\n');

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      throw new Error(gl.getShaderInfoLog(s));
    }
    return s;
  }
  var prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    canvas.style.display = 'none';
    return;
  }
  gl.useProgram(prog);

  // grid: string pitch ~15px @1338w at mid-depth
  var COLS = 168, ROWS = 241, N = COLS * ROWS;
  var grid = new Float32Array(N * 2);
  var k = 0;
  for (var j = 0; j < ROWS; j++) {
    for (var i = 0; i < COLS; i++) {
      grid[k++] = (i / (COLS - 1)) * 2.0 - 1.0;
      grid[k++] = j / (ROWS - 1);
    }
  }
  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, grid, gl.STATIC_DRAW);
  var aGrid = gl.getAttribLocation(prog, 'aGrid');
  gl.enableVertexAttribArray(aGrid);
  gl.vertexAttribPointer(aGrid, 2, gl.FLOAT, false, 0, 0);

  var uTime = gl.getUniformLocation(prog, 'uTime');
  var uRes = gl.getUniformLocation(prog, 'uRes');
  var uPointer = gl.getUniformLocation(prog, 'uPointer');

  gl.disable(gl.DEPTH_TEST);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE);           // additive
  gl.clearColor(0, 0, 0, 0);

  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  function resize() {
    var w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    var W = Math.round(w * dpr), H = Math.round(h * dpr);
    if (canvas.width !== W || canvas.height !== H) {
      canvas.width = W; canvas.height = H;
      gl.viewport(0, 0, W, H);
    }
  }
  window.addEventListener('resize', resize);

  // subtle hover: heavily eased pointer -> few-px camera drift only
  var tx = 0, ty = 0, px = 0, py = 0;
  window.addEventListener('mousemove', function (e) {
    tx = (e.clientX / window.innerWidth) * 2 - 1;
    ty = (e.clientY / window.innerHeight) * 2 - 1;
  });

  var start = performance.now();
  var running = false;
  var rafId = 0;
  function frame(now) {
    resize();
    px += (tx - px) * 0.025;
    py += (ty - py) * 0.025;
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(uTime, (now - start) / 1000);
    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform2f(uPointer, px, py);
    gl.drawArrays(gl.POINTS, 0, N);
    if (running) rafId = requestAnimationFrame(frame);
  }
  // render only while the hero is on screen; the field sleeps otherwise
  var io = new IntersectionObserver(function (entries) {
    var vis = entries[0].isIntersecting;
    if (vis && !running) { running = true; rafId = requestAnimationFrame(frame); }
    else if (!vis && running) { running = false; cancelAnimationFrame(rafId); }
  }, { rootMargin: '80px 0px' });
  io.observe(canvas);
})();
