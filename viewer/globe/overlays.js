import * as THREE from 'three';
import { S, state } from './state.js';
import { $, DIAG, group } from './scene.js';
import { huOverlays, techOverlays, techTree } from './colours.js';
import { cellPos, cellPositions, disposeObj, lineObj, llMode, llPoint, llPos, llPosPt, plateVelocity, reliefScale, ribbonObj, select, toThree, unitVec } from './geometry.js';
import { buildAxis, buildLandmassNames } from './axis.js';
import { projOverlaysChanged, windKey } from './map2d.js';
import { buildHighlightMarks } from './highlights.js';
import { buildZoomOutlines } from './tabs.js';
// ------------------------------------------------------------ clouds
// The cloud overlay: an equirectangular texture whose patches cover each
// place's cloud share (cloud_jul / cloud_jan, or their mean) of the sky.
// The shapes are made up: fractal noise on the sphere, thresholded at the
// local share (the noise's own distribution, so the cover comes out right).
const CLOUD_W = 2048, CLOUD_H = 1024, cloudCache = new Map();
function hash3(x, y, z) {
  let h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 2147483647);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
function vnoise(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const u = x - xi, v = y - yi, w = z - zi;
  const fu = u * u * (3 - 2 * u), fv = v * v * (3 - 2 * v), fw = w * w * (3 - 2 * w);
  const l = (a, b, t) => a + (b - a) * t;
  return l(l(l(hash3(xi, yi, zi), hash3(xi + 1, yi, zi), fu), l(hash3(xi, yi + 1, zi), hash3(xi + 1, yi + 1, zi), fu), fv),
           l(l(hash3(xi, yi, zi + 1), hash3(xi + 1, yi, zi + 1), fu), l(hash3(xi, yi + 1, zi + 1), hash3(xi + 1, yi + 1, zi + 1), fu), fv), fw);
}
function cloudTexture(season) {
  const key = `${S.V.id}|${season}`;
  if (cloudCache.has(key)) return cloudCache.get(key);
  const L = S.V.layers, G = S.V.grid, W = CLOUD_W, H = CLOUD_H;
  // the cloud share per texel: cells drawn as polygons, blurred
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const cx = cv.getContext('2d');
  for (let i = 0; i < S.V.n; i++) {
    const c = season ? L['cloud_' + season][i] : 0.5 * (L.cloud_jul[i] + L.cloud_jan[i]), g = Math.round(2.55 * c);
    cx.fillStyle = `rgb(${g},${g},${g})`;
    const lon0 = G.lon[i], cs = G.cells[i];
    const xs = cs.map((k) => { let d = G.corner_lon[k] - lon0; d -= 360 * Math.round(d / 360); return (lon0 + d + 180) / 360 * W; });
    const shifts = [0]; if (Math.min(...xs) < 0) shifts.push(W); if (Math.max(...xs) > W) shifts.push(-W);
    for (const sh of shifts) {
      cx.beginPath();
      cs.forEach((k, j) => { const y = (90 - G.corner_lat[k]) / 180 * H; j ? cx.lineTo(xs[j] + sh, y) : cx.moveTo(xs[j] + sh, y); });
      cx.fill();
    }
  }
  const cv2 = document.createElement('canvas'); cv2.width = W; cv2.height = H;
  const c2 = cv2.getContext('2d');
  c2.filter = 'blur(10px)'; c2.drawImage(cv, 0, 0);
  const share = c2.getImageData(0, 0, W, H).data;
  // fractal noise on the sphere (stretched east-west a little, as weather bands are)
  const nz = new Float32Array(W * H);
  for (let r = 0; r < H; r++) {
    const la = (90 - (r + 0.5) * 180 / H) * Math.PI / 180, cl = Math.cos(la), sl = Math.sin(la);
    for (let q = 0; q < W; q++) {
      const lo = ((q + 0.5) / W * 360 - 180) * Math.PI / 180;
      const x = cl * Math.cos(lo), y = sl * 1.6, z = cl * Math.sin(lo);
      let f = 6, a = 1, v = 0, s = 0;
      for (let o = 0; o < 7; o++) { v += a * vnoise(x * f + 17, y * f + 31, z * f + 5); s += a; f *= 2.1; a *= 0.55; }
      nz[r * W + q] = v / s;
    }
  }
  // the noise's distribution (a sample), to threshold it at quantiles
  const smp = []; for (let j = 0; j < nz.length; j += 97) smp.push(nz[j]);
  smp.sort((a, b) => a - b);
  const qf = (u) => smp[Math.min(smp.length - 1, Math.max(0, Math.floor(u * smp.length)))];
  const img = c2.createImageData(W, H), d = img.data;
  for (let j = 0; j < W * H; j++) {
    const c = 0.9 * share[4 * j] / 255, t = qf(1 - c), soft = 0.06;
    const a = Math.min(1, Math.max(0, (nz[j] - t + soft) / (2 * soft)));
    d[4 * j] = d[4 * j + 1] = d[4 * j + 2] = 250; d[4 * j + 3] = Math.round(225 * a * a * (3 - 2 * a));
  }
  c2.filter = 'none'; c2.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(cv2);
  tex.colorSpace = THREE.SRGBColorSpace;
  cloudCache.set(key, tex);
  return tex;
}
function cloudOverlay() {
  const s = state.season && S.V.layers['cloud_' + state.season] ? state.season : '';
  const tex = cloudTexture(s), globe = state.mode === 'globe';
  const geo = globe ? new THREE.SphereGeometry(1 + reliefScale() * 9000, 128, 64) : new THREE.PlaneGeometry(4, 2);
  const mat = globe ? new THREE.MeshLambertMaterial({ map: tex, transparent: true, depthWrite: false })
                    : new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
  const m = new THREE.Mesh(geo, mat);
  if (!globe) m.position.z = 0.004;
  m.raycast = () => {};  // (hovering picks the ground under the clouds)
  return m;
}

// Peoples runs (planet/lineages/): a ring at each people's origin, in its colour. (The track of each range's centre,
// meta.lineages[].track, stays in the data but is not drawn: PW-857, owner.)
function peopleOverlays(globe, wraps) {
  const lines = S.V.peopleTracks, now = -(S.V.run.frames[S.V.frame]?.t ?? 0), rings = [], rcols = [];
  const c = new THREE.Color(), r0 = globe ? 1.014 : 1;
  // (every point's cell and unit vector once per run, in V.peopleCache: the overlays are rebuilt each frame)
  const cache = S.V.peopleCache ||= new Map(), mode = llMode();
  for (const l of lines) {
    if (l.overlay || (state.people != null && l.index !== state.people)) continue;
    c.set(l.color);
    const o = l.origin_place;
    if (o && o.ago_kyr >= now - 1e-6) {
      let ring = cache.get('o' + l.index);
      if (!ring) {
        const cl = Math.max(Math.cos(o.lat * Math.PI / 180), 0.2);
        ring = [];
        for (let k = 0; k <= 20; k++) { const a = k / 20 * 2 * Math.PI; ring.push(llPoint(o.lat + 2 * Math.sin(a), o.lon + 2 * Math.cos(a) / cl)); }
        cache.set('o' + l.index, ring);
      }
      let p1 = llPosPt(ring[0], r0, mode);
      for (let k = 0; k < 20; k++) {
        const p2 = llPosPt(ring[k + 1], r0, mode);
        if (!wraps(p1, p2)) { rings.push(...p1, ...p2); rcols.push(c.r, c.g, c.b, c.r, c.g, c.b); }
        p1 = p2;
      }
    }
  }
  return { peopleRings: ribbonObj(rings, 0xffffff, 1, 2.5, rcols) };
}
export function buildOverlays() {
  DIAG.n.overlays++;
  Object.values(S.overlays).forEach((o) => { group.remove(o); disposeObj(o); });
  S.overlays = {};
  const G = S.V.grid, L = S.V.layers, globe = state.mode === 'globe';
  if ($('clouds').checked && L.cloud_jul && L.cloud_jan) S.overlays.clouds = cloudOverlay();
  const wraps = (a, b) => !globe && Math.abs(a[0] - b[0]) > 2;   // skip lines across the dateline

  if ($('rivers').checked && L.flow && L.downstream) {
    // the top (100 - riverQ)% of land cells by flow; the biggest 0.5% brighter
    const q = +$('riverQ').value / 100, n = S.V.n, elev = L.elevation, flow = L.flow, down = L.downstream;
    let nl = 0; for (let i = 0; i < n; i++) if (elev[i] > 0) nl++;
    const fl = new Float64Array(nl);
    for (let i = 0, j = 0; i < n; i++) if (elev[i] > 0) fl[j++] = flow[i];
    // the two order statistics, without sorting (quickselect: the sort cost ~5 ms a replay frame)
    const kThr = Math.floor(q * (nl - 1)), kBig = Math.floor(0.995 * (nl - 1));
    const thr = nl ? Math.max(select(fl, kThr, 0), 1e-6) : Infinity;
    const big = nl ? select(fl, kBig, kThr) : Infinity;  // (kBig >= kThr: what's left of kThr is no bigger)
    const small = [], large = [], pos = cellPositions(1.003);
    for (let i = 0; i < n; i++) {
      const d = down[i];
      if (d < 0 || elev[i] <= 0 || flow[i] < thr) continue;
      if (!globe && Math.abs(pos[3 * i] - pos[3 * d]) > 2) continue;  // (wraps: across the dateline)
      (flow[i] >= big ? large : small).push(pos[3 * i], pos[3 * i + 1], pos[3 * i + 2], pos[3 * d], pos[3 * d + 1], pos[3 * d + 2]);
    }
    const sat = state.layer === 'satellite';  // (river water in the satellite view: dark)
    S.overlays.rivers = ribbonObj(small, sat ? 0x2a4d63 : 0x4fb3ff, sat ? 0.7 : 1, 1.5);
    S.overlays.riversBig = ribbonObj(large, sat ? 0x24485e : 0xa8e1ff, 1, 2.5);
  }
  if (S.V.humanUse?.river_nav) Object.assign(S.overlays, huOverlays(globe, wraps));
  if ($('peopleTracks')?.checked && S.V.peopleTracks?.length) Object.assign(S.overlays, peopleOverlays(globe, wraps));
  if (state.layer === 'technology' && techTree() && S.V.data.peoples) Object.assign(S.overlays, techOverlays(globe, wraps));
  if ($('hotspots').checked && S.V.hotspots) {
    const pts = [], globe_ = globe;
    for (const [la, lo] of S.V.hotspots) {
      const r0 = globe_ ? 1.012 : 1;
      for (const rad of [1.2, 2.4]) for (let k = 0; k < 16; k++) {
        const a1 = k / 16 * 2 * Math.PI, a2 = (k + 1) / 16 * 2 * Math.PI, cl = Math.max(Math.cos(la * Math.PI / 180), 0.2);
        const p1 = llPos(la + rad * Math.sin(a1), lo + rad * Math.cos(a1) / cl, r0);
        const p2 = llPos(la + rad * Math.sin(a2), lo + rad * Math.cos(a2) / cl, r0);
        if (!wraps(p1, p2)) pts.push(...p1, ...p2);
      }
    }
    S.overlays.hotspots = lineObj(pts, 0xff9f1c);
  }
  if ($('volcanoes').checked && S.V.volcanoes) {
    // rows [lat, lon, kind (0 arc, 1 hotspot), mark (0 active, 1 extinct island, 2 atoll, 3 dormant,
    // 4 other extinct)]; a run's keyframes list only the active ones. Triangles: red arc, orange
    // hotspot (smaller when an extinct island), yellow dormant, grey-brown extinct (with "extinct
    // ones too"); atolls: cyan rings.
    const arcs = [], vents = [], atolls = [], dormant = [], extinct = [], r0 = globe ? 1.012 : 1;
    for (const [la, lo, kind = 0, mark = 0] of S.V.volcanoes) {
      if (mark === 4 && !$('volcExtinct').checked) continue;
      const cl = Math.max(Math.cos(la * Math.PI / 180), 0.2), s = mark === 3 ? 0.5 : mark ? 0.35 : 0.6;
      const out = mark === 2 ? atolls : mark === 3 ? dormant : mark === 4 ? extinct : kind === 1 ? vents : arcs;
      if (mark === 2) {
        for (let k = 0; k < 8; k++) {
          const a1 = k / 8 * 2 * Math.PI, a2 = (k + 1) / 8 * 2 * Math.PI;
          const p1 = llPos(la + s * Math.sin(a1), lo + s * Math.cos(a1) / cl, r0), p2 = llPos(la + s * Math.sin(a2), lo + s * Math.cos(a2) / cl, r0);
          if (!wraps(p1, p2)) out.push(...p1, ...p2);
        }
        continue;
      }
      const c = [llPos(la + s, lo, r0), llPos(la - 0.6 * s, lo - 0.8 * s / cl, r0), llPos(la - 0.6 * s, lo + 0.8 * s / cl, r0)];
      for (let k = 0; k < 3; k++) if (!wraps(c[k], c[(k + 1) % 3])) out.push(...c[k], ...c[(k + 1) % 3]);
    }
    S.overlays.volcanoes = lineObj(arcs, 0xff2d2d);
    S.overlays.vents = lineObj(vents, 0xffb347);
    S.overlays.atolls = lineObj(atolls, 0x5ff0e6);
    S.overlays.dormant = lineObj(dormant, 0xffe14d);
    S.overlays.extinct = lineObj(extinct, 0xb08d6a);
  }
  if ($('outlines').checked || $('pentas').checked) {
    const cp = (k, i) => {
      if (globe) {
        const cs = S.V.cornerCells[k]; let e = 0; for (const j of cs) e += Math.max(L.elevation[j], 0);
        const r = S.topo.relief && S.topo.R ? S.topo.R[S.V.n + k] : 1 + reliefScale() * e / cs.length;
        return unitVec(G.corner_lat[k], G.corner_lon[k]).map((x) => x * r * 1.001);
      }
      let d = G.corner_lon[k] - G.lon[i]; d -= 360 * Math.round(d / 360);
      return [(G.lon[i] + d) / 90, G.corner_lat[k] / 90, 0.001];
    };
    const ring = (i, arr) => {
      const cs = G.cells[i];
      for (let k = 0; k < cs.length; k++) arr.push(...cp(cs[k], i), ...cp(cs[(k + 1) % cs.length], i));
    };
    if ($('outlines').checked) {
      const pts = []; for (let i = 0; i < S.V.n; i++) ring(i, pts);
      S.overlays.outlines = lineObj(pts, 0x000000, 0.35);
    }
    if ($('pentas').checked) {
      const pts = [];
      for (const p of S.V.pentagons) {
        ring(p, pts);
        const c = cellPos(p, 1.0);
        const out = globe ? cellPos(p, 1.12) : [c[0], c[1], 0.1];
        pts.push(...c, ...out);
      }
      S.overlays.pentas = lineObj(pts, 0xff3df2);
    }
  }
  // winds and currents (~1 = a steady trade wind) and the jet stream (m/s), as (east, north)
  // components; mult scales each to arrow length. Drawn on an evenly spread sample of cells
  const flowArrows = (ke, kn, color, oceanOnly, lvlDrop, mult = 1, r = 1.004) => {
    const nS = Math.min(10 * 4 ** Math.max(S.V.level - lvlDrop, 0) + 2, S.V.n), pts = [], s = 0.0011;
    for (let i = 0; i < nS; i++) {
      if (oceanOnly && L.elevation[i] > 0) continue;
      let ue = L[ke][i] * mult, un = L[kn][i] * mult;
      const m = Math.hypot(ue, un); if (m < 3) continue;
      if (m > 90) { ue *= 90 / m; un *= 90 / m; }
      const la = G.lat[i] * Math.PI / 180, lo = G.lon[i] * Math.PI / 180;
      const a = cellPos(i, r);
      if (globe) {
        // planet-frame east/north -> three.js axes
        const E = new THREE.Vector3(...toThree([-Math.sin(lo), Math.cos(lo), 0]));
        const N = new THREE.Vector3(...toThree([-Math.sin(la) * Math.cos(lo), -Math.sin(la) * Math.sin(lo), Math.cos(la)]));
        const A = new THREE.Vector3(...a), Vv = E.multiplyScalar(ue * s).add(N.multiplyScalar(un * s));
        const B = A.clone().add(Vv), side = new THREE.Vector3().crossVectors(A, Vv).normalize().multiplyScalar(Vv.length() * 0.3);
        const back = Vv.clone().multiplyScalar(-0.35);
        pts.push(...a, ...B.toArray(), ...B.toArray(), ...B.clone().add(back).add(side).toArray(),
                 ...B.toArray(), ...B.clone().add(back).sub(side).toArray());
      } else {
        const e = ue * s, nn = un * s, bx = a[0] + e, by = a[1] + nn;
        pts.push(...a, bx, by, a[2],
                 bx, by, a[2], bx - 0.35 * e - 0.3 * nn, by - 0.35 * nn + 0.3 * e, a[2],
                 bx, by, a[2], bx - 0.35 * e + 0.3 * nn, by - 0.35 * nn - 0.3 * e, a[2]);
      }
    }
    return lineObj(pts, color);
  };
  // runs have these in every keyframe; worlds only when saved with them (tools/earth_world.py)
  if ($('winds').checked && L.wind_e) {
    const w = windKey();  // 'wind' or a half-year's 'wind_jul' / 'wind_jan'
    S.overlays.winds = flowArrows(w + '_e', w + '_n', 0xffe08a, false, 2, 50);
  }
  // (streamlines take ~0.15 s at level 7: arrows while a run plays)
  if ($('currents').checked && L.current_e) {
    if (state.playing) S.overlays.currents = flowArrows('current_e', 'current_n', 0x7fffd4, true, 1, 50);
    else [S.overlays.currents, S.overlays.currentHeads] = streamOverlay('current_e', 'current_n');
  }
  mocGroup.children.forEach(disposeObj);
  mocGroup.clear();
  if ($('overturning').checked && S.V.kind === 'world' && S.V.meta.overturning) {
    const labels = [];
    Object.assign(S.overlays, overturningOverlay(S.V.meta.overturning, labels));
    labels.forEach((l) => mocGroup.add(l));
  }
  if ($('arrows').checked && L.plate) {
    // sample cells from a coarser level of the subdivision: ids < 10*4^(level-2)+2 are evenly spread
    const nSample = 10 * 4 ** Math.max(S.V.level - 2, 0) + 2;
    const ids = [], vs = [];
    for (let i = 0; i < Math.min(nSample, S.V.n); i++) { const v = plateVelocity(i); if (v) { ids.push(i); vs.push(v); } }
    // scale so the average arrow is a fixed length on screen, whatever the units
    const mean = vs.reduce((a, v) => a + Math.hypot(...v), 0) / Math.max(vs.length, 1);
    const pts = [], s = mean > 0 ? 0.07 / mean : 0;
    for (let j = 0; j < ids.length; j++) {
      const i = ids[j], m = Math.hypot(...vs[j]);
      // clamp so a few very fast plates don't swamp the picture
      const v = m * s > 0.18 ? vs[j].map((x) => x * 0.18 / (m * s)) : vs[j];
      const a = cellPos(i, 1.004);
      if (globe) {
        const A = new THREE.Vector3(...a), Vv = new THREE.Vector3(...toThree(v)).multiplyScalar(s);
        const B = A.clone().add(Vv), side = new THREE.Vector3().crossVectors(A, Vv).normalize().multiplyScalar(Vv.length() * 0.3);
        const back = Vv.clone().multiplyScalar(-0.35);
        pts.push(...a, ...B.toArray(), ...B.toArray(), ...B.clone().add(back).add(side).toArray(),
                 ...B.toArray(), ...B.clone().add(back).sub(side).toArray());
      } else {
        const la = G.lat[i] * Math.PI / 180, lo = G.lon[i] * Math.PI / 180;
        const e = (-Math.sin(lo) * v[0] + Math.cos(lo) * v[1]) * s;
        const nn = (-Math.sin(la) * Math.cos(lo) * v[0] - Math.sin(la) * Math.sin(lo) * v[1] + Math.cos(la) * v[2]) * s;
        const bx = a[0] + e, by = a[1] + nn;
        pts.push(...a, bx, by, a[2],
                 bx, by, a[2], bx - 0.35 * e - 0.3 * nn, by - 0.35 * nn + 0.3 * e, a[2],
                 bx, by, a[2], bx - 0.35 * e + 0.3 * nn, by - 0.35 * nn - 0.3 * e, a[2]);
      }
    }
    S.overlays.arrows = lineObj(pts, 0xffffff);
  }
  if (S.V.kind === 'run' && $('events').checked) {
    // events within a short window of the current time get a spike + ring
    const t = S.V.t, win = eventWindow();
    const byKind = {};
    for (const e of S.V.run.events) {
      if (Math.abs(e.t - t) > win) continue;
      const pts = (byKind[e.kind] ||= []);
      const r0 = globe ? 1.01 : 1, r1 = globe ? 1.2 : 1;
      const a = llPos(e.lat, e.lon, r0), b = globe ? llPos(e.lat, e.lon, r1) : [a[0], a[1], a[2] + 0.1];
      pts.push(...a, ...b);
      for (let k = 0; k < 24; k++) {   // ring of ~3 degrees
        const ang1 = k / 24 * 2 * Math.PI, ang2 = (k + 1) / 24 * 2 * Math.PI;
        const p1 = llPos(e.lat + 3 * Math.sin(ang1), e.lon + 3 * Math.cos(ang1) / Math.max(Math.cos(e.lat * Math.PI / 180), 0.2), r0);
        const p2 = llPos(e.lat + 3 * Math.sin(ang2), e.lon + 3 * Math.cos(ang2) / Math.max(Math.cos(e.lat * Math.PI / 180), 0.2), r0);
        if (!wraps(p1, p2)) pts.push(...p1, ...p2);
      }
    }
    for (const [k, pts] of Object.entries(byKind)) S.overlays['ev_' + k] = lineObj(pts, EVENT_COLORS[k] || 0xffffff);
  }
  if (S.picked) {  // the square a zoom would cover
    const pts = [], r0 = globe ? 1.014 : 1, h = S.zoomSize / 2 / 111.2, cl = Math.max(Math.cos(S.picked.lat * Math.PI / 180), 0.1);
    const corners = [[-h, -h], [-h, h], [h, h], [h, -h], [-h, -h]];
    for (let c = 0; c < 4; c++) for (let k = 0; k < 8; k++) {
      const [a0, b0] = corners[c], [a1, b1] = corners[c + 1];
      const f = (t) => llPos(S.picked.lat + a0 + (a1 - a0) * t, S.picked.lon + (b0 + (b1 - b0) * t) / cl, r0);
      const p1 = f(k / 8), p2 = f((k + 1) / 8);
      if (!wraps(p1, p2)) pts.push(...p1, ...p2);
    }
    S.overlays.zoomRegion = lineObj(pts, 0xffffff);
  }
  Object.values(S.overlays).forEach((o) => group.add(o));
  buildAxis();
  buildLandmassNames();
  buildHighlightMarks();
  buildZoomOutlines();
  projOverlaysChanged();
}
// ------------------------------------------------------------ ocean currents as streamlines, the overturning loop
// Streamlines (Jobard & Lefer 1997, simplified): from evenly spread seeds,
// trace the current both ways (midpoint steps on the sphere, the velocity
// interpolated from the nearest cells) until the line reaches land, slack
// water, or comes within STREAM_SEP of another line (or closes on itself:
// a gyre). Brighter = faster; chevrons show the way it flows. Cached per
// world / frame, in lat/lon.
const STREAM_SEP = 2.6 * Math.PI / 180;  // rad between neighbouring lines
function lineColored(pts, cols, opacity = 1) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
  return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: opacity < 1, opacity }));
}
function streamlines(ke, kn) {
  const key = `${ke}|${S.V.kind === 'run' ? S.V.t : S.V.id}`;
  if (S.V._stream && S.V._stream.key === key) return S.V._stream.lines;
  const G = S.V.grid, L = S.V.layers, n = S.V.n, nbr = G.nbr;
  const P = new Float64Array(3 * n), U = new Float64Array(3 * n), spd = new Float64Array(n);
  const sea = [];
  for (let i = 0; i < n; i++) {
    const la = G.lat[i] * Math.PI / 180, lo = G.lon[i] * Math.PI / 180, cla = Math.cos(la);
    P[3 * i] = cla * Math.cos(lo); P[3 * i + 1] = cla * Math.sin(lo); P[3 * i + 2] = Math.sin(la);
    if (L.elevation[i] > 0) continue;
    const ue = L[ke][i], un = L[kn][i];
    U[3 * i] = -Math.sin(lo) * ue - Math.sin(la) * Math.cos(lo) * un;
    U[3 * i + 1] = Math.cos(lo) * ue - Math.sin(la) * Math.sin(lo) * un;
    U[3 * i + 2] = cla * un;
    spd[i] = Math.hypot(ue, un); sea.push(spd[i]);
  }
  sea.sort((a, b) => a - b);
  const ref = Math.max(sea[Math.floor(0.9 * (sea.length - 1))] || 0, 1e-6);
  const h = Math.sqrt(4 * Math.PI / n), step = Math.min(0.45 * h, STREAM_SEP / 4), minSpd = 0.12 * ref;
  const dot = (p, i) => p[0] * P[3 * i] + p[1] * P[3 * i + 1] + p[2] * P[3 * i + 2];
  const locate = (p, c) => {  // greedy walk to the nearest cell
    for (;;) {
      let best = c, bd = dot(p, c);
      for (const j of nbr[c]) { const d = dot(p, j); if (d > bd) { bd = d; best = j; } }
      if (best === c) return c;
      c = best;
    }
  };
  const vel = (p, c) => {  // inverse-distance mean of the cell's and its neighbours' currents, on p's tangent plane
    let vx = 0, vy = 0, vz = 0, ws = 0;
    for (const j of [c, ...nbr[c]]) {
      const w = 1 / (1 - dot(p, j) + 0.05 * h * h);
      vx += w * U[3 * j]; vy += w * U[3 * j + 1]; vz += w * U[3 * j + 2]; ws += w;
    }
    vx /= ws; vy /= ws; vz /= ws;
    const r = vx * p[0] + vy * p[1] + vz * p[2];
    return [vx - r * p[0], vy - r * p[1], vz - r * p[2]];
  };
  const move = (p, v, s) => {  // p + s * unit(v), back onto the sphere
    const m = Math.hypot(...v) || 1, q = [p[0] + s * v[0] / m, p[1] + s * v[1] / m, p[2] + s * v[2] / m], l = Math.hypot(...q);
    return [q[0] / l, q[1] / l, q[2] / l];
  };
  // occupancy: lat/lon bins of ~STREAM_SEP / 2, holding [line, step, point]
  const bdeg = STREAM_SEP * 90 / Math.PI, rows = Math.ceil(180 / bdeg), occ = new Map();
  const colsOf = (r) => Math.max(1, Math.round(360 * Math.cos((-90 + (r + 0.5) * bdeg) * Math.PI / 180) / bdeg));
  const llOf = (p) => [Math.asin(Math.max(-1, Math.min(1, p[2]))) * 180 / Math.PI, Math.atan2(p[1], p[0]) * 180 / Math.PI];
  const rowOf = (la) => Math.max(0, Math.min(rows - 1, Math.floor((la + 90) / bdeg)));
  const colOf = (lo, r) => { const cols = colsOf(r); return Math.floor((lo + 180) / 360 * cols) % cols; };
  const sep2 = 0.5 * (0.5 * STREAM_SEP) ** 2, selfGap = 3 * STREAM_SEP / step;
  // another line (or this one, far back along it) within ~STREAM_SEP / 2 (seed: within STREAM_SEP)
  const near = (p, line, k, seed = false) => {
    const [la, lo] = llOf(p), r = rowOf(la), w = seed ? 2 : 1, lim = seed ? 4 * sep2 : sep2;
    for (let rr = Math.max(0, r - w); rr <= Math.min(rows - 1, r + w); rr++) {
      const cols = colsOf(rr), c = colOf(lo, rr);
      for (let dc = -w; dc <= w; dc++) {
        const o = occ.get(rr * 100000 + ((c + dc + cols) % cols));
        if (!o) continue;
        for (const [l2, k2, q] of o) {
          if (l2 === line && Math.abs(k2 - k) < selfGap) continue;
          if (1 - (p[0] * q[0] + p[1] * q[1] + p[2] * q[2]) < lim) return true;
        }
      }
    }
    return false;
  };
  const mark = (p, line, k) => {
    const [la, lo] = llOf(p), r = rowOf(la), key = r * 100000 + colOf(lo, r);
    (occ.get(key) || occ.set(key, []).get(key)).push([line, k, p]);
    return key;
  };
  const lines = [], maxSteps = Math.round(Math.PI / step);
  for (let seed = 0; seed < n && lines.length < 900; seed++) {
    if (L.elevation[seed] > 0 || spd[seed] < 2.5 * minSpd) continue;
    const p0 = [P[3 * seed], P[3 * seed + 1], P[3 * seed + 2]], id = lines.length;
    if (near(p0, -1, 0, true)) continue;
    const keys = [mark(p0, id, 0)];
    const half = (sgn) => {
      const pts = [], sp = [];
      let p = p0, c = seed;
      for (let k = 1; k < maxSteps; k++) {
        const v1 = vel(p, c), pm = move(p, v1, 0.5 * step * sgn), cm = locate(pm, c);
        const v2 = vel(pm, cm), q = move(p, v2, step * sgn), cq = locate(q, cm);
        const s = Math.hypot(...v2);
        if (L.elevation[cq] > 0 || s < minSpd || near(q, id, sgn * k)) break;
        pts.push(q); sp.push(s); keys.push(mark(q, id, sgn * k)); p = q; c = cq;
      }
      return [pts, sp];
    };
    const [f, fs] = half(1), [b, bs] = half(-1);
    if (f.length + b.length < 6) {  // too short: forget it
      for (const key of new Set(keys)) occ.set(key, occ.get(key).filter((e) => e[0] !== id));
      continue;
    }
    const pts = [...b.reverse(), p0, ...f], sp = [...bs.reverse(), spd[seed], ...fs];
    lines.push({ pts: pts.map(llOf), sp: sp.map((x) => x / ref) });
  }
  S.V._stream = { key, lines };
  return lines;
}
// lat/lon -> a point on screen, and the chevron (arrowhead) at b coming from a
function chevron(a, b, size, out) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), d = B.clone().sub(A);
  if (d.lengthSq() === 0) return;
  d.normalize().multiplyScalar(size);
  const normal = state.mode === 'globe' ? B.clone().normalize() : new THREE.Vector3(0, 0, 1);
  const side = new THREE.Vector3().crossVectors(normal, d).multiplyScalar(0.6);
  out.push(...b, ...B.clone().sub(d).add(side).toArray(), ...b, ...B.clone().sub(d).sub(side).toArray());
}
function streamOverlay(ke, kn) {
  const globe = state.mode === 'globe', r = 1.004, pts = [], cols = [], heads = [], hc = [];
  const lo = new THREE.Color('#1f6f78'), hi = new THREE.Color('#b4fff0'), c = new THREE.Color();
  for (const ln of streamlines(ke, kn)) {
    const xy = ln.pts.map(([la, lo_]) => llPos(la, lo_, r));
    for (let k = 0; k < xy.length - 1; k++) {
      if (!globe && Math.abs(xy[k][0] - xy[k + 1][0]) > 2) continue;
      c.copy(lo).lerp(hi, Math.min(1, Math.sqrt(ln.sp[k + 1])));
      pts.push(...xy[k], ...xy[k + 1]); cols.push(c.r, c.g, c.b, c.r, c.g, c.b);
      if ((k + 6) % 14 === 0 && k + 1 < xy.length) {
        const n0 = heads.length; chevron(xy[k], xy[k + 1], globe ? 0.012 : 0.016, heads);
        for (let j = n0; j < heads.length; j += 3) hc.push(c.r, c.g, c.b);
      }
    }
  }
  return [lineColored(pts, cols), lineColored(heads, hc)];
}

// The overturning (world meta "overturning", ocean.loop_schematic): sinking
// sites as rings sized by their Sv, the warm surface inflow along the route
// the model sends it (solid), and the deep return flow (dashed: a schematic,
// the model has no deep ocean) to where deep water comes back up.
function labelSprite(text, color) {
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 64;
  const g = cv.getContext('2d');
  g.font = 'bold 36px -apple-system, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 7; g.strokeStyle = '#0b0f17'; g.strokeText(text, 128, 34);
  g.fillStyle = color; g.fillText(text, 128, 34);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthTest: false }));
  sp.scale.set(0.2, 0.05, 1);
  return sp;
}
const MOC_COLORS = { sink: 0xbfe0ff, surface: 0xff8a3a, deep: 0x7f9fff, up: 0x5ff0c8 };
function overturningOverlay(meta, labels) {
  const globe = state.mode === 'globe', r0 = globe ? 1.007 : 1;
  const wraps = (a, b) => !globe && Math.abs(a[0] - b[0]) > 2;
  const ring = (la, lo, rad, out, nseg = 28) => {
    const cl = Math.max(Math.cos(la * Math.PI / 180), 0.15);
    for (let k = 0; k < nseg; k++) {
      const a1 = k / nseg * 2 * Math.PI, a2 = (k + 1) / nseg * 2 * Math.PI;
      const p1 = llPos(la + rad * Math.sin(a1), lo + rad * Math.cos(a1) / cl, r0), p2 = llPos(la + rad * Math.sin(a2), lo + rad * Math.cos(a2) / cl, r0);
      if (!wraps(p1, p2)) out.push(...p1, ...p2);
    }
  };
  const sink = [], surf = [], deep = [], up = [], heads = { surface: [], deep: [] };
  // a path as three parallel lines (WebGL lines are one pixel wide): offsets of +-w deg across it
  const wide = (ll, w) => [-w, 0, w].map((o) => ll.map(([la, lo], k) => {
    const a = ll[Math.max(k - 1, 0)], b = ll[Math.min(k + 1, ll.length - 1)], cl = Math.max(Math.cos(la * Math.PI / 180), 0.15);
    let dn = b[0] - a[0], de = (((b[1] - a[1] + 540) % 360) - 180) * cl;
    const m = Math.hypot(dn, de) || 1;
    return [la - o * de / m, lo + o * dn / m / cl];
  }));
  const arc = ([la1, lo1], [la2, lo2]) => {  // great-circle degrees
    const r = Math.PI / 180, c = Math.sin(la1 * r) * Math.sin(la2 * r) + Math.cos(la1 * r) * Math.cos(la2 * r) * Math.cos((lo2 - lo1) * r);
    return Math.acos(Math.max(-1, Math.min(1, c))) / r;
  };
  for (const p of meta.paths || []) {
    // surface paths run from the site to their source: the water flows the other way
    const raw = p.limb === 'surface' ? [...p.pts].reverse() : p.pts, ll = [raw[0]];
    for (let k = 1; k < raw.length; k++) {  // in steps of <= 0.5 deg, for even dashes
      const [a, b] = [raw[k - 1], raw[k]], m = Math.ceil(arc(a, b) / 0.5), dl = ((b[1] - a[1] + 540) % 360) - 180;
      for (let j = 1; j <= m; j++) ll.push([a[0] + (b[0] - a[0]) * j / m, ((a[1] + dl * j / m + 540) % 360) - 180]);
    }
    // per segment: drawn (dashes of 1.6 deg, gaps of 1 deg on the deep limb) and where the chevrons go (every 9 deg)
    const draw = [], head = [];
    let run = 0, on = true, since = 0;
    for (let k = 0; k < ll.length - 1; k++) {
      const d = arc(ll[k], ll[k + 1]);
      draw.push(p.limb !== 'deep' || on); run += d; since += d;
      if (run > (on ? 1.6 : 1.0)) { on = !on; run = 0; }
      head.push(since > 9 && k > 1); if (since > 9 && k > 1) since = 0;
    }
    const out = p.limb === 'deep' ? deep : surf;
    wide(ll, 0.22).forEach((w, j) => {
      const pts = w.map(([la, lo]) => llPos(la, lo, r0));
      for (let k = 0; k < pts.length - 1; k++) {
        const a = pts[k], b = pts[k + 1];
        if (wraps(a, b)) continue;
        if (draw[k]) out.push(...a, ...b);
        if (head[k] && j === 1) chevron(a, b, globe ? 0.02 : 0.024, heads[p.limb]);
      }
    });
    if (p.limb === 'deep') { const [la, lo] = ll[ll.length - 1]; ring(la, lo, 1.4, up, 16); ring(la, lo, 0.6, up, 10); }
  }
  for (const s of meta.sites || []) {
    if (s.sv < 0.1) continue;
    const rad = 1.3 * Math.sqrt(s.sv) + 0.6;
    ring(s.lat, s.lon, rad, sink); ring(s.lat, s.lon, rad * 0.55, sink, 18);
    const cl = Math.max(Math.cos(s.lat * Math.PI / 180), 0.15), d = rad * 0.38;  // an X: going down
    for (const [a, b] of [[[d, d], [-d, -d]], [[d, -d], [-d, d]]]) {
      const p1 = llPos(s.lat + a[0], s.lon + a[1] / cl, r0), p2 = llPos(s.lat + b[0], s.lon + b[1] / cl, r0);
      if (!wraps(p1, p2)) sink.push(...p1, ...p2);
    }
    if (s.sv >= 0.3) {
      const lab = labelSprite(`${s.sv.toFixed(1)} Sv`, '#cfe4ff');
      lab.position.set(...(globe ? llPos(s.lat + rad + 1.2, s.lon, 1.03) : llPos(s.lat + rad + 2, s.lon, 1, 0.01)));
      if (!globe) lab.scale.set(0.16, 0.04, 1);
      labels.push(lab);
    }
  }
  return { mocSink: lineObj(sink, MOC_COLORS.sink), mocSurf: lineObj(surf, MOC_COLORS.surface),
           mocSurfHeads: lineObj(heads.surface, MOC_COLORS.surface), mocDeep: lineObj(deep, MOC_COLORS.deep),
           mocDeepHeads: lineObj(heads.deep, MOC_COLORS.deep), mocUp: lineObj(up, MOC_COLORS.up, 0.8) };
}
const mocGroup = new THREE.Group();  // the overturning's Sv labels
group.add(mocGroup);

export const EVENT_COLORS = { rift: 0x3bf0ff, subduction: 0x7dff6b, collision: 0xff6b3b, suture: 0xffd23b, absorbed: 0xc58cff, consumed: 0xc58cff,
                       'glacial max': 0x9fd8ff, interglacial: 0xffb36b };  // the last two: time zooms
export const hexColor = (c) => '#' + c.toString(16).padStart(6, '0');
// events this close to the frame on screen are marked on the globe and highlighted in the list
export function eventWindow() { return S.V.tz ? Math.max(2, S.V.run.meta.every * 1.5) : Math.max(10, S.V.run.meta.every * 2.5); }
