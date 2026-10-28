---
title: Re-rank PW-565 up; it is the real lever on giant plates (PW-827), more rift tries barely help
type: task
status: needs-decision
parent: null
subsystem: tectonics
effort: xs
impact: med
found_by: lane19b
blocked_by: []
relates: [PW-565, PW-827]
refs: [planet/tectonics/events.py]
---

## Description
Lane 19 made maybe_rift give big plates more stress_cut trials (tries = 12 * sqrt(size / stress_min_plate), max 60).
Seeds 1-6 L6 1 Gyr, mean over 600-1000 Myr: largest plate 0.45 -> 0.44 of the surface (main_tree 0.48), plates
> 2%: 5.1 -> 5.7 (Earth: ~20% and ~8). Scorecard at 1 Gyr: largest plate 52-54% (max 59-68%). Kept because it costs
no pass rate (paired judge 29/36 both arms), but it does not fix PW-827. Late plates stay huge because stress rifts
die out after ~600 Myr (PW-565), so PW-565 is what PW-827 needs. Suggest PW-565 milestone v2 -> v1-adjacent or high
priority in the tectonics lane, and PW-827 blocked_by PW-565. Coordinator call.
