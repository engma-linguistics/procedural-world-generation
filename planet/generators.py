"""Terrain generators. (The `noise` and `faults` generators lived here
until commit 503f101; see git history.)

Every generator has the signature

    gen(grid, rng, **params) -> (elevation_m: ndarray, extra_layers: dict)

and returns elevation in metres with 0 = sea level. Everything downstream
(climate, rivers, erosion, biomes) is shared.
"""

from __future__ import annotations

import numpy as np

from . import kernels
from .grid import Grid
from .noise import Perlin3D, fbm, ridged


def smooth(grid: Grid, values: np.ndarray, passes: int = 1, amount: float = 0.5) -> np.ndarray:
    a, b = grid.edges[:, 0], grid.edges[:, 1]
    deg = np.bincount(np.concatenate([a, b]), minlength=grid.n)
    for _ in range(passes):
        s = np.bincount(a, values[b], grid.n) + np.bincount(b, values[a], grid.n)
        values = (1 - amount) * values + amount * s / deg
    return values


# ---------------------------------------------------------------------------
# PLATES: "fake geology"
# ---------------------------------------------------------------------------
def _grow_plates(grid: Grid, rng: np.random.Generator, n_plates: int) -> np.ndarray:
    """Random flood fill from seed cells. Each plate gets a random growth rate
    so we get a mix of big and small plates, like Earth's."""
    seeds = rng.choice(grid.n, n_plates, replace=False)
    rates = rng.uniform(0.3, 1.0, n_plates) ** 2
    return kernels.grow_regions(int(rng.integers(2**31)), seeds.astype(np.int64), rates,
                                grid.nbr_off, grid.nbr_idx, grid.n)


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

    Mountains therefore come in long chains along plate edges rather than
    as random speckle. Ocean is whatever's left; there's no ocean_fraction.
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
    hops, src = kernels.bfs_within(np.flatnonzero(boundary), plate.astype(np.int64),
                                   grid.nbr_off, grid.nbr_idx, grid.n)
    dist = np.where(hops >= 0, hops, np.inf)
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


GENERATORS = {"plates": gen_plates}
