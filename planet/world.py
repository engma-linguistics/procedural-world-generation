"""Pipeline (generate -> climate -> erosion/rivers -> biomes) and file I/O.

On-disk format: worlds/<name>.json
-----------------------------------
{
  "format": "procgen-planet/1",
  "meta":    {...how it was made: method, seed, params...},
  "summary": {...headline stats...},
  "legend":  {...biome ids -> names/colours...},
  "layers":  {"elevation": [m per cell], "temperature": [...], ...},
  "grid":    {"lat": [...], "lon": [...], "corner_lat": [...], "corner_lon": [...],
              "cells": [[corner ids] per cell], "neighbors": [[cell ids] per cell]}
}
Every array in "layers" is indexed by cell id. A plain-text companion,
worlds/<name>.txt, has the summary plus ASCII maps. That's the
conversation-friendly view.
"""

from __future__ import annotations

import json
import secrets
import time
from collections import deque
from pathlib import Path

import numpy as np

from . import climate, hydrology
from .generators import GENERATORS
from .grid import Grid, build_grid

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ROOT / "worlds"
PLANET_RADIUS_KM = 6371


def generate(method: str, seed: int = 0, level: int = 5, erosion: float = 1.0,
             erosion_iterations: int = 12, equator_temp: float = 28.0,
             pole_temp: float = -22.0, **params) -> dict:
    t0 = time.time()
    grid = build_grid(level)
    rng = np.random.default_rng(seed)
    elev, extra = GENERATORS[method](grid, rng, **params)
    meta = {"method": method, "seed": seed, "level": level}
    return finish(grid, elev, extra, meta, erosion, erosion_iterations, equator_temp,
                  pole_temp, params, t0)


def finish(grid: Grid, elev: np.ndarray, extra: dict, meta: dict, erosion: float = 1.0,
           erosion_iterations: int = 12, equator_temp: float = 28.0, pole_temp: float = -22.0,
           params: dict | None = None, t0: float | None = None) -> dict:
    """Shared back half of the pipeline: climate -> erosion -> rivers -> biomes."""
    t0 = t0 or time.time()
    temp = climate.temperature(grid, elev, equator_temp, pole_temp)
    precip, _ = climate.precipitation(grid, elev, temp)
    if erosion > 0 and erosion_iterations > 0:
        elev = hydrology.erode(grid, elev, precip, erosion_iterations, erosion)
        temp = climate.temperature(grid, elev, equator_temp, pole_temp)
        precip, _ = climate.precipitation(grid, elev, temp)
    flow, down, lake = hydrology.rivers_and_lakes(grid, elev, precip)
    biome = climate.biomes(elev, temp, precip, lake)

    layers = {
        "elevation": np.round(elev).astype(int),
        "temperature": np.round(temp, 1),
        "precipitation": np.round(precip).astype(int),
        "biome": biome,
        "flow": np.round(flow, 2),
        "downstream": down,
        "lake": lake.astype(int),
    }
    for k, v in extra.items():
        layers[k] = np.round(v, 3) if np.asarray(v).dtype.kind == "f" else v

    meta = {
        **meta,
        "cells": grid.n,
        "pentagons": grid.pentagons.tolist(),
        "cell_size_km": round(grid.spacing * PLANET_RADIUS_KM),
        "params": {"erosion": erosion, "erosion_iterations": erosion_iterations,
                   "equator_temp": equator_temp, "pole_temp": pole_temp, **(params or {})},
        "generated_in_s": round(time.time() - t0, 2),
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return {"grid": grid, "layers": layers, "meta": meta}


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------
def landmasses(grid: Grid, land: np.ndarray, min_cells: int = 3):
    label = np.full(grid.n, -1)
    comps = []
    for s in np.flatnonzero(land):
        if label[s] >= 0:
            continue
        k = len(comps)
        label[s] = k
        q, members = deque([s]), [s]
        while q:
            i = q.popleft()
            for j in grid.neighbors[i]:
                if land[j] and label[j] < 0:
                    label[j] = k
                    q.append(j)
                    members.append(j)
        comps.append(members)
    comps.sort(key=len, reverse=True)
    out = []
    for idx, m in enumerate(c for c in comps if len(c) >= min_cells):
        c = grid.centers[m].mean(0)
        c /= np.linalg.norm(c)
        out.append({
            "name": _letters(idx),
            "cells": len(m),
            "pct_of_surface": round(100 * len(m) / grid.n, 2),
            "center_lat": round(float(np.degrees(np.arcsin(c[2]))), 1),
            "center_lon": round(float(np.degrees(np.arctan2(c[1], c[0]))), 1),
            "_members": m,
        })
    return out


def _letters(i: int) -> str:
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def summarize(world: dict) -> dict:
    g: Grid = world["grid"]
    L = world["layers"]
    elev, biome = L["elevation"], L["biome"]
    land = elev > 0
    masses = landmasses(g, land)
    lm = np.full(g.n, "", dtype=object)
    for m in masses:
        lm[m["_members"]] = m["name"]
    names = {b[0]: b[1] for b in climate.BIOMES}
    counts = np.bincount(biome[land], minlength=len(names)) if land.any() else []
    peak = int(np.argmax(elev))
    deep = int(np.argmin(elev))

    def loc(i):
        return {"cell": i, "lat": round(float(g.lat[i]), 1), "lon": round(float(g.lon[i]), 1)}

    # Biggest rivers: highest-flow cells that drain straight into the sea.
    flow, down = L["flow"], L["downstream"]
    mouths = [i for i in np.flatnonzero(land) if down[i] >= 0 and elev[down[i]] <= 0]
    mouths.sort(key=lambda i: -flow[i])
    rivers = []
    for i in mouths[:5]:
        rivers.append({**loc(i), "flow": float(flow[i]), "landmass": lm[i] or "?",
                       "length_cells": int(_river_length(g, L, i))})

    s = {
        "land_pct": round(100 * land.mean(), 1),
        "landmasses": [{k: v for k, v in m.items() if k != "_members"} for m in masses[:8]],
        "islands_small": max(0, len(masses) - 8),
        "highest_m": {**loc(peak), "elevation": int(elev[peak])},
        "deepest_m": {**loc(deep), "elevation": int(elev[deep])},
        "mean_land_elevation_m": int(elev[land].mean()) if land.any() else 0,
        "land_biomes_pct": {names[k]: round(100 * c / land.sum(), 1)
                            for k, c in sorted(enumerate(counts), key=lambda kc: -kc[1]) if c},
        "lake_cells": int(L["lake"].sum()),
        "largest_rivers": rivers,
    }
    if "plate" in L:
        s["plates"] = int(L["plate"].max() + 1)
    return s


def _river_length(g: Grid, L: dict, mouth: int) -> int:
    """Follow the biggest tributary upstream from a river mouth."""
    down, flow = L["downstream"], L["flow"]
    up: dict[int, list[int]] = {}
    for i, d in enumerate(down):
        if d >= 0:
            up.setdefault(int(d), []).append(i)
    n, i = 0, mouth
    while i in up:
        i = max(up[i], key=lambda j: flow[j])
        n += 1
    return n + 1


# ---------------------------------------------------------------------------
# ASCII maps
# ---------------------------------------------------------------------------
def nearest_cell_map(g: Grid, width: int, height: int) -> np.ndarray:
    lat = np.radians(90 - (np.arange(height) + 0.5) * 180 / height)
    lon = np.radians(-180 + (np.arange(width) + 0.5) * 360 / width)
    LON, LAT = np.meshgrid(lon, lat)
    pts = np.stack([np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)], -1).reshape(-1, 3)
    return g.locate(pts).reshape(height, width)


ELEV_CHARS = " .:-=+*#%@"


def ascii_map(world: dict, layer: str = "biome", width: int = 120, height: int | None = None) -> str:
    g, L = world["grid"], world["layers"]
    height = height or width // 4
    idx = nearest_cell_map(g, width, height)
    elev = L["elevation"]
    if layer == "biome":
        chars = {b[0]: b[2] for b in climate.BIOMES}
        grid = np.vectorize(chars.get)(L["biome"][idx])
        river = (L["flow"] > np.quantile(L["flow"][elev > 0], 0.97)) & (elev > 0) & (L["lake"] == 0)
        grid = np.where(river[idx], "|", grid)
    elif layer == "elevation":
        e = elev[idx]
        land_c = np.clip((e / 5000) * 9, 0, 9).astype(int)
        grid = np.where(e > 0, np.array(list("123456789#"))[land_c], np.where(e < -2000, " ", "."))
    elif layer == "plate":
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        grid = np.array(list(alpha))[L["plate"][idx] % len(alpha)]
        grid = np.where(elev[idx] > 0, grid, np.char.lower(grid.astype(str)))
    elif layer in ("temperature", "precipitation"):
        v = L[layer][idx]
        lo, hi = (-30, 30) if layer == "temperature" else (0, 3000)
        k = np.clip((v - lo) / (hi - lo) * 9, 0, 9).astype(int)
        grid = np.array(list("0123456789"))[k]
        grid = np.where(elev[idx] > 0, grid, " ")
    else:
        raise ValueError(f"unknown layer {layer}")
    border = "+" + "-" * width + "+"
    rows = [border] + ["|" + "".join(r) + "|" for r in grid] + [border]
    return "\n".join(rows)


LEGENDS = {
    "biome": "  ".join(f"{b[2]}={b[1]}" for b in climate.BIOMES) + "  |=major river",
    "elevation": "' '=deep ocean  .=shelf  1-9=land in ~550 m steps  #=5000 m+",
    "plate": "letter=plate id (UPPER=land, lower=sea)",
    "temperature": "land only, 0=-30C ... 9=+30C (mean annual)",
    "precipitation": "land only, 0=dry ... 9=3000+ mm/yr",
}


def _compact_json(d: dict) -> str:
    """One top-level key per line; lists of dicts get one dict per line."""
    lines = []
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            lines.append(f"  {k}:")
            lines += [f"    {json.dumps(x, default=_np)}" for x in v]
        else:
            lines.append(f"  {k}: {json.dumps(v, default=_np)}")
    return "\n".join(lines)


def text_report(world: dict, summary: dict, width: int = 120) -> str:
    m = world["meta"]
    out = [f"# World: {world.get('name', '?')}",
           f"method={m['method']} seed={m['seed']} level={m['level']} cells={m['cells']} "
           f"(~{m['cell_size_km']} km apart on an Earth-sized planet)",
           f"params: {json.dumps(m['params'])}"]
    if "source_run" in m:
        out.append(f"sliced from tectonic run runs/{m['source_run']} at t = {m['t_myr']:g} Myr")
    out += ["", "## Summary",
           _compact_json(summary), ""]
    layers = ["biome", "elevation"] + (["plate"] if "plate" in world["layers"] else []) + ["precipitation"]
    for layer in layers:
        out += [f"## {layer} map (equirectangular, north up, lon -180..180)",
                LEGENDS[layer], ascii_map(world, layer, width), ""]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------
def _np(o):
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def new_id() -> str:
    """Short random id for a run or world (6 hex characters)."""
    return secrets.token_hex(3)


def save(world: dict, name: str, file_id: str | None = None) -> Path:
    """Saves worlds/<id>.json (+ .txt); `name` is the human-readable label."""
    WORLDS.mkdir(exist_ok=True)
    file_id = file_id or new_id()
    g: Grid = world["grid"]
    world["name"] = name
    summary = summarize(world)
    from .climate import BIOMES

    def corner_ll(v):
        return (np.round(np.degrees(np.arcsin(np.clip(v[:, 2], -1, 1))), 3).tolist(),
                np.round(np.degrees(np.arctan2(v[:, 1], v[:, 0])), 3).tolist())

    clat, clon = corner_ll(g.corners)
    lat, lon = corner_ll(g.centers)
    parts = [
        ('"format"', json.dumps("procgen-planet/1")),
        ('"name"', json.dumps(name)),
        ('"id"', json.dumps(file_id)),
        ('"meta"', json.dumps(world["meta"], default=_np)),
        ('"summary"', json.dumps(summary, default=_np)),
        ('"legend"', json.dumps({"biome": [{"id": b[0], "name": b[1], "char": b[2], "color": b[3]}
                                           for b in BIOMES]})),
    ]
    layer_lines = ",\n".join(
        f'  {json.dumps(k)}: {json.dumps(np.asarray(v).tolist(), separators=(",", ":"))}'
        for k, v in world["layers"].items())
    grid_obj = {"lat": lat, "lon": lon, "corner_lat": clat, "corner_lon": clon,
                "cells": g.cell_corners, "neighbors": g.neighbors}
    grid_lines = ",\n".join(f'  {json.dumps(k)}: {json.dumps(v, separators=(",", ":"), default=_np)}'
                            for k, v in grid_obj.items())
    body = ",\n".join(f"{k}: {v}" for k, v in parts)
    text = "{\n" + body + ',\n"layers": {\n' + layer_lines + '\n},\n"grid": {\n' + grid_lines + "\n}\n}\n"
    path = WORLDS / f"{file_id}.json"
    path.write_text(text)
    (WORLDS / f"{file_id}.txt").write_text(text_report(world, summary))
    update_index()
    return path


def load(path: str | Path) -> dict:
    """Load a saved world back into the same in-memory shape generate() makes,
    so you can post-process it (edit layers, re-run climate, etc.)."""
    d = json.loads(Path(path).read_text())
    level = d["meta"]["level"]
    grid = build_grid(level)
    layers = {k: np.array(v) for k, v in d["layers"].items()}
    return {"grid": grid, "layers": layers, "meta": d["meta"], "name": d.get("name")}


def update_index():
    items = []
    for p in sorted(WORLDS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if p.name == "index.json":
            continue
        # the header (name, id, meta) is on the first few lines; don't parse megabytes of layers
        head = {}
        with open(p) as fh:
            for line in fh:
                if line.startswith('"layers"'):
                    break
                if line.startswith(('"name"', '"id"', '"meta"')):
                    k, v = line.split(":", 1)
                    head[json.loads(k)] = json.loads(v.rstrip().rstrip(","))
        m = head.get("meta", {})
        items.append({"file": p.name, "id": head.get("id", p.stem), "name": head.get("name", p.stem),
                      "created": m.get("created", ""), **{k: m.get(k) for k in ("method", "seed", "level")}})
    (WORLDS / "index.json").write_text(json.dumps(items, indent=1))
