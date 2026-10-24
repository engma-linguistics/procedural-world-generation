---
id: PW-618
title: "Resources: zoom deposits only by command; not in the 3D view; fine zooms don't inherit them"
type: task
status: done
parent: PW-155
milestone: v2
subsystem: zoom
effort: m
impact: med
found_by: resources2
blocked_by: []
relates: [PW-609, PW-610]
refs: [planet/zoom_resources.py, viewer/zoom.html, viewer/zoom3d.js, planet/zoom_fine.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Stage 2 sites deposits in a saved regional zoom with `planet resources zoom:<id>`, which writes them to
zoom.json under `resources`. The siting takes 0.2-1.5 s. On top of that comes the world's history pass, 6-9 s
at L7, which could be cached per world. There are three gaps:
1. When deposits are made. A: by command only (now). B: at every zoom build, which adds ~10 s at L7 unless
   the history is cached on the world (PW-609's option B would do that). C: lazily, by the viewer or server
   the first time the zoom is opened. Lean B, after PW-609 is decided: both depend on storing the history's
   per-cell outputs with the world.
2. The 3D view (zoom3d.js) draws no deposits. Markers like the volcano and waterfall ones would do.
3. Fine zooms (zoom_fine.py) neither inherit their parent's deposits nor refine them: veins and seams as
   lines, placers on the meander belt via valley_floor. zoom_resources already uses valley_floor when a
   zoom has it.
Lean: B for gap 1. Then gap 3: inherit the points that fall inside, and re-site at the fine resolution with
the same seeds.

## Updates
- 2026-10-23: Status todo -> done. fun5: B built. Every planet zoom sites deposits (0.3-1 s from the stored history); the 3D view marks them (pins, biggest 250, filtered by the Deposits menu); a fine zoom keeps its parent's deposits that lie inside it and re-sites the coal belts. Not done: veins/seams as lines and placers on the meander belt (draft-fine-zoom-deposits-resite).
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): B: deposits at every zoom build (history cached on the world, as PW-609 B makes it), shown in the 3D view, inherited by fine zooms.
- 2026-10-23: Created from inbox draft draft-resources-zoom-deposits-auto-and-3d.md (found by resources2).
