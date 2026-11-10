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
from ..surface import ARC, CRATON, FLOOD_BASALT, GRANITE, HOTSPOT, OCEAN, OROGEN, SEDIMENT, SHALE, TUFF
from . import record
from .isostasy import BECOMES_CONT_KM, LAVA, LAVA_MAX_KM, MAX_KM, MIX, OCEAN_KM, TUFF as TUFF_X, max_km
from .plate_kernels import crust_flow
from .plates import P_MAX

TUFF_SHARE = 0.1  # of the new arc crust on a continent that erupts as ash and ignimbrite sheets (cover)
GRANITE_KM = 4.0  # km of erosion since an arc went quiet that exposes its plutons (a batholith)
RIFT_THINNING = 0.015  # per Myr: crust thinning faster than this is being rifted (record.t_rift)
FOREARC_KM = 120.0  # km: width of the forearc (arc-trench gap) that subduction erosion grinds
L5_KM = 240.0  # km between level-5 cells (the unit of spread widths)
THERMO_MYR = 100.0  # Myr: the thermostats' memory of a persisting error (integral time)
THERMO_MAX = 0.4  # at most x e^(4 x 0.4) ~ 5 from that memory


@dataclass
class Column:
    """The world-frame crust being worked on during one step (per cell)."""
    t: np.ndarray  # km of crust
    cover: np.ndarray  # km of sediment on top
    x: np.ndarray  # isostasy.EXTRA columns
    cont: np.ndarray  # continental
    rock: np.ndarray  # basement rock id
    rec: np.ndarray  # record.RECORD columns: strata and history
    lith: np.ndarray  # record: the strata's rocks
    eroded_cover: np.ndarray | None = None  # km of cover erosion took this step (earth.erode)


def thermostats(sim):
    """Arcs: melting above the sinking slab adds new crust to the overriding
    plate. A thermostat holds continental area near continental_fraction
    (real growth vs. loss at trenches is roughly balanced but uncertain).
    Two gentle thermostats: arc growth (adds crust) follows the volume
    of continental crust, subduction erosion (removes continental
    edges) its area. Together they hold both near their targets, and so
    the average thickness, which decides how high continents stand.
    Each answers the present error (x error^4) and, slowly, the error that
    has persisted (integrated over THERMO_MYR, sim.thermo): with the
    present error alone, area settled ~12% above its target (45% of the
    surface against 40% after 1 Gyr), because the sources of new area
    (welds, rifted margins, new arcs) outrun subduction erosion at its
    nominal rate, and the continents' volume, held on target, was spread
    thinner over it (PW-046, PW-052).
    Returns (arc growth factor, subduction erosion factor)."""
    p = sim.params
    frac = max(sim.w_cont.mean(), 1e-3)
    vol = max(float((sim.w_thick * sim.w_cont).mean()), 1e-3)
    target = sim.target_fraction()
    err = np.log([target * p.continental_thickness / vol, frac / target])
    sim.thermo = np.clip(sim.thermo + sim.dt_now / THERMO_MYR * err, -THERMO_MAX, THERMO_MAX)
    thermostat = np.clip(np.exp(4 * (err[0] + sim.thermo[0])), 0.1, 5.0)
    shrink = np.clip(np.exp(4 * (err[1] + sim.thermo[1])), 0.2, 5.0)
    return thermostat, shrink


def spread(sim, src_rate, width, gap=0.0, also=None):
    """A rate at source cells, spread over a Gaussian belt `width` level-5
    cells wide on the same plate; with a gap (level-5 cells), little of it
    lands within ~gap of the source (1 - e^-(d/gap)^2). also: a second rate
    at the same source cells (> 0 where src_rate is), spread the same way
    and returned with the first (one search for both)."""
    g, n = sim.grid, sim.grid.n
    src = np.flatnonzero(src_rate > 0)
    if len(src) == 0:
        return np.zeros(n) if also is None else (np.zeros(n), np.zeros(n))
    w = width * sim.scale
    dist, s = kernels.bfs_within(src, sim.owner, g.nbr_off, g.nbr_idx, int(3 * w))
    hit = s >= 0
    bell = np.exp(-((dist[hit] / w) ** 2))
    near = 1 - np.exp(-((dist[hit] / (gap * sim.scale)) ** 2)) if gap > 0 else None
    outs = []
    for rate in (src_rate,) if also is None else (src_rate, also):
        out = np.zeros(n)
        out[hit] = rate[s[hit]] * bell
        if near is not None:
            out[hit] *= near
        outs.append(out)
    return outs[0] if also is None else tuple(outs)


def arc_growth(sim, bd, conv, thermostat):
    """km/Myr of new arc crust per cell, behind every trench: the volcanic
    front stands ~100-200 km behind the trench (the arc-trench gap), so the
    forearc right at the trench gets little (FOREARC_KM), and subduction
    erosion there isn't undone by the arc on the same cell.
    The volume thermostat steers only arcs built on continents (Andean
    arcs, which thicken what is there); island arcs on ocean floor grow at
    the nominal rate. (Steering both made a volume shortfall build new
    continent out of island arcs: more area instead of thicker crust, which
    the area thermostat then wore away again at the continents' edges, and
    the continents thinned over the run: PW-046, PW-052.)
    Returns (growth, nominal): nominal is the same arcs at their nominal
    rate (thermostat 1), the melt the subducting slabs make, which is what
    the arcs outgas (earth.global_temperature's CO2 source, PW-741)."""
    p = sim.params
    up = bd.overriding
    gain = np.where(sim.w_cont[up], thermostat, 1.0)
    arc_src, arc_nom = np.zeros(sim.grid.n), np.zeros(sim.grid.n)
    np.maximum.at(arc_src, up, p.arc_growth * sim.heat() * gain * bd.at_trenches(conv))
    np.maximum.at(arc_nom, up, p.arc_growth * sim.heat() * bd.at_trenches(conv))
    return spread(sim, arc_src, 1.6, FOREARC_KM / L5_KM, also=arc_nom)


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
    Deccan Traps; at most a LAVA_MAX_KM pile), and part of an arc's erupts as ash and ignimbrite
    sheets (tuff: the Altiplano-Puna, Taupo); both go on top of the strata."""
    dt, cont = sim.dt_now, col.cont
    col.t = col.t + growth * dt + plume * dt
    sim.book("arc", 0, growth * dt, cont)
    sim.book("plume", 0, plume * dt, cont)
    # (lava piles no thicker than LAVA_MAX_KM: the rest of a plume's or a
    # vent's melt stays in the crust as intrusions and underplating, PW-133)
    lava = np.minimum(plume * dt * cont, np.maximum(LAVA_MAX_KM - col.x[:, LAVA], 0.0))
    tuff = TUFF_SHARE * growth * dt * cont
    col.cover = col.cover + lava + tuff
    col.x[:, LAVA] += lava
    col.x[:, TUFF_X] += tuff
    n = sim.grid.n
    record.add_top(col.rec, col.lith, lava, np.full(n, FLOOD_BASALT, np.uint8), sim.t)
    record.add_top(col.rec, col.lith, tuff, np.full(n, TUFF, np.uint8), sim.t)


def inner_edges(sim, cont, bd=None):
    """Grid edges along which crust can be spread sideways, (ea, eb):
    inside one continent on one plate, and (with the boundaries bd) across
    a collision, between the two colliding continents. A collision belt is
    one belt on both plates (the Himalaya and Tibet straddle the suture):
    stacked crust and the flow of thick crust cross it. (Kept to one plate,
    the crust stacked at the front could only spread back into its own
    plate, and a front cell with few continental neighbours of its own
    plate, a promontory, piled up to MAX_KM, 30-40 km above its neighbours
    across the suture: single-cell spikes, and the MAX_KM cap deleted
    their excess, ~5% of the continents' crust per Gyr on L6 seed 2;
    PW-284, PW-046.)"""
    g = sim.grid
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    both = (sim.owner[ea] == sim.owner[eb]) & cont[ea] & cont[eb]
    ea, eb = ea[both], eb[both]
    if bd is not None and bd.collision.any():
        ca, cb = bd.a[bd.collision], bd.b[bd.collision]
        ok = cont[ca] & cont[cb]
        ea, eb = np.concatenate([ea, ca[ok]]), np.concatenate([eb, cb[ok]])
    return ea, eb


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
    p, n, dt = sim.params, sim.grid.n, sim.dt_now
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
    # the wedge is scraped off the top and thrust up in folds (Makran, Barbados)
    record.remove_top(col.rec, col.lith, scraped)
    record.add_top(col.rec, col.lith, gain, np.full(n, SHALE, np.uint8), sim.t)
    record.fold(col.rec, col.lith, gain > 0, np.zeros(n), col.cover, col.t, sim.t)


def subduction_erosion(sim, bd, conv, col, shrink):
    """Subduction erosion: the slab also grinds away the underside and
    front of the overriding continent and drags it down (the Andes'
    coast has retreated ~250 km since the Jurassic). Globally it removes
    about as much continental crust as arcs add. A continental edge cell
    worn below 15 km is gone: what's left counts as oceanic."""
    p, n, dt = sim.params, sim.grid.n, sim.dt_now
    if p.subduction_erosion <= 0:
        return
    up, cv = bd.overriding, bd.at_trenches(conv)
    worn = np.zeros(n)
    # (the rate is for a FOREARC_KM wide forearc: on a cell w km wide, x
    # FOREARC_KM / w, so the crust and area removed per km of trench is the
    # same at every level; per cell it halved at each finer level: PW-052)
    km = sim.edge_len * R_KM
    np.maximum.at(worn, up, p.subduction_erosion * cv * dt * shrink * FOREARC_KM / km)
    worn = np.minimum(worn * col.cont, col.t)
    t0 = col.t
    t = col.t = col.t - worn
    sim.book("subd.erosion", t0, t, col.cont)
    gone = col.cont & (worn > 0) & (t < 15.0)
    if gone.any():
        sim.book("subd.erosion", t, 0, gone)
        to_ocean(sim, col, gone)


def to_ocean(sim, col, gone):
    """Continental cells `gone` (their crust already booked away) become ocean floor at the trench. In place on col."""
    col.cont = col.cont.copy()
    col.cont[gone] = False
    col.rock[gone] = OCEAN
    col.t = col.t.copy()
    col.t[gone] = OCEAN_KM
    col.cover = col.cover.copy()
    col.cover[gone] = 0.0
    col.x[gone] = 0.0
    col.rec[gone] = record.blank()
    col.lith[gone] = 0
    floor_age(sim, gone, col.cont)


ANDES_BELT = 1.2  # level-5 cells: e-folding width of the belt contraction stacks behind the arc (andean_contraction)


def andean_contraction(sim, bd, conv, col, shrink):
    """The overriding plate contracts behind an ocean-continent trench (PW-1497 option A): the Andes are mostly
    shortened and thickened South American crust, not arc melt. The slab pins the trench, so the share
    `andean_shortening` of the overriding continent's own advance toward it (cm/yr, at most the convergence) is
    taken up by the plate's edge closing up (Schellart 2008: a stable or advancing trench goes with overriding-plate
    shortening; Medvedev et al. 2006: the central Andes shorten 1-1.75 cm/yr of the foreland's ~3 cm/yr westward
    motion). The area that closes is the plate's: it is pooled per plate (plates.short_pool, km^2) and, a whole cell
    at a time, the edge cell shortening fastest closes up: its whole column is stacked into a narrow belt behind it
    on its own continent (ANDES_BELT wide, past the forearc gap, like the arc's) and the cell becomes ocean floor at
    the trench, so continental volume is kept and area is lost as shortening loses it (as a collision's overlap
    does in plate_kernels.resolve). andean_steer: the area thermostat's factor steers the rate, as it does
    subduction erosion's. Returns km of crust added per cell (a squeezed belt, for flow_and_orogeny)."""
    p, g, n, dt = sim.params, sim.grid, sim.grid.n, sim.dt_now
    add = np.zeros(n)
    if p.andean_shortening <= 0 or not (bd.a_down.any() or bd.b_down.any()):
        return add
    from .motion import velocity
    from .plates import CMYR
    up = bd.overriding
    toward = np.concatenate([-bd.d[bd.a_down], bd.d[bd.b_down]])  # from the overriding cell toward the trench
    adv = (velocity(sim)[up] * toward).sum(1) * CMYR
    rate = p.andean_shortening * np.clip(adv, 0.0, bd.at_trenches(conv)) * col.cont[up]
    if p.andean_steer > 0:
        rate = rate * shrink
    r = np.zeros(n)
    np.maximum.at(r, up, rate)  # cm/yr per trench-edge cell
    if not r.any():
        return add
    km = sim.edge_len * R_KM
    cell_km2 = sim.cell_area * R_KM**2
    own, pl = sim.owner, sim.plates
    pl.short_pool += np.bincount(own, r * 10.0 * dt * km, P_MAX)  # km/Myr x Myr x km of trench per cell
    close = np.zeros(n, bool)
    for k in np.flatnonzero(pl.short_pool >= cell_km2):
        cand = np.flatnonzero((r > 0) & (own == k) & col.cont)
        m = min(int(pl.short_pool[k] // cell_km2), len(cand))
        if m > 0:
            close[cand[np.argsort(-r[cand], kind="stable")[:m]]] = True
            pl.short_pool[k] -= m * cell_km2
        pl.short_pool[k] = min(pl.short_pool[k], cell_km2 * max(len(cand) - m, 1))
    if not close.any():
        return add
    src = np.flatnonzero(close)
    label = np.where(col.cont, own, -1)
    w = ANDES_BELT * sim.scale
    dist, s = kernels.bfs_within(src, label, g.nbr_off, g.nbr_idx, int(3 * w))
    hit = (s >= 0) & ~close
    wt = np.exp(-((dist[hit] / w) ** 2)) * (1 - np.exp(-((dist[hit] / (FOREARC_KM / L5_KM * sim.scale)) ** 2)))
    tot = np.bincount(s[hit], wt, n)
    ok = close & (tot > 0)  # (a cell with no continent of its own behind it doesn't close)
    if not ok.any():
        return add
    keep = ok[s[hit]]
    cells, sw = np.flatnonzero(hit)[keep], s[hit][keep]
    np.add.at(add, cells, col.t[sw] * wt[keep] / tot[sw])
    sim.book("andean.closed", col.t, 0, ok)  # (the closed cells; their crust is the belt's "andean")
    col.t = col.t + add
    sim.book("andean", 0, add, col.cont)
    to_ocean(sim, col, ok)
    return add


def floor_age(sim, cells, cont):
    """Continental crust that has just become ocean floor (`cells`) takes
    the mean age of the ocean floor next to it (none: 0), not its rock's
    age: ocean depth, sea level and the age of passive margins
    (events.old_margins) read it as the floor's cooling age, and shreds of
    a 2 Gyr old continent showed as 2 Gyr old sea floor (PW-191)."""
    g = sim.grid
    w = np.flatnonzero(cells)
    if len(w) == 0:
        return
    nb = (~cont) & ~cells
    ok = nb[g.nbr_idx]
    s_age = np.add.reduceat(np.where(ok, sim.w_age[g.nbr_idx], 0.0), g.nbr_off[:-1])
    n_ok = np.add.reduceat(ok.astype(np.int64), g.nbr_off[:-1])
    age = sim.w_age.copy()
    age[w] = s_age[w] / np.maximum(n_ok[w], 1)
    sim.w_age = age


def arc_rock(sim, col, growth):
    """Arc rock: on continents wherever arcs build; at sea only once the
    crust has thickened into a real island arc. Returns where."""
    # (a rate: km/Myr x the run's step, so a finish-window step's shorter length doesn't raise the bar, PW-915)
    arcky = (growth * sim.dt > 0.1) & (col.rock != CRATON) & (col.cont | (col.t > OCEAN_KM + 5))
    col.rock[arcky] = ARC
    return arcky


SQUEEZED = 0.05  # km/Myr of collision stacking that makes a cell part of a squeezed belt (flow_and_orogeny)


def stretch(sim, col, rate, plume, newc, stack_add=None):
    """Thin stretched continental crust (rate per Myr from rift_stretching)
    down to 22 km, floor the opening rifts with what it lost
    (rifted_margin), and mark ocean-floor plume piles as hotspot rock.
    Crust a collision is stacking up this step (stack_add, km) is being
    shortened, not stretched: it isn't thinned or dated as rifting (a belt
    cell between a collision and an opening edge was both, every step, and
    its rift strain added up to beta ~6-9 on 80 km crust, whose thermal
    uplift, isostasy.subsidence, put it ~2 km above its belt: PW-172's
    one-frame 10.6 km peaks)."""
    dt, t = sim.dt_now, col.t
    thin = col.cont & (t > 22)
    if stack_add is not None:
        thin &= stack_add <= SQUEEZED * dt
    t0 = t.copy()
    t[thin] = np.maximum(22.0, t[thin] * np.exp(-rate[thin] * dt))
    record.rift(col.rec, thin & (rate > RIFT_THINNING), np.log(t0 / np.maximum(t, 1e-9)), sim.t)
    sim.book("stretch", t0, t, col.cont)
    rifted_margin(sim, t0 - t, col, newc)
    col.rock[~col.cont & (plume * sim.dt > 0.2)] = HOTSPOT  # (a rate, at the run's step: PW-915)


MARGIN_MIN_KM = 12.0  # thinnest rifted-margin crust laid in a rift (else: ocean floor)
POOL_MYR = 100.0  # Myr: e-folding time of a rift pool that no opening rift takes up


def flanks(sim, col, cont):
    """A rift that never opens (or opens too little to take its whole pool)
    keeps the crust stretched out of it in its own flanks: the pool decays
    over POOL_MYR back into the plate's continental cells that rifted within
    that time (the stretched ones, equally; none left: all its continent).
    Crust kept, so the pool isn't a sink (PW-287: the decayed share used to
    be deleted, ~5% of all stretched crust). Booked as "rift flanks"."""
    pl, own = sim.plates, sim.owner
    back = pl.rift_pool * (1 - np.exp(-sim.dt_now / POOL_MYR))
    pl.rift_pool -= back
    if not (back > 0).any():
        return
    rifted = cont & (sim.t - col.rec[:, record.T_RIFT] <= POOL_MYR)
    n_rift = np.bincount(own, rifted, P_MAX)
    n_cont = np.bincount(own, cont, P_MAX)
    to = np.where((n_rift[own] > 0) & rifted | (n_rift[own] == 0) & cont, 1.0, 0.0)
    n_to = np.where(n_rift > 0, n_rift, n_cont)
    add = to * (back / np.maximum(n_to, 1))[own]
    col.t = col.t + add
    sim.book("rift flanks", 0, add, cont)


def necking(sim, col, cont, k, cells, s):
    """Lay the new floor `cells` of plate k next to its continental crust
    (sources s) as stretched continental crust paid for by thinning the
    plate's own margin: the necking zone (PW-950). On Earth the crust
    thins from ~30 km to <= 10 km across a necking zone ~50-60 km wide
    before the ocean opens, with beta > 2 in it and < 2 landward (Mohn et
    al. 2012, Tectonics 31 TC1012, pp. 1-3), and the crust is conserved
    (ibid. p. 23; McKenzie 1978 p. 27). Here the gap the plates open is
    floored with crust as thick as the edge after thinning, taken from the
    plate's continental cells within neck_km of the edge (and the rift
    pool first): each thins by exp(-eps w), w = 1 - d / neck_km, eps solved
    so the crust taken equals the crust laid. Each ring is the next edge,
    so the margin thins seaward; once the next ring would be thinner than
    MARGIN_MIN_KM the rift has broken up and its floor stays ocean.
    Returns the cells laid, their sources and their thickness (km)."""
    g, p, pl = sim.grid, sim.params, sim.plates
    own = sim.owner
    cell_km = sim.edge_len * R_KM
    reach = max(int(np.ceil(p.neck_km / cell_km)), 1)
    label = np.where(cont, own, -1)
    dist, _ = kernels.bfs_within(np.unique(s), label, g.nbr_off, g.nbr_idx, reach)
    zone = np.flatnonzero((dist >= 0) & (dist * cell_km < p.neck_km))
    w = 1.0 - dist[zone] * cell_km / p.neck_km
    hz = col.t[zone]
    pool = max(float(pl.rift_pool[k]), 0.0)
    for _ in range(3):
        hs = col.t[s]
        need0 = float(hs.sum())
        if pool >= need0:
            eps = 0.0
        else:
            lo, hi = 0.0, 4.0
            for _ in range(40):
                eps = 0.5 * (lo + hi)
                gap = pool + float((hz * -np.expm1(-eps * w)).sum()) - need0 * np.exp(-eps)
                lo, hi = (eps, hi) if gap < 0 else (lo, eps)
            eps = hi
        km = hs * np.exp(-eps)
        ok = km >= MARGIN_MIN_KM
        if ok.all() or not ok.any():
            break
        cells, s = cells[ok], s[ok]
    if not ok.all():
        return cells[:0], s[:0], km[:0]
    laid = float(km.sum())
    take = laid - min(pool, laid)
    pl.rift_pool[k] = pool - min(pool, laid)
    if take > 0 and eps > 0:
        t0 = col.t[zone].copy()
        col.t[zone] = hz * np.exp(-eps * w)
        strain = np.zeros(g.n)
        strain[zone] = eps * w
        mask = np.zeros(g.n, bool)
        mask[zone] = True
        record.rift(col.rec, mask, strain, sim.t)
        sim.book("necking", t0, col.t[zone], 1.0)
    return cells, s, km


def rifted_margin(sim, lost, col, newc):
    """Stretching doesn't destroy crust, it spreads it thinner over a
    wider area: the opening rift is floored by thinned continental crust
    (rifted margins: 10-25 km thick, 100-300 km wide, under 1-4 km of sea)
    before true ocean floor appears. The crust a plate's continental edge
    loses to stretching is pooled and laid down as new margin cells in
    the gap next to it (newc: the new ocean floor of this step).
    The margin grows outward from the continent one ring of cells at a
    time, a whole ring at once (thinner, down to MARGIN_MIN_KM, when the
    pool runs short), so it is one continuous belt. (Laying the pool's
    cells wherever they fell left a mosaic of margin and ocean-floor
    cells, and bands of them as the rift opened step by step; the floor
    cells sank to -4 km beside -2 km margin, and the plates carried the
    mosaic past the world grid as cells flipping between continent and
    deep sea every few Myr: PW-108.)
    How thick a ring is laid depends only on the pool (PW-286: it used to
    be laid thicker when the continents' area was over its target, a second
    lever on the area thermostat's error acting through a local process;
    the area is the subduction-erosion thermostat's alone).
    In place on col (and sim.w_age)."""
    g, p, pl = sim.grid, sim.params, sim.plates
    own = sim.owner
    cont = col.cont
    pl.rift_pool += np.bincount(own, np.maximum(lost, 0) * cont, P_MAX)
    flanks(sim, col, cont)
    if p.rift_margin_km <= 0 or not newc.any():
        return
    src_of = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    cand = newc & ~cont
    if not cand.any():
        return
    cont = col.cont = cont.copy()
    laid = np.zeros(g.n, bool)
    for _ in range(int(round(2 * sim.scale))):
        # free new floor next to continental crust of its own plate: the next ring
        same = cont[g.nbr_idx] & (own[g.nbr_idx] == own[src_of])
        touch = np.logical_or.reduceat(same, g.nbr_off[:-1]) & cand & ~cont
        if not touch.any():
            break
        # a source for each: a continental neighbour on the same plate (the first)
        first = np.where(same, np.arange(len(g.nbr_idx)), len(g.nbr_idx))
        s_all = g.nbr_idx[np.minimum(np.minimum.reduceat(first, g.nbr_off[:-1]), len(g.nbr_idx) - 1)]
        grew = False
        for k in np.unique(own[touch]):
            cells = np.flatnonzero(touch & (own == k))
            s = s_all[cells]
            if p.neck_km > 0:
                cells, s, km = necking(sim, col, cont, k, cells, s)
                if not len(cells):
                    continue
            else:
                km = min(p.rift_margin_km, pl.rift_pool[k] / len(cells))
                if km < MARGIN_MIN_KM:
                    continue
            col.t[cells] = km
            cont[cells] = True
            col.rock[cells] = col.rock[s]
            sim.w_age[cells] = sim.w_age[s]
            col.cover[cells] = 0.0
            col.x[cells] = 0.0
            # (the source's history, no strata yet; rifted now)
            col.rec[cells] = col.rec[s]
            col.rec[cells, record.KM] = 0.0
            col.rec[cells, record.T] = record.NEVER
            col.rec[cells, record.T_RIFT] = sim.t
            col.lith[cells] = 0
            if p.neck_km <= 0:
                pl.rift_pool[k] -= len(cells) * km  # (necking takes its share of the pool itself)
            laid[cells] = True
            grew = True
        if not grew:
            break
    if laid.any():
        sim.book("margin", 0, col.t, laid)


def flow_and_orogeny(sim, col, edges, stack_add):
    """Crustal flow: very thick crust is hot and weak at depth and spreads
    sideways (Tibet is doing this now), within a continent on one plate
    and across a collision (inner_edges). Faster the thicker it is, which
    is why crust >~70 km is so rare.
    A diffusion: per-cell rates scale with 1/spacing^2, so finer grids
    take more (equally stable) substeps.
    Then collision belts are folded, faulted and metamorphosed wherever the
    crust is being stacked up, whatever it was before (an old arc,
    sediment); very thick crust is metamorphosed too. Returns where crust
    is being squeezed."""
    p, dt, cont, rock = sim.params, sim.dt_now, col.cont, col.rock
    t0 = col.t
    mult = np.ones(len(edges[0]))
    if p.collapse > 0:
        # post-orogenic collapse: a belt no longer being squeezed (none for collapse_delay Myr: its trench died
        # or became a collision, its collision stopped) has lost the convergence that held its thick crust up,
        # and spreads (Dewey 1988; the Variscan and Basin and Range plateaus): its flow is (1 + collapse) x faster
        dead = sim.t - col.rec[:, record.T_FOLD] > p.collapse_delay
        mult = np.where(dead[edges[0]] & dead[edges[1]], 1.0 + p.collapse, 1.0)
    # (a hotter planet's crust is softer: mountains and plateaus can't stand as high)
    t = crust_flow(col.t, edges[0], edges[1], p.crust_flow * sim.heat() ** 2 * dt / 3,
                   int(round(3 * sim.scale**2 * sim.heat() ** 2)), mult)
    t = col.t = np.minimum(t, max_km(cont, col.cover, col.x))  # (PW-1446: the cap is on the column's height)
    sim.book("flow+cap", t0, t, cont)
    squeezed = cont & (stack_add > SQUEEZED * dt)
    rock[squeezed & (rock != CRATON)] = OROGEN
    record.fold(col.rec, col.lith, squeezed, stack_add, col.cover, t, sim.t)
    rock[(t > 50) & cont & (rock != CRATON) & (rock != ARC)] = OROGEN
    return squeezed


def coherence(sim, col, trench=None):
    """Crust type is coherent at the grid's scale. An ocean-floor cell
    nearly ringed by continental crust of its own plate (a one-cell inlet
    or hole, <= 2 of its neighbours oceanic) is, at 50-100 km, part of the
    thinned margin or basin around it: it counts as (thin) continental
    crust from now on. A thin continental cell (< BECOMES_CONT_KM) nearly
    ringed by ocean floor (>= all but 2 of its neighbours oceanic) is a
    shred of margin: ocean floor. A shred keeps its thickness; into an
    inlet the continental crust around it flows (lower-crustal flow,
    volume kept): its neighbours each give it an equal share until it is
    as thick as their new mean, so a one-cell pit becomes a shallow dip.
    Why: a mosaic of one-cell inlets and shreds, left by margins, arcs and
    sampling, was carried past the world grid by the moving plates and
    showed as cells flipping between continent and deep sea every few Myr
    (PW-108). No welds at a trench (`trench`: cells on either side of a
    subducting edge): a notch there is the slab grinding the forearc away
    (subduction_erosion), and welding it shut again every step made the
    erosion thin the continent instead of shrinking it (PW-046, PW-052).
    Two more conditions on a weld (PW-970), or welds become a net source of
    continental area that no process answers, spread thin from the
    continents' volume (L5 seed 2, 380-400 Myr: 773 welds against 570
    shreds, +200 cells, more than the rifted margins laid; 26% of the
    continental crust thinner than 20 km, the area thermostat at x4.4):
    - the inlet must be one on the plate itself (its cell on the plate's
      own grid nearly ringed by the plate's continental crust, the same
      count as on the world grid). A gap that only the world grid's
      nearest-cell sampling of a moved plate shows (56% of the welds were
      continental on the world grid the step before) is not welded: welding
      it wrote continental crust into the plate's ocean cell at the coast,
      while the continental cell the world grid showed there before stayed
      on the plate, so every jitter of a sampled coastline grew the plate's
      continent by a cell, a ratchet that runs with coastline length and
      the cells per km (PW-749);
    - the crust around it must be continental crust by the model's own
      measure (its mean at least BECOMES_CONT_KM, as for a cell born
      continental; the shred rule's bound): a hole among thin margin cells
      is a gap in the ocean-continent transition, not in a continent.
    In place on col; returns (cells made continental, cells made oceanic)."""
    g = sim.grid
    own = sim.owner
    src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    same = own[g.nbr_idx] == own[src]
    n_same = np.add.reduceat(same.astype(np.int64), g.nbr_off[:-1])
    ok = same & col.cont[g.nbr_idx]
    n_cont = np.add.reduceat(ok.astype(np.int64), g.nbr_off[:-1])
    ring = n_same >= 5  # (not on a plate boundary)
    weld = ring & ~col.cont & (n_cont >= n_same - 2) & (col.rock != HOTSPOT)
    if trench is not None:
        weld &= ~trench
    s_t = np.add.reduceat(np.where(ok, col.t[g.nbr_idx], 0.0), g.nbr_off[:-1])
    weld &= s_t >= BECOMES_CONT_KM * np.maximum(n_cont, 1)
    weld[weld] = _inlet_on_plate(sim, np.flatnonzero(weld))
    shred = ring & col.cont & (n_cont <= 2) & (col.t < BECOMES_CONT_KM)
    if weld.any() or shred.any():
        v0 = col.t * col.cont
        col.cont = col.cont.copy()
        # (its basement: a continental neighbour's)
        first = np.minimum.reduceat(np.where(ok, np.arange(len(ok)), len(ok)), g.nbr_off[:-1])
        w = np.flatnonzero(weld)
        col.rock[w] = col.rock[g.nbr_idx[first[w]]]
        # crust flows in from the continental neighbours
        t = col.t
        x = np.where(weld, np.maximum(s_t / np.maximum(n_cont, 1) - t, 0) / (n_cont + 1), 0.0)
        e = np.flatnonzero(ok & weld[src])
        loss = np.zeros(g.n)
        np.add.at(loss, g.nbr_idx[e], x[src[e]])
        col.t = t - loss + np.where(weld, x * n_cont, 0.0)
        col.cont[weld] = True
        col.cont[shred] = False
        col.rock[shred] = OCEAN
        floor_age(sim, shred, col.cont)
        sim.book("coherence", v0, col.t * col.cont, 1.0)
    return weld, shred


def _inlet_on_plate(sim, cells):
    """For world cells `cells` (each an inlet on the world grid), whether
    its owner's own grid shows the inlet too: the plate's cell there
    (plates.idx) has all but 2 of its owned neighbours on that grid
    continental. Returns a mask over cells."""
    if len(cells) == 0:
        return np.zeros(0, bool)
    g, pl = sim.grid, sim.plates
    k = sim.owner[cells]
    r = pl.idx[k, cells]
    st, deg = g.nbr_off[r], g.nbr_off[r + 1] - g.nbr_off[r]
    n_own = np.zeros(len(cells), np.int64)
    n_cont = np.zeros(len(cells), np.int64)
    for j in range(int(deg.max())):
        nb = g.nbr_idx[np.minimum(st + j, len(g.nbr_idx) - 1)]
        owned = (j < deg) & pl.owned[k, nb]
        n_own += owned
        n_cont += owned & pl.cont[k, nb]
    return n_cont >= n_own - 2


def touches_own_continent(sim, cont):
    """Cells with a continental neighbour on their own plate (world grid)."""
    g, own = sim.grid, sim.owner
    src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    same = cont[g.nbr_idx] & (own[g.nbr_idx] == own[src])
    return np.logical_or.reduceat(same, g.nbr_off[:-1])


def birth_and_cratons(sim, col, arcky, squeezed):
    """Ocean crust thickened enough by arcs or sediment becomes continental;
    a sediment pile only where it touches its plate's continent (a margin
    wedge; PW-1292). Hotspot piles (Hawaii, Iceland) stay oceanic however
    big, unless it's sediment from a nearby continent that's piling up on
    them.
    Rock age (continents): crust that's just formed or been remelted /
    metamorphosed starts again at 0 (and so does its exhumation, the
    erosion since: record.EXHUMED). An arc worn GRANITE_KM down since
    it went quiet shows its plutons (granite: the Sierra Nevada's
    batholith). Old, cool, untouched crust stiffens into craton (Canada,
    Siberia, Africa's shields).
    Updates sim.w_age; returns the cells born continental."""
    p, t, cont, rock = sim.params, col.t, col.cont, col.rock
    # (or a pile whose cover has reached the burial depth: what's below it
    # was sediment too, now basement; PW-172)
    sedimented = (col.cover > 0.5 * (t - OCEAN_KM)) | (col.cover > 0.8 * sim.params.metamorphic_depth)
    born = ~cont & (t >= BECOMES_CONT_KM) & ((rock != HOTSPOT) | sedimented)
    # (a pile of sediment on the ocean floor is sediment on oceanic crust, however thick: it becomes continental
    # only as a margin wedge against its own plate's continent; elsewhere it joins one when a trench scrapes it on
    # (accrete) or a collision welds it on; PW-1292)
    if (born & sedimented).any():
        born &= ~sedimented | touches_own_continent(sim, cont)
    rock[born] = np.where(sedimented[born], SEDIMENT, ARC)
    sim.book("born", 0, t, born)
    age = sim.w_age.copy()
    age[born | (cont & arcky)] = 0.0
    age[squeezed & (rock != CRATON)] = 0.0
    sim.w_age = age
    col.rec[age == 0, record.EXHUMED] = 0.0
    rock[cont & (rock == ARC) & (col.rec[:, record.EXHUMED] >= GRANITE_KM) & (col.cover < surface.COVER_SHOWS)] = GRANITE
    rock[cont & (age > p.craton_age) & (t < 45) & (rock != CRATON) & (rock != HOTSPOT)] = CRATON
    return born
