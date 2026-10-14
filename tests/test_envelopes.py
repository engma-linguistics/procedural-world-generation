"""Ranges a healthy world stays in. Bands, not exact values, so tuning stays
free; a failure means a change pushed some other part of the planet out of
the plausible range. Level 5 (10k cells), two seeds, 400 Myr."""

from pathlib import Path

import numpy as np
import pytest

from planet import climate

from helpers import run_sim

pytestmark = pytest.mark.slow
GROUP = np.array([k[1][0] for k in climate.KOPPEN])


@pytest.fixture(scope="module", params=[1, 2])
def world(request):
    sim = run_sim(level=5, seed=request.param, myr=400)
    land = sim.w_elev > 0
    ocean = ~sim.w_cont
    st = sim.stats()
    return dict(
        sim=sim, st=st,
        land=100 * land.mean(),
        cont=100 * sim.w_cont.mean(),
        dry=100 * (GROUP[sim.snapshot().koppen[land]] == "B").mean(),
        ocean_age=sim.w_age[ocean].mean(),
        thick=sim.w_thick[sim.w_cont].mean(),
    )


def test_land_and_crust(world):
    assert 22 <= world["land"] <= 42, world["land"]  # Earth 29
    assert 33 <= world["cont"] <= 50, world["cont"]  # Earth ~41 incl. shelves
    assert 30 <= world["thick"] <= 42, world["thick"]  # Earth ~35-40


def test_relief(world):
    assert 2000 <= world["st"]["max_elev_m"] <= 9500


def test_plates(world):
    st = world["st"]
    assert 2 <= st["mean_speed_cmyr"] <= 9  # Earth ~4-5
    assert 5 <= st["plates"] <= 30
    assert 25 <= world["ocean_age"] <= 120  # Earth ~64


def test_climate(world):
    st = world["st"]
    assert 12 <= world["dry"] <= 45, world["dry"]  # Earth ~30% of land is B
    assert abs(st["global_temp_c"] - 14.5) <= 10
    assert st["ice_pct"] <= 15
    assert abs(st["sea_level_m"]) <= 400


EARTH = Path(__file__).resolve().parent.parent / "data" / "earth" / "L6.npz"


@pytest.mark.skipif(not EARTH.exists(), reason="Earth data not downloaded (run tools/earth_check.py once)")
def test_earth_climate_score():
    """The climate on real Earth geography keeps matching observed Koppen
    main groups on at least ~2/3 of land (70% when calibrated, Oct 2026)."""
    from planet.grid import build_grid
    e = np.load(EARTH)
    g = build_grid(6)
    elev, ice, obs = e["elev"].astype(float), e["ice"].astype(float), e["obs_koppen"]
    c = climate.compute(g, elev, 0.0, 23.4, ice)
    land = (elev > 0) & (g.lat > -60) & (obs >= 0) & (obs != climate.SEA_CLASS)
    obs_group = np.array([climate.KOPPEN[int(k)][1][0] if 0 <= k < len(climate.KOPPEN) else "?" for k in obs])
    agree = (GROUP[c["koppen"][land]] == obs_group[land]).mean()
    assert agree >= 0.66, agree
