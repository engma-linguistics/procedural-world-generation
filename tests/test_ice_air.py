"""The sheets' carried air within a climate update (PW-1050): climate.compute's reground and earth.ice_sheets'
re-making of it."""

import numpy as np

from planet import climate, nest
from planet.tectonics import earth


def _ground_sheet(s):
    g = s.grid
    e = s.w_elev
    land = e > 0
    ice = np.where(land, s.ice, 0.0)
    sheet = np.where(land & (np.abs(g.lat) > 55), np.maximum(ice, 1500.0), ice)  # (a big polar sheet, wherever land is)
    return g, e, land, ice, sheet


def test_reground_of_the_climates_own_ice_is_its_ground_and_a_bigger_sheet_chills_it(sim4_60):
    s = sim4_60
    g, e, land, ice, sheet = _ground_sheet(s)
    assert (sheet > ice).any()
    for c in (climate.compute(g, e, s.dT, s.params.tilt, ice), nest.climate_coarse(g, 3, e, s.dT, s.params.tilt, ice)):
        same = c["reground"](ice)
        for a, b in zip(same, c["ground"]):
            assert np.array_equal(a, b)
        warm = c["reground"](sheet)[0]
        on = sheet > ice
        # the new sheet's own air damps its summers (and its margins'); nothing warms
        assert warm[on].mean() < c["ground"][0][on].mean() - 0.5
        assert (warm <= c["ground"][0] + 1e-9).all()


def test_ice_sheets_remake_the_air_at_most_the_cap_and_off_is_the_plain_fixed_point(sim4_60):
    s = sim4_60
    g, e, land, ice, sheet = _ground_sheet(s)
    c = climate.compute(g, e, s.dT, s.params.tilt, sheet)  # (the climate saw a sheet the ice will shrink from)
    marine = earth.marine_view(e, c)
    plain = earth.ice_sheets(s, land, e, c["ground"], sheet, s.ice_sink, {}, marine=marine)
    keep = s.params.ice_air_rounds  # (a session fixture: put its params back)
    try:
        for rounds in (0, 1, 8):
            s.params.ice_air_rounds = float(rounds)
            info = {}
            out = earth.ice_sheets(s, land, e, c["ground"], sheet, s.ice_sink, info, marine=marine,
                                   reground=c["reground"])
            assert 0 <= info["air_rounds"] <= rounds
            assert info["air_capped"] == (rounds > 0 and info["air_rounds"] == rounds)
            if rounds == 0:
                assert np.array_equal(out, plain) and info["ground"] is c["ground"]
            else:
                assert info["air_rounds"] >= 1  # (the sheet shrank by far more than AIR_SEA_TOL)
    finally:
        s.params.ice_air_rounds = keep


def test_the_surface_damps_only_the_air_that_isnt_the_sheets(sim4_60):
    """(a): air_mass is sheet_air on the ice; the surface's own damping is LOCAL x (1 - sheet air), so a big
    sheet's margin takes less of its summer off twice, and with no sheet air it is LOCAL as before."""
    from planet import icemass
    s = sim4_60
    g, e, land, ice, sheet = _ground_sheet(s)
    a = icemass.sheet_air(g, sheet)
    on = sheet > 1
    assert np.array_equal(icemass.air_mass(g, sheet), np.where(on, a, 0.0))
    assert a[on].max() > 0.2
    plain, fixed = icemass.sheet_cover(g, sheet), icemass.sheet_cover(g, sheet, air=a)
    assert np.allclose(plain, icemass.LOCAL) and np.allclose(fixed, icemass.LOCAL * (1 - a))
    assert np.allclose(icemass.sheet_cover(g, sheet, air=np.zeros(g.n)), plain)


def _year(t_mean, half, cool=2.0):
    from planet.timezoom.kernels import climate_step
    n = 2
    z, o = np.zeros(n), np.ones(n)
    out = [np.zeros(n) for _ in range(6)]  # smb, t_ann, t_warm, t_cold, p_scale, f_sum
    climate_step(np.zeros(n, bool), np.array([True, False]), np.full(n, t_mean), np.full(n, half), z, z, z, z,
                 z, np.zeros(n, np.int64), np.zeros((1, 12)), o, z, cool, z, 0.5, 0.3, 30.0, 5.0, 3.0, 8.0, 0.6,
                 0.07, *out)
    return out[1:4]


def test_the_inversion_follows_the_season_only_where_the_summer_melts():
    """PW-1050 (b), PW-1095: thick ice's ICE_COOL keeps its annual mean everywhere. Its seasonal swing (none at
    midsummer, twice it at midwinter) is scaled by the share of the warmest month's days the air reaching the
    surface is above freezing: a melting margin loses its inversion in summer, a plateau that never melts keeps
    it all year (the kernel shared by the run, the worlds, the zoom and the time zoom)."""
    # a melting margin: the air's warmest month +20 C, share ~1: (b)'s full swing
    t_ann, t_warm, t_cold = _year(0.0, 20.0)
    assert np.allclose(t_warm, 20.0, atol=1e-3) and np.allclose(t_cold, -24.0, atol=1e-3) and np.allclose(t_ann, -2.0)
    # a plateau: the air's warmest month -30 C, share ~0: the same inversion all year
    t_ann, t_warm, t_cold = _year(-40.0, 10.0)
    assert np.allclose(t_warm, -32.0, atol=1e-3) and np.allclose(t_cold, -52.0, atol=1e-3)
    assert np.allclose(t_ann, -42.0)
    # in between (warmest month at 0 C: half its days above freezing), half the swing; the annual mean is kept
    t_ann, t_warm, t_cold = _year(-10.0, 10.0)
    s = 0.5  # (erfc(0) = 1)
    assert np.allclose(t_warm, -2.0 * (1 - s)) and np.allclose(t_cold, -20.0 - 2.0 * (1 + s))
    assert np.allclose(t_ann, -12.0)
