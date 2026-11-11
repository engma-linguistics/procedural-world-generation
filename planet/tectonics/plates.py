"""Plates as rigid bodies: units, slots, rotations.

Every plate stores its crust on its own private copy of the grid (its
"reference frame") plus a rotation matrix Q saying where that copy currently
sits on the globe. Moving a plate = updating Q; the crust data never gets
resampled, so a plate's interior doesn't blur as it travels.
"""

from __future__ import annotations

import copy
import mmap
from dataclasses import dataclass, fields

import numpy as np

from ..geo import R_KM
from . import record

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


# the per-cell crust columns each plate carries in its own frame (isostasy.EXTRA: extra's
# columns; record.RECORD: rec's, the strata and history)
CRUST = ("age", "thick", "cont", "rock", "cover", "extra", "rec", "lith")
# the (P, n, ...) arrays that live on mapped memory (_mapped): only the rows of slots in use cost memory (PW-1389)
MAPPED = ("owned", *CRUST)


def _mapped(shape, dtype) -> np.ndarray:
    """A zeroed array on its own anonymous memory map: a page costs memory
    only once it is written, and Plates.release can hand a dead slot's
    pages back (a plain np.zeros may come from reused heap memory, written
    in full)."""
    dtype = np.dtype(dtype)
    count = int(np.prod(shape))
    # (private: madvise(DONTNEED) frees a private page and it reads as zero again; a shared one keeps its data)
    if hasattr(mmap, "MAP_ANONYMOUS"):
        buf = mmap.mmap(-1, max(count * dtype.itemsize, 1), flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    else:  # (Windows: no flags; an anonymous map is zeroed, backed by the page file; release() does nothing, PW-1760)
        buf = mmap.mmap(-1, max(count * dtype.itemsize, 1))
    return np.frombuffer(buf, dtype, count).reshape(shape)


def _map_of(arr: np.ndarray) -> mmap.mmap | None:
    b = arr.base
    while b is not None and not isinstance(b, mmap.mmap):
        b = getattr(b, "base", None) if not isinstance(b, memoryview) else b.obj
    return b


@dataclass
class Plates:
    """All per-plate state, by slot (P_MAX of them; `alive` says which are
    in use). Per-cell arrays are on the plate's own copy of the grid.

    Rigid motion and identity:
      alive (P,)        slot in use
      label (P,)        the permanent id people see (slots are reused)
      next_label        the label the next new plate gets
      formed (P,)       Myr: when the plate split off another (events.split; its settle_time clock)
      Q (P, 3, 3)       rotation: plate frame -> world
      omega (P, 3)      angular velocity, rad/Myr
      wander (P, 3)     the slowly wandering basal mantle drag (see motion.forces)
      rift_pool (P,)    km x cells of stretched-out crust waiting to line a rift
      short_pool (P,)   km^2 of the plate's edge shortened at ocean-continent trenches, not yet closed up
                        as whole cells (crust.andean_contraction)
    Crust, (P, n), in the plate's frame:
      owned             the plate has crust in this cell of its grid
      age               Myr (ocean floor: since it formed; continent: rock age)
      thick             km of crust
      cont              continental (else oceanic)
      rock              surface.ROCKS id of the basement
      cover             km of sediment on top of the basement
      extra (P, n, 8)   isostasy.EXTRA columns
      rec (P, n, R)     record.RECORD columns (float32): the strata's thickness
                        and dates, and the crust's history (rift, folding, ...)
      lith (P, n, K)    record: each stratum's rock (surface.ROCKS id), top first
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
    short_pool: np.ndarray
    owned: np.ndarray
    age: np.ndarray
    thick: np.ndarray
    cont: np.ndarray
    rock: np.ndarray
    cover: np.ndarray
    extra: np.ndarray
    rec: np.ndarray
    lith: np.ndarray
    idx: np.ndarray
    contact: np.ndarray
    closing: np.ndarray
    last_logged: np.ndarray
    rifted_at: np.ndarray

    @classmethod
    def empty(cls, n: int, n_extra: int, next_label: int) -> "Plates":
        """No crust yet; slots 0..next_label-1 ready for setup.initial_state.
        (Later slots are only ever filled by events.split, which copies the
        parent's whole frame in, so their rows stay unwritten until then:
        on mapped memory they cost nothing, PW-1389.)"""
        P = P_MAX
        rec = _mapped((P, n, len(record.RECORD)), np.float32)
        rec[:next_label] = record.blank()
        return cls(
            alive=np.zeros(P, bool), label=np.arange(P), next_label=next_label, formed=np.zeros(P),
            Q=np.tile(np.eye(3), (P, 1, 1)), omega=np.zeros((P, 3)), wander=np.zeros((P, 3)),
            rift_pool=np.zeros(P), short_pool=np.zeros(P),
            owned=_mapped((P, n), bool), age=_mapped((P, n), float), thick=_mapped((P, n), float),
            cont=_mapped((P, n), bool), rock=_mapped((P, n), np.uint8), cover=_mapped((P, n), float),
            extra=_mapped((P, n, n_extra), float), rec=rec, lith=_mapped((P, n, record.K), np.uint8),
            idx=np.tile(np.arange(n), (P, 1)),
            contact=np.zeros((P, P)), closing=np.zeros((P, P)),
            last_logged=np.full((P, P), -1e9), rifted_at=np.full((P, P), -1e9))

    def mapped_copy(self) -> "Plates":
        """A copy with the MAPPED arrays on mapped memory and only the live
        slots' rows written (a dead slot's crust is never read: a slot comes
        back to life only by events.split, which overwrites its whole frame);
        for a state put back into a simulation (Simulation.load_state)."""
        out = {}
        for f in fields(self):
            v = getattr(self, f.name)
            if f.name in MAPPED:
                a = _mapped(v.shape, v.dtype)
                a[self.alive] = v[self.alive]
                out[f.name] = a
            else:
                out[f.name] = copy.deepcopy(v)
        return Plates(**out)

    def release(self, k: int):
        """Hand slot k's rows of the MAPPED arrays back to the system (they
        read as zeros after, or stale on the edge pages). Only for a dead
        slot nothing reads any more: see release_dead."""
        page = mmap.PAGESIZE
        for name in MAPPED:
            arr = getattr(self, name)
            mm = _map_of(arr)
            if mm is None or not hasattr(mmap, "MADV_DONTNEED"):  # (plain arrays: a state() copy, in tests)
                continue
            row = arr[0].nbytes
            a = -(-(k * row) // page) * page
            b = ((k + 1) * row) // page * page
            if b > a:
                mm.madvise(mmap.MADV_DONTNEED, a, b - a)

    def release_dead(self):
        """release() every dead slot (cheap for one already handed back).
        Called at the end of a step: within the step a plate's crust is
        still read after it dies (volcanism.re_home reads the swell under
        its volcanoes), but after it nothing reads a dead slot's crust until
        events.split brings the slot back and overwrites its whole frame
        (PW-1389)."""
        for k in np.flatnonzero(~self.alive):
            self.release(int(k))

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
        self.short_pool[new] = 0.0
        return new
