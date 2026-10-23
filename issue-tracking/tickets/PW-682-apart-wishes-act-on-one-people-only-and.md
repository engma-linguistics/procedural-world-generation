---
id: PW-682
title: "'apart' wishes act on one people only, and most pairs score 1 by default"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: pw677
blocked_by: []
relates: [PW-678]
refs: [planet/lineages/history.py, planet/lineages/samples/dnd.toml]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`_wish_near` cuts only a's habitat where b lives (x(1 - 0.6 w p_b)); b is not moved, and the score is the share of a's range beyond ~330 km of b's. With 20 'apart' pairs in the D&D preset most score 0.9-1.0 on niches alone (elf apart goblin, gnome apart goblin...), which lifts the average wish score without the wish doing anything. Options: make apart symmetric (both peoples cut), score only wishes whose niches overlap, or weight the average by how contested each pair would be without the wish. Also the fire-giant 'near' wishes are met in 1-2 of 3: the near pull (x1.5 at the border) is weak against a narrow volcanic habitat.

## Updates
- 2026-10-23: Created from inbox draft draft-apart-wish-is-one-directional.md (found by pw677).
- 2026-10-24: fill2: 'apart' now cuts both peoples and is scored against the niche baseline (share of a's habitat within 330 km of b's habitat); uncontested pairs are left out of the average. 36 of 37 D&D pairs are contested; scores within 0.03 of the old ones. 'near' unchanged (draft: near-wish-weak-against-narrow-habitat). See docs/proposals/lineages.md, 'Filling the land'.
