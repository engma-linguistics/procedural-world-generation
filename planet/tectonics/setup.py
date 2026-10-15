"""The starting planet: plates, continents and their ancient crust.

All of it comes from default_rng(seed) (plus default_rng([seed, 7]) for the
continental rock ages), drawn in a fixed order, so a seed always gives the
same start.
"""

from __future__ import annotations

import numpy as np

from .. import kernels
from ..noise import Perlin3D, fbm, ridged
from ..surface import CRATON, OCEAN, OROGEN, SHALE
from . import record
from .isostasy import BECOMES_CONT_KM, CONT_KM, ISO_LAND, OCEAN_KM, ocean_depth, sediment_lift
from .plates import CMYR


def initial_state(sim):
    """Fill sim.plates (and sim.owner) with the starting plates and crust."""
    g, p, pl = sim.grid, sim.params, sim.plates
    rng = np.random.default_rng(sim.seed)
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
    cont = field_ > np.quantile(field_, 1 - sim.target_fraction())
    if p.start == "supercontinent":
        # A supercontinent is one plate: hand it to whichever plate holds
        # most of it, so the story starts with rifting, not collisions.
        k0 = np.bincount(plate[cont], minlength=p.n_plates).argmax()
        # Its plate also carries the ocean near its coast (passive margins,
        # like the Atlantic's today). Otherwise every bay belongs to some
        # other plate and the breakup tears the coast into fingers.
        near, _ = kernels.bfs_within(np.flatnonzero(cont), np.zeros(n, np.int64),
                                     g.nbr_off, g.nbr_idx, int(3 * sim.scale))
        plate = np.where(near >= 0, k0, plate)
        # oceanic leftovers cut off from their plate join a neighbour
        for k in range(p.n_plates):
            lab, nl = g.components(plate == k)
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
    inland = np.minimum(np.maximum(dist, 0) / sim.scale, 3)
    base = np.where(cont, -450 + 230 * inland + 300 * texture, 0)
    old_mtn = 900 * ridged(Perlin3D(int(rng.integers(2**31))), x, octaves=5, freq=2.5) * cont
    # Ocean floor ages as a steadily spreading ocean has them (patchy, as
    # smooth noise ranked): floor is made at a steady rate and subducted at
    # any age up to ~180 Myr, so the share of floor of age a falls off
    # linearly, p(a) ~ 1 - a/180, mean 60 Myr (Earth's ~64). An ocean
    # starting far from this would renew itself in the first ~100 Myr and
    # move the sea by hundreds of m (PW-053).
    nz_age = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=3, freq=1.0)
    q = (np.argsort(np.argsort(nz_age, kind="stable"), kind="stable") + 0.5) / n
    age = 180.0 * (1 - np.sqrt(q))
    elev = np.where(cont, base + old_mtn, ocean_depth(age))
    thick = np.where(cont, np.maximum(CONT_KM + (elev - 250) / ISO_LAND, BECOMES_CONT_KM + 1), OCEAN_KM)
    # What the planet's unsimulated early history leaves behind: ancient
    # cratons deep inside the continents, wrapped in old mountain belts,
    # partly under a blanket of flat-lying sediment.
    core = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=4, freq=2.0)
    craton = cont & (dist >= 2 * sim.scale) & (core > -0.05)
    rock = np.where(craton, CRATON, np.where(cont, OROGEN, OCEAN)).astype(np.uint8)
    blanket = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=4, freq=3.0)
    cover = np.where(cont, np.clip(1.5 * blanket + 0.6, 0, 3) + np.where(inland < 1, 1.5, 0), 0)
    # (sediment is lighter than crust: the same ground needs less of it)
    thick = np.where(cont, np.maximum(thick - sediment_lift(cont, rock, cover) / ISO_LAND, BECOMES_CONT_KM + 1), thick)
    # Continental rock ages from the unsimulated past (own random stream,
    # so adding this didn't change the rest of the set-up): shields
    # 1.5-3.5 Gyr, the belts around them 0.3-1.4 Gyr.
    r2 = np.random.default_rng([sim.seed, 7])
    a_n = fbm(Perlin3D(int(r2.integers(2**31))), x, octaves=4, freq=2.5)
    age = np.where(cont, np.where(rock == CRATON, 2500 + 900 * a_n, 850 + 500 * a_n), age)
    age = np.where(cont, np.maximum(age, 300), age)
    for k in range(p.n_plates):
        m = plate == k
        pl.alive[k] = True
        pl.owned[k] = m
        pl.cont[k] = cont & m
        pl.thick[k] = np.where(m, thick, 0)
        pl.rock[k] = np.where(m, rock, 0)
        pl.cover[k] = np.where(m, cover, 0)
        pl.age[k] = np.where(m, age, 0)
        axis = rng.normal(size=3)
        axis /= np.linalg.norm(axis)
        pl.omega[k] = axis * rng.uniform(2, 6) / CMYR
        # the blanket is one flat-lying layer of mud (its history isn't simulated)
        record.reconcile(pl.rec[k], pl.lith[k], pl.cover[k], np.full(n, SHALE, np.uint8), 0.0)
    sim.owner = plate.astype(np.int64)
