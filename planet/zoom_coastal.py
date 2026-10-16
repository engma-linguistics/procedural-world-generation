"""Coastal and shallow-sea life in the regional zoom (PW-188): coral reefs,
kelp forests, seagrass meadows, mangroves and salt marsh placed per pixel
on the zoom's own coastline and sea floor.

The world's rules (coastal.py) split into the water's or the climate's
part, interpolated from the coarse cells (coastal.environment: reef,
kelp_water, seagrass_water, mangrove_climate, salt_marsh_climate, the
mud and the light's attenuation Kd), and the place's part, from the pixel:
  reef        sea pixels shallower than the reefs' light depth (10% of the
              surface light, at most coastal.REEF_MAX_M); patches cover
              coastal.REEF_SHARE x the water's suitability of that floor.
              Plus the world's volcanoes' living reefs (zoom_volcanoes'
              fringing flats, barrier reefs and atoll rims).
  kelp        sea pixels above the kelp's light depth (1%, at most
              coastal.KELP_MAX_M) by a rocky shore: land rising ROCK_RISE m
              within ROCK_KM km, or hard rock at the shore (coastal.HARD_ROCKS),
              not muddy.
  seagrass    sea pixels above Duarte's depth limit, sheltered (the pixel's
              wave power), soft bottoms (not by a rocky shore), where no reef
              or kelp is.
  mangrove,   land pixels within TIDAL_KM of the sea whose ground lies
  salt marsh  between the tides (the pixel's share below half the tidal
              range plus coastal.SETUP, its heights taken as exponentially
              distributed about its mean, as on the globe), sheltered and
              muddy (coastal.intertidal_habitat), warm enough for mangroves,
              else salt marsh (the climate's part).
Each pixel is one habitat or none (layer `coastal_life`, LIFE): patches
from planet-fixed noise, so a pixel holds a habitat with the probability
its suitability gives (overlapping zooms agree). Mangrove and salt-marsh
pixels name the vegetation (vegetation.T "mangrove forest", "salt marsh").
"""

from __future__ import annotations

import math

import numpy as np

from . import coastal as CL
from . import vegetation as V
from . import zoom_kernels as ZK
from .geo import R_KM

LIFE = {0: ("none", ""), 1: ("coral reef", "#ff6fa8"), 2: ("kelp forest", "#9a7b2a"),
        3: ("seagrass meadow", "#3fbf6a"), 4: ("mangrove", "#14d2b0"), 5: ("salt marsh", "#e3d65a")}
REEF, KELP, SEAGRASS, MANGROVE, SALT_MARSH = 1, 2, 3, 4, 5
TIDAL_KM = 30.0  # km: tidal creeks reach this far inland at most (the pixel must also lie between the tides)
ROCK_KM = 3.0  # km: a rocky shore's land rises ...
ROCK_RISE = (30.0, 150.0)  # ... this much within ROCK_KM (from not to fully rocky)
PATCH_KM = {REEF: 6.0, KELP: 4.0, SEAGRASS: 8.0, MANGROVE: 3.0}  # km: the patches' size
FIELDS = ("reef", "kelp_water", "seagrass_water", "mud", "kd", "mangrove_climate", "salt_marsh_climate",
          "tide_range", "wave_power")
NEEDS = ("sst", "sst_jul", "sst_jan", "salinity", "wave_power", "tide_range", "warm_month", "cold_month",
         "precipitation", "downstream", "flow")  # the world layers coastal.environment needs
SEA_FIELDS = {"reef", "kelp_water", "seagrass_water", "mud", "kd", "tide_range", "wave_power"}


def _window_max(a: np.ndarray, r: int) -> np.ndarray:
    """Max over a (2r+1)^2 square around each pixel (2-D a)."""
    out = a.copy()
    for axis in (0, 1):
        src = out.copy()
        for s in range(1, r + 1):
            out = np.maximum(out, np.roll(src, s, axis))
            out = np.maximum(out, np.roll(src, -s, axis))
    return out


def _uniform(Pk: np.ndarray, km: float, res: float, seed: int) -> np.ndarray:
    """~uniform 0..1 planet-fixed noise with patches ~km across."""
    octaves = max(1, int(math.ceil(math.log2(max(km / (2 * res), 1.0)))) + 1)
    z = ZK.fbm(Pk, km, octaves, 0.5, seed) / 0.17
    return 0.5 * (1 + _erf(z / math.sqrt(2)))


def _erf(x: np.ndarray) -> np.ndarray:
    # Abramowitz & Stegun 7.1.26 (|error| < 1.5e-7)
    s = np.sign(x)
    x = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x)
    return s * y


def place(world: dict, fr, Pk: np.ndarray, px: np.ndarray, py: np.ndarray, nx: int, ny: int, res: float,
          size_km: float, seed: int, h: np.ndarray, water: np.ndarray, glacier: np.ndarray, d_sea: np.ndarray,
          surface_rock: np.ndarray | None = None, volcano_reef: np.ndarray | None = None) -> dict:
    """The zoom's coastal life. h: elevation (m; sea floor < 0), water (0
    land, 1 sea, 2 lake), glacier (bool), d_sea (km from land pixels to the
    sea), surface_rock (ROCKS ids), volcano_reef (bool: zoom_volcanoes' reef
    pixels); all flat (ny*nx). Returns {"layer": coastal_life (uint8, LIFE),
    "stats": km^2 of each habitat}."""
    from .zoom_vegetation import _sel
    g, L, meta = world["grid"], world["layers"], world["meta"]
    npx = nx * ny
    if not all(k in L for k in NEEDS):  # (a world without the sea's layers: hand-made in tests)
        return {"layer": np.zeros(npx, np.uint8), "stats": {LIFE[k][0]: 0 for k in LIFE if k}}
    pf = (meta.get("vegetation") or {}).get("pfts")
    unlocked = None if pf is None else np.array([c in pf for c in V.CODES])
    env = CL.environment(g, L, meta, unlocked)
    env["tide_range"] = np.asarray(L["tide_range"], float)
    env["wave_power"] = np.asarray(L["wave_power"], float)
    sel = _sel(g, fr, size_km)
    cx, cy = fr.to_plane(g.centers[sel])
    sea_c = np.asarray(L["elevation"], float)[sel] <= 0
    vals = np.column_stack([env[k][sel] for k in FIELDS])
    wts = np.column_stack([sea_c if k in SEA_FIELDS else np.ones(len(sel)) for k in FIELDS]).astype(float)
    f, _ = ZK.gauss_interp(px, py, cx, cy, vals, wts, 0.5 * g.spacing * R_KM)
    f = {k: np.nan_to_num(f[:, j]) for j, k in enumerate(FIELDS)}
    sea = water == 1
    land = (water == 0) & ~glacier
    depth = np.where(sea, -h, 0.0)
    kd = np.maximum(f["kd"], CL.KD_CLEAR)
    # a rocky shore: land rising ROCK_RISE within ROCK_KM, or hard rock at the shore, not muddy
    r = max(1, int(round(ROCK_KM / res)))
    hl = np.where(water == 0, np.maximum(h, 0.0), 0.0).reshape(ny, nx)
    rise = _window_max(hl, r).ravel()
    rocky = CL.ramp(rise, *ROCK_RISE)
    if surface_rock is not None:
        hard = (np.isin(surface_rock, CL.HARD_ROCKS) & (water == 0)).reshape(ny, nx).astype(float)
        rocky = np.maximum(rocky, CL.HARD_ROCK * _window_max(hard, r).ravel())
    rocky *= 1 - f["mud"]
    out = np.zeros(npx, np.uint8)
    S = int(seed) * 1_000_003 + 17 + 5_003
    u = {k: _uniform(Pk, km, res, S + 101 * k) for k, km in PATCH_KM.items()}
    # the sea floor: reefs, then kelp, then seagrass
    z_reef = np.minimum(CL.light_depth(kd, CL.REEF_LIGHT), CL.REEF_MAX_M)
    reef = sea & (depth <= z_reef) & (u[REEF] < CL.REEF_SHARE * f["reef"])
    if volcano_reef is not None:
        reef |= sea & volcano_reef
    out[reef] = REEF
    z_kelp = np.minimum(CL.light_depth(kd, CL.KELP_LIGHT), CL.KELP_MAX_M)
    kelp = sea & (out == 0) & (depth <= z_kelp) & (u[KELP] < f["kelp_water"] * rocky)
    out[kelp] = KELP
    seag = sea & (out == 0) & (depth <= CL.seagrass_depth(kd)) & (
        u[SEAGRASS] < f["seagrass_water"] * CL.sea_shelter(f["wave_power"], rocky))
    out[seag] = SEAGRASS
    # between the tides: mangroves, else salt marsh
    share = 1 - np.exp(-(0.5 * f["tide_range"] + CL.SETUP) / np.maximum(h, 0.5))
    p = (land & (d_sea <= TIDAL_KM)) * share * CL.intertidal_habitat(f["wave_power"], f["mud"])
    pm, ps = p * f["mangrove_climate"], p * f["salt_marsh_climate"]
    um = u[MANGROVE]
    out[land & (um < pm)] = MANGROVE
    out[land & (um >= pm) & (um < pm + ps)] = SALT_MARSH
    cell = res * res
    stats = {LIFE[k][0]: round(float((out == k).sum() * cell)) for k in LIFE if k}
    return {"layer": out, "stats": stats}


def name_vegetation(layer: np.ndarray, vegetation: np.ndarray) -> np.ndarray:
    """The vegetation layer with mangrove and salt-marsh pixels named so."""
    v = np.asarray(vegetation).copy()
    v[layer == MANGROVE] = V.T["mangrove forest"]
    v[layer == SALT_MARSH] = V.T["salt marsh"]
    return v


def legend() -> list[dict]:
    return [{"id": k, "name": n, "color": c} for k, (n, c) in LIFE.items() if k]
