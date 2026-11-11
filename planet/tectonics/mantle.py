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
from numba import njit, prange

from ..geo import R_KM
from .isostasy import BECOMES_CONT_KM

LMAX = 8  # highest spherical-harmonic degree kept (wavelength ~4500 km)
EDDY_DEGREES = (3, 8)  # the unresolved smaller convection (mantle_eddies)
_BASIS: dict[int, tuple[np.ndarray, np.ndarray]] = {}


def basis(grid) -> tuple[np.ndarray, np.ndarray]:
    """Real spherical harmonics of degree 1..LMAX on the grid's cells,
    orthonormal on the cells (Y.T @ Y = I; cells are near-equal area), and
    the degree of each column (_build_basis). Kept per process, and on disk
    next to numba's cache (planet/tectonics/__pycache__, per checkout): the
    orthonormalisation takes ~1 s at L7, which every run, slice or worker
    process would pay at start (PW-258). The build is deterministic (PW-693),
    so every checkout's file holds the same bits. The file's name hashes the
    grid's cells, LMAX, numpy's version and the build's code, so a
    change to any of them builds a new one; reading it back gives the same
    bits as building it."""
    if grid.n in _BASIS:
        return _BASIS[grid.n]
    path = _cache_path(grid)
    deg = np.repeat(np.arange(1, LMAX + 1), 2 * np.arange(1, LMAX + 1) + 1)
    try:
        Y = np.load(path)
        if Y.shape != (grid.n, len(deg)) or Y.dtype != np.float64:
            raise ValueError("stale")
    except (OSError, ValueError):
        Y, deg = _build_basis(grid)
        _save(path, Y)
    _BASIS[grid.n] = (Y, deg)
    return Y, deg


def _cache_path(grid):
    import hashlib
    import inspect
    from pathlib import Path
    h = hashlib.sha1(np.ascontiguousarray(grid.centers).tobytes())
    h.update(f"{LMAX} {np.__version__}".encode() + (inspect.getsource(_build_basis) + inspect.getsource(_orthonormalise.py_func)).encode())
    return Path(__file__).parent / "__pycache__" / f"mantle_basis_{grid.n}_{h.hexdigest()[:16]}.npy"


def _save(path, Y):
    """Written under a temporary name, then renamed (another process may be
    reading or writing it); a failure only costs the next process a rebuild."""
    import os
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "wb") as f:
            np.save(f, Y)
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)


def _build_basis(grid) -> tuple[np.ndarray, np.ndarray]:
    """The real spherical harmonics, by definition (PW-693): degree d,
    order m = 0, then cos and sin of m = 1..d, each N_dm P_d^m(z) x
    Re/Im((x + iy)^m) (no Condon-Shortley sign), from the Legendre
    recurrence in z and products of x, y only (no trig, no SVD: an SVD's
    columns are arbitrary within a degree, so the eddies on them depended on
    which LAPACK answer a process got). Then made exactly orthonormal on the
    cells (they are near-equal area) by modified Gram-Schmidt in this order,
    after the cells' mean (degree 0, left out: only differences matter), in
    a sequential compiled loop: the same bits under any thread count or load."""
    x, y, z = (np.ascontiguousarray(c, dtype=np.float64) for c in grid.centers.T)
    cols, degs = [], []
    C, S = [np.ones_like(x)], [np.zeros_like(x)]  # Re, Im (x + iy)^m
    for m in range(1, LMAX + 1):
        C.append(x * C[-1] - y * S[-1])
        S.append(x * S[-1] + y * C[-2])
    Q = {}  # P_d^m(z) / sin^m(theta), a polynomial in z
    for m in range(LMAX + 1):
        Q[m, m] = np.full_like(z, float(np.prod(np.arange(1, 2 * m, 2))))
        if m + 1 <= LMAX:
            Q[m + 1, m] = (2 * m + 1) * z * Q[m, m]
        for d in range(m + 2, LMAX + 1):
            Q[d, m] = ((2 * d - 1) * z * Q[d - 1, m] - (d + m - 1) * Q[d - 2, m]) / (d - m)
    for d in range(1, LMAX + 1):
        for m in range(d + 1):
            f = np.prod(np.arange(d - m + 1, d + m + 1, dtype=float))  # (d+m)!/(d-m)!
            N = np.sqrt((2 * d + 1) * (1 if m == 0 else 2) / f / grid.n)
            cols.append(N * Q[d, m] * C[m])
            degs.append(d)
            if m:
                cols.append(N * Q[d, m] * S[m])
                degs.append(d)
    Yt = np.stack(cols)  # (columns, cells): each column contiguous
    _orthonormalise(Yt)
    return np.ascontiguousarray(Yt.T), np.array(degs)


@njit(cache=True)
def _orthonormalise(Y):
    """In place on Y (columns, cells): each column, in order, made orthogonal
    to the cells' mean and to the columns before it (twice, for round-off),
    then unit length. Plain sequential sums, so the result is fixed by the
    input's bits."""
    k, n = Y.shape
    c = 1.0 / np.sqrt(n)
    for j in range(k):
        v = Y[j]
        for _ in range(2):
            s = 0.0
            for i in range(n):
                s += v[i]
            s *= c
            for i in range(n):
                v[i] -= s * c
            for q in range(j):
                u = Y[q]
                s = 0.0
                for i in range(n):
                    s += u[i] * v[i]
                for i in range(n):
                    v[i] -= s * u[i]
        s = 0.0
        for i in range(n):
            s += v[i] * v[i]
        s = 1.0 / np.sqrt(s)
        for i in range(n):
            v[i] *= s


def smooth(sim, f: np.ndarray, scale_km: float) -> np.ndarray:
    """f low-passed: its degree 1..LMAX part, damped like a diffusion
    (heat kernel) that spreads a point over ~scale_km."""
    Y, deg = basis(sim.grid)
    s = scale_km / R_KM
    return Y @ ((Y.T @ f) * np.exp(-deg * (deg + 1) * s * s / 2))


def keel(sim) -> np.ndarray:
    """The continental crust the plate dynamics feel: the keel's extra drag (motion.forces, traction) and the lid
    that insulates the mantle (update). All of it (sim.w_cont), or with the shred gap on (params.shred_km, PW-1295)
    only crust at least BECOMES_CONT_KM thick: a 15-20 km thinned margin kept as continental crust has neither a
    thick lithospheric keel nor a continent's insulating lid (PW-1318; kept as full continent, it left the young
    planet ~17% fewer plates, pw1295-note.md section 5)."""
    if sim.params.shred_km > 0:
        return sim.w_cont & (sim.w_thick >= BECOMES_CONT_KM)
    return sim.w_cont


def init(sim):
    """The starting mantle: the starting continents have sat where they are
    for a while (a supercontinent start begins over warm mantle, so its
    story starts with rifting). The eddies start at a random state of
    their own (default_rng([seed, 11]), so the rest of the start is as it was)."""
    p = sim.params
    sim.mantle_lid = keel(sim).astype(float)
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
    a = np.exp(-sim.dt_now / sim.params.mantle_timescale)
    sim.mantle_eddies = sim.mantle_eddies * a + np.sqrt(1 - a * a) * rng.normal(size=len(deg)) * _eddy_scale(sim, deg)


def eddies(sim) -> np.ndarray:
    """The eddy field on the grid (same units as sim.mantle)."""
    Y, _ = basis(sim.grid)
    return Y @ sim.mantle_eddies


def update(sim, bd):
    """One step of the mantle field (in place on sim.mantle, sim.mantle_lid)."""
    p, dt, n = sim.params, sim.dt_now, sim.grid.n
    if p.mantle_memory <= 0:
        return
    # how long continent has covered each patch of mantle (~100 Myr memory)
    lid = keel(sim)
    sim.mantle_lid += (1 - np.exp(-dt / 100.0)) * (lid - sim.mantle_lid)
    warm = p.insulation * lid * sim.mantle_lid
    # slabs: per trench edge, convergence (cm/yr / 5) x slab age (/80 Myr),
    # per unit length (level-independent: x edge length / cell area; the mean cell's area, not each cell's: smooth's
    # basis weighs the cells equally, so a cell's total over the mean area puts the whole slab into the field, PW-1628)
    cold = np.zeros(n)
    conv = np.clip(bd.at_trenches(bd.conv), 0, 15) / 5.0
    age = np.clip(sim.w_age[bd.sinking] / 80.0, 0.3, 1.5)
    np.add.at(cold, bd.sinking, conv * age)
    cold *= p.slab_cold * sim.edge_len / sim.cell_area
    src = smooth(sim, warm - cold, p.mantle_scale_km)
    sim.mantle = sim.mantle * np.exp(-dt / p.mantle_memory) + src * dt


_GRAD = {}


def _grad_edges(g):
    """Per cell, the edges it is the a (or b) end of, in edge order (CSR): the order np.bincount adds them in."""
    hit = _GRAD.get(g.n)
    if hit is None or hit[0] is not g.edges:
        e = g.edges
        ea, eb = e[:, 0].astype(np.int64), e[:, 1].astype(np.int64)
        offs, ids = [], []
        for end in (ea, eb):
            ids.append(np.argsort(end, kind="stable").astype(np.int64))
            offs.append(np.concatenate([[0], np.cumsum(np.bincount(end, minlength=g.n))]).astype(np.int64))
        hit = _GRAD[g.n] = (e, ea, eb, offs[0], ids[0], offs[1], ids[1])
    return hit[1:]


@njit(cache=True, parallel=True)
def _gradient_k(f, P, ea, eb, off_a, id_a, off_b, id_b, out):
    """gradient per cell: each cell adds up its own edges (as a, then as b), in edge order, like the bincounts."""
    for c in prange(P.shape[0]):
        n0 = n1 = n2 = 0.0
        dd = 0.0
        for e in id_a[off_a[c]:off_a[c + 1]]:
            x = f[eb[e]] - f[ea[e]]
            d0, d1, d2 = P[eb[e], 0] - P[ea[e], 0], P[eb[e], 1] - P[ea[e], 1], P[eb[e], 2] - P[ea[e], 2]
            n0 += x * d0
            n1 += x * d1
            n2 += x * d2
            dd += (d0 * d0 + d1 * d1) + d2 * d2
        m0 = m1 = m2 = 0.0
        de = 0.0
        for e in id_b[off_b[c]:off_b[c + 1]]:
            x = f[eb[e]] - f[ea[e]]
            d0, d1, d2 = P[eb[e], 0] - P[ea[e], 0], P[eb[e], 1] - P[ea[e], 1], P[eb[e], 2] - P[ea[e], 2]
            m0 += x * d0
            m1 += x * d1
            m2 += x * d2
            de += (d0 * d0 + d1 * d1) + d2 * d2
        den = dd + de
        g0, g1, g2 = 2 * (n0 + m0) / den, 2 * (n1 + m1) / den, 2 * (n2 + m2) / den
        s = (g0 * P[c, 0] + g1 * P[c, 1]) + g2 * P[c, 2]
        out[c, 0] = g0 - s * P[c, 0]
        out[c, 1] = g1 - s * P[c, 1]
        out[c, 2] = g2 - s * P[c, 2]


def gradient(sim, f: np.ndarray) -> np.ndarray:
    """Tangent gradient of a smooth field on the grid (per radian), from
    differences to the neighbours (least squares, isotropic neighbours)."""
    g = sim.grid
    f = np.ascontiguousarray(f, dtype=np.float64)
    out = np.empty((g.n, 3))
    ea, eb, off_a, id_a, off_b, id_b = _grad_edges(g)
    _gradient_k(f, np.ascontiguousarray(g.centers, dtype=np.float64), ea, eb, off_a, id_a, off_b, id_b, out)
    return out


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
    w = sim.cell_sr * (1 + p.continental_keel * keel(sim))
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
