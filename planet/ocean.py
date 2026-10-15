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
   Sv per kg/m3 (as in the zonally averaged model of Wright & Stocker 1991).
6. The inflow: the water replacing what sinks comes from the low latitudes
   along the cheapest sea routes, riding the currents that go its way (Gulf
   Stream, North Atlantic Drift), routed like rivers run backwards. It
   can't pass straits shallower than moc_sill, nor come up under year-round
   sea ice, nor cross a latitude that is sea all the way round (with no
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

import numpy as np
from numba import njit

from . import climate as C
from . import kernels
from .geo import R_KM
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
    order of grid.nbr_idx (cached)."""
    G = C._geom(grid)
    if "csr_dir" not in G:
        p = grid.centers
        src = np.repeat(np.arange(grid.n), np.diff(grid.nbr_off))
        d = p[grid.nbr_idx] - p[src]
        d -= (d * p[src]).sum(1, keepdims=True) * p[src]
        G["csr_dir"] = d / np.linalg.norm(d, axis=1, keepdims=True)
    return G["csr_dir"]


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
    return _serial("_smooth")(f, grid.nbr_off, grid.nbr_idx, iters, 0.5) if iters > 0 else f


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
def _paths(sources, ok, nbr_off, nbr_idx, cost):
    """Cheapest routes from the sources over the cells in ok (Dijkstra):
    cost per CSR edge (from a cell to that neighbour). Returns (cost to
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
        if d > dist[i]:
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
    exp(-rate / Q) (Q: the transport through the cell, m3/s) and is diluted
    by dil / Q (dil: fresh water added over the route's width there, m3/s)."""
    x = x0.copy()
    for k in range(order.shape[0] - 1, -1, -1):
        i = order[k]
        p = par[i]
        if p < 0:
            continue
        q = max(Q[i], 1e-9)
        x[i] = tgt[i] + (x[p] - tgt[i]) * np.exp(-rate / q) - x[p] * min(dil[i] / q, 0.5)
    return x


def overturning(grid: Grid, sea: np.ndarray, rho_w: np.ndarray, rho_a: np.ndarray, sst: np.ndarray,
                sss: np.ndarray, t_eq: np.ndarray, fresh: np.ndarray, cur: np.ndarray, tune: dict,
                lid: np.ndarray | None = None) -> dict:
    """Sinking, its strength and the surface inflow feeding it (steps 4-6).
    rho_w, rho_a: winter and annual surface density; sst, sss: the surface
    now; t_eq: the latitude's sea temperature (what the inflow gives its
    heat up toward); fresh: net fresh water (m/yr); cur: the (wind-driven)
    currents, which the inflow follows; lid: cells the inflow can't reach at
    the surface (shallow straits, the fresh lid under year-round sea ice).
    Returns sinking (Sv per cell), inflow (Sv per cell width, spread), share
    (0..1: how much of the surface water is the inflow), t_in, s_in (its
    temperature and salinity), rho_deep (the deep water's density, per cell
    of each sea, at moc_z), sites (list of dicts per connected sinking area: lat, lon, sv, drho
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
    src = np.repeat(np.arange(n), np.diff(grid.nbr_off))
    along = (cur[src] * cdir).sum(1) / tune["cur_ref"]
    cost = np.exp(-np.clip(tune["moc_follow"] * along, -2.0, 2.0))
    ok = sea & ~chan & (True if lid is None else ~lid)
    d_low, par, root = _paths(low[ok[low]], ok, grid.nbr_off, grid.nbr_idx, cost)
    reach = np.isfinite(d_low)
    # (beyond a channel: the channel's water is what wells up and is drawn in)
    rho_up = (area * ra)[chan].sum() / area[chan].sum() if chan.any() else 0.0
    # (an isolated polar sea with no low latitudes and no channel: no overturning)
    # Each sea that isn't connected to the others has its own deep water; a
    # small one (an inland sea) has none to speak of. Water can sink where
    # it is within moc_drho of that deep water's density (fully at it).
    lab, k = kernels.components(sea, grid.nbr_off, grid.nbr_idx)
    big = np.bincount(lab[sea], area[sea], k) >= tune["moc_sea_km2"]
    deep = np.zeros(n)
    drho = tune["moc_drho"]
    for c in np.flatnonzero(big):
        m = (lab == c) & (polar > 0) & (reach | (chan.any() & ~chan & (lat > _chan_lat(grid, chan))))
        if not m.any():
            continue
        # the deep water: a mix of the densest water there is (its densest
        # moc_top share of the polar sea, by area), made lighter by mixing on
        # its way down (moc_mix)
        o = np.argsort(rs[m])[::-1]
        cum = np.cumsum(area[m][o])
        top = o[: np.searchsorted(cum, tune["moc_top"] * cum[-1]) + 1]
        ref = (rs[m][top] * area[m][top]).sum() / area[m][top].sum() - tune["moc_mix"]
        gate = np.clip((rs[m] - ref + drho) / drho, 0, 1) ** tune["moc_pow"] * polar[m]
        # Stommel's flow law: sinking ~ the density difference that drives it
        dr = np.maximum(rs[m] - np.where(reach[m], ra[np.maximum(root[m], 0)], rho_up), 0.0)
        sinking[m] = tune["moc"] * gate * dr * area[m] / 1e6
        deep[lab == c] = ref
    out["rho_deep"] = deep
    if not sinking.any():
        return out
    # A big sinking area doesn't make a proportionally bigger overturning:
    # the deep return flow is limited by the ocean's size, not the sinking
    # area's (Stommel's two boxes; as zonally averaged, Wright & Stocker
    # 1991): each sea's overturning cell in each hemisphere carries at most
    # moc_k Sv per kg/m3 of its density difference.
    dr_all = np.maximum(rs - np.where(reach, ra[np.maximum(root, 0)], rho_up), 0.0)
    for c in np.flatnonzero(big):
        for h_ in (1.0, -1.0):
            cells = np.flatnonzero((lab == c) & (np.sign(grid.lat) == h_) & (sinking > 0))
            psi = sinking[cells].sum()
            cap = tune["moc_k"] * (sinking[cells] * dr_all[cells]).sum() / max(psi, 1e-12)
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
    Tr = _route(order, par, sinking)
    Q = Tr * SV
    hw = h * 1000.0 * tune["moc_width"] * 1000.0  # m2: the route's area per cell
    t_in = _along(order, par, Q, t_eq, sst, tune["moc_lambda"] * hw / 4.1e6, np.zeros(n))
    s_in = _along(order, par, Q, sss, sss, 0.0, np.maximum(fresh, 0.0) / 3.156e7 * hw)
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
    out["share"] = (1.0 - np.exp(-Ts / h / tune["moc_q0"])) * np.clip((lat - tune["moc_src_lat"]) / 10.0, 0, 1)
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


def freshwater(grid: Grid, sea: np.ndarray, surf: np.ndarray, precip: np.ndarray, evap: np.ndarray,
               runoff: np.ndarray, ice_m: np.ndarray, melt: np.ndarray | None, tune: dict,
               export: np.ndarray | float | None = None) -> dict:
    """Net fresh water into the sea surface (m/yr, step 1). precip, evap,
    runoff in mm/yr (runoff on land), ice_m: sea ice grown per winter (m),
    export: the share of it that drifts away (default ice_export), melt: ice-sheet meltwater (m/yr of water; on land routed like the
    rivers, at sea entering where it is). Returns the parts and the total
    with its (global, area-weighted) mean over the sea taken off."""
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
    mean = (tot * area)[sea].sum() / max(area[sea].sum(), 1e-9)
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
    from .grid import build_grid
    level = min(level, grid.level)
    key = (id(grid), grid.n, level, hash(sea.tobytes()))
    if key not in _COARSE:
        if len(_COARSE) > 8:
            _COARSE.clear()
        cg = build_grid(level)
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
          start: dict | None = None, iced: np.ndarray | None = None, depth: np.ndarray | None = None) -> dict:
    """Salinity, density and the overturning together, to a steady state
    (moc_iters damped iterations), on a coarser grid (moc_level: the
    overturning is thousands of km across; ~10x cheaper). There the
    inflow's warmth is added to the sea temperature sst0 (without it) the
    way climate.sea_surface would: by the same currents, part of the
    latitude's mean change taken off (moc_zonal).
    sst_of(share, t_in): the full sea-surface temperature (on grid) where a
    share of the surface water is the overturning's inflow at t_in, used
    once at the end. t_eq: the latitude's sea temperature; cur: the
    currents; fresh: net fresh water (m/yr, freshwater()'s total); ice_m:
    sea ice grown per winter (m); sea_half: the sea's seasonal half-swing
    (C); iced: how perennial the sea ice is (0..1); depth: sea depth (m).
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
    iced_c = None if iced is None else dn(iced)
    cur_c = np.where(sea_c[:, None], dn(cur), 0.0)
    # The inflow is a layer hundreds of m deep: it can't pass a strait
    # shallower than moc_sill (Bering), and where the sea is iced over all
    # year it dives under the fresh surface layer (the Arctic halocline).
    lid = np.zeros(cg.n, bool)
    if depth is not None:
        lid |= dn(depth) < tune["moc_sill"]
    if iced_c is not None:
        lid |= iced_c > 0.5
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
        zm = tune["moc_zonal"] * C.zonal_mean(cg, E, sea_c)
        return np.where(sea_c, np.maximum(sst0_c + E - zm, C.FREEZE), sst0_c)

    def state(st, sst):
        # (which water sinks deepest is decided deep down: compared at moc_z)
        sss = salinity(cg, sea_c, fresh_c, cur_c, tune, iced_c, st["share"], st["s_in"], out_w, warm.get("S"))
        warm["S"] = sss
        rho_w = density(np.maximum(sst - half_c, C.FREEZE), sss + brine, tune["moc_z"])
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
    for it in range(max(int(tune["moc_iters"]), 1)):
        sss, rho_w, rho_a = state(st, sst)
        # With no earlier state, the first passes let every sea that is
        # nearly dense enough sink, as if spun up from a well-mixed ocean,
        # then tighten that to moc_drho over the iterations (all but the last
        # two): the salt the overturning brings decides which sites keep
        # sinking.
        spin = it == 0 and start is None
        n_sp = max(int(tune["moc_iters"]) - 2, 1)
        f = tune["moc_spin"] ** max(1.0 - it / n_sp, 0.0) if start is None else 1.0
        ov = overturning(cg, sea_c, rho_w, rho_a, sst, sss, teq_c, fresh_c, cur_c,
                         {**tune, "moc_drho": tune["moc_drho"] * f}, lid)
        a = 1.0 if spin else tune["moc_relax"]
        st = {k: st[k] + a * (ov[k] - st[k]) for k in st}
        sst = sst_c(st)
    sss, rho_w, rho_a = state(st, sst)
    # back on the fine grid
    sst_f = sst_of(np.clip(_up(M, st["share"]), 0, 1), _up(M, st["t_in"]))
    sss_f = np.where(sea, _up(M, sss), S0)
    area = cell_area_km2(grid)
    sss_f = np.where(sea, sss_f + S0 - (sss_f * area)[sea].sum() / max(area[sea].sum(), 1e-9), S0)
    brine_f = S0 * ICE_FRESH * np.where(sea, ice_m, 0.0) / tune["brine_m"]
    sink_f = _up(M, ov["sinking"]) * sea
    sink_f *= ov["sinking"].sum() / max(sink_f.sum(), 1e-12)  # (same total)
    return dict(sss=sss_f, density=density(sst_f, sss_f),
                density_w=density(np.maximum(sst_f - sea_half, C.FREEZE), sss_f + brine_f),
                sinking=sink_f, inflow=_up(M, ov["inflow"]) * sea, state=st,
                sites=ov["sites"], sst=sst_f)


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


def loop_schematic(grid: Grid, elev: np.ndarray, c: dict, tune: dict | None = None) -> dict:
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
    sea = elev <= 0
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
            runs[key] = _paths(np.flatnonzero(targets), sea, grid.nbr_off, grid.nbr_idx, cost)
        return runs[key]

    # surface limb: from the low latitudes, riding the model's inflow
    infl = np.asarray(c.get("moc_inflow", np.zeros(n)), float)
    ref = np.percentile(infl[infl > 0], 95) if (infl > 0).any() else 1.0
    s_cost = (1.0 / (0.05 + np.clip(infl / max(ref, 1e-12), 0, 1)))[grid.nbr_idx]
    low = sea & (np.abs(grid.lat) < tune["moc_src_lat"])
    s_ok = sea & ~chan
    s_dist, s_par, _ = _paths(np.flatnonzero(low), s_ok, grid.nbr_off, grid.nbr_idx, s_cost)
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
