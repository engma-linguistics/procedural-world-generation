"""Per zoom: highest pixel, and (highest pixel - world cell mean) p75 by local relief against Earth's 4 km table
(scout 188, scout2.md section 3), plus plateau (mean > 2 km, local relief < 700 m) and lowland (mean < 500 m) groups.
usage: ZROOT=... measure.py ZOOM_ID..."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.getcwd())
from planet import world as W, summit
from planet.zoom import regional as RG

ROOT = os.environ["ZROOT"]
EDGES = [0, 300, 700, 1200, 2000, 3000, 9000]
EARTH4 = [128, 554, 844, 1255, 1703, 2086]  # Earth 4 km p75 (HydroSHEDS 0.5-degree blocks), scout2.md section 3
w = None
for zid in sys.argv[1:]:
    zd = f"{ROOT}/zooms/{zid}"
    d = json.load(open(zd + "/zoom.json"))
    if w is None:
        w = W.load(f"{ROOT}/worlds/{d['source_world']['id']}.json")
        g, L = w["grid"], w["layers"]
        E = np.asarray(L["elevation"], float)
        LR = summit.local_relief(g, E)
    nx, ny, res = d["nx"], d["ny"], d["res_km"]
    sp = d["layers"]["elevation"]
    e = np.fromfile(os.path.join(zd, sp["file"]), dtype=sp["dtype"]).reshape(sp["shape"]).astype(float).ravel()
    wat = np.fromfile(os.path.join(zd, "layers/water.bin"), dtype="u1").ravel()
    fr = RG.frame_of(d["center"])
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    own = g.locate(fr.to_sphere(X.ravel(), Y.ravel()))
    land = wat == 0
    cells, inv, cnt = np.unique(own, return_inverse=True, return_counts=True)
    zmax = np.full(len(cells), -1e9)
    np.maximum.at(zmax, inv[land], e[land])
    zmean = np.bincount(inv, e, len(cells)) / cnt
    em, lr = E[cells], LR[cells]
    ok = (cnt >= 0.6 * cnt.max()) & (em > 0) & (zmax > -1e8)
    dz = zmax - em
    c = d["center"]
    print(f"== {zid} at {c}: {ok.sum()} full land cells; highest cell {em[ok].max():.0f} m; highest pixel "
          f"{e[land].max():.0f} m; zoom-world cell mean median {np.median(zmean[ok] - em[ok]):+.0f} m")
    row = []
    for (a, b), ea in zip(zip(EDGES[:-1], EDGES[1:]), EARTH4):
        s = ok & (lr >= a) & (lr < b)
        row.append(f"{a}-{b}: {np.percentile(dz[s], 75):.0f} [{ea}] n{s.sum()}" if s.sum() >= 3 else f"{a}-{b}: -")
    print("  p75 by local relief [Earth 4 km]:", " | ".join(row))
    for name, s in (("plateau (mean>2km, lr<700)", ok & (em > 2000) & (lr < 700)),
                    ("high (mean>3km)", ok & (em > 3000)),
                    ("lowland (mean<500)", ok & (em < 500))):
        if s.sum() >= 3:
            ref = np.median(np.interp(lr[s], [150, 500, 950, 1600, 2500, 3500], EARTH4))
            print(f"  {name}: n {s.sum()}, p75 {np.percentile(dz[s], 75):.0f} m, p90 {np.percentile(dz[s], 90):.0f}, "
                  f"max {dz[s].max():.0f} (Earth 4 km p75 at their local relief ~{ref:.0f}; median lr {np.median(lr[s]):.0f})")
