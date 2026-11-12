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
  peoples        optional (PW-1394): a peoples run (kind 'peoples') of a named tree (dnd, seven_meals, a saved
                 tree) on the finished world and its time zoom (api.lineages_job); needs both
  languages      with peoples, on by default (PW-1634): the language pass over the peoples run (planet/language/run.py,
                 languages.json, the names), over `language_workers` forked processes; the peoples stage leaves it to this one.
                 Its gods.json (faiths) is already written by the peoples stage, so the pass does not re-derive the faiths

Settings: what the code honours today is listed in SETTINGS (tectonics.Params
fields that change the planet's character, plus seed, level and length) and
PRESETS (the showcase recipes of docs/coordination.md). `options()` is what
GET /api/make/options serves to the form. Orbit, sun strength, day length,
ocean fraction and water inventory are not parameters yet (draft-make-settings-gaps).

Time estimates (`estimate`) come from the fitted stage costs below (PW-478; the run-cost table in
docs/coordination.md has the same numbers).
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import traceback
from pathlib import Path

import numpy as np

from . import api
from . import osutil as OS
from . import store as S
from . import highlights as H
from .finish import NOWS

LEVELS = (4, 5, 6, 7, 8)
# Stage costs, fitted to the store's own timings (PW-478). Measured: L6 runs (2 store runs of 2 Gyr:
# 705 and 802 s/Gyr; health sweep 2026-10-15, 8 L6 seeds of 1 Gyr: median 659 s), L7 runs (3 sweep
# seeds of 1 Gyr: median 3028 s, 11 workers at once), time zooms (3 store runs: 0.21 s/kyr pooled),
# worlds' finish (3: mean 7.3 s), highlights (2: 1.2 s), regional zooms (500 px, 1000 km @ 2 km:
# median 15 s over 12; 25-50 km: 5 s). Levels with no measurement are scaled from the nearest
# measured one: L4 is one 100 Myr run (23 s, fixed start-up cost included), L5 is interpolated between
# L4 and L6, L7 -> L8 by the cell count (x4), and the time zoom and zoom ratios L6 -> L7 come from the
# speed pass (100 kyr 10.0 -> 30.8 s; zoom 4.85 -> 6.9 s, idle Threadripper). Measured under load
# (2-63 load average): treat as "about", the machine's load moves them by 2x.
RUN_S_PER_GYR = {4: 230, 5: 400, 6: 705, 7: 3010, 8: 12000}
# seconds per kyr of glacial time zoom
TZ_S_PER_KYR = {4: 0.07, 5: 0.12, 6: 0.21, 7: 3.5, 8: 15}  # (PW-1661: L7 measured 3.4-3.7 s/kyr for 1 and 2 Myr at load ~15-35, docs/review/timezoom/two-myr.md; L8 10-20 s/kyr, docs/coordination.md)
FINISH_S = {4: 1.5, 5: 3, 6: 9, 7: 38, 8: 155}   # finishing / slicing one world (PW-609: with its coast and resource layers, +1.5 s at L6, +9 s at L7)
HIGHLIGHTS_S = {4: 0.3, 5: 0.5, 6: 1.2, 7: 4.8, 8: 19}
ZOOM_S = {4: 8, 5: 11, 6: 15, 7: 22, 8: 31}   # one regional zoom (500 px); 25-50 km zooms run ~1/3 of this
DT, EVERY = 2.0, 4.0                          # the simulate defaults

# The showcase recipes (docs/coordination.md), as presets. `set` are tectonics.Params overrides.
PEOPLES_S = {4: 25, 5: 70, 6: 220, 7: 700, 8: 3000}   # one peoples run (store timings of 60 runs: L6 median ~220 s, L7 ~100-1800 s, median ~500 s)
# the language pass over a peoples run at 8 workers (PW-1634): L7 a24559 ~11 min (PW-1555, 620 living lects); L6 423 s (a 200 Myr
# make, 422 living, lane 12): it scales with the demes more than the cells; L4, L5 and L8 guessed from those
LANGUAGES_S = {4: 180, 5: 300, 6: 420, 7: 660, 8: 1500}
LANGUAGE_WORKERS = 8  # (the default cap: the pass forks this many processes; a shared machine keeps lanes under ~32 cores)
PRESETS = {
    "earthlike": {"label": "Earth-like", "myr": 1000, "set": {},
                  "blurb": "Default parameters: a few continents drifting around, Earth's tilt and climate."},
    "water-world": {"label": "Water world", "myr": 2000, "set": {"continental_start": 0.1, "heat_start": 2},
                    "blurb": "Starts almost all ocean with a hot young mantle; land emerges over the first Gyr."},
    "land-heavy": {"label": "Land heavy", "myr": 1000, "set": {"continental_fraction": 0.6},
                   "blurb": "60% continental crust: big continents and little ocean."},
    "cold": {"label": "Cold world", "myr": 1000, "set": {"tilt": 15, "climate_offset": -6},
             "blurb": "Low tilt and a colder climate: big ice sheets."},
    "hothouse": {"label": "Hothouse", "myr": 1000, "set": {"tilt": 45, "climate_offset": 3},
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
UNSUPPORTED = ["orbit (distance, eccentricity)", "a different star (always Sun-like, and the run ends at today's Sun)", "day length", "ocean fraction / water inventory",
               "atmosphere (pressure, CO2 level)", "planet size / gravity"]

NOW_CHOICES = [{"key": "interglacial", "label": "Interglacial (like Earth today)"},
               {"key": "glacial", "label": "Glacial maximum"}, {"key": "end", "label": "End of the time zoom"}]
DEFAULTS = {"level": 6, "myr": 1000, "kyr": 2000, "now": "interglacial", "timezoom": True, "finish": True, "highlights": True, "zooms": 4,
            "require_ice": False, "tries": 3, "peoples": "", "languages": True, "language_workers": LANGUAGE_WORKERS}  # require_ice (owner D19, PW-1164): refuse a finish with no permanent ice, re-rolling the seed up to `tries` runs


GODS_MODE_LABELS = [["faith_made", "faith-made (gods exist while worshipped)"], ["belief_only", "belief only (no gods are real, no divine magic)"],
                    ["absolute", "absolute (gods outlive their worshippers)"]]  # (PW-1309; the ids are spec.GODS_MODES)


def peoples_trees() -> list[str]:
    """The names of the peoples trees a make may use: the presets (dnd, seven_meals, ...) and the saved trees."""
    from .lineages import run as LR
    return [t["name"] for t in LR.list_trees() if t["name"] != "techtree"]


def parse_make_request(req: dict) -> dict:
    """Validates a make request and fills defaults. Raises api.BadRequest.
    {seed, preset, level, myr, set, timezoom, kyr, now, finish, highlights, zooms, name, require_ice, tries, peoples, languages,
    language_workers}
    (peoples: the name of a peoples tree, a preset such as dnd or seven_meals or a saved one; "" makes none; languages: with
    peoples, run the language pass too (default on, PW-1634), over language_workers processes (1..16, default 8))"""
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
    out["require_ice"] = bool(req.get("require_ice", DEFAULTS["require_ice"]))
    out["tries"] = int(api._num(req, "tries", DEFAULTS["tries"]))
    if not 1 <= out["tries"] <= 8:
        raise api.BadRequest("tries must be within 1..8")
    out["peoples"] = str(req.get("peoples") or "").strip()
    if out["peoples"]:
        if peoples_trees() and out["peoples"] not in peoples_trees():
            raise api.BadRequest(f"peoples must be one of {peoples_trees()} (or empty for none)")
        if not (out["timezoom"] and out["finish"]):
            raise api.BadRequest("peoples need the time zoom and the finished world (they are built on both)")
    out.update(api._gods_mode(req) if out["peoples"] else {})  # (PW-1309: the peoples run's gods mode)
    out["languages"] = bool(out["peoples"]) and bool(req.get("languages", DEFAULTS["languages"]))  # (PW-1634)
    out["language_workers"] = int(api._num(req, "language_workers", DEFAULTS["language_workers"]))
    if not 1 <= out["language_workers"] <= 16:
        raise api.BadRequest("language_workers must be within 1..16")
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
    st = [("simulate", f"Simulating {spec['myr']:g} Myr of tectonics"
                       + (f" (one try; a roll with no permanent ice is re-rolled, up to {spec['tries']} tries)" if spec["require_ice"] else ""),
           spec["myr"] / 1000 * RUN_S_PER_GYR[L])]
    if spec["timezoom"]:
        st.append(("timezoom", f"Ice ages: {spec['kyr']:g} kyr time zoom", spec["kyr"] * TZ_S_PER_KYR[L]))
    if spec["finish"]:
        st.append(("world", "Finishing the world", FINISH_S[L]))
    if spec["highlights"]:
        st.append(("highlights", "Finding highlights", HIGHLIGHTS_S[L]))
    if spec["zooms"]:
        st.append(("zooms", f"{spec['zooms']} regional zoom{'s' if spec['zooms'] > 1 else ''}", spec["zooms"] * ZOOM_S[L]))
    if spec["peoples"]:
        st.append(("peoples", f"Peoples ({spec['peoples']})", PEOPLES_S[L]))
    if spec.get("languages"):
        w = spec.get("language_workers", LANGUAGE_WORKERS)
        st.append(("languages", f"Languages ({w} worker{'s' if w > 1 else ''})", LANGUAGES_S[L] * 8 / min(w, 8)))
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
            "peoples": peoples_trees(), "gods_modes": GODS_MODE_LABELS, "defaults": DEFAULTS, "nows": NOW_CHOICES, "unsupported": UNSUPPORTED}


def reroll_seed(seed: int, k: int) -> int:
    """The seed of roll k (k >= 1) of a require-permanent-ice make: derived from the first, so the whole chain repeats."""
    return int(np.random.default_rng([int(seed), int(k)]).integers(10**6))


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
    have = {"timezoom": "run", "world": "world", "peoples": "run"}
    out = {k: v for k, v in out.items() if k not in have or S.exists(have[k], v)}
    if out.get("languages") and "peoples" not in out:  # (languages belong to the peoples run they were made over)
        out.pop("languages")
    return out


DEBUG_ENV = "PLANET_DEBUG"  # (set, not 0/no/off: a failed stage's traceback is also printed to stderr)


def log_failure(stage: str, run_id: str | None) -> str | None:
    """Called inside the except block of a failed stage: appends the full traceback to the run's run.txt (when the run
    exists) and, with $PLANET_DEBUG set, prints it to stderr, so a failure on a machine we can't reach (the 3-OS CI,
    PW-1760) shows where it came from. Returns the log file's path for the message, or None. Never raises."""
    tb = traceback.format_exc()
    if os.environ.get(DEBUG_ENV, "").lower() not in ("", "0", "no", "off"):
        print(f"planet make: {stage} failed:\n{tb}", file=sys.stderr, flush=True)
    if not run_id:
        return None
    try:
        path = S.find_run(run_id) / "run.txt"
        with open(path, "a") as f:
            f.write(f"\nplanet make: {stage} failed:\n{tb}")
        return S.rel(path)
    except (Exception, SystemExit):  # noqa: BLE001 (the log is a help; the stage's own error is what is raised)
        return None


def make(req: dict, progress=lambda f, msg: None, state=None, resume: bool = False) -> dict:
    """Runs the chain. Returns {"run", "timezoom", "world", "zooms": [...], "highlights": n, "peoples": run id, "languages": {living,
    languages, secs} (PW-1634), "t_myr", "zooms_skipped": why (the memory guard refused a zoom: skipped, not failed, PW-1760)};
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
            params = T.make_params({**spec["set"], "finish_require_ice": spec["require_ice"]})
            p = prog("simulate")
            rolls = []  # (recorded in the output only with require_ice: off, the output is unchanged)
            tries = spec["tries"] if spec["require_ice"] else 1
            for k in range(tries):  # (require permanent ice: a roll whose finish window has none is refused, then a new seed)
                seed = spec["seed"] if k == 0 else reroll_seed(spec["seed"], k)
                p(k / tries, f"simulating {spec['myr']:g} Myr at level {spec['level']} (seed {seed}"
                  + (f", roll {k + 1} of {tries})" if spec["require_ice"] else ")"))
                run_dir = T.simulate(seed, spec["level"], spec["myr"], DT, EVERY, spec["name"], params,
                                     progress=lambda f, k=k: p((k + f) / tries, f"tectonics: {f * spec['myr']:.0f} of {spec['myr']:g} Myr"))
                run = json.loads((run_dir / "run.json").read_text())
                fm = run["meta"]["finish_moment"]
                rolls.append({"seed": seed, "run": run["id"], "permanent_ice": not fm["no_permanent_ice"],
                              "finish": fm["why"]})
                if spec["require_ice"]:
                    p((k + 1) / tries, f"roll {k + 1}: seed {seed} "
                      + ("has permanent ice" if rolls[-1]["permanent_ice"] else "has NO permanent ice: refused"))
                if rolls[-1]["permanent_ice"] or not spec["require_ice"]:
                    break
            else:
                made = ", ".join(f"seed {r['seed']} (run {r['run']})" for r in rolls)
                raise RuntimeError(f"no roll had permanent ice in {tries} tries: {made}; the runs are kept")
            if spec["require_ice"]:
                out["seed"], out["rolls"] = seed, rolls
            run_id = out["run"] = run["id"]
            t = out["t_myr"] = H.representative_time(run["frames"], run["meta"])
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
            skipped: list = []  # (the memory guard says no: the zoom is skipped, the world stands, PW-1760)
            out["zooms"] = api.zoom_highlights(out["world"], hl["features"], spec["zooms"], prog("zooms"), skipped=skipped)
            if skipped:
                sk = skipped[0]
                out["zooms_skipped"] = (f"skipped {sk['not_made']} of {sk['picked']} regional zoom"
                                        f"{'s' if sk['picked'] > 1 else ''}: {sk['reason']}")
                prog("zooms")(1.0, out["zooms_skipped"])
        if spec["peoples"]:
            stage = "peoples"
            if "peoples" in out:
                prog("peoples")(1.0, f"peoples run {out['peoples']} already made")
            else:
                out["peoples"] = api.lineages_job({"type": "lineages", "world": out["world"], "tree": spec["peoples"], "languages": False,
                                                   **({"gods_mode": spec["gods_mode"]} if spec.get("gods_mode") else {})}, prog("peoples"))["run"]
                save()
        if spec["languages"]:
            stage = "languages"
            if "languages" in out:
                prog("languages")(1.0, f"languages of {out['peoples']} already made")
            else:
                from .language import run as LR
                p = prog("languages")
                p(0.0, f"languages: the pass over peoples run {out['peoples']} ({spec['language_workers']} workers)")
                rd = S.find_run(out["peoples"])
                try:  # (a failure is logged, not fatal, as in the peoples stage before: the peoples run stands without languages)
                    sm = LR.write(rd, workers=OS.fork_workers(spec["language_workers"]), report=True, progress=p)  # (no fork on Windows: 1, PW-1760)
                except api.Cancelled:
                    raise
                except Exception as e:  # noqa: BLE001 (a run too short for the pass's 20 kyr, no demes...)
                    with open(rd / "run.txt", "a") as f:
                        f.write(f"languages (PW-986): failed, {type(e).__name__}: {e}\n")
                    out["languages"] = {"error": f"{type(e).__name__}: {e}"}
                    p(1.0, f"languages: not made ({e}); `planet languages {out['peoples']}` retries")
                else:
                    out["languages"] = {"living": sm.get("living"), "languages": sm.get("languages"), "secs": sm.get("generated_in_s")}
                    p(1.0, f"languages: {sm.get('living')} living lects, {sm.get('languages')} languages")
                    try:  # (the features' names, PW-1656: a read-out of the languages; a failure leaves the run as it is)
                        from .lineages import featnames as FN
                        FN.write(rd)
                    except Exception as e:  # noqa: BLE001
                        with open(rd / "run.txt", "a") as f:
                            f.write(f"features (PW-1656): failed, {type(e).__name__}: {e}\n")
                save()
    except api.Cancelled:
        raise
    except (Exception, SystemExit) as e:
        made = ", ".join(f"{k} {v}" for k, v in out.items() if k in ("run", "timezoom", "world", "peoples")) or "nothing"
        where = log_failure(stage, out.get("run"))
        raise RuntimeError(f"{stage} failed: {e or type(e).__name__} (made so far: {made})"
                           + (f"; the traceback is in {where}" if where else "")) from e
    progress(1.0, "done")
    return out
