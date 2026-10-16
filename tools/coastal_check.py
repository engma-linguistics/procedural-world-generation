"""Coastal and shallow-sea life (coastal.py, PW-188) on Earth, against
what is observed: global areas, latitude limits and named places.

    PYTHONPATH=. uv run python tools/coastal_check.py [--level 6] [--world ID] [--png out.png]

Without --world it builds the Earth world in memory (tools/earth_world.py:
ETOPO1 terrain, the model's climate, waves and tides). Earth is a test
analogue, not a target: the numbers are for judging whether the rules are
sound, not for tuning them.

Observed (global):
  coral reefs     ~250,000-285,000 km^2 (Spalding & Grenfell 1997; Spalding et al. 2001)
  mangroves       ~138,000 km^2 (Giri et al. 2011; Global Mangrove Watch 2016: ~136,000)
  salt marsh      ~55,000 km^2 mapped, likely 2-4x that (Mcowen et al. 2017)
  seagrass        ~160,000 km^2 mapped, ~270,000-600,000 likely (McKenzie et al. 2020)
  kelp forests    ~1.5-2 million km^2 of suitable rocky coast (Jayathilake & Costello 2020; Wernberg et al. 2019)
  latitude limits reefs to ~32 deg (Bermuda, Lord Howe, Japan ~33-35); mangroves to ~32 N
                  (Japan, Bermuda) and ~38-39 S (New Zealand, Victoria); kelp mostly poleward
                  of ~25-30 deg, closer to the equator only in upwelling (Peru, Galapagos, Oman)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planet import coastal as C  # noqa: E402
from planet.geo import R_KM, xyz  # noqa: E402

OBSERVED_KM2 = {"reef": (250e3, 285e3), "mangrove": (130e3, 140e3), "salt_marsh": (55e3, 220e3),
                "seagrass": (160e3, 600e3), "kelp": (1.5e6, 2.0e6)}
OBS_LAT = {"reef": "~32 N / ~32 S", "mangrove": "~32 N / ~39 S", "salt_marsh": "~70 N / ~55 S",
           "seagrass": "~70 N / ~45 S", "kelp": "~80 N / ~60 S (equatorward of 25 deg only with upwelling)"}
# (name, lat, lon, layer, present?)
SITES = [
    ("Great Barrier Reef", -18.0, 147.5, "reef", True), ("Red Sea", 22.0, 38.0, "reef", True),
    ("Belize barrier reef", 17.0, -87.8, "reef", True), ("Bahamas", 24.0, -77.0, "reef", True),
    ("Indonesia (Flores)", -8.0, 120.0, "reef", True), ("Maldives", 4.0, 73.5, "reef", True),
    ("New Caledonia", -21.5, 165.5, "reef", True), ("Florida Keys", 24.7, -81.0, "reef", True),
    ("Amazon mouth", 1.0, -49.0, "reef", False), ("Ganges mouth", 21.0, 90.0, "reef", False),
    ("Peru (upwelling)", -12.0, -77.5, "reef", False), ("California", 34.0, -120.0, "reef", False),
    ("Mediterranean", 38.0, 18.0, "reef", False),
    ("Sundarbans", 21.8, 89.3, "mangrove", True), ("Niger delta", 4.5, 6.5, "mangrove", True),
    ("Para coast (Brazil)", -0.8, -47.0, "mangrove", True), ("Gulf of Papua", -8.0, 144.0, "mangrove", True),
    ("Mekong delta", 9.3, 106.3, "mangrove", True), ("Everglades", 25.3, -81.0, "mangrove", True),
    ("Strait of Malacca", 2.0, 101.5, "mangrove", True), ("Guinea-Bissau", 11.5, -15.8, "mangrove", True),
    ("Zambezi delta", -18.8, 36.3, "mangrove", True), ("Gulf of Carpentaria", -16.0, 141.0, "mangrove", True),
    ("Mediterranean", 38.0, 18.0, "mangrove", False), ("Chile", -35.0, -72.5, "mangrove", False),
    ("Namibia", -23.0, 14.3, "mangrove", False), ("North Sea", 53.5, 7.0, "mangrove", False),
    ("Wadden Sea", 53.5, 7.5, "salt_marsh", True), ("Georgia (US)", 31.5, -81.2, "salt_marsh", True),
    ("Chesapeake Bay", 37.5, -76.2, "salt_marsh", True), ("Bay of Fundy", 45.3, -64.5, "salt_marsh", True),
    ("Essex (Thames)", 51.6, 1.0, "salt_marsh", True), ("Bahia Blanca", -39.0, -62.0, "salt_marsh", True),
    ("Yellow Sea (Jiangsu)", 33.5, 120.8, "salt_marsh", True), ("Sundarbans", 21.8, 89.3, "salt_marsh", False),
    ("Amazon mouth", 1.0, -49.0, "salt_marsh", False),
    ("Monterey (California)", 36.6, -122.0, "kelp", True), ("Central Chile", -33.0, -71.8, "kelp", True),
    ("Cape Town", -34.0, 18.3, "kelp", True), ("Tasmania", -43.0, 147.8, "kelp", True),
    ("Norway", 62.0, 5.0, "kelp", True), ("Gulf of Maine", 44.0, -68.0, "kelp", True),
    ("Hokkaido", 42.5, 143.5, "kelp", True), ("Falklands", -51.7, -59.0, "kelp", True),
    ("Indonesia", -8.0, 120.0, "kelp", False), ("Caribbean", 17.0, -75.0, "kelp", False),
    ("Baltic proper", 58.0, 19.5, "kelp", False),
    ("Shark Bay", -25.8, 113.6, "seagrass", True), ("Florida Bay", 25.0, -81.0, "seagrass", True),
    ("Balearics (Posidonia)", 39.5, 3.0, "seagrass", True), ("Wadden Sea", 53.5, 7.5, "seagrass", True),
    ("Torres Strait", -10.0, 142.5, "seagrass", True), ("Persian Gulf", 26.5, 51.0, "seagrass", True),
    ("Weddell Sea", -72.0, -45.0, "seagrass", False), ("Kara Sea", 74.0, 70.0, "seagrass", False),
]
PRESENT = 1.0  # % of a cell, at the place or within NEAR_KM: "present"
NEAR_KM = 250.0


def sites(grid, L) -> list[tuple]:
    out = []
    for name, lat, lon, layer, want in SITES:
        p = xyz(np.radians(lat), np.radians(lon))
        near = np.arccos(np.clip(grid.centers @ p, -1, 1)) * R_KM <= NEAR_KM
        got = float(np.asarray(L[layer], float)[near].max()) if near.any() else 0.0
        out.append((name, layer, want, got, (got >= PRESENT) == want))
    return out


def lat_limits(grid, L, layer: str) -> tuple[float, float]:
    """The furthest north and south (deg) a habitat covers >= PRESENT % of a cell."""
    v = np.asarray(L[layer], float) >= PRESENT
    lat = grid.lat[v]
    return (float(lat.max()) if v.any() else float("nan"), float(lat.min()) if v.any() else float("nan"))


def report(grid, L) -> str:
    a = C.areas_km2(grid, L)
    lines = ["habitat       model km2    observed km2        model lat limits (N / S)   observed"]
    for k in C.LAYERS:
        lo, hi = OBSERVED_KM2[k]
        n, s = lat_limits(grid, L, k)
        lines.append(f"{k:12s} {a[k]:>10,}   {lo:>9,.0f}-{hi:<9,.0f}   {n:6.1f} / {s:6.1f}            {OBS_LAT[k]}")
    res = sites(grid, L)
    ok = sum(r[4] for r in res)
    lines.append(f"\nplaces: {ok} of {len(res)} as observed (present = >= {PRESENT:g}% of a cell within {NEAR_KM:g} km)")
    for k in C.LAYERS:
        sub = [r for r in res if r[1] == k]
        lines.append(f"  {k}: {sum(r[4] for r in sub)}/{len(sub)}  " + "; ".join(
            f"{'' if r[4] else 'MISS '}{r[0]} {'yes' if r[2] else 'no'} ({r[3]:.0f}%)" for r in sub))
    if "vegetation" in L:
        from planet import vegetation as V
        t = np.asarray(L["vegetation"])
        cell = 4 * np.pi * R_KM ** 2 / grid.n
        lines.append(f"\nvegetation types: mangrove forest {int((t == V.T['mangrove forest']).sum())} cells "
                     f"({(t == V.T['mangrove forest']).sum() * cell:,.0f} km2), salt marsh "
                     f"{int((t == V.T['salt marsh']).sum())} cells")
    ssc = np.asarray(L["turbidity"], float)
    sea = np.asarray(L["elevation"]) <= 0
    lines.append(f"turbidity (sea cells): median {np.median(ssc[sea]):.1f} mg/L, 99th pct "
                 f"{np.percentile(ssc[sea], 99):.1f}, max {ssc.max():.0f}")
    return "\n".join(lines)


def maps_png(grid, L, path: Path, width: int = 900) -> None:
    """An equirectangular map: land grey, sea dark blue, each habitat in its colour by its share."""
    from planet.images import write_png
    from planet.world import nearest_cell_map
    h = width // 2
    idx = nearest_cell_map(grid, width, h)
    elev = np.asarray(L["elevation"])[idx]
    img = np.where((elev > 0)[..., None], np.array([150, 145, 135]), np.array([20, 35, 70])).astype(float)
    cols = {"kelp": (150, 120, 30), "seagrass": (60, 200, 80), "salt_marsh": (230, 220, 60),
            "reef": (255, 90, 160), "mangrove": (0, 255, 200)}
    for k, c in cols.items():
        f = np.clip(np.asarray(L[k], float)[idx] / 20.0, 0, 1)[..., None] ** 0.5
        f = f * (np.asarray(L[k], float)[idx] >= 0.5)[..., None]
        img = img * (1 - f) + np.array(c) * f
    write_png(path, img.astype(np.uint8))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--level", "-l", type=int, default=6)
    ap.add_argument("--world", help="a saved Earth world instead of building one")
    ap.add_argument("--png", help="write a map of the habitats")
    a = ap.parse_args()
    if a.world:
        from planet import store as S
        from planet import world as W
        w = W.load(S.path_of("world", a.world))
    else:
        from tools.earth_world import build
        w = build(a.level)
    print(report(w["grid"], w["layers"]))
    if a.png:
        maps_png(w["grid"], w["layers"], Path(a.png))


if __name__ == "__main__":
    main()
