// The settlement view (PW-1659): with the Settlements overlay on, clicking a town (or any place: a village, a mine, a ruin) on the globe
// opens a card with what the run knows about it at the slider's moment, from GET /api/settlement (planet/lineages/settlement_view.py):
// its names, its people (size over time, the peoples living there and their shares, founders, changes of hands, wars and walls, the
// ruins under it), its goods (what its own cell makes beyond its want and what it lacks, its cultures' "has / lacks" lines and the brief's
// "Bought in" lines, and what passes through a trading town), who rules it, the faiths held there, the tongues spoken, and its history.
// Empty sections are hidden. Link: ?site=<site id> opens the card of that place once the run is loaded (with &settle=all for the dots).
import { esc } from '../planets.js';
import { S } from './state.js';
import { $, renderer } from './scene.js';
import { popAt } from './settlements.js';

const box = document.createElement('div');
box.id = 'settleView';
box.hidden = true;
box.style.cssText = 'position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.35)';
box.innerHTML = '<div class="panel" style="width:min(760px,94vw);max-height:88vh;display:flex;flex-direction:column;padding:12px 14px">'
  + '<div style="display:flex;gap:8px;align-items:baseline"><b id="svTitle" style="flex:1;font-size:15px">Settlement</b>'
  + '<button id="svClose" title="Close (Esc)">Close</button></div><div id="svBody" style="overflow:auto;margin-top:6px"></div></div>';
document.head.append(Object.assign(document.createElement('style'), { textContent:
  '#settleView h4{margin:10px 0 3px;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--accent)}'
  + '#settleView .svrow{margin:2px 0}#settleView .svk{color:var(--muted);display:inline-block;min-width:92px}'
  + '#settleView ul{margin:2px 0 0 18px;padding:0}#settleView a[data-site]{cursor:pointer;color:var(--accent)}'
  + '#settleView .svbar{display:inline-block;height:8px;vertical-align:middle;margin-right:4px;border-radius:2px}' }));
document.body.append(box);
const close = () => { box.hidden = true; };
box.addEventListener('click', (e) => {
  if (e.target === box || e.target.id === 'svClose') close();
  const a = e.target.closest?.('a[data-site]');
  if (a) openSite(+a.dataset.site);
});
addEventListener('keydown', (e) => { if (e.key === 'Escape' && !box.hidden) close(); });

const agoNow = () => Math.max(0, -(S.V.run.frames[S.V.frame]?.t ?? 0));
const ago = (k) => globalThis.NumFmt?.ago ? globalThis.NumFmt.ago(Math.max(k, 0.0001)) : `${k} kyr ago`;
const n0 = (x) => Math.round(x).toLocaleString('en-US');
const pc = (x) => `${Math.round(100 * x)}%`;
const cap = (t) => (t ? t[0].toUpperCase() + t.slice(1) : t);
const row = (k, v) => (v ? `<div class="svrow"><span class="svk">${esc(k)}</span> ${v}</div>` : '');
const sec = (title, body) => (body ? `<h4>${esc(title)}</h4>${body}` : '');

// the place to show for a cell at the slider's moment: the biggest living place, else the newest ruin
export function siteAt(cell, at = agoNow()) {
  const list = S.V?.settleByCell?.get(cell);
  if (!list?.length) return null;
  const alive = list.filter((s) => at <= s.founded_kyr + 1e-6 && (s.abandoned_kyr == null || at > s.abandoned_kyr + 1e-6));
  if (alive.length) return alive.reduce((a, b) => (popAt(b, at) > popAt(a, at) ? b : a));
  const ruins = list.filter((s) => at <= s.founded_kyr + 1e-6 && s.tier_now === 'ruin');
  return ruins.length ? ruins.reduce((a, b) => (b.abandoned_kyr < a.abandoned_kyr ? b : a)) : null;
}

// the people over time: a small line of the site's series (kyr ago on x, people on y)
function spark(series) {
  if (!series || series.length < 2) return '';
  const W = 300, H = 46, a0 = series[0][0], a1 = series.at(-1)[0], pm = Math.max(...series.map((x) => x[1]), 1);
  const x = (a) => (a0 === a1 ? W : (a0 - a) / (a0 - a1) * (W - 4) + 2), y = (p) => H - 3 - p / pm * (H - 8);
  const pts = series.map(([a, p]) => `${x(a).toFixed(1)},${y(p).toFixed(1)}`).join(' ');
  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="people over time" style="display:block;margin:2px 0">`
    + `<polyline points="${pts}" fill="none" stroke="var(--accent)" stroke-width="1.5"/>`
    + `<text x="2" y="10" fill="var(--muted)" font-size="9">~${n0(pm)}</text><text x="2" y="${H - 1}" fill="var(--muted)" font-size="9">${esc(ago(a0))}</text>`
    + `<text x="${W - 2}" y="${H - 1}" fill="var(--muted)" font-size="9" text-anchor="end">${esc(ago(a1))}</text></svg>`;
}

const bar = (v, col) => `<span class="svbar" style="width:${Math.max(2, Math.round(60 * v))}px;background:${col}"></span>`;

export function render(d) {
  const P = d.place, pn = (p) => d.place.peoples?.[p] || String(p).replace(/_/g, ' ');
  const tierWord = P.tier === 'ruin' ? `ruin of a ${P.tier_peak}` : P.tier === 'gone' ? 'place merged into another' : P.kind === 'minority' ? `${P.tier} (a second people's own place)` : P.tier;
  $('svTitle').textContent = `${cap(P.name || `cell ${P.cell}`)}: ${tierWord}`;
  // names
  const names = row('name', esc(cap(P.name || '(none stored)'))) + row('where', `lat ${P.lat}, lon ${P.lon} (cell ${P.cell})`)
    + row('older places', P.ruins_under.map((o) => `${esc(o.tier_peak || 'place')} of the ${esc(pn(o.by))} (${esc(ago(o.founded_kyr))} to ${o.abandoned_kyr != null ? esc(ago(o.abandoned_kyr)) : '?'})`).join('; '))
    + row('later', P.resettled_as ? `resettled as <a data-site="${P.resettled_as.site}">${esc(P.resettled_as.place || 'a new place')}</a> ${esc(ago(P.resettled_as.founded_kyr))}` : '')
    + row('same cell', (d.same_cell || []).filter((x) => x.tier !== 'gone').map((x) => `<a data-site="${x.site}">${esc(x.tier)} of the ${esc(x.holder)}</a>`).join(', '));
  // people
  const who = Object.entries(P.who || {}).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${esc(k === 'others' ? 'others' : pn(k))} ${v}%`).join(', ');
  const people = row('people', P.tier === 'ruin' || P.tier === 'gone' ? `none now (at most ~${n0(P.peak_pop)})` : `~${n0(P.people)}${P.peak_pop > P.people * 1.05 ? ` (at most ~${n0(P.peak_pop)}, ${esc(ago(P.peak_kyr))})` : ''}`)
    + spark(P.series)
    + row('peoples', who ? `${who} <span class="muted">(${esc(P.who_when || '')})</span>` : '')
    + row('its cultures', (d.cultures || []).filter((c) => c.in_town).map((c) => `${esc(c.name)} <span class="muted">(${esc(c.people_name || '')})</span>`).join(', '))
    + row('around it', (d.cultures || []).filter((c) => !c.in_town).map((c) => `${esc(c.name)} <span class="muted">(${esc(c.people_name || '')})</span>`).join(', '))
    + row('founded', `${esc(ago(P.founded_kyr))} by the ${esc(pn(P.founded_by))}`)
    + row('held by', P.holders.length > 1 ? P.holders.map(([a, p]) => `the ${esc(pn(p))} from ${esc(ago(a))}`).join(', ') : `the ${esc(pn(P.holder))}`)
    + row('wars', P.war.slice().reverse().map(([a, how, by]) => `${esc(how)} by the ${esc(pn(by))} ${esc(ago(a))}`).join('; '))
    + row('walls', P.walled_kyr != null ? `walled since ${esc(ago(P.walled_kyr))}` : '')
    + row('left', P.abandoned_kyr != null ? `${esc(ago(P.abandoned_kyr))}: ${esc(P.why || '')}` : '')
    + row('mining', P.district ? `${P.colony ? 'a colony of incomers ' : ''}working the ${esc(P.district)}` : '');
  // goods
  const G = d.goods;
  let goods = '';
  if (G) {
    const side = (xs, col) => (xs.length ? '<div style="margin-left:92px">' + xs.map(([, lab, v]) => `${bar(v, col)}${esc(lab)} <span class="muted">${pc(v)}</span>`).join('<br>') + '</div>' : '');
    const blk = (k, v) => (v ? `<div class="svrow"><span class="svk">${esc(k)}</span></div>${v}` : '');
    if (G.own) goods += blk('makes, spare', side(G.own.spare, '#5fbf5a')) + blk('lacks', side(G.own.lacking, '#e0584a'));
    if (G.hub) goods += row(G.hub.trading ? 'trading town' : 'market town', `a ${esc(G.hub.kind)} of ${esc(G.hub.culture_name || '')}: ${esc(G.hub.goods.join(', '))} pass through, by ${esc(G.hub.modes.join(', '))}`
      + (G.hub.quarters.length ? `; merchant quarters of ${esc(G.hub.quarters.join(', '))}` : ''));
    const cl = (G.cultures || []).filter((c) => c.line || c.bought_in);
    if (cl.length) goods += '<ul>' + cl.map((c) => `<li><b>${esc(c.name)}</b>: ${esc(c.line || '')}${c.bought_in ? `<br><span class="svk">bought in</span> ${esc(c.bought_in)}` : ''}</li>`).join('') + '</ul>';
    if (goods) goods += `<div class="muted">The land-use frame ${esc(ago(G.ago_kyr))}. Spare and lacking: the share of the cell's people who make a good beyond their own want, or want it and lack it at home (planet/lineages/trade.py).</div>`;
  }
  // rule
  const R = d.rule, card = (c) => `${esc(c.name)} <span class="muted">(${esc(c.tier)}${c.ruler ? `, ruled by ${esc(c.ruler)}` : ''})</span>`;
  const rule = R ? row('ruled by', R.now ? card(R.now) + (R.now.capital ? ' <b>its capital</b>' : '') + `, since ${esc(ago(R.now.founded_kyr))}` : 'no state rules it now')
    + row('before', R.past.slice(0, -1).reverse().slice(0, 6).filter(([, c]) => c).map(([a, c]) => `${card(c)} from ${esc(ago(a))}`).join('; ')) : '';
  // faith
  const F = d.faith;
  const faith = F ? F.held.map((f) => row('faith', `<span class="svbar" style="width:10px;background:${esc(f.color || '#888')}"></span>${esc(f.name)}${f.core ? ` <span class="muted">(${esc(f.core)})</span>` : ''}: held by ${esc(f.cultures.map((c) => c[1]).join(', '))}`)).join('') : '';
  // tongues
  const T = d.tongues;
  let tongue = '';
  if (T) {
    tongue += row('own tongues', esc(T.own.map((c) => c[1]).join(', ')));
    const oth = (T.others || []).filter((x) => x.share >= 0.05).sort((a, b) => b.share - a.share).slice(0, 8);
    tongue += row('also spoken', oth.map((x) => `${esc(x.name)} <span class="muted">(${esc(x.kind)}, ${pc(x.share)} of ${esc(x.culture_name)})</span>`).join('; '));
    tongue += row('trade tongue', (T.trade || []).map((x) => `${esc(x.name)} <span class="muted">(${esc(x.kind)}, since ${esc(ago(x.since_kyr || 0))}, ${x.towns} towns)</span>`).join('; '));
  }
  // history
  const hist = (d.history || []).length ? '<ul>' + d.history.map(([a, t]) => `<li><span class="muted">${esc(ago(a))}</span>: ${esc(t)}</li>`).join('') + '</ul>' : '';
  $('svBody').innerHTML = sec('Names', names) + sec('People', people) + sec('Goods made and bought', goods) + sec('Rule', rule) + sec('Faith', faith)
    + sec('Language', tongue) + sec('History', hist)
    + `<p class="muted">At ${esc(ago(d.ago_kyr))} (the time slider). Read from the run's settlements, goods ledger, exchange, polities, gods and tongues (planet/lineages/settlement_view.py); nothing here changes the run.</p>`;
}

let want = 0;
export async function openSite(id) {
  const v = S.V;
  if (!v?.run || v.run.kind !== 'peoples') return;
  const tok = ++want;
  box.hidden = false;
  $('svTitle').textContent = 'Settlement';
  $('svBody').innerHTML = '<span class="muted">Reading this place from the run (the first time for a run takes a minute or two: the goods, the polities and the tongues are worked out once)…</span>';
  try {
    const d = await (await fetch(`../api/settlement?run=${encodeURIComponent(v.dir)}&site=${id}&ago=${agoNow()}`, { cache: 'no-store' })).json();
    if (tok !== want || S.V !== v) return;
    if (d.error) { $('svBody').innerHTML = `<span class="muted">No view: ${esc(d.error)}</span>`; return; }
    render(d);
  } catch (e) { if (tok === want) $('svBody').innerHTML = `<span class="muted">No view: ${esc(e.message)}</span>`; }
}

// a click (not a drag) on a place's cell with the Settlements overlay on
let downAt = null;
renderer.domElement.addEventListener('pointerdown', (e) => { downAt = [e.clientX, e.clientY]; });
renderer.domElement.addEventListener('pointerup', (e) => {
  if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 4) return;
  if (!S.V?.settleByCell || !$('settlements')?.checked || !(S.hovered >= 0)) return;
  const s = siteAt(S.hovered);
  if (s) openSite(s.id);
});

// ?site=<id>: open that place's card once the run's places are loaded
const urlSite = new URLSearchParams(location.search).get('site');
if (urlSite != null) {
  const t = setInterval(() => { if (S.V?.settleDoc) { clearInterval(t); openSite(+urlSite); } }, 500);
  setTimeout(() => clearInterval(t), 120000);
}
