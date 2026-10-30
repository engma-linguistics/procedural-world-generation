import * as THREE from 'three';
import { createNavigator } from '../navigator.js';
import { S, state } from './state.js';
import { $, group } from './scene.js';
import { disposeObj, lineObj, llPos } from './geometry.js';
import { openWorld } from './provenance.js';
import { zoomSource } from './zoom.js';
import { fetchHighlights } from './highlights.js';
import { stop } from './playback.js';
import { fillSelector, openRun } from './select.js';
// ------------------------------------------------------------ tabs: globe | regional zoom (zoom.html in an iframe)
state.tab = 'globe';
let fromPop = false;
export function showTab(tab, zoomId) {
  state.tab = tab;
  document.body.classList.toggle('zoomTab', tab === 'zoom');
  [...$('tabs').children].forEach((b) => b.classList.toggle('on', b.dataset.tab === tab));
  if (tab === 'zoom') {
    stop();
    // reloaded every time, so zooms made since show up in its list
    const q = new URLSearchParams(zoomId ? { id: zoomId } : {});
    if (S.V?.kind === 'run') q.set('run', S.V.dir); else if (S.V?.id) q.set('world', S.V.id);
    const fw = $('zoomFrame').contentWindow;  // (location.replace: reloading by .src would add a back-button step of its own)
    if ($('zoomFrame').getAttribute('src')) fw.location.replace('zoom.html?' + q); else $('zoomFrame').src = 'zoom.html?' + q;
  }
  const u = new URL(location);
  if (tab === 'zoom') u.searchParams.set('tab', 'zoom'); else u.searchParams.delete('tab');
  const newZoom = zoomId && zoomId !== new URLSearchParams(location.search).get('zoom');
  if (zoomId) u.searchParams.set('zoom', zoomId);
  history[newZoom && !fromPop ? 'pushState' : 'replaceState'](null, '', u);  // (a new zoom is a step for the back button)
  navSync();
}
$('tabs').addEventListener('click', (e) => { if (e.target.dataset.tab) showTab(e.target.dataset.tab); });

// ------------------------------------------------------------ world navigator (PW-473, navigator.js)
// A bar with the provenance chain of what is on screen and the planet's family tree; it opens things
// through navOpen and learns what is on screen through navSync (called when a run, a world or the tab changes).
function navView() {
  if (state.tab === 'zoom') { const z = new URLSearchParams(location.search).get('zoom'); if (z) return { kind: 'zoom', id: z }; }
  if (!S.V) return null;
  if (S.V.kind === 'run') return { kind: S.V.tz ? 'timezoom' : 'run', id: S.V.dir, t: S.V.t };
  return S.V.id ? { kind: 'world', id: S.V.id } : null;
}
export function navSync() { S.navUi?.set(navView()); }
async function navOpen(n, planet, t) {
  await fillSelector();
  if (state.tab === 'zoom' && n.kind !== 'zoom') showTab('globe');
  if (n.phase === 'lineages') state.layer = 'peoples';  // (a peoples run opens on its own layer)
  if (n.kind === 'run' || n.kind === 'timezoom') await openRun(n.id, t);
  else if (n.kind === 'world') await openWorld(n.file);
  else {
    if (!(S.V?.kind === 'world' && S.V.id === n.world)) {
      const w = planet.nodes.find((x) => x.key === 'world:' + n.world);
      if (w) await openWorld(w.file);
    }
    showTab('zoom', n.id);
  }
}
// the zoom tab's page tells which zoom it shows (picked in its own list, or a fine zoom opened there)
addEventListener('message', (e) => {
  if (e.origin !== location.origin || e.source !== $('zoomFrame').contentWindow || !e.data?.zoomOpen || state.tab !== 'zoom') return;
  const u = new URL(location);
  if (u.searchParams.get('zoom') === e.data.zoomOpen) return;
  u.searchParams.set('zoom', e.data.zoomOpen);
  history.pushState(null, '', u);
  navSync();
});
// back / forward: show what the address says
addEventListener('popstate', () => {
  const q = new URLSearchParams(location.search);
  fromPop = true;
  try { if (q.get('tab') === 'zoom') showTab('zoom', q.get('zoom')); else showTab('globe'); } finally { fromPop = false; }
});
// the world on screen and which of the optional layers it lacks (the navigator's "Add resources / coasts")
function navLayers() {
  if (S.V?.kind !== 'world' || !S.V.id || !S.V.layers) return null;
  return { world: S.V.id, resources: !!(S.V.layers.resource || Object.keys(S.V.layers).some((k) => k.startsWith('res_'))), coast: !!S.V.layers.coast_type };
}
S.navUi = createNavigator({ openNode: navOpen, layers: navLayers, findHighlights: () => fetchHighlights(false), zoomSource: () => (S.V ? zoomSource() : null), picked: () => S.picked });

// The squares of the zooms already made of what is on screen (a world, or the world made from this run
// frame), clickable on their edge: a click there opens that zoom instead of picking a cell.
export const zoomOutlines = new THREE.Group();
group.add(zoomOutlines);
function zoomsOnScreen() {
  if (!S.V) return [];
  const worlds = S.V.kind === 'world' ? [S.V.id] : S.V.tz ? [] : S.IDX.worlds.filter((w) => w.source_run === S.V.dir && w.t_myr === S.V.t && !w.timezoom).map((w) => w.id);
  return S.IDX.zooms.filter((z) => worlds.includes(z.world) && !z.parent_zoom && z.center);
}
function wideSprite(text, color) {  // (a label of a few words: textSprite's canvas is square)
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 64;
  const g = cv.getContext('2d');
  g.font = 'bold 32px -apple-system, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 6; g.strokeStyle = '#0b0f17'; g.strokeText(text, 128, 34);
  g.fillStyle = color; g.fillText(text, 128, 34);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthWrite: false, alphaTest: 0.05 }));
  sp.renderOrder = 5;  // (after the 3D relief's translucent sea: PW-839)
  return sp;
}
export function buildZoomOutlines() {
  zoomOutlines.children.forEach(disposeObj);
  zoomOutlines.clear();
  const globe = state.mode === 'globe', r0 = globe ? 1.012 : 1;
  const wraps = (a, b) => !globe && Math.abs(a[0] - b[0]) > 2;
  for (const z of zoomsOnScreen()) {
    const { lat, lon } = z.center, h = z.size_km / 2 / 111.2, cl = Math.max(Math.cos(lat * Math.PI / 180), 0.1), pts = [];
    const corners = [[-h, -h], [-h, h], [h, h], [h, -h], [-h, -h]];
    for (let c = 0; c < 4; c++) for (let k = 0; k < 8; k++) {
      const [a0, b0] = corners[c], [a1, b1] = corners[c + 1];
      const f = (t) => llPos(lat + a0 + (a1 - a0) * t, lon + (b0 + (b1 - b0) * t) / cl, r0);
      const p1 = f(k / 8), p2 = f((k + 1) / 8);
      if (!wraps(p1, p2)) pts.push(...p1, ...p2);
    }
    zoomOutlines.add(lineObj(pts, 0x7cc4ff, 0.9));
    const label = wideSprite(`${z.id} · ${z.size_km} km`, '#7cc4ff');
    label.position.set(...(globe ? llPos(lat + h + 0.6, lon, 1.03) : llPos(lat + h + 1.5, lon, 1, 0.01)));
    label.scale.set(globe ? 0.13 : 0.1, globe ? 0.0325 : 0.025, 1);
    zoomOutlines.add(label);
  }
}
// the zoom whose outline (its edge, a generous band) is at cell i, if any
export function outlineAt(i) {
  const lat = S.V.grid.lat[i], lon = S.V.grid.lon[i];
  for (const z of zoomsOnScreen()) {
    const h = z.size_km / 2 / 111.2, cl = Math.max(Math.cos(z.center.lat * Math.PI / 180), 0.1);
    const dy = Math.abs(lat - z.center.lat), dx = Math.abs(((lon - z.center.lon + 540) % 360) - 180) * cl;
    const m = Math.max(dy, dx) / h;
    if (m >= 0.75 && m <= 1.15) return z;
  }
  return null;
}
