---
id: PW-119
title: "Highlights: find island chains and atolls from the volcano table"
type: task
status: todo
parent: PW-001
subsystem: highlights
effort: s
impact: low
found_by: volcanoes
blocked_by: []
relates: [PW-004]
refs: [planet/highlights.py, planet/zoom_volcanoes.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
`highlights.hotspot_islands` finds hotspot islands from land cells of hotspot rock near a plume. Worlds
now carry every volcano (`meta.volcanoes`, columns `meta.volcano_columns`) with its age, summit height
and reef state, and `zoom_volcanoes.form()` names what each looks like. A detector could rank chains by
how many separate islands, atolls and guyots they have in a row (Hawaii -> Midway -> Emperor), and
coral atoll groups, and pick a zoom that fits the chain. At level 6 this matters more: the cells there
rarely show the islands (see the coarse-grid draft).

## Updates
- 2026-10-14: Created from inbox draft draft-hotspot-chain-highlight.md (found by volcanoes).
