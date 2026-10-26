---
id: PW-866
title: Take the finished world at the latest human-habitable moment near the run's end, not always at the end itself
type: task
status: done
parent: PW-244
milestone: v1
subsystem: timezoom
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-865, PW-807]
refs: [planet/cli.py]
created: 2026-10-25
updated: 2026-10-26
---

## Description
Owner, 2026-10-25: Earth itself has spent most of its history unfit for people. Choosing a moment near the end that suits people is "choosing the right kind of moment", not a kludge. Earth passes all of the finish checks (true mean -6..+3 C, interglacial land ice ~Earth's, forested wet tropics, CO2 >= C3 limit) only in roughly the last 3-5 Myr: the Pliocene and Pleistocene, plus perhaps parts of the Late Paleozoic Ice Age. That is well under 5% of its last 540 Myr.

Proposal: `--at auto` picks the latest moment within a bounded window before the run's end (window size set from v1-finish-13's moment-search diagnostic: 5/10/20 Myr) that passes a cheap run-trace screen; the time zoom and finish run there. A draw with no passing moment in the window fails.

Design points:
- The plant calendar and the star stay counted from the run's end. The window must stay short enough that grasses (~70 Ma) and C4 (~30 Ma) still hold. Alternatively, relabel the chosen moment as "now".
- The deep-time bar (PW-865) still judges the whole history.
- Report how far back the chosen moment sits.
- This must not hide model bugs. The per-moment finish rates stay diagnostics, and the physics fixes (light, drift) go ahead regardless.

## Updates
- 2026-10-26: Status todo -> done. Merged: finish at the latest moment in the last 10 Myr passing the finish checks. Bar+checks at the moment: L6 15/18, L7 7/8 (end-only 10/18, 5/8). Earth group 71%.
- 2026-10-25: RULING (owner): approved. Run the last ~10 Myr at a ~0.5 Myr climate step and choose the finish moment from those candidates.
- 2026-10-25: Owner 2026-10-25: wants many candidate steps to choose a near-ideal moment from. Several measures together: the deep-time bar on the whole history, the finish checks at the chosen moment, the look-back, and the pass rate at the very end. Run climate is every 4 Myr (keyframes) and the time zoom is 300 kyr, already set at an interglacial. Plan (coordinator): run the last ~10 Myr at a finer climate step (~0.5 Myr) to give ~20 candidate moments, window ~5-10 Myr, then the time zoom at the best one. Waits for the carbon fixes (v1-finish-13).
- 2026-10-25: Created from inbox draft draft-finish-at-a-habitable-moment.md (found by coordinator).
