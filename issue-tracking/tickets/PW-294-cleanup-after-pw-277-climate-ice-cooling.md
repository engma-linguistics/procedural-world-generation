---
id: PW-294
title: "Cleanup after PW-277: climate.ice_cooling / TUNE['ice_cooling'] only feed icemass's 2 C"
type: task
status: in-progress
parent: null
subsystem: climate
effort: xs
impact: low
found_by: ice-fix
blocked_by: []
relates: [PW-277, PW-112]
refs: [planet/climate.py, planet/icemass.py, planet/timezoom.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Since PW-277 the ice surface's temperatures are icemass's own year (climate.ice_surface calls icemass.surface).
`climate.ice_cooling()` is no longer called anywhere, and `TUNE['ice_cooling']` = 10 is used only as
`ALBEDO_SHARE` (0.2) x it = the 2 C all-year cooling of thick ice in icemass and TZParams. `climate.ice_cover`
is still used by zoom_vegetation (vegetation's ice share) only.
Tidy (climate agent's file, so not done on the ice branch): drop `ice_cooling()`, give icemass its own
`ICE_COOL = 2.0` C (and TZParams the same default), remove `TUNE['ice_cooling']`, and fix the docstrings that still
call it "10 C colder". No output change.

## Updates
- 2026-10-15: Status todo -> in-progress. Infra batch agent started 2026-10-15 night.
- 2026-10-15: Created from inbox draft draft-ice-cooling-cleanup.md (found by ice-fix).
