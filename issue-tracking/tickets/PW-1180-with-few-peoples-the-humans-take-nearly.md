---
id: PW-1180
title: With few peoples the humans take nearly everything; contests go to the denser people wherever niches overlap
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: lane77
blocked_by: []
relates: [PW-887, PW-1147, PW-1152]
refs: [planet/lineages/history/competition.py, planet/lineages/history/pressure.py, planet/lineages/history/model.py, planet/lineages/history/habitat.py, tools/peoples_robust.py, tools/peoples_robust/trees/five_peoples.toml, tools/peoples_robust/trees/even_six.toml]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
When a tree has only a few peoples, the humans end up holding almost all the land and almost all the people. With five peoples
(humans, lizardfolk, goblins, aarakocra, gnomes) humans are 94% of all people at the median and lead 80-99% of the peopled cells. The
goblins never grow past the patch they started in. With the dnd tree, the other peoples' head start is what holds the humans back,
so their share depends on who got where first. The six-people tree the owner wants near-even lands at humans ~72%. The causes are
the general contest rules, not the humans' data alone. Where two peoples overlap, the denser one wins at the frontier. The niche
overlap is symmetric: a broad people presses on a specialist as hard as the specialist presses on it, even in the specialist's own
best country. In closed country any overlap above ~0.7 becomes exclusion.

## Description
Stress suite (lane 77, tools/peoples_robust.py, L6 worlds 4360a3 and af2677, one try per variant). Small trees fail the 85% invariant in
every run: dnd3 (humans, goblins, kobolds) 89%, dnd5 88-90%, five_peoples 94-100% (cells led 79-99%). The rules that combine, all
general:
1. Frontier invasion (pressure.invasion_weights, INVADE 0.5): on the cells next to its range a people weighs a thinner rival at
   (dens_own / dens_rival)^-0.5, floor 0.3. Humans (10, farmers 12) weigh goblins (5) at 0.71, bugbears (0.8) and goliaths at 0.3.
2. Numbers in the competition (model, DENSITY_PUSH 0.1, clip 0.7-1.4): a 10 /km² rival weighs x1.29 on a 0.8 /km² people.
3. Symmetric niche overlap (habitat.niche_overlap divides the shared comfort range by the narrower range). A specialist inside a
   generalist's range has overlap ~0.7-0.9 both ways, and per cell the specialist's better fit (K) is not what decides it.
4. ALPHA_CLOSED 1.4 in closed country (contact 0, same way of life): any pair above alpha_eff 1 excludes, so the winner of 1-2
   takes the cell outright (HOLD_MIN then clears the loser's thin remnant).
5. Density also sets the reported share (population = presence x density x area), so a sparse people is small twice over.
Diagnostic screens (4360a3, seed 7; `run --family screen` and `--params`) show that none of 1-5 carries the monopoly alone. Switch
off one rule and the humans stay at 86-100%: INVADE 0, DENSITY_PUSH 0, both, ALPHA_CLOSED 1.0, HOLD_MIN 0, SURGE_Q 0, EXPANSE_PRESS 0,
COEXIST off. On five_peoples, edits to the humans' own data:
| human edit | share | area Mkm² | cells led |
|---|---|---|---|
| none | 94-100% | 139 | 99% |
| narrow niche | 94% | 88 | 71% |
| density 2 (from 10) | 98% | 138 | - |
| every people at density 5 | 95% | 131 | - |
| no groups | 99% | - | - |
| no agricultural trait | 99% | - | - |
| no sea (sea_share 0.05, no seafaring) | 86% | 58 | 53% |
| no groups and no sea | 70.5% | 28 | 33% |
So density is not the lever. Two things carry it. The humans reach every landmass (seafaring groups and sea share), and wherever
they land they hold it, because nothing in the contest favours the people already better suited there. That points at A
(per-cell fit decides the contest) more than at B.

Options (general, least forced first):
- A. Asymmetric overlap: compute the competition i feels from j as the share of i's niche that j's covers (MacArthur's alpha_ij =
  integral of u_i u_j / integral of u_i^2 over the climate axes). Then a generalist feels a specialist less than the specialist
  feels it. Per cell, weight the load by the rivals' fit there (K_j / K_i), so a specialist at its optimum holds against a
  generalist at its margin.
- B. Frontier invasion by the habitat edge (K_own / K_rival at the cell), not by the density ratio. Keep density for the share and
  for DENSITY_PUSH only.
- C. Leave the rules and give each people a share band (lane 78's soft targets). That is a target, not a mechanism. Better as a
  guard rail over A/B.
- Lean: A (the screens rule out density as the lever), then B, judged on the suite (even_six, five_peoples, dnd3, dnd5 against today), with C as the guard rail.

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03: option A built. competition._fit_w weights the contest by fit and breadth (FIT_Q, owner D20 lever 1); overview 2.26 'Fit decides the contest'. Few-people trees are handled by D31 (commonest share target) and PW-1241.
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-dense-broad-people-takes-small-trees.md (found by lane77).
