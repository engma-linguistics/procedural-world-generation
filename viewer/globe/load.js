import { S, state } from './state.js';
import { SEASONAL, layerNeeds } from './layers.js';
import { $, DIAG } from './scene.js';
import { loadDemes, techTellParent, worldAnthroLoad } from './colours.js';
import { buildTopology, paint, prepareGrid } from './geometry.js';
import { renderLayerButtons, renderRunSummary, renderSummary } from './panel.js';
import { timeLabel } from './timezoom.js';
import { drawAxis, timeAxis } from './timeaxis.js';
import { drawMarks, drawTint } from './provenance.js';
import { renderHover, toast } from './pick.js';
import { renderZoomBox } from './zoom.js';
import { navSync } from './tabs.js';
import { stop } from './playback.js';
import { esc } from '../planets.js';
import { applyPalette } from './palettes.js';
import { seaMask } from './landsea.js';
import { loadSettlements } from './settlements.js';
// ------------------------------------------------------------ latest wins (PW-1044)
// Opening a run or world takes several awaits; picking another meanwhile must not let the slower one land last.
let loadSeq = 0;
export const beginLoad = () => ++loadSeq;
const stale = (tok) => tok !== loadSeq;
// a JSON file the viewer must have, with a plain error when it isn't there (a missing run answers with the
// server's HTML 404 page, which JSON.parse turned into "Unexpected token '<'")
export class LoadError extends Error {}
async function needJSON(url, what) {
  let r;
  try { r = await fetch(url, { cache: 'no-cache' }); } catch { throw new LoadError(`The viewer's server did not answer while opening ${what}. Is planet serve still running?`); }
  if (r.status === 404) throw new LoadError(`There is no ${what}. It may have been deleted, or the link has a typo.`);
  if (!r.ok) throw new LoadError(`The server could not send ${what} (HTTP ${r.status}).`);
  try { return await r.json(); } catch { throw new LoadError(`${what[0].toUpperCase() + what.slice(1)} could not be read: its file is damaged or unfinished.`); }
}
// A level's grid is the same for every run and world on it: the last one asked for is kept, fetched and prepared
// once (prepareGrid), and a world's is asked for while the world itself downloads (select.js loadSelection). At L8
// that is ~0.6 s of fetching and parsing and ~0.3 s of preparing off each opening.
let gridMemo = { url: null, p: null };
export function gridOf(url, what) {
  const key = String(url);
  if (gridMemo.url !== key) {
    const p = needJSON(key, what).then((G) => ({ G, pg: prepareGrid(G) }));
    gridMemo = { url: key, p };
    p.catch(() => { if (gridMemo.p === p) gridMemo = { url: null, p: null }; });  // (a failed fetch is tried again next time)
  }
  return gridMemo.p;
}
// The error card (PW-1044): what failed in plain words, with the newest planets and the start page to go on from.
// Nothing half-built stays behind it, and Delete and the star are off while nothing is open.
export function loadFailed(err) {
  console.error(err);
  const plain = err instanceof LoadError ? err.message : `Something went wrong while opening this: ${err.message}`;
  let card = $('errCard');
  if (!card) { card = document.createElement('div'); card.id = 'errCard'; card.className = 'panel'; document.body.append(card); }
  const recent = [...(S.IDX.runs || []).map((r) => ({ when: r.created, href: `?run=${r.dir}`, label: `${r.name} (${r.kind === 'peoples' ? 'peoples' : r.kind === 'timezoom' ? 'time zoom' : 'run'})` })),
                  ...(S.IDX.worlds || []).map((w) => ({ when: w.created, href: `?world=${w.file}`, label: `${w.name} (world)` }))]
    .sort((a, b) => (b.when || '').localeCompare(a.when || '')).slice(0, 5);
  card.innerHTML = `<h3>Could not open this</h3><p>${esc(plain)}</p>
    ${recent.length ? `<div class="muted">Newest planets:</div><ul>${recent.map((x) => `<li><a href="${esc(x.href)}">${esc(x.label)}</a></li>`).join('')}</ul>` : ''}
    <p><a class="btn" href="./">Go to the start page</a></p>`;
  document.body.classList.add('failed');
  S.infoHtml = null; $('infoText').textContent = '';
  for (const id of ['delBtn', 'favBtn']) $(id).disabled = true;
}
function loadOk() {
  document.body.classList.remove('failed');
  $('errCard')?.remove();
  $('delBtn').disabled = false;
}
// "Loading <layer>…" while a picked layer or overlay is fetched and painted (PW-1044): the button lights at once,
// the picture follows
let busyN = 0;
const nextPaint = () => new Promise((ok) => requestAnimationFrame(() => setTimeout(ok, 0)));
function busy(on) {
  busyN = Math.max(0, busyN + (on ? 1 : -1));
  let el = $('busy');
  if (!el) { el = document.createElement('div'); el.id = 'busy'; el.setAttribute('role', 'status'); document.body.append(el); }
  el.textContent = `Loading ${state.layer}…`;
  document.body.classList.toggle('busy', busyN > 0);
}
// ------------------------------------------------------------ loading
// The legends (rock, Köppen and biome ids -> names and colours) come with every run and world.
function legendFields(leg) {
  return { rocks: leg.rocks, rockColors: leg.rocks.map((r) => r.color), koppen: leg.koppen,
           landforms: leg.landforms || [], landformColors: (leg.landforms || []).map((f) => f.color),
           koppenColors: leg.koppen.map((k) => k.color), biomes: leg.biomes, biomeColors: leg.biomes.map((b) => b.color),
           vegTypes: leg.vegetation?.types || [], vegColors: (leg.vegetation?.types || []).map((t) => t.color),
           pfts: leg.vegetation?.pfts || [], plantGroups: leg.vegetation?.groups || [],
           soilTypes: leg.soils?.types || [], soilColors: (leg.soils?.types || []).map((t) => t.color),
           soilTextures: leg.soils?.textures || [], soilDrainage: leg.soils?.drainage || [],
           soilPermafrost: leg.soils?.permafrost || [], humanUse: leg.human_use || {}, gameLeg: leg.game || null,
           resLeg: leg.resources || null,
           coastLeg: leg.coast || null };
}

// does the run (any of its layers, loaded or not) or the world have this layer?
export function hasLayer(k) { return S.V.kind === 'run' ? !!S.V.run.layers[k] : !!S.V.layers[k]; }

// A world file names its grid file ("../grids/L6.json", relative to worlds/),
// shared with the runs at that level.
export async function setWorld(w, tok = beginLoad()) {
  if (stale(tok)) return;
  stop(); S.picked = null; renderZoomBox();
  const { G, pg } = typeof w.grid === 'string' ? await gridOf(new URL(w.grid, new URL('../worlds/', location.href)), `the grid of world ${w.id || w.name}`)
    : { G: w.grid, pg: prepareGrid(w.grid) };
  if (stale(tok)) return;
  DIAG.mark('grid: parsed and prepared');
  // (the owner's names for the landmasses, planet name: they replace the summary's, so its lines and the labels agree)
  const nm = w.id ? await fetch(`/api/names?world=${w.id}`).then((r) => (r.ok ? r.json() : null)).catch(() => null) : null;  // (the server's: the owner's names, else the generated; PW-886)
  if (stale(tok)) return;
  DIAG.mark('names');
  (w.summary?.landmasses || []).forEach((m, i) => { const o = nm?.names?.[i]?.name; if (o) m.name = o; });
  S.lmEdit = -1;
  for (const k of ['humidity', 'dewpoint', 'cloud', 'sunshine'])  // the year's: the mean of the two half-years
    if (w.layers[k + '_jul'] && !w.layers[k]) w.layers[k] = w.layers[k + '_jul'].map((v, i) => (v + w.layers[k + '_jan'][i]) / 2);
  S.V = { kind: 'world', name: w.name, id: w.id, grid: G, n: pg.n, nc: pg.nc, cStart: pg.cStart, cList: pg.cList, U: pg.U, UC: pg.UC, layers: w.layers,
        meta: w.meta, summary: w.summary, pentagons: G.pentagons || w.meta.pentagons, level: w.meta.level,
        hotspots: w.meta.hotspots, volcanoes: worldVolcanoes(w.meta), volcTable: volcTable(w.meta), ...legendFields(w.legend) };
  landView(S.V.layers);
  DIAG.mark('world fields');
  document.title = `${w.name} · Planet Viewer`;
  renderLayerButtons(); renderSummary(); DIAG.mark('buttons, summary');
  buildTopology(); DIAG.mark('buildTopology');
  paint(); DIAG.mark('paint');
  navSync(); loadOk();
  worldAnthroLoad();  // (peoples change the land on a finished world, PW-669)
}

// ------------------------------------------------------------ run layers
// A run stores one file per layer, all frames in it (runs/<id>/layers/<name>.bin,
// frames x cells). run.json "layers" says, per layer, its file, dtype, shape and
// encoding: value = stored * scale + offset, then the transform if any
// ("log2p1": 2^value - 1; "nbr_slot": the stored number is the position of the
// target cell in the cell's neighbour list, 255 = none -> -1).
// Only the layers the picture needs are downloaded (layersNeeded), when needed.
const TYPED = { int16: Int16Array, uint8: Uint8Array, uint16: Uint16Array, uint32: Uint32Array, uint64: BigUint64Array, int8: Int8Array, float32: Float32Array };
// overlay -> the run layers it draws from (a colour layer's: layerNeeds, layers.js)
const OVERLAY_NEEDS = { rivers: ['flow', 'downstream'], winds: ['wind_e', 'wind_n', 'wind_jul_e', 'wind_jul_n', 'wind_jan_e', 'wind_jan_n'],
                        currents: ['current_e', 'current_n'],
                        arrows: ['plate'] };

function layersNeeded() {
  // elevation always; lake_kind too, so hovering any layer names the lake (its depth comes with the elevation layer);
  // ice, which says which cells are land (see landView)
  const want = ['elevation', 'lake_kind', 'ice', ...layerNeeds(state.layer)];  // (layers.js: each layer's needs)
  // a peoples run keeps all its peoples layers: switching between them (or away and back) refetched and
  // re-parsed 24 MB each time, and the hover card names the overlay peoples (PW-679)
  if (S.V.run.kind === 'peoples') want.push(...layerNeeds('peoples'), 'peoples_overlay', 'animal_wild', 'animal_known', 'crop_wild', 'crop_known', 'mix_lead', 'mix_lead_share', 'mix_second',
    'mix_second_share', 'mix_other_share', ...Object.keys(S.V.run.layers).filter((k) => k.startsWith('body_')));
  // the picked season's temperature or rain (runs since PW-138 store them)
  if (state.season && SEASONAL[state.layer]) want.push(`${SEASONAL[state.layer]}_${state.season}`);
  for (const [id, ks] of Object.entries(OVERLAY_NEEDS)) if ($(id).checked) want.push(...ks);
  return [...new Set(want)].filter((k) => S.V.run.layers[k]);
}

// Download what the current colour layer and overlays need, and drop the layers
// nothing draws any more (a run layer holds every keyframe: 40-80 MB each at L7;
// one picked again is fetched again, gzipped by the server). A no-op for worlds.
async function loadNeeded() {
  if (S.V?.kind !== 'run') return;
  const v = S.V, need = layersNeeded(), keep = new Set(need), want = need.filter((k) => !v.data[k]);
  const drop = [...new Set([...Object.keys(v.data), ...Object.keys(v.pending)])].filter((k) => !keep.has(k));
  for (const k of drop) { delete v.data[k]; delete v.pending[k]; delete v.bytes[k]; }
  if (drop.length && !want.length) return setFrame(S.V.frame, false);  // (V.layers mustn't read the dropped ones)
  if (!want.length) return;
  $('tlabel').textContent = `loading ${want.join(', ')}…`;
  await Promise.all(want.map(async (k) => {
    const p = v.pending[k] ||= fetch(v.base + v.run.layers[k].file, { cache: 'no-cache' }).then((r) => {
      if (!r.ok) throw new Error(`${v.run.layers[k].file}: HTTP ${r.status}`);
      return r.arrayBuffer();
    });
    const buf = await p;
    if (v.pending[k] !== p) return;  // dropped while it came (another layer picked meanwhile)
    v.data[k] = new TYPED[v.run.layers[k].dtype](buf);
    v.bytes[k] = buf.byteLength;
  }));
  if (S.V === v) setFrame(S.V.frame, false);  // rebuild V.layers with the new ones
}

// redraw after something that may need more layers (colour layer, overlay ticked)
export async function refresh(draw) {
  busy(true);
  try {
    await nextPaint();  // (so the pill shows before a long paint)
    try { await loadNeeded(); } catch (err) { toast(`Could not load that layer (${err.message})`); console.error(err); return; }
    draw();
  } finally { busy(false); }
}

// layer k of frame f in real units (see the encoding above)
function decodeFrame(k, f) {
  const s = S.V.run.layers[k], raw = S.V.data[k], n = S.V.n;
  const a = raw.length === n ? raw : raw.subarray(f * n, (f + 1) * n);  // stored once (shape [1, cells]): every frame
  if (s.transform === 'nbr_slot') {
    const out = new Int32Array(n), nbr = S.V.grid.nbr;
    for (let i = 0; i < n; i++) out[i] = a[i] === 255 ? -1 : nbr[i][a[i]];
    return out;
  }
  if (s.scale === 1 && !s.offset && !s.transform) return a;
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) out[i] = a[i] * s.scale + s.offset;
  if (s.transform === 'log2p1') for (let i = 0; i < n; i++) out[i] = 2 ** out[i] - 1;
  return out;
}

export async function loadRun(dir, wantT) {
  const tok = beginLoad();
  stop(); S.picked = null; renderZoomBox();
  const base = `../runs/${dir}/`;
  const run = await needJSON(base + 'run.json', `run "${dir}"`);
  if (stale(tok)) return;
  const { G: grid, pg } = await gridOf(new URL(run.grid, new URL(base, location.href)), `the grid of run "${dir}"`);
  if (stale(tok)) return;
  const tz = run.kind === 'timezoom' || run.kind === 'peoples';  // glacial time zoom or peoples run: time in kyr
  S.V = { kind: 'run', name: run.name, dir, base, run, data: {}, pending: {}, bytes: {}, grid, n: pg.n, nc: pg.nc, cStart: pg.cStart, cList: pg.cList, U: pg.U, UC: pg.UC,
        pentagons: grid.pentagons, level: grid.level, frame: 0, tz, tzEarth: tz && run.meta.source_run === 'earth',
        ...legendFields(run.legend) };
  document.title = `${run.name} · Planet Viewer`;
  S.V.axis = timeAxis(run); drawAxis();  // (the slider's dated axis, PW-1042)
  let f = 0;
  if (wantT == null && !tz && run.meta.finish_moment) wantT = run.meta.finish_moment.t;  // (PW-866: open at the finish moment)
  if (wantT == null && run.kind === 'peoples') wantT = run.frames.at(-1).t;  // (a peoples run opens at the present, PW-1028)
  if (wantT != null) f = run.frames.reduce((b, fr, i) => (Math.abs(fr.t - wantT) < Math.abs(run.frames[b].t - wantT) ? i : b), 0);
  S.V.frame = f;
  renderLayerButtons();  // settles state.layer, which says what to load
  await loadDemes();
  await loadSettlements();  // (the settlement ledger, PW-1011)
  if (stale(tok)) return;
  await loadNeeded();
  if (stale(tok)) return;
  applyPalette(S.V);  // (family hues, neighbours told apart, PW-1032)
  setFrame(f, false);
  buildTopology(); paint(); renderRunSummary(); drawTint(); drawMarks();
  navSync(); loadOk();
}

// A world's volcano table (tectonics.volcanism.COLUMNS) -> [lat, lon, kind, mark]
// for the overlay: the active and dormant ones, extinct hotspot islands and
// atolls; the many other extinct ones (seamounts, guyots, dead arc cones, old
// calderas) only with "extinct ones too".
// mark: 0 active, 1 extinct island, 2 atoll (a living reef round a sunken volcano), 3 dormant, 4 other extinct
function worldVolcanoes(meta) {
  const out = [];
  for (const v of volcTable(meta)) {
    const m = v.status === 'active' ? 0 : v.status === 'dormant' ? 3 : v.kind === 1 && v.top_m > 0 ? 1
      : v.top_m <= 0 && v.reef === 1 ? 2 : 4;
    out.push([v.lat, v.lon, v.kind, m]);
  }
  return out;
}
// The volcano table as objects, each with its status as zoom.volcanoes.status (keep the two alike):
// active: fed now (a hotspot vent over its plume, an arc volcano within its life); dormant: a hotspot
// vent off its plume's centre but within DORMANT_KM (the plume's head, volcanism.PLUME_KM) of a live
// plume, so it can erupt again; else extinct. The run has Myr steps, no eruptions: it can't tell a
// volcano that erupted last year from one quiet for 50,000 years.
const DORMANT_KM = 150;
function volcTable(meta) {
  const cols = meta.volcano_columns;
  if (!cols || !meta.volcanoes) return [];
  const rad = Math.PI / 180, u = (la, lo) => [Math.cos(la * rad) * Math.cos(lo * rad), Math.cos(la * rad) * Math.sin(lo * rad), Math.sin(la * rad)];
  const P = (meta.hotspots || []).map(([la, lo]) => u(la, lo));
  return meta.volcanoes.filter((r) => r.length === cols.length).map((r) => {
    const v = Object.fromEntries(cols.map((k, i) => [k, r[i]]));
    let status = v.active ? 'active' : 'extinct';
    if (!v.active && v.kind === 1) {
      const p = u(v.lat, v.lon);
      if (P.some((q) => Math.acos(Math.min(1, p[0] * q[0] + p[1] * q[1] + p[2] * q[2])) * 6371 <= DORMANT_KM)) status = 'dormant';
    }
    return { ...v, status, type: v.kind === 0 ? 'stratovolcano' : v.floor_m > 0 ? 'caldera' : 'shield volcano' };
  });
}
// the volcanoes in cell i (within ~0.6 cell spacings of its centre), for the hover card
export function volcLine(i) {
  const T = S.V.volcTable;
  if (!T?.length) return '';
  const G = S.V.grid, rad = Math.PI / 180, km = (S.V.meta.cell_size_km || 100) * 0.6;
  const la0 = G.lat[i] * rad, lo0 = G.lon[i] * rad;
  const here = T.filter((v) => {
    const c = Math.sin(la0) * Math.sin(v.lat * rad) + Math.cos(la0) * Math.cos(v.lat * rad) * Math.cos(lo0 - v.lon * rad);
    return Math.acos(Math.min(1, c)) * 6371 <= km;
  }).sort((a, b) => b.top_m - a.top_m);
  const fm = (x) => Math.round(x).toLocaleString('en-US');
  return here.slice(0, 3).map((v) => `${v.status} ${v.type}${v.top_m <= 0 ? (v.reef === 1 ? ' (an atoll now)' : ' (below the sea)') : ''}, `
    + `summit ${fm(v.top_m)} m, ${v.age < 1 ? 'under 1' : fm(v.age)} Myr`).join('; ') + (here.length > 3 ? `; +${here.length - 3} more` : '');
}

// Glacial isostasy (PW-189): a run's and a world's elevation is the bed, pressed down by its ice, so
// grounded ice can sit on a bed below sea level (land all the same: PW-307); a time zoom's is the surface
// (ice included). And ground below sea level cut off from the sea is land too (landsea.js, PW-1229). L.bed
// keeps the bed, and the elevation is shown floored at 1 m on such land, so it reads as land everywhere
// (the sea shading, the coasts, the land counts).
function landView(L) {
  if (!L.elevation) return;
  const n = S.V.n, e = L.elevation, bed = new Float32Array(n);
  if (S.V.tz) { if (L.ice) { for (let i = 0; i < n; i++) bed[i] = e[i] - L.ice[i]; L.bed = bed; } return; }
  const sea = seaMask(e, L.ice, S.V.grid.nbr), land = new Float32Array(n);
  for (let i = 0; i < n; i++) { bed[i] = e[i]; land[i] = !sea[i] && e[i] < 1 ? 1 : e[i]; }
  L.bed = bed; L.elevation = land;
}

// A frame's layers, each decoded when first read: every layer downloaded so far
// is there (the hover card names what it can), but a frame only pays for the
// ones the picture and the hover actually use.
function frameLayers(f) {
  const L = {};
  const put = (k, v) => Object.defineProperty(L, k, { value: v, writable: true, enumerable: true, configurable: true });
  for (const k of Object.keys(S.V.data)) {
    Object.defineProperty(L, k, { enumerable: true, configurable: true,
      get() { const v = decodeFrame(k, f); put(k, v); return v; }, set(v) { put(k, v); } });
  }
  return L;
}

export function setFrame(f, repaint = true) {
  const r = S.V.run;
  S.V.frame = f; S.V.t = r.frames[f].t; S.V.omega = r.frames[f].omega;
  S.V.layers = frameLayers(f);
  landView(S.V.layers);
  S.V.hotspots = r.frames[f].hotspots;
  S.V.volcanoes = r.frames[f].volcanoes;
  $('frame').value = S.V.axis.pos[f];
  $('tlabel').textContent = timeLabel(S.V.t);
  S.navUi?.time(S.V.t);
  // (the cell under the pointer stays the one it was: no new ray through the globe each frame)
  if (repaint) { paint(); renderRunSummary(); renderHover(); if (S.picked) renderZoomBox(); }
  if (!state.playing) frameToUrl();  // (while playing: when it stops)
  techTellParent();
}
export function frameToUrl() { const u = new URL(location); u.searchParams.set('t', S.V.t); history.replaceState(null, '', u); }
