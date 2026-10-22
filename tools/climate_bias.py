"""The base climate's biases where they matter for ice, on the real Earth (base-climate review, v2).

    PYTHONPATH=. uv run python tools/climate_bias.py [--level 6] [--dT 0] [--set k=v ...] [--json out.json]

The model gets Earth's real elevation and ice (as tools/earth_check.py, with the vegetation's feedbacks:
vegetation.coupled_climate) and is compared with NCEP/NCAR 2 m air temperature (1981-2010, ~1.9 deg) and
GPCC (land) / GPCP (sea) precipitation, mapped onto the same cells. earth_check covers the whole globe;
this tool looks at what an ice sheet feels and at the mechanisms behind the biases:

  1. ice regions: warmest / coldest month, annual mean and precipitation on the margins and inception
     areas of past and present ice (Labrador, Arctic Canada, Fennoscandia, Greenland's ice-free rim and its
     ice, Antarctica's coast and interior, the Southern Ocean's sea-ice zone, ...), land split into bare
     and iced cells.
  2. continentality: the land's seasonal range (warmest - coldest month) by distance from the sea, model
     against observed, poleward of 35 deg. This tests the land/sea air rule (climate._air_temps) on any
     geography, not on named places.
  3. west and east coasts: the coldest month on land within 600 km of a sea on the upwind (west) or
     downwind (east) side, 40-65 N, model against observed: how much the westerlies carry the sea's
     winter warmth inland, and how much colder the lee coasts are.
  4. the summer heat: the warmest month on land 35-65 deg by summer rain (wet, dry): whether the summer
     bias follows the land's water (the evaporative cooling) or the latitude.
  5. winter sea ice (a proxy): sea cells whose coldest month is below -5 C, area per hemisphere, model
     against NCEP's 2 m air (the same proxy on both sides; no sea-ice dataset is in the Earth cache).

NCEP's 2 m air is coarse and is known to run warm on the high Antarctic plateau and to smooth Greenland's
margins; for Greenland's ice use tools/tz_earth.py --greenland (RACMO2.3p3). --dT shifts the model's
climate (the observations stay today's); --set changes climate.TUNE entries (k=v) for a test.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps)
import numpy as np  # noqa: E402
from planet import climate, kernels, vegetation  # noqa: E402
from planet.geo import R_KM, xyz  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data  # noqa: E402
from tools.earth_data import cell_areas  # noqa: E402

# (name, lat0, lat1, lon0, lon1, surface): surface 'land' (ice-free land), 'ice' (land ice), 'sea', 'all land'
ICE_REGIONS = [
    ("Labrador / Quebec N", 52, 62, -80, -56, "land"),
    ("Hudson Bay lowlands", 50, 60, -95, -80, "land"),
    ("Keewatin / Nunavut", 60, 70, -105, -85, "land"),
    ("Arctic Canada islands", 70, 83, -125, -60, "land"),
    ("Baffin Island", 62, 73, -80, -62, "land"),
    ("Alaska / Yukon", 60, 70, -160, -130, "land"),
    ("Canadian Rockies", 50, 60, -125, -114, "land"),
    ("Great Lakes / Midwest", 40, 50, -95, -75, "land"),
    ("Fennoscandia", 58, 71, 5, 32, "land"),
    ("Kola / Karelia", 62, 70, 30, 42, "land"),
    ("Svalbard / Franz Josef", 76, 82, 10, 65, "all land"),
    ("Iceland", 63, 67, -25, -13, "all land"),
    ("Taymyr / Putorana", 66, 78, 85, 110, "land"),
    ("Alps", 44, 48, 5, 15, "land"),
    ("Tibet", 30, 36, 80, 95, "land"),
    ("Patagonia", -55, -40, -76, -65, "all land"),
    ("Greenland rim (bare)", 59, 84, -75, -10, "land"),
    ("Greenland ice", 59, 84, -75, -10, "ice"),
    ("Antarctic coast ice (<1500 m)", -90, -60, -180, 180, "ice<1500"),
    ("Antarctic plateau (>2500 m)", -90, -60, -180, 180, "ice>2500"),
    ("Southern Ocean 60-70S", -70, -60, -180, 180, "sea"),
    ("Arctic Ocean >75N", 75, 90, -180, 180, "sea"),
    ("Labrador Sea / Baffin Bay", 55, 75, -70, -45, "sea"),
    ("Nordic Seas", 62, 78, -20, 20, "sea"),
    ("Barents Sea", 68, 80, 20, 60, "sea"),
]


def _wm(x, w, m):
    return float((x * w)[m].sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")


def _in(lat, lon, a, b, lo, hi):
    return (lat >= a) & (lat < b) & (lon >= lo) & (lon < hi)


def coast_distance(grid, land):
    """km from each land cell to the nearest sea cell (grid hops x spacing)."""
    coast = np.flatnonzero(land & (np.add.reduceat(~land[grid.nbr_idx], grid.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(coast, land.astype(np.int64), grid.nbr_off, grid.nbr_idx, 10**6)
    return np.where(land & (hops >= 0), hops * grid.spacing * R_KM + 0.5 * grid.spacing * R_KM, np.inf)


def side_of_sea(grid, land, km=600.0, step_deg=1.0):
    """Land within km of a sea that lies to its west (upwind in the westerlies) or its east (downwind), found
    by walking along the parallel. Returns (west_sea, east_sea) masks; a cell can be in both."""
    lat, lon = grid.lat, grid.lon
    west, east = np.zeros(grid.n, bool), np.zeros(grid.n, bool)
    cand = np.flatnonzero(land & (np.abs(lat) >= 35) & (np.abs(lat) <= 70))
    for sgn, out in ((-1, west), (1, east)):
        d = step_deg
        while True:
            dkm = d * np.pi / 180 * R_KM * np.cos(np.radians(lat[cand]))
            live = dkm <= km
            if not live.any():
                break
            c = cand[live]
            lo2 = ((lon[c] + sgn * d + 180) % 360) - 180
            idx = grid.locate(xyz(np.radians(lat[c]), np.radians(lo2)), c)
            out[c[~land[idx]]] = True
            d += step_deg
    return west, east


def run(level, dT, tune):
    t0 = time.time()
    grid = build_grid(level)
    d = earth_data.earth_on_grid(grid)
    elev, ice = d["elev"].astype(np.float64), d["ice"].astype(np.float64)
    old = dict(climate.TUNE)
    climate.TUNE.update(tune)
    try:
        c = vegetation.coupled_climate(grid, elev, dT, 23.4, ice)[0]
    finally:
        climate.TUNE.clear()
        climate.TUNE.update(old)
    return grid, d, c, time.time() - t0


def analyse(grid, d, c) -> dict:
    lat, lon = grid.lat, grid.lon
    w = cell_areas(grid)
    land = earth_data.land_of(d)
    iced = land & (d["ice"] > 0)
    bare = land & ~iced
    surf = d["elev"] + d["ice"]
    ok_t = np.isfinite(d["obs_temp"])
    R = {"regions": [], "continentality": [], "coasts": {}, "summer": [], "sea_ice": {}}
    for name, a, b, lo, hi, kind in ICE_REGIONS:
        box = _in(lat, lon, a, b, lo, hi) & ok_t
        m = {"land": box & bare, "all land": box & land, "ice": box & iced, "sea": box & ~land,
             "ice<1500": box & iced & (surf < 1500), "ice>2500": box & iced & (surf > 2500)}[kind]
        p_obs = np.where(land, d["obs_precip"], d["obs_gpcp"])
        row = dict(name=name, kind=kind, cells=int(m.sum()),
                   Tw=_wm(c["t_warm"], w, m), Tw_obs=_wm(d["obs_t_warm"], w, m),
                   Tc=_wm(c["t_cold"], w, m), Tc_obs=_wm(d["obs_t_cold"], w, m),
                   T=_wm(c["temp"], w, m), T_obs=_wm(d["obs_temp"], w, m),
                   P=_wm(c["precip"], w, m & np.isfinite(p_obs)), P_obs=_wm(p_obs, w, m & np.isfinite(p_obs)),
                   elev=_wm(surf, w, m))
        R["regions"].append(row)
    # 2. continentality, poleward of 35 deg, ice-free land
    dist = coast_distance(grid, land)
    rng_m, rng_o = c["t_warm"] - c["t_cold"], d["obs_t_warm"] - d["obs_t_cold"]
    for hemi, hm in (("N", lat >= 35), ("S", lat <= -35)):
        for lo_km, hi_km in ((0, 150), (150, 400), (400, 800), (800, 1500), (1500, 1e9)):
            m = bare & hm & ok_t & (dist >= lo_km) & (dist < hi_km)
            R["continentality"].append(dict(hemi=hemi, km=f"{lo_km:.0f}-{hi_km:.0f}" if hi_km < 1e8 else f">{lo_km:.0f}",
                                            cells=int(m.sum()), range=_wm(rng_m, w, m), range_obs=_wm(rng_o, w, m),
                                            Tw_bias=_wm(c["t_warm"] - d["obs_t_warm"], w, m),
                                            Tc_bias=_wm(c["t_cold"] - d["obs_t_cold"], w, m)))
    # 3. west vs east coasts, 40-65 N
    west, east = side_of_sea(grid, land)
    band = bare & ok_t & (lat >= 40) & (lat <= 65)
    for nm, m in (("sea to the west (only)", band & west & ~east), ("sea to the east (only)", band & east & ~west),
                  ("both", band & west & east), ("neither (interior)", band & ~west & ~east)):
        R["coasts"][nm] = dict(cells=int(m.sum()), Tc=_wm(c["t_cold"], w, m), Tc_obs=_wm(d["obs_t_cold"], w, m),
                               Tw=_wm(c["t_warm"], w, m), Tw_obs=_wm(d["obs_t_warm"], w, m))
    # 4. summer heat by summer rain, 35-65 deg
    north = lat >= 0
    p_sum_obs = np.where(north, d["obs_p_jul"], d["obs_p_jan"])
    for hemi, hm in (("N", (lat >= 35) & (lat <= 65)), ("S", (lat <= -35) & (lat >= -65))):
        for lo_mm, hi_mm in ((0, 300), (300, 700), (700, 1200), (1200, 1e9)):
            m = bare & hm & ok_t & np.isfinite(p_sum_obs) & (p_sum_obs >= lo_mm) & (p_sum_obs < hi_mm)
            R["summer"].append(dict(hemi=hemi, mm=f"{lo_mm:.0f}-{hi_mm:.0f}" if hi_mm < 1e8 else f">{lo_mm:.0f}",
                                    cells=int(m.sum()), Tw_bias=_wm(c["t_warm"] - d["obs_t_warm"], w, m),
                                    P_sum=_wm(np.where(north, c["p_jul"], c["p_jan"]), w, m),
                                    P_sum_obs=_wm(p_sum_obs, w, m)))
    # 5. winter sea-ice proxy
    a_km2 = w / w.sum() * 4 * np.pi * R_KM**2
    sea = ~land & ok_t
    for hemi, hm in (("N", lat > 0), ("S", lat < 0)):
        R["sea_ice"][hemi] = dict(model=float(a_km2[sea & hm & (c["t_cold"] < -5)].sum() / 1e6),
                                  obs=float(a_km2[sea & hm & (d["obs_t_cold"] < -5)].sum() / 1e6))
    return R


def report(R, level, dT, secs):
    print(f"=== base-climate biases for ice, Earth L{level}, model dT {dT:+.1f} ({secs:.0f} s) ===")
    print("\n1. Ice regions (model - observed; T C vs NCEP 2 m, P mm/yr vs GPCC/GPCP)")
    print(f"{'region':32s} {'kind':9s} {'n':>4s} {'elev':>5s} | {'Tw':>6s} {'obs':>6s} {'bias':>5s} | {'Tc':>6s} {'obs':>6s} "
          f"{'bias':>5s} | {'T':>6s} {'bias':>5s} | {'P':>5s} {'Pobs':>5s} {'ratio':>5s}")
    for r in R["regions"]:
        if r["cells"] == 0:
            continue
        print(f"{r['name']:32s} {r['kind']:9s} {r['cells']:4d} {r['elev']:5.0f} | {r['Tw']:6.1f} {r['Tw_obs']:6.1f} "
              f"{r['Tw'] - r['Tw_obs']:+5.1f} | {r['Tc']:6.1f} {r['Tc_obs']:6.1f} {r['Tc'] - r['Tc_obs']:+5.1f} | "
              f"{r['T']:6.1f} {r['T'] - r['T_obs']:+5.1f} | {r['P']:5.0f} {r['P_obs']:5.0f} "
              f"{r['P'] / max(r['P_obs'], 1e-9):5.2f}")
    print("\n2. Continentality: seasonal range (warmest - coldest month) of ice-free land poleward of 35 deg, "
          "by distance from the sea")
    print(f"{'hemi':4s} {'km':>10s} {'n':>5s} | {'range':>6s} {'obs':>6s} | {'Tw bias':>7s} {'Tc bias':>7s}")
    for r in R["continentality"]:
        if r["cells"]:
            print(f"{r['hemi']:4s} {r['km']:>10s} {r['cells']:5d} | {r['range']:6.1f} {r['range_obs']:6.1f} | "
                  f"{r['Tw_bias']:+7.1f} {r['Tc_bias']:+7.1f}")
    print("\n3. Coasts 40-65 N (ice-free land within 600 km of a sea along its parallel)")
    for nm, r in R["coasts"].items():
        print(f"  {nm:24s} n {r['cells']:4d}  coldest {r['Tc']:6.1f} vs {r['Tc_obs']:6.1f} ({r['Tc'] - r['Tc_obs']:+.1f})"
              f"   warmest {r['Tw']:5.1f} vs {r['Tw_obs']:5.1f} ({r['Tw'] - r['Tw_obs']:+.1f})")
    print("\n4. Summer heat by observed summer-half rain (ice-free land 35-65 deg)")
    for r in R["summer"]:
        if r["cells"]:
            print(f"  {r['hemi']} {r['mm']:>9s} mm  n {r['cells']:4d}  warmest month bias {r['Tw_bias']:+5.1f} C   "
                  f"summer rain {r['P_sum']:5.0f} vs {r['P_sum_obs']:5.0f}")
    print("\n5. Winter sea-ice proxy (sea whose coldest month < -5 C), Mkm2")
    for h, r in R["sea_ice"].items():
        print(f"  {h}: model {r['model']:5.1f}  NCEP {r['obs']:5.1f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--dT", type=float, default=0.0)
    ap.add_argument("--set", nargs="*", default=[], help="climate.TUNE entries k=v")
    ap.add_argument("--json")
    a = ap.parse_args()
    tune = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in climate.TUNE:
            raise SystemExit(f"unknown TUNE key {k}")
        tune[k] = type(climate.TUNE[k])(float(v)) if not isinstance(climate.TUNE[k], tuple) else eval(v)
    grid, d, c, secs = run(a.level, a.dT, tune)
    R = analyse(grid, d, c)
    report(R, a.level, a.dT, secs)
    if a.json:
        Path(a.json).write_text(json.dumps(dict(level=a.level, dT=a.dT, tune=tune, **R), indent=1))


if __name__ == "__main__":
    main()
