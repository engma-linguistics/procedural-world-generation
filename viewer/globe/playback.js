import { S, state } from './state.js';
import { $ } from './scene.js';
import { paint } from './geometry.js';
import { buildOverlays } from './overlays.js';
import { northUp } from './axis.js';
import { renderRunSummary } from './panel.js';
import { CHART, startFinish, startTimezoom } from './timezoom.js';
import { openWorld } from './provenance.js';
import { closeDetail } from './describe.js';
import { unpick } from './zoom.js';
import { showTab } from './tabs.js';
import { frameToUrl, setFrame } from './load.js';
import { openRun } from './select.js';
// ------------------------------------------------------------ playback
export function stop() {
  const was = state.playing;
  state.playing = false; $('play').innerHTML = '&#9654;';
  if (was && S.V?.kind === 'run') frameToUrl();
  if (was && S.V && S.mesh && S.topo.smoothRelief) paint();  // (the relief's smooth normals again)
  else if (was && S.V && S.mesh && $('currents').checked) buildOverlays();  // back to streamlines
}
function togglePlay() {
  if (!S.V || S.V.kind !== 'run') return;
  if (!state.playing && S.V.frame >= S.V.run.frames.length - 1) setFrame(0);
  if (state.playing) return stop();
  state.playing = true;
  $('play').innerHTML = '&#10073;&#10073;';
}
$('play').addEventListener('click', togglePlay);
// (scrubbing: at most one repaint per display frame, the last position wins; a repaint is ~20 ms at L7, and slider
// events arrive faster than that when the machine is busy, so each used to queue behind the one before, PW-679)
let scrubTo = null;
$('frame').addEventListener('input', (e) => {
  stop();
  const wasIdle = scrubTo === null;
  scrubTo = +e.target.value;
  if (wasIdle) requestAnimationFrame(() => { const f = scrubTo; scrubTo = null; if (S.V?.kind === 'run' && f < S.V.run.frames.length) setFrame(f); });
});
addEventListener('keydown', (e) => {
  if (!S.V || state.tab === 'zoom' || e.target.tagName === 'SELECT') return;
  if (e.code === 'KeyN' && !e.metaKey && !e.ctrlKey) northUp();
  if (e.code === 'Escape' && S.detailCell >= 0) return closeDetail();  // (the panel first, then the pick)
  if (e.code === 'Escape' && S.picked) unpick();
  if (S.V.kind !== 'run') return;
  if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
  if (e.code === 'ArrowRight') { stop(); setFrame(Math.min(S.V.frame + 1, S.V.run.frames.length - 1)); }
  if (e.code === 'ArrowLeft') { stop(); setFrame(Math.max(S.V.frame - 1, 0)); }
});
export function nearestFrame(t) { const fr = S.V.run.frames; return fr.reduce((b, x, i) => (Math.abs(x.t - t) < Math.abs(fr[b].t - t) ? i : b), 0); }
$('summary').addEventListener('click', (e) => {
  const a = e.target.closest('[data-run],[data-world],[data-zoom],[data-jump]');  // provenance links
  if (a) {
    e.preventDefault();
    if (a.dataset.run) return openRun(a.dataset.run, a.dataset.t != null ? +a.dataset.t : undefined);
    if (a.dataset.world) return openWorld(a.dataset.world);
    if (a.dataset.zoom) return showTab('zoom', a.dataset.zoom);
    if (S.V.kind === 'run') { stop(); return setFrame(nearestFrame(+a.dataset.jump)); }
    return;
  }
  if (S.V.kind !== 'run') return;
  const act = e.target.dataset?.act;
  if (act === 'tz') return startTimezoom();
  if (act === 'finish') return startFinish();
  if (act === 'openTz') { e.preventDefault(); return openRun(S.tzJob.run); }
  if (act === 'source') { e.preventDefault(); return openRun(S.V.run.meta.source_run, S.V.run.meta.at_myr); }
  const chart = e.target.closest('svg.tzchart');
  if (chart) {  // jump to the time clicked on the chart
    const fr = S.V.run.frames, { w, left, right } = CHART, px = e.clientX - chart.getBoundingClientRect().left;
    const t0 = fr[0].t, t1 = fr[fr.length - 1].t;
    stop(); setFrame(nearestFrame(t0 + (px - left) / (w - left - right) * (t1 - t0)));
    return;
  }
  const ev = e.target.closest('.ev'); if (!ev) return;
  stop();
  setFrame(nearestFrame(+ev.dataset.t));
});
$('summary').addEventListener('change', (e) => { if (e.target.id === 'tzKyr') { S.tzKyr = +e.target.value; renderRunSummary(); } });
