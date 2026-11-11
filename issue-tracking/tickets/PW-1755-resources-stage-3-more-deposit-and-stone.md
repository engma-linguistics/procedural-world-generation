---
id: PW-1755
title: "Resources stage 3: more deposit and stone kinds (silver, lead, mercury, sulphur, nitre, jade, lapis, turquoise, amber, ruby/sapphire split, opal, quartz gems), all derived at finish time"
type: task
status: todo
parent: PW-155
milestone: v1.0
subsystem: surface
effort: m
impact: med
found_by: owner
blocked_by: []
relates: [PW-098, PW-1005]
refs: [planet/resources.py, planet/zoom/resources.py, docs/proposals/resources.md, planet/lineages/mining.py]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** The resources layer already has 26 kinds (23 real deposit models plus 3 fantasy ones), and building stone is in the land layer. Daniel (11-11) asked whether "more rock/mineral/gem/stone/metal types" had been done; v2 had planned more ore types. Add the commonly wanted kinds that are still missing. Each needs a named deposit model from the run's own geology, written next to its rule like the existing ones. Candidates: silver (with lead-zinc and epithermal), lead, mercury (cinnabar at young hot springs and arcs), sulphur (volcanic), nitre (arid caves and playas), jade (serpentinite in sutures), lapis lazuli (metamorphosed limestone), turquoise (arid weathering over porphyry copper), amber (old coastal forest basins), the ruby/sapphire split of corundum, opal (arid silica weathering), and quartz gems (amethyst, agate in volcanic cavities).

**Cost.** These are labels derived when the world is finished or zoomed; they add no run time (PW-155 cost note, 10-20). The zoom siting (stage 2) and the tech tree's ore goods read the new keys only where they are mapped in.

**Done when:** each new kind has a rule and a test, shows as a world layer with hover text, appears in the deposit summary, and is checked on Earth (data/earth) against where it really is, by eye and in a short table. Nothing changes in a run's physics or history unless a key is deliberately added to mining.ORE_GOODS.

## Updates
- 2026-11-11: Created from inbox draft draft-resources-more-kinds.md (found by owner).
