---
id: PW-592
title: With the overturning's heat folded over both hemispheres (PW-589), the NH open sea at 45-65N is 1.8-5 C too warm, and the inflow seas' winters are too mild (Norwegian coast sea air 6.6 vs NCEP 3.5)
type: task
status: todo
parent: PW-570
milestone: later
subsystem: ocean
effort: m
impact: med
found_by: base-climate-laneA13
blocked_by: []
relates: [PW-589, PW-583, PW-458]
refs: [planet/ocean.py, planet/climate.py, docs/review/base-climate/laneA13/bands_fold.txt, docs/review/base-climate/laneA13/climate_bias_a1.txt]
created: 2026-10-22
updated: 2026-11-03
---

## Description
Lane A13 (PW-589) stopped taking the overturning's heat off each latitude band alone. It now comes off the band's
mean over both hemispheres. The NH band means at 55–70N are now right (−2.9 … −3.6 → −0.2 … −2.0 C, annual sea air),
but the warmth inside the band sits too much in the open sea:
- NH open sea (land share within 600 km < 0.15), annual air minus NCEP: 45–50N +2.4, 50–55N +2.2, 55–60N +3.5,
  60–65N +5.1. Before, it was +1.4 / +0.5 / +1.2 / +2.6, so the bias was already there.
- Winter air: Norwegian coast sea 4.2 → 6.6 C (NCEP ~3.5); Nordic Seas coldest month −1.5 → +1.4 bias; Labrador
  Sea / Baffin Bay +0.2 → +3.3; Okhotsk +2.4 → +5.1. The stage-1 and stage-2 bars still pass.
- Iceland's warmest month +0.7 → +3.2, while its coldest month improves −10.0 → −3.7.

Candidates:
- The inflow's E is spread by the surface currents with `relax_km` reach and doesn't reach the coasts and marginal
  seas (North Sea −2.7, Baltic −4.3 annual SST against NCEP's air).
- The winter damping (`winter_half`, `moc_layer_m`) acts on the full share, so the open sea's winter barely cools.
- The tropics: the NH 15–40N sea is still ~1–1.4 C too cold and the SH's 0.3 C too warm. That part of Earth's
  hemispheric asymmetry is the atmosphere's (the ITCZ north of the equator), not the overturning's.

The Barents (PW-583) does not share PW-589's cause. The fold warms it only 0.5–0.8 C (annual −5.7 → −5.2, coldest
month −13.1 → −12.3), so its too-cold inflow stays PW-583's.
- [ ] NH open sea 45–65N within 2 C without losing the band means

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ocean calibration against Earth sea temperatures; Earth is a plausibility anchor, not a target
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Lane A20 (held branch worktree-agent-a2b66e784ed5186c3, 1d076ad): shelf seas take the air the wind brings (only depth/moc_layer_m of the currents' anomaly reaches a shelf). North Sea SST 6.9 -> 8.5, W Europe warmest -1.0 -> -0.4, Yellow Sea warm bias 4.3 -> 3.6; other bars unchanged. Open-sea part (inflow trunk too narrow) is PW-639. Held on PW-640.
- 2026-10-23: Lane A18: the North Sea's annual SST is 6.8 vs observed air ~10.5, about 3 C too cold already before PW-627; the overturning's heat reaching it is +1.4..+1.8 vs +3.6 in the NE Atlantic. First candidate for PW-592 (shelf seas starved of Atlantic heat).
- 2026-10-22: Created from inbox draft draft-nh-open-sea-and-inflow-winters-too-warm.md (found by base-climate-laneA13).
