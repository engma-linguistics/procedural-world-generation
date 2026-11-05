'use strict';
// The peoples workbench's Religion tab (PW-1358, PW-1311; the data: planet/lineages/gods.py, taboos.py, faithmap.py via /api/gods,
// /api/taboos, /api/faithmap). Four views of one run's faiths:
//   trees    a few small god trees: how one faith's gods split (copied into daughter cultures), fused and individuated over time
//   map      where each faith was at each stored moment (a time slider), its birthplace and the path of its centre
//   timeline a row per faith on a log time axis, schisms under their parent, like the Cultures tab
//   taboos   each culture's taboos by kind, and the catalogue with its sources
//   yours    the faiths Daniel writes in (PW-1430): add, edit, remove; saved in the run's authored.json (POST /api/authored), then
//            every view is fetched and drawn again with them, marked "yours". The gods mode (PW-1309) is picked in the tab's bar and
//            saved the same way. Every date is read with NumFmt.parseDate and shown with NumFmt.ago.
// A classic script: lineages.html calls ReligionTab.draw(el, result) with result = { id, ...run.meta } of the picked run.
(() => {
  const CSS = `
#tab-religion.on { display: grid; grid-template-rows: auto auto minmax(0, 1fr); padding: 0; overflow: hidden; }
#tab-religion .rl-nav { display: flex; gap: 2px; align-items: center; padding: 0 12px; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
#tab-religion .rl-nav button { border: 0; border-bottom: 2px solid transparent; border-radius: 0; background: none; padding: 6px 12px; color: var(--muted); }
#tab-religion .rl-nav button.on { color: var(--text); border-bottom-color: var(--acc); }
#tab-religion .rl-bar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; padding: 6px 12px; border-bottom: 1px solid var(--line); background: var(--panel); }
#tab-religion .rl-main { min-height: 0; overflow: auto; padding: 10px 12px; }
#tab-religion .rl-split { display: grid; grid-template-columns: minmax(0, 1fr) clamp(400px, 40vw, 620px); gap: 10px; min-height: 100%; align-items: start; }
#tab-religion .rl-side { border-left: 1px solid var(--line); padding-left: 10px; overflow: auto; min-width: 0; }
@media (max-width: 1100px) { #tab-religion .rl-split { grid-template-columns: minmax(0, 1fr); } #tab-religion .rl-side { order: -1; border-left: 0; padding-left: 0; border-bottom: 1px solid var(--line); padding-bottom: 10px; } }
#tab-religion .rl-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(560px, 1fr)); gap: 12px; }
#tab-religion .rl-cards.one { grid-template-columns: minmax(0, 1fr); }
#tab-religion .rl-card { border: 1px solid var(--line); border-radius: 6px; padding: 8px; background: var(--panel); overflow-x: auto; }
#tab-religion .rl-card h3 { margin: 0 0 4px; font-size: 13px; }
#tab-religion svg text { fill: var(--text); font-size: 11px; }
#tab-religion svg text.m { fill: var(--muted); font-size: 10px; }
#tab-religion .rl-mapbox { position: relative; width: 100%; }
#tab-religion .rl-mapbox img { width: 100%; display: block; image-rendering: pixelated; border-radius: 4px; }
#tab-religion .rl-mapbox svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
#tab-religion tr.sel td { background: var(--ctl-hi, #223047); }
#tab-religion tr[data-f] { cursor: pointer; }
#tab-religion .kind { display: inline-block; min-width: 120px; color: var(--muted); }
#tab-religion .rl-yours { font-size: 10px; color: var(--acc, #6fa8ff); border: 1px solid currentColor; border-radius: 3px; padding: 0 3px; margin-left: 4px; white-space: nowrap; }
#tab-religion .rl-form { display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; align-content: start; min-width: 0; }
#tab-religion .rl-form input:not([type]), #tab-religion .rl-form input[type=text], #tab-religion .rl-form select { min-width: 0; max-width: 100%; box-sizing: border-box; }
#tab-religion .rl-form label { display: grid; gap: 2px; }
#tab-religion .rl-form .row { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; }
#tab-religion .rl-pick { position: relative; cursor: crosshair; max-width: 560px; }
#tab-religion .rl-pick img { width: 100%; display: block; border-radius: 4px; }
#tab-religion .rl-pick svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
#tab-religion .ok { color: #6bd66b; } #tab-religion .no { color: #ff7b6b; } #tab-religion .err { color: #ff7b6b; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmt = NumFmt.kyr;
  const ago = (k) => NumFmt.ago(k);  // a date: '12,400 years ago', or 'year 1400' once the run's present is set (numfmt.js, PW-1429)
  const VIEWS = [['trees', 'God trees'], ['map', 'Map'], ['timeline', 'Timeline'], ['taboos', 'Taboos'], ['yours', 'Your faiths']];
  const MODES = [['faith_made', 'faith-made (gods exist while worshipped)'], ['belief_only', 'belief only (no gods are real)'], ['absolute', 'absolute (gods outlive their worshippers)']];
  const yours = (f) => (f && f.authored != null ? '<span class="rl-yours" title="a faith you wrote">✎ yours</span>' : '');
  const fname = (f) => esc(f?.name) + yours(f);
  const FOOT = {
    trees: `Each card is one faith's gods on a log time axis (left: older, right: now). A line is one god or spirit, coloured by how individuated it was then
      (grey: a spirit bound to a place; blue: a power; gold: a god; red: a person-god). A god copied into a daughter culture branches off its parent at the split;
      a god that fused into another ends in ×; one that faded ends in a bar. Pick any faith in the list above to draw its tree.`,
    map: `Where each faith was at a stored moment of the run: every cell held by a culture takes the colour of that culture's faith then
      (pale grey: peoples with no faith yet; dark grey: empty land). ✚ marks where a faith was founded; the thin line follows its centre over time.
      Drag the slider or press ▶. Click a faith on the right to follow it alone, with the path of its centre (a faith spread over several lands has a centre between them).`,
    timeline: `One row per faith on a log time axis, schisms (faiths that broke away) under the faith they broke from. The bar runs from its founding to its end;
      green dots: cultures it won by conversion; red dots: cultures it lost to another faith. "No followers left": the faith ended while its cultures lived on.`,
    yours: `Faiths you write. Each is founded under the same rules as the rest, at the first stored moment from its year on at which its founder
      is on the map and has gods (spirit ritual); after that its gods drift, fade, split and fuse like any. A missionary faith sends preachers: it wins
      neighbours whose faith is less organised and does not seek converts itself, over a century or two each (as early Christianity, Islam or Buddhism did);
      a faith that only spreads wins neighbours slowly, over a millennium or two, and only from temples; a closed one takes no converts. Wherever its
      cultures rule a state, they push it on their subjects: within a generation for a harsh ruler, hardly at all for a tolerant one (each culture's
      tolerance is on its taboos card). The result column says whether it took hold, how it spread, and why not. Saved with the run; nothing in the peoples history is re-run.`,
    taboos: `Each living culture's taboos by kind. Food taboos come from its herds, crops, neighbours and gods; the other kinds from its way of life, its techs
      and its gods' domains (the tags shown). Every rule names its source; the catalogue below lists the sources and how far each was read.`,
  };
  const st = { view: (location.hash.split('/')[1] || 'trees'), faith: null, frame: null, follow: null, culture: null, gone: false, playing: null };
  if (!VIEWS.some(([v]) => v === st.view)) st.view = 'trees';
  let D = null, mounted = '';

  function load(result, done) {  // (gods, taboos and cultures of the run, fetched once)
    if (D && D.id === result.id) { if (D.busy) D.waiters.push(done); else done(); return; }  // (a second draw while the first fetch is in flight waits for it)
    const id = result.id;
    D = { id, gods: null, taboos: null, authored: null, cultures: result.culturesDoc || null, busy: true, waiters: [done] };
    const get = (u) => fetch(u, { cache: 'no-store' }).then((r) => r.ok ? r.json() : r.text().then((t) => { let m = t; try { m = JSON.parse(t).error || t; } catch (e) {} return { error: `${r.status} ${String(m).slice(0, 200)}` }; })).catch((e) => ({ error: e.message }));
    Promise.all([get(`../api/gods?run=${encodeURIComponent(id)}`), get(`../api/taboos?run=${encodeURIComponent(id)}`),
      D.cultures ? Promise.resolve(D.cultures) : get(`../api/cultures?run=${encodeURIComponent(id)}`), get(`../api/authored?run=${encodeURIComponent(id)}`)])
      .then(([g, t, c, a]) => { if (D.id !== id) return; D.gods = g; D.taboos = t; D.cultures = c; D.authored = a && !a.error ? a : { faiths: [], gods_mode: null }; D.busy = false; prep(); const w = D.waiters; D.waiters = []; for (const f of w) f(); });
  }
  function prep() {
    const g = D.gods;
    if (!g || g.error || !g.faiths) return;
    D.F = g.faiths.list; D.B = g.beings;
    D.C = (D.cultures && D.cultures.cultures) || [];
    D.cname = (c) => D.C[c]?.name || `culture ${c}`;
    D.frames = g.frames || [];
    D.lost = {};
    for (const f of D.F) for (const e of f.events) if (e[3] != null) (D.lost[e[3]] = D.lost[e[3]] || []).push(e);
    // three small examples: living faiths with 5..30 gods, the most individuated first, of different peoples where possible
    const cand = D.F.filter((f) => f.ended_kyr == null && f.beings.length >= 5 && f.beings.length <= 30)
      .sort((a, b) => maxInd(b) - maxInd(a) || b.beings.length - a.beings.length);
    D.examples = []; const seen = new Set();
    for (const f of cand) if (!seen.has(f.origin_people) && D.examples.length < 3) { D.examples.push(f.id); seen.add(f.origin_people); }
    for (const f of cand) if (D.examples.length < 3 && !D.examples.includes(f.id)) D.examples.push(f.id);
    if (st.faith == null || !D.F[st.faith]) st.faith = D.examples[0] ?? D.F[0]?.id;
    if (st.frame == null || !D.frames.some((x) => x[0] === st.frame)) st.frame = D.frames.length ? D.frames[D.frames.length - 1][0] : 0;
  }
  const maxInd = (f) => Math.max(0, ...f.beings.map((i) => D.B[i].individuation));
  const indCol = (x) => (x < 0.3 ? '#8a94a3' : x < 0.5 ? '#6fa8ff' : x < 0.7 ? '#e3c26b' : '#ff7b6b');
  const faithOpts = (cur) => D.F.filter((f) => f.beings.length).sort((a, b) => b.beings.length - a.beings.length)
    .map((f) => `<option value="${f.id}" ${f.id === cur ? 'selected' : ''}>${f.authored != null ? '✎ ' : ''}${esc(f.name)} · ${f.beings.length} gods${f.ended_kyr != null ? ' (gone)' : ''}</option>`).join('');
  const sw = (c) => `<span class="sw" style="background:${c}"></span>`;
  const logX = (oldest, x0, x1) => { const lo = Math.log10(0.05), hi = Math.log10(Math.max(oldest, 0.1) * 1.05); x0 += 14;
    return (k) => x0 + (1 - (Math.log10(Math.max(k, 0.05)) - lo) / (hi - lo)) * (x1 - x0); };
  const TICKS = [0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000];

  // ---- 1. god trees ----
  function treeSvg(f, W = 560) {
    const ids = new Set(f.beings), B = D.B;
    const kids = {}, roots = [];
    for (const i of f.beings) { const p = B[i].parent; if (p != null && ids.has(p)) (kids[p] = kids[p] || []).push(i); else roots.push(i); }
    const order = [], depth = {};
    const walk = (i, d) => { order.push(i); depth[i] = d; (kids[i] || []).sort((a, b) => B[b].born_kyr - B[a].born_kyr).forEach((k) => walk(k, d + 1)); };
    roots.sort((a, b) => B[b].born_kyr - B[a].born_kyr).forEach((r) => walk(r, 0));
    const RH = 14, TOP = 18, LAB = 190, H = TOP + order.length * RH + 6;
    const oldest = Math.max(...f.beings.map((i) => B[i].born_kyr)), x = logX(oldest, 4, W - LAB - 8);
    const row = Object.fromEntries(order.map((i, k) => [i, TOP + k * RH + RH / 2]));
    let h = TICKS.filter((k) => k > 0.1 && k <= oldest * 1.05).map((k) => `<line x1="${x(k)}" x2="${x(k)}" y1="12" y2="${H}" stroke="#1f2836"/><text class="m" x="${x(k)}" y="10" text-anchor="middle">${fmt(k)}</text>`).join('')
      + `<line x1="${x(0)}" x2="${x(0)}" y1="12" y2="${H}" stroke="#3a4a63"/><text class="m" x="${x(0)}" y="10" text-anchor="end">now</text>`;
    for (const i of order) {
      const b = B[i], y = row[i], end = b.ended_kyr ?? 0.05;
      if (b.parent != null && row[b.parent] != null) h += `<path d="M${x(b.born_kyr)},${row[b.parent]} V${y}" stroke="#4a5b78" fill="none"/>`;
      const pts = (b.history || []).filter((p) => p[0] <= b.born_kyr + 1e-9 && p[0] >= end - 1e-9);
      const seg = [[b.born_kyr, pts[0]?.[1] ?? b.individuation], ...pts.map((p) => [p[0], p[1]]), [end, b.individuation]];
      for (let k = 0; k + 1 < seg.length; k++) {
        if (seg[k][0] <= seg[k + 1][0]) continue;
        h += `<line x1="${x(seg[k][0])}" x2="${x(seg[k + 1][0])}" y1="${y}" y2="${y}" stroke="${indCol(seg[k + 1][1])}" stroke-width="${b.high ? 4 : 2.5}"/>`;
      }
      if (b.status === 'merged') h += `<text x="${x(end) + 2}" y="${y + 4}" style="fill:#c88">×</text>`;
      else if (b.status === 'faded' || b.status === 'dormant') h += `<line x1="${x(end)}" x2="${x(end)}" y1="${y - 4}" y2="${y + 4}" stroke="#c88"/>`;
      const tip = `${b.label} (${b.individuation.toFixed(2)}${b.grants_spells ? ', grants spells' : ''}), ${b.how} ${ago(b.born_kyr)} in ${D.cname(b.culture)}; ${b.status}${b.ended_kyr != null ? ' ' + ago(b.ended_kyr) + (b.end ? ' (' + b.end + ')' : '') : ''}; domains ${b.top.map((t) => t[0] + ' ' + t[1]).join(', ')}`;
      h += `<g><title>${esc(tip)}</title><rect x="0" y="${y - RH / 2}" width="${W}" height="${RH}" fill="transparent"/>
        <text x="${W - LAB}" y="${y + 4}" style="${b.status !== 'living' ? 'opacity:.55' : ''}">${'· '.repeat(Math.min(depth[i], 4))}${esc(b.label)}</text></g>`;
    }
    return `<svg width="${W}" height="${H}">${h}</svg>`;
  }
  function treesMount(bar) {
    bar.innerHTML = `<span class="muted">faith</span><select id="rl-faith"><option value="">the three examples</option>${faithOpts(st.pick)}</select>
      <span class="key">${[['spirit', 0.1], ['power', 0.4], ['god', 0.6], ['person-god', 0.8]].map(([n, v]) => `<span>${sw(indCol(v))}${n}</span>`).join(' ')}</span>`;
    $('rl-faith').onchange = (e) => { st.pick = e.target.value === '' ? null : +e.target.value; update(); };
  }
  function treesDraw(main) {
    const list = st.pick != null ? [st.pick] : D.examples;
    if (!list.length) { main.innerHTML = '<p class="muted">No faith in this run has gods yet.</p>'; return; }
    main.innerHTML = `<div class="rl-cards${list.length === 1 ? ' one' : ''}">${list.map((id) => { const f = D.F[id];
      return `<div class="rl-card"><h3>${sw(f.color)}${fname(f)}</h3><div class="muted" style="margin-bottom:4px">${f.how === 'schism' ? 'broke away from ' + esc(D.F[f.parent]?.name) + ', ' : 'founded '}${ago(f.founded_kyr)};
        ${f.ended_kyr == null ? `${f.cultures_now.length} cultures of ${f.peoples_now.length} peoples now` : 'ended ' + ago(f.ended_kyr) + ' (' + esc(f.end) + ')'}; ${f.beings.length} gods and spirits ever</div>${treeSvg(f, st.pick != null ? Math.max(700, main.clientWidth - 40) : 560)}</div>`; }).join('')}</div>`;
  }

  // ---- 2. the map ----
  function mapMount(bar, main) {
    const n = D.frames.length;
    bar.innerHTML = `<button id="rl-play" title="play the frames">▶</button><input type="range" id="rl-fr" min="0" max="${n - 1}" value="${D.frames.findIndex((x) => x[0] === st.frame)}" style="width:420px">
      <b id="rl-when"></b><span class="muted" id="rl-load"></span><label class="muted"><input type="checkbox" id="rl-paths" ${st.paths ? 'checked' : ''}> every faith's path (else only the followed one's)</label>`;
    main.innerHTML = `<div class="rl-split"><div><div class="rl-mapbox"><img id="rl-img" alt="the faiths on the map"><svg id="rl-ov" viewBox="0 0 1024 512" preserveAspectRatio="none"></svg></div></div><div class="rl-side" id="rl-side"></div></div>`;
    $('rl-fr').oninput = (e) => { st.frame = D.frames[+e.target.value][0]; update(); };
    $('rl-paths').onchange = (e) => { st.paths = e.target.checked; update(); };
    $('rl-play').onclick = () => {
      if (st.playing) { clearInterval(st.playing); st.playing = null; $('rl-play').textContent = '▶'; return; }
      $('rl-play').textContent = '❚❚';
      st.playing = setInterval(() => { const k = D.frames.findIndex((x) => x[0] === st.frame); if (k + 1 >= D.frames.length || !$('rl-fr')) { clearInterval(st.playing); st.playing = null; if ($('rl-play')) $('rl-play').textContent = '▶'; return; }
        st.frame = D.frames[k + 1][0]; $('rl-fr').value = k + 1; update(); }, 900);
    };
  }
  const P = (lat, lon) => [(lon + 180) / 360 * 1024, (90 - lat) / 180 * 512];
  function mapDraw() {
    const fr = D.frames.find((x) => x[0] === st.frame) || D.frames[D.frames.length - 1], at = fr[1];
    $('rl-when').textContent = ago(at);
    const img = $('rl-img'), src = `../api/faithmap?run=${encodeURIComponent(D.id)}&frame=${fr[0]}&w=1024${st.follow != null ? '&only=' + st.follow : ''}`;
    if (img.dataset.src !== src) { img.dataset.src = src; $('rl-load').textContent = 'drawing…'; img.onload = () => { if ($('rl-load')) $('rl-load').textContent = ''; }; img.src = src; }
    const live = D.F.filter((f) => f.founded_kyr >= at - 1e-9 && (f.ended_kyr == null || f.ended_kyr < at - 1e-9));
    const sample = (f) => { let s = null; for (const t of f.track) if (t[0] >= at - 1e-9) s = t; else break; return s; };
    let o = '';
    for (const f of live) {
      if (st.follow != null && f.id !== st.follow) continue;
      const tr = f.track.filter((t) => t[0] >= at - 1e-9 && t[3] != null);
      if (!tr.length) continue;
      if ((st.paths || st.follow === f.id) && tr.length > 1) {  // (the centre's path; split where it jumps the date line)
        let d = '', prev = null;
        for (const t of tr) { const [px, py] = P(t[3], t[4]); d += (prev && Math.abs(px - prev) < 512 ? 'L' : 'M') + px.toFixed(1) + ',' + py.toFixed(1); prev = px; }
        o += `<path d="${d}" fill="none" stroke="${f.color}" stroke-width="${st.follow === f.id ? 2.5 : 1.2}" opacity=".9"/>`;
      }
      const [x0, y0] = P(tr[0][3], tr[0][4]);
      o += `<path d="M${x0 - 5},${y0}h10M${x0},${y0 - 5}v10" stroke="#fff" stroke-width="3.5"/><path d="M${x0 - 5},${y0}h10M${x0},${y0 - 5}v10" stroke="${f.color}" stroke-width="2"/>`;
    }
    $('rl-ov').innerHTML = o;
    const rows = live.map((f) => [f, sample(f)]).filter(([, s]) => s).sort((a, b) => b[1][2] - a[1][2]);
    $('rl-side').innerHTML = `<h3>${rows.length} faiths ${at > 0 ? ago(at) : 'now'}</h3>${st.follow != null ? '<p><a href="#" id="rl-all">show all faiths</a></p>' : ''}
      <table class="t"><tr><th>faith</th><th>cultures</th><th>cells</th><th>lead god</th></tr>${rows.map(([f, s]) => `<tr data-f="${f.id}" class="${st.follow === f.id ? 'sel' : ''}" title="founded ${esc(ago(f.founded_kyr))} in ${esc(D.cname(f.origin_culture))}; core ${esc(s[6])}"><td>${sw(f.color)}${fname(f)}</td><td class="n">${s[1]}</td><td class="n">${s[2]}</td><td class="n" style="color:${indCol(s[5])}">${s[5].toFixed(2)}</td></tr>`).join('')}</table>`;
    for (const tr of $('rl-side').querySelectorAll('tr[data-f]')) tr.onclick = () => { st.follow = st.follow === +tr.dataset.f ? null : +tr.dataset.f; update(); };
    if ($('rl-all')) $('rl-all').onclick = (e) => { e.preventDefault(); st.follow = null; update(); };
  }

  // ---- 3. the timeline ----
  function tlMount(bar) {
    const s = D.gods.summary.faiths || {};
    bar.innerHTML = `<label class="muted"><input type="checkbox" id="rl-gone" ${st.gone ? 'checked' : ''}> with the faiths gone</label>
      <span class="muted">${D.F.length} faiths since ${ago(D.gods.from_kyr)}, ${D.F.filter((f) => f.ended_kyr == null).length} living: ${s.founded || 0} founded, ${s.schisms || 0} schisms, ${s.conversions || 0} conversions, ${s.core_changes || 0} cores moved;
      ${D.F.filter((f) => f.end === 'no followers left').length} ended with no followers left</span>`;
    $('rl-gone').onchange = (e) => { st.gone = e.target.checked; update(); };
  }
  function tlDraw(main) {
    const keep = new Set();
    for (const f of D.F) if (st.gone || f.ended_kyr == null) { let x = f; while (x && !keep.has(x.id)) { keep.add(x.id); x = x.parent != null ? D.F[x.parent] : null; } }
    const kids = {};
    for (const f of D.F) if (keep.has(f.id)) (kids[f.parent ?? 'root'] = kids[f.parent ?? 'root'] || []).push(f);
    const BW = 260, x = logX(D.gods.from_kyr || 300, 0, BW);
    const bar = (f) => { const a = x(f.founded_kyr), b = x(f.ended_kyr ?? 0.05);
      let dots = f.events.map((e) => `<span title="${e[1] === 'founded' ? 'founded in' : 'won'} ${esc(D.cname(e[2]))} ${esc(ago(e[0]))}" style="position:absolute;left:${x(e[0]) - 2}px;top:1px;width:5px;height:5px;border-radius:50%;background:#6bd66b"></span>`).join('');
      dots += (D.lost[f.id] || []).map((e) => `<span title="lost ${esc(D.cname(e[2]))} to ${esc(D.F.find((g) => g.events.includes(e))?.name || '')} ${esc(ago(e[0]))}" style="position:absolute;left:${x(e[0]) - 2}px;top:1px;width:5px;height:5px;border-radius:50%;background:#ff6b6b"></span>`).join('');
      return `<span style="position:relative;display:inline-block;width:${BW}px;height:8px;background:var(--line,#1f2836);vertical-align:middle"><span style="position:absolute;left:${a}px;width:${Math.max(2, b - a)}px;top:0;bottom:0;background:${f.color};opacity:${f.ended_kyr != null ? 0.45 : 1}"></span>${dots}</span>`; };
    let h = `<table class="t"><tr><th>faith</th><th>how</th><th>life <span class="muted">(${ago(D.gods.from_kyr)} → now)</span></th><th>cultures now / ever</th><th>peoples now</th><th>leading god now</th><th>end</th></tr>`;
    const L = Object.fromEntries((D.result.lineages || []).map((l) => [l.id, l.name.split(' (')[0]]));
    const row = (f, d) => { const lead = f.lead_being != null ? D.B[f.lead_being] : null;
      h += `<tr style="${f.ended_kyr != null ? 'opacity:.6' : ''}"><td style="white-space:nowrap;padding-left:${4 + 14 * d}px">${d ? '<span class="muted">↳ </span>' : ''}${sw(f.color)}${fname(f)}</td>
        <td>${esc(f.how)}</td><td style="white-space:nowrap">${bar(f)} <span class="muted">${ago(f.founded_kyr)}</span></td><td class="n">${f.cultures_now.length} / ${f.cultures_ever.length}</td>
        <td class="muted" style="max-width:260px">${esc(f.peoples_now.map((p) => L[p] || p).join(', '))}</td>
        <td>${lead ? `<span style="color:${indCol(lead.individuation)}">${esc(lead.label)}</span> <span class="muted">${lead.individuation.toFixed(2)}</span>` : ''}</td>
        <td class="muted">${f.ended_kyr != null ? esc(f.end) + ' ' + ago(f.ended_kyr) : ''}${f.changes.length ? ` <span title="${esc(f.changes.map((c) => `${ago(c[0])}: ${c[1]} → ${c[2]}`).join('\n'))}">core moved ×${f.changes.length}</span>` : ''}</td></tr>`; };
    const walk = (k, d) => (kids[k] || []).sort((a, b) => b.founded_kyr - a.founded_kyr).forEach((f) => { row(f, d); walk(f.id, d + 1); });
    walk('root', 0);
    main.innerHTML = h + '</table>' + `<p class="muted" style="max-width:900px">The rule (a judgement call, readout only): ${esc(D.gods.faiths.rule)}</p>`;
  }

  // ---- 4. taboos ----
  function tabMount(bar) {
    const T = D.taboos;
    if (!T || T.error) { bar.innerHTML = `<span class="muted">No taboos: ${esc(T?.error || '')}</span>`; return; }
    const cs = Object.entries(T.cultures).sort((a, b) => a[1].name.localeCompare(b[1].name));
    if (st.culture == null || !T.cultures[st.culture]) st.culture = cs[0]?.[0];
    bar.innerHTML = `<span class="muted">culture</span><select id="rl-cul">${cs.map(([id, c]) => `<option value="${id}" ${id === st.culture ? 'selected' : ''}>${esc(c.name)} (${c.taboos.length})</option>`).join('')}</select>
      <span class="muted">${cs.length} living cultures · ${Object.values(T.summary.by_kind || {}).reduce((a, b) => a + b, 0)} taboos in all</span>`;
    $('rl-cul').onchange = (e) => { st.culture = e.target.value; update(); };
  }
  function tabDraw(main) {
    const T = D.taboos; if (!T || T.error) { main.innerHTML = ''; return; }
    const c = T.cultures[st.culture], K = T.kinds || {}, S = T.sources || {};
    const src = (k) => (S[k] ? `<a href="${esc(S[k].url)}" target="_blank" title="${esc(S[k].title)} (${esc(S[k].level)})">${esc(k)}</a>` : esc(k || ''));
    const fn = D.gods.cultures?.[st.culture]?.faith_now, cf = fn != null ? D.F[fn] : null;
    const at = D.gods.attitudes?.cultures?.[st.culture]?.now;  // (PW-904: [tolerance, aggression] now, 0..1)
    const atx = at ? `tolerance ${at[0].toFixed(2)}, aggression ${at[1].toFixed(2)} <span title="${esc(D.gods.attitudes.rule || '')}">(?)</span> · ` : '';
    let h = `<h3>${esc(c.name)}</h3><p class="muted">${cf ? `faith: ${sw(cf.color)}${fname(cf)}${cf.missionary ? ' (missionary)' : ''} · ` : ''}${atx}tags:${esc((c.tags || []).join(', '))}</p><table class="t"><tr><th>kind</th><th>taboo</th><th>who</th><th>why</th><th>source</th></tr>`;
    for (const t of c.taboos) h += `<tr><td>${esc(K[t.kind]?.name || t.kind)}</td><td>${esc(t.kind === 'food' ? 'not eaten: ' + t.label : t.label)}</td><td>${esc(t.scope)}</td><td class="muted" style="max-width:360px">${esc(t.why)}</td><td>${t.kind === 'food' ? '<span class="muted">taboos.py (food)</span>' : src(t.source)}</td></tr>`;
    h += '</table><h3 style="margin-top:16px">The catalogue: kinds across all living cultures</h3><table class="t"><tr><th>kind</th><th>what</th><th>cultures with one</th><th>rules</th><th>sources</th></tr>';
    const all = Object.values(T.cultures);
    for (const [k, v] of Object.entries(K)) {
      const n = all.filter((x) => x.taboos.some((t) => t.kind === k)).length;
      h += `<tr><td>${esc(v.name)}</td><td class="muted" style="max-width:420px">${esc(v.what)}</td><td class="n">${n} (${Math.round(100 * n / Math.max(all.length, 1))}%)</td><td class="n">${T.summary.by_kind?.[k] ?? ''}</td><td>${v.sources.map(src).join(', ')}</td></tr>`;
    }
    h += '</table><h3 style="margin-top:16px">Sources</h3><ul>' + Object.entries(S).map(([k, s]) => `<li><b>${esc(k)}</b>: <a href="${esc(s.url)}" target="_blank">${esc(s.title)}</a> <span class="muted">(${esc(s.level)})</span></li>`).join('') + '</ul>';
    main.innerHTML = h;
  }

  // ---- 5. your faiths (PW-1430) ----
  const dflt = () => (NumFmt.present && NumFmt.present() != null ? 'year' : 'ago');  // (a bare number: a calendar year once the present is set, else years ago)
  const readYear = (t) => { const k = NumFmt.parseDate ? NumFmt.parseDate(t, dflt()) : null; return k == null || !Number.isFinite(k) ? null : k; };
  const blank = () => ({ id: null, name: '', culture: null, people: null, place: null, year_text: '', ago_kyr: null, gods: [{ name: '', domains: [] }], spreads: true, missionary: true });
  function founderOpts(f) {
    const L = Object.fromEntries((D.result.lineages || []).map((l) => [l.id, l.name.split(' (')[0]]));
    const cs = D.C.map((c) => c).sort((a, b) => a.name.localeCompare(b.name));
    const ps = [...new Set(D.C.map((c) => c.people))].sort((a, b) => String(L[a] || a).localeCompare(String(L[b] || b)));
    const cur = f.culture != null ? `c${f.culture}` : f.people != null ? `p${f.people}` : '';
    return `<option value="" ${cur === '' ? 'selected' : ''}>nobody chosen: the culture nearest the place</option>
      <optgroup label="a people (its culture nearest the place, else its largest)">${ps.map((p) => `<option value="p${esc(p)}" ${cur === 'p' + p ? 'selected' : ''}>${esc(L[p] || p)}</option>`).join('')}</optgroup>
      <optgroup label="a culture">${cs.map((c) => `<option value="c${c.id}" ${cur === 'c' + c.id ? 'selected' : ''}>${esc(c.name)} (${esc(L[c.people] || c.people)}${c.end ? ', ' + esc(c.end) : ''})</option>`).join('')}</optgroup>`;
  }
  const domOpts = (cur) => `<option value="">-</option>` + Object.entries(D.gods.groups || {}).map(([g, ds]) => `<optgroup label="${esc(g)}">${ds.map((d) => `<option ${d === cur ? 'selected' : ''}>${esc(d)}</option>`).join('')}</optgroup>`).join('');
  function yoursMount(bar) {
    const A = D.gods.authored || {};
    bar.innerHTML = `<button id="rl-add">✎ write a faith</button><span class="muted" style="max-width:900px">${esc(A.rule || '')}</span>`;
    $('rl-add').onclick = () => { st.edit = blank(); update(); };
  }
  function yoursDraw(main) {
    const saved = D.authored.faiths || [], R = Object.fromEntries(((D.gods.authored || {}).faiths || []).map((r) => [r.id, r]));
    const who = (f) => (f.culture != null ? D.cname(f.culture) : f.people != null ? `the ${f.people}` : 'the culture nearest the place') + (f.place ? ` at ${f.place[0].toFixed(1)}°, ${f.place[1].toFixed(1)}°` : '');
    let h = `<div class="rl-split"><div>`;
    if (!saved.length) h += `<p class="muted">No faiths written in yet. Press "write a faith" to add one: a name, who founds it, where and when, its gods.</p>`;
    else {
      h += `<table class="t"><tr><th>faith</th><th>founded by</th><th>asked for</th><th>gods</th><th>result</th><th></th></tr>`;
      saved.forEach((f, i) => { const r = R[f.id], F = r && r.faith != null ? D.F[r.faith] : null;
        const res = !r ? '<span class="muted">not read (see the problems below)</span>' : r.took_hold
          ? `<span class="ok">took hold</span> ${esc(ago(r.founded_kyr))} in ${esc(r.founded_in_name || D.cname(r.founded_in))}; ${esc(r.spread || '')}; ${r.ended_kyr != null ? `ended ${esc(ago(r.ended_kyr))} (${esc(r.end)})` : `${r.cultures_now} cultures now, ${r.cultures_ever} ever`}${r.note ? `<br><span class="muted">${esc(r.note)}</span>` : ''}`
          : `<span class="no">did not take hold</span>: ${esc(r.why || '')}`;
        h += `<tr><td>${F ? sw(F.color) : ''}${esc(f.name)}<span class="rl-yours">✎ yours</span></td><td>${esc(who(f))}</td><td>${esc(f.year_text || '')} <span class="muted">(${esc(ago(f.ago_kyr))})</span></td>
          <td>${f.gods.map((g) => `${esc(g.name)} <span class="muted">(${esc(g.domains.join(', '))})</span>`).join('<br>')}</td><td style="max-width:420px">${res}<br><span class="muted">${!f.spreads ? 'stays closed' : f.missionary === false ? 'spreads (no missionaries)' : 'missionary'}</span></td>
          <td style="white-space:nowrap"><button data-ed="${i}">edit</button> <button data-rm="${i}">remove</button>${F ? ` <button data-tree="${F.id}">its tree</button>` : ''}</td></tr>`; });
      h += '</table>';
    }
    const probs = (D.gods.authored || {}).problems || [];
    if (probs.length) h += `<p class="err">Problems in the saved file (skipped): ${probs.map(esc).join('; ')}</p>`;
    h += `<p class="err" id="rl-err">${esc(st.err || '')}</p></div><div class="rl-side">${st.edit ? formHtml(st.edit) : '<p class="muted">Pick "edit" on a faith, or "write a faith".</p>'}</div></div>`;
    main.innerHTML = h;
    for (const b of main.querySelectorAll('[data-ed]')) b.onclick = () => { st.edit = JSON.parse(JSON.stringify(saved[+b.dataset.ed])); st.err = ''; update(); };
    for (const b of main.querySelectorAll('[data-rm]')) b.onclick = () => { const f = saved[+b.dataset.rm]; if (typeof confirm === 'function' && !confirm(`Remove "${f.name}"?`)) return; save(saved.filter((x) => x !== f)); };
    for (const b of main.querySelectorAll('[data-tree]')) b.onclick = () => { st.pick = +b.dataset.tree; setView('trees'); };
    if (st.edit) formWire(saved);
  }
  function formHtml(f) {
    const k = f.ago_kyr;
    return `<div class="rl-form"><h3>${f.id ? 'Edit' : 'Write'} a faith</h3>
      <label>name <input id="rf-name" value="${esc(f.name)}" maxlength="80"></label>
      <label>founded by <select id="rf-who">${founderOpts(f)}</select></label>
      <div><div class="row"><span class="muted">where</span><label class="row"><input type="radio" name="rf-pl" value="home" ${f.place ? '' : 'checked'}> the founder's home</label>
        <label class="row"><input type="radio" name="rf-pl" value="map" ${f.place ? 'checked' : ''}> a place: click the map</label><span id="rf-plt" class="muted">${f.place ? `${f.place[0].toFixed(2)}°, ${f.place[1].toFixed(2)}°` : ''}</span></div>
        <div class="rl-pick" id="rf-map"><img alt="click to pick the place" src="../api/faithmap?run=${encodeURIComponent(D.id)}&frame=${D.frames.length ? D.frames[D.frames.length - 1][0] : 0}&w=1024"><svg id="rf-mk" viewBox="0 0 1024 512" preserveAspectRatio="none"></svg></div></div>
      <label>year <input id="rf-year" value="${esc(f.year_text || (k != null ? ago(k) : ''))}" placeholder="${dflt() === 'year' ? 'year 1400, 300 before year 1' : '12,000 years ago, 12 kyr'}"><span id="rf-yr" class="muted"></span></label>
      <div><span class="muted">gods (name, then one to three domains)</span><div id="rf-gods">${f.gods.map((g, i) => `<div class="row" data-g="${i}"><input class="rf-gn" value="${esc(g.name)}" placeholder="name" maxlength="60" style="width:120px">
        ${[0, 1, 2].map((j) => `<select class="rf-gd">${domOpts(g.domains[j])}</select>`).join('')}<button data-gx="${i}" title="remove this god">×</button></div>`).join('')}</div><button id="rf-addg">+ a god</button></div>
      <label class="row"><input type="checkbox" id="rf-spr" ${f.spreads ? 'checked' : ''}> spreads to its neighbours (else it stays closed: it takes no converts)</label>
      <label class="row"><input type="checkbox" id="rf-mis" ${f.spreads && f.missionary !== false ? 'checked' : ''}> missionary: it sends preachers and wins less organised neighbours within a century or two (else it spreads slowly, from temples)</label>
      <div class="row"><button id="rf-save">save</button><button id="rf-cancel">cancel</button><span id="rf-msg" class="err"></span></div></div>`;
  }
  function readForm() {  // (the form into st.edit, so a redraw keeps what was typed)
    const f = st.edit;
    f.name = $('rf-name').value.trim();
    const w = $('rf-who').value;
    f.culture = w[0] === 'c' ? +w.slice(1) : null; f.people = w[0] === 'p' ? w.slice(1) : null;
    const map = D.root.querySelector('input[name="rf-pl"][value="map"]');
    if (map && !map.checked) f.place = null;
    f.year_text = $('rf-year').value.trim(); f.ago_kyr = readYear(f.year_text);
    f.gods = [...D.root.querySelectorAll('#rf-gods [data-g]')].map((r) => ({ name: r.querySelector('.rf-gn').value.trim(), domains: [...r.querySelectorAll('.rf-gd')].map((s) => s.value).filter(Boolean) }));
    f.spreads = $('rf-spr').checked;
    f.missionary = f.spreads && $('rf-mis').checked;
    return f;
  }
  function problem(f) {  // (what the server would refuse, said before saving)
    if (!f.name) return 'it needs a name';
    if (f.ago_kyr == null) return `the year "${f.year_text}" could not be read (try ${dflt() === 'year' ? '"year 1400"' : '"12,000 years ago"'} or "12 kyr")`;
    if (f.culture == null && f.people == null && !f.place) return 'pick who founds it, or a place on the map';
    if (!f.gods.some((g) => g.domains.length)) return 'it needs at least one god with a domain';
    return '';
  }
  function marker(f) { const mk = $('rf-mk'); if (!mk) return; if (!f.place) { mk.innerHTML = ''; return; } const [x, y] = P(f.place[0], f.place[1]);
    mk.innerHTML = `<path d="M${x - 8},${y}h16M${x},${y - 8}v16" stroke="#fff" stroke-width="5"/><path d="M${x - 8},${y}h16M${x},${y - 8}v16" stroke="#ff7b6b" stroke-width="2.5"/>`; }
  function formWire(saved) {
    const f = st.edit, yr = () => { const k = readYear($('rf-year').value); $('rf-yr').textContent = $('rf-year').value.trim() ? (k == null ? 'cannot read that date' : `→ ${ago(k)}`) : ''; };
    yr(); marker(f);
    $('rf-year').oninput = yr;
    $('rf-map').onclick = (e) => { const r = e.currentTarget.getBoundingClientRect(); if (!r.width) return;
      const lon = ((e.clientX - r.left) / r.width) * 360 - 180, lat = 90 - ((e.clientY - r.top) / r.height) * 180;
      f.place = [Math.max(-90, Math.min(90, lat)), lon]; const m = D.root.querySelector('input[name="rf-pl"][value="map"]'); if (m) m.checked = true;
      $('rf-plt').textContent = `${f.place[0].toFixed(2)}°, ${f.place[1].toFixed(2)}°`; marker(f); };
    $('rf-addg').onclick = () => { readForm(); if (f.gods.length < 15) f.gods.push({ name: '', domains: [] }); update(); };
    for (const b of D.root.querySelectorAll('[data-gx]')) b.onclick = () => { readForm(); f.gods.splice(+b.dataset.gx, 1); if (!f.gods.length) f.gods.push({ name: '', domains: [] }); update(); };
    $('rf-cancel').onclick = () => { st.edit = null; st.err = ''; update(); };
    $('rf-save').onclick = () => {
      readForm(); f.gods = f.gods.filter((g) => g.name || g.domains.length);
      const why = problem(f); if (why) { $('rf-msg').textContent = why; if (!f.gods.length) f.gods.push({ name: '', domains: [] }); return; }
      if (!f.id) { let n = saved.length + 1; while (saved.some((x) => x.id === `a${n}`)) n++; f.id = `a${n}`; }
      const i = saved.findIndex((x) => x.id === f.id);
      save(i >= 0 ? saved.map((x, k) => (k === i ? f : x)) : [...saved, f]);
    };
  }
  function post(body) {
    return fetch('../api/authored', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ run: D.id, ...body }) })
      .then((r) => r.json().then((j) => (r.ok ? j : Promise.reject(new Error(j.error || r.status)))));
  }
  function reload(msg) {  // (fetch everything again: the trees, map, timeline and taboos all redraw with the saved faiths)
    const root = D.root, result = D.result;
    D = null; mounted = '';
    window.ReligionTab.draw(root, result);
    if (msg) st.err = msg;
  }
  function save(list) {
    if ($('rf-msg')) $('rf-msg').textContent = 'saving, then working the faiths out again…';
    post({ faiths: list }).then(() => { st.edit = null; st.err = ''; reload(); })
      .catch((e) => { st.err = `not saved: ${e.message}`; if ($('rf-msg')) $('rf-msg').textContent = st.err; else update(); });
  }
  function setMode(m) { post({ gods_mode: m }).then(() => reload()).catch((e) => { st.err = `gods mode not saved: ${e.message}`; update(); }); }

  const MOUNT = { trees: treesMount, map: mapMount, timeline: tlMount, taboos: tabMount, yours: yoursMount };
  const DRAW = { trees: treesDraw, map: mapDraw, timeline: tlDraw, taboos: tabDraw, yours: yoursDraw };
  function update() { if ($('rl-main')) DRAW[st.view]($('rl-main')); }
  function setView(v) { if (st.playing) { clearInterval(st.playing); st.playing = null; } st.view = v; mounted = ''; history.replaceState(null, '', `${location.search}#religion/${v}`); window.ReligionTab.draw(D.root, D.result); }
  window.ReligionTab = {
    get view() { return st.view; },
    draw(el, result) {
      if (!D || D.id !== result.id || D.busy) { mounted = ''; el.innerHTML = `<p class="muted" style="padding:10px 12px">Working out the gods, faiths and taboos of ${esc(result.id)}…</p>`; }
      load(result, () => {
        D.root = el; D.result = result;
        if (!D.gods || D.gods.error || !D.F) { el.innerHTML = `<p class="muted" style="padding:10px 12px">No religion for ${esc(result.id)}: ${esc(D.gods?.error || 'this run has no faiths')}</p>`; return; }
        const key = `${D.id}|${st.view}`;
        if (mounted !== key || !$('rl-main')) {
          el.innerHTML = `<div class="rl-nav">${VIEWS.map(([v, n]) => `<button data-view="${v}" class="${v === st.view ? 'on' : ''}">${n}</button>`).join('')}
            <span style="flex:1"></span><span class="muted">run ${esc(D.id)} · ${D.gods.summary.living} living gods and spirits · ${D.F.filter((f) => f.ended_kyr == null).length} living faiths${D.F.some((f) => f.authored != null) ? ` (${D.F.filter((f) => f.authored != null).length} yours)` : ''} · gods mode</span>
            <select id="rl-mode" title="saved with the run: whether the gods are real (PW-1309)">${MODES.map(([m, n]) => `<option value="${m}" ${m === D.gods.gods_mode ? 'selected' : ''}>${n}</option>`).join('')}</select></div>
            <div class="rl-bar" id="rl-bar"></div><div class="rl-main" id="rl-main"></div>`;
          for (const b of el.querySelectorAll('[data-view]')) b.onclick = () => setView(b.dataset.view);
          if ($('rl-mode')) $('rl-mode').onchange = (e) => setMode(e.target.value);
          MOUNT[st.view]($('rl-bar'), $('rl-main'));
          mounted = key;
        }
        if ($('foot')) $('foot').innerHTML = FOOT[st.view];
        update();
      });
    },
  };
})();
