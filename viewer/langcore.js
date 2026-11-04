'use strict';
// The languages viewer's pure helpers (no DOM): languages.html draws with them, tests/test_languages_viewer.py runs them
// under node. The data: a run's languages.json (planet/language/output.py). Exposed as globalThis.LangCore (and
// module.exports under node).
//   index(doc)               lookups built once per file: lects by id, children, frames, intelligibility by pair, etymology walk
//   snapFull(snaps)          undo the snapshot delta encoding (history.snapshot_full)
//   stitch(ix, id)           a lect's history at every frame through its ancestors: [{i, kyr, lect, snap}]
//   layoutTree(ix, opts)     the true lect tree as rows on a time axis (parent links, bud / shift / arrival)
//   layoutDendro(roots)      the scholars' UPGMA tree ({distance, children} | {lect}) as a dendrogram
//   intelColor(v)            green > 0.7, amber 0.4-0.7, red < 0.4, grey when not measured
//   chainAt(ix, chain, i)    a continuum's adjacent and end-to-end values at frame i; chainBreak(ix, chain) when it broke
//   findContinua(...)        the same search as families.continua, at any frame
//   ipaPlace(seg)            where a segment sits on the consonant grid (place x manner) or the vowel trapezoid
//   etymChain(ix, node)      a word's etymology, oldest first; processText(step) its process in plain words
(function (g) {
  // ------------------------------------------------------------------ index
  const pairKey = (a, b) => (a < b ? a + '|' + b : b + '|' + a);

  function index(doc) {
    const lects = doc.lects || [];
    const by = new Map(), kids = new Map();
    for (const l of lects) by.set(l.id, l);
    for (const l of lects) {
      if (l.parent != null && by.has(l.parent)) {
        if (!kids.has(l.parent)) kids.set(l.parent, []);
        kids.get(l.parent).push(l.id);
      }
    }
    for (const v of kids.values()) v.sort((a, b) => (by.get(b).born_kyr - by.get(a).born_kyr) || cmpId(a, b));
    const frames = doc.frames_kyr || (doc.intelligibility && doc.intelligibility.frames) || [];
    const intel = new Map();
    for (const [a, b, vals] of ((doc.intelligibility && doc.intelligibility.pairs) || [])) intel.set(pairKey(a, b), vals);
    const now = new Map();
    for (const [a, b, v] of ((doc.intelligibility && doc.intelligibility.now) || [])) now.set(pairKey(a, b), v);
    const langOf = new Map();
    for (const L of ((doc.families && doc.families.languages) || [])) for (const x of L.lects) langOf.set(x, L.id);
    const snapCache = new Map();
    return {
      doc, by, kids, frames, intel, now, langOf, snapCache,
      living: lects.filter((l) => l.died_kyr == null && l.deme != null).map((l) => l.id),
      intelAt(a, b, i) {
        if (a === b) return 1;
        const v = intel.get(pairKey(a, b));
        if (v) return v[i] == null ? null : v[i];
        if (i === frames.length - 1) { const x = now.get(pairKey(a, b)); return x == null ? null : x; }
        return null;
      },
      snaps(id) {  // a lect's snapshots, full dicts, cached
        if (!snapCache.has(id)) { const l = by.get(id); snapCache.set(id, snapFull((l && l.snapshots) || [])); }
        return snapCache.get(id);
      },
      frameOf(kyr) { return nearestFrame(frames, kyr); },
    };
  }
  function cmpId(a, b) {  // d12 < d12.1 < d13 < d100 (numeric parts)
    const pa = String(a).match(/\d+|\D+/g) || [], pb = String(b).match(/\d+|\D+/g) || [];
    for (let k = 0; k < Math.min(pa.length, pb.length); k++) {
      const x = pa[k], y = pb[k];
      if (x === y) continue;
      const nx = /^\d/.test(x), ny = /^\d/.test(y);
      if (nx && ny) return +x - +y;
      return x < y ? -1 : 1;
    }
    return pa.length - pb.length;
  }
  function nearestFrame(frames, kyr) {
    let best = 0, d = Infinity;
    for (let i = 0; i < frames.length; i++) { const e = Math.abs(frames[i] - kyr); if (e < d) { d = e; best = i; } }
    return best;
  }
  const alive = (l, kyr) => l.born_kyr >= kyr - 1e-9 && (l.died_kyr == null || l.died_kyr < kyr - 1e-9);

  // ------------------------------------------------------------------ snapshots
  function snapFull(snaps) {
    const out = [];
    let cur = null;
    for (const [kyr, sn] of snaps) {
      if (!sn.d || !cur) {
        cur = {};
        for (const k in sn) if (k !== 'd') cur[k] = Array.isArray(sn[k]) ? sn[k].slice() : sn[k];
        if (sn.d && !Array.isArray(cur.core)) cur.core = [];  // (a delta with nothing before it: should not happen)
      } else {
        const nx = Object.assign({}, cur);
        nx.core = cur.core.slice();
        for (const j in sn.core || {}) nx.core[+j] = sn.core[j];
        for (const k in sn) if (k !== 'd' && k !== 'core') nx[k] = sn[k];
        cur = nx;
      }
      out.push([kyr, cur]);
    }
    return out;
  }
  // a lect's line of descent, oldest first (the lect last)
  function ancestry(ix, id) {
    const out = [];
    let l = ix.by.get(id);
    const seen = new Set();
    while (l && !seen.has(l.id)) { seen.add(l.id); out.push(l); l = l.parent != null ? ix.by.get(l.parent) : null; }
    return out.reverse();
  }
  // per frame: the lect on the line of descent alive then (the youngest at a split) and its snapshot at or just before it
  function stitch(ix, id) {
    const line = ancestry(ix, id);
    const out = [];
    for (let i = 0; i < ix.frames.length; i++) {
      const kyr = ix.frames[i];
      let who = null;
      for (let k = line.length - 1; k >= 0; k--) {
        const l = line[k];
        if (l.born_kyr >= kyr - 1e-9 && (k === line.length - 1 || line[k + 1].born_kyr < kyr - 1e-9)) { who = l; break; }
      }
      let snap = null, at = null;
      for (let k = who ? line.indexOf(who) : -1; k >= 0 && !snap; k--) {  // (a proto keeps no snapshots: fall back to the oldest record)
        const S = ix.snaps(line[k].id);
        for (const [sk, s] of S) if (sk >= kyr - 1e-9) { snap = s; at = sk; } else break;
        if (snap) { who = line[k]; }
      }
      if (!snap && who) {  // (before the first snapshot of the line: its earliest one)
        for (const l of line) { const S = ix.snaps(l.id); if (S.length) { snap = S[0][1]; at = S[0][0]; who = l; break; } }
      }
      out.push({ i, kyr, lect: who ? who.id : null, snap, at, exists: !!who && alive(who, kyr) });
    }
    return out;
  }
  // the sound changes along a lect's line of descent, each from the lect that held the line then, newest first
  function changeLog(ix, id) {
    const line = ancestry(ix, id);
    const out = [];
    for (let k = 0; k < line.length; k++) {
      const l = line[k], until = k + 1 < line.length ? line[k + 1].born_kyr : -1;
      for (const c of l.changes || []) if (c[0] > until + 1e-9) out.push({ kyr: c[0], rule: c[1], cause: c[2], origin: c[3], extra: c[4] || null, lect: l.id });
    }
    out.sort((a, b) => a.kyr - b.kyr);
    return out;
  }

  // ------------------------------------------------------------------ the true tree (rows on a time axis)
  // opts: {collapsed: Set, keep: (lect) => bool (a lect not kept is left out with its subtree unless a descendant is kept)}
  function layoutTree(ix, opts) {
    opts = opts || {};
    const collapsed = opts.collapsed || new Set(), keep = opts.keep || null;
    const lects = ix.doc.lects || [];
    const roots = lects.filter((l) => l.parent == null || !ix.by.has(l.parent));
    roots.sort((a, b) => (String(a.people) < String(b.people) ? -1 : a.people > b.people ? 1 : 0) || (b.born_kyr - a.born_kyr) || cmpId(a.id, b.id));
    const wanted = new Map();  // id -> has a kept lect in its subtree
    const want = (id) => {
      if (wanted.has(id)) return wanted.get(id);
      wanted.set(id, false);
      const l = ix.by.get(id);
      let w = !keep || keep(l);
      for (const c of ix.kids.get(id) || []) if (want(c)) w = true;
      wanted.set(id, w);
      return w;
    };
    const rows = [], rowOf = new Map();
    const stack = [];
    for (let r = roots.length - 1; r >= 0; r--) stack.push([roots[r].id, 0, null]);
    while (stack.length) {
      const [id, depth, par] = stack.pop();
      if (!want(id)) continue;
      const l = ix.by.get(id);
      const kids = (ix.kids.get(id) || []).filter(want);
      const row = { id, y: rows.length, depth, parent: par, how: l.how, people: l.people, x0: l.born_kyr, x1: l.died_kyr == null ? 0 : l.died_kyr,
        dead: l.died_kyr != null, kids: kids.length, collapsed: collapsed.has(id) && kids.length > 0, desc: 0 };
      rowOf.set(id, row);
      rows.push(row);
      if (!row.collapsed) for (let k = kids.length - 1; k >= 0; k--) stack.push([kids[k], depth + 1, id]);
    }
    if (collapsed.size) for (const r of rows) if (r.collapsed) r.desc = countDesc(ix, r.id, want);
    const links = [];
    for (const r of rows) if (r.parent != null && rowOf.has(r.parent)) links.push({ from: r.parent, to: r.id, x: r.x0, y0: rowOf.get(r.parent).y, y1: r.y, how: r.how });
    return { rows, rowOf, links };
  }
  function countDesc(ix, id, want) {
    let n = 0;
    const st = [...(ix.kids.get(id) || [])];
    while (st.length) { const c = st.pop(); if (want && !want(c)) continue; n++; st.push(...(ix.kids.get(c) || [])); }
    return n;
  }

  // ------------------------------------------------------------------ the scholars' tree (dendrogram)
  // roots: [{distance, children} | {lect}]; returns {leaves: [lect ids in order], nodes: [{x (distance), y, leaf?, kids: [node idx]}], roots: [idx]}
  // keep(lect id): leaves not kept are left out, and a node left with one child is replaced by it
  function layoutDendro(roots, keep) {
    const nodes = [], leaves = [], rootIdx = [];
    const rec = (n) => {  // (recursive: UPGMA over <= ~2k lects is a few thousand deep at worst)
      if (n.lect != null) {
        if (keep && !keep(n.lect)) return -1;
        const k = nodes.length;
        nodes.push({ x: 0, y: leaves.length, leaf: n.lect, kids: [] });
        leaves.push(n.lect);
        return k;
      }
      const kids = (n.children || []).map(rec).filter((c) => c >= 0);
      if (!kids.length) return -1;
      if (kids.length === 1) return kids[0];
      const k = nodes.length;
      const ys = kids.map((c) => nodes[c].y);
      nodes.push({ x: n.distance != null ? n.distance : (n.split_kyr || 0), y: ys.length ? (Math.min(...ys) + Math.max(...ys)) / 2 : 0, leaf: null, kids });
      return k;
    };
    for (const r of roots || []) { const k = rec(r); if (k >= 0) rootIdx.push(k); }
    return { leaves, nodes, roots: rootIdx };
  }

  // ------------------------------------------------------------------ intelligibility
  const INTEL_GREEN = 0.7, INTEL_RED = 0.4;
  function intelClass(v) { return v == null ? 'none' : v > INTEL_GREEN ? 'high' : v >= INTEL_RED ? 'mid' : 'low'; }
  const INTEL_COL = { high: '#5fd17a', mid: '#f2b544', low: '#ef5b5b', none: '#4a5466' };
  function intelColor(v) { return INTEL_COL[intelClass(v)]; }
  function intelRamp(v) {  // a continuous red -> amber -> green for the heatmap (grey when not measured)
    if (v == null) return '#2a3140';
    const t = Math.max(0, Math.min(1, v));
    const a = [239, 91, 91], b = [242, 181, 68], c = [95, 209, 122];
    const mix = (p, q, s) => p.map((x, k) => Math.round(x + (q[k] - x) * s));
    const m = t < 0.55 ? mix(a, b, t / 0.55) : mix(b, c, (t - 0.55) / 0.45);
    return `rgb(${m[0]},${m[1]},${m[2]})`;
  }
  function chainAt(ix, chain, i) {
    const adj = [];
    for (let k = 0; k + 1 < chain.length; k++) adj.push(ix.intelAt(chain[k], chain[k + 1], i));
    const ends = ix.intelAt(chain[0], chain[chain.length - 1], i);
    const known = adj.filter((v) => v != null);
    const linked = known.length === adj.length && known.every((v) => v > 0.5);
    return { adj, ends, linked, broken: linked && ends != null && ends < 0.5, minAdj: known.length ? Math.min(...known) : null };
  }
  // the frames at which the chain's two ends stopped understanding each other while every link still held: the latest such turn
  function chainBreak(ix, chain) {
    let was = null, at = null;
    const hist = [];
    for (let i = 0; i < ix.frames.length; i++) {
      const c = chainAt(ix, chain, i);
      hist.push(c);
      if (c.ends != null) {
        const lost = c.ends < 0.5;
        if (lost && was === false) at = i;
        was = lost;
      }
    }
    return { history: hist, broke_frame: at, broke_kyr: at == null ? null : ix.frames[at] };
  }
  // families.continua at frame i: per group (familyOf) the contact graph of lects with intelligibility above adjMin; the pair
  // below endsMax joined by the longest shortest path in each piece
  function findContinua(ids, valueOf, inContact, familyOf, adjMin, endsMax) {
    adjMin = adjMin == null ? 0.5 : adjMin; endsMax = endsMax == null ? 0.5 : endsMax;
    const fams = new Map();
    for (const id of ids) { const f = familyOf(id); if (!fams.has(f)) fams.set(f, []); fams.get(f).push(id); }
    const out = [];
    for (const [fam, mem] of [...fams.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1))) {
      if (mem.length < 3) continue;
      mem.sort();
      const adj = new Map(mem.map((x) => [x, []]));
      for (let x = 0; x < mem.length; x++) for (let y = x + 1; y < mem.length; y++) {
        const a = mem[x], b = mem[y], v = valueOf(a, b);
        if (v != null && v > adjMin && inContact(a, b)) { adj.get(a).push(b); adj.get(b).push(a); }
      }
      for (const v of adj.values()) v.sort();
      let best = null;
      for (const src of mem) {
        const prev = new Map([[src, null]]), q = [src];
        for (let h = 0; h < q.length; h++) for (const v of adj.get(q[h])) if (!prev.has(v)) { prev.set(v, q[h]); q.push(v); }
        for (const dst of prev.keys()) {
          const e = valueOf(src, dst);
          if (dst <= src || (e != null && e >= endsMax)) continue;
          const path = [dst];
          while (prev.get(path[path.length - 1]) != null) path.push(prev.get(path[path.length - 1]));
          if (!best || path.length > best.length) best = path.reverse();
        }
      }
      if (best && best.length >= 3) {
        out.push({ family: fam, chain: best, adjacent: best.slice(1).map((b, k) => valueOf(best[k], b)), ends: valueOf(best[0], best[best.length - 1]) });
      }
    }
    return out.sort((a, b) => b.chain.length - a.chain.length);
  }

  // ------------------------------------------------------------------ IPA placement
  const PLACES = ['bilabial', 'labiodental', 'dental', 'alveolar', 'postalveolar', 'retroflex', 'palatal', 'velar', 'uvular', 'pharyngeal', 'glottal'];
  const MANNERS = ['plosive', 'implosive', 'nasal', 'trill', 'tap', 'fricative', 'lateral fricative', 'affricate', 'approximant', 'lateral approximant', 'click'];
  const C = {};
  const put = (chars, place, manner) => { for (const ch of chars) C[ch] = [place, manner]; };
  put('pb', 'bilabial', 'plosive'); put('td', 'alveolar', 'plosive'); put('ʈɖ', 'retroflex', 'plosive'); put('cɟ', 'palatal', 'plosive');
  put('kɡg', 'velar', 'plosive'); put('qɢ', 'uvular', 'plosive'); put('ʡ', 'pharyngeal', 'plosive'); put('ʔ', 'glottal', 'plosive');
  put('ɓ', 'bilabial', 'implosive'); put('ɗ', 'alveolar', 'implosive'); put('ʄ', 'palatal', 'implosive'); put('ɠ', 'velar', 'implosive'); put('ʛ', 'uvular', 'implosive');
  put('m', 'bilabial', 'nasal'); put('ɱ', 'labiodental', 'nasal'); put('n', 'alveolar', 'nasal'); put('ɳ', 'retroflex', 'nasal');
  put('ɲȵ', 'palatal', 'nasal'); put('ȶȡ', 'palatal', 'plosive'); put('ȴ', 'palatal', 'lateral approximant'); put('ᶑ', 'retroflex', 'implosive'); put('ŋ', 'velar', 'nasal'); put('ɴ', 'uvular', 'nasal');
  put('ʙ', 'bilabial', 'trill'); put('r', 'alveolar', 'trill'); put('ʀ', 'uvular', 'trill');
  put('ⱱ', 'labiodental', 'tap'); put('ɾɺ', 'alveolar', 'tap'); put('ɽ', 'retroflex', 'tap');
  put('ɸβ', 'bilabial', 'fricative'); put('fv', 'labiodental', 'fricative'); put('θð', 'dental', 'fricative'); put('sz', 'alveolar', 'fricative');
  put('ʃʒ', 'postalveolar', 'fricative'); put('ʂʐ', 'retroflex', 'fricative'); put('ɕʑçʝ', 'palatal', 'fricative'); put('xɣɧ', 'velar', 'fricative');
  put('χʁ', 'uvular', 'fricative'); put('ħʕʜʢ', 'pharyngeal', 'fricative'); put('hɦ', 'glottal', 'fricative');
  put('ɬɮ', 'alveolar', 'lateral fricative');
  put('wʍ', 'bilabial', 'approximant'); put('ʋ', 'labiodental', 'approximant'); put('ɹ', 'alveolar', 'approximant'); put('ɻ', 'retroflex', 'approximant');
  put('jɥ', 'palatal', 'approximant'); put('ɰ', 'velar', 'approximant');
  put('lɫ', 'alveolar', 'lateral approximant'); put('ɭ', 'retroflex', 'lateral approximant'); put('ʎ', 'palatal', 'lateral approximant'); put('ʟ', 'velar', 'lateral approximant');
  put('ʘ', 'bilabial', 'click'); put('ǀ', 'dental', 'click'); put('ǃ', 'postalveolar', 'click'); put('ǂ', 'palatal', 'click'); put('ǁ', 'alveolar', 'click');
  const VOICED = new Set('ȡᶑȵȴɫbdɖɟɡgɢɓɗʄɠʛmɱnɳɲȵŋɴʙrʀⱱɾɺɽβvðzʒʐʑʝɣʁʕʢɦɮwʋɹɻjɥɰlɭʎʟ');
  // vowels: [height 0 close .. 6 open, backness 0 front, 1 central, 2 back, rounded]
  const V = {
    i: [0, 0, 0], y: [0, 0, 1], ɨ: [0, 1, 0], ʉ: [0, 1, 1], ɯ: [0, 2, 0], u: [0, 2, 1],
    ɪ: [1, 0.3, 0], ʏ: [1, 0.3, 1], ʊ: [1, 1.7, 1],
    e: [2, 0, 0], ø: [2, 0, 1], ɘ: [2, 1, 0], ɵ: [2, 1, 1], ɤ: [2, 2, 0], o: [2, 2, 1],
    ə: [3, 1, 0],
    ɛ: [4, 0, 0], œ: [4, 0, 1], ɜ: [4, 1, 0], ɞ: [4, 1, 1], ʌ: [4, 2, 0], ɔ: [4, 2, 1],
    æ: [5, 0, 0], ɐ: [5, 1, 0],
    a: [6, 0, 0], ɶ: [6, 0, 1], ä: [6, 1, 0], ɑ: [6, 2, 0], ɒ: [6, 2, 1],
  };
  const HEIGHTS = ['close', 'near-close', 'close-mid', 'mid', 'open-mid', 'near-open', 'open'];
  const MODS = /[̀-ͯ᷀-᷿⃐-⃿ʰʷʲʼʱˠˤⁿᵐᵑᶮᶯᶰᵊˀːˑ˞˥˦˧˨˩ˈˌ.‿͡]/g;
  function ipaPlace(seg) {
    const s = String(seg || '');
    const nfc = s.normalize ? s.normalize('NFD') : s;
    const dental = /̪/.test(nfc), lowered = /̞/.test(nfc), raised = /̝/.test(nfc);
    const feat = /\{[^}]*\}/.test(nfc);  // (a percept with no IPA symbol is written with its features in braces: kʰ{voice=0})
    const chars = [...nfc.replace(/\{[^}]*\}/g, '').replace(MODS, '')];
    const base = chars.filter((ch) => C[ch] || V[ch]).join('');
    const special = feat || base.length !== chars.length;  // (non-human percepts and house symbols, ‼ ᴖ and the like, ride on a placed sound)
    if (base.length === 1 && V[base]) {
      const [h, b, r] = V[base];
      return { kind: 'V', base, height: Math.max(0, Math.min(6, h + (lowered ? 1 : 0) - (raised ? 1 : 0))), back: b, round: !!r, special };
    }
    if (base.length === 1 && C[base]) {
      let [place, manner] = C[base];
      if (dental && (place === 'alveolar')) place = 'dental';
      return { kind: 'C', base, place, manner, voiced: VOICED.has(base), special };
    }
    if (base.length === 2 && C[base[0]] && C[base[1]]) {
      const [p0, m0] = C[base[0]], [p1, m1] = C[base[1]];
      if (m0 === 'plosive' && (m1 === 'fricative' || m1 === 'lateral fricative')) return { kind: 'C', base, place: p1 === 'labiodental' ? 'labiodental' : p1, manner: 'affricate', voiced: VOICED.has(base[0]), special };
      if (m0 === 'nasal' && m1 === 'plosive') return { kind: 'C', base, place: p1, manner: 'plosive', voiced: true, prenasal: true, special };
      return { kind: 'C', base, place: p1, manner: m1, voiced: VOICED.has(base[1]), double: true, special };  // (k͡p and the like: the second place)
    }
    if (base.length === 2 && V[base[0]] && V[base[1]]) {  // (a diphthong as one segment: its start)
      const [h, b, r] = V[base[0]];
      return { kind: 'V', base, height: h, back: b, round: !!r, special, diphthong: true };
    }
    return { kind: 'X', base, special: true };
  }
  // the trapezoid: x in [0, 1] (front .. back) for a height, the front edge slanting in towards the open vowels
  function vowelXY(p) {
    const y = p.height / 6;
    const front = 0.36 * y, back = 1;
    const x = front + (back - front) * (p.back / 2);
    return { x: x + (p.round ? 0.035 : -0.035), y };
  }

  // ------------------------------------------------------------------ etymologies
  // node = [parent | -1, kyr, lect, process, ipa, gloss (0: the parent's)(, note)]; a chain is [{kyr, lect, process, ipa, gloss, note}]
  function etymChain(ix, node) {
    const N = ix.doc.etym_nodes || [];
    if (Array.isArray(node)) return node.map(stepObj);  // (a chain stored inline, oldest first)
    const out = [];
    let n = node, guard = 0;
    while (n != null && n >= 0 && n < N.length && guard++ < 10000) { out.push(N[n]); n = N[n][0]; }
    out.reverse();
    const steps = out.map((r) => ({ kyr: r[1], lect: r[2], process: r[3], ipa: r[4], gloss: r[5], note: r[6] || null }));
    for (let k = 1; k < steps.length; k++) if (steps[k].gloss === 0) steps[k].gloss = steps[k - 1].gloss;
    return steps;
  }
  const stepObj = (s) => (Array.isArray(s) ? { kyr: s[0], lect: s[1], process: s[2], ipa: s[3], gloss: s[4], note: s[5] || null } : s);
  function processText(p) {
    const s = String(p || ''), [k, rest] = s.includes(':') ? [s.slice(0, s.indexOf(':')), s.slice(s.indexOf(':') + 1)] : [s, ''];
    switch (k) {
      case 'proto': return 'in the proto-language';
      case 'sound_change': { const n = rest.split('+'); const more = n.length && /^…/.test(n[n.length - 1]) ? +(n.pop().slice(1) || 1) : 0; return `sound change${n.length + more > 1 ? 's' : ''} ${n.join(', ')}${more ? ` and ${more} more` : ''}`; }
      case 'derive': return `made from the word before with the affix '${rest}'`;
      case 'compound': return `compound of ${rest.split('+').join(' + ')}`;
      case 'shift': return `its meaning moved from ${rest || 'another sense'}`;
      case 'borrow': return `borrowed from ${rest}`;
      case 'substrate': return `kept from the language spoken here before${rest ? ' (' + rest + ')' : ''}`;
      case 'taboo': return `replaced under a taboo${rest ? ' (' + rest + ')' : ''}`;
      case 'elaborate': return `lengthened to keep it apart from a lookalike${rest ? ' (' + rest + ')' : ''}`;
      case 'coin': return 'coined';
      case 'name': return `made into a name${rest ? ' (pattern ' + rest + ')' : ''}`;
      case 'accent': return `heard through the accent of ${rest}`;
      default: return s;
    }
  }
  const CAUSES = {
    effort: 'easier to say', coarticulation: 'neighbouring sounds rubbed off on it', prosody: 'stress and rhythm',
    perception: 'misheard by listeners', dispersion: 'sounds moved apart to stay distinct', tonogenesis: 'pitch took over a lost contrast',
    substrate: 'the accent of speakers who switched to this language', contact: 'spread from neighbours', koine: 'levelled in a mixed city speech',
  };
  const causeText = (c) => CAUSES[c] || String(c || '');

  // ------------------------------------------------------------------ small things
  function hue(s) {  // a stable colour for a language or family id
    let h = 0;
    for (const ch of String(s)) h = (h * 31 + ch.codePointAt(0)) >>> 0;
    const x = (h * 137.508) % 360;
    return `hsl(${x.toFixed(0)}, 62%, ${55 + (h % 3) * 6}%)`;
  }
  // a line between two longitudes the short way: one segment, or two (each running off one edge of the map) across the date line
  function wrapLon(a, b) {
    if (Math.abs(b - a) <= 180) return [[a, b]];
    const b2 = b + (b < a ? 360 : -360);
    return [[a, b2], [a - (b2 - b), b]];
  }
  const API = { pairKey, index, cmpId, nearestFrame, alive, snapFull, ancestry, stitch, changeLog, layoutTree, layoutDendro,
    intelClass, intelColor, intelRamp, INTEL_GREEN, INTEL_RED, chainAt, chainBreak, findContinua,
    PLACES, MANNERS, HEIGHTS, ipaPlace, vowelXY, etymChain, processText, causeText, hue, wrapLon };
  g.LangCore = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);
