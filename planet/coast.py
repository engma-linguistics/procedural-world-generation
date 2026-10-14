"""Waves and tides at the coast, and how they shape a delta.

Real deltas differ by what reworks the river's sediment at the mouth
(Galloway's triangle): the river itself (Mississippi: long distributaries
into calm water), the waves (Nile, Sao Francisco: a smooth arc of beach
ridges, few mouths) or the tides (Ganges-Brahmaputra, Mekong, Fly: funnel-
shaped channels, elongate islands, tidal flats). This module estimates the
two marine forces per ocean cell from the world's winds and sea floor, and
weighs them against a river's sediment supply.

Wave power (world layer `wave_power`, kW per m of wave crest)
--------------------------------------------------------------
Waves are made by wind blowing over open water: the longer the stretch of
water upwind (the fetch) and the stronger the wind, the bigger the waves,
up to a "fully developed" sea for that wind (Pierson-Moskowitz):
    Hs = 0.24 U^2 / g,  Te = 6.75 U / g,  P = rho g^2 Hs^2 Te / (64 pi) = 0.49 Hs^2 Te kW/m
(U wind speed m/s, Hs significant wave height m, Te energy period s). A
younger sea grows with fetch F as P ~ F^(4/3) (Hs ~ F^(1/2), Te ~ F^(1/3);
JONSWAP), reaching full development at g F / U^2 ~ 22,000 (~400 km in a
13 m/s gale). Once the wind drops, the waves carry on as swell, losing
energy slowly (e-folding over L_SWELL km), so a coast also gets the swell
of storms thousands of km away (Southern Ocean swell on Chile, Cape Town,
Western Australia; North Atlantic swell on Ireland and Portugal).

For each ocean cell, rays are traced outward over the sea in N_DIR
directions, up to D_MAX km or the first land (or winter sea ice). Walking
back in along each ray, the sea state travelling toward the cell grows,
using the "equivalent fetch" method, under each stretch's wind component
along the ray (directional spreading ~cos^2 around the wind), decays as
swell where the wind is weaker or contrary, and loses energy to bottom
friction over shallow shelves (wide shallow shelves like the Gulf of
Mexico's or the North Sea's take the edge off). Summing the directions
gives the power arriving at the cell. A coast in the lee of land gets
little: every ray toward the sea is short, and the waves in the long ones
travel away from it.

Wind speed: the climate's half-year mean winds are vectors (~1 = a steady
trade wind, ~7 m/s). Wave power grows as ~U^5, so storms dominate; the
effective wind is U_TRADE x |wind| + U_STORM x storminess along the jet's
storm tracks (climate.storm_track, ~1 in a mid-latitude winter), in each
half-year, averaged. Calibrated on Earth (tools/coast_check.py).

Tidal range (world layer `tide_range`, m, mean spring-ish range)
-----------------------------------------------------------------
A crude physical proxy, in three factors:
1. Connection to the open ocean. The tide is a wave raised in the big
   ocean basins (R_OPEN = 2 m: the range on an open-ocean coast with a
   narrow shelf, before the factors below). A sea joined to the ocean only
   through narrow, shallow straits co-oscillates weakly, and a basin too
   small to raise its own tide has almost none (the Mediterranean, Baltic
   and Black Sea: a few cm to ~0.3 m). Cells from which most directions
   reach > D_OPEN km of open water are "open ocean" (connection 1); from
   there the tide spreads over the sea as a screened diffusion whose
   conductance between cells is their depth (shallow straits choke it),
   decaying over ~L_TIDE km. A sea with no ocean connection at all gets
   only its own small tide, growing with its size.
2. Shelf resonance and shoaling. On a continental shelf of width W and
   depth h the tide is a standing wave; it resonates when W is near a
   quarter of the tidal wavelength sqrt(g h) x 12.42 h (~300 km on a 80 m
   shelf): amplification 1 / sqrt(cos^2(2 pi W / lambda) + r^2), r a
   friction term (Bay of Fundy, Patagonia, NW Australia, the Yellow Sea).
   Shelves far wider than that lose the tide to friction instead (Siberia).
3. Funnelling. A tide running into a narrowing embayment is squeezed
   (Green's law: amplitude ~ width^-1/2): the fewer directions open to
   the sea within R_NEAR km, the bigger the tide (the head of the Bay of
   Bengal, the Gulf of Khambhat, the Gulf of California). Headlands and
   islands get smaller tides.

Both layers are computed on ocean cells only (0 on land).

Galloway weights (galloway())
-----------------------------
At a river mouth, three sediment fluxes are compared (after Nienhuis et
al. 2015, 2020, Nature, who put numbers on Galloway's triangle):
- river: the sediment the river brings, from the BQART model (Syvitski &
  Milliman 2007): Qs = 0.0006 B Q^0.31 A^0.5 R T  Mt/yr (Q km^3/yr, A
  catchment km^2, R its relief km, T its mean temperature C; B is higher
  for soft rock / sediment cover and glaciers);
- waves: the most sediment the waves can carry along the coast (CERC
  formula, deep-water form, at the angle of maximum transport):
  Qw = 0.14 Hs^2.4 Te^0.2 m^3/s, with Hs and Te
  from the wave power;
- tides: the river's sediment concentration carried by the tidal water
  flux instead of the river's: Qt = Qs x Q_tide / Q, where Q_tide = 2 x
  tidal prism / tidal period, the prism being the water that floods the
  channels and the low delta plain at high tide (tidal_prism: none of the
  plain for a microtidal sea, a wide belt for a macrotidal one).
Weights = each flux / their sum. They shape the zoom's delta continuously
(zoom.py); the dominant type is the largest weight (and "mixed" when none
reaches 0.5).
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange

from . import climate
from .geo import R_KM
from .kernels import walk_nearest

GRAV = 9.81
# waves
U_TRADE = 6.5  # m/s for a climate wind vector of length 1
U_STORM = 6.0  # m/s added at storminess 1 (a mid-latitude winter storm track)
N_DIR = 16  # ray directions
D_MAX = 6000.0  # km: the farthest swell is traced from
L_SWELL = 8000.0  # km: swell energy e-folding distance
# The wind isn't steady: for a Weibull (k = 2) spread of speeds about a mean
# U, the mean of U^5 (wave power ~ U^5) is 6.1 x U^5, as for a steady wind
# 6.1^(1/5) = 1.43 x faster.
GUST = 1.43
T_STORM = 12.0  # hours a storm's wind blows over the same sea (duration-limited growth)
LAND_SLOW, L_RECOVER = 0.5, 600.0  # wind off land: slower by this share, recovering over this many km of sea
STORM_ZONAL = 0.5  # share of the storminess taken from the latitude belt (rest: the jet's storm tracks)
SHELF_FRIC_KM, SHELF_FRIC_M = 250.0, 35.0  # bottom friction: e-folding km at the coast's depth scale
# tides
R_OPEN = 2.0  # m: tidal range on an open-ocean coast with a narrow shelf
D_OPEN = 2500.0  # km of open water (direction mean) that makes a cell "open ocean"
OPEN_FRAC = 0.55  # ... as a share of the D_OPEN-capped mean reach
L_TIDE = 3000.0  # km the tide spreads (deep water) from the open ocean into seas
CONN_POW = 1.0  # the tide's amplitude goes as the connection to this power
H_COND = 150.0  # m: depth at which a passage conducts the tide fully
SHELF_BREAK = 200.0  # m: shelf / slope boundary
R_FRIC = 0.3  # shelf resonance friction term
L_SHELF_FRIC = 1200.0  # km: decay of the tide over a shelf wider than lambda/4
R_NEAR = 300.0  # km: the reach that counts a direction as open to the sea (funnelling)
SELF_KM = 5000.0  # km: a sea this wide (sqrt of its area) raises a full tide on its own
T_M2 = 44712.0  # s: the main lunar tide's period


@njit(cache=True)
def _wsat(u):
    """Fully developed sea for wind u (m/s): power kW/m."""
    hs = 0.24 * u * u / GRAV
    te = 6.75 * u / GRAV
    return 0.49 * hs * hs * te


def hs_te(power_kw):
    """Significant wave height (m) and energy period (s) of a sea of the
    given power (kW/m), assuming a fully developed wind sea (Te = 4.4 Hs^0.5)."""
    hs = (np.maximum(power_kw, 0.0) / 2.16) ** 0.4
    return hs, 4.4 * np.sqrt(hs)


@njit(cache=True)
def _basis(p):
    if abs(p[2]) < 0.999:
        e1 = np.array([-p[1], p[0], 0.0])
    else:
        e1 = np.array([1.0, 0.0, 0.0]) - p[0] * p
    e1 /= np.sqrt(e1[0] ** 2 + e1[1] ** 2 + e1[2] ** 2)
    e2 = np.array([p[1] * e1[2] - p[2] * e1[1], p[2] * e1[0] - p[0] * e1[2], p[0] * e1[1] - p[1] * e1[0]])
    return e1, e2


@njit(cache=True)
def _march(c0, k, ndir, step_rad, nsteps, centers, nbr_off, nbr_idx, land, cells):
    """Cells along the great circle from cell c0 in direction k of ndir,
    every step_rad, up to nsteps steps or the first land cell (included).
    Fills cells; returns how many."""
    p0 = centers[c0]
    e1, e2 = _basis(p0)
    a = 2 * np.pi * (k + 0.5) / ndir
    d0 = np.cos(a) * e1 + np.sin(a) * e2
    cur = c0
    m = 0
    q = np.empty(3)
    for j in range(nsteps + 1):
        s = j * step_rad
        for t in range(3):
            q[t] = np.cos(s) * p0[t] + np.sin(s) * d0[t]
        cur = walk_nearest(q, cur, centers, nbr_off, nbr_idx)
        cells[j] = cur
        m = j + 1
        if land[cur]:
            break
    return m, p0, d0


@njit(cache=True, parallel=True)
def _wave_rays(targets, centers, nbr_off, nbr_idx, land, blocked, U, wdir, kfric, ndir, step_km, nsteps,
               l_swell, radius, land_slow, l_recover, t_storm):
    """Wave power (kW/m) arriving at each target cell, per season (see the
    module docstring). blocked[s]: land or sea ice in season s; U[s]: wind
    speed m/s; wdir[s]: unit wind direction (zero where calm); kfric: bottom
    friction per km. Wind coming off land is slowed by the land's roughness
    (by land_slow) and recovers over the sea over ~l_recover km (the marine
    boundary layer): over a small sea the wind never gets up to speed.)"""
    ns = U.shape[0]
    out = np.zeros((targets.shape[0], ns))
    step_rad = step_km / radius
    wk = 4.0 / ndir  # sum over directions of cos^2 (on the downwind half) = ndir / 4
    for t in prange(targets.shape[0]):
        cells = np.empty(nsteps + 1, np.int64)
        for k in range(ndir):
            m, p0, d0 = _march(targets[t], k, ndir, step_rad, nsteps, centers, nbr_off, nbr_idx, land, cells)
            for s in range(ns):
                W = 0.0
                sea_km = 0.0 if land[cells[m - 1]] else 1e9  # open water upwind along the ray
                for j in range(m - 1, -1, -1):
                    c = cells[j]
                    if blocked[s, c]:
                        W = 0.0
                        sea_km = 0.0
                        continue
                    sea_km += step_km
                    sa = j * step_rad
                    # the waves travel inward: minus the ray's outward tangent
                    cosd = 0.0
                    for i in range(3):
                        cosd += wdir[s, c, i] * (np.sin(sa) * p0[i] - np.cos(sa) * d0[i])
                    u = U[s, c] * (1.0 - land_slow * np.exp(-sea_km / l_recover))
                    grew = False
                    if cosd > 0.0 and u > 0.5:
                        fs = 2.2e4 * u * u / GRAV / 1000.0  # km to full development
                        # a storm blows for only ~t_storm: the sea gets no older than that
                        # (JONSWAP: g F / U^2 = (g t / (68.8 U))^1.5)
                        fd = (GRAV * t_storm / (68.8 * u)) ** 1.5 * u * u / GRAV / 1000.0
                        ws = _wsat(u) * cosd * cosd * min(fd / fs, 1.0) ** (4.0 / 3.0)
                        fs = min(fs, fd)
                        if W < ws:
                            feq = fs * (W / ws) ** 0.75 + step_km
                            W = ws * min(feq / fs, 1.0) ** (4.0 / 3.0)
                            grew = True
                    if not grew:
                        W *= np.exp(-step_km / l_swell)
                    W *= np.exp(-step_km * kfric[c])
                out[t, s] += wk * W
    return out


@njit(cache=True, parallel=True)
def _reach(targets, centers, nbr_off, nbr_idx, land, ndir, step_km, nsteps, radius):
    """Distance (km) over the sea from each target to the first land, in
    each of ndir directions (capped at nsteps x step_km)."""
    out = np.empty((targets.shape[0], ndir))
    step_rad = step_km / radius
    for t in prange(targets.shape[0]):
        cells = np.empty(nsteps + 1, np.int64)
        for k in range(ndir):
            m, _, _ = _march(targets[t], k, ndir, step_rad, nsteps, centers, nbr_off, nbr_idx, land, cells)
            out[t, k] = (m - 1) * step_km if land[cells[m - 1]] else nsteps * step_km
    return out


@njit(cache=True)
def _tide_spread(fixed, val, cond_e, decay, nbr_off, nbr_idx, ocean, iters):
    """Steady state of x_i = (decay * 0 + sum_j c_ij x_j) / (decay + sum_j c_ij)
    over the ocean, with x held at val where fixed (Gauss-Seidel)."""
    n = val.shape[0]
    x = val.copy()
    for _ in range(iters):
        for i in range(n):
            if fixed[i] or not ocean[i]:
                continue
            num = 0.0
            den = decay
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if ocean[j]:
                    num += cond_e[e] * x[j]
                    den += cond_e[e]
            x[i] = num / den
    return x


def _season_winds(grid, elev, c, ice):
    """Per half-year (jul, jan): effective wind speed (m/s), unit direction,
    and the sea-ice mask, from climate.compute's output c."""
    surf = elev + ice
    tracks = []
    temps = climate.season_temps(grid, surf, c["t_warm"], c["t_cold"], climate.TUNE["hk"])
    for t_s in temps:
        j, baro = climate.jet_stream(grid, t_s)
        tr = climate.storm_track(grid, j, baro, climate.TUNE)
        tracks.append(STORM_ZONAL * climate.storminess(grid, t_s) / 7.0 + (1 - STORM_ZONAL) * tr)
    U, D, icy = [], [], []
    ocean = elev <= 0
    for v, tr, t_s in zip((c["wind_jul"], c["wind_jan"]), tracks, temps):
        sp = np.linalg.norm(v, axis=1)
        U.append(GUST * (U_TRADE * sp + U_STORM * np.clip(tr, 0, 2)))
        D.append(np.where(sp[:, None] > 1e-6, v / np.maximum(sp, 1e-6)[:, None], 0.0))
        icy.append(ocean & (t_s < climate.FREEZE))  # the sea freezes over in that half-year
    return np.array(U), np.array(D), np.array(icy)


def wave_power(grid, elev: np.ndarray, c: dict, ice: np.ndarray | None = None) -> np.ndarray:
    """Mean wave power arriving at each ocean cell, kW/m (0 on land). c:
    climate.compute's output for this elevation."""
    elev = np.asarray(elev, float)
    ice = np.zeros(grid.n) if ice is None else np.asarray(ice, float)
    return wave_power_winds(grid, elev, *_season_winds(grid, elev, c, ice))


def wave_power_winds(grid, elev: np.ndarray, U: np.ndarray, D: np.ndarray, icy: np.ndarray) -> np.ndarray:
    """wave_power() from given winds: U (seasons, cells) effective speed m/s,
    D (seasons, cells, 3) unit direction the wind blows toward (0: calm),
    icy (seasons, cells) frozen sea. Mean over the seasons, kW/m."""
    elev = np.asarray(elev, float)
    land = elev > 0
    ocean = ~land
    U, D = np.asarray(U, float), np.asarray(D, float)
    blocked = (np.asarray(icy, bool) | land[None, :]).astype(np.bool_)
    depth = np.maximum(-elev, 1.0)
    kfric = np.exp(-depth / SHELF_FRIC_M) / SHELF_FRIC_KM
    targets = np.flatnonzero(ocean)
    step = 0.45 * grid.spacing * R_KM
    nsteps = int(D_MAX / step)
    p = _wave_rays(targets, grid.centers, grid.nbr_off, grid.nbr_idx, land, blocked, U, np.ascontiguousarray(D),
                   kfric, N_DIR, step, nsteps, L_SWELL, R_KM, LAND_SLOW, L_RECOVER, T_STORM * 3600.0)
    out = np.zeros(grid.n)
    out[targets] = p.mean(1)
    return out


def _shelf_width(grid, elev, ocean):
    """Per ocean cell: shelf width W (km, coast to the shelf break, measured
    from the cell across the shelf to the nearest deeper-than-SHELF_BREAK
    cell) and the shelf depth h (m) the tide wave runs over."""
    from .kernels import bfs_within
    depth = np.where(ocean, -elev, 0.0)
    h = grid.spacing * R_KM
    off = ocean & (depth >= SHELF_BREAK)
    lab = np.where(ocean, 0, -1).astype(np.int64)
    if off.any():
        hops, _ = bfs_within(np.flatnonzero(off).astype(np.int64), lab, grid.nbr_off, grid.nbr_idx, 10 ** 6)
    else:
        hops = np.full(grid.n, -1)
    W = np.where(hops > 0, hops * h, np.where(hops == 0, 0.5 * h * np.clip(SHELF_BREAK / np.maximum(depth, 1.0), 0, 1),
                                              20 * h))
    # the shelf's depth: the cell's own (a shelf cell), else a typical shelf
    hs = np.clip(np.where(depth < SHELF_BREAK, depth, 100.0), 20.0, 150.0)
    return W, hs


def tide_range(grid, elev: np.ndarray, detail: bool = False):
    """Tidal range at each ocean cell, m (0 on land). With detail, also a
    dict of the factors (connection, shelf amplification, funnel, shelf
    width km, openness)."""
    elev = np.asarray(elev, float)
    land = elev > 0
    ocean = ~land
    n = grid.n
    h = grid.spacing * R_KM
    out = np.zeros(n)
    targets = np.flatnonzero(ocean)
    if not len(targets):
        return (out, {}) if detail else out
    step = 0.45 * h
    reach = _reach(targets, grid.centers, grid.nbr_off, grid.nbr_idx, land, N_DIR, step, int(D_OPEN / step), R_KM)
    openness = np.zeros(n)
    openness[targets] = np.minimum(reach, D_OPEN).mean(1) / D_OPEN
    near = np.zeros(n)
    near[targets] = (reach >= R_NEAR).mean(1)
    # 1. connection to the open ocean
    depth = np.where(ocean, -elev, 0.0)
    fixed = ocean & (openness >= OPEN_FRAC)
    src = np.repeat(np.arange(n), np.diff(grid.nbr_off))
    cond = np.clip(np.minimum(depth[src], depth[grid.nbr_idx]) / H_COND, 0.02, 1.0)
    decay = (h / L_TIDE) ** 2 * 6  # a 6-neighbour cell: spreads ~L_TIDE in deep water
    iters = int(4 * (L_TIDE / h) ** 2 / 6) + 50
    conn = _tide_spread(fixed, fixed.astype(float), cond, decay, grid.nbr_off, grid.nbr_idx, ocean, min(iters, 3000))
    # seas without an ocean connection raise their own small tide
    lab, nl = grid.components(ocean)
    size = np.sqrt(np.bincount(lab[ocean], minlength=nl) * 4 * np.pi * R_KM ** 2 / n)
    own = np.clip(size / SELF_KM, 0, 1) ** 2
    own[np.unique(lab[fixed])] = 0.0  # (seas joined to the open ocean get its tide, above)
    conn = np.maximum(conn ** CONN_POW, own[np.maximum(lab, 0)])
    # 2. shelf resonance
    W, hs = _shelf_width(grid, elev, ocean)
    lam = np.sqrt(GRAV * hs) * T_M2 / 1000.0  # km
    kw = 2 * np.pi * W / lam
    amp = 1.0 / np.sqrt(np.cos(np.minimum(kw, np.pi / 2)) ** 2 + R_FRIC ** 2)
    amp *= np.exp(-np.maximum(W - lam / 4, 0) / L_SHELF_FRIC)
    # 3. funnelling
    fun = np.clip((0.5 / np.maximum(near, 1.0 / N_DIR)) ** 0.5, 0.65, 2.2)
    out = np.where(ocean, R_OPEN * conn * amp * fun, 0.0)
    if detail:
        return out, {"connection": conn, "shelf_amp": amp, "funnel": fun, "shelf_km": W, "openness": openness}
    return out


# ---------------------------------------------------------------------------
# Galloway weights at a river mouth
# ---------------------------------------------------------------------------
SEC_PER_YR = 3.156e7
CHANNEL_SHARE = 0.002  # share of the delta plain that is tidal channel
PLAIN_Z0, PLAIN_RISE = 0.8, 10.0  # m: the delta plain's height at the coast, and its rise to its edge (zoom.py)
SED_DENSITY = 1600.0  # kg/m^3: bulk density of deposited sand (2650 x (1 - porosity 0.4))
RIVER_DOMINANT = 0.5  # a weight at least this large names the delta's type


def upstream_cells(down: np.ndarray, mouth: int) -> np.ndarray:
    """The mouth cell and every cell draining to it."""
    down = np.asarray(down, int)
    order = np.argsort(down, kind="stable")
    ds = down[order]
    starts = np.searchsorted(ds, np.arange(len(down)))
    ends = np.searchsorted(ds, np.arange(len(down)), side="right")
    out, stack = [mouth], [mouth]
    while stack:
        i = stack.pop()
        kids = order[starts[i]:ends[i]]
        out.extend(kids.tolist())
        stack.extend(kids.tolist())
    return np.array(out)


def river_sediment(L: dict, basin: np.ndarray, q_m3s: float, cell_area_km2: float) -> float:
    """BQART sediment load (kg/s) of a river with discharge q_m3s draining
    the given cells of world layers L."""
    elev = np.asarray(L["elevation"], float)[basin]
    A = len(basin) * cell_area_km2
    relief = max(float(np.percentile(elev, 98)) / 1000.0, 0.05)  # km: the basin's high ground (robust max)
    T = max(float(np.mean(np.asarray(L["temperature"], float)[basin])), 2.0)
    soft = float(np.mean(np.asarray(L["sediment_cover"], float)[basin] > 0.5)) if "sediment_cover" in L else 0.3
    iced = float(np.mean(np.asarray(L.get("ice", np.zeros(len(L["elevation"]))), float)[basin] > 1))
    B = (0.6 + 1.4 * soft) * (1 + 1.0 * iced)  # lithology (soft sediment erodes easily) x glacial erosion
    Q = q_m3s * SEC_PER_YR / 1e9  # km^3/yr
    mt_yr = 0.0006 * B * Q ** 0.31 * A ** 0.5 * relief * T
    return mt_yr * 1e9 / SEC_PER_YR


def tidal_prism(tide_m: float, plain_km: float) -> float:
    """Water (m^3) flowing in and out of a delta each tide: the channels
    (CHANNEL_SHARE of the plain) times the range, plus the low plain that
    high water floods. The plain is a half-disc of radius plain_km rising
    from PLAIN_Z0 at the coast to PLAIN_Z0 + PLAIN_RISE at its edge as
    (r / R)^1.5 (zoom.py's delta plain); high water stands half the range
    above mean sea level, so a microtidal sea floods none of it."""
    R2 = (plain_km * 1000.0) ** 2
    prism = CHANNEL_SHARE * 0.5 * np.pi * R2 * tide_m
    hw = 0.5 * tide_m
    if hw > PLAIN_Z0:
        rho = np.linspace(0, ((hw - PLAIN_Z0) / PLAIN_RISE) ** (2 / 3), 64)
        depth = hw - PLAIN_Z0 - PLAIN_RISE * rho ** 1.5
        prism += float(np.trapezoid(np.maximum(depth, 0) * np.pi * rho, rho)) * R2
    return prism


def galloway(qs_kgs: float, q_m3s: float, wave_kw: float, tide_m: float, plain_km: float) -> dict:
    """Galloway weights from the river's sediment (kg/s) and water (m^3/s),
    the wave power (kW/m) and tidal range (m) at the mouth, and the delta
    plain radius (km). See the module docstring."""
    hs, te = hs_te(wave_kw)
    qw = 0.14 * hs ** 2.4 * te ** 0.2 * SED_DENSITY  # kg/s
    prism = tidal_prism(tide_m, plain_km)
    q_tide = 2 * prism / T_M2  # m^3/s
    qt = qs_kgs * q_tide / max(q_m3s, 1.0)
    tot = max(qs_kgs + qw + qt, 1e-9)
    w = {"river": qs_kgs / tot, "wave": qw / tot, "tide": qt / tot}
    top = sorted(w, key=lambda k: -w[k])
    kind = f"{top[0]}-dominated" if w[top[0]] >= RIVER_DOMINANT else f"mixed {top[0]}-{top[1]}"
    return {"weights": {k: round(float(v), 3) for k, v in w.items()}, "type": kind,
            "sediment_river_kgs": round(float(qs_kgs), 1), "sediment_wave_kgs": round(float(qw), 1),
            "sediment_tide_kgs": round(float(qt), 1), "tidal_discharge_m3s": round(float(q_tide)),
            "wave_hs_m": round(float(hs), 2), "wave_te_s": round(float(te), 1)}


def plain_radius_km(q_m3s: float, sf: float) -> float:
    """Radius of the delta plain a river builds (zoom.py's delta plain): grows
    with discharge and with the sediment factor sf (0..1, the coarse
    sediment cover offshore). Earth: Nile ~150 km of plain at 2,800 m^3/s,
    Mississippi ~250 km at 17,000, Ganges-Brahmaputra ~350 km."""
    return float(np.clip(10.0 * (q_m3s / 100) ** 0.35 * (0.8 + 0.6 * sf), 15.0, 300.0))


def delta_at(grid, L: dict, mouth: int, q_m3s: float, plain_km: float) -> dict:
    """Galloway weights for the river reaching the sea at land cell `mouth`
    of a world (layers L), with discharge q_m3s and delta plain radius
    plain_km: galloway()'s dict plus the wave power and tidal range used
    (the mean over the sea cells next to the mouth) and whether the world
    has those layers at all ("marine"; without them waves and tides count
    as 0)."""
    from .geo import R_KM
    elev = np.asarray(L["elevation"], float)
    down = np.asarray(L["downstream"], int)
    nb = grid.nbr_idx[grid.nbr_off[mouth]:grid.nbr_off[mouth + 1]]
    wet = np.unique(np.concatenate([[down[mouth]], nb[elev[nb] <= 0]]).astype(int))
    wet = wet[(wet >= 0) & (elev[np.maximum(wet, 0)] <= 0)]
    marine = "wave_power" in L and "tide_range" in L and len(wet) > 0
    wave = float(np.mean(np.asarray(L["wave_power"], float)[wet])) if marine else 0.0
    tide = float(np.mean(np.asarray(L["tide_range"], float)[wet])) if marine else 0.0
    cell_area = 4 * np.pi * R_KM ** 2 / grid.n
    qs = river_sediment(L, upstream_cells(down, int(mouth)), q_m3s, cell_area)
    return {**galloway(qs, q_m3s, wave, tide, plain_km), "wave_power_kw_m": round(wave, 1),
            "tide_range_m": round(tide, 2), "marine": marine}
