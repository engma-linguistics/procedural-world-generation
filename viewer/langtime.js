'use strict';
// The languages viewer's "A language over time" tab (languages.html; helpers in langcore.js, page in langview.js): the picked
// lect at any frame of the last 20 kyr through its line of descent (its ancestors' snapshots before it was born), with its
// sounds on the consonant grid and the vowel trapezoid (sounds that came or went since the frame before flash), the core words
// (IPA, house spelling when known, audio), the live grams on the grammaticalization ladder, the typology line, the complexity
// over time and the sound-change log up to the frame.
(() => {
  const V = globalThis.LangView, LC = globalThis.LangCore;
  const { esc, ago, lk, say } = V;
  const CORE18 = ['I', 'THOU', 'WE', 'ONE', 'TWO', 'WATER', 'FIRE', 'SUN', 'MOON', 'STAR', 'STONE', 'TREE', 'PERSON', 'WOMAN', 'MAN', 'EAT', 'DRINK', 'NAME'];
  const RUNGS = ['free word', 'clitic', 'affix', 'fused'];
  const CSS = `
#tab-time .tgrid { display: grid; grid-template-columns: minmax(380px, 1.25fr) minmax(300px, 1fr) minmax(320px, 1fr); gap: 10px; align-items: start; }
#tab-time table.cg { border-collapse: collapse; font-size: 11px; }
#tab-time table.cg th { color: var(--muted); font-weight: 500; padding: 2px 3px; white-space: nowrap; font-size: 10px; }
#tab-time table.cg th.mn { text-align: right; }
#tab-time table.cg td { border: 1px solid #222b3a; padding: 1px 3px; min-width: 26px; max-width: 92px; height: 22px; text-align: center; font-family: var(--ipa); font-size: 14px; white-space: normal; }
#tab-time .card.snd { overflow-x: auto; }
#tab-time .sg { display: inline-block; padding: 0 1px; }
#tab-time .sg.sp { color: #d7a6ff; }
#tab-time .nw { animation: lnew 1.4s ease-out; color: var(--hi); }
#tab-time .gone { color: var(--lo); text-decoration: line-through; animation: lgone 1.6s ease-out forwards; }
@keyframes lnew { from { background: rgba(95,209,122,.5); } to { background: transparent; } }
@keyframes lgone { from { opacity: 1; } to { opacity: .25; } }
#tab-time table.words td { padding: 2px 6px; }
#tab-time tr.chg td { background: rgba(95,209,122,.08); }
#tab-time .rung { border-top: 1px solid #3a475c; padding: 4px 0 4px 86px; position: relative; min-height: 26px; }
#tab-time .rung > span.rl { position: absolute; left: 0; top: 5px; width: 80px; color: var(--muted); font-size: 11px; }
#tab-time .chip { display: inline-block; border: 1px solid var(--line); border-radius: 10px; padding: 0 6px; margin: 1px 2px; font-size: 11px; background: var(--ctl); }
#tab-time .chip .ipa { font-size: 12px; }
#tab-time .log { max-height: 340px; overflow: auto; font-size: 12px; }
#tab-time .log div { padding: 2px 0; border-bottom: 1px solid #1c2430; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const st = { all: false, logN: 120, romanOf: null };

  function romanIndex(S) {  // IPA -> house spelling, from every lexicon in the file (forms the pass spelled); built once
    if (st.romanOf && st.romanOf.doc === S.doc) return st.romanOf.map;
    const m = new Map();
    for (const l of S.doc.lects) for (const w of Object.values(l.lexicon || {})) if (w.ipa && w.roman && !m.has(w.ipa)) m.set(w.ipa, w.roman);
    st.romanOf = { doc: S.doc, map: m };
    return m;
  }
  const segLabel = (s) => String(s).replace(/\{[^}]*\}/g, '°');  // (features in braces: a degree sign, the full form on hover)
  function segsOf(snap) { return snap ? [...(snap.c || []), ...(snap.v || [])] : []; }
  // allophone tests (inventory.ALLO_TESTS): short and long plain words
  const ALLO_SHORT = { nasal_place: 'before a consonant of its place', palatal: 'before front vowels', intervocalic: 'between vowels',
    final: 'word-finally', initial: 'word-initially', nasal_vowel: 'before a nasal', glottal_onset: 'before a word-initial vowel or between vowels' };
  const ALLO = { nasal_place: 'nasal place assimilation', palatal: 'palatalized before front vowels and j', intervocalic: 'lenition between vowels',
    final: 'final devoicing or voicing', initial: 'strengthened at the start of a word', nasal_vowel: 'a vowel nasalized before a nasal consonant',
    glottal_onset: 'a glottal stop inserted before a vowel at the start of a word or between vowels' };

  V.TABS.time = {
    foot: 'One lect through time: drag the slider or press ▶ (before it was born you see its ancestors). Green sounds just appeared, red struck-out ones just went. The ladder shows how far each grammar word has worn down (a free word becomes a clitic, then an affix, then fuses into the stem). Click ▶ next to a word to hear it.',
    reset() { st.logN = 120; },
    draw(el, S) {
      el.innerHTML = '';
      el.appendChild(V.scrubber());
      const body = document.createElement('div');
      body.id = 'tmBody';
      el.appendChild(body);
      this.frame(el, S);
    },
    frame(el, S) {
      const body = el.querySelector('#tmBody');
      if (!body) return this.draw(el, S);
      const t0 = performance.now();
      const ix = S.ix, id = S.sel, l = ix.by.get(id);
      if (!l) { body.innerHTML = '<p class="muted">Pick a lect first (Families tab, the map, or the search box above).</p>'; return; }
      const H = LC.stitch(ix, id), cur = H[S.f], prev = S.prevF != null && H[S.prevF] ? H[S.prevF] : null;
      const snap = cur && cur.snap, psnap = prev && prev.snap && Math.abs(S.prevF - S.f) <= 3 ? prev.snap : null;
      const holders = [];
      for (const h of H) if (h.lect && (!holders.length || holders[holders.length - 1][0] !== h.lect)) holders.push([h.lect, h.kyr]);
      const line = holders.map(([x, k], j) => `${lk(x)} <span class="muted">from ${ago(k)}</span>`).join(' → ');
      const people = (ix.by.get(cur && cur.lect) || l).people;
      const head = `<div class="row" style="margin-bottom:8px"><span class="muted">line of descent:</span> ${line}
        ${cur && cur.lect !== id ? `<span class="pill">at ${esc(ago(cur.kyr))} this is still ${esc(cur.lect)}${cur.at != null && Math.abs(cur.at - cur.kyr) > 1e-6 ? `, as recorded ${esc(ago(cur.at))}` : ''}</span>` : ''}
        ${cur && !cur.exists ? '<span class="pill">not yet spoken then: its oldest record</span>' : ''}</div>`;
      if (!snap) { body.innerHTML = head + '<p class="muted">No snapshot of this lect or its ancestors is stored for this frame.</p>'; return; }
      // the sounds: rows and columns from every frame of the line, so the grid stays put while scrubbing
      const allSegs = new Set();
      for (const h of H) for (const s of segsOf(h.snap)) allSegs.add(s);
      const now = new Set(segsOf(snap)), before = psnap ? new Set(segsOf(psnap)) : now;
      const places = new Set(), manners = new Set(), cells = new Map(), others = [];
      const vowels = [];
      for (const s of allSegs) {
        const on = now.has(s), was = before.has(s);
        if (!on && !was) continue;
        const p = LC.ipaPlace(s);
        const cls = on && !was ? 'nw' : !on && was ? 'gone' : '';
        const item = { s, p, cls };
        if (p.kind === 'C') { places.add(p.place); manners.add(p.manner); const k = p.manner + '|' + p.place; if (!cells.has(k)) cells.set(k, []); cells.get(k).push(item); }
        else if (p.kind === 'V') vowels.push(item);
        else others.push(item);
      }
      for (const h of H) for (const s of segsOf(h.snap)) { const p = LC.ipaPlace(s); if (p.kind === 'C') { places.add(p.place); manners.add(p.manner); } }
      const PL = LC.PLACES.filter((p) => places.has(p)), MN = LC.MANNERS.filter((m) => manners.has(m));
      const segHtml = (it) => `<span class="sg ${it.cls}${it.p.special ? ' sp' : ''}" title="${esc(it.s)}${it.p.special ? ' (a sound with a part IPA has no letter for: features in braces, or a house symbol)' : ''}${it.cls === 'nw' ? ': new' : it.cls === 'gone' ? ': lost' : ''}">${esc(segLabel(it.s))}</span>`;
      const cg = `<table class="cg"><tr><th></th>${PL.map((p) => `<th title="${p}">${p.replace('postalveolar', 'post-alv.').replace('labiodental', 'labio-dent.').replace('pharyngeal', 'pharyng.')}</th>`).join('')}</tr>
        ${MN.map((m) => `<tr><th class="mn">${m}</th>${PL.map((p) => `<td>${(cells.get(m + '|' + p) || []).sort((a, b) => a.s.localeCompare(b.s)).map(segHtml).join('')}</td>`).join('')}</tr>`).join('')}</table>
        ${others.length ? `<div style="margin-top:4px"><span class="muted">other sounds:</span> <span class="ipa">${others.map(segHtml).join(' ')}</span></div>` : ''}
        ${(snap.al || []).length ? `<div style="margin-top:4px;font-size:12px"><span class="muted">allophones (said, but not separate sounds):</span> ${snap.al.map(([x, p, t]) => `<span class="ipa" title="${esc(ALLO[t] || t)}">[${esc(x)}]${p ? ` of /${esc(p)}/` : ' (inserted)'}</span> <span class="muted">${esc(ALLO_SHORT[t] || t)}</span>`).join(' · ')}</div>` : ''}`;
      const vt = vowelChart(vowels, segHtml);
      const nC = (snap.c || []).length, nV = (snap.v || []).length;
      // the core words
      const ro = romanIndex(S);
      const concepts = S.doc.snapshot_concepts || [];
      const want = st.all ? concepts : CORE18.filter((c) => concepts.includes(c));
      const rows = want.map((c) => {
        const j = concepts.indexOf(c), ipa = snap.core[j], pipa = psnap ? psnap.core[j] : ipa;
        const roman = ipa ? ro.get(ipa) : null;
        return `<tr class="${psnap && ipa !== pipa ? 'chg' : ''}"><td class="muted" style="font-size:11px">${esc(c.toLowerCase())}</td><td class="ipa">${ipa ? esc(ipa) : '<span class="muted">–</span>'}${psnap && ipa !== pipa && pipa ? `<div class="muted" style="font-size:11px">was ${esc(pipa)}</div>` : ''}</td><td class="rom">${roman ? esc(roman) : ''}</td><td>${say(ipa, people)}</td></tr>`;
      }).join('');
      const words = `<table class="t words"><tr><th>meaning</th><th>IPA</th><th>spelling</th><th></th></tr>${rows}</table>
        <div style="margin-top:4px"><span class="lk" id="tmAll">${st.all ? 'show the 18 core words' : `show all ${concepts.length}`}</span> <span class="muted">· spelling shown where the pass spelled that form</span></div>`;
      // grams on the ladder
      const pg = new Map((psnap ? psnap.grams || [] : []).map((g) => [g[0], g]));
      const ladder = RUNGS.map((r, lv) => `<div class="rung"><span class="rl">${r}</span>${(snap.grams || []).filter((g) => g[2] === lv).map((g) => {
        const was = pg.get(g[0]), cls = psnap && (!was || was[2] !== g[2]) ? ' nw' : '';
        return `<span class="chip${cls}" title="${esc(g[0])}${was && was[2] !== g[2] ? ': was a ' + RUNGS[was[2]] : !was && psnap ? ': new' : ''}">${esc(g[0])} <span class="ipa">${esc(g[1])}</span></span>`;
      }).join('') || '<span class="muted" style="font-size:11px">–</span>'}</div>`).join('');
      const typ = snap.typ || {};
      const tl = [typ.order && `word order <b>${esc(typ.order)}</b>`, typ.adp && `${{ pre: 'prepositions', post: 'postpositions' }[typ.adp] || esc(typ.adp) + ' adpositions'}`,
        typ.case != null && `case: ${esc(typ.case)}${typ.n_case ? ` (${typ.n_case} live)` : ''}`, typ.number != null && `number: ${esc(typ.number)}${typ.n_number ? ` (${typ.n_number})` : ''}`,
        typ.gender != null && `${/no agreement/.test(typ.gender) ? 'class' : 'gender/class'}: ${esc(typ.gender)}${typ.n_class ? ` (${typ.n_class})` : ''}`].filter(Boolean).join(' · ');
      // complexity over time
      const cx = cxChart(H, S.f);
      // the change log
      const log = LC.changeLog(ix, id).filter((c) => c.kyr >= cur.kyr - 1e-9);
      const rules = S.doc.rules || {};
      const desc = (r) => { const x = rules[r]; return x == null ? '' : typeof x === 'string' ? x : (x.describe || x.words || ''); };
      const logHtml = log.slice(0, st.logN).map((c) => `<div><span class="muted">${esc(ago(c.kyr))}</span> ${c.lect !== id ? `<span class="muted">(${esc(c.lect)})</span> ` : ''}<code>${esc(c.rule)}</code> ${esc(desc(c.rule))}
        <span class="muted">— ${esc(LC.causeText(c.cause))}${c.origin && c.origin !== c.lect ? `, spread from ${lk(c.origin)}` : ''}${c.extra && c.extra.city ? `, in the city ${esc(c.extra.city)}` : ''}</span></div>`).join('');
      // the live phonological rules (today's; planet/language/phonology.py), in the order the language applies them
      const lj = ix.by.get(id), ph = lj && lj.phonology;
      const LV = { phrase: 'across words', word: 'inside words', stem: 'word-making only', phonetic: 'allophone' };
      const phHtml = ph && (ph.rules || []).length ? `<h3>Phonological rules today <span class="muted" style="font-weight:normal">(in order)</span></h3>
        <div style="font-size:12px">${ph.rules.map((r, k) => `<div>${k + 1}. <span class="ipa">${esc(r.t)}</span> <span class="muted">— ${esc(LV[r.lv] || r.lv)}${r.b != null ? `, since ~${r.b} kyr ago` : ''}</span>${r.ex ? `<div class="muted" style="margin-left:14px">e.g. <span class="ipa">${esc(r.ex[0])} → ${esc(r.ex[1])}</span> '${esc(r.ex[2])}'</div>` : ''}</div>`).join('')}</div>` : '';
      body.innerHTML = head + `<div class="tgrid">
        <div class="card snd"><h3>Sounds at ${esc(ago(cur.kyr))} <span class="muted" style="font-weight:normal">${nC} consonants, ${nV} vowels${psnap ? '' : ''}</span></h3>${cg}<h3>Vowels</h3>${vt}${phHtml}</div>
        <div class="card"><h3>Core words</h3>${words}</div>
        <div class="card"><h3>Grammar words on the ladder</h3>${ladder}<div style="border-top:1px solid #3a475c;margin-bottom:6px"></div>
          <div style="font-size:12px">${tl || '<span class="muted">no typology recorded</span>'}</div>
          <h3>Complexity over time</h3>${cx}
          <h3>Sound changes up to ${esc(ago(cur.kyr))} <span class="muted" style="font-weight:normal">(${log.length}, newest first)</span></h3>
          <div class="log">${logHtml || '<span class="muted">none yet</span>'}${log.length > st.logN ? `<div><span class="lk" id="tmMore">${log.length - st.logN} more…</span></div>` : ''}</div></div>
      </div>`;
      const a = body.querySelector('#tmAll'); if (a) a.onclick = () => { st.all = !st.all; this.frame(el, S); };
      const m = body.querySelector('#tmMore'); if (m) m.onclick = () => { st.logN += 400; this.frame(el, S); };
      S.timeMs = Math.round(performance.now() - t0);
    },
  };

  function vowelChart(items, segHtml) {
    // the trapezoid with a dot at each vowel quality; the vowels of that quality (plain, long, nasal, toned...) as a small block
    // beside the dot: unrounded to its left, rounded to its right, at most three a line
    const W = 400, H = 236, P = 28, L = 64;
    const X = (x) => L + x * (W - L - P - 40), Y = (y) => P + y * (H - 2 * P);
    const edge = (h) => LC.vowelXY({ height: h, back: 0, round: true }).x - 0.035;
    const pts = [[edge(0), 0], [1, 0], [1, 1], [edge(6), 1]].map(([x, y]) => `${X(x)},${Y(y)}`).join(' ');
    const grid = [2, 4].map((h) => `<line x1="${X(edge(h))}" y1="${Y(h / 6)}" x2="${X(1)}" y2="${Y(h / 6)}" stroke="#2a3446"/>`).join('')
      + `<line x1="${X((edge(0) + 1) / 2)}" y1="${Y(0)}" x2="${X((edge(6) + 1) / 2)}" y2="${Y(1)}" stroke="#2a3446"/>`;
    const groups = new Map();
    for (const it of items) { const k = it.p.height + '|' + it.p.back + '|' + it.p.round; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(it); }
    const labs = [], dots = [];
    for (const [, g] of groups) {
      g.sort((a, b) => a.s.length - b.s.length || a.s.localeCompare(b.s));
      const p = g[0].p, cx = X((LC.vowelXY({ ...p, round: true }).x + LC.vowelXY({ ...p, round: false }).x) / 2), cy = Y(p.height / 6);
      dots.push(`<circle cx="${cx}" cy="${cy}" r="2" fill="#6b7a90"/>`);
      const rows = Math.ceil(g.length / 3), lh = 15;
      labs.push(`<div style="position:absolute;${p.round ? `left:${cx + 4}px` : `right:${W - cx + 4}px`};top:${cy - rows * lh / 2}px;line-height:${lh}px;max-width:66px;text-align:${p.round ? 'left' : 'right'};font-family:var(--ipa);font-size:13px;white-space:normal">${g.map(segHtml).join(' ')}</div>`);
    }
    const hl = ['close', 'close-mid', 'open-mid', 'open'].map((h, k) => `<text x="2" y="${Y([0, 2, 4, 6][k] / 6) + 4}" class="m">${h}</text>`).join('');
    return `<div style="position:relative;width:${W}px;height:${H}px"><svg width="${W}" height="${H}" style="position:absolute;inset:0"><polygon points="${pts}" fill="none" stroke="#3a475c"/>${grid}${hl}${dots.join('')}
      <text x="${X(edge(0))}" y="${P - 14}" class="m">front</text><text x="${X(0.55)}" y="${P - 14}" class="m">central</text><text x="${X(1) - 20}" y="${P - 14}" class="m">back</text></svg>${labs.join('')}</div>
      <div class="muted" style="font-size:11px">left of a dot unrounded, right of it rounded; long, nasal and toned vowels of one quality share its dot</div>`;
  }
  function cxChart(H, f) {
    const W = 330, Ht = 90, P = 18;
    const vals = H.map((h) => (h.snap && h.snap.cx != null ? h.snap.cx : null));
    const ok = vals.filter((v) => v != null);
    if (!ok.length) return '<span class="muted">no complexity recorded</span>';
    const hi = Math.max(1, ...ok), n = H.length;
    const X = (i) => P + i / Math.max(1, n - 1) * (W - 2 * P), Y = (v) => Ht - P - v / hi * (Ht - 2 * P);
    let d = '';
    vals.forEach((v, i) => { if (v != null) d += (d && vals[i - 1] != null ? 'L' : 'M') + X(i) + ',' + Y(v); });
    const ticks = [];
    for (let i = 1; i < n; i++) if (H[i].lect !== H[i - 1].lect) ticks.push(`<line x1="${X(i)}" y1="${P - 4}" x2="${X(i)}" y2="${Ht - P}" stroke="#ffc940" stroke-dasharray="2 2" opacity=".6"/><text x="${X(i) + 2}" y="${P - 6}" class="m">${esc(H[i].lect)}</text>`);
    return `<svg width="${W}" height="${Ht}"><line x1="${P}" y1="${Ht - P}" x2="${W - P}" y2="${Ht - P}" stroke="#3a475c"/>${ticks.join('')}
      <path d="${d}" stroke="#7cc4ff" fill="none" stroke-width="1.5"/><line x1="${X(f)}" y1="${P - 4}" x2="${X(f)}" y2="${Ht - P}" stroke="#dfe6f0"/>
      ${vals[f] != null ? `<circle cx="${X(f)}" cy="${Y(vals[f])}" r="3" fill="#dfe6f0"/><text x="${Math.min(X(f) + 5, W - 40)}" y="${Y(vals[f]) - 5}">${vals[f].toFixed(2)}</text>` : ''}
      <text x="${P}" y="${Ht - 4}" class="m">${esc(ago(H[0].kyr))}</text><text x="${W - P - 18}" y="${Ht - 4}" class="m">now</text><text x="2" y="${Y(hi) + 4}" class="m">${hi.toFixed(1)}</text></svg>
      <div class="muted" style="font-size:11px">grammar.complexity score (bound grams, fused forms, paradigm cells, classes); dashed: the line passes to a daughter</div>`;
  }
})();
