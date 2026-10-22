---
title: "dad91b's southern sinking (2.5 Sv) is now set by the straits: its densest polar water sits behind passages too small for the inflow"
type: task
status: needs-decision
subsystem: ocean
effort: s
impact: low
found_by: base-climate-laneA10
parent: null
blocked_by: []
relates: [PW-579, PW-582]
refs: [planet/ocean.py, docs/review/base-climate/stages.md]
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
