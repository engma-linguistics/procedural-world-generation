"""The sheets' carried air within a climate update (PW-1050): climate.compute's reground and earth.ice_air_rounds."""

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


def test_ice_air_rounds_stop_at_the_cap_and_off_keeps_the_first_settling(sim4_60):
    s = sim4_60
    g, e, land, ice, sheet = _ground_sheet(s)
    c = climate.compute(g, e, s.dT, s.params.tilt, sheet)  # (the climate saw a sheet the ice will shrink from)
    marine = earth.marine_view(e, c)
    first = earth.ice_sheets(s, land, e, c["ground"], sheet, s.ice_sink, {}, marine=marine)
    keep = s.ice  # (a session fixture: put its ice and params back)
    for rounds in (0, 1, 4):
        s.params.ice_air_rounds = float(rounds)
        s.ice, info = first.copy(), {}
        out, ground = earth.ice_air_rounds(s, land, e, c, sheet, marine, info)
        assert 0 <= info["air_rounds"] <= rounds
        if rounds == 0:
            assert np.array_equal(out, first) and ground is c["ground"]
    s.params.ice_air_rounds, s.ice = 4.0, keep
