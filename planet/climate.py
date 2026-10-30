"""Toy climate: temperature, prevailing wind, rainfall, then biomes.

Not a real climate model (no equations of motion are solved), but each
step is a simplified version of a real mechanism, so it works on any
planet's geography. In order (see compute):

- Temperature by latitude and height (-6.5 C per km), separately for land
  and sea; the seasons swing more with latitude and on land.
- Winds: the planet-wide belts (trade winds, westerlies, polar easterlies)
  plus the winds that land-sea temperature contrasts make (monsoons,
  subtropical highs, winter highs over cold continents).
- Ocean currents: the wind-driven gyres, solved as a streamfunction in
  each ocean basin (the Stommel model), plus the circumpolar and
  equatorial currents. They move heat around: fast warm currents up the
  east coasts of continents, slow cold drift down the west coasts, upwelling.
- Each place takes on the temperature of the air the wind brings it: mild
  sea air on west coasts in the westerlies, harsh land air inland.
- Rain: water vapour picked up over the sea (and evaporated from wet land)
  is carried by the wind. It rains where the air is forced up (mountains:
  wet windward slopes, dry rain shadows), where storms stir it (mid-
  latitudes), and in showers where the air near the ground is warm and
  moist enough to be unstable (tropics, summer continents). Warm air holds
  more water (~6% per C), so the tropics are wettest.
- Clouds (a diagnostic, after the rain): deep cloud where it rains hard,
  layer cloud along the storm tracks, low cloud over cold seas and
  stratocumulus decks where air sinks onto cool upwelling water, cumulus
  over summer land; clear skies under the sinking subtropical air. Sunshine
  hours follow from them and the day length.
- Koppen climate classes from the monthly-ish temperatures and rain.
- Where the rain goes (water_balance): back into the air (evaporation,
  limited by the sunshine and warmth to drive it, and by the rain there is)
  or into the rivers (runoff).
"""

from __future__ import annotations

import numpy as np

import numba
from numba import njit, prange

from . import kernels
from . import ocean as ocean_mod
from .geo import R_KM, is_land
from .grid import Grid

PCO2_REF = 350.0  # ppm: the CO2 of the climate model's dT = 0, Earth's climate as its data show it (~1960-2000,
# 320-370 ppm; the plants' "today", vegetation.CA_REF).
PCO2_BALANCE = 500.0  # ppm: the pCO2 a planet's carbon cycle rests at, its own balance of outgassing against
# weathering once its start has settled (tectonics/earth.py; the CO2 stock is ln X against it, X = 1 here). Not
# today's: Earth's present is the low end of its Phanerozoic range (~280-400 ppm in the Carboniferous-Permian and
# the late Cenozoic, ~1000+ through the Mesozoic and the early Paleozoic; Foster et al. 2017), and its long-run mean
# climate is several C warmer than today's (Scotese et al. 2021). 500 ppm, about the record's middle in log terms,
# is half a doubling above PCO2_REF (+1.5 C at co2_sensitivity 3; PW-559 B). With the balance at today's pCO2 the
# planets spent a median 45% of their time in an icehouse; with 500 ppm 19% (Earth ~10-30%); with 700 ppm 0%,
# i.e. most never glaciate (32 L6 seeds, docs/review/base-climate/v1-finish/).


RAIN_PER_C = 0.03  # global mean rain's growth per C of dT (compute's wet; ~2-3%/K in GCMs, Held & Soden 2006: the
# upper end), which the weathering sink's runoff factor also reads (tectonics/earth.py, WEATHER_RUNOFF)


def pco2(co2: float) -> float:
    """The CO2 stock co2 (ln X, X against the planet's balance PCO2_BALANCE) as a partial pressure, ppm: what
    plants and the temperature term both read (PW-646)."""
    return PCO2_BALANCE * float(np.exp(co2))

LAPSE = 6.5 / 1000  # degC per metre
FREEZE = -1.8  # C: sea water freezes


def temperature(grid: Grid, elev: np.ndarray, equator_temp: float, pole_temp: float) -> np.ndarray:
    """Annual mean temperature of land by latitude and height, for land the
    sea's air doesn't reach (compute brings the sea air in). The shape is a
    polynomial in sin^2(latitude), the classic shape of simple energy-
    balance climate models, fitted to Earth's land reduced to sea level:
    ~28 C in the tropics, ~15 C at 40 deg, ~0 C at 60 deg; the poles'
    -10 C is for low ground (ice sheets are high, hence much colder)."""
    x = np.sin(np.radians(grid.lat)) ** 2
    f = 0.156 * x + 2.012 * x**2 - 1.168 * x**3  # 0 at the equator, 1 at the poles
    t = equator_temp + (pole_temp - equator_temp) * f
    return t - LAPSE * np.maximum(elev, 0)


def sea_temperature(grid: Grid, equator_temp: float, pole_temp: float) -> np.ndarray:
    """The latitude's sea-surface temperature before currents move heat
    around (Earth: ~27 C at the equator, ~21 C at 30 deg, ~9 C at 50 deg).
    Cooler than land in the subtropics: a warm sea evaporates a lot, which
    cools it, and the ocean gyres carry heat poleward. Not clipped at
    freezing: below ~-1.8 C the sea freezes over (see compute)."""
    s = np.abs(np.sin(np.radians(grid.lat)))
    return equator_temp + (pole_temp - equator_temp) * s**2.3


def season_strength(grid: Grid, tilt: float = 23.4) -> np.ndarray:
    """How strongly the seasons swing at each latitude, 0..~1. The
    difference between summer and winter sunshine grows roughly like
    sin(latitude) (times the axial tilt). Near the equator the swing is
    damped further: there the Earth's spin barely deflects the winds, so
    the air spreads any heating sideways and temperatures stay even (and
    the summer there is the cloudy rainy season)."""
    a = np.abs(grid.lat)
    return np.sin(np.radians(a)) * np.clip(0.65 + a / 70.0, 0, 1) * (tilt / 23.4)


def seasons(grid: Grid, elev: np.ndarray, temp: np.ndarray, tilt: float = 23.4, land=None):
    """First guess of the warmest- and coldest-month temperatures (used for
    the winds; compute refines them). The swing grows with latitude and
    with distance from the sea, which evens temperatures out (Vancouver: 4
    to 18 C; Yakutsk, 62 N inland: -39 to +19). land: default elev > 0
    (compute's: geo.is_land). Returns (t_warm, t_cold)."""
    land = elev > 0 if land is None else land
    coast = np.flatnonzero(land & (np.add.reduceat(~land[grid.nbr_idx], grid.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(coast, land.astype(np.int64), grid.nbr_off, grid.nbr_idx, 10**6)
    dist = np.where(land, np.maximum(hops, 0) * grid.spacing * R_KM + 50.0, 0.0)
    dist = np.where(land & (hops < 0), 3000.0, dist)  # land with no coast at all
    continental = 1 - np.exp(-dist / 800.0)
    half_range = (4.0 + 24.0 * continental) * season_strength(grid, tilt)
    half_range += 0.3 * land  # even the tropics have a small swing on land
    return temp + half_range, temp - half_range


# --------------------------------------------------------------------------
# Grid helpers: smoothing, gradients, transport along a vector field
# --------------------------------------------------------------------------
_GEOM = {}
GEOM_KEEP = 8  # grids whose constants are kept (the main grid and the shared coarse grids: grid.shared_grid)


def _geom(grid: Grid):
    """Per-grid constants: local east/north unit vectors, directed edges and
    their tangent directions, cell spacing (km). Cached."""
    key = (id(grid), grid.n)
    G = _GEOM.pop(key, None)
    if G is not None:
        _GEOM[key] = G  # (most recently used last)
    else:
        p = grid.centers
        east = np.cross([0.0, 0.0, 1.0], p)
        east /= np.maximum(np.linalg.norm(east, axis=1, keepdims=True), 1e-9)
        north = np.cross(p, east)
        src = np.concatenate([grid.edges[:, 0], grid.edges[:, 1]])
        dst = np.concatenate([grid.edges[:, 1], grid.edges[:, 0]])
        d = p[dst] - p[src]
        d -= (d * p[src]).sum(1, keepdims=True) * p[src]
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        deg = np.bincount(src, minlength=grid.n).astype(np.float64)
        # Each cell's outgoing and incoming directed edges, in edge order: the
        # kernels gather along these in parallel and still add up in the same
        # order as a loop over the edges (so the results are bit-identical).
        out_e = np.argsort(src, kind="stable")
        in_e = np.argsort(dst, kind="stable")
        off = np.concatenate([[0], np.cumsum(np.bincount(src, minlength=grid.n))])
        in_off = np.concatenate([[0], np.cumsum(np.bincount(dst, minlength=grid.n))])
        # Least-squares gradient weights: the gradient g that best fits the
        # differences to the neighbours, len_e (d_e . g) = df_e, is
        # g = sum_e gq_e df_e with gq_e = M^-1 len_e d_e, M = sum_e len_e^2 d_e d_e^T
        # (+ the normal, to make it invertible). It uses each edge's own length:
        # the icosphere's cells are up to ~9% smaller or larger along the seams of
        # the icosahedron it was built from, and a gradient taken with the mean
        # spacing shows those seams as straight lines (in the winds, then the rain).
        ln = np.arccos(np.clip((p[src] * p[dst]).sum(1), -1.0, 1.0)) * R_KM
        c = ln[:, None] * d
        M = np.zeros((grid.n, 3, 3))
        np.add.at(M, src, c[:, :, None] * c[:, None, :])
        M += p[:, :, None] * p[:, None, :]
        gq = np.einsum("eij,ej->ei", np.linalg.inv(M)[src], c)
        # Blur weights (_smooth), per neighbour in grid.nbr_idx order: a
        # plain neighbour average drifts toward the side with more or nearer
        # neighbours and blurs less where the cells are smaller, which on
        # the icosphere leaves the icosahedron's seams in a blurred field's
        # gradient. So the weights are tilted until the neighbours' weighted
        # centre is the cell's own (a straight slope stays straight), and
        # the cell's mixing is scaled to spread the same km^2 everywhere.
        nsrc = np.repeat(np.arange(grid.n), np.diff(grid.nbr_off))
        r = p[grid.nbr_idx] - p[nsrc]
        r -= (r * p[nsrc]).sum(1, keepdims=True) * p[nsrc]
        r *= R_KM
        dg = np.diff(grid.nbr_off).astype(np.float64)
        rr = np.zeros((grid.n, 3, 3))
        np.add.at(rr, nsrc, r[:, :, None] * r[:, None, :] / dg[nsrc, None, None])
        rr += p[:, :, None] * p[:, None, :]  # (the normal: makes it invertible)
        rm = np.add.reduceat(r, grid.nbr_off[:-1], axis=0) / dg[:, None]
        b = -np.linalg.solve(rr, rm[:, :, None])[:, :, 0]
        wk = np.maximum(1.0 / dg[nsrc] + (b[nsrc] * r).sum(1) / dg[nsrc], 0.0)
        wk /= np.add.reduceat(wk, grid.nbr_off[:-1])[nsrc]
        spread = np.add.reduceat(wk * (r * r).sum(1), grid.nbr_off[:-1])
        h = grid.spacing * R_KM
        sk = wk * np.minimum(0.5 * h * h / spread, 0.9)[nsrc]
        if len(_GEOM) >= GEOM_KEEP:  # (the least recently used goes, never the grid in use)
            del _GEOM[next(iter(_GEOM))]
        _GEOM[key] = dict(east=east, north=north, src=src, dst=dst, d=d, deg=deg, h=grid.spacing * R_KM,
                          out_off=off, out_e=out_e, in_off=in_off, in_e=in_e, in_src=src[in_e], gq=gq, sk=sk)
    return _GEOM[key]


def _faces(grid: Grid) -> dict:
    """The cell faces, for the rain's finite-volume transport (PW-015):
    each grid edge (a, b) once (grid.edges' order), with its face (the
    great-circle arc between the two cell corners the cells share): length
    L (m) and unit normal n at its middle, pointing from a to b; the
    distance between the cells' centres lc (m); each cell's area A (m2);
    and each cell's faces (CSR: off, eid) with sign sg = +1 where the cell
    is the edge's a (a flux from a to b leaves it) and the cell beyond
    (nbr). Cached with _geom."""
    G = _geom(grid)
    if "faces" not in G:
        from .ocean import cell_area_km2
        n = grid.n
        ea, eb = grid.edges[:, 0].astype(np.int64), grid.edges[:, 1].astype(np.int64)
        # each icosphere triangle is a corner of its three cells, so an edge's two
        # corners are the two triangles it borders
        f = grid.faces.astype(np.int64)
        sides = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
        tri = np.tile(np.arange(len(f)), 3)
        key = sides.min(1) * n + sides.max(1)
        o = np.argsort(key, kind="stable")
        key, tri = key[o], tri[o]
        at = np.searchsorted(key, ea * n + eb)
        c1, c2 = grid.corners[tri[at]], grid.corners[tri[at + 1]]
        L = np.arccos(np.clip((c1 * c2).sum(1), -1, 1)) * R_KM * 1000.0
        mid = c1 + c2
        mid /= np.linalg.norm(mid, axis=1, keepdims=True)
        nrm = np.cross(c2 - c1, mid)
        nrm -= (nrm * mid).sum(1, keepdims=True) * mid
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
        p = grid.centers
        nrm *= np.where(((p[eb] - p[ea]) * nrm).sum(1) < 0, -1.0, 1.0)[:, None]
        lc = np.arccos(np.clip((p[ea] * p[eb]).sum(1), -1, 1)) * R_KM * 1000.0
        cells = np.concatenate([ea, eb])
        eid = np.tile(np.arange(len(ea), dtype=np.int64), 2)
        sg = np.concatenate([np.ones(len(ea)), -np.ones(len(ea))])
        o = np.argsort(cells, kind="stable")
        off = np.concatenate([[0], np.cumsum(np.bincount(cells, minlength=n))]).astype(np.int64)
        eid, sg = eid[o], sg[o]
        G["faces"] = dict(ea=ea, eb=eb, L=L, n=nrm, lc=lc, A=cell_area_km2(grid) * 1e6, off=off, eid=eid, sg=sg,
                          nbr=np.where(sg > 0, eb[eid], ea[eid]))
    return G["faces"]


_COARSE = {}
COARSE_R = 1.5  # coarse cells: reach of the interpolation weights (two rings of neighbours around the
# containing cell cover it: the nearest cell three steps away is further from any point of it)


def _coarse(grid: Grid, level: int = 3):
    """A coarser icosphere (level 3: ~900 km cells, for patterns thousands
    of km across): which coarse cell each fine cell falls in, the coarse
    neighbours, and weights to interpolate back smoothly: the nearby coarse
    cells, by a bell of distance, (1 - (d/r)^2)^2 out to r = COARSE_R coarse
    cells, which is smooth at its centre and at its edge (a cone, 1 - d/r,
    leaves kinks that the gradient of the field shows). Cached."""
    from .grid import shared_grid
    key = (id(grid), grid.n, level)
    if key not in _COARSE:
        cg = shared_grid(min(level, grid.level))
        cidx = cg.locate(grid.centers)
        # candidates: the containing coarse cell and two rings of neighbours around it
        off, idx = cg.nbr_off, cg.nbr_idx
        ring = np.full((cg.n, 19), -1, np.int64)
        for j in range(cg.n):
            near = {j}
            for a in idx[off[j]:off[j + 1]]:
                near.add(int(a))
                near.update(int(b) for b in idx[off[a]:off[a + 1]])
            ring[j, :len(near)] = sorted(near)
        cand = ring[cidx]
        ok = cand >= 0
        cand = np.where(ok, cand, cidx[:, None])
        d = np.arccos(np.clip((cg.centers[cand] * grid.centers[:, None, :]).sum(-1), -1, 1))
        w = np.where(ok, np.maximum(0.0, 1 - (d / (COARSE_R * cg.spacing)) ** 2) ** 2, 0.0)
        w /= w.sum(1, keepdims=True)
        # the inverse map, coarse cell -> the (fine cell, candidate) pairs that count towards it, in
        # ascending flat order (for _coarse_smooth's gather)
        inv = np.argsort(cand.ravel(), kind="stable")
        inv_off = np.concatenate([[0], np.cumsum(np.bincount(cand.ravel(), minlength=cg.n))])
        if len(_COARSE) > 8:
            _COARSE.clear()
        _COARSE[key] = dict(n=cg.n, cidx=cidx, off=cg.nbr_off, idx=cg.nbr_idx, cand=cand, w=w,
                            h=cg.spacing * R_KM, sk=_geom(cg)["sk"], inv=inv, inv_off=inv_off)
    return _COARSE[key]


BLUR_CELLS_PER_THREAD = 2500


def _coarse_smooth(f, cidx, nc, off, idx, sk, iters, cand, w, inv_off, inv):
    """Average f onto the coarse grid, blur it there (iters steps of
    _smooth, sk: the coarse grid's blur weights) and interpolate it back. Each fine cell counts towards all
    the coarse cells near it, by the interpolation weights (a nested grid's
    cells on a coarse cell's edge are as near to the next one).
    Every loop is a parallel gather: coarse cell j sums its fine cells'
    shares (inv[inv_off[j]:inv_off[j + 1]], flat indices i * K + k into
    cand / w, ascending) in the order a loop over the fine cells would add
    them, so the result is bit-identical to that loop at any thread count."""
    c = _coarse_down(f, nc, cand, w, inv_off, inv)
    # (the coarse grid is small: each blur step's parallel loop costs more to start on many threads
    # than it saves, ~40 us at 16 threads; one thread per ~2500 cells is about the fastest)
    nt = numba.get_num_threads()
    numba.set_num_threads(max(1, min(nt, nc // BLUR_CELLS_PER_THREAD)))
    try:
        c = _smooth(c, off, idx, sk, iters)
    finally:
        numba.set_num_threads(nt)
    return _coarse_up(c, cand, w)


@njit(cache=True, parallel=True)
def _coarse_down(f, nc, cand, w, inv_off, inv):
    K = cand.shape[1]
    c = np.empty(nc)
    for j in prange(nc):
        st, sc = 0.0, 0.0
        for r in range(inv_off[j], inv_off[j + 1]):
            i, k = inv[r] // K, inv[r] % K
            st += w[i, k] * f[i]
            sc += w[i, k]
        c[j] = st / max(sc, 1e-12)
    return c


@njit(cache=True, parallel=True)
def _coarse_up(c, cand, w):
    out = np.empty(cand.shape[0])
    for i in prange(cand.shape[0]):
        o = 0.0
        for k in range(cand.shape[1]):
            o += w[i, k] * c[cand[i, k]]
        out[i] = o
    return out


def smooth_big(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """Blur a field over thousands of km (smooth() does it on a coarse grid:
    cheap)."""
    return smooth(grid, f, km)


@njit(cache=True, parallel=True)
def _smooth(f, nbr_off, nbr_idx, sk, iters):
    """iters steps of f += sum over the neighbours of sk (f_nbr - f) (sk:
    _geom's blur weights)."""
    f = f.copy()
    g = np.empty_like(f)
    for _ in range(iters):
        for i in prange(f.shape[0]):
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += sk[e] * (f[nbr_idx[e]] - f[i])
            g[i] = f[i] + s
        f, g = g, f
    return f


COARSE_CELLS = 2.4  # a blur this many coarser cells wide or more is done on the coarser grid


def smooth(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """Blur a field over roughly `km` (Gaussian-ish sigma). A wide blur is
    done on the coarsest grid level it still spans COARSE_CELLS cells of
    (at level 6: ~580 km and up, a grid level coarser), which is ~10x
    cheaper and the same to within ~2% of the field's spread. Moving the
    field to that grid and back blurs it by about half a coarse cell's
    width already, so that much is taken off the blur there. The way back
    (interpolating from the coarse cells) leaves kinks along the coarse
    cells' edges: the field is right, but its gradient has a lattice of
    the coarse grid's spacing in it, which the winds (pressure gradients)
    and through them the rain used to show as diagonal streaks. So the
    last half coarse cell of the blur is done on the fine grid, which
    irons them out (the gradient is then within ~1.5% of a blur done all
    on the fine grid)."""
    h = _geom(grid)["h"]
    lev = grid.level
    while lev > 0 and km >= COARSE_CELLS * h * 2 ** (grid.level - lev + 1):
        lev -= 1
    f = np.ascontiguousarray(f, np.float64)
    if lev < grid.level:
        C = _coarse(grid, lev)
        fine = FINE_FINISH * C["h"]
        km_c = np.sqrt(max(km**2 - fine**2, 0.0))
        iters = int(round(4 * max(km_c**2 - 0.5 * C["h"] ** 2, 0.0) / C["h"] ** 2))
        f = _coarse_smooth(f, C["cidx"], C["n"], C["off"], C["idx"], C["sk"], iters, C["cand"], C["w"],
                           C["inv_off"], C["inv"])
        km = fine
    iters = int(round(4 * (km / h) ** 2))
    if iters <= 0:
        return f.copy()
    return _smooth(f, grid.nbr_off, grid.nbr_idx, _geom(grid)["sk"], iters)


FINE_FINISH = 0.5  # share of a coarse cell's width of a wide blur done on the fine grid (see smooth)


@njit(cache=True, parallel=True)
def _gradient(f, src, dst, gq, out_off, out_e):
    n = out_off.shape[0] - 1
    g = np.empty((n, 3))
    for i in prange(n):
        g0 = 0.0
        g1 = 0.0
        g2 = 0.0
        for k in range(out_off[i], out_off[i + 1]):
            e = out_e[k]
            df = f[dst[e]] - f[src[e]]
            g0 += gq[e, 0] * df
            g1 += gq[e, 1] * df
            g2 += gq[e, 2] * df
        g[i, 0] = g0
        g[i, 1] = g1
        g[i, 2] = g2
    return g


def gradient(grid: Grid, f: np.ndarray) -> np.ndarray:
    """Tangent gradient per cell, units of f per km (least squares over the
    neighbours; see _geom)."""
    G = _geom(grid)
    return _gradient(np.ascontiguousarray(f, np.float64), G["src"], G["dst"], G["gq"], G["out_off"], G["out_e"])


@njit(cache=True, parallel=True)
def _out_shares(v, d, out_off, out_e, allowed):
    n = out_off.shape[0] - 1
    w = np.empty(d.shape[0])
    tot = np.empty(n)
    for i in prange(n):
        t = 0.0
        for k in range(out_off[i], out_off[i + 1]):
            e = out_e[k]
            x = max(v[i, 0] * d[e, 0] + v[i, 1] * d[e, 1] + v[i, 2] * d[e, 2], 0.0)
            if allowed.shape[0] > 0:
                x = x * allowed[e]
            w[e] = x
            t += x
        tot[i] = t
        t = max(t, 1e-12)
        for k in range(out_off[i], out_off[i + 1]):
            w[out_e[k]] = w[out_e[k]] / t
    return w, tot


def _edge_weights(grid: Grid, v: np.ndarray, allowed: np.ndarray | None = None):
    """Share of each cell's outflow along each directed edge, for flow v.
    allowed: optional per-edge mask (e.g. sea-to-sea only for currents)."""
    G = _geom(grid)
    allowed = np.zeros(0) if allowed is None else np.ascontiguousarray(allowed, np.float64)
    w, tot = _out_shares(np.ascontiguousarray(v, np.float64), G["d"], G["out_off"], G["out_e"], allowed)
    return w, tot > 1e-12


@njit(cache=True, parallel=True)
def _relax_along(a, b, in_src, in_w, in_off, deg, nbr_off, nbr_idx, iters, diffusion):
    """Steady state of x = a + b * (upstream x): each cell sees the
    flow-weighted mean of the cells feeding it (its own value if none), mixed
    a little with its neighbours. Used to carry heat with ocean currents and
    air temperatures with the wind. in_off, in_src, in_w: each cell's
    incoming edges (CSR, in edge order), where they come from and their
    share of the source cell's outflow."""
    n = a.shape[0]
    x = a.copy()
    y = np.empty(n)
    den = np.empty(n)
    for i in prange(n):
        dw = 0.0
        for k in range(in_off[i], in_off[i + 1]):
            dw += in_w[k]
        den[i] = dw
    for _ in range(iters):
        for i in prange(n):
            num = 0.0
            for k in range(in_off[i], in_off[i + 1]):
                num += in_w[k] * x[in_src[k]]
            up = (num + 1e-3 * x[i]) / (den[i] + 1e-3)
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += x[nbr_idx[e]]
            up = (1 - diffusion) * up + diffusion * s / deg[i]
            y[i] = a[i] + b[i] * up
        x, y = y, x
    return x


def carry(grid: Grid, v: np.ndarray, a: np.ndarray, b: np.ndarray, km: float = 8000.0,
          diffusion: float = 0.1, allowed=None) -> np.ndarray:
    """Solve x = a + b * (upstream x) along flow v, far enough for signals
    to travel ~km."""
    G = _geom(grid)
    out_w, _ = _edge_weights(grid, v, allowed)
    iters = int(km / G["h"]) + 10
    return _relax_along(a.astype(np.float64), b.astype(np.float64), G["in_src"], out_w[G["in_e"]], G["in_off"],
                        G["deg"], grid.nbr_off, grid.nbr_idx, iters, diffusion)


def zonal_mean(grid: Grid, f: np.ndarray, mask: np.ndarray | None = None, width: float = 3.0,
               fold: bool = False):
    """Mean of f in latitude bands `width` deg wide, given back per cell,
    interpolated linearly in latitude between the bands' centres (a step at
    each band's edge left straight east-west lines in the sea temperatures,
    and the rain and clouds over the sea followed them). fold: the bands
    take in both hemispheres at the same distance from the equator."""
    nb = int(180 // width)
    lat = -np.abs(grid.lat) if fold else grid.lat
    bins = np.clip(((lat + 90) // width).astype(int), 0, nb - 1)
    m = np.ones(grid.n, bool) if mask is None else mask
    tot = np.bincount(bins[m], f[m], nb)
    cnt = np.bincount(bins[m], minlength=nb)
    allm = np.bincount(bins, f, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    zm = np.where(cnt > 0, tot / np.maximum(cnt, 1), allm)
    return np.interp(lat, -90 + width * (np.arange(nb) + 0.5), zm)


def _nbr_mean(grid: Grid, f: np.ndarray) -> np.ndarray:
    """Mean of f over each cell's neighbours."""
    return np.add.reduceat(f[grid.nbr_idx], grid.nbr_off[:-1]) / np.diff(grid.nbr_off)


# --------------------------------------------------------------------------
# Wind
# --------------------------------------------------------------------------
TRADE_ROUND = 3.0  # deg


def wind(grid: Grid, shift: float = 0.0, front: np.ndarray | None = None, belt=1.0) -> np.ndarray:
    """The planet-wide three-cell pattern, the same at every longitude
    (unless front moves it, below):
    easterly trade winds below ~30 deg, westerlies from 30 to 60, polar
    easterlies above. shift (deg) moves the bands north (northern summer):
    the tropical belts follow the sun fully, the westerlies only a third as
    much (they stay strong at 45-60 deg in winter, which is what brings the
    sea's mild air deep into Europe). front: deg added to each cell's
    latitude for the bands outside the tropics (front_shift: they sit where
    the air masses are, not at fixed latitudes). belt: the westerlies'
    strength, per cell or one number (westerly_belt: each season's and
    hemisphere's own, from its baroclinicity)."""
    G = _geom(grid)
    lat = _wind_lat(grid, shift, front)
    a = np.abs(lat)
    hemi = np.sign(lat)[:, None]
    # east component: trades strongest ~12 deg, calm 'horse latitudes' ~30,
    # westerlies strongest ~48, weak polar easterlies; poleward component:
    # toward the equator under the trades, poleward under the westerlies
    # (the trades' east component is rounded off within TRADE_ROUND deg of the
    # convergence, where |lat| has a corner: the speed had a one-cell dip there,
    # where the air lingered and rained more; PW-227)
    au = np.where(a < TRADE_ROUND, a * a / (2 * TRADE_ROUND) + TRADE_ROUND / 2, a)
    ue = (-0.9 * np.exp(-((au - 12) / 14) ** 2) + belt * np.exp(-((au - 48) / 15) ** 2)
          - 0.4 * np.exp(-((a - 78) / 10) ** 2))[:, None]
    un = (-0.3 * np.sin(np.radians(6 * np.minimum(a, 90))))[:, None]
    return ue * G["east"] + un * hemi * G["north"]


def _wind_lat(grid: Grid, shift: float, front: np.ndarray | None = None) -> np.ndarray:
    """wind()'s latitudes, its bands moved by shift and front (see there)."""
    lat = grid.lat - shift * (0.3 + 0.7 * np.exp(-(grid.lat / 25.0) ** 2))
    return lat if front is None else lat + front


FRONT_LAT = (30.0, 50.0)  # deg: the wind bands follow the air masses poleward of the subtropical highs (fully from
# the second)


def front_shift(grid: Grid, t_sl: np.ndarray, km: float = 900.0) -> np.ndarray:
    """How far (deg, added to the latitude) the mid- and high-latitude wind
    bands sit from their zonal place, for one season's sea-level air
    temperatures t_sl (C). The polar front, and with it the westerlies' storm
    belt and the polar easterlies beyond it, lies where the polar and the
    maritime air masses meet, not at a fixed latitude: so a cell takes the
    winds of the latitude whose zonal-mean air (smoothed over km, as the
    land-sea winds' contrast) is as warm as its own. Over a warm polar sea
    in winter (the Norwegian Sea, ~20 C above its latitude) the westerlies
    reach far north, the Icelandic low's south-westerlies onto Norway; over a
    cold continent the polar air reaches south. Tapered in over FRONT_LAT,
    so the trades and the subtropical highs keep their latitudes."""
    S = smooth(grid, t_sl, km)
    a = np.abs(grid.lat)
    out = np.zeros(grid.n)
    width = 3.0
    a_c = np.arange(0.5 * width, 90.0, width)
    for hm in (grid.lat >= 0, grid.lat < 0):
        b = np.clip((a[hm] // width).astype(int), 0, len(a_c) - 1)
        cnt = np.bincount(b, minlength=len(a_c))
        zm = np.bincount(b, S[hm], len(a_c)) / np.maximum(cnt, 1)
        ok = (cnt > 0) & (a_c >= 15.0)
        if ok.sum() < 2:
            continue
        # (the zonal mean made to fall poleward, strictly, so the latitude of a temperature is one)
        z = np.minimum.accumulate(zm[ok]) - 1e-6 * np.arange(ok.sum())
        a_eq = np.interp(-S[hm], -z, a_c[ok])
        w = np.clip((a[hm] - FRONT_LAT[0]) / (FRONT_LAT[1] - FRONT_LAT[0]), 0, 1)
        out[hm] = np.sign(grid.lat[hm]) * w * (a_eq - a[hm])
    return out


def polar_drift(grid: Grid, shift: float = 0.0, front: np.ndarray | None = None) -> np.ndarray:
    """The polar cell's equatorward part of wind() (poleward of 60 deg; up
    to 0.3 at 75): cold air draining off the pole in a shallow layer under
    the polar inversion (on Antarctica, the katabatic outflow). It carries
    the surface air's temperature but little of the column's water vapour,
    which sits above the inversion, in warmer air: the vapour reaches the
    polar coasts and ice sheets aloft, with the storms (the rain's wind
    leaves this drift out, PW-332)."""
    G = _geom(grid)
    lat = _wind_lat(grid, shift, front)
    a = np.abs(lat)
    un = np.where(a > 60.0, -0.3 * np.sin(np.radians(6 * np.minimum(a, 90))), 0.0)
    return (un * np.sign(lat))[:, None] * G["north"]


BELT_LAT = (30.0, 65.0)  # deg: the mid-latitudes whose baroclinicity drives the eddy-driven westerlies


def westerly_belt(grid: Grid, t_jul: np.ndarray, t_jan: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The westerlies' strength (wind()'s belt) in each half-year, per cell:
    each hemisphere's own in each season (PW-596). The surface westerlies
    are eddy-driven: the storms that grow on the mid-latitudes' poleward
    temperature contrast carry the jet's westerly momentum down to the
    ground, and the jet scales with that contrast (the thermal wind). So the
    belt follows each season's and hemisphere's zonal-mean contrast
    (storminess: the zonal mean jet_stream's thermal wind is built on),
    averaged over BELT_LAT, relative to the planet's own mean of the four
    (both seasons, both hemispheres). A planet without seasons keeps one
    belt, and the mean strength stays the one the winds are measured in
    (U_REF). On Earth the northern summer's belt is weak (the continents
    warm and the contrast falls by a third) and the south's strong all year
    round the cold Antarctic. t_jul / t_jan: the half-years' temperatures
    reduced to sea level, C."""
    a = np.abs(grid.lat)
    mid = (a >= BELT_LAT[0]) & (a <= BELT_LAT[1])
    north = grid.lat >= 0
    g = {}
    for k, t in (("jul", t_jul), ("jan", t_jan)):
        st = storminess(grid, t)
        g[k] = [float(st[mid & h].mean()) if (mid & h).any() else 0.0 for h in (north, ~north)]
    ref = float(np.mean(g["jul"] + g["jan"]))
    if ref <= 1e-9:
        return np.ones(grid.n), np.ones(grid.n)
    return tuple(np.where(north, g[k][0], g[k][1]) / ref for k in ("jul", "jan"))


def low_column(grid: Grid, land: np.ndarray, tune: dict) -> tuple[np.ndarray, np.ndarray]:
    """How much of the air column over each cell its ground's warmth or cold
    fills (0..1): what sets a thermal low's or high's pressure, which is
    hydrostatic, the column's mean temperature (PW-596). The boundary layer
    (sum_h) takes on any land's heat within a day; the air above it, up to
    the depth a continent's heat low reaches (fetch_h), only as far as the
    land within the synoptic scale (fetch_km) is land (as _summer_fetch). So
    a narrow land (Patagonia, Tasmania, New Zealand) or a continent's coast
    makes a shallow low, and a continent's interior a deep one. The sea's
    own column: 1. Returns (warm, cold): the column a warm land fills, and
    the one a cold land fills. Cold ground warms no air above it: its cold
    stays in the stable winter air mass under the inversion (air_m deep, as
    _winter_air has it), so a winter continent's high is a shallow dome,
    air_m / fetch_h of the warm column at most (PW-998: on Earth its full-
    depth outflow blew the Gulf's and the South China Sea's air offshore,
    where the subtropical highs' return flow blows weakly onshore)."""
    bl = tune["sum_h"] / tune["fetch_h"]
    cont = np.clip(smooth(grid, land.astype(float), tune["fetch_km"]), 0.0, 1.0)
    return (np.where(land, bl + (1 - bl) * cont, 1.0),
            np.where(land, min(tune["air_m"] / tune["fetch_h"], 1.0), 1.0))


def monsoon_wind(grid: Grid, t_sl: np.ndarray, shift: float, strength: float = 1.0, big: float = 0.0,
                 big_km: float = 2000.0, front: np.ndarray | None = None, belt=1.0,
                 column: tuple | None = None):
    """Zonal bands plus the winds made by land-sea temperature contrasts.
    Air over ground warmer than its latitude's average rises (low pressure),
    over cooler ground it sinks (high pressure). Away from the equator the
    Earth's spin turns the flow around the lows and highs (counter-clockwise
    around lows in the north): summer continents pull in moist sea air
    (monsoons) and the cooler oceans hold subtropical highs whose western
    sides send warm moist air up the east coasts (Florida, China) while
    their eastern sides blow dry along the west coasts (California, Chile).
    Winter continents push cold dry air out (Siberian high). Two scales: the
    contrast smoothed over ~900 km, plus (big) a continent-wide part over
    big_km, which reaches out over the neighbouring oceans (the summer heat
    of all of Asia pulls the monsoon across the Indian Ocean). t_sl:
    surface temperature reduced to sea level, C. front: the bands'
    displacement (wind(), front_shift); belt: the westerlies' strength
    (westerly_belt). column: how much of the air column the ground's
    warmth and cold fill (low_column's pair; default all of it): a land's
    lows and highs are as deep as its air's warmth or cold. Returns (wind, warmth):
    warmth is the smoothed temperature excess, C (>0: rising air)."""
    anom = t_sl - zonal_mean(grid, t_sl)
    if column is not None:
        anom = anom * np.where(anom >= 0, column[0], column[1])
    warmth = smooth(grid, anom, 900.0)
    if big > 0:
        warmth = warmth + big * smooth_big(grid, anom, big_km)
    P = -warmth  # warm -> low pressure
    g = gradient(grid, P) * 1000.0  # per 1000 km
    up = grid.centers
    geo = np.cross(up, g) * np.sign(grid.lat)[:, None]
    w = np.clip(np.abs(grid.lat) / 15.0, 0, 1)[:, None]
    v = w * (0.9 * geo - 0.45 * g) - (1 - w) * g
    v = strength * 0.3 * v
    # The land-sea circulation is shallow; it never fully overrides the big
    # wind belts, least of all in the strong mid- and high-latitude westerlies.
    m = np.linalg.norm(v, axis=1, keepdims=True)
    cap = 0.7 * strength * np.clip((65 - np.abs(grid.lat)) / 25, 0.3, 1)[:, None]
    v = v * np.minimum(1, cap / np.maximum(m, 1e-9))
    return wind(grid, shift, front, belt) + v, warmth


def speed(v):
    return np.linalg.norm(v, axis=1)


def deflect(grid: Grid, v: np.ndarray, surf: np.ndarray, tune: dict) -> np.ndarray:
    """Air flows round high ground rather than over it: a shallow layer of
    air near the ground can't climb kilometres (it would have to be
    pushed up against its own weight), so the part of the wind running up
    into high terrain (above ~block_m) is turned to run along the slope
    instead, keeping its speed (the westerlies part round Tibet; the
    trades are steered along the Andes). Partial where the ground is only
    a little above block_m (some air still crosses, and deeper winds carry
    over), full (block = 1) where it rises another block_m above it.
    surf: ground or ice height, m."""
    if tune["block"] <= 0:
        return v
    # how far the terrain ahead rises above block_m, felt a few hundred km out
    excess = smooth(grid, np.maximum(surf - tune["block_m"], 0.0), tune["block_km"])
    g = gradient(grid, excess)
    gn = np.linalg.norm(g, axis=1, keepdims=True)
    n = g / np.maximum(gn, 1e-12)
    b = tune["block"] * np.clip(excess / tune["block_m"], 0, 1)[:, None] * (gn > 1e-9)
    into = np.maximum((v * n).sum(1, keepdims=True), 0)
    w = v - b * into * n
    s0, s1 = speed(v)[:, None], np.maximum(speed(w), 1e-12)[:, None]
    return w * np.minimum(s0 / s1, 1.0 / np.maximum(1 - b, 0.3))


# --------------------------------------------------------------------------
# Ocean currents and sea-surface temperature
# --------------------------------------------------------------------------
def _csr_east(grid: Grid):
    """Eastward component of the unit direction from each cell to each of its
    neighbours, in the CSR order of grid.nbr_idx (for the numba kernels).
    Cached."""
    G = _geom(grid)
    if "csr_east" not in G:
        p = grid.centers
        src = np.repeat(np.arange(grid.n), np.diff(grid.nbr_off))
        d = p[grid.nbr_idx] - p[src]
        d -= (d * p[src]).sum(1, keepdims=True) * p[src]
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        G["csr_east"] = (d * G["east"][src]).sum(1)
    return G["csr_east"]


def curl(grid: Grid, v: np.ndarray) -> np.ndarray:
    """Vertical component of the curl of a tangent field, per km (>0:
    counter-clockwise seen from above). curl = -div(up x v); div from the
    flux through each cell's sides."""
    G = _geom(grid)
    w = np.cross(grid.centers, v)
    src, dst = G["src"], G["dst"]
    flux = ((w[dst] - w[src]) * G["d"]).sum(1)
    return -np.bincount(src, flux, grid.n) * 2.0 / (G["deg"] * G["h"])


@njit(cache=True)
def _stommel(F, beta, east_d, solve, order, nbr_off, nbr_idx, r, h, damp, iters, omega):
    """Gauss-Seidel / SOR relaxation of r lap(psi) + beta dpsi/dx = F on the
    cells where solve is set (psi stays 0 elsewhere: the coasts). The graph
    Laplacian is 4/(deg h^2) sum(psi_j - psi_i) and the eastward derivative
    2/(deg h) sum((d_ij . east_i)(psi_j - psi_i)), both exact for linear
    fields on a regular hexagonal grid. order: cells sorted east to west, so
    one sweep carries the interior (Sverdrup) balance across a whole ocean
    from its eastern shore. damp: a weak pull of psi toward 0 (keeps a sea
    with no coasts at all well-posed). Returns psi."""
    n = F.shape[0]
    # The coefficients don't change between sweeps: work them out once, and
    # store the cells in the order they're swept (it's faster to read them
    # in order). pos: each cell's place in that order (the cells that aren't
    # solved, whose psi stays 0, after them).
    pos = np.empty(n, np.int64)
    m = 0
    for k in range(order.shape[0]):
        if solve[order[k]]:
            pos[order[k]] = m
            m += 1
    rest = m
    for k in range(order.shape[0]):
        if not solve[order[k]]:
            pos[order[k]] = rest
            rest += 1
    off = np.zeros(m + 1, np.int64)
    for k in range(order.shape[0]):
        i = order[k]
        if solve[i]:
            off[pos[i] + 1] = nbr_off[i + 1] - nbr_off[i]
    for k in range(m):
        off[k + 1] += off[k]
    coef = np.empty(off[m])
    nb = np.empty(off[m], np.int64)
    den = np.empty(m)
    rhs = np.empty(m)
    for k in range(order.shape[0]):
        i = order[k]
        if not solve[i]:
            continue
        p = pos[i]
        deg = nbr_off[i + 1] - nbr_off[i]
        lap = 4.0 * r / (deg * h * h)
        adv = 2.0 * beta[i] / (deg * h)
        dc = 0.0
        for e in range(nbr_off[i], nbr_off[i + 1]):
            c = lap + adv * east_d[e]
            coef[off[p] + e - nbr_off[i]] = c
            nb[off[p] + e - nbr_off[i]] = pos[nbr_idx[e]]
            dc += c
        den[p] = dc + damp
        rhs[p] = F[i]
    x = np.zeros(n)
    for _ in range(iters):
        for p in range(m):
            num = 0.0
            for e in range(off[p], off[p + 1]):
                num += coef[e] * x[nb[e]]
            new = (num - rhs[p]) / den[p]
            x[p] += omega * (new - x[p])
    psi = np.empty(n)
    for i in range(n):
        psi[i] = x[pos[i]]
    return psi


def currents(grid: Grid, ocean: np.ndarray, wind_v: np.ndarray, tune: dict | None = None
             ) -> tuple[np.ndarray, np.ndarray]:
    """Surface ocean currents, from the wind (the Stommel model of the
    wind-driven gyres). The wind's twisting (the curl of its stress) pushes
    the water toward or away from the poles, and on a spinning planet the
    sea answers by flowing round closed gyres. Because the Coriolis effect
    grows toward the poles (beta), the return flow is squeezed into a
    narrow fast current on each ocean's western side: in the subtropical
    gyres warm water runs poleward up the east coasts of continents (Gulf
    Stream, Kuroshio, Brazil, Agulhas, East Australian currents) and drifts
    slowly back toward the equator across the rest of the ocean, coldest
    along the west coasts (California, Humboldt, Canary, Benguela); poleward
    of the westerlies the subpolar gyres turn the other way (cold Labrador
    and Oyashio currents; the North Atlantic drift reaching Norway).
    Solved as r lap(psi) + beta dpsi/dx = curl(wind) with psi = 0 on the
    coasts, for the whole ocean at once (with walls on every coast, that's
    each basin separately); the current is up x grad(psi). Islands smaller
    than ~150,000 km^2 (Iceland, Cuba) don't count as walls: the gyres are
    solved as if they were sea (their own island circulation is left out). Plus two flows the gyres don't capture:
    - a circumpolar current where some latitude is sea all the way round
      (no coast to close a gyre: the westerlies drive the water round the
      planet, the Antarctic Circumpolar Current);
    - the equatorial currents, pushed straight along by the trade winds
      where the Coriolis effect vanishes.
    Returns (current vectors, unit vectors pointing away from nearest land)."""
    tune = {**TUNE, **(tune or {})}
    G = _geom(grid)
    up = grid.centers
    h = G["h"]
    lat = grid.lat
    # The boundary layer (r/beta) has to span a couple of cells to be resolved.
    r = max(tune["gyre_km"], 0.8 * h)
    # Small islands are sea as far as the gyres are concerned, unless they
    # reach further north to south than the boundary current is wide (two
    # of its widths r/beta at the island's latitude): then the current runs
    # along the island's east coast instead of passing it (New Zealand,
    # Sakhalin, Luzon: the Pacific's gyre closes on New Zealand, and the
    # Tasman Sea between it and Australia has only its own; PW-594).
    land = ~ocean
    lab, nlab = _components(grid, land)
    nl = max(nlab, 1)
    k = np.maximum(lab, 0)
    sizes = np.bincount(lab[lab >= 0], minlength=nl) * (4 * np.pi * R_KM**2 / grid.n)
    lo = np.full(nl, 90.0)
    hi = np.full(nl, -90.0)
    np.minimum.at(lo, lab[lab >= 0], lat[lab >= 0])
    np.maximum.at(hi, lab[lab >= 0], lat[lab >= 0])
    span = np.radians(hi - lo) * R_KM + h
    width = 2 * r / np.maximum(np.cos(np.radians(0.5 * (lo + hi))), 0.1)
    wall = land & ((sizes[k] >= tune["island_km2"]) | (span[k] >= width[k]))
    sea = ~wall
    cosl = np.cos(np.radians(lat))
    tau = wind_v * np.abs(speed(wind_v))[:, None] ** (tune["tau_pow"] - 1)  # stress ~ |u|^p
    F = R_KM * smooth(grid, curl(grid, tau), 250.0) * sea
    order = np.argsort(-grid.lon, kind="stable")
    iters = int(tune["gyre_iters"] * 2 ** max(grid.level - 6, 0))  # finer grids: more cells across an ocean
    psi = _stommel(F, cosl, _csr_east(grid), sea, order, grid.nbr_off, grid.nbr_idx, r, h, r / 3000.0**2,
                   iters, 1.3)
    v = tune["gyre"] * np.cross(up, gradient(grid, psi))
    # circumpolar: latitude bands with no wall all the way round
    width = 2.0
    nb = int(180 // width)
    bins = np.clip(((lat + 90) // width).astype(int), 0, nb - 1)
    open_band = np.bincount(bins, wall, nb) == 0
    ue = (wind_v * G["east"]).sum(1)
    zm = np.bincount(bins, ue, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    ring = np.interp(lat, -90 + width * (np.arange(nb) + 0.5),
                     np.convolve(np.pad(open_band * zm, 3, mode="edge"), np.ones(7) / 7, mode="valid"))
    # equatorial currents: the trades' push where Coriolis vanishes
    eq = np.exp(-(lat / tune["eq_cur_lat"]) ** 2)
    push = tune["acc"] * ring + tune["eq_cur"] * eq * smooth(grid, np.where(ocean, ue, 0.0), 300.0)
    v = v + push[:, None] * G["east"]
    # nothing flows into a coast
    coast = np.flatnonzero(ocean & (np.add.reduceat(~ocean[grid.nbr_idx], grid.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(coast, ocean.astype(np.int64), grid.nbr_off, grid.nbr_idx, 8)
    dl = np.where(ocean, np.where(hops >= 0, hops + 1.0, 9.0), 0.0)
    away = gradient(grid, smooth(grid, dl, 150.0))
    away /= np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
    near = ocean & (hops >= 0) & (hops <= 2)
    into = np.minimum((v * away).sum(1, keepdims=True), 0)
    v = np.where(near[:, None], v - into * away, v)
    v -= (v * up).sum(1, keepdims=True) * up
    # the fastest real currents run ~2 m/s; a coastal jet a cell or two wide
    # can overshoot on a coarse grid
    s = np.maximum(speed(v), 1e-12)[:, None]
    v = v * 2.5 * np.tanh(s / 2.5) / s
    return np.where(ocean[:, None], v, 0.0), np.where(near[:, None], away, 0.0)


def _components(grid: Grid, mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Connected components of mask: label per cell (-1 outside), count."""
    return _label(mask, grid.nbr_off, grid.nbr_idx)


@njit(cache=True)
def _label(mask, nbr_off, nbr_idx):
    n = mask.shape[0]
    lab = np.full(n, -1, np.int64)
    q = np.empty(n, np.int64)
    k = 0
    for s in range(n):
        if not mask[s] or lab[s] >= 0:
            continue
        lab[s] = k
        q[0] = s
        head, tail = 0, 1
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


def upwelling_cooling(grid: Grid, ocean: np.ndarray, wind_v: np.ndarray, away: np.ndarray,
                      upwelling: float = 5.0, eq_upwelling: float = 0.0) -> np.ndarray:
    """C by which upwelling cools the sea surface before the currents carry
    it (sea_surface's source term; also a world layer, coastal.py's
    nutrient supply): coastal upwelling where the wind's Ekman transport
    pushes the surface water away from a coast (away: unit vectors pointing
    away from the nearest land, currents()), between ~5 and ~45 deg, and,
    with eq_upwelling, equatorial upwelling under easterlies."""
    G = _geom(grid)
    # Ekman transport: 90 deg to the right of the wind in the north, left in the south
    ek = np.cross(wind_v, grid.centers) * np.sign(grid.lat)[:, None]
    off = np.clip((ek * away).sum(1), 0, 1.5)
    lat_ok = np.clip((np.abs(grid.lat) - 5) / 8, 0, 1) * np.clip((45 - np.abs(grid.lat)) / 8, 0, 1)
    cold = upwelling * off * lat_ok
    if eq_upwelling > 0:
        # Equatorial upwelling: easterlies on the equator push the surface
        # water apart (Ekman, to the right in the north and left in the
        # south), and cold water wells up - but only where the warm layer is
        # thin, near the ocean's eastern shore (the trades pile warm water up
        # in the west): the cold tongues off Ecuador and in the Gulf of Guinea.
        land_big = smooth_big(grid, (~ocean).astype(float), 1500.0)
        thin = np.clip((gradient(grid, land_big) * G["east"]).sum(1) * 3000.0, 0, 1)  # land to the east
        u_e = (wind_v * G["east"]).sum(1)
        cold = cold + eq_upwelling * np.clip(-u_e, 0, 1) * np.exp(-(grid.lat / 6.0) ** 2) * thin
    return cold


def sea_surface(grid: Grid, ocean: np.ndarray, t_eq: np.ndarray, wind_v: np.ndarray,
                relax_km: float = 2500.0, upwelling: float = 5.0,
                eq_upwelling: float = 0.0, tune: dict | None = None, cur=None, away=None,
                share=None, t_in=None, base=None, chill=None) -> tuple[np.ndarray, np.ndarray]:
    """Sea-surface temperature: the latitude's temperature t_eq, moved by the
    currents (warm water poleward along the western side of each ocean, cold
    water toward the equator along the eastern side), plus coastal upwelling
    where the wind pushes surface water away from a coast (Peru, California,
    Namibia) and equatorial upwelling (eq_upwelling, C). Each band's average
    is kept. cur, away: the currents (as climate.currents returns them) if
    already known; share, t_in, base: where the overturning's inflow makes
    up a share of the surface water, its temperature (see ocean.py), and
    this function's sst without it: then the inflow's warmth is added to
    base. chill: C the air off land takes from the water over the year
    beyond what it gives back (compute's, from _sea_half), a cooling at the
    surface like upwelling's. Returns (sst, current)."""
    G = _geom(grid)
    tune = {**TUNE, **(tune or {})}
    if cur is None:
        cur, away = currents(grid, ocean, wind_v, tune)
    src = G["src"]
    allowed = (ocean[src] & ocean[G["dst"]]).astype(np.float64)
    # The water gives its heat up to the air over a set time, so a fast
    # current carries its warmth (or cold) far before it fades: relax_km at
    # the reference speed cur_ref (the Gulf Stream reaches Norway, the slow
    # drift across an ocean's middle soon takes on the latitude's temperature).
    reach = relax_km * np.clip(speed(cur) / tune["cur_ref"], tune["cur_min"], tune["cur_max"])
    keep = np.exp(-G["h"] / reach)
    b = np.where(ocean, keep, 0.0)
    km = 1.5 * tune["cur_max"] * relax_km
    if share is not None:
        # Where the overturning's inflow makes up a share of the surface
        # water, the water relaxes toward its temperature instead: carried
        # by the same currents, that adds (the carrying is linear) to base.
        # The overturning moves heat rather than making it (PW-265): the
        # mean change over each latitude's sea, in both hemispheres
        # together, is taken off (moc_zonal = 1). t_eq is the same in both
        # hemispheres, so it can hold only the overturning's average over
        # the two; what one hemisphere's overturning carries beyond the
        # other's is its own, and comes out of the other hemisphere's sea
        # (the north's sinking draws its warm water across the equator).
        # Taken off each band alone, it cooled the coasts off the inflow's
        # path (Alaska, the Baltic) and left the south as warm as the north
        # (PW-589).
        d = np.where(ocean, (1 - keep) * share * (t_in - t_eq), 0.0)
        e = np.where(ocean, carry(grid, cur, d, b, km=km, diffusion=0.15, allowed=allowed), 0.0)
        return base + e - tune["moc_zonal"] * np.where(ocean, zonal_mean(grid, e, ocean, fold=True), 0.0), cur
    cold = upwelling_cooling(grid, ocean, wind_v, away, upwelling, eq_upwelling)
    if chill is not None:
        cold = cold + chill
    a = np.where(ocean, (1 - keep) * (t_eq - cold), t_eq)
    sst = carry(grid, cur, a, b, km=km, diffusion=0.15, allowed=allowed)
    anom = np.where(ocean, sst - t_eq, 0.0)
    anom -= np.where(ocean, zonal_mean(grid, anom, ocean), 0.0)
    return t_eq + anom, cur


# --------------------------------------------------------------------------
# Rain
# --------------------------------------------------------------------------
def _qsat(t, k):
    """Water the air can hold at t C, relative to 0 C (~3.8 g/kg); k: per C
    (Clausius-Clapeyron ~0.07)."""
    return np.exp(k * t)


def humidity(q: np.ndarray, t_air: np.ndarray, tune: dict) -> tuple[np.ndarray, np.ndarray]:
    """Dew point (C) and relative humidity (%) of the air near the ground,
    holding q water vapour (_rain's, in _qsat units) at t_air C, by the
    model's own Clausius-Clapeyron rate q_k (a little gentler than the real
    ~0.07/C). A half-year's mean air is never quite saturated: the ratio x
    of q to what the air can hold saturates softly, x / (1 + x^4)^(1/4)
    (0.85 over the sea -> ~79%; 1 -> 84%), where the vapour comes from the
    air mass aloft, warmer than a frosty ground. And the rain model's air
    loses its water too readily over long dry stretches (it is tuned for the
    rain, not the vapour; vapour_mixed adds back the background it lacks):
    the driest air is still held at HUMID_MIN."""
    x = q / _qsat(t_air, tune["q_k"])
    rh = np.maximum(x / (1.0 + x**4) ** 0.25, HUMID_MIN)  # (the floor after the soft saturation, which takes a hair off it)
    return t_air + np.log(rh) / tune["q_k"], 100.0 * rh


HUMID_MIN = 0.15  # the lowest relative humidity humidity() reports


LQ = 9.5  # C of moist static energy per unit of vapour (latent heat / heat capacity * 3.8 g/kg)


@njit(cache=True)
def _budyko1(p, pet, w):
    """budyko() for one value."""
    if p <= 0:
        return 0.0
    x = pet / p
    if x <= 1:
        return p * (1 + x - (1 + x**w) ** (1 / w))
    if x > 1e8:  # (a trace of rain: it all evaporates; also keeps an infinite x out)
        return p
    return p * (1 + x - x * (1 + x ** -w) ** (1 / w))  # (the same, without overflow on very dry ground)


@njit(cache=True, parallel=True)
def _rain(qs, src_q, ocean, ls_rate, cv_rate, mse_t, mse_thr, pet, budyko_w, soil_mm, open_sea, c_self, c_in,
          nbr, off, steps, dt, tau_ex, rh_c, rh_pow, cv_scale, evap, mean_mm, m0, ema0, warm):
    """Water vapour carried along the wind in physical time, for all
    seasons at once (arrays are [season, cell]). Each time step dt (s):
    - the air moves: a finite-volume transport through the cell faces
      (_transport: the upwind vapour times the face wind, plus eddy mixing
      down the vapour's gradient across the face), as each cell keeping
      c_self [season, cell] of its vapour and gathering c_in [slot, season]
      of each neighbour's (nbr, CSR off: _faces'), so what leaves one cell
      enters the next and the vapour's mass (per m2 x the cell's area) is
      kept;
    - over the sea the air takes up the share open_sea [season, cell] of
      its deficit to src_q each step: the bulk exchange's uptake in one
      step (_rain_args' sea_uptake, PW-015);
    - over land it takes up what the ground evaporates: water_balance's
      actual evaporation (Budyko, Fu's w budyko_w per cell, with soil_mm
      kept over from the other season) of the rain the place gets, in mm
      as the global mean mean_mm sets them, against the potential
      evaporation pet (mm/yr in each season), so the air gets back exactly
      what the land's water balance says it gives (PW-266);
    - what the air can't hold (above qs) rains out on a time scale tau_ex
      (s);
    - plus large-scale rain (fronts, rising air) at a rate ls_rate (1/s)
      of the rest that needs fairly humid air (relative humidity near rh_c
      [season, cell] or more: less where storms lift it, _season_inputs);
    - plus showers and thunderstorms, at cv_rate (1/s) per cv_scale C of
      instability: the moist static energy of the air near the ground (heat
      + height + latent heat of its vapour: mse_t + LQ * vapour) above that
      of the air aloft (mse_thr). Wet ground is cooler and dry ground hotter
      (evap C, see compute), which feeds back on the showers.
    It starts from the vapour m0 and the running mean of the rain ema0
    (zeros from cold) and runs `steps` steps toward the steady state; warm
    (a run's earlier update: m0 and ema0 its end state) sets the land's
    evaporation and the ground's cooling from ema0 at once instead of after
    5 and 20 steps. Returns the rain per step averaged over the last quarter
    of the steps, the large-scale part of it, the evaporation from the sea
    (the water the air takes up over it, same units), the air's water
    vapour left after its rain (_qsat units: 1 = saturated at 0 C), and the
    vapour and the running mean of the rain at the end. (Parallel over cells, each adding up in a fixed order; the
    one sum over all cells stays serial, so the results don't depend on the
    threads.)"""
    S, n = qs.shape
    m = np.ascontiguousarray(m0.T)  # [cell, season]: a neighbour's seasons side by side (one gather)
    m1 = np.empty((n, S))
    acc = np.zeros((S, n))
    acc_ls = np.zeros((S, n))
    ema = ema0.copy()  # running mean of each place's rain
    tcor = np.zeros((S, n))  # wet ground cooler, dry ground hotter (C)
    acc_up = np.zeros((S, n))  # water the air takes up over the sea (evaporation)
    acc_q = np.zeros((S, n))  # the air's water vapour after its rain (for humidity)
    land_e = np.zeros((S, n))  # what the land evaporates, per step (model units)
    tail = max(steps // 4, 1)
    fex = 1.0 - np.exp(-dt / tau_ex)
    scale = 1.0
    for it in range(steps):
        tcor_due = evap != 0 and ((it >= 20 and it % 10 == 0) or (warm and it == 0))
        land_due = (it >= 5 and it % 5 == 0) or (warm and it == 0)
        if land_due or tcor_due:
            tot = 0.0
            for k in range(S):
                for i in range(n):
                    tot += ema[k, i]
            scale = mean_mm * S * n / max(tot, 1e-12)  # model units -> mm/yr
        if land_due:
            # the land's evaporation, as water_balance has it: each season's
            # amount (mm) with what the soil kept from the other season's
            # surplus, all of it at most the year's rain
            for i in prange(n):
                if not ocean[i]:
                    aet = np.empty(S)
                    tot_p = 0.0
                    tot_e = 0.0
                    for k in range(S):
                        o = (k - 1) % S
                        p_o = ema[o, i] * scale / S
                        kept = min(p_o - _budyko1(p_o, pet[o, i] / S, budyko_w[i]), soil_mm)
                        p_k = ema[k, i] * scale / S
                        aet[k] = _budyko1(p_k + kept, pet[k, i] / S, budyko_w[i])
                        tot_p += p_k
                        tot_e += aet[k]
                    f = tot_p / tot_e if tot_e > tot_p else 1.0
                    for k in range(S):
                        land_e[k, i] = f * aet[k] * S / scale  # back to a rate, model units
        if tcor_due:
            for i in prange(n):
                if not ocean[i]:
                    for k in range(S):
                        lp = np.log10(max(ema[k, i] * scale, 1.0) / 100.0) / 1.2
                        tcor[k, i] = evap * (1.0 - 2.0 * min(max(lp, 0.0), 1.0))
        last = it >= steps - tail
        for i in prange(n):
            for k in range(S):
                q = c_self[k, i] * m[i, k]
                for j in range(off[i], off[i + 1]):
                    q += c_in[j, k] * m[nbr[j], k]
                if ocean[i]:
                    if src_q[k, i] > q:
                        up = open_sea[k, i] * (src_q[k, i] - q)
                        if last:
                            acc_up[k, i] += up
                        q += up
                else:
                    q += land_e[k, i]
                excess = max(q - qs[k, i], 0.0)
                rh = min(q / max(qs[k, i], 1e-12) / rh_c[k, i], 1.0)
                rate = ls_rate[k, i] * rh**rh_pow
                r_ls = min(rate * dt, 1.0) * (q - excess)
                inst = (mse_t[k, i] + tcor[k, i] + LQ * q - mse_thr[k, i]) / cv_scale
                if inst > 0:
                    rate += cv_rate[k, i] * min(inst, 2.0)
                r = fex * excess + min(rate * dt, 1.0) * (q - excess)
                m1[i, k] = q - r
                ema[k, i] += 0.05 * (r - ema[k, i])
                if last:
                    acc[k, i] += r
                    acc_ls[k, i] += r_ls
                    acc_q[k, i] += q - r
        m, m1 = m1, m
    return acc / tail, acc_ls / tail, acc_up / tail, acc_q / tail, np.ascontiguousarray(m.T), ema


def vapour_mixed(grid: Grid, q: np.ndarray, qs: np.ndarray, t_air: np.ndarray, tune: dict) -> np.ndarray:
    """The air's water vapour near the ground (_qsat units), from the rain
    kernel's q, with the large-scale mixing the kernel leaves out. The
    kernel's air rains out a little every step, so over a long dry stretch
    (a desert or a continent in its dry winter) its vapour drains toward
    nothing; real dry air keeps a background that eddies and the air
    sinking from aloft bring in from the moister air around (Delhi's and
    the Sahara's January dew points are ~-5 to +8 C, not -40). So: at least
    vap_bg of the vapour averaged over vap_bg_km, but no more than vap_bg_cap
    of what the air there can hold (qs: the kernel's capacity), so a cold
    place doesn't take up its warm neighbours' water (qs: the kernel's
    capacity of the air mass; t_air: the air near the ground, C, which over
    an ice sheet is far colder). Used for humidity and clouds only: the
    rain is the kernel's own."""
    cap = tune["vap_bg_cap"] * np.minimum(qs, _qsat(t_air, tune["q_k"]))
    bg = np.minimum(tune["vap_bg"] * smooth(grid, q, tune["vap_bg_km"]), cap)
    return np.maximum(q, bg)


def clouds(grid: Grid, elev: np.ndarray, seasons_in: list[dict], vap: list[np.ndarray],
           p_mm: list[np.ndarray], tune: dict, ocean=None) -> list[np.ndarray]:
    """Cloud cover (0..1, the share of the sky) in each half-year: a
    diagnostic from what the rain model knows (seasons_in: _season_inputs'
    dicts; vap: the air's water vapour, vapour_mixed; p_mm: the half-year's
    rain rate, mm/yr). Four kinds of cloud, overlapping at random (a sky
    with two kinds a and b is 1 - (1 - a)(1 - b) cloudy):
    - deep cloud where the air rises and rains: the tropical rain belt,
      monsoon summers, wet windward slopes (cloud_deep, growing with the
      rain above cloud_deep_mm0);
    - layer cloud of the storms and their fronts: the storm tracks, in
      proportion to the storminess and (on land) the air's humidity, not under the
      sinking subtropical air (cloud_storm);
    - low cloud over the sea: a base of shallow cumulus and stratus
      (cloud_sea), more over cold water (cloud_cold: the polar seas, fog
      off the sea-ice edge); thinner under sinking air (cloud_sink), but
      where the air above is much warmer than the sea (a strong inversion:
      the stability that keeps the rain kernel's showers away, its moist
      static energy below that aloft by more than cloud_sc_c[0] C) the
      sinking air traps a deck of stratocumulus under the inversion
      (cloud_sc): off California, Peru, Namibia and the Canaries, over the
      cool upwelling seas. Dry continental air from nearby land under the
      same sinking air clears it (cloud_cont: the summer Mediterranean);
    - over land: cloud in proportion to the air's humidity (cloud_rh:
      winter stratus over Europe), fair-weather cumulus where the ground
      heats moist air enough to make it unstable (cloud_cu, the summer
      continents), thin cloud over the cold poles (cloud_polar), and the
      sea's stratocumulus drifting over low coasts (cloud_coast). The
      sinking subtropical air clears the land (cloud_clear), less where it
      rains anyway (a monsoon overrides it).
    Returns a list of (cloud cover, sunshine share of the day: sunshine()),
    one per half-year. ocean: default elev <= 0 (compute's: not geo.is_land)."""
    ocean = elev <= 0 if ocean is None else ocean
    pole = np.clip((np.abs(grid.lat) - 60.0) / 20.0, 0, 1)
    landy = smooth(grid, (~ocean).astype(float), tune["cloud_cont_km"])
    coastal = tune["cloud_coast"] * np.clip(1 - np.maximum(elev, 0) / tune["cloud_coast_m"], 0, 1)
    out = []
    for si, q, p in zip(seasons_in, vap, p_mm):
        rh = np.clip(q / np.maximum(si["qs"], 1e-12), 0, 1)
        moist = np.where(ocean, 1.0, rh)
        sink, B = si["sink"], np.clip(si["B"], 0, 1.2)
        inst = si["mse_t"] + LQ * q - si["mse_thr"]  # C: > 0 unstable (see _rain)
        # (the towers' anvils spread over a few hundred km: the rain smoothed over cloud_rain_km,
        # which also hides the rain's cell-to-cell streaks, PW-019)
        p_s = smooth(grid, p, tune["cloud_rain_km"])
        deep = tune["cloud_deep"] * (1 - np.exp(-np.maximum(p_s - tune["cloud_deep_mm0"], 0) / tune["cloud_deep_mm"]))
        # (a front lifts the storm's own moist air: the land's half-year mean humidity,
        # dry in a continent's summer, thins its cloud only in proportion, PW-162)
        storm = tune["cloud_storm"] * B * np.clip(1 - sink, 0, 1) * moist
        s0, s1 = tune["cloud_sc_c"]
        dry = 1 - tune["cloud_cont"] * landy * sink
        deck = tune["cloud_sc"] * np.clip((-inst - s0) / s1, 0, 1) * sink * dry
        sea = (tune["cloud_sea"] + tune["cloud_cold"] * np.clip((20.0 - si["t_sl"]) / 20.0, -0.5, 1)
               - tune["cloud_sink"] * sink) * dry + deck
        sea = np.clip(sea, 0, tune["cloud_low_max"]) * (1 - tune["cloud_itcz"] * si["itcz"])
        c0, c1 = tune["cloud_cu_c"]
        cu = np.where(ocean, 0.0, tune["cloud_cu"] * np.clip((inst + c0) / c1, 0, 1) * np.sqrt(rh))
        # the stratocumulus deck drifts over low coasts (the garua of Lima, the Namib's fog)
        drift = np.clip(_nbr_mean(grid, np.where(ocean, deck, 0.0)) * coastal, 0, 1)
        layer = np.clip(1 - (1 - tune["cloud_rh"] * rh ** 1.5 - tune["cloud_polar"] * pole) * (1 - drift), 0, 1)
        low = np.where(ocean, sea, layer)
        clear = np.where(ocean, 0.0, tune["cloud_clear"] * sink * np.exp(-p / tune["cloud_clear_mm"]))
        cover = lambda k: np.clip((1 - (1 - k * deep) * (1 - k * cu) * (1 - storm) * (1 - low)) * (1 - clear), 0, 1)
        # Showers and thunderstorms build up in the afternoon and leave sunny
        # mornings: the convective clouds (deep and cumulus) shade only
        # cloud_sun_conv of the day that layer cloud of the same cover would.
        out.append((cover(1.0), sunshine(cover(tune["cloud_sun_conv"]))))
    return out


def day_hours(lat, tilt: float = 23.4) -> tuple[np.ndarray, np.ndarray]:
    """Mean day length (hours from sunrise to sunset) over the July
    (Apr-Sep) and January (Oct-Mar) half-years."""
    phi = np.radians(np.asarray(lat, float))[None, :]
    mid = np.cumsum(MONTH_DAYS) - MONTH_DAYS / 2
    decl = np.radians(tilt) * np.sin(2 * np.pi * (mid - 80.0) / 365.25)[:, None]
    h = 24.0 / np.pi * np.arccos(np.clip(-np.tan(phi) * np.tan(decl), -1, 1))  # (12, n)
    return h[3:9].mean(0), np.concatenate([h[:3], h[9:]]).mean(0)


SUN_CLEAR, SUN_CLOUD = 0.95, 0.9  # sunshine share of the day under a clear sky, and less per unit of cloud


def sunshine(cloud: np.ndarray) -> np.ndarray:
    """Share of the possible (sunrise to sunset) hours with bright sunshine
    under cloud cover cloud (0..1; for showery skies, see clouds): roughly
    1 - cloud, as observed (a sunshine recorder misses the low sun even in a
    clear sky: ~0.95; London: ~70% cloud, ~35% sunshine)."""
    return np.clip(SUN_CLEAR - SUN_CLOUD * cloud, 0, 1)


def shade(sun_share) -> np.ndarray:
    """The cloud cover as the day's light sees it (0..1): the cover that sunshine() maps onto the sunshine
    share sun_share. clouds' sunshine counts the convective clouds at cloud_sun_conv of the day (afternoon
    showers leave sunny mornings), so in the wet tropics the shade is well below the sky's cover. What the
    light at the ground follows (months' PAR for the plants, PW-806/PW-808: they read the sky's cover before
    v1-finish-12, ~0.21 sunshine on the Earth world's wet equatorial land against the climate's own 0.31 and
    CRU's ~0.51)."""
    return np.clip((SUN_CLEAR - np.asarray(sun_share, float)) / SUN_CLOUD, 0, 1)


def shade_from_hours(lat, sun_jul, sun_jan, tilt: float = 23.4) -> tuple[np.ndarray, np.ndarray]:
    """(shade_jul, shade_jan) from a world's stored bright-sunshine hours a day (sunshine_jul / sunshine_jan
    layers: day_hours x the sunshine share)."""
    h_jul, h_jan = day_hours(lat, tilt)
    return (shade(np.asarray(sun_jul, float) / np.maximum(h_jul, 1e-6)),
            shade(np.asarray(sun_jan, float) / np.maximum(h_jan, 1e-6)))


def storminess(grid: Grid, t_sl: np.ndarray) -> np.ndarray:
    """How stormy each latitude is in a season: the north-south temperature
    gradient of the latitude belt (C per 1000 km, from its zonal mean). The
    mid-latitude storms feed on exactly this contrast, which is why they
    are strongest in winter and reach further toward the equator then
    (winter rain around the Mediterranean, dry summers)."""
    width = 3.0
    nb = int(180 // width)
    bins = np.clip(((grid.lat + 90) // width).astype(int), 0, nb - 1)
    zm = np.bincount(bins, t_sl, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    zm = np.convolve(np.pad(zm, 2, mode="edge"), np.ones(5) / 5, mode="valid")
    grad = np.abs(np.gradient(zm)) / (width * 111.2) * 1000.0
    lat_c = -90 + width * (np.arange(nb) + 0.5)
    return np.interp(grid.lat, lat_c, grad)


OMEGA = 7.292e-5  # 1/s: the planet's spin (Earth)


def season_temps(grid: Grid, surf: np.ndarray, t_warm: np.ndarray, t_cold: np.ndarray, hk: float = 0.64):
    """Each half-year's mean temperature (Apr-Sep 'jul', Oct-Mar 'jan'),
    reduced to sea level, from the warmest- and coldest-month temperatures
    (a sine averages hk of its peak over a half-year). surf: height of the
    ground or ice surface, m. Returns (t_jul, t_jan)."""
    tm = 0.5 * (t_warm + t_cold)
    dt = hk * 0.5 * (t_warm - t_cold) * np.where(grid.lat >= 0, 1, -1)
    lift = LAPSE * np.maximum(surf, 0)
    return tm + dt + lift, tm - dt + lift


def jet_stream(grid: Grid, t_sl: np.ndarray, tune: dict | None = None) -> tuple[np.ndarray, np.ndarray]:
    """The upper-level wind (~10 km up) for one season, from the thermal
    wind relation: the wind aloft blows along the isotherms (cold air on its
    left in the north), the faster the sharper the temperature contrast
    beneath it: u = g H / (f T) up x grad(T), f the Coriolis parameter.
    So it's strongest at the polar front, in winter, and bends round warm
    and cold land (the jet over Japan, the trough over eastern Canada). The
    surface wind beneath adds little and is left out. t_sl: the season's
    temperatures reduced to sea level (C). Near the equator, where f
    vanishes, the relation fails and the jet fades out. Returns (jet: tangent
    vectors in m/s, baroclinicity: the temperature gradient near the ground
    in C per 1000 km, smoothed over baro_km, which is what feeds the storms)."""
    tune = {**TUNE, **(tune or {})}
    G = _geom(grid)
    lat = grid.lat
    # Storms grow from the contrast near the ground, land-sea fronts and all.
    S = smooth(grid, t_sl, tune["baro_km"])
    baro = np.linalg.norm(gradient(grid, S), axis=1) * 1000.0
    # Land-sea contrasts are shallow (a few km of air); the north-south
    # contrast fills the whole troposphere. So aloft only part of the
    # former is felt (jet_anom), smoothed further (to ~jet_km in all).
    width = 3.0
    nb = int(180 // width)
    bins = np.clip(((lat + 90) // width).astype(int), 0, nb - 1)
    zm = np.bincount(bins, S, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    zm = np.convolve(np.pad(zm, 2, mode="edge"), np.ones(5) / 5, mode="valid")
    lat_c = -90 + width * (np.arange(nb) + 0.5)
    dzm = np.interp(lat, lat_c, np.gradient(zm) / (width * 111.2))  # C per km northward
    anom = smooth_big(grid, S - np.interp(lat, lat_c, zm), np.sqrt(max(tune["jet_km"] ** 2 - tune["baro_km"] ** 2, 0)))
    gT = dzm[:, None] * G["north"] + tune["jet_anom"] * gradient(grid, anom)  # C per km
    a = np.abs(lat)
    f = 2 * OMEGA * np.maximum(np.sin(np.radians(a)), np.sin(np.radians(tune["jet_f_lat"])))
    k = 9.81 * tune["jet_h"] / (f * 250.0) / 1000.0 * np.sign(lat)  # m/s per (C per km)
    k *= np.clip(a / tune["jet_f_lat"], 0, 1) ** 2
    jet = k[:, None] * np.cross(grid.centers, gT)
    return jet, baro


def storm_track(grid: Grid, jet: np.ndarray, baro: np.ndarray, tune: dict) -> np.ndarray:
    """Storminess (~1 in a mid-latitude winter) along the storm tracks:
    storms are born where the temperature contrast is sharp (baro, C per
    1000 km; off the east coasts of continents in winter, where cold land
    air meets warm currents) and the jet steers them downstream, so they
    carry on across the ocean (to Ireland, to British Columbia) and fade
    over a few thousand km."""
    h = _geom(grid)["h"]
    k = np.exp(-h / tune["track_km"])
    b = baro / 7.0
    return carry(grid, jet, (1 - k) * b, np.full(grid.n, k), 2 * tune["track_km"], 0.2)


def _season_inputs(grid: Grid, elev, t_air, sst, v, shift, t_sl_season, tune, track=None, surf=None,
                   ocean=None) -> dict:
    """Per-cell inputs of the rain kernel for one season (see _rain).
    elev: the ground (<= 0: sea); surf: the ground or ice surface (m;
    default elev), which t_air, the surface air temperature (C, used over
    land), is on: an ice sheet lifts the air as a mountain range does
    (PW-332). sst: sea surface temperature, v: the vapour's wind, shift:
    deg the tropical rain belt is north of the equator, t_sl_season: the
    season's temperatures reduced to sea level, track: storminess along
    the jet's storm tracks (storm_track), which takes over a share
    storm_jet of the latitude belt's storminess. ocean: default elev <= 0
    (compute's: not geo.is_land)."""
    ocean = elev <= 0 if ocean is None else ocean
    lat = grid.lat
    up = LAPSE * np.maximum(elev if surf is None else surf, 0)
    # How much water the air can hold. Clouds form in the air mass aloft,
    # whose temperature follows the big picture (the sea-level temperature
    # smoothed over ~800 km) rather than the ground under it: a frosty
    # winter night inland doesn't wring the water out of the air. But where
    # the ground is hotter than the air mass (a summer desert), the sun-
    # heated air is stirred up from the ground through kilometres, and
    # clouds need that hot air saturated: hot desert air carries water but
    # rarely rains it. Rising air cools, but less than the ground does: only
    # part (lapse_q) of the cooling with height wrings water out.
    t_sl = np.where(ocean, sst, t_air + up)
    t_mass = np.maximum(smooth(grid, t_sl, tune["airmass_km"]), np.where(ocean, -99.0, t_sl))
    qs = np.where(ocean, _qsat(sst, tune["q_k"]), _qsat(t_mass - tune["lapse_q"] * up, tune["q_k"]))
    # the sea's own humidity, which its evaporation drives the air toward: saturation over salt water
    src_q = np.where(ocean, tune["sea_sat"] * qs, 0.0)
    # Storms stir moisture around (eddy mixing, see rain) and make large-scale
    # rain, both in proportion to the storminess (~1 in a mid-latitude winter).
    B = storminess(grid, t_sl_season) / 7.0
    if track is not None:
        B = (1 - tune["storm_jet"]) * B + tune["storm_jet"] * track
    # The tropical rain belt (where the trade winds meet and the air rises)
    # follows the sun; ~25 deg either side of it the air sinks (the dry
    # subtropics, the trade-wind inversion); the poles are dry highs.
    itcz = np.exp(-((lat - shift) / tune["itcz_w"]) ** 2)
    sink = np.exp(-((np.abs(lat - shift) - 25) / 9) ** 2)
    pole = np.clip((np.abs(lat) - 70) / 15, 0, 1)
    ls = tune["base"] * np.clip(tune["bg"] + tune["storm"] * B + tune["itcz_ls"] * itcz
                                - tune["belt_dry"] * sink - 0.3 * pole, 0.05, None)
    # Storms lift the air (PW-998 round 2): along the storm tracks the warm
    # sector's air glides up over the fronts, so it rains at a surface
    # humidity well below saturation (winter rain on the subtropical east
    # coasts is frontal: Gulf or Kuroshio air lifted over the continent's
    # cold air). A storminess of 1 lifts the air lift_m, so the large-scale
    # rain's humidity gate rh_c falls by what that lift's cooling takes from
    # saturation; not under the subtropics' sinking air, which holds the
    # storms' fronts down (as clouds' cloud_storm).
    lift = B * np.clip(1 - sink, 0, 1)
    rhc = tune["rh_c"] * np.exp(-tune["q_k"] * LAPSE * tune["lift_m"] * lift)
    # Showers need unstable air: warm, moist air near the ground compared
    # with the air aloft. Within ~20-30 deg of the equator the air aloft has
    # the same temperature everywhere (the Earth's spin is too weak there to
    # hold temperature differences up), set by the warmest seas: so hot but
    # dry deserts and cool seas stay stable while humid hot land and warm
    # seas boil over. Further poleward the air aloft follows the latitude's
    # sea temperature (so summer continents get thunderstorms).
    mse_t = np.where(ocean, sst, t_air + 9.8e-3 / LAPSE * up)  # (+ height: g/cp per m)
    zs = zonal_mean(grid, sst, ocean)
    t_trop = zs[np.abs(lat) < 20].max()
    zs = zs + np.clip((tune["wtg"] + 15 - np.abs(lat)) / 15, 0, 1) * np.maximum(t_trop - zs, 0)
    t_ref = smooth(grid, zs, 800.0)
    mse_thr = t_ref + LQ * tune["rh"] * _qsat(t_ref, tune["q_k"])
    cv = tune["cv"] * tune["base"] * (1 + tune["itcz_cv"] * itcz) * np.clip(1 - tune["cv_sink"] * sink, 0, 1)
    # (t_sl, t_ref, sink, itcz: not used by the rain kernel, but by clouds())
    return dict(qs=qs, src_q=src_q, ls=ls, cv=cv, rhc=rhc, mse_t=mse_t, mse_thr=mse_thr, v=np.asarray(v, np.float64),
                B=B, track=B if track is None else track, t_sl=t_sl, t_ref=t_ref, sink=sink, itcz=itcz, t_air=np.where(ocean, sst, t_air))


U_REF = 7.0  # m/s: wind speed 1 (a steady trade wind)
RATE_S = 17189.0  # s: TUNE's rain rates (base, cv, fex) are shares per this long: one step of the old per-cell
# kernel at level 6 (its 120 km at U_REF), where they were calibrated (PW-015)
K_MIX = 2.0e5  # m2/s: the eddy mixing at full strength (the old kernel's one neighbour mix per L6 step)
RAIN_DAYS = 20.0  # days of pseudo-time to the vapour's steady state (it rains out in ~5-10; Earth L6: the
# regions within 1% of 60 days, the global books within 0.05% of the rain)
RAIN_WARM_DAYS = 8.0  # ... from a run's last climate update (4 Myr before: compute's rain_start), which
# starts near it (PW-387)
RAIN_INIT = 0.5  # the land's air starts this share saturated (the sea's at src_q): a guess near the steady
# state, which it doesn't change (from dry air the same takes 30 days)
RAIN_CFL = 0.95  # the most of a cell's vapour that may leave it in one step (<= 1: no cell goes negative)


def face_winds(grid: Grid, seasons_in: list[dict], tune: dict) -> tuple[np.ndarray, np.ndarray]:
    """The vapour's wind through each face (_faces' order; m/s, + from ea to
    eb: the mean of the two cells' winds across the face's normal) and the
    eddy mixing across it (m2/s), [season, face]. The vapour's wind adds
    the storms' poleward drift (PW-998 round 3): along the storm tracks the
    warm sectors carry moist air poleward and the cold air behind them
    brings dry air back, a net poleward flux of vapour (v'q', most of what
    crosses 30-40 deg; unverified) that mixing down the mean gradient
    doesn't make. Its speed is eddy_drift (m/s) x the storm track's
    storminess (_season_inputs' track), fading out within 15 deg of the
    equator."""
    F = _faces(grid)
    ea, eb = F["ea"], F["eb"]
    S, ne = len(seasons_in), len(ea)
    un, kd = np.empty((S, ne)), np.empty((S, ne))
    mid = grid.centers[ea] + grid.centers[eb]
    mid = mid / np.linalg.norm(mid, axis=1)[:, None]
    north = np.array([0.0, 0.0, 1.0])[None, :] - mid[:, 2:3] * mid
    north = north / np.maximum(np.linalg.norm(north, axis=1)[:, None], 1e-12)
    # the face normal's poleward part, faded within 15 deg of the equator, where the Earth's spin is too weak for
    # the storms' eddies (as monsoon_wind's geostrophic share; the storm tracks run on into the tropics)
    poleward = np.clip(np.abs(np.degrees(np.arcsin(np.clip(mid[:, 2], -1, 1)))) / 15.0, 0, 1) * np.sign(mid[:, 2]) \
        * (F["n"] * north).sum(1)
    for k, d in enumerate(seasons_in):
        v = d["v"] * U_REF
        drift = tune["eddy_drift"] * np.clip(0.5 * (d["track"][ea] + d["track"][eb]), 0, 1.2)
        un[k] = (0.5 * (v[ea] + v[eb]) * F["n"]).sum(1) + drift * poleward
        kd[k] = K_MIX * np.clip(0.12 + tune["eddy"] * 0.5 * (d["B"][ea] + d["B"][eb]), 0, 1)
    return un, kd


def _transport(grid: Grid, un: np.ndarray, kd: np.ndarray) -> tuple:
    """The finite-volume transport as each cell's share kept (c_self) and
    gathered from each neighbour (c_in, per slot of _faces' CSR; nbr: that
    neighbour) in one time step dt (s), the longest at which at most
    RAIN_CFL of any cell's vapour leaves it. A face passes on, per second,
    (its outward wind if positive + the mixing kd / lc) x L / A of the cell's
    vapour: the same amount the cell beyond gains, so the vapour's mass is
    kept."""
    F = _faces(grid)
    n = grid.n
    e, sg = F["eid"], F["sg"]
    cell = np.repeat(np.arange(n), np.diff(F["off"]))
    u_out = sg[None, :] * un[:, e]  # [season, slot]: the wind out of the cell through the face
    mix = (kd / F["lc"])[:, e]
    LA = (F["L"][e] / F["A"][cell])[None, :]
    leave = (np.maximum(u_out, 0) + mix) * LA
    gain = (np.maximum(-u_out, 0) + mix) * LA
    out = np.stack([np.bincount(cell, leave[k], n) for k in range(len(un))])
    dt = float(RAIN_CFL / out.max())
    return 1.0 - dt * out, np.ascontiguousarray((dt * gain).T), F["nbr"], dt


def sea_uptake(seasons_in: list[dict], open_sea: np.ndarray, dt: float, tune: dict) -> np.ndarray:
    """The share of its deficit to the sea's humidity (src_q) that the air
    takes up over the sea in one rain step of dt s, [season, cell]: a bulk
    exchange (PW-015). The sea evaporates into the boundary layer at
    C_E x wind x (src_q - q), so the air's deficit closes on a time scale
    sea_bl_m / (sea_ce x wind): ~0.6 days at 7 m/s, a fetch of ~400 km,
    with sea_wind_min standing for the gusts in a calm. Only the open share
    of the sea (open_sea: not under sea ice, less the stable summer air
    off land, compute) exchanges, per unit of time, so a frozen sea's
    leads take up the same per day at any time step. Before, the air was
    refilled to src_q at once each step: the sea's evaporation was set by
    what left the air, and any strip of sea saturated the air crossing it."""
    spd = np.stack([np.maximum(speed(d["v"]) * U_REF, tune["sea_wind_min"]) for d in seasons_in])
    return np.ascontiguousarray(1.0 - np.exp(-open_sea * tune["sea_ce"] * spd / tune["sea_bl_m"] * dt))


def _rain_args(grid: Grid, elev, seasons_in: list[dict], tune: dict, pet, w=None, open_sea=None,
               ocean=None, start=None) -> tuple:
    """rain's arguments to _rain (also tools/moisture_budget.py's). start:
    an earlier call's end state (rain's), to start warm from."""
    n = grid.n
    ocean = elev <= 0 if ocean is None else ocean
    w = np.full(n, tune["budyko_w"]) if w is None else np.ascontiguousarray(np.broadcast_to(w, (n,)), np.float64)
    open_sea = np.ones(n) if open_sea is None else np.asarray(open_sea, np.float64)
    open_sea = np.ascontiguousarray(np.broadcast_to(open_sea, (len(seasons_in), n)), np.float64)
    st = {k: np.ascontiguousarray(np.stack([d[k] for d in seasons_in])) for k in
          ("qs", "src_q", "ls", "cv", "mse_t", "mse_thr", "rhc")}
    c_self, c_in, nbr, dt = _transport(grid, *face_winds(grid, seasons_in, tune))
    open_sea = sea_uptake(seasons_in, open_sea, dt, tune)
    warm = start is not None and start["vap"].shape == st["qs"].shape
    steps = int((RAIN_WARM_DAYS if warm else RAIN_DAYS) * 86400.0 / dt) + 20
    tau_ex = -RATE_S / np.log(1.0 - tune["fex"])
    m0 = start["vap"] if warm else np.where(ocean, st["src_q"], RAIN_INIT * st["qs"])
    ema0 = start["ema"] if warm else np.zeros_like(st["qs"])
    return (st["qs"], st["src_q"], ocean, st["ls"] / RATE_S, st["cv"] / RATE_S, st["mse_t"], st["mse_thr"],
            np.ascontiguousarray(pet, np.float64), w, float(tune["soil_mm"]), open_sea, c_self, c_in, nbr,
            _faces(grid)["off"], steps, dt, tau_ex, st["rhc"], tune["rh_pow"], tune["cv_scale"],
            tune["evap_cool"], tune["mean_mm"], np.ascontiguousarray(m0, np.float64),
            np.ascontiguousarray(ema0, np.float64), warm)
def storm_spread(grid: Grid, r: np.ndarray, r_ls: np.ndarray, seasons_in: list[dict], tune: dict) -> np.ndarray:
    """Storms carry their rain with them: the large-scale (frontal) rain is
    spread over a storm's size, so e.g. the storms that brew over warm
    coastal seas in winter rain on the east coasts even though the mean
    wind blows offshore there."""
    r = r.copy()
    for k, d in enumerate(seasons_in):
        w = np.clip(tune["storm_mix"] * d["B"], 0, 0.9)
        r[k] += w * (smooth(grid, r_ls[k], tune["storm_km"]) - r_ls[k])
    return r


def rain(grid: Grid, elev, seasons_in: list[dict], tune: dict, pet, w=None,
         open_sea=None, ocean=None, start=None) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Rain rate (model units) per season, [season, cell], from the inputs
    of _season_inputs for each season (v: the vapour's wind), the
    evaporation from the sea (same units and shape; 0 on land) and the
    air's water vapour (_qsat units, same shape; see humidity()). The
    vapour is carried in physical time (_rain, PW-015): wind 1 is U_REF
    m/s, TUNE's rain rates are shares per RATE_S seconds, and the eddy
    mixing is K_MIX m2/s x clip(0.12 + eddy x storminess, 0, 1), so a
    planet rains the same at every grid level. pet: potential evaporation
    (mm/yr) in each season, [season, cell], and w: Fu's w per cell
    (default TUNE's budyko_w), from which the land evaporates as
    water_balance has it; open_sea: the open share of the sea (default 1;
    per cell, or [season, cell]): the share not under sea ice, the only
    part the air takes up water from, less the stable land air of a summer
    (compute), which sets its bulk exchange (sea_uptake). tune's
    mean_mm: the global mean rain the kernel's rain is scaled to (in mm,
    for the land's evaporation). ocean: default elev <= 0 (compute's: not
    geo.is_land). start: an earlier call's end state (the fourth result:
    the kernel's vapour and running mean of the rain), to start from it and
    run RAIN_WARM_DAYS instead of RAIN_DAYS (a run's climate updates, PW-387;
    the outputs move by the kernel's convergence error, ~1%)."""
    r, r_ls, up, vap, m, ema = _rain(*_rain_args(grid, elev, seasons_in, tune, pet, w, open_sea, ocean, start))
    return storm_spread(grid, r, r_ls, seasons_in, tune), up, vap, dict(vap=m, ema=ema)


TUNE = dict(
    # moisture
    rh=0.85,  # sea air's humidity relative to saturation at the sea surface (the showers' reference air aloft)
    sea_sat=0.98,  # the sea surface's own humidity, relative to fresh water's saturation (salt lowers it ~2%)
    sea_ce=1.3e-3,  # bulk transfer coefficient of the sea's evaporation (C_E, neutral, ~10 m)
    sea_bl_m=500.0,  # m: the marine boundary layer the sea's evaporation fills (the bulk exchange's depth)
    sea_wind_min=3.0,  # m/s: the least wind the bulk exchange sees (gusts in a calm)
    q_k=0.06,  # per C: how much more water warm air holds (Clausius-Clapeyron ~0.07)
    lapse_q=0.5,  # share of the cooling with height that wrings water out of rising air
    airmass_km=800.0,  # km over which the air mass aloft evens out the ground's temperatures
    # rain-making
    fex=0.25,  # share of the oversaturated water that rains out per RATE_S (rest further on)
    base=0.035,  # share of the vapour that rains out per RATE_S (large-scale rain; showers: cv times this)
    bg=0.45,  # large-scale rain everywhere (fronts, drizzle), times base
    itcz_ls=0.3,  # extra large-scale rain under the tropical rain belt
    itcz_w=10.0,  # deg: half-width of the tropical rain belt
    belt_dry=0.3,  # how much the sinking subtropical air suppresses large-scale rain
    storm=0.6,  # large-scale rain from storms, per unit of storminess
    eddy=1.0,  # how much storms stir moisture around (x K_MIX), per unit of storminess
    eddy_drift=1.0,  # m/s: the storms' poleward drift of the vapour at a storm track's storminess 1 (face_winds;
    # ~ r x sigma_v x sigma_q / q ~ 0.5 x 6 m/s x 0.3, unverified back of the envelope, PW-998 round 3)
    storm_mix=1.0,  # share of the frontal rain spread over a storm's size, per unit of storminess
    storm_km=600.0,  # km: a storm's rain area
    cv=4.0,  # showers: rain-out per RATE_S at cv_scale C of instability, times base
    cv_scale=10.0,  # C of moist static energy excess for full-rate showers
    itcz_cv=1.0,  # showers are likelier under the tropical rain belt (rising air) ...
    cv_sink=0.5,  # ... and rarer under the sinking subtropical air
    wtg=20.0,  # deg: the tropics' even temperature aloft reaches this far (then fades over 15 deg)
    rh_c=0.8,  # relative humidity above which the large-scale rain runs at full rate...
    rh_pow=3.0,  # ...and how fast it falls off below it
    lift_m=1500.0,  # m: how far a storm (storminess 1) lifts the air it rains from (PW-998 round 2; the
    # warm conveyor belt's ascent is several km, unverified; a season-mean storminess of 1 is ~1-2 km of it)
    # humidity and clouds (vapour_mixed, clouds; diagnostics: they don't change the rain)
    vap_bg=0.5,  # the air keeps at least this share of the vapour around it ...
    vap_bg_km=2500.0,  # ... averaged over this far ...
    vap_bg_cap=0.5,  # ... up to this share of what it can hold
    cloud_deep=0.8,  # deep cloud where it rains hard (tropical rain belt, monsoons) ...
    cloud_deep_mm0=300.0,  # ... above this rain rate (mm/yr) ...
    cloud_deep_mm=1000.0,  # ... reaching 63% of it this much more
    cloud_rain_km=300.0,  # km over which a rain belt's anvils spread its deep cloud
    cloud_storm=0.45,  # layer cloud per unit of storminess (storm tracks, fronts)
    cloud_sea=0.4,  # low cloud over the sea at 20 C (shallow cumulus, stratus) ...
    cloud_cold=0.35,  # ... plus this much over freezing water (polar seas, sea-ice edges)
    cloud_sink=0.25,  # ... less this under the sinking subtropical air ...
    cloud_sc=0.7,  # ... but a stratocumulus deck where it sinks onto a strong inversion ...
    cloud_sc_c=(4.0, 8.0),  # ... C of stability (moist static energy below that aloft): from, full over
    cloud_cont=1.0,  # sinking dry air off the land around (cloud_cont_km) clears the sea's low cloud
    cloud_cont_km=800.0,
    cloud_low_max=0.85,  # the most low cloud over the sea
    cloud_coast=1.0,  # share of the sea's stratocumulus deck that drifts over a coast (times the share of
    # its neighbours that are sea) ...
    cloud_coast_m=1000.0,  # ... less the higher it is, none this high (the decks are ~1 km deep)
    cloud_itcz=0.1,  # share of the sea's low cloud the tropical rain belt's towers replace
    cloud_rh=0.55,  # land: cloud per unit of relative humidity (^1.5) of the air mass ...
    cloud_polar=0.25,  # ... thin cloud over the cold poles (from 60 deg, in full from 80) ...
    cloud_cu=0.5,  # ... fair-weather cumulus where the ground makes the air unstable ...
    cloud_cu_c=(4.0, 6.0),  # ... from this many C stable, in full over this many more
    cloud_clear=0.5,  # share of the land's cloud the sinking subtropical air clears ...
    cloud_clear_mm=800.0,  # ... less where it rains (e-fold mm/yr)
    cloud_sun_conv=0.6,  # share of the day showers and cumulus shade (they build up in the afternoon)
    # winds and seasons
    ice_cool_km=300.0,  # an ice sheet's cover (ice_cover) is the share of the land this far around
    # under ice (a small cap sits in its surroundings' air)
    belt_shift=10.0,  # deg the tropical rain belt follows the sun at the solstice (times tilt/23.4)
    hk=0.64,  # the half-years' mean of a seasonal swing (2/pi of the peak, for a sine)
    monsoon=1.0,  # strength of the land-sea pressure winds ...
    big=1.5,  # ... and of their continent-wide part
    big_km=2000.0,  # km: the scale of that part
    eq_up=15.0,  # C: equatorial upwelling (cold tongues) under a full trade wind
    coast_up=10.0,  # C: coastal upwelling where a full wind pushes the surface water offshore (the slow
    # eastern-boundary currents bring little cold of their own: Peru and Namibia are cold from below)
    block=1.0,  # share of the wind running up into high ground that turns along it instead
    block_m=1500.0,  # m: ground higher than this blocks the low-level wind ...
    block_km=250.0,  # ... felt this far out
    # jet stream and storm tracks
    jet_km=1000.0,  # km: smoothing of the temperature field the jet follows
    jet_anom=0.4,  # share of the land-sea temperature contrast felt through the troposphere
    baro_km=600.0,  # km: smoothing of the low-level temperature contrast storms grow from
    jet_h=10000.0,  # m: depth of the air the thermal wind builds up over (~the troposphere)
    jet_f_lat=20.0,  # deg: the thermal wind fades out equatorward of this
    storm_jet=0.7,  # share of the storminess that follows the jet's storm tracks (rest: latitude belts)
    track_km=2500.0,  # km a storm track carries on downstream of where storms are born
    # ocean currents
    gyre=0.05,  # strength of the wind-driven gyres (scales the streamfunction's currents)
    gyre_km=200.0,  # km: friction width of the western boundary currents at the equator (r/beta)
    gyre_iters=300,  # relaxation sweeps of the gyre solver (over-relaxed: converged to <1%)
    tau_pow=1.0,  # wind stress ~ |wind|^tau_pow (1: linear)
    island_km2=150000.0,  # land smaller than this doesn't wall off the gyres
    acc=1.0,  # circumpolar current per unit of zonal wind, where a latitude is sea all round
    eq_cur=1.0,  # equatorial currents per unit of zonal (trade) wind ...
    eq_cur_lat=8.0,  # ... within ~this many deg of the equator
    cur_ref=0.5,  # current speed at which sea-surface heat is carried ~2500 km before it fades ...
    cur_min=0.3,  # ... scaled with speed, between these multiples
    cur_max=3.0,
    # temperature
    continental=24.0,  # C: seasonal half-swing of land left to itself (times season strength)
    coast=0.35,  # sea air at a coast per share of sea neighbours (sea breezes, fog)
    sum_tau=86400.0,  # s: the summer air's memory over land: the sunlit, convective boundary layer takes up the
    # ground's heat in about a day (its daily cycle), so the air reaches U x this inland before it is the land's
    # (~450 km in a 5 m/s wind)
    sum_h=1500.0,  # m: ... the depth of that boundary layer, which the day's sensible heat warms (encroachment:
    # h = sqrt(2 H tau / (rho c_p gamma)) ~1500 m for ~80 W/m2 into a free troposphere of ~5 K/km)
    ef_ref=0.61,  # the summer's actual / potential evaporation the temperature curve stands for (Earth's ice-free
    # land 20-60 deg without the split: tools' water_balance on its own climate) ...
    cloud_ref=0.63,  # ... and its summer cloud cover (Earth's ice-free land 20-60 deg, as albedo_ref)
    fetch_km=1000.0,  # km: the summer air above the boundary layer is as continental as the land within this
    # (the synoptic scale its storms and highs mix it over; _summer_fetch) ...
    fetch_h=3500.0,  # m: ... up to this height (the summer's continental heat low reaches ~650 hPa), so the
    # boundary layer's own share of the land's swing is sum_h / fetch_h
    air_km_w=900.0,  # km: how far the air that came off land reaches over the sea (_sea_half's land_air)
    air_m=1000.0,  # m: the depth of the winter air mass over land (to ~850 hPa, which the storms mix): its heat
    # capacity against ice_b sets how long it keeps the sea's warmth over land; higher ground cuts it off
    air_km_sea=300.0,  # ... and over open water, its winter surface (the boundary layer's depth over the bulk
    # heat-transfer coefficient, ~500 m / 1.5e-3: cold air off a continent warms over this; _winter_air)
    k_ice=2.0,  # W/m/K: sea ice's thermal conductivity (the water's heat through the ice warms the air over it) ...
    ice_b=3.5,  # ... against W/m2 per C the winter air loses to space (the land's seasonal swing: ~100 W/m2 of
    # seasonal sunshine for its ~24 C half-swing; perennial ice ~3 m: 1/6 of the way to the water, a 1 m pack 1/3)
    open_b=30.0,  # W/m2 per C: the heat open water gives the cold air over it (turbulent and longwave; leads,
    # polynyas and the open part of a freezing sea: a pack 15% open keeps its air ~10 C nearer the water's)
    evap_cool=1.5,  # C: how much cooler wet summers are (and hotter dry ones), for the rain kernel's own showers
    # (the temperatures' own: _summer_split)
    # the vegetation's feedbacks (vegetation_feedbacks, albedo_warming; tuned on Earth: tools/veg_check.py)
    veg_w=1.0,  # Budyko w per unit of woody cover ...
    veg_w_deep=0.3,  # ... plus this per unit of deep-rooted evergreen tree cover ...
    veg_w_ref=0.41,  # ... less Earth's land mean of the two (so Earth stays at budyko_w)
    albedo_k=0.03,  # C per W/m2 of sunshine absorbed at the ground (local; the air mixes it away)
    albedo_cap=2.0,  # C: the most a half-year moves either way
    albedo_ref=0.21,  # the snow-free albedo the temperature curve stands for (Earth's land mean) ...
    albedo_snow_ref=0.59,  # ... and with snow lying (Earth's mix of open and forest-masked snow)
    snow_albedo=0.75,  # fresh-ish snow on open ground
    snow_full_mm=30.0,  # mm of snowpack (water) that covers the ground
    mean_mm=1000.0,  # global mean precipitation, mm/yr (Earth ~1000)
    # evaporation and runoff (see water_balance)
    budyko_w=2.6,  # Fu's w: how readily the land gives the rain back to the air (Earth's mean ~2.6)
    soil_mm=150.0,  # mm of water the soil holds over from one half-year to the next
    lake_wind=2.0,  # m/s at 2 m over lakes for open_water_evap (FAO-56's default without wind data)
    leads=0.1,  # share of a frozen sea open in leads and polynyas, which the rain model's air takes up water
    # through (winter pack ice: ~1-3% open in the central Arctic, ~5-20% in the Antarctic pack; PW-308)
    # salinity and the overturning circulation (see ocean.py)
    salt_k=2.0,  # psu fresher per m/yr of net fresh water into the sea (S0 x mixing time / depth) ...
    salt_ice=4.0,  # ... x (1 + this) under year-round sea ice (the fresh lid: a halocline)
    salt_km=3000.0,  # km a current carries its salinity at cur_ref before it has mixed
    salt_diff=0.3,  # eddy mixing of salinity with the neighbours, per step
    river_km=300.0,  # km: a river plume's spread over the sea
    ice_export=0.25,  # share of the winter's sea ice that drifts away to melt elsewhere (all of it
    # where the winter wind blows off the coast) ...
    ice_km=800.0,  # ... spread over this far
    brine_m=50.0,  # m: depth of the winter mixed layer the brine of new sea ice mixes into (and the seasons' heat:
    # _sea_half)
    moc=0.65,  # Sv sinking per kg/m3 of density difference (sinking - water replacing it) per 1e6 km2
    moc_k=3.0,  # Sv per kg/m3: the most one sinking site turns over (see ocean.overturning)
    moc_z=2000.0,  # m: depth at which the waters' densities are compared for sinking
    moc_top=0.1,  # the deep water is the densest water of this share of the polar sea (by area) ...
    moc_mix=0.5,  # ... less this (kg/m3: it mixes on its way down)
    moc_entrain=1.5,  # ... and a pocket far denser than the polar sea around it draws in this many times its
    # own volume of that sea's water as it cascades down (overflows, Antarctic shelf water: 2-3x; PW-579)
    moc_drho=0.3,  # kg/m3: water this much lighter than the deep water can't sink ...
    moc_pow=3.0,  # ... and the sinking grows as (excess / moc_drho)^moc_pow up to its density
    moc_lat=50.0,  # deg: deep water forms poleward of this (fully 10 deg further)
    moc_km=300.0,  # km: a sinking site's water is the mix over this
    moc_sea_km2=1.0e6,  # km2: a sea smaller than this (cut off from the others) has no deep water of its own
    moc_src_lat=25.0,  # deg: the water replacing what sinks comes from equatorward of this ...
    moc_follow=3.0,  # ... riding the currents (a step costs exp(-this x the current's speed its way / cur_ref))
    moc_width=250.0,  # km: the inflow's width (for its heat loss to the air, and the straits it can pass) ...
    moc_lambda=30.0,  # ... W/m2 per C it gives up to the air above the latitude's sea temperature
    moc_q0=0.001,  # Sv per km of width: an inflow this strong makes up ~2/3 of the surface water
    moc_layer_m=500.0,  # m: the inflow layer's depth, which winter convection mixes into (ocean.winter_half)
    moc_zonal=1.0,  # share of the inflow's warmth taken off its latitude's mean, both hemispheres together
    # (see sea_surface; PW-265, PW-589)
    moc_level=5,  # grid level the overturning is solved on (5: ~220 km cells)
    moc_spin=6.0,  # x moc_drho at the start (see ocean.solve)
    moc_iters=4,  # damped iterations of salinity <-> overturning while the spin-up tightens, then ...
    moc_tol=0.003,  # ... on until the inflow's share of the surface water moves by less than this (PW-360) ...
    moc_max_iters=40,  # ... or this many in all (a cost bound)
    moc_relax=0.6,  # damping of each iteration
)


# --------------------------------------------------------------------------
# Evaporation and runoff
# --------------------------------------------------------------------------
MONTH_DAYS = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
S0_MJ = 1361.0 * 86400 / 1e6  # the solar constant, MJ/m2 per day
LATENT = 2.45  # MJ to evaporate 1 kg of water (1 kg/m2 = 1 mm)


_INSOL = {}


def insolation(lat, tilt: float = 23.4) -> np.ndarray:
    """Daily mean sunshine at the top of the atmosphere (MJ/m2/day) in
    each month, shape (12, n): long polar summer days, none in polar winter.
    (Cached: the same grid's latitudes come back every climate update.)"""
    lat = np.asarray(lat, float)
    key = (lat.size, float(tilt), hash(lat.tobytes()))
    if key not in _INSOL:
        if len(_INSOL) > 8:
            _INSOL.clear()
        _INSOL[key] = _insolation(lat, tilt)
        _INSOL[key].setflags(write=False)
    return _INSOL[key]


def _insolation(lat, tilt: float) -> np.ndarray:
    phi = np.radians(lat)[None, :]
    mid = np.cumsum(MONTH_DAYS) - MONTH_DAYS / 2  # day of the year at mid-month
    decl = np.radians(tilt) * np.sin(2 * np.pi * (mid - 80.0) / 365.25)[:, None]  # 0 at the March equinox
    h0 = np.arccos(np.clip(-np.tan(phi) * np.tan(decl), -1, 1))  # half the day length, radians
    return S0_MJ / np.pi * (h0 * np.sin(phi) * np.sin(decl) + np.cos(phi) * np.cos(decl) * np.sin(h0))


def budyko(p, pet, w):
    """Actual evaporation (same units as p) from rain p and potential
    evaporation pet, by Fu's form of the Budyko curve: where energy is
    short (pet << p) the ground gives back about pet and the rest runs off;
    where water is short (pet >> p) nearly all the rain evaporates. w sets
    how sharp the bend between the two is."""
    x = pet / np.maximum(p, 1e-9)
    return np.where(p > 0, p * (1 + x - (1 + x**w) ** (1 / w)), 0.0)


def pet_months(lat, temp, t_warm, t_cold, tilt: float = 23.4) -> np.ndarray:
    """Potential evaporation (mm per month, shape (12, n)) by Oudin et al.
    (2005): Ra/lambda*(T+5)/100, nothing below -5 C; each month's
    temperature a sine between the coldest and warmest month, peaking in
    July (north) or January (south). Summed over the year it is the `pet`
    of water_balance (the aridity index P/PET uses it)."""
    lat = np.asarray(lat, float)
    return _pet(insolation(lat, tilt), month_temps(lat, temp, t_warm, t_cold))


def _pet(ra, t_m):
    """Oudin PET, mm per month, from top-of-atmosphere sunshine ra (MJ/m2/day) and temperature t_m."""
    return np.maximum(ra / LATENT * (t_m + 5) / 100, 0) * MONTH_DAYS[:, None]


def month_temps(lat, temp, t_warm, t_cold) -> np.ndarray:
    """Mean temperature of each month (C, shape (12, n)): a sine between
    the coldest and warmest month around the annual mean, peaking in July
    (north) or January (south), clipped to [t_cold, t_warm]."""
    m = np.arange(12)[:, None]
    peak = np.where(np.asarray(lat) >= 0, 6, 0)[None, :]
    amp = 0.5 * (t_warm - t_cold)
    return np.clip(temp + amp * np.cos(2 * np.pi * (m - peak) / 12), t_cold, t_warm)


# share of a half-year's months under a cosine peaking at its middle month
# (Jul for Apr-Sep): (0 + .5 + .866 + 1 + .866 + .5) / 6
_HALF_COS = (1 + 2 * np.cos(np.pi / 6) + 2 * np.cos(np.pi / 3)) / 6
SNOW_DDF = 3.0  # mm of snow melted per positive degree-day (icemass.py's snow DDF; months melt at the monthly mean, no day-to-day scatter: PW-877)


def month_rain(p_jul, p_jan) -> np.ndarray:
    """Rain (mm) in each month, shape (12, n), from the two half-year rates
    (mm/yr; Apr-Sep, Oct-Mar): a cosine through the year peaking in July
    (or January, when that half is wetter), as koppen() assumes, rescaled
    so each half-year's months add up to exactly its rate / 2."""
    m = np.arange(12)[:, None]
    mean = (p_jul + p_jan) / 24.0
    a = np.clip((p_jul - p_jan) / np.maximum(p_jul + p_jan, 1e-9) / _HALF_COS, -1, 1)
    shape = mean * (1 + a * np.cos(2 * np.pi * (m - 6) / 12))
    jul = (m >= 3) & (m <= 8)
    s_jul = np.maximum(shape[3:9].sum(0), 1e-12)
    s_jan = np.maximum(shape.sum(0) - shape[3:9].sum(0), 1e-12)
    return np.where(jul, shape * (0.5 * p_jul / s_jul), shape * (0.5 * p_jan / s_jan))


def _erf(x):
    """Abramowitz-Stegun 7.1.26 (|error| < 1.5e-7)."""
    sg = np.sign(x)
    x = np.abs(x)
    t = 1 / (1 + 0.3275911 * x)
    y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496735) * t + 0.254829592) * t * np.exp(-x * x)
    return sg * y


def months(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt: float = 23.4, cloud_jul=None, cloud_jan=None) -> dict:
    """The twelve months of a climate, rebuilt from what it stores (annual,
    warmest- and coldest-month temperature, the two half-year rain rates,
    optionally the half-years' cloud cover), shared by everything that needs
    months (PW-194). Each value has shape (12, n):
      t      C: month mean temperature (month_temps: a sine, as pet_months)
      p      mm: precipitation (month_rain: half-year sums exact)
      pet    mm: potential evaporation (Oudin; sums to water_balance's pet)
      par    MJ/m2: photosynthetically active light at the ground: the top of
             the atmosphere's sunshine x the share reaching the ground
             (Angstrom-Prescott: 0.25 + 0.5 x the sunshine share, from the
             cloud as climate.sunshine; 0.5 cloud without one) x 0.48. The
             cloud given should be the light's (compute's shade_jul /
             shade_jan, or shade_from_hours of a world's sunshine layers),
             not the sky's cover: showers leave sunny mornings
      snow   mm: snowpack at the month's end (snow falls below 0 C, half of
             it between -2 and +2 C, and melts SNOW_DDF mm per degree-day;
             two years spun up from bare ground)
      water  mm: what reaches the soil (rain + snowmelt)
    plus gdd5 (n,): degree-days above 5 C in the year (the days of each
    month scattered around its mean with sd 4 C)."""
    lat = np.asarray(lat, float)
    t_m = month_temps(lat, temp, t_warm, t_cold)
    p_m = month_rain(p_jul, p_jan)
    ra = insolation(lat, tilt)
    jul = ((np.arange(12) >= 3) & (np.arange(12) <= 8))[:, None]
    c_jul = 0.5 if cloud_jul is None else np.asarray(cloud_jul)
    c_jan = 0.5 if cloud_jan is None else np.asarray(cloud_jan)
    cloud = np.where(jul, c_jul, c_jan)
    par = 0.48 * ra * (0.25 + 0.5 * sunshine(cloud)) * MONTH_DAYS[:, None]
    snow_share = np.clip((2.0 - t_m) / 4.0, 0, 1)
    melt_cap = SNOW_DDF * np.maximum(t_m, 0) * MONTH_DAYS[:, None]
    pack = np.zeros(lat.shape)
    snow, water = np.zeros_like(t_m), np.zeros_like(t_m)
    for _ in range(2):
        for m in range(12):
            pack = pack + snow_share[m] * p_m[m]
            melt = np.minimum(pack, melt_cap[m])
            pack = pack - melt
            snow[m], water[m] = pack, (1 - snow_share[m]) * p_m[m] + melt
    # degree-days above 5 C, the days scattered around each month's mean (sd
    # 4 C, as Reeh 1991 for melt): a month averaging 5 C still has warm days
    x = (t_m - 5.0) / 4.0
    cdf = 0.5 * (1 + _erf(x / np.sqrt(2)))
    gdd5 = ((4.0 / np.sqrt(2 * np.pi) * np.exp(-0.5 * x * x) + (t_m - 5.0) * cdf) * MONTH_DAYS[:, None]).sum(0)
    return dict(t=t_m, p=p_m, pet=_pet(ra, t_m), par=par, snow=snow, water=water, gdd5=np.maximum(gdd5, 0.0))


def pet_halves(lat, temp, t_warm, t_cold, tilt: float = 23.4) -> np.ndarray:
    """Potential evaporation in the Apr-Sep and Oct-Mar half-years, each as
    a rate per year like p_jul / p_jan (mm/yr), shape (2, n)."""
    pet_m = pet_months(lat, temp, t_warm, t_cold, tilt)
    return np.stack([2 * pet_m[3:9].sum(0), 2 * (pet_m[:3].sum(0) + pet_m[9:].sum(0))])


def water_balance(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt: float = 23.4, tune: dict | None = None,
                  w=None) -> dict:
    """Where the rain goes: evaporation back to the air, or runoff into
    rivers (mm/yr). Per half-year, so a wet winter and a dry summer
    (Mediterranean) don't cancel out.
      pet       potential evaporation: what a wet surface would evaporate,
                from the sunshine (top-of-atmosphere, by latitude and month)
                and the temperature (Oudin et al. 2005: Ra/lambda*(T+5)/100;
                nothing below -5 C)
      aet       actual evaporation, from the Budyko curve (Fu's equation)
      runoff    rain - aet: what feeds the rivers (Earth: ~35-40% of the
                rain on land)
      aet_half, pet_half  (2, n): aet and pet in the Apr-Sep and Oct-Mar
                half-years (amounts, mm)
    w: Fu's w per cell (default TUNE's budyko_w; vegetation sets it in
    compute). Months are a sine between the coldest and warmest month, peaking in
    July (north) or January (south)."""
    tune = {**TUNE, **(tune or {})}
    pet_jul, pet_jan = pet_halves(lat, temp, t_warm, t_cold, tilt)
    # Each half-year on its own (amounts, mm), then again with what the
    # soil kept from the other half-year's surplus (snowmelt and winter rain
    # still in the ground when summer comes), up to its capacity.
    w, cap = (tune["budyko_w"] if w is None else w), tune["soil_mm"]
    p_s, e_s = 0.5 * np.stack([p_jul, p_jan]), 0.5 * np.stack([pet_jul, pet_jan])
    kept = np.minimum(p_s - budyko(p_s, e_s, w), cap)[::-1]
    aet_h = budyko(p_s + kept, e_s, w)
    precip = p_s.sum(0)
    aet = np.minimum(aet_h.sum(0), precip)
    return dict(pet=e_s.sum(0), aet=aet, runoff=precip - aet, aet_half=aet_h, pet_half=e_s)


SIGMA_MJ = 4.903e-9  # MJ/m2/day per K^4: Stefan-Boltzmann
PSYCHRO = 0.0665  # kPa per C: the psychrometric constant (at sea level)


def open_water_evap(lat, temp, t_warm, t_cold, rh_jul, rh_jan, cloud_jul, cloud_jan, tilt: float = 23.4,
                    tune: dict | None = None) -> np.ndarray:
    """Evaporation from open water (lakes), mm/yr, by Penman's combination
    equation (Penman 1948; as FAO-56 sets it out): the energy the water
    gets, Delta Rn / (Delta + gamma), plus the air's drying power, gamma
    f(u) (e_s - e_a) / (Delta + gamma), with Penman's open-water wind
    function f(u) = 6.43 (1 + 0.536 u2) (MJ/m2/day per kPa; u2 = lake_wind
    m/s at 2 m). The water's temperature is the air's, month by month (a
    sine between the coldest and warmest month); the net radiation Rn is
    the sunshine at the ground (Angstrom: the top of the atmosphere's x
    0.25 + 0.5 x the sunshine share, from the half-year's cloud cover, as
    climate.months) less 6% reflected, less the net long-wave loss (FAO-56:
    warmer, drier and clearer air loses more); e_a is the half-year's
    humidity (rh_jul / rh_jan, %: humidity()). So a humid, cloudy tropical
    lake evaporates ~1500 mm and a desert one ~3000 (Lake Victoria ~1500,
    Lake Nasser ~2700), where the land's potential evaporation (Oudin, on
    the top of the atmosphere's sunshine and the temperature alone) gives
    both about the same (PW-358). None from a frozen lake (months below
    0 C)."""
    tune = {**TUNE, **(tune or {})}
    lat = np.asarray(lat, float)
    t = month_temps(lat, temp, t_warm, t_cold)
    ra = insolation(lat, tilt)
    jul = ((np.arange(12) >= 3) & (np.arange(12) <= 8))[:, None]
    rh = np.clip(np.where(jul, rh_jul, rh_jan) / 100.0, 0.0, 1.0)
    rs = ra * (0.25 + 0.5 * sunshine(np.where(jul, cloud_jul, cloud_jan)))
    es = 0.6108 * np.exp(17.27 * t / (t + 237.3))
    ea = rh * es
    rnl = (SIGMA_MJ * (t + 273.15) ** 4 * (0.34 - 0.14 * np.sqrt(ea))
           * (1.35 * np.clip(rs / np.maximum(0.75 * ra, 1e-9), 0, 1) - 0.35))
    rn = np.maximum((1 - 0.06) * rs - rnl, 0.0)
    delta = 4098.0 * es / (t + 237.3) ** 2
    fu = 6.43 * (1 + 0.536 * tune["lake_wind"])
    e = (delta * rn + PSYCHRO * fu * (es - ea)) / (delta + PSYCHRO) / LATENT  # mm/day
    return (np.where(t > 0, e, 0.0) * MONTH_DAYS[:, None]).sum(0)


# --------------------------------------------------------------------------
# Koppen climate classes (Peel et al. 2007 rules; colours from their map)
# --------------------------------------------------------------------------
KOPPEN = [
    # id, code, name, colour
    (0, "Af", "tropical rainforest", "#0000fe"),
    (1, "Am", "tropical monsoon", "#0077ff"),
    (2, "Aw", "tropical savanna", "#46a9fa"),
    (3, "BWh", "hot desert", "#fe0000"),
    (4, "BWk", "cold desert", "#fe9695"),
    (5, "BSh", "hot steppe", "#f5a301"),
    (6, "BSk", "cold steppe", "#ffdb63"),
    (7, "Csa", "Mediterranean, hot summer", "#ffff00"),
    (8, "Csb", "Mediterranean, warm summer", "#c6c700"),
    (9, "Csc", "Mediterranean, cool summer", "#969600"),
    (10, "Cwa", "subtropical, dry winter", "#96ff96"),
    (11, "Cwb", "subtropical highland, dry winter", "#63c764"),
    (12, "Cwc", "subpolar highland, dry winter", "#329633"),
    (13, "Cfa", "humid subtropical", "#c6ff4e"),
    (14, "Cfb", "oceanic", "#66ff33"),
    (15, "Cfc", "subpolar oceanic", "#33c701"),
    (16, "Dsa", "continental, dry hot summer", "#ff00fe"),
    (17, "Dsb", "continental, dry warm summer", "#c600c7"),
    (18, "Dsc", "subarctic, dry summer", "#963295"),
    (19, "Dsd", "subarctic, dry summer, severe winter", "#966495"),
    (20, "Dwa", "continental, dry winter, hot summer", "#abb1ff"),
    (21, "Dwb", "continental, dry winter, warm summer", "#5a77db"),
    (22, "Dwc", "subarctic, dry winter", "#4c51b5"),
    (23, "Dwd", "subarctic, dry winter, severe", "#320087"),
    (24, "Dfa", "humid continental, hot summer", "#00ffff"),
    (25, "Dfb", "humid continental, warm summer", "#38c7ff"),
    (26, "Dfc", "subarctic", "#007e7d"),
    (27, "Dfd", "subarctic, severe winter", "#00455e"),
    (28, "ET", "tundra", "#b2b2b2"),
    (29, "EF", "ice cap", "#686868"),
    (30, "-", "sea", "#1d3f6e"),
]
SEA_CLASS = 30


def koppen(elev, temp, t_warm, t_cold, p_ann, p_jul, p_jan, lat, ice=None):
    """Koppen class per cell, from the twelve months the climate implies
    (month_temps, month_rain: as climate.months)."""
    lat = np.asarray(lat, float)
    north = lat >= 0
    p_m = month_rain(p_jul, p_jan)
    t_m = month_temps(lat, temp, t_warm, t_cold)
    # the local summer half-year: Apr-Sep in the north, Oct-Mar in the south
    jul = ((np.arange(12) >= 3) & (np.arange(12) <= 8))[:, None]
    summer = np.where(north[None, :], jul, ~jul)
    big = 1e9
    dry_s, wet_s = np.where(summer, p_m, big).min(0), np.where(summer, p_m, -big).max(0)
    dry_w, wet_w = np.where(summer, big, p_m).min(0), np.where(summer, -big, p_m).max(0)
    driest = p_m.min(0)
    p_sum = np.where(summer, p_m, 0.0).sum(0)
    p_win = np.where(summer, 0.0, p_m).sum(0)
    P, T = p_ann, temp
    m10 = (t_m >= 10).sum(0)  # months at 10 C or more
    out = np.full(len(elev), -1)

    def put(mask, cid):
        sel = mask & (out < 0)
        out[sel] = cid[sel] if np.ndim(cid) else cid

    sea = ~is_land(elev, ice)  # (a bed below sea level under grounded ice is land)
    out[sea] = SEA_CLASS
    if ice is not None:
        put(ice > 0, 29)
    put(t_warm < 0, 29)
    put(t_warm < 10, 28)
    summer_share = p_sum / np.maximum(p_sum + p_win, 1e-9)
    pth = 20 * T + np.where(summer_share >= 0.7, 280, np.where(summer_share >= 0.3, 140, 0))
    hot = T >= 18
    put(P < 0.5 * pth, np.where(hot, 3, 4))
    put(P < pth, np.where(hot, 5, 6))
    trop = t_cold >= 18
    put(trop & (driest >= 60), 0)
    put(trop & (driest >= 100 - P / 25), 1)
    put(trop, 2)
    s_ = (dry_s < 40) & (dry_s < wet_w / 3)
    w_ = (dry_w < wet_s / 10)
    third = np.where(t_warm >= 22, 0, np.where(m10 >= 4, 1, np.where(t_cold < -38, 3, 2)))
    third_c = np.minimum(third, 2)  # C climates have no 'd'
    temperate = t_cold > -3
    put(temperate & s_, 7 + third_c)
    put(temperate & w_, 10 + third_c)
    put(temperate, 13 + third_c)
    put(s_, 16 + third)
    put(w_, 20 + third)
    put(np.ones(len(elev), bool), 24 + third)
    return out


# --------------------------------------------------------------------------
# Biomes: a rough Whittaker diagram (mean annual temperature x rainfall)
# --------------------------------------------------------------------------
BIOMES = [
    # id, name, ascii char, colour
    (0, "deep ocean", "~", "#1d3f6e"),
    (1, "shallow sea", "-", "#3a6ea5"),
    (2, "sea ice", "=", "#d8e6ef"),
    (3, "lake", "o", "#4f8fcf"),
    (4, "ice sheet", "I", "#f4f7fa"),
    (5, "tundra", "t", "#9aa58a"),
    (6, "boreal forest", "B", "#3f6b4d"),
    (7, "cold desert", "c", "#b7ad8f"),
    (8, "temperate grassland", "g", "#a9b964"),
    (9, "temperate forest", "F", "#4d8a3a"),
    (10, "temperate rainforest", "R", "#2f6e4a"),
    (11, "hot desert", "d", "#e0c68a"),
    (12, "savanna", "s", "#c2b553"),
    (13, "tropical seasonal forest", "S", "#6a9a2f"),
    (14, "tropical rainforest", "J", "#2a7a2a"),
    (15, "alpine / bare rock", "^", "#8b8178"),
]


def biomes(elev: np.ndarray, temp: np.ndarray, precip: np.ndarray,
           lake: np.ndarray | None = None, ice: np.ndarray | None = None) -> np.ndarray:
    t, p = temp, precip
    b = np.full(len(elev), -1)
    land = is_land(elev, ice)

    def land_rule(mask, bid):
        sel = land & mask & (b < 0)
        b[sel] = bid

    if lake is not None:
        b[land & lake] = 3
    land_rule(t < -9, 4)
    land_rule((elev > 3200) & (t < 3), 15)
    land_rule(t < -2, 5)
    land_rule((t < 6) & (p < 250), 7)
    land_rule(t < 6, 6)
    land_rule((t < 18) & (p < 300), 7)
    land_rule((t < 18) & (p < 700), 8)
    land_rule((t < 18) & (p < 1800), 9)
    land_rule(t < 18, 10)
    land_rule(p < 350, 11)
    land_rule(p < 1000, 12)
    land_rule(p < 1900, 13)
    land_rule(np.ones_like(land), 14)

    sea = ~land
    b[sea & (t < -10)] = 2
    b[sea & (b < 0) & (elev < -1500)] = 0
    b[sea & (b < 0)] = 1
    return b


def compute(grid: Grid, elev: np.ndarray, dT: float = 0.0, tilt: float = 23.4,
            ice: np.ndarray | None = None, tune: dict | None = None, melt: np.ndarray | None = None,
            moc_start: dict | None = None, veg: dict | None = None, orbit_dt: np.ndarray | None = None,
            ice_air: np.ndarray | None = None, rain_start: dict | None = None,
            ice_cold: np.ndarray | None = None) -> dict:
    """The whole climate for one moment: elevation (m above the current sea
    level; <= 0 is sea unless grounded ice is on it: geo.is_land), the global
    temperature offset dT from today's Earth, axial tilt and land ice (m).
    melt: fresh water from shrinking ice sheets,
    m/yr per cell (on land it runs off to the sea; see ocean.py), none in
    the main run; moc_start: an earlier call's moc_state, to start the
    overturning from (see ocean.solve). Returns a dict of per-cell arrays:
      temp, t_warm, t_cold   C: annual mean, warmest and coldest month
      t_jul, t_jan           C: July and January (each the warmest or the coldest month,
                             whichever it is there: world.seasons)
      precip, p_jul, p_jan   mm/yr: annual, and the rate in each half-year
      koppen                 KOPPEN id
      sst                    C: sea-surface temperature (annual)
      sst_jul, sst_jan       C: ... in July and January (the peak months of the sea's
                             seasonal swing, as t_warm / t_cold; not below freezing)
      dew_jul, dew_jan       C: dew point of the air near the ground, July / January
                             half-year (humidity())
      rh_jul, rh_jan         %: relative humidity, July / January half-year
      cloud_jul, cloud_jan   0..1: cloud cover, July / January half-year (clouds())
      shade_jul, shade_jan   0..1: the cloud as the day's light sees it (shade(): the
                             convective clouds count at cloud_sun_conv); what the
                             plants' light (months' cloud_jul / cloud_jan) takes
      sun_jul, sun_jan       hours/day of bright sunshine, July / January half-year
                             (day_hours x sunshine())
      wind_jul, wind_jan     tangent vectors, ~1 = a steady trade wind
      current                tangent vectors of the surface ocean currents
      jet_jul, jet_jan       tangent vectors, m/s: the upper-level wind (jet stream)
      pet, aet, runoff       mm/yr: potential and actual evaporation, and what runs
                             off into rivers (0 at sea; see water_balance)
      lake_evap              mm/yr: evaporation from open water (lakes; open_water_evap; 0 at sea)
      sss                    psu: sea-surface salinity (S0 on land)
      density, density_winter  kg/m3: surface sea water, annual and coldest month
      overturning            Sv per cell: deep water sinking there
      moc_inflow             Sv per cell width: the warm surface inflow feeding the sinking
      moc_heat               C: how much the overturning warms (cools) the sea surface
      freshwater             m/yr: net fresh water into the sea (rain + rivers + ice and
                             meltwater - evaporation), global mean taken off
      sea_evap               mm/yr: evaporation from the sea
      sea_ice_growth         m: sea ice frozen per winter
      upwelling              C: how much coastal and equatorial upwelling cools the sea
                             surface where it wells up (0 on land; upwelling_cooling)
    and ground: (t_warm, t_cold, temp) of the bare ground under the ice (ice_surface
    turns them back into the ice's), moc_sites: a list of dicts per sinking site (lat, lon, sv, drho,
    area_km2, heat_pw) and moc_state, a dict to pass on as moc_start, and
    rain_state, the rain kernel's end state to pass on as rain_start (a
    run's next update starts its rain from it, PW-387; default: from cold,
    as worlds and the Earth checks do).
    veg: the vegetation's feedbacks (vegetation.feedback: woody and deep-
    rooted cover, LAI, albedo, snow masking; per cell, land only), or None
    for land with an Earth-like average cover: plants give more of the rain
    back to the air (Budyko w, which the rain kernel recycles) and set the surface's
    albedo (see vegetation_feedbacks).
    orbit_dt: an orbit's temperature anomaly (C) per cell and month (n x
    12, month 0 = April; timezoom.orbit_anomaly), added to the air's
    warmest / coldest month and annual mean before the rain (a finished
    time-zoom frame: precession and eccentricity, PW-198).
    ice_air: the land ice (m) whose own cold air the winds carry (default
    ice; the time zoom passes its ice here with elevation as the ice's
    surface and no ice, since its own surface rule takes the ice's year).
    ice_cold: the share (0..1) of each ice cell's summer its surface stays
    frozen (icemass.cold_share; None: all of it), the share of its air that
    is the sheet's cold air (icemass.air_mass; the time zoom's).
    Order: a first guess of temperatures by latitude, height and distance
    from the sea -> seasonal winds from the land-sea contrast -> ocean
    currents and sea-surface temperature -> air temperatures carried by the
    winds -> rain in each half-year -> wet ground cools the summer ->
    salinity and the overturning (ocean.py), whose heat is then added to
    the sea and air temperatures."""
    tune = {**TUNE, **(tune or {})}
    n = grid.n
    ice = np.zeros(n) if ice is None else ice
    land = is_land(elev, ice)  # (a bed below sea level under grounded ice is land, PW-307)
    ocean = ~land
    surf = elev + ice
    north = grid.lat >= 0
    sgn = np.where(north, 1, -1)
    tilt_adj = (tilt - 23.4) * 0.3  # more tilt: milder poles, slightly cooler tropics
    eq, pole = 27.8 + 0.5 * dT - 0.3 * tilt_adj, -10.4 + 1.5 * dT + tilt_adj
    temp0 = temperature(grid, surf, eq, pole)
    # the latitude's sea temperature; below freezing, the air over sea ice
    t_sea_air = sea_temperature(grid, eq - 0.8, pole + 2.9)
    t_sea = np.maximum(t_sea_air, FREEZE)
    s = season_strength(grid, tilt)
    # The sea's seasonal swing (_sea_half): its own, under the sun's
    # seasons, plus a share of the land's, where the air over it came off
    # land (land_air: the share of it that did, within ~air_km_w on the
    # prevailing winds).
    h = _geom(grid)["h"]
    land_air = carry(grid, wind(grid, 0.0), land.astype(float), np.where(ocean, np.exp(-h / tune["air_km_w"]), 0.0),
                     4 * tune["air_km_w"], 0.25)
    sea_half, sea_half_w = _sea_half(grid.lat, tilt, s, land_air, tune, t_sea)
    # The land's air takes more of the water's heat in winter than it gives
    # it in summer, so the water's year is that much colder: hk x half the
    # difference, a cooling at the surface the currents carry like upwelling's
    chill = 0.5 * tune["hk"] * (sea_half_w - sea_half)

    # Winds for each half-year (Apr-Sep 'jul', Oct-Mar 'jan'). Rain is a
    # half-year mean, so the winds and rain use the half-years' mean
    # conditions: a sine averages 2/pi (hk) of its peak.
    hk = tune["hk"]
    shift = hk * tune["belt_shift"] * tilt / 23.4
    warm0, cold0 = seasons(grid, elev, temp0, tilt, land)
    lift = LAPSE * np.maximum(surf, 0)  # back to sea level, for pressure
    t_sl0 = np.where(ocean, t_sea_air, 0.5 * (warm0 + cold0) + lift)
    half_jul = np.where(ocean, np.where(north, sea_half, sea_half_w), 0.5 * (warm0 - cold0))
    half_jan = np.where(ocean, np.where(north, sea_half_w, sea_half), 0.5 * (warm0 - cold0))
    t_sl0 = t_sl0 - np.where(ocean, chill, 0.0)
    t_sl_jul, t_sl_jan = t_sl0 + sgn * hk * half_jul, t_sl0 - sgn * hk * half_jan
    # the westerlies by season and hemisphere, from the first guess's contrast (westerly_belt); the land's
    # lows and highs as deep as its air column's warmth (low_column)
    col = low_column(grid, land, tune)
    b_jul, b_jan = westerly_belt(grid, t_sl_jul, t_sl_jan)
    w_jul, _ = monsoon_wind(grid, t_sl_jul, shift, tune["monsoon"], tune["big"], tune["big_km"], None, b_jul, col)
    w_jan, _ = monsoon_wind(grid, t_sl_jan, -shift, tune["monsoon"], tune["big"], tune["big_km"], None, b_jan, col)
    v_jul, v_jan = deflect(grid, w_jul, surf, tune), deflect(grid, w_jan, surf, tune)
    v_ann = 0.5 * (v_jul + v_jan)
    # the rain's wind: the water vapour rides above the polar inversion, not
    # in the shallow cold air draining off the poles (polar_drift, PW-332)
    vq_jul = deflect(grid, w_jul - polar_drift(grid, shift), surf, tune)
    vq_jan = deflect(grid, w_jan - polar_drift(grid, -shift), surf, tune)

    cur, away = currents(grid, ocean, v_ann, tune)

    raw0, _ = sea_surface(grid, ocean, t_sea, v_ann, upwelling=tune["coast_up"], eq_upwelling=tune["eq_up"],
                          tune=tune, cur=cur, away=away, chill=chill)

    def sst_of(share, t_in):  # (with the overturning's inflow)
        t, _ = sea_surface(grid, ocean, t_sea, v_ann, tune=tune, cur=cur, away=away, share=share, t_in=t_in,
                           base=raw0)
        return np.maximum(t, FREEZE)

    sst0 = sst = np.maximum(raw0, FREEZE)
    v_sum = np.where(north[:, None], v_jul, v_jan)  # each hemisphere's summer wind
    v_win = np.where(north[:, None], v_jan, v_jul)
    lift = LAPSE * np.maximum(surf, 0)
    # the air over land ice is the sheet's own (icemass.air_mass; ice_air: the ice whose air it is, by
    # default `ice`; the time zoom's elevation already has its ice on, and it passes that ice here)
    ice_air = np.where(land, ice, 0.0) if ice_air is None else np.where(land, ice_air, 0.0)
    from .icemass import air_mass
    damp_air = air_mass(grid, ice_air, cold=ice_cold) if (ice_air > 1).any() else np.zeros(n)
    air = dict(grid=grid, ocean=ocean, temp0=temp0, lift=lift, t_sea_air=t_sea_air, t_sea=t_sea, s=s,
               sea_half=sea_half, v_sum=v_sum, v_win=v_win, tune=tune, damp_air=damp_air, half_w=sea_half_w)
    t_warm, t_cold, temp, open_w = _orbit(_air_temps(sst=sst, **air), orbit_dt, north)

    # rain in each half-year, from its mean conditions
    tm = 0.5 * (t_warm + t_cold)
    dt = hk * (np.where(north, t_warm, t_cold) - tm)
    sum_half = _summer_half(sst, sea_half, sea_half_w)
    sst_jul = np.maximum(sst + hk * np.where(north, sum_half, -sea_half_w), FREEZE)
    sst_jan = np.maximum(sst + hk * np.where(north, -sea_half_w, sum_half), FREEZE)
    # the jet stream over each half-year's temperatures steers its storms
    jets, tracks = [], []
    for t_s in season_temps(grid, surf, t_warm, t_cold, hk):
        j, baro = jet_stream(grid, t_s, tune)
        jets.append(j)
        tracks.append(storm_track(grid, j, baro, tune))
    s_in = [_season_inputs(grid, elev, tm + dt, sst_jul, vq_jul, shift, t_sl_jul, tune, tracks[0], surf, ocean),
            _season_inputs(grid, elev, tm - dt, sst_jan, vq_jan, -shift, t_sl_jan, tune, tracks[1], surf, ocean)]
    fb = vegetation_feedbacks(land & (ice <= 0), veg, tune)
    wet = np.exp(RAIN_PER_C * dT)  # a warmer world is a wetter one
    # The air takes up water from the open sea and from the land as much as
    # the land's water balance evaporates (on these first-pass temperatures;
    # the kernel's own mm/yr, for that and its wet-cool / dry-hot showers,
    # use the same global mean as the rain). Pack ice is no lid: its leads
    # and polynyas keep a share `leads` of a frozen sea open, and the very
    # cold, dry air over them takes up water fast (PW-308).
    open_y = ocean_mod.open_share(sst, np.minimum(t_sea_air - t_sea, 0.0), sea_half_w)
    pet = pet_halves(grid.lat, temp, t_warm, t_cold, tilt)
    # In the summer half the air that came off land (land_air) is warmer
    # than the sea it crosses (that air is what warms a coastal sea beyond
    # its own swing, _sea_half): it lies stable over the cooler water, which
    # can't stir its vapour up into it, so the sea fills only the rest of
    # the air (PW-578). In winter the land's air is colder than the water,
    # and the sea fills it fast.
    open_air = np.where(ocean, open_y + tune["leads"] * (1.0 - open_y), 1.0)
    calm = np.where(ocean, 1.0 - land_air, 1.0)
    open_k = np.stack([open_air * np.where(north, calm, 1.0), open_air * np.where(north, 1.0, calm)])
    (r_jul, r_jan), (e_jul, e_jan), (q_jul, q_jan), rain_state = rain(
        grid, elev, s_in, {**tune, "mean_mm": tune["mean_mm"] * wet}, pet, fb["w"], open_k, ocean, rain_start)
    scale = tune["mean_mm"] * wet / max(0.5 * (r_jul + r_jan).mean(), 1e-12)
    p_jul, p_jan = np.clip(r_jul * scale, 0, 8000), np.clip(r_jan * scale, 0, 8000)
    precip = 0.5 * (p_jul + p_jan)
    sea_evap = np.where(ocean, 0.5 * (e_jul + e_jan) * scale, 0.0)
    fin = dict(land=land, north=north, p_jul=p_jul, p_jan=p_jan, ice=ice, ocean=ocean, tune=tune,
               cover=_sheet_cover(grid, np.where(land, ice, 0.0), ice_air, ice_cold), lat=grid.lat, tilt=tilt, fb=fb)
    qm_jul, qm_jan = (vapour_mixed(grid, q, d_["qs"], d_["t_air"], tune) for q, d_ in zip((q_jul, q_jan), s_in))
    (cloud_jul, sun_jul), (cloud_jan, sun_jan) = clouds(grid, elev, s_in, [qm_jul, qm_jan], [p_jul, p_jan], tune,
                                                        ocean)
    # The summer's surface energy split (_summer_split): with the rain, the
    # clouds and the evaporation known, the land's summer air is warmed by
    # the sensible heat the ground has left, so cloudy, wet summers stay
    # cooler and sunny, dry ones get hotter. (The rain came before, on the
    # first pass's temperatures.)
    wb0 = water_balance(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, tune, fb["w"])
    air["d_sum"] = np.where(land & (ice <= 0), _summer_split(grid.lat, tilt, north, wb0["aet_half"],
                                                             wb0["pet_half"], np.where(north, cloud_jul, cloud_jan),
                                                             tune), 0.0)
    t_warm, t_cold, temp, open_w = _orbit(_air_temps(sst=sst, **air), orbit_dt, north)
    t_warm, t_cold, temp, ground, jul_warm = _land_finish(t_warm, t_cold, temp, **fin)
    wb = water_balance(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, tune, fb["w"])

    # The deep ocean's overturning (ocean.py): fresh water in and out of the
    # sea -> salinity -> density -> sinking where the water is densest ->
    # warm surface water flowing in to replace it, carrying heat poleward.
    # It needs the rain, which needs the sea temperatures: the overturning's
    # warmth is added to the air temperatures afterwards (the rain doesn't
    # see it).
    ice_m = np.where(ocean, ocean_mod.ice_growth(0.5 * (t_warm + t_cold), 0.5 * (t_warm - t_cold)), 0.0)
    # only where the sea freezes over in winter; under year-round pack ice
    # little new ice forms (thick ice insulates the water; it grows in leads)
    ice_m *= (1 - open_w) * (0.2 + 0.8 * np.clip(open_y / 0.25, 0, 1))
    # Where the winter wind blows off the coast, it pushes the new ice out to
    # sea as it forms (a polynya): it all drifts away, to melt far off.
    near = np.linalg.norm(away, axis=1) > 0
    off = np.where(near & ocean, np.clip((v_win * away).sum(1) / 0.3, 0, 1), 0.0)
    export = tune["ice_export"] + (1 - tune["ice_export"]) * off
    fw = ocean_mod.freshwater(grid, ocean, surf, precip, sea_evap, np.where(land, wb["runoff"], 0.0), ice_m, melt,
                              tune, export)
    oc = ocean_mod.solve(grid, ocean, sst_of, sst0, t_sea, cur, fw["total"], ice_m, sea_half_w, tune, moc_start,
                         np.where(ocean, np.minimum(t_sea_air - t_sea, 0.0), 0.0), -elev)
    half_w = sea_half_w
    if oc["sites"]:
        sst = oc["sst"]
        # where the surface water is the overturning's deep inflow, its winter cools less (ocean.winter_half)
        half_w = air["half_w"] = ocean_mod.winter_half(sea_half_w, oc["share"], tune)
        t_warm, t_cold, temp, _ = _orbit(_air_temps(sst=sst, **air), orbit_dt, north)
        t_warm, t_cold, temp, _, _ = _land_finish(t_warm, t_cold, temp, **fin)
    # A shelf sea's water is the air's more than the currents' (_shelf_air): the North Sea's and the Baltic's
    # winters are the Atlantic air's that crossed Britain and Denmark, the Yellow Sea's the monsoon's off China.
    # (After the overturning, like its warmth: the rain and the sinking don't see it.)
    sst = _shelf_air(grid, ocean, sst, t_sea, v_ann, -elev, _open_air(t_warm + lift, t_cold + lift), tune)
    # The wind belts follow the air masses (front_shift): with the finished
    # air, a warm polar sea pulls the westerlies north over it and a cold
    # continent lets the polar air south. The land-sea winds stay the first
    # guess's (t_sl_jul / jan); the air is carried on the new winds. (The rain
    # came before and keeps the first guess's winds, as it doesn't see the
    # overturning.)
    t_sj, t_sn = season_temps(grid, surf, t_warm, t_cold, hk)
    f_jul, f_jan = front_shift(grid, t_sj), front_shift(grid, t_sn)
    # (and the westerlies' strength from the finished air's contrast)
    b_jul, b_jan = westerly_belt(grid, t_sj, t_sn)
    w_jul, _ = monsoon_wind(grid, t_sl_jul, shift, tune["monsoon"], tune["big"], tune["big_km"], f_jul, b_jul, col)
    w_jan, _ = monsoon_wind(grid, t_sl_jan, -shift, tune["monsoon"], tune["big"], tune["big_km"], f_jan, b_jan, col)
    v_jul, v_jan = deflect(grid, w_jul, surf, tune), deflect(grid, w_jan, surf, tune)
    air["v_sum"] = np.where(north[:, None], v_jul, v_jan)
    air["v_win"] = np.where(north[:, None], v_jan, v_jul)
    t_warm, t_cold, temp, _ = _orbit(_air_temps(sst=sst, **air), orbit_dt, north)
    t_warm, t_cold, temp, ground, jul_warm = _land_finish(t_warm, t_cold, temp, **fin)
    wb = water_balance(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, tune, fb["w"])
    k = koppen(elev, temp, t_warm, t_cold, precip, p_jul, p_jan, grid.lat, ice)
    wb["runoff"] = np.where(land, wb["runoff"], 0.0)
    # July / January: the sea's peak months (where it is iced over most of
    # the year, the summer's heat goes into melting the ice: a smaller
    # swing), and the half-years' humidity
    swing = sgn * np.clip((sst - FREEZE) / 4.0, 0.1, 1.0)
    # (July is the north's summer and the south's winter)
    sum_half = _summer_half(sst, sea_half, half_w)
    sst_m = (np.maximum(sst + swing * np.where(north, sum_half, half_w), FREEZE),
             np.maximum(sst - swing * np.where(north, half_w, sum_half), FREEZE))
    tm = 0.5 * (t_warm + t_cold)
    dt = hk * (np.where(north, t_warm, t_cold) - tm)
    (dew_jul, rh_jul), (dew_jan, rh_jan) = humidity(qm_jul, tm + dt, tune), humidity(qm_jan, tm - dt, tune)
    day_jul, day_jan = day_hours(grid.lat, tilt)
    # lakes: Penman's open water, on the clouds and the air's humidity (PW-358)
    wb["lake_evap"] = np.where(land, open_water_evap(grid.lat, temp, t_warm, t_cold, rh_jul, rh_jan, cloud_jul,
                                                     cloud_jan, tilt, tune), 0.0)

    def reground(ice_new):
        """The bare ground's (t_warm, t_cold, temp), as `ground`, under another land ice's carried air (its own
        air mass, icemass.air_mass, carried on these winds), the rest of this climate held: its sea, rain,
        clouds and summer energy split (PW-1050: the run's ice settles with its own air within an update)."""
        a = np.where(land, ice_new, 0.0)
        damp = air_mass(grid, a, cold=ice_cold) if (a > 1).any() else np.zeros(n)
        t = _orbit(_air_temps(sst=sst, **{**air, "damp_air": damp}), orbit_dt, north)
        return _land_finish(*t[:3], **fin)[3]

    return dict(reground=reground, temp=temp, t_warm=t_warm, t_cold=t_cold, t_jul=np.where(jul_warm, t_warm, t_cold),
                t_jan=np.where(jul_warm, t_cold, t_warm), precip=precip, p_jul=p_jul, p_jan=p_jan, koppen=k,
                sst=sst, sst_jul=sst_m[0], sst_jan=sst_m[1], dew_jul=dew_jul, dew_jan=dew_jan, rh_jul=rh_jul,
                rh_jan=rh_jan, cloud_jul=cloud_jul, cloud_jan=cloud_jan, shade_jul=shade(sun_jul),
                shade_jan=shade(sun_jan), sun_jul=day_jul * sun_jul,
                sun_jan=day_jan * sun_jan, wind_jul=v_jul, wind_jan=v_jan, current=cur, jet_jul=jets[0], jet_jan=jets[1], **wb,
                sss=oc["sss"], density=oc["density"], density_winter=oc["density_w"], overturning=oc["sinking"],
                moc_inflow=oc["inflow"], moc_heat=np.where(ocean, sst - sst0, 0.0), freshwater=fw["total"],
                sea_evap=sea_evap, sea_ice_growth=ice_m,
                upwelling=np.where(ocean, upwelling_cooling(grid, ocean, v_ann, away, tune["coast_up"],
                                                            tune["eq_up"]), 0.0),
                moc_sites=oc["sites"],
                moc_state=oc["state"], rain_state=rain_state, ground=ground)


def _orbit(temps, orbit_dt, north):
    """_air_temps' (t_warm, t_cold, temp, open water) with an orbit's monthly
    anomaly (n x 12, month 0 = April: July is 3, January 9) added."""
    if orbit_dt is None:
        return temps
    t_warm, t_cold, temp, *rest = temps
    d = np.asarray(orbit_dt, float)
    jul, jan = d[:, 3], d[:, 9]
    return (t_warm + np.where(north, jul, jan), t_cold + np.where(north, jan, jul), temp + d.mean(1), *rest)


def _air_temps(grid, ocean, sst, temp0, lift, t_sea_air, t_sea, s, sea_half, v_sum, v_win, tune, damp_air,
               half_w=None, d_sum=None):
    """Each place takes on the temperature of the air the wind brings it.
    Air over land drifts toward the land's own temperature for the
    season (land holds little heat: hot summers, cold winters) over a few
    hundred km; air over open sea takes on the water's temperature (mild
    winters, cool summers). So in the westerlies the west coasts get sea
    air (Ireland, Vancouver), the east coasts and interiors land air, and
    where the winter wind blows from the north (the east sides of
    continents) it brings the cold with it. In winter the air is carried
    over the sea too (_winter_air): air off a continent warms over open
    water and stays cold over a frozen sea, which moderates little (only
    the heat conducted up through the ice and its open water).
    The sea's summer air is the water's summer, less the winter's freezing
    deficit (_summer_half: the heat goes into melting the ice), and the
    latitude's would-be sea below freezing, but never below freezing:
    melting ice holds the air over it near 0 C (PW-335). A land ice sheet makes its own cold, bright air:
    the air over its ice has its summer warmth damped by SUMMER_DAMP x
    damp_air (icemass.air_mass: how much of the air around is the sheet's),
    and the winds carry it on (katabatic outflow onto its margins, ice
    shelves and the land beyond; PW-336).
    half_w: the sea's winter half-swing, where it differs from its summer
    one sea_half (ocean.winter_half: less where the overturning's deep
    inflow makes up the surface water).
    Returns (t_warm, t_cold, temp, open water in winter 0..1)."""
    from .icemass import SUMMER_DAMP
    half_w = sea_half if half_w is None else half_w
    half_l = tune["continental"] * s + 0.3  # land left to itself
    t_land = temp0 + lift  # (carried at sea level; heights are taken off after)
    frozen = np.minimum(t_sea_air - t_sea, 0)  # how far below freezing the latitude's sea would be
    sea_sum = np.maximum(sst + frozen + _summer_half(sst, sea_half, half_w), FREEZE)
    h = _geom(grid)["h"]
    # The summer air relaxes toward the land's summer in time (sum_tau),
    # not over a fixed distance: it reaches U x sum_tau inland (PW-581),
    # so a strong wind carries the sea's summer further onto the land.
    # d_sum: the summer's surface energy split (_summer_split).
    km_s = _summer_km(v_sum, h, tune)
    # The land's own swing (half_l, a big continent's) is reached only
    # where the land around is wide: _summer_fetch builds it from the sea air
    # that arrives (PW-573). The share of the air that is an ice sheet's own
    # (SUMMER_DAMP x damp_air) stays the sheet's: its annual mean, as before.
    bare = _summer_fetch(grid, ocean, v_sum, sea_sum, t_land + half_l, h, tune)
    land_full = bare - SUMMER_DAMP * damp_air * (bare - t_land)
    land_sum = land_full + (0.0 if d_sum is None else d_sum)
    eq_s = np.where(ocean, sea_sum, land_sum)
    k_s = np.where(ocean, 0.0, np.exp(-h / km_s))
    t_warm = carry(grid, v_sum, (1 - k_s) * eq_s, k_s, 4 * float(np.max(km_s)), 0.25)
    t_cold, open_w = _winter_air(grid, ocean, sst, t_land, half_l, half_w, sea_sum, v_win, h, tune, lift)
    # right at a coast the sea's air mixes in anyway (sea breezes, fog; on land)
    sea_n, open_n = _nbr_mean(grid, ocean.astype(float)), _nbr_mean(grid, open_w)
    c_s, c_w = tune["coast"] * sea_n, np.where(ocean, 0.0, tune["coast"] * open_n)
    sea_s = _nbr_mean(grid, np.where(ocean, eq_s, 0.0)) / np.maximum(sea_n, 1e-9)
    sea_w = _nbr_mean(grid, np.where(ocean, np.maximum(sst - half_w, FREEZE), 0.0) * open_w) / np.maximum(
        open_n, 1e-9)
    t_warm = (1 - c_s) * t_warm + c_s * sea_s - lift
    t_cold = (1 - c_w) * t_cold + c_w * sea_w - lift
    # over the sea the summer is the water's (sea_sum); the winter is the air
    # the wind brings over it (_winter_air)
    t_warm = np.where(ocean, sea_sum, t_warm)
    temp = 0.5 * (t_warm + t_cold)
    return t_warm, t_cold, temp, open_w


RHO_C_SEA = 4.1e6  # J/m3 per C: sea water's heat capacity
RHO_C_AIR = 1.2 * 1005.0  # J/m3 per C: air's, near the ground
YEAR_S = 365.25 * 86400.0
SEA_ALBEDO = 0.06
SUN_SURFACE = 0.5  # share of the top-of-atmosphere sunshine that reaches the ground (Angstrom's 0.25 + 0.5 x
# sunshine, at half the day sunny)


def _open_air(t_warm, t_cold):
    """The year's mean of the air as a sea's water feels it: the months'
    sine between t_cold and t_warm, but no colder than freezing, since the
    sea's ice keeps the colder air off the water."""
    m, amp = 0.5 * (t_warm + t_cold), np.maximum(0.5 * (t_warm - t_cold), 1e-6)
    th = np.arcsin(np.clip((FREEZE - m) / amp, -1.0, 1.0))
    return FREEZE + ((m - FREEZE) * (np.pi - 2 * th) + 2 * amp * np.cos(th)) / (2 * np.pi)


def _shelf_air(grid, ocean, sst, t_eq, v, depth, t_air, tune):
    """The sea temperature on the shelves (PW-592). The currents carry the
    water's warmth (or cold) in a layer moc_layer_m deep (the overturning's
    inflow, the gyres' thermocline), and the shelf break steers them along
    it (geostrophic flow follows the depth contours), so on a shelf only
    depth / moc_layer_m of their anomaly (sst - t_eq) comes onto it. The rest
    of a shallow column's temperature is the air's: it takes on the air the
    wind brings, which is the land's (t_air: its annual air at sea level as
    the water feels it, _open_air) where that came off land, and the
    water's own over the sea it crossed. So the
    North Sea gets the Atlantic air that crossed Britain instead of the
    latitude's mean, and the Yellow Sea the monsoon air off China; the deep
    sea next to them is left as it was. Not kept to each band's mean: the
    heat is the air's, not moved round the ocean."""
    anom = np.where(ocean, sst - t_eq, 0.0)
    f = np.where(ocean, np.clip(1.0 - np.maximum(depth, 0.0) / tune["moc_layer_m"], 0.0, 1.0), 0.0)
    a = np.where(ocean, (1.0 - f) * anom, t_air - t_eq)
    z = carry(grid, v, a, f, 4 * tune["air_km_w"], 0.25)
    return np.where(ocean, np.maximum(t_eq + z, FREEZE), sst)


def _sea_half(lat, tilt, s, land_air, tune, t_sea=None):
    """The sea's seasonal half-swing (C): its own plus a share of the land's.
    Its own: the seasons' sunshine (half the year's swing of the monthly
    mean at the ground, after the sea's albedo) into the mixed layer
    (brine_m deep), a heat capacity rho c h omega (~41 W/m2 per C at 50 m)
    against which the loss to space (ice_b) hardly counts: ~1-2.5 C, more
    toward the poles, and none at the equator. The land's: where the air
    over the sea came off land (land_air), it pulls the water toward the
    land's own swing (continental x season strength) by the air-sea
    exchange against the mixed layer's heat capacity. In winter the land's
    air is colder than the water: heated from below, it churns, and takes
    the water's heat at open_b (c = open_b / (open_b + rho c h omega) ~0.42).
    In summer it is warmer than the water and lies stable over it (as it
    does for the vapour, PW-578): no turbulence carries its heat down, only
    its longwave (4 sigma T^3 at the water's temperature t_sea, ~5 W/m2 per
    C: c ~0.12). So a sea downwind of land swings far more than an ocean
    the westerlies cross without meeting land, and a bay inside a continent
    most of all, mostly in its winter (PW-595). (The winter air's own cold
    over the sea is carried separately: _winter_air.)
    Returns (summer half-swing, winter half-swing)."""
    ra = insolation(lat, tilt) * (1e6 / 86400.0)  # W/m2, (12, n)
    cap = RHO_C_SEA * tune["brine_m"] * 2 * np.pi / YEAR_S
    own = (1 - SEA_ALBEDO) * SUN_SURFACE * 0.5 * (ra.max(0) - ra.min(0)) / np.hypot(cap, tune["ice_b"])
    c = tune["open_b"] / (tune["open_b"] + cap)
    t = 15.0 if t_sea is None else t_sea
    lw = 4 * SIGMA_SB * (np.maximum(t, FREEZE) + 273.15) ** 3
    c_s = lw / (lw + cap)
    land = tune["continental"] * s * land_air
    return own + c_s * land, own + c * land


SIGMA_SB = 5.67e-8  # W/m2/K4


def _summer_half(sst, half, half_w):
    """The sea's summer half-swing: half, less the winter's freezing deficit
    (how far the water's winter, sst - half_w, would fall below freezing).
    That cold went into growing ice, and the summer's heat goes into melting
    it again, so a sea that freezes hard in winter stays cool in summer."""
    return np.maximum(half - np.maximum(FREEZE - (sst - half_w), 0.0), 0.0)


def _winter_air(grid, ocean, sst, t_land, half_l, half_w, t_sum, v_win, h, tune, lift, passes: int = 3):
    """The winter air, carried by the winter wind over land and sea alike
    (at sea level). Over land it relaxes toward the land's own winter in
    time, not over a fixed distance: the air mass (air_m deep, heat capacity
    rho c_p air_m) loses heat to space at ice_b W/m2 per C, an e-folding of
    ~4 days, so it keeps the sea's warmth over U x 4 days of land: ~2400 km in
    a steady westerly (Europe's winter: London, Berlin, Moscow), a few hundred
    in a calm high (Siberia). Ground higher than the air mass (lift) cuts it
    off: the maritime air rides over the range and the cold air pooled
    beyond it stays (the prairies behind the Rockies). That slow relaxation
    is the stable case, warm air over colder ground; air colder than the
    land's own winter (the trades' sea air reaching a tropical land) is heated
    from below, mixes, and takes the land's temperature as fast as in summer
    (_summer_km). Over open water it relaxes toward the water's winter surface,
    faster (air_km_sea: the boundary layer takes up the water's heat). Over
    a frozen sea it relaxes as over land, toward the land's winter, warmed by
    the heat the water below conducts up through the ice: k_ice / h of the
    ice's thickness h (the winter's growth, ocean.ice_growth, from this
    air), against the ice_b W/m2 per C the winter air loses to space, so
    thin seasonal pack ice keeps its air milder than thick perennial ice.
    The open part of a freezing sea gives its air the water's heat far
    faster (open_b), so a pack with some open water stays milder still. So
    the air that comes off a continent in winter stays cold over a frozen bay,
    and warms over open water as it crosses it.
    The water's winter is its own half-swing half_w below its annual mean
    (which knows the land's air that reaches it: compute's sea_half), so a
    bay or a leeward sea freezes, and the freeze then follows the air that
    reaches the sea, not the latitude.
    t_sum: the summer air over the sea (for the ice's growth).
    Returns (the coldest month's air at sea level, the open water 0..1 in
    winter)."""
    from .ocean import ice_growth
    tau = RHO_C_AIR * tune["air_m"] / tune["ice_b"]  # s
    air_km = np.maximum(U_REF * speed(v_win) * tau / 1000.0, 0.5 * h)
    z = lift / LAPSE
    cut = np.maximum(z - tune["air_m"], 0.0) / tune["air_m"]
    k_stable = np.exp(-h / air_km - cut)
    # (air colder than the land's own winter is heated from below: it mixes and
    # takes the land's temperature as fast as in summer, _summer_km)
    k_mixed = np.exp(-h / _summer_km(v_win, h, tune) - cut)
    k_l = k_stable
    k_o = np.exp(-h / tune["air_km_sea"])
    t_lw = t_land - half_l  # land left to itself
    tw = sst - half_w
    open_w = ocean * np.clip((tw - FREEZE) / 2.0, 0, 1)
    t_cold = np.where(ocean, tw, t_lw)
    for _ in range(passes):  # (the ice's thickness from the air over it)
        open_w = ocean * np.clip((tw - FREEZE) / 2.0, 0, 1)
        thick = np.maximum(ice_growth(0.5 * (t_sum + t_cold), 0.5 * (t_sum - t_cold)), 0.1)
        # the air's winter over the sea: its loss to space (over the ice) against the heat the water gives
        # it, through the open water and conducted up through the ice
        wi = (1 - open_w) * tune["ice_b"]
        wo = open_w * tune["open_b"]
        wg = (1 - open_w) * tune["k_ice"] / thick
        t_sea_w = (wi * t_lw + wo * np.maximum(tw, FREEZE) + wg * FREEZE) / (wi + wo + wg)
        eq = np.where(ocean, t_sea_w, t_lw)
        st = np.clip((t_cold - t_lw) / 2.0 + 0.5, 0, 1)
        k_l = st * k_stable + (1 - st) * k_mixed
        k = np.where(ocean, open_w * k_o + (1 - open_w) * k_l, k_l)
        t_cold = carry(grid, v_win, (1 - k) * eq, k, 3 * float(air_km.max()), 0.25)
    if (cut > 0).any():
        # On the high ground itself the air is lifted over it, not cut off:
        # it keeps what the wind brought (PW-581). The cut-off is for the air
        # it passes on, so the cold pooled beyond the range stays.
        k0 = st * np.exp(-h / air_km) + (1 - st) * np.exp(-h / _summer_km(v_win, h, tune))
        up = _upstream(grid, v_win, t_cold)
        hi = ~ocean & (cut > 0)
        t_cold = np.where(hi, (1 - k0) * t_lw + k0 * up, t_cold)
    return t_cold, open_w


def _summer_fetch(grid, ocean, v_sum, sea_sum, land_full, h, tune):
    """The summer air the land would give the air over it, from the sea air
    that arrives and the width of the land around (PW-573).
    land_full is the land's own summer (a big continent's: half_l). Air
    off the sea takes it on in two parts:
    - the boundary layer (sum_h deep) takes the ground's heat in about a day
      (sum_tau, which the reach carries), wherever it is;
    - the air above it, up to the depth the summer's continental heat
      reaches (fetch_h: the thermal low, ~650 hPa), mixes over the
      synoptic scale (fetch_km: the storms' and the summer highs' ~1000
      km), so it is as continental as the land within that distance.
    So the surface air's share of the land's swing is sum_h / fetch_h,
    plus the rest times the land's share within fetch_km. A narrow land
    in the westerlies (Patagonia, New Zealand) then keeps much of the
    sea's summer and a continent's interior gets its full swing. The air
    always lies between the sea air that arrives and the land's own summer,
    so a warm land never cools the sea air below what arrives.
    Both scales are distances, not cells, so a coarse grid gives the same
    air as a fine one.
    The arriving sea air is the sea's summer air along the wind's path,
    weighted over fetch_km: the maritime air mass of the ocean upwind, not
    one cell's water (the air over a narrow sea is mostly the air that
    crossed the land or the ocean beyond it)."""
    km = tune["fetch_km"]
    cont = np.clip(smooth(grid, (~ocean).astype(float), km), 0.0, 1.0)
    k = np.full(grid.n, np.exp(-h / km))
    num = carry(grid, v_sum, np.where(ocean, (1 - k) * sea_sum, 0.0), k, 4 * km, 0.25)
    den = carry(grid, v_sum, np.where(ocean, 1 - k, 0.0), k, 4 * km, 0.25)
    # (deep inside a continent no sea air arrives: the land's own)
    sea_in = (num + 1e-3 * land_full) / (den + 1e-3)
    bl = tune["sum_h"] / tune["fetch_h"]
    return sea_in + (bl + (1 - bl) * cont) * (land_full - sea_in)


def _summer_km(v, h, tune):
    """km: how far the summer air (and the winter air heated from below) reaches over land before it is the
    land's: the wind's speed x sum_tau, but at least a cell (a cell's air is the mean over its width, so its
    upwind half is still mostly its upwind neighbour's)."""
    return np.maximum(U_REF * speed(v) * tune["sum_tau"] / 1000.0, h)


def _upstream(grid, v, x):
    """The flow-weighted mean of x over the cells upstream of each cell along v (its own value where none)."""
    G = _geom(grid)
    out_w, _ = _edge_weights(grid, v)
    w_in = out_w[G["in_e"]]
    dst = np.repeat(np.arange(grid.n), np.diff(G["in_off"]))
    num = np.bincount(dst, w_in * x[G["in_src"]], grid.n)
    den = np.bincount(dst, w_in, grid.n)
    return np.where(den > 1e-9, num / np.maximum(den, 1e-12), x)


def _summer_split(lat, tilt, north, aet_half, pet_half, cloud_sum, tune):
    """C warmer (colder) the land's summer air is from its surface energy
    split: the sunshine reaching the ground in the summer half (under its
    clouds, sunshine; the curve's albedo) less what evaporation takes
    (aet_half's summer half, in W/m2) is the sensible heat H that warms
    the boundary layer (sum_h deep) over the air's day (sum_tau), against
    the H the temperature curve stands for: its sunshine under cloud_ref,
    less ef_ref of the summer's potential evaporation (pet_half, the
    model's own wet surface at that place and temperature). So a cloudy,
    wet summer is cooler than the curve's (Houston, the Yangtze) and a
    sunny, dry one hotter (Phoenix), while a cold summer, whose wet
    surface evaporates little, has little to gain or lose; this replaces
    the +-evap_cool table."""
    S = insolation(np.asarray(lat, float), tilt) * 1e6 / 86400.0
    s_sum = np.where(north, S[3:9].mean(0), np.concatenate([S[:3], S[9:]]).mean(0))
    ground = (1 - tune["albedo_ref"]) * s_sum
    sw = ground * (0.25 + 0.5 * sunshine(cloud_sum))
    sw_ref = ground * (0.25 + 0.5 * sunshine(np.full_like(cloud_sum, tune["cloud_ref"])))
    i, sm = np.arange(len(lat)), np.where(north, 0, 1)
    to_w = LATENT * 1e6 / (0.5 * YEAR_S)  # mm per half-year -> W/m2
    le, le_ref = aet_half[sm, i] * to_w, tune["ef_ref"] * pet_half[sm, i] * to_w
    return tune["sum_tau"] / (RHO_C_AIR * tune["sum_h"]) * ((sw - le) - (sw_ref - le_ref))


def vegetation_feedbacks(open_land, veg, tune) -> dict:
    """Per-cell Budyko w from the vegetation (vegetation.feedback; None:
    TUNE's budyko_w, an Earth-like average cover) on ice-free land
    (open_land), plus what albedo_warming needs (section 4.1 of
    docs/proposals/vegetation.md):
      w   Fu's w = budyko_w + veg_w x (woody cover + veg_w_deep x deep-rooted
          evergreen - veg_w_ref): forests give more of their rain back to the
          air than grass or bare ground (Zhang et al. 2001); veg_w_ref is
          Earth's land mean, so Earth stays at ~budyko_w. The rain kernel
          recycles what the water balance evaporates (PW-266), so this is
          also the plants' rain recycling."""
    n = open_land.shape[0]
    w = np.full(n, tune["budyko_w"])
    if veg is None:
        return dict(w=w, veg=None, has=np.zeros(n, bool))
    has = open_land
    x = veg["woody"] + tune["veg_w_deep"] * veg["deep"] - tune["veg_w_ref"]
    w = np.where(has, np.clip(tune["budyko_w"] + tune["veg_w"] * x, 1.5, 4.0), w)
    return dict(w=w, veg=veg, has=has)


def snow_cover(lat, tilt, temp, t_warm, t_cold, p_jul, p_jan, tune) -> np.ndarray:
    """(12, n) 0..1: the share of the ground under lying snow each month (climate.months' snowpack; full
    cover from snow_full_mm)."""
    mo = months(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt)
    return np.clip(mo["snow"] / tune["snow_full_mm"], 0, 1)


def surface_albedo(sc, veg, tune) -> np.ndarray:
    """(12, n) the land surface's albedo each month under snow cover sc (snow_cover) and vegetation veg
    (vegetation.feedback): lying snow is bright on open ground (snow_albedo) but mostly hidden under
    conifers (veg's mask)."""
    a_free = veg["albedo"][None, :]
    a_snow = veg["mask"] * a_free + (1 - veg["mask"]) * tune["snow_albedo"]
    return sc * a_snow + (1 - sc) * a_free


def albedo_warming(lat, tilt, temp, t_warm, t_cold, p_jul, p_jan, veg, tune, sc=None) -> tuple[np.ndarray, np.ndarray]:
    """C warmer (colder) in the Apr-Sep and Oct-Mar half-years from the
    surface's albedo against the one the temperature curve stands for
    (section 4.2): the sunshine reaching the ground (half the top of the
    atmosphere's) x (reference albedo - the cell's) x albedo_k, per month.
    Snow (climate.months' snowpack; full cover from snow_full_mm) is bright
    on open ground (snow_albedo) but mostly hidden under conifers
    (vegetation's mask: Bonan 1992), against a reference albedo_snow_ref;
    snow-free ground against albedo_ref. Each half-year capped at
    +-albedo_cap. sc: snow_cover's result, if already at hand."""
    if sc is None:
        sc = snow_cover(lat, tilt, temp, t_warm, t_cold, p_jul, p_jan, tune)
    a = surface_albedo(sc, veg, tune)
    a_ref = sc * tune["albedo_snow_ref"] + (1 - sc) * tune["albedo_ref"]
    sun = 0.5 * insolation(np.asarray(lat, float), tilt) * 1e6 / 86400.0  # W/m2 at the ground
    d = tune["albedo_k"] * (a_ref - a) * sun
    cap = tune["albedo_cap"]
    return np.clip(d[3:9].mean(0), -cap, cap), np.clip(np.concatenate([d[:3], d[9:]]).mean(0), -cap, cap)


def _land_finish(t_warm, t_cold, temp, land, north, p_jul, p_jan, ice, cover, ocean, tune, lat, tilt, fb):
    """The plants' and the ice's effect on the land's temperatures (the
    rain's, through the summer's evaporation, is in the air already:
    _summer_split). Returns (t_warm, t_cold, temp) on the ice surface and
    the same three for the bare ground under it (see ice_surface)."""
    if fb["veg"] is not None:  # the surface's albedo
        d_jul, d_jan = albedo_warming(lat, tilt, temp, t_warm, t_cold, p_jul, p_jan, fb["veg"], tune)
        d_sum, d_win = np.where(north, d_jul, d_jan), np.where(north, d_jan, d_jul)
        t_warm = np.where(fb["has"], t_warm + d_sum, t_warm)
        t_cold = np.where(fb["has"], t_cold + d_win, t_cold)
        temp = np.where(fb["has"], temp + 0.5 * (d_sum + d_win), temp)
    # (near the equator the rainy 'summer' can be the cooler half-year, and
    # under an eccentric orbit (orbit_dt) the season of the near sun, the
    # same month in both hemispheres, outweighs the tilt's there: warmest
    # and coldest are whichever is warmer and colder, and jul_warm keeps
    # which of them is July, so July and January stay continuous across the
    # equator, PW-380)
    jul_warm = north == (t_warm >= t_cold)
    t_warm, t_cold = np.maximum(t_warm, t_cold), np.minimum(t_warm, t_cold)
    # the bare ground under the ice: its own height, no white surface
    up = LAPSE * np.where(land, ice, 0.0)
    ground = (t_warm + up, t_cold + up, temp + up)
    return (*ice_surface(*ground, np.where(land, ice, 0.0), cover, lat, p_jul, p_jan), ground, jul_warm)


def ice_cover(grid: Grid, ice: np.ndarray, land: np.ndarray, tune: dict | None = None) -> np.ndarray:
    """A land-ice sheet's cover (0..1; icemass damps its summer by SUMMER_DAMP x
    this): the share of the land within ~ice_cool_km that is under ice (~1
    on and around a big sheet,
    small on a lone mountain cap), and only away from the tropics, where
    long cold nights and winters let the air over the ice pool and chill
    (and where the model's sea-level summers, calibrated on ice-free land,
    are too warm for an ice surface): none within 15 deg of the equator,
    in full from 50 deg."""
    tune = TUNE if tune is None else tune
    km = tune["ice_cool_km"]
    a = smooth(grid, ((ice > 0) & land).astype(float), km)
    b = smooth(grid, land.astype(float), km)
    polar = np.clip((np.abs(grid.lat) - 15.0) / 35.0, 0.0, 1.0)
    return np.where(ice > 0, np.clip(a / np.maximum(b, 1e-6), 0.0, 1.0) * polar, 0.0)


def ice_surface(t_warm, t_cold, temp, ice, cover, lat, p_jul, p_jan):
    """Temperatures on top of land ice (m; 0 = bare ground), from those of
    the bare ground under it, by the ice's own surface mass balance year
    (icemass.surface, PW-277: the one rule that also sets where the ice
    is): the ice's height (lapse rate), thick ice ~2 C colder on the year's mean (in winter
    where the summer melts, all year where it never does: inversion, katabatic air), the summer's warmth damped while snow lies
    (by the bright surface's own share: cover, icemass.sheet_cover; a big
    sheet's own air mass is in the ground's air already, carried along the
    winds: icemass.air_mass, PW-336) and a melting surface held near 0 C.
    Antarctica's coast reaches ~-2 C in summer, its plateau ~-20 C (~10 C
    warmer than observed: the plateau's inversion, PW-039). The annual mean keeps the ground's own
    offset from its months' midpoint. lat (deg), p_jul, p_jan (mm/yr: the
    half-years' precipitation, whose snow sets how long the summer is
    bright) per cell."""
    from . import icemass
    on = np.asarray(ice) > 0
    if not on.any():
        return t_warm, t_cold, temp
    t_warm, t_cold, temp = (np.array(x, float) for x in (t_warm, t_cold, temp))
    i = np.flatnonzero(on)
    pick = (lambda x: np.broadcast_to(np.asarray(x, float), on.shape)[i])
    ta, tw, tc = icemass.surface(pick(lat), t_warm[i], t_cold[i], pick(p_jul), pick(p_jan), pick(ice), pick(cover))
    ta = np.clip(temp[i] + ta - 0.5 * (t_warm[i] + t_cold[i]), tc, tw)
    t_warm[i], t_cold[i], temp[i] = tw, tc, ta
    return t_warm, t_cold, temp


def _sheet_cover(grid: Grid, ice: np.ndarray, ice_air: np.ndarray, cold=None) -> np.ndarray:
    """icemass.sheet_cover (ice_surface's cover), on the share of the air that isn't the sheets' own air mass
    (icemass.sheet_air of ice_air, the ice whose air the winds carry: PW-1050)."""
    from .icemass import sheet_air, sheet_cover
    if not (np.asarray(ice) > 0).any():
        return np.zeros(grid.n)
    air = sheet_air(grid, ice_air, cold=cold) if (np.asarray(ice_air) > 1).any() else None
    return sheet_cover(grid, ice, air=air)
