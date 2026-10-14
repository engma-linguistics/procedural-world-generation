"""Tectonic runs: simulate, store keyframes, report, replay, slice.

On disk (paths and formats: store.py): runs/<id>/
  run.json         small and human-readable: settings, per-frame stats, plate
                   velocities, the event log, and the layer specs (file,
                   dtype, shape, encoding, units)
  layers/<name>.bin  one file per layer, (n_frames, n_cells) raw little-endian,
                   so the viewer loads only the layers it draws
  state/<t>.ckpt   the full simulation state every `checkpoint_every` Myr
  volcanoes.json.gz  every volcano (arc and hotspot) at each keyframe
  run.txt          the conversation-friendly report (event log, stats table,
                   ASCII maps), rendered from the files above.

A run is fully determined by (seed, level, dt, params) and the code version.
`slice` replays the simulation (from the nearest checkpoint at or before the
time asked for) and builds a complete world there (climate, rivers, biomes);
`world_from_frame` builds one straight from a stored keyframe instead
(seconds, no replay; the viewer's zoom uses it).
"""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import asdict, fields
from pathlib import Path

import numpy as np

from . import store as S
from . import world as W
from .provenance import code_version, describe
from .geo import R_KM
from .grid import Grid, build_grid
from .noise import Perlin3D, fbm, ridged
from .tectonics import CMYR, Params, Simulation
from .landform import LAYERS as LANDFORM_LAYERS
from .surface import surface_rock
from .tectonics.volcanism import COLUMNS as VOLCANO_COLUMNS

# the layers of a run's keyframes, in store.LAYERS' vocabulary and encodings
RUN_LAYERS = ("elevation", "plate", "crust", "crust_age", "plate_boundary", "rock", "surface_rock",
              "sediment_cover", "crust_thickness", "precipitation", "temperature", "climate", "ice", "flow",
              "downstream", "lake_depth", "lake_kind", "wind_e", "wind_n", "current_e", "current_n", "jet_e", "jet_n",
              *LANDFORM_LAYERS)
CHECKPOINT_EVERY = 100.0  # Myr


def vec_layers(grid: Grid, name: str, v: np.ndarray):
    """(east, north) components of tangent vectors (n, 3), as
    [(name_e, east), (name_n, north)] in the vectors' own units."""
    from .climate import _geom
    G = _geom(grid)
    return [(f"{name}_e", (v * G["east"]).sum(1)), (f"{name}_n", (v * G["north"]).sum(1))]


def jet_of(grid: Grid, snap) -> np.ndarray:
    """Annual-mean jet stream (m/s) for a snapshot, from its temperatures
    (the thermal wind is linear in temperature, so the mean of the two
    half-years' jets is the jet of the mean of their temperatures)."""
    from . import climate
    surf = np.maximum(snap.elevation, 0) + snap.ice
    t_jul, t_jan = climate.season_temps(grid, surf, snap.t_warm, snap.t_cold, climate.TUNE["hk"])
    return climate.jet_stream(grid, 0.5 * (t_jul + t_jan))[0]


def frame_values(grid: Grid, snap, jet: np.ndarray) -> dict:
    """A snapshot's keyframe layers in real units (store.encode stores them)."""
    return {"elevation": snap.elevation, "plate": snap.plate, "crust": snap.continental,
            "crust_age": snap.age, "plate_boundary": snap.boundary, "rock": snap.rock,
            "surface_rock": snap.surface, "sediment_cover": snap.cover, "crust_thickness": snap.thickness,
            "precipitation": snap.precip, "temperature": snap.temperature, "climate": snap.koppen,
            "ice": snap.ice, "flow": snap.flow, "downstream": snap.downstream,
            "lake_depth": snap.lake_depth, "lake_kind": snap.lake_kind,
            **dict(vec_layers(grid, "wind", snap.wind)), **dict(vec_layers(grid, "current", snap.current)),
            **dict(vec_layers(grid, "jet", jet)), **landforms_of(snap)}


def landforms_of(snap) -> dict:
    """A snapshot's landform layers (landform.LAYERS), in real units."""
    return {k: getattr(snap, k) for k in LANDFORM_LAYERS}


def active_volcanoes(table: list) -> list:
    """[lat, lon, kind] of the active volcanoes in a volcano table (rows of
    tectonics.volcanism.COLUMNS): what a run's keyframes list for the viewer
    (the full table is in volcanoes.json.gz, store.write_volcanoes)."""
    return [[round(r[0], 1), round(r[1], 1), r[2]] for r in table if r[4]]


def make_params(overrides: dict) -> Params:
    known = {f.name for f in fields(Params)}
    bad = set(overrides) - known
    if bad:
        raise SystemExit(f"unknown tectonics params: {sorted(bad)}; known: {sorted(known)}")
    return Params(**overrides)


def simulate(seed: int, level: int, myr: float, dt: float, every: float, name: str,
             params: Params, checkpoint_every: float = CHECKPOINT_EVERY) -> Path:
    """checkpoint_every: Myr between saved simulation states (0: none)."""
    t0 = time.time()
    grid = build_grid(level)
    sim = Simulation(grid, seed, params, dt)
    stride = max(1, round(every / dt))
    ck_stride = round(checkpoint_every / dt) if checkpoint_every > 0 else 0
    frames, vframes, data = [], [], {k: [] for k in RUN_LAYERS}
    jet = {"src": None, "v": None}  # the climate (and so the jet) changes only every climate_every Myr
    run_id = S.new_id()
    out = S.runs_dir() / run_id

    def keep(s: Simulation):
        if ck_stride and s.step_no and s.step_no % ck_stride == 0:
            S.save_checkpoint(out, s)
        if s.step_no % stride:
            return
        snap = s.snapshot()
        if jet["v"] is None or jet["src"] is not s.t_warm:
            jet["src"], jet["v"] = s.t_warm, jet_of(s.grid, snap)
        # encode now: at level 7, 126 float64 keyframes per layer would be ~1 GB
        for k, v in frame_values(s.grid, snap, jet["v"]).items():
            data[k].append(S.encode(v, S.LAYERS[k], s.grid))
        frames.append({"t": s.t, "stats": s.stats(),
                       "omega": {k: [round(x, 6) for x in v] for k, v in snap.omega.items()},
                       "hotspots": [[round(a, 1), round(b, 1)] for a, b in snap.hotspots],
                       "volcanoes": active_volcanoes(snap.volcanoes)})
        vframes.append(snap.volcanoes)

    out.mkdir(parents=True, exist_ok=True)
    try:
        keep(sim)
        sim.run(myr, keep)
        layers = S.write_layers(out, {k: np.stack(data[k]) for k in RUN_LAYERS})
        S.write_volcanoes(out, VOLCANO_COLUMNS, vframes)
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    S.write_grid(grid)
    S.write_json(out / "run.json", {
        "format": "procgen-run/2",
        "id": run_id,
        "name": name,
        "meta": {"seed": seed, "level": level, "cells": grid.n, "dt": dt, "myr": myr,
                 "every": stride * dt, "steps": sim.step_no, "checkpoint_every": ck_stride * dt,
                 "cell_size_km": round(grid.spacing * R_KM),
                 "params": asdict(params), "code": code_version(),
                 "generated_in_s": round(time.time() - t0, 1),
                 "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{level}.json",
        "legend": S.legends(),
        "layers": layers,
        "events": [e.as_dict() for e in sim.events],
        "frames": frames,
    })
    report(out)
    update_index()
    return out


def load_frames(run_dir: Path, names=None) -> tuple[dict, dict]:
    """(run.json, {layer: raw (frames, cells) array, memory-mapped}); decode
    a frame with frame()."""
    run = json.loads((Path(run_dir) / "run.json").read_text())
    return run, S.read_layers(run_dir, run["layers"], names)


def frame(run: dict, arr: dict, name: str, i: int, grid: Grid | None = None) -> np.ndarray:
    """Layer `name` at frame i in real units (a layer stored once serves every frame)."""
    a = arr[name]
    return S.decode(np.asarray(a[i if a.shape[0] > 1 else 0]), run["layers"][name], grid)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def report(run_dir: Path) -> Path:
    run, arr = load_frames(run_dir, ())
    if run.get("kind") == "timezoom":
        from . import timezoom
        return timezoom.report(run_dir)
    arr = S.read_layers(run_dir, run["layers"], ("elevation", "plate", "crust"))
    m = run["meta"]
    grid = build_grid(m["level"])
    defaults = asdict(Params())
    changed = {k: v for k, v in m["params"].items() if defaults.get(k) != v}
    out = [f"# Tectonic run {run.get('id', run_dir.name)}: {run['name']}  (created {m['created']})",
           f"seed={m['seed']} level={m['level']} cells={m['cells']} (~{m['cell_size_km']} km) "
           f"dt={m['dt']} Myr, {m['myr']} Myr total, keyframe every {m['every']} Myr",
           f"non-default params: {json.dumps(changed) if changed else 'none'}",
           f"replay any time with: uv run python -m planet slice {run_dir.name} --at <Myr>", "",
           "## Events"]
    out += [f"  t={e['t']:>5.0f}  {e['kind']:<9} {e['text']}  near ({e['lat']}, {e['lon']})"
            for e in run["events"]] or ["  (none)"]
    out += ["", "## Stats over time",
            "      t  plates  land%  cont%  landmasses  largest%  max_elev  mean_v  max_v (cm/yr)"]
    frames = run["frames"]
    pick = np.unique(np.linspace(0, len(frames) - 1, min(len(frames), 40)).round().astype(int))
    for i in pick:
        s = frames[i]["stats"]
        out.append(f"  {s['t']:>5.0f}  {s['plates']:>6}  {s['land_pct']:>5}  {s['continental_pct']:>5}  "
                   f"{s['landmasses']:>10}  {s['largest_landmass_pct']:>8}  {s['max_elev_m']:>8}  "
                   f"{s['mean_speed_cmyr']:>6}  {s['max_speed_cmyr']:>5}")
    for i in np.unique(np.linspace(0, len(frames) - 1, 5).round().astype(int)):
        w = {"grid": grid, "layers": {"elevation": frame(run, arr, "elevation", i).astype(int),
                                       "plate": frame(run, arr, "plate", i).astype(int)}}
        out += ["", f"## t = {frames[i]['t']:.0f} Myr: elevation", W.LEGENDS["elevation"],
                W.ascii_map(w, "elevation", 100, 25)]
    last = len(frames) - 1
    plate = frame(run, arr, "plate", last).astype(int)
    w = {"grid": grid, "layers": {"elevation": frame(run, arr, "elevation", last).astype(int), "plate": plate}}
    out += ["", f"## t = {frames[last]['t']:.0f} Myr: plates", W.LEGENDS["plate"],
            W.ascii_map(w, "plate", 100, 25)]
    # per-plate table at the end
    om = frames[last]["omega"]
    out += ["", f"## Plates at t = {frames[last]['t']:.0f} Myr",
            "  plate  area%  continental%  mean_speed(cm/yr)  heading"]
    cont = frame(run, arr, "crust", last).astype(bool)
    for k, w_ in sorted(om.items(), key=lambda kv: -(plate == int(kv[0])).sum()):
        sel = plate == int(k)
        if not sel.any():
            continue
        v = np.cross(np.array(w_), grid.centers[sel])
        speed = np.linalg.norm(v, axis=1).mean() * CMYR
        mv = v.mean(0)
        c = grid.centers[sel].mean(0)
        c /= np.linalg.norm(c)
        east = np.cross([0, 0, 1.0], c)
        east /= max(np.linalg.norm(east), 1e-9)
        north = np.cross(c, east)
        ang = np.degrees(np.arctan2(mv @ east, mv @ north)) % 360
        compass = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][int((ang + 22.5) // 45) % 8]
        out.append(f"  {int(k):>5}  {100 * sel.mean():>5.1f}  {100 * cont[sel].mean():>12.0f}  "
                   f"{speed:>17.1f}  {compass}")
    path = run_dir / "run.txt"
    path.write_text("\n".join(out) + "\n")
    return path


# ---------------------------------------------------------------------------
# Replay + slice
# ---------------------------------------------------------------------------
def replay(run_dir: Path, at: float, use_checkpoints: bool = True, log=print) -> Simulation:
    """The run's simulation at time `at`: from the latest checkpoint at or
    before it when the run was made by this same code (else from t=0)."""
    run = S.read_header(Path(run_dir) / "run.json")
    m = run["meta"]
    grid = build_grid(m["level"])
    params = Params.from_stored(m["params"])
    made_by = m.get("code") or {}
    usable = [t for t in S.checkpoints(run_dir) if t <= at + 1e-9]
    if use_checkpoints and usable and made_by.get("planet_src_sha") == code_version()["planet_src_sha"]:
        sim = Simulation.from_state(grid, m["seed"], params, m["dt"], S.load_checkpoint(run_dir, usable[-1]))
        log(f"replaying from the checkpoint at t={usable[-1]:g}")
    else:
        sim = Simulation(grid, m["seed"], params, m["dt"])
    sim.run(at)
    return sim


class ReplayMismatch(RuntimeError):
    """Replaying a run didn't reproduce its stored keyframe (the code
    changed since the run was made), so a sliced world wouldn't show what
    the viewer showed for that run."""


def slice_world(run_dir: Path, at: float, erosion: float = 0.3, force: bool = False) -> Path:
    """erosion: strength of the final river-carving pass. Erosion already ran
    for the whole history inside the simulation; this only sharpens valleys.
    Raises ReplayMismatch if the replay doesn't match the stored keyframe at
    `at`, unless force (then the world is saved, marked as not matching)."""
    run, arr = load_frames(run_dir, ("elevation", "plate"))
    _not_timezoom(run, run_dir)
    m = run["meta"]
    at = round(at / m["dt"]) * m["dt"]
    if not 0 <= at <= m["myr"] + 1e-9:
        raise SystemExit(f"--at must be between 0 and {m['myr']}")
    made_by, now = m.get("code"), code_version()
    same_code = bool(made_by) and made_by.get("planet_src_sha") == now["planet_src_sha"]
    if not same_code:
        print(f"WARNING: run {run_dir.name} was made by {describe(made_by)}; this is {describe(now)}. "
              f"The replay may not reproduce it.")
    sim = replay(run_dir, at)
    snap = sim.snapshot()
    # determinism check against the stored keyframe, when there is one
    times = [f["t"] for f in run["frames"]]
    same = None
    if at in times:
        i = times.index(at)
        same = all(np.array_equal(arr[k][i], S.encode(v, run["layers"][k]))
                   for k, v in (("plate", snap.plate), ("elevation", snap.elevation)))
        if same:
            print(f"replay at t={at:g} matches the stored keyframe")
        else:
            msg = (f"replay at t={at:g} DOES NOT match the stored keyframe of run {run_dir.name}: "
                   f"the code changed since it was made, so this world is not what the viewer shows")
            if not force:
                raise ReplayMismatch(msg + ". Not saved (use --force / force=True to save it anyway).")
            print("!" * 72 + f"\nWARNING: {msg}. Saving anyway (--force).\n" + "!" * 72)

    world = world_from_sim(sim, erosion, source_run=run_dir.name, source_run_name=run["name"],
                           replay_matches_keyframe=same, code=now)
    return W.save(world, f"{run['name']} @ {at:g} Myr")


def world_from_sim(sim: Simulation, erosion: float = 0.3, **meta_extra) -> dict:
    """A complete world (climate, rivers, biomes, all layers) from a
    simulation's current state, in memory."""
    snap = sim.snapshot()
    return _world(sim.grid, sim.seed, sim.params, sim.t, snap.elevation.astype(float), snap.plate,
                  snap.continental, snap.boundary, snap.age, sim.velocity(), snap.rock, snap.surface,
                  snap.cover, snap.thickness, snap.ice, snap.hotspots, snap.volcanoes,
                  sim.dT, sim.sea_level, erosion, meta_extra, landforms_of(snap))


FRAME_LAYERS = ("elevation", "plate", "crust", "crust_age", "plate_boundary", "rock",
                "sediment_cover", "crust_thickness", "ice", *LANDFORM_LAYERS)


def world_from_frame(run_dir: Path, at: float, erosion: float = 0.3, **meta_extra) -> dict:
    """A complete world from a stored keyframe, without replaying: exactly
    the state the viewer shows, at keyframe precision (elevation to 1 m, ice
    to 20 m, thickness to 1 km). `at` snaps to the nearest keyframe."""
    run, arr = load_frames(run_dir, ())
    _not_timezoom(run, run_dir)
    m = run["meta"]
    missing = [k for k in FRAME_LAYERS if k not in run["layers"]]
    if missing or "sea_level_m" not in run["frames"][0]["stats"]:
        raise ValueError(f"run {run_dir.name} is too old to build worlds from its keyframes "
                         f"(missing {', '.join(missing) or 'sea level'}); use `planet slice`")
    arr = S.read_layers(run_dir, run["layers"], FRAME_LAYERS)
    times = np.array([f["t"] for f in run["frames"]])
    i = int(np.argmin(np.abs(times - at)))
    fr = run["frames"][i]
    vt = S.read_volcanoes(run_dir)
    vols = vt["frames"][i] if vt and vt["columns"] == list(VOLCANO_COLUMNS) else []
    a = {k: frame(run, arr, k, i) for k in FRAME_LAYERS}
    grid = build_grid(m["level"])
    params = Params.from_stored(m["params"])
    omega = np.zeros((int(a["plate"].max()) + 1, 3))
    for label, w in fr["omega"].items():
        omega[int(label)] = w
    velocity = np.cross(omega[a["plate"]], grid.centers)
    # the exposed rock from the stored strata, by the current rule (as snapshot() does)
    exposed = surface_rock(a["rock"], a["sediment_cover"], a["strata_top"], a["strata_top_km"])
    s = fr["stats"]
    return _world(grid, m["seed"], params, float(fr["t"]), a["elevation"].astype(float), a["plate"].astype(int),
                  a["crust"].astype(bool), a["plate_boundary"].astype(int), a["crust_age"].astype(float), velocity,
                  a["rock"], exposed, a["sediment_cover"], a["crust_thickness"].astype(float),
                  a["ice"], fr["hotspots"], vols, s["global_temp_c"] - 14.5,
                  s["sea_level_m"], erosion, {"source_run": run_dir.name, "source_run_name": run["name"],
                                              "from_keyframe": True, **meta_extra},
                  {k: a[k] for k in LANDFORM_LAYERS})


def _world(g: Grid, seed: int, params: Params, at: float, e, plate, continental, boundary, age,
           v, rock, surface_rock, cover, thickness, ice, hotspots, volcanoes, dT, sea_level,
           erosion, meta_extra, landforms: dict) -> dict:
    m = {"seed": seed, "level": g.level, "params": asdict(params)}
    rng_seed = seed * 100003 + int(at)
    # sub-cell texture: roughness the plate model can't produce at this resolution
    tex = fbm(Perlin3D(rng_seed), g.centers, octaves=6, freq=6.0)
    rough = ridged(Perlin3D(rng_seed + 1), g.centers, octaves=5, freq=5.0)
    mountains = np.clip((e - 800) / 2500, 0, 1)
    elev = e + 180 * tex * (e > 0) + mountains * 900 * (rough - 0.45)
    elev = np.where((e > 0) & (elev <= 0), 5.0, elev)  # texture shouldn't drown coasts

    extra = {"plate": plate, "crust": continental.astype(int),
             "plate_boundary": boundary.astype(int), "crust_age": np.round(age),
             "plate_speed": np.linalg.norm(v, axis=1) * CMYR, "_plate_velocity": v,
             "rock": rock.astype(int), "surface_rock": surface_rock.astype(int), "sediment_cover": cover,
             "crust_thickness": thickness, "ice": ice,
             **{k: np.asarray(v).astype(int if S.LAYERS[k]["dtype"] in ("u1", "<u2") and S.LAYERS[k]["scale"] == 1
                                        else float) for k, v in landforms.items()}}
    meta = {"method": "tectonics", "seed": seed, "level": g.level, **meta_extra, "t_myr": at,
            "hotspots": hotspots, "volcanoes": volcanoes, "volcano_columns": list(VOLCANO_COLUMNS)}
    meta["global_temp_c"] = round(14.5 + dT, 1)
    meta["sea_level_m"] = round(sea_level, 1)
    return W.finish(g, elev, extra, meta, erosion=erosion, params={"tectonics": m["params"]},
                    dT=dT, tilt=params.tilt, ice=ice)


def _not_timezoom(run: dict, run_dir: Path):
    if run.get("kind") == "timezoom":
        m = run["meta"]
        raise SystemExit(f"{run_dir.name} is a glacial time zoom (of {m['source_run']} @ {m['at_myr']:g} Myr); "
                         f"slice its source run instead")


def find_run(ref: str) -> Path:
    """A run by id ('a3f9c2') or path ('runs/a3f9c2')."""
    return S.find_run(ref)


def update_index():
    S.update_index("run")
