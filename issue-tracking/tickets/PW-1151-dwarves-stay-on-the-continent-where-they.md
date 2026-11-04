---
id: PW-1151
title: Dwarves stay on the continent where they split off, which holds 9% of their country
type: task
status: needs-decision
parent: null
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lane73
blocked_by: []
relates: []
refs: [planet/lineages/history/origins.py, planet/lineages/samples/dnd.toml, "world 4360a3; peoples runs 488d7e 570701 097797 ae4d0b"]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
Dwarves branch off the early human-like stem on the one continent that stem lives on (Tenar, on world 4360a3). Only about a tenth of the
world's good dwarf mountains are there. In 500 thousand years the dwarves never leave it: not in the owner's runs, and not with the lane 73
fixes or a more adventurous dwarf. So however well they do against their neighbours, they stay a small people of one continent's mountains.

## Description
On 4360a3, 1,732 cells suit the dwarves (habitat 0.3 or better): Tholosas 767, Hodron 350, Gugiki 296, Tenar 163. The hominid stem lives
only on Tenar, so every split from it is founded there. The orcs (700 kyr) and halflings (100 kyr) also hold parts of Gugiki because the
stem reached it at their split dates; the dwarves at 500 kyr do not. The dwarves are inland mountain folk with a sea share of 0.05, so they
almost never sail. They reached one islet by sea in one run (ae4d0b, 40 kyr ago).
Lane 73's explore nudge (0.35 to 0.5) and the mainline flag do not change this.

Options:
- A. Dwarves split earlier, at about 1-1.5 Myr, while the stem's range is wider; whether that range is wider depends on the world. Data only.
- B. A split's founding may cross the sea to its own country when the parent has none of that country nearby (_origin_split already allows
  "across the sea", weighted by the parent's crossing reach; at 500 kyr that reach is drift rafts only). Model change.
- C. Accept it: dwarves are a one-continent people on worlds like this one, common where they are.
- Lean: A as data, checked on 2-3 worlds, since the date is a placeholder.

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: peoples tuning or owner call that no milestone theme needs
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-dwarves-stranded-in-hominid-cradle.md (found by lane73).
