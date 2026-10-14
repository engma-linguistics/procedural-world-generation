---
id: PW-142
title: "Travel highlights: 'sunny' and 'warm sea' are proxies (dry month, air over the sea)"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: low
found_by: travel
blocked_by: []
relates: [PW-140, PW-126]
refs: [planet/highlights.py, planet/world.py, "world 67317b"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The PW-140 beach finder (`highlights.beaches`) wants a warm, dry, *sunny* summer and a
warm *sea*. Worlds have neither cloud cover / sunshine hours nor a sea-surface
temperature layer, so it uses the summer month's rain (<= 90 mm) as the sunshine proxy
and the July/January air temperature of the neighbouring sea cells as the sea
temperature. Both are reasonable, but a monsoon-edge coast with a dry but overcast
summer, or a cold-current coast with warm air over cold water (Namibia, California),
would be mis-rated.

Also near the equator "summer" is ambiguous: world:67317b(2.58,-41.93) is picked as a
beach for its dry July (18 mm, 27 C) while its January half is wet (1,129 mm/yr); the
seasons doc in `world.seasons` notes the months can be swapped there.

If the climate gains a seasonal SST (ocean.py has one internally) or a cloud fraction,
store them as world layers (`sst_jul/jan`, `cloud_jul/jan`) and use them in
`_beach_cands`.
- [ ] decide whether a seasonal SST / cloud layer is worth storing on worlds
- [ ] if so, switch the beach finder to it

## Updates
- 2026-10-14: Created from inbox draft draft-travel-sunshine-sst.md (found by travel).
