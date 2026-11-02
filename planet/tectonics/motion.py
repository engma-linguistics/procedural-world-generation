"""Plate boundaries and plate motion.

Plate motion is basically very slow Stokes flow, so each step the force
balance gives every plate a target velocity: slab pull (dominant), ridge
push, collision resistance, basal traction from the mantle flowing under
the plate (mantle.py: toward cold slab graveyards, away from warm mantle),
and a small, slowly wandering drag term that supplies meandering. Every force acts on world cells; it becomes a torque
on the cell's plate, and a drag matrix (resistance to rotating, larger
under continental keels) turns the plate's total torque into a target
angular velocity. The plate's angular velocity then relaxes toward that
target over velocity_timescale (15 Myr; plate inertia, in effect) and is
capped so no cell moves faster than max_speed (18 cm/yr). forces() runs
after the step's move, so the velocities it sets are used by the next
step's move.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numba import njit

from . import mantle
from .plates import CMYR, P_MAX


@dataclass
class Boundaries:
    """The grid edges (a, b) whose two cells are on different plates.
    Per edge: d = unit tangent from a toward b, conv = closing speed in
    cm/yr (>0 converging), and what happens there. a_down / b_down: which
    side of a subducting edge sinks."""
    a: np.ndarray
    b: np.ndarray
    d: np.ndarray
    conv: np.ndarray
    collision: np.ndarray
    subduct: np.ndarray
    a_down: np.ndarray
    b_down: np.ndarray
    opening: np.ndarray

    def at_trenches(self, per_edge: np.ndarray) -> np.ndarray:
        """per_edge values of the subducting edges, in the order of
        `sinking` / `overriding`."""
        return np.concatenate([per_edge[self.a_down], per_edge[self.b_down]])

    @property
    def sinking(self) -> np.ndarray:
        """Cell on the down-going plate at each trench edge."""
        return np.concatenate([self.a[self.a_down], self.b[self.b_down]])

    @property
    def overriding(self) -> np.ndarray:
        """Cell on the overriding plate at each trench edge."""
        return np.concatenate([self.b[self.a_down], self.a[self.b_down]])

    @property
    def spreading(self) -> np.ndarray:
        """Cells on both sides of every opening edge."""
        return np.concatenate([self.a[self.opening], self.b[self.opening]])


def velocity(sim) -> np.ndarray:
    """Tangent velocity of every cell (rad/Myr, world frame)."""
    return np.cross(sim.plates.omega[sim.owner], sim.grid.centers)


def boundaries(sim) -> Boundaries:
    g = sim.grid
    P = g.centers
    a, b = g.edges[:, 0], g.edges[:, 1]
    m = sim.owner[a] != sim.owner[b]
    a, b = a[m], b[m]
    d = P[b] - P[a]
    d -= (d * P[a]).sum(1, keepdims=True) * P[a]
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    v = velocity(sim)
    conv = ((v[a] - v[b]) * d).sum(1) * CMYR  # cm/yr, >0 = closing
    ca, cb = sim.w_cont[a], sim.w_cont[b]
    closing = conv > 0.5
    opening = conv < -0.5
    collision = closing & ca & cb
    subduct = closing & ~collision
    # which side goes down: oceanic under continental; older ocean under younger
    a_down = subduct & (~ca & (cb | (sim.w_age[a] >= sim.w_age[b])))
    b_down = subduct & ~a_down
    return Boundaries(a=a, b=b, d=d, conv=conv, collision=collision, subduct=subduct,
                      a_down=a_down, b_down=b_down, opening=opening)


@dataclass
class CellForces:
    """Per-cell terms of the force balance, kept for the stress test in
    events.stress_cut: the torque each cell's boundary forces put on its
    plate, and its drag matrix (resistance to the plate rotating)."""
    torque: np.ndarray  # (n, 3)
    drag: np.ndarray  # (n, 3, 3)


@njit(cache=True)
def _add_rows(out, idx, vals):
    """np.add.at(out, idx, vals) for 2-D rows, in the same (sequential) order: bit-identical, without add.at's overhead."""
    for i in range(idx.shape[0]):
        r = idx[i]
        for j in range(out.shape[1]):
            out[r, j] += vals[i, j]


def _add_at(out, idx, vals):
    """np.add.at for row scatter-adds (out (m, k), vals (len(idx), k) or broadcastable), else numpy's."""
    idx = np.asarray(idx)
    if out.ndim == 2 and out.dtype == np.float64 and idx.ndim == 1 and idx.dtype.kind in "iu":
        v = np.ascontiguousarray(np.broadcast_to(vals, (idx.shape[0], out.shape[1])), dtype=np.float64)
        _add_rows(out, idx.astype(np.int64, copy=False), v)
    else:
        np.add.at(out, idx, vals)


def forces(sim, bd: Boundaries, rng) -> CellForces:
    """Move every plate's angular velocity toward the one the forces on it
    call for (relaxing over velocity_timescale, capped at max_speed; in
    place on plates.omega and plates.wander)."""
    g, p, dt = sim.grid, sim.params, sim.dt_now
    pl = sim.plates
    P = g.centers
    mantle.stir(sim, rng)
    a, b, d, conv = bd.a, bd.b, bd.d, bd.conv
    F = np.zeros((g.n, 3))
    L = sim.edge_len
    # slab pull: the sinking side is pulled toward (and under) the other
    # plate by its slab's weight, less the mantle's resistance to the slab
    # sinking through it (Stokes drag, ~ the sinking speed: slab_drag x the
    # convergence), so a slab sinks no faster than its terminal speed,
    # slab_pull x age factor / slab_drag (PW-288)
    resist = p.slab_drag * np.clip(conv, 0, 15)
    slab_a = (p.slab_pull * np.clip(sim.w_age[a] / 80, 0.3, 1.5) - resist) * L
    slab_b = (p.slab_pull * np.clip(sim.w_age[b] / 80, 0.3, 1.5) - resist) * L
    _add_at(F, a[bd.a_down], d[bd.a_down] * slab_a[bd.a_down, None])
    _add_at(F, b[bd.b_down], -d[bd.b_down] * slab_b[bd.b_down, None])
    # ridge push: away from opening boundaries
    o = bd.opening
    _add_at(F, a[o], -d[o] * p.ridge_push * L)
    _add_at(F, b[o], d[o] * p.ridge_push * L)
    # collision: resist further closing, harder the faster they close
    c = bd.collision
    k = (p.collision_drag * np.clip(conv[c], 0, 15) * L)[:, None]
    _add_at(F, a[c], -d[c] * k)
    _add_at(F, b[c], d[c] * k)
    # basal traction: the mantle flowing under the plate from warm to cold
    F += mantle.traction(sim)

    torque = np.zeros((P_MAX, 3))
    cell_torque = np.cross(P, F)
    _add_at(torque, sim.owner, cell_torque)
    w = sim.cell_area * (1 + p.continental_keel * sim.w_cont)
    outer = (np.eye(3)[None] - P[:, :, None] * P[:, None, :]) * w[:, None, None]
    drag = np.zeros((P_MAX, 3, 3))
    _add_at(drag.reshape(P_MAX, 9), sim.owner, outer.reshape(len(outer), 9))

    decay = np.exp(-dt / p.mantle_timescale)
    relax = 1 - np.exp(-dt / p.velocity_timescale)
    for k in np.flatnonzero(pl.alive):
        area = np.trace(drag[k]) / 2
        if area <= 0:
            continue
        # wandering basal drag: an Ornstein-Uhlenbeck process, scaled by plate area
        pl.wander[k] = pl.wander[k] * decay + np.sqrt(1 - decay**2) * rng.normal(size=3)
        tau = torque[k] + p.mantle_noise * pl.wander[k] * area * 0.5
        Dk = drag[k] + 0.1 * area * np.eye(3)  # regularise spin about the plate's own centre
        target = p.mobility * sim.heat() ** 0.5 * np.linalg.solve(Dk, tau)
        pl.omega[k] += (target - pl.omega[k]) * relax
        vmax = np.linalg.norm(np.cross(pl.omega[k], P[sim.owner == k]), axis=1).max(initial=0) * CMYR
        if vmax > p.max_speed:
            pl.omega[k] *= p.max_speed / vmax
    return CellForces(cell_torque, outer)
