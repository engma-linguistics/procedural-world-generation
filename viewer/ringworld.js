// Ringworld look demo (PW-803): a star, a thin ribbon ring, rim walls, shadow squares. No simulation: the land is value
// noise coloured with the viewer's biome palette (planet/climate.py BIOMES).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { wheelZoom } from './wheelzoom.js';

const BIOMES = [  // id, name, colour: copied from planet/climate.py BIOMES
  [0, 'deep ocean', '#1d3f6e'], [1, 'shallow sea', '#3a6ea5'], [2, 'sea ice', '#d8e6ef'], [4, 'ice sheet', '#f4f7fa'],
  [5, 'tundra', '#9aa58a'], [6, 'boreal forest', '#3f6b4d'], [7, 'cold desert', '#b7ad8f'], [8, 'temperate grassland', '#a9b964'],
  [9, 'temperate forest', '#4d8a3a'], [10, 'temperate rainforest', '#2f6e4a'], [11, 'hot desert', '#e0c68a'], [12, 'savanna', '#c2b553'],
  [13, 'tropical seasonal forest', '#6a9a2f'], [14, 'tropical rainforest', '#2a7a2a'], [15, 'alpine / bare rock', '#8b8178']];
const COL = {}; for (const [id, , c] of BIOMES) COL[id] = new THREE.Color(c);

const $ = (id) => document.getElementById(id);
const R = 100;            // ring radius (scene units); the star sits at the origin; the ring's axis is z
const BASE_W = 0.04;      // ring width / radius at exaggeration 1
const NU = 1536, NV = 40; // surface grid: around, across
const R_SHADOW = 0.42 * R; // orbit radius of the shadow squares
const TAU = Math.PI * 2;

// ---------------------------------------------------------------- cheap noise (periodic around the ring)
function hash(ix, iy) { let h = (ix * 374761393 + iy * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177 | 0; return ((h ^ (h >>> 16)) >>> 0) / 4294967295; }
function vnoise(x, y, period) {
  const x0 = Math.floor(x), y0 = Math.floor(y), fx = x - x0, fy = y - y0;
  const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
  const w = (i) => ((i % period) + period) % period;
  const a = hash(w(x0), y0), b = hash(w(x0 + 1), y0), c = hash(w(x0), y0 + 1), d = hash(w(x0 + 1), y0 + 1);
  return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
}
function fbm(u, v, base, seed) {  // u in [0,1) around the ring, v in [-1,1] across
  let s = 0, amp = 0.5, tot = 0, per = base;
  for (let o = 0; o < 5; o++) { s += amp * vnoise(u * per, v * per * 0.08 + seed + o * 17, per); tot += amp; amp *= 0.5; per *= 2; }
  return s / tot;
}

// ---------------------------------------------------------------- scene
const renderer = new THREE.WebGLRenderer({ canvas: $('c'), antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070c);
const camera = new THREE.PerspectiveCamera(60, 1, 0.05, 6000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
wheelZoom(controls, renderer.domElement);

// background stars
{
  const n = 1500, p = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const a = Math.random() * TAU, z = Math.random() * 2 - 1, r = Math.sqrt(1 - z * z); p.set([4000 * r * Math.cos(a), 4000 * r * Math.sin(a), 4000 * z], i * 3); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xbfc8d8, size: 2, sizeAttenuation: false })));
}

// the star: a bright ball and an additive glow
const star = new THREE.Mesh(new THREE.SphereGeometry(5, 32, 16), new THREE.MeshBasicMaterial({ color: 0xfff3d0 }));
scene.add(star);
{
  const cv = document.createElement('canvas'); cv.width = cv.height = 128;
  const x = cv.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,244,214,1)'); g.addColorStop(0.15, 'rgba(255,226,160,.6)'); g.addColorStop(1, 'rgba(255,200,120,0)');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
  sp.scale.set(60, 60, 1); star.add(sp);
}

// ---------------------------------------------------------------- the ring surface: colours once, positions on demand
const nVert = (NU + 1) * (NV + 1);
const alt = new Float32Array(nVert);
const colors = new Float32Array(nVert * 3);
{
  const tmp = new THREE.Color();
  for (let j = 0; j <= NV; j++) for (let i = 0; i <= NU; i++) {
    const k = j * (NU + 1) + i, u = (i % NU) / NU, v = (j / NV) * 2 - 1;
    const e = fbm(u, v, 56, 3), m = fbm(u, v, 40, 41), d = fbm(u, v, 300, 7);
    const a = e - 0.5;
    const rim = Math.pow(Math.abs(v), 1.6);
    const t = 1.05 - 0.95 * rim + 0.2 * (fbm(u, v, 30, 90) - 0.5) - 0.35 * Math.max(a, 0);
    let b;
    if (a < 0) b = t < 0.1 ? 2 : (a < -0.07 ? 0 : 1);
    else if (a > 0.17) b = t < 0.1 ? 4 : 15;
    else if (t < 0.12) b = 4;
    else if (t < 0.26) b = 5;
    else if (t < 0.4) b = m > 0.45 ? 6 : 7;
    else if (t < 0.62) b = m < 0.38 ? 8 : (m < 0.55 ? 9 : 10);
    else b = m < 0.4 ? 11 : (m < 0.52 ? 12 : (m < 0.64 ? 13 : 14));
    tmp.copy(COL[b]);
    if (a >= 0) tmp.multiplyScalar(0.86 + 0.28 * d + 0.5 * Math.max(a, 0)); else tmp.multiplyScalar(0.92 + 0.16 * d);
    colors.set([tmp.r, tmp.g, tmp.b], k * 3);
    alt[k] = Math.max(a, 0);
  }
}
const surfGeom = new THREE.BufferGeometry();
surfGeom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(nVert * 3), 3));
surfGeom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
{
  const idx = [];
  for (let j = 0; j < NV; j++) for (let i = 0; i < NU; i++) { const a = j * (NU + 1) + i, b = a + 1, c = a + NU + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
  surfGeom.setIndex(idx);
}
const surfMat = new THREE.ShaderMaterial({
  side: THREE.DoubleSide,
  uniforms: { uPhase: { value: 0 }, uN: { value: 10 }, uHalf: { value: 0.2 } },  // phase: shadow rotation (rad); half: half-angle of one shadow
  vertexShader: `varying vec3 vC; varying float vTh;
    void main(){ vC = color; vTh = atan(position.y, position.x); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }`,
  fragmentShader: `varying vec3 vC; varying float vTh; uniform float uPhase, uN, uHalf;
    void main(){
      float cell = 6.2831853 / uN;
      float d = abs(fract((vTh - uPhase) / cell + 0.5) - 0.5) * cell;     // angular distance to the nearest square
      float shade = 1.0 - smoothstep(uHalf - 0.012, uHalf + 0.012, d);   // soft edge: the star is not a point
      vec3 night = vC * vec3(0.13, 0.16, 0.26);
      gl_FragColor = vec4(mix(vC, night, shade), 1.);
    }`,
  vertexColors: true,
});
const surface = new THREE.Mesh(surfGeom, surfMat);
surface.frustumCulled = false;
scene.add(surface);

// hull (outside), walls (both rims)
const hull = new THREE.Mesh(new THREE.CylinderGeometry(R + 0.4, R + 0.4, 1, 192, 1, true).rotateX(Math.PI / 2),
  new THREE.MeshBasicMaterial({ color: 0x3a4250 }));
scene.add(hull);
const wallGeom = new THREE.BufferGeometry();
const wallPos = new Float32Array(2 * 2 * (NU + 1) * 3);
wallGeom.setAttribute('position', new THREE.BufferAttribute(wallPos, 3));
{
  const idx = [], seg = NU + 1;
  for (let s = 0; s < 2; s++) for (let i = 0; i < NU; i++) { const a = s * 2 * seg + i * 2, b = a + 2; idx.push(a, a + 1, b, b, a + 1, b + 1); }
  wallGeom.setIndex(idx);
}
const wall = new THREE.Mesh(wallGeom, new THREE.MeshBasicMaterial({ color: 0x6d6f78, side: THREE.DoubleSide }));
wall.frustumCulled = false;
scene.add(wall);

// shadow squares: thin plates on an inner orbit, as wide as the ring, facing the star
const sqGroup = new THREE.Group(); scene.add(sqGroup);
const sqMat = new THREE.MeshBasicMaterial({ color: 0x4a5f82 });
scene.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(
  Array.from({ length: 129 }, (_, i) => new THREE.Vector3(R_SHADOW * Math.cos(i / 128 * TAU), R_SHADOW * Math.sin(i / 128 * TAU), 0))),
  new THREE.LineBasicMaterial({ color: 0x35435c, transparent: true, opacity: 0.6 })));

// ---------------------------------------------------------------- state-driven geometry
const P = { ex: 4, rel: 1, n: 10, sz: 0.4, sp: 0.15, play: true, phase: 0 };
const width = () => R * BASE_W * P.ex;

function rebuildRing() {
  const w = width(), wallH = 0.15 * w, pos = surfGeom.attributes.position.array, relief = 2.2 * P.rel * (w / (R * BASE_W * 4));
  for (let j = 0; j <= NV; j++) for (let i = 0; i <= NU; i++) {
    const k = j * (NU + 1) + i, th = (i % NU) / NU * TAU, r = R - relief * alt[k] * 6 * (1 - 0.5 * Math.abs(j / NV * 2 - 1) ** 3);
    pos.set([r * Math.cos(th), r * Math.sin(th), (j / NV - 0.5) * w], k * 3);
  }
  surfGeom.attributes.position.needsUpdate = true;
  for (let s = 0; s < 2; s++) for (let i = 0; i <= NU; i++) {
    const th = (i % NU) / NU * TAU, z = (s ? 0.5 : -0.5) * w, c = Math.cos(th), sn = Math.sin(th), k = (s * (NU + 1) + i) * 6;
    wallPos.set([R * c, R * sn, z, (R - wallH) * c, (R - wallH) * sn, z], k);
  }
  wallGeom.attributes.position.needsUpdate = true;
  hull.scale.set(1, 1, w);
  $('scaleNote').textContent = `Ring width = ${(BASE_W * 100).toFixed(0)}% of its radius, drawn at ${P.ex}x = ${(BASE_W * P.ex * 100).toFixed(0)}%; walls ${(wallH / w * 100).toFixed(0)}% of the width.`;
  rebuildSquares();
}
function rebuildSquares() {
  while (sqGroup.children.length) { const g = sqGroup.children.pop(); g.children[0].geometry.dispose(); }
  const cell = TAU / P.n, half = P.sz * cell / 2, len = 2 * R_SHADOW * Math.tan(half);
  surfMat.uniforms.uN.value = P.n; surfMat.uniforms.uHalf.value = half;
  for (let i = 0; i < P.n; i++) {
    const g = new THREE.Group(), m = new THREE.Mesh(new THREE.BoxGeometry(0.4, len, width() * 1.04), sqMat);
    m.position.x = R_SHADOW; g.add(m); g.rotation.z = i * cell; sqGroup.add(g);
  }
}

// ---------------------------------------------------------------- camera presets
function setCam(name) {
  controls.minDistance = 0; controls.maxDistance = 3000;
  if (name === 'surf') {  // stand at the bottom of the ring (5 units above the datum), looking along it and up at the arch
    const pos = new THREE.Vector3(0, -R + 5, 0), dir = new THREE.Vector3(1, 0.55, 0).normalize();
    camera.position.copy(pos); controls.target.copy(pos).addScaledVector(dir, 0.5); camera.fov = 75;
    controls.minDistance = 0.5; controls.maxDistance = 0.5; controls.enablePan = false;  // drag = look around
  } else {
    controls.enablePan = true; camera.fov = 50;
    if (name === 'over') { camera.position.set(0, -190, 150); controls.target.set(0, 0, 0); }
    else { camera.position.set(40, -400, 28); controls.target.set(0, 0, 0); }
  }
  camera.updateProjectionMatrix(); controls.update();
}

// ---------------------------------------------------------------- UI
const LBL = { ex: 'vEx', rel: 'vRel', n: 'vN', sz: 'vSz', sp: 'vSp' };
const bind = (id, fmt, cb) => { const el = $(id), upd = () => { P[id] = +el.value; $(LBL[id]).textContent = fmt(P[id]); cb(); }; el.addEventListener('input', upd); upd(); };
bind('ex', (v) => v + 'x', rebuildRing);
bind('rel', (v) => v.toFixed(1) + 'x', rebuildRing);
bind('n', (v) => v, rebuildSquares);
bind('sz', (v) => Math.round(v * 100) + '%', rebuildSquares);
bind('sp', (v) => v.toFixed(2) + ' rad/s', () => {});
$('play').onclick = () => { P.play = !P.play; $('play').textContent = P.play ? 'Pause' : 'Play'; };
document.querySelectorAll('[data-cam]').forEach((b) => b.onclick = () => setCam(b.dataset.cam));
$('lg').innerHTML = BIOMES.map(([, n, c]) => `<div class="sw"><i style="background:${c}"></i>${n}</div>`).join('')
  + `<div class="sw"><i style="background:#4a5f82"></i>shadow square</div><div class="sw"><i style="background:#3a4250"></i>ring hull</div>`
  + `<div class="sw"><i style="background:#6d6f78"></i>rim wall</div><div class="sw"><i style="background:#fff3d0"></i>star</div>`
  + `<div class="muted" style="margin-top:6px">Dark bands on the surface are night: the shadows of the squares.</div>`;

function resize() { renderer.setSize(innerWidth, innerHeight, false); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize();
setCam(new URLSearchParams(location.search).get('cam') || 'over');

let last = performance.now();
renderer.setAnimationLoop((now) => {
  const dt = Math.min((now - last) / 1000, 0.1); last = now;
  if (P.play) P.phase += P.sp * dt;
  surfMat.uniforms.uPhase.value = P.phase; sqGroup.rotation.z = P.phase;
  controls.update(); renderer.render(scene, camera);
});
