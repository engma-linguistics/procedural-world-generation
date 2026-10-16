"""Earth soil-check data on the model grid (PW-314; docs/proposals/soils.md section 7).

    PYTHONPATH=. uv run python tools/soil_check.py [--level 6]

Loads the three observed inputs the soils check needs (tools/earth_data.py,
which downloads each once into data/earth/) and prints a summary:
  - SoilGrids 2.0 WRB most probable group, area share of each group over the
    cells that have data (ISRIC, CC BY 4.0);
  - GLiM parent rock mapped to planet.surface.ROCKS ids, area share of each
    rock (Hartmann & Moosdorf 2012, CC BY 3.0);
  - the observed Last Glacial Maximum (21 ka) ice cover, area in total and by
    region, against published numbers (Shao et al., Zenodo, CC BY 4.0).
The soil model itself is not built yet; this is the data plumbing.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy, planet/parallel.py)
import numpy as np  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.surface import ROCKS  # noqa: E402
from tools.earth_data import SOILGRIDS_NODATA, cell_areas, earth_glim, earth_lgm_ice, earth_soilgrids  # noqa: E402

# Published LGM ice-sheet areas, Mkm2 (approximate, from reconstructions such as ICE-6G_C, GLAC-1D
# and Ehlers & Gibbard 2007; they differ by 10-20% between reconstructions)
LGM_REF = {"total": (40, 50), "Laurentide + Cordilleran": (13, 17), "Fennoscandia + Barents-Kara": (4, 8),
           "Greenland + Innuitian (merged then)": (2, 6), "Antarctica": (14, 19)}


def lgm_regions(lat, lon):
    """Boolean masks of the regions LGM_REF names (boxes; the ice sheets don't overlap in them)."""
    return {
        "total": np.ones(len(lat), bool),
        "Laurentide + Cordilleran": (lat > 35) & (lon > -170) & (lon < -55) & ~((lat > 58) & (lon > -75)),
        "Fennoscandia + Barents-Kara": (lat > 50) & (lon > -10) & (lon < 110),
        "Greenland + Innuitian (merged then)": (lat > 58) & (lon > -75) & (lon < -10),
        "Antarctica": lat < -60,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--level", type=int, default=6)
    a = ap.parse_args()
    t0 = time.time()
    grid = build_grid(a.level)
    area = cell_areas(grid) * R_KM**2 / 1e6  # Mkm2
    lat = np.degrees(np.arcsin(grid.centers[:, 2]))
    lon = np.degrees(np.arctan2(grid.centers[:, 1], grid.centers[:, 0]))

    sg = earth_soilgrids(grid)
    t1 = time.time()
    has = sg["wrb"] != SOILGRIDS_NODATA
    print(f"level {a.level}: {grid.n} cells, {area.sum():.0f} Mkm2")
    warea = area * sg["cover"]  # area with data, so a half-sea coastal cell counts half
    print(f"\nSoilGrids WRB: {has.sum()} cells with data, {warea[has].sum():.1f} Mkm2 with data "
          f"(Earth's land outside ice sheets ~ 120 Mkm2); {t1 - t0:.1f}s")
    share = np.bincount(sg["wrb"][has], warea[has], 30) / warea[has].sum()
    for i in np.argsort(-share)[:12]:
        print(f"  {sg['legend'][i]:<13s} {share[i]:6.1%}")
    print(f"  ... {int((share > 0).sum())} of 30 groups present")

    rock = earth_glim(grid)
    t2 = time.time()
    has_r = rock >= 0
    print(f"\nGLiM parent rock: {has_r.sum()} cells with a rock, {area[has_r].sum():.1f} Mkm2; {t2 - t1:.1f}s")
    rs = np.bincount(rock[has_r], area[has_r], len(ROCKS)) / area[has_r].sum()
    for i in np.argsort(-rs):
        if rs[i] > 0:
            print(f"  {ROCKS[i][1]:<13s} {rs[i]:6.1%}")

    ice = earth_lgm_ice(grid)
    t3 = time.time()
    print(f"\nLGM (21 ka) ice cover, Mkm2 (observed here | published, approx.); {t3 - t2:.1f}s")
    for name, m in lgm_regions(lat, lon).items():
        lo, hi = LGM_REF[name]
        v = (ice * area)[m].sum()
        print(f"  {name:<28s} {v:6.1f} | {lo}-{hi} {'' if lo * 0.9 <= v <= hi * 1.1 else '  <-- outside'}")
    nh = (ice * area)[lat > 0].sum()
    print(f"  Northern Hemisphere total    {nh:6.1f}; cells >= 50% ice: {(ice >= 0.5).sum()}")
    print(f"\ntotal {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
