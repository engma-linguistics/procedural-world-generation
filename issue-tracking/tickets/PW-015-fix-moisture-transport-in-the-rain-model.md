---
id: PW-015
title: Fix moisture transport in the rain model
type: story
status: in-progress
parent: PW-013
subsystem: climate
effort: l
impact: high
found_by: daniel
blocked_by: [PW-014]
relates: [PW-019]
refs: [planet/climate.py, tools/earth_check.py, tools/scorecard.py, "plan_next@bdc967f: Known issues → Climate", tools/ice_probe.py, docs/review/audit/polar-bundle.md]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Make the rain model carry vapour realistically between basins and inland, guided by the diagnosis.
Success: basin E−P contrast close to observed, and the regional misses that share this root improve.

Merged known issues (Earth on our climate):
- Sahel and East Africa too wet; Indian and Chinese monsoons too dry (from the v1 notes).
- River discharges miss because of rain: the Yangtze ends in a lake; the Lena, Mekong and Ganges are
  too small (dry China, Siberia, Indian monsoon); the Nile is 19× too big (wet Sahel). With observed
  rain, magnitudes are about right (`water`).
- The model's Ganges is ~3,700 m³/s against ~40,000, so no Earth delta comes out tide-dominated
  (`deltas`; morning decision 4).
- Also consider: rain doesn't see the overturning's ocean warming (one extra temperature pass, no rain
  recompute; morning decision 3b).

Check with `tools/earth_check.py` and the scorecard; don't chase parity.

## Updates
- 2026-10-16: Stage 1 measured alone: regresses Earth (L7 arid 24.5->17.9%, land rain 784->1152 mm vs 791 obs, exact Koppen -2.9), not merged. Stage-2 east-coast fix 326e482 helps summer but winter coasts and sea-column saturation still wrong. Next: one bounded attempt at a boundary layer under the column (option A), riding the surface wind, with an explicit success bar; if it misses, park PW-015 with the branch kept and move the run lane to PW-380.
- 2026-10-16: Status todo -> in-progress. Run-lane agent started: implementing the approved proposal stage by stage (with PW-358).
- 2026-10-16: Status needs-decision -> todo. Owner 2026-10-16: approved; implement as the coordinator sees fit (all six leans). Queued as the next run-physics lane after PW-344/328, together with PW-358 (open-water evaporation, same bulk/humidity physics).
- 2026-10-16: Status todo -> needs-decision. Proposal ready for owner review: docs/proposals/moisture_transport.md (6 decisions with leans). Prototype on local branch pw015-prototype (tools/proto_pw015/): L6/L7 agree within ~2%, Koppen exact 32.7 -> 36%, Sahara 70 mm, Gobi 85, Australia 291; humid subtropics dry out (SE USA 294), wet tropics wetter.
- 2026-10-16: Redesign proposed for owner review: docs/proposals/moisture_transport.md (physical-time conservative kernel, storm eddies, bulk sea evaporation, humid-column showers with an air-mass trigger, shallow heat lows; prototype numbers §4, steps with acceptance §8, decisions §9; prototype on local branch pw015-prototype).
- 2026-10-16: Merged inbox draft draft-polar-storm-track-moisture-half.md ("High-latitude seas get half of GPCP's rain (50-70 deg, both hemispheres), and Antarctica's margins still ~half their snow: the storm tracks bring no moisture of their own", found by polar-bundle).
  After the polar bundle (PW-332's vapour wind and ice-surface lift), Earth L6 at dT 0 still has the high-latitude
  seas at about half of GPCP: sea precipitation 55-60S 433 mm vs 1154, 60-65S 356 vs 861, 50-60N 561 vs 1150,
  60-70N 323 vs 886 (earth_check's ocean columns). Antarctica's margins sit at about half too (bed 0-500 m:
  167 mm vs GPCP 364; 500-1000 m: 198 vs 420), and with them the PW-313 probe's last gap: at dT 0 the sheet still
  loses ~12 margin cells per update (2.33% after 8 updates; with Antarctic snowfall x1.5 as a diagnostic it holds
  at 965 cells, no loss after the 2nd update). The tropical land is too wet by about as much (0-20N land 2034 /
  1403 vs GPCC 1721 / 746), since the global mean is renormalised to 1000 mm.
  
  Why (measured, polar-bundle write-up section 3):
  - Over open sea the kernel refills the air to `rh x qs(sst)` every iteration, so a sea's rain is the local
    rain rate times the local saturation: P ~ ls x qs(sst). Cold storm-track seas (sst 1-4 C) rain what they
    evaporate, ~0.4-0.6 of a 12 C sea's. On Earth the storms carry the subtropics' water poleward (P - E
    ~+300-500 mm/yr poleward of 50 deg) and rain ~2.5x more per unit of vapour than the tropics.
  - The storms' eddy mixing is capped: `diff = clip(0.12 + eddy x B, 0, 1)` is already 1 in every storm track
    (B ~0.8-1.4), so `TUNE['eddy']` x3 changes nothing. At L6 that is one neighbour mix per ~4 h step (K ~2e5
    m2/s against ~1-2e6 for real storm tracks). Extra mixing passes (diagnostic) push vapour onto the
    continents (Antarctica's plateau too wet at 8 passes) but don't wet the seas.
  
  What it needs is PW-015's moisture transport: storms that converge vapour into the storm track and rain it
  there (a storm-track rain efficiency, or eddy moisture flux down the vapour gradient at the storms' scale),
  then re-check the Southern Ocean, Antarctica's margins (PW-332's 100-500 mm) and the probe.
  - [ ] Southern Ocean 50-65S and N Atlantic/Pacific 50-70N sea precipitation within ~30% of GPCP
  - [ ] PW-313 probe at dT 0 steady near 3% over 8 updates without a snowfall multiplier
- 2026-10-14: Created from the rain/overturning epic. Merged: 'Older Earth errors' and 'Also noted: Earth climate errors' (v1), 'Discharge misses come from the rain model' (water), 'No Earth delta comes out tide-dominated' (deltas), morning decision 3(b).
