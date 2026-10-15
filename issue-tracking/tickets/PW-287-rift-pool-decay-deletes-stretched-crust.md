---
id: PW-287
title: Rift pool decay deletes stretched crust that its comment says stays in the flanks
type: task
status: todo
parent: PW-245
subsystem: tectonics
effort: xs
impact: low
found_by: audit-tectonics
blocked_by: []
relates: [PW-046]
refs: [planet/tectonics/crust.py, docs/review/audit/tectonics.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`crust.rifted_margin` pools the crust a plate's continent loses to
stretching and lays it as margin cells when new floor opens. The pool decays
`x exp(-dt/100)` per step, with the comment "a rift that never opens keeps
it in its thickened flanks... eventually". The decayed crust is not put
anywhere: it is deleted. The budget books it as part of "stretch", so the
budget's "margin" line overstates how much of the stretched crust is kept.

Measured (audit probes): L6 seed 21 over 1 Gyr, 3228 km x L5 cells
decayed against 58847 laid as margin and 62455 stretched, so ~5% of
stretched crust is lost (L5 seed 1: the same share). This is part of the slow continental-volume decline the thermostat
fights (PW-046: continents thin 1-2 km below target over a Gyr), though not
most of it.

Fix (either): return the decayed share to the plate's continental cells
that were stretched (spread over the rift flanks, which is what the comment
says happens); or keep the deletion and book it separately
("rift pool lost"), with the comment corrected. Lean: return it.

## Updates
- 2026-10-15: Created from inbox draft draft-audit-tectonics-rift-pool-decay.md (found by audit-tectonics).
