---
title: "Peoples history: miner kinds lean harder toward rich ore (and copper, tin, rock salt) at the next history re-run"
type: task
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-72
blocked_by: []
relates: [PW-1116, PW-1131]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/history/habitat.py, planet/lineages/settlements.py]
---

## Description
In plain words. Dwarves should live where the ore is. Fun lane 72 got there without touching the history: dwarves,
kobolds and gnomes now send mining colonies to ore districts near their own country (settlements, D12). Where the
dwarves themselves live is still set by the history. The history already gives them a mild pull toward gold, iron, gems and
mithril, but it does almost nothing, for two reasons:
- "Ore" covers about half of all land (see the companion draft on the ore threshold).
- The pull is rescaled over the dwarves' own country, so it moves them a little within their mountains and no further.

On world 4360a3 the dwarves' cells are 54% ore against 47% for land overall, but only 3.8% rich ore (best ore good
>= 0.75) against 7.7% for land overall. They live on poorer ground than the average people.

What to change at the next planned history re-run (not on its own: it means re-running all seven peoples histories):
- Add the missing miner rows in dnd.toml [[use]]: copper and tin (miners have gold, iron, gems and mithril only), and
  rock salt (salt_rock).
- Let the miner rows read rich ore rather than any ore: a good of `ore_rich` (the best ore good above 0.75, scaled), or a
  strength above 1 on the existing rows.
- Then measure the dwarves' share of rich-ore cells (now 3.8%, target well above the land's 7.7%) and their mines and
  colonies in settlements (now 4-18 a run).

Expected effect: small, because the dwarves are few (present on 69-184 cells of ~14,100 land cells). Most of their
mines will still be colonies. If the owner wants dwarves to be many, that is a range and density question for the
history, not a mining one.
