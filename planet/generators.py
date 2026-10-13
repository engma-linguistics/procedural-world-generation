"""Three entirely different ways to make a planet's terrain.

Every generator has the signature

    gen(grid, rng, **params) -> (elevation_m: ndarray, extra_layers: dict)

and returns elevation in metres with 0 = sea level. Everything downstream
(climate, rivers, erosion, biomes) is shared, so you can compare the three
directly.
"""

from __future__ import annotations

from collections import deque

import numpy as np

from .grid import Grid
from .noise import Perlin3D, fbm, ridged


def to_sea_level(raw: np.ndarray, ocean_fraction: float, max_height: float = 6500,
                 max_depth: float = 6000) -> np.ndarray:
    """Shift and scale an arbitrary 'height-ish' field so the requested share of
    cells is under water, then map to metres. Land gets a curve that keeps
    most of it low (real continents are mostly lowland)."""
    sea = np.quantile(raw, ocean_fraction)
    s = raw - sea
    out = np.empty_like(s)
    land = s > 0
    if land.any():
        out[land] = max_height * (s[land] / s[land].max()) ** 1.5
    if (~land).any():
        out[~land] = -max_depth * (-s[~land] / -s[~land].min()) ** 0.6
    return out


def smooth(grid: Grid, values: np.ndarray, passes: int = 1, amount: float = 0.5) -> np.ndarray:
    a, b = grid.edges[:, 0], grid.edges[:, 1]
    deg = np.bincount(np.concatenate([a, b]), minlength=grid.n)
    for _ in range(passes):
        s = np.bincount(a, values[b], grid.n) + np.bincount(b, values[a], grid.n)
        values = (1 - amount) * values + amount * s / deg
    return values


# ---------------------------------------------------------------------------
# 1. NOISE: "sculpt with static"
# ---------------------------------------------------------------------------
def gen_noise(grid: Grid, rng: np.random.Generator, ocean_fraction: float = 0.65,
              continent_scale: float = 1.2, warp: float = 0.4,
              mountain_amount: float = 0.35) -> tuple[np.ndarray, dict]:
    """Fractal noise sampled on the sphere. The most common technique: fast,
    pretty, and has no idea what a mountain range *is*. Mountains end up
    as random speckle rather than long chains, which is its tell.

    - continent_scale: lower = fewer, bigger continents.
    - warp: domain warping. Feed noise into the coordinates of other noise
      to get swirly, less blobby coastlines.
    - mountain_amount: weight of a 'ridged' noise layer on land.
    """
    seed = int(rng.integers(2**31))
    n1, n2, n3 = Perlin3D(seed), Perlin3D(seed + 1), Perlin3D(seed + 2)
    p = grid.centers
    if warp:
        q = np.stack([fbm(n2, p + o, octaves=3, freq=1.0) for o in (0.0, 5.2, 9.7)], axis=1)
        p = p + warp * q
    base = fbm(n1, p, octaves=7, freq=continent_scale)
    mask = np.clip(base * 4 + 0.2, 0, 1)  # mountains only where it's already fairly high
    mountains = ridged(n3, p, octaves=5, freq=2.5) * mask
    raw = base + mountain_amount * mountains
    return to_sea_level(raw, ocean_fraction), {}


# ---------------------------------------------------------------------------
# 2. FAULTS: "slice the planet a thousand times"
# ---------------------------------------------------------------------------
def gen_faults(grid: Grid, rng: np.random.Generator, ocean_fraction: float = 0.65,
               n_faults: int = 1200, offset: float = 0.5,
               sharpness: float = 1.0) -> tuple[np.ndarray, dict]:
    """A classic from the 1990s demoscene (Hugo Elias / 'spherical landscapes').
    Repeatedly cut the planet with a random plane; nudge everything on one
    side up and everything on the other side down. After ~1000 cuts you get
    surprisingly Earth-like fractal coastlines from an absurdly simple rule.

    - n_faults: number of cuts.
    - offset: how far from the planet's centre cut planes may sit. At 0
      every cut goes through the centre and the planet comes out
      'antisymmetric': the opposite side of every continent is an ocean.
    - sharpness: higher = crisper cliffs at each cut.
    """
    p = grid.centers
    width = grid.spacing / max(sharpness, 1e-3)
    h = np.zeros(grid.n)
    for start in range(0, n_faults, 250):
        k = min(250, n_faults - start)
        normals = rng.normal(size=(k, 3))
        normals /= np.linalg.norm(normals, axis=1, keepdims=True)
        d = rng.uniform(-offset, offset, size=k)
        h += np.tanh((p @ normals.T - d) / width).sum(axis=1)
    h = smooth(grid, h, passes=2, amount=0.4)
    return to_sea_level(h, ocean_fraction), {}


# ---------------------------------------------------------------------------
# 3. PLATES: "fake geology"
# ---------------------------------------------------------------------------
def _grow_plates(grid: Grid, rng: np.random.Generator, n_plates: int) -> np.ndarray:
    """Random flood fill from seed cells. Each plate gets a random growth rate
    so we get a mix of big and small plates, like Earth's."""
    plate = np.full(grid.n, -1)
    seeds = rng.choice(grid.n, n_plates, replace=False)
    rates = rng.uniform(0.3, 1.0, n_plates) ** 2
    frontier: list[list[int]] = [[] for _ in range(n_plates)]
    for k, s in enumerate(seeds):
        plate[s] = k
        frontier[k].append(s)
    remaining = grid.n - n_plates
    while remaining:
        live = [k for k in range(n_plates) if frontier[k]]
        w = rates[live] / rates[live].sum()
        k = live[rng.choice(len(live), p=w)]
        f = frontier[k]
        idx = rng.integers(len(f))
        cell = f[idx]
        free = [nb for nb in grid.neighbors[cell] if plate[nb] < 0]
        if not free:
            f[idx] = f[-1]
            f.pop()
            continue
        nb = free[rng.integers(len(free))]
        plate[nb] = k
        f.append(nb)
        remaining -= 1
    return plate


def gen_plates(grid: Grid, rng: np.random.Generator, n_plates: int = 14,
               continental_fraction: float = 0.38, mountain_height: float = 4500,
               trench_depth: float = 3500, ridge_height: float = 1800,
               plate_speed: float = 1.0) -> tuple[np.ndarray, dict]:
    """A cartoon of plate tectonics, in the spirit of Andy Gainey's
    'Experilous' planet generator:

    1. Split the surface into plates by random flood fill.
    2. Mark each cell as continental (thick, light, floats high) or oceanic
       crust. Continental crust follows a noise field biased per plate, so
       continents can straddle plate boundaries like real ones do.
    3. Give each plate a random spin around a random axis (an 'Euler pole');
       that defines a velocity at every cell.
    4. At each boundary, compare the two sides' velocities:
       - colliding continents -> big mountain ranges (Himalayas)
       - ocean diving under continent -> trench + coastal range (Andes)
       - ocean meets ocean, colliding -> trench + island arc (Japan)
       - pulling apart under ocean -> mid-ocean ridge (Atlantic)
       - pulling apart under continent -> rift valley (East Africa)
    5. Spread each boundary feature inland with a falloff.

    Mountains therefore come in long chains along plate edges, unlike in
    the noise method. Ocean is whatever's left; there's no ocean_fraction.
    """
    seed = int(rng.integers(2**31))
    noise = Perlin3D(seed)
    p = grid.centers
    plate = _grow_plates(grid, rng, n_plates)

    # Crust type.
    bias = rng.uniform(-1, 1, n_plates)
    crust_field = fbm(noise, p, octaves=5, freq=1.3) + 0.25 * bias[plate]
    thr = np.quantile(crust_field, 1 - continental_fraction)
    continental = crust_field > thr
    # Smooth transition = continental shelf / slope.
    c = np.tanh((crust_field - thr) / 0.04)
    base = np.where(c > 0, 300 + 500 * c, -200 + 4000 * c)

    # Motion: angular velocity vector per plate, plus velocity at each cell.
    axes = rng.normal(size=(n_plates, 3))
    axes /= np.linalg.norm(axes, axis=1, keepdims=True)
    omega = axes * rng.uniform(0.3, 1.0, (n_plates, 1)) * plate_speed
    vel = np.cross(omega[plate], p)

    # Boundary interactions. For each cross-plate edge, compute pressure:
    # positive = the two cells approaching each other.
    a, b = grid.edges[:, 0], grid.edges[:, 1]
    cross = plate[a] != plate[b]
    a, b = a[cross], b[cross]
    d = p[b] - p[a]
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    pressure = ((vel[a] - vel[b]) * d).sum(1)  # >0 converging

    delta = np.zeros(grid.n)
    width = np.ones(grid.n)
    count = np.zeros(grid.n)
    press = np.zeros(grid.n)

    def apply(cell, other, pr):
        ci, co = continental[cell], continental[other]
        if pr > 0:  # convergent
            if ci and co:
                return mountain_height * pr * 1.3, 6.0
            if ci and not co:
                return mountain_height * pr, 3.5
            if not ci and co:
                return -trench_depth * pr, 1.2
            # ocean-ocean: the plate with the smaller index subducts (arbitrary)
            if plate[cell] < plate[other]:
                return -trench_depth * pr, 1.2
            return (4200 + mountain_height * 0.5) * pr, 1.8  # island arc
        pr = -pr  # divergent
        if ci:
            return -1500 * pr, 2.5  # rift valley
        return ridge_height * pr, 3.0

    for i, j, pr in zip(a, b, pressure):
        for cell, other, sgn in ((i, j, 1), (j, i, 1)):
            dv, w = apply(cell, other, sgn * pr)
            delta[cell] += dv
            width[cell] = max(width[cell], w) if count[cell] else w
            count[cell] += 1
            press[cell] += pr
    boundary = count > 0
    delta[boundary] /= count[boundary]

    # Spread inward from the nearest boundary cell (BFS within the plate).
    dist = np.full(grid.n, np.inf)
    src = np.full(grid.n, -1)
    q = deque()
    for i in np.flatnonzero(boundary):
        dist[i], src[i] = 0, i
        q.append(i)
    while q:
        i = q.popleft()
        for j in grid.neighbors[i]:
            if plate[j] == plate[i] and dist[j] == np.inf:
                dist[j], src[j] = dist[i] + 1, src[i]
                q.append(j)
    scale = 2 ** (grid.level - 5)  # widths are tuned for level 5
    has = src >= 0
    falloff = np.zeros(grid.n)
    falloff[has] = np.exp(-((dist[has] / (width[src[has]] * scale)) ** 2))
    tectonic = np.where(has, delta[np.maximum(src, 0)] * falloff, 0)

    # Roughness: ridged noise makes boundary ranges look like ranges, not ramps.
    rough = ridged(Perlin3D(seed + 1), p, octaves=5, freq=3.0)
    h = base + tectonic * (0.6 + 0.8 * rough) + 350 * fbm(Perlin3D(seed + 2), p, octaves=6, freq=4.0)
    h = smooth(grid, h, passes=1, amount=0.3)
    h = np.clip(h, -10500, 8800)

    speed = np.linalg.norm(vel, axis=1)
    extra = {
        "plate": plate,
        "crust": continental.astype(int),
        # +1 converging boundary, -1 diverging, 0 interior / sliding past
        "plate_boundary": np.where(boundary & (np.abs(press / np.maximum(count, 1)) > 0.15),
                                   np.sign(press), 0).astype(int),
        "plate_speed": speed,
        "_plate_velocity": vel,  # underscore = used by the viewer, not summarised
    }
    return h, extra


GENERATORS = {"noise": gen_noise, "faults": gen_faults, "plates": gen_plates}
