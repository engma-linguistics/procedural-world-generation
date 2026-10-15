"""Highlights: the eye-catching places on a world, found from its layers.

    uv run python -m planet highlights <world-id>            # or: <run-id> --at <Myr>
    uv run python -m planet highlights <run-id> --at 400 --zoom 5   # also pre-make 5 zooms
    uv run python -m planet highlights <run-id> --at auto           # a representative moment

Each detector looks for one kind of place (the highest peak, the longest
mountain range, a big river mouth, a fjord coast...) and returns features:

    {kind, category, title, blurb, lat, lon, cell, size_km, score, zoomable, stats, path?}

category groups the kinds for the viewer (CATEGORIES: landscape, water,
climate, travel, geology, vegetation).

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
  model draws a delta there is another matter, hence "delta site". When the
  world has wave_power and tide_range layers, the blurb says which kind of
  delta it would be (coast.delta_at: Galloway's river / wave / tide weights).
- fjord coast: ice-free coast (where the glaciers have gone) that is steep
  (mountains >= 800 m within ~2 cells of the sea), with cool summers (warmest
  month 0..12 C) and enough snow (>= 400 mm/yr) to have fed glaciers. The
  zoom doesn't carve fjords.
- Mediterranean ("wine country"): Koppen Csa/Csb land below 1500 m with a
  warmest month <= 30 C (a hothouse Cs at 40 C is correct but no vineyard);
  hillier is better.
- rift: diverging plate boundary with continental land of two different
  plates within ~3 cells (a continent splitting, or a new narrow sea).
- volcanic arc: chains of the run's active arc volcanoes (meta "volcanoes")
  less than 600 km apart. Hotspot island chain: from the same volcano table,
  a plume's vents on the sea floor linked when within CHAIN_LINK_KM and
  CHAIN_LINK_MYR of each other, ranked by how many islands, atolls and guyots
  they show (zoom_volcanoes.form), zoomed where most islands and atolls are;
  worlds without a table fall back to land of hotspot basalt on oceanic crust
  within 1500 km of a live hotspot. Atolls: the biggest group of atolls
  (hotspot or arc, within ATOLL_LINK_KM) not already shown as a chain.
- fastest plate: the big plate (>= FAST_MIN_SHARE of the planet) with the
  highest mean speed, placed on its leading edge (converging boundary it
  moves towards), saying what happens there (collision, subduction,
  overriding); none when it has no such edge.
- climate records (hottest, coldest, wettest, driest) are on ice-free land
  and dropped when they sit on a better feature.
- highest peak: under more than ICE_PEAK_M of ice it ranks lower and the
  highest ice-free summit is added as its own place. The longest river ranks
  lower when it's small or crosses mostly barren land (ice, tundra, desert).
- waterfall / steep river: the biggest drop of the water surface (a lake's
  surface on lake cells) over one or two downstream links, on rivers of at
  least WF_MIN_Q m^3/s, ranked by the power of the falling water (discharge x
  drop). On ~110 km cells that's a steep reach, not a fall; the zoom keeps
  part of it as real falls (zoom.knickpoints(): a lip, gorge and plunge
  pool, plus cascades), listed in each zoom's stats ("waterfalls").
- canyon: a river (>= 300 m^3/s) far below the median of its neighbours off
  the river, on ground averaging >= 1000 m within two cells.
- salt lake / salt flat: the biggest lake_kind 2 (closed, salty) and 3 (salt
  pan) regions; inland basin: the largest land area whose drainage ends in a
  closed lake or pit. Worlds without lake_kind have no closed basins; there,
  evaporite beds at the surface on dry land are "salt flats".
- coral coast: open sea next to land, shallow (cell mean <= 250 m), coldest
  month >= 18 C, away from big river mouths; limestone on shore is a bonus.
- rain shadow: an ice-free summit >= 1500 m with land 2-4 cells away whose rain differs
  most between the two sides of a line through it (wet >= 600 mm, dry < 600
  mm, >= 3x); ranked by the ratio (up to 10) x height.
- plateau: one piece of land >= 2000 m, ice-free, whose cells differ from
  their neighbours by < 500 m on average.
- most varied square: the 1000 km square (around a land cell) with the most
  even mix of Koppen classes and named vegetation types (biomes on worlds
  without vegetation; exp of Shannon entropy, geometric mean of the two),
  lowered when under half land.
- vegetation (worlds with the vegetation layers): rainforest is the evergreen
  tropical forest types (else Koppen Af); great forests: the two largest
  closed forests (tree cover >= 60%) of different kinds outside the
  rainforest; the great savanna; the biggest wetlands (swamp forest, flooded
  grassland, marsh, bog, fen, palsa mire); the maquis coast (Mediterranean
  vegetation along a coast; wine country stays the Koppen Cs climate, with
  its vegetation in the blurb); the treeline: alpine vegetation over forest
  >= 300 m lower along a mountain range, and the polar forest-tundra belt.
- travel (worlds with July / January layers; each hemisphere's own summer and
  winter, July being summer in the north): beach destination (coast with a
  warm, sunny summer at sea level: sunshine_jul / sunshine_jan, a warm sea: its
  summer surface temperature, sst_jul / sst_jan, where the world has them;
  moderate waves), ski country
  (ice-free mountains freezing and snowy in winter, not glaciated, a town with
  a tolerable winter below), winter-sun retreat (low land with a mild winter
  and >= 5 h of sunshine a day over the winter half-year), year-round resort (a beach and ski country within RESORT_KM). Each
  blurb starts with the numbers that make it ("July 28 °C, 40 mm of rain...").
"""

from __future__ import annotations

import hashlib
import heapq
import json
import time
from pathlib import Path

import numpy as np

from . import coast, hydrology
from . import world as W
from .climate import BIOMES, KOPPEN, LAPSE
from .geo import R_KM
from .grid import Grid
from .tectonics.volcanism import ARC as ARC_VOLCANO
from .vegetation import TYPES as VEG_TYPES

# cached lists are recomputed whenever this file changes
VERSION = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:10]
ZOOM_SIZES = (250, 500, 1000, 2000, 4000)  # the viewer's choices
MAX_ZOOM = 2000  # suggested zooms stay detailed (4 km pixels); the viewer can go wider
SEC_PER_YR = 3.156e7

# Fixed priority per kind: how eye-catching a zoom there usually is.
PRIORITY = {
    "highest_peak": 100, "mountain_range": 95, "largest_river": 92, "longest_river": 88, "delta": 85,
    "fjords": 82, "mediterranean": 78, "volcanic_arc": 75, "hotspot_islands": 72, "atolls": 69, "rift": 70,
    "trench": 68, "fastest_plate": 45, "lake": 66, "inland_sea": 64, "ice_sheet": 62, "desert": 60, "rainforest": 58,
    "island": 55, "archipelago": 54, "continent": 50, "hottest": 40, "coldest": 39, "wettest": 38,
    "driest": 37, "ice_free_peak": 99, "waterfall": 90, "canyon": 84, "varied_square": 80, "plateau": 76,
    "rain_shadow": 74, "coral_coast": 73, "salt_lake": 65, "salt_pan": 63, "salt_flats": 61, "inland_basin": 56,
    "year_round": 74, "ski": 71, "beach": 70, "mild_winter": 67,
    "wetland": 59, "great_forest": 57, "maquis_coast": 54, "savanna": 53, "treeline": 52,
}
# Category per kind, for the viewer's filter and marker colours (PW-141)
CATEGORIES = {
    "landscape": ("highest_peak", "ice_free_peak", "mountain_range", "plateau", "canyon", "fjords", "rain_shadow",
                  "varied_square", "continent", "island", "archipelago"),
    "water": ("largest_river", "longest_river", "delta", "waterfall", "lake", "inland_sea", "salt_lake", "salt_pan",
              "salt_flats", "inland_basin", "coral_coast"),
    "climate": ("desert", "rainforest", "ice_sheet", "mediterranean", "hottest", "coldest", "wettest", "driest"),
    "travel": ("beach", "ski", "mild_winter", "year_round"),
    "geology": ("volcanic_arc", "hotspot_islands", "atolls", "rift", "trench", "fastest_plate"),
    "vegetation": ("great_forest", "savanna", "wetland", "maquis_coast", "treeline"),
}
CATEGORY = {k: c for c, kinds in CATEGORIES.items() for k in kinds}
assert set(CATEGORY) == set(PRIORITY), set(CATEGORY) ^ set(PRIORITY)
ROCK_SETTING = {1: "a hotspot volcano", 2: "a volcanic arc", 3: "sedimentary rock",
                4: "a collision belt", 5: "an ancient shield"}
KOPPEN_NAME = {k[0]: f"{k[2]} ({k[1]})" for k in KOPPEN}
BIOME_NAME = {b[0]: b[1] for b in BIOMES}
BARREN = (4, 5, 7, 11, 15)  # biomes: ice sheet, tundra, cold desert, hot desert, alpine / bare rock


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
    f = {"kind": kind, "category": CATEGORY[kind], "title": title, "blurb": blurb, "lat": lat, "lon": lon,
         "cell": int(cell),
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


def _c(x: float) -> str:
    """Degrees C, whole (no "-0")."""
    return f"{int(round(float(x)))} °C"


def _plates(ps: list[int]) -> str:
    return f"plates {ps[0]} and {ps[1]}" if len(ps) >= 2 else f"plate {ps[0]}" if ps else ""


# ---------------------------------------------------------------------------
# Detectors: each returns a list of features, best first
# ---------------------------------------------------------------------------
ICE_PEAK_M = 100.0  # m of ice over the highest peak that hides it


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
    ice = np.asarray(L["ice"], float) if "ice" in L else np.zeros(ctx.n)
    blurb = (f"The top of the world, {where}" if where else "The top of the world") + \
        (f", under ~{ice[i]:.0f} m of ice" if ice[i] > 0 else "") + "."
    # a summit under an ice cap zooms to a white blank: rank it lower, and
    # add the highest ice-free summit as its own place
    buried = ice[i] > ICE_PEAK_M
    feats = [_feature(ctx, "highest_peak", f"Highest peak: {_m(ctx.elev[i])}" + (" (under ice)" if buried else ""),
                      blurb, i, 500, {"elevation_m": int(ctx.elev[i]), "plates": ps, "ice_m": round(ice[i])},
                      quality=(0.7 + 0.3 * min(ctx.elev[i] / 6000, 1)) * (0.7 if buried else 1.0))]
    free = np.flatnonzero(ctx.land & (ice <= 0))
    if buried and len(free):
        j = int(free[np.argmax(ctx.elev[free])])
        setting = ROCK_SETTING.get(int(L["rock"][j]), "") if "rock" in L else ""
        km = float(ctx.dist(i, [j])[0])
        blurb = ("The highest summit not under ice" + (f", on {setting}" if setting else "") +
                 f"; the highest peak ({_m(ctx.elev[i])}) is {_n(km)} km away under ~{_m(ice[i])} of ice.")
        feats.append(_feature(ctx, "ice_free_peak", f"Highest ice-free peak: {_m(ctx.elev[j])}", blurb, j, 500,
                              {"elevation_m": int(ctx.elev[j]), "km_from_highest": round(km)},
                              quality=0.7 + 0.3 * min(ctx.elev[j] / 6000, 1)))
    return feats


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
            gal = galloway_note(ctx, m, q) if d["delta_like"] else {}
            blurb = (f"{_n(q)} m³/s reaches the sea here, from a {_area(len(basin) * ctx.area)} basin; "
                     f"{_n(length)} km from its farthest source.{site}{gal.pop('note', '')}")
            d.pop("delta_score")
            feats.append(_feature(ctx, kind, "Largest river (its mouth)", blurb, m, 1000, {**stats, **d, **gal},
                                  path=ctx.path(course)))
        else:
            mid = course[len(course) // 2]
            blurb = f"From its farthest source to the sea; {_n(q)} m³/s at the mouth. This is its middle course."
            # a long trickle across a barren (icy, tundra, desert) land makes a bland zoom: rank it lower
            bare = 0.0
            if "biome" in ctx.L:
                b = np.asarray(ctx.L["biome"])[course]
                bare = float(np.isin(b, BARREN).mean())
                if bare > 0.5:
                    blurb += f" Most of its course is {BIOME_NAME[int(np.bincount(b).argmax())]} country: a thin river."
            feats.append(_feature(ctx, kind, f"Longest river: {_n(length)} km", blurb, mid,
                                  zoom_size(ctx.span_km(course, mid)), stats, path=ctx.path(course),
                                  quality=min(1.0, 0.45 + 0.55 * (q / 5000) ** 0.5) * (0.75 if bare > 0.5 else 1.0)))
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


GALLOWAY_LOOK = {
    "river": "long distributaries with levees reaching out to sea (a bird's foot, like the Mississippi's)",
    "wave": "a smooth arc of beach ridges with one or two mouths and lagoons behind barriers (like the Nile or Sao Francisco)",
    "tide": "funnel-shaped mouths widening to sea, elongate islands and tidal flats (like the Ganges-Brahmaputra or Mekong)",
}


def galloway_note(ctx: _Ctx, m: int, q: float) -> dict:
    """What would shape a delta at mouth m (coast.delta_at): Galloway
    weights, the dominant type and a sentence on the look; {} when the
    world has no wave/tide layers."""
    if "wave_power" not in ctx.L or "tide_range" not in ctx.L:
        return {}
    sea = int(_rivers(ctx)["down"][m])
    cover = float(np.asarray(ctx.L.get("sediment_cover", np.zeros(ctx.n)), float)[sea]) if sea >= 0 else 0.0
    sf = float(np.clip((cover - 0.5) / 7.5, 0, 1))
    sf = sf * sf * (3 - 2 * sf)
    gw = coast.delta_at(ctx.g, ctx.L, m, q, coast.plain_radius_km(q, sf))
    w = gw["weights"]
    top = max(w, key=w.get)
    note = (f" Waves {gw['wave_power_kw_m']:.0f} kW/m, tides {gw['tide_range_m']:.1f} m, river sediment "
            f"{gw['sediment_river_kgs'] * coast.SEC_PER_YR / 1e9:.0f} Mt/yr: {gw['type']} "
            f"(river {100 * w['river']:.0f}%, wave {100 * w['wave']:.0f}%, tide {100 * w['tide']:.0f}%)"
            + (f", so {GALLOWAY_LOOK[top]}." if w[top] >= coast.RIVER_DOMINANT else "."))
    return {"delta_type": gw["type"], "galloway": w, "wave_power_kw_m": gw["wave_power_kw_m"],
            "tide_range_m": gw["tide_range_m"], "note": note}


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
        gal = galloway_note(ctx, m, q)
        feats.append(_feature(ctx, "delta", "River mouth / delta site", blurb + gal.pop("note", ""), m, 500,
                              {"discharge_m3s": round(q), "length_km": round(length),
                               **{k: v for k, v in d.items() if k != "delta_score"}, **gal},
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


RAINFOREST_TYPES = (1, 2, 5, 6)  # vegetation: tropical lowland rainforest, cloud forest, swamp and peat swamp forest


def rainforest(ctx: _Ctx) -> list[dict]:
    """The largest rainforest: the evergreen tropical forest types where the
    world has vegetation, else Koppen Af."""
    L = ctx.L
    if "vegetation" in L:
        cells = _largest_region(ctx, ctx.land & np.isin(np.asarray(L["vegetation"]), RAINFOREST_TYPES))
    elif "climate" in L:
        cells = _largest_region(ctx, ctx.land & (L["climate"] == 0))
    else:
        return []
    if cells is None:
        return []
    mid = ctx.middle(cells)
    a = len(cells) * ctx.area
    rain = float(L["precipitation"][cells].mean())
    stats = {"area_km2": round(a), "rain_mm": round(rain)}
    if "vegetation" in L:
        stats["tree_cover_pct"] = round(float(np.asarray(L["tree_cover"], float)[cells].mean()))
        blurb = (f"Evergreen tropical forest, ~{_n(rain)} mm of rain a year, {stats['tree_cover_pct']}% canopy cover: "
                 f"{_veg_mix(ctx, cells)}.")
    else:
        blurb = f"Hot and wet all year (Köppen Af), ~{_n(rain)} mm of rain a year."
    return [_feature(ctx, "rainforest", f"Largest rainforest: {_area(a)}", blurb, mid,
                     zoom_size(ctx.span_km(cells, mid)), stats, quality=0.6 + 0.4 * min(a / 3e6, 1))]


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


MED_MAX_WARM_C = 30.0
MED_TYPES = (19, 20, 21)  # vegetation: Mediterranean scrub (maquis), evergreen woodland, pine forest


def mediterranean(ctx: _Ctx, top: int = 2) -> list[dict]:
    """Csa/Csb (hot or warm dry summers, mild wet winters) on hilly but
    not alpine land: where wine country would be."""
    if "climate" not in ctx.L:
        return []
    k = ctx.L["climate"]
    relief = ctx.ring_max(ctx.elev) - ctx.ring_min(np.where(ctx.land, ctx.elev, 0.0))
    # warmest month <= 30 C: Seville, the hottest real wine Csa, is ~28 C
    ok = ctx.land & ((k == 7) | (k == 8)) & (ctx.elev < 1500) & (ctx.L["warm_month"] <= MED_MAX_WARM_C)
    regions = ctx.components(ok, min_cells=2, bridge=1)
    coast = ctx.dilate(~ctx.land) & ctx.land
    feats = []
    for rank, cells in enumerate(regions[:top]):
        mid = ctx.middle(cells)
        a = len(cells) * ctx.area
        L = ctx.L
        hilly = float(np.mean((relief[cells] > 150) & (relief[cells] < 2000)))
        on_coast = float(coast[cells].mean())
        blurb = (f"Mediterranean climate, like wine country: {_area(a)} of dry summers (~{L['warm_month'][cells].mean():.0f} °C) "
                 f"and wet winters (~{L['cold_month'][cells].mean():.0f} °C), {_n(L['precipitation'][cells].mean())} mm a year; "
                 f"{100 * hilly:.0f}% of it hilly, {100 * on_coast:.0f}% on the coast.")
        stats = {"area_km2": round(a), "hilly_pct": round(100 * hilly), "coast_pct": round(100 * on_coast)}
        q_veg = 0.0
        if "vegetation" in L:  # the Mediterranean vegetation: maquis, evergreen oak woodland, pinewoods
            med = float(np.isin(np.asarray(L["vegetation"])[cells], MED_TYPES).mean())
            stats["med_vegetation_pct"] = round(100 * med)
            blurb += f" Vegetation: {_veg_mix(ctx, cells)}."
            q_veg = 0.15 * med
        feats.append(_feature(ctx, "mediterranean", "Wine country", blurb, mid,
                              zoom_size(ctx.span_km(cells, mid)), stats,
                              quality=(0.8 ** rank) * (0.45 + 0.25 * min(a / 2e5, 1) + 0.15 * hilly
                                                       + 0.1 * min(on_coast / 0.3, 1) + q_veg)))
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
    # active arc volcanoes, from the world's volcano table (tectonics.volcanism.COLUMNS;
    # a time zoom's lists only the active ones: lat, lon, kind)
    vols = [r[:2] for r in (ctx.meta.get("volcanoes") or [])
            if len(r) >= 3 and r[2] == ARC_VOLCANO and (len(r) < 5 or r[4])]
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


CHAIN_LINK_KM = 250.0  # vents of one hotspot track are 60-195 km apart (volcanism.vent_gap)...
CHAIN_LINK_MYR = 8.0  # ... and ~1-8 Myr apart in age (100 km at 1-10 cm/yr)
ATOLL_LINK_KM = 300.0  # atolls this close make one group
WINDOW_KM = 350.0  # a chain's or group's zoom: the most islands within this of its centre


def _volcano_forms(ctx: _Ctx) -> list[dict]:
    """The world's volcano table (zoom_volcanoes.table) with each one's form
    (what it looks like now: island, atoll, guyot...); [] without one."""
    if getattr(ctx, "_vforms", None) is None:
        from .zoom_volcanoes import form, table
        ctx._vforms = [dict(v, form=form(v)) for v in table({"meta": ctx.meta})]
    return ctx._vforms


def _sunk(f: str) -> bool:
    return f in ("guyot", "drowned atoll (guyot)", "seamount")


def _counts(vs: list[dict]) -> tuple[int, int, int]:
    """(islands, atolls, guyots and seamounts) among volcanoes vs."""
    isl = sum(1 for v in vs if v["top_m"] > 0)
    atl = sum(1 for v in vs if v["form"] == "atoll")
    return isl, atl, sum(1 for v in vs if v["top_m"] <= 0 and _sunk(v["form"]))


def _best_window(ctx: _Ctx, vs: list[dict], show) -> tuple[int, float]:
    """Where to zoom on a group of volcanoes: the one with the most volcanoes
    show(v) within WINDOW_KM (so they fit a 1000 km zoom), and the km across
    those. Returns (index into vs, km)."""
    P = np.array([_unit(v["lat"], v["lon"]) for v in vs])
    d = np.arccos(np.clip(P @ P.T, -1, 1)) * R_KM
    vis = np.array([bool(show(v)) for v in vs])
    near = (d <= WINDOW_KM) & vis[None, :]
    k = int(np.argmax(near.sum(1) + 0.01 * vis))
    span = 2 * float(d[k][near[k]].max()) if near[k].any() else 0.0
    return k, span


def _tracks(vents: list[dict]) -> list[list[int]]:
    """Hotspot tracks: vents linked when within CHAIN_LINK_KM and
    CHAIN_LINK_MYR of each other's age (consecutive vents of one plume;
    a neighbouring plume's track of another age stays apart), biggest first."""
    if not vents:
        return []
    P = np.array([_unit(v["lat"], v["lon"]) for v in vents])
    age = np.array([v["age"] for v in vents], float)
    link = (np.arccos(np.clip(P @ P.T, -1, 1)) * R_KM <= CHAIN_LINK_KM) & (np.abs(age[:, None] - age[None, :]) <= CHAIN_LINK_MYR)
    lab = np.arange(len(vents))
    while True:
        new = np.where(link, lab[None, :], len(vents)).min(1)
        new = new[new]
        if np.array_equal(new, lab):
            break
        lab = new
    groups = [list(np.flatnonzero(lab == k)) for k in np.unique(lab)]
    groups.sort(key=lambda gr: -len(gr))
    return groups


def _chain_hotspot_islands(ctx: _Ctx, top: int) -> list[dict]:
    """Hotspot tracks from the volcano table (_tracks: a plume's vents in a
    row on the sea floor, youngest over the plume), ranked by how many
    islands, atolls and guyots they show (Hawaii -> Midway -> the Emperor
    seamounts). The zoom goes where most islands and atolls are."""
    if getattr(ctx, "_hchains", None) is not None:
        return ctx._hchains[:top]
    vents = [v for v in _volcano_forms(ctx) if v["kind"] == 1]
    chains = []
    for gr in _tracks(vents):
        vs = sorted((vents[k] for k in gr), key=lambda v: v["age"])
        if len(vs) < 3 or np.mean([v["floor_m"] < 0 for v in vs]) < 0.5:  # (a continental track: not islands)
            continue
        isl, atl, sunk = _counts(vs)
        if isl + atl == 0:
            continue
        chains.append((isl + atl + 0.3 * sunk, vs, isl, atl, sunk))
    chains.sort(key=lambda c: -c[0])
    out = []
    for rank, (s, vs, isl, atl, sunk) in enumerate(chains[:3]):
        k, span = _best_window(ctx, vs, lambda v: v["top_m"] > 0 or v["form"] == "atoll")
        cell = int(ctx.g.locate(np.array([_unit(vs[k]["lat"], vs[k]["lon"])]))[0])
        P = np.array([_unit(v["lat"], v["lon"]) for v in vs])
        length = float(np.arccos(np.clip(P @ P.T, -1, 1)).max()) * R_KM
        young, peak = vs[0], max(vs, key=lambda v: v["top_m"])
        parts = ([f"{isl} island{'s' if isl != 1 else ''}"] if isl else []) \
            + ([f"{atl} atoll{'s' if atl != 1 else ''}"] if atl else []) \
            + ([f"{sunk} guyots and seamounts" if sunk > 1 else "a guyot"] if sunk else [])
        head = (f"active, {_m(young['top_m'])}, over the plume" if young["active"]
                else "under 1 Myr old" if young["age"] < 1 else f"{young['age']:.0f} Myr old")
        blurb = (f"A hotspot chain of {len(vs)} volcanoes over ~{_n(length)} km: the youngest ({head}), "
                 f"then {', '.join(parts)} as the plate carries them off and they sink, the oldest {vs[-1]['age']:.0f} Myr"
                 + (f"; highest {_m(peak['top_m'])}" if peak["top_m"] > 0 else "")
                 + ". Like Hawaii, Midway and the Emperor seamounts.")
        title = (f"Island chain: {isl} islands" + (f", {atl} atolls" if atl else "")) if isl else f"Atoll chain: {atl} atolls"
        path = [[round(v["lat"], 2), round(v["lon"], 2)] for v in vs]
        if len(path) > 60:
            path = [path[j] for j in np.unique(np.linspace(0, len(path) - 1, 60).round().astype(int))]
        out.append(_feature(ctx, "hotspot_islands", title, blurb, cell, zoom_size(span + 100),
                            {"volcanoes": len(vs), "islands": isl, "atolls": atl, "sunk": sunk, "length_km": round(length),
                             "peak_m": round(peak["top_m"]), "oldest_myr": round(vs[-1]["age"]), "active": bool(young["active"])},
                            quality=(0.8 ** rank) * (0.5 + 0.5 * min(s / 10, 1)), path=path))
    ctx._hchains = out
    return out[:top]


def atolls(ctx: _Ctx, top: int = 1) -> list[dict]:
    """Coral atoll groups: atolls (a reef ring round a lagoon where a volcano
    sank, volcanism's reef state) of any volcano, hotspot or arc, within
    ATOLL_LINK_KM of each other; the group with the most, with its reef-
    fringed islands (the Tuamotus, the Marshalls, the Maldives)."""
    vols = [v for v in _volcano_forms(ctx) if v["form"] == "atoll" or (v["top_m"] > 0 and "reef" in v["form"])]
    groups = []
    for gr in _chains(ctx, [(v["lat"], v["lon"]) for v in vols], ATOLL_LINK_KM):
        vs = [vols[k] for k in gr]
        atl = sum(1 for v in vs if v["form"] == "atoll")
        if atl >= 3:
            groups.append((atl + 0.5 * (len(vs) - atl), vs, atl))
    groups.sort(key=lambda g: -g[0])
    taken = [f["cell"] for f in _chain_hotspot_islands(ctx, 3)]  # (an atoll chain is shown as the chain)
    out = []
    for s, vs, atl in groups:
        if len(out) >= top:
            break
        k, span = _best_window(ctx, vs, lambda v: v["form"] == "atoll")
        cell = int(ctx.g.locate(np.array([_unit(vs[k]["lat"], vs[k]["lon"])]))[0])
        if taken and ctx.dist(cell, taken).min() < 600:
            continue
        rank = len(out)
        reefy = len(vs) - atl
        sst = ""
        if "sst" in ctx.L:
            sst = f"; the sea ~{_c(ctx.L['sst'][cell])}"
        blurb = (f"{atl} coral atolls" + (f" and {reefy} reef-fringed islands" if reefy else "")
                 + f" within ~{_n(_extent(ctx, ctx.g.locate(np.array([_unit(v['lat'], v['lon']) for v in vs]))))} km{sst}: "
                 "rings of reef round lagoons where old volcanoes sank, like the Tuamotus or the Marshall Islands.")
        out.append(_feature(ctx, "atolls", f"Atolls: {atl} in a group", blurb, cell, zoom_size(span + 100),
                            {"atolls": atl, "reef_islands": reefy}, quality=(0.8 ** rank) * (0.5 + 0.5 * min(s / 10, 1))))
    return out


def hotspot_islands(ctx: _Ctx, top: int = 2) -> list[dict]:
    """Hotspot island chains from the volcano table where the world has one
    (_chain_hotspot_islands); else volcanic islands of hotspot basalt on
    oceanic crust, near a live hotspot."""
    if any(v["kind"] == 1 for v in _volcano_forms(ctx)):
        return _chain_hotspot_islands(ctx, top)
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


FAST_MIN_SHARE = 0.015  # a plate covering less of the planet is a microplate (they spin fast) and doesn't count
EDGE_MIN_CELLS = 3


def fastest_plate(ctx: _Ctx) -> list[dict]:
    """The fastest plate (mean speed over its cells; plates of at least
    FAST_MIN_SHARE of the planet), shown where something happens because of
    it: its leading edge, the converging boundary cells it moves towards
    (velocity pointing at the other plate), longest stretch first; there it
    is colliding, diving under its neighbour or overriding it. Nothing when
    the fastest plate has no such edge."""
    L = ctx.L
    if any(k not in L for k in ("plate", "plate_speed", "_plate_velocity", "plate_boundary", "crust")):
        return []
    plate = np.asarray(L["plate"])
    speed = np.asarray(L["plate_speed"], float)
    ids, cnt = np.unique(plate, return_counts=True)
    big = ids[cnt >= FAST_MIN_SHARE * ctx.n]
    if len(big) < 2:
        return []
    mean = {int(p): float(speed[plate == p].mean()) for p in big}
    p = max(mean, key=mean.get)
    v = np.asarray(L["_plate_velocity"], float)
    C = ctx.g.centers
    a, b = ctx.a, ctx.b
    conv = np.asarray(L["plate_boundary"]) > 0
    lead = np.zeros(ctx.n, bool)
    across = {}
    for i, j in ((a, b), (b, a)):
        m = (plate[i] == p) & (plate[j] != p) & (conv[i] | conv[j]) & ((v[i] * (C[j] - C[i])).sum(1) > 0)
        lead[i[m]] = True
        for x, y in zip(i[m], j[m]):
            across.setdefault(int(x), int(y))
    regions = ctx.components(lead, min_cells=EDGE_MIN_CELLS, bridge=1)
    if not regions:
        return []
    cells = regions[0]
    other = np.array([across[int(c)] for c in cells if int(c) in across])
    length, spine = ctx.spine(cells, ctx.dilate(lead) & (plate == p))  # (along the plate's own side)
    length += ctx.cell_km
    mid = spine[len(spine) // 2]
    q = int(np.bincount(plate[other]).argmax())
    cont = np.asarray(L["crust"]) > 0
    mine_c, theirs_c = cont[cells].mean() >= 0.5, cont[other].mean() >= 0.5
    zone = ctx.dilate(np.isin(np.arange(ctx.n), cells), 2)
    top, deep = float(ctx.elev[zone].max()), float(ctx.elev[zone].min())
    if mine_c and theirs_c:
        what, kind_ = f"colliding with plate {q}'s continent: mountains rising to {_m(top)} (like India into Asia)", "collision"
    elif mine_c:
        what, kind_ = (f"overriding plate {q}'s ocean floor: a trench to {_m(-deep)} below the sea and mountains to "
                       f"{_m(top)} (like the Andes)"), "overriding"
    elif theirs_c:
        what, kind_ = (f"diving under plate {q}'s continent: a trench {_m(-deep)} deep and mountains to {_m(top)} "
                       f"(like the Nazca plate under South America)"), "subducting"
    else:
        arc = bool((ctx.land & zone & (plate == q)).any())
        what, kind_ = (f"diving under plate {q}: a trench {_m(-deep)} deep"
                       + (f" and an island arc to {_m(top)} (like the Pacific under the Marianas)" if arc else
                          " (like the Pacific under the Marianas, before an island arc rises)")), "subducting"
    ranked = sorted(mean.values(), reverse=True)
    blurb = (f"Plate {p} moves at {mean[p]:.1f} cm/yr on average, the fastest of the {len(big)} big plates "
             f"(Earth's fastest, the Pacific and Australian plates, ~7-10 cm/yr; the next here {ranked[1]:.1f}). "
             f"Its leading edge, {_n(length)} km of it, is {what}.")
    return [_feature(ctx, "fastest_plate", f"Fastest plate: {mean[p]:.1f} cm/yr", blurb, mid, zoom_size(length),
                     {"plate": p, "speed_cmyr": round(mean[p], 1), "next_cmyr": round(ranked[1], 1), "edge_km": round(length),
                      "edge": kind_, "against": q, "top_m": round(top), "deep_m": round(deep)},
                     quality=0.5 + 0.5 * min(mean[p] / 8, 1), path=ctx.path(spine))]


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


# ---------------------------------------------------------------------------
# Round 2: falls, canyons, salt, reefs, rain shadows, plateaus, variety
# ---------------------------------------------------------------------------
def _water_surface(ctx: _Ctx) -> np.ndarray:
    """The level water runs on: a lake's surface on its cells (the world's
    lake_level, else the spill level), the ground elsewhere, 0 at sea."""
    if getattr(ctx, "_ws", None) is not None:
        return ctx._ws
    L = ctx.L
    ws = np.where(ctx.land, ctx.elev, 0.0)
    lake = ctx.land & (np.asarray(L["lake"]) > 0) if "lake" in L else np.zeros(ctx.n, bool)
    if lake.any():
        lvl = np.asarray(L["lake_level"], float) if "lake_level" in L else \
            hydrology.priority_flood(ctx.g, ctx.elev)[0]
        ws = np.where(lake, np.maximum(lvl, ctx.elev), ws)
    ctx._ws, ctx._lake = ws, lake
    return ws


def _link_km(ctx: _Ctx, i, j) -> np.ndarray:
    C = ctx.g.centers
    return np.arccos(np.clip((C[i] * C[j]).sum(-1), -1, 1)) * R_KM


def _gw(q: float, h: float) -> float:
    """Power of falling water, GW (rho g Q H)."""
    return 1000 * 9.81 * q * h / 1e9


WF_MIN_Q, WF_MIN_DROP = 300.0, 300.0  # m^3/s, m: a big river, a big drop (over one or two ~110 km links)


def waterfalls(ctx: _Ctx, top: int = 3) -> list[dict]:
    """Big rivers dropping steeply: the biggest fall of the water surface
    over one or two downstream links, to land or a lake, on rivers of at
    least WF_MIN_Q m^3/s; ranked by the power of the falling water."""
    if "flow" not in ctx.L or not ctx.land.any():
        return []
    R = _rivers(ctx)
    down, q = R["down"], R["q"]
    ws = _water_surface(ctx)
    lake = ctx._lake
    i = np.flatnonzero(ctx.land & (down >= 0) & ~R["iced"] & (q >= WF_MIN_Q) & ctx.land[np.maximum(down, 0)])
    if not len(i):
        return []
    d1 = down[i]
    h1, k1 = ws[i] - ws[d1], _link_km(ctx, i, d1)
    two = (down[d1] >= 0) & ctx.land[np.maximum(down[d1], 0)]
    d2 = np.where(two, down[d1], d1)
    h2 = np.where(two, ws[i] - ws[d2], -np.inf)
    use2 = h2 > 1.3 * h1  # the second link counts if it adds a good part of the drop
    h = np.where(use2, h2, h1)
    km = np.where(use2, k1 + _link_km(ctx, d1, d2), k1)
    cand = [{"cell": int(a), "h": float(hh), "km": float(kk), "q": float(q[a]), "gw": _gw(float(q[a]), float(hh)),
             "cells": [int(a), int(b)] + ([int(c)] if u else [])}
            for a, b, c, hh, kk, u in zip(i, d1, d2, h, km, use2) if hh >= WF_MIN_DROP]
    cand.sort(key=lambda c: -c["gw"])
    kept = []
    for c in cand:  # one per stretch of river
        if all(ctx.dist(k["cell"], [c["cell"]])[0] > 400 for k in kept):
            kept.append(c)
        if len(kept) >= top:
            break
    feats = []
    for rank, c in enumerate(kept):
        a, end = c["cell"], c["cells"][-1]
        spill = bool(lake[a] and not lake[c["cells"][1]])
        if spill:
            title = ("Biggest waterfall" if rank == 0 else "Waterfall") + f": a {_m(c['h'])} drop from a lake"
            what = (f"A lake spills over its rim here: its outflow, {_n(c['q'])} m³/s, drops ~{_m(c['h'])} "
                    f"within {_n(c['km'])} km.")
        else:
            title = ("Steepest big river" if rank == 0 else "Steep river reach") + f": {_m(c['h'])} drop"
            what = (f"A {_n(c['q'])} m³/s river drops ~{_m(c['h'])} over {_n(c['km'])} km "
                    f"(from {_m(ws[a])} to {_m(ws[end])}). On ~{_n(ctx.cell_km)} km cells that's a steep "
                    f"reach; zoom in to see the falls, gorge and cascades it holds.")
        blurb = what + f" ~{_n(c['gw'])} GW of falling water (Niagara: ~1.2 GW)."
        feats.append(_feature(ctx, "waterfall", title, blurb, a, 500,
                              {"drop_m": round(c["h"]), "reach_km": round(c["km"]), "discharge_m3s": round(c["q"]),
                               "power_gw": round(c["gw"], 1), "top_m": round(float(ws[a])),
                               "bottom_m": round(float(ws[end])), "lake_outlet": spill},
                              quality=(0.8 ** rank) * min(1.0, 0.5 + c["gw"] / 40),
                              path=ctx.path(c["cells"])))
    return feats


def canyons(ctx: _Ctx, top: int = 2) -> list[dict]:
    """A river cut deep into high ground: its cell far below the land on
    both sides of it (the lower of the two sides' mean height, neighbours
    off the river only), on ground averaging >= 1000 m within two cells."""
    if "flow" not in ctx.L or not ctx.land.any():
        return []
    R = _rivers(ctx)
    down, q = R["down"], R["q"]
    mean2 = _ring_mean(ctx, np.where(ctx.land, ctx.elev, 0.0), 2)
    riv = ctx.land & ~R["iced"] & (q >= 300) & (mean2 >= 1000) & (down >= 0)
    up = np.full(ctx.n, -1)  # the main upstream cell (most water) of each river cell
    has = np.flatnonzero(ctx.land & (down >= 0))
    for c in has[np.argsort(q[has], kind="stable")]:
        up[down[c]] = c
    cand = []
    for i in np.flatnonzero(riv):
        depth, rim = _incision(ctx, int(i), down, up)
        if depth >= 400:
            cand.append((depth, int(i), rim))
    cand.sort(key=lambda c: -c[0])
    kept = []
    for c in cand:
        if all(ctx.dist(k[1], [c[1]])[0] > 500 for k in kept):
            kept.append(c)
        if len(kept) >= top:
            break
    feats = []
    for rank, (depth, i, rim) in enumerate(kept):
        # the canyon: the river's course up and down from here while it stays far below its rims
        deep = lambda c: _incision(ctx, int(c), down, up)[0] >= 0.5 * depth
        course = [i]
        while up[course[0]] >= 0 and deep(up[course[0]]) and len(course) < 50:
            course.insert(0, int(up[course[0]]))
        while down[course[-1]] >= 0 and ctx.land[down[course[-1]]] and deep(down[course[-1]]) and len(course) < 100:
            course.append(int(down[course[-1]]))
        length = float(_link_km(ctx, course[:-1], course[1:]).sum()) + ctx.cell_km
        blurb = (f"A {_n(q[i])} m³/s river runs at ~{_m(ctx.elev[i])}, ~{_m(depth)} below the high ground on "
                 f"both sides (~{_m(rim)}), for ~{_n(length)} km: a canyon cut into an upland, like the Grand "
                 f"Canyon (on ~{_n(ctx.cell_km)} km cells only the biggest show).")
        feats.append(_feature(ctx, "canyon", ("Deepest canyon" if rank == 0 else "Canyon") + f": ~{_m(depth)}",
                              blurb, i, zoom_size(max(length, 250)),
                              {"depth_m": round(depth), "river_m": int(ctx.elev[i]), "rim_m": round(rim),
                               "discharge_m3s": round(q[i]), "length_km": round(length)},
                              quality=(0.8 ** rank) * (0.5 + 0.5 * min(depth / 1500, 1)), path=ctx.path(course)))
    return feats


def _incision(ctx: _Ctx, i: int, down: np.ndarray, up: np.ndarray) -> tuple[float, float]:
    """(depth, rim) of river cell i: its neighbours off the river, split by
    the flow line into left and right banks; the rim is the lower bank's
    mean height. (0, 0) unless both banks have land."""
    g, C = ctx.g, ctx.g.centers
    nb = g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]
    side = np.array([j for j in nb if j != down[i] and down[j] != i and ctx.land[j]], int)
    if not len(side):
        return 0.0, 0.0
    a = C[down[i]] - (C[up[i]] if up[i] >= 0 else C[i])
    s = np.cross(a, C[side] - C[i]) @ C[i]
    left, right = ctx.elev[side[s > 0]], ctx.elev[side[s < 0]]
    if not len(left) or not len(right):
        return 0.0, 0.0
    rim = float(min(left.mean(), right.mean()))
    return rim - float(ctx.elev[i]), rim


def _ring_mean(ctx: _Ctx, v: np.ndarray, k: int = 1) -> np.ndarray:
    """Mean of v over each cell and its neighbours, k times (a smoothing)."""
    g = ctx.g
    deg = np.diff(g.nbr_off)
    out = v.astype(float)
    for _ in range(k):
        out = (out + np.add.reduceat(out[g.nbr_idx], g.nbr_off[:-1])) / (deg + 1)
    return out


def salt(ctx: _Ctx) -> list[dict]:
    """Closed basins: the biggest salt lake (lake_kind 2: closed, keeps its
    water and its salt), the biggest salt pan (lake_kind 3: dried out), and
    the largest region draining inland (its rivers end in a closed lake or a
    pit, not the sea). Worlds made before lake_kind existed have none of
    these; there, exposed evaporite beds (surface rock) on dry land count as
    salt flats."""
    L = ctx.L
    feats = []
    if "lake_kind" in L:
        kind = np.asarray(L["lake_kind"])
        ws = _water_surface(ctx)
        pet = np.asarray(L["pet"], float) if "pet" in L else None
        for k, kd in ((2, "salt_lake"), (3, "salt_pan")):
            regions = ctx.components(ctx.land & (kind == k))
            if not regions:
                continue
            cells = regions[0]
            mid = ctx.middle(cells)
            a = len(cells) * ctx.area
            lvl = float(np.median(ws[cells]))
            below = f"{_m(-lvl)} below sea level" if lvl < 0 else f"at {_m(lvl)}"
            basin = _inland_basins(ctx).get(int(_sink(ctx, [cells[0]])[0]))
            basin_a = len(basin) * ctx.area if basin is not None else a
            evap = f"; ~{_n(pet[cells].mean())} mm a year could evaporate" if pet is not None else ""
            rain = float(L["precipitation"][cells].mean())
            if k == 2:
                depth = float((ws[cells] - ctx.elev[cells]).max())
                title = f"Biggest salt lake: {_area(a)}"
                blurb = (f"A lake with no outlet (like the Caspian or the Dead Sea), surface {below}, up to "
                         f"~{_m(depth)} deep. Rivers from a {_area(basin_a)} basin feed it and the sun takes the "
                         f"water away, leaving the salt: ~{rain:.0f} mm of rain{evap}.")
            else:
                title = f"Biggest salt flat: {_area(a)}"
                blurb = (f"A dry lake bed {below}, crusted with salt (like Salar de Uyuni or Lake Eyre): what "
                         f"reaches it from a {_area(basin_a)} basin all evaporates; ~{rain:.0f} mm of rain{evap}.")
            feats.append(_feature(ctx, kd, title, blurb, mid, zoom_size(max(ctx.span_km(cells, mid), 250)),
                                  {"area_km2": round(a), "surface_m": round(lvl), "basin_km2": round(basin_a)},
                                  quality=0.6 + 0.4 * min(a / 1e5, 1)))
    basins = _inland_basins(ctx)
    if basins:
        cells = max(basins.values(), key=len)
        a = len(cells) * ctx.area
        if a >= 5 * ctx.area:
            low = int(cells[np.argmin(_water_surface(ctx)[cells])])
            mid = ctx.middle(cells)
            pct = 100 * len(cells) / max(ctx.land.sum(), 1)
            all_inland = sum(len(b) for b in basins.values()) / max(ctx.land.sum(), 1)
            rain = float(L["precipitation"][cells].mean())
            blurb = (f"{_area(a)} ({pct:.0f}% of all land) whose rivers never reach the sea: they end at "
                     f"~{_m(_water_surface(ctx)[low])} in a closed lake or salt pan; ~{rain:.0f} mm of rain a year. "
                     f"{100 * all_inland:.0f}% of the world's land drains inland (Earth: ~20%).")
            feats.append(_feature(ctx, "inland_basin", f"Largest inland basin: {_area(a)}", blurb, mid,
                                  zoom_size(ctx.span_km(cells, mid)),
                                  {"area_km2": round(a), "pct_of_land": round(float(pct), 1), "sink_cell": low,
                                   "inland_pct_of_land": round(100 * float(all_inland), 1)},
                                  quality=0.6 + 0.4 * min(a / 2e6, 1)))
    if "lake_kind" not in L and "surface_rock" in L and "precipitation" in L:
        ev = ctx.land & (np.asarray(L["surface_rock"]) == 9) & (np.asarray(L["precipitation"]) < 500)
        regions = ctx.components(ev, min_cells=2, bridge=1)
        if regions:
            cells = regions[0]
            mid = ctx.middle(cells)
            a = len(cells) * ctx.area
            blurb = (f"{_area(a)} of salt and gypsum beds at the surface, ~{_m(np.median(ctx.elev[cells]))} up, "
                     f"~{L['precipitation'][cells].mean():.0f} mm of rain a year: the floors of old salt lakes "
                     f"and seas that dried out.")
            feats.append(_feature(ctx, "salt_flats", f"Salt flats: {_area(a)}", blurb, mid,
                                  zoom_size(max(ctx.span_km(cells, mid), 250)), {"area_km2": round(a)},
                                  quality=0.6 + 0.4 * min(a / 1e5, 1)))
    return feats


def _inland_basins(ctx: _Ctx) -> dict[int, np.ndarray]:
    """Land draining inland, grouped by where it ends: {sink: cells}. The
    sink is the closed lake's lowest-id cell (_sink), or the pit."""
    if getattr(ctx, "_inland", None) is not None:
        return ctx._inland
    out = {}
    _water_surface(ctx)
    ctx._lake_lab = ctx.g.components(ctx._lake)[0]
    if "downstream" in ctx.L and ctx.land.any():
        R = _rivers(ctx)
        end = R["outlet"]
        cells = np.flatnonzero(ctx.land & ~R["mouth"][end])
        if len(cells):
            key = _sink(ctx, end[cells])
            for k in np.unique(key):
                out[int(k)] = cells[key == k]
    ctx._inland = out
    return out


def _sink(ctx: _Ctx, cells) -> np.ndarray:
    """Each cell, or the lowest-id cell of the lake it's in."""
    lab = ctx._lake_lab
    cells = np.asarray(cells)
    lk = np.flatnonzero(lab >= 0)
    first = np.full(lab.max() + 2, ctx.n)
    np.minimum.at(first, lab[lk], lk)
    return np.where(lab[cells] >= 0, first[np.maximum(lab[cells], 0)], cells)


REEF_MIN_C, REEF_MAX_DEPTH = 18.0, 250.0  # coldest-month sea temperature, m of water (cell mean)


def coral_coasts(ctx: _Ctx, top: int = 2) -> list[dict]:
    """Where reefs would grow: open sea next to land that is shallow (cell
    mean <= REEF_MAX_DEPTH m) and warm all year (coldest month >=
    REEF_MIN_C at the surface), away from big river mouths (mud). Limestone
    on the shore (surface rock) is old reef, a bonus."""
    L = ctx.L
    if "cold_month" not in L or not ctx.land.any():
        return []
    sea = ~ctx.land
    ocean = np.zeros(ctx.n, bool)
    regions = ctx.components(sea)
    if regions:
        ocean[regions[0]] = True
    muddy = np.zeros(ctx.n, bool)
    if "flow" in L:
        R = _rivers(ctx)
        m = np.flatnonzero(R["mouth"] & (R["q"] > 3000))
        muddy[R["down"][m]] = True
        muddy = ctx.dilate(muddy, 1)
    cold = np.asarray(L["cold_month"], float)
    reef = ocean & (ctx.elev > -REEF_MAX_DEPTH) & (cold >= REEF_MIN_C) & ctx.dilate(ctx.land) & ~muddy
    lime = ctx.land & np.isin(L["surface_rock"], (6, 14)) if "surface_rock" in L else None  # limestone, dolomite
    out = []
    for cells in ctx.components(reef, min_cells=3, bridge=1)[:8]:
        length, spine = ctx.spine(cells, ctx.dilate(reef) & sea)
        length += ctx.cell_km
        shore = ctx.dilate(np.isin(np.arange(ctx.n), cells)) & ctx.land
        lime_pct = 100 * float(lime[shore].mean()) if lime is not None and shore.any() else 0.0
        out.append((length * (1 + lime_pct / 100), length, cells, spine, lime_pct))
    out.sort(key=lambda x: -x[0])
    feats = []
    best = out[0][0] if out else 1.0
    for rank, (s, length, cells, spine, lime_pct) in enumerate(out[:top]):
        mid = spine[len(spine) // 2]
        t_cold, t_warm = float(cold[cells].mean()), float(np.asarray(L["warm_month"])[cells].mean())
        depth = float(-ctx.elev[cells].mean())
        lime_txt = f" {lime_pct:.0f}% of the shore is limestone, old reefs lifted onto land." if lime_pct >= 5 else ""
        blurb = (f"{_n(length)} km of warm, shallow, clear sea along the coast: ~{_m(depth)} deep on average, "
                 f"{t_cold:.0f}–{t_warm:.0f} °C through the year, no big river mud. Coral reef country (like "
                 f"the Great Barrier Reef or the Caribbean).{lime_txt} The zoom shows the shallows, not the reefs.")
        feats.append(_feature(ctx, "coral_coast", "Coral coast", blurb, mid, zoom_size(min(length, 1000)),
                              {"length_km": round(length), "mean_depth_m": round(depth), "sea_c_min": round(t_cold, 1),
                               "limestone_pct": round(lime_pct)},
                              quality=(0.8 ** rank) * (0.5 + 0.5 * s / best) * min(1, 0.4 + length / 1500),
                              path=ctx.path(spine)))
    return feats


def rain_shadows(ctx: _Ctx, top: int = 3) -> list[dict]:
    """Mountains with a wet side and a dry side: for each high cell (>=
    1500 m), the land 2-4 cells away, split in two by the line through it
    that gives the biggest contrast in yearly rain (12 directions). Needs a
    dry side under 600 mm, a wet side over 600 mm with at least 3x as much; ranked
    by the ratio (up to 10) x the height of the mountains."""
    L = ctx.L
    if "precipitation" not in L or not ctx.land.any():
        return []
    P = np.asarray(L["precipitation"], float)
    C = ctx.g.centers
    ice = np.asarray(L["ice"], float) if "ice" in L else np.zeros(ctx.n)
    # only summits (local maxima) are tried, one per hill; not under ice caps (a white zoom)
    crest = np.flatnonzero(ctx.land & (ctx.elev >= 1500) & (ctx.elev >= ctx.ring_max(ctx.elev) - 1) &
                           (ice <= ICE_PEAK_M))
    if not len(crest):
        return []
    ring = _rings(ctx, 4)
    th = np.linspace(0, np.pi, 12, endpoint=False)
    cand = []
    for c in crest:
        nb = np.array([j for j in ring(c) if ctx.land[j] and ctx.elev[j] < ctx.elev[c] - 300])
        if len(nb) < 8:
            continue
        e = np.cross([0.0, 0.0, 1.0], C[c])
        e = e / max(np.linalg.norm(e), 1e-9) if np.linalg.norm(e) > 1e-9 else np.array([0.0, 1.0, 0.0])
        nn = np.cross(C[c], e)
        d = C[nb] - C[c]
        x, y = d @ e, d @ nn
        r = np.hypot(x, y)
        best = None
        for t in th:
            s = (x * np.cos(t) + y * np.sin(t)) / r
            a, b = nb[s > 0.4], nb[s < -0.4]
            if len(a) < 3 or len(b) < 3:
                continue
            pa, pb = P[a].mean(), P[b].mean()
            wet, dry = (a, b) if pa > pb else (b, a)
            ratio = max(pa, pb) / max(min(pa, pb), 10.0)
            if best is None or ratio > best[0]:
                best = (ratio, wet, dry)
        if best and best[0] >= 3 and P[best[2]].mean() < 600 and P[best[1]].mean() >= 600:
            ratio, wet, dry = best
            cand.append((min(ratio, 10) * ctx.elev[c], int(c), ratio, wet, dry))
    cand.sort(key=lambda x: -x[0])
    kept = []
    for x in cand:
        if all(ctx.dist(k[1], [x[1]])[0] > 800 for k in kept):
            kept.append(x)
        if len(kept) >= top:
            break
    feats = []
    best = kept[0][0] if kept else 1.0
    for rank, (s, c, ratio, wet, dry) in enumerate(kept):
        pw, pd = float(P[wet].mean()), float(P[dry].mean())
        cw, cd = ctx.middle(wet), ctx.middle(dry)
        km = float(ctx.dist(cw, [cd])[0])
        blurb = (f"~{_n(pw)} mm of rain a year on the wet side, ~{_n(pd)} mm on the dry side ({ratio:.0f}× less), "
                 f"{_n(km)} km apart across {_m(ctx.elev[c])} mountains: the mountains wring the rain out of the "
                 f"air before it crosses (like the Andes over Patagonia, or the Sierra Nevada).")
        feats.append(_feature(ctx, "rain_shadow", "Rain shadow", blurb, c, 1000,
                              {"wet_mm": round(pw), "dry_mm": round(pd), "ratio": round(float(ratio), 1),
                               "crest_m": int(ctx.elev[c]), "across_km": round(km)},
                              quality=(0.8 ** rank) * (0.5 + 0.5 * s / best), path=ctx.path([cw, c, cd])))
    return feats


def _rings(ctx: _Ctx, k: int):
    """cells(c): the cells 2..k links from c (not c's own neighbours)."""
    g = ctx.g

    def cells(c):
        seen, front = {int(c)}, [int(c)]
        out = []
        for step in range(k):
            nxt = []
            for i in front:
                for j in g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]:
                    j = int(j)
                    if j not in seen:
                        seen.add(j)
                        nxt.append(j)
            if step >= 1:
                out += nxt
            front = nxt
        return out
    return cells


PLATEAU_M, PLATEAU_RELIEF = 2000.0, 500.0  # m


def plateaus(ctx: _Ctx, top: int = 3) -> list[dict]:
    """Large high, flat ground: land >= PLATEAU_M (not under an ice sheet)
    whose cells differ from their neighbours by < PLATEAU_RELIEF m on
    average, in one piece of at least 4 cells. Like Tibet or the Altiplano."""
    if not ctx.land.any():
        return []
    L = ctx.L
    g = ctx.g
    deg = np.diff(g.nbr_off)
    relief = np.add.reduceat(np.abs(ctx.elev[g.nbr_idx] - np.repeat(ctx.elev, deg)), g.nbr_off[:-1]) / deg
    ice = np.asarray(L["ice"], float) if "ice" in L else np.zeros(ctx.n)
    mask = ctx.land & (ctx.elev >= PLATEAU_M) & (relief < PLATEAU_RELIEF) & (ice < 100)
    feats = []
    regions = ctx.components(mask, min_cells=4)
    for rank, cells in enumerate(regions[:top]):
        mid = ctx.middle(cells)
        a = len(cells) * ctx.area
        h, r = float(ctx.elev[cells].mean()), float(np.median(relief[cells]))
        clim = ""
        if "climate" in L:
            k = np.bincount(np.asarray(L["climate"])[cells], minlength=31).argmax()
            clim = f" Mostly {KOPPEN_NAME.get(int(k), '')}: ~{_c(L['temperature'][cells].mean())}, " \
                   f"~{_n(L['precipitation'][cells].mean())} mm of rain a year."
        blurb = (f"{_area(a)} of high, flat ground averaging {_m(h)} (neighbouring ~{_n(ctx.cell_km)} km cells "
                 f"differ by ~{_m(r)}), like Tibet or the Altiplano.{clim}")
        feats.append(_feature(ctx, "plateau", ("Largest plateau" if rank == 0 else "Plateau") + f": {_area(a)}",
                              blurb, mid, zoom_size(ctx.span_km(cells, mid)),
                              {"area_km2": round(a), "mean_m": round(h), "relief_m": round(r)},
                              quality=(0.85 ** rank) * (0.4 + 0.3 * min(a / 1e6, 1) + 0.3 * min(h / 4000, 1))))
    return feats


VARIED_KM = 1000.0
VARIED_CENTRES = 6000  # most squares tried (every other land cell at level 6, ~1 in 8 at level 7)


def most_varied(ctx: _Ctx) -> list[dict]:
    """The VARIED_KM square (centred on a land cell, edges east-west and
    north-south) with the most varied climates and plants: the effective
    number of Koppen classes x of vegetation types (the named types where
    the world has them, else biomes; exp of the Shannon entropy of their
    land shares, so evenly mixed beats one big class with specks of others),
    square-rooted, and lowered when it's under half land."""
    L = ctx.L
    veg = "vegetation" if "vegetation" in L else "biome"
    if "climate" not in L or veg not in L or ctx.land.sum() < 10:
        return []
    land = np.flatnonzero(ctx.land)
    C = ctx.g.centers
    Pl = C[land]
    kk = np.asarray(L["climate"])[land]
    bb = np.asarray(L[veg])[land]
    ok_ = np.eye(max(kk.max(), 30) + 1)[kk]
    ob = np.eye(max(bb.max(), len(VEG_TYPES) if veg == "vegetation" else 15) + 1)[bb]
    full = VARIED_KM ** 2 / ctx.area  # cells in a full square
    half = VARIED_KM / 2 / R_KM
    best = (-1.0, -1, None, None, 0.0)
    # candidate centres: every land cell up to VARIED_CENTRES of them, else
    # evenly thinned (a 1000 km square hardly changes over a cell or two)
    centres = land[::max(1, -(-len(land) // VARIED_CENTRES))]
    for s in range(0, len(centres), 512):
        ci = centres[s:s + 512]
        c = C[ci]
        e = np.cross([0.0, 0.0, 1.0], c)
        e /= np.maximum(np.linalg.norm(e, axis=1, keepdims=True), 1e-9)
        nn = np.cross(c, e)
        inside = (np.abs(e @ Pl.T) <= half) & (np.abs(nn @ Pl.T) <= half) & (c @ Pl.T > 0)
        insf = inside.astype(float)
        nk, nb = insf @ ok_, insf @ ob
        cnt = inside.sum(1)
        eff = []
        for cnts in (nk, nb):
            p = cnts / np.maximum(cnt, 1)[:, None]
            eff.append(np.exp(-(p * np.log(np.where(p > 0, p, 1))).sum(1)))
        score = np.sqrt(eff[0] * eff[1]) * np.minimum(1, cnt / (0.5 * full))
        j = int(np.argmax(score))
        if score[j] > best[0]:
            best = (float(score[j]), int(ci[j]), nk[j], nb[j], float(cnt[j] / full))
    score, c, nk, nb, landfrac = best
    if c < 0:
        return []
    names = sorted(((n, k) for k, n in enumerate(nk) if n > 0), reverse=True)
    top3 = ", ".join(f"{KOPPEN_NAME.get(k, k)} {100 * n / nk.sum():.0f}%" for n, k in names[:3])
    n_k, n_b = int((nk > 0).sum()), int((nb > 0).sum())
    what = "vegetation types" if veg == "vegetation" else "biomes"
    blurb = (f"{n_k} Köppen climates and {n_b} {what} in one {_n(VARIED_KM)} km square "
             f"({100 * min(landfrac, 1):.0f}% land): {top3}, and more. The most varied corner of the world.")
    return [_feature(ctx, "varied_square", f"Most varied {_n(VARIED_KM)} km square", blurb, c, 1000,
                     {"koppen_classes": n_k, ("vegetation_types" if veg == "vegetation" else "biomes"): n_b, "diversity": round(score, 2),
                      "land_pct": round(100 * min(landfrac, 1))},
                     quality=0.6 + 0.4 * min(score / 8, 1))]


# ---------------------------------------------------------------------------
# Vegetation (worlds with the vegetation layers, vegetation.py)
# ---------------------------------------------------------------------------
VEG_NAME = {t[0]: t[1] for t in VEG_TYPES}
VEG_GROUP = {t[0]: t[2] for t in VEG_TYPES}
FOREST_COVER = 60.0  # % tree cover: a closed forest
SAVANNA_TYPES = (8, 9, 10)  # moist savanna woodland, dry savanna, tropical grassland
WETLAND_TYPES = (5, 6, 11, 50, 51, 52, 53, 54)  # swamp and peat forests, flooded grassland, marsh, bog, fen, palsa mire
ALPINE_TYPES = (12, 47, 48, 49)  # paramo, alpine meadow, krummholz, fellfield
TREELINE_DROP_M = 300.0  # the forest below an alpine cell at least this much lower
TREELINE_FOREST = 40.0  # % tree cover of that forest


def _veg_mix(ctx: _Ctx, cells, k: int = 3) -> str:
    """The region's commonest named vegetation types with their shares."""
    ids, cnt = np.unique(np.asarray(ctx.L["vegetation"])[np.asarray(cells)], return_counts=True)
    order = np.argsort(-cnt, kind="stable")[:k]
    return ", ".join(f"{VEG_NAME.get(int(ids[o]), ids[o])} {100 * cnt[o] / cnt.sum():.0f}%" for o in order)


def _dominant(ctx: _Ctx, cells) -> int:
    ids, cnt = np.unique(np.asarray(ctx.L["vegetation"])[np.asarray(cells)], return_counts=True)
    return int(ids[np.argmax(cnt)])


def great_forests(ctx: _Ctx, top: int = 2) -> list[dict]:
    """The largest closed forests (tree cover >= FOREST_COVER) outside the
    evergreen tropics (the rainforest has its own place): each of a
    different kind (its commonest type's group: boreal, temperate, warm
    temperate, monsoon forest...), largest first."""
    L = ctx.L
    if "vegetation" not in L or "tree_cover" not in L:
        return []
    veg = np.asarray(L["vegetation"])
    ok = ctx.land & (np.asarray(L["tree_cover"], float) >= FOREST_COVER) & ~np.isin(veg, RAINFOREST_TYPES)
    feats, groups = [], set()
    for cells in ctx.components(ok, min_cells=5):
        d = _dominant(ctx, cells)
        if VEG_GROUP[d] in groups:
            continue
        groups.add(VEG_GROUP[d])
        mid = ctx.middle(cells)
        a = len(cells) * ctx.area
        tc = float(np.asarray(L["tree_cover"], float)[cells].mean())
        stats = {"area_km2": round(a), "tree_cover_pct": round(tc), "type": VEG_NAME[d], "group": VEG_GROUP[d]}
        if "canopy_height" in L:
            stats["canopy_m"] = round(float(np.asarray(L["canopy_height"], float)[cells].mean()))
        blurb = (f"{_area(a)} of closed forest, {round(tc)}% canopy cover"
                 + (f", trees ~{stats['canopy_m']} m tall" if "canopy_m" in stats else "")
                 + f": {_veg_mix(ctx, cells)}. {VEG_TYPES[d][5]}")
        rank = len(feats)
        feats.append(_feature(ctx, "great_forest", f"Great forest: {_area(a)} of {VEG_NAME[d]}", blurb, mid,
                              zoom_size(ctx.span_km(cells, mid)), stats,
                              quality=(0.85 ** rank) * (0.6 + 0.4 * min(a / 3e6, 1))))
        if len(feats) >= top:
            break
    return feats


def savanna(ctx: _Ctx) -> list[dict]:
    """The great savanna: the largest region of savanna woodland, dry savanna
    and tropical grassland, with how often it burns."""
    L = ctx.L
    if "vegetation" not in L:
        return []
    cells = _largest_region(ctx, ctx.land & np.isin(np.asarray(L["vegetation"]), SAVANNA_TYPES), min_cells=5)
    if cells is None:
        return []
    mid = ctx.middle(cells)
    a = len(cells) * ctx.area
    stats = {"area_km2": round(a), "rain_mm": round(float(L["precipitation"][cells].mean()))}
    blurb = f"{_area(a)} of grass and scattered trees, ~{_n(stats['rain_mm'])} mm of rain a year"
    if "tree_cover" in L:
        stats["tree_cover_pct"] = round(float(np.asarray(L["tree_cover"], float)[cells].mean()))
        blurb += f", {stats['tree_cover_pct']}% tree cover"
    if "fire_return" in L:
        fr = np.asarray(L["fire_return"], float)[cells]
        if (fr > 0).any():
            stats["fire_return_yr"] = round(float(np.median(fr[fr > 0])))
            blurb += f", burning every ~{stats['fire_return_yr']} years"
    blurb += f": {_veg_mix(ctx, cells)}. Big herds and their predators."
    return [_feature(ctx, "savanna", f"Great savanna: {_area(a)}", blurb, mid, zoom_size(ctx.span_km(cells, mid)),
                     stats, quality=0.6 + 0.4 * min(a / 3e6, 1))]


def wetlands(ctx: _Ctx, top: int = 2) -> list[dict]:
    """The biggest wetlands (the Sudd, the Pantanal, the West Siberian bogs):
    connected swamp forest, flooded grassland, marsh, bog, fen and palsa
    mire, one-cell gaps bridged; ranked by area x the flooded share."""
    L = ctx.L
    if "vegetation" not in L:
        return []
    regions = ctx.components(ctx.land & np.isin(np.asarray(L["vegetation"]), WETLAND_TYPES), min_cells=3, bridge=1)
    fl = np.asarray(L["flooded"], float) if "flooded" in L else None
    cand = []
    for cells in regions[:20]:
        f = float(fl[cells].mean()) if fl is not None else 30.0
        cand.append((len(cells) * ctx.area * (0.5 + f / 100), cells, f))
    cand.sort(key=lambda c: -c[0])
    feats = []
    for rank, (_, cells, f) in enumerate(cand[:top]):
        mid = ctx.middle(cells)
        a = len(cells) * ctx.area
        d = _dominant(ctx, cells)
        stats = {"area_km2": round(a), "flooded_pct": round(f), "type": VEG_NAME[d]}
        blurb = (f"{_area(a)} of wetland, ~{round(f)}% of it under water part of the year: {_veg_mix(ctx, cells)}. "
                 f"{VEG_TYPES[d][5]}")
        feats.append(_feature(ctx, "wetland", f"Wetland: {_area(a)} of {VEG_NAME[d]}", blurb, mid,
                              zoom_size(ctx.span_km(cells, mid)), stats,
                              quality=(0.85 ** rank) * (0.5 + 0.5 * min(a / 5e5, 1))))
    return feats


def maquis_coast(ctx: _Ctx) -> list[dict]:
    """The largest stretch of Mediterranean vegetation (maquis, evergreen oak
    woodland, pinewoods) along a coast: connected cells of MED_TYPES, one-
    cell gaps bridged, at least a quarter of them on the coast. (Wine
    country is the Koppen Cs climate; this is the plants.)"""
    L = ctx.L
    if "vegetation" not in L:
        return []
    coast = ctx.dilate(~ctx.land) & ctx.land
    best = None
    for cells in ctx.components(ctx.land & np.isin(np.asarray(L["vegetation"]), MED_TYPES), min_cells=3, bridge=1):
        on = float(coast[cells].mean())
        if on >= 0.25 and (best is None or len(cells) * on > best[0]):
            best = (len(cells) * on, cells, on)
    if best is None:
        return []
    _, cells, on = best
    mid = ctx.middle(cells[coast[cells]])
    a = len(cells) * ctx.area
    stats = {"area_km2": round(a), "coast_pct": round(100 * on),
             "warm_month_c": round(float(L["warm_month"][cells].mean())),
             "rain_mm": round(float(L["precipitation"][cells].mean()))}
    blurb = (f"{_area(a)} of evergreen scrub and woodland, {stats['coast_pct']}% of it on the coast; warmest month "
             f"~{stats['warm_month_c']} °C, ~{_n(stats['rain_mm'])} mm of rain a year")
    if "fire_return" in L:
        fr = np.asarray(L["fire_return"], float)[cells]
        if (fr > 0).any():
            stats["fire_return_yr"] = round(float(np.median(fr[fr > 0])))
            blurb += f", burning every ~{stats['fire_return_yr']} years"
    blurb += f": {_veg_mix(ctx, cells)}. Aromatic evergreen thickets down to the sea."
    return [_feature(ctx, "maquis_coast", f"Maquis coast: {_area(a)}", blurb, mid,
                     zoom_size(min(ctx.span_km(cells, mid), 1000)), stats, quality=0.5 + 0.5 * min(a / 3e5, 1))]


def treelines(ctx: _Ctx) -> list[dict]:
    """The treeline, two ways: on mountains, the longest line of alpine
    meadow, krummholz or fellfield above forest (>= TREELINE_FOREST % trees)
    at least TREELINE_DROP_M lower next to it, with the height the trees
    reach; towards the poles, the largest belt of forest-tundra."""
    L = ctx.L
    if "vegetation" not in L or "tree_cover" not in L:
        return []
    veg = np.asarray(L["vegetation"])
    tc = np.asarray(L["tree_cover"], float)
    forest = ctx.land & (tc >= TREELINE_FOREST)
    alpine = ctx.land & np.isin(veg, ALPINE_TYPES)
    feats = []
    # alpine: an alpine cell with a forest neighbour well below it, and that forest cell
    a, b = ctx.a, ctx.b
    line = np.zeros(ctx.n, bool)
    for i, j in ((a, b), (b, a)):
        m = alpine[i] & forest[j] & (ctx.elev[i] - ctx.elev[j] >= TREELINE_DROP_M)
        line[i[m]] = True
        line[j[m]] = True
    regions = ctx.components(line, min_cells=3, bridge=1)
    if regions:
        cells = regions[0]
        top_forest = cells[forest[cells]]
        mid = ctx.middle(cells)
        tl = float(np.percentile(ctx.elev[top_forest], 90)) if len(top_forest) else float(ctx.elev[cells].min())
        length, path = ctx.spine(cells, ctx.dilate(line, 1))
        lat = float(abs(ctx.g.lat[mid]))
        stats = {"treeline_m": round(tl, -1), "length_km": round(length), "lat": round(lat)}
        blurb = (f"Forest gives way to {VEG_NAME[_dominant(ctx, cells[alpine[cells]])]} at ~{_m(round(tl, -1))} along "
                 f"~{_n(length)} km of mountains ({lat:.0f}° {'N' if ctx.g.lat[mid] >= 0 else 'S'}): "
                 f"{_veg_mix(ctx, cells)}.")
        feats.append(_feature(ctx, "treeline", f"Treeline at ~{_m(round(tl, -1))}", blurb, mid,
                              zoom_size(min(ctx.span_km(cells, mid), 1000)), stats,
                              quality=0.6 + 0.4 * min(length / 1500, 1), path=ctx.path(path)))
    cells = _largest_region(ctx, ctx.land & (veg == 42), min_cells=3)  # forest-tundra
    if cells is not None:
        mid = ctx.middle(cells)
        ar = len(cells) * ctx.area
        stats = {"area_km2": round(ar), "lat": round(float(ctx.g.lat[mid]), 1),
                 "warm_month_c": round(float(L["warm_month"][cells].mean()), 1)}
        blurb = (f"The northern edge of the forest" if ctx.g.lat[mid] >= 0 else "The southern edge of the forest") + (
            f": {_area(ar)} of stunted trees in sheltered hollows and tundra between, warmest month "
            f"~{stats['warm_month_c']:.0f} °C.")
        feats.append(_feature(ctx, "treeline", f"Polar treeline: {_area(ar)} of forest-tundra", blurb, mid,
                              zoom_size(ctx.span_km(cells, mid)), stats, quality=0.5 + 0.3 * min(ar / 5e5, 1)))
    return feats


# ---------------------------------------------------------------------------
# Round 3: travel, from the July / January layers (world.seasons)
# ---------------------------------------------------------------------------
SEASON_LAYERS = ("temperature_jul", "temperature_jan", "precipitation_jul", "precipitation_jan")
TRAVEL_SPACING_KM = 800.0  # places of one travel kind at least this far apart
# beaches: summer air at sea level, monthly rain, sea surface, wave power
BEACH_T = (22.0, 34.0, 28.0)  # C: min, max, best
BEACH_SUN = (7.0, 10.0)  # h/day of bright sunshine over the summer half-year: the least, and the best
# (Algarve, Crete ~9.5-10, Miami ~9, Barbados ~7, London ~6)
BEACH_MIN_SEA = 20.0  # C, the sea next to it in summer
BEACH_WAVES = (1.0, 40.0)  # kW/m: below is a dead calm, above a storm coast (Earth's west coasts at 45-60 N)
# skiing: winter at the slopes, snow (winter rain as water), a tolerable town below
SKI_MIN_M = 1200.0
SKI_MAX_WINTER = -2.0  # C at the slopes (cell mean at its height)
SKI_MIN_SUMMER = 5.0  # C at the slopes in summer: colder (with summits above the cell mean) is permanent snow / glacier
SKI_MIN_SNOW = 300.0  # mm/yr winter-half rate: >= 150 mm of water in the winter half, ~1.5 m of snow (Colorado)
SKI_TOWN_MIN_C, SKI_TOWN_DROP = -12.0, 500.0  # the town's winter, and how far below the slopes it is
SKI_MIN_VERTICAL = 400.0  # m of snow-covered slope above the snow line or the town
# mild winters
MILD_T = (10.0, 21.0, 16.0)  # C in the winter month: min, max, best (Nice ~9, Canaries ~18)
MILD_SUN = (5.0, 7.5)  # h/day of bright sunshine over the winter half-year: the least, and the best
# (Canaries ~6-7, Florida ~7, Algarve ~5.5, Nice ~5, London ~2)
MILD_WET_MM = 150.0  # mm in the winter month: a wet winter (rain on most days) ranks lower, not out
MILD_MAX_M = 1000.0
RESORT_KM = 400.0  # beach and skiing this close make a year-round resort


def _seasons(ctx: _Ctx) -> dict | None:
    """Each cell's own summer and winter: July is summer in the north,
    January in the south. Temperatures (C, cell mean at its height) and
    monthly rain (mm, from the half-year rates). None on worlds made before
    the seasonal layers."""
    L = ctx.L
    if any(k not in L for k in SEASON_LAYERS):
        return None
    if getattr(ctx, "_sea", None) is not None:
        return ctx._sea
    north = ctx.g.lat >= 0
    tj, ta = np.asarray(L["temperature_jul"], float), np.asarray(L["temperature_jan"], float)
    pj, pa = np.asarray(L["precipitation_jul"], float), np.asarray(L["precipitation_jan"], float)
    ctx._sea = {"north": north,
                "t_sum": np.where(north, tj, ta), "t_win": np.where(north, ta, tj),
                # half-year rates (mm/yr) / 12: a typical month of that half-year
                "p_sum": np.where(north, pj, pa) / 12, "p_win": np.where(north, pa, pj) / 12,
                "rate_win": np.where(north, pa, pj)}
    return ctx._sea


def _summer(ctx: _Ctx, i: int) -> str:
    return "July" if ctx.g.lat[i] >= 0 else "January"


def _winter(ctx: _Ctx, i: int) -> str:
    return "January" if ctx.g.lat[i] >= 0 else "July"


def _nbr_mean(ctx: _Ctx, v: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mean of v over each cell's neighbours inside mask, and how many there are."""
    s, n = np.zeros(ctx.n), np.zeros(ctx.n)
    for a, b in ((ctx.a, ctx.b), (ctx.b, ctx.a)):
        m = mask[b]
        np.add.at(s, a[m], v[b[m]])
        np.add.at(n, a[m], 1)
    return s / np.maximum(n, 1), n


def _spaced(ctx: _Ctx, cand: list[tuple], top: int, km: float = TRAVEL_SPACING_KM) -> list[tuple]:
    """Best first (cand: (score, cell, ...)), each at least km from those kept."""
    kept = []
    for c in sorted(cand, key=lambda c: -c[0]):
        if all(ctx.dist(k[1], [c[1]])[0] > km for k in kept):
            kept.append(c)
        if len(kept) >= top:
            break
    return kept


def _tri(x, lo, best, hi):
    """1 at best, falling linearly to 0 at lo and hi."""
    return np.clip(np.minimum((x - lo) / max(best - lo, 1e-9), (hi - x) / max(hi - best, 1e-9)), 0, 1)


def _beach_cands(ctx: _Ctx) -> list[tuple]:
    """(quality, cell, stats) for every coast cell that makes a summer beach."""
    if getattr(ctx, "_beach", None) is not None:
        return ctx._beach
    S, L = _seasons(ctx), ctx.L
    ctx._beach = []
    if S is None or "wave_power" not in L or not ctx.land.any():
        return ctx._beach
    sea = ~ctx.land
    open_sea = np.zeros(ctx.n, bool)  # not a pond: a sea of at least 20 cells
    for cells in ctx.components(sea, min_cells=20):
        open_sea[cells] = True
    if "sunshine_jul" not in L:
        return ctx._beach
    ice = np.asarray(L["ice"], float) if "ice" in L else np.zeros(ctx.n)
    # the sea's own summer surface temperature where the world has it (sst_jul / sst_jan),
    # else the summer air over the sea
    sst_sum = (np.where(S["north"], np.asarray(L["sst_jul"], float), np.asarray(L["sst_jan"], float))
               if "sst_jul" in L and "sst_jan" in L else S["t_sum"])
    sea_t, n_sea = _nbr_mean(ctx, sst_sum, open_sea)
    wave, _ = _nbr_mean(ctx, np.asarray(L["wave_power"], float), open_sea)
    # the beach is at sea level; the cell's temperature is for its mean height
    t_beach = S["t_sum"] + LAPSE * np.maximum(ctx.elev, 0)
    rain = S["p_sum"]
    sun = np.where(S["north"], np.asarray(L["sunshine_jul"], float), np.asarray(L["sunshine_jan"], float))
    ok = (ctx.land & (n_sea > 0) & (ice <= 0) & (t_beach >= BEACH_T[0]) & (t_beach <= BEACH_T[1])
          & (sun >= BEACH_SUN[0]) & (sea_t >= BEACH_MIN_SEA) & (wave >= BEACH_WAVES[0]) & (wave <= BEACH_WAVES[1]))
    rock = np.asarray(L["surface_rock"]) if "surface_rock" in L else np.zeros(ctx.n, int)
    sed, _ = _nbr_mean(ctx, np.asarray(L.get("sediment_cover", np.zeros(ctx.n)), float), open_sea)
    for i in np.flatnonzero(ok):
        q_t = float(_tri(t_beach[i], BEACH_T[0] - 2, BEACH_T[2], BEACH_T[1] + 2))
        q_sun = 0.4 + 0.6 * float(np.clip((sun[i] - BEACH_SUN[0]) / (BEACH_SUN[1] - BEACH_SUN[0]), 0, 1))
        q_sea = float(np.clip((sea_t[i] - BEACH_MIN_SEA + 2) / 7, 0, 1))
        lw = np.log(wave[i])  # gentle-to-lively surf (5-20 kW/m) is best
        q_wave = float(np.clip(1 - 0.35 * max(np.log(5) - lw, lw - np.log(20), 0), 0.3, 1))
        sandy = bool(rock[i] in (3, 7) or sed[i] >= 0.5)  # sandstone / sediment ashore, or a sediment shelf
        q = q_t * q_sun * q_sea * q_wave * (1.15 if sandy else 1.0)
        ctx._beach.append((q, int(i), {"t_c": round(float(t_beach[i])), "sun_h": round(float(sun[i]), 1),
                                      "rain_mm": round(float(rain[i])),
                                      "sea_c": round(float(sea_t[i])), "wave_kw_m": round(float(wave[i]), 1),
                                      "sandy": sandy, "month": _summer(ctx, int(i))}))
    return ctx._beach


def _surf(kw: float) -> str:
    return "calm water" if kw < 3 else "gentle surf" if kw < 10 else "lively surf" if kw < 25 else "big surf"


def _beach_why(s: dict) -> str:
    return (f"{s['month']} {s['t_c']} °C, {s['sun_h']:.0f} h of sunshine a day, {s['rain_mm']} mm of rain, "
            f"warm sea {s['sea_c']} °C, "
            f"{_surf(s['wave_kw_m'])} ({s['wave_kw_m']:.0f} kW/m)" + (", sandy shore" if s["sandy"] else ""))


def beaches(ctx: _Ctx, top: int = 4) -> list[dict]:
    """Beach destinations: coast with a warm, sunny summer (the hemisphere's
    own: July in the north, January in the south; air at sea level, from the
    cell's mean by the lapse rate), a warm sea next to it and moderate waves
    (not a storm coast, not a dead calm); sandstone or sediment ashore or on
    the shelf is a bonus."""
    kept = _spaced(ctx, _beach_cands(ctx), top)
    best = kept[0][0] if kept else 1.0
    feats = []
    for rank, (q, i, s) in enumerate(kept):
        blurb = (f"{_beach_why(s)}. A warm, sunny summer on the coast: a beach holiday "
                 f"(like the Mediterranean or the Algarve in {s['month']}).")
        feats.append(_feature(ctx, "beach", f"Beach: {s['month']} {s['t_c']} °C, sea {s['sea_c']} °C", blurb, i, 500, s, quality=(0.85 ** rank) * (0.5 + 0.5 * q / best)))
    return feats


def _ski_cands(ctx: _Ctx) -> list[tuple]:
    """(quality, cell, stats) for every ski-country cell: slopes with a
    freezing, snowy winter and a tolerable town within two cells below."""
    if getattr(ctx, "_ski", None) is not None:
        return ctx._ski
    S, L = _seasons(ctx), ctx.L
    ctx._ski = []
    if S is None or not ctx.land.any():
        return ctx._ski
    ice = np.asarray(L["ice"], float) if "ice" in L else np.zeros(ctx.n)
    glacier = ctx.dilate(ice > 0, 1)  # an ice cap on or next to it: not a ski field
    tw, ts = S["t_win"], S["t_sum"]
    top = np.flatnonzero(ctx.land & ~glacier & (ctx.elev >= SKI_MIN_M) & (tw <= SKI_MAX_WINTER)
                         & (ts >= SKI_MIN_SUMMER) & (S["rate_win"] >= SKI_MIN_SNOW))
    if not len(top):
        return ctx._ski
    town_ok = ctx.land & (ice <= 0) & (tw >= SKI_TOWN_MIN_C)
    if "lake" in L:
        town_ok &= np.asarray(L["lake"]) == 0
    g = ctx.g
    for i in top:
        ring = {int(i)}
        for _ in range(2):  # cells within two links
            ring |= {int(j) for c in ring for j in g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]]}
        towns = [j for j in ring if town_ok[j] and ctx.elev[j] <= ctx.elev[i] - SKI_TOWN_DROP]
        if not towns:
            continue
        t = max(towns, key=lambda j: tw[j])  # the mildest town below
        # the winter snow line: where it's 0 C between the town and the slopes
        # (cell means at their heights); down to the town when the town freezes
        zt, zs = float(ctx.elev[t]), float(ctx.elev[i])
        snowline = zt if tw[t] <= 0 else zt + (zs - zt) * float(tw[t] / (tw[t] - tw[i]))
        vertical = zs - snowline
        if vertical < SKI_MIN_VERTICAL:
            continue
        snow = float(S["rate_win"][i]) / 2  # mm of water over the winter half
        q_snow = 0.4 + 0.6 * min(snow / 600, 1)
        q_vert = 0.5 + 0.5 * min(vertical / 1500, 1)
        q_town = float(np.clip((tw[t] + 14) / 14, 0.3, 1))  # 0 C and up is easy; -12 C is hard going
        q_cold = float(np.clip(1 - (-tw[i] - 15) / 15, 0.3, 1))  # colder than -15 C at the slopes is bitter
        n_high = sum(1 for j in ring if ctx.elev[j] >= SKI_MIN_M)  # a range, not a lone peak
        q_range = 0.6 + 0.4 * min(n_high / 8, 1)
        ctx._ski.append((q_snow * q_vert * q_town * q_cold * q_range, int(i),
                         {"slopes_m": int(ctx.elev[i]), "slopes_c": round(float(tw[i])), "snow_water_mm": round(snow),
                          "snowline_m": round(snowline), "snow_to_town": bool(tw[t] <= 0), "vertical_m": round(vertical),
                          "summer_c": round(float(ts[i])), "town_m": int(ctx.elev[t]), "town_c": round(float(tw[t])),
                          "town_cell": int(t), "high_cells": n_high, "month": _winter(ctx, int(i))}))
    return ctx._ski


def _ski_why(s: dict) -> str:
    line = "down to the town" if s["snow_to_town"] else f"from ~{_m(round(s['snowline_m'], -2))}"
    return (f"{s['month']} {s['slopes_c']} °C at {_m(s['slopes_m'])}, {s['snow_water_mm']} mm of winter snow "
            f"(as water, ~{s['snow_water_mm'] / 100:.1f} m of snow), snow {line}; town at {_m(s['town_m'])}, {s['town_c']} °C")


def ski_country(ctx: _Ctx, top: int = 4) -> list[dict]:
    """Ski country: ice-free mountains (>= SKI_MIN_M) whose winter (the
    hemisphere's own) is below freezing on the slopes, with good winter
    precipitation (snow), not a glaciated summit (summer above SKI_MIN_SUMMER
    there), and a town within two cells, well below, with a tolerable winter.
    Temperatures are cell means at the cell's height (the climate's lapse rate
    is in them); the snow line is where 0 C falls between the town and the
    slopes, and the skiable vertical is from it up to the slopes' height (the
    summits above the cell mean add more)."""
    kept = _spaced(ctx, _ski_cands(ctx), top)
    best = kept[0][0] if kept else 1.0
    feats = []
    for rank, (q, i, s) in enumerate(kept):
        blurb = (f"{_ski_why(s)}. Snowy mountains over a valley with a bearable winter: ski country "
                 f"(like the Alps or the Rockies), ~{_m(s['vertical_m'])} of snow-covered slope.")
        feats.append(_feature(ctx, "ski", f"Ski country: {s['month']} {s['slopes_c']} °C, ~{s['snow_water_mm'] / 100:.1f} m of snow", blurb, i, 500, s, quality=(0.85 ** rank) * (0.5 + 0.5 * q / best),
                              path=ctx.path([s["town_cell"], i])))
    return feats


def mild_winters(ctx: _Ctx, top: int = 3) -> list[dict]:
    """Winter-sun retreats: low land (< MILD_MAX_M) with a mild winter month
    (the hemisphere's own: January in the north, July in the south) and
    sunny winter days (>= MILD_SUN[0] h of bright sunshine a day over the
    winter half-year: sunshine_jan in the north, sunshine_jul in the south),
    like the Canaries, the Algarve or Florida; ranked by warmth and sunshine,
    a little lower for a wet winter, and a coast is a bonus. None on worlds
    without the sunshine layers."""
    S, L = _seasons(ctx), ctx.L
    if S is None or "sunshine_jul" not in L or not ctx.land.any():
        return []
    ice = np.asarray(L["ice"], float) if "ice" in L else np.zeros(ctx.n)
    tw, rain = S["t_win"], S["p_win"]
    sun = np.where(S["north"], np.asarray(L["sunshine_jan"], float), np.asarray(L["sunshine_jul"], float))
    ok = (ctx.land & (ice <= 0) & (ctx.elev < MILD_MAX_M) & (tw >= MILD_T[0]) & (tw <= MILD_T[1])
          & (sun >= MILD_SUN[0]))
    if "lake" in L:
        ok &= np.asarray(L["lake"]) == 0
    coast = ctx.dilate(~ctx.land) & ctx.land
    cand = []
    for i in np.flatnonzero(ok):
        q_t = float(_tri(tw[i], MILD_T[0] - 2, MILD_T[2], MILD_T[1] + 3))
        q_sun = 0.4 + 0.6 * float(np.clip((sun[i] - MILD_SUN[0]) / (MILD_SUN[1] - MILD_SUN[0]), 0, 1))
        q_wet = 1 - 0.4 * min(rain[i] / MILD_WET_MM, 1)
        cand.append((q_t * q_sun * q_wet * (1.0 if coast[i] else 0.8), int(i)))
    kept = _spaced(ctx, cand, top)
    best = kept[0][0] if kept else 1.0
    feats = []
    for rank, (q, i) in enumerate(kept):
        mon = _winter(ctx, i)
        s = {"month": mon, "winter_c": round(float(tw[i])), "sun_h": round(float(sun[i]), 1),
             "rain_mm": round(float(rain[i])), "summer_c": round(float(S["t_sum"][i])), "coast": bool(coast[i])}
        blurb = (f"{mon} {s['winter_c']} °C, {s['sun_h']:.0f} h of sunshine a day, {s['rain_mm']} mm of rain; "
                 f"summer {s['summer_c']} °C. A mild, sunny winter{' by the sea' if coast[i] else ''}: "
                 f"somewhere to spend it (like the Canaries or the Algarve).")
        feats.append(_feature(ctx, "mild_winter", f"Winter sun: {mon} {s['winter_c']} °C, {s['sun_h']:.0f} h of sunshine",
                              blurb, i, 500, s, quality=(0.85 ** rank) * (0.5 + 0.5 * q / best)))
    return feats


def year_round(ctx: _Ctx, top: int = 1) -> list[dict]:
    """Year-round resort: a beach and ski country within RESORT_KM of each
    other (summer on the coast, winter in the mountains)."""
    b, s = _beach_cands(ctx), _ski_cands(ctx)
    if not b or not s:
        return []
    sc = np.array([x[1] for x in s])
    sq = np.array([x[0] for x in s])
    cand = []
    for qb, i, sb in b:
        d = ctx.dist(i, sc)
        near = np.flatnonzero(d <= RESORT_KM)
        if not len(near):
            continue
        k = int(near[np.argmax(sq[near])])
        cand.append((float(np.sqrt(qb * sq[k])), i, sb, s[k], float(d[k])))
    kept = _spaced(ctx, cand, top, 1500)
    feats = []
    for rank, (q, i, sb, (_, j, ss), km) in enumerate(kept):
        blurb = (f"Summer on the beach: {_beach_why(sb)}. Winter skiing {_n(km)} km away: {_ski_why(ss)}.")
        feats.append(_feature(ctx, "year_round", f"Year-round resort: beach and skiing {_n(km)} km apart", blurb, i, zoom_size(km + 100),
                              {"km": round(km), "beach": sb, "ski": {k: v for k, v in ss.items() if k != "town_cell"},
                               "ski_lat": ctx.latlon(j)[0], "ski_lon": ctx.latlon(j)[1]},
                              quality=(0.85 ** rank) * (0.5 + 0.5 * min(q, 1.0)), path=ctx.path([i, j])))
    return feats


DETECTORS = [highest_peak, mountain_ranges, rivers, deltas, deepest_trench, fjords, mediterranean,
             volcanic_arcs, hotspot_islands, atolls, rifts, fastest_plate, lakes, inland_seas, ice_sheet, desert, rainforest,
             landmasses, extremes, waterfalls, canyons, salt, coral_coasts, rain_shadows, plateaus, most_varied,
             beaches, ski_country, mild_winters, year_round, great_forests, savanna, wetlands, maquis_coast, treelines]


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
# A representative moment of a run (`--at auto`)
# ---------------------------------------------------------------------------
REPRESENTATIVE_AFTER_MYR = 300.0


def representative_time(frames: list[dict], after_myr: float = REPRESENTATIVE_AFTER_MYR) -> float:
    """The keyframe time most typical of a run's mature geography: after
    `after_myr` (once the start-up has settled; the last two thirds for a
    shorter run), the frame whose land %, largest landmass % and log of the
    landmass count are jointly closest to that stretch's medians, each
    measured in its interquartile ranges. Neither the most dispersed nor the
    most assembled moment, which is what a showcase world should be."""
    end = frames[-1]["t"]
    start = after_myr if end > after_myr else end / 3
    late = [f for f in frames if f["t"] >= start] or frames[-1:]
    x = np.array([[f["stats"]["land_pct"], f["stats"]["largest_landmass_pct"],
                   np.log(1 + f["stats"]["landmasses"])] for f in late], float)
    med = np.median(x, 0)
    q1, q3 = np.percentile(x, [25, 75], 0)
    scale = np.maximum(q3 - q1, 1e-6 + 0.05 * np.abs(med))
    d = np.sqrt((((x - med) / scale) ** 2).sum(1))
    return float(late[int(np.argmin(d))]["t"])


# ---------------------------------------------------------------------------
# Cache: worlds/highlights/<world id>.json
# ---------------------------------------------------------------------------
def cache_path(world_path: Path) -> Path:
    from .store import highlights_path
    return highlights_path(world_path.stem)


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
