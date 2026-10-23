"""Game attributes (PW-206, gameattrs.py) on a few made-up places: each rule shows on the place built for it."""

import numpy as np

from planet import gameattrs as GA
from planet import soils as SO
from planet import vegetation as V


def _places():
    """0 prairie, 1 temperate forest, 2 raised bog, 3 hot desert, 4 boreal forest, 5 sea."""
    n = 6
    nu = np.zeros((V.NP, n))
    nu[V.IDX["C3G"], 0] = 0.9
    nu[V.IDX["TeBS"], 1], nu[V.IDX["TeNE"], 1], nu[V.IDX["C3G"], 1] = 0.6, 0.3, 0.05
    nu[V.IDX["Sph"], 2], nu[V.IDX["WetH"], 2] = 0.6, 0.3
    nu[V.IDX["XerS"], 3], nu[V.IDX["Succ"], 3] = 0.08, 0.04
    nu[V.IDX["BoNE"], 4], nu[V.IDX["Moss"], 4] = 0.75, 0.2
    F = {"land": np.array([1, 1, 1, 1, 1, 0], bool), "ice": np.zeros(n), "elevation": np.array([300, 400, 100, 500, 300, -1000.0]),
         "temp": np.array([9, 10, 4, 25, -4, 15.0]), "t_warm": np.array([22, 20, 15, 34, 16, 20.0]),
         "t_cold": np.array([-6, 0, -8, 14, -25, 10.0]), "p_jul": np.array([700, 1000, 900, 60, 500, 800.0]),
         "p_jan": np.array([300, 900, 700, 40, 300, 800.0]),
         "tree": np.array([0, 0.9, 0, 0, 0.75, 0]), "cover": np.array([0.9, 0.95, 0.9, 0.12, 0.95, 0]),
         "lai": np.array([2.5, 5, 2, 0.3, 3, 0]), "height": np.array([1, 30, 1, 1, 18, 0.0]),
         "npp": np.array([500, 700, 200, 40, 250, 0.0]), "fire_return": np.array([8, 0, 0, 0, 200, 0.0]),
         "biomass": np.array([3, 150, 5, 1, 60, 0.0]), "stand_age": np.array([5, 250, 100, 50, 150, 0.0]),
         "flooded": np.array([0, 0, 0.7, 0, 0.05, 0]),
         "soil": np.array([SO.CHERNOZEM, SO.LUVISOL, SO.PEAT, SO.CALCIC, SO.PODZOL, SO.NONE]),
         "soil_texture": np.array([3, 2, 5, 1, 1, 0]), "soil_drainage": np.array([2, 2, 5, 1, 2, 0]),
         "peat_depth": np.array([0, 0, 3, 0, 0, 0.0]), "permafrost": np.array([0, 0, 0, 0, 1, 0])}
    return F, nu


def test_rules_show_on_their_places():
    F, nu = _places()
    lat = np.array([45, 48, 55, 25, 62, 0.0])
    a = GA.compute(lat, F, nu)
    assert set(a) == set(GA.NAMES)
    pr, fo, bog, de, bo, sea = range(6)
    assert a["travel"][pr] < 1.3 < a["travel"][fo] < a["travel"][bog]  # grass, forest, bog
    assert a["travel"][sea] == 0 and a["sightline"][sea] == 0 and a["hazards"][sea] == 0
    assert a["sightline"][pr] == GA.HORIZON_M and a["sightline"][fo] < 100
    assert a["grazing"][pr] > 3 > a["grazing"][fo]
    assert a["timber"][fo] > 3 > a["timber"][pr]
    assert a["fuel"][bog] > a["fuel"][de]  # (peat)
    assert a["building"][bog] <= 1 and a["building"][de] >= 4
    assert a["hazards"][bog] & GA.HAZARD_BIT["bog"]
    assert a["hazards"][de] & GA.HAZARD_BIT["heat"]
    assert a["hazards"][bo] & GA.HAZARD_BIT["snow"] and a["hazards"][bo] & GA.HAZARD_BIT["cold"]
    assert a["fire_months"][pr] > 0 and a["fire_months"][fo] == 0  # burns / doesn't
    assert bin(int(a["green_months"][fo])).count("1") < 12  # leafless winters (summergreen broadleaves)
    assert a["green_months"][pr] & (1 << 6) and not a["green_months"][pr] & 1  # green in July, not January (north)


def test_without_fractions_and_legend():
    F, _ = _places()
    a = GA.compute(np.array([45, 48, 55, 25, 62, 0.0]), F, None)
    assert a["travel"][0] < a["travel"][1] and a["timber"][1] > a["timber"][0]
    leg = GA.legend()
    assert [h["bit"] for h in leg["hazards"]] == list(range(len(GA.HAZARDS))) and len(GA.HAZARDS) <= 16
