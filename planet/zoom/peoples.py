"""Peoples change the land, on a regional zoom (PW-667): a peoples run's cleared land at the zoom's pixels.

An optional overlay step on a zoom of a world that has a peoples run (`planet zoom ... --peoples RUN`): the run's
anthropogenic layers (landuse.py: cell fractions of cropland, pasture, burned grass, managed woods, and the people
per km2) are interpolated to the zoom's pixels and turned into land use there, then the plants follow:

    land_use (uint8)   0 wild   1 cropland   2 pasture   3 burned grass   4 managed woods   5 settlement

Where each use goes, inside every coarse cell (so each cell keeps the run's share of its land):
    cropland     the best arable ground first: the pixel's farmland score, flat ground, nearness to a river (a
                 floodplain), and a patchy noise (so fields lie in patches, not as speckle); not on steep ground
    settlement   one village (VILLAGE_PEOPLE) to a pixel, at water, on a harbour, near a pass, on flat fertile ground
    pasture      open, gentle ground round the fields (and where the noise opens woodland up)
    burned grass the wooded ground left, in large fire patches
    managed      woods near the settled and farmed country (and rivers), thinned by landuse.THIN, stand age reset
and the plant fractions (nu) of the pixel follow: fields take trees and shrubs out for crop grass, pasture and burned
ground lose most trees and keep grass, managed woods lose 30% of the canopy, a village is mostly bare ground; tree
cover, plant cover, leaf area, npp, canopy height, fire return, the named vegetation type and the biome with them.
The satellite colours show fields, pasture, burned ground and villages (satellite.py, from `land_use`).

Nothing here is read unless a zoom is made with a peoples run, so zooms without one are untouched.

    load(run_ref, world_id)  -> the run's overlay (cell fractions)
    apply(world, fr, nx, ny, res, size_km, A, lay, nu) -> the changed plants and the land_use layer
"""

from __future__ import annotations

import json

import numpy as np

from .. import store as S
from .. import vegetation as V
from . import kernels as ZK
from . import vegetation as ZVG
from ..geo import R_KM
from ..lineages import landuse as LU

CROP, PASTURE, BURNED, MANAGED, TOWN = 1, 2, 3, 4, 5
NAMES = ("wild", "cropland", "pasture", "burned grass", "managed woods", "settlement")
COLOURS = ("#000000", "#e0b13a", "#b9d36a", "#c98a3c", "#2d6a4a", "#9c3b2a")
VILLAGE_PEOPLE = 1000.0  # people to a village (one pixel of settlement: a big village or small market town)
TOWN_MAX = 0.03  # the most of a cell's land that is village ground
MIN_DENSITY = 0.3  # people/km2 under which nobody lives: no settlements
SLOPE_CROP = 0.18  # tan(slope) above which nothing is ploughed (~10 degrees)
SLOPE_PASTURE = 0.45
FERT_MIN = 0.12  # farmland score (0..1) under which there is no field
TREE_FELLED = {CROP: 0.97, PASTURE: 0.80, BURNED: 0.90, TOWN: 0.95}  # the share of the trees a use takes out
SHRUB_FELLED = {CROP: 0.90, PASTURE: 0.40, BURNED: 0.70, TOWN: 0.95}
FIELD_COVER = 0.80  # plant cover of a field over the year (crops, stubble and bare earth between)
TOWN_COVER = 0.25


def load(run_ref: str, world_id: str | None = None) -> dict:
    """The overlay of a peoples run: {id, name, world, layers: crop, pasture, burned, managed (0..1 per cell), people
    (per km2), summary}. Raises when the run has none (planet landuse RUN) or belongs to another world."""
    d = S.find("run", run_ref)
    run = json.loads((d / "run.json").read_text())
    m = run["meta"]
    a = m.get("anthro")
    if run.get("kind") != "peoples" or not a:
        raise SystemExit(f"{d.name}: not a peoples run with a land-use overlay (planet landuse {d.name})")
    if world_id is not None and m.get("world") != world_id:
        raise SystemExit(f"peoples run {d.name} belongs to world {m.get('world')}, not {world_id}")
    out = {}
    for k in ("crop", "pasture", "burned", "managed", "people"):
        s = a["layers"][k]
        raw = np.fromfile(d / s["file"], np.uint8).astype(float)
        out[k] = 2 ** (raw * s["scale"]) - 1 if k == "people" else raw / 100.0
    return {"id": d.name, "name": run.get("name"), "world": m.get("world"), "layers": out, "summary": a["summary"],
            "cells": m["cells"]}


def _rank(score, mask, own):
    """Each masked pixel's rank among the masked pixels of its coarse cell, as (rank + 0.5) / count, and that count
    (2 and 0 off the mask)."""
    n = len(score)
    pct, cnt = np.full(n, 2.0), np.zeros(n)
    idx = np.flatnonzero(mask)
    if not len(idx):
        return pct, cnt
    order = np.lexsort((score[idx], own[idx]))
    o = idx[order]
    co = own[o]
    starts = np.r_[0, np.flatnonzero(np.diff(co)) + 1]
    sizes = np.diff(np.r_[starts, len(o)])
    first = np.repeat(starts, sizes)
    c = np.repeat(sizes, sizes)
    pct[o] = (np.arange(len(o)) - first + 0.5) / c
    cnt[o] = c
    return pct, cnt


def _blur(a, ny, nx, k):
    """Mean over a (2k+1)^2 window (edges repeated), a (ny*nx,)."""
    a = a.reshape(ny, nx)
    p = np.pad(a, k, mode="edge")
    c = np.cumsum(np.cumsum(np.pad(p, ((1, 0), (1, 0))), 0), 1)
    w = 2 * k + 1
    s = c[w:, w:] - c[:-w, w:] - c[w:, :-w] + c[:-w, :-w]
    return (s / (w * w)).ravel()


def _select(score, ok, own, frac, n_land):
    """The pixels of each coarse cell that take `frac` (the run's share of the cell's land, per pixel) of its land,
    best score first among the ok pixels (all of them if there are fewer)."""
    pct, cnt = _rank(-score, ok, own)
    return ok & (pct < frac * n_land / np.maximum(cnt, 1))


def apply(world: dict, fr, nx: int, ny: int, res: float, size_km: float, A: dict, lay: dict, nu: np.ndarray,
          seed: int = 1) -> dict:
    """The zoom's plants under the peoples of overlay A. lay: flat (nx*ny) arrays of the wild zoom: elevation (m, the
    ground), water (0 land, 1 sea, 2 lake), ice, discharge, temperature, fertile_score (0..1), harbour, pass,
    river_dist (px), coast_dist (px), and the vegetation's vegetation, tree_cover (%), plant_cover (%), lai,
    canopy_height, npp, fire_return, biome; nu (NP, nx*ny): the wild plant fractions (zero off the vegetated land).
    Returns {nu, layers: the changed layers, land_use, stats}."""
    n = nx * ny
    g, L = world["grid"], world["layers"]
    sp = g.spacing * R_KM
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    px, py = X.ravel(), Y.ravel()
    P = fr.to_sphere(px, py)
    own = g.locate(P)
    sel = ZVG._sel(g, fr, size_km)
    cx, cy = fr.to_plane(g.centers[sel])
    ice_c = np.asarray(L.get("ice", np.zeros(g.n)), float)[sel] > 0
    land_c = (np.asarray(L["elevation"], float)[sel] > 0) & ~ice_c
    vals = np.column_stack([A["layers"][k][sel] for k in ("crop", "pasture", "burned", "managed", "people")])
    f, _ = ZK.gauss_interp(px, py, cx, cy, vals, np.repeat(land_c[:, None].astype(float), 5, 1), 0.5 * sp)
    f = np.nan_to_num(f, nan=0.0)
    f_crop, f_pas, f_bur, f_man = (np.clip(f[:, k], 0, 1) for k in range(4))
    dens = np.maximum(f[:, 4], 0)

    water, ice = np.asarray(lay["water"]), np.asarray(lay["ice"], float)
    h = np.asarray(lay["elevation"], float)
    ok = (water == 0) & (ice <= 0) & (nu.sum(0) > 0)  # (vegetated land)
    gy, gx = np.gradient(np.where(water == 0, h, 0.0).reshape(ny, nx), res * 1000.0)
    slope = np.hypot(gx, gy).ravel()
    flat = np.clip(1 - slope / 0.12, 0, 1)
    fert = np.asarray(lay["fertile_score"], float)  # 0..1 (humanuse.py)
    rd = np.minimum(np.asarray(lay["river_dist"], float), 255) * res
    river = np.exp(-rd / 6.0)
    Pk = np.ascontiguousarray(P * R_KM)
    S0 = int(seed) * 1_000_003 + 51

    def noise(km, k):
        return ZVG._uniform(ZK.fbm(Pk, km, max(1, int(np.ceil(np.log2(km / (2 * res)))) + 1), 0.55, S0 + k) / 0.17)

    n_land = np.bincount(own[ok], minlength=g.n)[own].astype(float)  # (each pixel's cell's vegetated land, px)
    wild_tc = np.asarray(lay["tree_cover"], float) / 100.0

    # cropland: the best arable ground first
    ok_crop = ok & (slope < SLOPE_CROP) & (fert >= FERT_MIN)
    k1 = max(1, int(round(2.0 / res)))
    s_crop = _blur(0.45 * fert + 0.25 * flat + 0.15 * river, ny, nx, k1) + 0.15 * noise(12.0, 1)
    crop = _select(s_crop, ok_crop, own, f_crop, n_land)
    # settlements: a village to VILLAGE_PEOPLE, at water, harbours and passes, on flat fertile ground
    harb = _blur((np.asarray(lay["harbour"]) > 0).astype(float), ny, nx, max(1, int(round(3.0 / res)))) > 0
    passes = _blur((np.asarray(lay["pass"]) > 0).astype(float), ny, nx, max(1, int(round(4.0 / res)))) > 0
    coast = (np.asarray(lay["coast_dist"], float) * res <= 4.0) & harb
    site = 0.15 + 2.0 * np.exp(-rd / 2.5) + 1.0 * coast + 0.5 * passes + 0.8 * flat * fert
    people_px = dens * res * res  # (people on each pixel)
    n_vil = np.bincount(own, np.where(ok, people_px, 0.0), minlength=g.n)[own] / VILLAGE_PEOPLE
    ok_town = ok & (dens >= MIN_DENSITY) & (slope < 0.3)
    w_sum = np.bincount(own[ok_town], site[ok_town], minlength=g.n)[own]
    cap = np.minimum(n_vil, TOWN_MAX * n_land)
    # (a village at random, more likely at a good site: a scatter of dots, not a ribbon along every river; drawn
    # without replacement, weighted by site (key u^(1/w)), so the weights hold where villages fill most of the room)
    rnd = np.random.default_rng(S0 + 7).random(n)
    key = np.log(np.maximum(rnd, 1e-300)) / site
    town = _select(key, ok_town, own, cap / np.maximum(n_land, 1.0), n_land)
    # pasture: open gentle ground round the fields
    near_f = _blur((crop | town).astype(float), ny, nx, max(1, int(round(8.0 / res))))
    rest = ok & ~crop & ~town
    s_pas = 0.30 * flat + 0.50 * near_f + 0.20 * noise(8.0, 3)
    pas = _select(s_pas, rest & (slope < SLOPE_PASTURE), own, f_pas, n_land)
    # burned grass: fire patches in the woods that are left
    rest2 = rest & ~pas & (wild_tc >= 0.2)
    bur = _select(noise(18.0, 4) + 0.2 * flat, rest2, own, f_bur, n_land)
    # managed woods: near the settled and farmed country and rivers
    near_s = _blur((crop | town | pas).astype(float), ny, nx, max(1, int(round(6.0 / res))))
    rest3 = rest2 & ~bur
    man = _select(0.5 * near_s + 0.25 * river + 0.25 * noise(8.0, 5), rest3, own, f_man, n_land)

    lu = np.zeros(n, np.uint8)
    for code, m in ((MANAGED, man), (BURNED, bur), (PASTURE, pas), (CROP, crop), (TOWN, town)):
        lu[m] = code

    # --- the plants follow
    tr, sh, he = V.TREES, V.SHRUBS, V.HERBS
    nt0, ns0 = nu[tr].sum(0), nu[sh].sum(0)
    keep_t, keep_s = np.ones(n), np.ones(n)
    for code in (CROP, PASTURE, BURNED, TOWN):
        keep_t = np.where(lu == code, 1 - TREE_FELLED[code], keep_t)
        keep_s = np.where(lu == code, 1 - SHRUB_FELLED[code], keep_s)
    keep_t = np.where(lu == MANAGED, 1 - LU.THIN, keep_t)
    new = nu.copy()
    new[tr] = nu[tr] * keep_t
    new[sh] = nu[sh] * keep_s
    freed = (nt0 - new[tr].sum(0)) + (ns0 - new[sh].sum(0))
    hs = nu[he].sum(0)
    c3, c4 = V.IDX["C3G"], V.IDX["C4G"]
    warm = np.asarray(lay["temperature"], float) >= 18
    herb_share = nu[he] / np.maximum(hs, 1e-9)
    add = np.zeros_like(nu)
    add[he] = herb_share * freed
    none = hs <= 1e-9
    add[c4] += np.where(none & warm, freed, 0.0)
    add[c3] += np.where(none & ~warm, freed, 0.0)
    new = new + add
    new[:, lu == TOWN] *= 0.25  # (a village: mostly bare ground, yards and gardens)
    tot = new.sum(0)
    new = np.where(tot > 1, new / np.maximum(tot, 1e-9), new)
    nt1 = new[tr].sum(0)

    # --- the summary layers
    tc0 = wild_tc
    ratio = np.where(nt0 > 1e-9, nt1 / np.maximum(nt0, 1e-9), 1.0)
    tc1 = tc0 * ratio
    pc0 = np.asarray(lay["plant_cover"], float) / 100.0
    lost = tc0 - tc1
    pc1 = np.where(lu == CROP, FIELD_COVER, np.where(lu == TOWN, np.minimum(pc0, TOWN_COVER), np.clip(pc0 - 0.5 * lost, 0, 1)))
    pc1 = np.where(ok, pc1, pc0)
    lost_frac = np.where(tc0 > 1e-6, lost / np.maximum(tc0, 1e-6), 0.0)
    lai1 = np.asarray(lay["lai"], float) * (1 - 0.7 * lost_frac)
    lai1 = np.where(lu == CROP, 2.0, np.where(lu == TOWN, 0.5, lai1))
    npp1 = np.asarray(lay["npp"], float) * (1 - 0.35 * lost_frac)
    ch0 = np.asarray(lay["canopy_height"], float)
    ch1 = np.where(lu == MANAGED, ch0 * 0.55, ch0)
    ch1 = np.where((tc1 < 0.10) & (ch0 > 0) & (lu > 0), np.where(lu == CROP, 1.0, 0.5), ch1)
    fr1 = np.asarray(lay["fire_return"], float)
    fr1 = np.where(lu == BURNED, 3.0, np.where((lu == CROP) | (lu == TOWN), 0.0, fr1))
    # the named type: where the woods are gone, the open type of that climate
    veg0 = np.asarray(lay["vegetation"]).astype(int)
    group = np.array([t[2] for t in V.TYPES])[veg0]
    wooded = np.isin(group, ("tropical forest", "tropical woodland", "warm temperate", "temperate forest",
                             "temperate woodland", "Mediterranean", "savanna"))
    trop = np.isin(group, ("tropical forest", "tropical woodland", "savanna"))
    dry = np.asarray(lay["precipitation"], float) < 450
    tg, med = V.T["tropical grassland"], V.T["Mediterranean scrub (maquis, chaparral, fynbos)"]
    park = np.where(trop, V.T["moist savanna woodland"], V.T["temperate woodland and parkland"])
    grass = np.where(trop, tg, np.where(group == "Mediterranean", med, np.where(dry, V.T["short-grass steppe"], V.T["tall-grass prairie"])))
    opened = ok & wooded & (lu > 0) & (lu != MANAGED) & (tc0 >= 0.1)
    veg1 = np.where(opened & (tc1 < 0.10), grass, np.where(opened & (tc1 < 0.35 * tc0), park, veg0))
    layers = {"vegetation": veg1.astype(np.uint8), "tree_cover": 100 * tc1, "plant_cover": 100 * pc1, "lai": lai1,
              "canopy_height": ch1, "npp": npp1, "fire_return": fr1}
    layers = {k: np.where(ok, v, np.asarray(lay[k], float)).astype(np.asarray(lay[k]).dtype) for k, v in layers.items()}

    a_km2 = res * res
    land_px = max(int(ok.sum()), 1)
    st = {"run": A["id"], "world": A["world"]}
    for code, nm in zip(range(1, 6), NAMES[1:]):
        st[nm.replace(" ", "_") + "_km2"] = round(float((lu == code).sum() * a_km2), 1)
    st["tree_cover_mean_before_pct"] = round(100 * float(tc0[ok].mean()), 2) if ok.any() else 0.0
    st["tree_cover_mean_after_pct"] = round(100 * float(tc1[ok].mean()), 2) if ok.any() else 0.0
    st["people"] = int(people_px[ok].sum())
    st["cropland_pct_of_land"] = round(100 * float((lu == CROP).sum()) / land_px, 2)
    return {"nu": new, "layers": layers, "land_use": lu, "stats": st}


def legend() -> list:
    return [{"id": i, "name": NAMES[i], "color": COLOURS[i]} for i in range(len(NAMES))]
