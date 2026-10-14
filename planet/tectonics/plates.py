"""Plates as rigid bodies: units, slots, rotations.

Every plate stores its crust on its own private copy of the grid (its
"reference frame") plus a rotation matrix Q saying where that copy currently
sits on the globe. Moving a plate = updating Q; the crust data never gets
resampled, so a plate's interior doesn't blur as it travels.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..geo import R_KM

CMYR = R_KM / 10.0  # (rad/Myr on unit sphere) -> cm/yr
P_MAX = 48  # plate slots; slots are reused, labels are the permanent ids


def rotation(axis_angle: np.ndarray) -> np.ndarray:
    """Rodrigues: rotation matrix for rotating by |v| radians about v."""
    th = np.linalg.norm(axis_angle)
    if th < 1e-15:
        return np.eye(3)
    k = axis_angle / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


# the per-cell crust columns each plate carries in its own frame (isostasy.EXTRA: extra's columns)
CRUST = ("age", "thick", "cont", "rock", "cover", "extra")


@dataclass
class Plates:
    """All per-plate state, by slot (P_MAX of them; `alive` says which are
    in use). Per-cell arrays are on the plate's own copy of the grid.

    Rigid motion and identity:
      alive (P,)        slot in use
      label (P,)        the permanent id people see (slots are reused)
      next_label        the label the next new plate gets
      formed (P,)       Myr: when the plate got its current shape (rift/split)
      Q (P, 3, 3)       rotation: plate frame -> world
      omega (P, 3)      angular velocity, rad/Myr
      wander (P, 3)     the slowly wandering basal mantle drag (see motion.forces)
      rift_pool (P,)    km x cells of stretched-out crust waiting to line a rift
    Crust, (P, n), in the plate's frame:
      owned             the plate has crust in this cell of its grid
      age               Myr (ocean floor: since it formed; continent: rock age)
      thick             km of crust
      cont              continental (else oceanic)
      rock              surface.ROCKS id of the basement
      cover             km of sediment on top of the basement
      extra (P, n, 6)   isostasy.EXTRA columns
      idx               cell of the plate's grid under each world cell
                        (refreshed every step; also read for unowned cells)
    Pairs of plates, (P, P), upper triangle (i < j) for the timers:
      contact           Myr the pair has been in continental collision
      closing           cm/yr they still converge there (smoothed)
      last_logged       Myr: last "collision" event logged for the pair
      rifted_at         Myr: when the pair split from one plate
    """
    alive: np.ndarray
    label: np.ndarray
    next_label: int
    formed: np.ndarray
    Q: np.ndarray
    omega: np.ndarray
    wander: np.ndarray
    rift_pool: np.ndarray
    owned: np.ndarray
    age: np.ndarray
    thick: np.ndarray
    cont: np.ndarray
    rock: np.ndarray
    cover: np.ndarray
    extra: np.ndarray
    idx: np.ndarray
    contact: np.ndarray
    closing: np.ndarray
    last_logged: np.ndarray
    rifted_at: np.ndarray

    @classmethod
    def empty(cls, n: int, n_extra: int, next_label: int) -> "Plates":
        P = P_MAX
        return cls(
            alive=np.zeros(P, bool), label=np.arange(P), next_label=next_label, formed=np.zeros(P),
            Q=np.tile(np.eye(3), (P, 1, 1)), omega=np.zeros((P, 3)), wander=np.zeros((P, 3)),
            rift_pool=np.zeros(P),
            owned=np.zeros((P, n), bool), age=np.zeros((P, n)), thick=np.zeros((P, n)),
            cont=np.zeros((P, n), bool), rock=np.zeros((P, n), np.uint8), cover=np.zeros((P, n)),
            extra=np.zeros((P, n, n_extra)), idx=np.tile(np.arange(n), (P, 1)),
            contact=np.zeros((P, P)), closing=np.zeros((P, P)),
            last_logged=np.full((P, P), -1e9), rifted_at=np.full((P, P), -1e9))

    def crust(self) -> tuple[np.ndarray, ...]:
        """The per-cell crust arrays (CRUST order), for copying crust between plates."""
        return tuple(getattr(self, name) for name in CRUST)

    def copy_crust(self, dst: int, dst_cells, src: int, src_cells):
        """Copy crust columns src_cells of plate src into dst_cells of plate dst."""
        for arr in self.crust():
            arr[dst, dst_cells] = arr[src, src_cells]

    def move(self, grid, dt: float):
        """Rotate every live plate by its angular velocity, and find which of
        its cells lies under each world cell."""
        for k in np.flatnonzero(self.alive):
            self.Q[k] = rotation(self.omega[k] * dt) @ self.Q[k]
            self.idx[k] = grid.locate(grid.centers @ self.Q[k], self.idx[k])

    def new_slot(self) -> int:
        """Bring the first free slot to life under a fresh label, with no
        crust and no history with any other plate."""
        new = int(np.flatnonzero(~self.alive)[0])
        self.label[new] = self.next_label
        self.next_label += 1
        for arr, fill in ((self.contact, 0), (self.closing, 0), (self.last_logged, -1e9), (self.rifted_at, -1e9)):
            arr[new, :] = fill
            arr[:, new] = fill
        self.alive[new] = True
        self.owned[new] = False
        return new
