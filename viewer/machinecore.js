// The viewer's low-detail mode (PW-1721): the pure part (no DOM, no three.js), so node tests it (tests/test_machine.py).
// globe/machine.js reads the GPU, asks /api/machine for the machine presets (PW-1720) and applies the chosen budgets.
//
// Full detail is what the LOD globe was tuned with on a big discrete GPU (lodtiles.js: 120 tiles / 0.4 GB kept, 4 fetches,
// a tile's pixel refined past 1.5 screen pixels, down to level 4 = 25 m). Low detail keeps a third of the tiles and
// bytes, fetches two at a time, refines at 3 screen pixels (about a quarter as many tiles in view) and stops at level 3
// (250 m), and draws at one device pixel per CSS pixel (a 2x screen costs a quarter of the fill). Judgement, to be
// measured on an integrated GPU (the ticket's acceptance).

export const DETAIL = {
  full: { maxTiles: 120, maxBytes: 0.4e9, fetches: 4, refinePx: 1.5, maxLevel: 4, dprCap: 2 },
  low: { maxTiles: 40, maxBytes: 0.12e9, fetches: 2, refinePx: 3, maxLevel: 3, dprCap: 1 },
};
export const MODES = ['auto', 'low', 'full'];
export const MIN_TEXTURE = 8192;  // a GPU whose largest texture is smaller is an old or weak one
export const LOW_DEVICE_GB = 4;   // navigator.deviceMemory (rounded, Chrome only) at or under this: low

// gpu: {renderer, maxTexture, webgl2, deviceMemory}; preset: the machine presets' low_detail ("on" | "auto" | undefined).
// -> {low: bool, why: text}
export function autoDetail(gpu, preset) {
  const r = String(gpu?.renderer || '');
  if (gpu && gpu.webgl2 === false) return { low: true, why: 'no WebGL2' };
  if (/swiftshader|llvmpipe|softpipe|software|basic render/i.test(r)) return { low: true, why: 'software rendering' };
  if (/intel/i.test(r) && !/arc/i.test(r)) return { low: true, why: 'integrated graphics (Intel)' };
  if (gpu?.maxTexture && gpu.maxTexture < MIN_TEXTURE) return { low: true, why: `largest texture ${gpu.maxTexture} px` };
  if (gpu?.deviceMemory && gpu.deviceMemory <= LOW_DEVICE_GB) return { low: true, why: `${gpu.deviceMemory} GB device memory` };
  if (preset === 'on') return { low: true, why: 'the machine probe (integrated or small GPU, or under 16 GB RAM)' };
  return { low: false, why: r ? 'a capable GPU' : 'nothing says otherwise' };
}

// mode: 'auto' | 'low' | 'full' (the user's choice, else auto) -> {level: 'low' | 'full', why, budget}
export function chooseDetail(mode, gpu, preset) {
  const a = autoDetail(gpu, preset);
  const level = mode === 'low' ? 'low' : mode === 'full' ? 'full' : a.low ? 'low' : 'full';
  const why = mode === 'low' || mode === 'full' ? 'your choice' : a.why;
  return { level, why, budget: DETAIL[level] };
}

// the LOD settings to apply: the budget, except where the page's URL set them (?lodpx=, ?lodmax=) and the device
// pixel ratio (?dpr=) -> {maxTiles, maxBytes, fetches, refinePx?, maxLevel?, dpr?}
export function lodSettings(budget, url, devicePixelRatio, finest = 4) {
  const p = new URLSearchParams(url || '');
  const out = { maxTiles: budget.maxTiles, maxBytes: budget.maxBytes, fetches: budget.fetches };
  if (!p.get('lodpx')) out.refinePx = budget.refinePx;
  if (!p.get('lodmax')) out.maxLevel = Math.min(budget.maxLevel, finest);
  if (!p.has('dpr')) out.dpr = Math.min(devicePixelRatio || 1, budget.dprCap);
  return out;
}
