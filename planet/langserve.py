"""`planet langserve <run>`: the languages viewer on its own, beside (never instead of) `planet serve`.

  GET  /                              -> /viewer/languages.html?run=<run>
  GET  /viewer/<file>                 the languages page and the scripts it loads (LANG_FILES), from the repository
  GET  /runs/index.json               just this run
  GET  /runs/<run>/run.json, demes.json   the run's own files, read from the data root (never written)
  GET  /runs/<run>/languages.json     the --languages file (default: the run's own), gzipped when the browser takes it
  GET  /api/speak, /api/speak/backends   words and whole sentences said aloud (server.speak, server.speak_backends)
  GET  /api/thumb                     the map tab's backdrop (server's thumbs.thumb)

It starts no job queue, no worker pools and writes nothing (no .jobs/ file), so it can run on another port while
the main viewer runs on 8765, and it can show a languages.json written anywhere (`planet languages --out ...`).
--host 0.0.0.0 makes it reachable from other machines on the network (a phone, a remote desktop): read-only, but
anyone who can reach the port can hear the speech backend, so only on a network you trust.
"""

from __future__ import annotations

import gzip
import http.server
import json
import threading
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from . import store as S

# the languages page's own files (viewer/languages.html and what it loads); nothing else under viewer/ is served
LANG_FILES = {"languages.html", "langcore.js", "langview.js", "langtime.js", "langmap.js", "langmore.js", "langgram.js",
              "numfmt.js", "theme.css"}
RUN_FILES = {"run.json", "demes.json"}
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".json": "application/json"}


class LangHandler(http.server.BaseHTTPRequestHandler):
    run: str = ""
    languages: Path | None = None  # the languages.json shown
    _gz: tuple | None = None       # (mtime_ns, size, gzipped bytes) of `languages`
    _gz_lock = threading.Lock()

    def log_message(self, *a):
        pass

    def send(self, body: bytes, ctype: str, code: int = 200, gz: bool = False) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, obj, code: int = 200) -> None:
        self.send(json.dumps(obj).encode(), "application/json", code)

    def languages_gz(self) -> bytes:
        """The languages file gzipped, once per version of the file (kept in memory; ~1/8 of the file)."""
        st = self.languages.stat()
        with self._gz_lock:
            if LangHandler._gz is None or LangHandler._gz[:2] != (st.st_mtime_ns, st.st_size):
                LangHandler._gz = (st.st_mtime_ns, st.st_size, gzip.compress(self.languages.read_bytes(), 6))
            return LangHandler._gz[2]

    def do_GET(self):  # noqa: N802
        from . import server as SV
        url = urlsplit(self.path)
        parts = url.path.lstrip("/").split("/")
        if url.path in ("/", "/viewer", "/viewer/"):
            self.send_response(302)
            self.send_header("Location", f"/viewer/languages.html?run={self.run}")
            self.end_headers()
            return
        if url.path == "/api/speak/backends":
            return self.send_json(*SV.speak_backends())
        if url.path == "/api/speak":
            body, code = SV.speak(url.query)
            return self.send_json(body, code) if isinstance(body, dict) else self.send(body, "audio/wav", code)
        if url.path == "/api/thumb":
            from . import thumbs
            q = dict(parse_qsl(url.query))
            w = q.get("w", "")
            png = thumbs.thumb(q.get("kind", ""), q.get("id", ""), q.get("proj", "equal-earth"),
                               int(w) if w.isdigit() else thumbs.W)
            return self.send(png.read_bytes(), "image/png") if png else self.send_error(404)
        if len(parts) == 2 and parts[0] == "viewer" and parts[1] in LANG_FILES:
            p = S.REPO / "viewer" / parts[1]
            return self.send(p.read_bytes(), TYPES.get(p.suffix, "application/octet-stream"))
        if parts == ["runs", "index.json"]:
            return self.send_json([{"dir": self.run, "kind": "peoples", "name": "languages"}])
        if len(parts) == 3 and parts[0] == "runs" and parts[1] == self.run:
            if parts[2].endswith(".json") and parts[2].startswith("languages"):
                if "gzip" in (self.headers.get("Accept-Encoding") or ""):
                    return self.send(self.languages_gz(), "application/json", gz=True)
                return self.send(self.languages.read_bytes(), "application/json")
            if parts[2] in RUN_FILES:
                p = S.root() / "runs" / self.run / parts[2]
                if p.is_file():
                    return self.send(p.read_bytes(), "application/json")
        self.send_error(404)


def serve(run: str, languages: str | None = None, port: int = 8790, host: str = "127.0.0.1",
          open_browser: bool = False) -> None:
    """Serve the languages viewer for `run`, showing `languages` (default <data root>/runs/<run>/languages.json)."""
    lj = Path(languages).resolve() if languages else S.root() / "runs" / run / "languages.json"
    if not lj.is_file():
        raise SystemExit(f"no languages file at {lj} (run `planet languages {run}`, or pass --languages)")
    if not (S.root() / "runs" / run / "run.json").is_file():
        print(f"(note: {S.root() / 'runs' / run / 'run.json'} is missing: the page shows lects without people names)")
    LangHandler.run, LangHandler.languages = run, lj
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    http.server.ThreadingHTTPServer.daemon_threads = True
    with http.server.ThreadingHTTPServer((host, port), LangHandler) as httpd:
        shown = "127.0.0.1" if host in ("127.0.0.1", "localhost") else host
        url = f"http://{shown}:{port}/viewer/languages.html?run={run}"
        print(f"Languages viewer at {url}   (languages: {lj}; Ctrl-C to stop)", flush=True)
        if host == "0.0.0.0":
            print("  reachable from other machines: use this machine's address instead of 0.0.0.0", flush=True)
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        httpd.serve_forever()

