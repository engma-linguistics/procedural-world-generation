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


def _coastal_belt(sim):
    """A continental coast cell with an ocean neighbour of its own plate, thickened with its continental
    neighbours into a 70-km dead belt (never folded). Returns (Column, coast cell, its ocean neighbours)."""
    from planet.tectonics import record
    from planet.tectonics.crust import Column
    g, own, c = sim.grid, sim.owner, sim.w_cont
    col = Column(t=sim.w_thick.copy(), cover=sim.w_cover.copy(), x=sim.w_extra.copy(), cont=c.copy(),
                 rock=sim.w_rock.copy(), rec=sim.w_rec.copy(), lith=sim.w_lith.copy())
    for i in np.random.default_rng(0).permutation(g.n):
        nb = np.asarray(g.neighbors[i])
        sea = nb[~c[nb] & (own[nb] == own[i])]
        if c[i] and len(sea) and (own[nb] == own[i]).all() and c[nb].sum() >= 3:
            belt = np.concatenate([[i], nb[c[nb]]])
            col.t[belt] = 70.0
            col.cover[belt] = 0.0
            col.x[belt] = 0.0
            col.rec[:, record.T_FOLD] = record.NEVER
            return col, i, sea
    raise AssertionError("no coast cell")


def test_a_dead_belt_at_the_coast_spreads_seaward_and_widens_the_continent():
    """PW-1693: with collapse_margin on, a thick dead belt at a continent's edge also flows into its plate's ocean
    cell next to it, which becomes thin continental crust once it holds BECOMES_CONT_KM: the continent gains area,
    the crust's volume is kept. Off (the default), and at a trench, collapse stays inside the continent."""
    from planet.tectonics.isostasy import BECOMES_CONT_KM
    n = build_grid(5).n
    out = {}
    for name, cm, at_trench in (("off", 0.0, False), ("on", 1.0, False), ("trench", 1.0, True)):
        sim = Simulation(build_grid(5), 1, Params(collapse_margin=cm), 2.0)
        sim.dt_now = 5.0
        col, coast, sea = _coastal_belt(sim)
        trench = np.zeros(n, bool)
        if at_trench:
            trench[coast] = True
        v0 = col.t.sum()
        area0 = col.cont.sum()
        crust.flow_and_orogeny(sim, col, crust.inner_edges(sim, col.cont), np.zeros(n), trench)
        assert abs(col.t.sum() - v0) < 1e-6 * v0  # volume kept (ocean and continent together)
        out[name] = (col.cont.sum() - area0, col.t[sea].max())
        if name == "on":
            grown = sea[col.cont[sea]]
            assert len(grown) and (col.t[grown] >= BECOMES_CONT_KM).all()
            assert sim.budget.get("collapse.margin", 0) > 0
    assert out["off"][0] == 0 and out["trench"][0] == 0
    assert out["on"][0] > 0, out
