// The globe's line overlays at the ground (PW-1696): rivers, the human-use rivers, settlements, trade, the peoples'
// rings, the zoom outlines, the cell outlines, highlights and every other line overlay.
//
//   - Above DRAPE_KM (300 km over the ground) they are drawn as built (at the globe's full exaggeration, each with its
//     small lift) and eased in the vertex shader by the same factor as the cells (a uniform, LOD.relK; patchLine): they
//     come down with the ground as the exaggeration eases toward 1x. That alone can't put them on the ground near it:
//     their lift eases too but stays (a river's 0.003 radii is ~0.8 km at 1x with the relief slider at 25), and they
//     stand at the cells' heights, not the tiles' (measured: tools/viewer_lod_dive.py, float_km).
//   - Below DRAPE_KM the built overlays are hidden and copies "draped" on the drawn ground take their place: each
//     segment cut into pieces a share of their distance from the camera long (STEP_FRAC; finer near the camera), each
//     point put on the ground as drawn (lodtiles.js::groundRadius: the finest tile's own mesh, else the cells), and in
//     the shader pulled toward the camera by PULL of its distance (the screen position stays; only the depth test
//     changes, so a line on a slope is not swallowed by the triangles round it). Only the segments near what is in
//     view are draped (the region, rebuilt when the view leaves it, the height changes by REBUILD_H, the tiles drawn
//     change or the overlays are rebuilt). The draped points keep their exaggeration at the build in a uniform, so
//     the ease between 300 and 50 km needs no rebuild.
//   - What can't follow the ground is hidden below DRAPE_KM: labels (sprites), the clouds' shell, the spin axis.
// URL: ?drape=0 (no draping: the built overlays, eased, all the way down), ?drapekm=<km>.
import * as THREE from 'three';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { S, state } from './state.js';
import { camera, group } from './scene.js';
import { LOD, groundRadius } from './lodtiles.js';
import { zoomOutlines } from './tabs.js';
import { hlGroup } from './highlights.js';
import { axisGroup, lmGroup } from './axis.js';

const P = new URLSearchParams(location.search);
const R_KM = 6371, DRAPE_KM = +P.get('drapekm') || 300, DRAPE_OUT_KM = DRAPE_KM * 1.1;
const STEP_FRAC = 0.015, STEP_MIN_KM = 0.08, MAX_PIECES = 512, PULL = 0.003, REBUILD_H = 1.6, TILE_REBUILD_MS = 300, HIDDEN = 1;
export const DRAPE = { on: P.get('drape') !== '0', low: false, built: 0, ms: 0, msMax: 0, log: [], segs: 0, pieces: 0, objects: 0 };

// ---- the shader patch: the ease (radial, as the cells') and the pull toward the camera (view space) -----------------
const EASE = 'uniform float uRelK; uniform float uPullK;\n' +
  'vec3 lodEase(vec3 p) { float rr = length(p); return (uRelK != 1.0 && rr > 0.5) ? p * ((1.0 + (rr - 1.0) * uRelK) / rr) : p; }\n';
const BUILT = { relK: LOD.relK, pullK: { value: 1 } };            // (the built overlays: the cells' ease, no pull)
const DRAPED = { relK: { value: 1 }, pullK: { value: 1 - PULL } }; // (the draped copies: exaggeration now / at the build)
function patchLine(m, U) {
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uRelK = U.relK; sh.uniforms.uPullK = U.pullK;
    if (m.isShaderMaterial) {  // (LineMaterial: the ribbons)
      sh.vertexShader = sh.vertexShader.replace('void main() {', EASE + 'void main() {')
        .replace('vec4 start = modelViewMatrix * vec4( instanceStart, 1.0 );', 'vec4 start = modelViewMatrix * vec4( lodEase( instanceStart ), 1.0 ); start.xyz *= uPullK;')
        .replace('vec4 end = modelViewMatrix * vec4( instanceEnd, 1.0 );', 'vec4 end = modelViewMatrix * vec4( lodEase( instanceEnd ), 1.0 ); end.xyz *= uPullK;');
    } else {  // (LineBasicMaterial: the 1-pixel lines)
      sh.vertexShader = EASE + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n  transformed = lodEase( transformed );')
        .replace('#include <project_vertex>', '#include <project_vertex>\n  mvPosition.xyz *= uPullK; gl_Position = projectionMatrix * mvPosition;');
    }
  };
  m.customProgramCacheKey = () => 'lodLine';
  m.userData.lodLine = true;
  m.needsUpdate = true;
}
const isLine = (o) => o.isLineSegments2 || o.isLineSegments;
// the draped copy's material: one per built material (kept, as the overlays' own are)
const dmats = new WeakMap();
function drapedMat(m) {
  let c = dmats.get(m);
  if (!c) { c = m.clone(); c.userData = { shared: true }; patchLine(c, DRAPED); dmats.set(m, c); }
  c.opacity = m.opacity; c.transparent = m.transparent;
  if (m.resolution) c.resolution.copy(m.resolution);
  return c;
}

// ---- what is on the globe: the line overlays (draped), the rest (hidden when low) ------------------------------------
function sources() {
  const lines = [], other = [];
  const add = (o) => { if (!o || o.userData.draped) return; (isLine(o) ? lines : other).push(o); };
  Object.values(S.overlays || {}).forEach(add);
  zoomOutlines.children.forEach(add); hlGroup.children.forEach(add);
  lmGroup.children.forEach((o) => other.push(o)); axisGroup.children.forEach((o) => other.push(o));
  return { lines, other };
}
// the overlays as built get the ease (once per material)
function patchBuilt(lines) { for (const o of lines) if (!o.material.userData.lodLine) patchLine(o.material, BUILT); }

// ---- draping ---------------------------------------------------------------------------------------------------------
const dgroup = new THREE.Group(); dgroup.userData.draped = true;
group.add(dgroup);
let pairs = [], region = null, srcSig = '', tileSig = 0, lastTileBuild = 0;
const hidden = new Set();
function hide(o) { if (!hidden.has(o)) { o.layers.set(HIDDEN); hidden.add(o); } }
function unhideAll() { for (const o of hidden) o.layers.set(0); hidden.clear(); }
function clearDraped() { for (const { d } of pairs) { dgroup.remove(d); d.geometry.dispose(); } pairs = []; }

// segments (x0 y0 z0 x1 y1 z1 ...) and colours (r g b per end) of a built line object
function segsOf(o) {
  const g = o.geometry;
  if (o.isLineSegments2) {
    const s = g.attributes.instanceStart, c = g.attributes.instanceColorStart;
    return { pos: s ? s.data.array : new Float32Array(0), stride: s ? s.data.stride : 6, col: c ? c.data.array : null };
  }
  const a = g.attributes.position, c = g.attributes.color;
  return { pos: a ? a.array : new Float32Array(0), stride: 6, col: c ? c.array : null, colStride: 6 };
}
const camL = new THREE.Vector3(), cn = new THREE.Vector3(), ua = new THREE.Vector3(), ub = new THREE.Vector3(), w = new THREE.Vector3(), cp = new THREE.Vector3();
// the angle (rad) from the unit vector c to the chord a-b's nearest point
function segAngle(c, a, b) {
  cp.subVectors(b, a); const L2 = cp.lengthSq();
  const t = L2 > 0 ? Math.min(1, Math.max(0, w.subVectors(c, a).dot(cp) / L2)) : 0;
  w.copy(a).addScaledVector(cp, t).normalize();
  return Math.acos(Math.min(1, Math.max(-1, w.dot(c))));
}
// per built geometry, once: each segment's middle direction and half its angle (a quick test against the region)
const preps = new WeakMap();
function prep(o) {
  let p = preps.get(o.geometry);
  if (p) return p;
  const { pos, stride, col } = segsOf(o), n = Math.floor(pos.length / stride), mid = new Float32Array(3 * n), half = new Float32Array(n);
  let maxHalf = 0;
  for (let s = 0; s < n; s++) {
    const k = s * stride;
    ua.set(pos[k], pos[k + 1], pos[k + 2]); ub.set(pos[k + 3], pos[k + 4], pos[k + 5]);
    if (!(ua.lengthSq() > 0) || !(ub.lengthSq() > 0)) { half[s] = -1; continue; }
    ua.normalize(); ub.normalize();
    const hA = Math.acos(Math.min(1, Math.max(-1, ua.dot(ub)))) / 2;
    w.addVectors(ua, ub); if (!(w.lengthSq() > 1e-12)) w.copy(ua); w.normalize();
    mid[3 * s] = w.x; mid[3 * s + 1] = w.y; mid[3 * s + 2] = w.z; half[s] = hA; maxHalf = Math.max(maxHalf, hA);
  }
  p = { pos, stride, col, n, mid, half, maxHalf };
  preps.set(o.geometry, p);
  return p;
}
function drape(o, cam, rho) {
  const { pos, stride, col, n, mid, half, maxHalf } = prep(o), outP = [], outC = col ? [] : null;
  const cosLim = Math.cos(Math.min(Math.PI, rho + maxHalf)), cx = cn.x, cy = cn.y, cz = cn.z;
  let segs = 0;
  for (let s = 0; s < n; s++) {
    const dot = mid[3 * s] * cx + mid[3 * s + 1] * cy + mid[3 * s + 2] * cz;
    if (dot < cosLim || half[s] < 0 || Math.acos(Math.min(1, dot)) - half[s] > rho) continue;
    const k = s * stride;
    ua.set(pos[k], pos[k + 1], pos[k + 2]).normalize(); ub.set(pos[k + 3], pos[k + 4], pos[k + 5]).normalize();
    if (segAngle(cn, ua, ub) > rho) continue;
    segs++;
    // pieces: a share of the distance from the camera (from the nearer end or the nearest point of the chord)
    const dKm = Math.min(cam.distanceTo(ua), cam.distanceTo(ub), cam.distanceTo(w)) * R_KM;
    const step = Math.max(STEP_MIN_KM, dKm * STEP_FRAC), len = Math.acos(Math.min(1, Math.max(-1, ua.dot(ub)))) * R_KM;
    const m = Math.min(MAX_PIECES, Math.max(1, Math.ceil(len / step)));
    let px = 0, py = 0, pz = 0;
    for (let j = 0; j <= m; j++) {
      const t = j / m;
      w.copy(ua).multiplyScalar(1 - t).addScaledVector(ub, t);
      if (!(w.lengthSq() > 1e-12)) w.copy(ua);
      w.normalize();
      const r = groundRadius(w), x = w.x * r, y = w.y * r, z = w.z * r;
      if (j) {
        outP.push(px, py, pz, x, y, z);
        if (outC) {
          const t0 = (j - 1) / m;
          for (const tt of [t0, t]) for (let c = 0; c < 3; c++) outC.push(col[k + c] * (1 - tt) + col[k + 3 + c] * tt);
        }
      }
      px = x; py = y; pz = z;
    }
  }
  let d;
  if (o.isLineSegments2) {
    const g = new LineSegmentsGeometry();
    if (outP.length) { g.setPositions(outP); if (outC) g.setColors(outC); }
    d = new LineSegments2(g, drapedMat(o.material));
  } else {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(outP, 3));
    if (outC) g.setAttribute('color', new THREE.Float32BufferAttribute(outC, 3));
    d = new THREE.LineSegments(g, drapedMat(o.material));
  }
  Object.assign(d, { frustumCulled: false, renderOrder: o.renderOrder, raycast: () => {} });
  d.userData.draped = true;
  DRAPE.segs += segs; DRAPE.pieces += outP.length / 6;
  return d;
}

// the region the view needs: the angle round the camera's nadir that holds what the screen's corners and top edge see
// (the horizon where they see the sky)
const rc = new THREE.Raycaster(), nd = new THREE.Vector2(), sph = new THREE.Sphere(), hp = new THREE.Vector3();
function needed(r) {
  const hor = Math.acos(Math.min(1, 1 / r)) + 0.004;
  let a = 0;
  camera.updateMatrixWorld();
  sph.center.set(0, 0, 0); sph.radius = groundRadius(cn);
  for (const [x, y] of [[-1, -1], [1, -1], [-1, 1], [1, 1], [0, 1], [0, 0]]) {
    rc.setFromCamera(nd.set(x, y), camera);
    if (!rc.ray.intersectSphere(sph, hp)) return hor;
    group.worldToLocal(hp);
    a = Math.max(a, Math.acos(Math.min(1, hp.normalize().dot(cn))));
  }
  return Math.min(hor, a);
}

// each frame (after updateLod): low or not, the built overlays' ease, the draped copies kept up
export function updateDrape(now) {
  const { lines, other } = sources();
  patchBuilt(lines);
  const want = DRAPE.on && LOD.on && !!LOD.src && state.mode === 'globe' && state.tab !== 'zoom' && LOD.hgKm < (DRAPE.low ? DRAPE_OUT_KM : DRAPE_KM);
  if (!want) {
    if (DRAPE.low) { DRAPE.low = false; clearDraped(); unhideAll(); region = null; LOD.dirty = true; }
    return;
  }
  DRAPE.low = true;
  for (const o of hidden) if (!o.parent) hidden.delete(o);  // (rebuilt overlays: the old ones are gone)
  for (const o of lines) hide(o);
  for (const o of other) hide(o);
  if (S.overlays?.clouds) hide(S.overlays.clouds);
  camL.copy(camera.position); group.worldToLocal(camL);
  const r = camL.length(); cn.copy(camL).divideScalar(r);
  const hKm = LOD.hgKm, need = needed(r);
  const sig = lines.map((o) => o.id).join(',');
  let ts = 0;
  for (const t of LOD.tiles.values()) if (t.mesh?.visible) ts = (ts + (t.hsh ??= hashId(t.k.id)) * (t.fade >= 1 ? 2 : 1)) % 2147483647;
  const regionOk = region && Math.acos(Math.min(1, region.c.dot(cn))) + need <= region.rho && hKm < region.h * REBUILD_H && hKm > region.h / REBUILD_H;
  const tilesChanged = ts !== tileSig && now - lastTileBuild > TILE_REBUILD_MS;
  if (regionOk && sig === srcSig && !tilesChanged) { syncDraped(); return; }
  // rebuild
  const t0 = performance.now();
  clearDraped();
  DRAPE.segs = 0; DRAPE.pieces = 0;
  const rho = Math.min(Math.acos(Math.min(1, 1 / r)) + 0.004, Math.max(need * 1.5, need + 0.5 * hKm / R_KM, 20 / R_KM));
  for (const o of lines) { const dd = drape(o, camL, rho); dgroup.add(dd); pairs.push({ o, d: dd }); }
  DRAPED.relK.value = 1;
  region = { c: cn.clone(), rho, h: hKm, ex: LOD.ex };
  srcSig = sig; tileSig = ts; lastTileBuild = now;
  DRAPE.ms = +(performance.now() - t0).toFixed(1); DRAPE.msMax = Math.max(DRAPE.msMax, DRAPE.ms); DRAPE.built++; DRAPE.objects = pairs.length;
  DRAPE.log.push([+hKm.toFixed(2), DRAPE.ms, DRAPE.segs, DRAPE.pieces, +(rho * R_KM).toFixed(0)]); if (DRAPE.log.length > 200) DRAPE.log.shift();
  syncDraped();
  LOD.dirty = true;
}
// the draped copies follow their built twins' visibility, opacity and width; their exaggeration follows the tiles'
function syncDraped() {
  for (const { o, d } of pairs) {
    d.visible = o.visible;
    const c = d.material, m = o.material;
    if (c.opacity !== m.opacity) c.opacity = m.opacity;
    if (m.resolution && !c.resolution.equals(m.resolution)) c.resolution.copy(m.resolution);
  }
  const k = region && region.ex > 0 ? LOD.ex / region.ex : 1;
  if (k !== DRAPED.relK.value) { DRAPED.relK.value = k; LOD.dirty = true; }
}
function hashId(s) { let h = 7; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 2147483647; return h; }

// How far the line overlays stand off the drawn ground in view (planetViewer.drapeFloat: the dive tool): each point's
// height over the ground under it (km), for the built overlays as drawn above DRAPE_KM (eased like the cells) and for
// the draped copies: {n, median, p90, max} of |height|
export function drapeFloat() {
  camL.copy(camera.position); group.worldToLocal(camL);
  const r = camL.length(); cn.copy(camL).divideScalar(r);
  const rho = needed(r), v = new THREE.Vector3(), u = new THREE.Vector3();
  const stats = (xs) => {
    xs.sort((a, b) => a - b);
    const q = (f) => (xs.length ? +xs[Math.min(xs.length - 1, Math.floor(f * xs.length))].toFixed(4) : null);
    return { n: xs.length, median: q(0.5), p90: q(0.9), max: q(1) };
  };
  const off = (a, k, kk) => {
    v.set(a[k], a[k + 1], a[k + 2]);
    if (!(v.lengthSq() > 0) || Math.acos(Math.min(1, u.copy(v).normalize().dot(cn))) > rho) return null;
    return Math.abs(1 + (v.length() - 1) * kk - groundRadius(v)) * R_KM;
  };
  const built = [], draped = [];
  for (const o of sources().lines) {
    const { pos, stride, n } = prep(o);
    for (let s = 0; s < n; s++) for (const e of [0, 3]) { const h = off(pos, s * stride + e, LOD.relK.value); if (h !== null) built.push(h); }
  }
  for (const { d } of pairs) {
    const { pos, stride } = segsOf(d), m = Math.floor(pos.length / stride);
    for (let s = 0; s < m; s++) for (const e of [0, 3]) { const h = off(pos, s * stride + e, DRAPED.relK.value); if (h !== null) draped.push(h); }
  }
  return { region_km: +(rho * R_KM).toFixed(1), built: stats(built), draped: stats(draped) };
}
