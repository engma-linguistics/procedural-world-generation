---
id: PW-1255
title: "Three-people tree on world 4360a3: humans 99% even with the raider brakes off, since the inland pits"
type: task
status: todo
parent: PW-917
milestone: later
subsystem: peoples
effort: s
impact: med
found_by: lane101
blocked_by: []
relates: [PW-1239, PW-1240, PW-1229, PW-1218]
refs: [docs/review/peoples-leader/data.json, tools/peoples_robust.py]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** The suite's three-people tree (humans, kobolds, goblins) fails the "nobody above 85%" rule on world 4360a3 in
every try. Lane 97 blamed the brakes. On the code after the inland pits it is not the brakes: with the raiders' dial at x0 the humans
are still 99% there (seeds 7 and 10; lane 97, before the pits, had 90% at x0). The kobolds' broken country on that world seems to
have changed with the new land. On af2677 the brakes do matter (82% humans at x0, 87-90% with them).

- [ ] where the dnd3 kobolds of 4360a3 found before the pits and where they found after (their origin and first land), to see what
  the new land took from them
- [ ] then decide whether this tree is a fair test of the brakes on that world

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-11-01: Created from inbox draft draft-dnd3-4360a3-humans-99-without-brakes.md (found by lane101).
- 2026-10-31: Created by lane 101.
