// Where the globe's level-of-detail tiles come from (PW-1688): the thin interface lodtiles.js draws against.
//
//   open()                      -> {cells: [{id, lat, lon, up, outline, tiles: {level: Set('tx,ty')}}]} the cells with tiles
//   has(key)                    whether the source can give this tile (now or once built)
//   want(keys)                  the tiles the view needs and lacks, most wanted first (a build queue may follow it)
//   elevation(key, signal)      -> {n, half: Uint16Array n*n (float16 m), water: Uint8Array n*n}
//   satellite(key, signal)      -> ImageBitmap (n x n, row 0 the tile's north edge)
//   layer(key, name, signal)    -> Float32Array n*n of one zoom layer, or null when the tile has no such layer
//
// StandinTileSource is the STAND-IN: GET /api/tiles/... of planet/tiles_standin.py, which serves a world's built
// section zooms as level 1 and slices of them as level 2 and builds nothing. The tile service (PW-1690) replaces it:
// want() becomes POST /api/tiles/want (replace the queue), has() says "buildable" for every existing tile, and a
// status poll tells lodtiles.js what is building (the badge).
export class StandinTileSource {
  constructor(world) { this.world = world; this.cells = new Map(); this.standin = true; }

  async open() {
    const r = await fetch(`/api/tiles/index?world=${encodeURIComponent(this.world)}`);
    if (!r.ok) throw new Error(`tiles index: ${r.status}`);
    const ix = await r.json();
    for (const c of ix.cells) {
      const tiles = {};
      for (const [lv, list] of Object.entries(c.tiles)) tiles[lv] = new Set(list.map(([x, y]) => `${x},${y}`));
      this.cells.set(c.id, { ...c, tiles });
    }
    return { cells: [...this.cells.values()] };
  }

  has(k) { return !!this.cells.get(k.cell)?.tiles[k.level]?.has(`${k.tx},${k.ty}`); }

  want(_keys) {}  // (the stand-in has every tile it lists already)

  url(k, file) { return `/api/tiles/${encodeURIComponent(this.world)}/${k.cell}/${k.level}/${k.tx}/${k.ty}/${file}`; }

  async elevation(k, signal) {
    const r = await fetch(this.url(k, 'view.bin'), { signal });
    if (!r.ok) throw new Error(`${k.id} view.bin: ${r.status}`);
    const buf = await r.arrayBuffer(), dv = new DataView(buf);
    if (dv.getUint32(0, false) !== 0x50575431) throw new Error(`${k.id}: not a PWT1 tile`);
    const n = dv.getInt32(4, true);
    return { n, half: new Uint16Array(buf, 8, n * n), water: new Uint8Array(buf, 8 + 2 * n * n, n * n) };
  }

  async satellite(k, signal) {
    const r = await fetch(this.url(k, 'satellite.png'), { signal });
    if (!r.ok) throw new Error(`${k.id} satellite: ${r.status}`);
    return createImageBitmap(await r.blob(), { imageOrientation: 'none', premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
  }

  async layer(k, name, signal) {
    const r = await fetch(this.url(k, `layer/${name}.bin`), { signal });
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`${k.id} ${name}: ${r.status}`);
    return new Float32Array(await r.arrayBuffer());
  }
}
