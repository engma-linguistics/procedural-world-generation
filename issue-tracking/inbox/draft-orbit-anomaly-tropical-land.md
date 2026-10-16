---
title: "Time zoom orbit anomaly: tropical land feels insol_k in full, so an eccentric orbit gives a 13-16 C annual swing at the equator in finished frames"
type: task
status: needs-decision
parent: null
subsystem: timezoom
effort: s
impact: med
found_by: pw380-equator
blocked_by: []
relates: [PW-380, PW-198]
refs: [planet/timezoom.py, planet/finish.py, "world bcd6c8", "world bd9a7a"]
---

## Description
PW-380's July step across the equator was a labelling bug, now fixed: compute's max/min of the two half-years
lost which one was July. The size of the swing is a separate issue. In a finished time-zoom frame the
orbit anomaly (`timezoom.orbit_anomaly` -> climate.compute's `orbit_dt`) is insol_k = 0.25 C per W/m2 on
all land, the tropics included. World bcd6c8's frame has e = 0.041 and perihelion 237 deg. Its equatorial
insolation swings -31..+37 W/m2 against the circular orbit, the same months in both hemispheres. That makes
July -7.4 C and January +6.4 C on equatorial land, so the frame's equatorial land runs 11 C in July and
24-26 C in January: a 13-16 C annual swing. The same terrain without the orbit swings 0.6 C (world 592f2a, a
plain run world: 0.3 C). bd9a7a (+1000 kyr) shows 15.6 C.

0.25 C per W/m2 is a mid-latitude land sensitivity (65N summers, where the time zoom's ice is made). Tropical
land responds much less to a seasonal forcing. The free troposphere there is horizontally uniform (the weak
temperature gradient) and tied to the tropical ocean by deep convection, and the extra sun goes into
evaporation and cloud. The model's own seasons damp the tropics the same way (season_strength's equatorial
factor). On Earth today the equator's semiannual insolation swing of ~+-30 W/m2 makes a 1-3 C land swing.

What to try (judgement call for the time-zoom lane):
- In `orbit_k`, mix land's response toward the large-scale air's over the deep tropics, as it already does for
  bright ice: a weight ~1 at the equator falling to 0 by ~25 deg, over a weak-temperature-gradient scale of a few
  thousand km. The mixed k is then mostly the sea's (insol_sea 0.3) because the tropics are mostly sea.
  That gives about +-3 C instead of +-7 C at e = 0.04. It barely touches 65N or the time zoom's ice.
- Check: the time zoom's glacial cycle stats on its usual test seed unchanged, and the finished frame's equatorial
  land swing about 4-6 C at e ~0.04 (palaeo-model range for high-eccentricity tropics).
