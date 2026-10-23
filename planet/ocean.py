"""Sea-surface salinity and the overturning (thermohaline) circulation.

The wind-driven gyres (climate.currents) only stir the top few hundred
metres. Below them the oceans turn over slowly: where the surface water gets
dense enough in winter (cold, and salty), it sinks to the deep ocean and
spreads along the bottom, and warm surface water flows in to replace it. The
Atlantic's overturning is what keeps the Nordic seas open and Norway mild.
Each step is a simplified version of the real mechanism, so it works on any
planet:

1. Fresh water in and out of the sea surface (m/yr, + into the sea):
   - rain on the sea minus evaporation from it, both from the rain model
     (climate._rain; no evaporation through sea ice), so the moisture the
     wind carries from one ocean to another (the Atlantic's over Central
     America to the Pacific) is in it;
   - river water: the land's runoff routed downhill to the river mouths
     and spread over a plume offshore (the Arctic, the Bay of Bengal);
   - sea ice: freezing leaves the salt behind in the water (brine), and the
     share of the ice that drifts away (all of it where the winter wind
     blows off the coast) melts, as fresh water, further off;
   - meltwater from shrinking ice sheets (compute's `melt`: the glacial
     time zoom passes its ice loss in, the main run nothing), on land
     routed like the rivers.
   Its global mean is taken off: salt is conserved, the sea's mean salinity
   stays S0.
2. Salinity: each place relaxes toward S0 - salt_k x (net fresh water) (a
   dilution where fresh water comes in), more so under year-round sea ice
   (the fresh lid of the Arctic), carried along the currents.
3. Density from temperature and salinity (Roquet et al. 2015 simplified
   equation of state: warm water expands more per degree, so cold water's
   density depends mostly on its salt), in winter (the coldest month, with
   the brine of the winter's new ice), compared at moc_z deep (cold water
   is more compressible: the thermobaric effect).
4. Sinking: the deep ocean fills with the densest water there is, mixed on
   its way down (the densest moc_top of the polar sea, less moc_mix).
   Water within moc_drho of that, poleward of moc_lat, can sink; lighter
   water can't get through. So the fresh North Pacific doesn't sink, while
   the North Atlantic, fed salty water from the south, and the Antarctic
   margin do.
5. Strength: Stommel's flow law (his two-box model, 1961): sinking ~ moc x
   the density difference between the sinking water and the water that
   replaces it x the area; each sea's cell in each hemisphere at most moc_k
   Sv per kg/m3 of its densest water's density over the water replacing it
   (as in the zonally averaged model of Wright & Stocker 1991).
6. The inflow: the water replacing what sinks comes from the low latitudes
   along the cheapest sea routes, riding the currents that go its way (Gulf
   Stream, North Atlantic Drift) and, in the polar seas, the sea floor's
   slope (a boundary current round the basin), routed like rivers run
   backwards. It can't pass a strait whose cross-section is smaller than
   its own (moc_width x moc_layer_m: Bering, but not the wide Barents
   shelf), nor come up under sea ice that lasts most of the year (the ice
   its own warmth leaves): it dives under that lid where it meets it, and
   sinks there if the open sea's winter water it brings is dense enough
   (the Arctic branch). Nor can it cross a latitude that is sea all the way round (with no
   coast, a circumpolar channel can't hold up a north-south surface flow:
   beyond one, as round Antarctica, deep water wells up to replace it). It
   is a layer hundreds of metres deep: it gives its heat up to the air only
   slowly (moc_lambda W/m2 per C over moc_width km) and the rain barely
   dilutes it. Where it is strong it makes up most of the surface water,
   whose temperature and salinity relax toward it rather than toward the
   latitude's: the North Atlantic Drift's warmth reaching Norway.
These are solved to a steady state together on a coarser grid (moc_level)
in a few damped iterations: more overturning brings more salt (which keeps
it going: Stommel's salt-advection feedback) but also more heat (which makes
the water lighter). Several states can be stable; with no earlier state
(compute's moc_start) every sea that is nearly dense enough starts sinking,
as if spun up from a mixed ocean, and the salt each site draws decides
which keep going.
"""


from __future__ import annotations

import warnings

import numpy as np
from numba import njit

from . import climate as C
from . import kernels
from .geo import R_KM, is_land
from .grid import Grid

S0 = 34.7  # psu: the oceans' mean salinity
RHO0 = 1026.0  # kg/m3 at 10 C, 35 psu (sea-surface pressure)
SV = 1e6  # m3/s per sverdrup
ICE_FRESH = 0.72  # m of fresh water per m of sea ice (0.9 g/cm3, ~1/5 of the salt kept)


def density(t, s, z: float = 0.0):
    """Sea-water density (kg/m3) from temperature (C) and salinity (psu) at
    depth z (m): the simplified equation of state of Roquet et al. (2015).
    The thermal expansion grows with the temperature (x4 from 0 to 25 C),
    so near freezing salt decides; and it grows with depth (cold water is
    more compressible: the thermobaric effect), so compared deep down,
    cold water is relatively denser."""
    ta, sa = t - 10.0, s - 35.0
    return (RHO0 - 0.1655 * (1.0 + 0.5 * 0.05952 * ta + 1.497e-4 * z) * ta
            + 0.76554 * (1.0 - 0.5 * 5.4914e-4 * sa - 1.109e-5 * z) * sa - 2.4341e-3 * ta * sa)


def cell_area_km2(grid: Grid) -> np.ndarray:
    """Spherical area of each cell, km2 (cached)."""
    G = C._geom(grid)
    if "area_km2" not in G:
        k = max(len(c) for c in grid.cell_corners)
        idx = np.array([c + [c[-1]] * (k - len(c)) for c in grid.cell_corners])
        a = grid.centers[:, None, :]
        b = grid.corners[idx]
        c = grid.corners[np.roll(idx, -1, axis=1)]
        num = np.abs(np.einsum("nkj,nkj->nk", a, np.cross(b, c)))
        den = (1 + np.einsum("nkj,nkj->nk", a, b) + np.einsum("nkj,nkj->nk", b, c)
               + np.einsum("nkj,nkj->nk", c, a))
        G["area_km2"] = (2 * np.arctan2(num, den)).sum(1) * R_KM**2
    return G["area_km2"]


def _csr_dir(grid: Grid) -> np.ndarray:
    """Unit tangent direction from each cell to each neighbour, in the CSR
    order of grid.nbr_idx."""
    return grid.edge_dir


def _spread(grid: Grid, f: np.ndarray, sea: np.ndarray, km: float) -> np.ndarray:
    """Spread a sea-surface input over ~km of sea around where it enters,
    keeping its total."""
    g = np.where(sea, C.smooth(grid, f, km), 0.0)
    tot = g.sum()
    return g * (f.sum() / tot) if tot > 0 else g


# The overturning is solved on a coarse grid, where the parallel kernels'
# start-up costs more than the work: serial copies of climate's.
_SERIAL = {}


def _serial(name: str):
    if name not in _SERIAL:  # (made on first use: climate imports this module before defining them)
        _SERIAL[name] = njit(cache=True)(getattr(C, name).py_func)
    return _SERIAL[name]


def _smooth(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """climate.smooth's fine-grid blur, serial (for the coarse grid)."""
    iters = int(round(4 * (km / C._geom(grid)["h"]) ** 2))
    f = np.ascontiguousarray(f, np.float64)
    return _serial("_smooth")(f, grid.nbr_off, grid.nbr_idx, C._geom(grid)["sk"], iters) if iters > 0 else f


@njit(cache=True)
def _relax_from(x, a, b, in_src, in_w, in_off, deg, nbr_off, nbr_idx, iters, diffusion):
    """climate._relax_along (x = a + b * upstream x along a flow), serial
    and starting from x (an earlier answer: fewer iterations needed)."""
    n = a.shape[0]
    x = x.copy()
    y = np.empty(n)
    den = np.empty(n)
    for i in range(n):
        dw = 0.0
        for k in range(in_off[i], in_off[i + 1]):
            dw += in_w[k]
        den[i] = dw
    for _ in range(iters):
        for i in range(n):
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


def _carry(grid: Grid, out_w: np.ndarray, a: np.ndarray, b: np.ndarray, km: float, diffusion: float,
           x0: np.ndarray | None = None) -> np.ndarray:
    """climate.carry, serial, with the flow's edge weights out_w
    (climate._edge_weights) already worked out; from x0 if given (an
    earlier answer: then a third of the iterations)."""
    G = C._geom(grid)
    iters = int(km / G["h"]) + 10
    if x0 is not None:
        iters = iters // 3 + 5
    x0 = a if x0 is None else x0
    return _relax_from(np.asarray(x0, np.float64), a.astype(np.float64), b.astype(np.float64), G["in_src"],
                       out_w[G["in_e"]], G["in_off"], G["deg"], grid.nbr_off, grid.nbr_idx, iters, diffusion)


def river_input(grid: Grid, surf: np.ndarray, sea: np.ndarray, water_mm: np.ndarray, km: float) -> np.ndarray:
    """Fresh water reaching the sea (m/yr over each sea cell) from water_mm
    (mm/yr) on the land: routed downhill (priority flood: pits filled, so
    inland basins drain too) to the river mouths, then spread over a
    plume ~km offshore."""
    land_w = np.where(sea, 0.0, np.maximum(water_mm, 0.0)) / 1000.0
    if not land_w.any():
        return np.zeros(grid.n)
    _, down, order = kernels.priority_flood(np.where(sea, np.minimum(surf, 0.0), np.maximum(surf, 1e-3)),
                                            grid.nbr_off, grid.nbr_idx, 0.01)
    flow = kernels.accumulate(down, order, land_w)
    return _spread(grid, np.where(sea, flow, 0.0), sea, km)


def ice_growth(t_air: np.ndarray, half: np.ndarray) -> np.ndarray:
    """Sea ice a winter grows (m), from the freezing degree-days of the air
    over the sea (a sine of half-swing `half` around the annual mean t_air,
    below the sea's freezing point) by Lebedev's rule h = 1.33 FDD^0.58 cm
    (Arctic ~2 m)."""
    m = np.cos(2 * np.pi * (np.arange(12) + 0.5) / 12)[:, None]
    fdd = (np.maximum(C.FREEZE - (t_air + half * m), 0.0) * 30.44).sum(0)
    return 0.0133 * fdd**0.58


def open_share(sst: np.ndarray, frozen: np.ndarray, half: np.ndarray) -> np.ndarray:
    """Share of the year the sea is free of ice: months whose sea surface
    (annual sst +- the seasonal half-swing, plus `frozen`: how far below
    freezing the latitude's sea would be, <= 0) stays above freezing. Sea
    ice shuts off evaporation."""
    m = np.cos(2 * np.pi * (np.arange(12) + 0.5) / 12)[:, None]
    return ((sst + frozen + half * m) > C.FREEZE + 0.2).mean(0)


@njit(cache=True)
def _paths(sources, ok, nbr_off, nbr_idx, cost, through):
    """Cheapest routes from the sources over the cells in ok (Dijkstra):
    cost per CSR edge (from a cell to that neighbour); cells where through
    is False are reached but not passed through. Returns (cost to
    reach each cell, inf where unreached; the cell each is reached from,
    -1 at the sources; the source each route starts at)."""
    n = ok.shape[0]
    dist = np.full(n, np.inf)
    par = np.full(n, -1, np.int64)
    root = np.full(n, -1, np.int64)
    m = nbr_idx.shape[0] + n
    hk = np.empty(m)
    hv = np.empty(m, np.int64)
    size = 0
    for s in sources:
        dist[s] = 0.0
        root[s] = s
        size = kernels._heap_push(hk, hv, size, 0.0, s)
    while size > 0:
        d, i, size = kernels._heap_pop(hk, hv, size)
        if d > dist[i] or not through[i]:
            continue
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if not ok[j]:
                continue
            nd = d + cost[e]
            if nd < dist[j]:
                dist[j] = nd
                par[j] = i
                root[j] = root[i]
                size = kernels._heap_push(hk, hv, size, nd, j)
    return dist, par, root


@njit(cache=True)
def _narrowest(centers, nbr_off, nbr_idx, sea, section, need, max_steps):
    """Per sea cell: the smallest cross-section (sum of `section` over the
    cells crossed) of the sea along the great circles through it in three
    directions 60 deg apart, walked both ways until land; a walk stops
    once the sum reaches `need` (it is then no strait), or after max_steps
    cells each way (a cost bound)."""
    n = centers.shape[0]
    out = np.full(n, np.inf)
    for i in range(n):
        if not sea[i]:
            continue
        c0 = centers[i]
        e = np.array([-c0[1], c0[0], 0.0])
        if e[0] * e[0] + e[1] * e[1] < 1e-12:
            e = np.array([1.0, 0.0, 0.0])
        e /= np.sqrt((e * e).sum())
        nth = np.cross(c0, e)
        best = np.inf
        for a in range(3):
            ang = a * np.pi / 3.0
            u = np.cos(ang) * e + np.sin(ang) * nth
            nrm = np.cross(c0, u)
            tot = section[i]
            for sgn in (1.0, -1.0):
                k = i
                for _ in range(max_steps):
                    if tot >= need:
                        break
                    t = sgn * np.cross(nrm, centers[k])
                    jb, sb = -1, -np.inf
                    for q in range(nbr_off[k], nbr_off[k + 1]):
                        j = nbr_idx[q]
                        d = centers[j] - centers[k]
                        s = (d * t).sum() - abs((centers[j] * nrm).sum())
                        if s > sb:
                            sb, jb = s, j
                    if jb < 0 or not sea[jb]:
                        break
                    k = jb
                    tot += section[k]
            best = min(best, tot)
            if best < need:
                break
        out[i] = best
    return out


def _straits(grid: Grid, sea: np.ndarray, sea_frac: np.ndarray, depth: np.ndarray, tune: dict) -> np.ndarray:
    """Sea cells in a passage too small for the overturning's inflow: a
    layer moc_layer_m deep and moc_width wide can't pass where the sea's
    narrowest cross-section, counted down to the layer's depth, is smaller
    than its own (moc_width x moc_layer_m). So a narrow, shallow strait
    (Bering, ~85 km x 50 m; Hudson Strait) shuts it out, while a wide shelf
    sea of the same depth (the Barents, ~1000 km x 200-400 m), or a
    narrow but deep strait (Fram, Denmark Strait), lets it through. Each
    cell is a cell's width (h) of sea_frac sea down to min(depth, layer)."""
    h = C._geom(grid)["h"]
    sec = np.where(sea, h * sea_frac * np.clip(depth, 0.0, tune["moc_layer_m"]) / 1000.0, 0.0)  # km2
    need = tune["moc_width"] * tune["moc_layer_m"] / 1000.0
    return sea & (_narrowest(grid.centers, grid.nbr_off, grid.nbr_idx, sea, sec, need, 40) < need)


@njit(cache=True)
def _route(order, par, sink):
    """The transport through each cell of the routes that bring the
    sinking water's replacement (like a river run backwards: each cell's
    inflow passes through the cell it is reached from). order: the reached
    cells, farthest first."""
    T = sink.copy()
    for k in range(order.shape[0]):
        i = order[k]
        if par[i] >= 0:
            T[par[i]] += T[i]
    return T


@njit(cache=True)
def _along(order, par, Q, tgt, x0, rate, dil):
    """A property of the inflowing water along its routes, from its
    sources (x0 there) on: each cell, it relaxes toward tgt by
    exp(-rate / Q) (rate per cell, m3/s; Q: the transport through it) and is diluted
    by dil / Q (dil: fresh water added over the route's width there, m3/s)."""
    x = x0.copy()
    for k in range(order.shape[0] - 1, -1, -1):
        i = order[k]
        p = par[i]
        if p < 0:
            continue
        q = max(Q[i], 1e-9)
        x[i] = tgt[i] + (x[p] - tgt[i]) * np.exp(-rate[i] / q) - x[p] * min(dil[i] / q, 0.5)
    return x


def _slope_current(grid: Grid, sea: np.ndarray, depth: np.ndarray, tune: dict) -> np.ndarray:
    """How the overturning's inflow, a layer moc_layer_m deep, is steered along the sea floor's
    slope in a polar sea (PW-582). There it is a buoyant boundary current going round the basin
    (Spall 2004): it follows the depth contours (f/H) with the shallow side on its right in the
    north, on its left in the south, as the Norwegian Atlantic Current follows Norway's slope on
    towards the Barents and Spitsbergen. Taken as a current of cur_ref where the floor drops by
    about the layer's depth across a cell (1 - 1/e of it), fully where by much more; poleward of
    moc_lat, fully 10 deg on (as the sinking). (In the subtropical gyres the western boundary
    currents run the other way round, with the coast on their left: not this.)"""
    dd = C.gradient(grid, np.where(sea, np.maximum(depth, 0.0), 0.0))  # m per km, toward deeper water
    mag = np.linalg.norm(dd, axis=1)
    w = 1.0 - np.exp(-mag * C._geom(grid)["h"] / tune["moc_layer_m"])
    w *= np.clip((np.abs(grid.lat) - tune["moc_lat"]) / 10.0, 0, 1)
    t = -np.cross(grid.centers, dd) / np.maximum(mag, 1e-9)[:, None]
    return np.where(sea[:, None], tune["cur_ref"] * (w * np.sign(grid.lat))[:, None] * t, 0.0)


def overturning(grid: Grid, sea: np.ndarray, rho_w: np.ndarray, rho_a: np.ndarray, sst: np.ndarray,
                sss: np.ndarray, t_eq: np.ndarray, fresh: np.ndarray, cur: np.ndarray, tune: dict,
                lid: np.ndarray | None = None, depth: np.ndarray | None = None,
                ice_lid: np.ndarray | None = None) -> dict:
    """Sinking, its strength and the surface inflow feeding it (steps 4-6).
    rho_w, rho_a: winter and annual surface density; sst, sss: the surface
    now; t_eq: the latitude's sea temperature (what the inflow gives its
    heat up toward); fresh: net fresh water (m/yr); cur: the (wind-driven)
    currents, which the inflow follows; lid: cells the inflow can't reach
    (straits too small for it); ice_lid: the fresh lid under year-round sea
    ice, which the inflow dives under where it meets it and can sink below
    (the Arctic branch) but doesn't come up through.
    Returns sinking (Sv per cell), inflow (Sv per cell width, spread), share
    (0..1: how much of the surface water is the inflow), t_in, s_in (its
    temperature and salinity), rho_deep (the deep water's density, per cell
    of each sea and hemisphere, at moc_z), sites (list of dicts per connected sinking area: lat, lon, sv, drho
    (kg/m3, sinking water minus the water feeding it), area_km2, heat_pw)."""
    n = grid.n
    area = cell_area_km2(grid)
    h = C._geom(grid)["h"]
    lat = np.abs(grid.lat)
    sinking = np.zeros(n)
    sites = []
    out = dict(sinking=sinking, inflow=np.zeros(n), share=np.zeros(n), t_in=sst, s_in=sss,
               rho_deep=np.zeros(n), sites=sites)
    low = np.flatnonzero(sea & (lat < tune["moc_src_lat"]))
    if tune["moc"] <= 0 or not len(low):
        return out
    # (on the coarse grid a cell is ~200 km: about a deep convection area)
    rs = np.where(sea, rho_w, -np.inf)
    ra = np.where(sea, rho_a, 0.0)
    polar = np.clip((lat - tune["moc_lat"]) / 10.0, 0, 1) * sea
    # The water replacing what sinks comes from the low latitudes, along the
    # shortest sea routes: d_low is the distance (cells) from them, root
    # the cell each route starts at. But no surface flow crosses a latitude
    # that is sea all the way round (a circumpolar channel: with no coast,
    # nothing holds up the east-west pressure difference a north-south
    # flow needs; Drake Passage). Beyond one, the sinking water is replaced
    # from below: deep water wells up (as round Antarctica).
    chan = sea & _circumpolar(grid, sea, tune)
    # The inflow rides the currents where they go its way (the Gulf Stream
    # and North Atlantic Drift rather than straight across the gyres, or up
    # against the Labrador Current): a step costs exp(-moc_follow x the
    # current's speed its way / cur_ref) (at most e^2 less or more).
    cdir = _csr_dir(grid)
    src = grid.nbr_src
    # It is a layer hundreds of m deep, so it also follows the sea floor's slope (_slope_current).
    if depth is not None:
        cur = cur + _slope_current(grid, sea, depth, tune)
    along = (cur[src] * cdir).sum(1) / tune["cur_ref"]
    cost = np.exp(-np.clip(tune["moc_follow"] * along, -2.0, 2.0))
    ok = sea & ~chan & (True if lid is None else ~lid)
    # The Arctic branch (PW-582): where the inflow meets the year-round ice
    # it dives under the fresh lid (the Atlantic layer) rather than
    # stopping. Its water there is the winter water of the open sea it came
    # through, cooled and salted by that sea's winter (the Barents' water
    # going on into the Arctic, St Anna Trough): where that is dense enough
    # it sinks at the lid's edge as the open sea's does, so the inflow
    # carries on past the open sea's own sinking toward it. Under the lid
    # nothing more is exchanged, so the routes end at its edge.
    under = np.zeros(n, np.bool_) if ice_lid is None else ice_lid & ok
    d_low, par, root = _paths(low[ok[low]], ok, grid.nbr_off, grid.nbr_idx, cost, ok & ~under)
    reach = np.isfinite(d_low)
    edge = under & reach & (par >= 0)
    rs = np.where(edge, rs[np.maximum(par, 0)], np.where(under, -np.inf, rs))
    # (beyond a channel: the channel's water is what wells up and is drawn in)
    rho_up = (area * ra)[chan].sum() / area[chan].sum() if chan.any() else 0.0
    # (an isolated polar sea with no low latitudes and no channel: no overturning)
    # Each sea that isn't connected to the others has its own deep water; a
    # small one (an inland sea) has none to speak of. Water can sink where
    # it is within moc_drho of that deep water's density (fully at it).
    # Each hemisphere's polar sea makes its own: the deep water a polar sea
    # forms fills its own side of the ocean first (as North Atlantic and
    # Antarctic bottom water both form on Earth), so one hemisphere's denser
    # water doesn't shut the other's sinking off (with one reference per
    # ocean the hemispheres competed, winner takes all: PW-458).
    lab, k = kernels.components(sea, grid.nbr_off, grid.nbr_idx)
    big = np.bincount(lab[sea], area[sea], k) >= tune["moc_sea_km2"]
    deep = np.zeros(n)
    top_rho = np.zeros(n)
    drho = tune["moc_drho"]
    hemis = (grid.lat > 0, grid.lat <= 0)
    for c, hm in ((c, hm) for c in np.flatnonzero(big) for hm in hemis):
        m = ((lab == c) & hm & (polar > 0) & (reach | (chan.any() & ~chan & (lat > _chan_lat(grid, chan))))
             & (~under | edge))
        mo = m & ~under
        if not mo.any():
            continue
        # the deep water: a mix of the densest water there is (its densest
        # moc_top share of the polar sea, by area, at the surface: not the
        # lid's edge, whose water is its open neighbour's), made lighter by
        # mixing on its way down (moc_mix)
        o = np.argsort(rs[mo])[::-1]
        cum = np.cumsum(area[mo][o])
        top = o[: np.searchsorted(cum, tune["moc_top"] * cum[-1]) + 1]
        rho_top = (rs[mo][top] * area[mo][top]).sum() / area[mo][top].sum()
        ref0 = rho_top - tune["moc_mix"]
        # Entrainment (PW-579): where the densest water is a small pocket far
        # denser than the polar sea around it (brine-salted shelf water by a
        # polynya), it cascades down the slope and draws in the water it
        # passes, moc_entrain times its own volume (overflows and Antarctic
        # shelf water grow 2-3x on their way down: Denmark Strait ~3 -> 5-6 Sv,
        # Weddell shelf water ~1-2 -> 4-5 Sv). The deep water it forms is the
        # mix, rho_d = (rho_top + E rho_a) / (1 + E) with the open polar sea's
        # mean rho_a: lighter than the pocket less its ordinary mixing, so the
        # rest of the open sea within moc_drho of it sinks too, and the
        # pocket's own sinking carries its entrained water with it. Where the
        # densest water is only a little denser than the rest (by less than
        # moc_mix x (1 + E) / E), its ordinary mixing already brings it to the
        # deep water's density and nothing changes.
        e_ = tune["moc_entrain"]
        pw = area[mo] * polar[mo]
        rho_amb = (rs[mo] * pw).sum() / pw.sum()
        rho_d = (rho_top + e_ * rho_amb) / (1.0 + e_)
        ref = min(ref0, rho_d)
        gate = np.clip((rs[m] - ref + drho) / drho, 0, 1) ** tune["moc_pow"] * polar[m]
        # Stommel's flow law: sinking ~ the density difference that drives it
        dr = np.maximum(rs[m] - np.where(reach[m], ra[np.maximum(root[m], 0)], rho_up), 0.0)
        # (the pocket: water denser than the deep water would be with its ordinary mixing alone; q how much
        # the entrainment lowers the deep water beyond that, 0..1 per moc_mix)
        q = np.clip((ref0 - rho_d) / tune["moc_mix"], 0.0, 1.0)
        pocket = np.clip((rs[m] - ref0) / tune["moc_mix"], 0.0, 1.0)
        sinking[m] = tune["moc"] * gate * dr * area[m] / 1e6 * (1.0 + e_ * q * pocket)
        deep[(lab == c) & hm] = ref
        top_rho[(lab == c) & hm] = rho_top
    out["rho_deep"] = deep
    if not sinking.any():
        return out
    # A big sinking area doesn't make a proportionally bigger overturning:
    # the deep return flow is limited by the ocean's size, not the sinking
    # area's (Stommel's two boxes; as zonally averaged, Wright & Stocker
    # 1991): each sea's overturning cell in each hemisphere carries at most
    # moc_k Sv per kg/m3 of its density difference: the polar box's dense
    # water (its densest moc_top share, before it mixes on the way down:
    # rho_top) against the water replacing it (the low box, by where it
    # sinks). Not the sinking water's own density weighted by the sinking: a
    # fresh pulse that shuts the densest site off moves the weight to the
    # other sites, and that mean could rise; the densest water can only get
    # lighter (PW-578).
    rep = np.where(reach, ra[np.maximum(root, 0)], rho_up)
    dr_all = np.maximum(rs - rep, 0.0)
    for c in np.flatnonzero(big):
        for h_ in (1.0, -1.0):
            cells = np.flatnonzero((lab == c) & (np.sign(grid.lat) == h_) & (sinking > 0))
            if not len(cells):
                continue
            psi = sinking[cells].sum()
            rho_rep = (sinking[cells] * rep[cells]).sum() / psi
            cap = tune["moc_k"] * max(top_rho[cells[0]] - rho_rep, 0.0)
            if psi > cap:
                sinking[cells] *= cap / psi
    # diagnostics per connected sinking area
    root = np.where(reach, root, np.arange(n))
    order = np.argsort(-np.where(reach, d_low, -1.0), kind="stable")
    order = order[reach[order]]
    slab, ns = kernels.components(sinking > 1e-3, grid.nbr_off, grid.nbr_idx)
    for s_ in range(ns):
        cells = np.flatnonzero(slab == s_)
        w = sinking[cells]
        psi = w.sum()
        if psi < 0.1:
            continue
        cx = (grid.centers[cells] * w[:, None]).sum(0)
        cx /= np.linalg.norm(cx)
        t_low = (w * sst[root[cells]]).sum() / psi
        sites.append(dict(lat=round(float(np.degrees(np.arcsin(cx[2]))), 1),
                          lon=round(float(np.degrees(np.arctan2(cx[1], cx[0]))), 1),
                          sv=round(float(psi), 2), drho=round(float((w * dr_all[cells]).sum() / psi), 3),
                          area_km2=round(float(area[cells].sum())),
                          heat_pw=round(float(psi * SV * 4.1e6 * (t_low - (w * sst[cells]).sum() / psi) / 1e15), 3)))
    # All sites' routes at once. The inflow is a layer hundreds of m deep: it
    # gives its heat up to the air (moc_lambda W/m2 per C over moc_width km)
    # only slowly, and the rain and rivers on its way barely dilute it.
    # Its temperature's relaxation is taken as an exchange of water with the
    # sea it passes, and that exchange carries salt as well as heat: the
    # inflow's salinity relaxes toward the surface water's at the same rate
    # (PW-582; ~0.4 Sv per 220 km cell, as a lateral eddy diffusivity of
    # ~1000 m2/s over moc_layer_m and moc_width, within the ~500-2000 m2/s
    # observed for boundary currents). Without it the Nordic inflow kept the
    # subtropics' 35.6-36.1 psu against the ~35.2 observed.
    Tr = _route(order, par, sinking)
    Q = Tr * SV
    hw = h * 1000.0 * tune["moc_width"] * 1000.0  # m2: the route's area per cell
    mix = np.where(under, 0.0, tune["moc_lambda"] * hw / 4.1e6)  # m3/s per cell (none under the ice lid)
    t_in = _along(order, par, Q, t_eq, sst, mix, np.zeros(n))
    s_in = _along(order, par, Q, sss, sss, mix, np.where(under, 0.0, np.maximum(fresh, 0.0)) / 3.156e7 * hw)
    # spread over the route's width; where it carries more than ~moc_q0 Sv
    # per km of width, the surface water is mostly the inflow
    norm = np.maximum(_smooth(grid, sea.astype(float), tune["moc_km"]), 1e-6)
    wt = np.maximum(_smooth(grid, Tr, tune["moc_km"]), 1e-12)
    Ts = np.where(sea, wt / norm, 0.0)
    out["t_in"] = np.where(Ts > 1e-6, _smooth(grid, Tr * t_in, tune["moc_km"]) / wt, sst)
    out["s_in"] = np.where(Ts > 1e-6, _smooth(grid, Tr * s_in, tune["moc_km"]) / wt, sss)
    out["inflow"] = Ts
    # (in the subtropical gyres the gyre itself is the warm current; the
    # inflow's own warmth shows once it has left them, ~10 deg on)
    out["share"] = np.where(under, 0.0, (1.0 - np.exp(-Ts / h / tune["moc_q0"]))
                            * np.clip((lat - tune["moc_src_lat"]) / 10.0, 0, 1))
    return out


def salinity(grid: Grid, sea: np.ndarray, fresh: np.ndarray, cur: np.ndarray, tune: dict,
             iced: np.ndarray | None = None, share: np.ndarray | None = None,
             s_in: np.ndarray | None = None, out_w: np.ndarray | None = None,
             s0: np.ndarray | None = None) -> np.ndarray:
    """Sea-surface salinity (psu, step 2): relaxed toward S0 - salt_k x
    fresh (net fresh water, m/yr, global mean already off; where fresh water
    comes in, as a dilution: S0 / (1 + salt_k fresh / S0)), carried along
    the currents cur over ~salt_km at the reference speed. The mean over
    the sea's area is S0 (salt is conserved). out_w: cur's edge weights, if
    known; s0: an earlier answer to start from."""
    G = C._geom(grid)
    reach = tune["salt_km"] * np.clip(C.speed(cur) / tune["cur_ref"], tune["cur_min"], tune["cur_max"])
    keep = np.where(sea, np.exp(-G["h"] / reach), 0.0)
    # fresh water dilutes: a river plume tends to fresh water, never below it
    # Under year-round sea ice the wind can't stir the surface, and no new
    # ice forms to stir it with brine: the fresh water stays in a thin layer
    # on top (the Arctic's halocline). iced: 0..1, how perennial the ice is.
    k = tune["salt_k"] * (1.0 + tune["salt_ice"] * (0.0 if iced is None else iced))
    x = k * fresh / S0
    s_eq = S0 * np.where(x > 0, 1.0 / (1.0 + np.maximum(x, 0.0)), 1.0 - x)
    if share is not None:  # where the overturning's inflow makes up the surface water
        s_eq = (1 - share) * s_eq + share * s_in
    if out_w is None:
        out_w, _ = C._edge_weights(grid, cur, (sea[G["src"]] & sea[G["dst"]]).astype(np.float64))
    # (carried as the difference from S0, which starts the iterations nearer the answer)
    s = S0 + _carry(grid, out_w, np.where(sea, (1 - keep) * (s_eq - S0), 0.0), keep,
                    1.5 * tune["cur_max"] * tune["salt_km"], tune["salt_diff"], None if s0 is None else s0 - S0)
    area = cell_area_km2(grid)
    s = np.where(sea, s, S0)
    return s + (S0 - (s * area)[sea].sum() / area[sea].sum())


FW_RESIDUE = 0.02  # m/yr: see freshwater (the rain model's transport itself leaks ~0.5-1.6 cm/yr at L5-6)


def freshwater(grid: Grid, sea: np.ndarray, surf: np.ndarray, precip: np.ndarray, evap: np.ndarray,
               runoff: np.ndarray, ice_m: np.ndarray, melt: np.ndarray | None, tune: dict,
               export: np.ndarray | float | None = None) -> dict:
    """Net fresh water into the sea surface (m/yr, step 1). precip, evap,
    runoff in mm/yr (runoff on land), ice_m: sea ice grown per winter (m),
    export: the share of it that drifts away (default ice_export), melt: ice-sheet meltwater (m/yr of water; on land routed like the
    rivers, at sea entering where it is). Returns the parts and the total
    with its (global, area-weighted) mean over the sea taken off. The rain
    model's air takes up what the sea and the land's water balance
    evaporate (PW-266), so without meltwater that mean is only the books'
    small residue (the temperatures move a little after the rain): a warning
    above FW_RESIDUE m/yr."""
    area = cell_area_km2(grid)
    ep = np.where(sea, (precip - evap) / 1000.0, 0.0)
    melt = np.zeros(grid.n) if melt is None else np.maximum(np.asarray(melt, float), 0.0)
    river = river_input(grid, surf, sea, np.where(sea, 0.0, runoff), tune["river_km"])
    melt_in = river_input(grid, surf, sea, 1000.0 * melt, tune["river_km"]) if melt.any() else np.zeros(grid.n)
    melt_in = melt_in + _spread(grid, np.where(sea, melt, 0.0), sea, tune["river_km"])
    export = tune["ice_export"] if export is None else export
    out = ICE_FRESH * export * np.where(sea, ice_m, 0.0)
    ice = -out + _spread(grid, out * area, sea, tune["ice_km"]) / area
    tot = ep + river + melt_in + ice
    a_sea = max(area[sea].sum(), 1e-9)
    mean = (tot * area)[sea].sum() / a_sea
    residue = mean - (melt_in * area)[sea].sum() / a_sea
    if abs(residue) > FW_RESIDUE:
        warnings.warn(f"fresh water into the sea doesn't balance: {residue:+.4f} m/yr", RuntimeWarning, stacklevel=2)
    return dict(ep=ep, river=river, melt=melt_in, ice=ice, mean=mean, total=np.where(sea, tot - mean, 0.0))


def _circumpolar(grid: Grid, sea: np.ndarray, tune: dict) -> np.ndarray:
    """Cells in latitude bands (2 deg) that are sea all the way round
    (islands smaller than island_km2 don't block them, as for the currents)."""
    land = ~sea
    lab, k = C._components(grid, land)
    area = cell_area_km2(grid)
    sizes = np.bincount(lab[land], area[land], max(k, 1))
    wall = land & (sizes[np.maximum(lab, 0)] >= tune["island_km2"])
    nb = 90
    bins = np.clip(((grid.lat + 90) // 2.0).astype(int), 0, nb - 1)
    open_band = np.bincount(bins, wall, nb) == 0
    return open_band[bins]


def _chan_lat(grid: Grid, chan: np.ndarray) -> np.ndarray:
    """Per cell: |lat| of the nearest circumpolar channel in its hemisphere
    (90 where there is none): poleward of it, sinking water is replaced from below."""
    out = np.full(grid.n, 90.0)
    for hemi in (1, -1):
        sel = chan & (np.sign(grid.lat) == hemi)
        if sel.any():
            out[np.sign(grid.lat) == hemi] = np.abs(grid.lat[sel]).max()
    return out


_COARSE = {}


def _coarse(grid: Grid, sea: np.ndarray, level: int) -> dict:
    """The coarser grid the overturning is solved on, and the maps between
    it and grid: fine -> coarse is the mean over the sea cells in each
    coarse cell, coarse -> fine interpolates from the nearby coarse sea
    cells (climate._coarse's weights). Cached per grid and sea mask."""
    from .grid import shared_grid
    level = min(level, grid.level)
    key = (id(grid), grid.n, level, hash(sea.tobytes()))
    if key not in _COARSE:
        if len(_COARSE) > 8:
            _COARSE.clear()
        cg = shared_grid(level)  # (one per process: its climate._geom is computed once)
        K = C._coarse(grid, level)
        cnt = np.bincount(K["cidx"], sea.astype(float), cg.n)
        tot = np.bincount(K["cidx"], minlength=cg.n)
        sea_c = cnt >= 0.5 * tot
        w = K["w"] * sea_c[K["cand"]]
        sw = w.sum(1)
        _COARSE[key] = dict(cg=cg, cidx=K["cidx"], cnt=cnt, sea=sea_c, cand=K["cand"],
                            w=w / np.maximum(sw, 1e-12)[:, None], has=sw > 0)
    return _COARSE[key]


def _down(M: dict, sea: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Fine -> coarse: mean over each coarse cell's sea cells (scalars or vectors)."""
    f = np.asarray(f, float)
    if f.ndim == 2:
        v = np.stack([_down(M, sea, f[:, j]) for j in range(f.shape[1])], 1)
        p = M["cg"].centers
        return v - (v * p).sum(1, keepdims=True) * p
    return np.bincount(M["cidx"], np.where(sea, f, 0.0), M["cg"].n) / np.maximum(M["cnt"], 1e-9)


def _up(M: dict, fc: np.ndarray) -> np.ndarray:
    """Coarse -> fine: interpolated from the coarse sea cells nearby."""
    out = (M["w"] * fc[M["cand"]]).sum(1)
    return np.where(M["has"], out, fc[M["cidx"]])


def solve(grid: Grid, sea: np.ndarray, sst_of, sst0: np.ndarray, t_eq: np.ndarray, cur: np.ndarray,
          fresh: np.ndarray, ice_m: np.ndarray, sea_half: np.ndarray, tune: dict,
          start: dict | None = None, frozen: np.ndarray | None = None,
          depth: np.ndarray | None = None) -> dict:
    """Salinity, density and the overturning together, to a steady state
    (moc_iters damped iterations), on a coarser grid (moc_level: the
    overturning is thousands of km across; ~10x cheaper). There the
    inflow's warmth is added to the sea temperature sst0 (without it) the
    way climate.sea_surface would: by the same currents, part of the
    latitude's mean change over both hemispheres taken off (moc_zonal; 1: the heat is conserved, PW-265, PW-589).
    sst_of(share, t_in): the full sea-surface temperature (on grid) where a
    share of the surface water is the overturning's inflow at t_in, used
    once at the end. t_eq: the latitude's sea temperature; cur: the
    currents; fresh: net fresh water (m/yr, freshwater()'s total); ice_m:
    sea ice grown per winter (m); sea_half: the sea's seasonal half-swing
    (C); frozen: how far below freezing the latitude's sea would be (C, <= 0;
    see open_share), from which the sea ice is found on the overturning's
    own sea temperatures each iteration; depth: sea depth (m).
    start: an earlier call's moc_state to begin from (picks the state when
    several are stable; same grid). Returns sss, density
    (annual), density_w (winter), sinking (Sv per cell), inflow, state,
    sites, sst; all on grid."""
    M = _coarse(grid, sea, int(tune["moc_level"]))
    cg, sea_c = M["cg"], M["sea"]
    G = C._geom(cg)

    def dn(f):
        return _down(M, sea, f)

    fresh_c, ice_c, half_c, teq_c, sst0_c = dn(fresh), dn(ice_m), dn(sea_half), dn(t_eq), dn(sst0)
    frozen_c = None if frozen is None else dn(frozen)
    iced_c = None
    cur_c = np.where(sea_c[:, None], dn(cur), 0.0)
    # The inflow is a layer hundreds of m deep: it can't pass a strait
    # too small for it (_straits: Bering, not the Barents), and where the sea is iced over most
    # of the year it dives under the fresh surface layer (the Arctic
    # halocline). That ice is the one the overturning's own warmth leaves,
    # found again each iteration (from the first guess's sea, without the
    # inflow, a sea the inflow would keep open stayed shut to it: PW-582).
    frac_c = M["cnt"] / np.maximum(np.bincount(M["cidx"], minlength=cg.n), 1)
    lid_d = np.zeros(cg.n, bool) if depth is None else _straits(cg, sea_c, frac_c, dn(depth), tune)
    ice_lid = None
    depth_c = None if depth is None else dn(depth)
    brine = S0 * ICE_FRESH * np.where(sea_c, ice_c, 0.0) / tune["brine_m"]
    # how the sea surface takes up a change of the temperature it relaxes to (as climate.sea_surface)
    reach = tune.get("relax_km", 2500.0) * np.clip(C.speed(cur_c) / tune["cur_ref"], tune["cur_min"], tune["cur_max"])
    keep = np.where(sea_c, np.exp(-G["h"] / reach), 0.0)
    out_w, _ = C._edge_weights(cg, cur_c, (sea_c[G["src"]] & sea_c[G["dst"]]).astype(np.float64))

    warm = {}  # the last answers, to start the next iteration's from

    def sst_c(st):
        D = np.where(sea_c, st["share"] * (st["t_in"] - teq_c), 0.0)
        E = _carry(cg, out_w, (1 - keep) * D, keep, 1.5 * tune["cur_max"] * 2500.0, 0.15, warm.get("E"))
        warm["E"] = E
        zm = tune["moc_zonal"] * C.zonal_mean(cg, E, sea_c, fold=True)
        return np.where(sea_c, np.maximum(sst0_c + E - zm, C.FREEZE), sst0_c)

    def state(st, sst):
        # (which water sinks deepest is decided deep down: compared at moc_z)
        sss = salinity(cg, sea_c, fresh_c, cur_c, tune, iced_c, st["share"], st["s_in"], out_w, warm.get("S"))
        warm["S"] = sss
        rho_w = density(np.maximum(sst - winter_half(half_c, st["share"], tune), C.FREEZE), sss + brine,
                        tune["moc_z"])
        return sss, rho_w, density(sst, sss, tune["moc_z"])

    nc = cg.n
    if start is None:
        st = dict(share=np.zeros(nc), t_in=sst0_c.copy(), s_in=np.full(nc, S0))
    else:
        st = {k: np.asarray(start[k], float) for k in ("share", "t_in", "s_in")}
        if len(st["share"]) != nc:
            raise ValueError("moc_start is from a different grid")
    sst = sst_c(st)
    ov = None
    n_it = max(int(tune["moc_iters"]), 1)
    it = 0
    while True:
        if frozen_c is not None:
            # (0..1: how much of the year the sea is iced over; a lid where most of it)
            iced_c = np.where(sea_c, np.clip(1.0 - 2.0 * open_share(sst, frozen_c, half_c), 0.0, 1.0), 0.0)
            ice_lid = iced_c > 0.5
        sss, rho_w, rho_a = state(st, sst)
        # With no earlier state, the first passes let every sea that is
        # nearly dense enough sink, as if spun up from a well-mixed ocean,
        # then tighten that to moc_drho over the iterations (all but the last
        # two): the salt the overturning brings decides which sites keep
        # sinking.
        spin = it == 0 and start is None
        n_sp = max(n_it - 2, 1)
        f = tune["moc_spin"] ** max(1.0 - it / n_sp, 0.0) if start is None else 1.0
        ov = overturning(cg, sea_c, rho_w, rho_a, sst, sss, teq_c, fresh_c, cur_c,
                         {**tune, "moc_drho": tune["moc_drho"] * f}, lid_d, depth_c, ice_lid)
        a = 1.0 if spin else tune["moc_relax"]
        step = a * (ov["share"] - st["share"])
        st = {k: st[k] + a * (ov[k] - st[k]) for k in st}
        sst = sst_c(st)
        it += 1
        # after the spin-up's moc_iters, on to a steady state (PW-360): until the inflow's share of the
        # surface water moves by less than moc_tol anywhere (4 iterations left Earth's north at 10.0 Sv
        # on its way to 11.3)
        if it >= n_it and (np.abs(step).max() < tune["moc_tol"] or it >= tune["moc_max_iters"]):
            break
    sss, rho_w, rho_a = state(st, sst)
    # back on the fine grid
    sst_f = sst_of(np.clip(_up(M, st["share"]), 0, 1), _up(M, st["t_in"]))
    sss_f = np.where(sea, _up(M, sss), S0)
    area = cell_area_km2(grid)
    sss_f = np.where(sea, sss_f + S0 - (sss_f * area)[sea].sum() / max(area[sea].sum(), 1e-9), S0)
    brine_f = S0 * ICE_FRESH * np.where(sea, ice_m, 0.0) / tune["brine_m"]
    sink_f = _up(M, ov["sinking"]) * sea
    sink_f *= ov["sinking"].sum() / max(sink_f.sum(), 1e-12)  # (same total)
    share_f = np.where(sea, np.clip(_up(M, st["share"]), 0, 1), 0.0)
    return dict(sss=sss_f, density=density(sst_f, sss_f),
                density_w=density(np.maximum(sst_f - winter_half(sea_half, share_f, tune), C.FREEZE),
                                  sss_f + brine_f),
                sinking=sink_f, inflow=_up(M, ov["inflow"]) * sea, share=share_f, state=st,
                sites=ov["sites"], sst=sst_f)


def winter_half(sea_half: np.ndarray, share: np.ndarray, tune: dict) -> np.ndarray:
    """The sea's winter half-swing (C) where a share of the surface water is
    the overturning's inflow. The inflow is a layer moc_layer_m deep (the
    Atlantic Water under the Nordic Seas, ~500-800 m), and winter convection
    mixes down into it: the winter's heat loss is spread over that layer
    instead of the ordinary winter mixed layer (brine_m), so the surface
    cools by brine_m / moc_layer_m as much. The summer's warming sits in a
    shallow layer on top and is left as it is."""
    return sea_half * (1.0 - share * (1.0 - tune["brine_m"] / tune["moc_layer_m"]))


# ---------------------------------------------------------------------------
# A schematic of the overturning loop, for the viewer
# ---------------------------------------------------------------------------
LOOP_MIN_SV = 0.3  # sites weaker than this get no drawn loop
LOOP_DEEP_M = 1500.0  # the deep return flow keeps to sea deeper than this
LOOP_CHAN_LAT = 70.0  # deg: a circumpolar channel equatorward of this is where deep water wells up
LOOP_GAP_DEG = 20.0  # deg: no deep limb from a site this far from the deep sea that leads to the upwelling
LOOP_WEST_KM = 500.0  # ... preferring a western boundary: a step costs 1 + min(km to land due west, LOOP_WEST_CAP_KM) / this
LOOP_WEST_CAP_KM = 3000.0  # (at most 7x a western-boundary step: enough to hug the slope, not to send
# the limb round the far side of the planet for a western boundary)
# The deep limb keeps to the deep sea where it can, but a basin walled in by
# ridges or shelves still spills its dense water over the sill (the Nordic
# seas over the Greenland-Scotland ridge, ~600-850 m): a step over sea
# shallower than LOOP_DEEP_M costs LOOP_SILL_COST x, and over sea shallower
# than LOOP_SILL_M LOOP_SHELF_COST x, a deep step's
LOOP_SILL_M = 400.0
LOOP_SILL_COST = 3.0
LOOP_SHELF_COST = 10.0


def _west_distance(grid: Grid, land: np.ndarray, max_km: float, min_km2: float) -> np.ndarray:
    """km due west from each cell to land (a landmass of at least min_km2,
    not an island in mid-ocean), at most max_km: the deep western boundary
    currents hug the continental slope on a basin's west side."""
    lab, k = C._components(grid, land)
    area = cell_area_km2(grid)
    sizes = np.bincount(lab[land], area[land], max(k, 1))
    land = land & (sizes[np.maximum(lab, 0)] >= min_km2)
    out = np.full(grid.n, max_km)
    p = grid.centers
    cl = np.maximum(np.cos(np.radians(grid.lat)), 0.15)
    guess = np.arange(grid.n)
    step = 0.5 * grid.spacing * R_KM
    for d in np.arange(step, max_km, step):
        a = -d / R_KM / cl  # rotate west about the spin axis
        q = np.stack([p[:, 0] * np.cos(a) - p[:, 1] * np.sin(a), p[:, 0] * np.sin(a) + p[:, 1] * np.cos(a),
                      p[:, 2]], 1)
        guess = grid.locate(q, guess)
        out = np.where(land[guess] & (out >= max_km), d, out)
    return out


def _trace(grid: Grid, par: np.ndarray, start: int, max_points: int = 70) -> list[list[float]]:
    """The route from start along par (to its source), as [[lat, lon], ...],
    smoothed (a schematic, not cell steps) and thinned."""
    cells = [start]
    while par[cells[-1]] >= 0 and len(cells) < 20000:
        cells.append(int(par[cells[-1]]))
    v = grid.centers[cells].astype(float)
    for _ in range(4):
        if len(v) > 2:
            v[1:-1] = 0.25 * v[:-2] + 0.5 * v[1:-1] + 0.25 * v[2:]
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    step = max(1, int(np.ceil(len(v) / max_points)))
    keep = list(range(0, len(v), step)) + ([len(v) - 1] if (len(v) - 1) % step else [])
    lat = np.degrees(np.arcsin(np.clip(v[keep, 2], -1, 1)))
    lon = np.degrees(np.arctan2(v[keep, 1], v[keep, 0]))
    return [[round(float(a), 2), round(float(b), 2)] for a, b in zip(lat, lon)]


def _arc(lat1: float, lon1: float, lat2: float, lon2: float, step_deg: float = 1.0) -> list[list[float]]:
    """Points along the great circle from (lat1, lon1) to (lat2, lon2), both ends included."""
    from .geo import latlon, xyz
    a, b = xyz(np.radians(lat1), np.radians(lon1)), xyz(np.radians(lat2), np.radians(lon2))
    ang = float(np.arccos(np.clip(a @ b, -1, 1)))
    m = max(1, int(np.ceil(np.degrees(ang) / step_deg)))
    t = np.linspace(0, 1, m + 1)[:, None]
    v = a * np.sin((1 - t) * ang) + b * np.sin(t * ang) if ang > 1e-9 else np.repeat(a[None], m + 1, 0)
    la, lo = latlon(v / np.linalg.norm(v, axis=1, keepdims=True))
    return [[round(float(x), 2), round(float(y), 2)] for x, y in zip(la, lo)]


def _arc_deg(grid: Grid, i: int, lat: float, lon: float) -> float:
    from .geo import xyz
    return float(np.degrees(np.arccos(np.clip(grid.centers[i] @ xyz(np.radians(lat), np.radians(lon)), -1, 1))))


def _nearest(grid: Grid, cells: np.ndarray, lat: float, lon: float) -> int:
    from .geo import xyz
    p = np.asarray(xyz(np.radians(lat), np.radians(lon)), float)
    return int(cells[np.argmax(grid.centers[cells] @ p)])


def loop_schematic(grid: Grid, elev: np.ndarray, c: dict, tune: dict | None = None,
                   ice: np.ndarray | None = None) -> dict:
    """The overturning in numbers plus a schematic of its loop, for world
    meta (climate.compute's result c):
      sv, north_sv, south_sv   Sv sinking in all, and per hemisphere
      sites                    c's moc_sites (lat, lon, sv, drho, area_km2, heat_pw)
      paths                    [{site, limb, pts: [[lat, lon], ...]}] per site of at
                               least LOOP_MIN_SV:
        limb "surface": the warm inflow from the low latitudes (equatorward
          of moc_src_lat), along the route the model's inflow takes
          (moc_inflow; the cheapest sea route riding it). None for a site
          beyond a circumpolar channel: there the sinking water is replaced
          by deep water welling up in the channel (as round Antarctica).
        limb "deep": NOT modelled (the model has no deep ocean): the
          textbook path of the deep return flow, the cheapest route through
          sea deeper than LOOP_DEEP_M (over sills and shelves only at a
          cost: LOOP_SILL_COST, LOOP_SHELF_COST) preferring western boundaries, to
          where deep water comes back up: a circumpolar channel (equatorward
          of LOOP_CHAN_LAT) in the other hemisphere if there is one (the
          Southern Ocean), else the equatorial band.
        A limb is left out where the site is more than LOOP_GAP_DEG from
        the sea its route would start in.
      upwelling                where the deep limbs end: "channel" and / or "tropics"
      note                     says which parts are schematic"""
    from . import climate as Cm
    tune = tune or Cm.TUNE
    sea = ~is_land(elev, ice)  # (ice: grounded land ice, whose bed may be below the sea)
    sink = np.asarray(c["overturning"], float)
    out = {"sv": round(float(sink.sum()), 2), "north_sv": round(float(sink[grid.lat >= 0].sum()), 2),
           "south_sv": round(float(sink[grid.lat < 0].sum()), 2), "sites": list(c.get("moc_sites") or []),
           "paths": []}
    if not any(s["sv"] >= LOOP_MIN_SV for s in out["sites"]):
        return out
    n = grid.n
    chan = sea & _circumpolar(grid, sea, tune)
    chan_lat = _chan_lat(grid, chan & (np.abs(grid.lat) < LOOP_CHAN_LAT))
    # deep limb: through deep sea, along the western boundaries; over sills
    # and shelves only at a cost (LOOP_SILL_COST, LOOP_SHELF_COST)
    depth = -elev
    deep = sea & (depth > LOOP_DEEP_M)
    west = _west_distance(grid, ~sea, LOOP_WEST_CAP_KM, tune["island_km2"])
    step = np.select([depth > 3000.0, depth > LOOP_DEEP_M, depth > LOOP_SILL_M], [1.0, 1.5, LOOP_SILL_COST], LOOP_SHELF_COST)
    cost = ((1.0 + west / LOOP_WEST_KM) * step)[grid.nbr_idx]
    dest = {}
    for hemi in (1, -1):
        # (a channel between continents, as the Southern Ocean's: not a polar sea's ring round the pole)
        ch = chan & deep & (np.sign(grid.lat) == hemi) & (np.abs(grid.lat) < LOOP_CHAN_LAT)
        dest[hemi] = ch if ch.sum() >= 10 else None
    eq = deep & (np.abs(grid.lat) < 5)
    runs = {}

    def routes(key, targets):
        if key not in runs:
            runs[key] = _paths(np.flatnonzero(targets), sea, grid.nbr_off, grid.nbr_idx, cost, sea)
        return runs[key]

    # surface limb: from the low latitudes, riding the model's inflow
    infl = np.asarray(c.get("moc_inflow", np.zeros(n)), float)
    ref = np.percentile(infl[infl > 0], 95) if (infl > 0).any() else 1.0
    s_cost = (1.0 / (0.05 + np.clip(infl / max(ref, 1e-12), 0, 1)))[grid.nbr_idx]
    low = sea & (np.abs(grid.lat) < tune["moc_src_lat"])
    s_ok = sea & ~chan
    s_dist, s_par, _ = _paths(np.flatnonzero(low), s_ok, grid.nbr_off, grid.nbr_idx, s_cost, s_ok)
    up_kind = set()
    for k, s in enumerate(out["sites"]):
        if s["sv"] < LOOP_MIN_SV:
            continue
        hemi = 1 if s["lat"] >= 0 else -1
        # (poleward of a circumpolar channel in its own hemisphere)
        beyond = dest[hemi] is not None and abs(s["lat"]) > chan_lat[_nearest(grid, np.arange(n), s["lat"], s["lon"])]
        # surface limb
        reach = np.flatnonzero(np.isfinite(s_dist))
        if not beyond and len(reach):
            i = _nearest(grid, reach, s["lat"], s["lon"])
            if _arc_deg(grid, i, s["lat"], s["lon"]) <= LOOP_GAP_DEG:
                out["paths"].append({"site": k, "limb": "surface", "pts": _trace(grid, s_par, i)})
        # deep limb
        other = dest[-hemi]
        key = ("chan", -hemi) if other is not None and not beyond else ("eq", 0)
        tg = other if key[0] == "chan" else eq
        if not tg.any():
            continue
        dist, par, _ = routes(key, tg)
        reach = np.flatnonzero(np.isfinite(dist))
        if not len(reach):
            continue
        i = _nearest(grid, reach, s["lat"], s["lon"])
        if _arc_deg(grid, i, s["lat"], s["lon"]) > LOOP_GAP_DEG:
            continue  # (the site's own deep sea doesn't lead there)
        # (from the site itself, along a great circle: it may sit behind a sill, as the Nordic seas do)
        pts = _trace(grid, par, i)
        out["paths"].append({"site": k, "limb": "deep", "pts": _arc(s["lat"], s["lon"], *pts[0]) + pts[1:]})
        up_kind.add("channel" if key[0] == "chan" else "tropics")
    out["upwelling"] = sorted(up_kind)
    out["note"] = ("schematic: the surface limb follows the model's inflow; the deep limb is not modelled "
                   "(a textbook route along the deep western boundaries)")
    return out
