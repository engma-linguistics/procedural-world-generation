---
id: PW-1301
title: "Land zoom seams: neighbouring sections agree at their edges (heights, coasts, landforms, biomes)"
type: task
status: done
parent: PW-1299
milestone: v2
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: [PW-1319]
relates: []
refs: [planet/zoom/stage_finish.py, planet/zoom/coastal.py, planet/zoom/fine_forms.py, planet/zoom/match.py, "planet/zoom/match.py::prepare", "planet/zoom/stage_landscape.py::landscape_loop", "planet/zoom/stage_terrain.py::mean_correction", "planet/zoom/stage_terrain.py::coastline", "planet/zoom/regional.py::zoom", planet/zoom/tiling.py, tests/test_zoom_match.py, docs/review/land-zoom/seams-round1.md, docs/review/land-zoom/practice.md, docs/review/land-zoom/seams.py, docs/review/land-zoom/table.py, "world dba204", docs/review/land-zoom/seams-round2.md, docs/review/land-zoom/round2/, "planet/zoom/match.py::lakes", "planet/zoom/match.py::hold", "planet/zoom/match.py::final", "planet/zoom/match.py::sources", "planet/zoom/match.py::_owner", "planet/zoom/stage_landscape.py::lakes", "planet/zoom/stage_landscape.py::fit_setup", docs/review/land-zoom/stage_diag.py, docs/review/land-zoom/match_diag.py, "zoom d904d6", "zoom a13667", "zoom fe600a", "zoom 59336f", "zoom b710fd", "zoom 0852e2", "zoom a3a793", "zoom d7b43d", "zoom 683193", "zoom 3b412b"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Make adjacent sections agree where they meet: shared overlap bands with blending, noise and landform seeds keyed by place rather than by section, and coastlines from one source. Judged on the practice sections.

## Updates
- 2026-11-02: Status todo -> done. Lanes 127/128 (merged 13c281dc): planet zoom --match IDS. Neighbour owns its tiling cell's ground (coast, finished heights, lakes at surface), 80 km blend ramp. 4 practice seams + turned tile pair py.1.1/py.0.1 at 4 km: median dh at the line 10-410 m -> 0.0 m (p95 <= 0.3), coast/biome <= 0.1%, no ramp steps; 1 km tile pair same. Matched 1 km section ~110 GB. Notes docs/review/land-zoom/seams-round2.md.
- 2026-11-02: Created.
- 2026-11-02: Lane 128 (in branch, not merged): judged lane 127's matching (`planet zoom --match`) on lane 116's four practice seams and one tiling pair (py.1.1 / py.0.1) at 4 km/px: height difference at the owner line 10-410 m alone -> 0.0 m matched (p95 <= 0.3 m), coast and biome at the line 0-0.1%, ramp slopes no steeper than built alone. Fixed: neighbour's lakes (held at their surface, outlines taken where it weighs over a half; the only coast mismatch left at the line), a crash on held lake beds, the tiling owner rule's crash. Far-inside test bound back to 1 m (measured 480 km in; the reach is by design and scales with the coarse cell). Notes: docs/review/land-zoom/seams-round2.md.
