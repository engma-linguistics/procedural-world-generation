import { esc } from '../planets.js';
import { S, state } from './state.js';
import { VEG_VIEWS } from './layers.js';
import { $ } from './scene.js';
import { renderSummary } from './panel.js';
import { finishedOf } from './timezoom.js';
import { projOverlaysChanged } from './map2d.js';
import { buildZoomOutlines } from './tabs.js';
import { setFrame } from './load.js';
import { nearestFrame, stop } from './playback.js';
import { fillSelector, loadSelection, syncFav } from './select.js';
// ------------------------------------------------------------ provenance (PW-128)
// What came from what, from the indexes: each world's source run and time
// (worlds/index.json), each zoom's world (zooms/index.json) and each time
// zoom's source run (runs/index.json). Filled by fillSelector().
  // "run:<dir>" / "world:<id>" the owner starred (GET /api/favourites; kept by the server, not the browser)
try { $('favMode').value = localStorage.getItem('planet.favMode') || 'all'; } catch { /* private window */ }
if (!$('favMode').value) $('favMode').value = 'all';
export const favKeyOf = (v) => v.replace(/\.json$/, '');  // option value -> favourites key
const runOf = (id) => S.IDX.runs.find((r) => r.dir === id || r.id === id);
// a world from a run is "<run name> @ T Myr"; others go by their name
export function worldTitle(w) {
  if (!w.source_run) return w.name;
  if (w.source_run === 'earth') return w.timezoom ? `Earth + ${w.timezoom_kyr} kyr (finished)` : w.name;
  return `${w.source_run_name || runOf(w.source_run)?.name || 'run ' + w.source_run} @ ${w.t_myr} Myr` +
    (w.timezoom ? ` + ${w.timezoom_kyr} kyr (finished)` : '');
}
// a finished world's time zoom and frame, linked to open the time zoom there
export function timezoomLink(tzId, kyr) {
  const r = runOf(tzId);
  return r ? `<a href="?run=${r.dir}&t=${kyr}" data-run="${r.dir}" data-t="${kyr}" title="Open time zoom ${tzId} at +${kyr} kyr">time zoom ${tzId} + ${kyr} kyr</a>`
    : `time zoom ${tzId} + ${kyr} kyr <span class="muted">(deleted)</span>`;
}
// '<run name> @ T Myr', linked to open the run at that time
export function sourceLink(runId, t) {
  const r = runOf(runId), label = `${esc(r?.name || 'run ' + runId)} @ ${t} Myr`;
  return r ? `<a href="?run=${runId}&t=${t}" data-run="${runId}" data-t="${t}" title="Open run ${runId} at ${t} Myr">${label}</a> <span class="muted">(run ${runId})</span>`
    : `${label} <span class="muted">(run ${runId}, deleted)</span>`;
}
// a zoom's id, linked to open it in the Regional zoom tab (its size and place on hover)
const zoomLink = (z) => `<a href="#" data-zoom="${z.id}" title="${esc(z.name)}">${z.id}</a>`;
export function zoomsOf(worldId) {
  const zs = S.IDX.zooms.filter((z) => z.world === worldId);
  return zs.length ? `<span class="muted">Zooms of this world:</span> ${zs.map(zoomLink).join(', ')}<br>` : '';
}
const madeFrom = (runId) => ({
  worlds: S.IDX.worlds.filter((w) => w.source_run === runId && !w.timezoom).sort((a, b) => a.t_myr - b.t_myr),
  tzs: S.IDX.runs.filter((r) => r.kind === 'timezoom' && r.source_run === runId).sort((a, b) => a.at_myr - b.at_myr),
});
// a main run's worlds (with their zooms) and time zooms, as a small tree
export function runTree() {
  const { worlds, tzs } = madeFrom(S.V.dir);
  let html = '<h2 title="Worlds and glacial time zooms made from this run; their times are the ticks above the time slider">Made from this run</h2>';
  if (!worlds.length && !tzs.length) return html + '<span class="muted">nothing yet (a Zoom or Highlights here makes a world at that time)</span>';
  html += '<div class="tree">' + worlds.map((w) => {
    const zs = S.IDX.zooms.filter((z) => z.world === w.id), named = w.name !== worldTitle(w) ? ` <span class="muted">${esc(w.name)}</span>` : '';
    return `<div><a href="#" data-jump="${w.t_myr}" title="Go to ${w.t_myr} Myr">${w.t_myr} Myr</a> · <a href="?world=${w.file}" data-world="${w.file}">world ${w.id}</a>${named}` +
      (zs.length ? `<div class="sub"><span class="muted">zoom${zs.length > 1 ? 's' : ''}:</span> ${zs.map(zoomLink).join(', ')}</div>` : '') + '</div>';
  }).join('') + tzs.map((r) => {
    const fins = finishedOf(r.id);
    return `<div><a href="#" data-jump="${r.at_myr}" title="Go to ${r.at_myr} Myr">${r.at_myr} Myr</a> ·
    <a href="?run=${r.dir}" data-run="${r.dir}">time zoom ${r.id}</a> <span class="muted">${r.kyr} kyr of ice ages</span>` +
      fins.map((w) => {
        const zs = S.IDX.zooms.filter((z) => z.world === w.id);
        return `<div class="sub"><a href="?run=${r.dir}&t=${w.timezoom_kyr}" data-run="${r.dir}" data-t="${w.timezoom_kyr}" title="Open the time zoom at +${w.timezoom_kyr} kyr">+${w.timezoom_kyr} kyr</a> ·
          <a href="?world=${w.file}" data-world="${w.file}">finished world ${w.id}</a> <span class="muted">sea ${Math.round(w.sea_level_change_m)} m</span>` +
          (zs.length ? ` <span class="muted">zoom${zs.length > 1 ? 's' : ''}:</span> ${zs.map(zoomLink).join(', ')}` : '') + '</div>';
      }).join('') + '</div>';
  }).join('') + '</div>';
  return html;
}
// ticks above the time slider at the times of the worlds and time zooms made from this run
export function drawMarks() {
  const el = $('marks');
  el.innerHTML = '';
  if (S.V?.kind !== 'run') return;
  const fr = S.V.run.frames, t0 = fr[0].t, t1 = fr[fr.length - 1].t;
  const tick = (t, names, cls) => `<span class="${cls}" style="left:${(100 * (t - t0) / (t1 - t0 || 1)).toFixed(2)}%" data-t="${t}"
    title="${t} ${S.V.tz ? 'kyr' : 'Myr'}: ${names.join(', ')} (click to go there)"></span>`;
  if (S.V.tz) {  // a time zoom: its finished worlds
    el.innerHTML = finishedOf(S.V.run.id || S.V.dir).map((w) => tick(w.timezoom_kyr, [`finished world ${w.id}`], 'fin')).join('');
    return;
  }
  const { worlds, tzs } = madeFrom(S.V.dir), at = new Map();
  for (const w of worlds) at.set(w.t_myr, [...(at.get(w.t_myr) || []), `world ${w.id}`]);
  const tzAt = new Map();
  for (const r of tzs) tzAt.set(r.at_myr, [...(tzAt.get(r.at_myr) || []), `time zoom ${r.id}`]);
  el.innerHTML = [...tzAt].map(([t, n]) => tick(t, n, 'tz')).join('') + [...at].map(([t, n]) => tick(t, n, '')).join('');
  // with a vegetation view: a tick and a label where each plant group appeared (vegetation.GROUPS)
  if (VEG_VIEWS.has(state.layer)) {
    const short = ['mosses', 'marsh plants', 'conifers', 'flowering plants', 'grasses', 'C4 + CAM'];
    let last = -1e9, row = 0;
    for (const g of S.V.run.meta.plant_groups || []) {
      if (g.t == null || g.t < t0 || g.t > t1) continue;
      const xf = 100 * (g.t - t0) / (t1 - t0 || 1), x = xf.toFixed(2), title = `${g.t} Myr: ${esc(g.name)} appear (${g.pfts.join(', ')})`;
      row = xf - last < 12 ? (row + 1) % 3 : 0;  // close labels step up through three rows
      last = xf;
      el.innerHTML += `<span class="veg" style="left:${x}%" data-t="${g.t}" title="${title}"></span>` +
        `<b style="left:${x}%;top:${-13 - 10 * row}px" data-t="${g.t}" title="${title}">${short[g.group - 1] || g.group}</b>`;
    }
  }
}
$('marks').addEventListener('click', (e) => {
  if (e.target.dataset.t == null || S.V?.kind !== 'run') return;
  stop(); setFrame(nearestFrame(+e.target.dataset.t));
});
export async function openWorld(file) {
  $('worldSel').value = 'world:' + file; syncFav();
  await loadSelection('world:' + file);
}
// after something new was made: re-read the indexes, redraw what lists them
export async function refreshIndex() {
  await fillSelector();
  S.navUi?.refresh();
  if (!S.V) return;
  renderSummary(); drawMarks(); buildZoomOutlines(); projOverlaysChanged();
}

// ------------------------------------------------------------ cold eras on the timeline
// 0 (warm) .. 1 (deep icehouse) for a main run's keyframe, from its land ice
// and global mean temperature. Earth today (land ice on ~3% of the surface,
// 14.5 C) counts as fully cold: an icehouse with ice-age cycles.
export function coldness(s) {
  if (s.ice_pct == null) return 0;
  return Math.min(1, Math.max(0, (s.ice_pct - 1) / 2, (13 - s.global_temp_c) / 4));
}
export const COLD_HELP = 'Blue under the slider: cold eras (land ice on more than 1% of the surface, or a global mean below 13 °C; ' +
  'darkest = Earth-like icehouse or colder; smoothed over 5 keyframes). That is where a glacial time zoom shows ice ages.';

// The tint strip under the time slider: cold eras for a main run; for a time zoom, the ice volume.
export function drawTint() {
  const cv = $('tint'), fr = S.V.run.frames, w = cv.clientWidth || 600;
  cv.width = w; cv.height = 1;
  const g = cv.getContext('2d');
  g.clearRect(0, 0, w, 1);
  // a running mean over 5 keyframes: temperature wobbles frame to frame near
  // the thresholds, which drew the strip as stripes (PW-081)
  const raw = fr.map((f) => coldness(f.stats));
  let val = raw.map((_, i) => {
    const win = raw.slice(Math.max(0, i - 2), i + 3);
    return win.reduce((a, b) => a + b, 0) / win.length;
  });
  if (S.V.tz) {
    const sl = fr.map((f) => f.stats.sea_level_change_m), hi = Math.max(...sl), lo = Math.min(...sl);
    val = sl.map((v) => (hi - lo > 1 ? (hi - v) / (hi - lo) : 0));
  }
  const dx = w / Math.max(fr.length - 1, 1);
  val.forEach((c, i) => {
    if (c < 0.01) return;
    // ramps in from 0 so a value wobbling near the bottom doesn't switch on and off
    const a = c < 0.1 ? 2.2 * c : 0.15 + 0.7 * c;
    g.fillStyle = `rgba(120, 190, 255, ${a.toFixed(2)})`;
    // abutting, not overlapping: overlapped translucent rects doubled the alpha in thin stripes
    const x0 = Math.max(0, Math.round((i - 0.5) * dx)), x1 = Math.round((i + 0.5) * dx);
    g.fillRect(x0, 0, Math.max(x1 - x0, 1), 1);
  });
  $('track').title = S.V.tz ? 'Blue under the slider: how much ice there is (darkest = the largest ice volume of this time zoom)' : COLD_HELP;
}
