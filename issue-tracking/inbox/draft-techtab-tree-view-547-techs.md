---
title: "Technology tab: the tree view of 547 techs is a 4,300 x 4,700 px pan; add a track filter or fold the eras"
type: task
status: todo
parent: PW-913
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-69
blocked_by: []
relates: [PW-1122]
refs: [viewer/techtab.js, "run 488d7e"]
---

## Description
In plain words: with the tech catalogue in (547 techs), the Technology tab still works: every view draws in under 2 s on run
488d7e (tree 547 nodes, inventory 547 chips, table, timeline, cascade, map; no page errors). But the Tree view is now a
4,320 x 4,744 px picture with a thousand prerequisite curves crossing it, so finding one tech means panning a long way.

Ideas: a track picker on the Tree view (the Timeline view has one), folding each era to a summary column until clicked, or a
search box that pans to a tech. Only the tree view needs it; the others filter already.
