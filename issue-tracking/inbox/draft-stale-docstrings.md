---
title: Stale numbers in module docstrings (volcanism, zoom_landforms, scorecard, earth_world)
type: task
status: todo
parent: null
subsystem: docs
effort: xs
impact: low
found_by: docoverview
blocked_by: []
relates: [PW-001, PW-011, PW-148]
refs: [planet/tectonics/volcanism.py, planet/zoom_landforms.py, tools/scorecard.py, tools/earth_world.py, docs/coordination.md]
---

## Description
While rewriting docs/overview.md against the code (branch docoverview), several
docstrings were found to disagree with the constants they describe. Code
behaviour is fine; only the text is stale, but these docstrings are what agents
read first.

- `planet/tectonics/volcanism.py` module docstring: says a new vent opens every
  "~50-120 km" of plate motion and the vent cone is "VENT_KM, ~30 km". Code:
  `vent_spacing` = 1.5 flexural wavelengths, `GAP_KM` = (60, 150) km, `VENT_KM`
  = 25 km (~100 km spacing on Hawaii-like 90 Myr floor).
- `planet/zoom_landforms.py` module docstring (~line 116-120): caprock "relief
  1.5x deeper". `Caprock.relief` was removed in a2afa0f (PW-148); the 1.5 left
  is `Caprock.RELIEF` (bench period at most 1.5x the zone's relief). Only the
  lava plateau has deeper valleys now.
- `planet/zoom_landforms.py` Shield docstring (~line 1079): domes "1-4 km
  across, 100-400 m". The call uses radius 0.8-4.5 km (1.6-9 km across) and
  height 0.1-0.3 x radius capped at 500 m, x 0.65-1. Either the docstring or
  the parameters should change (check which was intended in PW-011).
- `tools/scorecard.py` docstring says "~2-4 min"; recorded `seconds` in
  docs/scorecard.jsonl are 640-796 s (~11-13 min). docs/coordination.md says
  "~6 min" (also stale), and its run-cost table's "checkpoint ~23 MB" at L6 is
  now 25-30 MB.
- `tools/earth_world.py` docstring says it "adds" wind/current/jet layers;
  since PW-045 every world has them.
- Also: `climate.compute` "~0.65 s at L6" (docs/proposals/ocean_overturning.md)
  predates humidity and clouds; re-time when the machine is free.

- [ ] docstrings match the constants; coordination.md numbers refreshed
