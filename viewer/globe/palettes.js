// Peoples' colours (PW-1032): family hues + distinct neighbours. Dragons in reds (a dragon named by a colour or metal
// in that colour), giants in blues, fey in violets, every other branch its own hue; siblings told apart by lightness;
// then neighbours that still look alike (to normal or red-green colour-blind sight) are pushed apart.
// The palette rewrites run.meta.lineages[].color once, when the run opens, so the map, the legend, the summary and the
// rings all follow. planetViewer.paletteReport() measures the colours on screen.
import { S } from './state.js';

// ------------------------------------------------------------ colour maths (sRGB <-> CIELAB, D65; colour-blind sight)
const lin = (u) => (u <= 0.04045 ? u / 12.92 : ((u + 0.055) / 1.055) ** 2.4);
const gam = (u) => (u <= 0.0031308 ? 12.92 * u : 1.055 * u ** (1 / 2.4) - 0.055);
const hexRgb = (h) => [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16) / 255);
const rgbHex = (c) => '#' + c.map((u) => Math.round(Math.max(0, Math.min(1, u)) * 255).toString(16).padStart(2, '0')).join('');
const F = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116);
const Fi = (t) => (t ** 3 > 216 / 24389 ? t ** 3 : (116 * t - 16) / (24389 / 27));
function linLab([r, g, b]) {
  const x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, y = 0.2126 * r + 0.7152 * g + 0.0722 * b, z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883;
  return [116 * F(y) - 16, 500 * (F(x) - F(y)), 200 * (F(y) - F(z))];
}
const LAB = new Map(), SEEN = new Map();
export const lab = (hex) => LAB.get(hex) || (LAB.set(hex, linLab(hexRgb(hex).map(lin))), LAB.get(hex));
function labHex([L, a, b], strict = false) {
  const fy = (L + 16) / 116, x = 0.95047 * Fi(fy + a / 500), y = Fi(fy), z = 1.08883 * Fi(fy - b / 200);
  const rgb = [3.2406 * x - 1.5372 * y - 0.4986 * z, -0.9689 * x + 1.8758 * y + 0.0415 * z, 0.0557 * x - 0.204 * y + 1.057 * z];
  if (strict && rgb.some((u) => u < -0.002 || u > 1.002)) return null;  // (out of the screen's gamut)
  return rgbHex(rgb.map((u) => gam(Math.max(0, Math.min(1, u)))));
}
const lch = (L, C, h) => [L, C * Math.cos(h * Math.PI / 180), C * Math.sin(h * Math.PI / 180)];
const dE = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
// red-green colour blindness (Machado et al. 2009, severity 1), on linear RGB
const CVD = {
  protan: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  deutan: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]],
};
const seen = (hex, m) => {
  const k = hex + (m === CVD.protan ? 'p' : 'd');
  if (!SEEN.has(k)) { const c = hexRgb(hex).map(lin); SEEN.set(k, linLab(m.map((r) => Math.max(0, Math.min(1, r[0] * c[0] + r[1] * c[1] + r[2] * c[2]))))); }
  return SEEN.get(k);
};
// how far apart two colours look to the worst of normal, protan and deutan sight
const dEsight = (h1, h2) => Math.min(dE(lab(h1), lab(h2)), dE(seen(h1, CVD.protan), seen(h2, CVD.protan)), dE(seen(h1, CVD.deutan), seen(h2, CVD.deutan)));
const GROUND = { ocean: '#1c2f4f', nobody: '#5a5a52' };  // (colours.js OCEAN and NOBODY: a people must not sink into them)

// ------------------------------------------------------------ who touches whom
// Pairs of peoples (indexes) whose leading cells border each other, or who share cells (the cell's second people),
// counted over the present and every 6th stored moment; weight = cell edges.
function contacts(V) {
  const n = V.n, nbr = V.grid.nbr, P = V.data.peoples, M = V.data.mix_second, W = new Map();
  if (!P) return W;
  const nf = P.length / n, add = (a, b) => { const k = a < b ? a * 256 + b : b * 256 + a; W.set(k, (W.get(k) || 0) + 1); };
  const frames = [...new Set([nf - 1, ...Array.from({ length: Math.ceil(nf / 6) }, (_, k) => k * 6)])].filter((f) => f < nf);
  for (const f of frames) {
    const o = f * n;
    for (let i = 0; i < n; i++) {
      const a = P[o + i];
      if (a === 255) continue;
      for (const j of nbr[i]) if (j > i) { const b = P[o + j]; if (b !== 255 && b !== a) add(a, b); }
      if (M) { const s = M[o + i]; if (s !== 255 && s !== a) add(a, s); }
    }
  }
  return W;
}
function neighbourSets(lines, W, min = 4) {
  const nb = lines.map(() => new Set());
  for (const [k, w] of W) if (w >= min) { const a = k >> 8, b = k & 255; if (nb[a] && nb[b]) { nb[a].add(b); nb[b].add(a); } }
  return nb;
}

// a group (a way of life inside a people) is its people's colour, lighter or darker by its place among the groups
function groupColours(lines, col) {
  for (const l of lines) {
    if (!l.groups?.length || !col[l.index]) continue;
    // (the people and its groups on evenly spaced lightness steps around the people's own, inside 46..90, the groups
    // also turned a little in hue, so neighbouring groups stay apart)
    const base = lab(col[l.index]), gs = l.groups.map((g) => lines.find((x) => x.id === g)).filter(Boolean);
    const n = gs.length, W = Math.min(44, 12 * n), lo = Math.max(46, Math.min(90 - W, base[0] - W / 2));
    const slots = Array.from({ length: n + 1 }, (_, k) => lo + (W * k) / n);
    slots.splice(slots.reduce((b, v, k) => (Math.abs(v - base[0]) < Math.abs(slots[b] - base[0]) ? k : b), 0), 1);
    const C = Math.max(30, Math.hypot(base[1], base[2])), h = Math.atan2(base[2], base[1]) * 180 / Math.PI;
    gs.forEach((g, k) => { col[g.index] = labHex(lch(slots[k], C, h + (k % 2 ? 10 : -10))); });
  }
}

// ------------------------------------------------------------ family hues
const NAMED = {  // a colour or metal in a people's name ("red dragons", "gold dragons")
  red: '#d42a1e', blue: '#3f7fe0', green: '#2f9e44', black: '#40202c', white: '#eeeee6',
  gold: '#e8b923', silver: '#c3ccd6', bronze: '#a87632', copper: '#c8643a', brass: '#d9bf6a',
};
const FAMILY_HUE = { dragon: 28, giant: 255, fey: 305 };  // CIELAB hue angles: reds, blues, violets
const OTHER_HUES = [85, 140, 60, 180, 110, 210, 345, 160, 40, 230];
function familyOf(l, byId) {
  for (let x = l; x; x = byId[x.parents?.[0]]) {
    const nm = x.name.toLowerCase();
    if (/dragon|draconic|kobold/.test(nm)) return 'dragon';
    if (/giant|goliath|firbolg/.test(nm)) return 'giant';
    if (/feywild|\bfey\b|\belf\b|elves|drow|gnome/.test(nm)) return 'fey';
  }
  let x = l;  // otherwise the branch just under the root (or the arrival itself)
  while (x.parents?.length && byId[x.parents[0]]?.parents?.length) x = byId[x.parents[0]];
  return 'b:' + x.id;
}
function familyColours(lines, nb, order) {
  const byId = Object.fromEntries(lines.map((l) => [l.id, l])), col = {};
  const base = lines.filter((l) => !l.group_of);
  const fams = new Map();
  for (const l of base) { const f = familyOf(l, byId); if (!fams.has(f)) fams.set(f, []); fams.get(f).push(l); }
  let other = 0;
  for (const [f, ls] of fams) {
    const hue = FAMILY_HUE[f] ?? OTHER_HUES[other++ % OTHER_HUES.length];
    // siblings by lightness (and a little hue), in tree order; named colours win
    const free = ls.filter((l) => !Object.keys(NAMED).some((w) => new RegExp(`^${w}\\b`).test(l.name.toLowerCase())));
    for (const l of ls) { const w = Object.keys(NAMED).find((k) => new RegExp(`^${k}\\b`).test(l.name.toLowerCase())); if (w) col[l.index] = NAMED[w]; }
    free.forEach((l, k) => {
      const t = free.length > 1 ? k / (free.length - 1) : 0.5;
      const L = 50 + 38 * ((k * 0.618) % 1), h = hue + (t - 0.5) * 34, C = f === 'fey' || f === 'giant' ? 50 : 58;
      col[l.index] = labHex(lch(L, C, h));
    });
  }
  return col;
}
// Neighbours that still look alike (to any sight), or a colour lost in the ocean or the grey of "nobody": the later
// one moves to the nearest shade of its own hue band (within hue ± span) that is farthest from its neighbours.
const sinks = (c) => dEsight(c, GROUND.ocean) < 20 || dEsight(c, GROUND.nobody) < 14;
function separate(order, nb, col, span) {
  for (let pass = 0; pass < 3; pass++) for (const u of order) {
    if (!col[u]) continue;
    if (!sinks(col[u]) && ![...nb[u]].some((v) => col[v] && dEsight(col[u], col[v]) < 14)) continue;
    const h0 = Math.atan2(lab(col[u])[2], lab(col[u])[1]) * 180 / Math.PI;
    let best = col[u], bs = -1;
    for (const L of [46, 52, 58, 64, 70, 76, 82, 88]) for (const dh of [-span, -span / 2, 0, span / 2, span]) for (const C of [40, 55, 70]) {
      const c = labHex(lch(L, C, h0 + dh), true);
      if (!c || sinks(c)) continue;
      let near = 99;
      for (const v of nb[u]) if (col[v]) near = Math.min(near, dEsight(c, col[v]));
      if (near > bs) { bs = near; best = c; }
    }
    col[u] = best;
  }
}

// ------------------------------------------------------------ apply, and measure
export function applyPalette(V) {
  const lines = V.run.meta.lineages;
  if (!lines?.length || V.run.kind !== 'peoples') return;
  const nb = neighbourSets(lines, contacts(V));
  const order = lines.map((l) => l.index).sort((a, b) => nb[b].size - nb[a].size);
  const col = familyColours(lines, nb, order);
  groupColours(lines, col);
  separate(order, nb, col, 18);
  for (const l of lines) if (col[l.index]) { l.color = col[l.index]; delete l._c; }
  V.paletteNb = nb;
}

// the numbers for a palette on screen: neighbour pairs, how many look alike (normal / colour-blind sight), the closest
// pair, and colours that sink into the ocean or the grey of "nobody"
export function paletteReport(V = S.V) {
  const lines = V.run.meta.lineages, nb = V.paletteNb || neighbourSets(lines, contacts(V));
  const pairs = [];
  for (const l of lines) for (const v of nb[l.index]) if (v > l.index) pairs.push([l.index, v]);
  const nd = (a, b) => dE(lab(lines[a].color.slice(0, 7)), lab(lines[b].color.slice(0, 7)));
  const ns = (a, b) => dEsight(lines[a].color.slice(0, 7), lines[b].color.slice(0, 7));
  const same = pairs.filter(([a, b]) => lines[a].color === lines[b].color);
  const close = pairs.filter(([a, b]) => nd(a, b) < 12), closeCvd = pairs.filter(([a, b]) => ns(a, b) < 12);
  const worst = pairs.map(([a, b]) => [ns(a, b), lines[a].name, lines[b].name]).sort((x, y) => x[0] - y[0]).slice(0, 5);
  const sink = lines.filter((l) => dEsight(l.color.slice(0, 7), GROUND.ocean) < 18 || dEsight(l.color.slice(0, 7), GROUND.nobody) < 12).map((l) => l.name);
  return { lines: lines.length, colours: new Set(lines.map((l) => l.color)).size, neighbourPairs: pairs.length, sameColourNeighbours: same.length,
           lookAlikeNeighbours: close.length, lookAlikeNeighboursColourBlind: closeCvd.length,
           closestNeighbours: worst.map(([d, a, b]) => `${a.replace(/ \(.*/, '')} / ${b.replace(/ \(.*/, '')}: ${d.toFixed(1)}`), sinkIntoOceanOrGrey: sink };
}
