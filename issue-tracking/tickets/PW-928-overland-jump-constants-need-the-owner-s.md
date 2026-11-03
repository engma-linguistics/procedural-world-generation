---
id: PW-928
title: "Overland jump constants need the owner's eye: JUMP_RATE 0.02/kyr, JUMP_HEMMED 5%, HOLD_MIN 0.25"
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: peoples
effort: xs
impact: low
found_by: fun-lane-35
blocked_by: []
relates: [PW-920]
refs: [planet/lineages/history/params.py]
created: 2026-10-27
updated: 2026-10-29
---

## Description
**In plain words.** When a people is boxed in, how often does a group of them make a long jump overland to new country? Three settings, sourced from the literature except where noted:
- **How often:** 0.02 per 1,000 years at full crowding, about one jump per 50,000 years. No source; chosen to be "rare".
- **When a people counts as boxed in:** under 5% of its frontier is free good land. A judgement call.
- **How dense a new colony must be to survive:** at least 25% of what the land can carry, or it dies out. This is a standard "too few to keep going" rule (Courchamp 2008).

Question for the owner: does roughly one long jump per 50,000 years, when crowded, feel right? Or should it be more or less often? The other two can stay unless they feel wrong.

Fun lane 35 set these from the literature, not fitted to targets. Kernel shape c = 0.5 is Clark 1998's exponential-power fit, with fat-tailed long-distance dispersal per Nathan 2012. Walker length 300 km is the order of the largest mammal natal dispersal (Sutherland 2000). Fliers use spec.HOPS flies at 700 km (Paradis 1998). Sea peoples get 1000 km (Kinlan & Gaines 2003). HOLD_MIN 0.25 x K is an Allee-type critical density (Courchamp 2008). JUMP_RATE (0.02 per kyr at full crowding) has no direct source: it is chosen as "rare" over deep-time steps. The hemmed-in test (JUMP_HEMMED: under 5% of the frontier is free good country) is a judgement call. Giants jump under the general rule; dragons (spec megafauna) are excluded, per PW-924.
- [ ] owner/coordinator confirms or replaces JUMP_RATE, JUMP_HEMMED and HOLD_MIN

## Updates
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: try JUMP_RATE at about one jump per 20 kyr when crowded (0.05/kyr) and run it a few times. Report what follows, e.g. 'the goblins left their last jungle and found a mostly-empty land'. Long, hard migrations under pressure every ~20 kyr are acceptable even if generous; show the ramifications before settling.
- 2026-10-29: 2026-10-29: plain-language summary added at the top.
- 2026-10-27: Created from inbox draft draft-jump-dispersal-constants.md (found by fun-lane-35).
