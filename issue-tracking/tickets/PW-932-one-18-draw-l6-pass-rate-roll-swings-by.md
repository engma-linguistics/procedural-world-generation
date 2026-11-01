---
id: PW-932
title: One 18-draw L6 pass-rate roll swings by ~6 passes; compare sets over two re-rolls
type: task
status: done
parent: null
milestone: v1
subsystem: infra
effort: xs
impact: med
found_by: v1-finish-17
blocked_by: []
relates: [PW-866, PW-872, PW-876]
refs: [docs/review/base-climate/v1-finish-16/fmtally.py]
created: 2026-10-27
updated: 2026-11-01
---

## Description
v1-finish-17 bisected a seeming L6 regression (main 15/18 bar + moment checks, set A = PW-871/879/883/884 + PW-872
+ PW-876 at 6/18). Results, L6 1 Gyr, 18 draws each:
commits only 15/18, + PW-872 12-13/18 (13), + PW-876 12/18, A 6/18; re-rolled (every climate_offset +0.0005):
A 12/18, commits only 12/18. A + PW-915 (B) gave the same draws as A within ~1 C, so it was not an independent roll.
So the 6/18 was a bad roll. One roll of 18 draws moves by +-3 (and once by 6), so a single set can't tell a
2-3 pass change from chaos.
- [ ] the merge bar for run-physics lanes: two re-rolled offsets per set (36 L6 draws), pooled

## Updates
- 2026-11-01: Status todo -> done. Lane 102 compared its 36 re-rolled draws with lane 92's set: soft pass 29/36 vs 28/36. By the 10-30 ruling we stop re-running pass-rate sets.
- 2026-10-27: Created from inbox draft draft-l6-passrate-roll-noise.md (found by v1-finish-17).
