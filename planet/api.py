"""What `planet serve` does beyond static files: regional zooms requested
from the viewer. Plain functions plus a one-job-at-a-time queue, so tests can
drive them without a socket.

  POST /api/zoom      {run, t} or {world}, plus {lat, lon, size_km, res_km}
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
                      (timezoom.py) from the run's keyframe nearest t; the
                      job's "run" is the new run's id when done. Shares the
                      job queue with zooms (one job at a time).
"""

from __future__ import annotations

import itertools
import json
import queue
import threading
import time
from pathlib import Path

from . import highlights as H
from . import store as S
from . import timeline as T
from . import world as W
from . import zoom as Z

ZOOM_PX = 500  # the viewer's zooms are 500 x 500 px whatever their size
_slicing = threading.Lock()  # the zoom worker and highlights requests may slice the same run at once


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
    if bool(req.get("run")) == bool(req.get("world")):
        raise BadRequest("give either run (+ t) or world")
    out = {"lat": _num(req, "lat"), "lon": _num(req, "lon"), "size_km": _num(req, "size_km", 1000)}
    out["res_km"] = _num(req, "res_km", out["size_km"] / 500)
    out["seed"] = int(_num(req, "seed", 1))
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
        if m.get("source_run") == run_dir.name and m.get("t_myr") is not None and abs(m["t_myr"] - at) < 1e-6:
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
    with _slicing:
        return _slice_run(run_ref, t, progress)


def _slice_run(run_ref: str, t: float, progress) -> Path:
    run_dir = S.find_run(run_ref)
    run = S.read_header(run_dir / "run.json")
    at = keyframe_t(run_dir, t)
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
    if "run" in r:
        world_path = slice_run(r["run"], r["t"], lambda f, msg: progress(0.5 * f, msg))
    else:
        world_path = S.find_world(r["world"])
    zid = Z.zoom_id(world_path.stem, r["lat"], r["lon"], r["size_km"], r["res_km"], r["seed"])
    if S.exists("zoom", zid):
        progress(1.0, f"zoom {zid} already exists")
        return {"zoom": zid, "world": world_path.stem}
    done = [0]

    def log(msg):  # build() logs four stages
        done[0] += 1
        progress(0.5 + 0.5 * min(done[0], 4) / 5, msg.strip())

    progress(0.5, "zooming in")
    out = Z.zoom(str(world_path), r["lat"], r["lon"], r["size_km"], r["res_km"], r["seed"], log=log)
    progress(1.0, "done")
    return {"zoom": out.name, "world": world_path.stem}


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


def highlights(req: dict, cached_only: bool = False, refresh: bool = False) -> dict:
    """GET /api/highlights. For a run, builds the world at that keyframe
    first if there isn't one (unless cached_only)."""
    src = parse_source(req)
    if "run" in src:
        run_dir = S.find_run(src["run"])
        at = keyframe_t(run_dir, src["t"])
        src["t"] = at
        world_path = find_slice(run_dir, at) if cached_only else slice_run(src["run"], at)
    else:
        world_path = S.find_world(src["world"])
    d = None
    if world_path is not None:
        d = H.cached(world_path) if cached_only else H.for_world(world_path, refresh)
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
    found = find_timezoom(run_id, r["t"], r["kyr"])
    if found:
        progress(1.0, f"time zoom {found} already exists")
        return {"run": found}
    progress(0.0, f"{r['kyr']:g} kyr of ice ages from {r['t']:g} Myr")
    out = TZ.timezoom(str(run_dir), r["t"], r["kyr"], progress=lambda f, msg: progress(0.98 * f, msg))
    progress(1.0, "done")
    return {"run": out.name}


def any_job(req: dict, progress=lambda f, msg: None) -> dict:
    """The server's job queue runs zooms and time zooms (req["type"])."""
    return (timezoom_job if req.get("type") == "timezoom" else zoom_job)(req, progress)


class Jobs:
    """Background jobs run one at a time, in submission order, on one worker
    thread. State is kept in memory only (lost on server restart)."""

    def __init__(self, fn=any_job):
        self.fn = fn
        self.jobs: dict[str, dict] = {}
        self.lock = threading.Lock()
        self.q: queue.Queue = queue.Queue()
        self.ids = itertools.count(1)
        self.worker = None

    def submit(self, req: dict) -> str:
        key = json.dumps(req, sort_keys=True)
        with self.lock:
            for j in self.jobs.values():  # the same request twice -> the same job
                if j["key"] == key and j["status"] in ("queued", "running"):
                    return j["id"]
            jid = f"{next(self.ids)}-{int(time.time()) % 100000}"
            self.jobs[jid] = {"id": jid, "key": key, "request": req, "status": "queued", "progress": 0.0,
                              "message": "waiting for the job before it", "created": time.time()}
            if self.worker is None or not self.worker.is_alive():
                self.worker = threading.Thread(target=self._loop, daemon=True)
                self.worker.start()
        self.q.put(jid)
        return jid

    def get(self, jid: str) -> dict | None:
        with self.lock:
            j = self.jobs.get(jid)
            return None if j is None else {k: v for k, v in j.items() if k != "key"}

    def _update(self, jid, **kw):
        with self.lock:
            self.jobs[jid].update(kw)

    def run_one(self, jid: str):
        req = self.jobs[jid]["request"]
        self._update(jid, status="running", message="starting", started=time.time())
        try:
            res = self.fn(req, lambda f, msg: self._update(jid, progress=round(float(f), 3), message=msg))
            # the result's keys ("zoom", "world" or "run") are copied to the job too
            self._update(jid, **res, status="done", progress=1.0, result=res, finished=time.time())
        except (Exception, SystemExit) as e:  # zoom/slice raise SystemExit for bad input
            self._update(jid, status="error", error=str(e) or type(e).__name__, finished=time.time())

    def _loop(self):
        while True:
            self.run_one(self.q.get())

    def wait(self, jid: str, timeout: float = 600) -> dict:
        t0 = time.time()
        while time.time() - t0 < timeout:
            j = self.get(jid)
            if j["status"] in ("done", "error"):
                return j
            time.sleep(0.05)
        raise TimeoutError(jid)
