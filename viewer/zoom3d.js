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
// centre, drawn over it: picking, ground heights and the camera already ask the finest
// tile that covers a point (see Zoom3D.tileAt); its falls, lakes and
// texture would be built per tile as the zoom's are.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const QMIN = 10;           // m3/s: smallest river drawn
const RIVER_RGB = '#3b77ad';
const SEA_RGB = 0x1d5487, LAKE_RGB = 0x3a7cb8, SKIRT_RGB = 0x3a3128;
const SKY = 0xa9c2dc;
// a river's drawn width in zoom pixels: 0.2 px at 10 m3/s to 1.4 px at ~600,000 (small streams exaggerated)
const riverPx = (q, mul = 1) => mul * Math.min(1.4, Math.max(0.2, 0.2 + 0.25 * Math.log10(Math.max(q, QMIN) / QMIN)));
// Chaikin-smoothed polyline [[x, y, ...], ...] (ends kept; the extra values follow the nearer end)
function chaikin(p, n = 2) {
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
// white water: streaks down the fall (v runs downstream), more opaque in the middle
function streaks() {
  const cv = document.createElement('canvas'), W = 64, H = 256;
  cv.width = W; cv.height = H;
  const cx = cv.getContext('2d');
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let x = 0; x < W; x++) {
    const edge = Math.sin(Math.PI * (x + 0.5) / W) ** 0.6;
    for (let k = 0; k < 6; k++) {
      const y = rnd() * H, len = 30 + rnd() * 90, a = (0.55 + 0.45 * rnd()) * edge;
      const g = cx.createLinearGradient(0, y, 0, y + len);
      g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.3, `rgba(255,255,255,${a})`); g.addColorStop(1, 'rgba(235,245,255,0)');
      cx.fillStyle = g; cx.fillRect(x, y, 1, len); cx.fillRect(x, y - H, 1, len);
    }
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

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

  // Each river (and lake) pixel's downstream neighbour (the zoom stores discharge, not
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
      // (lake pixels too: a fall's reach runs on through its plunge pool)
      if (water[i] === 1 || !(q[i] >= QMIN)) continue;
      if (water[i] === 0 && area[i] >= minArea && !(ice[i] > 0)) isR[i] = 1;
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
  terrain(step, material, skirtMat) {
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
    const skirt = new THREE.Mesh(sg, skirtMat);
    return { mesh, skirt, triangles: idx.length / 3, base };
  }

  // lake surfaces: a mesh on the pixel centres' grid over every cell with a
  // lake pixel at a corner: lake pixels at their level, the pixels round them
  // at the level or just under their ground where that is lower. So the
  // shore is where the ground rises through the water (not the pixels'
  // staircase), and next to lower ground (an outlet's gorge, the foot of a
  // fall) the surface dips under it instead of floating.
  lakes(material) {
    const { nx, ny, L } = this, n = nx * ny, h = L.elevation, water = L.water, EPS = 3;
    const vy = new Float32Array(n).fill(NaN);
    let any = false;
    for (let i = 0; i < n; i++) {
      if (water[i] !== 2) continue;
      any = true;
      const r = (i / nx) | 0, c = i - r * nx;
      // (no higher than its lowest dry neighbour: a plunge pool on a fall's
      // slope, smaller than its pixel, would otherwise hang above the ground below it)
      let y = this.wsA[i];
      for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
        const rr = r + dr, cc = c + dc, j = rr * nx + cc;
        if (rr >= 0 && cc >= 0 && rr < ny && cc < nx && water[j] === 0 && h[j] < y) y = h[j];
      }
      vy[i] = Number.isNaN(vy[i]) ? y : Math.min(vy[i], y);
      for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
        const rr = r + dr, cc = c + dc, j = rr * nx + cc;
        if (rr < 0 || cc < 0 || rr >= ny || cc >= nx || water[j] === 2) continue;
        const v = Math.min(y, h[j] - EPS);  // (sea pixels too: under their floor)
        vy[j] = Number.isNaN(vy[j]) ? v : Math.min(vy[j], v);
      }
    }
    if (!any) return null;
    const vid = new Int32Array(n).fill(-1), pos = [], idx = [];
    const V = (i) => {
      if (vid[i] < 0) { const r = (i / nx) | 0; vid[i] = pos.length / 3; pos.push(this.x(i - r * nx), vy[i], this.z(r)); }
      return vid[i];
    };
    for (let r = 0; r < ny - 1; r++) for (let c = 0; c < nx - 1; c++) {
      const a = r * nx + c, b = a + 1, d = a + nx, e = d + 1;
      if (water[a] !== 2 && water[b] !== 2 && water[d] !== 2 && water[e] !== 2) continue;
      // (the terrain's diagonal)
      if (Math.abs(h[a] - h[e]) <= Math.abs(h[b] - h[d])) idx.push(V(a), V(d), V(e), V(a), V(e), V(b));
      else idx.push(V(a), V(d), V(b), V(b), V(d), V(e));
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, material);
    m.receiveShadow = true;
    return m;
  }

  // the colour texture: the layer's nx x ny colours, scaled up, with rivers
  // (width by discharge, log scale)
  texture(colours, { smooth = true, rivers = true, widthMul = 1 } = {}) {
    const { nx, ny, L } = this, q = L.discharge;
    const S = Math.max(1, Math.min(4, Math.floor(4096 / Math.max(nx, ny))));
    const cv = document.createElement('canvas');
    cv.width = nx * S; cv.height = ny * S;
    const cx = cv.getContext('2d');
    cx.imageSmoothingEnabled = smooth;
    cx.drawImage(colours, 0, 0, cv.width, cv.height);
    const P = (i) => { const r = (i / nx) | 0; return [(i - r * nx + 0.5) * S, (r + 0.5) * S]; };
    const wpx = (v) => riverPx(v, widthMul);
    cx.lineCap = cx.lineJoin = 'round';
    const stroke = (pts, colour, extra = 0) => {
      // Chaikin-smoothed polyline (ends kept), stroked in runs of one width
      let p = pts.map((i) => [...P(i), q[i] || 0]);
      if (L.water[pts[pts.length - 1]] !== 0 && p.length > 1) p[p.length - 1][2] = p[p.length - 2][2];
      p = chaikin(p);
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
    }
    return cv;
  }

  // white water down each fall's reach: a ribbon just above the ground, as wide
  // as the river; v counts km downstream (the streaks' scale)
  fallRibbons(falls, widthMul) {
    const { nx, L } = this, pos = [], uv = [], idx = [], LIFT = 6;
    for (const f of falls) {
      if (!f.path || f.path.length < 2) continue;
      const q = L.discharge[f.path[0]] || f.discharge_m3s, hw = riverPx(q, widthMul) * this.res * 0.6;
      const p = chaikin(f.path.map((i) => [this.x(i % nx), this.z((i / nx) | 0), this.wsA[i]]), 3);
      let v = 0;
      const base = pos.length / 3;
      p.forEach(([x, z, ws], j) => {
        const a = p[Math.max(j - 1, 0)], b = p[Math.min(j + 1, p.length - 1)];
        let dx = b[0] - a[0], dz = b[1] - a[1];
        const dl = Math.hypot(dx, dz) || 1; dx /= dl; dz /= dl;
        if (j) v += Math.hypot(x - p[j - 1][0], z - p[j - 1][1]);
        for (const s of [-1, 1]) {
          const X = x - s * dz * hw, Z = z + s * dx * hw;
          pos.push(X, Math.max(this.height(X, Z), this.height(x, z), ws) + LIFT, Z);
          uv.push((s + 1) / 2, -v / 0.6);
        }
        if (j) { const k = base + 2 * j; idx.push(k - 2, k - 1, k, k, k - 1, k + 1); }
      });
    }
    if (!idx.length) return null;
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx);
    g.computeVertexNormals();
    return g;
  }

  // a fall's reach: from its lip down the river for its drop's length (at
  // least a pixel), through a plunge pool, not into the sea
  fallPath(f) {
    const { nx, res } = this, path = [f.px[0] * nx + f.px[1]];
    let km = 0, p = path[0];
    const want = Math.max(f.length_km || 0, res);
    for (let k = 0; k < 64 && km < want - 1e-6; k++) {
      const r = this.rec[p];
      if (r < 0) break;
      km += (r % nx !== p % nx && ((r / nx) | 0) !== ((p / nx) | 0) ? 1.4142 : 1) * res;
      path.push(r); p = r;
      if (this.L.water[r] === 1) break;
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
    const R = this.renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, powerPreference: 'high-performance',
      logarithmicDepthBuffer: true });  // (the sea at 0 over tidal flats a metre under it, seen from 1000 km)
    R.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    R.shadowMap.enabled = true;
    R.shadowMap.type = THREE.PCFSoftShadowMap;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(SKY);
    this.scene.fog = new THREE.Fog(SKY, 1, 2);  // (a little haze far off: set from the camera's distance in tick)
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.05, 5000);
    const C = this.controls = new OrbitControls(this.camera, cv);
    C.enableDamping = true; C.dampingFactor = 0.12;
    C.screenSpacePanning = false; C.maxPolarAngle = THREE.MathUtils.degToRad(89);
    C.zoomToCursor = true; C.minDistance = 0.3;
    C.listenToKeyEvents(window);
    this.hemi = new THREE.HemisphereLight(0xe4eef8, 0x5b4c3c, 1.0);
    this.sun = new THREE.DirectionalLight(0xfff2dd, 2.4);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(4096, 4096);
    this.scene.add(this.hemi, this.sun, this.sun.target);
    this.group = new THREE.Group();   // terrain, lakes, sea: y in metres, scaled by exag / 1000
    this.scene.add(this.group);
    this.pins = null; this.fallsOn = true;
    this.pinMat = new THREE.LineBasicMaterial({ color: 0xe8f6ff });
    this.skirtMat = new THREE.MeshBasicMaterial({ color: SKIRT_RGB, side: THREE.DoubleSide });
    this.terrainMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    this.seaMat = new THREE.MeshStandardMaterial({ color: SEA_RGB, transparent: true, opacity: 0.8, roughness: 0.6, metalness: 0 });
    this.fallMat = new THREE.MeshLambertMaterial({ map: streaks(), emissive: 0x7a8794, transparent: true,
      depthWrite: false, side: THREE.DoubleSide });
    this.lakeMat = new THREE.MeshStandardMaterial({ color: LAKE_RGB, roughness: 0.5, metalness: 0,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
    // a software renderer (no GPU): a quarter of the triangles, no shadows
    const dbg = R.getContext().getExtension('WEBGL_debug_renderer_info');
    this.gpu = dbg ? R.getContext().getParameter(dbg.UNMASKED_RENDERER_WEBGL) : '';
    if (/SwiftShader|llvmpipe|softpipe|Software/i.test(this.gpu)) Object.assign(this.opts, { step: 4, shadows: false });
    this.sun.castShadow = this.opts.shadows;
    this.tiles = []; this.falls = []; this.dirty = true; this.fly = null; this.frames = 0; this.fpsT = performance.now(); this.fps = 0;
    this.running = false;
    this.events(cv);
    addEventListener('resize', () => this.resize());
    // a GPU that drops the context (seen with shadows on NVIDIA through ANGLE's
    // Vulkan backend): three.js restores it; carry on without shadows
    cv.addEventListener('webglcontextrestored', () => {
      if (this.opts.shadows) { this.set('shadows', false); this.api.shadowsOff?.(); }
      this.dirty = true;
    });
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
    const { mesh, skirt, triangles } = t.terrain(this.opts.step, this.terrainMat, this.skirtMat);
    const lakes = t.lakes(this.lakeMat);
    const fg = t.fallRibbons(this.falls, this.opts.widthMul);
    this.fallMesh = fg ? new THREE.Mesh(fg, this.fallMat) : null;
    t.objects = [mesh, skirt, ...(lakes ? [lakes] : []), ...(this.fallMesh ? [this.fallMesh] : [])];
    this.group.add(...t.objects);
    this.triangles = triangles;
    this.applyExag();
  }
  setTexture(colours, smooth) {
    this.colours = colours; this.smooth = smooth;
    const t = this.tiles[0];
    if (!t) return;
    const cv = t.texture(colours, { smooth, rivers: this.opts.rivers, widthMul: this.opts.widthMul });
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
    else if (k === 'rivers') this.setTexture(this.colours, this.smooth);
    else if (k === 'widthMul') { this.rebuild(); this.setTexture(this.colours, this.smooth); }
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
      pos.push(x, y, z, x, y, z);
      f.base = new THREE.Vector3(x, y, z); f.anchor = f.base.clone(); f.pin = big.has(f.k) ? 0.07 : 0.035;
      const el = document.createElement('div');
      el.className = 'z3d-fall' + (big.has(f.k) ? ' big' : '') + (f.top ? ' top' : '');
      el.innerHTML = big.has(f.k) ? `&#9660; ${Math.round(f.height_m)} m` : '&#9660;';
      el.title = `waterfall ${Math.round(f.height_m)} m, ${Math.round(f.discharge_m3s)} m3/s (click: fly there)`;
      el.onclick = (e) => { e.stopPropagation(); (this.api.flyTo || ((k) => this.flyTo(k)))(f.k); };
      el.onmouseenter = (e) => this.api.showCard(f, e, false);
      el.onmouseleave = () => this.api.hideCard(false);
      f.el = el;
      this.labels.appendChild(el);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    this.pins = new THREE.LineSegments(g, this.pinMat);
    this.scene.add(this.pins);
    this.showFalls(this.fallsOn);
  }
  // the falls' pins and labels on or off (their white water stays: it's part of the river)
  showFalls(on) {
    this.fallsOn = on;
    this.labels.style.display = on ? '' : 'none';
    if (this.pins) this.pins.visible = on;
    this.dirty = true;
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
  // fly to fall k: look up its reach from downstream and a little to the side, a bit above
  flyTo(k) {
    const f = this.falls.find((g) => g.k === k), t = this.tiles[0];
    if (!f) return;
    const s = this.opts.exag / 1000, nx = t.nx;
    const a = f.path[0], b = f.path[f.path.length - 1];
    const ax = t.x(a % nx), az = t.z((a / nx) | 0), bx = t.x(b % nx), bz = t.z((b / nx) | 0);
    let dx = bx - ax, dz = bz - az;
    const dl = Math.hypot(dx, dz) || 1, turn = 0.35;  // (rad: a three-quarter view, the drop in profile)
    [dx, dz] = [(dx * Math.cos(turn) - dz * Math.sin(turn)) / dl, (dx * Math.sin(turn) + dz * Math.cos(turn)) / dl];
    const top = f.top_m ?? t.wsA[a], bot = f.bottom_m ?? t.wsA[b];
    const target = new THREE.Vector3((ax + bx) / 2, ((top + bot) / 2) * s, (az + bz) / 2);
    const d = Math.max(6, 3.5 * (f.length_km || 1), 6 * t.res, 5 * f.height_m * s);
    const el = THREE.MathUtils.degToRad(26);
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
  // pins a constant share of the view high (their length grows with the distance)
  placePins() {
    if (!this.pins) return;
    const a = this.pins.geometry.attributes.position, cam = this.camera.position;
    for (const f of this.falls) {
      f.anchor.copy(f.base);
      f.anchor.y += f.pin * Math.min(cam.distanceTo(f.base), this.size);
      a.setY(2 * f.k + 1, f.anchor.y);
    }
    a.needsUpdate = true;
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
    if (changed || this.dirty) this.tail = 10;  // (and a few frames after the last change: browsers can skip presenting one)
    else if (this.tail > 0) { this.tail--; this.dirty = true; }
    if (!changed && !this.dirty && !force) {
      this.frames = 0; this.fpsT = now;  // (fps counts only frames drawn while moving)
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
    this.scene.fog.near = 1.3 * dist; this.scene.fog.far = 1.3 * dist + 3 * this.size;
    this.camera.updateProjectionMatrix();
    this.aimSun(dist);
    this.placePins();
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
  // (a pixel read back after each waits for the GPU: its time, not the display's refresh)
  bench(frames = 120) {
    const gl = this.renderer.getContext(), C = this.controls, px = new Uint8Array(4), t0 = performance.now();
    const off = this.camera.position.clone().sub(C.target);
    for (let k = 0; k < frames; k++) {
      off.applyAxisAngle(new THREE.Vector3(0, 1, 0), (2 * Math.PI) / frames);
      this.camera.position.copy(C.target).add(off);
      this.camera.lookAt(C.target);
      this.dirty = true;
      this.tick(true);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    }
    const ms = (performance.now() - t0) / frames;
    return { ms_per_frame: +ms.toFixed(2), fps: +(1000 / ms).toFixed(1), triangles: this.triangles,
      pixels: [this.renderer.domElement.width, this.renderer.domElement.height], step: this.opts.step, shadows: this.opts.shadows };
  }
}
