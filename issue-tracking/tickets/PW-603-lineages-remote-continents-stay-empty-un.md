---
id: PW-603
title: "Lineages: remote continents stay empty unless seafarers or fliers get lucky; owner call on whether that is wanted"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lineages-lane-2
blocked_by: []
relates: [PW-601]
refs: [planet/lineages/crossing.py, planet/lineages/spec.py, "world 119973 (18 Mkm2 continent 4300 km out)", "world c00ebf (16 Mkm2 at 52N)"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane 2 added three ways across the sea:
- land bridges: implicit in each epoch's land, and named in the events
- short hops: the spread's per-trait sea factor
- long crossings (spec.HOPS): length scales of 150 km for rafting, 250 for coastal canoes, 400 for swimmers, 700 for fliers and 1500 for seafarers (seafarers only in the last 6 kyr)

On 119973 the 18 Mkm2 continent lies ~4300 km (36 cells) of open ocean from all other land. One try left it 0.79 held and others left it empty: the seafarers' chance of reaching it is ~15-30% per try. c00ebf's 16 Mkm2 continent at 52N is reached in some tries only. The summary now lists `empty_continents`.

Options:
- A (current): leave it to the crossings. An empty continent far across an ocean is plausible (the Americas before people) and is that world's own story.
- B: count empty continents in the best-of-N score, so a try that peoples every continent wins ties.
- C: the owner places an arrival or seafaring people there in the editor. This already works: give an arrival a `place`.

Lean: A + C, with C documented in the editor. B only if the owner wants every continent peopled by default.

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-empty-remote-continents.md (found by lineages-lane-2).
