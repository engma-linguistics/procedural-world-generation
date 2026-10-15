"""Ranges a healthy world stays in. Bands, not exact values, so tuning stays
free; a failure means a change pushed some other part of the planet out of
the plausible range. Level 5 (10k cells), two seeds, 400 Myr."""

from pathlib import Path

import numpy as np
import pytest

from planet import climate

from helpers import run_sim
from tools.churn import churn, sim_frame

pytestmark = pytest.mark.slow
GROUP = np.array([k[1][0] for k in climate.KOPPEN])


@pytest.fixture(scope="module", params=[1, 2])
def world(request):
    # the dry share swings a lot as continents move: average it over the last 80 Myr
    sim, dry = run_sim(level=5, seed=request.param, myr=320), []
    frames = []
    for t in (340, 360, 380, 400):
        while sim.t < t - 1e-9:  # (keyframes every 4 Myr over the last 40, for the churn)
            sim.run(sim.t + 4)
            if sim.t > 356:
                frames.append(sim_frame(sim))
        land = sim.w_elev > 0
        dry.append(100 * (GROUP[sim.snapshot().koppen[land]] == "B").mean())
    land = sim.w_elev > 0
    ocean = ~sim.w_cont
    st = sim.stats()
    return dict(
        sim=sim, st=st,
        land=100 * land.mean(),
        cont=100 * sim.w_cont.mean(),
        dry=float(np.mean(dry)),
        ocean_age=sim.w_age[ocean].mean(),
        thick=sim.w_thick[sim.w_cont].mean(),
        churn=churn(sim.grid, frames),
    )


def test_land_and_crust(world):
    assert 22 <= world["land"] <= 42, world["land"]  # Earth 29
    assert 33 <= world["cont"] <= 50, world["cont"]  # Earth ~41 incl. shelves
    # Earth ~35-40. Floor 28, not 30: since crust.coherence (PW-108) level 5
    # sits at 28.6-30.1 km; PW-052 is to restore the thickness (PW-169 decision C).
    assert 28 <= world["thick"] <= 42, world["thick"]


def test_relief(world):
    assert 2000 <= world["st"]["max_elev_m"] <= 9500


def test_plates(world):
    st = world["st"]
    assert 2 <= st["mean_speed_cmyr"] <= 9  # Earth ~4-5
    assert 5 <= st["plates"] <= 30
    assert 25 <= world["ocean_age"] <= 120  # Earth ~64


def test_churn(world):
    """Continental cells that flip type (or by > 2 km) and flip back within
    8 Myr: sampling artifacts (PW-108). At level 5, 400 Myr: crust 0.4-0.8%
    and any 1.0-1.8% with crust.coherence, 2.9-3.3% and 3.2-3.8% before."""
    c = world["churn"]
    assert c["crust"] <= 1.5, c
    assert c["any"] <= 2.5, c


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
    main groups on at least ~2/3 of land: earth_data.koppen_agreement's
    area-weighted "group" score (70.7% when calibrated, Oct 2026)."""
    from planet.grid import build_grid
    from tools.earth_data import koppen_agreement
    e = np.load(EARTH)
    g = build_grid(6)
    elev, ice, obs = e["elev"].astype(float), e["ice"].astype(float), e["obs_koppen"]
    c = climate.compute(g, elev, 0.0, 23.4, ice)
    agree = koppen_agreement(g, c["koppen"], obs, elev)["group"]
    assert agree >= 66, agree
