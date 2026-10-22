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
- 2026-10-22: Stage 1 in progress on branch worktree-agent-aa70af297efc2b900 (not for merge yet). Earth baseline on main added to checkpoint-0.md: Earth meets its zoom bars only at 6.5 C (at 6 C its first glacial is -73 m); the Earth staircase holds today's ice at dT 0 but keeps 44% of a cold era's extra ice back at dT 0. Zoom-only changes: margin_ramp, seasonal_k, sheet air from frozen summers (sheet_air=cold), ice-surface terms on the non-sheet air (surface_air=rest); the run untouched (consistency test runs the run's rules). Diagnosis: the carried sheet air on ramp margins is what stops endings (removing it: give-back 0.42 -> 0.82); isostatic lag, calving and dynamic thinning aren't. Checkpoint 1 at 5.5 C: cycles, maxima -108..-138, give-back 0.64-0.91 pass; interglacial ice 12-15% of land fails (bar 9-12); window mean 2/6 -> 3/6; L4 endings test fails. One attempt left on the lever. docs/review/ice-v2/stage-1.md, handoff-stage1.md; drafts in the inbox.
- 2026-10-22: Stage 0 done on branch worktree-agent-abf55f5e1e8b62d98: criteria doc docs/review/ice-v2-criteria.md (Earth's record, base assumptions A0-C5, new whole-history bars, recovery lever design), tools (tectonics/diag.py + ice_diag, ice_criteria, tz_mean, ice_probe --stair, sea_ice_m/sea_tect_m in stats and health; no output change), checkpoint 0 in docs/review/ice-v2/checkpoint-0.md: old bar 8/10, new 5/10; icehouse share median 62%; CO2 clip never reached, the thermostat barely answers cold eras; deep-era sheets in snow surplus; window mean 2/6; Earth items blocked by a failed Koppen download. Drafts in the inbox. Handoff docs/review/ice-v2/handoff.md.
- 2026-10-21: Owner 2026-10-21: the first ~100 Myr of a run is warm-up while the coupled systems settle; it shouldn't count toward success bars.
- 2026-10-21: Status needs-decision -> in-progress. Owner 2026-10-21: plan approved as described. Prefers option 2 (the run runs the zoom's ice model in cold eras), extra run time fine. Agrees with all nine leans in the review. Work proceeds on a v2 ice worktree, merging main as things land. Owner also asks: (1) revisit the success criteria: they're anchored on Earth's last glacial, but the record has snowball Earths (Cryogenian) and hothouses (PETM); deep, long ice ages are fine if a planet can come out of them. (2) What are the base assumptions, and which might be off? (3) An optional generation-time lever: the longer a deep ice age lasts, the harder the systems nudge toward recovery, easing off as the planet recovers. (4) Build measuring tools first; runs may take far longer and use much more storage if that helps debugging.
- 2026-10-21: Created from inbox draft draft-ice-v2-plan.md (found by ice-v2-review).
