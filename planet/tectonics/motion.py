"""Plate boundaries and plate motion.

Plates have no momentum (it's basically very slow Stokes flow), so each
step the velocity is *solved* from the forces: slab pull (dominant), ridge
push, collision resistance, and a slowly wandering mantle-drag term that
supplies meandering. Every force acts on world cells; it becomes a torque
on the cell's plate, and a drag matrix (resistance to rotating, larger
under continental keels) turns the plate's total torque into its angular
velocity.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

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


def forces(sim, bd: Boundaries, rng) -> CellForces:
    """Solve every plate's angular velocity from the forces on it (in place
    on plates.omega and plates.wander)."""
    g, p, dt = sim.grid, sim.params, sim.dt
    pl = sim.plates
    P = g.centers
    a, b, d, conv = bd.a, bd.b, bd.d, bd.conv
    F = np.zeros((g.n, 3))
    L = sim.edge_len
    # slab pull: the sinking side is pulled toward (and under) the other plate
    slab_a = p.slab_pull * np.clip(sim.w_age[a] / 80, 0.3, 1.5) * L
    slab_b = p.slab_pull * np.clip(sim.w_age[b] / 80, 0.3, 1.5) * L
    np.add.at(F, a[bd.a_down], d[bd.a_down] * slab_a[bd.a_down, None])
    np.add.at(F, b[bd.b_down], -d[bd.b_down] * slab_b[bd.b_down, None])
    # ridge push: away from opening boundaries
    o = bd.opening
    np.add.at(F, a[o], -d[o] * p.ridge_push * L)
    np.add.at(F, b[o], d[o] * p.ridge_push * L)
    # collision: resist further closing, harder the faster they close
    c = bd.collision
    k = (p.collision_drag * np.clip(conv[c], 0, 15) * L)[:, None]
    np.add.at(F, a[c], -d[c] * k)
    np.add.at(F, b[c], d[c] * k)

    torque = np.zeros((P_MAX, 3))
    cell_torque = np.cross(P, F)
    np.add.at(torque, sim.owner, cell_torque)
    w = sim.cell_area * (1 + p.continental_keel * sim.w_cont)
    outer = (np.eye(3)[None] - P[:, :, None] * P[:, None, :]) * w[:, None, None]
    drag = np.zeros((P_MAX, 3, 3))
    np.add.at(drag, sim.owner, outer)

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
