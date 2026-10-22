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
from .isostasy import BECOMES_CONT_KM, CONT_KM, OCEAN_KM
from .plates import CMYR


# Myr: the oldest floor of the starting ocean (mean age a third of it, 54 Myr). Measured, not derived: sea
# level 0 is the floor's mean depth after the first step (earth.global_temperature), and it should be the
# model's own long-run ocean. Over 300-1000 Myr (after the warm-up; 10 L6 seeds, 2026-10-21, PW-549) that
# ocean's mean floor depth is -4962 m (mean age 62 Myr); this start reads -4968..-4977 m after its first
# 2 Myr step.
# Setup's plates can't give it: their speeds are random draws the force balance replaces within ~15 Myr, and
# their boundaries a random partition, not a ridge system. (PW-293 measured it over the first 500 Myr: 144,
# mean 48 Myr, -4853 m after one step. That window is mostly the starting supercontinent's breakup, when
# rifting is two to three times as frequent as later and the floor young, so the later ocean read
# -100..-350 m of sea; PW-549. Before PW-293: 180, mean 60, ranked over all cells.)
OCEAN_MAX_AGE = 162.0

# The continents start mature: with the relief and the sediment a run's continents have once it has settled, not a
# made-up low plain that the first collisions take 200-600 Myr to raise (the ice-free land then eroded at ~25% of
# its later rate, and the CO2 thermostat's kept balance read the rise as a lasting cooling: PW-576). Measured, not
# derived, like OCEAN_MAX_AGE: the run's own continents over 300-1000 Myr (snapshots at 300, 600 and 1000 Myr of
# 10 L6 seeds, 2026-10-22), where the distribution is already steady (sd 9.4-9.7 km at each time).
# Percentiles (MATURE_Q) of the continental crust's thickness about its mean, km: thin stretched margins and their
# sediment wedges below, old high belts and plateaus above (the top 10% stand ~1.7-7 km up; they are old crust
# inside the continents, 70-90% of it more than 5 cells from any converging boundary, which the slow wear of high
# old ground leaves standing).
MATURE_Q = np.array([0, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100], float)
MATURE_DTHICK = np.array([-34.8, -22.6, -20.9, -17.8, -14.0, -6.6, -2.0, 0.0, 1.0, 2.1, 3.4, 5.3, 9.7, 15.4, 22.9,
                          26.9, 49.1])
# ...and the median sediment cover, km, in each tenth of that thickness ranking (thinnest first): rivers carry the
# high ground's sediment to the low, so the margins' wedges are thick and the highest tenths mostly bare rock.
MATURE_COVER = np.array([16.8, 12.75, 7.91, 1.19, 0.44, 0.21, 0.14, 0.03, 0.0, 0.0])


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
    # Continents ride inside plates, as on Earth, so the story starts with
    # rifting and drifting, not collisions: each continent goes whole to
    # whichever plate holds most of it (a supercontinent is one plate), and
    # that plate also carries the ocean near its coast (passive margins, like
    # the Atlantic's today; otherwise every bay belongs to some other plate
    # and a breakup tears the coast into fingers). The scattered start used
    # to cut its continents along the random plates' boundaries (18-31% of
    # the boundary ran through continent, a big continent on up to 10
    # plates): collisions everywhere, slow plates, few ridges, and an ocean
    # that aged to 70-110 Myr and a sea 150-400 m low over 300 Myr (PW-328).
    if p.start == "supercontinent":
        lab = np.where(cont, 0, -1)
    else:
        lab, _ = g.components(cont)
    nl = int(lab.max()) + 1
    k_of = np.array([np.bincount(plate[lab == i], minlength=p.n_plates).argmax() for i in range(nl)], np.int64)
    near, src = kernels.bfs_within(np.flatnonzero(cont), np.zeros(n, np.int64),
                                   g.nbr_off, g.nbr_idx, int(3 * sim.scale))
    plate = np.where(near >= 0, k_of[lab[np.maximum(src, 0)]], plate)
    # oceanic leftovers cut off from their plate join a neighbour
    for k in range(p.n_plates):
        lab_k, nk = g.components(plate == k)
        if nk > 1:
            sizes = np.bincount(lab_k[lab_k >= 0])
            for piece in np.flatnonzero(sizes < sizes.max()):
                cells = np.flatnonzero(lab_k == piece)
                nb = np.concatenate([g.neighbors[i] for i in cells])
                others = plate[nb][plate[nb] != k]
                if len(others):
                    plate[cells] = np.bincount(others).argmax()
    # distance inland from the coast -> continental shelf / interior base level
    coast = np.flatnonzero(cont & np.array([not cont[g.neighbors[i]].all() for i in range(n)]))
    dist, _ = kernels.bfs_within(coast, cont.astype(np.int64), g.nbr_off, g.nbr_idx, int(4 * sim.scale))
    # (the search stops a few hundred km in; everything beyond is interior.
    # It used to stop at 50 cells, ~2700 km at level 7, and left the middle of
    # a level-7 supercontinent as unreached 'coast': shelf-low and craton-free,
    # so L7 continents started ~3 km thinner than L6's: PW-052)
    dist = np.where(cont & (dist < 0), 4 * sim.scale, dist)
    texture = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=6, freq=3.0)
    # shelf: coast cells sit underwater, interiors a few hundred metres up
    inland = np.minimum(np.maximum(dist, 0) / sim.scale, 3)
    base = np.where(cont, -450 + 230 * inland + 300 * texture, 0)
    old_mtn = 900 * ridged(Perlin3D(int(rng.integers(2**31))), x, octaves=5, freq=2.5) * cont
    # Ocean floor ages as a steadily spreading ocean has them (patchy, as
    # smooth noise ranked): floor is made at a steady rate and subducted at
    # any age up to OCEAN_MAX_AGE, so the share of floor of age a falls off
    # linearly, p(a) ~ 1 - a/OCEAN_MAX_AGE, mean OCEAN_MAX_AGE / 3. An ocean
    # starting far from this would renew itself in the first ~100 Myr and
    # move the sea by hundreds of m (PW-053). The starting floor is also sea
    # level 0 (earth.global_temperature), so it is the model's own steady
    # ocean (PW-293), and ranked over the ocean's cells only, so every seed
    # starts at the same mean depth (ranked over all cells, the continent
    # took a patchy share and the start's mean age ran 55-65 Myr by seed).
    nz_age = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=3, freq=1.0)
    sea = np.flatnonzero(~cont)
    q = (np.argsort(np.argsort(nz_age[sea], kind="stable"), kind="stable") + 0.5) / len(sea)
    age = np.zeros(n)
    age[sea] = OCEAN_MAX_AGE * (1 - np.sqrt(q))
    # The continents' pattern: low at the coast, a few hundred m up inland, old belts along the ridged noise. Its
    # ranking takes the long-run run's thickness distribution (MATURE_DTHICK): the coast's thin stretched margins,
    # the interiors' lowlands, the belts' highlands.
    pattern = base + old_mtn
    rank = np.zeros(n)
    cc = np.flatnonzero(cont)
    rank[cc] = (np.argsort(np.argsort(pattern[cc], kind="stable"), kind="stable") + 0.5) / len(cc)
    dthick = np.interp(100 * rank, MATURE_Q, MATURE_DTHICK)
    thick = np.where(cont, np.maximum(CONT_KM + dthick, BECOMES_CONT_KM + 1), OCEAN_KM)
    # What the planet's unsimulated early history leaves behind: ancient
    # cratons deep inside the continents, wrapped in old mountain belts,
    # partly under a blanket of flat-lying sediment: thick in the margins'
    # wedges and the lowlands' basins, patchy on the uplands, and gone from
    # most of the highest ground (MATURE_COVER, by the same ranking).
    core = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=4, freq=2.0)
    craton = cont & (dist >= 2 * sim.scale) & (core > -0.05)
    rock = np.where(craton, CRATON, np.where(cont, OROGEN, OCEAN)).astype(np.uint8)
    blanket = fbm(Perlin3D(int(rng.integers(2**31))), x, octaves=4, freq=3.0)
    level = np.interp(rank, (np.arange(10) + 0.5) / 10, MATURE_COVER)
    cover = np.where(cont, np.minimum(level * np.clip(1 + 3 * blanket, 0, 2), 0.8 * thick), 0)
    # (the thickness above is the whole column, cover included, as the run's measured one is; its sediment's
    # lightness, isostasy.sediment_lift, is part of the height it gives)
    # The continents start with the mean thickness the volume thermostat
    # holds (continental_thickness): the ranking above sets the pattern, a
    # uniform shift its mean. (The old made-up relief gave ~37 km, 6% more crust
    # than the target: the run spent its first ~250 Myr shedding it, and the
    # thermostat's integral term, wound up meanwhile, held arcs back long
    # after, so every run lost 8-13% of its crust volume: PW-046.)
    shift = thick[cont].mean() - p.continental_thickness
    thick = np.where(cont, np.maximum(thick - shift, BECOMES_CONT_KM + 1), thick)
    # Continental rock ages from the unsimulated past (own random stream,
    # so adding this didn't change the rest of the set-up): shields
    # 1.5-3.5 Gyr, the belts around them 0.3-1.4 Gyr.
    r2 = np.random.default_rng([sim.seed, 7])
    a_n = fbm(Perlin3D(int(r2.integers(2**31))), x, octaves=4, freq=2.5)
    age = np.where(cont, np.where(rock == CRATON, 2500 + 900 * a_n, 850 + 500 * a_n), age)
    age = np.where(cont, np.maximum(age, 300), age)
    for k in range(p.n_plates):
        m = plate == k
        pl.alive[k] = m.any()  # (a plate whose cells all went to a continent's plate is gone)
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
