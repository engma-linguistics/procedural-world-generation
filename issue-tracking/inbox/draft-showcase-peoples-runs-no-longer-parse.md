---
title: "The showcase peoples runs (b4d502, 3c1caf, a24559) no longer parse: the viewer's whole-people Culinary brief fails on them"
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: xs
impact: high
found_by: lane164
blocked_by: []
relates: [PW-1275, PW-1391, PW-728]
refs: ["planet/lineages/brief.py::_people_contacts (SP.parse of meta.tree)", "planet/lineages/spec.py::build (ValueError: density and band_km2 are no longer given)", "runs b4d502 3c1caf a24559 (the v0.1.0 showcases)", "run a2b637 (the one D&D run on current code)", docs/wiki/state.md]
---

## Description
In plain words: the v0.1.0 showcase peoples runs (b4d502 and a24559 D&D, 3c1caf Seven Meals) were made before the density ladder
(PW-1275). Their stored tree still gives `density`/`band_km2`, which today's spec parser refuses, so the brief's per-people block
(`_people_contacts` parses the tree) raises and the viewer's Culinary brief for a whole people shows "Could not build the brief" on
those runs. The new per-culture sheet (PW-1391) does not parse the tree and works on them. Every Seven Meals peoples run in runs/ has
the same problem; only a2b637 (D&D) parses. What breaks if never done: Daniel opens the showcase in the viewer, picks a people, and the
brief fails.

Fix (no code): re-run the showcase peoples on current code (minutes each) and point state.md at the new ids; delete the old ones
(no backward compatibility).
- [ ] a Seven Meals and a D&D showcase peoples run on current code; the whole-people brief builds on both
