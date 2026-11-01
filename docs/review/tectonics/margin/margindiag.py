"""tools/ice_diag.py with continental-margin numbers added to the recorded steps (PW-950), every 50 Myr from 100 Myr:
- shelf: 0..-200 m, % of the ocean; slope: -200..-3000 m, % of the ocean; abyss4_5: -4000..-5000 m, % of the ocean
- sub_med: median elevation (m) of submerged continental crust
- c3000_km: median distance (km, hops x cell spacing) from a coast cell (land with a sea neighbour) to the nearest
  cell deeper than 3000 m; near1 / near2: % of coast cells with such a cell within 1 / 2 hops
- prof_t / prof_e: median crust (km) and elevation (m) at signed hops -3..-1 (continental) and +1..+3 (oceanic)
  from the continent-ocean crust boundary; edge_strain: median rift strain (record.RIFT_STRAIN) of the hop -1 cells
- cont, land, thick: continental and land % of the surface, mean continental crust (km)
Same arguments as ice_diag; run from the code checkout being judged (cwd). Reads the sim, changes nothing. Harness only."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.tectonics import diag, record  # noqa: E402

_step = diag.Recorder.step


def hops(nbr_off, nbr_idx, src, allowed, maxd=12):
    """BFS hop distance from src cells (0) through allowed cells; -1 beyond maxd or unreachable."""
    n = len(nbr_off) - 1
    d = np.full(n, -1, np.int32)
    d[src] = 0
    front = np.flatnonzero(src)
    src_of = np.repeat(np.arange(n), np.diff(nbr_off))
    for k in range(1, maxd + 1):
        if not len(front):
            break
        m = np.zeros(n, bool)
        m[front] = True
        e = m[src_of]
        nb = nbr_idx[e]
        nb = nb[(d[nb] < 0) & allowed[nb]]
        nb = np.unique(nb)
        d[nb] = k
        front = nb
    return d


def margin(sim):
    g = sim.grid
    e, cont = sim.bed(), sim.w_cont
    sea = e <= 0
    off, idx = g.nbr_off, g.nbr_idx
    src_of = np.repeat(np.arange(g.n), np.diff(off))
    km = float(sim.edge_len * R_KM)
    any_nb = lambda mask: np.logical_or.reduceat(mask[idx], off[:-1])  # noqa: E731
    out = {}
    se = e[sea]
    out["shelf"] = round(100 * float((se > -200).mean()), 2)
    out["slope"] = round(100 * float(((se <= -200) & (se > -3000)).mean()), 2)
    out["abyss4_5"] = round(100 * float(((se <= -4000) & (se > -5000)).mean()), 2)
    sub = sea & cont
    out["sub_med"] = int(np.median(e[sub])) if sub.any() else 0
    deep = e < -3000
    coast = ~sea & any_nb(sea)
    dd = hops(off, idx, deep, np.ones(g.n, bool), 40)
    dc = dd[coast]
    dc = np.where(dc < 0, 41, dc)
    out["c3000_km"] = int(np.median(dc) * km)
    out["near1"] = round(100 * float((dc <= 1).mean()), 1)
    out["near2"] = round(100 * float((dc <= 2).mean()), 1)
    # signed hops from the continent-ocean crust boundary
    edge_c = cont & any_nb(~cont)
    edge_o = ~cont & any_nb(cont)
    hc = hops(off, idx, edge_c, cont, 3)
    ho = hops(off, idx, edge_o, ~cont, 3)
    pt, pe = [], []
    for k in (2, 1, 0):
        m = hc == k
        pt.append(round(float(np.median(sim.w_thick[m])), 1) if m.any() else None)
        pe.append(int(np.median(e[m])) if m.any() else None)
    for k in (0, 1, 2):
        m = ho == k
        pt.append(round(float(np.median(sim.w_thick[m])), 1) if m.any() else None)
        pe.append(int(np.median(e[m])) if m.any() else None)
    out["prof_t"], out["prof_e"] = pt, pe
    # the same profile on rifted margins only: boundary cells whose continental side rifted in the last 150 Myr
    # and hasn't been folded since (passive margins young enough to show their rift)
    rec = sim.w_rec
    young = cont & (sim.t - rec[:, record.T_RIFT].astype(float) < 150) & (rec[:, record.T_FOLD] <= rec[:, record.T_RIFT])
    near_young = any_nb(young & edge_c)
    rt, re_ = [], []
    for k in (2, 1, 0):
        m = (hc == k) & young
        rt.append(round(float(np.median(sim.w_thick[m])), 1) if m.any() else None)
        re_.append(int(np.median(e[m])) if m.any() else None)
    m = (ho == 0) & near_young
    rt.append(round(float(np.median(sim.w_thick[m])), 1) if m.any() else None)
    re_.append(int(np.median(e[m])) if m.any() else None)
    out["rift_t"], out["rift_e"] = rt, re_
    out["rift_edge_share"] = round(100 * float((young & edge_c).sum() / max(edge_c.sum(), 1)), 1)
    st = sim.w_rec[edge_c, record.RIFT_STRAIN].astype(float)
    out["edge_strain"] = round(float(np.median(np.maximum(st, 0))), 3) if len(st) else 0.0
    out["cont"] = round(100 * float(cont.mean()), 2)
    out["land"] = round(100 * float((~sea).mean()), 2)
    out["thick"] = round(float(sim.w_thick[cont].mean()), 2)
    out["km"] = round(km, 1)
    return out


def step(self, sim):
    _step(self, sim)
    t = float(sim.t)
    if t < 100 or abs(t / 50 - round(t / 50)) > 1e-6:
        return
    self.steps[-1]["margin"] = margin(sim)


diag.Recorder.step = step
sys.argv = [str(Path.cwd() / "tools" / "ice_diag.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
