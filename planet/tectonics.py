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
 4. Physics on the resulting world map. Every cell carries a crust
    thickness, and elevation follows from it by isostasy (thick crust floats
    higher) plus, for ocean floor, its age (it sinks as it cools). Arcs
    add crust above subducting slabs (Andes, Japan); collisions stack it
    (Himalaya/Tibet), very thick crust flows sideways, erosion (placeholder)
    removes it from high ground, and part of that becomes sediment on the
    continental margins. Continental crust is conserved through all of it,
    so the continents neither leak away nor swell over billions of years.
 5. Forces -> velocities. Plates have no momentum (it's basically very slow
    Stokes flow), so each step the velocity is *solved* from the forces:
    slab pull (dominant), ridge push, collision resistance, and a slowly
    wandering mantle-drag term that supplies meandering.
 6. Events: long collisions weld plates together; plates split when a big
    continent overheats the mantle beneath it, when the forces on a plate
    pull its halves apart, or when old ocean floor at a passive margin
    breaks off and starts to sink (new subduction); slivers get absorbed.

Determinism: all randomness for step s comes from default_rng([seed, s]),
so any step can be reproduced exactly by re-running from t=0.

Units: time in Myr, angular velocity in rad/Myr on the unit sphere,
speeds reported in cm/yr (1 cm/yr = 10 km/Myr), elevation in metres.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numba import njit

from . import climate, kernels, surface
from .grid import Grid
from .surface import ARC, CRATON, HOTSPOT, OCEAN, OROGEN, SEDIMENT
from .noise import Perlin3D, fbm, ridged

R_KM = 6371.0
CMYR = R_KM / 10.0  # (rad/Myr on unit sphere) -> cm/yr
P_MAX = 48


@dataclass
class Params:
    n_plates: int = 12
    start: str = "supercontinent"  # or "scattered"
    # starting share of the surface that's continental crust, and the level
    # the thermostat on island-arc growth holds it near (Earth: ~0.41)
    continental_fraction: float = 0.4
    # forces (arbitrary units; mobility converts torque to rad/Myr)
    slab_pull: float = 1.0
    ridge_push: float = 0.15
    collision_drag: float = 1.2
    mantle_noise: float = 0.35
    mantle_timescale: float = 60.0  # Myr: how fast the wandering drag term changes
    velocity_timescale: float = 15.0  # Myr: smoothing on velocity changes (plate inertia, in effect)
    continental_keel: float = 1.5  # extra drag per continental cell
    mobility: float = 0.008
    max_speed: float = 18.0  # cm/yr
    # crust: arcs add new crust above subducting slabs (km/Myr per cm/yr of
    # convergence, before the thermostat); collisions stack crust (see
    # _resolve), which then flows sideways where it's very thick
    arc_growth: float = 0.03
    # per Myr between level-5 neighbours, times (x + x^3), x = (crust - 40 km)/10 km.
    # (At 0.03 the stability clamp in _crust_flow always bound, so plateaus
    # flattened at the numerical limit: ~1 km in 4 Myr from flow alone.)
    crust_flow: float = 0.0006
    # surface (see surface.py): erosion, rivers, sediment, climate
    hillslope: float = 100.0  # km^2/Myr: wearing-down of ground standing above its neighbours
    erosion_timescale: float = 400.0  # Myr e-folding of low ground above base level (weathering)...
    erosion_height: float = 2000.0  # m: ...which gets (1 + (h/this)^2) times faster higher up
    stretching: float = 0.01  # per Myr per cm/yr of opening: continental crust thins near rifts
    incision: float = 0.004  # river cutting, per Myr per sqrt(flow)
    climate_every: float = 10.0  # Myr between rainfall updates
    # hotspots: mantle plumes fixed in the mantle; plates slide over them
    hotspots: int = 10  # typical number alive at once
    hotspot_life: float = 120.0  # Myr, mean
    hotspot_rate: float = 4.0  # km/Myr of crust added at the centre (a quarter of that under continents)
    hotspot_at_ridges: float = 0.6  # share of new plumes that rise under a ridge or rift
    volcano_life: float = 8.0  # Myr an arc volcano (or its replacement nearby) stays active
    volcano_spacing: float = 350.0  # km: at most one shown volcano per this much arc
    volcano_km: float = 2.0  # km of crust a new volcano adds to its cell (~300 m on land)
    swell_time: float = 12.0  # Myr: the swell decays behind a plume as the plate carries it off
    # reefs: carbonate builds shallow sea floor up to sea level where it's warm and clear
    reef_temp: float = 23.5  # C, annual mean sea surface (reefs reach ~30 deg latitude)
    reef_rate: float = 200.0  # m/Myr of build-up near the surface (much less deeper: light-limited)
    reef_mud: float = 10.0  # m/Myr of river mud deposited is enough to smother reefs
    # mantle heat at the start relative to the end state (1 = steady, today's Earth);
    # scales plume numbers, arc melting and (as sqrt) plate speed. See Simulation.heat
    heat_start: float = 1.0
    heat_halflife: float = 600.0  # Myr
    # events
    suture_after: float = 30.0  # Myr of continental collision before plates can weld...
    suture_closing: float = 2.0  # ...once they've (nearly) stopped converging, cm/yr
    suture_max: float = 150.0  # Myr: weld anyway after this long
    rift_timescale: float = 130.0  # Myr: mean time before a big continental plate rifts
    rift_min_continent: float = 0.07  # fraction of surface
    stress_min_plate: float = 0.05  # plates larger than this (any crust) can break under stress
    rift_stress: float = 3.0  # cm/yr: how hard the halves must pull apart before it can break
    big_plate: float = 0.2  # plates bigger than this fraction of the surface break up more readily
    settle_time: float = 30.0  # Myr after forming before a plate can break under stress
    margin_age: float = 120.0  # Myr: ocean floor older than this at a passive margin may start subducting
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
def _fill(k, r, refs, owned, age, cont, thick, rock, cover, extra):
    """Fill hole r in plate k's grid from its neighbours refs (-1 = not part
    of this plate). It's continental only if it's completely enclosed by
    continent; otherwise it copies just its oceanic neighbours. A notch in a
    continent's edge (no oceanic neighbour, not enclosed) is left empty.

    A majority vote here let continents fill in their own ragged edges every
    step and slowly swell (~1.5% of the planet per 100 Myr)."""
    nc, no = 0, 0
    sa, st, sc, oa, ot, oc = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    nx = extra.shape[2]
    sx, ox = np.zeros(nx), np.zeros(nx)
    rc, ro = -1, -1
    for j in refs:
        if j < 0 or not owned[k, j]:
            continue
        if cont[k, j]:
            nc += 1
            sa += age[k, j]
            st += thick[k, j]
            sc += cover[k, j]
            sx += extra[k, j]
            rc = j
        else:
            no += 1
            oa += age[k, j]
            ot += thick[k, j]
            oc += cover[k, j]
            ox += extra[k, j]
            ro = j
    if nc == len(refs):
        age[k, r], thick[k, r], cont[k, r], cover[k, r] = sa / nc, st / nc, True, sc / nc
        rock[k, r] = rock[k, rc]
        extra[k, r] = sx / nc
    elif no > 0:
        age[k, r], thick[k, r], cont[k, r], cover[k, r] = oa / no, ot / no, False, oc / no
        rock[k, r] = rock[k, ro]
        extra[k, r] = ox / no
    else:
        return False
    owned[k, r] = True
    return True


@njit(cache=True)
def _resolve(alive, idx, owned, age, cont, thick, rock, cover, extra, prev_owner, nbr_off, nbr_idx, Q, centers, stacked):
    """Decide which plate owns each world cell; delete subducted crust,
    fill aliasing holes, create new ocean floor in gaps.
    Returns (owner, new_crust flag, collision count matrix).

    Continent vs continent: the loser's crust isn't destroyed, it's stacked
    onto the winner's (crust is too buoyant to sink: collisions thicken it)."""
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
            cnt, tot = 0, nbr_off[r + 1] - nbr_off[r]
            for e in range(nbr_off[r], nbr_off[r + 1]):
                if owned[k, nbr_idx[e]]:
                    cnt += 1
            if cnt >= tot - 2:
                _fill(k, r, nbr_idx[nbr_off[r]:nbr_off[r + 1]], owned, age, cont, thick, rock, cover, extra)
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
                if k == prev_owner[i] or (w != prev_owner[i] and thick[k, rk] > thick[w, rw]):
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
                stacked[i] += thick[k, rk]  # spread over a belt in _physics
                if rock[w, rw] != CRATON:
                    rock[w, rw] = OROGEN  # buried, squeezed and cooked
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
            r = idx[best_k, i]
            if _fill(best_k, r, nbr_idx[nbr_off[r]:nbr_off[r + 1]], owned, age, cont, thick, rock, cover, extra):
                owner[i] = best_k
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
            refs = np.full(deg, -1, np.int64)
            for e in range(nbr_off[i], nbr_off[i + 1]):
                if owner[nbr_idx[e]] == k:
                    refs[e - nbr_off[i]] = idx[k, nbr_idx[e]]
            if _fill(k, idx[k, i], refs, owned, age, cont, thick, rock, cover, extra):
                owner[i] = k
                continue
        if counts[k] == 0:
            k = prev_owner[i] if prev_owner[i] >= 0 and alive[prev_owner[i]] else np.argmax(alive)
        r = idx[k, i]
        owned[k, r] = True
        age[k, r] = 0.0
        thick[k, r] = OCEAN_KM
        rock[k, r] = OCEAN
        cover[k, r] = 0.0
        extra[k, r] = 0.0
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
                age[k, r2] = 0.0
                thick[k, r2] = OCEAN_KM
                rock[k, r2] = OCEAN
                cover[k, r2] = 0.0
                extra[k, r2] = 0.0
                cont[k, r2] = False
    return owner, newc, coll


@njit(cache=True)
def _crust_flow(t, ea, eb, k0, n_sub):
    """Thick crust spreads to its neighbours, faster the thicker it is."""
    t = t.copy()
    flux = np.empty(len(ea))
    for _ in range(n_sub):
        for e in range(len(ea)):
            a, b = ea[e], eb[e]
            x = max(max(t[a], t[b]) - 40.0, 0.0) / 10.0
            flux[e] = min(k0 * (x + x * x * x), 0.15) * (t[b] - t[a])
        for e in range(len(ea)):
            t[ea[e]] += flux[e]
            t[eb[e]] -= flux[e]
    return t


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


# Crust thickness (km) and isostasy. Crust floats on the denser mantle like
# ice on water: thicker crust stands higher, and for continents ~85% of any
# thickening is hidden below as a root (Airy isostasy: 1 km of extra crust
# -> ~150 m of extra elevation). 35 km of continental crust sits at ~250 m;
# Tibet's ~70 km gives ~5.5 km.
OCEAN_KM = 7.0  # normal oceanic crust
CONT_KM = 35.0  # normal continental crust
BECOMES_CONT_KM = 20.0  # an arc or sediment pile this thick is continental crust
MAX_KM = 80.0
ISO_LAND = 150.0  # m of elevation per km of crust
ISO_SEA = 200.0  # under water the displaced stuff is water, not air


# Extra per-cell numbers carried by every plate (column order):
#   lift  m of broad doming over a plume; it rides away with the plate and
#         decays as the hot mantle under it cools (Hawaii's swell trails
#         ~1000 km down the chain)
#   carb  km of the sediment cover that is carbonate (limestone), and
#   lava  km of it that is lava flows (flood basalts, hotspot tracks);
#         the rest is ordinary sediment (sand, mud)
EXTRA = ("lift", "carb", "lava")
LIFT, CARB, LAVA = range(3)


ISO_VOLCANO = 350.0  # a narrow volcanic pile is also held up by the stiff plate around it (flexure)


def isostasy(cont, rock):
    """m of elevation per km of crust added or removed, per cell."""
    return np.where(cont, ISO_LAND, np.where(rock == HOTSPOT, ISO_VOLCANO, ISO_SEA))


def elevation(thick, age, cont, rock=None, swell=0.0):
    sea = ISO_SEA if rock is None else np.where(rock == HOTSPOT, ISO_VOLCANO, ISO_SEA)
    return np.where(cont, 250 + ISO_LAND * (thick - CONT_KM),
                    ocean_depth(age) + sea * (thick - OCEAN_KM)) + swell


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
    rock: np.ndarray  # surface.ROCKS id of the basement
    cover: np.ndarray  # km of sediment on top
    thickness: np.ndarray  # km of crust
    precip: np.ndarray  # mm/yr
    flow: np.ndarray  # river flow (sum of upstream rainfall, cells x m/yr)
    downstream: np.ndarray  # next cell down the river, -1 at the sea
    hotspots: list  # [lat, lon] of each live plume
    volcanoes: list  # [lat, lon] of each active arc volcano
    surface: np.ndarray  # surface.ROCKS id of what's exposed (basement or its sediment cover)


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
        self.age = np.zeros((P_MAX, n))
        self.thick = np.zeros((P_MAX, n))
        self.rock = np.zeros((P_MAX, n), np.uint8)
        self.cover = np.zeros((P_MAX, n))  # km of sediment on top of the basement
        self.extra = np.zeros((P_MAX, n, len(EXTRA)))  # see EXTRA
        self.hotspots = []  # dicts: pos (mantle frame = world frame), born, life
        self.volcanoes = []  # arc volcanoes: dicts plate, ref (cell in the plate's frame), born, life, pos
        self.cont = np.zeros((P_MAX, n), bool)
        self.idx = np.tile(np.arange(n), (P_MAX, 1))
        self.contact = np.zeros((P_MAX, P_MAX))
        self.closing = np.zeros((P_MAX, P_MAX))  # cm/yr, smoothed, for colliding pairs
        self.last_logged = np.full((P_MAX, P_MAX), -1e9)
        self.rifted_at = np.full((P_MAX, P_MAX), -1e9)
        self.formed = np.zeros(P_MAX)  # when each plate got its current shape
        self.precip, self.temp, self.climate_t = None, None, 0.0
        self.removed = self.flow = self.stacked = np.zeros(n)
        self.down = np.full(n, -1, np.int64)
        self.swell = np.zeros(n)  # m: broad dome pushed up by active plumes
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
            # Its plate also carries the ocean near its coast (passive margins,
            # like the Atlantic's today). Otherwise every bay belongs to some
            # other plate and the breakup tears the coast into fingers.
            near, _ = kernels.bfs_within(np.flatnonzero(cont), np.zeros(n, np.int64),
                                         g.nbr_off, g.nbr_idx, int(3 * self.scale))
            plate = np.where(near >= 0, k0, plate)
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
        thick = np.where(cont, np.maximum(CONT_KM + (elev - 250) / ISO_LAND, BECOMES_CONT_KM + 1), OCEAN_KM)
        # What the planet's unsimulated early history leaves behind: ancient
        # cratons deep inside the continents, wrapped in old mountain belts,
        # partly under a blanket of flat-lying sediment.
        core = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=4, freq=2.0)
        craton = cont & (dist >= 2 * self.scale) & (core > -0.05)
        rock = np.where(craton, CRATON, np.where(cont, OROGEN, OCEAN)).astype(np.uint8)
        blanket = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=4, freq=3.0)
        cover = np.where(cont, np.clip(1.5 * blanket + 0.6, 0, 3) + np.where(inland < 1, 1.5, 0), 0)
        for k in range(p.n_plates):
            m = plate == k
            self.alive[k] = True
            self.owned[k] = m
            self.cont[k] = cont & m
            self.thick[k] = np.where(m, thick, 0)
            self.rock[k] = np.where(m, rock, 0)
            self.cover[k] = np.where(m, cover, 0)
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
        self.stacked = np.zeros(g.n)
        self.owner, newc, coll = _resolve(
            self.alive, self.idx, self.owned, self.age, self.cont, self.thick, self.rock, self.cover, self.extra,
            self.owner, g.nbr_off, g.nbr_idx, self.Q, g.centers, self.stacked)
        _cleanup_ghosts(self.alive, self.owned, self.Q, g.centers, self.owner, g.raster,
                        g.nbr_off, g.nbr_idx)
        self._world_view()

        # 4. boundaries, uplift, forces
        bd = self._boundaries()
        self._physics(bd, rng)
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
        self.w_age = self.age[o, r]
        self.w_cont = self.cont[o, r]
        self.w_thick = self.thick[o, r]
        self.w_rock = self.rock[o, r]
        self.w_cover = self.cover[o, r]
        self.w_extra = self.extra[o, r]
        self.swell = self.w_extra[:, LIFT]
        self.w_elev = elevation(self.w_thick, self.w_age, self.w_cont, self.w_rock, self.swell)
        self.w_ref = r

    def _scatter(self):
        o, r = self.owner, self.w_ref
        self.age[o, r] = self.w_age
        self.cont[o, r] = self.w_cont
        self.thick[o, r] = self.w_thick
        self.rock[o, r] = self.w_rock
        self.cover[o, r] = self.w_cover
        self.extra[o, r] = self.w_extra

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
    def _physics(self, bd, rng):
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

        # arcs: melting above the sinking slab adds new crust to the overriding
        # plate. A thermostat holds continental area near continental_fraction
        # (real growth vs. loss at trenches is roughly balanced but uncertain).
        frac = max(self.w_cont.mean(), 1e-3)
        thermostat = np.clip((p.continental_fraction / frac) ** 4, 0.1, 5.0)
        arc_src = np.zeros(n)
        over = np.concatenate([b[bd["a_down"]], a[bd["b_down"]]])
        rate = np.concatenate([conv[bd["a_down"]], conv[bd["b_down"]]])
        np.maximum.at(arc_src, over, p.arc_growth * self.heat() * thermostat * rate)
        growth = spread(arc_src, 1.6)
        # rifting stretches continental crust thin near the opening boundary;
        # that thinned crust is why continents have drowned shelves and slopes
        rift_src = np.zeros(n)
        op = bd["opening"]
        opening_rate = -np.clip(bd["conv"][op], -15, 0)
        np.maximum.at(rift_src, a[op], p.stretching * opening_rate)
        np.maximum.at(rift_src, b[op], p.stretching * opening_rate)
        stretch = spread(rift_src, 1.0)
        plume, dome = self._hotspots(rng, bd)

        # Ageing acts on *every* cell of every plate, in the plate's own frame.
        # (Doing it only on the cells currently visible on the world grid left
        # the 10-20% momentarily unsampled cells un-aged: speckle.)
        self.age[self.owned] += dt
        self._world_view()
        cont, rock = self.w_cont, self.w_rock.copy()
        x = self.w_extra.copy()
        # the swell rides off with the plate and subsides as the mantle under it cools
        x[:, LIFT] = np.maximum(x[:, LIFT] * np.exp(-dt / p.swell_time), dome)
        self.swell = x[:, LIFT]
        # Volcanoes can't build forever: past ~4.5 km above the sea (Mauna Kea,
        # 10 km above its sea floor) magma can't lift itself to the summit and
        # the flanks slide away. Plume heads under continents make broad lava
        # plateaus (~2.5 km, Yellowstone) rather than peaks.
        as_volcano = elevation(self.w_thick, self.w_age, cont, np.where(cont, rock, HOTSPOT), self.swell)
        room = np.maximum(np.where(cont, 2500.0, 4500.0) - as_volcano, 0) / np.where(cont, ISO_LAND, ISO_VOLCANO)
        plume = np.minimum(plume * np.where(cont, 0.25, 1.0) * dt, room) / dt
        t = self.w_thick + growth * dt + plume * dt
        # on a continent the plume's lava spreads over the land as a cover of
        # basalt flows (Snake River Plain, Deccan Traps)
        cover = self.w_cover + plume * dt * cont
        x[:, LAVA] += plume * dt * cont
        # Collisions: the crust that was shortened away is stacked into a
        # belt a few hundred km wide (Himalaya + Tibet), not one cell.
        ea, eb = g.edges[:, 0], g.edges[:, 1]
        both = (self.owner[ea] == self.owner[eb]) & cont[ea] & cont[eb]
        if self.stacked.any():
            t = t + surface._spread(self.stacked, ea[both], eb[both], 0.15, int(round(6 * self.scale**2)))
        # arc rock: on continents wherever arcs build; at sea only once the
        # crust has thickened into a real island arc
        arcky = (growth * dt > 0.1) & (rock != CRATON) & (cont | (t > OCEAN_KM + 5))
        rock[arcky] = ARC
        t = self._volcanoes(growth, t, rng)
        thin = cont & (t > 22)
        t[thin] = np.maximum(22.0, t[thin] * np.exp(-stretch[thin] * dt))
        rock[~cont & (plume * dt > 0.2)] = HOTSPOT

        # crustal flow: very thick crust is hot and weak at depth and spreads
        # sideways (Tibet is doing this now), within a continent on one plate.
        # Faster the thicker it is, which is why crust >~70 km is so rare.
        # A diffusion: per-cell rates scale with 1/spacing^2, so finer grids
        # take more (equally stable) substeps.
        t = _crust_flow(t, ea[both], eb[both], p.crust_flow * dt / 3, int(round(3 * self.scale**2)))
        t = np.minimum(t, MAX_KM)
        rock[(t > 50) & cont & (rock != CRATON) & (rock != ARC)] = OROGEN

        # weather, rivers, erosion, sediment
        if self.precip is None or self.t - self.climate_t >= p.climate_every - 1e-9:
            e = elevation(t, self.w_age, cont, rock, self.swell)
            self.temp = climate.temperature(g, e)
            self.precip = climate.precipitation(g, e, self.temp)
            self.climate_t = self.t
        t, cover, x[:, CARB], x[:, LAVA], self.removed, dep, self.flow, self.down = surface.erode(
            g, elevation(t, self.w_age, cont, rock, self.swell), t, cover, x[:, CARB], x[:, LAVA], rock, cont,
            self.precip, dt, p.hillslope, p.erosion_timescale, p.erosion_height, p.incision, self.scale,
            isostasy(cont, rock))

        # Reefs: in warm, clear, shallow sea, corals and other carbonate
        # makers build up to just below sea level, fast enough to outpace any
        # subsidence. A volcanic island that sinks with its ageing sea floor
        # becomes an atoll; carried out of the tropics, the reef dies and it
        # drowns into a flat-topped seamount (the Darwin point, ~30 deg).
        # Muddy water from big rivers stops them (no reefs off the Amazon).
        e = elevation(t, self.w_age, cont, rock, self.swell)
        reef = (e < -5) & (e > -1500) & (self.temp >= p.reef_temp) & (dep * 1000 < p.reef_mud * dt)
        grow = np.minimum(p.reef_rate * np.exp((e + 5) / 150.0) * dt, -5 - e) * reef  # m of elevation
        carb = grow / isostasy(cont, rock)
        t, cover = t + carb, cover + carb
        x[:, CARB] += carb

        # ocean crust thickened enough by arcs or sediment becomes continental;
        # hotspot piles (Hawaii, Iceland) stay oceanic however big, unless
        # it's sediment from a nearby continent that's piling up on them
        sedimented = cover > 0.5 * (t - OCEAN_KM)
        born = ~cont & (t >= BECOMES_CONT_KM) & ((rock != HOTSPOT) | sedimented)
        rock[born] = np.where(sedimented[born], SEDIMENT, ARC)
        self.w_cont = cont | born
        self.w_thick = np.clip(t, 1.0, MAX_KM)
        self.w_cover = np.clip(cover, 0, self.w_thick)
        shrink = self.w_cover / np.maximum(cover, 1e-9)
        x[:, CARB] = np.clip(x[:, CARB] * shrink, 0, self.w_cover)
        x[:, LAVA] = np.clip(x[:, LAVA] * shrink, 0, self.w_cover - x[:, CARB])
        self.w_extra = x
        self.w_rock = rock
        self.w_elev = elevation(self.w_thick, self.w_age, self.w_cont, self.w_rock, self.swell)
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

    def heat(self) -> float:
        """Mantle heat relative to today's. A young planet is hotter (more
        radioactive decay, leftover heat of formation): more plumes, more
        melting at arcs, a runnier mantle and faster plates. It fades toward
        1 with the given half-life."""
        p = self.params
        return 1.0 + (p.heat_start - 1.0) * 0.5 ** (self.t / p.heat_halflife)

    def _volcanoes(self, growth, t, rng):
        """The ring of fire: individual volcanoes along active arcs (Fuji,
        Rainier, the Andes' peaks). Each is far smaller than a cell, so it's a
        point on the map plus a modest bump of crust; it rides with its plate,
        stays active for a few Myr and then erodes away. Spaced out so that
        only a representative few show, not every vent."""
        p, g, dt = self.params, self.grid, self.dt
        live = []
        for v in self.volcanoes:
            k, r = v["plate"], v["ref"]
            if self.t - v["born"] < v["life"] and self.alive[k] and self.owned[k, r]:
                v["pos"] = g.centers[r] @ self.Q[k].T
                live.append(v)
        self.volcanoes = live
        # only on established arcs: continental margins (Andes, Cascades) or
        # island arcs that have built up near the surface (Japan, Aleutians)
        near_top = elevation(t, self.w_age, self.w_cont, self.w_rock, self.swell) > -1500
        cand = np.flatnonzero((growth * dt > 0.15) & near_top & (self.w_cont | (t > OCEAN_KM + 8)))
        if len(cand) == 0:
            return t
        cand = cand[rng.random(len(cand)) < dt / p.volcano_life]
        min_cos = np.cos(p.volcano_spacing / R_KM)
        pts = [v["pos"] for v in self.volcanoes]
        for i in rng.permutation(cand):
            c = g.centers[i]
            if pts and (np.asarray(pts) @ c).max() > min_cos:
                continue
            k = int(self.owner[i])
            self.volcanoes.append({"plate": k, "ref": int(self.w_ref[i]), "born": self.t, "pos": c,
                                   "life": rng.uniform(0.5, 1.5) * p.volcano_life})
            pts.append(c)
            t[i] += p.volcano_km
        return t

    def _hotspots(self, rng, bd):
        """Mantle plumes: fixed in the mantle while plates slide over them, so
        each leaves a trail of volcanoes that drift away, erode and sink as
        their sea floor ages (Hawaii -> Emperor seamounts). A new plume's
        head arrives as a short, huge outpouring (flood basalts, like the
        Deccan Traps). Most plumes sit under ridges or rifts (Iceland,
        Galapagos, Afar: hot mantle and spreading plates find each other);
        the rest anywhere (Hawaii, mid-plate).
        Returns (crust added per Myr, dome height in m) on each world cell."""
        p, g = self.params, self.grid
        self.hotspots = [h for h in self.hotspots if self.t - h["born"] < h["life"]]
        n_new = rng.poisson(p.hotspots * self.heat() * self.dt / p.hotspot_life)
        if self.step_no == 1:
            n_new = int(round(p.hotspots * self.heat()))  # start with a full set, of mixed ages
        spreading = np.concatenate([bd["a"][bd["opening"]], bd["b"][bd["opening"]]])
        for _ in range(n_new):
            v = rng.normal(size=3)
            if len(spreading) and rng.random() < p.hotspot_at_ridges:
                v = g.centers[rng.choice(spreading)] + rng.normal(size=3) * 100.0 / R_KM
            life = rng.uniform(0.4, 1.6) * p.hotspot_life
            born = self.t - (rng.uniform(0, life) if self.step_no == 1 else 0.0)
            self.hotspots.append({"pos": v / np.linalg.norm(v), "born": born, "life": life,
                                  "strength": rng.uniform(0.5, 1.5)})
        out = np.zeros(g.n)
        dome = np.zeros(g.n)
        r = 150.0 / R_KM  # plume radius, radians
        for h in self.hotspots:
            age = self.t - h["born"]
            head = 4.0 if age < 6 else 1.0
            d2 = 2 * (1 - g.centers @ h["pos"])  # chord^2 ~ angle^2
            near = d2 < (3 * r) ** 2
            out[near] += p.hotspot_rate * h["strength"] * head * np.exp(-d2[near] / r**2)
            dome = np.maximum(dome, 1000.0 * h["strength"] * np.exp(-d2 / (4 * r) ** 2))
        return out, dome

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
        cell_torque = np.cross(P, F)
        np.add.at(torque, self.owner, cell_torque)
        w = self.cell_area * (1 + p.continental_keel * self.w_cont)
        outer = (np.eye(3)[None] - P[:, :, None] * P[:, None, :]) * w[:, None, None]
        self.cell_torque, self.cell_drag = cell_torque, outer  # for _stress_cut
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
            target = p.mobility * self.heat() ** 0.5 * np.linalg.solve(Dk, tau)
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
        for arr in (self.age, self.thick, self.cont, self.rock, self.cover, self.extra):
            arr[keep, t] = arr[gone, r]
        ak, ag = (self.owner == keep).sum(), (self.owner == gone).sum()
        self.omega[keep] = (self.omega[keep] * ak + self.omega[gone] * ag) / max(ak + ag, 1)
        self.owned[gone] = False
        self.alive[gone] = False
        self.owner[self.owner == gone] = keep
        for arr in (self.contact, self.closing):
            arr[gone, :] = 0
            arr[:, gone] = 0

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
        # How fast each colliding pair is still closing (cm/yr, smoothed over
        # ~10 Myr). Collision goes on while they converge (India has pushed
        # into Asia for 50 Myr and counting); they only weld into one plate
        # once the collision has ground to a halt.
        csum = np.zeros((P_MAX, P_MAX))
        np.add.at(csum, (pairs[:, 0], pairs[:, 1]), bd["conv"][c])
        rate = np.where(cnt > 0, csum / np.maximum(cnt, 1), 0.0)
        w = 1 - np.exp(-self.dt / 10.0)
        self.closing = np.where(active, self.closing + w * (rate - self.closing), self.closing)
        stalled = (self.contact >= p.suture_after) & (self.closing < p.suture_closing)
        for i, j in zip(*np.nonzero(stalled | (self.contact >= p.suture_max))):
            if not (self.alive[i] and self.alive[j]) or self.t - self.rifted_at[i, j] < 80:
                continue
            sel = (pairs[:, 0] == i) & (pairs[:, 1] == j)
            where = g.centers[bd["a"][c][sel]].mean(0) if sel.any() else g.centers[self.owner == i].mean(0)
            ai, aj = (self.owner == i).sum(), (self.owner == j).sum()
            keep, gone = (i, j) if ai >= aj else (j, i)
            self._merge(keep, gone)
            self.closing[i, j] = 0
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

    def _stress_cut(self, k, rng, tries=6):
        """Plates are rigid only up to a point. Try a few straight cuts through
        plate k and, for each, solve how the two halves would move on their
        own (same force balance as _forces). Returns (centre, cut normal,
        opening speed in cm/yr) for the cut across which the halves most want
        to pull apart, e.g. a plate with slabs pulling on opposite sides."""
        p = self.params
        cells = np.flatnonzero(self.owner == k)
        P = self.grid.centers[cells]
        c = P.mean(0)
        c /= np.linalg.norm(c)
        t = rng.normal(size=(tries, 3))
        t -= (t @ c)[:, None] * c
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        side = ((P - c) @ t.T > 0).T.astype(float)  # (tries, cells)
        tq, D = self.cell_torque[cells], self.cell_drag[cells]
        motion = []
        for s_ in (side, 1 - side):
            Dh = np.einsum("tc,cij->tij", s_, D)
            area = np.trace(Dh, axis1=1, axis2=2) / 2
            tau = s_ @ tq + p.mantle_noise * 0.5 * area[:, None] * self.mantle[k]
            Dh = Dh + 0.1 * area[:, None, None] * np.eye(3)
            motion.append(p.mobility * self.heat() ** 0.5 * np.linalg.solve(Dh, tau[:, :, None])[:, :, 0])
        opening = np.einsum("tj,tj->t", np.cross(motion[0] - motion[1], c), t) * CMYR
        frac = side.mean(1)
        opening[(frac < 0.25) | (frac > 0.75)] = 0
        i = int(opening.argmax())
        return (c, t[i], float(opening[i])) if opening[i] > 0 else (c, None, 0.0)

    def _old_margins(self):
        """Per plate: mean age of the ocean floor along its passive margins
        (coastlines where continent and ocean ride on the same plate, like
        today's Atlantic coasts), and how many margin edges it has."""
        a, b = self.grid.edges[:, 0], self.grid.edges[:, 1]
        m = (self.owner[a] == self.owner[b]) & (self.w_cont[a] != self.w_cont[b])
        ocean = np.where(self.w_cont[a], b, a)[m]
        k = self.owner[a][m]
        cnt = np.bincount(k, minlength=P_MAX)
        age = np.bincount(k, self.w_age[ocean], P_MAX) / np.maximum(cnt, 1)
        return age, cnt

    def _maybe_rift(self, rng):
        """Three ways a plate splits, each a hazard rate (per Myr, in units of
        1/rift_timescale); at most one split per step.
          heat:   a big continent insulates the mantle under it and rifts
                  (Pangaea -> Atlantic).
          stress: a big plate whose halves are pulled different ways breaks
                  along the line where they'd separate fastest.
          margin: old ocean floor at a passive margin is cold and dense enough
                  to break off and start sinking under the continent: new
                  subduction (the closing half of the Wilson cycle)."""
        p, g = self.params, self.grid
        if self.alive.sum() >= min(p.max_plates, P_MAX):
            return
        P = g.centers
        cont_cells = np.bincount(self.owner, weights=self.w_cont, minlength=P_MAX)
        all_cells = np.bincount(self.owner, minlength=P_MAX)
        margin_age, margin_len = self._old_margins()
        threshold = p.rift_min_continent * g.n
        big = p.stress_min_plate * g.n
        for k in np.flatnonzero(self.alive):
            heat = cont_cells[k] / threshold if cont_cells[k] >= threshold else 0.0
            stress, cut, t_s = 0.0, None, None
            # (a freshly formed plate gets time to settle first, or splits cascade)
            if all_cells[k] >= big and self.t - self.formed[k] >= p.settle_time:
                c_s, t_s, opening = self._stress_cut(k, rng)
                if opening > p.rift_stress:
                    stress = (opening / p.rift_stress - 1) * all_cells[k] / big
                # Plates much bigger than the Pacific (~20% of Earth) are rare:
                # they span too many different mantle flow regimes to stay whole.
                stress += 2 * max(0.0, all_cells[k] / (p.big_plate * g.n) - 1)
                if stress > 0 and t_s is not None:
                    cut = (c_s, t_s)
            margin = 0.0
            ocean_cells = all_cells[k] - cont_cells[k]
            if (margin_len[k] >= 4 * self.scale and ocean_cells >= 0.5 * big
                    and cont_cells[k] >= 0.5 * big):
                margin = max(0.0, margin_age[k] / p.margin_age - 1) * 3
            rate = heat + stress + margin
            if rate == 0 or rng.random() > 1 - np.exp(-self.dt / p.rift_timescale * rate):
                continue
            refs = np.flatnonzero(self.owned[k])
            world = P[refs] @ self.Q[k].T
            u = rng.random() * rate
            if u < margin:
                # the ocean side of the largest stretch of ocean on this plate
                lab, _ = components(g, (self.owner == k) & ~self.w_cont)
                biggest = np.bincount(lab[lab >= 0]).argmax()
                at = g.locate(world)
                side = ~self.cont[k, refs] & (lab[at] == biggest)
                if self._split(k, refs, world, side, toward=True):
                    edge = (self.owner == k) & self.w_cont & (lab[g.nbr_idx[g.nbr_off[:-1]]] == biggest)
                    c = P[edge].mean(0) if edge.any() else world[side].mean(0)
                    self._log("subduction", [k, self.newest], c, "old ocean floor on plate {0} breaks off "
                              "its continental margin and starts to sink; it becomes plate {1}")
                    return
                continue
            if u < margin + stress:
                if cut is None:  # a huge plate with no clear stress direction
                    c = P[self.owner == k].mean(0)
                    c /= np.linalg.norm(c)
                    t = rng.normal(size=3)
                    t -= (t @ c) * c
                    t /= np.linalg.norm(t)
                else:
                    c, t = cut
                why = "is pulled apart by the forces on it"
            else:
                core = P[(self.owner == k) & self.w_cont]
                c = core.mean(0)
                c /= np.linalg.norm(c)
                t = rng.normal(size=3)
                t -= (t @ c) * c
                t /= np.linalg.norm(t)
                why = "rifts apart"
            side = self._rift_side(k, c, t, rng, world)
            if not 0.2 < side.mean() < 0.8:
                continue
            self._split(k, refs, world, side, toward=False)
            what = "continent on plate" if cont_cells[k] >= threshold else "plate"
            self._log("rift", [k, self.newest], c, what + " {0} " + why + "; the split-off part becomes plate {1}")
            return

    def _rift_side(self, k, c, t, rng, world):
        """Which of plate k's reference cells (at positions `world`) go to the
        new plate. The cut is a great circle through c with normal t, bent
        out of shape by warped multi-scale noise so it wanders like a real
        rift (East Africa, the Atlantic's zig-zag margins). Stray fragments
        it cuts off are handed back to whichever side surrounds them."""
        g = self.grid
        seeds = rng.integers(2**31, size=4)
        def cut(x):
            warp = np.stack([fbm(Perlin3D(int(sd)), x, octaves=3, freq=2.0) for sd in seeds[:3]], 1)
            y = x + 0.12 * warp
            return (y - c) @ t + 0.07 * fbm(Perlin3D(int(seeds[3])), y, octaves=4, freq=4.0)
        mine = np.flatnonzero(self.owner == k)
        v = np.full(g.n, np.nan)
        v[mine] = cut(g.centers[mine])
        on = self.owner == k
        wside = on & (v > 0)
        for m in (wside, on & ~wside):
            lab, nl = components(g, m)
            if nl > 1:
                sizes = np.bincount(lab[lab >= 0])
                stray = (lab >= 0) & (lab != sizes.argmax())
                wside = np.where(stray, ~wside & on, wside)
        cell = g.locate(world)
        here = self.owner[cell] == k
        return np.where(here, wside[cell], cut(world) > 0)

    def _split(self, k, refs, world, side, toward):
        """Move plate k's reference cells refs[side] to a new plate. The two
        parts get a nudge apart (a rift) or together (new subduction)."""
        if side.sum() < 4 or (~side).sum() < 4:
            return False
        new = int(np.flatnonzero(~self.alive)[0])
        self.newest = new
        self.label[new] = self.next_label
        self.next_label += 1
        for arr in (self.contact, self.closing, self.last_logged, self.rifted_at):
            fill = 0 if arr is self.contact or arr is self.closing else -1e9
            arr[new, :] = fill
            arr[:, new] = fill
        self.alive[new] = True
        self.formed[new] = self.formed[k] = self.t
        self.Q[new] = self.Q[k]
        self.idx[new] = self.idx[k]
        self.owned[new] = False
        r = refs[side]
        self.owned[new, r] = True
        self.owned[k, r] = False
        for arr in (self.age, self.thick, self.cont, self.rock, self.cover, self.extra):
            arr[new] = arr[k]
        axis = np.cross(world[~side].mean(0), world[side].mean(0))
        axis /= np.linalg.norm(axis)
        if toward:
            axis = -axis
        push = 2.5 / CMYR
        self.omega[new] = self.omega[k] + axis * push
        self.omega[k] = self.omega[k] - axis * push
        # the push lasts a while: seed the wandering term
        self.mantle[new] = self.mantle[k] + axis * 4.0
        self.mantle[k] = self.mantle[k] - axis * 4.0
        a_, b_ = min(k, new), max(k, new)
        self.rifted_at[a_, b_] = self.t
        self.last_logged[a_, b_] = self.t
        self.contact[a_, b_] = 0
        moved = np.isin(self.w_ref, r) & (self.owner == k)
        self.owner[moved] = new
        return True

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
            rock=self.w_rock.copy(),
            cover=self.w_cover.copy(),
            thickness=self.w_thick.copy(),
            precip=self.precip.copy() if self.precip is not None else np.zeros(self.grid.n),
            flow=self.flow.copy(),
            downstream=self.down.copy(),
            hotspots=[list(latlon(h["pos"])) for h in self.hotspots],
            volcanoes=[list(latlon(v["pos"])) for v in self.volcanoes],
            surface=surface.surface_rock(self.w_rock, self.w_cover, self.w_extra[:, CARB], self.w_extra[:, LAVA]),
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
