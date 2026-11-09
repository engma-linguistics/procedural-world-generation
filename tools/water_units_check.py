"""PW-820: do the culinary water goods agree on the same ground at two levels? Read-only.

    uv run python tools/water_units_check.py <coarse world> <fine world refined from it> [--regions 150] [--json]

The fine world must be `planet refine` of the coarse one (the grids nest, so every fine cell has a coarse parent). The coarse
land is split into --regions pseudo-cultures (nearest of that many random land cells, seed 1) and each fine cell takes its
parent's region. Per good: the share of land holding it at each level, the regions holding it at each level, and the share
of regions where both levels agree. Tolerance (TOL, from the measured refined pairs in
docs/review/pw820-water-units/README.md): region agreement >= TOL for each good; FAIL lines are printed otherwise."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from planet import coastform as CF  # noqa: E402
from planet.lineages import land as LD  # noqa: E402
from planet.lineages import seafood as SF  # noqa: E402
from planet.lineages.gridops import nbr_reduce  # noqa: E402

# region agreement floor per good (measured on L6 -> L7 refines of 4360a3 and 28442c and L7 -> L8 of 899985 after PW-820;
# the README's table): the lowest measured, rounded down to the next 0.05
TOL = {"fish_run": 0.85, "run_strong": 0.9, "fish_lake": 0.8, "lake_full": 0.85, "fish_sea": 0.85, "salt_lick": 0.85, "island": 0.9}


def goods(ref: str):
    """(grid, land, the salt and seafood parts and the island mask) of a stored world. Never writes the goods cache."""
    g, L, _ = LD._layers(ref)
    f = lambda k: np.asarray(L[k], float) if k in L else np.zeros(g.n)  # noqa: E731
    land = LD.world_land(L)
    coast = land & nbr_reduce(g, np.logical_or, (~land)[g.nbr_idx])
    out = SF.salt(g, L, land, coast, f)
    out.update(SF.seafood(g, L, land, coast, f))
    out["island"] = CF.island_mask(g, land)
    return g, land, out


def flags(o: dict) -> dict:
    return {"fish_run": o["fish_run"] > 0.05, "run_strong": o["fish_run"] > 0.3, "fish_lake": o["fish_lake"] > 0.05,
            "lake_full": o["fish_lake"] > 0.6, "fish_sea": o["fish_sea"] > 0.3, "salt_lick": o["salt_lick"] >= 0.25,
            "island": o["island"]}


def parent(gf, gc) -> np.ndarray:
    """Each fine cell's coarse cell (nearest centre)."""
    out = np.empty(gf.n, np.int64)
    for a in range(0, gf.n, 4096):
        out[a:a + 4096] = np.argmax(gf.centers[a:a + 4096] @ gc.centers.T, 1)
    return out


def check(coarse: str, fine: str, n_reg: int = 150, seed: int = 1) -> dict:
    gc, lc, oc = goods(coarse)
    gf, lf, of = goods(fine)
    cells = np.flatnonzero(lc)
    seeds = np.random.default_rng(seed).choice(cells, n_reg, replace=False)
    reg_c = np.full(gc.n, -1)
    reg_c[cells] = np.argmax(gc.centers[cells] @ gc.centers[seeds].T, 1)
    reg_f = reg_c[parent(gf, gc)]
    fc, ff = flags(oc), flags(of)
    res = {"coarse": coarse, "fine": fine, "levels": [gc.level, gf.level], "regions": n_reg, "goods": {}}
    for k in fc:
        hc = np.bincount(reg_c[lc & fc[k] & (reg_c >= 0)], minlength=n_reg) > 0
        hf = np.bincount(reg_f[lf & ff[k] & (reg_f >= 0)], minlength=n_reg) > 0
        res["goods"][k] = {"land_share": [round(float(fc[k][lc].mean()), 4), round(float(ff[k][lf].mean()), 4)],
                           "regions": [int(hc.sum()), int(hf.sum())], "agree": round(float((hc == hf).mean()), 3)}
    res["fails"] = [k for k, v in res["goods"].items() if v["agree"] < TOL.get(k, 0.0)]
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("coarse")
    ap.add_argument("fine")
    ap.add_argument("--regions", type=int, default=150)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = check(a.coarse, a.fine, a.regions)
    if a.json:
        print(json.dumps(r))
        return
    print(f"{r['coarse']} (L{r['levels'][0]}) vs {r['fine']} (L{r['levels'][1]}), {r['regions']} regions")
    print(f"{'good':12s} {'land share':>17s} {'regions':>9s} {'agree':>6s} {'tol':>5s}")
    for k, v in r["goods"].items():
        ls = f"{v['land_share'][0]:.4f}/{v['land_share'][1]:.4f}"
        print(f"{k:12s} {ls:>17s} {v['regions'][0]:>4d}/{v['regions'][1]:<4d} {v['agree']:6.3f} {TOL.get(k, 0):5.2f}"
              + ("  FAIL" if k in r["fails"] else ""))


if __name__ == "__main__":
    main()
