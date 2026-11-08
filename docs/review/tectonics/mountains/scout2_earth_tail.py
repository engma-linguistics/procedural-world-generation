"""Earth's sub-cell relief tail, at 1 km and at 4 km pixels (PW-1446 scout 188).
Same blocks as docs/review/tectonics/mountains/pw846_fit.py: 0.5 degree (60 x 30") HydroSHEDS blocks, >= 90% land,
local relief = 3x3 max-min of block means. Adds the 4 km view: the highest 4x4-pixel mean in the block."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, '.')
from tools.earth_data import _tiff
from numpy.lib.stride_tricks import sliding_window_view as sw

a, geo, nd = _tiff(Path("/home/daniel/personal/repos/procedural-world-generation/data/earth/raw_hydrosheds_dem_30s.zip"))
B, Q = 60, 4
h, w = (a.shape[0] // B) * B, (a.shape[1] // B) * B
R, C = h // B, w // B
mean = np.full((R, C), np.nan); mx = mean.copy(); mx4 = mean.copy(); fr = np.zeros((R, C))
for r in range(R):
    blk = a[r*B:(r+1)*B, :w].astype(np.float32)
    land = (blk > -1000) & (blk < 32000)
    v = np.where(land, blk, np.nan).reshape(B, C, B).transpose(1, 0, 2)  # C, B, B
    n = land.reshape(B, C, B).transpose(1, 0, 2).sum((1, 2))
    with np.errstate(all='ignore'):
        mean[r] = np.nanmean(v.reshape(C, -1), 1)
        mx[r] = np.nanmax(v.reshape(C, -1), 1)
        q = v.reshape(C, B // Q, Q, B // Q, Q)
        mx4[r] = np.nanmax(np.nanmean(q, (2, 4)).reshape(C, -1), 1)
    fr[r] = n / (B * B)
ok = fr > 0.9
m = np.where(ok, mean, np.nan)
p = np.pad(m, 1, constant_values=np.nan)
win = sw(p, (3, 3)).reshape(R, C, 9)
with np.errstate(all='ignore'):
    rel = np.nanmax(win, 2) - np.nanmin(win, 2)
sel = ok & np.isfinite(rel) & (m > 0)
m, rel, d1, d4 = m[sel], rel[sel], (mx - mean)[sel], (mx4 - mean)[sel]
print('blocks', len(m), 'max (highest 1 km px - mean)', int(d1.max()), 'max (4 km)', int(d4.max()))
edges = [0, 300, 700, 1200, 2000, 3000, 9000]
print('relief bin | n | 1 km: p75 p90 p99 max | 4 km: p75 p90 p99 max | mean-height median')
for lo, hi in zip(edges, edges[1:]):
    t = (rel >= lo) & (rel < hi)
    q1 = [int(np.percentile(d1[t], x)) for x in (75, 90, 99)] + [int(d1[t].max())]
    q4 = [int(np.percentile(d4[t], x)) for x in (75, 90, 99)] + [int(d4[t].max())]
    print(lo, hi, t.sum(), '|', *q1, '|', *q4, '|', int(np.median(m[t])))
print('mean bin | n | 4 km: p90 p99 max')
for lo, hi in ((3000, 4000), (4000, 5000), (5000, 7000)):
    t = (m >= lo) & (m < hi)
    print(lo, hi, t.sum(), '|', int(np.percentile(d4[t], 90)), int(np.percentile(d4[t], 99)), int(d4[t].max()))
