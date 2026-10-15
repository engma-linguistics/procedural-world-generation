---
title: "zoom_landforms docstrings: caprock 'relief 1.5x deeper' and shield dome sizes (rest of PW-192)"
type: task
status: todo
parent: null
subsystem: docs
effort: xs
impact: low
found_by: smalls
blocked_by: []
relates: [PW-192, PW-148, PW-011]
refs: [planet/zoom_landforms.py]
---

## Description
PW-192's other docstrings were fixed on branch smalls (volcanism, scorecard,
earth_world, coordination.md numbers); `planet/zoom_landforms.py` was left
alone because the vegzoom agent owned zoom*.py that night.
- Module docstring, caprock entry: "relief 1.5x deeper" is stale. `Caprock.relief`
  went in a2afa0f (PW-148); `Caprock.RELIEF = 1.5` is the bench period cap
  (at most 1.5x the zone's relief), already described earlier in the same entry.
  Drop the phrase (only the lava plateau has deeper valleys now).
- `Shield` docstring: domes "1-4 km across, 100-400 m"; the call uses radius
  0.8-4.5 km (1.6-9 km across), height 0.1-0.3 x radius capped at 500 m,
  x 0.65-1. Check PW-011 for which was meant and fix the docstring or the
  parameters.
- [ ] both docstrings match the code
