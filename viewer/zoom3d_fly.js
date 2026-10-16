// "Fly along a river" for the zoom 3D view (zoom3d.js): the zoom's biggest
// rivers as courses from head to mouth, and a camera that follows one
// downstream at low altitude, slowing past its falls.
//
// A course is the main stem traced upstream from where a river ends (the sea,
// a closed lake, or the zoom's edge): at each pixel the donor carrying the most
// water (Tile.flow's receivers), through lakes, until the stream is under
// QMIN. Scene units as zoom3d.js: x, z in km, heights in metres (scaled by
// exag / 1000 in the scene).
import * as THREE from 'three';

const QMIN = 10;            // m3/s, as zoom3d.js: the smallest river drawn
const MIN_PX = 25;          // a course this many pixels long at least
const SMOOTH_KM = 6;        // the camera's path: the course averaged over this
const FALL_SLOW_KM = 4;     // slower within this of a fall

// t: a Tile (zoom3d.js), falls: its falls with .path; up to max courses, biggest mouth first
export function riverCourses(t, falls, max = 12) {
  const { nx, ny, L, rec } = t, n = nx * ny, q = L.discharge, water = L.water;
  // donors: each pixel's upstream neighbours (as CSR lists)
  const cnt = new Int32Array(n + 1);
  for (let i = 0; i < n; i++) if (rec[i] >= 0) cnt[rec[i] + 1]++;
  for (let i = 0; i < n; i++) cnt[i + 1] += cnt[i];
  const don = new Int32Array(cnt[n]), fill = cnt.slice(0, n);
  for (let i = 0; i < n; i++) if (rec[i] >= 0) don[fill[rec[i]]++] = i;
  // ends: river pixels on land whose water goes on into the sea, off the zoom, or nowhere
  const ends = [];
  for (let i = 0; i < n; i++) {
    if (water[i] !== 0 || !(q[i] >= 4 * QMIN)) continue;
    const r = rec[i];
    if (r < 0 || water[r] === 1) ends.push(i);
  }
  ends.sort((a, b) => q[b] - q[a]);
  const used = new Uint8Array(n), courses = [];
  const fallAt = new Map();
  falls.forEach((f) => fallAt.set(f.px[0] * nx + f.px[1], f));
  for (const e of ends) {
    if (courses.length >= max) break;
    if (used[e]) continue;
    const up = [e];
    let p = e;
    for (let k = 0; k < 4 * (nx + ny); k++) {
      let best = -1, bq = QMIN;
      for (let j = cnt[p]; j < cnt[p + 1]; j++) { const d = don[j]; if (q[d] >= bq && !used[d]) { bq = q[d]; best = d; } }
      if (best < 0) break;
      up.push(best); p = best;
    }
    if (up.length < MIN_PX) continue;
    // (a course that ran into one already traced is a tributary: kept only if long by itself)
    for (const i of up) used[i] = 1;
    const path = up.reverse(), km = [0];
    for (let j = 1; j < path.length; j++) {
      const a = path[j - 1], b = path[j];
      km.push(km[j - 1] + (a % nx !== b % nx && ((a / nx) | 0) !== ((b / nx) | 0) ? 1.4142 : 1) * t.res);
    }
    const fs = [];
    path.forEach((i, j) => { const f = fallAt.get(i); if (f) fs.push({ ...f, km: km[j] }); });
    const end = rec[e] < 0 ? 'the edge' : 'the sea';
    courses.push({ path, km, length_km: km[km.length - 1], q: q[e], falls: fs, end,
                   lake: path.some((i) => water[i] === 2) });
  }
  courses.forEach((c, k) => (c.k = k));
  return courses;
}

// moving average of a[] over w samples either side (ends kept)
function smooth(a, w) {
  const n = a.length, o = new Float32Array(n), cs = new Float64Array(n + 1);
  for (let i = 0; i < n; i++) cs[i + 1] = cs[i] + a[i];
  for (let i = 0; i < n; i++) { const lo = Math.max(0, i - w), hi = Math.min(n - 1, i + w); o[i] = (cs[hi + 1] - cs[lo]) / (hi - lo + 1); }
  return o;
}
// running max over w samples either side
function runMax(a, w) {
  const n = a.length, o = new Float32Array(n);
  for (let i = 0; i < n; i++) { let m = -Infinity; for (let j = Math.max(0, i - w); j <= Math.min(n - 1, i + w); j++) m = Math.max(m, a[j]); o[i] = m; }
  return o;
}

// A flight down course c of tile t: the camera's path (smoothed), its height
// above the water (never under a fall's lip just ahead), and where the falls are.
export class Flight {
  constructor(t, c, { speed = 8, clearance = null } = {}) {
    const { nx } = t, n = c.path.length;
    const x = new Float32Array(n), z = new Float32Array(n), ws = new Float32Array(n);
    c.path.forEach((i, j) => { x[j] = t.x(i % nx); z[j] = t.z((i / nx) | 0); ws[j] = Math.max(t.wsA[i], 0); });
    const w = Math.max(1, Math.round(SMOOTH_KM / t.res / 2));
    this.x = smooth(smooth(x, w), w); this.z = smooth(smooth(z, w), w);
    // (metres above the water: more on a coarse zoom, whose valleys are wider)
    this.clear = clearance ?? 500 + 500 * t.res;
    this.y = smooth(runMax(ws, w + 2), w);
    this.ground = ws;
    this.km = Float32Array.from(c.km);
    this.len = c.length_km; this.course = c; this.speed = speed;
    this.s = 0; this.t = performance.now(); this.paused = false;
  }
  // position (x, y m, z) at s km along, interpolated
  at(s) {
    const km = this.km, n = km.length;
    s = Math.min(Math.max(s, 0), this.len);
    let lo = 0, hi = n - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (km[m] <= s) lo = m; else hi = m; }
    const f = km[hi] > km[lo] ? (s - km[lo]) / (km[hi] - km[lo]) : 0, L = (a) => a[lo] + (a[hi] - a[lo]) * f;
    return { x: L(this.x), y: L(this.y), z: L(this.z), ground: L(this.ground) };
  }
  // km to the nearest fall (ahead or just behind)
  nearFall(s) {
    let d = Infinity;
    for (const f of this.course.falls) if (f.km > s - 1) d = Math.min(d, Math.abs(f.km - s));
    return d;
  }
  // advance by the time since the last call; returns false at the mouth
  step(now) {
    const dt = Math.min((now - this.t) / 1000, 0.1);
    this.t = now;
    if (this.paused) return true;
    const slow = this.nearFall(this.s) < FALL_SLOW_KM ? 0.35 : 1;
    this.s += this.speed * slow * dt;
    return this.s < this.len;
  }
  // the camera: a little above the water at s, looking ahead down the river
  // (exag: metres -> scene units; groundY(x, z): the scene's ground height there)
  pose(exag, groundY, res) {
    const s = this.s, k = exag / 1000, ahead = Math.max(5, 8 * res);
    const p = this.at(s), a = this.at(s + ahead);
    const pos = new THREE.Vector3(p.x, (p.y + this.clear) * k, p.z);
    pos.y = Math.max(pos.y, groundY(pos.x, pos.z) + 0.6 * this.clear * k);
    const tgt = new THREE.Vector3(a.x, (a.ground + 0.3 * this.clear) * k, a.z);
    return { pos, tgt };
  }
  info() {
    const s = this.s, next = this.course.falls.find((f) => f.km > s);
    return `km ${Math.round(s)} of ${Math.round(this.len)}` + (next ? ` · next fall ${Math.round(next.height_m)} m in ${Math.max(0, next.km - s).toFixed(1)} km` : '');
  }
}
