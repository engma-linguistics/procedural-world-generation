"""The time zoom from a run's moment starts close to its own balance (PW-418, PW-366): the run's ice
rule (earth.ice_sheets, as earth.update_climate runs it) makes the sheets of a cold moment, then the time
zoom runs 20 kyr with no forcing (no orbit, CO2 or ice albedo). Level 5, seed 1, 300 Myr (seed 2 lost most of its polar ice after PW-300), 4 C colder."""

from types import SimpleNamespace

import numpy as np
import pytest

from planet import climate, timezoom as Z
from planet.tectonics import earth
from planet.tectonics.isostasy import ice_load, land_view

from helpers import run_sim

pytestmark = pytest.mark.slow
UNFORCED = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean", co2_cool=0.0,
                ice_albedo=0.0)
FLT = 1 - Z.RHO_I / Z.RHO_W


@pytest.fixture(scope="module")
def cold_moment():
    """A run's moment made 4 C colder, with the sheets the run's own ice rule gives that climate
    (6 climate updates from no ice; as tools/ice_probe.py)."""
    src = Z.source_from_sim(run_sim(level=5, seed=1, myr=300))
    g = src["grid"]
    dT = src["dT"] - 4.0
    bed0 = src["elev"] + ice_load(g, src["ice"])
    sim = SimpleNamespace(grid=g, params=SimpleNamespace(tilt=src["tilt"]), cell_area=4 * np.pi / g.n,
                          precip=None, p_jul=None, p_jan=None)
    ice = np.zeros(g.n)
    for _ in range(6):
        e, ice0, _ = land_view(bed0 - ice_load(g, ice), np.where(bed0 > 0, ice, 0.0))
        land = e > 0
        c = climate.compute(g, e, dT, src["tilt"], np.where(land, ice0, 0.0))
        sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
        ice = earth.ice_sheets(sim, land, e, c["ground"], ice0, ice_load(g, ice))
    e, ice0, _ = land_view(bed0 - ice_load(g, ice), np.where(bed0 > 0, ice, 0.0))
    src = dict(src, elev=e, ice=ice0, dT=dT)
    return src, Z.simulate(src, 20.0, 0.5, 2.0, Z.TZParams(**UNFORCED))


def test_cold_moment_has_sheets(cold_moment):
    src, _ = cold_moment
    assert (src["ice"] > 1).mean() > 0.01  # (else the drift test below proves nothing)


def test_ice_speeds_plausible(cold_moment):
    """Shallow-ice speeds (D |grad s| / H, the steepest way down) under grounded sheets: interiors
    metres to tens of m/yr, outlets up to a few km/yr."""
    src, r = cold_moment
    g, G, p, st = src["grid"], Z.geometry(src["grid"]), Z.TZParams(), r["state"]
    H, bed, sl = st["H"], st["bed"], st["sl"]
    s = np.maximum(bed + H, sl + FLT * H)
    e_src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    grad = np.zeros(g.n)
    np.maximum.at(grad, e_src, np.maximum(s[e_src] - s[g.nbr_idx], 0) / G["dist"])
    gamma = 2 * p.flow_a * p.enhancement * (Z.RHO_I * 9.81) ** 3 / 5
    D = np.minimum(gamma * H**5 * grad**2, p.d_cap)
    sheet = (H > 100) & (bed + H > sl + FLT * H)
    u = (D * grad / np.maximum(H, 1.0))[sheet]
    assert 1.0 < np.median(u) < 100.0
    assert np.percentile(u, 99) < 5000.0
    assert 500 < np.median(H[sheet]) < 3500


@pytest.mark.xfail(strict=True, reason="PW-366: the run's sheets are thinner than the time zoom's and leave "
                   "a snow surplus (-43 m in 20 kyr here); remove this mark once that is fixed")
def test_unforced_start_stays_near_balance(cold_moment):
    """With no forcing, a run's sheets are already this mass balance's: sea level moves little."""
    _, r = cold_moment
    assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 25.0
