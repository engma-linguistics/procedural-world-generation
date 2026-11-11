"""Coast form in a regional zoom (PW-097 stage 2, docs/proposals/coast_detail.md):
the world's coast classes (coastform.py) drawn per pixel along the zoom's own
shore, barrier islands with inlets and lagoons where the world says the coast
is a barrier coast, seabird and seal colonies as points, and hazards to ships.
A step of every `planet zoom` (and `planet coast zoom:<id>` redoes it): the
barrier islands are part of the zoom's terrain (islands(), called by zoom.build
before the rivers; PW-622); build() draws the rest as new layers, and with
--terrain also raises the spits and other shore forms out of the sea.

Per shore pixel (land with a sea pixel among its 8 neighbours), first match wins:
  ice       a glacier pixel at the shore
  fjord     the world's coast cell is a fjord coast and the land rises
            FJORD_RISE m within RISE_KM
  delta     the world's coast cell is a delta and the shore is low
  mangrove  the zoom's mangrove (coastal_life 4) within RISE_KM;  salt marsh
            (5) -> tidal flats and marsh, as are big tides (>= coastform.
            MACROTIDAL_M) on a low shore
  barrier   the shore of a lagoon behind a barrier island drawn here
  coral     a reef pixel (coastal_life 1) within REEF_KM offshore
  cliff     the land rises CLIFF_RISE m within RISE_KM, with waves (the
            nearest sea pixel's) >= coastform.CLIFF_WAVE[0] or hard rock
  rocky     hard rock (coastal.HARD_ROCKS) or a rise of ROCKY_RISE m
  beach     waves >= coastform.BEACH_WAVE;   else a sheltered low shore.
The band drawn is the shore pixel and its sea neighbours (BAND_PX).

Barrier islands (Hayes 1979; Davis & Fitzgerald 2004): where the nearest
coastal world cell's barrier score >= coastform.BAR_MIN and the mainland
shore is low, a strip of sand ISLAND_KM wide stands LAGOON_KM (planet-fixed
noise, LAGOON_KM range) off the shore, over water shallower than
BAR_DEPTH_M; tidal inlets cut it where a planet-fixed noise with patches
INLET_KM across (fewer and wider apart with small tides: Hayes 1979's
microtidal barriers are long, mesotidal ones short, "drumstick") falls
under INLET_SHARE. Layer barrier_island: 1 island, 2 lagoon, 3 inlet.
The islands are made by zoom.build as part of the terrain (islands(), PW-622: they stand ISLAND_M above
the sea, the lagoon is at most LAGOON_M deep), so its rivers, satellite view, coastal life and harbours see them.

Colonies: the shore pixels with the best cliff-or-island nesting, where
the world's seabird (seal) score >= COLONY_MIN, at least COLONY_KM apart.
nav_hazard (0/1 per sea pixel): reef pixels, water shallower than SHOAL_M
further than SHOAL_KM off the shore, barrier inlets (shifting bars).
"""

from __future__ import annotations

import json
import math
import time

import numpy as np

from .. import coastal as CL
from .. import coastform as CF
from ..geo import R_KM, latlon

RISE_KM = 2.0
FJORD_RISE = 300.0  # m within RISE_KM
CLIFF_RISE = 40.0
ROCKY_RISE = 15.0
REEF_KM = 3.0
BAND_PX = 1
LOW_M = 15.0  # m: a low mainland shore (the highest land within RISE_KM) for barriers and deltas
LAGOON_KM = (1.0, 5.0)  # km from the mainland shore to the island
ISLAND_KM = 0.8  # km: the island's width (at least a pixel)
BAR_DEPTH_M = 15.0
INLET_KM = (8.0, 25.0)  # km: patch size of the inlets' noise: mesotidal (~2 m tides) .. microtidal (~0.5 m)
INLET_SHARE = 0.12
ISLAND_M = 3.0
LAGOON_M = 4.0
COLONY_MIN = 0.3
COLONY_KM = 25.0
MAX_COLONIES = 25
SHOAL_M = 5.0
SHOAL_KM = 2.0

BARRIER_LEGEND = [{"id": 0, "key": "none", "name": "none", "color": "#00000000"},
                  {"id": 1, "key": "island", "name": "barrier island", "color": "#f4dc8c"},
                  {"id": 2, "key": "lagoon", "name": "lagoon", "color": "#56b6c8"},
                  {"id": 3, "key": "inlet", "name": "tidal inlet", "color": "#1c5f9a"}]


def _shift(a, dr, dc, fill):
    out = np.full_like(a, fill)
    ny, nx = a.shape
    out[max(dr, 0):ny + min(dr, 0), max(dc, 0):nx + min(dc, 0)] = a[max(-dr, 0):ny + min(-dr, 0),
                                                                  max(-dc, 0):nx + min(-dc, 0)]
    return out


def _dilate(m, r):
    out = m.copy()
    for _ in range(r):
        nxt = out.copy()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nxt |= _shift(out, dr, dc, False)
        out = nxt
    return out


def _distance(src, mask, res, max_km):
    """km from src pixels, through mask pixels (8-connected chamfer steps), up to max_km (inf beyond)."""
    d = np.where(src, 0.0, np.inf)
    steps = [(dr, dc, res * math.hypot(dr, dc)) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
    for _ in range(int(max_km / res) + 2):
        prev = d
        for dr, dc, w in steps:
            d = np.minimum(d, np.where(mask, _shift(prev, dr, dc, np.inf) + w, np.inf))
        d = np.where(src, 0.0, d)
        if np.array_equal(prev, d):
            break
    return np.where(d <= max_km, d, np.inf)


def _pixel_cells(meta, grid):
    """Planet-fixed points (km) of each pixel, and its nearest world cell."""
    from .regional import frame_of
    nx, ny, res = meta["nx"], meta["ny"], meta["res_km"]
    fr = frame_of(meta["center"])
    c, r = np.meshgrid(np.arange(nx), np.arange(ny))
    x, y = (c.ravel() + 0.5 - nx / 2) * res, (ny / 2 - r.ravel() - 0.5) * res
    P = fr.to_sphere(x, y)
    return np.ascontiguousarray(P * R_KM), grid.locate(P), fr


def _coast_value(grid, near, v, cells):
    """The value of v at the nearest coastal world cell: the pixel's cell if coastal, else the
    best of its coastal neighbours (0 where none)."""
    v = np.where(near, np.asarray(v, float), -np.inf)
    best = np.maximum.reduceat(v[grid.nbr_idx], grid.nbr_off[:-1])
    out = np.where(near, v, best)
    out = np.where(np.isfinite(out), out, 0.0)
    return out[cells]


def _coast_class(grid, ct, cells):
    """The class of the nearest coastal world cell (the pixel's, or its first coastal neighbour's)."""
    ct = np.asarray(ct)
    first = np.zeros(grid.n, ct.dtype)
    for i in range(grid.n):  # (small: L6-L7 grids, once per zoom)
        if ct[i]:
            first[i] = ct[i]
            continue
        nb = grid.nbr_idx[grid.nbr_off[i]:grid.nbr_off[i + 1]]
        hit = nb[ct[nb] > 0]
        first[i] = ct[hit[0]] if len(hit) else 0
    return first[cells]


def inlet_spacing(tide_mean: float) -> float:
    """km between tidal inlets: fewer and wider apart with small tides (Hayes 1979)."""
    return float(np.interp(tide_mean, [0.5, 2.0], INLET_KM[::-1]))


def islands(world: dict, Pk: np.ndarray, P: np.ndarray, ind: np.ndarray, e_land: np.ndarray,
            e_sea: np.ndarray, taken: np.ndarray, sel: np.ndarray, nx: int, ny: int, res: float, seed: int) -> dict:
    """Barrier islands for zoom.build's coastline (PW-622), before the terrain, rivers, coastal life and harbours are
    made, so they all see them: off the low shores of the world's barrier coasts (coastform.BAR_MIN), a strip of sand
    ISLAND_KM wide stands LAGOON_KM off the mainland over shallow water, tidal inlets cut it; the lagoon is the
    shallow sea behind. ind: the coast indicator (> 0 land) flat over the built area (halo included), e_land / e_sea
    the interpolated coarse heights, taken: pixels the delta and coastal-plain barriers already use, sel: the coarse
    cells around (their mean tide sets how far apart the inlets lie).
    Returns {"island", "lagoon", "inlet"}: flat bool arrays."""
    from .coastal import _uniform, window_max
    g, L = world["grid"], world["layers"]
    none = np.zeros(nx * ny, bool)
    if "barrier" not in L:  # (a world without coast layers, e.g. a hand-made test world: no coast data, no islands)
        return {"island": none, "lagoon": none, "inlet": none}
    s = CF.scores(g, L, world["meta"])
    cells = g.locate(P)
    bar_w = _coast_value(g, s["near"], s["barrier"], cells).reshape(ny, nx)
    if not (bar_w >= CF.BAR_MIN).any():
        return {"island": none, "lagoon": none, "inlet": none}
    land = (ind > 0).reshape(ny, nx)
    sea = ~land
    shore = land & _dilate(sea, 1)
    r_px = max(1, int(round(RISE_KM / res)))
    low = window_max(np.where(land, e_land.reshape(ny, nx), -np.inf), r_px) < LOW_M
    taken = _dilate(taken.reshape(ny, nx), max(1, int(round(LAGOON_KM[1] / res))))
    d_land = _distance(land, sea, res, LAGOON_KM[1] + ISLAND_KM + 2 * res)
    u = _uniform(Pk, 30.0, res, seed + 71).reshape(ny, nx)
    d0 = np.maximum(LAGOON_KM[0] + u * (LAGOON_KM[1] - LAGOON_KM[0]), res)
    w = max(ISLAND_KM, 1.5 * res)  # (1.5 pixels: a diagonal strip stays connected)
    low_shore = _dilate(shore & low & (bar_w >= CF.BAR_MIN) & ~taken, int(math.ceil((LAGOON_KM[1] + w) / res)) + 1)
    depth = np.where(sea, -e_sea.reshape(ny, nx), 0.0)
    band = sea & low_shore & ~taken & (d_land > d0) & (d_land <= d0 + w) & (depth < BAR_DEPTH_M)
    tide = np.asarray(L["tide_range"], float)[sel]
    sea_c = np.asarray(L["elevation"])[sel] <= 0
    inlet_km = inlet_spacing(float(tide[sea_c].mean()) if sea_c.any() else 1.0)
    v = _uniform(Pk, inlet_km, res, seed + 72).reshape(ny, nx)
    inlet = band & (v < INLET_SHARE)
    island = band & ~inlet
    lagoon = sea & low_shore & ~taken & (d_land <= d0) & _dilate(island, int(math.ceil(LAGOON_KM[1] / res)))
    return {"island": island.ravel(), "lagoon": lagoon.ravel(), "inlet": inlet.ravel(), "u": u.ravel()}


def build(world: dict, meta: dict, lay: dict, terrain: bool = False, seed: int | None = None) -> dict:
    """The zoom's coast layers (flat arrays are (ny, nx) here) and its point features. lay: the zoom's
    layers decoded (elevation, water, coastal_life, wave_power, tide_range, surface_rock or rock, ice)."""
    from .coastal import _uniform, window_max
    g, L = world["grid"], world["layers"]
    if "coast_type" not in L:
        L.update(CF.world_layers(g, L, world["meta"]))
    s = CF.scores(g, L, world["meta"])
    res = float(meta["res_km"])
    seed = int(meta.get("seed", 1) if seed is None else seed)
    h = np.asarray(lay["elevation"], float)
    ny, nx = h.shape
    water = np.asarray(lay["water"])
    sea = water == 1
    land = water == 0
    ice = np.asarray(lay.get("ice", np.zeros_like(h)), float) > 0
    life = np.asarray(lay.get("coastal_life", np.zeros_like(h, np.uint8)))
    wave = np.asarray(lay.get("wave_power", np.zeros_like(h)), float)
    tide = np.asarray(lay.get("tide_range", np.zeros_like(h)), float)
    rock = np.asarray(lay.get("surface_rock", lay.get("rock", np.zeros_like(h, np.uint8))))
    Pk, cells, fr = _pixel_cells(meta, g)
    near = s["near"]
    bar_w = _coast_value(g, near, s["barrier"], cells).reshape(ny, nx)
    birds_w = _coast_value(g, near, L["seabirds"], cells).reshape(ny, nx)
    seals_w = _coast_value(g, near, L["seals"], cells).reshape(ny, nx)
    cls_w = _coast_class(g, L["coast_type"], cells).reshape(ny, nx)
    # the shore and what stands behind it
    sea_nb = _dilate(sea, 1)
    shore = land & sea_nb
    r_px = max(1, int(round(RISE_KM / res)))
    rise = window_max(np.where(land, h, -np.inf), r_px) - np.maximum(h, 0)
    wave_sea = window_max(np.where(sea, wave, -np.inf), max(1, int(round(1.0 / res))))
    wave_sea = np.where(np.isfinite(wave_sea), wave_sea, 0.0)
    tide_sea = window_max(np.where(sea, tide, -np.inf), max(1, int(round(1.0 / res))))
    tide_sea = np.where(np.isfinite(tide_sea), tide_sea, 0.0)
    hard = np.isin(rock, CL.HARD_ROCKS)
    reef_near = _dilate(life == 1, max(1, int(round(REEF_KM / res))))
    mang_near = _dilate(life == 4, r_px)
    marsh_near = _dilate(life == 5, r_px)
    low = window_max(np.where(land, h, -np.inf), r_px) < LOW_M
    depth = np.where(sea, -h, 0.0)
    # barrier islands: drawn into the terrain by zoom.build (islands(), PW-622); here they are the layer it left
    bi = np.asarray(lay["barrier_island"], np.uint8) if "barrier_island" in lay else np.zeros((ny, nx), np.uint8)
    island, lagoon, inlet = bi == 1, bi == 2, bi == 3
    inlet_km = inlet_spacing(float(np.mean(tide[sea])) if sea.any() else 1.0)
    lagoon_shore = shore & _dilate(lagoon, 1)
    # the shore's class
    ct = np.zeros((ny, nx), np.uint8)
    rules = [
        (CF.ICE, ice),
        (CF.FJORD, (cls_w == CF.FJORD) & (rise >= FJORD_RISE)),
        (CF.DELTA, (cls_w == CF.DELTA) & low),
        (CF.MANGROVE, mang_near),
        (CF.TIDAL, marsh_near | ((tide_sea >= CF.MACROTIDAL_M) & low)),
        (CF.BARRIER, lagoon_shore),
        (CF.CORAL, reef_near),
        (CF.CLIFF, (rise >= CLIFF_RISE) & ((wave_sea >= CF.CLIFF_WAVE[0]) | hard)),
        (CF.ROCKY, hard | (rise >= ROCKY_RISE)),
        (CF.BEACH, wave_sea >= CF.BEACH_WAVE),
        (CF.LOW, np.ones_like(shore)),
    ]
    free = shore.copy()
    for cid, m in rules:
        hit = free & m
        ct[hit] = cid
        free &= ~hit
    ct[island] = CF.BARRIER  # (the islands' own sea-facing beaches)
    # a band for the eye: the class spread onto the sea pixels next to the shore
    band_ct = ct.copy()
    for _ in range(BAND_PX):
        grow = band_ct.copy()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = _shift(band_ct, dr, dc, 0)
            take = (grow == 0) & (sh > 0) & sea & (bi == 0)
            grow[take] = sh[take]
        band_ct = grow
    # colonies: the best nesting shore pixels (cliffs, islands) of the world's colony coasts
    ri = np.flatnonzero(island.ravel())
    nest = (np.where(ct == CF.CLIFF, 1.0, np.where(ct == CF.ROCKY, 0.5, 0.2))
            + 0.5 * np.clip(rise / 200.0, 0, 1)).ravel()
    feats = []
    for kind, sw in (("seabird colony", birds_w), ("seal haul-out", seals_w)):
        score = np.where(shore.ravel() | np.isin(np.arange(nx * ny), ri), sw.ravel() * nest, 0.0)
        picked = []
        for i in np.argsort(-score):
            if score[i] < COLONY_MIN or len(picked) >= MAX_COLONIES:
                break
            r, c = divmod(int(i), nx)
            if all(math.hypot(r - pr, c - pc) * res >= COLONY_KM for pr, pc in picked):
                picked.append((r, c))
                lat, lon = latlon(Pk[i] / R_KM)
                feats.append({"kind": kind, "px": [r, c], "lat": round(float(lat), 4), "lon": round(float(lon), 4),
                              "score": round(float(score[i]), 2), "coast": CF.CLASSES[int(ct.ravel()[i])][2]})
    # hazards to ships
    d_shore = _distance(land, sea, res, SHOAL_KM + res)
    hazard = sea & ((life == 1) | ((depth < SHOAL_M) & ~np.isfinite(d_shore)) | (bi == 3))
    out = {"coast_type": band_ct, "barrier_island": bi, "nav_hazard": hazard.astype(np.uint8)}
    # spits, beach ridges, tidal channels, drowned reefs (zoom/shoreforms.py, PW-621)
    from . import shoreforms as SF
    ctx = {"land": land, "sea": sea, "shore": shore, "h": h, "res": res, "ct": ct, "Pk": Pk, "cells": cells,
           "wave_sea": wave_sea, "tide_sea": tide_sea, "rise": rise, "hard": hard,
           "uniform": lambda km, sd: _uniform(Pk, km, res, sd).reshape(ny, nx)}
    sf = SF.build(world, meta, lay, ctx, terrain=terrain, seed=seed)
    out["shore_form"] = sf["shore_form"]
    feats += sf["features"]
    if terrain:
        h2 = h.copy()
        w2 = water.copy()
        if sf["terrain"] is not None:  # (spits raised out of the sea)
            m, z = sf["terrain"]
            h2[m] = np.maximum(h2[m], z[m])
            w2[m] = 0
        out["elevation"], out["water"] = h2.astype(np.float32), w2
    km = {CF.CLASSES[cid][1]: round(float((ct == cid).sum() * res), 1) for cid in range(1, len(CF.CLASSES))
          if (ct == cid).any()}
    stats = {"shore_km": km, "barrier_islands_km2": round(float(island.sum() * res * res), 1),
             "lagoons_km2": round(float(lagoon.sum() * res * res), 1), "inlets": int(_count_blobs(inlet)),
             "inlet_spacing_km": round(inlet_km, 1), "hazard_km2": round(float(hazard.sum() * res * res), 1),
             "terrain": bool(terrain), "forms": sf["stats"]}
    return {"layers": out, "features": feats, "stats": stats}


def _count_blobs(m):
    """Connected (4-neighbour) groups of True pixels."""
    lab = np.where(m, np.arange(m.size).reshape(m.shape), -1)
    while True:
        prev = lab
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            lab = np.where(m, np.maximum(lab, _shift(lab, dr, dc, -1)), -1)
        if np.array_equal(prev, lab):
            break
    return len(np.unique(lab[m]))


LAYER_SPECS = {
    "coast_type": {"dtype": "u1", "units": "id", "description": "coast form along the shore (coastform.CLASSES; "
                                                                 "legend 'coast'): the shore pixels and the sea next to them"},
    "barrier_island": {"dtype": "u1", "units": "enum", "description": "1 barrier island, 2 lagoon, 3 tidal inlet "
                                                                      "(zoom/coast.py)"},
    "nav_hazard": {"dtype": "u1", "units": "0/1", "description": "hazard to ships: reefs, shoals off the shore, "
                                                                 "barrier inlets"},
    "shore_form": {"dtype": "u1", "units": "enum", "description": "1 spit, 2 beach-ridge plain, 3 tidal channel, "
                                                                 "4 tidal flat, 5 drowned reef (zoom/shoreforms.py)"},
}


def add_to_zoom(ref, terrain: bool = False, world: dict | None = None):
    """(Re)makes a saved zoom's coast layers in place; with terrain, also its elevation and water."""
    from .. import store as S
    from .. import world as W
    from . import regional as Z
    d = S.find_zoom(ref)
    meta, lay = Z.load(d, decode=True, mmap=False)  # (it rewrites layer files: none may be mapped, PW-1760)
    w = world or W.load(S.find_world(meta["source_world"]["id"]))
    r = build(w, meta, lay, terrain=terrain)
    new = r["layers"]
    specs = {k: LAYER_SPECS[k] for k in new if k in LAYER_SPECS}
    meta["layers"].update(S.write_layers(d, {k: S.encode(new[k], specs[k]) for k in specs}, specs))
    if terrain:  # (the zoom's own encodings for the terrain it already had)
        for k in ("elevation", "water"):
            spec = meta["layers"][k]
            meta["layers"].update(S.write_layers(d, {k: S.encode(new[k], spec)}, {k: spec}))
    meta.setdefault("legend", {})["coast"] = CF.legend()
    meta["legend"]["barrier_island"] = BARRIER_LEGEND
    from .shoreforms import LEGEND as SHORE_FORM_LEGEND
    meta["legend"]["shore_form"] = SHORE_FORM_LEGEND
    meta["coast"] = {"features": r["features"], "stats": r["stats"], "created": time.strftime("%Y-%m-%d %H:%M:%S")}
    S.write_atomic(d / "zoom.json", json.dumps(meta, indent=1))
    return d


def text_lines(c: dict) -> list[str]:
    s = c["stats"]
    out = ["coast (zoom/coast.py, PW-097): " + ", ".join(f"{k} {v:g} km" for k, v in
                                                         sorted(s["shore_km"].items(), key=lambda kv: -kv[1]))]
    out.append(f"  barrier islands {s['barrier_islands_km2']:g} km2, lagoons {s['lagoons_km2']:g} km2, "
               f"{s['inlets']} inlets (~{s['inlet_spacing_km']:g} km apart); hazards {s['hazard_km2']:g} km2"
               + "; the islands are part of the zoom's terrain")
    fm = s.get("forms")
    if fm:
        out.append(f"  shore forms: {fm['spits']} spits ({fm['spit_km']:g} km), beach ridges {fm['beach_ridges_km2']:g} km2, "
                   f"tidal flats {fm['tidal_flats_km2']:g} km2 with {fm['tidal_channels_km2']:g} km2 of channels, "
                   f"drowned reefs {fm['drowned_reefs_km2']:g} km2 (lowstand {fm['lowstand_m']:g} m)")
    for f in [f for f in c["features"] if f["kind"] != "spit"][:8]:
        out.append(f"  {f['kind']} at {f['lat']:.2f}, {f['lon']:.2f} ({f['coast']}, {f['score']:.2f})")
    return out
