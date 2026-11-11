// The globe's level-of-detail tiles (PW-1688, step 4 of docs/review/zoom/lod-plan-v2.md): as the camera comes down, the
// 4,000 km cells' tiles replace the globe's own cells (level 0): level 1 (4 km pixels, the whole cell) and level 2
// (1 km pixels, 500 km tiles), each where its pixel would cover more than ~1.5 screen pixels (?lodpx=).
//
//   - A tile shows when it has arrived; until then its parent shows there, stretched (the parent drops, by dithering,
//     exactly the fragments its drawn children keep: their fade-in over FADE_S is the parent's fade-out; no sorting).
//   - Each cell's tiles are clipped to the cell (a mask of its outline in its plane), so neighbours meet at the line.
//   - The globe's cells are hidden by the stencil wherever a tile is drawn (tiles draw first and mark it).
//   - Heights: the globe's exaggeration, easing to 1x between 2,000 km and 50 km above the ground (the cells too, so
//     cells and tiles stand at one height; easeEx).
//   - Only the active layer's colours are fetched per tile: satellite, or a layer with a zoom twin (elevation,
//     temperature, precipitation, biome); any other layer shows the satellite view on tiles.
//   - Tiles are placed relative to their own centre (float32 stays exact near the camera).
//   - At most MAX_TILES tiles / MAX_BYTES are kept; the least recently drawn go first.
// The tiles come through a tile source (tilesource.js): the server builds the wanted tiles on demand (planet/tiles.py,
// PW-1690); until a tile is built its parent shows there, stretched, and a small "sharpening…" note shows (badge()).
// URL: ?lod=0 off, ?lodpx=1.5 refine threshold, ?lodmax=2 finest level, ?lodslow=<ms> delay each tile (to see fallback).
import * as THREE from 'three';
import * as M from '../lodmath.js';
import { aeFrame } from '../zoom3d_place.js';
import { S, state } from './state.js';
import { camera, group, renderer } from './scene.js';
import { nearestCellU, reliefScale } from './geometry.js';
import { rampFns } from './layers.js';
import { OCEAN } from './colours.js';
import { NotBuilt, TileSource } from './tilesource.js';

const P = new URLSearchParams(location.search);
const R_M = 6371000;
const FADE_S = 0.4, MAX_TILES = 300, MAX_BYTES = 1.2e9, FETCHES = 4, MASK_PX = 2048, KIDS_PX = 64, GN = 129;
const EASE_HI_KM = 2000, EASE_LO_KM = 50;
export const LOD = {
  on: P.get('lod') !== '0', refinePx: +P.get('lodpx') || 1.5, maxLevel: Math.min(+P.get('lodmax') || 2, 2), slowMs: +P.get('lodslow') || 0,
  src: null, world: null, cells: [], tiles: new Map(), queue: [], inflight: 0, dirty: false, ex: 0, relK: { value: 1 }, hgKm: Infinity,
  stats: { drawn: 0, kept: 0, bytes: 0, fetched: 0, failed: 0, wanted: 0, byLevel: {}, queued: 0, building: 0 }, note: '',
};
const three = (p) => new THREE.Vector3(p[0], p[2], -p[1]);  // planet (x, y, z) -> three.js axes (geometry.toThree)
const planet = (v) => [v.x, -v.z, v.y];

// ---- the shared grid: GN x GN vertices plus a ring of skirt vertices round them (each a copy of its edge vertex, hung down)
const G = GN + 2;
const SHARED = (() => {
  const uv = new Float32Array(2 * G * G), sk = new Float32Array(G * G), idx = [];
  for (let j = 0; j < G; j++) for (let i = 0; i < G; i++) {
    const k = j * G + i, ii = Math.min(GN - 1, Math.max(0, i - 1)), jj = Math.min(GN - 1, Math.max(0, j - 1));
    uv[2 * k] = ii / (GN - 1); uv[2 * k + 1] = jj / (GN - 1);
    sk[k] = i === 0 || j === 0 || i === G - 1 || j === G - 1 ? 1 : 0;
  }
  for (let j = 0; j < G - 1; j++) for (let i = 0; i < G - 1; i++) { const a = j * G + i; idx.push(a, a + G, a + 1, a + 1, a + G, a + G + 1); }
  return { uv: new THREE.BufferAttribute(uv, 2), skirt: new THREE.BufferAttribute(sk, 1), index: new THREE.Uint32BufferAttribute(idx, 1) };
})();

const VERT = `
uniform sampler2D uElev; uniform vec3 uCentre; uniform float uEx; uniform float uSkirt;
attribute float skirt;
varying vec2 vUv;
void main() {
  vUv = uv;
  vec3 n = normalize(uCentre + position);
  float h = max(texture2D(uElev, uv).r, 0.0);
  vec3 p = position + n * (uEx * h - skirt * uSkirt);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}`;
const FRAG = `
uniform sampler2D uElev; uniform sampler2D uColor; uniform sampler2D uMask; uniform sampler2D uKids;
uniform vec3 uRect; uniform float uFade; uniform float uExM; uniform float uTexel; uniform float uResM;
varying vec2 vUv;
float ign(vec2 p) { return fract(52.9829189 * fract(dot(p, vec2(0.06711056, 0.00583715)))); }
float hAt(vec2 q) { return max(texture2D(uElev, q).r, 0.0); }
void main() {
  float d = ign(gl_FragCoord.xy);
  if (d >= uFade) discard;                       // fading in
  if (d < texture2D(uKids, vUv).r) discard;      // a drawn child has this spot (its share of the dither)
  vec2 pl = vec2(uRect.x + vUv.x * uRect.z, uRect.y - vUv.y * uRect.z);
  if (texture2D(uMask, vec2((pl.x + 2000.0) / 4000.0, (2000.0 - pl.y) / 4000.0)).r < 0.3) discard;  // outside the cell (a fraction of a mask texel generous: neighbours overlap, never gap)
  float gx = (hAt(vUv + vec2(uTexel, 0.0)) - hAt(vUv - vec2(uTexel, 0.0))) * uExM / (2.0 * uResM);
  float gy = (hAt(vUv - vec2(0.0, uTexel)) - hAt(vUv + vec2(0.0, uTexel))) * uExM / (2.0 * uResM);
  vec3 nrm = normalize(vec3(-gx, -gy, 1.0)), L = normalize(vec3(-1.0, 1.0, 1.2));
  float sh = clamp(dot(nrm, L) / L.z, 0.35, 1.45);
  gl_FragColor = vec4(texture2D(uColor, vUv).rgb * mix(1.0, sh, 0.85), 1.0);
}`;

// ---- the source, the cells ------------------------------------------------------------------------------------------
function reset() {
  for (const t of LOD.tiles.values()) dropTile(t);
  LOD.src?.close();
  LOD.tiles.clear(); LOD.queue = []; LOD.cells = []; LOD.src = null; LOD.note = '';
}
async function openWorld(id) {
  reset(); LOD.world = id;
  const src = new TileSource(id);
  src.onBuilt = () => { LOD.dirty = true; };
  try {
    const { cells } = await src.open();
    if (LOD.world !== id) return;
    LOD.cells = cells.map((c) => {
      const fr = aeFrame(c.lat, c.lon, c.up);
      return { ...c, fr, centre: three(fr.C), mask: cellMask(c.outline) };
    });
    LOD.src = src; LOD.dirty = true;
  } catch (e) { console.warn('[lod] no tiles:', e.message); LOD.note = 'no detail tiles for this world'; }
}
function cellMask(outline) {
  const cv = document.createElement('canvas'); cv.width = cv.height = MASK_PX;
  const g = cv.getContext('2d'), s = MASK_PX / M.SQUARE_KM;
  g.fillStyle = '#000'; g.fillRect(0, 0, MASK_PX, MASK_PX); g.fillStyle = '#fff'; g.beginPath();
  outline.forEach(([x, y], i) => (i ? g.lineTo : g.moveTo).call(g, (x + M.HALF) * s, (M.HALF - y) * s));
  g.closePath(); g.fill();
  // (one byte a texel: 4 MB on the GPU a cell, not the canvas's 16)
  const rgba = g.getImageData(0, 0, MASK_PX, MASK_PX).data, r = new Uint8Array(MASK_PX * MASK_PX);
  for (let i = 0; i < r.length; i++) r[i] = rgba[4 * i];
  const t = new THREE.DataTexture(r, MASK_PX, MASK_PX, THREE.RedFormat, THREE.UnsignedByteType);
  Object.assign(t, { flipY: false, generateMipmaps: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, needsUpdate: true });
  return t;
}

// ---- tiles ----------------------------------------------------------------------------------------------------------
function tileRec(k, cell) {
  let t = LOD.tiles.get(k.id);
  if (t) return t;
  const [cx, cy] = M.centreXY(k), half = M.tileKm(k.level) / 2;
  t = { k, cell, centre: three(cell.fr.toSphere(cx, cy)), radius: Math.SQRT2 * half / M.R_KM, elev: null, colId: null, mesh: null,
        fade: 0, target: 0, lastUsed: 0, loading: false, failed: false, bytes: 0, kids: null, kidTex: null, want: 0 };
  LOD.tiles.set(k.id, t);
  return t;
}
function dropTile(t) {
  if (t.mesh) { group.remove(t.mesh); t.mesh.geometry.dispose(); const u = t.mesh.material.uniforms; u.uElev.value.dispose(); u.uColor.value?.dispose(); t.mesh.material.dispose(); }
  t.kidTex?.dispose();
  t.mesh = null; t.elev = null; t.vh = null; t.colId = null; t.kidTex = null; t.bytes = 0;
}
function buildMesh(t) {
  const { k, cell } = t, [x0, , , y1] = M.rect(k), T = M.tileKm(k.level), pos = new Float32Array(3 * G * G), c = t.centre;
  for (let j = 0; j < G; j++) for (let i = 0; i < G; i++) {
    const q = j * G + i, u = SHARED.uv.array[2 * q], v = SHARED.uv.array[2 * q + 1];
    const p = cell.fr.toSphere(x0 + u * T, y1 - v * T);
    pos[3 * q] = p[0] - c.x; pos[3 * q + 1] = p[2] - c.y; pos[3 * q + 2] = -p[1] - c.z;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('uv', SHARED.uv); geo.setAttribute('skirt', SHARED.skirt); geo.setIndex(SHARED.index);
  const n = t.elev.n, et = new THREE.DataTexture(t.elev.half, n, n, THREE.RedFormat, THREE.HalfFloatType);
  Object.assign(et, { flipY: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false, needsUpdate: true });
  t.kids = new Uint8Array(KIDS_PX * KIDS_PX);
  t.kidTex = new THREE.DataTexture(t.kids, KIDS_PX, KIDS_PX, THREE.RedFormat, THREE.UnsignedByteType);
  Object.assign(t.kidTex, { flipY: false, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, needsUpdate: true });
  const mat = new THREE.ShaderMaterial({
    vertexShader: VERT, fragmentShader: FRAG, side: THREE.DoubleSide,
    uniforms: { uElev: { value: et }, uColor: { value: null }, uMask: { value: cell.mask }, uKids: { value: t.kidTex }, uCentre: { value: c.clone() },
                uEx: { value: 0 }, uExM: { value: 1 }, uSkirt: { value: 3 * M.resKm(k.level) / M.R_KM }, uRect: { value: new THREE.Vector3(x0, y1, T) },
                uFade: { value: 0 }, uTexel: { value: 1 / n }, uResM: { value: M.resKm(k.level) * 1000 } },
    stencilWrite: true, stencilRef: 1, stencilFunc: THREE.AlwaysStencilFunc, stencilZPass: THREE.ReplaceStencilOp,
  });
  t.mesh = new THREE.Mesh(geo, mat);
  Object.assign(t.mesh, { frustumCulled: false, renderOrder: -1, visible: false });
  t.mesh.position.copy(c);
  t.mesh.userData.lodTile = k.id;
  group.add(t.mesh);
  t.bytes = 2 * (n * n * 2) + pos.byteLength + KIDS_PX * KIDS_PX;
}

// the active layer's colours for tiles: {id, name, fn(v, c)} or satellite
function colourSpec() {
  const l = state.layer;
  if (l === 'biome' && S.V?.biomeColors) return { id: 'biome', name: 'biome', fn: (v, c) => c.set(S.V.biomeColors[v] ?? '#000') };
  if (['elevation', 'temperature', 'precipitation'].includes(l) && rampFns[l]) return { id: l, name: l, fn: rampFns[l], sea: l !== 'elevation' };
  return { id: 'satellite' };
}
function valuesTexture(vals, n, spec, half) {
  const rgba = new Uint8Array(4 * n * n), c = new THREE.Color();
  for (let i = 0; i < n * n; i++) {
    if (spec.sea && M.halfToFloat(half[i]) <= 0) c.copy(OCEAN); else spec.fn(vals[i], c);
    const h = c.getHex(); rgba[4 * i] = h >> 16; rgba[4 * i + 1] = (h >> 8) & 255; rgba[4 * i + 2] = h & 255; rgba[4 * i + 3] = 255;
  }
  const t = new THREE.DataTexture(rgba, n, n, THREE.RGBAFormat, THREE.UnsignedByteType);
  Object.assign(t, { flipY: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, needsUpdate: true });
  return t;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function load(t, spec) {
  t.loading = true; LOD.inflight++;
  try {
    if (LOD.slowMs) await sleep(LOD.slowMs);
    if (!t.elev) {
      t.elev = await LOD.src.elevation(t.k);
      buildMesh(t);
    }
    let tex;
    if (spec.id === 'satellite') {
      const bmp = await LOD.src.satellite(t.k);
      tex = new THREE.Texture(bmp);
      Object.assign(tex, { flipY: false, minFilter: THREE.LinearFilter, generateMipmaps: false, needsUpdate: true });
    } else {
      const vals = await LOD.src.layer(t.k, spec.name);
      tex = vals ? valuesTexture(vals, t.elev.n, spec, t.elev.half) : null;
      if (!tex) { LOD.inflight--; try { return await load(t, { id: 'satellite' }); } finally { LOD.inflight++; } }
    }
    if (!t.mesh) { tex.dispose(); return; }  // (dropped meanwhile)
    const u = t.mesh.material.uniforms;
    u.uColor.value?.dispose(); u.uColor.value = tex; t.colId = spec.id;
    t.bytes = 2 * (t.elev.n ** 2 * 2) + 2 * (t.elev.n ** 2 * 4) + 3 * 4 * G * G;
    LOD.stats.fetched++; LOD.dirty = true;
  } catch (e) {
    if (!(e instanceof NotBuilt)) { t.failed = true; LOD.stats.failed++; console.warn('[lod]', t.k.id, e.message); }
  } finally { t.loading = false; LOD.inflight--; pump(); }
}
function pump() {
  const spec = colourSpec();
  while (LOD.inflight < FETCHES && LOD.queue.length) {
    const t = LOD.queue.shift();
    if (!t.loading && !t.failed && (t.colId !== spec.id)) load(t, spec);
  }
}

// ---- heights --------------------------------------------------------------------------------------------------------
// the tiles' (and the cells') exaggeration: the globe's above EASE_HI_KM, 1x below EASE_LO_KM, log-linear between
export function easeEx(hKm) {
  const g = reliefScale(), one = 1 / R_M;
  if (!(g > one)) return g;
  const t = Math.min(1, Math.max(0, Math.log(hKm / EASE_LO_KM) / Math.log(EASE_HI_KM / EASE_LO_KM)));
  return Math.exp(Math.log(one) + t * (Math.log(g) - Math.log(one)));
}
// The drawn ground's radius along a direction (group space, any length): where the ray from the centre meets the
// surface as drawn this frame (PW-1696). The finest tile drawn there (its own mesh: the grid's heights as the vertex
// shader samples them, the grid's two triangles between), else the globe's cells (the fan of triangles from the cell's
// centre to its corners, eased as patchCells eases them). The camera's least height and its pivot (dive.js) and the
// overlays laid on the ground (drape.js) all stand on it.
const _v = new THREE.Vector3();
export function groundRadius(dir) {
  const u = _v.copy(dir).normalize();
  let best = null, bd = -2;
  for (const c of LOD.cells) { const d = u.dot(c.centre); if (d > bd) { bd = d; best = c; } }
  if (best && LOD.src) {
    const [x, y] = best.fr.toPlane(planet(u));
    for (let lv = LOD.maxLevel; lv >= 1; lv--) {
      if (Math.abs(x) >= M.HALF || Math.abs(y) >= M.HALF) break;
      const t = LOD.tiles.get(M.tileAt(best.id, lv, x, y).id);
      if (!t?.elev || !(t.fade > 0) || !t.mesh?.visible) continue;
      const [tu, tv] = M.tileUV(t.k, x, y);
      return 1 + LOD.ex * meshHeight(t, tu, tv);
    }
  }
  return cellsRadius(u);
}
// the tile mesh's height (m) at (u, v) (lodmath.js: the grid's heights as the vertex shader samples them, its
// triangles between)
function meshHeight(t, u, v) {
  t.vh ??= M.gridHeights(t.elev.half, t.elev.n, GN);
  return M.meshHeightAt(t.vh, GN, u, v);
}
// the globe's cell mesh along u: the fan triangle (centre, corner k, corner k+1) that the ray meets, of the nearest cell
// or one of its neighbours, its vertices eased as the cells' shader eases them (patchCells)
const triple = (a, b, c) => a[0] * (b[1] * c[2] - b[2] * c[1]) + a[1] * (b[2] * c[0] - b[0] * c[2]) + a[2] * (b[0] * c[1] - b[1] * c[0]);
function cellsRadius(u) {
  if (!S.V?.layers?.elevation || state.mode !== 'globe') return 1;
  const i = nearestCellU([u.x, u.y, u.z]), R = S.V.R, k = LOD.relK.value, ease = (r) => 1 + (r - 1) * k;
  if (!R || !S.V.U || !S.V.UC) return ease(1 + reliefScale() * Math.max(S.V.layers.elevation[i], 0));
  for (const c of [i, ...(S.V.grid.nbr?.[i] || [])]) { const r = fanRadius(c, u, R, ease); if (r !== null) return r; }
  return ease(R[i]);
}
function fanRadius(i, u, R, ease) {
  const U = S.V.U, UC = S.V.UC, n = S.V.n, cs = S.V.grid.cells[i], m = cs.length, w = [u.x, u.y, u.z];
  const P0 = [U[3 * i], U[3 * i + 1], U[3 * i + 2]], r0 = ease(R[i]);
  for (let q = 0; q < m; q++) {
    const a = cs[q], b = cs[(q + 1) % m];
    const A = [UC[3 * a], UC[3 * a + 1], UC[3 * a + 2]], B = [UC[3 * b], UC[3 * b + 1], UC[3 * b + 2]];
    const o = triple(P0, A, B);  // (u inside the cone of the three: on the inner side of each of its planes)
    if (triple(P0, A, w) * o < -1e-15 || triple(A, B, w) * o < -1e-15 || triple(B, P0, w) * o < -1e-15) continue;
    const ra = ease(R[n + a]), rb = ease(R[n + b]);
    const p = [P0[0] * r0, P0[1] * r0, P0[2] * r0];
    const e1 = [A[0] * ra - p[0], A[1] * ra - p[1], A[2] * ra - p[2]], e2 = [B[0] * rb - p[0], B[1] * rb - p[1], B[2] * rb - p[2]];
    const nx = e1[1] * e2[2] - e1[2] * e2[1], ny = e1[2] * e2[0] - e1[0] * e2[2], nz = e1[0] * e2[1] - e1[1] * e2[0];
    const den = nx * w[0] + ny * w[1] + nz * w[2];
    if (Math.abs(den) > 1e-15) return (nx * p[0] + ny * p[1] + nz * p[2]) / den;
  }
  return null;
}

// ---- the globe's cells: eased with the tiles, hidden under them -------------------------------------------------------
function patchCells(active) {
  for (const m of S.mesh?.userData.mats || []) {
    if (!m.userData.lodPatch) {
      m.userData.lodPatch = true;
      m.onBeforeCompile = (sh) => {
        sh.uniforms.uRelK = LOD.relK;
        sh.vertexShader = 'uniform float uRelK;\n' + sh.vertexShader.replace('#include <begin_vertex>',
          '#include <begin_vertex>\n  { float rr = length(transformed); if (uRelK != 1.0 && rr > 0.5) transformed *= (1.0 + (rr - 1.0) * uRelK) / rr; }');
      };
      m.customProgramCacheKey = () => 'lodRelK';
      m.needsUpdate = true;
    }
    if (m.stencilWrite !== active) Object.assign(m, { stencilWrite: active, stencilRef: 1, stencilFunc: THREE.NotEqualStencilFunc, stencilFail: THREE.KeepStencilOp, stencilZFail: THREE.KeepStencilOp, stencilZPass: THREE.KeepStencilOp });
  }
}

// ---- each frame -----------------------------------------------------------------------------------------------------
const frustum = new THREE.Frustum(), pm = new THREE.Matrix4(), camL = new THREE.Vector3(), wc = new THREE.Vector3(), sph = new THREE.Sphere();
let lastNow = 0;
export function updateLod(now) {
  const dt = lastNow ? Math.min(0.1, (now - lastNow) / 1000) : 0; lastNow = now;
  const globe = state.mode === 'globe' && state.tab !== 'zoom' && LOD.on;
  if (globe && S.V?.kind === 'world' && S.V.id && LOD.world !== S.V.id) openWorld(S.V.id);
  camL.copy(camera.position); group.worldToLocal(camL);
  const r = camL.length();
  LOD.hgKm = Math.max(1e-3, (r - groundRadius(camL)) * M.R_KM);
  const ex = globe ? easeEx(LOD.hgKm) : reliefScale(), g = reliefScale();
  if (ex !== LOD.ex) LOD.dirty = true;
  LOD.ex = ex; LOD.relK.value = globe && g > 0 ? ex / g : 1;
  const active = globe && !!LOD.src;
  patchCells(active);
  if (!active) { for (const t of LOD.tiles.values()) if (t.mesh) t.mesh.visible = false; badge(false); return; }

  // which tiles the view wants: walk each visible cell's pyramid down while the next level's pixel covers > refinePx
  camera.updateMatrixWorld(); group.updateMatrixWorld();
  frustum.setFromProjectionMatrix(pm.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
  const focal = renderer.domElement.clientHeight / 2 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const horizon = Math.acos(Math.min(1, 1 / r)) + Math.acos(1 / (1 + ex * 9000)) + 0.02, cdir = camL.clone().normalize();
  const want = new Set(), order = [], spec = colourSpec();
  const visit = (k, cell) => {
    if (!LOD.src.has(k)) return;
    const t = tileRec(k, cell);
    const ang = Math.acos(Math.min(1, Math.max(-1, cdir.dot(t.centre)))) - t.radius;
    if (ang > horizon) return;
    wc.copy(t.centre); group.localToWorld(wc);
    if (!frustum.intersectsSphere(sph.set(wc, t.radius * 1.1 + 0.01))) return;
    const dist = Math.max(LOD.hgKm, (camL.distanceTo(t.centre) - t.radius) * M.R_KM);
    if (M.pixelsOnScreen(M.resKm(k.level), dist, focal) < LOD.refinePx) return;
    want.add(t); t.want = k.level * 1e6 + Math.hypot(...screenOffset(wc)) * 1e3 + dist / 1e4;
    order.push(t);
    if (k.level < LOD.maxLevel) for (const ck of M.children(k)) visit(ck, cell);
  };
  for (const c of LOD.cells) visit(M.key(c.id, 1, 0, 0), c);
  LOD.stats.wanted = want.size;

  // what is wanted and missing (coarse first, then nearest the screen's centre) goes to the server, which builds the
  // unbuilt ones (a new list replaces its queue); the built ones are fetched; the rest of the fetch queue is dropped
  order.sort((a, b) => a.want - b.want);
  const missing = order.filter((t) => !t.loading && !t.failed && t.colId !== spec.id);
  LOD.src.want(missing.map((t) => t.k));
  LOD.queue = missing.filter((t) => LOD.src.ready(t.k));
  pump();
  const b = LOD.src.building;
  LOD.stats.queued = b.queued; LOD.stats.building = b.building;
  badge(b.queued + b.building > 0 && missing.length > LOD.queue.length, b);

  // fade in what is wanted and ready, out the rest; a drawn tile's children take their share of its fragments
  let drawn = 0, bytes = 0; const byLevel = {};
  for (const t of LOD.tiles.values()) {
    t.target = want.has(t) && t.colId ? 1 : 0;
    const f = Math.max(0, Math.min(1, t.fade + (t.target ? 1 : -1) * dt / FADE_S));
    if (f !== t.fade) { t.fade = f; LOD.dirty = true; }
    if (t.mesh) {
      const u = t.mesh.material.uniforms;
      t.mesh.visible = t.fade > 0 && !!u.uColor.value;
      u.uFade.value = t.fade; u.uEx.value = ex; u.uExM.value = ex * R_M;
      if (t.mesh.visible) { drawn++; t.lastUsed = now; byLevel[t.k.level] = (byLevel[t.k.level] || 0) + 1; }
      bytes += t.bytes;
    }
  }
  for (const t of LOD.tiles.values()) {
    if (!t.kids) continue;
    const kids = new Uint8Array(KIDS_PX * KIDS_PX);
    for (const ck of M.children(t.k)) {
      const c = LOD.tiles.get(ck.id);
      if (!c?.mesh?.visible) continue;
      const b = M.branching(t.k.level), s = KIDS_PX / b, v = Math.round(255 * c.fade);
      for (let y = ck.ty % b * s; y < (ck.ty % b + 1) * s; y++) kids.fill(v, y * KIDS_PX + (ck.tx % b) * s, y * KIDS_PX + (ck.tx % b + 1) * s);
    }
    let same = true;
    for (let i = 0; i < kids.length && same; i++) same = kids[i] === t.kids[i];
    if (!same) { t.kids.set(kids); t.kidTex.needsUpdate = true; LOD.dirty = true; }
  }
  Object.assign(LOD.stats, { drawn, kept: [...LOD.tiles.values()].filter((t) => t.mesh).length, bytes, byLevel });

  // keep at most MAX_TILES / MAX_BYTES: drop the least recently drawn
  if (LOD.stats.kept > MAX_TILES || bytes > MAX_BYTES) {
    const old = [...LOD.tiles.values()].filter((t) => t.mesh && !t.mesh.visible && !t.loading).sort((a, b) => a.lastUsed - b.lastUsed);
    let n = LOD.stats.kept, b = bytes;
    for (const t of old) { if (n <= MAX_TILES * 0.9 && b <= MAX_BYTES * 0.9) break; n--; b -= t.bytes; dropTile(t); }
  }
}
// the "sharpening…" note: tiles in view are being built (unobtrusive: bottom centre, no clicks)
let badgeEl = null;
function badge(on, b) {
  if (!badgeEl) {
    if (!on) return;
    badgeEl = document.createElement('div');
    badgeEl.id = 'lod-badge';
    Object.assign(badgeEl.style, { position: 'fixed', left: '50%', bottom: '14px', transform: 'translateX(-50%)', padding: '3px 10px',
      borderRadius: '10px', background: 'rgba(0, 0, 0, 0.45)', color: '#e8e8e8', font: '12px system-ui, sans-serif',
      pointerEvents: 'none', zIndex: 20, transition: 'opacity 0.4s', opacity: '0' });
    badgeEl.textContent = 'sharpening…';
    document.body.appendChild(badgeEl);
  }
  badgeEl.style.opacity = on ? '1' : '0';
  if (on && b) badgeEl.title = `building detail: ${b.building} building, ${b.queued} queued${b.note ? ` (${b.note})` : ''}`;
}
const _s = new THREE.Vector3();
function screenOffset(w) { _s.copy(w).project(camera); return [_s.x, _s.y]; }
// main.js: draw this frame although nothing three.js tracks changed (a fade, a uniform, a tile's colours)
export function lodDirty() { const d = LOD.dirty; LOD.dirty = false; return d; }
