// Polities (planet/lineages/polities.py, PW-1431): who rules where in a peoples run, read after the run (GET /api/polities).
// The 'polities' layer colours each ruled cell by its polity (its ruling culture's colour, shaded per polity), darker on its
// borders; chiefdoms (one town and its cell) paler; land no one rules grey. The map is the century step nearest the slider's frame,
// fetched one step at a time (?ago=); the polities themselves (the state cards) come once per run. Clicking a cell shows its
// polity's card in the info box (polityRows): name, tier, ruling culture, subject cultures, founded, fell, capital.
import * as THREE from 'three';
import { esc } from '../planets.js';
import { S, state } from './state.js';
import { paint } from './geometry.js';
import { renderLegend } from './panel.js';

const NOBODY = new THREE.Color('#5a5a52'), OCEAN = new THREE.Color('#1c2a3c'), ICE = new THREE.Color('#dfe8ee'), BLACK = new THREE.Color('#000000');
const WHITE = new THREE.Color('#ffffff');
const agoNow = () => Math.max(0, -(S.V.run.frames[S.V.frame]?.t ?? 0));
const n0 = (x) => Math.round(x).toLocaleString('en');

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
    const owner = new Int32Array(v.n).fill(-1), here = new Map();
    for (const p of j.polities) { for (const c of p.cells) owner[c] = p.id; here.set(p.id, { ...p, size: p.cells.length, cells: undefined }); }
    const nbr = v.grid.nbr, edge = new Uint8Array(v.n);
    for (let i = 0; i < v.n; i++) if (owner[i] >= 0) for (const b of nbr[i]) if (owner[b] !== owner[i]) { edge[i] = 1; break; }
    v.polStep = { k, ago: j.ago, owner, edge, here };
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
  return `${esc(globalThis.NumFmt.ago(P.ago))}: ${esc(cnt)}<br>` + big.map((h) => sw(D.polities[h.id].color, `${esc(D.polities[h.id].name)} (${h.tier}, ${n0(h.size * D.cell_km2)} km²)`)).join('') +
    sw('#5a5a52', 'no one rules here') + '<span class="muted">The century nearest this frame. A polity holds the peopled land within its reach (travel from its capital); ' +
    'the bigger, stronger seats claim first. Chiefdoms (one town and its cell) are pale; borders dark. An empire is a state where another culture holds a fifth or more of its people; ' +
    'a dragon realm is ruled by a dragon culture. Click a cell for its card. (planet/lineages/polities.py, read after the run)</span>';
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
  R('place', '', `${rec.name}: a ${h.tier}, ${n0(h.size * D.cell_km2)} km², ~${n0(h.people)} people in its towns and villages`, { lab: 'polity', ess: true });
  if (ruler) R('place', 'ruled by', `${cname(ruler[1])}${rec.kind === 'dragon' ? ' (one dragon rules absolutely)' : ''}`, { ess: true });
  const subj = Object.entries(h.subjects || {}).sort((a, b) => b[1] - a[1]);
  if (subj.length) R('place', 'subjects', subj.slice(0, 6).map(([u, n]) => `${cname(u)}${n ? ` (~${n0(n)})` : ''}`).join(', ') + (subj.length > 6 ? `, + ${subj.length - 6} more` : ''), { ess: true });
  R('place', 'founded', ago(rec.founded_kyr), { ess: true });
  R('place', 'fell', rec.fell_kyr != null ? `${ago(rec.fell_kyr)} (${rec.fell_why})` : 'still stands', { ess: true });
  const cap = rec.capital;
  R('place', 'capital', `${rec.kind === 'dragon' ? 'the dragons\' lair' : 'a town of the ' + (rec.people_name || rec.people)} in ${cap.place || 'cell ' + cap.cell} (cell ${cap.cell}, lat ${cap.lat}, lon ${cap.lon})`, { ess });
  if (rec.tiers.length > 1) R('place', 'tiers', rec.tiers.map(([a, t]) => `${t} ${ago(a)}`).join(', '), { ess: false });
}
