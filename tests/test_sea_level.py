"""Sea level follows the ocean basins against a fixed reference
(planet/tectonics/earth.py, PW-288)."""

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics import earth
from planet.tectonics.isostasy import RHO_MANTLE, RHO_WATER


def test_basin_term_is_measured_against_the_starting_floor():
    """depth_ref is the first step's mean floor depth and never moves; the
    basin term is (rho_m - rho_w) / rho_m of the smoothed floor's shallowing
    (the water's own load sinks the floor by the rest), softly limited."""
    s = Simulation(build_grid(4), 1, Params(heat_start=1.0), 2.0)
    s.run(2)
    ref = s.depth_ref
    seen = []
    for _ in range(40):
        s.step()
        assert s.depth_ref == ref
        rise = (RHO_MANTLE - RHO_WATER) / RHO_MANTLE * (s.depth_ridge - ref)
        assert np.isclose(s.sea_tect, earth.SEA_TECT_MAX * np.tanh(rise / earth.SEA_TECT_MAX))
        seen.append(rise)
    assert max(abs(x) for x in seen) > 1.0  # (the floor did change)
    assert abs((RHO_MANTLE - RHO_WATER) / RHO_MANTLE - 0.69) < 0.01
