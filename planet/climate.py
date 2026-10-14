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
"""

from __future__ import annotations

import numpy as np

from numba import njit

from . import kernels
from .grid import Grid

LAPSE = 6.5 / 1000  # degC per metre
FREEZE = -1.8  # C: sea water freezes
R_KM = 6371.0


def temperature(grid: Grid, elev: np.ndarray, equator_temp: float = 27.8,
                pole_temp: float = -10.4) -> np.ndarray:
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


def sea_temperature(grid: Grid, equator_temp: float = 27.0, pole_temp: float = -7.5) -> np.ndarray:
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
        if len(_GEOM) > 4:
            _GEOM.clear()
        _GEOM[key] = dict(east=east, north=north, src=src, dst=dst, d=d, deg=deg, h=grid.spacing * R_KM)
    return _GEOM[key]


_COARSE = {}


def _coarse(grid: Grid):
    """A coarser icosphere (~900 km cells) for patterns thousands of km
    across: which coarse cell each fine cell falls in, the coarse
    neighbours, and weights to interpolate back smoothly (the nearby coarse
    cells, by distance). Cached."""
    from .grid import build_grid
    key = (id(grid), grid.n)
    if key not in _COARSE:
        cg = build_grid(min(3, grid.level))
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
        if len(_COARSE) > 4:
            _COARSE.clear()
        _COARSE[key] = dict(n=cg.n, cidx=cidx, off=cg.nbr_off, idx=cg.nbr_idx, cand=cand, w=w,
                            h=cg.spacing * R_KM)
    return _COARSE[key]


@njit(cache=True)
def _coarse_smooth(f, cidx, nc, off, idx, iters, cand, w):
    """Average f onto the coarse grid, blur it there (iters neighbour
    averages) and interpolate it back."""
    tot = np.zeros(nc)
    cnt = np.zeros(nc)
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
                          C["cand"], C["w"])


@njit(cache=True)
def _smooth(f, nbr_off, nbr_idx, iters, w):
    f = f.copy()
    g = np.empty_like(f)
    for _ in range(iters):
        for i in range(f.shape[0]):
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += f[nbr_idx[e]]
            g[i] = (1 - w) * f[i] + w * s / (nbr_off[i + 1] - nbr_off[i])
        f[:] = g
    return f


def smooth(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """Blur a field over roughly `km` (Gaussian-ish sigma)."""
    iters = int(round(4 * (km / _geom(grid)["h"]) ** 2))
    if iters <= 0:
        return f.astype(np.float64)
    return _smooth(np.ascontiguousarray(f, np.float64), grid.nbr_off, grid.nbr_idx, iters, 0.5)


def gradient(grid: Grid, f: np.ndarray) -> np.ndarray:
    """Tangent gradient per cell, units of f per km."""
    G = _geom(grid)
    df = f[G["dst"]] - f[G["src"]]
    g = np.zeros((grid.n, 3))
    np.add.at(g, G["src"], G["d"] * df[:, None])
    return g * (2.0 / (G["deg"][:, None] * G["h"]))


def _edge_weights(grid: Grid, v: np.ndarray, allowed: np.ndarray | None = None):
    """Share of each cell's outflow along each directed edge, for flow v.
    allowed: optional per-edge mask (e.g. sea-to-sea only for currents)."""
    G = _geom(grid)
    src = G["src"]
    w = np.maximum((v[src] * G["d"]).sum(1), 0)
    if allowed is not None:
        w = w * allowed
    tot = np.bincount(src, w, grid.n)
    return w / np.maximum(tot[src], 1e-12), tot > 1e-12


@njit(cache=True)
def _relax_along(a, b, src, dst, out_w, deg, nbr_off, nbr_idx, iters, diffusion):
    """Steady state of x = a + b * (upstream x): each cell sees the
    flow-weighted mean of the cells feeding it (its own value if none), mixed
    a little with its neighbours. Used to carry heat with ocean currents and
    air temperatures with the wind."""
    n = a.shape[0]
    x = a.copy()
    num = np.empty(n)
    den = np.empty(n)
    for _ in range(iters):
        num[:] = 0.0
        den[:] = 0.0
        for e in range(src.shape[0]):
            num[dst[e]] += out_w[e] * x[src[e]]
            den[dst[e]] += out_w[e]
        for i in range(n):
            up = (num[i] + 1e-3 * x[i]) / (den[i] + 1e-3)
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += x[nbr_idx[e]]
            up = (1 - diffusion) * up + diffusion * s / deg[i]
            num[i] = a[i] + b[i] * up
        x[:] = num
    return x


def carry(grid: Grid, v: np.ndarray, a: np.ndarray, b: np.ndarray, km: float = 8000.0,
          diffusion: float = 0.1, allowed=None) -> np.ndarray:
    """Solve x = a + b * (upstream x) along flow v, far enough for signals
    to travel ~km."""
    G = _geom(grid)
    out_w, _ = _edge_weights(grid, v, allowed)
    iters = int(km / G["h"]) + 10
    return _relax_along(a.astype(np.float64), b.astype(np.float64), G["src"], G["dst"], out_w, G["deg"],
                        grid.nbr_off, grid.nbr_idx, iters, diffusion)


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
    psi = np.zeros(n)
    for _ in range(iters):
        for k in range(order.shape[0]):
            i = order[k]
            if not solve[i]:
                continue
            deg = nbr_off[i + 1] - nbr_off[i]
            lap = 4.0 * r / (deg * h * h)
            adv = 2.0 * beta[i] / (deg * h)
            num = 0.0
            den = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                c = lap + adv * east_d[e]
                num += c * psi[nbr_idx[e]]
                den += c
            new = (num - F[i]) / (den + damp)
            psi[i] += omega * (new - psi[i])
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
                eq_upwelling: float = 0.0, tune: dict | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Sea-surface temperature: the latitude's temperature t_eq, moved by the
    currents (warm water poleward along the western side of each ocean, cold
    water toward the equator along the eastern side), plus coastal upwelling
    where the wind pushes surface water away from a coast (Peru, California,
    Namibia) and equatorial upwelling (eq_upwelling, C). Each band's average
    is kept. Returns (sst, current)."""
    G = _geom(grid)
    tune = {**TUNE, **(tune or {})}
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
    a = np.where(ocean, (1 - keep) * (t_eq - cold), t_eq)
    b = np.where(ocean, keep, 0.0)
    sst = carry(grid, cur, a, b, km=1.5 * tune["cur_max"] * relax_km, diffusion=0.15, allowed=allowed)
    anom = np.where(ocean, sst - t_eq, 0.0)
    anom -= np.where(ocean, zonal_mean(grid, anom, ocean), 0.0)
    return t_eq + anom, cur


# --------------------------------------------------------------------------
# Rain
# --------------------------------------------------------------------------
def _qsat(t, k=0.07):
    """Water the air can hold at t C, relative to 0 C (~3.8 g/kg)."""
    return np.exp(k * t)


LQ = 9.5  # C of moist static energy per unit of vapour (latent heat / heat capacity * 3.8 g/kg)


@njit(cache=True)
def _rain(qs, src_q, ocean, ls_rate, cv_rate, mse_t, mse_thr, warm, move, diffusion, out_w,
          src, dst, deg, nbr_off, nbr_idx, iterations, fex, rh_c, rh_pow, cv_scale, et, evap, mean_mm):
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
    and the large-scale part of it."""
    S, n = qs.shape
    m = src_q.copy()
    acc = np.zeros((S, n))
    acc_ls = np.zeros((S, n))
    ema = np.zeros((S, n))  # running mean of each place's rain
    tcor = np.zeros((S, n))  # wet ground cooler, dry ground hotter (C)
    moved = np.empty(n)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        if evap != 0 and it >= 20 and it % 10 == 0:
            tot = 0.0
            for k in range(S):
                for i in range(n):
                    tot += ema[k, i]
            scale = mean_mm * S * n / max(tot, 1e-12)  # model units -> mm/yr
            for k in range(S):
                for i in range(n):
                    if not ocean[i]:
                        lp = np.log10(max(ema[k, i] * scale, 1.0) / 100.0) / 1.2
                        tcor[k, i] = evap * (1.0 - 2.0 * min(max(lp, 0.0), 1.0))
        for k in range(S):
            for i in range(n):
                if ocean[i]:
                    if src_q[k, i] > m[k, i]:
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
                if it >= iterations - tail:
                    acc[k, i] += r
                    acc_ls[k, i] += r_ls
            mk = m[k]
            mv = move[k]
            for i in range(n):
                moved[i] = (1 - mv[i]) * mk[i]
            ow = out_w[k]
            for e in range(src.shape[0]):
                moved[dst[e]] += mv[src[e]] * mk[src[e]] * ow[e]
            dk = diffusion[k]
            for i in range(n):
                t = 0.0
                for e in range(nbr_off[i], nbr_off[i + 1]):
                    t += moved[nbr_idx[e]]
                mk[i] = (1 - dk[i]) * moved[i] + dk[i] * t / deg[i]
    return acc / tail, acc_ls / tail


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


def _season_inputs(grid: Grid, elev, t_air, sst, v, shift, t_sl_season, tune) -> dict:
    """Per-cell inputs of the rain kernel for one season (see _rain).
    t_air: surface air temperature (C, used over land), sst: sea surface
    temperature, v: wind, shift: deg the tropical rain belt is north of the
    equator, t_sl_season: the season's temperatures reduced to sea level."""
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


def rain(grid: Grid, elev, seasons_in: list[dict], tune: dict) -> np.ndarray:
    """Rain rate (model units) per season, [season, cell], from the inputs
    of _season_inputs for each season."""
    G = _geom(grid)
    st = {k: np.ascontiguousarray(np.stack([d[k] for d in seasons_in])) for k in seasons_in[0]}
    iters = int(60 * 2 ** (grid.level - 5)) + 40
    r, r_ls = _rain(st["qs"], st["src_q"], elev <= 0, st["ls"], st["cv"], st["mse_t"], st["mse_thr"],
                    st["warm"], st["move"], st["diff"], st["out_w"], G["src"], G["dst"], G["deg"],
                    grid.nbr_off, grid.nbr_idx, iters, tune["fex"], tune["rh_c"], tune["rh_pow"],
                    tune["cv_scale"], tune["et"], tune["evap_cool"], tune["mean_mm"])
    # Storms carry their rain with them: the large-scale (frontal) rain is
    # spread over a storm's size, so e.g. the storms that brew over warm
    # coastal seas in winter rain on the east coasts even though the mean
    # wind blows offshore there.
    for k in range(len(seasons_in)):
        w = np.clip(tune["storm_mix"] * st["B"][k], 0, 0.9)
        r[k] += w * (smooth(grid, r_ls[k], tune["storm_km"]) - r_ls[k])
    return r


def precipitation(grid: Grid, elev: np.ndarray, temp: np.ndarray, **_):
    """Annual rain without seasons (generators' quick path): temp is used
    for both the air and the sea surface. Returns (mm/yr, scale)."""
    t_sl = np.where(elev <= 0, temp, temp + LAPSE * np.maximum(elev, 0))
    r = rain(grid, elev, [_season_inputs(grid, elev, temp, temp, wind(grid), 0.0, t_sl, TUNE)], TUNE)[0]
    scale = TUNE["mean_mm"] / max(r.mean(), 1e-12)
    return np.clip(r * scale, 0, 6000), scale


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
    ice_cooling=10.0,  # C: how much colder an ice sheet's surface is than bare ground would be
    belt_shift=10.0,  # deg the tropical rain belt follows the sun at the solstice (times tilt/23.4)
    hk=0.64,  # the half-years' mean of a seasonal swing (2/pi of the peak, for a sine)
    monsoon=1.0,  # strength of the land-sea pressure winds ...
    big=1.5,  # ... and of their continent-wide part
    big_km=2000.0,  # km: the scale of that part
    eq_up=15.0,  # C: equatorial upwelling (cold tongues) under a full trade wind
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
)


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
            ice: np.ndarray | None = None, tune: dict | None = None) -> dict:
    """The whole climate for one moment: elevation (m above the current sea
    level; <= 0 is sea), the global temperature offset dT from today's Earth,
    axial tilt and land ice (m). Returns a dict of per-cell arrays:
      temp, t_warm, t_cold   C: annual mean, warmest and coldest month
      precip, p_jul, p_jan   mm/yr: annual, and the rate in each half-year
      koppen                 KOPPEN id
      sst                    C: sea-surface temperature (annual)
      wind_jul, wind_jan     tangent vectors, ~1 = a steady trade wind
      current                tangent vectors of the surface ocean currents
    Order: a first guess of temperatures by latitude, height and distance
    from the sea -> seasonal winds from the land-sea contrast -> ocean
    currents and sea-surface temperature -> air temperatures carried by the
    winds -> rain in each half-year -> wet ground cools the summer."""
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
    v_ann = 0.5 * (v_jul + v_jan)

    sst, cur = sea_surface(grid, ocean, t_sea, v_ann, eq_upwelling=tune["eq_up"], tune=tune)
    sst = np.maximum(sst, FREEZE)

    # Each place takes on the temperature of the air the wind brings it.
    # Air over land drifts toward the land's own temperature for the
    # season (land holds little heat: hot summers, cold winters) over a few
    # hundred km; air over open sea has the water's temperature (mild
    # winters, cool summers). So in the westerlies the west coasts get sea
    # air (Ireland, Vancouver), the east coasts and interiors land air, and
    # where the winter wind blows from the north (the east sides of
    # continents) it brings the cold with it. A frozen sea moderates
    # nothing: the air over winter sea ice is as cold as over land.
    v_sum = np.where(north[:, None], v_jul, v_jan)  # each hemisphere's summer wind
    v_win = np.where(north[:, None], v_jan, v_jul)
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

    # rain in each half-year, from its mean conditions
    tm = 0.5 * (t_warm + t_cold)
    dt = hk * (np.where(north, t_warm, t_cold) - tm)
    sst_jul = np.maximum(sst + sgn * hk * sea_half, FREEZE)
    sst_jan = np.maximum(sst - sgn * hk * sea_half, FREEZE)
    r_jul, r_jan = rain(grid, elev, [_season_inputs(grid, elev, tm + dt, sst_jul, v_jul, shift, t_sl_jul, tune),
                                     _season_inputs(grid, elev, tm - dt, sst_jan, v_jan, -shift, t_sl_jan, tune)],
                        tune)
    wet = np.exp(0.03 * dT)  # a warmer world is a wetter one
    scale = tune["mean_mm"] * wet / max(0.5 * (r_jul + r_jan).mean(), 1e-12)
    p_jul, p_jan = np.clip(r_jul * scale, 0, 8000), np.clip(r_jan * scale, 0, 8000)
    precip = 0.5 * (p_jul + p_jan)
    # Wet ground and plants spend the summer sun on evaporating water rather
    # than on heating the air: rainy summers stay cooler, droughty ones and
    # deserts get hotter (Houston vs Phoenix). (The rain kernel feels this too.)
    p_sum = np.where(north, p_jul, p_jan)
    dry = 1.0 - 2.0 * np.clip(np.log10(np.maximum(p_sum, 1.0) / 100.0) / 1.2, 0, 1)  # +1 desert .. -1 wet
    t_warm = np.where(land, t_warm + tune["evap_cool"] * dry, t_warm)
    temp = np.where(land, temp + 0.5 * tune["evap_cool"] * dry, temp)
    # An ice sheet keeps itself cold: its white surface reflects most of the
    # sunshine, and in summer melting holds it near 0 C however warm the air
    # (Antarctica's coast reaches ~0 C in summer, its plateau ~-30 C). So
    # once ice has formed it outlasts the climate that made it.
    # (near the equator the rainy 'summer' can be the cooler half-year:
    # warmest and coldest are whichever is warmer and colder)
    t_warm, t_cold = np.maximum(t_warm, t_cold), np.minimum(t_warm, t_cold)
    on_ice = (ice > 0) & ~ocean
    cool = tune["ice_cooling"] * on_ice
    temp, t_cold = temp - cool, t_cold - cool
    t_warm = np.where(on_ice, np.minimum(t_warm - cool, 0.5 * np.maximum(t_warm - cool, 0)), t_warm)
    # (the melting cap can hold an ice sheet's summer below what its year
    # would average: then it's that cold all year)
    temp = np.minimum(temp, t_warm)
    t_cold = np.minimum(t_cold, temp)
    k = koppen(elev, temp, t_warm, t_cold, precip, p_jul, p_jan, grid.lat, ice)
    return dict(temp=temp, t_warm=t_warm, t_cold=t_cold, precip=precip, p_jul=p_jul, p_jan=p_jan, koppen=k,
                sst=sst, wind_jul=v_jul, wind_jan=v_jan, current=cur)
