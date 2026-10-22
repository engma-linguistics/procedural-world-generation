"""The overturning report (PW-572): where deep water sinks, how much, the heat it draws, and how open the sea is.

    PYTHONPATH=. uv run python tools/overturning_report.py [--earth] [--world ID ...] [--level 6] [--dT 0]
                                                       [--set k=v ...] [--json out.json]

The climate is recomputed with today's code on each geography: Earth's real elevation and ice (as
tools/climate_bias.py: vegetation.coupled_climate at --level), or a stored world's elevation and ice, at
its own dT and tilt. With neither flag, Earth. For each, it prints:
- the NH and SH sinking (Sv) and the heat the inflow gives up on its way (PW, ocean.overturning's heat_pw);
- each sinking site: centre, Sv, the density excess that drives it (kg/m3), its area, the size of the
  connected sea it sinks in (km2: a sea smaller than moc_sea_km2 has no deep water of its own) and its
  openness: the sea's share of the area within 1000 km (a semi-enclosed bay ~0.3-0.5, an open polar sea
  ~0.6-0.8);
- the share of each hemisphere's sinking (cell by cell) that is poleward of 55 deg in sea at least 0.55
  open: the planet-relative form of "deep water forms in open polar seas, not in bays";
- on Earth also the sinking by named sea (Nordic, Irminger, Labrador, Baffin, Weddell, Ross, ...), the
  Norwegian coast's winter sea (share of its cells whose coldest month stays above freezing) and
  Fennoscandia's coldest and warmest months against NCEP.
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
from planet import climate, kernels, ocean, vegetation  # noqa: E402
from planet.geo import R_KM, is_land  # noqa: E402
from planet.grid import build_grid  # noqa: E402

OPEN_KM = 1000.0
OPEN_MIN = 0.55
POLAR = 55.0
# (name, lat0, lat1, lon0, lon1); lon may run past 180 (east of the date line)
EARTH_SEAS = [
    ("Nordic Seas", 62, 82, -25, 30),
    ("Barents / Kara", 66, 82, 30, 100),
    ("Irminger / Iceland S", 55, 66, -45, -15),
    ("Labrador Sea", 50, 64, -65, -45),
    ("Baffin Bay", 64, 80, -82, -50),
    ("Hudson Bay", 50, 66, -96, -76),
    ("Arctic >82N", 82, 91, -180, 180),
    ("North Atlantic 40-55N", 40, 55, -70, 0),
    ("North Pacific >40N", 40, 66, 120, 250),
    ("Weddell", -82, -60, -65, 0),
    ("Ross", -82, -65, 155, 215),
    ("Southern Ocean (all)", -90, -50, -180, 180),
]


def openness(grid, sea, idx, km=OPEN_KM):
    """Sea's share (by area) of the disc within km of each cell in idx."""
    area = ocean.cell_area_km2(grid)
    c = np.cos(km / R_KM)
    out = np.empty(len(idx))
    for j, i in enumerate(idx):
        m = grid.centers @ grid.centers[i] >= c
        out[j] = area[m & sea].sum() / area[m].sum()
    return out


def report(grid, c, sea, label, earth=None):
    lat, lon = grid.lat, grid.lon
    area = ocean.cell_area_km2(grid)
    sink = np.where(sea, c["overturning"], 0.0)
    sites = sorted(c["moc_sites"], key=lambda s: -s["sv"])
    lab, k = kernels.components(sea, grid.nbr_off, grid.nbr_idx)
    basin = np.bincount(lab[sea], area[sea], k)
    cells = np.flatnonzero(sink > 1e-4)
    op = dict(zip(cells, openness(grid, sea, cells)))
    R = dict(label=label, sites=[], hemi={})
    for h, hm in (("N", lat > 0), ("S", lat < 0)):
        tot = sink[hm].sum()
        good = sum(sink[i] for i in cells if hm[i] and abs(lat[i]) >= POLAR and op[i] >= OPEN_MIN)
        R["hemi"][h] = dict(sv=float(tot), heat_pw=float(sum(s["heat_pw"] for s in sites if np.sign(s["lat"]) == (1 if h == "N" else -1))),
                            open_polar_share=float(good / tot) if tot > 0 else float("nan"))
    print(f"=== overturning: {label} ===")
    for h, r in R["hemi"].items():
        print(f"  {h}H sinking {r['sv']:5.2f} Sv, heat {r['heat_pw']:5.3f} PW, poleward of {POLAR:.0f} in open sea "
              f"(>= {OPEN_MIN} within {OPEN_KM:.0f} km): {100 * r['open_polar_share']:3.0f}%")
    print(f"  {'lat':>6s} {'lon':>7s} {'Sv':>6s} {'drho':>6s} {'heat PW':>7s} {'area km2':>9s} {'basin Mkm2':>10s} {'open':>5s}")
    for s in sites:
        v = np.array([np.cos(np.radians(s["lat"])) * np.cos(np.radians(s["lon"])),
                      np.cos(np.radians(s["lat"])) * np.sin(np.radians(s["lon"])), np.sin(np.radians(s["lat"]))])
        j = int(cells[np.argmax(grid.centers[cells] @ v)])  # (the site's nearest sinking cell)
        o = float(openness(grid, sea, [j])[0])
        b = float(basin[lab[j]]) / 1e6
        R["sites"].append(dict(**s, basin_mkm2=b, openness=o))
        print(f"  {s['lat']:6.1f} {s['lon']:7.1f} {s['sv']:6.2f} {s['drho']:6.3f} {s['heat_pw']:7.3f} {s['area_km2']:9.0f} "
              f"{b:10.1f} {o:5.2f}")
    if earth is not None:
        d = earth
        R["seas"] = {}
        lo360 = np.where(lon < 0, lon + 360, lon)
        print("  by sea (Sv): " + ", ".join(
            f"{nm} {_box_sum(sink, lat, lon, lo360, b):.2f}" for nm, *b in EARTH_SEAS if _box_sum(sink, lat, lon, lo360, b) > 0.05))
        for nm, *b in EARTH_SEAS:
            R["seas"][nm] = _box_sum(sink, lat, lon, lo360, b)
        land = ~sea
        nw = sea & (lat > 62) & (lat < 72) & (lon > -5) & (lon < 15)
        fs = land & (d["ice"] <= 0) & (lat > 58) & (lat < 71) & (lon > 5) & (lon < 32) & np.isfinite(d["obs_t_cold"])
        w = ocean.cell_area_km2(grid)
        open_w = float(w[nw & (c["sst_jan"] > climate.FREEZE + 0.2)].sum() / w[nw].sum())
        f = lambda x, m: float((x * w)[m].sum() / w[m].sum())
        R["norway"] = dict(open_winter=open_w, sea_air_cold=f(c["t_cold"], nw), sst_cold=f(c["sst_jan"], nw),
                           fenno_tc=f(c["t_cold"], fs), fenno_tc_obs=f(d["obs_t_cold"], fs),
                           fenno_tw=f(c["t_warm"], fs), fenno_tw_obs=f(d["obs_t_warm"], fs))
        r = R["norway"]
        print(f"  Norwegian coast sea (62-72N 5W-15E): open in winter {100 * open_w:.0f}% of area, coldest-month SST "
              f"{r['sst_cold']:.1f} C, sea air {r['sea_air_cold']:.1f} C (NCEP ~+3.5)")
        print(f"  Fennoscandia (ice-free land): coldest month {r['fenno_tc']:.1f} vs {r['fenno_tc_obs']:.1f} "
              f"({r['fenno_tc'] - r['fenno_tc_obs']:+.1f}), warmest {r['fenno_tw']:.1f} vs {r['fenno_tw_obs']:.1f} "
              f"({r['fenno_tw'] - r['fenno_tw_obs']:+.1f})")
    return R


def _box_sum(x, lat, lon, lo360, b):
    a, z, l0, l1 = b
    L = lo360 if l1 > 180 else lon
    return float(x[(lat >= a) & (lat < z) & (L >= l0) & (L < l1)].sum())


def earth(level, dT, tune):
    from tools import earth_data
    grid = build_grid(level)
    d = earth_data.earth_on_grid(grid)
    c = _with_tune(tune, lambda: vegetation.coupled_climate(grid, d["elev"].astype(np.float64), dT, 23.4,
                                                          d["ice"].astype(np.float64))[0])
    return grid, c, earth_data.land_of(d), d


def _with_tune(tune, f):
    old = dict(climate.TUNE)
    climate.TUNE.update(tune)
    try:
        return f()
    finally:
        climate.TUNE.clear()
        climate.TUNE.update(old)


def world(wid, tune):
    from planet import store
    d = json.loads(store.find("world", wid).read_text())
    m = d["meta"]
    grid = build_grid(int(m["level"]))
    elev = np.asarray(d["layers"]["elevation"], np.float64)
    ice = np.asarray(d["layers"].get("ice", np.zeros(grid.n)), np.float64)
    p = m.get("params", {})
    c = _with_tune(tune, lambda: climate.compute(grid, elev, float(p.get("dT", 0.0)), float(p.get("tilt", 23.4)), ice))
    return grid, c, is_land(elev, ice)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--earth", action="store_true")
    ap.add_argument("--world", nargs="*", default=[])
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
        tune[k] = type(climate.TUNE[k])(float(v))
    out = []
    if a.earth or not a.world:
        t0 = time.time()
        grid, c, land, d = earth(a.level, a.dT, tune)
        out.append(report(grid, c, ~land, f"Earth L{a.level}, dT {a.dT:+.1f} ({time.time() - t0:.0f} s)", earth=d))
    for wid in a.world:
        t0 = time.time()
        grid, c, land = world(wid, tune)
        out.append(report(grid, c, ~land, f"world {wid} L{grid.level} ({time.time() - t0:.0f} s)"))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
