'use strict';
// The languages viewer's "Continuum & intelligibility" tab (languages.html; helpers in langcore.js): a map of the lects spoken
// at the scrubbed frame (each at its deme's place, coloured by language, true family or people) with the contacts between them
// coloured by how well they understand each other then; the dialect chains (the pass's own, found now, and the same search at
// the scrubbed frame) with each link's value and the end-to-end value; and a heatmap of every pair inside the picked lect's
// language, family or people.
(() => {
  const V = globalThis.LangView, LC = globalThis.LangCore;
  const { esc, ago, lk, sw } = V;
  const CSS = `
#tab-continuum .cgrid { display: grid; grid-template-columns: minmax(0, 1fr) 400px; gap: 10px; align-items: start; }
#tab-continuum .mapbox { position: relative; width: 100%; aspect-ratio: 2 / 1; background: #0a1420; border-radius: 4px; overflow: hidden; }
#tab-continuum .mapbox img { position: absolute; inset: 0; width: 100%; height: 100%; opacity: .55; image-rendering: auto; }
#tab-continuum .mapbox canvas { position: absolute; inset: 0; width: 100%; height: 100%; cursor: crosshair; }
#tab-continuum .tip { position: absolute; pointer-events: none; background: var(--panel); border: 1px solid var(--line); border-radius: 4px; padding: 3px 6px; font-size: 12px; white-space: nowrap; z-index: 3; display: none; }
#tab-continuum .chain { border: 1px solid var(--line); border-radius: 6px; padding: 6px 8px; margin-bottom: 8px; cursor: pointer; }
#tab-continuum .chain.on { border-color: var(--acc); background: #16233a; }
#tab-continuum .link { display: flex; align-items: center; gap: 6px; margin: 1px 0 1px 14px; font-size: 11px; color: var(--muted); }
#tab-continuum .bar { height: 7px; border-radius: 3px; }
#tab-continuum .side { max-height: calc(100vh - 230px); overflow: auto; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const st = { color: 'language', scope: 'language', chain: null, edges: new Map(), found: new Map(), doc: null, img: null, pts: [] };

  function aliveAt(S, i) {
    const kyr = S.ix.frames[i];
    return S.doc.lects.filter((l) => l.deme != null && LC.alive(l, kyr));
  }
  function inContact(S, a, b, kyr) {
    const la = S.ix.by.get(a), lb = S.ix.by.get(b);
    if (!la || !lb || la.deme == null || lb.deme == null) return false;
    if (la.deme === lb.deme) return true;
    const p = S.demePairs.get(la.deme < lb.deme ? la.deme + '|' + lb.deme : lb.deme + '|' + la.deme);
    return !!p && p.first_kyr >= kyr - 1e-9 && p.last_kyr <= kyr + 1e-9;
  }
  function edgesAt(S, i) {  // [a, b, v] for measured pairs both spoken at frame i whose demes touched then
    if (st.doc !== S.doc) { st.doc = S.doc; st.edges = new Map(); st.found = new Map(); }
    if (st.edges.has(i)) return st.edges.get(i);
    const kyr = S.ix.frames[i], out = [];
    for (const [a, b, vals] of (S.doc.intelligibility && S.doc.intelligibility.pairs) || []) {
      const v = vals[i];
      if (v == null) continue;
      const la = S.ix.by.get(a), lb = S.ix.by.get(b);
      if (!la || !lb || !LC.alive(la, kyr) || !LC.alive(lb, kyr)) continue;
      if (inContact(S, a, b, kyr)) out.push([a, b, v]);
    }
    if (i === S.ix.frames.length - 1 && !out.length) for (const [a, b, v] of (S.doc.intelligibility && S.doc.intelligibility.now) || []) if (inContact(S, a, b, kyr)) out.push([a, b, v]);
    st.edges.set(i, out);
    return out;
  }
  function foundAt(S, i) {  // the continua search (families.continua) at frame i, grouped by true family
    edgesAt(S, i);
    if (st.found.has(i)) return st.found.get(i);
    const kyr = S.ix.frames[i];
    const ids = aliveAt(S, i).map((l) => l.id);
    const res = LC.findContinua(ids, (a, b) => S.ix.intelAt(a, b, i), (a, b) => inContact(S, a, b, kyr), (x) => S.ix.by.get(x).family_true || x);
    st.found.set(i, res);
    return res;
  }
  function colorOf(S, l) {
    if (st.color === 'people') return V.peopleColor(l.people);
    if (st.color === 'family') return LC.hue(l.family_true || l.id);
    return LC.hue(l.language || l.family_true || l.id);
  }

  V.TABS.continuum = {
    foot: 'Each dot is a lect spoken at the moment on the slider, at its people\'s place; a line joins neighbours, green when they understand each other well (> 0.7), amber in part (0.4-0.7), red hardly (< 0.4). A chain lists dialects in a row: each neighbour understands the next, yet the two ends may not understand each other. Press ▶ to watch when a chain broke apart.',
    hash() { return `col=${st.color}&sc=${st.scope}`; },
    reset(S, q) { st.chain = null; if (q.get('col')) st.color = q.get('col'); if (q.get('sc')) st.scope = q.get('sc'); },
    draw(el, S) {
      el.innerHTML = '';
      el.appendChild(V.scrubber());
      const body = document.createElement('div');
      body.innerHTML = `<div class="cgrid"><div>
          <div class="row" style="margin-bottom:6px"><span class="muted">colour dots by</span><span class="seg" id="cmCol">${[['language', 'language'], ['family', 'true family'], ['people', 'people']].map(([k, t]) => `<button data-k="${k}" class="${st.color === k ? 'on' : ''}">${t}</button>`).join('')}</span>
            <span class="muted" style="margin-left:10px">${['high', 'mid', 'low'].map((c, k) => `<span class="sw" style="background:${LC.intelColor([0.8, 0.5, 0.2][k])}"></span>${['> 0.7', '0.4-0.7', '< 0.4'][k]}`).join(' ')}</span>
            <label class="muted"><input type="checkbox" id="cmLow" ${st.hideLow ? 'checked' : ''}> hide red</label><span id="cmCount" class="muted"></span></div>
          <div class="mapbox" id="cmBox"><img id="cmImg" alt="" hidden><canvas id="cmCv"></canvas><div class="tip" id="cmTip"></div></div>
          <div class="card" style="margin-top:10px"><h3>Who understands whom <span class="muted" style="font-weight:normal">inside the picked lect's</span> <span class="seg" id="cmScope">${[['language', 'language'], ['family', 'true family'], ['people', 'people']].map(([k, t]) => `<button data-k="${k}" class="${st.scope === k ? 'on' : ''}">${t}</button>`).join('')}</span></h3><div id="cmMat"></div></div>
        </div><div class="side" id="cmSide"></div></div>`;
      el.appendChild(body);
      body.querySelectorAll('#cmCol button').forEach((b) => (b.onclick = () => { st.color = b.dataset.k; V.writeHash(); this.draw(el, S); }));
      body.querySelectorAll('#cmScope button').forEach((b) => (b.onclick = () => { st.scope = b.dataset.k; V.writeHash(); this.draw(el, S); }));
      body.querySelector('#cmLow').onchange = (e) => { st.hideLow = e.target.checked; this.frame(el, S); };
      const img = body.querySelector('#cmImg');
      img.onload = () => { img.hidden = false; };
      img.onerror = () => { img.hidden = true; };
      img.src = `../api/thumb?kind=run&id=${encodeURIComponent(S.runId)}&proj=equirect&w=1024`;
      const cv = body.querySelector('#cmCv');
      cv.onmousemove = (e) => { const h = hit(cv, e); const tip = body.querySelector('#cmTip'); if (!h) { tip.style.display = 'none'; return; } tip.style.display = 'block'; tip.style.left = (h.x + 10) + 'px'; tip.style.top = (h.y - 8) + 'px'; tip.textContent = `${V.lectLabel(h.id)} (${V.peopleName(S.ix.by.get(h.id).people)})`; };
      cv.onmouseleave = () => { body.querySelector('#cmTip').style.display = 'none'; };
      cv.onclick = (e) => { const h = hit(cv, e); if (h) V.select(h.id); };
      this.frame(el, S);
    },
    frame(el, S) {
      const t0 = performance.now();
      const cv = el.querySelector('#cmCv');
      if (!cv) return this.draw(el, S);
      drawMap(S, cv, el);
      drawSide(S, el.querySelector('#cmSide'), el);
      drawMatrix(S, el.querySelector('#cmMat'));
      S.mapMs = Math.round(performance.now() - t0);
    },
  };
  function hit(cv, e) {
    const r = cv.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
    let best = null, bd = 64;
    for (const p of st.pts) { const d = (p.x - mx) ** 2 + (p.y - my) ** 2; if (d < bd) { bd = d; best = p; } }
    return best;
  }
  function drawMap(S, cv, el) {
    const box = cv.parentElement, W = box.clientWidth, H = box.clientHeight, dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr; cv.height = H * dpr;
    const g = cv.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, W, H);
    const X = (lon) => (lon + 180) / 360 * W, Y = (lat) => (90 - lat) / 180 * H;
    g.strokeStyle = 'rgba(139,151,168,.15)'; g.lineWidth = 0.5;
    for (let lo = -180; lo <= 180; lo += 30) { g.beginPath(); g.moveTo(X(lo), 0); g.lineTo(X(lo), H); g.stroke(); }
    for (let la = -60; la <= 60; la += 30) { g.beginPath(); g.moveTo(0, Y(la)); g.lineTo(W, Y(la)); g.stroke(); }
    const i = S.f, live = aliveAt(S, i);
    const pos = new Map(), perDeme = new Map();
    for (const l of live) {
      const d = S.demes.get(l.deme);
      if (!d || d.lat == null) continue;
      const k = perDeme.get(l.deme) || 0; perDeme.set(l.deme, k + 1);
      pos.set(l.id, [X(d.lon) + k * 4, Y(d.lat) + k * 4, d.lon]);
    }
    const E = edgesAt(S, i).slice().sort((p, q) => p[2] - q[2]);  // (red first, green on top)
    for (const [a, b, v] of E) {
      const pa = pos.get(a), pb = pos.get(b);
      if (!pa || !pb) continue;
      if (st.hideLow && v < LC.INTEL_RED) continue;
      const c = LC.intelClass(v);
      g.strokeStyle = LC.intelColor(v); g.globalAlpha = c === 'low' ? 0.35 : 0.9; g.lineWidth = c === 'low' ? 0.7 : c === 'mid' ? 1.6 : 2.2;
      const la = S.demes.get(S.ix.by.get(a).deme), lb = S.demes.get(S.ix.by.get(b).deme);
      for (const [l0, l1] of LC.wrapLon(la.lon, lb.lon)) { g.beginPath(); g.moveTo(X(l0), pa[1]); g.lineTo(X(l1), pb[1]); g.stroke(); }
    }
    g.globalAlpha = 1;
    if (st.chain) {  // the picked chain, thick, each link in its colour at this frame
      g.lineWidth = 4;
      for (let k = 0; k + 1 < st.chain.length; k++) {
        const pa = pos.get(st.chain[k]), pb = pos.get(st.chain[k + 1]);
        if (!pa || !pb) continue;
        g.strokeStyle = LC.intelColor(S.ix.intelAt(st.chain[k], st.chain[k + 1], i));
        g.beginPath(); g.moveTo(pa[0], pa[1]); g.lineTo(pb[0], pb[1]); g.stroke();
      }
    }
    st.pts = [];
    const chainSet = new Set(st.chain || []);
    for (const l of live) {
      const p = pos.get(l.id);
      if (!p) continue;
      g.fillStyle = colorOf(S, l);
      g.beginPath(); g.arc(p[0], p[1], chainSet.has(l.id) ? 5 : 3.5, 0, 7); g.fill();
      g.strokeStyle = '#0b0f17'; g.lineWidth = 1; g.stroke();
      st.pts.push({ x: p[0], y: p[1], id: l.id });
    }
    const sp = pos.get(S.sel);
    if (sp) { g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.arc(sp[0], sp[1], 8, 0, 7); g.stroke(); }
    const c = el.querySelector('#cmCount');
    if (c) c.textContent = ` · ${live.length} lects spoken ${ago(S.ix.frames[i])}, ${E.length} neighbour pairs measured`;
  }
  function chainCard(S, ch, i, stored) {
    const c = LC.chainAt(S.ix, ch.chain, i), br = LC.chainBreak(S.ix, ch.chain);
    const on = st.chain && st.chain.join() === ch.chain.join();
    const bar = (v) => `<span class="bar" style="width:${v == null ? 30 : Math.max(4, v * 120)}px;background:${LC.intelColor(v)}${v == null ? ';opacity:.4' : ''}"></span><span>${v == null ? 'not measured' : v.toFixed(2)}</span>`;
    const rows = [];
    ch.chain.forEach((id, k) => {
      const l = S.ix.by.get(id);
      rows.push(`<div style="font-size:12px">${sw(colorOf(S, l))}${lk(id)} <span class="muted">${esc(V.peopleName(l.people))}${LC.alive(l, S.ix.frames[i]) ? '' : ', not spoken then'}</span></div>`);
      if (k + 1 < ch.chain.length) rows.push(`<div class="link">↕ ${bar(c.adj[k])}</div>`);
    });
    const verdict = c.broken ? '<span style="color:var(--mid)">the middle understands both neighbours, the two ends do not</span>'
      : c.linked && c.ends != null ? '<span class="ok">still one speech end to end</span>'
        : c.adj.some((v) => v != null && v <= 0.5) ? '<span class="err">a link in the chain is broken</span>' : '<span class="muted">not all of it was measured then</span>';
    // the ends' and the weakest link's value over time
    const n = S.ix.frames.length, Wd = 360, Hh = 46;
    const X = (j) => 4 + j / Math.max(1, n - 1) * (Wd - 8), Y = (v) => Hh - 4 - v * (Hh - 8);
    const line = (get, col) => { let d = ''; br.history.forEach((h, j) => { const v = get(h); if (v != null) d += (d && get(br.history[j - 1]) != null ? 'L' : 'M') + X(j) + ',' + Y(v); }); return `<path d="${d}" stroke="${col}" fill="none" stroke-width="1.5"/>`; };
    const spark = `<svg width="${Wd}" height="${Hh}"><line x1="4" x2="${Wd - 4}" y1="${Y(0.5)}" y2="${Y(0.5)}" stroke="#3a475c" stroke-dasharray="3 3"/>${line((h) => h.minAdj, '#7cc4ff')}${line((h) => h.ends, '#ffc940')}<line x1="${X(i)}" x2="${X(i)}" y1="2" y2="${Hh - 2}" stroke="#dfe6f0"/></svg>`;
    return `<div class="chain${on ? ' on' : ''}" data-chain="${esc(ch.chain.join(','))}">
      <div class="row" style="justify-content:space-between"><b>${ch.chain.length} lects</b><span class="muted">family ${esc(ch.family || '')}${stored ? ' · found by the pass' : ''}</span></div>
      ${rows.join('')}
      <div style="margin-top:4px;font-size:12px">ends ${esc(ch.chain[0])} ↔ ${esc(ch.chain[ch.chain.length - 1])}: ${bar(c.ends)}</div>
      <div style="font-size:12px">${verdict}${br.broke_kyr != null ? ` · <span class="muted">the ends stopped understanding each other ${esc(ago(br.broke_kyr))}</span>` : ''}</div>
      ${spark}<div class="muted" style="font-size:10px"><span style="color:#ffc940">ends</span> and <span style="color:#7cc4ff">weakest link</span> over time; dashed: 0.5</div></div>`;
  }
  function drawSide(S, side, el) {
    const i = S.f, stored = S.doc.continua || [];
    const found = foundAt(S, i).filter((c) => !stored.some((s) => s.chain.join() === c.chain.join()));
    side.innerHTML = `<h3 style="margin-top:0">Dialect chains found now <span class="muted" style="font-weight:normal">(${stored.length})</span></h3>
      ${stored.map((c) => chainCard(S, c, i, true)).join('') || '<p class="muted">none</p>'}
      <h3>Chains ${i === S.ix.frames.length - 1 ? 'now' : 'at ' + esc(ago(S.ix.frames[i]))} <span class="muted" style="font-weight:normal">(the same search at this frame: ${found.length})</span></h3>
      ${found.slice(0, 12).map((c) => chainCard(S, c, i, false)).join('') || '<p class="muted">none at this frame</p>'}`;
    side.querySelectorAll('.chain').forEach((d) => (d.onclick = (e) => {
      if (e.target.closest('[data-lect]')) return;
      const ch = d.dataset.chain.split(',');
      st.chain = st.chain && st.chain.join() === ch.join() ? null : ch;
      V.TABS.continuum.frame(el, S);
    }));
  }
  function drawMatrix(S, box) {
    const i = S.f, kyr = S.ix.frames[i], l = S.ix.by.get(S.sel);
    if (!l) { box.innerHTML = '<p class="muted">pick a lect</p>'; return; }
    const keyOf = (sc) => (sc === 'people' ? (x) => x.people === l.people : sc === 'family' ? (x) => x.family_true === l.family_true
      : (x) => (l.language ? x.language === l.language : x.family_true === l.family_true));
    let mem = S.doc.lects.filter((x) => x.deme != null && LC.alive(x, kyr) && keyOf(st.scope)(x));
    let fell = '';
    if (mem.length < 2 && st.scope === 'language') { mem = S.doc.lects.filter((x) => x.deme != null && LC.alive(x, kyr) && keyOf('family')(x)); fell = 'its language has one lect then, so its true family: '; }
    const MAX = 80;
    let note = '';
    if (mem.length > MAX) {  // (the picked lect's best-understood companions)
      mem.sort((a, b) => (S.ix.intelAt(S.sel, b.id, i) ?? -1) - (S.ix.intelAt(S.sel, a.id, i) ?? -1));
      note = ` (the ${MAX} that understand ${S.sel} best of ${mem.length})`;
      mem = mem.slice(0, MAX);
    }
    if (mem.length < 2) { box.innerHTML = `<p class="muted">fewer than two lects of this ${st.scope} spoken ${ago(kyr)}${l.language ? '' : ' (dead lects carry no language id: try the true family)'}.</p>`; return; }
    mem.sort((a, b) => ((S.demes.get(a.deme) || {}).lon ?? 0) - ((S.demes.get(b.deme) || {}).lon ?? 0));
    const n = mem.length, cs = Math.max(6, Math.min(16, Math.floor(560 / n))), LAB = 150;
    const Wd = LAB + n * cs + 4, Hh = LAB * 0 + n * cs + 4;
    const cells = [];
    for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) {
      const v = a === b ? 1 : S.ix.intelAt(mem[a].id, mem[b].id, i);
      cells.push(`<rect x="${LAB + b * cs}" y="${a * cs}" width="${cs - 1}" height="${cs - 1}" fill="${LC.intelRamp(v)}"><title>${esc(mem[a].id)} ↔ ${esc(mem[b].id)}: ${v == null ? 'not measured' : v.toFixed(2)}</title></rect>`);
    }
    const labs = mem.map((x, a) => `<text x="${LAB - 4}" y="${a * cs + cs - 3}" text-anchor="end" style="font-size:${Math.min(11, cs)}px;${x.id === S.sel ? 'font-weight:700' : ''}" data-lect="${esc(x.id)}">${esc(V.lectShort(x.id))}</text>`).join('');
    box.innerHTML = `<div class="muted" style="font-size:11px;margin-bottom:4px">${fell}${n} lects spoken ${esc(ago(kyr))}, west to east${note}; grey: never measured (not neighbours)</div>
      <div style="overflow:auto;max-height:640px"><svg width="${Wd}" height="${Hh}">${labs}${cells.join('')}</svg></div>`;
  }
})();
