---
title: "Climate: a 12-16 C seasonal swing right at the equator, so July steps by ~14 C between neighbouring cells at latitude 0"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: pw374-zoom-veg
blocked_by: []
relates: [PW-374, PW-139]
refs: [planet/climate.py, "world bcd6c8", "zoom 369394"]
---

## Description
In world bcd6c8 (ice-age showcase, run 2c2810 @ 536 Myr), the land cells within a degree of the equator near lon -7
have warm_month ~27 C / cold_month ~11 C just south of it and ~24.5 / ~12.5 C just north of it: a seasonal swing of
12-16 C at latitude 0, where the sun's annual cycle has almost no amplitude (Earth's equatorial land: 1-3 C). Because
warm_month is July in the north and January in the south, the world's own `temperature_jul` steps from ~11 C to
~25 C between neighbouring cells at the equator (and `temperature_jan` the other way).

`_air_temps` builds t_warm and t_cold from each hemisphere's own summer and winter (`v_sum` / `v_win` air carried
from `eq_s` / `eq_w`, the land's half-swing `continental x |sin lat| + 0.3`, the orbit's anomaly by `north`), so
nothing forces the two hemispheres' summers to meet at the equator: whatever the carried air, the sea's swing
(`sea_half`) or the orbit leaves there becomes a swing of the full size on both sides, with the phase flipping at 0.

PW-374 made the zoom interpolate July and January (a smooth ramp over the cells' blend instead of a pixel-row
step), but the coarse step itself is the climate's. Where the ramp crosses over (July = January), a ~30-60 km
band along the equator has no seasons at all, between two strongly seasonal sides; zoom 369394 rebuilt shows it as
a wavy stripe of different vegetation across the whole zoom (docs/review/zoom-polish/pw374_369394_satellite.png).
Two half-year values can't rotate the phase through April / October, so only a smaller equatorial swing in the
world removes the stripe. What I'd try: make the seasonal half-swing go through zero at
the equator (e.g. taper the summer-minus-winter part by the insolation's own annual amplitude, which is ~|sin lat|
plus a small semiannual term), or compute July and January (not warmest / coldest) so the two hemispheres share
one field that is continuous by construction.
- [ ] |temperature_jul(0.1 N) - temperature_jul(0.1 S)| under ~3 C on land in a showcase world
- [ ] earth_check equatorial seasonal amplitudes not worse
