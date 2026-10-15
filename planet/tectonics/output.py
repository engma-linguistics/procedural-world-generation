"""What the simulation shows the outside world: snapshots and stats."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .. import climate, hydrology, landform, surface
from . import volcanism
from .events import latlon
from .isostasy import MIX
from .plates import CMYR


@dataclass
class Snapshot:
    """World-frame view of the simulation at one instant."""
    t: float
    elevation: np.ndarray  # m, includes trenches
    plate: np.ndarray
    continental: np.ndarray
    age: np.ndarray  # Myr
    boundary: np.ndarray  # +1 converging, -1 diverging, 0 otherwise
    omega: dict[int, list[float]]  # plate id -> angular velocity (rad/Myr)
    rock: np.ndarray  # surface.ROCKS id of the basement
    cover: np.ndarray  # km of sediment on top
    thickness: np.ndarray  # km of crust
    precip: np.ndarray  # mm/yr
    p_jul: np.ndarray  # mm/yr: the July half-year's rate (Apr-Sep)
    p_jan: np.ndarray  # mm/yr: the January half-year's rate (Oct-Mar)
    flow: np.ndarray  # river flow (sum of upstream runoff, cells x m/yr)
    downstream: np.ndarray  # next cell down the river, -1 at the sea
    lake_kind: np.ndarray  # hydrology lake_kind: 0 none, 1 open, 2 closed (salt), 3 salt pan
    lake_depth: np.ndarray  # m of lake water (0 off lakes)
    hotspots: list  # [lat, lon] of each live plume
    volcanoes: list  # arc volcanoes and hotspot vents: rows of volcanism.COLUMNS
    surface: np.ndarray  # surface.ROCKS id of what's exposed (the top stratum, or the basement)
    temperature: np.ndarray  # C, annual mean
    t_warm: np.ndarray  # C, warmest month
    t_cold: np.ndarray  # C, coldest month
    koppen: np.ndarray  # climate.KOPPEN id
    ice: np.ndarray  # m of land ice
    wind: np.ndarray  # (n, 3) annual-mean surface wind, ~1 = a steady trade wind
    current: np.ndarray  # (n, 3) surface ocean current, same scale
    # landform classes and what the zoom needs to draw them (landform.py)
    landform: np.ndarray  # landform.CLASSES id
    landform_age: np.ndarray  # Myr, meaning by class (landform.CLASSES)
    strata_top: np.ndarray  # surface.ROCKS id of the exposed stratum (or the basement)
    strata_top_km: np.ndarray  # km of it (0: basement)
    strata_next: np.ndarray  # surface.ROCKS id under it
    strata_dip: np.ndarray  # deg
    fold_wavelength: np.ndarray  # km (0: not folded)
    rift_strain: np.ndarray  # ln beta of the last rifting (0: never rifted)
    glaciated_myr: np.ndarray  # Myr since last under ice (landform.GLACIATED_NEVER: never)
    # vegetation at the last climate update (vegetation.py; tectonics/earth.update_vegetation)
    vegetation: np.ndarray  # vegetation.TYPES id (0 at sea)
    tree_cover: np.ndarray  # 0..1
    npp: np.ndarray  # g C/m2/yr


def snapshot(sim) -> Snapshot:
    """World-frame copy of everything worth saving or drawing right now."""
    live = np.flatnonzero(sim.plates.alive)
    vrows = volcanism.rows(sim)
    lf = landforms_now(sim, vrows)
    return Snapshot(
        t=sim.t,
        elevation=np.where(sim.w_cont, sim.bed(), sim.bed() + sim.w_trench),  # (under ice: the pressed-down bed)
        plate=sim.plates.label[sim.owner],
        continental=sim.w_cont.copy(),
        age=sim.w_age.copy(),
        boundary=sim.w_boundary.copy(),
        omega={int(sim.plates.label[k]): sim.plates.omega[k].tolist() for k in live},
        rock=sim.w_rock.copy(),
        cover=sim.w_cover.copy(),
        thickness=sim.w_thick.copy(),
        precip=sim.precip.copy() if sim.precip is not None else np.zeros(sim.grid.n),
        p_jul=sim.p_jul.copy() if sim.p_jul is not None else np.zeros(sim.grid.n),
        p_jan=sim.p_jan.copy() if sim.p_jan is not None else np.zeros(sim.grid.n),
        flow=sim.flow.copy(),
        downstream=sim.down.copy(),
        **lakes_now(sim),
        hotspots=[list(latlon(h["pos"])) for h in sim.hotspots],
        volcanoes=vrows,
        surface=surface.surface_rock(sim.w_rock, sim.w_cover, lf["strata_top"], lf["strata_top_km"]),
        **climate_now(sim),
        **lf,
        **vegetation_now(sim),
    )


def vegetation_now(sim) -> dict:
    """The vegetation of the last climate update, on today's land."""
    land = sim.land()
    return dict(vegetation=np.where(land, sim.veg_type, 0).astype(np.uint8),
                tree_cover=np.where(land, sim.tree_cover, 0.0), npp=np.where(land, sim.npp, 0.0))


def landforms_now(sim, vrows) -> dict:
    """The landform classes now (landform.classify on the record)."""
    z = np.zeros(sim.grid.n)
    return landform.classify(sim.grid, sim.t, sim.w_elev, sim.w_cont, sim.w_rock, sim.w_cover, sim.w_extra[:, MIX],
                             sim.w_rec, sim.w_lith, sim.w_age, z if sim.precip is None else sim.precip,
                             z if sim.temp is None else sim.temp, vrows, sim.owner,
                             t_warm=sim.t_warm, t_cold=sim.t_cold, tilt=sim.params.tilt)


def lakes_now(sim) -> dict:
    """The lakes of the last erosion step (hydrology.lakes on the terrain
    before it eroded). Like worlds (hydrology.rivers_and_lakes), no lakes
    on land ice, nor on cells the step left below sea level."""
    ok = (sim.bed() > 0) & (sim.ice <= 0)
    kind = np.where(ok, sim.lake_kind, 0).astype(np.int8)
    wet = (kind == hydrology.OPEN_LAKE) | (kind == hydrology.CLOSED_LAKE)
    return dict(lake_kind=kind, lake_depth=np.where(wet, sim.lake_depth, 0.0))


def climate_now(sim) -> dict:
    """Climate fields for a snapshot. They're updated every climate_every
    Myr; the sea/land pattern may have moved since, so cells that are now
    sea get the sea class and no ice."""
    n = sim.grid.n
    if sim.koppen is None:
        z = np.zeros(n)
        z3 = np.zeros((n, 3))
        return dict(temperature=z, t_warm=z, t_cold=z, koppen=np.full(n, climate.SEA_CLASS), ice=z,
                    wind=z3, current=z3)
    land = sim.land()
    k = climate.koppen(np.where(land, np.maximum(sim.bed(), 1.0), sim.bed()), sim.temp, sim.t_warm, sim.t_cold, sim.precip, sim.p_jul,
                       sim.p_jan, sim.grid.lat, np.where(land, sim.ice, 0.0))
    return dict(temperature=sim.temp.copy(), t_warm=sim.t_warm.copy(), t_cold=sim.t_cold.copy(),
                koppen=k, ice=np.where(land, sim.ice, 0.0), wind=sim.wind.copy(),
                current=np.where(land[:, None], 0.0, sim.current))


def stats(sim) -> dict:
    """A few headline numbers for progress lines and run summaries."""
    g = sim.grid
    land = sim.land()
    lab, nlab = g.components(land)
    sizes = np.bincount(lab[lab >= 0], minlength=1) if nlab else np.array([0])
    v = np.linalg.norm(sim.velocity(), axis=1) * CMYR
    return {
        "t": sim.t,
        "plates": int(sim.plates.alive.sum()),
        "land_pct": round(100 * land.mean(), 1),
        "continental_pct": round(100 * sim.w_cont.mean(), 1),
        "landmasses": int((sizes >= 3).sum()),
        "largest_landmass_pct": round(100 * sizes.max() / g.n, 1),
        "max_elev_m": int(sim.bed().max()),
        "global_temp_c": round(14.5 + sim.dT, 1),
        "co2": round(float(sim.co2), 3),
        "sea_level_m": round(sim.sea_level, 1),
        "ice_pct": round(100 * float((sim.ice > 0).mean()), 1),
        "mean_speed_cmyr": round(float(v.mean()), 2),
        "max_speed_cmyr": round(float(v.max()), 2),
    }
