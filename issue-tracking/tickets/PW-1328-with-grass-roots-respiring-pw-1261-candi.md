---
id: PW-1328
title: "With grass roots respiring (PW-1261 candidate), Mediterranean scrub stops burning: the fire's fine-fuel floor was set on inflated grass growth"
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: s
impact: med
found_by: lane123
blocked_by: []
relates: [PW-1261, PW-234, PW-228]
refs: ["planet/vegetation.py", "planet/vegetation.py::fire_rate", "planet/vegetation.py::globfirm", "tests/test_vegetation.py::test_mediterranean_scrub_burns_and_stays_scrub", docs/review/vegetation/npp-check/candidate1-herb-root-resp.patch, docs/review/vegetation/npp-check/screens.md, docs/review/vegetation/npp-check/diagnosis.md, tools/veg_check.py]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** Lane 123's fix for grass growing too much (the herbs' roots pay upkeep, NPP/GPP 0.7 -> ~0.6) takes the
fine fuel of the idealised Mediterranean climate below the fire's floor (`FUEL_MIN` = 250 g C/m2, a tuned value with no
source in the code), so most of its scrub cells never burn (median fire return 0 against the test's 10-400 yr). On Earth
the burned area falls from 5.7 to 4.25 Mkm2/yr (GFED ~4.7), still in range. The fuel floor and span were tuned while grass
was ~1.4x too productive; they need a sourced value (GlobFIRM's own minimum fuel: Thonicke et al. 2001, not read) before
the plant fix can merge.
- [ ] read the minimum fine-fuel load for fire spread from a source and set FUEL_MIN/FUEL_SPAN from it
- [ ] with the patch applied: tests/test_vegetation.py passes unchanged; Earth burned area and Mediterranean fire return (veg_check) in range

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: surface/resources refinement; not needed for the culinary goal
- 2026-11-02: Created from inbox draft draft-fire-fuel-threshold-after-grass-cue.md (found by lane123).
