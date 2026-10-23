"""usage (tree root, PYTHONPATH=.:tests:THISDIR): eligibility_metrics.py EPS a-b OUT.json
Per L4 world: candidate start-state eligibility metrics + the forest test's outcome."""
import json
import os
import sys

os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import planet  # noqa
import numpy as np
import seeds


def job(arg):
    seed, eps = arg
    from helpers import run_sim
    from planet import climate, timezoom as Z
    from planet.timezoom.geometry import geometry
    from planet.timezoom.plants import Plants
    import test_timezoom as T
    src = Z.source_from_sim(run_sim(seed=seed, climate_offset=eps))
    out = {}
    try:
        T._forest_case(src, out)
        ok = True
    except AssertionError:
        ok = False
    g, tilt = src["grid"], src["tilt"]
    elev, H = np.asarray(src["elev"], float), np.maximum(np.asarray(src["ice"], float), 0.0)
    grounded = (H > 1.0) & (elev > 0)
    surf = np.where(grounded, elev + H, elev)
    area = geometry(g)["area"]
    pl = Plants(g, src, Z.TZParams(), tilt, area)

    def comp(veg):
        return climate.compute(g, surf, src["dT"], tilt, veg=veg)

    c = pl.step(0.0, comp(None), surf, grounded, H, 0.0, comp)
    t = pl.tune
    open_ = (surf > 0) & ~grounded
    sc = climate.snow_cover(g.lat, tilt, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], t)
    scm = sc.mean(0)
    tree0 = pl.tree
    hi = np.abs(g.lat) >= 40
    ref = pl.ref
    hid = (pl.sun * sc).mean(0) * ref["mask"] * (t["snow_albedo"] - ref["albedo"])
    A = float(area.sum())

    def W(x, m):
        return float((x * area)[m].sum())

    return dict(seed=seed, eps=eps, ok=ok, F=out.get("F_wm2"), run_dT=float(src["dT"]),
                snow0=W(scm, open_) / max(W(1, open_), 1),
                fs_all=W(tree0 * scm, open_) / max(W(tree0, open_), 1),
                fs_hi=W(tree0 * scm, open_ & hi) / max(W(tree0, open_ & hi), 1),
                fany=W(tree0 * (sc.max(0) > 0), open_) / max(W(tree0, open_), 1),
                tree_snow=W(tree0 * scm, open_) / 1e12, tree_lo=W(tree0, open_ & ~hi) / 1e12,
                tree_hi=W(tree0, open_ & hi) / 1e12, tree_all=W(tree0, open_) / 1e12,
                hid=pl.p.veg_toa * W(hid, open_) / A, hid_hi=pl.p.veg_toa * W(hid, open_ & hi) / A,
                mask_mean=W(ref["mask"] * tree0, open_) / max(W(tree0, open_), 1))


def main():
    eps = float(sys.argv[1])
    a, b = map(int, sys.argv[2].split("-"))
    rows = seeds.pool_map(job, [(s, eps) for s in range(a, b + 1)])
    json.dump(rows, open(sys.argv[3], "w"), indent=0)


if __name__ == "__main__":
    sys.modules.setdefault("eligibility_metrics", sys.modules["__main__"])
    main()
