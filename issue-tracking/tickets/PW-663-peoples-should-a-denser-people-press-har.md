---
id: PW-663
title: "Peoples: should a denser people press harder on its neighbours (DENSITY_PUSH), and how hard?"
type: task
status: done
parent: PW-649
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: peoples-workbench-lane
blocked_by: []
relates: [PW-650, PW-655, PW-601]
refs: [planet/lineages/history.py, planet/lineages/spec.py, docs/proposals/lineages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The workbench lane (PW-650) gave every people a density (people per km² of full habitat). Density sets the
people's numbers and the viable-population rule: a separate patch with fewer than 500 people fades. It also
enters competition. The competition a line feels from a rival is multiplied by (the rival's density / its own)
raised to `DENSITY_PUSH`, clipped to `DENSITY_CLIP`. So farmers press on foragers, and giants barely dent
anyone's room.

The owner did not ask for the competition part. It is a judgement call, and it moves every people.

Single tries on 1df1c3 (L7, try seed 0, preset as of the lane; areas in Mkm²):

| push | humans | elves | firbolgs | storm giants | wish score |
|---|---|---|---|---|---|
| before the lane (no density) | 24.0 | 0.31 | 1.4 | 0.47 | 0.754 |
| none | 37.0 | 11.8 | 0.04 | 0.19 | 0.798 |
| ^0.1, clip 0.7..1.4 (built) | 41.9 | 0.11 | 0.04 | 0.43 | 0.819 |

The arriving elves (25 kyr ago, density 1) are the most sensitive. With no push they take 12 Mkm²; with the
mild push they stay as small as before the lane. At ^0.25 (0.5..2) the humans held 41–75 Mkm² on the two worlds
and several giants fell to refuges of 9–28 individuals.

The humans' larger range on these tries came mostly from their exploration (more long crossings), not from the
push. The preset now gives the humans explore 0.55, which brought them to ~27 Mkm² on try seed 1.

Options:
- **A (built):** a mild push, ^0.1 within 0.7..1.4.
- **B:** no push. Density acts only on numbers and on the viable-population rule. Giants then compete for land as strongly as humans per unit of presence.
- **C:** a stronger push, ^0.25. Farmers sweep the lowlands, as historically they did, at the cost of most other peoples' ranges.

Lean: A. The giants need some push to stay off contested land without the old strict pull, but anything
stronger hands the world to the humans.

## Updates
- 2026-10-23: Status needs-decision -> done. Owner (2026-10-24): as built. Crowding out should read as coexistence and/or pressing away, not killing off: foragers were mostly outcompeted and absorbed (e.g. Corded Ware herders beside still-extant hunter-gatherers). Later epics turn it into warfare, integration, coexistence or forced migration (PW-661).
- 2026-10-23: Created from inbox draft draft-peoples-density-push.md (found by peoples-workbench-lane).
