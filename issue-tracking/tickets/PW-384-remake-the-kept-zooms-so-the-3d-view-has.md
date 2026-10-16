---
id: PW-384
title: Remake the kept zooms so the 3D view has their rivers (receiver layer)
type: task
status: done
parent: null
subsystem: zoom
effort: xs
impact: med
found_by: small-fixes-batch
blocked_by: []
relates: [PW-373]
refs: [planet/zoom.py, viewer/zoom3d_mesh.js, "zoom:226c95", "zoom:e33c3d", "zoom:02734d"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-373 made zooms store their D8 receivers (`receiver` layer) and the zoom 3D view now draws its rivers,
river splits, falls' reaches, flow shimmer and fly-along courses only from that layer (no guessing fallback,
per the no-backward-compatibility rule). The 19 zooms in `zooms/` were made before it, so in 3D they show
no rivers and no river flights until they are made again (same world, centre, size, res, seed: same id).
Re-run them (e.g. `planet zoom <world> --lat --lon --size-km --res-km` from each zoom.json, or delete and
re-make via highlights `--zoom`), ~10-60 s each.
- [ ] every kept zoom has `layers/receiver.bin`

## Updates
- 2026-10-16: Status in-progress -> done. Done: all 19 kept zooms rebuilt in place (ids are spec hashes), each with layers/receiver.bin; 3D rivers checked on 226c95 and 02734d.
- 2026-10-16: Status todo -> in-progress. Agent remaking kept zooms in the main checkout.
- 2026-10-16: Created from inbox draft draft-remake-zooms-for-receiver-layer.md (found by small-fixes-batch).
