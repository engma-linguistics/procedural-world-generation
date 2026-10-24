---
title: World mode as a world-creation option and a viewer toggle for the fantasy resources
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: fun4
blocked_by: []
relates: [PW-695, PW-607]
refs: [planet/resources.py, planet/zoom_resources.py, viewer/index.html, viewer/zoom.html, planet/__main__.py]
---

## Description
PW-607's ruling asked for the fantasy resources behind "a world option and a viewer toggle". Built: the world's mode is set
by `planet resources WORLD --mode real|fantasy` (stored as `meta.mode`; real drops the `res_x_*` layers, and the world's
zooms site no fantasy deposits); the peoples runs take `--mode` / the workbench's "world mode". Not built:

1. `planet world` / the server's world creation does not take a mode yet; a world is made in fantasy mode and switched
   afterwards. Is a separate flag at creation worth it (it only saves the `planet resources` call), or should one
   switch (on the run? the world?) cascade to world, zooms and peoples runs?
2. The viewer shows what the world has (no `res_x_*` layer: no fantasy rows), so there is no live toggle. A viewer toggle that hides the
   fantasy rows in a fantasy world would need a client-side filter in `index.html` (hover, resource layer list) and `zoom.html`.
   Lean: no toggle, the mode switch per world is enough; revisit when magic (PW-696) adds more fantasy layers.

Options: A. leave as built; B. add the creation flag; C. B plus the viewer filter. Lean A.
