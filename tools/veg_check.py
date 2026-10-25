"""The vegetation model on Earth (PW-187 step 3; docs/proposals/vegetation.md section 7).

    PYTHONPATH=. uv run python tools/veg_check.py [--world dc3732] [--json out.json]

Runs planet/vegetation.py on Earth's terrain twice: on the model's own
climate (the Earth world's layers) and on the observed climate (NCEP
temperature, GPCC half-year rain, CRU sunshine for cloud; tools/earth_data.py),
each on the soils (planet/soils.py pass 1, with GLiM rock and the LGM ice as
tools/soil_check.py; --no-soil: the old fixed buckets).
The gap between the two separates vegetation errors from climate errors.
Lakes are ignored (vegetation is computed on every land cell; the L6
Earth world floods ~6 Mkm2 of flat basins, the Amazon and Congo among them).

Compared with:
  - potential natural vegetation (Ramankutty & Foley 1999, downloaded by
    earth_data.earth_potveg): area-weighted agreement of 7 groups, land
    outside Antarctica, wetlands and lakes left out;
  - GFED4.1s burned area (2001-2015 mean, small fires included; the owner's
    ORNL DAAC download, earth_data.gfed_ba_raw; --no-gfed): total, the share
    in savanna and grassland, boreal fire rotation, by latitude, by cell;
  - MODIS MOD17A3 NPP (2000-2015 mean, NTSG mirror) and MOD44B tree cover
    (2001-2015 mean, UHH-ICDC 0.5 deg; earth_data.mod17_npp_raw,
    mod44b_tree_raw; --no-modis): totals on common cells, zonal means, by
    group and cell. Both observe today's land use, the model potential vegetation;
  - published global numbers: land NPP ~56 Pg C/yr (Field et al. 1998; MODIS
    MOD17 ~53), approximate MOD17 zonal means (Zhao et al. 2005; read off
    their maps, so only good to ~20%), potential biome areas, vegetation
    carbon ~450-650 Pg C, the five Mediterranean regions, the C3/C4 crossover
    (~30-35 deg, Still et al. 2003).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy, planet/parallel.py)
import numpy as np  # noqa: E402
from planet import climate  # noqa: E402
from planet import store as S  # noqa: E402
from planet import vegetation as V  # noqa: E402
from planet import world as W  # noqa: E402
from tools.earth_data import (POTVEG_CLASSES, cell_areas, earth_clouds, earth_gfed, earth_mod17_npp,  # noqa: E402
                              earth_on_grid, earth_potveg, earth_tree_cover, gfed_ba_raw)

TILT = 23.44
# comparison groups
GROUPS = ["forest/woodland", "savanna", "grassland", "shrubland", "tundra", "desert", "ice/rock", "wetland", "lake"]
_G = {k: i for i, k in enumerate(GROUPS)}


def _type_group() -> np.ndarray:
    g = np.full(len(V.TYPES), -1)
    put = {
        "forest/woodland": [1, 2, 3, 4, 5, 6, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 38, 39, 40, 41, 51],
        "savanna": [7, 8, 9, 10, 11],
        "shrubland": [19, 35, 36, 62], "tundra": [12, 42, 43, 44, 45, 47, 48, 54],
        "desert": [13, 14, 16, 17, 59], "grassland": [15, 31, 32, 33, 34, 61], "ice/rock": [46, 49, 57, 58], "wetland": [50, 52, 53, 55, 56], "lake": [60]}
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


def run(grid, L, obs: dict | None, geo: dict | None = None):
    """The vegetation model on the Earth world's model climate, or (obs) on
    the observed one where it has data; on the soils (pass 1, PW-185) from
    that climate and geo (tools/soil_check.geology), or without soils (fixed
    buckets) when geo is None."""
    t, tw, tc = L["temperature"].astype(float), L["warm_month"].astype(float), L["cold_month"].astype(float)
    pj, pa = L["precipitation_jul"].astype(float), L["precipitation_jan"].astype(float)
    cj, ca = climate.shade_from_hours(grid.lat, L["sunshine_jul"], L["sunshine_jan"])  # (the light's cloud)
    if obs is not None:
        def fill(o, m):
            o = np.asarray(o, float)
            return np.where(np.isfinite(o), o, m)
        t, tw, tc = fill(obs["obs_temp"], t), fill(obs["obs_t_warm"], tw), fill(obs["obs_t_cold"], tc)
        pj, pa = fill(obs["obs_p_jul"], pj), fill(obs["obs_p_jan"], pa)
        cj = fill(np.clip((0.95 - obs["obs_sun_jul"]) / 0.9, 0, 1), cj)
        ca = fill(np.clip((0.95 - obs["obs_sun_jan"]) / 0.9, 0, 1), ca)
    soil = None
    if geo is not None:
        from planet import soils as SO
        soil = SO.mineral(grid, L["elevation"], t, tw, tc, pj, pa, TILT, cj, ca, geo["rock"],
                          glaciated_myr=geo["glaciated_myr"], ice=L["ice"], lake_kind=L["lake_kind"], flow=L["flow"],
                          flood_ratio=L.get("flood_ratio"),
                          winds=[(L["wind_jul_e"], L["wind_jul_n"]), (L["wind_jan_e"], L["wind_jan_n"])])
    return V.model(grid, L["elevation"], t, tw, tc, pj, pa, TILT, cj, ca, L["flow"], None, None, L["ice"], soil=soil)


def report(grid, L, v, pv, area_km2, label: str, gfed: np.ndarray | None = None,
           sat: dict | None = None) -> dict:
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
    if gfed is not None:
        out["fire_obs"] = fire_vs_gfed(grid, types, grp, burned, gfed, pv, land, a)
    if sat is not None:
        out["sat_obs"] = npp_tree_vs_modis(grid, L, sm, grp, land, a, sat)
    out["forest_mkm2"] = float(a[land & (sm["tree"] >= 0.6)].sum() / 1e6)
    out["boreal_mkm2"] = float(a[np.isin(types, [37, 38, 39, 40, 41])].sum() / 1e6)
    out["savanna_grass_mkm2"] = float(a[sav].sum() / 1e6)
    out["desert_xeric_mkm2"] = float(a[np.isin(types, [13, 14, 15, 16, 17, 59])].sum() / 1e6)
    out["wetland_types_mkm2"] = float(a[np.isin(types, [5, 6, 11, 50, 51, 52, 53, 54])].sum() / 1e6)
    out["flooded_mkm2"] = float((v["fw"] * a).sum() / 1e6)
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


BOREAL_TYPES = [37, 38, 39, 40, 41]


def _rotation(burned, a, m):
    """Fire rotation (yr): the area of m over the area it burns a year; and the median cell's interval."""
    b = (burned * a)[m].sum()
    rot = float(a[m].sum() / b) if b > 0 else float("inf")
    med = float(np.median(1.0 / np.maximum(burned[m], 1e-6))) if m.any() else float("nan")
    return round(min(rot, 1e5)), round(min(med, 1e5))


def fire_vs_gfed(grid, types, grp, burned, gfed, pv, land, a) -> dict:
    """The model's burned area against GFED4.1s (2001-2015 mean, with small fires,
    tools/earth_data.gfed_ba_raw). GFED counts every fire, crop and deforestation
    fires among them; the model has natural fire on potential vegetation, so its
    shares are the comparison, not cell-by-cell parity."""
    o = {}
    obs = gfed * land
    tot_m, tot_o = (burned * a)[land].sum(), (obs * a).sum()
    o["gfed_mkm2"] = float(tot_o / 1e6)
    raw = gfed_ba_raw()
    o["gfed_years"] = f"{int(raw['years'][0])}-{int(raw['years'][-1])}"
    o["gfed_range_mkm2"] = (round(float(raw["total_mkm2"].min()), 2), round(float(raw["total_mkm2"].max()), 2))
    pvg = np.where(pv > 0, POTVEG_GROUP[pv], -1)
    # burned share of grassy land: observed by potential vegetation's savanna + grassland (and shrubland)
    o["gfed_share_savanna_grass_potveg"] = float((obs * a)[np.isin(pvg, [1, 2])].sum() / tot_o)
    o["gfed_share_sav_grass_shrub_potveg"] = float((obs * a)[np.isin(pvg, [1, 2, 3])].sum() / tot_o)
    # where the model puts savanna/grassland: GFED's share there, and the model's own
    mg = land & np.isin(grp, [_G["savanna"], _G["grassland"]])
    o["gfed_share_in_model_grassy"] = float((obs * a)[mg].sum() / tot_o)
    o["model_share_in_model_grassy"] = float((burned * a)[mg].sum() / max(tot_m, 1e-12))
    o["gfed_by_model_group"] = {k: round(float((obs * a)[grp == i].sum() / 1e6), 2) for i, k in enumerate(GROUPS)}
    o["gfed_by_potveg_group"] = {k: round(float((obs * a)[pvg == i].sum() / 1e6), 2) for i, k in enumerate(GROUPS[:7])}
    # boreal fire return: on the model's boreal types, and on potential vegetation's boreal forest
    mb = land & np.isin(types, BOREAL_TYPES)
    pb = land & np.isin(pv, [6, 7])
    o["boreal_model"] = _rotation(burned, a, mb)
    o["boreal_gfed_on_model_boreal"] = _rotation(gfed, a, mb)
    o["boreal_gfed_on_potveg_boreal"] = _rotation(gfed, a, pb)
    o["boreal_mkm2_yr"] = (round(float((burned * a)[mb].sum() / 1e6), 3), round(float((obs * a)[pb].sum() / 1e6), 3))
    # by latitude band (Mkm2/yr), model / GFED
    lat = grid.lat
    o["by_lat"] = {b0: (round(float((burned * a)[land & (lat >= b0) & (lat < b0 + 15)].sum() / 1e6), 2),
                        round(float((obs * a)[(lat >= b0) & (lat < b0 + 15)].sum() / 1e6), 2))
                   for b0 in range(-45, 75, 15)}
    # cell-by-cell rank correlation on land outside Antarctica
    m = land & (lat > -60)
    rk = lambda x: np.argsort(np.argsort(x)).astype(float)  # noqa: E731
    o["spearman"] = float(np.corrcoef(rk(burned[m]), rk(gfed[m]))[0, 1])
    # land burning at least every 10 / 100 years
    o["burning_mkm2"] = {f">=1/{n}yr": (round(float(a[m & (burned >= 1 / n)].sum() / 1e6), 1),
                                         round(float(a[m & (gfed >= 1 / n)].sum() / 1e6), 1)) for n in (10, 100)}
    return o


def npp_tree_vs_modis(grid, L, sm, grp, land, a, sat) -> dict:
    """The model's NPP and tree cover against MODIS: MOD17A3 NPP (2000-2015 mean)
    and MOD44B tree cover (2001-2015 mean; tools/earth_data). Both observe
    today's land, fields and pastures included, against the model's potential
    vegetation: NPP is close (crops are productive), tree cover is lower than
    potential where forests were cleared."""
    o = {}
    lat = grid.lat
    ok = land & (L["ice"] <= 0)
    obs_n, obs_t = sat["npp"], sat["tree"]
    mn = ok & np.isfinite(obs_n) & (sat["npp_cover"] >= 0.5)
    o["npp_pg_common"] = (round(float((sm["npp"] * a)[mn].sum() * 1e6 / 1e15), 1),
                          round(float((obs_n * a)[mn].sum() * 1e6 / 1e15), 1))
    o["npp_r"] = float(np.corrcoef(sm["npp"][mn], obs_n[mn])[0, 1])
    o["npp_bias"] = float(((sm["npp"] - obs_n) * a)[mn].sum() / a[mn].sum())
    o["npp_zonal_mod17"] = {}
    for s0 in range(-60, 80, 10):
        b = mn & (lat >= s0) & (lat < s0 + 10)
        if b.sum() > 3:
            o["npp_zonal_mod17"][s0] = (round(float((sm["npp"] * a)[b].sum() / a[b].sum())),
                                        round(float((obs_n * a)[b].sum() / a[b].sum())))
    o["npp_by_group"] = {k: (round(float((sm["npp"] * a)[mn & (grp == i)].sum() / a[mn & (grp == i)].sum())),
                             round(float((obs_n * a)[mn & (grp == i)].sum() / a[mn & (grp == i)].sum())))
                         for i, k in enumerate(GROUPS[:7]) if (mn & (grp == i)).sum() > 3}
    mt = ok & np.isfinite(obs_t) & (sat["tree_cover"] >= 0.5) & (lat > -60)
    tr = sm["tree"]
    o["tree_r"] = float(np.corrcoef(tr[mt], obs_t[mt])[0, 1])
    o["tree_mean"] = (round(float((tr * a)[mt].sum() / a[mt].sum()), 3), round(float((obs_t * a)[mt].sum() / a[mt].sum()), 3))
    o["tree_area_mkm2"] = (round(float((tr * a)[mt].sum() / 1e6), 1), round(float((obs_t * a)[mt].sum() / 1e6), 1))
    o["tree_ge"] = {f">={x}": (round(float(a[mt & (tr >= x)].sum() / 1e6), 1), round(float(a[mt & (obs_t >= x)].sum() / 1e6), 1))
                    for x in (0.1, 0.3, 0.6)}
    o["tree_by_group"] = {k: (round(float(tr[mt & (grp == i)].mean()), 2), round(float(obs_t[mt & (grp == i)].mean()), 2))
                          for i, k in enumerate(GROUPS[:7]) if (mt & (grp == i)).sum() > 3}
    o["tree_zonal"] = {}
    for s0 in range(-60, 80, 10):
        b = mt & (lat >= s0) & (lat < s0 + 10)
        if b.sum() > 3:
            o["tree_zonal"][s0] = (round(float((tr * a)[b].sum() / a[b].sum()), 2),
                                   round(float((obs_t * a)[b].sum() / a[b].sum()), 2))
    return o


def fmt_sat(f: dict) -> list[str]:
    return [
        f"  MOD17A3 NPP (2000-2015): on common land cells model {f['npp_pg_common'][0]} / MOD17 {f['npp_pg_common'][1]} "
        f"Pg C/yr; r by cell {f['npp_r']:.2f}, mean bias {f['npp_bias']:+.0f} g C/m2/yr",
        "    NPP by band (model / MOD17): " + ", ".join(f"{k}: {m}/{o}" for k, (m, o) in f["npp_zonal_mod17"].items()),
        "    NPP by model group (model / MOD17): " + ", ".join(f"{k} {m}/{o}" for k, (m, o) in f["npp_by_group"].items()),
        f"  MOD44B tree cover (2001-2015, today's land use): mean model {f['tree_mean'][0]:.2f} / MODIS {f['tree_mean'][1]:.2f}, "
        f"canopy area {f['tree_area_mkm2'][0]} / {f['tree_area_mkm2'][1]} Mkm2; r by cell {f['tree_r']:.2f}",
        "    land with tree cover (model/MODIS Mkm2): " + ", ".join(f"{k} {m}/{o}" for k, (m, o) in f["tree_ge"].items()),
        "    mean tree cover by model group (model/MODIS): " + ", ".join(f"{k} {m}/{o}" for k, (m, o) in f["tree_by_group"].items()),
        "    tree cover by band (model/MODIS): " + ", ".join(f"{k}: {m}/{o}" for k, (m, o) in f["tree_zonal"].items()),
    ]


def fmt_fire(f: dict) -> list[str]:
    return [
        f"  GFED4.1s ({f['gfed_years']}, small fires incl.): {f['gfed_mkm2']:.2f} Mkm2/yr on land cells "
        f"(years {f['gfed_range_mkm2'][0]}-{f['gfed_range_mkm2'][1]}); rank correlation model vs GFED by cell {f['spearman']:.2f}",
        f"    GFED share in potveg savanna+grassland {100 * f['gfed_share_savanna_grass_potveg']:.0f}% "
        f"(+shrubland {100 * f['gfed_share_sav_grass_shrub_potveg']:.0f}%); in the model's savanna+grassland cells: "
        f"GFED {100 * f['gfed_share_in_model_grassy']:.0f}%, model {100 * f['model_share_in_model_grassy']:.0f}%",
        "    GFED by model group (Mkm2/yr): " + ", ".join(f"{k} {v}" for k, v in f["gfed_by_model_group"].items() if v),
        "    GFED by potveg group (Mkm2/yr): " + ", ".join(f"{k} {v}" for k, v in f["gfed_by_potveg_group"].items() if v),
        f"    boreal fire rotation / median interval (yr): model types {f['boreal_model'][0]} / {f['boreal_model'][1]}; "
        f"GFED on those cells {f['boreal_gfed_on_model_boreal'][0]} / {f['boreal_gfed_on_model_boreal'][1]}; "
        f"GFED on potveg boreal {f['boreal_gfed_on_potveg_boreal'][0]} / {f['boreal_gfed_on_potveg_boreal'][1]} "
        f"(burned Mkm2/yr: model types {f['boreal_mkm2_yr'][0]}, GFED potveg boreal {f['boreal_mkm2_yr'][1]})",
        "    by 15-deg band, model/GFED Mkm2/yr: " + ", ".join(f"{k}: {m}/{g}" for k, (m, g) in f["by_lat"].items()),
        "    land burning at least (model/GFED Mkm2): " + ", ".join(f"{k} {m}/{g}" for k, (m, g) in f["burning_mkm2"].items()),
    ]


def fmt(r: dict) -> str:
    lo = TARGETS
    lines = [f"## {r['label']}",
             f"  land NPP            {r['npp_pg']:6.1f} Pg C/yr      (target 45-70; obs ~56)",
             f"  vegetation carbon   {r['vegc_pg']:6.0f} Pg C         (target 300-800; obs ~450-650)",
             f"  burned area         {r['burned_mkm2']:6.1f} Mkm2/yr      (target 2-8; GFED4s ~4-5), "
             f"{100 * r['burned_savanna_share']:.0f}% in savanna and grassland (obs ~70-80%), {r['burned_rainforest_mkm2']:.2f} in rainforest",
             "  burned by group (Mkm2/yr): " + ", ".join(f"{k} {v}" for k, v in r["burned_by_group"].items() if v),
             *(fmt_fire(r["fire_obs"]) if "fire_obs" in r else []),
             *(fmt_sat(r["sat_obs"]) if "sat_obs" in r else []),
             f"  forest (trees>=60%) {r['forest_mkm2']:6.1f} Mkm2         (potential ~55-60)",
             f"  boreal forest       {r['boreal_mkm2']:6.1f} Mkm2         (~12-17)",
             f"  savanna, trop. grass{r['savanna_grass_mkm2']:6.1f} Mkm2         (~20)",
             f"  desert, xeric shrub {r['desert_xeric_mkm2']:6.1f} Mkm2         (~25-30)",
             f"  tundra (+alpine)    {r['tundra_mkm2']:6.1f} Mkm2         (~8-11)",
             f"  wetland types       {r['wetland_types_mkm2']:6.1f} Mkm2         (cells where wetland dominates; "
             f"flooded share of all cells {r['flooded_mkm2']:.1f} Mkm2; Earth's wetlands ~5-9)",
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
    ap.add_argument("--no-gfed", action="store_true", help="skip the GFED4.1s burned-area comparison")
    ap.add_argument("--no-modis", action="store_true", help="skip the MOD17 NPP and MOD44B tree-cover comparison")
    ap.add_argument("--no-soil", action="store_true", help="fixed soil buckets, no soils (as before PW-185)")
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
    gfed = None
    if not a.no_gfed:
        try:
            gfed = earth_gfed(grid)
        except SystemExit as e:  # the zip needs an Earthdata login; the check runs without it
            print(f"(no GFED comparison: {e})")
    sat = None
    if not a.no_modis:
        n, t = earth_mod17_npp(grid), earth_tree_cover(grid)
        sat = {"npp": n["npp"], "npp_cover": n["cover"], "tree": t["tree"], "tree_cover": t["cover"]}
    area = cell_areas(grid) * 6371.0 ** 2
    geo = None
    if not a.no_soil:
        from tools.soil_check import geology
        geo = geology(grid, L)
    res = []
    for label, o in (("model climate", None), ("observed climate", obs)):
        v = run(grid, L, o, geo)
        res.append(report(grid, L, v, pv, area, label, gfed, sat))
        print(fmt(res[-1]))
        if a.png and o is not None:
            maps_png(grid, L, v, pv, Path(a.png))
    print(f"(world {path.stem}, level {grid.level}; potential vegetation classes: {len(POTVEG_CLASSES)}; "
          f"{time.time() - t0:.1f}s)")
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
