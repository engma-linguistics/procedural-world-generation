"""Per-frame hypsometry, crust-thickness tail and active collision zones of stored runs (read-only).
usage: hyps.py RUN_DIR [RUN_DIR ...]  (or 'earth')"""
import json
import sys
from pathlib import Path

import numpy as np

from planet import timeline as T
from planet.grid import shared_grid

MAIN = Path("/home/daniel/personal/repos/procedural-world-generation")


def hyps(e, land):
    le = e[land]
    n = max(len(le), 1)
    return {f"gt{k}": 100.0 * (le > k * 1000).sum() / n for k in (1, 2, 3, 4)} | {
        "max": float(e.max()), "p99": float(np.percentile(le, 99)) if len(le) else 0}


def earth():
    for lv in (6, 7):
        d = np.load(MAIN / f"data/earth/L{lv}.npz")
        elev, ice, surf = d["elev"].astype(float), d["ice"].astype(float), d["surface"].astype(float)
        land = surf > 0
        noice = land & (ice < 10)
        print(f"Earth L{lv} bed, all land  ", fmt(hyps(elev, land)))
        print(f"Earth L{lv} ice-free land   ", fmt(hyps(elev, noice)))
        print(f"Earth L{lv} surface (ice top)", fmt(hyps(surf, land)))
    b = np.load(MAIN / "data/earth/raw_etopo_bed.npz")
    i = np.load(MAIN / "data/earth/raw_etopo_ice.npz")
    lat = b["lat"]
    w = np.cos(np.radians(lat))[:, None] * np.ones_like(b["val"], float)
    bed, top = b["val"].astype(float), i["val"].astype(float)
    land = top > 0
    noice = land & (top - bed < 10)
    for name, m, z in (("all land, ice top", land, top), ("ice-free land", noice, bed)):
        W = w[m].sum()
        s = {f"gt{k}": 100 * w[m & (z > k * 1000)].sum() / W for k in (1, 2, 3, 4)} | {"max": z[m].max(), "p99": 0}
        print(f"Earth ETOPO1 10' {name:18s}", fmt(s))


def fmt(s):
    return " ".join(f"{k}={v:6.2f}" if k.startswith("gt") else f"{k}={v:5.0f}" for k, v in s.items())


def run(rd):
    rd = Path(rd)
    r, arr = T.load_frames(rd, ["elevation", "crust_thickness", "plate", "crust", "plate_boundary"])
    lv = r["meta"]["level"]
    g = shared_grid(lv)
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    rows = []
    nf = len(r["frames"])
    for i in range(0, nf, max(1, nf // 50)):
        e = T.frame(r, arr, "elevation", i).astype(float)
        th = T.frame(r, arr, "crust_thickness", i).astype(float)
        pl = T.frame(r, arr, "plate", i)
        cr = T.frame(r, arr, "crust", i) > 0
        land = e > 0
        h = hyps(e, land)
        c = th[cr]
        # active collision: a grid edge between two continental cells of different plates, converging
        pb = T.frame(r, arr, "plate_boundary", i)
        coll = cr[ea] & cr[eb] & (pl[ea] != pl[eb]) & ((pb[ea] > 0) | (pb[eb] > 0))
        m = np.zeros(g.n, bool)
        m[ea[coll]] = True
        m[eb[coll]] = True
        lab, nz = g.components(m)
        big = np.bincount(lab[lab >= 0]).astype(int) if nz else np.zeros(0, int)
        zones = int((big >= 3).sum())
        rows.append(dict(t=r["frames"][i]["t"], **h, th60=100 * (c > 60).mean(), th70=100 * (c > 70).mean(),
                         th78=100 * (c >= 78).mean(), thmax=c.max(), zones=zones, zcells=int(m.sum()),
                         plates=r["frames"][i]["stats"].get("plates"), speed=r["frames"][i]["stats"].get("mean_speed_cmyr")))
    print(f"== {rd.name} {r['name']} L{lv} seed {r['meta']['seed']} code {r['meta']['code'].get('commit')}")
    print("   t   >1km  >2km  >3km  >4km   max  p99 | cont>60 >70 >=78 thmax | zones zcells plates speed")
    for x in rows:
        print(f"{x['t']:6.0f} {x['gt1']:5.1f} {x['gt2']:5.2f} {x['gt3']:5.2f} {x['gt4']:5.2f} {x['max']:5.0f} {x['p99']:5.0f}"
              f" | {x['th60']:5.2f} {x['th70']:5.2f} {x['th78']:5.2f} {x['thmax']:3.0f} | {x['zones']:3d} {x['zcells']:5d}"
              f" {x['plates']} {x['speed']}")
    late = [x for x in rows if x["t"] >= 100]
    def med(k): return float(np.median([x[k] for x in late]))
    early = [x for x in rows if 100 <= x["t"] <= 500]
    lt = [x for x in rows if x["t"] > 500]
    def med2(rs, k): return float(np.median([x[k] for x in rs])) if rs else float("nan")
    print(f"SUMMARY {rd.name} L{lv}: median(t>=100) >2km {med('gt2'):.2f} >3km {med('gt3'):.2f} >4km {med('gt4'):.2f}"
          f" max {med('max'):.0f} cont>60 {med('th60'):.2f} >=78 {med('th78'):.2f} zones {med('zones'):.1f}"
          f" | 100-500: >4km {med2(early,'gt4'):.2f} zones {med2(early,'zones'):.1f} | >500: >4km {med2(lt,'gt4'):.2f} zones {med2(lt,'zones'):.1f}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        earth() if a == "earth" else run(a)
