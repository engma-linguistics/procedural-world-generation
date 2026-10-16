"""Where outputs live and how they are stored: one place for paths, ids,
indexes, find/delete, binary layers and checkpoints.

Data root: $PLANET_DATA if set, else the repository (set_root() overrides
both, e.g. for tests). Under it:

  runs/<id>/run.json             settings, per-frame stats, events, layer specs (below)
  runs/<id>/run.txt              the conversation-friendly report
  runs/<id>/layers/<name>.bin    one layer, all frames: (frames, cells), raw little-endian
  runs/<id>/state/<t>.ckpt       full simulation state every ~100 Myr (replay starts there)
  runs/<id>/volcanoes.json.gz    every volcano at every keyframe (write_volcanoes)
  worlds/<id>.json, <id>.txt     a full world (JSON layers; the grid by reference)
  worlds/highlights/<id>.json    highlights.py cache for world <id>
  zooms/<id>/zoom.json           a regional zoom: meta + layer specs
  zooms/<id>/layers/<name>.bin   one layer, (ny, nx)
  grids/L<level>.json            grid geometry, shared by every run and world at that level
  {runs,worlds,zooms}/index.json what the viewer lists
  {runs,worlds,zooms}/.locks/    lock files (lock()): one process builds a slice, zoom, ... at a time

Several processes may write here at once (planet/parallel.py, the server's
job workers, a CLI run beside the server): files are written whole to a
temporary name and renamed into place (write_atomic), so a reader never sees
half a file, and builds that two processes could start together (slicing
the same run moment, the same zoom, a world's highlights, the indexes) take
a file lock (lock()) and look again for the finished item once they hold it.

Binary layers
-------------
Each layer's spec (in run.json / zoom.json "layers") says how to read it:

  {"file": "layers/precipitation.bin", "dtype": "uint16", "shape": [frames, cells],
   "scale": 1, "offset": 0, "transform": null, "units": "mm/yr", "description": ...}

value = stored * scale + offset, then the transform if any:
  "log2p1"    value = 2**value - 1      (river flow: wide range in a byte)
  "nbr_slot"  stored = position of the target in the cell's neighbour list
              (grid "nbr"); 255 = none, decoded as -1 (river downstream cell)
Python (decode) and the viewer (viewer/index.html, decodeFrame) both read
these fields; nothing else hard-codes an encoding. LAYERS below is the one
vocabulary of layer names shared by runs, time zooms, worlds and the viewer.
"""

from __future__ import annotations

import contextlib
import gzip
import json
import os
import pickle
import re
import secrets
import shutil
import threading
import zlib
from pathlib import Path

try:
    import fcntl
except ImportError:  # (Windows: no cross-process locks; the project targets Linux and macOS)
    fcntl = None

import numpy as np

REPO = Path(__file__).resolve().parent.parent
KINDS = ("run", "world", "zoom")
_root: Path | None = None


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
def root() -> Path:
    """The data root: set_root(), else $PLANET_DATA, else the repository."""
    if _root is not None:
        return _root
    env = os.environ.get("PLANET_DATA")
    return Path(env).resolve() if env else REPO


def set_root(path: str | Path | None) -> None:
    """Use another data root (None: back to $PLANET_DATA / the repository)."""
    global _root
    _root = Path(path).resolve() if path is not None else None


def runs_dir() -> Path:
    return root() / "runs"


def worlds_dir() -> Path:
    return root() / "worlds"


def zooms_dir() -> Path:
    return root() / "zooms"


def grids_dir() -> Path:
    return root() / "grids"


def highlights_path(world_id: str) -> Path:
    """highlights.py's cache for a world (a subfolder: world listings don't see it)."""
    return worlds_dir() / "highlights" / f"{world_id}.json"


def new_id() -> str:
    """Short random id for a run or world (6 hex characters)."""
    return secrets.token_hex(3)


def rel(path: Path) -> str:
    """A path for printing: relative to the data root when it's under it."""
    try:
        return str(Path(path).resolve().relative_to(root()))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Safe writes and locks between processes
# ---------------------------------------------------------------------------
def write_atomic(path: Path, data: str | bytes) -> Path:
    """Writes the whole file under a temporary name in the same folder, then
    renames it into place (os.replace is atomic): readers in other processes
    see the old file or the new one, never a partial one. The temporary
    name starts with a dot and ends in .tmp, so no listing glob matches it."""
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        if isinstance(data, str):
            tmp.write_text(data)
        else:
            tmp.write_bytes(data)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return path


_locks: dict[str, list] = {}  # lock file -> [RLock, depth, fd] (this process's holders)
_locks_guard = threading.Lock()


def lock_path(base_dir: Path, name: str) -> Path:
    return Path(base_dir) / ".locks" / (re.sub(r"[^0-9A-Za-z_.-]", "_", name) + ".lock")


@contextlib.contextmanager
def lock(base_dir: Path, name: str):
    """An exclusive lock named `name` under base_dir/.locks/, held across
    processes (fcntl.flock) and threads, re-entrant within a thread. Lock
    files are left in place (removing them would race)."""
    path = str(lock_path(base_dir, name))
    with _locks_guard:
        ent = _locks.setdefault(path, [threading.RLock(), 0, None])
    with ent[0]:  # threads of this process queue here; flock then queues processes
        if ent[1] == 0:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
            try:
                if fcntl is not None:
                    fcntl.flock(fd, fcntl.LOCK_EX)
            except BaseException:
                os.close(fd)
                raise
            ent[2] = fd
        ent[1] += 1
        try:
            yield
        finally:
            ent[1] -= 1
            if ent[1] == 0:
                os.close(ent[2])  # (releases the flock)
                ent[2] = None


# ---------------------------------------------------------------------------
# JSON: one top-level key per line, header keys first, so listings read a
# few lines instead of parsing megabytes of frames or layers
# ---------------------------------------------------------------------------
def jsonable(o):
    """json.dumps default= for numpy values."""
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def write_json(path: Path, obj: dict) -> None:
    """obj with one top-level key per line (compact values), in obj's order."""
    lines = [f"{json.dumps(k)}: {json.dumps(v, default=jsonable, separators=(',', ':'))}"
             for k, v in obj.items()]
    write_atomic(path, "{\n" + ",\n".join(lines) + "\n}\n")


HEADER_END = ("grid", "legend", "summary", "layers", "events", "frames")  # big keys come after the header


def read_header(path: Path, keys=("format", "kind", "id", "name", "meta")) -> dict:
    """The given top-level keys of a file written by write_json (or
    world.save), reading only the lines before the first big key."""
    head, want = {}, set(keys)
    with open(path) as fh:
        if fh.readline().strip() != "{":  # not one key per line (e.g. edited by hand): parse it all
            d = json.loads(Path(path).read_text())
            return {k: d[k] for k in keys if k in d}
        for line in fh:
            m = re.match(r'"(\w+)": ', line)
            if not m:
                continue
            if m.group(1) in HEADER_END:
                break
            if m.group(1) in want:
                head[m.group(1)] = json.loads(line[m.end():].rstrip().rstrip(","))
                want.discard(m.group(1))
                if not want:
                    break
    return head


# ---------------------------------------------------------------------------
# Layer vocabulary and encodings
# ---------------------------------------------------------------------------
def _spec(dtype, units, description, scale=1, offset=0, transform=None) -> dict:
    return {"dtype": dtype, "scale": scale, "offset": offset, "transform": transform,
            "units": units, "description": description}


# The names used everywhere (runs, time zooms, worlds, viewer), with the
# encoding runs store them in. Worlds hold the same names as JSON values,
# for the layers they have: sliced and generated worlds don't store the
# wind_*, current_* and jet_* layers (only runs and the Earth world do).
LAYERS = {
    "elevation": _spec("<i2", "m", "above sea level: the ground, below any ice (runs, worlds; land where > 0 or "
                                   "under grounded ice, geo.is_land), or the ice surface (time zooms)"),
    "plate": _spec("<u2", "id", "plate id"),
    "crust": _spec("u1", "0/1", "1 = continental crust, 0 = oceanic"),
    "crust_age": _spec("<u2", "Myr", "age of the crust (sea floor: since it formed at a ridge)"),
    "plate_boundary": _spec("i1", "+1/-1", "+1 converging, -1 diverging, 0 none"),
    "rock": _spec("u1", "ROCKS id", "basement rock (surface.ROCKS)"),
    "surface_rock": _spec("u1", "ROCKS id", "exposed rock: the cover's top stratum, or the basement under < 50 m of cover"),
    "sediment_cover": _spec("<u2", "km", "sediment on top of the basement", scale=0.1),
    "crust_thickness": _spec("u1", "km", "crust thickness"),
    "precipitation": _spec("<u2", "mm/yr", "annual precipitation"),
    "temperature": _spec("i1", "C", "annual mean temperature"),
    # seasons (worlds): July and January, not warmest/coldest month (those swap between hemispheres)
    "temperature_jul": _spec("i1", "C", "July mean temperature (the warmest month in the north, coldest in the south)"),
    "temperature_jan": _spec("i1", "C", "January mean temperature (the coldest month in the north, warmest in the south)"),
    "precipitation_jul": _spec("<u2", "mm/yr", "precipitation in the July half-year (Apr-Sep), as a rate per year"),
    "precipitation_jan": _spec("<u2", "mm/yr", "precipitation in the January half-year (Oct-Mar), as a rate per year"),
    "climate": _spec("u1", "KOPPEN id", "Koppen class (climate.KOPPEN)"),
    "ice": _spec("u1", "m", "land ice thickness", scale=20),
    "flow": _spec("u1", "cells x m/yr", "river flow: upstream runoff (x cell area / 1 yr = m3/s)",
                  scale=1 / 16, transform="log2p1"),
    "downstream": _spec("u1", "cell", "next cell down the river, -1 none", transform="nbr_slot"),
    "lake_depth": _spec("<u2", "m", "lake water depth (lake surface - elevation; 0 off lakes), in decimetres", scale=0.1),
    "lake_kind": _spec("u1", "id", "0 none, 1 open (fresh), 2 closed (salt), 3 salt pan (hydrology)"),
    "flood_ratio": _spec("u1", "x", "river's peak month flow / mean month flow (hydrology.seasonal_flow; 0 at sea)",
                         scale=0.1),
    "flood_month": _spec("u1", "month", "month of the river's peak flow, 1-12 (0 at sea)"),
    "river_frozen": _spec("u1", "months", "months a year the cell's rivers are frozen (below -2 C; 0 at sea)"),
    "wind_e": _spec("i1", "~1 = steady trade wind", "annual-mean surface wind, east component", scale=0.02),
    "wind_n": _spec("i1", "~1 = steady trade wind", "annual-mean surface wind, north component", scale=0.02),
    "wind_jul_e": _spec("i1", "~1 = steady trade wind", "July half-year surface wind, east component", scale=0.02),
    "wind_jul_n": _spec("i1", "~1 = steady trade wind", "July half-year surface wind, north component", scale=0.02),
    "wind_jan_e": _spec("i1", "~1 = steady trade wind", "January half-year surface wind, east component", scale=0.02),
    "wind_jan_n": _spec("i1", "~1 = steady trade wind", "January half-year surface wind, north component", scale=0.02),
    "current_e": _spec("i1", "same scale as wind", "surface ocean current, east component", scale=0.02),
    "current_n": _spec("i1", "same scale as wind", "surface ocean current, north component", scale=0.02),
    "jet_e": _spec("i1", "m/s", "annual-mean jet stream (upper-level wind), east component"),
    "jet_n": _spec("i1", "m/s", "annual-mean jet stream (upper-level wind), north component"),
    "jet_jul_e": _spec("i1", "m/s", "July half-year jet stream (upper-level wind), east component"),
    "jet_jul_n": _spec("i1", "m/s", "July half-year jet stream (upper-level wind), north component"),
    "jet_jan_e": _spec("i1", "m/s", "January half-year jet stream (upper-level wind), east component"),
    "jet_jan_n": _spec("i1", "m/s", "January half-year jet stream (upper-level wind), north component"),
    "wave_power": _spec("<u2", "kW/m", "mean wave power arriving at sea cells (coast.py; 0 on land)", scale=0.1),
    "sst": _spec("<i2", "C", "sea-surface temperature, annual mean (0 on land)", scale=0.1),
    "sst_jul": _spec("<i2", "C", "sea-surface temperature in July (0 on land)", scale=0.1),
    "sst_jan": _spec("<i2", "C", "sea-surface temperature in January (0 on land)", scale=0.1),
    "salinity": _spec("<u2", "psu", "sea-surface salinity (ocean.py; 0 on land)", scale=0.01),
    "sinking": _spec("<u2", "Sv", "deep water sinking there: the overturning's sinking sites (ocean.py)",
                     scale=0.001),
    "dewpoint_jul": _spec("i1", "C", "dew point of the air near the ground, July half-year"),
    "dewpoint_jan": _spec("i1", "C", "dew point of the air near the ground, January half-year"),
    "humidity_jul": _spec("u1", "%", "relative humidity near the ground, July half-year"),
    "humidity_jan": _spec("u1", "%", "relative humidity near the ground, January half-year"),
    "cloud_jul": _spec("u1", "%", "cloud cover (share of the sky), July half-year (climate.clouds)"),
    "cloud_jan": _spec("u1", "%", "cloud cover (share of the sky), January half-year (climate.clouds)"),
    "sunshine_jul": _spec("u1", "h/day", "bright sunshine, hours a day, July half-year (climate.sunshine)", scale=0.1),
    "sunshine_jan": _spec("u1", "h/day", "bright sunshine, hours a day, January half-year (climate.sunshine)",
                          scale=0.1),
    "tide_range": _spec("u1", "m", "tidal range at sea cells (coast.py; 0 on land)", scale=0.1),
    "upwelling": _spec("u1", "C", "how much upwelling cools the sea surface (climate.upwelling_cooling; 0 on land)",
                       scale=0.1),
    # coastal and shallow-sea life (coastal.py, PW-188; worlds): % of each cell
    "reef": _spec("<u2", "%", "coral reef framework (sea cells)", scale=0.1),
    "kelp": _spec("<u2", "%", "kelp forest (sea cells)", scale=0.1),
    "seagrass": _spec("<u2", "%", "seagrass meadow (sea cells)", scale=0.1),
    "mangrove": _spec("<u2", "%", "mangrove forest between the tides (coastal land cells)", scale=0.1),
    "salt_marsh": _spec("<u2", "%", "salt marsh between the tides (coastal land cells)", scale=0.1),
    "turbidity": _spec("<u2", "mg/L", "suspended sediment at the sea surface, from the rivers (0 on land)",
                       scale=0.1),
    # landform classes and their parameters (landform.py; read from each cell's geological record)
    "landform": _spec("u1", "id", "landform class (landform.CLASSES; legend 'landforms')"),
    "landform_age": _spec("<u2", "Myr", "landform age; by class: since rifting, folding, eruption, the top "
                                        "stratum last grew, or the basement formed (landform.CLASSES)"),
    "strata_top": _spec("u1", "ROCKS id", "exposed stratum (or the basement, where none is left)"),
    "strata_top_km": _spec("u1", "km", "thickness of the exposed stratum (0: basement)", scale=0.02),
    "strata_next": _spec("u1", "ROCKS id", "what lies under the exposed stratum (next stratum or the basement)"),
    "strata_dip": _spec("u1", "deg", "dip of the exposed strata (folded: by the squeezing; flat: regional slope)",
                        scale=0.25),
    "fold_wavelength": _spec("u1", "km", "distance between fold crests (0: strata not folded)", scale=0.2),
    "rift_strain": _spec("u1", "ln beta", "stretching of the cell's last rifting (0: never rifted)", scale=0.01),
    "glaciated_myr": _spec("<u2", "Myr", "since the cell was last under ice (0: now; 9999: never)"),
    # vegetation (vegetation.py): runs store vegetation, tree_cover and npp per keyframe; worlds all of them
    "vegetation": _spec("u1", "id", "named vegetation type (vegetation.TYPES; legend 'vegetation')"),
    "tree_cover": _spec("u1", "%", "tree canopy cover (each tree type's share x its canopy closure)"),
    "plant_cover": _spec("u1", "%", "ground shaded by plants of any kind"),
    "lai": _spec("u1", "m2/m2", "leaf area index, year's mean of the two half-years", scale=0.1),
    "lai_jul": _spec("u1", "m2/m2", "leaf area index, July half-year (Apr-Sep)", scale=0.1),
    "lai_jan": _spec("u1", "m2/m2", "leaf area index, January half-year (Oct-Mar)", scale=0.1),
    "canopy_height": _spec("u1", "m", "height of the tallest layer covering >= 10% of the cell"),
    "npp": _spec("<u2", "g C/m2/yr", "net primary productivity"),
    "biomass": _spec("<u2", "t C/ha", "living plant carbon"),
    "fire_return": _spec("<u2", "yr", "mean years between fires (0: none)"),
    "stand_age": _spec("<u2", "yr", "mean time since the last stand-replacing disturbance"),
    "pft_dominant": _spec("u1", "id", "the plant functional type with the largest cover (255: none)"),
    "flooded": _spec("u1", "%", "share of the cell flooded part of the year (wetland habitat)"),
    # soils (soils.py, worlds; PW-185)
    "soil": _spec("u1", "id", "named soil type (soils.TYPES; legend 'soils')"),
    "soil_depth": _spec("u1", "m", "rootable soil above rock or saprolite", scale=0.02),
    "soil_texture": _spec("u1", "id", "soil texture (legend soils.textures: none, sand, loam, silt, clay, peat)"),
    "soil_water": _spec("<u2", "mm", "water the soil holds for plants (available water x depth to 1.5 m)"),
    "soil_fertility": _spec("u1", "0-1", "nutrient and base status", scale=0.01),
    "soil_drainage": _spec("u1", "class", "drainage, 1 excessive .. 5 very poor (0: no soil)"),
    "soil_carbon": _spec("u1", "kg C/m2", "organic carbon in the top metre (peat included)", scale=0.5),
    "peat_depth": _spec("u1", "m", "peat thickness where peat lies (0: none)", scale=0.05),
    "permafrost": _spec("u1", "class", "0 none, 1 sporadic, 2 discontinuous, 3 continuous"),
    "loess": _spec("<u2", "m", "wind-blown silt thickness", scale=0.1),
}
# the satellite view (satellite.py): true colour as 0xRRGGBB (worlds only)
# Runs store some layers more compactly than worlds and zooms (a keyframe per
# few Myr adds up): the half-year rain as a log scale in one byte (~4% steps).
RUN_LAYERS = {
    "precipitation_jul": _spec("u1", "mm/yr", "precipitation in the July half-year (Apr-Sep), as a rate per year",
                               scale=1 / 16, transform="log2p1"),
    "precipitation_jan": _spec("u1", "mm/yr", "precipitation in the January half-year (Oct-Mar), as a rate per year",
                               scale=1 / 16, transform="log2p1"),
}


def run_spec(name: str) -> dict:
    """The encoding a run's keyframes store layer `name` in."""
    return RUN_LAYERS.get(name) or LAYERS[name]


LAYERS["sat"] = _spec("<u4", "0xRRGGBB", "true colour, each hemisphere's summer (satellite.py)")
LAYERS["sat_jul"] = _spec("<u4", "0xRRGGBB", "true colour in July (satellite.py)")
LAYERS["sat_jan"] = _spec("<u4", "0xRRGGBB", "true colour in January (satellite.py)")
from .vegetation import CODES as _VEG_CODES  # noqa: E402

for _c in _VEG_CODES:
    LAYERS[f"veg_{_c}"] = _spec("u1", "%", f"cover of plant functional type {_c} (vegetation.PFTS)")


def nbr_slot(grid, target: np.ndarray) -> np.ndarray:
    """Each cell's target cell (e.g. downstream) as its position in the
    cell's neighbour list; 255 where the target isn't a neighbour (or -1)."""
    deg = np.diff(grid.nbr_off)
    src = np.repeat(np.arange(grid.n), deg)
    pos = np.arange(len(grid.nbr_idx)) - grid.nbr_off[src]
    hit = grid.nbr_idx == np.asarray(target)[src]
    out = np.full(grid.n, 255, np.uint8)
    out[src[hit]] = pos[hit]
    return out


def encode(values, spec: dict, grid=None) -> np.ndarray:
    """Values in real units -> the stored array (rounded, clipped to the dtype)."""
    dt = np.dtype(spec["dtype"])
    if spec.get("transform") == "nbr_slot":
        return nbr_slot(grid, values).astype(dt)
    x = np.asarray(values)
    if x.dtype.kind == "b":
        x = x.astype(np.uint8)
    if spec.get("transform") == "log2p1":
        x = np.log2(1 + x)
    if spec.get("offset", 0):
        x = x - spec["offset"]
    if spec.get("scale", 1) != 1:
        x = x / spec["scale"]
    if dt.kind in "iu":
        info = np.iinfo(dt)
        x = np.clip(np.round(x), info.min, info.max)
    return x.astype(dt)


def decode(raw: np.ndarray, spec: dict, grid=None) -> np.ndarray:
    """Stored array -> values in real units. Layers stored as is (ids,
    metres, ...) come back unchanged (same dtype); scaled ones as float."""
    tr = spec.get("transform")
    if tr == "nbr_slot":
        raw = np.asarray(raw)
        cell = np.arange(raw.shape[-1])
        j = grid.nbr_off[cell] + np.minimum(raw, 254)
        return np.where(raw == 255, -1, grid.nbr_idx[np.minimum(j, len(grid.nbr_idx) - 1)])
    if spec.get("scale", 1) == 1 and not spec.get("offset", 0) and not tr:
        return raw
    x = np.asarray(raw, dtype=float) * spec.get("scale", 1) + spec.get("offset", 0)
    if tr == "log2p1":
        x = np.exp2(x) - 1
    return x


# ---------------------------------------------------------------------------
# Binary layer files
# ---------------------------------------------------------------------------
def write_layers(out_dir: Path, arrays: dict, specs: dict | None = None) -> dict:
    """Writes out_dir/layers/<name>.bin per array (already encoded; cast to
    the spec's dtype, little-endian). specs: name -> encoding/units/description
    (default LAYERS[name]; without a dtype, the array's own). Returns the
    layer specs for the metadata file, in the order given."""
    (out_dir / "layers").mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, a in arrays.items():
        spec = dict((specs or {}).get(name) or LAYERS[name])
        dt = np.dtype(spec.get("dtype") or np.asarray(a).dtype).newbyteorder("<")
        arr = np.ascontiguousarray(np.asarray(a).astype(dt))
        path = out_dir / "layers" / f"{name}.bin"
        arr.tofile(path)
        meta[name] = {"file": f"layers/{name}.bin", "dtype": dt.name, "shape": list(arr.shape),
                      **{k: spec.get(k, d) for k, d in (("scale", 1), ("offset", 0), ("transform", None))},
                      **{k: spec[k] for k in ("units", "description") if k in spec}}
    return meta


def read_layer(base_dir: Path, spec: dict, mmap: bool = True) -> np.ndarray:
    """One stored layer (raw, not decoded), memory-mapped by default: reading
    one frame of a 500 MB run touches only that frame."""
    dt = np.dtype(spec["dtype"]).newbyteorder("<")
    path = Path(base_dir) / spec["file"]
    shape = tuple(spec["shape"])
    if mmap and int(np.prod(shape)) > 0:
        return np.memmap(path, dt, "r", shape=shape)
    return np.fromfile(path, dt).reshape(shape)


def read_layers(base_dir: Path, specs: dict, names=None, mmap: bool = True) -> dict:
    """{name: raw layer} for names (default: all in specs)."""
    return {k: read_layer(base_dir, specs[k], mmap) for k in (specs if names is None else names)}


# ---------------------------------------------------------------------------
# Grids and legends
# ---------------------------------------------------------------------------
def latlon_lists(v: np.ndarray) -> tuple[list, list]:
    """Lat and lon (degrees, 3 decimals) of unit vectors, as JSON-ready lists."""
    from .geo import latlon
    lat, lon = latlon(v)
    return np.round(lat, 3).tolist(), np.round(lon, 3).tolist()


def grid_path(level: int) -> Path:
    return grids_dir() / f"L{level}.json"


def write_grid(grid) -> Path:
    """Geometry for the viewer, shared by every run and world at this level."""
    path = grid_path(grid.level)
    if path.exists() and '"nbr"' in path.read_text()[-200000:]:
        return path
    grids_dir().mkdir(parents=True, exist_ok=True)
    lat, lon = latlon_lists(grid.centers)
    clat, clon = latlon_lists(grid.corners)
    write_atomic(path, json.dumps({"level": grid.level, "lat": lat, "lon": lon, "corner_lat": clat,
                                   "corner_lon": clon, "cells": grid.cell_corners,
                                   "pentagons": grid.pentagons.tolist(), "nbr": grid.neighbors},
                                  separators=(",", ":")))
    return path


def legends() -> dict:
    """Rock, Koppen, biome, landform, vegetation and soil ids -> names and colours, as every file stores them."""
    from .climate import BIOMES, KOPPEN
    from .landform import legend
    from .surface import ROCKS
    from .soils import legend as soil_legend
    from .vegetation import legend as veg_legend
    from .zoom_coastal import legend as coastal_legend
    return {"rocks": [{"id": r[0], "key": r[1], "name": r[2], "color": r[4]} for r in ROCKS],
            "landforms": legend(), "vegetation": veg_legend(), "coastal_life": coastal_legend(),
            "soils": soil_legend(),
            "koppen": [{"id": k[0], "code": k[1], "name": k[2], "color": k[3]} for k in KOPPEN],
            "biomes": [{"id": b[0], "name": b[1], "char": b[2], "color": b[3]} for b in BIOMES]}


# ---------------------------------------------------------------------------
# Find, list, delete
# ---------------------------------------------------------------------------
_ID = re.compile(r"[0-9a-zA-Z_-]+")


def path_of(kind: str, item_id: str) -> Path:
    """Where an item of this kind with this id lives (whether or not it exists)."""
    if kind == "run":
        return runs_dir() / item_id
    if kind == "world":
        return worlds_dir() / f"{item_id}.json"
    if kind == "zoom":
        return zooms_dir() / item_id
    raise ValueError(f"unknown kind {kind!r}; one of {KINDS}")


def exists(kind: str, item_id: str) -> bool:
    if not _ID.fullmatch(item_id or "") or item_id == "index":
        return False
    p = path_of(kind, item_id)
    return {"run": p / "run.json", "world": p, "zoom": p / "zoom.json"}[kind].is_file()


def find(kind: str, ref: str | Path) -> Path:
    """An item by id ('a3f9c2'; worlds also 'a3f9c2.json') or by path.
    Returns the run/zoom directory or the world file; SystemExit if none."""
    p = Path(ref)
    marker = {"run": "run.json", "world": None, "zoom": "zoom.json"}[kind]
    if (p / marker).is_file() if marker else (p.is_file() and p.suffix == ".json"):
        return p
    item_id = p.name.removesuffix(".json") if kind == "world" else p.name
    if exists(kind, item_id):
        return path_of(kind, item_id)
    raise SystemExit(f"no {kind} {str(ref)!r} (see: uv run python -m planet list)")


def find_run(ref) -> Path:
    return find("run", ref)


def find_world(ref) -> Path:
    return find("world", ref)


def find_zoom(ref) -> Path:
    return find("zoom", ref)


def kinds_of(item_id: str) -> list[str]:
    """Which kinds have an item with this id (ids are random, but a run and a
    world can share one)."""
    return [k for k in KINDS if exists(k, item_id)]


def zooms_of(world_id: str) -> list[Path]:
    out = []
    for p in sorted(zooms_dir().glob("*/zoom.json")):
        try:
            if json.loads(p.read_text())["source_world"]["id"] == world_id:
                out.append(p.parent)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def children_of(zoom_id: str) -> list[Path]:
    """The fine zooms made from this zoom (zoom_fine: parent_zoom.id)."""
    out = []
    for p in sorted(zooms_dir().glob("*/zoom.json")):
        try:
            if (json.loads(p.read_text()).get("parent_zoom") or {}).get("id") == zoom_id:
                out.append(p.parent)
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return out


def descendants_of(zoom_id: str) -> list[Path]:
    """Its fine zooms, theirs, and so on (children before grandchildren)."""
    out, todo = [], [zoom_id]
    while todo:
        kids = children_of(todo.pop(0))
        out += [k for k in kids if k not in out]
        todo += [k.name for k in kids]
    return out


def delete(kind: str, item_id: str) -> list[Path]:
    """Delete one run, world or zoom; returns what was removed (empty: no
    such item). A world takes its highlights cache and its zooms with it;
    a zoom its fine zooms (zoom_fine), theirs too.
    Runs and worlds don't cascade into each other: a world sliced from a
    run is self-contained."""
    if not exists(kind, item_id):
        return []
    p = path_of(kind, item_id)
    gone = []
    if kind == "world":
        for q in (p, p.with_suffix(".txt"), highlights_path(item_id)):
            if q.exists():
                q.unlink()
                gone.append(q)
        for z in zooms_of(item_id):
            shutil.rmtree(z)
            gone.append(z)
    else:
        if kind == "zoom":
            for z in descendants_of(item_id):
                if z.exists():
                    shutil.rmtree(z)
                    gone.append(z)
        shutil.rmtree(p)
        gone.append(p)
    for k in {"run": ("run",), "world": ("world", "zoom"), "zoom": ("zoom",)}[kind]:
        update_index(k)
    return gone


def orphans() -> list[Path]:
    """Zooms whose world (or parent zoom) is gone, highlight caches of
    deleted worlds, and run folders without a run.json (a simulate that was
    killed)."""
    out = [p for p in sorted(runs_dir().glob("*"))
           if p.is_dir() and not p.name.startswith(".") and not (p / "run.json").exists()]
    for p in sorted(zooms_dir().glob("*/zoom.json")):
        try:
            m = json.loads(p.read_text())
            wid, pz = m["source_world"]["id"], (m.get("parent_zoom") or {}).get("id")
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
        if not exists("world", wid) or (pz and not exists("zoom", pz)):
            out.append(p.parent)
    out += [p for p in sorted((worlds_dir() / "highlights").glob("*.json")) if not exists("world", p.stem)]
    return out


def delete_orphans() -> list[Path]:
    gone = orphans()
    for p in gone:
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    update_index("zoom")
    return gone


def _run_item(p: Path) -> dict:
    r = read_header(p)
    m = r["meta"]
    item = {"dir": p.parent.name, "id": r.get("id", p.parent.name), "name": r["name"],
            "seed": m["seed"], "level": m["level"], "myr": m["myr"], "created": m["created"]}
    if r.get("kind") == "timezoom":  # glacial time zoom (planet/timezoom.py): time in kyr
        item.update(kind="timezoom", source_run=m["source_run"], at_myr=m["at_myr"], kyr=m["kyr"])
    return item


def _world_item(p: Path) -> dict:
    head = read_header(p, ("id", "name", "meta"))
    m = head.get("meta", {})
    item = {"file": p.name, "id": head.get("id", p.stem), "name": head.get("name", p.stem),
            "created": m.get("created", ""), **{k: m.get(k) for k in ("method", "seed", "level")}}
    if m.get("source_run"):  # provenance: the run and time it was sliced from
        item.update({k: m.get(k) for k in ("source_run", "source_run_name", "t_myr")})
    if m.get("timezoom"):  # a finished world (finish.py): the time zoom and its frame
        item.update({k: m.get(k) for k in ("timezoom", "timezoom_kyr", "sea_level_change_m")})
    return item


def _zoom_item(p: Path) -> dict:
    m = json.loads(p.read_text())
    sw = m["source_world"]
    item = {"id": m["id"], "name": m["name"], "created": m["created"], "world": sw["id"],
            "world_name": sw.get("name"), "source_run": sw.get("source_run"), "t_myr": sw.get("t_myr"),
            "center": m["center"], "size_km": m["size_km"], "res_km": m["res_km"]}
    if m.get("parent_zoom"):  # a fine zoom (zoom_fine): the zoom it was made from
        item["parent_zoom"] = m["parent_zoom"]["id"]
    return item


def items(kind: str) -> list[tuple[Path, dict]]:
    """(metadata file, index entry) of every item of a kind, newest first."""
    d, pattern, item = {"run": (runs_dir(), "*/run.json", _run_item),
                        "world": (worlds_dir(), "*.json", _world_item),
                        "zoom": (zooms_dir(), "*/zoom.json", _zoom_item)}[kind]
    out = []
    for p in sorted(d.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
        if p.name == "index.json":
            continue
        try:
            out.append((p, item(p)))
        except (OSError, ValueError, KeyError, TypeError):
            continue  # half-written or foreign file
    return out


def update_index(kind: str) -> list[dict]:
    """Rewrites <kind>s/index.json (what the viewer lists) and returns it."""
    d = {"run": runs_dir, "world": worlds_dir, "zoom": zooms_dir}[kind]()
    d.mkdir(parents=True, exist_ok=True)
    with lock(d, "index"):  # (the last writer has listed last: no new item is left out)
        entries = [e for _, e in items(kind)]
        if kind == "zoom":  # each zoom lists its fine zooms (by parent_zoom), as a world's zooms name it
            kids = {}
            for e in entries:
                if e.get("parent_zoom"):
                    kids.setdefault(e["parent_zoom"], []).append(e["id"])
            for e in entries:
                if e["id"] in kids:
                    e["children"] = kids[e["id"]]
        write_atomic(d / "index.json", json.dumps(entries, indent=1))
    return entries


# ---------------------------------------------------------------------------
# Volcanoes: the table of every volcano (tectonics.volcanism.COLUMNS) at each
# keyframe of a run, gzipped JSON (~0.5-2k rows a frame: too big for run.json,
# whose frames list only the active ones, for the viewer)
# ---------------------------------------------------------------------------
def volcanoes_path(run_dir: Path) -> Path:
    return Path(run_dir) / "volcanoes.json.gz"


def write_volcanoes(run_dir: Path, columns, frames: list) -> Path:
    path = volcanoes_path(run_dir)
    write_atomic(path, gzip.compress(json.dumps({"columns": list(columns), "frames": frames},
                                                separators=(",", ":")).encode(), 6))
    return path


def read_volcanoes(run_dir: Path) -> dict | None:
    """{"columns", "frames": [rows per keyframe]}, or None for a run without it."""
    path = volcanoes_path(run_dir)
    return json.loads(gzip.decompress(path.read_bytes())) if path.exists() else None


# ---------------------------------------------------------------------------
# Checkpoints: the full simulation state every ~100 Myr of a run
# ---------------------------------------------------------------------------
# A pickle of sim.state() (tectonics.Simulation: arrays, the Plates, hotspot
# and volcano lists, events, budget), zlib-compressed, the crust of the
# plates' unowned cells zeroed (shrink_state) and the plates' cell map stored
# as its difference from a fresh grid.locate (pack_idx). Only ever read back
# from our own runs/.
def checkpoint_path(run_dir: Path, t: float) -> Path:
    return Path(run_dir) / "state" / f"{t:08.1f}.ckpt"


def save_checkpoint(run_dir: Path, sim, writer=None) -> Path:
    """The state, with the crust of plate cells nothing reads zeroed
    (shrink_state: ~9 in 10 of the plates' cells are stale copies of crust
    that has left, which compress badly). writer: a CheckpointWriter to
    pickle, compress and write it in the background (sim.state() is a deep
    copy taken here, so the run can go on meanwhile)."""
    path = checkpoint_path(run_dir, sim.t)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = sim.state()
    if writer is None:
        _write_checkpoint(path, state, sim.grid)
    else:
        writer.submit(path, state, sim.grid)
    return path


def shrink_state(state: dict) -> dict:
    """Zeroes, in place, the crust columns (plates.CRUST) of plate cells
    nothing reads on: cells a plate owns no crust in (dead slots, cells its
    crust has left: a column is written in full when a plate gains a cell)
    except those the world view samples (Simulation._world_view: a plate's
    slot can be the view's without being owned, and the view and its
    subsidence read it, PW-291) and the volcanoes' crust cells (re_home
    reads a volcano's swell, volcanism.base_level). Returns state."""
    pl = state["plates"]
    keep = pl.owned.copy()
    owner = state["owner"]
    keep[owner, pl.idx[owner, np.arange(owner.size)]] = True
    for v in state["volcanoes"]:
        keep[v["plate"], v["ref"]] = True
    for arr in pl.crust():
        arr[~keep] = 0
    return state


def _located(plates, grid) -> np.ndarray:
    """(P, n): each plate slot's cell under each world cell, found afresh
    (no warm start) from its rotation."""
    return np.stack([grid.locate(grid.centers @ q) for q in plates.Q])


def pack_idx(state: dict, grid) -> dict:
    """Replaces, in place, the plates' cell map idx ((P, n) int64, a rotated
    nearest-neighbour map that zlib can't compress: ~a quarter of a
    checkpoint) by its difference from _located (Plates.move computes it the
    same way, but warm-started from the last step: ~all zeros). unpack_idx
    adds it back, so the round trip is exact whatever the warm start did
    (PW-306). Returns state."""
    pl = state["plates"]
    pl.idx = pl.idx - _located(pl, grid)
    return state


def unpack_idx(state: dict, grid) -> dict:
    pl = state["plates"]
    pl.idx = pl.idx + _located(pl, grid)
    return state


def _write_checkpoint(path: Path, state: dict, grid):
    write_atomic(path, zlib.compress(pickle.dumps(pack_idx(shrink_state(state), grid), protocol=5), 1))


class CheckpointWriter:
    """Writes checkpoints on one background thread, one at a time (zlib and
    the disk write release the GIL: ~0.75 s per checkpoint at level 6, ~2.4 s
    at level 7, off the run's main thread; PW-258). Use as a context manager:
    leaving it waits for the last write and raises its error, if any."""

    def __init__(self):
        self._thread = None
        self._error = None

    def submit(self, path: Path, state: dict, grid):
        self.wait()

        def work():
            try:
                _write_checkpoint(path, state, grid)
            except BaseException as e:  # (raised again by wait, on the run's thread)
                self._error = e
        self._thread = threading.Thread(target=work, name="checkpoint", daemon=True)
        self._thread.start()

    def wait(self):
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        if self._error is not None:
            e, self._error = self._error, None
            raise e

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.wait()


def checkpoints(run_dir: Path) -> list[float]:
    """Times (Myr) with a checkpoint, ascending."""
    return sorted(float(p.stem) for p in (Path(run_dir) / "state").glob("*.ckpt"))


def load_checkpoint(run_dir: Path, t: float, grid) -> dict:
    """The state saved at t (grid: the run's, to unpack the plates' cell map)."""
    return read_checkpoint(checkpoint_path(run_dir, t), grid)


def read_checkpoint(path: Path, grid) -> dict:
    return unpack_idx(pickle.loads(zlib.decompress(Path(path).read_bytes())), grid)
