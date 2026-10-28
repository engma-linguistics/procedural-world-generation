---
title: A failed triple-junction arm (aulacogen) leaves no trough, stretched crust or sediment basin
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: low
found_by: lane22
blocked_by: []
relates: [PW-952, PW-135, PW-242]
refs: [planet/tectonics/events.py, planet/tectonics/crust.py]
---

## Description
events.triple_rift (PW-952) cracks a big plate from a new plume head along three arms; each arm fails with
odds aulacogen_odds. A failed arm today only changes how many pieces the plate splits into (two instead of three)
and the event text: the crust along it is not stretched, dated as rifted (record.T_RIFT) or thinned, so no
graben, thermal sag or thick sediment fill marks it. On Earth an aulacogen is a deep, sediment-filled trough
running into the continent from the junction, often later inverted into a fold belt (the Benue trough, the
Reelfoot rift under the Mississippi embayment, the Dniepr-Donets basin); they matter for oil, salt and river
courses (the Mississippi and the Niger follow theirs).
What to try: along the failed arm's line (the sector boundary triple_sectors drops), from the junction for
~500-1500 km, stretch the continental crust once by a modest ln beta (~0.2-0.4) through crust.stretch, so the
existing rift record, sag (rift_sag) and the fault-block-rift landform pick it up with no new machinery.
- [ ] a failed arm shows as a fault-block rift landform and sinks by thermal sag in the following ~100 Myr
- [ ] no change to the plate counts or the paired pass rate
