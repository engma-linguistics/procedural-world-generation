// 3D relief on the globe and the flat map: the "3D relief" toggle under View
// (index.html). With it on, the ground stands at its surface (land ice and
// lake surfaces included, so ice sheets and lakes read as heights), the sea
// floor sinks to its depth under a translucent sea, the flat map is raised
// into a tilting relief model, and a low sun lights it all instead of the
// head-on light, so mountain ranges, rifts, trenches and ice sheets show in
// relief. For worlds, runs and time zooms alike: the heights are rewritten
// every replay frame with the mesh's positions (index.html paint), so a time
// zoom's ice sheets grow and shrink in 3D as it plays.
//
// The globe's mesh (index.html buildTopology) has its own vertices per cell:
// the centre and a copy of each corner. radii() gives the radius of each
// centre (0..n-1) and each corner (n..n+nc-1); each vertex takes its source's.
import * as THREE from 'three';

export const DEFAULTS = { ex: 50, sunAz: 135, sunEl: 60, sea: true };

// Each cell's displayed height (m): land at its surface (a run's or world's
// elevation is the bed, floored at 1 m under grounded ice: the ice goes on
// top; a time zoom's elevation is already the ice surface, bed + ice), a lake
// at its surface, the sea floor at its depth (or at 0 without the sea floor).
export function surfaceHeights(V, seaFloor, out) {
  const L = V.layers, n = V.n, e = L.elevation, ice = L.ice, bed = L.bed;
  const kind = L.lake_kind, ld = L.lake_depth, ll = L.lake_level;
  if (!out || out.length !== n) out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    let h = e[i];
    if (ice && bed && ice[i] > 0) h = Math.max(bed[i] + ice[i], 1);
    else if (h > 0 && kind && (kind[i] === 1 || kind[i] === 2)) {
      const d = ld ? ld[i] : ll ? ll[i] - h : 0;
      if (d > 0) h += d;
    }
    out[i] = h > 0 || seaFloor ? h : 0;
  }
  return out;
}

// The radius (1 = sea level) of each cell centre, then of each corner (the
// mean of the cells round it), from heights H (m) at ex units per metre.
// With the sea floor down, a corner between land and sea stands at sea level:
// the coast runs along the cells' edges, the land rising from the water at
// them, the sea floor falling away from them (a mean there would drown the
// coastal land under the sea surface).
const COAST_M = 2;  // (just above the sea surface: no flicker along the coast)
export function radii(H, cStart, cList, n, ex, seaFloor, R) {
  const nc = cStart.length - 1;
  if (!R || R.length !== n + nc) R = new Float32Array(n + nc);
  for (let i = 0; i < n; i++) R[i] = 1 + ex * H[i];
  for (let k = 0; k < nc; k++) {
    const a = cStart[k], b = cStart[k + 1];
    let s = 0, land = 0;
    for (let q = a; q < b; q++) { const h = H[cList[q]]; s += h; if (h > 0) land++; }
    R[n + k] = seaFloor && land && land < b - a ? 1 + ex * COAST_M : 1 + ex * s / (b - a);
  }
  return R;
}

// Smooth normals for the globe's relief (flat shading shows every cell's
// six facets): a normal per cell centre (the sum of its fan's triangles) and
// per corner (the triangle of its three cells' centres), each vertex taking
// its source's (vSrc), as the radii; out: normalized Int8 (x 127). U: the unit vectors of the centres then
// the corners (3 (n + nc)); fan: each cell's corners in order (fanStart, fanList).
export function sphereNormals(R, U, n, fanStart, fanList, cStart, cList, vSrc, out) {
  const ns = R.length;
  if (!scratch || scratch.P.length !== 3 * ns) scratch = { P: new Float32Array(3 * ns), N: new Int8Array(3 * ns) };
  const { P, N } = scratch;
  for (let s = 0; s < ns; s++) { const r = R[s], s3 = 3 * s; P[s3] = U[s3] * r; P[s3 + 1] = U[s3 + 1] * r; P[s3 + 2] = U[s3 + 2] * r; }
  for (let i = 0; i < n; i++) {
    const a = fanStart[i], b = fanStart[i + 1], i3 = 3 * i, px = P[i3], py = P[i3 + 1], pz = P[i3 + 2];
    let x = 0, y = 0, z = 0, j = 3 * (n + fanList[b - 1]);
    let ax = P[j] - px, ay = P[j + 1] - py, az = P[j + 2] - pz;
    for (let q = a; q < b; q++) {
      const k = 3 * (n + fanList[q]), bx = P[k] - px, by = P[k + 1] - py, bz = P[k + 2] - pz;
      x += ay * bz - az * by; y += az * bx - ax * bz; z += ax * by - ay * bx;
      ax = bx; ay = by; az = bz;
    }
    // (outward, unit: the fan's order may wind either way)
    let l = 127 / Math.sqrt(x * x + y * y + z * z || 1);
    if (x * U[i3] + y * U[i3 + 1] + z * U[i3 + 2] < 0) l = -l;
    N[i3] = Math.round(x * l); N[i3 + 1] = Math.round(y * l); N[i3 + 2] = Math.round(z * l);
  }
  const nc = cStart.length - 1;
  for (let k = 0; k < nc; k++) {
    const q = cStart[k], a = 3 * cList[q], b = 3 * cList[q + 1], c = 3 * cList[q + 2], k3 = 3 * (n + k);
    const ax = P[b] - P[a], ay = P[b + 1] - P[a + 1], az = P[b + 2] - P[a + 2];
    const bx = P[c] - P[a], by = P[c + 1] - P[a + 1], bz = P[c + 2] - P[a + 2];
    const x = ay * bz - az * by, y = az * bx - ax * bz, z = ax * by - ay * bx;
    let l = 127 / Math.sqrt(x * x + y * y + z * z || 1);
    if (x * U[k3] + y * U[k3 + 1] + z * U[k3 + 2] < 0) l = -l;
    N[k3] = Math.round(x * l); N[k3 + 1] = Math.round(y * l); N[k3 + 2] = Math.round(z * l);
  }
  for (let v = 0, nv = vSrc.length; v < nv; v++) {
    const j = 3 * vSrc[v], v3 = 3 * v;
    out[v3] = N[j]; out[v3 + 1] = N[j + 1]; out[v3 + 2] = N[j + 2];
  }
  return out;
}
let scratch = null;

// The lights: the viewer's head-on light (a hemisphere and a sun fixed to the
// camera, up and to the left) or, for the relief, a low sun at an angle to
// the view, so slopes facing it brighten and the far ones fall into shade.
// az: where it comes from on screen (0 = right, 90 = top, counter-clockwise);
// el: its angle from the line of sight (0 = from behind the camera, 90 = grazing).
export class Lights {
  // (sun: a child of the camera; for the relief its target follows the camera too, so the
  // light's direction on screen is the sliders' wherever the camera looks)
  constructor(hemi, sun) {
    this.hemi = hemi; this.sun = sun;
    this.flat = { hemi: hemi.intensity, sun: sun.intensity, pos: sun.position.clone(), target: sun.target };
    this.target = new THREE.Object3D();
    sun.parent?.add(this.target);
  }
  set(on, az = DEFAULTS.sunAz, el = DEFAULTS.sunEl) {
    if (!on) {
      this.hemi.intensity = this.flat.hemi; this.sun.intensity = this.flat.sun; this.sun.position.copy(this.flat.pos);
      this.sun.target = this.flat.target;
      return;
    }
    this.sun.target = this.target;
    const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
    this.hemi.intensity = 0.55;
    this.sun.intensity = 2.3;
    this.sun.position.set(Math.sin(e) * Math.cos(a), Math.sin(e) * Math.sin(a), Math.cos(e)).multiplyScalar(3);
  }
}

// The sea surface over the sunken sea floor: a translucent shell at sea level
// on the globe (the sun glints on it), a translucent plane on the map. Not
// pickable: hovering finds the floor under it.
let seaMat = null;
export function seaSurface(globe) {
  seaMat ||= new THREE.MeshPhongMaterial({ color: 0x1f5d93, transparent: true, opacity: 0.5, shininess: 320,
    specular: 0x1c2a3a, depthWrite: false });
  seaMat.userData.shared = true;
  const geo = globe ? new THREE.SphereGeometry(1, 256, 128) : new THREE.PlaneGeometry(4.2, 2);
  const m = new THREE.Mesh(geo, seaMat);
  m.renderOrder = 1;
  m.raycast = () => {};
  return m;
}
