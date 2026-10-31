---
id: PW-1206
title: "Proposal: hostile peoples hunt each other down locally, by the dragons' persecution rule (kill against breeding: goblins bounce back)"
type: task
status: needs-decision
parent: PW-917
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lane84
blocked_by: []
relates: [PW-1172, PW-1169, PW-1068, PW-661]
refs: [planet/lineages/history/megafauna.py, planet/lineages/history/competition.py, planet/lineages/compose.py, docs/review/peoples-counterpressures/design.md, docs/review/peoples-why/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## In plain words
You asked whether the model has anything like "too many goblins, so the neighbours hunt them down locally, and they bounce back". It
does not. Peoples only ever compete for room; nobody kills anybody. The model does have exactly that rule for dragons and giants:
the peoples' kill presses them below their natural numbers, and a kind that breeds fast keeps more of its numbers. The same rule could
run between hostile peoples. Goblins next to humans would then live thinner on the border and fill back in when the pressure lets up.

## Description
Today: no war, raids or killing between peoples anywhere in planet/lineages (grep; settlements.py:41 "Not modelled in v0: war and
raids"). Peoples interact only through the competition for room (competition.py:24-99: niche overlap, closed-country exclusion,
frontier invasion, displacement at TAU_KYR, the HOLD_MIN lapse) and through hybrids and contacts.

The megafauna rule (megafauna.py: `kill`, `kept`, `local_density`): kill effort = KILL_Q x the persecutors' people per km² x their
means; a kind keeps 1 / (1 + effort x vulnerability / r) of its natural density, r its breeding rate. Proposal: the same form on a
people k, the effort from its hostile neighbours (cohabitation < 0.5, compose.cohabitation, within reach of their range), r from
lane 78's life tables. Its output is a cut to K on the border cells (the one plug lane 82 designed: PW-1165).
What it does and does not do (lane 82's finding, PW-1169): deaths alone press slow breeders far harder than fast ones, so this gives
the "they bounce back" story for goblins and kobolds but is no brake on them; it would thin elves and dwarves on hostile borders.
Options:
- A. Build it as part of PW-1172 (war) with its era dials.
- B. Only for authored hostile pairs (an 'apart' wish with weight), as story, not as a population brake.
- C. Leave it out; numbers stay set by land and density.
Lean: B first (cheap, readable, shows on the map), A with the war ticket.

## Updates
- 2026-10-31: Created from inbox draft draft-peoples-persecute-peoples.md (found by lane84).
