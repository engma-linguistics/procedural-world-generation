"""tools/moisture_budget.py: its instrumented copy of the rain kernel must stay the model's kernel."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from planet import climate  # noqa: E402
from tools import moisture_budget as mb  # noqa: E402


@pytest.fixture(scope="module")
def recorded():
    from planet.grid import build_grid
    g = build_grid(4)
    rng = np.random.default_rng(3)
    elev = np.where(rng.random(g.n) < 0.3, rng.uniform(0, 3000, g.n), -3000.0)
    c, rec = mb.capture(g, elev, None, compute=lambda: climate.compute(g, elev, 0.0, 23.4))
    return g, elev, c, rec


def test_probe_is_the_kernel(recorded):
    """The probe is climate._rain line for line: same rain, uptake and vapour, bit for bit
    (if this fails, climate._rain changed: copy the change into moisture_budget._probe)."""
    g, elev, c, rec = recorded
    want = climate._rain(*mb.kernel_args(rec))
    tag = np.where(elev <= 0, 0, 1)
    P = mb.probe(rec, tag, 2)
    for k, w in zip(("r", "r_ls", "up", "q"), want):
        assert np.array_equal(P[k], w), k
    assert np.array_equal(mb.storm_mixed(g, rec, P["r"], P["r_ls"]), rec["out"][0])
    # the tracers account for all the rain
    assert np.allclose(P["r_tag"].sum(1), P["r"], rtol=1e-9, atol=1e-15)


def test_face_fluxes_close_the_budget(recorded):
    """Northward vapour flux across a latitude circle through the kernel's faces = the sources minus
    the rain south of it (the transport is conservative: only the steady state's drift is left)."""
    g, elev, c, rec = recorded
    P = mb.probe(rec, np.zeros(g.n, np.int64), 1)
    F = climate._faces(g)
    lat, a, b = g.lat, F["ea"], F["eb"]
    for k in range(2):
        net = (P["up"][k] + P["land_e"][k] - P["r"][k]) * F["A"]  # model units x m2 per step
        scale = np.abs(net).sum()
        flux = (P["f_adv"][k] + P["f_mix"][k]) * P["dt"]
        for phi in (-30.0, 0.0, 30.0):
            sgn = np.where((lat[a] < phi) & (lat[b] >= phi), 1.0, np.where((lat[b] < phi) & (lat[a] >= phi), -1.0, 0))
            assert abs((flux * sgn).sum() - net[lat < phi].sum()) < 0.005 * scale, (k, phi)
