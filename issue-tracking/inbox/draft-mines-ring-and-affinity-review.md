---
title: "Settlements: owner check of the mine rule (ring size, orc/goblin kin weight, dwarves few)"
type: task
status: needs-decision
parent: PW-856
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-68
blocked_by: []
relates: [PW-1116]
refs: [planet/lineages/settlements.py, docs/overview.md]
---

## Description
In plain words. Mines now go to the people in a cell who are most inclined to dig (dwarves, kobolds, gnomes, then orcs and goblins, then everyone else), even when they are a small minority among humans; flyers like the aarakocra and swimmers are much less inclined. Only the best mine of each ring of cells survives, so a run has 260-370 mines instead of about 2,200, and humans work 42-80% of them (was 95%). Three judgement calls to look at in the viewer:
- A: the ring (one mine per cell plus its neighbours) is a guess; a smaller ring means more mines. The literature gives districts (Mitterberg: 200+ smelting sites in one district) but no count per region.
- B: orcs and goblinoids get weight 0.4 from lore (no trait says they mine). Hobgoblins now work 22-92 mines a run, more than dwarves, because dwarves hold few ore cells in these worlds. Give orcs and goblinoids a `miner` trait in the sample file (which would change their density) or lower the weight.
- C: dwarves work only 3-12 mines a run. If the owner wants them to dominate, the cause is their range (mountains without ore districts, or few of them), not this rule.
Lean: keep as is, look at one globe, then adjust MINING_KIN or the ring.
- [ ] owner looks at the mines on the globe
