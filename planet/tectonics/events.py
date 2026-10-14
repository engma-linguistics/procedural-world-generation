"""Plate events: collisions, sutures, slivers, rifts.

Long collisions weld plates together; plates split when a big continent
overheats the mantle beneath it, when the forces on a plate pull its halves
apart, or when old ocean floor at a passive margin breaks off and starts to
sink (new subduction); slivers get absorbed. Every event is logged as an
Event for the run's timeline.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..geo import latlon as _latlon
from ..noise import Perlin3D, fbm
from ..surface import CRATON, OROGEN
from .motion import Boundaries, CellForces
from .plates import CMYR, P_MAX


@dataclass
class Event:
    t: float
    kind: str
    plates: list[int]
    lat: float
    lon: float
    text: str

    def as_dict(self):
        return {"t": self.t, "kind": self.kind, "plates": self.plates,
                "lat": round(self.lat, 1), "lon": round(self.lon, 1), "text": self.text}


def latlon(p) -> tuple[float, float]:
    """(lat, lon) in degrees of a point (any length) on the sphere."""
    lat, lon = _latlon(p / np.linalg.norm(p))
    return float(lat), float(lon)


def log(sim, kind, slots, where, template):
    """template uses {0}, {1}... for the plates' permanent ids."""
    ids = [int(sim.plates.label[s]) for s in slots]
    lat, lon = latlon(where)
    sim.events.append(Event(sim.t, kind, ids, lat, lon, template.format(*ids)))


# ---------------------------------------------------------------------------
# joining plates
# ---------------------------------------------------------------------------
def merge(sim, keep, gone):
    """Move plate `gone`'s crust into plate `keep`'s reference frame."""
    g, pl = sim.grid, sim.plates
    # Pull, don't push: for every empty cell of `keep`'s grid, ask whether
    # `gone` has crust at that spot. (Pushing gone's cells into keep's grid
    # skips some cells, because the two grids are rotated relative to
    # each other, and leaves a lacy pattern of holes.)
    t = np.flatnonzero(~pl.owned[keep])
    world = g.centers[t] @ pl.Q[keep].T
    r = g.locate(world @ pl.Q[gone])
    has = pl.owned[gone, r]
    t, r = t[has], r[has]
    pl.owned[keep, t] = True
    pl.copy_crust(keep, t, gone, r)
    # World cells `gone` shows whose spot on keep's grid the pull missed
    # (the rotated grids don't map one to one): push those too, or they
    # would show keep's never-written (zero-thickness) crust.
    w = np.flatnonzero(sim.owner == gone)
    rk, rg = pl.idx[keep, w], pl.idx[gone, w]
    miss = ~pl.owned[keep, rk]
    rk, rg = rk[miss], rg[miss]
    pl.owned[keep, rk] = True
    pl.copy_crust(keep, rk, gone, rg)
    ak, ag = (sim.owner == keep).sum(), (sim.owner == gone).sum()
    pl.omega[keep] = (pl.omega[keep] * ak + pl.omega[gone] * ag) / max(ak + ag, 1)
    pl.owned[gone] = False
    pl.alive[gone] = False
    sim.owner[sim.owner == gone] = keep
    for arr in (pl.contact, pl.closing):
        arr[gone, :] = 0
        arr[:, gone] = 0


def sutures(sim, bd: Boundaries):
    """Continental collisions: log new ones; weld plates whose collision
    has stalled (or gone on very long)."""
    p, g, pl = sim.params, sim.grid, sim.plates
    c = bd.collision
    pairs = np.stack([sim.owner[bd.a[c]], sim.owner[bd.b[c]]], 1)
    pairs.sort(axis=1)
    cnt = np.zeros((P_MAX, P_MAX), int)
    np.add.at(cnt, (pairs[:, 0], pairs[:, 1]), 1)
    thr = max(3, int(4 * sim.scale))
    active = cnt >= thr
    # contact builds while touching and drains (not resets) when not, so a
    # boundary hovering around the threshold doesn't flicker
    started = active & (pl.contact == 0) & (sim.t - pl.last_logged > 40)
    for i, j in zip(*np.nonzero(started)):
        sel = (pairs[:, 0] == i) & (pairs[:, 1] == j)
        where = g.centers[bd.a[c][sel]].mean(0)
        log(sim, "collision", [i, j], where, "continents on plates {0} and {1} collide")
        pl.last_logged[i, j] = sim.t
    pl.contact = np.where(active, pl.contact + sim.dt, np.maximum(pl.contact - sim.dt, 0))
    # How fast each colliding pair is still closing (cm/yr, smoothed over
    # ~10 Myr). Collision goes on while they converge (India has pushed
    # into Asia for 50 Myr and counting); they only weld into one plate
    # once the collision has ground to a halt.
    csum = np.zeros((P_MAX, P_MAX))
    np.add.at(csum, (pairs[:, 0], pairs[:, 1]), bd.conv[c])
    rate = np.where(cnt > 0, csum / np.maximum(cnt, 1), 0.0)
    w = 1 - np.exp(-sim.dt / 10.0)
    pl.closing = np.where(active, pl.closing + w * (rate - pl.closing), pl.closing)
    stalled = (pl.contact >= p.suture_after) & (pl.closing < p.suture_closing)
    for i, j in zip(*np.nonzero(stalled | (pl.contact >= p.suture_max))):
        if not (pl.alive[i] and pl.alive[j]) or sim.t - pl.rifted_at[i, j] < 80:
            continue
        sel = (pairs[:, 0] == i) & (pairs[:, 1] == j)
        where = g.centers[bd.a[c][sel]].mean(0) if sel.any() else g.centers[sim.owner == i].mean(0)
        ai, aj = (sim.owner == i).sum(), (sim.owner == j).sum()
        keep, gone = (i, j) if ai >= aj else (j, i)
        merge(sim, keep, gone)
        pl.closing[i, j] = 0
        log(sim, "suture", [keep, gone], where,
            "plates {0} and {1} weld together along their collision; {1} is absorbed")


def absorb_slivers(sim):
    """Plates too small to matter join the neighbour that surrounds them most."""
    g, pl = sim.grid, sim.plates
    sizes = np.bincount(sim.owner, minlength=P_MAX)
    min_cells = max(4, int(0.0015 * g.n))
    for k in np.flatnonzero(pl.alive & (sizes < min_cells)):
        if pl.alive.sum() <= 2:
            break
        cells = np.flatnonzero(sim.owner == k)
        if len(cells) == 0:
            pl.alive[k] = False
            pl.owned[k] = False
            log(sim, "consumed", [k], g.centers[0], "plate {0} has been entirely subducted")
            continue
        nb = np.concatenate([g.neighbors[i] for i in cells])
        others = sim.owner[nb][sim.owner[nb] != k]
        if len(others) == 0:
            continue
        keep = int(np.bincount(others).argmax())
        where = g.centers[cells].mean(0)
        merge(sim, keep, k)
        log(sim, "absorbed", [keep, k], where, "remnant plate {1} is absorbed into plate {0}")


# ---------------------------------------------------------------------------
# splitting plates
# ---------------------------------------------------------------------------
def strength(sim) -> np.ndarray:
    """How hard the lithosphere of each world cell is to break, relative to
    ordinary crust (1). Old, cold cratons are strong; continents break
    instead along their weak zones: the belts where they were welded
    together (young collision belts, still warm and faulted; Pangaea split
    along the ~300-400 Myr old Appalachian/Caledonian sutures) and crust
    already thinned by earlier stretching."""
    cont, rock, age = sim.w_cont, sim.w_rock, sim.w_age
    s = np.ones(sim.grid.n)
    s[cont & (rock == CRATON)] = 1.6
    belt = cont & (rock == OROGEN)
    s[belt] = 0.85 - 0.5 * np.exp(-age[belt] / 400.0)
    return np.where(cont, s * np.clip(sim.w_thick / 35.0, 0.7, 1.0), s)


def piece_ok(sim, cont_a, cont_b) -> bool:
    """Rifts break continents into a few large pieces, not slivers: each
    side must carry either (almost) no continent or at least
    rift_min_piece of the surface of it."""
    lo, hi = 0.1 * sim.params.rift_min_piece * sim.grid.n, sim.params.rift_min_piece * sim.grid.n
    return all(not (lo < x < hi) for x in (cont_a, cont_b))


def cut_lines(sim, cells, c, rng, tries):
    """`tries` random straight cuts across the cells (positions on the unit
    sphere) around centre c: normals t, offsets off (a cut is (x - c) @ t =
    off), which side each cell is on, and the cells along each cut line."""
    P = sim.grid.centers[cells]
    t = rng.normal(size=(tries, 3))
    t -= (t @ c)[:, None] * c
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    proj = (P - c) @ t.T  # (cells, tries)
    spread_ = np.sqrt((proj**2).mean(0))
    off = rng.uniform(-0.6, 0.6, tries) * spread_
    d = (proj - off).T  # (tries, cells)
    return t, off, d > 0, np.abs(d) < sim.grid.spacing


def stress_cut(sim, k, cf: CellForces, rng, tries=12):
    """Plates are rigid only up to a point. Try a few straight cuts across
    plate k and, for each, solve how the two halves would move on their
    own (same force balance as motion.forces). The cut that wins is the
    one across which the halves most want to pull apart (e.g. slabs
    pulling on opposite sides) for the strength of the rock along it
    (strength()), among cuts that leave no continental sliver (piece_ok).
    Returns (point on the cut, cut normal, effective opening speed in
    cm/yr: opening / mean strength along the cut)."""
    p = sim.params
    cells = np.flatnonzero(sim.owner == k)
    P = sim.grid.centers[cells]
    c = P.mean(0)
    c /= np.linalg.norm(c)
    t, off, side_b, line = cut_lines(sim, cells, c, rng, tries)
    side = side_b.astype(float)
    tq, D = cf.torque[cells], cf.drag[cells]
    motion = []
    for s_ in (side, 1 - side):
        Dh = np.einsum("tc,cij->tij", s_, D)
        area = np.trace(Dh, axis1=1, axis2=2) / 2
        tau = s_ @ tq + p.mantle_noise * 0.5 * area[:, None] * sim.plates.wander[k]
        Dh = Dh + 0.1 * area[:, None, None] * np.eye(3)
        motion.append(p.mobility * sim.heat() ** 0.5 * np.linalg.solve(Dh, tau[:, :, None])[:, :, 0])
    at = c + off[:, None] * t
    at /= np.linalg.norm(at, axis=1, keepdims=True)
    opening = np.einsum("tj,tj->t", np.cross(motion[0] - motion[1], at), t) * CMYR
    s = strength(sim)[cells]
    weak = (line @ s) / np.maximum(line.sum(1), 1)
    eff = opening / np.maximum(weak, 0.1)
    frac = side.mean(1)
    cont = sim.w_cont[cells].astype(float)
    ca = side @ cont
    ok = (frac > 0.15) & (frac < 0.85) & np.array([piece_ok(sim, x, cont.sum() - x) for x in ca])
    eff[~ok] = 0
    i = int(eff.argmax())
    return (at[i], t[i], float(eff[i])) if eff[i] > 0 else (c, None, 0.0)


def weak_cut(sim, k, rng, tries=12):
    """A cut across plate k's continent along its weakest line (heat
    rifting): (point on the cut, normal), or (c, None) if every cut would
    leave a sliver."""
    cells = np.flatnonzero((sim.owner == k) & sim.w_cont)
    c = sim.grid.centers[cells].mean(0)
    c /= np.linalg.norm(c)
    t, off, side, line = cut_lines(sim, cells, c, rng, tries)
    weak = (line @ strength(sim)[cells]) / np.maximum(line.sum(1), 1)
    na = side.sum(1)
    ok = np.array([piece_ok(sim, x, len(cells) - x) for x in na]) & (line.sum(1) > 0)
    if not ok.any():
        return c, None
    i = int(np.where(ok, -weak, -np.inf).argmax())
    at = c + off[i] * t[i]
    return at / np.linalg.norm(at), t[i]


def old_margins(sim):
    """Per plate: mean age of the ocean floor along its passive margins
    (coastlines where continent and ocean ride on the same plate, like
    today's Atlantic coasts), and how many margin edges it has."""
    a, b = sim.grid.edges[:, 0], sim.grid.edges[:, 1]
    m = (sim.owner[a] == sim.owner[b]) & (sim.w_cont[a] != sim.w_cont[b])
    ocean = np.where(sim.w_cont[a], b, a)[m]
    k = sim.owner[a][m]
    cnt = np.bincount(k, minlength=P_MAX)
    age = np.bincount(k, sim.w_age[ocean], P_MAX) / np.maximum(cnt, 1)
    return age, cnt


def maybe_rift(sim, cf: CellForces, rng):
    """Three ways a plate splits, each a hazard rate (per Myr, in units of
    1/rift_timescale); at most one split per step.
      heat:   a big continent insulates the mantle under it and rifts
              (Pangaea -> Atlantic).
      stress: a big plate whose halves are pulled different ways breaks
              along the line where they'd separate fastest.
      margin: old ocean floor at a passive margin is cold and dense enough
              to break off and start sinking under the continent: new
              subduction (the closing half of the Wilson cycle)."""
    p, g, pl = sim.params, sim.grid, sim.plates
    if pl.alive.sum() >= min(p.max_plates, P_MAX):
        return
    P = g.centers
    cont_cells = np.bincount(sim.owner, weights=sim.w_cont, minlength=P_MAX)
    all_cells = np.bincount(sim.owner, minlength=P_MAX)
    margin_age, margin_len = old_margins(sim)
    threshold = p.rift_min_continent * g.n
    big = p.stress_min_plate * g.n
    for k in np.flatnonzero(pl.alive):
        heat = cont_cells[k] / threshold if cont_cells[k] >= threshold else 0.0
        stress, cut, t_s = 0.0, None, None
        # (a freshly formed plate gets time to settle first, or splits cascade)
        if all_cells[k] >= big and sim.t - pl.formed[k] >= p.settle_time:
            c_s, t_s, opening = stress_cut(sim, k, cf, rng)
            if opening > p.rift_stress:
                stress = (opening / p.rift_stress - 1) * all_cells[k] / big
            # Plates much bigger than the Pacific (~20% of Earth) are rare:
            # they span too many different mantle flow regimes to stay whole.
            stress += 2 * max(0.0, all_cells[k] / (p.big_plate * g.n) - 1)
            if stress > 0 and t_s is not None:
                cut = (c_s, t_s)
        margin = 0.0
        ocean_cells = all_cells[k] - cont_cells[k]
        if (margin_len[k] >= 4 * sim.scale and ocean_cells >= 0.5 * big
                and cont_cells[k] >= 0.5 * big):
            margin = max(0.0, margin_age[k] / p.margin_age - 1) * 3
        rate = heat + stress + margin
        if rate == 0 or rng.random() > 1 - np.exp(-sim.dt / p.rift_timescale * rate):
            continue
        refs = np.flatnonzero(pl.owned[k])
        world = P[refs] @ pl.Q[k].T
        u = rng.random() * rate
        if u < margin:
            # the ocean side of the largest stretch of ocean on this plate
            lab, _ = g.components((sim.owner == k) & ~sim.w_cont)
            biggest = np.bincount(lab[lab >= 0]).argmax()
            at = g.locate(world)
            side = ~pl.cont[k, refs] & (lab[at] == biggest)
            new = split(sim, k, refs, world, side, toward=True)
            if new is not None:
                # continental cells of plate k with any neighbour in that stretch of ocean
                touches = np.logical_or.reduceat(lab[g.nbr_idx] == biggest, g.nbr_off[:-1])
                edge = (sim.owner == k) & sim.w_cont & touches
                c = P[edge].mean(0) if edge.any() else world[side].mean(0)
                log(sim, "subduction", [k, new], c, "old ocean floor on plate {0} breaks off "
                    "its continental margin and starts to sink; it becomes plate {1}")
                return
            continue
        if u < margin + stress:
            if cut is None:  # a huge plate with no clear stress direction
                c, t = weak_cut(sim, k, rng) if cont_cells[k] > 0 else (None, None)
                if t is None:
                    c = P[sim.owner == k].mean(0)
                    c /= np.linalg.norm(c)
                    t = rng.normal(size=3)
                    t -= (t @ c) * c
                    t /= np.linalg.norm(t)
            else:
                c, t = cut
            why = "is pulled apart by the forces on it"
        else:
            c, t = weak_cut(sim, k, rng)
            if t is None:
                continue
            why = "rifts apart"
        side = rift_side(sim, k, c, t, rng, world)
        if side is None or not 0.2 < side.mean() < 0.8:
            continue
        new = split(sim, k, refs, world, side, toward=False)
        what = "continent on plate" if cont_cells[k] >= threshold else "plate"
        log(sim, "rift", [k, new], c, what + " {0} " + why + "; the split-off part becomes plate {1}")
        return


def rift_side(sim, k, c, t, rng, world, tries=4):
    """Which of plate k's reference cells (at positions `world`) go to the
    new plate, or None if every try leaves a continental sliver. The cut
    is a great circle through c with normal t, bent out of shape by warped
    multi-scale noise so it wanders like a real rift (East Africa, the
    Atlantic's zig-zag margins). Stray fragments it cuts off are handed
    back to whichever side surrounds them. Of a few such wanderings, the
    one through the weakest rock (strength()) wins: rifts follow old
    sutures where they can."""
    g = sim.grid
    on = sim.owner == k
    mine = np.flatnonzero(on)
    s = strength(sim)
    best, best_w, best_cut = None, np.inf, None
    for _ in range(tries):
        seeds = rng.integers(2**31, size=4)

        def cut(x, seeds=seeds):
            warp = np.stack([fbm(Perlin3D(int(sd)), x, octaves=3, freq=2.0) for sd in seeds[:3]], 1)
            y = x + 0.12 * warp
            return (y - c) @ t + 0.07 * fbm(Perlin3D(int(seeds[3])), y, octaves=4, freq=4.0)
        v = np.zeros(g.n)
        v[mine] = cut(g.centers[mine])
        wside = on & (v > 0)
        for m in (wside, on & ~wside):
            lab, nl = g.components(m)
            if nl > 1:
                sizes = np.bincount(lab[lab >= 0])
                stray = (lab >= 0) & (lab != sizes.argmax())
                wside = np.where(stray, ~wside & on, wside)
        ca = int((wside & sim.w_cont).sum())
        if not piece_ok(sim, ca, int((on & sim.w_cont).sum()) - ca):
            continue
        # cells along the cut: on the plate, with a neighbour across it
        across = np.logical_or.reduceat(
            (wside[g.nbr_idx] != np.repeat(wside, np.diff(g.nbr_off))) & on[g.nbr_idx], g.nbr_off[:-1]) & on
        w = s[across].mean() if across.any() else np.inf
        if w < best_w:
            best, best_w, best_cut = wside, w, cut
    if best is None:
        return None
    cell = g.locate(world)
    here = sim.owner[cell] == k
    return np.where(here, best[cell], best_cut(world) > 0)


def split(sim, k, refs, world, side, toward):
    """Move plate k's reference cells refs[side] to a new plate. The two
    parts get a nudge apart (a rift) or together (new subduction).
    Returns the new plate's slot, or None if either part would be tiny."""
    pl = sim.plates
    if side.sum() < 4 or (~side).sum() < 4:
        return None
    new = pl.new_slot()
    pl.formed[new] = pl.formed[k] = sim.t
    pl.Q[new] = pl.Q[k]
    pl.idx[new] = pl.idx[k]
    r = refs[side]
    pl.owned[new, r] = True
    pl.owned[k, r] = False
    pl.copy_crust(new, slice(None), k, slice(None))
    axis = np.cross(world[~side].mean(0), world[side].mean(0))
    axis /= np.linalg.norm(axis)
    if toward:
        axis = -axis
    push = 2.5 / CMYR
    pl.omega[new] = pl.omega[k] + axis * push
    pl.omega[k] = pl.omega[k] - axis * push
    # the push lasts a while: seed the wandering term
    pl.wander[new] = pl.wander[k] + axis * 4.0
    pl.wander[k] = pl.wander[k] - axis * 4.0
    a_, b_ = min(k, new), max(k, new)
    pl.rifted_at[a_, b_] = sim.t
    pl.last_logged[a_, b_] = sim.t
    pl.contact[a_, b_] = 0
    moved = np.isin(sim.w_ref, r) & (sim.owner == k)
    sim.owner[moved] = new
    return new
