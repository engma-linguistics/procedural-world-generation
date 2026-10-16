"""The soil model on Earth (PW-185; docs/proposals/soils.md section 7).

    PYTHONPATH=. uv run python tools/soil_check.py [--world 611870] [--png out.png] [--json out.json] [--data]

Runs planet/soils.py (both passes, with the vegetation between them) on
Earth's terrain twice, as tools/veg_check.py does for vegetation: on the
observed climate (NCEP temperature, GPCC half-year rain, CRU sunshine for
cloud; tools/earth_data.py), which is what the soils are tuned on, and on the
model's own climate (the Earth world's layers), reported only, so the
climate's errors aren't tuned in (section 7.2). Both use the Earth world's
terrain, rivers, lakes and winds, and observed geology:
  - parent rock: GLiM (Hartmann & Moosdorf 2012, CC BY 3.0) mapped to
    planet.surface.ROCKS (earth_data.GLIM_TO_ROCK); the Earth world's own
    rough rock where GLiM has none;
  - glaciation: the Last Glacial Maximum ice (Shao et al., CC BY 4.0): ground
    under >= 50% LGM ice was glaciated 21 kyr ago, the rest never (the
    earlier ice ages are older than any soil age that matters here);
  - no landform record (Earth has none, PW-132): no dune fields, aggrading
    coastal plains or young volcano landforms; ash soils only on GLiM's
    pyroclastics (tuff).
Compared with SoilGrids 2.0 WRB most probable group (ISRIC, CC BY 4.0),
grouped into 10 groups, area-weighted over land with SoilGrids data, and
with published global numbers (section 7.3).

--data prints the input data summary instead (SoilGrids shares, GLiM rock,
LGM ice areas: PW-314's plumbing check).
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
from planet import soils as SO  # noqa: E402
from planet import store as S  # noqa: E402
from planet import vegetation as V  # noqa: E402
from planet import world as W  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.surface import ROCKS  # noqa: E402
from tools.earth_data import (SOILGRIDS_NODATA, cell_areas, earth_clouds, earth_glim, earth_lgm_ice,  # noqa: E402
                              earth_on_grid, earth_soilgrids)

TILT = 23.44
LGM_KYR = 21.0

# Published LGM ice-sheet areas, Mkm2 (approximate, from reconstructions such as ICE-6G_C, GLAC-1D
# and Ehlers & Gibbard 2007; they differ by 10-20% between reconstructions)
LGM_REF = {"total": (40, 50), "Laurentide + Cordilleran": (13, 17), "Fennoscandia + Barents-Kara": (4, 8),
           "Greenland + Innuitian (merged then)": (2, 6), "Antarctica": (14, 19)}

# comparison groups (section 7.3)
GROUPS = ["organic", "frozen", "thin", "desert", "steppe/black earth", "podzol", "temperate forest",
          "tropical red", "wet/alluvial", "young"]
_G = {k: i for i, k in enumerate(GROUPS)}
WRB_GROUP = {
    "Histosols": "organic", "Cryosols": "frozen", "Leptosols": "thin",
    "Calcisols": "desert", "Gypsisols": "desert", "Arenosols": "desert", "Solonchaks": "desert",
    "Solonetz": "desert", "Durisols": "desert",
    "Chernozems": "steppe/black earth", "Kastanozems": "steppe/black earth", "Phaeozems": "steppe/black earth",
    "Vertisols": "steppe/black earth",
    "Podzols": "podzol", "Luvisols": "temperate forest", "Albeluvisols": "temperate forest",
    "Ferralsols": "tropical red", "Acrisols": "tropical red", "Lixisols": "tropical red", "Alisols": "tropical red",
    "Nitisols": "tropical red", "Plinthosols": "tropical red",
    "Fluvisols": "wet/alluvial", "Gleysols": "wet/alluvial", "Planosols": "wet/alluvial",
    "Stagnosols": "wet/alluvial",
    "Cambisols": "young", "Regosols": "young", "Andosols": "young", "Umbrisols": "young",
}
TYPE_GROUP = {SO.PEAT: "organic", SO.FROZEN: "frozen", SO.THIN: "thin", SO.RENDZINA: "thin",
              SO.SALT: "desert", SO.SAND: "desert", SO.GYPSIC: "desert", SO.CALCIC: "desert",
              SO.VERTISOL: "steppe/black earth", SO.CHESTNUT: "steppe/black earth",
              SO.CHERNOZEM: "steppe/black earth", SO.PODZOL: "podzol", SO.LUVISOL: "temperate forest",
              SO.FERRALSOL: "tropical red", SO.ACRISOL: "tropical red", SO.ALLUVIUM: "wet/alluvial",
              SO.GLEY: "wet/alluvial", SO.ANDOSOL: "young", SO.CAMBISOL: "young"}
# our types -> the WRB groups they stand for (for the per-type share table)
TYPE_WRB = {SO.PEAT: ["Histosols"], SO.FROZEN: ["Cryosols"], SO.THIN: ["Leptosols"], SO.RENDZINA: [],
            SO.SALT: ["Solonchaks", "Solonetz"], SO.SAND: ["Arenosols"], SO.GYPSIC: ["Gypsisols", "Durisols"],
            SO.CALCIC: ["Calcisols"], SO.VERTISOL: ["Vertisols"], SO.CHESTNUT: ["Kastanozems"],
            SO.CHERNOZEM: ["Chernozems", "Phaeozems"], SO.PODZOL: ["Podzols"],
            SO.LUVISOL: ["Luvisols", "Albeluvisols"], SO.FERRALSOL: ["Ferralsols", "Nitisols", "Plinthosols"],
            SO.ACRISOL: ["Acrisols", "Lixisols", "Alisols"], SO.ALLUVIUM: ["Fluvisols"],
            SO.GLEY: ["Gleysols", "Planosols", "Stagnosols"], SO.ANDOSOL: ["Andosols"],
            SO.CAMBISOL: ["Cambisols", "Regosols", "Umbrisols"]}
# where each type should be (section 7.3's placement check): lat0, lat1, lon0, lon1, types
PLACES = {
    "Ferralsols, Amazon": ((-15, 5, -75, -45), [SO.FERRALSOL]),
    "Ferralsols, Congo": ((-10, 5, 12, 30), [SO.FERRALSOL]),
    "black earth, Ukraine-Kazakhstan": ((45, 55, 25, 75), [SO.CHERNOZEM, SO.CHESTNUT]),
    "black earth, Great Plains": ((35, 52, -105, -92), [SO.CHERNOZEM, SO.CHESTNUT]),
    "black earth, Pampas": ((-38, -28, -65, -57), [SO.CHERNOZEM, SO.CHESTNUT]),
    "podzols, boreal Canada": ((48, 60, -100, -60), [SO.PODZOL]),
    "podzols, Scandinavia-W Russia": ((58, 66, 10, 60), [SO.PODZOL]),
    "ash soils, Japan-Java-Andes": (None, [SO.ANDOSOL]),
    "Vertisols, Deccan": ((15, 24, 73, 80), [SO.VERTISOL]),
    "Vertisols, Sudan": ((8, 16, 25, 36), [SO.VERTISOL]),
    "desert soils, Sahara-Arabia": ((15, 32, -15, 55), [SO.GYPSIC, SO.CALCIC, SO.SALT, SO.SAND]),
    "desert soils, inland Australia": ((-32, -20, 120, 145), [SO.GYPSIC, SO.CALCIC, SO.SALT, SO.SAND]),
    "red clay, SE United States": ((30, 37, -90, -76), [SO.ACRISOL]),
    "red clay, S China": ((22, 30, 105, 120), [SO.ACRISOL]),
}
ANDOSOL_BOXES = [(30, 45, 129, 146), (-9, -6, 105, 115), (-40, 5, -80, -70)]
LOESS_PLACES = {"Loess Plateau": (34, 40, 103, 113), "central Europe": (45, 52, 5, 30),
                "Mississippi valley": (35, 43, -95, -86), "Pampas": (-38, -28, -65, -57),
                "Sahara (none expected)": (15, 30, -10, 30)}


def lgm_regions(lat, lon):
    """Boolean masks of the regions LGM_REF names (boxes; the ice sheets don't overlap in them)."""
    return {
        "total": np.ones(len(lat), bool),
        "Laurentide + Cordilleran": (lat > 35) & (lon > -170) & (lon < -55) & ~((lat > 58) & (lon > -75)),
        "Fennoscandia + Barents-Kara": (lat > 50) & (lon > -10) & (lon < 110),
        "Greenland + Innuitian (merged then)": (lat > 58) & (lon > -75) & (lon < -10),
        "Antarctica": lat < -60,
    }


def geology(grid, L) -> dict:
    """Earth's observed parent rock and glaciation as soils.mineral wants them."""
    rock = earth_glim(grid)
    rock = np.where(rock >= 0, rock, np.asarray(L["rock"], int))
    lgm = earth_lgm_ice(grid)
    glac = np.where(lgm >= 0.5, LGM_KYR / 1000.0, 9999.0)
    glac = np.where(np.asarray(L["ice"]) > 0, 0.0, glac)
    return {"rock": rock, "glaciated_myr": glac}


def climate_of(L, obs: dict | None) -> dict:
    """The Earth world's model climate, or (obs) the observed one where it has data."""
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
    return dict(temp=t, t_warm=tw, t_cold=tc, p_jul=pj, p_jan=pa, cloud_jul=cj, cloud_jan=ca)


def earth_soils(grid, L, obs: dict | None, geo: dict, soil: bool = True):
    """Pass 1, the vegetation (on the soil, or without it: soil=False is the
    old fixed-bucket vegetation, for comparison), pass 2."""
    c = climate_of(L, obs)
    winds = [(L["wind_jul_e"], L["wind_jul_n"]), (L["wind_jan_e"], L["wind_jan_n"])]
    m = SO.mineral(grid, L["elevation"], c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], TILT,
                   c["cloud_jul"], c["cloud_jan"], geo["rock"], glaciated_myr=geo["glaciated_myr"], ice=L["ice"],
                   lake_kind=L["lake_kind"], flow=L["flow"], flood_ratio=L.get("flood_ratio"), winds=winds)
    vg = V.model(grid, L["elevation"], c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], TILT,
                 c["cloud_jul"], c["cloud_jan"], L["flow"], None, None, L["ice"], soil=m if soil else None)
    return m, vg, SO.organic(m, vg)


def report(grid, L, m, vg, o, sg, area_km2, label: str) -> dict:
    lat, lon = grid.lat, grid.lon
    a = area_km2
    land = m["land"]
    types = o["types"]
    legend = list(sg["legend"])
    wrb = sg["wrb"].astype(int)
    has = (wrb != SOILGRIDS_NODATA) & land & (types > 0)
    wg = np.full(len(legend) + 1, -1)
    for i, name in enumerate(legend):
        wg[i] = _G[WRB_GROUP[str(name)]]
    obs_g = np.where(wrb != SOILGRIDS_NODATA, wg[np.minimum(wrb, len(legend))], -1)
    tg = np.full(len(SO.TYPES), -1)
    for t, g in TYPE_GROUP.items():
        tg[t] = _G[g]
    mod_g = tg[types]
    w = a * sg["cover"]
    msk = has & (obs_g >= 0) & (mod_g >= 0)
    out = {"label": label}
    out["agreement"] = float(100 * w[msk][obs_g[msk] == mod_g[msk]].sum() / w[msk].sum())
    conf = np.zeros((len(GROUPS), len(GROUPS)))
    np.add.at(conf, (obs_g[msk], mod_g[msk]), w[msk] / 1e6)
    out["confusion_mkm2"] = conf.round(1).tolist()
    out["group_share"] = {g: (round(float(100 * w[msk & (mod_g == i)].sum() / w[msk].sum()), 1),
                              round(float(100 * w[msk & (obs_g == i)].sum() / w[msk].sum()), 1))
                          for i, g in enumerate(GROUPS)}
    # per-type share of land (area-weighted) against its WRB groups' share
    sgw = has & (wrb != SOILGRIDS_NODATA)
    tot = w[sgw].sum()
    out["type_share"] = {}
    for t in range(1, len(SO.TYPES)):
        ids = [legend.index(x) for x in TYPE_WRB[t] if x in legend]
        out["type_share"][SO.TYPES[t][2]] = (round(float(100 * w[sgw & (types == t)].sum() / tot), 1),
                                             round(float(100 * w[sgw & np.isin(wrb, ids)].sum() / tot), 1))
    # placement
    pl = {}
    for name, (box, want) in PLACES.items():
        if box is None:
            bm = np.zeros(len(lat), bool)
            for la0, la1, lo0, lo1 in ANDOSOL_BOXES:
                bm |= (lat >= la0) & (lat <= la1) & (lon >= lo0) & (lon <= lo1)
        else:
            la0, la1, lo0, lo1 = box
            bm = (lat >= la0) & (lat <= la1) & (lon >= lo0) & (lon <= lo1)
        bm &= land
        pl[name] = round(float(100 * a[bm & np.isin(types, want)].sum() / max(a[bm].sum(), 1e-9)), 0)
    out["placement_pct"] = pl
    # carbon, peat, permafrost, loess
    out["soil_carbon_pg"] = float((o["carbon"] * a * 1e6).sum() / 1e12)
    peat_area = np.where(o["peat_depth"] >= 0.3, vg["fw"], 0.0) * a
    out["peat_mkm2"] = float(peat_area.sum() / 1e6)
    out["peat_carbon_pg"] = float((o["peat_c"] * vg["fw"] * a * 1e6).sum() / 1e12)
    out["peat_boreal_tropical_mkm2"] = (round(float(peat_area[np.abs(lat) >= 45].sum() / 1e6), 2),
                                        round(float(peat_area[np.abs(lat) < 25].sum() / 1e6), 2))
    out["histosol_mkm2"] = float(a[types == SO.PEAT].sum() / 1e6)
    pf = m["permafrost"]
    out["permafrost_mkm2"] = {SO.PERMAFROST[k]: round(float(a[pf == k].sum() / 1e6), 1) for k in (1, 2, 3)}
    out["permafrost_region_mkm2"] = float(a[(pf > 0) & (lat > -60)].sum() / 1e6)
    # southern limit of permafrost (any class) by 60-deg sector in the north: 5th percentile latitude
    lim = {}
    for l0 in range(-180, 180, 60):
        sec = land & (lat > 30) & (lon >= l0) & (lon < l0 + 60) & (pf > 0) & (L["elevation"] < 1500)
        if sec.sum() >= 3:
            lim[l0] = round(float(np.percentile(lat[sec], 5)), 1)
    out["permafrost_south_limit"] = lim
    out["loess_m"] = {}
    for name, (la0, la1, lo0, lo1) in LOESS_PLACES.items():
        bm = land & (lat >= la0) & (lat <= la1) & (lon >= lo0) & (lon <= lo1)
        out["loess_m"][name] = (round(float(np.median(m["loess"][bm])), 1), round(float(m["loess"][bm].max()), 1))
    out["loess_area_1m_mkm2"] = float(a[m["loess"] >= 1].sum() / 1e6)
    out["npp_pg"] = float((vg["sm"]["npp"] * a * 1e6).sum() / 1e15)
    lm = land & (lat > -60)
    out["cap_means_mm"] = (round(float((m["cap1"] * a)[lm].sum() / a[lm].sum()), 1),
                           round(float((m["cap2"] * a)[lm].sum() / a[lm].sum()), 1))
    out["f_numerator_mean"] = round(float(((0.85 + 0.25 * m["fertility"]) * a)[lm].sum() / a[lm].sum()), 4)
    out["fertility_mean"] = round(float((o["fertility"] * a)[lm].sum() / a[lm].sum()), 2)
    out["depth_mean_m"] = round(float((m["depth"] * a)[lm].sum() / a[lm].sum()), 2)
    return out


def fmt(r: dict) -> str:
    lines = [f"## {r['label']}",
             f"  type agreement (10 groups, area-weighted, vs SoilGrids WRB) {r['agreement']:.1f}%  (good enough >= 50)",
             "  groups, % of land (model / SoilGrids): "
             + ", ".join(f"{k} {m}/{s}" for k, (m, s) in r["group_share"].items()),
             "  types, % of land (model / its WRB groups in SoilGrids):"]
    items = list(r["type_share"].items())
    for i in range(0, len(items), 5):
        lines.append("    " + ", ".join(f"{k} {m}/{s}" for k, (m, s) in items[i:i + 5]))
    lines += ["  placement (% of the region's land in the expected types): "
              + ", ".join(f"{k} {v:.0f}" for k, v in r["placement_pct"].items()),
              f"  soil carbon, top metre {r['soil_carbon_pg']:6.0f} Pg C   (~1500; good enough 1000-2200)",
              f"  peatland (>= 0.3 m)    {r['peat_mkm2']:6.1f} Mkm2   (~4; 2-8), carbon {r['peat_carbon_pg']:.0f} Pg C "
              f"(~500; 200-900); boreal / tropical {r['peat_boreal_tropical_mkm2']} Mkm2; peat-type cells "
              f"{r['histosol_mkm2']:.1f} Mkm2",
              f"  permafrost region      {r['permafrost_region_mkm2']:6.1f} Mkm2   (~20; 13-28) "
              + ", ".join(f"{k} {v}" for k, v in r["permafrost_mkm2"].items())
              + "; southern limit (5th pct lat, below 1500 m) by sector: "
              + ", ".join(f"{k}: {v}" for k, v in r["permafrost_south_limit"].items()),
              "  loess, m (median / max): " + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in r["loess_m"].items())
              + f"; land with >= 1 m {r['loess_area_1m_mkm2']:.1f} Mkm2",
              f"  land NPP {r['npp_pg']:.1f} Pg C/yr; vegetation buckets' land means {r['cap_means_mm']} mm; "
              f"mean (0.85 + 0.25 fertility) {r['f_numerator_mean']}; fertility {r['fertility_mean']}; "
              f"depth {r['depth_mean_m']} m",
              "  confusion (rows SoilGrids, cols model; Mkm2; " + "/".join(g[:5] for g in GROUPS) + "):"]
    lines += ["    " + f"{GROUPS[i][:12]:12} " + " ".join(f"{x:5.1f}" for x in row)
              for i, row in enumerate(r["confusion_mkm2"])]
    return "\n".join(lines)


def _rgb(hexes) -> np.ndarray:
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in hexes], np.uint8)


GROUP_COLORS = ["#7a4f9a", "#8aa3b4", "#8c8c8c", "#f3e2a8", "#1c1c1c", "#d9d9d0", "#b07e4e", "#cf4b22",
                "#3f8fd0", "#9cae5a"]


def maps_png(grid, L, o, sg, path: Path, width: int = 720) -> None:
    """Three maps, top to bottom: the model's groups, SoilGrids' groups, the model's named types."""
    from planet.images import write_png
    idx = W.nearest_cell_map(grid, width, width // 2)
    sea = (np.asarray(L["elevation"]) <= 0)[idx]
    legend = [str(x) for x in sg["legend"]]
    wg = np.array([_G[WRB_GROUP[x]] for x in legend] + [-1])
    wrb = sg["wrb"].astype(int)
    obs = np.where(wrb != SOILGRIDS_NODATA, wg[np.minimum(wrb, len(legend))], -1)
    tg = np.full(len(SO.TYPES), -1)
    for t, g in TYPE_GROUP.items():
        tg[t] = _G[g]
    gc, tc = _rgb(GROUP_COLORS), _rgb([t[5] for t in SO.TYPES])
    panels = []
    for arr, cols, none in ((tg[o["types"]], gc, -1), (obs, gc, -1), (o["types"], tc, None)):
        x = arr[idx]
        img = np.where((x >= 0)[..., None], cols[np.maximum(x, 0)], np.uint8(90))
        img[sea] = (29, 63, 110)
        panels.append(img.astype(np.uint8))
    write_png(path, np.concatenate(panels, 0))


def data_summary(level: int):
    """The input data (PW-314): SoilGrids shares, GLiM rock, LGM ice areas."""
    t0 = time.time()
    grid = build_grid(level)
    area = cell_areas(grid) * R_KM**2 / 1e6  # Mkm2
    lat, lon = grid.lat, grid.lon
    sg = earth_soilgrids(grid)
    has = sg["wrb"] != SOILGRIDS_NODATA
    print(f"level {level}: {grid.n} cells, {area.sum():.0f} Mkm2")
    warea = area * sg["cover"]
    print(f"\nSoilGrids WRB: {has.sum()} cells with data, {warea[has].sum():.1f} Mkm2 with data")
    share = np.bincount(sg["wrb"][has], warea[has], 30) / warea[has].sum()
    for i in np.argsort(-share)[:12]:
        print(f"  {sg['legend'][i]:<13s} {share[i]:6.1%}")
    rock = earth_glim(grid)
    has_r = rock >= 0
    print(f"\nGLiM parent rock: {has_r.sum()} cells with a rock, {area[has_r].sum():.1f} Mkm2")
    rs = np.bincount(rock[has_r], area[has_r], len(ROCKS)) / area[has_r].sum()
    for i in np.argsort(-rs):
        if rs[i] > 0:
            print(f"  {ROCKS[i][1]:<13s} {rs[i]:6.1%}")
    ice = earth_lgm_ice(grid)
    print("\nLGM (21 ka) ice cover, Mkm2 (observed here | published, approx.)")
    for name, msk in lgm_regions(lat, lon).items():
        lo, hi = LGM_REF[name]
        v = (ice * area)[msk].sum()
        print(f"  {name:<28s} {v:6.1f} | {lo}-{hi} {'' if lo * 0.9 <= v <= hi * 1.1 else '  <-- outside'}")
    print(f"\ntotal {time.time() - t0:.1f}s")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--world", default=None, help="Earth world id (default: the newest Earth world)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--png", default=None, help="maps (model groups, SoilGrids groups, model types) for the "
                                               "observed-climate run")
    ap.add_argument("--data", action="store_true", help="print the input data summary instead")
    ap.add_argument("--level", type=int, default=6, help="(--data) grid level")
    a = ap.parse_args()
    if a.data:
        return data_summary(a.level)
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
    sg = earth_soilgrids(grid)
    geo = geology(grid, L)
    area = cell_areas(grid) * R_KM ** 2
    res = []
    for label, o_ in (("observed climate", obs), ("model climate", None)):
        m, vg, o = earth_soils(grid, L, o_, geo)
        res.append(report(grid, L, m, vg, o, sg, area, label))
        print(fmt(res[-1]))
        if a.png and o_ is not None:
            maps_png(grid, L, o, sg, Path(a.png))
    print(f"(world {path.stem}, level {grid.level}; {time.time() - t0:.1f}s)")
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
