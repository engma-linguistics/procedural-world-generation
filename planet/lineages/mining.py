"""Salt miners (PW-797, light first pass): which mining peoples work rock salt, which work ore, which both.

Nothing here is authored per people. A line with the `miner` trait that holds country with rock-salt beds (the world's
`salt_rock` good, evaporite near the surface: Hallstatt, Wieliczka, Khewra) works salt there; where ore districts lie in the
same country it works both. A people's kind is read from the cells it leads (or is second in), so the same dwarves are
salt miners where the beds are and ore miners where the veins are. Salt a miner people works is a trade good: salt_reach.reach
carries it further than the salt of unworked beds (MINED_CAP), and the brief says what the miners sell and what they must
buy (the goods their own country lacks). Mineral licks and brine springs stay a human source (salt_lick, seafood.py).
"""
from __future__ import annotations

import numpy as np

SALT_MIN = 0.25  # the rock-salt good (0..1, one ring inland) from this is a bed worth working (as seafood.SRC_MIN)
ORE_MIN = 0.75  # a RAW ore good (the per-cell deposit likelihood, no one-ring reach) from this is a worked district (PW-1146: at 0.5 with the
# reach it was 46% of land; here ~8%, rare and clustered as on Earth). land.DISTRICT_MIN (0.5, the notes' districts) and the history's pull stay.
ORE_GOODS = ("gold", "iron", "copper", "tin", "gems", "mithril", "metal")
HELD_MIN = 0.05  # a share of a people's cells that must carry salt (or ore) for it to work it: a mine is a point, not a plain
NEEDS = (("fertile", "grain and bread"), ("grazing", "meat, wool, hides and cheese"), ("timber", "timber and charcoal"),
         ("foraging", "wild food, nuts and honey"))  # the goods a mining country may lack, and what it then buys
NEED_BELOW = 0.2  # a living good under this (0..1 against the world's best) over the people's country is a lack


def is_miner(traits) -> bool:
    return "miner" in (traits or ())


def kind_of(salt_share: float, ore_share: float) -> str | None:
    """'salt', 'ore' or 'salt and ore' from the shares of the people's cells carrying rock salt and ore; None: neither (stone only)."""
    s, o = salt_share >= HELD_MIN, ore_share >= HELD_MIN
    return "salt and ore" if s and o else "salt" if s else "ore" if o else None


def ore_good(G: dict, k: str) -> np.ndarray:
    """An ore good per cell on its raw layer (the deposit likelihood in the cell itself; the good G[k] carries it a ring further)."""
    return np.asarray(G.get("_raw", {}).get(k, G[k]), float)


def ore_cells(G: dict) -> np.ndarray:
    """Per cell: the best ore good (0..1), raw: no reach, so a district is a cell with a deposit and not the country around it."""
    return np.maximum.reduce([ore_good(G, k) for k in ORE_GOODS if k in G])


def salt_cells(G: dict) -> np.ndarray:
    return np.asarray(G["salt_rock"], float) if "salt_rock" in G else np.zeros(len(G["_land"]))


def worked_salt(G: dict, miner_here: np.ndarray) -> np.ndarray:
    """Cells where a mining people works rock salt: beds (SALT_MIN) in the country of a line with the miner trait."""
    return (salt_cells(G) >= SALT_MIN) & miner_here


def people_kind(G: dict, cells: np.ndarray) -> dict | None:
    """A mining people's work over its cells: shares of cells with salt beds and with ore, the kind, and what its country lacks."""
    if not cells.any():
        return None
    ss = float((salt_cells(G)[cells] >= SALT_MIN).mean())
    os_ = float((ore_cells(G)[cells] >= ORE_MIN).mean())
    lacks = [text for g, text in NEEDS if g in G and float(np.asarray(G[g], float)[cells].mean()) < NEED_BELOW]
    return {"kind": kind_of(ss, os_), "salt_share": round(ss, 3), "ore_share": round(os_, 3), "lacks": lacks}


COLONY_KM = 300.0  # a mining people (the miner trait: dwarves) sends a colony to work beds this far from its own country, if a people holds them (PW-854)


def colony_cells(G: dict, miner_here: np.ndarray, settled: np.ndarray, near_miner: np.ndarray) -> np.ndarray:
    """Cells of a mining colony (PW-854): rock-salt beds held by a settled people beyond the miners' own country but within COLONY_KM of it
    (near_miner), worked by a colony of the miners: dwarves are predisposed to mining, so the beds of their neighbours get a mining
    settlement. Salt is something peoples seek: no subgroup of miners is needed for it."""
    return (salt_cells(G) >= SALT_MIN) & settled & near_miner & ~miner_here


def settled_works(G: dict, settled: np.ndarray, mined: np.ndarray) -> np.ndarray:
    """Cells where a settled people of any kind works the beds in its country as salt works (PW-854), the miners' mines and colonies
    (mined) apart."""
    return (salt_cells(G) >= SALT_MIN) & settled & ~mined
