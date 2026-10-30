"""Physical constants shared by several modules (one definition each). A planet-wide
number that is the *model's* choice rather than a unit, such as the radius, lives in geo.py."""

from __future__ import annotations

SEC_PER_YR = 3.156e7  # s per year (the model's rounded value)
GRAV = 9.81  # m/s2, surface gravity (Earth)
RHO_ICE = 917.0  # kg/m3, glacier ice
RHO_C_SEA = 4.1e6  # J/m3 per C: sea water's heat capacity
T_REF_C = 14.5  # C: the global mean temperature a run's dT is measured from (Earth's, preindustrial-ish)
