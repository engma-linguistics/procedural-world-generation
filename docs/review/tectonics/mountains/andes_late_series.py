"""PW-1680 lane 286 (andes-late.md): per checkpoint of a run (every 20 Myr, t >= 100 Myr), which high ground there
is and what it does to the carbon cycle. Read-only.

Per checkpoint:
- land above 3 and 4 km (% of land, sim.w_elev, the scorecard's measure);
- of the land above 4 km: the share squeezed in the last collapse_delay Myr (live: collapse does not act on it) and
  the share near a live ocean-continent margin (scout6_measure's zone, from the keyframe nearest t; "Andean");
  the rest of the live part is collision or inland stacking; the dead part is what collapse should be taking down;
- the carbon cycle: co2 (ln of the stock against the balance), dT, land ice % of land, the weathering supply
  (bare ground's erosion, earth.weathering) as a total and the share of it from land above 2 and 3 km.
usage: PYTHONPATH=. andes_late_series.py RUN_DIR [RUN_DIR ...]   (--every N: every Nth checkpoint)"""
import sys
from pathlib import Path

import numpy as np

from planet import store as S
from planet import timeline as T
from planet.grid import build_grid
from planet.tectonics.params import Params
from planet.tectonics.record import NEVER, T_FOLD
from planet.tectonics.simulation import Simulation

sys.path.insert(0, str(Path(__file__).parent))
from scout6_measure import dilate  # noqa: E402


def zones(r, arr, g, t, k, k_oc, k_cc):
    """The Andes zone (scout6_measure's: within k = 2 L6 / 4 L7 cells of the continental side of a converging
    ocean-continent plate edge) and, for attribution, wider ones: within k_oc cells of that edge (the Andean belt
    reaches ~3 x ANDES_BELT = 3.6 L5 cells, ~7 L6 cells, behind it) and within k_cc cells of a continent-continent
    plate edge (collision belts). k_oc, k_cc are L6 cells; doubled at L7."""
    i = int(np.argmin([abs(f["t"] - t) for f in r["frames"]]))
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    pl, cr, pb = T.frame(r, arr, "plate", i), T.frame(r, arr, "crust", i) > 0, T.frame(r, arr, "plate_boundary", i)
    edge = (pl[ea] != pl[eb]) & ((pb[ea] > 0) | (pb[eb] > 0))
    oc, cc = edge & (cr[ea] != cr[eb]), edge & cr[ea] & cr[eb]
    m = np.zeros(g.n, bool)
    m[np.where(cr[ea[oc]], ea[oc], eb[oc])] = True
    c = np.zeros(g.n, bool)
    c[ea[cc]] = c[eb[cc]] = True
    return dilate(g, m, k) & cr, dilate(g, m, k_oc) & cr, dilate(g, c, k_cc) & cr


def series(rd, every=1):
    rd = Path(rd)
    m = S.read_header(rd / "run.json")["meta"]
    g = build_grid(m["level"])
    params = Params.from_stored(m["params"])
    delay = max(params.collapse_delay, 20.0)
    r, arr = T.load_frames(rd, ["plate", "crust", "plate_boundary"])
    rows = []
    for t in [t for t in S.checkpoints(rd) if t >= 100][::every]:
        sim = Simulation.from_state(g, m["seed"], params, m["dt"], S.load_checkpoint(rd, t, g))
        e, rec = sim.w_elev, sim.w_rec
        land = e > 0
        nl = max(land.sum(), 1)
        h3, h4 = e > 3000, e > 4000
        age = np.where(rec[:, T_FOLD] <= NEVER / 2, np.inf, t - rec[:, T_FOLD])
        live = age < delay
        f = 2 if m["level"] >= 7 else 1
        zone, z5, zc = zones(r, arr, g, t, 2 * f, 5 * f, 3 * f)
        cont = sim.w_cont
        n4 = max(h4.sum(), 1)
        sup = sim.weathered * land * g.area_weight
        st = sup.sum()
        ice = (np.asarray(sim.ice) > 0) & land if sim.ice is not None else np.zeros(g.n, bool)
        rows.append(dict(t=t, gt3=100 * h3.sum() / nl, gt4=100 * h4.sum() / nl,
                         live4=100 * (h4 & live).sum() / n4, andes4=100 * (h4 & zone).sum() / n4,
                         andes3=100 * (h3 & zone).sum() / max(h3.sum(), 1),
                         oc5_4=100 * (h4 & live & z5 & ~zc).sum() / n4, cc_4=100 * (h4 & live & zc).sum() / n4,
                         cont=100 * cont.mean(), thick=float(sim.w_thick[cont].mean()),
                         npp=float(np.asarray(sim.npp)[land].mean()) if sim.npp is not None else 0.0,
                         co2=float(sim.co2), dT=float(sim.dT), ice=100 * ice.sum() / nl,
                         sup=float(st), sup2=100 * sup[e > 2000].sum() / max(st, 1e-30),
                         sup3=100 * sup[h3].sum() / max(st, 1e-30)))
    return m, params, rows


if __name__ == "__main__":
    args = sys.argv[1:]
    every = 1
    if "--every" in args:
        i = args.index("--every")
        every = int(args[i + 1])
        del args[i:i + 2]
    for rd in args:
        m, p, rows = series(rd, every)
        print(f"# {Path(rd).name} seed {m['seed']} L{m['level']} andean_shortening {p.andean_shortening} collapse {p.collapse}")
        print("   t | >3km >4km | of >4km: live% andes% oc5only% cc3% | andes% of >3km | cont% thick | co2    dT   ice%  npp | supply  sup>2km% sup>3km%")
        for x in rows:
            print(f"{x['t']:4.0f} | {x['gt3']:4.2f} {x['gt4']:4.2f} | {x['live4']:5.1f} {x['andes4']:5.1f} {x['oc5_4']:5.1f} {x['cc_4']:5.1f} | {x['andes3']:5.1f} |"
                  f" {x['cont']:4.1f} {x['thick']:4.1f} |"
                  f" {x['co2']:+5.2f} {x['dT']:+5.1f} {x['ice']:5.1f} {x['npp']:4.0f} | {x['sup']:7.3g} {x['sup2']:5.1f} {x['sup3']:5.1f}")
        for t0, t1 in ((100, 600), (600, 1000), (900, 1000)):
            a = [x for x in rows if t0 <= x["t"] <= t1]
            if a:
                print(f"median {t0}-{t1}: >3km {np.median([x['gt3'] for x in a]):.2f} >4km {np.median([x['gt4'] for x in a]):.2f}"
                      f" andes% of >3km (pooled) {100 * sum(x['andes3'] * x['gt3'] for x in a) / max(sum(x['gt3'] for x in a), 1e-9) / 100:.1f}")
        a = [x for x in rows if x["t"] >= 600]
        if a:
            print("late mean (t>=600):", " ".join(f"{k} {np.mean([x[k] for x in a]):.3g}" for k in
                                                  ("gt3", "gt4", "live4", "andes4", "oc5_4", "cc_4", "andes3", "cont", "thick", "co2", "dT", "ice", "npp", "sup", "sup3")))
