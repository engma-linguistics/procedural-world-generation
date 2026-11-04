---
id: PW-585
title: "dad91b's southern sinking (2.5 Sv) is now set by the straits: its densest polar water sits behind passages too small for the inflow"
type: task
status: todo
parent: PW-570
milestone: later
subsystem: ocean
effort: s
impact: low
found_by: base-climate-laneA10
blocked_by: []
relates: [PW-579, PW-582]
refs: [planet/ocean.py, docs/review/base-climate/stages.md]
created: 2026-10-22
updated: 2026-11-03
---

## Description
After PW-579's entrainment (lane A10), Earth's south is 5.9 Sv. The other 8 generated worlds' south is 11.5–18 Sv.
dad91b's south stays at 2.5 Sv, because its brine-dense shelf water (1029.6 kg/m3) lies behind passages that PW-582's
`_straits` judges too small for the inflow. So it isn't in the polar sea the inflow reaches, and the reachable polar
sea (~3.8 Mkm2) is nearly uniform: its densest 10% are 0.8 kg/m3 above its mean, so there is nothing to entrain.

On Earth, dense water forms behind sills and still spills out over them: the Mediterranean outflow, the Denmark
Strait, the Weddell's Filchner trough. So a strait that the warm inflow can't pass could still let dense water out.
In the model, sinking needs a reachable surface inflow.

Options:
- A: accept it. A hemmed-in polar sea makes little deep water, and dad91b still sinks in both hemispheres.
- B: let water behind a strait sink as an overflow, replaced by surface water from the reachable side, with the
  flux limited by the strait's cross-section.

Lean: A for v2. B is a real mechanism, but it matters for one world in 9.
- [ ] rule A or B

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ocean calibration against Earth sea temperatures; Earth is a plausibility anchor, not a target
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-dad91b-south-is-straits.md (found by base-climate-laneA10).
