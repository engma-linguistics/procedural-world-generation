'use strict';
// The languages viewer (viewer/languages.html; the data: a peoples run's languages.json from planet/language/output.py, with the
// run's run.json for the peoples' names and colours and demes.json for where each deme lived). This file: the page (run picker,
// loading, the shared selection and time, hash routing #<tab>/sel=<lect>&f=<frame>&p=<people>, audio buttons) and the
// Families tab. The other tabs: langtime.js (a language over time), langmap.js (continuum and intelligibility), langmore.js
// (names, food words and shifts, checks and voices). Pure helpers: langcore.js (LangCore).
(() => {
  const LC = globalThis.LangCore;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ago = (k) => (k == null ? '?' : k <= 0 ? 'now' : NumFmt.kyr(k) + ' ago');
  const TABS = {};
  const S = { runId: null, doc: null, ix: null, meta: null, demes: new Map(), demePairs: new Map(), peoples: new Map(), sel: null, f: 0, people: null, tab: 'families', audio: null, prevF: null };

  // ------------------------------------------------------------------ labels and colours
  const lect = (id) => S.ix && S.ix.by.get(id);
  function demeOf(id) { const l = lect(id); return l && l.deme != null ? S.demes.get(l.deme) : null; }
  function lectShort(id) {
    const l = lect(id);
    if (!l) return String(id);
    if (l.deme == null) return `proto-${peopleName(l.people)} ${l.id}`;
    const d = S.demes.get(l.deme);
    return `${l.id} · ${d ? d.short : (l.deme_name || 'deme ' + l.deme).replace(/ \(.*\)$/, '')}`;
  }
  function lectLabel(id) {
    const l = lect(id);
    if (!l) return String(id);
    if (l.deme == null) return `proto-language ${l.id} of the ${peopleName(l.people)}`;
    const d = S.demes.get(l.deme);
    return `${l.id} · ${d ? d.name : l.deme_name || 'deme ' + l.deme}`;
  }
  function peopleName(p) { const x = S.peoples.get(p); return x ? x.short : String(p); }
  function peopleColor(p) { const x = S.peoples.get(p); return (x && x.color) || '#8b97a8'; }
  function langColor(id) { const l = lect(id); return LC.hue((l && (l.language || l.family_true)) || id); }
  const lk = (id, text) => `<span class="lk" data-lect="${esc(id)}" title="${esc(lectLabel(id))}">${esc(text ?? lectShort(id))}</span>`;
  const sw = (c) => `<span class="sw" style="background:${c}"></span>`;
  // a play button: a word, or with o.sentence a whole sentence (word gaps and phrase intonation; o.q a yes/no question);
  // o.label puts text beside the triangle (the header's "hear a sample")
  const say = (ipa, people, o = {}) => (ipa ? `<button class="say${o.label ? ' lab' : ''}" data-ipa="${esc(ipa)}" data-people="${esc(people || '')}"${o.sentence ? ' data-sentence="1"' : ''}${o.q ? ' data-q="1"' : ''} title="${esc(o.title || (o.sentence ? 'hear the sentence' : 'hear it') + ' (voice: the picker at the top right; a non-human people gets its species\' effects)')}">&#9654;${o.label ? ' ' + esc(o.label) : ''}</button>` : '');

  // ------------------------------------------------------------------ audio (GET /api/speak; no backend hides every button)
  // The voice picker (header) chooses the backend, remembered in this browser; /api/speak/backends says which exist.
  const audioCache = new Map();
  const VOICE_KEY = 'lang.voice';
  let current = null;   // { audio, button } while something plays
  function voice() { try { return localStorage.getItem(VOICE_KEY) || 'auto'; } catch (e) { return 'auto'; } }
  function setVoice(v) { try { localStorage.setItem(VOICE_KEY, v); } catch (e) { /* (private window: not remembered) */ } }
  function audioState(text, cls) { const el = $('audioState'); if (el) { el.textContent = text; el.className = 'muted ' + (cls || ''); } }
  function probeAudio() {
    const sel = $('voice');
    fetch('../api/speak/backends').then((r) => (r.ok ? r.json() : { backends: [] })).then((info) => {
      const have = info.backends || [];
      S.audio = have.length > 0;
      document.body.classList.toggle('noaudio', !S.audio);
      if (!sel) return;
      for (const o of sel.options) { o.disabled = o.value !== 'auto' && !have.includes(o.value); }
      const autoOpt = sel.querySelector('option[value=auto]');
      if (autoOpt) autoOpt.textContent = `best (${info.default || 'none'})`;
      let v = voice();
      if (v !== 'auto' && !have.includes(v)) v = 'auto';
      sel.value = v;
      audioState(S.audio ? 'ready' : 'audio unavailable on this server', S.audio ? '' : 'err');
    }).catch(() => { S.audio = false; document.body.classList.add('noaudio'); audioState('audio unavailable', 'err'); });
    if (sel) sel.onchange = () => { setVoice(sel.value); audioState(`voice: ${sel.value === 'auto' ? 'best available' : sel.value}`); };
  }
  function speakUrl(b) {
    const l = S.ix && S.sel ? S.ix.by.get(S.sel) : null;
    const stress = b.dataset.stress || (l && l.inventory && l.inventory.stress) || '';
    return LC.speakUrl('../api/speak', b.dataset.ipa, b.dataset.people, { backend: voice(), sentence: !!b.dataset.sentence, q: !!b.dataset.q, stress });
  }
  function stop() {
    if (current) { current.audio.pause(); current.button.classList.remove('playing'); current = null; }
  }
  // play one button's sound; resolves when it ends (or fails), so "play all" can chain
  function playButton(b) {
    return new Promise((resolve) => {
      const url = speakUrl(b);
      const go = (u) => {
        stop();
        const a = new Audio(u);
        current = { audio: a, button: b };
        b.classList.add('playing');
        audioState('playing…', 'on');
        const end = () => { b.classList.remove('playing'); if (current && current.audio === a) { current = null; audioState('ready'); } resolve(true); };
        a.onended = end; a.onerror = end;
        a.play().catch(end);
      };
      if (audioCache.has(url)) return go(audioCache.get(url));
      b.classList.add('busy');
      audioState('making the sound…', 'on');
      fetch(url)
        .then((r) => { if (r.status === 503) { document.body.classList.add('noaudio'); throw new Error('no audio backend'); } if (!r.ok) return r.json().then((j) => { throw new Error(j.error || r.status); }, () => { throw new Error(r.status); }); return r.blob(); })
        .then((bl) => { const u = URL.createObjectURL(bl); audioCache.set(url, u); b.classList.remove('busy'); go(u); })
        .catch((err) => { b.classList.remove('busy'); b.classList.add('err'); b.title = `could not say this: ${err.message}`; audioState('could not say that: ' + err.message, 'err'); resolve(false); });
    });
  }
  // play buttons one after another (a "play all"); a second click stops
  let chain = null;
  async function playAll(buttons, ctl) {
    if (chain) { chain.stop = true; stop(); return; }
    chain = { stop: false };
    if (ctl) ctl.classList.add('playing');
    for (const b of buttons) { if (chain.stop) break; await playButton(b); await new Promise((r) => setTimeout(r, 350)); }
    if (ctl) ctl.classList.remove('playing');
    chain = null;
  }
  document.addEventListener('click', (e) => {
    const b = e.target.closest('.say');
    if (b) {
      e.stopPropagation();
      if (current && current.button === b) { stop(); audioState('ready'); return; }
      playButton(b);
      return;
    }
    const pa = e.target.closest('[data-playall]');
    if (pa) {
      e.stopPropagation();
      const box = document.getElementById(pa.dataset.playall) || pa.closest('.tab');
      playAll([...box.querySelectorAll('.say[data-sentence]')], pa);
      return;
    }
    const a = e.target.closest('[data-lect]');
    if (a && !e.target.closest('.tw')) { e.preventDefault(); select(a.dataset.lect); return; }
    const t = e.target.closest('[data-gotab]');
    if (t) { e.preventDefault(); setTab(t.dataset.gotab); }
  });

  // ------------------------------------------------------------------ state, hash
  function writeHash() {
    const q = new URLSearchParams();
    if (S.sel) q.set('sel', S.sel);
    if (S.ix) q.set('f', S.f);
    if (S.people) q.set('p', S.people);
    const extra = TABS[S.tab] && TABS[S.tab].hash ? TABS[S.tab].hash() : '';
    history.replaceState(null, '', `${location.pathname}${location.search}#${S.tab}/${q.toString()}${extra ? '&' + extra : ''}`);
  }
  function readHash() {
    const [t, rest] = (location.hash || '').slice(1).split('/');
    if (t && TABS[t]) S.tab = t;
    const q = new URLSearchParams(rest || '');
    return q;
  }
  function select(id) {
    if (!S.ix || !S.ix.by.has(id)) return;
    S.sel = id;
    const l = lect(id);
    if (l && l.people) S.people = l.people;
    lectBar(); writeHash(); draw();
  }
  function setFrame(i) {
    if (!S.ix) return;
    i = Math.max(0, Math.min(S.ix.frames.length - 1, i | 0));
    if (i === S.f) return;
    S.prevF = S.f; S.f = i;
    for (const el of document.querySelectorAll('.scrub input[type=range]')) el.value = i;
    for (const el of document.querySelectorAll('.scrub .when')) el.textContent = ago(S.ix.frames[i]);
    writeHash();
    const T = TABS[S.tab];
    if (T && T.frame) T.frame($('tab-' + S.tab), S); else draw();
  }
  function setTab(t) {
    if (!TABS[t]) return;
    S.tab = t;
    for (const b of document.querySelectorAll('#tabs button')) b.classList.toggle('on', b.dataset.tab === t);
    for (const s of document.querySelectorAll('.tab')) s.classList.toggle('on', s.id === 'tab-' + t);
    $('foot').textContent = (TABS[t] && TABS[t].foot) || '';
    writeHash(); draw();
  }
  function draw() {
    const T = TABS[S.tab];
    if (!S.ix || !T) return;
    const t0 = performance.now();
    try { T.draw($('tab-' + S.tab), S); } catch (e) { $('tab-' + S.tab).innerHTML = `<p class="err">could not draw this tab: ${esc(e.message)}</p>`; console.error(e); }
    S.lastDrawMs = Math.round(performance.now() - t0);
  }
  function lectBar() {
    const el = $('lectbar'), l = lect(S.sel);
    if (!l) { el.innerHTML = '<span class="muted">pick a lect in any tab (click a tree line, a dot on the map or a name)</span>'; return; }
    const lang = l.language ? (S.doc.families.languages || []).find((x) => x.id === l.language) : null;
    const how = { proto: l.deme == null ? 'a proto-language' : 'first to speak', bud: 'budded off', shift: 'took over the speech of', arrival: 'arrived with settlers from' }[l.how] || l.how;
    el.innerHTML = `${sw(peopleColor(l.people))}<b>${esc(lectLabel(l.id))}</b>
      <span><span class="k">people</span> ${esc(peopleName(l.people))}</span>
      ${lang ? `<span><span class="k">language</span> ${sw(langColor(l.id))}${esc(lang.name)} (${lang.lects.length} lect${lang.lects.length > 1 ? 's' : ''})</span>` : ''}
      <span><span class="k">true family</span> ${esc(l.family_true || '–')}</span>
      ${l.family_scholars ? `<span><span class="k">scholars' family</span> ${esc(l.family_scholars)}</span>` : ''}
      <span><span class="k">from</span> ${ago(l.born_kyr)}${l.parent ? `, ${how} ${lk(l.parent)}` : ''}${l.substrate ? `, over ${lk(l.substrate)} (substrate)` : ''}</span>
      <span>${l.died_kyr == null ? '<span class="ok">spoken now</span>' : `<span class="muted">${esc(l.end || 'ended')} ${ago(l.died_kyr)}</span>`}</span>
      ${l.population ? `<span><span class="k">speakers</span> ~${NumFmt.count(l.population)}</span>` : ''}
      ${sampleButton(l)}`;
  }
  // the lect's short sample for the header: its first sample sentence, else its word for 'person' (or the first word it has)
  function sampleButton(l) {
    const s = (l.sentences || [])[0];
    if (s) return say(s.ipa, l.people, { sentence: true, q: s.q, label: 'hear a sample', title: `hear a sample: ‘${s.en}’ (${s.ipa})` });
    const lex = l.lexicon || {};
    const c = ['PERSON', 'PEOPLE', 'WATER'].find((k) => lex[k]) || Object.keys(lex)[0];
    return c ? say(lex[c].ipa, l.people, { label: 'hear a word', title: `hear its word for ‘${c.toLowerCase()}’ (${lex[c].ipa})` }) : '';
  }
  // a time scrubber over the frames, bound to the shared frame (S.f); ▶ plays from the oldest frame to now
  let player = null;
  function scrubber() {
    const n = S.ix.frames.length;
    const div = document.createElement('div');
    div.className = 'scrub';
    div.innerHTML = `<button class="play" title="play from ${esc(ago(S.ix.frames[0]))} to now">${player ? '&#10073;&#10073;' : '&#9654;'}</button>
      <button class="prev" title="one frame older">&#8249;</button><button class="next" title="one frame younger">&#8250;</button>
      <span class="muted">${esc(ago(S.ix.frames[0]))}</span><input type="range" min="0" max="${n - 1}" step="1" value="${S.f}"><span class="muted">now</span>
      <b class="when">${esc(ago(S.ix.frames[S.f]))}</b>`;
    div.querySelector('input').oninput = (e) => setFrame(+e.target.value);
    div.querySelector('.prev').onclick = () => setFrame(S.f - 1);
    div.querySelector('.next').onclick = () => setFrame(S.f + 1);
    div.querySelector('.play').onclick = () => {
      if (player) { clearInterval(player); player = null; for (const b of document.querySelectorAll('.scrub .play')) b.innerHTML = '&#9654;'; return; }
      if (S.f >= n - 1) setFrame(0);
      for (const b of document.querySelectorAll('.scrub .play')) b.innerHTML = '&#10073;&#10073;';
      player = setInterval(() => { if (S.f >= n - 1) { clearInterval(player); player = null; for (const b of document.querySelectorAll('.scrub .play')) b.innerHTML = '&#9654;'; return; } setFrame(S.f + 1); }, 450);
    };
    return div;
  }

  // ------------------------------------------------------------------ loading
  async function getJSON(url, onProgress) {
    const r = await fetch(url, { cache: 'no-store' });
    if (!r.ok) { const e = new Error(`${r.status} ${url}`); e.status = r.status; throw e; }
    const total = +r.headers.get('Content-Length') || 0;
    if (!onProgress || !r.body || !r.body.getReader) return r.json();
    const rd = r.body.getReader(), parts = [];
    let got = 0;
    for (;;) { const { done, value } = await rd.read(); if (done) break; parts.push(value); got += value.length; onProgress(got, total); }
    const buf = new Uint8Array(got);
    let o = 0;
    for (const p of parts) { buf.set(p, o); o += p.length; }
    return JSON.parse(new TextDecoder().decode(buf));
  }
  function loading(msg, frac) {
    const el = $('loading');
    el.style.display = msg == null ? 'none' : 'flex';
    if (msg != null) { $('loadMsg').textContent = msg; $('loadBar').value = frac || 0; $('loadBar').style.visibility = frac == null ? 'hidden' : 'visible'; }
  }
  async function listRuns(want) {
    let runs = [];
    try { runs = await getJSON('../runs/index.json'); } catch (e) { runs = []; }
    const pr = runs.filter((r) => r.kind === 'peoples').sort((a, b) => (b.created || '').localeCompare(a.created || ''));
    if (want && !pr.some((r) => r.dir === want)) pr.unshift({ dir: want, name: '' });
    $('run').innerHTML = pr.map((r) => `<option value="${esc(r.dir)}">${esc(r.dir)} · ${esc(r.name || '')}${r.world ? ' · ' + esc(r.world) : ''}</option>`).join('') || '<option value="">(no peoples runs)</option>';
    return pr;
  }
  async function load(id) {
    S.runId = id; S.doc = null; S.ix = null;
    $('run').value = id;
    $('toWorkbench').href = `lineages.html?run=${encodeURIComponent(id)}`;
    for (const s of document.querySelectorAll('.tab')) s.innerHTML = '';
    loading(`loading the run ${id}…`, null);
    try {
      const run = await getJSON(`../runs/${id}/run.json`);
      S.meta = run.meta || {};
      S.peoples = new Map((S.meta.lineages || []).map((l) => [l.id, { name: l.name || l.id, short: (l.name || l.id).replace(/ \(.*$/, ''), color: l.color }]));
      S.demes = new Map(); S.demePairs = new Map();
      try {
        const dd = await getJSON(`../runs/${id}/${(S.meta.demes && S.meta.demes.file) || 'demes.json'}`);
        for (const d of dd.demes || []) S.demes.set(d.id, d);
        for (const p of dd.pairs || []) S.demePairs.set(p.a < p.b ? p.a + '|' + p.b : p.b + '|' + p.a, p);
      } catch (e) { /* (no demes: lects keep their deme_name, the map has no dots) */ }
      const file = (S.meta.languages && S.meta.languages.file) || 'languages.json';
      const t0 = performance.now();
      let doc = await getJSON(`../runs/${id}/${file}`, (got, tot) => loading(`loading ${file}: ${(got / 1e6).toFixed(0)} MB${tot ? ' of ' + Math.round(tot / 1e6) + ' MB' : ''}`, tot ? got / tot : null));
      if (doc.format === LC.FORMAT2) {  // (format /2: the etymologies and the snapshots sit in two sidecar files beside it)
        loading('loading the etymologies and the snapshots…', null);
        const [etym, snapshots] = await Promise.all(['etym', 'snapshots'].map((k) => getJSON(`../runs/${id}/${LC.sidecarName(file, k)}`).catch(() => null)));
        doc = LC.expand(doc, { etym, snapshots });
      }
      loading('reading the languages…', 1);
      await new Promise((r) => setTimeout(r, 0));
      S.doc = doc; S.ix = LC.index(doc);
      S.loadMs = Math.round(performance.now() - t0);
      const q = readHash();
      S.f = q.has('f') ? Math.max(0, Math.min(S.ix.frames.length - 1, +q.get('f'))) : S.ix.frames.length - 1;
      S.prevF = null;
      S.sel = q.get('sel') && S.ix.by.has(q.get('sel')) ? q.get('sel') : defaultLect();
      S.people = q.get('p') || (lect(S.sel) && lect(S.sel).people) || null;
      for (const T of Object.values(TABS)) if (T.reset) T.reset(S, q);
      findList();
      $('status').textContent = `${doc.lects.length} lects, ${S.ix.living.length} spoken now, ${S.ix.frames.length} frames from ${ago(S.ix.frames[0])}`;
      loading(null);
      lectBar(); setTab(S.tab);
    } catch (e) {
      loading(e.status === 404 ? `This run has no languages yet (no ${id}/languages.json). Pick another run above.` : `Could not load the run: ${e.message}`, null);
      $('status').textContent = '';
    }
  }
  function defaultLect() {  // the most spoken living human lect, else the most spoken living lect
    let best = null;
    for (const id of S.ix.living) {
      const l = lect(id), sc = (l.population || 0) * (l.people === 'human' ? 10 : 1);
      if (!best || sc > best[0]) best = [sc, id];
    }
    return best ? best[1] : (S.doc.lects[0] || {}).id;
  }
  function findList() {
    const opts = [];
    for (const l of S.doc.lects) if (l.died_kyr == null) opts.push(`<option value="${esc(l.id)}">${esc(lectLabel(l.id))} (${esc(peopleName(l.people))})</option>`);
    $('findList').innerHTML = opts.join('');
  }
  $('find').addEventListener('change', (e) => {
    const v = e.target.value.trim();
    if (!S.ix) return;
    let id = S.ix.by.has(v) ? v : null;
    if (!id) {
      const lo = v.toLowerCase();
      const hit = S.doc.lects.find((l) => l.died_kyr == null && (lectLabel(l.id).toLowerCase().includes(lo) || String(l.people).toLowerCase() === lo));
      id = hit && hit.id;
    }
    if (id) { select(id); e.target.value = ''; }
  });

  async function start() {
    probeAudio();
    const q = new URLSearchParams(location.search);
    readHash();
    for (const b of document.querySelectorAll('#tabs button')) b.onclick = () => setTab(b.dataset.tab);
    const want = q.get('run');
    const runs = await listRuns(want);
    $('run').onchange = (e) => { const u = new URL(location.href); u.searchParams.set('run', e.target.value); history.replaceState(null, '', u); load(e.target.value); };
    const first = want || (runs.find((r) => r.dir === 'a24559') || runs[0] || {}).dir;
    if (first) load(first); else loading('No peoples runs yet.', null);
  }

  // ================================================================== tab 1: Families
  const FAM = { living: false, dead: true, collapsed: new Set(), people: '' };
  const ROW = 14;
  TABS.families = {
    foot: 'Left: what really happened (every lect from its proto-language, solid lines budding, dashed lines a place that took over another people\'s speech, faded lines no longer spoken; the band is where scholars should stop seeing kinship, 6-10 kyr). Right: the tree a linguist would draw from the words alone. Click any line to pick a lect.',
    reset() { FAM.collapsed = new Set(); },
    hash() { return FAM.people ? 'fp=' + encodeURIComponent(FAM.people) : ''; },
    draw(el) {
      const ix = S.ix, doc = S.doc, fam = doc.families || {};
      const peoples = [...new Set(doc.lects.map((l) => l.people))].sort();
      const counts = {};
      for (const l of doc.lects) counts[l.people] = (counts[l.people] || 0) + 1;
      const hz = fam.horizon_kyr, hzH = fam.horizon_by && fam.horizon_by.human && fam.horizon_by.human.horizon_kyr;
      el.style.display = '';
      el.innerHTML = `<div class="row" style="margin-bottom:6px">
          <span class="muted">people</span><select id="fmPeople"><option value="">all peoples (${doc.lects.length} lects)</option>${peoples.map((p) => `<option value="${esc(p)}" ${p === FAM.people ? 'selected' : ''}>${esc(peopleName(p))} (${counts[p]})</option>`).join('')}</select>
          <label class="muted"><input type="checkbox" id="fmDead" ${FAM.dead ? 'checked' : ''}> lects no longer spoken (faded)</label>
          <button id="fmCollapse" title="Fold every proto-language's tree into one line">fold to proto-languages</button><button id="fmExpand">unfold all</button>
          <span class="muted" style="margin-left:12px"><svg width="150" height="10"><line x1="0" y1="5" x2="30" y2="5" stroke="#aaa" stroke-width="2"/><text x="34" y="9" class="m">budded</text><line x1="78" y1="5" x2="108" y2="5" stroke="#aaa" stroke-width="2" stroke-dasharray="5 3"/><text x="112" y="9" class="m">shift</text></svg></span>
          <span class="muted">scholars' horizon: measured <b>${hz == null ? '–' : NumFmt.kyr(hz)}</b>${hzH != null ? ` (human lects ${NumFmt.kyr(hzH)})` : ''}, target 6-10 kyr · ${fam.true_families ?? '?'} true families, ${fam.scholars_families ?? '?'} the scholars would see</span>
        </div>
        <div id="fmPanes" style="display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:10px;height:calc(100% - 34px)">
          <div class="card" style="overflow:auto;padding:0;position:relative" id="fmTrue"></div>
          <div class="card" style="overflow:auto;padding:0;position:relative" id="fmSch"></div>
        </div>`;
      $('fmPeople').onchange = (e) => { FAM.people = e.target.value; writeHash(); draw(); };
      $('fmDead').onchange = (e) => { FAM.dead = e.target.checked; draw(); };
      $('fmCollapse').onclick = () => { FAM.collapsed = new Set(doc.lects.filter((l) => l.parent == null).map((l) => l.id)); draw(); };
      $('fmExpand').onclick = () => { FAM.collapsed = new Set(); draw(); };
      drawTrue($('fmTrue'));
      drawScholars($('fmSch'));
    },
  };
  function drawTrue(box) {
    const ix = S.ix, fam = S.doc.families || {};
    const keepP = FAM.people ? (l) => l.people === FAM.people : null;
    const keep = (l) => (!keepP || keepP(l)) && (FAM.dead || l.died_kyr == null);
    // (the selected lect's line of descent is always unfolded)
    const col = new Set(FAM.collapsed);
    for (const a of LC.ancestry(ix, S.sel)) col.delete(a.id);
    const T = LC.layoutTree(ix, { collapsed: col, keep });
    const W = Math.max(560, box.clientWidth - 2), LAB = 190, L = 16, top = 30;
    const t0 = ix.frames.length ? Math.max(...ix.frames) : 20;
    const x = (k) => L + (t0 - k) / t0 * (W - L - LAB);
    const H = top + T.rows.length * ROW + 10;
    const y = (r) => top + r * ROW + ROW / 2;
    const hz = fam.horizon_kyr;
    const parts = [];
    parts.push(`<rect x="${x(10)}" y="0" width="${x(6) - x(10)}" height="${H}" fill="#7cc4ff" opacity="0.07"/>`);
    parts.push(`<text x="${(x(10) + x(6)) / 2}" y="24" text-anchor="middle" class="m">target horizon 6-10 kyr</text>`);
    if (hz != null) {
      const hx = x(Math.min(hz, t0));
      parts.push(`<line x1="${hx}" y1="0" x2="${hx}" y2="${H}" stroke="#ffc940" stroke-dasharray="4 3" opacity="0.8"/><text x="${hx + 3}" y="24" class="m" fill="#ffc940">measured ${NumFmt.kyr(hz)}${hz > t0 ? ' (older than the window)' : ''}</text>`);
    }
    for (let k = 0; k <= t0; k += 2) parts.push(`<line x1="${x(k)}" y1="${top - 4}" x2="${x(k)}" y2="${H}" stroke="#2a3446" stroke-width="0.5"/><text x="${x(k)}" y="11" text-anchor="middle" class="m">${k ? k + ' kyr' : 'now'}</text>`);
    const dash = (how) => (how === 'shift' ? ' stroke-dasharray="5 3"' : how === 'arrival' ? ' stroke-dasharray="1 3"' : '');
    for (const lnk of T.links) {
      const r = T.rowOf.get(lnk.to), c = peopleColor(r.people);
      parts.push(`<path d="M${x(lnk.x)},${y(lnk.y0)}V${y(lnk.y1)}" stroke="${c}" fill="none" stroke-width="1"${dash(lnk.how)} opacity="${r.dead ? 0.3 : 0.75}"/>`);
    }
    const selLine = new Set(LC.ancestry(ix, S.sel).map((l) => l.id));
    for (const r of T.rows) {
      const l = ix.by.get(r.id), c = peopleColor(r.people), yy = y(r.y), sel = r.id === S.sel;
      const op = r.dead ? 0.35 : 1;
      if (sel) parts.push(`<rect x="0" y="${yy - ROW / 2}" width="${W}" height="${ROW}" fill="#223652"/>`);
      parts.push(`<g data-lect="${esc(r.id)}" style="cursor:pointer" opacity="${op}"><rect x="${x(r.x0) - 2}" y="${yy - ROW / 2}" width="${Math.max(8, x(r.x1) - x(r.x0) + LAB)}" height="${ROW}" fill="transparent"/>`
        + `<line x1="${x(r.x0)}" y1="${yy}" x2="${Math.max(x(r.x1), x(r.x0) + 2)}" y2="${yy}" stroke="${c}" stroke-width="${selLine.has(r.id) ? 3 : 2}"${dash(r.how === 'proto' ? '' : r.how)}/>`
        + `<text x="${Math.max(x(r.x1), x(r.x0) + 2) + 4}" y="${yy + 4}"${r.dead ? ' class="m"' : ''}>${esc(lectShort(r.id))}${r.collapsed ? ` <tspan class="m">+${r.desc}</tspan>` : ''}</text></g>`);
      if (r.kids) parts.push(`<text x="${x(r.x0) - 11}" y="${yy + 4}" class="m tw" data-tw="${esc(r.id)}" style="cursor:pointer" title="fold or unfold">${r.collapsed ? '▸' : '▾'}</text>`);
    }
    // the selected lect's substrate: a dotted line to the lect its place spoke before
    const sl = ix.by.get(S.sel);
    if (sl && sl.substrate && T.rowOf.has(sl.substrate) && T.rowOf.has(sl.id)) {
      const a = T.rowOf.get(sl.substrate), b = T.rowOf.get(sl.id);
      parts.push(`<path d="M${x(sl.born_kyr)},${y(a.y)}V${y(b.y)}" stroke="#ffc940" stroke-dasharray="2 2" fill="none"/>`);
    }
    box.innerHTML = `<div style="position:sticky;top:0;background:var(--panel);padding:4px 8px;border-bottom:1px solid var(--line);z-index:2"><b>True tree</b> <span class="muted">what happened: ${T.rows.length} lects, time left to right</span></div>
      <svg width="${W}" height="${H}" style="display:block">${parts.join('')}</svg>`;
    box.querySelectorAll('[data-tw]').forEach((t) => t.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = t.dataset.tw;
      if (FAM.collapsed.has(id) || col.has(id)) FAM.collapsed.delete(id); else FAM.collapsed.add(id);
      draw();
    }));
    const r = T.rowOf.get(S.sel);
    if (r) scrollTo(box, top + r.y * ROW);
  }
  function scrollTo(box, py) {
    if (py < box.scrollTop + 40 || py > box.scrollTop + box.clientHeight - 40) box.scrollTop = Math.max(0, py - box.clientHeight / 2);
  }
  function drawScholars(box) {
    const ix = S.ix, fam = S.doc.families || {};
    const keep = FAM.people ? (id) => ix.by.get(id) && ix.by.get(id).people === FAM.people : null;
    const D = LC.layoutDendro(fam.scholars || [], keep);
    const W = Math.max(480, box.clientWidth - 2), LAB = 250, L = 10, top = 30;
    const maxD = Math.max(1, ...D.nodes.map((n) => n.x));
    const x = (d) => L + (maxD - d) / maxD * (W - L - LAB);
    const y = (r) => top + r * ROW + ROW / 2;
    const H = top + D.leaves.length * ROW + 10;
    const parts = [];
    const floor = fam.chance && fam.chance.floor, ls = fam.lang_share;
    if (floor != null) parts.push(`<line x1="${x(1 - floor)}" y1="0" x2="${x(1 - floor)}" y2="${H}" stroke="#ffc940" stroke-dasharray="4 3" opacity="0.7"/><text x="${x(1 - floor) + 3}" y="24" class="m">chance: no kinship visible</text>`);
    if (ls != null) parts.push(`<line x1="${x(1 - ls)}" y1="0" x2="${x(1 - ls)}" y2="${H}" stroke="#7cc4ff" stroke-dasharray="4 3" opacity="0.6"/><text x="${x(1 - ls) + 3}" y="24" class="m">one language (share > ${ls})</text>`);
    for (let d = 0; d <= maxD + 1e-9; d += 0.2) parts.push(`<text x="${x(d)}" y="11" text-anchor="middle" class="m">${Math.round((1 - d) * 100)}%</text>`);
    parts.push(`<text x="${W - LAB + 4}" y="11" class="m">core words shared</text>`);
    const selLang = ix.by.get(S.sel) && ix.by.get(S.sel).language;
    const path = [];
    for (const n of D.nodes) {
      if (n.leaf != null) continue;
      const ys = n.kids.map((k) => D.nodes[k].y);
      path.push(`M${x(n.x)},${y(Math.min(...ys))}V${y(Math.max(...ys))}`);
      for (const k of n.kids) path.push(`M${x(n.x)},${y(D.nodes[k].y)}H${x(D.nodes[k].x)}`);
    }
    parts.push(`<path d="${path.join('')}" stroke="#6b7a90" fill="none" stroke-width="1"/>`);
    let selY = null;
    for (const n of D.nodes) {
      if (n.leaf == null) continue;
      const l = ix.by.get(n.leaf), yy = y(n.y), sel = n.leaf === S.sel, same = selLang && l && l.language === selLang;
      if (sel) { selY = n.y; parts.push(`<rect x="0" y="${yy - ROW / 2}" width="${W}" height="${ROW}" fill="#223652"/>`); }
      parts.push(`<g data-lect="${esc(n.leaf)}" style="cursor:pointer"><rect x="${x(0) - 4}" y="${yy - ROW / 2}" width="${LAB}" height="${ROW}" fill="transparent"/>`
        + `<rect x="${x(0) + 3}" y="${yy - 4}" width="8" height="8" rx="2" fill="${langColor(n.leaf)}"/>`
        + `<text x="${x(0) + 15}" y="${yy + 4}" style="${same ? 'font-weight:600' : ''}">${esc(lectShort(n.leaf))}</text></g>`);
    }
    box.innerHTML = `<div style="position:sticky;top:0;background:var(--panel);padding:4px 8px;border-bottom:1px solid var(--line);z-index:2"><b>Scholars' tree</b> <span class="muted">from the core words alone (UPGMA over ${D.leaves.length} lects spoken now); the swatch is the language</span></div>
      <svg width="${W}" height="${H}" style="display:block">${parts.join('')}</svg>`;
    if (selY != null) scrollTo(box, top + selY * ROW);
  }

  globalThis.LangView = { start, S, TABS, esc, ago, lect, demeOf, lectShort, lectLabel, peopleName, peopleColor, langColor, lk, sw, say, select, setFrame, setTab, draw, writeHash, scrubber, playAll, stop };
})();
