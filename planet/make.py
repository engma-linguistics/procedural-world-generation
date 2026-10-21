"""`planet make`: seed to finished world in one command (PW-248), and the same
chain as a server job (POST /api/make) behind the viewer's "New planet" form
(PW-472).

The chain, each stage optional after the first:

  simulate       a tectonic run (T.simulate) of `myr` Myr at `level`
  timezoom       ~`kyr` kyr of ice ages from the run's representative moment
                 (highlights.representative_time), api.timezoom_job
  world          the finished world: the time zoom's frame for `now` (the latest
                 interglacial by default, finish.now_kyr; finish.finish_timezoom), or, without a time zoom, the run's
                 keyframe at the representative moment (api.slice_run)
  highlights     the world's interesting places (api.highlights)
  zooms          regional zooms of the top N highlights (api.zoom_job)

Settings: what the code honours today is listed in SETTINGS (tectonics.Params
fields that change the planet's character, plus seed, level and length) and
PRESETS (the showcase recipes of docs/coordination.md). `options()` is what
GET /api/make/options serves to the form. Orbit, sun strength, day length,
ocean fraction and water inventory are not parameters yet (draft-make-settings-gaps).

Time estimates (`estimate`) come from the run-cost table in docs/coordination.md.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path

from . import api
from . import store as S
from . import highlights as H
from .finish import NOWS

LEVELS = (4, 5, 6, 7, 8)
# seconds per Gyr of tectonic run, per grid level (docs/coordination.md run costs: L6 ~5-6 min,
# L7 ~20-40 min; L5 and L4 scaled by cell count; L8 3-4 h). Under load these are a lower bound.
RUN_S_PER_GYR = {4: 25, 5: 80, 6: 330, 7: 1800, 8: 12600}
# seconds per kyr of glacial time zoom (speed pass: 100 kyr = 10 s at L6, 31 s at L7)
TZ_S_PER_KYR = {4: 0.01, 5: 0.03, 6: 0.1, 7: 0.31, 8: 1.2}
FINISH_S = {4: 2, 5: 3, 6: 6, 7: 20, 8: 80}   # finishing / slicing one world
HIGHLIGHTS_S = {4: 3, 5: 5, 6: 10, 7: 40, 8: 150}
ZOOM_S = {4: 4, 5: 4, 6: 5, 7: 7, 8: 12}      # one 1000 km regional zoom
DT, EVERY = 2.0, 4.0                          # the simulate defaults

# The showcase recipes (docs/coordination.md), as presets. `set` are tectonics.Params overrides.
PRESETS = {
    "earthlike": {"label": "Earth-like", "myr": 1000, "set": {},
                  "blurb": "Default parameters: a few continents drifting around, Earth's tilt and climate."},
    "water-world": {"label": "Water world", "myr": 2000, "set": {"continental_start": 0.1, "heat_start": 2},
                    "blurb": "Starts almost all ocean with a hot young mantle; land emerges over the first Gyr."},
    "land-heavy": {"label": "Land heavy", "myr": 1000, "set": {"continental_fraction": 0.6},
                   "blurb": "60% continental crust: big continents and little ocean."},
    "cold": {"label": "Cold world", "myr": 1000, "set": {"tilt": 15, "climate_offset": -6},
             "blurb": "Low tilt and a colder climate: big ice sheets."},
    "hothouse": {"label": "Hothouse", "myr": 1000, "set": {"tilt": 45, "climate_offset": 5},
                 "blurb": "High tilt and a warmer climate: strong seasons, little ice."},
}
DEFAULT_PRESET = "earthlike"

# The planet settings the form offers, all tectonics.Params fields the run honours (type, range, default
# from the dataclass). Anything else goes through `--set KEY=VALUE` on the command line.
SETTINGS = [
    {"key": "n_plates", "label": "Plates at the start", "type": "int", "min": 4, "max": 30,
     "help": "How many plates the surface starts split into (rifting and welding change it later)."},
    {"key": "start", "label": "Starting layout", "type": "choice", "choices": ["supercontinent", "scattered"],
     "help": "All land in one supercontinent, or continents scattered over the globe."},
    {"key": "continental_fraction", "label": "Continental crust", "type": "float", "min": 0.1, "max": 0.7,
     "help": "Share of the surface that is continental crust (Earth ~0.41). The thermostat on island arcs holds it near this."},
    {"key": "tilt", "label": "Axial tilt (deg)", "type": "float", "min": 0, "max": 60,
     "help": "Sets how strong the seasons are (Earth 23.4)."},
    {"key": "climate_offset", "label": "Climate offset (C)", "type": "float", "min": -10, "max": 10,
     "help": "Shifts the whole climate history warmer or colder."},
    {"key": "heat_start", "label": "Early mantle heat", "type": "float", "min": 1, "max": 3,
     "help": "Mantle heat at the start relative to today (1 = steady). Hot starts give more plumes and faster plates, early on."},
    {"key": "continental_start", "label": "Starting land share", "type": "float", "min": -1, "max": 0.7,
     "help": "Start with this share of continental crust and grow toward the continental fraction (-1: start at it)."},
]
UNSUPPORTED = ["orbit (distance, eccentricity)", "star brightness", "day length", "ocean fraction / water inventory",
               "atmosphere (pressure, CO2 level)", "planet size / gravity"]

NOW_CHOICES = [{"key": "interglacial", "label": "Interglacial (like Earth today)"},
               {"key": "glacial", "label": "Glacial maximum"}, {"key": "end", "label": "End of the time zoom"}]
DEFAULTS = {"level": 6, "myr": 1000, "kyr": 300, "now": "interglacial", "timezoom": True, "finish": True, "highlights": True, "zooms": 4}


def parse_make_request(req: dict) -> dict:
    """Validates a make request and fills defaults. Raises api.BadRequest.
    {seed, preset, level, myr, set, timezoom, kyr, now, finish, highlights, zooms, name}"""
    from dataclasses import fields
    from .tectonics import Params
    if not isinstance(req, dict):
        raise api.BadRequest("expected a JSON object")
    preset = str(req.get("preset") or DEFAULT_PRESET)
    if preset not in PRESETS:
        raise api.BadRequest(f"preset must be one of {sorted(PRESETS)}")
    out = {"type": "make", "preset": preset}
    seed = req.get("seed")
    out["seed"] = int(api._num(req, "seed")) if seed not in (None, "") else secrets.randbelow(10**6)
    out["level"] = int(api._num(req, "level", DEFAULTS["level"]))
    if out["level"] not in LEVELS:
        raise api.BadRequest(f"level must be one of {list(LEVELS)}")
    out["myr"] = api._num(req, "myr", PRESETS[preset]["myr"])
    if not 20 <= out["myr"] <= 4000:
        raise api.BadRequest("myr must be within 20..4000")
    out["kyr"] = api._num(req, "kyr", DEFAULTS["kyr"])
    if not 1 <= out["kyr"] <= 2000:
        raise api.BadRequest("kyr must be within 1..2000")
    now = req.get("now")
    now = DEFAULTS["now"] if now in (None, "") else now
    if now not in NOWS:
        try:
            now = float(now)
        except (TypeError, ValueError):
            raise api.BadRequest(f"now must be one of {list(NOWS)} or a kyr") from None
        if not 0 <= now <= out["kyr"]:
            raise api.BadRequest(f"now must be within 0..{out['kyr']:g} kyr (the time zoom)")
    out["now"] = now
    for k in ("timezoom", "finish", "highlights"):
        out[k] = bool(req.get(k, DEFAULTS[k]))
    out["zooms"] = int(api._num(req, "zooms", DEFAULTS["zooms"]))
    if not 0 <= out["zooms"] <= 12:
        raise api.BadRequest("zooms must be within 0..12")
    if not out["finish"]:
        out["highlights"], out["zooms"] = False, 0
    if out["zooms"] and not out["highlights"]:
        out["highlights"] = True  # (zooms come from the highlights)
    known = {f.name: f for f in fields(Params)}
    over = req.get("set") or {}
    if not isinstance(over, dict):
        raise api.BadRequest("set must be an object of tectonics parameters")
    bad = sorted(set(over) - set(known))
    if bad:
        raise api.BadRequest(f"unknown tectonics params: {bad}")
    sets = {**PRESETS[preset]["set"], **over}
    spec = {s["key"]: s for s in SETTINGS}
    for k, v in sets.items():
        s = spec.get(k)
        if s and s["type"] in ("int", "float"):
            try:
                v = int(v) if s["type"] == "int" else float(v)
            except (TypeError, ValueError):
                raise api.BadRequest(f"{k} must be a number") from None
            if not s["min"] <= v <= s["max"]:
                raise api.BadRequest(f"{k} must be within {s['min']}..{s['max']}")
        elif s and s["type"] == "choice" and v not in s["choices"]:
            raise api.BadRequest(f"{k} must be one of {s['choices']}")
        sets[k] = v
    out["set"] = sets
    out["name"] = str(req.get("name") or "").strip() or f"{PRESETS[preset]['label']} seed {out['seed']}, L{out['level']}"
    return out


def estimate(spec: dict) -> dict:
    """{"stages": [{"key", "label", "s"}], "total_s"}: expected seconds per stage on a typical
    machine (the run-cost table), for the form and for weighting the progress bar."""
    L = spec["level"]
    st = [("simulate", f"Simulating {spec['myr']:g} Myr of tectonics", spec["myr"] / 1000 * RUN_S_PER_GYR[L])]
    if spec["timezoom"]:
        st.append(("timezoom", f"Ice ages: {spec['kyr']:g} kyr time zoom", spec["kyr"] * TZ_S_PER_KYR[L]))
    if spec["finish"]:
        st.append(("world", "Finishing the world", FINISH_S[L]))
    if spec["highlights"]:
        st.append(("highlights", "Finding highlights", HIGHLIGHTS_S[L]))
    if spec["zooms"]:
        st.append(("zooms", f"{spec['zooms']} regional zoom{'s' if spec['zooms'] > 1 else ''}", spec["zooms"] * ZOOM_S[L]))
    stages = [{"key": k, "label": lab, "s": round(s, 1)} for k, lab, s in st]
    return {"stages": stages, "total_s": round(sum(s["s"] for s in stages), 1)}


def options() -> dict:
    """GET /api/make/options: everything the New planet form needs."""
    from dataclasses import asdict
    from .tectonics import Params
    d = asdict(Params())
    settings = [{**s, "default": d[s["key"]]} for s in SETTINGS]
    return {"presets": {k: {**v, "set": dict(v["set"])} for k, v in PRESETS.items()}, "default_preset": DEFAULT_PRESET,
            "settings": settings, "levels": [{"level": L, "cells": 10 * 4 ** L + 2, "run_s_per_gyr": RUN_S_PER_GYR[L]} for L in LEVELS],
            "defaults": DEFAULTS, "nows": NOW_CHOICES, "unsupported": UNSUPPORTED}


def _load_state(state, spec: dict) -> dict:
    """What an earlier try of this same job finished (the file `state`, make's own record):
    {"run", "t_myr", "timezoom", "world"}, each only if it is still on disk."""
    try:
        d = json.loads(Path(state).read_text())
    except (OSError, ValueError, TypeError):
        return {}
    out = d.get("out") or {}
    if d.get("spec") != json.loads(json.dumps(spec)) or not S.exists("run", out.get("run", "")):
        return {}
    have = {"timezoom": "run", "world": "world"}
    return {k: v for k, v in out.items() if k not in have or S.exists(have[k], v)}


def make(req: dict, progress=lambda f, msg: None, state=None, resume: bool = False) -> dict:
    """Runs the chain. Returns {"run", "timezoom", "world", "zooms": [...], "highlights": n, "t_myr"};
    only what was made. progress(fraction, message). A failure names the stage and what exists so far.
    state: a file the finished stages are recorded in (the server's make jobs); with resume, a run,
    time zoom or world an earlier try of the same request finished is reused, not made again (a server
    restart, PW-480: the simulation itself cannot resume, so a restart during it starts it over).
    api.Cancelled (raised by a progress report once the job is cancelled) passes through: what finished stays."""
    from . import timeline as T
    spec = parse_make_request(req)
    plan = estimate(spec)
    total = plan["total_s"] or 1.0
    start = {}
    acc = 0.0
    for s in plan["stages"]:
        start[s["key"]] = (acc / total, s["s"] / total)
        acc += s["s"]
    out: dict = _load_state(state, spec) if state and resume else {}

    def save():
        if state:
            Path(state).write_text(json.dumps({"spec": spec, "out": out}))

    hi = [0.0]  # (a stage's own fractions may restart or overshoot: the bar only moves forward)

    def prog(key):
        f0, w = start[key]

        def report(f, msg):
            hi[0] = max(hi[0], min(0.999, f0 + w * max(0.0, min(float(f), 1.0))))
            progress(hi[0], msg)
        return report

    stage = "simulate"
    try:
        if "run" in out:  # (an earlier try finished the run)
            run_id, t = out["run"], out["t_myr"]
            prog("simulate")(1.0, f"run {run_id} already made; representative moment {t:g} Myr")
        else:
            params = T.make_params(spec["set"])
            p = prog("simulate")
            p(0.0, f"simulating {spec['myr']:g} Myr at level {spec['level']} (seed {spec['seed']})")
            run_dir = T.simulate(spec["seed"], spec["level"], spec["myr"], DT, EVERY, spec["name"], params,
                                 progress=lambda f: p(f, f"tectonics: {f * spec['myr']:.0f} of {spec['myr']:g} Myr"))
            run = json.loads((run_dir / "run.json").read_text())
            run_id = out["run"] = run["id"]
            t = out["t_myr"] = H.representative_time(run["frames"])
            save()
            prog("simulate")(1.0, f"run {run_id} done; representative moment {t:g} Myr")

        tz_id = None
        if spec["timezoom"]:
            stage = "timezoom"
            if "timezoom" in out:
                prog("timezoom")(1.0, f"time zoom {out['timezoom']} already made")
            else:
                tz = api.timezoom_job({"type": "timezoom", "run": run_id, "t": t, "kyr": spec["kyr"]}, prog("timezoom"))
                out["timezoom"] = tz["run"]
                save()
            tz_id = out["timezoom"]
        if spec["finish"]:
            stage = "world"
            if "world" in out:
                prog("world")(1.0, f"world {out['world']} already made")
            else:
                req = {"type": "finish", "timezoom": tz_id, "now": spec["now"]} if tz_id else {"type": "finish", "run": run_id, "t": t}
                out["world"] = api.finish_job(req, prog("world"))["world"]
                save()
        if spec["highlights"]:
            stage = "highlights"
            prog("highlights")(0.0, "looking over the world for interesting places")
            hl = api.highlights({"world": out["world"]})
            out["highlights"] = len(hl["features"])
            prog("highlights")(1.0, f"{out['highlights']} highlights")
        if spec["zooms"]:
            stage = "zooms"
            out["zooms"] = api.zoom_highlights(out["world"], hl["features"], spec["zooms"], prog("zooms"))
    except api.Cancelled:
        raise
    except (Exception, SystemExit) as e:
        made = ", ".join(f"{k} {v}" for k, v in out.items() if k in ("run", "timezoom", "world")) or "nothing"
        raise RuntimeError(f"{stage} failed: {e or type(e).__name__} (made so far: {made})") from e
    progress(1.0, "done")
    return out
