"""PW-680: test_bed_settles_under_the_ice's numbers on the L4 worlds (seeds 1-24, made 8 C colder): the median
|bed - want|, the tolerance with its lag from the global ice volume (the test as it is) and from each cell's own
load change over the last iso_tau (the proposed lag), and the same with a broken isostasy (BREAK: the bed relaxes
toward 0.8 of the load, or never moves). usage: bedtol.py OUT.txt [BREAK=none|scale|frozen] [seeds...]"""
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "tests")]
os.environ.setdefault("NUMBA_NUM_THREADS", "4")


def one(args):
    seed, brk = args
    import numpy as np
    import seeds
    from planet import timezoom as Z
    from planet.tectonics.isostasy import ice_load
    from planet.timezoom import params as P
    from planet.timezoom import sim as S
    if brk == "scale":
        def iso(self):
            self.bed += (self.bed_rest - 0.8 * self.load(self.grounded_ice()) - self.bed) * (1 - math.exp(-self.step / self.p.iso_tau))
        S._Sim.isostasy = iso
    elif brk == "frozen":
        S._Sim.isostasy = lambda self: None
    src = seeds.source4(seed)
    src["dT"] = src["dT"] - 8.0
    r = Z.simulate(src, kyr=40, step=0.5, every=2.0)
    s, g, p = r["state"], src["grid"], Z.TZParams()
    H0 = np.maximum(np.asarray(src["ice"], float), 0.0)
    flt = 1 - P.RHO_I / P.RHO_W
    H = np.where(s["bed"] + s["H"] > s["sl"] + flt * s["H"], s["H"], 0.0)
    want = src["elev"] + ice_load(g, H0, p.iso_ratio, p.flex_km) - ice_load(g, H, p.iso_ratio, p.flex_km)
    grew = H > H0 + 500
    if not grew.any():
        return seed, None
    bed = s["bed"] + s["cut"] - s["till"] - s["rock_iso"]
    t = [f["t"] for f in r["frames"]]
    v = [f["stats"]["ice_volume_mkm3"] for f in r["frames"]]
    lag = (v[-1] - np.interp(t[-1] - p.iso_tau, t, v)) / max(v[-1] - v[0], 1e-9)
    dip = np.median((H - H0)[grew]) * p.iso_ratio
    tol_old = (0.05 + max(lag, 0.0)) * dip + 20
    ice = np.asarray(r["data"]["ice"], float)
    tb = t[-1] - p.iso_tau
    k = np.searchsorted(t, tb) - 1
    w = (tb - t[k]) / (t[k + 1] - t[k])
    Lb = (1 - w) * ice_load(g, ice[k], p.iso_ratio, p.flex_km) + w * ice_load(g, ice[k + 1], p.iso_ratio, p.flex_km)
    dl = np.abs(ice_load(g, ice[-1], p.iso_ratio, p.flex_km) - Lb)[grew]
    tol_new = 0.05 * dip + np.median(dl) + 20
    err = float(np.median(np.abs(bed - want)[grew]))
    pressed = bool((bed[grew] < src["elev"][grew]).all())
    return seed, dict(n=int(grew.sum()), dip=float(dip), lag_share=float(lag), err=err, tol_old=float(tol_old),
                      tol_new=float(tol_new), cell_lag=float(np.median(dl)), pressed=pressed)


if __name__ == "__main__":
    out, brk = sys.argv[1], sys.argv[2]
    ss = [int(x) for x in sys.argv[3:]] or list(range(1, 25))
    with ProcessPoolExecutor(int(os.environ.get("W", "6")), mp_context=mp.get_context("spawn")) as ex:
        rows = list(ex.map(one, [(s, brk) for s in ss]))
    with open(out, "w") as f:
        for seed, d in rows:
            if d is None:
                print(f"seed {seed:3d}: no ice grew > 500 m", file=f)
                continue
            print(f"seed {seed:3d}: n {d['n']:4d} dip {d['dip']:6.1f} err {d['err']:6.1f} | old tol {d['tol_old']:6.1f} "
                  f"(lag share {d['lag_share']:+.3f}) {'pass' if d['err'] < d['tol_old'] and d['pressed'] else 'FAIL'}"
                  f" | new tol {d['tol_new']:6.1f} (cell lag {d['cell_lag']:5.1f}) "
                  f"{'pass' if d['err'] < d['tol_new'] and d['pressed'] else 'FAIL'} | pressed {d['pressed']}", file=f)
        ok = [d for _, d in rows if d]
        print(f"eligible {len(ok)} of {len(rows)}; old pass {sum(d['err'] < d['tol_old'] and d['pressed'] for d in ok)}, "
              f"new pass {sum(d['err'] < d['tol_new'] and d['pressed'] for d in ok)}", file=f)
