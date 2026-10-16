// The 3D view of a regional zoom (PW-072): a three.js heightmap of the zoom's
// heights, coloured by the 2D viewer's active layer (unshaded: the sun lights
// it here), with the sea at 0, lake surfaces at their levels, rivers painted
// into the texture sized by discharge, and the waterfalls marked and listed.
//
// Loaded by zoom.html (`import('./zoom3d.js')`), which hands it the zoom's
// layers and colours through `api` (below) and keeps its own controls, hover
// panel and marker cards.
//
// Scene units: km. x = east, z = south (north is -z), y = up. Each terrain is
// a Tile: a 500 x 500 zoom at its res_km, centred at (x0, z0) km. Heights are
// stored in metres and the tiles' group is scaled by exag / 1000, so the
// vertical exaggeration is one scale. The first tile is the zoom; a finer
// nested zoom (PW-129) would be a second Tile at its offset from the parent's
// centre, drawn over it: picking, heights and markers already ask the finest
// tile that covers a point (see Zoom3D.tileAt).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const QMIN = 10;           // m3/s: smallest river drawn
const RIVER_RGB = '#3b77ad', FOAM_RGB = '#f2fbff';
const SEA_RGB = 0x1d5487, LAKE_RGB = 0x3a7cb8, SKIRT_RGB = 0x3a3128;
const SKY = 0xa9c2dc;

// --------------------------------------------------------------- one terrain
class Tile {
  // src: {nx, ny, res_km, L: {elevation, water, lake_depth, discharge, drainage_area, ice}};
  // x0, z0: its centre in scene km
  constructor(src, x0 = 0, z0 = 0) {
    Object.assign(this, { nx: src.nx, ny: src.ny, res: src.res_km, L: src.L, x0, z0 });
    this.w = this.nx * this.res; this.d = this.ny * this.res;
    const h = this.L.elevation;
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < h.length; i++) { if (h[i] < lo) lo = h[i]; if (h[i] > hi) hi = h[i]; }
    this.lo = lo; this.hi = hi;
    this.flow();
  }
  // pixel centre (r, c) -> scene x, z
  x(c) { return this.x0 + (c + 0.5 - this.nx / 2) * this.res; }
  z(r) { return this.z0 + (r + 0.5 - this.ny / 2) * this.res; }
  contains(x, z) { return Math.abs(x - this.x0) <= this.w / 2 && Math.abs(z - this.z0) <= this.d / 2; }
  // scene x, z -> fractional pixel (r, c) of the pixel centres' grid
  rc(x, z) { return [(z - this.z0) / this.res + this.ny / 2 - 0.5, (x - this.x0) / this.res + this.nx / 2 - 0.5]; }
  pixel(x, z) {
    const [r, c] = this.rc(x, z), ri = Math.round(r), ci = Math.round(c);
    return ri >= 0 && ci >= 0 && ri < this.ny && ci < this.nx ? [ri, ci] : null;
  }
  // ground height (m), bilinear between pixel centres, as the full-detail mesh draws it
  height(x, z) {
    const [r, c] = this.rc(x, z), nx = this.nx, ny = this.ny, h = this.L.elevation;
    const r0 = Math.min(Math.max(Math.floor(r), 0), ny - 2), c0 = Math.min(Math.max(Math.floor(c), 0), nx - 2);
    const fr = Math.min(Math.max(r - r0, 0), 1), fc = Math.min(Math.max(c - c0, 0), 1), i = r0 * nx + c0;
    return (h[i] * (1 - fc) + h[i + 1] * fc) * (1 - fr) + (h[i + nx] * (1 - fc) + h[i + nx + 1] * fc) * fr;
  }
  // water surface (m): lakes at their level, the sea at 0, else the ground
  ws(i) { const L = this.L; return L.water[i] === 2 ? L.elevation[i] + L.lake_depth[i] : L.water[i] === 1 ? 0 : L.elevation[i]; }

  // Each river pixel's downstream neighbour (the zoom stores discharge, not
  // its D8 receivers): the steepest drop in water surface among neighbours
  // that carry at least as much water (or are lake or sea), else the one
  // with the most water. Then the river lines: runs of river pixels between
  // heads, confluences and the water they end in.
  flow() {
    const { nx, ny, res, L } = this, n = nx * ny, q = L.discharge, water = L.water, area = L.drainage_area, ice = L.ice;
    const minArea = 500 * Math.max(res / 2, 1);
    const ws = new Float32Array(n);
    for (let i = 0; i < n; i++) ws[i] = this.ws(i);
    const rec = new Int32Array(n).fill(-1), isR = new Uint8Array(n);
    for (let i = 0; i < n; i++) {
      if (water[i] !== 0 || !(q[i] >= QMIN)) continue;
      if (area[i] >= minArea && !(ice[i] > 0)) isR[i] = 1;
      const r = (i / nx) | 0, c = i - r * nx;
      let best = -1, bs = 0, alt = -1, aq = -1;
      for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
        if (!dr && !dc) continue;
        const rr = r + dr, cc = c + dc;
        if (rr < 0 || cc < 0 || rr >= ny || cc >= nx) continue;
        const j = rr * nx + cc;
        if (water[j] === 0 && q[j] < q[i]) continue;
        const s = (ws[i] - ws[j]) / (dr && dc ? 1.4142 : 1);
        if (s > bs) { bs = s; best = j; }
        if (q[j] > aq) { aq = q[j]; alt = j; }
      }
      rec[i] = best >= 0 ? best : alt;
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
    this.rec = rec; this.lines = lines; this.wsA = ws;
  }

  // the terrain mesh, every `step` pixels (the texture keeps full detail)
  terrain(step, material) {
    const { nx, ny, L } = this, h = L.elevation;
    const ix = (m) => { const a = []; for (let k = 0; k < m - 1; k += step) a.push(k); a.push(m - 1); return a; };
    const cs = ix(nx), rs = ix(ny), W = cs.length, H = rs.length;
    const pos = new Float32Array(W * H * 3), uv = new Float32Array(W * H * 2);
    for (let a = 0; a < H; a++) for (let b = 0; b < W; b++) {
      const r = rs[a], c = cs[b], v = a * W + b;
      pos[3 * v] = this.x(c); pos[3 * v + 1] = h[r * nx + c]; pos[3 * v + 2] = this.z(r);
      uv[2 * v] = (c + 0.5) / nx; uv[2 * v + 1] = 1 - (r + 0.5) / ny;
    }
    const idx = new Uint32Array((W - 1) * (H - 1) * 6);
    let k = 0;
    for (let a = 0; a < H - 1; a++) for (let b = 0; b < W - 1; b++) {
      const v = a * W + b;
      // split each quad along the diagonal that follows the ground better
      const d1 = Math.abs(pos[3 * v + 1] - pos[3 * (v + W + 1) + 1]), d2 = Math.abs(pos[3 * (v + 1) + 1] - pos[3 * (v + W) + 1]);
      if (d1 <= d2) { idx.set([v, v + W, v + W + 1, v, v + W + 1, v + 1], k); }
      else { idx.set([v, v + W, v + 1, v + 1, v + W, v + W + 1], k); }
      k += 6;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    g.setIndex(new THREE.BufferAttribute(idx, 1));
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, material);
    mesh.castShadow = mesh.receiveShadow = true;
    // the block's sides, down to a base below the deepest point (a diorama)
    const base = Math.min(this.lo, 0) - 0.08 * (this.hi - Math.min(this.lo, 0)) - 200;
    const ring = [];
    for (const b of cs) ring.push([rs[0], b]);
    for (const a of rs.slice(1)) ring.push([a, cs[W - 1]]);
    for (const b of cs.slice(0, -1).reverse()) ring.push([rs[H - 1], b]);
    for (const a of rs.slice(1, -1).reverse()) ring.push([a, cs[0]]);
    ring.push(ring[0]);
    const sp = new Float32Array(ring.length * 6);
    ring.forEach(([r, c], j) => {
      const x = this.x(c), z = this.z(r);
      sp.set([x, h[r * nx + c], z, x, base, z], 6 * j);
    });
    const si = [];
    for (let j = 0; j < ring.length - 1; j++) si.push(2 * j, 2 * j + 1, 2 * j + 2, 2 * j + 2, 2 * j + 1, 2 * j + 3);
    const sg = new THREE.BufferGeometry();
    sg.setAttribute('position', new THREE.BufferAttribute(sp, 3));
    sg.setIndex(si);
    const skirt = new THREE.Mesh(sg, new THREE.MeshBasicMaterial({ color: SKIRT_RGB, side: THREE.DoubleSide }));
    return { mesh, skirt, triangles: idx.length / 3, base };
  }

  // lake surfaces: a quad per lake pixel at its level (lakes are flat, so a lake's quads are one plane)
  lakes(material) {
    const { nx, ny, res, L } = this, n = nx * ny, pos = [];
    for (let i = 0; i < n; i++) {
      if (L.water[i] !== 2) continue;
      const r = (i / nx) | 0, c = i - r * nx, x = this.x(c), z = this.z(r), y = this.wsA[i], e = res / 2;
      pos.push(x - e, y, z - e, x - e, y, z + e, x + e, y, z + e, x - e, y, z - e, x + e, y, z + e, x + e, y, z - e);
    }
    if (!pos.length) return null;
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, material);
    m.receiveShadow = true;
    return m;
  }

  // the colour texture: the layer's nx x ny colours, scaled up, with rivers
  // (width by discharge, log scale) and white water down each fall's reach
  texture(colours, { smooth = true, rivers = true, widthMul = 1, falls = [] } = {}) {
    const { nx, ny, L } = this, q = L.discharge;
    const S = Math.max(1, Math.min(4, Math.floor(4096 / Math.max(nx, ny))));
    const cv = document.createElement('canvas');
    cv.width = nx * S; cv.height = ny * S;
    const cx = cv.getContext('2d');
    cx.imageSmoothingEnabled = smooth;
    cx.drawImage(colours, 0, 0, cv.width, cv.height);
    const P = (i) => { const r = (i / nx) | 0; return [(i - r * nx + 0.5) * S, (r + 0.5) * S]; };
    // width in zoom pixels: 0.25 px at 10 m3/s to 1.6 px at ~300,000 (small streams exaggerated)
    const wpx = (v) => widthMul * Math.min(1.6, Math.max(0.25, 0.25 + 0.3 * Math.log10(Math.max(v, QMIN) / QMIN)));
    cx.lineCap = cx.lineJoin = 'round';
    const stroke = (pts, colour, extra = 0) => {
      // Chaikin-smoothed polyline (ends kept), stroked in runs of one width
      let p = pts.map((i) => [...P(i), q[i] || 0]);
      if (L.water[pts[pts.length - 1]] !== 0 && p.length > 1) p[p.length - 1][2] = p[p.length - 2][2];
      for (let it = 0; it < 2 && p.length > 2; it++) {
        const o = [p[0]];
        for (let j = 0; j < p.length - 1; j++) {
          const a = p[j], b = p[j + 1];
          o.push([0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1], a[2]], [0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1], b[2]]);
        }
        o.push(p[p.length - 1]);
        p = o;
      }
      cx.strokeStyle = colour;
      let j = 0;
      while (j < p.length - 1) {
        const w = Math.round(4 * (wpx(p[j][2]) * S + extra)) / 4;
        cx.lineWidth = w; cx.beginPath(); cx.moveTo(p[j][0], p[j][1]);
        while (j < p.length - 1 && Math.round(4 * (wpx(p[j][2]) * S + extra)) / 4 === w) { j++; cx.lineTo(p[j][0], p[j][1]); }
        cx.stroke();
      }
    };
    if (rivers) {
      for (const pts of this.lines) stroke(pts, RIVER_RGB);
      for (const f of falls) if (f.path && f.path.length > 1) stroke(f.path, FOAM_RGB, 0.6 * S);
    }
    return cv;
  }

  // a fall's reach: from its lip down the river for its drop's length (at least a pixel)
  fallPath(f) {
    const { nx, res } = this, path = [f.px[0] * nx + f.px[1]];
    let km = 0, p = path[0];
    const want = Math.max(f.length_km || 0, res);
    for (let k = 0; k < 64 && km < want - 1e-6; k++) {
      const r = this.rec[p];
      if (r < 0) break;
      km += (r % nx !== p % nx && ((r / nx) | 0) !== ((p / nx) | 0) ? 1.4142 : 1) * res;
      path.push(r); p = r;
      if (this.L.water[r] !== 0) break;
    }
    return path;
  }
}

// --------------------------------------------------------------- the view
export class Zoom3D {
  // host: an element to fill; api: {hoverPixel(r, c), showCard(o, ev, pin), hideCard(), changed()}
  constructor(host, api) {
    this.host = host; this.api = api;
    this.opts = { exag: 3, step: 1, shadows: true, facets: false, sunAz: 315, sunEl: 35, rivers: true, widthMul: 1 };
    const cv = document.createElement('canvas');
    cv.className = 'z3d-canvas';
    host.appendChild(cv);
    this.labels = document.createElement('div');
    this.labels.className = 'z3d-labels';
    host.appendChild(this.labels);
    const R = this.renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, powerPreference: 'high-performance' });
    R.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    R.shadowMap.enabled = true;
    R.shadowMap.type = THREE.PCFSoftShadowMap;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(SKY);
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.05, 5000);
    const C = this.controls = new OrbitControls(this.camera, cv);
    C.enableDamping = true; C.dampingFactor = 0.12;
    C.screenSpacePanning = false; C.maxPolarAngle = THREE.MathUtils.degToRad(89);
    C.zoomToCursor = true; C.minDistance = 0.3;
    C.listenToKeyEvents(window);
    this.hemi = new THREE.HemisphereLight(0xe4eef8, 0x5b4c3c, 1.1);
    this.sun = new THREE.DirectionalLight(0xfff2dd, 3.2);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(4096, 4096);
    this.scene.add(this.hemi, this.sun, this.sun.target);
    this.group = new THREE.Group();   // terrain, lakes, sea: y in metres, scaled by exag / 1000
    this.scene.add(this.group);
    this.pins = null;
    this.terrainMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    this.seaMat = new THREE.MeshStandardMaterial({ color: SEA_RGB, transparent: true, opacity: 0.8, roughness: 0.3, metalness: 0 });
    this.lakeMat = new THREE.MeshStandardMaterial({ color: LAKE_RGB, transparent: true, opacity: 0.88, roughness: 0.25, metalness: 0,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
    this.tiles = []; this.falls = []; this.dirty = true; this.fly = null; this.frames = 0; this.fpsT = performance.now(); this.fps = 0;
    this.running = false;
    this.events(cv);
    addEventListener('resize', () => this.resize());
  }

  // ------------------------------------------------ building
  // z: {nx, ny, res_km, L, falls: [{px, height_m, top_m, bottom_m, length_km, ...}], colours: canvas, smooth}
  setZoom(z, cam) {
    for (const t of this.tiles) this.group.remove(...t.objects);
    if (this.sea) this.group.remove(this.sea);
    const t = new Tile(z, 0, 0);
    t.objects = [];
    this.tiles = [t];
    this.size = Math.max(t.w, t.d);
    this.falls = z.falls.map((f, k) => ({ ...f, k, path: t.fallPath(f) }));
    const seaPx = z.L.water.some((w) => w === 1);
    this.sea = null;
    if (seaPx) {
      const g = new THREE.PlaneGeometry(t.w, t.d).rotateX(-Math.PI / 2);
      this.sea = new THREE.Mesh(g, this.seaMat);
      this.sea.receiveShadow = true;
      this.group.add(this.sea);
    }
    this.colours = z.colours; this.smooth = z.smooth;
    this.rebuild();
    this.setTexture(z.colours, z.smooth);
    this.home(cam);
  }
  rebuild() {
    const t = this.tiles[0];
    if (!t) return;
    this.group.remove(...t.objects);
    t.objects.forEach((o) => o.geometry?.dispose());
    const { mesh, skirt, triangles } = t.terrain(this.opts.step, this.terrainMat);
    const lakes = t.lakes(this.lakeMat);
    t.objects = [mesh, skirt, ...(lakes ? [lakes] : [])];
    this.group.add(...t.objects);
    this.triangles = triangles;
    this.applyExag();
  }
  setTexture(colours, smooth) {
    this.colours = colours; this.smooth = smooth;
    const t = this.tiles[0];
    if (!t) return;
    const cv = t.texture(colours, { smooth, rivers: this.opts.rivers, widthMul: this.opts.widthMul, falls: this.falls });
    const tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = this.renderer.capabilities.getMaxAnisotropy();
    tex.minFilter = THREE.LinearMipmapLinearFilter;
    this.terrainMat.map?.dispose();
    this.terrainMat.map = tex; this.terrainMat.needsUpdate = true;
    this.dirty = true;
  }
  set(k, v) {
    this.opts[k] = v;
    if (k === 'exag') this.applyExag();
    else if (k === 'step') this.rebuild();
    else if (k === 'rivers' || k === 'widthMul') this.setTexture(this.colours, this.smooth);
    else if (k === 'shadows') { this.sun.castShadow = v; this.renderer.shadowMap.needsUpdate = true; }
    else if (k === 'facets') { this.terrainMat.flatShading = v; this.terrainMat.needsUpdate = true; }
    this.dirty = true;
  }
  applyExag() {
    const old = this.group.scale.y, s = this.opts.exag / 1000;
    this.group.scale.y = s;
    // keep the camera's target on the ground and its height above it in proportion
    if (old && old !== s && this.tiles.length) {
      const C = this.controls, ty = C.target.y;
      C.target.y *= s / old; this.camera.position.y += C.target.y - ty;
    }
    this.buildPins();
    this.dirty = true;
  }
  // a pin above each fall, its label at the top
  buildPins() {
    if (this.pins) { this.scene.remove(this.pins); this.pins.geometry.dispose(); }
    const t = this.tiles[0];
    if (!t) return;
    const s = this.opts.exag / 1000, pos = [];
    this.labels.innerHTML = '';
    const ranked = [...this.falls].sort((a, b) => b.height_m - a.height_m);
    const big = new Set(ranked.slice(0, 12).map((f) => f.k));
    for (const f of this.falls) {
      const x = t.x(f.px[1]), z = t.z(f.px[0]), y = Math.max(f.top_m ?? t.wsA[f.path[0]], 0) * s;
      const ph = (big.has(f.k) ? 0.035 : 0.018) * this.size ** 0.75;
      pos.push(x, y, z, x, y + ph, z);
      f.anchor = new THREE.Vector3(x, y + ph, z); f.base = new THREE.Vector3(x, y, z);
      const el = document.createElement('div');
      el.className = 'z3d-fall' + (big.has(f.k) ? ' big' : '') + (f.top ? ' top' : '');
      el.innerHTML = big.has(f.k) ? `&#9660; ${Math.round(f.height_m)} m` : '&#9660;';
      el.title = `waterfall ${Math.round(f.height_m)} m, ${Math.round(f.discharge_m3s)} m3/s (click: fly there)`;
      el.onclick = (e) => { e.stopPropagation(); this.flyTo(f.k); };
      el.onmouseenter = (e) => this.api.showCard(f, e, false);
      el.onmouseleave = () => this.api.hideCard(false);
      f.el = el;
      this.labels.appendChild(el);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    this.pins = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xe8f6ff }));
    this.scene.add(this.pins);
    this.occlusionAt = 0;
  }

  // ------------------------------------------------ camera
  home(cam) {
    const C = this.controls, s = this.size;
    if (cam && cam.length === 6) {
      this.camera.position.set(cam[0], cam[1], cam[2]); C.target.set(cam[3], cam[4], cam[5]);
    } else {
      C.target.set(0, 0, 0);
      this.camera.position.set(0, 0.62 * s, 0.78 * s);
    }
    C.maxDistance = 3 * s;
    C.update();
    this.dirty = true;
  }
  camState() {
    const p = this.camera.position, t = this.controls.target;
    return [p.x, p.y, p.z, t.x, t.y, t.z].map((v) => +v.toFixed(2));
  }
  // fly to fall k: look up its reach from downstream, a bit above
  flyTo(k) {
    const f = this.falls.find((g) => g.k === k), t = this.tiles[0];
    if (!f) return;
    const s = this.opts.exag / 1000, nx = t.nx;
    const a = f.path[0], b = f.path[f.path.length - 1];
    const ax = t.x(a % nx), az = t.z((a / nx) | 0), bx = t.x(b % nx), bz = t.z((b / nx) | 0);
    let dx = bx - ax, dz = bz - az;
    const dl = Math.hypot(dx, dz) || 1; dx /= dl; dz /= dl;
    const top = f.top_m ?? t.wsA[a], bot = f.bottom_m ?? t.wsA[b];
    const target = new THREE.Vector3((ax + bx) / 2, ((top + bot) / 2) * s, (az + bz) / 2);
    const d = Math.max(5, 3 * (f.length_km || 1), 5 * t.res, 4 * f.height_m * s);
    const el = THREE.MathUtils.degToRad(22);
    const pos = new THREE.Vector3(target.x + dx * d * Math.cos(el), target.y + d * Math.sin(el), target.z + dz * d * Math.cos(el));
    // (not under the ground on the way)
    pos.y = Math.max(pos.y, this.groundY(pos.x, pos.z) + 0.3);
    this.fly = { t0: performance.now(), dur: 1400, p0: this.camera.position.clone(), q0: this.controls.target.clone(), p1: pos, q1: target };
    this.flown = k;
    this.dirty = true;
  }

  // ------------------------------------------------ heights and picking
  tileAt(x, z) { for (let j = this.tiles.length - 1; j >= 0; j--) if (this.tiles[j].contains(x, z)) return this.tiles[j]; return null; }
  groundY(x, z) { const t = this.tileAt(x, z); return t ? t.height(x, z) * this.opts.exag / 1000 : -Infinity; }
  // march a ray over the heightfield: the first point under the ground (bisected), or null
  march(o, dir, maxD, step) {
    let prev = 0;
    for (let d = step; d <= maxD; d += step) {
      const x = o.x + dir.x * d, y = o.y + dir.y * d, z = o.z + dir.z * d;
      if (y < this.groundY(x, z)) {
        let lo = prev, hi = d;
        for (let k = 0; k < 12; k++) {
          const m = (lo + hi) / 2;
          if (o.y + dir.y * m < this.groundY(o.x + dir.x * m, o.z + dir.z * m)) hi = m; else lo = m;
        }
        return new THREE.Vector3(o.x + dir.x * hi, o.y + dir.y * hi, o.z + dir.z * hi);
      }
      prev = d;
    }
    return null;
  }
  pickGround(ev) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(((ev.clientX - rect.left) / rect.width) * 2 - 1, -((ev.clientY - rect.top) / rect.height) * 2 + 1);
    const ray = new THREE.Raycaster();
    ray.setFromCamera(ndc, this.camera);
    const t = this.tiles[0];
    return this.march(ray.ray.origin, ray.ray.direction, 4 * this.size, t.res * 0.4);
  }
  occlude() {
    const cam = this.camera.position, t = this.tiles[0];
    const W = this.renderer.domElement.clientWidth, H = this.renderer.domElement.clientHeight;
    for (const f of this.falls) {
      const p = f.anchor.clone().project(this.camera);
      const on = p.z < 1 && Math.abs(p.x) < 1.05 && Math.abs(p.y) < 1.05;
      let hidden = !on;
      if (on) {
        const dir = f.base.clone().sub(cam), D = dir.length();
        dir.divideScalar(D);
        const hit = this.march(cam, dir, D - 1.5 * t.res, Math.max(t.res * 0.5, D / 1500));
        hidden = !!hit;
      }
      f.hidden = hidden;
      f.el.classList.toggle('behind', hidden);
    }
    this.placeLabels(W, H);
  }
  placeLabels(W, H) {
    for (const f of this.falls) {
      const p = f.anchor.clone().project(this.camera);
      const vis = p.z < 1 && Math.abs(p.x) < 1.05 && Math.abs(p.y) < 1.05;
      f.el.style.display = vis ? '' : 'none';
      if (vis) f.el.style.transform = `translate(${((p.x + 1) / 2) * W}px, ${((1 - p.y) / 2) * H}px) translate(-50%, -100%)`;
    }
  }

  // ------------------------------------------------ events and loop
  events(cv) {
    let pending = null, down = null;
    cv.addEventListener('pointermove', (e) => {
      if (pending) return;
      pending = requestAnimationFrame(() => {
        pending = null;
        if (down) return;
        const p = this.pickGround(e), t = p && this.tileAt(p.x, p.z), px = t && t.pixel(p.x, p.z);
        this.api.hoverPixel(px ? px[0] : null, px ? px[1] : null, t);
      });
    });
    cv.addEventListener('pointerdown', (e) => { down = [e.clientX, e.clientY]; this.fly = null; });
    cv.addEventListener('pointerup', () => { down = null; });
    cv.addEventListener('dblclick', (e) => {
      // double-click the ground: orbit round that point
      const p = this.pickGround(e);
      if (p) this.fly = { t0: performance.now(), dur: 700, p0: this.camera.position.clone(), q0: this.controls.target.clone(),
        p1: this.camera.position.clone().add(p.clone().sub(this.controls.target)), q1: p };
    });
    this.controls.addEventListener('change', () => { this.dirty = true; this.moved = performance.now(); });
  }
  resize() {
    const w = this.host.clientWidth || innerWidth, h = this.host.clientHeight || innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    this.dirty = true;
  }
  start() {
    if (this.running) return;
    this.running = true; this.resize();
    const loop = () => {
      if (!this.running) return;
      requestAnimationFrame(loop);
      this.tick();
    };
    requestAnimationFrame(loop);
  }
  stop() { this.running = false; }
  tick(force = false) {
    const now = performance.now();
    if (this.fly) {
      const F = this.fly, u = Math.min(1, (now - F.t0) / F.dur), e = u * u * (3 - 2 * u);
      this.camera.position.lerpVectors(F.p0, F.p1, e);
      this.controls.target.lerpVectors(F.q0, F.q1, e);
      if (u >= 1) this.fly = null;
      this.dirty = true; this.moved = now;
    }
    const changed = this.controls.update();
    if (!changed && !this.dirty && !force) {
      // settled: hide the labels behind the ground, once
      if (this.moved && now - this.moved > 150) { this.moved = 0; this.occlude(); this.api.changed?.(); }
      return;
    }
    this.dirty = false;
    // keep the camera above the ground
    const cam = this.camera.position, gy = this.groundY(cam.x, cam.z);
    if (cam.y < gy + 0.05) cam.y = gy + 0.05;
    const dist = cam.distanceTo(this.controls.target);
    this.camera.near = Math.max(0.01, dist / 400); this.camera.far = dist * 6 + 3 * this.size;
    this.camera.updateProjectionMatrix();
    this.aimSun(dist);
    this.renderer.render(this.scene, this.camera);
    this.placeLabels(this.renderer.domElement.clientWidth, this.renderer.domElement.clientHeight);
    this.frames++;
    if (now - this.fpsT > 1000) { this.fps = this.frames * 1000 / (now - this.fpsT); this.frames = 0; this.fpsT = now; this.api.fps?.(this.fps); }
  }
  // the sun: its direction from the sliders; its shadow box round what the camera looks at
  aimSun(dist) {
    const az = THREE.MathUtils.degToRad(this.opts.sunAz), el = THREE.MathUtils.degToRad(this.opts.sunEl);
    const dir = new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el));
    const tg = this.controls.target, r = Math.min(0.75 * this.size, Math.max(2 * dist, 10));
    this.sun.target.position.copy(tg);
    this.sun.position.copy(tg).addScaledVector(dir, 2 * this.size);
    const sc = this.sun.shadow.camera;
    sc.left = -r; sc.right = r; sc.top = r; sc.bottom = -r; sc.near = 0.1; sc.far = 4 * this.size;
    sc.updateProjectionMatrix();
    this.sun.shadow.normalBias = 0.6 * (this.tiles[0]?.res || 1) * (r / (0.75 * this.size)) ** 0.5;
    this.sun.shadow.bias = -0.0004;
  }
  // frames per second with the camera turning: `frames` rendered back to back
  // (gl.finish after each, so it's the GPU's time, not the display's refresh)
  bench(frames = 120) {
    const gl = this.renderer.getContext(), C = this.controls, t0 = performance.now();
    const off = this.camera.position.clone().sub(C.target);
    for (let k = 0; k < frames; k++) {
      off.applyAxisAngle(new THREE.Vector3(0, 1, 0), (2 * Math.PI) / frames);
      this.camera.position.copy(C.target).add(off);
      this.camera.lookAt(C.target);
      this.dirty = true;
      this.tick(true);
      gl.finish();
    }
    const ms = (performance.now() - t0) / frames;
    return { ms_per_frame: +ms.toFixed(2), fps: +(1000 / ms).toFixed(1), triangles: this.triangles,
      pixels: [this.renderer.domElement.width, this.renderer.domElement.height], step: this.opts.step, shadows: this.opts.shadows };
  }
}
