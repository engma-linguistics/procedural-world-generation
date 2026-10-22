---
id: PW-459
title: "Orbit response insol_k 0.25 C per W/m2 is ~3x the seasonal cycle's 0.08-0.09: precession makes glacial heartbeats"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: timezoom
effort: l
impact: high
found_by: pw033
blocked_by: []
relates: [PW-033, PW-435, PW-440, PW-398, PW-034, PW-114]
refs: [planet/timezoom/params.py, planet/timezoom/forcing.py, planet/icemass.py, docs/review/audit/PW-033-diagnosis.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
The time zoom's land response to a month's insolation change is `insol_k` = 0.25 C per W/m2, and the run's
cycle-averaged ice uses the same `icemass.INSOL_K`. Precession changes the same annual harmonic of the sun
as the seasons. The July-January range per range of the lagged top-of-atmosphere sun on ice-free land is
0.082-0.090 in the model's own climate and 0.078-0.088 observed (40-70 N, Earth L6, `scratchpad/pw033/seasonk.py`).
GCMs give ~0.05-0.1 for Eemian and 116 ka Arctic summers. So 0.25 is ~3x, and precession swings 65 N land
summers by ~+-10 C.

Effect on the Earth zoom: each precession minimum nucleates ice fast, and the next maximum erases it. The
NH ice goes +3 -> -45 -> -12 m over 300-326 kyr, and the Laurentide is never above 1.7 Mkm2. With
`insol_k=0.10`: -62 m (main -45), 6 endings, 0 backstops, but interglacial ice 11.8-13.0% of land (bar 8-9)
and the same Laurentide geography (~1.5 Mkm2).

History: 0.25 was set as a "65 N land sensitivity" (PW-398). Above 0.3 the Eemian start melts Antarctica
and Greenland (PW-034, PW-114), and PW-440 found 0.45 gives cycles but melts interglacial Antarctica.

Options:
- (a) `k` from the climate's own seasonal response per cell: (t_warm - t_cold) / the lagged sun's seasonal
  range, with a floor on the range near the equator. This is planet-relative, gives ~0.085 at high
  latitudes, and covers PW-398's tropical over-response and the sea's damping (`insol_sea`) too. The run and
  the zoom change together, then the 10-seed cold-era check, Earth's Eemian start (PW-034) and the
  interglacial ice share. Lean, together with the sub-cell margin (`draft-subcell-margin-run-and-zoom.md`),
  which deepens glacials in the other direction.
- (b) Keep 0.25.
- [ ] decide

## Updates
- 2026-10-20: pw460: seasonal_k built (branch worktree-agent-a9f64607e1a64d2e8 (246ef40), kept unmerged): k from each cell's own seasons, ~0.08-0.09 on land, ~0.023 at sea (drops insol_sea). k-only: Earth -60 m, interglacial ice 12-12.8%, Laurentide geography unchanged; run 6/10 seeds (below the 7/10 bar); consistency +14.7 m. Not merged; decision in PW-461 option A.
- 2026-10-20: Status needs-decision -> todo. Coordinator decision 2026-10-20 (owner delegates physics): take the agent's lean. PW-460 (resolution-aware sub-cell margin) and PW-459 (insol_k from each cell's own seasonal response) are done together, in the run and the zoom, so the unforced start stays consistent; then the 10-seed check (~70% bar). Interglacial-ice bar corrected: real Earth today is ~10% of land (Antarctica + Greenland ~15 Mkm2), so ~9-12% is acceptable; the old 8-9% was the model's own value, not a target.
- 2026-10-20: Created from inbox draft draft-orbit-response-from-seasons.md (found by pw033).
