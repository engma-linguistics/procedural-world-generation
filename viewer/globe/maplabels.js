// Map labels (PW-1655, PW-1656): the names of a peoples run's continents, seas, states, towns and features (peaks, ranges, capes,
// bays, islands, lakes, rivers, regions) written on the globe, from GET /api/maplabels (planet/lineages/featnames.py). They thin
// out by zoom: far out only the continents and seas; closer the states, regions, ranges, big rivers and big islands; near the
// ground the towns, peaks, lakes, capes and bays. Each kind fades in from its own scale (the bigger of a kind sooner), and a label
// that would overlap one drawn before it (continents first, bays last) waits. A toggle writes the English Common (default,
// PW-1654) or what the locals call each place. Labels follow the slider: a town shows from its founding to its abandonment, a
// feature with the name it had then (none before it was first named), a state with the name of its capital then.
// HTML over the canvas (constant-size text, cheap overlap tests); laid out again only when the camera, frame or toggles change.
import * as THREE from 'three';
import { S, state, proj } from './state.js';
import { $, camera, group } from './scene.js';
import { unitVec } from './geometry.js';
import { lmGroup } from './axis.js';

// per kind: [pixels per degree where the biggest shows, where the smallest shows, hides above (px/deg), css class]
const KINDS = {
  continent: [0, 0, 70, 'cont'], sea: [0, 6, 1e9, 'sea'], state: [11, 26, 1e9, 'state'], region: [10, 26, 120, 'region'],
  range: [9, 30, 1e9, 'range'], river: [14, 44, 1e9, 'water'], city: [14, 30, 1e9, 'city'], island: [9, 44, 1e9, 'island'],
  lake: [20, 48, 1e9, 'water'], peak: [20, 50, 1e9, 'peak'], town: [30, 70, 1e9, 'town'], cape: [30, 60, 1e9, 'coast'],
  bay: [30, 60, 1e9, 'coast'],
};
const ORDER = Object.keys(KINDS);
const PX = { cont: 19, sea: 14, state: 12, region: 12, range: 12, water: 11, city: 13, island: 12, peak: 11, town: 11, coast: 11 };
const CSS = `
#mapLabels{position:fixed;left:0;top:0;pointer-events:none;overflow:hidden}
#mapLabels div{position:absolute;white-space:nowrap;transform:translate(-50%,-50%);font-family:-apple-system,sans-serif;
  text-shadow:0 0 3px #0b0f17,0 0 3px #0b0f17,0 0 2px #0b0f17;color:#f4f1e6;line-height:1}
#mapLabels .cont{font-size:19px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;opacity:.9}
#mapLabels .sea{font-size:14px;font-style:italic;letter-spacing:.12em;color:#9fd0ff}
#mapLabels .state{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#ffe2a8}
#mapLabels .region{font-size:12px;letter-spacing:.2em;color:#e8dcc0;opacity:.8}
#mapLabels .range{font-size:12px;font-style:italic;letter-spacing:.1em;color:#e2c8a0}
#mapLabels .water{font-size:11px;font-style:italic;color:#9fd0ff}
#mapLabels .city{font-size:13px;font-weight:700}
#mapLabels .town{font-size:11px}
#mapLabels .island{font-size:12px;color:#f0f0d8}
#mapLabels .peak{font-size:11px;color:#f0dcc0}
#mapLabels .peak::before{content:'\\25B2 ';font-size:8px}
#mapLabels .coast{font-size:11px;font-style:italic;color:#cfe6f0}`;

let box = null, doc = null, docFor = null, sig = '', pool = new Map(), posKey = '';

function setup() {
  if (box) return;
  const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
  box = document.createElement('div'); box.id = 'mapLabels'; $('c').after(box);  // (just above the globe, under the panels)
  if (window.planetViewer) window.planetViewer.mapLabels = () => [...box.children].map((e) => [e.className, e.textContent]);  // (what is drawn now: tools, tests)
  const lm = $('lmNames')?.closest('label');
  if (lm) {  // (the toggles beside 'Continent names'; peoples runs only)
    const w = document.createElement('span'); w.className = 'runOnly'; w.id = 'mapLabelsBox';
    w.innerHTML = '<label title="Names on the map (peoples runs): continents and seas far out; states, regions, mountain ranges, big rivers and islands closer; towns, peaks, lakes, capes and bays near the ground. Who named each feature and when: features.json (planet features RUN)."><input type="checkbox" id="mapLabelsOn" checked> Map labels</label> '
      + '<select id="mapLabelLang" title="The English Common (the names as an English map would give them) or what the people there call each place now"><option value="english">English Common</option><option value="local">local names</option></select>';
    lm.after(w);
    $('mapLabelsOn').onchange = $('mapLabelLang').onchange = () => { sig = ''; };
  }
}

function load(v) {
  if (docFor === v) return;
  docFor = v; doc = null; posKey = '';
  fetch(`../api/maplabels?run=${encodeURIComponent(v.dir)}`, { cache: 'no-store' }).then((r) => r.json()).then((j) => {
    if (docFor !== v || !j.labels) return;
    const by = {};
    for (const l of j.labels) (by[l.kind] ??= []).push(l);
    for (const [k, ls] of Object.entries(by)) {  // (each kind's rank by size: the bigger shows from further out)
      ls.sort((a, b) => (b.size || 0) - (a.size || 0));
      const [lo, hi] = KINDS[k] || [0, 0];
      ls.forEach((l, i) => { l.minPpd = lo + (hi - lo) * (ls.length > 1 ? i / (ls.length - 1) : 0); });
    }
    j.labels.sort((a, b) => (ORDER.indexOf(a.kind) - ORDER.indexOf(b.kind)) || ((b.size || 0) - (a.size || 0)));
    doc = j; sig = '';
  }).catch(() => {});
}

// the name in force `ago` kyr ago in the chosen tongue (null: not there, or not yet named)
function nameAt(l, ago, local) {
  if (l.from_kyr != null && l.from_kyr < ago - 1e-6) return null;
  if (l.to_kyr != null && l.to_kyr >= ago - 1e-6) return null;
  if (Array.isArray(l.names) && l.names.length && l.names[0][0] != null) {
    let s = null;
    for (const x of l.names) if (x[0] >= ago - 1e-6) s = x;
    if (!s) return null;
    return (local ? s[2] : s[1]) || null;
  }
  return (local ? l.local : l.english) || l.english || l.local;
}

function ppd() {
  const f = innerHeight / 2 / Math.tan(camera.fov * Math.PI / 360);
  return state.mode === 'globe' ? f / Math.max(camera.position.length() - 1, 1e-3) * Math.PI / 180 : f / Math.max(camera.position.z, 1e-3) / 90;
}

const v3 = new THREE.Vector3(), nrm = new THREE.Vector3(), toCam = new THREE.Vector3();
export function updateMapLabels() {
  try { layout(); } catch (e) { if (!updateMapLabels.warned) { updateMapLabels.warned = true; console.warn('map labels:', e); } }  // (never the render loop's end)
}
function layout() {
  const v = S.V;
  const ok = v?.kind === 'run' && v.run?.kind === 'peoples' && state.tab !== 'zoom' && !(state.mode === 'map' && proj.on);
  setup();
  const on = ok && $('mapLabelsOn')?.checked !== false;
  if ($('mapLabelsBox')) $('mapLabelsBox').hidden = !(v?.kind === 'run' && v.run?.kind === 'peoples');
  lmGroup.visible = !on;  // (the labels write the continents themselves, in either tongue)
  if (!on) { if (box.childElementCount) { box.replaceChildren(); pool.clear(); sig = ''; } return; }
  load(v);
  if (!doc) return;
  const local = $('mapLabelLang')?.value === 'local', ago = -(v.run.frames[v.frame]?.t ?? 0);
  const cv = $('c').getBoundingClientRect();
  const s = [camera.matrixWorld.elements.join(), group.rotation.y, v.frame, local, cv.width, cv.height, cv.left, cv.top, state.mode].join('|');
  if (s === sig) return;
  sig = s;
  const pk = state.mode;  // (on the unit sphere or the flat map: the text is drawn over the canvas, the ground never hides it)
  if (pk !== posKey) { for (const l of doc.labels) l.p = state.mode === 'globe' ? unitVec(l.lat, l.lon) : [l.lon / 90, l.lat / 90, 0]; posKey = pk; }
  Object.assign(box.style, { left: cv.left + 'px', top: cv.top + 'px', width: cv.width + 'px', height: cv.height + 'px' });
  group.updateMatrixWorld();
  const scale = ppd(), taken = [], seen = new Set(), globe = state.mode === 'globe';
  for (const l of doc.labels) {
    const k = KINDS[l.kind];
    if (!k || scale < l.minPpd || scale > k[2]) continue;
    const text = nameAt(l, ago, local);
    if (!text) continue;
    v3.set(...l.p).applyMatrix4(group.matrixWorld);
    if (globe) {
      nrm.copy(v3).normalize(); toCam.copy(camera.position).sub(v3);
      if (nrm.dot(toCam) <= 0.02 * toCam.length()) continue;  // (the far side)
    }
    v3.project(camera);
    if (v3.z > 1 || Math.abs(v3.x) > 1.05 || Math.abs(v3.y) > 1.05) continue;
    const x = (v3.x + 1) / 2 * cv.width, y = (1 - v3.y) / 2 * cv.height, px = PX[k[3]];
    const w = text.length * px * (k[3] === 'cont' ? 0.85 : 0.62) / 2 + 4, h = px * 0.7 + 3;
    if (taken.some((b) => Math.abs(b[0] - x) < b[2] + w && Math.abs(b[1] - y) < b[3] + h)) continue;
    taken.push([x, y, w, h]);
    let el = pool.get(l.id);
    if (!el) { el = document.createElement('div'); pool.set(l.id, el); }
    el.className = k[3];
    if (el.textContent !== text) el.textContent = text;
    el.style.left = x.toFixed(1) + 'px'; el.style.top = y.toFixed(1) + 'px';
    if (el.parentNode !== box) box.appendChild(el);
    seen.add(l.id);
  }
  for (const [id, el] of pool) if (!seen.has(id) && el.parentNode) el.remove();
}
