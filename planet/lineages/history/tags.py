"""The place tags of an epoch (PLACES, Koppen groups) shared by every line."""

from __future__ import annotations

import numpy as np

from ...geo import R_KM
from .. import land as LD, spec as SP
from .params import BREAKS_RAIN, BREAKS_RISE, CHAIN_CELLS
from ..gridops import nbr_reduce
from .gridops import _isin


def _tags(grid, env: dict, chains: bool = True, volcanic: np.ndarray | None = None) -> dict:
    """Place tags of an epoch (PLACES) and Köppen ids, shared by every line (island_chain only if `chains`:
    the costliest tag, needed only when a wish or a line names it; volcanic from the world's volcanic good,
    land.goods, where given: none in the deep epochs, whose volcanoes were elsewhere)."""
    land = env["land"] & ~(env["ice"] > 0.5)
    sea = ~env["land"]
    ni, src = grid.nbr_idx, grid.nbr_src
    sea_nbr = nbr_reduce(grid, np.logical_or, sea[ni])
    elev = np.maximum(env["elevation"] - env["ice"], 0)
    dh = np.maximum(0.0, nbr_reduce(grid, np.maximum, np.abs(elev[ni] - elev[src])))
    lab, k = grid.components(env["land"])
    sizes = np.bincount(lab[lab >= 0], minlength=k) if k else np.zeros(0)
    island = np.zeros(grid.n, bool)
    if k:
        small = sizes < max(3, 0.004 * env["land"].sum())
        island = env["land"] & (lab >= 0) & small[np.maximum(lab, 0)]
    trees = env.get("tree_cover", np.zeros(grid.n))
    rain = env["precipitation"]
    mountain = land & ((elev > 1500) | (dh > 700))
    cl = env["climate"].astype(int)
    # island chains: islands with another island (or any other landmass) within CHAIN_CELLS cells over the sea
    chain = np.zeros(grid.n, bool)
    if chains and island.any():
        big = np.iinfo(np.int64).max
        lo_ = np.where(env["land"], lab, big)
        hi_ = np.where(env["land"], lab, -1)
        through = ~env["land"] | island
        for _ in range(CHAIN_CELLS):
            l2 = np.minimum(lo_, nbr_reduce(grid, np.minimum, np.where(through[ni], lo_[ni], big)))
            h2 = np.maximum(hi_, nbr_reduce(grid, np.maximum, np.where(through[ni], hi_[ni], -1)))
            lo_, hi_ = np.where(through, l2, lo_), np.where(through, h2, hi_)
        chain = island & (lo_ != hi_)
    farm = land & _isin(cl, SP.GROUPS["temperate"] + [2, 20, 24]) & (rain > 500) & (elev < 1000)
    hills = land & ~mountain & (LD._window(dh / (grid.spacing * R_KM), LD.HILL_SLOPE) * LD._window(elev, LD.HILL_ELEV) >= 0.5)
    volc = land & (volcanic >= 0.5) if volcanic is not None else np.zeros(grid.n, bool)
    opn = land & (trees < 20) & (rain > 200)
    # breaks (PW-1024: copper dragons' badlands, buttes and river breaks): open, dry-ish grassland cut by relief, under the mountains
    breaks = opn & ~mountain & (rain < BREAKS_RAIN) & (dh / (grid.spacing * R_KM) >= BREAKS_RISE)
    return {"farmland": farm, "jungle": land & _isin(cl, [0, 1]), "steppe": land & _isin(cl, [5, 6]),
            "desert": land & _isin(cl, [3, 4]), "tundra": land & (cl == 28), "island_chain": chain,
            "hills": hills, "volcanic": volc, "breaks": breaks,
            "land": land, "sea": sea, "shore": sea & nbr_reduce(grid, np.logical_or, env["land"][ni]), "coast": land & sea_nbr, "island": island, "mountain": mountain,
            "lowland": land & (elev < 500), "inland": land & ~sea_nbr, "forest": land & (trees >= 35),
            "open": opn, "wetland": land & (elev < 300) & (rain > 1600),
            "elev": elev, "label": lab, "sizes": sizes}


def needs_chains(tree: SP.Tree) -> bool:
    return any(w.want == "island_chain" for w in tree.wishes) or any(
        "island_chain" in (*l.prefers, *l.avoids) for l in tree.lines.values())
