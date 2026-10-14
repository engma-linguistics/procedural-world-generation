---
id: PW-108
title: Kilometre-scale cell churn at converging boundaries (cells flip owner/crust type frame to frame)
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-048, PW-053]
refs: ["run:428083@1000Myr(3.79,-37.41)", "run:428083@1000Myr(8.03,-41.31)", "run:428083@1000Myr(1.66,-39.3)", planet/tectonics/simulation.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner zoomed into a visually striking spot (run 428083, t=1000, around (3.8,-37.4), plate 62/79 converging boundary): rainforest next to glaciers next to hot desert. Much of the extreme cell-to-cell relief there is churn, not landform:
- cell 9773 (3.79,-37.41): 156 m continental (988) -> -4425 m oceanic, 12 km crust (992) -> 686 m continental (996);
- cell 4495 (8.03,-41.31): ocean -2974 m (992) -> 104 m (996) -> 5358 m, 59 km crust (1000) while all neighbours sit at 14-173 m;
- cell 110673 (1.66,-39.30): 5349 m, 68 km crust (996) -> 1084 m, marked oceanic, 19 km crust (1000).
Diagnose with the frame layers plate/crust/crust_thickness and events (only 'subduction' breakoffs on 79 and 62 in 988-1000): ownership resolve, sliver absorption or collision stacking moving whole columns per step. Broader than PW-048 (one-off 12 km spikes) and a candidate contributor to PW-053's sea-level swings. Real relief at collision belts changes over 10s of Myr, not 4.

## Updates
- 2026-10-14: Created.
