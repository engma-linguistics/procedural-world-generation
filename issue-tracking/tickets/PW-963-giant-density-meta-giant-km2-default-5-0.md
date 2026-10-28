---
id: PW-963
title: Giant density - meta.giant_km2 default 5,000 km2 vs ~130-345 (forager-scaled) vs ~30-100 (culinary-dnd herders)
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-936, PW-724, PW-923]
refs: [planet/lineages/spec.py, planet/lineages/samples/dnd.toml, docs/proposals/megafauna-scaling.md, /home/daniel/personal/repos/culinary-dnd/docs/giants-shared-fact-sheet.md]
created: 2026-10-28
updated: 2026-10-28
---

## Description
The three giant densities disagree, all as of 10-28.

**Fun lane 38** (merge 94c5a318) set meta.giant_km2 = 5,000, the same as dragons. That carried the owner's 10-28 ruling "giants get their own, lower density (user option like dragons')".

**The megafauna scaling session** (docs/proposals/megafauna-scaling.md) gives, per giant:

| basis | hill giant | storm giant |
|---|---|---|
| human foragers (~0.1/km²) scaled by mass^-0.75 | 1/140 km² | 1/345 km² |
| pure carnivore (Carbone & Gittleman) | 1/400 km² | 1/1,300 km² |

**culinary-dnd** (the owner's consumer repo, giants-shared-fact-sheet.md) gives, per giant:
- hunting giants: 1/50-100 km²;
- herding giants: a few hundred to ~1,000 in 30,000 km², so about 1/30-100 km²;
- farming giants: denser still.

So 5,000 is 15-35x below forager-scaled giants and 50-150x below culinary-dnd's. Lane 38's note says a lower density helped coverage and the peoples' remnant pass (giants take less room), which may be what really drove the number.

Options:
- **A.** Keep 5,000 and read it as people pressure, like dragons (PW-957). Giants are pressed hard by the younger peoples (giant-slaying, displacement) and have natural density only in unpeopled country. This is consistent with the dragon story, but it leaves culinary-dnd's local numbers as the "natural, unpressed" case, which the consumer repo would need told.
- **B.** Default by way of life, scaled by mass (forager-scaled ~1/150-350, herders denser, raiders sparser), with giant_km2 as a multiplier. Coverage and remnants then need re-solving by competition, not by thinning.
- **C.** A split: a natural density from mass, pressed by peoples to a present-day default. The present default sits between, e.g. ~1/1,000-2,000, so a steading of 10 holds 10-20 thousand km2.

Lean: C, sharing PW-957's pressure mechanism, so dragons and giants follow one rule. Check that a steading's country still reads right in the brief.

## Updates
- 2026-10-28: Created from inbox draft draft-megafauna-7-giant-density-reconcile.md (found by coordinator).
