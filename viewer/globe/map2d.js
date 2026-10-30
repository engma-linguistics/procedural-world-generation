import * as THREE from 'three';
import * as PM from '../projmap.js';
import * as Relief from '../relief.js';
import { S, proj, state } from './state.js';
import { SEASONAL, cellColors } from './layers.js';
import { $, controls, fitMap, lights, relief3d } from './scene.js';
import { huMapFeatures, setSeason } from './colours.js';
import { buildTopology, nearestCellU, paint } from './geometry.js';
import { buildOverlays } from './overlays.js';
import { axisGroup, lmGroup } from './axis.js';
import { renderLegend } from './panel.js';
import { canRotate, renderHover, toast, updateHover } from './pick.js';
import { pickCell } from './zoom.js';
import { hlGroup } from './highlights.js';
import { zoomOutlines } from './tabs.js';
import { refresh } from './load.js';
// ------------------------------------------------------------ the 2D map (PW-477, projmap.js)
// What the globe shows (the layer under Colour by, its season, the replay frame) drawn into a chosen
// projection centred on a chosen point; click the map to centre it there.
$('projSel').innerHTML = PM.NAMES.map((k) => `<option value="${k}">${PM.LABELS[k]}</option>`).join('');
$('projExt').insertAdjacentHTML('beforeend', [8000, 4000, 2000, 1000, 500, 250, 100].map((k) => `<option value="${k}">${k} km</option>`).join(''));
const projExtent = () => (proj.ext ? [proj.ext, proj.ext] : null);
const fmtLL = (la, lo) => `${Math.abs(la).toFixed(1)}°${la >= 0 ? 'N' : 'S'}, ${Math.abs(lo).toFixed(1)}°${lo >= 0 ? 'E' : 'W'}`;
function projBox() {  // the room the map may use: between the control panel and the right column, below the nav bar, above the timeline
  const wide = innerWidth > 1000, l = innerWidth > 700 ? 300 : 8, r = wide ? 340 : 8;
  return { l, t: 60, w: Math.max(100, innerWidth - l - r), h: Math.max(100, innerHeight - 60 - 96) };
}
// PW-860: the overlays of the live map (rivers, events, highlights, zoom outlines, tropics, tracks, labels...)
// are three.js objects whose map-mode positions are (lon / 90, lat / 90); read back as (lat, lon) they go through
// the chosen projection's forward map. So every overlay the equirectangular map draws shows here too, without a second
// description of each. (The human-use ribbons have their own map form, huMapFeatures; their three.js objects are skipped.)
let projDirty = false;
export function projOverlaysChanged() {  // overlays were rebuilt: redraw the canvas once, after whatever else this frame does
  if (!proj.on || projDirty) return;
  projDirty = true;
  requestAnimationFrame(() => { if (projDirty) drawProj(); });
}
function projFeatures(cssW) {
  const feats = huMapFeatures() || { lines: [], marks: [] }, buckets = new Map(), labels = [];
  const hex = (c) => '#' + c.getHexString(THREE.SRGBColorSpace);
  const add = (color, alpha, width, a, b) => {
    const key = `${color}|${alpha}|${width}`;
    let e = buckets.get(key);
    if (!e) buckets.set(key, e = { color, alpha, width, pts: [] });
    e.pts.push(a, b);
  };
  const ll = (x, y) => [y * 90, x * 90];
  const col = new THREE.Color();
  const visit = (o) => {
    if (o.visible === false) return;
    if (o.isSprite) {
      const img = o.material.map?.image;
      if (img) labels.push({ lat: o.position.y * 90, lon: o.position.x * 90, img, w: o.scale.x, h: o.scale.y, px: o.userData.px });
      return;
    }
    const m = o.material;
    if (o.isLineSegments2) {
      const g = o.geometry, A = g.attributes.instanceStart, B = g.attributes.instanceEnd, C = g.attributes.instanceColorStart;
      if (!A) return;
      const w = m.linewidth, al = m.opacity;
      for (let i = 0; i < A.count; i++) {
        let c;
        if (C) { col.setRGB(C.getX(i), C.getY(i), C.getZ(i)); c = hex(col); } else c = hex(m.color);
        add(c, al, w, ll(A.getX(i), A.getY(i)), ll(B.getX(i), B.getY(i)));
      }
    } else if (o.isLineSegments && o.geometry.attributes.position) {
      const P = o.geometry.attributes.position, c = hex(m.color), al = m.opacity;
      for (let i = 0; i + 1 < P.count; i += 2) add(c, al, 1, ll(P.getX(i), P.getY(i)), ll(P.getX(i + 1), P.getY(i + 1)));
    }
  };
  for (const [k, o] of Object.entries(S.overlays)) if (!/^hu(Riv|Har|Pass)/.test(k)) visit(o);
  for (const grp of [lmGroup, hlGroup, zoomOutlines, axisGroup]) grp.children.forEach(visit);
  feats.segs = [...buckets.values()];
  feats.labels = labels;
  feats.cssW = cssW;
  return feats;
}
export function drawProj() {
  if (!proj.on || !S.V || !S.lastColors) return;
  const cv = $('projCanvas'), p = PM.makeProjection(proj.name, proj.lat, proj.lon), ext = projExtent();
  const g0 = PM.pixelGrid(p, 1000, ext), aspect = g0.width / g0.height, b = projBox();
  const cssW = Math.floor(Math.min(b.w, b.h * aspect)), cssH = Math.floor(cssW / aspect);
  Object.assign(cv.style, { width: cssW + 'px', height: cssH + 'px', left: b.l + (b.w - cssW) / 2 + 'px', top: b.t + (b.h - cssH) / 2 + 'px' });
  S.V.projCache ??= {};
  proj.grid = PM.drawMap(cv, p, Math.round(cssW * Math.min(devicePixelRatio || 1, 2)), ext, S.lastColors, (x, y, z) => nearestCellU([x, z, -y]),
    { cache: S.V.projCache, gridId: S.V.n, graticule: $('projGrid').checked, marker: true, features: projFeatures(cssW) });
  proj.p = p;
  projDirty = false;
  $('projCentre').textContent = `centre ${fmtLL(proj.lat, proj.lon)}`;
}
// One control: Flat map's projection. The live three.js map is the equirectangular one (overlays, hill
// shading, 3D relief); any other projection is the canvas drawn over it. Only in Flat map, never over the
// globe, and 3D relief (a three.js model) takes the live map back whatever the projection.
export function syncProj() {
  const flat = state.mode === 'map', canvas = flat && proj.name !== 'equirect' && !relief3d();
  const was = proj.on;
  proj.on = canvas;
  $('flatOpts').hidden = !flat;
  $('projSel').value = proj.name;
  $('projSel').disabled = relief3d();
  $('projSel').title = relief3d() ? 'The 3D relief is the equirectangular map; untick 3D relief to use another projection' : '';
  $('projBox').hidden = !canvas;
  $('projView').hidden = !canvas;
  if (canvas) {
    if (!was && S.picked && proj.lat === 0 && proj.lon === 0) { proj.lat = S.picked.lat; proj.lon = S.picked.lon; }
    $('projExt').value = proj.ext || '';
    if (S.V) { if (!S.lastColors) S.lastColors = cellColors(state.layer); drawProj(); }
  } else if (was) { S.hovered = -1; renderHover(); }
  const u = new URL(location);
  ['mode', 'proj', 'map2d'].forEach((k) => u.searchParams.delete(k));
  if (flat) { u.searchParams.set('mode', 'map'); if (proj.name !== 'equal-earth') u.searchParams.set('proj', proj.name); }
  history.replaceState(null, '', u);
}
function projCell(e) {
  if (!proj.grid) return null;
  const cv = $('projCanvas'), r = cv.getBoundingClientRect();
  const ll = PM.pixelToLatLon(proj.p, proj.grid, (e.clientX - r.left) * cv.width / r.width, (e.clientY - r.top) * cv.height / r.height);
  return ll && { ...ll, cell: nearestCellU([ll.p[0], ll.p[2], -ll.p[1]]) };
}
$('projSel').addEventListener('change', (e) => { proj.name = e.target.value; syncProj(); });
$('projExt').addEventListener('change', (e) => { proj.ext = e.target.value ? +e.target.value : null; drawProj(); });
$('projGrid').addEventListener('change', drawProj);
$('projPick').addEventListener('click', () => { if (!S.picked) return toast('Pick a cell on the globe first'); proj.lat = S.picked.lat; proj.lon = S.picked.lon; drawProj(); });
$('projPng').addEventListener('click', () => {
  if (!proj.on || !S.V || !S.lastColors) return;
  const cv = document.createElement('canvas'), p = PM.makeProjection(proj.name, proj.lat, proj.lon);
  S.V.projCachePng ??= {};
  PM.drawMap(cv, p, 2048, projExtent(), S.lastColors, (x, y, z) => nearestCellU([x, z, -y]), { cache: S.V.projCachePng, gridId: S.V.n, graticule: $('projGrid').checked, marker: false, features: huMapFeatures() });
  const name = [S.V.name || S.V.id || S.V.dir || 'planet', state.layer, proj.name, `${proj.lat.toFixed(1)}_${proj.lon.toFixed(1)}`, proj.ext && proj.ext + 'km'].filter(Boolean).join('-').replace(/[^\w.-]+/g, '_') + '.png';
  cv.toBlob((blob) => { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); toast('Saved ' + name); }, 'image/png');
});
{
  let down = null;
  const cv = $('projCanvas');
  cv.addEventListener('pointerdown', (e) => { down = [e.clientX, e.clientY]; });
  cv.addEventListener('pointermove', (e) => { const h = projCell(e); S.hovered = h ? h.cell : -1; renderHover(); });
  cv.addEventListener('pointerleave', () => { S.hovered = -1; renderHover(); });
  cv.addEventListener('pointerup', (e) => {
    if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4) return;
    const h = projCell(e);
    if (!h) return;
    if (e.ctrlKey || e.metaKey) { pickCell(h.cell); toast('Cell picked for zooming (the Zoom box on the globe)'); return; }
    proj.lat = +h.lat.toFixed(2); proj.lon = +h.lon.toFixed(2);
    drawProj();
  });
}
addEventListener('resize', () => { if (proj.on) drawProj(); });
// ?mode=map&proj=laea&center=48.5,-2&extent=2000 opens the map (screenshots, links; map2d= is the old name of proj=)
export function applyProjUrl() {
  const q = new URLSearchParams(location.search), nm = q.get('proj') || q.get('map2d');
  if (!nm || !PM.NAMES.includes(nm)) { syncProj(); return; }
  state.mode = 'map'; [...$('modeSeg').children].forEach((b) => b.classList.toggle('on', b.dataset.v === 'map')); canRotate();
  proj.name = nm;
  const c = (q.get('center') || '').split(',').map(Number);
  if (c.length === 2 && c.every(Number.isFinite)) { proj.lat = Math.max(-90, Math.min(90, c[0])); proj.lon = c[1]; }
  proj.ext = +q.get('extent') || null;
  $('projGrid').checked = q.get('grid') !== '0';
  syncProj();
}
$('smooth').addEventListener('change', paint);
// overlay checkboxes: each id here redraws the overlays when ticked and can be set from the URL (?winds=1)
export const OVERLAY_IDS = ['lmNames', 'peopleTracks', 'settlements', 'settleVillages', 'rivers', 'huRivers', 'huHarbours', 'huPasses', 'outlines', 'pentas', 'arrows', 'events', 'hotspots', 'volcanoes', 'volcExtinct', 'winds', 'currents', 'overturning',
                     'axis', 'tropics', 'clouds'];
OVERLAY_IDS.forEach((id) => $(id).addEventListener('change', () => refresh(() => { buildOverlays(); renderLegend(); })));
// the wind overlay's season: the yearly mean, or the July / January half-year where the world has them
export function windKey() {
  const s = state.season, k = s ? 'wind_' + s : 'wind';
  return s && S.V.layers[k + '_e'] ? k : 'wind';
}
// one season for the winds and the temperature / rain colours (they're shown together)
$('windSeason').addEventListener('change', () => {
  setSeason($('windSeason').value);
  if (state.season) $('winds').checked = true;
  refresh(() => { if (SEASONAL[state.layer]) paint(); else { buildOverlays(); renderLegend(); } updateHover(); });
});
$('layerSeason').addEventListener('change', () => {
  setSeason($('layerSeason').value);
  refresh(() => { paint(); updateHover(); });
});
$('relief').addEventListener('input', () => { $('reliefVal').textContent = $('relief').value + '×'; });
$('relief').addEventListener('change', paint);
// the 3D relief (relief.js): toggle, exaggeration, sun, sea floor; kept in the URL (&relief3d=1&ex=60&sun=135,60&sea=0)
export function reliefLabels() {
  $('reliefBox').hidden = !relief3d();
  $('reliefExV').textContent = $('reliefEx').value + '×';
  $('sunAzV').textContent = $('sunAz').value + '°'; $('sunElV').textContent = $('sunEl').value + '°';
}
function reliefToUrl() {
  const u = new URL(location), D = Relief.DEFAULTS;
  for (const k of ['relief3d', 'ex', 'sun', 'sea']) u.searchParams.delete(k);
  if (relief3d()) {
    u.searchParams.set('relief3d', '1');
    if (+$('reliefEx').value !== D.ex) u.searchParams.set('ex', $('reliefEx').value);
    if (+$('sunAz').value !== D.sunAz || +$('sunEl').value !== D.sunEl) u.searchParams.set('sun', `${$('sunAz').value},${$('sunEl').value}`);
    if (!$('seaFloor').checked) u.searchParams.set('sea', '0');
  }
  history.replaceState(null, '', u);
}
export function setLights() { lights.set(relief3d(), +$('sunAz').value, +$('sunEl').value); }
$('relief3d').addEventListener('change', () => {
  reliefLabels(); setLights(); canRotate();
  if (state.mode === 'map' && !relief3d()) { controls.reset(); fitMap(); }  // (flat again: face on)
  reliefToUrl(); syncProj();
  if (S.V) { buildTopology(); paint(); }
});
let reliefPending = 0;  // (the slider repaints at most once a frame)
$('reliefEx').addEventListener('input', () => {
  reliefLabels(); reliefToUrl();
  if (S.V && !reliefPending) reliefPending = requestAnimationFrame(() => { reliefPending = 0; paint(); });
});
for (const id of ['sunAz', 'sunEl']) $(id).addEventListener('input', () => { reliefLabels(); setLights(); reliefToUrl(); });
$('seaFloor').addEventListener('change', () => { reliefToUrl(); if (S.V) paint(); });
$('riverQ').addEventListener('input', () => { $('riverVal').textContent = 'top ' + (100 - $('riverQ').value).toFixed(1) + '% of land'; });
$('riverQ').addEventListener('change', buildOverlays);
$('riverVal').textContent = 'top ' + (100 - $('riverQ').value).toFixed(1) + '% of land';
