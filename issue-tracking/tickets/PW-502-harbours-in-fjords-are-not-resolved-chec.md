---
id: PW-502
title: "Harbours in fjords are not resolved: check on an Earth zoom, add a world proxy"
type: task
status: todo
parent: PW-099
milestone: v2
subsystem: coast
effort: s
impact: med
found_by: humanuse
blocked_by: []
relates: [PW-099]
refs: [planet/humanuse.py, "world f6e955", tests/test_humanuse.py]
created: 2026-10-21
updated: 2026-10-23
---

## Description
Measured on the Earth world f6e955 (L6, ~120 km cells): harbours appear at estuaries (Thames fine harbour, Gironde, Chesapeake, Hudson, St Lawrence), but the Norwegian and Chilean fjord coasts come out as at most one anchorage: the effective fetch of a 120 km cell cannot see an inlet a few km wide (shelter 0.45-0.48 against a class floor of 0.6). The zoom path (2 km pixels, fetch to 50 km, deep water within 6 km) was only tested on a synthetic bay and on an Earth-like seed-3 zoom (107 anchorages, a few harbours); there is no Earth zoom to test on because f6e955 (a time-zoom frame) has no rock layer, so `planet zoom` refuses it (and the Earth tectonic run is not in the store).
- [ ] build an Earth zoom of a fjord coast (Norway 61N 6E, or Chile 46S 74W) and check that fjords come out as harbours (deep, sheltered, ice-free in Norway)
- [ ] if the world needs it: a fjord proxy (deep water beside high relief, 800+ m land next to 100+ m water) as a shelter bonus, as the estuary has; ask before adding, it is a judgement call

## Updates
- 2026-10-23: Milestone null/later -> v2 (PW-597 triage, coordinator, 2026-10-23): fjord harbours are v2.
- 2026-10-21: Created from inbox draft draft-humanuse-fjord-harbours.md (found by humanuse).
