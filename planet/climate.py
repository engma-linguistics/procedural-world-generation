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
- Koppen climate classes from the monthly-ish temperatures and rain.
- Where the rain goes (water_balance): back into the air (evaporation,
  limited by the sunshine and warmth to drive it, and by the rain there is)
  or into the rivers (runoff).
"""

from __future__ import annotations

import numpy as np

from numba import njit, prange

from . import kernels
from . import ocean as ocean_mod
from .geo import R_KM
from .grid import Grid

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


def seasons(grid: Grid, elev: np.ndarray, temp: np.ndarray, tilt: float = 23.4):
    """First guess of the warmest- and coldest-month temperatures (used for
    the winds; compute refines them). The swing grows with latitude and
    with distance from the sea, which evens temperatures out (Vancouver: 4
    to 18 C; Yakutsk, 62 N inland: -39 to +19). Returns (t_warm, t_cold)."""
    land = elev > 0
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


def _geom(grid: Grid):
    """Per-grid constants: local east/north unit vectors, directed edges and
    their tangent directions, cell spacing (km). Cached."""
    key = (id(grid), grid.n)
    if key not in _GEOM:
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
        if len(_GEOM) > 4:
            _GEOM.clear()
        _GEOM[key] = dict(east=east, north=north, src=src, dst=dst, d=d, deg=deg, h=grid.spacing * R_KM,
                          out_off=off, out_e=out_e, in_off=in_off, in_e=in_e, in_src=src[in_e])
    return _GEOM[key]


_COARSE = {}


def _coarse(grid: Grid, level: int = 3):
    """A coarser icosphere (level 3: ~900 km cells, for patterns thousands
    of km across): which coarse cell each fine cell falls in, the coarse
    neighbours, and weights to interpolate back smoothly (the nearby coarse
    cells, by distance). Cached."""
    from .grid import build_grid
    key = (id(grid), grid.n, level)
    if key not in _COARSE:
        cg = build_grid(min(level, grid.level))
        cidx = cg.locate(grid.centers)
        cand = np.zeros((grid.n, 7), np.int64)
        ok = np.zeros((grid.n, 7), bool)
        cand[:, 0], ok[:, 0] = cidx, True
        deg = np.diff(cg.nbr_off)
        for k in range(6):  # the containing coarse cell and its neighbours
            has = deg[cidx] > k
            cand[has, k + 1] = cg.nbr_idx[cg.nbr_off[cidx[has]] + k]
            ok[has, k + 1] = True
        d = np.arccos(np.clip((cg.centers[cand] * grid.centers[:, None, :]).sum(-1), -1, 1))
        w = np.where(ok, np.maximum(0.0, 1 - d / (1.2 * cg.spacing)), 0.0)
        w /= w.sum(1, keepdims=True)
        if len(_COARSE) > 8:
            _COARSE.clear()
        _COARSE[key] = dict(n=cg.n, cidx=cidx, off=cg.nbr_off, idx=cg.nbr_idx, cand=cand, w=w,
                            h=cg.spacing * R_KM)
    return _COARSE[key]


@njit(cache=True)
def _coarse_smooth(f, cidx, nc, off, idx, iters, cand, w, full):
    """Average f onto the coarse grid, blur it there (iters neighbour
    averages) and interpolate it back. The average is over the fine cells
    in each coarse cell, or (full) weighted by the interpolation weights,
    which is smoother: each fine cell counts towards all the coarse cells
    near it (a nested grid's cells on a coarse cell's edge are as near to
    the next one)."""
    tot = np.zeros(nc)
    cnt = np.zeros(nc)
    if full:
        for i in range(f.shape[0]):
            for k in range(cand.shape[1]):
                tot[cand[i, k]] += w[i, k] * f[i]
                cnt[cand[i, k]] += w[i, k]
        c = tot / np.maximum(cnt, 1e-12)
    else:
        for i in range(f.shape[0]):
            tot[cidx[i]] += f[i]
            cnt[cidx[i]] += 1.0
        c = tot / np.maximum(cnt, 1.0)
    g = np.empty(nc)
    for _ in range(iters):
        for j in range(nc):
            t = 0.0
            for e in range(off[j], off[j + 1]):
                t += c[idx[e]]
            g[j] = 0.5 * c[j] + 0.5 * t / (off[j + 1] - off[j])
        c[:] = g
    out = np.zeros(f.shape[0])
    for i in range(f.shape[0]):
        for k in range(cand.shape[1]):
            out[i] += w[i, k] * c[cand[i, k]]
    return out


def smooth_big(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """Blur a field over thousands of km (on the coarse grid: cheap)."""
    C = _coarse(grid)
    iters = int(round(4 * (km / C["h"]) ** 2))
    return _coarse_smooth(np.ascontiguousarray(f, np.float64), C["cidx"], C["n"], C["off"], C["idx"], iters,
                          C["cand"], C["w"], False)


@njit(cache=True, parallel=True)
def _smooth(f, nbr_off, nbr_idx, iters, w):
    f = f.copy()
    g = np.empty_like(f)
    for _ in range(iters):
        for i in prange(f.shape[0]):
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += f[nbr_idx[e]]
            g[i] = (1 - w) * f[i] + w * s / (nbr_off[i + 1] - nbr_off[i])
        f, g = g, f
    return f


COARSE_CELLS = 2.4  # a blur this many coarser cells wide or more is done on the coarser grid


def smooth(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """Blur a field over roughly `km` (Gaussian-ish sigma). A wide blur is
    done on the coarsest grid level it still spans COARSE_CELLS cells of
    (at level 6: ~580 km and up, a grid level coarser), which is ~10x
    cheaper and the same to within ~0.5% of the field's spread. Moving the
    field to that grid and back blurs it by about half a coarse cell's
    width already, so that much is taken off the blur there."""
    h = _geom(grid)["h"]
    lev = grid.level
    while lev > 0 and km >= COARSE_CELLS * h * 2 ** (grid.level - lev + 1):
        lev -= 1
    if lev < grid.level:
        C = _coarse(grid, lev)
        iters = int(round(4 * max(km**2 - 0.5 * C["h"] ** 2, 0.0) / C["h"] ** 2))
        return _coarse_smooth(np.ascontiguousarray(f, np.float64), C["cidx"], C["n"], C["off"], C["idx"], iters,
                              C["cand"], C["w"], True)
    iters = int(round(4 * (km / h) ** 2))
    if iters <= 0:
        return f.astype(np.float64)
    return _smooth(np.ascontiguousarray(f, np.float64), grid.nbr_off, grid.nbr_idx, iters, 0.5)


@njit(cache=True, parallel=True)
def _gradient(f, src, dst, d, out_off, out_e, deg, h):
    n = out_off.shape[0] - 1
    g = np.empty((n, 3))
    for i in prange(n):
        g0 = 0.0
        g1 = 0.0
        g2 = 0.0
        for k in range(out_off[i], out_off[i + 1]):
            e = out_e[k]
            df = f[dst[e]] - f[src[e]]
            g0 += d[e, 0] * df
            g1 += d[e, 1] * df
            g2 += d[e, 2] * df
        c = 2.0 / (deg[i] * h)
        g[i, 0] = g0 * c
        g[i, 1] = g1 * c
        g[i, 2] = g2 * c
    return g


def gradient(grid: Grid, f: np.ndarray) -> np.ndarray:
    """Tangent gradient per cell, units of f per km."""
    G = _geom(grid)
    return _gradient(np.ascontiguousarray(f, np.float64), G["src"], G["dst"], G["d"], G["out_off"], G["out_e"],
                     G["deg"], G["h"])


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


def zonal_mean(grid: Grid, f: np.ndarray, mask: np.ndarray | None = None, width: float = 3.0):
    """Mean of f in latitude bands `width` deg wide, given back per cell."""
    bins = np.clip(((grid.lat + 90) // width).astype(int), 0, int(180 // width) - 1)
    m = np.ones(grid.n, bool) if mask is None else mask
    nb = int(180 // width)
    tot = np.bincount(bins[m], f[m], nb)
    cnt = np.bincount(bins[m], minlength=nb)
    allm = np.bincount(bins, f, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    zm = np.where(cnt > 0, tot / np.maximum(cnt, 1), allm)
    return zm[bins]


def _nbr_mean(grid: Grid, f: np.ndarray) -> np.ndarray:
    """Mean of f over each cell's neighbours."""
    return np.add.reduceat(f[grid.nbr_idx], grid.nbr_off[:-1]) / np.diff(grid.nbr_off)


# --------------------------------------------------------------------------
# Wind
# --------------------------------------------------------------------------
def wind(grid: Grid, shift: float = 0.0) -> np.ndarray:
    """The planet-wide three-cell pattern, the same at every longitude:
    easterly trade winds below ~30 deg, westerlies from 30 to 60, polar
    easterlies above. shift (deg) moves the bands north (northern summer):
    the tropical belts follow the sun fully, the westerlies only a third as
    much (they stay strong at 45-60 deg in winter, which is what brings the
    sea's mild air deep into Europe)."""
    G = _geom(grid)
    lat = grid.lat - shift * (0.3 + 0.7 * np.exp(-(grid.lat / 25.0) ** 2))
    a = np.abs(lat)
    hemi = np.sign(lat)[:, None]
    # east component: trades strongest ~12 deg, calm 'horse latitudes' ~30,
    # westerlies strongest ~48, weak polar easterlies; poleward component:
    # toward the equator under the trades, poleward under the westerlies
    ue = (-0.9 * np.exp(-((a - 12) / 14) ** 2) + 1.0 * np.exp(-((a - 48) / 15) ** 2)
          - 0.4 * np.exp(-((a - 78) / 10) ** 2))[:, None]
    un = (-0.3 * np.sin(np.radians(6 * np.minimum(a, 90))))[:, None]
    return ue * G["east"] + un * hemi * G["north"]


def monsoon_wind(grid: Grid, t_sl: np.ndarray, shift: float, strength: float = 1.0, big: float = 0.0,
                 big_km: float = 2000.0):
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
    surface temperature reduced to sea level, C. Returns (wind, warmth):
    warmth is the smoothed temperature excess, C (>0: rising air)."""
    anom = t_sl - zonal_mean(grid, t_sl)
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
    return wind(grid, shift) + v, warmth


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
    # Small islands are sea as far as the gyres are concerned.
    land = ~ocean
    lab, nlab = _components(grid, land)
    sizes = np.bincount(lab[lab >= 0], minlength=max(nlab, 1)) * (4 * np.pi * R_KM**2 / grid.n)
    wall = land & (sizes[np.maximum(lab, 0)] >= tune["island_km2"])
    sea = ~wall
    cosl = np.cos(np.radians(lat))
    tau = wind_v * np.abs(speed(wind_v))[:, None] ** (tune["tau_pow"] - 1)  # stress ~ |u|^p
    F = R_KM * smooth(grid, curl(grid, tau), 250.0) * sea
    # The boundary layer (r/beta) has to span a couple of cells to be resolved.
    r = max(tune["gyre_km"], 0.8 * h)
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


def sea_surface(grid: Grid, ocean: np.ndarray, t_eq: np.ndarray, wind_v: np.ndarray,
                relax_km: float = 2500.0, upwelling: float = 5.0,
                eq_upwelling: float = 0.0, tune: dict | None = None, cur=None, away=None,
                share=None, t_in=None, base=None) -> tuple[np.ndarray, np.ndarray]:
    """Sea-surface temperature: the latitude's temperature t_eq, moved by the
    currents (warm water poleward along the western side of each ocean, cold
    water toward the equator along the eastern side), plus coastal upwelling
    where the wind pushes surface water away from a coast (Peru, California,
    Namibia) and equatorial upwelling (eq_upwelling, C). Each band's average
    is kept. cur, away: the currents (as climate.currents returns them) if
    already known; share, t_in, base: where the overturning's inflow makes
    up a share of the surface water, its temperature (see ocean.py), and
    this function's sst without it: then the inflow's warmth is added to
    base. Returns (sst, current)."""
    G = _geom(grid)
    tune = {**TUNE, **(tune or {})}
    if cur is None:
        cur, away = currents(grid, ocean, wind_v, tune)
    # Ekman transport: 90 deg to the right of the wind in the north, left in the south
    ek = np.cross(wind_v, grid.centers) * np.sign(grid.lat)[:, None]
    off = np.clip((ek * away).sum(1), 0, 1.5)
    lat_ok = np.clip((np.abs(grid.lat) - 5) / 8, 0, 1) * np.clip((45 - np.abs(grid.lat)) / 8, 0, 1)
    cold = upwelling * off * lat_ok
    src = G["src"]
    allowed = (ocean[src] & ocean[G["dst"]]).astype(np.float64)
    # The water gives its heat up to the air over a set time, so a fast
    # current carries its warmth (or cold) far before it fades: relax_km at
    # the reference speed cur_ref (the Gulf Stream reaches Norway, the slow
    # drift across an ocean's middle soon takes on the latitude's temperature).
    reach = relax_km * np.clip(speed(cur) / tune["cur_ref"], tune["cur_min"], tune["cur_max"])
    keep = np.exp(-G["h"] / reach)
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
    b = np.where(ocean, keep, 0.0)
    km = 1.5 * tune["cur_max"] * relax_km
    if share is not None:
        # Where the overturning's inflow makes up a share of the surface
        # water, the water relaxes toward its temperature instead: carried
        # by the same currents, that adds (the carrying is linear) to base.
        # Its warmth adds to the latitude's mean but for moc_zonal of it
        # (t_eq was fitted to Earth's sea, overturning and all).
        d = np.where(ocean, (1 - keep) * share * (t_in - t_eq), 0.0)
        e = np.where(ocean, carry(grid, cur, d, b, km=km, diffusion=0.15, allowed=allowed), 0.0)
        return base + e - tune["moc_zonal"] * np.where(ocean, zonal_mean(grid, e, ocean), 0.0), cur
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
    rain, not the vapour): the driest air is held at HUMID_MIN."""
    x = np.maximum(q / _qsat(t_air, tune["q_k"]), HUMID_MIN)
    rh = x / (1.0 + x**4) ** 0.25
    return t_air + np.log(rh) / tune["q_k"], 100.0 * rh


HUMID_MIN = 0.15  # the lowest relative humidity humidity() reports


LQ = 9.5  # C of moist static energy per unit of vapour (latent heat / heat capacity * 3.8 g/kg)


@njit(cache=True, parallel=True)
def _rain(qs, src_q, ocean, ls_rate, cv_rate, mse_t, mse_thr, warm, move, diffusion, in_w,
          in_src, in_off, deg, nbr_off, nbr_idx, iterations, fex, rh_c, rh_pow, cv_scale, et, evap, mean_mm):
    """Water vapour carried along the wind, for all seasons at once
    (arrays are [season, cell]). Each iteration, in each cell:
    - over the sea the air takes up water to src_q;
    - over land it takes up what the ground evaporates: a share et of the
      rain the place gets in an average season, because soil, groundwater
      and deep roots keep the wet season's water for the dry one (less where
      it is cold: warm);
    - it rains a share fex of what the air can't hold (above qs);
    - plus large-scale rain (fronts, rising air), a share ls_rate of the
      rest that needs fairly humid air (relative humidity near rh_c or more);
    - plus showers and thunderstorms, a share cv_rate per cv_scale C of
      instability: the moist static energy of the air near the ground (heat
      + height + latent heat of its vapour: mse_t + LQ * vapour) above that
      of the air aloft (mse_thr). Wet ground is cooler and dry ground hotter
      (evap C, see compute), which feeds back on the showers;
    - then the air moves on (move: share per iteration; slow winds linger)
      and mixes with its neighbours (diffusion: eddies, storms).
    Returns the rain rate averaged over the last quarter of the iterations,
    the large-scale part of it, the evaporation from the sea (the water
    the air takes up over it, same units), and the air's water vapour left
    after its rain (_qsat units: 1 = saturated at 0 C). (Parallel over cells; the one sum over
    all cells stays serial, so the results don't depend on the threads.)"""
    S, n = qs.shape
    m = src_q.copy()
    acc = np.zeros((S, n))
    acc_ls = np.zeros((S, n))
    ema = np.zeros((S, n))  # running mean of each place's rain
    tcor = np.zeros((S, n))  # wet ground cooler, dry ground hotter (C)
    moved = np.empty((S, n))
    acc_up = np.zeros((S, n))  # water the air takes up over the sea (evaporation)
    acc_q = np.zeros((S, n))  # the air's water vapour after its rain (for humidity)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        if evap != 0 and it >= 20 and it % 10 == 0:
            tot = 0.0
            for k in range(S):
                for i in range(n):
                    tot += ema[k, i]
            scale = mean_mm * S * n / max(tot, 1e-12)  # model units -> mm/yr
            for i in prange(n):
                if not ocean[i]:
                    for k in range(S):
                        lp = np.log10(max(ema[k, i] * scale, 1.0) / 100.0) / 1.2
                        tcor[k, i] = evap * (1.0 - 2.0 * min(max(lp, 0.0), 1.0))
        last = it >= iterations - tail
        for k in range(S):
            # The previous season's mixing with the neighbours (p) is done in
            # the same pass as this season's rain: they touch different
            # numbers, so this only saves a pass over the cells. (The last
            # season's mixing waits for the next iteration; after the last
            # iteration it would no longer change the rain.)
            p = k - 1 if k > 0 else (S - 1 if it > 0 else -1)
            for i in prange(n):
                if p >= 0:
                    t = 0.0
                    for e in range(nbr_off[i], nbr_off[i + 1]):
                        t += moved[p, nbr_idx[e]]
                    m[p, i] = (1 - diffusion[p, i]) * moved[p, i] + diffusion[p, i] * t / deg[i]
                if ocean[i]:
                    if src_q[k, i] > m[k, i]:
                        if last:
                            acc_up[k, i] += src_q[k, i] - m[k, i]
                        m[k, i] = src_q[k, i]
                else:
                    year = 0.0
                    for j in range(S):
                        year += ema[j, i]
                    m[k, i] += et * warm[k, i] * year / S
                q = m[k, i]
                excess = max(q - qs[k, i], 0.0)
                rh = min(q / max(qs[k, i], 1e-12) / rh_c, 1.0)
                rate = ls_rate[k, i] * rh**rh_pow
                r_ls = rate * (q - excess)
                inst = (mse_t[k, i] + tcor[k, i] + LQ * q - mse_thr[k, i]) / cv_scale
                if inst > 0:
                    rate += cv_rate[k, i] * min(inst, 2.0)
                r = fex * excess + rate * (q - excess)
                m[k, i] = q - r
                ema[k, i] += 0.05 * (r - ema[k, i])
                if last:
                    acc[k, i] += r
                    acc_ls[k, i] += r_ls
                    acc_q[k, i] += q - r
            # the air moves on: each cell keeps what stays and gathers what
            # its upwind neighbours send it
            for i in prange(n):
                mo = (1 - move[k, i]) * m[k, i]
                for e in range(in_off[i], in_off[i + 1]):
                    j = in_src[e]
                    mo += move[k, j] * m[k, j] * in_w[k, e]
                moved[k, i] = mo
    return acc / tail, acc_ls / tail, acc_up / tail, acc_q / tail


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


def _season_inputs(grid: Grid, elev, t_air, sst, v, shift, t_sl_season, tune, track=None) -> dict:
    """Per-cell inputs of the rain kernel for one season (see _rain).
    t_air: surface air temperature (C, used over land), sst: sea surface
    temperature, v: wind, shift: deg the tropical rain belt is north of the
    equator, t_sl_season: the season's temperatures reduced to sea level,
    track: storminess along the jet's storm tracks (storm_track), which
    takes over a share storm_jet of the latitude belt's storminess."""
    ocean = elev <= 0
    lat = grid.lat
    up = LAPSE * np.maximum(elev, 0)
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
    src_q = np.where(ocean, tune["rh"] * qs, 0.0)
    # Storms stir moisture around (eddy mixing) and make large-scale rain,
    # both in proportion to the storminess (~1 in a mid-latitude winter).
    B = storminess(grid, t_sl_season) / 7.0
    if track is not None:
        B = (1 - tune["storm_jet"]) * B + tune["storm_jet"] * track
    diff = np.clip(0.12 + tune["eddy"] * B, 0, 1.0)
    # The tropical rain belt (where the trade winds meet and the air rises)
    # follows the sun; ~25 deg either side of it the air sinks (the dry
    # subtropics, the trade-wind inversion); the poles are dry highs.
    itcz = np.exp(-((lat - shift) / tune["itcz_w"]) ** 2)
    sink = np.exp(-((np.abs(lat - shift) - 25) / 9) ** 2)
    pole = np.clip((np.abs(lat) - 70) / 15, 0, 1)
    ls = tune["base"] * np.clip(tune["bg"] + tune["storm"] * B + tune["itcz_ls"] * itcz
                                - tune["belt_dry"] * sink - 0.3 * pole, 0.05, None)
    # Showers need unstable air: warm, moist air near the ground compared
    # with the air aloft. Within ~20-30 deg of the equator the air aloft has
    # the same temperature everywhere (the Earth's spin is too weak there to
    # hold temperature differences up), set by the warmest seas: so hot but
    # dry deserts and cool seas stay stable while humid hot land and warm
    # seas boil over. Further poleward the air aloft follows the latitude's
    # sea temperature (so summer continents get thunderstorms).
    mse_t = np.where(ocean, sst, t_air + 9.8e-3 * np.maximum(elev, 0))  # (+ height: g/cp per m)
    zs = zonal_mean(grid, sst, ocean)
    t_trop = zs[np.abs(lat) < 20].max()
    zs = zs + np.clip((tune["wtg"] + 15 - np.abs(lat)) / 15, 0, 1) * np.maximum(t_trop - zs, 0)
    t_ref = smooth(grid, zs, 800.0)
    mse_thr = t_ref + LQ * tune["rh"] * _qsat(t_ref, tune["q_k"])
    cv = tune["cv"] * tune["base"] * (1 + tune["itcz_cv"] * itcz) * np.clip(1 - tune["cv_sink"] * sink, 0, 1)
    out_w, _ = _edge_weights(grid, v)
    move = np.clip(speed(v), 0.25, 1.0)
    warm = np.clip(t_air / 15.0, 0, 1)  # evaporation needs warmth
    return dict(qs=qs, src_q=src_q, ls=ls, cv=cv, mse_t=mse_t, mse_thr=mse_thr, warm=warm, move=move,
                diff=diff, out_w=out_w, B=B)


def rain(grid: Grid, elev, seasons_in: list[dict], tune: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rain rate (model units) per season, [season, cell], from the inputs
    of _season_inputs for each season, the evaporation from the sea
    (same units and shape; 0 on land) and the air's water vapour (_qsat
    units, same shape; see humidity())."""
    G = _geom(grid)
    st = {k: np.ascontiguousarray(np.stack([d[k] for d in seasons_in])) for k in seasons_in[0]}
    iters = int(60 * 2 ** (grid.level - 5)) + 40
    r, r_ls, up, vap = _rain(st["qs"], st["src_q"], elev <= 0, st["ls"], st["cv"], st["mse_t"], st["mse_thr"],
                    st["warm"], st["move"], st["diff"], st["out_w"][:, G["in_e"]], G["in_src"], G["in_off"], G["deg"],
                    grid.nbr_off, grid.nbr_idx, iters, tune["fex"], tune["rh_c"], tune["rh_pow"],
                    tune["cv_scale"], tune["et"], tune["evap_cool"], tune["mean_mm"])
    # Storms carry their rain with them: the large-scale (frontal) rain is
    # spread over a storm's size, so e.g. the storms that brew over warm
    # coastal seas in winter rain on the east coasts even though the mean
    # wind blows offshore there.
    for k in range(len(seasons_in)):
        w = np.clip(tune["storm_mix"] * st["B"][k], 0, 0.9)
        r[k] += w * (smooth(grid, r_ls[k], tune["storm_km"]) - r_ls[k])
    return r, up, vap


TUNE = dict(
    # moisture
    rh=0.85,  # sea air's humidity relative to saturation at the sea surface
    q_k=0.06,  # per C: how much more water warm air holds (Clausius-Clapeyron ~0.07)
    lapse_q=0.5,  # share of the cooling with height that wrings water out of rising air
    airmass_km=800.0,  # km over which the air mass aloft evens out the ground's temperatures
    et=0.5,  # share of land rain that evaporates back into the air (soil, plants)
    # rain-making
    fex=0.25,  # share of the oversaturated water that rains out in one cell (rest further on)
    base=0.035,  # rain-out per cell and iteration (large-scale rain; showers: cv times this)
    bg=0.45,  # large-scale rain everywhere (fronts, drizzle), times base
    itcz_ls=0.3,  # extra large-scale rain under the tropical rain belt
    itcz_w=10.0,  # deg: half-width of the tropical rain belt
    belt_dry=0.3,  # how much the sinking subtropical air suppresses large-scale rain
    storm=0.6,  # large-scale rain from storms, per unit of storminess
    eddy=1.0,  # how much storms stir moisture around, per unit of storminess
    storm_mix=1.0,  # share of the frontal rain spread over a storm's size, per unit of storminess
    storm_km=600.0,  # km: a storm's rain area
    cv=4.0,  # showers: rain-out per cell and iteration at cv_scale C of instability, times base
    cv_scale=10.0,  # C of moist static energy excess for full-rate showers
    itcz_cv=1.0,  # showers are likelier under the tropical rain belt (rising air) ...
    cv_sink=0.5,  # ... and rarer under the sinking subtropical air
    wtg=20.0,  # deg: the tropics' even temperature aloft reaches this far (then fades over 15 deg)
    rh_c=0.8,  # relative humidity above which the large-scale rain runs at full rate...
    rh_pow=3.0,  # ...and how fast it falls off below it
    # winds and seasons
    ice_cooling=10.0,  # C: how much colder an ice sheet's surface is than bare ground would be ...
    ice_cool_km=300.0,  # ... in full where the land this far around is all ice (a small cap sits in
    # its surroundings' air)
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
    sea_half=6.0,  # C: the sea's seasonal half-swing (times season strength)
    coast=0.35,  # sea air at a coast per share of sea neighbours (sea breezes, fog)
    air_km_s=450.0,  # km over which air over land takes on the land's summer temperature
    air_km_w=900.0,  # ... its winter temperature (slower: cold ground under warm air is stable)
    evap_cool=1.5,  # C: how much cooler rainy summers are (and hotter dry ones)
    mean_mm=1000.0,  # global mean precipitation, mm/yr (Earth ~1000)
    # evaporation and runoff (see water_balance)
    budyko_w=2.6,  # Fu's w: how readily the land gives the rain back to the air (Earth's mean ~2.6)
    soil_mm=150.0,  # mm of water the soil holds over from one half-year to the next
    open_water=1.2,  # open water's evaporation per unit of the land's potential evaporation
    # salinity and the overturning circulation (see ocean.py)
    salt_k=2.0,  # psu fresher per m/yr of net fresh water into the sea (S0 x mixing time / depth) ...
    salt_ice=4.0,  # ... x (1 + this) under year-round sea ice (the fresh lid: a halocline)
    salt_km=3000.0,  # km a current carries its salinity at cur_ref before it has mixed
    salt_diff=0.3,  # eddy mixing of salinity with the neighbours, per step
    river_km=300.0,  # km: a river plume's spread over the sea
    ice_export=0.25,  # share of the winter's sea ice that drifts away to melt elsewhere (all of it
    # where the winter wind blows off the coast) ...
    ice_km=800.0,  # ... spread over this far
    brine_m=50.0,  # m: depth of the winter mixed layer the brine of new sea ice mixes into
    moc=0.65,  # Sv sinking per kg/m3 of density difference (sinking - water replacing it) per 1e6 km2
    moc_k=3.0,  # Sv per kg/m3: the most one sinking site turns over (see ocean.overturning)
    moc_z=2000.0,  # m: depth at which the waters' densities are compared for sinking
    moc_top=0.1,  # the deep water is the densest water of this share of the polar sea (by area) ...
    moc_mix=0.5,  # ... less this (kg/m3: it mixes on its way down)
    moc_drho=0.3,  # kg/m3: water this much lighter than the deep water can't sink ...
    moc_pow=3.0,  # ... and the sinking grows as (excess / moc_drho)^moc_pow up to its density
    moc_lat=50.0,  # deg: deep water forms poleward of this (fully 10 deg further)
    moc_km=300.0,  # km: a sinking site's water is the mix over this
    moc_sea_km2=1.0e6,  # km2: a sea smaller than this (cut off from the others) has no deep water of its own
    moc_src_lat=25.0,  # deg: the water replacing what sinks comes from equatorward of this ...
    moc_follow=3.0,  # ... riding the currents (a step costs exp(-this x the current's speed its way / cur_ref))
    moc_sill=300.0,  # m: it can't pass straits shallower than this
    moc_width=250.0,  # km: the inflow's width (for its heat loss to the air) ...
    moc_lambda=30.0,  # ... W/m2 per C it gives up to the air above the latitude's sea temperature
    moc_q0=0.001,  # Sv per km of width: an inflow this strong makes up ~2/3 of the surface water
    moc_zonal=0.0,  # share of the inflow's warmth taken off its latitude's mean (see sea_surface)
    moc_level=5,  # grid level the overturning is solved on (5: ~220 km cells)
    moc_spin=6.0,  # x moc_drho at the start (see ocean.solve)
    moc_iters=4,  # damped iterations of salinity <-> overturning
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


def water_balance(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt: float = 23.4, tune: dict | None = None) -> dict:
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
      lake_evap evaporation from open water (lakes; larger than pet)
    Months are a sine between the coldest and warmest month, peaking in
    July (north) or January (south)."""
    tune = {**TUNE, **(tune or {})}
    north = lat >= 0
    ra = insolation(lat, tilt)
    m = np.arange(12)[:, None]
    peak = np.where(north, 6, 0)[None, :]
    amp = 0.5 * (t_warm - t_cold)
    t_m = np.clip(temp + amp * np.cos(2 * np.pi * (m - peak) / 12), t_cold, t_warm)
    pet_m = np.maximum(ra / LATENT * (t_m + 5) / 100, 0) * MONTH_DAYS[:, None]  # mm per month
    pet_jul = 2 * pet_m[3:9].sum(0)  # Apr-Sep, as a rate per year like p_jul
    pet_jan = 2 * (pet_m[:3].sum(0) + pet_m[9:].sum(0))
    # Each half-year on its own (amounts, mm), then again with what the
    # soil kept from the other half-year's surplus (snowmelt and winter rain
    # still in the ground when summer comes), up to its capacity.
    w, cap = tune["budyko_w"], tune["soil_mm"]
    p_s, e_s = 0.5 * np.stack([p_jul, p_jan]), 0.5 * np.stack([pet_jul, pet_jan])
    kept = np.minimum(p_s - budyko(p_s, e_s, w), cap)[::-1]
    aet = budyko(p_s + kept, e_s, w).sum(0)
    precip = p_s.sum(0)
    aet = np.minimum(aet, precip)
    return dict(pet=e_s.sum(0), aet=aet, runoff=precip - aet, lake_evap=tune["open_water"] * e_s.sum(0))


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
    """Koppen class per cell. Monthly values aren't modelled, so they're
    estimated from the two half-years assuming a smooth (sinusoidal) annual
    cycle of temperature and of rain."""
    north = lat >= 0
    p_sum = np.where(north, p_jul, p_jan) / 12  # monthly mean, summer half (mm)
    p_win = np.where(north, p_jan, p_jul) / 12
    # rain(month) = mean * (1 + a cos): the half-year means are mean*(1 +- 2a/pi),
    # the extremes mean*(1 +- a), and where the halves meet it's the mean
    mean = (p_sum + p_win) / 2
    a = np.clip((p_sum - p_win) / np.maximum(p_sum + p_win, 1e-9) * np.pi / 2, -1, 1)
    lo, hi = mean * (1 - np.abs(a)), mean * (1 + np.abs(a))
    summer_dry = a < 0
    dry_s, wet_s = np.where(summer_dry, lo, mean), np.where(summer_dry, mean, hi)
    dry_w, wet_w = np.where(summer_dry, mean, lo), np.where(summer_dry, hi, mean)
    driest = lo
    P, T = p_ann, temp
    # months above 10 C on a sinusoidal year
    amp = np.maximum((t_warm - t_cold) / 2, 1e-6)
    m10 = 12 * np.arccos(np.clip((10 - T) / amp, -1, 1)) / np.pi
    out = np.full(len(elev), -1)

    def put(mask, cid):
        sel = mask & (out < 0)
        out[sel] = cid[sel] if np.ndim(cid) else cid

    sea = elev <= 0
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
           lake: np.ndarray | None = None) -> np.ndarray:
    t, p = temp, precip
    b = np.full(len(elev), -1)
    land = elev > 0

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
            moc_start: dict | None = None) -> dict:
    """The whole climate for one moment: elevation (m above the current sea
    level; <= 0 is sea), the global temperature offset dT from today's Earth,
    axial tilt and land ice (m). melt: fresh water from shrinking ice sheets,
    m/yr per cell (on land it runs off to the sea; see ocean.py), none in
    the main run; moc_start: an earlier call's moc_state, to start the
    overturning from (see ocean.solve). Returns a dict of per-cell arrays:
      temp, t_warm, t_cold   C: annual mean, warmest and coldest month
      precip, p_jul, p_jan   mm/yr: annual, and the rate in each half-year
      koppen                 KOPPEN id
      sst                    C: sea-surface temperature (annual)
      sst_jul, sst_jan       C: ... in July and January (the peak months of the sea's
                             seasonal swing, as t_warm / t_cold; not below freezing)
      dew_jul, dew_jan       C: dew point of the air near the ground, July / January
                             half-year (humidity())
      rh_jul, rh_jan         %: relative humidity, July / January half-year
      wind_jul, wind_jan     tangent vectors, ~1 = a steady trade wind
      current                tangent vectors of the surface ocean currents
      jet_jul, jet_jan       tangent vectors, m/s: the upper-level wind (jet stream)
      pet, aet, runoff       mm/yr: potential and actual evaporation, and what runs
                             off into rivers (0 at sea; see water_balance)
      lake_evap              mm/yr: evaporation from open water (lakes)
      sss                    psu: sea-surface salinity (S0 on land)
      density, density_winter  kg/m3: surface sea water, annual and coldest month
      overturning            Sv per cell: deep water sinking there
      moc_inflow             Sv per cell width: the warm surface inflow feeding the sinking
      moc_heat               C: how much the overturning warms (cools) the sea surface
      freshwater             m/yr: net fresh water into the sea (rain + rivers + ice and
                             meltwater - evaporation), global mean taken off
      sea_evap               mm/yr: evaporation from the sea
      sea_ice_growth         m: sea ice frozen per winter
    and ground: (t_warm, t_cold, temp) of the bare ground under the ice (ice_surface
    turns them back into the ice's), moc_sites: a list of dicts per sinking site (lat, lon, sv, drho,
    area_km2, heat_pw) and moc_state, a dict to pass on as moc_start.
    Order: a first guess of temperatures by latitude, height and distance
    from the sea -> seasonal winds from the land-sea contrast -> ocean
    currents and sea-surface temperature -> air temperatures carried by the
    winds -> rain in each half-year -> wet ground cools the summer ->
    salinity and the overturning (ocean.py), whose heat is then added to
    the sea and air temperatures."""
    tune = {**TUNE, **(tune or {})}
    n = grid.n
    ocean = elev <= 0
    land = ~ocean
    ice = np.zeros(n) if ice is None else ice
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
    sea_half = tune["sea_half"] * s

    # Winds for each half-year (Apr-Sep 'jul', Oct-Mar 'jan'). Rain is a
    # half-year mean, so the winds and rain use the half-years' mean
    # conditions: a sine averages 2/pi (hk) of its peak.
    hk = tune["hk"]
    shift = hk * tune["belt_shift"] * tilt / 23.4
    warm0, cold0 = seasons(grid, elev, temp0, tilt)
    lift = LAPSE * np.maximum(surf, 0)  # back to sea level, for pressure
    t_sl0 = np.where(ocean, t_sea_air, 0.5 * (warm0 + cold0) + lift)
    dsl = np.where(ocean, sea_half, 0.5 * (warm0 - cold0)) * sgn * hk
    t_sl_jul, t_sl_jan = t_sl0 + dsl, t_sl0 - dsl
    v_jul, _ = monsoon_wind(grid, t_sl_jul, shift, tune["monsoon"], tune["big"], tune["big_km"])
    v_jan, _ = monsoon_wind(grid, t_sl_jan, -shift, tune["monsoon"], tune["big"], tune["big_km"])
    v_jul, v_jan = deflect(grid, v_jul, surf, tune), deflect(grid, v_jan, surf, tune)
    v_ann = 0.5 * (v_jul + v_jan)

    cur, away = currents(grid, ocean, v_ann, tune)

    raw0, _ = sea_surface(grid, ocean, t_sea, v_ann, upwelling=tune["coast_up"], eq_upwelling=tune["eq_up"],
                          tune=tune, cur=cur, away=away)

    def sst_of(share, t_in):  # (with the overturning's inflow)
        t, _ = sea_surface(grid, ocean, t_sea, v_ann, tune=tune, cur=cur, away=away, share=share, t_in=t_in,
                           base=raw0)
        return np.maximum(t, FREEZE)

    sst0 = sst = np.maximum(raw0, FREEZE)
    v_sum = np.where(north[:, None], v_jul, v_jan)  # each hemisphere's summer wind
    v_win = np.where(north[:, None], v_jan, v_jul)
    lift = LAPSE * np.maximum(surf, 0)
    air = dict(grid=grid, ocean=ocean, temp0=temp0, lift=lift, t_sea_air=t_sea_air, t_sea=t_sea, s=s,
               sea_half=sea_half, v_sum=v_sum, v_win=v_win, tune=tune)
    t_warm, t_cold, temp, open_w = _air_temps(sst=sst, **air)

    # rain in each half-year, from its mean conditions
    tm = 0.5 * (t_warm + t_cold)
    dt = hk * (np.where(north, t_warm, t_cold) - tm)
    sst_jul = np.maximum(sst + sgn * hk * sea_half, FREEZE)
    sst_jan = np.maximum(sst - sgn * hk * sea_half, FREEZE)
    # the jet stream over each half-year's temperatures steers its storms
    jets, tracks = [], []
    for t_s in season_temps(grid, surf, t_warm, t_cold, hk):
        j, baro = jet_stream(grid, t_s, tune)
        jets.append(j)
        tracks.append(storm_track(grid, j, baro, tune))
    (r_jul, r_jan), (e_jul, e_jan), (q_jul, q_jan) = rain(
        grid, elev, [_season_inputs(grid, elev, tm + dt, sst_jul, v_jul, shift, t_sl_jul, tune, tracks[0]),
                     _season_inputs(grid, elev, tm - dt, sst_jan, v_jan, -shift, t_sl_jan, tune, tracks[1])],
        tune)
    wet = np.exp(0.03 * dT)  # a warmer world is a wetter one
    scale = tune["mean_mm"] * wet / max(0.5 * (r_jul + r_jan).mean(), 1e-12)
    p_jul, p_jan = np.clip(r_jul * scale, 0, 8000), np.clip(r_jan * scale, 0, 8000)
    precip = 0.5 * (p_jul + p_jan)
    # (the rain model lets the air take up water over sea ice too; it doesn't)
    open_y = ocean_mod.open_share(sst, np.minimum(t_sea_air - t_sea, 0.0), sea_half)
    sea_evap = np.where(ocean, 0.5 * (e_jul + e_jan) * scale * open_y, 0.0)
    fin = dict(land=land, north=north, p_jul=p_jul, p_jan=p_jan, ice=ice, ocean=ocean, tune=tune,
               cover=ice_cover(grid, ice, land, tune))
    t_warm, t_cold, temp, ground = _land_finish(t_warm, t_cold, temp, **fin)
    wb = water_balance(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, tune)

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
    oc = ocean_mod.solve(grid, ocean, sst_of, sst0, t_sea, cur, fw["total"], ice_m, sea_half, tune, moc_start,
                         np.where(ocean, np.clip(1.0 - 2.0 * open_y, 0.0, 1.0), 0.0), -elev)
    if oc["sites"]:
        sst = oc["sst"]
        t_warm, t_cold, temp, _ = _air_temps(sst=sst, **air)
        t_warm, t_cold, temp, ground = _land_finish(t_warm, t_cold, temp, **fin)
        wb = water_balance(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, tune)
    k = koppen(elev, temp, t_warm, t_cold, precip, p_jul, p_jan, grid.lat, ice)
    wb["runoff"] = np.where(land, wb["runoff"], 0.0)
    # July / January: the sea's peak months (where it is iced over most of
    # the year, the summer's heat goes into melting the ice: a smaller
    # swing), and the half-years' humidity
    swing = sgn * sea_half * np.clip((sst - FREEZE) / 4.0, 0.1, 1.0)
    sst_m = (np.maximum(sst + swing, FREEZE), np.maximum(sst - swing, FREEZE))
    tm = 0.5 * (t_warm + t_cold)
    dt = hk * (np.where(north, t_warm, t_cold) - tm)
    (dew_jul, rh_jul), (dew_jan, rh_jan) = humidity(q_jul, tm + dt, tune), humidity(q_jan, tm - dt, tune)
    return dict(temp=temp, t_warm=t_warm, t_cold=t_cold, precip=precip, p_jul=p_jul, p_jan=p_jan, koppen=k,
                sst=sst, sst_jul=sst_m[0], sst_jan=sst_m[1], dew_jul=dew_jul, dew_jan=dew_jan, rh_jul=rh_jul,
                rh_jan=rh_jan, wind_jul=v_jul, wind_jan=v_jan, current=cur, jet_jul=jets[0], jet_jan=jets[1], **wb,
                sss=oc["sss"], density=oc["density"], density_winter=oc["density_w"], overturning=oc["sinking"],
                moc_inflow=oc["inflow"], moc_heat=np.where(ocean, sst - sst0, 0.0), freshwater=fw["total"],
                sea_evap=sea_evap, sea_ice_growth=ice_m, moc_sites=oc["sites"],
                moc_state=oc["state"], ground=ground)


def _air_temps(grid, ocean, sst, temp0, lift, t_sea_air, t_sea, s, sea_half, v_sum, v_win, tune):
    """Each place takes on the temperature of the air the wind brings it.
    Air over land drifts toward the land's own temperature for the
    season (land holds little heat: hot summers, cold winters) over a few
    hundred km; air over open sea has the water's temperature (mild
    winters, cool summers). So in the westerlies the west coasts get sea
    air (Ireland, Vancouver), the east coasts and interiors land air, and
    where the winter wind blows from the north (the east sides of
    continents) it brings the cold with it. A frozen sea moderates
    nothing: the air over winter sea ice is as cold as over land.
    Returns (t_warm, t_cold, temp, open water in winter 0..1)."""
    half_l = tune["continental"] * s + 0.3  # land left to itself
    t_land = temp0 + lift  # (carried at sea level; heights are taken off after)
    open_w = ocean * np.clip((sst - sea_half - FREEZE) / 2.0, 0, 1)  # open water in winter
    eq_s = np.where(ocean, sst + sea_half, t_land + half_l)
    eq_w = np.where(ocean, open_w * (sst - sea_half) + (1 - open_w) * (t_land - half_l), t_land - half_l)
    h = _geom(grid)["h"]
    k_s = np.where(ocean, 0.0, np.exp(-h / tune["air_km_s"]))
    k_w = np.where(ocean, 0.0, np.exp(-h / tune["air_km_w"]))
    t_warm = carry(grid, v_sum, (1 - k_s) * eq_s, k_s, 4 * tune["air_km_s"], 0.25)
    t_cold = carry(grid, v_win, (1 - k_w) * eq_w, k_w, 4 * tune["air_km_w"], 0.25)
    # right at a coast the sea's air mixes in anyway (sea breezes, fog)
    sea_n, open_n = _nbr_mean(grid, ocean.astype(float)), _nbr_mean(grid, open_w)
    c_s, c_w = tune["coast"] * sea_n, tune["coast"] * open_n
    sea_s = _nbr_mean(grid, np.where(ocean, eq_s, 0.0)) / np.maximum(sea_n, 1e-9)
    sea_w = _nbr_mean(grid, np.where(ocean, eq_w, 0.0) * open_w) / np.maximum(open_n, 1e-9)
    t_warm = (1 - c_s) * t_warm + c_s * sea_s - lift
    t_cold = (1 - c_w) * t_cold + c_w * sea_w - lift
    temp = 0.5 * (t_warm + t_cold)
    # over the sea: the water's temperature (the air over sea ice is colder)
    t_ice = 3.0 * np.minimum(t_sea_air - t_sea, 0)
    temp = np.where(ocean, sst + t_ice, temp)
    t_warm = np.where(ocean, sst + sea_half + t_ice, t_warm)
    t_cold = np.where(ocean, sst - sea_half + 1.5 * t_ice, t_cold)
    return t_warm, t_cold, temp, open_w


def _land_finish(t_warm, t_cold, temp, land, north, p_jul, p_jan, ice, cover, ocean, tune):
    """The rain's and the ice's effect on the land's temperatures. Returns
    (t_warm, t_cold, temp) on the ice surface and the same three for the
    bare ground under it (see ice_surface)."""
    # Wet ground and plants spend the summer sun on evaporating water rather
    # than on heating the air: rainy summers stay cooler, droughty ones and
    # deserts get hotter (Houston vs Phoenix). (The rain kernel feels this too.)
    p_sum = np.where(north, p_jul, p_jan)
    dry = 1.0 - 2.0 * np.clip(np.log10(np.maximum(p_sum, 1.0) / 100.0) / 1.2, 0, 1)  # +1 desert .. -1 wet
    t_warm = np.where(land, t_warm + tune["evap_cool"] * dry, t_warm)
    temp = np.where(land, temp + 0.5 * tune["evap_cool"] * dry, temp)
    # (near the equator the rainy 'summer' can be the cooler half-year:
    # warmest and coldest are whichever is warmer and colder)
    t_warm, t_cold = np.maximum(t_warm, t_cold), np.minimum(t_warm, t_cold)
    # the bare ground under the ice: its own height, no white surface
    up = LAPSE * np.where(land, ice, 0.0)
    ground = (t_warm + up, t_cold + up, temp + up)
    return (*ice_surface(*ground, np.where(land, ice, 0.0), cover, tune), ground)


def ice_cover(grid: Grid, ice: np.ndarray, land: np.ndarray, tune: dict | None = None) -> np.ndarray:
    """How much (0..1) of ice_cooling land ice (m) gets: the share of the land
    within ~ice_cool_km that is under ice (~1 on and around a big sheet,
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


def ice_cooling(ice, cover, tune=None):
    """C: how much colder land ice (m) keeps its own surface (its white top,
    the cold air pooling on it): in full on a big polar sheet, little on a
    small mountain cap that sits in the warmer air around it, none in the
    tropics (a cap like Quelccaya's is barely colder than the rock beside
    it). cover: ice_cover."""
    tune = TUNE if tune is None else tune
    return tune["ice_cooling"] * (ice > 0) * cover


def ice_surface(t_warm, t_cold, temp, ice, cover, tune=None):
    """Temperatures on top of land ice (m; 0 = bare ground), from those of
    the bare ground under it: the ice's own height (lapse rate), and its
    white surface. An ice sheet keeps itself cold: it reflects most of the
    sunshine, and in summer melting holds it near 0 C however warm the air
    (Antarctica's coast reaches ~0 C in summer, its plateau ~-30 C). So
    once ice has formed it outlasts the climate that made it (but see
    earth.ice_sheets: only partly). cover: ice_cover."""
    on_ice = ice > 0
    up = LAPSE * ice
    t_warm, t_cold, temp = t_warm - up, t_cold - up, temp - up
    cool = ice_cooling(ice, cover, tune)
    temp, t_cold = temp - cool, t_cold - cool
    t_warm = np.where(on_ice, np.minimum(t_warm - cool, 0.5 * np.maximum(t_warm - cool, 0)), t_warm)
    # (the melting cap can hold an ice sheet's summer below what its year
    # would average: then it's that cold all year)
    temp = np.minimum(temp, t_warm)
    t_cold = np.minimum(t_cold, temp)
    return t_warm, t_cold, temp
