---
id: PW-1076
title: "No river or lake place tag: bronze dragons' big rivers and steppe lakes stand in as 'wetland'"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: fun-lane-50
blocked_by: []
relates: [PW-1024]
refs: [planet/lineages/history/tags.py, planet/lineages/crossing.py, planet/lineages/samples/dnd.toml]
created: 2026-10-30
updated: 2026-11-03
---

## Description
**In plain words.** The owner wants bronze dragons on big rivers and steppe lakes, as well as on sea coasts (PW-1024 ruling). The habitat code has no place tag for "on a big river" or "by a lake", so for now bronze dragons tolerate `wetland` (low, very wet ground) instead. That is a poor stand-in for a river through dry steppe.

The river mask already exists inside `crossing.corridor`: the land cells whose world flow is in the top 8%. It is not a place tag, because `_tags` runs without the flow (several callers: the summary, demes, the presence cache).

What to try:
- Add `river` (and `lake`, if the world has lakes as a layer) to `spec.PLACES`, computed in `_tags` from a flow passed in, empty in the deep epoch.
- Then give bronze dragons `tolerates = ["wetland", "river", "lake"]`.
- The copper dragons' `breaks` could then include river breaks: open dry country next to a big river.

- [ ] bronze dragons present along big steppe rivers on at least one sweep world

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-10-30: Created from inbox draft draft-river-and-lake-place-tags.md (found by fun-lane-50).
