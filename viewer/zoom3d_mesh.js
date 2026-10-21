// How the zoom's 3D terrain splits its grid into triangles (zoom3d.js), kept
// free of three.js so node can test it (tests/test_viewer.py).
//
// Each quad of four pixel centres a b / d e is split along one diagonal. Where
// a river runs diagonally across a quad (a D8 link a-e or b-d), the split is
// along the river: split the other way, the two valley sides meet over the
// river's diagonal and the water's line rises over the ridge they make. Below
// a fall in a narrow valley (a 180 m drop on the diagonal between walls 500 m
// above it) the old rule (the diagonal with the smaller height difference)
// took the walls' diagonal and drew a step hundreds of metres up across the
// river, the "jut" just downstream of many falls (PW-375). Elsewhere the old
// rule stays: the diagonal along which the ground changes least.

// split[k] for quad k = r * (nx - 1) + c (top-left pixel r, c): 1 along a-e, 0 along b-d.
// h: heights (nx * ny); rec: each pixel's downstream neighbour (-1: none); q: discharge (the bigger river wins).
export function quadSplits(h, rec, q, nx, ny) {
  const split = new Uint8Array((nx - 1) * (ny - 1));
  const linked = (i, j) => rec[i] === j || rec[j] === i;
  for (let r = 0; r < ny - 1; r++) for (let c = 0; c < nx - 1; c++) {
    const a = r * nx + c, b = a + 1, d = a + nx, e = d + 1, k = r * (nx - 1) + c;
    const ae = linked(a, e), bd = linked(b, d);
    if (ae && bd) split[k] = Math.max(q[a], q[e]) >= Math.max(q[b], q[d]) ? 1 : 0;
    else if (ae || bd) split[k] = ae ? 1 : 0;
    else split[k] = Math.abs(h[a] - h[e]) <= Math.abs(h[b] - h[d]) ? 1 : 0;
  }
  return split;
}

// height at fractional pixel (r, c) on the triangles `split` draws (the full-detail mesh)
export function meshHeight(h, split, nx, ny, r, c) {
  const r0 = Math.min(Math.max(Math.floor(r), 0), ny - 2), c0 = Math.min(Math.max(Math.floor(c), 0), nx - 2);
  const fr = Math.min(Math.max(r - r0, 0), 1), fc = Math.min(Math.max(c - c0, 0), 1), a = r0 * nx + c0;
  const A = h[a], B = h[a + 1], D = h[a + nx], E = h[a + nx + 1];
  if (split[r0 * (nx - 1) + c0]) return fr >= fc ? A + (D - A) * fr + (E - D) * fc : A + (B - A) * fc + (E - B) * fr;
  return fr + fc <= 1 ? A + (B - A) * fc + (D - A) * fr : E + (D - E) * (1 - fc) + (B - E) * (1 - fr);
}

// The terrain mesh at `step` (1 full detail, 2 half, 4 quarter; zoom3d.js's
// Tile.terrain). Coarse blocks of step x step pixels are two triangles with
// corners on every step-th pixel, split along the diagonal the ground changes
// least. But a river in a valley narrower than a block lies between the
// corners, where the block is the walls' interpolation, and the painted river
// rode up and down it (PW-376). So blocks whose pixels (edges included) hold a
// drawn river (keep: a mask) are kept at full detail, split as the full mesh
// (split, quadSplits), and a coarse block next to one is a fan round its centre
// pixel through every pixel of the sides it shares with them, so the two meet
// without cracks. Returns {vert: the pixel index of each vertex, idx: the
// triangles (vertex indices; counter-clockwise seen from above, as three.js
// wants with z south), ring: the boundary's vertices in order (the skirt),
// blocks} where blocks lets meshAt find a point's triangle.
export function coarseMesh(h, split, keep, nx, ny, step) {
  // block corners: every step-th pixel and the last (a last block at least 2 wide, so it has a centre)
  const ix = (m) => {
    const a = [];
    for (let k = 0; k < m - 1; k += step) a.push(k);
    if (a.length > 1 && m - 1 - a[a.length - 1] < 2) a.pop();
    a.push(m - 1);
    return a;
  };
  const cs = ix(nx), rs = ix(ny), W = cs.length - 1, H = rs.length - 1;
  // keep's pixels per block, by a summed-area table of the mask
  const S = new Int32Array((nx + 1) * (ny + 1));
  for (let r = 0; r < ny; r++) for (let c = 0; c < nx; c++)
    S[(r + 1) * (nx + 1) + c + 1] = (keep[r * nx + c] ? 1 : 0) + S[r * (nx + 1) + c + 1] + S[(r + 1) * (nx + 1) + c] - S[r * (nx + 1) + c];
  const count = (r0, r1, c0, c1) => S[(r1 + 1) * (nx + 1) + c1 + 1] - S[r0 * (nx + 1) + c1 + 1] - S[(r1 + 1) * (nx + 1) + c0] + S[r0 * (nx + 1) + c0];
  const fine = new Uint8Array(W * H);
  for (let a = 0; a < H; a++) for (let b = 0; b < W; b++)
    fine[a * W + b] = step === 1 || count(rs[a], rs[a + 1], cs[b], cs[b + 1]) > 0 ? 1 : 0;
  const isFine = (a, b) => a >= 0 && b >= 0 && a < H && b < W && fine[a * W + b] === 1;
  const vmap = new Int32Array(nx * ny).fill(-1), vert = [];
  const V = (r, c) => { const i = r * nx + c; if (vmap[i] < 0) { vmap[i] = vert.length; vert.push(i); } return vmap[i]; };
  const idx = [];
  // kind per block: 1 fine, 0 two triangles split a-e, 2 split b-d, 3 a fan (its centre pixel in centre[])
  const kind = new Uint8Array(W * H), centre = new Int32Array(W * H).fill(-1);
  for (let a = 0; a < H; a++) for (let b = 0; b < W; b++) {
    const r0 = rs[a], r1 = rs[a + 1], c0 = cs[b], c1 = cs[b + 1], k = a * W + b;
    if (fine[k]) {
      kind[k] = 1;
      for (let r = r0; r < r1; r++) for (let c = c0; c < c1; c++) {
        if (split[r * (nx - 1) + c]) idx.push(V(r, c), V(r + 1, c), V(r + 1, c + 1), V(r, c), V(r + 1, c + 1), V(r, c + 1));
        else idx.push(V(r, c), V(r + 1, c), V(r, c + 1), V(r, c + 1), V(r + 1, c), V(r + 1, c + 1));
      }
      continue;
    }
    const L = isFine(a, b - 1), R = isFine(a, b + 1), T = isFine(a - 1, b), B = isFine(a + 1, b);
    if (!(L || R || T || B)) {
      const pa = r0 * nx + c0, pb = r0 * nx + c1, pd = r1 * nx + c0, pe = r1 * nx + c1;
      if (Math.abs(h[pa] - h[pe]) <= Math.abs(h[pb] - h[pd])) {
        kind[k] = 0;
        idx.push(V(r0, c0), V(r1, c0), V(r1, c1), V(r0, c0), V(r1, c1), V(r0, c1));
      } else {
        kind[k] = 2;
        idx.push(V(r0, c0), V(r1, c0), V(r0, c1), V(r0, c1), V(r1, c0), V(r1, c1));
      }
      continue;
    }
    // a fan round the centre through the block's corners and the pixels of its sides shared with fine blocks
    kind[k] = 3;
    const ring = fanRing(r0, r1, c0, c1, L, R, T, B);
    const cr = (r0 + r1) >> 1, cc = (c0 + c1) >> 1, C = V(cr, cc);
    centre[k] = cr * nx + cc;
    for (let j = 0; j < ring.length; j++) {
      const p = ring[j], q = ring[(j + 1) % ring.length];
      idx.push(V(p[0], p[1]), V(q[0], q[1]), C);
    }
  }
  // the boundary's vertices (the skirt's top), clockwise from the top-left as the old ring
  const ringV = [];
  const edge = [];
  for (let c = 0; c < nx; c++) edge.push(c);
  for (let r = 1; r < ny; r++) edge.push(r * nx + nx - 1);
  for (let c = nx - 2; c >= 0; c--) edge.push((ny - 1) * nx + c);
  for (let r = ny - 2; r > 0; r--) edge.push(r * nx);
  for (const i of edge) if (vmap[i] >= 0) ringV.push(vmap[i]);
  ringV.push(ringV[0]);
  return { vert: Int32Array.from(vert), idx: Uint32Array.from(idx), ring: ringV,
           blocks: { rs, cs, W, H, kind, centre } };
}

// a fan block's boundary [r, c], counter-clockwise from the top-left (down the west side,
// east along the south, up the east, west along the north), with every pixel of the
// sides whose neighbour (L, R, T, B: west, east, north, south) is at full detail
function fanRing(r0, r1, c0, c1, L, R, T, B) {
  const ring = [[r0, c0]];
  if (L) for (let r = r0 + 1; r < r1; r++) ring.push([r, c0]);
  ring.push([r1, c0]);
  if (B) for (let c = c0 + 1; c < c1; c++) ring.push([r1, c]);
  ring.push([r1, c1]);
  if (R) for (let r = r1 - 1; r > r0; r--) ring.push([r, c1]);
  ring.push([r0, c1]);
  if (T) for (let c = c1 - 1; c > c0; c--) ring.push([r0, c]);
  return ring;
}

// height (m) at fractional pixel (r, c) on coarseMesh's triangles (m: its result)
export function meshAt(h, split, m, nx, ny, r, c) {
  const { rs, cs, W, H, kind, centre } = m.blocks;
  r = Math.min(Math.max(r, 0), ny - 1); c = Math.min(Math.max(c, 0), nx - 1);
  const find = (a, x) => { let lo = 0, hi = a.length - 2; while (lo < hi) { const md = (lo + hi + 1) >> 1; if (a[md] <= x) lo = md; else hi = md - 1; } return lo; };
  const a = Math.min(find(rs, r), H - 1), b = Math.min(find(cs, c), W - 1), k = a * W + b;
  if (kind[k] === 1) return meshHeight(h, split, nx, ny, r, c);
  const r0 = rs[a], r1 = rs[a + 1], c0 = cs[b], c1 = cs[b + 1];
  if (kind[k] !== 3) {
    const fr = (r - r0) / (r1 - r0), fc = (c - c0) / (c1 - c0);
    const A = h[r0 * nx + c0], B = h[r0 * nx + c1], D = h[r1 * nx + c0], E = h[r1 * nx + c1];
    if (kind[k] === 0) return fr >= fc ? A + (D - A) * fr + (E - D) * fc : A + (B - A) * fc + (E - B) * fr;
    return fr + fc <= 1 ? A + (B - A) * fc + (D - A) * fr : E + (D - E) * (1 - fc) + (B - E) * (1 - fr);
  }
  // a fan: the triangle (centre, p, q) round the centre that holds the point
  const ci = centre[k], cr = (ci / nx) | 0, cc = ci - cr * nx;
  const fineAt = (aa, bb) => aa >= 0 && bb >= 0 && aa < H && bb < W && kind[aa * W + bb] === 1;
  const ring = fanRing(r0, r1, c0, c1, fineAt(a, b - 1), fineAt(a, b + 1), fineAt(a - 1, b), fineAt(a + 1, b));
  const hc = h[ci];
  for (let j = 0; j < ring.length; j++) {
    const p = ring[j], q = ring[(j + 1) % ring.length];
    // barycentric in (c, r)
    const x1 = p[1] - cc, y1 = p[0] - cr, x2 = q[1] - cc, y2 = q[0] - cr, x = c - cc, y = r - cr;
    const det = x1 * y2 - x2 * y1;
    if (Math.abs(det) < 1e-12) continue;
    const u = (x * y2 - x2 * y) / det, v = (x1 * y - x * y1) / det;
    if (u >= -1e-9 && v >= -1e-9 && u + v <= 1 + 1e-9) return hc + u * (h[p[0] * nx + p[1]] - hc) + v * (h[q[0] * nx + q[1]] - hc);
  }
  return hc;
}

// Chaikin-smoothed polyline [[x, y, ...], ...] (ends kept; the extra values follow the nearer end)
export function chaikin(p, n = 2) {
  for (let it = 0; it < n && p.length > 2; it++) {
    const o = [p[0]];
    for (let j = 0; j < p.length - 1; j++) {
      const a = p[j], b = p[j + 1];
      o.push([0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1], ...a.slice(2)],
        [0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1], ...b.slice(2)]);
    }
    o.push(p[p.length - 1]);
    p = o;
  }
  return p;
}

// A river's painted line, smoothed but kept on its valley floor: the smoothing
// cuts the D8 path's corners, and where a corner's off-river pixel is a valley
// side (a gorge one pixel wide, a fall's face, a river zigzagging between
// diagonals) the cut corner lies up that side, so the painted water climbs it
// and drops back (PW-375). Each smoothed point whose ground H(x, y) stands more
// than tol metres above the path's ground at its nearest point on the path is
// pulled back towards that point until it doesn't, and so is the middle of
// each piece between them (split there, down to 1/4096 of a piece), until the
// line runs on the floor. p: the path [[x, y, ...], ...]; returns the line.
export function hugChaikin(p, H, n = 2, tol = 1) {
  const c = chaikin(p, n);
  if (p.length < 3) return c;
  const m = p.length - 1;
  // (pt, segment near it) -> [pt, or pt pulled back towards its nearest point on the path; that point's segment]
  const pull = (pt, k) => {
    const [x, y] = pt;
    let best = Infinity, px = x, py = y, kb = k;
    for (let i = Math.max(0, k - 2); i <= Math.min(m - 1, k + 3); i++) {
      const ax = p[i][0], ay = p[i][1], dx = p[i + 1][0] - ax, dy = p[i + 1][1] - ay, l2 = dx * dx + dy * dy || 1;
      const t = Math.min(Math.max(((x - ax) * dx + (y - ay) * dy) / l2, 0), 1);
      const qx = ax + t * dx, qy = ay + t * dy, d2 = (x - qx) ** 2 + (y - qy) ** 2;
      if (d2 < best) { best = d2; px = qx; py = qy; kb = i; }
    }
    const ref = H(px, py) + tol;
    if (H(x, y) <= ref) return [pt, kb];
    let lo = 0, hi = 1;  // (the share of the way from the path's point to pt)
    for (let it = 0; it < 10; it++) {
      const t = (lo + hi) / 2;
      if (H(px + t * (x - px), py + t * (y - py)) <= ref) lo = t; else hi = t;
    }
    return [[px + lo * (x - px), py + lo * (y - py), ...pt.slice(2)], kb];
  };
  const out = [c[0]];
  let k = 0;
  // the line on from a (the last point out) to b, split where its middle climbs
  const add = (a, b, depth) => {
    const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, ...b.slice(2)], [mp] = pull(mid, k);
    if (mp !== mid && depth < 12) { add(a, mp, depth + 1); add(mp, b, depth + 1); } else out.push(b);
  };
  for (let j = 1; j < c.length; j++) {
    let b = c[j];
    if (j < c.length - 1) [b, k] = pull(c[j], k);
    add(out[out.length - 1], b, 0);
  }
  return out;
}

// D8 slot (the zoom's `receiver` layer, planet/zoom.py d8_slots: 0 NW, 1 N,
// 2 NE, 3 W, 4 E, 5 SW, 6 S, 7 SE; rows run south) -> [dr, dc]; 255: none
export const D8 = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];

// The rivers of a zoom tile (zoom3d.js's Tile.flow). Each river (and lake)
// pixel's downstream neighbour, as the zoom's landscape pass routed the water
// (its `receiver` layer, PW-373; a zoom without one has no rivers here: make
// it again). Then the river lines: runs of river pixels between heads,
// confluences and the water they end in.
// L: {elevation, water, lake_depth, discharge, drainage_area, ice, receiver}; returns {rec, lines, ws}.
export function riverNet(L, nx, ny, res, qmin) {
  const n = nx * ny, q = L.discharge, water = L.water, area = L.drainage_area, ice = L.ice, slot = L.receiver;
  const minArea = 500 * Math.max(res / 2, 1);
  const ws = new Float32Array(n);
  for (let i = 0; i < n; i++) ws[i] = water[i] === 2 ? L.elevation[i] + L.lake_depth[i] : water[i] === 1 ? 0 : L.elevation[i];
  const rec = new Int32Array(n).fill(-1), isR = new Uint8Array(n);
  for (let i = 0; slot && i < n; i++) {
    // (lake pixels too: a fall's reach runs on through its plunge pool)
    if (water[i] === 1 || !(q[i] >= qmin) || slot[i] > 7) continue;
    if (water[i] === 0 && area[i] >= minArea && !(ice[i] > 0)) isR[i] = 1;
    const [dr, dc] = D8[slot[i]];
    rec[i] = i + dr * nx + dc;
  }
  const ndon = new Uint8Array(n);
  for (let i = 0; i < n; i++) if (isR[i] && rec[i] >= 0 && isR[rec[i]]) ndon[rec[i]]++;
  const lines = [];
  for (let s = 0; s < n; s++) {
    if (!isR[s] || ndon[s] === 1) continue;
    const pts = [s];
    let p = rec[s], k = 0;
    while (p >= 0 && k++ < 4 * (nx + ny)) {
      pts.push(p);
      if (!isR[p] || ndon[p] !== 1) break;
      p = rec[p];
    }
    if (pts.length > 1) lines.push(pts);
  }
  return { rec, lines, ws };
}

// The lakes' water (zoom3d.js's Tile.lakes, PW-537): each lake, a 4-connected
// set of lake pixels, is ONE flat surface at its level (the mean of its pixels'
// elevation + depth), clipped by the drawn terrain: the same triangles
// quadSplits chose, cut where the ground rises through the level, so the shore
// is the ground's own contour (no pixel staircase, no spikes) and nothing floats
// over dry ground. A dry neighbour lower than the level (a lake's outlet, the
// foot of a fall: where the water would run on) ends the water half way to it,
// with a short wall of water down to the ground there instead of a tilted skirt.
// h: ground heights (lake pixels: the bed); water: 2 on lake pixels; depth: lake_depth;
// kind: per-pixel lake kind or null. Returns {pos: top triangles' vertices [c, y, r] (c, r in
// fractional pixels), kind: per vertex, wall: the walls' triangles [c, y, r], levels: [{level, px}]}.
export function lakeSurfaces(h, water, depth, split, nx, ny, kind = null) {
  const n = nx * ny, lab = new Int32Array(n);
  const levels = [], pos = [], kinds = [], wall = [];
  const sum = [], cnt = [];
  let k = 0;
  for (let s = 0; s < n; s++) {
    if (water[s] !== 2 || lab[s]) continue;
    k++; lab[s] = k; sum.push(0); cnt.push(0);
    const st = [s];
    while (st.length) {
      const i = st.pop(), r = (i / nx) | 0, c = i - r * nx;
      sum[k - 1] += h[i] + (depth[i] || 0); cnt[k - 1]++;
      for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
        const rr = r + dr, cc = c + dc, j = rr * nx + cc;
        if (rr >= 0 && cc >= 0 && rr < ny && cc < nx && water[j] === 2 && !lab[j]) { lab[j] = k; st.push(j); }
      }
    }
  }
  if (!k) return null;
  const Z = sum.map((v, j) => v / cnt[j]);
  const seen = new Map();  // cell -> lakes that already drew it
  for (let s = 0; s < n; s++) {
    if (!lab[s]) continue;
    const r0 = (s / nx) | 0, c0 = s - r0 * nx, id = lab[s];
    for (let dr = -1; dr <= 0; dr++) for (let dc = -1; dc <= 0; dc++) {
      const r = r0 + dr, c = c0 + dc;
      if (r < 0 || c < 0 || r >= ny - 1 || c >= nx - 1) continue;
      const key = (r * (nx - 1) + c) * 4096 + id;
      if (seen.has(key)) continue;
      seen.set(key, 1);
      const z = Z[id - 1], a = r * nx + c, px = [a, a + 1, a + nx, a + nx + 1];
      // f: how far the level stands over each corner's ground (> 0 wet); a lower dry corner is cut at the half way
      let fm = 0;
      for (const i of px) if (lab[i] === id) fm = Math.max(fm, z - h[i], 0.05);
      const f = {}, g = {};
      for (const i of px) {
        g[i] = h[i];
        f[i] = lab[i] === id ? Math.max(z - h[i], 0.05) : h[i] > z ? z - h[i] : -fm;
      }
      const [A, B, D, E] = px, tris = split[r * (nx - 1) + c] ? [[A, D, E], [A, E, B]] : [[A, D, B], [B, D, E]];
      for (const t of tris) {
        // clip the triangle to f > 0 (Sutherland-Hodgman on one plane)
        const V = t.map((i) => ({ c: i % nx, r: (i / nx) | 0, f: f[i], g: g[i], k: lab[i] === id ? (kind ? kind[i] : 1) : -1 }));
        const out = [];
        for (let j = 0; j < 3; j++) {
          const p = V[j], q = V[(j + 1) % 3];
          if (p.f > 0) out.push({ ...p, cut: false });
          if ((p.f > 0) !== (q.f > 0)) {
            const u = p.f / (p.f - q.f);
            out.push({ c: p.c + u * (q.c - p.c), r: p.r + u * (q.r - p.r), f: 0, g: p.g + u * (q.g - p.g), k: p.k >= 0 ? p.k : q.k, cut: true });
          }
        }
        if (out.length < 3) continue;
        const kk = V.find((v) => v.k >= 0)?.k ?? 1;
        for (let j = 1; j < out.length - 1; j++) for (const p of [out[0], out[j], out[j + 1]]) { pos.push(p.c, z, p.r); kinds.push(kk); }
        // the cut's wall, where the ground there is below the level
        const cuts = out.filter((p) => p.cut);
        if (cuts.length === 2 && (cuts[0].g < z - 0.05 || cuts[1].g < z - 0.05)) {
          const [p, q] = cuts;
          wall.push(p.c, z, p.r, q.c, z, q.r, q.c, Math.min(q.g, z), q.r, p.c, z, p.r, q.c, Math.min(q.g, z), q.r, p.c, Math.min(p.g, z), p.r);
        }
      }
    }
  }
  return { pos, kind: kinds, wall, levels: Z.map((level, j) => ({ level, px: cnt[j] })) };
}
