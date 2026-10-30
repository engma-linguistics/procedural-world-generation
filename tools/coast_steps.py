"""Staircase measure for a fine zoom's coast (PW-488): the share of coastline edges lying on the parent's
pixel grid lines, the share in long straight axis-aligned runs, and the land share against the parent's.

    uv run python tools/coast_steps.py <fine-zoom-id> [more ids]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np  # noqa: E402

from planet import zoom as Z  # noqa: E402
from planet import zoom_fine as ZF  # noqa: E402


def _runs(m, kmin):
    tot = 0
    for row in m:
        d = np.diff(np.r_[0, row.astype(int), 0])
        s, e = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
        ln = e - s
        tot += ln[ln >= kmin].sum()
    return tot


def measure(zid: str) -> dict:
    meta, lay = Z.load(zid)
    pm, pl = Z.load(meta["parent_zoom"]["id"])
    pa = ZF._Parent(pm, {k: np.asarray(v) for k, v in pl.items()})
    res, n = meta["res_km"], meta["nx"]
    sea = np.asarray(lay["water"]).reshape(n, n) == 1
    fr = Z.Frame(meta["center"]["lat"], meta["center"]["lon"])
    xs = (np.arange(n) + 0.5 - n / 2) * res
    ys = (n / 2 - np.arange(n) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    pr, pc = pa.coords(fr.to_sphere(X.ravel(), Y.ravel()))
    pr, pc = pr.reshape(n, n), pc.reshape(n, n)
    h = sea[:, :-1] != sea[:, 1:]  # a coast edge between horizontal neighbours
    v = sea[:-1, :] != sea[1:, :]
    mr = np.r_[(pr[:, :-1] + pr[:, 1:])[h] / 2, (pr[:-1, :] + pr[1:, :])[v] / 2]
    mc = np.r_[(pc[:, :-1] + pc[:, 1:])[h] / 2, (pc[:-1, :] + pc[1:, :])[v] / 2]
    rp = pa.rp
    eps = 0.6 * res / rp  # within 0.6 fine px of a parent pixel edge (k + 0.5), on either axis
    aligned = float(((np.abs((mr % 1.0) - 0.5) < eps) | (np.abs((mc % 1.0) - 0.5) < eps)).mean()) if len(mr) else 0.0
    chance = 1 - (1 - 2 * eps) ** 2
    kmin = max(3, int(0.5 * rp / res))
    straight = (_runs(h.T, kmin) + _runs(v, kmin)) / max(1, int(h.sum() + v.sum()))
    pw = pa.bilinear((np.asarray(pa.L["water"]) != 1).astype(float), pr.ravel(), pc.ravel()).reshape(n, n)
    land_f, land_p = float((~sea).mean()), float(pw.mean())
    return {"id": zid, "coast_edges": len(mr), "grid_aligned": round(aligned, 3), "chance": round(chance, 3),
            "straight_run_share": round(float(straight), 3), "land_fine": round(land_f, 4),
            "land_parent": round(land_p, 4), "land_ratio": round(land_f / max(land_p, 1e-9), 3)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("zooms", nargs="+", help="fine zoom ids")
    for z in ap.parse_args().zooms:
        print(measure(z))
