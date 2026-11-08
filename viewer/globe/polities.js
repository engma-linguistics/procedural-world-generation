// Polities (planet/lineages/polities.py, PW-1431): who rules where in a peoples run, read after the run (GET /api/polities).
// The 'polities' layer colours each ruled cell by its polity (its ruling culture's colour, shaded per polity), darker on its
// borders; chiefdoms (one town and its cell) paler; land no one rules grey. The map is the century step nearest the slider's frame,
// fetched one step at a time (?ago=); the polities themselves (the state cards) come once per run. Clicking a cell shows its
// polity's card in the info box (polityRows): name, tier, ruling culture, subject cultures, founded, fell, capital; with war v0
// (PW-1432) also "this land: taken from X", the fall ("conquered by Y" / "collapsed") and its conquests.
import * as THREE from 'three';
import { esc } from '../planets.js';
import { S, state } from './state.js';
import { paint } from './geometry.js';
import { renderLegend } from './panel.js';

const NOBODY = new THREE.Color('#5a5a52'), OCEAN = new THREE.Color('#1c2a3c'), ICE = new THREE.Color('#dfe8ee'), BLACK = new THREE.Color('#000000');
const WHITE = new THREE.Color('#ffffff');
const agoNow = () => Math.max(0, -(S.V.run.frames[S.V.frame]?.t ?? 0));
const n0 = (x) => Math.round(x).toLocaleString('en');
// a span of [[kyr ago, ...], ...] (oldest first) in force at ago; a polity's name then (PW-1451: the people holding its capital names it)
const spanAt = (sp, ago) => (sp || []).reduce((o, s) => (s[0] >= ago - 1e-6 ? s : o), (sp || [])[0]);
export const nameAt = (rec, ago) => spanAt(rec?.names, ago)?.[1] ?? rec?.name;

// an invasion saved in the workbench (invasiontab.js, PW-1433) remakes the run's polities: drop them and fetch again
try {
  new BroadcastChannel('pw-polities').onmessage = (e) => {
    const v = S.V, run = e.data?.run;
    if (!v?.run || (run && run !== v.dir && !String(v.dir).endsWith(`/${run}`))) return;
    v.polDoc = null; v.polStep = null; v.polDocF = false; v.polStepF = null;
    if (state.layer === 'polities') { loadPolities(); paint(); renderLegend(); }
  };
} catch (e) { /* no BroadcastChannel: the globe shows the new polities when the run is opened again */ }

// the run's polities (once), then the step for this frame (again whenever the frame's nearest step changes)
export function loadPolities() {
  const v = S.V;
  if (!v?.run || v.run.kind !== 'peoples' || !v.run.meta?.settlements) return;
  const id = encodeURIComponent(v.dir);
  if (!v.polDoc && !v.polDocF) {
    v.polDocF = true;
    fetch(`../api/polities?run=${id}`, { cache: 'no-store' }).then((r) => r.json()).then((j) => {
      if (S.V !== v) return;
      v.polDocF = false;
      if (j.error) { v.polDoc = { error: j.error, steps: [], polities: [], cultures: {} }; renderLegend(); return; }
      v.polDoc = j;
      loadPolities();
      renderLegend();
    }).catch((e) => { v.polDocF = false; console.error(e); });
    return;
  }
  const D = v.polDoc;
  if (!D || !D.steps?.length) return;
  const ago = agoNow();
  let k = 0;
  D.steps.forEach((s, i) => { if (Math.abs(s.ago - ago) < Math.abs(D.steps[k].ago - ago)) k = i; });
  if (v.polStep?.k === k || v.polStepF === k) return;
  v.polStepF = k;
  fetch(`../api/polities?run=${id}&ago=${D.steps[k].ago}`, { cache: 'no-store' }).then((r) => r.json()).then((j) => {
    if (S.V !== v) return;
    v.polStepF = null;
    if (j.error) { console.error(j.error); return; }
    const owner = new Int32Array(v.n).fill(-1), from = new Int32Array(v.n).fill(-1), here = new Map();
    for (const p of j.polities) {
      for (const c of p.cells) owner[c] = p.id;
      for (const [r, cs] of Object.entries(p.provinces || {})) for (const c of cs) from[c] = +r;  // (land war took: the polity it was taken from)
      here.set(p.id, { ...p, size: p.cells.length, cells: undefined, provinces: undefined });
    }
    const nbr = v.grid.nbr, edge = new Uint8Array(v.n);
    for (let i = 0; i < v.n; i++) if (owner[i] >= 0) for (const b of nbr[i]) if (owner[b] !== owner[i]) { edge[i] = 1; break; }
    v.polStep = { k, ago: j.ago, owner, from, edge, here };
    if (state.layer === 'polities') { paint(); renderLegend(); }
    loadPolities();  // (the slider may have moved on meanwhile)
  }).catch((e) => { v.polStepF = null; console.error(e); });
}

export function politiesColor(i, c) {
  const L = S.V.layers, P = S.V.polStep, D = S.V.polDoc;
  if (L.ice && L.ice[i] > 0) return c.copy(ICE);
  const o = P ? P.owner[i] : -1;
  if (o < 0) return L.elevation[i] <= 0 ? c.copy(OCEAN) : c.copy(NOBODY);
  const rec = D.polities[o], h = P.here.get(o);
  const col = rec._c ||= new THREE.Color(rec.color || '#999999');
  c.copy(col);
  if (h?.tier === 'chiefdom') c.lerp(WHITE, 0.35).lerp(NOBODY, 0.25);
  if (P.edge[i]) c.lerp(BLACK, 0.45);
  return c;
}

// the legend: this step's counts, then the biggest polities
export function politiesLegend(sw) {
  const D = S.V.polDoc, P = S.V.polStep;
  if (!D) return '<span class="muted">reading the polities from the settlements, techs and cultures (about half a minute the first time)…</span>';
  if (D.error) return `<span class="muted">${esc(D.error)}</span>`;
  if (!P) return '<span class="muted">loading this century\'s map…</span>';
  const st = D.steps[P.k], cnt = Object.entries(st.counts).filter(([, n]) => n).map(([t, n]) => `${n} ${t}${n > 1 ? 's' : ''}`).join(', ') || 'none yet';
  const big = [...P.here.values()].filter((h) => h.tier !== 'chiefdom').sort((a, b) => b.size - a.size).slice(0, 10);
  const war = [st.taken ? `${st.taken} taken by war` : '', st.collapsed ? `${st.collapsed} fell apart` : ''].filter(Boolean).join(', ');
  const iv = D.invasions?.rows || [], ivTxt = iv.length ? `<br>${iv.length} invasion${iv.length > 1 ? 's' : ''} you scheduled, ${iv.filter((r) => r.happened).length} happened (workbench, States &amp; war)` : '';
  return `${esc(globalThis.NumFmt.ago(P.ago))}: ${esc(cnt)}${war ? `; this century ${esc(war)}` : ''}${ivTxt}<br>` + big.map((h) => sw(D.polities[h.id].color, `${esc(nameAt(D.polities[h.id], P.ago))} (${h.tier}, ${n0(h.size * D.cell_km2)} km²)`)).join('') +
    sw('#5a5a52', 'no one rules here') + '<span class="muted">The century nearest this frame. A polity holds the peopled land within its reach (travel from its capital); ' +
    'the bigger, stronger seats claim first. Chiefdoms (one town and its cell) are pale; borders dark. An empire is a state where another culture holds a fifth or more of its people; ' +
    'a dragon realm is ruled by a dragon culture. A people with kings or law but no city may still band its villages into a confederation beside a foreign state or dragon realm. War: a state at least half again as strong as a neighbour may take all of it (its farmers keep farming); ' +
    'a state also falls apart by chance, about as often as history\'s (Arbesman 2011), and a dragon realm when its ruler dies. Click a cell for its card. (planet/lineages/polities.py, read after the run)</span>';
}

// the polity card: rows for the info box of cell i (describe.js cellInfo)
export function polityRows(i, R) {
  const P = S.V.polStep, D = S.V.polDoc;
  if (!P || !D || D.error) return;
  const o = P.owner[i], ess = state.layer === 'polities';
  if (o < 0) { if (ess) R('place', '', `no one rules here ${globalThis.NumFmt.ago(P.ago)}`, { lab: 'polity', ess }); return; }
  const rec = D.polities[o], h = P.here.get(o), C = D.cultures, ago = globalThis.NumFmt.ago;
  const cname = (u) => C[u]?.name || u;
  const ruler = [...rec.rulers].reverse().find(([a]) => a >= P.ago - 1e-6) || rec.rulers[0];
  const held = spanAt(rec.peoples, P.ago), founder = rec.peoples?.[0];
  R('place', '', `${nameAt(rec, P.ago)}: a ${h.tier}, ${n0(h.size * D.cell_km2)} km², ~${n0(h.people)} people in its towns and villages`, { lab: 'polity', ess: true });
  if (ruler) R('place', 'ruled by', `${cname(ruler[1])}${rec.kind === 'dragon' ? ' (one dragon rules absolutely)' : ''}`, { ess: true });
  const subj = Object.entries(h.subjects || {}).sort((a, b) => b[1] - a[1]);
  if (subj.length) R('place', 'subjects', subj.slice(0, 6).map(([u, n]) => `${cname(u)}${n ? ` (~${n0(n)})` : ''}`).join(', ') + (subj.length > 6 ? `, + ${subj.length - 6} more` : ''), { ess: true });
  if (held && rec.kind !== 'dragon') R('place', 'its people', `the ${held[2]} hold its capital` + (rec.peoples.length > 1 ? `, since ${ago(held[0])}` : ''), { ess: true });
  const cf = (rec.confed || []).find(([a]) => Math.abs(a - P.ago) < 1e-6);
  if (cf) R('place', 'confederation', `no city of its own: ~${n0(cf[1])} of the ${held?.[2] || 'people'} in villages and camps within its reach banded together beside a foreign state or dragon realm`, { ess: true });
  R('place', 'founded', ago(rec.founded_kyr) + (founder && held && founder[1] !== held[1] ? ` by the ${founder[2]}` : ''), { ess: true });
  if (rec.peoples?.length > 1) R('place', 'held by', rec.peoples.map(([a, , n]) => `the ${n} ${ago(a)}`).join(', then '), { ess: false });
  const fr = P.from[i];
  if (fr >= 0 && D.polities[fr]) R('place', 'this land', `taken from ${nameAt(D.polities[fr], D.polities[fr].fell_kyr)} ${ago(D.polities[fr].fell_kyr)}`, { ess: true });
  R('place', 'fell', rec.fell_kyr != null ? `${ago(rec.fell_kyr)}: ${rec.fell_why}` : 'still stands', { ess: true });
  const took = (rec.took || []).filter(([a]) => a >= P.ago - 1e-6);
  if (took.length) R('place', 'conquests', took.slice(-6).reverse().map(([a, r, how]) => `${D.polities[r] ? nameAt(D.polities[r], a) : r} ${ago(a)}${how === 'invasion' ? ' (an invasion)' : ''}`).join(', ') + (took.length > 6 ? `, + ${took.length - 6} earlier` : ''), { ess: true });
  const cap = rec.capital;
  R('place', 'capital', `${rec.kind === 'dragon' ? 'the dragons\' lair' : 'a town of the ' + (held?.[2] || rec.people_name || rec.people)} in ${cap.place || 'cell ' + cap.cell} (cell ${cap.cell}, lat ${cap.lat}, lon ${cap.lon})`, { ess });
  if (rec.tiers.length > 1) R('place', 'tiers', rec.tiers.map(([a, t]) => `${t} ${ago(a)}`).join(', '), { ess: false });
}
