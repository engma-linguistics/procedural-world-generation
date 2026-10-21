// The viewer's 2D map mode (PW-477): the formulas of planet/projection.py ported to JS (same oblique
// aspects, same unit-sphere maps; tests/test_projection_js.py checks them against the Python), and
// the drawing of a layer's per-cell colours into a projection. Pure functions, no DOM except
// drawMap/pngBlob, which take a canvas. Why client-side: the viewer already holds the current
// layer's colours for every cell (cellColors), so a map is a nearest-cell lookup per pixel with no
// round trip, and changing layer, season or replay frame redraws at once.
//
// World vectors: x through 0N 0E, y 90E, z north (as projection.py). The viewer's three.js axes
// differ (x, z, -y); nearestCell takes those, see toThree.

export const NAMES = ['equirect', 'equal-earth', 'mollweide', 'laea', 'aeqd', 'ortho', 'stereo'];
export const LABELS = { equirect: 'Equirectangular', 'equal-earth': 'Equal Earth', mollweide: 'Mollweide', laea: 'Lambert azimuthal equal-area',
  aeqd: 'Azimuthal equidistant', ortho: 'Orthographic (globe)', stereo: 'Stereographic' };
const WORLD = new Set(['equirect', 'equal-earth', 'mollweide']);
export const R_KM = 6371.0;
const STEREO_MAX = (160 * Math.PI) / 180, STEREO_DEFAULT = (120 * Math.PI) / 180;
const A1 = 1.340264, A2 = -0.081106, A3 = 0.000893, A4 = 0.003796, EE_M = Math.sqrt(3) / 2;
const eeD = (t) => { const t2 = t * t; return A1 + 3 * A2 * t2 + 7 * A3 * t2 ** 3 + 9 * A4 * t2 ** 4; };
const eeY = (t) => { const t2 = t * t; return t * (A1 + A2 * t2 + A3 * t2 ** 3 + A4 * t2 ** 4); };
const clip = (v, a, b) => Math.min(b, Math.max(a, v));
const rad = Math.PI / 180;

function mollTheta(lat) {
  if (Math.abs(lat) > 89.99999 * rad) return Math.sign(lat) * Math.PI / 2;
  const s = Math.PI * Math.sin(lat);
  let t = lat;
  for (let k = 0; k < 40; k++) t -= (2 * t + Math.sin(2 * t) - s) / Math.max(2 + 2 * Math.cos(2 * t), 1e-9);
  return clip(t, -Math.PI / 2, Math.PI / 2);
}

export const toThree = (v) => [v[0], v[2], -v[1]];

export function makeProjection(name, latDeg = 0, lonDeg = 0) {
  if (!NAMES.includes(name)) throw new Error(`unknown projection ${name}`);
  const la = latDeg * rad, lo = lonDeg * rad;
  const c = [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)];
  const e = [-Math.sin(lo), Math.cos(lo), 0];
  const n = [c[1] * e[2] - c[2] * e[1], c[2] * e[0] - c[0] * e[2], c[0] * e[1] - c[1] * e[0]];
  const world = WORLD.has(name);

  // world unit vector -> [x, y] on the unit sphere's map, or null where not shown
  function forward(p, out = [0, 0]) {
    const qx = c[0] * p[0] + c[1] * p[1] + c[2] * p[2], qy = e[0] * p[0] + e[1] * p[1] + e[2] * p[2], qz = n[0] * p[0] + n[1] * p[1] + n[2] * p[2];
    if (world) {
      const lat = Math.asin(clip(qz, -1, 1)), lon = Math.atan2(qy, qx);
      if (name === 'equirect') { out[0] = lon; out[1] = lat; return out; }
      if (name === 'equal-earth') {
        const th = Math.asin(EE_M * Math.sin(lat));
        out[0] = 2 * Math.sqrt(3) * lon * Math.cos(th) / (3 * eeD(th)); out[1] = eeY(th); return out;
      }
      const th = mollTheta(lat);
      out[0] = 2 * Math.SQRT2 / Math.PI * lon * Math.cos(th); out[1] = Math.SQRT2 * Math.sin(th); return out;
    }
    const cosc = clip(qx, -1, 1), cc = Math.acos(cosc);
    let k;
    if (name === 'laea') { if (cosc < -1 + 1e-12) return null; k = Math.sqrt(2 / (1 + cosc)); }
    else if (name === 'aeqd') { if (cc > Math.PI - 1e-9) return null; k = cc > 1e-12 ? cc / Math.sin(cc) : 1; }
    else if (name === 'ortho') { if (cosc < 0) return null; k = 1; }
    else { if (cc > STEREO_MAX) return null; k = 2 / (1 + cosc); }
    out[0] = k * qy; out[1] = k * qz; return out;
  }

  // map (x, y) -> world unit vector written to `out`; false where there is no point
  function unproject(x, y, out) {
    let qx, qy, qz;
    if (world) {
      let lat, lon;
      if (name === 'equirect') { lat = y; lon = x; if (Math.abs(lat) > Math.PI / 2 || Math.abs(lon) > Math.PI) return false; }
      else if (name === 'equal-earth') {
        if (Math.abs(y) > eeY(Math.PI / 3) * (1 + 1e-12)) return false;
        let th = clip(y / 1.3, -Math.PI / 3, Math.PI / 3);
        for (let k = 0; k < 30; k++) th -= (eeY(th) - y) / eeD(th);
        th = clip(th, -Math.PI / 3, Math.PI / 3);
        lat = Math.asin(clip(Math.sin(th) / EE_M, -1, 1));
        lon = 3 * x * eeD(th) / (2 * Math.sqrt(3) * Math.cos(th));
        if (Math.abs(lon) > Math.PI * (1 + 1e-12)) return false;
      } else {
        if (Math.abs(y) > Math.SQRT2 * (1 + 1e-12)) return false;
        const th = Math.asin(clip(y / Math.SQRT2, -1, 1));
        lat = Math.asin(clip((2 * th + Math.sin(2 * th)) / Math.PI, -1, 1));
        const ct = Math.cos(th);
        if (ct < 1e-12) lon = 0; else lon = Math.PI * x / (2 * Math.SQRT2 * ct);
        if (Math.abs(lon) > Math.PI * (1 + 1e-12)) return false;
      }
      const cl = Math.cos(lat);
      qx = cl * Math.cos(lon); qy = cl * Math.sin(lon); qz = Math.sin(lat);
    } else {
      const rho = Math.hypot(x, y);
      let cc;
      if (name === 'laea') { if (rho > 2) return false; cc = 2 * Math.asin(clip(rho / 2, 0, 1)); }
      else if (name === 'aeqd') { if (rho > Math.PI) return false; cc = rho; }
      else if (name === 'ortho') { if (rho > 1) return false; cc = Math.asin(clip(rho, 0, 1)); }
      else { cc = 2 * Math.atan(rho / 2); if (cc > STEREO_MAX) return false; }
      const ux = rho > 1e-15 ? x / rho : 0, uy = rho > 1e-15 ? y / rho : 0, s = Math.sin(cc);
      qx = Math.cos(cc); qy = s * ux; qz = s * uy;
    }
    out[0] = c[0] * qx + e[0] * qy + n[0] * qz;
    out[1] = c[1] * qx + e[1] * qy + n[1] * qz;
    out[2] = c[2] * qx + e[2] * qy + n[2] * qz;
    return true;
  }

  // half width / height (unit sphere) of the whole map
  function fullExtent() {
    if (name === 'equirect') return [Math.PI, Math.PI / 2];
    if (name === 'equal-earth') return [2 * Math.sqrt(3) * Math.PI / (3 * eeD(0)), eeY(Math.PI / 3)];
    if (name === 'mollweide') return [2 * Math.SQRT2, Math.SQRT2];
    const r = { laea: 2, aeqd: Math.PI, ortho: 1, stereo: 2 * Math.tan(STEREO_DEFAULT / 2) }[name];
    return [r, r];
  }
  return { name, lat0: latDeg, lon0: lonDeg, forward, unproject, fullExtent };
}

// The pixel raster of a map `width` px wide (square pixels, the map's origin in the middle);
// extentKm: [w, h] of the map plane, or null for the whole projection.
export function pixelGrid(proj, width, extentKm = null) {
  let [hw, hh] = proj.fullExtent();
  if (extentKm) { hw = extentKm[0] / 2 / R_KM; hh = extentKm[1] / 2 / R_KM; }
  width = Math.max(1, Math.round(width));
  const step = 2 * hw / width, height = Math.max(1, Math.round(2 * hh / step));
  return { width, height, step, hw, hh: height * step / 2 };
}

// For each pixel the nearest cell, or -1 where the projection shows nothing.
// nearest(x, y, z) takes a world unit vector.
export function cellMap(proj, g, nearest) {
  const out = new Int32Array(g.width * g.height), p = [0, 0, 0];
  for (let j = 0; j < g.height; j++) {
    const y = g.hh - (j + 0.5) * g.step;
    for (let i = 0; i < g.width; i++) {
      out[j * g.width + i] = proj.unproject(-g.hw + (i + 0.5) * g.step, y, p) ? nearest(p[0], p[1], p[2]) : -1;
    }
  }
  return out;
}

// linear 0..1 -> sRGB byte
const SRGB = new Uint8Array(4097);
for (let k = 0; k <= 4096; k++) { const v = k / 4096; SRGB[k] = Math.round(255 * (v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055)); }
export const srgbByte = (v) => SRGB[Math.round(clip(v, 0, 1) * 4096)];

// colours: Float32Array(3n) of linear rgb per cell (cellColors); bg: [r, g, b] bytes for empty pixels
export function fillImage(img, cells, colors, bg = [11, 16, 24]) {
  const d = img.data;
  for (let k = 0; k < cells.length; k++) {
    const c = cells[k], o = 4 * k;
    if (c < 0) { d[o] = bg[0]; d[o + 1] = bg[1]; d[o + 2] = bg[2]; }
    else { d[o] = srgbByte(colors[3 * c]); d[o + 1] = srgbByte(colors[3 * c + 1]); d[o + 2] = srgbByte(colors[3 * c + 2]); }
    d[o + 3] = 255;
  }
}

// graticule lines (lat, lon every `stepDeg`) as polylines in pixel coordinates; a line is cut
// where the map has no point or the projection jumps (the seam, an azimuthal edge)
export function graticule(proj, g, stepDeg) {
  const lines = [], p = [0, 0, 0], q = [0, 0];
  const px = (x, y) => [(x + g.hw) / g.step, (g.hh - y) / g.step];
  const trace = (pts) => {
    let cur = [], last = null;
    for (const [la, lo] of pts) {
      const cl = Math.cos(la * rad);
      p[0] = cl * Math.cos(lo * rad); p[1] = cl * Math.sin(lo * rad); p[2] = Math.sin(la * rad);
      const r = proj.forward(p, q);
      const ok = r && Math.abs(q[0]) <= g.hw * 1.5 && Math.abs(q[1]) <= g.hh * 1.5;
      if (!ok || (last && Math.hypot(q[0] - last[0], q[1] - last[1]) > 25 * g.step)) { if (cur.length > 1) lines.push(cur); cur = []; last = null; if (!ok) continue; }
      cur.push(px(q[0], q[1])); last = [q[0], q[1]];
    }
    if (cur.length > 1) lines.push(cur);
  };
  const dens = Math.max(0.5, Math.min(2, stepDeg / 10));
  for (let la = -90 + stepDeg; la < 90; la += stepDeg) {
    const pts = []; for (let lo = -180; lo <= 180; lo += dens) pts.push([la, lo]); trace(pts);
  }
  for (let lo = -180; lo < 180; lo += stepDeg) {
    const pts = []; for (let la = -90; la <= 90; la += dens) pts.push([la, lo]); trace(pts);
  }
  return lines;
}

// A sensible graticule spacing (degrees) for a map of this extent (km across, null: the whole projection).
export function graticuleStep(extentKm) {
  const deg = extentKm ? extentKm[0] / (R_KM * rad) : 360;
  return deg > 200 ? 30 : deg > 80 ? 15 : deg > 30 ? 10 : deg > 12 ? 5 : deg > 5 ? 2 : deg > 2 ? 1 : 0.5;
}

// Draws the map of `colors` into `canvas` at `width` px. Returns the grid. `cache` holds the pixel
// -> cell map between calls ({key, cells}); key says what it was made for.
export function drawMap(canvas, proj, width, extentKm, colors, nearest, opt = {}) {
  const g = pixelGrid(proj, width, extentKm);
  canvas.width = g.width; canvas.height = g.height;
  const key = `${proj.name}|${proj.lat0}|${proj.lon0}|${g.width}|${g.height}|${extentKm || ''}|${opt.gridId || ''}`;
  const cache = opt.cache || {};
  if (cache.key !== key) { cache.cells = cellMap(proj, g, nearest); cache.key = key; }
  const ctx = canvas.getContext('2d'), img = ctx.createImageData(g.width, g.height);
  fillImage(img, cache.cells, colors, opt.bg);
  ctx.putImageData(img, 0, 0);
  if (opt.graticule) {
    ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = Math.max(1, g.width / 1500);
    ctx.beginPath();
    for (const line of graticule(proj, g, graticuleStep(extentKm))) { ctx.moveTo(line[0][0], line[0][1]); for (let k = 1; k < line.length; k++) ctx.lineTo(line[k][0], line[k][1]); }
    ctx.stroke();
  }
  if (opt.features) drawFeatures(ctx, proj, g, opt.features);
  if (opt.marker) {  // a small cross at the centre
    const s = Math.max(5, g.width / 150);
    ctx.strokeStyle = '#fff'; ctx.lineWidth = Math.max(1.5, g.width / 800);
    ctx.beginPath(); ctx.moveTo(g.width / 2 - s, g.height / 2); ctx.lineTo(g.width / 2 + s, g.height / 2); ctx.moveTo(g.width / 2, g.height / 2 - s); ctx.lineTo(g.width / 2, g.height / 2 + s); ctx.stroke();
  }
  return g;
}

// Lines and markers over the map (PW-505: the human-use layers). feats: {lines: [{pts: [[lat, lon], ...], color, width}],
// marks: [{lat, lon, shape: 'diamond' | 'hourglass', color, size}]}; width and size in px of a map 1000 px wide
// (scaled with the map). Whatever the projection shows nothing of, or jumps over (the seam), is left out.
export function drawFeatures(ctx, proj, g, feats) {
  const k = g.width / 1000, p = [0, 0, 0], q = [0, 0];
  const px = (la, lo) => {
    const cl = Math.cos(la * rad);
    p[0] = cl * Math.cos(lo * rad); p[1] = cl * Math.sin(lo * rad); p[2] = Math.sin(la * rad);
    return proj.forward(p, q) ? [(q[0] + g.hw) / g.step, (g.hh - q[1]) / g.step] : null;
  };
  const lim = g.width / 4;  // a segment longer than this on the map crosses the seam
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const halo of [true, false]) {
    for (const l of feats.lines || []) {
      const a = px(...l.pts[0]), b = px(...l.pts[1]);
      if (!a || !b || Math.hypot(a[0] - b[0], a[1] - b[1]) > lim) continue;
      ctx.strokeStyle = halo ? 'rgba(0,0,0,0.55)' : l.color; ctx.lineWidth = Math.max(1, (l.width + (halo ? 1.6 : 0)) * k);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    }
    for (const m of feats.marks || []) {
      const c = px(m.lat, m.lon);
      if (!c) continue;
      const s = Math.max(3, m.size * k);
      ctx.strokeStyle = halo ? 'rgba(0,0,0,0.7)' : m.color; ctx.lineWidth = Math.max(1, (halo ? 3.2 : 1.8) * Math.sqrt(k));
      ctx.beginPath();
      if (m.shape === 'hourglass') {
        ctx.moveTo(c[0] - s, c[1] - s); ctx.lineTo(c[0] + s, c[1] - s); ctx.lineTo(c[0] - s, c[1] + s); ctx.lineTo(c[0] + s, c[1] + s); ctx.closePath();
      } else {
        ctx.moveTo(c[0], c[1] - s); ctx.lineTo(c[0] + s, c[1]); ctx.lineTo(c[0], c[1] + s); ctx.lineTo(c[0] - s, c[1]); ctx.closePath();
      }
      ctx.stroke();
    }
  }
}

// pixel (px, py) of the map -> {lat, lon} or null
export function pixelToLatLon(proj, g, px, py) {
  const p = [0, 0, 0];
  if (!proj.unproject(-g.hw + (px + 0.5) * g.step, g.hh - (py + 0.5) * g.step, p)) return null;
  return { lat: Math.asin(clip(p[2], -1, 1)) / rad, lon: Math.atan2(p[1], p[0]) / rad, p };
}

export const parseExtent = (v) => (v ? [+v, +v] : null);
