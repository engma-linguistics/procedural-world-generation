---
id: PW-928
title: "Overland jump constants need the owner's eye: JUMP_RATE 0.02/kyr, JUMP_HEMMED 5%, HOLD_MIN 0.25"
type: task
status: needs-decision
parent: PW-692
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-35
blocked_by: []
relates: [PW-920]
refs: [planet/lineages/history/params.py]
created: 2026-10-27
updated: 2026-10-27
---

## Description
Fun lane 35 set these from the literature, not fitted to targets. Kernel shape c = 0.5 is Clark 1998's exponential-power fit, with fat-tailed long-distance dispersal per Nathan 2012. Walker length 300 km is the order of the largest mammal natal dispersal (Sutherland 2000). Fliers use spec.HOPS flies at 700 km (Paradis 1998). Sea peoples get 1000 km (Kinlan & Gaines 2003). HOLD_MIN 0.25 x K is an Allee-type critical density (Courchamp 2008). JUMP_RATE (0.02 per kyr at full crowding) has no direct source: it is chosen as "rare" over deep-time steps. The hemmed-in test (JUMP_HEMMED: under 5% of the frontier is free good country) is a judgement call. Giants jump under the general rule; dragons (spec megafauna) are excluded, per PW-924.
- [ ] owner/coordinator confirms or replaces JUMP_RATE, JUMP_HEMMED and HOLD_MIN

## Updates
- 2026-10-27: Created from inbox draft draft-jump-dispersal-constants.md (found by fun-lane-35).
