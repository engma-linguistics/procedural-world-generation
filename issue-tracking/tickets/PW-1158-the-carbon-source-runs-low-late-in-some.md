---
id: PW-1158
title: "The carbon source runs low late in some runs (819014 l6c_p: 0.57 of its reference over 850-1000 Myr), giving a long cold finish"
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: med
found_by: lane75
blocked_by: []
relates: [PW-969, PW-980, PW-1142]
refs: [planet/tectonics/earth.py, docs/overview.md]
created: 2026-10-30
updated: 2026-11-01
---

## Description
In plain words. Volcanoes, mid-ocean ridges and arcs add CO2, and weathering takes it out. On some worlds the
volcanic supply drops well below its usual level for the last couple of hundred million years. The thermostat
can't fully make up for that, so those worlds stay deeply cold to the end. Is the drop real plate behaviour
(fewer, slower ridges when plates weld into giants), or a quirk of the model?

Lane 75 (PW-1142 gate). In lane 67's 18-draw X arm (main physics), the closed-loop gain is ~11 C of dT per e-fold
of source, so a source at 0.57 means ~-6 C. In 819014 l6c_p the source (`src`, against the reference learnt by 300
Myr) median is 1.03 / 0.91 / 0.74 / 0.57 over 300-500 / 500-700 / 700-850 / 850-1000 Myr. The drift explains only
~0.89x of the last value (drift -1.0); the rest is tectonic (ridges + arcs; plumes are ~1-2% of the source). The
predicted dT is -6.2 and the run's is -6.9; it's one of the four frozen-over worlds. Across the 18 draws, ln src
has sd 0.17 over 520-1000 Myr, which is Earth-like. But this draw's p5 is -0.78.

docs/overview.md already notes that stress rifts die out after ~600 Myr (10-16 to 1-5 per 200 Myr) and the late
floor ages. If the ridges die off, the source falls. PW-969's giant welded plates may be the same cause.
- [ ] The source split into ridge / arc / plume over 600-1000 Myr for 819014 l6c_p and two controls
      (a diag field per part), and whether the decline tracks the rift count or the largest plate

## Updates
- 2026-11-01: Lane 100e (11-01): arc CO2 already uses nominal slab melt (convergence x trench length), not the volume thermostat; the late fall is real slab flux against the 0-300 Myr reference. See docs/review/tectonics/margin/note-arc-co2.md.
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-late-run-outgassing-decline.md (found by lane75).
