import sys, numpy as np
from pathlib import Path
sys.path.insert(0, '.')
from tools.earth_data import _tiff
from numpy.lib.stride_tricks import sliding_window_view as sw
a, geo, nd = _tiff(Path("/home/daniel/personal/repos/procedural-world-generation/data/earth/raw_hydrosheds_dem_30s.zip"))
B = 60
h, w = (a.shape[0] // B) * B, (a.shape[1] // B) * B
R, C = h // B, w // B
mean = np.full((R, C), np.nan); mx = mean.copy(); fr = np.zeros((R, C))
for r in range(R):
    blk = a[r*B:(r+1)*B, :w].reshape(B, C, B).transpose(1, 0, 2).reshape(C, B*B).astype(float)
    land = (blk > -1000) & (blk < 32000)
    n = land.sum(1)
    mean[r] = np.where(n > 0, np.where(land, blk, 0).sum(1) / np.maximum(n, 1), np.nan)
    mx[r] = np.where(n > 0, np.where(land, blk, -1e9).max(1), np.nan)
    fr[r] = n / (B*B)
ok = fr > 0.9
m = np.where(ok, mean, np.nan)
p = np.pad(m, 1, constant_values=np.nan)
win = sw(p, (3, 3)).reshape(R, C, 9)
with np.errstate(all='ignore'):
    rel = np.nanmax(win, 2) - np.nanmin(win, 2)
d = mx - mean
sel = ok & np.isfinite(rel)
np.savez(sys.argv[1], m=m[sel], rel=rel[sel], d=d[sel])
m, rel, d = m[sel], rel[sel], d[sel]
print(len(m))
edges = [0, 100, 200, 400, 600, 800, 1000, 1300, 1700, 2200, 3000, 9000]
print("relief bin: blocks, median relief, p50 / p75 / p90 of (highest - mean) = RELIEF_KNOTS source in planet/summit.py")
for lo, hi in zip(edges, edges[1:]):
    t = (m > 0) & (rel >= lo) & (rel < hi)
    print(lo, hi, t.sum(), int(np.median(rel[t])), *[int(np.percentile(d[t], q)) for q in (50, 75, 90)])
for lo, hi in ((0, 500), (500, 1000), (1000, 2000), (2000, 3000), (3000, 4000), (4000, 5000), (5000, 7000)):
    print(lo, hi, end=' ')
    for rl, rh in ((0, 300), (300, 800), (800, 1500), (1500, 9000)):
        s = (m >= lo) & (m < hi) & (rel >= rl) & (rel < rh)
        print(f"| {s.sum():5d} {np.median(d[s]) if s.sum() > 5 else 0:5.0f} {np.percentile(d[s], 90) if s.sum() > 5 else 0:5.0f}", end=' ')
    print()
