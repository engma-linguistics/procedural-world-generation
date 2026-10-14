"""What the simulation shows the outside world: snapshots and stats."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .. import climate, surface
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
    flow: np.ndarray  # river flow (sum of upstream runoff, cells x m/yr)
    downstream: np.ndarray  # next cell down the river, -1 at the sea
    hotspots: list  # [lat, lon] of each live plume
    volcanoes: list  # [lat, lon] of each active arc volcano
    surface: np.ndarray  # surface.ROCKS id of what's exposed (basement or its sediment cover)
    temperature: np.ndarray  # C, annual mean
    t_warm: np.ndarray  # C, warmest month
    t_cold: np.ndarray  # C, coldest month
    koppen: np.ndarray  # climate.KOPPEN id
    ice: np.ndarray  # m of land ice
    wind: np.ndarray  # (n, 3) annual-mean surface wind, ~1 = a steady trade wind
    current: np.ndarray  # (n, 3) surface ocean current, same scale


def snapshot(sim) -> Snapshot:
    """World-frame copy of everything worth saving or drawing right now."""
    live = np.flatnonzero(sim.plates.alive)
    return Snapshot(
        t=sim.t,
        elevation=np.where(sim.w_cont, sim.w_elev, sim.w_elev + sim.w_trench),
        plate=sim.plates.label[sim.owner],
        continental=sim.w_cont.copy(),
        age=sim.w_age.copy(),
        boundary=sim.w_boundary.copy(),
        omega={int(sim.plates.label[k]): sim.plates.omega[k].tolist() for k in live},
        rock=sim.w_rock.copy(),
        cover=sim.w_cover.copy(),
        thickness=sim.w_thick.copy(),
        precip=sim.precip.copy() if sim.precip is not None else np.zeros(sim.grid.n),
        flow=sim.flow.copy(),
        downstream=sim.down.copy(),
        hotspots=[list(latlon(h["pos"])) for h in sim.hotspots],
        volcanoes=[list(latlon(v["pos"])) for v in sim.volcanoes],
        surface=surface.surface_rock(sim.w_rock, sim.w_cover, sim.w_extra[:, MIX]),
        **climate_now(sim),
    )


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
    land = sim.w_elev > 0
    k = climate.koppen(sim.w_elev, sim.temp, sim.t_warm, sim.t_cold, sim.precip, sim.p_jul,
                       sim.p_jan, sim.grid.lat, np.where(land, sim.ice, 0.0))
    return dict(temperature=sim.temp.copy(), t_warm=sim.t_warm.copy(), t_cold=sim.t_cold.copy(),
                koppen=k, ice=np.where(land, sim.ice, 0.0), wind=sim.wind.copy(),
                current=np.where(land[:, None], 0.0, sim.current))


def stats(sim) -> dict:
    """A few headline numbers for progress lines and run summaries."""
    g = sim.grid
    land = sim.w_elev > 0
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
        "max_elev_m": int(sim.w_elev.max()),
        "global_temp_c": round(14.5 + sim.dT, 1),
        "sea_level_m": round(sim.sea_level, 1),
        "ice_pct": round(100 * float((sim.ice > 0).mean()), 1),
        "mean_speed_cmyr": round(float(v.mean()), 2),
        "max_speed_cmyr": round(float(v.max()), 2),
    }
