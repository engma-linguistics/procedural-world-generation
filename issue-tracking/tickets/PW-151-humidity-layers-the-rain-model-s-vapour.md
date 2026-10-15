---
id: PW-151
title: Humidity layers - the rain model's vapour drains to near zero over dry land in winter
type: task
status: done
parent: null
subsystem: climate
effort: s
impact: low
found_by: viewerocean
blocked_by: []
relates: [PW-144]
refs: [planet/climate.py, "world dc3732"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-144 derives dew point and relative humidity from the rain kernel's water vapour
(_rain now also returns the air's vapour after its rain; climate.humidity). Over long dry
stretches the kernel's air keeps raining out a small share every step (it is tuned for
the rain, not the vapour), so in a dry season the vapour falls toward zero: on Earth
(world dc3732) raw values gave Sahara / Delhi January dew points of -40 to -50 C (real:
about -5 to +8 C, RH 30-60%). humidity() holds the lowest relative humidity at
HUMID_MIN = 15% and saturates high values softly (x / (1 + x^4)^(1/4)), which gives
sensible numbers elsewhere (Amazon 63-68%, sea ~75%, London Jan 85%) but leaves dry
continental winters at the 15% floor.

What I'd try: keep a background vapour in the kernel that sinking air doesn't rain
out (e.g. no large-scale rain below rh_c x 0.5), or carry a separate tracer for
humidity that only loses water to actual rain; then compare with observed RH
(e.g. ERA5 2 m dew point) in tools/earth_check.py.
- [ ] Delhi / Sahara January RH ~30-50% without the floor
- [ ] no change to rain (goldens)

## Updates
- 2026-10-14: Status todo -> done. clouds: climate.vapour_mixed keeps a background of vapour in dry air (at least half the vapour averaged over 2500 km, capped at half of what the local air holds), used for humidity and clouds only; the rain is unchanged (goldens: only the new cloud keys moved). Earth January RH: Delhi 45%, Timbuktu 33%, Kashgar 49%, Vostok ~76%; no land at the 15% floor.
- 2026-10-14: Created from inbox draft draft-humidity-dry-air.md (found by viewerocean).
