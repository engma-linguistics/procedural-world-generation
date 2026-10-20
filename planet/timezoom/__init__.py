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
  main run's ice_albedo rule, as the change from the start). Rain scales
  ~ exp(0.07 dT) with the global and orbital changes (climate.compute
  already dries the air over high domes).
- Ice surfaces: perennial snow is bright, so its summer warmth is damped
  and it feels only a fraction of an insolation change (the snow-albedo
  feedback that lets ice spread); where the year's snow melts away the
  ice is bare and darker and gets more of the summer (which helps it
  melt back). Thick ice is a little colder all year (inversion, katabatic
  winds; ice_cool, 2 C).
- Starting ice: a run's is this mass balance's own extent (earth.ice_sheets);
  Earth's is real, and where the climate model's summer on it is warmer
  than observed the ice surface gets a cooling to the observed summer,
  spread a few cells beyond the ice and applied wherever ice lies there
  (start_anchor; it leaves with the ice, PW-035).
- Mass balance: snow (monthly, where it's below ~0 C) minus melt from
  positive degree days (kernels.climate_step).
- Flow: shallow-ice approximation, nonlinear diffusion with
  D ~ H^5 |grad s|^2 (kernels.sia_flow).
- Isostasy (ELRA: elastic lithosphere, relaxing asthenosphere): the bed
  relaxes with iso_tau (3 kyr) toward its settled dip under the ice,
  iso_ratio x the ice thickness spread by flexure over ~flex_km
  (tectonics.isostasy.ice_load, as the main run), and rebounds after the
  ice is gone. The start is settled (the run's bed is already pressed down
  by its ice).
- Sea: ice the flow carries past the grounding line is an ice shelf
  (PW-367): it floats (no load on the bed, no sea level), spreads under
  its own weight (Weertman 1957; confined, by the buttressing it gives)
  to calve at its own front, melts from below where the sea's winter
  water is above freezing, and breaks up where the air over it is too
  warm for a shelf (shelf_viable). Grounded ice on the sea floor calves
  at a rate ~ water depth where it faces open water (not a shelf:
  shelf_cover, whose shelf holds back `buttress` of its flow across the
  grounding line), or stands in water deeper than calve_depth. Sea level falls by the sea water the ice holds / ocean
  area: 0.89 x the ice above flotation (ice grounded below sea level only
  replaces sea water) plus the room the sinking bed made below sea level
  (Goelzer et al. 2020), so coastlines and land bridges move with the ice.

Output: runs/<id>/ in the run format (timeline.py, store.py) so the viewer
plays it, with time in kyr since the start and run["kind"] = meta["kind"] =
"timezoom". Per-frame layers: elevation (surface incl. ice, relative to
that frame's sea level), ice, temperature, climate. plate / crust /
crust_age / plate_boundary are stored once (shape [1, cells]): geology is frozen.
Frame stats carry sea level, ice volume and the orbit.

Package layout
--------------
params     constants, the per-frame layers, TZParams (the knobs)
sources    source_from_run / source_from_sim / source_earth
geometry   cell areas and edge lengths for the finite volumes
forcing    orbit_anomaly / orbit_k, and Forcing: the global dT from CO2 and ice albedo (PW-440 hooks in here)
fields     ClimateFields: the full climates, blended between refreshes
ice        ice shelves, calving fronts, ice above flotation
kernels    numba: the year's mass balance (climate_step), shallow-ice flow (sia_flow)
sim        simulate(): the stepping loop, one named function per step
events     glacial events, the cycling ice's summer sun
output     save, report
run        timezoom(): the CLI entry
The orbit and insolation maths are planet/orbit.py (shared with icemass).
"""

from __future__ import annotations

from .forcing import orbit_anomaly
from .output import report, save
from .params import LAYERS, STATIC, TZParams
from .run import timezoom
from .sim import simulate
from .sources import source_earth, source_from_run, source_from_sim

__all__ = ["LAYERS", "STATIC", "TZParams", "orbit_anomaly", "report", "save", "simulate", "source_earth",
           "source_from_run", "source_from_sim", "timezoom"]
