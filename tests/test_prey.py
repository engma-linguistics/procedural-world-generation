"""The static prey field (PW-966): wild herbivores from grazing NPP, overkill outside refuge country, livestock by way of life."""
from types import SimpleNamespace as NS

import numpy as np

from planet import gameattrs as GA
from planet.lineages import prey as PR


def test_wild_prey_scales_with_grazing_npp():
    w = PR.wild(np.array([0.0, PR.PREY_G_REF / 10, PR.PREY_G_REF, -5.0]))
    assert np.allclose(w, [0, PR.PREY_T_REF / 10, PR.PREY_T_REF, 0])
    assert PR.wild(None) is None


def test_overkill_spares_refuges_and_livestock_adds():
    wild = np.full(4, 2.0)
    press = np.array([0.0, 1.0, 1.0, 1.0])
    ref = np.array([False, False, True, False])
    f = PR.field(wild, press, ref, np.array([0, 0, 0, 1.0]))
    assert np.allclose(f["wild"], [2, 2 * (1 - PR.OVERKILL), 2, 2 * (1 - PR.OVERKILL)])
    assert f["wild"].min() > 0  # (overkill never zeroes the prey)
    assert np.allclose(f["livestock"], [0, 0, 0, 2 * PR.LIVESTOCK_X]) and np.allclose(f["total"], f["wild"] + f["livestock"])
    tags = {"land": np.array([True, True, True, False]), "tundra": np.array([False, True, False, False]),
            "mountain": np.array([False, False, True, False])}
    assert PR.refuge(tags).tolist() == [False, True, True, True]


def test_stocked_by_way_of_life():
    lines = [NS(megafauna=False, overlay=False, way="pastoral_nomad"), NS(megafauna=False, overlay=False, way="forager"),
             NS(megafauna=True, overlay=False, way=None)]
    sh = PR.herd_share(lines)
    assert sh.tolist() == [1.0, 0.0, 0.0]
    P = np.array([[0.5, 0.0, 0.01], [0.5, 1.0, 0.0], [1.0, 1.0, 1.0]])
    assert np.allclose(PR.stocked(P, sh, 0.02), [0.5, 0, 0])
    p = PR.productivity(np.array([1.0, 2.0, 3.0, 0.0]), np.array([True, True, True, True]))
    assert np.allclose(p[:3], [0.5, 1, 1.5])


def test_gameattrs_raw_grazing_npp():
    n = 3
    F = {"land": np.array([True, True, False]), "temp": np.full(n, 20.0), "t_warm": np.full(n, 25.0), "t_cold": np.full(n, 15.0),
         "p_jul": np.full(n, 800.0), "p_jan": np.full(n, 800.0), "tree": np.zeros(n), "cover": np.full(n, 0.8),
         "lai": np.full(n, 2.0), "height": np.full(n, 1.0), "npp": np.array([400.0, 100.0, 400.0])}
    out = GA.compute(np.zeros(n), F, raw=True)
    assert "grazing_npp" not in GA.compute(np.zeros(n), F)
    g = out["grazing_npp"]
    assert g[0] > g[1] > 0 and g[2] == 0
    assert np.allclose(out["grazing"][:2], GA._sat(g[:2], 250.0), atol=0.06)


def test_brief_bounty_hook_picks_the_ruined_valley():
    """PW-961: the brief names the pocket where an ancient's kill is the largest share of the herd in its range."""
    from planet.lineages.brief import _bounty

    def p(head, km2, rng_, anc):
        return {"stages": [0, 1, 2, anc], "livestock_head": head, "km2": km2, "ancient_range_km2": rng_,
                "ancient_cattle_yr": 56.0, "country": "hills", "lat": 1.0, "lon": 2.0}
    assert _bounty([p(1000, 1000, 300, 0)]) is None  # (no ancient)
    assert _bounty([p(10, 1000, 300, 1)]) is None  # (no herd worth the name in its range)
    t = _bounty([p(100000, 1000, 300, 1), p(100, 1000, 300, 2)])
    assert t.startswith("2 ancients") and "~30 head" in t and "bounties" in t
