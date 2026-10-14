"""Crust thickness -> elevation, and the per-cell columns every plate carries.

Crust thickness (km) and isostasy. Crust floats on the denser mantle like
ice on water: thicker crust stands higher, and for continents ~85% of any
thickening is hidden below as a root (Airy isostasy: 1 km of extra crust
-> ~150 m of extra elevation). 35 km of continental crust sits at ~250 m;
Tibet's ~70 km gives ~5.5 km.
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


def elevation(thick, age, cont, rock, swell):
    """m above sea level (swell: m of plume doming minus the sea level)."""
    sea = np.where(rock == HOTSPOT, ISO_VOLCANO, ISO_SEA)
    return np.where(cont, 250 + ISO_LAND * (thick - CONT_KM),
                    ocean_depth(age) + sea * (thick - OCEAN_KM)) + swell


def ocean_depth(age):
    """Half-space cooling: sea floor sinks ~ sqrt(age). (Real fit: 2600 + 345*sqrt(t) m.)"""
    return -np.minimum(2600 + 345 * np.sqrt(np.maximum(age, 0)), 6400)
