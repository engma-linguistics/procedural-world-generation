import * as THREE from 'three';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import * as Relief from '../relief.js';
import { S, proj, state } from './state.js';
import { cellColors } from './layers.js';
import { $, DIAG, RIBBON_MATS, R_EARTH, group, relief3d, seaFloorOn } from './scene.js';
import { buildOverlaysIfChanged } from './overlays.js';
import { renderLegend } from './panel.js';
import { drawProj } from './map2d.js';
// ------------------------------------------------------------ geometry
export function unitVec(lat, lon) {
  const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
  return [Math.cos(la) * Math.cos(lo), Math.sin(la), -Math.cos(la) * Math.sin(lo)];  // north = +Y
}

// Each corner's cells as flat lists, cList[cStart[k] .. cStart[k+1]-1], in cell order; and the cells' unit
// vectors (U, 3 per cell) and the corners' (UC). Typed arrays, once per grid: at L8 (655k cells, 1.3M corners)
// the arrays of arrays these replaced cost ~0.6 s to build and millions of small objects for the GC to trace.
export function prepareGrid(G) {
  const n = G.lat.length, nc = G.corner_lat.length, cells = G.cells;
  const cStart = new Int32Array(nc + 1);
  for (let i = 0; i < n; i++) { const cs = cells[i]; for (let k = 0; k < cs.length; k++) cStart[cs[k] + 1]++; }
  for (let k = 0; k < nc; k++) cStart[k + 1] += cStart[k];
  const cList = new Int32Array(cStart[nc]), fill = cStart.slice(0, nc);
  for (let i = 0; i < n; i++) { const cs = cells[i]; for (let k = 0; k < cs.length; k++) cList[fill[cs[k]]++] = i; }
  const units = (lat, lon, m) => {
    const out = new Float64Array(3 * m);
    for (let i = 0; i < m; i++) {
      const la = lat[i] * Math.PI / 180, lo = lon[i] * Math.PI / 180, cl = Math.cos(la);  // (exactly as unitVec)
      out[3 * i] = cl * Math.cos(lo); out[3 * i + 1] = Math.sin(la); out[3 * i + 2] = -cl * Math.sin(lo);
    }
    return out;
  };
  return { n, nc, cStart, cList, U: units(G.lat, G.lon, n), UC: units(G.corner_lat, G.corner_lon, nc) };
}

// Topology depends only on grid + view mode: which cell/corner each vertex
// belongs to, and its base position. Colours/relief are filled in by paint().
// Each cell has its own vertices (its centre and a copy of each corner, so it
// keeps its own flat colour) and an index of triangles (centre, corner k,
// corner k+1): ~7 vertices per cell instead of 18. Every replay frame rewrites
// and uploads them, so this is what lets a level-7 run play smoothly.
// The flat map's hill shading (mapHillshade) shades each triangle on its own,
// so the satellite layer on the map keeps three vertices per triangle (perTri).
function needsPerTri() { return state.mode !== 'globe' && state.layer === 'satellite'; }
// Built straight into typed arrays (lane 91, the first step of PW-1198): the arrays of pushed numbers this replaced
// cost ~1.5 s at L8 on every build (opening, globe <-> flat map, 3D relief on or off, the map's satellite layer).
export function buildTopology() {
  if (proj.on && S.topo) { S.meshDeferred = true; return; }  // (hidden under the flat map's canvas: see paint)
  S.meshDeferred = false;
  const G = S.V.grid, globe = state.mode === 'globe', perTri = needsPerTri(), n = S.V.n, cells = G.cells;
  const { U, UC } = S.V;  // (the unit vectors of the cells and corners: prepareGrid's)
  // the flat map: each cell's corners unwrapped round its centre's longitude (lonU, in the order of
  // G.cells.flat()), and the cells that cross the dateline, drawn again shifted by +-360 degrees
  // (shifts: bit 1 +360, bit 2 -360) so that both edges of the map show them
  let lonU = null, shifts = null;
  if (!globe) {
    let m = 0; for (let i = 0; i < n; i++) m += cells[i].length;
    lonU = new Float64Array(m); shifts = new Uint8Array(n);
    for (let i = 0, q = 0; i < n; i++) {
      const cs = cells[i], lon0 = G.lon[i];
      let minL = Infinity, maxL = -Infinity;
      for (let k = 0; k < cs.length; k++, q++) {
        let d = G.corner_lon[cs[k]] - lon0; d -= 360 * Math.round(d / 360);
        const l = lonU[q] = lon0 + d;
        if (l < minL) minL = l;
        if (l > maxL) maxL = l;
      }
      shifts[i] = (minL < -180 ? 1 : 0) | (maxL > 180 ? 2 : 0);
    }
  }
  const SHIFTS = [[0], [0, 360], [0, -360], [0, 360, -360]];
  let nv = 0, nt = 0;
  for (let i = 0; i < n; i++) {
    const m = cells[i].length, c = shifts ? SHIFTS[shifts[i]].length : 1;
    nt += c * m; nv += c * (perTri ? 3 * m : 1 + m);
  }
  const vCell = new Int32Array(nv), vCorner = new Int32Array(nv), base = new Float32Array(3 * nv), triCell = new Int32Array(nt);
  const index = perTri ? null : nv > 65535 ? new Uint32Array(3 * nt) : new Uint16Array(3 * nt);
  const triStart = globe ? new Int32Array(n + 1) : null;  // (the globe: cell i's triangles are triStart[i] .. triStart[i+1]-1)
  let v = 0, t = 0;
  // vertex v: cell i, corner k (-1: the centre) at (x, y, z)
  const put = (i, k, x, y, z) => { vCell[v] = i; vCorner[v] = k; base[3 * v] = x; base[3 * v + 1] = y; base[3 * v + 2] = z; v++; };
  // corner k of the cell (its position in G.cells[i]) on the unit sphere, or on the map shifted by s
  const cornerPut = (i, cs, q0, k, s) => {
    const c = cs[k];
    if (globe) put(i, c, UC[3 * c], UC[3 * c + 1], UC[3 * c + 2]);
    else put(i, c, (lonU[q0 + k] + s) / 90, G.corner_lat[c] / 90, 0);
  };
  // the globe (the common case) in one plain loop: a centre and its corners per cell, one triangle per corner
  // (its own counters: v and t live in the closures' context, slower to reach)
  if (globe) for (let i = 0, w = 0, u = 0; i < n; i++) {
    const cs = cells[i], m = cs.length, w0 = w;
    triStart[i] = u; triStart[i + 1] = u + m;
    vCell[w] = i; vCorner[w] = -1; base[3 * w] = U[3 * i]; base[3 * w + 1] = U[3 * i + 1]; base[3 * w + 2] = U[3 * i + 2]; w++;
    for (let k = 0; k < m; k++) {
      const c = cs[k];
      vCell[w] = i; vCorner[w] = c; base[3 * w] = UC[3 * c]; base[3 * w + 1] = UC[3 * c + 1]; base[3 * w + 2] = UC[3 * c + 2]; w++;
      index[3 * u] = w0; index[3 * u + 1] = w0 + 1 + k; index[3 * u + 2] = k + 1 < m ? w0 + 2 + k : w0 + 1;
      triCell[u++] = i;
    }
  }
  else for (let i = 0, q0 = 0; i < n; q0 += cells[i].length, i++) {
    const cs = cells[i], m = cs.length;
    for (const s of shifts ? SHIFTS[shifts[i]] : SHIFTS[0]) {
      const cx = globe ? U[3 * i] : (G.lon[i] + s) / 90, cy = globe ? U[3 * i + 1] : G.lat[i] / 90, cz = globe ? U[3 * i + 2] : 0;
      if (triStart) { triStart[i] = t; triStart[i + 1] = t + m; }
      const v0 = v;
      if (!perTri) put(i, -1, cx, cy, cz);
      for (let k = 0; k < m; k++) {
        const k2 = (k + 1) % m;
        if (perTri) { put(i, -1, cx, cy, cz); cornerPut(i, cs, q0, k, s); cornerPut(i, cs, q0, k2, s); }
        else { cornerPut(i, cs, q0, k, s); index[3 * t] = v0; index[3 * t + 1] = v0 + 1 + k; index[3 * t + 2] = v0 + 1 + k2; }
        triCell[t++] = i;
      }
    }
  }
  // each vertex's source in paint's per-centre-then-per-corner arrays: its cell, or n + its corner
  // (and each corner's cells as flat lists, cList[cStart[k] .. cStart[k+1]-1]: prepareGrid's)
  const { cStart, cList } = S.V, vSrc = new Int32Array(nv);
  for (let j = 0; j < nv; j++) vSrc[j] = vCorner[j] < 0 ? vCell[j] : n + vCorner[j];
  S.topo = { vCell, vCorner, vSrc, cStart, cList, base, triCell, triStart, globe, perTri, posKey: null };
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(base.length), 3));
  // colours as normalized 16-bit (half the upload of floats, no banding in the dark sea ramps)
  geo.setAttribute('color', new THREE.BufferAttribute(new Uint16Array(base.length), 3, true));
  if (!perTri) geo.setIndex(new THREE.BufferAttribute(index, 1));
  if (S.mesh) { group.remove(S.mesh); S.mesh.geometry.dispose(); S.mesh.userData.mats.forEach((m) => m.dispose()); }
  // flatShading: each triangle lit by its own face normal, worked out on the GPU (the
  // same normals the old three-vertices-per-triangle mesh had, with none to compute or upload)
  // the globe's 3D relief: smooth normals (relief.sphereNormals), from each cell's corners in order and
  // the unit vectors of the centres and corners, while the view is still; flat shading during a replay
  // (the normals cost ~20 ms a keyframe at L7: the replay keeps its speed)
  const smoothRelief = globe && relief3d() && !perTri;
  if (smoothRelief) {
    geo.setAttribute('normal', new THREE.BufferAttribute(new Int8Array(base.length), 3, true));  // (a quarter of floats' upload)
    if (!S.V.fan) {
      const fanStart = new Int32Array(n + 1);
      for (let i = 0; i < n; i++) fanStart[i + 1] = fanStart[i] + cells[i].length;
      const fanList = new Int32Array(fanStart[n]);
      for (let i = 0; i < n; i++) fanList.set(cells[i], fanStart[i]);
      const UF = new Float32Array(3 * (n + S.V.nc));  // (the cells' unit vectors, then the corners')
      UF.set(U); UF.set(UC, 3 * n);
      S.V.fan = { fanStart, fanList, U: UF };
    }
  }
  S.topo.smoothRelief = smoothRelief;
  // (the flat map in 3D relief is lit too)
  const mat = globe || relief3d() ? new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: !smoothRelief, side: globe ? THREE.FrontSide : THREE.DoubleSide })
                                  : new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide });
  S.mesh = new THREE.Mesh(geo, mat);
  S.mesh.userData.mats = [mat];
  if (smoothRelief) S.mesh.userData.mats.push(S.mesh.userData.flatMat = new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true }));
  group.add(S.mesh);
  if (S.seaShell) { group.remove(S.seaShell); S.seaShell.geometry.dispose(); S.seaShell = null; }
  if (relief3d()) { S.seaShell = Relief.seaSurface(globe); group.add(S.seaShell); }
  S.topo.relief = relief3d();
}

// m -> globe radii: the Sliders' exaggeration, or the 3D relief's
export function reliefScale() { return +$(relief3d() ? 'reliefEx' : 'relief').value / R_EARTH; }
// cell i's radius: paint's (V.R, this frame's), else from its elevation
function cellRadius(i) { return S.V.R ? S.V.R[i] : 1 + reliefScale() * Math.max(S.V.layers.elevation[i], 0); }

export function paint() {
  DIAG.n.paints++;
  // The flat map in another projection than the live one (proj.on, the default Equal Earth): its canvas
  // (drawProj) covers the live map, so the mesh is neither rebuilt nor repainted until it shows again
  // (S.meshDeferred; map2d.js syncProj). At L8 that work was 1.5-2.5 s a layer switch on the flat map.
  if (proj.on && S.topo) {
    S.lastColors = cellColors(state.layer); S.meshDeferred = true;
    buildOverlaysIfChanged();  // (the canvas draws the live map's overlays, PW-860)
    renderLegend(); drawProj();
    return;
  }
  // (the map's satellite layer: per-triangle shading; the 3D relief: lit map, sea surface)
  if (S.meshDeferred || S.topo.perTri !== needsPerTri() || S.topo.relief !== relief3d()) buildTopology();
  const L = S.V.layers, globe = S.topo.globe, r3d = relief3d(), sea = seaFloorOn();
  const col = S.lastColors = cellColors(state.layer);
  const smooth = $('smooth').checked, ex = reliefScale();
  const shadeMap = !globe && !r3d && state.layer === 'satellite', mapZ = 2 / Math.PI;  // relief: sphere radii -> map units (1 = 90 deg)
  // The positions are written only when they change (lane 91: at L8 rewriting and uploading 4.6 M of them
  // took half of a layer switch). They follow the relief: the heights (this frame's layers: elevation, and
  // ice, lakes and the sea floor in 3D relief), the exaggeration and the view; the plain flat map has none,
  // its positions are written once. The map's hill shading flattens them after use: written every time.
  const posKey = shadeMap ? null : globe ? `globe|${r3d}|${sea}|${ex}` : r3d ? `map3d|${sea}|${ex}` : 'flat';
  const writePos = posKey === null || S.topo.posKey !== posKey || (posKey !== 'flat' && S.topo.posLayers !== L);
  const n = S.V.n, nc = S.V.nc, elev = L.elevation;
  const { vCell, vSrc, cStart, cList, base } = S.topo, nv = vCell.length;
  // R: the relief radius of each cell centre (0..n-1), then of each corner (n..n+nc-1), the
  // mean of the cells round it; vSrc says which one each vertex takes (as for the smooth colours).
  // The 3D relief's heights: the surface (ice, lakes) and the sea floor (relief.js).
  let R = null;
  if (writePos) {
    if (r3d) R = S.topo.R = Relief.radii(S.topo.H = Relief.surfaceHeights(S.V, sea, S.topo.H), cStart, cList, n, ex, sea, S.topo.R);
    else {
      R = new Float32Array(n + nc);
      for (let i = 0; i < n; i++) R[i] = 1 + ex * Math.max(elev[i], 0);
      for (let k = 0; k < nc; k++) {
        const a = cStart[k], b = cStart[k + 1]; let e = 0;
        for (let q = a; q < b; q++) e += R[cList[q]] - 1;
        R[n + k] = 1 + e / (b - a);
      }
    }
  }
  const cornerCol = smooth ? new Float32Array(3 * (n + nc)) : null;
  if (smooth) for (let k = 0; k < nc; k++) {
    const a = cStart[k], b = cStart[k + 1];
    for (let q = a; q < b; q++) for (let c = 0; c < 3; c++) cornerCol[3 * (n + k) + c] += col[3 * cList[q] + c] / (b - a);
  }
  if (writePos) S.V.R = R;  // (the overlays sit on it; unchanged positions keep theirs, the plain flat map has none)
  else if (posKey === 'flat') S.V.R = null;
  if (S.seaShell) S.seaShell.visible = sea;
  const pos = S.mesh.geometry.attributes.position.array, rgb = S.mesh.geometry.attributes.color.array;
  let maxR = 1, minR = Infinity;
  if (writePos) for (let v = 0; v < nv; v++) {
    const rr = R[vSrc[v]], r = globe ? rr : 1, v3 = 3 * v;
    if (rr > maxR) maxR = rr;
    if (rr < minR) minR = rr;
    pos[v3] = base[v3] * r; pos[v3 + 1] = base[v3 + 1] * r; pos[v3 + 2] = shadeMap || r3d && !globe ? mapZ * (rr - 1) : base[v3 + 2] * r;
  }
  // (16-bit colours: each cell's, or corner's, converted once, then copied to its vertices)
  const u16 = (a) => { const o = new Uint16Array(a.length); for (let j = 0; j < a.length; j++) o[j] = a[j] * 65535 + 0.5; return o; };
  if (smooth) {  // corners take the mean colour of the cells round them, centres their own
    cornerCol.set(col);
    const cu = u16(cornerCol);
    for (let v = 0; v < nv; v++) { const j = 3 * vSrc[v], v3 = 3 * v; rgb[v3] = cu[j]; rgb[v3 + 1] = cu[j + 1]; rgb[v3 + 2] = cu[j + 2]; }
  } else {
    const cu = u16(col);
    for (let v = 0; v < nv; v++) { const j = 3 * vCell[v], v3 = 3 * v; rgb[v3] = cu[j]; rgb[v3 + 1] = cu[j + 1]; rgb[v3 + 2] = cu[j + 2]; }
  }
  if (writePos) S.mesh.geometry.attributes.position.needsUpdate = true;
  // (smooth normals while still; flat shading while a replay plays)
  if (S.topo.smoothRelief) S.mesh.material = S.mesh.userData.mats[state.playing ? 1 : 0];
  if (writePos) S.topo.normalsOk = false;  // (the normals of these positions: not yet, while a replay plays)
  if (S.topo.smoothRelief && !state.playing && !S.topo.normalsOk) {
    const F = S.V.fan;
    Relief.sphereNormals(R || S.topo.R, F.U, n, F.fanStart, F.fanList, cStart, cList, vSrc, S.mesh.geometry.attributes.normal.array);
    S.mesh.geometry.attributes.normal.needsUpdate = true;
    S.topo.normalsOk = true;
  }
  S.mesh.geometry.attributes.color.needsUpdate = true;
  if (shadeMap) mapHillshade(pos, rgb);
  if (writePos) {
    // the bounding sphere (for picking and culling), without a pass over every vertex:
    // the globe is centred, of radius the highest point; the map is 4 x 2 (plus the overlap)
    S.topo.maxR = maxR;  // (the highest point: fitClip)
    S.topo.minR = minR;  // (the lowest: the globe pick's shell)
    if (globe) S.mesh.geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), maxR);
    else S.mesh.geometry.computeBoundingSphere();
    S.topo.posKey = posKey; S.topo.posLayers = L;
  }
  buildOverlaysIfChanged();  // (only when something they show moved, PW-1045)
  renderLegend();
  if (proj.on) drawProj();
}

// The flat map's hill shading (the satellite view; the globe has its light):
// the relief as height, lit from the north-west 40 deg up, as the zoom's
// hillshade, then flattened again so the overlays stay on top.
const MAP_LIGHT = new THREE.Vector3(-Math.SQRT1_2, Math.SQRT1_2, Math.tan(40 * Math.PI / 180)).normalize();
function mapHillshade(pos, rgb) {
  S.mesh.geometry.computeVertexNormals();
  const nr = S.mesh.geometry.attributes.normal.array, flat = MAP_LIGHT.z;
  for (let v = 0; v < pos.length / 3; v++) {
    const sh = Math.max(0, nr[3 * v] * MAP_LIGHT.x + nr[3 * v + 1] * MAP_LIGHT.y + nr[3 * v + 2] * MAP_LIGHT.z);
    const f = 0.4 + 0.6 * sh / flat;
    rgb[3 * v] *= f; rgb[3 * v + 1] *= f; rgb[3 * v + 2] *= f;
    pos[3 * v + 2] = 0;
  }
}

// cell centre position (with relief) for overlays
// the k-th smallest of a[lo..] (as a sorted a[k] would be), reordering a in place (Hoare's quickselect)
export function select(a, k, lo = 0) {
  let hi = a.length - 1;
  while (hi > lo) {
    const p = a[(lo + hi) >> 1];
    let i = lo, j = hi;
    while (i <= j) {
      while (a[i] < p) i++;
      while (a[j] > p) j--;
      if (i <= j) { const t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
    }
    if (k <= j) hi = j; else if (k >= i) lo = i; else break;
  }
  return a[k];
}

// cellPos for every cell at once, as a Float32Array(3n) (the rivers, every replay frame)
export function cellPositions(lift) {
  const G = S.V.grid, n = S.V.n, out = new Float32Array(3 * n);
  if (state.mode !== 'globe') {
    const R = relief3d() && S.V.R, mz = 2 / Math.PI;  // (the 3D relief's map: on its heights)
    for (let i = 0; i < n; i++) { out[3 * i] = G.lon[i] / 90; out[3 * i + 1] = G.lat[i] / 90; out[3 * i + 2] = 0.002 + (R ? mz * (R[i] - 1) * lift : 0); }
    return out;
  }
  const ex = reliefScale(), e = S.V.layers.elevation, u = cellUnits(), R = S.V.R;
  for (let i = 0; i < n; i++) {
    const r = (R ? Math.max(R[i], 1) : 1 + ex * Math.max(e[i], 0)) * lift;
    out[3 * i] = u[3 * i] * r; out[3 * i + 1] = u[3 * i + 1] * r; out[3 * i + 2] = u[3 * i + 2] * r;
  }
  return out;
}
export function cellPos(i, lift = 1.002) {
  const G = S.V.grid;
  if (state.mode === 'globe') return unitVec(G.lat[i], G.lon[i]).map((x) => x * Math.max(cellRadius(i), 1) * lift);
  return [G.lon[i] / 90, G.lat[i] / 90, 0.002 + (relief3d() && S.V.R ? 2 / Math.PI * (S.V.R[i] - 1) : 0)];
}
// the cells' unit vectors (three.js axes), once per grid
function cellUnits() {
  if (!S.V.unit) S.V.unit = Float32Array.from(S.V.U);  // (prepareGrid's, as floats)
  return S.V.unit;
}
// the cell nearest (lat, lon): the cells hashed by their unit vectors into cubes two
// cell spacings wide, so the nearest is in the point's cube or one next to it
function nearestCell(lat, lon) { return nearestCellU(unitVec(lat, lon)); }
export function nearestCellU(p) {
  const u = cellUnits(), n = S.V.n;
  if (!S.V.cellHash) {
    const h = 2 * Math.sqrt(4 * Math.PI / n), K = Math.ceil(2 / h) + 1;
    const key = new Int32Array(n), ord = new Int32Array(n), start = new Map();
    for (let i = 0; i < n; i++) {
      key[i] = Math.floor((u[3 * i] + 1) / h) + K * (Math.floor((u[3 * i + 1] + 1) / h) + K * Math.floor((u[3 * i + 2] + 1) / h));
      ord[i] = i;
    }
    ord.sort((a, b) => key[a] - key[b]);
    for (let j = 0; j < n; j++) { const k = key[ord[j]]; if (!start.has(k)) start.set(k, [j, j]); start.get(k)[1] = j + 1; }
    S.V.cellHash = { h, K, ord, start };
  }
  const { h, K, ord, start } = S.V.cellHash;
  const ix = Math.floor((p[0] + 1) / h), iy = Math.floor((p[1] + 1) / h), iz = Math.floor((p[2] + 1) / h);
  let best = 0, bd = -2;
  for (let dz = -1; dz <= 1; dz++) for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
    const se = start.get(ix + dx + K * (iy + dy + K * (iz + dz)));
    if (!se) continue;
    for (let j = se[0]; j < se[1]; j++) {
      const i = ord[j], d = u[3 * i] * p[0] + u[3 * i + 1] * p[1] + u[3 * i + 2] * p[2];
      if (d > bd) { bd = d; best = i; }
    }
  }
  return best;
}
// the flat map's relief under cell i (the 3D relief's: map units above the sea; else 0)
function mapRelief(i) { return relief3d() && S.V.R ? 2 / Math.PI * Math.max(S.V.R[i] - 1, 0) : 0; }
// an overlay's point at (lat, lon), on the drawn surface (the relief, PW-372): on the globe
// r times the radius of the nearest cell's surface (as cellPos: at least the sea's), on the
// map just above its relief. The fixed radii the overlays used floated over the lowlands and
// sank under high ground and ice at the 3D relief's exaggeration.
export function llPos(lat, lon, r, mapLift = 0.003) {
  const flat = !relief3d() && !(reliefScale() > 0);
  if (state.mode === 'globe') {
    const R = flat ? 1 : Math.max(cellRadius(nearestCell(lat, lon)), 1);
    return unitVec(lat, lon).map((x) => x * R * r);
  }
  return [lon / 90, lat / 90, mapLift + (relief3d() && S.V.R ? mapRelief(nearestCell(lat, lon)) : 0)];
}
// llPos for a point whose cell and unit vector are known: {lat, lon, cell, u} from llPoint (PW-679: the
// peoples tracks ask for the same thousands of points every frame, and the grid doesn't change)
export function llPoint(lat, lon) { return { lat, lon, cell: nearestCell(lat, lon), u: unitVec(lat, lon) }; }
export function llPosPt(q, r, mode, mapLift = 0.003) {  // mode: llMode()
  if (state.mode === 'globe') {
    const k = (mode.flat ? 1 : Math.max(cellRadius(q.cell), 1)) * r;
    return [q.u[0] * k, q.u[1] * k, q.u[2] * k];
  }
  return [q.lon / 90, q.lat / 90, mapLift + (mode.r3d && S.V.R ? mapRelief(q.cell) : 0)];
}
export function llMode() { const r3d = relief3d(); return { r3d, flat: !r3d && !(reliefScale() > 0) }; }

// The rivers are ribbons of triangles a fixed number of screen pixels
// wide (three's fat lines, LineSegments2): they read better than 1-pixel lines and are drawn
// the same on every GPU. Materials are shared by colour, opacity and width and never
// disposed: overlays are rebuilt every replay frame, and disposing the last material of a
// kind makes three.js throw away its shader program and link it again on the next frame.
// Their resolution (CSS pixels) follows the window (resize).
function ribbonMat(color, opacity, width, vertexColors = false) {
  const key = `${color}|${opacity}|${width}|${vertexColors}`;
  if (!RIBBON_MATS.has(key)) {
    const m = new LineMaterial({ color, linewidth: width, transparent: opacity < 1, opacity, vertexColors });
    m.resolution.set(innerWidth, innerHeight);
    m.userData.shared = true; RIBBON_MATS.set(key, m);
  }
  return RIBBON_MATS.get(key);
}
// pts: segment end points (x, y, z, x, y, z per segment); cols: a colour (r, g, b) per end point
export function ribbonObj(pts, color, opacity = 1, width = 1.5, cols = null) {
  const g = new LineSegmentsGeometry();
  if (pts.length) { g.setPositions(pts); if (cols) g.setColors(cols); }
  const o = new LineSegments2(g, ribbonMat(cols ? 0xffffff : color, opacity, width, !!cols));
  o.raycast = () => {};  // (hovering picks the ground)
  return o;
}
// (shared materials and textures, e.g. the cached label sprites and cloud pictures, stay; a Sprite's geometry is three's
// own, one for every sprite, so it stays too: PW-1045)
export function disposeObj(o) {
  if (!o.isSprite) o.geometry?.dispose();
  if (o.material.map && !o.material.map.userData.shared) o.material.map.dispose();
  if (!o.material.userData.shared) o.material.dispose();
}
// The other overlays stay 1-pixel GL lines (the plate outlines alone are ~1 M segments; fitClip
// keeps them off the ground too); their materials are shared the same way.
const LINE_MATS = new Map();
function lineMat(color, opacity) {
  const key = `${color}|${opacity}`;
  if (!LINE_MATS.has(key)) {
    const m = new THREE.LineBasicMaterial({ color, transparent: opacity < 1, opacity });
    m.userData.shared = true; LINE_MATS.set(key, m);
  }
  return LINE_MATS.get(key);
}
export function lineObj(pts, color, opacity = 1) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  return new THREE.LineSegments(g, lineMat(color, opacity));
}

// planet (x,y,z) vector -> three.js axes
export const toThree = (v) => [v[0], v[2], -v[1]];

export function plateVelocity(i) {
  // returns planet-frame tangent velocity (rad/Myr) of cell i, or null
  if (S.V.kind === 'run') {
    const w = S.V.omega[S.V.layers.plate[i]]; if (!w) return null;
    const la = S.V.grid.lat[i] * Math.PI / 180, lo = S.V.grid.lon[i] * Math.PI / 180;
    const p = [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)];
    return [w[1] * p[2] - w[2] * p[1], w[2] * p[0] - w[0] * p[2], w[0] * p[1] - w[1] * p[0]];
  }
  const v = S.V.layers._plate_velocity; return v ? v[i] : null;
}
