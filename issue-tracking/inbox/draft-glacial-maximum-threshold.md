---
title: Glacial maximum is reported at 25% of land under ice; confirm the number
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: climate
effort: xs
impact: low
found_by: lane65
blocked_by: []
relates: [PW-1091]
refs: [tools/ice_criteria.py, docs/review/base-climate/v1-finish-12/passrate4.py]
---

## Description
In plain words. The owner's three ice terms are icehouse, glacial maximum and frozen over. Frozen over has a number (40% of land under ice) and now fails a world. Glacial maximum had none, so lane 65 reuses the 25% that passrate4 already calls "LGM-like" (`LAND_ICE_LGM`, Earth's Last Glacial Maximum is commonly put at about a quarter of the land; the coordinator's note on PW-1091 asks for a source). It is only reported (a GLACIAL-MAX flag and a count), so nothing passes or fails on it.

On the 18 L6 draws of the D arm (roll 0.001) it flags 14, with frozen over 3, because the worlds' ice-age peaks reach 25-40% of land. If the owner wants "glacial maximum" to be a rarer, colder state (for example also needing the world to be cold, as PW-1091 first asked), the cut belongs in `tools/ice_criteria.py` (`GLACIAL_MAX_LAND`).

- [ ] Owner or coordinator: keep 25% of land as the glacial-maximum line, or give another number or rule
- [ ] Verify Earth's LGM land-ice share from a source and note it in the glossary
