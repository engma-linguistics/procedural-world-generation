"""Glacial "time zoom": ~1 Myr of ice sheets at 500-year steps, whole planet.

    uv run python -m planet timezoom <run-id> --at <Myr> [--kyr 1000] [--step 0.5]
    uv run python -m planet timezoom earth [--kyr 150]          # real Earth (ETOPO1)

A side simulation: it starts from one moment of a main run and never feeds
back into it, but any of its frames can be made into a "finished world"
(finish.py, `planet finish <id> --kyr N`). The main run's ice is a 'typical extent over the
cycles' (tectonics.Simulation._climate); here the ice comes and goes with
the orbital (Milankovitch) cycles. In a greenhouse era little happens; in
an icehouse era the ice sheets grow and collapse.

Model (per 500-yr step, see simulate)
-------------------------------------
- Frozen geology: bedrock, sea floor and plates as the run had them at t
  (plates move ~50 km per Myr, under half a cell).
- Orbit: obliquity swings around the planet's tilt (41 kyr), eccentricity
  (100 and 405 kyr terms) and the precession of the perihelion (23 kyr)
  set the insolation of every latitude and month (Berger 1978 formulas).
  The change against a reference orbit becomes a monthly temperature
  anomaly (insol_k C per W/m2 on land, less over the sea), so precession
  moves the warmth between the seasons and hemispheres, obliquity between
  the poles and tropics.
- Climate: a full climate.compute every climate_every kyr on the current
  surface (ice domes included, as height) and global temperature; in
  between the stored fields (blended from the previous full climate to the
  newest over the interval, so they change smoothly, ~climate_every late)
  are shifted by the lapse rate over the changed surface, the global
  change and the orbital anomaly. Global temperature
  follows the ice: CO2 drops as ice grows (~ -2.5 C at an Earth-LGM-sized
  ice volume, then saturates) and new ice sheets reflect sunlight (a
  smaller version of the main run's ice_albedo rule, capped). Rain scales
  ~ exp(0.07 dT) with the global and orbital changes (climate.compute
  already dries the air over high domes).
- Ice surfaces: perennial snow is bright, so its summer warmth is damped
  and it feels only a fraction of an insolation change (the snow-albedo
  feedback that lets ice spread); where the year's snow melts away the
  ice is bare and darker and gets more of the summer (which helps it
  melt back). Thick ice is a little colder all year (inversion, katabatic
  winds; climate.TUNE['ice_cooling'] x albedo_share).
- Starting ice: taken to be in balance with the starting climate (the main
  model put it where summers stay cold; Earth's is real). Where this
  model's mass balance would melt it anyway (mostly: the climate model's
  ice-free summers are too warm over big polar ice sheets) the place gets
  a fixed cooling, the smallest that lets snow outlast the summer, spread
  a few cells beyond the ice (start_anchor).
- Mass balance: snow (monthly, where it's below ~0 C) minus melt from
  positive degree days (timezoom_kernels.climate_step).
- Flow: shallow-ice approximation, nonlinear diffusion with
  D ~ H^5 |grad s|^2 (timezoom_kernels.sia_flow).
- Isostasy: bedrock sinks to iso_ratio x the ice thickness, relaxing with
  iso_tau (3 kyr), and rebounds after the ice is gone.
- Sea: ice that floats (thinner than 1.12x the water depth) breaks off;
  grounded ice on the sea floor calves at a rate ~ water depth where it
  meets open water. Sea level falls by the sea water the ice holds / ocean
  area: 0.89 x the ice above flotation (ice grounded below sea level only
  replaces sea water) plus the room the sinking bed made below sea level
  (Goelzer et al. 2020), so coastlines and land bridges move with the ice.

Output: runs/<id>/ in the run format (timeline.py, store.py) so the viewer
plays it, with time in kyr since the start and run["kind"] = meta["kind"] =
"timezoom". Per-frame layers: elevation (surface incl. ice, relative to
that frame's sea level), ice, temperature, climate. plate / crust /
crust_age / plate_boundary are stored once (shape [1, cells]): geology is frozen.
Frame stats carry sea level, ice volume and the orbit.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import numpy as np

from . import climate
from . import store as S
from . import timeline as T
from . import world as W
from .geo import R_KM
from .grid import Grid, build_grid
from .provenance import code_version
from .timezoom_kernels import climate_step, dilate, sia_flow

R_M = R_KM * 1000.0
RHO_I, RHO_W = 917.0, 1028.0
S0 = 1361.0  # W/m2, the star's light at the planet's mean distance

LAYERS = {  # per frame: store.LAYERS names and encodings, as runs
    "elevation": S.LAYERS["elevation"],  # m, surface (ice included) above that frame's sea level
    # 1 m steps in 16 bits (domes on big polar continents pass 5.1 km), so a finished world (finish.py)
    # gets the bed back from any frame as elevation - ice to a metre
    "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
    "temperature": S.LAYERS["temperature"],  # C, annual mean
    "climate": S.LAYERS["climate"],  # climate.KOPPEN id
}
STATIC = ("plate", "crust", "crust_age", "plate_boundary")  # stored once


@dataclass
class TZParams:
    """Knobs (--set key=value). Times in kyr."""
    # orbit (Earth-like ranges by default; the planet's tilt is the mean obliquity)
    obliquity_amp: float = 1.2  # deg: obliquity swings +- this around the tilt ...
    obliquity_period: float = 41.0  # ... with this period
    precession_period: float = 23.0  # perihelion goes once around the seasons
    ecc_mean: float = 0.027  # eccentricity = mean + two cycles, clipped to >= 0
    ecc_100: float = 0.015  # amplitude of the ~100 kyr cycle
    ecc_400: float = 0.010  # amplitude of the 405 kyr cycle
    phases: str = "auto"  # 'auto': for Earth 'eemian', else 'seed'; 'seed': from the source run's seed
    # and time; 'eemian': start like the last interglacial (obliquity and eccentricity high, perihelion
    # in northern summer); 'zero'; or 'a,b,c,d' = obliquity phase, perihelion longitude at t=0,
    # 100k and 405k eccentricity phases (deg)
    orbit_ref: str = "auto"  # anomalies against 'mean' (tilt, circular orbit), 'start' (the orbit at t=0)
    # or 'today' (Earth's, which the climate model is calibrated to); 'auto': 'today' for Earth, else 'mean'
    insol_k: float = 0.25  # C per W/m2 of insolation change, on land (month by month, ~2 weeks' lag)
    insol_sea: float = 0.3  # share of that over the sea (deep mixed layer)
    # climate
    climate_every: float = 10.0  # kyr between full climate.compute calls
    baseline: str = "model"  # Earth only: 'obs' = observed climate + the model's changes from today
    # (the 'delta method' of paleo ice-sheet modelling: takes the climate model's regional biases out)
    # ice surfaces
    snow_h: float = 20.0  # m: perennial snow/ice this thick is bright (phased in from 0):
    summer_damp: float = 0.6  # its summer warmth (above the annual mean) is damped by this share,
    melt_hold: float = 0.5  # temperatures above 0 C are scaled by this (as climate.compute),
    ice_absorb: float = 0.2  # and it feels this share of an insolation change (it absorbs little) ...
    absorb_km: float = 600.0  # ... mixed over this scale (km; the air mass), 0 = locally (wider pulls the
    # open sea's full absorption onto coastal ice: Earth's Eemian-like start then melts +25 m in 10 kyr)
    bright_smb: float = 0.5  # m/yr: bright where snow outlasts the summer, bare where it loses this much ...
    bare_share: float = 0.3  # ... and bare ice keeps this share of the snow's effects
    albedo_share: float = 0.2  # thick ice is this x climate.TUNE['ice_cooling'] colder all year ...
    albedo_h: float = 800.0  # ... in full from this thickness (m)
    anchor_max: float = 15.0  # C: largest cooling that keeps the starting ice from melting (start_anchor) ...
    anchor_rings: int = 3  # ... spread this many cells beyond it
    # global feedbacks
    co2_cool: float = 2.5  # C global cooling per 120 m of sea level locked in extra ice (CO2 drawdown) ...
    co2_max: float = 1.0  # ... saturating at this many times that (glacial CO2 bottoms out, Earth ~180 ppm)
    start: str = "auto"  # where the start sits in the ice-age cycle: 'interglacial' (Earth today: the CO2
    # and ice-albedo feedbacks have their full room to a glacial maximum) or 'average' (a run's moment:
    # its ice is the mean extent over the cycles and its dT already has that ice's albedo and part of
    # the glacial CO2 drop, so only average_room of each cap is left); 'auto': interglacial for Earth
    average_room: float = 0.5  # (Earth: 230 ppm on average over the last cycles, 280 interglacial, 185 glacial)
    co2_lag: float = 3.0  # kyr: CO2 follows the ice this slowly
    ice_albedo: float = 0.75  # C global cooling per 3% of the surface newly under ice (the local
    # effect is already in the ice surface's own climate; the main run uses 1.5 for both) ...
    ice_albedo_max: float = 2.0  # ... at most this many C
    precip_k: float = 0.07  # rain ~ exp(precip_k * dT) (Clausius-Clapeyron)
    # mass balance
    pdd_sigma: float = 5.0  # C: day-to-day spread of temperature around the monthly mean
    ddf_snow: float = 3.0  # mm w.e. melted per positive degree-day, snow
    ddf_ice: float = 8.0  # ... ice
    refreeze: float = 0.6  # share of snowmelt that refreezes in the snowpack
    # flow, bed, sea
    flow_a: float = 1e-16  # Pa^-3 yr^-1: Glen's rate factor (~-10 C ice) ...
    enhancement: float = 3.0  # ... times this (common for ice-age ice sheets; also stands in for sliding)
    d_cap: float = 3e8  # m2/yr: cap on the ice diffusivity (unresolved steep margins)
    cfl: float = 0.15  # explicit time step safety factor
    iso_ratio: float = 0.3  # bedrock sinks this x ice thickness (ice/mantle density) ...
    iso_tau: float = 3.0  # ... with this e-folding time (kyr)
    calving: float = 1.0  # per yr: calving speed (m/yr) per m of water depth at a marine ice front


# --------------------------------------------------------------------------
# Orbit and insolation
# --------------------------------------------------------------------------
def orbit_phases(p: TZParams, seed: int, earth: bool = False) -> np.ndarray:
    """Phases (deg) of obliquity, perihelion longitude at t=0, the 100 kyr
    and 405 kyr eccentricity terms."""
    mode = ("eemian" if earth else "seed") if p.phases == "auto" else p.phases
    if mode == "zero":
        return np.zeros(4)
    if mode == "eemian":  # (405 kyr term at 0: eccentricity ~0.042, as at 127 ka; both peaks gave 0.052)
        return np.array([0.0, 90.0, 0.0, 90.0])
    if mode == "seed":
        return np.random.default_rng([seed, 7919]).uniform(0, 360, 4)
    return np.array([float(x) for x in p.phases.split(",")])


def orbit_at(t_kyr: float, p: TZParams, tilt: float, ph: np.ndarray) -> tuple[float, float, float]:
    """(obliquity deg, eccentricity, longitude of perihelion deg) at t."""
    r = np.radians
    obl = tilt + p.obliquity_amp * math.cos(2 * math.pi * t_kyr / p.obliquity_period + r(ph[0]))
    ecc = p.ecc_mean + p.ecc_100 * math.cos(2 * math.pi * t_kyr / 100.0 + r(ph[2])) \
        + p.ecc_400 * math.cos(2 * math.pi * t_kyr / 405.0 + r(ph[3]))
    peri = (ph[1] + 360.0 * t_kyr / p.precession_period) % 360.0
    return obl, max(ecc, 0.0), peri


BAND_DEG = 1.0
BAND_LAT = np.arange(-90 + BAND_DEG / 2, 90, BAND_DEG)


def insolation(obl: float, ecc: float, peri: float, lat=BAND_LAT) -> np.ndarray:
    """Daily-mean insolation (W/m2) at each latitude and the middle of each
    of 12 equal-time months, month 0 starting at the March equinox.
    peri: true longitude of the perihelion from that equinox (Earth today
    ~283 deg: early January). (Berger 1978.)"""
    e, w = ecc, np.radians(peri)
    # time -> true longitude via Kepler's equation; the equinox (true
    # longitude 0) is at true anomaly -w
    v_eq = -w
    E_eq = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(v_eq / 2))
    M_eq = E_eq - e * np.sin(E_eq)
    M = M_eq + 2 * np.pi * (np.arange(12) + 0.5) / 12
    E = M.copy()
    for _ in range(8):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    v = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    lam = v + w
    dist2 = ((1 + e * np.cos(v)) / (1 - e * e)) ** 2  # (mean distance / distance)^2
    dec = np.arcsin(np.sin(np.radians(obl)) * np.sin(lam))
    phi = np.radians(lat)[:, None]
    cos_h0 = np.clip(-np.tan(phi) * np.tan(dec)[None, :], -1, 1)
    h0 = np.arccos(cos_h0)
    q = S0 / np.pi * dist2[None, :] * (h0 * np.sin(phi) * np.sin(dec)[None, :]
                                        + np.cos(phi) * np.cos(dec)[None, :] * np.sin(h0))
    return np.maximum(q, 0.0)


# --------------------------------------------------------------------------
# Grid geometry for finite volumes
# --------------------------------------------------------------------------
_GEO = {}


def geometry(grid: Grid) -> dict:
    """Per cell: area (m2). Per directed edge (CSR order): centre distance
    and shared side length (m), unit tangent toward the neighbour. Cached."""
    key = (id(grid), grid.n)
    if key in _GEO:
        return _GEO[key]
    n, p = grid.n, grid.centers
    src = np.repeat(np.arange(n), np.diff(grid.nbr_off))
    dst = grid.nbr_idx
    dist = np.arccos(np.clip((p[src] * p[dst]).sum(1), -1, 1)) * R_M
    u = p[dst] - p[src]
    u -= (u * p[src]).sum(1, keepdims=True) * p[src]
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    # the side between two cells joins the two triangle centroids (corners)
    # of the two icosphere triangles that contain both of them
    f = grid.faces
    pairs = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    pairs.sort(1)
    face = np.tile(np.arange(len(f)), 3)
    k = pairs[:, 0].astype(np.int64) * n + pairs[:, 1]
    o = np.argsort(k, kind="stable")
    k, face = k[o], face[o]
    ukeys, c1, c2 = k[0::2], face[0::2], face[1::2]
    side = np.arccos(np.clip((grid.corners[c1] * grid.corners[c2]).sum(1), -1, 1)) * R_M
    ek = np.minimum(src, dst).astype(np.int64) * n + np.maximum(src, dst)
    elen = side[np.searchsorted(ukeys, ek)]
    # cell area: fan of triangles from the centre over its ordered corners
    deg = np.diff(grid.nbr_off)
    cc = np.zeros((n, 7), np.int64)
    for i, cs in enumerate(grid.cell_corners):
        cc[i, :len(cs)] = cs
        cc[i, len(cs):] = cs[0]
    a = grid.corners[cc[:, :-1]] - p[:, None, :]
    b = grid.corners[cc[:, 1:]] - p[:, None, :]
    area = 0.5 * np.linalg.norm(np.cross(a, b), axis=2).sum(1)
    area *= 4 * np.pi / area.sum() * R_M**2
    assert (deg >= 5).all()
    g = dict(area=area, dist=dist, elen=elen, ux=u[:, 0].copy(), uy=u[:, 1].copy(), uz=u[:, 2].copy(),
             d2min=float(dist.min()) ** 2)
    if len(_GEO) > 4:
        _GEO.clear()
    _GEO[key] = g
    return g


# --------------------------------------------------------------------------
# Sources: a run at some moment, or the real Earth
# --------------------------------------------------------------------------
def source_from_run(run_dir: Path, at: float) -> dict:
    """Elevation (m above the run's sea level, without ice), ice (m), the
    global temperature offset dT, tilt and the frozen geology at `at` Myr,
    from the stored keyframe nearest to `at` (as timeline.world_from_frame:
    no replay; ice to 20 m, dT to 0.1 C)."""
    run, arr = T.load_frames(run_dir, ("elevation", "ice", *STATIC))
    if run.get("kind") == "timezoom":
        raise SystemExit("that's a time zoom already; give its source run")
    m = run["meta"]
    times = np.array([f["t"] for f in run["frames"]])
    if not times.min() - 1e-9 <= at <= times.max() + 1e-9:
        raise SystemExit(f"--at must be between {times.min():g} and {times.max():g}")
    i = int(np.argmin(np.abs(times - at)))
    fr = run["frames"][i]
    if "sea_level_m" not in fr["stats"]:
        raise SystemExit(f"run {run_dir.name} is too old (its keyframes have no climate)")
    return {"source_run": run.get("id", run_dir.name), "source_name": run["name"], "seed": m["seed"],
            "level": m["level"], "tilt": m["params"].get("tilt", 23.4), "params": m["params"],
            "grid": build_grid(m["level"]), "at": float(fr["t"]),
            "elev": T.frame(run, arr, "elevation", i).astype(float),
            "ice": T.frame(run, arr, "ice", i).astype(float), "dT": fr["stats"]["global_temp_c"] - 14.5,
            "sea_level": fr["stats"]["sea_level_m"], "static": {k: T.frame(run, arr, k, i) for k in STATIC},
            "hotspots": fr["hotspots"], "volcanoes": fr["volcanoes"]}


def source_from_sim(sim, name: str = "in-memory simulation") -> dict:
    """The same, from a tectonics.Simulation in memory (exact, no keyframe)."""
    snap = sim.snapshot()
    return {"source_run": "sim", "source_name": name, "seed": sim.seed, "level": sim.grid.level,
            "tilt": sim.params.tilt, "params": asdict(sim.params), "grid": sim.grid, "at": float(sim.t),
            "elev": snap.elevation.astype(float), "ice": snap.ice.astype(float), "dT": float(sim.dT),
            "sea_level": float(sim.sea_level),
            "static": {"plate": snap.plate, "crust": snap.continental, "crust_age": snap.age,
                       "plate_boundary": snap.boundary},
            "hotspots": [[round(a, 1), round(b, 1)] for a, b in snap.hotspots],
            "volcanoes": T.active_volcanoes(snap.volcanoes)}


def source_earth(level: int = 6) -> dict:
    """Today's Earth (tools/earth_data.py: ETOPO1 elevation and ice) at dT=0."""
    from tools.earth_data import earth_on_grid
    grid = build_grid(level)
    d = earth_on_grid(grid)
    elev, ice = d["elev"].astype(float), d["ice"].astype(float)
    # ETOPO1 counts the floating ice shelves (Ross, Ronne...) as land with
    # their bed floored at 1 m (earth_data); they aren't modelled here, so
    # they become sea (thin ice on a floored bed, low surface)
    shelf = (ice > 0) & (elev <= 1.5) & (elev + ice < 200)
    elev = np.where(shelf, -500.0, elev)
    land = elev > 0
    return {"source_run": "earth", "source_name": "Earth (ETOPO1)", "seed": 0, "level": level, "tilt": 23.44,
            "params": {"tilt": 23.44}, "grid": grid, "at": 0.0, "elev": elev, "ice": np.where(land, ice, 0.0),
            "dT": 0.0, "sea_level": 0.0,
            "static": {"plate": np.zeros(grid.n), "crust": land, "crust_age": np.zeros(grid.n),
                       "plate_boundary": np.zeros(grid.n)},
            "hotspots": [], "volcanoes": [],
            "obs": {k: d[f"obs_{k}"].astype(float) for k in ("t_warm", "t_cold", "p_jul", "p_jan")}}


# Earth's orbit today: obliquity 23.44 deg, eccentricity 0.0167, perihelion
# 283 deg from the March equinox (early January)
EARTH_TODAY = dict(obl=23.44, ecc=0.0167, peri=283.0)


# --------------------------------------------------------------------------
# The simulation
# --------------------------------------------------------------------------
def simulate(src: dict, kyr: float = 1000.0, step: float = 0.5, every: float = 2.0,
             params: TZParams | None = None, progress=False) -> dict:
    """Run the time zoom in memory. progress: True prints a line every 5%,
    or a function(fraction, message) gets them. Returns {"frames": [per-frame dicts:
    t (kyr), stats], "data": {layer: (frames, n) arrays}, "series": per-step
    sea level / ice volume / orbit, "params", "runtime_s"}."""
    t_start = time.time()
    p = params or TZParams()
    g: Grid = src["grid"]
    n = g.n
    G = geometry(g)
    area = G["area"]
    lat = g.lat
    north = lat >= 0
    band = np.clip(((lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    tilt = float(src["tilt"])
    ph = orbit_phases(p, int(src["seed"]) * 1000 + int(round(src["at"])), src["source_run"] == "earth")
    ref = p.orbit_ref if p.orbit_ref != "auto" else ("today" if src["source_run"] == "earth" else "mean")
    start = p.start if p.start != "auto" else ("interglacial" if src["source_run"] == "earth" else "average")
    if start not in ("interglacial", "average"):
        raise SystemExit(f"start must be interglacial, average or auto, not {p.start!r}")
    room = 1.0 if start == "interglacial" else p.average_room  # share of the feedback caps left
    if ref == "start":
        q_ref = insolation(*orbit_at(0.0, p, tilt, ph))
    elif ref == "today":
        q_ref = insolation(**EARTH_TODAY)
    else:
        q_ref = insolation(tilt, 0.0, 0.0)
    # polar amplification of a global temperature change (as climate.compute: 0.5x tropics .. 1.5x poles)
    amp = climate.temperature(g, np.zeros(n), 0.5, 1.5)
    flt = 1 - RHO_I / RHO_W
    gamma = 2 * p.flow_a * p.enhancement * (RHO_I * 9.81) ** 3 / 5

    # state: bedrock relative to the starting sea level, its ice-free rest
    # height (the start is taken as isostatically settled), ice, sea level
    elev0 = np.asarray(src["elev"], float)
    H = np.where(elev0 > 0, np.asarray(src["ice"], float), 0.0)
    bed = elev0.copy()
    bed_rest = bed + p.iso_ratio * H
    sl = 0.0
    ocean_area = float(area[elev0 <= 0].sum())
    V0 = float((H * area).sum())

    bed0 = bed.copy()

    def above_flotation(sl_):
        """m3 of water equivalent the ice takes from the sea (the usual
        ice-sheet bookkeeping, Goelzer et al. 2020): the grounded ice above
        flotation (ice grounded below sea level only stands in for sea water
        it pushed out, so filling a marine basin with ice lowers the sea far
        less than its volume would) in ocean water, plus the room the bed's
        sinking made below sea level (where ice presses an inland bed below
        the sea, the ice under that level does take water out of the sea)."""
        vaf = float((np.maximum(H - np.maximum(sl_ - bed, 0.0) * (RHO_W / RHO_I), 0.0) * area).sum())
        pov = float(((np.maximum(-bed, 0.0) - np.maximum(-bed0, 0.0)) * area).sum())
        return RHO_I / RHO_W * vaf + pov

    Vaf0 = above_flotation(0.0)
    ice_frac0 = float((H > 1).mean())
    dT_run = float(src["dT"])
    co2 = 0.0  # C, the lagged CO2 part of the global change

    out = {k: [] for k in LAYERS}
    frames, series, flows = [], [], []  # flows: accumulation, ablation, calving, NH net (Gt/yr) per step
    budget = {"smb": 0.0, "calved": 0.0}  # m3 of ice gained / lost
    n_steps = int(round(kyr / step))
    keep = max(1, int(round(every / step)))
    refresh = max(1, int(round(p.climate_every / step)))
    fields_ = {}
    smb, t_ann, t_warm, t_cold, p_scale = (np.zeros(n) for _ in range(5))
    nsub_total = 0
    t_compute = 0.0

    def grounded_surface():
        """Surface height above the current sea level (ice included where
        grounded; the sea floor elsewhere) and the grounded-ice mask."""
        grounded = (H > 0) & (bed + H > sl + flt * H)
        surf = np.where(grounded, bed + H, bed) - sl
        return surf, grounded

    melt_ref = {"H": H.copy(), "t": 0.0}

    def meltwater(t_kyr):
        """Fresh water from the ice the sheets have lost since the last full
        climate (m/yr of water per cell, where they thinned; the net loss
        over the planet, nothing while they grow). The ocean's overturning
        feels it (climate.compute's melt)."""
        yrs = (t_kyr - melt_ref["t"]) * 1000.0
        dv = (H - melt_ref["H"]) * area
        melt_ref.update(H=H.copy(), t=t_kyr)
        loss = np.maximum(-dv, 0.0)
        net = max(-float(dv.sum()), 0.0)
        if yrs <= 0 or net <= 0 or loss.sum() <= 0:
            return None
        return RHO_I / RHO_W * loss * (net / loss.sum()) / area / yrs

    def full_climate(dTg):
        nonlocal t_compute
        t0 = time.time()
        surf, _ = grounded_surface()
        # (the overturning carries on from the last full climate's state)
        c = climate.compute(g, surf, dT_run + dTg, tilt, melt=meltwater(t_kyr), moc_start=fields_.get("moc"))
        fields_["moc"] = c["moc_state"]
        fields_["moc_sv"] = (float(c["overturning"][lat >= 0].sum()), float(c["overturning"][lat < 0].sum()))
        t_compute += time.time() - t0
        if p.baseline == "obs" and "bias" not in fields_:
            fields_["bias"] = obs_bias(c)
        tw, tc, pj, pn = c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"]
        if "bias" in fields_:
            b = fields_["bias"]
            tw, tc, pj, pn = tw + b["t_warm"], tc + b["t_cold"], pj * b["p_jul"], pn * b["p_jan"]
        new = dict(t_mean=0.5 * (tw + tc), half=0.5 * np.maximum(tw - tc, 0), p_jul=pj, p_jan=pn,
                   s0=np.maximum(surf, 0), dTg0=dTg)
        # the steps until the next refresh blend from the last one to this one, so the climate
        # (snowfall above all) changes smoothly instead of jumping at each refresh
        fields_["prev"], fields_["next"] = fields_.get("next", new), new
        fields_.update(new)

    def blend(w):
        """The climate fields a share w (0..1) of the way from the last full climate to the newest."""
        a, b = fields_["prev"], fields_["next"]
        fields_.update({k: (1 - w) * a[k] + w * b[k] for k in b})

    def obs_bias(c):
        """Observed minus modelled climate at the start (temperatures: a
        difference, rain: a ratio), where observed and not under the
        starting ice (the model's own ice-sheet climate is used there)."""
        if "obs" not in src:
            raise SystemExit("baseline=obs needs observations (only the Earth source has them)")
        o, w = src["obs"], 1 - np.clip(H / p.albedo_h, 0, 1)
        b = {}
        for k in ("t_warm", "t_cold"):
            b[k] = np.where(np.isfinite(o[k]), o[k] - c[k], 0.0) * w
        for k in ("p_jul", "p_jan"):
            r = np.clip(o[k] / np.maximum(c[k], 1.0), 0.2, 5.0)
            b[k] = np.where(np.isfinite(o[k]), r ** w, 1.0)
        return b

    def record(t_kyr, orb, dq65, dTg):
        surf, grounded = grounded_surface()
        land = surf > 0
        ice = np.where(grounded, H, 0.0)
        precip = 0.5 * (fields_["p_jul"] + fields_["p_jan"]) * p_scale
        k = climate.koppen(surf, t_ann, t_warm, t_cold, precip, fields_["p_jul"] * p_scale,
                           fields_["p_jan"] * p_scale, lat, np.where(land, ice, 0.0))
        for name, v in (("elevation", surf), ("ice", ice), ("temperature", t_ann), ("climate", k)):
            out[name].append(S.encode(v, LAYERS[name]))
        vol = float((H * area).sum())
        frames.append({"t": round(t_kyr, 3), "stats": stats(t_kyr, surf, ice, vol, orb, dq65, dTg)})

    def stats(t_kyr, surf, ice, vol, orb, dq65, dTg):
        land = surf > 0
        lab, nlab = g.components(land)
        sizes = np.bincount(lab[lab >= 0], minlength=1) if nlab else np.array([0])
        return {"t": round(t_kyr, 3), "plates": int(len(np.unique(src["static"]["plate"]))),
                "land_pct": round(100 * land.mean(), 1), "landmasses": int((sizes >= 3).sum()),
                "largest_landmass_pct": round(100 * sizes.max() / n, 1), "max_elev_m": int(surf.max()),
                "global_temp_c": round(14.5 + dT_run + dTg, 2),
                "sea_level_m": round(src["sea_level"] + sl, 1), "sea_level_change_m": round(sl, 2),
                "ice_pct": round(100 * float((ice > 1).mean()), 2),
                "ice_volume_mkm3": round(vol / 1e15, 3),
                "ice_sea_equiv_mkm3": round(above_flotation(sl) / 1e15, 3),  # m3 of sea water the ice holds
                "max_ice_m": int(ice.max()),
                "obliquity": round(orb[0], 3), "eccentricity": round(orb[1], 4),
                "perihelion": round(orb[2], 1), "precession_index": round(orb[1] * math.sin(math.radians(orb[2])), 4),
                "insol_65n_jul_anom": round(dq65, 1), "dT_global": round(dTg, 2),
                "overturning_north_sv": round(fields_["moc_sv"][0], 1),
                "overturning_south_sv": round(fields_["moc_sv"][1], 1),
                "mean_speed_cmyr": 0, "max_speed_cmyr": 0}

    i65 = int(np.argmin(np.abs(BAND_LAT - 65)))
    anchor = np.zeros(n)  # C, fixed per-cell correction under the starting ice (see start_anchor)

    def start_anchor(year, dt_b, iced):
        """The starting ice is taken to be in balance with the starting
        climate (for a run: the main model put it where its summers stay
        cold; for Earth: it's there). Where this model's mass balance (mean
        orbit) would melt it anyway, those cells get the smallest cooling
        (0.5 C steps, at most anchor_max) that lets snow outlast the summer.
        Mostly it makes up for the climate model's ice-free seasons being too
        warm over big polar ice sheets. Fixed for the whole run."""
        todo = iced.copy()
        z = np.zeros_like(q_ref)
        for off in np.arange(0.0, p.anchor_max + 1e-9, 0.5):
            anchor[todo] = -off  # (the cells still melting try the next step; rain isn't changed)
            year(dt_b, z, 1.0)
            todo &= smb < 0
            if not todo.any():
                break
        # a climate bias is regional: spread it a few rings beyond the ice
        # (each new cell: the mean of its corrected neighbours), so ice
        # flowing out of its starting cells doesn't meet a different climate
        a = anchor.copy()
        has = iced.copy()
        src_ = np.repeat(np.arange(n), np.diff(g.nbr_off))
        for _ in range(p.anchor_rings):
            tot = np.bincount(src_, weights=np.where(has, a, 0.0)[g.nbr_idx], minlength=n)
            cnt = np.bincount(src_, weights=has[g.nbr_idx].astype(float), minlength=n)
            new = ~has & (cnt > 0)
            a[new] = tot[new] / cnt[new]
            has |= new
        return a

    for s_no in range(n_steps + 1):
        t_kyr = s_no * step
        orb = orbit_at(t_kyr, p, tilt, ph)
        dq = insolation(*orb) - q_ref
        # global temperature: CO2 follows the ice volume (lagged), ice albedo follows its area
        excess = -sl / 120.0  # 1 = an Earth-LGM-sized extra ice volume
        co2 += (1 - math.exp(-step / p.co2_lag)) * (-p.co2_cool * float(np.clip(excess, -0.5, p.co2_max * room)) - co2)
        dTg = co2 - float(np.clip(p.ice_albedo * ((H > 1).mean() - ice_frac0) / 0.03, -p.ice_albedo_max,
                                  p.ice_albedo_max * room))
        if s_no % refresh == 0:
            full_climate(dTg)
        blend((s_no % refresh) / refresh)
        surf, grounded = grounded_surface()
        land = surf > 0
        dt_wet = amp * (dTg - fields_["dTg0"])
        dt_base = -climate.LAPSE * (np.maximum(surf, 0) - fields_["s0"]) + dt_wet
        f_ice = np.clip(np.where(grounded, H, 0) / p.albedo_h, 0, 1)
        f_alb = np.clip(np.where(grounded, H, 0) / p.snow_h, 0, 1)  # perennial snow is bright from the start

        def year(dt_b, dq_, bright):
            f_snow = f_alb * (p.bare_share + (1 - p.bare_share) * bright)
            # bright snow absorbs little of an insolation change, but the air over it also brings
            # what the surroundings absorbed: the response is mixed over an air mass (absorb_km)
            absorb = 1 - f_snow * (1 - p.ice_absorb)
            if p.absorb_km > 0:
                absorb = climate.smooth_big(g, absorb, p.absorb_km)
            k_orb = np.where(land, p.insol_k, p.insol_k * p.insol_sea) * absorb
            climate_step(land, north, fields_["t_mean"] + anchor, fields_["half"], fields_["p_jul"],
                         fields_["p_jan"], dt_b, dt_wet, k_orb, band, dq_, f_ice, f_snow,
                         climate.TUNE["ice_cooling"] * p.albedo_share, p.summer_damp, p.melt_hold, p.pdd_sigma,
                         p.ddf_snow, p.ddf_ice, p.refreeze, p.precip_k, smb, t_ann, t_warm, t_cold, p_scale)
            return f_snow

        if s_no == 0:
            anchor[:] = start_anchor(year, dt_base, H > 0)
        # snow-covered (bright) where last year's snow outlasted the summer
        f_snow = year(dt_base, dq, np.clip(1 + smb / p.bright_smb, 0, 1) if s_no else 1.0)
        if s_no % keep == 0:
            record(t_kyr, orb, float(dq[i65, 3] + dq[i65, 4]) / 2, dTg)
        series.append((t_kyr, sl, float((H * area).sum()) / 1e15, dTg, *orb))
        if s_no == n_steps:
            break
        dt = step * 1000.0  # yr
        # 1) mass balance (not below zero thickness)
        h_new = np.where(land, np.maximum(H + smb * dt, 0.0), H)
        dv = (h_new - H) * area
        budget["smb"] += float(dv.sum())
        gt = RHO_I / 1e12 / dt  # m3 per step -> Gt per yr
        H[:] = h_new
        # 2) flow
        active = np.flatnonzero(dilate(H > 0, g.nbr_off, g.nbr_idx, 2))
        if len(active):
            nsub_total += sia_flow(H, bed, sl, active, g.nbr_off, g.nbr_idx, G["dist"], G["elen"], G["ux"],
                                   G["uy"], G["uz"], area, gamma, p.d_cap, dt, p.cfl, flt, G["d2min"])
        # 3) the sea: floating ice breaks off; grounded marine fronts calve
        depth = sl - bed
        floating = (H > 0) & (H * RHO_I < depth * RHO_W)
        lost = np.where(floating, H, 0.0)
        H[floating] = 0.0
        marine = (H > 0) & (depth > 0)
        if marine.any():
            open_sea = (depth > 0) & (H <= 0)
            nb_open = np.add.reduceat(open_sea[g.nbr_idx], g.nbr_off[:-1]) > 0
            front = marine & nb_open
            frac = np.exp(-p.calving * depth * dt / np.sqrt(area))
            lost += np.where(front, H * (1 - frac), 0.0)
            H[front] *= frac[front]
        budget["calved"] += float((lost * area).sum())
        flows.append((float(dv[dv > 0].sum()) * gt, float(-dv[dv < 0].sum()) * gt, float((lost * area).sum()) * gt,
                      float(dv[north].sum()) * gt))
        # 4) isostasy
        bed += (bed_rest - p.iso_ratio * H - bed) * (1 - math.exp(-step / p.iso_tau))
        # 5) sea level from the ice volume
        sl = -(above_flotation(sl) - Vaf0) / ocean_area
        if progress and (s_no + 1) % max(1, n_steps // 20) == 0:
            msg = (f"{t_kyr + step:7.1f} kyr  sea level {sl:7.1f} m  ice {100 * (H > 1).mean():5.2f}%  "
                   f"dT {dTg:+5.2f}  [{time.time() - t_start:.0f}s]")
            if callable(progress):  # e.g. the server's job progress: (fraction done, message)
                progress((s_no + 1) / n_steps, " ".join(msg.split()))
            else:
                print("  " + msg, flush=True)

    return {"frames": frames, "data": {k: np.stack(v) for k, v in out.items()},
            "series": np.array(series), "flows": np.array(flows), "params": asdict(p), "phases": ph.tolist(),
            "budget": {**budget, "V0": V0, "V_end": float((H * area).sum()), "ocean_area": ocean_area,
                       "Vaf0": Vaf0, "Vaf_end": above_flotation(sl)},
            "state": {"H": H, "bed": bed, "sl": sl, "smb": smb, "t_warm": t_warm, "t_ann": t_ann,
                      "p_scale": p_scale, "f_snow": f_snow, "p_ann": 0.5 * (fields_["p_jul"] + fields_["p_jan"])},
            "runtime_s": round(time.time() - t_start, 1), "compute_s": round(t_compute, 1),
            "substeps": nsub_total}


# --------------------------------------------------------------------------
# Saving and reporting
# --------------------------------------------------------------------------
def glacial_events(res: dict, g: Grid, min_swing: float = 15.0) -> list[dict]:
    """Glacial maxima and interglacials: turning points of sea level that
    differ from the neighbouring turning points by >= min_swing m."""
    fr = res["frames"]
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    turns, ext, d = [], 0, 0  # zig-zag: a leg ends once sea level turns back by min_swing
    for i in range(1, len(sl)):
        if d == 0:
            if abs(sl[i] - sl[0]) >= min_swing:
                d, ext = (1 if sl[i] > sl[0] else -1), i
        elif (sl[i] - sl[ext]) * d > 0:
            ext = i
        elif abs(sl[i] - sl[ext]) >= min_swing:
            turns.append((ext, d < 0))
            ext, d = i, -d
    ev = []
    for i, lo in turns:
        ice = S.decode(res["data"]["ice"][i], LAYERS["ice"])
        j = int(np.argmax(ice))
        s = fr[i]["stats"]
        ev.append({"t": fr[i]["t"], "kind": "glacial max" if lo else "interglacial",
                   "text": f"sea level {s['sea_level_change_m']:+.0f} m, land ice {s['ice_pct']}% of the surface, "
                           f"thickest {int(ice[j])} m", "lat": round(float(g.lat[j]), 1),
                   "lon": round(float(g.lon[j]), 1)})
    return ev


def save(res: dict, src: dict, kyr: float, step: float, every: float, name: str | None = None) -> Path:
    g: Grid = src["grid"]
    run_id = S.new_id()
    out = S.path_of("run", run_id)
    nf = len(res["frames"])
    arrays = {**{k: res["data"][k] for k in LAYERS},
              **{k: S.encode(np.asarray(src["static"][k])[None, :], S.LAYERS[k]) for k in STATIC}}
    layers = S.write_layers(out, arrays, {**LAYERS, **{k: S.LAYERS[k] for k in STATIC}})
    S.write_grid(g)
    for fr in res["frames"]:
        fr.update(omega={}, hotspots=src["hotspots"], volcanoes=src["volcanoes"])
    label = name or f"time zoom: {src['source_name']} @ {src['at']:g} Myr"
    S.write_json(out / "run.json", {
        "format": "procgen-run/2",
        "kind": "timezoom",
        "id": run_id,
        "name": label,
        "meta": {"kind": "timezoom", "time_unit": "kyr", "source_run": src["source_run"],
                 "source_name": src["source_name"], "at_myr": src["at"], "kyr": kyr, "step_kyr": step,
                 "every": every, "dt": step, "myr": kyr / 1000.0, "frames": nf,
                 "seed": src["seed"], "level": g.level, "cells": g.n,
                 "cell_size_km": round(g.spacing * R_KM),
                 "params": src["params"], "timezoom": res["params"], "orbit_phases_deg": res["phases"],
                 "dT_source": round(src["dT"], 2), "sea_level_source_m": round(src["sea_level"], 1),
                 "static_layers": list(STATIC),
                 "code": code_version(), "generated_in_s": res["runtime_s"], "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{g.level}.json",
        "legend": S.legends(),
        "layers": layers,
        "events": glacial_events(res, g),
        "frames": res["frames"],
    })
    report(out)
    T.update_index()
    return out


def report(run_dir: Path) -> Path:
    """runs/<id>/run.txt: settings, the sea-level / ice / orbit table, ASCII
    maps of the ice at the start, the biggest glacial maximum and the end."""
    run, arr = T.load_frames(run_dir, ("elevation", "ice"))
    m = run["meta"]
    grid = build_grid(m["level"])
    defaults = asdict(TZParams())
    changed = {k: v for k, v in m["timezoom"].items() if defaults.get(k) != v}
    fr = run["frames"]
    out = [f"# Time zoom {run['id']}: {run['name']}  (created {m['created']})",
           f"{m['kyr']:g} kyr after {m['source_run']} @ {m['at_myr']:g} Myr, step {m['step_kyr']:g} kyr, "
           f"frame every {m['every']:g} kyr; level {m['level']} ({m['cells']} cells, ~{m['cell_size_km']} km)",
           f"source: dT {m['dT_source']:+.1f} C, tilt {m['params'].get('tilt', 23.4)}, "
           f"sea level {m['sea_level_source_m']} m; non-default knobs: {json.dumps(changed) if changed else 'none'}",
           f"remake: uv run python -m planet timezoom {m['source_run']} --at {m['at_myr']:g} --kyr {m['kyr']:g} "
           f"--step {m['step_kyr']:g}", "", "## Glacial events"]
    out += [f"  t={e['t']:>7.1f} kyr  {e['kind']:<12} {e['text']}  near ({e['lat']}, {e['lon']})"
            for e in run["events"]] or ["  (none)"]
    out += ["", "## Over time (sea level relative to the start)",
            "    t(kyr)  sea(m)  ice_vol(Mkm3)  ice%  global_T  obliq   ecc     e*sin(w)  65N_Jul_anom(W/m2)"]
    pick = np.unique(np.linspace(0, len(fr) - 1, min(len(fr), 51)).round().astype(int))
    for i in pick:
        s = fr[i]["stats"]
        out.append(f"  {s['t']:>8.1f}  {s['sea_level_change_m']:>6.1f}  {s['ice_volume_mkm3']:>13.2f}  "
                   f"{s['ice_pct']:>4.1f}  {s['global_temp_c']:>8.1f}  {s['obliquity']:>5.2f}  "
                   f"{s['eccentricity']:.4f}  {s['precession_index']:>8.4f}  {s['insol_65n_jul_anom']:>8.1f}")
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    for title, i in (("start", 0), ("largest ice volume", int(np.argmin(sl))), ("end", len(fr) - 1)):
        w = {"grid": grid, "layers": {"elevation": np.where(arr["ice"][i] > 0, 5000,
                                                             T.frame(run, arr, "elevation", i).astype(int))}}
        out += ["", f"## t = {fr[i]['t']:g} kyr ({title}): land ice shown as '#', sea level "
                f"{fr[i]['stats']['sea_level_change_m']:+.0f} m", W.LEGENDS["elevation"],
                W.ascii_map(w, "elevation", 100, 25)]
    path = run_dir / "run.txt"
    path.write_text("\n".join(out) + "\n")
    return path


def timezoom(run_ref: str, at: float = 0.0, kyr: float = 1000.0, step: float = 0.5, every: float = 2.0,
             overrides: dict | None = None, level: int = 6, name: str | None = None,
             progress=True) -> Path:
    """CLI entry: source (a run id, or 'earth') -> simulate -> runs/<id>/.
    progress: as simulate's."""
    known = {f.name for f in fields(TZParams)}
    bad = set(overrides or {}) - known
    if bad:
        raise SystemExit(f"unknown timezoom params: {sorted(bad)}; known: {sorted(known)}")
    params = TZParams(**(overrides or {}))
    src = source_earth(level) if run_ref == "earth" else source_from_run(T.find_run(run_ref), at)
    res = simulate(src, kyr, step, every, params, progress=progress)
    return save(res, src, kyr, step, every, name)
