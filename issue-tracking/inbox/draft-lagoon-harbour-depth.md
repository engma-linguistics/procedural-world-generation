---
title: Barrier lagoons are sheltered (the islands block the fetch) but too shallow to rate as harbours
type: task
status: todo
parent: PW-097
milestone: v2
subsystem: coast
effort: s
impact: low
found_by: fun5
blocked_by: []
relates: [PW-622, PW-099]
refs: [planet/humanuse.py, planet/zoom_coast.py, "zoom f4d05d (fun5 test, barrier coast near -18, 144 on world 726047)"]
---

## Description
PW-622's second checkbox (lagoons count as sheltered water in humanuse harbours) holds through the fetch: the barrier
islands are land in the zoom, so `humanuse.zoom_layers` sees the lagoon behind them as sheltered. But a harbour also
needs deep water beside it (`humanuse.harbours`), and the lagoons are drawn 1-7 m deep (LAGOON_M), so they rate as
anchorage at best, and the tidal inlets (the way in) are shoals and nav hazards. For a game a lagoon is a good
shallow-draught harbour. Options: A leave it; B a "lagoon" harbour class or a shallow-draught anchorage rule for
sheltered water of 2-6 m next to a lagoon-coast; C lower the depth threshold for lagoon pixels. Lean B, small.
