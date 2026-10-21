// The world navigator (PW-473): a bar on top of the viewer with the provenance chain of what is on
// screen (run -> time zoom -> finished world -> zoom -> fine zoom, each with its thumbnail), and a
// drop-down with the planet's whole family tree. "Make from here" buttons start the same jobs the
// viewer's own buttons do (POST /api/timezoom, /api/finish) and open the result when it is done.
// index.html gives it: getView() -> {kind: run|timezoom|world|zoom, id, t}, openNode(node, planet, t),
// findHighlights(), zoomSource() -> {run, t} | {world} | null (what a regional zoom is made from on screen), picked() -> {lat, lon} | null
// (the cell picked on the globe).
import { cancelJob, esc, fmtDuration, getPlanets, injectCss, kindName, nodeWhen, postJob, trackJob, treeHtml } from './planets.js';

const CSS = `
#navBar { top: 12px; left: 294px; right: 340px; padding: 4px 8px; display: flex; align-items: center; gap: 8px; z-index: 21; min-width: 0; }
#navBar .crumbs { display: flex; align-items: center; gap: 2px; min-width: 0; overflow-x: auto; flex: 1; scrollbar-width: none; }
#navBar .crumbs::-webkit-scrollbar { display: none; }
#navBar .crumb { display: flex; align-items: center; gap: 5px; flex: none; padding: 2px 6px 2px 2px; border-radius: 6px; cursor: pointer; border: 1px solid transparent; white-space: nowrap; font-size: 12px; }
#navBar .crumb:hover { background: #1d2738; }
#navBar .crumb.cur { border-color: var(--accent); background: #223652; }
#navBar .crumb img { width: 36px; height: 18px; object-fit: cover; border-radius: 3px; background: #111827; }
#navBar .sep { color: var(--muted); flex: none; }
#navBar [hidden] { display: none; }
#navTree .zf { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; margin-top: 3px; font-size: 11px; }
#navTree .zf input, #navTree .zf select { background: #111827; color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 1px 4px; font: inherit; width: 64px; }
#navTree .zf select { width: auto; }
#navBar .job { font-size: 11px; color: var(--muted); flex: none; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
#navTree { top: 56px; left: 294px; width: min(460px, calc(100vw - 306px)); max-height: calc(100vh - 140px); overflow-y: auto; z-index: 21; }
#navTree[hidden], #navBar[hidden] { display: none; }
#navTree h3 { margin: 0 0 6px; font-size: 13px; }
@media (max-width: 700px) {
  #navBar { left: 12px; right: 12px; top: 60px; }
  #navBar .crumb:not(.cur) span { display: none; }
  #navTree { left: 12px; right: 12px; top: 104px; width: auto; max-height: calc(100vh - 160px); }
  #controls { top: 104px !important; max-height: calc(100vh - 116px) !important; }
}
`;

export function createNavigator(host) {
  injectCss();
  const st = document.createElement('style'); st.textContent = CSS; document.head.append(st);
  const bar = document.createElement('div');
  bar.id = 'navBar'; bar.className = 'panel';
  bar.innerHTML = `<a class="btn" href="./" title="All planets, and make a new one">Planets</a><div class="crumbs"></div><span class="job"></span>
    <button class="btn" data-act="cancelJob" hidden title="Stop the job that is running">Cancel</button>
    <button class="btn" data-act="tree" title="The whole family of this planet: what was made from what">Family &#9662;</button>`;
  const tree = document.createElement('div');
  tree.id = 'navTree'; tree.className = 'panel'; tree.hidden = true;
  document.body.append(bar, tree);
  const crumbs = bar.querySelector('.crumbs'), jobEl = bar.querySelector('.job');
  let planets = [], fetched = 0, job = null, view = null;
  const cancelBtn = bar.querySelector('[data-act=cancelJob]');
  const forms = {};  // per node: what is typed in its zoom form (the tree redraws while a job runs)
  const SIZES = [250, 500, 1000, 2000, 4000];
  if (new URLSearchParams(location.search).get('navtree') === '1') tree.hidden = false;  // (?navtree=1: the family open, for screenshots)

  const keyOf = (v) => (!v ? null : v.kind === 'world' ? `world:${v.id}` : v.kind === 'zoom' ? `zoom:${v.id}` : `run:${v.id}`);
  function find(key) {
    for (const p of planets) { const n = p.nodes.find((x) => x.key === key); if (n) return [p, n]; }
    return [null, null];
  }
  const short = (n, v) => {
    if (n.kind === 'run') return `Run${v && keyOf(v) === n.key && v.t != null ? ` ${v.t} Myr` : ''}`;
    if (n.kind === 'timezoom') return `Time zoom${v && keyOf(v) === n.key && v.t != null ? ` +${v.t} kyr` : ` ${n.kyr} kyr`}`;
    if (n.kind === 'world') return n.timezoom_kyr != null ? `Finished world +${n.timezoom_kyr} kyr` : `World ${n.t_myr ?? ''} Myr`;
    return n.kind === 'fine' ? `Fine zoom ${n.size_km} km` : `Zoom ${n.size_km} km`;
  };

  function renderBar() {
    const [p, cur] = find(keyOf(view));
    if (!cur) {
      crumbs.innerHTML = `<span class="muted">${view ? esc(`${view.kind} ${view.id}`) : ''}</span>`;
      return;
    }
    const chain = [];
    for (let n = cur; n; n = p.nodes.find((x) => x.key === n.parent)) chain.unshift(n);
    crumbs.innerHTML = chain.map((n, i) => {
      // an ancestor opens at the moment its child came from
      const next = chain[i + 1];
      const t = !next ? '' : n.kind === 'run' ? (next.kind === 'timezoom' ? next.at_myr : next.t_myr) : n.kind === 'timezoom' ? next.timezoom_kyr : '';
      return `${i ? '<span class="sep">&rsaquo;</span>' : ''}<div class="crumb${n === cur ? ' cur' : ''}" data-key="${esc(n.key)}" data-t="${t ?? ''}" title="${esc(kindName(n) + ' ' + n.id + ': ' + nodeWhen(n))}">
        <img src="${esc(n.thumb)}" alt="" onerror="this.style.visibility='hidden'"><span>${esc(short(n, view))}</span></div>`;
    }).join('');
    crumbs.querySelector('.cur')?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }

  const busy = () => job && !job.finished;
  function actions(n) {
    const here = keyOf(view) === n.key, dis = busy() ? 'disabled' : '';
    if (n.kind === 'run' && here && view.kind === 'run') {
      const kyr = forms.kyr || 300;
      return `<button class="pl-btn sm" data-do="timezoom" ${dis} title="${kyr} kyr of ice ages from ${view.t} Myr">Time zoom from here</button>
        <select class="pl-btn sm" data-kyr title="How long the time zoom runs">${[100, 300, 1000].map((k) => `<option value="${k}"${k === kyr ? ' selected' : ''}>${k} kyr</option>`).join('')}</select>
        <button class="pl-btn sm" data-do="finishRun" ${dis} title="The full world at this keyframe">Finish world here</button>`;
    }
    if (n.kind === 'timezoom')
      return `<button class="pl-btn sm" data-do="finishTz" data-id="${esc(n.id)}" ${dis}>Finish ${here ? `at +${view.t} kyr` : 'at its end'}</button>
        <button class="pl-btn sm" data-do="finishIg" data-id="${esc(n.id)}" ${dis} title="The latest interglacial peak of the time zoom, like Earth today">Finish at the interglacial</button>
        <button class="pl-btn sm" data-do="finishGl" data-id="${esc(n.id)}" ${dis} title="The time zoom's last glacial maximum: lowest sea level, biggest ice sheets">Finish at the glacial maximum</button>`;
    if (n.kind === 'world') return worldActions(n, here, dis);
    if (n.kind === 'zoom' || n.kind === 'fine') return fineForm(n, dis);
    return '';
  }
  // a world: find highlights (on screen), zoom a region (a point and a size), zoom its top highlights
  function worldActions(n, here, dis) {
    const f = forms[n.key] ||= {}, pk = here ? host.picked?.() : null;
    if (pk && f.lat == null) { f.lat = pk.lat; f.lon = pk.lon; }
    const hlN = f.hl || 4;
    return `${here ? '<button class="pl-btn sm" data-do="highlights">Find highlights</button> ' : ''}
      <button class="pl-btn sm" data-do="hlZooms" data-id="${esc(n.id)}" ${dis} title="Regional zooms of the world's best highlights, as planet highlights --zoom N">Zoom the top</button>
      <select class="pl-btn sm" data-hln="${esc(n.key)}">${[2, 4, 6, 8].map((k) => `<option value="${k}"${k === hlN ? ' selected' : ''}>${k}</option>`).join('')}</select> <span class="sub">highlights</span>
      <div class="zf" data-form="${esc(n.key)}">Zoom a region: lat <input data-f="lat" value="${f.lat ?? ''}" placeholder="${pk || !here ? 'lat' : 'pick a cell'}"> lon <input data-f="lon" value="${f.lon ?? ''}" placeholder="lon">
        <select data-f="size">${SIZES.map((k) => `<option value="${k}"${k === +(f.size || 1000) ? ' selected' : ''}>${k} km</option>`).join('')}</select>
        <button class="pl-btn sm" data-do="zoomRegion" data-id="${esc(n.id)}" ${dis}>Zoom</button>${here ? ` <button class="pl-btn sm" data-do="usePicked" data-key="${esc(n.key)}" title="Take the cell picked on the globe">use picked cell</button>` : ''}</div>`;
  }
  // a zoom: a fine zoom inside it, at a point (default: its centre) and a size (default: 25-50 km at 50-100 m)
  function fineForm(n, dis) {
    const f = forms[n.key] ||= {}, c = n.center || {};
    return `<div class="zf" data-form="${esc(n.key)}">Fine zoom: lat <input data-f="lat" value="${f.lat ?? (+c.lat).toFixed(2)}"> lon <input data-f="lon" value="${f.lon ?? (+c.lon).toFixed(2)}">
      size <input data-f="size" value="${f.size ?? ''}" placeholder="default" title="km across; empty: the default for this zoom"> km
      <button class="pl-btn sm" data-do="fineZoom" data-id="${esc(n.id)}" ${dis}>Zoom in</button></div>`;
  }
  function renderTree() {
    const [p] = find(keyOf(view));
    if (!p) { tree.innerHTML = '<span class="muted">Nothing known about this view yet (a world dropped from a file, or not saved).</span>'; return; }
    const c = p.counts;
    tree.innerHTML = `<h3>${esc(p.name)}</h3><div class="muted" style="font-size:12px;margin-bottom:6px">${p.nodes.length} things: 1 run, ${c.timezoom} time zoom${c.timezoom === 1 ? '' : 's'},
      ${c.world} world${c.world === 1 ? '' : 's'}, ${c.zoom + c.fine} zoom${c.zoom + c.fine === 1 ? '' : 's'}. Click a picture or a name to open it.</div>
      ${jobHtml()}${treeHtml(p, keyOf(view), actions)}
      <div style="margin-top:8px"><a class="pl-btn" href="./#new">Make another planet</a></div>`;
  }
  function jobHtml() {
    if (!job) return '';
    return `<div style="margin:6px 0"><b>${esc(job.label)}</b>: ${job.status === 'error' ? (job.cancelled ? '<span class="muted">cancelled</span>' : `<span class="pl-err">${esc(job.error)}</span>`)
      : job.status === 'done' ? 'done' : `<span class="muted">${esc(job.message || job.status)}</span><div class="pl-bar"><div style="width:${Math.round(100 * (job.progress || 0))}%"></div></div>
      <button class="pl-btn sm danger" data-do="cancel">Cancel</button>`}</div>`;
  }

  async function refresh(force = false) {
    if (!force && Date.now() - fetched < 8000 && find(keyOf(view))[1]) return renderAll();
    planets = await getPlanets();
    fetched = Date.now();
    renderAll();
  }
  function renderAll() { renderBar(); if (!tree.hidden) renderTree(); }

  async function open(key, t) {
    const [p, n] = find(key);
    if (n) { tree.hidden = true; await host.openNode(n, p, t === '' || t == null ? null : +t); }
  }
  bar.addEventListener('click', (e) => {
    const c = e.target.closest('.crumb');
    if (c) return open(c.dataset.key, c.dataset.t);
    if (e.target.dataset.act === 'cancelJob') return doCancel();
    if (e.target.dataset.act === 'tree') { tree.hidden = !tree.hidden; if (!tree.hidden) { renderTree(); refresh(true); } }
  });
  tree.addEventListener('click', (e) => {
    const o = e.target.dataset.open;
    if (o) return open(o, null);
    const d = e.target.dataset.do;
    if (!d) return;
    if (d === 'cancel') return doCancel();
    if (d === 'usePicked') { const pk = host.picked?.(); if (pk) { Object.assign(forms[e.target.dataset.key] ||= {}, { lat: pk.lat, lon: pk.lon }); renderTree(); } return; }
    if (d === 'zoomRegion' || d === 'fineZoom') return zoomFromForm(e.target, d);
    if (d === 'hlZooms') {
      const k = e.target.parentElement.querySelector('[data-hln]'), n = +k.value;
      return start('highlight-zooms', { world: e.target.dataset.id, n }, `Zoom the top ${n} highlights`, 'zoom');
    }
    if (d === 'highlights') { tree.hidden = true; return host.findHighlights(); }
    if (d === 'timezoom') return start('timezoom', { run: view.id, t: view.t, kyr: forms.kyr || 300 }, `Time zoom from ${view.t} Myr (${forms.kyr || 300} kyr)`, 'timezoom');
    if (d === 'finishRun') return start('finish', { run: view.id, t: view.t }, `World at ${view.t} Myr`, 'world');
    if (d === 'finishIg' || d === 'finishGl') {
      const ig = d === 'finishIg';
      return start('finish', { timezoom: e.target.dataset.id, now: ig ? 'interglacial' : 'glacial' }, ig ? 'World at the interglacial' : 'World at the glacial maximum', 'world');
    }
    if (d === 'finishTz') {
      const same = view.kind === 'timezoom' && view.id === e.target.dataset.id;
      return start('finish', same ? { timezoom: view.id, kyr: view.t } : { timezoom: e.target.dataset.id }, same ? `World at +${view.t} kyr` : 'World at the end of the time zoom', 'world');
    }
  });

  // the inputs of a zoom form (typed values survive the tree's redraws), then the job
  function zoomFromForm(btn, d) {
    const box = btn.closest('[data-form]'), key = box.dataset.form, f = forms[key] ||= {};
    const get = (k) => box.querySelector(`[data-f=${k}]`)?.value.trim();
    Object.assign(f, { lat: get('lat'), lon: get('lon'), size: get('size') });
    const lat = parseFloat(f.lat), lon = parseFloat(f.lon), size = f.size ? parseFloat(f.size) : null;
    const fail = (m) => { job = { label: 'Zoom', status: 'error', finished: true, error: m }; renderAll(); };
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90) return fail('Give a latitude (-90..90) and a longitude, or pick a cell on the globe.');
    if (f.size && !(size > 0)) return fail('The size is a number of km.');
    if (d === 'fineZoom') return start('zoom', { zoom: btn.dataset.id, lat, lon, ...(size ? { size_km: size } : {}) }, `Fine zoom at ${lat.toFixed(2)}, ${lon.toFixed(2)}`, 'zoom');
    const src = key === keyOf(view) ? host.zoomSource?.() : { world: btn.dataset.id };
    if (!src) return fail('This view cannot be zoomed (a generated world has no rock or climate layers; zoom the world made from a run).');
    const km = size || 1000;
    return start('zoom', { ...src, lat, lon, size_km: km, res_km: km / 500 }, `${km} km zoom at ${lat.toFixed(2)}, ${lon.toFixed(2)}`, 'zoom');
  }
  async function doCancel() {
    if (!job?.id || job.finished) return;
    cancelBtn.disabled = true;
    await cancelJob(job.id);  // (the poll then sees it ended)
  }
  tree.addEventListener('input', (e) => {  // (remember what is typed)
    const box = e.target.closest('[data-form]'), k = e.target.dataset.f;
    if (box && k) (forms[box.dataset.form] ||= {})[k] = e.target.value;
    if (e.target.dataset.hln) (forms[e.target.dataset.hln] ||= {}).hl = +e.target.value;
    if (e.target.dataset.kyr !== undefined) forms.kyr = +e.target.value;
  });

  async function start(path, req, label, result) {
    if (busy()) return;
    job = { label, status: 'starting', progress: 0 };
    renderAll();
    const out = await postJob(path, req);
    if (out.error) { Object.assign(job, { status: 'error', finished: true, error: out.error }); return renderAll(); }
    job.id = out.job;
    cancelBtn.hidden = false; cancelBtn.disabled = false;
    const res = await trackJob(out.job, (j) => {
      Object.assign(job, j);
      jobEl.textContent = j.status === 'error' || j.status === 'done' ? '' : `${label}: ${Math.round(100 * (j.progress || 0))}%`;
      if (!tree.hidden) renderTree();
    });
    job.finished = true;
    jobEl.textContent = '';
    cancelBtn.hidden = true;
    await refresh(true);
    if (res.status === 'done') {
      const [p, n] = find(result === 'world' ? `world:${res.world}` : result === 'zoom' ? `zoom:${res.zoom}` : `run:${res.run}`);
      if (n) await host.openNode(n, p, null);
    }
    renderAll();
  }

  return {
    // the view changed: redraw the chain (fetches the planets again if this one isn't known yet)
    set(v) { view = v; refresh(); },
    // only the time on screen changed (playback)
    time(t) { if (view) { view.t = t; if (view.kind === 'run' || view.kind === 'timezoom') { const c = crumbs.querySelector('.cur span'); const [, n] = find(keyOf(view)); if (c && n) c.textContent = short(n, view); } } },
    refresh: () => refresh(true),
  };
}
