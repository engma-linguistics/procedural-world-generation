import { S, state } from './state.js';
import { $ } from './scene.js';
import { ANIMAL_COLS, COASTAL, COAST_LAYERS, COAST_SCORES, CROP_COLS, GAME_LAYERS, HU_LAYERS, HU_OVERLAY, LAKE_KINDS, LAKE_LAYERS, OBS_LAYERS, RAMPS, RES_LAYERS, SEASONAL, SEA_LAYERS, SOIL_LAYERS, TECH_HOW, TECH_HOW_TEXT, UNITS, VEG_LAYERS, WORLD_TINTED, animalStocks, anthroOn, anthroSrc, availableLayers, coastLegend, coastText, cropBit, cropStocks, fillRes, fillTechs, fuelRows, fuelSrc, huSwatches, isSeaPeople, lakeKind, obsView, peoplesIdx, resInfo, resLegend, seasonUnits, seasonalData, techHowText, techId, techName, techOldest, techTree, worldAnthroOn, worldAnthroPanel } from './colours.js';
import { EVENT_COLORS, eventWindow, hexColor } from './overlays.js';
import { buildLandmassNames, rankLetter } from './axis.js';
import { agoLabel, finishBox, finishMomentLine, timezoomBox, timezoomSummary } from './timezoom.js';
import { drawMarks, esc, runTree, sourceLink, timezoomLink, zoomsOf } from './provenance.js';
import { fillPfts, toast } from './pick.js';
import { windKey } from './map2d.js';
import { hasLayer } from './load.js';
// ------------------------------------------------------------ UI
// a colour bar for RAMPS[key]; labels (optional) replace the end values
function rampLegend(key, units, labels) {
  const stops = RAMPS[key], lo = stops[0][0], hi = stops[stops.length - 1][0];
  const g = stops.map(([v, c]) => `${c} ${((v - lo) / (hi - lo) * 100).toFixed(1)}%`).join(',');
  const [a, b] = labels || [lo, hi];
  return `<div><div class="grad" style="background:linear-gradient(90deg,${g})"></div>
    <div class="row" style="justify-content:space-between;width:260px"><span>${a}</span><span class="muted">${units}</span><span>${b}</span></div></div>`;
}

// ------------------------------------------------------------ what the colour layer says about the whole world (PW-840)
// and about the cell under the cursor: a summary under the world's own, and a small tooltip by the pointer.
const CAT_LAYERS = () => ({ biome: ['biome', S.V.biomes], climate: ['climate', S.V.koppen], 'rock type': ['rock', S.V.rocks], 'surface rock': ['surface_rock', S.V.rocks],
  vegetation: ['vegetation', S.V.vegTypes], soils: ['soil', S.V.soilTypes], landforms: ['landform', S.V.landforms] });
// where a numeric layer has values: 'sea', 'all', or land
const NUM_ALL = new Set(['elevation', 'temperature', 'precipitation', 'humidity', 'dew point', 'cloud', 'sunshine', 'crust age', 'crust thickness', 'sediment']);
function layerNumbers(layer) {  // {arr, key, where} for a ramp layer with one number a cell, or null
  const L = S.V.layers, sv = seasonalData(layer);
  const key = SEA_LAYERS[layer] || VEG_LAYERS[layer] || SOIL_LAYERS[layer] || GAME_LAYERS[layer]
    || { 'crust age': 'crust_age', 'crust thickness': 'crust_thickness', sediment: 'sediment_cover', 'leaf area': 'lai_jul', 'river floods': 'flood_ratio' }[layer] || layer;
  const arr = sv || L[key];
  if (!arr || !arr.length || typeof arr[0] === 'bigint' || !(layer in UNITS) && !RAMPS[layer]) return null;
  return { arr, where: SEA_LAYERS[layer] ? 'sea' : NUM_ALL.has(layer) ? 'all' : 'land' };
}
function layerCats(layer) {  // {arr (ids), names, colors} for a categorical layer, fuels included
  const L = S.V.layers, c = CAT_LAYERS()[layer];
  if (c && L[c[0]] && c[1]?.length) return { arr: L[c[0]], names: c[1].map((e) => e.name || e.code || String(e)), colors: c[1].map((e) => e.color || '#888'), land: true, none: c[0] === 'soil' || c[0] === 'landform' ? 0 : -1 };
  if (layer === 'fuels' && fuelSrc()) {
    const { F, A } = fuelSrc();
    return { arr: A.fuel_lead, names: F.names, colors: F.names.map((k) => F.colors[k]), land: true, none: 255, noneName: 'nobody there' };
  }
  return null;
}
function fmtNum(v) { const a = Math.abs(v); return a >= 100 ? Math.round(v).toLocaleString() : a >= 10 ? v.toFixed(1) : a >= 1 ? v.toFixed(2) : v.toFixed(3); }
// PW-864: the summary block and the tooltip value for the layers that are neither a category nor one number a cell: the peoples
// layers (share of the land per people, mixing), animal: and crop: (wild range against where it is known), land use, resources, coasts.
// Returns {sum: html, tip: (i) => text} or null.
const sumSw = (color, text) => `<div><span class="swatch" style="display:inline-block;width:9px;height:9px;background:${color};margin-right:5px"></span>${text}</div>`;
function layerSpecial(layer) {  // (cached: the tooltip asks on every hover)
  const key = [layer, S.V.id, S.V.run?.id, S.V.frame, S.V.layers, state.res, state.peoplesWhole, anthroOn?.()].map((x) => (typeof x === "object" && x ? (x._k ||= Math.random()) : x)).join("|");
  if (S.V._spec?.key !== key) S.V._spec = { key, val: layerSpecialMake(layer) };
  return S.V._spec.val;
}
function layerSpecialMake(layer) {
  const L = S.V.layers, elev = L.elevation, n = S.V.n, cellMkm2 = 4 * Math.PI * 6371 ** 2 / n / 1e6;
  const mk = (x) => (x * cellMkm2 >= 10 ? (x * cellMkm2).toFixed(1) : (x * cellMkm2).toFixed(2)) + ' Mkm²';
  const share = (x, tot) => (tot ? (100 * x / tot < 1 && x ? (100 * x / tot).toFixed(1) : Math.round(100 * x / tot)) : 0) + '%';
  const lines = S.V.run?.meta?.lineages || [];
  if (['peoples', 'peoples mix', 'peoples overlay', 'peoples blend'].includes(layer) && L.peoples) {
    let tot = 0, peopled = 0, mixed = 0; const cnt = new Map(), mixc = [0, 0, 0, 0, 0];
    const ov = layer === 'peoples overlay' ? L.peoples_overlay : null;
    for (let i = 0; i < n; i++) {
      if (elev[i] <= 0) continue;
      tot++;
      const m = L.peoples_mix ? L.peoples_mix[i] : 0;
      if (m >= 1) peopled++;
      if (m >= 2) mixed++;
      mixc[Math.min(4, m)]++;
      const d = ov ? ov[i] : layer === 'peoples blend' && L.mix_lead ? L.mix_lead[i] : peoplesIdx(i);
      if (d != null && d !== 255 && lines[d]) cnt.set(d, (cnt.get(d) || 0) + 1);
    }
    const rows = [...cnt.entries()].sort((a, b) => b[1] - a[1]);
    let html;
    if (layer === 'peoples mix') {
      html = `<div class="muted">peoples per land cell</div>` + [1, 2, 3, 4].map((m) => mixc[m] ? `<div>${m === 4 ? '4+' : m} ${m === 1 ? 'people' : 'peoples'} <span class="muted">${share(mixc[m], tot)} · ${mk(mixc[m])}</span></div>` : '').join('') +
        `<div class="muted">nobody ${share(mixc[0], tot)}</div>`;
    } else {
      html = `<div class="muted">${ov ? 'templates and contact hybrids' : 'leading people'}, share of the land (${mk(tot)})</div>` + rows.slice(0, 8).map(([d, k]) =>
        sumSw(lines[d].color, `${esc(lines[d].name)} <span class="muted">${share(k, tot)} · ${mk(k)}</span>`)).join('') +
        (rows.length > 8 ? `<div class="muted">+ ${rows.length - 8} more</div>` : '') +
        (ov ? '' : `<div class="muted">peopled ${share(peopled, tot)} of the land · ${share(mixed, tot)} holds two or more peoples</div>`);
    }
    const tip = (i) => {
      if (elev[i] <= 0) return '';
      const m = L.peoples_mix?.[i] || 0, d = ov ? ov[i] : layer === 'peoples blend' && L.mix_lead ? L.mix_lead[i] : peoplesIdx(i);
      const nm = d != null && d !== 255 && lines[d] ? lines[d].name : ov ? 'no template or hybrid' : 'nobody';
      return layer === 'peoples mix' ? `${m} ${m === 1 ? 'people' : 'peoples'}` : nm + (m >= 2 ? ` (${m} peoples here)` : '');
    };
    return { sum: html, tip };
  }
  const bitSum = (what, wild, known, label) => {
    let tot = 0, w = 0, k = 0, kw = 0;
    for (let i = 0; i < n; i++) { if (elev[i] <= 0) continue; tot++; const a = wild(i), b = known(i); if (a) w++; if (b) k++; if (a && b) kw++; }
    return `<div class="muted">${esc(what)}, share of the land (${mk(tot)})</div>` +
      `<div>wild range <b>${mk(w)}</b> <span class="muted">${share(w, tot)}</span></div>` +
      `<div>${label} <b>${mk(k)}</b> <span class="muted">${share(k, tot)}${w ? ` · ${share(kw, w)} of its wild range` : ''}</span></div>` +
      (k > kw ? `<div class="muted">${mk(k - kw)} of it outside the wild range (carried there)</div>` : '');
  };
  const bitTip = (wild, known, label) => (i) => elev[i] <= 0 ? '' : known(i) ? `${label} here` + (wild(i) ? ' (and wild)' : '') : wild(i) ? 'wild range, not yet known' : 'not here';
  if (layer.startsWith('animal: ') && L.animal_wild) {
    const st = animalStocks()[layer.slice(8)];
    if (!st) return null;
    const wild = (i) => ((L.animal_wild[i] || 0) >> st.bit) & 1, known = (i) => ((L.animal_known?.[i] || 0) >> st.bit) & 1;
    return { sum: bitSum(st.label || layer.slice(8), wild, known, 'tamed and known'), tip: bitTip(wild, known, 'tamed and known') };
  }
  if (layer.startsWith('crop: ') && L.crop_wild) {
    const st = cropStocks()[layer.slice(6)];
    if (!st) return null;
    const wild = (i) => cropBit(L.crop_wild, i, st.bit), known = (i) => cropBit(L.crop_known, i, st.bit);
    return { sum: bitSum(st.label || layer.slice(6), wild, known, 'cultivated and known'), tip: bitTip(wild, known, 'cultivated and known') };
  }
  if (layer === 'land use') {
    if (!anthroOn()) return { sum: '<div class="muted">step to the last frame (the present) to see it</div>', tip: () => '' };
    const A = anthroSrc(), P = S.V.run.meta.anthro.layers.people.scale;
    let tot = 0, cr = 0, pa = 0, bu = 0, ma = 0, town = 0;
    for (let i = 0; i < n; i++) {
      if (elev[i] <= 0) continue;
      tot++; cr += A.crop[i] / 100; pa += A.pasture[i] / 100; bu += A.burned[i] / 100; ma += A.managed[i] / 100;
      if (2 ** (A.people[i] * P) - 1 >= 6) town++;
    }
    const row = (c, name, v) => sumSw(c, `${name} <b>${mk(v)}</b> <span class="muted">${share(v, tot)} of the land</span>`);
    return { sum: row('#f0b429', 'cropland', cr) + row('#b9d36a', 'pasture', pa) + row('#c98a3c', 'burned grassland', bu) + row('#2d6a4a', 'managed woods', ma) +
      sumSw('#9c3b2a', `densely settled (6+ people/km²) <b>${mk(town)}</b> <span class="muted">${share(town, tot)}</span>`),
      tip: (i) => {
        if (elev[i] <= 0) return '';
        const d = 2 ** (A.people[i] * P) - 1;
        const bits = [['cropland', A.crop[i]], ['pasture', A.pasture[i]], ['burned grass', A.burned[i]], ['managed woods', A.managed[i]]].filter(([, v]) => v >= 1).map(([k, v]) => `${k} ${v}%`);
        return (d >= 0.1 ? `${d < 10 ? d.toFixed(1) : Math.round(d)} people/km²` : 'unsettled') + (bits.length ? ': ' + bits.join(', ') : '');
      } };
  }
  if (layer === 'resources' && L.resource && S.V.resLeg) {
    const cnt = new Map(); let tot = 0;
    for (let i = 0; i < n; i++) { if (elev[i] <= 0) continue; tot++; if (L.resource[i]) cnt.set(L.resource[i], (cnt.get(L.resource[i]) || 0) + 1); }
    const rows = [...cnt.entries()].sort((a, b) => b[1] - a[1]);
    return { sum: `<div class="muted">most likely resource, share of the land</div>` + rows.slice(0, 7).map(([id, k]) => {
      const r = S.V.resLeg.resources[id - 1];
      return sumSw(r.color, `${esc(r.name)} <span class="muted">${share(k, tot)}</span>`);
    }).join('') + (rows.length > 7 ? `<div class="muted">+ ${rows.length - 7} more</div>` : ''),
      tip: (i) => { const id = L.resource[i], r = id ? S.V.resLeg.resources[id - 1] : null; return r ? `${r.name} ${(L['res_' + r.key]?.[i] || 0).toFixed(2)}` : 'none likely'; } };
  }
  if (layer === 'resource' && L.resource && S.V.resLeg) {
    const r = resInfo(state.res), a = r && L['res_' + r.key];
    if (!a) return null;
    let tot = 0, hi = 0, mid = 0, sum = 0;
    for (let i = 0; i < n; i++) { if (elev[i] <= 0) continue; tot++; sum += a[i]; if (a[i] >= 0.5) hi++; else if (a[i] >= 0.15) mid++; }
    return { sum: `<div class="muted">${esc(r.name)} likelihood, over the land (${mk(tot)})</div><div>likely (0.5+) <b>${mk(hi)}</b> <span class="muted">${share(hi, tot)}</span></div>` +
      `<div>possible (0.15 to 0.5) <b>${mk(mid)}</b> <span class="muted">${share(mid, tot)}</span></div><div class="muted">mean ${fmtNum(sum / tot)}</div>`,
      tip: (i) => `${r.name} ${fmtNum(a[i] || 0)}` };
  }
  if (layer === 'building stone' && L.stone && S.V.resLeg) {
    const cnt = new Map(); let tot = 0;
    for (let i = 0; i < n; i++) { if (elev[i] <= 0) continue; tot++; if (L.stone[i]) cnt.set(L.stone[i], (cnt.get(L.stone[i]) || 0) + 1); }
    const rows = [...cnt.entries()].sort((a, b) => b[1] - a[1]);
    return { sum: `<div class="muted">best stone exposed, share of the land</div>` + rows.slice(0, 7).map(([id, k]) => sumSw(S.V.resLeg.stone[id].color, `${esc(S.V.resLeg.stone[id].name)} <span class="muted">${share(k, tot)}</span>`)).join(''),
      tip: (i) => (L.stone[i] ? S.V.resLeg.stone[L.stone[i]].name : 'none') };
  }
  if (layer === 'coasts' && L.coast_type && S.V.coastLeg) {
    const km = Math.sqrt(cellMkm2 * 1e6), cnt = new Map();
    for (let i = 0; i < n; i++) if (L.coast_type[i]) cnt.set(L.coast_type[i], (cnt.get(L.coast_type[i]) || 0) + 1);
    return { sum: `<div class="muted">coastline by form</div>` + [...cnt.entries()].sort((a, b) => b[1] - a[1]).slice(0, 7).map(([id, k]) => {
      const e = S.V.coastLeg[id];
      return sumSw(e.color.slice(0, 7), `${esc(e.name)} <span class="muted">${Math.round(k * km / 1000).toLocaleString()}k km</span>`);
    }).join(''), tip: (i) => coastText(i) };
  }
  if (COAST_SCORES[layer] && L[COAST_SCORES[layer]]) {
    const a = L[COAST_SCORES[layer]]; let k = 0, hi = 0;
    for (let i = 0; i < n; i++) if (a[i] > 0) { k++; if (a[i] >= 0.5) hi++; }
    return { sum: `<div class="muted">cells with any: ${mk(k)}; 0.5 or more: ${mk(hi)}</div>`, tip: (i) => (a[i] > 0 ? fmtNum(a[i]) : 'none') };
  }
  return null;
}
function renderLayerSum() {
  const el = $('layerSum');
  if (!el) return;
  if (!S.V || !S.V.layers || state.playing) { if (!S.V) el.innerHTML = ''; return; }
  const layer = state.layer, L = S.V.layers, elev = L.elevation, n = S.V.n;
  let html = '';
  const cat = layerCats(layer), num = !cat && layerNumbers(layer), spec = !cat && !num && layerSpecial(layer);
  if (spec) html = spec.sum;
  else if (cat) {
    const cnt = new Map(); let tot = 0;
    for (let i = 0; i < n; i++) {
      if (cat.land && elev[i] <= 0) continue;
      const v = cat.arr[i]; if (cat.none === 0 && v === 0) continue;
      cnt.set(v, (cnt.get(v) || 0) + 1); tot++;
    }
    const rows = [...cnt.entries()].sort((a, b) => b[1] - a[1]);
    if (tot) html = `<div class="muted">share of the land</div>` + rows.slice(0, 7).map(([v, k]) =>
      `<div><span class="swatch" style="display:inline-block;width:9px;height:9px;background:${v === cat.none ? '#555' : cat.colors[v] || '#888'};margin-right:5px"></span>${esc(v === cat.none ? cat.noneName || 'none' : cat.names[v] || '?')} <span class="muted">${(100 * k / tot).toFixed(1)}%</span></div>`).join('') +
      (rows.length > 7 ? `<div class="muted">+ ${rows.length - 7} more</div>` : '');
  } else if (num) {
    const vals = [], stride = Math.max(1, Math.floor(n / 30000));
    for (let i = 0; i < n; i += stride) {
      if (num.where === 'land' && elev[i] <= 0 || num.where === 'sea' && elev[i] > 0) continue;
      const v = Number(num.arr[i]); if (Number.isFinite(v)) vals.push(v);
    }
    vals.sort((a, b) => a - b);
    if (vals.length) {
      const q = (f) => vals[Math.min(vals.length - 1, Math.floor(f * vals.length))], mean = vals.reduce((a, b) => a + b, 0) / vals.length;
      const unit = esc(String(UNITS[layer] || '').split(/[,(]/)[0]);
      html = `<div class="muted">over ${num.where === 'sea' ? 'the sea' : num.where === 'all' ? 'the whole planet' : 'the land'}${unit ? ` (${unit})` : ''}</div>` +
        `<div>mean <b>${fmtNum(mean)}</b> · median ${fmtNum(q(0.5))}</div><div class="muted">10% below ${fmtNum(q(0.1))} · 90% below ${fmtNum(q(0.9))} · range ${fmtNum(vals[0])} to ${fmtNum(vals[vals.length - 1])}</div>`;
    }
  }
  el.innerHTML = html ? `<hr style="border:0;border-top:1px solid var(--border);margin:6px 0"><b>${esc(layer)}</b>${html}` : '';
}
// the tooltip: the colour layer's value under the pointer first, then place and height
const tipEl = document.createElement('div');
tipEl.style.cssText = 'position:fixed;z-index:30;pointer-events:none;display:none;max-width:260px;padding:5px 8px;border-radius:6px;font-size:12px;line-height:1.35;background:rgba(14,19,30,0.94);border:1px solid var(--border);color:var(--text, #e6edf3)';
document.body.append(tipEl);
let tipXY = [0, 0];
addEventListener('pointermove', (e) => { tipXY = [e.clientX, e.clientY]; if (tipEl.style.display !== 'none') placeTip(); }, true);
function placeTip() { const w = tipEl.offsetWidth; tipEl.style.left = Math.min(innerWidth - w - 8, tipXY[0] + 14) + 'px'; tipEl.style.top = Math.min(innerHeight - tipEl.offsetHeight - 8, tipXY[1] + 14) + 'px'; }
function tipHtml(i) {
  const layer = state.layer, L = S.V.layers, G = S.V.grid, land = L.elevation[i] > 0;
  const cat = layerCats(layer), num = !cat && layerNumbers(layer);
  let main = '';
  if (cat) { const v = cat.arr[i]; main = v === cat.none ? (cat.noneName || 'none') : cat.names[v] || '?'; }
  else if (num) { const v = Number(num.arr[i]); if (Number.isFinite(v)) main = `${fmtNum(v)} ${String(UNITS[layer] || '').split(/[,(:]/)[0].replace(/^class$/, '')}`; }
  else if (layer === 'fuels' && fuelSrc()) { const t = []; fuelRows(i, (g, k, v) => t.push(v)); main = t.join(''); }
  else { const sp = layerSpecial(layer); if (sp) main = sp.tip(i); }
  return `<b>${esc(layer)}</b>${main ? ': ' + esc(main) : ''}<br><span class="muted">${land ? '' : 'sea, '}${L.elevation[i]} m · ${G.lat[i].toFixed(1)}°, ${G.lon[i].toFixed(1)}°</span>`;
}
export function renderTip() {
  if (!S.V || S.hovered < 0 || !S.V.layers) { tipEl.style.display = 'none'; return; }
  try { tipEl.innerHTML = tipHtml(S.hovered); } catch (e) { tipEl.style.display = 'none'; return; }
  tipEl.style.display = 'block'; placeTip();
}
export function renderLegend() {
  try { renderLayerSum(); } catch (e) { console.error(e); }
  const el = $('legend');
  const ov = obsView(state.layer);
  // the model / observed / difference switch: only for an Earth world's temperature, rainfall, climate and sunshine
  $('obsSeg').style.display = S.V.kind === 'world' && S.V.layers.obs_temperature && OBS_LAYERS[state.layer] ? '' : 'none';
  // (a run's seasonal layers download when a season is picked: the picker shows if the run has them)
  const sk = SEASONAL[state.layer] && SEASONAL[state.layer] + '_jul';
  $('seasonRow').style.display = sk && (S.V.layers[sk] || (S.V.kind === 'run' && S.V.run.layers[sk])) && !ov ? '' : 'none';
  $('pftRow').style.display = state.layer === 'plant type' && S.V.pfts?.length ? '' : 'none';
  $('resRow').style.display = state.layer === 'resource' && S.V.resLeg ? '' : 'none';
  $('techRow').style.display = state.layer === 'technology' && techTree() ? '' : 'none';
  drawMarks();  // (the plant groups' ticks come and go with the vegetation views)
  const sw = (color, text) => `<span><span class="sw" style="background:${color}"></span>${text}</span>`;
  if (ov && ov.diff && state.layer === 'climate') {
    el.innerHTML = sw('#3fae5a', 'same class') + sw('#e8c547', 'same group (A, B, C, D or E), another class') +
      sw('#d0453a', 'another group') + sw('#4a4f57', 'no observation') + '<span class="muted">(model vs Kottek et al. 2006 Köppen)</span>';
  } else if (ov && ov.diff && state.layer === 'temperature') {
    el.innerHTML = rampLegend('temperature difference', UNITS['temperature difference']) +
      '<span class="muted">observed: NCEP/NCAR 2 m air, 1981–2010</span>';
  } else if (ov && ov.diff && state.layer === 'sunshine') {
    el.innerHTML = rampLegend('sunshine difference', 'h of sunshine a day, model minus observed') +
      '<span class="muted">observed: CRU CL 2.0 sunshine, 1961–90 (land)</span>';
  } else if (ov && ov.diff) {
    el.innerHTML = rampLegend('rainfall ratio', 'model ÷ observed rainfall', ['¼×', '4×']) +
      '<span class="muted">observed: GPCC (land), GPCP where GPCC has none</span>';
  } else if (state.layer === 'technology' && techTree()) {
    const tt = techTree(), id = techId(), f = tt.firsts[id], now = -S.V.t, lines = S.V.run.meta.lineages || [];
    const knew = lines.filter((l) => (tt.known[l.id]?.[id]?.[0] ?? -1) >= now - 1e-9).length;
    el.innerHTML = `<b>${esc(techName(id))}</b>` + (state.techCol === 'when'
      ? `<span>new</span><span class="sw" style="width:70px;background:linear-gradient(90deg,#ffeca0,#d64828)"></span><span>long known</span>`
      : Object.keys(TECH_HOW).map((h) => sw(TECH_HOW[h], TECH_HOW_TEXT[h])).join('')) + sw('#464e5a', 'not yet') + sw('#2a2e28', 'nobody') +
      `<span class="muted">${knew} peoples know it by ${now <= 0 ? 'the present' : agoLabel(S.V.t)}; first: ${f ? `${esc((lines.find((l) => l.id === f.line)?.name || f.line).split(' (')[0])}, ${agoLabel(-f.ago_kyr)} (${esc(techHowText(f.how))})` : 'nobody'}. Stars: inventions, tamings, kits; arrows: giver to taker${techOldest(id) > -S.V.run.frames[0].t ? `; older events are drawn on the ranges of the first stored moment (${agoLabel(S.V.run.frames[0].t)})` : ''}.</span>`;
  } else if (state.layer.startsWith('body: ')) {
    el.innerHTML = rampLegend('body', `% of the cell's people with it (${state.layer.slice(6)}: each people's share, mixed by who lives there)`, ['0%', '100%']) + sw('#5a5a52', 'nobody');
  } else if (state.layer === 'demes') {
    // the regional populations of this frame (planet/lineages/demes.py, PW-981), the largest first
    const L = S.V.layers, D = S.V.demes?.demes || [], cnt = new Map();
    if (L.demes) for (let i = 0; i < S.V.n; i++) { const d = L.demes[i]; if (d !== 65535) cnt.set(d, (cnt.get(d) || 0) + 1); }
    const rows = [...cnt.entries()].filter(([d]) => D[d]).sort((a, b) => b[1] - a[1]);
    el.innerHTML = rows.slice(0, 14).map(([d]) => sw(D[d].color, esc(D[d].name))).join('') + (rows.length > 14 ? `<span class="muted">+ ${rows.length - 14} more</span>` : '') +
      sw('#5a5a52', 'nobody') + `<span class="muted">${rows.length} regional populations of the leading peoples here: cut where sea, hard country or distance part a people (each a shade of its people's colour); ${S.V.demes ? `cut since ${S.V.demes.from_kyr} kyr ago` : 'loading the tree…'}</span>`;
  } else if (state.layer === 'peoples' || state.layer === 'peoples mix' || state.layer === 'peoples overlay' || state.layer === 'peoples blend') {
    // the peoples present in this frame (planet/lineages/), by the land they lead
    const L = S.V.layers, lines = S.V.run.meta.lineages || [], cnt = new Map();
    if (state.layer === 'peoples overlay') {  // (it fell through to the ramp legend, which threw: PW-679)
      const ov = L.peoples_overlay;
      for (let i = 0; i < S.V.n; i++) { const d = ov ? ov[i] : 255; if (d !== 255 && lines[d]) cnt.set(d, (cnt.get(d) || 0) + 1); }
      el.innerHTML = [...cnt.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => sw(lines[d].color, esc(lines[d].name))).join('') +
        '<span class="muted">templates and contact hybrids; elsewhere the leading people</span>';
    } else if (state.layer === 'peoples mix') el.innerHTML = [1, 2, 3, 4].map((m) => sw(`hsl(${(0.75 - 0.12 * m) * 360},70%,${35 + 6 * m}%)`, m === 4 ? '4+ peoples' : `${m}`)).join('') + sw('#5a5a52', 'nobody');
    else {
      for (let i = 0; i < S.V.n; i++) { const d = L.peoples ? peoplesIdx(i) : null; if (d != null && d !== 255) cnt.set(d, (cnt.get(d) || 0) + 1); }
      el.innerHTML = [...cnt.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => sw(lines[d]?.color || '#888', esc(lines[d]?.name || d) + (isSeaPeople(lines[d]) ? ' (at sea)' : ''))).join('') +
        sw('#5a5a52', 'nobody') + (state.layer === 'peoples blend' ? '<span class="muted">(each cell blends its leading people\'s colour, the second\'s and grey for all the others, by their shares)</span>' : '<span class="muted">(whitened: mixed)</span>');
    }
  } else if (state.layer.startsWith('animal: ')) {
    const id = state.layer.slice(8), h = animalStocks()[id], t = h?.tamed?.[0];
    el.innerHTML = sw('#3f9d4a', `wild range of ${h?.label || id} (from the land)`) + sw(ANIMAL_COLS[(h?.bit || 0) % 8], 'tamed and known') +
      `<span class="muted">${h?.fantasy ? `fantasy animal (${S.V.run.meta.mode} mode); ` : ''}${t ? `tamed ~${t.ago_kyr} kyr ago by the ${esc(t.people)} on the ${esc(t.country)} of ${esc(t.landmass_name)} (${t.lat}, ${t.lon})` : h ? 'never tamed on this world: ' + esc(h.never || '') : ''}${h && h.tamed.length > 1 ? `; again, on its own: ${h.tamed.slice(1).map((x) => `${esc(x.people)}, ~${x.ago_kyr} kyr ago`).join('; ')}` : ''}${h && h.crossed ? `; carried over the sea ${h.crossed} times` : ''}</span>`;
  } else if (state.layer.startsWith('crop: ')) {
    const id = state.layer.slice(6), h = cropStocks()[id], t = h?.tamed?.[0];
    el.innerHTML = sw('#3f9d4a', `wild range of ${h?.label || id} (from the land)`) + sw(CROP_COLS[(h?.bit || 0) % CROP_COLS.length], 'cultivated and known') +
      `<span class="muted">${h?.fantasy ? `fantasy crop (${S.V.run.meta.mode} mode); ` : ''}${t ? `first cultivated ~${t.ago_kyr} kyr ago by the ${esc(t.people)} on ${esc(t.landmass_name)} (${t.lat}, ${t.lon})` : h ? 'never cultivated on this world: ' + esc(h.never || '') : ''}${h && h.tamed.length > 1 ? `; again, on its own: ${h.tamed.slice(1).map((x) => `${esc(x.people)}, ~${x.ago_kyr} kyr ago`).join('; ')}` : ''}${h && h.crossed ? `; carried over the sea ${h.crossed} times` : ''}</span>`;
  } else if (state.layer === 'fuels') {
    const F = S.V.kind === 'world' ? S.V.wAnthroRun.fuels : S.V.run.meta.fuels;
    el.innerHTML = F.names.map((k) => sw(F.colors[k], F.phrases[k])).join('') + sw('#5a5a52', 'nobody') +
      `<span class="muted">${S.V.kind === 'world' ? `the leading fuel of peoples run ${S.V.wAnthroRun.id}, paler where it is a smaller share (the 'fuel' layer is the land's firewood score, 0-5)` : anthroOn() ? 'the leading fuel at the present, paler where it is a smaller share' : 'step to the last frame (the present) to see it'}</span>`;
  } else if (state.layer === 'land use') {
    el.innerHTML = rampLegend('tree cover', '% wild tree cover (the land as it was)') + sw('#f0b429', 'cropland') + sw('#b9d36a', 'pasture') +
      sw('#c98a3c', 'burned grassland') + sw('#2d6a4a', 'managed woods') + sw('#9c3b2a', 'densely settled (6+ people/km²)') +
      `<span class="muted">${anthroOn() ? 'the present, from the peoples and their ways of life' : 'step to the last frame (the present) to see it'}</span>`;
  } else if (state.layer === 'vegetation') {
    // the named types present, grouped (forest, savanna, desert, ...), with their share of the land
    const L = S.V.layers, cnt = new Map();
    let land = 0;
    for (let i = 0; i < S.V.n; i++) if (L.elevation[i] > 0) { cnt.set(L.vegetation[i], (cnt.get(L.vegetation[i]) || 0) + 1); land++; }
    const groups = [];
    for (const t of S.V.vegTypes) if (cnt.has(t.id) && t.id > 0) {
      if (!groups.length || groups[groups.length - 1][0] !== t.group) groups.push([t.group, []]);
      groups[groups.length - 1][1].push(t);
    }
    const share = (k) => 100 * cnt.get(k) / land, pct = (k) => (share(k) < 1 ? share(k).toFixed(1) : share(k).toFixed(0));
    // the types covering at least 0.5% of the land, by group; the rest only counted (hover a cell for them)
    let rare = 0;
    el.innerHTML = groups.map(([g, ts]) => {
      const big = ts.filter((t) => share(t.id) >= 0.5 || t.id >= 57);
      rare += ts.length - big.length;
      return big.length ? `<span><b class="muted" style="font-weight:600">${g}:</b></span>` +
        big.map((t) => `<span title="${esc(t.text || t.name)}">${sw(t.color, '')}${t.name} ${pct(t.id)}%</span>`).join('') : '';
    }).join('') + `<span class="muted">(named vegetation types, % of land${rare ? `; ${rare} rarer types not listed` : ''})</span>`;
  } else if (state.layer === 'soils') {
    // the soil types present with their share of the land
    const L = S.V.layers, cnt = new Map();
    let land = 0;
    for (let i = 0; i < S.V.n; i++) if (L.elevation[i] > 0) { cnt.set(L.soil[i], (cnt.get(L.soil[i]) || 0) + 1); land++; }
    el.innerHTML = S.V.soilTypes.filter((t) => cnt.has(t.id)).map((t) => {
      const p = 100 * cnt.get(t.id) / land;
      return `<span title="${esc(`${t.wrb} / ${t.usda}: ${t.desc}`)}">${sw(t.color, '')}${t.name} ${p < 1 ? p.toFixed(1) : p.toFixed(0)}%</span>`;
    }).join('') + '<span class="muted">(soil types, % of land; hover a type for its WRB / USDA name)</span>';
  } else if (state.layer === 'coastal life') {
    const L = S.V.layers, cell = 4 * Math.PI * 6371 ** 2 / S.V.n / 100;
    const km2 = (k) => { let t = 0; for (let i = 0; i < S.V.n; i++) t += L[k][i]; return t * cell; };
    el.innerHTML = COASTAL.map(([k, n, c]) => sw(c, `${n} ${Math.round(km2(k)).toLocaleString()} km²`)).join('') +
      `<span class="muted">(${UNITS['coastal life']}; reefs, kelp, seagrass at sea, mangroves and salt marsh between the tides; hover a cell for its shares)</span>`;
  } else if (state.layer === 'satellite') {
    el.innerHTML = `<span>${seasonUnits('satellite')}: plants by type and season, bare ground, snow, ice, lakes and sea</span>` +
      '<span class="muted">(satellite.py; season picker: year = each hemisphere\'s summer; tick Clouds under Overlays)</span>';
  } else if (state.layer === 'plant type') {
    const p = S.V.pfts.find((q) => q.code === state.pft);
    el.innerHTML = `<div><div class="grad" style="background:linear-gradient(90deg,#6b675f,${p?.color || '#fff'})"></div>
      <div class="row" style="justify-content:space-between;width:260px"><span>0</span><span class="muted">% cover</span><span>100</span></div></div>
      <span>${p ? `${p.code}: ${esc(p.name)}` : '?'}</span><span class="muted">(${p ? 'its group: ' + esc(p.group) : ''})</span>`;
  } else if (state.layer === 'biome') {
    const present = new Set(S.V.layers.biome);
    el.innerHTML = S.V.biomes.filter((b) => present.has(b.id) && !(b.name === 'lake' && S.V.layers.lake_kind))
      .map((b) => `<span><span class="sw" style="background:${b.color}"></span>${b.name}</span>`).join('');
  } else if (state.layer === 'rock type' || state.layer === 'surface rock') {
    const surf = state.layer === 'surface rock';
    const present = new Set(surf ? S.V.layers.surface_rock : S.V.layers.rock);
    el.innerHTML = S.V.rocks.filter((r) => present.has(r.id))
      .map((r) => `<span><span class="sw" style="background:${r.color}"></span>${r.name}</span>`).join('') +
      (surf ? '<span class="muted">(what you would walk on: sediment where it covers the basement; faded = under the sea)</span>'
            : '<span class="muted">(basement rock; faded = under the sea; see "sediment" for what covers it)</span>');
  } else if (state.layer === 'landforms') {
    const L = S.V.layers, cnt = new Map();
    let land = 0;
    for (let i = 0; i < S.V.n; i++) if (L.elevation[i] > 0 && L.landform[i]) { cnt.set(L.landform[i], (cnt.get(L.landform[i]) || 0) + 1); land++; }
    el.innerHTML = S.V.landforms.filter((f) => cnt.has(f.id))
      .map((f) => sw(f.color, `${f.name} ${(() => { const p = 100 * cnt.get(f.id) / land; return p < 1 ? p.toFixed(1) : p.toFixed(0); })()}%`)).join('') +
      '<span class="muted">(landform classes from each cell\'s geological record: rifting, folding, strata, eruptions; % of land)</span>';
  } else if (state.layer === 'climate') {
    const present = new Set(ov ? ov.obs : S.V.layers.climate);
    el.innerHTML = S.V.koppen.filter((k) => present.has(k.id) && k.code !== '-')
      .map((k) => `<span title="${k.name}"><span class="sw" style="background:${k.color}"></span>${k.code} ${k.name}</span>`).join('') +
      `<span class="muted">(Köppen climate classes${ov ? ', observed: Kottek et al. 2006; grey = no data' : ''})</span>`;
  } else if (RES_LAYERS.has(state.layer)) {
    el.innerHTML = resLegend(state.layer, sw);
  } else if (COAST_LAYERS.has(state.layer)) {
    el.innerHTML = coastLegend(state.layer, sw);
  } else if (HU_LAYERS[state.layer]) {
    const k = HU_LAYERS[state.layer];
    el.innerHTML = huSwatches(k) + `<span class="muted">(${{ river_nav: 'ribbons follow the rivers; also under Overlays', harbour: 'diamonds mark them; also under Overlays',
      pass: 'bow-ties mark the saddle cells; also under Overlays', fertile: 'soil, water, growing season and slope', fresh_water: 'nearest perennial stream, lake, wetland or spring' }[k]}; hover a cell for details)</span>`;
  } else if (state.layer === 'plates') {
    el.innerHTML = `<span>Each colour = one plate (bright = continental crust, dark = oceanic)</span>
      <span><span class="sw" style="background:#ff3b3b"></span>converging boundary</span>
      <span><span class="sw" style="background:#3bf0ff"></span>diverging boundary</span>`;
  } else {
    el.innerHTML = rampLegend(state.layer, seasonUnits(state.layer) + (ov ? ' (observed)' : '')) +
      (state.layer === 'crust age' ? '<div class="muted">continents: age of the rock since it last formed or was remade <span class="sw" style="background:#f2e6d0"></span>0 <span class="sw" style="background:#a87d5a"></span>1 Gyr <span class="sw" style="background:#3a2a22"></span>3.5 Gyr</div>' : '') +
      (state.layer === 'dew point' ? '<span class="muted">(above ~20 °C feels muggy)</span>' : '') +
      (state.layer === 'elevation' && S.V.tz ? '<span class="muted">(ice surface included; heights above that moment\'s sea level)</span>' : '');
  }
  if (LAKE_LAYERS.has(state.layer) && !ov && (S.V.layers.lake_kind || S.V.layers.lake)) {
    const kinds = new Set();
    for (let i = 0; i < S.V.n; i++) kinds.add(lakeKind(i));
    el.innerHTML += Object.entries(LAKE_KINDS).filter(([k]) => kinds.has(+k)).map(([, [name, c]]) => sw(c, name)).join('');
  }
  if (S.V.kind === 'run' && $('events').checked) {  // the kinds of event this run has
    const kinds = [...new Set(S.V.run.events.map((e) => e.kind))];
    el.innerHTML += kinds.map((k) => sw(hexColor(EVENT_COLORS[k] || 0xffffff), k)).join('');
  }
  for (const k of Object.keys(HU_OVERLAY))  // overlays of the human-use layers not already the layer's own legend
    if (S.V.humanUse?.[k] && S.V.layers[k] && $(HU_OVERLAY[k]).checked && HU_LAYERS[state.layer] !== k) el.innerHTML += huSwatches(k);
  if ($('hotspots').checked && S.V.hotspots?.length)
    el.innerHTML += '<span><span class="sw" style="background:#ff9f1c"></span>hotspot</span>';
  if ($('volcanoes').checked && S.V.volcanoes?.length) {
    const has = (f) => S.V.volcanoes.some(f);
    if (has((v) => !v[2] && (v[3] || 0) !== 2)) el.innerHTML += '<span><span class="sw" style="background:#ff2d2d"></span>arc volcano</span>';
    if (has((v) => v[2] === 1 && v[3] !== 2)) el.innerHTML += '<span><span class="sw" style="background:#ffb347"></span>hotspot volcano</span>';
    if (has((v) => v[3] === 2)) el.innerHTML += '<span><span class="sw" style="background:#5ff0e6"></span>atoll</span>';
    if (has((v) => v[3] === 3)) el.innerHTML += '<span title="A hotspot volcano carried off its plume but still over the plume\'s head (within 150 km): quiet, but it can erupt again"><span class="sw" style="background:#ffe14d"></span>dormant volcano</span>';
    if ($('volcExtinct').checked && has((v) => v[3] === 4)) el.innerHTML += '<span><span class="sw" style="background:#b08d6a"></span>extinct volcano</span>';
  }
  if (worldAnthroOn() && WORLD_TINTED.has(state.layer))
    el.innerHTML += sw('#f0b429', 'cropland') + sw('#b9d36a', 'pasture') + sw('#c98a3c', 'burned grass') + sw('#2d6a4a', 'managed woods') +
      `<span class="muted">(cleared land of peoples run ${S.V.wAnthroRun.id}, tinted over the wild colours)</span>`;
  if ($('winds').checked && S.V.layers.wind_e)
    el.innerHTML += `<span><span class="sw" style="background:#ffe08a"></span>wind${
      { wind_jul: ' (July)', wind_jan: ' (January)' }[windKey()] || ''}</span>`;
  if ($('currents').checked && S.V.layers.current_e)
    el.innerHTML += '<span><span class="sw" style="background:linear-gradient(90deg,#1f6f78,#b4fff0)"></span>ocean current (slow → fast)</span>';
  if ($('overturning').checked && S.V.kind === 'world' && S.V.meta.overturning)
    el.innerHTML += sw('#bfe0ff', '⊗ deep water sinks (Sv)') + sw('#ff8a3a', 'warm inflow (model)') +
      sw('#7f9fff', '- - deep return (schematic)') + sw('#5ff0c8', '◎ wells up');
}

// what each colour layer shows (the button's hover hint; the units from UNITS are added)
const LAYER_HINTS = {
  satellite: 'True colour, as seen from space: plants, bare ground, snow and sea, by season.',
  biome: 'Biome class from the climate (worlds without the vegetation model).',
  elevation: 'Height above sea level; sea floor depth below it. Lakes cyan (fresh) and pink (salt), ice white.',
  plates: 'Tectonic plates (light: continental crust, dark: oceanic); red converging and cyan diverging boundaries.',
  'crust age': 'Age of the sea floor since it formed at a ridge (continents: age of their rock).',
  'bed under ice': 'The ground with the ice taken off, pressed down by its load.',
  'ice thickness': 'Thickness of the land ice.',
  'surface rock': 'The rock exposed at the surface (the top stratum of the rock record).',
  'rock type': 'The bulk rock of the crust.',
  'crust thickness': 'Thickness of the crust (continents ~35 km, ocean floor ~7 km).',
  sediment: 'Thickness of sediment on top of the basement rock.',
  rainfall: 'Precipitation (rain and snow as water).', precipitation: 'Precipitation (rain and snow as water).',
  temperature: 'Air temperature near the ground.',
  climate: 'Köppen climate classes (A tropical, B dry, C temperate, D continental, E polar).',
  landforms: 'Landform classes: what shaped the ground here (folds, rifts, volcanoes, plains, glacial forms...).',
  vegetation: 'Vegetation types from the mix of plant functional types that grow in this climate.',
  'tree cover': 'Tree canopy cover: the share of the ground under tree crowns.',
  fuels: 'Peoples runs, at the present: what each cell burns to cook and heat (wood, charcoal, dung, peat, straw, grass, driftwood, coal), from the trees left, the herds, the peat, the crops and the coal (planet/lineages/fuels.py).',
  technology: 'Peoples runs with a technology tree: where one tech (picked under the layers) was known at this moment. Each people\'s land is lit when it knew it by then, in the colour of how it came (or how long it was known); grey: not yet. Stars: inventions; arrows: giver to taker (planet/lineages/techtree.py).',
  'land use': 'Peoples runs, at the present: cropland, pasture, burned grassland and managed woods around the peoples there, settlement density in red (planet/lineages/landuse.py).',
  'plant cover': 'Plant cover: the share of the ground shaded by plants of any kind.',
  'canopy height': 'Height of the tallest plant layer.',
  'leaf area': 'Leaf area index (LAI): m² of leaf per m² of ground (0 bare, 1-2 grassland, 4-6 dense forest).',
  NPP: 'Net primary productivity: the carbon plants fix by photosynthesis in a year, less what they respire themselves, in g C/m²/yr (grams of carbon per m² of ground per year). Earth: rainforest ~800-1000, desert < 100.',
  biomass: 'Carbon in living plants, in t C/ha (tonnes of carbon per hectare).',
  'fire return': 'Fire return interval: the mean number of years between fires.',
  'stand age': 'Years since the last stand-replacing fire.',
  'plant type': 'Cover of one plant functional type (PFT; pick it below).',
  soils: 'Soil types, from parent rock, slope, surface age, climate, plants and wind-blown silt (WRB groups with player names).',
  'soil depth': 'Rootable soil above rock: thin on steep, young or wind-scoured ground, deep on old plains and soft deposits.',
  'soil water': 'Water the soil holds for plants down to 1.5 m (available water capacity).',
  fertility: 'Nutrient and base status: rich on young ash, loess and alluvium, poor where old soils are leached.',
  'soil carbon': 'Organic carbon in the top metre of soil, peat included.',
  peat: 'Peat thickness, where peat lies (waterlogged ground where plant remains pile up).',
  permafrost: 'Permanently frozen ground: sporadic, discontinuous or continuous.',
  loess: 'Wind-blown silt, from deserts and glacier margins, laid down downwind.',
  'river floods': 'How seasonal the rivers are: the peak month over the mean month.',
  travel: 'How slow walking is, off roads in the snow-free season: stems and undergrowth, wet ground and bogs, deadfall in old forest, rough or steep ground (gameattrs.py).',
  sightline: 'How far you can see at eye level through the plants: tens of metres in forest, to the horizon on open ground.',
  grazing: 'Pasture for herds: the herb layer\'s growth plus browse from shrubs, less where the ground is frozen or snowed in.',
  foraging: 'Wild food for people: mast and fruit trees, game, wetlands (waterfowl, wild grain, roots) and river fish.',
  timber: 'Building timber: woody biomass and height; straight conifers score higher.',
  fuel: 'Firewood and fuel: wood, shrubs, cut peat from bogs, dung on pasture.',
  'building ground': 'How good the ground is to build on: firm rock or gravel best; loose sand, soft clay, loess, waterlogged ground, salt, swelling clay, peat, permafrost and slopes worse.',
  'mud season': 'Months the ground turns to mud: wet, thawed months on clay, silt or poorly drained soil, and the summer thaw over permafrost.',
  'fire season': 'Months of fire weather (dry litter, warm, no snow), where the place burns at all.',
  'green season': 'Months the plants are in leaf and free of snow (each plant type\'s leaf habit, weighted by its cover).',
  'navigable rivers': 'Rivers by what can float on them: small boats, barges, sea-going ships (depth from the mean discharge, rapids, months frozen).',
  harbours: 'Natural harbours at the coast: sheltered, deep water, or an estuary (anchorage, harbour, fine harbour).',
  passes: 'The lowest crossings of divides between drainage basins separated by real relief, by the months they are open.',
  farmland: 'Farmland quality from soil fertility and depth, water, growing season and slope, less permafrost, peat and flooding.',
  'fresh water': 'How far perennial fresh water is: on site, close by, a day or two away, or none within reach.',
  'wave power': 'Mean wave power per metre of wave crest (at sea).',
  'tide range': 'Tidal range: the height between high and low tide (at sea).',
  'sea temperature': 'Sea surface temperature.',
  salinity: 'Sea surface salinity in psu (practical salinity units, ≈ grams of salt per kg of sea water).',
  humidity: 'Relative humidity near the ground.', 'dew point': 'Dew point: the temperature at which the air would be saturated.',
  cloud: 'Cloud cover: the share of the sky covered.', sunshine: 'Hours of bright sunshine a day.',
  'coastal life': 'Coral reefs, kelp forests and seagrass on the shallow sea floor, mangroves and salt marsh between the tides: each cell in its biggest habitat\'s colour.',
  coasts: 'The form of each coast: ice fronts, fjords, deltas, mangrove and coral coasts, tidal flats, barrier islands, cliffs, rocky shores, beaches (planet/coastform.py).',
  'barrier islands': 'How likely the coast is fronted by barrier islands and lagoons: low land, a gentle shelf, waves and small tides.',
  cliffs: 'How likely the coast is cliffed: high or hard land under strong waves.',
  seabirds: 'How likely seabird colonies are: rich water nearby and cliffs or predator-free islands to nest on.',
  seals: 'How likely seals and sea lions haul out here: rich, cool water and rocky shores, island beaches or sea ice.',
  'sea hazards': 'Hazards to ships: coral reefs, shallow banks away from the coast, sea ice much of the year.',
  turbidity: 'River mud suspended in the sea (it takes the light reefs and seagrass need).',
  upwelling: 'Cold, nutrient-rich water welling up along coasts and the equator: how much it cools the sea.',
};
const HINT_HAS_UNITS = new Set(['NPP', 'biomass', 'leaf area', 'salinity', 'river floods', 'plant type']);
export function renderLayerButtons() {
  fillPfts();
  fillRes();
  fillTechs();
  const layers = availableLayers();
  if (!layers.includes(state.layer)) { state.wantLayer = state.layer; state.layer = layers[0]; }  // (wantLayer: a layer that arrives later, like a world's fuels, PW-845)
  $('layerSeg').innerHTML = layers.map((l) => `<button data-v="${l}" class="${l === state.layer ? 'on' : ''}"` +
    (LAYER_HINTS[l] ? ` title="${esc(LAYER_HINTS[l] + (UNITS[l] && !HINT_HAS_UNITS.has(l) ? ` Units: ${UNITS[l]}.` : ''))}"` : '') + `>${l}</button>`).join('');
  $('arrowsLbl').style.display = hasLayer('plate') && !S.V.tz ? '' : 'none';
  document.querySelectorAll('[data-needs]').forEach((e) => (e.style.display = hasLayer(e.dataset.needs) ? '' : 'none'));
  $('windYear').style.display = hasLayer('wind_jul_e') ? 'none' : '';  // the season picker says it instead
  document.body.classList.toggle('run', S.V.kind === 'run');
  document.querySelectorAll('.worldOnly').forEach((e) => (e.style.display = S.V.kind === 'world' ? '' : 'none'));
  document.querySelectorAll('.runOnly').forEach((e) => (e.style.display = S.V.kind === 'run' ? '' : 'none'));
  S.V.peopleTracks = S.V.run?.meta?.phase === 'lineages' ? S.V.run.meta.lineages : null;
  document.querySelectorAll('[data-needs-volc]').forEach((e) => (e.style.display = S.V[e.dataset.needsVolc]?.length ? '' : 'none'));
}

// Renaming a landmass (PW-886): click its name here, type, Enter; "reset" gives the generated name back. Saved by POST /api/names to the file
// `planet name` writes (worlds/names/<id>.json); the labels, this list and later peoples runs take it from there.
function landmassRows(s) {
  return s.landmasses.slice(0, 5).map((l, i) => S.lmEdit === i
    ? `<span class="lmEdit"><input id="lmInput" data-lm="${i}" value="${esc(l.name)}" maxlength="40" size="12"> <button data-lm-save="${i}">save</button> <button data-lm-reset="${i}" title="back to the generated name">reset</button> <button data-lm-cancel>cancel</button></span> ${l.pct_of_surface}%`
    : `<a href="#" class="lmName" data-lm-edit="${i}" title="rename this landmass">${esc(l.name)}</a> ${l.pct_of_surface}%`).join(', ');
}
async function saveLandmassName(i, name) {
  const letter = rankLetter(i);
  const r = await fetch('/api/names', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ world: S.V.id, letter, name }) });
  const d = await r.json();
  if (!r.ok) return toast(d.error || 'Could not save the name');
  d.names.forEach((n, k) => { if (S.V.summary.landmasses[k]) S.V.summary.landmasses[k].name = n.name; });
  S.lmEdit = -1;
  renderSummary(); buildLandmassNames();
}
document.addEventListener('click', (e) => {
  const t = e.target.closest?.('[data-lm-edit],[data-lm-save],[data-lm-reset],[data-lm-cancel]');
  if (!t || S.V?.kind !== 'world') return;
  e.preventDefault();
  if (t.dataset.lmEdit != null) { S.lmEdit = +t.dataset.lmEdit; renderSummary(); $('lmInput')?.focus(); $('lmInput')?.select(); }
  else if (t.dataset.lmSave != null) saveLandmassName(+t.dataset.lmSave, $('lmInput').value);
  else if (t.dataset.lmReset != null) saveLandmassName(+t.dataset.lmReset, '');
  else { S.lmEdit = -1; renderSummary(); }
});
document.addEventListener('keydown', (e) => {
  if (e.target.id !== 'lmInput') return;
  if (e.key === 'Enter') saveLandmassName(+e.target.dataset.lm, e.target.value);
  else if (e.key === 'Escape') { S.lmEdit = -1; renderSummary(); }
  e.stopPropagation();
});
export function renderSummary() {
  if (S.V.kind === 'run') return renderRunSummary();
  const m = S.V.meta, s = S.V.summary;
  let cmd;
  if (m.timezoom) cmd = `uv run python -m planet finish ${m.timezoom} --kyr ${m.timezoom_kyr}`;
  else if (m.source_run) cmd = `uv run python -m planet slice ${m.source_run} --at ${m.t_myr}`;
  else {
    const set = Object.entries(m.params).filter(([k]) => !['erosion_iterations', 'equator_temp', 'pole_temp', 'erosion'].includes(k));
    cmd = `uv run python -m planet generate -m ${m.method} -s ${m.seed} -l ${m.level}` +
      (m.params.erosion !== 1 ? ` --erosion ${m.params.erosion}` : '') +
      (set.length ? ' --set ' + set.map(([k, v]) => `${k}=${v}`).join(' ') : '');
  }
  if (m.remake) cmd = m.remake;  // e.g. the Earth reference world (tools/earth_world.py)
  $('sumTitle').textContent = 'World summary';
  $('summaryBody').innerHTML = `<b>${S.V.id || ''}</b> ${S.V.name} <span class="muted">· ${m.cells} cells · ~${m.cell_size_km} km each</span><br>
    ${m.timezoom ? `<span class="muted">Finished from</span> ${m.source_run === 'earth' ? "today's Earth" : sourceLink(m.source_run, m.t_myr)}
      <span class="muted">→</span> ${timezoomLink(m.timezoom, m.timezoom_kyr)}<br>
      <span class="muted">sea level ${m.sea_level_change_m > 0 ? '+' : ''}${Math.round(m.sea_level_change_m)} m vs the time zoom's start
      (${m.sea_level_m} m vs the run's reference level) · global mean ${m.global_temp_c} °C · land ice ${m.ice_volume_mkm3} M km³ · made ${m.created}</span><br>`
    : m.source_run ? `<span class="muted">From</span> ${sourceLink(m.source_run, m.t_myr)} <span class="muted">· made ${m.created}</span><br>` : ''}
    ${zoomsOf(S.V.id)}
    ${worldAnthroPanel()}
    ${m.observed ? `<span class="muted">The model's climate on real terrain; observed layers too: switch "model / observed / difference"
      under Colour by (temperature, precipitation, climate). Made ${m.created}.</span><br>` : ''}
    Land ${s.land_pct}% · peak ${s.highest_m.elevation} m · trench ${s.deepest_m.elevation} m<br>
    <span class="muted">Landmasses (click a name to rename it):</span> ${landmassRows(s)}<br>
    ${overturningLine(m.overturning)}
    <span class="muted">Remake:</span> <code>${cmd}</code>`;
}

// the overturning's strength and its main sinking sites (world meta, ocean.loop_schematic)
function overturningLine(o) {
  if (!o) return '';
  const ll = (s) => `${Math.abs(s.lat).toFixed(0)}°${s.lat >= 0 ? 'N' : 'S'} ${Math.abs(s.lon).toFixed(0)}°${s.lon >= 0 ? 'E' : 'W'}`;
  const sites = (o.sites || []).filter((s) => s.sv >= 0.3).sort((a, b) => b.sv - a.sv);
  return `<span title="Thermohaline overturning (ocean.py): deep water formed where the winter sea is densest. Tick &quot;Overturning&quot; under Overlays to see it.">` +
    `<span class="muted">Overturning:</span> ${o.sv.toFixed(1)} Sv sinking (north ${o.north_sv.toFixed(1)}, south ${o.south_sv.toFixed(1)})` +
    (sites.length ? `<span class="muted"> · </span>${sites.slice(0, 4).map((s) => `${ll(s)} ${s.sv.toFixed(1)}`).join(', ')}` : ' · no sinking site') +
    '</span><br>';
}

export function renderRunSummary() {
  const r = S.V.run, m = r.meta, f = r.frames[S.V.frame], s = f.stats;
  const win = eventWindow();
  const evs = r.events.map((e, idx) =>
    `<div class="ev ${Math.abs(e.t - S.V.t) <= win ? 'now' : ''}" data-t="${e.t}"><span class="tt">${e.t}</span><span style="color:${hexColor(EVENT_COLORS[e.kind] || 0xffffff)}">${e.kind}</span><span>${e.text}</span></div>`).join('');
  const head = S.V.tz ? timezoomSummary() : `<b>${r.id || ''}</b> ${r.name} <span class="muted">· ${m.cells} cells · made ${m.created}</span><br>
    t = ${S.V.t} Myr · ${s.plates} plates · land ${s.land_pct}% · ${s.landmasses} landmasses (largest ${s.largest_landmass_pct}%)<br>
    plate speed: mean ${s.mean_speed_cmyr}, max ${s.max_speed_cmyr} cm/yr · peak ${s.max_elev_m} m<br>
    ${s.global_temp_c != null ? `global mean ${s.global_temp_c} °C (Earth today ~14.5) · land ice ${s.ice_pct}% of surface · sea level ${s.sea_level_m} m<br>` : ''}
    ${finishMomentLine()}
    ${finishBox()}
    ${timezoomBox()}`;
  $('sumTitle').textContent = S.V.tz ? 'Time zoom and events' : 'Run and events';
  $('summaryBody').innerHTML = `${head}${S.V.tz ? '' : runTree()}
    <h2>Events <span class="muted">(click to jump${S.V.tz ? '; t in kyr' : ''})</span></h2><div id="evlist">${evs || '<span class="muted">none</span>'}</div>`;
  const now = $('summary').querySelector('.ev.now');
  if (now && state.playing) now.scrollIntoView({ block: 'nearest' });
}
