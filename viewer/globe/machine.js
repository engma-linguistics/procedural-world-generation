// The Machine panel and low-detail mode (PW-1720, PW-1721): a "Machine" section at the foot of the left panel.
//   - Detail: auto / low / full (kept in this browser). Auto goes low on software rendering, integrated Intel graphics,
//     a small largest-texture, <= 4 GB deviceMemory, or when the machine probe said so (machinecore.js). Low detail
//     keeps fewer LOD tiles in flight and in GPU memory, refines them less finely, stops at 250 m and draws at 1x pixels.
//   - The GPU as WebGL reports it (renderer string, largest texture) and the browser's deviceMemory.
//   - The machine presets from GET /api/machine (planet/machine.py): the probe, the budget, jobs, tiles, and each
//     heavy feature allowed / warned / off with the peak that decided it; in an install a gate can be overridden
//     (POST /api/machine, saved in the config's [overrides]).
import { esc } from '../planets.js';
import { DIAG, renderer, resize } from './scene.js';
import { LOD } from './lodtiles.js';
import { MODES, chooseDetail, lodSettings } from '../machinecore.js';

const KEY = 'planetViewer.detail';
const store = { get() { try { return localStorage.getItem(KEY) || 'auto'; } catch { return 'auto'; } },
                set(v) { try { localStorage.setItem(KEY, v); } catch { /* not kept */ } } };

function gpuInfo() {
  const gl = renderer.getContext();
  let name = '';
  try {
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    name = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
  } catch { /* hidden by the browser */ }
  return { renderer: String(name || ''), maxTexture: gl.getParameter(gl.MAX_TEXTURE_SIZE),
           webgl2: typeof WebGL2RenderingContext !== 'undefined' && gl instanceof WebGL2RenderingContext,
           deviceMemory: navigator.deviceMemory || null };
}

export const MACHINE = { gpu: null, report: null, detail: null, mode: store.get() };

export function applyDetail() {
  const d = chooseDetail(MACHINE.mode, MACHINE.gpu, MACHINE.report?.presets?.low_detail);
  const s = lodSettings(d.budget, location.search, devicePixelRatio);
  Object.assign(LOD, { maxTiles: s.maxTiles, maxBytes: s.maxBytes, fetches: s.fetches });
  if (s.refinePx != null) LOD.refinePx = s.refinePx;
  if (s.maxLevel != null) LOD.maxLevel = s.maxLevel;
  if (s.dpr != null && !DIAG.dpr && renderer.getPixelRatio() !== s.dpr) { renderer.setPixelRatio(s.dpr); resize(); }
  LOD.dirty = true;
  MACHINE.detail = d;
  window.planetViewer && (window.planetViewer.machine = MACHINE);
  return d;
}

const CHIP = { allow: ['#2e7d4f', 'allowed'], warn: ['#a87a12', 'warned'], off: ['#8c2f2f', 'off'] };
const chip = (s) => `<span style="display:inline-block;min-width:46px;text-align:center;border-radius:8px;padding:0 5px;font-size:10px;color:#fff;background:${CHIP[s]?.[0] || '#555'}">${CHIP[s]?.[1] || s}</span>`;
const gb = (x) => (x == null ? '?' : `${(+x).toLocaleString(undefined, { maximumFractionDigits: 1 })} GB`);

let sec = null;
function render() {
  if (!sec) return;
  const r = MACHINE.report, d = MACHINE.detail, g = MACHINE.gpu || {};
  const p = r?.presets || {};
  const rows = (r?.gates || []).map((x) => `<tr title="${esc(x.source)}"><td>${chip(x.state)}</td><td>${esc(x.label)}</td><td class="muted" style="text-align:right">${gb(x.peak_gb)}</td>`
    + (r.applied && r.can_save ? `<td><select data-gate="${esc(x.gate)}" title="Override (saved in the install's config)" style="font-size:10px;width:62px">${['auto', 'allow', 'warn', 'off'].map((o) => `<option value="${o}"${(x.override || 'auto') === o ? ' selected' : ''}>${o === 'auto' ? 'preset' : o}</option>`).join('')}</select></td>` : '') + '</tr>').join('');
  sec.querySelector('.mbody').innerHTML = `
    <div class="row" style="gap:6px;align-items:center"><span>Detail</span>
      <select id="detailMode" style="width:auto">${MODES.map((m) => `<option value="${m}"${MACHINE.mode === m ? ' selected' : ''}>${m}</option>`).join('')}</select>
      <span class="muted" style="font-size:11px">${d ? `${d.level} (${esc(d.why)})` : ''}</span></div>
    <div class="muted" style="font-size:11px;margin:2px 0 6px">Low detail: fewer detail tiles in flight and in GPU memory, coarser
      tiles near the ground, at most 250 m, 1x pixels. For laptop graphics; kept in this browser.</div>
    <div style="font-size:11px">GPU <span class="muted">${esc(g.renderer || 'hidden by the browser')}; largest texture ${g.maxTexture || '?'} px${g.deviceMemory ? `; device memory ${g.deviceMemory} GB` : ''}${g.webgl2 ? '' : '; <b>no WebGL2</b>'}</span></div>
    ${r ? `<div style="font-size:11px;margin-top:4px">Machine <span class="muted">${p.probed_cores} cores, ${gb(p.probed_ram_gb)} RAM, ${gb(p.probed_disk_free_gb)} free disk, GPU ${esc(p.probed_gpu || '?')}</span></div>
    <div style="font-size:11px">Budget <span class="muted">${gb(p.budget_gb)} for the app, ${gb(p.spare_gb)} kept spare; ${p.jobs} job(s) at once; level ${p.default_level} and ${(p.default_kyr || 0) / 1000} Myr by default;
      detail tiles ${p.tile_levels?.length ? `${p.tile_at_once} at once, levels ${p.tile_levels.join(', ')}` : 'off'}, cache ${gb(p.tile_cache_gb)}</span></div>
    <div class="muted" style="font-size:11px;margin:4px 0">${r.applied ? `Applied (from ${esc(r.config || 'the config')}). Off: refused with the reason; warned: runs, with a warning.`
      : 'Not applied: this server is not an install (a checkout), so nothing is gated. This is what the probe would set.'}</div>
    <table style="font-size:11px;border-collapse:collapse;width:100%">${rows}</table>
    <div class="muted" style="font-size:10px;margin-top:3px">Hover a row for where its number was measured. Tile changes apply at the next server start.</div>`
    : '<div class="muted" style="font-size:11px">No machine report (the server has no /api/machine).</div>'}`;
  sec.querySelector('#detailMode').onchange = (e) => { MACHINE.mode = e.target.value; store.set(MACHINE.mode); applyDetail(); render(); };
  sec.querySelectorAll('select[data-gate]').forEach((s) => (s.onchange = async () => {
    try {
      const res = await fetch('/api/machine', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gate: s.dataset.gate, state: s.value }) });
      const j = await res.json();
      if (res.ok) MACHINE.report = j;
    } catch { /* kept as it was */ }
    applyDetail(); render();
  }));
}

function mount() {
  const host = document.getElementById('controls');
  if (!host) return;
  sec = document.createElement('details');
  sec.className = 'sec'; sec.dataset.sec = 'machine'; sec.id = 'machineSec';
  sec.innerHTML = '<summary>Machine</summary><div class="mbody"></div>';
  host.appendChild(sec);
}

async function start() {
  MACHINE.gpu = gpuInfo();
  applyDetail();  // (at once, from the GPU alone; again with the presets once they arrive)
  mount();
  render();
  try {
    const res = await fetch('/api/machine', { cache: 'no-store' });
    if (res.ok) MACHINE.report = await res.json();
  } catch { /* a static copy of the viewer: no server */ }
  applyDetail();
  render();
}
start();
