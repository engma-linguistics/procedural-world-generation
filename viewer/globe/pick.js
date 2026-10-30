import * as THREE from 'three';
import { esc } from '../planets.js';
import { S, state } from './state.js';
import { $, DIAG, camera, controls, fitMap, group, relief3d, renderer } from './scene.js';
import { buildTopology, nearestCellU, paint } from './geometry.js';
import { renderTip } from './panel.js';
import { closeDetail, describe, infoBoxHtml, openDetail, renderDetail } from './describe.js';
import { syncProj } from './map2d.js';
import { pickCell, startZoom } from './zoom.js';
import { turnTo } from './highlights.js';
import { outlineAt, showTab } from './tabs.js';
import { refresh } from './load.js';
// hover / click
export const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
// The cell under the pointer on the globe (PW-679). three's raycast tests every triangle (~1 M at L7,
// ~25 ms a mouse move); the ray only crosses the thin shell between the lowest and the highest
// surface point, so walk it in half-cell steps, take the cells nearest those points and their
// neighbours, and test only their triangles (Moller-Trumbore, nearest hit). Same cell as the full
// raycast (planetViewer.pickCheck). undefined: not the globe, use the full raycast.
const pickTmp = new THREE.Matrix4();
export function pickGlobeCell() {
  const T = S.topo;
  if (!T.globe || !T.triStart || !T.maxR || !(T.minR < Infinity)) return undefined;
  const rr = ray.ray.clone().applyMatrix4(pickTmp.copy(S.mesh.matrixWorld).invert());
  const o = rr.origin, d = rr.direction, b = o.dot(d), c0 = o.dot(o);
  const dOut = b * b - (c0 - T.maxR * T.maxR);
  if (dOut < 0) return -1;
  const sOut = Math.sqrt(dOut);
  let t0 = Math.max(-b - sOut, 0), t1 = -b + sOut;
  if (t1 < 0) return -1;
  const rIn = Math.max(T.minR - 1e-4, 1e-3), dIn = b * b - (c0 - rIn * rIn);
  if (dIn >= 0) { const ti = -b - Math.sqrt(dIn); if (ti >= t0) t1 = Math.min(t1, ti); }
  const G = S.V.grid, n = S.V.n, pos = S.mesh.geometry.attributes.position.array, idx = S.mesh.geometry.index?.array, tri = T.triStart;
  const step = 0.5 * Math.sqrt(4 * Math.PI / n), seen = new Set(), P = [0, 0, 0];
  let best = -1, bt = Infinity;
  const test = (c) => {
    if (seen.has(c)) return; seen.add(c);
    for (let t = tri[c]; t < tri[c + 1]; t++) {
      const ia = idx ? idx[3 * t] : 3 * t, ib = idx ? idx[3 * t + 1] : 3 * t + 1, ic = idx ? idx[3 * t + 2] : 3 * t + 2;
      const ax = pos[3 * ia], ay = pos[3 * ia + 1], az = pos[3 * ia + 2];
      const e1x = pos[3 * ib] - ax, e1y = pos[3 * ib + 1] - ay, e1z = pos[3 * ib + 2] - az;
      const e2x = pos[3 * ic] - ax, e2y = pos[3 * ic + 1] - ay, e2z = pos[3 * ic + 2] - az;
      const px = d.y * e2z - d.z * e2y, py = d.z * e2x - d.x * e2z, pz = d.x * e2y - d.y * e2x;
      const det = e1x * px + e1y * py + e1z * pz;
      if (Math.abs(det) < 1e-14) continue;
      const inv = 1 / det, sx = o.x - ax, sy = o.y - ay, sz = o.z - az;
      const u = (sx * px + sy * py + sz * pz) * inv;
      if (u < 0 || u > 1) continue;
      const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x;
      const v = (d.x * qx + d.y * qy + d.z * qz) * inv;
      if (v < 0 || u + v > 1) continue;
      const tt = (e2x * qx + e2y * qy + e2z * qz) * inv;
      if (tt >= 0 && tt < bt) { bt = tt; best = c; }
    }
  };
  for (let t = t0; ; t += step) {
    const tc = Math.min(t, t1), x = o.x + d.x * tc, y = o.y + d.y * tc, z = o.z + d.z * tc, l = Math.hypot(x, y, z) || 1;
    P[0] = x / l; P[1] = y / l; P[2] = z / l;
    const c = nearestCellU(P);
    test(c); for (const j of G.nbr[c]) test(j);
    if (tc >= t1) break;
  }
  return best;
}
export function updateHover() {
  if (!S.mesh) return;
  ray.setFromCamera(mouse, camera);
  const fast = pickGlobeCell();
  if (fast !== undefined) S.hovered = fast;
  else { const hit = ray.intersectObject(S.mesh)[0]; S.hovered = hit ? S.topo.triCell[hit.faceIndex] : -1; }
  renderHover();
}
export function renderHover() {
  renderTip();
  if (S.detailCell >= 0) renderDetail();  // (a new frame: the panel follows)
  if (S.picked) return;  // the info box stays on the clicked cell until it's closed
  const html = S.hovered >= 0 ? infoBoxHtml(S.hovered) + '<div class="muted ifoot">click: copy and pick for zooming · double-click: zoom</div>'
    : '<span class="muted">Hover a cell. Click to copy its description and pick it for a regional zoom; double-click to zoom straight in.</span>';
  // (only when it changes, PW-415: rewriting the same box on every mouse move, as over empty
  // space, repainted the panel over the canvas each time, and on the owner's Chrome each
  // such repaint flickered the rivers; ?rehover=1 rewrites it every time, for comparison)
  if (html === S.infoHtml && !DIAG.rehover) return;
  S.infoHtml = html; DIAG.n.info++;
  $('infoText').innerHTML = html;
}
$('infoText').addEventListener('click', (e) => {
  if (e.target.dataset.act !== 'more') return;
  const i = S.picked ? S.picked.i : S.hovered;
  if (i >= 0) openDetail(i);
});
$('detail').addEventListener('click', (e) => { if (e.target.id === 'detail' || e.target.dataset.act === 'close') closeDetail(); });
renderer.domElement.addEventListener('pointermove', (e) => {
  mouse.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  updateHover();
});
let downAt = null;
renderer.domElement.addEventListener('pointerdown', (e) => { downAt = [e.clientX, e.clientY]; });
renderer.domElement.addEventListener('pointerup', (e) => {
  if (!downAt || S.hovered < 0 || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 4) return;
  const zo = !S.picked && outlineAt(S.hovered);  // the edge of a zoom already made: open it (click inside to zoom elsewhere)
  if (zo) { toast(`Opening zoom ${zo.id}`); showTab('zoom', zo.id); return; }
  const txt = `${refOf(S.hovered)} ${S.V.name}: ` + describe(S.hovered).join(', ') + ` ${linkOf(S.hovered)}`;
  navigator.clipboard?.writeText(txt).then(() => toast('Copied: ' + txt.slice(0, 60) + '…'), () => {});
  pickCell(S.hovered);
});
renderer.domElement.addEventListener('dblclick', () => { if (S.hovered >= 0) { pickCell(S.hovered); startZoom(); } });
// References (PW-105, convention in issue-tracking/README.md): run:<id>@<t>Myr(lat,lon) or
// world:<id>(lat,lon), and a deep link that reopens the viewer there (?run=&t=&lat=&lon=, picking the cell)
function refOf(i) {
  const ll = `(${S.V.grid.lat[i].toFixed(2)},${S.V.grid.lon[i].toFixed(2)})`;
  if (S.V.kind === 'run') return `run:${S.V.run.id || S.V.dir}@${S.V.t}Myr${ll}`;
  return S.V.id ? `world:${S.V.id}${ll}` : ll;
}
function linkOf(i) {
  const u = new URL(location.href);
  for (const k of [...u.searchParams.keys()]) if (!['mode', 'layer'].includes(k)) u.searchParams.delete(k);
  if (S.V.kind === 'run') { u.searchParams.set('run', S.V.dir); u.searchParams.set('t', S.V.t); }
  else if (S.V.id) u.searchParams.set('world', S.V.id + '.json');
  u.searchParams.set('lat', S.V.grid.lat[i].toFixed(2)); u.searchParams.set('lon', S.V.grid.lon[i].toFixed(2));
  return u.href;
}
// ?lat=&lon=: turn to the place and pick the nearest cell
export function goToLatLon(lat, lon) {
  const r = Math.PI / 180, x = Math.cos(lat * r) * Math.cos(lon * r), y = Math.cos(lat * r) * Math.sin(lon * r), z = Math.sin(lat * r);
  const G = S.V.grid; let best = -1, bd = -2;
  for (let i = 0; i < S.V.n; i++) {
    const a = G.lat[i] * r, b = G.lon[i] * r, d = Math.cos(a) * (Math.cos(b) * x + Math.sin(b) * y) + Math.sin(a) * z;
    if (d > bd) { bd = d; best = i; }
  }
  $('spin').checked = false;
  turnTo(lat, lon);
  pickCell(best);
}
export function toast(t) { const el = $('toast'); el.textContent = t; el.style.opacity = 1; setTimeout(() => (el.style.opacity = 0), 1800); }

// collapsible panel sections: remember which are open. localStorage can be
// missing or throw (private windows, file://), so every access is guarded.
const SECTIONS_KEY = 'planetViewer.sections';
let openSections = {};
try { openSections = JSON.parse(localStorage.getItem(SECTIONS_KEY)) || {}; } catch { openSections = {}; }
document.querySelectorAll('details.sec').forEach((d) => {
  if (d.dataset.sec in openSections) d.open = !!openSections[d.dataset.sec];
  d.addEventListener('toggle', () => {
    openSections[d.dataset.sec] = d.open;
    try { localStorage.setItem(SECTIONS_KEY, JSON.stringify(openSections)); } catch { /* not saved */ }
  });
});
// the summary (bottom right) folds down to its title bar; remembered the same way
const SUMMARY_KEY = 'planetViewer.summaryCollapsed';
try { $('summary').classList.toggle('collapsed', localStorage.getItem(SUMMARY_KEY) === '1'); } catch { /* open */ }
$('sumToggle').addEventListener('click', () => {
  const c = $('summary').classList.toggle('collapsed');
  try { localStorage.setItem(SUMMARY_KEY, c ? '1' : '0'); } catch { /* not saved */ }
});

function seg(id, key, after) {
  $(id).addEventListener('click', (e) => {
    const v = e.target.dataset?.v; if (!v) return;
    state[key] = v;
    [...$(id).children].forEach((b) => b.classList.toggle('on', b.dataset.v === v));
    after();
  });
}
seg('layerSeg', 'layer', () => refresh(paint));
// the plant functional type shown by the 'plant type' layer (?pft=BoNS)
state.pft = 'TrBE';
export function pftColor() { return new THREE.Color(S.V.pfts.find((p) => p.code === state.pft)?.color || '#ffffff'); }
export function fillPfts() {
  if (!S.V?.pfts?.length) return;
  if (!S.V.pfts.some((p) => p.code === state.pft)) state.pft = S.V.pfts[0].code;
  $('pftSel').innerHTML = S.V.pfts.map((p) => `<option value="${p.code}"${p.code === state.pft ? ' selected' : ''}>${p.code}: ${esc(p.name)}</option>`).join('');
}
$('pftSel').addEventListener('change', () => {
  state.pft = $('pftSel').value;
  const u = new URL(location); u.searchParams.set('pft', state.pft); history.replaceState(null, '', u);
  paint(); updateHover();
});
state.obs = 'model';
seg('obsSeg', 'obs', paint);
// the globe turns; the flat map only pans, unless it is a 3D relief model (it tilts)
export function canRotate() { controls.enableRotate = state.mode === 'globe' || relief3d(); }
seg('modeSeg', 'mode', () => {
  group.rotation.set(0, 0, 0);
  canRotate();
  controls.reset();
  if (state.mode === 'globe') { camera.position.set(0, 0.6, 3.4); controls.target.set(0, 0, 0); } else fitMap();
  syncProj();
  buildTopology(); paint();
});
