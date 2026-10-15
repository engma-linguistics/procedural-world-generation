"""Finished worlds: a world made at one moment of a glacial time zoom (PW-091).

    uv run python -m planet finish <timezoom-id> [--kyr N]   # that frame of the time zoom (default: its end)
    uv run python -m planet finish <run-id> --at T           # straight from a run's keyframe (no time zoom)

A finished world is an ordinary world (world.py's format, so the world
view, regional zooms and highlights work unchanged). Its geology (plates,
crust, rock, sediment, landform classes, volcanoes) is the source run's
keyframe that the time zoom started from; its bed, ice, sea level and global
temperature are the time zoom's at the chosen kyr, and climate, rivers,
lakes, biomes, sea and coasts are computed on them by the usual finishing
(world.finish). So an ice-age moment gets its ice sheets, the bed pressed
down under them, the lowered sea with its land bridges, proglacial lakes
where the ice dams the drainage, and the colder climate.

What the time zoom stores is enough (no re-run): each frame (every 2 kyr)
has the surface relative to its sea level and the grounded ice to 1 m
(timezoom.LAYERS), and its stats the sea level, the global temperature and
the orbit. Bed = surface - ice. A chosen kyr snaps to the nearest frame.

Approximations (see docs/overview.md 2.11):
- grounded ice on a bed below sea level (marine ice sheets, deep isostatic
  depressions) is stored as land with its bed floored at 1 m and the ice
  thinned to keep the surface (as tools/earth_data.py does for Antarctica);
- the climate gets the frame's seasonal insolation anomaly against the
  planet's mean orbit (obliquity, precession, eccentricity; timezoom.orbit_anomaly)
  and the time zoom's start-anchor cooling (Earth's) as climate.compute's
  orbit_dt (PW-198), so the finished world's seasons are the time zoom's.

Provenance in the world's meta: source_run, source_run_name, t_myr (the
run and moment the time zoom started from), timezoom (its id),
timezoom_kyr (the frame), plus that frame's sea-level change and orbit.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import store as S
from . import timeline as T
from . import world as W
from .grid import build_grid
from .tectonics.isostasy import land_view


def load_timezoom(ref: str) -> tuple[Path, dict]:
    """(directory, run.json) of a time zoom; SystemExit if it isn't one."""
    d = S.find_run(ref)
    run = json.loads((d / "run.json").read_text())
    if run.get("kind") != "timezoom":
        raise SystemExit(f"{d.name} is not a glacial time zoom; finish a run time with --at instead")
    return d, run


def frame_index(run: dict, kyr: float | None) -> int:
    """The stored frame nearest kyr (None: the last)."""
    times = np.array([f["t"] for f in run["frames"]])
    if kyr is None:
        return len(times) - 1
    if not times.min() - 1e-9 <= kyr <= times.max() + 1e-9:
        raise SystemExit(f"kyr must be between {times.min():g} and {times.max():g}")
    return int(np.argmin(np.abs(times - kyr)))


def frame_state(tz_dir: Path, i: int) -> dict:
    """The state a finished world needs from frame i of a time zoom: bed and
    ice (m, relative to that frame's sea level), dT (global temperature
    offset from 14.5 C), absolute sea level, tilt (the obliquity then)."""
    run, arr = T.load_frames(tz_dir, ("elevation", "ice"))
    surf = T.frame(run, arr, "elevation", i).astype(float)
    ice = T.frame(run, arr, "ice", i).astype(float)
    bed = surf - ice  # (the true bed: below sea level under a marine sheet or a deep isostatic dip;
    # the world's finishing floors it, isostasy.land_view)
    s = run["frames"][i]["stats"]
    return {"elevation": bed, "ice": ice, "dT": s["global_temp_c"] - 14.5, "sea_level": s["sea_level_m"],
            "tilt": s["obliquity"], "floored_cells": int(land_view(bed, ice)[2].sum()), "stats": s,
            "t": run["frames"][i]["t"]}


def find_finished(tz_id: str, t_kyr: float) -> Path | None:
    """An already finished world of this time zoom at this frame, if any."""
    for p in S.worlds_dir().glob("*.json"):
        if p.name == "index.json":
            continue
        try:
            m = S.read_header(p, ("meta",)).get("meta", {})
        except (OSError, ValueError):
            continue
        if m.get("timezoom") == tz_id and m.get("timezoom_kyr") is not None and abs(m["timezoom_kyr"] - t_kyr) < 1e-6:
            return p
    return None


def finish_timezoom(ref: str, kyr: float | None = None, erosion: float = 0.3,
                    progress=lambda f, msg: None) -> Path:
    """worlds/<id>.json at the time zoom's frame nearest kyr (default: its
    end). Reuses one already finished there."""
    tz_dir, run = load_timezoom(ref)
    tz_id = run.get("id", tz_dir.name)
    m = run["meta"]
    i = frame_index(run, kyr)
    t = float(run["frames"][i]["t"])
    found = find_finished(tz_id, t)
    if found:
        progress(1.0, f"using world {found.stem} (already finished at {t:g} kyr)")
        return found
    progress(0.1, f"finishing the world at {t:g} kyr (climate, rivers, lakes, biomes)")
    st = frame_state(tz_dir, i)
    s = st["stats"]
    prov = {"timezoom": tz_id, "timezoom_name": run["name"], "timezoom_kyr": t, "finished": True,
            "sea_level_change_m": s["sea_level_change_m"], "ice_volume_mkm3": s["ice_volume_mkm3"],
            "orbit": {k: s[k] for k in ("obliquity", "eccentricity", "perihelion", "insol_65n_jul_anom")},
            "marine_ice_floored_cells": st["floored_cells"]}
    state = {k: st[k] for k in ("elevation", "ice", "dT", "sea_level", "tilt")}
    # (the orbit's obliquity is in its insolation anomaly: the climate keeps the planet's mean tilt, as the
    # time zoom's own)
    state["tilt"] = float(m["params"].get("tilt", 23.44 if m["source_run"] == "earth" else 23.4))
    state["orbit_dt"] = orbit_dt(run, st)
    if m["source_run"] == "earth":
        world = _earth_world(m["level"], state, prov, erosion=0.0)
        name = f"Earth + {t:g} kyr (time zoom {tz_id}, finished)"
    else:
        src_dir = S.find_run(m["source_run"])
        world = T.world_from_frame(src_dir, m["at_myr"], erosion, state=state, **prov)
        if abs(world["meta"]["t_myr"] - m["at_myr"]) > 1e-6:  # the source run lost its keyframe
            raise SystemExit(f"run {src_dir.name} has no keyframe at {m['at_myr']:g} Myr any more")
        name = f"{world['meta']['source_run_name']} @ {m['at_myr']:g} Myr + {t:g} kyr (finished)"
    path = W.save(world, name)
    progress(1.0, f"saved world {path.stem}")
    return path


def orbit_dt(run: dict, st: dict) -> np.ndarray:
    """climate.compute's orbit_dt for a frame (PW-198): the time zoom's
    monthly insolation anomaly at that frame's orbit, plus its start anchor
    (C, all year, where it had one)."""
    from . import timezoom as TZ
    m = run["meta"]
    p = TZ.TZParams(**{k: v for k, v in m.get("timezoom", {}).items() if k in TZ.TZParams.__dataclass_fields__})
    s = st["stats"]
    grid = build_grid(m["level"])
    land = st["elevation"] > 0
    d = TZ.orbit_anomaly(grid, (s["obliquity"], s["eccentricity"], s["perihelion"]), m["params"].get("tilt", 23.4),
                         p, land, st["ice"], earth=m["source_run"] == "earth", phases=m.get("orbit_phases_deg"))
    for i, v in m.get("anchor", []):
        d[i] += v
    return d


def _earth_world(level: int, state: dict, prov: dict, erosion: float = 0.0) -> dict:
    """A finished world of an Earth time zoom: the real terrain has no plates
    or rock record, so only the time zoom's bed and ice go through the
    finishing (as tools/earth_world.py, without the observations)."""
    grid = build_grid(level)
    bed, ice, _ = land_view(state["elevation"], state["ice"])
    state = {**state, "elevation": bed, "ice": ice}
    land = state["elevation"] > 0
    meta = {"method": "earth", "seed": 0, "level": level, "source_run": "earth", "source_run_name": "Earth (ETOPO1)",
            "t_myr": 0.0, **prov, "global_temp_c": round(14.5 + state["dT"], 1),
            "sea_level_m": round(state["sea_level"], 1)}
    return W.finish(grid, state["elevation"], {"ice": np.where(land, state["ice"], 0.0), "crust": land.astype(int)},
                    meta, erosion=erosion, dT=state["dT"], tilt=state["tilt"], params={"earth": True},
                    ice=np.where(land, state["ice"], 0.0), orbit_dt=state.get("orbit_dt"))
