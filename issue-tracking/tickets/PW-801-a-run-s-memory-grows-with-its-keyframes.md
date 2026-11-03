---
id: PW-801
title: "A run's memory grows with its keyframes and spikes at the end: L7 1 Gyr peaks at 9.9 GB, L6 at 2.8 GB"
type: task
status: done
parent: null
milestone: v2
subsystem: infra
effort: m
impact: high
found_by: benchmark-2026-10-24
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-11-03
---

## Description
Owner asked whether a non-powerhouse machine can still run the sims. Clean benchmark 2026-10-24, seed 957317, 1000 Myr, nothing else running (scratchpad bench/, /usr/bin/time -v plus 5 s process-tree samples):
- L6: 5:40 wall, 709% CPU (~7 cores), max RSS 2.77 GB. Run on disk 659 MB.
- L7: 28:52 wall, 734% CPU, max RSS 9.94 GB. Run on disk 2.6 GB.
- L7 memory climbs steadily (~2.6 GB at 2 min to 4.7 GB at 26 min, about +0.1 GB/min: keyframes held in RAM, 251 of them) and then jumps to 8-10 GB in the last ~2 minutes (the save step, likely stacking/copying all keyframes at once).
Goal: stream keyframes to disk (or preallocate and write in place) so memory stays flat; aim for an L7 1 Gyr peak that fits an 8 GB machine (under ~4-5 GB) without changing outputs (golden tests unchanged). Re-measure with the same command, one run at a time, and record the numbers here.
CPU: one run uses ~7 cores (numba capped at 8 threads), so a 4-core laptop should take roughly 1.5-2x as long (L7 ~45-60 min per Gyr); worth one --threads 4 measurement to confirm.

## Updates
- 2026-11-03: Status todo -> done. Lane 154 merged: keyframes and volcanoes stream to disk (store.LayerStream/VolcanoStream); outputs byte-identical on 4 seed-957317 pairs; peak RSS vs main ceda2abc same seed: L6 1 Gyr 2.74->1.09 GB, L7 400 Myr 4.81->3.36, L7 1 Gyr 7.94->3.43. 972 passed.
- 2026-11-03: Lane 154: keyframes stream to disk as the run makes them (store.LayerStream, store.VolcanoStream; timeline.simulate no longer holds or stacks them). Seed 957317, --threads 4, against main ceda2abc on the same seed at the same time: L6 1 Gyr 2.74 -> 1.09 GB peak, L7 400 Myr 4.81 -> 3.36 GB, L7 1 Gyr 7.94 -> 3.43 GB (memory now level through the run). All layer files and volcanoes.json.gz byte-identical by SHA-256 at L5, L6 and L7; golden tests unchanged. A Ctrl-C'd run now keeps its whole keyframes readable (header lists layers and frames). Write-up: docs/review/speed/memory-fixes/round2.md.
- 2026-11-03: Cause located (11-03, docs/review/speed/l9-memory.md): keyframes are kept as lists all run (timeline.py:125,145) and every layer is np.stack'ed at once before writing (timeline.py:164), hence the end spike. Streaming frames to disk keeps outputs bit-identical; ~38 GB per Gyr at L9 (estimate).
- 2026-10-24: Created.
