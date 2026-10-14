---
id: PW-005
title: Landform classes for coarse-to-fine zoom variety
type: epic
status: todo
parent: null
subsystem: zoom
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: [PW-001]
refs: [planet/surface.py, planet/zoom.py, docs/review/falls/]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Zooms all look like the same graded hills and valleys; real coarse-to-fine variety comes from geology
history. The run computes each cell's **landform class** from its history, and the zoom synthesises
terrain to match, so waterfalls emerge where rivers cross scarps (instead of being designed per reach).

8–12 classes (owner: more than 3, fewer than 20), introduced testably, a few at a time. Candidates:
rifted-margin great escarpment (retreat set by rift age: Drakensberg, Western Ghats); caprock plateau /
cuestas (Niagara, Grand Staircase); lava plateau / traps (Deccan); fault-block rift (Basin and Range,
East African Rift); fold-and-thrust belt (Zagros, Valley and Ridge); old shield with granite domes /
inselbergs; volcanic arc and hotspot island (see PW-001); coastal plain / delta;
glacially carved terrain; karst; dune field.

Stories: per-cell stratigraphy; new rock types; history bookkeeping; class assignment; zoom synthesis
in batches of 3–4. This is also where taller waterfalls come from (morning decision 2).

## Updates
- 2026-10-14: Created from the 2026-10-14 discussion with the owner (waterfall decision follow-up).
