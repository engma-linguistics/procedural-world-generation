---
id: PW-015
title: Fix moisture transport in the rain model
type: story
status: todo
parent: PW-013
milestone: v1
subsystem: climate
effort: l
impact: high
found_by: daniel
blocked_by: [PW-352]
relates: [PW-019]
refs: [planet/climate.py, tools/earth_check.py, tools/scorecard.py, "plan_next@bdc967f: Known issues → Climate", tools/ice_probe.py, docs/review/audit/polar-bundle.md, tools/moisture_budget.py, docs/review/audit/pw015-rain.md, docs/review/health-rain-s2b/ (removed; see git d32f7fa), docs/review/audit/pw015-handoff.md, tools/overturning_report.py, docs/review/base-climate/handoff-A.md]
created: 2026-10-14
updated: 2026-10-29
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
- 2026-10-29: Lane 25 merged the sea's bulk evaporation exchange: Earth B 20 -> 27-28% (obs 30), BWh 14.5% (14.8), log-rain corr 0.65 -> 0.69. Next: the dry subtropical coasts, PW-998 with PW-026 (v1, owner 10-29).
- 2026-10-29: Lane 25 (branch, 5840dcc6): diagnosis + round 1 committed, round 2 dropped (docs/review/base-climate/deserts/README.md). Diagnosis: the Earth B deficit is summer land rain at the monsoon margins (Sahel, Australia, S Africa, Mongolia, W N America, C Asia, E Africa) with vapour near observed, supply-limited (insensitive to shower rates): land imports ~1.9x the net vapour. Round 1, sea evaporation as a bulk exchange (climate.sea_uptake: C_E 1.3e-3 x max(U, 3) / 500 m toward 0.98 q_sat(SST)): Earth L6 B 20.3 -> 27.3% (L7 19.6 -> 27.6), BWh 9.0 -> 14.5 (Kottek 14.8), exact 34 -> 36, group 71, log-rain corr 0.648 -> 0.691, land rain x1.42 -> x1.31; sea E pattern near NCEP; overturning unchanged. Costs: SE USA 482 (1328), Pampas 294, Japan 524, E Australia 488, Med 383. Paired judge (36 L6): arid +6.7 [5.6, 7.4], hot desert +4.6, trees -4.2, carbon terms unchanged, passes 29 -> 27. Known failure: test_sea_level warm-up bar on L4 seed 1 (-55 vs -50 m), draft. Round 2 (vapour's share of the land-sea circulation, return flow aloft): B 26-31 but log-rain corr down to 0.58-0.62 and India drier; needs a circulation-depth rule (draft, v2).
- 2026-10-28: Owner 10-28: no per-world desert quota. Target only the Earth analogue: on Earth's own map, dry (B) climates should land near Earth's ~30% of land (now ~20%). Generated worlds get whatever deserts their geography and Hadley belts give.
- 2026-10-28: Coordinator 10-28: pulled into v1 as a soundness gap (too few hot deserts: B 20% vs Earth 30%, hot desert 3-5%). The PW-821 attempt shows the rain-side patch alone fails; fix the moisture source.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: Milestone null -> v1 (PW-597 triage, coordinator, 2026-10-23): rain is v1; the owner put sim-physics work back under v1 on 2026-10-22.
- 2026-10-22: Merged inbox draft draft-sea-evaporation-bulk-exchange.md ("Rain kernel: the sea fills the air to src_q instantly each step; a bulk exchange over a fetch moves the overturning and the rain a lot", found by base-climate-laneA).
  For PW-015 (probably `--merge-into PW-015`), and found while working PW-458 (lane A, stage 1).
  
  **The mechanism.**
  - In `climate._rain`, the air over the sea takes up `open_sea × (src_q − q)` per step, with no time constant. Open
    sea refills the air to src_q every step, at once.
  - Through sea ice (open share 0.1, leads) the uptake rate per second depends on the step. The physical-time kernel
    (1416523) steps at 4984 s at L6, against the old 17189 s, so the leads became ~3.4× faster.
  - Sea evaporation is therefore set by what leaves the air, not by an exchange rate. It piles up where dry air first
    meets water, and it is small over open interior seas (Earth L6):
  
    | sea | evaporation (mm/yr) | precipitation (mm/yr) |
    |---|---|---|
    | Baffin Bay | 517 | 237 |
    | Labrador Sea | 92 | |
    | Nordic Seas | 268 | |
  
    Observed, the open subpolar seas evaporate several times more than these, and Baffin far less.
  - That makes Baffin Bay salty (35.2 psu without the overturning), and its brine water the densest in the north. This
    is part of why Earth's overturning sinks in Baffin Bay (PW-458).
  
  **Tried on lane A's branch (commit a11776e; reverted: main's instant fill is back).**
  - A bulk exchange: per step, `1 − exp(−open × wind × dt / sea_fetch_km)` of the deficit is taken up.
    `sea_fetch_km` = 770 (a ~1 km boundary layer / C_E 1.3e-3) and `sea_wind_min` = 3 m/s.
  - Earth L6, HEAD → bulk exchange:
    - **Overturning:** NH sinking 5.1 → 13.0 Sv. The Nordic Seas go 0.1 → 5.9 Sv, Baffin 2.6 → 2.4. The Norwegian Sea
      is 0% → 43% open in winter.
    - **Rain, better:**
      - log-rain correlation 0.617 → 0.659;
      - Köppen arid (group B) share 18.0 → 27.5%;
      - exact match 31 → 34%;
      - the Sahara and Arabia drop off the worst-regions list.
    - **Rain, worse:**
      - land mean 1138 → 1284 mm (GPCC 791), and its 90th percentile 2611 → 3795;
      - group match 71 → 70%;
      - cities in the wrong group 18 → 25;
      - runoff / rain 0.47 → 0.59;
      - the Sahel and East Africa wetter (×4 → ×5).
  - **Generated L6 worlds:** two of three (28442c, 607540) lose their northern overturning (16 → 0 Sv). The shared
    deep-water reference makes the hemispheres compete (see handoff-A).
  - **After stage 1's per-hemisphere deep water** (PW-458, `ocean.overturning`), the exchange no longer helps the
    overturning. On Earth it is **weaker** with it: 7.2 Sv with the fetch against 13.1 with the instant fill, since the
    Nordic Seas are gated out. World 7082f5 is 6.6 against 14.6 Sv
    (`docs/review/base-climate/stages.md`, stage 1). So the exchange is now only a rain question.
  
  **Verdict (parked by lane A, attempt 3).** It isn't merge-ready as it stands: the rain is mixed, and the overturning tips on generated worlds. The
  mechanism is right, though: sea evaporation should be a bulk exchange, and the leads' uptake should be per unit of
  time. What's open:
  - with the exchange, the target humidity `rh` (0.85 of saturation at the sea surface) no longer stands for the
    equilibrium. Should it become the surface's ~0.98?
  - whether the extra land rain comes from the global `mean_mm` renormalisation now that less vapour is taken up near
    the coasts.
  
  - [ ] sea evaporation as a bulk exchange, with the rain no worse overall on earth_check and on a few L6 seeds
  - [ ] re-check the overturning (`tools/overturning_report.py`) on Earth and on generated worlds: the stage-1 bar
    (8–20 Sv in the north, ≥ 70% of it in open polar seas, the Norwegian coast open in winter) must still hold
- 2026-10-16: Scorecard after stage 1 merge: Earth 70.6/30.9, corr 0.617; seeds 1/2 dry 21.3/22.6%, NPP 385/342, tree cover 16.6/29.4% (seed 1 was 29.7: single 1000 Myr snapshot, health sweep 27.0 -> 26.0; checked under PW-387's agent).
- 2026-10-16: Status in-progress -> blocked. Stage 1 (conservative physical-time transport) merged alone under the owner's relaxed bar: generated planets about as main (arid 27.8 vs 29.3%, NPP 321 vs 334, fewer giant-lake frames), Earth Koppen group unchanged, exact -1.8/-2.9 pts, land too wet (~1150 mm vs 791) and arid share 18% vs 30. The wetness is land rain efficiency (showers rain out regardless of the upper air), previously hidden by the old transport's leaks; stage 3 gating waits on PW-352. Stages 2 and A parked on branches pw015-prototype, pw015-wip, pw015-optA.
- 2026-10-16: Merged inbox draft draft-winter-coast-eddy-flux.md ("Winter east coasts: a storm-eddy flux of boundary-layer vapour can't make winter rain without the storms' own lifting, and storminess is high in continental interiors", found by pw015-rain).
  In PW-015 option A, the boundary layer has its own storm-eddy flux, down the gradient of its own vapour:
  `storm_eddies` with `q_eddy`, K = `storm_k_bl` x B, as a velocity -K grad(Q)/Q, with Q the first phase's
  boundary-layer vapour over 800 km. Measured on Earth L6 (box diagnostic, Oct-Mar):
  - **SE USA:** the mean boundary-layer wind is offshore (2.8 E, -1.9 N m/s). The eddy velocity is +1.07 m/s
    onshore (the saturation closure gave 0.64). q_b/qs rises 0.23 -> 0.29, but the winter rain stays ~20 mm/yr
    (obs ~1300 rate). At that humidity the large-scale rain gate (rh/rh_c)^3 is ~0.05. Annual: SE USA +27 mm,
    Pampas +104 (with bl_m 1 km).
  - **Why the Gobi got wetter:** not the free troposphere and not the winter high. The extra Gobi rain falls in
    **summer** (Apr-Sep 668 -> 814 mm/yr rate; Oct-Mar unchanged, ~25). Storminess B there is 0.70 in summer and
    1.08 in winter, about the same as the SE USA's 1.01. That is because `storm_track` grows storms on any
    low-level temperature contrast, including the contrasts inside a continent. The flux also wets the Gobi
    with only the boundary layer carrying it.
- 2026-10-16: Merged inbox draft draft-subtropics-dry-after-bulk-evaporation.md ("PW-015 stage 2 (bulk evaporation + eddies) dries the humid subtropics and generated planets; one cause fixed on the branch, two left (the one-layer column, the winter eddy flux)", found by pw015-rain).
  PW-015 stage 2 (storm eddies + the bulk sea evaporation, commit ecffcb9) and its revision (326e482, on the
  branch, not for merging) were measured on Earth L6/L7 and on 8 L6 seeds (docs/review/audit/pw015-rain.md
  section 9).
  
  **Found and fixed on the branch:** in the cold half the vapour rode the continents' shallow cold outflow off the
  east coasts at full strength. The revision (`rain_phases`) lets the vapour ride only part of a shallow
  land-sea circulation: 0.53 over a winter high or a dry heat low, deeper over a wet low.
  - SE USA 277 -> 757 mm (obs 1328), Sahel 2733 -> 1975, Australia interior 823 -> 463, Gobi 556 -> 196.
  - Koppen 72.2 / 36.2% (main 71.0 / 32.7), log-rain corr 0.685.
  
  **Left:**
  1. **The winter east coasts** (SE USA Oct-Mar PW 4.6 vs NCEP 17.4 mm, Pampas and E Australia likewise): the
     westerlies themselves blow offshore there. The storms' eddy flux on the saturation gradient (storm_k 1.3e6
     x B x q_k grad T over 800 km) gives only 0.3-1.2 m/s onshore; the real Gulf moisture comes in with the
     cyclones. An eddy closure on the actual vapour's gradient helped a little (SE USA +60 mm, Pampas +120) but
     wetted the Gobi.
  2. **The one-layer column under the bulk formula:**
     - The subtropical seas' columns sit at q/qs 0.5-0.6 (PW 20-30N 26 vs 33 mm), so their own rain is low:
       20-40 deg sea P ~300-450 vs GPCP 700-1160, sea E 2056 vs 1689 at 20-30N.
     - So the global mean's share goes to land: land P 1153 vs 791, land 50-60N 1175 vs 584, Amazon 3597 vs 2335.
     - The ITCZ's convergent columns are near saturation, so they evaporate little (0-10 deg 1216 vs 1407).
     - Real surface air over the sea stays at ~0.8 of saturation under a dry free troposphere, which one layer
       can't represent (proposal decision 1, option C).
  3. **Generated planets** (health --quick): arid 29 -> 38% of land, tree cover 27 -> 21%, NPP 334 -> 304, deeper
     icehouses (seed 2 -491 m of ice sea level, past PW-240's -250 m).
  
  Options:
  - (A) A boundary layer under the column: the bulk formula against a boundary-layer humidity kept by
    entrainment from the column (two humidities per cell; the rain's humidity gates read the layer they act on).
    This is decision 1's option C done properly. Cost: one more field in the kernel.
  - (B) Keep one layer and go back to the instant refill (main's) with the storm eddies only: transport
    -0.77 / +0.53 Sv, small gains (proposal section 4).
  - (C) Park stage 2: merge stage 1 alone and revisit after PW-352/PW-026 (the air model's summers and winter
    maritime air).
  
  Lean A, as its own small proposal: every downstream stage of PW-015 rests on the sea's evaporation.
- 2026-10-16: Owner 2026-10-16: if this option-A batch misses the bar, step back rather than keep chasing: consider cruder approximations, partial measures or a relaxed bar. Don't chase Earth perfection.
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
