// Where the globe's level-of-detail tiles come from (PW-1688, PW-1690): the thin interface lodtiles.js draws against.
//
//   open()                      -> {cells: [{id, lat, lon, up, outline}]} every cell of the tiling
//   has(key)                    whether the pyramid has this tile (lod.exists: it can be built)
//   ready(key)                  whether it is built (its files can be fetched now)
//   want(keys)                  the tiles the view needs and lacks, most wanted first: the unbuilt ones go to the server
//   building                    {queued, building, failed}: the server's queue for this world (the "sharpening" badge)
//   onBuilt                     called when a poll finds tiles newly built
//   elevation(key, signal)      -> {n, half: Uint16Array n*n (float16 m), water: Uint8Array n*n}
//   satellite(key, signal)      -> ImageBitmap (n x n, row 0 the tile's north edge)
//   layer(key, name, signal)    -> Float32Array n*n of one zoom layer, or null when the tile has no such layer
//
// The server (planet/tiles.py) builds tiles on demand: POST /api/tiles/want replaces its queue for the world with the
// list (so a pan away drops the rest), coarse first, then in our order (nearest the screen's centre first);
// GET /api/tiles/status says what is built, queued and building. The list is sent when it changes, once the view has
// settled for SETTLE_MS, and at least every MOVING_MS while it keeps changing; the status is polled every POLL_MS while
// anything is queued or building.
import * as M from '../lodmath.js';

const SETTLE_MS = 250, MOVING_MS = 2000, POLL_MS = 1000, RETRY_MS = 60000;

export class NotBuilt extends Error {}

export class TileSource {
  constructor(world) {
    this.world = world; this.cells = new Map(); this.built = new Set(); this.failed = new Map();  // (failed: id -> when; retried after RETRY_MS)
    this.exists = new Map(); this.building = { queued: 0, building: 0, failed: 0, note: '' };
    this.sent = null; this.pending = null; this.changed = 0; this.lastPost = 0; this.timer = null; this.polling = null;
    this.gen = 0; this.closed = false; this.onBuilt = null;
  }

  async open() {
    const r = await fetch(`/api/tiles/index?world=${encodeURIComponent(this.world)}`);
    if (!r.ok) throw new Error(`tiles index: ${r.status}`);
    const ix = await r.json();
    for (const c of ix.cells) {
      this.cells.set(c.id, c);
      for (const [lv, list] of Object.entries(c.built || {})) for (const [x, y] of list) this.built.add(`${c.id}/${lv}/${x}/${y}`);
    }
    return { cells: [...this.cells.values()] };
  }

  close() { this.closed = true; clearTimeout(this.timer); clearTimeout(this.polling); }

  has(k) {
    let e = this.exists.get(k.id);
    if (e === undefined) {
      const c = this.cells.get(k.cell);
      e = !!c && M.exists(k, c.outline);
      this.exists.set(k.id, e);
    }
    return e;
  }

  ready(k) { return this.built.has(k.id); }

  want(keys) {
    const now = performance.now();
    const list = keys.filter((k) => !this.built.has(k.id) && !(now - (this.failed.get(k.id) ?? -Infinity) < RETRY_MS)).map((k) => k.id);
    const sig = list.join(' ');
    if (sig === (this.pending ?? this.sent)) return;
    this.pending = sig; this.changed = performance.now();
    this.schedule();
  }

  schedule() {
    clearTimeout(this.timer);
    if (this.pending === null || this.closed) return;
    const now = performance.now(), due = Math.min(this.changed + SETTLE_MS, this.lastPost + MOVING_MS);
    if (now >= due) this.post();
    else this.timer = setTimeout(() => this.schedule(), due - now);
  }

  async post() {
    const sig = this.pending; this.pending = null; this.sent = sig; this.lastPost = performance.now();
    try {
      const r = await fetch('/api/tiles/want', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ world: this.world, gen: ++this.gen, tiles: sig ? sig.split(' ') : [] }),
      });
      if (r.ok) this.take(await r.json());
    } catch (e) { console.warn('[lod] want:', e.message); }
  }

  async poll() {
    this.polling = null;
    if (this.closed) return;
    try {
      const r = await fetch(`/api/tiles/status?world=${encodeURIComponent(this.world)}`);
      if (r.ok) this.take(await r.json());
    } catch (e) { console.warn('[lod] status:', e.message); }
  }

  take(st) {
    let fresh = 0;
    for (const [id, t] of Object.entries(st.tiles || {})) {
      if (t.state === 'built' && !this.built.has(id)) { this.built.add(id); fresh++; }
      if (t.state === 'failed' && !this.failed.has(id)) { this.failed.set(id, performance.now()); console.warn('[lod] tile', id, 'failed:', t.error); }
    }
    this.building = { queued: st.queued || 0, building: st.building || 0, failed: this.failed.size, note: st.note || '' };
    if (fresh && this.onBuilt) this.onBuilt(fresh);
    if (fresh) this.sent = null;  // (the next want() resends the list without them)
    clearTimeout(this.polling);
    if (!this.closed && (this.building.queued || this.building.building)) this.polling = setTimeout(() => this.poll(), POLL_MS);
  }

  url(k, file) { return `/api/tiles/${encodeURIComponent(this.world)}/${k.cell}/${k.level}/${k.tx}/${k.ty}/${file}`; }

  async fetchOk(k, file, signal) {
    const r = await fetch(this.url(k, file), { signal });
    if (r.status === 404 && file !== 'satellite.png' && !file.startsWith('layer/')) {
      this.built.delete(k.id);  // (dropped from the server's cache meanwhile: wanted again)
      throw new NotBuilt(`${k.id} is not built`);
    }
    return r;
  }

  async elevation(k, signal) {
    const r = await this.fetchOk(k, 'view.bin', signal);
    if (!r.ok) throw new Error(`${k.id} view.bin: ${r.status}`);
    const buf = await r.arrayBuffer(), dv = new DataView(buf);
    if (dv.getUint32(0, false) !== 0x50575431) throw new Error(`${k.id}: not a PWT1 tile`);
    const n = dv.getInt32(4, true);
    return { n, half: new Uint16Array(buf, 8, n * n), water: new Uint8Array(buf, 8 + 2 * n * n, n * n) };
  }

  async satellite(k, signal) {
    const r = await this.fetchOk(k, 'satellite.png', signal);
    if (!r.ok) throw new Error(`${k.id} satellite: ${r.status}`);
    return createImageBitmap(await r.blob(), { imageOrientation: 'none', premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
  }

  async layer(k, name, signal) {
    const r = await this.fetchOk(k, `layer/${name}.bin`, signal);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`${k.id} ${name}: ${r.status}`);
    return new Float32Array(await r.arrayBuffer());
  }
}
