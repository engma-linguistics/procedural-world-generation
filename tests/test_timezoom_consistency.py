"""The time zoom from a run's moment starts close to its own balance (PW-418, PW-366): the run's ice
rule (earth.ice_sheets, as earth.update_climate runs it) makes the sheets of a cold moment, then the time
zoom runs 20 kyr with no orbital swing (so the glacial index stays 0: an interglacial). Level 5, seed 4, 300 Myr (seed 2 lost most of its polar ice after PW-300, seed 1 after PW-549), 4 C colder."""

from types import SimpleNamespace

import numpy as np
import pytest

from planet import timezoom as Z, vegetation
from planet.timezoom import params as P
from planet.timezoom.geometry import geometry
from planet.tectonics import earth
from planet.tectonics.isostasy import ice_load, land_view

from helpers import run_sim

pytestmark = pytest.mark.slow
UNFORCED = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")
# The run's margin, orbit and air rules (EDGE_H margins, INSOL_K, all ice's air, the ice's own effects on top): the zoom took the honest ones first (PW-555 stage
# 1: margin_ramp, the seasons' response); the run takes them in stage 3. Until then this checks the rest of the
# shared rule (the balance, the Nye profile, the marine budget) with the run's own margins and orbit.
RUN_RULE = dict(margin="edge", front="edge", orbit_resp="run", sheet_air="all", surface_air="all")
FLT = 1 - P.RHO_I / P.RHO_W


@pytest.fixture(scope="module")
def cold_moment():
    """A run's moment made 4 C colder than an icehouse moment (its own dT, or -2 C if it is warmer: the
    moment itself may be a greenhouse; the test was written on an icehouse moment at -1.8 C), with the sheets the run's own ice rule gives that climate
    (6 climate updates from no ice; as tools/ice_probe.py)."""
    src = Z.source_from_sim(run_sim(level=5, seed=4, myr=300))
    g = src["grid"]
    dT = min(src["dT"], -2.0) - 4.0
    bed0 = src["elev"] + ice_load(g, src["ice"])
    sim = SimpleNamespace(grid=g, params=SimpleNamespace(tilt=src["tilt"]), cell_area=4 * np.pi / g.n,
                          precip=None, p_jul=None, p_jan=None)
    ice = np.zeros(g.n)
    for _ in range(6):
        bed = bed0 - ice_load(g, ice)
        e, ice0, _ = land_view(bed, np.where(bed0 > 0, ice, 0.0))
        land = e > 0
        v = src["veg"]  # (as the run: the climate with its plants' feedbacks)
        c, _ = vegetation.coupled_climate(g, e, dT, src["tilt"], np.where(land, ice0, 0.0), nu0=v["nu0"],
                                          co2=v["co2"], unlocked=v["unlocked"])
        sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
        ice = earth.ice_sheets(sim, land, e, c["ground"], ice0, ice_load(g, ice), marine=earth.marine_view(bed, c))
    e, ice0, _ = land_view(bed0 - ice_load(g, ice), np.where(bed0 > 0, ice, 0.0))
    src = dict(src, elev=e, ice=ice0, dT=dT)
    return src, Z.simulate(src, 20.0, 0.5, 2.0, Z.TZParams(**UNFORCED, **RUN_RULE))


def test_cold_moment_has_sheets(cold_moment):
    src, _ = cold_moment
    assert (src["ice"] > 1).mean() > 0.01  # (else the drift test below proves nothing)


def test_ice_speeds_plausible(cold_moment):
    """Shallow-ice speeds (D |grad s| / H, the steepest way down) under grounded sheets: interiors
    metres to tens of m/yr, outlets up to a few km/yr."""
    src, r = cold_moment
    g, G, p, st = src["grid"], geometry(src["grid"]), Z.TZParams(), r["state"]
    H, bed, sl = st["H"], st["bed"], st["sl"]
    s = np.maximum(bed + H, sl + FLT * H)
    e_src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    grad = np.zeros(g.n)
    np.maximum.at(grad, e_src, np.maximum(s[e_src] - s[g.nbr_idx], 0) / G["dist"])
    gamma = 2 * p.flow_a * p.enhancement * (P.RHO_I * 9.81) ** 3 / 5
    D = np.minimum(gamma * H**5 * grad**2, p.d_cap)
    sheet = (H > 100) & (bed + H > sl + FLT * H)
    u = (D * grad / np.maximum(H, 1.0))[sheet]
    assert 1.0 < np.median(u) < 100.0
    assert np.percentile(u, 99) < 5000.0
    assert 500 < np.median(H[sheet]) < 3500


def test_ice_at_index_zero_is_the_runs(cold_moment):
    """At I = 0 (an interglacial: the run's own climate) the zoom keeps the run's ice: with no orbital swing
    the default index never builds, and sea level moves little (PW-366: -43 m in 20 kyr here while the
    run's sheets were 50 kPa profiles with their margins' inner-edge rise and the time zoom melted its
    margins before its flow; PW-471: the index replaced the CO2 and ice-albedo feedbacks)."""
    _, r = cold_moment
    assert all(f["stats"]["glacial_index"] == 0.0 for f in r["frames"])
    assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 25.0
