"""The level-of-detail tile service (PW-1690; docs/review/zoom/lod-plan-v2.md section 3, step 2): the globe asks for the
tiles on screen and the server builds them, on demand, and keeps them.

    GET  /api/tiles/index?world=<id>
        {world, ladder: lod.describe(), cap_gb, cells: [{id, lat, lon, up, outline: [[x, y] km in the cell's plane],
         built: {"1": [[0, 0]], "2": [[tx, ty], ...], ...}}]}   all 54 cells; every tile lod.exists can be asked for
    POST /api/tiles/want {world, gen, tiles: [[cell, level, tx, ty] | "cell/level/tx/ty", ...]}
        the tiles the view needs and lacks, most wanted first. The list REPLACES the world's queue: what is no longer
        wanted is dropped (a build already running is not stopped: it finishes and is kept). The missing tiles a build
        reads (lod.parent_sources, down to the level-1 section) go in ahead of it; the queue is ordered coarser level
        first, then the viewer's order (nearest the screen's centre first). Answers as status.
    GET  /api/tiles/status?world=<id>
        {world, gen, queued, building, waiting, tiles: {key: {state: built|queued|building|failed|blocked, pos, progress,
         error}}, note, cache_gb, cap_gb}: per wanted tile and per tile queued for them
    GET  /api/tiles/<world>/<cell>/<level>/<tx>/<ty>/view.bin
        b"PWT1", int32 n, then n*n float16 ground elevation (m, row-major from the north-west, lod.lattice order), then
        n*n uint8 water (0 land, 1 sea, 2 lake); written into the tile's directory when it is built
    GET  .../satellite.png               the tile's satellite view
    GET  .../layer/<name>.bin            one zoom layer as n*n float32 (decoded units)

Builds run as server jobs (api.Jobs, each in a worker process), never in a request thread:
  - level 1 is the cell's section at 4 km, a lod_build.tile job too: built matched to the neighbouring cells' level 1
    already built (lod_build.build_level1, PW-1699), one at a time and not beside another section-sized zoom; budget
    PEAK_GB[1] = 8.3 GB (lane 290 measured; matched 8.3-8.4 GB, lane 295);
  - levels 2-4 are lod_build.tile jobs, AT_ONCE (3) at a time, PEAK_GB 3.2 GB each (lane 290: 2.9-3.2 GB);
  - at most AT_ONCE tile jobs in all (the server has 4 job workers: one is left for everything else);
  - the RAM guard: a build starts only while free memory covers its peak, api.ZOOM_RAM_SPARE_GB and the peaks of the
    tile builds already started (counted again although they show in the free memory: on the safe side).
The disk cache: tiles are zoom directories (zoom.load and the zoom page's files work on them) in the world's own tile
store, <data root>/.tiles/<world>/zooms/ (store.tile_store; lod.tile_id; level 1: the cell's matched section), never in
zooms/: they are not in zooms/index.json, so not in the viewer's zoom lists, the navigator or `planet list`, and saving one
rescans nothing. An index per world at <data root>/.tiles/<world>.json (bytes, built, last used) is how a tile is found
(levels 2-4 also by their deterministic id). The globe uses only level-1 sections built here, matched to their built
neighbours; a section made by POST /api/zoom is an ordinary zoom and the globe never sees it (lod-plan-v2.md, State lane 298). Past the cap (CAP_GB, $PLANET_TILE_CACHE_GB,
default 60) the least recently used tiles of levels 2-4 are deleted (a tile counts as used when any finer tile under it
was: children go before their parents); level 1 is never dropped, nor a tile a queued or running build reads.
"""
from __future__ import annotations

import json
import os
import shutil
import struct
import threading
import time
from pathlib import Path

import numpy as np

from . import api
from . import store as S
from .zoom import lod as L

SEED = 1  # (lod_build's: every tile of a world is built with seed 1)
PEAK_GB = api.TILE_PEAK_GB  # budget per build by level (the job checks the same numbers; lod-plan-v2.md, State lanes 290, 295)
AT_ONCE = 3  # tile builds at once (level 1 among them, at most one of those)
CAP_GB = 60.0  # the disk cache's default cap
EVICT_TO = 0.95  # a sweep frees down to this share of the cap (so not every build sweeps)
FAIL_RETRY_S = 300.0  # a failed tile is not tried again for this long
ROOM_RETRY_S = 30.0  # (a build refused for memory in its worker: sooner)
MAX_WANT = 512  # tiles per want list
FLUSH_S = 5.0  # last-used times are written at most this often


class NotFound(Exception):
    pass


def _key(k) -> L.Key:
    if isinstance(k, L.Key):
        return k
    if isinstance(k, str):
        return L.Key.parse(k)
    cell, level, tx, ty = k
    return L.Key(str(cell), int(level), int(tx), int(ty))


def _dir_bytes(d: Path) -> int:
    return sum(f.stat().st_size for f in d.rglob("*") if f.is_file())


def write_view(d: Path) -> Path:
    """The tile's view.bin (module doc) from its zoom directory's elevation and water layers."""
    m = json.loads((d / "zoom.json").read_text())
    e = _layer(d, m, "elevation")
    w = np.asarray(_raw(d, m, "water")).astype(np.uint8)
    n = e.shape[0]
    body = b"PWT1" + struct.pack("<i", n) + e.astype("<f2").tobytes() + w.tobytes()
    return S.write_atomic(d / "view.bin", body)


def _raw(d: Path, m: dict, name: str):
    spec = m["layers"].get(name)
    if spec is None or spec.get("transform") not in (None, "log2p1"):
        raise NotFound(f"no layer {name}")
    return np.memmap(d / spec["file"], dtype=np.dtype(spec["dtype"]).newbyteorder("<"), mode="r", shape=tuple(spec["shape"]))


def _layer(d: Path, m: dict, name: str) -> np.ndarray:
    return np.asarray(S.decode(np.asarray(_raw(d, m, name)), m["layers"][name]), dtype=np.float32)


class _Queue:
    """One world's wanted tiles and build queue."""

    def __init__(self):
        self.wanted: list[L.Key] = []  # (the viewer's last list, as sent)
        self.queue: list[L.Key] = []  # (with what they read, in build order)
        self.gen = 0
        self.t = 0.0


class TileService:
    """The tile queue, the builds and the disk cache of one server (module doc). jobs: the server's api.Jobs (or
    anything with submit, get, cancel, active_where); free_ram: GB free now (api.free_ram_gb)."""

    def __init__(self, jobs, cap_gb: float | None = None, at_once: int = AT_ONCE, free_ram=api.free_ram_gb,
                 clock=time.time):
        self.jobs = jobs
        self.cap_gb = float(cap_gb if cap_gb is not None else os.environ.get("PLANET_TILE_CACHE_GB", CAP_GB))
        self.at_once = at_once
        self.free_ram = free_ram
        self.clock = clock
        self.lock = threading.RLock()
        self.worlds: dict[str, _Queue] = {}
        self.inflight: dict[tuple[str, L.Key], dict] = {}  # (wid, key) -> {jid, level}
        self.failed: dict[tuple[str, L.Key], tuple[float, str]] = {}
        self.idx: dict[str, dict[str, dict]] = {}  # wid -> {key str: {id, level, bytes, built, used}}
        self._dirty: set[str] = set()
        self._flushed = 0.0
        self.note = ""
        self._stop = threading.Event()
        self._wids: dict[str, str] = {}

    # ---- the index on disk ---------------------------------------------------------------------------------------
    @staticmethod
    def _index_path(wid: str) -> Path:
        return S.root() / ".tiles" / f"{wid}.json"

    def _world_index(self, wid: str) -> dict[str, dict]:
        """The world's index (read once; entries whose directory is gone are dropped)."""
        ix = self.idx.get(wid)
        if ix is None:
            try:
                ix = json.loads(self._index_path(wid).read_text())
            except (OSError, ValueError):
                ix = {}
            ix = {k: e for k, e in ix.items() if (S.tile_zooms_dir(wid) / e["id"] / "zoom.json").exists()}
            self.idx[wid] = ix
        return ix

    def load_all(self):
        """Every world's index (the cap counts all of them)."""
        d = S.root() / ".tiles"
        for f in sorted(d.glob("*.json")) if d.is_dir() else []:
            with self.lock:
                self._world_index(f.stem)

    def _record(self, wid: str, key: L.Key, d: Path) -> dict:
        now = self.clock()
        e = {"id": d.name, "level": key.level, "bytes": _dir_bytes(d), "built": now, "used": now}
        self.idx.setdefault(wid, {})[str(key)] = e
        self._dirty.add(wid)
        return e

    def flush(self, force: bool = False):
        with self.lock:
            if not self._dirty or (not force and self.clock() - self._flushed < FLUSH_S):
                return
            for wid in sorted(self._dirty):
                p = self._index_path(wid)
                p.parent.mkdir(parents=True, exist_ok=True)
                S.write_atomic(p, json.dumps(self.idx.get(wid, {}), indent=0))
            self._dirty.clear()
            self._flushed = self.clock()

    # ---- what is built ---------------------------------------------------------------------------------------------
    def wid(self, world: str) -> str:
        w = self._wids.get(world)
        if w is None:
            w = self._wids[world] = S.find_world(str(world).removesuffix(".json")).stem  # (SystemExit: no such world)
        return w

    @staticmethod
    def _section_request(wid: str, cell: str) -> dict:
        return api.parse_zoom_request({"world": wid, "section": cell, "res_km": L.res_km(1), "seed": SEED})

    def built(self, wid: str, key: L.Key) -> Path | None:
        """The tile's directory if it is built (recorded in the index when found)."""
        ix = self._world_index(wid)
        e = ix.get(str(key))
        td = S.tile_zooms_dir(wid)
        if e is not None:
            d = td / e["id"]
            if (d / "zoom.json").exists():
                return d
            del ix[str(key)]
            self._dirty.add(wid)
        if key.level == 1:  # (a matched section's id depends on what it was matched to: only the index knows it, from
            return None     # the job that built it (_refresh))
        d = td / L.tile_id(wid, key, SEED)
        if not (d / "zoom.json").exists():
            return None
        self._record(wid, key, d)
        return d

    def _needs(self, wid: str, key: L.Key, out: list, seen: set):
        """Appends the unbuilt tiles key's build reads (recursively, coarsest first), then key."""
        if key in seen:
            return
        seen.add(key)
        if self.built(wid, key) is not None:
            return
        for s in L.parent_sources(key):
            self._needs(wid, s, out, seen)
        out.append(key)

    # ---- the queue -------------------------------------------------------------------------------------------------
    def want(self, world: str, tiles, gen: int = 0) -> dict:
        """POST /api/tiles/want: replace the world's queue with these tiles (most wanted first) and what they read."""
        wid = self.wid(world)
        keys = []
        for t in list(tiles)[:MAX_WANT]:
            k = _key(t)
            if L.exists(k):
                keys.append(k)
        with self.lock:
            out, seen = [], set()
            for k in keys:
                self._needs(wid, k, out, seen)
            order = {k: i for i, k in enumerate(out)}
            queue = sorted(out, key=lambda k: (k.level, order[k]))  # coarser first, then the viewer's order
            q = self.worlds.setdefault(wid, _Queue())
            q.wanted, q.queue, q.gen, q.t = keys, queue, int(gen or 0), self.clock()
            keep = set(queue)
            for (w, k), f in list(self.inflight.items()):  # a build still waiting for a worker and no longer wanted: dropped
                if w == wid and k not in keep:
                    j = self.jobs.get(f["jid"])
                    if j is not None and j.get("status") == "queued":
                        self.jobs.cancel(f["jid"])
                        del self.inflight[(w, k)]
            self.pump()
            return self.status(wid)

    def _refresh(self):
        """Builds that ended: recorded (view.bin written) or marked failed."""
        for (wid, k), f in list(self.inflight.items()):
            j = self.jobs.get(f["jid"])
            st = None if j is None else j.get("status")
            if st in ("queued", "running"):
                continue
            del self.inflight[(wid, k)]
            if st == "done":
                d = self.built(wid, k)
                if d is None and j.get("zoom") and (S.tile_zooms_dir(wid) / j["zoom"] / "zoom.json").exists():
                    d = S.tile_zooms_dir(wid) / j["zoom"]  # (level 1: named by the job)
                if d is not None:
                    try:
                        write_view(d)
                    except (OSError, KeyError, NotFound) as e:
                        self.failed[(wid, k)] = (self.clock(), f"view.bin: {e}")
                        continue
                    self._record(wid, k, d)
                    self.failed.pop((wid, k), None)
                    continue
                self.failed[(wid, k)] = (self.clock(), "the build ended but the tile is not there")
            elif j is not None and j.get("cancelled"):
                continue
            else:
                msg = (j or {}).get("error") or "the build was lost"
                self.failed[(wid, k)] = (self.clock(), msg)

    def _failed(self, wid: str, k: L.Key) -> str | None:
        f = self.failed.get((wid, k))
        if f is None:
            return None
        wait = ROOM_RETRY_S if f[1].startswith("not started") else FAIL_RETRY_S
        if self.clock() - f[0] > wait:
            del self.failed[(wid, k)]
            return None
        return f[1]

    def _blocked(self, wid: str, k: L.Key) -> bool:
        """A tile it reads has failed (and is not built)."""
        for s in L.parent_sources(k):
            if self.built(wid, s) is None and (self._failed(wid, s) or self._blocked(wid, s)):
                return True
        return False

    def pump(self):
        """Note the builds that ended, start what may start, keep the cache under its cap."""
        with self.lock:
            self._refresh()
            self.note = ""
            stop = False
            for wid, q in sorted(self.worlds.items(), key=lambda kv: -kv[1].t):  # (the world looked at last first)
                q.queue = [k for k in q.queue if self.built(wid, k) is None]
                for k in q.queue:
                    if stop or len(self.inflight) >= self.at_once:
                        stop = True
                        break
                    if (wid, k) in self.inflight or self._failed(wid, k):
                        continue
                    if any(self.built(wid, s) is None for s in L.parent_sources(k)):
                        continue  # (parents first)
                    if k.level == 1 and any(f["level"] == 1 for f in self.inflight.values()):
                        continue  # (one section at a time)
                    reserved = sum(PEAK_GB[f["level"]] for f in self.inflight.values())
                    need = PEAK_GB[k.level] + api.ZOOM_RAM_SPARE_GB + reserved
                    ram = self.free_ram()
                    if ram is not None and ram < need:
                        self.note = (f"waiting for memory: {ram:.0f} GB free, the next tile needs {PEAK_GB[k.level]:.1f} GB "
                                     f"+ {api.ZOOM_RAM_SPARE_GB:.0f} spare + {reserved:.1f} for the builds running")
                        stop = True
                        break
                    if k.level == 1:
                        req = self._section_request(wid, k.cell)
                        busy = self.jobs.active_where(lambda r: r != req and "type" not in r and api.zoom_is_heavy(r))
                        if busy:
                            self.note = f"waiting for another section-sized zoom (job {busy})"
                            continue
                    req = {"type": "tile", "world": wid, "tile": str(k), "seed": SEED}
                    self.inflight[(wid, k)] = {"jid": self.jobs.submit(req), "level": k.level, "t0": self.clock()}
            self.evict()
            self.flush()

    # ---- what the viewer polls -------------------------------------------------------------------------------------
    def status(self, world: str, gen: int | None = None) -> dict:
        wid = self.wid(world)
        with self.lock:
            q = self.worlds.get(wid) or _Queue()
            tiles, nq, nb, nw = {}, 0, 0, 0
            for i, k in enumerate(q.queue):
                f = self.inflight.get((wid, k))
                err = self._failed(wid, k)
                if f is not None:
                    j = self.jobs.get(f["jid"]) or {}
                    tiles[str(k)] = {"state": "building", "progress": j.get("progress", 0.0), "message": j.get("message", "")}
                    nb += 1
                elif err:
                    tiles[str(k)] = {"state": "failed", "error": err}
                elif self._blocked(wid, k):
                    tiles[str(k)] = {"state": "blocked"}
                else:
                    tiles[str(k)] = {"state": "queued", "pos": i}
                    nq += 1
                    nw += any(self.built(wid, s) is None for s in L.parent_sources(k))
            for k in q.wanted:
                if str(k) not in tiles and self.built(wid, k) is not None:
                    tiles[str(k)] = {"state": "built"}
            running = sum(1 for (w, _) in self.inflight if w != wid)
            return {"world": wid, "gen": q.gen, "queued": nq, "building": nb, "waiting": nw, "other_worlds_building": running,
                    "tiles": tiles, "note": self.note, "cache_gb": round(self.cache_bytes() / 1e9, 3), "cap_gb": self.cap_gb}

    def index(self, world: str) -> dict:
        wid = self.wid(world)
        with self.lock:
            ix = self._world_index(wid)
            built: dict[str, dict[str, list]] = {}
            for ks, e in ix.items():
                k = L.Key.parse(ks)
                built.setdefault(k.cell, {}).setdefault(str(k.level), []).append([k.tx, k.ty])
        cells = [{**c, "built": built.get(c["id"], {})} for c in _cells()]
        return {"world": wid, "ladder": L.describe(), "cap_gb": self.cap_gb, "pad_px": L.PAD_PX, "cells": cells}

    # ---- tile files ------------------------------------------------------------------------------------------------
    def file(self, world: str, key: L.Key, name: str) -> tuple[bytes, str]:
        """(body, content type) of one built tile's file; NotFound when it is not built (or has no such file)."""
        wid = self.wid(world)
        with self.lock:
            d = self.built(wid, key)
            if d is None:
                raise NotFound(f"tile {key} is not built")
            e = self.idx[wid][str(key)]
            e["used"] = self.clock()
            self._dirty.add(wid)
        if name == "view.bin":
            f = d / "view.bin"
            if not f.exists():
                write_view(d)
            return f.read_bytes(), "application/octet-stream"
        m = json.loads((d / "zoom.json").read_text())
        if name == "satellite.png":
            f = d / m.get("files", {}).get("satellite", "satellite.png")
            if not f.exists():
                raise NotFound(f"tile {key} has no satellite view")
            return f.read_bytes(), "image/png"
        if name.startswith("layer/") and name.endswith(".bin"):
            return _layer(d, m, name[6:-4]).astype("<f4").tobytes(), "application/octet-stream"
        raise NotFound(f"no tile file {name}")

    # ---- the disk cap ----------------------------------------------------------------------------------------------
    def cache_bytes(self) -> int:
        return sum(e["bytes"] for ix in self.idx.values() for e in ix.values())

    def evict(self) -> list[str]:
        """Past the cap: delete the least recently used tiles of levels 2-4 (a tile's use is the latest of its own and
        its built descendants', so children go first) down to EVICT_TO of the cap. Never level 1, a tile being built or
        one a queued or running build reads. Returns the keys dropped."""
        cap = self.cap_gb * 1e9
        total = self.cache_bytes()
        if total <= cap:
            return []
        keep = set()
        for (wid, k) in self.inflight:
            keep.add((wid, k))
            keep.update((wid, s) for s in L.parent_sources(k))
        for wid, q in self.worlds.items():
            for k in q.queue:
                keep.update((wid, s) for s in L.parent_sources(k))
        eff = {}
        for wid, ix in self.idx.items():
            for ks, e in ix.items():
                eff[(wid, ks)] = e["used"]
        for lv in sorted(L.LEVELS, reverse=True):  # (finest first: a parent's use takes in its children's)
            for (wid, ks), u in list(eff.items()):
                k = L.Key.parse(ks)
                if k.level == lv and k.level > 1:
                    pk = (wid, str(L.parent(k)))
                    if pk in eff:
                        eff[pk] = max(eff[pk], u)
        cands = sorted(((u, -L.Key.parse(ks).level, wid, ks) for (wid, ks), u in eff.items()
                        if L.Key.parse(ks).level > 1 and (wid, L.Key.parse(ks)) not in keep))
        dropped = []
        for _, _, wid, ks in cands:
            if total <= EVICT_TO * cap:
                break
            e = self.idx[wid].pop(ks)
            self._dirty.add(wid)
            total -= e["bytes"]
            d = S.tile_zooms_dir(wid) / e["id"]
            if d.is_dir() and not d.is_symlink() and d.resolve().parent == S.tile_zooms_dir(wid).resolve():
                shutil.rmtree(d)
            dropped.append(f"{wid}:{ks}")
        return dropped

    # ---- the ticker ------------------------------------------------------------------------------------------------
    def start(self, every: float = 0.5) -> threading.Thread:
        """A thread that pumps the queue (builds that ended, the next to start) every `every` s."""
        self.load_all()

        def loop():
            while not self._stop.wait(every):
                try:
                    self.pump()
                except Exception as e:  # (never let the ticker die)
                    print(f"[tiles] {type(e).__name__}: {e}", flush=True)
        t = threading.Thread(target=loop, daemon=True, name="tiles")
        t.start()
        return t

    def stop(self):
        self._stop.set()
        self.flush(force=True)

    # ---- routes ----------------------------------------------------------------------------------------------------
    def get(self, path: str, query: str) -> tuple[bytes | dict, int, str]:
        """A GET under /api/tiles: (body, status, content type)."""
        from urllib.parse import parse_qsl
        q = dict(parse_qsl(query))
        try:
            if path == "/api/tiles/index":
                return self.index(q.get("world", "")), 200, "application/json"
            if path == "/api/tiles/status":
                return self.status(q.get("world", "")), 200, "application/json"
            parts = path.split("/")[3:]  # world, cell, level, tx, ty, file...
            if len(parts) < 6:
                raise NotFound("bad tile path")
            world, cell, level, tx, ty = parts[:5]
            body, ctype = self.file(world, L.Key(cell, int(level), int(tx), int(ty)), "/".join(parts[5:]))
            return body, 200, ctype
        except (NotFound, SystemExit, FileNotFoundError, KeyError) as e:
            return {"error": str(e)}, 404, "application/json"
        except ValueError as e:
            return {"error": str(e)}, 400, "application/json"

    def post(self, path: str, body: bytes) -> tuple[dict, int]:
        if path != "/api/tiles/want":
            return {"error": "no such route"}, 404
        try:
            req = json.loads(body or b"{}")
            return self.want(req.get("world", ""), req.get("tiles") or [], req.get("gen", 0)), 200
        except SystemExit as e:
            return {"error": str(e)}, 404
        except (ValueError, TypeError, KeyError) as e:
            return {"error": str(e)}, 400


_CELLS: list[dict] | None = None


def _cells() -> list[dict]:
    """The 54 cells' placement and outlines (the same for every world)."""
    global _CELLS
    if _CELLS is None:
        from .zoom import tiling as ZT
        out = []
        for s in ZT.sections(None, L.SQUARE_KM):
            fr = L.frame(s["id"])
            lat = np.degrees(np.arcsin(np.clip(fr.c[2], -1, 1)))
            lon = np.degrees(np.arctan2(fr.c[1], fr.c[0]))
            out.append({"id": s["id"], "lat": round(float(lat), 6), "lon": round(float(lon), 6),
                        "up": [round(float(v), 8) for v in fr.n], "outline": np.round(L.outline(s["id"]), 3).tolist()})
        _CELLS = out
    return _CELLS
