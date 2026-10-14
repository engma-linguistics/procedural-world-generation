"""Tectonic runs: simulate, store keyframes, report, replay, slice.

On disk: runs/<name>/
  run.json    small and human-readable: settings, per-frame stats, plate
              velocities, the event log, and the layout of frames.bin
  frames.bin  raw little-endian arrays, one block per layer, shape
              (n_frames, n_cells). For the viewer; never parsed as JSON.
  run.txt     the conversation-friendly report (event log, stats table,
              ASCII maps), rendered from the two files above.

A run is fully determined by (seed, level, dt, params). Keyframes are just a
cache for the viewer: `slice` replays the simulation from t=0 to any step
and builds a complete world there (climate, rivers, biomes).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, fields
from pathlib import Path

import numpy as np

from . import world as W
from .grid import Grid, build_grid
from .noise import Perlin3D, fbm, ridged
from .climate import KOPPEN
from .surface import ROCKS
from .tectonics import CMYR, Params, Simulation

RUNS = W.ROOT / "runs"
GRIDS = W.ROOT / "grids"

LAYERS = {  # name -> dtype on disk
    "elevation": "<i2",
    "plate": "<u2",
    "continental": "u1",
    "age": "<u2",
    "boundary": "i1",
    "rock": "u1",  # surface.ROCKS id of the basement
    "surface": "u1",  # surface.ROCKS id of what's exposed (basement or sediment cover)
    "cover": "<u2",  # sediment cover, units of 0.1 km
    "thickness": "u1",  # crust, km
    "precip": "<u2",  # mm/yr
    "temperature": "i1",  # C, annual mean
    "climate": "u1",  # climate.KOPPEN id
    "ice": "u1",  # land ice, units of 20 m
    "flow": "u1",  # river flow, 16 * log2(1 + flow)
    "wind_e": "i1",  # annual-mean wind, east and north components x 50
    "wind_n": "i1",
    "current_e": "i1",  # surface ocean current, x 50
    "current_n": "i1",
    "jet_e": "i1",  # annual-mean jet stream (upper-level wind), east and north components, m/s
    "jet_n": "i1",  # (optional: runs made before Oct 2026 don't have the jet layers)
    "down": "u1",  # which neighbour (index into grid nbr list) the river goes to; 255 = none
}


def down_slot(grid: Grid, down: np.ndarray) -> np.ndarray:
    """Encode each cell's downstream cell as its position in the cell's
    neighbour list (fits in a byte)."""
    deg = np.diff(grid.nbr_off)
    src = np.repeat(np.arange(grid.n), deg)
    pos = np.arange(len(grid.nbr_idx)) - grid.nbr_off[src]
    hit = grid.nbr_idx == down[src]
    out = np.full(grid.n, 255, np.uint8)
    out[src[hit]] = pos[hit]
    return out


def vec_layers(grid: Grid, name: str, v: np.ndarray, scale: float = 50.0):
    """(east, north) components of tangent vectors, x scale as int8 layers."""
    from .climate import _geom
    G = _geom(grid)
    q = lambda x: np.clip(np.round(scale * x), -127, 127)
    return [(f"{name}_e", q((v * G["east"]).sum(1))), (f"{name}_n", q((v * G["north"]).sum(1)))]


def jet_of(grid: Grid, snap) -> np.ndarray:
    """Annual-mean jet stream (m/s) for a snapshot, from its temperatures
    (the thermal wind is linear in temperature, so the mean of the two
    half-years' jets is the jet of the mean of their temperatures)."""
    from . import climate
    surf = np.maximum(snap.elevation, 0) + snap.ice
    t_jul, t_jan = climate.season_temps(grid, surf, snap.t_warm, snap.t_cold, climate.TUNE["hk"])
    return climate.jet_stream(grid, 0.5 * (t_jul + t_jan))[0]


def make_params(overrides: dict) -> Params:
    known = {f.name for f in fields(Params)}
    bad = set(overrides) - known
    if bad:
        raise SystemExit(f"unknown tectonics params: {sorted(bad)}; known: {sorted(known)}")
    return Params(**overrides)


def write_grid(grid: Grid) -> Path:
    """Geometry for the viewer, shared by every run at this level."""
    GRIDS.mkdir(exist_ok=True)
    path = GRIDS / f"L{grid.level}.json"
    if path.exists() and '"nbr"' in path.read_text()[-200000:]:
        return path
    ll = lambda v: (np.round(np.degrees(np.arcsin(np.clip(v[:, 2], -1, 1))), 3).tolist(),
                    np.round(np.degrees(np.arctan2(v[:, 1], v[:, 0])), 3).tolist())
    lat, lon = ll(grid.centers)
    clat, clon = ll(grid.corners)
    path.write_text(json.dumps({"level": grid.level, "lat": lat, "lon": lon, "corner_lat": clat,
                                "corner_lon": clon, "cells": grid.cell_corners,
                                "pentagons": grid.pentagons.tolist(), "nbr": grid.neighbors},
                               separators=(",", ":")))
    return path


def simulate(seed: int, level: int, myr: float, dt: float, every: float, name: str,
             params: Params) -> Path:
    t0 = time.time()
    grid = build_grid(level)
    sim = Simulation(grid, seed, params, dt)
    stride = max(1, round(every / dt))
    frames, data = [], {k: [] for k in LAYERS}
    jet = {"src": None, "v": None}  # the climate (and so the jet) changes only every climate_every Myr

    def keep(s: Simulation):
        if s.step_no % stride:
            return
        snap = s.snapshot()
        if jet["v"] is None or jet["src"] is not s.t_warm:
            jet["src"], jet["v"] = s.t_warm, jet_of(s.grid, snap)
        # cast now: at level 7, 126 float64 keyframes per layer would be ~1 GB
        for k, v in (("elevation", np.clip(np.round(snap.elevation), -32000, 32000)),
                     ("plate", snap.plate), ("continental", snap.continental),
                     ("age", np.clip(np.round(snap.age), 0, 65535)), ("boundary", snap.boundary),
                     ("rock", snap.rock), ("surface", snap.surface), ("cover", np.clip(np.round(snap.cover * 10), 0, 65535)),
                     ("thickness", np.clip(np.round(snap.thickness), 0, 255)),
                     ("precip", np.clip(np.round(snap.precip), 0, 65535)),
                     ("temperature", np.clip(np.round(snap.temperature), -128, 127)),
                     ("climate", snap.koppen), ("ice", np.clip(np.round(snap.ice / 20), 0, 255)),
                     ("flow", np.clip(np.round(16 * np.log2(1 + snap.flow)), 0, 255)),
                     ("down", down_slot(s.grid, snap.downstream)),
                     *vec_layers(s.grid, "wind", snap.wind), *vec_layers(s.grid, "current", snap.current),
                     *vec_layers(s.grid, "jet", jet["v"], 1.0)):
            data[k].append(v.astype(LAYERS[k]))
        frames.append({"t": s.t, "stats": s.stats(),
                       "omega": {k: [round(x, 6) for x in v] for k, v in snap.omega.items()},
                       "hotspots": [[round(a, 1), round(b, 1)] for a, b in snap.hotspots],
                       "volcanoes": [[round(a, 1), round(b, 1)] for a, b in snap.volcanoes]})

    keep(sim)
    sim.run(myr, keep)

    run_id = W.new_id()
    out = RUNS / run_id
    out.mkdir(parents=True, exist_ok=True)
    layout, offset = {}, 0
    with open(out / "frames.bin", "wb") as f:
        for k, dtype in LAYERS.items():
            arr = np.ascontiguousarray(np.stack(data[k]).astype(dtype))
            pad = (-offset) % 8
            f.write(b"\0" * pad)
            offset += pad
            layout[k] = {"dtype": np.dtype(dtype).name, "offset": offset, "shape": list(arr.shape)}
            f.write(arr.tobytes())
            offset += arr.nbytes
    write_grid(grid)
    run = {
        "format": "procgen-run/1",
        "id": run_id,
        "name": name,
        "meta": {"seed": seed, "level": level, "cells": grid.n, "dt": dt, "myr": myr,
                 "every": stride * dt, "steps": sim.step_no,
                 "cell_size_km": round(grid.spacing * W.PLANET_RADIUS_KM),
                 "params": asdict(params), "generated_in_s": round(time.time() - t0, 1),
                 "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{level}.json",
        "rocks": [{"id": r[0], "key": r[1], "name": r[2], "color": r[4]} for r in ROCKS],
            "koppen": [{"id": k[0], "code": k[1], "name": k[2], "color": k[3]} for k in KOPPEN],
        "events": [e.as_dict() for e in sim.events],
        "frames": frames,
        "layers": layout,
    }
    (out / "run.json").write_text(json.dumps(run, default=W._np, separators=(",", ":")))
    report(out)
    update_index()
    return out


def load_frames(run_dir: Path) -> tuple[dict, dict]:
    run = json.loads((run_dir / "run.json").read_text())
    raw = (run_dir / "frames.bin").read_bytes()
    arrays = {}
    for k, spec in run["layers"].items():
        dt = np.dtype(spec["dtype"]).newbyteorder("<")
        count = int(np.prod(spec["shape"]))
        arrays[k] = np.frombuffer(raw, dt, count, spec["offset"]).reshape(spec["shape"])
    return run, arrays


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def report(run_dir: Path) -> Path:
    run, arr = load_frames(run_dir)
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
        w = {"grid": grid, "layers": {"elevation": arr["elevation"][i].astype(int),
                                       "plate": arr["plate"][i].astype(int)}}
        out += ["", f"## t = {frames[i]['t']:.0f} Myr: elevation", W.LEGENDS["elevation"],
                W.ascii_map(w, "elevation", 100, 25)]
    last = len(frames) - 1
    w = {"grid": grid, "layers": {"elevation": arr["elevation"][last].astype(int),
                                   "plate": arr["plate"][last].astype(int)}}
    out += ["", f"## t = {frames[last]['t']:.0f} Myr: plates", W.LEGENDS["plate"],
            W.ascii_map(w, "plate", 100, 25)]
    # per-plate table at the end
    om = frames[last]["omega"]
    out += ["", f"## Plates at t = {frames[last]['t']:.0f} Myr",
            "  plate  area%  continental%  mean_speed(cm/yr)  heading"]
    plate = arr["plate"][last].astype(int)
    cont = arr["continental"][last].astype(bool)
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
def replay(run_dir: Path, at: float) -> Simulation:
    run = json.loads((run_dir / "run.json").read_text())
    m = run["meta"]
    grid = build_grid(m["level"])
    sim = Simulation(grid, m["seed"], Params(**m["params"]), m["dt"])
    sim.run(at)
    return sim


def slice_world(run_dir: Path, at: float, erosion: float = 0.3) -> Path:
    """erosion: strength of the final river-carving pass. Erosion already ran
    for the whole history inside the simulation; this only sharpens valleys."""
    run, arr = load_frames(run_dir)
    m = run["meta"]
    at = round(at / m["dt"]) * m["dt"]
    if not 0 <= at <= m["myr"] + 1e-9:
        raise SystemExit(f"--at must be between 0 and {m['myr']}")
    sim = replay(run_dir, at)
    snap = sim.snapshot()
    # determinism check against the stored keyframe, when there is one
    times = [f["t"] for f in run["frames"]]
    if at in times:
        i = times.index(at)
        same = (np.array_equal(arr["plate"][i], snap.plate.astype("<u2")) and
                np.array_equal(arr["elevation"][i], np.clip(np.round(snap.elevation), -32000, 32000).astype("<i2")))
        print(f"replay at t={at:g} {'matches' if same else 'DOES NOT match'} the stored keyframe")

    world = world_from_sim(sim, erosion, source_run=run_dir.name, source_run_name=run["name"])
    return W.save(world, f"{run['name']} @ {at:g} Myr")


def world_from_sim(sim: Simulation, erosion: float = 0.3, **meta_extra) -> dict:
    """A complete world (climate, rivers, biomes, all layers) from a
    simulation's current state, in memory."""
    snap = sim.snapshot()
    at = sim.t
    g = sim.grid
    m = {"seed": sim.seed, "level": g.level, "params": asdict(sim.params)}
    rng_seed = m["seed"] * 100003 + int(at)
    # sub-cell texture: roughness the plate model can't produce at this resolution
    tex = fbm(Perlin3D(rng_seed), g.centers, octaves=6, freq=6.0)
    rough = ridged(Perlin3D(rng_seed + 1), g.centers, octaves=5, freq=5.0)
    e = snap.elevation.astype(float)
    mountains = np.clip((e - 800) / 2500, 0, 1)
    elev = e + 180 * tex * (e > 0) + mountains * 900 * (rough - 0.45)
    elev = np.where((e > 0) & (elev <= 0), 5.0, elev)  # texture shouldn't drown coasts

    v = sim.velocity()
    extra = {"plate": snap.plate, "crust": snap.continental.astype(int),
             "plate_boundary": snap.boundary.astype(int), "crust_age": np.round(snap.age),
             "plate_speed": np.linalg.norm(v, axis=1) * CMYR, "_plate_velocity": v,
             "rock": snap.rock.astype(int), "surface_rock": snap.surface.astype(int), "sediment_cover": snap.cover,
             "crust_thickness": snap.thickness, "ice": snap.ice}
    meta = {"method": "tectonics", "seed": m["seed"], "level": m["level"], **meta_extra, "t_myr": at,
            "rocks": [{"id": r[0], "key": r[1], "name": r[2], "color": r[4]} for r in ROCKS],
            "koppen": [{"id": k[0], "code": k[1], "name": k[2], "color": k[3]} for k in KOPPEN],
            "hotspots": snap.hotspots, "volcanoes": snap.volcanoes}
    meta["global_temp_c"] = round(14.5 + sim.dT, 1)
    meta["sea_level_m"] = round(sim.sea_level, 1)
    return W.finish(g, elev, extra, meta, erosion=erosion, params={"tectonics": m["params"]},
                    dT=sim.dT, tilt=sim.params.tilt, ice=snap.ice)


def find_run(ref: str) -> Path:
    """A run by id ('a3f9c2') or path ('runs/a3f9c2')."""
    p = Path(ref)
    for cand in (p, RUNS / ref, RUNS / p.name):
        if (cand / "run.json").exists():
            return cand
    raise SystemExit(f"no run {ref!r} (see: uv run python -m planet list)")


def delete(ref: str) -> list[Path]:
    """Delete a run (by id) or a world (by id); returns what was removed."""
    import shutil
    gone = []
    if (RUNS / ref / "run.json").exists():
        shutil.rmtree(RUNS / ref)
        gone.append(RUNS / ref)
    for ext in (".json", ".txt"):
        if (W.WORLDS / f"{ref}{ext}").exists() and ref != "index":
            (W.WORLDS / f"{ref}{ext}").unlink()
            gone.append(W.WORLDS / f"{ref}{ext}")
    update_index()
    W.update_index()
    return gone


def update_index():
    RUNS.mkdir(exist_ok=True)
    items = []
    for p in sorted(RUNS.glob("*/run.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        r = json.loads(p.read_text())
        items.append({"dir": p.parent.name, "id": r.get("id", p.parent.name), "name": r["name"],
                      "seed": r["meta"]["seed"], "level": r["meta"]["level"], "myr": r["meta"]["myr"],
                      "created": r["meta"]["created"]})
    (RUNS / "index.json").write_text(json.dumps(items, indent=1))
