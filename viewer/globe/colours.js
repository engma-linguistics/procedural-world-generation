import * as THREE from 'three';
import { S, state } from './state.js';
import { $ } from './scene.js';
import { cellPositions, llMode, llPoint, llPos, llPosPt, paint, ribbonObj, unitVec } from './geometry.js';
import { buildOverlays } from './overlays.js';
import { renderLayerButtons, renderLegend, renderRunSummary, renderSummary } from './panel.js';
import { esc } from './provenance.js';
import { pftColor, toast, updateHover } from './pick.js';
import { renderZoomBox } from './zoom.js';
import { turnTo } from './highlights.js';
import { hasLayer, setFrame } from './load.js';
import { stop } from './playback.js';
// ------------------------------------------------------------ colours
function ramp(stops) {
  const cs = stops.map(([v, c]) => [v, new THREE.Color(c)]);
  return (v, out) => {
    if (v <= cs[0][0]) return out.copy(cs[0][1]);
    for (let i = 1; i < cs.length; i++) {
      if (v <= cs[i][0]) {
        const t = (v - cs[i - 1][0]) / (cs[i][0] - cs[i - 1][0]);
        return out.copy(cs[i - 1][1]).lerp(cs[i][1], t);
      }
    }
    return out.copy(cs[cs.length - 1][1]);
  };
}
export const RAMPS = {
  elevation: [[-8000, '#0a1a36'], [-4000, '#153766'], [-1000, '#2d68a3'], [-1, '#6aa7d8'],
              [0, '#3f7d3f'], [300, '#6f9a4b'], [1000, '#c4b56c'], [2000, '#a37a4a'],
              [3500, '#7d6656'], [5000, '#e6e2dc'], [8000, '#ffffff']],
  temperature: [[-30, '#2b3f99'], [-10, '#5b8fd6'], [0, '#e6f0f5'], [12, '#f4d27a'], [24, '#e2703a'], [32, '#9e1c1c']],
  precipitation: [[0, '#d9c49a'], [300, '#c9c27a'], [800, '#7fb35a'], [1600, '#2f8f5a'], [2500, '#1f6f8f'], [4000, '#203f8f']],
  'crust age': [[0, '#d7301f'], [15, '#fc8d59'], [40, '#fee08b'], [80, '#91bfdb'], [140, '#4575b4'], [200, '#313695']],
  'crust thickness': [[0, '#08306b'], [8, '#2171b5'], [20, '#9ecae1'], [30, '#c7e9c0'], [38, '#74c476'],
                      [50, '#fd8d3c'], [65, '#d94801'], [80, '#7f2704']],
  sediment: [[0, '#3a3a3a'], [0.5, '#7d6b4f'], [2, '#c9a464'], [6, '#f0d58c'], [15, '#fff7dc']],
};
RAMPS['rock age'] = [[0, '#f2e6d0'], [300, '#d9b98c'], [1000, '#a87d5a'], [2000, '#6e4f3a'], [3500, '#3a2a22']];
RAMPS.rainfall = RAMPS.precipitation;
RAMPS['wave power'] = [[0, '#1d2f55'], [5, '#2f6f8f'], [15, '#4fae9b'], [30, '#b8d66b'], [60, '#f2c14e'], [100, '#e8603c']];  // kW/m
RAMPS['tide range'] = [[0, '#1d2f55'], [0.5, '#2c5d8a'], [1.5, '#3f9bb0'], [3, '#8fd19e'], [6, '#f0d36b'], [10, '#e8603c']];  // m
// the rivers' year (worlds, PW-028): the peak month's flow over the mean month's (1 = steady)
RAMPS['river floods'] = [[1, '#2f5f8f'], [1.5, '#4f9fb0'], [2, '#9fd0a0'], [3, '#f0d36b'], [4.5, '#ef8a3a'], [7, '#b8283a']];
// the glacial imprint of a time zoom (PW-037): m of bed the ice eroded, m of till and moraine it dropped
RAMPS['glacial erosion'] = [[0, '#f4f1ea'], [5, '#e9d9b8'], [30, '#e0a96d'], [100, '#cc6b3d'], [300, '#9c2f2a'], [1000, '#4a1020']];
RAMPS['glacial outwash'] = [[0, '#f4f1ea'], [1, '#f1e3b5'], [5, '#e0c26a'], [15, '#c99a2e'], [40, '#8a5a12']];
RAMPS['glacial loess'] = [[0, '#f4f1ea'], [0.5, '#f3e9c0'], [2, '#e8cf7a'], [6, '#d1a63a'], [15, '#9a6b14']];
RAMPS['glacial till'] = [[0, '#f4f1ea'], [5, '#dfe8c8'], [20, '#a9cc86'], [60, '#5fa05a'], [150, '#2f6f45'], [400, '#123f2a']];
RAMPS['bed under ice'] = RAMPS.elevation;  // (runs, time zooms: the bed pressed down by the ice, PW-189)
RAMPS['ice thickness'] = [[0, '#f4f8fb'], [500, '#cfe3f2'], [1500, '#94bde0'], [2500, '#5d8fcb'], [3500, '#3b5fae'], [4500, '#2b2f7a']];
// the sea and the air's moisture (worlds): sea-surface temperature (C), salinity (psu), relative humidity (%), dew point (C)
RAMPS['sea temperature'] = [[-2, '#3b3a8f'], [4, '#3f74c0'], [10, '#5fb6c8'], [16, '#bfe3b0'], [21, '#f2d77a'], [26, '#ef8f45'], [30, '#b8282a']];
RAMPS.salinity = [[31, '#3b2a78'], [33, '#3f6fb5'], [34.2, '#8fc3d8'], [34.9, '#e9eee6'], [35.8, '#f0c870'], [37, '#d9783a'], [39, '#9e2a1e']];
// coastal life (worlds, coastal.py, PW-188): river mud in the sea (mg/L, log-like stops) and upwelling (C of cooling)
RAMPS.turbidity = [[0, '#0f3a5f'], [1, '#2f6f8f'], [3, '#6fa88a'], [10, '#c9b26a'], [30, '#a8743a'], [100, '#6b4424']];
RAMPS.upwelling = [[0, '#1d2f55'], [0.5, '#2f5f8f'], [1.5, '#3f9bb0'], [3, '#8fd19e'], [6, '#f0d36b'], [10, '#e8603c']];
RAMPS.humidity = [[15, '#b98a4f'], [35, '#e3cf94'], [55, '#d9e7c4'], [70, '#7fc3b0'], [82, '#3f8fb0'], [95, '#244f8f']];
RAMPS['dew point'] = [[-25, '#5b4f9a'], [-5, '#9fb0d0'], [5, '#d8e6e0'], [12, '#b9dc8a'], [17, '#f2d55e'], [21, '#ef8a3a'], [25, '#b8283a']];
// the sky (worlds): cloud cover (% of the sky) and bright sunshine (hours a day)
RAMPS.cloud = [[0, '#f2c14e'], [20, '#efe0a6'], [40, '#d3dade'], [60, '#a3b1bf'], [80, '#6f7f93'], [100, '#454e5e']];
RAMPS.sunshine = [[0, '#2e3348'], [2, '#4d5674'], [4, '#8a93a6'], [6, '#d3d3c0'], [8, '#efd98a'], [10, '#f3b33d'], [12, '#e57a22'], [14, '#c4461a']];
// model minus observed (Earth reference world): temperature in C, rainfall as log2 of the ratio
RAMPS['temperature difference'] = [[-10, '#2b5fb3'], [-5, '#7fa8de'], [-1, '#eef1f4'], [1, '#eef1f4'], [5, '#e8956b'], [10, '#b2262b']];
RAMPS['rainfall ratio'] = [[-2, '#a6611a'], [-1, '#dfc27d'], [-0.2, '#f0ece2'], [0.2, '#f0ece2'], [1, '#80cdc1'], [2, '#018571']];
RAMPS['sunshine difference'] = [[-4, '#4d5674'], [-2, '#a3b1bf'], [-0.5, '#f0ece2'], [0.5, '#f0ece2'], [2, '#efd98a'], [4, '#e57a22']];
// vegetation (worlds; tree cover and NPP also in runs)
RAMPS['tree cover'] = [[0, '#e8dcb0'], [10, '#cdd28a'], [30, '#8fb85f'], [60, '#3f8f3f'], [90, '#1f5a2a']];
RAMPS['body'] = [[0, '#ece6d6'], [25, '#e6c98a'], [50, '#d8a24a'], [75, '#b9712a'], [100, '#7a3b14']];  // (peoples runs: a body trait as a share of the cell's people, PW-701)
RAMPS['plant cover'] =[[0, '#efe0b0'], [25, '#d8cf8a'], [50, '#a9c46a'], [75, '#5f9f4a'], [100, '#2f6f3a']];
RAMPS['canopy height'] = [[0, '#efe6c8'], [2, '#c9cf8a'], [8, '#8fb85f'], [20, '#4f8f45'], [35, '#2a6a3a'], [50, '#123f2a']];
RAMPS['leaf area'] = [[0, '#efe6c8'], [1, '#cfd28a'], [2.5, '#8fbf5a'], [4, '#4f9a45'], [6, '#1f6a32']];
RAMPS.NPP = [[0, '#f2ead0'], [100, '#e3d28a'], [300, '#b9c85f'], [600, '#6faf45'], [900, '#2f8a3a'], [1300, '#0f5a2a']];
RAMPS.biomass = [[0, '#f2ead0'], [10, '#d8d28a'], [50, '#9cc060'], [120, '#4f9a45'], [250, '#1f6a32'], [400, '#0a3f22']];
RAMPS['fire return'] = [[0, '#3a2a2a'], [1, '#e8503a'], [3, '#f09a3a'], [10, '#f2d36a'], [50, '#c9d6a0'], [300, '#8fb0a0'], [3000, '#4f6f80']];
RAMPS['stand age'] = [[0, '#f2d36a'], [20, '#c9cf8a'], [80, '#7fb05a'], [200, '#3f8a45'], [600, '#1f5a3a'], [2000, '#0f3a2a']];
RAMPS['plant type'] = [[0, '#2a2a2a'], [100, '#ffffff']];  // (drawn in the PFT's own colour)
// soils (worlds; soils.py, PW-185)
RAMPS['soil depth'] = [[0, '#8a7f6e'], [0.25, '#c9b48a'], [0.75, '#d9c27a'], [1.5, '#a8743f'], [3, '#5a3a22']];
RAMPS['soil water'] = [[0, '#efe0b0'], [50, '#d9cf8a'], [120, '#9cc07a'], [200, '#4f9fa0'], [350, '#1f5f8a']];
RAMPS.fertility = [[0, '#d8c8a8'], [0.25, '#c9a86a'], [0.5, '#a9b85a'], [0.75, '#5f9f3a'], [1, '#1f5f22']];
RAMPS['soil carbon'] = [[0, '#efe6c8'], [3, '#d6c28a'], [8, '#a8844f'], [15, '#6a4a2a'], [30, '#3a2a1a'], [60, '#1a120a']];
RAMPS.peat = [[0, '#efe6c8'], [0.3, '#b9a57a'], [1, '#7a5a3a'], [3, '#3a2a1a'], [8, '#120a05']];
RAMPS.permafrost = [[0, '#e8dcc0'], [1, '#bcd0dc'], [2, '#7fa8c8'], [3, '#3a6a9a']];
RAMPS.loess = [[0, '#ece6d6'], [1, '#e6d49a'], [5, '#d9b45a'], [20, '#b5852f'], [60, '#7a5418']];
export const SOIL_LAYERS = { 'soil depth': 'soil_depth', 'soil water': 'soil_water', fertility: 'soil_fertility',
                      'soil carbon': 'soil_carbon', peat: 'peat_depth', permafrost: 'permafrost', loess: 'loess' };
// game attributes of the plants and soils (gameattrs.py, PW-206): ramps on land; the month masks as month counts
const SCORE5 = [[0, '#efe6c8'], [1, '#e0cf8a'], [2, '#b9c260'], [3, '#7aa848'], [4, '#3f8a3a'], [5, '#1a5a2a']];
RAMPS.travel = [[1, '#f2ead0'], [1.5, '#e8d38a'], [2, '#e0a85a'], [3, '#c9703a'], [5, '#9a3a2a'], [8, '#5a1a1a']];
RAMPS.sightline = [[15, '#1a3a22'], [50, '#3f7a3a'], [150, '#8fb05a'], [500, '#d9cf8a'], [5000, '#f5efdc']];
RAMPS.grazing = SCORE5; RAMPS.foraging = SCORE5; RAMPS.timber = SCORE5;
RAMPS.fuel = [[0, '#efe6c8'], [1, '#e8cf8a'], [2, '#d9a65a'], [3, '#b8743a'], [4, '#8a4a2a'], [5, '#4a2a1a']];
RAMPS['building ground'] = [[0, '#6a3a3a'], [1, '#a8603f'], [2, '#d9a65a'], [3, '#e3d28a'], [4, '#b5c9a0'], [5, '#7f9fb0']];
RAMPS['mud season'] = [[0, '#efe6c8'], [2, '#d9c08a'], [4, '#a8844f'], [7, '#6a4a2a'], [12, '#3a2a1a']];
RAMPS['fire season'] = [[0, '#dfe6d8'], [1, '#f2d36a'], [3, '#f09a3a'], [6, '#e8503a'], [9, '#8a2a2a']];
RAMPS['green season'] = [[0, '#c9b38a'], [3, '#d9cf8a'], [6, '#a9c26a'], [9, '#5f9f45'], [12, '#1f6a32']];
export const GAME_LAYERS = { travel: 'travel', sightline: 'sightline', grazing: 'grazing', foraging: 'foraging', timber: 'timber',
                      fuel: 'fuel', 'building ground': 'building', 'mud season': 'mud_months', 'fire season': 'fire_months',
                      'green season': 'green_months' };
const bits = (m) => { let n = 0; for (let k = 0; k < 12; k++) n += (m >> k) & 1; return n; };
const GAME_MASKS = new Set(['fire season', 'green season']);
// month ranges of a 12-bit mask ("Jun–Sep, Dec"; "all year"), runs wrapping round the year
export function monthRuns(m) {
  const M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], on = (k) => (m >> ((k + 12) % 12)) & 1;
  if (bits(m) === 12) return 'all year';
  if (!m) return '';
  let s = 0; while (on(s) && s < 12) s++;  // (start after an off month, so a run across December stays one)
  const out = [];
  for (let k = s; k < s + 12; k++) if (on(k) && !on(k - 1)) { let e = k; while (on(e + 1)) e++; out.push(e > k ? `${M[k % 12]}–${M[e % 12]}` : M[k % 12]); }
  return out.join(', ');
}
// human use (humanuse.py, PW-099/505): class maps coloured from the legend (legend.human_use); the first three also
// draw ribbons / markers (overlays huRivers, huHarbours, huPasses), which a layer of the same name switches on by itself
export const HU_LAYERS = { 'navigable rivers': 'river_nav', harbours: 'harbour', passes: 'pass', farmland: 'fertile', 'fresh water': 'fresh_water' };
export const HU_OVERLAY = { river_nav: 'huRivers', harbour: 'huHarbours', pass: 'huPasses' };
const huOn = (k) => $(HU_OVERLAY[k]).checked || HU_LAYERS[state.layer] === k;
function huCols(k) {  // legend colours as THREE.Colors (null: the legend's transparent "nothing" class)
  S.V.huCols ??= {};
  return (S.V.huCols[k] ??= (S.V.humanUse?.[k] || []).map((e) => (e.color.length > 7 ? null : new THREE.Color(e.color))));
}
function huColor(layer, i, c) {
  const k = HU_LAYERS[layer], land = S.V.layers.elevation[i] > 0, col = huCols(k)[S.V.layers[k][i]];
  // (rivers are drawn as ribbons over plain ground: a filled cell would make every small river look like a plain)
  if (col && k !== 'river_nav' && (k === 'harbour' ? !land : land)) c.copy(col); else c.copy(land ? BARE : OCEAN);
  if (k === 'river_nav' && land) c.multiplyScalar(0.7);  // (darker ground, so the ribbons stand out)
}
// resources (resources.py, PW-155): 'resources' = the most likely metal/gem/energy/salt resource per cell (faded by
// its likelihood), 'resource' = one resource's likelihood (picker resSel, ?res=), 'building stone' = the best stone
export const RES_LAYERS = new Set(['resources', 'resource', 'building stone']);
state.res = 'porphyry_cu';
export function resInfo(key) { return S.V.resLeg?.resources.find((r) => r.key === key); }
function resColor(layer, i, c) {
  const L = S.V.layers, land = L.elevation[i] > 0 || (L.ice && L.ice[i] > 0);
  if (layer === 'building stone') {
    const e = S.V.resLeg.stone[L.stone[i]];
    if (land && e && L.stone[i]) c.set(e.color); else c.copy(land ? BARE : OCEAN);
    return;
  }
  const base = land ? BARE : OCEAN;
  if (layer === 'resources') {
    const id = L.resource[i], r = id ? S.V.resLeg.resources[id - 1] : null;
    if (!r) { c.copy(base); return; }
    const v = (L['res_' + r.key]?.[i] || 0);
    c.copy(base).lerp(new THREE.Color(r.color), 0.35 + 0.65 * Math.min(1, v));
    return;
  }
  const r = resInfo(state.res), v = r ? (L['res_' + r.key]?.[i] || 0) : 0;
  c.copy(base).multiplyScalar(0.8).lerp(new THREE.Color(r?.color || '#fff'), Math.sqrt(Math.min(1, v)));
}
// coast form (coastform.py, PW-097): 'coasts' = each coastal land cell's class (legend.coast); the scores 0-1
// (barrier islands, cliffs, seabird and seal colonies on the coast's land, hazards to ships at sea)
export const COAST_SCORES = { 'barrier islands': 'barrier', cliffs: 'cliff', seabirds: 'seabirds', seals: 'seals', 'sea hazards': 'nav_hazard' };
export const COAST_LAYERS = new Set(['coasts', ...Object.keys(COAST_SCORES)]);
const COAST_RAMP = ramp([[0, '#3a4250'], [0.25, '#3f7f9f'], [0.5, '#8fc89a'], [0.75, '#f2c45a'], [1, '#e8503c']]);
function coastColor(layer, i, c) {
  const L = S.V.layers, land = L.elevation[i] > 0 || (L.ice && L.ice[i] > 0);
  if (layer === 'coasts') {
    const e = S.V.coastLeg?.[L.coast_type[i]];
    if (e && e.id > 0) c.set(e.color.slice(0, 7));
    else { c.copy(land ? BARE : OCEAN); if (land) c.multiplyScalar(0.6); }
    return;
  }
  const k = COAST_SCORES[layer], v = L[k][i];
  if (land === (k === 'nav_hazard') || v <= 0) { c.copy(land ? BARE : OCEAN); if (land) c.multiplyScalar(0.6); return; }
  COAST_RAMP(v, c);
}
export function coastLegend(layer, sw) {
  const L = S.V.layers, km = Math.sqrt(4 * Math.PI * 6371 ** 2 / S.V.n);  // (one cell width of coast per coastal cell)
  if (layer === 'coasts') {
    const cnt = new Map();
    for (let i = 0; i < S.V.n; i++) if (L.coast_type[i]) cnt.set(L.coast_type[i], (cnt.get(L.coast_type[i]) || 0) + 1);
    return [...cnt.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => S.V.coastLeg[id])
      .map((e) => `<span title="${esc(e.about)}">${sw(e.color.slice(0, 7), `${esc(e.name)} ${Math.round(cnt.get(e.id) * km / 1000).toLocaleString()}k km`)}</span>`).join('') +
      '<span class="muted">(the coast form of each coastal land cell, km of coastline; hover a class for what it means, a cell for its scores)</span>';
  }
  const about = { barrier: 'low coast, gentle shelf, waves, small tides, sand', cliff: 'high or hard land under strong waves',
                  seabirds: 'food in the water (upwelling, cool or tidally mixed seas) x nesting cliffs or predator-free islands',
                  seals: 'food in cool water x rocky shores, island beaches or sea ice to haul out on',
                  nav_hazard: 'reefs, shallow banks off the coast, sea ice much of the year' }[COAST_SCORES[layer]];
  return [0.25, 0.5, 0.75, 1].map((v) => { const c = new THREE.Color(); COAST_RAMP(v, c); return sw('#' + c.getHexString(), v.toFixed(2)); }).join('') +
    `<span class="muted">(likelihood 0-1: ${about}; coastform.py)</span>`;
}
export function coastText(i) {
  const L = S.V.layers, e = S.V.coastLeg?.[L.coast_type[i]];
  if (!e || !e.id) return '';
  const extra = [['barrier', 'barrier'], ['cliff', 'cliffs'], ['seabirds', 'seabirds'], ['seals', 'seals']]
    .filter(([k]) => L[k] && L[k][i] >= 0.3).map(([k, n]) => `${n} ${L[k][i].toFixed(2)}`);
  return e.name + (extra.length ? ` (${extra.join(', ')})` : '');
}

export function resLegend(layer, sw) {
  const L = S.V.layers, R = S.V.resLeg;
  if (layer === 'building stone') {
    const present = new Set(L.stone);
    return R.stone.filter((e) => e.id && present.has(e.id)).map((e) => sw(e.color, e.name)).join('') +
      '<span class="muted">(the best stone exposed: rock at the surface, hardness; folded limestone = marble, folded shale = slate)</span>';
  }
  if (layer === 'resources') {
    const cnt = new Map();
    for (let i = 0; i < S.V.n; i++) if (L.resource[i]) cnt.set(L.resource[i], (cnt.get(L.resource[i]) || 0) + 1);
    return [...cnt.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => R.resources[id - 1])
      .map((r) => `<span title="${esc(r.model)}">${sw(r.color, esc(r.name))}</span>`).join('') +
      '<span class="muted">(the most likely resource per cell, brighter = likelier; coarse likelihoods from the run\'s history, not surveyed deposits; hover for the top three)</span>';
  }
  const r = resInfo(state.res);
  return `<div><div class="grad" style="background:linear-gradient(90deg,#55524c,${r?.color || '#fff'})"></div>
    <div class="row" style="justify-content:space-between;width:260px"><span>0</span><span class="muted">likelihood</span><span>1</span></div></div>
    <span>${r ? esc(r.name) : '?'}</span><span class="muted">(${r ? esc(r.model) : ''})</span>`;
}
export function resRows(L, i, land, R) {
  if (!L.resource || !S.V.resLeg) return;
  const top = S.V.resLeg.resources.map((r) => [r, L['res_' + r.key]?.[i] || 0]).filter(([, v]) => v >= 0.15)
    .sort((a, b) => b[1] - a[1]);
  const real = top.filter(([r]) => r.group !== 'fantasy').slice(0, 3), fan = top.filter(([r]) => r.group === 'fantasy');
  if (real.length) R('ground', 'resources', real.map(([r, v]) => `${r.name} ${v.toFixed(2)}` +
    (r.key === 'coal' && L.coal_rank?.[i] ? ` (${['', 'lignite', 'bituminous', 'anthracite'][L.coal_rank[i]]})` : '')).join(' · ') +
    (L.resource[i] && L.res_depth ? `; the first at ~${Math.round(L.res_depth[i])} m` : ''), { sep: ': ', ess: true });
  if (fan.length) R('ground', 'fantasy', fan.map(([r, v]) => `${r.name} ${v.toFixed(2)}`).join(' · '), { sep: ': ' });
  if (land && L.stone && L.stone[i]) R('ground', 'building stone', S.V.resLeg.stone[L.stone[i]].name, { sep: ': ' });
}
export function fillRes() {
  if (!S.V?.resLeg) return;
  if (!resInfo(state.res)) state.res = S.V.resLeg.resources[0].key;
  const groups = [...new Set(S.V.resLeg.resources.map((r) => r.group))];
  $('resSel').innerHTML = groups.map((g) => `<optgroup label="${g}">` + S.V.resLeg.resources.filter((r) => r.group === g)
    .map((r) => `<option value="${r.key}" title="${esc(r.model)}"${r.key === state.res ? ' selected' : ''}>${esc(r.name)}</option>`).join('') + '</optgroup>').join('');
}
$('resSel').addEventListener('change', () => {
  state.res = $('resSel').value;
  const u = new URL(location); u.searchParams.set('res', state.res); history.replaceState(null, '', u);
  paint(); updateHover();
});
const HU_TEXT = { river_nav: 'navigable rivers: what floats on them', harbour: 'harbours: shelter and depth at the coast',
                  pass: 'mountain passes: how long they are open', fertile: 'farmland', fresh_water: 'fresh water within reach' };
export function huSwatches(k) {
  const sw = (e) => `<span><span class="sw" style="background:${e.color}"></span>${e.name}</span>`;
  return `<span><b class="muted" style="font-weight:600">${HU_TEXT[k]}:</b></span>` +
    (S.V.humanUse[k] || []).filter((e) => e.color.length <= 7 && !(e.id === 0 && HU_OVERLAY[k])).map(sw).join('');
}
// ribbons and markers of the human-use layers as cell data (once per world); the globe and the 2D map draw them
function huFeatures() {
  if (S.V.huFeat) return S.V.huFeat;
  const L = S.V.layers, f = { rivers: [], harbours: [], passes: [] };
  for (let i = 0; i < S.V.n; i++) {
    const d = L.downstream ? L.downstream[i] : -1;
    if (L.river_nav && L.river_nav[i] > 0 && d >= 0 && L.elevation[i] > 0) f.rivers.push({ a: i, b: d, cls: L.river_nav[i] });
    if (L.harbour && L.harbour[i] > 0 && L.elevation[i] <= 0) f.harbours.push({ i, cls: L.harbour[i] });
    if (L.pass && L.pass[i] > 0) f.passes.push({ i, cls: L.pass[i] });
  }
  return (S.V.huFeat = f);
}
const HU_RIVER_W = [0, 1.3, 2.6, 4.2], HU_HARBOUR_S = [0, 0.5, 0.8, 1.1];  // ribbon width (px), marker half-size (degrees)
// the globe's overlays (fat lines per class, in the legend's colours)
export function huOverlays(globe, wraps) {
  const out = {}, f = huFeatures(), L = S.V.layers, G = S.V.grid;
  if (L.river_nav && huOn('river_nav')) {
    const pos = cellPositions(1.004), by = [[], [], [], []];
    for (const { a, b, cls } of f.rivers) {
      if (!globe && Math.abs(pos[3 * a] - pos[3 * b]) > 2) continue;
      by[cls].push(pos[3 * a], pos[3 * a + 1], pos[3 * a + 2], pos[3 * b], pos[3 * b + 1], pos[3 * b + 2]);
    }
    for (let c = 1; c <= 3; c++) out['huRiv' + c] = ribbonObj(by[c], huCols('river_nav')[c], c === 1 ? 0.8 : 1, HU_RIVER_W[c]);
  }
  const r0 = globe ? 1.012 : 1;
  const shape = (pts, la, lo, s, kind) => {
    const cl = Math.max(Math.cos(la * Math.PI / 180), 0.2), dl = s / cl;
    const P = kind === 'hourglass'
      ? [[la + s, lo - dl], [la + s, lo + dl], [la - s, lo - dl], [la - s, lo + dl]]
      : [[la + s, lo], [la, lo + dl], [la - s, lo], [la, lo - dl]];
    const q = P.map(([a, b]) => llPos(a, b, r0));
    for (let k = 0; k < 4; k++) if (!wraps(q[k], q[(k + 1) % 4])) pts.push(...q[k], ...q[(k + 1) % 4]);
  };
  if (L.harbour && huOn('harbour')) {
    const by = [[], [], [], []];
    for (const { i, cls } of f.harbours) if (cls > 1 || HU_LAYERS[state.layer] === 'harbour') shape(by[cls], G.lat[i], G.lon[i], HU_HARBOUR_S[cls], 'diamond');
    for (let c = 1; c <= 3; c++) out['huHar' + c] = ribbonObj(by[c], huCols('harbour')[c], 1, 2);
  }
  if (L.pass && huOn('pass')) {
    const by = [[], [], [], []];
    for (const { i, cls } of f.passes) shape(by[cls], G.lat[i], G.lon[i], 0.8, 'hourglass');
    for (let c = 1; c <= 3; c++) out['huPass' + c] = ribbonObj(by[c], huCols('pass')[c], 1, 2);
  }
  return out;
}
// the same for the 2D map (projmap.drawFeatures)
export function huMapFeatures() {
  if (!S.V.humanUse?.river_nav) return null;
  const f = huFeatures(), G = S.V.grid, L = S.V.layers, feats = { lines: [], marks: [] };
  const col = (k, c) => '#' + huCols(k)[c].getHexString(THREE.SRGBColorSpace);
  if (L.river_nav && huOn('river_nav'))
    for (const { a, b, cls } of f.rivers) {
      let dl = G.lon[b] - G.lon[a]; dl -= 360 * Math.round(dl / 360);
      feats.lines.push({ pts: [[G.lat[a], G.lon[a]], [G.lat[b], G.lon[a] + dl]], color: col('river_nav', cls), width: HU_RIVER_W[cls] });
    }
  if (L.harbour && huOn('harbour'))
    for (const { i, cls } of f.harbours) if (cls > 1 || HU_LAYERS[state.layer] === 'harbour') feats.marks.push({ lat: G.lat[i], lon: G.lon[i], shape: 'diamond', color: col('harbour', cls), size: 2.5 + 2 * cls });
  if (L.pass && huOn('pass'))
    for (const { i, cls } of f.passes) feats.marks.push({ lat: G.lat[i], lon: G.lon[i], shape: 'hourglass', color: col('pass', cls), size: 5 });
  return feats;
}
export const VEG_LAYERS = { 'tree cover': 'tree_cover', 'plant cover': 'plant_cover', 'canopy height': 'canopy_height',
                     NPP: 'npp', biomass: 'biomass', 'fire return': 'fire_return', 'stand age': 'stand_age' };
export const VEG_VIEWS = new Set(['vegetation', 'plant type', 'leaf area', ...Object.keys(VEG_LAYERS)]);
export const UNITS = { elevation: 'm', temperature: '°C mean annual', precipitation: 'mm/yr', rainfall: 'mm/yr',
                'crust age': 'Myr (sea floor)', 'crust thickness': 'km of crust', sediment: 'km of sediment on top',
                'ice thickness': 'm of land ice (bare land grey)', 'glacial erosion': 'm of bed the ice has eroded so far (time zoom)',
                'glacial till': 'm of till and moraine the ice has dropped so far (time zoom)', 'glacial outwash': 'm of outwash (sandur) the meltwater has laid down so far (time zoom)', 'glacial loess': 'm of loess the wind has laid down so far (time zoom)', 'bed under ice': 'm, the ground with the ice taken off (pressed down by its load; ice faintly outlined)', 'temperature difference': '°C, model minus observed',
                'navigable rivers': 'class: 1 small boats, 2 barges, 3 sea-going', harbours: 'class: 1 anchorage, 2 harbour, 3 fine harbour',
                passes: 'class: open most of the year, seasonal, snow-bound', farmland: 'class: 0 not arable .. 4 prime',
                'fresh water': 'class: 0 none .. 3 on site',
                'river floods': "x: the rivers' peak month over their mean month (1 = steady; Arctic spring floods 3-5); grey: frozen half the year or more",
                'wave power': 'kW/m of wave crest, mean (at sea)', 'tide range': 'm, tidal range (at sea)',
                'sea temperature': '°C sea surface, year', salinity: 'psu at the sea surface (mean 34.7)',
                humidity: '% rel. humidity, year', 'dew point': '°C dew point, year',
                cloud: '% cloud cover, year', sunshine: 'hours of bright sunshine a day, year',
                'tree cover': '% tree canopy cover', 'plant cover': '% of the ground shaded by plants',
                'canopy height': 'm, tallest layer', 'leaf area': 'm² of leaf per m² (LAI), year',
                NPP: 'g C/m²/yr net primary productivity', biomass: 't C/ha in living plants',
                'fire return': 'years between fires (log scale; dark = never)', 'stand age': 'years since the last stand-replacing fire',
                'plant type': '% cover of the plant type',
                'soil depth': 'm of rootable soil', 'soil water': 'mm of water the soil holds for plants',
                fertility: 'soil fertility, 0 poor to 1 rich', 'soil carbon': 'kg C/m² in the top metre',
                peat: 'm of peat where peat lies', permafrost: '0 none, 1 sporadic, 2 discontinuous, 3 continuous',
                loess: 'm of wind-blown silt',
                travel: "x the time of walking open level ground (snow-free, off roads)", sightline: 'm you can see at eye level (log scale)',
                grazing: '0-5 pasture for herds', foraging: '0-5 wild food for people', timber: '0-5 building timber',
                fuel: '0-5 firewood and fuel', 'building ground': '0-5: 0 peat or swelling clay .. 5 firm, dry rock',
                'mud season': 'months the ground is mud', 'fire season': 'fire-weather months (where it burns)',
                'green season': 'months the plants are in leaf and snow-free',
                turbidity: 'mg/L of river mud at the sea surface (clear sea ~0.5; reefs need under ~10)',
                upwelling: '°C the sea surface is cooled by upwelling (nutrients for kelp and fisheries)',
                'coastal life': '% of the cell: the biggest habitat\'s colour, stronger = more' };
// coastal life (coastal.py): layer, name, colour (as zoom_coastal.LIFE), sea or land
export const COASTAL = [['reef', 'coral reef', '#ff6fa8'], ['kelp', 'kelp forest', '#9a7b2a'], ['seagrass', 'seagrass meadow', '#3fbf6a'],
                 ['mangrove', 'mangrove', '#14d2b0'], ['salt_marsh', 'salt marsh', '#e3d65a']];
const COASTAL_COLS = Object.fromEntries(COASTAL.map(([k, , c]) => [k, new THREE.Color(c)]));
// the habitat with the biggest share of cell i (and the share, %), or null
function coastalTop(i) {
  let best = null, v = 0;
  for (const [k] of COASTAL) { const x = S.V.layers[k]?.[i] || 0; if (x > v) { v = x; best = k; } }
  return best && v >= 0.5 ? [best, v] : null;
}
// the habitats covering at least 0.5% of cell i, as text ("coral reef 12%, seagrass 30%"), or ''
export function coastalText(i) {
  const L = S.V.layers;
  return COASTAL.filter(([k]) => (L[k]?.[i] || 0) >= 0.5)
    .map(([k, n]) => `${n} ${L[k][i] < 10 ? L[k][i].toFixed(1) : Math.round(L[k][i])}%`).join(', ');
}
const rampFns = Object.fromEntries(Object.entries(RAMPS).map(([k, v]) => [k, ramp(v)]));
const OCEAN = new THREE.Color('#1c2f4f'), CONT = new THREE.Color('#8a8478');
const RED = new THREE.Color('#ff3b3b'), CYAN = new THREE.Color('#3bf0ff'), ICE = new THREE.Color('#f4f8fb');
const BARE = new THREE.Color('#6b675f'), NODATA = new THREE.Color('#4a4f57');

function plateColor(id, continental, out) {
  return out.setHSL((id * 0.618034) % 1, 0.55, continental ? 0.55 : 0.32);
}

// Earth reference world: temperature, precipitation and climate exist as our
// model's and as observed (obs_* layers). state.obs picks which to colour by:
// 'model', 'obs', or 'diff' (model minus observed). Returns null when the
// layer on screen has no observed counterpart.
export const OBS_LAYERS = { temperature: 'obs_temperature', precipitation: 'obs_precipitation', climate: 'obs_climate',
                     sunshine: 'obs_sunshine' };
export function obsView(layer) {
  if (!S.V || S.V.kind !== 'world' || !OBS_LAYERS[layer] || !S.V.layers[OBS_LAYERS[layer]] || state.obs === 'model') return null;
  return { layer, model: S.V.layers[layer], obs: S.V.layers[OBS_LAYERS[layer]], diff: state.obs === 'diff' };
}
// Seasons (PW-126): worlds store July and January temperature and rain
// (temperature_jul, precipitation_jan, ...). state.season ('' = the year,
// 'jul', 'jan') is shared by the colour layers and the winds' picker (?season=).
export const SEASONAL = { temperature: 'temperature', precipitation: 'precipitation', rainfall: 'precipitation',
                   'sea temperature': 'sst', humidity: 'humidity', 'dew point': 'dewpoint', cloud: 'cloud',
                   sunshine: 'sunshine', 'leaf area': 'lai', satellite: 'sat' };
export const SEASON_NAMES = { jul: 'July', jan: 'January' };
state.season = '';
// the season the colour layer shows: '' (the year, or no seasonal layer here), 'jul' or 'jan'
function colourSeason(layer = state.layer) {
  const k = SEASONAL[layer];
  return k && state.season && S.V?.layers?.[`${k}_${state.season}`] && !obsView(layer) ? state.season : '';
}
// the values a seasonal colour layer draws (annual or seasonal), else null
export function seasonalData(layer) {
  const k = SEASONAL[layer], s = k && colourSeason(layer);
  return k ? S.V.layers[s ? `${k}_${s}` : k] : null;
}
export function seasonUnits(layer) {
  const s = colourSeason(layer);
  if (layer === 'satellite') return s ? `true colour in ${SEASON_NAMES[s]}` : "true colour, each hemisphere's summer (July north, January south)";
  if (!s) return UNITS[layer];
  const half = s === 'jul' ? 'Apr–Sep' : 'Oct–Mar';
  return { temperature: `°C, ${SEASON_NAMES[s]} mean`, sst: `°C sea surface, ${SEASON_NAMES[s]}`, lai: `m² of leaf per m² (LAI), ${half}`,
           humidity: `% rel. humidity, ${half}`, dewpoint: `°C dew point, ${half}`, cloud: `% cloud cover, ${half}`,
           sunshine: `hours of bright sunshine a day, ${half}` }[SEASONAL[layer]]
    || `mm/yr, ${half} rate`;
}
export function setSeason(s) {
  state.season = s in SEASON_NAMES ? s : '';
  $('windSeason').value = $('layerSeason').value = state.season;
  const u = new URL(location);
  if (state.season) u.searchParams.set('season', state.season); else u.searchParams.delete('season');
  history.replaceState(null, '', u);
}
const koppenGroup = (id) => S.V.koppen[id]?.code[0];  // A tropical, B dry, C temperate, D continental, E polar

function obsColor(ov, i, c) {
  const m = ov.model[i], o = ov.obs[i];
  if (S.V.layers.elevation[i] <= 0) return c.copy(OCEAN);
  if (o == null || (ov.layer === 'climate' && o < 0)) return c.copy(NODATA);  // no observation here
  if (!ov.diff) return ov.layer === 'climate' ? c.set(S.V.koppenColors[o]) : rampFns[ov.layer](o, c);
  if (ov.layer === 'temperature') return rampFns['temperature difference'](m - o, c);
  if (ov.layer === 'precipitation') return rampFns['rainfall ratio'](Math.log2((m + 50) / (o + 50)), c);  // +50: deserts
  if (ov.layer === 'sunshine') return rampFns['sunshine difference'](m - o, c);
  return c.set(m === o ? '#3fae5a' : koppenGroup(m) === koppenGroup(o) ? '#e8c547' : '#d0453a');
}

// Lakes, drawn the same way for runs and worlds. lake_kind (hydrology): 0 none,
// 1 open (fresh: it spills, its river flows on), 2 closed (salty: evaporation
// balances the inflow), 3 salt pan (a closed basin's dry floor). Depth: a run
// frame stores lake_depth, a world lake_level (its surface; minus elevation =
// depth); a world from before lake_kind has only lake (0/1, drawn as fresh).
// (fresh: a bright cyan, apart from the sea's blues; salt: pink, as brine
// shrimp and algae colour real salt lakes, apart from the greens and blues)
export const LAKE_KINDS = { 1: ['fresh lake', '#38c8f0'], 2: ['salt lake', '#e58fbf'], 3: ['salt pan', '#efe8d8'] };
const LAKE_COLS = Object.fromEntries(Object.entries(LAKE_KINDS).map(([k, [, c]]) => [k, new THREE.Color(c)]));
const DEEP_LAKE = { 1: new THREE.Color('#137fb0'), 2: new THREE.Color('#a8508a') };  // (deep water stays its kind's hue)
// the colour layers lakes are drawn on (not rainfall or climate: their own blues and greens would read as lakes)
export const LAKE_LAYERS = new Set(['biome', 'elevation']);
export function lakeKind(i) {
  const L = S.V.layers;
  if (L.elevation[i] <= 0) return 0;
  return L.lake_kind ? L.lake_kind[i] : L.lake ? (L.lake[i] ? 1 : 0) : 0;
}
function lakeDepth(i) {
  const L = S.V.layers;
  return L.lake_depth ? L.lake_depth[i] : L.lake_level ? L.lake_level[i] - L.elevation[i] : null;
}
// colours cell i's lake into c (deeper water darker); false where there's none
function lakeColor(i, c) {
  const k = lakeKind(i);
  if (!k || !LAKE_COLS[k]) return false;
  c.copy(LAKE_COLS[k]);
  const d = lakeDepth(i);
  if (DEEP_LAKE[k] && d > 0) c.lerp(DEEP_LAKE[k], Math.min(d / 500, 1) * 0.8);
  return true;
}
// depth in words: whole metres from 10 m, tenths below (runs store decimetres, worlds a tenth-metre lake_level)
const lakeDepthText = (d) => d >= 9.95 ? `~${Math.round(d)} m deep` : d >= 0.05 ? `~${d.toFixed(1)} m deep` : 'a few cm deep';
export function lakeLine(i) {
  const k = lakeKind(i), d = lakeDepth(i);
  if (!k) return null;
  return LAKE_KINDS[k][0] + (k !== 3 && d != null ? `, ${lakeDepthText(d)}` : '');
}

// colour layers drawn at sea only -> their world layer
export const SEA_LAYERS = { 'wave power': 'wave_power', 'tide range': 'tide_range', salinity: 'salinity', 'sea temperature': 'sst',
                     turbidity: 'turbidity', upwelling: 'upwelling' };
// fills a Float32Array(3n) with per-cell colours
// Peoples (planet/lineages/, meta.phase 'lineages'): the leading people's colour, paler where it holds
// less of the land, whitened where two or more mix; 'peoples mix' counts them. A picked line
// (state.people, from the panel) shows only its own range. state.peoplesWhole (the panel's toggle): a people with groups
// (ways of life, PW-665) as a whole, from the peoples_whole layer, instead of by group.
export const peoplesIdx = (i) => (state.peoplesWhole && S.V.layers.peoples_whole ? S.V.layers.peoples_whole : S.V.layers.peoples)[i];
const MIXC = new THREE.Color('#ffffff'), NOBODY = new THREE.Color('#5a5a52');
// (each line's THREE.Color once: parsing its CSS string per cell was a third of the recolour, PW-679)
const lineColor = (l) => (l ? (l._c ||= new THREE.Color(l.color)) : NOBODY);
// A marine people (realm 'coast': the shore ring, 'sea': open water; PW-775/778) is drawn on sea cells, its colour over the ocean's blue
export const isSeaPeople = (l) => !!l && (l.realm || 'land') !== 'land';
const REALM_TEXT = { coast: 'sea people, shore ring', sea: 'sea people, open sea' };
function peoplesColor(layer, i, c) {
  const L = S.V.layers, elev = L.elevation;
  if (elev[i] <= 0 && !(L.ice && L.ice[i] > 0)) {
    const sl = (S.V.run.meta.lineages || [])[layer === 'peoples blend' && L.mix_lead ? L.mix_lead[i] : layer === 'peoples mix' ? 255 : peoplesIdx(i)];
    if (!isSeaPeople(sl)) return c.copy(OCEAN);
    const dim = state.people != null && sl.index !== state.people;
    return c.copy(OCEAN).lerp(lineColor(sl), dim ? 0.12 : 0.75 * (0.5 + 0.5 * (L.peoples_share ? L.peoples_share[i] : 100) / 100));
  }
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  const lines = S.V.run.meta.lineages || [];
  if (layer === 'peoples overlay') {  // templates (tieflings...) and contact hybrids (half-elves...): the strongest
    const o = L.peoples_overlay?.[i];
    if (o == null || o === 255 || !lines[o]) {  // (no overlay here: the leading people at 25% over grey, PW-686)
      const p = lines[L.peoples[i]];
      return p ? c.copy(NOBODY).lerp(lineColor(p), 0.25) : c.copy(NOBODY);
    }
    return c.copy(lineColor(lines[o]));
  }
  if (layer === 'peoples blend') {  // the cell's composition (PW-689): the leading people's colour and the second's, by their shares, and the rest grey
    const a = L.mix_lead ? L.mix_lead[i] : L.peoples_whole[i], lead = lines[a];
    if (a === 255 || !lead) return c.copy(NOBODY);
    const sh = L.mix_lead_share[i] / 100, sb = L.mix_second_share[i] / 100, second = lines[L.mix_second[i]];
    const cl = lineColor(lead), cs = second ? lineColor(second) : NOBODY, rest = Math.max(0, 1 - sh - (second ? sb : 0));
    return c.setRGB(cl.r * sh + (second ? cs.r * sb : 0) + NOBODY.r * rest, cl.g * sh + (second ? cs.g * sb : 0) + NOBODY.g * rest,
      cl.b * sh + (second ? cs.b * sb : 0) + NOBODY.b * rest);
  }
  if (layer === 'peoples mix') { const m = L.peoples_mix[i]; return m ? c.setHSL(0.75 - 0.12 * Math.min(m, 6), 0.7, 0.35 + 0.06 * m) : c.copy(NOBODY); }
  const d = peoplesIdx(i);
  if (d === 255 || !lines[d]) return c.copy(NOBODY);
  if (state.people != null && d !== state.people) return c.copy(NOBODY).lerp(lineColor(lines[d]), 0.15);  // (the others dimmed, PW-686)
  c.copy(lineColor(lines[d])).lerp(NOBODY, 0.55 * (1 - (L.peoples_share ? L.peoples_share[i] : 100) / 100));
  if (L.peoples_mix && L.peoples_mix[i] >= 2) c.lerp(MIXC, 0.35);
  return c;
}
// Demes (planet/lineages/demes.py, PW-981): the regional population of each cell's leading people, each a shade of its
// people's colour (layer demes: index into demes.json, V.demes, loaded with the run; 65535 nobody)
export function demeOf(i) { const d = S.V.layers.demes?.[i]; return d == null || d === 65535 ? null : S.V.demes?.demes?.[d] || null; }
function demesColor(i, c) {
  const L = S.V.layers, elev = L.elevation;
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  const d = demeOf(i);
  if (elev[i] <= 0 && !d) return c.copy(OCEAN);
  if (!d) return c.copy(NOBODY);
  const col = d._c ||= new THREE.Color(d.color);
  if (state.people != null && (S.V.run.meta.lineages || [])[state.people]?.id !== d.people) return c.copy(NOBODY).lerp(col, 0.15);
  return elev[i] <= 0 ? c.copy(OCEAN).lerp(col, 0.75) : c.copy(col);
}
export async function loadDemes() {  // (demes.json beside run.json: the tree, names and colours)
  if (!S.V?.run?.meta?.demes || S.V.demes) return;
  const v = S.V;
  try { const j = await (await fetch(v.base + v.run.meta.demes.file, { cache: 'no-store' })).json(); if (S.V === v) S.V.demes = j; } catch (e) { console.error(e); }
}
// Animals (planet/lineages/animals.py, PW-691): per animal the wild range (green: derived from the land) and where it is known
// (the animal's own colour, spreading from the taming homeland over peopled land and, by boat, over the sea); both: its colour over green.
// The layers hold one bit per animal (animal_wild, animal_known; meta.animals.stocks[id].bit).
const ANIMAL_WILD = new THREE.Color('#3f9d4a');
export const ANIMAL_COLS = ['#e8a23a', '#c4553a', '#d9d4c2', '#8a5a2b', '#e6c829', '#3a7bd5', '#9b59b6', '#16a085'];
export function animalStocks() { return S.V.run?.meta?.animals?.stocks || {}; }
function animalsColor(i, c, id) {
  const L = S.V.layers, elev = L.elevation, st = animalStocks()[id];
  if (elev[i] <= 0 && !(L.ice && L.ice[i] > 0)) return c.copy(OCEAN);
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  if (!st) return c.copy(BARE);
  const w = ((L.animal_wild?.[i] || 0) >> st.bit) & 1, r = ((L.animal_known?.[i] || 0) >> st.bit) & 1;
  c.copy(BARE);
  if (w) c.lerp(ANIMAL_WILD, 0.75);
  if (r) c.lerp(new THREE.Color(ANIMAL_COLS[st.bit % 8]), 0.8);
  return c;
}
// Crops (planet/lineages/crops.py, PW-721): the same as the animals, per crop: its wild range (green) and where it is known (its colour);
// the layers crop_wild / crop_known hold one bit per crop (meta.crops.stocks[id].bit).
export const CROP_COLS = ['#e6c829', '#7aa650', '#d6b25e', '#4aa3c7', '#c9a227', '#f2d04a', '#a67c52', '#c06b3a', '#e3c34f', '#9fb46a', '#7d6bb0', '#d4482f',
  '#c0504d', '#8a9a3b', '#7b3f6e', '#d9c35a', '#5fa8a0', '#9c5a2a', '#e8452c', '#f0e6c8', '#c98a3c', '#3f7d4a', '#6fbf73', '#b58fc7',
  '#d9532b', '#5b8c3a', '#9bb86a', '#5a3b2e', '#e9e2c4', '#c79a5a', '#e08a4a', '#a3a3d1', '#6e9b3f'];  // (24-32: the regional foods, PW-765)
export function cropBit(a, i, bit) { const v = a?.[i]; return v ? Number((BigInt(v) >> BigInt(bit)) & 1n) : 0; }  // (the crop layers are uint64: BigInt)
export function cropStocks() { return S.V.run?.meta?.crops?.stocks || {}; }
function cropsColor(i, c, id) {
  const L = S.V.layers, elev = L.elevation, st = cropStocks()[id];
  if (elev[i] <= 0 && !(L.ice && L.ice[i] > 0)) return c.copy(OCEAN);
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  if (!st) return c.copy(BARE);
  const w = cropBit(L.crop_wild, i, st.bit), r = cropBit(L.crop_known, i, st.bit);
  c.copy(BARE);
  if (w) c.lerp(ANIMAL_WILD, 0.75);
  if (r) c.lerp(new THREE.Color(CROP_COLS[st.bit % CROP_COLS.length]), 0.8);
  return c;
}
export function cropRows(i, R) {  // the crops known in this frame's cell, and the wild ranges it lies in
  const L = S.V.layers;
  if (!L.crop_wild) return;
  const known = [], wild = [];
  for (const [, st] of Object.entries(cropStocks())) {
    if (cropBit(L.crop_known, i, st.bit)) known.push(st.label);
    else if (cropBit(L.crop_wild, i, st.bit)) wild.push(st.label);
  }
  if (known.length) R('place', '', known.join(', '), { lab: 'crops known', ess: true });
  if (wild.length) R('place', '', wild.join(', '), { lab: 'wild range of (crops)' });
}
// Technology (planet/lineages/techtree.py, PW-675; the map view of the workbench's Technology tab, PW-913): one tech
// (state.tech) on the frame's ranges. Each cell takes its leading people (the peoples layer): lit in the colour of how the
// tech came to that people (state.techCol 'how') or of how long it had known it ('when') if it knew it by the frame's
// time, else grey with a trace of the people's colour. Stars mark inventions (and tamings, kits) and arrows run giver
// to taker, each at the peoples' ranges of the moment it happened (overlays: techOverlays).
export const TECH_HOW = { invented: '#ffd27a', contact: '#7fb0ff', kit: '#c79bff', inherited: '#8fa0b4', tamed: '#6bd6a0', shared: '#6bd6d0' };
export const TECH_HOW_TEXT = { invented: 'invented', contact: 'by contact', kit: 'brought along (kit)', inherited: 'inherited at the split', tamed: 'by taming', shared: 'shared within its people' };
const techHowCol = (how) => TECH_HOW[how] || (String(how).startsWith('with ') ? TECH_HOW.tamed : '#aaaaaa');
export const techHowText = (how) => TECH_HOW_TEXT[how] || (String(how).startsWith('with ') ? `with ${how.slice(5)}` : how);
const TECH_NOT = new THREE.Color('#464e5a'), TECH_EMPTY = new THREE.Color('#2a2e28'), TECH_NEW = new THREE.Color('#ffeca0'), TECH_OLD = new THREE.Color('#d64828');
state.tech = null; state.techCol = 'how';
export const techTree = () => S.V?.run?.meta?.techtree || null;
export function techId() {  // the tech shown: state.tech if the run has it, else pottery, else the first tech anybody came to
  const tt = techTree();
  if (!tt) return null;
  if (tt.techs.some((t) => t.id === state.tech)) return state.tech;
  return tt.techs.find((t) => t.id === 'pottery' && tt.firsts.pottery)?.id || tt.techs.find((t) => tt.firsts[t.id])?.id || tt.techs[0]?.id;
}
const techAgoText = (k) => (k >= 1000 ? `${+(k / 1000).toFixed(2)} Myr ago` : k >= 1 ? `${+k.toFixed(k >= 100 ? 0 : 2)} kyr ago` : k > 0 ? `${Math.round(k * 1000)} years ago` : 'the present');  // (finer than agoLabel: a frame and an event a few years apart)
export const techName = (id) => (techTree()?.techs.find((t) => t.id === id)?.name || id || '').split(' (')[0];
export const techOldest = (id) => Math.max(0.1, ...Object.values(techTree().known).map((k) => k[id]?.[0] ?? 0));
function techFrameColors() {  // per line index: the colour of its land this frame
  const tt = techTree(), id = techId(), now = -S.V.t, old = techOldest(id);
  return (S.V.run.meta.lineages || []).map((l) => {
    const v = tt.known[l.id]?.[id];
    if (!v || v[0] < now - 1e-9) return TECH_NOT.clone().lerp(lineColor(l), 0.18);
    if (state.techCol !== 'when') return new THREE.Color(techHowCol(v[1]));
    const u = Math.log10(Math.max(v[0] - now, 0.05) / 0.05) / Math.log10(Math.max(old, 0.1) / 0.05);
    return TECH_NEW.clone().lerp(TECH_OLD, Math.min(1, Math.max(0, u)));
  });
}
function techColor(i, c, cols) {
  const L = S.V.layers, d = L.peoples[i], ice = L.ice && L.ice[i] > 0;
  if (L.elevation[i] <= 0 && !ice) return isSeaPeople((S.V.run.meta.lineages || [])[d]) && cols[d] ? c.copy(OCEAN).lerp(cols[d], 0.75) : c.copy(OCEAN);
  if (ice) return c.copy(ICE);
  return d === 255 || !cols[d] ? c.copy(TECH_EMPTY) : c.copy(cols[d]);
}
export function techRows(i, R) {  // the hover card: what the cell's leading people knew of the tech by this frame
  const tt = techTree(), d = S.V.layers.peoples[i], l = (S.V.run.meta.lineages || [])[d], id = techId();
  if (!tt || !l) return;
  const v = tt.known[l.id]?.[id], now = -S.V.t;
  R('place', '', v && v[0] >= now - 1e-9 ? `${techName(id)}: since ${techAgoText(v[0])}, ${techHowText(v[1])}${v[2] ? ' from ' + ((S.V.run.meta.lineages.find((x) => x.id === v[2])?.name || v[2]).split(' (')[0]) : ''}`
    : `${techName(id)}: not yet${v ? ` (comes ${techAgoText(v[0])})` : ''}`, { lab: 'technology (this people)', ess: true });
}
// each people's centre (its cells' mean direction) in frame f, by line index: [lat, lon, cells]; cached per run
function techCentres(f) {
  const cache = S.V.techCent ||= new Map();
  if (cache.has(f)) return cache.get(f);
  const n = S.V.n, raw = S.V.data.peoples, G = S.V.grid, acc = new Map(), out = new Map();
  if (!raw) return out;
  const U = S.V.techU ||= (() => { const u = new Float32Array(3 * n); for (let i = 0; i < n; i++) u.set(unitVec(G.lat[i], G.lon[i]), 3 * i); return u; })();
  const a = raw.length === n ? raw : raw.subarray(f * n, (f + 1) * n);
  for (let i = 0; i < n; i++) {
    const d = a[i]; if (d === 255) continue;
    let s = acc.get(d); if (!s) acc.set(d, s = [0, 0, 0, 0]);
    s[0] += U[3 * i]; s[1] += U[3 * i + 1]; s[2] += U[3 * i + 2]; s[3]++;
  }
  for (const [d, s] of acc) {  // (three.js axes: x through 0N 0E, y north, z = -east: unitVec)
    const r = Math.hypot(s[0], s[1], s[2]) || 1;
    out.set(d, [Math.asin(s[1] / r) * 180 / Math.PI, Math.atan2(-s[2], s[0]) * 180 / Math.PI, s[3]]);
  }
  cache.set(f, out);
  return out;
}
// where a people was when something happened k kyr ago: its centre in the stored frame nearest that time (the run's first
// frame for older events), else the nearest frame it held land in, else its present centre or its origin
function techWhere(l, k) {
  const fr = S.V.run.frames, t = -k;
  let f0 = 0;
  for (let f = 0; f < fr.length; f++) if (Math.abs(fr[f].t - t) < Math.abs(fr[f0].t - t)) f0 = f;
  for (let s = 0; s < fr.length; s++) for (const f of s ? [f0 - s, f0 + s] : [f0]) {
    if (f < 0 || f >= fr.length) continue;
    const c = techCentres(f).get(l.index);
    if (c) return c;
  }
  const p = S.V.run.meta.present?.lines?.[l.id]?.centroid;
  if (p) return [p[0], p[1], 0];
  return l.origin_place ? [l.origin_place.lat, l.origin_place.lon, 0] : null;
}
export function techOverlays(globe, wraps) {
  const tt = techTree(), id = techId(), now = -S.V.t, lines = S.V.run.meta.lineages || [], byId = Object.fromEntries(lines.map((l) => [l.id, l]));
  const pts = [], cols = [], c = new THREE.Color(), mode = llMode(), r0 = globe ? 1.016 : 1;
  const seg = (p1, p2) => { if (!wraps(p1, p2)) { pts.push(...p1, ...p2); cols.push(c.r, c.g, c.b, c.r, c.g, c.b); } };
  const P = (la, lo, lift = 1) => llPosPt(llPoint(la, lo), r0 * lift, mode);
  for (const l of lines) {
    const v = tt.known[l.id]?.[id];
    if (!v || v[0] < now - 1e-9) continue;
    const b = techWhere(l, v[0]);
    if (!b) continue;
    c.set(techHowCol(v[1]));
    if (v[1] === 'invented' || v[1] === 'tamed' || v[1] === 'kit') {  // a five-pointed star, ~2.4 degrees across
      const cl = Math.max(Math.cos(b[0] * Math.PI / 180), 0.2), ring = [];
      for (let k = 0; k <= 10; k++) { const a = Math.PI / 2 + k * Math.PI / 5, r = k % 2 ? 1.0 : 2.4; ring.push(P(b[0] + r * Math.sin(a), b[1] + r * Math.cos(a) / cl)); }
      for (let k = 0; k < 10; k++) seg(ring[k], ring[k + 1]);
    } else if (v[2] && byId[v[2]]) {  // an arrow from the giver, arching over the surface on the globe
      const a = techWhere(byId[v[2]], v[0]);
      if (!a) continue;
      const ua = unitVec(a[0], a[1]), ub = unitVec(b[0], b[1]);
      const om = Math.acos(Math.min(1, Math.max(-1, ua[0] * ub[0] + ua[1] * ub[1] + ua[2] * ub[2])));
      if (om < 1e-4) continue;
      const N = Math.max(4, Math.ceil(om * 40)), arc = [];
      for (let k = 0; k <= N; k++) {
        const s = k / N, wa = Math.sin((1 - s) * om) / Math.sin(om), wb = Math.sin(s * om) / Math.sin(om);
        const x = wa * ua[0] + wb * ub[0], y = wa * ua[1] + wb * ub[1], z = wa * ua[2] + wb * ub[2];
        arc.push(P(Math.asin(Math.max(-1, Math.min(1, y))) * 180 / Math.PI, Math.atan2(-z, x) * 180 / Math.PI, globe ? 1 + 0.035 * om * Math.sin(Math.PI * s) : 1));
      }
      for (let k = 0; k < N; k++) seg(arc[k], arc[k + 1]);
      const e = arc[N], q = arc[N - 1], d = [e[0] - q[0], e[1] - q[1], e[2] - q[2]], dl = Math.hypot(...d) || 1;
      const up = globe ? e.map((x) => x / (Math.hypot(...e) || 1)) : [0, 0, 1], h = globe ? 0.025 : 0.035;
      const sd = [d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0]].map((x) => x / dl);
      for (const sg of [1, -1]) seg(e, [0, 1, 2].map((j) => e[j] - d[j] / dl * h + sg * sd[j] * h * 0.6));
    }
  }
  return { techMarks: ribbonObj(pts, 0xffffff, 1, 2.2, cols) };
}
export function fillTechs() {
  const tt = techTree();
  if (!tt) return;
  const id = techId();
  $('techSel').innerHTML = tt.tracks.map((k) => `<optgroup label="${esc(k.name)}">` + tt.techs.filter((t) => t.track === k.id)
    .map((t) => `<option value="${t.id}"${t.id === id ? ' selected' : ''}>${esc(t.name.split(' (')[0])}${tt.firsts[t.id] ? '' : ' (nobody)'}</option>`).join('') + '</optgroup>').join('');
  $('techColSel').value = state.techCol;
}
function setTech(id, col) {
  if (id) state.tech = id;
  if (col) state.techCol = col;
  const u = new URL(location); u.searchParams.set('tech', techId()); u.searchParams.set('techcol', state.techCol); history.replaceState(null, '', u);
  if (state.layer === 'technology') { fillTechs(); paint(); updateHover(); }
}
$('techSel').addEventListener('change', () => setTech($('techSel').value));
$('techColSel').addEventListener('change', () => setTech(null, $('techColSel').value));
// embedded (?embed=tech): the workbench picks the tech, the colour mode and the moment, and hears of each frame shown
addEventListener('message', (e) => {
  if (e.origin !== location.origin || e.source !== parent || !S.V?.run || !e.data) return;
  if (e.data.techSet) setTech(e.data.techSet.tech, e.data.techSet.col);
  if (e.data.techAgo != null) {
    const t = -e.data.techAgo, fr = S.V.run.frames;  // (the first stored moment at or after it, so the event shows)
    let f = fr.findIndex((x) => x.t >= t - 1e-6); if (f < 0) f = fr.length - 1;
    stop(); setFrame(f);
  }
  if (e.data.techLine) {  // (turn the globe to where that people was then: {techLine: id, techLineAgo: kyr})
    const l = (S.V.run.meta.lineages || []).find((x) => x.id === e.data.techLine), b = l && techWhere(l, e.data.techLineAgo ?? -S.V.t);
    if (b) { $('spin').checked = false; turnTo(b[0], b[1]); }
  }
});
export function techTellParent() {
  if (parent === window || !document.body.classList.contains('embed') || !S.V?.run) return;
  parent.postMessage({ techFrame: { ago: -S.V.t, first: -S.V.run.frames[0].t, frames: S.V.run.frames.length, tech: techId() } }, location.origin);
}

// Fuels (planet/lineages/fuels.py, PW-722): what the cell burns to cook, at the present (meta.fuels: the lead fuel and each fuel's share)
// (PW-845: the same layer on a run's present and on a finished world with a peoples run: fuelSrc gives {F: meta.fuels, A: the layers})
export function fuelSrc() {
  if (S.V.kind === 'world') return S.V.wAnthroRun?.fuels && S.V.wAnthro?.fuel_lead && worldAnthroOn() ? { F: S.V.wAnthroRun.fuels, A: S.V.wAnthro } : null;
  return S.V.run?.meta?.fuels && anthroOn() && S.V.anthro?.fuel_lead ? { F: S.V.run.meta.fuels, A: S.V.anthro } : null;
}
function fuelColor(i, c) {
  const L = S.V.layers, fs = fuelSrc();
  if (L.elevation[i] <= 0 && !(L.ice && L.ice[i] > 0)) return c.copy(OCEAN);
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  if (!fs) return c.copy(BARE);
  const d = fs.A.fuel_lead[i];
  if (d === 255) return c.copy(NOBODY);
  const name = fs.F.names[d];
  c.set(fs.F.colors[name]);
  return c.lerp(NOBODY, 0.45 * (1 - fs.A['fuel_' + name][i] / 100));
}
export function fuelRows(i, R) {
  const fs = fuelSrc();
  if (!fs || fs.A.fuel_lead[i] === 255) return;
  const F = fs.F, bits = F.names.map((k) => [k, fs.A['fuel_' + k][i]]).filter(([, v]) => v >= 5).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}%`);
  R('place', '', bits.join(', '), { lab: 'fuel (present)', ess: true });
}
// Peoples change the land (planet/lineages/landuse.py, PW-662): the run's anthropogenic overlay at the present
// (meta.anthro: cropland, pasture, burned grassland, managed woods, settlement density, tree cover left) as the
// 'land use' layer, and as a tint on the vegetation colours (tree cover, vegetation, satellite) where land is
// cleared (state.anthro, the panel's checkbox; &anthro=0 turns it off). Only the last frame (the present) shows it.
const ANTHRO_TINTED = new Set(['tree cover', 'vegetation', 'satellite']);
export const WORLD_TINTED = new Set(['vegetation', 'satellite', 'biome']);  // (a finished world, PW-669)
const A_CROP = new THREE.Color('#f0b429'), A_PAST = new THREE.Color('#b9d36a'), A_BURN = new THREE.Color('#c98a3c'),
  A_MAN = new THREE.Color('#2d6a4a'), A_TOWN = new THREE.Color('#9c3b2a');
function anthroLoad() {
  const a = S.V.run.meta.anthro, id = S.V.run.id;
  S.V.anthroFor = id; S.V.anthro = {};
  const fl = S.V.run.meta.fuels?.layers || {};  // (the fuel layers ride along: V.anthro.fuel_<name>)
  Promise.all([...Object.entries(a.layers).map(([k, s]) => [k, s]), ...Object.entries(fl).map(([k, s]) => ['fuel_' + k, s])]
    .map(([k, s]) => fetch(`../runs/${id}/${s.file}`).then((r) => r.arrayBuffer())
    .then((b) => { S.V.anthro[k] = new Uint8Array(b); }))).then(() => { if (S.V.run.id === id) { S.V.anthroReady = id; paint(); if (S.picked) renderZoomBox(); } }).catch(() => {});
}
// A finished world with a peoples run (run.meta.world = the world id): the run's overlay tints the world's own
// satellite, vegetation and biome colours (PW-669). Newest peoples run, or &peoples=RUN (&peoples=0: none). The
// cells are the run's cells; the layers are read on the fly and nothing is written into the world.
export async function worldAnthroLoad() {
  const v = S.V;
  v.wAnthro = null; v.wAnthroRun = null;
  const want = new URLSearchParams(location.search).get('peoples');
  if (want === '0' || v.kind !== 'world' || !v.id) return;
  const cands = (S.IDX?.runs || []).filter((r) => r.phase === 'lineages' && r.world === v.id && (!want || r.dir === want || r.id === want))
    .sort((a, b) => (b.created || '').localeCompare(a.created || ''));
  for (const r of cands) {
    try {
      const run = await (await fetch(`../runs/${r.dir}/run.json`, { cache: 'no-store' })).json();
      const a = run.meta?.anthro;
      if (!a || run.meta.cells !== v.n) continue;
      const A = {};
      const fl = run.meta.fuels?.layers || {};  // (the fuels view of the peoples run, PW-845)
      await Promise.all([...Object.entries(a.layers), ...Object.entries(fl).map(([k, s]) => ['fuel_' + k, s])]
        .map(([k, s]) => fetch(`../runs/${r.dir}/${s.file}`).then((x) => x.arrayBuffer()).then((b) => { A[k] = new Uint8Array(b); })));
      if (S.V !== v) return;
      v.wAnthro = A; v.wAnthroRun = { id: r.id, dir: r.dir, name: r.name, anthro: a, fuels: run.meta.fuels || null };
      if (state.wantLayer === 'fuels') state.layer = 'fuels';
      state.wantLayer = null;
      renderLayerButtons(); renderSummary(); renderLegend(); paint();
      return;
    } catch (err) { console.warn('peoples run', r.dir, err); }
  }
}
export const worldAnthroOn = () => !!(S.V?.kind === 'world' && S.V.wAnthro && state.anthro !== false);
export function worldAnthroPanel() {
  const r = S.V.wAnthroRun;
  if (!r) return '';
  const s = r.anthro.summary;
  return `<div style="margin-top:4px"><label title="Tint the satellite, vegetation and biome colours where the peoples of run ${r.id} have cleared, grazed, burned or cut the land (read from the run; nothing is written into the world)."><input type="checkbox" data-anthro ${state.anthro !== false ? 'checked' : ''}> show cleared land</label>
    <span class="muted">· peoples run <a href="?run=${r.dir}">${r.id}</a>: cropland ${s.cropland_mkm2} Mkm² (${(100 * s.cropland_share_of_fertile).toFixed(1)}% of the ${s.fertile_mkm2} Mkm² farmland), pasture ${s.pasture_mkm2}, burned grass ${s.burned_mkm2}, managed woods ${s.managed_mkm2}</span></div>`;
}
// the present's overlay is ready and this frame is the present (the last)
export const anthroOn = () => !!(S.V.run?.meta?.anthro && S.V.anthroReady === S.V.run.id && S.V.frame === S.V.run.frames.length - 1);
export const anthroSrc = () => (S.V.kind === 'world' ? S.V.wAnthro : S.V.anthro);
function anthroTint(i, c) {
  const A = anthroSrc(), cr = A.crop[i] / 100, pa = A.pasture[i] / 100, bu = A.burned[i] / 100, ma = A.managed[i] / 100;
  if (cr + pa + bu + ma <= 0.004) return c;
  c.lerp(A_PAST, Math.min(0.85, 1.6 * Math.sqrt(pa))).lerp(A_BURN, Math.min(0.85, 2.5 * Math.sqrt(bu)));
  c.lerp(A_MAN, Math.min(0.5, 2 * ma)).lerp(A_CROP, Math.min(0.95, 2.2 * Math.sqrt(cr)));
  return c;
}
function landUseColor(i, c) {
  const L = S.V.layers;
  if (L.elevation[i] <= 0 && !(L.ice && L.ice[i] > 0)) return c.copy(OCEAN);
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  rampFns['tree cover'](L.tree_cover[i], c);  // (the land as it was: wild tree cover)
  if (!anthroOn()) return c;
  anthroTint(i, c);
  const d = 2 ** (S.V.anthro.people[i] * S.V.run.meta.anthro.layers.people.scale) - 1;  // people/km²: settled country reddens
  if (d >= 6) c.lerp(A_TOWN, Math.min(0.4, 0.02 * (d - 4)));
  return c;
}
export function anthroRows(i, R) {
  if (S.V.kind !== 'world' && !anthroOn()) return;
  const A = anthroSrc(), d = 2 ** (A.people[i] * (S.V.kind === 'world' ? S.V.wAnthroRun.anthro : S.V.run.meta.anthro).layers.people.scale) - 1;
  const bits = [['cropland', A.crop[i]], ['pasture', A.pasture[i]], ['burned grass', A.burned[i]], ['managed woods', A.managed[i]]]
    .filter(([, v]) => v >= 1).map(([k, v]) => `${k} ${v}%`);
  R('place', '', `${d >= 0.1 ? `${d < 10 ? d.toFixed(1) : Math.round(d)} people/km²` : 'unsettled'}${bits.length ? ': ' + bits.join(', ') : ''}`,
    { lab: 'land use (present)', ess: true });
}
function anthroPanel() {
  const a = S.V.run.meta.anthro;
  if (!a) return '';
  const s = a.summary;
  return `<div style="margin-top:4px"><label title="Tint the vegetation colours (tree cover) where peoples have cleared the land, grazed it, burned it or cut it. Shown at the present (the last frame); the 'land use' layer shows it on its own."><input type="checkbox" data-anthro ${state.anthro !== false ? 'checked' : ''}> show cleared land (present)</label>
    <div class="muted" style="max-width:340px">cropland ${s.cropland_mkm2} Mkm² (${(100 * s.cropland_share_of_fertile).toFixed(1)}% of ${s.fertile_mkm2} Mkm² farmland), pasture ${s.pasture_mkm2}, burned grass ${s.burned_mkm2}, managed woods ${s.managed_mkm2}; trees ${s.tree_before_mkm2} → ${s.tree_after_mkm2} Mkm² (−${(100 * s.forest_lost_share).toFixed(1)}%)</div></div>`;
}
document.addEventListener('change', (e) => {
  if (!e.target.matches?.('[data-anthro]')) return;
  if (S.V?.kind === 'world' && S.V.wAnthro) { state.anthro = e.target.checked; paint(); renderLegend(); return; }
  if (!S.V?.run?.meta?.anthro) return;
  state.anthro = e.target.checked;
  paint(); buildOverlays(); renderRunSummary();
});
export function peoplesPanel() {
  const m = S.V.run.meta, lines = m.lineages || [], s = S.V.run.frames[S.V.frame].stats.peoples || {};
  const mf = S.V.frame === S.V.run.frames.length - 1 ? (m.present?.megafauna || {}) : {};  // (counted megafauna at the present, PW-924)
  const kids = {}; lines.forEach((l) => (l.parents || []).forEach((p) => (kids[p] = kids[p] || []).push(l)));
  const hasGroups = lines.some((l) => l.group_of);
  const fmt = (a) => (a >= 1000 ? `${+(a / 1000).toFixed(1)} Myr` : a >= 1 ? `${+a.toFixed(1)} kyr` : `${Math.round(a * 1000)} yr`);
  const row = (l, depth) => {
    const alive = s[l.id] != null, o = l.origin_place;
    const sea = isSeaPeople(l) ? ` <span class="muted">(${REALM_TEXT[l.realm] || 'sea people'})</span>` : '';
    const kind = sea + (l.origin === 'split' ? '' : l.origin === 'group' ? ' <span class="muted">(way of life)</span>'
      : ` <span class="muted">(${l.origin}${l.parents?.length && l.origin !== 'split' ? ' of ' + l.parents.join(' + ') : ''})</span>`);
    return `<div style="padding:1px 0 1px ${6 + 12 * depth}px;cursor:pointer;opacity:${alive ? 1 : 0.5}" data-people="${l.index}"
      title="${esc(l.story || (o ? `from ${o.lat}, ${o.lon} at ${fmt(o.ago_kyr)} ago: ${o.why}` : 'not yet / never appeared'))}">
      <span style="display:inline-block;width:10px;height:10px;background:${l.color};margin-right:4px"></span>${esc(l.name)}${kind}
      <span class="muted">${fmt(l.ago_kyr)}${l.extinct_kyr != null ? ` → † ${fmt(l.extinct_kyr)}` : ''}${alive ? ` · ${s[l.id]} Mkm²` : ''}${alive && mf[l.id] ? ` · ~${mf[l.id].count} in ${mf[l.id].pockets} pockets` : ''}</span></div>`;
  };
  const seen = new Set(), out = [];
  const walk = (l, d) => { if (seen.has(l.id)) return; seen.add(l.id); out.push(row(l, d));
    if (!state.peoplesWhole) (kids[l.id] || []).filter((k) => k.origin === 'group').forEach((k) => walk(k, d + 1));
    (kids[l.id] || []).filter((k) => k.origin === 'split').forEach((k) => walk(k, d + 1)); };
  lines.filter((l) => l.origin !== 'split' && l.origin !== 'group').forEach((l) => walk(l, 0));
  const mfSel = state.people != null && lines[state.people] ? mf[lines[state.people].id] : null;
  const mfBox = mfSel ? `<div style="margin-top:4px;max-width:360px"><b>Counted</b> <span class="muted">(megafauna, 1 per ${(mfSel.one_per_km2 || 0).toLocaleString()} km²${mfSel.pressed_one_per_km2 ? `: 1 per ${mfSel.pressed_one_per_km2.toLocaleString()} where peoples press them, 1 per ${mfSel.natural_one_per_km2.toLocaleString()} where none do` : ''}${mfSel.suitable_reached != null ? `; in ${Math.round(100 * mfSel.suitable_reached)}% of their country` : ''})</span><br>`
    + (mfSel.stages ? `<span title="By stage, under the age schedule '${esc(mfSel.ages || '')}' (PW-958)">${[[3, 'ancient', 'ancients'], [2, 'adult', 'adults'], [1, 'young', 'young'], [0, 'wyrmling', 'wyrmlings']].filter(([i]) => mfSel.stages[i]).map(([i, a, b]) => `${mfSel.stages[i]} ${mfSel.stages[i] === 1 ? a : b}`).join(', ')}; ~${Math.round(mfSel.count * (mfSel.cattle_yr_each || 0)).toLocaleString()} cattle a year</span><br>` : '')
    + mfSel.pocket_list.slice(0, 8).map((q) => `~${q.count} in the ${esc(q.country)} at ${q.lat}, ${q.lon}${q.landmass_name ? ` (${esc(q.landmass_name)})` : ''} <span class="muted">${esc(q.groups)}</span>`).join('<br>')
    + (mfSel.pocket_list.length > 8 ? `<br><span class="muted">… ${mfSel.pocket_list.length - 8} more pockets</span>` : '') + '</div>' : '';
  const p = m.present || {}, zones = (p.mixing_zones || []).slice(0, 5).map((z) => `${z.lines.join(', ')} <span class="muted">(${z.area_mkm2} Mkm² near ${z.lat}, ${z.lon})</span>`);
  return `<div class="tzBox"><b>Peoples</b> <span class="muted">(${esc(m.tree_name || '')}; click one to show only its range;
    <a href="lineages.html?tree=${encodeURIComponent((m.tree_file || '').split('/').pop().replace(/\.(toml|json)$/, '') || 'dnd')}&world=${m.world || ''}">edit the tree</a>)</span>
    ${hasGroups ? `<div><label title="A people with groups (ways of life: steppe and forest orcs, human seafarers...) shown as one people, or each group in its own tint"><input type="checkbox" data-peopleswhole ${state.peoplesWhole ? 'checked' : ''}> peoples as wholes (not by group)</label></div>` : ''}
    ${anthroPanel()}
    ${state.people != null ? `<div><a href="#" data-people="-1">show all</a></div>` : ''}${out.join('')}
    ${zones.length ? `<div style="margin-top:4px"><b>Mixing at the present:</b> <span class="muted">${p.mixing ? `${p.mixing.area_mkm2} Mkm² (${Math.round(100 * p.mixing.land_share)}% of the land; corridors ${Math.round(100 * (p.mixing.in_corridors || 0))}% mixed, closed country ${Math.round(100 * (p.mixing.in_closed || 0))}%)` : ''}</span><br>${zones.join('<br>')}</div>` : ''}
    ${p.empty_continents?.length ? `<div class="muted">nobody on ${p.empty_continents.join(', ')}</div>` : ''}
    ${Object.keys(mf || {}).length ? `<div class="muted"><a href="/docs/review/megafauna/age-of-dragons.html" target="_blank" title="The owner's review of the natural dragon numbers (PW-967): candidates side by side, counts over familiar areas, food against livestock, ranges">age of dragons review</a></div>` : ''}
    ${Object.entries(p.megafauna_ages || {}).filter(([, r]) => r.peak > r.present && r.peak_kyr > 0).map(([kind, r]) => `<div class="muted" title="The megafauna's count over the stored frames: where no people presses them they keep near their natural density (PW-957)">the age of ${kind}: ~${r.peak.toLocaleString()} ${r.peak_kyr} kyr ago, before the peoples spread; ~${r.present.toLocaleString()} now</div>`).join('')}
    ${state.people != null && lines[state.people]?.story ? `<div style="margin-top:4px;max-width:340px">${esc(lines[state.people].story)}</div>` : ''}${mfBox}
    <div style="margin-top:4px"><button data-brief="${state.people != null && lines[state.people] ? esc(lines[state.people].id) : ''}" title="What a people's range looks like for a cook: land, fuels, wild and grown foods, coast, seasons, bad years; pick any people, an era, or the picked cell in the window (planet brief, PW-728)">Culinary brief…</button></div>
    ${p.wishes?.length ? `<div style="margin-top:4px"><b>Wishes</b> <span class="muted">(score ${p.wish_score}; tries ${(p.tries || []).join(', ')})</span><br>${p.wishes.map((w) => `${w.a} ${w.want} ${w.b || ''}: ${w.score}`).join(' · ')}</div>` : ''}</div>`;
}
document.addEventListener('change', (e) => {
  if (!e.target.matches?.('[data-peopleswhole]') || !S.V?.run?.meta?.lineages) return;
  state.peoplesWhole = e.target.checked;
  const lines = S.V.run.meta.lineages;  // (a picked group becomes its people)
  if (state.peoplesWhole && state.people != null && lines[state.people]?.group_of) state.people = lines.find((l) => l.id === lines[state.people].group_of)?.index ?? null;
  paint(); buildOverlays(); renderRunSummary();
});
// The culinary brief of a people (PW-837): the server builds it (GET /api/brief) and the panel shows its Markdown text
// as it is, with a copy button and the JSON a download.
const briefBox = document.createElement('div');
// (the box's inline display:flex beat the `hidden` attribute, so the brief's dark overlay covered the page from the start: [hidden] wins now)
document.head.append(Object.assign(document.createElement('style'), { textContent: '[hidden]{display:none !important}' }));
briefBox.hidden = true;
briefBox.style.cssText = 'position:fixed;inset:0;z-index:40;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center';
briefBox.innerHTML = '<div class="panel" style="width:min(820px,94vw);max-height:88vh;display:flex;flex-direction:column;padding:12px"><div style="display:flex;gap:8px;align-items:center;margin-bottom:6px"><b id="briefTitle" style="flex:1">Culinary brief</b><select id="briefWho" title="Any people of this run"></select><label title="How long ago, in kyr (0: the present)">era <input id="briefEra" type="number" min="0" step="1" value="0" style="width:56px"> kyr ago</label><button id="briefGo">Show</button><button id="briefHere" title="The brief of the country around the picked cell (click a cell on the map first), all peoples there">Brief here</button><button id="briefCopy">Copy text</button><button id="briefJson">Download JSON</button><button id="briefClose">Close</button></div><pre id="briefText" style="overflow:auto;white-space:pre-wrap;margin:0;font:12px/1.45 ui-monospace,monospace"></pre></div>';
document.body.append(briefBox);
let briefData = null;
briefBox.addEventListener('click', (e) => { if (e.target === briefBox || e.target.id === 'briefClose') briefBox.hidden = true; });
$('briefCopy', briefBox).addEventListener('click', () => navigator.clipboard?.writeText(briefData?.markdown || '').then(() => toast('Copied the brief')));
$('briefJson', briefBox).addEventListener('click', () => {
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(briefData.brief, null, 1)], { type: 'application/json' }));
  a.download = `brief-${S.V.run.id}-${briefData.who}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
});
// (people: one of the run's peoples; region: {lat, lon} of the picked cell for "brief here": the country around it, whoever lives there; era: kyr ago, PW-863)
async function showBrief(pid, era = 0, region = null) {
  const run = S.V.run.id || S.V.dir, lines = (S.V.run.meta.lineages || []).filter((l) => !l.overlay);
  const who = $('briefWho', briefBox), eraIn = $('briefEra', briefBox);
  if (who.options.length !== lines.length) who.innerHTML = lines.map((l) => `<option value="${esc(l.id)}">${esc(l.name || l.id)}</option>`).join('');
  if (!pid && !who.value) pid = 'human';
  if (pid && [...who.options].some((o) => o.value === pid)) who.value = pid;
  eraIn.value = era;
  const line = lines.find((l) => l.id === who.value);
  const when = era > 0 ? `${era} kyr ago` : 'present';
  $('briefTitle', briefBox).textContent = region ? `Culinary brief: around ${region.lat}, ${region.lon} (${when})` : `Culinary brief: ${line?.name || who.value} (${when})`;
  $('briefText', briefBox).textContent = 'Building the brief…';
  briefBox.hidden = false;
  try {
    const q = region ? `region=${region.lat},${region.lon}` : `people=${encodeURIComponent(who.value)}`;
    const r = await fetch(`/api/brief?run=${encodeURIComponent(run)}&${q}&era=${era}`), j = await r.json();
    if (!r.ok) throw new Error(j.error || r.status);
    briefData = { ...j, who: region ? `here-${region.lat}_${region.lon}` : who.value };
    $('briefText', briefBox).textContent = j.markdown;
  } catch (err) { $('briefText', briefBox).textContent = 'Could not build the brief: ' + err.message; }
}
const briefEra = () => Math.max(0, +$('briefEra', briefBox).value || 0);
$('briefGo', briefBox).addEventListener('click', () => showBrief($('briefWho', briefBox).value, briefEra()));
$('briefWho', briefBox).addEventListener('change', () => showBrief($('briefWho', briefBox).value, briefEra()));
$('briefHere', briefBox).addEventListener('click', () => {
  if (!S.picked) return toast('Pick a cell on the map first');
  showBrief($('briefWho', briefBox).value, briefEra(), { lat: S.picked.lat, lon: S.picked.lon });
});
addEventListener('keydown', (e) => { if (e.key === 'Escape' && !briefBox.hidden) briefBox.hidden = true; });
document.addEventListener('click', (e) => {
  const bt = e.target.closest?.('[data-brief]');
  if (bt) { e.preventDefault(); showBrief(bt.dataset.brief); return; }
  const el = e.target.closest?.('[data-people]');
  if (!el || !S.V?.run?.meta?.lineages) return;
  e.preventDefault();
  const k = +el.dataset.people;
  state.people = k < 0 || state.people === k ? null : k;
  paint(); buildOverlays(); renderRunSummary();
});

export function cellColors(layer) {
  const L = S.V.layers, n = S.V.n, out = new Float32Array(3 * n), c = new THREE.Color();
  const elev = L.elevation, ov = obsView(layer), lakes = !ov && LAKE_LAYERS.has(layer) && (L.lake_kind || L.lake);
  const sv = seasonalData(layer);  // temperature / rain: the year's, or July's / January's
  if (S.V.run?.meta?.anthro && S.V.anthroFor !== S.V.run.id) anthroLoad();  // (peoples change the land, PW-662)
  const tint = state.anthro !== false && (ANTHRO_TINTED.has(layer) && anthroOn() || WORLD_TINTED.has(layer) && worldAnthroOn());
  const techCols = layer === 'technology' && techTree() && L.peoples ? techFrameColors() : null;  // (each line's colour this frame, once)
  for (let i = 0; i < n; i++) {
    if (lakes && lakeColor(i, c)) { /* a lake (or salt pan) */ }
    else if (layer === 'satellite') { const v = sv[i]; c.setRGB(((v >> 16) & 255) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255, THREE.SRGBColorSpace); }
    else if (ov) obsColor(ov, i, c);
    else if (layer === 'biome') c.set(S.V.biomeColors[L.biome[i]]);
    else if (layer === 'peoples' || layer === 'peoples mix' || layer === 'peoples overlay' || layer === 'peoples blend') peoplesColor(layer, i, c);
    else if (layer === 'demes') demesColor(i, c);
    else if (layer.startsWith('body: ')) {
      if (L.ice && L.ice[i] > 0) c.copy(ICE); else if (elev[i] <= 0) c.copy(OCEAN);
      else if (L.peoples_whole[i] === 255) c.copy(NOBODY); else rampFns.body(L['body_' + layer.slice(6)][i], c);
    }
    else if (layer === 'land use') landUseColor(i, c);
    else if (layer.startsWith('animal: ')) animalsColor(i, c, layer.slice(8));
    else if (layer.startsWith('crop: ')) cropsColor(i, c, layer.slice(6));
    else if (layer === 'technology') { if (techCols) techColor(i, c, techCols); else c.copy(NODATA); }
    else if (layer === 'fuels') fuelColor(i, c);
    else if (layer === 'vegetation') {
      if (elev[i] <= 0) c.copy(OCEAN); else c.set(S.V.vegColors[L.vegetation[i]] || '#888');
    } else if (layer === 'plant type') {
      if (elev[i] <= 0) c.copy(OCEAN);
      else { const f = (L['veg_' + state.pft]?.[i] || 0) / 100; c.copy(BARE).lerp(pftColor(), Math.sqrt(f)); }
    } else if (VEG_LAYERS[layer] || layer === 'leaf area') {
      if (elev[i] <= 0) c.copy(OCEAN);
      else if (layer === 'fire return') { const y = L.fire_return[i]; rampFns[layer](y > 0 ? y : 3000, c); if (!y) c.copy(BARE).lerp(OCEAN, 0.1); }
      else rampFns[layer]((sv || L[VEG_LAYERS[layer]])[i], c);
    }
    else if (layer === 'soils') {
      if (elev[i] <= 0) c.copy(OCEAN); else c.set(S.V.soilColors[L.soil[i]] || '#888');
    } else if (SOIL_LAYERS[layer]) {
      if (elev[i] <= 0) c.copy(OCEAN); else rampFns[layer](L[SOIL_LAYERS[layer]][i], c);
    } else if (GAME_LAYERS[layer]) {
      const v = L[GAME_LAYERS[layer]][i];
      if (elev[i] <= 0) c.copy(OCEAN);
      else if (layer === 'travel' && !v) c.copy(BARE);  // (lakes)
      else rampFns[layer](GAME_MASKS.has(layer) ? bits(v) : v, c);
    }
    else if (HU_LAYERS[layer]) huColor(layer, i, c);
    else if (RES_LAYERS.has(layer)) resColor(layer, i, c);
    else if (COAST_LAYERS.has(layer)) coastColor(layer, i, c);
    else if (layer === 'bed under ice') {
      rampFns.elevation(L.bed ? L.bed[i] : elev[i], c);
      if (L.ice && L.ice[i] > 0) c.lerp(ICE, 0.15);
    }
    else if (layer === 'ice thickness') {
      if (L.ice[i] > 0) rampFns[layer](L.ice[i], c); else c.copy(elev[i] > 0 ? BARE : OCEAN);
    }
    else if (layer === 'plates') {
      plateColor(L.plate[i], L.crust[i], c);
      if (L.plate_boundary[i] > 0) c.lerp(RED, 0.75);
      else if (L.plate_boundary[i] < 0) c.lerp(CYAN, 0.75);
    } else if (layer === 'crust age') {
      if (L.crust[i]) rampFns['rock age'](L.crust_age[i], c); else rampFns[layer](L.crust_age[i], c);
    } else if (layer === 'rock type') {
      c.set(S.V.rockColors[L.rock[i]]);
      if (elev[i] <= 0) c.lerp(OCEAN, 0.45);
    } else if (layer === 'climate') {
      c.set(S.V.koppenColors[L.climate[i]] || '#1d3f6e');
    } else if (layer === 'surface rock') {
      c.set(S.V.rockColors[L.surface_rock[i]]);
      if (elev[i] <= 0) c.lerp(OCEAN, 0.45);
    } else if (layer === 'landforms') {
      if (elev[i] <= 0 || !L.landform[i]) c.copy(OCEAN); else c.set(S.V.landformColors[L.landform[i]] || '#888');
    } else if (layer === 'crust thickness') rampFns[layer](L.crust_thickness[i], c);
    else if (layer === 'sediment') rampFns[layer](L.sediment_cover[i], c);
    else if (layer === 'glacial erosion') rampFns[layer](L.glacial_erosion[i], c);
    else if (layer === 'glacial till') rampFns[layer](L.glacial_till[i], c);
    else if (layer === 'glacial outwash') rampFns[layer](L.glacial_outwash[i], c);
    else if (layer === 'glacial loess') rampFns[layer](L.glacial_loess[i], c);
    else if (layer === 'coastal life') {  // the biggest habitat's colour over land or sea
      c.copy(elev[i] > 0 ? BARE : OCEAN);
      const t = coastalTop(i);
      if (t) c.lerp(COASTAL_COLS[t[0]], 0.25 + 0.75 * Math.min(Math.sqrt(t[1] / 30), 1));
    }
    else if (SEA_LAYERS[layer]) {  // at sea only
      if (elev[i] > 0) c.copy(BARE).lerp(OCEAN, 0.15);
      else rampFns[layer]((sv || L[SEA_LAYERS[layer]])[i], c);
    }
    else if (layer === 'humidity' || layer === 'dew point') {  // land and sea (land a little greyed, for the coasts)
      rampFns[layer](sv[i], c);
      if (elev[i] > 0) c.lerp(BARE, 0.3);
    }
    else if (layer === 'cloud' || layer === 'sunshine') {  // land and sea (the sea a little bluer, for the coasts)
      rampFns[layer](sv[i], c);
      if (elev[i] <= 0) c.lerp(OCEAN, 0.25);
    }
    else if (layer === 'rainfall') { if (elev[i] <= 0) c.copy(OCEAN); else rampFns[layer](sv[i], c); }
    else if (layer === 'river floods') {
      if (elev[i] <= 0) c.copy(OCEAN);
      else { rampFns[layer](L.flood_ratio[i], c); if (L.river_frozen && L.river_frozen[i] >= 6) c.lerp(ICE, 0.35); }
    }
    else if (layer !== 'elevation' && elev[i] <= 0) c.copy(OCEAN);
    else {
      rampFns[layer]((sv || L[layer])[i], c);
      if (layer === 'elevation' && L.ice && L.ice[i] > 0 && elev[i] > 0) c.lerp(ICE, 0.75);
    }
    if (tint && elev[i] > 0 && !(L.ice && L.ice[i] > 0)) anthroTint(i, c);
    out[3 * i] = c.r; out[3 * i + 1] = c.g; out[3 * i + 2] = c.b;
  }
  return out;
}

export function availableLayers() {
  // a time zoom has no rock, rivers or rain; its plates/crust are frozen (and empty for Earth)
  if (S.V.tz) return ['elevation', 'ice thickness', 'bed under ice', 'temperature', 'climate'].concat(S.V.tzEarth ? [] : ['plates', 'crust age'],
    hasLayer('glacial_erosion') ? ['glacial erosion', 'glacial till', 'glacial outwash', 'glacial loess'] : [], hasLayer('tree_cover') ? ['tree cover'] : [],
    hasLayer('peoples') ? ['peoples', ...(hasLayer('mix_second') ? ['peoples blend'] : []), ...(hasLayer('demes') ? ['demes'] : []), 'peoples mix', 'peoples overlay'].concat(
      Object.keys(S.V.run.layers).filter((k) => k.startsWith('body_')).map((k) => 'body: ' + k.slice(5))) : [], hasLayer('animal_wild') ? Object.keys(animalStocks()).map((k) => 'animal: ' + k) : [], hasLayer('crop_wild') ? Object.keys(cropStocks()).map((k) => 'crop: ' + k) : [],
    S.V.run?.meta?.anthro ? ['land use'] : [], S.V.run?.meta?.fuels ? ['fuels'] : [], S.V.run?.meta?.techtree && hasLayer('peoples') ? ['technology'] : []);
  if (S.V.kind === 'run') return ['elevation', 'plates', 'crust age'].concat(hasLayer('ice') ? ['bed under ice'] : [],
    hasLayer('rock') ? (hasLayer('surface_rock') ? ['surface rock'] : []).concat(['rock type', 'crust thickness', 'sediment', 'rainfall']) : [],
    hasLayer('climate') ? ['temperature', 'climate'] : [], hasLayer('landform') ? ['landforms'] : [],
    hasLayer('vegetation') ? ['vegetation', 'tree cover', 'NPP'] : []);
  const ls = ['biome', 'elevation', 'temperature', 'precipitation'];
  if (S.V.layers.sat) ls.unshift('satellite');  // true colour (satellite.py, PW-083)
  if (S.V.layers.ice) ls.push('bed under ice');
  if (S.V.layers.plate) ls.push('plates');
  if (S.V.layers.crust_age) ls.push('crust age');
  if (S.V.layers.climate) ls.push('climate');
  if (S.V.layers.surface_rock) ls.push('surface rock');
  if (S.V.layers.rock) ls.push('rock type', 'crust thickness', 'sediment');
  if (S.V.layers.landform) ls.push('landforms');
  if (S.V.layers.glacial_erosion) ls.push('glacial erosion', 'glacial till', 'glacial outwash', 'glacial loess');
  if (S.V.layers.vegetation) ls.push('vegetation', 'tree cover', 'plant cover', 'canopy height', 'leaf area', 'NPP', 'biomass',
                                   'fire return', 'stand age', 'plant type');
  if (S.V.layers.soil) ls.push('soils', ...Object.keys(SOIL_LAYERS));
  if (S.V.layers.travel) ls.push(...Object.keys(GAME_LAYERS));
  if (S.V.wAnthroRun?.fuels) ls.push('fuels');  // (the peoples run's lead fuel, as in its own view: PW-845)
  if (S.V.layers.flood_ratio) ls.push('river floods');
  for (const [name, k] of Object.entries(HU_LAYERS)) if (S.V.layers[k] && S.V.humanUse?.[k]) ls.push(name);
  if (S.V.layers.resource && S.V.resLeg) ls.push('resources', 'resource', 'building stone');
  if (S.V.layers.coast_type && S.V.coastLeg) ls.push('coasts', ...Object.keys(COAST_SCORES));
  if (S.V.layers.wave_power) ls.push('wave power');
  if (S.V.layers.tide_range) ls.push('tide range');
  if (S.V.layers.sst) ls.push('sea temperature');
  if (S.V.layers.salinity) ls.push('salinity');
  if (S.V.layers.reef) ls.push('coastal life', 'turbidity');
  if (S.V.layers.upwelling) ls.push('upwelling');
  if (S.V.layers.humidity) ls.push('humidity', 'dew point');
  if (S.V.layers.cloud) ls.push('cloud', 'sunshine');
  return ls;
}
