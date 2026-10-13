"""Time-stepped plate tectonics.

Representation
--------------
Every plate stores its crust on its own private copy of the grid (its
"reference frame") plus a rotation matrix Q saying where that copy currently
sits on the globe. Moving a plate = updating Q; the crust data never gets
resampled, so a plate's interior doesn't blur as it travels.

Each step:
 1. Rotate each plate by its angular velocity * dt.
 2. Pull: every world cell asks every plate "do you have crust here?"
    (nearest cell of the plate's reference grid, via kernels.locate).
 3. Resolve:  nobody   -> gap -> brand-new ocean floor (a ridge)
              one plate -> that plate owns the cell
              several  -> overlap. Continental crust beats oceanic, young
                          ocean beats old ocean. The loser's crust there is
                          deleted: that's subduction. Continent vs continent
                          is a collision.
 4. Physics on the resulting world map: ocean floor sinks as it ages,
    subduction builds arcs (Andes, Japan), collisions build big ranges
    (Himalaya), and a placeholder decay wears continents back down.
 5. Forces -> velocities. Plates have no momentum (it's basically very slow
    Stokes flow), so each step the velocity is *solved* from the forces:
    slab pull (dominant), ridge push, collision resistance, and a slowly
    wandering mantle-drag term that supplies meandering.
 6. Events: long collisions weld plates together; big continental plates
    eventually rift apart; plates consumed down to a sliver get absorbed.

Determinism: all randomness for step s comes from default_rng([seed, s]),
so any step can be reproduced exactly by re-running from t=0.

Units: time in Myr, angular velocity in rad/Myr on the unit sphere,
speeds reported in cm/yr (1 cm/yr = 10 km/Myr), elevation in metres.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numba import njit

from . import kernels
from .grid import Grid
from .noise import Perlin3D, fbm, ridged

R_KM = 6371.0
CMYR = R_KM / 10.0  # (rad/Myr on unit sphere) -> cm/yr
P_MAX = 48


@dataclass
class Params:
    n_plates: int = 12
    start: str = "supercontinent"  # or "scattered"
    continental_fraction: float = 0.32
    # forces (arbitrary units; mobility converts torque to rad/Myr)
    slab_pull: float = 1.0
    ridge_push: float = 0.15
    collision_drag: float = 0.6
    mantle_noise: float = 0.35
    mantle_timescale: float = 60.0  # Myr: how fast the wandering drag term changes
    velocity_timescale: float = 8.0  # Myr: smoothing on velocity changes
    continental_keel: float = 1.5  # extra drag per continental cell
    mobility: float = 0.008
    max_speed: float = 18.0  # cm/yr
    # mountain building (m per Myr per cm/yr of convergence)
    arc_uplift: float = 9.0
    collision_uplift: float = 22.0
    erosion_timescale: float = 70.0  # Myr: placeholder until real erosion runs in-loop
    # events
    suture_after: float = 30.0  # Myr of sustained continental collision -> weld plates
    rift_timescale: float = 130.0  # Myr: mean time before a big continental plate rifts
    rift_min_continent: float = 0.07  # fraction of surface
    big_plate: float = 0.16  # plates larger than this (any crust) may also split
    max_plates: int = 30


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


# ---------------------------------------------------------------------------
# compiled kernels
# ---------------------------------------------------------------------------
@njit(cache=True)
def _resolve(alive, idx, owned, elev, age, cont, base, prev_owner, nbr_off, nbr_idx,
             ridge_depth, Q, centers):
    """Decide which plate owns each world cell; delete subducted crust,
    fill aliasing holes, create new ocean floor in gaps.
    Returns (owner, new_crust flag, collision count matrix)."""
    P, n = idx.shape
    owner = np.full(n, -1, np.int64)
    newc = np.zeros(n, np.bool_)
    coll = np.zeros((P, P), np.int64)
    cand = np.empty(P, np.int64)
    # Pass 0: patch small holes inside a plate (nearest-neighbour
    # sampling of a rotated grid occasionally lands on a ref cell nobody
    # wrote). Without this, older crust underneath shows through as speckle.
    for k in range(P):
        if not alive[k]:
            continue
        for i in range(n):
            r = idx[k, i]
            if owned[k, r]:
                continue
            cnt, tot = 0, 0
            for e in range(nbr_off[r], nbr_off[r + 1]):
                tot += 1
                if owned[k, nbr_idx[e]]:
                    cnt += 1
            if cnt < tot - 2:
                continue
            se, sa, sb, sc = 0.0, 0.0, 0.0, 0
            for e in range(nbr_off[r], nbr_off[r + 1]):
                j = nbr_idx[e]
                if owned[k, j]:
                    se += elev[k, j]
                    sa += age[k, j]
                    sb += base[k, j]
                    sc += 1 if cont[k, j] else 0
            owned[k, r] = True
            elev[k, r] = se / cnt
            age[k, r] = sa / cnt
            base[k, r] = sb / cnt
            cont[k, r] = 2 * sc > cnt
    for i in range(n):
        m = 0
        for k in range(P):
            if alive[k] and owned[k, idx[k, i]]:
                cand[m] = k
                m += 1
        if m == 0:
            continue
        w = cand[0]
        for c in range(1, m):
            k = cand[c]
            rk, rw = idx[k, i], idx[w, i]
            if cont[k, rk] != cont[w, rw]:
                if cont[k, rk]:
                    w = k
            elif cont[k, rk]:
                if k == prev_owner[i] or (w != prev_owner[i] and elev[k, rk] > elev[w, rw]):
                    w = k
            elif age[k, rk] < age[w, rw]:
                w = k
        owner[i] = w
        rw = idx[w, i]
        for c in range(m):
            k = cand[c]
            if k == w:
                continue
            rk = idx[k, i]
            if cont[k, rk] and cont[w, rw]:
                coll[w, k] += 1
                coll[k, w] += 1
            owned[k, rk] = False
    # gaps: first try "hole in a plate" (aliasing), else new ocean floor
    for i in range(n):
        if owner[i] >= 0:
            continue
        best_k, best_c = -1, 0
        for k in range(P):
            if not alive[k]:
                continue
            r = idx[k, i]
            cnt = 0
            for e in range(nbr_off[r], nbr_off[r + 1]):
                if owned[k, nbr_idx[e]]:
                    cnt += 1
            if cnt > best_c:
                best_c, best_k = cnt, k
        if best_k >= 0 and best_c >= 4:
            k = best_k
            r = idx[k, i]
            se, sa, sb, sc, cnt = 0.0, 0.0, 0.0, 0, 0
            for e in range(nbr_off[r], nbr_off[r + 1]):
                j = nbr_idx[e]
                if owned[k, j]:
                    se += elev[k, j]
                    sa += age[k, j]
                    sb += base[k, j]
                    sc += 1 if cont[k, j] else 0
                    cnt += 1
            owned[k, r] = True
            elev[k, r] = se / cnt
            age[k, r] = sa / cnt
            base[k, r] = sb / cnt
            cont[k, r] = 2 * sc > cnt
            owner[i] = k
    counts = np.zeros(P, np.int64)
    for i in range(n):
        if owner[i] >= 0:
            continue
        # new ocean floor joins whichever plate holds most of its neighbours
        for k in range(P):
            counts[k] = 0
        for e in range(nbr_off[i], nbr_off[i + 1]):
            o = owner[nbr_idx[e]]
            if o >= 0:
                counts[o] += 1
        k = np.argmax(counts)
        deg = nbr_off[i + 1] - nbr_off[i]
        if counts[k] >= deg - 1 and counts[k] == counts.sum():
            # Surrounded by one plate (at most one other gap next to it): a real
            # ridge always borders another plate, so this is a sampling hole.
            # Fill it from the neighbours instead of making new sea floor.
            r = idx[k, i]
            se, sa, sb, sc, cnt = 0.0, 0.0, 0.0, 0, 0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if owner[j] == k:
                    rj = idx[k, j]
                    se += elev[k, rj]
                    sa += age[k, rj]
                    sb += base[k, rj]
                    sc += 1 if cont[k, rj] else 0
                    cnt += 1
            owned[k, r] = True
            elev[k, r] = se / cnt
            age[k, r] = sa / cnt
            base[k, r] = sb / cnt
            cont[k, r] = 2 * sc > cnt
            owner[i] = k
            continue
        if counts[k] == 0:
            k = prev_owner[i] if prev_owner[i] >= 0 and alive[prev_owner[i]] else np.argmax(alive)
        r = idx[k, i]
        owned[k, r] = True
        elev[k, r] = ridge_depth
        age[k, r] = 0.0
        base[k, r] = 0.0
        cont[k, r] = False
        owner[i] = k
        newc[i] = True
        # The plate's grid is rotated relative to the world grid, so several of
        # its cells can fall inside world cell i. Write all of them, or the
        # skipped ones become holes ("lace") that show up later as speckle.
        for e in range(nbr_off[r], nbr_off[r + 1]):
            r2 = nbr_idx[e]
            if owned[k, r2]:
                continue
            q = np.empty(3)
            for a in range(3):
                q[a] = Q[k, a, 0] * centers[r2, 0] + Q[k, a, 1] * centers[r2, 1] + Q[k, a, 2] * centers[r2, 2]
            if kernels.walk_nearest(q, i, centers, nbr_off, nbr_idx) == i:
                owned[k, r2] = True
                elev[k, r2] = ridge_depth
                age[k, r2] = 0.0
                base[k, r2] = 0.0
                cont[k, r2] = False
    return owner, newc, coll


@njit(cache=True)
def _cleanup_ghosts(alive, owned, Q, centers, owner, raster, nbr_off, nbr_idx):
    """Delete plate crust that sits deep under another plate (a leftover of
    nearest-neighbour sampling: a subducted cell nobody happened to 'pull')."""
    P, n = owned.shape
    h, w = raster.shape
    q = np.empty(3)
    removed = 0
    for k in range(P):
        if not alive[k]:
            continue
        for r in range(n):
            if not owned[k, r]:
                continue
            for a in range(3):
                q[a] = Q[k, a, 0] * centers[r, 0] + Q[k, a, 1] * centers[r, 1] + Q[k, a, 2] * centers[r, 2]
            lat = np.arcsin(min(1.0, max(-1.0, q[2])))
            lon = np.arctan2(q[1], q[0])
            y = min(h - 1, int((np.pi / 2 - lat) / np.pi * h))
            x = min(w - 1, int((lon + np.pi) / (2 * np.pi) * w))
            c = kernels.walk_nearest(q, raster[y, x], centers, nbr_off, nbr_idx)
            if owner[c] == k:
                continue
            deep = True
            for e in range(nbr_off[c], nbr_off[c + 1]):
                if owner[nbr_idx[e]] == k:
                    deep = False
                    break
            if deep:
                owned[k, r] = False
                removed += 1
    return removed


@njit(cache=True)
def _components(mask, nbr_off, nbr_idx):
    n = mask.shape[0]
    lab = np.full(n, -1, np.int64)
    q = np.empty(n, np.int64)
    k = 0
    for s in range(n):
        if not mask[s] or lab[s] >= 0:
            continue
        lab[s] = k
        head, tail = 0, 1
        q[0] = s
        while head < tail:
            i = q[head]
            head += 1
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if mask[j] and lab[j] < 0:
                    lab[j] = k
                    q[tail] = j
                    tail += 1
        k += 1
    return lab, k


def components(grid: Grid, mask: np.ndarray):
    return _components(mask, grid.nbr_off, grid.nbr_idx)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def rotation(axis_angle: np.ndarray) -> np.ndarray:
    """Rodrigues: rotation matrix for rotating by |v| radians about v."""
    th = np.linalg.norm(axis_angle)
    if th < 1e-15:
        return np.eye(3)
    k = axis_angle / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


def ocean_depth(age):
    """Half-space cooling: sea floor sinks ~ sqrt(age). (Real fit: 2600 + 345*sqrt(t) m.)"""
    return -np.minimum(2600 + 345 * np.sqrt(np.maximum(age, 0)), 6400)


def latlon(p):
    p = p / np.linalg.norm(p)
    return float(np.degrees(np.arcsin(np.clip(p[2], -1, 1)))), float(np.degrees(np.arctan2(p[1], p[0])))


@dataclass
class Snapshot:
    """World-frame view of the simulation at one instant."""
    t: float
    elevation: np.ndarray  # m, includes trenches
    plate: np.ndarray
    continental: np.ndarray
    age: np.ndarray  # Myr
    boundary: np.ndarray  # +1 converging, -1 diverging, 0 otherwise
    omega: dict[int, list[float]]  # plate id -> angular velocity (rad/Myr)


@dataclass
class Simulation:
    grid: Grid
    seed: int
    params: Params = field(default_factory=Params)
    dt: float = 2.0

    def __post_init__(self):
        g, p = self.grid, self.params
        n = g.n
        self.step_no = 0
        self.t = 0.0
        self.events: list[Event] = []
        self.alive = np.zeros(P_MAX, bool)
        self.Q = np.tile(np.eye(3), (P_MAX, 1, 1))
        self.omega = np.zeros((P_MAX, 3))
        self.mantle = np.zeros((P_MAX, 3))
        self.owned = np.zeros((P_MAX, n), bool)
        self.elev = np.zeros((P_MAX, n))
        self.age = np.zeros((P_MAX, n))
        self.base = np.zeros((P_MAX, n))
        self.cont = np.zeros((P_MAX, n), bool)
        self.idx = np.tile(np.arange(n), (P_MAX, 1))
        self.contact = np.zeros((P_MAX, P_MAX))
        self.last_logged = np.full((P_MAX, P_MAX), -1e9)
        self.rifted_at = np.full((P_MAX, P_MAX), -1e9)
        self.scale = 2.0 ** (g.level - 5)  # widths below are tuned in level-5 cells
        self.cell_area = 4 * np.pi / n
        self.edge_len = g.spacing
        # slots are reused; labels are permanent ids shown to people
        self.label = np.arange(P_MAX)
        self.next_label = p.n_plates
        self._initial_state()
        self._world_view()
        # tidy up slivers left by the initial set-up before the clock starts
        self._absorb_slivers()
        self.events.clear()
        self._world_view()

    # ------------------------------------------------------------- set-up
    def _initial_state(self):
        g, p = self.grid, self.params
        rng = np.random.default_rng(self.seed)
        n = g.n
        seeds = rng.choice(n, p.n_plates, replace=False).astype(np.int64)
        rates = rng.uniform(0.3, 1.0, p.n_plates) ** 2
        plate = kernels.grow_regions(int(rng.integers(2**31)), seeds, rates, g.nbr_off, g.nbr_idx, n)
        nz = Perlin3D(int(rng.integers(2**31)))
        x = g.centers
        if p.start == "supercontinent":
            c = rng.normal(size=3)
            c /= np.linalg.norm(c)
            field_ = x @ c + 0.35 * fbm(nz, x, octaves=5, freq=1.6)
        else:
            bias = rng.uniform(-1, 1, p.n_plates)
            field_ = fbm(nz, x, octaves=5, freq=1.3) + 0.25 * bias[plate]
        cont = field_ > np.quantile(field_, 1 - p.continental_fraction)
        if p.start == "supercontinent":
            # A supercontinent is one plate: hand it to whichever plate holds
            # most of it, so the story starts with rifting, not collisions.
            k0 = np.bincount(plate[cont], minlength=p.n_plates).argmax()
            plate = np.where(cont, k0, plate)
            # oceanic leftovers cut off from their plate join a neighbour
            for k in range(p.n_plates):
                lab, nl = components(g, plate == k)
                if nl > 1:
                    sizes = np.bincount(lab[lab >= 0])
                    for piece in np.flatnonzero(sizes < sizes.max()):
                        cells = np.flatnonzero(lab == piece)
                        nb = np.concatenate([g.neighbors[i] for i in cells])
                        others = plate[nb][plate[nb] != k]
                        if len(others):
                            plate[cells] = np.bincount(others).argmax()
        # distance inland from the coast -> continental shelf / interior base level
        coast = np.flatnonzero(cont & np.array([not cont[g.neighbors[i]].all() for i in range(n)]))
        dist, _ = kernels.bfs_within(coast, cont.astype(np.int64), g.nbr_off, g.nbr_idx, 50)
        texture = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=6, freq=3.0)
        # shelf: coast cells sit underwater, interiors a few hundred metres up
        inland = np.minimum(np.maximum(dist, 0) / self.scale, 3)
        base = np.where(cont, -450 + 230 * inland + 300 * texture, 0)
        old_mtn = 900 * ridged(Perlin3D(int(rng.integers(2**31))), x, octaves=5, freq=2.5) * cont
        age = np.clip(90 + 90 * fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=3, freq=1.0), 5, 180)
        elev = np.where(cont, base + old_mtn, ocean_depth(age))
        for k in range(p.n_plates):
            m = plate == k
            self.alive[k] = True
            self.owned[k] = m
            self.cont[k] = cont & m
            self.elev[k] = np.where(m, elev, 0)
            self.base[k] = np.where(m, base, 0)
            self.age[k] = np.where(m, age, 0)
            axis = rng.normal(size=3)
            axis /= np.linalg.norm(axis)
            self.omega[k] = axis * rng.uniform(2, 6) / CMYR
        self.owner = plate.astype(np.int64)

    # ------------------------------------------------------------- main loop
    def run(self, until_t: float, on_step=None):
        while self.t < until_t - 1e-9:
            self.step()
            if on_step:
                on_step(self)

    def step(self):
        g, p, dt = self.grid, self.params, self.dt
        self.step_no += 1
        self.t = self.step_no * dt
        rng = np.random.default_rng([self.seed, self.step_no])
        live = np.flatnonzero(self.alive)

        # 1-2. move plates and pull
        for k in live:
            self.Q[k] = rotation(self.omega[k] * dt) @ self.Q[k]
            self.idx[k] = g.locate(g.centers @ self.Q[k], self.idx[k])

        # 3. resolve ownership
        self.owner, newc, coll = _resolve(
            self.alive, self.idx, self.owned, self.elev, self.age, self.cont, self.base,
            self.owner, g.nbr_off, g.nbr_idx, float(ocean_depth(0.0)), self.Q, g.centers)
        _cleanup_ghosts(self.alive, self.owned, self.Q, g.centers, self.owner, g.raster,
                        g.nbr_off, g.nbr_idx)
        self._world_view()

        # 4. boundaries, uplift, forces
        bd = self._boundaries()
        self._physics(bd)
        self._forces(bd, rng)

        # 5. events
        self._sutures(bd)
        self._absorb_slivers()
        self._maybe_rift(rng)
        self._world_view()

    # ------------------------------------------------------------- world view
    def _world_view(self):
        o, i = self.owner, np.arange(self.grid.n)
        r = self.idx[o, i]
        self.w_elev = self.elev[o, r]
        self.w_age = self.age[o, r]
        self.w_cont = self.cont[o, r]
        self.w_base = self.base[o, r]
        self.w_ref = r

    def _scatter(self):
        o, r = self.owner, self.w_ref
        self.elev[o, r] = self.w_elev
        self.age[o, r] = self.w_age
        self.cont[o, r] = self.w_cont
        self.base[o, r] = self.w_base

    def velocity(self) -> np.ndarray:
        """Tangent velocity of every cell (rad/Myr, world frame)."""
        return np.cross(self.omega[self.owner], self.grid.centers)

    # ------------------------------------------------------------- boundaries
    def _boundaries(self):
        g = self.grid
        P = g.centers
        a, b = g.edges[:, 0], g.edges[:, 1]
        m = self.owner[a] != self.owner[b]
        a, b = a[m], b[m]
        d = P[b] - P[a]
        d -= (d * P[a]).sum(1, keepdims=True) * P[a]
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        v = self.velocity()
        conv = ((v[a] - v[b]) * d).sum(1) * CMYR  # cm/yr, >0 = closing
        ca, cb = self.w_cont[a], self.w_cont[b]
        closing = conv > 0.5
        opening = conv < -0.5
        collision = closing & ca & cb
        subduct = closing & ~collision
        # which side goes down: oceanic under continental; older ocean under younger
        a_down = subduct & (~ca & (cb | (self.w_age[a] >= self.w_age[b])))
        b_down = subduct & ~a_down
        return dict(a=a, b=b, d=d, conv=conv, collision=collision, subduct=subduct,
                    a_down=a_down, b_down=b_down, opening=opening)

    # ------------------------------------------------------------- physics
    def _physics(self, bd):
        g, p, dt = self.grid, self.params, self.dt
        n = g.n
        a, b, conv = bd["a"], bd["b"], np.clip(bd["conv"], 0, 15)

        def spread(src_rate, width):
            src = np.flatnonzero(src_rate > 0)
            if len(src) == 0:
                return np.zeros(n)
            w = width * self.scale
            dist, s = kernels.bfs_within(src, self.owner, g.nbr_off, g.nbr_idx, int(3 * w))
            out = np.zeros(n)
            hit = s >= 0
            out[hit] = src_rate[s[hit]] * np.exp(-((dist[hit] / w) ** 2))
            return out

        # arcs on the overriding side of subduction zones
        arc_src = np.zeros(n)
        over = np.concatenate([b[bd["a_down"]], a[bd["b_down"]]])
        rate = np.concatenate([conv[bd["a_down"]], conv[bd["b_down"]]])
        np.maximum.at(arc_src, over, p.arc_uplift * rate)
        # big ranges on both sides of continental collisions
        col_src = np.zeros(n)
        cm = bd["collision"]
        np.maximum.at(col_src, a[cm], p.collision_uplift * conv[cm])
        np.maximum.at(col_src, b[cm], p.collision_uplift * conv[cm])
        uplift = spread(arc_src, 1.6) + spread(col_src, 3.0)

        # Time evolution acts on *every* cell of every plate, in the plate's own
        # frame. (Doing it only on the cells currently visible on the world
        # grid left the 10-20% momentarily unsampled cells un-aged: speckle.)
        own = self.owned
        oc_r, co_r = own & ~self.cont, own & self.cont
        age0 = self.age[oc_r]
        self.age[own] += dt
        # oceanic: depth follows age; anything built on top (arcs) decays slowly
        excess = np.maximum(self.elev[oc_r] - ocean_depth(age0), 0) * np.exp(-dt / 40.0)
        self.elev[oc_r] = ocean_depth(self.age[oc_r]) + excess
        # continental: relax toward base level (stand-in for erosion)
        lvl = self.base[co_r]
        self.elev[co_r] = lvl + (self.elev[co_r] - lvl) * np.exp(-dt / p.erosion_timescale)
        self._world_view()
        self.w_elev = self.w_elev + uplift * dt
        oc = ~self.w_cont
        # island arcs that reach near sea level become new continental crust
        born = oc & (self.w_elev > -400)
        self.w_cont = self.w_cont | born
        self.w_base = np.where(born, 0.0, self.w_base)
        # gentle lateral spreading of continental relief
        ea, eb = g.edges[:, 0], g.edges[:, 1]
        same = (self.owner[ea] == self.owner[eb]) & self.w_cont[ea] & self.w_cont[eb]
        flux = 0.04 * (self.w_elev[eb] - self.w_elev[ea]) * same
        self.w_elev = self.w_elev + np.bincount(ea, flux, n) - np.bincount(eb, flux, n)
        self.w_elev = np.minimum(self.w_elev, 9500)
        self._scatter()

        # remember for snapshots
        bnd = np.zeros(n, np.int8)
        conv_cells = np.concatenate([a[bd["collision"] | bd["subduct"]], b[bd["collision"] | bd["subduct"]]])
        bnd[np.concatenate([a[bd["opening"]], b[bd["opening"]]])] = -1
        bnd[conv_cells] = 1
        self.w_boundary = bnd
        trench = np.zeros(n)
        down = np.concatenate([a[bd["a_down"]], b[bd["b_down"]]])
        np.minimum.at(trench, down, -350 * np.concatenate([conv[bd["a_down"]], conv[bd["b_down"]]]))
        self.w_trench = np.maximum(trench, -4000)

    # ------------------------------------------------------------- forces
    def _forces(self, bd, rng):
        g, p, dt = self.grid, self.params, self.dt
        P = g.centers
        a, b, d, conv = bd["a"], bd["b"], bd["d"], bd["conv"]
        F = np.zeros((g.n, 3))
        L = self.edge_len
        # slab pull: the sinking side is pulled toward (and under) the other plate
        slab_a = p.slab_pull * np.clip(self.w_age[a] / 80, 0.3, 1.5) * L
        slab_b = p.slab_pull * np.clip(self.w_age[b] / 80, 0.3, 1.5) * L
        np.add.at(F, a[bd["a_down"]], d[bd["a_down"]] * slab_a[bd["a_down"], None])
        np.add.at(F, b[bd["b_down"]], -d[bd["b_down"]] * slab_b[bd["b_down"], None])
        # ridge push: away from opening boundaries
        o = bd["opening"]
        np.add.at(F, a[o], -d[o] * p.ridge_push * L)
        np.add.at(F, b[o], d[o] * p.ridge_push * L)
        # collision: resist further closing, harder the faster they close
        c = bd["collision"]
        k = (p.collision_drag * np.clip(conv[c], 0, 15) * L)[:, None]
        np.add.at(F, a[c], -d[c] * k)
        np.add.at(F, b[c], d[c] * k)

        torque = np.zeros((P_MAX, 3))
        np.add.at(torque, self.owner, np.cross(P, F))
        w = self.cell_area * (1 + p.continental_keel * self.w_cont)
        outer = (np.eye(3)[None] - P[:, :, None] * P[:, None, :]) * w[:, None, None]
        drag = np.zeros((P_MAX, 3, 3))
        np.add.at(drag, self.owner, outer)

        decay = np.exp(-dt / p.mantle_timescale)
        relax = 1 - np.exp(-dt / p.velocity_timescale)
        for k in np.flatnonzero(self.alive):
            area = np.trace(drag[k]) / 2
            if area <= 0:
                continue
            # wandering basal drag: an Ornstein-Uhlenbeck process, scaled by plate area
            self.mantle[k] = self.mantle[k] * decay + np.sqrt(1 - decay**2) * rng.normal(size=3)
            tau = torque[k] + p.mantle_noise * self.mantle[k] * area * 0.5
            Dk = drag[k] + 0.1 * area * np.eye(3)  # regularise spin about the plate's own centre
            target = p.mobility * np.linalg.solve(Dk, tau)
            self.omega[k] += (target - self.omega[k]) * relax
            vmax = np.linalg.norm(np.cross(self.omega[k], P[self.owner == k]), axis=1).max(initial=0) * CMYR
            if vmax > p.max_speed:
                self.omega[k] *= p.max_speed / vmax

    # ------------------------------------------------------------- events
    def _log(self, kind, slots, where, template):
        """template uses {0}, {1}... for the plates' permanent ids."""
        ids = [int(self.label[s]) for s in slots]
        lat, lon = latlon(where)
        self.events.append(Event(self.t, kind, ids, lat, lon, template.format(*ids)))

    def _merge(self, keep, gone):
        """Move plate `gone`'s crust into plate `keep`'s reference frame."""
        g = self.grid
        # Pull, don't push: for every empty cell of `keep`'s grid, ask whether
        # `gone` has crust at that spot. (Pushing gone's cells into keep's grid
        # skips some cells, because the two grids are rotated relative to
        # each other, and leaves a lacy pattern of holes.)
        t = np.flatnonzero(~self.owned[keep])
        world = g.centers[t] @ self.Q[keep].T
        r = g.locate(world @ self.Q[gone])
        has = self.owned[gone, r]
        t, r = t[has], r[has]
        self.owned[keep, t] = True
        for arr in (self.elev, self.age, self.base, self.cont):
            arr[keep, t] = arr[gone, r]
        ak, ag = (self.owner == keep).sum(), (self.owner == gone).sum()
        self.omega[keep] = (self.omega[keep] * ak + self.omega[gone] * ag) / max(ak + ag, 1)
        self.owned[gone] = False
        self.alive[gone] = False
        self.owner[self.owner == gone] = keep
        self.contact[gone, :] = 0
        self.contact[:, gone] = 0

    def _sutures(self, bd):
        p, g = self.params, self.grid
        c = bd["collision"]
        pairs = np.stack([self.owner[bd["a"][c]], self.owner[bd["b"][c]]], 1)
        pairs.sort(axis=1)
        cnt = np.zeros((P_MAX, P_MAX), int)
        np.add.at(cnt, (pairs[:, 0], pairs[:, 1]), 1)
        thr = max(3, int(4 * self.scale))
        active = cnt >= thr
        # contact builds while touching and drains (not resets) when not, so a
        # boundary hovering around the threshold doesn't flicker
        started = active & (self.contact == 0) & (self.t - self.last_logged > 40)
        for i, j in zip(*np.nonzero(started)):
            sel = (pairs[:, 0] == i) & (pairs[:, 1] == j)
            where = g.centers[bd["a"][c][sel]].mean(0)
            self._log("collision", [i, j], where, "continents on plates {0} and {1} collide")
            self.last_logged[i, j] = self.t
        self.contact = np.where(active, self.contact + self.dt, np.maximum(self.contact - self.dt, 0))
        for i, j in zip(*np.nonzero(self.contact >= p.suture_after)):
            if not (self.alive[i] and self.alive[j]) or self.t - self.rifted_at[i, j] < 80:
                continue
            sel = (pairs[:, 0] == i) & (pairs[:, 1] == j)
            where = g.centers[bd["a"][c][sel]].mean(0) if sel.any() else g.centers[self.owner == i].mean(0)
            ai, aj = (self.owner == i).sum(), (self.owner == j).sum()
            keep, gone = (i, j) if ai >= aj else (j, i)
            self._merge(keep, gone)
            self._log("suture", [keep, gone], where,
                      "plates {0} and {1} weld together along their collision; {1} is absorbed")

    def _absorb_slivers(self):
        g = self.grid
        sizes = np.bincount(self.owner, minlength=P_MAX)
        min_cells = max(4, int(0.0015 * g.n))
        for k in np.flatnonzero(self.alive & (sizes < min_cells)):
            if self.alive.sum() <= 2:
                break
            cells = np.flatnonzero(self.owner == k)
            if len(cells) == 0:
                self.alive[k] = False
                self.owned[k] = False
                self._log("consumed", [k], g.centers[0], "plate {0} has been entirely subducted")
                continue
            nb = np.concatenate([g.neighbors[i] for i in cells])
            others = self.owner[nb][self.owner[nb] != k]
            if len(others) == 0:
                continue
            keep = int(np.bincount(others).argmax())
            where = g.centers[cells].mean(0)
            self._merge(keep, k)
            self._log("absorbed", [keep, k], where, "remnant plate {1} is absorbed into plate {0}")

    def _maybe_rift(self, rng):
        p, g = self.params, self.grid
        if self.alive.sum() >= min(p.max_plates, P_MAX):
            return
        P = g.centers
        cont_cells = np.bincount(self.owner, weights=self.w_cont, minlength=P_MAX)
        all_cells = np.bincount(self.owner, minlength=P_MAX)
        threshold = p.rift_min_continent * g.n
        big = p.big_plate * g.n
        for k in np.flatnonzero(self.alive):
            # big continents rift (heat builds up under them); so, more slowly,
            # do very large plates of any kind (ridge jumps, new plates forming)
            rate = max(cont_cells[k] / threshold if cont_cells[k] >= threshold else 0,
                       0.5 * all_cells[k] / big if all_cells[k] >= big else 0)
            if rate == 0 or rng.random() > 1 - np.exp(-self.dt / p.rift_timescale * rate):
                continue
            continental = cont_cells[k] >= threshold
            # cut through the plate's continental core (or the whole plate) with a wiggly great circle
            core = P[(self.owner == k) & (self.w_cont if continental else True)]
            c = core.mean(0)
            c /= np.linalg.norm(c)
            t = rng.normal(size=3)
            t -= (t @ c) * c
            t /= np.linalg.norm(t)
            nz = Perlin3D(int(rng.integers(2**31)))
            refs = np.flatnonzero(self.owned[k])
            world = P[refs] @ self.Q[k].T
            side = (world - c) @ t + 0.12 * fbm(nz, world, octaves=4, freq=3.0) > 0
            frac = side.mean()
            if not 0.2 < frac < 0.8:
                continue
            new = int(np.flatnonzero(~self.alive)[0])
            self.label[new] = self.next_label
            self.next_label += 1
            for arr in (self.contact, self.last_logged, self.rifted_at):
                fill = 0 if arr is self.contact else -1e9
                arr[new, :] = fill
                arr[:, new] = fill
            self.mantle[new] = 0
            self.alive[new] = True
            self.Q[new] = self.Q[k]
            self.idx[new] = self.idx[k]
            self.owned[new] = False
            r = refs[side]
            self.owned[new, r] = True
            self.owned[k, r] = False
            for arr in (self.elev, self.age, self.base, self.cont):
                arr[new] = arr[k]
            cA = world[~side].mean(0)
            cB = world[side].mean(0)
            axis = np.cross(cA, cB)
            axis /= np.linalg.norm(axis)
            push = 2.5 / CMYR
            self.omega[new] = self.omega[k] + axis * push
            self.omega[k] = self.omega[k] - axis * push
            # the rift keeps pushing for a while: seed the wandering term
            self.mantle[new] = self.mantle[k] + axis * 4.0
            self.mantle[k] = self.mantle[k] - axis * 4.0
            a_, b_ = min(k, new), max(k, new)
            self.rifted_at[a_, b_] = self.t
            self.last_logged[a_, b_] = self.t
            self.contact[a_, b_] = 0
            moved = np.isin(self.w_ref, r) & (self.owner == k)
            self.owner[moved] = new
            what = "continent on plate" if continental else "oceanic plate"
            self._log("rift", [k, new], c, what + " {0} rifts apart; the split-off part becomes plate {1}")
            return  # at most one rift per step

    # ------------------------------------------------------------- output
    def snapshot(self) -> Snapshot:
        live = np.flatnonzero(self.alive)
        return Snapshot(
            t=self.t,
            elevation=np.where(self.w_cont, self.w_elev, self.w_elev + getattr(self, "w_trench", 0)),
            plate=self.label[self.owner],
            continental=self.w_cont.copy(),
            age=self.w_age.copy(),
            boundary=getattr(self, "w_boundary", np.zeros(self.grid.n, np.int8)).copy(),
            omega={int(self.label[k]): self.omega[k].tolist() for k in live},
        )

    def stats(self) -> dict:
        g = self.grid
        land = self.w_elev > 0
        lab, nlab = components(g, land)
        sizes = np.bincount(lab[lab >= 0], minlength=1) if nlab else np.array([0])
        v = np.linalg.norm(self.velocity(), axis=1) * CMYR
        return {
            "t": self.t,
            "plates": int(self.alive.sum()),
            "land_pct": round(100 * land.mean(), 1),
            "continental_pct": round(100 * self.w_cont.mean(), 1),
            "landmasses": int((sizes >= 3).sum()),
            "largest_landmass_pct": round(100 * sizes.max() / g.n, 1),
            "max_elev_m": int(self.w_elev.max()),
            "mean_speed_cmyr": round(float(v.mean()), 2),
            "max_speed_cmyr": round(float(v.max()), 2),
        }
