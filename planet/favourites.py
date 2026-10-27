"""Favourites: the runs and worlds the owner hand-picked in the viewer (a star), kept server-side in
<data root>/worlds/favourites/favourites.json (a subfolder: world listings don't see it; worktrees share it through
the `worlds` symlink). `planet favourites` lists them for agents; the peoples workbench defaults its world to one.

The file is {"favourites": [{"kind": "world", "id": "...", "starred": "<iso time>"}, ...]}, oldest star first.
Items that were deleted since drop out of every listing (and out of the file on the next write)."""

from __future__ import annotations

import json
import threading
import time

from . import store as S

_LOCK = threading.Lock()  # (the server answers on threads; one writer at a time)


def path():
    return S.worlds_dir() / "favourites" / "favourites.json"


def _read() -> list[dict]:
    try:
        raw = json.loads(path().read_text())
        return [e for e in raw["favourites"] if e.get("kind") in S.KINDS and isinstance(e.get("id"), str)]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return []


def listing(kind: str | None = None) -> list[dict]:
    """The favourites that still exist, oldest star first; kind: only run, world or zoom ones."""
    return [e for e in _read() if (kind is None or e["kind"] == kind) and S.exists(e["kind"], e["id"])]


def is_favourite(kind: str, item_id: str) -> bool:
    return any(e["kind"] == kind and e["id"] == item_id for e in listing())


def _write(entries: list[dict]) -> None:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    S.write_atomic(p, json.dumps({"favourites": entries}, indent=1))


def set_favourite(kind: str, item_id: str, starred: bool) -> list[dict]:
    """Star or unstar one item; answers the new listing. ValueError for a kind that doesn't exist, KeyError for an id that doesn't."""
    if kind not in S.KINDS:
        raise ValueError(f"unknown kind {kind!r}; one of {S.KINDS}")
    if starred and not S.exists(kind, item_id):
        raise KeyError(f"no {kind} {item_id!r}")
    with _LOCK:
        cur = [e for e in listing() if not (e["kind"] == kind and e["id"] == item_id)]
        if starred:
            cur.append({"kind": kind, "id": item_id, "starred": time.strftime("%Y-%m-%dT%H:%M:%S")})
        _write(cur)
        return cur


def forget(kind: str, item_id: str) -> None:
    """An item was deleted: drop its star (store.delete calls this)."""
    with _LOCK:
        cur = _read()
        keep = [e for e in cur if not (e["kind"] == kind and e["id"] == item_id)]
        if len(keep) != len(cur):
            _write(keep)
