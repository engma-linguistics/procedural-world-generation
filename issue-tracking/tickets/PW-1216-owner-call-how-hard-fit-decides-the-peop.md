---
id: PW-1216
title: "Owner call: how hard fit decides the peoples' contest (FIT_CLIP 3, BREADTH_Q 0.5, martial 1.5)"
type: task
status: needs-decision
parent: PW-917
milestone: later
subsystem: highlights
effort: xs
impact: med
found_by: lane83
blocked_by: []
relates: [PW-1180, PW-1149]
refs: [planet/lineages/history/params.py, planet/lineages/history/competition.py, docs/review/peoples-d20/report.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
**In plain words:** where two peoples share a cell, each now presses on the other by how well the land there suits it (ruling D20
(1)). Four numbers set how strong this is. All four are guesses, with no data behind them:
- **FIT_Q 1:** a people at the edge of its country (fit 0.4) presses 0.4× as hard there as one at home (fit 1).
- **BREADTH_Q 0.5:** a specialist presses harder. A people with a quarter of the other's range presses 2× as hard: a niche people beats
  a broad one in the land it is built for.
- **FIT_CLIP 3:** no weight goes above 3× or below 1/3×, so no people is invincible.
- **martial 1.5:** dwarves and hobgoblins press 1.5× as hard (ruling D20 (5)).

Options:
- A. Keep these numbers.
- B. Make the contest stronger (FIT_CLIP 5, BREADTH_Q 0.75). The narrow peoples would hold their niches more firmly. The risk is a
  specialist that can't be displaced anywhere it fits.
- C. Make it weaker (FIT_CLIP 2). That is closer to the old contest, where the broad farmers take most of the land.

Lean: A. Judge it on the stress suite, not on single seeds. The numbers are in docs/review/peoples-d20/report.md.

## Updates
- 2026-11-03: Status done -> needs-decision. Coordinator 11-03: reopened. D31 paused share tuning, which parks this rather than deciding it; kept as a parked decision for Daniel.
- 2026-11-03: Status needs-decision -> done. Closed 11-03: option A (keep FIT_CLIP 3, BREADTH_Q 0.5, martial 1.5) is what is built (params.py, overview 2.26) and D31 (10-31) ruled to stop fiddling with peoples shares; revisit judged on the stress suite only if the mechanism ledger (D44) asks.
- 2026-10-31: Created from inbox draft draft-peoples-fit-contest-knobs.md (found by lane83).
