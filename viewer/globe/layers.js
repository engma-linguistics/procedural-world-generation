// The colour layers: one entry each in LAYERS, with everything the viewer needs to know about it.
//
//   group    what kind of layer (sets the summary's key and where its numbers count; see byGroup)
//   ramp     colour stops [value, '#hex'] (the colour bar and the per-cell colour of a ramp layer)
//   units    the legend's units (and the button's hint, unless hintUnits is false)
//   hint     the layer button's hover text
//   in       when the layer button shows, per kind of view: world, run (a main run's frame), tz (a time zoom or a peoples
//            run). true; a layer name (the world or run has it, hasLayer); or a function of V. Missing: never.
//   needs    the run layers its colours draw from (loaded when picked; elevation, lake_kind and ice always are)
//   key      the data layer it reads (sea / vegetation / soil / game layers: the per-cell number; human use: the class)
//   num      the summary's per-cell numbers, when not the layer's own name or its key (layerNumbers)
//   where    where the summary counts its numbers: 'all', 'sea' (default: land)
//   cat      a categorical layer: V => [data layer, the legend's classes] (the summary's shares)
//   seasonal the data layer's stem when it has _jul / _jan versions (state.season)
//   obs      the Earth reference world's observed counterpart (state.obs: model / observed / difference)
//   lakes    lakes are drawn in their own colours over this layer
//   tint     peoples' cleared land is tinted over it: 'run' (a peoples run at the present), 'world' (a finished world
//            with a peoples run), or both
//   color    x => (i, c) => colour of cell i into the THREE.Color c; x = {L, elev, sv (the season's values), layer}.
//            Missing: the ramp of the layer's own values, the sea in OCEAN (rampColor).
//   legend   (sw, ov) => html of the legend (sw(colour, text): a swatch); null or missing: the ramp's colour bar
//   note     () => html after the ramp's colour bar
//
// Families (FAMILIES: 'body: ', 'animal: ', 'crop: ') are layers made per trait, animal or crop of a peoples run.
// MENUS gives each kind of view's buttons in order.
import * as THREE from 'three';
import { esc } from '../planets.js';
import { S, state } from './state.js';
import { ANIMAL_COLS, BARE, COASTAL, COASTAL_COLS, CROP_COLS, CYAN, ICE, NOBODY, NODATA, OCEAN, RED, TECH_HOW, TECH_HOW_TEXT, animalStocks, animalsColor, anthroLoad, anthroOn, anthroTint, bits, coastColor, coastLegend, coastalTop, cropStocks, cropsColor, demesColor, fuelColor, huColor, huSwatches, isSeaPeople, lakeColor, landUseColor, obsColor, obsView, peoplesColor, peoplesIdx, plateColor, resColor, resLegend, seasonUnits, seasonalData, techColor, techFrameColors, techHowText, techId, techName, techOldest, techTree, worldAnthroOn } from './colours.js';
import { rampLegend } from './panel.js';
import { agoLabel } from './timezoom.js';
import { pftColor } from './pick.js';
import { hasLayer } from './load.js';
export function ramp(stops) {
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

// ramps that colour something other than a layer of their own
const ELEVATION = [[-8000, '#0a1a36'], [-4000, '#153766'], [-1000, '#2d68a3'], [-1, '#6aa7d8'],
  [0, '#3f7d3f'], [300, '#6f9a4b'], [1000, '#c4b56c'], [2000, '#a37a4a'], [3500, '#7d6656'], [5000, '#e6e2dc'], [8000, '#ffffff']];
const PRECIPITATION = [[0, '#d9c49a'], [300, '#c9c27a'], [800, '#7fb35a'], [1600, '#2f8f5a'], [2500, '#1f6f8f'], [4000, '#203f8f']];
const SCORE5 = [[0, '#efe6c8'], [1, '#e0cf8a'], [2, '#b9c260'], [3, '#7aa848'], [4, '#3f8a3a'], [5, '#1a5a2a']];
const EXTRA_RAMPS = {
  'rock age': [[0, '#f2e6d0'], [300, '#d9b98c'], [1000, '#a87d5a'], [2000, '#6e4f3a'], [3500, '#3a2a22']],  // (crust age: the continents)
  // model minus observed (Earth reference world): temperature in C, rainfall as log2 of the ratio
  'temperature difference': [[-10, '#2b5fb3'], [-5, '#7fa8de'], [-1, '#eef1f4'], [1, '#eef1f4'], [5, '#e8956b'], [10, '#b2262b']],
  'rainfall ratio': [[-2, '#a6611a'], [-1, '#dfc27d'], [-0.2, '#f0ece2'], [0.2, '#f0ece2'], [1, '#80cdc1'], [2, '#018571']],
  'sunshine difference': [[-4, '#4d5674'], [-2, '#a3b1bf'], [-0.5, '#f0ece2'], [0.5, '#f0ece2'], [2, '#efd98a'], [4, '#e57a22']],
  body: [[0, '#ece6d6'], [25, '#e6c98a'], [50, '#d8a24a'], [75, '#b9712a'], [100, '#7a3b14']],  // (peoples runs: a body trait, PW-701)
};
const EXTRA_UNITS = { 'temperature difference': '°C, model minus observed' };

// per-cell colour helpers
const rampColor = ({ L, elev, sv, layer }) => (i, c) => {  // the default: the layer's values on land (all of it for elevation)
  if (layer !== 'elevation' && elev[i] <= 0) c.copy(OCEAN);
  else {
    rampFns[layer]((sv || L[layer])[i], c);
    if (layer === 'elevation' && L.ice && L.ice[i] > 0 && elev[i] > 0) c.lerp(ICE, 0.75);
  }
};
const onLand = (f) => (x) => { const g = f(x); return (i, c) => { if (x.elev[i] <= 0) c.copy(OCEAN); else g(i, c); }; };
const keyRamp = (key) => ({ L, layer }) => (i, c) => rampFns[layer](L[key][i], c);  // land and sea
const vegRamp = onLand(({ L, sv, layer }) => (i, c) => rampFns[layer]((sv || L[LAYERS[layer].key])[i], c));
const atSea = ({ L, elev, sv, layer }) => (i, c) => {
  if (elev[i] > 0) c.copy(BARE).lerp(OCEAN, 0.15);
  else rampFns[layer]((sv || L[LAYERS[layer].key])[i], c);
};
const greyLand = ({ elev, sv, layer }) => (i, c) => { rampFns[layer](sv[i], c); if (elev[i] > 0) c.lerp(BARE, 0.3); };  // (for the coasts)
const blueSea = ({ elev, sv, layer }) => (i, c) => { rampFns[layer](sv[i], c); if (elev[i] <= 0) c.lerp(OCEAN, 0.25); };
const classColor = (colors, key, sea) => ({ L, elev }) => (i, c) => { c.set(S.V[colors][L[key][i]]); if (sea && elev[i] <= 0) c.lerp(OCEAN, 0.45); };
const gameColor = onLand(({ L, layer }) => (i, c) => {
  const v = L[LAYERS[layer].key][i];
  if (layer === 'travel' && !v) c.copy(BARE);  // (lakes)
  else rampFns[layer](LAYERS[layer].months ? bits(v) : v, c);
});
const huLayer = ({ layer }) => (i, c) => huColor(layer, i, c);
const resLayer = ({ layer }) => (i, c) => resColor(layer, i, c);
const coastLayer = ({ layer }) => (i, c) => coastColor(layer, i, c);
const peoplesLayer = ({ layer }) => (i, c) => peoplesColor(layer, i, c);

// share-of-the-land legends of a categorical layer: count each class's land cells
const landShares = (key, cond = () => true) => {
  const L = S.V.layers, cnt = new Map();
  let land = 0;
  for (let i = 0; i < S.V.n; i++) if (L.elevation[i] > 0 && cond(i)) { cnt.set(L[key][i], (cnt.get(L[key][i]) || 0) + 1); land++; }
  return [cnt, land];
};
const peoplesLegend = (sw) => {  // the peoples present in this frame (planet/lineages/), by the land they lead
  const L = S.V.layers, lines = S.V.run.meta.lineages || [], cnt = new Map();
  for (let i = 0; i < S.V.n; i++) { const d = L.peoples ? peoplesIdx(i) : null; if (d != null && d !== 255) cnt.set(d, (cnt.get(d) || 0) + 1); }
  return [...cnt.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => sw(lines[d]?.color || '#888', esc(lines[d]?.name || d) + (isSeaPeople(lines[d]) ? ' (at sea)' : ''))).join('') +
    sw('#5a5a52', 'nobody') + (state.layer === 'peoples blend' ? '<span class="muted">(each cell blends its leading people\'s colour, the second\'s and grey for all the others, by their shares)</span>' : '<span class="muted">(whitened: mixed)</span>');
};
const HU_NOTE = { river_nav: 'ribbons follow the rivers; also under Overlays', harbour: 'diamonds mark them; also under Overlays',
  pass: 'bow-ties mark the saddle cells; also under Overlays', fertile: 'soil, water, growing season and slope', fresh_water: 'nearest perennial stream, lake, wetland or spring' };
const huLegend = (sw) => { const k = LAYERS[state.layer].key; return huSwatches(k) + `<span class="muted">(${HU_NOTE[k]}; hover a cell for details)</span>`; };
const resLeg = (sw) => resLegend(state.layer, sw);
const coastLeg = (sw) => coastLegend(state.layer, sw);
const rockLegend = (surf) => () => {
  const present = new Set(surf ? S.V.layers.surface_rock : S.V.layers.rock);
  return S.V.rocks.filter((r) => present.has(r.id))
    .map((r) => `<span><span class="sw" style="background:${r.color}"></span>${r.name}</span>`).join('') +
    (surf ? '<span class="muted">(what you would walk on: sediment where it covers the basement; faded = under the sea)</span>'
          : '<span class="muted">(basement rock; faded = under the sea; see "sediment" for what covers it)</span>');
};

const peoplesIn = (more = () => true) => (V) => hasLayer('peoples') && more(V);
const PEOPLES_NEEDS = ['peoples', 'peoples_mix', 'peoples_share', 'peoples_whole'];
const VEG_NEEDS = ['vegetation', 'tree_cover', 'npp'];
const LAKE_NEEDS = ['lake_kind', 'lake_depth'];
const RUN_ROCK = (more) => () => hasLayer('rock') && (!more || hasLayer(more));

const LAYERS = {
  // ---- the planet's surface
  satellite: { group: 'surface', seasonal: 'sat', tint: ['run', 'world'], in: { world: 'sat' },
    hint: 'True colour, as seen from space: plants, bare ground, snow and sea, by season.',
    color: ({ sv }) => (i, c) => { const v = sv[i]; c.setRGB(((v >> 16) & 255) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255, THREE.SRGBColorSpace); },
    legend: () => `<span>${seasonUnits('satellite')}: plants by type and season, bare ground, snow, ice, lakes and sea</span>` +
      '<span class="muted">(satellite.py; season picker: year = each hemisphere\'s summer; tick Clouds under Overlays)</span>' },
  biome: { group: 'surface', lakes: true, tint: ['world'], in: { world: true }, cat: (V) => ['biome', V.biomes],
    hint: 'Biome class from the climate (worlds without the vegetation model).',
    color: ({ L }) => (i, c) => c.set(S.V.biomeColors[L.biome[i]]),
    legend: () => {
      const present = new Set(S.V.layers.biome);
      return S.V.biomes.filter((b) => present.has(b.id) && !(b.name === 'lake' && S.V.layers.lake_kind))
        .map((b) => `<span><span class="sw" style="background:${b.color}"></span>${b.name}</span>`).join('');
    } },
  elevation: { group: 'surface', ramp: ELEVATION, units: 'm', where: 'all', lakes: true, needs: ['ice', ...LAKE_NEEDS], in: { world: true, run: true, tz: true },
    hint: 'Height above sea level; sea floor depth below it. Lakes cyan (fresh) and pink (salt), ice white.',
    note: () => (S.V.tz ? '<span class="muted">(ice surface included; heights above that moment\'s sea level)</span>' : '') },
  'bed under ice': { group: 'ice', ramp: ELEVATION, needs: ['ice'], in: { world: 'ice', run: 'ice', tz: true },
    units: 'm, the ground with the ice taken off (pressed down by its load; ice faintly outlined)',
    hint: 'The ground with the ice taken off, pressed down by its load.',
    color: ({ L, elev }) => (i, c) => { rampFns.elevation(L.bed ? L.bed[i] : elev[i], c); if (L.ice && L.ice[i] > 0) c.lerp(ICE, 0.15); } },
  'ice thickness': { group: 'ice', needs: ['ice'], in: { tz: true }, units: 'm of land ice (bare land grey)', hint: 'Thickness of the land ice.',
    ramp: [[0, '#f4f8fb'], [500, '#cfe3f2'], [1500, '#94bde0'], [2500, '#5d8fcb'], [3500, '#3b5fae'], [4500, '#2b2f7a']],
    color: ({ L, elev, layer }) => (i, c) => { if (L.ice[i] > 0) rampFns[layer](L.ice[i], c); else c.copy(elev[i] > 0 ? BARE : OCEAN); } },
  // ---- the solid earth
  plates: { group: 'geology', needs: ['plate', 'crust', 'plate_boundary'], in: { world: 'plate', run: true, tz: (V) => !V.tzEarth && hasLayer('plate') },
    hint: 'Tectonic plates (light: continental crust, dark: oceanic); red converging and cyan diverging boundaries.',
    color: ({ L }) => (i, c) => {
      plateColor(L.plate[i], L.crust[i], c);
      if (L.plate_boundary[i] > 0) c.lerp(RED, 0.75);
      else if (L.plate_boundary[i] < 0) c.lerp(CYAN, 0.75);
    },
    legend: () => `<span>Each colour = one plate (bright = continental crust, dark = oceanic)</span>
      <span><span class="sw" style="background:#ff3b3b"></span>converging boundary</span>
      <span><span class="sw" style="background:#3bf0ff"></span>diverging boundary</span>` },
  'crust age': { group: 'geology', num: 'crust_age', where: 'all', needs: ['crust', 'crust_age'], in: { world: 'crust_age', run: true, tz: (V) => !V.tzEarth && hasLayer('crust_age') },
    ramp: [[0, '#d7301f'], [15, '#fc8d59'], [40, '#fee08b'], [80, '#91bfdb'], [140, '#4575b4'], [200, '#313695']], units: 'Myr (sea floor)',
    hint: 'Age of the sea floor since it formed at a ridge (continents: age of their rock).',
    color: ({ L, layer }) => (i, c) => { if (L.crust[i]) rampFns['rock age'](L.crust_age[i], c); else rampFns[layer](L.crust_age[i], c); },
    note: () => '<div class="muted">continents: age of the rock since it last formed or was remade <span class="sw" style="background:#f2e6d0"></span>0 <span class="sw" style="background:#a87d5a"></span>1 Gyr <span class="sw" style="background:#3a2a22"></span>3.5 Gyr</div>' },
  'surface rock': { group: 'geology', needs: ['surface_rock'], in: { world: 'surface_rock', run: RUN_ROCK('surface_rock') }, cat: (V) => ['surface_rock', V.rocks],
    hint: 'The rock exposed at the surface (the top stratum of the rock record).',
    color: classColor('rockColors', 'surface_rock', true), legend: rockLegend(true) },
  'rock type': { group: 'geology', needs: ['rock'], in: { world: 'rock', run: RUN_ROCK() }, cat: (V) => ['rock', V.rocks],
    hint: 'The bulk rock of the crust.', color: classColor('rockColors', 'rock', true), legend: rockLegend(false) },
  'crust thickness': { group: 'geology', num: 'crust_thickness', where: 'all', needs: ['crust_thickness'], in: { world: 'rock', run: RUN_ROCK() },
    ramp: [[0, '#08306b'], [8, '#2171b5'], [20, '#9ecae1'], [30, '#c7e9c0'], [38, '#74c476'], [50, '#fd8d3c'], [65, '#d94801'], [80, '#7f2704']],
    units: 'km of crust', hint: 'Thickness of the crust (continents ~35 km, ocean floor ~7 km).', color: keyRamp('crust_thickness') },
  sediment: { group: 'geology', num: 'sediment_cover', where: 'all', needs: ['sediment_cover'], in: { world: 'rock', run: RUN_ROCK() },
    ramp: [[0, '#3a3a3a'], [0.5, '#7d6b4f'], [2, '#c9a464'], [6, '#f0d58c'], [15, '#fff7dc']],
    units: 'km of sediment on top', hint: 'Thickness of sediment on top of the basement rock.', color: keyRamp('sediment_cover') },
  // ---- climate
  rainfall: { group: 'climate', ramp: PRECIPITATION, units: 'mm/yr', seasonal: 'precipitation', needs: ['precipitation'], in: { run: RUN_ROCK() },
    hint: 'Precipitation (rain and snow as water).', color: onLand(({ sv, layer }) => (i, c) => rampFns[layer](sv[i], c)) },
  temperature: { group: 'climate', ramp: [[-30, '#2b3f99'], [-10, '#5b8fd6'], [0, '#e6f0f5'], [12, '#f4d27a'], [24, '#e2703a'], [32, '#9e1c1c']],
    units: '°C mean annual', where: 'all', seasonal: 'temperature', obs: 'obs_temperature', needs: ['temperature'], in: { world: true, run: 'climate', tz: true },
    hint: 'Air temperature near the ground.' },
  precipitation: { group: 'climate', ramp: PRECIPITATION, units: 'mm/yr', where: 'all', seasonal: 'precipitation', obs: 'obs_precipitation', in: { world: true },
    hint: 'Precipitation (rain and snow as water).' },
  climate: { group: 'climate', obs: 'obs_climate', needs: ['climate'], in: { world: 'climate', run: 'climate', tz: true }, cat: (V) => ['climate', V.koppen],
    hint: 'Köppen climate classes (A tropical, B dry, C temperate, D continental, E polar).',
    color: ({ L }) => (i, c) => c.set(S.V.koppenColors[L.climate[i]] || '#1d3f6e'),
    legend: (sw, ov) => {
      const present = new Set(ov ? ov.obs : S.V.layers.climate);
      return S.V.koppen.filter((k) => present.has(k.id) && k.code !== '-')
        .map((k) => `<span title="${k.name}"><span class="sw" style="background:${k.color}"></span>${k.code} ${k.name}</span>`).join('') +
        `<span class="muted">(Köppen climate classes${ov ? ', observed: Kottek et al. 2006; grey = no data' : ''})</span>`;
    } },
  landforms: { group: 'geology', needs: ['landform', 'landform_age', 'strata_top', 'strata_top_km', 'strata_next', 'strata_dip', 'fold_wavelength'],
    in: { world: 'landform', run: 'landform' }, cat: (V) => ['landform', V.landforms],
    hint: 'Landform classes: what shaped the ground here (folds, rifts, volcanoes, plains, glacial forms...).',
    color: ({ L, elev }) => (i, c) => { if (elev[i] <= 0 || !L.landform[i]) c.copy(OCEAN); else c.set(S.V.landformColors[L.landform[i]] || '#888'); },
    legend: (sw) => {
      const [cnt, land] = landShares('landform', (i) => S.V.layers.landform[i]);
      return S.V.landforms.filter((f) => cnt.has(f.id))
        .map((f) => sw(f.color, `${f.name} ${(() => { const p = 100 * cnt.get(f.id) / land; return p < 1 ? p.toFixed(1) : p.toFixed(0); })()}%`)).join('') +
        '<span class="muted">(landform classes from each cell\'s geological record: rifting, folding, strata, eruptions; % of land)</span>';
    } },
  // ---- what the ice left (time zooms, and the worlds finished from them)
  ...Object.fromEntries([
    ['glacial erosion', 'glacial_erosion', [[0, '#f4f1ea'], [5, '#e9d9b8'], [30, '#e0a96d'], [100, '#cc6b3d'], [300, '#9c2f2a'], [1000, '#4a1020']], 'm of bed the ice has eroded so far (time zoom)'],
    ['glacial till', 'glacial_till', [[0, '#f4f1ea'], [5, '#dfe8c8'], [20, '#a9cc86'], [60, '#5fa05a'], [150, '#2f6f45'], [400, '#123f2a']], 'm of till and moraine the ice has dropped so far (time zoom)'],
    ['glacial outwash', 'glacial_outwash', [[0, '#f4f1ea'], [1, '#f1e3b5'], [5, '#e0c26a'], [15, '#c99a2e'], [40, '#8a5a12']], 'm of outwash (sandur) the meltwater has laid down so far (time zoom)'],
    ['glacial loess', 'glacial_loess', [[0, '#f4f1ea'], [0.5, '#f3e9c0'], [2, '#e8cf7a'], [6, '#d1a63a'], [15, '#9a6b14']], 'm of loess the wind has laid down so far (time zoom)'],
  ].map(([id, k, r, u]) => [id, { group: 'glacial', key: k, ramp: r, units: u, needs: [k], in: { world: 'glacial_erosion', tz: 'glacial_erosion' }, color: keyRamp(k) }])),
  // ---- plants (worlds; tree cover and NPP also in runs)
  vegetation: { group: 'plants', needs: VEG_NEEDS, tint: ['run', 'world'], in: { world: 'vegetation', run: 'vegetation' }, cat: (V) => ['vegetation', V.vegTypes],
    hint: 'Vegetation types from the mix of plant functional types that grow in this climate.',
    color: onLand(({ L }) => (i, c) => c.set(S.V.vegColors[L.vegetation[i]] || '#888')),
    legend: (sw) => {  // the named types present, grouped (forest, savanna, desert, ...), with their share of the land
      const [cnt, land] = landShares('vegetation');
      const groups = [];
      for (const t of S.V.vegTypes) if (cnt.has(t.id) && t.id > 0) {
        if (!groups.length || groups[groups.length - 1][0] !== t.group) groups.push([t.group, []]);
        groups[groups.length - 1][1].push(t);
      }
      const share = (k) => 100 * cnt.get(k) / land, pct = (k) => (share(k) < 1 ? share(k).toFixed(1) : share(k).toFixed(0));
      // the types covering at least 0.5% of the land, by group; the rest only counted (hover a cell for them)
      let rare = 0;
      return groups.map(([g, ts]) => {
        const big = ts.filter((t) => share(t.id) >= 0.5 || t.id >= 57);
        rare += ts.length - big.length;
        return big.length ? `<span><b class="muted" style="font-weight:600">${g}:</b></span>` +
          big.map((t) => `<span title="${esc(t.text || t.name)}">${sw(t.color, '')}${t.name} ${pct(t.id)}%</span>`).join('') : '';
      }).join('') + `<span class="muted">(named vegetation types, % of land${rare ? `; ${rare} rarer types not listed` : ''})</span>`;
    } },
  'tree cover': { group: 'plants', key: 'tree_cover', ramp: [[0, '#e8dcb0'], [10, '#cdd28a'], [30, '#8fb85f'], [60, '#3f8f3f'], [90, '#1f5a2a']],
    units: '% tree canopy cover', needs: VEG_NEEDS, tint: ['run'], in: { world: 'vegetation', run: 'vegetation', tz: 'tree_cover' },
    hint: 'Tree canopy cover: the share of the ground under tree crowns.', color: vegRamp },
  'plant cover': { group: 'plants', key: 'plant_cover', ramp: [[0, '#efe0b0'], [25, '#d8cf8a'], [50, '#a9c46a'], [75, '#5f9f4a'], [100, '#2f6f3a']],
    units: '% of the ground shaded by plants', in: { world: 'vegetation' }, hint: 'Plant cover: the share of the ground shaded by plants of any kind.', color: vegRamp },
  'canopy height': { group: 'plants', key: 'canopy_height', ramp: [[0, '#efe6c8'], [2, '#c9cf8a'], [8, '#8fb85f'], [20, '#4f8f45'], [35, '#2a6a3a'], [50, '#123f2a']],
    units: 'm, tallest layer', in: { world: 'vegetation' }, hint: 'Height of the tallest plant layer.', color: vegRamp },
  'leaf area': { group: 'plants', num: 'lai_jul', seasonal: 'lai', ramp: [[0, '#efe6c8'], [1, '#cfd28a'], [2.5, '#8fbf5a'], [4, '#4f9a45'], [6, '#1f6a32']],
    units: 'm² of leaf per m² (LAI), year', hintUnits: false, in: { world: 'vegetation' },
    hint: 'Leaf area index (LAI): m² of leaf per m² of ground (0 bare, 1-2 grassland, 4-6 dense forest).', color: vegRamp },
  NPP: { group: 'plants', key: 'npp', ramp: [[0, '#f2ead0'], [100, '#e3d28a'], [300, '#b9c85f'], [600, '#6faf45'], [900, '#2f8a3a'], [1300, '#0f5a2a']],
    units: 'g C/m²/yr net primary productivity', hintUnits: false, needs: VEG_NEEDS, in: { world: 'vegetation', run: 'vegetation' },
    hint: 'Net primary productivity: the carbon plants fix by photosynthesis in a year, less what they respire themselves, in g C/m²/yr (grams of carbon per m² of ground per year). Earth: rainforest ~800-1000, desert < 100.',
    color: vegRamp },
  biomass: { group: 'plants', key: 'biomass', ramp: [[0, '#f2ead0'], [10, '#d8d28a'], [50, '#9cc060'], [120, '#4f9a45'], [250, '#1f6a32'], [400, '#0a3f22']],
    units: 't C/ha in living plants', hintUnits: false, in: { world: 'vegetation' }, hint: 'Carbon in living plants, in t C/ha (tonnes of carbon per hectare).', color: vegRamp },
  'fire return': { group: 'plants', key: 'fire_return', ramp: [[0, '#3a2a2a'], [1, '#e8503a'], [3, '#f09a3a'], [10, '#f2d36a'], [50, '#c9d6a0'], [300, '#8fb0a0'], [3000, '#4f6f80']],
    units: 'years between fires (log scale; dark = never)', in: { world: 'vegetation' }, hint: 'Fire return interval: the mean number of years between fires.',
    color: onLand(({ L, layer }) => (i, c) => { const y = L.fire_return[i]; rampFns[layer](y > 0 ? y : 3000, c); if (!y) c.copy(BARE).lerp(OCEAN, 0.1); }) },
  'stand age': { group: 'plants', key: 'stand_age', ramp: [[0, '#f2d36a'], [20, '#c9cf8a'], [80, '#7fb05a'], [200, '#3f8a45'], [600, '#1f5a3a'], [2000, '#0f3a2a']],
    units: 'years since the last stand-replacing fire', in: { world: 'vegetation' }, hint: 'Years since the last stand-replacing fire.', color: vegRamp },
  'plant type': { group: 'plants', ramp: [[0, '#2a2a2a'], [100, '#ffffff']], units: '% cover of the plant type', hintUnits: false, in: { world: 'vegetation' },
    hint: 'Cover of one plant functional type (PFT; pick it below).',
    color: onLand(({ L }) => (i, c) => { const f = (L['veg_' + state.pft]?.[i] || 0) / 100; c.copy(BARE).lerp(pftColor(), Math.sqrt(f)); }),
    legend: () => {
      const p = S.V.pfts.find((q) => q.code === state.pft);
      return `<div><div class="grad" style="background:linear-gradient(90deg,#6b675f,${p?.color || '#fff'})"></div>
      <div class="row" style="justify-content:space-between;width:260px"><span>0</span><span class="muted">% cover</span><span>100</span></div></div>
      <span>${p ? `${p.code}: ${esc(p.name)}` : '?'}</span><span class="muted">(${p ? 'its group: ' + esc(p.group) : ''})</span>`;
    } },
  // ---- soils (worlds; soils.py, PW-185)
  soils: { group: 'soil', in: { world: 'soil' }, cat: (V) => ['soil', V.soilTypes],
    hint: 'Soil types, from parent rock, slope, surface age, climate, plants and wind-blown silt (WRB groups with player names).',
    color: onLand(({ L }) => (i, c) => c.set(S.V.soilColors[L.soil[i]] || '#888')),
    legend: (sw) => {  // the soil types present with their share of the land
      const [cnt, land] = landShares('soil');
      return S.V.soilTypes.filter((t) => cnt.has(t.id)).map((t) => {
        const p = 100 * cnt.get(t.id) / land;
        return `<span title="${esc(`${t.wrb} / ${t.usda}: ${t.desc}`)}">${sw(t.color, '')}${t.name} ${p < 1 ? p.toFixed(1) : p.toFixed(0)}%</span>`;
      }).join('') + '<span class="muted">(soil types, % of land; hover a type for its WRB / USDA name)</span>';
    } },
  ...Object.fromEntries([
    ['soil depth', 'soil_depth', [[0, '#8a7f6e'], [0.25, '#c9b48a'], [0.75, '#d9c27a'], [1.5, '#a8743f'], [3, '#5a3a22']], 'm of rootable soil',
      'Rootable soil above rock: thin on steep, young or wind-scoured ground, deep on old plains and soft deposits.'],
    ['soil water', 'soil_water', [[0, '#efe0b0'], [50, '#d9cf8a'], [120, '#9cc07a'], [200, '#4f9fa0'], [350, '#1f5f8a']], 'mm of water the soil holds for plants',
      'Water the soil holds for plants down to 1.5 m (available water capacity).'],
    ['fertility', 'soil_fertility', [[0, '#d8c8a8'], [0.25, '#c9a86a'], [0.5, '#a9b85a'], [0.75, '#5f9f3a'], [1, '#1f5f22']], 'soil fertility, 0 poor to 1 rich',
      'Nutrient and base status: rich on young ash, loess and alluvium, poor where old soils are leached.'],
    ['soil carbon', 'soil_carbon', [[0, '#efe6c8'], [3, '#d6c28a'], [8, '#a8844f'], [15, '#6a4a2a'], [30, '#3a2a1a'], [60, '#1a120a']], 'kg C/m² in the top metre',
      'Organic carbon in the top metre of soil, peat included.'],
    ['peat', 'peat_depth', [[0, '#efe6c8'], [0.3, '#b9a57a'], [1, '#7a5a3a'], [3, '#3a2a1a'], [8, '#120a05']], 'm of peat where peat lies',
      'Peat thickness, where peat lies (waterlogged ground where plant remains pile up).'],
    ['permafrost', 'permafrost', [[0, '#e8dcc0'], [1, '#bcd0dc'], [2, '#7fa8c8'], [3, '#3a6a9a']], '0 none, 1 sporadic, 2 discontinuous, 3 continuous',
      'Permanently frozen ground: sporadic, discontinuous or continuous.'],
    ['loess', 'loess', [[0, '#ece6d6'], [1, '#e6d49a'], [5, '#d9b45a'], [20, '#b5852f'], [60, '#7a5418']], 'm of wind-blown silt',
      'Wind-blown silt, from deserts and glacier margins, laid down downwind.'],
  ].map(([id, k, r, u, h]) => [id, { group: 'soil', key: k, ramp: r, units: u, hint: h, in: { world: 'soil' }, color: onLand(keyRamp(k)) }])),
  // ---- game attributes of the plants and soils (gameattrs.py, PW-206): ramps on land; the month masks as month counts
  ...Object.fromEntries([
    ['travel', 'travel', [[1, '#f2ead0'], [1.5, '#e8d38a'], [2, '#e0a85a'], [3, '#c9703a'], [5, '#9a3a2a'], [8, '#5a1a1a']], 'x the time of walking open level ground (snow-free, off roads)',
      'How slow walking is, off roads in the snow-free season: stems and undergrowth, wet ground and bogs, deadfall in old forest, rough or steep ground (gameattrs.py).'],
    ['sightline', 'sightline', [[15, '#1a3a22'], [50, '#3f7a3a'], [150, '#8fb05a'], [500, '#d9cf8a'], [5000, '#f5efdc']], 'm you can see at eye level (log scale)',
      'How far you can see at eye level through the plants: tens of metres in forest, to the horizon on open ground.'],
    ['grazing', 'grazing', SCORE5, '0-5 pasture for herds', 'Pasture for herds: the herb layer\'s growth plus browse from shrubs, less where the ground is frozen or snowed in.'],
    ['foraging', 'foraging', SCORE5, '0-5 wild food for people', 'Wild food for people: mast and fruit trees, game, wetlands (waterfowl, wild grain, roots) and river fish.'],
    ['timber', 'timber', SCORE5, '0-5 building timber', 'Building timber: woody biomass and height; straight conifers score higher.'],
    ['fuel', 'fuel', [[0, '#efe6c8'], [1, '#e8cf8a'], [2, '#d9a65a'], [3, '#b8743a'], [4, '#8a4a2a'], [5, '#4a2a1a']], '0-5 firewood and fuel',
      'Firewood and fuel: wood, shrubs, cut peat from bogs, dung on pasture.'],
    ['building ground', 'building', [[0, '#6a3a3a'], [1, '#a8603f'], [2, '#d9a65a'], [3, '#e3d28a'], [4, '#b5c9a0'], [5, '#7f9fb0']], '0-5: 0 peat or swelling clay .. 5 firm, dry rock',
      'How good the ground is to build on: firm rock or gravel best; loose sand, soft clay, loess, waterlogged ground, salt, swelling clay, peat, permafrost and slopes worse.'],
    ['mud season', 'mud_months', [[0, '#efe6c8'], [2, '#d9c08a'], [4, '#a8844f'], [7, '#6a4a2a'], [12, '#3a2a1a']], 'months the ground is mud',
      'Months the ground turns to mud: wet, thawed months on clay, silt or poorly drained soil, and the summer thaw over permafrost.'],
    ['fire season', 'fire_months', [[0, '#dfe6d8'], [1, '#f2d36a'], [3, '#f09a3a'], [6, '#e8503a'], [9, '#8a2a2a']], 'fire-weather months (where it burns)',
      'Months of fire weather (dry litter, warm, no snow), where the place burns at all.', true],
    ['green season', 'green_months', [[0, '#c9b38a'], [3, '#d9cf8a'], [6, '#a9c26a'], [9, '#5f9f45'], [12, '#1f6a32']], 'months the plants are in leaf and snow-free',
      'Months the plants are in leaf and free of snow (each plant type\'s leaf habit, weighted by its cover).', true],
  ].map(([id, k, r, u, h, months]) => [id, { group: 'game', key: k, ramp: r, units: u, hint: h, months: !!months, in: { world: 'travel' }, color: gameColor }])),
  // ---- peoples runs
  peoples: { group: 'peoples', needs: PEOPLES_NEEDS, in: { tz: peoplesIn() }, color: peoplesLayer, legend: peoplesLegend },
  'peoples blend': { group: 'peoples', in: { tz: peoplesIn(() => hasLayer('mix_second')) }, color: peoplesLayer, legend: peoplesLegend },
  demes: { group: 'peoples', needs: ['demes'], in: { tz: peoplesIn(() => hasLayer('demes')) }, color: () => (i, c) => demesColor(i, c),
    legend: (sw) => {  // the regional populations of this frame (planet/lineages/demes.py, PW-981), the largest first
      const L = S.V.layers, D = S.V.demes?.demes || [], cnt = new Map();
      if (L.demes) for (let i = 0; i < S.V.n; i++) { const d = L.demes[i]; if (d !== 65535) cnt.set(d, (cnt.get(d) || 0) + 1); }
      const rows = [...cnt.entries()].filter(([d]) => D[d]).sort((a, b) => b[1] - a[1]);
      return rows.slice(0, 14).map(([d]) => sw(D[d].color, esc(D[d].name))).join('') + (rows.length > 14 ? `<span class="muted">+ ${rows.length - 14} more</span>` : '') +
        sw('#5a5a52', 'nobody') + `<span class="muted">${rows.length} regional populations of the leading peoples here: cut where sea, hard country or distance part a people (each a shade of its people's colour); ${S.V.demes ? `cut since ${S.V.demes.from_kyr} kyr ago` : 'loading the tree…'}</span>`;
    } },
  'peoples mix': { group: 'peoples', needs: ['peoples_mix'], in: { tz: peoplesIn() }, color: peoplesLayer,
    legend: (sw) => [1, 2, 3, 4].map((m) => sw(`hsl(${(0.75 - 0.12 * m) * 360},70%,${35 + 6 * m}%)`, m === 4 ? '4+ peoples' : `${m}`)).join('') + sw('#5a5a52', 'nobody') },
  'peoples overlay': { group: 'peoples', needs: ['peoples', 'peoples_overlay'], in: { tz: peoplesIn() }, color: peoplesLayer,
    legend: (sw) => {  // (it fell through to the ramp legend, which threw: PW-679)
      const L = S.V.layers, lines = S.V.run.meta.lineages || [], cnt = new Map(), ov = L.peoples_overlay;
      for (let i = 0; i < S.V.n; i++) { const d = ov ? ov[i] : 255; if (d !== 255 && lines[d]) cnt.set(d, (cnt.get(d) || 0) + 1); }
      return [...cnt.entries()].sort((a, b) => b[1] - a[1]).map(([d]) => sw(lines[d].color, esc(lines[d].name))).join('') +
        '<span class="muted">templates and contact hybrids; elsewhere the leading people</span>';
    } },
  '@body': {}, '@animal': {}, '@crop': {},  // (the families' places in the menus)
  'land use': { group: 'peoples', needs: ['tree_cover', 'ice'], in: { tz: (V) => !!V.run?.meta?.anthro },
    hint: 'Peoples runs, at the present: cropland, pasture, burned grassland and managed woods around the peoples there, settlement density in red (planet/lineages/landuse.py).',
    color: () => (i, c) => landUseColor(i, c),
    legend: (sw) => rampLegend('tree cover', '% wild tree cover (the land as it was)') + sw('#f0b429', 'cropland') + sw('#b9d36a', 'pasture') +
      sw('#c98a3c', 'burned grassland') + sw('#2d6a4a', 'managed woods') + sw('#9c3b2a', 'densely settled (6+ people/km²)') +
      `<span class="muted">${anthroOn() ? 'the present, from the peoples and their ways of life' : 'step to the last frame (the present) to see it'}</span>` },
  fuels: { group: 'peoples', needs: ['tree_cover', 'ice'], in: { world: (V) => !!V.wAnthroRun?.fuels, tz: (V) => !!V.run?.meta?.fuels },
    hint: 'Peoples runs, at the present: what each cell burns to cook and heat (wood, charcoal, dung, peat, straw, grass, driftwood, coal), from the trees left, the herds, the peat, the crops and the coal (planet/lineages/fuels.py).',
    color: () => (i, c) => fuelColor(i, c),
    legend: (sw) => {
      const F = S.V.kind === 'world' ? S.V.wAnthroRun.fuels : S.V.run.meta.fuels;
      return F.names.map((k) => sw(F.colors[k], F.phrases[k])).join('') + sw('#5a5a52', 'nobody') +
        `<span class="muted">${S.V.kind === 'world' ? `the leading fuel of peoples run ${S.V.wAnthroRun.id}, paler where it is a smaller share (the 'fuel' layer is the land's firewood score, 0-5)` : anthroOn() ? 'the leading fuel at the present, paler where it is a smaller share' : 'step to the last frame (the present) to see it'}</span>`;
    } },
  technology: { group: 'peoples', needs: ['peoples'], in: { tz: (V) => !!V.run?.meta?.techtree && hasLayer('peoples') },
    hint: 'Peoples runs with a technology tree: where one tech (picked under the layers) was known at this moment. Each people\'s land is lit when it knew it by then, in the colour of how it came (or how long it was known); grey: not yet. Stars: inventions; arrows: giver to taker (planet/lineages/techtree.py).',
    color: ({ L }) => {
      const techCols = techTree() && L.peoples ? techFrameColors() : null;  // (each line's colour this frame, once)
      return (i, c) => { if (techCols) techColor(i, c, techCols); else c.copy(NODATA); };
    },
    legend: (sw) => {
      if (!techTree()) return null;
      const tt = techTree(), id = techId(), f = tt.firsts[id], now = -S.V.t, lines = S.V.run.meta.lineages || [];
      const knew = lines.filter((l) => (tt.known[l.id]?.[id]?.[0] ?? -1) >= now - 1e-9).length;
      return `<b>${esc(techName(id))}</b>` + (state.techCol === 'when'
        ? `<span>new</span><span class="sw" style="width:70px;background:linear-gradient(90deg,#ffeca0,#d64828)"></span><span>long known</span>`
        : Object.keys(TECH_HOW).map((h) => sw(TECH_HOW[h], TECH_HOW_TEXT[h])).join('')) + sw('#464e5a', 'not yet') + sw('#2a2e28', 'nobody') +
        `<span class="muted">${knew} peoples know it by ${now <= 0 ? 'the present' : agoLabel(S.V.t)}; first: ${f ? `${esc((lines.find((l) => l.id === f.line)?.name || f.line).split(' (')[0])}, ${agoLabel(-f.ago_kyr)} (${esc(techHowText(f.how))})` : 'nobody'}. Stars: inventions, tamings, kits; arrows: giver to taker${techOldest(id) > -S.V.run.frames[0].t ? `; older events are drawn on the ranges of the first stored moment (${agoLabel(S.V.run.frames[0].t)})` : ''}.</span>`;
    } },
  // ---- rivers (worlds, PW-028)
  'river floods': { group: 'water', num: 'flood_ratio', ramp: [[1, '#2f5f8f'], [1.5, '#4f9fb0'], [2, '#9fd0a0'], [3, '#f0d36b'], [4.5, '#ef8a3a'], [7, '#b8283a']],
    units: "x: the rivers' peak month over their mean month (1 = steady; Arctic spring floods 3-5); grey: frozen half the year or more", hintUnits: false,
    in: { world: 'flood_ratio' }, hint: 'How seasonal the rivers are: the peak month over the mean month.',
    color: onLand(({ L, layer }) => (i, c) => { rampFns[layer](L.flood_ratio[i], c); if (L.river_frozen && L.river_frozen[i] >= 6) c.lerp(ICE, 0.35); }) },
  // ---- human use (humanuse.py, PW-099/505): class maps coloured from the legend (legend.human_use); the first three also draw
  // ribbons / markers (overlays huRivers, huHarbours, huPasses), which a layer of the same name switches on by itself
  ...Object.fromEntries([
    ['navigable rivers', 'river_nav', 'class: 1 small boats, 2 barges, 3 sea-going', 'Rivers by what can float on them: small boats, barges, sea-going ships (depth from the mean discharge, rapids, months frozen).'],
    ['harbours', 'harbour', 'class: 1 anchorage, 2 harbour, 3 fine harbour', 'Natural harbours at the coast: sheltered, deep water, or an estuary (anchorage, harbour, fine harbour).'],
    ['passes', 'pass', 'class: open most of the year, seasonal, snow-bound', 'The lowest crossings of divides between drainage basins separated by real relief, by the months they are open.'],
    ['farmland', 'fertile', 'class: 0 not arable .. 4 prime', 'Farmland quality from soil fertility and depth, water, growing season and slope, less permafrost, peat and flooding.'],
    ['fresh water', 'fresh_water', 'class: 0 none .. 3 on site', 'How far perennial fresh water is: on site, close by, a day or two away, or none within reach.'],
  ].map(([id, k, u, h]) => [id, { group: 'humanuse', key: k, units: u, hint: h, in: { world: (V) => !!(V.layers[k] && V.humanUse?.[k]) }, color: huLayer, legend: huLegend }])),
  // ---- resources (resources.py, PW-155): 'resources' = the most likely metal/gem/energy/salt resource per cell (faded by
  // its likelihood), 'resource' = one resource's likelihood (picker resSel, ?res=), 'building stone' = the best stone
  ...Object.fromEntries(['resources', 'resource', 'building stone'].map((id) => [id, { group: 'resources', in: { world: (V) => !!(V.layers.resource && V.resLeg) }, color: resLayer, legend: resLeg }])),
  // ---- coasts (coastform.py)
  coasts: { group: 'coasts', in: { world: (V) => !!(V.layers.coast_type && V.coastLeg) }, color: coastLayer, legend: coastLeg,
    hint: 'The form of each coast: ice fronts, fjords, deltas, mangrove and coral coasts, tidal flats, barrier islands, cliffs, rocky shores, beaches (planet/coastform.py).' },
  ...Object.fromEntries([
    ['barrier islands', 'barrier', 'How likely the coast is fronted by barrier islands and lagoons: low land, a gentle shelf, waves and small tides.'],
    ['cliffs', 'cliff', 'How likely the coast is cliffed: high or hard land under strong waves.'],
    ['seabirds', 'seabirds', 'How likely seabird colonies are: rich water nearby and cliffs or predator-free islands to nest on.'],
    ['seals', 'seals', 'How likely seals and sea lions haul out here: rich, cool water and rocky shores, island beaches or sea ice.'],
    ['sea hazards', 'nav_hazard', 'Hazards to ships: coral reefs, shallow banks away from the coast, sea ice much of the year.'],
  ].map(([id, k, h]) => [id, { group: 'coasts', key: k, hint: h, in: { world: (V) => !!(V.layers.coast_type && V.coastLeg) }, color: coastLayer, legend: coastLeg }])),
  // ---- the sea (worlds): waves and tides, sea-surface temperature (C) and salinity (psu)
  'wave power': { group: 'sea', key: 'wave_power', ramp: [[0, '#1d2f55'], [5, '#2f6f8f'], [15, '#4fae9b'], [30, '#b8d66b'], [60, '#f2c14e'], [100, '#e8603c']],
    units: 'kW/m of wave crest, mean (at sea)', where: 'sea', in: { world: 'wave_power' }, hint: 'Mean wave power per metre of wave crest (at sea).', color: atSea },
  'tide range': { group: 'sea', key: 'tide_range', ramp: [[0, '#1d2f55'], [0.5, '#2c5d8a'], [1.5, '#3f9bb0'], [3, '#8fd19e'], [6, '#f0d36b'], [10, '#e8603c']],
    units: 'm, tidal range (at sea)', where: 'sea', in: { world: 'tide_range' }, hint: 'Tidal range: the height between high and low tide (at sea).', color: atSea },
  'sea temperature': { group: 'sea', key: 'sst', seasonal: 'sst', where: 'sea', in: { world: 'sst' }, units: '°C sea surface, year', hint: 'Sea surface temperature.',
    ramp: [[-2, '#3b3a8f'], [4, '#3f74c0'], [10, '#5fb6c8'], [16, '#bfe3b0'], [21, '#f2d77a'], [26, '#ef8f45'], [30, '#b8282a']], color: atSea },
  salinity: { group: 'sea', key: 'salinity', where: 'sea', in: { world: 'salinity' }, units: 'psu at the sea surface (mean 34.7)', hintUnits: false,
    ramp: [[31, '#3b2a78'], [33, '#3f6fb5'], [34.2, '#8fc3d8'], [34.9, '#e9eee6'], [35.8, '#f0c870'], [37, '#d9783a'], [39, '#9e2a1e']],
    hint: 'Sea surface salinity in psu (practical salinity units, ≈ grams of salt per kg of sea water).', color: atSea },
  // coastal life (worlds, coastal.py, PW-188): habitats, river mud in the sea (mg/L, log-like stops) and upwelling (C of cooling)
  'coastal life': { group: 'sea', in: { world: 'reef' }, units: '% of the cell: the biggest habitat\'s colour, stronger = more',
    hint: 'Coral reefs, kelp forests and seagrass on the shallow sea floor, mangroves and salt marsh between the tides: each cell in its biggest habitat\'s colour.',
    color: ({ elev }) => (i, c) => {  // the biggest habitat's colour over land or sea
      c.copy(elev[i] > 0 ? BARE : OCEAN);
      const t = coastalTop(i);
      if (t) c.lerp(COASTAL_COLS[t[0]], 0.25 + 0.75 * Math.min(Math.sqrt(t[1] / 30), 1));
    },
    legend: (sw) => {
      const L = S.V.layers, cell = 4 * Math.PI * 6371 ** 2 / S.V.n / 100;
      const km2 = (k) => { let t = 0; for (let i = 0; i < S.V.n; i++) t += L[k][i]; return t * cell; };
      return COASTAL.map(([k, n, c]) => sw(c, `${n} ${Math.round(km2(k)).toLocaleString()} km²`)).join('') +
        `<span class="muted">(${UNITS['coastal life']}; reefs, kelp, seagrass at sea, mangroves and salt marsh between the tides; hover a cell for its shares)</span>`;
    } },
  turbidity: { group: 'sea', key: 'turbidity', where: 'sea', in: { world: 'reef' }, ramp: [[0, '#0f3a5f'], [1, '#2f6f8f'], [3, '#6fa88a'], [10, '#c9b26a'], [30, '#a8743a'], [100, '#6b4424']],
    units: 'mg/L of river mud at the sea surface (clear sea ~0.5; reefs need under ~10)', hint: 'River mud suspended in the sea (it takes the light reefs and seagrass need).', color: atSea },
  upwelling: { group: 'sea', key: 'upwelling', where: 'sea', in: { world: 'upwelling' }, ramp: [[0, '#1d2f55'], [0.5, '#2f5f8f'], [1.5, '#3f9bb0'], [3, '#8fd19e'], [6, '#f0d36b'], [10, '#e8603c']],
    units: '°C the sea surface is cooled by upwelling (nutrients for kelp and fisheries)', hint: 'Cold, nutrient-rich water welling up along coasts and the equator: how much it cools the sea.', color: atSea },
  // ---- the air's moisture (worlds): relative humidity (%), dew point (C); the sky: cloud cover (% of the sky), bright sunshine (hours a day)
  humidity: { group: 'air', seasonal: 'humidity', where: 'all', in: { world: 'humidity' }, units: '% rel. humidity, year', hint: 'Relative humidity near the ground.',
    ramp: [[15, '#b98a4f'], [35, '#e3cf94'], [55, '#d9e7c4'], [70, '#7fc3b0'], [82, '#3f8fb0'], [95, '#244f8f']], color: greyLand },
  'dew point': { group: 'air', seasonal: 'dewpoint', where: 'all', in: { world: 'humidity' }, units: '°C dew point, year', hint: 'Dew point: the temperature at which the air would be saturated.',
    ramp: [[-25, '#5b4f9a'], [-5, '#9fb0d0'], [5, '#d8e6e0'], [12, '#b9dc8a'], [17, '#f2d55e'], [21, '#ef8a3a'], [25, '#b8283a']], color: greyLand,
    note: () => '<span class="muted">(above ~20 °C feels muggy)</span>' },
  cloud: { group: 'air', seasonal: 'cloud', where: 'all', in: { world: 'cloud' }, units: '% cloud cover, year', hint: 'Cloud cover: the share of the sky covered.',
    ramp: [[0, '#f2c14e'], [20, '#efe0a6'], [40, '#d3dade'], [60, '#a3b1bf'], [80, '#6f7f93'], [100, '#454e5e']], color: blueSea },
  sunshine: { group: 'air', seasonal: 'sunshine', obs: 'obs_sunshine', where: 'all', in: { world: 'cloud' }, units: 'hours of bright sunshine a day, year', hint: 'Hours of bright sunshine a day.',
    ramp: [[0, '#2e3348'], [2, '#4d5674'], [4, '#8a93a6'], [6, '#d3d3c0'], [8, '#efd98a'], [10, '#f3b33d'], [12, '#e57a22'], [14, '#c4461a']], color: blueSea },
};

// layers made per trait, animal or crop of a peoples run: 'body: tall', 'animal: horse', 'crop: wheat'
const FAMILIES = {
  'body: ': { group: 'peoples', in: { tz: peoplesIn() }, expand: () => Object.keys(S.V.run.layers).filter((k) => k.startsWith('body_')).map((k) => 'body: ' + k.slice(5)),
    needs: (id) => ['peoples_whole', 'body_' + id],
    color: ({ L, elev, layer }) => { const v = L['body_' + layer.slice(6)]; return (i, c) => {
      if (L.ice && L.ice[i] > 0) c.copy(ICE); else if (elev[i] <= 0) c.copy(OCEAN);
      else if (L.peoples_whole[i] === 255) c.copy(NOBODY); else rampFns.body(v[i], c);
    }; },
    legend: (sw) => rampLegend('body', `% of the cell's people with it (${state.layer.slice(6)}: each people's share, mixed by who lives there)`, ['0%', '100%']) + sw('#5a5a52', 'nobody') },
  'animal: ': { group: 'peoples', in: { tz: 'animal_wild' }, expand: () => Object.keys(animalStocks()).map((k) => 'animal: ' + k),
    needs: () => ['animal_wild', 'animal_known'],
    color: ({ layer }) => { const id = layer.slice(8); return (i, c) => animalsColor(i, c, id); },
    legend: (sw) => {
      const id = state.layer.slice(8), h = animalStocks()[id], t = h?.tamed?.[0];
      return sw('#3f9d4a', `wild range of ${h?.label || id} (from the land)`) + sw(ANIMAL_COLS[(h?.bit || 0) % 8], 'tamed and known') +
        `<span class="muted">${h?.fantasy ? `fantasy animal (${S.V.run.meta.mode} mode); ` : ''}${t ? `tamed ~${t.ago_kyr} kyr ago by the ${esc(t.people)} on the ${esc(t.country)} of ${esc(t.landmass_name)} (${t.lat}, ${t.lon})` : h ? 'never tamed on this world: ' + esc(h.never || '') : ''}${h && h.tamed.length > 1 ? `; again, on its own: ${h.tamed.slice(1).map((x) => `${esc(x.people)}, ~${x.ago_kyr} kyr ago`).join('; ')}` : ''}${h && h.crossed ? `; carried over the sea ${h.crossed} times` : ''}</span>`;
    } },
  'crop: ': { group: 'peoples', in: { tz: 'crop_wild' }, expand: () => Object.keys(cropStocks()).map((k) => 'crop: ' + k),
    needs: () => ['crop_wild', 'crop_known'],
    color: ({ layer }) => { const id = layer.slice(6); return (i, c) => cropsColor(i, c, id); },
    legend: (sw) => {
      const id = state.layer.slice(6), h = cropStocks()[id], t = h?.tamed?.[0];
      return sw('#3f9d4a', `wild range of ${h?.label || id} (from the land)`) + sw(CROP_COLS[(h?.bit || 0) % CROP_COLS.length], 'cultivated and known') +
        `<span class="muted">${h?.fantasy ? `fantasy crop (${S.V.run.meta.mode} mode); ` : ''}${t ? `first cultivated ~${t.ago_kyr} kyr ago by the ${esc(t.people)} on ${esc(t.landmass_name)} (${t.lat}, ${t.lon})` : h ? 'never cultivated on this world: ' + esc(h.never || '') : ''}${h && h.tamed.length > 1 ? `; again, on its own: ${h.tamed.slice(1).map((x) => `${esc(x.people)}, ~${x.ago_kyr} kyr ago`).join('; ')}` : ''}${h && h.crossed ? `; carried over the sea ${h.crossed} times` : ''}</span>`;
    } },
};
const FAMILY_OF = { '@body': 'body: ', '@animal': 'animal: ', '@crop': 'crop: ' };

// each kind of view's layer buttons, in order (a layer shows when its `in` says so)
const MENUS = {
  world: ['satellite', 'biome', 'elevation', 'temperature', 'precipitation', 'bed under ice', 'plates', 'crust age', 'climate', 'surface rock',
    'rock type', 'crust thickness', 'sediment', 'landforms', 'glacial erosion', 'glacial till', 'glacial outwash', 'glacial loess',
    'vegetation', 'tree cover', 'plant cover', 'canopy height', 'leaf area', 'NPP', 'biomass', 'fire return', 'stand age', 'plant type',
    'soils', 'soil depth', 'soil water', 'fertility', 'soil carbon', 'peat', 'permafrost', 'loess',
    'travel', 'sightline', 'grazing', 'foraging', 'timber', 'fuel', 'building ground', 'mud season', 'fire season', 'green season',
    'fuels', 'river floods', 'navigable rivers', 'harbours', 'passes', 'farmland', 'fresh water', 'resources', 'resource', 'building stone',
    'coasts', 'barrier islands', 'cliffs', 'seabirds', 'seals', 'sea hazards', 'wave power', 'tide range', 'sea temperature', 'salinity',
    'coastal life', 'turbidity', 'upwelling', 'humidity', 'dew point', 'cloud', 'sunshine'],
  run: ['elevation', 'plates', 'crust age', 'bed under ice', 'surface rock', 'rock type', 'crust thickness', 'sediment', 'rainfall',
    'temperature', 'climate', 'landforms', 'vegetation', 'tree cover', 'NPP'],
  // a time zoom has no rock, rivers or rain; its plates/crust are frozen (and empty for Earth)
  tz: ['elevation', 'ice thickness', 'bed under ice', 'temperature', 'climate', 'plates', 'crust age', 'glacial erosion', 'glacial till',
    'glacial outwash', 'glacial loess', 'tree cover', 'peoples', 'peoples blend', 'demes', 'peoples mix', 'peoples overlay', '@body',
    '@animal', '@crop', 'land use', 'fuels', 'technology'],
};

// a layer's entry (a family's for 'body: x', 'animal: x', 'crop: x'); {} for a name it doesn't know
export function layerDef(layer) {
  if (LAYERS[layer]) return LAYERS[layer];
  const f = Object.keys(FAMILIES).find((p) => layer.startsWith(p));
  return f ? FAMILIES[f] : {};
}

const shows = (w) => w === true || (typeof w === 'string' ? hasLayer(w) : !!(w && w(S.V)));
export function availableLayers() {
  const kind = S.V.tz ? 'tz' : S.V.kind === 'run' ? 'run' : 'world';
  return MENUS[kind].flatMap((id) => {
    const fam = FAMILY_OF[id] && FAMILIES[FAMILY_OF[id]];
    if (fam) return shows(fam.in[kind]) ? fam.expand() : [];
    return shows(LAYERS[id].in[kind]) ? [id] : [];
  });
}

// the run layers a colour layer draws from (load.js: layersNeeded)
export function layerNeeds(layer) {
  const d = layerDef(layer);
  return typeof d.needs === 'function' ? d.needs(layer.slice(layer.indexOf(': ') + 2)) : d.needs || [];
}

// fills a Float32Array(3n) with per-cell colours
export function cellColors(layer) {
  const L = S.V.layers, n = S.V.n, out = new Float32Array(3 * n), c = new THREE.Color();
  const elev = L.elevation, ov = obsView(layer), d = layerDef(layer), lakes = !ov && d.lakes && (L.lake_kind || L.lake);
  const sv = seasonalData(layer);  // temperature / rain: the year's, or July's / January's
  if (S.V.run?.meta?.anthro && S.V.anthroFor !== S.V.run.id) anthroLoad();  // (peoples change the land, PW-662)
  const tint = state.anthro !== false && (d.tint?.includes('run') && anthroOn() || d.tint?.includes('world') && worldAnthroOn());
  const color = ov ? (i, c) => obsColor(ov, i, c) : (d.color || rampColor)({ L, elev, sv, layer });
  for (let i = 0; i < n; i++) {
    if (!(lakes && lakeColor(i, c))) color(i, c);
    if (tint && elev[i] > 0 && !(L.ice && L.ice[i] > 0)) anthroTint(i, c);
    out[3 * i] = c.r; out[3 * i + 1] = c.g; out[3 * i + 2] = c.b;
  }
  return out;
}

// ---- lookups derived from LAYERS, for the code that asks one question of many layers
const pick = (f) => Object.fromEntries(Object.entries(LAYERS).filter(([, d]) => f(d) != null).map(([id, d]) => [id, f(d)]));
const byGroup = (g) => pick((d) => (d.group === g && d.key ? d.key : null));
export const RAMPS = { ...pick((d) => d.ramp), ...EXTRA_RAMPS };
export const UNITS = { ...pick((d) => d.units), ...EXTRA_UNITS };
export const rampFns = Object.fromEntries(Object.entries(RAMPS).map(([k, v]) => [k, ramp(v)]));
export const SEASONAL = pick((d) => d.seasonal);
export const OBS_LAYERS = pick((d) => d.obs);
export const LAKE_LAYERS = new Set(Object.keys(pick((d) => d.lakes)));
export const WORLD_TINTED = new Set(Object.keys(pick((d) => (d.tint?.includes('world') ? 1 : null))));
export const VEG_VIEWS = new Set(Object.keys(pick((d) => (d.group === 'plants' ? 1 : null))));
export const HU_LAYERS = byGroup('humanuse');
export const COAST_SCORES = byGroup('coasts');
