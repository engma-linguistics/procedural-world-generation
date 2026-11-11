// The globe's level-of-detail tiles (PW-1688 step 4, PW-1673 step 5 of docs/review/zoom/lod-plan-v2.md): as the camera
// comes down, the 4,000 km cells' tiles replace the globe's own cells (level 0): level 1 (4 km pixels, the whole cell),
// level 2 (1 km pixels, 500 km tiles), level 3 (250 m, 125 km) and level 4 (25 m, 12.5 km), each where its pixel would
// cover more than ~1.5 screen pixels (?lodpx=).
//
//   - A tile shows when it has arrived; until then its parent shows there, stretched (the parent drops, by dithering,
//     exactly the fragments its drawn children keep: their fade-in over FADE_S is the parent's fade-out; no sorting).
//   - Each cell's tiles are clipped to the cell exactly (its edges are the cube's great circles, lodmath.js::cellAngles),
//     a pixel of the tile's level generous, so neighbours meet at the line (a 2 km mask did, PW-1673 step 6: at 25 m
//     the cells overlapped by up to ~1 km, beyond the line's fade, and their grounds cut through each other).
//   - The globe's cells are hidden by the stencil wherever a tile is drawn (tiles draw first and mark it).
//   - Heights: the globe's exaggeration, easing to 1x between 2,000 km and 50 km above the ground (the cells too, so
//     cells and tiles stand at one height; easeEx).
//   - Only the active layer's colours are fetched per tile: satellite, or any globe layer whose colouring reads only its
//     own values and has a zoom twin (layers.js::tileLayer: elevation, temperature, rain, biome, vegetation, soils,
//     climate, ...), coloured by the globe's own colouring and legend; any other layer shows the satellite view on tiles
//     (a note under the legend says so). The hover readout reads the tile's value under the cursor (tileHover).
//   - Rivers (PW-1711): a level-2 or finer tile draws its own rivers (its discharge at the globe's river threshold, as
//     wide as the river at its pixel size, in the ribbons' colours) and marks stencil bit 2, which hides the globe's
//     river ribbons there (overlays.js); over level 1 and the cells the ribbons show as before.
//   - Tiles are placed relative to their own centre (float32 stays exact near the camera).
//   - The memory pool: at most MAX_TILES tiles / MAX_BYTES (GPU and JS copies) are kept, the least recently drawn
//     dropped first; records of tiles not seen for FORGET_MS are forgotten.
// The tiles come through a tile source (tilesource.js): the server builds the wanted tiles on demand (planet/tiles.py,
// PW-1690); until a tile is built its parent shows there, stretched, and a small "sharpening…" note shows (badge()).
// URL: ?lod=0 off, ?lodpx=1.5 refine threshold, ?lodmax=4 finest level, ?lodslow=<ms> delay each tile (to see fallback).
import * as THREE from 'three';
import * as M from '../lodmath.js';
import { aeFrame } from '../zoom3d_place.js';
import { S, state } from './state.js';
import { camera, group, renderer } from './scene.js';
import { nearestCellU, reliefScale } from './geometry.js';
import { tileLayer, tileValueText } from './layers.js';
import { NotBuilt, TileSource } from './tilesource.js';

const P = new URLSearchParams(location.search);
const R_M = 6371000;
const FADE_S = 0.4, MAX_TILES = 120, MAX_BYTES = 0.4e9, FORGET_MS = 60000, FETCHES = 4, GN = 129;
const KIDS_PX = 80;  // (a tile's children grid: 8, 4 and 10 a side divide it)
const RIVER_W = 4.5, RIVER_MAX_PX = 8;  // river width m = RIVER_W sqrt(Q m3/s) (judgement), at most RIVER_MAX_PX pixels across
const EASE_HI_KM = 2000, EASE_LO_KM = 50;
export const LOD = {
  on: P.get('lod') !== '0', refinePx: +P.get('lodpx') || 1.5, maxLevel: Math.min(+P.get('lodmax') || M.FINEST, M.FINEST), slowMs: +P.get('lodslow') || 0,
  src: null, world: null, cells: [], tiles: new Map(), queue: [], inflight: 0, dirty: false, ex: 0, relK: { value: 1 }, hgKm: Infinity,
  stats: { drawn: 0, kept: 0, bytes: 0, fetched: 0, failed: 0, wanted: 0, byLevel: {}, queued: 0, building: 0, records: 0, dropped: 0, satOnly: 0 }, note: '',
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
varying vec2 vUv; varying vec3 vDir;
void main() {
  vUv = uv;
  vec3 n = normalize(uCentre + position);
  vDir = vec3(n.x, -n.z, n.y);  // (planet coordinates: the scene's (x, y, z) is the planet's (x, z, -y))
  float h = max(texture2D(uElev, uv).r, 0.0);
  vec3 p = position + n * (uEx * h - skirt * uSkirt);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}`;
const FRAG = `
uniform sampler2D uElev; uniform sampler2D uColor; uniform sampler2D uKids; uniform sampler2D uRiver;
uniform float uRiverOn; uniform vec3 uRiverCol; uniform vec3 uRiverBig;
uniform vec3 uRect; uniform float uFade; uniform float uExM; uniform float uTexel; uniform float uResM;
uniform vec3 uFA; uniform vec3 uFU; uniform vec3 uFV; uniform vec4 uAB; uniform float uPad;
varying vec2 vUv; varying vec3 vDir;
float ign(vec2 p) { return fract(52.9829189 * fract(dot(p, vec2(0.06711056, 0.00583715)))); }
float hAt(vec2 q) { return max(texture2D(uElev, q).r, 0.0); }
void main() {
  float d = ign(gl_FragCoord.xy);
  if (d >= uFade) discard;                       // fading in
  if (d < texture2D(uKids, vUv).r) discard;      // a drawn child has this spot (its share of the dither)
  // outside the cell: its edges are great circles of the cube (lodmath.js::inCellAngles), exact for both cells there; each
  // cell draws uPad (a pixel of the tile's level) past them, where both cells' tiles hold the same ground (the fade to
  // the line, lod_build.line_surface: weight 1 within 1.5 px), so neighbours overlap a little and never leave a gap
  float fd = dot(vDir, uFA);
  vec2 ab = vec2(atan(dot(vDir, uFU), fd), atan(dot(vDir, uFV), fd));
  if (fd <= 0.0 || ab.x < uAB.x - uPad || ab.x > uAB.y + uPad || ab.y < uAB.z - uPad || ab.y > uAB.w + uPad) discard;
  float gx = (hAt(vUv + vec2(uTexel, 0.0)) - hAt(vUv - vec2(uTexel, 0.0))) * uExM / (2.0 * uResM);
  float gy = (hAt(vUv - vec2(0.0, uTexel)) - hAt(vUv + vec2(0.0, uTexel))) * uExM / (2.0 * uResM);
  vec3 nrm = normalize(vec3(-gx, -gy, 1.0)), L = normalize(vec3(-1.0, 1.0, 1.2));
  float sh = clamp(dot(nrm, L) / L.z, 0.35, 1.45);
  vec3 col = texture2D(uColor, vUv).rgb * mix(1.0, sh, 0.85);
  vec2 rv = texture2D(uRiver, vUv).rg;
  col = mix(col, rv.g > 0.5 ? uRiverBig : uRiverCol, uRiverOn * smoothstep(0.25, 0.6, rv.r));
  gl_FragColor = vec4(col, 1.0);
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
      const a = M.cellAngles(c.id);
      return { ...c, fr, centre: three(fr.C), clip: { A: new THREE.Vector3(...a.A), U: new THREE.Vector3(...a.U), V: new THREE.Vector3(...a.V),
                                                     ab: new THREE.Vector4(...a.ab) } };
    });
    LOD.src = src; LOD.dirty = true;
  } catch (e) { console.warn('[lod] no tiles:', e.message); LOD.note = 'no detail tiles for this world'; }
}

// ---- tiles ----------------------------------------------------------------------------------------------------------
function tileRec(k, cell) {
  let t = LOD.tiles.get(k.id);
  if (t) return t;
  const [cx, cy] = M.centreXY(k), half = M.tileKm(k.level) / 2;
  t = { k, cell, centre: three(cell.fr.toSphere(cx, cy)), radius: Math.SQRT2 * half / M.R_KM, elev: null, colId: null, mesh: null,
        fade: 0, target: 0, lastUsed: 0, seen: 0, loading: false, failed: false, bytes: 0, kids: null, kidTex: null, want: 0,
        vals: null, valsLayer: null, river: null, riverThr: null, riverLoading: false };
  LOD.tiles.set(k.id, t);
  return t;
}
function dropTile(t) {
  if (t.mesh) { group.remove(t.mesh); t.mesh.geometry.dispose(); const u = t.mesh.material.uniforms; u.uElev.value.dispose(); u.uColor.value?.dispose(); t.mesh.material.dispose(); }
  t.kidTex?.dispose(); t.river?.dispose();
  t.mesh = null; t.elev = null; t.vh = null; t.colId = null; t.kidTex = null; t.bytes = 0; t.vals = null; t.river = null; t.riverThr = null;
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
    uniforms: { uElev: { value: et }, uColor: { value: null }, uFA: { value: cell.clip.A }, uFU: { value: cell.clip.U }, uFV: { value: cell.clip.V }, uAB: { value: cell.clip.ab },
                uPad: { value: M.resKm(k.level) / M.R_KM }, uKids: { value: t.kidTex }, uCentre: { value: c.clone() },
                uRiver: { value: NO_RIVER }, uRiverOn: { value: 0 }, uRiverCol: { value: new THREE.Color() }, uRiverBig: { value: new THREE.Color() },
                uEx: { value: 0 }, uExM: { value: 1 }, uSkirt: { value: 3 * M.resKm(k.level) / M.R_KM }, uRect: { value: new THREE.Vector3(x0, y1, T) },
                uFade: { value: 0 }, uTexel: { value: 1 / n }, uResM: { value: M.resKm(k.level) * 1000 } },
    // (stencil bit 1: hides the globe's cells; bit 2, level 2 and finer: hides the globe's river ribbons, PW-1711)
    stencilWrite: true, stencilRef: k.level >= 2 ? 3 : 1, stencilFunc: THREE.AlwaysStencilFunc, stencilZPass: THREE.ReplaceStencilOp,
  });
  t.mesh = new THREE.Mesh(geo, mat);
  Object.assign(t.mesh, { frustumCulled: false, renderOrder: -1, visible: false });
  t.mesh.position.copy(c);
  t.mesh.userData.lodTile = k.id;
  group.add(t.mesh);
  sizeTile(t);
}
// a tile's bytes, JS and GPU copies: elevation (float16, twice: the JS copy stays for the ground and the hover), colours
// and the river mask (on the GPU only: their JS copies are let go once uploaded, gpuOnly), the values kept for the hover,
// positions, the children grid
function sizeTile(t) {
  const n = t.elev?.n || 0;
  t.bytes = 2 * (n * n * 2) + (t.colId ? n * n * 4 : 0) + (t.vals ? t.vals.byteLength : 0) + (t.river ? 2 * n * n : 0)
    + 3 * 4 * G * G + KIDS_PX * KIDS_PX;
}
// let a texture's JS copy go once it is on the GPU (an ImageBitmap closed, a data array dropped); never uploaded again
function gpuOnly(tex) {
  tex.onUpdate = () => {
    tex.onUpdate = null;
    const im = tex.image;
    if (im?.close) im.close();
    else if (im?.data) tex.image = { width: im.width, height: im.height, data: null };
  };
  return tex;
}
const NO_RIVER = (() => { const t = new THREE.DataTexture(new Uint8Array(2), 1, 1, THREE.RGFormat, THREE.UnsignedByteType); t.needsUpdate = true; return t; })();

// the active layer's colours for tiles: layers.js::tileLayer (cached per layer and season), or the satellite view
let specCache = null;
function colourSpec() {
  const key = `${state.layer}|${state.season}|${state.obs}`;
  if (specCache?.key !== key) {
    let tl = null;
    try { tl = S.V ? tileLayer(state.layer) : null; } catch { tl = null; }
    specCache = { key, spec: tl || { id: 'satellite' } };
  }
  return specCache.spec;
}
// the layer's colours over a tile's pixels: the globe's own colouring (tileLayer.color) on the tile's arrays; land and
// sea from the tile's water mask (a land depression below the sea stays land); lakes in the globe's lake colours for
// the layers that draw lakes. null when the colouring can't take the tile's values (the satellite view instead).
const LAKE_COL = new THREE.Color('#38c8f0');  // (colours.js LAKE_KINDS' fresh lake; not imported: a module cycle)
function valuesTexture(spec, L, t) {
  const { n, half, water } = t.elev, N = n * n, el = new Float32Array(N), rgba = new Uint8Array(4 * N), c = new THREE.Color();
  for (let i = 0; i < N; i++) { const e = M.halfToFloat(half[i]); el[i] = water[i] === 1 ? Math.min(e, -1) : Math.max(e, 0.5); }
  const main = L[spec.names[spec.main]], lakes = spec.layer !== 'satellite' && ['elevation', 'biome', 'vegetation', 'soils'].includes(spec.layer);
  let fn;
  try { fn = spec.color({ L, elev: el, sv: main }); fn(0, c); } catch { return null; }
  for (let i = 0; i < N; i++) {
    if (lakes && water[i] === 2) c.copy(LAKE_COL);
    else fn(i, c);
    const h = c.getHex(); rgba[4 * i] = h >> 16; rgba[4 * i + 1] = (h >> 8) & 255; rgba[4 * i + 2] = h & 255; rgba[4 * i + 3] = 255;  // (sRGB, as the satellite's)
  }
  const tex = gpuOnly(new THREE.DataTexture(rgba, n, n, THREE.RGBAFormat, THREE.UnsignedByteType));
  Object.assign(tex, { flipY: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, needsUpdate: true });
  return tex;
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
    let tex = null, vals = null;
    if (spec.id !== 'satellite') {  // (the layer's value layer, then the extras its colouring reads; the tile may lack any)
      const main = await LOD.src.layer(t.k, spec.main);
      if (main) {
        const L = { [spec.names[spec.main]]: main, [spec.layer]: main };
        for (const zn of Object.keys(spec.names)) if (zn !== spec.main) { const a = await LOD.src.layer(t.k, zn).catch(() => null); if (a) L[spec.names[zn]] = a; }
        tex = valuesTexture(spec, L, t);
        if (tex) vals = main;
      }
    }
    t.sat = !tex;
    if (!tex) {
      const bmp = await LOD.src.satellite(t.k);
      tex = gpuOnly(new THREE.Texture(bmp));
      Object.assign(tex, { flipY: false, minFilter: THREE.LinearFilter, generateMipmaps: false, needsUpdate: true });
    }
    if (!t.mesh) { tex.dispose(); return; }  // (dropped meanwhile)
    const u = t.mesh.material.uniforms;
    u.uColor.value?.dispose(); u.uColor.value = tex; t.colId = spec.id; t.vals = vals; t.valsLayer = vals ? spec.layer : null;
    sizeTile(t);
    LOD.stats.fetched++; LOD.dirty = true;
  } catch (e) {
    if (!(e instanceof NotBuilt)) { t.failed = true; LOD.stats.failed++; console.warn('[lod]', t.k.id, e.message); }
  } finally { t.loading = false; LOD.inflight--; pump(); }
}
function pump() {
  const spec = colourSpec(), rv = S.riverTiles;
  while (LOD.inflight < FETCHES && LOD.queue.length) {
    const t = LOD.queue.shift();
    if (!t.loading && !t.failed && (t.colId !== spec.id)) load(t, spec);
    else if (rv && t.mesh && t.k.level >= 2 && t.riverThr !== rv.thr && !t.riverLoading) loadRiver(t, rv);
  }
}
// a level-2+ tile's rivers (PW-1711): its discharge at the globe's threshold, each river pixel widened to the river's
// width (RIVER_W sqrt(Q), at least the pixel, at most RIVER_MAX_PX across); R: coverage, G: one of the biggest rivers
async function loadRiver(t, rv) {
  t.riverLoading = true; LOD.inflight++;
  try {
    const q = await LOD.src.layer(t.k, 'discharge');
    if (!t.mesh) return;
    const n = t.elev.n, rg = new Uint8Array(2 * n * n), resM = M.resKm(t.k.level) * 1000;
    if (q) for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const v = q[j * n + i];
      if (!(v >= rv.thr) || t.elev.water[j * n + i] === 1) continue;
      const r = Math.min(RIVER_MAX_PX / 2, Math.max(0.5, RIVER_W * Math.sqrt(v) / 2 / resM)), ri = Math.ceil(r - 0.5), big = v >= rv.big ? 255 : 0;
      for (let dj = -ri; dj <= ri; dj++) for (let di = -ri; di <= ri; di++) {
        const x = i + di, y = j + dj;
        if (x < 0 || y < 0 || x >= n || y >= n || di * di + dj * dj > (r + 0.25) ** 2) continue;
        const o = 2 * (y * n + x); rg[o] = 255; if (big) rg[o + 1] = 255;
      }
    }
    const tex = gpuOnly(new THREE.DataTexture(rg, n, n, THREE.RGFormat, THREE.UnsignedByteType));
    Object.assign(tex, { flipY: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false, needsUpdate: true });
    t.river?.dispose(); t.river = tex; t.riverThr = rv.thr;
    t.mesh.material.uniforms.uRiver.value = tex;
    sizeTile(t); LOD.dirty = true;
  } catch (e) {
    if (!(e instanceof NotBuilt)) console.warn('[lod] rivers', t.k.id, e.message);
    t.riverThr = rv.thr;  // (not asked again at this threshold)
  } finally { t.riverLoading = false; LOD.inflight--; pump(); }
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
  const u = _v.copy(dir).normalize(), h = tileUnder(u);
  return h ? 1 + LOD.ex * meshHeight(h.t, h.tu, h.tv) : cellsRadius(u);
}
// the finest drawn tile along a unit direction (group space) and where in it: {t, tu, tv}, or null
export function tileUnder(u) {
  let best = null, bd = -2;
  for (const c of LOD.cells) { const d = u.dot(c.centre); if (d > bd) { bd = d; best = c; } }
  if (!best || !LOD.src) return null;
  const [x, y] = best.fr.toPlane(planet(u));
  for (let lv = LOD.maxLevel; lv >= 1; lv--) {
    if (Math.abs(x) >= M.HALF || Math.abs(y) >= M.HALF) break;
    const t = LOD.tiles.get(M.tileAt(best.id, lv, x, y).id);
    if (!t?.elev || !(t.fade > 0) || !t.mesh?.visible) continue;
    const [tu, tv] = M.tileUV(t.k, x, y);
    return { t, tu, tv };
  }
  return null;
}
// The hover on tiles: where a ray (world space) meets the drawn ground (a few rounds of "meet the sphere through the
// ground found last time"), and the tile there. {dir: unit vector in group space, t, tu, tv} or null (no tile drawn there).
const _o = new THREE.Vector3(), _d = new THREE.Vector3(), _p = new THREE.Vector3(), _inv = new THREE.Matrix4();
export function tileHit(ray) {
  if (!LOD.src || !LOD.stats.drawn) return null;
  _inv.copy(group.matrixWorld).invert();
  _o.copy(ray.origin).applyMatrix4(_inv); _d.copy(ray.direction).transformDirection(_inv);
  let r = groundRadius(_o), tt = null;
  for (let k = 0; k < 8; k++) {
    const b = _o.dot(_d), disc = b * b - (_o.lengthSq() - r * r);
    if (disc < 0) return null;
    tt = -b - Math.sqrt(disc);
    if (tt < 0) return null;
    _p.copy(_d).multiplyScalar(tt).add(_o);
    const r2 = groundRadius(_p);
    if (Math.abs(r2 - r) < 1e-10) break;
    r = r2;
  }
  const u = _p.clone().normalize(), h = tileUnder(u);
  return h && { dir: u, ...h };
}
// the hover readout of a tile hit: the tile, its pixel size, the ground height, the active layer's value there
export function tileHover(hit) {
  const { t, tu, tv } = hit, n = t.elev.n, i = Math.min(n - 1, Math.max(0, Math.floor(tu * n))), j = Math.min(n - 1, Math.max(0, Math.floor(tv * n)));
  const e = M.halfToFloat(t.elev.half[j * n + i]), w = t.elev.water[j * n + i], res = M.resKm(t.k.level);
  const [px, py, pz] = planet(hit.dir), lat = Math.asin(Math.max(-1, Math.min(1, pz))) * 180 / Math.PI, lon = Math.atan2(py, px) * 180 / Math.PI;
  const parts = [`${w === 1 ? 'sea' : w === 2 ? 'lake' : 'land'}, ${Math.round(e).toLocaleString()} m`];
  if (t.vals && t.valsLayer === state.layer && t.valsLayer !== 'elevation') parts.push(`${state.layer} ${tileValueText(state.layer, t.vals[j * n + i])}`);
  else if (t.sat && state.layer !== 'satellite') parts.push(`(no fine ${state.layer}: satellite view)`);
  return { id: t.k.id, lat, lon, text: parts.join(' · '), res: res >= 1 ? `${res} km` : `${res * 1000} m` };
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
    if (m.stencilWrite !== active) Object.assign(m, { stencilWrite: active, stencilRef: 1, stencilFuncMask: 1, stencilWriteMask: 0, stencilFunc: THREE.NotEqualStencilFunc, stencilFail: THREE.KeepStencilOp, stencilZFail: THREE.KeepStencilOp, stencilZPass: THREE.KeepStencilOp });
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
    t.seen = now;
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
  const rv = S.riverTiles;
  LOD.queue = missing.filter((t) => LOD.src.ready(t.k));
  if (rv) LOD.queue.push(...order.filter((t) => t.mesh && t.colId && t.k.level >= 2 && t.riverThr !== rv.thr && !t.riverLoading));
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
      u.uRiverOn.value = rv && t.river && t.riverThr === rv.thr ? 1 : 0;
      if (rv) { u.uRiverCol.value.setHex(rv.color, THREE.LinearSRGBColorSpace); u.uRiverBig.value.setHex(rv.colorBig, THREE.LinearSRGBColorSpace); }  // (the hex as is: the tile's colours are sRGB bytes)
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
  const satOnly = spec.id === 'satellite' ? 0 : [...want].filter((t) => t.mesh?.visible && t.sat).length;
  Object.assign(LOD.stats, { drawn, kept: [...LOD.tiles.values()].filter((t) => t.mesh).length, bytes, byLevel, records: LOD.tiles.size, satOnly });
  legendNote(drawn > 0 && state.layer !== 'satellite' && (spec.id === 'satellite' || satOnly > 0)
    ? `Detail tiles: ${spec.id === 'satellite' ? 'this layer has no fine version; they show the satellite view' : `${satOnly} drawn without this layer show the satellite view`}.` : '');

  // the memory pool: keep at most MAX_TILES / MAX_BYTES, dropping the least recently drawn; forget old records
  if (LOD.stats.kept > MAX_TILES || bytes > MAX_BYTES) {
    const old = [...LOD.tiles.values()].filter((t) => t.mesh && !t.mesh.visible && !t.loading && !t.riverLoading).sort((a, b) => a.lastUsed - b.lastUsed);
    let n = LOD.stats.kept, b = bytes;
    for (const t of old) { if (n <= MAX_TILES * 0.9 && b <= MAX_BYTES * 0.9) break; n--; b -= t.bytes; dropTile(t); LOD.stats.dropped++; }
  }
  if (LOD.tiles.size > 4 * MAX_TILES) for (const [id, t] of LOD.tiles) if (!t.mesh && !t.loading && now - t.seen > FORGET_MS) LOD.tiles.delete(id);
}
// one line under the legend while tiles are drawn and the layer can't follow onto some of them
let noteEl = null;
function legendNote(text) {
  if (!noteEl) {
    if (!text) return;
    const lg = document.getElementById('legend');
    if (!lg) return;
    noteEl = document.createElement('div');
    noteEl.id = 'lod-legend-note'; noteEl.className = 'muted'; noteEl.style.fontSize = '11px';
    lg.insertAdjacentElement('afterend', noteEl);
  }
  if (noteEl.textContent !== text) { noteEl.textContent = text; noteEl.style.display = text ? '' : 'none'; }
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
