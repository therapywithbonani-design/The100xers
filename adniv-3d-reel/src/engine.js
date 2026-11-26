import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {Reflector} from 'three/addons/objects/Reflector.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {FontLoader} from 'three/addons/loaders/FontLoader.js';
import {TextGeometry} from 'three/addons/geometries/TextGeometry.js';
import {createHUD} from './hud.js';
import {makeShots} from './shots.js';

const W = 1080, H = 1920;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const mulberry = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

const AMBER = new THREE.Color(1.0, 0.52, 0.10);   // sodium ~1900K
const WHITE = new THREE.Color(0.93, 0.96, 1.0);   // clean LED white

// ------------------------------------------------------------------ renderer + post
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias: false, preserveDrawingBuffer: true});
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
const rt = new THREE.WebGLRenderTarget(W, H, {type: THREE.HalfFloatType, samples: Math.min(4, renderer.capabilities.maxSamples)});
const composer = new EffectComposer(renderer, rt);
const renderPass = new RenderPass(new THREE.Scene(), new THREE.PerspectiveCamera());
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 1, 0.6, 0.15);
const FinalShader = {
  uniforms: {tDiffuse: {value: null}, uTime: {value: 0}, uVig: {value: 0.45}, uGrain: {value: 0.035}, uCA: {value: 0.004}, uGrade: {value: new THREE.Vector3(1, 1, 1)}},
  vertexShader: 'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
  fragmentShader: `uniform sampler2D tDiffuse;uniform float uTime,uVig,uGrain,uCA;uniform vec3 uGrade;varying vec2 vUv;
  float h(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233))+uTime*7.13)*43758.5453);}
  void main(){vec2 d=vUv-.5;float r=dot(d,d);vec2 o=d*uCA*r*4.0;
   vec3 c=vec3(texture2D(tDiffuse,vUv+o).r,texture2D(tDiffuse,vUv).g,texture2D(tDiffuse,vUv-o).b);
   c*=uGrade; c=c*c*(3.0-2.0*c)*0.35+c*0.65;            // gentle S-curve
   c*=1.0-uVig*smoothstep(0.08,0.62,r*2.0);
   c+=(h(vUv*vec2(1080.,1920.))-.5)*uGrain;
   gl_FragColor=vec4(max(c,0.0),1.0);}`
};
const finalPass = new ShaderPass(FinalShader);
composer.addPass(renderPass); composer.addPass(bloom); composer.addPass(new OutputPass()); composer.addPass(finalPass);
const pmrem = new THREE.PMREMGenerator(renderer);
const roomEnv = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ------------------------------------------------------------------ textures
function ctex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; return t;
}
const glowTex = ctex(256, 256, (g) => { const r = g.createRadialGradient(128, 128, 0, 128, 128, 128); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.22, 'rgba(255,255,255,.55)'); r.addColorStop(.6, 'rgba(255,255,255,.13)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, 256, 256); }, false);
const streakTex = ctex(64, 256, (g, w, h) => { for (let y = 0; y < h; y++) { const a = Math.pow(1 - y / h, 1.7); const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, `rgba(255,255,255,${a})`); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, y, w, 1); } }, false);
function windowTex(seed, pal, p, thin) {
  const r = mulberry(seed);
  return ctex(256, 512, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h); const cols = 8, rows = 16, cw = w / cols, ch = h / rows;
    for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
      if (r() > p) continue; g.fillStyle = pal[Math.floor(r() * pal.length)];
      if (thin) g.fillRect(x * cw + cw * .42, y * ch + 2, cw * .16, ch - 4); else g.fillRect(x * cw + cw * .2, y * ch + ch * .2, cw * .6, ch * .6);
    }
  });
}
const roadTex = (accent) => ctex(256, 1024, (g, w, h) => {
  g.fillStyle = '#888'; g.fillRect(0, 0, w, h); const r = mulberry(7);
  for (let i = 0; i < 5000; i++) { const v = 100 + r() * 70; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(r() * w, r() * h, 2, 2); }
  g.fillStyle = accent; for (let y = 0; y < h; y += 256) g.fillRect(w / 2 - 4, y + 20, 8, 120);
  g.fillStyle = 'rgba(230,230,230,.55)'; g.fillRect(8, 0, 5, h); g.fillRect(w - 13, 0, 5, h);
});

// ------------------------------------------------------------------ look configs
const LOOKS = {
  A: {name: 'Neon Diorama', exposure: 1.0, bloom: [0.85, 0.7, 0.45], bg: 0x0b0e36, fog: [0x1a2268, 0.0165], fogW: 0x2a3a8c, camH: 5.4, camV: 4.6, fov: 50, roll: 0.035, vig: 0.4,
    hemi: [0x7080ff, 0x20104a], pl: 150, winE: 1.5, look: 1.6, bld: [0x27358a, 0x43308e, 0x1f5a8f, 0x6a2f86, 0x31409e], win: ['#ffd27a', '#7ae9ff', '#ff8adf', '#fff2c0'], winP: 0.55, beam: 0.5, pool: 0.55, ca: 0.002},
  B: {name: 'Realistic Night', exposure: 0.95, bloom: [0.6, 0.5, 0.55], bg: 0x04060c, fog: [0x0a0f1a, 0.016], fogW: 0x141c2c, camH: 2.7, camV: 5.2, fov: 54, roll: 0.012, vig: 0.5,
    hemi: [0x303c5a, 0x0a0c12], pl: 150, winE: 0.85, look: 3.2, bld: [0x1b1d24, 0x22252d, 0x17191f, 0x2a2c33], win: ['#ffcf8a', '#ffe9c0', '#9bc8ff', '#ffb870'], winP: 0.42, beam: 0.3, pool: 0.62, ca: 0.0045},
  C: {name: 'Studio Product-Viz', exposure: 1.0, bloom: [0.7, 0.55, 0.5], bg: 0x070a24, fog: [0x0b1038, 0.0125], fogW: 0x16205a, camH: 2.3, camV: 4.2, fov: 46, roll: 0.0, vig: 0.55,
    hemi: [0x2a3a88, 0x06081c], pl: 110, winE: 1.3, look: 2.4, bld: [0x0c1130, 0x101640], win: ['#a8c0ff', '#ffffff', '#F7931E'], winP: 0.2, beam: 0.3, pool: 0.45, ca: 0.003},
};

// ------------------------------------------------------------------ street scene
const beamMat = (h) => new THREE.ShaderMaterial({
  uniforms: {uColor: {value: new THREE.Color()}, uI: {value: 1}, uH: {value: h}}, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false,
  vertexShader: 'uniform float uH;varying float vH;varying vec3 vN;varying vec3 vV;varying float vD;void main(){vec4 mv=modelViewMatrix*vec4(position,1.0);vN=normalize(normalMatrix*normal);vV=normalize(-mv.xyz);vD=length(mv.xyz);vH=position.y/uH+0.5;gl_Position=projectionMatrix*mv;}',
  fragmentShader: 'uniform vec3 uColor;uniform float uI;varying float vH;varying vec3 vN;varying vec3 vV;varying float vD;void main(){float f=pow(1.0-abs(dot(vN,vV)),1.6);float a=f*pow(vH,2.0)*uI*exp(-vD*0.05)*smoothstep(1.0,6.0,vD);gl_FragColor=vec4(uColor,a);}'
});
const addMat = (map, col = 0xffffff, op = 1, fog = false) => new THREE.MeshBasicMaterial({map, color: col, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending, fog});

function buildStreet(id) {
  const L = LOOKS[id]; const scene = new THREE.Scene(); scene.background = new THREE.Color(L.bg); scene.fog = new THREE.FogExp2(L.fog[0], L.fog[1]);
  const cam = new THREE.PerspectiveCamera(L.fov, W / H, 0.1, 600); scene.add(cam);
  const rnd = mulberry(id.charCodeAt(0) * 17);
  const hemi = new THREE.HemisphereLight(L.hemi[0], L.hemi[1], id === 'B' ? 0.5 : 0.7); scene.add(hemi);
  const moon = new THREE.DirectionalLight(0x6a7cff, 0.25); moon.position.set(-30, 60, 20); scene.add(moon);
  const env = id === 'B' ? 0.18 : 0.1; scene.environment = roomEnv;

  // --- ground
  const roadW = 15, roadLen = 520;
  if (id === 'C') {
    const mirror = new Reflector(new THREE.PlaneGeometry(260, roadLen), {textureWidth: 540, textureHeight: 960, color: 0x7a80b0, clipBias: 0.003});
    mirror.rotation.x = -Math.PI / 2; mirror.position.set(0, 0, -200); scene.add(mirror);
    const veil = new THREE.Mesh(new THREE.PlaneGeometry(260, roadLen), new THREE.MeshBasicMaterial({color: 0x04061a, transparent: true, opacity: 0.6, fog: true}));
    veil.rotation.x = -Math.PI / 2; veil.position.set(0, 0.01, -200); scene.add(veil);
    for (const x of [-2.2, 2.2]) { const ln = new THREE.Mesh(new THREE.PlaneGeometry(0.06, roadLen), new THREE.MeshBasicMaterial({color: new THREE.Color(2.2, 1.1, 0.2), fog: true})); ln.rotation.x = -Math.PI / 2; ln.position.set(x, 0.02, -200); scene.add(ln); }
  } else {
    const rt_ = roadTex(id === 'A' ? '#ff9a2a' : '#d8d8d8'); rt_.repeat.set(1, roadLen / 16);
    const road = new THREE.Mesh(new THREE.PlaneGeometry(roadW, roadLen), new THREE.MeshStandardMaterial({map: rt_, color: id === 'A' ? 0x3a4290 : 0x6a6e78, roughness: id === 'A' ? 0.55 : 0.26, metalness: id === 'A' ? 0.0 : 0.35, envMapIntensity: env}));
    road.rotation.x = -Math.PI / 2; road.position.set(0, 0, -200); scene.add(road);
    for (const s of [-1, 1]) { const sw = new THREE.Mesh(new THREE.BoxGeometry(5, 0.22, roadLen), new THREE.MeshStandardMaterial({color: id === 'A' ? 0x3a3f98 : 0x2a2b31, roughness: 0.8})); sw.position.set(s * (roadW / 2 + 2.5), 0.11, -200); scene.add(sw); }
    const gnd = new THREE.Mesh(new THREE.PlaneGeometry(400, roadLen), new THREE.MeshStandardMaterial({color: id === 'A' ? 0x0d1138 : 0x07080c, roughness: 1})); gnd.rotation.x = -Math.PI / 2; gnd.position.set(0, -0.05, -200); scene.add(gnd);
  }

  // --- buildings
  const wins = [0, 1, 2, 3, 4].map(i => windowTex(100 + i * 13 + id.charCodeAt(0), L.win, L.winP, id === 'C'));
  const addB = (x, z, w, h, d, tone) => {
    const t = wins[Math.floor(rnd() * wins.length)].clone(); t.needsUpdate = true; t.repeat.set(Math.max(1, Math.round(w / 3.4)) / 8 * 1, Math.max(1, Math.round(h / 3.6)) / 16 * 1);
    const col = L.bld[Math.floor(rnd() * L.bld.length)];
    let m;
    if (id === 'C') m = new THREE.MeshStandardMaterial({color: col, roughness: 0.18, metalness: 0.85, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: L.winE * tone, envMapIntensity: 0.5});
    else m = new THREE.MeshStandardMaterial({color: col, roughness: id === 'A' ? 0.7 : 0.88, metalness: id === 'A' ? 0.0 : 0.05, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: L.winE * tone, envMapIntensity: 0.15});
    const g = id === 'A' ? new RoundedBoxGeometry(w, h, d, 3, 0.9) : new THREE.BoxGeometry(w, h, d);
    const mesh = new THREE.Mesh(g, m); mesh.position.set(x, h / 2, z); scene.add(mesh);
  };
  for (const s of [-1, 1]) {
    let z = 40; while (z > -330) { const w = 10 + rnd() * 8, d = 11 + rnd() * 7, h = id === 'C' ? 30 + rnd() * 70 : 14 + rnd() * 44; addB(s * (id === 'C' ? 22 + rnd() * 14 : 11 + w / 2 + rnd() * 2), z - d / 2, id === 'C' ? 6 + rnd() * 6 : w, h, id === 'C' ? 6 + rnd() * 6 : d, 1); z -= d + 0.6 + rnd() * 2.5; }
    z = 30; while (z > -340) { const w = 14 + rnd() * 10, d = 14 + rnd() * 10, h = 40 + rnd() * 70; addB(s * (36 + w / 2 + rnd() * 10), z - d / 2, w, h, d, 0.7); z -= d + 3 + rnd() * 6; }
  }

  // --- lamps
  const lamps = []; const poleMat = new THREE.MeshStandardMaterial({color: id === 'A' ? 0x2e3a9a : id === 'B' ? 0x2a2d34 : 0x14183c, roughness: id === 'B' ? 0.45 : 0.4, metalness: id === 'A' ? 0.1 : 0.8, envMapIntensity: 0.6});
  const headMat = new THREE.MeshStandardMaterial({color: id === 'A' ? 0x3d4ec0 : 0x2b2e36, roughness: 0.35, metalness: id === 'A' ? 0.1 : 0.85, envMapIntensity: 0.7});
  const bH = {A: 5.0, B: 3.9, C: 3.5}[id]; const hy = 9.2; const hx = 3.7;
  let n = 0;
  for (let z = 4; z > -200; z -= 15) for (const side of [-1, 1]) {
    const g = new THREE.Group(); g.position.set(side * 7.2, 0, z);
    const lensMat = new THREE.MeshBasicMaterial({color: 0xffffff});
    if (id === 'A') {
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.25, hy, 10), poleMat); pole.position.y = hy / 2; g.add(pole);
      const arm = new THREE.Mesh(new RoundedBoxGeometry(3.6, 0.22, 0.22, 2, 0.09), poleMat); arm.position.set(-side * 1.8, hy - 0.1, 0); g.add(arm);
      const head = new THREE.Mesh(new RoundedBoxGeometry(2.0, 0.46, 1.0, 3, 0.18), headMat); head.position.set(-side * 3.5, hy - 0.1, 0); g.add(head);
      const lens = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 0.7), lensMat); lens.rotation.x = Math.PI / 2; lens.position.set(-side * 3.5, hy - 0.34, 0); g.add(lens);
    } else if (id === 'B') {
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.18, hy + 0.6, 16), poleMat); pole.position.y = (hy + 0.6) / 2; g.add(pole);
      const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, hy + 0.2, 0), new THREE.Vector3(-side * 0.5, hy + 0.9, 0), new THREE.Vector3(-side * 2.0, hy + 1.05, 0), new THREE.Vector3(-side * 3.4, hy + 0.7, 0)]);
      g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.075, 8), poleMat));
      const head = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), headMat); head.scale.set(1.2, 0.2, 0.52); head.position.set(-side * 3.6, hy + 0.55, 0); g.add(head);
      const lens = new THREE.Mesh(new THREE.PlaneGeometry(1.85, 0.7), lensMat); lens.rotation.x = Math.PI / 2; lens.position.set(-side * 3.6, hy + 0.37, 0); g.add(lens);
    } else {
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.09, hy + 0.4, 12), poleMat); pole.position.y = (hy + 0.4) / 2; g.add(pole);
      const arm = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.05, 0.08), poleMat); arm.position.set(-side * 1.75, hy + 0.3, 0); arm.rotation.z = side * 0.07; g.add(arm);
      const head = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.07, 0.6), headMat); head.position.set(-side * 3.55, hy + 0.12, 0); g.add(head);
      const lens = new THREE.Mesh(new THREE.PlaneGeometry(2.3, 0.5), lensMat); lens.rotation.x = Math.PI / 2; lens.position.set(-side * 3.55, hy + 0.08, 0); g.add(lens);
      const rim = new THREE.Mesh(new THREE.BoxGeometry(2.45, 0.02, 0.02), new THREE.MeshBasicMaterial({color: new THREE.Color(3, 1.6, 0.3)})); rim.position.set(-side * 3.55, hy + 0.17, 0.31); g.add(rim);
    }
    scene.add(g);
    const hxw = side * 7.2 - side * 3.55, hyw = id === 'A' ? hy - 0.34 : id === 'B' ? hy + 0.37 : hy + 0.08;
    const bm = beamMat(hyw); const beam = new THREE.Mesh(new THREE.ConeGeometry(bH, hyw, 40, 1, true), bm); beam.position.set(hxw, hyw / 2, z); scene.add(beam);
    const pool = new THREE.Mesh(new THREE.PlaneGeometry(id === 'B' ? 10 : 11, id === 'B' ? 15 : 11), addMat(glowTex, 0xffffff, 1, true)); pool.rotation.x = -Math.PI / 2; pool.position.set(hxw, 0.04, z); scene.add(pool);
    let streak = null;
    if (id === 'B') { streak = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 22), addMat(streakTex, 0xffffff, 1, true)); streak.rotation.x = -Math.PI / 2; streak.position.set(hxw * 0.92, 0.05, z + 11); scene.add(streak); }
    const glow = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, color: 0xffffff, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: true})); glow.scale.set(5, 5, 1); glow.position.set(hxw, hyw, z); scene.add(glow);
    lamps.push({i: n++, side, z, x: hxw, y: hyw, lensMat, beam: bm, pool, streak, glow});
  }
  const plights = [0, 1, 2, 3].map(() => { const l = new THREE.PointLight(0xffffff, 0, 36, 1.7); scene.add(l); return l; });

  // sky glow + stars + dust
  const skyGlow = new THREE.Mesh(new THREE.PlaneGeometry(420, 120), addMat(glowTex)); skyGlow.position.set(0, 18, -310); scene.add(skyGlow);
  const sp = []; const sr = mulberry(5); for (let i = 0; i < 500; i++) { const a = sr() * Math.PI * 2, e = 0.18 + sr() * 1.1, r = 400; sp.push(Math.cos(a) * Math.cos(e) * r, 40 + Math.sin(e) * r * 0.5, -Math.abs(Math.sin(a)) * Math.cos(e) * r - 20); }
  const stars = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(sp, 3)), new THREE.PointsMaterial({color: 0xcfd8ff, size: id === 'A' ? 3 : 2, sizeAttenuation: false, transparent: true, opacity: 0.8, fog: false})); scene.add(stars);
  const DN = 650; const dBase = new Float32Array(DN * 3); const dr = mulberry(21); for (let i = 0; i < DN; i++) { dBase[i * 3] = -9 + dr() * 18; dBase[i * 3 + 1] = 0.4 + dr() * 9; dBase[i * 3 + 2] = -70 + dr() * 80; }
  const dGeo = new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(DN * 3), 3));
  const dust = new THREE.Points(dGeo, new THREE.PointsMaterial({map: glowTex, size: id === 'A' ? 0.2 : 0.11, transparent: true, opacity: 0.4, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xffffff, fog: false})); scene.add(dust);

  const tmp = new THREE.Color();
  return {id, scene, cam, L, lamps, exposureK: 1,
    update(t, p) {
      const ct = p.camT ?? t, z0 = p.z0 ?? 14;
      const z = z0 - L.camV * ct, sw = Math.sin(ct * 0.45) * (id === 'A' ? 1.1 : 0.7);
      const yy = L.camH + Math.sin(ct * 0.7) * 0.12 + (p.camLift || 0);
      cam.position.set(sw + (p.camX || 0), yy, z); cam.lookAt(sw * 0.3, L.camH * 0.62 + 0.7 + L.look + (p.lookY || 0), z - 40); cam.rotation.z += L.roll * Math.sin(ct * 0.5);
      let sSum = 0, sN = 0;
      lamps.forEach(l => {
        let s = 0, pop = 0, fl = 1;
        if (p.sFixed !== undefined) s = p.sFixed; else if (p.sSide) s = l.side < 0 ? p.sSide.L : p.sSide.R;
        else if (p.flipT0 !== undefined) {
          const ts = p.flipT0 + Math.min(Math.max(0, z0 - l.z), 150) / 75 + hash(l.i) * 0.06;
          if (t >= ts) { s = 1; pop = Math.exp(-(t - ts) * 7); }
          else if (t > ts - 0.24) fl = hash(Math.floor(t * 30) * 3 + l.i) > 0.45 ? 1 : 0.12;
        }
        l.s = s; l.fl = fl; l.pop = pop;
        const col = tmp.copy(AMBER).lerp(WHITE, s); const b = fl * (1 + pop * 1.4);
        const hdr = (3.0 + 1.8 * s) * b; l.lensMat.color.setRGB(col.r * hdr, col.g * hdr, col.b * hdr);
        l.beam.uniforms.uColor.value.copy(col); l.beam.uniforms.uI.value = L.beam * (0.8 + 0.3 * s) * b;
        const pc = col.clone().multiplyScalar((L.pool * (0.62 + 0.25 * s)) * b); l.pool.material.color.copy(pc);
        if (l.streak) l.streak.material.color.copy(col.clone().multiplyScalar(0.55 * b));
        l.glow.material.color.copy(col.clone().multiplyScalar(0.3 * b * (id === 'C' ? 1.2 : 1)));
        if (Math.abs(l.z - z) < 70) { sSum += s; sN++; }
      });
      const sAvg = sN ? sSum / sN : 0;
      hemi.color.setHex(L.hemi[0]).lerp(new THREE.Color(1.0, 0.55, 0.25), (1 - sAvg) * (id === 'A' ? 0.85 : 0.55)); hemi.groundColor.setHex(L.hemi[1]);
      scene.fog.color.setHex(L.fog[0]).lerp(new THREE.Color(L.fogW), sAvg).lerp(new THREE.Color(0x3a1c08), (1 - sAvg) * (id === 'C' ? 0.15 : id === 'A' ? 0.6 : 0.35));
      scene.background.copy(scene.fog.color).multiplyScalar(id === 'A' ? 0.7 : 0.45);
      const sg = tmp.copy(AMBER).lerp(WHITE, sAvg); skyGlow.material.color.copy(sg.clone().multiplyScalar(0.16 + 0.08 * sAvg));
      const near = [...lamps].sort((a, b) => Math.abs(a.z - (z - 14)) - Math.abs(b.z - (z - 14))).slice(0, 4);
      near.forEach((l, k) => { const c = tmp.copy(AMBER).lerp(WHITE, l.s); plights[k].color.copy(c); plights[k].intensity = L.pl * l.fl * (1 + l.pop); plights[k].position.set(l.x, l.y - 0.5, l.z); });
      skyGlow.position.z = z - 280; stars.position.z = z; dust.position.z = z;
      const arr = dGeo.attributes.position.array; for (let i = 0; i < DN; i++) { arr[i * 3] = dBase[i * 3] + 0.5 * Math.sin(ct * 0.6 + i); arr[i * 3 + 1] = dBase[i * 3 + 1] + 0.25 * Math.cos(ct * 0.5 + i * 1.7); arr[i * 3 + 2] = dBase[i * 3 + 2]; }
      dGeo.attributes.position.needsUpdate = true; dust.material.color.copy(sg); NUM.set(p.num?.text, p.num?.a ?? 0, ct, p.num?.fit, true);
    }};
}

// ------------------------------------------------------------------ LED street-light head, exploded view
function buildInside(id) {
  const L = LOOKS[id]; const scene = new THREE.Scene(); const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
  const bgc = {A: ['#1b2373', '#0a0d36'], B: ['#2a2e3a', '#07080c'], C: ['#141a5a', '#04061a']}[id];
  scene.background = ctex(8, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, bgc[0]); gr.addColorStop(1, bgc[1]); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  scene.environment = roomEnv;
  const rig = new THREE.Group(); scene.add(rig);
  const metal = (c, r, m) => new THREE.MeshStandardMaterial({color: c, roughness: r, metalness: m, envMapIntensity: id === 'A' ? 0.4 : 0.9});
  const M = {
    A: {housing: metal(0x3a49c4, 0.32, 0.15), fin: metal(0x2a3590, 0.4, 0.1), mod: metal(0xe8ecf8, 0.35, 0.2), pcb: metal(0x1a1d4a, 0.5, 0.1), drv: metal(0xF7931E, 0.35, 0.15), drvFin: metal(0xd97a0c, 0.4, 0.1), lens: 0x9fb4ff},
    B: {housing: metal(0x565c6a, 0.34, 0.8), fin: metal(0x3d424d, 0.4, 0.75), mod: metal(0xb9bec8, 0.3, 0.95), pcb: metal(0x0b0c0e, 0.55, 0.2), drv: metal(0x30343c, 0.38, 0.8), drvFin: metal(0x4a4f5a, 0.42, 0.75), lens: 0xdfe8ff},
    C: {housing: metal(0x3a4380, 0.25, 0.85), fin: metal(0x262d66, 0.32, 0.8), mod: metal(0xc8cde0, 0.22, 0.98), pcb: metal(0x07080f, 0.5, 0.2), drv: metal(0x232a5c, 0.28, 0.85), drvFin: metal(0x39438a, 0.32, 0.8), lens: 0xcfdcff}
  }[id];
  const roundRect = (w, d, r) => { const s = new THREE.Shape(); const x = -w / 2, y = -d / 2; s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + d - r); s.quadraticCurveTo(x + w, y + d, x + w - r, y + d); s.lineTo(x + r, y + d); s.quadraticCurveTo(x, y + d, x, y + d - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s; };
  const slab = (w, d, h, r, mat, bev = 0.06) => { const g = new THREE.ExtrudeGeometry(roundRect(w, d, r), {depth: h, bevelEnabled: true, bevelSize: bev, bevelThickness: bev, bevelSegments: 3, curveSegments: 12}); g.rotateX(-Math.PI / 2); g.translate(0, -h / 2, 0); return new THREE.Mesh(g, mat); };
  // housing
  const housing = new THREE.Group(); housing.add(slab(3.7, 1.7, 0.7, 0.55, M.housing, 0.08));
  for (let i = -4; i <= 4; i++) { const f = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.22, 1.25), M.fin); f.position.set(i * 0.34, 0.45, 0); housing.add(f); }
  const hinge = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.5, 16), M.fin); hinge.rotation.z = Math.PI / 2; hinge.position.set(-1.8, 0.1, -0.7); housing.add(hinge);
  // driver
  const driver = new THREE.Group(); driver.add(new THREE.Mesh(new RoundedBoxGeometry(2.0, 0.5, 0.95, 4, 0.08), M.drv));
  for (let i = -3; i <= 3; i++) { const f = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.16, 0.8), M.drvFin); f.position.set(i * 0.27, 0.32, 0); driver.add(f); }
  const lab = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.3), new THREE.MeshBasicMaterial({color: 0xffffff})); lab.position.set(0, 0.0, 0.48); driver.add(lab);
  for (const sx of [-1, 1]) { const cn = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.3, 16), metal(0x222222, 0.5, 0.6)); cn.rotation.z = Math.PI / 2; cn.position.set(sx * 1.1, 0, 0); driver.add(cn); }
  const wire = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(1.2, 0, 0), new THREE.Vector3(1.7, -0.3, 0.1), new THREE.Vector3(1.9, -0.9, 0.2)]), 20, 0.04, 8), new THREE.MeshStandardMaterial({color: 0xF7931E, roughness: 0.6})); driver.add(wire);
  // module
  const module_ = new THREE.Group(); module_.add(slab(3.2, 1.4, 0.1, 0.25, M.mod, 0.03)); const pcb = slab(3.0, 1.2, 0.05, 0.2, M.pcb, 0.01); pcb.position.y = 0.08; module_.add(pcb);
  const chipGeo = new THREE.BoxGeometry(0.17, 0.05, 0.17); const chipMat = new THREE.MeshBasicMaterial({color: new THREE.Color(2.6, 2.3, 1.7)}); const chips = new THREE.InstancedMesh(chipGeo, chipMat, 40); const d = new THREE.Object3D();
  let k = 0; for (let x = 0; x < 10; x++) for (let z = 0; z < 4; z++) { d.position.set(-1.24 + x * 0.275, 0.14, -0.45 + z * 0.3); d.updateMatrix(); chips.setMatrixAt(k++, d.matrix); } module_.add(chips);
  const chipGlow = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, color: new THREE.Color(1, 0.8, 0.5), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.3})); chipGlow.scale.set(3.6, 1.8, 1); chipGlow.position.y = 0.3; module_.add(chipGlow);
  // lens
  const lens = new THREE.Group(); lens.add(slab(3.3, 1.5, 0.08, 0.3, new THREE.MeshPhysicalMaterial({color: M.lens, roughness: 0.15, metalness: 0, transparent: true, opacity: 0.38, clearcoat: 1, envMapIntensity: 1.2}), 0.04));
  const domeGeo = new THREE.SphereGeometry(0.15, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2); const domeMat = new THREE.MeshPhysicalMaterial({color: 0xffffff, roughness: 0.05, transparent: true, opacity: 0.55, clearcoat: 1}); const domes = new THREE.InstancedMesh(domeGeo, domeMat, 40); k = 0;
  for (let x = 0; x < 10; x++) for (let z = 0; z < 4; z++) { d.position.set(-1.24 + x * 0.275, 0.08, -0.45 + z * 0.3); d.updateMatrix(); domes.setMatrixAt(k++, d.matrix); } lens.add(domes);
  rig.add(housing, driver, module_, lens);
  // lights
  const key = new THREE.DirectionalLight(0xffffff, id === 'A' ? 2.0 : 2.4); key.position.set(4, 9, 7); scene.add(key); const fill = new THREE.DirectionalLight(0xdfe6ff, 0.9); fill.position.set(-5, 3, 8); scene.add(fill);
  const rim = new THREE.DirectionalLight(0xF7931E, 2.4); rim.position.set(-6, 3, -5); scene.add(rim);
  const rim2 = new THREE.DirectionalLight(0x6a8cff, 1.2); rim2.position.set(6, 2, -4); scene.add(rim2);
  scene.add(new THREE.AmbientLight(0xffffff, id === 'A' ? 0.7 : 0.25));
  // floor
  if (id === 'C') {
    const mirror = new Reflector(new THREE.PlaneGeometry(60, 60), {textureWidth: 540, textureHeight: 960, color: 0x777faa, clipBias: 0.003}); mirror.rotation.x = -Math.PI / 2; mirror.position.y = -4.2; scene.add(mirror);
    const veil = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshBasicMaterial({color: 0x04061a, transparent: true, opacity: 0.5})); veil.rotation.x = -Math.PI / 2; veil.position.y = -4.19; scene.add(veil);
  } else if (id === 'A') { const fl = new THREE.Mesh(new THREE.CircleGeometry(5, 64), addMat(glowTex, 0x4a5cff, 0.9)); fl.rotation.x = -Math.PI / 2; fl.position.y = -4.2; fl.scale.set(1.6, 1.6, 1); scene.add(fl); }
  const halo = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), addMat(glowTex, id === 'B' ? 0x6a5030 : 0xF7931E, id === 'B' ? 0.28 : 0.2)); halo.position.set(0, 0.5, -3); scene.add(halo);
  const pts = []; const pr = mulberry(33); for (let i = 0; i < 160; i++) pts.push((pr() - .5) * 10, (pr() - .5) * 9, -3 + pr() * 4);
  const sparks = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(pts, 3)), new THREE.PointsMaterial({map: glowTex, size: 0.18, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xF7931E, opacity: 0.7})); scene.add(sparks);
  const beamM = beamMat(6.5); beamM.uniforms.uColor.value.copy(WHITE); const beam = new THREE.Mesh(new THREE.ConeGeometry(3.4, 6.5, 40, 1, true), beamM); beam.position.y = -0.6 - 3.25; scene.add(beam);
  const underGlow = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, color: new THREE.Color(1, 0.97, 0.9), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0})); underGlow.scale.set(7, 3.2, 1); scene.add(underGlow);
  const V = new THREE.Vector3();
  const api = {id, scene, cam, L, exposureK: 0.9, bloomK: 0.6,
    update(t, p) {
      const e = p.explode ?? 1, ee = e * e * (3 - 2 * e); const st = (a) => clamp(ee * 1.0 + a);
      housing.position.y = 3.15 * clamp(ee * 1.1); driver.position.y = 1.55 * clamp(ee * 1.05) + 0.1 - 0.1; module_.position.y = 0; lens.position.y = -1.55 * clamp(ee * 1.05);
      driver.position.y = 0.2 + (1.15 - 0.2) * clamp(ee * 1.05); module_.position.y = -0.3 + 0.3 * clamp(ee);
      housing.position.y = 0.3 + 2.35 * clamp(ee * 1.1); lens.position.y = -0.55 - 0.82 * clamp(ee * 1.05);
      const on = p.on ?? 1; chipMat.color.setRGB(2.6 * on + 0.3, 2.3 * on + 0.3, 1.7 * on + 0.3); chipGlow.material.opacity = 0.08 + 0.25 * on;
      const th = (p.orbit ?? 0) * 1 + Math.sin(t * 0.5) * 0.25; const R = p.dist ?? 26;
      cam.position.set(Math.sin(th) * R, 3.4 + (p.elev ?? 4.2), Math.cos(th) * R); cam.lookAt(0, 0.6 + (p.lookY ?? 0.5), 0);
      rig.rotation.y = p.spin ?? 0; sparks.rotation.y = t * 0.1; rig.position.y = Math.sin(t * 0.9) * 0.06;
      beamM.uniforms.uI.value = 0.75 * (p.beam ?? 0); underGlow.material.opacity = 0.95 * (p.beam ?? 0); underGlow.position.y = lens.position.y - 0.2;
    },
    project(name) { const o = {module: module_, driver: driver, housing, lens}[name]; V.set(name === 'module' ? 1.6 : 1.1, 0.1, 0.35); o.localToWorld(V); V.project(cam); return [(V.x * 0.5 + 0.5) * W, (-V.y * 0.5 + 0.5) * H]; }};
  return api;
}

// ------------------------------------------------------------------ end screen backdrop
function buildCTA(id) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color(0x1B1F54); const cam = new THREE.PerspectiveCamera(36, W / H, 0.1, 100); cam.position.set(0, 0, 14);
  const g1 = new THREE.Mesh(new THREE.PlaneGeometry(26, 26), addMat(glowTex, 0xF7931E, id === 'B' ? 0.28 : 0.36)); g1.position.set(-3, 6.5, -3); scene.add(g1);
  const g2 = new THREE.Mesh(new THREE.PlaneGeometry(22, 22), addMat(glowTex, 0x2a3aa8, 0.16)); g2.position.set(5, -6, -4); scene.add(g2);
  scene.add(new THREE.HemisphereLight(0x8090ff, 0x1B1F54, 1.0)); const dl = new THREE.DirectionalLight(0xffffff, 2); dl.position.set(3, 5, 8); scene.add(dl);
  const items = new THREE.Group(); scene.add(items); const r = mulberry(9);
  if (id === 'A') {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(3.4, 0.5, 24, 80), new THREE.MeshStandardMaterial({color: 0xF7931E, roughness: 0.3, emissive: 0xF7931E, emissiveIntensity: 0.9})); ring.position.set(0, 6.4, -3); items.add(ring);
    for (let i = 0; i < 40; i++) { const s = new THREE.Mesh(new THREE.IcosahedronGeometry(0.1 + r() * 0.2, 0), new THREE.MeshBasicMaterial({color: new THREE.Color(2, 1.2, .4)})); s.position.set((r() - .5) * 18, (r() - .5) * 28, -2 - r() * 4); items.add(s); }
  } else if (id === 'B') {
    for (let i = 0; i < 46; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, color: r() > .5 ? new THREE.Color(1, .55, .15) : new THREE.Color(.6, .7, 1), transparent: true, opacity: .12 + r() * .3, depthWrite: false, blending: THREE.AdditiveBlending})); const sc = 1 + r() * 3.5; s.scale.set(sc, sc, 1); s.position.set((r() - .5) * 18, (r() - .5) * 30, -2 - r() * 6); items.add(s); }
  } else {
    const mirror = new Reflector(new THREE.PlaneGeometry(60, 60), {textureWidth: 540, textureHeight: 960, color: 0x666fa0, clipBias: 0.003}); mirror.rotation.x = -Math.PI / 2; mirror.position.y = -8; scene.add(mirror);
    const veil = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshBasicMaterial({color: 0x10143c, transparent: true, opacity: 0.6})); veil.rotation.x = -Math.PI / 2; veil.position.y = -7.99; scene.add(veil);
    const bar = new THREE.Mesh(new THREE.BoxGeometry(11, 0.14, 0.14), new THREE.MeshBasicMaterial({color: new THREE.Color(5, 2.6, .5)})); bar.position.set(0, -7.4, -3); items.add(bar);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(3.0, 0.08, 16, 100), new THREE.MeshBasicMaterial({color: new THREE.Color(4, 2, .4)})); ring.position.set(0, 6.8, -3); items.add(ring);
  }
  return {id, scene, cam, L: LOOKS[id], update(t) { items.rotation.y = Math.sin(t * 0.4) * 0.15; items.position.y = Math.sin(t * 0.6) * 0.15; }};
}


// ------------------------------------------------------------------ real 3D numbers (TextGeometry, counted up per frame)
const FONT = new FontLoader().parse(await (await fetch('node_modules/three/examples/fonts/helvetiker_bold.typeface.json')).json());
const gcache = {};
const numScene = new THREE.Scene(); numScene.environment = roomEnv; const numCam = new THREE.PerspectiveCamera(50, W / H, 0.1, 50);
numScene.add(new THREE.HemisphereLight(0xdfe6ff, 0x33406e, 1.2)); const nd = new THREE.DirectionalLight(0xffffff, 2.4); nd.position.set(-3, 5, 6); numScene.add(nd);
const nd2 = new THREE.DirectionalLight(0xF7931E, 1.6); nd2.position.set(4, -2, 3); numScene.add(nd2);
const glyph = ch => gcache[ch] || (gcache[ch] = new TextGeometry(ch, {font: FONT, size: 1, height: 0.34, curveSegments: 8, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.035, bevelSegments: 4}));
const adv = ch => ((FONT.data.glyphs[ch] || FONT.data.glyphs['0']).ha) / FONT.data.resolution;
const easeBack = x => { x = clamp(x); const c = 1.5; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
function makeNumber() {
  const root = new THREE.Group(); root.position.set(0, 0.58, -8.6); const holder = new THREE.Group(); root.add(holder);
  const face = new THREE.MeshStandardMaterial({color: 0xa9b4dc, roughness: 0.3, metalness: 0.25, emissive: new THREE.Color(0x6f7ab0), emissiveIntensity: 0.1, envMapIntensity: 0.6, fog: false});
  const side = new THREE.MeshStandardMaterial({color: 0xF7931E, roughness: 0.4, metalness: 0.3, emissive: new THREE.Color(0xF7931E), emissiveIntensity: 0.25, envMapIntensity: 0.6, fog: false});
  
  let key = '';
  const FACE_LIGHT = new THREE.Color(0xeef2ff), FACE_DARK = new THREE.Color(0xeef2ff);
  const plateTex = ctex(512, 192, (g, w, h) => { g.fillStyle = 'rgba(27,31,84,0.86)'; g.beginPath(); g.roundRect(6, 6, w - 12, h - 12, 44); g.fill(); g.strokeStyle = 'rgba(247,147,30,0.9)'; g.lineWidth = 5; g.stroke(); });
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 1.42), new THREE.MeshBasicMaterial({map: plateTex, transparent: true, depthWrite: false, fog: false, toneMapped: false})); plate.position.set(0, 0.0, -0.5); plate.renderOrder = -1; root.add(plate);
  return {root, set(text, appear, t, fit, dark) {
    if (!text || appear <= 0.001) { root.visible = false; return; }
    root.visible = true; face.color.copy(dark ? FACE_DARK : FACE_LIGHT); face.emissive.set(0x8a96c8); face.emissiveIntensity = 0.12; side.emissiveIntensity = 0.3; plate.visible = true; const fk = text + '|' + (fit || '');
    if (key !== fk) { key = fk; holder.clear(); const total = [...(fit || text)].reduce((a, c) => a + adv(c), 0); let x = -total / 2;
      for (const ch of text) { if (ch !== ' ') { const m = new THREE.Mesh(glyph(ch), [face, side]); m.position.x = x; holder.add(m); } x += adv(ch); } holder.userData.total = total; }
    const sc = (3.6 / holder.userData.total) * (0.65 + 0.35 * easeBack(appear)); holder.scale.setScalar(sc); holder.position.y = -0.36 * sc;
    root.rotation.y = Math.sin(t * 0.9) * 0.12; root.rotation.x = (1 - clamp(appear)) * -0.9 + Math.sin(t * 0.7) * 0.03;
  }};
}

const NUM = makeNumber(); numScene.add(NUM.root);
// ------------------------------------------------------------------ aerial city
function buildCity() {
  const L = LOOKS.B; const scene = new THREE.Scene(); scene.background = new THREE.Color(0x05070d); scene.fog = new THREE.FogExp2(0x0a0f1a, 0.0014);
  const cam = new THREE.PerspectiveCamera(50, W / H, 0.5, 2600); scene.add(cam);
  const rnd = mulberry(77);
  const hemi = new THREE.HemisphereLight(0x303c5a, 0x0a0c12, 0.6); scene.add(hemi); const moon = new THREE.DirectionalLight(0x6a7cff, 0.35); moon.position.set(-60, 120, 40); scene.add(moon);
  scene.environment = roomEnv;
  const gt = ctex(512, 512, (g, w, h) => { g.fillStyle = '#05060a'; g.fillRect(0, 0, w, h); const rw = 14 / 44 * w; g.fillStyle = '#12141a'; g.fillRect(0, 0, rw / 2, h); g.fillRect(w - rw / 2, 0, rw / 2, h); g.fillRect(0, 0, w, rw / 2); g.fillRect(0, h - rw / 2, w, rw / 2);
    g.fillStyle = 'rgba(220,220,220,.3)'; for (let y = 0; y < h; y += 44) { g.fillRect(0, y + 6, 3, 18); g.fillRect(w - 3, y + 6, 3, 18); } for (let x = 0; x < w; x += 44) { g.fillRect(x + 6, 0, 18, 3); g.fillRect(x + 6, h - 3, 18, 3); } });
  gt.repeat.set(16, 24); const ground = new THREE.Mesh(new THREE.PlaneGeometry(704, 1056), new THREE.MeshStandardMaterial({map: gt, roughness: 0.4, metalness: 0.3, envMapIntensity: 0.1})); ground.rotation.x = -Math.PI / 2; ground.position.set(0, 0, -396); scene.add(ground);
  const wt = windowTex(301, L.win, 0.5, false); wt.repeat.set(1, 1.5);
  const bm = new THREE.MeshStandardMaterial({color: 0x1b1d24, roughness: 0.85, emissive: 0xffffff, emissiveMap: wt, emissiveIntensity: 0.85, envMapIntensity: 0.1});
  const bl = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), bm, 1300); let bi = 0; const o = new THREE.Object3D(); const col = new THREE.Color();
  for (let i = -8; i < 8; i++) for (let j = 3; j > -13; j--) {
    const cx = 44 * i + 22, cz = 44 * j - 22; const n = rnd() < 0.35 ? 1 : 2 + Math.floor(rnd() * 2); const centre = 1 - Math.min(1, Math.hypot(cx, cz + 100) / 360);
    for (let k = 0; k < n; k++) { const w = n === 1 ? 22 + rnd() * 6 : 11 + rnd() * 7, d = n === 1 ? 22 + rnd() * 6 : 11 + rnd() * 7; const h = 6 + rnd() * 13 + centre * rnd() * 34 * (rnd() < 0.25 ? 1.7 : 0.5);
      const px = cx + (n === 1 ? 0 : (k % 2 ? 8 : -8) + (rnd() - 0.5) * 3), pz = cz + (n === 1 ? 0 : (k > 1 ? 8 : -8) + (rnd() - 0.5) * 3);
      if (bi >= 1300) break; o.position.set(px, h / 2, pz); o.scale.set(w, h, d); o.updateMatrix(); bl.setMatrixAt(bi, o.matrix); col.setHSL(0.62 + rnd() * 0.06, 0.2, 0.55 + rnd() * 0.5); bl.setColorAt(bi, col); bi++; }
  }
  bl.count = bi; scene.add(bl);
  // lamps along every road
  const lp = []; const roads = (axis, c, lo, hi) => { for (let p = lo; p <= hi; p += 16) for (const sd of [-8, 8]) lp.push(axis === 'z' ? [c + sd, p] : [p, c + sd]); };
  for (let i = -8; i <= 8; i++) roads('z', 44 * i, -520, 130);
  for (let j = 3; j >= -11; j--) roads('x', 44 * j, -350, 350);
  const LN = lp.length; const pools = new THREE.InstancedMesh(new THREE.PlaneGeometry(13, 13), new THREE.MeshBasicMaterial({map: glowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: true, opacity: 0.55}), LN);
  const pos = new Float32Array(LN * 3), cols = new Float32Array(LN * 3); const lampOrigin = [0, -60];
  const dist = new Float32Array(LN); const jit = new Float32Array(LN);
  lp.forEach((q, i) => { o.position.set(q[0], 0.05, q[1]); o.rotation.set(-Math.PI / 2, 0, 0); o.scale.set(1, 1, 1); o.updateMatrix(); pools.setMatrixAt(i, o.matrix); pos.set([q[0], 9.2, q[1]], i * 3); dist[i] = Math.hypot(q[0] - lampOrigin[0], q[1] - lampOrigin[1]); jit[i] = hash(i) * 0.4; });
  pools.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(LN * 3), 3); pools.frustumCulled = false; scene.add(pools);
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pos, 3)); pg.setAttribute('color', new THREE.BufferAttribute(cols, 3));
  const heads = new THREE.Points(pg, new THREE.PointsMaterial({map: glowTex, size: 3.2, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true})); heads.frustumCulled = false; scene.add(heads);
  const skyGlow = new THREE.Mesh(new THREE.PlaneGeometry(2600, 520), addMat(glowTex)); scene.add(skyGlow);
  const tmp = new THREE.Color();
  return {id: 'city', scene, cam, L, exposureK: 1, bloomK: 0.7,
    update(t, p) {
      const u = t, y = 6 + 270 * sstep(0, 3.6, u) + 3 * Math.max(0, u - 3.6), z = 70 - 26 * u, x = Math.sin(u * 0.25) * 18;
      const pitch = (3 + 58 * sstep(0.3, 3.8, u)) * Math.PI / 180; cam.position.set(x, y, z);
      cam.lookAt(x * 0.6 + Math.sin(u * 0.2) * 10, y - Math.sin(pitch) * 100, z - Math.cos(pitch) * 100); cam.rotation.z += 0.012 * Math.sin(u * 0.5);
      const t0 = p.sweepT0 ?? 1.2, spd = 175; let sSum = 0;
      for (let i = 0; i < LN; i++) {
        const ts = t0 + dist[i] / spd + jit[i] * 0.3; let s = 0, pop = 0, fl = 1;
        if (t >= ts) { s = Math.min(1, (t - ts) / 0.25); pop = Math.exp(-(t - ts) * 5); } else if (t > ts - 0.2) fl = hash(Math.floor(t * 30) * 3 + i) > 0.5 ? 1 : 0.2;
        sSum += s; tmp.copy(AMBER).lerp(WHITE, s); const b = fl * (1 + pop * 1.2);
        const pi = i * 3; cols[pi] = tmp.r * b * 1.6; cols[pi + 1] = tmp.g * b * 1.6; cols[pi + 2] = tmp.b * b * 1.6;
        pools.instanceColor.array[pi] = tmp.r * b * (0.55 + 0.2 * s); pools.instanceColor.array[pi + 1] = tmp.g * b * (0.55 + 0.2 * s); pools.instanceColor.array[pi + 2] = tmp.b * b * (0.55 + 0.2 * s);
      }
      pg.attributes.color.needsUpdate = true; pools.instanceColor.needsUpdate = true;
      const sAvg = sSum / LN; hemi.color.setHex(0x303c5a).lerp(new THREE.Color(1, 0.55, 0.25), (1 - sAvg) * 0.5);
      scene.fog.color.setHex(0x0a0f1a).lerp(new THREE.Color(0x3a1c08), (1 - sAvg) * 0.35).lerp(new THREE.Color(0x1c2638), sAvg);
      scene.background.copy(scene.fog.color).multiplyScalar(0.45);
      skyGlow.material.color.copy(tmp.copy(AMBER).lerp(WHITE, sAvg).multiplyScalar(0.22)); skyGlow.position.set(0, 120, z - 1200);
      NUM.set(p.num?.text, p.num?.a ?? 0, u, p.num?.fit);
    }};
}

// ------------------------------------------------------------------ sodium macro + colour ring
function buildSodium() {
  const L = LOOKS.B; const scene = new THREE.Scene(); scene.background = new THREE.Color(0x05040a); scene.fog = new THREE.FogExp2(0x0b0705, 0.018);
  const cam = new THREE.PerspectiveCamera(50, W / H, 0.1, 200); scene.add(cam); scene.environment = roomEnv;
  scene.add(new THREE.HemisphereLight(0x30241a, 0x050403, 0.3));
  const lamp = new THREE.Group(); lamp.position.set(0, 7.6, 0); scene.add(lamp);
  const metal = new THREE.MeshStandardMaterial({color: 0x3a3631, roughness: 0.55, metalness: 0.8, envMapIntensity: 0.5});
  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), metal); head.scale.set(2.9, 0.62, 1.4); lamp.add(head);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(1, 0.05, 12, 64), metal); rim.rotation.x = Math.PI / 2; rim.scale.set(2.5, 1.2, 1); rim.position.y = -0.32; lamp.add(rim);
  const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.3, 4, 16), metal); arm.position.set(2.0, 1.6, 0); arm.rotation.z = -0.5; lamp.add(arm);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), new THREE.MeshBasicMaterial({color: new THREE.Color(2.6, 1.3, 0.25), transparent: true, opacity: 0.9})); dome.scale.set(2.3, 0.7, 1.05); dome.position.y = -0.3; lamp.add(dome);
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 2.6, 16), new THREE.MeshBasicMaterial({color: new THREE.Color(6, 3.4, 0.6)})); tube.rotation.z = Math.PI / 2; tube.position.y = -0.4; lamp.add(tube);
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, color: new THREE.Color(1, 0.55, 0.12), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.9})); glow.scale.set(8, 5, 1); glow.material.opacity = 0.4; glow.position.y = -0.4; lamp.add(glow);
  const bm = beamMat(7.4); bm.uniforms.uColor.value.set(1, 0.52, 0.1); bm.uniforms.uI.value = 0.28; const beam = new THREE.Mesh(new THREE.ConeGeometry(4.6, 7.4, 48, 1, true), bm); beam.position.set(0, 3.7 + 0.1, 0); scene.add(beam);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({color: 0x08090c, roughness: 0.22, metalness: 0.4, envMapIntensity: 0.3})); floor.rotation.x = -Math.PI / 2; scene.add(floor);
  const pool = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), addMat(glowTex, new THREE.Color(1, 0.5, 0.1), 0.8, true)); pool.rotation.x = -Math.PI / 2; pool.position.y = 0.03; scene.add(pool);
  const amber = new THREE.PointLight(0xff8a1f, 26, 34, 1.5); amber.position.set(0, 6.6, 1.5); scene.add(amber);
  const white = new THREE.PointLight(0xffffff, 22, 30, 1.6); white.position.set(2, 5.5, 7); scene.add(white);
  const ring = new THREE.Group(); ring.position.set(0, 2.7, 0); scene.add(ring);
  const defs = [[0xe02020, 'sphere'], [0x20c040, 'box'], [0x2f5bff, 'ico'], [0xffd020, 'torus']]; const objs = [];
  for (let i = 0; i < 8; i++) { const [c, k] = defs[i % 4]; const g = {sphere: new THREE.SphereGeometry(0.55, 32, 16), box: new THREE.BoxGeometry(0.9, 0.9, 0.9), ico: new THREE.IcosahedronGeometry(0.62, 1), torus: new THREE.TorusGeometry(0.46, 0.18, 16, 40)}[k];
    const m = new THREE.MeshStandardMaterial({color: c, roughness: 0.4, metalness: 0.05, envMapIntensity: 0.15}); const mesh = new THREE.Mesh(g, m); const a = i / 8 * Math.PI * 2; mesh.scale.setScalar(0.8); mesh.position.set(Math.cos(a) * 2.2, 0, Math.sin(a) * 2.2); mesh.userData = {base: new THREE.Color(c), a}; ring.add(mesh); objs.push(mesh); }
  const SODIUM_FLAT = new THREE.Color(0.9, 0.42, 0.07); const dp = []; const dr = mulberry(12); for (let i = 0; i < 300; i++) dp.push((dr() - .5) * 14, dr() * 9, (dr() - .5) * 12);
  const dust = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(dp, 3)), new THREE.PointsMaterial({map: glowTex, size: 0.14, transparent: true, opacity: 0.4, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xff9a30})); scene.add(dust);
  return {id: 'sodium', scene, cam, L, exposureK: 0.85, bloomK: 0.6,
    update(t, p) {
      const d = clamp(p.drain ?? 0);
      ring.rotation.y = t * 0.4; ring.position.y = 2.7 + Math.sin(t * 0.8) * 0.12;
      objs.forEach((m, i) => { m.rotation.x = t * (0.5 + i * 0.07); m.rotation.y = t * 0.6; m.material.color.copy(m.userData.base).lerp(SODIUM_FLAT, d * 0.92); m.material.roughness = 0.32 + 0.3 * d; });
      white.intensity = 22 * (1 - d); amber.intensity = 28 * (0.5 + 0.5 * d); dust.rotation.y = t * 0.05;
      const z = 14.5 - 0.3 * t; cam.position.set(Math.sin(t * 0.3) * 1.0, 1.9 + Math.sin(t * 0.5) * 0.1, z); cam.lookAt(0, 4.1, 0);
    }};
}

// ------------------------------------------------------------------ engine API + shots
const cache = {};
const get = (kind, id) => { const k = kind + id; if (!cache[k]) cache[k] = {street: buildStreet, inside: buildInside, cta: buildCTA, city: buildCity, sodium: buildSodium}[kind](id); return cache[k]; };
const WORDS = await (await fetch('assets/words.json')).json();
const hud = createHUD(document.getElementById('hud'), WORDS.words);
await document.fonts.ready;
for (const f of ['400 20px IX', '600 20px IX', '700 20px IX', '900 20px ID', '800 20px ID', '500 20px JB']) await document.fonts.load(f);
const E = {THREE, W, H, get, hud, words: WORDS.words, clamp, lerp, sstep, AMBER, WHITE, LOOKS};
const SHOTS = makeShots(E);
window.renderShot = (name, look, t) => {
  NUM.root.visible = false; const sh = SHOTS[name]; const r = sh(look, t); const L = r.sc.L || LOOKS[look];       // r: {sc, state}
  renderer.toneMappingExposure = L.exposure * (r.sc.exposureK ?? 1);
  bloom.strength = L.bloom[0] * (r.sc.bloomK ?? 1); bloom.radius = L.bloom[1]; bloom.threshold = L.bloom[2];
  finalPass.uniforms.uTime.value = t; finalPass.uniforms.uVig.value = L.vig; finalPass.uniforms.uCA.value = L.ca ?? 0.003;
  renderPass.scene = r.sc.scene; renderPass.camera = r.sc.cam; r.sc.cam.updateProjectionMatrix(); r.sc.cam.updateMatrixWorld();
  NUM.root.visible = NUM.root.visible; composer.render();
  if (NUM.root.visible) { renderer.autoClear = false; renderer.clearDepth(); renderer.toneMappingExposure = 1.0; renderer.render(numScene, numCam); renderer.autoClear = true; }
  hud.apply(r.state(r.sc)); window.__cam = [r.sc.id, ...r.sc.cam.position.toArray().map(v => +v.toFixed(1))];
  return true;
};
window.ready = true;
