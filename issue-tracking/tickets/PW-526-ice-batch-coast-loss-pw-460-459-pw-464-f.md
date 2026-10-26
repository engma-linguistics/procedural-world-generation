---
id: PW-526
title: "Ice batch (coast_loss + PW-460/459 + PW-464) fails: with honest margins neither the run nor the zoom can deglaciate a big sheet (cold eras 1/10, Earth interglacials 16-20% iced)"
type: task
status: wontdo
parent: PW-470
milestone: v2
subsystem: tectonics
effort: l
impact: high
found_by: pw514
blocked_by: []
relates: [PW-514, PW-464, PW-460, PW-459, PW-465, PW-461, PW-515]
refs: [docs/review/audit/PW-514-batch.md, planet/tectonics/earth.py, planet/icemass.py, planet/timezoom/sim.py]
created: 2026-10-21
updated: 2026-10-26
---

## Description
Branch `worktree-agent-ae1d70b30254180ac` holds all three pieces together. PW-464 is built as
`earth.cycle_ice`: glacial-index states, a warm-half-orbit interglacial, and only the interglacial
carried. The cost is cut to +4% wall at L6.

Results (docs/review/audit/PW-514-batch.md):
- 10-seed cold-era check: 1/10 (main 8/10), worst -421..-715 m.
- Earth zoom maxima: -141..-182 m (bar -86..-104).
- Earth interglacial ice: 16-20% of land (bar 9-12).
- Consistency test: +40.7 m at I = 0.

The interglacial fixed point itself freezes in cold eras. In the zoom, endings can't clear the sheets
once margins are ramps (PW-460).

Options:
- (A) A sheet-wide mass balance in the run's fixed point: a sheet in deficit under its climate thins,
  lowering its Nye surface by the deficit, before the extent test. In the zoom, look at why ramp margins
  don't retreat after an ending (dynamic thinning, the front's balance).
- (B) PW-461 B(3): the run's cold eras from a short zoom-like integration.
- (C) Park PW-460 (keep the 408 m edge, which brakes the sheets crudely). Cherry-pick only the cost cut
  for coast_loss (PW-514 option A).

Lean: (C) now, plus the cost cut. (A) as the next ice-physics attempt under PW-470.
- [ ] decide

## Updates
- 2026-10-26: Status todo -> wontdo. Wontdo: a result record, kept as a note under PW-555. (PW-900 backlog reorg).
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-21: Status needs-decision -> todo. Owner 2026-10-21: park the batch. Take PW-465 coast_loss with the cost cut (PW-514 option A) onto main if it holds up. For v2, a holistic review of ice-age work first: what's been tried and what didn't work.
- 2026-10-21: Created from inbox draft draft-honest-margins-need-sheet-deglaciation.md (found by pw514).
