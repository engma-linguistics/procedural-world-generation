---
id: PW-387
title: "Runs could start the rain kernel from the last climate update's vapour (PW-015's warm start): L7 updates 3.5 s -> ~2.5 s"
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: pw015-rain
blocked_by: []
relates: [PW-015]
refs: [planet/climate.py, planet/tectonics/earth.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-015's kernel runs 20 days of pseudo-time from a guess (land air 30% saturated, sea at TUNE's rh) every
climate update: Earth L7 compute 2.2 s (main) -> 3.5 s, L6 0.50 -> 0.62 s (Threadripper, 8 threads), ~+5 min
per L7 Gyr. In a run, 4 Myr apart, the last update's vapour (`_rain`'s fifth output, [season, cell]) is a far
better start: ~8-10 days would do (proposal section 6), about -40% of the kernel. Needs compute() to take and
return the vapour (like moc_start / moc_state) and earth.update_climate to keep it in the sim (and in
checkpoints, or recompute cold after a resume: results would then differ by the convergence error, ~1%,
so store it for bit-identical replays). Outside the PW-015 lane's files.
- [ ] L7 run update <= 1.2x main's; checkpoint replays still bit-identical

## Updates
- 2026-10-16: Created from inbox draft draft-rain-warm-start-in-runs.md (found by pw015-rain).
