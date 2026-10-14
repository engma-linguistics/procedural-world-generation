"""The crust budget: where continental crust is made, thickened, thinned
and destroyed each step.

Every cell carries a crust thickness, and elevation follows from it by
isostasy (isostasy.py). Arcs add crust above subducting slabs (Andes,
Japan); collisions stack it (Himalaya/Tibet), very thick crust flows
sideways, rifts stretch it thin, trenches scrape sediment onto it and grind
its edge away. Two gentle thermostats hold the continents' area and volume
near their targets, so they neither leak away nor swell over billions of
years.

All of this works on a Column: the world-frame crust of this step, which
Simulation._physics threads through its substeps and finally writes back to
the plates. Every change to continental crust is booked (Simulation.book)
next to the line that makes it, so the budget shows where crust went.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .. import kernels, surface
from ..geo import R_KM
from ..surface import ARC, CRATON, HOTSPOT, OCEAN, OROGEN, SEDIMENT
from .isostasy import BECOMES_CONT_KM, LAVA, MAX_KM, MIX, OCEAN_KM
from .plate_kernels import crust_flow
from .plates import P_MAX


@dataclass
class Column:
    """The world-frame crust being worked on during one step (per cell)."""
    t: np.ndarray  # km of crust
    cover: np.ndarray  # km of sediment on top
    x: np.ndarray  # isostasy.EXTRA columns
    cont: np.ndarray  # continental
    rock: np.ndarray  # basement rock id


def thermostats(sim):
    """Arcs: melting above the sinking slab adds new crust to the overriding
    plate. A thermostat holds continental area near continental_fraction
    (real growth vs. loss at trenches is roughly balanced but uncertain).
    Two gentle thermostats: arc growth (adds crust) follows the volume
    of continental crust, subduction erosion (removes continental
    edges) its area. Together they hold both near their targets, and so
    the average thickness, which decides how high continents stand.
    Returns (arc growth factor, subduction erosion factor)."""
    p = sim.params
    frac = max(sim.w_cont.mean(), 1e-3)
    vol = max(float((sim.w_thick * sim.w_cont).mean()), 1e-3)
    target = sim.target_fraction()
    thermostat = np.clip((target * p.continental_thickness / vol) ** 4, 0.1, 5.0)
    shrink = np.clip((frac / target) ** 4, 0.2, 5.0)
    return thermostat, shrink


def spread(sim, src_rate, width):
    """A rate at source cells, spread over a Gaussian belt `width` level-5
    cells wide on the same plate."""
    g, n = sim.grid, sim.grid.n
    src = np.flatnonzero(src_rate > 0)
    if len(src) == 0:
        return np.zeros(n)
    w = width * sim.scale
    dist, s = kernels.bfs_within(src, sim.owner, g.nbr_off, g.nbr_idx, int(3 * w))
    out = np.zeros(n)
    hit = s >= 0
    out[hit] = src_rate[s[hit]] * np.exp(-((dist[hit] / w) ** 2))
    return out


def arc_growth(sim, bd, conv, thermostat):
    """km/Myr of new arc crust per cell, behind every trench."""
    p = sim.params
    arc_src = np.zeros(sim.grid.n)
    np.maximum.at(arc_src, bd.overriding, p.arc_growth * sim.heat() * thermostat * bd.at_trenches(conv))
    return spread(sim, arc_src, 1.6)


def rift_stretching(sim, bd):
    """Rifting stretches continental crust thin near the opening boundary;
    that thinned crust is why continents have drowned shelves and slopes.
    Returns the thinning rate (per Myr) per cell."""
    p = sim.params
    a, b = bd.a, bd.b
    rift_src = np.zeros(sim.grid.n)
    op = bd.opening
    opening_rate = -np.clip(bd.conv[op], -15, 0)
    # only crust that hasn't been thinned yet keeps a rift stretching:
    # once the edge is thin (or the rift floor is new margin or ocean)
    # the stretching moves to the ridge and the margin is left behind
    fresh = sim.w_cont & (sim.w_thick > 23.0)
    np.maximum.at(rift_src, a[op], p.stretching * opening_rate * fresh[a[op]])
    np.maximum.at(rift_src, b[op], p.stretching * opening_rate * fresh[b[op]])
    return spread(sim, rift_src, 1.0)


def add_arcs_and_plumes(sim, col, growth, plume):
    """New crust from arcs and plumes. On a continent the plume's lava
    spreads over the land as a cover of basalt flows (Snake River Plain,
    Deccan Traps)."""
    dt, cont = sim.dt, col.cont
    col.t = col.t + growth * dt + plume * dt
    sim.book("arc", 0, growth * dt, cont)
    sim.book("plume", 0, plume * dt, cont)
    col.cover = col.cover + plume * dt * cont
    col.x[:, LAVA] += plume * dt * cont


def inner_edges(sim, cont):
    """Grid edges inside one continent on one plate (where crust can be
    spread sideways): (ea, eb)."""
    g = sim.grid
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    both = (sim.owner[ea] == sim.owner[eb]) & cont[ea] & cont[eb]
    return ea[both], eb[both]


def stack_collisions(sim, col, stacked, edges):
    """Collisions: the crust that was shortened away (stacked: km per cell,
    from plate_kernels.resolve) is stacked into a belt a few hundred km
    wide (Himalaya + Tibet), not one cell. Returns km added per cell."""
    if not stacked.any():
        return np.zeros(sim.grid.n)
    stack_add = surface._spread(stacked, edges[0], edges[1], 0.15, int(round(6 * sim.scale**2)))
    col.t = col.t + stack_add
    sim.book("collision", 0, stack_add, col.cont)
    return stack_add


def accrete(sim, bd, conv, col):
    """Trenches scrape part of the sediment off the sinking plate onto the
    edge of the overriding one (accretionary wedges: Makran, Barbados,
    much of Japan); the rest goes down with the slab. The share scraped
    per step grows with how much plate the trench swallows in it."""
    p, n, dt = sim.params, sim.grid.n, sim.dt
    if p.accretion <= 0:
        return
    dn, up, cv = bd.sinking, bd.overriding, bd.at_trenches(conv)
    share = p.accretion * np.minimum(1.0, cv * 10 * dt / (sim.edge_len * R_KM))
    scraped = np.zeros(n)
    np.maximum.at(scraped, dn, share * col.cover[dn])
    gain = np.zeros(n)
    np.add.at(gain, up, scraped[dn] / np.maximum(np.bincount(dn, minlength=n)[dn], 1))
    keep = 1 - scraped / np.maximum(col.cover, 1e-9)
    col.x[:, MIX] *= keep[:, None]
    col.t, col.cover = col.t - scraped + gain, col.cover - scraped + gain
    sim.book("accreted", 0, gain, col.cont)


def subduction_erosion(sim, bd, conv, col, shrink):
    """Subduction erosion: the slab also grinds away the underside and
    front of the overriding continent and drags it down (the Andes'
    coast has retreated ~250 km since the Jurassic). Globally it removes
    about as much continental crust as arcs add. A continental edge cell
    worn below 15 km is gone: what's left counts as oceanic."""
    p, n, dt = sim.params, sim.grid.n, sim.dt
    if p.subduction_erosion <= 0:
        return
    up, cv = bd.overriding, bd.at_trenches(conv)
    worn = np.zeros(n)
    np.maximum.at(worn, up, p.subduction_erosion * cv * dt * shrink)
    worn = np.minimum(worn * col.cont, col.t)
    t0 = col.t
    t = col.t = col.t - worn
    sim.book("subd.erosion", t0, t, col.cont)
    gone = col.cont & (worn > 0) & (t < 15.0)
    if gone.any():
        sim.book("subd.erosion", t, 0, gone)
        col.cont = col.cont.copy()
        col.cont[gone] = False
        col.rock[gone] = OCEAN
        t[gone] = OCEAN_KM
        col.cover[gone] = 0.0
        col.x[gone] = 0.0


def arc_rock(sim, col, growth):
    """Arc rock: on continents wherever arcs build; at sea only once the
    crust has thickened into a real island arc. Returns where."""
    arcky = (growth * sim.dt > 0.1) & (col.rock != CRATON) & (col.cont | (col.t > OCEAN_KM + 5))
    col.rock[arcky] = ARC
    return arcky


def stretch(sim, col, rate, plume, newc):
    """Thin stretched continental crust (rate per Myr from rift_stretching)
    down to 22 km, floor the opening rifts with what it lost
    (rifted_margin), and mark ocean-floor plume piles as hotspot rock."""
    dt, t = sim.dt, col.t
    thin = col.cont & (t > 22)
    t0 = t.copy()
    t[thin] = np.maximum(22.0, t[thin] * np.exp(-rate[thin] * dt))
    sim.book("stretch", t0, t, col.cont)
    rifted_margin(sim, t0 - t, col, newc)
    col.rock[~col.cont & (plume * dt > 0.2)] = HOTSPOT


def rifted_margin(sim, lost, col, newc):
    """Stretching doesn't destroy crust, it spreads it thinner over a
    wider area: the opening rift is floored by thinned continental crust
    (rifted margins: 10-25 km thick, 100-300 km wide, under 1-4 km of sea)
    before true ocean floor appears. The crust a plate's continental edge
    loses to stretching is pooled and laid down as new margin cells in
    the gap next to it (newc: the new ocean floor of this step).
    In place on col (and sim.w_age)."""
    g, p, pl = sim.grid, sim.params, sim.plates
    own = sim.owner
    cont = col.cont
    pl.rift_pool += np.bincount(own, np.maximum(lost, 0) * cont, P_MAX)
    pl.rift_pool *= np.exp(-sim.dt / 100.0)  # a rift that never opens keeps it in its thickened flanks... eventually
    if p.rift_margin_km <= 0 or not newc.any():
        return
    near, src = kernels.bfs_within(np.flatnonzero(cont), own, g.nbr_off, g.nbr_idx, int(round(2 * sim.scale)))
    cand = newc & ~cont & (near > 0)
    if not cand.any():
        return
    cont = col.cont = cont.copy()
    for k in np.unique(own[cand]):
        n_cells = int(pl.rift_pool[k] // p.rift_margin_km)
        if n_cells <= 0:
            continue
        cells = np.flatnonzero(cand & (own == k))
        cells = cells[np.argsort(near[cells], kind="stable")][:n_cells]
        s = src[cells]
        col.t[cells] = p.rift_margin_km
        cont[cells] = True
        col.rock[cells] = col.rock[s]
        sim.w_age[cells] = sim.w_age[s]
        col.cover[cells] = 0.0
        col.x[cells] = 0.0
        pl.rift_pool[k] -= len(cells) * p.rift_margin_km
        sim.book("margin", 0, p.rift_margin_km, np.isin(np.arange(g.n), cells))


def flow_and_orogeny(sim, col, edges, stack_add):
    """Crustal flow: very thick crust is hot and weak at depth and spreads
    sideways (Tibet is doing this now), within a continent on one plate.
    Faster the thicker it is, which is why crust >~70 km is so rare.
    A diffusion: per-cell rates scale with 1/spacing^2, so finer grids
    take more (equally stable) substeps.
    Then collision belts are folded, faulted and metamorphosed wherever the
    crust is being stacked up, whatever it was before (an old arc,
    sediment); very thick crust is metamorphosed too. Returns where crust
    is being squeezed."""
    p, dt, cont, rock = sim.params, sim.dt, col.cont, col.rock
    t0 = col.t
    # (a hotter planet's crust is softer: mountains and plateaus can't stand as high)
    t = crust_flow(col.t, edges[0], edges[1], p.crust_flow * sim.heat() ** 2 * dt / 3,
                   int(round(3 * sim.scale**2 * sim.heat() ** 2)))
    t = col.t = np.minimum(t, MAX_KM)
    sim.book("flow+cap", t0, t, cont)
    squeezed = cont & (stack_add > 0.05 * dt)
    rock[squeezed & (rock != CRATON)] = OROGEN
    rock[(t > 50) & cont & (rock != CRATON) & (rock != ARC)] = OROGEN
    return squeezed


def birth_and_cratons(sim, col, arcky, squeezed):
    """Ocean crust thickened enough by arcs or sediment becomes continental;
    hotspot piles (Hawaii, Iceland) stay oceanic however big, unless
    it's sediment from a nearby continent that's piling up on them.
    Rock age (continents): crust that's just formed or been remelted /
    metamorphosed starts again at 0. Old, cool, untouched crust
    stiffens into craton (Canada, Siberia, Africa's shields).
    Updates sim.w_age; returns the cells born continental."""
    p, t, cont, rock = sim.params, col.t, col.cont, col.rock
    sedimented = col.cover > 0.5 * (t - OCEAN_KM)
    born = ~cont & (t >= BECOMES_CONT_KM) & ((rock != HOTSPOT) | sedimented)
    rock[born] = np.where(sedimented[born], SEDIMENT, ARC)
    sim.book("born", 0, t, born)
    age = sim.w_age.copy()
    age[born | (cont & arcky)] = 0.0
    age[squeezed & (rock != CRATON)] = 0.0
    sim.w_age = age
    rock[cont & (age > p.craton_age) & (t < 45) & (rock != CRATON) & (rock != HOTSPOT)] = CRATON
    return born
