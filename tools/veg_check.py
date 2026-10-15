"""The vegetation model on Earth (PW-187 step 3; docs/proposals/vegetation.md section 7).

    PYTHONPATH=. uv run python tools/veg_check.py [--world dc3732] [--json out.json]

Runs planet/vegetation.py on Earth's terrain twice: on the model's own
climate (the Earth world's layers) and on the observed climate (NCEP
temperature, GPCC half-year rain, CRU sunshine for cloud; tools/earth_data.py).
The gap between the two separates vegetation errors from climate errors.
Lakes are ignored (vegetation is computed on every land cell; the L6
Earth world floods ~6 Mkm2 of flat basins, the Amazon and Congo among them).

Compared with:
  - potential natural vegetation (Ramankutty & Foley 1999, downloaded by
    earth_data.earth_potveg): area-weighted agreement of 7 groups, land
    outside Antarctica, wetlands and lakes left out;
  - published global numbers (no small, login-free gridded product exists
    for these): land NPP ~56 Pg C/yr (Field et al. 1998; MODIS MOD17 ~53),
    approximate MOD17 zonal means (Zhao et al. 2005; read off their maps, so
    only good to ~20%), potential biome areas, GFED4s burned area ~4-5
    Mkm2/yr (~70% in savannas), vegetation carbon ~450-650 Pg C, the five
    Mediterranean regions, the C3/C4 crossover (~30-35 deg, Still et al. 2003).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planet import store as S  # noqa: E402
from planet import vegetation as V  # noqa: E402
from planet import world as W  # noqa: E402
from tools.earth_data import POTVEG_CLASSES, cell_areas, earth_clouds, earth_on_grid, earth_potveg  # noqa: E402

TILT = 23.44
# comparison groups
GROUPS = ["forest/woodland", "savanna", "grassland", "shrubland", "tundra", "desert", "ice/rock", "wetland", "lake"]
_G = {k: i for i, k in enumerate(GROUPS)}


def _type_group() -> np.ndarray:
    g = np.full(len(V.TYPES), -1)
    put = {
        "forest/woodland": [1, 2, 3, 4, 5, 6, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 38, 39, 40, 41, 51],
        "savanna": [7, 8, 9, 10, 11], "grassland": [15, 31, 32, 33, 34],
        "shrubland": [19, 35, 36], "tundra": [12, 42, 43, 44, 45, 47, 48, 54],
        "desert": [13, 14, 16, 17, 59], "ice/rock": [46, 49, 57, 58], "wetland": [50, 52, 53, 55, 56], "lake": [60]}
    for k, ids in put.items():
        g[ids] = _G[k]
    return g


TYPE_GROUP = _type_group()
# Ramankutty & Foley class (1..15) -> group
POTVEG_GROUP = np.array([-1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 3, 4, 5, 6])

# approximate MOD17 zonal mean land NPP, g C/m2/yr, by 10-deg band (south edge)
NPP_ZONAL = {-60: 150, -50: 350, -40: 450, -30: 400, -20: 550, -10: 800, 0: 900, 10: 550, 20: 250, 30: 330,
             40: 420, 50: 360, 60: 220, 70: 80}
MED_BOXES = {"California": (32, 41, -124, -117), "Chile": (-38, -30, -74, -70), "Mediterranean": (30, 46, -10, 37),
             "Cape": (-35, -31, 17, 24), "SW and S Australia": (-38, -30, 114, 141)}
TARGETS = dict(npp=(45, 70), vegc=(300, 800), burned=(2, 8), forest=(55 * 0.65, 60 * 1.35),
               boreal=(12 * 0.65, 17 * 1.35), savanna=(20 * 0.65, 20 * 1.35), desert=(25 * 0.65, 30 * 1.35),
               tundra=(8 * 0.65, 11 * 1.35))


def run(grid, L, obs: dict | None):
    """The vegetation model on the Earth world's model climate, or (obs) on
    the observed one where it has data."""
    t, tw, tc = L["temperature"].astype(float), L["warm_month"].astype(float), L["cold_month"].astype(float)
    pj, pa = L["precipitation_jul"].astype(float), L["precipitation_jan"].astype(float)
    cj, ca = L["cloud_jul"] / 100.0, L["cloud_jan"] / 100.0
    if obs is not None:
        def fill(o, m):
            o = np.asarray(o, float)
            return np.where(np.isfinite(o), o, m)
        t, tw, tc = fill(obs["obs_temp"], t), fill(obs["obs_t_warm"], tw), fill(obs["obs_t_cold"], tc)
        pj, pa = fill(obs["obs_p_jul"], pj), fill(obs["obs_p_jan"], pa)
        cj = fill(np.clip((0.95 - obs["obs_sun_jul"]) / 0.9, 0, 1), cj)
        ca = fill(np.clip((0.95 - obs["obs_sun_jan"]) / 0.9, 0, 1), ca)
    return V.model(grid, L["elevation"], t, tw, tc, pj, pa, TILT, cj, ca, L["flow"], None, None, L["ice"])


def report(grid, L, v, pv, area_km2, label: str) -> dict:
    land = v["land"]
    types, sm, nu = v["types"], v["sm"], v["eq"]["nu"]
    lat, lon = grid.lat, grid.lon
    a = area_km2
    out = {"label": label}
    out["npp_pg"] = float((sm["npp"] * a * 1e6).sum() / 1e15)
    out["vegc_pg"] = float((sm["biomass"] * 100 * a * 1e6).sum() / 1e15)
    burned = v["eq"]["burned"]
    out["burned_mkm2"] = float((burned * a).sum() / 1e6)
    sav = np.isin(types, [7, 8, 9, 10, 11])
    grassy = sav | np.isin(types, [15, 31, 32, 33, 34])
    out["burned_savanna_share"] = float((burned * a)[grassy].sum() / max((burned * a).sum(), 1e-9))
    out["burned_rainforest_mkm2"] = float((burned * a)[types == 1].sum() / 1e6)
    grp = np.where(types > 0, TYPE_GROUP[types], -1)
    out["burned_by_group"] = {k: round(float((burned * a)[grp == i].sum() / 1e6), 2) for i, k in enumerate(GROUPS)}
    out["group_mkm2"] = {k: float(a[grp == i].sum() / 1e6) for i, k in enumerate(GROUPS)}
    out["forest_mkm2"] = float(a[land & (sm["tree"] >= 0.6)].sum() / 1e6)
    out["boreal_mkm2"] = float(a[np.isin(types, [37, 38, 39, 40, 41])].sum() / 1e6)
    out["savanna_grass_mkm2"] = float(a[sav].sum() / 1e6)
    out["desert_xeric_mkm2"] = float(a[np.isin(types, [13, 14, 15, 16, 17, 59])].sum() / 1e6)
    out["tundra_mkm2"] = float(a[np.isin(types, [42, 43, 44, 45, 46, 54, 47, 48, 49, 12])].sum() / 1e6)
    # agreement with potential vegetation
    obs_g = np.where(pv > 0, POTVEG_GROUP[pv], -1)
    m = land & (lat > -60) & (obs_g >= 0) & (grp >= 0) & (grp < _G["wetland"])
    out["potveg_agreement"] = float(100 * a[m][grp[m] == obs_g[m]].sum() / a[m].sum())
    conf = np.zeros((7, 7))
    np.add.at(conf, (obs_g[m], grp[m]), a[m] / 1e6)
    out["confusion_mkm2"] = conf.round(1).tolist()
    # NPP by latitude band
    zon = {}
    for s0, ref in NPP_ZONAL.items():
        b = land & (lat >= s0) & (lat < s0 + 10) & (L["ice"] <= 0)
        if b.sum() > 3:
            zon[s0] = (round(float((sm["npp"] * a)[b].sum() / a[b].sum())), ref)
    out["npp_zonal"] = zon
    # Mediterranean regions
    med = np.isin(types, [19, 20, 21])
    out["mediterranean"] = {k: int((med & (lat >= la0) & (lat <= la1) & (lon >= lo0) & (lon <= lo1)).sum())
                            for k, (la0, la1, lo0, lo1) in MED_BOXES.items()}
    # C3/C4 crossover: mean C4 share of the grasses in grassy cells, by 5 deg band
    grassy = land & (nu[V.IDX["C4G"]] + nu[V.IDX["C3G"]] >= 0.2)
    c4 = nu[V.IDX["C4G"]] / np.maximum(nu[V.IDX["C4G"]] + nu[V.IDX["C3G"]], 1e-9)
    cross = {}
    for hemi, sgn in (("N", 1), ("S", -1)):
        edge = None
        for b0 in range(0, 60, 5):
            bb = grassy & (sgn * lat >= b0) & (sgn * lat < b0 + 5)
            if bb.sum() >= 3 and c4[bb].mean() < 0.5:
                edge = b0
                break
        cross[hemi] = edge
    out["c4_crossover_lat"] = cross
    # northern treeline by 30 deg longitude sector: 95th percentile latitude of tree cover >= 10%
    tl = {}
    rf_forest = (pv >= 1) & (pv <= 8)
    for l0 in range(-180, 180, 30):
        sec = land & (lat > 45) & (lon >= l0) & (lon < l0 + 30)
        mt, ot = sec & (sm["tree"] >= 0.1), sec & rf_forest
        if mt.sum() >= 3 and ot.sum() >= 3:
            tl[l0] = (round(float(np.percentile(lat[mt], 95)), 1), round(float(np.percentile(lat[ot], 95)), 1))
    out["treeline"] = tl
    # savanna-forest boundary rain (observed annual rain) in Africa and South America
    P = 0.5 * (L["precipitation_jul"] + L["precipitation_jan"]) if "obs" not in label else v["s"]["precip"]
    sf = {}
    for name, (la0, la1, lo0, lo1) in {"Africa": (-20, 20, -20, 50), "South America": (-30, 10, -80, -35)}.items():
        box = land & (lat >= la0) & (lat <= la1) & (lon >= lo0) & (lon <= lo1)
        fo, sv = box & np.isin(types, [1, 2, 3, 4, 5, 6]), box & sav
        sf[name] = (round(float(np.median(P[fo]))) if fo.any() else None,
                    round(float(np.median(P[sv]))) if sv.any() else None)
    out["savanna_forest_rain"] = sf
    return out


def fmt(r: dict) -> str:
    lo = TARGETS
    lines = [f"## {r['label']}",
             f"  land NPP            {r['npp_pg']:6.1f} Pg C/yr      (target 45-70; obs ~56)",
             f"  vegetation carbon   {r['vegc_pg']:6.0f} Pg C         (target 300-800; obs ~450-650)",
             f"  burned area         {r['burned_mkm2']:6.1f} Mkm2/yr      (target 2-8; GFED4s ~4-5), "
             f"{100 * r['burned_savanna_share']:.0f}% in savanna and grassland (obs ~70-80%), {r['burned_rainforest_mkm2']:.2f} in rainforest",
             "  burned by group (Mkm2/yr): " + ", ".join(f"{k} {v}" for k, v in r["burned_by_group"].items() if v),
             f"  forest (trees>=60%) {r['forest_mkm2']:6.1f} Mkm2         (potential ~55-60)",
             f"  boreal forest       {r['boreal_mkm2']:6.1f} Mkm2         (~12-17)",
             f"  savanna, trop. grass{r['savanna_grass_mkm2']:6.1f} Mkm2         (~20)",
             f"  desert, xeric shrub {r['desert_xeric_mkm2']:6.1f} Mkm2         (~25-30)",
             f"  tundra (+alpine)    {r['tundra_mkm2']:6.1f} Mkm2         (~8-11)",
             f"  potential-vegetation agreement {r['potveg_agreement']:.1f}%  (target >= 60 obs climate, >= 50 model)",
             "  groups (Mkm2): " + ", ".join(f"{k} {v:.1f}" for k, v in r["group_mkm2"].items()),
             "  NPP by band (model / ~MOD17): " + ", ".join(f"{k}: {m}/{o}" for k, (m, o) in r["npp_zonal"].items()),
             "  Mediterranean cells per region: " + ", ".join(f"{k} {v}" for k, v in r["mediterranean"].items()),
             f"  C4 share < 50% from latitude (N, S): {r['c4_crossover_lat']['N']}, {r['c4_crossover_lat']['S']}"
             f"  (obs ~30-35)",
             "  treeline lat by sector (model / potveg): " + ", ".join(f"{k}: {m}/{o}" for k, (m, o) in r["treeline"].items()),
             "  median rain forest / savanna: " + ", ".join(f"{k} {f}/{s} mm" for k, (f, s) in r["savanna_forest_rain"].items()),
             "  confusion (rows potveg, cols model; Mkm2; " + "/".join(g[:4] for g in GROUPS[:7]) + "):"]
    lines += ["    " + f"{GROUPS[i][:10]:10} " + " ".join(f"{x:5.1f}" for x in row) for i, row in enumerate(r["confusion_mkm2"])]
    return "\n".join(lines)


GROUP_COLORS = ["#2f7a3a", "#c9b44a", "#b5c86a", "#9a7a5a", "#a8b0a0", "#e8d8a8", "#f0f0f0", "#4f9f8f", "#4f8fcf"]


def _rgb(hexes) -> np.ndarray:
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in hexes], np.uint8)


def maps_png(grid, L, v, pv, path: Path, width: int = 720) -> None:
    """Three maps, top to bottom: the model's comparison groups, potential
    vegetation's, and the model's named types (sea dark blue)."""
    from planet.images import write_png
    idx = W.nearest_cell_map(grid, width, width // 2)
    sea = (np.asarray(L["elevation"]) <= 0)[idx]
    gc = _rgb(GROUP_COLORS)
    grp = np.where(v["types"] > 0, TYPE_GROUP[v["types"]], -1)
    obs = np.where(pv > 0, POTVEG_GROUP[pv], -1)
    tc = _rgb([t[3] for t in V.TYPES])
    panels = []
    for arr, cols in ((grp, gc), (obs, gc), (v["types"], tc)):
        a = arr[idx]
        img = np.where((a >= 0)[..., None], cols[np.maximum(a, 0)], np.uint8(90))
        img[sea] = (29, 63, 110)
        panels.append(img.astype(np.uint8))
    write_png(path, np.concatenate(panels, 0))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--world", default=None, help="Earth world id (default: the newest Earth world)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--png", default=None, help="write maps (model groups, potential vegetation, model types) "
                                               "for the observed-climate run to this file")
    a = ap.parse_args()
    if a.world is None:
        cands = [p for p, e in S.items("world") if e.get("method") == "earth"]
        if not cands:
            raise SystemExit("no Earth world: make one with tools/earth_world.py")
        path = cands[0]
    else:
        path = S.find_world(a.world)
    w = W.load(path)
    grid, L = w["grid"], w["layers"]
    t0 = time.time()
    obs = {**earth_on_grid(grid), **earth_clouds(grid)}
    pv = earth_potveg(grid)
    area = cell_areas(grid) * 6371.0 ** 2
    res = []
    for label, o in (("model climate", None), ("observed climate", obs)):
        v = run(grid, L, o)
        res.append(report(grid, L, v, pv, area, label))
        print(fmt(res[-1]))
        if a.png and o is not None:
            maps_png(grid, L, v, pv, Path(a.png))
    print(f"(world {path.stem}, level {grid.level}; potential vegetation classes: {len(POTVEG_CLASSES)}; "
          f"{time.time() - t0:.1f}s)")
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
