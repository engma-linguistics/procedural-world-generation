---
id: PW-1209
title: "Binary world layers: an L8 world's 448 MB JSON is 15% below Chrome's string limit, and L9 cannot be opened at all"
type: task
status: done
parent: PW-1198
milestone: v5
subsystem: store
effort: m
impact: high
found_by: lane91-viewer-l8
blocked_by: []
relates: [PW-490, PW-1198]
refs: [planet/world.py, planet/server.py, planet/names.py, viewer/globe/load.js, viewer/globe/select.js, docs/review/viewer-l8/diagnosis.md]
created: 2026-10-31
updated: 2026-11-08
---

## Description
**In plain words.** A finished world is saved as one big JSON text. At L8 that text is about 450 MB, and the
browser cannot read a text longer than about 537 MB. An L8 world fits with roughly 15% to spare, so adding a
few more layers would make it fail to open. An L9 world (about 1.8 GB) could not be opened at all. Reading
the text is also now most of the time it takes to open an L8 world: about 3 of its 4.5-5.5 seconds.

Measured (lane 91, headless Chrome 155, docs/review/viewer-l8/diagnosis.md):
- Chrome's longest string is 536,870,888 characters. `Response.json()` on a longer body fails with
  "Unexpected end of JSON input", which is misleading.
- Synthetic L8 world (2a7385 upsampled, 184 layers): 448 MB of JSON, 60.6 MB gzipped. Fetch and parse take
  2.3-3 s in a clean page and up to 4 s on a loaded machine. JS heap after load: 1.25 GB. Real L7 worlds
  are 112-113 MB, so a real L8 world should be ~450 MB.

Try: write the layers the way runs already do, one typed binary file per layer (or one file with an
offset table), with dtype, scale and offset in the world's JSON header (runs: `run.json` "layers",
`load.js decodeFrame`). Keep a small JSON head (meta, summary, legend, grid). The viewer then gets typed
arrays without parsing text. That roughly halves the heap (Int16/Uint8 instead of 8-byte doubles) and cuts
opening to well under a second, and it removes the size wall before PW-490's L9. Readers to update:
`planet/world.py load`, `server.py` (`_cell_worlds`, which scans the layer lines), `names.py
world_landmasses` (scans for the summary line), the viewer's `setWorld`, and any tools that read
`worlds/*.json` directly (grep). No backward compatibility: old worlds are re-made or deleted.
- [ ] an L8 world opens in < 1.5 s on the owner's machine; heap after load < 0.8 GB
- [ ] an L9-sized world (synthetic is fine) opens

## Updates
- 2026-11-08: Status todo -> done. Lane 229 merged (64035024): worlds as a JSON header + worlds/layers/<id>/<name>.bin (procgen-planet/3); all 50 stored worlds converted 11-08 (about half the bytes); converter fixed for null cells (506694).
- 2026-11-03: Milestones 11-03: later -> v5: v5 must-have: binary world layers, so an L9 refined world opens in the viewer at all
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-10-31: Created from inbox draft draft-binary-world-layers.md (found by lane91-viewer-l8).
