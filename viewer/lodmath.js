// The level-of-detail tile pyramid's addressing, as planet/zoom/lod.py has it (PW-1688; plan: docs/review/zoom/lod-plan-v2.md).
// No three.js, so the tests can import it (tests/test_viewer_lod.py checks it against lod.py).
//
// Every 4,000 km tiling cell is the root of a pyramid of square tiles laid on the cell's own plane (its section's
// azimuthal equidistant frame, x east / y up, km, the square [-2000, 2000]). Level 1 is the whole square; each finer
// level is a grid of tiles on one pixel lattice. A key is {cell, level, tx, ty}, tx east and ty south from the
// square's north-west corner.
export const SQUARE_KM = 4000;
export const HALF = SQUARE_KM / 2;
export const R_KM = 6371;
// level -> [res_km, tile_km] (lod.LEVELS)
export const LEVELS = { 1: [4.0, 4000.0], 2: [1.0, 500.0], 3: [0.25, 125.0], 4: [0.025, 12.5] };
export const FINEST = 4;

export const resKm = (level) => LEVELS[level][0];
export const tileKm = (level) => LEVELS[level][1];
export const tilePx = (level) => Math.round(LEVELS[level][1] / LEVELS[level][0]);
export const perSide = (level) => Math.round(SQUARE_KM / tileKm(level));
export const branching = (level) => Math.round(tileKm(level) / tileKm(level + 1));

export const key = (cell, level, tx, ty) => ({ cell, level, tx, ty, id: `${cell}/${level}/${tx}/${ty}` });
export function parseKey(s) { const [cell, level, tx, ty] = s.split('/'); return key(cell, +level, +tx, +ty); }

// (x0, x1, y0, y1) km in the cell's plane
export function rect(k) {
  const t = tileKm(k.level), x0 = -HALF + k.tx * t, y1 = HALF - k.ty * t;
  return [x0, x0 + t, y1 - t, y1];
}
export function centreXY(k) { const [x0, x1, y0, y1] = rect(k); return [(x0 + x1) / 2, (y0 + y1) / 2]; }

export function parent(k) {
  if (k.level === 1) return null;
  const b = branching(k.level - 1);
  return key(k.cell, k.level - 1, Math.floor(k.tx / b), Math.floor(k.ty / b));
}
export function children(k) {
  if (k.level === FINEST) return [];
  const b = branching(k.level), out = [];
  for (let j = 0; j < b; j++) for (let i = 0; i < b; i++) out.push(key(k.cell, k.level + 1, k.tx * b + i, k.ty * b + j));
  return out;
}
// the tile of a level holding the plane point (x, y)
export function tileAt(cell, level, x, y) {
  const t = tileKm(level), n = perSide(level), c = (v) => Math.min(n - 1, Math.max(0, Math.floor(v)));
  return key(cell, level, c((x + HALF) / t), c((HALF - y) / t));
}
// where (x, y) falls in a tile, as texture coordinates (u east, v south: row 0 is the tile's north edge)
export function tileUV(k, x, y) { const [x0, , , y1] = rect(k), t = tileKm(k.level); return [(x - x0) / t, (y1 - y) / t]; }

// the level a tile pixel of res_km stops being finer than a screen pixel: refine when a pixel of the next level would
// cover more than refinePx screen pixels at distance distKm (focalPx: the screen's focal length in CSS pixels)
export const pixelsOnScreen = (resKmV, distKm, focalPx) => resKmV / Math.max(distKm, 1e-6) * focalPx;

// IEEE half float -> number (view.bin's elevation; for the few CPU samples: the camera's ground)
export function halfToFloat(h) {
  const s = h & 0x8000 ? -1 : 1, e = (h >> 10) & 0x1f, f = h & 0x3ff;
  if (e === 0) return s * 2 ** -14 * (f / 1024);
  if (e === 31) return f ? NaN : s * Infinity;
  return s * 2 ** (e - 15) * (1 + f / 1024);
}

// ---- which tiles the pyramid has (lod.exists): a tile comes within PAD_PX of its own pixels of its cell's outline
// (outline: [[x, y], ...] km in the cell's plane, closed by wrapping; the tile index sends it); level 1 always
export const PAD_PX = 8;
function inside(poly, x, y) {
  let c = false;
  for (let i = 0, n = poly.length; i < n; i++) {
    const [ax, ay] = poly[i], [bx, by] = poly[(i + 1) % n];
    if ((ay > y) !== (by > y) && x < ax + (y - ay) * (bx - ax) / (by - ay)) c = !c;
  }
  return c;
}
// least distance (km) from the polygon's boundary to the rectangle r = [x0, x1, y0, y1] (0 where they cross)
function segRectDist(poly, [x0, x1, y0, y1]) {
  let best = Infinity;
  const n = poly.length;
  for (let i = 0; i < n; i++) {  // a segment crossing the rectangle (Liang-Barsky)
    const [ax, ay] = poly[i], [bx, by] = poly[(i + 1) % n], dx = bx - ax, dy = by - ay;
    let t0 = 0, t1 = 1, ok = true;
    for (const [p, q] of [[-dx, ax - x0], [dx, x1 - ax], [-dy, ay - y0], [dy, y1 - ay]]) {
      if (p === 0) { if (q < 0) ok = false; continue; }
      const t = q / p;
      if (p < 0) t0 = Math.max(t0, t); else t1 = Math.min(t1, t);
    }
    if (ok && t0 <= t1) return 0;
  }
  for (let i = 0; i < n; i++) {
    const [ax, ay] = poly[i], [bx, by] = poly[(i + 1) % n], dx = bx - ax, dy = by - ay;
    best = Math.min(best, Math.hypot(Math.max(x0 - ax, 0, ax - x1), Math.max(y0 - ay, 0, ay - y1)));
    const L2 = Math.max(dx * dx + dy * dy, 1e-12);
    for (const [cx, cy] of [[x0, y0], [x0, y1], [x1, y0], [x1, y1]]) {
      const t = Math.min(1, Math.max(0, ((cx - ax) * dx + (cy - ay) * dy) / L2));
      best = Math.min(best, Math.hypot(ax + t * dx - cx, ay + t * dy - cy));
    }
  }
  return best;
}
export function exists(k, outline) {
  if (k.level === 1) return true;
  const r = rect(k), [cx, cy] = centreXY(k);
  if (inside(outline, cx, cy)) return true;
  return segRectDist(outline, r) <= PAD_PX * resKm(k.level);
}

// ---- the tile mesh's ground (globe/lodtiles.js::groundRadius, PW-1696): the gn x gn grid's heights as the vertex
// shader samples them from the n x n elevation (linear filtering, clamped to the edge, below the sea 0), and the height
// at (u, v) on the grid's triangles ((i,j)-(i,j+1)-(i+1,j) and (i+1,j)-(i,j+1)-(i+1,j+1), as lodtiles' index has them)
export function gridHeights(half, n, gn) {
  const vh = new Float32Array(gn * gn), c = (k) => Math.min(n - 1, Math.max(0, k));
  const at = (i, j) => Math.max(0, halfToFloat(half[c(j) * n + c(i)]));
  for (let j = 0; j < gn; j++) for (let i = 0; i < gn; i++) {
    const fx = i / (gn - 1) * n - 0.5, fy = j / (gn - 1) * n - 0.5, x0 = Math.floor(fx), y0 = Math.floor(fy), ax = fx - x0, ay = fy - y0;
    vh[j * gn + i] = (1 - ay) * ((1 - ax) * at(x0, y0) + ax * at(x0 + 1, y0)) + ay * ((1 - ax) * at(x0, y0 + 1) + ax * at(x0 + 1, y0 + 1));
  }
  return vh;
}
export function meshHeightAt(vh, gn, u, v) {
  const gx = Math.min(gn - 1 - 1e-9, Math.max(0, u * (gn - 1))), gy = Math.min(gn - 1 - 1e-9, Math.max(0, v * (gn - 1)));
  const i = Math.floor(gx), j = Math.floor(gy), fu = gx - i, fv = gy - j, a = j * gn + i;
  if (fu + fv <= 1) return vh[a] + fu * (vh[a + 1] - vh[a]) + fv * (vh[a + gn] - vh[a]);
  return vh[a + gn + 1] + (1 - fu) * (vh[a + gn] - vh[a + gn + 1]) + (1 - fv) * (vh[a + 1] - vh[a + gn + 1]);
}

// ---- the globe camera's tilt toward the horizon (globe/dive.js, PW-1696), radians, by the height (km) of the straight-
// down camera over the ground: the automatic tilt grows from 0 at AUTO_HI_KM to AUTO_DEG at AUTO_LO_KM (linear in the
// log of the height: the same step per wheel notch); the user may tilt within a cap of MAX_DEG below CAP_LO_KM, closing
// to 0 at CAP_HI_KM (so scrolling out always ends straight down)
export const TILT = { AUTO_DEG: 75, AUTO_HI_KM: 200, AUTO_LO_KM: 1.5, MAX_DEG: 80, CAP_LO_KM: 200, CAP_HI_KM: 1000 };
const clamp01 = (x) => Math.min(1, Math.max(0, x));
export const autoTilt = (hKm) => TILT.AUTO_DEG * Math.PI / 180 * clamp01(Math.log(TILT.AUTO_HI_KM / hKm) / Math.log(TILT.AUTO_HI_KM / TILT.AUTO_LO_KM));
export const capTilt = (hKm) => TILT.MAX_DEG * Math.PI / 180 * clamp01(Math.log(TILT.CAP_HI_KM / hKm) / Math.log(TILT.CAP_HI_KM / TILT.CAP_LO_KM));
