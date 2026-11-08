'use strict';
// The languages viewer's "Grammar & sentences" tab (languages.html; page in langview.js, helpers in langcore.js): the picked
// lect as it is spoken now. Sample sentences glossed word by word (a lect's `sentences`, planet/language/sentences.py), the
// grammar in short (`grammar_notes`), pronouns, the words, and word families seen two ways (`roots`: what a speaker feels;
// `etym_roots`: what a historian reconstructs). Every form has a ▶ button (GET /api/speak; sentences with sentence=1).
(() => {
  const V = globalThis.LangView, LC = globalThis.LangCore;
  const { esc, lk, say } = V;
  const CSS = `
#tab-grammar .gwrap { display: grid; grid-template-columns: minmax(420px, 1.1fr) minmax(380px, 1fr); gap: 12px; align-items: start; }
@media (max-width: 1100px) { #tab-grammar .gwrap { grid-template-columns: 1fr; } }
#tab-grammar .ghead { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 10px; }
#tab-grammar .ghead h2 { font-size: 16px; margin: 0; }
.sent { border-bottom: 1px solid #1c2430; padding: 7px 0 8px; }
.sent .en { font-weight: 600; margin-bottom: 3px; }
.sent .num { color: var(--muted); margin-right: 6px; font-weight: normal; }
.igl { display: flex; flex-wrap: wrap; gap: 2px 14px; margin: 2px 0 3px; }
.igl > div { display: flex; flex-direction: column; }
.igl .f { font-family: var(--ipa); font-size: 15px; }
.igl .g { font-size: 12px; color: #c9d4e3; }
.sc { font-variant: small-caps; text-transform: lowercase; letter-spacing: .03em; }
.sent .line2 { font-size: 12px; color: var(--muted); }
.sent .note { font-size: 11px; color: var(--muted); margin-top: 2px; }
.gnote { margin-bottom: 8px; }
.gnote h3 { margin: 0 0 3px; }
.gnote .ex { margin: 3px 0 0 10px; }
.wfam { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }
.wfam .fam { margin: 4px 0 8px; }
.wfam .fam .w { display: inline-block; margin: 1px 10px 1px 0; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const G = { filter: '', all: false };
  const cname = (c) => { const m = String(c).match(/^(crop|animal|good|fuel|kin):(.*)$/); return m ? `${m[2].replace(/_/g, ' ')} (${m[1]})` : String(c).toLowerCase(); };
  // a gloss with its category labels in small caps (Leipzig), lexical glosses as they are
  const glossHtml = (g) => String(g).split(/([-=.])/).map((t) => (/^[0-9A-Z][0-9A-Z]*$/.test(t) && t !== 'I' ? `<span class="sc">${esc(t)}</span>` : esc(t))).join('');
  function interlinear(form, gloss) {
    const fw = String(form).split(' '), gw = String(gloss).split(' ');
    if (fw.length !== gw.length) return `<div class="igl"><div><span class="f">${esc(form)}</span><span class="g">${glossHtml(gloss)}</span></div></div>`;
    return `<div class="igl">${fw.map((f, k) => `<div><span class="f">${esc(f)}</span><span class="g">${glossHtml(gw[k])}</span></div>`).join('')}</div>`;
  }
  const PRON = [['1st', 'I', 'WE'], ['2nd', 'THOU', 'YOU'], ['3rd', 'HE OR SHE OR IT', 'THEY']];

  function families(S, l, field) {
    const fams = LC.rootFamilies(l.lexicon, field);
    if (fams == null) return `<p class="muted">This run's file has no <code>${esc(field)}</code> (it predates them).</p>`;
    const big = fams.filter((f) => f.main.length >= 2);
    const inFam = new Set(big.flatMap((f) => f.main));
    const n = Object.keys(l.lexicon || {}).length;
    const R = S.doc.roots || {};
    const head = `<p class="muted">${big.filter((f) => f.main.length >= 3).length} families of 3+ words; ${Math.round(100 * inFam.size / Math.max(1, n))}% of the ${n} words share a root with another word.</p>`;
    return head + big.slice(0, 8).map((f) => {
      const r = R[f.root] || {};
      const c = String(f.root).split(':').slice(1).join(':').split('@')[0];
      return `<div class="fam"><b>${esc(String(r.gloss || cname(c)))}</b> ${r.ipa ? `<span class="ipa">*${esc(r.ipa)}</span>` : ''}
        <span class="muted">${r.lect ? 'from ' + lk(r.lect, r.lect) : ''}${r.kyr != null ? ', ' + esc(V.ago(r.kyr)) : ''} · ${f.main.length} words</span><br>
        ${f.main.slice(0, 14).map((k) => { const w = l.lexicon[k]; return `<span class="w">${esc(cname(k))} <span class="ipa">${esc(w.ipa)}</span>${say(w.ipa, l.people)}</span>`; }).join('')}${f.main.length > 14 ? ` <span class="muted">… ${f.main.length - 14} more</span>` : ''}</div>`;
    }).join('') || '<p class="muted">Every root has a single word here.</p>';
  }

  V.TABS.grammar = {
    foot: 'The picked language as it is spoken now: sample sentences glossed morpheme by morpheme (Leipzig style: - an affix, = a clitic, category labels in small caps), its grammar in short, pronouns, words, and word families as a speaker feels them and as a historian would reconstruct them. Every ▶ says the form aloud; ▶ play all says the sentences in turn. The voice picker is at the top right.',
    draw(el, S) {
      const l = V.lect(S.sel);
      if (!l) { el.innerHTML = '<p class="muted">Pick a lect (any tab, or the find box at the top).</p>'; return; }
      const lex = l.lexicon || {};
      const p = l.people;
      const sents = l.sentences || [];
      const notes = l.grammar_notes || [];
      const living = l.died_kyr == null && l.deme != null;
      const first = sents[0];
      let html = `<div class="ghead"><h2>${esc(V.lectLabel(l.id))}</h2><span class="muted">${esc(V.peopleName(p))}</span>
        ${first ? say(first.ipa, p, { sentence: true, q: first.q, label: 'hear a sample', title: `hear a sample: ‘${first.en}’` }) : ''}
        ${sents.length > 1 ? `<button class="say lab playall" data-playall="gsents" title="say every sample sentence in turn (click again to stop)">&#9654; play all sentences</button>` : ''}</div>`;
      if (!living) html += '<p class="muted">This lect is no longer spoken: sample sentences and grammar notes are made for living lects only. Its words are below.</p>';
      else if (!sents.length && !notes.length) html += '<p class="muted">This run\'s languages.json has no sample sentences yet (written before round 5): re-run the language pass to get them.</p>';
      const sentHtml = sents.map((s, k) => `<div class="sent"><div class="en"><span class="num">(${k + 1})</span>‘${esc(s.en)}’ ${say(s.ipa, p, { sentence: true, q: s.q })}</div>
          ${interlinear(s.w.map((w) => w[0]).join(' '), s.w.map((w) => w[1]).join(' '))}
          <div class="line2"><span class="ipa">/${esc(s.ipa)}/</span> · <span class="rom">${esc(s.roman || '')}</span>${s.q ? ' · rising intonation' : ''}</div>
          ${s.note ? `<div class="note">${esc(s.note)}</div>` : ''}</div>`).join('');
      const noteHtml = notes.map((n) => `<div class="gnote card"><h3>${esc(n.topic)}</h3><div>${esc(n.text)}</div>
          ${(n.ex || []).slice(0, 4).map((x) => {
            if (typeof x === 'string') {  // a sample sentence by id
              const k = sents.findIndex((s) => s.id === x);
              if (k < 0) return '';
              const s = sents[k];
              return `<div class="ex">${interlinear(s.w.map((w) => w[0]).join(' '), s.w.map((w) => w[1]).join(' '))}<span class="muted">‘${esc(s.en)}’ (sentence ${k + 1})</span>${say(s.ipa, p, { sentence: true, q: s.q })}</div>`;
            }
            const [f, g, en] = x;
            return `<div class="ex">${interlinear(f, g)}<span class="muted">‘${esc(en)}’</span>${say(LC.surfaceOf(f), p, { sentence: f.includes(' '), q: /\?$/.test(en) })}</div>`;
          }).join('')}</div>`).join('');
      if (sents.length || notes.length) {
        html += `<div class="gwrap"><div id="gsents"><h3>Sample sentences</h3>${sentHtml || '<p class="muted">none</p>'}</div>
          <div><h3>The grammar in short</h3>${noteHtml || '<p class="muted">none</p>'}</div></div>`;
      }
      // pronouns
      const cell = (c) => (lex[c] ? `<span class="ipa">${esc(lex[c].ipa)}</span> <span class="rom">${esc(lex[c].roman || '')}</span>${say(lex[c].ipa, p)}` : '<span class="muted">–</span>');
      html += `<h3>Pronouns</h3><table class="t"><tr><th>person</th><th>singular</th><th>plural</th></tr>${PRON.map(([n, sg, pl]) => `<tr><td>${n}</td><td>${cell(sg)}</td><td>${cell(pl)}</td></tr>`).join('')}</table>`;
      // words
      const core = (S.doc.snapshot_concepts || []).filter((c) => lex[c]);
      const allW = Object.keys(lex).sort();
      const f = G.filter.trim().toLowerCase();
      let list = G.all || f ? allW : core.length ? core : allW;
      if (f) list = list.filter((c) => c.toLowerCase().includes(f) || (lex[c].roman || '').toLowerCase().includes(f) || (lex[c].ipa || '').includes(f));
      html += `<h3>Words <span class="muted" style="font-weight:normal">(${G.all || f ? 'all ' + allW.length : 'the core ' + core.length}${f ? `, ${list.length} matching` : ''})</span></h3>
        <div class="row" style="margin-bottom:4px"><input id="gFind" placeholder="find a meaning, spelling or IPA…" size="28" value="${esc(G.filter)}">
          <label><input type="checkbox" id="gAll" ${G.all ? 'checked' : ''}> every word</label></div>
        <div style="max-height:360px;overflow:auto"><table class="t"><tr><th>meaning</th><th>IPA</th><th>spelling</th><th>part of speech</th><th></th></tr>
        ${list.slice(0, 600).map((c) => `<tr><td>${esc(cname(c))}</td><td class="ipa">${esc(lex[c].ipa)}</td><td class="rom">${esc(lex[c].roman || '')}</td><td class="muted">${esc(lex[c].pos || '')}</td><td>${say(lex[c].ipa, p)}</td></tr>`).join('')}</table></div>`;
      // word families, two views
      html += `<h3>Word families</h3><div class="wfam"><div class="card"><h3>Families a speaker feels</h3>
          <p class="muted">Roots a speaker still hears in the words: a derivation or compound younger than 3,000 years whose parts are still in use.</p>${families(S, l, 'roots')}</div>
        <div class="card"><h3>Families a historian reconstructs</h3>
          <p class="muted">Every word's family as it was when the word was made, however opaque it has become since (like *bher- ‘carry’ behind English burden).</p>${families(S, l, 'etym_roots')}</div></div>`;
      el.innerHTML = html;
      const fi = el.querySelector('#gFind');
      fi.oninput = (e) => { G.filter = e.target.value; const pos = e.target.selectionStart; this.draw(el, S); const n = el.querySelector('#gFind'); n.focus(); n.setSelectionRange(pos, pos); };
      el.querySelector('#gAll').onchange = (e) => { G.all = e.target.checked; this.draw(el, S); };
    },
  };
})();
