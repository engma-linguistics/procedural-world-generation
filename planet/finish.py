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
where the ice dams the drainage, and the colder climate. The glacial
imprint up to that frame comes along (PW-037, glacial_imprint): the bed is
the carved one, and the world gets glacial_erosion, glacial_till and
ice_max (timeline.world_from_frame: cover, texture, glaciated_myr).

What the time zoom stores is enough (no re-run): each frame (every 2 kyr)
has the surface relative to its sea level and the grounded ice to 1 m
(timezoom.LAYERS), and its stats the sea level, the global temperature and
the orbit. Bed = surface - ice. A chosen kyr snaps to the nearest frame.

The bed is stored as it is: grounded ice on a bed below sea level (marine
ice sheets, deep isostatic depressions) is land by its ice (geo.is_land;
PW-307, PW-197).

Approximation (see docs/overview.md 2.11):
- the climate gets the frame's seasonal insolation anomaly against the
  planet's mean orbit (obliquity, precession, eccentricity; timezoom.orbit_anomaly)
  and the time zoom's start-anchor cooling (Earth's, where ice lies) as climate.compute's
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
from .geo import is_land
from . import surface as SF
from . import vegetation
from .tectonics.isostasy import grounded


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


NOWS = ("interglacial", "glacial", "end")
LOW_I = 0.05   # (an interglacial: the glacial index this low)


def now_kyr(run: dict, now) -> tuple[float, str]:
    """(kyr, why): the time zoom's frame for a "now" (PW-479). `now` is "end" (the last frame), a number
    (kyr, snapped to a frame), "interglacial" or "glacial".

    interglacial: like Earth today. The last stretch of frames with the glacial index I (stored in each
    frame's stats) at or below LOW_I that comes after one full cycle (I has gone past 0.5 and back); in it
    the frame with the most melted ice (highest sea_level_change_m). Without a completed cycle (a short
    zoom) it falls back to the end.
    glacial: the last stretch with I within 0.2 of the zoom's highest; in it the lowest sea level. A zoom
    that never got glacial (I max < 0.1) takes its lowest sea level overall."""
    fr = run["frames"]
    t = np.array([f["t"] for f in fr], float)
    if isinstance(now, (int, float)) or str(now).replace(".", "", 1).lstrip("-").isdigit():
        k = float(now)
        return float(t[frame_index(run, k)]), f"{k:g} kyr"
    if now == "end":
        return float(t[-1]), "the end of the time zoom"
    if now not in NOWS:
        raise SystemExit(f"now must be one of {list(NOWS)} or a kyr, not {now!r}")
    if any("glacial_index" not in f["stats"] for f in fr):
        raise SystemExit("this time zoom has no glacial index per frame (made before PW-471); remake it or give a kyr")
    I = np.array([f["stats"]["glacial_index"] for f in fr], float)
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr], float)

    def runs(mask):  # [(first, last)] of the consecutive True frames
        idx = np.flatnonzero(mask)
        return [(g[0], g[-1]) for g in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1) if len(g)]
    if now == "glacial":
        if I.max() < 0.1:
            i = int(np.argmin(sl))
            return float(t[i]), "no glaciation in this time zoom: its lowest sea level"
        a, b = runs(I >= I.max() - 0.2)[-1]
        i = a + int(np.argmin(sl[a:b + 1]))
        return float(t[i]), f"the glacial maximum (index {I[i]:.2f}, sea level {sl[i]:+.0f} m)"
    up = np.flatnonzero(I > 0.5)
    if len(up):  # (after the first frame past 0.5 and back under it: one full cycle)
        back = np.flatnonzero((I <= 0.5) & (np.arange(len(I)) > up[0]))
        after = [(a, b) for a, b in runs(I <= LOW_I) if len(back) and b >= back[0]]
        if after:
            a, b = after[-1]
            i = a + int(np.argmax(sl[a:b + 1]))
            return float(t[i]), f"the latest interglacial (index {I[i]:.2f}, sea level {sl[i]:+.0f} m)"
    return float(t[-1]), "no full glacial cycle in this time zoom yet: its end"


def frame_state(tz_dir: Path, i: int) -> dict:
    """The state a finished world needs from frame i of a time zoom: bed and
    ice (m, relative to that frame's sea level), dT (global temperature
    offset from 14.5 C), absolute sea level, tilt (the obliquity then)."""
    run, arr = T.load_frames(tz_dir, ("elevation", "ice"))
    surf = T.frame(run, arr, "elevation", i).astype(float)
    ice = T.frame(run, arr, "ice", i).astype(float)
    bed = surf - ice  # (the true bed: below sea level under a marine sheet or a deep isostatic dip)
    s = run["frames"][i]["stats"]
    # the plants of that frame (PW-213): its tree cover, the trees held where they stand (world.finish: held)
    veg = None
    if "tree_cover" in run["layers"]:
        tree = T.frame(run, S.read_layers(tz_dir, run["layers"], ("tree_cover",)), "tree_cover", i)
        veg = {"nu0": vegetation.start_from_tree_cover(np.asarray(tree, float) / 100.0), "held": True,
               **({"co2": s["co2"]} if "co2" in s else {})}
    return {"veg": veg, "elevation": bed, "ice": ice, "dT": s["global_temp_c"] - 14.5, "sea_level": s["sea_level_m"],
            "tilt": s["obliquity"], "below_sea_cells": int(((ice > 0) & (bed <= 0)).sum()), "stats": s,
            "t": run["frames"][i]["t"], "glacial": glacial_imprint(tz_dir, i)}


def glacial_imprint(tz_dir: Path, i: int) -> dict:
    """The time zoom's glacial imprint up to frame i (PW-037): m of bed eroded
    and of till dropped (the frame's bed already has both), the thickest
    the land ice has been (m) and where it has been (frames every ~2 kyr)."""
    run, arr = T.load_frames(tz_dir, ())
    if "glacial_erosion" not in run["layers"]:
        raise SystemExit(f"time zoom {tz_dir.name} was made before glacial carving (PW-037); run it again "
                         f"(its remake line is in its run.txt)")
    run, arr = T.load_frames(tz_dir, ("ice", "glacial_erosion", "glacial_till", "glacial_outwash", "glacial_loess"))
    ice_max = np.asarray(arr["ice"][: i + 1]).max(0).astype(float)  # (1 m steps, as stored)
    return {"glacial_erosion": T.frame(run, arr, "glacial_erosion", i).astype(float),
            "glacial_till": T.frame(run, arr, "glacial_till", i).astype(float),
            "glacial_outwash": T.frame(run, arr, "glacial_outwash", i).astype(float),
            "glacial_loess": T.frame(run, arr, "glacial_loess", i).astype(float),
            "ice_max": ice_max, "glaciated": ice_max > 0}


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
    i = frame_index(run, kyr)
    t = float(run["frames"][i]["t"])
    with S.lock(S.worlds_dir(), f"finish-{tz_id}-{t:g}"):  # (one process finishes it; the others find it)
        found = find_finished(tz_id, t)
        if found:
            progress(1.0, f"using world {found.stem} (already finished at {t:g} kyr)")
            return found
        return _finish(tz_dir, run, tz_id, i, t, erosion, progress)


def _finish(tz_dir, run: dict, tz_id: str, i: int, t: float, erosion: float, progress) -> Path:
    m = run["meta"]
    progress(0.1, f"finishing the world at {t:g} kyr (climate, rivers, lakes, biomes)")
    st = frame_state(tz_dir, i)
    s = st["stats"]
    prov = {"timezoom": tz_id, "timezoom_name": run["name"], "timezoom_kyr": t, "finished": True,
            "sea_level_change_m": s["sea_level_change_m"], "ice_volume_mkm3": s["ice_volume_mkm3"],
            "orbit": {k: s[k] for k in ("obliquity", "eccentricity", "perihelion", "insol_65n_jul_anom")},
            "ice_bed_below_sea_cells": st["below_sea_cells"]}
    state = {k: st[k] for k in ("elevation", "ice", "dT", "sea_level", "tilt", "glacial", "veg")}
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
    (C, all year, where it had one and the frame has ice, as the time zoom
    applies it)."""
    from . import timezoom as TZ
    m = run["meta"]
    p = TZ.TZParams(**{k: v for k, v in m.get("timezoom", {}).items() if k in TZ.TZParams.__dataclass_fields__})
    s = st["stats"]
    grid = build_grid(m["level"])
    land = st["elevation"] + st["ice"] > 0  # (the time zoom's land: grounded ice on a sunk bed included)
    d = TZ.orbit_anomaly(grid, (s["obliquity"], s["eccentricity"], s["perihelion"]), m["params"].get("tilt", 23.4),
                         p, land, st["ice"], earth=m["source_run"] == "earth", phases=m.get("orbit_phases_deg"))
    bright = np.clip(st["ice"] / p.snow_h, 0, 1)  # (the anchor corrects the ice's climate: where ice lies, PW-035)
    for i, v in m.get("anchor", []):
        d[i] += v * bright[i]
    return d


def earth_rock(grid, elev: np.ndarray, ice: np.ndarray) -> dict:
    """A plausible rock map of Earth from its terrain (no geological map is
    used): rugged high ground is a metamorphic belt, low plains and the shelves
    sedimentary basins, the rest old shield; what the zoom needs to draw it.
    (tools/earth_world.py's Earth world has the same; PW-494: GLiM instead.)"""
    rel = vegetation.relief(grid, elev)  # m to the steepest neighbour
    land = is_land(elev, ice)
    shelf = ~land & (elev > -1000)
    rugged = land & ((rel > 900) | (elev > 2500))
    plain = (land & ~rugged & (elev < 400) & (rel < 250)) | shelf
    rock = np.select([~land & ~shelf, rugged, plain], [SF.OCEAN, SF.OROGEN, SF.SEDIMENT], SF.CRATON)
    cover = np.select([~land & ~shelf, rugged, plain], [0.3, 0.1, 2.0], 0.02)  # km
    surf = np.where(cover >= SF.COVER_SHOWS, SF.SHALE, rock)
    return {"rock": rock.astype(int), "surface_rock": surf.astype(int), "sediment_cover": np.round(cover, 2),
            "crust": (land | shelf).astype(int)}


def _earth_world(level: int, state: dict, prov: dict, erosion: float = 0.0) -> dict:
    """A finished world of an Earth time zoom: the real terrain has no plates
    or rock record, so only the time zoom's bed and ice go through the
    finishing (as tools/earth_world.py, without the observations)."""
    grid = build_grid(level)
    ice = grounded(state["elevation"], state["ice"])  # (the true bed: land by its ice where that is below the sea)
    land = is_land(state["elevation"], ice)
    meta = {"method": "earth", "seed": 0, "level": level, "source_run": "earth", "source_run_name": "Earth (ETOPO1)",
            "t_myr": 0.0, **prov, "global_temp_c": round(14.5 + state["dT"], 1),
            "sea_level_m": round(state["sea_level"], 1)}
    gl = state.get("glacial") or {}
    return W.finish(grid, state["elevation"], {"ice": ice, **earth_rock(grid, state["elevation"], ice),
                                               "crust": land.astype(int),
                                               **{k: gl[k] for k in T.GLACIAL_LAYERS if k in gl}},
                    meta, erosion=erosion, dT=state["dT"], tilt=state["tilt"], params={"earth": True},
                    ice=ice, orbit_dt=state.get("orbit_dt"), veg=state.get("veg"))
