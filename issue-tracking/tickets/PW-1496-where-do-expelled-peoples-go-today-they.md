---
id: PW-1496
title: "Where do expelled peoples go? Today they simply die (live polities: kept / thinned / expelled)"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane204
blocked_by: []
relates: [PW-1465, PW-1487, PW-1481]
refs: ["planet/lineages/history/polity_live.py::LivePolities._fates", "planet/lineages/history/polity_live.py::harshness", "planet/lineages/history/polity_live.py::FATE_CUT", "planet/lineages/history/polity_live.py::FATE_MAX", docs/review/culture/polities/round11.md, docs/review/culture/polities/round10.md, docs/review/cultures-proposal/proposal-r2.md, "world 899985"]
created: 2026-11-07
updated: 2026-11-07
---

## Description
**In plain words.** With polities in the history (the switch), a conqueror now keeps, thins or expels each people on the land it
takes, by its own tolerance and aggression (PW-1481, and since lane 204 the martial, intolerant ones expel: D59 C). But an
"expelled" people is simply removed: 80% of its presence on the taken land is lost (more for an aggressive winner), and nobody
arrives anywhere. So every expulsion reads as a massacre. Real expulsions mostly made refugees: the exiles went to their own
kin's land or to whoever would take them (proposal-r2 3.3 records your P3 B ruling: intolerant winners "expel, enslave or
exterminate a share").

What misleads if never decided: the v4 card will say "expelled" while the heads silently vanish; peoples' shares under the switch
shrink where they should move. Since D59 C makes expulsion common for martial, intolerant winners (round11.md section 2), this
now matters more than before.

**Options.**
- A. Keep: the expelled are lost (now). Simple; expulsion = razing.
- B. The expelled move: the heads cut by an "expelled" fate are added to the same people's nearest land the winner does not rule
  (spread over its cells there, by its existing density); only if it has none are they lost. "Thinned" stays a loss (war deaths).
- C. Split by the winner's aggression: an expulsion by a winner of aggression above the martial mark razes (lost, as A), below it
  drives out (moves, as B). Genghis Khan's sacks and the Assyrian deportations both happen, from the same rule.
Lean: C. It is B's mechanism (refugees), and keeps D59's "a martial winner razes" literal. The share moved needs no new number
(the existing cut is the share). Effort small: one pass in `_fates` after the cut.
- [ ] Daniel picks; then measure on seeds 7, 10, 3 (round11/measure.py) against the round 11 runs.

## Updates
- 2026-11-07: Status needs-decision -> todo. Daniel 11-07: D61 C. A very martial winner razes (lost), a less martial one drives the people out to its own nearest land the winner doesn't rule.
- 2026-11-07: Desk D61 (lean C).
- 2026-11-07: Created from inbox draft draft-expelled-peoples-go-where.md (found by lane204).
