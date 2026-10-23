---
id: PW-460
title: "Margin cells melt as their outermost 10 km (edge_h 408 m vs the cell's ~900 m mean): sub-cell margin in run and time zoom together"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: timezoom
effort: l
impact: high
found_by: pw033
blocked_by: []
relates: [PW-033, PW-435, PW-115, PW-422, PW-453]
refs: [planet/timezoom/sim.py, planet/icemass.py, planet/tectonics/earth.py, docs/review/audit/PW-033-diagnosis.md]
created: 2026-10-20
updated: 2026-10-23
---

## Description
A margin cell (grounded ice next to bare land) takes the balance of a surface `edge_h` = `icemass.EDGE_H` =
408 m high. That is the 75 kPa Nye profile 10 km in from the edge. Across a whole L6 cell (~110 km) the
profile rises to 1354 m, and the cell's area-mean surface is ~900 m: ~3 C colder at 6.5 C/km. So a sheet's
outer cell melts as if all of it were its outermost 10 km, and the ablation zone is one cell of all-melt
(PW-115). The run uses the same height (`earth.ICE_EDGE_M`).

Measured, Earth L6 time zoom, 600 kyr (docs/review/audit/PW-033-diagnosis.md section 4):
- main: -45 m, Laurentide at most 1.7 Mkm2 (south 54 N), interglacial ice 8.7-9.8% of land.
- `edge_h=900` (margins and fronts): -98 m, 5 endings, 0 backstops, interglacial ice 9.7-13.3%.
  Margins only: -65 m. Fronts only: -73 m.
- `baseline=obs` + `edge_h=900`: -71 m, **Laurentide 5.0 Mkm2 reaching 46.6 N** (> 2 Mkm2 for 60% of the
  time), Hudson Bay grounded across, Fennoscandia 0.75 Mkm2. This is the first LGM-like geography.
- **The zoom alone can't change it:** the unforced cold moment of `tests/test_timezoom_consistency.py`
  drifts -46 m in 20 kyr with `edge_h=900` (main -17, bar 25 m), because the run's sheets are the 408 m
  rule's equilibrium.

Options:
- (a) A resolution-aware sub-cell margin in both run and zoom: the margin's balance averaged over the Nye
  ramp across the cell (2-point quadrature at 0.46 and 0.89 x the profile at the cell width, or the 2/3
  mean height). This needs the run's 10-seed cold-era check (pw449 `runN.sh`, bar ~70%) and a look at
  PW-422's creeping margins. Lean.
- (b) Keep 408 m and accept the pulse-like glacials.
- (c) Zoom-only: no; it breaks the run-zoom consistency.
Pair it with the orbit-response decision (`draft-orbit-response-from-seasons.md`): both lift the
interglacial ice, so they should be balanced together.
- [ ] decide

## Updates
- 2026-10-23: Absorbs PW-115 (superseded; PW-597 triage): PW-115's measurement was that in the Earth time zoom (L6, 100 kyr from today) 94% of ice cells with negative mass balance are margin cells (north of 40N 87 of 93 ablating cells on the sheet's edge, Antarctica 64 of 65), where real ablation zones are tens to ~150 km wide. Its ideas (a sub-cell hypsometry for margin cells, or a partial ice cover per cell) and its measures (share of ablating cells away from the margin; ablation area ratio, Greenland today ~0.15-0.2 of its area, reported in the run's stats) apply to this fix.
- 2026-10-20: pw460: built in run and zoom (branch worktree-agent-a9f64607e1a64d2e8 (246ef40), kept unmerged). Zoom: margin-only with obs baseline meets every Earth target (-82 m, Laurentide 5.65 Mkm2 to 44.9 N, interglacial ice 9.5-12.3%). Run: cold eras freeze (10-seed check 0-3/10 vs main 8/10); unforced-start consistency +17.9 to +76 m. The 408 m edge was the run's only way to deglaciate. Not merged; decision moved to PW-461.
- 2026-10-20: Status needs-decision -> todo. Coordinator decision 2026-10-20 (owner delegates physics): take the agent's lean. PW-460 (resolution-aware sub-cell margin) and PW-459 (insol_k from each cell's own seasonal response) are done together, in the run and the zoom, so the unforced start stays consistent; then the 10-seed check (~70% bar). Interglacial-ice bar corrected: real Earth today is ~10% of land (Antarctica + Greenland ~15 Mkm2), so ~9-12% is acceptable; the old 8-9% was the model's own value, not a target.
- 2026-10-20: Created from inbox draft draft-subcell-margin-run-and-zoom.md (found by pw033).
