"""Crust thickness -> elevation, and the per-cell columns every plate carries.

Crust thickness (km) and isostasy. Crust floats on the denser mantle like
ice on water: thicker crust stands higher, and for continents ~85% of any
thickening is hidden below as a root (Airy isostasy: 1 km of extra crust
-> ~150 m of extra elevation). 35 km of continental crust sits at ~250 m;
Tibet's ~70 km gives ~5.5 km.

Sediment is lighter than crust: fresh mud and sand are full of water-filled
pores (~2.1 g/cm3), squeezed out as the pile gets buried (~2.6 at 5+ km),
against ~2.8 for crystalline crust. So a km of sediment holds the surface up
more than a km of crust would (sediment_lift), and filling a deep basin
takes ~3x its depth of sediment (as on Earth), not the ~5x crust would.
Compaction here follows the current burial depth (it isn't remembered when
the pile is later eroded down).

Glacial isostasy (PW-189): an ice sheet presses the crust down by about
rho_ice / rho_mantle ~ 0.28 of its thickness (a 3 km sheet: ~830 m, so the
middle of a big sheet's bed often lies below sea level, as Greenland's and
Antarctica's do), spread over a few hundred km by the stiff lithosphere
(flexure: a small cap barely dents it, a continent-wide sheet sinks in
full). After the ice melts the crust rebounds, over ~10 kyr (Hudson Bay
and the Baltic still rise ~1 cm/yr). ice_load is the settled dip; the main
run (Myr steps) takes it at once, the glacial time zoom relaxes toward it
with an e-folding time of a few kyr (an "ELRA" model: elastic lithosphere,
relaxing asthenosphere).
"""

from __future__ import annotations

import numpy as np

from ..surface import HOTSPOT

OCEAN_KM = 7.0  # normal oceanic crust
CONT_KM = 35.0  # normal continental crust
BECOMES_CONT_KM = 20.0  # an arc or sediment pile this thick is continental crust
MAX_KM = 80.0
ISO_LAND = 150.0  # m of elevation per km of crust
ISO_SEA = 200.0  # under water the displaced stuff is water, not air
ISO_VOLCANO = 350.0  # a narrow volcanic pile is also held up by the stiff plate around it (flexure)...
VOLCANO_PILE_KM = 20.0  # ...for its first this many km beyond normal ocean crust (Hawaii's pile: ~10-15 km)
# densities, g/cm3: mantle, sea water; sediment at the surface and deep
# down, compacting over SED_COMPACT_KM of burial (Athy's porosity law)
RHO_MANTLE, RHO_WATER = 3.3, 1.03
SED_TOP, SED_DEEP, SED_COMPACT_KM = 2.1, 2.6, 2.0
K_LAND = 1000.0 / RHO_MANTLE  # m of elevation per km x g/cm3 of buoyancy, in air...
K_SEA = 1000.0 / (RHO_MANTLE - RHO_WATER)  # ...and under water
RHO_CONT = RHO_MANTLE - ISO_LAND / K_LAND  # the crust densities ISO_LAND / ISO_SEA imply: 2.80
RHO_OCEAN = RHO_MANTLE - ISO_SEA / K_SEA  # 2.85


RHO_ICE = 0.917
ICE_SINK = RHO_ICE / RHO_MANTLE  # m the bed sinks per m of ice, once settled (~0.28)
FLEX_KM = 150.0  # km: the lithosphere's flexure spreads an ice load over about this (Gaussian-ish sigma)
BED_FLOOR = 1.0  # m: grounded ice on a bed at or below sea level keeps its cell land (land_view)


def ice_load(grid, ice, ratio=ICE_SINK, km=FLEX_KM):
    """m the bed is pressed down by land ice (m per cell) once settled:
    ratio x the ice thickness, spread by the lithosphere's flexure over
    ~km (the blur keeps the total, so a small cap sinks less than ratio x
    its thickness and its surroundings a little)."""
    from ..climate import smooth  # (climate doesn't import tectonics, but keep the import light)
    ice = np.asarray(ice, float)
    if not (ice > 0).any():
        return np.zeros_like(ice)
    return np.maximum(smooth(grid, ratio * ice, km), 0.0)


SAG_KM = 2.2  # km: thermal subsidence after infinite stretching, air-loaded (McKenzie 1978's ~3.2 km under water)
SAG_TIME = 63.0  # Myr: the stretched lithosphere's cooling time constant (McKenzie)
MOAT_MAX = 2500.0  # m: deepest a moat gets, smoothly (the Ganges foreland's basement is ~4-5 km down under its fill)
ROOT = 1000.0 - ISO_LAND  # m of root per km of extra continental crust (Airy: the part that doesn't show)


def subsidence(grid, thick, cont, rec, t, flexure=0.3, sag=SAG_KM, sag_time=SAG_TIME, km=FLEX_KM):
    """m of tectonic subsidence (< 0) or uplift beyond local (Airy)
    isostasy, per cell (PW-054): what keeps basins sinking as they fill.

    - Flexure: a mountain belt's load is carried by the stiff lithosphere
      over ~km, so the plain beside it is dragged down into a moat (the
      Ganges, Po, Persian Gulf and Alberta foreland basins; between two
      ranges an intermontane basin: Tarim, Fergana). The root Airy puts
      under each cell of thickened continent (ROOT per km of crust beyond
      CONT_KM) is spread over ~km (the same lithosphere as ice_load's), and
      continent standing where the spread root reaches deeper than its own
      sinks by flexure x the difference (smoothly capped at MOAT_MAX). Only the moat is applied: ranges
      keep their Airy height (the crust model makes their thickness), so
      the belt itself isn't held up by the plate.
    - Thermal sag after rifting: a stretched lithosphere starts hot and
      buoyant and sinks as it cools (McKenzie 1978): sag x f(beta) of
      uplift, f = (beta/pi) sin(pi/beta), decaying over sag_time, beta =
      e^rift_strain from the record. Airy isostasy gives the thinned crust's
      final, cold height at once; this adds the hot start, so a rift's
      floor and its margins keep sinking for ~100 Myr after the stretching
      stops (sag basins over old rifts: the North Sea, Paris, Michigan;
      passive margins' thick wedges).
    thick km, cont mask, rec the geological record (record.RECORD columns),
    t Myr now."""
    from ..climate import smooth
    from .record import RIFT_STRAIN, T_RIFT
    out = np.zeros(len(thick))
    if flexure > 0:
        root = np.where(cont, ROOT * np.maximum(thick - CONT_KM, 0.0), 0.0)
        if root.any():
            moat = flexure * np.maximum(smooth(grid, root, km) - root, 0.0) * cont
            out -= MOAT_MAX * np.tanh(moat / MOAT_MAX)
    if sag > 0:
        age = t - rec[:, T_RIFT].astype(float)
        hot = cont & (age >= 0) & (age < 8 * sag_time)
        if hot.any():
            beta = np.exp(np.maximum(rec[hot, RIFT_STRAIN].astype(float), 0.0))
            f = beta / np.pi * np.sin(np.pi / beta)
            out[hot] += 1000.0 * sag * f * np.exp(-age[hot] / sag_time)
    return out


def land_view(elev, ice, floor=BED_FLOOR):
    """(elev, ice, floored) for code that takes land as elevation > 0:
    grounded ice on a bed at or below sea level (a bed pressed down by its
    ice, a marine ice sheet) becomes land with its bed floored at `floor` m
    and the ice thinned to keep the surface (as tools/earth_data.py does
    for Antarctica). ice > 0 means grounded ice (runs and time zooms store
    only that). floored: the mask of the cells changed."""
    elev = np.asarray(elev, float)
    ice = np.asarray(ice, float)
    low = (ice > 0) & (elev < floor)
    return (np.where(low, floor, elev), np.where(low, np.maximum(elev + ice - floor, 0.0), ice), low)


# Extra per-cell numbers carried by every plate (column order):
#   lift  m of broad doming over a plume; it rides away with the plate and
#         decays as the hot mantle under it cools (Hawaii's swell trails
#         ~1000 km down the chain)
#   carb  km of the sediment cover that is carbonate (limestone),
#   lava  km of it that is lava flows (flood basalts, hotspot tracks),
#   evap  km of evaporites (salt, gypsum), coal  km of coal,
#   sand  km of sandstone, tuff  km of volcanic ash and ignimbrite from
#         arcs on continents; the rest of the cover is mud (shale).
# Columns MIX line up with surface.MIX_ROCKS. (The order the cover is
# layered in is in tectonics.record.)
EXTRA = ("lift", "carb", "lava", "evap", "coal", "sand", "tuff")
LIFT, CARB, LAVA, EVAP, COAL, SAND, TUFF = range(7)
MIX = slice(1, 7)
LAVA_MAX_KM = 3.0  # km: the thickest flood-basalt pile on a continent (Siberian Traps ~3.5, Deccan ~2; PW-133)


def iso_rate(cont, rock):
    """m of elevation per km of crust added or removed, per cell."""
    return np.where(cont, ISO_LAND, np.where(rock == HOTSPOT, ISO_VOLCANO, ISO_SEA))


def _k(cont, rock):
    return np.where(cont, K_LAND, K_SEA * np.where(rock == HOTSPOT, ISO_VOLCANO / ISO_SEA, 1.0))


def sediment_density(z):
    """g/cm3 of sediment buried z km deep."""
    return SED_DEEP - (SED_DEEP - SED_TOP) * np.exp(-np.maximum(z, 0) / SED_COMPACT_KM)


def sediment_iso(cont, rock, sed):
    """m of elevation per km of sediment added on top of (or eroded off) a
    pile sed km thick. Adding a layer buries the whole pile deeper, so it
    counts at the density of the pile's base."""
    return _k(cont, rock) * (RHO_MANTLE - sediment_density(sed))


def sediment_lift(cont, rock, sed):
    """m a pile of sed km of sediment stands higher than the same thickness
    of crust would (the integral of the density deficit)."""
    c = np.maximum(sed, 0)
    rho = np.where(cont, RHO_CONT, RHO_OCEAN)
    deficit = (rho - SED_DEEP) * c + (SED_DEEP - SED_TOP) * SED_COMPACT_KM * (1 - np.exp(-c / SED_COMPACT_KM))
    return _k(cont, rock) * deficit


def sediment_km(cover, extra):
    """km of light sediment in the cover: all of it but the lava flows."""
    return np.maximum(cover - extra[:, LAVA], 0)


def elevation(thick, age, cont, rock, swell, sed):
    """m above sea level (swell: m of plume doming minus the sea level;
    sed: km of the crust that is (light) sediment, see sediment_km)."""
    # (a volcanic pile is held up by the plate's flexure only up to the
    # load it can carry, VOLCANO_PILE_KM; crust beyond that floats like
    # any other: PW-172, a 45 km sediment-laden pile stood at 11.5 km)
    extra = thick - OCEAN_KM
    pile = np.where(rock == HOTSPOT, np.clip(extra, 0, VOLCANO_PILE_KM), 0.0)
    return np.where(cont, 250 + ISO_LAND * (thick - CONT_KM),
                    ocean_depth(age) + ISO_SEA * extra + (ISO_VOLCANO - ISO_SEA) * pile) \
        + sediment_lift(cont, rock, sed) + swell


def ocean_depth(age):
    """Half-space cooling: sea floor sinks ~ sqrt(age). (Real fit: 2600 + 345*sqrt(t) m.)"""
    return -np.minimum(2600 + 345 * np.sqrt(np.maximum(age, 0)), 6400)
