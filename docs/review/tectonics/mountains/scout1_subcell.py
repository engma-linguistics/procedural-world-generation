"""Earth's sub-cell relief: in ~0.5 deg (~55 km, an L7 cell) blocks of the HydroSHEDS 30" DEM, the highest
pixel against the block's mean land height. Read-only on data/earth."""
import sys
import zipfile

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))
from pathlib import Path
from tools.earth_data import _tiff

Z = "/home/daniel/personal/repos/procedural-world-generation/data/earth/raw_hydrosheds_dem_30s.zip"
a, geo, nodata = _tiff(Path(Z))
print("geo", geo, "nodata", nodata)
print("shape", a.shape, a.dtype, "min", a.min(), "max", a.max())
B = int(sys.argv[1]) if len(sys.argv) > 1 else 60
h, w = (a.shape[0] // B) * B, (a.shape[1] // B) * B
mean = np.zeros((h // B, w // B))
mx = np.zeros_like(mean)
nland = np.zeros_like(mean)
for r in range(h // B):
    blk = a[r * B:(r + 1) * B, :w].reshape(B, w // B, B).transpose(1, 0, 2).reshape(w // B, B * B).astype(float)
    land = (blk > -1000) & (blk < 32000)
    blk[~land] = np.nan
    n = land.sum(1)
    with np.errstate(all="ignore"):
        mean[r] = np.where(n > 0, np.nansum(np.where(land, blk, 0), 1) / np.maximum(n, 1), np.nan)
        mx[r] = np.where(n > 0, np.nanmax(np.where(land, blk, -1e9), 1), np.nan)
    nland[r] = n / (B * B)
ok = nland > 0.9
m, x = mean[ok], mx[ok]
print(f"block {B} px ({B/120:.2f} deg): highest block mean {m.max():.0f} m, highest pixel {x.max():.0f} m")
print(" mean-height bin   blocks  median(max-mean)  p90(max-mean)  highest pixel")
for lo, hi in ((0, 500), (500, 1000), (1000, 2000), (2000, 3000), (3000, 4000), (4000, 5000), (5000, 7000)):
    s = (m >= lo) & (m < hi)
    if s.any():
        d = x[s] - m[s]
        print(f" {lo:5d}-{hi:5d} m  {s.sum():7d}  {np.median(d):8.0f}  {np.percentile(d, 90):8.0f}  {x[s].max():8.0f}")
for thr in (4000, 5000, 6000, 7000, 8000):
    print(f" blocks whose highest pixel > {thr} m: {(x > thr).sum()}, of them block mean median {np.median(m[x > thr]) if (x > thr).any() else 0:.0f} m")
