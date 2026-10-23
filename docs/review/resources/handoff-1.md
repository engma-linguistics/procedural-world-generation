# Resources lane: handoff 1 (2026-10-23)

Branch `worktree-agent-addded300a2c6fa99`, commit 8ac7344 (on main 8fe3788). Stage 1 of PW-155 is done; stage 2 is not started.

## Built
- `planet/resources.py`: resource likelihoods per world cell from deposit models, plus a history pass that traces the keyframes back along plate rotations (600 Myr; 1.5 s at L6, 6 s at L7) and rebuilds a 10-layer column. The design and rules are in `docs/proposals/resources.md`.
- `planet resources <world> [--no-history]` adds the layers in place. The layers are `res_<key>`, `resource`, `stone`, `coal_rank` and `res_depth`, with the `resources` legend in `store.legends()`. `world.summarize` gives `summary.resources`, and the `.txt` gets a `## Resources` section.
- Viewer (`viewer/index.html`): three new layers, resources, resource (with a `resSel` picker and `?res=`) and building stone. Each has a legend, and the hover shows rows for them (`resRows`).
- Checks: `tools/resources_check.py` (shares, PNG maps, the Earth fallback on GLiM rock) and `tests/test_resources.py`. A full `pytest` run passed: 580 tests. `tests/test_store.py` now expects the `resources` legend key.

## Next
1. Stage 2, zoom siting (`draft-resources-zoom-siting`; design in proposal section 6): a new `zoom_resources.py`, markers in zoom.html, and export features.
2. Owner decisions in the inbox: `draft-resources-when` (lean: B, automatic at world save), `-fantasy` (lean: A) and `-clocks` (lean: A).
3. Tuning that is still open. Bauxite has a wide spread between 0.25 and 0.5 (11-23% of land at >= 0.25). laterite_ni is about 0, because nothing marks ophiolites (`draft-resources-run-record`). Coal maps are speckled because of keyframe quantisation and flicker.

## Notes
- No world in the shared store holds resource layers. 119973 was written to once by mistake and then restored, using the main checkout's code to strip the layers.
- The test worlds were copies in the scratchpad store (`PLANET_DATA=...`), which was served on port 8793. That server has been stopped and the copies deleted.
