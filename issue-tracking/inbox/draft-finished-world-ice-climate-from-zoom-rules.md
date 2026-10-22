---
title: "A finished world from a stage-1 time zoom frame takes the run's ice-surface climate, not the zoom's (sheet air, local terms)"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: ice-v2-stage1
blocked_by: []
relates: [PW-555, PW-198]
refs: [planet/finish.py, planet/climate.py, planet/timezoom/params.py]
---

## Description
Stage 1 (PW-555) gives the time zoom its own rules for the sheets' carried air (`sheet_air=cold`) and the
ice surface's own effects (`surface_air=fetch`), and the seasonal orbit response. `finish.orbit_dt` takes the
seasonal response, but the finished world's climate (climate.compute with the frame's ice, icemass.surface)
still counts all the ice's air and the local terms on top, so a world's ice-surface summers are a few C
colder than the zoom's own frame. Close when the run takes the same rules (stage 3), or pass the zoom's
rules through finish if stage 3 is far off.
