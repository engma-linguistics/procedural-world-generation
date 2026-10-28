---
id: PW-952
title: "Rifts that split a plate into three: plume-centred triple junctions (with PW-565)"
type: task
status: done
parent: null
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-565, PW-827, PW-949]
refs: [planet/tectonics/events.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
The owner asked whether a plate can split into three or more pieces, not just two. Today events.maybe_rift makes at most one two-way split per step. Earth precedent: rifts often start as three arms from a hot spot (rift-rift-rift triple junctions; Burke & Dewey 1973, J. Geol. 81:406, to be verified). Afar today, where the Red Sea, Gulf of Aden and East African Rift meet, is one. The Atlantic opening and the Pangaea breakup went along chains of them, usually with one arm failing (an aulacogen, e.g. the Benue trough).

Try a plume-centred rift on a big plate: two or three arms from one point, with a seeded chance for each arm to fail. Pair it with PW-565 (stress rifts die out after about 600 Myr, the real cause of half-planet plates). Owner, 2026-10-28: that limit is likely an earlier kludge that "can be experimented away".
- [ ] Largest plate share over 600-1000 Myr falls toward Earth's ~20%.
- [ ] Paired two-roll L6 pass rate does not drop.
- [ ] Before/after plate maps in docs/review/tectonics/.

## Updates
- 2026-10-28: Status todo -> done. Merged (lane 22): largest plate 41 -> 26% over 600-1000 Myr, paired 31/36 vs 31/36; owner approved the examples 10-28.
- 2026-10-28: Created from inbox draft draft-triple-junction-rifts.md (found by coordinator).
