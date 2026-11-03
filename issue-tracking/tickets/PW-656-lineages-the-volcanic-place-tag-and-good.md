---
id: PW-656
title: "Lineages: the volcanic place tag and good have no volcanoes in the deep (Myr) epochs"
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: lineages-preset-lane
blocked_by: []
relates: []
refs: [planet/lineages/land.py, planet/lineages/history.py, planet/tectonics/volcanism.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The `volcanic` good and place tag (land.goods, history._tags) come from the finished world's volcano table, so
they exist only in the glacial and recent epochs (the plates have moved since the deep ones). A line that
prefers `volcanic` and splits in the deep epochs (none in the dnd preset: fire giants split at 250 kyr, inside
the time zoom on tonight's worlds; their stem at 700 kyr is not volcanic) finds no volcanoes there.

The source run's keyframes carry their own volcano tables (tectonics output `volcanoes`): the deep steps could
build the tag from the nearest keyframe's table, the same rule as land._volcanic. Cheap; worth doing only if
a preset or user line needs volcanoes in Myr time.

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-volcanic-tag-deep-epochs.md (found by lineages-preset-lane).
