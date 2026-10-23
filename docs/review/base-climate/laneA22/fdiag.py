"""usage (from a tree root, PYTHONPATH=.:tests): fdiag.py CACHE.pkl OUT.json [seeds 1-24]

The forest-to-tundra test's forcing F taken apart on each L4 300 Myr world (seeds 1-24), with the world's own
numbers beside it. The sources are built once (CACHE.pkl, seeds.source4 in a pool) so a second tree's worlds can be
read with the first tree's climate (CLIMATE_TREE=path puts that tree's planet first on sys.path before import).

F = -veg_toa x mean over months and the start's open land of sun x (albedo(plants now) - albedo(start's)),
at the cold climate's snow. Split here:
  - snow-free part (1 - sc) x (a_free change) and snowy part sc x (a_snow change)
  - cells that lost trees (tree drop > 0.05), gained them (rise > 0.05), and the rest
  - |lat| < 40 and >= 40
"""
import json
import os
import pickle
import sys
import time

os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import planet  # noqa: F401  (before numpy)
import numpy as np

import seeds


def case(src):
    from planet import climate
    from planet import timezoom as Z
    from planet.timezoom.geometry import geometry
    from planet.timezoom.plants import Plants

    g, tilt = src["grid"], src["tilt"]
    elev, H = np.asarray(src["elev"], float), np.maximum(np.asarray(src["ice"], float), 0.0)
    grounded = (H > 1.0) & (elev > 0)
    surf = np.where(grounded, elev + H, elev)
    area = geometry(g)["area"]
    pl = Plants(g, src, Z.TZParams(), tilt, area)

    def compute(dT):
        return lambda veg: climate.compute(g, surf, src["dT"] + dT, tilt, veg=veg)

    c00 = pl.step(0.0, compute(0.0)(None), surf, grounded, H, 0.0, compute(0.0))
    tree0 = pl.tree.copy()
    c = compute(-4.0)(pl.feedback(grounded))
    t0 = c["temp"].copy()
    c = pl.step(10.0, c, surf, grounded, H, -1.0, compute(-4.0))
    lat = g.lat
    lost = (surf > 0) & ~grounded & (np.abs(lat) > 40) & (tree0 - pl.tree > 0.2)
    A = float(area.sum())
    t = pl.tune
    open_ = (surf > 0) & ~grounded & pl.land0
    args = (lat, tilt, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"])
    sc = climate.snow_cover(*args, t)
    new, ref = pl.raw, pl.ref
    a_sn = lambda v: v["mask"] * v["albedo"] + (1 - v["mask"]) * t["snow_albedo"]  # noqa: E731
    d_free = (1 - sc) * (new["albedo"] - ref["albedo"])[None, :]
    d_snow = sc * (a_sn(new) - a_sn(ref))[None, :]
    toa = pl.p.veg_toa

    def F(d, m):
        dF = np.where(open_ & m, -toa * (d * pl.sun).mean(0), 0.0)
        return float((dF * area).sum()) / A

    dtree = pl.tree - tree0
    al = np.abs(lat)
    out = dict(seed=int(src["seed"]), run_dT=float(src["dT"]), lost=int(lost.sum()),
               cooling=float((c["temp"] - t0)[lost].mean()) if lost.any() else float("nan"),
               F=float(pl.series[-1]["F_wm2"]), belts=pl.series[-1]["F_belts"])
    every = np.ones(g.n, bool)
    for nm, m in (("all", every), ("loss", dtree < -0.05), ("gain", dtree > 0.05),
                  ("rest", np.abs(dtree) <= 0.05)):
        for bn, bm in (("", every), ("_lo", al < 40), ("_hi", al >= 40)):
            out[f"F_{nm}{bn}_free"] = round(F(d_free, m & bm), 4)
            out[f"F_{nm}{bn}_snow"] = round(F(d_snow, m & bm), 4)
    # where the bare-ground share changed (desert <-> grass: 0.30 against ~0.19)
    cov = lambda v: v["albedo"]  # noqa: E731
    land = surf > 0
    ocean = ~land
    depth = -elev
    out.update(
        land_frac=float(area[land].sum() / A),
        land_hi45=float(area[land & (al >= 45)].sum() / max(area[land].sum(), 1)),
        land_lo30=float(area[land & (al < 30)].sum() / max(area[land].sum(), 1)),
        land_nh=float(area[land & (lat > 0)].sum() / max(area[land].sum(), 1)),
        ice_land=float(area[grounded].sum() / max(area[land].sum(), 1)),
        shelf_frac=float(area[ocean & (depth < 500)].sum() / max(area[ocean].sum(), 1)),
        sea_level=float(src["sea_level"]),
        co2=float((src.get("veg") or {}).get("co2", np.nan)),
        t_land0=float((c00["temp"] * area)[open_].sum() / max(area[open_].sum(), 1)),
        sst0=float((c00["sst"] * area)[ocean].sum() / max(area[ocean].sum(), 1)),
        seaice0=float(area[ocean & (c00["sst"] <= -1.79)].sum() / max(area[ocean].sum(), 1)),
        tree0_mkm2=float((tree0 * area)[open_].sum() / 1e12),
        tree0_hi50=float((tree0 * area)[open_ & (al >= 50)].sum() / 1e12),
        tree0_4050=float((tree0 * area)[open_ & (al >= 40) & (al < 50)].sum() / 1e12),
        tree0_lo40=float((tree0 * area)[open_ & (al < 40)].sum() / 1e12),
        dtree_lo40=float((dtree * area)[open_ & (al < 40)].sum() / 1e12),
        dtree_hi40=float((dtree * area)[open_ & (al >= 40)].sum() / 1e12),
        snow0_land=float((climate.snow_cover(lat, tilt, c00["temp"], c00["t_warm"], c00["t_cold"], c00["p_jul"],
                                             c00["p_jan"], t).mean(0) * area)[open_].sum() / max(area[open_].sum(), 1)),
        dalb_free_lo40=float(((new["albedo"] - ref["albedo"]) * area)[open_ & (al < 40)].sum()
                             / max(area[open_ & (al < 40)].sum(), 1)),
    )
    _ = cov
    return out


def main():
    cache, outp = sys.argv[1], sys.argv[2]
    a, b = map(int, (sys.argv[3] if len(sys.argv) > 3 else "1-24").split("-"))
    S = list(range(a, b + 1))
    t0 = time.time()
    if os.path.exists(cache):
        src = pickle.loads(open(cache, "rb").read())
    else:
        src = list(zip(S, seeds.pool_map(source, S)))
        open(cache, "wb").write(pickle.dumps(src))
    print("built", round(time.time() - t0), flush=True)
    rows = seeds.pool_map(case_job, [s for _, s in src])
    json.dump(rows, open(outp, "w"), indent=1)
    print("done", round(time.time() - t0), flush=True)


def source(seed):
    """seeds.source4, or with PW_EPS set, the run with climate_offset PW_EPS C (a null perturbation: the same
    physics, another chaotic draw of the worlds)."""
    eps = float(os.environ.get("PW_EPS", "0") or 0)
    if not eps:
        return seeds.source4(seed)
    from helpers import run_sim
    from planet import timezoom as Z
    return Z.source_from_sim(run_sim(seed=seed, climate_offset=eps))


def case_job(s):
    return case(s)


if __name__ == "__main__":
    sys.modules.setdefault("fdiag", sys.modules["__main__"])
    main()
