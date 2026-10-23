---
id: PW-677
title: Peoples leave much habitable land empty at the present (e.g. 1df1c3 at 42.5 N, -113.3 on run d489d0); after tens of kyr they should settle nearly everything
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24) on run d489d0: the cell at 42.5, -113.3 (437 m) is unpeopled at the present. With several species arising apart over tens of kyr of being 'genetically modern', peoples should settle nearly all habitable land; initial peopling should try to reach most reasonable major landmasses (not force all of them). Find why spread stalls (rates, crossings, viable population, competition, habitat floors) and fix the cause, not a fill-in.

## Updates
- 2026-10-23: Created.
- 2026-10-24: Fixed on branch worktree-agent-ab254628c4ccfa51b. Causes: (1) a stem's range on landmasses not joined to a child vanished when the stem ended (`History._end_parent`); (2) no sea crossing for ordinary peoples between the raft and the boats at 6 kyr (`spec.CANOES_KYR`). Habitable land empty at the present: 1df1c3 35.7% -> 19.9% (31.9% -> 11.8% of the land warmer than 0 C), 3e9e7d 30.4% -> 19.7% (21.0% -> 4.7%); the rest is mostly cold country. 42.5 N -113.3 is peopled. See docs/proposals/lineages.md. Status left for the coordinator.
