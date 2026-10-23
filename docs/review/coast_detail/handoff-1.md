# Coast-detail lane: handoff 1 (2026-10-23)

Branch `worktree-agent-a3f04a5319db36c00`, on top of main 11b37f0. Proposal: `docs/proposals/coast_detail.md`.

## Built
- `planet/coastform.py` (stage 1): world layers coast_type (11 classes, legend `coast`), barrier, cliff,
  seabirds, seals, nav_hazard; summary + `.txt` section; `planet coast <world>` (add-on, in place).
  `coastal.environment` now also returns `rocky_land` and `hard` (additive keys, no output change).
- Viewer (index.html): layers coasts / barrier islands / cliffs / seabirds / seals / sea hazards, legends, hover.
- `planet/zoom_coast.py` (stage 2, part): zoom layers coast_type (shore band), barrier_island (island,
  lagoon, inlet), nav_hazard; colonies in zoom.json `coast.features`; `planet coast zoom:<id> [--terrain]`
  (terrain opt-in: islands raised, water -> land). zoom.html: layers Coasts, Barrier islands, hover rows.
- `tools/coast_check.py` (Earth anchor: 26/32), `tests/test_coastform.py`.

## Scratch store
`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/coast`
(PLANET_DATA): worlds 577526, 28442c, aa6d61, 1144ce with coast layers; zooms 30cb73, a5de65, 4dcc95, 478ca0
(copies) and the new ccf03a (28442c, -28, -127, 500 km at 1 km: barrier coast) with coast layers. The shared
store was not written. Viewer for it: `PLANET_DATA=<scratch> uv run python -m planet serve --port 8795 --no-open`.

## Screenshots (this folder)
- `earth_coasts_atlantic.png`: Earth, US Atlantic and Gulf: barrier islands Outer Banks to Texas, marsh and
  delta on the Gulf, coral and mangrove in Florida and Cuba, cliffs and rocky shore in Atlantic Canada.
- `world_28442c_coasts.png`: the Earth-like seed's barrier coast at -28, -127.
- `world_1144ce_seabirds.png`: the L7 world's seabird colony likelihood.
- `zoom_ccf03a_coasts.png`, `zoom_ccf03a_barrier.png`: the zoom's shore classes and its barrier islands
  (936 km2), lagoons (2561 km2) and 44 inlets ~12.5 km apart.

## Next
1. Decisions (drafts): fold coastform into world.finish (lean yes); barrier terrain inside `planet zoom`
   before rivers/satellite (lean yes, needs a zoom golden update).
2. Spits by drift, cliffs as terrain, drowned reefs from the time zoom's sea-level curve
   (draft-coast-zoom-forms-remaining).
3. The shore band follows estuary channels the zoom marks as sea (noise, harmless).
