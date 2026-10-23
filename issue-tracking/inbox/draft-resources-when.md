---
title: Resources: make the resource layers automatically when a world is saved from a run?
type: task
status: needs-decision
parent: PW-155
milestone: v2
subsystem: surface
effort: xs
impact: med
found_by: resources
blocked_by: []
relates: [PW-155]
refs: [planet/resources.py, planet/timeline.py, docs/proposals/resources.md]
---

## Description
Stage 1 of PW-155 (planet/resources.py) adds the res_* layers with a separate command,
`planet resources <world>` (in place, like `planet humanuse`). It costs 1.5 s at L6 and 6 s at L7 (the
history pass reads 600 Myr of keyframes) and adds ~25 one-byte layers (~5-12 MB of JSON at L7).

Options:
- **A.** Keep it a separate command (now). Worlds stay lean; the viewer shows the layers only where run.
- **B.** Make them in every world save from a run (slice, Zoom button, finish), after the human-use layers;
  `--no-resources` to skip. Every world has them; +6 s and +10% file size at L7.
- **C.** Compute lazily in the server when the viewer asks (cached next to the world).

Lean: **B** once the owner has looked at the maps (docs/review/resources/), since they are a v2 headline
feature and the cost is small.
