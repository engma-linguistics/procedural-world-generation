'use strict';
// The peoples workbench's "States & war" tab (PW-1433): the invasions Daniel schedules, and the incursions the sim found on its own.
//   Your invasions  rows "who comes down on whom, when, from where, how hard": add, edit, remove; saved in the run's authored.json
//                   (POST /api/authored {invasions}, beside the faiths he wrote), then the polities doc is worked out again with them
//                   (GET /api/polities: planet/lineages/polities.py, war v0, the rows through planet/lineages/invasions.py) and each row
//                   reads "it happened" (who took what from whom, when, how much land) or "it didn't" and why. The globe's Polities layer
//                   and cards are told to fetch again (BroadcastChannel 'pw-polities').
//   Found by the sim  the incursions the history's own detector found (planet/lineages/contacts.py, the run's meta.contacts.incursions):
//                   read-only, beside his rows.
// Every date is read with NumFmt.parseDate and shown with NumFmt.ago. Cultures are keyed by their cultures.json uid.
// A classic script: lineages.html calls InvasionTab.draw(el, result) with result = { id, ...run.meta } of the picked run.
(() => {
  const CSS = `
#tab-polities.on { display: grid; grid-template-rows: auto minmax(0, 1fr); padding: 0; overflow: hidden; }
#tab-polities .iv-bar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; padding: 6px 12px; border-bottom: 1px solid var(--line); background: var(--panel); }
#tab-polities .iv-main { min-height: 0; overflow: auto; padding: 10px 12px; }
#tab-polities .iv-split { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 10px; min-height: 100%; }
#tab-polities .iv-side { border-left: 1px solid var(--line); padding-left: 10px; overflow: auto; }
#tab-polities .iv-form { display: grid; gap: 8px; align-content: start; }
#tab-polities .iv-form label { display: grid; gap: 2px; }
#tab-polities .iv-form .row { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
#tab-polities .iv-pick { position: relative; cursor: crosshair; }
#tab-polities .iv-pick img { width: 100%; display: block; border-radius: 4px; }
#tab-polities .iv-pick svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
#tab-polities .ok { color: #6bd66b; } #tab-polities .no { color: #ff7b6b; } #tab-polities .err { color: #ff7b6b; }
#tab-polities h3 { margin: 12px 0 4px; font-size: 13px; }
`;
  document.head.insertAdjacentHTML('beforeend', `<style>${CSS}</style>`);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ago = (k) => NumFmt.ago(k);
  const km2 = (x) => `${Math.round(x).toLocaleString('en')} km²`;
  const dflt = () => (NumFmt.present && NumFmt.present() != null ? 'year' : 'ago');  // (a bare number: a calendar year once the present is set, else years ago)
  const readYear = (t) => { const k = NumFmt.parseDate ? NumFmt.parseDate(t, dflt()) : null; return k == null || !Number.isFinite(k) ? null : k; };
  const COMPASS = ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west'];
  const FOOT = `Invasions you schedule: "the antelope-kin come down on the humans around year 1400". Each changes only the states and wars
    read after the run (the Polities layer on the globe), never the peoples history: in its window a state of the invaders that borders a polity
    of the victims attacks it with twice war's usual chance per century (light) or for certain and with no edge in strength needed (strong).
    A strong one also reaches: a war band if the invaders have only chiefdoms, an expedition of up to about 1,000 km (further for a large empire: as far as its own radius) if no state of theirs borders the
    victims, and further for nomads and herders. The result says what came of it: who took what from whom, when, and how much land, or why nothing happened (no state of the invaders then,
    no border with the victims, the odds, or the chance). On the right, the incursions the peoples history found on its own (read-only).`;
  const st = { edit: null, err: '', who: '' };
  let D = null;

  const get = (u) => fetch(u, { cache: 'no-store' }).then((r) => r.ok ? r.json() : r.text().then((t) => { let m = t; try { m = JSON.parse(t).error || t; } catch (e) {} return { error: `${r.status} ${String(m).slice(0, 200)}` }; })).catch((e) => ({ error: e.message }));
  function load(result) {  // (the saved rows and what they may name: quick; the polities doc with the read-out: up to a minute the first time)
    const id = result.id;
    D = { id, result, authored: null, pol: null, busy: true };
    get(`../api/authored?run=${encodeURIComponent(id)}&choices=1`).then((a) => { if (!D || D.id !== id) return; D.authored = a; D.busy = false; draw(); });
    get(`../api/polities?run=${encodeURIComponent(id)}`).then((p) => { if (!D || D.id !== id) return; if (st.edit && $('if-who') && $('if-who').value !== undefined) readForm(); D.pol = p; draw(); });  // (keep what was typed)
  }
  const peopleName = (id) => { const p = (D.authored?.choices?.peoples || []).find((x) => x.id === id) || (D.result.lineages || []).find((x) => x.id === id); return p ? String(p.name).split(' (')[0] : id; };
  const cultureName = (u) => (D.authored?.choices?.cultures || []).find((c) => c.uid === u)?.name || u;
  const side = (s) => (!s ? 'anyone they border' : s.culture ? cultureName(s.culture) : `the ${peopleName(s.people)}`);
  const when = (r) => (Math.abs(r.from_kyr - r.to_kyr) < 1e-9 ? `around ${ago(r.from_kyr)}` : `${ago(r.from_kyr)} to ${ago(r.to_kyr)}`);
  function result(r) {  // (one row's read-out: from the polities doc, matched by id)
    const P = D.pol;
    if (!P) return '<span class="muted">working out the states and wars with your invasions (about a minute the first time)…</span>';
    if (P.error) return `<span class="err">${esc(P.error)}</span>`;
    const o = ((P.invasions || {}).rows || []).find((x) => x.id === r.id);
    if (!o) return '<span class="muted">not read yet (save again, or see the problems below)</span>';
    if (o.happened) {
      const far = (o.reach || []).reduce((m, e) => Math.max(m, e.km), 0), nx = (o.reach || []).length, wb = (o.war_band || []).length;  // (PW-1450: how it reached)
      const how = [nx ? `${nx} by expedition, the furthest ${Math.round(far).toLocaleString('en')} km across the gap` : '',
        wb ? `a war band ruled as a state for them in ${wb} centur${wb === 1 ? 'y' : 'ies'}` : ''].filter(Boolean).join('; ');
      return `<span class="ok">it happened</span>: ${o.took.map((t) => `${esc(t.winner)} took ${esc(t.loser)} ${esc(ago(t.ago_kyr))} (${km2(t.km2)})`).join('; ')}. <b>${km2(o.km2)}</b> in all.${how ? ` <span class="muted">(${esc(how)})</span>` : ''}`;
    }
    const s = o.states || {}, hint = s.centuries ? ` <span class="muted">(${esc(side(r.who))} ruled a state in ${s.centuries} centur${s.centuries === 1 ? 'y' : 'ies'} of this run, between ${esc(ago(s.from_kyr))} and ${esc(ago(s.to_kyr))})</span>`
      : (o.why || '').includes('no people') || (o.why || '').includes('no culture') ? '' : ` <span class="muted">(${esc(side(r.who))} never ruled a state in this run)</span>`;
    return `<span class="no">it didn't</span>: ${esc(o.why || '')}.${hint}`;
  }
  function rowsHtml() {
    const saved = D.authored.invasions || [];
    let h = '<h3>Your invasions</h3>';
    if (!saved.length) h += '<p class="muted">None scheduled yet. Press "schedule an invasion": who comes down on whom, when, from where, and how hard.</p>';
    else {
      h += '<table class="t"><tr><th>who</th><th>on whom</th><th>when</th><th>from</th><th>how hard</th><th>what came of it</th><th></th></tr>';
      saved.forEach((r, i) => {
        h += `<tr><td>${esc(side(r.who))}</td><td>${esc(side(r.whom))}</td><td>${esc(r.year_text || '')} <span class="muted">(${esc(when(r))})</span></td>
          <td>${r.place ? `${r.place[0].toFixed(1)}°, ${r.place[1].toFixed(1)}°` : '<span class="muted">anywhere</span>'}</td><td>${esc(r.strength)}</td>
          <td style="max-width:520px">${result(r)}</td><td style="white-space:nowrap"><button data-ed="${i}">edit</button> <button data-rm="${i}">remove</button></td></tr>`;
      });
      h += '</table>';
    }
    const probs = (D.pol?.invasions || {}).problems || [];
    if (probs.length) h += `<p class="err">Problems in the saved file (skipped): ${probs.map(esc).join('; ')}</p>`;
    return h + `<p class="err" id="iv-err">${esc(st.err || '')}</p>`;
  }
  function foundHtml() {  // (the incursions the history's own detector found: contacts.py, read-only)
    const all = (D.result.contacts || {}).incursions || [];
    let h = '<h3>Found by the sim <span class="muted">(read-only)</span></h3>';
    if (!all.length) return h + '<p class="muted">The peoples history found no incursions in this run (or it is older than the detector).</p>';
    const ps = [...new Set(all.flatMap((x) => [x.by, x.over]))].sort((a, b) => peopleName(a).localeCompare(peopleName(b)));
    const list = all.filter((x) => !st.who || x.by === st.who || x.over === st.who).slice().sort((a, b) => a.ago_kyr - b.ago_kyr).slice(0, 80);
    h += `<p class="muted">A people taking ground another held, within a few centuries (by moving in, or by settling among them). ${all.length} in all; the most recent first.</p>
      <label class="row">people <select id="iv-who"><option value="">all</option>${ps.map((p) => `<option value="${esc(p)}" ${p === st.who ? 'selected' : ''}>${esc(peopleName(p))}</option>`).join('')}</select></label>
      <table class="t"><tr><th>who</th><th>over</th><th>when</th><th>land</th><th>where</th></tr>`;
    for (const x of list) {
      const dir = x.from_deg == null ? '' : `, from the ${COMPASS[Math.round(x.from_deg / 45) % 8]}`;
      h += `<tr><td>${esc(peopleName(x.by))}</td><td>${esc(peopleName(x.over))} <span class="muted">(${esc(String(x.kind).replace(/_/g, ' '))})</span></td><td>${esc(ago(x.ago_kyr))}</td>
        <td>${km2(x.mkm2 * 1e6)}</td><td>${x.lat.toFixed(1)}°, ${x.lon.toFixed(1)}°${esc(dir)}</td></tr>`;
    }
    return h + '</table>';
  }
  function sideOpts(cur, anyone) {
    const C = D.authored.choices || { peoples: [], cultures: [] };
    const now = cur ? (cur.culture ? `c${cur.culture}` : `p${cur.people}`) : '';
    const ps = C.peoples.slice().sort((a, b) => peopleName(a.id).localeCompare(peopleName(b.id)));
    const cs = C.cultures.slice().sort((a, b) => String(a.name).localeCompare(String(b.name)));
    return (anyone ? `<option value="" ${now === '' ? 'selected' : ''}>anyone they border</option>` : `<option value="" ${now === '' ? 'selected' : ''}>pick a people or culture</option>`)
      + `<optgroup label="a people (with its groups and daughter lines)">${ps.map((p) => `<option value="p${esc(p.id)}" ${now === 'p' + p.id ? 'selected' : ''}>${esc(peopleName(p.id))}</option>`).join('')}</optgroup>`
      + `<optgroup label="a culture">${cs.map((c) => `<option value="c${esc(c.uid)}" ${now === 'c' + c.uid ? 'selected' : ''}>${esc(c.name)} (${esc(peopleName(c.people))})</option>`).join('')}</optgroup>`;
  }
  const pick = (v) => (!v ? null : v[0] === 'c' ? { culture: v.slice(1) } : { people: v.slice(1) });
  const P = (lat, lon) => [(lon + 180) / 360 * 1024, (90 - lat) / 180 * 512];
  function formHtml(r) {
    const steps = D.pol?.steps || [], fr = steps.length ? steps[steps.length - 1].frame : null;
    const [a, b] = (r.year_text || '').split(/\s+to\s+/);
    return `<div class="iv-form"><h3>${r.id ? 'Edit' : 'Schedule'} an invasion</h3>
      <label>who invades <select id="if-who">${sideOpts(r.who, false)}</select></label>
      <label>on whom <select id="if-whom">${sideOpts(r.whom, true)}</select></label>
      <label>year, or the start of a window <input id="if-from" value="${esc(a || (r.from_kyr != null ? ago(r.from_kyr) : ''))}" placeholder="${dflt() === 'year' ? 'year 1400' : '600 years ago'}"><span id="if-fy" class="muted"></span></label>
      <label>until (optional: leave empty for the century around that year) <input id="if-to" value="${esc(b || (r.to_kyr != null && Math.abs(r.to_kyr - r.from_kyr) > 1e-9 ? ago(r.to_kyr) : ''))}" placeholder="${dflt() === 'year' ? 'year 1600' : '400 years ago'}"><span id="if-ty" class="muted"></span></label>
      <div><div class="row"><span class="muted">from where</span><label class="row"><input type="radio" name="if-pl" value="any" ${r.place ? '' : 'checked'}> anywhere</label>
        <label class="row"><input type="radio" name="if-pl" value="map" ${r.place ? 'checked' : ''}> a place: click the map</label><span id="if-plt" class="muted">${r.place ? `${r.place[0].toFixed(2)}°, ${r.place[1].toFixed(2)}°` : ''}</span></div>
        ${fr != null ? `<div class="iv-pick" id="if-map"><img alt="click to pick where they come from" src="../api/faithmap?run=${encodeURIComponent(D.id)}&frame=${fr}&w=1024"><svg id="if-mk" viewBox="0 0 1024 512" preserveAspectRatio="none"></svg></div>` : '<span class="muted">(the map shows once the states are worked out)</span>'}</div>
      <div class="row"><span class="muted">how hard</span><label class="row"><input type="radio" name="if-st" value="light" ${r.strength !== 'strong' ? 'checked' : ''}> light (twice the chance)</label>
        <label class="row"><input type="radio" name="if-st" value="strong" ${r.strength === 'strong' ? 'checked' : ''}> strong (certain, no edge needed)</label></div>
      <div class="row"><button id="if-save">save</button><button id="if-cancel">cancel</button><span id="if-msg" class="err"></span></div></div>`;
  }
  function readForm() {
    const r = st.edit, q = (s) => D.root.querySelector(s);
    r.who = pick($('if-who').value); r.whom = pick($('if-whom').value);
    const a = $('if-from').value.trim(), b = $('if-to').value.trim();
    r.year_text = b ? `${a} to ${b}` : a;
    const ka = readYear(a), kb = b ? readYear(b) : ka;
    r.from_kyr = ka == null || kb == null ? null : Math.max(ka, kb); r.to_kyr = ka == null || kb == null ? null : Math.min(ka, kb);
    r._bad = ka == null ? a : kb == null ? b : null;
    const any = q('input[name="if-pl"][value="any"]');
    if (any && any.checked) r.place = null;
    const strong = q('input[name="if-st"][value="strong"]');
    r.strength = strong && strong.checked ? 'strong' : 'light';
    return r;
  }
  function problem(r) {  // (what the server would refuse, said before saving; odd but well-formed rows are saved and explained)
    if (!r.who) return 'pick who invades';
    if (r.from_kyr == null) return `the date "${r._bad ?? ''}" could not be read (try ${dflt() === 'year' ? '"year 1400"' : '"600 years ago"'} or "0.6 kyr")`;
    return '';
  }
  function marker(r) { const mk = $('if-mk'); if (!mk) return; if (!r.place) { mk.innerHTML = ''; return; } const [x, y] = P(r.place[0], r.place[1]);
    mk.innerHTML = `<circle cx="${x}" cy="${y}" r="9" fill="none" stroke="#fff" stroke-width="5"/><circle cx="${x}" cy="${y}" r="9" fill="none" stroke="#ff7b6b" stroke-width="2.5"/>`; }
  function formWire(saved) {
    const r = st.edit;
    const yr = (inp, out) => { const v = $(inp).value.trim(), k = readYear(v); $(out).textContent = v ? (k == null ? 'cannot read that date' : `→ ${ago(k)}`) : ''; };
    yr('if-from', 'if-fy'); yr('if-to', 'if-ty'); marker(r);
    $('if-from').oninput = () => yr('if-from', 'if-fy'); $('if-to').oninput = () => yr('if-to', 'if-ty');
    if ($('if-map')) $('if-map').onclick = (e) => { const b = e.currentTarget.getBoundingClientRect(); if (!b.width) return;
      const lon = ((e.clientX - b.left) / b.width) * 360 - 180, lat = 90 - ((e.clientY - b.top) / b.height) * 180;
      r.place = [Math.max(-90, Math.min(90, lat)), lon]; const m = D.root.querySelector('input[name="if-pl"][value="map"]'); if (m) m.checked = true;
      $('if-plt').textContent = `${r.place[0].toFixed(2)}°, ${r.place[1].toFixed(2)}°`; marker(r); };
    $('if-cancel').onclick = () => { st.edit = null; st.err = ''; draw(); };
    $('if-save').onclick = () => {
      readForm();
      const why = problem(r); if (why) { $('if-msg').textContent = why; return; }
      if (!r.id) { let n = saved.length + 1; while (saved.some((x) => x.id === `i${n}`)) n++; r.id = `i${n}`; }
      const { _bad, ...row } = r;
      const i = saved.findIndex((x) => x.id === r.id);
      save(i >= 0 ? saved.map((x, k) => (k === i ? row : x)) : [...saved, row]);
    };
  }
  function save(list) {
    if ($('if-msg')) $('if-msg').textContent = 'saving…';
    fetch('../api/authored', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ run: D.id, invasions: list }) })
      .then((r) => r.json().then((j) => (r.ok ? j : Promise.reject(new Error(j.error || r.status)))))
      .then(() => {
        st.edit = null; st.err = '';
        try { new BroadcastChannel('pw-polities').postMessage({ run: D.id }); } catch (e) { /* no channel: the globe fetches again on its next load */ }
        const root = D.root, res = D.result; load(res); D.root = root; draw();
      })
      .catch((e) => { st.err = `not saved: ${e.message}`; if ($('if-msg')) $('if-msg').textContent = st.err; else draw(); });
  }
  function draw() {
    const el = D.root;
    if (!el) return;
    if (D.busy) { el.innerHTML = `<p class="muted" style="padding:10px 12px">Reading the invasions of ${esc(D.id)}…</p>`; return; }
    if (D.authored?.error) { el.innerHTML = `<p class="muted" style="padding:10px 12px">No invasions for ${esc(D.id)}: ${esc(D.authored.error)}</p>`; return; }
    const rule = [(D.pol?.invasions || {}).rule, (D.pol?.invasions || {}).reach].filter(Boolean).join(' ');  // (reach: PW-1450, beside rows only)
    el.innerHTML = `<div class="iv-bar"><button id="iv-add">✎ schedule an invasion</button><span class="muted" style="max-width:1000px">${esc(rule)}</span></div>
      <div class="iv-main" id="iv-main"><div class="iv-split"><div>${rowsHtml()}${foundHtml()}</div>
      <div class="iv-side">${st.edit ? formHtml(st.edit) : '<p class="muted">Pick "edit" on an invasion, or "schedule an invasion".</p>'}</div></div></div>`;
    const saved = D.authored.invasions || [];
    $('iv-add').onclick = () => { st.edit = { id: null, who: null, whom: null, from_kyr: null, to_kyr: null, year_text: '', place: null, strength: 'light' }; st.err = ''; draw(); };
    for (const b of el.querySelectorAll('[data-ed]')) b.onclick = () => { st.edit = JSON.parse(JSON.stringify(saved[+b.dataset.ed])); st.err = ''; draw(); };
    for (const b of el.querySelectorAll('[data-rm]')) b.onclick = () => { const r = saved[+b.dataset.rm]; if (typeof confirm === 'function' && !confirm(`Remove the invasion of ${side(r.who)} on ${side(r.whom)}?`)) return; save(saved.filter((x) => x !== r)); };
    if ($('iv-who')) $('iv-who').onchange = (e) => { st.who = e.target.value; draw(); };
    if ($('foot')) $('foot').innerHTML = FOOT;
    if (st.edit) formWire(saved);
  }
  window.InvasionTab = {
    FOOT,
    draw(el, result) {
      if (!D || D.id !== result.id) load(result);
      D.root = el; D.result = result;
      draw();
    },
  };
})();
