---
id: PW-1472
title: "Tech tree inside the history: D52's town arms (B, E) need a town footprint there, from the live seats"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane-192
blocked_by: []
relates: [PW-1466, PW-1464, PW-1461, PW-1434]
refs: [planet/lineages/history/tech_live.py, "planet/lineages/history/polity_live.py::LivePolities._step", "planet/lineages/techtree.py::Calendar.arm_rate", "planet/lineages/techspread.py::town_footprint", "planet/lineages/output.py::_towns_first", docs/review/culture/polities/round8.md, docs/review/culture/writing/round2.md]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** If Daniel picks arm B or E for D53 (writing crosses a people's towns, or a court takes writing once the front
reaches its nearest town), new runs now get it: the tree is built again after the town ledger (PW-1464, lane 192). But with polities
in the history switched on, the tech tree runs inside the history (PW-1466), and there is no ledger yet. It runs without B and E and
warns. So the switch-on runs, the ones meant to become the product in v4, would quietly lose the arm Daniel chose, and their writing
would spread at the old, slower pace while the switch-off runs used the faster one.

**What breaks if never done.** Turning on both D53's arm and the live polities gives a calendar that ignores the arm: the states of
the live map come later than the arm says, and the two runs (on and off) disagree for a reason no one can see.

**Try.** The live polities already find town seats every century (`LivePolities._step` step 1: central places from the history's
own sedentary heads, the ledger's SHARE and TOWN_MIN). Count each people's town cells per step into the footprint shape `Calendar`
reads (`{people: (agos oldest first, town cells), "_cell_km2": km2}`, as `techspread.town_footprint`), and hand it to the live
calendar (`Calendar.towns`, read by `arm_rate`). The seats run only on the recent pass after the first chiefdom gate, so before them
the footprint is empty, which is right for writing (it needs towns). Check: on 899985 seed 7, the live calendar under E against
`techtree.rebuild(run, arms="E")` of the same history (median date move of writing per people).
- [ ] with the switch on and arm E, the live calendar uses the live seats' footprint and the warning in tech_live goes
- [ ] writing's half-way time under E within the after-run E tree's spread on the same history

## Updates
- 2026-11-04: Created from inbox draft draft-live-tree-town-arms-from-live-seats.md (found by lane-192).
