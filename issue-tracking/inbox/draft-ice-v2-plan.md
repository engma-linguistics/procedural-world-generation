---
title: "Ice ages v2 plan: honest margins that deglaciate in the zoom first, then one ice model (run cold eras from short zoom integrations) vs a sheet-wide budget, decided by a spike"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: ice-v2-review
blocked_by: []
relates: [PW-470, PW-526, PW-514, PW-461, PW-462, PW-464, PW-465, PW-467, PW-469, PW-459, PW-460, PW-538, PW-496, PW-030, PW-549]
refs: [docs/review/ice-v2-review.md, docs/review/audit/ice-framing-deep-dive.md, docs/review/audit/PW-514-batch.md]
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
