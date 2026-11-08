// Trade routes (planet/lineages/trade_routes.py, PW-1504): the big flows of goods between cultures as lines on the map, and the towns
// they pass through as trading towns, at the slider's moment (GET /api/trade?routes=1&ago=: the land-use window's frame nearest it, every
// 500 years over the last ~12,500). A line is one stretch between two cells that most of a big flow takes: wider for a bigger share of
// that kind of goods' trade between cultures, coloured by the kind of goods (food, salt, metal, fine goods, raw goods). A trading town is
// a ring in the colour of its kind (port, caravan town, river port, market town); its hover card says what passes and whose merchants
// live there. Read after the run: it does not change the history. Link: ?trade=routes
import { S, state } from './state.js';
import { $ } from './scene.js';
import { cellPositions, llPos } from './geometry.js';
import { esc } from '../planets.js';

export const GROUP_COL = { food: '#f2c14e', salt: '#f4f4f4', metal: '#e07a3a', precious: '#c86be0', raw: '#7fbf5a' };
export const KIND_COL = { port: '#4fb3ff', 'caravan town': '#f5a301', 'river port': '#5ff0e6', 'market town': '#ffffff' };
const GROUP_LAB = { food: 'food', salt: 'salt', metal: 'metal', precious: 'fine goods', raw: 'raw goods' };
const agoNow = () => Math.max(0, -(S.V.run.frames[S.V.frame]?.t ?? 0));

// the routes of the frame nearest the slider (fetched once per frame; the first fetch for a run works out its exchange, a minute or two)
export function loadTradeRoutes(onReady) {
  const v = S.V;
  if (!v?.run || v.run.kind !== 'peoples' || !$('tradeRoutes')?.checked) return null;
  v.tradeRoutes ??= new Map();
  const key = Math.round(agoNow() * 2) / 2;
  if (v.tradeRoutes.has(key)) return v.tradeRoutes.get(key);
  if (v.tradeBusy === key) return null;
  v.tradeBusy = key;
  status('working out the trade routes (a minute or two the first time for a run)…');
  fetch(`../api/trade?run=${encodeURIComponent(v.dir)}&routes=1&ago=${key}`, { cache: 'no-store' }).then((r) => r.json()).then((j) => {
    if (S.V !== v) return;
    v.tradeBusy = null;
    v.tradeRoutes.set(key, j.error ? { error: j.error, routes: [], hubs: [] } : j);
    onReady();
  }).catch((e) => { v.tradeBusy = null; console.error(e); status('no trade routes: ' + e.message); });
  return null;
}
function status(t) { const el = $('tradeStatus'); if (el) el.innerHTML = t; }

export function tradeOverlays(globe, ribbonObj, onReady) {
  const D = loadTradeRoutes(onReady);
  if (!D) return {};
  if (D.error) { status(`no trade routes: ${esc(D.error)}`); return {}; }
  if (D.ago_kyr == null) { status('no trade routes at this moment: they are read over the last ~12,500 years (the land-use window)'); return {}; }
  const G = S.V.grid, pos = cellPositions(globe ? 1.011 : 1), out = {};
  const lines = {};  // (group -> width bucket -> segment points)
  for (const [a, b, st, g] of D.routes) {
    if (!globe && Math.abs(pos[3 * a] - pos[3 * b]) > 2) continue;  // (across the dateline)
    const w = st >= 0.15 ? 2 : st >= 0.05 ? 1 : 0;
    ((lines[D.groups[g]] ??= [[], [], []])[w]).push(pos[3 * a], pos[3 * a + 1], pos[3 * a + 2], pos[3 * b], pos[3 * b + 1], pos[3 * b + 2]);
  }
  for (const [g, ws] of Object.entries(lines)) ws.forEach((pts, w) => { if (pts.length) out[`trade_${g}_${w}`] = ribbonObj(pts, parseInt(GROUP_COL[g].slice(1), 16), 0.95, [2, 3.5, 5.5][w]); });
  const r0 = globe ? 1.014 : 1, rings = {};
  for (const h of D.hubs) {
    const la = G.lat[h.cell], lo = G.lon[h.cell], cl = Math.max(Math.cos(la * Math.PI / 180), 0.2), rad = 0.5 + 2.5 * Math.min(h.strength, 0.3);
    const arr = (rings[h.kind] ??= []);
    let p1 = llPos(la + rad, lo, r0);
    for (let k = 1; k <= 16; k++) {
      const t = k / 16 * 2 * Math.PI, p2 = llPos(la + rad * Math.cos(t), lo + rad * Math.sin(t) / cl, r0);
      if (globe || Math.abs(p1[0] - p2[0]) < 2) arr.push(...p1, ...p2);
      p1 = p2;
    }
  }
  for (const [k, pts] of Object.entries(rings)) out[`tradeHub_${k}`] = ribbonObj(pts, parseInt(KIND_COL[k].slice(1), 16), 1, 2.5);
  const nk = (k) => D.hubs.filter((h) => h.kind === k).length;
  const sw = (c, t) => `<span style="display:inline-block;width:10px;height:3px;background:${c};vertical-align:middle;margin-right:3px"></span>${t}`;
  status(`${esc(globalThis.NumFmt?.ago ? globalThis.NumFmt.ago(D.ago_kyr || 0.0001) : D.ago_kyr + ' kyr ago')}: ${D.routes.length} stretches, ${D.hubs.length} trading towns<br>`
    + Object.keys(GROUP_COL).map((g) => sw(GROUP_COL[g], GROUP_LAB[g])).join(' ') + '<br>'
    + Object.keys(KIND_COL).map((k) => sw(KIND_COL[k], `${k} ${nk(k)}`)).join(' '));
  return out;
}

// the hover card: a trading town in this cell at the slider's frame
export function tradeRows(i, R) {
  if (!$('tradeRoutes')?.checked || !S.V.tradeRoutes) return;
  const D = S.V.tradeRoutes.get(Math.round(agoNow() * 2) / 2);
  const h = D?.hubs?.find((x) => x.cell === i);
  if (!h) return;
  const goods = h.goods.map((g) => g.replace(/_/g, ' ')).join(', ');
  const q = h.quarters.length ? `; a merchant quarter of the ${h.quarters.map((x) => esc(x[1])).join(', the ')}` : '';
  R('place', '', `${esc(h.kind)} of the ${esc(h.culture_name || 'unknown')} (${esc(h.place || 'here')}, ~${Math.round(h.people).toLocaleString('en')} people): `
    + `${esc(goods)} pass through, by ${esc(h.modes.join(', '))}${q}`, { lab: 'trading town', ess: true });
}
