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
ISO_VOLCANO = 350.0  # a narrow volcanic pile is also held up by the stiff plate around it (flexure)
# densities, g/cm3: mantle, sea water; sediment at the surface and deep
# down, compacting over SED_COMPACT_KM of burial (Athy's porosity law)
RHO_MANTLE, RHO_WATER = 3.3, 1.03
SED_TOP, SED_DEEP, SED_COMPACT_KM = 2.1, 2.6, 2.0
K_LAND = 1000.0 / RHO_MANTLE  # m of elevation per km x g/cm3 of buoyancy, in air...
K_SEA = 1000.0 / (RHO_MANTLE - RHO_WATER)  # ...and under water
RHO_CONT = RHO_MANTLE - ISO_LAND / K_LAND  # the crust densities ISO_LAND / ISO_SEA imply: 2.80
RHO_OCEAN = RHO_MANTLE - ISO_SEA / K_SEA  # 2.85


# Extra per-cell numbers carried by every plate (column order):
#   lift  m of broad doming over a plume; it rides away with the plate and
#         decays as the hot mantle under it cools (Hawaii's swell trails
#         ~1000 km down the chain)
#   carb  km of the sediment cover that is carbonate (limestone),
#   lava  km of it that is lava flows (flood basalts, hotspot tracks),
#   evap  km of evaporites (salt, gypsum), coal  km of coal,
#   sand  km of sandstone; the rest of the cover is mud (shale).
# Columns MIX line up with surface.MIX_ROCKS.
EXTRA = ("lift", "carb", "lava", "evap", "coal", "sand")
LIFT, CARB, LAVA, EVAP, COAL, SAND = range(6)
MIX = slice(1, 6)


def isostasy(cont, rock):
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
    sea = np.where(rock == HOTSPOT, ISO_VOLCANO, ISO_SEA)
    return np.where(cont, 250 + ISO_LAND * (thick - CONT_KM),
                    ocean_depth(age) + sea * (thick - OCEAN_KM)) + sediment_lift(cont, rock, sed) + swell


def ocean_depth(age):
    """Half-space cooling: sea floor sinks ~ sqrt(age). (Real fit: 2600 + 345*sqrt(t) m.)"""
    return -np.minimum(2600 + 345 * np.sqrt(np.maximum(age, 0)), 6400)
