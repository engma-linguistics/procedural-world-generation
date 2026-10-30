---
id: PW-1116
title: "Settlements: mines v0 makes ~2,200 mines a run, 95% of them human; check the count and the gate"
type: task
status: needs-decision
parent: PW-856
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-61
blocked_by: []
relates: [PW-1011, PW-1105]
refs: [planet/lineages/settlements.py, viewer/globe/settlements.js, "run 488d7e", "world 4360a3"]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Fun lane 61 added mines as their own kind of place (owner 10-30: mines from the first metalworking on, as in the Yamnaya era). How a mine works:
- It stands on an ore district or a rock-salt bed (mining.ORE_MIN, SALT_MIN).
- It is worked by the cell's lead people, else its second, once that people knows 'mines'. For ore it must also know 'copper'.
- It holds MINE_SHARE (0.4%) of the cell's people, and is founded at 300 people or more.
- The globe draws it as a small diamond in its holder's colour. It shows with the villages, only when zoomed in.

On world 4360a3 the four runs have 2,193 to 2,277 mines living now (villages 11,300 to 12,200). Humans work 1,997 to 2,196 of them: they hold the dense cells, and ore districts are common. Dwarves work 1 to 10, kobolds 10 to 46, gnomes 0 to 119.

Options:
- A: keep as is (a mining district per ore cell of the dense peoples);
- B: fewer, richer mines: only the stronger deposits (ore >= 0.75), or one per ring of cells;
- C: favour the mining peoples: a miner people works a deposit in its cells even as the second people, at its halls' size.

Lean: B + C, so mines read as a dwarf and kobold thing as well as a human industry.

## Updates
- 2026-10-30: Owner 10-30: humans as nearly the only miners feels weird; dwarves, kobolds, orcs and similar should do their share (aarakocra less so). Literature search or think it through.
- 2026-10-30: Created from inbox draft draft-settlements-mines-count.md (found by fun-lane-61).
