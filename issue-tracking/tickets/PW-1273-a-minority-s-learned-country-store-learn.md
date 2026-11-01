---
id: PW-1273
title: A minority's learned country - store learned acceptance per presence entry? (measured, nothing built)
type: task
status: needs-decision
parent: null
milestone: null
subsystem: timezoom
effort: m
impact: low
found_by: lane111
blocked_by: []
relates: [PW-1269, PW-1259, PW-1155, PW-981]
refs: [planet/lineages/demes.py, planet/lineages/history/frame.py, planet/lineages/output.py, "run b4d502"]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: a deme can split off as "adapted" (tundra elves, say) only where its people has learned new country. The stored
learned-country layer (`peoples_learned`) holds only the learning of the people that leads each cell, so since lane 109 the demes
read it only where the people leads. A people that lives mostly under another's lead (the dragon kinds) therefore can never split
off an adapted deme, even if its own learning would justify one. Daniel to decide whether that is worth fixing.

Measured on the L7 peoples run b4d502 (167 frames, 20.6 M presence entries, 69 lines, 56 with any presence):
- Peoples that never lead a cell in any frame: 1 (half-orcs, 12.8 k entries, 0.1% of the table). Four more lead on under 5% of their
  entries (archaic humans, goblinoids, felines, half-elves). So the "never leads" case is rare for ordinary peoples.
- Where it bites is the many that mostly follow. Share of each kind's presence entries where the kind does not lead, and (in brackets)
  those that lie on a cell whose leader has learned at least 50%, i.e. where lane 109's old bug would have borrowed the leader's learning:
  red dragon 87% (30% of all its entries), green 62% (34%), hill giant 62% (21%), brass 49% (20%), gold 87% (15%), copper 77% (15%),
  bronze 83% (17%), blue 72% (13%), cloud giant 66% (16%), fire giant 81% (20%). Over all peoples, 56.5% of entries are on cells the line
  does not lead, and 12.8% (2.6 M entries) are on a learned-country cell of another leader.
- So the number of adapted splits that would be missed is not directly countable from stored data: the per-line learned acceptance
  (`History._L`, in the simulation) is not saved except for the leader. The counts above bound it: at most those entries.

Cost of storing it: one more uint8 per presence entry, the learned acceptance of that line on that cell. That is 20.6 MB at L7 (b4d502;
the table is 103 MB today, so +20%) and about 5 MB at L6 (4.85 M entries). Needs the simulation to write it (frame.py `_learned_frame`
already computes per-line L), the demes to read it per entry instead of `peoples_learned` gated by `whole`, and a new peoples run
to get it (old runs keep the leader-only reading; owner runs would need re-cutting to see any change).

Options:
- A. Leave as is. Dragons and giants live over others' country; their "way of life" differences are weak anyway.
- B. Store the per-entry byte and let any people split adapted demes from its own learning (cost above, a re-run of peoples).
- C. Only for kinds whose lead share is under ~25% (dragon kinds): store the byte for those, the same cost mostly (they hold most of the entries).
Lean: A until a dragon or giant culture looks wrong for lack of it; B if wanted, since the byte is cheap.

## Updates
- 2026-11-01: Created from inbox draft draft-minority-learned-country.md (found by lane111).
