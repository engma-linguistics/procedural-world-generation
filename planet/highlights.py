"""Highlights: the eye-catching places on a world, found from its layers.

    uv run python -m planet highlights <world-id>            # or: <run-id> --at <Myr>
    uv run python -m planet highlights <run-id> --at 400 --zoom 5   # also pre-make 5 zooms

Each detector looks for one kind of place (the highest peak, the longest
mountain range, a big river mouth, a fjord coast...) and returns features:

    {kind, title, blurb, lat, lon, cell, size_km, score, zoomable, stats, path?}

lat/lon/cell is where to look (a cell on the feature, near its middle);
size_km is a suggested regional-zoom extent, one of the viewer's zoom sizes;
path, when there is one, is the feature's course as [[lat, lon], ...] (a
river from its farthest source to the sea, the spine of a mountain range).
The score only orders the list: a fixed priority per kind (how much a zoom
there tends to show), lowered for second and third places of the same kind
and for weak examples. Places of the same kind closer than a few hundred km
are merged (non-maximum suppression), keeping the better one.

Definitions are deliberately physical and simple, on ~110 km cells:
- mountain range: connected high ground (above the higher of 1500 m and the
  95th percentile of land), one-cell gaps bridged; length = the longest
  shortest-path across it (its spine).
- river: downstream links from the farthest source to the sea; discharge is
  the accumulated rain (flow) at the mouth, in m^3/s.
- delta site: a big river mouth with sediment to deliver (discharge x the
  basin's mean height), onto a low coast and a shallow shelf. Whether the
  model draws a delta there is another matter, hence "delta site".
- fjord coast: ice-free coast (where the glaciers have gone) that is steep
  (mountains >= 800 m within ~2 cells of the sea), with cool summers (warmest
  month 0..12 C) and enough snow (>= 400 mm/yr) to have fed glaciers. The
  zoom doesn't carve fjords.
- Mediterranean ("wine country"): Koppen Csa/Csb land below 1500 m; hillier
  is better.
- rift: diverging plate boundary with continental land of two different
  plates within ~3 cells (a continent splitting, or a new narrow sea).
- volcanic arc: chains of the run's active volcanoes (meta "volcanoes")
  less than 600 km apart; hotspot islands: land of hotspot basalt on oceanic
  crust within 1500 km of a live hotspot.
- climate records (hottest, coldest, wettest, driest) are on ice-free land
  and dropped when they sit on a better feature.
"""

from __future__ import annotations

import hashlib
import heapq
import json
import time
from pathlib import Path

import numpy as np

from . import hydrology
from . import world as W
from .geo import R_KM
from .grid import Grid

# cached lists are recomputed whenever this file changes
VERSION = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:10]
ZOOM_SIZES = (250, 500, 1000, 2000, 4000)  # the viewer's choices
MAX_ZOOM = 2000  # suggested zooms stay detailed (4 km pixels); the viewer can go wider
SEC_PER_YR = 3.156e7

# Fixed priority per kind: how eye-catching a zoom there usually is.
PRIORITY = {
    "highest_peak": 100, "mountain_range": 95, "largest_river": 92, "longest_river": 88, "delta": 85,
    "fjords": 82, "mediterranean": 78, "volcanic_arc": 75, "hotspot_islands": 72, "rift": 70,
    "trench": 68, "lake": 66, "inland_sea": 64, "ice_sheet": 62, "desert": 60, "rainforest": 58,
    "island": 55, "archipelago": 54, "continent": 50, "hottest": 40, "coldest": 39, "wettest": 38,
    "driest": 37,
}
ROCK_SETTING = {1: "a hotspot volcano", 2: "a volcanic arc", 3: "sedimentary rock",
                4: "a collision belt", 5: "an ancient shield"}


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
class _Ctx:
    """The world plus derived things several detectors need."""

    def __init__(self, world: dict):
        self.g: Grid = world["grid"]
        self.L = world["layers"]
        self.meta = world.get("meta", {})
        g = self.g
        self.n = g.n
        self.cell_km = g.spacing * R_KM
        self.area = 4 * np.pi * R_KM**2 / g.n  # km^2 per cell (cells are near-equal)
        self.elev = self.L["elevation"].astype(float)
        self.land = self.elev > 0
        self.a, self.b = g.edges[:, 0], g.edges[:, 1]

    def dist(self, i: int, idx) -> np.ndarray:
        """Great-circle km from cell i to cells idx."""
        return np.arccos(np.clip(self.g.centers[idx] @ self.g.centers[i], -1, 1)) * R_KM

    def dilate(self, mask: np.ndarray, k: int = 1) -> np.ndarray:
        m = mask.copy()
        for _ in range(k):
            m2 = m.copy()
            m2[self.a[m[self.b]]] = True
            m2[self.b[m[self.a]]] = True
            m = m2
        return m

    def ring_max(self, v: np.ndarray, k: int = 1) -> np.ndarray:
        out = v.astype(float).copy()
        for _ in range(k):
            prev = out.copy()
            np.maximum.at(out, self.a, prev[self.b])
            np.maximum.at(out, self.b, prev[self.a])
        return out

    def ring_min(self, v: np.ndarray, k: int = 1) -> np.ndarray:
        return -self.ring_max(-v, k)

    def components(self, mask: np.ndarray, min_cells: int = 1, bridge: int = 0) -> list[np.ndarray]:
        """Connected regions of mask, largest first. bridge > 0 links regions
        separated by gaps up to that many cells (members stay inside mask)."""
        lab, k = self.g.components(self.dilate(mask, bridge) if bridge else mask)
        out = [np.flatnonzero((lab == c) & mask) for c in range(k)]
        out = [m for m in out if len(m) >= min_cells]
        out.sort(key=lambda m: (-len(m), m[0]))
        return out

    def middle(self, cells) -> int:
        """The member cell nearest the region's centroid."""
        cells = np.asarray(cells)
        c = self.g.centers[cells].mean(0)
        return int(cells[np.argmax(self.g.centers[cells] @ c)])

    def span_km(self, cells, centre: int | None = None) -> float:
        """Twice the farthest member's distance from the centre cell."""
        centre = self.middle(cells) if centre is None else centre
        return 2 * float(self.dist(centre, np.asarray(cells)).max()) + self.cell_km

    def spine(self, cells: np.ndarray, allowed: np.ndarray | None = None) -> tuple[float, list[int]]:
        """Longest shortest path across a region (double-sweep Dijkstra over
        cell links, inside `allowed`, which defaults to the region): its length
        in km and the cells along it. Endpoints are region members."""
        allowed = np.zeros(self.n, bool) if allowed is None else allowed.copy()
        allowed[cells] = True
        members = set(int(c) for c in cells)
        _, far, _ = self._dijkstra(int(cells[0]), allowed, members)
        d, far2, prev = self._dijkstra(far, allowed, members)
        path = [far2]
        while path[-1] != far:
            path.append(prev[path[-1]])
        return d, path[::-1]

    def _dijkstra(self, src: int, allowed: np.ndarray, members: set):
        g, C = self.g, self.g.centers
        dist = {src: 0.0}
        prev = {}
        heap = [(0.0, src)]
        best, far = 0.0, src
        while heap:
            d, i = heapq.heappop(heap)
            if d > dist[i]:
                continue
            if i in members and d > best:
                best, far = d, i
            for j in g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]:
                j = int(j)
                if not allowed[j]:
                    continue
                nd = d + float(np.arccos(min(1.0, C[i] @ C[j]))) * R_KM
                if nd < dist.get(j, np.inf):
                    dist[j], prev[j] = nd, i
                    heapq.heappush(heap, (nd, j))
        return best, far, prev

    def latlon(self, i: int) -> tuple[float, float]:
        return round(float(self.g.lat[i]), 2), round(float(self.g.lon[i]), 2)

    def path(self, cells: list[int], max_points: int = 60) -> list[list[float]]:
        cells = list(cells)
        if len(cells) > max_points:
            keep = np.unique(np.linspace(0, len(cells) - 1, max_points).round().astype(int))
            cells = [cells[k] for k in keep]
        return [[round(float(self.g.lat[c]), 2), round(float(self.g.lon[c]), 2)] for c in cells]

    def plates_near(self, cells, converging_only: bool = True, k: int = 2) -> list[int]:
        """Plates meeting at (converging) boundaries within k cells of the
        region, most common first; at most two."""
        if "plate" not in self.L:
            return []
        m = np.zeros(self.n, bool)
        m[np.asarray(cells)] = True
        near = self.dilate(m, k)
        if converging_only:
            near &= self.L["plate_boundary"] > 0
        ids, counts = np.unique(self.L["plate"][near], return_counts=True)
        return [int(p) for p in ids[np.argsort(-counts, kind="stable")][:2]]


def zoom_size(span_km: float) -> int:
    """The smallest viewer zoom size that fits span_km (with a margin), at
    most MAX_ZOOM: a long feature gets a detailed look at its middle."""
    for s in ZOOM_SIZES:
        if s >= min(1.15 * span_km, MAX_ZOOM):
            return s
    return MAX_ZOOM


def _feature(ctx: _Ctx, kind: str, title: str, blurb: str, cell: int, size_km: float,
             stats: dict, quality: float = 1.0, path=None, zoomable: bool = True) -> dict:
    lat, lon = ctx.latlon(cell)
    f = {"kind": kind, "title": title, "blurb": blurb, "lat": lat, "lon": lon, "cell": int(cell),
         "size_km": int(size_km), "score": round(PRIORITY[kind] * float(np.clip(quality, 0.3, 1.0)), 1),
         "zoomable": zoomable, "stats": stats}
    if path is not None:
        f["path"] = path
    return f


# number formatting for blurbs
def _n(x: float, sig: int = 2) -> str:
    """Round to `sig` significant figures, with thousands separators."""
    if x == 0:
        return "0"
    d = sig - 1 - int(np.floor(np.log10(abs(x))))
    return f"{round(x, d):,.{max(d, 0)}f}"


def _area(km2: float) -> str:
    return f"{_n(km2 / 1e6)} million km²" if km2 >= 1e6 else f"{_n(km2)} km²"


def _m(x: float) -> str:
    return f"{x:,.0f} m"


def _plates(ps: list[int]) -> str:
    return f"plates {ps[0]} and {ps[1]}" if len(ps) >= 2 else f"plate {ps[0]}" if ps else ""


# ---------------------------------------------------------------------------
# Detectors: each returns a list of features, best first
# ---------------------------------------------------------------------------
def highest_peak(ctx: _Ctx) -> list[dict]:
    i = int(np.argmax(ctx.elev))
    if ctx.elev[i] <= 0:
        return []
    L = ctx.L
    setting = ROCK_SETTING.get(int(L["rock"][i]), "") if "rock" in L else ""
    ps = ctx.plates_near([i], k=3)
    where = f"on {setting}" if setting else ""
    if len(ps) == 2:
        where += f" where {_plates(ps)} converge"
    elif ps:
        where += f" at the converging edge of plate {ps[0]}"
    elif "plate" in L:
        where += " with no active plate boundary nearby (an old range)"
    ice = float(L["ice"][i]) if "ice" in L else 0.0
    blurb = (f"The top of the world, {where}" if where else "The top of the world") + \
        (f", under ~{ice:.0f} m of ice" if ice > 0 else "") + "."
    return [_feature(ctx, "highest_peak", f"Highest peak: {_m(ctx.elev[i])}", blurb, i, 500,
                     {"elevation_m": int(ctx.elev[i]), "plates": ps, "ice_m": round(ice)},
                     quality=0.7 + 0.3 * min(ctx.elev[i] / 6000, 1))]


def deepest_trench(ctx: _Ctx) -> list[dict]:
    i = int(np.argmin(ctx.elev))
    if ctx.elev[i] >= 0:
        return []
    ps = ctx.plates_near([i], k=3)
    if ps:
        blurb = f"A trench where {_plates(ps)} converge and one dives under the other."
    else:
        blurb = "The deepest ocean floor, away from any trench."
    return [_feature(ctx, "trench", f"Deepest ocean: {_m(ctx.elev[i])}", blurb, i, 1000,
                     {"elevation_m": int(ctx.elev[i]), "plates": ps},
                     quality=0.7 + 0.3 * min(-ctx.elev[i] / 10000, 1))]


def mountain_ranges(ctx: _Ctx, top: int = 3) -> list[dict]:
    if not ctx.land.any():
        return []
    thr = max(1500.0, float(np.quantile(ctx.elev[ctx.land], 0.95)))
    high = ctx.land & (ctx.elev >= thr)
    out = []
    bridge = ctx.dilate(high) & ctx.land  # ranges stay ranges across a low pass one cell wide
    for cells in ctx.components(high, min_cells=3, bridge=1)[:12]:
        length, spine = ctx.spine(cells, bridge)
        length += ctx.cell_km  # a cell's width at each end
        out.append((length, cells, spine))
    out.sort(key=lambda x: -x[0])
    feats = []
    for rank, (length, cells, spine) in enumerate(out[:top]):
        peak = int(cells[np.argmax(ctx.elev[cells])])
        mid = spine[len(spine) // 2]
        L = ctx.L
        volcanic = "rock" in L and np.mean(L["rock"][cells] == 2) >= 0.4
        ps = ctx.plates_near(cells)
        if len(ps) == 2:
            ctxt = f"{'a volcanic arc ' if volcanic else ''}rising where {_plates(ps)} converge"
        elif ps:
            ctxt = f"{'a volcanic arc ' if volcanic else ''}along the converging edge of plate {ps[0]}"
        else:
            ctxt = "an old range, with no active plate boundary nearby"
        iced = float(np.mean(L["ice"][cells] > 0)) if "ice" in L else 0.0
        title = ("Longest mountain range" if rank == 0 else "Mountain range") + f": {_n(length)} km"
        blurb = f"High ground above {_m(thr)}, peaks to {_m(ctx.elev[peak])}; {ctxt}." + \
            (" Mostly buried under an ice sheet." if iced > 0.5 else "")
        f = _feature(ctx, "mountain_range", title, blurb, mid, zoom_size(length),
                     {"length_km": round(length), "peak_m": int(ctx.elev[peak]), "threshold_m": round(thr),
                      "cells": len(cells), "plates": ps, "peak_cell": peak},
                     quality=(0.8 ** rank) * (0.6 + 0.4 * min(length / 3000, 1)) * (1 - 0.4 * iced),
                     path=ctx.path(spine))
        feats.append(f)
    return feats


def _rivers(ctx: _Ctx) -> dict:
    """Mouths, the outlet of every land cell, distance to the mouth along
    downstream links (km), and discharge (m^3/s)."""
    if getattr(ctx, "_riv", None):
        return ctx._riv
    L, g = ctx.L, ctx.g
    down = L["downstream"].astype(int)
    land = ctx.land
    has = (down >= 0) & land
    link = np.zeros(ctx.n)
    idx = np.flatnonzero(has)
    link[idx] = np.arccos(np.clip((g.centers[idx] * g.centers[down[idx]]).sum(1), -1, 1)) * R_KM
    mouth = has & ~land[np.maximum(down, 0)]
    # distance to the sea and the outlet, by relaxing along the links
    flows_on = has & ~mouth
    dist = np.where(has, link, 0.0)
    outlet = np.where(flows_on, np.maximum(down, 0), np.arange(ctx.n))
    for _ in range(ctx.n):
        nd = np.where(flows_on, link + dist[np.maximum(down, 0)], dist)
        no = np.where(flows_on, outlet[outlet], outlet)
        if np.array_equal(nd, dist) and np.array_equal(no, outlet):
            break
        dist, outlet = nd, no
    # sources whose water runs under an ice sheet somewhere on the way don't count as rivers
    iced = land & (L["ice"] > 0) if "ice" in L else np.zeros(ctx.n, bool)
    for _ in range(ctx.n):
        ni = iced | (flows_on & iced[np.maximum(down, 0)])
        if np.array_equal(ni, iced):
            break
        iced = ni
    q = L["flow"].astype(float) * ctx.area * 1e6 / SEC_PER_YR  # cells x m/yr -> m^3/s
    ctx._riv = {"down": down, "mouth": mouth, "dist": dist, "outlet": outlet, "q": q, "iced": iced}
    return ctx._riv


def _river_course(ctx: _Ctx, mouth: int) -> tuple[float, list[int]]:
    """Length (km) and course, farthest source -> mouth, of the river at mouth."""
    R = _rivers(ctx)
    basin = np.flatnonzero((R["outlet"] == mouth) & ctx.land)
    free = basin[~R["iced"][basin]]
    basin = free if len(free) else basin
    src = int(basin[np.argmax(R["dist"][basin])])
    course = [src]
    while course[-1] != mouth and R["down"][course[-1]] >= 0 and len(course) < ctx.n:
        course.append(int(R["down"][course[-1]]))
    return float(R["dist"][src]) + 0.5 * ctx.cell_km, course


def _basin_cells(ctx: _Ctx, mouth: int) -> np.ndarray:
    R = _rivers(ctx)
    return np.flatnonzero((R["outlet"] == mouth) & ctx.land)


def rivers(ctx: _Ctx) -> list[dict]:
    """The largest river (by discharge, pointing at its mouth) and the
    longest (pointing at its middle), merged if they're the same river."""
    if "flow" not in ctx.L or not ctx.land.any():
        return []
    R = _rivers(ctx)
    mouths = np.flatnonzero(R["mouth"])
    if not len(mouths):
        return []
    big = int(mouths[np.argmax(R["q"][mouths])])
    # longest: the mouth whose basin holds the farthest source
    land = np.flatnonzero(ctx.land & ~R["iced"])
    if not len(land):
        return []
    far = int(land[np.argmax(R["dist"][land])])
    long_mouth = int(R["outlet"][far])
    feats = []
    for kind, m in (("largest_river", big), ("longest_river", long_mouth)):
        if kind == "longest_river" and m == big:
            feats[0]["title"] = "Largest and longest river"
            continue
        length, course = _river_course(ctx, m)
        basin = _basin_cells(ctx, m)
        q = float(R["q"][m])
        stats = {"discharge_m3s": round(q), "length_km": round(length), "basin_km2": round(len(basin) * ctx.area),
                 "mouth_lat": ctx.latlon(m)[0], "mouth_lon": ctx.latlon(m)[1]}
        if kind == "largest_river":
            d = delta_score(ctx, m)
            site = " Low coast and shallow shelf at the mouth: a likely delta site." if d["delta_like"] else ""
            blurb = (f"{_n(q)} m³/s reaches the sea here, from a {_area(len(basin) * ctx.area)} basin; "
                     f"{_n(length)} km from its farthest source.{site}")
            d.pop("delta_score")
            feats.append(_feature(ctx, kind, "Largest river (its mouth)", blurb, m, 1000, {**stats, **d},
                                  path=ctx.path(course)))
        else:
            mid = course[len(course) // 2]
            blurb = f"From its farthest source to the sea; {_n(q)} m³/s at the mouth. This is its middle course."
            feats.append(_feature(ctx, kind, f"Longest river: {_n(length)} km", blurb, mid,
                                  zoom_size(ctx.span_km(course, mid)), stats, path=ctx.path(course)))
    return feats


def delta_score(ctx: _Ctx, m: int) -> dict:
    """How delta-prone a river mouth is: sediment supply (discharge x the
    basin's mean height), a low coast, a shallow shelf offshore."""
    R = _rivers(ctx)
    basin = _basin_cells(ctx, m)
    relief = float(ctx.elev[basin].mean()) if len(basin) else 0.0
    sea = int(R["down"][m])
    shelf = float(-ctx.elev[sea])  # water depth just offshore, m
    nb = ctx.g.nbr_idx[ctx.g.nbr_off[m]:ctx.g.nbr_off[m + 1]]
    coast_h = float(np.mean(ctx.elev[[m, *[j for j in nb if ctx.land[j]]]]))
    supply = float(R["q"][m]) * max(relief, 100.0) / 1000.0
    flat = float(np.clip(1.5 - coast_h / 400.0, 0.2, 1.0))
    shallow = float(np.clip(1.5 - shelf / 400.0, 0.2, 1.0))
    return {"sediment_index": round(supply), "basin_mean_m": round(relief), "shelf_depth_m": round(shelf),
            "coast_m": round(coast_h), "delta_like": bool(coast_h < 300 and shelf < 300),
            "delta_score": supply * flat * shallow}


def deltas(ctx: _Ctx, top: int = 3) -> list[dict]:
    """Big river mouths likely to build deltas (except the largest river's,
    which that feature already covers)."""
    if "flow" not in ctx.L or not ctx.land.any():
        return []
    R = _rivers(ctx)
    mouths = np.flatnonzero(R["mouth"])
    if len(mouths) < 2:
        return []
    biggest = int(mouths[np.argmax(R["q"][mouths])])
    cand = mouths[np.argsort(-R["q"][mouths])][:40]
    # the largest river's mouth (and its neighbours) are that feature's
    cand = [int(m) for m in cand if ctx.dist(biggest, [m])[0] > 500]
    scored = [(delta_score(ctx, m), m) for m in cand]
    scored = [s for s in scored if s[0]["delta_like"] and R["q"][s[1]] > 2000]
    scored.sort(key=lambda s: -s[0]["delta_score"])
    best = scored[0][0]["delta_score"] if scored else 1.0
    feats = []
    for d, m in scored:
        q = float(R["q"][m])
        length, course = _river_course(ctx, m)
        shelf = "a very shallow shelf" if d["shelf_depth_m"] < 50 else f"a {_m(d['shelf_depth_m'])}-deep shelf"
        blurb = (f"{_n(q)} m³/s from a {_n(length)} km river meets a low coast (~{_m(d['coast_m'])}) and "
                 f"{shelf}: where a delta could build.")
        feats.append(_feature(ctx, "delta", "River mouth / delta site", blurb, m, 500,
                              {"discharge_m3s": round(q), "length_km": round(length),
                               **{k: v for k, v in d.items() if k != "delta_score"}},
                              quality=(0.4 + 0.6 * d["delta_score"] / best) * min(1, (q / 50000) ** 0.5),
                              path=ctx.path(course[-12:])))
    return _nms(ctx, feats, 500)[:top]


def lakes(ctx: _Ctx) -> list[dict]:
    if "lake" not in ctx.L or not ctx.L["lake"].any():
        return []
    filled, _, _ = hydrology.priority_flood(ctx.g, ctx.elev)
    regions = ctx.components(ctx.L["lake"] > 0, min_cells=2)
    if not regions:
        return []
    cells = regions[0]
    mid = ctx.middle(cells)
    level = float(filled[cells].max())
    depth = float((filled[cells] - ctx.elev[cells]).max())
    a = len(cells) * ctx.area
    blurb = f"Surface at {_m(level)} above sea level, up to ~{_m(depth)} deep."
    return [_feature(ctx, "lake", f"Biggest lake: {_area(a)}", blurb, mid, zoom_size(ctx.span_km(cells, mid)),
                     {"area_km2": round(a), "surface_m": round(level), "max_depth_m": round(depth)})]


def inland_seas(ctx: _Ctx) -> list[dict]:
    """Water below sea level that isn't connected to the world ocean
    (like the Caspian)."""
    regions = ctx.components(~ctx.land, min_cells=3)
    if len(regions) < 2:
        return []
    cells = regions[1]  # [0] is the world ocean
    mid = ctx.middle(cells)
    a = len(cells) * ctx.area
    floor = float(ctx.elev[cells].min())
    blurb = f"Sea cut off from the ocean (like the Caspian), its floor down to {_m(floor)}."
    return [_feature(ctx, "inland_sea", f"Landlocked sea: {_area(a)}", blurb, mid,
                     zoom_size(ctx.span_km(cells, mid)), {"area_km2": round(a), "floor_m": round(floor)},
                     quality=0.6 + 0.4 * min(a / 3e5, 1))]


def _largest_region(ctx: _Ctx, mask: np.ndarray, min_cells: int = 3):
    regions = ctx.components(mask, min_cells=min_cells)
    return regions[0] if regions else None


def desert(ctx: _Ctx) -> list[dict]:
    if "climate" not in ctx.L:
        return []
    k = ctx.L["climate"]
    cells = _largest_region(ctx, ctx.land & ((k == 3) | (k == 4)))
    if cells is None:
        return []
    mid = ctx.middle(cells)
    a = len(cells) * ctx.area
    hot = (k[cells] == 3).mean() >= 0.5
    rain = float(ctx.L["precipitation"][cells].mean())
    t_warm = float(ctx.L["warm_month"][cells].mean())
    blurb = (f"{'Hot desert (BWh)' if hot else 'Desert with cold winters (BWk)'}: ~{rain:.0f} mm of rain a year, "
             f"warmest month ~{t_warm:.0f} °C.")
    return [_feature(ctx, "desert", f"Largest desert: {_area(a)}", blurb, mid,
                     zoom_size(ctx.span_km(cells, mid)),
                     {"area_km2": round(a), "hot": bool(hot), "rain_mm": round(rain)},
                     quality=0.6 + 0.4 * min(a / 3e6, 1))]


def rainforest(ctx: _Ctx) -> list[dict]:
    if "climate" not in ctx.L:
        return []
    cells = _largest_region(ctx, ctx.land & (ctx.L["climate"] == 0))
    if cells is None:
        return []
    mid = ctx.middle(cells)
    a = len(cells) * ctx.area
    rain = float(ctx.L["precipitation"][cells].mean())
    blurb = f"Hot and wet all year (Köppen Af), ~{_n(rain)} mm of rain a year."
    return [_feature(ctx, "rainforest", f"Largest rainforest: {_area(a)}", blurb, mid,
                     zoom_size(ctx.span_km(cells, mid)), {"area_km2": round(a), "rain_mm": round(rain)},
                     quality=0.6 + 0.4 * min(a / 3e6, 1))]


def ice_sheet(ctx: _Ctx) -> list[dict]:
    if "ice" not in ctx.L:
        return []
    ice = ctx.L["ice"]
    cells = _largest_region(ctx, ctx.land & (ice > 50), min_cells=2)
    if cells is None:
        return []
    mid = ctx.middle(cells)
    a = len(cells) * ctx.area
    big = a > 1e6
    coast = ctx.dilate(~ctx.land)[cells].any()
    blurb = f"Land ice up to ~{_m(ice[cells].max())} thick" + (", reaching the sea." if coast else ".")
    return [_feature(ctx, "ice_sheet", ("Ice sheet" if big else "Ice cap") + f": {_area(a)}", blurb, mid,
                     zoom_size(ctx.span_km(cells, mid)),
                     {"area_km2": round(a), "max_thickness_m": round(float(ice[cells].max()))},
                     quality=0.6 + 0.4 * min(a / 2e6, 1))]


def mediterranean(ctx: _Ctx, top: int = 2) -> list[dict]:
    """Csa/Csb (hot or warm dry summers, mild wet winters) on hilly but
    not alpine land: where wine country would be."""
    if "climate" not in ctx.L:
        return []
    k = ctx.L["climate"]
    relief = ctx.ring_max(ctx.elev) - ctx.ring_min(np.where(ctx.land, ctx.elev, 0.0))
    ok = ctx.land & ((k == 7) | (k == 8)) & (ctx.elev < 1500)
    regions = ctx.components(ok, min_cells=2, bridge=1)
    feats = []
    for rank, cells in enumerate(regions[:top]):
        mid = ctx.middle(cells)
        a = len(cells) * ctx.area
        L = ctx.L
        hilly = float(np.mean((relief[cells] > 150) & (relief[cells] < 2000)))
        blurb = (f"Mediterranean climate, like wine country: {_area(a)} of dry summers (~{L['warm_month'][cells].mean():.0f} °C) "
                 f"and wet winters (~{L['cold_month'][cells].mean():.0f} °C), {_n(L['precipitation'][cells].mean())} mm a year; "
                 f"{100 * hilly:.0f}% of it hilly.")
        feats.append(_feature(ctx, "mediterranean", "Wine country", blurb, mid,
                              zoom_size(ctx.span_km(cells, mid)),
                              {"area_km2": round(a), "hilly_pct": round(100 * hilly)},
                              quality=(0.8 ** rank) * (0.5 + 0.3 * min(a / 2e5, 1) + 0.2 * hilly)))
    return feats


def fjords(ctx: _Ctx, top: int = 2) -> list[dict]:
    L = ctx.L
    if "warm_month" not in L:
        return []
    sea = ~ctx.land
    coast = ctx.land & ctx.dilate(sea)
    high = ctx.ring_max(np.where(ctx.land, ctx.elev, 0.0), 2)
    ice = L["ice"] if "ice" in L else np.zeros(ctx.n)
    # cool summers at the coast itself: glaciers reached the sea (now or in colder times)
    cold = ((L["warm_month"] < 12) & (L["warm_month"] > 0)) | (ice > 0)
    snowy = (L["precipitation"] >= 400) | (ice > 0)
    # the sea next to it should be more than a sliver of lake-like water: part of a real ocean
    ocean = np.zeros(ctx.n, bool)
    regions = ctx.components(sea)
    if regions:
        ocean[regions[0]] = True
    # ice-free coast: fjords show where the glaciers have gone (under an ice sheet they're hidden)
    mask = coast & (ice <= 0) & cold & snowy & (high >= 800) & ctx.dilate(ocean)
    glaciers = ctx.dilate(ice > 0, 2)
    regs = ctx.components(mask, min_cells=3, bridge=1)
    feats = []
    for cells in regs[:8]:
        length, spine = ctx.spine(cells, ctx.dilate(mask) & ctx.land)
        length += ctx.cell_km
        relief = float(high[cells].mean())
        icefrac = float(np.mean(glaciers[cells]))
        mid = int(cells[np.argmax(high[cells])])  # look where it's steepest
        s = min(length, 3000) * min(relief / 1500, 1.3)
        feats.append((s, length, cells, spine, mid, relief, icefrac))
    feats.sort(key=lambda x: -x[0])
    out = []
    best = feats[0][0] if feats else 1
    for rank, (s, length, cells, spine, mid, relief, icefrac) in enumerate(feats[:top]):
        summer = float(L["warm_month"][cells].mean())
        ice_txt = "; glaciers still on the mountains above it" if icefrac > 0.5 else \
            "; some glaciers left on the mountains" if icefrac > 0.1 else ""
        blurb = (f"{_n(length)} km of steep, cold coast: mountains of ~{_m(relief)} within ~200 km of the sea, "
                 f"summers ~{summer:.0f} °C{ice_txt}. Glacier-carved fjord country (the zoom doesn't carve the fjords themselves).")
        out.append(_feature(ctx, "fjords", "Fjord coast", blurb, mid, 1000,
                            {"length_km": round(length), "mean_relief_m": round(relief), "summer_c": round(summer, 1),
                             "ice_pct": round(100 * icefrac)},
                            quality=(0.85 ** rank) * (0.5 + 0.5 * s / best) * min(1, length / 500 + 0.4),
                            path=ctx.path(spine)))
    return out


def _chains(ctx: _Ctx, pts: list, link_km: float) -> list[list[int]]:
    """Single-linkage clusters of (lat, lon) points, biggest first."""
    if not pts:
        return []
    la, lo = np.radians(np.array(pts, float)).T
    v = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
    d = np.arccos(np.clip(v @ v.T, -1, 1)) * R_KM
    lab = np.arange(len(pts))
    changed = True
    while changed:
        new = np.where(d <= link_km, lab[None, :], len(pts)).min(1)
        changed = not np.array_equal(new, lab)
        lab = new[new] if changed else lab
    groups = [list(np.flatnonzero(lab == k)) for k in np.unique(lab)]
    groups.sort(key=lambda gr: -len(gr))
    return groups


def volcanic_arcs(ctx: _Ctx, top: int = 2) -> list[dict]:
    vols = ctx.meta.get("volcanoes") or []
    if len(vols) < 3:
        return []
    cells = ctx.g.locate(np.array([_unit(la, lo) for la, lo in vols]))
    feats = []
    for rank, gr in enumerate(_chains(ctx, vols, 600.0)[:top]):
        if len(gr) < 3:
            break
        cs = cells[gr]
        length = _extent(ctx, cs)
        on_land = ctx.land[cs].mean()
        continental = ("crust" in ctx.L) and ctx.L["crust"][cs].mean() > 0.5
        kind_txt = "a continental arc (like the Andes)" if continental and on_land > 0.5 else \
            "an island arc (like Japan or the Aleutians)" if on_land > 0 else "an underwater arc"
        mid = ctx.middle(cs)
        ps = ctx.plates_near(cs, k=3)
        blurb = (f"{len(gr)} active volcanoes in a {_n(length)} km chain: {kind_txt}"
                 + (f" where {_plates(ps)} converge." if len(ps) == 2 else "."))
        feats.append(_feature(ctx, "volcanic_arc", "Volcanic arc", blurb, mid, zoom_size(length),
                              {"volcanoes": len(gr), "length_km": round(length), "on_land_pct": round(100 * on_land),
                               "plates": ps},
                              quality=(0.8 ** rank) * (0.5 + 0.5 * min(len(gr) / 8, 1))))
    return feats


def _unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return [np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def _extent(ctx: _Ctx, cells) -> float:
    """km between the two farthest-apart cells, plus a cell."""
    C = ctx.g.centers[np.asarray(cells)]
    return float(np.arccos(np.clip(C @ C.T, -1, 1)).max()) * R_KM + ctx.cell_km


def hotspot_islands(ctx: _Ctx, top: int = 2) -> list[dict]:
    """Volcanic islands of hotspot basalt on oceanic crust, near a live hotspot."""
    L = ctx.L
    hs = ctx.meta.get("hotspots") or []
    if "rock" not in L or not hs:
        return []
    isl = ctx.land & (L["rock"] == 1) & (L["crust"] == 0)
    hcells = ctx.g.locate(np.array([_unit(la, lo) for la, lo in hs]))
    feats = []
    for cells in ctx.components(isl, min_cells=1, bridge=3):
        near = min(float(ctx.dist(h, cells).min()) for h in hcells)
        if near > 1500:
            continue
        n_islands = len(ctx.components(np.isin(np.arange(ctx.n), cells)))
        length = _extent(ctx, cells)
        peak = int(cells[np.argmax(ctx.elev[cells])])
        feats.append((n_islands + len(cells) / 4, cells, n_islands, length, peak))
    feats.sort(key=lambda x: -x[0])
    out = []
    for rank, (s, cells, n_islands, length, peak) in enumerate(feats[:top]):
        if n_islands > 1:
            blurb = (f"{n_islands} volcanic islands over a mantle plume, like Hawaii, in a {_n(length)} km chain; "
                     f"highest {_m(ctx.elev[peak])}.")
        else:
            blurb = (f"A volcanic island ~{_n(length)} km across over a mantle plume, like Iceland or Hawaii; "
                     f"highest {_m(ctx.elev[peak])}.")
        out.append(_feature(ctx, "hotspot_islands", "Hotspot islands" if n_islands > 1 else "Hotspot island", blurb, peak, zoom_size(length),
                            {"islands": n_islands, "length_km": round(length), "peak_m": int(ctx.elev[peak])},
                            quality=(0.8 ** rank) * (0.5 + 0.5 * min(s / 6, 1))))
    return out


def rifts(ctx: _Ctx, top: int = 2) -> list[dict]:
    """Continents splitting: diverging boundaries with continental land on
    both sides (of two different plates) within ~3 cells."""
    L = ctx.L
    if "plate_boundary" not in L:
        return []
    div = L["plate_boundary"] < 0
    cont_land = (L["crust"] > 0) & ctx.land
    near = ctx.dilate(div, 3)
    sides = np.zeros(ctx.n, int)  # how many plates have continental land near each cell
    for p in np.unique(L["plate"][near & cont_land]):
        sides += ctx.dilate(cont_land & (L["plate"] == p), 3)
    mask = div & (sides >= 2)
    feats = []
    for rank, cells in enumerate(ctx.components(mask, min_cells=4, bridge=1)[:top]):
        length, spine = ctx.spine(cells, ctx.dilate(mask))
        length += ctx.cell_km
        land_frac = float(ctx.land[cells].mean())
        mid = spine[len(spine) // 2]
        ps = ctx.plates_near(cells, converging_only=False, k=1)
        if land_frac >= 0.5:
            title, what = "Rift valley", "a continent pulling apart on land (like East Africa)"
        else:
            title, what = "Young rift sea", "a new ocean opening between continents (like the Red Sea)"
        blurb = f"{_n(length)} km of {what}" + (f", between {_plates(ps)}." if len(ps) == 2 else ".")
        feats.append(_feature(ctx, "rift", title, blurb, mid, zoom_size(length),
                              {"length_km": round(length), "land_pct": round(100 * land_frac), "plates": ps},
                              quality=(0.8 ** rank) * (0.5 + 0.5 * min(length / 1500, 1)), path=ctx.path(spine)))
    return feats


ISLAND_MAX_KM2 = 3.5e6  # bigger landmasses are continents (Greenland 2.2, Australia 7.7 million km^2)


def landmasses(ctx: _Ctx) -> list[dict]:
    masses = ctx.components(ctx.land)
    if not masses:
        return []
    feats = []
    big = masses[0]
    a = len(big) * ctx.area
    mid = ctx.middle(big)
    pct = 100 * len(big) / max(ctx.land.sum(), 1)
    feats.append(_feature(ctx, "continent", f"Largest continent: {_area(a)}",
                          f"{pct:.0f}% of all land; highest point {_m(ctx.elev[big].max())}.", mid,
                          4000, {"area_km2": round(a), "pct_of_land": round(pct)}, zoomable=False))
    islands = [m for m in masses if len(m) * ctx.area < ISLAND_MAX_KM2]
    if islands and len(islands[0]) >= 3:
        isl = islands[0]
        a = len(isl) * ctx.area
        mid = ctx.middle(isl)
        bigger = np.concatenate([m for m in masses if len(m) > len(isl)])
        off = float(ctx.dist(mid, bigger).min())
        feats.append(_feature(ctx, "island", f"Largest island: {_area(a)}",
                              f"Highest point {_m(ctx.elev[isl].max())}; its middle is {_n(off)} km from the "
                              f"nearest bigger landmass.", mid,
                              zoom_size(ctx.span_km(isl, mid)), {"area_km2": round(a)},
                              quality=0.6 + 0.4 * min(a / 1e6, 1)))
    # archipelago: the most small islands (<= 5 cells) within a few hundred km of each other
    small = [m for m in masses if len(m) <= 5]
    if len(small) >= 4:
        pts = [ctx.latlon(ctx.middle(m)) for m in small]
        groups = _chains(ctx, pts, 450.0)
        if groups and len(groups[0]) >= 4:
            cells = np.concatenate([small[k] for k in groups[0]])
            mid = ctx.middle(cells)
            span = ctx.span_km(cells, mid)
            feats.append(_feature(ctx, "archipelago", f"Archipelago: {len(groups[0])} islands",
                                  f"{len(groups[0])} islands strung across ~{_n(span)} km of sea.", mid,
                                  zoom_size(span), {"islands": len(groups[0]), "span_km": round(span)},
                                  quality=0.6 + 0.4 * min(len(groups[0]) / 10, 1)))
    return feats


def extremes(ctx: _Ctx) -> list[dict]:
    """Climate records on ice-free land."""
    L = ctx.L
    if "warm_month" not in L or not ctx.land.any():
        return []
    ok = ctx.land & ((L["ice"] <= 0) if "ice" in L else True) & (L["lake"] == 0)
    if not ok.any():
        return []
    idx = np.flatnonzero(ok)
    feats = []
    i = int(idx[np.argmax(L["warm_month"][idx])])
    feats.append(_feature(ctx, "hottest", "Hottest summers",
                          f"Warmest month ~{L['warm_month'][i]:.0f} °C (yearly mean {L['temperature'][i]:.0f} °C).",
                          i, 500, {"warm_month_c": round(float(L["warm_month"][i]), 1)}))
    i = int(idx[np.argmin(L["cold_month"][idx])])
    feats.append(_feature(ctx, "coldest", "Coldest winters (ice-free land)",
                          f"Coldest month ~{L['cold_month'][i]:.0f} °C (yearly mean {L['temperature'][i]:.0f} °C).",
                          i, 500, {"cold_month_c": round(float(L["cold_month"][i]), 1)}))
    i = int(idx[np.argmax(L["precipitation"][idx])])
    feats.append(_feature(ctx, "wettest", "Wettest place",
                          f"{_n(L['precipitation'][i])} mm of rain a year.", i, 500,
                          {"rain_mm": int(L["precipitation"][i])}))
    i = int(idx[np.argmin(L["precipitation"][idx])])
    feats.append(_feature(ctx, "driest", "Driest place",
                          f"{L['precipitation'][i]:.0f} mm of rain a year.", i, 500,
                          {"rain_mm": int(L["precipitation"][i])}))
    return feats


DETECTORS = [highest_peak, mountain_ranges, rivers, deltas, deepest_trench, fjords, mediterranean,
             volcanic_arcs, hotspot_islands, rifts, lakes, inland_seas, ice_sheet, desert, rainforest,
             landmasses, extremes]


def _nms(ctx: _Ctx, feats: list[dict], radius_km: float) -> list[dict]:
    """Drop features within radius_km of a better one already kept."""
    kept = []
    for f in sorted(feats, key=lambda f: -f["score"]):
        if all(ctx.dist(k["cell"], [f["cell"]])[0] > radius_km for k in kept):
            kept.append(f)
    return kept


def find(world: dict) -> list[dict]:
    """All highlights of a world (W.finish / W.load shape), best first."""
    ctx = _Ctx(world)
    feats = []
    for det in DETECTORS:
        feats += det(ctx)
    # same-kind duplicates were handled per detector; the climate records
    # are dropped when they sit on top of a better feature (driest place
    # in the middle of the largest desert, say)
    records = [f for f in feats if f["kind"] in ("hottest", "coldest", "wettest", "driest")]
    rest = [f for f in feats if f not in records]
    for f in records:
        if all(ctx.dist(k["cell"], [f["cell"]])[0] > 400 for k in rest):
            rest.append(f)
    rest.sort(key=lambda f: -f["score"])
    for k, f in enumerate(rest):
        f["rank"] = k + 1
    return rest


# ---------------------------------------------------------------------------
# Cache: worlds/highlights/<world id>.json
# ---------------------------------------------------------------------------
def cache_path(world_path: Path) -> Path:
    return W.WORLDS / "highlights" / f"{world_path.stem}.json"


def cached(world_path: Path) -> dict | None:
    p = cache_path(world_path)
    try:
        d = json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    return d if d.get("version") == VERSION else None


def for_world(world_path: Path, refresh: bool = False) -> dict:
    """Highlights of a saved world, computed once and cached."""
    world_path = Path(world_path)
    if not refresh and (d := cached(world_path)):
        return d
    t0 = time.time()
    world = W.load(world_path)
    feats = find(world)
    m = world["meta"]
    d = {"version": VERSION, "world": world_path.stem, "name": world.get("name"),
         "source_run": m.get("source_run"), "t_myr": m.get("t_myr"), "level": m.get("level"),
         "computed_in_s": round(time.time() - t0, 2), "features": feats}
    cache_path(world_path).parent.mkdir(parents=True, exist_ok=True)
    cache_path(world_path).write_text(json.dumps(d, default=W._np, separators=(",", ":")))
    return d


def pick_zooms(features: list[dict], n: int) -> list[dict]:
    """The top n zoomable features, skipping any whose centre falls inside
    the square of one already picked (they'd show the same region)."""
    out = []
    for f in features:
        if len(out) >= n:
            break
        if not f.get("zoomable", True):
            continue
        v = np.array(_unit(f["lat"], f["lon"]))
        if any(np.arccos(np.clip(v @ np.array(_unit(o["lat"], o["lon"])), -1, 1)) * R_KM < 0.4 * o["size_km"]
               for o in out):
            continue
        out.append(f)
    return out
