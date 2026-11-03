---
id: PW-1092
title: Japan rains its vapour at 0.3-0.4x the observed rate in both halves (no cold-air-outbreak or orographic showers in winter, weak Baiu front in summer)
type: task
status: todo
parent: PW-013
milestone: later
subsystem: climate
effort: m
impact: low
found_by: lane26
blocked_by: []
relates: [PW-998, PW-026, PW-013]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md]
created: 2026-10-30
updated: 2026-11-03
---

## Description
Split from PW-998 (lane 26, option b).

Numbers, Earth L6 db7a178a. Rain (mm/yr) model / GPCC; vapour (mm) model / NCEP:

| half | rain | GPCC | vapour | NCEP | (P/PW) / obs | rain type |
|---|---|---|---|---|---|---|
| Apr-Sep | 554 | 2075 | 22.2 | 31.7 | 0.38 | 72% large-scale |
| Oct-Mar | 495 | 1268 | 15.3 | 12.3 | 0.31 | 100% large-scale, no showers |

- Japan's annual rain is 524 vs 1672 (31%).

**Mechanism: not the frontal-rain ticket's, at least in winter.** Japan's winter rain is the NW monsoon's cold air
made unstable over the warm Sea of Japan, then lifted by Japan's mountains. The vapour is already above NCEP there,
so the missing piece is the trigger.
- The shower trigger uses the land cell's own air.
- The model's Japan winter is 8.6 C against 2.0, too warm. That is PW-026's maritime-air side, and the cold domes make
  it 9.5, so the outbreak's cold air never arrives.
- The summer (the Baiu front) may share the frontal-rain ticket's lifting term. Re-check it after that lands.

To do: check the winter outbreak's air temperature first (PW-026), then the shower trigger over windward coasts.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Earth-only regional residual; Earth is a test analogue (PW-013 relation added).
- 2026-10-30: Coordinator: moved to v2; regional Earth-fidelity refinement, Earth is a plausibility anchor.
- 2026-10-30: Created from inbox draft draft-japan-rain-efficiency.md (found by lane26).
