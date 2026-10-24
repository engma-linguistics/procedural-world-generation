---
id: PW-706
title: "'near' wishes are all contested on the D&D preset, so the PW-699 rule changes nothing there; the fire giants' misses are real"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-3
blocked_by: []
relates: [PW-699, PW-682]
refs: [planet/lineages/history.py, planet/lineages/samples/dnd.toml]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-699 (A) is built: a 'near' wish is scored only where the two niches can reach each other (baseline >= `APART_CONTESTED`, same rule as 'apart'); `wishes_counted` and the run page show it. On L7 worlds 1df1c3 and 3e9e7d all 7 'near' wishes have a baseline of 0.60-1.00 (fire_giant near hobgoblin/dwarf/human: 0.93-1.00), so every one is still counted and the scores are identical before and after (4 tries each, same seeds). The rule is a guard for trees whose niches never meet; it does not help the fire giants.

The giants' misses stay real and seed-dependent: fire_giant near hobgoblin scores 0.0 / 0.8 / 1.0 and near dwarf 0.0 / 1.0 across tries, because their habitat is narrow and the x1.5 nudge cannot move them (PW-699's original observation).

Options:
- A: accept (a narrow-habitat people is where its habitat is; the wish stays a soft preference that sometimes fails).
- B: strengthen the pull for strict-use peoples (the option the owner did not pick for PW-699), or score the wish against the niche baseline per cell like 'apart' (1 - closeness / baseline).
- C: let a 'near' wish with weight 1 move the habitat itself (x(1 + w) at the border, a gap of at most one niche).

Lean: A, and look again once the tries' spread (a wish score moves 0.70-0.81 between seeds) is smaller than the effect being tuned.

## Updates
- 2026-10-23: Status needs-decision -> done. Accepted: the rule stays (it bites on other trees); the fire giants' misses are real dynamics, not this rule.
- 2026-10-23: Created from inbox draft draft-near-wish-contested-rule-is-a-noop.md (found by fun-lane-3).
