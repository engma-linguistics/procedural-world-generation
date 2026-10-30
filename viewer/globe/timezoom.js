import { S, state } from './state.js';
import { peoplesPanel } from './colours.js';
import { EVENT_COLORS, hexColor } from './overlays.js';
import { renderRunSummary } from './panel.js';
import { COLD_HELP, coldness, esc, openWorld, sourceLink } from './provenance.js';
import { fetchJob } from './zoom.js';
import { viewKey } from './highlights.js';
import { fillSelector, openRun } from './select.js';
// ------------------------------------------------------------ glacial time zooms
// A time zoom (planet/timezoom.py) is stored as a run with time in kyr since
// its start: a few hundred kyr of ice ages from one moment of a main run (or
// today's Earth), with the geology frozen. Its summary has the sea-level curve.
export function timeLabel(t) {
  if (!S.V.tz) return `${t} Myr`;
  if (S.V.run.meta.phase) return agoLabel(t);  // recent pass and lineages (planet/lineages/): kyr before the present
  return S.V.tzEarth ? `+${t} kyr from today` : `+${t} kyr`;
}

// Recent passes and lineage histories (planet/lineages/, docs/proposals/lineages.md) are time-zoom
// runs with meta.phase and time in kyr before the present (t <= 0).
export function agoLabel(t) {
  const a = -t;
  if (a <= 0) return 'present';
  if (a >= 1000) return `${+(a / 1000).toFixed(a >= 10000 ? 0 : 1)} Myr ago`;
  return a >= 10 ? `${+a.toFixed(1)} kyr ago` : `${Math.round(a * 1000)} years ago`;
}
function phaseSummary() {
  const r = S.V.run, m = r.meta, s = r.frames[S.V.frame].stats;
  const sign = (x, d = 0) => (x > 0 ? '+' : x < 0 ? '−' : '') + Math.abs(x).toFixed(d);
  const what = m.phase === 'recent' ? `recent pass (${m.kyr} kyr at ${m.step_kyr * 1000}-year steps)` : 'peoples and their history';
  const tzl = m.timezoom ? `<a href="?run=${m.timezoom}&t=${m.now_kyr}" data-run="${m.timezoom}" data-t="${m.now_kyr}">time zoom ${m.timezoom} @ +${m.now_kyr} kyr</a>` : '';
  const remake = m.phase === 'recent' ? `uv run python -m planet recent ${m.timezoom} --now ${m.now_kyr} --kyr ${m.kyr}`
    : `uv run python -m planet lineages ${m.world || m.timezoom} --tree ${m.tree_file || '<tree.toml>'}`;
  const stat = s.sea_level_change_m != null ? `sea level ${sign(s.sea_level_change_m)} m vs the time zoom's start · land ice on ${s.ice_pct}% of the surface` : '';
  return `<b>${r.id || ''}</b> ${r.name} <span class="muted">· ${what} · ${m.cells} cells · made ${m.created}</span><br>
    <b>${agoLabel(S.V.t)}</b>${s.variability_c != null ? ` · centennial anomaly ${sign(s.variability_c, 2)} °C` : ''}<br>${stat}<br>
    ${m.phase === 'lineages' && typeof peoplesPanel === 'function' ? peoplesPanel() : ''}
    <span class="muted">Present = </span>${tzl}${m.world ? ` (finished world <a href="?world=${m.world}.json" data-world="${m.world}.json">${m.world}</a>)` : ''}<br>
    <span class="muted">Remake:</span> <code>${remake}</code>`;
}

export function timezoomSummary() {
  if (S.V.run.meta.phase) return phaseSummary();
  const r = S.V.run, m = r.meta, s = r.frames[S.V.frame].stats;
  const when = S.V.tzEarth ? `<b>+${S.V.t} kyr</b> from today's Earth`
    : `<b>+${S.V.t} kyr</b> after ${m.source_name} @ ${m.at_myr} Myr`;
  const sign = (x, d = 0) => (x > 0 ? '+' : x < 0 ? '−' : '') + Math.abs(x).toFixed(d);
  const src = S.V.tzEarth ? 'earth' : m.source_run;
  const opts = (m.at_myr ? ` --at ${m.at_myr}` : '') + ` --kyr ${m.kyr}` + (m.step_kyr !== 0.5 ? ` --step ${m.step_kyr}` : '');
  return `<b>${r.id || ''}</b> ${r.name} <span class="muted">· glacial time zoom · ${m.cells} cells · made ${m.created}</span><br>
    ${when}<br>
    sea level ${sign(s.sea_level_change_m)} m vs the start · ice ${s.ice_volume_mkm3} M km³ (land ice on ${s.ice_pct}% of the surface,
    thickest ${s.max_ice_m} m) · global mean ${s.global_temp_c} °C<br>
    <span class="muted">orbit:</span> obliquity ${s.obliquity.toFixed(2)}° · eccentricity ${s.eccentricity.toFixed(4)} ·
    ${iceSun() ? `summer sun at ${iceSun().name} ${sign(s.insol_ice_summer_anom, 1)} W/m² · ` : ''}65°N July sun ${sign(s.insol_65n_jul_anom, 1)} W/m² <span class="muted" title="vs. ${S.V.tzEarth ? "today's orbit" : 'a circular orbit at the mean tilt'}; precession index e·sin(perihelion) ${s.precession_index}">(?)</span>
    ${timezoomChart()}
    ${S.V.tzEarth ? '' : `<span class="muted">From</span> ${sourceLink(m.source_run, m.at_myr)}<br>`}
    <span class="muted">Remake:</span> <code>uv run python -m planet timezoom ${src}${opts}</code>
    ${finishBox()}`;
}

// Where the ice comes and goes (timezoom.cycling_ice_sun, PW-428): its latitude
// and name ("47°S"); null when that is 65 N (or the time zoom predates it)
function iceSun() {
  const c = S.V.run.meta.ice_cycle;
  if (!c || S.V.run.frames[0].stats.insol_ice_summer_anom == null || Math.abs(c.lat - 65) < 3) return null;
  return { ...c, name: `${Math.abs(c.lat).toFixed(0)}°${c.lat < 0 ? 'S' : 'N'}` };
}

// The whole time zoom at a glance: sea level (falls as the ice grows; ice
// volume on the right axis) and, below, the summer sun that drives it: at the
// latitude where the ice comes and goes (dashed: 65 N July, the classic
// index). The white line is the frame on screen; click to jump.
export const CHART = { w: 296, top: 72, sun: 24, left: 30, right: 30 };
function timezoomChart() {
  const fr = S.V.run.frames, { w, top, sun, left, right } = CHART;
  const ts = fr.map((f) => f.t), t0 = ts[0], t1 = ts[ts.length - 1];
  const x = (t) => left + (t - t0) / (t1 - t0 || 1) * (w - left - right);
  const sl = fr.map((f) => f.stats.sea_level_change_m), vol = fr.map((f) => f.stats.ice_volume_mkm3);
  const hi = Math.max(...sl, 5), lo = Math.min(...sl, -5);
  const y = (v) => 4 + (hi - v) / (hi - lo) * (top - 8);
  const cyc = iceSun(), i65 = fr.map((f) => f.stats.insol_65n_jul_anom);
  const ins = cyc ? fr.map((f) => f.stats.insol_ice_summer_anom) : i65;
  const im = Math.max(...ins.map(Math.abs), ...(cyc ? i65.map(Math.abs) : []), 1);
  const ys = (v) => top + 4 + (1 - v / im) / 2 * (sun - 6);
  const line = (vals, yf) => vals.map((v, i) => `${i ? 'L' : 'M'}${x(ts[i]).toFixed(1)},${yf(v).toFixed(1)}`).join('');
  const iHi = sl.indexOf(Math.max(...sl)), iLo = sl.indexOf(Math.min(...sl));  // ice volume at the two extremes
  const ev = S.V.run.events.map((e) => `<circle cx="${x(e.t).toFixed(1)}" cy="${y(sl[Math.max(0, ts.indexOf(e.t))]).toFixed(1)}" r="2"
    fill="${hexColor(EVENT_COLORS[e.kind] || 0xffffff)}"/>`).join('');
  const xn = x(S.V.t).toFixed(1), h = top + sun + 12;
  return `<svg class="tzchart" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <line x1="${left}" x2="${w - right}" y1="${y(0)}" y2="${y(0)}" stroke="#2a3446"/>
    <path d="${line(sl, y)}L${x(t1)},${y(0)}L${x(t0)},${y(0)}Z" fill="#5d8fcb" fill-opacity=".25"/>
    <path d="${line(sl, y)}" fill="none" stroke="#7cc4ff" stroke-width="1.4"/>${ev}
    <text x="${left - 3}" y="${y(hi) + 4}" text-anchor="end">${Math.round(hi)}</text>
    <text x="${left - 3}" y="${y(lo)}" text-anchor="end">${Math.round(lo)}</text>
    <text x="${left - 3}" y="${y(0) + 3}" text-anchor="end">0 m</text>
    <text x="${w - right + 3}" y="${y(sl[iHi]) + 4}">${vol[iHi].toFixed(0)}</text>
    <text x="${w - right + 3}" y="${y(sl[iLo])}">${vol[iLo].toFixed(0)}</text>
    <line x1="${left}" x2="${w - right}" y1="${ys(0)}" y2="${ys(0)}" stroke="#2a3446"/>
    ${cyc ? `<path d="${line(i65, ys)}" fill="none" stroke="#ffc864" stroke-opacity=".45" stroke-width="1" stroke-dasharray="2 2"/>` : ''}
    <path d="${line(ins, ys)}" fill="none" stroke="#ffc864" stroke-width="1"/>
    <text x="${left - 3}" y="${ys(0) + 3}" text-anchor="end">sun</text>
    <line x1="${xn}" x2="${xn}" y1="0" y2="${top + sun}" stroke="#ffffff" stroke-opacity=".85"/>
    <text x="${left}" y="${h - 1}">${t0}</text><text x="${w - right}" y="${h - 1}" text-anchor="end">${t1} kyr</text>
  </svg><div class="muted" style="font-size:11px">Blue: sea level vs the start (m, left) = ice volume (M km³, right).
    Yellow: ${cyc ? `summer sun at ${cyc.name}, where the ice comes and goes (${cyc.area_mkm2} M km²); dashed: 65°N July`
      : 'summer sun at 65°N'}, the orbital forcing. Click the chart to jump.</div>`;
}

// "Glacial time zoom from here" (main runs): the server runs it as a
// background job, ~4 min per 1000 kyr at level 6, then we open it.
const TZ_KYR = [100, 300, 1000];
export function timezoomBox() {
  const s = S.V.run.frames[S.V.frame].stats;
  let html = '<div class="tzBox">';
  if (s.sea_level_m == null) return html + '<span class="muted">Glacial time zooms need a run made with the climate model.</span></div>';
  const min = Math.max(1, Math.round(4 * S.tzKyr / 1000 * S.V.n / 40962));
  const busy = S.tzJob && !S.tzJob.finished;
  html += `<b>Glacial time zoom from here</b> <span class="muted" title="${COLD_HELP}">(ice ages at ${S.V.t} Myr;
    blue under the time slider = cold eras)</span><br>
    <div class="row" style="align-items:center;margin-top:3px">
      <select id="tzKyr">${TZ_KYR.map((k) => `<option value="${k}" ${k === S.tzKyr ? 'selected' : ''}>${k} kyr</option>`).join('')}</select>
      <button class="btn" data-act="tz" ${busy ? 'disabled' : ''}>Start</button>
      <span class="muted">~${min} min${coldness(s) < 0.05 ? '; a warm era: expect little ice' : ''}</span></div>`;
  if (S.tzJob) {
    const j = S.tzJob;
    html += `<div style="margin-top:4px">${j.label}: `;
    if (j.status === 'error') html += `<span class="err">${j.error}</span>`;
    else if (j.status === 'done') html += `done, <a href="#" data-act="openTz">open time zoom ${j.run}</a>`;
    else html += `<span class="muted">${j.message || j.status}</span><div class="bar"><div style="width:${Math.round(100 * (j.progress || 0))}%"></div></div>`;
    html += '</div>';
  }
  return html + '</div>';
}

export async function startTimezoom() {
  if (S.tzJob && !S.tzJob.finished) return;
  const req = { run: S.V.dir, t: S.V.t, kyr: S.tzKyr };
  const job = S.tzJob = { label: `${S.tzKyr} kyr from ${S.V.dir} @ ${S.V.t} Myr`, status: 'starting', progress: 0 };
  renderRunSummary();
  let r = null, out = {};
  try {
    r = await fetch('../api/timezoom', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) });
    out = await r.json().catch(() => ({}));
  } catch (err) { r = null; }
  if (!r || r.status === 501 || (r.status === 404 && !out.error)) {
    Object.assign(job, { status: 'error', finished: true, error: 'The server has no time zoom API. Restart it: uv run python -m planet serve' });
  } else if (!r.ok) Object.assign(job, { status: 'error', finished: true, error: out.error || `HTTP ${r.status}` });
  if (job.finished) { if (S.V.kind === 'run' && !S.V.tz) renderRunSummary(); return; }
  while (job === S.tzJob) {
    let j;
    j = await fetchJob(out.job);
    Object.assign(job, j);
    if (j.status === 'done' || j.status === 'error') job.finished = true;
    if (S.V.kind === 'run' && !S.V.tz && !state.playing) renderRunSummary();
    if (j.status === 'done') { await openRun(j.run); return; }
    if (job.finished) return;
    await new Promise((ok) => setTimeout(ok, 1500));
  }
}

// "Finish world here" (PW-091/193): a full world (climate, rivers, lakes,
// biomes, sea) at the moment on screen. In a time zoom: that frame's ice,
// pressed-down bed, sea level and climate on the source run's geology
// (planet/finish.py); in a main run: the keyframe's world (what the Zoom
// button builds). A job on the server, then the world opens.
let finJob = null;
export const finishedOf = (tzId) => S.IDX.worlds.filter((w) => w.timezoom === tzId).sort((a, b) => a.timezoom_kyr - b.timezoom_kyr);
// The run's finish moment (PW-866, highlights.finish_moment): the latest human-habitable keyframe near its end,
// where the default finished world is taken; flagged when no moment in the finish window passes.
export function finishMomentLine() {
  const fm = S.V.run.meta.finish_moment;
  if (!fm) return '';
  const tag = fm.passes ? '' : ' <span class="err">(no habitable moment: flagged)</span>';
  return `<span class="muted">Finish moment:</span> <a href="#" data-jump="${fm.t}" title="Go to ${fm.t} Myr">${fm.t} Myr</a>${tag}
    <span class="muted">· ${esc(fm.why)}</span><br>`;
}

export function finishBox() {
  const s = S.V.run.frames[S.V.frame].stats;
  if (!S.V.tz && s.sea_level_m == null) return '';
  const here = S.V.tz ? `+${S.V.t} kyr` : `${S.V.t} Myr`;
  const made = S.V.tz ? finishedOf(S.V.run.id || S.V.dir).find((w) => w.timezoom_kyr === S.V.t)
    : S.IDX.worlds.find((w) => w.source_run === S.V.dir && w.t_myr === S.V.t && !w.timezoom);
  const busy = finJob && !finJob.finished;
  const sec = Math.max(5, Math.round(20 * S.V.n / 40962));
  let html = `<div class="tzBox"><b>Finish world here</b> <span class="muted">(${here}: ${S.V.tz
    ? "this frame's ice, sea level and climate on the run's geology" : 'the full world at this keyframe'};
    then zooms and highlights)</span><br>
    <div class="row" style="align-items:center;margin-top:3px">` +
    (made ? `<a href="?world=${made.file}" data-world="${made.file}">open world ${made.id}</a> <span class="muted">(made already)</span>`
      : `<button class="btn" data-act="finish" ${busy ? 'disabled' : ''}>Finish world here</button>
         <span class="muted">~${sec < 60 ? sec + ' s' : Math.round(sec / 60) + ' min'}</span>`) + '</div>';
  if (finJob && finJob.view === viewKey()) {
    const j = finJob;
    html += `<div style="margin-top:4px">${j.label}: `;
    if (j.status === 'error') html += `<span class="err">${esc(j.error)}</span>`;
    else if (j.status === 'done') html += `done, <a href="?world=${j.world}.json" data-world="${j.world}.json">open world ${j.world}</a>`;
    else html += `<span class="muted">${esc(j.message || j.status)}</span><div class="bar"><div style="width:${Math.round(100 * (j.progress || 0))}%"></div></div>`;
    html += '</div>';
  }
  if (S.V.tz) {
    const fins = finishedOf(S.V.run.id || S.V.dir);
    if (fins.length) html += `<span class="muted">Finished worlds of this time zoom:</span> ${fins.map((w) =>
      `<a href="?world=${w.file}" data-world="${w.file}" title="sea level ${Math.round(w.sea_level_change_m)} m vs the start">+${w.timezoom_kyr} kyr</a>`).join(', ')}<br>`;
    html += `<span class="muted">CLI:</span> <code>uv run python -m planet finish ${S.V.run.id || S.V.dir} --kyr ${S.V.t}</code>`;
  } else html += `<span class="muted">CLI:</span> <code>uv run python -m planet finish ${S.V.run.id || S.V.dir} --at ${S.V.t}</code>
    <span class="muted">(or <code>slice</code>: replayed, exact)</span>`;
  return html + '</div>';
}

export async function startFinish() {
  if (finJob && !finJob.finished) return;
  const req = S.V.tz ? { timezoom: S.V.dir, kyr: S.V.t } : { run: S.V.dir, t: S.V.t };
  const job = finJob = { label: S.V.tz ? `world at +${S.V.t} kyr` : `world at ${S.V.t} Myr`, view: viewKey(), status: 'starting', progress: 0 };
  renderRunSummary();
  let r = null, out = {};
  try {
    r = await fetch('../api/finish', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) });
    out = await r.json().catch(() => ({}));
  } catch (err) { r = null; }
  if (!r || r.status === 501 || (r.status === 404 && !out.error)) {
    Object.assign(job, { status: 'error', finished: true, error: 'The server has no finish API. Restart it: uv run python -m planet serve' });
  } else if (!r.ok) Object.assign(job, { status: 'error', finished: true, error: out.error || `HTTP ${r.status}` });
  if (job.finished) { if (S.V.kind === 'run') renderRunSummary(); return; }
  while (job === finJob) {
    let j;
    j = await fetchJob(out.job);
    Object.assign(job, j);
    if (j.status === 'done' || j.status === 'error') job.finished = true;
    if (S.V.kind === 'run' && !state.playing) renderRunSummary();
    if (j.status === 'done') { await fillSelector(); await openWorld(j.world + '.json'); return; }
    if (job.finished) return;
    await new Promise((ok) => setTimeout(ok, 1000));
  }
}
