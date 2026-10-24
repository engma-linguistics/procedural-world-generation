---
id: PW-778
title: "Marine peoples v0 follow-ups: the viewer's peoples layer at sea, and the deep folk's trench and vent habitat"
type: task
status: todo
parent: PW-729
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: fun17
blocked_by: []
relates: [PW-729, PW-775]
refs: [planet/lineages/history.py, planet/lineages/output.py, viewer/, planet/lineages/samples/seven_meals.toml]
created: 2026-10-24
updated: 2026-10-24
---

## Description
fun17 built the coast and sea realms (PW-775 steps 1 and 2): `realm = "coast" | "sea"` on a line, merfolk on the shallow shore ring,
storm giants on open water, contacts and the brief's `sea_peoples`. Left out on purpose (light v0):
- **Viewer**: the `peoples` layer already carries the sea cells (index into `meta.lineages`, same legend), but the peoples legend,
  hatch for sea presence, the range/area read-outs and the peoples editor have not been checked with sea cells; the editor has no
  `realm` field (a custom line cannot be made marine from the UI; `spec.to_raw` keeps it for a tree edited as JSON).
- **Deep folk** stay authored (owner): in `seven_meals.toml` they keep their coastal land stand-in (`deep_folk`, traits swims/coastal/insular).
  That stand-in puts them on land coasts, which is wrong for a people with no fire living at vents; either drop the stand-in range (a
  line with no habitat is "lost") or give them a `realm = "sea"` with a depth band and vent cells when the tectonics volcano table
  exposes ridge/arc vents at sea. Their facts (no fire, brine curing, vent intoxicant) are the culinary side's.
- [ ] viewer: legend and hatch at sea, editor `realm` select
- [ ] decide the deep folk's stand-in (see above)

## Updates
- 2026-10-24: Created from inbox draft draft-marine-peoples-viewer-and-vents.md (found by fun17).
- 2026-10-24: fun21: map half done in viewer/index.html: marine peoples drawn on sea cells (their colour over the ocean, plain/whole/blend layers), legend "(at sea)", panel marks "sea people, shore ring / open sea", hover card too; checked on run 104de8 (merfolk, storm giants). Editor realm select, hatch and sea area read-outs left (draft-peoples-editor-realm-select).
