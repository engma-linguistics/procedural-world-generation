---
title: "Polities: states last 600-1,400 years against a historical median of 130 (no collapse yet)"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lane-169
blocked_by: []
relates: [PW-1431, PW-1432]
refs: [planet/lineages/polities.py::derive, planet/lineages/polities.py::WAR, docs/review/culture/polities/round1.md, docs/review/cultures-proposal/proposal.md, "run a2b637", "run 3c1caf"]
---

## Description
**In plain words.** In polities v0 a state falls only when its capital shrinks, empties or comes under a stronger neighbour.
Nothing else ends it. Half the states last 600 years on a2b637 and 1,400 years on 3c1caf (Seven Meals). Taagepera 1997's median
is 130 years at half or more of peak size, and only 16 of his 78 polities lasted 300 years or more. These figures are from round
1 of the cultures proposal (section 2.1.2). If this is never done, the state cards' "fell" date is mostly "still stands". The map
then shows the same borders for a thousand years, and that misleads anyone building a history from it.

The fix the proposal names: a base hazard of ending that does not grow with age. Arbesman 2011 found empire lifetimes are
exponential with a mean of ~220 years, about 0.46 per century. A fallen state drops one tier at a time (Currie et al. 2010), and its
towns become seats again. Do it with war v0 (PW-1432) at the `polities.WAR` seam. Use a seeded draw per polity and century, so a
rebuild gives the same map.
- [ ] median state life within 2x of 130 years on a2b637 and 3c1caf, with counts per step still stable when the reach is nudged
  ±10%
