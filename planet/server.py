"""`planet serve`: the viewer's HTTP server.

  GET    /viewer/...                  the viewer (from the repository)
  GET    /runs/..., /worlds/..., /zooms/..., /grids/...
                                      outputs, from the data root (store.root())
  DELETE /runs/<id>, /worlds/<id>, /zooms/<id>
                                      delete one item (store.delete; a world
                                      takes its zooms and highlights with it)
  POST   /api/zoom, /api/timezoom, /api/finish, /api/make, /api/highlight-zooms
                                      start a job (api.py; make.py: seed to finished world) -> {"job": id}
  GET    /api/presence?run=&frame=    one frame of a peoples run's presence table + demes_all (binary; the demes picker, PW-1269)
  DELETE /api/jobs/<id>               cancel a queued or running job (api.Jobs.cancel)
  GET    /api/planets                 runs, time zooms, worlds and zooms grouped by provenance (family.py)
  GET    /api/thumb?kind=run|world&id=<id>   a small PNG preview (thumbs.py; &proj=equal-earth|equirect &w=192|512|1024)
  GET    /api/make/options, /api/make/estimate?seed=&preset=&level=...   the New planet form (make.py)
  GET    /api/jobs/<id>               a job's progress / result
  GET    /api/highlights?run=<id>&t=<Myr> or ?world=<id>   (api.highlights)
  GET    /api/brief?run=<id>&people=<id>[&era=<kyr>] or &region=lat,lon[,km]   the culinary brief (brief())
  GET    /api/cultures?run=<id>      a peoples run's emergent cultures (cultures()): its cultures.json, else worked out on the fly, not saved
  POST   /api/names {world, letter, name}   rename a landmass (names.set_name; empty name clears)
  GET    /api/favourites[?kind=run|world|zoom]   the starred items [{kind, id, starred}] (favourites.py)
  POST   /api/favourites {kind, id, starred}   star or unstar one; answers the new list
  GET    /api/cell?world=<id>&i=<cell>  one world cell's 12 months (cell())

Big data files (.bin run layers, .json worlds and grids) go gzipped when the
browser accepts it (Content-Encoding: gzip), compressed once and cached under
<data root>/.gzcache (Handler.send_gzip).

Every POST must say `Content-Type: application/json`, and one that carries an
Origin must come from this server's own address (Handler.post_refused, PW-1037):
any other web page open in the browser can't start jobs. (A cross-site JSON POST
needs a preflight, which this server never answers.)

Files are never cached (runs get regenerated in place). Requests run on
threads (ThreadingHTTPServer), so a slow /api/highlights doesn't block file
serving. Zooms, time zooms and finished worlds run on the job queue, up to
--jobs at once, each in a worker process (parallel.Pool: separate processes
scale, threads in one process don't). Highlights that aren't cached yet are
computed in worker processes of their own (HIGHLIGHT_WORKERS at once, PW-261),
so they don't wait for the jobs or for each other. Job state is kept in
.jobs/<port>.json and survives a restart (api.Jobs).
"""

from __future__ import annotations

import gzip
import email.utils
import http.server
import json
import os
import re
import shutil
import threading
import webbrowser
import zlib
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from . import api, family, favourites, make, thumbs
from .zoom import fine as ZF
from . import parallel as P
from . import store as S

KIND_OF = {"runs": "run", "worlds": "world", "zooms": "zoom"}


def delete(path: str) -> int:
    """DELETE /<runs|worlds|zooms>/<id> -> HTTP status (204 done, 404 none, 400 bad path)."""
    m = re.fullmatch(r"/(runs|worlds|zooms)/([0-9a-zA-Z_-]+?)(?:\.json)?", path)
    if not m:
        return 400
    gone = S.delete(KIND_OF[m.group(1)], m.group(2))
    for p in (S.root() / thumbs.CACHE).glob(f"{KIND_OF[m.group(1)]}-{m.group(2)}-*.png"):
        p.unlink(missing_ok=True)
    return 204 if gone else 404


def make_query(query: str) -> dict:
    """GET /api/make/estimate's query string as a make request (?seed=&preset=&level=&myr=&kyr=&timezoom=1&zooms=4...)."""
    q = dict(parse_qsl(query))
    req = {k: q[k] for k in ("seed", "preset", "level", "myr", "kyr", "zooms", "now", "tries") if q.get(k) not in (None, "")}
    for k in ("timezoom", "finish", "highlights", "require_ice"):
        if k in q:
            req[k] = q[k] not in ("0", "false", "")
    return req


def make_estimate(query: str) -> tuple[dict, int]:
    try:
        spec = make.parse_make_request(make_query(query))
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    return {"spec": spec, **make.estimate(spec)}, 200


def highlights(query: str, compute=None) -> tuple[dict, int]:
    """GET /api/highlights?...: (JSON body, status). Synchronous: a few
    seconds at L6 (building a world from a keyframe), longer at L7/L8.
    compute: where what isn't cached is computed (api.highlights)."""
    q = dict(parse_qsl(query))
    try:
        return api.highlights(q, cached_only=q.get("cached") == "1", refresh=q.get("refresh") == "1",
                              compute=compute), 200
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:  # no such run / world
        return {"error": str(e)}, 404
    except Exception as e:  # a bug: show it in the viewer rather than drop the connection
        return {"error": f"{type(e).__name__}: {e}"}, 500


def rename_landmass(raw: bytes) -> tuple[dict, int]:
    """POST /api/names {world, letter, name}: your own name for a landmass of a world (an empty name: back to the generated one), kept in
    worlds/names/<id>.json like `planet name`. Answers {names: [{letter, name, generated, custom}]} (PW-886)."""
    from . import names as NM
    try:
        b = json.loads(raw or b"{}")
        return {"names": NM.set_name(str(b.get("world") or ""), str(b.get("letter") or ""), str(b.get("name") or ""))}, 200
    except (ValueError, TypeError) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404


def presence_frame(query: str) -> tuple[bytes | dict, int]:
    """GET /api/presence?run=<id>&frame=<f>: one frame of the run's presence table and demes_all (PW-1269), so the viewer's
    "whose demes" picker downloads that frame's slice instead of the whole table. The body is binary: (lines + 1) uint32 offsets
    of each line's entries within the slice, then the cell ids (meta.presence.dtypes.cells), then the demes (uint16, if the
    run has demes_all). The entry count is the last offset."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import output as LO
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        meta = (json.loads((d / "run.json").read_text()).get("meta") or {})
        cells, dem, offs = LO.read_presence_frame(d, meta, int(q.get("frame", "")))
        return offs.astype("<u4").tobytes() + cells.tobytes() + dem.tobytes(), 200
    except (ValueError, IndexError) as e:
        return {"error": str(e)}, 400
    except KeyError as e:
        return {"error": e.args[0]}, 404
    except SystemExit as e:
        return {"error": str(e)}, 404


def favourites_list(query: str) -> tuple[dict, int]:
    """GET /api/favourites[?kind=]: the starred runs, worlds and zooms that still exist, oldest star first."""
    kind = dict(parse_qsl(query)).get("kind") or None
    if kind and kind not in S.KINDS:
        return {"error": f"unknown kind {kind!r}; one of {list(S.KINDS)}"}, 400
    return {"favourites": favourites.listing(kind)}, 200


def favourites_set(raw: bytes) -> tuple[dict, int]:
    """POST /api/favourites {kind, id, starred}: star (default) or unstar one item (an id may carry .json)."""
    try:
        b = json.loads(raw or b"{}")
        item_id = str(b.get("id") or "").removesuffix(".json")
        return {"favourites": favourites.set_favourite(str(b.get("kind") or ""), item_id, bool(b.get("starred", True)))}, 200
    except (ValueError, TypeError, AttributeError) as e:
        return {"error": str(e)}, 400
    except KeyError as e:
        return {"error": e.args[0]}, 404


def landmass_names(query: str) -> tuple[dict, int]:
    """GET /api/names?world=<id>: [{letter, name, generated, custom}] of a world's landmasses, as the viewer's labels and peoples runs show them."""
    from . import names as NM
    try:
        wid, _h, lms, gen = NM.world_landmasses(dict(parse_qsl(query)).get("world", ""))
        ov = NM.load_overrides(wid)
        return {"names": [{"letter": NM.rank_letter(i), "name": ov.get(NM.rank_letter(i), g), "generated": g, "custom": NM.rank_letter(i) in ov}
                          for i, g in enumerate(gen)]}, 200
    except SystemExit as e:
        return {"error": str(e)}, 404


def brief(query: str) -> tuple[dict, int]:
    """GET /api/brief?run=<run>&people=<id>[&era=<kyr ago>] or &region=lat,lon[,radius_km]: the culinary brief
    (lineages/brief.py, PW-728) as {markdown, brief} (PW-837: the viewer's Peoples panel shows it)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import brief as BR
        run, era = q.get("run"), float(q.get("era") or 0.0)
        if not run:
            raise ValueError("run= is required")
        region = None
        if q.get("region"):
            v = [float(x) for x in q["region"].split(",")]
            if len(v) not in (2, 3):
                raise ValueError("region=lat,lon[,radius_km]")
            region = (v[0], v[1], v[2] if len(v) == 3 else BR.DEFAULT_RADIUS_KM)
        elif not q.get("people"):
            raise ValueError("give people=<id> or region=lat,lon[,radius_km]")
        b = BR.build(run, region=region, people=q.get("people"), era_kyr=era)
        return {"markdown": BR.markdown(b), "brief": b}, 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:  # no such run / people
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


_cultures_cache: dict = {}  # (run id, run.json mtime) -> cultures doc: a run without cultures.json, worked out once per change


def cultures(query: str) -> tuple[dict, int]:
    """GET /api/cultures?run=<id>: the emergent cultures of a peoples run (lineages/cultures.py, PW-670) for the workbench's Cultures
    tab: the run's cultures.json if it has one, else derived from its demes (a few seconds) and kept in memory, never written into the run."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import cultures as CU
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        f = d / "cultures.json"
        if f.exists():
            return json.loads(f.read_text()), 200
        run = json.loads((d / "run.json").read_text())
        if not (run.get("meta") or {}).get("demes"):
            return {"error": "this run has no demes (older than PW-981): run the peoples again"}, 404
        key = (d.name, (d / "run.json").stat().st_mtime)
        if key not in _cultures_cache:
            _cultures_cache.clear()
            _cultures_cache[key] = CU.derive(d)["doc"]
        return _cultures_cache[key], 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


# ---------------------------------------------------------------- /api/cell
CELL_INPUTS = ("temperature", "warm_month", "cold_month", "precipitation_jul", "precipitation_jan",
               "cloud_jul", "cloud_jan")  # what climate.months needs from a world
CELL_WORLDS = 4  # worlds kept loaded (their CELL_INPUTS only: ~9 MB each at L7)
_cell_lock = threading.Lock()
_cell_worlds: dict = {}  # world id -> (file mtime, lat, tilt, {layer: array}), oldest first
_grid_lat: dict = {}  # level -> cell latitudes


def world_columns(path: Path, keys) -> dict:
    """{layer: array} for some of a saved world's layers, parsing only their
    lines (world.save writes one line per layer); the whole file if the
    lines aren't there (a world edited by hand)."""
    import numpy as np
    keys, out = set(keys), {}
    with open(path) as fh:
        for line in fh:
            m = re.match(r'  "(\w+)": ', line)
            if m and m.group(1) in keys:
                out[m.group(1)] = np.array(json.loads(line[m.end():].rstrip().rstrip(",")), float)
                if len(out) == len(keys):
                    return out
    layers = json.loads(path.read_text())["layers"]
    return {k: np.array(layers[k], float) for k in keys}


def cell(query: str) -> tuple[dict, int]:
    """GET /api/cell?world=<id>&i=<cell>: (JSON body, status). The cell's
    twelve months, Jan..Dec, from climate.months (PW-194) on the world's
    stored climate: t (C) and p (mm in the month). Only the one cell is
    computed; the world's inputs stay loaded for the next cell (~1 s to read
    an L7 world and its grid the first time, ~1 ms after)."""
    from . import climate
    from .grid import build_grid
    q = dict(parse_qsl(query))
    wid = q.get("world", "").removesuffix(".json")
    if not S.exists("world", wid):
        return {"error": f"no world {wid!r}"}, 404
    try:
        i = int(q.get("i", ""))
    except ValueError:
        return {"error": "i: a cell index"}, 400
    path = S.path_of("world", wid)
    mtime = path.stat().st_mtime_ns
    with _cell_lock:
        w = _cell_worlds.pop(wid, None)
        if w is None or w[0] != mtime:  # (a world rebuilt in place is read again)
            meta = S.read_header(path, ("meta",))["meta"]
            if meta["level"] not in _grid_lat:
                _grid_lat[meta["level"]] = build_grid(meta["level"]).lat
            w = (mtime, _grid_lat[meta["level"]], meta.get("params", {}).get("tilt", 23.4),
                 world_columns(path, CELL_INPUTS))
        _cell_worlds[wid] = w  # (now the newest)
        while len(_cell_worlds) > CELL_WORLDS:
            del _cell_worlds[next(iter(_cell_worlds))]
    _, lat, tilt, L = w
    if not 0 <= i < len(lat):
        return {"error": f"i: 0..{len(lat) - 1}"}, 400
    c = {k: v[i:i + 1] for k, v in L.items()}
    mo = climate.months(lat[i:i + 1], c["temperature"], c["warm_month"], c["cold_month"], c["precipitation_jul"],
                        c["precipitation_jan"], tilt, c["cloud_jul"] / 100, c["cloud_jan"] / 100)
    return {"world": wid, "i": i, "lat": round(float(lat[i]), 3),
            "t": [round(float(x), 2) for x in mo["t"][:, 0]], "p": [round(float(x), 2) for x in mo["p"][:, 0]]}, 200


# ---------------------------------------------------------------- gzip
GZIP_SUFFIXES = (".bin", ".json")  # run layers, worlds, grids, run.json
GZIP_MIN = 256 << 10  # smaller files go as they are
# level 1: an L7 run's default layers 330 -> ~87 MB, ~1.4 s for the biggest
# file (level 6: ~3% smaller, twice the time). An int16 elevation barely
# shrinks (78 -> 67 MB); the int8 and mostly-zero layers 5-50x.
GZIP_LEVEL = 1
GZIP_DIR = ".gzcache"


def gz_path(src: Path, st: os.stat_result) -> Path:
    """Where src's gzipped copy is cached: <data root>/.gzcache/<its path
    there>.<size>-<mtime>.gz (a file rewritten in place gets a new name)."""
    rel = os.path.relpath(src, S.root())
    return S.root() / GZIP_DIR / f"{rel}.{st.st_size}-{st.st_mtime_ns}.gz"


def prune_gz() -> None:
    """Drop cached copies whose file is gone or has changed (deleted runs and
    worlds, regenerated layers)."""
    top = S.root() / GZIP_DIR
    for p in top.rglob("*.gz"):
        src = S.root() / p.relative_to(top).parent / p.name.rsplit(".", 2)[0]
        try:
            ok = gz_path(src, src.stat()) == p
        except OSError:
            ok = False
        if not ok:
            p.unlink(missing_ok=True)


def etag(st: os.stat_result, gz: bool = False) -> str:
    """A data file's validator: its size and modification time (PW-1045). The gzipped answer is a
    different body, so it gets its own tag."""
    return f'"{st.st_size:x}-{st.st_mtime_ns:x}{"-gz" if gz else ""}"'


def etag_matches(header: str | None, tag: str) -> bool:
    """If-None-Match names tag (or *); weak tags (W/"...") count, as for a GET they should."""
    if not header:
        return False
    tags = [t.strip().removeprefix("W/") for t in header.split(",")]
    return "*" in tags or tag in tags


def accepts_gzip(header: str | None) -> bool:
    """Accept-Encoding names gzip (and not with q=0)."""
    for a in (header or "").split(","):
        name, *params = [x.strip() for x in a.split(";")]
        if name == "gzip":
            return not any(x.replace(" ", "") in ("q=0", "q=0.0", "q=0.00", "q=0.000") for x in params)
    return False


def submit(jobs: api.Jobs, path: str, body: bytes) -> tuple[dict, int]:
    """POST /api/zoom, /api/timezoom or /api/finish: checks the request now
    (so a bad one fails at once), then queues it."""
    try:
        req = json.loads(body or b"{}")
        if path == "/api/make":
            req = make.parse_make_request(req)
        elif path == "/api/zoom":
            api.parse_zoom_request(req)
        elif path == "/api/highlight-zooms":
            req = api.parse_highlight_zooms_request(req)
        elif path == "/api/enrich":  # resource / coast layers added to a saved world
            req = api.parse_enrich_request(req)
        elif path == "/api/finish":  # kyr snaps to a frame, t to a keyframe
            req = api.parse_finish_request(req)
        else:  # t snaps to a keyframe
            req = api.parse_timezoom_request(req)
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:  # no such run
        return {"error": str(e)}, 404
    return {"job": jobs.submit(req)}, 200


class Handler(http.server.SimpleHTTPRequestHandler):
    jobs: api.Jobs | None = None  # set by serve()
    hl_pool: P.Pool | None = None  # (highlights' worker processes, set by serve())

    def translate_path(self, path):
        # the viewer (and the review pages it links to, docs/review/, PW-967) comes from the repository, everything else from the data root
        parts = urlsplit(path).path.lstrip("/").split("/", 2)
        self.directory = str(S.REPO if parts[0] == "viewer" or parts[:2] == ["docs", "review"] else S.root())
        return super().translate_path(path)

    # Caching (PW-1045): the viewer's own files and every API answer are no-store (a code change shows on reload);
    # data files (runs, worlds, zooms, grids: up to ~100 MB a run) are no-cache with an ETag, so the browser keeps
    # its copy and asks again, and an unchanged file costs a 304 instead of a download.
    data_etag: str | None = None

    def end_headers(self):
        if self.data_etag:
            self.send_header("Cache-Control", "no-cache")
            self.send_header("ETag", self.data_etag)
            self.send_header("Vary", "Accept-Encoding")
            self.data_etag = None
        else:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def data_file(self) -> Path | None:
        """The data file this GET names (not the viewer, the review pages or the API), when it exists."""
        parts = urlsplit(self.path).path.lstrip("/").split("/")
        if parts[0] in ("viewer", "api") or parts[:2] == ["docs", "review"]:
            return None
        p = Path(self.translate_path(self.path))
        try:
            return p if p.is_file() else None
        except OSError:
            return None

    def not_modified(self, tag: str, mtime: float) -> bool:
        """Answer 304 when the browser's copy is this one: If-None-Match names the tag, or (with no If-None-Match)
        If-Modified-Since is not older than the file. This server speaks HTTP/1.0, and to a 1.0 server Chrome
        revalidates by date only, so both are needed."""
        inm, ims = self.headers.get("If-None-Match"), self.headers.get("If-Modified-Since")
        if inm is not None:
            fresh = etag_matches(inm, tag)
        else:
            try:
                fresh = ims is not None and int(mtime) <= email.utils.parsedate_to_datetime(ims).timestamp()
            except (TypeError, ValueError, IndexError, OverflowError):
                fresh = False
        if not fresh:
            return False
        self.send_response(304)
        self.data_etag = tag
        self.end_headers()
        return True

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_gzip(self, src: Path) -> None:
        """src gzipped: the cached copy, or compressed while it is sent (no
        Content-Length then: HTTP/1.0 closes the connection at the end) and
        cached for next time."""
        cache = gz_path(src, src.stat())
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(str(src)))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Last-Modified", self.date_time_string(src.stat().st_mtime))
        if cache.exists():
            self.send_header("Content-Length", str(cache.stat().st_size))
            self.end_headers()
            with open(cache, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return
        self.end_headers()
        cache.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache.with_name(f".{cache.name}.{threading.get_ident()}.tmp")
        try:
            with open(src, "rb") as f, open(tmp, "wb") as out:
                z = zlib.compressobj(GZIP_LEVEL, zlib.DEFLATED, 31)  # (31: with the gzip wrapper)
                while True:
                    chunk = f.read(1 << 20)
                    b = z.compress(chunk) if chunk else z.flush()
                    out.write(b)
                    self.wfile.write(b)
                    if not chunk:
                        break
            os.replace(tmp, cache)
        finally:
            tmp.unlink(missing_ok=True)
        prune_gz()

    def gzippable(self) -> Path | None:
        """The data file this GET asks for, when it should go gzipped."""
        top = urlsplit(self.path).path.lstrip("/").split("/", 1)[0]
        if top == "viewer" or not accepts_gzip(self.headers.get("Accept-Encoding")):
            return None
        p = Path(self.translate_path(self.path))
        try:
            ok = p.suffix in GZIP_SUFFIXES and p.is_file() and p.stat().st_size >= GZIP_MIN
        except OSError:
            ok = False
        return p if ok else None

    def do_GET(self):
        url = urlsplit(self.path)
        if self.lineages_api("GET"):
            return
        if url.path == "/api/highlights":
            return self.send_json(*highlights(url.query, self.hl_pool.call if self.hl_pool else None))
        if url.path == "/api/brief":
            return self.send_json(*brief(url.query))
        if url.path == "/api/presence":
            body, code = presence_frame(url.query)
            if isinstance(body, dict):
                return self.send_json(body, code)
            self.send_response(code)
            self.send_header("Content-Type", "application/octet-stream")
            if accepts_gzip(self.headers.get("Accept-Encoding")):  # (cell ids ascend, so it gzips ~3.4x at L7)
                body = gzip.compress(body, 1)
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if url.path == "/api/cultures":
            return self.send_json(*cultures(url.query))
        if url.path == "/api/names":
            return self.send_json(*landmass_names(url.query))
        if url.path == "/api/favourites":
            return self.send_json(*favourites_list(url.query))
        if url.path == "/api/cell":
            return self.send_json(*cell(url.query))
        if url.path == "/api/fine-rules":  # what a fine zoom may be (zoom.fine): the viewer's size menu
            q = dict(parse_qsl(url.query))
            try:
                res = float(q["res_km"]) if "res_km" in q else None
            except ValueError:
                return self.send_json({"error": "res_km must be a number"}, 400)
            return self.send_json({**ZF.rules(), **({"sizes": ZF.size_options(res)} if res else {})})
        if url.path == "/api/planets":
            return self.send_json({"planets": family.planets()})
        if url.path == "/api/make/options":
            return self.send_json(make.options())
        if url.path == "/api/make/estimate":
            return self.send_json(*make_estimate(url.query))
        if url.path == "/api/thumb":
            q = dict(parse_qsl(url.query))
            w = q.get("w", "")
            png = thumbs.thumb(q.get("kind", ""), q.get("id", ""), q.get("proj", "equal-earth"), int(w) if w.isdigit() else thumbs.W)
            if png is None:
                return self.send_error(404)
            body = png.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        gz = self.gzippable()
        if gz:
            st = gz.stat()
            tag = etag(st, gz=True)
            if self.not_modified(tag, st.st_mtime):
                return
            self.data_etag = tag
            return self.send_gzip(gz)
        m = re.fullmatch(r"/api/jobs/([0-9a-zA-Z_-]+)", url.path)
        if m:
            job = self.jobs.get(m.group(1))
            return self.send_json(job if job else {"error": "no such job"}, 200 if job else 404)
        f = self.data_file()
        if f:
            st = f.stat()
            tag = etag(st)
            if self.not_modified(tag, st.st_mtime):
                return
            self.data_etag = tag
        return super().do_GET()

    def lineages_api(self, method: str) -> bool:
        """The peoples editor (viewer/lineages.html, planet/lineages/): GET /api/lineage-schema (its option lists,
        lineages.run.editor_schema), GET /api/lineage-trees, GET or POST
        /api/lineage-tree?name=N (the tree as JSON; POST validates and saves it), POST /api/lineages
        {world | timezoom, tree | raw, tries} (queued on the job queue like a time zoom, ~20 s a try at L6;
        answers {job}; GET /api/jobs/<id> has its progress, and {run} when done)."""
        url = urlsplit(self.path)
        if not url.path.startswith("/api/lineage"):
            return False
        from .lineages import run as LR
        q = dict(parse_qsl(url.query))
        try:
            if method == "GET" and url.path == "/api/lineage-schema":
                self.send_json(LR.editor_schema())
            elif method == "GET" and url.path == "/api/lineage-trees":
                self.send_json({"trees": [{k: v for k, v in t.items() if k != "file"} for t in LR.list_trees()]})
            elif method == "GET" and url.path == "/api/lineage-tree":
                self.send_json(LR.read_raw(q.get("name", "")))
            elif method == "POST" and url.path in ("/api/lineage-tree", "/api/lineages"):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                if url.path == "/api/lineage-tree":
                    LR.save_raw(q.get("name", ""), body)
                    self.send_json({"saved": q.get("name")})
                else:
                    try:
                        req = api.parse_lineages_request(body)
                    except api.BadRequest as e:
                        return self.send_json({"error": str(e)}, 400) or True
                    self.send_json({"job": self.jobs.submit(req)})
            else:
                self.send_error(404)
        except (ValueError, KeyError) as e:
            self.send_json({"error": str(e)}, 400)
        except (FileNotFoundError, SystemExit) as e:
            self.send_json({"error": str(e)}, 404)
        return True

    def post_refused(self) -> str | None:
        """Why this POST is refused, or None (PW-1037): it must be JSON, and an Origin, if sent,
        must be this server's own address (http://127.0.0.1:<port> or http://localhost:<port>)."""
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return "POST needs Content-Type: application/json"
        origin = self.headers.get("Origin")
        if origin is not None:
            port = self.server.server_address[1]
            if origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"):
                return f"cross-site POST refused (Origin {origin})"
        return None

    def do_POST(self):
        refused = self.post_refused()
        if refused:
            return self.send_json({"error": refused}, 403)
        if self.lineages_api("POST"):
            return
        if self.path == "/api/favourites":
            return self.send_json(*favourites_set(self.rfile.read(int(self.headers.get("Content-Length", 0)))))
        if self.path == "/api/names":
            return self.send_json(*rename_landmass(self.rfile.read(int(self.headers.get("Content-Length", 0)))))
        if self.path not in ("/api/zoom", "/api/timezoom", "/api/finish", "/api/make", "/api/highlight-zooms",
                         "/api/enrich"):
            return self.send_error(404)
        self.send_json(*submit(self.jobs, self.path, self.rfile.read(int(self.headers.get("Content-Length", 0)))))

    def do_DELETE(self):
        m = re.fullmatch(r"/api/jobs/([0-9a-zA-Z_-]+)", urlsplit(self.path).path)
        if m:  # cancel a job
            out = self.jobs.cancel(m.group(1))
            return self.send_json(out if out else {"error": "no such job"}, 200 if out else 404)
        code = delete(self.path)
        if code == 400:
            return self.send_error(400, "expected /runs/<id>, /worlds/<id> or /zooms/<id>")
        self.send_response(code)
        self.end_headers()

    def log_message(self, *a):
        pass


JOBS = 4  # jobs at once (worker processes) by default
HIGHLIGHT_WORKERS = 2  # highlights computed at once (worker processes, started when first needed)


def serve(port: int = 8765, open_browser: bool = True, jobs: int = JOBS, threads: int | None = None):
    """jobs: how many jobs run at once, each in a worker process with
    `threads` numba threads (default: the cores shared out, at most 8)."""
    for kind in S.KINDS:
        S.update_index(kind)
    pool = P.Pool(jobs, threads)
    try:
        Handler.hl_pool = P.Pool(HIGHLIGHT_WORKERS, pool.threads)
        # job state survives a restart (per checkout and port: worktrees share the data folders)
        Handler.jobs = api.Jobs(pool.caller(api.any_job), S.REPO / ".jobs" / f"{port}.json", workers=jobs,
                                contexts=True)
        http.server.ThreadingHTTPServer.allow_reuse_address = True
        http.server.ThreadingHTTPServer.daemon_threads = True
        with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
            url = f"http://127.0.0.1:{port}/viewer/"
            print(f"Viewer at {url}   (data: {S.root()}; {jobs} jobs at once, {pool.threads} threads each; "
                  f"Ctrl-C to stop)", flush=True)
            if open_browser:
                webbrowser.open(url)
            httpd.serve_forever()
    finally:
        try:
            pool.close(kill=True)  # (running jobs are queued again at the next start)
        finally:
            if Handler.hl_pool:
                Handler.hl_pool.close(kill=True)
