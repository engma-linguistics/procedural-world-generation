import { postJob, trackJob } from '../planets.js';
import { S } from './state.js';
import { $ } from './scene.js';
import { buildOverlays } from './overlays.js';
import { timeLabel } from './timezoom.js';
import { refreshIndex } from './provenance.js';
import { infoBoxHtml, renderDetail } from './describe.js';
import { updateHover } from './pick.js';
import { showTab } from './tabs.js';
// ------------------------------------------------------------ regional zoom
// Clicking a cell offers a zoom of the region around it. The server (planet
// serve) does the work as a background job: for a run it first builds a full
// world from the keyframe on screen (a few seconds, reused afterwards), then
// refines the region. We poll the job and open the result.
let zoomJob = null;
const ZOOM_SIZES = [250, 500, 1000, 2000, 4000];
const ZOOM_PX = 500;  // pixels across, whatever the size: 1000 km -> 2 km pixels

export function zoomSource() {
  if (S.V.tz) return null;  // zoom from the time zoom's source run instead
  if (S.V.kind === 'run') return { run: S.V.dir, t: S.V.t };
  if (S.V.id && S.V.layers.rock) return { world: S.V.id };
  return null;  // a generated (not sliced) world has no rock/climate layers to refine
}

export function pickCell(i) {
  S.picked = { i, lat: +S.V.grid.lat[i].toFixed(2), lon: +S.V.grid.lon[i].toFixed(2) };
  renderZoomBox();
  buildOverlays();
}

export function unpick() {
  S.picked = null;
  if (zoomJob?.finished) zoomJob = null;
  renderZoomBox();
  buildOverlays();
  updateHover();
}

export function renderZoomBox() {
  const box = $('zoomBox');
  let html = '';
  if (S.picked && S.V) {
    const src = zoomSource();
    S.infoHtml = null; $('infoText').innerHTML = infoBoxHtml(S.picked.i);
    if (S.detailCell >= 0) renderDetail();
    html += `<button class="x" data-act="close" title="Close (Esc)">&times;</button>
      <b>Zoom into this region</b> <span class="muted">(white square)</span><br>
      <span class="muted">centre ${S.picked.lat}, ${S.picked.lon}${S.V.kind === 'run' ? ` · t = ${timeLabel(S.V.t)}` : ''}</span><br>`;
    if (src) {
      html += `<div class="row" style="margin-top:4px;align-items:center">
        <select id="zoomSize">${ZOOM_SIZES.map((k) => `<option value="${k}" ${k === S.zoomSize ? 'selected' : ''}>${k} km</option>`).join('')}</select>
        <button class="btn" data-act="go" ${zoomJob && !zoomJob.finished ? 'disabled' : ''}>Zoom</button></div>
        <div class="muted">${ZOOM_PX}×${ZOOM_PX} px at ${+(S.zoomSize / ZOOM_PX).toFixed(2)} km${S.V.kind === 'run' ? '; a full world is built from this frame first (a few seconds, once)' : ''}</div>`;
    } else html += `<div class="muted">${S.V.tz ? 'No regional zooms of a time zoom; zoom into its source run instead.'
      : 'Zooming needs a world sliced from a run (or a run). This one has no rock or climate layers.'}</div>`;
  }
  if (zoomJob) {
    const j = zoomJob;
    html += `<div style="margin-top:6px"><b>${j.label}</b><br>`;
    if (j.status === 'error') html += `<span class="err">${j.error}</span>`;
    else if (j.status === 'done') html += `done: zoom <a href="#" data-act="open">${j.zoom}</a> (opened in the Regional zoom tab)`;
    else html += `<div class="bar"><div style="width:${Math.round(100 * (j.progress || 0))}%"></div></div>
      <span class="muted">${j.message || j.status}</span> ${j.job ? '<button class="btn" data-act="cancel" title="Stop this zoom">Cancel</button>' : ''}`;
    if (j.status === 'error' && j.cancelled) html = html.replace(/<span class="err">.*?<\/span>/, '<span class="muted">cancelled</span>');
    html += '</div>';
  }
  box.innerHTML = html;
  box.hidden = !html;
}

$('zoomBox').addEventListener('change', (e) => { if (e.target.id === 'zoomSize') { S.zoomSize = +e.target.value; renderZoomBox(); buildOverlays(); } });
$('zoomBox').addEventListener('click', (e) => {
  const act = e.target.dataset.act;
  if (act === 'close') unpick();
  if (act === 'go') startZoom();
  if (act === 'open') { e.preventDefault(); showTab('zoom', zoomJob.zoom); }
  if (act === 'cancel' && zoomJob?.job) { e.target.disabled = true; fetch(`../api/jobs/${zoomJob.job}`, { method: 'DELETE' }).catch(() => {}); }
});

export async function startZoom() {
  const src = zoomSource(); if (!src || !S.picked) return;
  const req = { ...src, lat: S.picked.lat, lon: S.picked.lon, size_km: S.zoomSize, res_km: S.zoomSize / ZOOM_PX };
  if (zoomJob && !zoomJob.finished) return;
  zoomJob = { label: `${S.zoomSize} km around ${S.picked.lat}, ${S.picked.lon}`, status: 'starting', progress: 0 };
  renderZoomBox();
  const job = zoomJob, out = await postJob('zoom', req, 'zoom');
  if (out.error) { Object.assign(job, { status: 'error', finished: true, error: out.error }); return renderZoomBox(); }
  job.job = out.job;
  const j = await trackJob(out.job, (j) => {
    Object.assign(job, j);
    if (j.status === 'done' || j.status === 'error') job.finished = true;
    renderZoomBox();
  }, 1000, () => job === zoomJob);
  if (j?.status === 'done') { showTab('zoom', j.zoom); refreshIndex(); }
}
