"""Pipeline (generate -> climate -> erosion/rivers -> biomes) and file I/O.

On-disk format: worlds/<id>.json (paths: store.py)
-----------------------------------
{
  "format": "procgen-planet/2",
  "name", "id",
  "meta":    {...how it was made: method, seed, params...},
  "summary": {...headline stats...},
  "legend":  {"rocks", "koppen", "biomes": ids -> names/colours (store.legends)},
  "grid":    "../grids/L<level>.json"  (the shared grid file, as runs use:
              lat, lon, corner_lat, corner_lon, cells, pentagons, nbr),
  "layers":  {"elevation": [m per cell], "temperature": [...], ...}
}
Every array in "layers" is indexed by cell id; layer names are store.LAYERS'
vocabulary. A plain-text companion, worlds/<id>.txt, has the summary plus
ASCII maps. That's the conversation-friendly view.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import climate, coast, hydrology
from . import store as S
from .generators import GENERATORS
from .geo import R_KM, latlon, xyz
from .grid import Grid, build_grid


def generate(method: str, seed: int = 0, level: int = 5, erosion: float = 1.0,
             erosion_iterations: int = 12, dT: float = 0.0, tilt: float = 23.4, **params) -> dict:
    t0 = time.time()
    grid = build_grid(level)
    rng = np.random.default_rng(seed)
    elev, extra = GENERATORS[method](grid, rng, **params)
    meta = {"method": method, "seed": seed, "level": level}
    return finish(grid, elev, extra, meta, erosion, erosion_iterations, dT, tilt, params, t0)


def finish(grid: Grid, elev: np.ndarray, extra: dict, meta: dict, erosion: float = 1.0,
           erosion_iterations: int = 12, dT: float = 0.0, tilt: float = 23.4,
           params: dict | None = None, t0: float | None = None, ice: np.ndarray | None = None) -> dict:
    """Shared back half of the pipeline: climate -> erosion -> rivers -> biomes.
    dT: global temperature offset from today's Earth; ice: m of land ice."""
    t0 = t0 or time.time()
    c = climate.compute(grid, elev, dT, tilt, ice)
    if erosion > 0 and erosion_iterations > 0:
        elev = hydrology.erode(grid, elev, c["runoff"], erosion_iterations, erosion)
        c = climate.compute(grid, elev, dT, tilt, ice)
    temp, precip = c["temp"], c["precip"]
    extra = {"climate": c["koppen"], "warm_month": c["t_warm"], "cold_month": c["t_cold"], **extra}
    flow, down, lk = hydrology.rivers_and_lakes(grid, elev, c, ice)
    biome = climate.biomes(elev, temp, precip, lk["wet"])
    elev_m = np.round(elev).astype(int)

    layers = {
        "elevation": elev_m,
        "temperature": np.round(temp, 1),
        "precipitation": np.round(precip).astype(int),
        "biome": biome,
        "flow": np.round(flow, 2),  # river flow: upstream runoff, cells x m/yr (x cell area / 1 yr = m3/s)
        "downstream": down,
        "lake": lk["wet"].astype(int),
        # lake surface, m, same datum as "elevation" (lake_level - elevation = water depth);
        # equal to elevation where there's no lake
        "lake_level": np.maximum(np.round(lk["level"]).astype(int), elev_m),
        "lake_kind": lk["kind"].astype(int),  # hydrology: 0 none, 1 open (fresh), 2 closed (salt), 3 salt pan
        "runoff": np.round(c["runoff"]).astype(int),  # mm/yr: rain minus evaporation, what feeds rivers
        "evaporation": np.round(c["aet"]).astype(int),  # mm/yr, actual
        "pet": np.round(c["pet"]).astype(int),  # mm/yr, potential (what a wet surface would evaporate)
        # at sea (0 on land; coast.py): mean wave power arriving, kW per m of
        # wave crest, and the tidal range, m
        "wave_power": np.round(coast.wave_power(grid, elev, c, ice), 1),
        "tide_range": np.round(coast.tide_range(grid, elev, ice_share=coast.sea_ice_share(grid, elev, c).mean(0)), 2),
    }
    # winds, currents (0 on land) and the jet stream as east/north components,
    # annual means of the two half-years, plus the July and January winds
    # (the monsoons), for the viewer's overlays
    from .timeline import vec_layers
    for k, v in (vec_layers(grid, "wind", 0.5 * (c["wind_jul"] + c["wind_jan"]))
                 + vec_layers(grid, "current", np.where((elev > 0)[:, None], 0.0, c["current"]))
                 + vec_layers(grid, "jet", 0.5 * (c["jet_jul"] + c["jet_jan"]))
                 + vec_layers(grid, "wind_jul", c["wind_jul"]) + vec_layers(grid, "wind_jan", c["wind_jan"])):
        layers[k] = np.round(v, 2)
    for k, v in extra.items():
        layers[k] = np.round(v, 3) if np.asarray(v).dtype.kind == "f" else v

    meta = {
        **meta,
        "cells": grid.n,
        "pentagons": grid.pentagons.tolist(),
        "cell_size_km": round(grid.spacing * R_KM),
        "params": {"erosion": erosion, "erosion_iterations": erosion_iterations,
                   "dT": dT, "tilt": tilt, **(params or {})},
        "generated_in_s": round(time.time() - t0, 2),
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return {"grid": grid, "layers": layers, "meta": meta}


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------
def landmasses(grid: Grid, land: np.ndarray, min_cells: int = 3):
    """Connected land regions with at least min_cells cells, largest first
    (ties: lowest cell id first), named A, B, C..."""
    label, k = grid.components(land)
    sizes = np.bincount(label[label >= 0], minlength=k)
    out = []
    for idx, comp in enumerate(c for c in np.argsort(-sizes, kind="stable") if sizes[c] >= min_cells):
        m = np.flatnonzero(label == comp)
        c = grid.centers[m].mean(0)
        lat, lon = latlon(c / np.linalg.norm(c))
        out.append({
            "name": _letters(idx),
            "cells": len(m),
            "pct_of_surface": round(100 * len(m) / grid.n, 2),
            "center_lat": round(float(lat), 1),
            "center_lon": round(float(lon), 1),
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
        **_lake_summary(g, L),
        "largest_rivers": rivers,
    }
    if "plate" in L:
        s["plates"] = int(L["plate"].max() + 1)
    return s


def _lake_summary(g: Grid, L: dict) -> dict:
    """Count lakes by kind (connected cells of one kind = one lake)."""
    if "lake_kind" not in L:
        return {}
    k = np.asarray(L["lake_kind"])
    out = {}
    for kind, name in ((hydrology.OPEN_LAKE, "open"), (hydrology.CLOSED_LAKE, "closed"),
                       (hydrology.SALT_PAN, "salt_pan")):
        out[f"lakes_{name}"] = int(g.components(k == kind)[1])
    return out


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
    pts = xyz(LAT, LON).reshape(-1, 3)
    return g.locate(pts).reshape(height, width)


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
_np = S.jsonable  # json.dumps default= for numpy values


def save(world: dict, name: str, file_id: str | None = None) -> Path:
    """Saves worlds/<id>.json (+ .txt); `name` is the human-readable label."""
    S.worlds_dir().mkdir(parents=True, exist_ok=True)
    file_id = file_id or S.new_id()
    g: Grid = world["grid"]
    world["name"] = name
    summary = summarize(world)
    S.write_grid(g)
    parts = [
        ('"format"', json.dumps("procgen-planet/2")),
        ('"name"', json.dumps(name)),
        ('"id"', json.dumps(file_id)),
        ('"meta"', json.dumps(world["meta"], default=_np)),
        ('"summary"', json.dumps(summary, default=_np)),
        ('"legend"', json.dumps(S.legends())),
        ('"grid"', json.dumps(f"../grids/L{g.level}.json")),
    ]
    layer_lines = ",\n".join(
        f'  {json.dumps(k)}: {json.dumps(np.asarray(v).tolist(), separators=(",", ":"))}'
        for k, v in world["layers"].items())
    body = ",\n".join(f"{k}: {v}" for k, v in parts)
    text = "{\n" + body + ',\n"layers": {\n' + layer_lines + "\n}\n}\n"
    path = S.path_of("world", file_id)
    path.write_text(text)
    path.with_suffix(".txt").write_text(text_report(world, summary))
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
    S.update_index("world")
