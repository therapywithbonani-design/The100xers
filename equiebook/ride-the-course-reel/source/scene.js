import * as THREE from 'three';

await Promise.all(['700 40px Lora', '600 40px Lora', '500 20px Poppins', '600 20px Poppins', '700 20px Poppins'].map(f => document.fonts.load(f)));
const Q = new URLSearchParams(location.search);
const W = +(Q.get('w') || 1080), H = +(Q.get('h') || 1920);
const K = W / 1080;               // HUD design scale (design space 1080x1920)
const FPS = 30;
const SHADOW = +(Q.get('shadow') || 2048);

// ---------- brand ----------
const C = { dark: '#1A1510', gold: '#C9A96E', lgold: '#D4BE8A', cream: '#F5F0E8' };

// ---------- deterministic random ----------
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
const R = rng(7);
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, t) => a + (b - a) * t;
const easeOutBack = x => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };

// =====================================================================
// COURSE PATH
// =====================================================================
const J = 2.9;           // half-length of jump arc (m)
const JH = 1.05;         // camera rise over fence (m)
const V = 9.0;           // canter speed (m/s)
const segs = [
  { t: 'S', len: 52, fences: [{ at: 12, n: '1', type: 'vertical', col: 0 }, { at: 30, n: '2', type: 'oxer', col: 1 }, { at: 47, n: '3', type: 'wall', col: 2 }] },
  { t: 'A', dir: +1, ang: Math.PI, r: 9, prompt: 'LEFT' },
  { t: 'S', len: 40, fences: [{ at: 10, n: '4', type: 'oxer', col: 3 }, { at: 25, n: '5A', type: 'vertical', col: 0 }, { at: 32.6, n: '5B', type: 'oxer', col: 0 }] },
  { t: 'A', dir: -1, ang: Math.PI, r: 9, prompt: 'RIGHT' },
  { t: 'S', len: 52, fences: [{ at: 9, n: '6', type: 'vertical', col: 4 }, { at: 27, n: '7', type: 'oxer', col: 1 }] },
];
const STEP = 0.05;
const P = [];       // samples {x,z,a}
const fences = [];  // {s, n, ...}
const turns = [];   // {s0, s1, dir, prompt}
{
  let x = 0, z = 0, a = 0, s = 0;
  P.push({ x, z, a });
  for (const g of segs) {
    if (g.t === 'S') {
      for (const f of g.fences || []) fences.push({ ...f, s: s + f.at });
      const n = Math.round(g.len / STEP);
      for (let i = 0; i < n; i++) { x += Math.sin(a) * STEP; z -= Math.cos(a) * STEP; s += STEP; P.push({ x, z, a }); }
    } else {
      const L = g.ang * g.r; const n = Math.round(L / STEP);
      turns.push({ s0: s, s1: s + L, dir: g.dir, prompt: g.prompt });
      for (let i = 0; i < n; i++) { a -= g.dir * STEP / g.r; x += Math.sin(a) * STEP; z -= Math.cos(a) * STEP; s += STEP; P.push({ x, z, a }); }
    }
  }
}
const SMAX = (P.length - 1) * STEP;
function pathAt(s) {
  s = clamp(s, 0, SMAX); const f = s / STEP; const i = Math.floor(f), u = f - i; const p = P[i], q = P[Math.min(i + 1, P.length - 1)];
  return { x: lerp(p.x, q.x, u), z: lerp(p.z, q.z, u), a: lerp(p.a, q.a, u) };
}
let bb = { x0: 1e9, x1: -1e9, z0: 1e9, z1: -1e9 };
for (const p of P) { bb.x0 = Math.min(bb.x0, p.x); bb.x1 = Math.max(bb.x1, p.x); bb.z0 = Math.min(bb.z0, p.z); bb.z1 = Math.max(bb.z1, p.z); }
const M = 15; const AR = { x0: bb.x0 - M, x1: bb.x1 + M, z0: bb.z0 - M + 4, z1: bb.z1 + 10 };
const AC = { x: (AR.x0 + AR.x1) / 2, z: (AR.z0 + AR.z1) / 2 };

// =====================================================================
// TIMELINE (simulate speed profile)
// =====================================================================
const T0 = 3.9, TA = 1.2;          // start moving at T0
const lastF = fences[fences.length - 1];
const sDecel = lastF.s + J + 1.5;
const sArr = [], vArr = [];
{
  let s = 0, tDec = null;
  for (let i = 0; i < FPS * 40; i++) {
    const t = i / FPS; let v;
    if (t < T0) v = 0;
    else if (t < T0 + TA) v = V * smooth((t - T0) / TA);
    else if (s < sDecel) v = V;
    else { if (tDec === null) tDec = t; v = V * (1 - 0.78 * smooth((t - tDec) / 2.6)); }
    sArr.push(s); vArr.push(v); s += v / FPS;
  }
}
const tAtS = sv => { for (let i = 0; i < sArr.length; i++) if (sArr[i] >= sv) return i / FPS; return 99; };
for (const f of fences) { f.tTO = tAtS(f.s - J); f.tLD = tAtS(f.s + J); }
for (const tr of turns) { const prev = fences.filter(f => f.s < tr.s0).at(-1); tr.t0 = Math.max(tAtS(tr.s0 - 7), prev ? prev.tLD + 0.25 : 0); tr.t1 = Math.max(tAtS(tr.s0 + (tr.s1 - tr.s0) * 0.55), tr.t0 + 1.1); }
const tFinish = lastF.tLD;
const tClear = tFinish + 0.15;
const tEnd = tClear + 3.3;      // end card starts
const DUR = tEnd + 4.9;
const NFRAMES = Math.round(DUR * FPS);

// prompts list
const prompts = [];
prompts.push({ t0: 2.85, t1: 3.85, text: 'READY?' });
prompts.push({ t0: 3.85, t1: 4.55, text: 'GO!' });
fences.forEach((f, i) => {
  let text = 'JUMP!'; if (f.n === '5B') text = 'AGAIN!'; if (f.n === '7') text = 'LAST ONE!';
  const t0 = f.n === '5B' ? fences[i - 1].tLD - 0.05 : f.tTO - 0.8;
  prompts.push({ t0, t1: f.tLD - 0.1, text, kind: 'jump', press: f.tTO - 0.35, f });
});
for (const tr of turns) prompts.push({ t0: tr.t0, t1: tr.t1, text: tr.prompt, kind: tr.prompt === 'LEFT' ? 'left' : 'right', press: tr.t0 + 0.4 });
prompts.push({ t0: tClear, t1: tEnd + 0.1, text: 'CLEAR ROUND!', kind: 'clear' });

// =====================================================================
// RENDERER / SCENE
// =====================================================================
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = SHADOW > 0; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xe9dcc4, 70, 260);
const camera = new THREE.PerspectiveCamera(80, W / H, 0.05, 900);
scene.add(camera);

// sky
{
  const g = new THREE.SphereGeometry(600, 32, 16);
  const m = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { sun: { value: new THREE.Vector3(0.55, 0.32, 0.77).normalize() } },
    vertexShader: `varying vec3 vd; void main(){ vd = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `varying vec3 vd; uniform vec3 sun;
      void main(){ float h = clamp(vd.y,0.,1.);
        vec3 top = vec3(0.42,0.62,0.86), hor = vec3(0.98,0.90,0.78);
        vec3 c = mix(hor, top, pow(h,0.55));
        float d = max(dot(vd, sun),0.); c += vec3(1.0,0.78,0.45)*pow(d,40.)*0.6 + vec3(1.,0.85,0.6)*pow(d,6.)*0.18;
        gl_FragColor = vec4(c,1.); }`
  });
  const sky = new THREE.Mesh(g, m); sky.frustumCulled = false; scene.add(sky); camera.userData.sky = sky;
}

const sunDir = new THREE.Vector3(0.55, 0.42, 0.72).normalize();
const sun = new THREE.DirectionalLight(0xffdcb0, 3.1);
sun.castShadow = SHADOW > 0;
sun.shadow.mapSize.set(SHADOW || 1, SHADOW || 1);
Object.assign(sun.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 120 });
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03;
scene.add(sun, sun.target);
scene.add(new THREE.HemisphereLight(0xcfe0f5, 0xb89668, 1.15));

// ---------- canvas textures ----------
function canvasTex(w, h, draw, repeat) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); draw(x, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  return t;
}
const sandTex = canvasTex(512, 512, (x, w, h) => {
  x.fillStyle = '#d8b88a'; x.fillRect(0, 0, w, h); const r = rng(3);
  for (let i = 0; i < 9000; i++) { const v = r(); x.fillStyle = v < 0.5 ? `rgba(150,110,70,${0.10 + r() * 0.15})` : `rgba(255,240,215,${0.10 + r() * 0.2})`; const s = 1 + r() * 3; x.fillRect(r() * w, r() * h, s, s); }
  for (let i = 0; i < 40; i++) { x.strokeStyle = `rgba(140,100,60,${0.08 + r() * 0.08})`; x.lineWidth = 3 + r() * 6; x.beginPath(); const cx = r() * w, cy = r() * h; x.ellipse(cx, cy, 8 + r() * 10, 6 + r() * 8, r() * 3, 0, 6.28); x.stroke(); }
}, true);
sandTex.repeat.set(30, 30);
const grassTex = canvasTex(256, 256, (x, w, h) => {
  x.fillStyle = '#6e8a3c'; x.fillRect(0, 0, w, h); const r = rng(9);
  for (let i = 0; i < 6000; i++) { x.fillStyle = r() < 0.5 ? 'rgba(60,90,30,0.35)' : 'rgba(150,170,80,0.3)'; x.fillRect(r() * w, r() * h, 1 + r() * 2, 2 + r() * 3); }
}, true);
grassTex.repeat.set(120, 120);

function stripeTex(c1, c2) {
  return canvasTex(256, 16, (x, w, h) => { const n = 6; for (let i = 0; i < n; i++) { x.fillStyle = i % 2 ? c2 : c1; x.fillRect(i * w / n, 0, w / n, h); } });
}
const POLE = [['#C9A96E', '#F5F0E8'], ['#1F4E3D', '#F5F0E8'], ['#7A2E2E', '#F5F0E8'], ['#1C2B4A', '#F5F0E8'], ['#1A1510', '#C9A96E']];
const poleMats = POLE.map(([a, b]) => new THREE.MeshStandardMaterial({ map: stripeTex(a, b), roughness: 0.45 }));

function boardTex(kind) {
  return canvasTex(1024, 160, (x, w, h) => {
    if (kind === 0) {
      x.fillStyle = C.dark; x.fillRect(0, 0, w, h); x.strokeStyle = C.gold; x.lineWidth = 6; x.strokeRect(8, 8, w - 16, h - 16);
      x.fillStyle = C.gold; x.font = '700 92px Lora'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.letterSpacing = '18px'; x.fillText('EQUIEBOOK', w / 2 + 9, h / 2 + 4);
    } else if (kind === 1) {
      x.fillStyle = C.cream; x.fillRect(0, 0, w, h);
      x.fillStyle = C.dark; x.font = '600 58px Poppins'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.letterSpacing = '10px'; x.fillText('RIDE · CONNECT · DISCOVER', w / 2, h / 2 + 4);
    } else {
      x.fillStyle = '#2a3a2c'; x.fillRect(0, 0, w, h);
      x.fillStyle = C.cream; x.font = '600 64px Poppins'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.letterSpacing = '8px'; x.fillText('LIVE SCORING', w / 2 - 120, h / 2 + 4);
      x.fillStyle = C.gold; x.font = '700 64px Lora'; x.letterSpacing = '6px'; x.fillText('EQUIEBOOK', w / 2 + 290, h / 2 + 4);
    }
  });
}
const boardMats = [0, 1, 2].map(k => new THREE.MeshStandardMaterial({ map: boardTex(k), roughness: 0.7 }));
function numTex(n) {
  return canvasTex(128, 128, (x, w, h) => { x.fillStyle = '#fff'; x.fillRect(0, 0, w, h); x.fillStyle = C.dark; x.font = '700 70px Poppins'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(n, w / 2, h / 2 + 4); });
}

// ---------- ground ----------
{
  const grass = new THREE.Mesh(new THREE.PlaneGeometry(1200, 1200), new THREE.MeshStandardMaterial({ map: grassTex, roughness: 1 }));
  grass.rotation.x = -Math.PI / 2; grass.position.set(AC.x, -0.02, AC.z); grass.receiveShadow = true; scene.add(grass);
  const aw = AR.x1 - AR.x0, ad = AR.z1 - AR.z0;
  const sand = new THREE.Mesh(new THREE.PlaneGeometry(aw, ad), new THREE.MeshStandardMaterial({ map: sandTex, roughness: 0.95 }));
  sandTex.repeat.set(aw / 3.2, ad / 3.2);
  sand.rotation.x = -Math.PI / 2; sand.position.set(AC.x, 0, AC.z); sand.receiveShadow = true; scene.add(sand);
}

// ---------- arena rails + boards ----------
const white = new THREE.MeshStandardMaterial({ color: 0xf4f1ea, roughness: 0.5 });
{
  const sides = [
    [AR.x0, AR.z0, AR.x1, AR.z0], [AR.x1, AR.z0, AR.x1, AR.z1], [AR.x1, AR.z1, AR.x0, AR.z1], [AR.x0, AR.z1, AR.x0, AR.z0]];
  const postG = new THREE.BoxGeometry(0.14, 1.3, 0.14);
  let bi = 0;
  for (const [ax, az, bx, bz] of sides) {
    const L = Math.hypot(bx - ax, bz - az), ang = Math.atan2(bz - az, bx - ax);
    for (const hgt of [0.6, 1.15]) {
      const rail = new THREE.Mesh(new THREE.BoxGeometry(L, 0.12, 0.08), white);
      rail.position.set((ax + bx) / 2, hgt, (az + bz) / 2); rail.rotation.y = -ang; rail.castShadow = true; scene.add(rail);
    }
    const n = Math.floor(L / 3);
    for (let i = 0; i <= n; i++) { const p = new THREE.Mesh(postG, white); p.position.set(lerp(ax, bx, i / n), 0.65, lerp(az, bz, i / n)); scene.add(p); }
    // sponsor boards on inside
    const nb = Math.floor(L / 8.5);
    const nx = -Math.sin(ang), nz = Math.cos(ang); // inward normal (sides go clockwise?) checked below
    for (let i = 0; i < nb; i++) {
      const u = (i + 0.5) / nb; const cx = lerp(ax, bx, u), cz = lerp(az, bz, u);
      const b = new THREE.Mesh(new THREE.PlaneGeometry(6, 0.95), boardMats[bi++ % 3]);
      // point toward arena centre
      const tx = AC.x - cx, tz = AC.z - cz; const dot = tx * nx + tz * nz; const sgn = dot > 0 ? 1 : -1;
      b.position.set(cx + nx * 0.25 * sgn, 0.55, cz + nz * 0.25 * sgn);
      b.lookAt(cx + nx * sgn * 10, 0.55, cz + nz * sgn * 10);
      scene.add(b);
    }
  }
}

// ---------- fences ----------
const greenM = new THREE.MeshStandardMaterial({ color: 0x3f6b2f, roughness: 0.8 });
const flowerCols = [0xf5f0e8, 0xc9a96e, 0xb5533c, 0xe8d3a6];
const fenceObjs = [];
function makeFence(f) {
  const g = new THREE.Group(); const pm = poleMats[f.col];
  const half = 1.95;
  const poleG = new THREE.CylinderGeometry(0.055, 0.055, 3.8, 12); poleG.rotateZ(Math.PI / 2);
  const rows = f.type === 'oxer' ? [0, 1.1] : [0];
  for (const dz of rows) {
    for (const sx of [-1, 1]) {
      const st = new THREE.Mesh(new THREE.BoxGeometry(0.13, 1.75, 0.13), white); st.position.set(sx * half, 0.875, -dz); st.castShadow = true; g.add(st);
    }
    const heights = f.type === 'wall' ? [1.28] : [0.5, 0.92, 1.3];
    heights.forEach(hh => { const p = new THREE.Mesh(poleG, pm); p.position.set(0, hh + (dz ? 0.05 : 0), -dz); p.castShadow = true; g.add(p); });
  }
  // wings
  for (const sx of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.6, 0.09), new THREE.MeshStandardMaterial({ color: POLE[f.col][0], roughness: 0.6 }));
    w.position.set(sx * (half + 0.55), 0.8, -(rows.at(-1)) / 2); w.castShadow = true; g.add(w);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(0.95, 0.08, 0.14), white); cap.position.set(sx * (half + 0.55), 1.62, -(rows.at(-1)) / 2); g.add(cap);
  }
  // number plate
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.42), new THREE.MeshBasicMaterial({ map: numTex(f.n) }));
  plate.position.set(half + 0.55, 1.25, 0.07); g.add(plate);
  if (f.type === 'wall') {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(3.7, 1.05, 0.45), new THREE.MeshStandardMaterial({ color: 0x8a4a35, roughness: 0.9 }));
    wall.position.set(0, 0.525, 0); wall.castShadow = true; g.add(wall);
    const top = new THREE.Mesh(new THREE.BoxGeometry(3.75, 0.1, 0.5), white); top.position.set(0, 1.08, 0); g.add(top);
  } else {
    // flower box filler
    const box = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.28, 0.5), greenM); box.position.set(0, 0.14, 0.45); box.castShadow = true; g.add(box);
    const r = rng(f.s * 100);
    const fg = new THREE.IcosahedronGeometry(0.11, 0);
    for (let i = 0; i < 26; i++) { const m = new THREE.Mesh(fg, new THREE.MeshStandardMaterial({ color: flowerCols[Math.floor(r() * 4)], roughness: 0.8 })); m.position.set(-1.6 + r() * 3.2, 0.33 + r() * 0.08, 0.3 + r() * 0.3); g.add(m); }
  }
  const p = pathAt(f.s); g.position.set(p.x, 0, p.z); g.rotation.y = -p.a; scene.add(g); fenceObjs.push(g);
}
fences.forEach(makeFence);

// ---------- stands + crowd ----------
const crowdCols = [0x2c3e50, 0x8e5b3e, 0xc9a96e, 0xf5f0e8, 0x5d6d7e, 0x7b4b4b, 0x3f5f4f, 0xb9a38a, 0x1a1510, 0x9c7a54, 0x445566];
const people = []; // instanced
const personG = new THREE.CapsuleGeometry(0.2, 0.45, 3, 8);
const crowdMat = new THREE.MeshStandardMaterial({ roughness: 0.8 });
const crowdList = [];
function stand(cx, cz, length, rotY) {
  const g = new THREE.Group(); g.position.set(cx, 0, cz); g.rotation.y = rotY;
  const concrete = new THREE.MeshStandardMaterial({ color: 0xd9d2c4, roughness: 0.9 });
  const steps = 7;
  for (let i = 0; i < steps; i++) {
    const s = new THREE.Mesh(new THREE.BoxGeometry(length, 0.55 * (i + 1), 1.1), concrete); s.position.set(0, 0.275 * (i + 1), i * 1.1); s.castShadow = true; s.receiveShadow = true; g.add(s);
  }
  const roof = new THREE.Mesh(new THREE.BoxGeometry(length + 1, 0.15, steps * 1.1 + 1.5), new THREE.MeshStandardMaterial({ color: 0xf2efe8, roughness: 0.6 }));
  roof.position.set(0, 0.55 * steps + 3.2, (steps - 1) * 0.55); roof.rotation.x = -0.08; g.add(roof);
  for (const sx of [-1, 1]) for (const sz of [0, 1]) { const post = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 6.6), white); post.position.set(sx * length / 2, 3.3, sz * (steps - 1) * 1.1); g.add(post); }
  scene.add(g); g.updateMatrixWorld(true);
  const r = rng(Math.floor(cx * 13 + cz * 7));
  for (let i = 0; i < steps; i++) for (let x = -length / 2 + 0.5; x < length / 2 - 0.4; x += 0.62) {
    if (r() < 0.12) continue;
    const local = new THREE.Vector3(x + (r() - 0.5) * 0.15, 0.55 * (i + 1) + 0.42, i * 1.1 + 0.1);
    crowdList.push({ p: g.localToWorld(local.clone()), c: crowdCols[Math.floor(r() * crowdCols.length)], ph: r() * 6.28, amp: 0.5 + r() * 0.5 });
  }
}
// long stand on the +x side, short one on the far end
stand(AR.x1 + 4, AC.z + 8, 44, Math.PI / 2);
stand(AC.x, AR.z0 - 4, 30, Math.PI);
stand(AR.x0 - 4, AC.z - 14, 30, -Math.PI / 2);
const crowd = new THREE.InstancedMesh(personG, crowdMat, crowdList.length);
crowd.castShadow = false;
{
  const col = new THREE.Color();
  crowdList.forEach((p, i) => { crowd.setColorAt(i, col.setHex(p.c)); });
}
scene.add(crowd);
function updateCrowd(t) {
  const m = new THREE.Matrix4(); const cheer = smooth((t - tClear) / 0.4);
  crowdList.forEach((p, i) => {
    const y = p.p.y + Math.max(0, Math.sin(t * 7 * p.amp + p.ph)) * 0.25 * cheer + Math.sin(t * 1.3 + p.ph) * 0.02;
    m.makeTranslation(p.p.x, y, p.p.z); crowd.setMatrixAt(i, m);
  });
  crowd.instanceMatrix.needsUpdate = true;
}

// ---------- tents ----------
function tent(x, z, s = 1) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s);
  const b = new THREE.Mesh(new THREE.BoxGeometry(5, 2.4, 5), white); b.position.y = 1.2; b.castShadow = true; g.add(b);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(3.9, 2.2, 4), white); roof.position.y = 3.5; roof.rotation.y = Math.PI / 4; roof.castShadow = true; g.add(roof);
  scene.add(g);
}
tent(AR.x1 + 6, AR.z0 - 4, 1.1); tent(AR.x1 + 13, AR.z0 + 3); tent(AR.x0 - 7, AR.z1 + 5); tent(AR.x0 - 7, AR.z0 + 4, 1.2); tent(AR.x1 + 6, AR.z1 + 6, 0.9);

// ---------- trees ----------
{
  const trunks = [], crowns = [];
  const r = rng(21);
  const ring = (n, d0, d1) => {
    for (let i = 0; i < n; i++) {
      const ang = r() * Math.PI * 2; const ex = (AR.x1 - AR.x0) / 2 + d0 + r() * (d1 - d0), ez = (AR.z1 - AR.z0) / 2 + d0 + r() * (d1 - d0);
      const x = AC.x + Math.cos(ang) * ex, z = AC.z + Math.sin(ang) * ez;
      if (Math.abs(x - (AR.x1 + 6)) < 26 && Math.abs(z - (AC.z + 8)) < 25 && d0 < 20) continue; // keep stands clear
      const s = 0.8 + r() * 1.0;
      trunks.push({ x, z, s }); const nc = 2 + Math.floor(r() * 3);
      for (let k = 0; k < nc; k++) crowns.push({ x: x + (r() - 0.5) * 2.2 * s, y: (4.2 + r() * 2.2) * s, z: z + (r() - 0.5) * 2.2 * s, s: (1.9 + r() * 1.3) * s, c: Math.floor(r() * 4) });
    }
  };
  ring(150, 14, 30); ring(220, 30, 80);
  const tm = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.22, 0.32, 4, 6), new THREE.MeshStandardMaterial({ color: 0x5a4330 }), trunks.length);
  const m4 = new THREE.Matrix4();
  trunks.forEach((t, i) => { m4.compose(new THREE.Vector3(t.x, 2 * t.s, t.z), new THREE.Quaternion(), new THREE.Vector3(t.s, t.s, t.s)); tm.setMatrixAt(i, m4); });
  tm.castShadow = true; scene.add(tm);
  const greens = [0x5f7f3a, 0x6e8f43, 0x4f6e33, 0x7a9a4c];
  const cg = new THREE.IcosahedronGeometry(1, 1);
  const cm = new THREE.InstancedMesh(cg, new THREE.MeshStandardMaterial({ roughness: 0.9, flatShading: true }), crowns.length);
  const col = new THREE.Color(); const q = new THREE.Quaternion();
  crowns.forEach((c, i) => { q.setFromEuler(new THREE.Euler(r(), r(), r())); m4.compose(new THREE.Vector3(c.x, c.y, c.z), q, new THREE.Vector3(c.s, c.s * 0.9, c.s)); cm.setMatrixAt(i, m4); cm.setColorAt(i, col.setHex(greens[c.c])); });
  cm.castShadow = true; scene.add(cm);
}

// =====================================================================
// HORSE + RIDER (POV rig, in a level frame attached to camera)
// =====================================================================
function sweep(pts, rx, ry, radial = 24, cap = true) {
  const pos = [], idx = []; const n = pts.length; const up = new THREE.Vector3(0, 1, 0);
  for (let i = 0; i < n; i++) {
    const T = new THREE.Vector3().subVectors(pts[Math.min(i + 1, n - 1)], pts[Math.max(i - 1, 0)]).normalize();
    const S = new THREE.Vector3().crossVectors(T, up).normalize(); const U = new THREE.Vector3().crossVectors(S, T).normalize();
    for (let j = 0; j < radial; j++) {
      const a = j / radial * Math.PI * 2; const p = pts[i].clone().addScaledVector(S, Math.cos(a) * rx[i]).addScaledVector(U, Math.sin(a) * ry[i]);
      pos.push(p.x, p.y, p.z);
    }
  }
  for (let i = 0; i < n - 1; i++) for (let j = 0; j < radial; j++) {
    const a = i * radial + j, b = i * radial + (j + 1) % radial, c = (i + 1) * radial + j, d = (i + 1) * radial + (j + 1) % radial;
    idx.push(a, c, b, b, c, d);
  }
  if (cap) { const ci = pos.length / 3; const e = pts[n - 1]; pos.push(e.x, e.y, e.z); for (let j = 0; j < radial; j++) idx.push((n - 1) * radial + j, ci, (n - 1) * radial + (j + 1) % radial); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
function curvePts(ctrl, n) { const c = new THREE.CatmullRomCurve3(ctrl); return c.getPoints(n - 1); }

const BASE_PITCH = -0.385;  // camera looks down ~22deg
const rig = new THREE.Group(); rig.rotation.x = -BASE_PITCH; camera.add(rig);
const neckPivot = new THREE.Group(); neckPivot.position.set(0, -0.95, -0.35); rig.add(neckPivot); // withers
const coat = new THREE.MeshStandardMaterial({ color: 0x6a361a, roughness: 0.5, metalness: 0.0 });
const dark = new THREE.MeshStandardMaterial({ color: 0x24150c, roughness: 0.75 });
const leather = new THREE.MeshStandardMaterial({ color: 0x1b120c, roughness: 0.5 });
const W0 = new THREE.Vector3(0, -0.95, -0.35);
const loc = v => v.clone().sub(W0); // to neckPivot space
let maneTop = [];
{
  const ctrl = [new THREE.Vector3(0, -1.15, 0.05), new THREE.Vector3(0, -0.95, -0.35), new THREE.Vector3(0, -0.74, -0.95), new THREE.Vector3(0, -0.58, -1.45), new THREE.Vector3(0, -0.53, -1.66)].map(loc);
  const pts = curvePts(ctrl, 40); const n = pts.length;
  const rx = pts.map((_, i) => lerp(0.225, 0.11, Math.pow(i / (n - 1), 0.9)));
  const ry = pts.map((_, i) => lerp(0.42, 0.15, Math.pow(i / (n - 1), 0.8)));
  // shift centreline down so the crest sits on top line
  const neck = new THREE.Mesh(sweep(pts.map((p, i) => p.clone().add(new THREE.Vector3(0, -ry[i] * 0.35, 0))), rx, ry, 32), coat);
  neck.castShadow = true; neckPivot.add(neck);
  maneTop = pts.map((p, i) => p.clone().add(new THREE.Vector3(0, ry[i] * 0.65, 0)));
  // crest (dark mane line)
  const crestPts = maneTop.slice(2, n - 1);
  const crest = new THREE.Mesh(sweep(crestPts.map(p => p.clone().add(new THREE.Vector3(0, -0.005, 0))), crestPts.map(() => 0.03), crestPts.map(() => 0.03), 10), dark);
  neckPivot.add(crest);
  // plaits
  const kg = new THREE.SphereGeometry(1, 14, 10);
  for (let i = 0; i < 9; i++) {
    const k = Math.round(lerp(13, n - 5, i / 8)); const m = new THREE.Mesh(kg, dark); const s = lerp(0.036, 0.03, i / 8);
    m.scale.set(s * 0.9, s * 0.8, s * 1.2); m.position.copy(maneTop[k]).add(new THREE.Vector3(0, 0.012, 0)); neckPivot.add(m);
  }
  // head (angled down) — mostly hidden behind poll
  const hctrl = [new THREE.Vector3(0, -0.6, -1.55), new THREE.Vector3(0, -0.66, -1.78), new THREE.Vector3(0, -0.88, -1.98), new THREE.Vector3(0, -1.18, -2.12)].map(loc);
  const hp = curvePts(hctrl, 20);
  const head = new THREE.Mesh(sweep(hp, hp.map((_, i) => lerp(0.13, 0.085, i / 19)), hp.map((_, i) => lerp(0.17, 0.1, i / 19)), 24), coat); neckPivot.add(head);
  // forelock
  const fl = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), dark); fl.scale.set(0.06, 0.035, 0.09); fl.position.copy(loc(new THREE.Vector3(0, -0.47, -1.7))); neckPivot.add(fl);
  // bridle crownpiece & browband
  const crown = new THREE.Mesh(new THREE.TorusGeometry(0.15, 0.013, 8, 32), leather); crown.position.copy(loc(new THREE.Vector3(0, -0.58, -1.62))); crown.rotation.x = 0.35; neckPivot.add(crown);
  const brow = new THREE.Mesh(new THREE.TorusGeometry(0.145, 0.012, 8, 32, Math.PI), new THREE.MeshStandardMaterial({ color: 0xC9A96E, roughness: 0.3, metalness: 0.6 }));
  brow.position.copy(loc(new THREE.Vector3(0, -0.6, -1.72))); brow.rotation.set(-1.2, 0, 0); neckPivot.add(brow);
}
// ears
const ears = [];
for (const sx of [-1, 1]) {
  const e = new THREE.Group(); e.position.copy(loc(new THREE.Vector3(sx * 0.075, -0.49, -1.63))); neckPivot.add(e);
  const g = new THREE.SphereGeometry(1, 18, 14); g.translate(0, 1, 0);
  const pa = g.attributes.position; for (let i = 0; i < pa.count; i++) { const y = pa.getY(i); const k = 1 - Math.pow(y / 2, 2.2) * 0.75; pa.setX(i, pa.getX(i) * k); pa.setZ(i, pa.getZ(i) * k); } g.computeVertexNormals();
  const m = new THREE.Mesh(g, coat); m.scale.set(0.045, 0.085, 0.03); e.add(m);
  const inner = new THREE.Mesh(g, dark); inner.scale.set(0.03, 0.07, 0.02); inner.position.set(0, 0.01, -0.012); e.add(inner);
  e.rotation.set(-0.25, 0, -sx * 0.22); e.userData.sx = sx; ears.push(e);
}
// hands / gloves / sleeves
const glove = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.42, metalness: 0.05 });
const navy = new THREE.MeshStandardMaterial({ color: 0x1b2333, roughness: 0.75 });
const hands = [];
for (const sx of [-1, 1]) {
  const h = new THREE.Group(); h.position.set(sx * 0.14, -0.56, -0.62); rig.add(h);
  const palm = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), glove); palm.scale.set(0.05, 0.045, 0.062); h.add(palm);
  const fg = new THREE.CapsuleGeometry(0.017, 0.05, 4, 10);
  for (let k = 0; k < 4; k++) { const f = new THREE.Mesh(fg, glove); f.position.set(-sx * 0.012 + sx * (0.0), 0.01 - k * 0.022, -0.05); f.rotation.set(0, 0, Math.PI / 2); f.position.x = sx * 0.0; h.add(f); }
  const th = new THREE.Mesh(new THREE.CapsuleGeometry(0.016, 0.045, 4, 10), glove); th.position.set(-sx * 0.005, 0.047, -0.035); th.rotation.set(Math.PI / 2 - 0.4, 0, 0); h.add(th);
  const cuff = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.055, 0.05, 16), glove); cuff.position.set(0, -0.01, 0.06); cuff.rotation.x = Math.PI / 2 - 0.4; h.add(cuff);
  h.rotation.set(0.25, -sx * 0.15, sx * 0.35);
  // sleeve
  const a = new THREE.Vector3(sx * 0.42, -1.25, -0.05), b = new THREE.Vector3(sx * 0.16, -0.6, -0.545);
  const sl = new THREE.Mesh(sweep(curvePts([a, a.clone().lerp(b, 0.5).add(new THREE.Vector3(sx * 0.02, 0.02, 0)), b], 10), Array(10).fill(0).map((_, i) => lerp(0.07, 0.045, i / 9)), Array(10).fill(0).map((_, i) => lerp(0.07, 0.045, i / 9)), 18), navy);
  rig.add(sl);
  const shirt = new THREE.Mesh(new THREE.CylinderGeometry(0.047, 0.047, 0.018, 18), new THREE.MeshStandardMaterial({ color: 0xf5f0e8, roughness: 0.6 }));
  
  hands.push(h);
}
// reins (rebuilt per frame)
const reinMeshes = [null, null];
function updateReins() {
  neckPivot.updateMatrix(); rig.updateMatrixWorld(true);
  [-1, 1].forEach((sx, k) => {
    const bitW = neckPivot.localToWorld(loc(new THREE.Vector3(sx * 0.1, -1.0, -1.98)));
    const midW = neckPivot.localToWorld(loc(new THREE.Vector3(sx * 0.215, -0.8, -1.25)));
    const mid2W = neckPivot.localToWorld(loc(new THREE.Vector3(sx * 0.2, -0.7, -0.88)));
    const toRig = v => rig.worldToLocal(v);
    const hw = hands[k].position.clone().add(new THREE.Vector3(-sx * 0.01, -0.02, -0.02));
    const pts = [toRig(bitW), toRig(midW), toRig(mid2W), hw];
    const g = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 40, 0.009, 6);
    if (reinMeshes[k]) { reinMeshes[k].geometry.dispose(); reinMeshes[k].geometry = g; } else { reinMeshes[k] = new THREE.Mesh(g, leather); rig.add(reinMeshes[k]); }
  });
}

// shadow-only body (horse + rider) in world space
const shadowOnly = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false });
const body = new THREE.Group(); scene.add(body);
const legs = [];
{
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.42, 1.3, 4, 12), shadowOnly); torso.rotation.x = Math.PI / 2; torso.position.set(0, 1.4, 0.35); torso.castShadow = true; body.add(torso);
  const neckS = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.9, 4, 8), shadowOnly); neckS.position.set(0, 1.9, -0.75); neckS.rotation.x = 0.9; neckS.castShadow = true; body.add(neckS);
  const headS = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.45, 4, 8), shadowOnly); headS.position.set(0, 1.95, -1.4); headS.rotation.x = 2.3; headS.castShadow = true; body.add(headS);
  for (const [x, z] of [[-0.22, -0.4], [0.22, -0.4], [-0.22, 1.05], [0.22, 1.05]]) {
    const piv = new THREE.Group(); piv.position.set(x, 1.15, z); body.add(piv);
    const l = new THREE.Mesh(new THREE.CapsuleGeometry(0.08, 0.95, 4, 8), shadowOnly); l.position.y = -0.55; l.castShadow = true; piv.add(l); legs.push(piv);
  }
  const rt = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.5, 4, 8), shadowOnly); rt.position.set(0, 2.15, 0.15); rt.rotation.x = -0.3; rt.castShadow = true; body.add(rt);
  const rh = new THREE.Mesh(new THREE.SphereGeometry(0.15, 10, 8), shadowOnly); rh.position.set(0, 2.62, 0.05); rh.castShadow = true; body.add(rh);
}

// =====================================================================
// HUD
// =====================================================================
const out = document.createElement('canvas'); out.width = W; out.height = H; document.body.appendChild(out);
const ctx = out.getContext('2d');

function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function text(str, x, y, { font, fill = C.cream, align = 'center', ls = 0, alpha = 1, stroke = null, sw = 0, shadow = 0, base = 'middle' }) {
  ctx.save(); ctx.globalAlpha *= alpha; ctx.font = font; ctx.textAlign = align; ctx.textBaseline = base; ctx.letterSpacing = ls + 'px';
  if (shadow) { ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = shadow; ctx.shadowOffsetY = shadow * 0.3; }
  if (stroke) { ctx.lineJoin = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = sw; ctx.strokeText(str, x, y); ctx.shadowColor = 'transparent'; }
  ctx.fillStyle = fill; ctx.fillText(str, x, y); ctx.restore();
}
function goldGrad(y0, y1) { const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, '#FFF6E2'); g.addColorStop(0.5, '#E9D3A2'); g.addColorStop(1, '#C9A96E'); return g; }

// big prompt text (design coordinates, scaled)
function bigPrompt(str, t, t0, t1, y = 560) {
  const a = t - t0, b = t1 - t; if (a < 0 || b < 0) return;
  const inn = clamp(a / 0.22), outp = clamp(b / 0.18);
  const sc = lerp(1.45, 1, easeOutBack(inn)) * lerp(0.92, 1, outp);
  const size = str.length > 9 ? 112 : 132;
  ctx.save(); ctx.translate(W / 2, y * K); ctx.scale(sc * K, sc * K); ctx.globalAlpha = Math.min(inn * 1.4, outp);
  text(str, 0, 0, { font: `700 ${size}px Lora`, fill: C.dark, stroke: C.dark, sw: 22, ls: 2, alpha: 0.55, shadow: 30 });
  text(str, 0, 0, { font: `700 ${size}px Lora`, fill: goldGrad(-size / 2, size / 2), stroke: '#2a1f14', sw: 9, ls: 2 });
  ctx.restore();
}

function project(obj) {
  const v = new THREE.Vector3(); obj.getWorldPosition(v); v.project(camera);
  return { x: (v.x * 0.5 + 0.5) * W, y: (-v.y * 0.5 + 0.5) * H };
}

function fingerprint(x, y, r, alpha) {
  ctx.save(); ctx.translate(x, y); ctx.globalAlpha = alpha; ctx.strokeStyle = C.cream; ctx.lineWidth = 3.2 * K; ctx.lineCap = 'round';
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 8 * K;
  for (let i = 1; i <= 6; i++) {
    const rx = r * i / 6.4, ry = r * i / 5.2; ctx.beginPath();
    ctx.ellipse(0, r * 0.08, rx, ry, 0, Math.PI * (0.92 + (i % 2) * 0.1), Math.PI * (2.08 + (i % 3) * 0.08)); ctx.stroke();
  }
  ctx.restore();
}
function thumbRing(x, y, t, pressed, alpha = 1) {
  const r = 88 * K * lerp(1, 0.9, pressed);
  ctx.save(); ctx.globalAlpha = alpha;
  if (pressed > 0) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 1.25); g.addColorStop(0, `rgba(233,211,162,${0.75 * pressed})`); g.addColorStop(0.6, `rgba(201,169,110,${0.45 * pressed})`); g.addColorStop(1, 'rgba(201,169,110,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 1.25, 0, 7); ctx.fill();
  }
  ctx.lineWidth = 3.5 * K; ctx.strokeStyle = pressed > 0.5 ? C.gold : 'rgba(245,240,232,0.92)';
  ctx.setLineDash([14 * K, 11 * K]); ctx.lineDashOffset = -t * 30 * K;
  ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 6 * K;
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
}
function arrowTile(x, y, kind, t, alpha) {
  if (alpha <= 0) return;
  const bob = Math.sin(t * 9) * 7 * K; const w = 86 * K, h = 104 * K;
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y + bob);
  ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 18 * K; ctx.shadowOffsetY = 5 * K;
  const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2); g.addColorStop(0, '#E9D3A2'); g.addColorStop(1, '#C9A96E');
  ctx.fillStyle = g; rr(-w / 2, -h / 2, w, h, 18 * K); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = 'rgba(255,248,230,0.8)'; ctx.lineWidth = 2 * K; ctx.stroke();
  ctx.fillStyle = C.dark; ctx.strokeStyle = C.dark; ctx.lineWidth = 11 * K; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (kind === 'up') {
    ctx.beginPath(); ctx.moveTo(0, 30 * K); ctx.lineTo(0, -8 * K); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-24 * K, -4 * K); ctx.lineTo(0, -34 * K); ctx.lineTo(24 * K, -4 * K); ctx.closePath(); ctx.fill();
  } else {
    const s = kind === 'left' ? -1 : 1;
    ctx.beginPath(); ctx.moveTo(-s * 12 * K, 32 * K); ctx.lineTo(-s * 12 * K, 0); ctx.quadraticCurveTo(-s * 12 * K, -14 * K, 4 * s * K, -14 * K); ctx.lineTo(8 * s * K, -14 * K); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(6 * s * K, -36 * K); ctx.lineTo(32 * s * K, -14 * K); ctx.lineTo(6 * s * K, 8 * K); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

function topBar(t, alpha) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(0, lerp(-40, 0, alpha) * K);
  const x = 64 * K, y = 150 * K, w = 952 * K, h = 104 * K;
  ctx.fillStyle = 'rgba(26,21,16,0.78)'; rr(x, y, w, h, 52 * K); ctx.fill();
  ctx.strokeStyle = 'rgba(201,169,110,0.55)'; ctx.lineWidth = 2 * K; ctx.stroke();
  // fence counter
  let next = fences.find(f => t < f.tLD); const cur = next ? next.n : 'DONE';
  const lab = { font: `600 ${19 * K}px Poppins`, fill: C.gold, align: 'left', ls: 3 * K };
  text('FENCE', x + 52 * K, y + 33 * K, lab);
  text(cur === 'DONE' ? 'Finished' : cur, x + 52 * K, y + 70 * K, { font: `700 ${38 * K}px Poppins`, fill: C.cream, align: 'left' });
  if (cur !== 'DONE') { ctx.font = `700 ${38 * K}px Poppins`; const tw = ctx.measureText(cur).width; text(' / 7', x + 52 * K + tw, y + 72 * K, { font: `500 ${24 * K}px Poppins`, fill: C.lgold, align: 'left' }); }
  // wordmark
  text('EQUIEBOOK', W / 2 + 3 * K, y + h / 2 + 2 * K, { font: `700 ${30 * K}px Lora`, fill: C.gold, ls: 6 * K });
  // time + faults
  const tt = clamp(t - T0, 0, tFinish - T0);
  text('TIME', x + w - 250 * K, y + 33 * K, lab);
  text(tt.toFixed(2) + 's', x + w - 250 * K, y + 70 * K, { font: `700 ${34 * K}px Poppins`, fill: C.cream, align: 'left' });
  text('FAULTS', x + w - 100 * K, y + 33 * K, { ...lab, align: 'center' });
  text('0', x + w - 100 * K, y + 70 * K, { font: `700 ${34 * K}px Poppins`, fill: C.cream });
  ctx.restore();
}
function pill(str, t, t0, dur, y = 290) {
  const a = t - t0; if (a < 0 || a > dur) return;
  const al = Math.min(smooth(a / 0.15), smooth((dur - a) / 0.25));
  ctx.save(); ctx.globalAlpha = al; ctx.translate(W / 2, (y + lerp(-14, 0, al)) * K);
  ctx.font = `600 ${26 * K}px Poppins`; const tw = ctx.measureText(str).width; const w = tw + 90 * K, h = 52 * K;
  ctx.fillStyle = C.gold; rr(-w / 2, -h / 2, w, h, h / 2); ctx.fill();
  // check
  ctx.strokeStyle = C.dark; ctx.lineWidth = 5 * K; ctx.lineCap = 'round'; ctx.beginPath();
  ctx.moveTo(-w / 2 + 26 * K, 0); ctx.lineTo(-w / 2 + 36 * K, 10 * K); ctx.lineTo(-w / 2 + 54 * K, -10 * K); ctx.stroke();
  text(str, 20 * K, 2 * K, { font: `600 ${26 * K}px Poppins`, fill: C.dark });
  ctx.restore();
}

// confetti
const conf = []; { const r = rng(99); for (let i = 0; i < 160; i++) conf.push({ x: r(), d: r() * 0.6, vx: (r() - 0.5) * 0.12, sp: 0.55 + r() * 0.5, rot: r() * 6, vr: (r() - 0.5) * 12, c: [C.gold, C.cream, C.lgold, '#8a6a3a', '#ffffff'][Math.floor(r() * 5)], w: 10 + r() * 12, h: 5 + r() * 7 }); }
function confetti(t) {
  const a = t - tClear; if (a < 0) return;
  for (const p of conf) {
    const tt = a - p.d; if (tt < 0) continue;
    const y = (-0.05 + tt * p.sp * 0.5 + 0.08 * tt * tt) * H; if (y > H + 20) continue;
    const x = (p.x + p.vx * tt + Math.sin(tt * 3 + p.rot) * 0.02) * W;
    ctx.save(); ctx.translate(x, y); ctx.rotate(p.rot + p.vr * tt); ctx.scale(1, Math.cos(tt * 8 + p.rot));
    ctx.fillStyle = p.c; ctx.fillRect(-p.w * K / 2, -p.h * K / 2, p.w * K, p.h * K); ctx.restore();
  }
}
function rosette(cx, cy, r, rot) {
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot);
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24 * K; ctx.shadowOffsetY = 8 * K;
  // tails
  for (const s of [-1, 1]) {
    ctx.save(); ctx.rotate(s * 0.28); ctx.fillStyle = s < 0 ? C.gold : '#a8874f';
    ctx.beginPath(); ctx.moveTo(-r * 0.28, r * 0.2); ctx.lineTo(r * 0.28, r * 0.2); ctx.lineTo(r * 0.28, r * 1.9); ctx.lineTo(0, r * 1.65); ctx.lineTo(-r * 0.28, r * 1.9); ctx.closePath(); ctx.fill();
    ctx.restore();
  }
  // pleats
  const n = 36;
  for (let ring = 0; ring < 2; ring++) {
    const R0 = ring ? r * 0.82 : r;
    ctx.beginPath();
    for (let i = 0; i <= n * 2; i++) { const a = i / (n * 2) * Math.PI * 2; const rr2 = i % 2 ? R0 * 0.9 : R0; ctx.lineTo(Math.cos(a) * rr2, Math.sin(a) * rr2); }
    ctx.closePath(); ctx.fillStyle = ring ? C.cream : C.gold; ctx.fill(); ctx.shadowColor = 'transparent';
  }
  ctx.beginPath(); ctx.arc(0, 0, r * 0.58, 0, 7); ctx.fillStyle = C.dark; ctx.fill();
  ctx.lineWidth = 4 * K; ctx.strokeStyle = C.gold; ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, 7); ctx.stroke();
  text('E', 0, r * 0.04, { font: `700 ${r * 0.72}px Lora`, fill: C.gold });
  ctx.restore();
}

// end card
function endCard(t) {
  const a = t - tEnd; if (a < 0) return;
  const al = smooth(a / 0.5);
  ctx.save(); ctx.globalAlpha = al;
  const g = ctx.createRadialGradient(W / 2, H * 0.45, 0, W / 2, H * 0.45, H * 0.75); g.addColorStop(0, '#2a2118'); g.addColorStop(1, '#100c08');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // gold arcs
  ctx.strokeStyle = 'rgba(201,169,110,0.35)'; ctx.lineWidth = 2 * K;
  for (let i = 0; i < 3; i++) { ctx.beginPath(); const rad = (380 + i * 70) * K; const sweep = smooth((a - i * 0.12) / 1.2) * Math.PI * 1.6; ctx.arc(W / 2, 900 * K, rad, -Math.PI / 2 - sweep / 2 + a * 0.08, -Math.PI / 2 + sweep / 2 + a * 0.08); ctx.stroke(); }
  ctx.restore();
  const el = (d, fn) => { const e = smooth((a - d) / 0.45); if (e <= 0) return; ctx.save(); ctx.globalAlpha = e * al; ctx.translate(0, lerp(26, 0, e) * K); fn(); ctx.restore(); };
  el(0.2, () => text('SHOW JUMPING · DRESSAGE', W / 2, 560 * K, { font: `600 ${22 * K}px Poppins`, fill: C.lgold, ls: 6 * K }));
  el(0.3, () => text('EQUIEBOOK', W / 2 + 8 * K, 680 * K, { font: `700 ${100 * K}px Lora`, fill: goldGrad(630 * K, 730 * K), ls: 14 * K }));
  el(0.45, () => text('RIDE · CONNECT · DISCOVER', W / 2, 770 * K, { font: `500 ${25 * K}px Poppins`, fill: C.lgold, ls: 7 * K }));
  el(0.55, () => { ctx.fillStyle = C.gold; ctx.fillRect(W / 2 - 60 * K, 828 * K, 120 * K, 2 * K); });
  el(0.75, () => { text('Your next clear round', W / 2, 920 * K, { font: `600 ${62 * K}px Lora`, fill: C.cream }); text('starts here.', W / 2, 1000 * K, { font: `600 ${62 * K}px Lora`, fill: C.gold }); });
  el(1.0, () => text('Find events  ·  Enter in-app  ·  Live scores', W / 2, 1090 * K, { font: `500 ${29 * K}px Poppins`, fill: 'rgba(245,240,232,0.85)' }));
  el(1.25, () => {
    const pulse = 1 + Math.sin(Math.max(0, a - 1.6) * 5) * 0.025 * smooth((a - 1.6) / 0.3);
    text('DOWNLOAD FREE', W / 2, 1195 * K, { font: `700 ${28 * K}px Poppins`, fill: C.gold, ls: 5 * K });
    const bw = 330 * K, bh = 104 * K, gap = 26 * K, y = 1240 * K;
    [['Download on the', 'App Store', 'apple'], ['GET IT ON', 'Google Play', 'play']].forEach(([s1, s2, ic], i) => {
      const x = W / 2 + (i ? gap / 2 : -gap / 2 - bw);
      ctx.save(); ctx.translate(x + bw / 2, y + bh / 2); ctx.scale(pulse, pulse); ctx.translate(-bw / 2, -bh / 2);
      ctx.fillStyle = '#000'; rr(0, 0, bw, bh, 20 * K); ctx.fill(); ctx.strokeStyle = 'rgba(245,240,232,0.75)'; ctx.lineWidth = 2.5 * K; ctx.stroke();
      // icon
      ctx.fillStyle = C.cream;
      if (ic === 'play') { ctx.beginPath(); ctx.moveTo(40 * K, 30 * K); ctx.lineTo(80 * K, 52 * K); ctx.lineTo(40 * K, 74 * K); ctx.closePath(); ctx.fill(); }
      else { rr(40 * K, 26 * K, 34 * K, 54 * K, 7 * K); ctx.lineWidth = 4 * K; ctx.strokeStyle = C.cream; ctx.stroke(); ctx.fillRect(51 * K, 72 * K, 12 * K, 3 * K); }
      text(s1, 100 * K, 36 * K, { font: `500 ${18 * K}px Poppins`, fill: C.cream, align: 'left' });
      text(s2, 100 * K, 68 * K, { font: `600 ${33 * K}px Poppins`, fill: '#fff', align: 'left' });
      ctx.restore();
    });
  });
  el(1.5, () => text("iPhone & Android  ·  India's equestrian app", W / 2, 1410 * K, { font: `500 ${23 * K}px Poppins`, fill: 'rgba(212,190,138,0.75)' }));
}

function intro(t, L, Rr) {
  const al = Math.min(smooth(t / 0.35), smooth((3.0 - t) / 0.3)); if (al <= 0) return;
  ctx.save(); ctx.globalAlpha = al;
  // eyebrow
  ctx.fillStyle = 'rgba(26,21,16,0.75)'; rr(W / 2 - 220 * K, 276 * K, 440 * K, 48 * K, 24 * K); ctx.fill();
  text('SHOW JUMPING  ·  7 FENCES', W / 2 + 3 * K, 301 * K, { font: `600 ${22 * K}px Poppins`, fill: C.gold, ls: 6 * K });
  text('Can you ride a clear round?', W / 2, 360 * K, { font: `600 ${42 * K}px Poppins`, fill: C.cream, shadow: 16 * K });
  const sc = lerp(1.25, 1, easeOutBack(clamp(t / 0.4)));
  ctx.save(); ctx.translate(W / 2, 520 * K); ctx.scale(sc, sc);
  for (const [s, yy] of [['PLACE YOUR', -55], ['THUMBS HERE', 60]]) {
    text(s, 0, yy * K, { font: `700 ${104 * K}px Lora`, fill: C.dark, stroke: C.dark, sw: 20 * K, alpha: 0.5, shadow: 26 * K });
    text(s, 0, yy * K, { font: `700 ${104 * K}px Lora`, fill: goldGrad((yy - 50) * K, (yy + 50) * K), stroke: '#2a1f14', sw: 8 * K });
  }
  ctx.restore();
  // dashed arrows from title to rings
  const draw = smooth((t - 0.35) / 0.6);
  for (const [p, s] of [[L, -1], [Rr, 1]]) {
    ctx.save(); ctx.strokeStyle = C.cream; ctx.lineWidth = 4 * K; ctx.setLineDash([12 * K, 10 * K]); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 8 * K;
    const sx = W / 2 + s * 150 * K, sy = 640 * K, ex = p.x, ey = p.y - 110 * K;
    const cx1 = sx + s * 190 * K, cy1 = (sy + ey) / 2 - 40 * K;
    ctx.beginPath(); const N = 30; for (let i = 0; i <= N * draw; i++) { const u = i / N; const x = (1 - u) * (1 - u) * sx + 2 * u * (1 - u) * cx1 + u * u * ex; const y = (1 - u) * (1 - u) * sy + 2 * u * (1 - u) * cy1 + u * u * ey; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke();
    if (draw > 0.98) { ctx.setLineDash([]); ctx.beginPath(); ctx.moveTo(ex - 16 * K, ey - 18 * K); ctx.lineTo(ex, ey); ctx.lineTo(ex + 16 * K, ey - 18 * K); ctx.stroke(); }
    ctx.restore();
    fingerprint(p.x, p.y, 62 * K, smooth((t - 0.6) / 0.4) * (0.75 + 0.25 * Math.sin(t * 6)));
  }
  ctx.restore();
}

// =====================================================================
// FRAME UPDATE
// =====================================================================
const tmpV = new THREE.Vector3();
let gaitPhase = 0, lastI = -1;
const phaseArr = []; { let ph = 0; for (let i = 0; i < sArr.length; i++) { const v = vArr[i]; phaseArr.push(ph); ph += 2 * Math.PI * (v > 0.3 ? lerp(1.2, 1.75, clamp(v / V)) : 0) / FPS; } }

function jumpState(s) {
  let y = 0, pitch = 0, air = 0, u0 = -1, bascule = 0;
  for (const f of fences) {
    const u = (s - (f.s - J)) / (2 * J);
    if (u > 0 && u < 1) { y += JH * Math.pow(Math.sin(Math.PI * u), 1.15); pitch += Math.atan(JH * Math.PI / (2 * J) * Math.cos(Math.PI * u)) * 0.55; air = Math.sin(Math.PI * u); u0 = u; bascule = Math.sin(Math.PI * u); }
    else if (u > -0.16 && u <= 0) { const k = Math.sin(Math.PI * (u + 0.16) / 0.16); y -= 0.1 * k; pitch -= 0.03 * k; }
    else if (u >= 1 && u < 1.18) { const k = Math.sin(Math.PI * (u - 1) / 0.18); y -= 0.13 * k; pitch -= 0.05 * k; }
  }
  return { y, pitch, air, u: u0, bascule };
}

function update(i) {
  const t = i / FPS; const s = sArr[Math.min(i, sArr.length - 1)]; const v = vArr[Math.min(i, vArr.length - 1)];
  const p = pathAt(s); const ahead = pathAt(s + 5.5);
  const ph = phaseArr[Math.min(i, phaseArr.length - 1)];
  const js = jumpState(s);
  const sp = clamp(v / V);
  const ground = 1 - js.air;
  const bob = (Math.sin(ph) * 0.075 + Math.sin(2 * ph + 0.6) * 0.025) * sp * ground + (v < 0.3 ? Math.sin(t * 1.6) * 0.008 : 0);
  // yaw from look-ahead (anticipates turns)
  const yaw = Math.atan2(-(ahead.x - p.x), -(ahead.z - p.z));
  const turnRate = (pathAt(s + 3).a - p.a);
  const roll = clamp(turnRate * 0.55, -0.12, 0.12) * sp;
  camera.position.set(p.x, 2.45 + bob + js.y, p.z);
  camera.rotation.order = 'YXZ';
  camera.rotation.set(BASE_PITCH + js.pitch + Math.cos(ph) * 0.018 * sp * ground, yaw, roll);
  camera.updateMatrixWorld(true);
  camera.userData.sky.position.copy(camera.position);
  // horse neck motion
  const nod = Math.sin(ph - 0.9) * 0.05 * sp * ground;
  const jumpNeck = js.u >= 0 ? (js.u < 0.3 ? 0.10 * Math.sin(Math.PI * js.u / 0.3) : -0.16 * Math.sin(Math.PI * (js.u - 0.3) / 0.7)) : 0;
  neckPivot.rotation.x = nod + jumpNeck + (v < 0.3 ? Math.sin(t * 1.1) * 0.02 : 0);
  neckPivot.rotation.y = clamp(turnRate * 0.6, -0.12, 0.12);
  // ears: flick in intro, forward when approaching fences
  ears.forEach((e, k) => {
    const flick = t < T0 ? Math.max(0, Math.sin(t * 2.3 + k * 2.2)) ** 6 * 0.6 : 0;
    e.rotation.x = -0.25 - flick + js.air * 0.2; e.rotation.z = -e.userData.sx * (0.22 + flick * 0.4);
  });
  // hands follow mouth during bascule
  hands.forEach((h, k) => { const sx = k ? 1 : -1; h.position.set(sx * 0.14, -0.56 + bob * -0.3 - js.bascule * 0.03, -0.62 - js.bascule * 0.1); });
  updateReins();
  // shadow body
  body.position.set(p.x, js.y, p.z); body.rotation.set(js.pitch * 0.8, -p.a, 0);
  legs.forEach((l, k) => { l.rotation.x = js.air > 0.2 ? (k < 2 ? -1.2 : 0.9) * js.air : Math.sin(ph + k * 1.3) * 0.55 * sp; });
  // sun follows
  const c = camera.position; sun.position.set(c.x + sunDir.x * 50, sunDir.y * 50, c.z + sunDir.z * 50); sun.target.position.set(c.x - Math.sin(yaw) * 10, 0, c.z - Math.cos(yaw) * 10);
  updateCrowd(t);
  return { t, s, v };
}

function drawHUD(t) {
  const L = project(hands[0]), Rr = project(hands[1]);
  const ringsA = t < tClear ? 1 : 1 - smooth((t - tClear) / 0.3);
  // rings always present while riding
  let pressL = 0, pressR = 0, upA = 0, leftA = 0, rightA = 0;
  for (const pr of prompts) {
    if (!pr.kind || pr.kind === 'clear') continue;
    if (t >= pr.t0 && t <= pr.t1) {
      const a = Math.min(smooth((t - pr.t0) / 0.18), smooth((pr.t1 - t) / 0.15));
      const pz = smooth((t - pr.press) / 0.12) * smooth((pr.t1 - t) / 0.15);
      if (pr.kind === 'jump') { upA = Math.max(upA, a); pressL = Math.max(pressL, pz); pressR = Math.max(pressR, pz); }
      if (pr.kind === 'left') { leftA = a; pressL = Math.max(pressL, pz); }
      if (pr.kind === 'right') { rightA = a; pressR = Math.max(pressR, pz); }
    }
  }
  if (ringsA > 0) {
    const ry = -150 * K;
    thumbRing(L.x, L.y, t, pressL, ringsA); thumbRing(Rr.x, Rr.y, t, pressR, ringsA);
    arrowTile(L.x, L.y + ry, 'up', t, upA); arrowTile(Rr.x, Rr.y + ry, 'up', t, upA);
    arrowTile(L.x, L.y + ry, 'left', t, leftA); arrowTile(Rr.x, Rr.y + ry, 'right', t, rightA);
  }
  intro(t, L, Rr);
  topBar(t, t < tEnd ? smooth((t - T0 + 0.2) / 0.4) : 0);
  for (const f of fences) pill(`Fence ${f.n} clear`, t, f.tLD - 0.05, 1.1);
  for (const pr of prompts) bigPrompt(pr.text, t, pr.t0, pr.t1, pr.kind === 'clear' ? 470 : 560);
  // clear round extras
  if (t >= tClear) {
    const a = t - tClear;
    const drop = easeOutBack(clamp((a - 0.25) / 0.55));
    if (a > 0.25) rosette(W / 2, lerp(-200, 900, drop) * K, 120 * K, Math.sin(a * 3) * 0.06 * (1 - clamp(a / 2)));
    const tt = (tFinish - T0).toFixed(2);
    if (a > 0.5) {
      const e = smooth((a - 0.5) / 0.3);
      ctx.save(); ctx.globalAlpha = e; ctx.translate(W / 2, 592 * K);
      const str = `0 faults  ·  ${tt}s`; ctx.font = `600 ${30 * K}px Poppins`; const w = ctx.measureText(str).width + 70 * K, h = 60 * K;
      ctx.fillStyle = 'rgba(26,21,16,0.85)'; rr(-w / 2, -h / 2, w, h, h / 2); ctx.fill(); ctx.strokeStyle = C.gold; ctx.lineWidth = 2 * K; ctx.stroke();
      text(str, 0, 2 * K, { font: `600 ${30 * K}px Poppins`, fill: C.cream }); ctx.restore();
    }
    if (a > 1.3) {
      const e = smooth((a - 1.3) / 0.35);
      text('Every round. Scored live.', W / 2, lerp(1210, 1190, e) * K, { font: `600 ${44 * K}px Lora`, fill: C.cream, alpha: e, shadow: 18 * K, stroke: 'rgba(26,21,16,0.6)', sw: 6 * K });
      text('on EquiEbook', W / 2, lerp(1272, 1252, e) * K, { font: `600 ${30 * K}px Poppins`, fill: C.lgold, alpha: e, shadow: 14 * K, ls: 2 * K });
    }
    confetti(t);
  }
  endCard(t);
}

// vignette + warm grade overlay
function grade() {
  const g = ctx.createRadialGradient(W / 2, H * 0.48, H * 0.32, W / 2, H * 0.5, H * 0.78);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(20,12,4,0.42)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

window.renderFrame = (i, fmt = 'image/jpeg') => {
  const st = update(i);
  renderer.render(scene, camera);
  ctx.clearRect(0, 0, W, H); ctx.drawImage(renderer.domElement, 0, 0); grade();
  drawHUD(st.t);
  return out.toDataURL(fmt, 0.93);
};
window.META = { NFRAMES, FPS, DUR, T0, tClear, tEnd, tFinish, fences: fences.map(f => ({ n: f.n, tTO: f.tTO, tLD: f.tLD })), turns, prompts: prompts.map(p => ({ t0: p.t0, t1: p.t1, text: p.text, press: p.press })), phase: null };
// export stride beat times for audio
{
  const beats = []; let prev = 0;
  for (let i = 1; i < phaseArr.length && i < NFRAMES; i++) { const a = Math.floor(phaseArr[i - 1] / (2 * Math.PI)), b = Math.floor(phaseArr[i] / (2 * Math.PI)); if (b > a) beats.push({ t: i / FPS, v: vArr[i] / V, air: jumpState(sArr[i]).air }); }
  window.META.strides = beats;
}
await Promise.all(['700 40px Lora', '600 40px Lora', '500 20px Poppins', '600 20px Poppins', '700 20px Poppins'].map(f => document.fonts.load(f)));
// re-render board textures now that fonts are loaded
boardMats.forEach((m, k) => { m.map = boardTex(k); m.needsUpdate = true; });
window.READY = true;
