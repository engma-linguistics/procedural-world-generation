---
id: PW-601
title: "Lineages: how strongly the adjacency/place wishes act; competition and mixing strength"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lineages-lane
blocked_by: []
relates: [PW-103]
refs: [planet/lineages/history.py, "peoples run 992230 (world 119973, preset dnd)"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Built: wishes act as (1) best of N seeds by the wishes' score, (2) mild nudges on origins (place wishes x1.5 on matching cells, near/apart by the other's smoothed range) and on habitat (near x(1 + w p_b), apart x(1 - 0.6 w p_b)). On world 119973 with the preset (tries 2): score 0.68; goblin near orc, hobgoblin near goblin, halfling near human all 1.0; lizardfolk apart from tortles 0.94 and from aarakocra 1.0; "aarakocra on islands" and "tortles on islands" 0.0 (that planet's small islands are far from where the lines arise).

Options: A (built, lean) nudges + best of N, a wish can fail and says so; B stronger: place the wished lines' origins to satisfy the wish first (e.g. arrival-like seeding on islands), then simulate; C post-hoc range editing (rejected: forcing).

Related tuning (no decision needed unless the owner disagrees): competition alpha = 1.15 x niche overlap x kinship (cap 0.97); late mixing drops it 60% from `mixing_start` (3 kyr ago) to the present; at p >= 0.25 mixing zones still come out large (45 Mkm2 on one tropical continent before the alpha raise). Review the mixing zone sizes on a showcase world.

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-wish-strength.md (found by lineages-lane).
