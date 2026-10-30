import { esc } from '../planets.js';
import { S, state } from './state.js';
import { $, CMYR } from './scene.js';
import { SEASON_NAMES, animalStocks, anthroRows, coastText, coastalText, cropRows, demeOf, fuelRows, isSeaPeople, lakeLine, monthRuns, resRows, techRows } from './colours.js';
import { plateVelocity } from './geometry.js';
import { timeLabel } from './timezoom.js';
import { volcLine } from './load.js';
// ------------------------------------------------------------ the cell's description
// cellInfo(i) lists what is known about cell i as rows { g: group, k: label, v: value,
// sep: between them in the text, ess: shown in the compact info box (the rest in the
// "more" panel), join: appended to the previous line of the text with this separator,
// lab: the label to show when k is empty, extra: only in the panel, not in the text }.
// describe(i) is the text (the clipboard and the deep link) made from it.
// the players' line of the game attributes (gameattrs.py): "Travel slow (x2.5), sightlines 30 m, fine timber, poor
// grazing; fire weather Jul-Sep, big fires every ~30 yr." Words from the scores; the per-type text is the legend's.
const SCORE_WORDS = ['none', 'poor', 'fair', 'good', 'rich', 'superb'];
const sightText = (m) => (m >= 4000 ? 'to the horizon' : m >= 1000 ? `~${(m / 1000).toFixed(1)} km` : `~${m >= 100 ? Math.round(m / 50) * 50 : Math.round(m / 5) * 5} m`);
function gameSentence(L, i) {
  const t = L.travel[i], words = [];
  words.push(`Travel ${t < 1.3 ? 'easy' : t < 2 ? 'steady' : t < 3 ? 'slow' : t < 5 ? 'very slow' : 'a struggle'} (×${t.toFixed(1)})`);
  words.push(`sightlines ${sightText(L.sightline[i])}`);
  const best = [['timber', 'timber'], ['grazing', 'grazing'], ['foraging', 'foraging'], ['fuel', 'fuel']]
    .map(([k, n]) => [L[k][i], n]).sort((a, b) => b[0] - a[0]);
  const [v0, n0] = best[0], [v1, n1] = best[3];
  if (v0 >= 1.5) words.push(`${SCORE_WORDS[Math.round(v0)]} ${n0}`);
  if (v1 < 1 && v0 >= 1.5) words.push(`no ${n1}`);
  if (L.building[i] <= 1.5) words.push('treacherous ground to build on');
  if (L.mud_months[i] >= 3) words.push(`mud ${L.mud_months[i]} months a year`);
  const f = monthRuns(L.fire_months[i]), fr = L.fire_return?.[i];
  const fire = f ? `fire weather ${f}${fr ? `, fires every ~${fr < 10 ? fr : Math.round(fr / 10) * 10} yr` : ''}` : 'fire almost never';
  const g = monthRuns(L.green_months[i]);
  return words.join(', ') + `; ${g === 'all year' ? 'green all year' : g ? `green ${g}` : 'never green'}; ${fire}.`;
}
const GROUPS = { place: 'Place', climate: 'Climate', water: 'Water', plants: 'Plants', soil: 'Soil', game: 'For players', ground: 'Rock and landforms',
                 plates: 'Plates', observed: 'Observed (Earth)' };
// hover hints for terms that aren't self-evident: what it is and its units
const HINTS = {
  NPP: 'Net primary productivity: the carbon plants fix by photosynthesis in a year, less what they respire themselves, in grams of carbon per m² of ground per year (g C/m²/yr). Earth: rainforest ~800-1000, temperate forest ~500-700, desert < 100.',
  LAI: 'Leaf area index: m² of leaf (one side) per m² of ground. 0 bare, ~1-2 grassland, 4-6 dense forest.',
  leaves: 'Leaf area index (LAI): m² of leaf (one side) per m² of ground, in July and January. 0 bare, ~1-2 grassland, 4-6 dense forest.',
  canopy: 'Height of the tallest plant layer, in metres.',
  trees: 'Tree canopy cover: the share of the ground under tree crowns, in %.',
  vegetation: 'The vegetation type, from the mix of plant functional types that grow here (planet/vegetation.py).',
  'main plant types': 'Plant functional types (PFTs) with at least 3% cover: groups of plants that grow and respond alike (e.g. boreal needleleaf evergreen trees, C4 grasses).',
  fires: 'Fire return interval: the mean number of years between fires that burn the stand.',
  stands: 'Stand age: years since the last stand-replacing fire.',
  'flooded part of the year': 'The share of the cell flooded part of the year (floodplains and wetlands), in %.',
  climate: 'Köppen climate class (e.g. Cfb temperate oceanic), and the mean temperature of the coldest and warmest months.',
  temp: 'Air temperature near the ground, mean over the year (°C); July and January are the means of those months.',
  mean: 'Air temperature near the ground, mean over the year (°C).',
  rain: 'Precipitation (rain and snow as water), mm per year. The July / January halves are the April-September / October-March half-years, each as a rate per year.',
  July: 'The April-September half-year (temperature: July itself), rain as a rate per year.',
  January: 'The October-March half-year (temperature: January itself), rain as a rate per year.',
  river: 'Mean discharge of the river through this cell (m³/s), and in worlds its flood month and peak-over-mean ratio.',
  humidity: 'Relative humidity (%) and dew point (°C) near the ground, in July and January.',
  sky: 'Cloud cover (% of the sky) and bright sunshine (hours a day), in July and January.',
  sea: 'Sea surface temperature (°C) and salinity in psu (practical salinity units, ≈ grams of salt per kg of sea water; the ocean mean is ~34.7).',
  waves: 'Mean wave power in kW per metre of wave crest, and the tidal range in m (at sea).',
  'deep water sinks here': 'Deep-water formation: the sea water sinking here, in sverdrups (1 Sv = 1 million m³/s).',
  surface: 'The rock exposed at the surface: the top stratum of the rock record (veneers under 20 m looked through).',
  rock: 'The bulk rock of the crust here.',
  'sediment cover': 'Thickness of sediment on top of the basement, in km.',
  crust: 'Thickness of the crust, in km (continents ~35, ocean floor ~7).',
  landform: 'The landform class, and how long it has been forming (Myr) where that is known.',
  strata: 'The top stratum of the rock record and its thickness (km), over the next one down.',
  folded: 'How steeply the strata dip, and how far apart the fold crests are.',
  'strata dip': 'The regional dip of flat-lying strata, in degrees.',
  plate: 'The tectonic plate this cell belongs to, and whether its crust here is continental or oceanic.',
  'rock age': 'Age of the continental rock (Myr).', 'sea floor age': 'Age of the ocean floor (Myr since it formed at a ridge).',
  moving: 'Speed of the plate here, cm per year.',
  boundary: 'Plate boundary: converging (collision, subduction) or diverging (rift, ridge).',
  ice: 'Thickness of the land ice (m); in runs also the bed under it, pressed down by its load.',
  lake: 'A lake: fresh, salt, or a dry salt pan, with its depth.',
  elevation: 'Height above sea level (m); negative is the sea floor.',
  biome: 'Biome class (worlds without vegetation layers).',
  biomass: 'Carbon in living plants, tonnes of carbon per hectare (t C/ha).',
  'plant cover': 'The share of the ground shaded by plants, in %.',
  evaporation: 'Actual evaporation from the ground and plants, mm per year.',
  'potential evaporation': 'Potential evapotranspiration (PET): what a well-watered surface would evaporate, mm per year.',
  runoff: 'Rain minus evaporation: what feeds the rivers, mm per year.',
  'last glaciated': 'When the cell was last under ice, Myr before this moment (its landforms may still show it).',
  soil: 'The soil type (WRB / USDA names in brackets), what it formed on, its rootable depth, fertility (0 poor to 1 rich), the water it holds for plants (mm), its organic carbon (kg C/m² in the top metre) and its drainage.',
  'soil, also': 'Peat thickness, permafrost and wind-blown silt (loess) where there is some.',
  'coastal life': 'Coral reef, kelp forest and seagrass meadow (on the shallow sea floor), mangrove and salt marsh (land between the tides): the share of the cell each covers, in % (planet/coastal.py).',
  mud: 'Suspended sediment from the rivers at the sea surface, in mg/L: clear sea ~0.5; coral reefs need it under ~10, and seagrass and kelp need the light it takes.',
  upwelling: 'How much cold, nutrient-rich deep water welling up cools the sea surface here, in °C (feeds kelp forests and fisheries).',
};
// the hover card's peoples rows: this frame's leading people (its share, how many mix), the overlay
// (template / contact hybrid), and every people's share here at the present (layers/presence_present.bin)
function peoplesRows(i, R) {
  const L = S.V.layers, m = S.V.run.meta, lines = m.lineages || [], d = L.peoples[i], o = L.peoples_overlay?.[i];
  const mixn = L.peoples_mix?.[i] || 0;
  R('place', '', d !== 255 && lines[d] ? `${lines[d].name}${isSeaPeople(lines[d]) ? ' (at sea)' : ''} ${L.peoples_share?.[i] ?? ''}%${mixn >= 2 ? ` (${mixn} peoples mix here)` : ''}` : 'nobody',
    { lab: 'peoples (this frame)', ess: true });
  const dm = demeOf(i);  // (the regional population, PW-981: when the demes layer is loaded)
  if (dm) {
    const D = S.V.demes.demes, par = dm.parent != null ? D[dm.parent] : null;
    R('place', '', `${dm.name}, ${dm.how === 'first' ? `there when the cut starts (~${dm.born_kyr} kyr ago)` : `since ~${dm.born_kyr} kyr ago`}${par ? ` (${{ split_gap: 'split by a gap from', split_distance: 'budded off', crossing: 'founded over the sea from', from_people: 'arose from' }[dm.how] || 'from'} ${par.short})` : ''}`,
      { lab: 'regional population', ess: true });
  }
  const wd = L.peoples_whole?.[i];  // the cell's composition (PW-689): leading people, second, all others
  const ml = L.mix_lead ? L.mix_lead[i] : wd;  // (the people with most heads, PW-705)
  if (L.mix_lead_share && wd != null && wd !== 255 && lines[ml]) {
    const sd = L.mix_second[i], ot = L.mix_other_share[i];
    R('place', '', `${lines[ml].name} ${L.mix_lead_share[i]}%${sd !== 255 && lines[sd] ? `, ${lines[sd].name} ${L.mix_second_share[i]}%` : ''}${ot ? `, others ${ot}%` : ''}`,
      { lab: 'who lives here', ess: true });
  }
  for (const k of Object.keys(S.V.run.layers).filter((x) => x.startsWith('body_')))  // body traits that are population shares (lactase persistence...)
    if (L[k] && wd !== 255) R('place', '', `${L[k][i]}% ${({ milk: 'digest milk as adults', sweet: 'taste sweet', capsaicin: 'feel capsaicin heat', raw_meat: 'eat raw meat safely', cellulose: 'digest cellulose' })[k.slice(5)] || k.slice(5)}`,
      { lab: 'of its people', ess: true });
  if (o != null && o !== 255 && lines[o]) R('place', '', `${lines[o].name}`, { lab: 'among them', ess: true });
  const pp = m.presence_present;
  if (pp && S.V.presence === undefined && S.V.presenceFor !== S.V.run.id) {
    S.V.presenceFor = S.V.run.id;
    fetch(`../runs/${S.V.run.id}/${pp.file}`).then((r) => r.arrayBuffer()).then((b) => { S.V.presence = new Uint8Array(b); }).catch(() => {});
  }
  if (S.V.presence && S.V.presenceFor === S.V.run.id) {
    const n = pp.shape[1], here = lines.map((l, k) => [S.V.presence[k * n + i], l]).filter(([v]) => v >= 12).sort((a, b) => b[0] - a[0]);
    R('place', '', here.length ? here.map(([v, l]) => `${l.name} ${v}%`).join(', ') : 'nobody', { lab: 'at the present', ess: true });
  }
}
function animalRows(i, R) {  // the animals known in this frame's cell, and the wild ranges it lies in (animals.py)
  const L = S.V.layers;
  if (!L.animal_wild) return;
  const known = [], wild = [];
  for (const [id, st] of Object.entries(animalStocks())) {
    if (((L.animal_known?.[i] || 0) >> st.bit) & 1) known.push(st.label);
    else if (((L.animal_wild?.[i] || 0) >> st.bit) & 1 && id !== 'dog') wild.push(st.label);
  }
  if (known.length) R('place', '', known.join(', '), { lab: 'animals known', ess: true });
  if (wild.length) R('place', '', wild.join(', '), { lab: 'wild range of' });
}
function cellInfo(i) {
  const L = S.V.layers, G = S.V.grid, rows = [];
  const R = (g, k, v, o = {}) => rows.push({ g, k, v: String(v), sep: o.sep ?? ' ', ess: !!o.ess, join: o.join, lab: o.lab, extra: o.extra });
  const land = L.elevation[i] > 0;
  if (S.V.kind === 'run') R('place', 't', timeLabel(S.V.t), { sep: ' = ', ess: true });
  R('place', 'cell', `${i}${S.V.pentagons.includes(i) ? ' (pentagon!)' : ''}`, { ess: true });
  R('place', '', `lat ${G.lat[i].toFixed(1)}, lon ${G.lon[i].toFixed(1)}`, { lab: 'position', ess: true });
  R('place', 'elevation', `${L.elevation[i]} m${S.V.tz ? ' (above this moment\'s sea level)' : ''}`, { ess: true });
  const lk = (L.lake_kind || L.lake) && lakeLine(i);
  if (lk) R('place', '', lk, { lab: 'lake', ess: true });
  if (S.V.run?.meta?.phase === 'lineages' && L.peoples) { peoplesRows(i, R); if (state.layer === 'technology') techRows(i, R); animalRows(i, R); cropRows(i, R); anthroRows(i, R); fuelRows(i, R); }
  if (S.V.kind === 'world' && S.V.wAnthro && state.anthro !== false) { anthroRows(i, R); fuelRows(i, R); }
  const vl = S.V.kind === 'world' && volcLine(i);
  if (vl) R('place', 'volcano', vl, { sep: ': ', ess: true });
  const vegRows = () => {
    if (!L.vegetation || !land) return;
    const t = S.V.vegTypes[L.vegetation[i]];
    R('plants', 'vegetation', t ? t.name : '?', { sep: ': ', ess: true });
    if (L.veg_Moss) {  // a world: the mix
      const mix = S.V.pfts.map((p) => [L['veg_' + p.code]?.[i] || 0, p]).filter(([f]) => f >= 3).sort((a, b) => b[0] - a[0]);
      if (mix.length) R('plants', '', mix.slice(0, 4).map(([f, p]) => `${f}% ${p.name}`).join(', '), { lab: 'main plant types' });
      let first = true;
      const bit = (k, v, ess) => { R('plants', k, v, { join: first ? undefined : ' · ', ess }); first = false; };
      if (L.canopy_height[i] > 0) bit('canopy', `${L.canopy_height[i]} m`);
      bit('trees', `${L.tree_cover[i]}%`, true); bit('NPP', `${L.npp[i]} g C/m²/yr`, true);
      const fr = L.fire_return[i];
      if (fr > 0) R('plants', 'fires', `every ~${fr < 10 ? fr : Math.round(fr / 10) * 10} yr`);
      else R('plants', '', 'no fires', { lab: 'fires' });
      if (L.tree_cover[i] >= 10) R('plants', 'stands', `~${L.stand_age[i]} yr old`, { join: ' · ' });
      if (L.lai_jul) R('plants', 'leaves', `LAI ${L.lai_jul[i].toFixed(1)} Jul, ${L.lai_jan[i].toFixed(1)} Jan`, { sep: ': ', join: ' · ' });
      if (L.flooded && L.flooded[i] >= 10) R('plants', 'flooded part of the year', `${L.flooded[i]}% of the cell`, { sep: ': ' });
      if (L.plant_cover) R('plants', 'plant cover', `${L.plant_cover[i]}%`, { extra: true });
      if (L.biomass) R('plants', 'biomass', `${L.biomass[i]} t C/ha`, { extra: true });
    } else if (L.tree_cover) {
      R('plants', 'trees', `${Math.round(L.tree_cover[i])}%`, { ess: true });
      R('plants', 'NPP', `${Math.round(L.npp[i])} g C/m²/yr`, { join: ' · ', ess: true });
    }
  };
  const landformRows = () => {
    if (!L.landform || !S.V.landforms.length || !land) return;
    const f = S.V.landforms[L.landform[i]];
    if (!f) return;
    R('ground', 'landform', f.name + (f.age && L.landform_age ? ` (${f.age} ${Math.round(L.landform_age[i])} Myr)` : ''), { sep: ': ', ess: true });
    if (L.strata_top) {
      const top = S.V.rocks[L.strata_top[i]], next = S.V.rocks[L.strata_next[i]];
      R('ground', 'strata', L.strata_top_km[i] > 0 ? `${top.name.split(' (')[0]} ${L.strata_top_km[i].toFixed(2)} km over ${next.name.split(' (')[0]}`
                                                   : `none, ${top.name.split(' (')[0]} exposed`, { sep: ': ' });
      if (L.fold_wavelength && L.fold_wavelength[i] > 0)
        R('ground', 'folded', `dips ~${Math.round(L.strata_dip[i])}°, fold crests ~${Math.round(L.fold_wavelength[i])} km apart`, { sep: ': ' });
      else if (L.strata_dip && L.strata_top_km[i] > 0) R('ground', '', `flat-lying, regional dip ${L.strata_dip[i].toFixed(2)}°`, { lab: 'strata dip' });
    }
  };
  const soilRows = () => {
    if (!L.soil || !land || !L.soil[i]) return;
    const t = S.V.soilTypes[L.soil[i]];
    if (!t) return;
    const lo = L.loess[i], tex = S.V.soilTextures[L.soil_texture[i]];
    R('soil', 'soil', `${t.name} (${t.wrb} / ${t.usda})` + (lo >= 1 ? ` on loess ${lo.toFixed(0)} m` : `, ${tex}`) +
      ` · ${L.soil_depth[i].toFixed(1)} m deep · fertility ${L.soil_fertility[i].toFixed(1)} · holds ${L.soil_water[i]} mm` +
      ` · ${L.soil_carbon[i].toFixed(0)} kg C/m² · ${S.V.soilDrainage[L.soil_drainage[i]]} drained`, { sep: ': ', ess: true });
    const also = [];
    if (L.peat_depth[i] > 0) also.push(`peat ${L.peat_depth[i].toFixed(1)} m`);
    if (L.permafrost[i] > 0) also.push(`${S.V.soilPermafrost[L.permafrost[i]]} permafrost`);
    if (lo > 0.05 && lo < 1) also.push(`loess ${lo.toFixed(1)} m`);
    if (also.length) R('soil', '', also.join(', '), { lab: 'soil, also' });
  };
  // game attributes (gameattrs.py, PW-206): a line for players, then the numbers
  const gameRows = () => {
    if (!L.travel || !L.travel[i]) return;
    R('game', '', gameSentence(L, i), { lab: 'for players' });  // (More detail only, PW-840)
    const sc = (k) => `${SCORE_WORDS[Math.round(L[k][i])]} (${L[k][i].toFixed(1)})`;
    R('game', 'on foot', `×${L.travel[i].toFixed(1)} the time of open ground · sightlines ${sightText(L.sightline[i])}`, { sep: ': ' });
    R('game', 'yields', `grazing ${sc('grazing')} · foraging ${sc('foraging')} · timber ${sc('timber')} · fuel ${sc('fuel')}`, { sep: ': ' });
    R('game', 'ground', `building ${sc('building')}` + (L.mud_months[i] ? ` · mud ${L.mud_months[i]} months` : ' · no mud season'), { sep: ': ' });
    const g = monthRuns(L.green_months[i]), f = monthRuns(L.fire_months[i]);
    R('game', 'seasons', (g ? `green ${g}` : 'never green') + (f ? ` · fire weather ${f}` : ' · does not burn'), { sep: ': ' });
    const hz = (S.V.gameLeg?.hazards || []).filter((h) => (L.hazards[i] >> h.bit) & 1).map((h) => h.name);
    if (hz.length) R('game', 'hazards', hz.join(', '), { sep: ': ', ess: true });
  };
  // human use (humanuse.py): navigable reach, harbour, pass, farmland, fresh water
  const humanRows = () => {
    const H = S.V.humanUse, nm = (k) => H[k]?.[L[k][i]]?.name;
    if (L.river_nav && land && L.river_nav[i]) R('water', 'navigable', nm('river_nav'), { sep: ': ', ess: true });
    if (L.harbour && !land && L.harbour[i]) R('water', 'harbour', nm('harbour'), { sep: ': ', ess: true });
    if (L.pass && L.pass[i]) R('place', 'mountain pass', `${Math.round(L.pass_height[i])} m, ${nm('pass')}`, { sep: ': ', ess: true });
    if (L.fertile && land) R('soil', 'farmland', `${nm('fertile')} (score ${(L.fertile_score[i] / 100).toFixed(2)})`, { sep: ': ' });
    if (L.fresh_water && land) R('water', 'fresh water', `${nm('fresh_water')}${L.fresh_km[i] > 0 ? `, ${Math.round(L.fresh_km[i])} km away` : ''}${L.spring && L.spring[i] ? ', springs here' : ''}`, { sep: ': ' });
  };
  if (S.V.kind === 'world') {
    if (L.vegetation) vegRows();
    else R('plants', 'biome', S.V.biomes[L.biome[i]].name, { ess: true });
    soilRows();
    humanRows();
    gameRows();
    resRows(L, i, land, R);
    const s = L.temperature_jul ? state.season : '', yr = L.temperature_jul ? ' (year)' : '';
    if (s) R('climate', SEASON_NAMES[s], `${L['temperature_' + s][i]} °C, rain ${L['precipitation_' + s][i]} mm/yr` +
      ` (${s === 'jul' ? 'Apr–Sep' : 'Oct–Mar'} rate)`, { sep: ': ', ess: true });
    R('climate', 'temp', `${L.temperature[i]} °C${yr}` + (L.temperature_jul && !s ? `, July ${L.temperature_jul[i]}, January ${L.temperature_jan[i]}` : ''), { ess: true });
    R('climate', 'rain', `${L.precipitation[i]} mm/yr${yr}` + (L.precipitation_jul && !s ? `, July half ${L.precipitation_jul[i]}, January half ${L.precipitation_jan[i]}` : ''), { ess: true });
    R('water', ...riverRow(i), { ess: true });
    if (L.surface_rock) R('ground', 'surface', S.V.rocks[L.surface_rock[i]].name, { sep: ': ' });
    if (L.climate && land) R('climate', 'climate', `${S.V.koppen[L.climate[i]].code} (${S.V.koppen[L.climate[i]].name}), ` +
      `months ${Math.round(L.cold_month[i])} to ${Math.round(L.warm_month[i])} °C`, { ess: true });
    if (L.ice && L.ice[i] > 0) R('place', 'ice', `~${Math.round(L.ice[i])} m thick`, { ess: true });
    if (L.rock) {
      R('ground', 'rock', S.V.rocks[L.rock[i]].name, { sep: ': ' });
      R('ground', 'sediment cover', `${L.sediment_cover[i].toFixed(1)} km`);
      if (L.crust_thickness) R('ground', 'crust', `${Math.round(L.crust_thickness[i])} km thick`);  // (worlds from before it was stored have none)
    }
    landformRows();
    if (L.wave_power && !land) R('water', 'waves', `${L.wave_power[i].toFixed(1)} kW/m, tides ${L.tide_range[i].toFixed(1)} m`);
    if (L.reef && coastalText(i)) R('plants', 'coastal life', coastalText(i), { sep: ': ', ess: true });
    if (L.coast_type && coastText(i)) R('ground', 'coast', coastText(i), { sep: ': ', ess: true });
    if (L.nav_hazard && !land && L.nav_hazard[i] >= 0.3) R('water', 'hazard to ships', L.nav_hazard[i].toFixed(2), { sep: ': ' });
    if (L.turbidity && !land) R('water', 'mud', `${L.turbidity[i].toFixed(1)} mg/L in the water`, { sep: ': ', extra: true });
    if (L.upwelling && !land && L.upwelling[i] >= 0.3) R('water', 'upwelling', `cools the sea ${L.upwelling[i].toFixed(1)} °C`, { sep: ': ' });
    if (L.sst && !land) {
      R('water', 'sea', `${L.sst[i].toFixed(1)} °C (July ${L.sst_jul[i].toFixed(1)}, January ${L.sst_jan[i].toFixed(1)}), ` +
        `salinity ${L.salinity[i].toFixed(2)} psu`, { ess: true });
      if (L.sinking[i] >= 0.005) R('water', 'deep water sinks here', `${L.sinking[i].toFixed(2)} Sv`, { sep: ': ' });
    }
    if (L.humidity_jul) R('climate', 'humidity', `July ${L.humidity_jul[i]}% (dew point ${L.dewpoint_jul[i]} °C), ` +
      `January ${L.humidity_jan[i]}% (${L.dewpoint_jan[i]} °C)`, { sep: ': ' });
    if (L.cloud_jul) R('climate', 'sky', `July ${L.cloud_jul[i]}% cloud, ${L.sunshine_jul[i].toFixed(1)} h of sun a day; ` +
      `January ${L.cloud_jan[i]}%, ${L.sunshine_jan[i].toFixed(1)} h`, { sep: ': ' });
    if (land && L.evaporation) R('water', 'evaporation', `${L.evaporation[i]} mm/yr`, { extra: true });
    if (land && L.pet) R('water', 'potential evaporation', `${L.pet[i]} mm/yr`, { extra: true });
    if (land && L.runoff) R('water', 'runoff', `${L.runoff[i]} mm/yr`, { extra: true });
    if (L.glaciated_myr && land && L.glaciated_myr[i] < 9999)  // (9999: never under ice)
      R('place', 'last glaciated', L.glaciated_myr[i] > 0 ? `${L.glaciated_myr[i]} Myr ago` : 'under ice now', { extra: true });
    if (L.obs_temperature) {  // the Earth reference world
      const ot = L.obs_temperature[i], op = L.obs_precipitation[i], ok = L.obs_climate[i];
      if (ot != null) R('observed', 'observed', `${ot} °C` + (L.obs_cold_month[i] != null
        ? `, months ${Math.round(L.obs_cold_month[i])} to ${Math.round(L.obs_warm_month[i])} °C` : ''), { sep: ': ' });
      if (op != null && land) R('observed', 'observed rain', `${Math.round(op)} mm/yr`);
      if (ok >= 0 && land) R('observed', 'observed climate', `${S.V.koppen[ok].code} (${S.V.koppen[ok].name})`);
      const os = L.obs_sunshine?.[i];
      if (os != null && land) R('observed', 'observed sunshine', `${os.toFixed(1)} h a day (CRU)`);
    }
  }
  if (S.V.tz) {  // glacial time zoom: no rock or rain layers
    if (L.temperature) {
      const k = L.climate && S.V.koppen[L.climate[i]];
      R('climate', 'mean', `${L.temperature[i]} °C` + (land && k ? `, climate ${k.code} (${k.name})` : ''), { ess: true });
    }
    if (L.ice && L.ice[i]) R('place', 'ice', `~${Math.round(L.ice[i])} m thick`, { ess: true });
  }
  if (L.plate && !S.V.tzEarth) {
    R('plates', 'plate', `${L.plate[i]}` + (L.crust ? ` (${L.crust[i] ? 'continental' : 'oceanic'})` : ''), { ess: S.V.kind === 'run' });
    if (L.crust_age && L.crust) R('plates', `${L.crust[i] ? 'rock' : 'sea floor'} age`, `${Math.round(L.crust_age[i])} Myr`);
    const v = plateVelocity(i);
    if (v && (S.V.kind === 'run' || S.V.meta.method === 'tectonics')) R('plates', 'moving', `${(Math.hypot(...v) * CMYR).toFixed(1)} cm/yr`, { ess: S.V.kind === 'run' });
    if (L.plate_boundary && L.plate_boundary[i]) R('plates', '', L.plate_boundary[i] > 0 ? 'converging boundary' : 'diverging boundary', { lab: 'boundary', ess: S.V.kind === 'run' });
  }
  if (S.V.kind === 'run' && !S.V.tz) {  // a run frame: only the layers loaded so far (those on screen)
    if (L.surface_rock) R('ground', 'surface', S.V.rocks[L.surface_rock[i]].name, { sep: ': ', ess: state.layer === 'surface rock' });
    if (L.rock) R('ground', 'rock', S.V.rocks[L.rock[i]].name, { sep: ': ', ess: state.layer === 'rock type' });
    if (L.sediment_cover) R('ground', 'sediment cover', `${L.sediment_cover[i].toFixed(1)} km`, { ess: state.layer === 'sediment' });
    if (L.crust_thickness) R('ground', 'crust', `${L.crust_thickness[i]} km thick`, { ess: state.layer === 'crust thickness' });
    if (L.precipitation && land) R('climate', 'rain', `${L.precipitation[i]} mm/yr`, { ess: true });
    landformRows();
    vegRows();
    if (L.climate && land) {
      const k = S.V.koppen[L.climate[i]];
      R('climate', 'climate', `${k.code} (${k.name})`, { ess: true });
    }
    if (L.temperature) R('climate', 'mean', `${L.temperature[i]} °C`, { ess: true });
    if (L.ice && L.ice[i] && land) R('place', 'ice', `~${Math.round(L.ice[i])} m thick` + (L.bed ? `, bed ${Math.round(L.bed[i])} m` : ''), { ess: true });
  }
  return rows;
}

// the text of cellInfo's rows: one line per row (or joined to the line before)
function infoLines(rows) {
  const lines = [];
  for (const r of rows) {
    if (r.extra) continue;
    const s = r.k ? r.k + r.sep + r.v : r.v;
    if (r.join && lines.length) lines[lines.length - 1] += r.join + s; else lines.push(s);
  }
  return lines;
}
export function describe(i) { return infoLines(cellInfo(i)); }

// the river through cell i: discharge (flow x cell area / 1 yr) and, in worlds with the rivers' year (PW-028),
// when it peaks, how much above its mean month, and how long it's frozen -> [label, value]
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                     'November', 'December'];
function riverRow(i) {
  const L = S.V.layers, q = L.flow[i] * 4 * Math.PI * 6.371e6 ** 2 / S.V.n / 3.156e7;
  const qs = q >= 100 ? Math.round(q).toLocaleString('en-US') : q >= 1 ? q.toFixed(0) : q.toFixed(1);
  let s = `~${qs} m³/s`;
  if (L.flood_ratio && L.elevation[i] > 0 && L.flood_month[i] > 0) {
    s += `, highest in ${MONTH_NAMES[L.flood_month[i] - 1]} (${L.flood_ratio[i].toFixed(1)}× its mean month)`;
    if (L.river_frozen && L.river_frozen[i] > 0) s += `, frozen ${L.river_frozen[i]} month${L.river_frozen[i] > 1 ? 's' : ''}`;
  }
  return ['river', s];
}

// the label of a row as HTML, with its hint (a dotted underline; the hint on hover)
function infoLabel(r) {
  const lab = r.k || r.lab || '';
  const h = HINTS[lab];
  return h ? `<span class="hint" title="${esc(h)}">${esc(lab)}</span>` : esc(lab);
}
// a row's value as HTML: NPP, LAI, psu, Sv get their own hint where they appear inside a value
const TERM_HINTS = { NPP: HINTS.NPP, LAI: HINTS.LAI, psu: HINTS.sea, Sv: HINTS['deep water sinks here'] };
function infoValue(v) {
  return esc(v).replace(/\b(NPP|LAI|psu|Sv)\b/g, (m) => `<span class="hint" title="${esc(TERM_HINTS[m])}">${m}</span>`);
}
function infoRowsHtml(rows) {
  return rows.map((r) => `<div class="k">${infoLabel(r)}</div><div class="v">${infoValue(r.v)}</div>`).join('');
}
// the compact info box: the essentials, two columns (bold labels), and a button for the rest
export function infoBoxHtml(i) {
  const rows = cellInfo(i), ess = rows.filter((r) => r.ess && !['cell', 'position', 't'].includes(r.k || r.lab));
  const head = rows.find((r) => r.k === 'cell'), pos = rows.find((r) => r.lab === 'position'), t = rows.find((r) => r.k === 't');
  const more = rows.length - ess.length - [head, pos, t].filter(Boolean).length;
  return `<div class="ihead"><b>cell ${esc(head.v)}</b> <span class="muted">${esc(pos.v)}${t ? ' · ' + esc(t.v) : ''}</span></div>
    <div class="igrid">${infoRowsHtml(ess)}</div>` +
    (more > 0 ? `<button class="btn imore" data-act="more" title="Everything about this cell (Esc closes)">More detail (${more})…</button>` : '');
}

// the "more detail" panel: every row, by group, and a climograph for worlds
export function openDetail(i) { S.detailCell = i; renderDetail(); $('detail').hidden = false; }
export function closeDetail() { S.detailCell = -1; $('detail').hidden = true; }
export function renderDetail() {
  if (S.detailCell < 0 || !S.V) return;
  const i = S.detailCell, rows = cellInfo(i), G = S.V.grid;
  const groups = {};
  for (const r of rows) if (!['cell', 't'].includes(r.k) && r.lab !== 'position') (groups[r.g] ||= []).push(r);
  const secs = Object.keys(GROUPS).filter((g) => groups[g]).map((g) =>
    `<section><h3>${GROUPS[g]}</h3><div class="igrid">${infoRowsHtml(groups[g])}</div></section>`).join('');
  $('detailBody').innerHTML = `<div class="dhead"><b>cell ${i}</b>${S.V.pentagons.includes(i) ? ' (pentagon)' : ''}
      <span class="muted">· lat ${G.lat[i].toFixed(2)}, lon ${G.lon[i].toFixed(2)} · ${esc(S.V.name || S.V.id || '')}${S.V.kind === 'run' ? ' · t = ' + esc(timeLabel(S.V.t)) : ''}</span></div>
    ${climograph(i) || seasonChart(i)}<div class="dgrid">${secs}</div>
    <p class="muted">Hover a dotted label for what it means and its units. ${S.V.kind === 'run' ? 'A run frame shows only the layers the picture draws (the colour layer and overlays picked).' : ''}</p>`;
}
// A world cell's twelve months (GET /api/cell: the server runs climate.months on the cell's
// stored climate; worlds don't store months) as a climograph: rain bars (mm in the month,
// right axis) and the temperature line (°C, left axis). Until the months come (or with no
// server, e.g. a dropped file) the panel shows seasonChart. Runs: no chart (their keyframes
// don't carry what the months are built from).
const cellMonths = new Map();  // `${world}:${cell}` -> {t, p} | 'pending' | 'failed'
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
function climograph(i) {
  if (S.V.kind !== 'world' || !S.V.id) return '';
  const key = `${S.V.id}:${i}`, m = cellMonths.get(key);
  if (!m) {
    cellMonths.set(key, 'pending');
    const v = S.V;
    fetch(`../api/cell?world=${encodeURIComponent(S.V.id)}&i=${i}`, { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d) => cellMonths.set(key, d), () => cellMonths.set(key, 'failed'))
      .then(() => { if (S.V === v && S.detailCell === i) renderDetail(); });
  }
  if (!m || typeof m === 'string') return '';
  const W = 520, H = 182, x0 = 34, x1 = W - 40, y0 = 20, y1 = 134, cw = (x1 - x0) / 12;
  const tmin = Math.min(-10, Math.floor(Math.min(...m.t) / 10) * 10), tmax = Math.max(30, Math.ceil(Math.max(...m.t) / 10) * 10);
  const ptop = Math.max(100, ...m.p), pstep = [25, 50, 100, 200, 250, 500, 1000, 2000].find((d) => ptop / d <= 5) || 5000;
  const pmax = Math.ceil(ptop / pstep) * pstep;
  const ty = (t) => y1 - (y1 - y0) * (t - tmin) / (tmax - tmin), py = (p) => y1 - (y1 - y0) * p / pmax;
  const cx = (k) => x0 + (k + 0.5) * cw;
  let s = `<svg class="schart" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Monthly temperature and rain">`;
  for (let t = tmin; t <= tmax; t += 10)
    s += `<line x1="${x0}" x2="${x1}" y1="${ty(t)}" y2="${ty(t)}" class="${t === 0 ? 'zero' : 'grid'}"/><text x="${x0 - 4}" y="${ty(t) + 3}" class="tlab" text-anchor="end">${t}</text>`;
  for (let p = 0; p <= pmax; p += pstep) s += `<text x="${x1 + 4}" y="${py(p) + 3}" class="rlab">${p}</text>`;
  s += `<text x="0" y="8" class="tlab">°C</text><text x="${x1 + 4}" y="8" class="rlab">mm</text>`;
  m.t.forEach((t, k) => {
    const p = m.p[k];
    s += `<g class="mon"><title>${MON[k]}: ${t.toFixed(1)} °C, ${Math.round(p)} mm</title><rect x="${x0 + k * cw}" y="${y0}" width="${cw}" height="${y1 - y0}" class="mcol"/>` +
      `<rect x="${cx(k) - cw * 0.32}" y="${py(p)}" width="${cw * 0.64}" height="${Math.max(y1 - py(p), 0.5)}" rx="2" class="pbar"/>` +
      `<circle cx="${cx(k)}" cy="${ty(t)}" r="3" class="tdot"/></g>`;
    s += `<text x="${cx(k)}" y="${y1 + 11}" class="tick">${MON[k][0]}</text>`;
  });
  s += `<polyline points="${m.t.map((t, k) => `${cx(k)},${ty(t)}`).join(' ')}" class="tline" pointer-events="none"/>`;
  const ext = (a, f) => a.reduce((b, x, k) => (f(x, a[b]) ? k : b), 0);
  const hot = ext(m.t, (a, b) => a > b), cold = ext(m.t, (a, b) => a < b), wet = ext(m.p, (a, b) => a > b), dry = ext(m.p, (a, b) => a < b);
  const tyr = m.t.reduce((a, b) => a + b, 0) / 12, pyr = m.p.reduce((a, b) => a + b, 0);
  s += `<text x="${x0}" y="${y1 + 28}" class="plab"><tspan class="tlab">year ${tyr.toFixed(1)} °C · warmest ${MON[hot]} ${m.t[hot].toFixed(1)}, coldest ${MON[cold]} ${m.t[cold].toFixed(1)}</tspan>` +
    `<tspan class="rlab" x="${x0}" dy="12">${Math.round(pyr)} mm a year · wettest ${MON[wet]} ${Math.round(m.p[wet])}, driest ${MON[dry]} ${Math.round(m.p[dry])} mm</tspan></text>`;
  return s + '</svg>';
}

// July / year / January temperature and rain of a world cell, as a small SVG (worlds store
// those three, not every month): the temperature dots on a -30..40 °C scale with the
// coldest-warmest month range behind them, the rain as bars (rates per year)
function seasonChart(i) {
  const L = S.V.layers;
  if (S.V.kind !== 'world' || !L.temperature_jul || !L.precipitation_jul) return '';
  const W = 400, H = 128, x0 = 72, x1 = W - 12, tx = (t) => x0 + (x1 - x0) * (Math.min(Math.max(t, -30), 40) + 30) / 70;
  const T = [['Jan', L.temperature_jan[i]], ['year', L.temperature[i]], ['Jul', L.temperature_jul[i]]];
  const P = [['Oct–Mar', L.precipitation_jan[i]], ['year', L.precipitation[i]], ['Apr–Sep', L.precipitation_jul[i]]];
  const pmax = Math.max(500, ...P.map((p) => p[1])), px = (p) => x0 + 0.72 * (x1 - x0) * p / pmax;  // (room for the label after the bar)
  let s = `<svg class="schart" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Temperature and rain by season">`;
  s += `<text x="0" y="12" class="lab">temperature</text>`;
  for (const t of [-30, -10, 0, 10, 20, 30, 40]) s += `<line x1="${tx(t)}" x2="${tx(t)}" y1="4" y2="44" class="${t === 0 ? 'zero' : 'grid'}"/><text x="${tx(t)}" y="54" class="tick">${t}</text>`;
  if (L.cold_month && L.warm_month)
    s += `<rect x="${tx(L.cold_month[i])}" y="14" width="${Math.max(tx(L.warm_month[i]) - tx(L.cold_month[i]), 1)}" height="16" rx="3" class="range"><title>coldest to warmest month: ${Math.round(L.cold_month[i])} to ${Math.round(L.warm_month[i])} °C</title></rect>`;
  T.forEach(([k, t], j) => { s += `<circle cx="${tx(t)}" cy="22" r="4.5" class="t${j}"><title>${k}: ${t} °C</title></circle>`; });
  s += `<text x="${x0}" y="68" class="plab">` + T.map(([k, t], j) => `<tspan class="t${j}">● ${k} ${t} °C</tspan>`).join('  ') +
    (L.cold_month ? `<tspan>  months ${Math.round(L.cold_month[i])}…${Math.round(L.warm_month[i])}</tspan>` : '') + '</text>';
  s += `<text x="0" y="88" class="lab">rain (mm/yr)</text>`;
  P.forEach(([k, p], j) => {
    const y = 79 + j * 16;
    s += `<rect x="${x0}" y="${y}" width="${Math.max(px(p) - x0, 1)}" height="11" rx="2" class="p${j}"><title>${k}: ${p} mm/yr</title></rect>`;
    s += `<text x="${px(p) + 4}" y="${y + 9}" class="plab">${k} ${p}</text>`;
  });
  return s + '</svg>';
}
