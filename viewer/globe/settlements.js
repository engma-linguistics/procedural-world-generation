// Settlements (planet/lineages/settlements.py, PW-1011): the villages, towns and cities of a peoples run, from settlements.json
// beside run.json. At the slider's moment a living site is a dot in its holder's colour (bigger for a town, bigger again with a
// white ring for a city), a ruin a small grey cross; the hover card lists the sites of the cell under the pointer.
import { S } from './state.js';
import { llPos } from './geometry.js';
import { esc } from '../planets.js';

export async function loadSettlements() {
  if (!S.V?.run?.meta?.settlements || S.V.settleDoc) return;
  const v = S.V;
  try {
    const j = await (await fetch(v.base + v.run.meta.settlements.file, { cache: 'no-store' })).json();
    if (S.V !== v) return;
    S.V.settleDoc = j;
    S.V.settlements = j.sites;
    const by = new Map();
    for (const s of j.sites) { if (!by.has(s.cell)) by.set(s.cell, []); by.get(s.cell).push(s); }
    S.V.settleByCell = by;
  } catch (e) { console.error(e); }
}
const TIER = (pop, d) => (pop >= d.tiers.city[0] ? 'city' : pop >= d.tiers.town[0] ? 'town' : 'village');
// the site's people at `ago` kyr (its series, newest last), 0 before its founding or after it was left
export function popAt(s, ago) {
  if (ago > s.founded_kyr + 1e-6 || (s.abandoned_kyr != null && ago <= s.abandoned_kyr + 1e-6)) return 0;
  const sr = s.series;
  for (let k = 1; k < sr.length; k++) {
    if (sr[k][0] <= ago) { const [a0, p0] = sr[k - 1], [a1, p1] = sr[k]; const w = a0 === a1 ? 1 : (a0 - ago) / (a0 - a1); return p0 + (p1 - p0) * w; }
  }
  return sr.at(-1)[1];
}
const isRuin = (s, ago) => s.abandoned_kyr != null && ago <= s.abandoned_kyr + 1e-6;
const nowAgo = () => -(S.V.run.frames[S.V.frame]?.t ?? 0);
const holderAt = (s, ago) => { let h = s.founded_by; for (const [a, p] of s.holders) if (a >= ago - 1e-6) h = p; return h; };

export function settlementOverlays(globe, wraps, ribbonObj, people) {
  const d = S.V.settleDoc, ago = nowAgo(), r0 = globe ? 1.013 : 1;
  const col = new Map((S.V.run.meta.lineages || []).map((l) => [l.id, l.color]));
  const dots = [], dcols = [], rings = [], ruins = [], edges = [];
  const ring = (la, lo, rad, out, cols, rgb) => {
    const cl = Math.max(Math.cos(la * Math.PI / 180), 0.2);
    let p1 = llPos(la + rad, lo, r0);
    for (let k = 1; k <= 12; k++) {
      const a = k / 12 * 2 * Math.PI, p2 = llPos(la + rad * Math.cos(a), lo + rad * Math.sin(a) / cl, r0);
      if (!wraps(p1, p2)) { out.push(...p1, ...p2); if (cols) cols.push(...rgb, ...rgb); }
      p1 = p2;
    }
  };
  for (const s of d.sites) {
    if (ago > s.founded_kyr + 1e-6) continue;  // (not yet founded)
    if (isRuin(s, ago)) {
      const h = 0.18, cl = Math.max(Math.cos(s.lat * Math.PI / 180), 0.2);
      for (const [a, b] of [[[-h, -h], [h, h]], [[-h, h], [h, -h]]]) {
        const p1 = llPos(s.lat + a[0], s.lon + a[1] / cl, r0), p2 = llPos(s.lat + b[0], s.lon + b[1] / cl, r0);
        if (!wraps(p1, p2)) ruins.push(...p1, ...p2);
      }
      continue;
    }
    const h = holderAt(s, ago);
    if (people != null && h !== people) continue;
    const t = TIER(popAt(s, ago), d), c = col.get(h) || '#dddddd';
    const rgb = [parseInt(c.slice(1, 3), 16) / 255, parseInt(c.slice(3, 5), 16) / 255, parseInt(c.slice(5, 7), 16) / 255];
    const rad = t === 'city' ? 0.55 : t === 'town' ? 0.33 : 0.14;
    for (let k = 1; k <= (t === 'village' ? 1 : 3); k++) ring(s.lat, s.lon, rad * k / (t === 'village' ? 1 : 3), dots, dcols, rgb);  // (filled: rings within rings)
    if (t === 'city') ring(s.lat, s.lon, rad * 1.35, rings, null, null);
    if (t !== 'village') ring(s.lat, s.lon, rad * 1.12, edges, null, null);  // (a dark edge: the dot reads on its own people's colour)
  }
  return { settleRuins: ribbonObj(ruins, 0x9a948a, 0.9, 1.5), settleEdges: ribbonObj(edges, 0x15120e, 0.9, 1.5),
    settleDots: ribbonObj(dots, 0xffffff, 1, 3, dcols), settleCities: ribbonObj(rings, 0xffffff, 1, 1.5) };
}

const name = (id) => String(id).replace(/_/g, ' ');
const n0 = (x) => Math.round(x).toLocaleString('en-US');
const yrs = (kyr) => (kyr >= 1 ? `${+kyr.toFixed(1)} kyr` : `${Math.max(100, Math.round(kyr * 10) * 100)} years`);
// the hover card: the sites of cell i at the slider's moment (the living one first, then the ruins)
export function settlementRows(i, R) {
  const list = S.V.settleByCell?.get(i);
  if (!list) return;
  const ago = nowAgo(), d = S.V.settleDoc;
  for (const s of list) {
    if (ago > s.founded_kyr + 1e-6) continue;
    const by = `founded ~${yrs(s.founded_kyr)} ago by the ${name(s.founded_by)}${s.ruin_of != null ? ' on older ruins' : ''}`;
    if (isRuin(s, ago)) {
      R('place', '', `ruin of a ${s.tier_peak} of the ${name(holderAt(s, s.abandoned_kyr))} (at most ~${n0(s.peak_pop)} people); ${by}; abandoned ~${yrs(s.abandoned_kyr)} ago: ${esc(s.why)}`,
        { lab: 'settlement', ess: true });
      continue;
    }
    const h = holderAt(s, ago), p = popAt(s, ago), hands = s.holders.filter(([a]) => a >= ago - 1e-6).slice(1);
    const who = Object.entries(s.who).map(([k, v]) => `${name(k)} ${v}%`).join(', ');
    const q = s.quarters.map((x) => `a ${name(x.group)} quarter (${x.pct}%)`).join(', ');
    R('place', '', `${TIER(p, d)} of the ${name(h)}, ~${n0(p)} people; ${by}${hands.length ? `; changed hands: ${hands.map(([a, x]) => `the ${name(x)} ~${yrs(a)} ago`).join(', ')}` : ''}`
      + `${s.abandoned_kyr != null ? `; left ~${yrs(s.abandoned_kyr)} ago (${esc(s.why)})` : ''}`, { lab: 'settlement', ess: true });
    if (who) R('place', '', `${who}${q ? `; ${q}` : ''} (${s.who_when})`, { lab: 'its people', ess: true });
  }
}
