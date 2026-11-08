'use strict';
// The peoples workbench's Technology tab (PW-913; the data: planet/lineages/techtree.py, meta.techtree of a peoples run).
// Six views of one run's record of which people knew which tech, since when and how it came to them, from the owner's
// pick of the mock-ups in docs/review/techtree-views/ (2026-10-29):
//   tree      the tech tree, eras left to right and tracks as lanes, as seen by one people (the default view)
//   timeline  a row per people on a log time axis, a dot per tech it came to
//   map       one tech on the globe (index.html embedded, its 'technology' layer: the run's own cells at every stored moment)
//   inventory one people's kit by track, with what could come next and why not yet
//   cascade   one tech's transmission tree: who had it from whom, and how long it waited at each border
//   table     the first tab's matrix: every people against every tech, and the firsts
//   spread    how fast one tech (writing by default) spread: the share of settled people that knew it over time, and who had it
//             when and from whom, per people and per culture (GET /api/techspread, planet/lineages/techspread.py; lane 184)
// A classic script: lineages.html calls TechTab.draw(el, result) with result = { id, ...run.meta } of the picked run.
(() => {
  const CSS = `
#tab-tech.on { display: grid; grid-template-rows: auto auto minmax(0, 1fr); padding: 0; overflow: hidden; }
#tab-tech .tt-nav { display: flex; gap: 2px; align-items: center; padding: 0 12px; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
#tab-tech .tt-nav button { border: 0; border-bottom: 2px solid transparent; border-radius: 0; background: none; padding: 6px 12px; color: var(--muted); }
#tab-tech .tt-nav button.on { color: var(--text); border-bottom-color: var(--acc); }
#tab-tech .tt-bar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; padding: 6px 12px; border-bottom: 1px solid var(--line); background: var(--panel); }
#tab-tech .tt-main { min-height: 0; overflow: hidden; }
#tab-tech .tt-split { display: grid; grid-template-columns: minmax(0, 1fr) 340px; height: 100%; }
#tab-tech .tt-side { border-left: 1px solid var(--line); background: var(--panel); overflow: auto; padding: 10px; }
#tab-tech .tt-scroll { overflow: auto; position: relative; height: 100%; }
#tab-tech .tt-pad { overflow: auto; height: 100%; padding: 10px 12px; }
#tab-tech .tt-axis { position: sticky; top: 0; z-index: 3; background: var(--bg); display: block; }
#tab-tech svg { display: block; }
#tab-tech table.t td.n { white-space: nowrap; }
#tab-tech .key { display: inline-flex; gap: 10px; flex-wrap: wrap; align-items: center; color: var(--muted); font-size: 12px; }
#tab-tech button.on { border-color: var(--acc); color: var(--acc); }
#tab-tech .tt-tree { cursor: grab; } #tab-tech .tt-tree.panning { cursor: grabbing; user-select: none; }
#tab-tech .node { cursor: pointer; }
#tab-tech .node rect.bg { fill: #1b2330; stroke: #2f3a4d; }
#tab-tech .node.known rect.bg { fill: #223047; stroke: #4a5b78; }
#tab-tech .node.frontier rect.bg { stroke: #e3c26b; stroke-dasharray: 4 3; }
#tab-tech .node.dim { opacity: .28; }
#tab-tech .node.hl rect.bg { stroke: var(--acc); stroke-width: 2; }
#tab-tech .node .when { fill: var(--muted); font-size: 10px; }
#tab-tech path.e { fill: none; stroke: #3a4658; stroke-width: 1; opacity: .55; }
#tab-tech path.e.up { stroke: #e3c26b; opacity: 1; stroke-width: 1.6; }
#tab-tech path.e.down { stroke: var(--acc); opacity: 1; stroke-width: 1.6; }
#tab-tech path.e.faded { opacity: .12; }
#tab-tech .era text { fill: var(--muted); font-size: 12px; font-weight: 600; }
#tab-tech circle.d, #tab-tech .nd { cursor: pointer; }
#tab-tech .row:hover rect.bg { fill: #182131; }
#tab-tech .tt-map { position: relative; height: 100%; }
#tab-tech .tt-map iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; background: var(--bg); }
#tab-tech .tt-side table.t tr[data-k] { cursor: pointer; } #tab-tech .tt-side table.t tr[data-k]:hover td { background: var(--ctl-hi); }
#tab-tech .tt-side table.t tr.future td { opacity: .35; }
#tab-tech .kpi { display: flex; gap: 22px; flex-wrap: wrap; margin: 2px 0 10px; align-items: flex-end; }
#tab-tech .kpi div b { display: block; font-size: 17px; } #tab-tech .kpi div span { color: var(--muted); font-size: 11px; }
#tab-tech .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }
#tab-tech .card h3 { margin: 0 0 6px; display: flex; gap: 6px; align-items: center; } #tab-tech .card h3 .muted { font-weight: normal; margin-left: auto; font-size: 11px; }
#tab-tech .chips { display: flex; flex-wrap: wrap; gap: 4px; }
#tab-tech .chip { border: 1px solid var(--line); border-radius: 4px; padding: 2px 6px 2px 5px; font-size: 12px; cursor: default; background: #141a22; color: var(--muted); border-left-width: 4px; white-space: nowrap; }
#tab-tech .chip.k { background: #1f2a3a; color: var(--text); }
#tab-tech .chip.f { border-style: dashed; border-left-style: solid; color: #e8d9a8; }
#tab-tech .chip .w { color: var(--muted); font-size: 10px; margin-left: 4px; }
#tab-tech .chip.need { outline: 2px solid #e3c26b; } #tab-tech .chip.lead { outline: 2px solid var(--acc); } #tab-tech .chip.me { outline: 2px solid #fff; }
#tab-tech .chip .vs { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-left: 4px; vertical-align: 1px; }
#tab-tech .people { display: flex; gap: 10px; align-items: center; } #tab-tech .people .big { font-size: 16px; font-weight: 600; }
.tt-tip { position: fixed; display: none; z-index: 50; max-width: 380px; background: #1b2330; border: 1px solid #3a4658; border-radius: 5px; padding: 6px 8px; pointer-events: none; font-size: 12px; box-shadow: 0 4px 14px #0008; }
.tt-tip .src { margin-top: 4px; font-size: 11px; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  // a name cut to n characters at a word, with an ellipsis (never mid-word: "bread and flatbread bakin", PW-1047)
  const clipWords = (s, n) => {
    if (s.length <= n) return s;
    const cut = s.slice(0, n - 1), sp = cut.lastIndexOf(' ');
    return (sp > n / 2 ? cut.slice(0, sp) : cut).replace(/[ ,;:-]+(and|or|of|the)?$/, '') + '…';
  };
  const fmt = NumFmt.kyr;  // (numfmt.js, loaded first by lineages.html)
  const ago = (k) => NumFmt.ago(k);  // a date (numfmt.js, PW-1429)
  // how a people came to know a tech (the colours of the first tab and of the globe's 'technology' layer)
  const HOW_COL = { invented: '#ffd27a', contact: '#7fb0ff', kit: '#c79bff', inherited: '#8fa0b4', tamed: '#6bd6a0', shared: '#6bd6d0' };
  const howCol = (how) => HOW_COL[how] || (String(how).startsWith('with') ? '#6bd6a0' : '#aaa');
  const HOW_TEXT = { invented: 'invented', contact: 'by contact', kit: 'brought along (kit)', inherited: 'inherited at the split', tamed: 'by taming', shared: 'shared with its people' };
  const howText = (how) => HOW_TEXT[how] || how;
  const TRACK_COL = { communication: '#7cc4ff', fire: '#ff9d6b', tools: '#c9b08a', food: '#9fd18b', shelter: '#e3c26b', travel: '#6bd6d0', social: '#ff8fc8', arcane: '#c79bff' };
  const trackCol = (id) => TRACK_COL[id] || '#aab4c3';
  const ERAS = ['stone age', 'bronze age', 'classical', 'medieval', 'renaissance', 'industrial'];
  const VIEWS = [['tree', 'Tree'], ['timeline', 'Timeline'], ['map', 'Map'], ['inventory', 'Inventory'], ['cascade', 'Cascade'], ['table', 'Table'], ['spread', 'Spread']];
  const FOOT = {
    tree: `Columns: prerequisite depth inside each era (eras left to right, an era starts after the last column of the one before). Lanes: the tracks.
      A box shows the tech's earliest real-world date (or, as seen by a people, when and how it came to them); the small bar, bottom right, the share of living peoples that know it now. ✦ fantasy.
      Hover a tech for its chain and its real-world source; click it for who has it.`,
    timeline: `One row per people, on a log time axis (left: the oldest line, right: the present). The faint bar is the people's own span; each dot a tech it came to, coloured by track,
      filled when invented, a ring when it came by contact or was shared within its people. <b>+N</b> at a row's start counts what it inherited at its split (or brought along).
      Pick a tech to see it spread: the lines join a giver to a taker.`,
    map: `The globe viewer's 'technology' layer on the run's own cells, at every moment the run stores (drag its timeline, or press its ▶ to play the spread).
      Each people's land is lit when it knows the tech by then; grey land is held by peoples that do not yet; dark land is empty. Stars mark inventions (and tamings, kits); arrows run from giver to taker,
      drawn on the ranges of the moment it happened (older than the run's first stored moment: on that moment's ranges). Click an event on the right to go to it.`,
    inventory: `One people's kit, by track, in tree order. A dashed chip has all its needs met: it waits on chance, its earliest date, or land its country lacks (said on hover).
      With a second people picked, a dot on each chip says who else has it (<span style="color:#9fd18b">●</span> both, <span style="color:#ff7b7b">●</span> only the compared people).`,
    cascade: `Each row a people that came to the tech, placed under the people it came from (depth-first: a cascade reads downwards). Time runs left to right on a log axis.
      A line drops at the giver's date and runs along the taker's row to the taker's date: its length is how long the tech waited at the border. Stars are roots: independent inventions, brought kits, tamings.`,
    table: `Peoples down (oldest first), techs across by track: a square per known tech in the colour of how it came. Drag the time slider: what was not yet known then is greyed.`,
    spread: `How fast one tech spread. The curve: at each century step of the settlement ledger, the share of the settled people (everyone in a village, town or city) whose people knew it by then
      (solid), and the share of the cells with a town (dashed). The table: each people that ever had a place, when it first knew the tech and how; "ready" is when it knew the tech's own needs,
      "in touch" when it first bordered a people who knew it, so a long wait after both is the border being slow. A "big" people holds 1% or more of the settled people now. Cultures: on the right.`,
  };
  const st = { view: (location.hash.split('/')[1] || 'tree'), tech: null, who: '', fant: true, picked: null,
    tl: { track: '', tech: '', sort: 'start', inh: false, gone: true }, inv: { who: null, vs: '', at: 0 },
    colour: 'how', sp: { tech: 'writing', by: 'people', docs: {} }, mapAgo: null, mapFirst: null, table: { at: 0, track: 'all', all: false } };
  if (!VIEWS.some(([v]) => v === st.view)) st.view = 'tree';
  let D = null, ROOT = null, mounted = '';

  // ---- the data, once per run ----
  function prep(result) {
    const tt = result.techtree;
    const pres = (result.present || {}).lines || {}, keep = new Set(Object.keys(tt.known));
    const lines = (result.lineages || []).map((l) => ({ ...l, name: l.name.split(' (')[0], full: l.name, parents: l.parents || [], leaf: !!l.leaf,
      in_tree: keep.has(l.id), population: (pres[l.id] || {}).population }));
    const d = { id: result.id, result, tt, techs: tt.techs, tracks: tt.tracks, known: tt.known, firsts: tt.firsts, goods: tt.goods_checked || {}, lines };
    d.TECH = Object.fromEntries(d.techs.map((t) => [t.id, t]));
    d.LINE = Object.fromEntries(lines.map((l) => [l.id, l]));
    d.TRACK = Object.fromEntries(d.tracks.map((k) => [k.id, k]));
    d.PEOPLES = lines.filter((l) => l.in_tree).sort((a, b) => startOf(b) - startOf(a));
    d.users = {};
    for (const t of d.techs) for (const n of t.needs) (d.users[n] ||= []).push(t.id);
    return d;
  }
  const startOf = (l) => l.started_kyr ?? l.ago_kyr ?? 0;
  const alive = (l) => l.leaf && l.ended_kyr == null;
  const short = (id) => D.LINE[id]?.name || id;
  const tname = (id) => (D.TECH[id]?.name || id).split(' (')[0];
  const sw = (id) => `<span class="sw" style="background:${D.LINE[id]?.color || '#888'}"></span>`;
  function closure(ids) {  // everything the techs need, all the way down
    const out = new Set(), todo = [...ids];
    while (todo.length) { const i = todo.pop(); if (!out.has(i)) { out.add(i); todo.push(...(D.TECH[i]?.needs || [])); } }
    return out;
  }
  const techOptions = (cur, note) => D.tracks.map((k) => `<optgroup label="${esc(k.name)}">${D.techs.filter((t) => t.track === k.id)
    .map((t) => `<option value="${t.id}" ${t.id === cur ? 'selected' : ''}>${esc(tname(t.id))}${note && !D.firsts[t.id] ? ' (nobody)' : ''}</option>`).join('')}</optgroup>`).join('');
  const peopleOptions = (cur) => D.PEOPLES.map((l) => `<option value="${l.id}" ${l.id === cur ? 'selected' : ''}>${l.group_of ? '· ' : ''}${esc(l.name)}${alive(l) ? '' : ' (gone)'} — ${Object.keys(D.known[l.id]).length}</option>`).join('');
  const events = (tid) => D.PEOPLES.map((l) => { const v = D.known[l.id][tid]; return v && { lid: l.id, k: v[0], how: v[1], from: v[2] }; }).filter(Boolean)
    .sort((a, b) => b.k - a.k || (a.how === 'invented' ? 0 : 1) - (b.how === 'invented' ? 0 : 1));  // (on a tie the inventor first, PW-1012)
  const legendHow = () => `<div class="key">${Object.keys(HOW_COL).map((h) => `<span><span class="sw" style="background:${HOW_COL[h]}"></span>${esc(howText(h))}</span>`).join('')}</div>`;
  const keyHow = () => Object.keys(HOW_COL).map((h) => `<span><span class="sw" style="background:${HOW_COL[h]}"></span>${esc(h)}</span>`).join('');

  // ---- the floating tip ----
  const tip = document.createElement('div');
  tip.className = 'tt-tip';
  document.body.appendChild(tip);
  function showTip(e, html) {
    tip.innerHTML = html; tip.style.display = 'block';
    const r = tip.getBoundingClientRect();
    let x = e.clientX + 14, y = e.clientY + 12;
    if (x + r.width > innerWidth - 8) x = e.clientX - r.width - 14;
    if (y + r.height > innerHeight - 8) y = Math.max(8, innerHeight - r.height - 8);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  const hideTip = () => { tip.style.display = 'none'; };
  function techTip(id, extra = '') {  // (the real-world source at the bottom: where and when it happened on Earth)
    const t = D.TECH[id], f = D.firsts[id];
    const land = [...t.env, ...(t.env_any.length ? ['one of ' + t.env_any.join(' / ')] : [])].join(', ');
    return `<b>${esc(t.name)}</b><div class="muted">${esc(D.TRACK[t.track]?.name || t.track)} · ${esc(t.era)}${t.fantasy ? ' · fantasy' : ''}${t.sea ? ' · sea peoples\' branch' : ''}${t.state ? ' · needs towns of its own' : ''}</div>
      <div>needs: ${t.needs.length ? t.needs.map((n) => esc(tname(n))).join(', ') : '<span class="muted">nothing</span>'}</div>
      ${land ? `<div>land: ${esc(land)}</div>` : ''}
      <div>earliest ${t.earliest_kyr ?? '?'} kyr${t.elder_kyr ? ` (elder kinds ${t.elder_kyr})` : ''}</div>
      <div>first: ${f ? `${sw(f.line)}${esc(short(f.line))}, ${ago(f.ago_kyr)} (${esc(f.how)})` : '<span class="muted">nobody</span>'}</div>
      ${extra}<div class="muted src">${esc(t.source)}</div>`;
  }
  // drag to pan (the tree): one set of window listeners for the page's life
  let drag = null;
  addEventListener('mousemove', (e) => { if (drag) { drag.w.scrollLeft = drag.x - (e.clientX - drag.cx); drag.w.scrollTop = drag.y - (e.clientY - drag.cy); } });
  addEventListener('mouseup', () => { if (drag) { drag.w.classList.remove('panning'); drag = null; } });
  addEventListener('resize', () => { if (ROOT?.isConnected && ROOT.classList.contains('on') && ['timeline', 'cascade'].includes(st.view)) update(); });

  function setView(v, tech) {
    st.view = v;
    if (tech) st.tech = tech;
    history.replaceState(null, '', `${location.search}#tech/${v}`);
    window.TechTab.draw(ROOT, D.result);
  }

  // ---- 1. the tree (Civilization style) ----
  const CW = 190, BW = 160, BH = 30, RH = 38, TOP = 34, LEFT = 120;
  function treeLayout() {
    const techs = D.techs.filter((t) => st.fant || !t.fantasy), ids = new Set(techs.map((t) => t.id));
    const col = {}; let start = 0; const eraSpan = [];
    for (const e of ERAS) {
      if (!techs.some((t) => t.era === e)) continue;
      let mx = start;
      for (const t of techs) if (t.era === e) {  // (the techs come in prerequisite order)
        col[t.id] = Math.max(start, ...t.needs.filter((n) => ids.has(n)).map((n) => col[n] + 1));
        mx = Math.max(mx, col[t.id]);
      }
      eraSpan.push([e, start, mx]); start = mx + 1;
    }
    // lanes: within a track, the sub-row of its first same-track prerequisite (chains stay straight), else the first free one
    const rows = {}, laneRows = {};
    for (const k of D.tracks) {
      const these = techs.filter((t) => t.track === k.id).sort((a, b) => col[a.id] - col[b.id]);
      const used = [];
      for (const t of these) {
        const pre = t.needs.find((n) => D.TECH[n]?.track === k.id && rows[n] != null);
        let r = pre != null && !(used[rows[pre]]?.has(col[t.id])) ? rows[pre] : 0;
        if (pre == null || used[r]?.has(col[t.id])) { r = 0; while (used[r]?.has(col[t.id])) r++; }
        (used[r] ||= new Set()).add(col[t.id]); rows[t.id] = r;
      }
      laneRows[k.id] = Math.max(1, used.length);
    }
    let y = TOP; const laneY = {};
    for (const k of D.tracks) { laneY[k.id] = y; y += laneRows[k.id] * RH + 14; }
    const pos = {};
    for (const t of techs) pos[t.id] = [LEFT + col[t.id] * CW + 12, laneY[t.track] + rows[t.id] * RH + 6];
    return { techs, ids, pos, eraSpan, laneY, laneRows, W: LEFT + start * CW + 20, H: y };
  }
  function treeMount(bar, main) {
    bar.innerHTML = `<span class="muted">as seen by</span><select id="tt-who"><option value="">nobody (the whole tree)</option>${peopleOptions(st.who)}</select>
      <label class="muted"><input type="checkbox" id="tt-fant" ${st.fant ? 'checked' : ''}> fantasy techs</label>
      <span class="key"><span><span class="sw" style="background:#223047;border:1px solid #4a5b78"></span>known</span>
        <span><span class="sw" style="border:1px dashed #e3c26b"></span>could come next (all needs known)</span>
        <span><span class="sw" style="background:#e3c26b"></span>needs (upstream)</span><span><span class="sw" style="background:#7cc4ff"></span>leads to</span></span>
      <span class="muted">· hover a tech for its chain, click for who has it · drag to pan</span>`;
    main.innerHTML = '<div class="tt-split"><div class="tt-scroll tt-tree" id="tt-wrap"><svg id="tt-svg"></svg></div><div class="tt-side" id="tt-side"></div></div>';
    $('tt-who').onchange = (e) => { st.who = e.target.value; update(); };
    $('tt-fant').onchange = (e) => { st.fant = e.target.checked; update(); };
    const w = $('tt-wrap');
    w.addEventListener('scroll', treeFixLanes);
    w.addEventListener('mousedown', (e) => { if (e.target.closest('.node')) return; drag = { w, x: w.scrollLeft, y: w.scrollTop, cx: e.clientX, cy: e.clientY }; w.classList.add('panning'); });
  }
  function treeDraw() {
    const { techs, ids, pos, eraSpan, laneY, laneRows, W, H } = treeLayout();
    const kn = st.who ? D.known[st.who] : null;
    const nowKnow = {}; for (const l of D.PEOPLES) if (alive(l)) for (const t in D.known[l.id]) nowKnow[t] = (nowKnow[t] || 0) + 1;
    const nAlive = Math.max(1, D.PEOPLES.filter(alive).length);
    let s = '<g class="era">';
    eraSpan.forEach(([e, a, b], i) => {
      const x = LEFT + a * CW, w = (b - a + 1) * CW;
      s += `<rect x="${x}" y="0" width="${w}" height="${H}" fill="${i % 2 ? '#111821' : '#0e1218'}"/><text x="${x + 10}" y="20">${esc(e)}</text>`;
    });
    s += '</g>';
    for (const k of D.tracks) s += `<rect x="0" y="${laneY[k.id] - 4}" width="${W}" height="${laneRows[k.id] * RH + 6}" fill="${trackCol(k.id)}" opacity=".035"/>`;
    s += '<g>';
    for (const t of techs) for (const n of t.needs) if (ids.has(n)) {
      const [x1, y1] = pos[n], [x2, y2] = pos[t.id];
      const a = x1 + BW, b = y1 + BH / 2, c = x2, d = y2 + BH / 2, m = (a + c) / 2;
      s += `<path class="e" data-a="${n}" data-b="${t.id}" d="M${a},${b} C${m},${b} ${m},${d} ${c},${d}"/>`;
    }
    s += '</g>';
    for (const t of techs) {
      const [x, y] = pos[t.id], v = kn?.[t.id];
      const front = kn && !v && t.needs.every((n) => kn[n]);
      const cls = ['node', v ? 'known' : '', front ? 'frontier' : '', kn && !v && !front ? 'dim' : ''].join(' ');
      const share = (nowKnow[t.id] || 0) / nAlive;
      s += `<g class="${cls}" data-id="${t.id}" transform="translate(${x},${y})"><rect class="bg" width="${BW}" height="${BH}" rx="4"/>
        <rect width="4" height="${BH}" rx="2" fill="${trackCol(t.track)}"/>
        <title>${esc(tname(t.id))}</title><text x="10" y="13">${esc(clipWords(tname(t.id), t.fantasy ? 24 : 26))}${t.fantasy ? ' ✦' : ''}</text>
        <text class="when" x="10" y="25">${v ? `${ago(v[0])} · ${esc(v[1])}` : `from ${t.earliest_kyr != null ? fmt(t.earliest_kyr) : '?'}`}</text>
        <rect x="${BW - 26}" y="${BH - 7}" width="22" height="3" fill="#2a3446"/><rect x="${BW - 26}" y="${BH - 7}" width="${22 * share}" height="3" fill="${trackCol(t.track)}"/></g>`;
    }
    let lab = `<rect width="${LEFT}" height="${H}" fill="#0e1218" opacity=".92"/>`;  // (the lane names stay on the left)
    for (const k of D.tracks) lab += `<rect x="0" y="${laneY[k.id] - 4}" width="4" height="${laneRows[k.id] * RH + 6}" fill="${trackCol(k.id)}"/><text x="10" y="${laneY[k.id] + 16}" style="font-weight:600">${esc(k.name.split(' and ')[0])}</text>
      <text x="10" y="${laneY[k.id] + 30}" style="fill:#8b97a8;font-size:10px">${techs.filter((t) => t.track === k.id).length} techs</text>`;
    const svg = $('tt-svg'); svg.setAttribute('width', W); svg.setAttribute('height', H);
    svg.innerHTML = s + `<g id="tt-lanefix">${lab}</g>`;
    treeFixLanes();
    for (const g of svg.querySelectorAll('.node')) {
      const id = g.dataset.id;
      g.onmouseenter = (e) => { treeHl(id); showTip(e, techTip(id, kn ? `<div>${esc(short(st.who))}: ${kn[id] ? `${ago(kn[id][0])}, ${esc(howText(kn[id][1]))}${kn[id][2] ? ' from ' + esc(short(kn[id][2])) : ''}` : 'not known'}</div>` : '')); };
      g.onmousemove = (e) => showTip(e, tip.innerHTML);
      g.onmouseleave = () => { treeHl(st.picked); hideTip(); };
      g.onclick = () => { st.picked = id; treeSide(); treeHl(id); };
    }
    treeHl(st.picked); treeSide();
  }
  function treeFixLanes() { const g = $('tt-lanefix'); if (g) g.setAttribute('transform', `translate(${$('tt-wrap').scrollLeft},0)`); }
  function treeHl(id) {
    const up = id ? closure([id]) : new Set(), down = new Set();
    if (id) { const todo = [id]; while (todo.length) { const i = todo.pop(); for (const u of D.users[i] || []) if (!down.has(u)) { down.add(u); todo.push(u); } } }
    for (const p of $('tt-svg').querySelectorAll('path.e')) {
      const a = p.dataset.a, b = p.dataset.b;
      p.classList.toggle('up', !!id && up.has(a) && up.has(b));
      p.classList.toggle('down', !!id && down.has(b) && (a === id || down.has(a)));
      p.classList.toggle('faded', !!id && !p.classList.contains('up') && !p.classList.contains('down'));
    }
    for (const g of $('tt-svg').querySelectorAll('.node')) g.classList.toggle('hl', g.dataset.id === id);
  }
  function treeSide() {
    const el = $('tt-side'), id = st.picked;
    if (!id || !D.TECH[id]) { el.innerHTML = '<p class="muted">Click a tech to see who knows it and how it came to them.</p>' + '<h3>How it came</h3>' + legendHow(); return; }
    const have = D.PEOPLES.filter((l) => D.known[l.id][id]).sort((a, b) => D.known[b.id][id][0] - D.known[a.id][id][0]);
    const lack = D.PEOPLES.filter((l) => alive(l) && !D.known[l.id][id]);
    el.innerHTML = `${techTip(id)}
      <div class="row" style="margin:6px 0"><button data-go="map">on the map</button><button data-go="cascade">its cascade</button></div>
      <h3>Known by ${have.length} of ${D.PEOPLES.length} (${have.filter(alive).length} living)</h3>
      <table class="t">${have.map((l) => { const v = D.known[l.id][id]; return `<tr><td>${sw(l.id)}${esc(l.name)}${alive(l) ? '' : ' <span class="muted">(gone)</span>'}</td><td class="n">${fmt(v[0])}</td><td><span class="sw" style="background:${howCol(v[1])}"></span>${esc(v[1])}${v[2] ? ' <span class="muted">from</span> ' + esc(short(v[2])) : ''}</td></tr>`; }).join('')}</table>
      <h3>Living peoples without it (${lack.length})</h3><div>${lack.map((l) => `<span style="white-space:nowrap;margin-right:8px">${sw(l.id)}${esc(l.name)}</span>`).join(' ') || '<span class="muted">none</span>'}</div>
      <h3>How it came</h3>${legendHow()}`;
    for (const b of el.querySelectorAll('[data-go]')) b.onclick = () => setView(b.dataset.go, id);
  }

  // ---- 2. the per-people timeline ----
  function logAxis(oldest, near) {  // kyr ago -> 0..1 (0 the oldest, 1 the present)
    const lo = Math.log10(near), hi = Math.log10(oldest);
    return (k) => 1 - (Math.log10(Math.max(k, near)) - lo) / (hi - lo);
  }
  function tlMount(bar, main) {
    const s = st.tl;
    bar.innerHTML = `<span class="muted">track</span><select id="tt-track"><option value="">all tracks</option>${D.tracks.map((k) => `<option value="${k.id}" ${k.id === s.track ? 'selected' : ''}>${esc(k.name)}</option>`).join('')}</select>
      <span class="muted">highlight a tech</span><select id="tt-tech"><option value="">none</option>${techOptions(s.tech)}</select>
      <span class="muted">sort</span><select id="tt-sort"><option value="start">by when the people began</option><option value="n">by techs known now</option><option value="lang">by language</option><option value="tree">as the family tree</option></select>
      <label class="muted"><input type="checkbox" id="tt-inh" ${s.inh ? 'checked' : ''}> show inherited (split) dots</label>
      <label class="muted"><input type="checkbox" id="tt-gone" ${s.gone ? 'checked' : ''}> lines gone by the present</label>
      <span class="key">${D.tracks.map((k) => `<span><span class="sw" style="background:${trackCol(k.id)};border-radius:5px"></span>${esc(k.name.split(' and ')[0])}</span>`).join('')}
      <span><svg width="12" height="12" style="display:inline"><circle cx="6" cy="6" r="4" fill="#ddd"/></svg>invented</span><span><svg width="12" height="12" style="display:inline"><circle cx="6" cy="6" r="3.5" fill="none" stroke="#ddd" stroke-width="1.5"/></svg>contact / shared</span></span>`;
    main.innerHTML = '<div class="tt-scroll" id="tt-tlm"><svg id="tt-axis" class="tt-axis"></svg><svg id="tt-svg"></svg></div>';
    $('tt-sort').value = s.sort;
    for (const [id, k] of [['tt-track', 'track'], ['tt-tech', 'tech'], ['tt-sort', 'sort']]) $(id).onchange = (e) => { s[k] = e.target.value; update(); };
    $('tt-inh').onchange = (e) => { s.inh = e.target.checked; update(); };
    $('tt-gone').onchange = (e) => { s.gone = e.target.checked; update(); };
  }
  const isInh = (h) => h === 'inherited' || h === 'kit';
  function tlOrder() {
    const s = st.tl, rows = D.PEOPLES.filter((l) => s.gone || alive(l));
    const n = (l) => Object.keys(D.known[l.id]).length;
    for (const l of rows) l._d = 0;
    if (s.sort === 'n') rows.sort((a, b) => n(b) - n(a));
    else if (s.sort === 'lang') rows.sort((a, b) => (D.known[b.id].language?.[0] ?? -1) - (D.known[a.id].language?.[0] ?? -1));
    else if (s.sort === 'tree') {  // depth-first from the roots, children oldest first
      const kids = {}; for (const l of rows) { const p = l.group_of || l.parents[0]; (kids[p] ||= []).push(l); }
      const ids = new Set(rows.map((l) => l.id)), out = [], seen = new Set();
      const walk = (l, d) => { if (seen.has(l.id)) return; seen.add(l.id); l._d = d; out.push(l); for (const c of (kids[l.id] || []).sort((a, b) => startOf(b) - startOf(a))) walk(c, d + 1); };
      for (const l of rows) if (!ids.has(l.group_of || l.parents[0])) walk(l, 0);
      for (const l of rows) walk(l, 0);
      return out;
    }
    return rows;
  }
  function tlDraw() {
    const s = st.tl, RH = 24, LAB = 190, TOPH = 26;
    const W = Math.max(900, $('tt-tlm').clientWidth - 4), X = (u) => LAB + u * (W - LAB - 20);
    const oldest = Math.max(1, ...D.PEOPLES.map(startOf)), ax = logAxis(oldest * 1.05, 0.05), x = (k) => X(ax(k));
    const ticks = [0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000].filter((k) => k <= oldest * 1.05);
    const rows = tlOrder(), H = rows.length * RH + 10;
    let a = '<g class="axis">';
    for (const k of ticks) a += `<line x1="${x(k)}" x2="${x(k)}" y1="18" y2="${TOPH}" stroke="#3a4658"/><text x="${x(k)}" y="13" text-anchor="middle">${fmt(k)}</text>`;
    a += '<text x="8" y="13">ago</text></g>';
    $('tt-axis').setAttribute('width', W); $('tt-axis').setAttribute('height', TOPH); $('tt-axis').innerHTML = a;
    let h = ticks.map((k) => `<line x1="${x(k)}" x2="${x(k)}" y1="0" y2="${H}" stroke="#1a2230"/>`).join('');
    const rowY = {}, tix = Object.fromEntries(D.tracks.map((k, i) => [k.id, i])), nt = D.tracks.length;
    rows.forEach((l, i) => {
      const y = i * RH; rowY[l.id] = y;
      const kn = D.known[l.id], s0 = startOf(l), e0 = l.ended_kyr ?? 0.05;
      h += `<g class="row"><rect class="bg" x="0" y="${y}" width="${W}" height="${RH}" fill="${i % 2 ? '#10161e' : 'transparent'}"/>
        <rect x="${x(s0)}" y="${y + 3}" width="${Math.max(2, x(e0) - x(s0))}" height="${RH - 6}" rx="3" fill="${l.color}" opacity=".13"/>
        <text x="${6 + 10 * (l._d || 0)}" y="${y + 16}">${l.group_of ? '↳ ' : ''}${esc(l.name)}${alive(l) ? '' : ' †'}</text>
        <rect x="${LAB - 14}" y="${y + 7}" width="9" height="9" rx="2" fill="${l.color}"/>`;
      const inh = Object.entries(kn).filter(([t, v]) => isInh(v[1]) && D.TECH[t] && (!s.track || D.TECH[t].track === s.track));
      if (inh.length) h += `<text x="${x(s0) - 3}" y="${y + 16}" text-anchor="end" style="fill:#8b97a8;font-size:10px">+${inh.length}</text>`;
      for (const [t, v] of Object.entries(kn)) {
        const tk = D.TECH[t]; if (!tk || (s.track && tk.track !== s.track)) continue;
        if (isInh(v[1]) && !s.inh) continue;
        const cy = y + 4 + (tix[tk.track] + 0.5) * (RH - 8) / nt, cx = x(v[0]), col = trackCol(tk.track);
        const hl = s.tech === t, dim = s.tech && !hl;
        const fill = v[1] === 'invented' || v[1] === 'tamed' || String(v[1]).startsWith('with');
        h += `<circle class="d" data-l="${l.id}" data-t="${t}" cx="${cx}" cy="${cy}" r="${hl ? 6 : 3.2}" fill="${fill ? col : '#0e1218'}" stroke="${col}" stroke-width="${fill ? 0 : 1.4}" opacity="${dim ? 0.18 : 1}"${hl ? ' style="stroke:#fff;stroke-width:1.5"' : ''}/>`;
      }
      h += '</g>';
    });
    if (s.tech) for (const l of rows) {  // giver -> taker for the picked tech
      const v = D.known[l.id][s.tech]; if (!v || !v[2] || rowY[v[2]] == null) continue;
      const y1 = rowY[v[2]] + RH / 2, y2 = rowY[l.id] + RH / 2, cx = x(v[0]);
      h += `<path d="M${cx},${y1} C${cx + 18},${y1} ${cx + 18},${y2} ${cx},${y2}" fill="none" stroke="${howCol(v[1])}" stroke-width="1.3" opacity=".8"/>`;
    }
    const svg = $('tt-svg'); svg.setAttribute('width', W); svg.setAttribute('height', H); svg.innerHTML = h;
    for (const c of svg.querySelectorAll('circle.d')) {
      c.onmouseenter = (e) => { const l = c.dataset.l, t = c.dataset.t, v = D.known[l][t];
        showTip(e, `${sw(l)}<b>${esc(short(l))}</b>: ${esc(tname(t))}, ${ago(v[0])}<div>${esc(howText(v[1]))}${v[2] ? ' from ' + sw(v[2]) + esc(short(v[2])) : ''}</div><hr style="border-color:#2a3446">${techTip(t)}`); };
      c.onmouseleave = hideTip;
      c.onclick = () => { s.tech = s.tech === c.dataset.t ? '' : c.dataset.t; $('tt-tech').value = s.tech; update(); };
    }
  }

  // ---- 3. on the map: the globe viewer embedded, its 'technology' layer ----
  let frame = null;  // (the embedded globe: kept while the view and the run stay, it holds ~100 MB of layers)
  function mapMount(bar, main) {
    bar.innerHTML = `<span class="muted">tech</span><select id="tt-mtech">${techOptions(st.tech, true)}</select>
      <span class="muted">colour</span><select id="tt-colour"><option value="how">how it came</option><option value="when">how long known</option></select>
      <span class="muted" id="tt-mom">loading the globe…</span>
      <a id="tt-globe" target="_blank" title="The same layer in the full globe viewer">open on the globe</a>
      <span class="key" id="tt-mkey"></span>`;
    main.innerHTML = '<div class="tt-split" style="grid-template-columns:minmax(0,1fr) 360px"><div class="tt-map" id="tt-mapbox"></div><div class="tt-side" id="tt-side"></div></div>';
    $('tt-colour').value = st.colour;
    const src = `index.html?run=${encodeURIComponent(D.id)}&layer=technology&tech=${encodeURIComponent(st.tech)}&techcol=${st.colour}&embed=tech&peopleTracks=0&settlements=0&events=0&t=0`;
    frame = document.createElement('iframe');
    frame.title = 'The technology on the globe';
    frame.src = src;
    $('tt-mapbox').appendChild(frame);
    st.mapAgo = null;
    const send = () => frame.contentWindow?.postMessage({ techSet: { tech: st.tech, col: st.colour } }, location.origin);
    $('tt-mtech').onchange = (e) => {  // (a new tech: shown at the present, the globe turned to its first people)
      st.tech = e.target.value; send(); frame.contentWindow?.postMessage({ techAgo: 0 }, location.origin); mapFocusFirst(); update();
    };
    $('tt-colour').onchange = (e) => { st.colour = e.target.value; send(); update(); };
  }
  const mapFocusFirst = () => {  // (the globe turns to where the tech's first people had it)
    const f = D.firsts[st.tech];
    if (f) frame?.contentWindow?.postMessage({ techLine: f.line, techLineAgo: f.ago_kyr }, location.origin);
  };
  addEventListener('message', (e) => {  // (the globe says which moment it shows)
    if (e.origin !== location.origin || !frame || e.source !== frame.contentWindow || !e.data?.techFrame) return;
    if (st.mapAgo == null) mapFocusFirst();
    st.mapAgo = e.data.techFrame.ago; st.mapFirst = e.data.techFrame.first;
    if (st.view === 'map' && ROOT?.isConnected) mapDraw();
  });
  function mapDraw() {
    const at = st.mapAgo ?? 0, ev = events(st.tech);
    $('tt-globe').href = `index.html?run=${encodeURIComponent(D.id)}&layer=technology&tech=${encodeURIComponent(st.tech)}&techcol=${st.colour}&t=${-at}`;
    $('tt-mom').textContent = st.mapAgo == null ? 'loading the globe…' : `the globe shows ${ago(at)} (stored moments from ${ago(st.mapFirst)} to the present)`;
    $('tt-mkey').innerHTML = st.colour === 'how' ? keyHow() + '<span><span class="sw" style="background:#464e5a"></span>not yet</span><span><span class="sw" style="background:#2a2e28"></span>empty</span>'
      : '<span>new</span><span class="sw" style="width:80px;background:linear-gradient(90deg,#ffeca0,#d64828)"></span><span>long known</span><span><span class="sw" style="background:#464e5a"></span>not yet</span>';
    const n = ev.filter((e) => e.k >= at - 1e-9).length;
    $('tt-side').innerHTML = `${techTip(st.tech)}${D.firsts[st.tech] ? '' : '<p class="muted">Nobody in this run came to this tech.</p>'}
      <h3>${n} peoples know it ${at > 0 ? 'by ' + ago(at) : 'now'} · ${ev.length} ever</h3>
      <table class="t"><tr><th>when</th><th>people</th><th>how</th></tr>${ev.map((e) => `<tr data-k="${e.k}" data-l="${e.lid}" class="${e.k < at - 1e-9 ? 'future' : ''}" title="show ${esc(ago(e.k))} on the globe${st.mapFirst != null && e.k > st.mapFirst ? ' (before the first stored moment: the globe goes to that moment)' : ''}"><td class="n">${fmt(e.k)}</td><td>${sw(e.lid)}${esc(short(e.lid))}</td><td><span class="sw" style="background:${howCol(e.how)}"></span>${esc(e.how)}${e.from ? ' <span class="muted">from</span> ' + esc(short(e.from)) : ''}</td></tr>`).join('')}</table>`;
    for (const tr of $('tt-side').querySelectorAll('tr[data-k]')) tr.onclick = () => frame?.contentWindow?.postMessage({ techAgo: +tr.dataset.k, techLine: tr.dataset.l, techLineAgo: +tr.dataset.k }, location.origin);
  }

  // ---- 4. what a people has (inventory) ----
  const kit = (lid, at) => { const out = {}; for (const [t, v] of Object.entries(D.known[lid] || {})) if (v[0] >= at) out[t] = v; return out; };
  function why(t, kn, lid) {  // why a tech is not known yet
    const need = t.needs.filter((n) => !kn[n]);
    if (need.length) return `waits on ${need.map((n) => esc(tname(n))).join(', ')}`;
    const g = D.goods[lid];
    if (g) {
      const lack = t.env.filter((e) => !g.includes(e));
      if (lack.length) return `all needs known; its country lacks ${lack.join(', ')}`;
      if (t.env_any.length && !t.env_any.some((e) => g.includes(e))) return `all needs known; its country has none of ${t.env_any.join(' / ')}`;
    }
    return `all needs known${t.earliest_kyr != null ? `; not before ${ago(t.earliest_kyr)}` : ''}; waits on invention or a neighbour`;
  }
  function invMount(bar) {
    const s = st.inv;
    if (!s.who || !D.LINE[s.who]) s.who = D.LINE.human?.in_tree ? 'human' : [...D.PEOPLES].filter(alive).sort((a, b) => Object.keys(D.known[b.id]).length - Object.keys(D.known[a.id]).length)[0]?.id;
    bar.innerHTML = `<span class="muted">people</span><select id="tt-iwho">${peopleOptions(s.who)}</select>
      <span class="muted">compare with</span><select id="tt-ivs"><option value="">nobody</option>${peopleOptions(s.vs)}</select>
      <span class="muted">as at</span><select id="tt-iat">${[0, 1, 3, 6, 12, 25, 50, 100, 300, 1000].map((k) => `<option value="${k}" ${k === s.at ? 'selected' : ''}>${k ? ago(k) : 'the present'}</option>`).join('')}</select>
      <label class="muted"><input type="checkbox" id="tt-ifant" ${st.fant ? 'checked' : ''}> fantasy techs</label>
      <span class="key"><span><span class="sw" style="background:#1f2a3a;border-left:3px solid #ffd27a"></span>known (edge: how it came)</span><span><span class="sw" style="border:1px dashed #e3c26b"></span>could come next</span><span><span class="sw" style="background:#141a22;border:1px solid #2a3446"></span>out of reach</span>
      <span>hover: <span style="color:#e3c26b">needs</span> · <span style="color:#7cc4ff">leads to</span></span></span>`;
    $('tt-iwho').onchange = (e) => { s.who = e.target.value; update(); };
    $('tt-ivs').onchange = (e) => { s.vs = e.target.value; update(); };
    $('tt-iat').onchange = (e) => { s.at = +e.target.value; update(); };
    $('tt-ifant').onchange = (e) => { st.fant = e.target.checked; update(); };
  }
  function invDraw(main) {
    const s = st.inv, l = D.LINE[s.who], kn = kit(s.who, s.at), other = s.vs ? kit(s.vs, s.at) : null;
    const techs = D.techs.filter((t) => st.fant || !t.fantasy);
    const vals = Object.values(kn), cnt = (f) => vals.filter(f).length;
    const eraTop = ERAS.filter((e) => techs.some((t) => t.era === e && kn[t.id])).pop() || '—';
    const front = techs.filter((t) => !kn[t.id] && t.needs.every((n) => kn[n]));
    const lg = kn.language;
    let h = `<div class="tt-pad" id="tt-inv"><div class="people">${sw(s.who)}<span class="big">${esc(l.full)}</span><span class="muted">${esc(l.origin)}${l.group_of ? ' of ' + esc(short(l.group_of)) : l.parents.length ? ' from ' + l.parents.map((p) => esc(short(p))).join(' + ') : ''} · began ${ago(startOf(l))}${l.ended_kyr != null ? ', gone ' + ago(l.ended_kyr) : ''}${l.population ? ' · ' + (l.population / 1e6).toFixed(1) + ' M people now' : ''}</span></div>
      <div class="kpi"><div><b>${vals.length}</b><span>of ${techs.length} techs</span></div><div><b>${esc(eraTop)}</b><span>furthest era reached</span></div>
      <div><b>${cnt((v) => v[1] === 'invented')}</b><span>invented itself</span></div><div><b>${cnt((v) => v[1] === 'contact')}</b><span>by contact</span></div>
      <div><b>${cnt((v) => v[1] === 'inherited' || v[1] === 'kit')}</b><span>inherited or brought</span></div><div><b>${cnt((v) => v[1] === 'shared')}</b><span>shared within its people</span></div>
      <div><b>${front.length}</b><span>could come next</span></div><div><b>${lg ? fmt(lg[0]) : 'none'}</b><span>language${lg ? ' (' + esc(lg[1]) + ')' : ''}</span></div>
      ${other ? `<div><b>${Object.keys(kn).filter((t) => !other[t]).length} / ${Object.keys(other).filter((t) => !kn[t]).length}</b><span>only ${esc(l.name)} / only ${esc(short(s.vs))}</span></div>` : ''}</div><div class="grid">`;
    for (const k of D.tracks) {
      const tt = techs.filter((t) => t.track === k.id); if (!tt.length) continue;
      h += `<div class="card"><h3><span class="sw" style="background:${trackCol(k.id)}"></span>${esc(k.name)}<span class="muted">${tt.filter((t) => kn[t.id]).length} / ${tt.length}</span></h3><div class="chips">`;
      for (const t of tt) {
        const v = kn[t.id], f = !v && t.needs.every((n) => kn[n]);
        const dot = other ? (v && other[t.id] ? '#9fd18b' : !v && other[t.id] ? '#ff7b7b' : null) : null;
        h += `<span class="chip ${v ? 'k' : f ? 'f' : ''}" data-id="${t.id}" style="border-left-color:${v ? howCol(v[1]) : f ? '#e3c26b' : '#2a3446'}">${esc(tname(t.id))}${t.fantasy ? ' ✦' : ''}${v ? `<span class="w">${fmt(v[0])}</span>` : ''}${dot ? `<span class="vs" style="background:${dot}"></span>` : ''}</span>`;
      }
      h += '</div></div>';
    }
    main.innerHTML = h + '</div></div>';
    const box = $('tt-inv');
    for (const c of box.querySelectorAll('.chip')) {
      const id = c.dataset.id;
      c.onmouseenter = (e) => {
        const need = closure([id]); need.delete(id); const lead = new Set(D.users[id] || []);
        for (const o of box.querySelectorAll('.chip')) { o.classList.toggle('need', need.has(o.dataset.id)); o.classList.toggle('lead', lead.has(o.dataset.id)); o.classList.toggle('me', o.dataset.id === id); }
        const v = kn[id], ov = other?.[id];
        showTip(e, techTip(id, `<div style="margin-top:4px"><b>${esc(l.name)}</b>: ${v ? `since ${ago(v[0])}, ${esc(howText(v[1]))}${v[2] ? ' from ' + esc(short(v[2])) : ''}` : 'not known: ' + why(D.TECH[id], kn, s.who)}</div>
          ${other ? `<div><b>${esc(short(s.vs))}</b>: ${ov ? `since ${ago(ov[0])}, ${esc(howText(ov[1]))}` : 'not known'}</div>` : ''}`));
      };
      c.onmouseleave = () => { for (const o of box.querySelectorAll('.chip')) o.classList.remove('need', 'lead', 'me'); hideTip(); };
    }
  }

  // ---- 5. one tech's cascade: its transmission tree, time left to right; a row per people, under whoever passed it on ----
  function casMount(bar, main) {
    bar.innerHTML = `<span class="muted">tech</span><select id="tt-ctech">${techOptions(st.tech, true)}</select><span class="key">${keyHow()}<span>★ a root: invented, brought or tamed</span></span>`;
    main.innerHTML = '<div class="tt-split" style="grid-template-columns:minmax(0,1fr) 330px"><div class="tt-scroll" id="tt-pane"><svg id="tt-axis" class="tt-axis"></svg><svg id="tt-svg"></svg></div><div class="tt-side" id="tt-side"></div></div>';
    $('tt-ctech').onchange = (e) => { st.tech = e.target.value; update(); };
  }
  function casDraw() {
    const recs = events(st.tech);
    const by = Object.fromEntries(recs.map((r) => [r.lid, r])), kids = {}, roots = [];
    for (const r of recs) { if (r.from && by[r.from]) (kids[r.from] ||= []).push(r); else roots.push(r); }
    const rows = [], seen = new Set();
    const walk = (r, d) => { if (seen.has(r.lid)) return; seen.add(r.lid); r.d = d; rows.push(r); for (const c of (kids[r.lid] || []).sort((a, b) => b.k - a.k)) walk(c, d + 1); };
    for (const r of roots) walk(r, 0);
    for (const r of recs) walk(r, 0);
    const W = Math.max(860, $('tt-pane').clientWidth - 4), LAB = 200, RH = 19, TOPH = 24, H = rows.length * RH + 16;
    const oldest = Math.max(...recs.map((r) => r.k), 0.2), newest = Math.min(...recs.map((r) => r.k), oldest / 2);
    const lo = Math.log10(Math.max(newest * 0.7, 0.05)), hi = Math.log10(oldest * 1.15);
    const x = (k) => LAB + (1 - (Math.log10(Math.max(k, 0.05)) - lo) / (hi - lo)) * (W - LAB - 30);
    const ticks = [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000].filter((k) => Math.log10(k) >= lo && Math.log10(k) <= hi);
    $('tt-axis').setAttribute('width', W); $('tt-axis').setAttribute('height', TOPH);
    $('tt-axis').innerHTML = `<g class="axis">${ticks.map((k) => `<line x1="${x(k)}" x2="${x(k)}" y1="17" y2="24" stroke="#3a4658"/><text x="${x(k)}" y="13" text-anchor="middle">${fmt(k)}</text>`).join('')}<text x="8" y="13">${esc(tname(st.tech))}: ago</text></g>`;
    let s = ticks.map((k) => `<line x1="${x(k)}" x2="${x(k)}" y1="0" y2="${H}" stroke="#1a2230"/>`).join('');
    const Y = {}; rows.forEach((r, i) => { Y[r.lid] = 8 + i * RH + RH / 2; });
    rows.forEach((r, i) => { if (r.d === 0) s += `<rect x="0" y="${8 + i * RH}" width="${W}" height="1" fill="#2a3446"/>`; });
    for (const r of rows) if (r.from && by[r.from]) {  // (it drops at the giver's time and runs along the taker's row: the run is the wait)
      const p = by[r.from];
      s += `<path d="M${x(p.k)},${Y[p.lid]} V${Y[r.lid]} H${x(r.k)}" fill="none" stroke="${howCol(r.how)}" stroke-width="1.4" opacity=".75"/>`;
    }
    for (const r of rows) {
      const cx = x(r.k), y = Y[r.lid], root = !(r.from && by[r.from]);
      s += `<g class="nd" data-l="${r.lid}"><text x="${8 + r.d * 9}" y="${y + 4}" style="${root ? 'font-weight:600' : ''}">${esc(short(r.lid))}</text>
        <rect x="${LAB - 16}" y="${y - 5}" width="10" height="10" rx="2" fill="${D.LINE[r.lid].color}"/>
        ${root ? `<path transform="translate(${cx},${y})" d="M0,-7 L2,-2.3 L7,-2.3 L3,1.2 L4.6,6.2 L0,3.2 L-4.6,6.2 L-3,1.2 L-7,-2.3 L-2,-2.3 z" fill="${howCol(r.how)}"/>` : `<circle cx="${cx}" cy="${y}" r="4" fill="${howCol(r.how)}"/>`}</g>`;
    }
    const svg = $('tt-svg'); svg.setAttribute('width', W); svg.setAttribute('height', H); svg.innerHTML = s;
    for (const g of svg.querySelectorAll('.nd')) {
      g.onmouseenter = (e) => { const r = by[g.dataset.l], p = r.from && by[r.from];
        showTip(e, `${sw(r.lid)}<b>${esc(short(r.lid))}</b>: ${ago(r.k)}, ${esc(howText(r.how))}${r.from ? ` from ${sw(r.from)}${esc(short(r.from))}` : ''}${p ? `<div class="muted">waited ${fmt(Math.max(p.k - r.k, 0.001))} after its giver had it</div>` : ''}${(kids[r.lid] || []).length ? `<div>passed it on to ${kids[r.lid].length}</div>` : ''}`); };
      g.onmouseleave = hideTip;
    }
    const waits = rows.filter((r) => r.from && by[r.from] && r.how === 'contact').map((r) => by[r.from].k - r.k).sort((a, b) => a - b);
    const med = waits.length ? waits[waits.length >> 1] : null;
    const top = Object.entries(kids).map(([k, v]) => [k, v.length]).sort((a, b) => b[1] - a[1]).slice(0, 6);
    const cnt = {}; for (const r of recs) cnt[r.how] = (cnt[r.how] || 0) + 1;
    $('tt-side').innerHTML = `${techTip(st.tech)}${recs.length ? '' : '<p class="muted">Nobody in this run came to this tech.</p>'}
      <h3>The spread</h3><div class="kpi"><div><b>${recs.length}</b><span>peoples ever</span></div><div><b>${roots.filter((r) => r.how === 'invented').length}</b><span>independent inventions</span></div><div><b>${med != null ? fmt(med) : '—'}</b><span>median wait by contact</span></div></div>
      <table class="t">${Object.entries(cnt).sort((a, b) => b[1] - a[1]).map(([h, n]) => `<tr><td><span class="sw" style="background:${howCol(h)}"></span>${esc(howText(h))}</td><td class="n">${n}</td></tr>`).join('')}</table>
      <h3>Passed it on most</h3><table class="t">${top.map(([k, n]) => `<tr><td>${sw(k)}${esc(short(k))}</td><td class="n">${n}</td></tr>`).join('') || '<tr><td class="muted">nobody</td></tr>'}</table>
      <div class="row" style="margin-top:8px"><button data-go="map">this tech on the map</button></div>`;
    $('tt-side').querySelector('[data-go]').onclick = () => setView('map');
  }

  // ---- 6. the table: every people against every tech (the tab's first view, PW-675 v0), and the firsts ----
  function tableMount(bar, main) {
    const s = st.table;
    const rows = D.lines.filter((l) => D.known[l.id] && (s.all || l.leaf || l.ended_kyr == null));
    const oldest = Math.max(1, ...rows.map(startOf));
    const lo = Math.log10(0.05), hi = Math.log10(oldest);  // (the slider on a log scale: 0 the present, 1000 the oldest line shown)
    s.toK = (v) => (v <= 0 ? 0 : 10 ** (lo + (v / 1000) * (hi - lo)));
    s.toV = (k) => (k <= 0.05 ? 0 : Math.round(1000 * (Math.log10(k) - lo) / (hi - lo)));
    bar.innerHTML = `<select id="tt-ttrack"><option value="all">all tracks</option>${D.tracks.map((k) => `<option value="${k.id}" ${k.id === s.track ? 'selected' : ''}>${esc(k.name)}</option>`).join('')}</select>
      <label class="muted"><input type="checkbox" id="tt-tall" ${s.all ? 'checked' : ''}> lines gone by the present too</label>
      <span class="muted">known at</span><input type="range" id="tt-tat" min="0" max="1000" value="${s.toV(s.at)}" style="width:320px">
      <b id="tt-tatlab">${s.at <= 0 ? 'the present' : ago(s.at)}</b>
      <span class="key">${keyHow()}</span>`;
    $('tt-ttrack').onchange = (e) => { s.track = e.target.value; update(); };
    $('tt-tall').onchange = (e) => { s.all = e.target.checked; mounted = ''; window.TechTab.draw(ROOT, D.result); };
    $('tt-tat').oninput = (e) => {  // (only the squares' opacity and the counts change: no redraw)
      s.at = s.toK(+e.target.value);
      $('tt-tatlab').textContent = s.at <= 0 ? 'the present' : ago(s.at);
      for (const tr of $('tt-mat').rows) {
        let n = 0;
        for (const q of tr.querySelectorAll('.tq')) { const on = +q.dataset.k >= s.at; q.style.opacity = on ? 1 : 0.12; n += on; }
        const c = tr.querySelector('.tn'); if (c) c.textContent = n;
      }
    };
    main.innerHTML = '<div class="tt-pad" id="tt-tab"></div>';
  }
  function tableDraw() {
    const s = st.table, cell = 12;
    const techs = D.techs.filter((t) => s.track === 'all' || t.track === s.track);
    const rows = D.lines.filter((l) => D.known[l.id] && (s.all || l.leaf || l.ended_kyr == null)).sort((a, b) => startOf(b) - startOf(a));
    let h = '<div style="overflow:auto;max-height:calc(100vh - 260px)"><table id="tt-mat" style="border-collapse:collapse"><tr><th></th>', lastTrack = null;
    for (const t of techs) {
      const edge = t.track !== lastTrack ? 'border-left:2px solid #3a4658;' : ''; lastTrack = t.track;
      const land = [...t.env, ...(t.env_any.length ? ['one of ' + t.env_any.join('/')] : [])].join(', ');
      h += `<th title="${esc(t.name)} (${esc(t.track)}; ${esc(t.era)}; earliest ${t.earliest_kyr ?? '?'} kyr${t.elder_kyr ? `, elder kinds ${t.elder_kyr}` : ''}; needs ${esc(t.needs.join(', ') || 'nothing')}${land ? `; land: ${esc(land)}` : ''})&#10;${esc(t.source)}"
        style="${edge}vertical-align:bottom;font-weight:normal;font-size:10px;padding:0 1px"><div style="writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;max-height:130px;overflow:hidden">${esc(tname(t.id))}</div></th>`;
    }
    h += '<th style="vertical-align:bottom">known</th><th style="vertical-align:bottom;text-align:left">language</th></tr>';
    for (const l of rows) {
      const kn = D.known[l.id];
      let n = 0;
      h += `<tr><td style="white-space:nowrap;font-size:12px;padding-right:6px">${l.group_of ? '<span class="muted">↳ </span>' : ''}${sw(l.id)}${esc(l.name)}${l.leaf ? '' : ' <span class="muted">(gone)</span>'}</td>`;
      lastTrack = null;
      for (const t of techs) {
        const edge = t.track !== lastTrack ? 'border-left:2px solid #3a4658;' : ''; lastTrack = t.track;
        const v = kn[t.id], on = v && v[0] >= s.at;
        if (on) n++;
        h += v ? `<td style="padding:1px;${edge}" title="${esc(l.name)}: ${esc(t.name)} since ${ago(v[0])} (${esc(v[1])}${v[2] ? ' from ' + esc(short(v[2])) : ''})"><div class="tq" data-k="${v[0]}" style="width:${cell}px;height:${cell}px;border-radius:2px;background:${howCol(v[1])};opacity:${on ? 1 : 0.12}"></div></td>`
          : `<td style="padding:1px;${edge}"><div style="width:${cell}px;height:${cell}px;border-radius:2px;border:1px solid #1f2836;box-sizing:border-box"></div></td>`;
      }
      const lg = kn.language;
      h += `<td class="n tn">${n}</td><td class="muted" style="white-space:nowrap;font-size:12px">${lg ? `${ago(lg[0])}, ${esc(lg[1])}${lg[2] ? ' from ' + esc(short(lg[2])) : ''}` : 'none'}</td></tr>`;
    }
    h += '</table></div>';
    h += `<h2>Firsts</h2><div class="cards">${D.tracks.filter((k) => s.track === 'all' || k.id === s.track).map((k) => `<div class="card"><b>${esc(k.name)}</b>
      <table class="t" style="font-size:12px">${D.techs.filter((t) => t.track === k.id).map((t) => { const f = D.firsts[t.id];
        return `<tr><td title="${esc(t.source)}">${esc(t.name)}</td><td style="white-space:nowrap">${f ? `${sw(f.line)}${esc(short(f.line))}` : '<span class="muted">nobody</span>'}</td><td class="n">${f ? fmt(f.ago_kyr) : ''}</td><td class="muted">${f ? esc(f.how) : ''}</td></tr>`; }).join('')}</table></div>`).join('')}</div>`;
    $('tt-tab').innerHTML = h;
  }

  // ---- 7. how fast a tech spread (lane 184): the share of settled people over time, and who had it when ----
  function spMount(bar, main) {
    if (!D.TECH[st.sp.tech]) st.sp.tech = st.tech;
    bar.innerHTML = `<span class="muted">tech</span><select id="tt-stech">${techOptions(st.sp.tech, true)}</select>
      <span class="muted">curve of</span><select id="tt-sby"><option value="people">settled people</option><option value="towns">cells with a town</option><option value="both">both</option></select>
      <button id="tt-sglobe" title="The same tech on the globe: each people's land lit from the moment it knew it">on the globe</button>`;
    main.innerHTML = '<div class="tt-split" style="grid-template-columns:minmax(0,1fr) 360px"><div class="tt-pad" id="tt-sp"></div><div class="tt-side" id="tt-side"></div></div>';
    $('tt-sby').value = st.sp.by;
    $('tt-stech').onchange = (e) => { st.sp.tech = e.target.value; update(); };
    $('tt-sby').onchange = (e) => { st.sp.by = e.target.value; update(); };
    $('tt-sglobe').onclick = () => setView('map', st.sp.tech);
  }
  const spGet = (tech) => {  // (one fetch per run and tech; a second draw while it is in flight waits for the same one)
    const k = `${D.id}|${tech}`;
    return st.sp.docs[k] ||= fetch(`../api/techspread?run=${encodeURIComponent(D.id)}&tech=${encodeURIComponent(tech)}`, { cache: 'no-store' })
      .then((r) => r.ok ? r.json() : r.text().then((t) => { let m = t; try { m = JSON.parse(t).error || t; } catch (e) {} return { error: `${r.status} ${String(m).slice(0, 200)}` }; }))
      .catch((e) => ({ error: e.message }))
      .then((d) => { if (d.error) delete st.sp.docs[k]; return d; });
  };
  function spDraw() {
    const tech = st.sp.tech, run = D.id;
    if ($('tt-sp')) $('tt-sp').innerHTML = `<p class="muted">Working out how ${esc(tname(tech))} spread…</p>`;
    spGet(tech).then((doc) => {
      if (st.view !== 'spread' || st.sp.tech !== tech || D.id !== run || !$('tt-sp')) return;  // (the pick moved on meanwhile)
      if (doc.error) { $('tt-sp').innerHTML = `<p class="err">Could not work out the spread: ${esc(doc.error)}</p>`; $('tt-side').innerHTML = ''; return; }
      spRender(doc);
    });
  }
  function spCurve(doc) {
    const s = doc.stats, A = doc.steps, W = Math.max(520, ($('tt-sp').clientWidth || 800) - 30), H = 230, L = 46, R = 14, T = 12, B = 30;
    const hi = Math.min(A[0], s.first_kyr != null ? s.first_kyr + Math.max(0.6, s.first_kyr * 0.25) : A[0]);
    const x = (k) => L + (1 - k / hi) * (W - L - R), y = (v) => T + (1 - v) * (H - T - B);
    const line = (vals) => A.map((a, i) => a <= hi + 1e-9 ? `${x(a).toFixed(1)},${y(vals[i]).toFixed(1)}` : null).filter(Boolean).join(' ');
    const step = hi > 8 ? 2 : hi > 4 ? 1 : hi > 1.6 ? 0.5 : 0.2, ticks = [];
    for (let k = 0; k <= hi + 1e-9; k += step) ticks.push(+k.toFixed(3));
    let g = ticks.map((k) => `<line x1="${x(k)}" x2="${x(k)}" y1="${T}" y2="${H - B}" stroke="#1a2230"/><text x="${x(k)}" y="${H - B + 14}" text-anchor="middle" font-size="10" fill="var(--muted)">${esc(k ? ago(k) : 'now')}</text>`).join('');
    g += [0, 0.25, 0.5, 0.75, 1].map((v) => `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="${v === 0.5 ? '#3a4658' : '#1a2230'}"/><text x="${L - 6}" y="${y(v) + 3}" text-anchor="end" font-size="10" fill="var(--muted)">${Math.round(v * 100)}%</text>`).join('');
    if (st.sp.by !== 'towns') g += `<polyline points="${line(doc.share_people)}" fill="none" stroke="var(--acc)" stroke-width="2"/>`;
    if (st.sp.by !== 'people') g += `<polyline points="${line(doc.share_towns)}" fill="none" stroke="#e3c26b" stroke-width="1.6" stroke-dasharray="5 3"/>`;
    for (const p of doc.peoples) if (p.ago != null && p.how === 'invented' && p.ago <= hi) {
      g += `<path transform="translate(${x(p.ago)},${y(0) - 8})" d="M0,-6 L1.8,-2 L6,-2 L2.6,1 L4,5.4 L0,2.8 L-4,5.4 L-2.6,1 L-6,-2 L-1.8,-2 z" fill="${HOW_COL.invented}"><title>${esc(p.name)} invented it ${esc(ago(p.ago))}</title></path>`;
    }
    return `<svg width="${W}" height="${H}" role="img" aria-label="share that knew ${esc(doc.tech_name)} over time">${g}</svg>
      <div class="key"><span><span class="sw" style="background:var(--acc)"></span>settled people</span><span><span class="sw" style="background:#e3c26b"></span>cells with a town (dashed)</span><span style="color:${HOW_COL.invented}">★ an invention</span></div>`;
  }
  function spRender(doc) {
    const s = doc.stats, f = s.first_kyr;
    const after = (a) => a == null ? 'not yet' : `${ago(a)} <span class="muted">(${fmt(Math.max(f - a, 0))} after)</span>`;
    const kpi = f == null ? `<p class="muted">Nobody in this run came to ${esc(doc.tech_name)}.</p>` : `<div class="kpi">
      <div><b>${esc(ago(f))}</b><span>first: ${esc(s.first_by.join(', '))}</span></div>
      <div><b>${s.inventions}</b><span>independent inventions</span></div>
      <div><b>${after(s.reach_kyr['0.5'])}</b><span>half the settled people</span></div>
      <div><b>${after(s.reach_kyr['0.9'])}</b><span>nine in ten</span></div>
      <div><b>${s.last_big ? `${esc(s.last_big.name)}, ${after(s.last_big.ago)}` : '—'}</b><span>last big people to get it</span></div>
      <div><b>${Math.round(s.share_now * 100)}%</b><span>of settled people know it now</span></div></div>
      ${s.big_never.length ? `<p>Big peoples that never had it: <b>${esc(s.big_never.join(', '))}</b>.</p>` : ''}`;
    const rows = doc.peoples.map((p) => {
      const start = p.ready != null && p.touch != null ? Math.min(p.ready, p.touch) : null;
      const wait = p.ago != null && p.how === 'contact' && start != null ? fmt(Math.max(start - p.ago, 0)) : '';
      return `<tr class="${p.ago == null ? 'future' : ''}"><td>${sw(p.id)}${esc(p.name)}${p.big ? ' <span class="muted">big</span>' : ''}</td>
        <td class="n">${p.ago != null ? esc(ago(p.ago)) : '<span class="muted">never</span>'}</td>
        <td>${p.how ? `<span class="sw" style="background:${howCol(p.how)}"></span>${esc(howText(p.how))}${p.from ? ' <span class="muted">from</span> ' + esc(p.from_name || short(p.from)) : ''}` : ''}</td>
        <td class="n">${p.ready != null ? esc(ago(p.ready)) : '<span class="muted">not ready</span>'}</td><td class="n">${p.touch != null ? esc(ago(p.touch)) : '—'}</td>
        <td class="n">${wait}</td><td class="n">${(p.share_now * 100).toFixed(1)}%</td></tr>`;
    }).join('');
    $('tt-sp').innerHTML = `<h3>How fast ${esc(doc.tech_name)} spread</h3>${kpi}${spCurve(doc)}
      <h3>Peoples (${doc.peoples.filter((p) => p.ago != null).length} of ${doc.peoples.length} with places ever knew it)</h3>
      <table class="t"><tr><th>people</th><th>first knew it</th><th>how</th><th>ready</th><th>in touch</th><th>waited at the border</th><th>settled people now</th></tr>${rows}</table>`;
    $('tt-side').innerHTML = `${techTip(st.sp.tech)}<h3>Cultures (${doc.cultures.length})</h3>
      <table class="t"><tr><th>when</th><th>culture</th><th>how</th></tr>${doc.cultures.map((c) => `<tr class="${c.alive ? '' : 'future'}"><td class="n">${esc(ago(c.ago))}</td>
        <td>${sw(c.people)}${esc(c.name)}</td><td>${esc(c.how === 'from its start' ? 'its people knew it when it began' : howText(c.how))}${c.from ? ' <span class="muted">from</span> ' + esc(short(c.from)) : ''}</td></tr>`).join('')}</table>
      <p class="muted">Greyed: a culture that has since ended.</p>`;
  }

  // ---- the frame of the tab ----
  const MOUNT = { tree: treeMount, timeline: tlMount, map: mapMount, inventory: invMount, cascade: casMount, table: tableMount, spread: spMount };
  const DRAW = { tree: treeDraw, timeline: tlDraw, map: mapDraw, inventory: () => invDraw($('tt-main')), cascade: casDraw, table: tableDraw, spread: spDraw };
  function update() { hideTip(); DRAW[st.view](); }
  window.TechTab = {
    get view() { return st.view; },
    draw(el, result) {
      ROOT = el;
      if (!D || D.result !== result) { D = prep(result); mounted = ''; }
      if (!st.tech || !D.TECH[st.tech]) st.tech = D.TECH.pottery && D.firsts.pottery ? 'pottery' : D.techs.find((t) => D.firsts[t.id])?.id || D.techs[0].id;
      if (st.who && !D.LINE[st.who]) st.who = '';
      const key = `${D.id}|${st.view}`;
      if (mounted !== key || !$('tt-main')) {  // (a redraw of the same view keeps it: the map's globe is not reloaded)
        frame = null;
        el.innerHTML = `<div class="tt-nav">${VIEWS.map(([v, n]) => `<button data-view="${v}" class="${v === st.view ? 'on' : ''}">${n}</button>`).join('')}
          <span style="flex:1"></span><span class="muted">run ${esc(D.id)} · ${esc(result.tree_name || '')} · ${D.techs.length} techs in ${D.tracks.length} tracks · ${D.PEOPLES.length} peoples · era cap ${esc(D.tt.era)} · ${esc(D.tt.mode)} mode</span></div>
          <div class="tt-bar" id="tt-bar"></div><div class="tt-main" id="tt-main"></div>`;
        for (const b of el.querySelectorAll('[data-view]')) b.onclick = () => setView(b.dataset.view);
        MOUNT[st.view]($('tt-bar'), $('tt-main'));
        mounted = key;
      }
      if ($('foot')) $('foot').innerHTML = FOOT[st.view];
      update();
    },
  };
})();
