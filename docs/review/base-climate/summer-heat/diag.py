"""Lane 121 (PW-1279 / PW-1322): Earth's warm-month bias by band and region, with swaps into the summer energy split.

    PYTHONPATH=. uv run python docs/review/base-climate/summer-heat/diag.py MODE [--level 7] [--tune k=v,...] [--out DIR]

MODE (comma-separated, combined):
  base     the model as it is
  rain     GPCC's observed rain (land) into climate.water_balance, so the summer split's evaporation is the
           observed rain's (the cloud and the rain kernel keep the model's rain)
  le       NCEP's summer latent heat flux in place of the split's evaporation (planet/climate.py::_summer_split)
  sun      CRU's summer sunshine share in place of the split's sunshine(cloud)
  nosplit  the split's warming set to 0 (what the split adds at all)
Reads data/earth (the worktree's private copy); writes DIR/MODE.json and DIR/MODE.npz.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, vegetation  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data  # noqa: E402
from tools.earth_check import REGIONS  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("mode")
ap.add_argument("--level", type=int, default=7)
ap.add_argument("--tune", default="")
ap.add_argument("--out", default="/tmp/claude-1000/-data-personal-repos-procedural-world-generation/"
                "43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l121/diag")
a = ap.parse_args()
modes = set(a.mode.split(","))
for kv in filter(None, a.tune.split(",")):
    k, v = kv.split("=")
    assert k in climate.TUNE, k
    climate.TUNE[k] = float(v)

grid = build_grid(a.level)
d = earth_data.earth_on_grid(grid)
cl = earth_data.earth_clouds(grid)
elev, ice = d["elev"].astype(np.float64), d["ice"].astype(np.float64)
land = earth_data.land_of(d)
north = grid.lat >= 0

# observed summer-half latent heat (W/m2, NCEP, upward) and sunshine share (CRU)
r = earth_data.raster("ncep_lhtfl")
v = np.where(np.abs(r["val"]) > 1e20, np.nan, r["val"]).astype(np.float64)
m = earth_data._bilinear(r, v, grid.lat, grid.lon)
le_obs = np.where(north, m[3:9].mean(0), np.concatenate([m[:3], m[9:]]).mean(0))
sun_obs = np.where(north, cl["obs_sun_jul"], cl["obs_sun_jan"]).astype(np.float64)
pj, pn = d["obs_p_jul"].astype(np.float64), d["obs_p_jan"].astype(np.float64)
okp = land & np.isfinite(pj) & np.isfinite(pn)

rec = {}
orig_wb, orig_split = climate.water_balance, climate._summer_split


def wb(lat, temp, t_warm, t_cold, p_jul, p_jan, *args, **kw):
    if "rain" in modes and len(p_jul) == grid.n:
        p_jul, p_jan = np.where(okp, pj, p_jul), np.where(okp, pn, p_jan)
    return orig_wb(lat, temp, t_warm, t_cold, p_jul, p_jan, *args, **kw)


def split(lat, tilt, north_, aet_half, pet_half, cloud_sum, tune, *extra):
    """planet/climate.py::_summer_split, with its two terms kept and the swaps."""
    S = climate.insolation(np.asarray(lat, float), tilt) * 1e6 / 86400.0
    s_sum = np.where(north_, S[3:9].mean(0), np.concatenate([S[:3], S[9:]]).mean(0))
    ground = (1 - tune["albedo_ref"]) * s_sum
    sun = climate.sunshine(cloud_sum)
    if "sun" in modes:
        sun = np.where(np.isfinite(sun_obs), sun_obs, sun)
    sw = ground * (0.25 + 0.5 * sun)
    sw_ref = ground * (0.25 + 0.5 * climate.sunshine(np.full_like(cloud_sum, tune["cloud_ref"])))
    i, sm = np.arange(len(lat)), np.where(north_, 0, 1)
    to_w = climate.LATENT * 1e6 / (0.5 * climate.YEAR_S)
    le, le_ref = aet_half[sm, i] * to_w, tune["ef_ref"] * pet_half[sm, i] * to_w
    if "le" in modes:
        le = np.where(np.isfinite(le_obs), le_obs, le)
    k = tune["sum_tau"] / (climate.RHO_C_AIR * tune["sum_h"])
    out = k * ((sw - le) - (sw_ref - le_ref))
    rec.update(sw=sw, sw_ref=sw_ref, le=le, le_ref=le_ref, pet=pet_half[sm, i] * to_w, sun=sun, k=k,
               aet_mm=aet_half[sm, i], pet_mm=pet_half[sm, i])
    if modes == {"base"}:  # (the model's own split, with any candidate knobs: --tune)
        out = orig_split(lat, tilt, north_, aet_half, pet_half, cloud_sum, tune, *extra)
    if "nosplit" in modes:
        out = np.zeros_like(out)
    rec["d_sum"] = out
    return out


climate.water_balance, climate._summer_split = wb, split
c, _ = vegetation.coupled_climate(grid, elev, 0.0, 23.4, ice)

w = earth_data.cell_areas(grid)
open_land = land & (ice <= 0) & (grid.lat > -60)
ow, ot, oc_ = (d[k].astype(np.float64) for k in ("obs_t_warm", "obs_temp", "obs_t_cold"))
mw, mt, mc = c["t_warm"], c["temp"], c["t_cold"]
cont = np.clip(climate.smooth(grid, land.astype(float), 1000.0), 0, 1)


def wm(x, msk):
    msk = msk & np.isfinite(x)
    return float((x * w)[msk].sum() / w[msk].sum()) if msk.any() else float("nan")


res = dict(mode=a.mode, tune=a.tune, bands={}, regions={}, cont={})
alat = np.abs(grid.lat)
for lo, hi in ((0, 10), (10, 20), (0, 20), (20, 30), (30, 40), (20, 40), (40, 60)):
    b = open_land & (alat >= lo) & (alat < hi)
    res["bands"][f"{lo}-{hi}"] = dict(
        warm=wm(mw, b), warm_obs=wm(ow, b), ann=wm(mt, b), ann_obs=wm(ot, b), cold=wm(mc, b), cold_obs=wm(oc_, b),
        d_sum=wm(rec["d_sum"], b), sw_term=wm(rec["k"] * (rec["sw"] - rec["sw_ref"]), b),
        le_term=wm(-rec["k"] * (rec["le"] - rec["le_ref"]), b), le=wm(rec["le"], b), le_obs=wm(le_obs, b),
        sun=wm(rec["sun"], b), sun_obs=wm(sun_obs, b), p=wm(c["precip"], b), p_obs=wm(d["obs_precip"], b),
        p_sum=wm(np.where(north, c["p_jul"], c["p_jan"]), b), p_sum_obs=wm(np.where(north, pj, pn), b),
        ge30=wm((mw >= 30).astype(float), b), ge30_obs=wm((ow >= 30).astype(float), b))
for name in ("all",):
    b = open_land
    res["share"] = dict(ge30=wm((mw >= 30).astype(float), b), ge30_obs=wm((ow >= 30).astype(float), b),
                        ge35=wm((mw >= 35).astype(float), b), ge35_obs=wm((ow >= 35).astype(float), b))
for lo, hi in ((0, 0.4), (0.4, 0.7), (0.7, 0.9), (0.9, 1.01)):
    for blo, bhi in ((0, 20), (20, 40)):
        b = open_land & (cont >= lo) & (cont < hi) & (alat >= blo) & (alat < bhi)
        res["cont"][f"{blo}-{bhi} cont {lo}-{hi}"] = dict(warm=wm(mw, b), warm_obs=wm(ow, b), ann=wm(mt, b),
                                                         ann_obs=wm(ot, b), area=float(w[b].sum() / w[open_land].sum()))
for nm, la0, la1, lo0, lo1 in REGIONS:
    b = open_land & (grid.lat >= la0) & (grid.lat <= la1) & (grid.lon >= lo0) & (grid.lon <= lo1)
    if not b.any():
        continue
    res["regions"][nm] = dict(warm=wm(mw, b), warm_obs=wm(ow, b), ann=wm(mt, b), ann_obs=wm(ot, b),
                              d_sum=wm(rec["d_sum"], b), le=wm(rec["le"], b), le_obs=wm(le_obs, b),
                              sun=wm(rec["sun"], b), sun_obs=wm(sun_obs, b), p=wm(c["precip"], b),
                              p_obs=wm(d["obs_precip"], b), cloud=wm(np.where(north, c["cloud_jul"], c["cloud_jan"]), b))
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
tag = a.mode.replace(",", "+") + (("_" + a.tune.replace("=", "").replace(",", "_")) if a.tune else "")
(out / f"{tag}.json").write_text(json.dumps(res, indent=1))
np.savez_compressed(out / f"{tag}.npz", t_warm=mw, temp=mt, t_cold=mc, d_sum=rec["d_sum"], le=rec["le"],
                    le_ref=rec["le_ref"], sw=rec["sw"], sw_ref=rec["sw_ref"], sun=rec["sun"], precip=c["precip"],
                    p_jul=c["p_jul"], p_jan=c["p_jan"], cloud_jul=c["cloud_jul"], cloud_jan=c["cloud_jan"],
                    le_obs=le_obs, sun_obs=sun_obs, cont=cont, open_land=open_land, w=w)
print(tag, json.dumps(res["share"]))
for k, b in res["bands"].items():
    print(f"{k:>6} warm {b['warm']:.1f}/{b['warm_obs']:.1f} ann {b['ann']:.1f}/{b['ann_obs']:.1f} "
          f"cold {b['cold']:.1f}/{b['cold_obs']:.1f} d_sum {b['d_sum']:+.2f} (sw {b['sw_term']:+.2f} "
          f"le {b['le_term']:+.2f}) LE {b['le']:.0f}/{b['le_obs']:.0f} sun {b['sun']:.2f}/{b['sun_obs']:.2f} "
          f"Psum {b['p_sum']:.0f}/{b['p_sum_obs']:.0f}")
