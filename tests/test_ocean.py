"""Salinity and the overturning circulation (planet/ocean.py)."""

import numpy as np
import pytest

from planet import climate, ocean
from planet.grid import build_grid


@pytest.fixture(scope="module")
def basins():
    """Two continents from pole to pole (almost): two ocean basins, open
    round the south (a circumpolar channel) and in the far north."""
    g = build_grid(4)
    lon = g.lon
    land = (((lon > -20) & (lon < 20)) | ((lon > 120) & (lon < 170))) & (g.lat > -60) & (g.lat < 72)
    elev = np.where(land, 500.0, -4000.0)
    return g, elev, climate.compute(g, elev)


def _mean_sss(g, elev, c):
    a = ocean.cell_area_km2(g)
    sea = elev <= 0
    return (c["sss"] * a)[sea].sum() / a[sea].sum()


def test_output_keys_and_shapes(basins):
    g, elev, c = basins
    for k in ("sss", "density", "density_winter", "overturning", "moc_inflow", "moc_heat", "freshwater",
              "sea_evap", "sea_ice_growth"):
        assert c[k].shape == (g.n,), k
        assert np.isfinite(c[k]).all(), k
    assert isinstance(c["moc_sites"], list) and c["moc_sites"]
    assert set(c["moc_state"]) == {"share", "t_in", "s_in"}
    sea = elev <= 0
    assert (c["overturning"] >= 0).all() and (c["overturning"][~sea] == 0).all()
    assert 25 < c["sss"][sea].min() and c["sss"][sea].max() < 45
    assert 1015 < c["density"][sea].min() and c["density"][sea].max() < 1032


def test_salt_is_conserved(basins):
    """Fresh water only moves the salt around: the sea's mean salinity
    stays S0, with or without a big meltwater flux."""
    g, elev, c = basins
    assert _mean_sss(g, elev, c) == pytest.approx(ocean.S0, abs=1e-6)
    c2 = climate.compute(g, elev, melt=np.where(np.abs(g.lat) > 60, 2.0, 0.0))
    assert _mean_sss(g, elev, c2) == pytest.approx(ocean.S0, abs=1e-6)
    assert abs(c2["freshwater"][elev <= 0].mean()) < 0.05  # (its global mean is taken off)


def test_overturning_sinks_at_high_latitudes(basins):
    g, elev, c = basins
    s = c["overturning"]
    assert s.sum() > 5  # Sv
    assert s[np.abs(g.lat) < 45].sum() < 0.05 * s.sum()


def test_meltwater_weakens_the_overturning(basins):
    """A big fresh-water flux (a meltwater pulse) over the main northern
    sinking site freshens it: the sinking there weakens (some moves to the
    other basin), and so does the warm inflow it drew."""
    g, elev, c = basins
    s = c["overturning"]
    north = g.lat > 0
    j = np.argmax(np.where(north, s, 0.0))
    sea = elev <= 0
    near = sea & (np.arccos(np.clip(g.centers @ g.centers[j], -1, 1)) * 6371 < 1500)
    c2 = climate.compute(g, elev, melt=np.where(near, 3.0, 0.0))
    assert c2["sss"][near].mean() < c["sss"][near].mean() - 0.5
    assert c2["overturning"][near].sum() < 0.7 * s[near].sum()
    assert c2["overturning"][north].sum() <= s[north].sum() + 1e-9
    assert c2["moc_heat"][near].mean() < c["moc_heat"][near].mean()


def test_state_carries_over(basins):
    """Started from its own state, the overturning stays about where it is."""
    g, elev, c = basins
    c2 = climate.compute(g, elev, moc_start=c["moc_state"])
    assert c2["overturning"].sum() == pytest.approx(c["overturning"].sum(), rel=0.15)


def test_density_equation_of_state():
    """Warm water expands more per degree; salt adds ~0.77 kg/m3 per psu;
    cold water is denser than warm at the same salinity."""
    d = ocean.density
    assert d(0.0, 35.0) > d(10.0, 35.0) > d(25.0, 35.0)
    assert d(25.0, 35.0) - d(26.0, 35.0) > 3 * (d(0.0, 35.0) - d(1.0, 35.0))
    assert d(10.0, 36.0) - d(10.0, 35.0) == pytest.approx(0.766, abs=0.01)
    assert d(10.0, 35.0) == pytest.approx(ocean.RHO0)


def test_loop_schematic(basins):
    """The overturning's numbers and its schematic loop for world meta:
    totals add up, every drawn site has a deep limb ending where deep water
    wells up (the southern channel, or the tropics), and northern sites a
    surface limb from the low latitudes."""
    g, elev, c = basins
    o = ocean.loop_schematic(g, elev, c)
    assert o["sv"] == pytest.approx(c["overturning"].sum(), abs=0.01)
    assert o["north_sv"] + o["south_sv"] == pytest.approx(o["sv"], abs=0.02)
    assert o["sites"] and o["paths"] and o["upwelling"]
    for p in o["paths"]:
        assert p["limb"] in ("surface", "deep") and len(p["pts"]) >= 2
        assert all(-90 <= la <= 90 and -180 <= lo <= 180 for la, lo in p["pts"])
        s = o["sites"][p["site"]]
        assert s["sv"] >= ocean.LOOP_MIN_SV
        if p["limb"] == "deep":
            assert p["pts"][0] == [s["lat"], s["lon"]]  # from the site itself
            end = p["pts"][-1][0]
            assert end < -45 or abs(end) < 8
        else:
            assert abs(p["pts"][-1][0]) <= 26  # from the low latitudes


def test_seasonal_sst_and_humidity(basins):
    g, elev, c = basins
    sea = elev <= 0
    north = g.lat >= 0
    hot = np.where(north, c["sst_jul"], c["sst_jan"]) - np.where(north, c["sst_jan"], c["sst_jul"])
    assert (hot[sea] >= -1e-9).all() and hot[sea].max() > 3  # summer seas warmer
    assert (c["sst_jul"][sea] >= climate.FREEZE - 1e-9).all()
    for s in ("jul", "jan"):
        rh = c["rh_" + s]
        assert (rh >= 100 * climate.HUMID_MIN - 1e-6).all() and (rh <= 100).all()
        assert 60 < np.median(rh[sea]) < 90
        t = climate.humidity(np.ones(1), np.zeros(1), climate.TUNE)
        assert t[0][0] <= 0 and 80 < t[1][0] < 90  # saturated at 0 C: ~84%, dew point a little below


def test_clouds_and_sunshine(basins):
    """Cloud cover (climate.clouds): cloudy where the air rises (the tropical
    rain belt) and in the storm tracks, clear under the sinking subtropical
    air over land, and a stratocumulus deck on the eastern side of the
    oceans' subtropics (cool upwelling under the inversion): cloudier than
    the western side there with far less rain. Sunshine hours never exceed
    the day's length."""
    g, elev, c = basins
    sea, lat, lon = elev <= 0, g.lat, g.lon
    days = climate.day_hours(lat)
    for k, (s, shift) in enumerate((("jul", 6.4), ("jan", -6.4))):
        cl, p = c["cloud_" + s], c["p_" + s]
        assert np.isfinite(cl).all() and (cl >= 0).all() and (cl <= 1).all()
        assert ((c["sun_" + s] >= 0) & (c["sun_" + s] <= days[k] + 1e-9)).all()
        assert cl[sea & (np.abs(lat - shift) < 6)].mean() > 0.6  # the tropical rain belt
        assert cl[sea & (lat < -50) & (lat > -65)].mean() > 0.75  # the Southern Ocean's storms
        assert cl[~sea & (np.abs(np.abs(lat) - 25) < 6)].mean() < 0.45  # the subtropical deserts
        band = sea & (np.abs(np.abs(lat - shift) - 25) < 6) & (np.abs(lat) < 40)
        east = band & (((lon > -35) & (lon < -20)) | ((lon > 105) & (lon < 120)))  # off the west coasts
        west = band & (((lon > 20) & (lon < 35)) | (lon > 170) | (lon < -175))  # off the east coasts
        assert cl[east].mean() > cl[west].mean() + 0.1 and p[east].mean() < 0.6 * p[west].mean()
    # the dry winter air keeps a background of vapour (PW-151): little air sits at the floor
    assert (c["rh_jan"] <= 100 * climate.HUMID_MIN + 0.5).mean() < 0.02
