"""The installed app's config file (install.sh writes it; `planet serve` reads its defaults).

Read only when $PLANET_CONFIG names the file: the `planet` launcher of an install sets it, a
checkout run with `uv run` does not, so a developer's checkout never picks up an install's
settings. The file is TOML:

    data = "/home/me/procgen-world-data"   # the data root ($PLANET_DATA wins when set)

    [serve]
    port = 8765                            # the first port tried; the next free one is used if taken
    jobs = 4

    [presets]                              # machine-aware presets (planned): the server's defaults per feature
"""
from __future__ import annotations

import json
import os
import socket
import tomllib
import urllib.request
from pathlib import Path

DEFAULT_PORT = 8765


def path() -> Path | None:
    p = os.environ.get("PLANET_CONFIG")
    return Path(p) if p else None


def load() -> dict:
    """The config as a dict ({} with no $PLANET_CONFIG or no file). A broken file is an error, not ignored."""
    p = path()
    if p is None or not p.is_file():
        return {}
    with p.open("rb") as f:
        return tomllib.load(f)


def serve_defaults(cfg: dict | None = None) -> dict:
    """{port, jobs, threads} for `planet serve` from the config's [serve] table (missing keys left out)."""
    s = (load() if cfg is None else cfg).get("serve") or {}
    return {k: int(s[k]) for k in ("port", "jobs", "threads") if s.get(k) is not None}


def presets(cfg: dict | None = None) -> dict:
    """The [presets] table (the hook for machine-aware presets; empty until the installer probes the machine)."""
    return dict((load() if cfg is None else cfg).get("presets") or {})


def port_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            return False
    return True


def is_planet_server(port: int, timeout: float = 2.0) -> bool:
    """Whether a `planet serve` answers on this port (GET /api/planets gives JSON)."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/planets", timeout=timeout) as r:
            json.load(r)
            return r.status == 200
    except (OSError, ValueError):
        return False


def pick_port(first: int, tries: int = 20) -> int | None:
    """The first free port from `first` on, or None."""
    return next((p for p in range(first, first + tries) if port_free(p)), None)
