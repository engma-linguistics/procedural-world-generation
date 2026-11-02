// Placing fine zooms (PW-129) in the zoom 3D view (zoom3d.js): the zooms'
// azimuthal equidistant projection (planet/zoom/regional.py Frame) and the affine map
// that puts a fine zoom's frame into the first zoom's. No three.js, so the
// tests can import it (tests/test_viewer.py).
const R_KM = 6371;

// the zooms' projection (planet/zoom/regional.py Frame): azimuthal equidistant round
// (lat, lon); plane x east, y north, km; or, with `up` (a turned section's zoom.json center.up, PW-1338), y along
// up and x 90 degrees clockwise of it
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export function aeFrame(lat, lon, up = null) {
  const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
  const c = [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  let e, n;
  if (up) {
    const k = dot(up, c); n = [0, 1, 2].map((j) => up[j] - k * c[j]);
    const nn = Math.hypot(...n); n = n.map((v) => v / nn); e = cross(n, c);
  } else {
    e = [-c[1], c[0], 0];
    const ne = Math.hypot(e[0], e[1]);
    e = ne < 1e-9 ? [0, 1, 0] : [e[0] / ne, e[1] / ne, 0];
    n = cross(c, e);
  }
  return {
    C: c, E: e, N: n,
    toPlane(p) {
      const rho = Math.acos(Math.min(1, Math.max(-1, dot(p, c)))), a = dot(p, e), b = dot(p, n), s = Math.hypot(a, b);
      const k = s > 1e-12 ? rho * R_KM / s : 0;
      return [a * k, b * k];
    },
    toSphere(x, y) {
      const rho = Math.hypot(x, y) / R_KM, az = Math.atan2(x, y), sa = Math.sin(az), ca = Math.cos(az);
      return [0, 1, 2].map((j) => Math.cos(rho) * c[j] + Math.sin(rho) * (sa * e[j] + ca * n[j]));
    },
  };
}
export const latlonOf = (p) => [Math.asin(Math.max(-1, Math.min(1, p[2]))) * 180 / Math.PI, Math.atan2(p[1], p[0]) * 180 / Math.PI];

// a fine zoom's place in the scene (the first zoom's frame): each of a 9 x 9
// grid of its points -> lat/lon -> the scene, fitted by least squares as
// X = a x + b z + tx, Z = c x + d z + tz (x, z: its own frame, km east and
// south of its centre); err: the fit's largest miss over the grid, km
export function place(fine, root, w, d) {
  const F = aeFrame(fine.lat, fine.lon, fine.up), R = aeFrame(root.lat, root.lon, root.up), A = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], bx = [0, 0, 0], bz = [0, 0, 0], pts = [];
  for (let i = 0; i < 9; i++) for (let j = 0; j < 9; j++) {
    const x = (j / 8 - 0.5) * w, z = (i / 8 - 0.5) * d, [X, Y] = R.toPlane(F.toSphere(x, -z)), v = [x, z, 1];
    pts.push([x, z, X, -Y]);
    for (let p = 0; p < 3; p++) { bx[p] += v[p] * X; bz[p] += v[p] * -Y; for (let q = 0; q < 3; q++) A[p][q] += v[p] * v[q]; }
  }
  const solve = (b) => {  // (3 x 3 Cramer)
    const det3 = (m) => m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    const D = det3(A);
    return [0, 1, 2].map((k) => det3(A.map((row, r) => row.map((v, c) => (c === k ? b[r] : v)))) / D);
  };
  const [a, b, tx] = solve(bx), [c, dd, tz] = solve(bz);
  let err = 0;
  for (const [x, z, X, Z] of pts) err = Math.max(err, Math.hypot(a * x + b * z + tx - X, c * x + dd * z + tz - Z));
  return { M: [a, b, c, dd], T: [tx, tz], err };
}
