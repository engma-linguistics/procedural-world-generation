"""Earth (today) as a world for the viewer: our model on the real terrain,
next to what is observed.

    uv run python tools/earth_world.py [--level 6]     # prints the new world's id

The terrain is ETOPO1 (tools/earth_data.py: bare ground plus the Greenland
and Antarctic ice) on the icosphere grid. It goes through the normal
pipeline (world.finish: climate, rivers, lakes, biomes) at dT = 0 and
Earth's tilt, with erosion off so the real valleys and mountains are kept.
So the model layers (temperature, precipitation, climate, biome) are what
the model makes of the real Earth, as in tools/earth_check.py.

Extra layers saved with it (on top of every world's own, which include the
model's wind, current and jet layers since PW-045):
  ice                   m of land ice (ETOPO1 ice surface - bedrock)
  obs_temperature       C, NCEP/NCAR 2 m air temperature 1981-2010, annual mean
  obs_warm_month, obs_cold_month   ... its warmest / coldest month
  obs_precipitation     mm/yr, GPCC (land); where GPCC has no data
                        (Antarctica, some coasts), GPCP; null where neither
  obs_climate           Koppen class (climate.KOPPEN id) from Kottek et al.
                        2006; -1 where it has no data
  obs_sunshine          h/day of bright sunshine over the year, CRU CL 2.0
                        (land, no Antarctica; null elsewhere)

When the climate model changes, just run this again (and delete the old
world in the viewer).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planet import climate  # noqa: E402
from planet import world as W  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools.earth_data import earth_clouds, earth_on_grid  # noqa: E402

NAME = "Earth (today, ETOPO1) — model vs observed"
TILT = 23.44


def _with_nulls(x: np.ndarray, decimals: int = 1) -> np.ndarray:
    """Rounded, with NaN as None (null in the JSON: no observation)."""
    x = np.round(np.asarray(x, float), decimals)
    return np.where(np.isfinite(x), x, None).astype(object)


def build(level: int = 6) -> dict:
    t0 = time.time()
    grid = build_grid(level)
    d = earth_on_grid(grid)
    elev, ice = d["elev"].astype(float), d["ice"].astype(float)
    rain = np.where(np.isfinite(d["obs_precip"]), d["obs_precip"], d["obs_gpcp"])
    o, day = earth_clouds(grid), climate.day_hours(grid.lat, TILT)
    extra = {
        "ice": np.round(ice),
        "obs_temperature": _with_nulls(d["obs_temp"]),
        "obs_warm_month": _with_nulls(d["obs_t_warm"]),
        "obs_cold_month": _with_nulls(d["obs_t_cold"]),
        "obs_precipitation": _with_nulls(rain, 0),
        "obs_climate": d["obs_koppen"].astype(int),
        # CRU CL 2.0 sunshine (share of the possible hours, land) as hours a day over the year
        "obs_sunshine": _with_nulls(0.5 * sum(o[f"obs_sun_{h}"] * dh for h, dh in zip(("jul", "jan"), day))),
    }
    meta = {"method": "earth", "seed": 0, "level": level, "source": "ETOPO1 + observations (tools/earth_data.py)",
            "remake": "uv run python tools/earth_world.py",
            "observed": {"obs_temperature": "NCEP/NCAR reanalysis 2 m air temperature, 1981-2010",
                         "obs_precipitation": "GPCC v2018 (land), GPCP v2.3 where GPCC has none",
                         "obs_climate": "Kottek et al. 2006 Koppen-Geiger, 1951-2000 (As scored as Aw)",
                         "obs_sunshine": "CRU CL 2.0 sunshine duration (New et al. 2002), 1961-90, land"},
            "global_temp_c": 14.5, "sea_level_m": 0.0}
    world = W.finish(grid, elev, extra, meta, erosion=0.0, dT=0.0, tilt=TILT, params={"earth": True},
                     t0=t0, ice=ice)
    world["meta"]["generated_in_s"] = round(time.time() - t0, 1)
    return world


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--level", "-l", type=int, default=6)
    ap.add_argument("--name", "-n", default=NAME)
    args = ap.parse_args()
    world = build(args.level)
    path = W.save(world, args.name)
    print(f"{path.stem}  {args.name}  [{world['meta']['generated_in_s']}s]  "
          f"view: http://127.0.0.1:8765/viewer/?world={path.name}&layer=temperature")


if __name__ == "__main__":
    main()
