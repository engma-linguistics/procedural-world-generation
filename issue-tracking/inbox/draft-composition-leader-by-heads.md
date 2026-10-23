---
title: The cell's leader is the people holding most ground, so by head count the "lead" share can fall below the second's
type: task
status: needs-decision
parent: PW-689
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-3
blocked_by: []
relates: [PW-703, PW-689]
refs: [planet/lineages/compose.py]
---

## Description
PW-703 weights the composition shares by head count (presence x density). The leader is still the people with most presence (`peoples_whole`, the layer the rest of the viewer and the stories use). Where a dense people shares a cell with a sparse leader the leader's share can be below the second's (`mix_lead_share` 20%, `mix_second_share` 70%), which reads oddly ("lead" is not the largest).

Options:
- A (built): leader = most ground held; shares = heads. The blend colour layer still starts from the ground holder. Documented in `compose.py`.
- B: choose the leader for the composition layers by heads (the largest share), while `peoples_whole` stays the ground holder; the hover card lists the head-count leader first.
- C: sort by heads and drop "lead"/"second" naming from the layers (store the top two by heads).

Lean: B.

## Updates
