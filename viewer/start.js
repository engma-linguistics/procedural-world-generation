// The start screen (PW-472): a gallery of the planets already made (runs, time zooms, worlds, zooms
// grouped by what they came from: planet/family.py) and a "New planet" form that starts planet/make.py's
// chain as a server job (POST /api/make) and follows its progress. Shown by index.html when the address
// names nothing to open; opening anything is a plain navigation (?run=, ?world=, ?world=&tab=zoom&zoom=).
import { createGlobePicker } from './globepick.js';
import { cancelJob, deleteNode, esc, favKey, fmtDuration, getFavourites, getPlanets, setFavourite, starHtml, injectCss, kindName, nodeWhen, openUrl, postJob, primaryNode, trackJob, treeHtml } from './planets.js';

const CSS = `
#start { position: fixed; inset: 0; z-index: 40; overflow-y: auto; background: var(--bg); color: var(--text); }
#start .wrap { max-width: 1120px; margin: 0 auto; padding: 16px; }
#start header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
#start h1 { font-size: 20px; margin: 0; flex: 1; min-width: 160px; }
#start h2 { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin: 18px 0 6px; }
#start .seg { display: flex; gap: 6px; flex-wrap: wrap; }
#start .seg button { background: var(--ctl); color: var(--text); border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; cursor: pointer; font: inherit; }
#start .seg button.on { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
#start .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }
#start .card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 8px; display: flex; flex-direction: column; gap: 6px; }
#start .card:hover { border-color: var(--accent); }
#start .card .pic { cursor: pointer; }
#start .card .pl-thumb { object-fit: contain; }
#start .views { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-bottom: 10px; }
#start .views .lbl { color: var(--muted); font-size: 12px; }
#start .views button { background: var(--ctl); color: var(--text); border: 1px solid var(--border); padding: 4px 10px; border-radius: 6px; cursor: pointer; font: inherit; font-size: 12px; }
#start .views button[aria-pressed=true] { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
#start .find { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin: 4px 0 10px; }
#start .find input[type=search] { flex: 1 1 220px; min-width: 0; background: var(--ctl); color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 5px 8px; font: inherit; }
#start .find select { width: auto; padding: 4px 6px; }
#start .find .lbl { color: var(--muted); font-size: 12px; }
#start .find button { background: var(--ctl); color: var(--text); border: 1px solid var(--border); padding: 4px 10px; border-radius: 12px; cursor: pointer; font: inherit; font-size: 12px; }
#start .find button[aria-pressed=true] { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
#start .find .count { color: var(--muted); font-size: 12px; margin-left: auto; }
#start .chip.peoples { color: var(--accent); border-color: var(--accent); }
#start .card .nm { font-weight: 600; overflow-wrap: anywhere; }
#start .card .meta { color: var(--muted); font-size: 12px; }
#start .chips { display: flex; flex-wrap: wrap; gap: 4px; }
#start .chip { font-size: 11px; padding: 0 7px; border-radius: 9px; border: 1px solid var(--border); color: var(--muted); }
#start .card .row { display: flex; gap: 6px; margin-top: auto; }
#start .card .row .pl-btn:first-child { flex: 1; }
#start .empty { color: var(--muted); padding: 24px 0; }
#start .banner { background: var(--panel); border: 1px solid var(--accent); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; }
#start form { display: grid; gap: 14px; max-width: 760px; }
#start fieldset { border: 1px solid var(--border); border-radius: 8px; margin: 0; padding: 8px 12px 12px; min-width: 0; }
#start legend { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; padding: 0 6px; }
#start .presets { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 8px; }
#start .preset { text-align: left; background: var(--ctl); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 8px; cursor: pointer; font: inherit; }
#start .preset.on { border-color: var(--accent); background: #16263b; }
#start .preset b { display: block; }
#start .preset span { color: var(--muted); font-size: 12px; }
#start .f { display: grid; grid-template-columns: minmax(120px, 190px) 1fr; gap: 4px 12px; align-items: center; padding: 3px 0; }
#start .f .hp { grid-column: 2; color: var(--muted); font-size: 11px; margin-top: -2px; }
#start input[type=number], #start select { background: var(--ctl); color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 6px; font: inherit; width: 100%; min-width: 0; }
#start input[type=range] { width: 100%; }
#start .inl { display: flex; gap: 8px; align-items: center; }
#start label.ck { display: flex; gap: 8px; align-items: center; padding: 4px 0; cursor: pointer; flex-wrap: wrap; }
#start label.ck > span { flex: 1 1 200px; min-width: 0; }
#start input[type=checkbox] { width: 18px; height: 18px; flex: none; }
#start .est { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 12px; }
#start .est .st { display: flex; justify-content: space-between; gap: 12px; }
#start .est .tot { border-top: 1px solid var(--border); margin-top: 4px; padding-top: 4px; font-weight: 600; }
#start .gaps { color: var(--muted); font-size: 12px; }
#start details > summary { cursor: pointer; color: var(--muted); }
#start .modal { position: fixed; inset: 0; z-index: 45; background: rgba(5, 8, 14, .7); display: flex; align-items: center; justify-content: center; }
#start .modal .box { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; width: min(760px, calc(100vw - 24px)); max-height: 88vh; overflow-y: auto; }
#start .modal h3 { margin: 0 0 8px; font-size: 15px; }
@media (max-width: 560px) {
  #start .f { grid-template-columns: 1fr; } #start .f .hp { grid-column: 1; }
  #start .grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
}
`;

const JOB_KEY = 'planet.makeJob';
const store = {
  get() { try { return JSON.parse(localStorage.getItem(JOB_KEY) || 'null'); } catch { return null; } },
  set(v) { try { v ? localStorage.setItem(JOB_KEY, JSON.stringify(v)) : localStorage.removeItem(JOB_KEY); } catch { /* private window */ } },
};

export async function showStart() {
  injectCss();
  const st = document.createElement('style'); st.textContent = CSS; document.head.append(st);
  const el = document.createElement('div');
  el.id = 'start';
  el.innerHTML = `<div class="wrap"><header><h1>Planet Viewer</h1>
    <div class="seg" id="stTabs"><button data-tab="gallery" class="on">Planets</button><button data-tab="new">New planet</button></div></header>
    <div id="stBanner"></div><section id="stGallery"><div class="views" hidden>
      <span class="lbl">Show</span><button data-view="both">Globe and list</button><button data-view="globe">Globe only</button><button data-view="list">List only</button></div>
      <div class="find" hidden><input type="search" id="stQ" placeholder="Search by name, seed or id" aria-label="Search the planets">
        <span class="lbl">Sort</span><select id="stSort" title="The order of the planets"><option value="newest">newest first</option><option value="starred">starred first</option><option value="name">by name</option></select>
        <span class="lbl">Only</span><button data-f="peoples" title="Planets with at least one peoples run">has peoples</button><button data-f="l7" title="Showcase detail (grid level 7)">L7</button><button data-f="starred" title="Planets with anything starred">starred</button>
        <span class="count" id="stCount"></span></div>
      <div id="stGlobe"></div><div id="stList"></div></section><section id="stNew" hidden></section></div>`;
  document.body.append(el);
  const $ = (s) => el.querySelector(s);
  let planets = [], favs = new Set();

  const tab = (name) => {
    $('#stGallery').hidden = name !== 'gallery'; $('#stNew').hidden = name !== 'new';
    [...$('#stTabs').children].forEach((b) => b.classList.toggle('on', b.dataset.tab === name));
    if (name === 'new' && !$('#stNew').firstChild) buildForm();
  };
  $('#stTabs').addEventListener('click', (e) => e.target.dataset.tab && tab(e.target.dataset.tab));

  // ------------------------------------------------------------ gallery
  // which views are on (the globe picker, the list of Equal Earth maps), remembered per browser
  const VIEW_KEY = 'planet.startViews';
  const views = { globe: true, list: true };
  try { Object.assign(views, JSON.parse(localStorage.getItem(VIEW_KEY) || '{}')); } catch { /* private window */ }
  const saveViews = () => { try { localStorage.setItem(VIEW_KEY, JSON.stringify(views)); } catch { /* private window */ } };
  const metaOf = (p) => [p.seed != null && `seed ${p.seed}`, p.level != null && `L${p.level}`, p.myr && `${p.myr} Myr`, (p.updated || '').slice(0, 10)].filter(Boolean).join(' · ');
  const picker = createGlobePicker($('#stGlobe'), () => shown, (p) => openUrl(p, primaryNode(p)), metaOf);
  if (!views.globe && !views.list) views.list = true;  // (the old two toggles could turn both off)
  function applyViews() {
    $('#stList').hidden = !views.list;
    const cur = views.globe && views.list ? 'both' : views.globe ? 'globe' : 'list';
    $('#stGallery .views').querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === cur)));
    if (views.globe && shown.length) { picker.show(); picker.refresh(); } else picker.hide();
  }
  $('#stGallery .views').addEventListener('click', (e) => {
    const v = e.target.dataset.view;
    if (!v) return;
    views.globe = v !== 'list'; views.list = v !== 'globe'; saveViews(); applyViews();
  });
  // ------------------------------------------------------------ search, sort, filters (PW-1028; the sort and filters remembered per browser)
  const FIND_KEY = 'planet.startFind';
  const find = { q: '', sort: 'newest', only: [] };
  try { Object.assign(find, JSON.parse(localStorage.getItem(FIND_KEY) || '{}')); } catch { /* private window */ }
  const saveFind = () => { try { localStorage.setItem(FIND_KEY, JSON.stringify({ sort: find.sort, only: find.only })); } catch { /* private window */ } };
  const peoplesOf = (p) => p.nodes.filter((n) => n.phase === 'lineages').length;
  const starredOf = (p) => p.nodes.some((n) => favs.has(favKey(n)));
  let shown = [];  // the planets that pass the search and filters, in the chosen order
  function filterPlanets() {
    const words = find.q.toLowerCase().split(/\s+/).filter(Boolean);
    const hay = (p) => [p.name, p.key, p.seed != null ? `seed ${p.seed}` : '', ...p.nodes.map((n) => `${n.id} ${n.name || ''}`)].join(' ').toLowerCase();
    shown = planets.filter((p) => words.every((w) => hay(p).includes(w))
      && (!find.only.includes('peoples') || peoplesOf(p)) && (!find.only.includes('l7') || p.level === 7) && (!find.only.includes('starred') || starredOf(p)));
    const newest = (a, b) => (b.updated || b.created || '').localeCompare(a.updated || a.created || '');
    shown.sort(find.sort === 'name' ? (a, b) => a.name.localeCompare(b.name, undefined, { numeric: true })
      : find.sort === 'starred' ? (a, b) => (starredOf(b) - starredOf(a)) || newest(a, b) : newest);
  }
  $('#stQ').value = find.q;
  $('#stSort').value = find.sort;
  const syncFind = () => $('#stGallery .find').querySelectorAll('[data-f]').forEach((b) => b.setAttribute('aria-pressed', String(find.only.includes(b.dataset.f))));
  syncFind();
  $('#stQ').addEventListener('input', () => { find.q = $('#stQ').value; drawGallery(); });
  $('#stSort').addEventListener('change', () => { find.sort = $('#stSort').value; saveFind(); drawGallery(); });
  $('#stGallery .find').addEventListener('click', (e) => {
    const f = e.target.dataset.f;
    if (!f) return;
    find.only = find.only.includes(f) ? find.only.filter((x) => x !== f) : [...find.only, f];
    saveFind(); syncFind(); drawGallery();
  });
  async function loadGallery() {
    $('#stList').innerHTML = '<div class="empty">Loading...</div>';
    [planets, favs] = await Promise.all([getPlanets(), getFavourites()]);
    drawGallery();
  }
  function drawGallery() {
    $('#stGallery .views').hidden = !planets.length;
    $('#stGallery .find').hidden = !planets.length;
    filterPlanets();
    $('#stCount').textContent = shown.length === planets.length ? `${planets.length} planets` : `${shown.length} of ${planets.length} planets`;
    applyViews();
    if (!planets.length) {
      $('#stList').innerHTML = `<div class="empty">No planets yet. <button class="pl-btn primary" data-act="new">Make the first one</button>
        <p>You can also drop a world .json on this page's viewer.</p></div>`;
      return;
    }
    if (!shown.length) { $('#stList').innerHTML = '<div class="empty">No planet matches. Clear the search or the filters above.</div>'; return; }
    $('#stList').innerHTML = `<div class="grid">${shown.map((p) => {
      const i = planets.indexOf(p), np = peoplesOf(p);
      const c = p.counts, chips = [np && `${np} peoples run${np > 1 ? 's' : ''}`, c.timezoom && `${c.timezoom} time zoom${c.timezoom > 1 ? 's' : ''}`, c.world && `${c.world} world${c.world > 1 ? 's' : ''}`,
        (c.zoom + c.fine) && `${c.zoom + c.fine} zoom${c.zoom + c.fine > 1 ? 's' : ''}`].filter(Boolean);
      const meta = metaOf(p), starred = p.nodes.some((n) => favs.has(favKey(n)));
      return `<div class="card" data-i="${i}"><div class="pic" data-act="open"><img class="pl-thumb" src="${esc(p.thumb)}" alt="" loading="lazy" onerror="this.style.visibility='hidden'"></div>
        <div class="nm">${starHtml(favs.has(favKey(primaryNode(p))), 'data-act="star"')}${starred && !favs.has(favKey(primaryNode(p))) ? '<span title="Another part of this planet is starred (see Family)" style="color:var(--star)"> \u2605</span> ' : ' '}${esc(p.name)}</div><div class="meta">${esc(meta)}${p.run ? '' : ' · run deleted'}</div>
        <div class="chips">${chips.map((x) => `<span class="chip${x.includes('peoples') ? ' peoples' : ''}">${x}</span>`).join('')}</div>
        <div class="row"><button class="pl-btn primary" data-act="open">Open</button><button class="pl-btn" data-act="details" title="Everything made from this planet: its runs, time zooms, peoples runs, worlds and zooms">Family (${p.nodes.length})</button></div></div>`;
    }).join('')}</div>`;
  }
  $('#stGallery').addEventListener('click', async (e) => {
    const b = e.target.closest('[data-act]');
    if (!b) return;
    if (b.dataset.act === 'new') return tab('new');
    const p = planets[+b.closest('.card').dataset.i];
    if (b.dataset.act === 'star') {
      const k = favKey(primaryNode(p));
      if (!(await setFavourite(k, !favs.has(k)))) return alert('Could not save the favourite. Is the viewer running via planet serve?');
      favs = await getFavourites();
      return drawGallery();
    }
    if (b.dataset.act === 'open') location.href = openUrl(p, primaryNode(p));
    if (b.dataset.act === 'details') details(p);
  });

  function details(p) {
    const m = document.createElement('div');
    m.className = 'modal';
    m.innerHTML = `<div class="box"><div class="inl" style="justify-content:space-between"><h3>${esc(p.name)}</h3>
      <button class="pl-btn sm" data-act="close">Close</button></div>
      <div class="meta muted" style="color:var(--muted);font-size:12px;margin-bottom:8px">Each step shows what it was made from: run, then time zoom, finished world and zooms. Click one to open it.</div>
      ${treeHtml(p, null, (n) => `${n.kind === 'fine' || n.kind === 'zoom' ? '' : starHtml(favs.has(favKey(n)), `data-fav="${esc(n.key)}"`)} <button class="pl-btn sm danger" data-del="${esc(n.key)}">Delete</button>`)}
      <div style="margin-top:12px"><button class="pl-btn danger" data-act="delall">Delete this whole planet</button></div></div>`;
    el.append(m);
    m.addEventListener('click', async (e) => {
      if (e.target === m || e.target.dataset.act === 'close') return m.remove();
      const open = e.target.dataset.open;
      if (open) return (location.href = openUrl(p, p.nodes.find((n) => n.key === open)));
      const fav = e.target.dataset.fav && p.nodes.find((n) => n.key === e.target.dataset.fav);
      if (fav) {
        const k = favKey(fav);
        if (!(await setFavourite(k, !favs.has(k)))) return alert('Could not save the favourite.');
        m.remove(); await loadGallery();
        const again = planets.find((q) => q.key === p.key);
        if (again) details(again);
        return;
      }
      const del = e.target.dataset.del && p.nodes.find((n) => n.key === e.target.dataset.del);
      if (del) {
        const below = p.nodes.filter((n) => n.parent === del.key).length;
        if (!confirm(`Delete ${kindName(del)} ${del.id} from disk?` + (del.kind === 'world' ? '\nIts zooms and highlights go with it.' : '')
          + (below && del.kind !== 'world' ? '\nWhat was made from it stays.' : ''))) return;
        if (!(await deleteNode(del))) return alert('Delete failed. Is the viewer running via planet serve?');
        m.remove(); await loadGallery();
        const again = planets.find((q) => q.key === p.key);
        if (again) details(again);
      }
      if (e.target.dataset.act === 'delall') {
        if (!confirm(`Delete ${p.name} and all ${p.nodes.length} things made from it? This removes them from disk.`)) return;
        const order = ['world', 'fine', 'zoom', 'timezoom', 'run'];  // (worlds take their zooms with them)
        for (const k of order) for (const n of p.nodes.filter((x) => x.kind === k)) await deleteNode(n);
        m.remove(); await loadGallery();
      }
    });
  }

  // ------------------------------------------------------------ a running make job (survives a reload)
  let followed = null;  // the make job on screen (its Cancel button)
  el.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-act=cancel]');
    if (!b || !followed) return;
    b.disabled = true; b.textContent = 'Cancelling...';
    await cancelJob(followed);  // (the next poll shows it as cancelled)
  });
  async function follow(jobId) {
    store.set({ job: jobId });
    followed = jobId;
    const view = $('#stBanner');
    const res = await trackJob(jobId, (j) => {
      const pct = Math.round(100 * (j.progress || 0));
      view.innerHTML = `<div class="banner"><b>Making a planet</b> <span class="muted">${esc(j.request?.name || '')}</span><br>
        <span class="muted">${esc(j.message || j.status)}</span><div class="pl-bar"><div style="width:${pct}%"></div></div>
        ${j.status === 'error' ? (j.cancelled ? '<span class="muted">Cancelled. What was already finished is kept.</span>' : `<span class="pl-err">${esc(j.error)}</span>`)
          : j.status === 'done' ? '' : '<button class="pl-btn sm danger" data-act="cancel" title="Stop this job; what it already finished is kept">Cancel</button>'}</div>`;
      const f = el.querySelector('#fmProgress');
      if (f) f.innerHTML = progressHtml(j);
    });
    store.set(null);
    followed = null;
    if (res.status === 'done') {
      const r = res.result || {};
      view.innerHTML = `<div class="banner"><b>Planet made.</b> ${r.world ? `<a href="?world=${r.world}.json">Open the world</a> · ` : ''}
        ${!r.world && r.timezoom ? `<a href="?run=${r.timezoom}">Open the time zoom</a> · ` : ''}${r.run ? `<a href="?run=${r.run}">Open the run</a>` : ''} <button class="pl-btn sm" data-act="dismiss">Dismiss</button></div>`;
      await loadGallery();
    }
    view.querySelector('[data-act=dismiss]')?.addEventListener('click', () => (view.innerHTML = ''));
    return res;
  }
  const progressHtml = (j) => {
    const pct = Math.round(100 * (j.progress || 0)), r = j.result || {};
    return `<div class="est"><b>${j.status === 'done' ? 'Done' : j.cancelled ? 'Cancelled' : j.status === 'error' ? 'Failed' : 'Making'}</b>
      <div class="pl-bar"><div style="width:${pct}%"></div></div><div class="muted">${esc(j.message || j.status)}</div>
      ${j.status === 'error' && !j.cancelled ? `<div class="pl-err">${esc(j.error)}</div>` : ''}
      ${j.status === 'error' ? '' : j.status === 'done' ? '' : '<div style="margin-top:4px"><button type="button" class="pl-btn sm danger" data-act="cancel" title="Stop this job; what it already finished is kept">Cancel</button></div>'}
      ${j.status === 'done' ? `<div style="margin-top:6px">${r.world ? `<a class="pl-btn primary" href="?world=${r.world}.json">Open the world</a> ` : ''}
        ${!r.world && r.timezoom ? `<a class="pl-btn primary" href="?run=${r.timezoom}">Open the time zoom</a> ` : ''}
        ${r.run ? `<a class="pl-btn" href="?run=${r.run}">Open the run</a>` : ''}</div>` : ''}</div>`;
  };

  // ------------------------------------------------------------ the New planet form
  async function buildForm() {
    const box = $('#stNew');
    let opt;
    try { opt = await (await fetch('../api/make/options', { cache: 'no-store' })).json(); } catch { opt = null; }
    if (!opt) { box.innerHTML = '<div class="pl-err">The server has no make API. Restart it: uv run python -m planet serve</div>'; return; }
    const D = opt.defaults, byKey = Object.fromEntries(opt.settings.map((s) => [s.key, s]));
    const S = { preset: opt.default_preset, seed: Math.floor(Math.random() * 1e6), level: D.level, myr: opt.presets[opt.default_preset].myr,
      timezoom: D.timezoom, kyr: D.kyr, now: D.now, nowKey: D.now, finish: D.finish, highlights: D.highlights, zooms: D.zooms, vals: {} };
    const eff = (k) => (k in opt.presets[S.preset].set ? opt.presets[S.preset].set[k] : byKey[k].default);  // value without the user's change
    const cur = (k) => (k in S.vals ? S.vals[k] : eff(k));
    const levelNote = { 5: 'tiny, for testing', 6: 'quick', 7: 'showcase' };
    box.innerHTML = `<form id="fm" autocomplete="off">
      <fieldset><legend>Kind of planet</legend><div class="presets">${Object.entries(opt.presets).map(([k, p]) =>
        `<button type="button" class="preset" data-preset="${k}"><b>${esc(p.label)}</b><span>${esc(p.blurb)}</span></button>`).join('')}</div></fieldset>
      <fieldset><legend>Basics</legend>
        <div class="f"><label for="fSeed">Seed</label><div class="inl"><input id="fSeed" type="number" min="0" step="1"><button type="button" class="pl-btn" id="fDice" title="A random seed">Random</button></div>
          <div class="hp">The same seed and settings give the same planet.</div></div>
        <div class="f"><label>Detail (grid level)</label><div class="seg" id="fLevel">${[5, 6, 7].map((L) => `<button type="button" data-l="${L}">${L}<small style="display:block;font-size:10px;opacity:.8">${levelNote[L]}</small></button>`).join('')}</div>
          <div class="hp" id="fLevelHp"></div></div>
        <div class="f"><label for="fMyr">Length (Myr)</label><div class="inl"><input id="fMyr" type="range" min="100" max="2000" step="100"><b id="fMyrV" style="min-width:64px;text-align:right"></b></div>
          <div class="hp">How long plate tectonics, climate and erosion run. Longer gives older, more worked-over land.</div></div></fieldset>
      <fieldset><legend>What to make</legend>
        <label class="ck"><input type="checkbox" id="fTz"><span>Ice-age time zoom from a typical moment of the run</span>
          <select id="fKyr" style="width:auto;flex:none">${[100, 300, 1000].map((k) => `<option value="${k}">${k} kyr</option>`).join('')}</select></label>
        <label class="ck"><input type="checkbox" id="fFinish"><span>Finished world (climate, rivers, lakes, biomes) <span style="color:var(--muted)">at a typical moment of the run without a time zoom, or at:</span></span>
          <select id="fNow" style="width:auto;flex:none" title="Which moment of the ice-age cycle is the planet's present">${opt.nows.map((w) => `<option value="${w.key}">${esc(w.label)}</option>`).join('')}</select>
          or <input id="fNowKyr" type="number" min="0" step="1" placeholder="kyr" title="A specific kyr of the time zoom (overrides the choice above)" style="width:90px"> kyr</label>
        <label class="ck"><input type="checkbox" id="fHl"><span>Highlights (the most interesting places)</span></label>
        <label class="ck"><span>Regional zooms of the top highlights:</span> <select id="fZooms" style="width:auto;flex:none">${[0, 2, 4, 6].map((k) => `<option value="${k}">${k}</option>`).join('')}</select></label></fieldset>
      <fieldset><legend>Planet settings</legend><div id="fSettings">${opt.settings.map((s) => `<div class="f"><label for="s_${s.key}">${esc(s.label)}</label>${
        s.type === 'choice' ? `<select id="s_${s.key}" data-k="${s.key}">${s.choices.map((c) => `<option>${c}</option>`).join('')}</select>`
          : `<input id="s_${s.key}" data-k="${s.key}" type="number" min="${s.min}" max="${s.max}" step="${s.type === 'int' ? 1 : 0.1}">`}
        <div class="hp">${esc(s.help)}</div></div>`).join('')}</div>
        <details style="margin-top:8px"><summary>Not configurable yet</summary><div class="gaps">The model has no parameter for: ${opt.unsupported.map(esc).join('; ')}.</div></details></fieldset>
      <div class="est" id="fEst">...</div>
      <div><button type="submit" class="pl-btn primary" id="fGo" style="padding:8px 18px;font-size:14px">Make planet</button></div>
      <div id="fmProgress"></div></form>`;
    const q = (s) => box.querySelector(s);
    const sync = () => {
      box.querySelectorAll('.preset').forEach((b) => b.classList.toggle('on', b.dataset.preset === S.preset));
      q('#fSeed').value = S.seed; q('#fMyr').value = S.myr; q('#fMyrV').textContent = `${S.myr} Myr`;
      box.querySelectorAll('#fLevel button').forEach((b) => b.classList.toggle('on', +b.dataset.l === S.level));
      q('#fLevelHp').textContent = `${opt.levels.find((l) => l.level === S.level).cells.toLocaleString()} cells; a run takes about ${fmtDuration(opt.levels.find((l) => l.level === S.level).run_s_per_gyr)} per Gyr.`;
      q('#fTz').checked = S.timezoom; q('#fKyr').value = S.kyr; q('#fKyr').disabled = !S.timezoom;
      q('#fFinish').checked = S.finish; q('#fNow').value = S.nowKey; q('#fNow').disabled = !S.finish || !S.timezoom;
      q('#fNowKyr').value = typeof S.now === 'number' ? S.now : ''; q('#fNowKyr').max = S.kyr; q('#fNowKyr').disabled = !S.finish || !S.timezoom;q('#fHl').checked = S.highlights && S.finish; q('#fHl').disabled = !S.finish;
      q('#fZooms').value = S.zooms; q('#fZooms').disabled = !S.finish || !S.highlights;
      for (const s of opt.settings) { const i = q('#s_' + s.key); i.value = cur(s.key); i.style.borderColor = s.key in S.vals ? 'var(--accent)' : ''; }
      estimate();
    };
    const request = () => ({ seed: S.seed, preset: S.preset, level: S.level, myr: S.myr, timezoom: S.timezoom, kyr: S.kyr, now: S.now, finish: S.finish,
      highlights: S.highlights && S.finish, zooms: S.finish && S.highlights ? S.zooms : 0, set: S.vals });
    let estTimer = null;
    const estimate = () => {
      clearTimeout(estTimer);
      estTimer = setTimeout(async () => {
        const r = request();
        const qs = new URLSearchParams({ seed: r.seed, preset: r.preset, level: r.level, myr: r.myr, kyr: r.kyr, now: r.now, zooms: r.zooms,
          timezoom: r.timezoom ? 1 : 0, finish: r.finish ? 1 : 0, highlights: r.highlights ? 1 : 0 });
        let out;
        try { out = await (await fetch('../api/make/estimate?' + qs)).json(); } catch { return; }
        q('#fEst').innerHTML = out.error ? `<span class="pl-err">${esc(out.error)}</span>`
          : out.stages.map((s) => `<div class="st"><span>${esc(s.label)}</span><span class="muted">~${fmtDuration(s.s)}</span></div>`).join('')
            + `<div class="st tot"><span>About</span><span>${fmtDuration(out.total_s)}</span></div><div class="muted">A typical machine, one job at a time; busier machines take longer.</div>`;
        q('#fGo').disabled = !!out.error;
      }, 150);
    };
    box.addEventListener('click', (e) => {
      const pr = e.target.closest('[data-preset]');
      if (pr) { S.preset = pr.dataset.preset; S.myr = opt.presets[S.preset].myr; S.vals = {}; sync(); }
      const lv = e.target.closest('#fLevel button');
      if (lv) { S.level = +lv.dataset.l; sync(); }
      if (e.target.id === 'fDice') { S.seed = Math.floor(Math.random() * 1e6); sync(); }
    });
    box.addEventListener('input', (e) => {
      const t = e.target;
      if (t.id === 'fSeed') S.seed = Math.max(0, Math.floor(+t.value || 0));
      else if (t.id === 'fMyr') { S.myr = +t.value; q('#fMyrV').textContent = `${S.myr} Myr`; }
      else if (t.id === 'fTz') S.timezoom = t.checked;
      else if (t.id === 'fKyr') S.kyr = +t.value;
      else if (t.id === 'fNow') { S.nowKey = t.value; S.now = t.value; q('#fNowKyr').value = ''; }
      else if (t.id === 'fNowKyr') S.now = t.value === '' ? S.nowKey : +t.value;  // (the server checks the range)
      else if (t.id === 'fFinish') S.finish = t.checked;
      else if (t.id === 'fHl') S.highlights = t.checked;
      else if (t.id === 'fZooms') S.zooms = +t.value;
      else if (t.dataset.k) {
        const s = byKey[t.dataset.k], v = s.type === 'choice' ? t.value : +t.value;
        if (t.value === '' || v === eff(s.key)) delete S.vals[s.key]; else S.vals[s.key] = v;
        t.style.borderColor = s.key in S.vals ? 'var(--accent)' : '';
      }
      if (t.id !== 'fMyr') sync(); else estimate();
    });
    q('#fm').addEventListener('submit', async (e) => {
      e.preventDefault();
      q('#fGo').disabled = true;
      const out = await postJob('make', request());
      if (out.error) { q('#fmProgress').innerHTML = `<div class="est pl-err">${esc(out.error)}</div>`; q('#fGo').disabled = false; return; }
      q('#fmProgress').innerHTML = progressHtml({ status: 'queued', progress: 0, message: 'queued' });
      follow(out.job).finally(() => { q('#fGo').disabled = false; });
    });
    sync();
  }

  // ------------------------------------------------------------ go
  const pending = store.get();
  if (pending?.job) follow(pending.job);
  await loadGallery();
  if (!planets.length && !pending?.job) tab('new');
  return { el, tab };
}
