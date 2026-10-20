"""Saving a time zoom as a run (runs/<id>/) and its text report."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from .. import world as W
from ..geo import R_KM
from ..grid import Grid, build_grid
from ..provenance import code_version
from .events import glacial_events
from .params import LAYERS, STATIC, TZParams


def save(res: dict, src: dict, kyr: float, step: float, every: float, name: str | None = None) -> Path:
    g: Grid = src["grid"]
    run_id = S.new_id()
    out = S.path_of("run", run_id)
    nf = len(res["frames"])
    arrays = {**{k: res["data"][k] for k in LAYERS},
              **{k: S.encode(np.asarray(src["static"][k])[None, :], S.LAYERS[k]) for k in STATIC}}
    layers = S.write_layers(out, arrays, {**LAYERS, **{k: S.LAYERS[k] for k in STATIC}})
    S.write_grid(g)
    for fr in res["frames"]:
        fr.update(omega={}, hotspots=src["hotspots"], volcanoes=src["volcanoes"])
    label = name or f"time zoom: {src['source_name']} @ {src['at']:g} Myr"
    S.write_json(out / "run.json", {
        "format": "procgen-run/2",
        "kind": "timezoom",
        "id": run_id,
        "name": label,
        "meta": {"kind": "timezoom", "time_unit": "kyr", "source_run": src["source_run"],
                 "source_name": src["source_name"], "at_myr": src["at"], "kyr": kyr, "step_kyr": step,
                 "every": every, "dt": step, "myr": kyr / 1000.0, "frames": nf,
                 "seed": src["seed"], "level": g.level, "cells": g.n,
                 "cell_size_km": round(g.spacing * R_KM),
                 "params": src["params"], "timezoom": res["params"], "orbit_phases_deg": res["phases"],
                 "ice_cycle": res["ice_cycle"],  # (where the ice comes and goes: cycling_ice_sun)
                 "dT_source": round(src["dT"], 2), "sea_level_source_m": round(src["sea_level"], 1),
                 # (the start's climate correction over the ice, C per cell: start_anchor)
                 "anchor": [[int(i), round(float(res["anchor"][i]), 2)] for i in np.flatnonzero(res["anchor"])],
                 "static_layers": list(STATIC),
                 "code": code_version(), "generated_in_s": res["runtime_s"], "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{g.level}.json",
        "legend": S.legends(),
        "layers": layers,
        "events": glacial_events(res, g),
        "frames": res["frames"],
    })
    report(out)
    T.update_index()
    return out


def report(run_dir: Path) -> Path:
    """runs/<id>/run.txt: settings, the sea-level / ice / orbit table, ASCII
    maps of the ice at the start, the biggest glacial maximum and the end."""
    run, arr = T.load_frames(run_dir, ("elevation", "ice"))
    m = run["meta"]
    grid = build_grid(m["level"])
    defaults = asdict(TZParams())
    changed = {k: v for k, v in m["timezoom"].items() if defaults.get(k) != v}
    fr = run["frames"]
    out = [f"# Time zoom {run['id']}: {run['name']}  (created {m['created']})",
           f"{m['kyr']:g} kyr after {m['source_run']} @ {m['at_myr']:g} Myr, step {m['step_kyr']:g} kyr, "
           f"frame every {m['every']:g} kyr; level {m['level']} ({m['cells']} cells, ~{m['cell_size_km']} km)",
           f"source: dT {m['dT_source']:+.1f} C, tilt {m['params'].get('tilt', 23.4)}, "
           f"sea level {m['sea_level_source_m']} m; non-default knobs: {json.dumps(changed) if changed else 'none'}",
           f"remake: uv run python -m planet timezoom {m['source_run']} --at {m['at_myr']:g} --kyr {m['kyr']:g} "
           f"--step {m['step_kyr']:g}", "", "## Glacial events"]
    out += [f"  t={e['t']:>7.1f} kyr  {e['kind']:<12} {e['text']}  near ({e['lat']}, {e['lon']})"
            for e in run["events"]] or ["  (none)"]
    out += ["", "## Over time (sea level relative to the start)",
            "    t(kyr)  sea(m)  ice_vol(Mkm3)  ice%  global_T  obliq   ecc     e*sin(w)  65N_Jul_anom(W/m2)"]
    pick = np.unique(np.linspace(0, len(fr) - 1, min(len(fr), 51)).round().astype(int))
    for i in pick:
        s = fr[i]["stats"]
        out.append(f"  {s['t']:>8.1f}  {s['sea_level_change_m']:>6.1f}  {s['ice_volume_mkm3']:>13.2f}  "
                   f"{s['ice_pct']:>4.1f}  {s['global_temp_c']:>8.1f}  {s['obliquity']:>5.2f}  "
                   f"{s['eccentricity']:.4f}  {s['precession_index']:>8.4f}  {s['insol_65n_jul_anom']:>8.1f}")
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    for title, i in (("start", 0), ("largest ice volume", int(np.argmin(sl))), ("end", len(fr) - 1)):
        w = {"grid": grid, "layers": {"elevation": np.where(arr["ice"][i] > 0, 5000,
                                                             T.frame(run, arr, "elevation", i).astype(int))}}
        out += ["", f"## t = {fr[i]['t']:g} kyr ({title}): land ice shown as '#', sea level "
                f"{fr[i]['stats']['sea_level_change_m']:+.0f} m", W.LEGENDS["elevation"],
                W.ascii_map(w, "elevation", 100, 25)]
    path = run_dir / "run.txt"
    S.write_atomic(path, "\n".join(out) + "\n")
    return path
