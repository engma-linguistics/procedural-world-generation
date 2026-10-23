---
id: PW-613
title: "Lineages: contact hybrids (half-elf, half-orc) are lost when their parents stop meeting"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: lineages-lane-3
blocked_by: []
relates: [PW-598]
refs: [planet/lineages/history.py, "peoples runs 3cf7fe (1144ce), 5cdd4a (3e0b0a)"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
A contact hybrid (`contact = true`) exists only where both parents hold at least EST. In the L7 showcase it was lost at the present twice:
- half-elves on 1144ce (run 3cf7fe), in both tries;
- half-orcs on 3e0b0a (run 5cdd4a).

Lane 2's L7 runs kept them, so this depends on the seed. Lane 3 made best-of-N take 0.05 off a try's score for each living line it lost, but both tries lost the same line.

Options:
- A: accept it. The peoples no longer meet, so the hybrid people is a memory. Report it as such instead of listing it as "lost".
- B: once a contact hybrid has appeared, it lingers as a small people of its own (non-contact) where its parents last met.
- C: a stronger lost penalty, or more tries.

Lean: B. A half-elf people that outlives the contact is plausible and game-useful.

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-contact-hybrids-lost.md (found by lineages-lane-3).
