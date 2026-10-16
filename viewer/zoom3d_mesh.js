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
