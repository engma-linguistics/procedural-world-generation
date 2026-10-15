---
id: PW-024
title: "Plate count: gentle 'big plate over warm mantle splits' nudge"
type: task
status: done
parent: null
subsystem: tectonics
effort: m
impact: high
found_by: mantle
blocked_by: []
relates: [PW-025]
refs: [planet/tectonics/events.py, planet/tectonics/mantle.py, tools/supercontinent.py, docs/proposals/supercontinent_cycle.md, docs/review/overnight_runs.md, "run 9abc92"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Plate counts run low since the fixed-heat and big-plate rift rules were removed in B′: median 6–7
(before 8–10), dipping to 2–3 about 10–20% of the time (seed 1 around 500–700 Myr at L6 and L7). Earth
has ~7 major plus ~8 minor plates. Rifting may split big plates too rarely, or absorption is too eager
(41–61 absorbed vs 52–69 rifts per run). The plate-size rift-stress fix (c8a06d2) helped: the final L6
showcases end with 4–8 plates (01b0f7 7, 796a25 6, f0a1b0 7, 07fb28 7, 9abc92 4, 19385e 8) and L7
103c05 ends with 9.

Next step (owner-approved option C): a gentle nudge in `events.py` raising the split chance of a big
plate sitting over warm mantle (the B′ mantle field), not a forced rule. Check median and minimum plate
count over 4 L6 seeds × 2 Gyr with `tools/supercontinent.py`, and that the supercontinent cycle survives.

## Updates
- 2026-10-14: Status todo -> done. tectsea 0fd35e5: events.strength / (1 + warm_rift x mantle anomaly 0..2), warm_rift = 0.7. L6 4 seeds (1-4) x 2 Gyr (supercontinent.py, samples >= 200 Myr): plate median 7/8/6/7 -> 9/10/8/10 (all 7 -> 9), min 1/4/2/2 -> 4/4/3/4, share <= 4 plates 15.5% -> 3.2%; assemblies > 25% after the start 3/3/1/2 -> 4/3/3/2, every 280-740 Myr; ocean age median 76-110 -> 60-75 Myr; speed 3.5-4.2 -> 4.2-4.5 cm/yr. L7 s21 1 Gyr (cac9c4) still dips to 3-6 plates for 640-1000 Myr: draft.
- 2026-10-14: Owner's answer to morning decision 5: the cycle looks better and is pinned to come back to; this nudge is the concrete next step. Regularity is pinned in PW-025.
- 2026-10-14: Migrated. Merged: Known issues 'Too few plates after the mantle merge' and 'Plate count median 6–7' (mantle), overnight_runs 'plate counts drop to 2–3', morning decision 5 option C.
