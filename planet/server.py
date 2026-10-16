"""`planet serve`: the viewer's HTTP server.

  GET    /viewer/...                  the viewer (from the repository)
  GET    /runs/..., /worlds/..., /zooms/..., /grids/...
                                      outputs, from the data root (store.root())
  DELETE /runs/<id>, /worlds/<id>, /zooms/<id>
                                      delete one item (store.delete; a world
                                      takes its zooms and highlights with it)
  POST   /api/zoom, /api/timezoom, /api/finish
                                      start a job (api.py) -> {"job": id}
  GET    /api/jobs/<id>               a job's progress / result
  GET    /api/highlights?run=<id>&t=<Myr> or ?world=<id>   (api.highlights)

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

import http.server
import json
import re
import webbrowser
from urllib.parse import parse_qsl, urlsplit

from . import api
from . import parallel as P
from . import store as S

KIND_OF = {"runs": "run", "worlds": "world", "zooms": "zoom"}


def delete(path: str) -> int:
    """DELETE /<runs|worlds|zooms>/<id> -> HTTP status (204 done, 404 none, 400 bad path)."""
    m = re.fullmatch(r"/(runs|worlds|zooms)/([0-9a-zA-Z_-]+?)(?:\.json)?", path)
    if not m:
        return 400
    return 204 if S.delete(KIND_OF[m.group(1)], m.group(2)) else 404


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


def submit(jobs: api.Jobs, path: str, body: bytes) -> tuple[dict, int]:
    """POST /api/zoom, /api/timezoom or /api/finish: checks the request now
    (so a bad one fails at once), then queues it."""
    try:
        req = json.loads(body or b"{}")
        if path == "/api/zoom":
            api.parse_zoom_request(req)
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
        # the viewer comes from the repository, everything else from the data root
        top = urlsplit(path).path.lstrip("/").split("/", 1)[0]
        self.directory = str(S.REPO if top == "viewer" else S.root())
        return super().translate_path(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/api/highlights":
            return self.send_json(*highlights(url.query, self.hl_pool.call if self.hl_pool else None))
        m = re.fullmatch(r"/api/jobs/([0-9a-zA-Z_-]+)", url.path)
        if m:
            job = self.jobs.get(m.group(1))
            return self.send_json(job if job else {"error": "no such job"}, 200 if job else 404)
        return super().do_GET()

    def do_POST(self):
        if self.path not in ("/api/zoom", "/api/timezoom", "/api/finish"):
            return self.send_error(404)
        self.send_json(*submit(self.jobs, self.path, self.rfile.read(int(self.headers.get("Content-Length", 0)))))

    def do_DELETE(self):
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
    Handler.hl_pool = P.Pool(HIGHLIGHT_WORKERS, pool.threads)
    # job state survives a restart (per checkout and port: worktrees share the data folders)
    Handler.jobs = api.Jobs(pool.caller(api.any_job), S.REPO / ".jobs" / f"{port}.json", workers=jobs)
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    http.server.ThreadingHTTPServer.daemon_threads = True
    try:
        with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
            url = f"http://127.0.0.1:{port}/viewer/"
            print(f"Viewer at {url}   (data: {S.root()}; {jobs} jobs at once, {pool.threads} threads each; "
                  f"Ctrl-C to stop)", flush=True)
            if open_browser:
                webbrowser.open(url)
            httpd.serve_forever()
    finally:
        pool.close(kill=True)  # (running jobs are queued again at the next start)
        Handler.hl_pool.close(kill=True)
