"""Collision belts and the continents' crust volume (PW-046, PW-284)."""

from types import SimpleNamespace

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation, crust


def _two_plates(sim):
    """The starting supercontinent cut in two plates along a meridian: the
    edges between them, all continental, as a collision."""
    g = sim.grid
    other = int(sim.owner.max()) + 1 if sim.owner.max() + 1 < sim.plates.alive.size else 0
    east = sim.w_cont & (g.lon > np.median(g.lon[sim.w_cont]))
    sim.owner = np.where(east, other, sim.owner)
    a, b = g.edges[:, 0], g.edges[:, 1]
    m = (sim.owner[a] != sim.owner[b]) & sim.w_cont[a] & sim.w_cont[b]
    return SimpleNamespace(a=a[m], b=b[m], collision=np.ones(m.sum(), bool)), east


def _excess(sim, t):
    g = sim.grid
    nb, c = g.nbr_idx, sim.w_cont
    st = np.add.reduceat(np.where(c[nb], t[nb], 0.0), g.nbr_off[:-1])
    nc = np.add.reduceat(c[nb].astype(int), g.nbr_off[:-1])
    return np.where(c & (nc > 0), t - st / np.maximum(nc, 1), 0.0)


def test_stacked_crust_spreads_over_both_sides_of_a_collision():
    """A belt straddles its suture: crust stacked at the front reaches the
    other plate's side too, so no single front cell piles up far above its
    neighbours; volume kept."""
    sim = Simulation(build_grid(5), 1, Params(), 2.0)
    bd, east = _two_plates(sim)
    front = bd.a[len(bd.a) // 2]
    stacked = np.zeros(sim.grid.n)
    stacked[front] = 35.0  # one cell's worth of the other continent, shortened away
    peaks = {}
    for name, b in (("one plate", None), ("both", bd)):
        t = sim.w_thick.copy()
        col = SimpleNamespace(t=t.copy(), cont=sim.w_cont)
        add = crust.stack_collisions(sim, col, stacked, crust.inner_edges(sim, sim.w_cont, b))
        assert abs(add.sum() - 35.0) < 1e-9
        peaks[name] = _excess(sim, t + add)[front]
        if b is not None:
            side = east[front]
            assert add[sim.w_cont & (east != side)].sum() > 5.0  # across the suture
    assert peaks["both"] < 0.8 * peaks["one plate"], peaks


def test_the_continents_start_at_the_volume_thermostats_target():
    """PW-046: the starting continents have the mean thickness the volume
    thermostat holds, so a run doesn't spend its first ~250 Myr shedding the
    difference (and wind up the thermostat's integral term meanwhile)."""
    for seed, kw in ((1, {}), (2, {"continental_thickness": 38.0}), (3, {"continental_start": 0.15})):
        sim = Simulation(build_grid(5), seed, Params(**kw), 2.0)
        c = sim.w_cont
        p = sim.params
        assert abs((sim.w_thick * c).sum() / c.sum() - p.continental_thickness) < 0.05
        assert abs((sim.w_thick * c).mean() / (sim.target_fraction() * p.continental_thickness) - 1) < 0.01


def test_arc_outgassing_is_the_slabs_melt_not_the_volume_thermostats_gain():
    """PW-741: the CO2 the arcs outgas is their crust growth at the nominal rate, the melt the slabs make. The
    volume thermostat's gain (which holds the continents' volume on target, and climbed to ~3 at L6 but stayed
    ~1.5 at L7) speeds the Andean arcs' crust growth but not their outgassing, so it can't warm the climate."""
    from planet.tectonics import motion
    sim = Simulation(build_grid(5), 1, Params(), 2.0)
    for _ in range(60):  # (until a trench runs under a continent: an Andean arc)
        sim.step()
        bd = motion.boundaries(sim)
        if (sim.w_cont[bd.overriding] & (bd.at_trenches(np.clip(bd.conv, 0, 15)) > 0)).any():
            break
    conv = np.clip(bd.conv, 0, 15)
    g1, n1 = crust.arc_growth(sim, bd, conv, 1.0)
    g3, n3 = crust.arc_growth(sim, bd, conv, 3.0)
    assert n1.sum() > 0 and np.array_equal(n1, n3) and np.allclose(g1, n1)
    assert g3.sum() > n3.sum() + 0.1  # (the gain still builds the continental arcs' crust)
    assert np.all(g3 >= n3 - 1e-12) and np.all(g3 <= 3.0 * n3 + 1e-12)
