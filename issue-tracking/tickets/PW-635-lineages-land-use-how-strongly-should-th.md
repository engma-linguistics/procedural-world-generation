---
id: PW-635
title: "Lineages land use: how strongly should the world's goods shape the peoples' ranges (land_pull)?"
type: task
status: done
parent: PW-103
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: lineages-lane-4
blocked_by: []
relates: [PW-601]
refs: [planet/lineages/land.py, planet/lineages/history.py, planet/lineages/samples/dnd.toml, docs/review/lineages/showcase-4.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane 4 added `[[use]]` (trait or place → good, weight) and `meta.land_pull`. A line's habitat is multiplied by (1 − pull + pull G), normalised to a mean of 1 over its own country. This is a nudge: K is capped at 1, so most of the effect is the cut where the goods are absent.

On 119973 (L6, best of 2, the same seeds), the range's mean good against the world's land mean ("enrichment") moved as follows:

| people: good | pull 0 | pull 0.35 | pull 0.5 |
|---|---|---|---|
| humans: harbour | 0.75 | 0.79 | 1.84 |
| dwarves: gold | 1.49 | 1.58 | 1.69 |
| gnomes: gold | 0.75 | 1.04 | 1.59 |
| elves: timber | 3.0 | 1.5 | 4.7 |
| tortles: lagoon | 19 | 24 | 33 |
| wish score | 0.66 | 0.70 | 0.63 |

The wish scores move within seed noise. Mountain peoples already sit near ores (mountains and ores go together), so the dwarves move only a little.

Options:
- A: keep 0.5 (built). Visible but not forced.
- B: stronger (0.7–0.8), so that "dwarves next to their mines" is unmistakable. The risk is that small peoples get pinned to point goods and lose ground elsewhere.
- C: per-use strength: let the weight scale the pull, instead of being only relative within a line.

Lean: A for now. Revisit with C if the owner wants some goods (mines) to bite harder than others (forests).

## Updates
- 2026-10-23: Status todo -> done. Merged (fun lane 3, runs fa7183/18cf62).
- 2026-10-23: Built (fun lane 3), option C: each use's own pull = (its pull or meta.land_pull) x min(weight, 1); `Tree.pulls_of`; the multiplier is (1 - Pmax) + max_g(pull_g x G_g). dnd.toml weights rescaled so miners, subterranean, flyers and coastal peoples keep their old full strength (top weight 1) while forests and wetland stay at 0.5. Measured on 1df1c3 / 3e9e7d, 4 tries each, same seeds: mean wish score 0.723 -> 0.706 and 0.761 -> 0.780, best 0.802 -> 0.751 and 0.811 -> 0.793; empty land of the kept try 18.9 -> 12.6% and 9.1 -> 9.8%. Per-try differences go both ways: no signal beyond the best-of-N pick (draft draft-wish-score-needs-mean-of-tries).
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): C, per-use strength: each [[use]] row's weight sets its own pull, so mines or volcanoes can bite harder than forests.
- 2026-10-23: Created from inbox draft draft-lineages-land-pull-strength.md (found by lineages-lane-4).
