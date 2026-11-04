---
id: PW-715
title: Fine zooms keep their parent's deposits but do not re-site them at the fine scale
type: task
status: todo
parent: PW-155
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: fun5
blocked_by: []
relates: [PW-618, PW-610]
refs: [planet/zoom/resources.py, planet/zoom/fine.py, "zoom c7eff5 (fun5 test, fine zoom of 875af2)"]
created: 2026-10-23
updated: 2026-11-03
---

## Description
PW-618 B is built: every `planet zoom` sites deposits (from the history kept beside the world), and a fine zoom
inherits the parent's deposits that lie inside it (`zoom_resources._inherit`: same name, size and grade; a placer moves
to the nearest river pixel within 4 parent pixels; kimberlite pipes follow), and re-sites only the coal outcrop belts
on its own ground. What is not done, from the PW-618 description (gap 3):
- veins and seams as lines at the fine resolution (a hard-rock deposit is still a point);
- placers on the fine zoom's meander belt via `valley_floor` (they only snap to the nearest river pixel);
- a deposit near the fine zoom's edge whose parent point lies just outside is missed (no halo).
Options: A leave it (points are fine for the game use); B re-site with the same seeds at the fine resolution and match
to the parent's deposits by key and nearest position. Lean A until the lines are wanted.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: fine-zoom or coast-form polish; zooms read well enough
- 2026-10-23: Created from inbox draft draft-fine-zoom-deposits-resite.md (found by fun5).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
