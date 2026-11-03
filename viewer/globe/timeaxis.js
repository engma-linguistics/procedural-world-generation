// The time slider's axis (PW-1042): where each stored moment sits along the slider, and the dated ticks under it.
// A peoples run (kind 'peoples') stores moments unevenly (Myr apart in deep time, centuries at the end), so
// its slider is a log axis of time before the present, with "now" at the right end and the eras it was made from
// as bands, like the workbench timeline (lineages.html drawTimeline). Every other run is linear in its own time
// (a main run in Myr, a time zoom in kyr). The slider input runs 0..RES; a position picks the nearest moment.
import { kyr as fmtKyr } from '../planets.js';
import { S } from './state.js';
import { $ } from './scene.js';

export const RES = 1000;
// a round step giving about n ticks over span
function niceStep(span, n = 6) {
  const raw = span / n, p = 10 ** Math.floor(Math.log10(raw));
  return [1, 2, 2.5, 5, 10].map((m) => m * p).find((s) => s >= raw) || 10 * p;
}

// the axis of a run: { at(t): 0..1, pos: [slider position per frame], ticks: [{x, text}], bands: [{x0, x1, text, cls}], log }
export function timeAxis(run) {
  const fr = run.frames, t0 = fr[0].t, t1 = fr[fr.length - 1].t, m = run.meta || {};
  let at, ticks = [], bands = [];
  const log = run.kind === 'peoples' && t1 <= 0 && t0 < 0;
  if (log) {
    const agos = fr.map((f) => -f.t).filter((a) => a > 0);
    const amax = Math.max(...agos), amin = Math.min(...agos) / 2, L0 = Math.log10(amin), L1 = Math.log10(amax);
    at = (t) => (L1 - Math.log10(Math.min(amax, Math.max(-t, amin)))) / (L1 - L0);
    for (const k of [100000, 10000, 1000, 100, 10, 1, 0.1]) if (k < amax / 1.3 && k > amin * 2) ticks.push({ x: at(-k), text: fmtKyr(k) });
    ticks = ticks.filter((k) => k.x > 0.09 && k.x < 0.94);  // (room for the two ends' labels)
    ticks.unshift({ x: 0, text: fmtKyr(amax), end: 'start' });
    ticks.push({ x: 1, text: 'now', end: 'end' });
    // the eras the run was made from: the tectonic run, the glacial time zoom, the recent pass (when the meta says)
    const tz = m.now_kyr, rp = m.recent?.kyr;
    if (tz && rp && tz > rp && tz < amax) {
      bands = [{ x0: 0, x1: at(-tz), text: 'deep time (Myr)', cls: 'deep' },
        { x0: at(-tz), x1: at(-rp), text: 'ice ages (kyr)', cls: 'ice' },
        { x0: at(-rp), x1: 1, text: 'recent (centuries)', cls: 'recent' }];
    }
  } else {
    const span = t1 - t0 || 1;
    at = (t) => Math.min(1, Math.max(0, (t - t0) / span));
    const unit = run.kind === 'timezoom' || run.kind === 'peoples' ? 'kyr' : 'Myr', step = niceStep(span);
    const ago = !!m.phase || run.kind === 'peoples';
    const label = (v) => (ago && v === 0 ? 'now' : ago ? `${fmtKyr(-v)} ago` : `${+v.toFixed(3)} ${unit}`);
    for (let v = Math.ceil(t0 / step) * step; v <= t1 + 1e-9; v += step) {
      const x = at(v);
      ticks.push({ x, text: label(v), end: x < 0.02 ? 'start' : x > 0.98 ? 'end' : '' });
    }
  }
  return { at, log, ticks, bands, pos: fr.map((f) => Math.round(RES * at(f.t))) };
}

// the moment nearest a slider position
export function frameAtPos(p) {
  const pos = S.V.axis.pos;
  let best = 0;
  for (let i = 1; i < pos.length; i++) if (Math.abs(pos[i] - p) < Math.abs(pos[best] - p)) best = i;
  return best;
}

// the ticks and era bands under the slider (#taxis), the slider's range
export function drawAxis() {
  const ax = S.V.axis, el = $('taxis');
  $('frame').max = RES;
  el.innerHTML = ax.bands.map((b) => `<i class="band ${b.cls}" style="left:${(100 * b.x0).toFixed(2)}%;width:${(100 * (b.x1 - b.x0)).toFixed(2)}%" title="${b.text}">${b.text}</i>`).join('') +
    ax.ticks.map((k) => `<span class="${k.end || ''}" style="left:${(100 * k.x).toFixed(2)}%">${k.text}</span>`).join('');
  el.classList.toggle('banded', ax.bands.length > 0);
}
