"""Time-stepped plate tectonics.

Representation
--------------
Every plate stores its crust on its own private copy of the grid (its
"reference frame") plus a rotation matrix Q saying where that copy currently
sits on the globe. Moving a plate = updating Q; the crust data never gets
resampled, so a plate's interior doesn't blur as it travels.

Each step (Simulation.step):
 1. Rotate each plate by its angular velocity * dt.
 2. Pull: every world cell asks every plate "do you have crust here?"
    (nearest cell of the plate's reference grid, via kernels.locate).
 3. Resolve:  nobody   -> gap -> brand-new ocean floor (a ridge)
              one plate -> that plate owns the cell
              several  -> overlap. Continental crust beats oceanic, young
                          ocean beats old ocean. The loser's crust there is
                          deleted: that's subduction. Continent vs continent
                          is a collision.
 4. Physics on the resulting world map. Every cell carries a crust
    thickness, and elevation follows from it by isostasy (thick crust floats
    higher) plus, for ocean floor, its age (it sinks as it cools). Arcs
    add crust above subducting slabs (Andes, Japan); collisions stack it
    (Himalaya/Tibet), very thick crust flows sideways, erosion removes it
    from high ground, and part of that becomes sediment on the continental
    margins. Continental crust is conserved through all of it, so the
    continents neither leak away nor swell over billions of years.
 5. Forces -> velocities. Plates have no momentum (it's basically very slow
    Stokes flow), so each step the velocity is *solved* from the forces:
    slab pull (dominant), ridge push, collision resistance, basal traction
    from the mantle flowing under the plates, and a small, slowly
    wandering drag term that supplies meandering. The mantle (mantle.py)
    is a temperature anomaly in the world frame: cold where slabs have
    sunk for a long time, warm under continents that sit still; it flows
    from warm to cold, so continents gather over the cold (a
    supercontinent), warm the mantle under them, and are pulled apart.
 6. Events: long collisions weld plates together; plates split when the
    forces on them (including that traction) pull their halves apart,
    along their weakest line and never into continental slivers, or when
    old ocean floor at a passive margin breaks off and starts to sink (new
    subduction); slivers get absorbed.

Modules
-------
  simulation     Simulation: state, the step, the world view
  params         Params
  plates         Plates (all per-plate state), rotations, units
  plate_kernels  numba kernels: resolve ownership, crust flow, ghost cleanup
  motion         plate boundaries; forces -> velocities
  mantle         the mantle's temperature anomaly: slabs, insulation, traction, plumes
  isostasy       crust thickness -> elevation (light, compacting sediment); the per-cell EXTRA columns
  crust          the crust budget: arcs, collisions, accretion, subduction
                 erosion, stretching and rifted margins, crustal flow,
                 continents born, cratons; the thermostats
  volcanism      hotspots (mantle plumes) and arc volcanoes
  earth          mantle heat, global temperature, CO2, sea level, climate,
                 erosion and sediment, reefs
  events         collisions, sutures, slivers, rifts (and the Event log)
  setup          the starting planet
  output         Snapshot, stats

Determinism: all randomness for step s comes from default_rng([seed, s]),
so any step can be reproduced exactly by re-running from t=0.

Units: time in Myr, angular velocity in rad/Myr on the unit sphere,
speeds reported in cm/yr (1 cm/yr = 10 km/Myr), elevation in metres.
"""

from .events import Event
from .isostasy import (BECOMES_CONT_KM, CONT_KM, EXTRA, ISO_LAND, ISO_SEA, ISO_VOLCANO, MAX_KM, MIX, OCEAN_KM,
                       elevation, isostasy, ocean_depth)
from .output import Snapshot
from .params import Params
from .plates import CMYR, P_MAX, Plates, rotation
from .simulation import Simulation

__all__ = ["BECOMES_CONT_KM", "CMYR", "CONT_KM", "EXTRA", "Event", "ISO_LAND", "ISO_SEA", "ISO_VOLCANO", "MAX_KM",
           "MIX", "OCEAN_KM", "P_MAX", "Params", "Plates", "Simulation", "Snapshot", "elevation", "isostasy",
           "ocean_depth", "rotation"]
