"""The time zoom from a run's moment starts close to its own balance (PW-418, PW-366): the run's ice
rule (earth.ice_sheets, as earth.update_climate runs it) makes the sheets of a cold moment, then the time
zoom runs 20 kyr with no orbital swing (so the glacial index stays 0: an interglacial). Level 5, 300 Myr, 4 C
colder; every seed of SEEDS whose moment is a plausible world with polar land, and the drift tests on the
ones with sheets (the run is chaotic, so one seed's world flips with any climate change: PW-623, PW-640; the
seed used to be re-picked by hand: seed 2 lost most of its polar ice after PW-300, seed 1 after PW-549)."""

from types import SimpleNamespace

import numpy as np
import pytest

from planet import timezoom as Z, vegetation
from planet.timezoom import params as P
from planet.timezoom.geometry import geometry
from planet.tectonics import earth
from planet.tectonics.isostasy import ice_load, land_view

from helpers import run_sim
import seeds

pytestmark = pytest.mark.slow
UNFORCED = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")
# The run's margin, orbit and air rules (EDGE_H margins, INSOL_K, all ice's air, the ice's own effects on top): the zoom took the honest ones first (PW-555 stage
# 1: margin_ramp, the seasons' response); the run takes them in stage 3. Until then this checks the rest of the
# shared rule (the balance, the Nye profile, the marine budget) with the run's own margins and orbit.
RUN_RULE = dict(margin="edge", front="edge", orbit_resp="run", sheet_air="all", surface_air="all")
FLT = 1 - P.RHO_I / P.RHO_W


# The source: a 300 Myr L5 run, whose climate feeds back on its tectonics and erosion, so any climate change
# gives another world (PW-582 attempt 2 turned seed 4 into 6 plates at -314 m of sea level). The property under
# test (at I = 0 the zoom keeps the run's ice) needs an ordinary world with polar land, not a particular one:
# every seed of SEEDS whose cold moment meets the precondition below, so the fixture tracks the current code
# without riding on one chaotic world. Of those, the ones with sheets (> 1% of cells under > 1 m: else the drift
# tests prove nothing) are the drift tests' worlds; each drift test asks seeds.PASS_RATE of them to pass.
SEEDS = tuple(range(25, 51))  # (lane A16's scan window; 14 of them are plausible on main 86d3806, 7 with sheets)
MIN_SHEETED = 5  # plausible seeds with sheets the window must give (so a 70% bar on them tolerates one world)
SL_MAX = 150.0  # m: the run's sea level within this of today's
MOC_MIN = 2.0  # Sv: the cold climate overturns in both hemispheres
POLAR_LAND = 0.25  # land's share of the cap poleward of 60 deg, in at least one hemisphere (where sheets can grow)


def _cold(src):
    """src made 4 C colder, with the sheets the run's own ice rule gives that climate
    (6 climate updates from no ice; as tools/ice_probe.py); and the last update's climate."""
    g = src["grid"]
    dT = src["dT"] - 4.0
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
    return dict(src, elev=e, ice=ice0, dT=dT), c


def _plausible(src, c):
    """The precondition: a plausible sea level, an overturning in both hemispheres and polar land."""
    lat, land = src["grid"].lat, src["elev"] > 0
    sink = np.where(land, 0.0, c["overturning"])
    cap = max(land[lat > 60].mean(), land[lat < -60].mean())
    return (abs(src["sea_level"]) <= SL_MAX and sink[lat > 0].sum() >= MOC_MIN and sink[lat < 0].sum() >= MOC_MIN
            and cap >= POLAR_LAND)


def _moment(seed):
    """The seed's L5 300 Myr moment made 4 C colder (_cold) and its 20 kyr zoom, if it meets _plausible's
    precondition (else None): (src, zoom). Its run's dT is kept as src["run_dT"]."""
    src0 = Z.source_from_sim(run_sim(level=5, seed=seed, myr=300))
    src, c = _cold(src0)
    if not _plausible(src, c):
        return None
    src["run_dT"] = float(src0["dT"])
    return src, Z.simulate(src, 20.0, 0.5, 2.0, Z.TZParams(**UNFORCED, **RUN_RULE))


@pytest.fixture(scope="module")
def cold_moments(tmp_path_factory):
    """Every seed of SEEDS whose cold moment meets _plausible's precondition: [(seed, (src, zoom))]."""
    def build():
        return [(s, m) for s, m in zip(SEEDS, seeds.pool_map(_moment, SEEDS)) if m is not None]
    got = seeds.shared(tmp_path_factory, "cold_moments", build)
    if not got:
        pytest.fail(f"no seed of {SEEDS} gives a plausible source")
    return got


def _rows(case, moments):
    """case's unchanged assertions on each eligible seed, here (the moments are big to ship to a pool)."""
    rows = []
    for seed, m in moments:
        out = dict(run_dT=m[0]["run_dT"])
        try:
            case(m, out)
            rows.append((seed, True, out))
        except AssertionError as e:
            rows.append((seed, False, dict(out, error=(str(e).splitlines() or [""])[0])))
    return rows


def test_cold_moment_has_sheets(cold_moments):
    """The window gives the drift tests at least MIN_SHEETED plausible worlds with sheets (each seed's
    assertion as the single-seed test had it, in _sheets_case)."""
    rows = _rows(_sheets_case, cold_moments)
    k = sum(p for _, p, _ in rows)
    table = "\n".join(f"  seed {s:>3}: {'sheets' if p else 'none'}  {o}" for s, p, o in rows)
    print(f"cold moments with sheets: {k} of {len(rows)} plausible\n{table}")
    assert k >= MIN_SHEETED, f"{k} of {len(rows)} plausible seeds have sheets (need {MIN_SHEETED})\n{table}"


def _sheeted(cold_moments):
    return [(s, m) for s, m in cold_moments if _rows(_sheets_case, [(s, m)])[0][1]]


def _sheets_case(cold_moment, out):
    src, _ = cold_moment
    out.update(sheets_pct=100 * float((src["ice"] > 1).mean()))
    assert (src["ice"] > 1).mean() > 0.01  # (else the drift test below proves nothing)


def test_ice_speeds_plausible(cold_moments):
    """Shallow-ice speeds (D |grad s| / H, the steepest way down) under grounded sheets: interiors
    metres to tens of m/yr, outlets up to a few km/yr."""
    seeds.check_rate("ice speeds plausible", _rows(_speeds_case, _sheeted(cold_moments)))


def _speeds_case(cold_moment, out):
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
    out.update(sheet_cells=int(sheet.sum()), u_median=float(np.median(u)) if sheet.any() else float("nan"),
               u_p99=float(np.percentile(u, 99)) if sheet.any() else float("nan"),
               H_median=float(np.median(H[sheet])) if sheet.any() else float("nan"))
    assert 1.0 < np.median(u) < 100.0
    assert np.percentile(u, 99) < 5000.0
    assert 500 < np.median(H[sheet]) < 3500


def test_ice_at_index_zero_is_the_runs(cold_moments):
    """At I = 0 (an interglacial: the run's own climate) the zoom keeps the run's ice: with no orbital swing
    the default index never builds, and sea level moves little (PW-366: -43 m in 20 kyr here while the
    run's sheets were 50 kPa profiles with their margins' inner-edge rise and the time zoom melted its
    margins before its flow; PW-471: the index replaced the CO2 and ice-albedo feedbacks)."""
    seeds.check_rate("ice at index zero", _rows(_index_zero_case, _sheeted(cold_moments)))


def _index_zero_case(cold_moment, out):
    _, r = cold_moment
    out.update(index_max=max(f["stats"]["glacial_index"] for f in r["frames"]),
               sl_change_m=float(r["frames"][-1]["stats"]["sea_level_change_m"]))
    assert all(f["stats"]["glacial_index"] == 0.0 for f in r["frames"])
    assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 25.0
