"""Lane 123 (PW-1261): the vegetation's NPP and above-ground NPP against sourced NPP-climate relations, on Earth's observed climate.

PYTHONPATH=<worktree> PLANET_DATA=<main repo> uv run python npp_check.py [--world 506694] [--json out.json] [--tag base] [--kn 0.4]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WT = Path(__file__).resolve().parents[4]  # the checkout this script sits in
sys.path.insert(0, str(WT))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import store as S, vegetation as V, world as W, gameattrs as GA, climate  # noqa: E402
from planet.lineages import prey as PR  # noqa: E402
from tools.earth_data import earth_on_grid, earth_clouds, earth_potveg, earth_mod17_npp, cell_areas  # noqa: E402
from tools import veg_check as VC  # noqa: E402

C_FRAC = PR.C_FRAC  # g C per g dry (the herd module's own factor)


def miami(p, t):
    """Lieth's Miami model, g dry/m2/yr (FAO k1100e04; soilassessment::NPPmodel): min of the rain and temperature curves."""
    return np.minimum(3000 * (1 - np.exp(-0.000664 * p)), 3000 / (1 + np.exp(1.315 - 0.119 * t)))


def deshmukh(p):  # herb-layer peak biomass, g dry/m2 (Deshmukh 1984, Afr J Ecol 22:181, abstract): 8.488 P - 195.768 kg/ha
    return np.maximum(0.8488 * p - 19.5768, 0)


def yang(p):  # mean ANPP, g/m2/yr, 32 ungrazed grassland sites (Yang et al. 2020, LDR 31:2050? p. 844): 0.7 MAP - 41.7
    return np.maximum(0.7 * p - 41.7, 0)


def rosenzweig_coe(p):  # Rosenzweig 1968 as Coe et al. 1976 use it (p. 345): log10 NAAP = 1.66 log10 AE - 1.66, AE = AP to 700 mm
    return 10 ** (1.66 * np.log10(np.clip(p, 1, 700)) - 1.66)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="506694")
    ap.add_argument("--json", default=None)
    ap.add_argument("--tag", default="base")
    ap.add_argument("--model-climate", action="store_true")
    ap.add_argument("--herb-rl", type=float, default=1.0, help="x the herbs' leaf (and root) maintenance respiration rate")
    ap.add_argument("--eps", type=float, default=1.0, help="x all light-use efficiencies (EPS_SCALE 0.8 -> 0.8 x this)")
    ap.add_argument("--trop-eps", type=float, default=1.0, help="x the tropical trees' efficiency")
    ap.add_argument("--trbe-eps", type=float, default=1.0, help="x the tropical evergreen trees' (TrBE) efficiency only")
    ap.add_argument("--kn", type=float, default=None, help="canopy leaf-respiration depth constant for the non-herbs "
                    "(vegetation.KN_RESP; None: as the code has it, 0: every leaf respires alike)")
    a = ap.parse_args()
    if a.kn is not None:
        V._KP[~V.HERBS, 20] = a.kn
    V._KP[[V.IDX["TrBE"], V.IDX["TrBR"]], 0] *= a.trop_eps
    V._KP[V.IDX["TrBE"], 0] *= a.trbe_eps
    herbs = [V.IDX[c] for c in ("C4G", "C3G", "TunH", "WetH")]
    V._KP[herbs, 9] *= a.herb_rl
    V._KP[:, 0] *= a.eps
    w = W.load(S.find_world(a.world))
    grid, L = w["grid"], w["layers"]
    obs = None if a.model_climate else {**earth_on_grid(grid), **earth_clouds(grid)}
    from tools.soil_check import geology
    v = VC.run(grid, L, obs, geology(grid, L))
    s, sm, nu, pot = v["s"], v["sm"], v["eq"]["nu"], v["pot"]
    land = v["land"] & (L["ice"] <= 0)
    area = cell_areas(grid) * 6371.0 ** 2
    P, T = s["precip"], s["temp"]
    npp = sm["npp"]
    nppk = nu * np.maximum(pot["npp"], 0)  # (NP, n) each type's NPP in the cell
    herb = nppk[V.HERBS].sum(0)
    shrub = nppk[V.SHRUBS].sum(0)
    tree = nppk[V.TREES].sum(0)
    # the herds' grazing NPP exactly as gameattrs computes it
    F = dict(land=land, ice=L["ice"], tree=sm["tree"], cover=sm["cover"], lai=sm["lai"], height=sm.get("height", np.zeros(grid.n)),
             npp=npp, temp=T, t_warm=s["tw"], t_cold=s["tc"], p_jul=None, p_jan=None)
    # p_jul/p_jan as the vegetation saw them
    t, tw, tc = L["temperature"].astype(float), L["warm_month"].astype(float), L["cold_month"].astype(float)
    pj, pa = L["precipitation_jul"].astype(float), L["precipitation_jan"].astype(float)
    if obs is not None:
        fill = lambda o, m: np.where(np.isfinite(np.asarray(o, float)), np.asarray(o, float), m)  # noqa: E731
        pj, pa = fill(obs["obs_p_jul"], pj), fill(obs["obs_p_jan"], pa)
    F["p_jul"], F["p_jan"] = pj, pa
    ga = GA.compute(grid.lat, F, nu=nu, raw=True)
    graze = ga["grazing_npp"]
    above = PR.above(P)
    herds = PR.wild(graze, P)
    pv = earth_potveg(grid)
    pvg = np.where(pv > 0, VC.POTVEG_GROUP[pv], -1)
    m17 = earth_mod17_npp(grid)
    mod = np.where(m17["cover"] >= 0.5, m17["npp"], np.nan)
    rep = VC.report(grid, L, v, pv, area, "x")
    out = {"agreement": round(rep["potveg_agreement"], 1), "forest_mkm2": round(rep["forest_mkm2"], 1),
           "savanna_mkm2": round(rep["savanna_grass_mkm2"], 1), "desert_mkm2": round(rep["desert_xeric_mkm2"], 1),
           "burned": round(rep["burned_mkm2"], 2), "vegc": round(rep["vegc_pg"]), "groups": {k: round(x, 1) for k, x in rep["group_mkm2"].items()}}
    out.update({"tag": a.tag, "climate": "model" if a.model_climate else "observed", "npp_pg": float((npp * area * 1e6)[land].sum() / 1e15)})
    lat, lon = grid.lat, grid.lon

    def wmean(x, m):
        mm = m & np.isfinite(x)
        return float((x * area)[mm].sum() / max(area[mm].sum(), 1e-9)) if mm.sum() else float("nan")

    # 1. total NPP by potential-vegetation group (observed vegetation), model / MOD17 / Miami (g C)
    mi = miami(P, T) * C_FRAC
    rows = {}
    for gi, gname in enumerate(VC.GROUPS[:7]):
        m = land & (pvg == gi) & (lat > -60)
        if m.sum() < 5:
            continue
        rows[gname] = dict(n=int(m.sum()), map=round(wmean(P, m)), mat=round(wmean(T, m), 1), model=round(wmean(npp, m)),
                           mod17=round(wmean(mod, m)), miami=round(wmean(mi, m)),
                           herb=round(wmean(herb, m)), shrub=round(wmean(shrub, m)), tree=round(wmean(tree, m)))
    out["by_potveg_group"] = rows
    # 2. total NPP by rain band and temperature band, all land: model / Miami / MOD17
    grid2 = {}
    for t0, t1 in ((-15, 0), (0, 10), (10, 18), (18, 32)):
        for p0, p1 in ((0, 250), (250, 500), (500, 750), (750, 1000), (1000, 1500), (1500, 2500), (2500, 6000)):
            m = land & (T >= t0) & (T < t1) & (P >= p0) & (P < p1) & (lat > -60)
            if m.sum() >= 5:
                grid2[f"T{t0}..{t1} P{p0}..{p1}"] = dict(n=int(m.sum()), model=round(wmean(npp, m)), miami=round(wmean(mi, m)),
                                                         mod17=round(wmean(mod, m)))
    out["by_climate"] = grid2
    # 3. African warm savanna/grassland: herb and grazing ANPP (g dry) vs Deshmukh / Yang / Rosenzweig-Coe, by rain band
    afr = land & (lon > -20) & (lon < 52) & (lat > -35) & (lat < 20) & (T > 18) & np.isin(pvg, [1, 2, 3])
    bands = {}
    for p0, p1 in ((150, 250), (250, 400), (400, 550), (550, 700), (700, 900), (900, 1200)):
        m = afr & (P >= p0) & (P < p1)
        if m.sum() < 3:
            continue
        pm = wmean(P, m)
        bands[f"{p0}-{p1}"] = dict(
            n=int(m.sum()), map=round(pm), npp_c=round(wmean(npp, m)), herb_c=round(wmean(herb, m)), graze_c=round(wmean(graze, m)),
            above=round(wmean(above, m), 2), herb_anpp_dry=round(wmean(herb * above / C_FRAC, m)),
            graze_anpp_dry=round(wmean(graze * above / C_FRAC, m)), mod17_c=round(wmean(mod, m)),
            deshmukh=round(float(deshmukh(pm))), yang=round(float(yang(pm))), rosenzweig_coe=round(float(rosenzweig_coe(pm))),
            herds_t_km2=round(float(np.median(herds[m])), 2), tree_cover=round(wmean(sm["tree"], m), 2))
    out["africa_warm_grassy"] = bands
    # 4. grasslands worldwide (potveg grassland + steppe), herb ANPP vs Yang
    gl = land & (pvg == 2) & (lat > -60)
    gb = {}
    for p0, p1 in ((100, 250), (250, 400), (400, 600), (600, 900), (900, 1400)):
        m = gl & (P >= p0) & (P < p1)
        if m.sum() < 3:
            continue
        pm = wmean(P, m)
        gb[f"{p0}-{p1}"] = dict(n=int(m.sum()), map=round(pm), mat=round(wmean(T, m), 1), npp_c=round(wmean(npp, m)),
                                herb_anpp_dry=round(wmean(herb * above / C_FRAC, m)), above_dry=round(wmean(npp * above / C_FRAC, m)),
                                yang=round(float(yang(pm))), mod17_c=round(wmean(mod, m)))
    out["grassland_world"] = gb
    print(json.dumps({k: out[k] for k in ("tag", "npp_pg", "agreement", "forest_mkm2", "savanna_mkm2", "desert_mkm2", "burned", "vegc")}))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
