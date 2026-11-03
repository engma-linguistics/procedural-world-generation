---
id: PW-1173
title: "Owner call: after niche learning humans still hold about two thirds of people in the even-six tree; what next?"
type: task
status: done
parent: PW-917
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: lane79
blocked_by: []
relates: [PW-1155, PW-1149, PW-1152]
refs: [planet/lineages/history/params.py, tools/peoples_robust/trees/even_six.toml, "world 4360a3"]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
Every people can now slowly learn new country, and they do. Elves reach three to five times more land, gnomes and halflings gain, and
humans lose some ground. It does not even out the six peoples you wanted near-equal, though. Humans still hold 65-68% of all people
(72% before). Elves stay around 1%, because they arrive late (25,000 years ago) and are thin on the ground (1 person per km²
against the humans' 10). Learning adds land, not density. The next lever is the density and arrival question you parked
(PW-1149).

## Description
Measured by lane 79 on world 4360a3, one try per seed, with the lane 77 suite's even_six tree. Each figure is share of people,
off -> on:
- seed 7: human 72.2 -> 67.8; halfling 15.9 -> 16.4; dragonborn 8.6 -> 10.1; gnome 3.1 -> 4.8; elf 0.2 -> 0.9 (elf area 3.7 -> 15.4 Mkm²).
- seed 10: human 72.8 -> 68.4; halfling 16.3 -> 18.0; dragonborn 8.6 -> 9.3; gnome 2.1 -> 3.2; elf 0.3 -> 1.1.
- Tieflings are a template overlay, 10% of humans. Their share is set by the template, not by learning.
- With lane 77's SPLIT_FOUNDING = local (seed 7): humans 87.5 -> 64.9, gnome 5.8 -> 18.6, halfling 6.3 -> 15.4, elf 0.3 -> 1.0,
  and dragonborn 0.1-0.2 either way. Under local founding the dragonborn no longer inherit the draconic stem's range.

Options:
- A. Accept: learning is the mechanism, and the split follows density and arrival time.
- B. PW-1149 option B: set the elves' and dwarves' densities by way of life (elves 3-5/km²).
- C. Bring the elf and gnome arrivals earlier, so they have time to learn country before the world fills.
- D. Raise LEARN_GAIN, the share of the body's range a people can learn, now 0.6. Lane 79 measured 1.0: the first people into an
  empty continent then took the lowlands and the peoples' biome mixes converged. Not recommended.

Lean: B, then re-measure. Only C if B is short.

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03: its lean B (densities by way of life) is built (PW-1149 B, PW-1203 A, overview 2.26; owner D20 lever 3), and D31 (10-31) ruled to stop fiddling with peoples shares until war/polities. Remaining share questions are PW-1241.
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-even-six-after-niche-learning.md (found by lane79).
