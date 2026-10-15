"""Waves, tides and delta types on today's Earth: planet/coast.py against
known values.

    PYTHONPATH=. uv run python tools/coast_check.py [--level 6] [--cache file.npz]

Runs the model climate on the real terrain (as tools/earth_check.py), then
coast.wave_power and coast.tide_range, and prints them at named coasts
next to rough observed values (annual-mean wave power, offshore, from
global wave-energy atlases such as Gunn & Stock-Williams 2012 and Cornett
2008; typical spring tidal ranges from tide tables), and the Galloway
weights the model gives some real deltas (with the model's own discharges
and basins). --cache keeps the climate in an .npz so reruns take seconds.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planet import climate, coast, hydrology, vegetation  # noqa: E402
from planet.geo import R_KM, xyz  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools.earth_data import earth_on_grid  # noqa: E402

TILT = 23.44

# name, lat, lon, observed annual-mean wave power kW/m (lo, hi)
WAVES = [
    ("Ireland W", 53.5, -10.5, 50, 80), ("Scotland NW", 58.3, -7.5, 40, 70), ("Portugal", 40.0, -9.5, 30, 50),
    ("Norway W", 62.0, 4.5, 25, 45), ("Iceland S", 63.2, -19.0, 40, 70),
    ("SW Australia", -34.5, 114.5, 40, 70), ("S Chile", -45.0, -75.5, 60, 100), ("Cape Town", -34.2, 17.8, 35, 50),
    ("New Zealand SW", -46.0, 166.0, 60, 100), ("Tasmania W", -42.0, 144.5, 50, 90),
    ("California", 36.5, -122.5, 25, 40), ("Oregon", 44.5, -124.5, 35, 50), ("British Columbia", 50.5, -128.5, 35, 50),
    ("US East (Hatteras)", 35.0, -75.0, 8, 15), ("Brazil NE", -8.0, -34.5, 8, 15), ("Hawaii N", 21.8, -158.0, 15, 25),
    ("Japan E", 35.5, 141.0, 8, 15), ("India W", 15.0, 73.3, 8, 15), ("Java S", -8.6, 110.5, 20, 35),
    ("Gulf of Mexico (Mississippi)", 28.8, -89.0, 1, 5), ("Gulf of Mexico (Texas)", 27.5, -96.8, 2, 7),
    ("Caribbean (Venezuela)", 11.5, -67.0, 3, 10), ("Mediterranean (Nile)", 31.6, 31.0, 2, 6),
    ("Mediterranean (Gulf of Lion)", 43.0, 4.5, 3, 8), ("Baltic", 55.5, 18.0, 1, 6), ("North Sea S", 52.5, 3.5, 3, 10),
    ("Bay of Bengal head", 21.3, 89.0, 3, 8), ("Black Sea", 43.0, 34.0, 1, 5), ("Persian Gulf", 27.0, 51.5, 0.5, 3),
    ("Red Sea", 20.0, 39.0, 0.5, 3),
    # ice-covered most of the year (rough: open-water seas of 0.5-1 m in Jul-Sep only)
    ("Laptev (Lena delta)", 72.5, 128.0, 0.3, 3), ("Beaufort (Mackenzie)", 70.0, -135.0, 0.5, 4),
    ("Kara (Ob/Yenisei gulfs)", 73.0, 76.0, 0.3, 3),
]

# name, lat, lon, observed typical (spring) tidal range m (lo, hi)
TIDES = [
    ("Bay of Fundy / Gulf of Maine", 44.5, -66.5, 4, 15), ("Patagonia (San Julian)", -49.5, -67.0, 6, 11),
    ("NW Australia (King Sound)", -16.5, 122.5, 6, 11), ("Bay of Bengal head", 21.5, 90.0, 3, 6),
    ("Gulf of Khambhat", 21.0, 72.3, 6, 11), ("English Channel / St Malo", 49.0, -2.5, 5, 12),
    ("Severn / Bristol Channel", 51.2, -4.0, 6, 13), ("Yellow Sea (Incheon)", 37.0, 125.5, 4, 9),
    ("Gulf of California head", 31.0, -114.3, 4, 9), ("Alaska Cook Inlet", 59.5, -152.5, 5, 9),
    ("Amazon mouth", 0.5, -49.0, 3, 6), ("Mekong mouth", 9.5, 106.8, 2, 4), ("Fly mouth (Gulf of Papua)", -8.5, 143.8, 3, 5),
    ("Open Pacific (Hawaii)", 21.3, -157.9, 0.3, 1), ("California", 36.5, -122.5, 1, 2.2),
    ("Mediterranean (Nice)", 43.5, 7.3, 0, 0.4), ("Mediterranean (Nile)", 31.6, 31.0, 0, 0.5),
    ("Baltic", 55.5, 18.0, 0, 0.2), ("Black Sea", 43.0, 34.0, 0, 0.2), ("Gulf of Mexico (Mississippi)", 28.8, -89.0, 0, 0.6),
    ("Gulf of Mexico (Texas)", 27.5, -96.8, 0, 0.8), ("Caribbean (Jamaica)", 17.5, -77.0, 0, 0.5),
    ("Red Sea", 20.0, 39.0, 0, 1.0),
    ("Laptev (Tiksi)", 71.8, 129.5, 0.1, 0.6), ("Beaufort (Mackenzie)", 69.8, -134.5, 0.2, 0.6),
    ("East Siberian (Kolyma)", 69.8, 161.5, 0.1, 0.4),
]

# name, mouth lat, lon, the type it's usually filed under
DELTAS = [("Mississippi", 29.1, -89.3, "river"), ("Nile", 31.4, 31.0, "wave"), ("Ganges-Brahmaputra", 22.0, 90.5, "tide"),
          ("Mekong", 9.8, 106.5, "tide"), ("Niger", 4.5, 6.0, "mixed"), ("Sao Francisco", -10.5, -36.4, "wave"),
          ("Senegal", 15.9, -16.5, "wave"), ("Fly", -8.5, 143.5, "tide"), ("Amazon", 0.0, -50.0, "tide"),
          ("Danube", 45.1, 29.6, "wave"), ("Ebro", 40.7, 0.8, "wave"), ("Po", 44.9, 12.5, "river"),
          ("Yangtze", 31.4, 121.8, "tide"), ("Mackenzie", 69.0, -135.0, "river"), ("Orinoco", 8.6, -61.0, "tide"),
          ("Lena", 72.5, 126.5, "river")]


def nearest(g, lat, lon, mask, max_km=350.0, by=None) -> int:
    """The cell in mask nearest to (lat, lon) within max_km (-1: none); with
    by, the one with the largest `by` within max_km."""
    c = xyz(np.radians(lat), np.radians(lon))
    d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
    d = np.where(mask, d, np.inf)
    if by is not None:
        ok = d <= max_km
        return int(np.argmax(np.where(ok, by, -np.inf))) if ok.any() else -1
    i = int(np.argmin(d))
    return i if d[i] <= max_km else -1


def score(rows):
    """Share of sites within the observed range, and within a factor of 2 of it."""
    hit = sum(lo <= v <= hi for _, v, lo, hi in rows if v is not None)
    near = sum(lo / 2 <= v <= max(hi * 2, 0.2) for _, v, lo, hi in rows if v is not None)
    return hit, near, len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--level", "-l", type=int, default=6)
    ap.add_argument("--cache", help="npz to keep the climate in between runs")
    args = ap.parse_args()
    g = build_grid(args.level)
    d = earth_on_grid(g)
    elev, ice = d["elev"].astype(float), d["ice"].astype(float)
    if args.cache and Path(args.cache).exists():
        z = np.load(args.cache)
        c = {k: z[k] for k in z.files}
    else:
        c, _ = vegetation.coupled_climate(g, elev, 0.0, TILT, ice)
        if args.cache:
            np.savez(args.cache, **c)
    import time
    t0 = time.time()
    wp = coast.wave_power(g, elev, c, ice)
    t1 = time.time()
    tr, det = coast.tide_range(g, elev, detail=True, ice_share=coast.sea_ice_share(g, elev, c).mean(0))
    t2 = time.time()
    print(f"wave_power {t1 - t0:.1f}s, tide_range {t2 - t1:.1f}s")
    ocean = elev <= 0
    coastal = ocean & (np.bincount(np.repeat(np.arange(g.n), np.diff(g.nbr_off)), ~ocean[g.nbr_idx], g.n) > 0)

    print(f"\n{'WAVE POWER kW/m':34s} {'model':>7s}   observed")
    rows = []
    for name, lat, lon, lo, hi in WAVES:
        i = nearest(g, lat, lon, coastal)
        v = float(wp[i]) if i >= 0 else None
        rows.append((name, v, lo, hi))
        flag = "" if v is None else ("ok" if lo <= v <= hi else ("~" if lo / 2 <= v <= hi * 2 else "XX"))
        print(f"  {name:32s} {'-' if v is None else f'{v:.1f}':>7}   {lo}-{hi}  {flag}")
    h, nr, n = score(rows)
    print(f"  in range {h}/{n}, within 2x {nr}/{n}")

    print(f"\n{'TIDAL RANGE m':34s} {'model':>7s}   observed   (connection, shelf amp, funnel, shelf km)")
    rows = []
    for name, lat, lon, lo, hi in TIDES:
        i = nearest(g, lat, lon, coastal)
        v = float(tr[i]) if i >= 0 else None
        rows.append((name, v, lo, hi))
        flag = "" if v is None else ("ok" if lo <= v <= hi else ("~" if lo / 2 <= v <= max(hi * 2, 0.2) else "XX"))
        extra = "" if i < 0 else (f"({det['connection'][i]:.2f}, {det['shelf_amp'][i]:.2f}, {det['funnel'][i]:.2f}, "
                                  f"{det['shelf_km'][i]:.0f})")
        print(f"  {name:32s} {'-' if v is None else f'{v:.2f}':>7}   {lo}-{hi}  {flag:3s} {extra}")
    h, nr, n = score(rows)
    print(f"  in range {h}/{n}, within 2x {nr}/{n}")

    # deltas: the model's own rivers on Earth's terrain
    flow, down, _ = hydrology.rivers_and_lakes(g, elev, c, ice)
    cell_area = 4 * np.pi * R_KM ** 2 / g.n
    q = flow * cell_area * 1e6 / coast.SEC_PER_YR
    land = elev > 0
    mouth = land & (down >= 0) & ~land[np.maximum(down, 0)]
    L = {"elevation": elev, "temperature": c["temp"], "ice": ice}
    print(f"\n{'DELTAS':22s} {'Q m3/s':>8s} {'Qs Mt/yr':>8s} {'waves':>6s} {'tide':>5s}   river  wave  tide   model type (usually)")
    for name, lat, lon, usual in DELTAS:
        i = nearest(g, lat, lon, mouth & (q > 300), 400, by=q)
        if i < 0:
            print(f"  {name:20s} (no model river mouth nearby)")
            continue
        s = int(down[i])
        basin = coast.upstream_cells(down, i)
        qs = coast.river_sediment(L, basin, float(q[i]), cell_area)
        R = coast.plain_radius_km(float(q[i]), 0.0)
        gw = coast.galloway(qs, float(q[i]), float(wp[s]), float(tr[s]), R)
        w = gw["weights"]
        print(f"  {name:20s} {q[i]:8.0f} {qs * coast.SEC_PER_YR / 1e9:8.0f} {wp[s]:6.1f} {tr[s]:5.2f}   "
              f"{w['river']:.2f}  {w['wave']:.2f}  {w['tide']:.2f}   {gw['type']} ({usual})")


if __name__ == "__main__":
    main()
