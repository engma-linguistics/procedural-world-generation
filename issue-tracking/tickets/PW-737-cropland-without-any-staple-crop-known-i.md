---
id: PW-737
title: "Cropland without any staple crop known is cut to 30% (landuse.CROP_FLOOR): a judgement call"
type: task
status: done
parent: PW-721
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun7
blocked_by: []
relates: [PW-721, PW-662]
refs: [planet/lineages/landuse.py, planet/lineages/crops.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
`landuse.cover` multiplies the cropland of a cell by `CROP_FLOOR + (1 - CROP_FLOOR) x know` where `know` (0..1, crops.py
`present_cells`) is the share of a staple diet the crops known and growable there make (weights per crop in
`crop_defs`). With `CROP_FLOOR = 0.3`, a farming people with no staple in reach sows 30% of what it would with one. The
value is a judgement, not fitted: farmers without a domesticated staple still garden local plants, tubers and tree crops
(none of which are in the table yet). On run 14802d-like worlds the gate removes about a quarter to a third of the
cropland of the ungated overlay (6.97 -> 4.6 Mkm2 on 1df1c3 real), mostly on landmasses the crops reached late or not at all.
Options: keep 0.3; raise to 0.5 until fruit and tree crops, pulses and tubers are all in the table; or make it 1.0 (no gate)
and keep crops as a farm-capacity effect only.
- [ ] owner picks the floor

## Updates
- 2026-10-24: Status needs-decision -> done. Coordinator: keep 0.3 (fields without a staple stand for minor crops and gardens); revisit with PW-738's cuisine plants.
- 2026-10-24: Created from inbox draft draft-crop-floor-without-a-staple.md (found by fun7).
