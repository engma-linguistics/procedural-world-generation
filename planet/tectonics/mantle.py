"""The mantle under the plates: a slowly evolving temperature anomaly that
remembers where slabs sank and where continents sat, and drags on the
plates' undersides.

sim.mantle (n,) is a temperature anomaly on the world grid (the mantle
frame: plates slide over it, like the hotspots), in relative units: about
-1 over a long-lived slab graveyard, +1 under a continent that has sat still
for a few hundred Myr (roughly +-100-200 K on Earth). Its global mean is 0.

Two sources build it:
  slabs       every trench sends cold, dense rock down: cold (-) in
              proportion to the convergence rate times the slab's age (old
              slabs are cold and thick). Over 100s of Myr long-lived
              subduction zones pile up "slab graveyards" (under the Americas
              and East Asia today; the ring around Pangaea before).
  insulation  continents are a lid on the mantle's heat: under them it warms
              (+), faster the longer the continent has stayed over the same
              mantle (sim.mantle_lid, a ~100 Myr running average of
              continental cover in the mantle frame), so a parked
              supercontinent heats its mantle (Pangaea over Africa's warm
              mantle) while drifting continents smear it out.
It only keeps the large scales: sources are smoothed over ~mantle_scale_km
(a low-pass in spherical harmonics, degree <= LMAX), and the field relaxes
over mantle_memory Myr.

The mantle flows from warm to cold, and drags the plates along: traction()
is a basal force down the temperature gradient, on every cell, in
proportion to how strongly its base is coupled to the mantle (the same
weights as motion.forces' drag: deep continental keels ~2.5x ocean). So
continents gather over cold downwellings (supercontinent assembly); a
continent that then insulates the mantle under it ends up over a warm
upwelling whose flow diverges under it, and the stress test in
events.maybe_rift (which includes this traction) pulls it apart.
New plumes rise preferentially from warm mantle, at the edges of the warm
regions most (volcanism.hotspots).
"""

from __future__ import annotations

import numpy as np

from ..geo import R_KM

LMAX = 8  # highest spherical-harmonic degree kept (wavelength ~4500 km)
EDDY_DEGREES = (3, 8)  # the unresolved smaller convection (mantle_eddies)
_BASIS: dict[int, tuple[np.ndarray, np.ndarray]] = {}


def basis(grid) -> tuple[np.ndarray, np.ndarray]:
    """Real spherical harmonics of degree 1..LMAX on the grid's cells,
    orthonormal on the cells (Y.T @ Y = I; cells are near-equal area), and
    the degree of each column. Built by orthonormalising monomials
    x^a y^b z^c degree by degree: on the sphere, the degree-d monomials
    minus everything of lower degree span exactly the degree-d harmonics.
    (Degree 0, the global mean, is left out: only differences matter.)"""
    if grid.n in _BASIS:
        return _BASIS[grid.n]
    x, y, z = grid.centers.T
    cols, degs = [np.full(grid.n, 1 / np.sqrt(grid.n))], [0]
    for d in range(1, LMAX + 1):
        B = np.stack([x**a * y**b * z ** (d - a - b) for a in range(d + 1) for b in range(d + 1 - a)], 1)
        Q = np.stack(cols, 1)
        for _ in range(2):
            B -= Q @ (Q.T @ B)
        U, S, _ = np.linalg.svd(B, full_matrices=False)
        cols.extend(U[:, : 2 * d + 1].T)
        degs.extend([d] * (2 * d + 1))
    Y = np.stack(cols[1:], 1)
    deg = np.array(degs[1:])
    _BASIS[grid.n] = (Y, deg)
    return Y, deg


def smooth(sim, f: np.ndarray, scale_km: float) -> np.ndarray:
    """f low-passed: its degree 1..LMAX part, damped like a diffusion
    (heat kernel) that spreads a point over ~scale_km."""
    Y, deg = basis(sim.grid)
    s = scale_km / R_KM
    return Y @ ((Y.T @ f) * np.exp(-deg * (deg + 1) * s * s / 2))


def init(sim):
    """The starting mantle: the starting continents have sat where they are
    for a while (a supercontinent start begins over warm mantle, so its
    story starts with rifting). The eddies start at a random state of
    their own (default_rng([seed, 11]), so the rest of the start is as it was)."""
    p = sim.params
    sim.mantle_lid = sim.w_cont.astype(float)
    sim.mantle = p.insulation * 60.0 * smooth(sim, sim.mantle_lid, p.mantle_scale_km)
    Y, deg = basis(sim.grid)
    sim.mantle_eddies = np.random.default_rng([sim.seed, 11]).normal(size=len(deg)) * _eddy_scale(sim, deg)


def _eddy_scale(sim, deg):
    """Per spherical-harmonic coefficient: the eddies' spread (degrees
    EDDY_DEGREES only), so that their field has an rms of mantle_eddies."""
    on = (deg >= EDDY_DEGREES[0]) & (deg <= EDDY_DEGREES[1])
    return on * sim.params.mantle_eddies * np.sqrt(sim.grid.n / on.sum())


def stir(sim, rng):
    """The mantle's smaller convection cells, which this model doesn't
    resolve: a random field (degrees EDDY_DEGREES, ~2000-6000 km across)
    that wanders over ~mantle_timescale Myr (an Ornstein-Uhlenbeck process
    on its coefficients; in place on sim.mantle_eddies). Its flow adds to
    the traction: different parts of a big plate get dragged different
    ways (why plates much bigger than the Pacific are rare), and it keeps
    continents meandering."""
    Y, deg = basis(sim.grid)
    a = np.exp(-sim.dt / sim.params.mantle_timescale)
    sim.mantle_eddies = sim.mantle_eddies * a + np.sqrt(1 - a * a) * rng.normal(size=len(deg)) * _eddy_scale(sim, deg)


def eddies(sim) -> np.ndarray:
    """The eddy field on the grid (same units as sim.mantle)."""
    Y, _ = basis(sim.grid)
    return Y @ sim.mantle_eddies


def update(sim, bd):
    """One step of the mantle field (in place on sim.mantle, sim.mantle_lid)."""
    p, dt, n = sim.params, sim.dt, sim.grid.n
    if p.mantle_memory <= 0:
        return
    # how long continent has covered each patch of mantle (~100 Myr memory)
    sim.mantle_lid += (1 - np.exp(-dt / 100.0)) * (sim.w_cont - sim.mantle_lid)
    warm = p.insulation * sim.w_cont * sim.mantle_lid
    # slabs: per trench edge, convergence (cm/yr / 5) x slab age (/80 Myr),
    # per unit length (level-independent: x edge length / cell area)
    cold = np.zeros(n)
    conv = np.clip(bd.at_trenches(bd.conv), 0, 15) / 5.0
    age = np.clip(sim.w_age[bd.sinking] / 80.0, 0.3, 1.5)
    np.add.at(cold, bd.sinking, conv * age)
    cold *= p.slab_cold * sim.edge_len / sim.cell_area
    src = smooth(sim, warm - cold, p.mantle_scale_km)
    sim.mantle = sim.mantle * np.exp(-dt / p.mantle_memory) + src * dt


def gradient(sim, f: np.ndarray) -> np.ndarray:
    """Tangent gradient of a smooth field on the grid (per radian), from
    differences to the neighbours (least squares, isotropic neighbours)."""
    g = sim.grid
    a, b = g.edges[:, 0], g.edges[:, 1]
    P = g.centers
    d = P[b] - P[a]
    df = (f[b] - f[a])[:, None] * d
    num = np.stack([np.bincount(a, df[:, j], g.n) + np.bincount(b, df[:, j], g.n) for j in range(3)], 1)
    dd = (d * d).sum(1)
    den = np.bincount(a, dd, g.n) + np.bincount(b, dd, g.n)
    grad = 2 * num / den[:, None]
    return grad - (grad * P).sum(1, keepdims=True) * P


def traction(sim) -> np.ndarray:
    """(n, 3) basal force on each cell from the mantle flowing under it
    (motion.forces' units): mantle_drag x the temperature gradient (down
    it: from warm toward cold), times the cell's coupling to the mantle (its
    area, more under continental keels: the same weights as motion.forces'
    drag matrix). So a plate with nothing else acting on it moves with the
    mantle under it, at about mobility x mantle_drag x |gradient| rad/Myr
    (~2-3 cm/yr over a strong anomaly). The flow includes the
    unresolved eddies (stir)."""
    p = sim.params
    if p.mantle_drag <= 0:
        return np.zeros((sim.grid.n, 3))
    w = sim.cell_area * (1 + p.continental_keel * sim.w_cont)
    return -p.mantle_drag * gradient(sim, sim.mantle + eddies(sim)) * w[:, None]


def plume_odds(sim) -> np.ndarray:
    """Relative odds that a new mantle plume rises under each cell: more
    over warm mantle, and most at the edges of the warm regions, where the
    mantle's temperature changes fastest (the 'plume generation zones'
    around the warm piles under Africa and the Pacific)."""
    m = sim.mantle
    gr = np.linalg.norm(gradient(sim, m), axis=1)
    edge = gr / max(float(gr.mean()), 1e-9)
    return np.exp(1.5 * np.clip(m, -1.0, 1.5)) * (1 + np.clip(m, 0, 1.0) * edge)
