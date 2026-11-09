---
id: PW-1593
title: At L7 the humans are now 56-66% of all people, after the stem-refuge change (PW-1558), with polities on or off
type: task
status: done
parent: null
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane245
blocked_by: []
relates: [PW-1558, PW-1587]
refs: [planet/lineages/history/dispersal.py, planet/lineages/history/origins.py, "planet/lineages/history/params.py::LAST_LAND_REACH", docs/review/culture/polities/round17.md, docs/review/culture/polities/round17/shares.py, "world 899985", "time zoom fc5311", "scratch l245 data7 runs 7bf29c b08650 (off, main ad780a26)", "scratch l234 runs 0a1c30 7de58b (off, code 5723d08c)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** On world 899985 (L7, dnd tree), the humans make up 66% of all people now on seed 7 and 56% on seed 10, with
polities in the history switched off, on today's main. Before PW-1558 (lane 233, commit 12f38974: an empty stem holds out within
reach of its last land) the same seeds gave 40% and 61%. On seed 7 the change shows 38,000 years ago, long before any polity
(humans 9% before, 26% after), so it is the deep history's draws, not the polities. Lane 245 measured this while checking PW-1587;
nobody has looked at whether one people holding two-thirds of the world is what PW-1558 meant, or chance on two seeds.

**What misleads if never done.** Round 16 and the coordinator read the 65% as the polities' doing; anyone comparing runs across
that commit will again blame whatever lane they are testing. And a world where one people is two-thirds of everyone is the kind
of brittle outcome the peoples model should not give often (robust, not brittle).

- [x] the humans' share at L7 over 3+ seeds (and the lane 77 stress suite if cheap), before and after 12f38974
- [x] if the share is high on most seeds: which part of PW-1558 (founding near the last land, or holding out) feeds the humans

## Findings (lane 249)
World 899985 (L7), dnd tree, 30 kyr recent, polities off, languages skipped, peoples history only (a lane runner: `HP.POLITIES_LIVE =
False`, `planet.language.run.write` stubbed, `PLANET_DATA` a scratch root with the world and its source runs symlinked; 27-38 min per
run under load 20-35). "After" is main 4fccab70; "before" is the same code with `git revert 12f38974` applied in a scratch worktree
(not committed). Humans' share of all people now:

| seed | before 12f38974 | after (main) | largest is |
|---|---|---|---|
| 7 | 39.0 | 66.0 | humans both |
| 10 | 69.6 | 56.4 (lane 245's b08650) | humans both |
| 3 | 57.1 | 67.5 | humans both |
| 5 | 49.9 | 48.2 | humans both |
| mean / median | 53.9 / 53.5 | 59.5 / 61.5 | |

Reading: humans are the largest people, and about half of everyone, on this world with or without PW-1558. The change moves the
share by -13 to +27 points per seed with no consistent sign (2 of 4 up by 10+, 2 down; mean +5.6). So two-thirds on seeds 7 and 10
was a high draw on a world where humans are already near half; seed 7's 40% was the low draw. PW-1558 does shrink the peoples that
used to be teleported (seed 7 now: hobgoblin 13 M, halfling 7 M, leonin 5 M; before: 123, 116, 55 M): the range-bar trade of
PW-1577 (they start inside the humans' country and stay at the share floor), so the humans gain a little from it, not through a bug.
No code changed: giving those peoples room again is the separate mechanism PW-1577 option C names (more sea crossings for pre-boat
peoples, PW-888's across-sea founding weight), not the refuge. Not run: seed 11, the lane 77 stress suite (L6 worlds only, 40 min a run).

## Updates
- 2026-11-09: Status todo -> done. Lane 249 (29569610, findings moved here): humans ~half of all people on 899985 with or without PW-1558 (mean 53.9 -> 59.5% over 4 seeds, no consistent sign). No code change; room for the shrunken peoples is PW-1577 option C.
- 2026-11-09: Created from inbox draft draft-l7-humans-over-half-after-pw1558.md (found by lane245).
