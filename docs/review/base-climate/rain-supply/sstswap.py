"""Lane 132 diagnostic: run a tool with the rain's sea temperatures swapped for NCEP's 2 m air over the open sea
(half-year means, hk convention) + DT C (DT "nan": seas kept; env SWAP_LAND=1: the land air swapped too). sstswap.py DT[:LAT0:LAT1] tools/x.py args...  Not a model change:
asks how much rain the coasts gain if the seas the vapour comes from had observed temperatures."""
import os
import runpy
import sys
sys.path.insert(0, ".")
import numpy as np
import planet  # noqa: F401
from planet import climate
from tools import earth_data

spec = [float(x) for x in sys.argv[1].split(":")]
DT, LAT0, LAT1 = (spec + [-90.0, 90.0])[:3] if len(spec) == 1 else spec
cache = {}
orig = climate._season_inputs


def swapped(grid, elev, t_air, sst, v, shift, *a, **k):
    if grid.n not in cache:
        d = earth_data.earth_on_grid(grid)
        hk = climate.TUNE["hk"]
        om, ow, oc = d["obs_temp"], d["obs_t_warm"], d["obs_t_cold"]
        nh = grid.lat > 0
        cache[grid.n] = (np.where(nh, om + hk * (ow - om), om - hk * (om - oc)),
                         np.where(nh, om - hk * (om - oc), om + hk * (ow - om)))
    obs = cache[grid.n][0 if shift > 0 else 1]
    sel = np.isfinite(DT) & (sst > climate.FREEZE + 0.5) & (grid.lat >= LAT0) & (grid.lat <= LAT1) & np.isfinite(obs)
    sst = np.where(sel, np.maximum(obs + DT, climate.FREEZE), sst)
    if os.environ.get("SWAP_LAND"):  # the land's air too (NCEP's, at the cell's height: earth_data's)
        land = elev > 0
        t_air = np.where(land & np.isfinite(obs) & (grid.lat >= LAT0) & (grid.lat <= LAT1), obs, t_air)
    return orig(grid, elev, t_air, sst, v, shift, *a, **k)


climate._season_inputs = swapped
script = sys.argv[2]
sys.argv = [script] + sys.argv[3:]
runpy.run_path(script, run_name="__main__")
