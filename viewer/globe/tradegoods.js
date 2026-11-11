// The trade goods layer (PW-1508): pick a good and the globe shows, per peopled cell, where it is spare (green: its people make it beyond
// their own want) and where it is lacking (red: its people want it and lack it at home), at the land-use frame nearest the slider (the
// last ~12,500 years, every 500), from GET /api/trade?good=&ago= (planet/lineages/settlement_view.py over trade.py's per-cell ledger).
// A cell with both shows the larger; a peopled cell with neither is pale grey. Link: ?layer=trade%20goods&good=tin
import * as THREE from 'three';
import { esc } from '../planets.js';
import { S, state } from './state.js';
import { paint } from './geometry.js';
import { renderLegend } from './panel.js';

state.tradeGood = new URLSearchParams(location.search).get('good') || 'salt';
const OCEAN = new THREE.Color('#1c2a3c'), ICE = new THREE.Color('#dfe8ee'), EMPTY = new THREE.Color('#4a4a44'), NONE = new THREE.Color('#9a9a90');
const GREEN = new THREE.Color('#1fa83a'), RED = new THREE.Color('#d8312a');
const agoNow = () => Math.max(0, -(S.V.run.frames[S.V.frame]?.t ?? 0));

export function loadTradeGood() {
  const v = S.V;
  if (!v?.run || v.run.kind !== 'peoples') return null;
  const key = `${state.tradeGood}@${Math.round(agoNow() * 2) / 2}`;
  v.tradeGood ??= new Map();
  if (v.tradeGood.has(key)) return v.tradeGood.get(key);
  if (v.tradeGoodBusy === key) return null;
  v.tradeGoodBusy = key;
  fetch(`../api/trade?run=${encodeURIComponent(v.dir)}&good=${encodeURIComponent(state.tradeGood)}&ago=${agoNow()}`, { cache: 'no-store' })
    .then((r) => r.json()).then((j) => {
      if (S.V !== v) return;
      v.tradeGoodBusy = null;
      if (!j.error) {
        const spare = new Int8Array(v.n).fill(-1), lack = new Int8Array(v.n);
        j.cells.forEach((c, k) => { spare[c] = j.spare[k]; lack[c] = j.lacking[k]; });
        j.spareOf = spare; j.lackOf = lack;
        j.nSpare = j.spare.filter((x) => x >= 2).length; j.nLack = j.lacking.filter((x) => x >= 2).length;
      }
      v.tradeGoods = j.goods || v.tradeGoods;
      v.tradeGood.set(key, j);
      if (state.layer === 'trade goods') { paint(); renderLegend(); }
    }).catch((e) => { v.tradeGoodBusy = null; console.error(e); });
  return null;
}

export function tradeGoodColor(i, c) {
  const L = S.V.layers, D = S.V.tradeGood?.get(`${state.tradeGood}@${Math.round(agoNow() * 2) / 2}`);
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  if (L.elevation[i] <= 0 && !(D?.spareOf && D.spareOf[i] >= 0)) return c.copy(OCEAN);
  if (!D?.spareOf || D.spareOf[i] < 0) return c.copy(EMPTY);
  const s = D.spareOf[i], l = D.lackOf[i];
  if (s < 2 && l < 2) return c.copy(NONE);
  const t = 0.25 + 0.75 * Math.min(Math.max(s, l), 100) / 100;
  return c.copy(NONE).lerp(s >= l ? GREEN : RED, t);
}

export function tradeGoodLegend(sw) {
  const D = loadTradeGood() || S.V.tradeGood?.get(`${state.tradeGood}@${Math.round(agoNow() * 2) / 2}`);
  const G = S.V.tradeGoods;
  const opts = G ? Object.entries(G).map(([g, x]) => `<option value="${esc(g)}"${g === state.tradeGood ? ' selected' : ''}>${esc(x.label)} (${esc(x.class)})</option>`).join('')
    : `<option>${esc(state.tradeGood)}</option>`;
  const pick = `<label title="The good to show">good <select data-tradegood>${opts}</select></label><br>`;
  if (!D) return pick + '<span class="muted">working out the goods ledger (a minute the first time for a run)…</span>';
  if (D.error) return pick + `<span class="muted">${esc(D.error)}</span>`;
  return pick + sw('#1fa83a', 'spare (made beyond the people\'s own want)') + sw('#d8312a', 'lacking (wanted, not had at home)') + sw('#9a9a90', 'neither') + sw('#4a4a44', 'no one lives here')
    + `<span class="muted">${esc(D.label)} ${esc(globalThis.NumFmt?.ago ? globalThis.NumFmt.ago(D.ago_kyr || 0.0001) : D.ago_kyr + ' kyr ago')} (the land-use frame nearest the slider): spare in ${D.nSpare.toLocaleString('en')} cells, lacking in ${D.nLack.toLocaleString('en')}. `
    + 'The deeper the colour, the larger the share of the cell\'s people. Read after the run from the goods ledger (planet/lineages/trade.py): what would be traded, not what is.</span>';
}

document.addEventListener('change', (e) => {
  if (!e.target.matches?.('[data-tradegood]') || !S.V?.run) return;
  state.tradeGood = e.target.value;
  const u = new URL(location); u.searchParams.set('good', state.tradeGood); history.replaceState(null, '', u);
  loadTradeGood();
  paint(); renderLegend();
});
