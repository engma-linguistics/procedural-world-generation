"""Highest zoom pixels: height over the local box mean (the landscape pass's summit cap is box mean + min(1.8 amp, 3 km)),
and over the world's cell mean. usage: peaks.py ZOOM_ID RAD_PX"""
import json, os, sys
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv


def uniform_filter(a, k):
    p = np.pad(a, k // 2, mode='edge')
    return swv(p, (k, k)).mean((2, 3))


def maximum_filter(a, k):
    p = np.pad(a, k // 2, mode='edge')
    return swv(p, (k, k)).max((2, 3))

ROOT = os.environ.get('ZROOT', '/home/daniel/personal/repos/procedural-world-generation')
zid, rad = sys.argv[1], int(sys.argv[2])
zd = f'{ROOT}/zooms/{zid}'
d = json.load(open(zd + '/zoom.json'))
sp = d['layers']['elevation']
e = np.fromfile(os.path.join(zd, sp['file']), dtype=sp['dtype']).reshape(sp['shape']).astype(float)
w = np.fromfile(os.path.join(zd, 'layers/water.bin'), dtype='u1').reshape(e.shape)
land = (w == 0).astype(float)
k = 2 * rad + 1
bm = uniform_filter(e * land, k) / np.maximum(uniform_filter(land, k), 1e-9)
peak = (e == maximum_filter(e, 2 * k + 1)) & (w == 0) & (e > 6000)
idx = np.argsort(-np.where(peak, e, -1e9).ravel())[:10]
print(f'zoom {zid}: {peak.sum()} local peaks > 6 km (isolated over {2*k+1} px); box radius {rad} px = {rad*d["res_km"]:.0f} km')
over = (e - bm)[peak]
print(f'  height over box mean at all those peaks: median {np.median(over):.0f}, p90 {np.percentile(over, 90):.0f}, max {over.max():.0f} m')
for i in idx:
    r, c = divmod(i, e.shape[1])
    if not peak[r, c]:
        continue
    print(f'  peak {e[r,c]:6.0f} m at ({r},{c}): box mean {bm[r,c]:6.0f}, over {e[r,c]-bm[r,c]:5.0f}')
