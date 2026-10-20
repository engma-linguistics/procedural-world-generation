"""Sources: a run at some moment, or the real Earth."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np

from .. import timeline as T
from .. import vegetation as VEG
from ..geo import is_land
from ..grid import build_grid
from ..tectonics.params import Params
from .params import STATIC


def source_from_run(run_dir: Path, at: float) -> dict:
    """Elevation (m above the run's sea level, without ice), ice (m), the
    global temperature offset dT, tilt and the frozen geology at `at` Myr,
    from the stored keyframe nearest to `at` (as timeline.world_from_frame:
    no replay; ice to 20 m, dT to 0.1 C)."""
    run, arr = T.load_frames(run_dir, ("elevation", "ice", "tree_cover", *STATIC))
    if run.get("kind") == "timezoom":
        raise SystemExit("that's a time zoom already; give its source run")
    m = run["meta"]
    times = np.array([f["t"] for f in run["frames"]])
    if not times.min() - 1e-9 <= at <= times.max() + 1e-9:
        raise SystemExit(f"--at must be between {times.min():g} and {times.max():g}")
    i = int(np.argmin(np.abs(times - at)))
    fr = run["frames"][i]
    if "sea_level_m" not in fr["stats"] or "tree_cover" not in run["layers"]:
        raise SystemExit(f"run {run_dir.name} is too old (its keyframes have no climate or vegetation)")
    veg = T.keyframe_vegetation(m, fr, T.frame(run, arr, "tree_cover", i), Params.from_stored(m["params"]).plants_from)
    return {"source_run": run.get("id", run_dir.name), "source_name": run["name"], "seed": m["seed"],
            "level": m["level"], "tilt": m["params"].get("tilt", 23.4), "params": m["params"],
            "grid": build_grid(m["level"]), "at": float(fr["t"]),
            "elev": T.frame(run, arr, "elevation", i).astype(float),
            "ice": T.frame(run, arr, "ice", i).astype(float), "dT": fr["stats"]["global_temp_c"] - 14.5,
            "sea_level": fr["stats"]["sea_level_m"], "static": {k: T.frame(run, arr, k, i) for k in STATIC},
            "hotspots": fr["hotspots"], "volcanoes": fr["volcanoes"], "veg": veg}


def source_from_sim(sim, name: str = "in-memory simulation") -> dict:
    """The same, from a tectonics.Simulation in memory (exact, no keyframe)."""
    snap = sim.snapshot()
    return {"source_run": "sim", "source_name": name, "seed": sim.seed, "level": sim.grid.level,
            "tilt": sim.params.tilt, "params": asdict(sim.params), "grid": sim.grid, "at": float(sim.t),
            "elev": snap.elevation.astype(float), "ice": snap.ice.astype(float), "dT": float(sim.dT),
            "sea_level": float(sim.sea_level),
            "static": {"plate": snap.plate, "crust": snap.continental, "crust_age": snap.age,
                       "plate_boundary": snap.boundary},
            "hotspots": [[round(a, 1), round(b, 1)] for a, b in snap.hotspots],
            "volcanoes": T.active_volcanoes(snap.volcanoes),
            "veg": None if sim.veg_frac is None else {"nu0": sim.veg_frac, "co2": float(sim.co2),
                                                      "unlocked": VEG.unlocked_at(sim.flora, sim.t)}}


def source_earth(level: int = 6) -> dict:
    """Today's Earth (tools/earth_data.py: ETOPO1 elevation and ice) at dT=0."""
    from tools.earth_data import earth_on_grid
    grid = build_grid(level)
    d = earth_on_grid(grid)
    elev, ice = d["elev"].astype(float), d["ice"].astype(float)
    # (earth_data: the true bed, below the sea under much of West Antarctica
    # and central Greenland, land by its grounded ice; the floating shelves
    # are sea, PW-354)
    land = is_land(elev, ice)
    return {"source_run": "earth", "source_name": "Earth (ETOPO1)", "seed": 0, "level": level, "tilt": 23.44,
            "params": {"tilt": 23.44}, "grid": grid, "at": 0.0, "elev": elev, "ice": np.where(land, ice, 0.0),
            "dT": 0.0, "sea_level": 0.0,
            "static": {"plate": np.zeros(grid.n), "crust": land, "crust_age": np.zeros(grid.n),
                       "plate_boundary": np.zeros(grid.n)},
            "hotspots": [], "volcanoes": [],
            "obs": {k: d[f"obs_{k}"].astype(float) for k in ("t_warm", "t_cold", "p_jul", "p_jan")}}
