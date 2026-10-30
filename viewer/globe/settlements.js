// Settlements (planet/lineages/settlements.py, PW-1011): the villages, towns and cities of a peoples run, from settlements.json
// beside run.json. At the slider's moment a living site is a dot in its holder's colour (bigger for a town, bigger again with a
// white ring for a city), a ruin a small grey cross; the hover card lists the sites of the cell under the pointer.
// A second people's own place (kind 'minority', PW-1105: a dwarf hold in the humans' hills) is drawn like any other;
// a mine (kind 'mine') is a small diamond in its holder's colour, shown with the villages.
// At whole-globe view only the cities and city ruins show; the towns fade in as the camera closes in, then the villages,
// mines and lesser ruins (fadeSettlements, PW-1106: the owner found the towns too many at globe scale), and the 'villages'
// box turns the villages and mines off altogether. The hover card lists everything at any scale.
import { S, state } from './state.js';
import { $, camera } from './scene.js';
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
const isGone = (s, ago) => s.abandoned_kyr != null && ago <= s.abandoned_kyr + 1e-6;
const isRuin = (s, ago) => isGone(s, ago) && s.tier_now === 'ruin';  // (a minority's place that merged into the main place leaves none)
const nowAgo = () => -(S.V.run.frames[S.V.frame]?.t ?? 0);
const holderAt = (s, ago) => { let h = s.founded_by; for (const [a, p] of s.holders) if (a >= ago - 1e-6) h = p; return h; };

export function settlementOverlays(globe, wraps, ribbonObj, people) {
  const d = S.V.settleDoc, ago = nowAgo(), r0 = globe ? 1.013 : 1, minor = $('settleVillages')?.checked !== false;
  const col = new Map((S.V.run.meta.lineages || []).map((l) => [l.id, l.color]));
  const dots = [], dcols = [], tdots = [], tcols = [], vdots = [], vcols = [], rings = [], ruins = [], vruins = [], edges = [], tedges = [], mines = [], mcols = [];
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
    if (isGone(s, ago) && !isRuin(s, ago)) continue;  // (merged)
    if (isRuin(s, ago)) {  // (a city's ruin at every scale; a town's or a village's with the villages)
      const out = s.tier_peak === 'city' ? ruins : vruins;  // (a mine's too)
      if (out === vruins && !minor) continue;
      const h = 0.18, cl = Math.max(Math.cos(s.lat * Math.PI / 180), 0.2);
      for (const [a, b] of [[[-h, -h], [h, h]], [[-h, h], [h, -h]]]) {
        const p1 = llPos(s.lat + a[0], s.lon + a[1] / cl, r0), p2 = llPos(s.lat + b[0], s.lon + b[1] / cl, r0);
        if (!wraps(p1, p2)) out.push(...p1, ...p2);
      }
      continue;
    }
    const h = holderAt(s, ago);
    if (people != null && h !== people) continue;
    const t = s.kind === 'mine' ? 'mine' : TIER(popAt(s, ago), d), c = col.get(h) || '#dddddd';
    if ((t === 'village' || t === 'mine') && !minor) continue;
    const rgb = [parseInt(c.slice(1, 3), 16) / 255, parseInt(c.slice(3, 5), 16) / 255, parseInt(c.slice(5, 7), 16) / 255];
    if (t === 'mine') {  // (a diamond)
      const m = 0.2, cl = Math.max(Math.cos(s.lat * Math.PI / 180), 0.2);
      const P = [[m, 0], [0, m], [-m, 0], [0, -m], [m, 0]].map(([a, b]) => llPos(s.lat + a, s.lon + b / cl, r0));
      for (let k = 0; k < 4; k++) if (!wraps(P[k], P[k + 1])) { mines.push(...P[k], ...P[k + 1]); mcols.push(...rgb, ...rgb); }
      continue;
    }
    const rad = t === 'city' ? 0.55 : t === 'town' ? 0.33 : 0.14;
    if (t === 'village') { ring(s.lat, s.lon, rad, vdots, vcols, rgb); continue; }
    const [D, DC, E] = t === 'city' ? [dots, dcols, edges] : [tdots, tcols, tedges];
    for (let k = 1; k <= 3; k++) ring(s.lat, s.lon, rad * k / 3, D, DC, rgb);  // (filled: rings within rings)
    if (t === 'city') ring(s.lat, s.lon, rad * 1.35, rings, null, null);
    ring(s.lat, s.lon, rad * 1.12, E, null, null);  // (a dark edge: the dot reads on its own people's colour)
  }
  const own = (o, range) => {  // (its own material: its opacity follows the camera, fadeSettlements)
    o.material = o.material.clone(); o.material.userData = {}; o.material.transparent = true;
    o.userData.fade = o.material.opacity; o.userData.range = range;
    return o;
  };
  const out = { settleRuins: ribbonObj(ruins, 0x9a948a, 0.9, 1.5), settleEdges: ribbonObj(edges, 0x15120e, 0.9, 1.5),
    settleDots: ribbonObj(dots, 0xffffff, 1, 3, dcols), settleCities: ribbonObj(rings, 0xffffff, 1, 1.5) };
  if (tdots.length) { out.settleTowns = own(ribbonObj(tdots, 0xffffff, 1, 3, tcols), FADE_TOWN); out.settleTownEdges = own(ribbonObj(tedges, 0x15120e, 0.9, 1.5), FADE_TOWN); }
  if (vdots.length) out.settleVillages = own(ribbonObj(vdots, 0xffffff, 1, 3, vcols), FADE);
  if (vruins.length) out.settleVillageRuins = own(ribbonObj(vruins, 0x9a948a, 0.9, 1.5), FADE);
  if (mines.length) out.settleMines = own(ribbonObj(mines, 0xffffff, 1, 2.5, mcols), FADE);
  fadeSettlements(out);
  return out;
}

// The villages' (mines', lesser ruins') opacity at this camera: 0 while neighbouring cells are under FADE[0] pixels apart on
// screen (the whole globe: they would carpet the land), 1 from FADE[1] pixels (zoomed in: each dot stands alone). The towns
// (two cells apart or more) between FADE_TOWN's: at the default globe view (~9 px) they are still hidden.
const FADE = [18, 28], FADE_TOWN = [10, 16];
const FADED = ['settleTowns', 'settleTownEdges', 'settleVillages', 'settleVillageRuins', 'settleMines'];
export function villageFade(range = FADE) {
  if (!S.V?.n) return 0;
  const spacing = Math.sqrt(4 * Math.PI / S.V.n) * 180 / Math.PI;  // (degrees between neighbouring cells)
  const f = innerHeight / 2 / Math.tan(camera.fov * Math.PI / 360);  // (pixels per unit of distance at 1 unit away)
  const ppd = state.mode === 'globe' ? f / Math.max(camera.position.length() - 1, 1e-3) * Math.PI / 180 : f / Math.max(camera.position.z, 1e-3) / 90;
  return Math.min(Math.max((ppd * spacing - range[0]) / (range[1] - range[0]), 0), 1);
}
export function fadeSettlements(o = S.overlays) {
  if (!o || !FADED.some((k) => o[k])) return;
  for (const x of FADED.map((k) => o[k])) {
    if (!x) continue;
    const a = villageFade(x.userData.range);
    x.visible = a > 0.01;
    x.material.opacity = a * x.userData.fade;
    x.material.resolution.set(innerWidth, innerHeight);
  }
}

// a people's plural name ('the humans', 'the dwarves'), without its note in brackets ('elves (from the feywild)')
const name = (id) => {
  S.V.lineById ??= new Map((S.V.run.meta.lineages || []).map((x) => [x.id, x]));
  return (S.V.lineById.get(id)?.name || String(id).replace(/_/g, ' ')).replace(/ \(.*\)$/, '');
};
const n0 = (x) => Math.round(x).toLocaleString('en-US');
const yrs = (kyr) => (kyr >= 1 ? `${+kyr.toFixed(1)} kyr` : `${Math.max(100, Math.round(kyr * 10) * 100)} years`);
// the hover card: the sites of cell i at the slider's moment (the living one first, then the ruins)
export function settlementRows(i, R) {
  const list = S.V.settleByCell?.get(i);
  if (!list) return;
  const ago = nowAgo(), d = S.V.settleDoc;
  for (const s of list) {
    if (ago > s.founded_kyr + 1e-6 || (isGone(s, ago) && !isRuin(s, ago))) continue;
    const by = `founded ~${yrs(s.founded_kyr)} ago by the ${name(s.founded_by)}${s.ruin_of != null ? ' on older ruins' : ''}`;
    if (isRuin(s, ago)) {
      R('place', '', `ruin of a ${s.tier_peak}${s.kind === 'minority' ? ' (a second people\'s own place)' : ''} of the ${name(holderAt(s, s.abandoned_kyr))} (at most ~${n0(s.peak_pop)} people); ${by}; abandoned ~${yrs(s.abandoned_kyr)} ago: ${esc(s.why)}`,
        { lab: 'settlement', ess: true });
      continue;
    }
    const h = holderAt(s, ago), p = popAt(s, ago), hands = s.holders.filter(([a]) => a >= ago - 1e-6).slice(1);
    const who = Object.entries(s.who).map(([k, v]) => `${name(k)} ${v}%`).join(', ');
    const q = s.quarters.map((x) => `a ${String(x.group).replace(/_/g, ' ')} quarter (${x.pct}%)`).join(', ');  // (the group's id: 'a city kobold quarter')
    const what = s.kind === 'mine' ? 'mine' : s.kind === 'minority' ? `${TIER(p, d)} (their own place, as a second people here)` : TIER(p, d);
    R('place', '', `${what} of the ${name(h)}, ~${n0(p)} people; ${by}${hands.length ? `; changed hands: ${hands.map(([a, x]) => `the ${name(x)} ~${yrs(a)} ago`).join(', ')}` : ''}`
      + `${s.abandoned_kyr != null ? `; left ~${yrs(s.abandoned_kyr)} ago (${esc(s.why)})` : ''}`, { lab: 'settlement', ess: true });
    if (who) R('place', '', `${who}${q ? `; ${q}` : ''} (${s.who_when})`, { lab: 'its people', ess: true });
  }
}
