---
id: PW-479
title: "planet make: which moment of the time zoom is 'now' (glacial, interglacial, or the end)"
type: story
status: needs-decision
parent: PW-244
subsystem: timezoom
effort: s
impact: med
found_by: agent-make-ui
blocked_by: []
relates: [PW-248, PW-472]
refs: [planet/make.py, planet/finish.py, planet/timezoom/]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-248 says the chain optionally runs the time zoom to a "glacial or interglacial now" and finishes the world there. `make` currently finishes the world at the **end** of the time zoom (default 300 kyr from the run's representative moment), whatever the orbit has done by then: on a cold run that can be anywhere between glacial maximum and interglacial. No choice is offered.

Options:
- A: keep the end (simple, deterministic, but the world's character, ice cover and sea level are then luck of the phase).
- B: add `now: "glacial" | "interglacial" | "end"` to the request and the form; pick the stored frame with the lowest (glacial) or highest (interglacial) `sea_level_change_m` after the first 10% of the time zoom (the start is the run's own state), and finish that frame (`finish.finish_timezoom(kyr=...)`). The form gets a three-way choice. Cheap: the frames' stats are in run.json.
- C: B, plus default to interglacial for a "habitable looking" showcase and glacial only when asked.
Lean: B with `end` as the default, C once the owner has looked at a few. The sea-level and ice numbers differ a lot between the two, so this changes how a made planet looks (ice caps, coasts); that is why it is a decision.

## Updates
- 2026-10-20: Created from inbox draft draft-make-glacial-now.md (found by agent-make-ui).
