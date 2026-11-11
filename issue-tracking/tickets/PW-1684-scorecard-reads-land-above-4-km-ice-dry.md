---
id: PW-1684
title: Scorecard reads land above 4 km, ice, dry land and NPP from one 1000-Myr moment; report late-window medians too
type: task
status: done
parent: null
milestone: v1.0
subsystem: infra
effort: s
impact: med
found_by: lane 286
blocked_by: []
relates: [PW-1497]
refs: [tools/scorecard.py, docs/scorecard.jsonl, docs/review/tectonics/andes-late.md, docs/review/tectonics/mountains/andes_late_series.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: the scorecard's headline numbers for each test planet (land above 4 km, ice, dry land, plant growth)
are read at a single moment, the run's last step. Mountains and ice ages now come and go in pulses of 50-100 Myr, so
one moment can land on a peak or a trough and look like a trend. That is what started PW-1680: the 1-Gyr reading
showed land above 4 km doubled (2.35/4.86% against 1.35/1.86%) and land NPP down by a third, while over 600-1000 Myr
the medians of the same runs were 1.55/1.20% against 1.69/1.01% and mean NPP 414/454 against 427/402
(lane 286, andes-late.md section 1). A lane read the snapshot as a regression and a ticket and a lane followed.

If never done: every future scorecard line keeps inviting the same false alarm (or hiding a real drift that happens
to be in a trough at 1000 Myr).

What to do: `world_scores` already steps every 100 Myr (`track`); add `late` = the median (and mean) of each track
field over t >= 600 Myr (or the last 40% of the run), keep `final`, and print `late` first in the summary line.
Finer steps (every 20 Myr) would cost nothing measurable if the track is recorded inside `sim.run`.
- [ ] scorecard.jsonl lines carry a `late` block per world; summary prints it
- [ ] docs/overview.md / coordination.md say which to compare

## Updates
- 2026-11-10: Status todo -> done. Lane 288 merged (52148d49): late-window medians/means over the last 40% (600-1000 Myr), late_track kept; final row unchanged.
- 2026-11-10: Created from inbox draft draft-scorecard-late-window-medians.md (found by lane 286).
