---
id: PW-759
title: A template whose share grows where its bearers and hosts live together (kenku - the curse always takes)
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun13
blocked_by: []
relates: [PW-730]
refs: [planet/lineages/samples/seven_meals.toml, planet/lineages/history.py, planet/lineages/spec.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
`seven_meals.toml` (PW-730) makes the kenku a template on the aarakocra with a fixed `share = 0.08` at 3 kyr, like the dnd tieflings.
The canon (culinary-dnd G-06) says a child with a kenku parent is always kenku, so the share should only grow, slowly, wherever kenku
and aarakocra live together (the docksides), and not spread over the aarakocra's whole range. A template's share is a constant today.
Smallest change: a spec key `grows = <per kyr rate>` on a template that raises the share in a cell by the rate x (the kenku share x the
non-kenku share) per step, bounded by the hosts' presence there.
- [ ] a template with `grows` raises its share only where it already is
- [ ] `dnd.toml` runs byte-identical (no `grows`)

## Updates
- 2026-10-24: Created from inbox draft draft-kenku-share-grows.md (found by fun13).
