"""Human-use layers (PW-099): where a world can be used by people.

Five derived views of fields the simulation already has (no new physics; crude
but sound approximations, each with its rule written next to it):

  river_nav    reaches of rivers by what can float on them: 1 small boats,
               2 barges, 3 sea-going ships. From the river's depth (hydraulic
               geometry of the mean discharge), the gradient over the next
               few km (rapids), the months it is frozen, and falls (zooms).
  harbour      sheltered deep water at the coast: 1 anchorage, 2 harbour,
               3 fine harbour. From the effective fetch (how far the open water
               reaches around the compass; 16 bearings), depth, a river mouth
               (an estuary shelters itself) and the months of sea ice.
  pass         the lowest crossings of a divide between drainage basins that
               are separated by real relief: 1 open most of the year,
               2 seasonal, 3 snow-bound most of the year; pass_height (m).
  fertile      farmland quality 0..4 (fertile_score 0..1): soil fertility and
               depth, water (rain against potential evaporation, or a big
               river to irrigate from), the growing season (months above 5 C),
               slope, minus permafrost, peat and flooding.
  fresh_water  reach of perennial fresh water: 3 on site (a perennial
               stream, fresh lake, wetland or spring), 2 beside it, 1 within
               a day or two, 0 none; fresh_km is the distance; spring marks
               foot-of-mountain springs in dry ground.

One implementation runs on a *Net*: a graph of nodes (a world's cells, a
zoom's pixels) with undirected edges and a downstream pointer, so the world
and the zoom share the rules and differ only in what they resolve (a 120 km
cell cannot see a fjord, a rapid or a saddle; a 2 km pixel can). Thresholds
that depend on distance are given in km and scale with the node spacing.

    world_layers(grid, layers)  -> {name: array} to store with the world
    analyse_world(grid, layers) -> (layers, tables) incl. what export draws
    zoom_layers / analyse_zoom  -> the same for a zoom's decoded rasters
"""

from __future__ import annotations

import numpy as np

from .geo import R_KM, is_land, xyz

FREEZE_SEA = -1.8  # C: sea water freezes (climate.FREEZE)

# ---------------------------------------------------------------------------
# Legends (class-map ids; store.legends())
# ---------------------------------------------------------------------------
def _leg(*items):
    return [{"id": i, "name": n, "color": c} for i, (n, c) in enumerate(items)]


LEGEND = {
    "river_nav": _leg(("not navigable", "#00000000"), ("small boats", "#9ad0e8"), ("barges", "#3b8fd0"),
                      ("sea-going", "#1a3f9c")),
    "harbour": _leg(("none", "#00000000"), ("anchorage", "#f2c14e"), ("harbour", "#e8833a"), ("fine harbour", "#c0392b")),
    "pass": _leg(("none", "#00000000"), ("open most of the year", "#7fc36b"), ("seasonal", "#e3b341"),
                 ("snow-bound most of the year", "#c9d6e3")),
    "fertile": _leg(("not arable", "#8b8178"), ("marginal (grazing)", "#d9c98b"), ("fair", "#b5c96a"),
                    ("good", "#6fae45"), ("prime", "#2f7d32")),
    "fresh_water": _leg(("none within reach", "#d9c98b"), ("a day or two away", "#bfe0ef"),
                        ("close by", "#7ec0e0"), ("on site", "#2f8fd0")),
}


def legend() -> dict:
    return LEGEND


# the world layers' store specs / the zoom's: (dtype, scale, units, description)
LAYER_SPECS = {
    "river_nav": ("u1", 1, "class", "navigable rivers: 0 no, 1 small boats, 2 barges, 3 sea-going (legend human_use.river_nav)"),
    "harbour": ("u1", 1, "class", "natural harbours at sea: 0 none, 1 anchorage, 2 harbour, 3 fine harbour"),
    "pass": ("u1", 1, "class", "mountain pass on the divide (the saddle cell): 1 open most of the year, "
                               "2 seasonal, 3 snow-bound most of the year; 0 elsewhere"),
    "pass_height": ("<u2", 1, "m", "height of the pass (0 where there is none)"),
    "fertile": ("u1", 1, "class", "farmland: 0 not arable .. 4 prime (soil, water, growing season, slope)"),
    "fertile_score": ("u1", 0.01, "0-1", "farmland score behind the fertile classes"),
    "fresh_water": ("u1", 1, "class", "reach of perennial fresh water: 3 on site, 2 close, 1 a day or two, 0 none"),
    "fresh_km": ("<u2", 0.1, "km", "distance to the nearest perennial fresh water (0 on site; capped at 6000)"),
    "spring": ("u1", 1, "0/1", "1 where springs rise at the foot of wetter high ground in dry country"),
}
NAMES = tuple(LAYER_SPECS)
CLASS_MAPS = ("river_nav", "harbour", "pass", "fertile", "fresh_water")  # the class-id layers (LEGEND keys)


# ---------------------------------------------------------------------------
# The graph
# ---------------------------------------------------------------------------
class Net:
    """n nodes; undirected edges (ea, eb) of length elen (km); nxt: the node
    downstream (-1 none) and down_km the distance to it; area: km^2 per node;
    step: the typical spacing, km; kind: 'world' or 'zoom'."""

    def __init__(self, n, ea, eb, elen, nxt, down_km, area, step, kind, lat=None):
        self.n, self.ea, self.eb, self.elen = n, ea, eb, elen
        self.nxt, self.down_km, self.area, self.step, self.kind, self.lat = nxt, down_km, area, step, kind, lat

    @classmethod
    def world(cls, grid, downstream=None):
        c = grid.centers
        e = np.asarray(grid.edges)
        elen = np.arccos(np.clip((c[e[:, 0]] * c[e[:, 1]]).sum(1), -1, 1)) * R_KM
        if downstream is None:
            nxt, dk = np.full(grid.n, -1), np.zeros(grid.n)
        else:
            nxt = np.asarray(downstream).astype(np.int64)
            nxt = np.where((nxt >= 0) & (nxt < grid.n), nxt, -1)
            dk = np.where(nxt >= 0, np.arccos(np.clip((c * c[np.maximum(nxt, 0)]).sum(1), -1, 1)) * R_KM, 0.0)
        return cls(grid.n, e[:, 0], e[:, 1], elen, nxt, dk, np.full(grid.n, 4 * np.pi * R_KM**2 / grid.n),
                   grid.spacing * R_KM, "world", grid.lat)

    @classmethod
    def raster(cls, ny, nx, res_km, receiver=None):
        """Pixels of a zoom (row-major, rows run south); 8 neighbours; receiver: the zoom's D8 slots."""
        idx = np.arange(ny * nx, dtype=np.int32).reshape(ny, nx)
        ea = [idx[:, :-1].ravel(), idx[:-1, :].ravel(), idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel()]
        eb = [idx[:, 1:].ravel(), idx[1:, :].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()]
        ln = [np.full(len(a), res_km if i < 2 else res_km * 2**0.5, np.float32) for i, a in enumerate(ea)]
        nxt, dk = np.full(ny * nx, -1), np.zeros(ny * nx)
        if receiver is not None:
            rec = np.asarray(receiver).ravel().astype(int)
            k = np.where(rec < 4, rec, rec + 1)
            rr, cc = np.divmod(np.arange(ny * nx), nx)
            nr, nc = rr + k // 3 - 1, cc + k % 3 - 1
            ok = (rec != 255) & (nr >= 0) & (nr < ny) & (nc >= 0) & (nc < nx)
            nxt = np.where(ok, nr * nx + nc, -1)
            dk = np.where(ok, res_km * np.where((k % 2) == 0, 1.0, 1.0) * np.where(np.isin(k, (1, 3, 5, 7)), 1.0, 2**0.5), 0.0)
        return cls(ny * nx, np.concatenate(ea), np.concatenate(eb), np.concatenate(ln), nxt, dk,
                   np.full(ny * nx, res_km**2), res_km, "zoom")

    def hops(self, km: float) -> int:
        return max(int(round(km / self.step)), 1)


def dist_from(net: Net, src: np.ndarray, max_km: float) -> np.ndarray:
    """Km along the edges from the nearest True node of src (inf beyond max_km)."""
    d = np.where(src, 0.0, np.inf)
    for _ in range(int(np.ceil(max_km / net.step * 1.5)) + 1):
        m = d.copy()
        np.minimum.at(m, net.ea, d[net.eb] + net.elen)
        np.minimum.at(m, net.eb, d[net.ea] + net.elen)
        m = np.where(m > max_km, np.inf, m)
        if np.array_equal(m, d):
            break
        d = m
    return d


def hop_min(net: Net, z: np.ndarray, hops: int, same: np.ndarray | None = None) -> np.ndarray:
    """The lowest z within `hops` edges (only along edges where `same` is True, if given)."""
    ea, eb = (net.ea, net.eb) if same is None else (net.ea[same], net.eb[same])
    m = z.astype(float).copy()
    for _ in range(hops):
        n2 = m.copy()
        np.minimum.at(n2, ea, m[eb])
        np.minimum.at(n2, eb, m[ea])
        m = n2
    return m


def hop_max(net: Net, z: np.ndarray, hops: int) -> np.ndarray:
    return -hop_min(net, -np.asarray(z, float), hops)


def months_below(t_warm, t_cold, thr) -> np.ndarray:
    """Months a year below thr, the monthly temperature a sine between the coldest and warmest month
    (climate.sea_ice_share does the same with half-years)."""
    t_warm, t_cold = np.maximum(t_warm, t_cold), np.minimum(t_warm, t_cold)
    tm, a = 0.5 * (t_warm + t_cold), np.maximum(0.5 * (t_warm - t_cold), 1e-6)
    return 12 * (1 - np.arccos(np.clip((thr - tm) / a, -1, 1)) / np.pi)


def slope_deg_net(net: Net, z: np.ndarray) -> np.ndarray:
    """Steepest slope to a neighbour, degrees (node spacing sets what it can see)."""
    s = np.zeros(net.n)
    g = np.abs(z[net.ea] - z[net.eb]) / (net.elen * 1000.0)
    np.maximum.at(s, net.ea, g)
    np.maximum.at(s, net.eb, g)
    return np.degrees(np.arctan(s))


# ---------------------------------------------------------------------------
# Navigable rivers
# ---------------------------------------------------------------------------
# Mean-flow depth from discharge (a Leopold-Maddock style regression, d ~ 0.27 Q^0.3 m) against what floats:
# a skiff 0.6 m, a laden barge 1.8 m, a coaster / sea-going ship 3.5 m. Steeper than the gradient limit the
# reach has rapids for that class (poling and tracking up to 4 m/km, barges 1 m/km, ships 0.3 m/km).
NAV_DEPTH_M = (0.6, 1.8, 3.5)
NAV_SLOPE = (4e-3, 1e-3, 3e-4)
NAV_MIN_OPEN_MONTHS = 3  # a river iced over more than 9 months is not a way to travel
NAV_RUN_KM = 8.0  # the gradient is measured over about this much river (a zoom's pixels are noisy)


def river_depth_m(q) -> np.ndarray:
    return 0.27 * np.maximum(np.asarray(q, float), 0.0) ** 0.3


def river_nav(net: Net, z, q, land, frozen_months, falls=None):
    """(class uint8, gradient m/m, open months, reaches-the-sea bool) per node. z: the river surface
    (ground, or a lake's level); q: mean discharge m^3/s; falls: bool mask of nodes with a fall."""
    n = net.n
    hops = net.hops(NAV_RUN_KM) if net.kind == "zoom" else 1
    tgt, length = np.arange(n), np.zeros(n)
    for _ in range(hops):
        step = net.nxt[tgt]
        ok = step >= 0
        length += np.where(ok, net.down_km[tgt], 0.0)
        tgt = np.where(ok, step, tgt)
    grad = np.where(length > 0, (z - z[tgt]) / np.maximum(length * 1000.0, 1e-9), 0.0)
    grad = np.maximum(grad, 0.0)
    depth = river_depth_m(q)
    cls = np.zeros(n, np.uint8)
    for k in range(3):
        cls = np.where((depth >= NAV_DEPTH_M[k]) & (grad <= NAV_SLOPE[k]), k + 1, cls).astype(np.uint8)
    openm = 12 - np.clip(np.round(frozen_months), 0, 12)
    cls = np.where(land & (openm >= NAV_MIN_OPEN_MONTHS), cls, 0).astype(np.uint8)
    if falls is not None:
        cls = np.where(falls, 0, cls).astype(np.uint8)
    # does the reach lead to the sea along navigable water (a portage-free route)?
    nx_ = net.nxt
    safe = np.maximum(nx_, 0)
    to_sea = (cls > 0) & (nx_ >= 0) & ~land[safe]
    conn = to_sea.copy()
    for _ in range(5000):
        new = conn | ((cls > 0) & (nx_ >= 0) & land[safe] & conn[safe])
        if np.array_equal(new, conn):
            break
        conn = new
    return cls, grad, openm, conn


def nav_reaches(lines, cls, q, grad, openm, conn, km_of) -> list[dict]:
    """Split river lines ({nodes, q}; export.river_lines) into runs of one class: [{nodes, cls, ...}]."""
    out = []
    for ln in lines:
        nodes = np.asarray(ln["nodes"])
        c = cls[nodes[:-1]]
        i = 0
        while i < len(c):
            if c[i] == 0:
                i += 1
                continue
            j = i
            while j + 1 < len(c) and c[j + 1] == c[i]:
                j += 1
            seg = nodes[i:j + 2]
            body = nodes[i:j + 1]
            out.append({"nodes": seg, "cls": int(c[i]), "q_min": float(q[body].min()), "q_max": float(q[body].max()),
                        "gradient_m_per_km": float(np.mean(grad[body]) * 1000), "open_months": int(openm[body].min()),
                        "to_sea": bool(conn[body[-1]]), "length_km": km_of(seg)})
            i = j + 1
    return out


# ---------------------------------------------------------------------------
# Harbours
# ---------------------------------------------------------------------------
HARBOUR_DEPTH_M = 6.0  # a loaded ship's draught plus a margin
HARBOUR_FETCH_KM = 50.0  # km: zooms look this far for open water (fetch); a sea pit smaller than this square is no sea
DEPTH_REACH_KM = 6.0  # (zooms: the deepest water within this of the pixel; a shoreface shoals to the beach)
HARBOUR_SHELTER = (0.60, 0.72, 0.85)  # 1 - effective fetch / reach; a straight coast scores 0.5 (half the horizon is land)
ESTUARY_Q = 300.0  # m^3/s: a river mouth this big carves an estuary (shelters itself)
ESTUARY_BONUS = 0.2
SEA_ICE_MONTHS = (6, 10)  # one class down above the first, none above the second
BEARINGS = np.radians(np.arange(16) * 22.5)


def fetch_world(grid, land: np.ndarray, cells: np.ndarray, reach_cells: float = 6.0) -> np.ndarray:
    """Effective fetch (km, mean over 16 bearings of the open-water distance, capped at the reach) of
    the given sea cells: rays on the sphere, stepping half a cell."""
    step = grid.spacing / 2
    S = int(reach_cells * 2)
    c = grid.centers[cells]
    lat, lon = np.radians(grid.lat[cells]), np.radians(grid.lon[cells])
    east = np.stack([-np.sin(lon), np.cos(lon), np.zeros_like(lon)], 1)
    north = np.stack([-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)], 1)
    dist = np.full((len(cells), len(BEARINGS)), S * step * R_KM)
    for b, th in enumerate(BEARINGS):
        t = east * np.sin(th) + north * np.cos(th)
        alive = np.ones(len(cells), bool)
        for s in range(1, S + 1):
            p = c * np.cos(s * step) + t * np.sin(s * step)
            hit = land[grid.locate(np.ascontiguousarray(p))] & alive
            dist[hit, b] = s * step * R_KM
            alive &= ~hit
            if not alive.any():
                break
    return dist.mean(1), S * step * R_KM


def fetch_raster(land: np.ndarray, pix: np.ndarray, res_km: float, reach_km: float):
    """The same on a zoom's raster: (ny, nx) land mask, pix: flat indices; a ray leaving the zoom is open."""
    ny, nx = land.shape
    S = max(int(reach_km / res_km), 1)
    r0, c0 = np.divmod(pix, nx)
    dist = np.full((len(pix), len(BEARINGS)), S * res_km)
    for b, th in enumerate(BEARINGS):
        dr, dc = -np.cos(th), np.sin(th)  # (north is up the rows)
        alive = np.ones(len(pix), bool)
        for s in range(1, S + 1):
            r, c = np.round(r0 + s * dr).astype(int), np.round(c0 + s * dc).astype(int)
            inside = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
            hit = alive & inside & land[np.clip(r, 0, ny - 1), np.clip(c, 0, nx - 1)]
            dist[hit, b] = s * res_km
            alive &= ~hit & inside
            if not alive.any():
                break
    return dist.mean(1), S * res_km


def harbours(net: Net, depth, land, sea_ice_months, q_mouth, fetch_eff, reach_km, near):
    """(class uint8, shelter float, kind per node) at the sea nodes `near` the coast with fetch_eff given
    for those nodes (arrays over the nodes where near is True)."""
    n = net.n
    shelter = np.zeros(n)
    shelter[near] = 1 - np.clip(fetch_eff / reach_km, 0, 1)
    score = shelter + ESTUARY_BONUS * (q_mouth >= ESTUARY_Q)
    # depth: m of water, deepest within reach (a shoreface shoals to the beach; a harbour needs deep water beside it)
    cls = np.zeros(n, np.uint8)
    for k, th in enumerate(HARBOUR_SHELTER):
        cls = np.where(near & (score >= th), k + 1, cls)
    cls = np.where(depth >= HARBOUR_DEPTH_M, cls, 0)
    cls = np.where(sea_ice_months >= SEA_ICE_MONTHS[0], np.maximum(cls.astype(int) - 1, 0), cls)
    cls = np.where(sea_ice_months >= SEA_ICE_MONTHS[1], 0, cls).astype(np.uint8)
    return cls, shelter


def open_sea(sea, res_km: float):
    """(ny, nx) bool: the sea pixels of a zoom that ships reach from outside it: their (8-connected)
    water touches the zoom's edge, or is a sea of its own at least HARBOUR_FETCH_KM across (area)."""
    from .zoom_kernels import label_components
    if not sea.any():
        return sea
    ny, nx = sea.shape
    lab, size = label_components(sea.ravel(), nx, ny)
    lab = lab.reshape(ny, nx)
    ok = np.asarray(size, float) * res_km ** 2 >= HARBOUR_FETCH_KM ** 2
    rim = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    ok[rim[rim >= 0]] = True
    return sea & np.where(lab >= 0, ok[np.maximum(lab, 0)], False)


def _mouth_discharge(net: Net, land, q) -> np.ndarray:
    """Per sea node: the biggest river discharge entering it from land (a river mouth)."""
    m = np.zeros(net.n)
    d = net.nxt
    ok = (d >= 0) & land & ~land[np.maximum(d, 0)]
    np.maximum.at(m, d[ok], q[ok])
    return m


def _coast_nodes(net: Net, land, hops: int):
    return np.isfinite(dist_from(net, land, hops * net.step * 1.5)) & ~land


# ---------------------------------------------------------------------------
# Passes
# ---------------------------------------------------------------------------
PASS_BASINS_KM2 = {"world": (3e5, 2.5e4), "zoom": (2e3, 150.0)}  # one basin at least this big, the other this
PASS_RELIEF_M = {"world": 300.0, "zoom": 150.0}  # the saddle above the valley floors on both sides
PASS_RELIEF_KM = {"world": 0.0, "zoom": 20.0}  # (km looked over for those floors; the world: 2 cells)
PASS_SNOW_C = -3.0  # months with the pass colder than this are snow-bound
PASS_CLASS_OPEN = (9, 4)  # open months: >= 9 class 1, >= 4 class 2, else 3


def basin_labels(net: Net, land) -> np.ndarray:
    """Outlet node of each land node's drainage basin (a land node whose receiver is sea / none is its own)."""
    par = np.where(land & (net.nxt >= 0) & land[np.maximum(net.nxt, 0)], net.nxt, np.arange(net.n))
    for _ in range(40):
        p2 = par[par]
        if np.array_equal(p2, par):
            break
        par = p2
    return par


def passes(net: Net, z, land, t_warm, t_cold, precip):
    """List of passes [{a, b, node, height, open_months, area_a, area_b}], one per pair of drainage basins
    that touch (the lowest crossing), where one basin is big and the other not tiny, the crossing is above
    the valley floors of both sides by the relief, and the crossing is the lowest of the neighbourhood."""
    lab = basin_labels(net, land)
    area = np.bincount(lab[land], weights=net.area[land], minlength=net.n)
    big, small = PASS_BASINS_KM2[net.kind]
    la, lb = lab[net.ea], lab[net.eb]
    cross = land[net.ea] & land[net.eb] & (la != lb)
    cross &= (np.maximum(area[la], area[lb]) >= big) & (np.minimum(area[la], area[lb]) >= small)
    ia = np.flatnonzero(cross)
    if not len(ia):
        return []
    a, b = net.ea[ia], net.eb[ia]
    sad = np.maximum(z[a], z[b])
    lo, hi = np.minimum(la[ia], lb[ia]), np.maximum(la[ia], lb[ia])
    order = np.lexsort((sad, hi, lo))
    key = lo[order].astype(np.int64) * net.n + hi[order]
    first = order[np.r_[True, key[1:] != key[:-1]]]
    # valley floors on each side: the lowest ground in the node's own basin within reach
    same = land[net.ea] & land[net.eb] & (la == lb)
    k = max(2, net.hops(PASS_RELIEF_KM[net.kind])) if net.kind == "zoom" else 2
    floor = hop_min(net, np.where(land, z, np.inf), k, same)
    out = []
    for e in first:
        x, y = int(a[e]), int(b[e])
        top = max(z[x], z[y])
        if top - floor[x] < PASS_RELIEF_M[net.kind] or top - floor[y] < PASS_RELIEF_M[net.kind]:
            continue
        node = x if z[x] >= z[y] else y
        snow = float(months_below(t_warm[node], t_cold[node], PASS_SNOW_C)) if precip[node] > 100 else 0.0
        out.append({"a": int(la[ia][e]), "b": int(lb[ia][e]), "node": node, "other": y if node == x else x,
                    "height": float(top), "open_months": int(round(12 - snow)),
                    "area_a": float(area[la[ia][e]]), "area_b": float(area[lb[ia][e]])})
    # keep only the lowest pass within a couple of nodes' reach (a divide is crossed by many basin pairs)
    out.sort(key=lambda p: p["height"])
    taken, keep = np.zeros(net.n, bool), []
    near = max(net.hops(40.0), 1) if net.kind == "zoom" else 1
    for p in out:
        if taken[p["node"]]:
            continue
        keep.append(p)
        m = np.zeros(net.n, bool)
        m[p["node"]] = True
        taken |= np.isfinite(dist_from(net, m, near * net.step * 1.5))
    return keep


def pass_class(open_months) -> int:
    return 1 if open_months >= PASS_CLASS_OPEN[0] else 2 if open_months >= PASS_CLASS_OPEN[1] else 3


# ---------------------------------------------------------------------------
# Fertile land
# ---------------------------------------------------------------------------
FERTILE_EXP = {"fertility": 0.35, "water": 0.30, "season": 0.25, "depth": 0.10}  # weights of the geometric mean
FERTILE_CLASSES = (0.30, 0.48, 0.62, 0.75)  # score floors of marginal, fair, good, prime
GROW_C = 5.0  # a month above this grows crops
GROW_FULL_MONTHS = 6.0  # a full season for the score
IRRIGATE_Q = 100.0  # m^3/s: a river this big irrigates its banks


def holdridge_pet(t_warm, t_cold) -> np.ndarray:
    """Potential evaporation mm/yr from the biotemperature (monthly mean clipped to 0..30 C) x 58.93
    (Holdridge); for a zoom, which has no PET layer."""
    t = np.zeros_like(np.asarray(t_warm, float))
    for m in range(12):
        phase = np.cos(2 * np.pi * (m + 0.5) / 12)
        t += np.clip(0.5 * (t_warm + t_cold) + 0.5 * (t_warm - t_cold) * phase, 0, 30)
    return 58.93 * t / 12


def fertile(fert, depth, moisture, grow_months, slope, land, ice, permafrost, peat, flooded):
    """(score 0..1, class 0..4)."""
    w = FERTILE_EXP
    f = np.clip(fert, 0.01, 1) ** w["fertility"] * np.clip(moisture, 0.01, 1) ** w["water"] \
        * np.clip(grow_months / GROW_FULL_MONTHS, 0.01, 1) ** w["season"] \
        * np.clip(depth / 1.0, 0.05, 1) ** w["depth"]
    t = np.clip((slope - 8.0) / (25.0 - 8.0), 0, 1)
    f = f * (1 - t * t * (3 - 2 * t))  # (gentle ground to about 8 degrees, none steeper than 25)
    f = f * np.array([1.0, 0.85, 0.5, 0.2])[np.clip(permafrost.astype(int), 0, 3)]
    f = f * np.where(peat > 0.5, 0.5, 1.0) * (1 - 0.6 * np.clip(flooded / 60.0, 0, 1))
    f = np.where(land & (ice <= 0), f, 0.0)
    cls = np.zeros(len(f), np.uint8)
    for k, th in enumerate(FERTILE_CLASSES):
        cls = np.where(f >= th, k + 1, cls).astype(np.uint8)
    return f, cls


# ---------------------------------------------------------------------------
# Fresh water
# ---------------------------------------------------------------------------
STREAM_RUNOFF_MM = 100.0  # a land node shedding this much a year has perennial streams
RIVER_PERENNIAL_Q = {"world": 20.0, "zoom": 2.0}  # m^3/s through a node (an exotic river in dry ground)
ARID_MM = 250.0  # a zoom's river in ground drier than this is perennial only if big
ARID_Q = 20.0
FRESH_REACH = {"world": (0.0, 1.2, 2.3), "zoom": (3.0, 10.0, 30.0)}  # class 3 / 2 / 1 reach: world in cells, zoom km
WET_FLOODED_PCT = 20.0
SPRING_RELIEF_M = {"world": 800.0, "zoom": 400.0}  # wetter ground this far above
SPRING_DRY_MM = 100.0  # supply under this is dry
SPRING_WET_MM = 250.0  # a catchment above supplying this feeds springs


def springs(net: Net, z, supply_mm, land, flat_deg=None):
    """Foot-of-mountain springs: dry land with ground at least the relief higher and wetter within reach."""
    k = 2 if net.kind == "world" else net.hops(12.0)
    hz = hop_max(net, np.where(land, z, -np.inf), k)
    wetter = hop_max(net, np.where(land, supply_mm, 0.0), k)
    sp = land & (supply_mm < SPRING_DRY_MM) & (hz - z >= SPRING_RELIEF_M[net.kind]) & (wetter >= SPRING_WET_MM)
    if flat_deg is not None:
        sp &= flat_deg < 6.0
    return sp


def fresh_reach(net: Net, sources: np.ndarray):
    """(class uint8, km float) of the reach of fresh water from the source nodes."""
    r = FRESH_REACH[net.kind]
    scale = net.step if net.kind == "world" else 1.0
    far = r[2] * scale + net.step
    d = dist_from(net, sources, far)
    cls = np.zeros(net.n, np.uint8)
    cls = np.where(d <= r[2] * scale, 1, cls)
    cls = np.where(d <= r[1] * scale, 2, cls)
    cls = np.where(d <= r[0] * scale, 3, cls).astype(np.uint8)
    return cls, np.where(np.isfinite(d), d, far)


# ---------------------------------------------------------------------------
# Worlds
# ---------------------------------------------------------------------------
def _has(L, *keys):
    return all(k in L for k in keys)


def analyse_world(grid, L: dict) -> tuple[dict, dict]:
    """(layers, tables) of a world from its layers L (a dict of per-cell arrays; the subsets whose inputs
    are missing are left out). tables: what the export draws: nav (river reaches), harbours, passes, springs."""
    from . import hydrology
    out, tab = {}, {}
    n = grid.n
    el = np.asarray(L["elevation"], float)
    ice = np.asarray(L.get("ice", np.zeros(n)), float)
    land = is_land(el, ice)
    net = Net.world(grid, L.get("downstream"))
    q = hydrology.discharge(grid, np.asarray(L["flow"], float)) if "flow" in L else np.zeros(n)
    lake = (np.asarray(L["lake"]) > 0) if "lake" in L else np.zeros(n, bool)
    zs = np.where(lake & ("lake_level" in L), np.asarray(L.get("lake_level", el), float), el)
    tw = np.asarray(L.get("warm_month", L.get("temperature_jul", 10 + 0 * el)), float)
    tc = np.asarray(L.get("cold_month", L.get("temperature_jan", 0 * el)), float)
    runoff = np.asarray(L.get("runoff", np.zeros(n)), float)
    # navigable rivers
    if _has(L, "flow", "downstream"):
        frozen = np.asarray(L.get("river_frozen", months_below(tw, tc, -2.0)), float)
        cls, grad, openm, conn = river_nav(net, zs, q, land, frozen)
        out["river_nav"] = cls
        tab["nav"] = {"cls": cls, "q": q, "grad": grad, "open": openm, "conn": conn}
    # harbours
    sea = ~land
    cnt = np.bincount(net.ea, weights=land[net.eb], minlength=n) + np.bincount(net.eb, weights=land[net.ea], minlength=n)
    near = sea & (cnt > 0)
    out["harbour"] = np.zeros(n, np.uint8)  # always present, all 0 on a planet without a coast, so every consumer can index it
    if near.any():
        cells = np.flatnonzero(near)
        fe, reach = fetch_world(grid, land, cells)
        full = np.zeros(n)
        full[cells] = fe
        ice_m = months_below(tw, tc, FREEZE_SEA) * sea
        qm = _mouth_discharge(net, land, q)
        depth = hop_max(net, np.where(sea, -el, 0.0), 0)
        hcls, shelter = harbours(net, depth, land, ice_m, qm, full[near], reach, near)
        out["harbour"] = hcls
        tab["harbour"] = {"cls": hcls, "shelter": shelter, "fetch_km": full, "ice_months": ice_m, "q_mouth": qm, "depth": depth,
                          "reach_km": reach}
    # passes
    if _has(L, "downstream"):
        precip = np.asarray(L.get("precipitation", 500 + 0 * el), float)
        ps = passes(net, el, land, tw, tc, precip)
        pc, ph = np.zeros(n, np.uint8), np.zeros(n)
        for p in ps:
            pc[p["node"]] = pass_class(p["open_months"])
            ph[p["node"]] = p["height"]
        out["pass"], out["pass_height"] = pc, np.round(ph).astype(int)
        tab["passes"] = ps
    # fertile land
    if _has(L, "soil_fertility", "soil_depth"):
        pet = np.asarray(L["pet"], float) if "pet" in L else holdridge_pet(tw, tc)
        precip = np.asarray(L.get("precipitation", runoff + pet), float)
        moist = np.clip(np.asarray(L["evaporation"], float) / np.maximum(pet, 1.0), 0, 1) if "evaporation" in L \
            else np.clip(precip / np.maximum(pet, 1.0), 0, 1)
        irrigated = land & (q >= IRRIGATE_Q)
        moist = np.where(irrigated, np.maximum(moist, 0.8), moist)
        grow = 12 - months_below(tw, tc, GROW_C)
        score, fc = fertile(np.asarray(L["soil_fertility"], float), np.asarray(L["soil_depth"], float), moist, grow,
                            slope_deg_net(net, el), land, ice, np.asarray(L.get("permafrost", np.zeros(n))),
                            np.asarray(L.get("peat_depth", np.zeros(n)), float), np.asarray(L.get("flooded", np.zeros(n)), float))
        out["fertile"], out["fertile_score"] = fc, np.round(100 * score).astype(int)
    # fresh water
    if _has(L, "runoff"):
        fresh_lake = lake & (np.asarray(L.get("lake_kind", np.ones(n))) == 1)
        src = land & ((runoff >= STREAM_RUNOFF_MM) | (q >= RIVER_PERENNIAL_Q["world"]) | fresh_lake
                      | (np.asarray(L.get("flooded", np.zeros(n))) >= WET_FLOODED_PCT))
        sp = springs(net, el, runoff, land)
        fcls, fkm = fresh_reach(net, src | sp)
        out["fresh_water"], out["fresh_km"], out["spring"] = fcls, np.round(fkm * 10).astype(int) / 10, sp.astype(np.uint8)
        tab["springs"] = np.flatnonzero(sp)
    tab["net"] = net
    return out, tab


def world_layers(grid, L: dict) -> dict:
    """The layers to store with a world (finish())."""
    return analyse_world(grid, L)[0]


# ---------------------------------------------------------------------------
# Zooms
# ---------------------------------------------------------------------------
def analyse_zoom(L: dict, res_km: float, falls_px=()) -> tuple[dict, dict]:
    """(layers (ny, nx), tables) of a zoom from its decoded layers L (2-D arrays). falls_px: (row, col) of
    waterfalls, native pixels. Subsets whose inputs are missing are left out."""
    out, tab = {}, {}
    el = np.asarray(L["elevation"], float)
    ny, nx = el.shape
    net = Net.raster(ny, nx, res_km, L.get("receiver"))
    ez = el.ravel()
    water = np.asarray(L["water"]).ravel() if "water" in L else (ez <= 0).astype(int)
    land = water == 0
    ice = np.asarray(L.get("ice", np.zeros_like(el)), float).ravel()
    q = np.asarray(L.get("discharge", np.zeros_like(el)), float).ravel()
    tj = np.asarray(L.get("temperature_jul", L.get("temperature", 10 + 0 * el)), float).ravel()
    tn = np.asarray(L.get("temperature_jan", L.get("temperature", 0 * el)), float).ravel()
    tw, tc = np.maximum(tj, tn), np.minimum(tj, tn)
    precip = np.asarray(L.get("precipitation", 600 + 0 * el), float).ravel()
    if "receiver" in L:
        lake_z = ez + np.asarray(L.get("lake_depth", 0 * el), float).ravel()
        zs = np.where(water == 2, lake_z, ez)
        fmask = np.zeros(net.n, bool)
        for r, c in falls_px:
            fmask[int(r) * nx + int(c)] = True
        fmask = np.isfinite(dist_from(net, fmask, 1.5 * res_km))  # (a fall's point may sit a pixel off its channel)
        frozen = months_below(tw, tc, -2.0)
        cls, grad, openm, conn = river_nav(net, zs, q, land | (water == 2), frozen, fmask)
        cls = np.where(q >= 0.5 * RIVER_PERENNIAL_Q["zoom"], cls, 0).astype(np.uint8)
        out["river_nav"] = cls.reshape(ny, nx)
        tab["nav"] = {"cls": cls, "q": q, "grad": grad, "open": openm, "conn": conn}
    sea = water == 1
    # (a harbour is reached from the open sea: not in a pit of sea cut off inside the zoom, PW-844)
    near = _coast_nodes(net, land, 3) & open_sea(sea.reshape(ny, nx), res_km).ravel()
    out["harbour"] = np.zeros((ny, nx), np.uint8)  # always present (all 0 for an inland zoom): the viewer indexes it unconditionally
    if near.any():
        pix = np.flatnonzero(near)
        fe, reach = fetch_raster(land.reshape(ny, nx), pix, res_km, HARBOUR_FETCH_KM)
        full = np.zeros(net.n)
        full[pix] = fe
        ice_m = months_below(tw, tc, FREEZE_SEA) * sea
        qm = _mouth_discharge(net, land, q)
        depth = hop_max(net, np.where(sea, -ez, 0.0), net.hops(DEPTH_REACH_KM))
        hcls, shelter = harbours(net, depth, land, ice_m, qm, full[near], reach, near)
        out["harbour"] = hcls.reshape(ny, nx)
        tab["harbour"] = {"cls": hcls, "shelter": shelter, "fetch_km": full, "ice_months": ice_m, "q_mouth": qm, "depth": depth,
                          "reach_km": reach}
    if "receiver" in L:
        ps = passes(net, ez, land, tw, tc, precip)
        pc, ph = np.zeros(net.n, np.uint8), np.zeros(net.n)
        for p in ps:
            pc[p["node"]] = pass_class(p["open_months"])
            ph[p["node"]] = p["height"]
        out["pass"], out["pass_height"] = pc.reshape(ny, nx), np.round(ph).astype(int).reshape(ny, nx)
        tab["passes"] = ps
    if "soil_fertility" in L:
        pet = holdridge_pet(tw, tc)
        arid_zone = precip < pet
        moist = np.clip(precip / np.maximum(pet, 1.0), 0, 1)
        rd = np.asarray(L.get("river_dist", np.full(net.n, 255)), float).ravel() * res_km
        irrigated = land & (rd <= max(2 * res_km, 2.0)) & arid_zone
        moist = np.where(irrigated, np.maximum(moist, 0.8), moist)
        grow = 12 - months_below(tw, tc, GROW_C)
        g = lambda k, d=0.0: np.asarray(L.get(k, np.full_like(el, d)), float).ravel()
        sl = np.degrees(np.arctan(np.hypot(*np.gradient(el, res_km * 1000.0)))).ravel()
        score, fc = fertile(g("soil_fertility"), g("soil_depth"), moist, grow, sl, land, ice, g("permafrost"),
                            g("peat_depth"), 100.0 * (g("wetland") == 2))
        out["fertile"], out["fertile_score"] = fc.reshape(ny, nx), np.round(100 * score).astype(int).reshape(ny, nx)
    fresh_lake = (water == 2) & (np.asarray(L.get("lake_kind", np.ones_like(el))).ravel() != 2)
    arid = precip < ARID_MM
    river = land & ((q >= RIVER_PERENNIAL_Q["zoom"]) & (~arid | (q >= ARID_Q)))
    wet = np.asarray(L.get("wetland", np.zeros_like(el))).ravel() == 2
    supply = np.maximum(precip - holdridge_pet(tw, tc), 0)
    sp = springs(net, ez, supply, land, slope_deg_net(net, ez))
    sp &= ~river
    fcls, fkm = fresh_reach(net, river | fresh_lake | (wet & land) | sp)
    out["fresh_water"], out["fresh_km"] = fcls.reshape(ny, nx), (np.round(fkm * 10) / 10).reshape(ny, nx)
    out["spring"] = sp.astype(np.uint8).reshape(ny, nx)
    tab["springs"] = np.flatnonzero(sp)
    tab["net"] = net
    return out, tab


def falls_pixels(falls, fr, nx: int, ny: int, res_km: float) -> list[tuple[int, int]]:
    """(row, col) of a zoom's waterfalls (stats.falls: dicts with lat, lon); fr: the zoom's Frame."""
    out = []
    for f in falls:
        x, y = fr.to_plane(xyz(np.radians(np.array([f["lat"]])), np.radians(np.array([f["lon"]]))))
        c, r = int(np.floor(x[0] / res_km + nx / 2)), int(np.floor(ny / 2 - y[0] / res_km))
        if 0 <= r < ny and 0 <= c < nx:
            out.append((r, c))
    return out


def zoom_layers(L: dict, res_km: float, falls_px=()) -> dict:
    return analyse_zoom(L, res_km, falls_px)[0]


def zoom_layer_doc() -> dict:
    """zoom.LAYER_DOC entries: name -> (units, description, encoding or none)."""
    doc = {}
    for k, (dt, sc, units, desc) in LAYER_SPECS.items():
        enc = {"dtype": dt, "scale": sc} if sc != 1 else None
        doc[k] = (units, desc + " (humanuse.py)", *([enc] if enc else []))
    return doc
