"""Cell churn: how often continental cells flip and flip back within a few
keyframes (PW-108). Real relief and crust type change over tens of Myr, so a
cell that turns oceanic, changes plate or jumps by kilometres for one or two
4 Myr frames and then returns is a model artifact.

    PYTHONPATH=. uv run python tools/churn.py <run id> [--from T] [--to T]

For each frame a (continental cells only), a cell *churns* if within the
next two frames it leaves its state and comes back:
  crust     continental -> oceanic -> continental
  plate     plate p -> another plate -> p
  relief    ground (without ice) jumps > 2 km away and back to within 1 km
and, the other way round, ocean_flip: oceanic -> continental -> oceanic.
The shares are of continental cells, overall and near converging boundaries
(within 3 cells of one, at frame a or b). Also reports 'spike': pits and
peaks in continents, cells more than 2 km above or below the median of
their (at least 4) continental neighbours.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from planet import store as S  # noqa: E402
from planet import timeline as T  # noqa: E402
from planet.grid import build_grid  # noqa: E402

JUMP = 2000.0  # m
BACK = 1000.0  # m


def dilate(mask, grid, n=3):
    m = mask.copy()
    src = np.repeat(np.arange(grid.n), np.diff(grid.nbr_off))
    for _ in range(n):
        nb = np.zeros(grid.n, bool)
        np.logical_or.at(nb, src, m[grid.nbr_idx])
        m = m | nb
    return m


def spikes(grid, elev, cont):
    """Pits and peaks in continents: cells (of either crust type) with at
    least 4 continental neighbours, > 2 km off those neighbours' median."""
    deg = np.diff(grid.nbr_off)
    k = deg.max()
    pad = np.full((grid.n, k), np.nan)
    rows = np.repeat(np.arange(grid.n), deg)
    cols = np.arange(len(grid.nbr_idx)) - np.repeat(grid.nbr_off[:-1], deg)
    pad[rows, cols] = np.where(cont[grid.nbr_idx], elev[grid.nbr_idx], np.nan)
    ok = np.isfinite(pad).sum(1) >= 4
    med = np.nanmedian(np.where(ok[:, None], pad, 0.0), 1)
    return ok & (np.abs(elev - med) > JUMP)


def churn(grid, frames):
    """frames: list of dicts with cont, plate, elev (no ice), boundary.
    Returns {metric: percent of continental cells per frame}, averaged.
    Metrics: crust / plate / relief / any (see the module docstring), each
    also _conv (cells near converging boundaries); relief_cc only counts
    cells continental in every frame of the excursion (no shelf/abyss
    flips); land_any and land_relief_cc only cells above the sea at frame a;
    spike: pits and peaks in continents (spikes()), per continental cell."""
    acc = {}

    def add(k, v):
        acc.setdefault(k, []).append(v)

    for a in range(len(frames) - 2):
        A, B, C = frames[a], frames[a + 1], frames[a + 2]
        D = frames[a + 3] if a + 3 < len(frames) else None
        cont = A["cont"]
        near = dilate((A["boundary"] > 0) | (B["boundary"] > 0), grid)
        land = cont & (A["elev"] > 0)

        def back(key):
            gone = A[key] != B[key]
            ret = A[key] == C[key]
            if D is not None:
                ret = ret | ((A[key] != C[key]) & (A[key] == D[key]))
            return gone & ret

        f_crust = back("cont")
        f_plate = back("plate")
        dB, dC = B["elev"] - A["elev"], C["elev"] - A["elev"]
        one = (np.abs(dB) > JUMP) & (np.abs(dC) < BACK)
        f_relief = one.copy()
        stays = A["cont"] & B["cont"] & C["cont"]
        f_cc = one & stays
        if D is not None:
            dD = D["elev"] - A["elev"]
            two = (np.abs(dB) > JUMP) & (np.abs(dC) > JUMP) & (np.abs(dD) < BACK)
            f_relief |= two
            f_cc |= two & stays & D["cont"]
        f_any = f_crust | f_plate | f_relief
        nc, ncv, nl = max(cont.sum(), 1), max((cont & near).sum(), 1), max(land.sum(), 1)
        for k, f in (("crust", f_crust), ("plate", f_plate), ("relief", f_relief), ("any", f_any)):
            add(k, 100 * (f & cont).sum() / nc)
            add(k + "_conv", 100 * (f & cont & near).sum() / ncv)
        add("relief_cc", 100 * (f_cc & cont).sum() / nc)
        add("relief_cc_conv", 100 * (f_cc & cont & near).sum() / ncv)
        add("ocean_flip", 100 * (~A["cont"] & B["cont"] & ~C["cont"]).sum() / nc)
        add("land_any", 100 * (f_any & land).sum() / nl)
        add("land_relief_cc", 100 * (f_cc & land).sum() / nl)
        add("spike", 100 * spikes(grid, A["elev"], cont).sum() / nc)
    return {k: round(float(np.mean(v)), 3) for k, v in acc.items()}


def run_frames(run_dir, t0=None, t1=None):
    run, arr = T.load_frames(run_dir, ("crust", "plate", "elevation", "ice", "plate_boundary"))
    out = []
    for i, f in enumerate(run["frames"]):
        if (t0 is not None and f["t"] < t0) or (t1 is not None and f["t"] > t1):
            continue
        out.append({"t": f["t"], "cont": T.frame(run, arr, "crust", i).astype(bool),
                    "plate": T.frame(run, arr, "plate", i).astype(int),
                    "elev": T.frame(run, arr, "elevation", i) - T.frame(run, arr, "ice", i),
                    "boundary": T.frame(run, arr, "plate_boundary", i)})
    return run, out


def sim_frame(sim):
    """The same fields straight from a Simulation (for in-process tests)."""
    return {"t": sim.t, "cont": sim.w_cont.copy(), "plate": sim.plates.label[sim.owner].copy(),
            "elev": sim.w_elev.copy(), "boundary": sim.w_boundary.copy()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--from", dest="t0", type=float)
    ap.add_argument("--to", dest="t1", type=float)
    a = ap.parse_args()
    d = S.find_run(a.run)
    run, frames = run_frames(d, a.t0, a.t1)
    grid = build_grid(run["meta"]["level"])
    print(f"run {run['id']} L{run['meta']['level']} seed {run['meta']['seed']}, "
          f"{frames[0]['t']:.0f}-{frames[-1]['t']:.0f} Myr, {len(frames)} frames")
    for k, v in churn(grid, frames).items():
        print(f"  {k:<12} {v:7.3f} %")


if __name__ == "__main__":
    main()
