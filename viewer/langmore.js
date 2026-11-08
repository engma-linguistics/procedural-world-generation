'use strict';
// The languages viewer's last three tabs (languages.html; helpers in langcore.js, page in langview.js):
//   names    a people's names for itself (endonym, glossonym, the land / people / person / language set) and others' names for it
//            (exonyms), each with its etymology as a chain of forms; its demes' place and river names; any word's etymology
//   routes   food words: each word's route from deme to deme with the form at each hop; language shifts: each place that took
//            over another speech, with the trigger, the local words kept and the accent
//   checks   the pass's checks, the family numbers, and each species' voice profile
(() => {
  const V = globalThis.LangView, LC = globalThis.LangCore;
  const { esc, ago, lk, sw, say } = V;
  const CSS = `
.ety { border-left: 2px solid #3a475c; margin: 4px 0 4px 6px; padding-left: 10px; }
.ety .st { position: relative; padding: 3px 0 6px; }
.ety .st::before { content: ''; position: absolute; left: -15px; top: 9px; width: 8px; height: 8px; border-radius: 50%; background: var(--acc); }
.ety .st .ipa { font-size: 16px; }
.ety .pr { color: var(--muted); font-size: 12px; }
#tab-names .ngrid, #tab-checks .ngrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 10px; align-items: start; }
#tab-routes details { border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; margin-bottom: 6px; background: var(--panel); }
#tab-routes summary { cursor: pointer; }
.chipx { display: inline-block; padding: 0 5px; margin: 1px; border-radius: 3px; background: var(--ctl); font-size: 11px; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const demeName = (S, d) => { const x = S.demes.get(d); return x ? x.name : d == null ? '–' : 'deme ' + d; };
  const conceptText = (c) => { const m = String(c).match(/^(crop|animal|good|fuel):(.*)$/); return m ? `${m[2].replace(/_/g, ' ')} <span class="muted">(${m[1]})</span>` : esc(String(c).toLowerCase()); };

  function etymHtml(S, chain, people) {
    if (!chain || !chain.length) return '<span class="muted">no etymology stored</span>';
    return `<div class="ety">${chain.map((s, k) => `<div class="st"><span class="ipa">${esc(s.ipa)}</span>${say(s.ipa, people)}
      ${s.gloss && (k === 0 || s.gloss !== chain[k - 1].gloss) ? ` <span>‘${esc(String(s.gloss).toLowerCase())}’</span>` : ''}
      <div class="pr">${[s.kyr != null ? esc(ago(s.kyr)) : '', s.lect ? lk(s.lect, s.lect) : '', esc(procText(S, s.process))].filter(Boolean).join(' · ')}${s.note ? ` · ${esc(s.note)}` : ''}</div></div>`).join('')}</div>`;
  }
  // a step's process in plain words; a naming step (name:E2) also says what its pattern means (names.patterns)
  const patText = (S, k) => { const P = (S.doc.names && S.doc.names.patterns) || {}; return k && P[k] ? `${k}: ${P[k]}` : k || ''; };
  const procText = (S, p) => { const m = String(p || '').match(/^name:(.*)$/); return m ? `made into a name (${patText(S, m[1])})` : LC.processText(p); };
  // a romanized name: the readable spelling, the full one (with tone and length marks) on hover and beside it when it differs
  const rom = (n) => `<span class="rom" title="${esc(n.roman_full || n.roman || '')}">${esc(n.roman || '')}</span>${n.roman_full && n.roman_full !== n.roman ? ` <span class="muted" style="font-size:12px">(${esc(n.roman_full)})</span>` : ''}`;
  const chainOf = (S, x) => (x == null ? null : LC.etymChain(S.ix, x));
  // a word's root family, two ways: `roots` (what a speaker still feels) and `etym_roots` (what a historian reconstructs:
  // the family the word was made in, carried forward); each with the root (the document's `roots` table), its words in this
  // lect, and the concepts built on it across the living lects that keep it. A file without etym_roots says so.
  function rootView(S, sl, w, field, title, blurb) {
    if (!w || !Array.isArray(w[field])) return field === 'etym_roots' ? `<h3>${esc(title)}</h3><div class="muted">This run's file has no etym_roots (it predates them).</div>` : '';
    const r = w[field][0];
    if (!r) return '';
    const R = (S.doc.roots || {})[r] || {};
    const here = Object.entries((sl && sl.lexicon) || {}).filter(([, x]) => Array.isArray(x[field]) && x[field].includes(r)).map(([c]) => c).sort();
    const across = new Map();
    let lects = 0;
    for (const l of S.doc.lects) {
      if (l.died_kyr != null || l.deme == null) continue;
      let hit = false;
      for (const [c, x] of Object.entries(l.lexicon || {})) if (Array.isArray(x[field]) && x[field][0] === r) { across.set(c, (across.get(c) || 0) + 1); hit = true; }
      if (hit) lects++;
    }
    const fam = [...across.entries()].sort((a, b) => b[1] - a[1]);
    const c0 = String(r).split(':').slice(1).join(':').split('@')[0];
    return `<h3>${esc(title)}</h3><div class="muted" style="font-size:12px">${esc(blurb)}</div><div><span class="ipa">*${esc(R.ipa || '?')}</span> ‘${esc(String(R.gloss || R.concept || c0 || r).toLowerCase())}’
      <span class="muted">${R.lect ? 'in ' + lk(R.lect, R.lect) : ''}${R.kyr != null ? ', ' + esc(ago(R.kyr)) : ''} · ${esc(r)}</span></div>
      <div class="muted" style="margin-top:4px">in this lect: ${here.map((c) => conceptText(c)).join(', ') || '–'}</div>
      <div class="muted">across ${lects} living lects: ${fam.slice(0, 30).map(([c, n]) => `${conceptText(c)} (${n})`).join(', ')}</div>`;
  }
  function rootHtml(S, sl, w) {
    return rootView(S, sl, w, 'roots', 'The family a speaker feels', 'its root as speakers still hear it (a derivation or compound younger than 3 kyr whose parts are still in use)')
      + rootView(S, sl, w, 'etym_roots', 'The family a historian reconstructs', 'its root as it was when the word was made, however opaque it has become since');
  }

  // ================================================================== tab 4: names
  const NM = { concept: 'WATER' };
  V.TABS.names = {
    foot: 'Pick a people: its own name for itself and the names others gave it, each traced back step by step (the oldest form at the top, how it changed at each step below). Its places and rivers are named by whoever lived there first. At the bottom, trace any word of the picked lect.',
    hash() { return 'w=' + encodeURIComponent(NM.concept); },
    reset(S, q) { if (q.get('w')) NM.concept = q.get('w'); },
    draw(el, S) {
      const doc = S.doc, ix = S.ix;
      const living = {};
      for (const id of ix.living) { const p = ix.by.get(id).people; living[p] = (living[p] || 0) + 1; }
      const peoples = Object.keys(living).sort((a, b) => living[b] - living[a]);
      const p = S.people && living[S.people] ? S.people : peoples[0];
      const nm = (doc.names && doc.names.peoples && doc.names.peoples[p]) || null;
      const best = ix.living.map((id) => ix.by.get(id)).filter((l) => l.people === p).sort((a, b) => (b.population || 0) - (a.population || 0))[0];
      const nameCard = (title, n) => (n ? `<div class="card"><h3>${esc(title)}: ${rom(n)} <span class="ipa">/${esc(n.ipa || '')}/</span>${say(n.ipa, p)}</h3>
          <div class="muted" style="font-size:12px">${[n.gloss ? `‘${esc(n.gloss)}’` : '', n.pattern ? `pattern ${esc(patText(S, n.pattern))}` : '', n.how ? esc(n.how) : '', n.lect ? 'in ' + lk(n.lect) : '', n.basis ? esc(n.basis) : ''].filter(Boolean).join(' · ')}</div>
          ${n.plain ? `<div style="font-size:12px;margin-top:3px">${esc(n.plain)}</div>` : ''}
          ${n.etym != null ? etymHtml(S, chainOf(S, n.etym), p) : ''}</div>` : '');
      const common = doc.names && doc.names.common, inCommon = common && common.exonyms && common.exonyms[p];
      const scholars = Object.entries((doc.names && doc.names.scholars) || {}).filter(([, x]) => (x.lects || []).some((id) => (ix.by.get(id) || {}).people === p));
      let names;
      if (nm) {
        const set = nm.set || {};
        names = `<div class="ngrid">${nameCard('Their own name (endonym)', nm.endonym)}${nameCard('Name of their speech (glossonym)', nm.glossonym)}
          ${['land', 'people', 'person', 'language'].map((k) => nameCard(`The ${k}`, set[k])).join('')}
          ${inCommon ? nameCard(`In the Common (${V.peopleName(common.people)} ${common.lect}, ${common.why || 'the trade speech'})`, inCommon) : ''}</div>
          ${scholars.length ? `<details class="sec"><summary>The scholars' names for the families this people's lects fall in (${scholars.length})</summary><table class="t"><tr><th>family</th><th>name</th><th>why</th><th>pattern</th><th>lects</th><th>ended</th></tr>
            ${scholars.map(([id, x]) => `<tr><td class="muted">${esc(id)}</td><td>${rom(x)}</td><td style="font-size:12px">${esc(x.gloss || '')}</td><td>${esc(x.pattern || '')}</td><td style="font-size:11px">${(x.lects || []).slice(0, 12).map((l) => lk(l, l)).join(' ')}${(x.lects || []).length > 12 ? ' …' : ''}</td><td>${x.died_kyr != null ? esc(ago(x.died_kyr)) : '<span class="ok">spoken now</span>'}</td></tr>`).join('')}</table></details>` : ''}
          <h3>What others call them (exonyms)</h3>
          <table class="t"><tr><th>by</th><th>name</th><th>IPA</th><th>meaning</th><th>pattern</th><th>why</th><th>when</th><th>passed through</th><th></th></tr>
          ${(nm.exonyms || []).map((x, k) => `<tr><td>${sw(V.peopleColor(x.by_people))}${esc(V.peopleName(x.by_people))}${x.by_lect ? ' ' + lk(x.by_lect, x.by_lect) : ''}</td><td>${rom(x)}</td><td class="ipa">${esc(x.ipa || '')}${say(x.ipa, x.by_people)}</td>
            <td>${esc(x.gloss || '')}</td><td title="${esc(patText(S, x.pattern))}">${esc(x.pattern || '')}</td><td class="muted">${esc(x.basis || '')}</td><td>${x.era_kyr != null ? esc(ago(x.era_kyr)) : ''}</td>
            <td class="muted">${(x.relay || []).map((r) => esc(typeof r === 'string' ? r : r.lect || r.people || JSON.stringify(r))).join(' → ')}</td>
            <td>${x.etym != null ? `<span class="lk" data-ex="${k}">etymology</span>` : ''}</td></tr><tr class="exr" data-exr="${k}" hidden><td colspan="9">${x.etym != null ? etymHtml(S, chainOf(S, x.etym), x.by_people) : ''}</td></tr>`).join('') || '<tr><td colspan="9" class="muted">none recorded</td></tr>'}</table>`;
      } else {
        const lex = (best && best.lexicon) || {};
        const roots = ['PERSON', 'MAN', 'WOMAN', 'WE', 'NAME', 'EARTH (SOIL)', 'LAND', 'MOUNTAIN', 'RIVER', 'SPEAK', 'SAY'].filter((c) => lex[c]);
        names = `<p class="muted">The names of peoples, places and rivers are not in this file yet (${esc((doc.names && doc.names.note) || 'no names block')}). Meanwhile, the words such names grow from, in ${best ? lk(best.id) : 'its largest lect'}:</p>
          <div class="ngrid">${roots.map((c) => `<div class="card"><h3>${esc(c.toLowerCase())}: <span class="rom">${esc(lex[c].roman)}</span> <span class="ipa">/${esc(lex[c].ipa)}/</span>${say(lex[c].ipa, p)}</h3>${etymHtml(S, chainOf(S, lex[c].etym), p)}</div>`).join('')}</div>`;
      }
      // its demes: names, places, rivers
      const demes = [...new Set(ix.living.map((id) => ix.by.get(id)).filter((l) => l.people === p).map((l) => l.deme))].sort((a, b) => a - b);
      const nd = (doc.names && doc.names.demes) || {}, land = (doc.landscape && doc.landscape.demes) || {}, rivers = (doc.landscape && doc.landscape.rivers) || {};
      const riverDemes = {};
      for (const [rid, r] of Object.entries(rivers)) for (const [d] of r.demes || []) (riverDemes[d] = riverDemes[d] || []).push(rid);
      const drow = (d) => {
        const n = nd[d] || nd[String(d)], ls = land[String(d)] || {};
        const places = (n && n.places) || [];
        return `<tr><td>${esc(demeName(S, d))}</td><td>${n && n.name ? `${rom(n.name)} <span class="ipa">${esc(n.name.ipa || '')}</span>${say(n.name.ipa, p)}${n.name.gloss ? ` <span class="muted">‘${esc(n.name.gloss)}’</span>` : ''}` : '<span class="muted">–</span>'}</td>
          <td>${places.length ? places.map((x) => `<div>${esc(x.kind || '')}: ${rom(x)} <span class="ipa">${esc(x.ipa || '')}</span>${say(x.ipa, p)} <span class="muted">${x.gloss ? '‘' + esc(x.gloss) + '’ ' : ''}${x.lect ? 'from ' + esc(x.lect) : ''}${x.kyr != null ? ', ' + esc(ago(x.kyr)) : ''}${x.substrate_of ? ', kept from ' + esc(x.substrate_of) : ''}</span></div>`).join('')
            : `<span class="muted">${esc(ls.part || '')}${ls.river != null ? ` · river ${esc(ls.river)} (flow ${Math.round(ls.river_flow || 0)})` : ''}${ls.lake != null ? ` · lake ${esc(ls.lake)}` : ''}${ls.mountain_m ? ` · hills to ${Math.round(ls.mountain_m)} m` : ''}${ls.coast_share ? ` · ${Math.round(ls.coast_share * 100)}% coast` : ''}</span>`}</td></tr>`;
      };
      // any word's etymology in the picked lect
      const sl = ix.by.get(S.sel), slex = (sl && sl.lexicon) || {};
      const concepts = Object.keys(slex).sort();
      if (!slex[NM.concept]) NM.concept = concepts.includes('WATER') ? 'WATER' : concepts[0];
      const w = slex[NM.concept];
      el.innerHTML = `<div class="row" style="margin-bottom:8px"><span class="muted">people</span><select id="nmP">${peoples.map((x) => `<option value="${esc(x)}" ${x === p ? 'selected' : ''}>${esc(V.peopleName(x))} (${living[x]} lects)</option>`).join('')}</select></div>
        ${names}
        <h3>Its places now <span class="muted" style="font-weight:normal">(${demes.length} demes)</span></h3>
        <div style="max-height:360px;overflow:auto"><table class="t"><tr><th>deme</th><th>its name</th><th>places and rivers</th></tr>${demes.slice(0, 200).map(drow).join('')}</table></div>
        <h3>Trace a word of ${sl ? lk(sl.id) : 'the picked lect'}</h3>
        <div class="row"><select id="nmW">${concepts.map((c) => `<option ${c === NM.concept ? 'selected' : ''}>${esc(c)}</option>`).join('')}</select>
          ${w ? `<span class="rom">${esc(w.roman)}</span> <span class="ipa">/${esc(w.ipa)}/</span>${say(w.ipa, sl.people)} <span class="muted">${esc(w.pos || '')}</span>` : ''}</div>
        ${w ? etymHtml(S, chainOf(S, w.etym), sl.people) : ''}${w ? rootHtml(S, sl, w) : ''}`;
      el.querySelector('#nmP').onchange = (e) => { S.people = e.target.value; V.writeHash(); this.draw(el, S); };
      const ws = el.querySelector('#nmW'); if (ws) ws.onchange = (e) => { NM.concept = e.target.value; V.writeHash(); this.draw(el, S); };
      el.querySelectorAll('[data-ex]').forEach((a) => (a.onclick = () => { const r = el.querySelector(`[data-exr="${a.dataset.ex}"]`); r.hidden = !r.hidden; }));
    },
  };

  // ================================================================== tab 5: food words and shifts
  const RT = { view: 'food', concept: '', people: '', n: 40, kind: '' };
  V.TABS.routes = {
    foot: 'Food words: where each crop or animal word started and every hop it made from one place to the next, with the word as each place said it (and the sound changes it went through on the way). Shifts: places that gave up their own speech for a ruler\'s or a bigger neighbour\'s, the local words they kept and the sounds they kept saying their old way.',
    hash() { return `rv=${RT.view}`; },
    reset(S, q) { if (q.get('rv')) RT.view = q.get('rv'); RT.n = 40; },
    draw(el, S) {
      const doc = S.doc;
      const peoples = [...new Set(doc.lects.map((l) => l.people))].sort();
      const head = `<div class="row" style="margin-bottom:8px"><span class="seg" id="rtV"><button data-k="food" class="${RT.view === 'food' ? 'on' : ''}">Food words (${(doc.food_routes || []).length})</button><button data-k="shifts" class="${RT.view === 'shifts' ? 'on' : ''}">Language shifts (${(doc.shifts || []).length})</button></span>
        <span class="muted">people</span><select id="rtP"><option value="">all</option>${peoples.map((p) => `<option value="${esc(p)}" ${p === RT.people ? 'selected' : ''}>${esc(V.peopleName(p))}</option>`).join('')}</select><span id="rtX"></span></div><div id="rtBody"></div>`;
      el.innerHTML = head;
      el.querySelectorAll('#rtV button').forEach((b) => (b.onclick = () => { RT.view = b.dataset.k; RT.n = 40; V.writeHash(); this.draw(el, S); }));
      el.querySelector('#rtP').onchange = (e) => { RT.people = e.target.value; RT.n = 40; this.draw(el, S); };
      if (RT.view === 'food') food(el, S); else shifts(el, S);
    },
  };
  const peopleOfLect = (S, id) => (S.ix.by.get(id) || {}).people;
  // whether the receiver's word still comes from this hop (output.py hop_status, read from the receiver's own etymology)
  const hopNow = (h) => (h.now === 'kept' ? 'kept' : h.now === 'lost' ? 'word lost'
    : h.now === 'replaced' ? `replaced${h.by ? ` ${esc(ago(h.by.kyr))} (${esc(LC.processText(h.by.process))})` : ''}` : '');
  function food(el, S) {
    const all = S.doc.food_routes || [];
    const counts = {};
    for (const r of all) counts[r.concept] = (counts[r.concept] || 0) + 1;
    el.querySelector('#rtX').innerHTML = `<span class="muted">word</span><select id="rtC"><option value="">all (${all.length})</option>${Object.keys(counts).sort().map((c) => `<option value="${esc(c)}" ${c === RT.concept ? 'selected' : ''}>${esc(c)} (${counts[c]})</option>`).join('')}</select>`;
    el.querySelector('#rtC').onchange = (e) => { RT.concept = e.target.value; RT.n = 40; food(el, S); };
    let rs = all.filter((r) => !RT.concept || r.concept === RT.concept);
    if (RT.people) rs = rs.filter((r) => peopleOfLect(S, r.origin_lect) === RT.people || (r.hops || []).some((h) => peopleOfLect(S, h.lect) === RT.people));
    rs = rs.slice().sort((a, b) => (b.hops || []).length - (a.hops || []).length);
    const html = rs.slice(0, RT.n).map((r, k) => {
      const op = peopleOfLect(S, r.origin_lect);
      return `<details${k === 0 ? ' open' : ''}><summary><b>${conceptText(r.concept)}</b> <span class="rom">${esc(r.roman || '')}</span> <span class="ipa">${esc(r.ipa || '')}</span>${say(r.ipa, op)}
        <span class="muted">· ${esc(r.origin || 'from')} ${esc(demeName(S, r.origin_deme))} (${r.origin_lect ? esc(r.origin_lect) : ''}) ${r.kyr != null ? esc(ago(r.kyr)) : ''} · ${(r.hops || []).length} hops</span></summary>
        <table class="t" style="margin:4px 0"><tr><th>when</th><th>from</th><th></th><th>to</th><th>form there</th><th>spelling</th><th>changes on the way</th><th>word there later</th></tr>
        ${(r.hops || []).map((h) => `<tr><td class="n">${esc(ago(h.kyr))}</td><td>${esc(demeName(S, h.from_deme))} <span class="muted">${h.from_lect ? lk(h.from_lect, h.from_lect) : ''}</span></td><td class="muted">→</td>
          <td>${sw(V.peopleColor(peopleOfLect(S, h.lect)))}${esc(demeName(S, h.deme))} <span class="muted">${lk(h.lect, h.lect)}</span></td>
          <td class="ipa">${h.from_ipa && h.from_ipa !== h.ipa ? `<span class="muted">${esc(h.from_ipa)} →</span> ` : ''}${esc(h.ipa)}${say(h.ipa, peopleOfLect(S, h.lect))}</td><td class="rom">${esc(h.roman || '')}</td>
          <td class="muted" style="font-size:11px">${(h.changes || []).map((c) => esc(LC.processText(c))).join('; ') || (h.from_ipa && h.from_ipa !== h.ipa ? 'heard and said its own way' : '')}</td>
          <td class="muted" style="font-size:11px">${hopNow(h)}</td></tr>`).join('')}</table></details>`;
    }).join('');
    el.querySelector('#rtBody').innerHTML = (html || '<p class="muted">no routes</p>') + (rs.length > RT.n ? `<p><span class="lk" id="rtMore">${rs.length - RT.n} more routes…</span></p>` : '');
    const m = el.querySelector('#rtMore'); if (m) m.onclick = () => { RT.n += 80; food(el, S); };
  }
  function shifts(el, S) {
    const all = S.doc.shifts || [];
    const kinds = {};
    for (const s of all) { const k = (s.trigger && s.trigger.kind) || 'none'; kinds[k] = (kinds[k] || 0) + 1; }
    el.querySelector('#rtX').innerHTML = `<span class="muted">trigger</span><select id="rtK"><option value="">all</option>${Object.keys(kinds).sort().map((k) => `<option value="${esc(k)}" ${k === RT.kind ? 'selected' : ''}>${esc(k)} (${kinds[k]})</option>`).join('')}</select>`;
    el.querySelector('#rtK').onchange = (e) => { RT.kind = e.target.value; RT.n = 40; shifts(el, S); };
    let rs = all.filter((s) => (!RT.kind || ((s.trigger && s.trigger.kind) || 'none') === RT.kind) && (!RT.people || s.speakers === RT.people || s.ruler_people === RT.people));
    rs = rs.slice().sort((a, b) => b.kyr - a.kyr);
    const rows = rs.slice(0, RT.n * 2).map((s) => `<tr><td class="n">${esc(ago(s.kyr))}</td><td>${esc(demeName(S, s.deme))}</td>
      <td>${sw(V.peopleColor(s.speakers))}${esc(V.peopleName(s.speakers))} <span class="muted">→</span> ${sw(V.peopleColor(s.ruler_people))}${esc(V.peopleName(s.ruler_people))}</td>
      <td>${lk(s.from_lect, s.from_lect)} <span class="muted">→</span> ${lk(s.to_lect, s.to_lect)}${s.ruler_lect ? ` <span class="muted">(speech of ${esc(s.ruler_lect)})</span>` : ''}</td>
      <td style="max-width:340px"><b>${esc((s.trigger && s.trigger.kind) || '–')}</b> <span class="muted" style="font-size:11px">${esc((s.trigger && s.trigger.source) || '')}</span></td>
      <td style="max-width:260px;font-size:11px" title="${esc((s.substrate_words || []).join(', '))}">${(s.substrate_words || []).length ? `<b>${s.substrate_words.length}</b> ${(s.substrate_words || []).slice(0, 8).map((w) => `<span class="chipx">${esc(String(w).toLowerCase())}</span>`).join('')}${s.substrate_words.length > 8 ? '…' : ''}` : '<span class="muted">none</span>'}</td>
      <td class="ipa" style="font-size:13px">${(s.accent || []).map((a) => `${esc(a[0])}→${esc(a[1])}`).join(' ') || '<span class="muted">–</span>'}</td>
      <td style="font-size:11px">${(s.calques || []).map((c) => `${esc(c.feature)}: ${esc(c.from)}→${esc(c.to)}`).join('<br>')}</td></tr>`).join('');
    el.querySelector('#rtBody').innerHTML = `<table class="t"><tr><th>when</th><th>place</th><th>speakers → took the speech of</th><th>old lect → new</th><th>why</th><th>local words kept</th><th>sounds said the old way</th><th>grammar kept</th></tr>${rows || '<tr><td colspan="8" class="muted">none</td></tr>'}</table>
      ${rs.length > RT.n * 2 ? `<p><span class="lk" id="rtMore">${rs.length - RT.n * 2} more…</span></p>` : ''}`;
    const m = el.querySelector('#rtMore'); if (m) m.onclick = () => { RT.n += 80; shifts(el, S); };
  }

  // ================================================================== tab 6: checks and voices
  const val = (v) => (v == null ? '–' : typeof v === 'object' ? Object.entries(v).map(([k, x]) => `<div><span class="muted">${esc(k)}</span> ${esc(typeof x === 'object' ? JSON.stringify(x) : x)}</div>`).join('') : esc(v));
  V.TABS.checks = {
    foot: 'The pass checks itself against real languages (inventory sizes against PHOIBLE, how fast relatives stop looking related, and so on): green passed, red not yet. Below, each species\' voice: what it speaks with, which sounds cost it more (or cannot be made at all), and what it hears well. "Human default" means no voice of its own has been written yet.',
    draw(el, S) {
      const doc = S.doc, fam = doc.families || {};
      const checks = doc.checks || [];
      const profs = doc.profiles || {};
      const fnum = [['lects spoken now', fam.living], ['true families', fam.true_families], ["families the scholars see", fam.scholars_families],
        ["scholars' horizon (measured)", fam.horizon_kyr != null ? NumFmt.kyr(fam.horizon_kyr) : null], ['clade horizon', fam.clade_horizon_kyr != null ? NumFmt.kyr(fam.clade_horizon_kyr) : null],
        ['clades recovered', fam.clades_recovered != null ? `${fam.clades_recovered} of ${fam.clades_true}` : null], ['chance share (floor)', fam.chance ? fam.chance.floor : null],
        ['sisters (<= 2 kyr) share', fam.shares && fam.shares.siblings_le2kyr], ['cross-family share', fam.shares && fam.shares.cross_family]].filter((r) => r[1] != null);
      const prof = (p, x) => {
        const cost = Object.entries(x.make_cost || {}).map(([k, v]) => [k, v === 'inf' || v === Infinity ? Infinity : +v]);
        const cant = cost.filter(([, v]) => v === Infinity).map(([k]) => k), dear = cost.filter(([, v]) => v > 1 && v < Infinity).sort((a, b) => b[1] - a[1]), cheap = cost.filter(([, v]) => v < 1).sort((a, b) => a[1] - b[1]);
        const src = String(x.source || '');
        const flag = /default/i.test(src) || (x.notes || []).length === 1 && /^Human default/.test((x.notes || [])[0]) ? 'human default' : src === 'data_file' ? 'its own voice (data file)' : src || '–';
        return `<div class="card"><h3>${sw(V.peopleColor(p))}${esc(V.peopleName(p))} <span class="pill">${esc(flag)}</span> <span class="muted" style="font-weight:normal">${esc(x.modality || '')}${x.register != null ? ' · register ' + esc(x.register) : ''}</span></h3>
          <div><span class="muted">speaks with</span> ${(x.articulators || []).map((a) => `<span class="chipx">${esc(a.replace(/_/g, ' '))}</span>`).join('') || '–'}</div>
          ${cant.length ? `<div><span class="muted">cannot make</span> ${cant.map((a) => `<span class="chipx" style="color:var(--lo)">${esc(a.replace(/_/g, ' '))}</span>`).join('')}</div>` : ''}
          ${dear.length ? `<div><span class="muted">costly</span> ${dear.map(([a, v]) => `<span class="chipx">${esc(a.replace(/_/g, ' '))} ×${v}</span>`).join('')}</div>` : ''}
          ${cheap.length ? `<div><span class="muted">easy</span> ${cheap.map(([a, v]) => `<span class="chipx" style="color:var(--hi)">${esc(a.replace(/_/g, ' '))} ×${v}</span>`).join('')}</div>` : ''}
          <div><span class="muted">hears</span> ${Object.entries(x.hear || {}).map(([a, v]) => `<span class="chipx" style="${+v === 0 ? 'color:var(--lo)' : +v > 1 ? 'color:var(--hi)' : ''}">${esc(a)} ${+v === 0 ? 'not at all' : '×' + esc(v)}</span>`).join('') || '–'}</div>
          ${(x.notes || []).length ? `<details class="sec"><summary>notes (${x.notes.length})</summary><ul style="margin:2px 0 0 16px;padding:0;font-size:12px">${x.notes.map((n) => `<li>${esc(n)}</li>`).join('')}</ul></details>` : ''}</div>`;
      };
      el.innerHTML = `<h3 style="margin-top:0">Checks</h3>
        <table class="t"><tr><th></th><th>check</th><th>value</th><th>target</th><th>note</th></tr>${checks.map((c) => `<tr><td class="${c.pass ? 'pass' : 'fail'}" style="font-size:14px">${c.pass ? '✓' : '✗'}</td><td><b>${esc(c.name)}</b></td><td style="font-size:11px">${val(c.value)}</td><td style="max-width:300px">${esc(c.target)}</td><td class="muted" style="max-width:340px;font-size:11px">${esc(c.note || '')}</td></tr>`).join('') || '<tr><td colspan="5" class="muted">no checks in this file</td></tr>'}</table>
        <h3>Families in numbers</h3><table class="t">${fnum.map(([k, v]) => `<tr><td class="muted">${esc(k)}</td><td class="n">${esc(v)}</td></tr>`).join('')}</table>
        <h3>Voices <span class="muted" style="font-weight:normal">(${Object.keys(profs).length} species)</span></h3>
        <div class="ngrid">${Object.entries(profs).sort((a, b) => V.peopleName(a[0]).localeCompare(V.peopleName(b[0]))).map(([p, x]) => prof(p, x)).join('')}</div>
        <p class="muted" style="font-size:11px">file ${esc(doc.format || '')} · romanization ${esc(doc.romanization || '')} · seed ${esc(doc.seed)}${doc.romanization_failures && Object.keys(doc.romanization_failures).length ? ` · ${Object.keys(doc.romanization_failures).length} forms the speller could not spell (shown in IPA)` : ''}${doc.timing && doc.timing.total_s ? ` · the pass took ${Math.round(doc.timing.total_s)} s` : ''} · loaded in ${S.loadMs || '?'} ms</p>`;
    },
  };
})();
