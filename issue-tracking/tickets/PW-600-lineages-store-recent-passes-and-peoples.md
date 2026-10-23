---
id: PW-600
title: "Lineages: store recent passes and peoples as time-zoom-kind runs, or a kind of their own?"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: store
effort: m
impact: low
found_by: lineages-lane
blocked_by: []
relates: [PW-103, PW-473]
refs: [planet/lineages/output.py, planet/lineages/recent.py, planet/family.py, viewer/index.html]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Built: both are runs with `kind: timezoom` and `meta.phase` ('recent' / 'lineages'), time in kyr before the present (t <= 0), so the viewer's time-zoom UI plays them (slider, events, layers; a phase summary replaces the glacial chart, the peoples panel lists the tree). Side effects: the family tree (family.py) lists them as time zooms of the planet (parent: the source run, not their time zoom or world); "Finish world here" isn't meaningful for them (hidden by the phase summary); `planet list` shows them as time zooms.

Options: A (built, lean) keep the phase runs, and nest them under their time zoom / world in family.py and the navigator (small additive change, `meta.timezoom` / `meta.world` are stored); B a new store kind `lineages/` with its own index, viewer tab and family node (cleaner, more code).
- [ ] if A: family.py nests phase runs under meta.timezoom (or meta.world), navigator labels them "recent pass" / "peoples"

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-store-kind.md (found by lineages-lane).
