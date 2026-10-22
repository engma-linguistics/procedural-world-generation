---
id: PW-555
title: "Ice ages v2 plan: honest margins that deglaciate in the zoom first, then one ice model (run cold eras from short zoom integrations) vs a sheet-wide budget, decided by a spike"
type: task
status: in-progress
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: ice-v2-review
blocked_by: []
relates: [PW-470, PW-526, PW-514, PW-461, PW-462, PW-464, PW-465, PW-467, PW-469, PW-459, PW-460, PW-538, PW-496, PW-030, PW-549]
refs: [docs/review/ice-v2-review.md, docs/review/audit/ice-framing-deep-dive.md, docs/review/audit/PW-514-batch.md]
created: 2026-10-21
updated: 2026-10-22
---

## Description
The owner asked (2026-10-21) for a holistic review of the ice-age work before v2. It is in
`docs/review/ice-v2-review.md`: how ice works end to end, a chronology of about 22 attempts with numbers, the root
causes, what to keep, four v2 options and a staged plan.

Root causes that recur:
1. The run (an equilibrium extent: no flow, no budget) and the time zoom (a flowing sheet) are two different ice
   models. Each shared fix breaks one side.
2. The run's hysteretic fixed point has no sheet-scale deglaciation. The 408 m margin edge was an error doing a
   brake's job: PW-460/459 and the PW-514 batch give cold eras 0-1/10.
3. Saturated CO2 and albedo feedbacks give two branches (PW-030/440).

Options (section 5 of the review):
- **1. Sheet-wide budget in the run's fixed point** (PW-526 A). A sheet in deficit thins its Nye surface. m-l, ~0
  cost, medium risk. It keeps two models.
- **2. One ice model, two clocks.** The run's icy climate updates integrate the zoom's ice core for a short,
  warm-started window under the glacial index, and store the mean, interglacial and glacial states. l-xl. Estimated
  +15..+35% wall on icy runs (to measure). It removes the run/zoom gap by construction.
- **3. State-forced cycle** (PW-464 + PW-538 A) on top of 1 or 2. It fails on its own (the batch).
- **4. Emergent cycles** (retire the index). xl, high risk. Defer.

Lean:
- Stage 0: PW-467 harness and moment suite, after coast_loss lands.
- Stage 1: make the zoom deglaciate with `margin_ramp`/`seasonal_k`. Checkpoint: Earth bars at a cooling of ≤ 6 C.
- Stage 2: spike option 2 against option 1. Choose 2 if its L6 cost is ≤ +35% and its window mean matches a full
  zoom; else 1.
- Stage 3: build the chosen run side with PW-460/459 and PW-464's stored states.
- Stage 4: window, phase picker, imprint depth.
- Keep the glacial index as v2's driver.

Decisions for the owner (review section 7, each with a lean): the approach, the run-time budget, keeping the index,
PW-538's cooling share, re-applying PW-460/459, the cold-era depth bar, Earth's start, imprint depth, and the stop
rules.
- [ ] owner picks the approach and the cost budget
- [ ] stage 0 tickets cut (PW-467 tool, moment suite, ice/basin split in health, hysteresis probe)

## Updates
- 2026-10-22: Stage 1c on branch worktree-agent-a339320374f6026c2 (lane, not for merge). New lever, the margin balance at today's climate. Yardstick tools/tz_earth.py --dt0 (index off, 100 kyr) and an observed SMB, RACMO2.3p3 2001-2018, cached in data/earth (tools/earth_data.py; tools/tz_earth.py --greenland). RACMO: the outer 110 km of Greenland +0.15 m/yr; L6 margin cells -0.02 vs the zoom's +0.21, inland +0.29 vs +0.28. Suspects: (a) ramp quadrature no effect; (b) front=ramp (the new front as the ramp's outer 10 km with the fetch share) kept: dT-0 ice 1.30 -> 1.17 of today's, the recovery bar passes, but it doesn't follow the orbit; (c) caps in place are the base climate's cold mountains. Checkpoint 1c: maxima -49..-93 at 5.5-6 C (fail), give-back 0.51-0.85 (fail), interglacials 11.4-13.1% (fail); suite 4/7 with area (fixture and s1@540 added); L4 test fails (83.4 of 78.2 m left). The lever is spent. Left: Greenland's N/E margin summers 2-5 C too cold (the ice-surface air) and the run-side gap (stage 3). stage-1.md "Stage 1c"; handoff-stage1c.md.
- 2026-10-22: Stage 1b on branch worktree-agent-a059022acff222eac (lane, not for merge). Attempt 3 on the air lever kept: surface_air=fetch, the ice surface's own terms on the share of its air that has come over ice within 500 km (Greenland margins -6.1 -> -3.9 C vs ~-2.7 observed on their ice, inland -8.0 -> -6.2 vs -4.9, Antarctica +4.9 -> +3.3). Earth at 5.5 C: cycles, maxima -89..-118, give-back 0.62-0.82 pass; interglacial ice 11.8-15.5% fails. Suite mean 4/5, mean and area 3/5 (s5@420 +69 m: run-side). The air lever is spent. Base climate tried in its decisive form (baseline=obs): ig ice 11.4-12.9%, depth and give-back lost. Root finding: with the index off, Earth's zoom grows 3-4 Mkm2 in the first weak summer and keeps it (11.5-12.6% of land at dT 0; main's rules come and go with the orbit), so the interglacials sit on a dT-0 floor; the recovery bar fails. The L4 endings test also fails at L5 (0.83 left), and the ramp quadrature is accurate: no resolution limit. Next suspect: the margin balance at today's climate (Greenland's margin cells +0.20 m/yr), needs an observed SMB; owner's call. stage-1.md "Stage 1b"; drafts updated/added; handoff-stage1b.md.
- 2026-10-22: Stage 1 in progress on branch worktree-agent-aa70af297efc2b900 (not for merge yet). Earth baseline on main added to checkpoint-0.md: Earth meets its zoom bars only at 6.5 C (at 6 C its first glacial is -73 m); the Earth staircase holds today's ice at dT 0 but keeps 44% of a cold era's extra ice back at dT 0. Zoom-only changes: margin_ramp, seasonal_k, sheet air from frozen summers (sheet_air=cold), ice-surface terms on the non-sheet air (surface_air=rest); the run untouched (consistency test runs the run's rules). Diagnosis: the carried sheet air on ramp margins is what stops endings (removing it: give-back 0.42 -> 0.82); isostatic lag, calving and dynamic thinning aren't. Checkpoint 1 at 5.5 C: cycles, maxima -108..-138, give-back 0.64-0.91 pass; interglacial ice 12-15% of land fails (bar 9-12); window mean 2/6 -> 3/6; L4 endings test fails. One attempt left on the lever. docs/review/ice-v2/stage-1.md, handoff-stage1.md; drafts in the inbox.
- 2026-10-22: Stage 0 done on branch worktree-agent-abf55f5e1e8b62d98: criteria doc docs/review/ice-v2-criteria.md (Earth's record, base assumptions A0-C5, new whole-history bars, recovery lever design), tools (tectonics/diag.py + ice_diag, ice_criteria, tz_mean, ice_probe --stair, sea_ice_m/sea_tect_m in stats and health; no output change), checkpoint 0 in docs/review/ice-v2/checkpoint-0.md: old bar 8/10, new 5/10; icehouse share median 62%; CO2 clip never reached, the thermostat barely answers cold eras; deep-era sheets in snow surplus; window mean 2/6; Earth items blocked by a failed Koppen download. Drafts in the inbox. Handoff docs/review/ice-v2/handoff.md.
- 2026-10-21: Owner 2026-10-21: the first ~100 Myr of a run is warm-up while the coupled systems settle; it shouldn't count toward success bars.
- 2026-10-21: Status needs-decision -> in-progress. Owner 2026-10-21: plan approved as described. Prefers option 2 (the run runs the zoom's ice model in cold eras), extra run time fine. Agrees with all nine leans in the review. Work proceeds on a v2 ice worktree, merging main as things land. Owner also asks: (1) revisit the success criteria: they're anchored on Earth's last glacial, but the record has snowball Earths (Cryogenian) and hothouses (PETM); deep, long ice ages are fine if a planet can come out of them. (2) What are the base assumptions, and which might be off? (3) An optional generation-time lever: the longer a deep ice age lasts, the harder the systems nudge toward recovery, easing off as the planet recovers. (4) Build measuring tools first; runs may take far longer and use much more storage if that helps debugging.
- 2026-10-21: Created from inbox draft draft-ice-v2-plan.md (found by ice-v2-review).
