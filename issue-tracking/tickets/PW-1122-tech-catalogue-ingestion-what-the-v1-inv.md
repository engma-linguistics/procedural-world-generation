---
id: PW-1122
title: "Tech catalogue ingestion: what the v1 invention model needs from each row"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-64
blocked_by: []
relates: []
refs: [docs/references/tech-catalogue/, planet/lineages/samples/techtree.toml, planet/lineages/techtree.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
Notes for merging the 594-row catalogue (docs/references/tech-catalogue/) into techtree.toml under the v1 model (lane 64):
- `domains` is required on every tech (the load checks it), from the same eight tags. The catalogue already carries it.
- Give no `rate`, except as an override. A tech dated under gate_kyr (11.6) gets its rate from the anchor (its Earth lag after its
  prerequisites). Older techs use their track's rate.
- A row whose Earth date comes more than lag_max_kyr (10) after its prerequisites is floored at its date. That flags a missing real
  precondition; prefer adding the need.
- `pool`: the default is "all" for the stone age and "specialists" after. Set it by hand for anything a band could invent late, or a
  specialist could invent early.
- Bring the ids the lane already used: war_chariot and siege_mining are in the tree already, with the catalogue's ids.
- After ingesting, re-run the anchor check (techtree.anchor_check) and a firsts table on two runs. Report the world firsts and the
  finds per world, against Earth's independent origins (the catalogue's `origins`).

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-catalogue-ingest-v1.md (found by fun-lane-64).
