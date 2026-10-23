"""What `planet serve` does beyond static files: regional zooms requested
from the viewer. Plain functions plus a job queue (Jobs: up to `workers` jobs
at once, in worker processes for the server, saved to a file so a restart
keeps it), so tests can drive them without a socket.

  POST /api/zoom      {run, t} or {world}, plus {lat, lon, size_km, res_km,
                      seed?, iterations? (landscape-pass iterations, default 15)}
                      -> {"job": id}
  GET  /api/jobs/<id> -> {"status": queued|running|done|error, "progress": 0..1,
                          "message", "zoom" (when done), "error" (when failed)}
  GET  /api/highlights?run=<id>&t=<Myr>  or  ?world=<id>   [&cached=1] [&refresh=1]
                      -> {"world", "t_myr", "features": [...] (highlights.py), each
                          with "zoom": the id of an existing zoom of it, or null}
                      For a run this builds the world first if needed (a few
                      seconds). cached=1 only looks: features is null when
                      nothing has been computed yet.
  POST /api/timezoom  {run, t, kyr?} -> {"job": id}: a glacial time zoom
                      (timezoom/) from the run's keyframe nearest t; the
                      job's "run" is the new run's id when done. Shares the
                      job queue with zooms.
  POST /api/make      {seed?, preset?, level?, myr?, set?, timezoom?, kyr?, finish?, highlights?,
                      zooms?, now?, name?} -> {"job": id}: the whole chain (make.py); the job's "run",
                      "timezoom", "world" and "zooms" are what it made. GET /api/make/options and
                      /api/make/estimate?... describe the form and the expected time.
  POST /api/highlight-zooms  {world, n?} -> {"job": id}: regional zooms of the world's top n highlights
                      (highlights.pick_zooms, what `planet highlights --zoom N` makes; n default 4); the
                      job's "zooms" are their ids and "zoom" the first.
  DELETE /api/jobs/<id>  cancels a queued or running job (a worker stops at its next progress report;
                      what a make job already finished is kept, the unfinished stage's partial output is
                      removed). A server restart resumes a make job at its first unfinished stage.
  POST /api/finish    {timezoom, kyr} or {run, t} -> {"job": id}: a finished
                      world (finish.py) at the time zoom's frame nearest kyr,
                      or straight from the run's keyframe nearest t (the
                      same world the Zoom button makes); the job's "world"
                      is its id when done. Reuses an existing one.
"""

from __future__ import annotations

import itertools
import json
import os
import queue
import tempfile
import threading
import time
from pathlib import Path

from . import highlights as H
from . import store as S
from . import timeline as T
from . import world as W
from . import zoom as Z
from . import zoom_fine as ZF

ZOOM_PX = 500  # the viewer's zooms are 500 x 500 px whatever their size
# One computation at a time in this process (re-entrant: a job slices inside
# it). Under numba's workqueue threading layer (the fallback when TBB doesn't
# load, parallel.pin_threading_layer) two threads launching parallel kernels
# at once abort the process, and in-process jobs and highlights requests
# (server threads) both run them. Per process only: the server's jobs run in
# worker processes, each with its own. What two processes must not both
# build (a slice, a zoom, a time zoom, a world's highlights) takes a file
# lock instead (store.lock).
COMPUTE = threading.RLock()


class BadRequest(ValueError):
    pass


def _num(req: dict, key: str, default=None) -> float:
    v = req.get(key, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        raise BadRequest(f"{key} must be a number") from None


def parse_zoom_request(req: dict) -> dict:
    """Validates and fills defaults; raises BadRequest."""
    if not isinstance(req, dict):
        raise BadRequest("expected a JSON object")
    if sum(bool(req.get(k)) for k in ("run", "world", "zoom")) != 1:
        raise BadRequest("give either run (+ t), world, or zoom (a fine zoom of that zoom)")
    if req.get("zoom"):
        return _parse_fine_request(req)
    out = {"lat": _num(req, "lat"), "lon": _num(req, "lon"), "size_km": _num(req, "size_km", 1000)}
    out["res_km"] = _num(req, "res_km", out["size_km"] / 500)
    out["seed"] = int(_num(req, "seed", 1))
    out["iterations"] = int(_num(req, "iterations", 15))
    if not 1 <= out["iterations"] <= 100:
        raise BadRequest("iterations must be within 1..100")
    if not -90 <= out["lat"] <= 90:
        raise BadRequest("lat must be within -90..90")
    out["lon"] = (out["lon"] + 180) % 360 - 180
    if not 10 <= out["size_km"] <= 5000:
        raise BadRequest("size_km must be within 10..5000")
    if out["res_km"] <= 0 or out["size_km"] / out["res_km"] > 4096:
        raise BadRequest("keep size_km / res_km within 1..4096")
    if req.get("run"):
        out["run"] = str(req["run"])
        out["t"] = _num(req, "t")
    else:
        out["world"] = str(req["world"]).removesuffix(".json")
    return out


def _parse_fine_request(req: dict) -> dict:
    """A fine zoom (zoom_fine) of zoom `zoom`: size_km / res_km default to
    zoom_fine.default_size of the parent's resolution; checked against the
    parent (SystemExit: no such zoom)."""
    pid = str(req["zoom"])
    pmeta = json.loads((S.find_zoom(pid) / "zoom.json").read_text())
    ds, dr = ZF.default_size(float(pmeta["res_km"]))
    out = {"zoom": pmeta["id"], "lat": _num(req, "lat"), "lon": _num(req, "lon"), "seed": int(_num(req, "seed", 1))}
    out["res_km"] = _num(req, "res_km", dr)
    out["size_km"] = _num(req, "size_km", ds if out["res_km"] == dr else 500 * out["res_km"])
    out["lon"] = (out["lon"] + 180) % 360 - 180
    try:
        ZF.check(pmeta, out["lat"], out["lon"], out["size_km"], out["res_km"])
    except ValueError as e:
        raise BadRequest(str(e)) from None
    return out


def world_header(path: Path) -> dict:
    """name/id/meta of a saved world without parsing its layers."""
    return S.read_header(path, ("name", "id", "meta"))


def find_slice(run_dir: Path, at: float) -> Path | None:
    """An already saved world sliced from this run at this time, if any."""
    for p in sorted(S.worlds_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if p.name == "index.json":
            continue
        try:
            m = world_header(p).get("meta", {})
        except (OSError, ValueError):
            continue
        if (m.get("source_run") == run_dir.name and m.get("t_myr") is not None and abs(m["t_myr"] - at) < 1e-6
                and not m.get("timezoom")):  # (not a world finished from a time zoom of that moment)
            return p
    return None


def keyframe_t(run_dir: Path, t: float) -> float:
    """The run's keyframe time nearest t."""
    run = json.loads((run_dir / "run.json").read_text())
    times = [f["t"] for f in run["frames"]]
    at = min(times, key=lambda x: abs(x - t))
    if abs(at - t) > run["meta"]["every"]:
        raise BadRequest(f"t must be between 0 and {run['meta']['myr']}")
    return at


def slice_run(run_ref: str, t: float, progress=lambda f, msg: None) -> Path:
    """A world at the run's keyframe nearest t, built straight from the stored
    keyframe (a few seconds, and exactly what the viewer shows). Runs too old
    for that are replayed from t=0 instead, which refuses if the code has
    changed since. Reuses an existing slice."""
    with COMPUTE:
        return _slice_run(run_ref, t, progress)


def _slice_run(run_ref: str, t: float, progress) -> Path:
    run_dir = S.find_run(run_ref)
    at = keyframe_t(run_dir, t)
    with S.lock(S.runs_dir(), f"slice-{run_dir.name}-{at:g}"):  # (another process may be slicing it now)
        return _slice_locked(run_dir, at, progress)


def _slice_locked(run_dir: Path, at: float, progress) -> Path:
    run = S.read_header(run_dir / "run.json")
    found = find_slice(run_dir, at)
    if found:
        progress(1.0, f"using world {found.stem} (already sliced at {at:g} Myr)")
        return found
    progress(0.1, "building the world from the keyframe (climate, rivers, biomes)")
    try:
        world = T.world_from_frame(run_dir, at)
    except ValueError:
        progress(0.1, f"old run: replaying {run_dir.name} to {at:g} Myr (can take a minute)")
        try:
            return T.slice_world(run_dir, at)
        except T.ReplayMismatch as e:
            raise BadRequest(str(e)) from None
    path = W.save(world, f"{run['name']} @ {at:g} Myr")
    progress(1.0, f"saved world {path.stem}")
    return path


def zoom_job(req: dict, progress=lambda f, msg: None) -> dict:
    """The whole request: slice a run if needed, then zoom. Returns
    {"zoom": id, "world": id}. Reuses an identical existing zoom."""
    r = parse_zoom_request(req)
    if "zoom" in r:
        return _fine_zoom_job(r, progress)
    if "run" in r:
        world_path = slice_run(r["run"], r["t"], lambda f, msg: progress(0.5 * f, msg))
    else:
        world_path = S.find_world(r["world"])
    zid = Z.zoom_id(world_path.stem, r["lat"], r["lon"], r["size_km"], r["res_km"], r["seed"], r["iterations"])
    with S.lock(S.zooms_dir(), zid):  # (one process builds a zoom; the others then find it)
        if S.exists("zoom", zid):
            progress(1.0, f"zoom {zid} already exists")
            return {"zoom": zid, "world": world_path.stem}
        return _build_zoom(r, world_path, progress)


def _build_zoom(r: dict, world_path: Path, progress) -> dict:
    done = [0]

    def log(msg):  # build() logs four stages
        done[0] += 1
        progress(0.5 + 0.5 * min(done[0], 4) / 5, msg.strip())

    progress(0.5, "zooming in")
    out = Z.zoom(str(world_path), r["lat"], r["lon"], r["size_km"], r["res_km"], r["seed"], r["iterations"], log=log)
    progress(1.0, "done")
    return {"zoom": out.name, "world": world_path.stem}


def _fine_zoom_job(r: dict, progress) -> dict:
    """A fine zoom of zoom r["zoom"] (zoom_fine). Returns {"zoom", "world",
    "parent_zoom"}; reuses an identical existing one."""
    pmeta = json.loads((S.find_zoom(r["zoom"]) / "zoom.json").read_text())
    wid = pmeta["source_world"]["id"]
    zid = ZF.fine_id(r["zoom"], r["lat"], r["lon"], r["size_km"], r["res_km"], r["seed"])
    with S.lock(S.zooms_dir(), zid):
        if S.exists("zoom", zid):
            progress(1.0, f"zoom {zid} already exists")
            return {"zoom": zid, "world": wid, "parent_zoom": r["zoom"]}
        done = [0]

        def log(msg):  # build() logs three stages
            done[0] += 1
            progress(min(done[0], 3) / 4, msg.strip())

        progress(0.05, f"zooming into zoom {r['zoom']}")
        out = ZF.zoom(r["zoom"], r["lat"], r["lon"], r["size_km"], r["res_km"], r["seed"], log=log)
        progress(1.0, "done")
        return {"zoom": out.name, "world": wid, "parent_zoom": r["zoom"]}


def parse_source(req: dict) -> dict:
    """{run, t} or {world} from a request (query values may be strings)."""
    if bool(req.get("run")) == bool(req.get("world")):
        raise BadRequest("give either run (+ t) or world")
    if req.get("run"):
        return {"run": str(req["run"]), "t": _num(req, "t")}
    return {"world": str(req["world"]).removesuffix(".json")}


def zoom_request(source: dict, f: dict) -> dict:
    """The zoom request the viewer sends for a highlight (so the zoom ids match)."""
    return {**source, "lat": f["lat"], "lon": f["lon"], "size_km": f["size_km"], "res_km": f["size_km"] / ZOOM_PX}


def highlights_job(req: dict, progress=lambda f, msg: None) -> dict:
    """The heavy part of highlights (the server runs it in a worker process):
    slices the run if needed ({run, t} with t a keyframe, or {world}), then
    computes and caches the world's highlights (again if req["refresh"]).
    Returns {"world": its path, "highlights": them}."""
    if "run" in req:
        world_path = slice_run(req["run"], req["t"], progress)
    else:
        world_path = S.find_world(req["world"])
    with COMPUTE:  # (waits for a job running in this process)
        d = H.for_world(world_path, bool(req.get("refresh")))
    return {"world": str(world_path), "highlights": d}


def highlights(req: dict, cached_only: bool = False, refresh: bool = False, compute=None) -> dict:
    """GET /api/highlights. For a run, builds the world at that keyframe
    first if there isn't one (unless cached_only). What isn't cached is
    computed by compute(highlights_job, req) (the server's: a worker
    process, parallel.Pool.call; default: here)."""
    src = parse_source(req)
    if "run" in src:
        run_dir = S.find_run(src["run"])
        at = keyframe_t(run_dir, src["t"])
        src["t"] = at
        world_path = find_slice(run_dir, at)
    else:
        world_path = S.find_world(src["world"])
    d = H.cached(world_path) if world_path is not None and (cached_only or not refresh) else None
    if d is None and not cached_only:
        res = (compute or (lambda fn, r: fn(r)))(highlights_job, {**src, "refresh": refresh})
        world_path, d = Path(res["world"]), res["highlights"]
    out = {"source": src, "world": world_path.stem if world_path else None,
           "t_myr": src.get("t"), "features": None}
    if d is None:
        return out
    feats = []
    for f in d["features"]:
        zr = zoom_request(src, f)
        zid = Z.zoom_id(world_path.stem, zr["lat"], zr["lon"], zr["size_km"], zr["res_km"], 1)
        feats.append({**f, "zoom": zid if S.exists("zoom", zid) else None})
    return {**out, "name": d.get("name"), "t_myr": d.get("t_myr"), "computed_in_s": d.get("computed_in_s"),
            "features": feats}


TIMEZOOM_KYR = (100, 300, 1000)  # the viewer's choices; the API takes 1..2000


def parse_timezoom_request(req: dict) -> dict:
    """{run, t, kyr} checked against the run (exists, is a main run with
    climate in its keyframes); t snaps to the nearest keyframe. Raises
    BadRequest, or SystemExit for an unknown run."""
    if not isinstance(req, dict) or not req.get("run"):
        raise BadRequest("give run and t")
    out = {"type": "timezoom", "run": str(req["run"]), "kyr": _num(req, "kyr", 300)}
    if not 1 <= out["kyr"] <= 2000:
        raise BadRequest("kyr must be within 1..2000")
    run_dir = S.find_run(out["run"])
    run = json.loads((run_dir / "run.json").read_text())
    if run.get("kind") == "timezoom":
        raise BadRequest("this is a time zoom already; start one from its source run")
    out["t"] = keyframe_t(run_dir, _num(req, "t"))
    if "sea_level_m" not in run["frames"][0]["stats"]:
        raise BadRequest(f"run {run_dir.name} is too old (its keyframes have no climate)")
    return out


def find_timezoom(run_id: str, at: float, kyr: float) -> str | None:
    """An existing time zoom of this run, moment and length with the default
    knobs, if any (the viewer's button makes only those)."""
    from .timezoom import TZParams
    from dataclasses import asdict
    defaults = asdict(TZParams())
    for p in S.runs_dir().glob("*/run.json"):
        try:
            r = S.read_header(p)
        except (OSError, ValueError):
            continue
        m = r.get("meta", {})
        if (r.get("kind") == "timezoom" and m.get("source_run") == run_id and abs(m["at_myr"] - at) < 1e-6
                and abs(m["kyr"] - kyr) < 1e-6 and m.get("timezoom") == defaults):
            return r.get("id", p.parent.name)
    return None


def timezoom_job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/timezoom's work: {"run": id of the new time zoom}."""
    from . import timezoom as TZ
    r = parse_timezoom_request(req)
    run_dir = S.find_run(r["run"])
    run_id = S.read_header(run_dir / "run.json").get("id", run_dir.name)  # as timezoom records it
    with S.lock(S.runs_dir(), f"timezoom-{run_id}-{r['t']:g}-{r['kyr']:g}"):
        found = find_timezoom(run_id, r["t"], r["kyr"])
        if found:
            progress(1.0, f"time zoom {found} already exists")
            return {"run": found}
        progress(0.0, f"{r['kyr']:g} kyr of ice ages from {r['t']:g} Myr")
        out = TZ.timezoom(str(run_dir), r["t"], r["kyr"], progress=lambda f, msg: progress(0.98 * f, msg))
    progress(1.0, "done")
    return {"run": out.name}


def parse_finish_request(req: dict) -> dict:
    """{timezoom, kyr | now} or {run, t}, checked (now: interglacial, glacial, end or a kyr, finish.now_kyr): the time zoom exists and kyr is
    within it (snapped to its nearest frame), or the run is a main run and t
    snaps to its nearest keyframe. Raises BadRequest, or SystemExit for an
    unknown id."""
    from . import finish as F
    if not isinstance(req, dict) or bool(req.get("timezoom")) == bool(req.get("run")):
        raise BadRequest("give either timezoom (+ kyr) or run (+ t)")
    if req.get("timezoom"):
        try:
            tz_dir, run = F.load_timezoom(str(req["timezoom"]))
        except SystemExit as e:
            if "not a glacial time zoom" in str(e):
                raise BadRequest(str(e)) from None
            raise
        try:
            if req.get("now") not in (None, ""):  # (PW-479: interglacial | glacial | end | a kyr)
                kyr = F.now_kyr(run, req["now"])[0]
            else:
                kyr = _num(req, "kyr", run["frames"][-1]["t"])
            i = F.frame_index(run, kyr)
        except SystemExit as e:
            raise BadRequest(str(e)) from None
        return {"type": "finish", "timezoom": tz_dir.name, "kyr": run["frames"][i]["t"]}
    run_dir = S.find_run(str(req["run"]))
    run = S.read_header(run_dir / "run.json")
    if run.get("kind") == "timezoom":
        raise BadRequest("this is a time zoom: give it as timezoom (+ kyr)")
    return {"type": "finish", "run": run_dir.name, "t": keyframe_t(run_dir, _num(req, "t"))}


def finish_job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/finish's work: {"world": id of the finished world}."""
    from . import finish as F
    r = parse_finish_request(req)
    if "timezoom" in r:
        with COMPUTE:
            path = F.finish_timezoom(r["timezoom"], r["kyr"], progress=progress)
    else:
        path = slice_run(r["run"], r["t"], progress)
    progress(1.0, f"world {path.stem}")
    return {"world": path.stem}


class Cancelled(Exception):
    """A job was cancelled (DELETE /api/jobs/<id>): raised by a progress report in the worker."""


def parse_highlight_zooms_request(req: dict) -> dict:
    if not isinstance(req, dict) or not req.get("world"):
        raise BadRequest("give a world")
    n = int(_num(req, "n", 4))
    if not 1 <= n <= 12:
        raise BadRequest("n must be within 1..12")
    world = str(req["world"]).removesuffix(".json")
    S.find_world(world)  # (SystemExit: no such world)
    return {"type": "hlzooms", "world": world, "n": n}


def zoom_highlights(world: str, features: list[dict], n: int, progress=lambda f, msg: None) -> list[str]:
    """Regional zooms (the viewer's: zoom_request) of the top n zoomable highlights; the zoom ids."""
    picks = H.pick_zooms(features, n)
    out = []
    for k, f in enumerate(picks):
        z = zoom_job(zoom_request({"world": world}, f),
                     lambda fr, msg, k=k, f=f: progress((k + fr) / len(picks), f"zoom {k + 1}/{len(picks)}: {f['title']}"))
        out.append(z["zoom"])
    return out


def highlight_zooms_job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/highlight-zooms: the world's highlights (cached or computed), then zooms of the top n."""
    r = parse_highlight_zooms_request(req)
    progress(0.0, "looking over the world for interesting places")
    hl = highlights({"world": r["world"]})
    zooms = zoom_highlights(r["world"], hl["features"], r["n"], lambda f, msg: progress(0.05 + 0.95 * f, msg))
    return {"world": r["world"], "zooms": zooms, **({"zoom": zooms[0]} if zooms else {})}


def make_job(req: dict, progress=lambda f, msg: None, ctx: dict | None = None) -> dict:
    """POST /api/make's work (make.make): seed to finished world. {"run", "timezoom", "world", "zooms"}.
    ctx: {"state": a file the stages finished so far are kept in, "resume": use it (a restarted job)}."""
    from . import make
    return make.make(req, progress, state=(ctx or {}).get("state"), resume=bool((ctx or {}).get("resume")))


def lineages_job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/lineages's work (planet/lineages/run.job): {"run"} (a peoples run, meta.phase 'lineages')."""
    from .lineages import run as LR
    return LR.job({k: v for k, v in req.items() if k != "type"}, progress)


def parse_lineages_request(req: dict) -> dict:
    """Check a POST /api/lineages {world | timezoom, tree | raw, tries} now, so a bad one fails at once."""
    from .lineages import recent as R
    from .lineages import run as LR
    from .lineages import spec as SP
    ref = req.get("world") or req.get("timezoom")
    if not ref:
        raise BadRequest("give world or timezoom")
    try:
        tz = R.resolve(str(ref).removesuffix(".json"))[0]
        if not S.exists("run", tz):
            raise ValueError(f"the time zoom {tz} (of {ref}) has been deleted; peoples need it")
        SP.parse(req["raw"]) if req.get("raw") else LR.load_tree(str(req.get("tree") or ""))
    except (ValueError, KeyError, FileNotFoundError) as e:
        raise BadRequest(str(e)) from e
    tries = int(_num(req, "tries", 4))
    if not 1 <= tries <= 16:
        raise BadRequest("tries is 1-16")
    out = {"type": "lineages", "tries": tries, **({"world": str(req["world"])} if req.get("world") else
                                                  {"timezoom": str(req["timezoom"])})}
    out.update({"raw": req["raw"]} if req.get("raw") else {"tree": str(req["tree"])})
    return out


ENRICH = ("resources", "coast")  # what POST /api/enrich can add to a saved world


def parse_enrich_request(req: dict) -> dict:
    """Check a POST /api/enrich {world, what: resources | coast} now (the layers `planet resources` / `planet coast` add)."""
    if not isinstance(req, dict) or not req.get("world"):
        raise BadRequest("give a world")
    if req.get("what") not in ENRICH:
        raise BadRequest(f"what is one of {', '.join(ENRICH)}")
    world = str(req["world"]).removesuffix(".json")
    S.find_world(world)  # (SystemExit: no such world)
    return {"type": "enrich", "world": world, "what": req["what"]}


def enrich_job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/enrich's work: add the resource or coast layers to the saved world in place."""
    r = parse_enrich_request(req)
    progress(0.05, f"adding {r['what']} to world {r['world']}")
    if r["what"] == "resources":
        from . import resources as RS
        RS.add_to_world(r["world"], log=lambda *a: None)
    else:
        from . import coastform as CF
        CF.add_to_world(r["world"])
    progress(1.0, "done")
    return {"world": r["world"]}


JOBS = {"timezoom": timezoom_job, "finish": finish_job, "hlzooms": highlight_zooms_job, "make": make_job,
        "lineages": lineages_job, "enrich": enrich_job}


def any_job(req: dict, progress=lambda f, msg: None) -> dict:
    """The server's job queue runs zooms, time zooms and finished worlds (req["type"]),
    each holding COMPUTE (in its worker process). req["_job"] (added by Jobs) is {"cancel": a flag
    file (once it exists, the next progress report raises Cancelled), "state" and "resume": make's}."""
    ctx = req.get("_job") or {}
    if ctx:
        req = {k: v for k, v in req.items() if k != "_job"}
    flag = ctx.get("cancel")
    if flag:
        report = progress

        def progress(f, msg):  # (the same, but stops a cancelled job)
            if os.path.exists(flag):
                raise Cancelled("cancelled")
            report(f, msg)
    with COMPUTE:
        if req.get("type") == "make":
            return make_job(req, progress, ctx)
        return JOBS.get(req.get("type"), zoom_job)(req, progress)


class Jobs:
    """Background jobs, up to `workers` at once, started in submission order
    (one thread per slot; the server's fn runs each job in a worker process,
    parallel.Pool.caller, so jobs don't share a process or its COMPUTE; two
    jobs that need the same slice or zoom wait on its file lock and the
    second reuses it). The same request while one is queued or running gets
    that job. With a path, their state is saved there (JSON, on every status
    change and at most every SAVE_EVERY_S of progress) and read back when the
    server starts again: finished jobs keep answering the viewer's polls, and
    jobs that were queued or running are queued again (their outputs are
    reused or remade; a job interrupted twice is marked failed, in case it is
    what brought the server down). Finished jobs are forgotten after KEEP_S.

    contexts=True (the server's) gives each job's request a "_job" entry, {"cancel", "state",
    "resume"} (any_job): cancel(jid) then stops a running job at its next progress report, and a make
    job queued again after a restart carries on from the stages it finished (make.make)."""

    SAVE_EVERY_S = 2.0
    KEEP_S = 7 * 24 * 3600.0

    def __init__(self, fn=any_job, path: Path | None = None, workers: int = 1, contexts: bool = False):
        self.fn = fn
        self.contexts = contexts
        self._dir: Path | None = None  # (the cancel flags and make states, made when first needed)
        self.path = Path(path) if path else None
        self.jobs: dict[str, dict] = {}
        self.lock = threading.Lock()
        self._take = threading.Lock()
        self.q: queue.Queue = queue.Queue()
        self.ids = itertools.count(1)
        self.n_workers = max(1, int(workers))
        self.workers: list[threading.Thread] = []
        self._saved = 0.0
        if self.path:
            self._load()

    def _load(self):
        try:
            jobs = json.loads(self.path.read_text())
        except (OSError, ValueError):
            return
        now, again = time.time(), []
        for j in sorted(jobs.values(), key=lambda j: j.get("created", 0)):
            if j.get("status") in ("done", "error"):
                if now - j.get("finished", now) < self.KEEP_S:
                    self.jobs[j["id"]] = j
                continue
            if j.get("restarts", 0) >= 1:
                j.update(status="error", error="the server restarted twice during this job", finished=now)
            else:
                j.update(status="queued", progress=0.0, restarts=j.get("restarts", 0) + 1, resume=True,
                         message="queued again after a server restart")
                again.append(j["id"])
            self.jobs[j["id"]] = j
        n = max((int(k.split("-")[0]) for k in self.jobs if k.split("-")[0].isdigit()), default=0)
        self.ids = itertools.count(n + 1)
        with self.lock:
            self._save(force=True)
            if again:
                self._start_worker()
        for jid in again:
            self.q.put(jid)

    def _save(self, force: bool = False):
        """Write the jobs (call with self.lock held)."""
        if not self.path or (not force and time.time() - self._saved < self.SAVE_EVERY_S):
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(f"{self.path.name}.{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(self.jobs, default=str))
        tmp.replace(self.path)
        self._saved = time.time()

    def _start_worker(self):
        """Starts the job threads if they aren't running (call with self.lock held, or before any)."""
        self.workers = [w for w in self.workers if w.is_alive()]
        while len(self.workers) < self.n_workers:
            w = threading.Thread(target=self._loop, daemon=True)
            w.start()
            self.workers.append(w)

    def submit(self, req: dict) -> str:
        key = json.dumps(req, sort_keys=True)
        with self.lock:
            for j in self.jobs.values():  # the same request twice -> the same job
                if j["key"] == key and j["status"] in ("queued", "running"):
                    return j["id"]
            jid = f"{next(self.ids)}-{int(time.time()) % 100000}"
            self.jobs[jid] = {"id": jid, "key": key, "request": req, "status": "queued", "progress": 0.0,
                              "message": "waiting for a free worker", "created": time.time()}
            self._save(force=True)
            self._start_worker()
        self.q.put(jid)
        return jid

    def get(self, jid: str) -> dict | None:
        with self.lock:
            j = self.jobs.get(jid)
            return None if j is None else {k: v for k, v in j.items() if k != "key"}

    def _update(self, jid, **kw):
        with self.lock:
            j = self.jobs[jid]
            if j["status"] in ("done", "error") and ("status" not in kw or j.get("cancelled")):
                return  # (a late progress message from a worker process, or the end of a cancelled job)
            j.update(kw)
            self._save(force="status" in kw)

    def _files(self, jid: str) -> dict:
        """{"cancel": flag file, "state": make's state file} of a job (in a folder beside the jobs file)."""
        if self._dir is None:
            self._dir = self.path.with_suffix(".d") if self.path else Path(tempfile.mkdtemp(prefix="planet-jobs-"))
            self._dir.mkdir(parents=True, exist_ok=True)
        return {"cancel": str(self._dir / f"{jid}.cancel"), "state": str(self._dir / f"{jid}.state.json")}

    def cancel(self, jid: str) -> dict | None:
        """DELETE /api/jobs/<id>: a queued job never starts; a running one stops at its next progress
        report (the job shows as cancelled at once; its worker is free again when it has stopped).
        None: no such job; {"cancelled": False}: it had finished already."""
        with self.lock:
            j = self.jobs.get(jid)
            if j is None:
                return None
            if j["status"] in ("done", "error"):
                return {"id": jid, "status": j["status"], "cancelled": False}
            running = j["status"] == "running"
            j.update(status="error", error="cancelled", cancelled=True, message="cancelled", finished=time.time())
            self._save(force=True)
        if running and self.contexts:
            Path(self._files(jid)["cancel"]).touch()
        return {"id": jid, "status": "error", "cancelled": True}

    def run_one(self, jid: str, started: bool = False):
        req = self.jobs[jid]["request"]
        if not started:
            self._update(jid, status="running", message="starting", started=time.time())
        ctx = None
        if self.contexts:
            ctx = self._files(jid)
            Path(ctx["cancel"]).unlink(missing_ok=True)
            ctx["resume"] = bool(self.jobs[jid].get("resume"))
        try:
            res = self.fn({**req, "_job": ctx} if ctx else req,
                          lambda f, msg: self._update(jid, progress=round(float(f), 3), message=msg))
            # the result's keys ("zoom", "world" or "run") are copied to the job too
            self._update(jid, **res, status="done", progress=1.0, result=res, finished=time.time())
        except Cancelled:
            self._update(jid, status="error", error="cancelled", cancelled=True, finished=time.time())
        except (Exception, SystemExit) as e:  # zoom/slice raise SystemExit for bad input
            self._update(jid, status="error", error=str(e) or type(e).__name__, finished=time.time())
        finally:
            if ctx:
                Path(ctx["cancel"]).unlink(missing_ok=True)
                Path(ctx["state"]).unlink(missing_ok=True)  # (not reached when the process dies: that is what resumes)

    def _loop(self):
        while True:
            with self._take:  # (taken and marked running in one step, so jobs start in submission order)
                jid = self.q.get()
                if self.jobs[jid]["status"] != "queued":
                    continue  # (cancelled while it waited)
                self._update(jid, status="running", message="starting", started=time.time())
            self.run_one(jid, started=True)

    def wait(self, jid: str, timeout: float = 600) -> dict:
        t0 = time.time()
        while time.time() - t0 < timeout:
            j = self.get(jid)
            if j["status"] in ("done", "error"):
                return j
            time.sleep(0.05)
        raise TimeoutError(jid)
