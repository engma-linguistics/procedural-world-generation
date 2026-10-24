---
title: Spits and other shore forms are still raised after the fact (planet coast zoom --terrain)
type: task
status: todo
parent: PW-097
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: fun5
blocked_by: []
relates: [PW-622, PW-621]
refs: [planet/zoom_coast.py, planet/zoom_shoreforms.py, planet/zoom.py]
---

## Description
PW-622 B moved the barrier islands into `zoom.build` (`zoom_coast.islands`, before the land/sea split, so the rivers,
vegetation, coastal life, harbours and satellite view see them). The shore forms of PW-621 (spits, beach-ridge plains,
tidal flats and channels, drowned reefs) are still drawn by `zoom_coast.add_to_zoom` after the zoom is saved, and only
raised out of the sea with `planet coast zoom:<id> --terrain`; so a raised spit has the same staleness the islands had
(rivers end at the old shore, the satellite view shows sea). Every `planet zoom` runs `add_to_zoom` without `--terrain`.
Options: A leave them as layers (no terrain change); B build them in `zoom.build` like the islands (zoom goldens move).
Lean B if the owner wants spits as terrain.
