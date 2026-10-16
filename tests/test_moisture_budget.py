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


def test_edge_fluxes_close_the_budget(recorded):
    """Northward vapour flux across a latitude circle from the kernel's edges = the sources minus
    the rain south of it (in the kernel's own cell units), up to the transport's small residue."""
    g, elev, c, rec = recorded
    P = mb.probe(rec, np.zeros(g.n, np.int64), 1)
    F = mb.edge_fluxes(g, rec, P["q"])
    lat, src, dst = g.lat, F["src"], F["dst"]
    for k in range(2):
        net = P["up"][k] + P["land_e"][k] - P["r"][k]
        scale = np.abs(net).sum()
        for phi in (-30.0, 0.0, 30.0):
            cross, back = (lat[src] < phi) & (lat[dst] >= phi), (lat[src] >= phi) & (lat[dst] < phi)
            flux = F["adv"][k][cross].sum() + F["mix"][k][cross].sum() - F["adv"][k][back].sum()
            south = lat < phi
            implied = net[south].sum() + (F["res_move"][k] + F["res_mix"][k])[south].sum()
            assert abs(flux - implied) < 0.02 * scale, (k, phi, flux, implied)
