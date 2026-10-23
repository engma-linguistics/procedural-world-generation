---
title: "Lineages: what happens to a parent people at a split, and what switching one off does"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lineages-lane
blocked_by: []
relates: [PW-103]
refs: [planet/lineages/history.py, planet/lineages/spec.py, planet/lineages/samples/dnd.toml]
---

## Description
Built on the leans below (each a small swap in history.py / spec.py):

1. Parent at a split. A (built): the parent continues until its last living split child appears, then its remaining range is shared among the children by graph-nearest child range (a last vicariance); `persists = true` keeps it (humans in the preset, so halflings can branch off them). A child set to go extinct doesn't count (a side branch dying out leaves its parent alive). B: the parent always continues (more peoples at the present, more overlap). C: every split ends the parent (strict bifurcation; needs binary trees).
2. Switching a line off (editor toggle, `enabled = false`). Built: its split children re-parent to its nearest enabled ancestor (or become roots / arrivals under a disabled root / arrival), keeping the niche they inherited; its hybrids and templates are switched off too (no half-elves without elves). Alternative: cascade-disable all descendants.
3. Extinct-by-T: built as a habitat that dwindles linearly over min(30% of the line's life, 20 kyr) to nothing at T. Alternatives: absorbed into a named hybrid or sister, or a sudden end.

Lean: keep A and the built rules.
