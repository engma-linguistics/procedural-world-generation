"""The time zoom's ice at two resolutions (PW-736): one planet moment (an L7 run's keyframe, source_from_run) and the
same moment averaged onto the L6 grid (L6's cells are L7's first n6 vertices; each L6 cell the mean of the L7 cells
nearest it, categorical layers its own vertex's), each run through the same time zoom (same seed and moment: the
same orbits and glacial-index draw). Read only, nothing saved to the store. Variants:
  L7      the keyframe on its own grid, the current 'edge' margins (earth.margin_band: 2 rings at L7)
  L7old   the same with the band one ring (MARGIN_KM patched to 1 km: the rule before PW-736)
  L6      the averaged moment on the L6 grid (one ring either way)
Usage (repo root, PLANET_DATA set): uv run python docs/review/base-climate/v1-finish-4/tzlevel.py RUN T KYR VARIANT OUT.json"""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401  (first: thread caps before numpy's BLAS)
import json  # noqa: E402

import numpy as np  # noqa: E402

from planet import timeline as T  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import earth  # noqa: E402
from planet.timezoom.params import TZParams  # noqa: E402
from planet.timezoom.sim import simulate  # noqa: E402
from planet.timezoom.sources import source_from_run  # noqa: E402


def to_l6(src):
    g7, g6 = src["grid"], build_grid(6)
    par = g6.locate(g7.centers)
    cnt = np.bincount(par, minlength=g6.n)

    def down(v):
        if isinstance(v, dict):
            return {k: down(x) for k, x in v.items()}
        if isinstance(v, np.ndarray) and v.shape[-1:] == (g7.n,):
            if v.dtype.kind == "f" and v.ndim > 1:
                return np.stack([down(r) for r in v])
            if v.dtype.kind == "f":
                return (np.bincount(par, weights=v, minlength=g6.n) / cnt).astype(v.dtype)
            return v[..., :g6.n].copy()
        return v
    out = {k: down(v) for k, v in src.items() if k != "grid"}
    out.update(grid=g6, level=6)
    return out


def main():
    run, t, kyr, variant, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
    src = source_from_run(T.find_run(run), t)
    if variant == "L7old":
        earth.MARGIN_KM = 1.0
    elif variant == "L6":
        src = to_l6(src)
    res = simulate(src, kyr, 0.5, 2.0, TZParams(), progress=False)
    keys = ("t", "glacial_index", "dT_global", "ice_pct", "sea_level_change_m", "ice_volume_mkm3", "max_ice_m",
            "global_temp_c", "ice_age")
    frames = [{k: f["stats"][k] for k in keys} for f in res["frames"]]
    land = [f["stats"]["land_pct"] for f in res["frames"]]
    json.dump({"run": run, "t": t, "kyr": kyr, "variant": variant, "level": src["level"], "land_pct": land,
               "frames": frames, "cycle": {k: v for k, v in res["cycle"].items() if not isinstance(v, (list, dict))},
               "runtime_s": res["runtime_s"]}, open(out, "w"), indent=1, default=float)
    sl = np.array([f["sea_level_change_m"] for f in frames])
    ice = np.array([f["ice_pct"] for f in frames])
    print(variant, run, t, "runtime", res["runtime_s"], "sea min/mean/end", sl.min(), round(sl.mean(), 1), sl[-1],
          "ice% max/mean/end", ice.max(), round(ice.mean(), 2), ice[-1])


main()
