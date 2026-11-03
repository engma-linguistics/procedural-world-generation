---
id: PW-1205
title: "Proposal: a people's ways of life share one carrying capacity per cell (groups stack today, ~1.3x a single people's fill)"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: lane84
blocked_by: []
relates: [PW-1180, PW-1149, PW-665, PW-684]
refs: [planet/lineages/history/model.py, planet/lineages/history/groups.py, planet/lineages/history/peoples.py, planet/lineages/samples/dnd.toml, docs/review/peoples-why/report.md]
created: 2026-10-31
updated: 2026-11-03
---

## In plain words
Human farmers, herders, nomads, seafarers and arctic hunters are counted as humans, which is right. But in the model each of them is
its own line with its own full claim on the land, and they hardly compete with the core humans. So a human cell can hold the core
humans and the farmers side by side, each near full. A single-line people (elves, dwarves) can fill a cell once; humans fill it about
1.3 times. That is most of the jump in human numbers when farming starts (212 M to 417 M humans between 9.5 and 7 kyr ago, world
4360a3, seed 7). Your hypothesis was right in spirit: the ways of life should be one species that splits its land and people between
ways of life, not extra peoples.

## Description
Measured by lane 84 (docs/review/peoples-why/report.md, world 4360a3, one try per seed):
- Over the cells humans hold, the human lines' presences sum to 1.01 on average against a capped "whole" of 0.78 (dnd, seed 7),
  1.26 against 0.90 in a five-people cut; 89-90% of human cells hold two or more human lines.
- Turning the five human groups off (`enabled = false`): dnd humans 66.9% to 50.9% of people (seeds 7, 10, 13: -14, -12, -22 points),
  five-people cut 83.2% to 73.9% (5 seeds). Human range moves less (73 to 68 Mkm²). The loss is mostly people per km², not land.
- Without groups the farming-era jump goes: human share 37% at 9.5 kyr, 35% at 7 kyr (with groups 37% to 56%).

Why: groups compete with their own people at GROUP_KIN x niche overlap with no closed-country term (model.py:91-97), so alpha is
~0.5 and Lotka-Volterra coexistence gives each line ~K/(1+a) of the cell, ~1.35 K together. Population counts each line at its own
density (peoples.py:88-95: presence x density x area, summed per line), while `whole` caps the presence at 1 (peoples.py:46-53).

Options:
- A. One capacity: per cell, a people's lines together hold at most its K (the whole presence); a group takes a share of it,
  and its density applies to that share. The groups still decide where farmers, herders and seafarers live.
- B. Keep separate lines but count population on the capped whole, split by the lines' shares.
- C. Leave as is (humans get a ~1.3x density bonus wherever they have groups; orcs and dwarves get it too, smaller).

Lean: A. B fixes the count but not the extra pressure the stacked lines put on neighbours.
Lane 83 is reworking the contest in a worktree; this touches groups.py and the population count, so it can go after.
- [ ] Sum of a people's lines' presence <= 1 x its whole habitat per cell
- [ ] dnd and the lane 77 suite rerun; report the human share against today's

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03: option A built. competition._compete and model._kin give a people and its groups one capacity per cell (alpha 1 between kin); overview 2.26 'One capacity per people' (lane 83).
- 2026-10-31: Created from inbox draft draft-groups-share-their-peoples-capacity.md (found by lane84).
