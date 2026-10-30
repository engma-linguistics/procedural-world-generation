import * as THREE from 'three';
import { S, state } from './state.js';
import { $, camera, controls, group } from './scene.js';
import { disposeObj, lineObj, llPos, unitVec } from './geometry.js';
import { textSprite } from './axis.js';
import { projOverlaysChanged } from './map2d.js';
import { pickCell, renderZoomBox } from './zoom.js';
import { showTab } from './tabs.js';
import { setFrame } from './load.js';
import { stop } from './playback.js';
import { urlp } from './select.js';
// ------------------------------------------------------------ highlights
// The server (planet/highlights.py) looks over a world for its most
// interesting places: the highest peak, the longest range, big river mouths,
// fjord coasts, wine country... For a run it first builds the full world for
// the frame on screen (a few seconds, once). Clicking one turns the globe to
// it and picks it for a zoom, with the suggested size.
let hl = null;        // {key, t, features, world} from GET /api/highlights
let hlSel = -1;       // index of the selected feature
let hlSeenKey = null, hlPeekTimer = null;
export const hlGroup = new THREE.Group();
group.add(hlGroup);

export function viewKey() { return !S.V ? null : S.V.kind === 'run' ? `run:${S.V.dir}@${S.V.t}` : `world:${S.V.id}`; }
function hlQuery() {
  if (S.V.tz) return null;
  if (S.V.kind === 'run') return `run=${encodeURIComponent(S.V.dir)}&t=${S.V.t}`;
  return S.V.id ? `world=${encodeURIComponent(S.V.id)}` : null;
}

// cached=true only asks whether highlights were already found for this view
export async function fetchHighlights(cached) {
  const q = hlQuery(), key = viewKey();
  if (!q) { $('hlStatus').textContent = S.V.tz ? 'Not for time zooms: find them in the source run.' : 'Only for runs and saved worlds.'; return; }
  if (!cached) {
    $('hlFind').disabled = true;
    $('hlStatus').textContent = S.V.kind === 'run' && !(hl && hl.key === key)
      ? `Building the world at ${S.V.t} Myr and looking around (a few seconds)…` : 'Looking around…';
  }
  let r = null, out = {};
  try { r = await fetch(`../api/highlights?${q}${cached ? '&cached=1' : ''}`, { cache: 'no-store' }); out = await r.json(); }
  catch (err) { out = { error: r ? `HTTP ${r.status}` : 'no server' }; }
  $('hlFind').disabled = false;
  if (key !== viewKey()) return;  // the view moved on meanwhile
  if (!r || !r.ok) {
    if (!cached) $('hlStatus').innerHTML = `<span class="err">${r && r.status !== 404 && r.status !== 501 ? out.error
      : 'The server has no highlights API. Restart it: uv run python -m planet serve'}</span>`;
    return;
  }
  if (!out.features) { if (!hl || hl.key !== key) renderHighlights(); return; }
  if (!hl || hl.key !== key) hlSel = -1;  // a refresh of the same list keeps the selection
  hl = { key, t: out.t_myr, world: out.world, features: out.features };
  renderHighlights();
  buildHighlightMarks(); projOverlaysChanged();
  // ?hl=<rank>: open that highlight once, the first time a list arrives
  if (urlp.has('hl')) {
    const k = hl.features.findIndex((f) => f.rank === +urlp.get('hl'));
    urlp.delete('hl');
    if (k >= 0) { goToHighlight(k); $('hlList').querySelector('.hl.sel')?.scrollIntoView({ block: 'nearest' }); }
  }
}
$('hlFind').addEventListener('click', () => fetchHighlights(false));
$('hlMarks').addEventListener('change', buildHighlightMarks);

// categories (planet/highlights.py CATEGORIES): a colour each, on the markers and the list,
// and a filter (state.hlCat, '' = all; ?hlcat= in the URL)
export const HL_CATS = { landscape: '#e8b86a', water: '#5fb8ff', climate: '#8fe07a', travel: '#ff8ad8', geology: '#ff6b4a', vegetation: '#3ccf9a' };
const hlColor = (f) => HL_CATS[f.category] || '#c0c0c0';
const hlShown = (f) => !state.hlCat || f.category === state.hlCat;
state.hlCat = '';  // (?hlcat=: applyUrlOptions)
function renderHlCats() {
  const el = $('hlCats');
  if (!hl) { el.innerHTML = ''; return; }
  const cnt = {};
  for (const f of hl.features) cnt[f.category] = (cnt[f.category] || 0) + 1;
  el.innerHTML = `<button data-c="" class="${state.hlCat ? '' : 'on'}">all ${hl.features.length}</button>` +
    Object.entries(HL_CATS).filter(([c]) => cnt[c]).map(([c, col]) =>
      `<button data-c="${c}" class="${state.hlCat === c ? 'on' : ''}" style="${state.hlCat === c ? 'color:' + col : ''}"><span class="dot" style="background:${col}"></span>${c} ${cnt[c]}</button>`).join('');
}
$('hlCats').addEventListener('click', (e) => {
  const b = e.target.closest('button'); if (!b) return;
  state.hlCat = b.dataset.c;
  const u = new URL(location);
  if (state.hlCat) u.searchParams.set('hlcat', state.hlCat); else u.searchParams.delete('hlcat');
  history.replaceState(null, '', u);
  renderHighlights(); buildHighlightMarks(); projOverlaysChanged();
});
function renderHighlights() {
  const here = hl && hl.key === viewKey();
  const list = $('hlList');
  list.classList.toggle('stale', !!hl && !here);
  renderHlCats();
  if (!hl) {
    $('hlStatus').textContent = 'Not looked for yet' + (S.V && S.V.kind === 'run' ? ` at ${S.V.t} Myr.` : '.');
    list.innerHTML = '';
    return;
  }
  $('hlStatus').innerHTML = here ? `${hl.features.length} places, best first · world ${hl.world}`
    : `These are for t = ${hl.t} Myr (click one to go back there), or find them for ${S.V.t} Myr.`;
  list.innerHTML = hl.features.map((f, k) => {
    if (!hlShown(f) && k !== hlSel) return '';
    let html = `<div class="hl ${k === hlSel ? 'sel' : ''}" data-k="${k}"><span class="k">${f.rank}.</span>` +
      `<span class="dot" style="background:${hlColor(f)}" title="${f.category || ''}"></span><b>${f.title}</b>`;
    if (k === hlSel) {
      html += `<div class="blurb">${f.blurb}<br>`;
      if (f.zoom) html += `<a href="#" data-zoom="${f.zoom}">open zoom ${f.zoom}</a> (made already)`;
      else if (f.zoomable) html += `"Zoom" in the info box (top right) refines this ${f.size_km} km square`;
      html += '</div>';
    }
    return html + '</div>';
  }).join('');
}

$('hlList').addEventListener('click', (e) => {
  if (e.target.dataset.zoom) { e.preventDefault(); showTab('zoom', e.target.dataset.zoom); return; }
  const row = e.target.closest('.hl'); if (!row) return;
  goToHighlight(+row.dataset.k);
});

function goToHighlight(k) {
  const f = hl.features[k];
  hlSel = k;
  if (S.V.kind === 'run' && S.V.t !== hl.t) {  // back to the frame these were found for
    stop();
    setFrame(S.V.run.frames.findIndex((fr) => fr.t === hl.t));
  }
  $('spin').checked = false;
  turnTo(f.lat, f.lon);
  if (f.zoomable) S.zoomSize = f.size_km;
  pickCell(f.cell);
  S.picked.lat = f.lat; S.picked.lon = f.lon;  // exactly what `planet highlights --zoom` used, so zoom ids match
  renderZoomBox();
  renderHighlights();
}

// Turn the globe (smoothly) so lat/lon faces the camera; on the flat map, pan to it.
export function turnTo(lat, lon) {
  if (state.mode !== 'globe') {
    const x = lon / 90, y = lat / 90;
    camera.position.set(x, y, camera.position.z); controls.target.set(x, y, 0);
    return;
  }
  const d = camera.position.distanceTo(controls.target);
  lat = Math.max(-80, Math.min(80, lat));  // looking straight down a pole confuses the orbit controls
  const to = new THREE.Vector3(...unitVec(lat, lon)).applyQuaternion(group.quaternion).normalize();
  const from = camera.position.clone().sub(controls.target).normalize();
  controls.target.set(0, 0, 0);
  const t0 = performance.now(), ms = 700;
  const step = (now) => {
    const a = Math.min((now - t0) / ms, 1), e = a * a * (3 - 2 * a);
    const q = new THREE.Quaternion().setFromUnitVectors(from, to);
    const dir = from.clone().applyQuaternion(new THREE.Quaternion().slerp(q, e));
    camera.position.copy(dir.multiplyScalar(d));
    camera.lookAt(0, 0, 0);
    if (a < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// Numbered rings (and courses: rivers, range spines) on the globe, for the
// view the highlights were found for. Called at the end of buildOverlays.
export function buildHighlightMarks() {
  hlGroup.children.forEach(disposeObj);
  hlGroup.clear();
  const key = viewKey();
  if (key !== hlSeenKey) {  // the view changed: see if highlights were already found for it
    if (hl && key && hl.key.split('@')[0] !== key.split('@')[0]) { hl = null; hlSel = -1; }  // another run/world
    hlSeenKey = key;
    clearTimeout(hlPeekTimer);
    if (key && !state.playing) hlPeekTimer = setTimeout(() => fetchHighlights(true), 400);
    renderHighlights();
  }
  if (!hl || hl.key !== key || !$('hlMarks').checked) return;
  const globe = state.mode === 'globe', r0 = globe ? 1.016 : 1;
  const wraps = (a, b) => !globe && Math.abs(a[0] - b[0]) > 2;
  const rings = {}, paths = {}, sel = [];
  hl.features.forEach((f, k) => {
    if (!hlShown(f) && k !== hlSel) return;
    const col = hlColor(f), out = k === hlSel ? sel : (rings[col] ||= []), cl = Math.max(Math.cos(f.lat * Math.PI / 180), 0.2), rad = k === hlSel ? 2.2 : 1.4;
    for (let j = 0; j < 20; j++) {
      const a1 = j / 20 * 2 * Math.PI, a2 = (j + 1) / 20 * 2 * Math.PI;
      const p1 = llPos(f.lat + rad * Math.sin(a1), f.lon + rad * Math.cos(a1) / cl, r0);
      const p2 = llPos(f.lat + rad * Math.sin(a2), f.lon + rad * Math.cos(a2) / cl, r0);
      if (!wraps(p1, p2)) out.push(...p1, ...p2);
    }
    for (let j = 0; f.path && j < f.path.length - 1; j++) {
      const p1 = llPos(...f.path[j], r0), p2 = llPos(...f.path[j + 1], r0);
      if (!wraps(p1, p2)) (paths[col] ||= []).push(...p1, ...p2);
    }
    const label = textSprite(String(f.rank), k === hlSel ? '#ffffff' : col);
    const lp = globe ? llPos(f.lat + rad, f.lon, 1.03) : llPos(f.lat + rad + 1.5, f.lon, 1, 0.01);
    label.position.set(...lp);
    label.scale.setScalar(globe ? 0.075 : 0.06);
    hlGroup.add(label);
  });
  for (const [col, pts] of Object.entries(rings)) hlGroup.add(lineObj(pts, col));
  for (const [col, pts] of Object.entries(paths)) hlGroup.add(lineObj(pts, col, 0.8));
  hlGroup.add(lineObj(sel, 0xffffff));
}
